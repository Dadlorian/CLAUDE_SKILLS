# Cloud Pricing Models Reference

## Overview

Understanding cloud pricing models is fundamental to effective cost optimization. Each cloud provider (AWS, Azure, GCP) offers multiple pricing models with different trade-offs between flexibility, commitment, and cost. This reference covers all major pricing models across the three leading cloud providers.

## Core Pricing Models

### 1. On-Demand Pricing

**Description**: Pay for compute, storage, or other resources by the hour or second with no long-term commitments.

**Characteristics**:
- No upfront costs or long-term contracts
- Pay only for what you use
- Highest per-unit cost
- Maximum flexibility
- Instant availability

**When to Use**:
- Unpredictable workloads
- Short-term or temporary workloads
- Testing and development
- Applications with spiky traffic
- New workloads with unknown patterns

**Cost Comparison**: Baseline (100% cost)

**AWS Examples**:
- EC2 On-Demand instances
- Lambda invocations
- RDS on-demand instances
- DynamoDB on-demand capacity

**Azure Examples**:
- Virtual Machines pay-as-you-go
- Azure Functions consumption plan
- SQL Database pay-as-you-go
- Cosmos DB on-demand

**GCP Examples**:
- Compute Engine on-demand
- Cloud Functions invocations
- Cloud SQL on-demand
- Firestore usage-based pricing

### 2. Reserved Instances / Reservations

**Description**: Commit to using a specific instance type in a specific region for 1 or 3 years in exchange for significant discounts.

**Characteristics**:
- 1-year or 3-year term commitments
- 30-75% discount vs on-demand
- Three payment options: All Upfront, Partial Upfront, No Upfront
- Region and instance type specific (standard RIs)
- Convertible options allow flexibility (at lower discount)

**AWS Reserved Instances**:
- **Standard RIs**: Up to 72% discount, specific instance type and region
- **Convertible RIs**: Up to 54% discount, can change instance family
- **Payment Options**: All Upfront (highest discount), Partial Upfront, No Upfront
- **Scope**: Regional or zonal (zonal provides capacity reservation)
- **Services**: EC2, RDS, ElastiCache, Redshift, Elasticsearch, OpenSearch

**Azure Reservations**:
- **Discount**: Up to 72% vs pay-as-you-go
- **Term**: 1-year or 3-year
- **Flexibility**: Instance size flexibility within same series
- **Scope**: Single subscription, shared (all subscriptions), management group
- **Services**: VMs, SQL Database, Cosmos DB, App Service, Storage, Synapse

**GCP Committed Use Discounts (CUDs)**:
- **Resource-Based CUDs**: Commit to specific machine types (up to 57% discount)
- **Spend-Based CUDs**: Commit to spend amount, more flexibility (up to 25% discount)
- **Term**: 1-year or 3-year
- **Flexibility**: Partial CUD consumption allowed
- **Services**: Compute Engine, Cloud SQL, GKE, Dataflow, VMware Engine

**Best Practices**:
- Analyze 30-90 days of usage patterns before purchasing
- Start with 1-year terms to maintain flexibility
- Use convertible RIs for evolving workloads
- Monitor utilization and coverage metrics
- Consider zonal RIs only when capacity guarantees needed
- Use reservation exchange programs when available

### 3. Savings Plans (AWS) / Flexible Reserved Instances

**Description**: Commit to a consistent amount of usage (measured in $/hour) for 1 or 3 years, with automatic discounts applied to eligible usage.

**AWS Savings Plans**:

**Compute Savings Plans**:
- Up to 66% discount
- Applies to EC2, Fargate, Lambda
- Most flexible - works across instance family, size, OS, tenancy, region
- Ideal for dynamic workloads and containerized applications

**EC2 Instance Savings Plans**:
- Up to 72% discount
- Applies to specific EC2 instance family in specific region
- Flexible across size, OS, tenancy within that family
- Better discount than Compute SP but less flexible

**SageMaker Savings Plans**:
- Up to 64% discount
- Applies to SageMaker training and inference
- Flexible across instance families, sizes, regions

**Key Features**:
- Hourly commitment (e.g., $10/hour for 1 year)
- Automatically applies to eligible usage
- No need to specify instance types or regions upfront
- Easier to manage than RIs
- Can combine with RIs (RIs apply first)

