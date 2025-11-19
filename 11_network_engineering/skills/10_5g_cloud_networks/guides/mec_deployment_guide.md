# MEC (Multi-Access Edge Computing) Deployment Guide

## MEC Architecture Planning

### Location Selection

**RAN Edge Deployment**
- Co-located with gNodeB
- Latency: 1-5ms
- Capacity: Limited by site constraints
- Use case: V2X, AR/VR

**Network Edge Deployment**
- Located at aggregation points
- Latency: 5-20ms
- Capacity: Medium (500+ Gbps)
- Use case: Caching, analytics

**Cloud Edge Deployment**
- Regional data centers
- Latency: 20-100ms
- Capacity: High (10+ Tbps)
- Use case: Heavy processing

### Capacity Planning

```
Location: RAN Edge Site 1
Expected Traffic: 50 Gbps
Compute: 16 vCPU, 64GB RAM
Storage: 500GB NVMe
Network: 10Gbps uplink
Applications: V2X, AR, Real-time gaming
```

## Step 1: Infrastructure Setup

### Deploy MEC Platform

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mec-platform
  labels:
    mec-enabled: "true"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mec-platform
  namespace: mec-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mec-platform
  template:
    metadata:
      labels:
        app: mec-platform
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - mec-platform
            topologyKey: kubernetes.io/hostname
      containers:
      - name: platform
        image: etsi/mec-platform:latest
        ports:
        - containerPort: 8080
          name: api
        - containerPort: 8443
          name: api-secure
        env:
        - name: MEC_LOCATION
          value: "RAN_EDGE_1"
        - name: COMPUTE_CAPACITY
          value: "16000"  # millicpu
        - name: MEMORY_CAPACITY
          value: "67108864"  # bytes
        resources:
          requests:
            cpu: 4
            memory: 16Gi
          limits:
            cpu: 8
            memory: 32Gi
        volumeMounts:
        - name: config
          mountPath: /etc/mec
      volumes:
      - name: config
        configMap:
          name: mec-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mec-config
  namespace: mec-platform
data:
  platform.conf: |
    [platform]
    location_id=RAN_EDGE_1
    location_type=RAN_EDGE
    management_api=http://localhost:8080
    notification_api=http://localhost:9000
```

### Service Registration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mec-platform-api
  namespace: mec-platform
spec:
  type: LoadBalancer
  selector:
    app: mec-platform
  ports:
  - name: api
    port: 8080
    targetPort: 8080
  - name: api-secure
    port: 8443
    targetPort: 8443
```

## Step 2: Deploy MEC Services

### Application Enablement Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mec-app-enablement
  namespace: mec-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app-enablement
  template:
    metadata:
      labels:
        app: app-enablement
    spec:
      containers:
      - name: enablement
        image: etsi/mec-app-enablement:latest
        ports:
        - containerPort: 8081
        env:
        - name: SERVICE_REGISTRY_URL
          value: "http://service-registry:8000"
        - name: LOCATION_INFO_URL
          value: "http://location-service:8000"
        resources:
          requests:
            cpu: 2
            memory: 8Gi
```

### Location Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: location-service
  namespace: mec-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: location-service
  template:
    metadata:
      labels:
        app: location-service
    spec:
      containers:
      - name: location
        image: etsi/mec-location-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: RAN_INTEGRATION
          value: "true"
        - name: LOCATION_DB
          value: "location-db:5432"
        resources:
          requests:
            cpu: 2
            memory: 8Gi
```

### Radio Information Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: radio-info-service
  namespace: mec-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: radio-info-service
  template:
    metadata:
      labels:
        app: radio-info-service
    spec:
      containers:
      - name: radio-info
        image: etsi/mec-radio-info-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: RAN_INTERFACE
          value: "eth0"
        - name: METRICS_INTERVAL
          value: "1000"  # milliseconds
        resources:
          requests:
            cpu: 2
            memory: 8Gi
```

## Step 3: MEC-UPF Integration

### Co-Deploy UPF with MEC

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mec-upf
  namespace: mec-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mec-upf
  template:
    metadata:
      labels:
        app: mec-upf
    spec:
      nodeSelector:
        mec-upf-enabled: "true"
      hostNetwork: true
      containers:
      - name: upf
        image: 5gcore/mec-upf:latest
        ports:
        - containerPort: 8805
          protocol: UDP
          name: pfcp
        - containerPort: 2152
          protocol: UDP
          name: n3
        env:
        - name: PFCP_BIND_ADDR
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: N3_BIND_ADDR
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: MEC_PLATFORM_URL
          value: "http://mec-platform-api:8080"
        - name: LOCAL_BREAKOUT_ENABLED
          value: "true"
        - name: SERVICE_AREA_ROUTING
          value: "true"
        securityContext:
          privileged: true
          capabilities:
            add:
            - NET_ADMIN
        resources:
          requests:
            cpu: 8
            memory: 32Gi
          limits:
            cpu: 16
            memory: 64Gi
```

