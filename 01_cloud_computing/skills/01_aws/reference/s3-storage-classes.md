# S3 Storage Classes Reference

## Overview of S3 Storage Classes

Amazon S3 offers multiple storage classes designed for different use cases based on access frequency, performance requirements, and cost optimization needs.

## Storage Class Comparison Matrix

| Storage Class | Durability | Availability | AZs | Min Storage | Retrieval Fee | Use Case |
|--------------|-----------|--------------|-----|-------------|--------------|----------|
| S3 Standard | 99.999999999% | 99.99% | ≥3 | None | No | Frequently accessed |
| S3 Intelligent-Tiering | 99.999999999% | 99.9% | ≥3 | None | No* | Unknown/changing patterns |
| S3 Standard-IA | 99.999999999% | 99.9% | ≥3 | 30 days | Yes | Infrequent access |
| S3 One Zone-IA | 99.999999999%** | 99.5% | 1 | 30 days | Yes | Non-critical, infrequent |
| S3 Glacier Instant Retrieval | 99.999999999% | 99.9% | ≥3 | 90 days | Yes | Archive, instant access |
| S3 Glacier Flexible Retrieval | 99.999999999% | 99.99% | ≥3 | 90 days | Yes | Archive, min-hours retrieval |
| S3 Glacier Deep Archive | 99.999999999% | 99.99% | ≥3 | 180 days | Yes | Long-term archive |
| S3 Reduced Redundancy (RRS) | 99.99% | 99.99% | ≥3 | None | No | **DEPRECATED** |

*S3 Intelligent-Tiering has monitoring and automation fees but no retrieval fees
**Only if the AZ is not lost

## S3 Standard

### Characteristics
- **Durability**: 11 nines (99.999999999%) annual durability
- **Availability**: 99.99% availability SLA
- **Availability Zones**: Stored across minimum of 3 AZs
- **Performance**: Millisecond latency, high throughput
- **Lifecycle**: No minimum storage duration

### Pricing (US East - Ohio, approximate)
- **Storage**: $0.023 per GB/month (first 50 TB)
- **PUT/COPY/POST/LIST**: $0.005 per 1,000 requests
- **GET/SELECT**: $0.0004 per 1,000 requests
- **Data Transfer Out**: $0.09 per GB (first 10 TB)

### Use Cases
- Dynamic websites and web applications
- Content distribution
- Mobile and gaming applications
- Big data analytics
- Frequently accessed data

### Best Practices
- Default choice for unknown access patterns initially
- Use lifecycle policies to transition to IA after 30+ days
- Monitor access patterns with S3 Storage Class Analysis
- Enable versioning for data protection

## S3 Intelligent-Tiering

### Characteristics
- **Automatic Cost Optimization**: Moves objects between tiers based on access
- **No Retrieval Fees**: Unlike IA classes
- **No Operational Overhead**: Fully automated
- **Performance**: Same as S3 Standard for frequently accessed data
- **Monitoring Fee**: $0.0025 per 1,000 objects

### Access Tiers
1. **Frequent Access** (automatic): Default tier, millisecond latency
2. **Infrequent Access** (automatic): Not accessed for 30 days, lower storage cost
3. **Archive Instant Access** (automatic): Not accessed for 90 days
4. **Archive Access** (optional): Not accessed for 90-730 days, 3-5 hour retrieval
5. **Deep Archive Access** (optional): Not accessed for 180-730 days, 12-48 hour retrieval

### Pricing (US East - Ohio)
- **Frequent Access Tier**: $0.023 per GB/month
- **Infrequent Access Tier**: $0.0125 per GB/month
- **Archive Instant Access**: $0.004 per GB/month
- **Archive Access**: $0.0036 per GB/month
- **Deep Archive Access**: $0.00099 per GB/month
- **Monitoring**: $0.0025 per 1,000 objects