**When to Use**:
- Steady-state workloads with known minimum spend
- Multi-service usage (EC2 + Lambda + Fargate)
- Dynamic instance type requirements
- Multi-region deployments

### 4. Spot Instances / Preemptible VMs

**Description**: Purchase unused cloud capacity at steep discounts (up to 90%) with the caveat that instances can be interrupted with short notice.

**AWS Spot Instances**:
- Up to 90% discount vs on-demand
- 2-minute interruption warning
- Spot instance advisor shows interruption rates
- Spot Fleet for diversified instance types
- Spot blocks for defined duration (1-6 hours) - deprecated
- Integrates with Auto Scaling Groups, ECS, EKS, EMR

**Azure Spot VMs**:
- Up to 90% discount vs pay-as-you-go
- Eviction policies: Deallocate or Delete
- Can set max price (default is on-demand price)
- 30-second eviction notice
- Integrates with VM Scale Sets, AKS, Batch

**GCP Preemptible VMs**:
- Up to 80% discount vs on-demand
- Maximum 24-hour lifetime
- 30-second shutdown script notice
- No live migration
- Can be terminated any time
- Integrates with Instance Groups, GKE, Dataflow

**Ideal Workloads**:
- Batch processing jobs
- Data analysis and processing
- CI/CD build workers
- Rendering and transcoding
- Machine learning training
- Stateless web applications
- High-throughput computing

**Not Suitable For**:
- Databases with persistent state
- Applications requiring guaranteed availability
- Long-running jobs that can't tolerate interruption
- Applications without checkpointing

**Best Practices**:
- Diversify across multiple instance types and availability zones
- Implement graceful shutdown handling
- Use checkpointing for long-running jobs
- Combine with on-demand instances for baseline capacity
- Monitor spot pricing trends
- Use managed services (EMR, GKE, AKS) that handle spot orchestration

### 5. Sustained Use Discounts (GCP)

**Description**: Automatic discounts for running compute resources for a significant portion of the month (GCP only).

**GCP Sustained Use Discounts**:
- Automatic discount (no commitment required)
- Up to 30% discount for running VMs continuously
- Applies to Compute Engine and GKE
- Incremental discount: 20% of month (10%), 50% (20%), 100% (30%)
- Automatically applied to bill
- Inferred instances: Combines usage across instance types in same region

**How It Works**:
- Runs 25% of month: ~10% discount
- Runs 50% of month: ~20% discount
- Runs 100% of month: ~30% discount
- No action required, automatically calculated

**Stackable**:
- Can combine with CUDs for even greater savings
- Works with custom machine types
- Applies per-region, per-instance type

### 6. Savings Plans vs Reserved Instances Comparison

| Feature | Reserved Instances | Savings Plans |
|---------|-------------------|---------------|
| Discount Level | Up to 72% | Up to 72% |
| Flexibility | Locked to instance family/region | Works across families/regions |
| Commitment | Specific capacity | Dollar amount per hour |
| Complexity | More complex to manage | Simpler management |
| Service Coverage | Service-specific | Multi-service (Compute SP) |
| Modification | Requires exchange/modification | Automatically applies |
| Best For | Stable, predictable workloads | Dynamic, multi-service usage |

## Specialized Pricing Models

### Serverless / Consumption-Based

**AWS Lambda**:
- Per-request: $0.20 per 1M requests
- Per-GB-second: Based on memory allocated and execution time
- Free tier: 1M requests, 400,000 GB-seconds per month
- Provisioned concurrency: Additional charge for guaranteed warm instances

**Azure Functions**:
- Consumption Plan: Per execution and GB-seconds
- Premium Plan: Pre-warmed instances, higher limits
- Dedicated Plan: Run on App Service Plan

**GCP Cloud Functions**:
- Per invocation: $0.40 per 1M requests
- Per-GB-second and per-GHz-second of compute time
- Always-on instances: Keep functions warm (higher cost)

**Optimization Tips**:
- Right-size memory allocation (more memory = more CPU)
- Reduce cold starts with provisioned concurrency or always-on
- Batch operations when possible
- Use appropriate execution timeout
- Optimize dependencies and package size

### Database Pricing Models

**Provisioned Capacity**:
- Pay for allocated capacity (CPU, memory, IOPS)
- Consistent, predictable performance
- Can be over-provisioned (waste) or under-provisioned (performance issues)
- Examples: RDS, Azure SQL Database, Cloud SQL