## Step 4: Application Deployment

### Deploy MEC Application (V2X)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: v2x-application
  namespace: mec-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: v2x-app
      mec-app: "true"
  template:
    metadata:
      labels:
        app: v2x-app
        mec-app: "true"
      annotations:
        mec.platform.api: "http://mec-platform-api:8080"
    spec:
      serviceAccountName: mec-app
      containers:
      - name: v2x
        image: mec-apps/v2x:latest
        ports:
        - containerPort: 5000
          name: api
        - containerPort: 5001
          name: ws
        env:
        - name: MEC_LOCATION
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: SERVICE_REGISTRY_URL
          value: "http://mec-platform-api:8080/services"
        - name: LOCATION_SERVICE_URL
          value: "http://location-service:8000"
        - name: RADIO_INFO_URL
          value: "http://radio-info-service:8000"
        - name: TARGET_LATENCY_MS
          value: "5"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            cpu: 2
            memory: 4Gi
          limits:
            cpu: 4
            memory: 8Gi
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mec-app
  namespace: mec-platform
```

### MEC Application Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: v2x-application
  namespace: mec-platform
  annotations:
    mec.api/type: "external"
    mec.api/version: "1.0"
spec:
  type: LoadBalancer
  selector:
    app: v2x-app
  ports:
  - name: api
    port: 5000
    targetPort: 5000
  - name: websocket
    port: 5001
    targetPort: 5001
```

## Step 5: Service Discovery & Registration

### Application Registration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mec-app-manifest
  namespace: mec-platform
data:
  manifest.yaml: |
    appName: V2X Safety Service
    appProvider: SafetyNetworks
    appServiceProduced:
      - serName: v2x-safety
        version: "1.0"
        state: ACTIVE
        serializer: JSON
    appServiceConsumed:
      - serName: location
        version: "1.0"
      - serName: radio-info
        version: "1.0"
    appFeatures:
      maxLatency: 5
      reliability: 0.99999
      maxBandwidth: 100
```

## Step 6: Monitoring & Observability

### MEC Metrics Collection

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mec-prometheus-config
  namespace: mec-platform
data:
  prometheus.yml: |
    global:
      scrape_interval: 5s
    scrape_configs:
    - job_name: 'mec-platform'
      static_configs:
      - targets: ['mec-platform-api:8080']
    - job_name: 'mec-apps'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - mec-platform
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_mec_app]
        action: keep
        regex: "true"
```

### MEC Application Monitoring

```bash
# Monitor application latency
kubectl exec -it prometheus-0 -n mec-platform -- \
  promtool query instant 'mec_app_latency_p99{app="v2x"}'

# Monitor MEC resource usage
kubectl top pods -n mec-platform

# Monitor UPF traffic
kubectl exec -it mec-upf-0 -c upf -- \
  pfctl -s stats | grep -i packet
```

## Step 7: Testing & Validation

### Latency Testing

```bash
# Deploy latency test
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: mec-latency-test
  namespace: mec-platform
spec:
  template:
    spec:
      containers:
      - name: test
        image: mec-tools/latency-test:latest
        env:
        - name: TARGET_SERVICE
          value: "v2x-application:5000"
        - name: NUM_REQUESTS
          value: "1000"
        - name: TARGET_P99_LATENCY
          value: "5"
      restartPolicy: Never
EOF
```

### Cache Hit Rate Testing

```bash
# Monitor cache effectiveness
kubectl logs -f deployment/mec-platform -n mec-platform | grep -i cache

# Analyze cache metrics
kubectl exec -it prometheus-0 -n mec-platform -- \
  promtool query instant 'mec_cache_hit_ratio{service="v2x"}'
```

## Step 8: Production Hardening

### Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: mec-quota
  namespace: mec-platform
spec:
  hard:
    requests.cpu: "32"
    requests.memory: "128Gi"
    limits.cpu: "64"
    limits.memory: "256Gi"
    pods: "100"
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mec-isolation
  namespace: mec-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          mec-app: "true"
    - namespaceSelector:
        matchLabels:
          name: 5g-core
  egress:
  - to:
    - podSelector: {}
    - namespaceSelector:
        matchLabels:
          name: 5g-core
```

## Troubleshooting

### MEC Platform Issues

```bash
# Check MEC platform status
kubectl describe deployment mec-platform -n mec-platform

# View MEC platform logs
kubectl logs -f deployment/mec-platform -n mec-platform

# Test MEC API connectivity
kubectl exec -it mec-platform-0 -n mec-platform -- \
  curl -X GET http://localhost:8080/mec/platform/v1/
```

### Application Latency Issues

```bash
# Check application logs
kubectl logs -f deployment/v2x-application -n mec-platform

# Analyze network latency
kubectl exec -it v2x-application-0 -n mec-platform -- \
  ping -c 10 mec-upf

# Check resource usage
kubectl top pod v2x-application-0 -n mec-platform --containers
```

---

**Last Updated:** 2025-11-19