### Use Cases
- Data with unknown or changing access patterns
- Data lakes
- Analytics data
- User-generated content
- Long-lived data with unpredictable access

### Configuration
```bash
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket my-bucket \
  --id entire-bucket-config \
  --intelligent-tiering-configuration '{
    "Id": "entire-bucket-config",
    "Status": "Enabled",
    "Tierings": [
      {
        "Days": 90,
        "AccessTier": "ARCHIVE_ACCESS"
      },
      {
        "Days": 180,
        "AccessTier": "DEEP_ARCHIVE_ACCESS"
      }
    ]
  }'
```

### Best Practices
- Ideal for objects >128 KB (monitoring fee makes smaller objects expensive)
- Enable Archive Access and Deep Archive Access tiers for maximum savings
- Use for unpredictable access patterns
- Combine with S3 Lifecycle policies for deleted versions

## S3 Standard-IA (Infrequent Access)

### Characteristics
- **Lower Storage Cost**: ~50% less than S3 Standard
- **Retrieval Fee**: $0.01 per GB retrieved
- **Minimum Storage Duration**: 30 days (charged for 30 days even if deleted earlier)
- **Minimum Object Size**: 128 KB (smaller objects charged as 128 KB)
- **Availability**: 99.9% SLA

### Pricing (US East - Ohio)
- **Storage**: $0.0125 per GB/month
- **PUT/COPY/POST/LIST**: $0.01 per 1,000 requests
- **GET/SELECT**: $0.001 per 1,000 requests
- **Retrieval**: $0.01 per GB
- **Lifecycle Transition**: $0.01 per 1,000 requests

### Use Cases
- Backups
- Disaster recovery files
- Long-term storage with infrequent access
- Older data accessed less than once per month
- Compliance archives that may need quick access

### Cost Break-Even Analysis
```
Break-even calculation:
- Standard-IA is cost-effective if:
  - Objects stored for >30 days
  - Objects >128 KB
  - Retrieved <1-2 times per month

Example:
100 GB stored for 3 months, retrieved once:
- S3 Standard: $6.90 storage + $0 retrieval = $6.90
- S3 Standard-IA: $3.75 storage + $1.00 retrieval = $4.75
- Savings: $2.15 (31%)
```

### Best Practices
- Use for objects accessed less than once per month
- Objects must be >128 KB for cost efficiency
- Plan to store for at least 30 days
- Use lifecycle policies to automate transitions from Standard after 30+ days

## S3 One Zone-IA

### Characteristics
- **Single AZ Storage**: Data stored in only one availability zone
- **Lower Cost**: 20% less than Standard-IA
- **Availability**: 99.5% SLA (lower than Standard-IA)
- **Risk**: Data lost if AZ is destroyed
- **Performance**: Same millisecond latency as Standard-IA

### Pricing (US East - Ohio)
- **Storage**: $0.01 per GB/month
- **Retrieval**: $0.01 per GB
- **Minimum Storage**: 30 days
- **Minimum Size**: 128 KB

### Use Cases
- Recreatable data
- Secondary backup copies
- Data already replicated across regions
- Infrequently accessed thumbnails or resized media
- Dev/test environments

### Risk Considerations
```
Availability scenarios:
- Multi-AZ (Standard, Standard-IA): 99.9-99.99%
  - Survives AZ failure

- One Zone-IA: 99.5%
  - Does NOT survive AZ failure
  - ~0.5% annual risk of data loss
```

### Best Practices
- Only use for data you can regenerate
- Not suitable for compliance or critical data
- Good for secondary copies when primary is in Standard or Standard-IA
- Consider cross-region replication for additional protection

## S3 Glacier Instant Retrieval

### Characteristics
- **Archive Storage**: Long-term archive with instant access
- **Low Cost**: ~70% cheaper than Standard-IA
- **Retrieval**: Milliseconds (same as Standard)
- **Minimum Storage**: 90 days
- **Minimum Size**: 128 KB