**Serverless Database**:
- Pay per request or by capacity units consumed
- Automatically scales to zero when idle
- Higher per-unit cost but lower total cost for intermittent usage
- Examples: Aurora Serverless, Azure SQL Serverless, Firestore

**On-Demand Capacity (NoSQL)**:
- Pay per read/write request
- No capacity planning required
- Best for unpredictable workloads
- Examples: DynamoDB on-demand, Cosmos DB serverless

**Provisioned Throughput (NoSQL)**:
- Pre-allocate read/write capacity units
- Lower cost for consistent usage
- Requires capacity planning
- Examples: DynamoDB provisioned, Cosmos DB provisioned

### Storage Pricing Tiers

**Hot / Frequent Access**:
- Highest storage cost per GB
- Lowest retrieval cost
- Optimized for frequent access
- Examples: S3 Standard, Azure Blob Hot, GCS Standard

**Cool / Infrequent Access**:
- Lower storage cost (~50% less)
- Higher retrieval cost
- Minimum storage duration (30 days typically)
- Examples: S3 Infrequent Access, Azure Blob Cool, GCS Nearline

**Cold / Archive**:
- Very low storage cost (~10-20% of hot)
- Higher retrieval cost and latency
- Minimum storage duration (90-180 days)
- Examples: S3 Glacier, Azure Blob Archive, GCS Coldline/Archive

**Intelligent Tiering**:
- Automatic movement between tiers based on access patterns
- Small monitoring fee
- Optimizes cost automatically
- Examples: S3 Intelligent-Tiering, Azure Blob Archive Tier

## Network Pricing

### Data Transfer Costs

**Inbound Transfer**:
- Generally free across all providers
- Exceptions: Direct Connect, ExpressRoute, Interconnect setup costs

**Outbound Transfer (Internet Egress)**:
- Most expensive data transfer
- Tiered pricing (more usage = lower per-GB cost)
- Regional variations in pricing
- Critical cost driver for high-bandwidth applications

**Inter-Region Transfer**:
- Significant cost (similar to internet egress in some cases)
- Both source and destination may incur charges
- Use cases: replication, DR, multi-region architectures

**Intra-Region Transfer**:
- Between availability zones: Small cost (typically $0.01-0.02/GB)
- Within same availability zone: Often free
- Important for high-volume data flows

**CDN / Edge Pricing**:
- CloudFront, Azure CDN, Cloud CDN
- Generally cheaper than direct egress
- Tiered pricing based on volume
- Varies by geographic region

### Cost Optimization Strategies

**Data Transfer**:
- Use CDN for content delivery
- Cache aggressively
- Compress data in transit
- Keep data in same region when possible
- Use VPC endpoints / Private Link to avoid internet charges
- Batch data transfers
- Use AWS Direct Connect / Azure ExpressRoute / Cloud Interconnect for high volume

## Licensing Models

### Bring Your Own License (BYOL)
- Use existing on-premises licenses in cloud
- Typically requires License Mobility
- Examples: Windows Server, SQL Server, Oracle
- Can reduce costs significantly if licenses already owned

### License Included
- Cloud provider includes license in instance cost
- Higher per-hour cost but no separate license management
- Simpler, often better for new workloads
- Examples: RDS with SQL Server license included

### Open Source
- No licensing costs
- May have support subscription costs
- Examples: MySQL, PostgreSQL, MariaDB, MongoDB

## Pricing Calculators

### AWS Pricing Calculator
- URL: calculator.aws
- Estimate costs for AWS services
- Create detailed architecture estimates
- Share estimates with team/customers
- Export to CSV/PDF

### Azure Pricing Calculator
- URL: azure.microsoft.com/pricing/calculator
- Estimate Azure service costs
- Compare scenarios
- Export estimates

### GCP Pricing Calculator
- URL: cloud.google.com/products/calculator
- Estimate GCP costs
- Quick estimates and detailed scenarios
- Share via URL

### Third-Party Tools
- **Infracost**: IaC cost estimation for Terraform, CloudFormation
- **Concourse**: Multi-cloud cost estimation
- **Cloud cost management platforms**: Often include cost estimation features

## Pricing Optimization Decision Tree

