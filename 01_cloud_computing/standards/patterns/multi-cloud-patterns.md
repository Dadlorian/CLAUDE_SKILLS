# Multi-Cloud Architecture Patterns

## Overview

Multi-cloud architecture patterns enable organizations to leverage multiple cloud providers (AWS, Azure, GCP) to avoid vendor lock-in, optimize costs, improve resilience, and meet regulatory requirements. This guide covers proven patterns for building cloud-agnostic systems.

## Table of Contents

1. [Abstraction Layer Pattern](#abstraction-layer-pattern)
2. [Cloud-Agnostic Design Pattern](#cloud-agnostic-design-pattern)
3. [Service Mapping Pattern](#service-mapping-pattern)
4. [Cloud Broker Pattern](#cloud-broker-pattern)
5. [Federated Identity Pattern](#federated-identity-pattern)
6. [Data Replication Pattern](#data-replication-pattern)
7. [Cloud Bursting Pattern](#cloud-bursting-pattern)

---

## 1. Abstraction Layer Pattern

### Description

Create abstraction layers that decouple application logic from cloud-specific APIs, enabling portability across providers.

### When to Use

- Building applications that need to run on multiple cloud providers
- Avoiding vendor lock-in
- Supporting hybrid cloud deployments
- Enabling cloud migration flexibility

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│            (Business Logic & Core Services)              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Cloud Abstraction Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Storage    │  │   Compute    │  │  Messaging   │  │
│  │  Interface   │  │  Interface   │  │  Interface   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────┬───────────────┬────────────────┬────────────┘
           │               │                │
     ┌─────▼─────┐   ┌────▼────┐     ┌────▼────┐
     │    AWS    │   │  Azure  │     │   GCP   │
     │ Adapter   │   │ Adapter │     │ Adapter │
     └─────┬─────┘   └────┬────┘     └────┬────┘
           │              │                │
     ┌─────▼─────┐   ┌────▼────┐     ┌────▼────┐
     │    S3     │   │  Blob   │     │  Cloud  │
     │  Lambda   │   │Functions│     │Functions│
     │    SQS    │   │EventGrid│     │ Pub/Sub │
     └───────────┘   └─────────┘     └─────────┘
```

### Implementation Example

```python
# abstraction/storage.py
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class CloudStorageProvider(ABC):
    """Abstract base class for cloud storage operations"""

    @abstractmethod
    def upload_file(self, bucket: str, key: str, data: BinaryIO) -> bool:
        pass

    @abstractmethod
    def download_file(self, bucket: str, key: str) -> bytes:
        pass

    @abstractmethod
    def delete_file(self, bucket: str, key: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, bucket: str, prefix: str = "") -> list:
        pass


# providers/aws_storage.py
import boto3
from abstraction.storage import CloudStorageProvider

class AWSStorageProvider(CloudStorageProvider):
    def __init__(self, region: str = "us-east-1"):
        self.s3_client = boto3.client('s3', region_name=region)

    def upload_file(self, bucket: str, key: str, data: BinaryIO) -> bool:
        try:
            self.s3_client.upload_fileobj(data, bucket, key)
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def download_file(self, bucket: str, key: str) -> bytes:
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    def delete_file(self, bucket: str, key: str) -> bool:
        self.s3_client.delete_object(Bucket=bucket, Key=key)
        return True

    def list_files(self, bucket: str, prefix: str = "") -> list:
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]


# providers/azure_storage.py
from azure.storage.blob import BlobServiceClient
from abstraction.storage import CloudStorageProvider

class AzureStorageProvider(CloudStorageProvider):
    def __init__(self, connection_string: str):
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)

    def upload_file(self, bucket: str, key: str, data: BinaryIO) -> bool:
        try:
            container_client = self.blob_service.get_container_client(bucket)
            blob_client = container_client.get_blob_client(key)
            blob_client.upload_blob(data, overwrite=True)
            return True
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    def download_file(self, bucket: str, key: str) -> bytes:
        container_client = self.blob_service.get_container_client(bucket)
        blob_client = container_client.get_blob_client(key)
        return blob_client.download_blob().readall()

    def delete_file(self, bucket: str, key: str) -> bool:
        container_client = self.blob_service.get_container_client(bucket)
        blob_client = container_client.get_blob_client(key)
        blob_client.delete_blob()
        return True

    def list_files(self, bucket: str, prefix: str = "") -> list:
        container_client = self.blob_service.get_container_client(bucket)
        return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]


# Factory pattern for provider instantiation
class StorageProviderFactory:
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> CloudStorageProvider:
        if provider_type == "aws":
            return AWSStorageProvider(region=kwargs.get("region", "us-east-1"))
        elif provider_type == "azure":
            return AzureStorageProvider(connection_string=kwargs["connection_string"])
        elif provider_type == "gcp":
            from providers.gcp_storage import GCPStorageProvider
            return GCPStorageProvider(project_id=kwargs["project_id"])
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
```

### Terraform Configuration

```hcl
# multi-cloud storage abstraction using Terraform

# AWS S3 Bucket
resource "aws_s3_bucket" "multi_cloud_storage" {
  count  = var.enable_aws ? 1 : 0
  bucket = "${var.project_name}-storage-aws"

  tags = {
    Environment = var.environment
    Provider    = "AWS"
  }
}

# Azure Storage Account
resource "azurerm_storage_account" "multi_cloud_storage" {
  count                    = var.enable_azure ? 1 : 0
  name                     = "${var.project_name}storageazure"
  resource_group_name      = azurerm_resource_group.main[0].name
  location                 = var.azure_region
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    Environment = var.environment
    Provider    = "Azure"
  }
}

# GCP Storage Bucket
resource "google_storage_bucket" "multi_cloud_storage" {
  count    = var.enable_gcp ? 1 : 0
  name     = "${var.project_name}-storage-gcp"
  location = var.gcp_region

  labels = {
    environment = var.environment
    provider    = "gcp"
  }
}

# Output unified storage configuration
output "storage_config" {
  value = {
    aws = var.enable_aws ? {
      bucket = aws_s3_bucket.multi_cloud_storage[0].id
      region = var.aws_region
    } : null

    azure = var.enable_azure ? {
      account_name = azurerm_storage_account.multi_cloud_storage[0].name
      container    = azurerm_storage_container.main[0].name
    } : null

    gcp = var.enable_gcp ? {
      bucket  = google_storage_bucket.multi_cloud_storage[0].name
      project = var.gcp_project_id
    } : null
  }
}
```

### Trade-offs

**Pros:**
- Vendor independence and flexibility
- Easier cloud migration
- Reduced risk of vendor lock-in
- Negotiation leverage with providers

**Cons:**
- Additional abstraction layer complexity
- Potential performance overhead
- Maintenance burden for multiple adapters
- May miss cloud-specific optimizations

### Anti-patterns

- **Leaky Abstraction**: Exposing provider-specific details through the abstraction layer
- **Over-abstraction**: Creating abstractions for every minor cloud service
- **Lowest Common Denominator**: Only supporting features available across all clouds
- **Ignoring Provider Strengths**: Not leveraging unique cloud capabilities when beneficial

### Real-world Examples

**Netflix**: Uses Spinnaker for multi-cloud deployment abstraction across AWS and GCP, enabling seamless workload distribution.

**Spotify**: Implements storage abstraction layers allowing data to be stored across GCP and AWS based on regional requirements.

**Capital One**: Built cloud abstraction frameworks enabling applications to run on multiple clouds without code changes.

---

## 2. Cloud-Agnostic Design Pattern

### Description

Design applications using cloud-agnostic technologies and standards (Kubernetes, containers, open-source tools) that can run anywhere.

### When to Use

- Starting new cloud-native applications
- Need maximum portability
- Avoiding proprietary services
- Supporting on-premises and cloud deployments

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│           Cloud-Agnostic Application Stack               │
├─────────────────────────────────────────────────────────┤
│  Application Layer (Containerized Microservices)        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Service │  │ Service │  │ Service │  │ Service │   │
│  │    A    │  │    B    │  │    C    │  │    D    │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
├─────────────────────────────────────────────────────────┤
│  Service Mesh (Istio/Linkerd)                           │
├─────────────────────────────────────────────────────────┤
│  Kubernetes Orchestration                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Ingress   │  │   ConfigMap │  │   Secrets   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────┤
│  Container Runtime (containerd/CRI-O)                   │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │   AWS   │    │  Azure  │    │   GCP   │
   │   EKS   │    │   AKS   │    │   GKE   │
   └─────────┘    └─────────┘    └─────────┘
```

### Implementation Example

```yaml
# kubernetes/deployment.yaml - Cloud-agnostic Kubernetes manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-cloud-app
  labels:
    app: multi-cloud-app
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: multi-cloud-app
  template:
    metadata:
      labels:
        app: multi-cloud-app
    spec:
      containers:
      - name: app
        image: myregistry/multi-cloud-app:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: CLOUD_PROVIDER
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: provider
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: multi-cloud-app-service
spec:
  selector:
    app: multi-cloud-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: multi-cloud-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: multi-cloud-app
  minReplicas: 3
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

### Tool Recommendations

**Container Orchestration:**
- Kubernetes (EKS, AKS, GKE, self-managed)
- Nomad (HashiCorp)
- Docker Swarm

**Service Mesh:**
- Istio
- Linkerd
- Consul Connect

**Infrastructure as Code:**
- Pulumi (multi-language, cloud-agnostic)
- Terraform
- Crossplane

**CI/CD:**
- Jenkins
- GitLab CI
- Argo CD
- Flux

**Monitoring & Observability:**
- Prometheus + Grafana
- Elastic Stack
- OpenTelemetry
- Jaeger

---

## 3. Service Mapping Pattern

### Description

Map equivalent services across cloud providers to enable consistent functionality while leveraging provider-specific implementations.

### Service Mapping Table

| Category | AWS | Azure | GCP |
|----------|-----|-------|-----|
| **Compute** | EC2 | Virtual Machines | Compute Engine |
| **Serverless** | Lambda | Functions | Cloud Functions |
| **Containers** | ECS/EKS | AKS | GKE |
| **Object Storage** | S3 | Blob Storage | Cloud Storage |
| **Block Storage** | EBS | Managed Disks | Persistent Disk |
| **CDN** | CloudFront | Azure CDN | Cloud CDN |
| **DNS** | Route 53 | Azure DNS | Cloud DNS |
| **Load Balancer** | ELB/ALB | Load Balancer | Cloud Load Balancing |
| **Database (SQL)** | RDS | Azure SQL | Cloud SQL |
| **Database (NoSQL)** | DynamoDB | Cosmos DB | Firestore/Bigtable |
| **Cache** | ElastiCache | Azure Cache | Memorystore |
| **Message Queue** | SQS | Queue Storage | Cloud Tasks |
| **Pub/Sub** | SNS | Event Grid | Pub/Sub |
| **API Gateway** | API Gateway | API Management | API Gateway |
| **Identity** | IAM | Azure AD | Cloud IAM |
| **Secrets** | Secrets Manager | Key Vault | Secret Manager |
| **Monitoring** | CloudWatch | Monitor | Cloud Monitoring |
| **Logging** | CloudWatch Logs | Log Analytics | Cloud Logging |

### Implementation Example

```python
# service_mapper.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class ServiceType(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    MESSAGING = "messaging"
    CACHE = "cache"

@dataclass
class ServiceConfig:
    provider: CloudProvider
    service_name: str
    endpoint: str
    credentials: Dict[str, Any]
    region: str

class MultiCloudServiceMapper:
    def __init__(self):
        self.service_map = {
            ServiceType.STORAGE: {
                CloudProvider.AWS: "s3",
                CloudProvider.AZURE: "blob_storage",
                CloudProvider.GCP: "cloud_storage"
            },
            ServiceType.COMPUTE: {
                CloudProvider.AWS: "ec2",
                CloudProvider.AZURE: "virtual_machines",
                CloudProvider.GCP: "compute_engine"
            },
            ServiceType.DATABASE: {
                CloudProvider.AWS: "rds",
                CloudProvider.AZURE: "azure_sql",
                CloudProvider.GCP: "cloud_sql"
            },
            ServiceType.MESSAGING: {
                CloudProvider.AWS: "sqs",
                CloudProvider.AZURE: "queue_storage",
                CloudProvider.GCP: "pub_sub"
            },
            ServiceType.CACHE: {
                CloudProvider.AWS: "elasticache",
                CloudProvider.AZURE: "azure_cache",
                CloudProvider.GCP: "memorystore"
            }
        }

    def get_service(self, service_type: ServiceType, provider: CloudProvider) -> str:
        """Get the equivalent service for a given provider"""
        return self.service_map[service_type][provider]

    def get_all_equivalents(self, service_type: ServiceType) -> Dict[CloudProvider, str]:
        """Get all equivalent services across providers"""
        return self.service_map[service_type]

    def create_service_client(self, service_type: ServiceType,
                            provider: CloudProvider,
                            config: ServiceConfig):
        """Factory method to create appropriate service client"""
        service_name = self.get_service(service_type, provider)

        if provider == CloudProvider.AWS:
            return self._create_aws_client(service_name, config)
        elif provider == CloudProvider.AZURE:
            return self._create_azure_client(service_name, config)
        elif provider == CloudProvider.GCP:
            return self._create_gcp_client(service_name, config)

    def _create_aws_client(self, service_name: str, config: ServiceConfig):
        import boto3
        return boto3.client(service_name,
                          region_name=config.region,
                          **config.credentials)

    def _create_azure_client(self, service_name: str, config: ServiceConfig):
        # Azure client creation logic
        pass

    def _create_gcp_client(self, service_name: str, config: ServiceConfig):
        # GCP client creation logic
        pass
```

### Real-world Examples

**Airbnb**: Maps compute and storage services across AWS and GCP, using equivalent services for different regional deployments.

**Adobe**: Uses service mapping to run Creative Cloud services on both AWS and Azure, matching functionality across providers.

---

## 4. Cloud Broker Pattern

### Description

Implement a cloud broker/gateway that routes requests to appropriate cloud providers based on policies, costs, or availability.

### Architecture Diagram

```
                     ┌─────────────┐
                     │   Client    │
                     │ Application │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │    Cloud    │
                     │   Broker    │
                     │  (Gateway)  │
                     └──────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌───▼────┐         ┌───▼────┐
   │ Policy  │         │  Cost  │         │ Health │
   │ Engine  │         │ Engine │         │ Check  │
   └────┬────┘         └───┬────┘         └───┬────┘
        │                  │                   │
        └──────────────────┼───────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌───▼────┐        ┌───▼────┐
   │   AWS   │        │ Azure  │        │  GCP   │
   │Services │        │Services│        │Services│
   └─────────┘        └────────┘        └────────┘
```

### Trade-offs

**Pros:**
- Cost optimization through provider selection
- Improved availability through fallback
- Flexibility in provider usage
- Centralized governance

**Cons:**
- Single point of failure (broker)
- Increased latency
- Complex routing logic
- Additional infrastructure to manage

---

## 5. Federated Identity Pattern

### Description

Implement federated identity and access management across multiple cloud providers using standards like SAML, OAuth, and OpenID Connect.

### Architecture Diagram

```
                    ┌──────────────┐
                    │  Identity    │
                    │   Provider   │
                    │ (Okta/Auth0) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼───┐   ┌───▼────┐  ┌───▼────┐
         │  AWS   │   │ Azure  │  │  GCP   │
         │  IAM   │   │   AD   │  │  IAM   │
         │ (SAML) │   │(OIDC)  │  │(OIDC)  │
         └────┬───┘   └───┬────┘  └───┬────┘
              │           │           │
         ┌────▼───┐   ┌───▼────┐  ┌───▼────┐
         │  AWS   │   │ Azure  │  │  GCP   │
         │Services│   │Services│  │Services│
         └────────┘   └────────┘  └────────┘
```

### Real-world Examples

**Walmart**: Uses federated identity to manage access across AWS, Azure, and private cloud infrastructure.

**Bloomberg**: Implements single sign-on across multiple cloud providers using federated identity standards.

---

## 6. Data Replication Pattern

### Description

Replicate data across multiple cloud providers for redundancy, performance, and disaster recovery.

### Implementation Types

**Synchronous Replication:**
- Real-time data consistency
- Higher latency
- Used for critical data

**Asynchronous Replication:**
- Lower latency
- Eventual consistency
- Suitable for most use cases

**Selective Replication:**
- Replicate only critical data
- Cost-effective
- Reduces bandwidth usage

### Tool Recommendations

**Data Replication Tools:**
- Apache Kafka (with MirrorMaker)
- AWS Database Migration Service
- Azure Data Factory
- GCP Datastream
- Airbyte
- Fivetran

---

## 7. Cloud Bursting Pattern

### Description

Run workloads on a primary cloud but burst to secondary clouds during peak demand or when capacity is needed.

### When to Use

- Handle unpredictable traffic spikes
- Optimize costs (use cheaper cloud for burst)
- Disaster recovery scenarios
- Development/testing environments

### Architecture Diagram

```
        Normal Load              Peak Load

    ┌───────────┐           ┌───────────┐
    │ Primary   │           │ Primary   │
    │  Cloud    │           │  Cloud    │
    │  (AWS)    │           │  (AWS)    │
    │           │           │           │
    │ ████████  │           │ ██████████│ (At Capacity)
    └───────────┘           └─────┬─────┘
                                  │
                            ┌─────▼─────┐
                            │Secondary  │
                            │  Cloud    │
                            │  (Azure)  │
                            │           │
                            │ ████      │ (Burst Traffic)
                            └───────────┘
```

### Real-world Examples

**Lyft**: Uses cloud bursting from primary AWS infrastructure to GCP during peak demand periods.

**Pinterest**: Implements bursting strategies to handle seasonal traffic spikes across multiple clouds.

---

## Summary

Multi-cloud patterns enable organizations to:

1. **Reduce vendor lock-in** through abstraction and portability
2. **Optimize costs** by leveraging competitive pricing
3. **Improve resilience** through geographic and provider diversity
4. **Meet compliance** requirements with regional flexibility
5. **Leverage best-of-breed** services from each provider

### Key Success Factors

- **Start with abstraction**: Design for portability from day one
- **Use open standards**: Kubernetes, containers, open-source tools
- **Automate everything**: Infrastructure as Code across all providers
- **Monitor costs**: Multi-cloud can increase complexity and costs
- **Train teams**: Ensure expertise across chosen platforms
- **Governance**: Centralized policies and security controls

### Recommended Tool Stack

| Layer | Tools |
|-------|-------|
| **Orchestration** | Kubernetes, Terraform, Pulumi |
| **Service Mesh** | Istio, Linkerd |
| **Identity** | Okta, Auth0, Keycloak |
| **Monitoring** | Prometheus, Grafana, DataDog |
| **Security** | HashiCorp Vault, Open Policy Agent |
| **CI/CD** | GitLab, Jenkins, Argo CD |
| **Cost Management** | CloudHealth, Kubecost |

### FAANG Insights

- **Amazon**: While AWS-focused, uses multi-region for global reach
- **Facebook/Meta**: Multi-cloud strategy across own datacenters and major providers
- **Apple**: Strategic use of AWS, GCP, and Azure for different services
- **Netflix**: Primary AWS with expanding GCP usage for specific workloads
- **Google**: Primarily GCP but uses AWS for certain third-party integrations