### Pricing (US East - Ohio)
- **Storage**: $0.004 per GB/month
- **Retrieval**: $0.03 per GB
- **PUT/COPY/POST/LIST**: $0.02 per 1,000 requests
- **GET/SELECT**: $0.01 per 1,000 requests

### Use Cases
- Medical images and records
- News media assets
- User-generated content archives
- Genomics data
- Quarterly accessed backup data

### Cost Comparison
```
1 TB stored for 1 year, accessed 4 times:
- S3 Standard-IA: ($12.50 × 12) + ($10 × 4) = $190
- Glacier Instant: ($4.00 × 12) + ($30 × 4) = $168
- Savings: $22 (12%)

1 TB stored for 1 year, accessed 1 time:
- S3 Standard-IA: ($12.50 × 12) + ($10 × 1) = $160
- Glacier Instant: ($4.00 × 12) + ($30 × 1) = $78
- Savings: $82 (51%)
```

### Best Practices
- Use for data accessed once per quarter or less
- Objects must be >128 KB
- Plan to store for at least 90 days
- Ideal replacement for Standard-IA when access is rare

## S3 Glacier Flexible Retrieval (Formerly S3 Glacier)

### Characteristics
- **Very Low Cost**: ~80% cheaper than Standard
- **Retrieval Time**: Minutes to hours (configurable)
- **Minimum Storage**: 90 days
- **Minimum Size**: 40 KB

### Retrieval Options
1. **Expedited**: 1-5 minutes, $0.03/GB + $0.01 per request
2. **Standard**: 3-5 hours, $0.01/GB + $0.05 per 1,000 requests
3. **Bulk**: 5-12 hours, $0.0025/GB + $0.025 per 1,000 requests

### Pricing (US East - Ohio)
- **Storage**: $0.0036 per GB/month
- **Upload**: $0.03 per 1,000 requests
- **Retrieval**: Varies by speed (see above)

### Use Cases
- Long-term backups
- Archive for compliance
- Media asset archives
- Scientific data archives
- Historical records

### Provisioned Capacity
```bash
# Purchase provisioned capacity for guaranteed Expedited retrievals
aws glacier purchase-provisioned-capacity \
  --account-id - \
  --vault-name my-vault

# Cost: $100/month per unit
# Capacity: 3 expedited retrievals every 5 minutes, up to 150 MB/s
```

### Best Practices
- Use Bulk retrievals for cost-effective large restores
- Purchase provisioned capacity for guaranteed Expedited access
- Use for data accessed 1-2 times per year
- Combine with S3 Batch Operations for large restores

## S3 Glacier Deep Archive

### Characteristics
- **Lowest Cost**: $0.00099 per GB/month (99% cheaper than Standard)
- **Retrieval Time**: 12-48 hours
- **Minimum Storage**: 180 days
- **Minimum Size**: 40 KB
- **Durability**: Same 11 nines as other S3 classes

### Retrieval Options
1. **Standard**: 12 hours, $0.02/GB + $0.05 per 1,000 requests
2. **Bulk**: 48 hours, $0.0025/GB + $0.025 per 1,000 requests

### Pricing (US East - Ohio)
- **Storage**: $0.00099 per GB/month (~$1/TB/month)
- **Upload**: $0.05 per 1,000 requests
- **Retrieval**: $0.02/GB (Standard), $0.0025/GB (Bulk)

### Use Cases
- Regulatory archives (7-10 year retention)
- Financial services archives
- Healthcare information archives
- Media archives
- Tape replacement
- Long-term backup for disaster recovery

### Cost Example
```
10 TB stored for 7 years, never accessed:
- S3 Standard: $2,760 per year × 7 = $19,320
- Glacier Deep Archive: $120 per year × 7 = $840
- Savings: $18,480 (96%)

If accessed once during 7 years:
- Restore cost: $200 (10 TB × $0.02/GB)
- Total: $1,040 (still 95% savings)
```

