# Azure Storage Account Types Reference

## Storage Account Kinds

### Standard General-Purpose v2 (GPv2)
**Use Case**: Most scenarios - blobs, files, queues, tables
**Supported Services**: Blob (all types), File, Queue, Table
**Performance Tier**: Standard (HDD-backed)
**Redundancy Options**: LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS
**Access Tiers**: Hot, Cool, Archive (blob only)
**Cost**: Most flexible pricing, recommended for most scenarios

**When to Use**:
- General-purpose storage needs
- Need for file, queue, or table storage
- Cost-effective blob storage with tiering
- Most common choice for new applications

**Pricing Example (US East)**:
- Storage: $0.0184/GB (Hot), $0.01/GB (Cool), $0.002/GB (Archive)
- Operations: $0.004 per 10,000 writes (Hot)
- Data retrieval: Free (Hot), $0.01/GB (Cool), $0.02/GB (Archive)

### Premium Block Blob
**Use Case**: High transaction rates, low latency blob storage
**Supported Services**: Block blobs and append blobs only
**Performance Tier**: Premium (SSD-backed)
**Redundancy Options**: LRS, ZRS only
**Access Tiers**: Not supported (single performance tier)
**Cost**: Higher storage cost, lower transaction cost

**When to Use**:
- Consistent low-latency requirements (single-digit milliseconds)
- High transaction rate applications
- IoT telemetry, streaming, gaming
- Interactive workloads
- AI/ML training data with frequent access

**Pricing Example (US East)**:
- Storage: $0.15/GB per month
- Operations: $0.0013 per 10,000 reads, $0.065 per 10,000 writes
- No data retrieval charges

**Performance**:
- Target latency: < 10ms (95th percentile)
- Max IOPS per blob: 100,000
- Max throughput per blob: 1.2 GB/s

### Premium File Share
**Use Case**: High-performance SMB file shares
**Supported Services**: Azure Files only
**Performance Tier**: Premium (SSD-backed)
**Redundancy Options**: LRS, ZRS only
**Provisioned Model**: Pay for provisioned capacity (not used capacity)
**Cost**: Based on provisioned size, includes IOPS and throughput

**When to Use**:
- IO-intensive workloads (databases, dev environments)
- Consistent performance requirements
- Applications requiring SMB 3.0 protocol
- Lift-and-shift scenarios with on-premises file servers

**Pricing Example (US East)**:
- $0.20/GB provisioned per month
- Includes baseline IOPS: 1 IOPS per GB (min 100)
- Includes baseline throughput: 0.04 MB/s per GB
- Bursting: Up to 4,000 IOPS or 100 MB/s per 100 GB

**Performance**:
- Max IOPS per share: 100,000
- Max throughput per share: 10 GB/s
- Max size per share: 100 TB

### Premium Page Blob
**Use Case**: High-performance VHD storage for VMs
**Supported Services**: Page blobs only (VM disks)
**Performance Tier**: Premium (SSD-backed)
**Redundancy Options**: LRS only
**Access Tiers**: Not supported
**Cost**: Based on disk size and type

**When to Use**:
- VM OS and data disks requiring premium performance
- Database workloads on VMs
- Generally replaced by Premium Managed Disks

**Note**: For new deployments, use **Managed Disks** instead of page blobs in storage accounts.

### Blob Storage (Legacy)
**Status**: Being phased out, use GPv2 instead
**Supported Services**: Block blobs and append blobs only
**Note**: Cannot be upgraded to support all services; convert to GPv2

## Blob Access Tiers

### Hot Tier
**Optimized For**: Frequently accessed data
**Storage Cost**: Highest
**Access Cost**: Lowest
**Minimum Storage Duration**: None

**Use Cases**:
- Active website images and videos
- Data for processing and analytics
- Application data in active use
- Staging area for data

**Pricing Example**:
- Storage: $0.0184/GB
- Read operations: $0.0004 per 10,000
- Write operations: $0.05 per 10,000

### Cool Tier
**Optimized For**: Infrequently accessed data, stored at least 30 days
**Storage Cost**: Lower than Hot
**Access Cost**: Higher than Hot
**Minimum Storage Duration**: 30 days

**Use Cases**:
- Short-term backup and disaster recovery
- Older media content not viewed frequently
- Large data sets for future processing
- Compliance and archival data needing quick access

**Pricing Example**:
- Storage: $0.01/GB
- Read operations: $0.001 per 10,000
- Write operations: $0.10 per 10,000
- Data retrieval: $0.01/GB
- Early deletion fee if < 30 days

### Archive Tier
**Optimized For**: Rarely accessed data, stored at least 180 days
**Storage Cost**: Lowest
**Access Cost**: Highest
**Minimum Storage Duration**: 180 days
**Rehydration Required**: Must rehydrate to Hot/Cool before access

**Use Cases**:
- Long-term backup retention
- Compliance and regulatory data
- Original raw data after processing
- Historical data for analytics

