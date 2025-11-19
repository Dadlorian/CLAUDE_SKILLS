# Multi-Cloud API Patterns

## Table of Contents
- [Introduction](#introduction)
- [Core Principles](#core-principles)
- [Abstraction Patterns](#abstraction-patterns)
- [Cloud-Agnostic API Design](#cloud-agnostic-api-design)
- [Multi-Cloud Integration Strategies](#multi-cloud-integration-strategies)
- [Real-World Examples](#real-world-examples)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Introduction

Multi-cloud API patterns enable organizations to build applications that work seamlessly across different cloud providers (AWS, Azure, GCP) without tight coupling to any single vendor. This approach provides flexibility, reduces vendor lock-in, and enables strategic use of best-of-breed services.

### Why Multi-Cloud APIs Matter

- **Vendor Independence**: Avoid lock-in to a single cloud provider
- **Risk Mitigation**: Distribute workloads across multiple providers
- **Cost Optimization**: Leverage competitive pricing across clouds
- **Regulatory Compliance**: Meet data residency requirements
- **Business Continuity**: Enable disaster recovery across clouds

## Core Principles

### 1. Abstraction Over Implementation

Create abstraction layers that hide cloud-specific implementation details:

```python
# Cloud-agnostic storage interface
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class CloudStorageAdapter(ABC):
    """Abstract base class for cloud storage operations"""

    @abstractmethod
    async def upload_object(self, bucket: str, key: str, data: BinaryIO) -> str:
        """Upload object to cloud storage"""
        pass

    @abstractmethod
    async def download_object(self, bucket: str, key: str) -> bytes:
        """Download object from cloud storage"""
        pass

    @abstractmethod
    async def delete_object(self, bucket: str, key: str) -> bool:
        """Delete object from cloud storage"""
        pass

    @abstractmethod
    async def generate_presigned_url(self, bucket: str, key: str,
                                    expiry: int = 3600) -> str:
        """Generate presigned URL for temporary access"""
        pass

# AWS S3 Implementation
import boto3
from botocore.exceptions import ClientError

class S3Adapter(CloudStorageAdapter):
    def __init__(self, region: str = 'us-east-1'):
        self.s3_client = boto3.client('s3', region_name=region)

    async def upload_object(self, bucket: str, key: str, data: BinaryIO) -> str:
        try:
            self.s3_client.upload_fileobj(data, bucket, key)
            return f"s3://{bucket}/{key}"
        except ClientError as e:
            raise StorageException(f"S3 upload failed: {str(e)}")

    async def download_object(self, bucket: str, key: str) -> bytes:
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise StorageException(f"S3 download failed: {str(e)}")

    async def delete_object(self, bucket: str, key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            raise StorageException(f"S3 delete failed: {str(e)}")

    async def generate_presigned_url(self, bucket: str, key: str,
                                    expiry: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiry
            )
            return url
        except ClientError as e:
            raise StorageException(f"S3 presigned URL generation failed: {str(e)}")

# Azure Blob Storage Implementation
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

class AzureBlobAdapter(CloudStorageAdapter):
    def __init__(self, connection_string: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    async def upload_object(self, container: str, blob_name: str, data: BinaryIO) -> str:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container, blob=blob_name
            )
            blob_client.upload_blob(data, overwrite=True)
            return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{container}/{blob_name}"
        except AzureError as e:
            raise StorageException(f"Azure Blob upload failed: {str(e)}")

    async def download_object(self, container: str, blob_name: str) -> bytes:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container, blob=blob_name
            )
            return blob_client.download_blob().readall()
        except AzureError as e:
            raise StorageException(f"Azure Blob download failed: {str(e)}")

    async def delete_object(self, container: str, blob_name: str) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container, blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except AzureError as e:
            raise StorageException(f"Azure Blob delete failed: {str(e)}")

    async def generate_presigned_url(self, container: str, blob_name: str,
                                    expiry: int = 3600) -> str:
        from datetime import datetime, timedelta
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions

        try:
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=container,
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expiry)
            )
            return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{container}/{blob_name}?{sas_token}"
        except AzureError as e:
            raise StorageException(f"Azure SAS generation failed: {str(e)}")

# GCP Cloud Storage Implementation
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

class GCSAdapter(CloudStorageAdapter):
    def __init__(self, project_id: str):
        self.storage_client = storage.Client(project=project_id)

    async def upload_object(self, bucket_name: str, blob_name: str, data: BinaryIO) -> str:
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_file(data)
            return f"gs://{bucket_name}/{blob_name}"
        except GoogleCloudError as e:
            raise StorageException(f"GCS upload failed: {str(e)}")

    async def download_object(self, bucket_name: str, blob_name: str) -> bytes:
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
        except GoogleCloudError as e:
            raise StorageException(f"GCS download failed: {str(e)}")

    async def delete_object(self, bucket_name: str, blob_name: str) -> bool:
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            return True
        except GoogleCloudError as e:
            raise StorageException(f"GCS delete failed: {str(e)}")

    async def generate_presigned_url(self, bucket_name: str, blob_name: str,
                                    expiry: int = 3600) -> str:
        from datetime import timedelta

        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(seconds=expiry),
                method="GET"
            )
            return url
        except GoogleCloudError as e:
            raise StorageException(f"GCS signed URL generation failed: {str(e)}")

class StorageException(Exception):
    """Custom exception for storage operations"""
    pass
```

### 2. Configuration-Driven Cloud Selection

Use configuration to determine which cloud provider to use:

```python
# config.py
from enum import Enum
from pydantic import BaseSettings

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class MultiCloudConfig(BaseSettings):
    # Primary cloud provider
    primary_cloud: CloudProvider = CloudProvider.AWS

    # Storage configuration
    storage_provider: CloudProvider = CloudProvider.AWS
    aws_s3_region: str = "us-east-1"
    azure_storage_connection_string: str = ""
    gcp_project_id: str = ""

    # Compute configuration
    compute_provider: CloudProvider = CloudProvider.AWS
    aws_lambda_region: str = "us-east-1"
    azure_function_app_name: str = ""
    gcp_cloud_run_region: str = "us-central1"

    # Database configuration
    database_provider: CloudProvider = CloudProvider.AWS

    class Config:
        env_file = ".env"

# factory.py
from typing import Dict, Type

class CloudServiceFactory:
    """Factory pattern for creating cloud service instances"""

    _storage_adapters: Dict[CloudProvider, Type[CloudStorageAdapter]] = {
        CloudProvider.AWS: S3Adapter,
        CloudProvider.AZURE: AzureBlobAdapter,
        CloudProvider.GCP: GCSAdapter,
    }

    @classmethod
    def create_storage_adapter(cls, config: MultiCloudConfig) -> CloudStorageAdapter:
        """Create storage adapter based on configuration"""
        adapter_class = cls._storage_adapters.get(config.storage_provider)

        if adapter_class is None:
            raise ValueError(f"Unsupported storage provider: {config.storage_provider}")

        if config.storage_provider == CloudProvider.AWS:
            return adapter_class(region=config.aws_s3_region)
        elif config.storage_provider == CloudProvider.AZURE:
            return adapter_class(connection_string=config.azure_storage_connection_string)
        elif config.storage_provider == CloudProvider.GCP:
            return adapter_class(project_id=config.gcp_project_id)
```

## Abstraction Patterns

### 1. Adapter Pattern

The Adapter pattern translates cloud-specific APIs into a common interface:

```typescript
// TypeScript example for cloud messaging
interface CloudMessage {
  id: string;
  body: string;
  attributes: Record<string, string>;
  timestamp: Date;
}

interface CloudMessageQueueAdapter {
  sendMessage(queueUrl: string, message: CloudMessage): Promise<string>;
  receiveMessages(queueUrl: string, maxMessages: number): Promise<CloudMessage[]>;
  deleteMessage(queueUrl: string, messageId: string): Promise<void>;
  getQueueUrl(queueName: string): Promise<string>;
}

// AWS SQS Adapter
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from "@aws-sdk/client-sqs";

class SQSAdapter implements CloudMessageQueueAdapter {
  private client: SQSClient;

  constructor(region: string) {
    this.client = new SQSClient({ region });
  }

  async sendMessage(queueUrl: string, message: CloudMessage): Promise<string> {
    const command = new SendMessageCommand({
      QueueUrl: queueUrl,
      MessageBody: message.body,
      MessageAttributes: Object.entries(message.attributes).reduce((acc, [key, value]) => {
        acc[key] = { DataType: 'String', StringValue: value };
        return acc;
      }, {} as any)
    });

    const response = await this.client.send(command);
    return response.MessageId!;
  }

  async receiveMessages(queueUrl: string, maxMessages: number): Promise<CloudMessage[]> {
    const command = new ReceiveMessageCommand({
      QueueUrl: queueUrl,
      MaxNumberOfMessages: maxMessages,
      MessageAttributeNames: ['All']
    });

    const response = await this.client.send(command);

    return (response.Messages || []).map(msg => ({
      id: msg.MessageId!,
      body: msg.Body!,
      attributes: Object.entries(msg.MessageAttributes || {}).reduce((acc, [key, value]) => {
        acc[key] = value.StringValue!;
        return acc;
      }, {} as Record<string, string>),
      timestamp: new Date()
    }));
  }

  async deleteMessage(queueUrl: string, messageId: string): Promise<void> {
    const command = new DeleteMessageCommand({
      QueueUrl: queueUrl,
      ReceiptHandle: messageId
    });

    await this.client.send(command);
  }

  async getQueueUrl(queueName: string): Promise<string> {
    // Implementation for getting queue URL from name
    return `https://sqs.region.amazonaws.com/account-id/${queueName}`;
  }
}

// Azure Service Bus Adapter
import { ServiceBusClient, ServiceBusMessage } from "@azure/service-bus";

class AzureServiceBusAdapter implements CloudMessageQueueAdapter {
  private client: ServiceBusClient;

  constructor(connectionString: string) {
    this.client = new ServiceBusClient(connectionString);
  }

  async sendMessage(queueName: string, message: CloudMessage): Promise<string> {
    const sender = this.client.createSender(queueName);

    try {
      const sbMessage: ServiceBusMessage = {
        body: message.body,
        applicationProperties: message.attributes,
        messageId: message.id
      };

      await sender.sendMessages(sbMessage);
      return message.id;
    } finally {
      await sender.close();
    }
  }

  async receiveMessages(queueName: string, maxMessages: number): Promise<CloudMessage[]> {
    const receiver = this.client.createReceiver(queueName);

    try {
      const messages = await receiver.receiveMessages(maxMessages, { maxWaitTimeInMs: 5000 });

      return messages.map(msg => ({
        id: msg.messageId!,
        body: msg.body as string,
        attributes: msg.applicationProperties as Record<string, string>,
        timestamp: msg.enqueuedTimeUtc || new Date()
      }));
    } finally {
      await receiver.close();
    }
  }

  async deleteMessage(queueName: string, messageId: string): Promise<void> {
    const receiver = this.client.createReceiver(queueName);

    try {
      const messages = await receiver.receiveMessages(1);
      if (messages[0] && messages[0].messageId === messageId) {
        await receiver.completeMessage(messages[0]);
      }
    } finally {
      await receiver.close();
    }
  }

  async getQueueUrl(queueName: string): Promise<string> {
    return queueName; // Azure uses queue name directly
  }
}
```

### 2. Facade Pattern

Simplify complex multi-cloud operations behind a unified interface:

```go
// Go example for multi-cloud compute abstraction
package multicloud

import (
    "context"
    "time"
)

// ComputeFunction represents a serverless function
type ComputeFunction struct {
    Name        string
    Runtime     string
    Handler     string
    Timeout     time.Duration
    Memory      int
    Environment map[string]string
}

// InvocationRequest represents a function invocation
type InvocationRequest struct {
    FunctionName string
    Payload      []byte
    InvocationType string // "sync" or "async"
}

// InvocationResponse represents the result of a function invocation
type InvocationResponse struct {
    StatusCode int
    Payload    []byte
    LogResult  string
    ExecutionID string
}

// ComputeFacade provides unified interface for serverless compute
type ComputeFacade interface {
    CreateFunction(ctx context.Context, fn *ComputeFunction) error
    UpdateFunction(ctx context.Context, fn *ComputeFunction) error
    DeleteFunction(ctx context.Context, functionName string) error
    InvokeFunction(ctx context.Context, req *InvocationRequest) (*InvocationResponse, error)
    ListFunctions(ctx context.Context) ([]*ComputeFunction, error)
}

// MultiCloudComputeManager manages compute across multiple clouds
type MultiCloudComputeManager struct {
    primary   ComputeFacade
    secondary ComputeFacade
    failover  bool
}

func NewMultiCloudComputeManager(primary, secondary ComputeFacade, failover bool) *MultiCloudComputeManager {
    return &MultiCloudComputeManager{
        primary:   primary,
        secondary: secondary,
        failover:  failover,
    }
}

func (m *MultiCloudComputeManager) InvokeFunction(ctx context.Context, req *InvocationRequest) (*InvocationResponse, error) {
    resp, err := m.primary.InvokeFunction(ctx, req)

    if err != nil && m.failover && m.secondary != nil {
        // Failover to secondary cloud
        return m.secondary.InvokeFunction(ctx, req)
    }

    return resp, err
}
```

## Cloud-Agnostic API Design

### RESTful API Design Principles

```yaml
# OpenAPI 3.0 specification for cloud-agnostic API
openapi: 3.0.0
info:
  title: Multi-Cloud Data Processing API
  version: 1.0.0
  description: Cloud-agnostic API for data processing workflows

servers:
  - url: https://api.example.com/v1
    description: Production (Multi-cloud)
  - url: https://api-aws.example.com/v1
    description: AWS-specific endpoint
  - url: https://api-azure.example.com/v1
    description: Azure-specific endpoint

paths:
  /jobs:
    post:
      summary: Create a new data processing job
      operationId: createJob
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/JobRequest'
      responses:
        '201':
          description: Job created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Job'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /jobs/{jobId}:
    get:
      summary: Get job status and results
      operationId: getJob
      parameters:
        - name: jobId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Job details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Job'
        '404':
          description: Job not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    JobRequest:
      type: object
      required:
        - type
        - input
      properties:
        type:
          type: string
          enum: [batch, stream, realtime]
        input:
          type: object
          properties:
            source:
              type: string
              description: Cloud-agnostic URI (s3://, azure://, gs://)
            format:
              type: string
              enum: [json, csv, parquet, avro]
        parameters:
          type: object
          additionalProperties: true

    Job:
      type: object
      properties:
        id:
          type: string
          format: uuid
        status:
          type: string
          enum: [pending, running, completed, failed]
        type:
          type: string
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
        result:
          type: object
          properties:
            output:
              type: string
              description: Cloud-agnostic URI to output
            metrics:
              type: object

    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
        details:
          type: object
```

## Real-World Examples

### Netflix: Multi-Cloud Chaos Engineering

Netflix uses multi-cloud patterns to test resilience:

```python
# Simplified example inspired by Netflix's approach
class MultiCloudChaosService:
    """Service to test multi-cloud failover scenarios"""

    def __init__(self, storage_adapters: Dict[str, CloudStorageAdapter]):
        self.storage_adapters = storage_adapters
        self.primary = "aws"
        self.secondary = "gcp"

    async def store_with_replication(self, key: str, data: bytes) -> Dict[str, str]:
        """Store data across multiple cloud providers"""
        results = {}

        # Store in primary cloud
        try:
            primary_adapter = self.storage_adapters[self.primary]
            results[self.primary] = await primary_adapter.upload_object(
                bucket="primary-bucket",
                key=key,
                data=data
            )
        except Exception as e:
            results[self.primary] = f"Failed: {str(e)}"

        # Replicate to secondary cloud
        try:
            secondary_adapter = self.storage_adapters[self.secondary]
            results[self.secondary] = await secondary_adapter.upload_object(
                bucket="secondary-bucket",
                key=key,
                data=data
            )
        except Exception as e:
            results[self.secondary] = f"Failed: {str(e)}"

        return results

    async def retrieve_with_failover(self, key: str) -> bytes:
        """Retrieve data with automatic failover"""
        try:
            primary_adapter = self.storage_adapters[self.primary]
            return await primary_adapter.download_object("primary-bucket", key)
        except Exception as primary_error:
            # Failover to secondary
            try:
                secondary_adapter = self.storage_adapters[self.secondary]
                return await secondary_adapter.download_object("secondary-bucket", key)
            except Exception as secondary_error:
                raise Exception(f"All clouds failed: Primary={primary_error}, Secondary={secondary_error}")
```

### Stripe: Payment Processing Across Clouds

Stripe uses multi-cloud for global payment processing:

```javascript
// Multi-cloud payment processing abstraction
class PaymentProcessor {
  constructor(config) {
    this.regions = {
      'us-east': { cloud: 'aws', endpoint: 'https://api-us.stripe.com' },
      'eu-west': { cloud: 'azure', endpoint: 'https://api-eu.stripe.com' },
      'asia-pacific': { cloud: 'gcp', endpoint: 'https://api-ap.stripe.com' }
    };
  }

  async processPayment(paymentData, customerRegion) {
    const region = this.selectOptimalRegion(customerRegion);
    const endpoint = this.regions[region].endpoint;

    const response = await fetch(`${endpoint}/v1/payments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': paymentData.idempotencyKey,
        'X-Cloud-Region': region
      },
      body: JSON.stringify({
        amount: paymentData.amount,
        currency: paymentData.currency,
        source: paymentData.source,
        metadata: {
          cloudProvider: this.regions[region].cloud,
          processingRegion: region
        }
      })
    });

    return await response.json();
  }

  selectOptimalRegion(customerRegion) {
    // Intelligent region selection based on latency, cost, compliance
    const regionMap = {
      'NA': 'us-east',
      'EU': 'eu-west',
      'APAC': 'asia-pacific'
    };

    return regionMap[customerRegion] || 'us-east';
  }
}
```

## Security Considerations

### 1. Credential Management

```python
from abc import ABC, abstractmethod
import hvac  # HashiCorp Vault client

class SecretManager(ABC):
    """Abstract secret management across clouds"""

    @abstractmethod
    def get_secret(self, secret_name: str) -> dict:
        pass

    @abstractmethod
    def store_secret(self, secret_name: str, secret_value: dict) -> bool:
        pass

class VaultSecretManager(SecretManager):
    """Cloud-agnostic secret management using HashiCorp Vault"""

    def __init__(self, vault_url: str, token: str):
        self.client = hvac.Client(url=vault_url, token=token)

    def get_secret(self, secret_path: str) -> dict:
        """Retrieve secret from Vault"""
        response = self.client.secrets.kv.v2.read_secret_version(path=secret_path)
        return response['data']['data']

    def store_secret(self, secret_path: str, secret_value: dict) -> bool:
        """Store secret in Vault"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            secret=secret_value
        )
        return True

    def get_cloud_credentials(self, cloud_provider: str) -> dict:
        """Get credentials for specific cloud provider"""
        secret_paths = {
            'aws': 'cloud/aws/credentials',
            'azure': 'cloud/azure/credentials',
            'gcp': 'cloud/gcp/credentials'
        }

        return self.get_secret(secret_paths[cloud_provider])
```

### 2. Cross-Cloud Encryption

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class MultiCloudEncryption:
    """Encryption layer that works across all clouds"""

    def __init__(self, master_key: bytes):
        self.cipher = Fernet(master_key)

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data before storing in any cloud"""
        return self.cipher.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data retrieved from any cloud"""
        return self.cipher.decrypt(encrypted_data)

    @staticmethod
    def generate_key_from_password(password: str, salt: bytes) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
```

## Performance Optimization

### 1. Intelligent Request Routing

```python
import asyncio
from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class CloudEndpoint:
    provider: str
    region: str
    url: str
    latency: float = 0.0
    availability: float = 1.0

class MultiCloudRouter:
    """Route requests to optimal cloud endpoint"""

    def __init__(self, endpoints: List[CloudEndpoint]):
        self.endpoints = endpoints
        self.health_check_interval = 30  # seconds

    async def route_request(self, request_data: dict) -> tuple[CloudEndpoint, dict]:
        """Route request to best available endpoint"""
        best_endpoint = self._select_best_endpoint()

        try:
            response = await self._send_request(best_endpoint, request_data)
            return best_endpoint, response
        except Exception as e:
            # Try fallback endpoints
            for endpoint in self.endpoints:
                if endpoint != best_endpoint:
                    try:
                        response = await self._send_request(endpoint, request_data)
                        return endpoint, response
                    except:
                        continue

            raise Exception("All cloud endpoints failed")

    def _select_best_endpoint(self) -> CloudEndpoint:
        """Select endpoint based on latency and availability"""
        available_endpoints = [ep for ep in self.endpoints if ep.availability > 0.95]

        if not available_endpoints:
            available_endpoints = self.endpoints

        # Select endpoint with lowest latency
        return min(available_endpoints, key=lambda ep: ep.latency)

    async def _send_request(self, endpoint: CloudEndpoint, data: dict) -> dict:
        """Send request to specific endpoint"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint.url, json=data) as response:
                return await response.json()

    async def monitor_endpoints(self):
        """Continuously monitor endpoint health"""
        while True:
            for endpoint in self.endpoints:
                start_time = time.time()
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{endpoint.url}/health") as response:
                            if response.status == 200:
                                endpoint.latency = time.time() - start_time
                                endpoint.availability = 1.0
                            else:
                                endpoint.availability = 0.5
                except:
                    endpoint.availability = 0.0

            await asyncio.sleep(self.health_check_interval)
```

## Best Practices

### 1. Use Infrastructure as Code

```hcl
# Terraform example for multi-cloud deployment
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# AWS Resources
provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "${var.app_name}-data-aws"

  tags = {
    Environment = var.environment
    Cloud       = "aws"
  }
}

# Azure Resources
provider "azurerm" {
  features {}
}

resource "azurerm_storage_account" "data_storage" {
  name                     = "${var.app_name}dataazure"
  resource_group_name      = var.azure_resource_group
  location                 = var.azure_location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    Environment = var.environment
    Cloud       = "azure"
  }
}

# GCP Resources
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

resource "google_storage_bucket" "data_bucket" {
  name     = "${var.app_name}-data-gcp"
  location = var.gcp_region

  labels = {
    environment = var.environment
    cloud       = "gcp"
  }
}
```

### 2. Implement Observability

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class MultiCloudObservability:
    """Unified observability across clouds"""

    def __init__(self):
        # Initialize OpenTelemetry (works with all clouds)
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()

        # Export to cloud-agnostic backend (e.g., Jaeger, Datadog)
        otlp_exporter = OTLPSpanExporter(endpoint="http://collector:4317")
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)

        self.tracer = trace.get_tracer(__name__)

    def trace_cloud_operation(self, operation_name: str, cloud_provider: str):
        """Create trace span for cloud operation"""
        return self.tracer.start_as_current_span(
            operation_name,
            attributes={
                "cloud.provider": cloud_provider,
                "service.name": "multi-cloud-api"
            }
        )
```

### 3. Design for Eventual Consistency

```python
import hashlib
from datetime import datetime, timedelta

class MultiCloudConsistencyManager:
    """Manage eventual consistency across clouds"""

    def __init__(self, storage_adapters: Dict[str, CloudStorageAdapter]):
        self.storage_adapters = storage_adapters

    async def write_with_consistency_check(self, key: str, data: bytes,
                                          clouds: List[str]) -> bool:
        """Write to multiple clouds and verify consistency"""
        data_hash = hashlib.sha256(data).hexdigest()
        metadata = {
            'hash': data_hash,
            'timestamp': datetime.utcnow().isoformat(),
            'size': len(data)
        }

        # Write to all specified clouds
        write_results = {}
        for cloud in clouds:
            try:
                adapter = self.storage_adapters[cloud]
                result = await adapter.upload_object(f"{cloud}-bucket", key, data)
                write_results[cloud] = True
            except Exception as e:
                write_results[cloud] = False

        # Verify writes succeeded in majority of clouds
        successful_writes = sum(1 for success in write_results.values() if success)
        return successful_writes >= (len(clouds) / 2)

    async def verify_consistency(self, key: str, clouds: List[str]) -> bool:
        """Verify data is consistent across clouds"""
        hashes = {}

        for cloud in clouds:
            try:
                adapter = self.storage_adapters[cloud]
                data = await adapter.download_object(f"{cloud}-bucket", key)
                hashes[cloud] = hashlib.sha256(data).hexdigest()
            except Exception as e:
                hashes[cloud] = None

        # Check if all hashes are identical
        valid_hashes = [h for h in hashes.values() if h is not None]
        return len(set(valid_hashes)) == 1 if valid_hashes else False
```

## Conclusion

Multi-cloud API patterns enable organizations to build resilient, flexible applications that leverage the best of each cloud provider while minimizing vendor lock-in. Key takeaways:

1. **Abstraction is essential**: Use adapter and facade patterns to hide cloud-specific details
2. **Configuration over code**: Make cloud selection configurable, not hardcoded
3. **Security first**: Use cloud-agnostic secret management and encryption
4. **Monitor everything**: Implement comprehensive observability across all clouds
5. **Design for failure**: Assume individual cloud services will fail and build resilience
6. **Optimize intelligently**: Route requests based on latency, cost, and availability

By following these patterns, you can build truly cloud-agnostic APIs that provide flexibility and resilience in an increasingly multi-cloud world.
