# Google Kubernetes Engine (GKE) Reference

## Overview

Google Kubernetes Engine (GKE) is a managed Kubernetes service that provides a production-ready environment for deploying containerized applications with Google infrastructure.

## Cluster Modes

### Standard Mode
Full cluster configuration control with node management.

**Characteristics**:
- Full control over node configuration
- Manual/automatic node pool management
- Configure machine types, disk, networking
- Manage cluster upgrades and node pools
- Fine-grained autoscaling control

**Use Cases**:
- Need specific node configurations
- Custom security requirements
- Specialized workloads (GPU, local SSD)
- Existing Kubernetes expertise

**Create Standard Cluster**:
```bash
gcloud container clusters create my-cluster \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --num-nodes=3 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade
```

### Autopilot Mode
Fully managed Kubernetes with pod-level billing.

**Characteristics**:
- Google manages nodes, networking, security
- Pay per pod resource requests
- Automatic scaling, repair, upgrade
- Pre-configured security best practices
- No node management required

**Use Cases**:
- Reduced operational overhead
- Focus on workloads, not infrastructure
- Cost optimization per pod
- Simplified Kubernetes management

**Create Autopilot Cluster**:
```bash
gcloud container clusters create-auto my-autopilot-cluster \
    --region=us-central1
```

### Comparison

| Feature | Standard | Autopilot |
|---------|----------|-----------|
| **Node Management** | Manual | Fully managed |
| **Billing** | Per node | Per pod |
| **Scaling** | Node pools | Automatic |
| **Machine Types** | Any | Optimized selection |
| **Node Access** | SSH allowed | No SSH |
| **Workload Types** | All | Kubernetes-compliant |
| **Cost Predictability** | Node-based | Pod-based |
| **Operational Overhead** | Higher | Lower |
| **Customization** | Full | Limited |

## Node Pools

### Node Pool Configuration

**Create Node Pool**:
```bash
gcloud container node-pools create high-memory-pool \
    --cluster=my-cluster \
    --machine-type=n2-highmem-4 \
    --num-nodes=2 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5 \
    --zone=us-central1-a \
    --node-labels=workload=memory-intensive \
    --node-taints=special=true:NoSchedule
```

**Node Pool Features**:
- Multiple pools per cluster
- Different machine types per pool
- Separate autoscaling configuration
- Node labels and taints
- Preemptible/spot nodes
- Local SSD, GPUs

### Node Auto-Provisioning
Automatically create node pools for pending pods.

```bash
gcloud container clusters update my-cluster \
    --enable-autoprovisioning \
    --min-cpu=1 \
    --max-cpu=100 \
    --min-memory=1 \
    --max-memory=1000 \
    --autoprovisioning-scopes=https://www.googleapis.com/auth/cloud-platform
```

### Node Labels and Taints

**Node Labels** (for pod affinity):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  nodeSelector:
    workload: memory-intensive
  containers:
  - name: app
    image: gcr.io/my-project/my-app:latest
```

**Node Taints** (prevent scheduling):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  tolerations:
  - key: "special"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
  containers:
  - name: app
    image: gcr.io/my-project/my-app:latest
```

## Networking

### Network Modes

**VPC-Native (Alias IP)**:
```bash
gcloud container clusters create my-cluster \
    --enable-ip-alias \
    --network=my-vpc \
    --subnetwork=my-subnet \
    --cluster-secondary-range-name=pods \
    --services-secondary-range-name=services
```

**Routes-Based (Legacy)**:
- Not recommended for new clusters
- Uses routes for pod networking

### Network Policy
Control pod-to-pod communication.

**Enable Network Policy**:
```bash
gcloud container clusters update my-cluster \
    --enable-network-policy
```

**Network Policy Example**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Service Types

**ClusterIP** (Internal only):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
```

**LoadBalancer** (External L4):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
```

**Ingress** (External L7):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

### Private Clusters
Nodes have private IP addresses only.

```bash
gcloud container clusters create private-cluster \
    --enable-private-nodes \
    --enable-private-endpoint \
    --master-ipv4-cidr=172.16.0.0/28 \
    --enable-ip-alias \
    --network=my-vpc \
    --subnetwork=my-subnet
```

## Security

### Workload Identity
Secure way for pods to access Google Cloud services.

