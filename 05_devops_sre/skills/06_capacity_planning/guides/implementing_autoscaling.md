# Implementing Autoscaling in Kubernetes

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Horizontal Pod Autoscaler (HPA)](#horizontal-pod-autoscaler-hpa)
4. [Vertical Pod Autoscaler (VPA)](#vertical-pod-autoscaler-vpa)
5. [Cluster Autoscaler](#cluster-autoscaler)
6. [Karpenter](#karpenter)
7. [Combined Strategy](#combined-strategy)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)

---

## Introduction

This guide provides step-by-step instructions for implementing autoscaling in Kubernetes, covering pod-level and cluster-level scaling.

### Autoscaling Layers

```
┌─────────────────────────────────────┐
│  HPA - Scale Pods (Horizontal)      │  ← Seconds to Minutes
├─────────────────────────────────────┤
│  VPA - Size Pods (Vertical)         │  ← Hours to Days
├─────────────────────────────────────┤
│  CA/Karpenter - Scale Nodes         │  ← Minutes
└─────────────────────────────────────┘
```

---

## Prerequisites

### 1. Metrics Server

HPA requires Metrics Server to collect resource metrics.

```bash
# Check if Metrics Server is installed
kubectl get deployment metrics-server -n kube-system

# Install Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify installation
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml

# Test metrics collection
kubectl top nodes
kubectl top pods -A
```

**For local/development clusters (minikube, kind):**
```bash
# Metrics Server with insecure TLS
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: metrics-server
  namespace: kube-system
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      serviceAccountName: metrics-server
      containers:
      - name: metrics-server
        image: k8s.gcr.io/metrics-server/metrics-server:v0.6.4
        args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-insecure-tls
        - --kubelet-preferred-address-types=InternalIP
EOF
```

### 2. Resource Requests/Limits

All pods must have resource requests for HPA to work.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web-app
        image: web-app:1.0
        resources:
          requests:
            cpu: 500m        # Required for CPU-based HPA
            memory: 512Mi    # Required for memory-based HPA
          limits:
            cpu: 1000m
            memory: 1Gi
```

### 3. Custom Metrics (Optional)

For advanced HPA using custom metrics, install Prometheus Adapter.

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus (if not already installed)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Install Prometheus Adapter
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --namespace monitoring \
  --set prometheus.url=http://prometheus-kube-prometheus-prometheus.monitoring.svc \
  --set prometheus.port=9090
```

---

## Horizontal Pod Autoscaler (HPA)

### Step 1: Deploy Application

```yaml
# web-app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
  namespace: production
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

```bash
kubectl apply -f web-app-deployment.yaml
```

### Step 2: Create Basic CPU-Based HPA

```yaml
# hpa-cpu.yaml
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
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

```bash
kubectl apply -f hpa-cpu.yaml

# Verify HPA
kubectl get hpa -n production
kubectl describe hpa web-app-hpa -n production
```

### Step 3: Test HPA

```bash
# Generate load
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh

# Inside the pod, run:
while true; do wget -q -O- http://web-app.production.svc.cluster.local; done

# Watch HPA scaling (in another terminal)
kubectl get hpa web-app-hpa -n production --watch

# Watch pod count
kubectl get pods -n production --watch
```

### Step 4: Multi-Metric HPA

```yaml
# hpa-multi-metric.yaml
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
  minReplicas: 5
  maxReplicas: 50
  metrics:
  # CPU metric
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Memory metric
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

  # Custom metric: Requests per second (requires Prometheus)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"

  # Scaling behavior
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

```bash
kubectl apply -f hpa-multi-metric.yaml
```

### Step 5: HPA with External Metrics (SQS Example)

```yaml
# hpa-sqs.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worker
  minReplicas: 2
  maxReplicas: 100
  metrics:
  - type: External
    external:
      metric:
        name: sqs_queue_depth
        selector:
          matchLabels:
            queue: "orders-queue"
      target:
        type: AverageValue
        averageValue: "30"  # Scale up when queue depth > 30 per pod
```

**Note:** Requires KEDA or custom metrics adapter for SQS integration.

---

## Vertical Pod Autoscaler (VPA)

### Step 1: Install VPA

```bash
# Clone VPA repository
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# Install VPA
./hack/vpa-up.sh

# Verify installation
kubectl get pods -n kube-system | grep vpa
```

**Expected output:**
```
vpa-admission-controller-xxx
vpa-recommender-xxx
vpa-updater-xxx
```

### Step 2: Create VPA (Recommendations Mode)

```yaml
# vpa-recommendations.yaml
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
    updateMode: "Off"  # Only provide recommendations
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
```

```bash
kubectl apply -f vpa-recommendations.yaml

# View recommendations
kubectl describe vpa web-app-vpa -n production
```

**Sample output:**
```yaml
Recommendation:
  Container Recommendations:
    Container Name:  web-app
    Lower Bound:
      Cpu:     150m
      Memory:  200Mi
    Target:
      Cpu:     300m
      Memory:  512Mi
    Upper Bound:
      Cpu:     600m
      Memory:  1Gi
```

### Step 3: VPA in Auto Mode

```yaml
# vpa-auto.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: batch-job-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: batch-job
  updatePolicy:
    updateMode: "Auto"  # Automatically apply recommendations
  resourcePolicy:
    containerPolicies:
    - containerName: "batch-container"
      minAllowed:
        cpu: 500m
        memory: 512Mi
      maxAllowed:
        cpu: 8
        memory: 16Gi
      controlledResources:
      - cpu
      - memory
      mode: Auto
```

**Warning:** Auto mode will restart pods to apply new resources.

### Step 4: VPA + HPA (Avoiding Conflicts)

```yaml
# Use VPA for memory, HPA for CPU
---
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
    updateMode: "Initial"  # Only set on pod creation
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      controlledResources:
      - memory  # VPA only controls memory
      mode: Auto
---
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
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu  # HPA only scales on CPU
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Cluster Autoscaler

### AWS EKS Implementation

#### Step 1: Create IAM Policy

```bash
# Create IAM policy for Cluster Autoscaler
cat > cluster-autoscaler-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:DescribeLaunchConfigurations",
        "autoscaling:DescribeScalingActivities",
        "autoscaling:DescribeTags",
        "ec2:DescribeInstanceTypes",
        "ec2:DescribeLaunchTemplateVersions"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup",
        "ec2:DescribeImages",
        "ec2:GetInstanceTypesFromInstanceRequirements",
        "eks:DescribeNodegroup"
      ],
      "Resource": ["*"]
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name AmazonEKSClusterAutoscalerPolicy \
  --policy-document file://cluster-autoscaler-policy.json
```

#### Step 2: Create IAM Role

```bash
# Create service account
eksctl create iamserviceaccount \
  --cluster=my-cluster \
  --namespace=kube-system \
  --name=cluster-autoscaler \
  --attach-policy-arn=arn:aws:iam::ACCOUNT_ID:policy/AmazonEKSClusterAutoscalerPolicy \
  --override-existing-serviceaccounts \
  --approve
```

#### Step 3: Deploy Cluster Autoscaler

```yaml
# cluster-autoscaler.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
  labels:
    app: cluster-autoscaler
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
      priorityClassName: system-cluster-critical
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.28.2
        name: cluster-autoscaler
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
        volumeMounts:
        - name: ssl-certs
          mountPath: /etc/ssl/certs/ca-certificates.crt
          readOnly: true
      volumes:
      - name: ssl-certs
        hostPath:
          path: /etc/ssl/certs/ca-bundle.crt
```

```bash
kubectl apply -f cluster-autoscaler.yaml

# Verify
kubectl logs -f deployment/cluster-autoscaler -n kube-system
```

#### Step 4: Tag Auto Scaling Groups

```bash
# Tag ASG for auto-discovery
aws autoscaling create-or-update-tags \
  --tags ResourceId=eks-node-group-xxxxx,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/enabled,Value=true,PropagateAtLaunch=false \
         ResourceId=eks-node-group-xxxxx,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/my-cluster,Value=owned,PropagateAtLaunch=false
```

### GKE Implementation

```bash
# Enable Cluster Autoscaler on GKE
gcloud container clusters update my-cluster \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --zone=us-central1-a

# Per node pool
gcloud container node-pools update default-pool \
  --cluster=my-cluster \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --zone=us-central1-a
```

---

## Karpenter

### Step 1: Prerequisites

```bash
# Variables
export CLUSTER_NAME=my-cluster
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

### Step 2: Create IAM Roles

```bash
# Create Karpenter node role
cat > karpenter-node-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name KarpenterNodeRole-${CLUSTER_NAME} \
  --assume-role-policy-document file://karpenter-node-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name KarpenterNodeRole-${CLUSTER_NAME} \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy

aws iam attach-role-policy \
  --role-name KarpenterNodeRole-${CLUSTER_NAME} \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy

aws iam attach-role-policy \
  --role-name KarpenterNodeRole-${CLUSTER_NAME} \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

aws iam attach-role-policy \
  --role-name KarpenterNodeRole-${CLUSTER_NAME} \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name KarpenterNodeInstanceProfile-${CLUSTER_NAME}

aws iam add-role-to-instance-profile \
  --instance-profile-name KarpenterNodeInstanceProfile-${CLUSTER_NAME} \
  --role-name KarpenterNodeRole-${CLUSTER_NAME}
```

### Step 3: Install Karpenter

```bash
# Add Helm repo
helm repo add karpenter https://charts.karpenter.sh
helm repo update

# Install Karpenter
helm install karpenter karpenter/karpenter \
  --namespace karpenter \
  --create-namespace \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=arn:aws:iam::${AWS_ACCOUNT_ID}:role/KarpenterControllerRole-${CLUSTER_NAME} \
  --set settings.aws.clusterName=${CLUSTER_NAME} \
  --set settings.aws.defaultInstanceProfile=KarpenterNodeInstanceProfile-${CLUSTER_NAME} \
  --set settings.aws.interruptionQueueName=${CLUSTER_NAME} \
  --wait
```

### Step 4: Create Provisioner

```yaml
# karpenter-provisioner.yaml
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

  # Provider config
  providerRef:
    name: default

---
apiVersion: karpenter.k8s.aws/v1alpha1
kind: AWSNodeTemplate
metadata:
  name: default
spec:
  subnetSelector:
    karpenter.sh/discovery: ${CLUSTER_NAME}
  securityGroupSelector:
    karpenter.sh/discovery: ${CLUSTER_NAME}
  instanceProfile: KarpenterNodeInstanceProfile-${CLUSTER_NAME}

  # AMI
  amiFamily: AL2

  # User data
  userData: |
    #!/bin/bash
    /etc/eks/bootstrap.sh ${CLUSTER_NAME}

  # Block devices
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

  # Metadata
  metadataOptions:
    httpEndpoint: enabled
    httpProtocolIPv6: disabled
    httpPutResponseHopLimit: 2
    httpTokens: required
```

```bash
envsubst < karpenter-provisioner.yaml | kubectl apply -f -

# Verify
kubectl get provisioner
kubectl logs -f -n karpenter -l app.kubernetes.io/name=karpenter
```

### Step 5: Test Karpenter

```bash
# Create deployment that triggers scaling
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inflate
spec:
  replicas: 0
  selector:
    matchLabels:
      app: inflate
  template:
    metadata:
      labels:
        app: inflate
    spec:
      terminationGracePeriodSeconds: 0
      containers:
      - name: inflate
        image: public.ecr.aws/eks-distro/kubernetes/pause:3.7
        resources:
          requests:
            cpu: 1
            memory: 1Gi
EOF

# Scale up
kubectl scale deployment inflate --replicas=10

# Watch Karpenter provision nodes
kubectl logs -f -n karpenter -l app.kubernetes.io/name=karpenter

# Watch nodes
kubectl get nodes --watch

# Scale down
kubectl scale deployment inflate --replicas=0

# Karpenter will decommission nodes after ttlSecondsAfterEmpty
```

---

## Combined Strategy

### Netflix-Inspired Architecture

```yaml
---
# Layer 1: HPA for rapid pod scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: streaming-api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: streaming-api
  minReplicas: 20
  maxReplicas: 500
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60

---
# Layer 2: VPA for resource optimization (recommendations only)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: streaming-api-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: streaming-api
  updatePolicy:
    updateMode: "Off"

---
# Layer 3: Karpenter for node scaling
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: streaming-workload
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot"]  # Netflix uses spot heavily
    - key: karpenter.k8s.aws/instance-category
      operator: In
      values: ["c", "m"]  # Compute and memory optimized
    - key: node.kubernetes.io/instance-type
      operator: In
      values: ["m5.2xlarge", "m5.4xlarge", "c5.2xlarge", "c5.4xlarge"]
  labels:
    workload: streaming
  consolidation:
    enabled: true
  ttlSecondsAfterEmpty: 60
```

---

## Monitoring and Troubleshooting

### Monitoring HPA

```bash
# View HPA status
kubectl get hpa -A

# Describe HPA
kubectl describe hpa web-app-hpa -n production

# Watch HPA in real-time
kubectl get hpa web-app-hpa -n production --watch

# Check HPA events
kubectl get events -n production --field-selector involvedObject.name=web-app-hpa

# View metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/production/pods
```

### Monitoring VPA

```bash
# View VPA recommendations
kubectl describe vpa web-app-vpa -n production

# Get all VPAs
kubectl get vpa -A

# Check VPA components
kubectl get pods -n kube-system | grep vpa

# View VPA events
kubectl get events -n production --field-selector involvedObject.kind=VerticalPodAutoscaler
```

### Monitoring Cluster Autoscaler

```bash
# View logs
kubectl logs -f deployment/cluster-autoscaler -n kube-system

# Check status
kubectl get configmap cluster-autoscaler-status -n kube-system -o yaml

# View events
kubectl get events -n kube-system --field-selector involvedObject.name=cluster-autoscaler
```

### Monitoring Karpenter

```bash
# View logs
kubectl logs -f -n karpenter -l app.kubernetes.io/name=karpenter

# View provisioners
kubectl get provisioner

# View nodes provisioned by Karpenter
kubectl get nodes -l karpenter.sh/provisioner-name=default

# Metrics
kubectl port-forward -n karpenter svc/karpenter 8080:8080
# Visit http://localhost:8080/metrics
```

### Prometheus Queries

```promql
# HPA metrics
kube_hpa_status_current_replicas{namespace="production"}
kube_hpa_status_desired_replicas{namespace="production"}

# Pod resource usage
container_memory_usage_bytes{namespace="production",pod=~"web-app-.*"}
rate(container_cpu_usage_seconds_total{namespace="production",pod=~"web-app-.*"}[5m])

# Node metrics
kube_node_status_allocatable{resource="cpu"}
kube_node_status_allocatable{resource="memory"}

# Karpenter metrics
karpenter_pods_state{state="pending"}
karpenter_nodes_created
karpenter_nodes_terminated
```

### Common Issues and Solutions

#### Issue 1: HPA Not Scaling

```bash
# Check metrics availability
kubectl top pods -n production

# If metrics not available:
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml

# Check resource requests
kubectl get deployment web-app -n production -o yaml | grep -A 5 resources

# Check HPA status
kubectl describe hpa web-app-hpa -n production
```

#### Issue 2: VPA Evicting Too Many Pods

```yaml
# Use safer update mode
spec:
  updatePolicy:
    updateMode: "Initial"  # Only on pod creation

# Or use PodDisruptionBudget
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

#### Issue 3: Cluster Autoscaler Not Scaling

```bash
# Check logs
kubectl logs -f deployment/cluster-autoscaler -n kube-system

# Verify ASG tags
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names <asg-name> \
  --query 'AutoScalingGroups[0].Tags'

# Check pending pods
kubectl get pods -A | grep Pending
```

#### Issue 4: Karpenter Not Provisioning

```bash
# Check Karpenter logs
kubectl logs -f -n karpenter -l app.kubernetes.io/name=karpenter

# Verify provisioner
kubectl get provisioner -o yaml

# Check IAM permissions
# Ensure instance profile and roles are correct

# Verify subnet and security group tags
aws ec2 describe-subnets --filters "Name=tag:karpenter.sh/discovery,Values=${CLUSTER_NAME}"
```

---

## References

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [VPA GitHub](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Cluster Autoscaler FAQ](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md)
- [Karpenter Documentation](https://karpenter.sh/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Netflix Tech Blog](https://netflixtechblog.com/)
