# Azure Kubernetes Service (AKS) Reference

## AKS Overview

Azure Kubernetes Service (AKS) is a managed Kubernetes container orchestration service that simplifies deployment, management, and operations of Kubernetes clusters.

## Cluster Architecture

### Control Plane (Managed by Azure)
- **API Server**: Kubernetes API endpoint
- **etcd**: Cluster state storage
- **Scheduler**: Pod placement decisions
- **Controller Manager**: Cluster state management
- **Cloud Controller**: Azure-specific integrations

**Cost**: Free (you only pay for worker nodes)

### Node Pools

#### System Node Pool
**Purpose**: Host critical system pods (CoreDNS, metrics-server, tunnelfront)
**Minimum**: 1 node
**Recommended**: 2-3 nodes for production
**VM Size**: Minimum Standard_DS2_v2
**Taints**: Usually `CriticalAddonsOnly=true:NoSchedule`

#### User Node Pools
**Purpose**: Application workloads
**Scaling**: Can scale to zero (except system pools)
**VM Size**: Any supported size
**Node Count**: 0-1000 nodes per pool

```bash
# Add user node pool
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKS \
  --name userpool \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --mode User \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10
```

## Kubernetes Versions

### Version Support Policy
- AKS supports **3 GA minor versions** at any time
- Example: If latest is 1.28, supported are 1.28, 1.27, 1.26
- **Auto-upgrade available**: Patch, stable, rapid, node-image

### Upgrade Strategy

```bash
# Check available versions
az aks get-versions --location eastus --output table

# Upgrade control plane first
az aks upgrade \
  --resource-group myRG \
  --name myAKS \
  --kubernetes-version 1.28.3 \
  --control-plane-only

# Then upgrade node pools
az aks nodepool upgrade \
  --resource-group myRG \
  --cluster-name myAKS \
  --name nodepool1 \
  --kubernetes-version 1.28.3
```

**Best Practice**: Enable auto-upgrade for production clusters

```bash
az aks update \
  --resource-group myRG \
  --name myAKS \
  --auto-upgrade-channel stable
```

## Networking Models

### kubenet (Basic Networking)
**IP Allocation**: Nodes get Azure VNet IPs, pods get private IPs from separate CIDR
**Routing**: User Defined Routes (UDRs) required
**Network Policy**: Not supported
**Maximum Pods per Node**: 110 (default)

**Pros**:
- IP address efficient
- Simpler setup
- Lower cost

**Cons**:
- No network policies
- UDRs add complexity
- Pods not directly addressable from VNet

**Use Case**: Dev/test, non-production, simple scenarios

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --network-plugin kubenet \
  --pod-cidr 10.244.0.0/16
```

### Azure CNI (Advanced Networking)
**IP Allocation**: Each pod gets IP from Azure VNet
**Routing**: Direct VNet routing
**Network Policy**: Supported (Azure Network Policy or Calico)
**Maximum Pods per Node**: 30 (default), configurable up to 250

**Pros**:
- Pods directly addressable from VNet
- Network policies supported
- Better integration with Azure services
- Can use Azure Firewall, NSGs

**Cons**:
- Higher IP consumption (plan VNet size carefully)
- More expensive (larger subnets needed)

**Use Case**: Production, enterprise, security requirements

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --network-plugin azure \
  --vnet-subnet-id /subscriptions/.../subnets/aks-subnet \
  --service-cidr 10.0.0.0/16 \
  --dns-service-ip 10.0.0.10
```

### Azure CNI Overlay (Hybrid)
**IP Allocation**: Nodes from VNet, pods from overlay network
**Routing**: Overlay network with VNet integration
**Maximum Pods per Node**: 250
**IP Efficiency**: High (only nodes consume VNet IPs)

**Best of Both Worlds**: VNet integration + IP efficiency

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --pod-cidr 10.244.0.0/16
```

## IP Planning Guide

### Azure CNI Example
**Cluster**: 3 node pools × 5 nodes = 15 nodes
**Pods per node**: 30 (default)
**IPs needed**: (15 nodes × 30 pods) + 15 nodes = 465 IPs
**Subnet size**: /23 (512 IPs) minimum

**Formula**: `Subnet Size >= (Node Count × Max Pods per Node) + Node Count + Buffer`

### Recommended Subnet Sizes
| Max Nodes | Max Pods/Node | Min Subnet | Recommended |
|-----------|---------------|------------|-------------|
| 10 | 30 | /24 (256) | /23 (512) |
| 50 | 30 | /22 (1024) | /21 (2048) |
| 100 | 30 | /21 (2048) | /20 (4096) |
| 100 | 110 | /18 (16384) | /17 (32768) |

## Cluster Autoscaler

### Configuration

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10 \
  --node-count 3
```

### Autoscaler Profile

```bash
az aks update \
  --resource-group myRG \
  --name myAKS \
  --cluster-autoscaler-profile \
    scale-down-delay-after-add=10m \
    scale-down-unneeded-time=10m \
    max-graceful-termination-sec=600 \
    scan-interval=10s
```

### Pod Resource Requests (Critical!)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: myapp:1.0
        resources:
          requests:  # REQUIRED for autoscaler
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
```

## Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
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

## Identity and Access

### Managed Identity (Recommended)

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --enable-managed-identity \
  --assign-identity /subscriptions/.../userAssignedIdentities/myIdentity
```

### Azure AD Integration

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --enable-aad \
  --enable-azure-rbac \
  --aad-admin-group-object-ids <AAD_GROUP_ID>
