# Cloud Storage Classes and Configuration Reference

## Storage Class Overview

Google Cloud Storage offers multiple storage classes optimized for different access patterns and cost requirements. All classes provide the same durability, security features, and APIs.

### Storage Class Comparison

| Feature | Standard | Nearline | Coldline | Archive |
|---------|----------|----------|----------|---------|
| **Access Frequency** | Hot data | < 1/month | < 1/quarter | < 1/year |
| **Minimum Storage Duration** | None | 30 days | 90 days | 365 days |
| **Retrieval Cost** | None | $0.01/GB | $0.02/GB | $0.05/GB |
| **Storage Cost (US Multi-Region)** | $0.020/GB/month | $0.010/GB/month | $0.004/GB/month | $0.0012/GB/month |
| **Use Cases** | Frequently accessed data | Monthly backups, analytics | Quarterly archives, DR | Long-term archives, compliance |
| **Durability** | 99.999999999% (11 9's) | 99.999999999% (11 9's) | 99.999999999% (11 9's) | 99.999999999% (11 9's) |
| **Availability SLA** | 99.95% (multi-region), 99.9% (region) | 99.9% (multi-region), 99.0% (region) | 99.9% (multi-region), 99.0% (region) | 99.9% (multi-region), 99.0% (region) |

## Standard Storage

### Characteristics
- **Best For**: Hot data, frequently accessed content
- **Pricing**: Higher storage cost, no retrieval fees
- **No Minimum Duration**: Delete anytime without penalty
- **Performance**: Highest throughput and lowest latency

### Use Cases
- **Website Content**: Images, videos, CSS, JavaScript
- **Mobile/Gaming Content**: Assets, user-generated content
- **Data Analytics**: Active datasets, real-time processing
- **Streaming**: Video/audio streaming content
- **Transcoding**: Video processing pipelines

### Pricing (US Multi-Region)
```
Storage:         $0.020 per GB per month
Class A Ops:     $0.05 per 10,000 operations
Class B Ops:     $0.004 per 10,000 operations
Retrieval:       $0 (no cost)
Early Deletion:  None
```

### Configuration Example
```bash
# Create bucket with Standard storage
gsutil mb -c STANDARD -l US gs://my-standard-bucket

# Upload object as Standard class
gsutil cp file.txt gs://my-bucket/
```

## Nearline Storage

### Characteristics
- **Best For**: Infrequently accessed data (< once per month)
- **Minimum Duration**: 30 days
- **Retrieval Fee**: $0.01 per GB
- **Early Deletion Fee**: Charged for remaining days of 30-day minimum

### Use Cases
- **Data Backup**: Monthly backup retention
- **Long-Tail Content**: Rarely accessed media files
- **Data Analytics**: Cold datasets for periodic analysis
- **Disaster Recovery**: Secondary backup location

### Pricing (US Multi-Region)
```
Storage:         $0.010 per GB per month
Class A Ops:     $0.10 per 10,000 operations
Class B Ops:     $0.01 per 10,000 operations
Retrieval:       $0.01 per GB
Early Deletion:  Charged for remaining days (30-day minimum)
```

### Configuration Example
```bash
# Create Nearline bucket
gsutil mb -c NEARLINE -l US gs://my-nearline-bucket

# Set object storage class
gsutil -h "x-goog-storage-class:NEARLINE" cp file.txt gs://my-bucket/

# Change existing object to Nearline
gsutil rewrite -s NEARLINE gs://my-bucket/file.txt
```

### Early Deletion Calculation
If an object is deleted after 15 days:
- Charged for remaining 15 days at Nearline storage rate
- Example: 100 GB object → 100 GB × $0.010/GB × (15/30) = $5.00

## Coldline Storage

### Characteristics
- **Best For**: Infrequently accessed data (< once per 90 days)
- **Minimum Duration**: 90 days
- **Retrieval Fee**: $0.02 per GB
- **Lower Storage Cost**: ~80% cheaper than Standard

### Use Cases
- **Disaster Recovery**: DR backups, tested quarterly
- **Compliance Archives**: Regulatory data retention
- **Cold Analytics**: Historical data for occasional analysis
- **Long-Term Backups**: Quarterly/annual backup retention

### Pricing (US Multi-Region)
```
Storage:         $0.004 per GB per month
Class A Ops:     $0.10 per 10,000 operations
Class B Ops:     $0.01 per 10,000 operations
Retrieval:       $0.02 per GB
Early Deletion:  Charged for remaining days (90-day minimum)
```

### Configuration Example
```bash
# Create Coldline bucket
gsutil mb -c COLDLINE -l US gs://my-coldline-bucket

# Upload to Coldline
gsutil -h "x-goog-storage-class:COLDLINE" cp archive.zip gs://my-bucket/
```

### When to Use Coldline vs Nearline
- **Coldline**: Access every 90+ days, lower cost priority
- **Nearline**: Access monthly, balance of cost and accessibility

## Archive Storage

