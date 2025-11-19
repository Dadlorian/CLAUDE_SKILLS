# Litmus Chaos Experiments

This directory contains example ChaosEngine configurations for Litmus Chaos experiments.

## Prerequisites

1. **Kubernetes Cluster** (1.17+)
2. **Litmus Chaos Operator** installed
3. **Litmus Service Account** created with proper permissions
4. **Target Application** deployed and labeled

## Installation

```bash
# Install Litmus via Helm
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm repo update

# Create namespace
kubectl create namespace litmus

# Install Litmus
helm install chaos litmuschaos/litmus --namespace litmus

# Verify installation
kubectl get pods -n litmus
```

## Service Account Setup

```bash
# Create service account with permissions
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: litmus-admin
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: litmus-admin
  namespace: default
rules:
  - apiGroups: [""]
    resources: ["pods","events","services"]
    verbs: ["create","delete","get","list","patch","update","deletecollection"]
  - apiGroups: ["apps"]
    resources: ["deployments","statefulsets","replicasets","daemonsets"]
    verbs: ["get","list"]
  - apiGroups: ["batch"]
    resources: ["jobs"]
    verbs: ["create","delete","get","list","deletecollection"]
  - apiGroups: ["litmuschaos.io"]
    resources: ["chaosengines","chaosexperiments","chaosresults"]
    verbs: ["create","delete","get","list","patch","update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: litmus-admin
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: litmus-admin
subjects:
  - kind: ServiceAccount
    name: litmus-admin
    namespace: default
EOF
```

## Available Experiments

### 1. pod-delete.yaml
**Purpose**: Test pod failure and auto-healing

**What it does**:
- Randomly deletes pods
- Tests Kubernetes pod rescheduling
- Validates service availability during pod failures

**Usage**:
```bash
kubectl apply -f pod-delete.yaml
```

**Monitor**:
```bash
# Watch chaos engine status
kubectl get chaosengine pod-delete-chaos -w

# Watch pod deletions
kubectl get pods -w -l app=nginx

# Check experiment results
kubectl get chaosresult -n default
```

### 2. pod-network-latency.yaml
**Purpose**: Test timeout handling and circuit breakers

**What it does**:
- Adds network latency (2 seconds by default)
- Tests application timeout configurations
- Validates retry logic and circuit breakers

**Customization**:
```yaml
# Adjust latency (in milliseconds)
- name: NETWORK_LATENCY
  value: '2000'  # Change to desired latency

# Target specific services
- name: DESTINATION_HOSTS
  value: 'postgres.default.svc.cluster.local'

# Adjust jitter
- name: JITTER
  value: '100'  # Random variation
```

**Usage**:
```bash
kubectl apply -f pod-network-latency.yaml
```

### 3. pod-cpu-memory-stress.yaml
**Purpose**: Test resource limits and auto-scaling

**What it does**:
- Stresses CPU and memory
- Tests HPA (Horizontal Pod Autoscaler)
- Validates resource limits and requests

**Customization**:
```yaml
# CPU stress
- name: CPU_CORES
  value: '2'  # Number of cores
- name: CPU_LOAD
  value: '100'  # Percentage

# Memory stress
- name: MEMORY_CONSUMPTION
  value: '500'  # MB
```

**Usage**:
```bash
kubectl apply -f pod-cpu-memory-stress.yaml

# Watch HPA scaling
kubectl get hpa -w
```

## Experiment Lifecycle

### 1. Apply Experiment
```bash
kubectl apply -f <experiment-file>.yaml
```

### 2. Monitor Experiment
```bash
# Check ChaosEngine status
kubectl get chaosengine -n default

# View experiment progress
kubectl describe chaosengine <engine-name> -n default

# Watch pods
kubectl get pods -n default -w
```

### 3. Check Results
```bash
# Get ChaosResult
kubectl get chaosresult -n default

# View detailed results
kubectl describe chaosresult <engine-name>-<experiment-name> -n default
```

### 4. Stop Experiment
```bash
# Stop chaos engine
kubectl patch chaosengine <engine-name> -n default \
  --type merge \
  -p '{"spec":{"engineState":"stop"}}'

# Or delete it
kubectl delete chaosengine <engine-name> -n default
```

## Probes

Litmus supports multiple probe types for validating system behavior:

