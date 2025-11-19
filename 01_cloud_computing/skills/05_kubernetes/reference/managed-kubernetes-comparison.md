# Managed Kubernetes Services Comparison

## Overview

This document compares the major managed Kubernetes services: Amazon EKS, Azure AKS, and Google GKE.

## Service Comparison Matrix

| Feature | Amazon EKS | Azure AKS | Google GKE |
|---------|------------|-----------|------------|
| **Control Plane** | Managed, HA by default | Managed, free | Managed, charged ($0.10/hr Standard) |
| **Node Management** | Self-managed or managed node groups | Virtual Machine Scale Sets | Node pools |
| **Serverless Pods** | Fargate | Virtual Nodes (ACI) | Autopilot / Cloud Run for Anthos |
| **Kubernetes Version** | Up to 3 minor versions | Up to 2 versions behind latest | Latest + 2 previous |
| **Auto-upgrade** | Opt-in | Configurable | Configurable |
| **Multi-cluster Management** | EKS Anywhere, EKS Connector | Azure Arc | Anthos, GKE Enterprise |
| **Service Mesh** | AWS App Mesh | Istio (preview), Linkerd, Consul | Anthos Service Mesh (Istio) |
| **GitOps** | Flux (add-on) | Flux (extension) | Config Sync (Anthos) |
| **Policy Management** | OPA Gatekeeper | Azure Policy | Policy Controller (Anthos) |
| **Monitoring** | CloudWatch Container Insights | Azure Monitor | Cloud Monitoring, Cloud Logging |
| **Security Scanning** | ECR scanning | Defender for Containers | Container Analysis, Binary Authorization |
| **Identity Integration** | IAM Roles for Service Accounts (IRSA) | AAD Pod Identity, Workload Identity | Workload Identity |
| **Network Plugin** | AWS VPC CNI, Calico | Azure CNI, Kubenet, Calico | GKE Dataplane V2 (Cilium) |
| **Private Clusters** | Yes | Yes | Yes |
| **Windows Support** | Yes | Yes | Yes |
| **ARM Support** | Graviton | Yes | Yes |
| **Regional HA** | Multi-AZ by default | Availability Zones | Multi-zonal by default |
| **SLA** | 99.95% (multi-AZ) | 99.95% (SLA), 99.9% (SLO) | 99.95% (Regional), 99.5% (Zonal) |

## Amazon EKS (Elastic Kubernetes Service)

### Architecture

**Control Plane**:
- Managed by AWS
- Runs in AWS-managed VPC
- Multi-AZ by default (3 AZs minimum)
- etcd automatic backups

**Data Plane**:
- Self-managed nodes
- Managed node groups
- Fargate (serverless)

### Key Features

**Managed Node Groups**:
```bash
# Create node group
eksctl create nodegroup \
  --cluster my-cluster \
  --name ng-1 \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed
```

**Fargate**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fargate-ns
  labels:
    fargate: enabled
```

```bash
# Create Fargate profile
eksctl create fargateprofile \
  --cluster my-cluster \
  --name my-profile \
  --namespace fargate-ns
```

**IAM Roles for Service Accounts (IRSA)**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/my-app-role
```

**EKS Add-ons**:
- VPC CNI
- CoreDNS
- kube-proxy
- EBS CSI Driver
- EFS CSI Driver
- Amazon GuardDuty
- AWS Load Balancer Controller

### Networking

**VPC CNI**:
- Each pod gets VPC IP address
- Security groups for pods
- IP address management via IPAM

**Load Balancing**:
- Classic Load Balancer (deprecated)
- Network Load Balancer (Layer 4)
- Application Load Balancer (Layer 7)
- AWS Load Balancer Controller

### Security

**Security Features**:
- IAM authentication via aws-auth ConfigMap
- IRSA for pod-level permissions
- Encryption at rest (etcd via KMS)
- Secrets encryption via KMS
- Private API endpoint
- Security groups for pods

**Best Practices**:
```bash
# Enable secrets encryption
aws eks create-cluster \
  --encryption-config resources=secrets,provider.keyArn=arn:aws:kms:...
```

### Cost Structure

- **Control Plane**: $0.10/hour per cluster (~$73/month)
- **Nodes**: EC2 instance pricing
- **Fargate**: vCPU and memory pricing
- **Data Transfer**: Standard AWS rates