### Characteristics
- **Best For**: Long-term archival (< once per year)
- **Minimum Duration**: 365 days
- **Retrieval Fee**: $0.05 per GB
- **Lowest Cost**: ~94% cheaper than Standard

### Use Cases
- **Regulatory Compliance**: Legal/financial record retention (7+ years)
- **Long-Term Archives**: Historical data rarely accessed
- **Backup Archives**: Final backup tier for aged data
- **Cold Storage Migration**: Replace tape-based archives

### Pricing (US Multi-Region)
```
Storage:         $0.0012 per GB per month
Class A Ops:     $0.50 per 10,000 operations
Class B Ops:     $0.50 per 10,000 operations
Retrieval:       $0.05 per GB
Early Deletion:  Charged for remaining days (365-day minimum)
```

### Configuration Example
```bash
# Create Archive bucket
gsutil mb -c ARCHIVE -l US gs://my-archive-bucket

# Upload to Archive
gsutil -h "x-goog-storage-class:ARCHIVE" cp old-records.tar.gz gs://my-bucket/

# Autoclass for automatic transition
gsutil autoclass set on gs://my-bucket/
```

### Archive Retrieval
- **Latency**: Milliseconds (same as other classes)
- **Cost**: $0.05 per GB retrieved
- **No Restore Required**: Unlike AWS Glacier, no restore/thaw needed
- **Immediate Access**: Data available instantly

## Location Types

### Multi-Region
- **Locations**: US, EU, ASIA
- **Redundancy**: Geo-redundant across 100+ miles
- **Availability**: 99.95% SLA (Standard)
- **Use Cases**: Global content delivery, disaster recovery

**Multi-Region Locations**:
```
US:   Iowa, South Carolina, Oregon, N. Virginia, Texas, California
EU:   Belgium, Netherlands, Finland, Germany, UK, Switzerland
ASIA: Tokyo, Osaka, Seoul, Taiwan, Singapore, Mumbai, Delhi
```

### Dual-Region
- **Locations**: Paired regions (e.g., US-EAST1 + US-CENTRAL1)
- **Redundancy**: Data replicated across two specific regions
- **Availability**: 99.95% SLA
- **Use Cases**: Compliance requirements, specific geo-redundancy

**Available Dual-Regions**:
```
NAM4: us-central1 + us-east1
EUR4: europe-north1 + europe-west4
ASIA1: asia-northeast1 + asia-northeast2
```

### Single Region
- **Redundancy**: Redundant within single region (multi-zone)
- **Availability**: 99.9% SLA
- **Lower Cost**: ~20% cheaper than multi-region
- **Use Cases**: Regional applications, data residency requirements

**Example Regions**:
```
us-central1 (Iowa)
us-east1 (South Carolina)
europe-west1 (Belgium)
asia-east1 (Taiwan)
australia-southeast1 (Sydney)
```

## Bucket Configuration

### Creating Buckets

**Multi-Region Bucket**:
```bash
gsutil mb -c STANDARD -l US gs://my-multi-region-bucket
```

**Dual-Region Bucket**:
```bash
gsutil mb -c STANDARD -l NAM4 gs://my-dual-region-bucket
```

**Regional Bucket**:
```bash
gsutil mb -c STANDARD -l us-central1 gs://my-regional-bucket
```

**With Storage Class**:
```bash
# Nearline in EU multi-region
gsutil mb -c NEARLINE -l EU gs://my-eu-nearline-bucket

# Archive in specific region
gsutil mb -c ARCHIVE -l us-east1 gs://my-archive-bucket
```

### Bucket Attributes
Once set, these **cannot be changed**:
- Location (region/multi-region)
- Project

Can be changed:
- Default storage class
- Labels
- Lifecycle rules
- IAM policies
- CORS configuration

## Object Lifecycle Management

### Lifecycle Rules
Automatically transition or delete objects based on conditions.

**Rule Conditions**:
- **Age**: Days since upload
- **CreatedBefore**: Specific date
- **IsLive**: Current/noncurrent versions
- **MatchesStorageClass**: Current storage class
- **NumberOfNewerVersions**: Version count
- **DaysSinceCustomTime**: Days since custom metadata timestamp
- **DaysSinceNoncurrentTime**: Days since becoming noncurrent

**Actions**:
- **SetStorageClass**: Transition to different class
- **Delete**: Delete object

### Lifecycle Configuration Examples

**Transition to Colder Classes**:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
        "condition": {"age": 365, "matchesStorageClass": ["COLDLINE"]}
      }
    ]
  }
}
```

**Delete Old Objects**:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

**Apply Lifecycle**:
```bash
gsutil lifecycle set lifecycle.json gs://my-bucket
```

**View Current Lifecycle**:
```bash
gsutil lifecycle get gs://my-bucket
```

## Autoclass

### Overview
Automatically transitions objects between storage classes based on access patterns.

### How It Works
- **Monitoring**: Tracks object access patterns
- **Transitions**: Moves to colder classes after 30/90 days without access
- **Restoration**: Moves back to Standard when accessed
- **Cost**: $0.0025 per 1,000 objects per month

### Enable Autoclass
```bash
# Enable Autoclass
gsutil autoclass set on gs://my-bucket