### For Compute Workloads

```
Is workload steady-state and predictable?
├─ Yes → Consider Reserved Instances / Savings Plans
│  ├─ Can commit for 3 years? → 3-year term (highest discount)
│  └─ Only 1 year? → 1-year term
│
├─ Partially → Consider partial RI/SP coverage
│  └─ Cover baseline with RI/SP, use on-demand for peak
│
└─ No → Use on-demand or spot
   ├─ Can tolerate interruption? → Use Spot instances
   └─ Cannot tolerate interruption → Use on-demand
```

### For Storage

```
How frequently is data accessed?
├─ Multiple times per day → Hot/Standard tier
├─ Few times per month → Cool/Infrequent Access tier
├─ Few times per year → Cold/Archive tier
└─ Unknown/Variable → Intelligent Tiering
```

### For Databases

```
Is usage consistent and predictable?
├─ Yes → Provisioned capacity
│  └─ Can commit? → Reserved capacity
│
└─ No → Serverless or on-demand capacity
   ├─ Intermittent (goes idle) → Serverless
   └─ Unpredictable but active → On-demand
```

## Hybrid Pricing Strategies

### Layered Approach
1. **Base Layer (60-70%)**: Reserved capacity for baseline
2. **Variable Layer (20-30%)**: On-demand for fluctuations
3. **Burst Layer (5-10%)**: Spot instances for peak demand

### Risk-Balanced Approach
- Mix of commitment levels to balance discount and flexibility
- Longer terms for stable workloads
- Shorter terms or on-demand for evolving workloads

### Multi-Cloud Pricing Strategy
- Leverage pricing differences between providers
- Use each provider's strengths (GCP for compute, AWS for breadth)
- Balance with management complexity

## Pricing Change Management

### Tracking Price Changes
- Subscribe to cloud provider pricing updates
- Monitor announcements for price reductions
- Review quarterly for optimization opportunities
- Some prices decrease over time (compute, storage)

### Impact of New Pricing Models
- Evaluate new pricing options as released
- Savings Plans were introduced to simplify RIs
- Spot Blocks introduced then deprecated
- Stay current with pricing innovation

### Regional Pricing Differences
- Significant variation by geographic region
- Some regions 30-50% cheaper for same resources
- Consider data residency and latency requirements
- Evaluate workload placement by region pricing

## Common Pricing Pitfalls

1. **Not Using Commitments**: Paying on-demand prices for steady workloads
2. **Over-Committing**: Purchasing too many RIs that go unused
3. **Ignoring Data Transfer**: Underestimating egress and inter-region transfer costs
4. **Wrong Storage Tier**: Using hot storage for infrequently accessed data
5. **Not Rightsizing**: Over-provisioning before purchasing RIs
6. **Fragmented Purchases**: Buying small RI increments instead of consolidating
7. **Ignoring Spot**: Not using spot instances for suitable workloads
8. **License Waste**: Over-licensing or not leveraging BYOL

## Best Practices Summary

1. **Understand Your Workload**: Analyze before committing
2. **Start Conservative**: Begin with shorter commitments, increase as confidence grows
3. **Diversify**: Mix of pricing models based on workload characteristics
4. **Monitor Continuously**: Track utilization and coverage
5. **Automate Optimization**: Use tools to manage commitments
6. **Review Regularly**: Quarterly reviews of pricing and optimization opportunities
7. **Stay Informed**: Keep up with new pricing models and options
8. **Calculate Total Cost**: Include all factors (compute, storage, network, licensing)

## Resources

### AWS Pricing
- AWS Pricing page: aws.amazon.com/pricing
- AWS Cost Management: aws.amazon.com/aws-cost-management
- AWS Pricing Calculator: calculator.aws

### Azure Pricing
- Azure Pricing: azure.microsoft.com/pricing
- Azure Pricing Calculator: azure.microsoft.com/pricing/calculator
- Azure Cost Management: azure.microsoft.com/services/cost-management

### GCP Pricing
- GCP Pricing: cloud.google.com/pricing
- GCP Pricing Calculator: cloud.google.com/products/calculator
- GCP Cost Management: cloud.google.com/cost-management

### Comparison Resources
- Cloud provider pricing comparison tools
- FinOps Foundation pricing resources
- Independent analyst reports (Gartner, Forrester)