### EKS Anywhere

- Run EKS on-premises
- Curated Kubernetes distribution
- Optional AWS support subscription
- Integration with AWS services

## Azure AKS (Azure Kubernetes Service)

### Architecture

**Control Plane**:
- Fully managed by Azure
- Free (no charge for control plane)
- SLA requires Availability Zones or multiple node pools

**Data Plane**:
- Virtual Machine Scale Sets
- Virtual Nodes (Azure Container Instances)

### Key Features

**Auto-scaling**:
```bash
# Enable cluster autoscaler
az aks update \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 5
```

**Virtual Nodes (ACI)**:
```bash
# Enable virtual nodes
az aks enable-addons \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --addons virtual-node \
  --subnet-name VirtualNodeSubnet
```

**Azure AD Integration**:
```bash
# Create AKS with Azure AD integration
az aks create \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --enable-aad \
  --aad-admin-group-object-ids <group-id>
```

**Workload Identity**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: workload-identity-sa
  annotations:
    azure.workload.identity/client-id: <client-id>
    azure.workload.identity/tenant-id: <tenant-id>
```

**AKS Extensions**:
- Azure Policy
- Azure Monitor
- Dapr
- Azure Key Vault Provider
- GitOps (Flux)
- Open Service Mesh

### Networking

**Network Plugins**:
- **Azure CNI**: Pods get VNet IPs
- **Kubenet**: Pods get IPs from overlay network
- **Azure CNI Overlay**: New, combines benefits
- **Bring your own CNI**: Cilium, Calico

**Load Balancing**:
- Azure Load Balancer (Layer 4)
- Application Gateway (Layer 7)
- Application Gateway Ingress Controller (AGIC)

### Security

**Security Features**:
- Azure AD authentication
- Workload Identity
- Azure Policy integration
- Secrets Store CSI Driver
- Microsoft Defender for Containers
- Private cluster
- API server authorized IP ranges

**Azure Policy for AKS**:
```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAzureContainerAllowedImages
metadata:
  name: allowed-images
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters:
    imageRegex: "^myregistry\\.azurecr\\.io/.+"
```

### Cost Structure

- **Control Plane**: Free
- **Nodes**: VM pricing
- **Virtual Nodes**: ACI pricing (per second)
- **Standard Tier**: $0.10/hour for SLA (~$73/month)
- **Data Transfer**: Standard Azure rates

### Azure Arc-Enabled Kubernetes

- Manage any Kubernetes cluster
- Azure Policy and GitOps
- Azure Monitor integration
- Cluster extensions
- Connect on-premises or other clouds

## Google GKE (Google Kubernetes Engine)

### Architecture

**Control Plane**:
- Managed by Google
- Standard: $0.10/hour
- Autopilot: Free control plane

**Data Plane**:
- Standard: Managed node pools
- Autopilot: Fully managed, serverless

### Key Features

**GKE Autopilot**:
```bash
# Create Autopilot cluster
gcloud container clusters create-auto my-cluster \
  --region us-central1
```

- Fully managed nodes
- Pay only for pods
- Built-in security best practices
- Automatic scaling and upgrades

**GKE Standard**:
```bash
# Create Standard cluster
gcloud container clusters create my-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10
```

**Workload Identity**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    iam.gke.io/gcp-service-account: my-app@project.iam.gserviceaccount.com
```

**GKE Features**:
- Binary Authorization
- Config Connector (IaC)
- Config Sync (GitOps)
- Anthos Service Mesh
- GKE Dataplane V2 (Cilium-based)
- Backup for GKE

### Networking

**Network Plugins**:
- **GKE Dataplane V2**: eBPF-based (Cilium)
- **Standard**: Traditional dataplane

**Load Balancing**:
- Network Load Balancer (Layer 4)
- HTTP(S) Load Balancer (Layer 7)
- Internal Load Balancer
- Container-native load balancing

**Multi-cluster Networking**:
- Shared VPC
- VPC peering
- Multi-cluster ingress
- Multi-cluster services

### Security

**Security Features**:
- Workload Identity
- Binary Authorization
- Shielded GKE nodes
- Container-Optimized OS
- Automatic security patches
- Private clusters
- GKE Sandbox (gVisor)