**Enable Workload Identity**:
```bash
# Create cluster with Workload Identity
gcloud container clusters create my-cluster \
    --workload-pool=PROJECT_ID.svc.id.goog

# Create Kubernetes Service Account
kubectl create serviceaccount my-ksa

# Create Google Service Account
gcloud iam service-accounts create my-gsa

# Bind accounts
gcloud iam service-accounts add-iam-policy-binding \
    my-gsa@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/my-ksa]"

# Annotate Kubernetes SA
kubectl annotate serviceaccount my-ksa \
    iam.gke.io/gcp-service-account=my-gsa@PROJECT_ID.iam.gserviceaccount.com
```

**Use in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-ksa
  containers:
  - name: app
    image: gcr.io/my-project/my-app:latest
```

### Binary Authorization
Deploy-time security control.

**Enable Binary Authorization**:
```bash
gcloud container clusters update my-cluster \
    --enable-binauthz
```

**Policy Example** (allow only signed images):
```yaml
admissionWhitelistPatterns:
- namePattern: gcr.io/PROJECT_ID/*
defaultAdmissionRule:
  requireAttestationsBy:
  - projects/PROJECT_ID/attestors/my-attestor
  evaluationMode: REQUIRE_ATTESTATION
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
```

### GKE Sandbox
Run untrusted workloads with gVisor.

```bash
gcloud container node-pools create sandbox-pool \
    --cluster=my-cluster \
    --sandbox type=gvisor
```

**Use gVisor**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: untrusted-pod
spec:
  runtimeClassName: gvisor
  containers:
  - name: app
    image: untrusted/app:latest
```

### Pod Security Standards
Enforce security policies.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

## Autoscaling

### Cluster Autoscaler
Automatically adjust node pool size.

```bash
gcloud container clusters update my-cluster \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10
```

### Horizontal Pod Autoscaler (HPA)
Scale pods based on metrics.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**CLI**:
```bash
kubectl autoscale deployment my-deployment \
    --cpu-percent=70 \
    --min=2 \
    --max=10
```

### Vertical Pod Autoscaler (VPA)
Automatically adjust pod resource requests.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-deployment
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

### Multidimensional Pod Autoscaler (MPA)
Scale on custom metrics (Autopilot).

```yaml
apiVersion: autoscaling.gke.io/v1beta1
kind: MultidimPodAutoscaler
metadata:
  name: my-mpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-deployment
  policies:
  - type: ScaleUp
    periodSeconds: 60
    selectPolicy: Max
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Storage

### Persistent Volumes

**Storage Classes**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
  replication-type: regional-pd
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

**Persistent Volume Claim**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
```

**Use in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: gcr.io/my-project/my-app:latest
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-pvc
```

### Persistent Disk Types
- **pd-standard**: HDD persistent disk
- **pd-balanced**: SSD balanced persistent disk
- **pd-ssd**: SSD persistent disk
- **pd-extreme**: Extreme persistent disk (high IOPS)

### Filestore CSI Driver
NFS persistent volumes.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: filestore-pvc
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: filestore-csi
  resources:
    requests:
      storage: 1Ti
```

## Observability

### Cloud Logging
Automatic logging integration.

**Enable Cloud Logging**:
```bash
gcloud container clusters update my-cluster \
    --enable-cloud-logging \
    --logging=SYSTEM,WORKLOAD
```

**View Logs**:
```bash
# kubectl logs
kubectl logs my-pod

# Cloud Logging
gcloud logging read "resource.type=k8s_container AND resource.labels.cluster_name=my-cluster"
```

### Cloud Monitoring
Metrics and alerting.

**Enable Cloud Monitoring**:
```bash
gcloud container clusters update my-cluster \
    --enable-cloud-monitoring \
    --monitoring=SYSTEM,WORKLOAD
```

**Custom Metrics** (via Prometheus):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      external_labels:
        cluster: my-cluster
    scrape_configs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
```

### Cloud Trace
Distributed tracing for GKE workloads.

**OpenTelemetry Integration**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:
    exporters:
      googlecloud:
        project: PROJECT_ID
    service:
      pipelines:
        traces:
          receivers: [otlp]
          exporters: [googlecloud]
```

## CI/CD Integration

### Cloud Build
```yaml
# cloudbuild.yaml
steps:
# Build container image
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA', '.']

# Push to Container Registry
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA']

# Deploy to GKE
- name: 'gcr.io/cloud-builders/gke-deploy'
  args:
  - run
  - --filename=k8s/
  - --image=gcr.io/$PROJECT_ID/my-app:$SHORT_SHA
  - --location=us-central1-a
  - --cluster=my-cluster
```

### GitOps with Config Sync
```bash
# Enable Config Sync
gcloud beta container clusters update my-cluster \
    --enable-stackdriver-kubernetes

# Configure sync from Git
kubectl apply -f - <<EOF
apiVersion: configmanagement.gke.io/v1
kind: ConfigManagement
metadata:
  name: config-management
spec:
  sourceFormat: unstructured
  git:
    syncRepo: https://github.com/my-org/my-repo
    syncBranch: main
    secretType: none
EOF
```

## Multi-Cluster Management

### GKE Enterprise (Anthos)
Centralized multi-cluster management.

**Fleet Management**:
```bash
# Register cluster to fleet
gcloud container fleet memberships register my-cluster \
    --gke-cluster=us-central1-a/my-cluster \
    --enable-workload-identity

# List fleet members
gcloud container fleet memberships list
```

**Multi-Cluster Ingress**:
```yaml
apiVersion: networking.gke.io/v1
kind: MultiClusterIngress
metadata:
  name: my-multi-cluster-ingress
spec:
  template:
    spec:
      backend:
        serviceName: my-service
        servicePort: 80
```

## Cost Optimization

### Cost Optimization Strategies

1. **Use Autopilot**: Pay per pod, not per node
2. **Right-size Pods**: Use VPA for optimal resource requests
3. **Use Preemptible Nodes**: Up to 80% discount
```bash
gcloud container node-pools create preemptible-pool \
    --cluster=my-cluster \
    --preemptible \
    --machine-type=e2-medium
```

4. **Enable Cluster Autoscaler**: Scale down unused nodes
5. **Use Spot Pods** (Autopilot): Cheaper, interruptible
```yaml
apiVersion: v1
kind: Pod
metadata:
  labels:
    cloud.google.com/gke-spot: "true"
```

6. **Committed Use Discounts**: For predictable workloads
7. **Regional Clusters**: Balance cost vs availability
8. **Bin Packing**: Optimize pod packing with resource requests

### GKE Cost Allocation
```bash
# Enable cost allocation
gcloud container clusters update my-cluster \
    --enable-cost-allocation

# View costs by namespace
gcloud billing accounts get-iam-policy BILLING_ACCOUNT_ID
```

## Best Practices

1. **Use Autopilot** unless specific node control needed
2. **Enable Workload Identity** for secure service access
3. **Implement Network Policies** for pod segmentation
4. **Use Binary Authorization** for image security
5. **Enable Monitoring and Logging** from day one
6. **Configure Resource Requests/Limits** for all pods
7. **Use HPA/VPA** for autoscaling
8. **Implement Health Checks** (liveness, readiness, startup)
9. **Use Namespaces** for logical separation
10. **Regular Upgrades** to latest Kubernetes version
11. **Backup Etcd** or use multi-zonal clusters
12. **Tag Resources** for cost tracking
13. **Use Secrets** for sensitive data
14. **Implement RBAC** for access control
15. **Test DR Procedures** regularly

## Troubleshooting

### Common Issues

**Pods Not Starting**:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get events
```

**Node Issues**:
```bash
kubectl get nodes
kubectl describe node <node-name>
gcloud container operations list
```

**Network Issues**:
```bash
kubectl exec -it <pod-name> -- ping <service-name>
kubectl get svc
kubectl describe ingress <ingress-name>
```

**Resource Exhaustion**:
```bash
kubectl top nodes
kubectl top pods
kubectl describe resourcequotas
```

## Cluster Operations

### Upgrades
```bash
# List available versions
gcloud container get-server-config --zone=us-central1-a

# Upgrade control plane
gcloud container clusters upgrade my-cluster \
    --master \
    --cluster-version=1.27.3-gke.100

# Upgrade nodes
gcloud container clusters upgrade my-cluster \
    --zone=us-central1-a
```

### Backup and Restore
```bash
# Backup using Velero
velero backup create my-backup

# Restore
velero restore create --from-backup my-backup
```

### Cluster Migration
```bash
# Export workloads
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# Apply to new cluster
kubectl apply -f cluster-backup.yaml
```
