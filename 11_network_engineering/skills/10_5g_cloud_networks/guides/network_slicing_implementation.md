# Network Slicing Implementation Guide

## Slicing Architecture Overview

Network slicing enables isolated logical networks within shared infrastructure, each optimized for specific service requirements.

## Step 1: Design Slice Types

### URLLC Slice Design

**Requirements Definition**
```
Service Type: Ultra-Reliable Low-Latency Communications
Max Latency: 1-5ms
Reliability: 99.9999%
Bandwidth: 10-100 Mbps
Peak Load: 1000 users
Resources: Dedicated UPF instances
```

**Resource Allocation**
```yaml
apiVersion: 5g.example.com/v1
kind: NetworkSlice
metadata:
  name: urllc-slice
spec:
  # Identity
  name: "URLLC Service"
  sst: 2  # URLLC Slice Service Type
  sd: "000001"  # Slice Differentiator

  # Performance Requirements
  maxLatency: 5ms
  reliability: 0.999999
  avail abilityTarget: 0.99999

  # Bandwidth
  maxBandwidth: 1000  # Mbps
  guaranteedBandwidth: 500  # Mbps

  # Scaling
  minInstances:
    amf: 2
    smf: 2
    upf: 2
  maxInstances:
    amf: 5
    smf: 5
    upf: 10

  # Redundancy
  redundancy: "active-active"
  geoDistribution: "multi-site"
```

### eMBB Slice Design

**Requirements Definition**
```
Service Type: Enhanced Mobile Broadband
Max Latency: 50-100ms
Reliability: 99.9%
Bandwidth: 100+ Mbps
Peak Load: 100,000 users
Resources: Shared infrastructure
```

**Resource Configuration**
```yaml
apiVersion: 5g.example.com/v1
kind: NetworkSlice
metadata:
  name: embb-slice
spec:
  name: "eMBB Service"
  sst: 1
  sd: "000001"

  maxLatency: 100ms
  reliability: 0.999

  maxBandwidth: 10000
  guaranteedBandwidth: 0  # Best-effort

  minInstances:
    amf: 1
    smf: 1
    upf: 1
  maxInstances:
    amf: 10
    smf: 10
    upf: 50

  redundancy: "active-passive"
  geoDistribution: "regional"
```

## Step 2: Implement Slice Management

### Slice Orchestration Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slice-orchestrator
  namespace: 5g-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: slice-orchestrator
  template:
    metadata:
      labels:
        app: slice-orchestrator
    spec:
      serviceAccountName: slice-orchestrator
      containers:
      - name: orchestrator
        image: 5gcore/slice-orchestrator:latest
        ports:
        - containerPort: 8080
        env:
        - name: KUBERNETES_API
          value: "https://kubernetes.default.svc"
        - name: DB_HOST
          value: "postgres"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            cpu: 2
            memory: 8Gi
```

### Slice Selection Function (NSSF)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nssf
  namespace: 5g-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nssf
  template:
    metadata:
      labels:
        app: nssf
    spec:
      containers:
      - name: nssf
        image: 5gcore/nssf:latest
        ports:
        - containerPort: 8000
        env:
        - name: SLICE_CONFIG
          valueFrom:
            configMapKeyRef:
              name: slice-config
              key: slices.yaml
        resources:
          requests:
            cpu: 2
            memory: 8Gi
```

## Step 3: Configure Slice Resources

### URLLC Slice Deployment

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: urllc-slice-ns
  labels:
    slice-type: urllc
    slice-name: urllc-slice
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amf-urllc
  namespace: urllc-slice-ns
spec:
  replicas: 2
  selector:
    matchLabels:
      app: amf
      slice: urllc
  template:
    metadata:
      labels:
        app: amf
        slice: urllc
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - amf
            topologyKey: kubernetes.io/hostname
      containers:
      - name: amf
        image: 5gcore/amf:latest
        ports:
        - containerPort: 38412
          protocol: SCTP
        resources:
          requests:
            cpu: 4
            memory: 16Gi
          limits:
            cpu: 8
            memory: 32Gi
```

### eMBB Slice Deployment

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: embb-slice-ns
  labels:
    slice-type: embb
    slice-name: embb-slice
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: amf-embb
  namespace: embb-slice-ns
spec:
  serviceName: amf-embb
  replicas: 1
  selector:
    matchLabels:
      app: amf
      slice: embb
  template:
    metadata:
      labels:
        app: amf
        slice: embb
    spec:
      containers:
      - name: amf
        image: 5gcore/amf:latest
        resources:
          requests:
            cpu: 2
            memory: 8Gi
          limits:
            cpu: 4
            memory: 16Gi
```

## Step 4: QoS Configuration

### Slice QoS Policies