### HTTP Probe
```yaml
probe:
  - name: check-health
    type: httpProbe
    mode: Continuous
    httpProbe/inputs:
      url: http://service.namespace.svc.cluster.local/health
      method:
        get:
          criteria: ==
          responseCode: "200"
```

### Prometheus Probe
```yaml
probe:
  - name: check-error-rate
    type: promProbe
    mode: Continuous
    promProbe/inputs:
      endpoint: http://prometheus:9090
      query: "rate(http_errors[1m])"
      comparator:
        type: float
        criteria: "<"
        value: "0.05"
```

### Kubernetes Probe
```yaml
probe:
  - name: check-pod-count
    type: k8sProbe
    mode: Edge
    k8sProbe/inputs:
      group: ""
      version: v1
      resource: pods
      namespace: default
      labelSelector: app=nginx
      operation: present
```

### Command Probe
```yaml
probe:
  - name: check-disk-space
    type: cmdProbe
    mode: Edge
    cmdProbe/inputs:
      command: df -h | grep /data | awk '{print $5}' | sed 's/%//'
      comparator:
        type: int
        criteria: "<"
        value: "80"
```

## Probe Modes

- **SOT (Start of Test)**: Runs once before chaos
- **EOT (End of Test)**: Runs once after chaos
- **Edge**: Runs before and after chaos
- **Continuous**: Runs throughout chaos duration
- **OnChaos**: Runs while chaos is active

## Common Patterns

### Pattern 1: Gradual Rollout
```yaml
# Week 1
- name: PODS_AFFECTED_PERC
  value: '10'
- name: TOTAL_CHAOS_DURATION
  value: '30'

# Week 2
- name: PODS_AFFECTED_PERC
  value: '25'
- name: TOTAL_CHAOS_DURATION
  value: '60'

# Week 3
- name: PODS_AFFECTED_PERC
  value: '50'
- name: TOTAL_CHAOS_DURATION
  value: '120'
```

### Pattern 2: Multi-Experiment Sequence
```yaml
experiments:
  - name: pod-delete
    # ... config ...
  - name: pod-network-latency
    # ... config ...
  - name: pod-cpu-hog
    # ... config ...
```

### Pattern 3: Production Safety
```yaml
spec:
  # Target non-production first
  appinfo:
    appns: staging
    applabel: 'app=api,env=staging'

  # Small blast radius
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: PODS_AFFECTED_PERC
              value: '5'  # Only 5%
            - name: TOTAL_CHAOS_DURATION
              value: '30'  # Short duration

        # Strong abort conditions
        probe:
          - name: error-rate-check
            type: promProbe
            mode: Continuous
            # Automatically abort if error rate > 1%
```

## Troubleshooting

### Experiment Not Starting
```bash
# Check operator logs
kubectl logs -n litmus -l app=chaos-operator

# Check service account permissions
kubectl auth can-i create pods --as=system:serviceaccount:default:litmus-admin

# Verify ChaosExperiment exists
kubectl get chaosexperiment -n default
```

### Experiment Failed
```bash
# Check ChaosResult for failure reason
kubectl describe chaosresult <name> -n default

# Check experiment logs
kubectl logs -n default -l chaosUID=<chaos-engine-uid>

# Review probe failures
kubectl get chaosresult <name> -n default -o json | jq '.status.probeStatus'
```

### Cleanup Issues
```bash
# Force delete stuck ChaosEngine
kubectl delete chaosengine <name> -n default --force --grace-period=0

# Clean up experiment jobs
kubectl delete jobs -n default -l chaosUID=<uid>

# Reset namespace
kubectl delete chaosengine,chaosresult -n default --all
```

## Best Practices

1. **Start Small**: Begin with short duration and low percentage
2. **Use Probes**: Always configure health check probes
3. **Monitor**: Watch dashboards during experiments
4. **Document**: Record hypothesis and results
5. **Iterate**: Gradually increase complexity
6. **Automate**: Schedule regular chaos experiments
7. **Clean Up**: Delete completed experiments

## Resources

- **Litmus Docs**: https://docs.litmuschaos.io
- **ChaosHub**: https://hub.litmuschaos.io
- **Litmus GitHub**: https://github.com/litmuschaos/litmus
- **Slack Community**: litmuschaos.slack.com

## Next Steps

1. Try the examples in a development cluster
2. Customize for your applications
3. Add Prometheus/Grafana for monitoring
4. Create custom experiments
5. Integrate with CI/CD pipelines
6. Graduate to production chaos
