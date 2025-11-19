# 5G Core Deployment Guide

## Pre-Deployment Planning

### Requirements Assessment

**Hardware Requirements**
- Compute: High-performance servers (64+ vCPU, 256GB+ RAM)
- Storage: NVMe SSD for databases (1TB+ minimum)
- Network: 10+ Gbps connectivity
- HA: Redundant systems across sites

**Software Requirements**
- Kubernetes 1.24+ or OpenStack
- Docker/Containerd runtime
- Helm 3.x for package management
- PostgreSQL/MySQL for data stores

**Network Requirements**
- S1-U interface: Connection to RAN
- S1-MME interface: Control plane connectivity
- N2/N3 interfaces: For 5GC (if SA)
- External network: Internet/corporate network

### Capacity Planning

```
Expected Users: 100,000
Peak Traffic: 500 Gbps
Expected Throughput: 100 Mbps per user (average)
Storage: 500GB for logging (daily)
Compute: 100 vCPU, 400GB RAM
```

## Step 1: Infrastructure Setup

### Kubernetes Cluster Deployment

**Prerequisite: Kubernetes 1.24+**

```bash
# Install Kubernetes
kubeadm init --pod-network-cidr=10.244.0.0/16

# Install CNI (Calico recommended for 5G)
kubectl apply -f https://docs.projectcalico.org/manifests/tigera-operator.yaml

# Verify cluster
kubectl get nodes
kubectl get pods --all-namespaces
```

### Create Namespace for 5G

```bash
kubectl create namespace 5g-core
kubectl label namespace 5g-core 5g-enabled=true
```

### Install Helm Charts

```bash
helm repo add 5g-charts https://5g-charts-repo.example.com
helm repo update
```

## Step 2: Database Setup

### PostgreSQL Deployment

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: 5g-core
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: 5g-core
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 500Gi
```

**Initialize Database**

```sql
CREATE DATABASE 5gcore;
CREATE USER 5g_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE 5gcore TO 5g_user;

-- Create subscriber table
CREATE TABLE subscribers (
  imsi VARCHAR(15) PRIMARY KEY,
  status VARCHAR(20),
  apn VARCHAR(100),
  ambr_ul INTEGER,
  ambr_dl INTEGER
);
```

## Step 3: Deploy Network Functions

### Deploy AMF (Access and Mobility Management Function)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amf
  namespace: 5g-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: amf
  template:
    metadata:
      labels:
        app: amf
    spec:
      containers:
      - name: amf
        image: 5gcore/amf:latest
        ports:
        - name: n1n2
          containerPort: 38412
          protocol: SCTP
        - name: namf
          containerPort: 8000
        env:
        - name: AMF_INSTANCE
          value: "1"
        - name: SCTP_BIND_ADDR
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            cpu: 4
            memory: 16Gi
          limits:
            cpu: 8
            memory: 32Gi
```

### Deploy SMF (Session Management Function)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smf
  namespace: 5g-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smf
  template:
    metadata:
      labels:
        app: smf
    spec:
      containers:
      - name: smf
        image: 5gcore/smf:latest
        ports:
        - name: nsmf
          containerPort: 8080
        env:
        - name: NSMF_API_HOST
          value: "0.0.0.0"
        - name: NSMF_API_PORT
          value: "8080"
        - name: DB_HOST
          value: postgres
        - name: DB_PORT
          value: "5432"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            cpu: 4
            memory: 16Gi
          limits:
            cpu: 8
            memory: 32Gi
```

### Deploy UPF (User Plane Function)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: upf
  namespace: 5g-core
spec:
  selector:
    matchLabels:
      app: upf
  template:
    metadata:
      labels:
        app: upf
    spec:
      nodeSelector:
        upf-enabled: "true"
      hostNetwork: true
      containers:
      - name: upf
        image: 5gcore/upf:latest
        ports:
        - name: pfcp
          containerPort: 8805
          protocol: UDP
        - name: n3
          containerPort: 2152
          protocol: UDP
        securityContext:
          privileged: true
          capabilities:
            add:
            - NET_ADMIN
        env:
        - name: PFCP_BIND_ADDR
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: N3_BIND_ADDR
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        resources:
          requests:
            cpu: 8
            memory: 32Gi
          limits:
            cpu: 16
            memory: 64Gi
```

