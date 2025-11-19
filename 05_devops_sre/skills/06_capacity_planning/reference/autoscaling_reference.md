# Autoscaling Reference Guide

## Overview

Comprehensive reference for Kubernetes autoscaling mechanisms and cloud-native capacity management.

## Autoscaling Mechanisms Comparison

| Feature | HPA | VPA | Cluster Autoscaler | Karpenter |
|---------|-----|-----|-------------------|-----------|
| **Scope** | Pod replicas | Pod resources | Nodes | Nodes |
| **Scaling Direction** | Horizontal | Vertical | Horizontal | Horizontal |
| **Maturity** | GA (v1) | Beta | GA | Emerging |
| **Cloud Dependency** | No | No | Yes | AWS (primary) |
| **Reaction Time** | 15-30 seconds | Minutes | 30-60 seconds | 10-30 seconds |
| **Disruption** | None | Pod restart | None | Minimal |
| **Custom Metrics** | Yes | Limited | N/A | N/A |
| **Cost Optimization** | Indirect | Yes | Yes | Advanced |
| **Multi-Cloud** | Yes | Yes | Yes | Limited |

## Horizontal Pod Autoscaler (HPA)

### Overview
Automatically scales the number of pod replicas based on observed metrics (CPU, memory, custom metrics).

### API Versions
- **v1**: CPU-based scaling only
- **v2beta2**: Multiple metrics, custom metrics
- **v2**: GA version with full features (Kubernetes 1.23+)

### Scaling Algorithm
```
desiredReplicas = ceil[currentReplicas * (currentMetricValue / targetMetricValue)]
```

### Configuration Options

#### Basic CPU-Based HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 5
        periodSeconds: 60
      selectPolicy: Min
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 10
        periodSeconds: 30
      selectPolicy: Max
```

#### Multi-Metric HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: multi-metric-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 5
  maxReplicas: 100
  metrics:
  # CPU utilization
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Memory utilization
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # Custom metric: requests per second
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  # External metric: SQS queue depth
  - type: External
    external:
      metric:
        name: sqs_queue_depth
        selector:
          matchLabels:
            queue: "orders-queue"
      target:
        type: AverageValue
        averageValue: "30"
```

### HPA Best Practices