### Best Practices
- Use for data retained for compliance, accessed rarely or never
- Minimum 180-day retention required
- Plan retrievals in advance (12-48 hour wait)
- Most cost-effective for multi-year storage
- Ideal replacement for tape libraries

## S3 Lifecycle Policies

### Transition Rules
```json
{
  "Rules": [
    {
      "Id": "Archive-and-delete",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

### Supported Transitions
```
S3 Standard
    ↓
S3 Intelligent-Tiering
    ↓
S3 Standard-IA / S3 One Zone-IA
    ↓
S3 Glacier Instant Retrieval
    ↓
S3 Glacier Flexible Retrieval
    ↓
S3 Glacier Deep Archive

Constraints:
- Objects must be stored for min 30 days before transition to IA
- Objects must be ≥128 KB for IA classes
- Cannot transition from Glacier back to Standard
```

### Lifecycle Best Practices
1. **Start with Standard**: Unknown access patterns
2. **Transition to IA**: After 30 days for infrequent access
3. **Move to Glacier**: After 90 days for archive
4. **Deep Archive**: After 1 year for long-term retention
5. **Set Expiration**: Delete after retention period
6. **Version Management**: Transition and expire non-current versions

## Storage Class Analysis

### Enable Analysis
```bash
aws s3api put-bucket-analytics-configuration \
  --bucket my-bucket \
  --id my-analysis \
  --analytics-configuration '{
    "Id": "my-analysis",
    "StorageClassAnalysis": {
      "DataExport": {
        "OutputSchemaVersion": "V_1",
        "Destination": {
          "S3BucketDestination": {
            "Format": "CSV",
            "Bucket": "arn:aws:s3:::my-analysis-bucket",
            "Prefix": "analysis-results/"
          }
        }
      }
    }
  }'
```

### Analysis Insights
- Access patterns by age of data
- Recommendations for lifecycle transitions
- Analysis updated daily
- Results available after 30 days
- CSV export for further analysis

## Selection Decision Tree

```
Is data accessed frequently (daily/weekly)?
├─ YES → S3 Standard
└─ NO → Is access pattern predictable?
    ├─ YES → How often accessed?
    │   ├─ Monthly → S3 Standard-IA
    │   ├─ Quarterly → S3 Glacier Instant Retrieval
    │   ├─ Yearly → S3 Glacier Flexible Retrieval
    │   └─ Rarely/Never → S3 Glacier Deep Archive
    └─ NO → S3 Intelligent-Tiering

Is data critical?
├─ YES → Multi-AZ classes (Standard, Standard-IA, Glacier)
└─ NO → Consider S3 One Zone-IA for cost savings

Can you wait for retrieval?
├─ NO → S3 Standard, Intelligent-Tiering, IA, or Glacier Instant
└─ YES → Glacier Flexible or Deep Archive

Storage duration?
├─ <30 days → S3 Standard only
├─ 30-90 days → Standard or Standard-IA
├─ 90-180 days → Add Glacier Instant option
└─ >180 days → All classes available
```

## Best Practices Summary

1. **Start with Standard**: Move to other classes based on actual usage
2. **Use Intelligent-Tiering**: For unknown/changing access patterns
3. **Lifecycle Policies**: Automate transitions to reduce costs
4. **Storage Class Analysis**: Data-driven optimization decisions
5. **Consider Minimums**: 30/90/180 day minimums affect cost calculations
6. **Object Size Matters**: ≥128 KB for IA classes to be cost-effective
7. **Monitor Access**: Use S3 Analytics and CloudWatch metrics
8. **Tag for Organization**: Apply lifecycle policies per tag
9. **Version Management**: Transition old versions to cheaper classes
10. **Cross-Region Replication**: Consider storage class in destination

This comprehensive reference covers all S3 storage classes to help you optimize costs while meeting performance and durability requirements.