# Disable Autoclass
gsutil autoclass set off gs://my-bucket

# Check status
gsutil autoclass get gs://my-bucket
```

### Autoclass Transition Logic
```
Standard → (30 days no access) → Nearline
Nearline → (60 days no access) → Coldline
Coldline → (275 days no access) → Archive

On access → Standard
```

### When to Use Autoclass
- **Variable Access Patterns**: Unpredictable data access
- **Simplification**: Avoid manual lifecycle rules
- **Cost Optimization**: Automatic cost reduction

### When NOT to Use Autoclass
- **Known Access Patterns**: Use lifecycle rules instead
- **Archive-First**: Objects that should go directly to Archive
- **Fine-Grained Control**: Need specific transition timing

## Object Versioning

### Enable Versioning
```bash
gsutil versioning set on gs://my-bucket
```

### Versioning with Storage Classes
- **Live Version**: Default bucket storage class
- **Noncurrent Versions**: Can have different storage classes
- **Lifecycle**: Archive or delete old versions

**Example - Archive Old Versions**:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {
          "isLive": false,
          "daysSinceNoncurrentTime": 30
        }
      },
      {
        "action": {"type": "Delete"},
        "condition": {
          "isLive": false,
          "daysSinceNoncurrentTime": 90
        }
      }
    ]
  }
}
```

## Retention Policies

### Bucket Lock
Prevent deletion for compliance (WORM - Write Once Read Many).

**Set Retention Policy**:
```bash
# 7-year retention
gsutil retention set 7y gs://my-bucket

# Lock policy (irreversible!)
gsutil retention lock gs://my-bucket
```

### Event-Based Holds
Hold objects until specific event (e.g., legal case closure).

### Temporary Holds
Manual holds for specific objects.

## Cost Optimization Strategies

### 1. Use Appropriate Storage Classes
```
Frequent Access (daily):     Standard
Monthly Access:              Nearline
Quarterly Access:            Coldline
Yearly/Archival:            Archive
```

### 2. Implement Lifecycle Policies
Automate transitions to reduce costs:
```
0-30 days:     Standard  ($0.020/GB/month)
31-90 days:    Nearline  ($0.010/GB/month)
91-365 days:   Coldline  ($0.004/GB/month)
365+ days:     Archive   ($0.0012/GB/month)
```

### 3. Use Regional Buckets
If global redundancy not required:
```
Multi-Region:  $0.020/GB/month (Standard)
Regional:      $0.020/GB/month (Standard, us-central1)
Savings: Use region for lower retrieval costs
```

### 4. Optimize Operations
- Reduce Class A operations (writes)
- Batch operations
- Use composite uploads for large files

### 5. Monitor Access Patterns
Use Cloud Storage Analytics:
```bash
# Enable storage analytics
gsutil ubla set on gs://my-bucket
```

### 6. Consider Dual-Region vs Multi-Region
- Dual-region: Same cost, specific region control
- Multi-region: Broader geographic distribution

## Performance Considerations

### Request Rate Limits
- **Initial**: 1,000 writes/sec, 5,000 reads/sec per bucket
- **Auto-Scaling**: Scales to higher rates
- **Best Practice**: Ramp up gradually

### Bandwidth
- **Egress**: Charged for data leaving GCP
- **Free Tiers**:
  - Same region: Free
  - Different region (same multi-region): Free
  - Internet: $0.08-0.12/GB (varies by region)

### Latency
- **All Classes**: Millisecond latency (no difference)
- **Global**: Use multi-region for global users
- **Regional**: Lower latency for nearby users

## Security and Access Control

### IAM
```bash
# Grant read access
gsutil iam ch user:user@example.com:objectViewer gs://my-bucket

# Grant write access
gsutil iam ch serviceAccount:sa@project.iam.gserviceaccount.com:objectCreator gs://my-bucket
```

### Signed URLs
Temporary access without authentication:
```bash
gsutil signurl -d 10m private-key.json gs://my-bucket/file.txt
```

### Uniform Bucket-Level Access
Disable ACLs, use only IAM:
```bash
gsutil uniformbucketlevelaccess set on gs://my-bucket
```

## Best Practices Summary

1. **Match Storage Class to Access Pattern**: Choose class based on actual usage
2. **Implement Lifecycle Rules**: Automate transitions and deletions
3. **Use Autoclass for Unpredictable Access**: Let GCP optimize automatically
4. **Monitor Costs**: Use Cloud Storage Analytics and cost reports
5. **Regional vs Multi-Regional**: Balance cost vs availability requirements
6. **Enable Versioning Wisely**: Lifecycle old versions to cheaper classes
7. **Test Retrieval**: Verify DR procedures work as expected
8. **Calculate TCO**: Include storage, operations, retrieval, and egress
9. **Use Labels**: Tag buckets/objects for cost allocation
10. **Review Regularly**: Quarterly review of access patterns and costs