## Step 4: Service Configuration

### Create Services for Network Functions

```yaml
apiVersion: v1
kind: Service
metadata:
  name: amf
  namespace: 5g-core
spec:
  clusterIP: None
  selector:
    app: amf
  ports:
  - name: n1n2
    port: 38412
    protocol: SCTP
  - name: namf
    port: 8000
    protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: smf
  namespace: 5g-core
spec:
  clusterIP: None
  selector:
    app: smf
  ports:
  - name: nsmf
    port: 8080
    protocol: TCP
```

## Step 5: Network Slicing Setup

### Define Network Slice

```yaml
apiVersion: 5g.example.com/v1
kind: NetworkSlice
metadata:
  name: urllc-slice
  namespace: 5g-core
spec:
  name: URLLC Service
  sst: 2
  sd: "010203"
  maxLatency: 5ms
  reliability: 99.9999
  maxBitRate: 1000
  amf:
    replicas: 2
  smf:
    replicas: 2
  upf:
    replicas: 2
```

## Step 6: Monitoring & Observability

### Deploy Prometheus for Metrics

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: 5g-core
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'amf'
      static_configs:
      - targets: ['amf:8000']
    - job_name: 'smf'
      static_configs:
      - targets: ['smf:8080']
    - job_name: 'upf'
      static_configs:
      - targets: ['upf:9000']
```

### Deploy Grafana for Visualization

```bash
helm install grafana grafana/grafana \
  --namespace 5g-core \
  --set adminPassword=grafana
```

## Step 7: Testing & Validation

### Connectivity Test

```bash
# Test AMF accessibility
kubectl run -it --rm debug --image=nicolaka/netshoot \
  -- curl -X GET http://amf:8000/health

# Test database connectivity
kubectl exec -it postgres-0 -- \
  psql -U 5g_user -d 5gcore -c "SELECT COUNT(*) FROM subscribers;"
```

### Load Testing

```bash
# Generate simulated UE attachments
kubectl run -it --rm load-test --image=5gcore/load-test \
  -- python load_test.py --ues=1000 --duration=600
```

### Performance Validation

**Expected KPIs:**
- Attachment time: < 1 second
- Session setup: < 100ms
- Message latency: < 10ms
- Throughput: > 10 Gbps aggregate

## Step 8: Production Hardening

### Security Configuration

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: 5g-core-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - configMap
  - emptyDir
  - projected
  - secret
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: MustRunAsNonRoot
```

### Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: 5g-core-quota
  namespace: 5g-core
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "400Gi"
    limits.cpu: "200"
    limits.memory: "800Gi"
    pods: "500"
```

## Troubleshooting

### Common Issues

**Issue: AMF not accepting connections**
```bash
# Check AMF logs
kubectl logs -f deployment/amf -n 5g-core

# Verify SCTP support
kubectl exec -it amf-0 -- cat /proc/net/sctp/assocs

# Check network policies
kubectl get networkpolicies -n 5g-core
```

**Issue: Database connectivity failures**
```bash
# Test database
kubectl exec -it postgres-0 -- \
  psql -U 5g_user -c "SELECT 1"

# Check database logs
kubectl logs -f postgres-0 -n 5g-core
```

## Maintenance

### Regular Tasks

1. **Daily:** Monitor metrics and logs
2. **Weekly:** Security policy reviews
3. **Monthly:** Capacity planning reviews
4. **Quarterly:** Disaster recovery testing

### Backup Strategy

```bash
# Backup database daily
kubectl exec postgres-0 -- \
  pg_dump -U 5g_user 5gcore > backup-$(date +%Y%m%d).sql

# Store in S3/Blob
aws s3 cp backup-*.sql s3://5g-backups/
```

---

**Last Updated:** 2025-11-19