```yaml
apiVersion: 5g.example.com/v1
kind: SliceQoS
metadata:
  name: urllc-qos
  namespace: 5g-core
spec:
  sliceRef:
    name: urllc-slice

  # Uplink guarantee
  ulGBR: 500  # Mbps
  ulMBR: 1000  # Mbps

  # Downlink guarantee
  dlGBR: 500  # Mbps
  dlMBR: 1000  # Mbps

  # Delay budget
  delayBudget: 5  # ms

  # Reliability
  packetErrorRate: 0.00001

  # Priority
  priority: 1  # Highest
```

### QoS Flow Configuration

```yaml
apiVersion: 5g.example.com/v1
kind: QoSFlow
metadata:
  name: gaming-flow
  namespace: urllc-slice-ns
spec:
  qfi: 1  # QoS Flow Identifier

  # Guaranteed Bit Rate
  gbrUL: 50  # Mbps
  gbrDL: 100  # Mbps

  # Maximum Bit Rate
  mbrUL: 100  # Mbps
  mbrDL: 200  # Mbps

  # Priority Level
  pl: 15  # 1-15, lower is higher priority

  # Packet Error Rate
  per: 0.00001

  # Average window
  avgWindow: 2000  # ms
```

## Step 5: Network Function Isolation

### Pod Network Policies for Slices

```yaml
# Default deny all ingress for slice
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: urllc-default-deny
  namespace: urllc-slice-ns
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
# Allow inter-slice communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: urllc-allow-internal
  namespace: urllc-slice-ns
spec:
  podSelector:
    matchLabels:
      slice: urllc
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          slice: urllc
    - namespaceSelector:
        matchLabels:
          name: 5g-core
  egress:
  - to:
    - podSelector:
        matchLabels:
          slice: urllc
    - namespaceSelector:
        matchLabels:
          name: 5g-core
```

## Step 6: Monitoring Slice Performance

### Slice Metrics Collection

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: slice-prometheus-config
  namespace: 5g-core
data:
  prometheus.yml: |
    global:
      scrape_interval: 10s
    scrape_configs:
    - job_name: 'urllc-slice'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - urllc-slice-ns
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_slice]
        action: keep
        regex: urllc
```

### Grafana Dashboard Example

```json
{
  "dashboard": {
    "title": "URLLC Slice Dashboard",
    "panels": [
      {
        "title": "Slice Latency (p99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, slice_latency_ms{slice='urllc'})"
          }
        ]
      },
      {
        "title": "Slice Reliability",
        "targets": [
          {
            "expr": "rate(slice_packets_success{slice='urllc'}[1m]) / rate(slice_packets_total{slice='urllc'}[1m])"
          }
        ]
      },
      {
        "title": "UE Count",
        "targets": [
          {
            "expr": "count(ue_registered{slice='urllc'})"
          }
        ]
      }
    ]
  }
}
```

## Step 7: Slice Lifecycle Management

### Create Slice

```bash
# Apply slice definition
kubectl apply -f urllc-slice.yaml

# Verify slice creation
kubectl get networkslices -n 5g-core
kubectl describe networkslice urllc-slice -n 5g-core
```

### Update Slice

```bash
# Update slice resources
kubectl patch networkslice urllc-slice -n 5g-core \
  -p '{"spec":{"maxInstances":{"upf":15}}}'

# Verify update
kubectl get networkslice urllc-slice -n 5g-core -o yaml
```

### Monitor Slice Health

```bash
# Check slice pod status
kubectl get pods -n urllc-slice-ns

# View slice events
kubectl get events -n urllc-slice-ns --sort-by='.lastTimestamp'

# Check slice metrics
kubectl exec -it prometheus-0 -n 5g-core -- \
  promtool query instant 'slice_health{slice="urllc"}'
```

## Step 8: Slice Testing

### Load Test URLLC Slice

```bash
# Deploy load generator
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: urllc-load-test
  namespace: urllc-slice-ns
spec:
  completions: 1
  parallelism: 1
  template:
    spec:
      containers:
      - name: load-test
        image: 5gcore/load-tester:latest
        env:
        - name: TARGET_SLICE
          value: "urllc"
        - name: NUM_UES
          value: "100"
        - name: DURATION_SECONDS
          value: "300"
        - name: TARGET_LATENCY_MS
          value: "5"
        - name: TARGET_RELIABILITY
          value: "0.999999"
        resources:
          requests:
            cpu: 4
            memory: 8Gi
      restartPolicy: Never
EOF
```

### Analyze Test Results

```bash
# Get test logs
kubectl logs -f job/urllc-load-test -n urllc-slice-ns

# Extract metrics
kubectl exec -it prometheus-0 -n 5g-core -- \
  promtool query range 'slice_latency_p99{slice="urllc"}' \
  --start 2025-11-19T12:00:00Z --end 2025-11-19T12:05:00Z
```

## Best Practices

1. **Resource Planning** - Allocate 20% overhead
2. **Testing** - Test slices before production
3. **Monitoring** - Track all KPIs continuously
4. **Scaling** - Auto-scale based on demand
5. **Isolation** - Enforce network policies
6. **Updates** - Rolling updates without downtime

---

**Last Updated:** 2025-11-19