**Pricing Example**:
- Storage: $0.002/GB
- Write operations: $0.10 per 10,000
- Data retrieval: $0.02/GB
- Rehydration from Archive: $0.03/GB (standard), $0.13/GB (high priority)
- Early deletion fee if < 180 days

**Rehydration Time**:
- Standard priority: Up to 15 hours
- High priority: < 1 hour (for blobs < 10 GB)

## Redundancy Options

### Locally Redundant Storage (LRS)
**Replication**: 3 copies within single datacenter
**Durability**: 99.999999999% (11 nines)
**Availability SLA**: 99.9% (read), 99.9% (write)
**Cost**: Lowest
**Use Case**: Non-critical data, data that can be reconstructed

**Protection Against**:
- Server rack and drive failures

**Vulnerable To**:
- Datacenter-level disasters

**Pricing Multiplier**: 1x (baseline)

### Zone-Redundant Storage (ZRS)
**Replication**: 3 copies across 3 availability zones in primary region
**Durability**: 99.9999999999% (12 nines)
**Availability SLA**: 99.9% (read), 99.9% (write)
**Cost**: ~1.25x LRS
**Use Case**: High availability within region, resilience to zone failures

**Protection Against**:
- Datacenter-level failures in a region

**Vulnerable To**:
- Region-level disasters

**Availability**: Not available in all regions

### Geo-Redundant Storage (GRS)
**Replication**: LRS in primary + LRS in secondary region (paired region)
**Durability**: 99.99999999999999% (16 nines)
**Availability SLA**: 99.9% (read), 99.9% (write)
**Cost**: ~2x LRS
**Failover**: Manual or Microsoft-managed (regional disaster)

**Protection Against**:
- Region-level disasters

**Note**: Secondary region data is not readable until failover (use RA-GRS for read access)

### Read-Access Geo-Redundant Storage (RA-GRS)
**Replication**: Same as GRS
**Durability**: 99.99999999999999% (16 nines)
**Availability SLA**: 99.99% (read), 99.9% (write)
**Cost**: ~2x LRS
**Read Access**: Can read from secondary region anytime

**Use Case**: High availability reads even during regional outage

**Secondary Endpoint**: `https://<account>-secondary.blob.core.windows.net`

### Geo-Zone-Redundant Storage (GZRS)
**Replication**: ZRS in primary + LRS in secondary region
**Durability**: 99.99999999999999% (16 nines)
**Availability SLA**: 99.9% (read), 99.9% (write)
**Cost**: ~2.5x LRS
**Use Case**: Maximum durability and availability

**Protection Against**:
- Datacenter failures in primary region
- Region-level disasters

### Read-Access Geo-Zone-Redundant Storage (RA-GZRS)
**Replication**: Same as GZRS
**Durability**: 99.99999999999999% (16 nines)
**Availability SLA**: 99.99% (read), 99.9% (write)
**Cost**: ~2.5x LRS
**Read Access**: Can read from secondary region anytime

**Use Case**: Maximum availability and durability for critical data

## Performance Tiers Comparison

| Feature | Standard (GPv2) | Premium Block Blob | Premium File Share | Premium Page Blob |
|---------|----------------|-------------------|-------------------|------------------|
| Storage Type | HDD | SSD | SSD | SSD |
| Latency | 10-50ms | <10ms | <10ms | <10ms |
| IOPS per account | 20,000 | 100,000+ | 100,000+ | N/A |
| Throughput | Up to 60 GB/s | Up to 100 GB/s | Up to 100 GB/s | N/A |
| Access Tiers | Yes | No | No | No |
| Redundancy | LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS | LRS, ZRS | LRS, ZRS | LRS |
| Use Case | General purpose | High performance blobs | High performance files | VM disks (legacy) |

## Blob Types

### Block Blob
**Use Case**: Text and binary data (documents, images, videos)
**Max Size**: 190.7 TB (4.75 TB prior to 2019-12-12 API)
**Optimized For**: Uploading large amounts of data efficiently
**Upload Method**: Blocks uploaded in parallel, then committed

**Features**:
- Supports all access tiers (Hot, Cool, Archive)
- Can upload blocks in any order
- Best for streaming and cloud storage

**Cost**: Based on storage tier

### Append Blob
**Use Case**: Logging, audit data, data streams
**Max Size**: 195 GB
**Optimized For**: Append operations
**Constraint**: Only append operations allowed, no random writes

**Features**:
- Optimized for append scenarios
- Supports Hot and Cool tiers
- Ideal for log files

**Cost**: Same as block blobs

### Page Blob
**Use Case**: Virtual hard drives (VHDs), random read/write
**Max Size**: 8 TB
**Optimized For**: Random read/write operations
**Use Case**: VM disks, databases

**Features**:
- 512-byte page aligned
- Efficient random I/O
- Primarily for IaaS disks

**Cost**: Based on provisioned size, not used space