```

### Workload Identity (Pod Identity v2)

```bash
# Enable workload identity
az aks update \
  --resource-group myRG \
  --name myAKS \
  --enable-oidc-issuer \
  --enable-workload-identity
```

**Pod Configuration**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  annotations:
    azure.workload.identity/client-id: <MANAGED_IDENTITY_CLIENT_ID>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      labels:
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: myapp-sa
      containers:
      - name: app
        image: myapp:1.0
```

## Ingress Controllers

### NGINX Ingress Controller

```bash
# Install with Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-nginx \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

### Application Gateway Ingress Controller (AGIC)

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --enable-addons ingress-appgw \
  --appgw-name myAppGateway \
  --appgw-subnet-id /subscriptions/.../subnets/appgw-subnet
```

**Ingress Resource**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
```

## Storage Options

### Azure Disk (Block Storage)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-disk-pvc
spec:
  accessModes:
  - ReadWriteOnce  # Single node only
  storageClassName: managed-premium  # or managed-standard
  resources:
    requests:
      storage: 100Gi
```

**Storage Classes**:
- `default`: Standard HDD
- `managed-premium`: Premium SSD
- `managed-premium-ssd-v2`: Premium SSD v2

### Azure Files (Shared Storage)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-files-pvc
spec:
  accessModes:
  - ReadWriteMany  # Multi-node access
  storageClassName: azurefile
  resources:
    requests:
      storage: 100Gi
```

### Azure Blob (CSI Driver)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-blob-pvc
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: azureblob-nfs-premium
  resources:
    requests:
      storage: 100Gi
```

## Monitoring and Logging

### Azure Monitor Container Insights

```bash
az aks enable-addons \
  --resource-group myRG \
  --name myAKS \
  --addons monitoring \
  --workspace-resource-id /subscriptions/.../workspaces/myWorkspace
```

**Collected Metrics**:
- Node CPU/Memory/Disk
- Pod CPU/Memory
- Container logs
- Kubernetes events
- Inventory data

### Prometheus and Grafana

```bash
# Add Prometheus community helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

## Security Best Practices

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: myapp
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

### Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Private Cluster

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --enable-private-cluster \
  --private-dns-zone system  # or custom
```

### Authorized IP Ranges

```bash
az aks update \
  --resource-group myRG \
  --name myAKS \
  --api-server-authorized-ip-ranges 203.0.113.0/24,198.51.100.0/24
```

## Backup and Disaster Recovery

### Velero Backup

```bash
# Install Velero
velero install \
  --provider azure \
  --plugins velero/velero-plugin-for-microsoft-azure:v1.8.0 \
  --bucket velero \
  --secret-file ./credentials-velero \
  --backup-location-config resourceGroup=myBackupRG,storageAccount=mybackupsa \
  --use-node-agent \
  --use-volume-snapshots=false
```

**Backup Schedule**:
```bash
# Daily backup at 2 AM
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --ttl 720h
```

### Multi-Region Setup

**Primary Cluster**: East US
**Secondary Cluster**: West US
**Traffic Manager**: Route traffic based on health

## Cost Optimization

### Node Pool Scaling

```bash
# Scale node pool to zero during off-hours
az aks nodepool scale \
  --resource-group myRG \
  --cluster-name myAKS \
  --name userpool \
  --node-count 0
```

### Spot Node Pools

```bash
az aks nodepool add \
  --resource-group myRG \
  --cluster-name myAKS \
  --name spotpool \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 10 \
  --node-vm-size Standard_D4s_v3 \
  --node-taints kubernetes.azure.com/scalesetpriority=spot:NoSchedule
```

**Pod Toleration**:
```yaml
tolerations:
- key: "kubernetes.azure.com/scalesetpriority"
  operator: "Equal"
  value: "spot"
  effect: "NoSchedule"
```

### Reserved Instances
- Purchase 1 or 3-year reserved instances for node VMs
- 20-30% (1-year) or 40-60% (3-year) discount

## Troubleshooting

### Common Commands

```bash
# Get cluster credentials
az aks get-credentials --resource-group myRG --name myAKS

# Check node status
kubectl get nodes

# Describe node for events
kubectl describe node <node-name>

# Check pod logs
kubectl logs <pod-name> -n <namespace>

# Execute into pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Check cluster health
az aks show --resource-group myRG --name myAKS --query "powerState"

# View cluster logs
az aks show --resource-group myRG --name myAKS --query "addonProfiles"
```

### Common Issues

**Pods Pending**:
- Check resource requests vs node capacity
- Check node pool autoscaler settings
- Check for node taints/tolerations

**ImagePullBackOff**:
- Check image registry credentials
- Verify image name and tag
- Check ACR integration

**CrashLoopBackOff**:
- Check application logs: `kubectl logs <pod>`
- Check liveness/readiness probes
- Check resource limits

## Production Checklist

- [ ] Use Azure CNI for networking
- [ ] Enable cluster autoscaler
- [ ] Configure HPA for applications
- [ ] Enable Azure Monitor Container Insights
- [ ] Set up managed identity/workload identity
- [ ] Enable Azure AD integration
- [ ] Configure private cluster or authorized IP ranges
- [ ] Implement network policies
- [ ] Set resource requests and limits on all pods
- [ ] Enable auto-upgrade for patches
- [ ] Configure backup solution (Velero)
- [ ] Set up multi-zone or multi-region for HA
- [ ] Use pod security standards
- [ ] Enable Azure Policy for Kubernetes
- [ ] Configure log retention in Log Analytics
- [ ] Set up alerts for critical metrics
- [ ] Implement GitOps (Flux/ArgoCD)
- [ ] Regular vulnerability scanning
- [ ] Document disaster recovery procedures