#### 1. Metric Selection
- **CPU**: Good for compute-bound workloads
- **Memory**: Use with caution (memory doesn't decrease without restarts)
- **Custom Metrics**: Better for application-specific scaling (RPS, queue depth)
- **Multiple Metrics**: HPA uses the highest desired replica count

#### 2. Scaling Behavior
```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
    policies:
    - type: Percent
      value: 50                       # Scale down max 50% at a time
      periodSeconds: 60
  scaleUp:
    stabilizationWindowSeconds: 0     # Scale up immediately
    policies:
    - type: Percent
      value: 100                      # Double pods if needed
      periodSeconds: 30
```

#### 3. Min/Max Replicas
- **minReplicas**: Set based on minimum SLA requirements
- **maxReplicas**: Consider cluster capacity and cost limits
- **Safety Buffer**: Set max to 2-3x expected peak load

#### 4. Target Utilization
- **CPU**: 60-80% for most workloads
- **Memory**: 70-85% (leave headroom)
- **Custom Metrics**: Based on application testing

### Netflix HPA Strategy
1. **Multiple HPAs**: Separate HPAs for different services
2. **Custom Metrics**: Heavy use of application-level metrics
3. **Aggressive Scale-Up**: Fast response to traffic spikes
4. **Conservative Scale-Down**: Gradual reduction to prevent flapping
5. **Circuit Breakers**: Integrate with Hystrix for intelligent scaling

### Amazon HPA Patterns
1. **Queue-Based Scaling**: Scale workers based on SQS queue depth
2. **Predictive Scaling**: Pre-scale before known traffic patterns
3. **Cost Optimization**: Balance performance with EC2 instance costs
4. **Multi-Region**: Coordinate scaling across regions
5. **Auto-Discovery**: Automatically create HPAs for new services

## Vertical Pod Autoscaler (VPA)

### Overview
Automatically adjusts CPU and memory requests/limits for pods based on historical usage.

### Modes
1. **Auto**: Automatically apply recommendations (restarts pods)
2. **Initial**: Apply recommendations only at pod creation
3. **Off**: Only provide recommendations
4. **Recreate**: Delete and recreate pods with new resources

### Configuration

#### Basic VPA
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-app-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 4
        memory: 8Gi
      controlledResources:
      - cpu
      - memory
      mode: Auto
```

#### VPA with Custom Recommendations
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: custom-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  updatePolicy:
    updateMode: "Recreate"
    minReplicas: 2  # Ensure minimum availability
  resourcePolicy:
    containerPolicies:
    - containerName: "api-container"
      minAllowed:
        cpu: 500m
        memory: 512Mi
      maxAllowed:
        cpu: 8
        memory: 16Gi
      controlledResources:
      - cpu
      - memory
      # Scaling factors
      mode: Auto
    - containerName: "sidecar"
      mode: "Off"  # Don't scale sidecar
```

### VPA Best Practices

#### 1. Avoid VPA + HPA Conflicts
```yaml
# Bad: Both scaling CPU
HPA: cpu target 70%
VPA: Auto mode, cpu scaling

# Good: Different resources
HPA: cpu target 70%
VPA: Initial mode (or memory only)

# Good: Use VPA recommendations manually
VPA: updateMode: "Off"
```

#### 2. Use Initial Mode for Stateless Apps
```yaml
updatePolicy:
  updateMode: "Initial"  # Only set resources on pod creation
```

#### 3. Set Reasonable Limits
```yaml
resourcePolicy:
  containerPolicies:
  - containerName: "*"
    minAllowed:
      cpu: 100m        # Prevent over-reduction
      memory: 128Mi
    maxAllowed:
      cpu: 4           # Prevent runaway growth
      memory: 8Gi
```

#### 4. Monitor Recommendations
```bash
kubectl describe vpa web-app-vpa

# Look for:
# - Lower Bound: Minimum safe resources
# - Target: Recommended resources
# - Upper Bound: Maximum resources needed
# - Uncapped Target: Without maxAllowed constraints
```

### VPA Components
1. **Recommender**: Analyzes metrics, provides recommendations
2. **Updater**: Evicts pods that need resource updates
3. **Admission Controller**: Sets resource requests on new pods

## Cluster Autoscaler

### Overview
Automatically adjusts the number of nodes in a cluster based on pod resource requests.

### How It Works
1. **Scale Up**: When pods can't be scheduled due to insufficient resources
2. **Scale Down**: When nodes are underutilized (<50% requested resources)
3. **Considerations**: Node groups, zones, resource requests

### Configuration

#### AWS EKS Cluster Autoscaler
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.28.0
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
        - --scale-down-utilization-threshold=0.5
        env:
        - name: AWS_REGION
          value: us-east-1
        resources:
          limits:
            cpu: 100m
            memory: 600Mi
          requests:
            cpu: 100m
            memory: 600Mi
```

#### GKE Cluster Autoscaler
```yaml
gcloud container clusters create my-cluster \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --zone=us-central1-a
```

### Cluster Autoscaler Parameters

#### Scale Up
- `--max-nodes-total`: Maximum total nodes across all groups
- `--max-cores-total`: Maximum total CPU cores
- `--max-memory-total`: Maximum total memory
- `--expander`: Strategy for selecting node group (least-waste, most-pods, priority, random)

#### Scale Down
- `--scale-down-delay-after-add`: Wait time after scale-up before considering scale-down (default: 10m)
- `--scale-down-unneeded-time`: How long a node must be unneeded before scale-down (default: 10m)
- `--scale-down-utilization-threshold`: Node utilization below which scale-down is considered (default: 0.5)
- `--skip-nodes-with-local-storage`: Don't scale down nodes with local storage
- `--skip-nodes-with-system-pods`: Don't scale down nodes with kube-system pods

### Best Practices

#### 1. Set Pod Resource Requests
```yaml
# Required for CA to work properly
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1
    memory: 1Gi
```

#### 2. Use Pod Disruption Budgets
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web-app
```

#### 3. Configure Node Groups
```yaml
# Multiple node groups for different workloads
node-groups:
  - name: general
    min: 3
    max: 10
  - name: compute-optimized
    min: 0
    max: 20
  - name: memory-optimized
    min: 0
    max: 15
```

#### 4. Prevent Scale-Down
```yaml
# Annotation to prevent node scale-down
apiVersion: v1
kind: Node
metadata:
  annotations:
    cluster-autoscaler.kubernetes.io/scale-down-disabled: "true"
```

## Karpenter (Next-Generation Node Autoscaling)

### Overview
Open-source, high-performance Kubernetes cluster autoscaler built for AWS. Faster and more flexible than Cluster Autoscaler.

### Key Advantages
1. **Speed**: Provisions nodes in seconds vs. minutes
2. **Flexibility**: Right-sized instances for workloads
3. **Cost**: Automatically selects spot instances
4. **Simplicity**: No node group management
5. **Consolidation**: Actively optimizes node utilization

### Architecture
```
Pods (unscheduled) → Karpenter Controller → AWS EC2 API → Nodes
                          ↓
                    Provisioner CRDs
```

### Configuration

#### Basic Provisioner
```yaml
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: default
spec:
  # Requirements for nodes
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]
    - key: kubernetes.io/arch
      operator: In
      values: ["amd64"]
    - key: karpenter.k8s.aws/instance-category
      operator: In
      values: ["c", "m", "r"]
    - key: karpenter.k8s.aws/instance-generation
      operator: Gt
      values: ["4"]

  # Limits
  limits:
    resources:
      cpu: 1000
      memory: 1000Gi

  # Consolidation
  consolidation:
    enabled: true

  # TTL
  ttlSecondsAfterEmpty: 30
  ttlSecondsUntilExpired: 2592000  # 30 days

  # Provider-specific config
  providerRef:
    name: default
```

#### AWS Node Template
```yaml
apiVersion: karpenter.k8s.aws/v1alpha1
kind: AWSNodeTemplate
metadata:
  name: default
spec:
  subnetSelector:
    karpenter.sh/discovery: my-cluster
  securityGroupSelector:
    karpenter.sh/discovery: my-cluster
  instanceProfile: KarpenterNodeInstanceProfile-my-cluster

  # AMI selection
  amiFamily: AL2

  # User data
  userData: |
    #!/bin/bash
    /etc/eks/bootstrap.sh my-cluster

  # Block device mappings
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 100Gi
        volumeType: gp3
        encrypted: true
        deleteOnTermination: true

  # Tags
  tags:
    Environment: production
    ManagedBy: Karpenter

  # Metadata options
  metadataOptions:
    httpEndpoint: enabled
    httpProtocolIPv6: disabled
    httpPutResponseHopLimit: 2
    httpTokens: required
```

#### Multi-Provisioner Strategy
```yaml
---
# General workloads - spot preferred
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: general-spot
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot"]
    - key: karpenter.k8s.aws/instance-category
      operator: In
      values: ["c", "m", "r"]
  taints:
    - key: workload
      value: general
      effect: NoSchedule
  providerRef:
    name: spot-template
---
# Critical workloads - on-demand only
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: critical-ondemand
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["on-demand"]
    - key: node.kubernetes.io/instance-type
      operator: In
      values: ["m5.2xlarge", "m5.4xlarge"]
  labels:
    workload: critical
  providerRef:
    name: ondemand-template
---
# GPU workloads
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: gpu
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["on-demand"]
    - key: karpenter.k8s.aws/instance-category
      operator: In
      values: ["p", "g"]
  taints:
    - key: nvidia.com/gpu
      value: "true"
      effect: NoSchedule
  limits:
    resources:
      nvidia.com/gpu: 10
  providerRef:
    name: gpu-template
```

### Karpenter Best Practices

#### 1. Consolidation
```yaml
spec:
  consolidation:
    enabled: true  # Continuously optimize node utilization
  ttlSecondsAfterEmpty: 30  # Quickly remove empty nodes
```

#### 2. Spot Instance Handling
```yaml
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot"]
  # Karpenter automatically handles spot interruptions
  # Diversify across instance types for better availability
  - key: karpenter.k8s.aws/instance-category
    operator: In
    values: ["c", "m", "r", "t"]  # Multiple families
```

#### 3. Pod Affinity for Binpacking
```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: web-app
spec:
  affinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: web-app
          topologyKey: kubernetes.io/hostname
```

#### 4. Resource Limits per Provisioner
```yaml
spec:
  limits:
    resources:
      cpu: 500        # Max 500 CPUs
      memory: 500Gi   # Max 500Gi memory
      nvidia.com/gpu: 4  # Max 4 GPUs
```

### Netflix Karpenter Usage
1. **Rapid Scaling**: Handle sudden traffic spikes (new show releases)
2. **Cost Optimization**: Heavy use of spot instances
3. **Workload Isolation**: Separate provisioners for encoding, streaming, ML
4. **Multi-Region**: Karpenter in all regions for global scale
5. **Custom Metrics**: Integration with internal capacity planning

### Amazon Karpenter Patterns
1. **Batch Processing**: Spin up large compute clusters on-demand
2. **Machine Learning**: GPU instance right-sizing
3. **Microservices**: Fast scaling for containerized services
4. **Cost Savings**: 60-70% reduction using spot instances
5. **Developer Productivity**: No manual node group management

## Autoscaling Decision Matrix

### Use HPA when:
- Scaling stateless applications
- CPU/memory-based scaling is sufficient
- Need sub-minute scaling response
- Running microservices
- Custom application metrics available

### Use VPA when:
- Applications have unpredictable resource needs
- Want to right-size containers automatically
- Running batch jobs or ML workloads
- Need historical resource optimization
- Cost optimization is priority

### Use Cluster Autoscaler when:
- Using managed node groups (EKS, GKE, AKS)
- Need simple node scaling
- Existing cloud infrastructure
- Straightforward scaling requirements
- Multi-cloud support needed

### Use Karpenter when:
- On AWS EKS
- Need fastest scaling response
- Want cost optimization with spot instances
- Diverse workload requirements
- Advanced consolidation needed

## Combined Autoscaling Strategy

### Recommended Architecture
```
┌─────────────────────────────────────┐
│  Application Layer                  │
│  - HPA for pod scaling (seconds)    │
│  - Custom metrics from apps         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Resource Optimization Layer        │
│  - VPA for right-sizing (hours)     │
│  - Recommendations mode             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Infrastructure Layer               │
│  - Karpenter/CA for nodes (minutes) │
│  - Spot + On-Demand mix             │
└─────────────────────────────────────┘
```

### Example Combined Setup
```yaml
---
# HPA: Scale pods based on RPS
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
---
# VPA: Optimize resource requests (recommendations only)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Off"  # Don't conflict with HPA
---
# Karpenter: Scale nodes
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: web-app-provisioner
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]
  consolidation:
    enabled: true
```

## Monitoring and Observability

### Key Metrics to Track
```yaml
# HPA metrics
- kube_hpa_status_current_replicas
- kube_hpa_status_desired_replicas
- kube_hpa_spec_max_replicas
- kube_hpa_spec_min_replicas

# VPA metrics
- vpa_status_recommendation
- vpa_spec_resourcepolicy_container_policies_maxallowed
- vpa_spec_resourcepolicy_container_policies_minallowed

# Cluster Autoscaler metrics
- cluster_autoscaler_scaled_up_nodes_total
- cluster_autoscaler_scaled_down_nodes_total
- cluster_autoscaler_unschedulable_pods_count

# Karpenter metrics
- karpenter_pods_state{state="pending"}
- karpenter_nodes_created
- karpenter_nodes_terminated
- karpenter_consolidation_actions
```

### Grafana Dashboard Example
```json
{
  "dashboard": {
    "title": "Autoscaling Overview",
    "panels": [
      {
        "title": "HPA Replica Count",
        "targets": [
          {
            "expr": "kube_hpa_status_current_replicas{namespace=\"production\"}"
          }
        ]
      },
      {
        "title": "Node Count Over Time",
        "targets": [
          {
            "expr": "count(kube_node_info)"
          }
        ]
      },
      {
        "title": "Pod Pending Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(scheduler_pending_pods_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## References

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [VPA GitHub Repository](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [Karpenter Documentation](https://karpenter.sh/)
- [AWS Best Practices for Karpenter](https://aws.github.io/aws-eks-best-practices/karpenter/)
- [Netflix Technology Blog - Autoscaling](https://netflixtechblog.com/)