## Lifecycle Management

Automate blob tier transitions and deletions:

```json
{
  "rules": [
    {
      "name": "moveToArchive",
      "enabled": true,
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["logs/"]
        },
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            },
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 90
            },
            "delete": {
              "daysAfterModificationGreaterThan": 365
            }
          }
        }
      }
    }
  ]
}
```

## Cost Optimization Strategies

### Right-Size Access Tiers
- **Active data**: Hot tier
- **Backup/DR (< 30 days)**: Hot tier
- **Backup/DR (> 30 days)**: Cool tier
- **Long-term archive (> 180 days)**: Archive tier

### Use Lifecycle Policies
- Automatically transition data between tiers
- Delete old data automatically
- Reduce manual management

### Choose Appropriate Redundancy
- **Non-critical, reconstructable**: LRS
- **Production, single-region**: ZRS
- **Critical, must survive region failure**: GRS or GZRS
- **Critical + read during outage**: RA-GRS or RA-GZRS

### Reserved Capacity
- 1-year or 3-year commitment
- Up to 38% discount on storage capacity
- Available for Blob and Data Lake Storage

## Storage Account Limits

### Standard GPv2 Account
- Max capacity: 5 PB (US), 500 TB (other regions, can be increased)
- Max request rate: 20,000 IOPS
- Max ingress: 25 Gbps (RA-GRS/GRS), 50 Gbps (LRS/ZRS)
- Max egress: 50 Gbps (RA-GRS/GRS), 100 Gbps (LRS/ZRS)

### Premium Block Blob Account
- Max capacity: 4 PB
- Max request rate: 100,000+ IOPS
- Max throughput: 80 Gbps egress

### Blob Size Limits
- Block blob: 190.7 TB (5,000 blocks × 4,000 MB per block)
- Append blob: 195 GB
- Page blob: 8 TB

### Single Blob Performance
| Account Type | Max Throughput | Max IOPS |
|--------------|----------------|----------|
| Standard GPv2 | 500 MB/s | N/A |
| Premium Block Blob | 1.2 GB/s | 100,000 |

## Security Features

### Encryption
- **At Rest**: 256-bit AES encryption (always on)
- **In Transit**: HTTPS/TLS required (can enforce)
- **Customer-Managed Keys**: Use Azure Key Vault keys

### Network Security
- **Firewall**: Allow specific IP ranges or VNets
- **Private Endpoints**: Access via private IP in VNet
- **Service Endpoints**: Secure VNet access

### Access Control
- **Shared Key**: Account key access (full permissions)
- **Shared Access Signature (SAS)**: Limited-time, scoped access
- **Azure AD Integration**: Identity-based access control
- **Stored Access Policies**: Revocable SAS tokens

### Advanced Threat Protection
- Detects anomalous access patterns
- Malware hash reputation analysis
- Alerts on suspicious activities

## Decision Matrix

| Requirement | Recommendation |
|-------------|----------------|
| General blob storage, cost-effective | Standard GPv2, Hot tier |
| Infrequently accessed data | Standard GPv2, Cool tier |
| Long-term retention, rarely accessed | Standard GPv2, Archive tier |
| Low latency, high IOPS for blobs | Premium Block Blob |
| File shares for lift-and-shift | Premium File Share |
| VM disks | Premium Managed Disks (not storage account) |
| Zone redundancy needed | ZRS, GZRS, or RA-GZRS |
| Region redundancy needed | GRS, GZRS, RA-GRS, or RA-GZRS |
| Read from secondary during outage | RA-GRS or RA-GZRS |
| Maximum cost efficiency | Standard GPv2, LRS, appropriate tier |

## Migration Paths

### Upgrade Blob Storage to GPv2
- No downtime
- One-way operation (cannot downgrade)
- Command: `az storage account update --name <name> --set kind=StorageV2`

### GPv1 to GPv2
- No downtime
- One-way operation
- Recommended for all GPv1 accounts

### Change Redundancy
- LRS ↔ GRS: Supported, may take up to 72 hours
- LRS → ZRS: Manual migration required (copy data)
- GRS → GZRS: Supported in most regions

### Change Access Tier
- Account-level default tier can be changed
- Individual blobs can be moved between tiers
- Lifecycle policies can automate transitions

## Quick Reference Commands

```bash
# Create storage account
az storage account create \
  --name mystorageaccount \
  --resource-group myRG \
  --location eastus \
  --sku Standard_GRS \
  --kind StorageV2 \
  --access-tier Hot

# Change redundancy
az storage account update \
  --name mystorageaccount \
  --resource-group myRG \
  --sku Standard_ZRS

# Set blob tier
az storage blob set-tier \
  --account-name mystorageaccount \
  --container-name mycontainer \
  --name myblob \
  --tier Cool

# Enable lifecycle management
az storage account management-policy create \
  --account-name mystorageaccount \
  --policy @policy.json \
  --resource-group myRG
```