**Binary Authorization**:
```yaml
apiVersion: binaryauthorization.grafeas.io/v1beta1
kind: Policy
metadata:
  name: my-policy
spec:
  admissionWhitelistPatterns:
  - namePattern: gcr.io/myproject/*
  globalPolicyEvaluationMode: ENABLE
  defaultAdmissionRule:
    requireAttestationsBy:
    - projects/myproject/attestors/my-attestor
    enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
```

### Cost Structure

**Standard Mode**:
- **Control Plane**: $0.10/hour (~$73/month)
- **Nodes**: Compute Engine pricing
- **Zonal clusters**: $0.10/hour
- **Regional clusters**: $0.10/hour

**Autopilot Mode**:
- **Control Plane**: Free
- **Resources**: Pay for pod requests (vCPU, memory, ephemeral storage)
- Pricing: ~$0.05/vCPU-hour, ~$0.005/GB-hour

### Anthos

- Multi-cloud and on-premises Kubernetes
- Centralized management
- Service mesh (Anthos Service Mesh)
- Config management
- Policy controller
- Per-vCPU pricing

## Feature Deep Dive

### Serverless Options

**EKS Fargate**:
- Pod-level serverless
- Fargate profiles for namespace/label selection
- Pay per pod (vCPU/memory)
- No node management

**AKS Virtual Nodes**:
- Azure Container Instances integration
- Pod-level serverless
- Fast startup times
- Pay per second

**GKE Autopilot**:
- Fully managed cluster
- Node-level abstraction
- Pay for pod resources
- Google manages everything

### Auto-scaling

**EKS**:
- Cluster Autoscaler
- Karpenter (node provisioning)
- HPA (built-in)
- VPA (separate install)

**AKS**:
- Cluster Autoscaler (built-in)
- Virtual Node scaling
- HPA (built-in)
- KEDA integration

**GKE**:
- Cluster Autoscaler
- Node Auto Provisioning
- HPA (built-in)
- VPA (beta, built-in for Autopilot)

### Identity and Permissions

**EKS - IRSA**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/ROLE_NAME
```

**AKS - Workload Identity**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: CLIENT_ID
    azure.workload.identity/tenant-id: TENANT_ID
```

**GKE - Workload Identity**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    iam.gke.io/gcp-service-account: SA_NAME@PROJECT.iam.gserviceaccount.com
```

## Choosing the Right Service

### Choose EKS if:
- Already on AWS ecosystem
- Need deep AWS service integration
- Require Fargate for serverless
- Using AWS security services
- Want EKS Anywhere for hybrid

### Choose AKS if:
- Already on Azure ecosystem
- Need Azure AD integration
- Want free control plane
- Using Azure DevOps/GitHub Actions
- Need Azure Arc for hybrid

### Choose GKE if:
- Want latest Kubernetes features first
- Prefer fully managed (Autopilot)
- Need advanced networking (Cilium)
- Want Anthos for multi-cloud
- Prioritize ease of use

## Migration Considerations

### Cross-Cloud Migration
- Backup using Velero
- Recreate cluster in target cloud
- Migrate persistent volumes
- Update cloud-specific resources
- Test thoroughly before cutover

### Multi-Cloud Strategy
- Use Anthos, Azure Arc, or EKS Anywhere
- Abstract cloud services with operators
- Use cloud-agnostic storage (Rook, Longhorn)
- Implement GitOps for consistency
- Plan for networking complexity

## Cost Optimization

### General Strategies
- Use spot/preemptible instances
- Right-size nodes and pods
- Enable cluster autoscaling
- Use serverless for variable workloads
- Implement pod disruption budgets
- Monitor and optimize continuously

### Service-Specific

**EKS**:
- Use Savings Plans or Reserved Instances
- Consider Fargate Spot
- Use Karpenter for efficient provisioning

**AKS**:
- Use Azure Reservations
- Consider Spot node pools
- Free control plane

**GKE**:
- Use Committed Use Discounts
- Consider Autopilot for variable loads
- Use Preemptible VMs

## References

- [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Azure AKS Documentation](https://docs.microsoft.com/azure/aks/)
- [Google GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- [AKS Baseline Architecture](https://docs.microsoft.com/azure/architecture/reference-architectures/containers/aks/secure-baseline-aks)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
