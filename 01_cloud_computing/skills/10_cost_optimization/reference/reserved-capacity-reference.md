# Reserved Capacity Reference

## Overview

Reserved capacity (Reserved Instances, Savings Plans, Committed Use Discounts) offers significant cost savings (30-75% vs on-demand) in exchange for commitment to use cloud resources for 1 or 3 years. Effective reserved capacity management is a cornerstone of cloud cost optimization.

## Types of Reserved Capacity

### AWS Reserved Instances (RIs)

#### Standard Reserved Instances
**Discount**: Up to 72% vs on-demand
**Commitment**: 1-year or 3-year
**Flexibility**: Locked to instance family, region, OS, tenancy
**Modifications**: Can modify AZ, instance size (within family), network type
**Best For**: Stable, predictable workloads with no expected changes

**Example**:
- Reserved: m5.large in us-east-1, Linux
- Cannot change to: m5.xlarge, different region, or different family
- Can change to: Different AZ in us-east-1, different size within m5 family (size flexibility)

#### Convertible Reserved Instances
**Discount**: Up to 54% vs on-demand
**Commitment**: 1-year or 3-year
**Flexibility**: Can exchange for different instance family, region, OS, tenancy
**Exchange**: Must be equal or greater value
**Best For**: Long-term commitment with potential for workload changes

**Example**:
- Start: c5.large Convertible RI
- Can convert to: m5.large, different region, Windows instead of Linux
- Value constraint: New RI must be equal or greater value

#### Payment Options
1. **All Upfront**: Highest discount, pay entire amount upfront
2. **Partial Upfront**: Medium discount, pay ~50% upfront, rest monthly
3. **No Upfront**: Lowest discount, pay monthly, no upfront payment

**Discount Comparison (3-year Linux RIs)**:
- Standard All Upfront: ~72% discount
- Standard Partial Upfront: ~69% discount
- Standard No Upfront: ~65% discount
- Convertible All Upfront: ~54% discount
- Convertible Partial Upfront: ~52% discount
- Convertible No Upfront: ~50% discount

#### RI Scope
**Regional RIs** (Recommended):
- Apply to any AZ in the region
- Instance size flexibility (within family)
- No capacity reservation
- More flexible, easier to manage

**Zonal RIs**:
- Apply to specific AZ only
- Provides capacity reservation
- No instance size flexibility
- Use only when capacity reservation needed

#### Services Supporting RIs
- **EC2**: Virtual machines
- **RDS**: Managed databases (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server)
- **ElastiCache**: Redis and Memcached
- **Redshift**: Data warehouse
- **OpenSearch Service**: Search and analytics
- **DynamoDB**: Reserved capacity (separate from RIs)

### AWS Savings Plans

#### Compute Savings Plans
**Discount**: Up to 66% vs on-demand
**Commitment**: 1-year or 3-year hourly spend (e.g., $10/hour)
**Flexibility**: Applies across EC2, Fargate, Lambda
- Any instance family, size, region, OS, tenancy
- Most flexible option
**Best For**: Dynamic workloads, multi-service usage, multi-region

**How It Works**:
- Commit to $X per hour for 1 or 3 years
- Automatically applies to eligible usage up to commitment
- Usage beyond commitment charged at on-demand rates
- Applies to highest discount rate first

#### EC2 Instance Savings Plans
**Discount**: Up to 72% vs on-demand
**Commitment**: 1-year or 3-year hourly spend
**Flexibility**: Applies within instance family in specific region
- Flexible across size, OS, tenancy within family
- Region-specific
**Best For**: Predictable EC2 usage in specific family/region

**Example**:
- Commit to $20/hour for M5 instances in us-east-1
- Applies to m5.large, m5.xlarge, m5.2xlarge, etc.
- Any OS, any tenancy, any size within M5 family

#### SageMaker Savings Plans
**Discount**: Up to 64% vs on-demand
**Commitment**: 1-year or 3-year hourly spend
**Flexibility**: Applies across SageMaker instance families, regions
**Best For**: ML training and inference workloads

#### Payment Options
Same as RIs: All Upfront, Partial Upfront, No Upfront

### Azure Reservations

#### Azure Reserved VM Instances
**Discount**: Up to 72% vs pay-as-you-go
**Commitment**: 1-year or 3-year
**Flexibility**:
- Instance size flexibility within same series/region
- Can exchange for different VM series
- Can cancel (up to $50k/year refund limit with 12% early termination fee)

**Scope Options**:
1. **Shared**: Applies to all subscriptions in billing account
2. **Single Subscription**: Applies to one subscription
3. **Single Resource Group**: Applies to VMs in specific resource group
4. **Management Group**: Applies to all subscriptions in management group

#### Other Azure Reservations
- **SQL Database**: Reserved vCore capacity
- **Cosmos DB**: Reserved throughput (RU/s)
- **Synapse Analytics**: Reserved capacity
- **Storage**: Reserved capacity (Blob, Files, Data Lake)
- **App Service**: Stamp fee reservations
- **Azure VMware Solution**: Reserved hosts

#### Azure Reservation Exchange and Refund
- **Exchange**: Swap for different reservation
- **Refund**: Up to $50,000 per year, 12% early termination fee
- **Flexibility**: More flexible than AWS RIs

### GCP Committed Use Discounts (CUDs)

#### Resource-Based CUDs
**Discount**: Up to 57% vs on-demand (70% for memory-optimized)
**Commitment**: 1-year or 3-year for specific machine types
**Flexibility**:
- Committed to specific vCPU and memory in region
- Can be shared across projects
- Partial consumption allowed

**How It Works**:
- Commit to X vCPUs and Y GB memory for a machine type
- Can use across instances of that type
- Partial usage still charged for full commitment
- Stacks with sustained use discounts

**Example**:
- Commit to 100 vCPUs and 400 GB memory for N1 machines in us-central1
- Can use across any combination of N1 instances totaling that capacity

#### Spend-Based CUDs
**Discount**: Up to 25% (lower than resource-based)
**Commitment**: 1-year or 3-year for minimum spend amount
**Flexibility**:
- Most flexible GCP option
- Applies across machine types, GPUs, local SSD
- More similar to AWS Savings Plans

**How It Works**:
- Commit to minimum hourly spend (e.g., $100/hour)
- Applied to eligible Compute Engine usage
- Flexibility across instance types and regions

#### Services Supporting CUDs
- **Compute Engine**: VMs, sole-tenant nodes
- **GKE**: Kubernetes cluster nodes
- **Cloud SQL**: Database instances
- **Dataflow**: Stream and batch processing
- **VMware Engine**: VMware on GCP

## Reserved Capacity Strategy

### Coverage Analysis

**What to Cover**:
- Stable, predictable workloads
- Production critical systems
- Long-running instances (> 730 hours/month)
- Workloads not planned for migration/decommission

**What NOT to Cover**:
- Highly variable or burstable workloads
- Short-lived or temporary workloads
- Workloads likely to change significantly
- Testing/development (unless runs 24x7)
- New workloads without established patterns

### Coverage Target

**Industry Benchmarks**:
- **Mature FinOps**: 60-80% coverage with commitments
- **Growing FinOps**: 40-60% coverage
- **Early FinOps**: 20-40% coverage

**Coverage Formula**:
```
Coverage % = (Hours covered by RIs/SPs) / (Total eligible hours) × 100
```

**Optimal Coverage**:
- Not 100% (need flexibility for changes)
- Balance discount rate with commitment risk
- Typically 70-80% sweet spot for most organizations

### Utilization Tracking

**Utilization Formula**:
```
Utilization % = (RI/SP hours used) / (RI/SP hours purchased) × 100
```

**Target Utilization**:
- **Goal**: > 95% utilization
- **< 80% utilization**: Problem - over-purchased or workload changes
- **100% utilization**: Optimal but consider increasing coverage

**Monitoring**:
- Daily utilization checks
- Alerts for utilization < 90%
- Monthly utilization reports
- Quarterly deep dives

### Portfolio Approach

**Diversification Strategy**:

1. **Term Mix**:
   - 70% 1-year commitments
   - 30% 3-year commitments (highest savings for stable workloads)

2. **Flexibility Mix**:
   - 60% Savings Plans / Convertible RIs (flexibility)
   - 40% Standard RIs / Resource CUDs (highest discount)

3. **Payment Mix**:
   - All Upfront: If cash flow allows (highest discount)
   - Partial Upfront: Balance cash flow and discount
   - No Upfront: If cash flow constrained

4. **Coverage Mix**:
   - 70-80% commitment coverage
   - 20-30% on-demand for flexibility

### Recommendation Engine

**Data-Driven Recommendations**:
1. Analyze 30-90 days of historical usage
2. Identify stable baseline usage (minimum usage over analysis period)
3. Calculate potential savings for different commitment levels
4. Consider upcoming changes (migrations, decommissions, growth)
5. Generate recommendations with risk assessment

**AWS Cost Explorer RI Recommendations**:
- Based on last 7, 30, or 60 days
- Considers payment option, term length
- Shows estimated monthly savings
- Multiple recommendation options

**Azure Advisor Recommendations**:
- Based on 7 or 30 days of usage
- VM reservation recommendations
- SQL Database, Cosmos DB recommendations
- Estimated annual savings

**GCP Recommender CUD Recommendations**:
- Analyzes recent usage patterns
- Resource-based and spend-based recommendations
- Projected savings and configuration

**Third-Party Tools**:
- **ProsperOps**: Autonomous RI/SP management
- **CloudHealth**: RI/SP recommendations and management
- **Apptio Cloudability**: Advanced RI/SP optimization

## Reserved Capacity Management

### Purchase Process

**1. Analysis Phase**:
- Gather utilization data (minimum 30 days, prefer 90 days)
- Identify stable workloads
- Calculate baseline usage
- Project growth and changes
- Consider planned migrations or decommissions

**2. Recommendation Phase**:
- Generate recommendations using native tools or third-party
- Review multiple scenarios (1-year vs 3-year, payment options)
- Calculate ROI and payback period
- Assess risk (what if workload changes?)

**3. Approval Phase**:
- Finance approval for commitment
- Engineering validation of workload stability
- Executive approval for large purchases
- Document decision rationale

**4. Purchase Phase**:
- Purchase RIs/SPs/CUDs
- Document purchase details
- Update tracking systems
- Communicate to relevant teams

**5. Monitoring Phase**:
- Track utilization daily
- Alert on low utilization
- Report on savings realized
- Identify optimization opportunities

### Modification and Exchange

**AWS RI Modifications**:
- **Standard RIs**: Can modify AZ, instance size (within family), network type
- **Convertible RIs**: Can exchange for different family, region, OS (equal or greater value)
- **Process**: AWS Console or API, instant for modifications
- **Limitations**: Cannot change term, payment option

**AWS Savings Plans**:
- Cannot be modified or exchanged
- Automatic application to eligible usage
- Less need for modification due to flexibility

**Azure Reservation Exchange**:
- Can exchange for different VM series, region
- Can return for refund (up to $50k/year, 12% fee)
- Process: Azure Portal or API
- Flexibility: More flexible than AWS

**GCP CUD Modifications**:
- Cannot modify existing CUDs
- Can purchase additional CUDs
- Can let CUDs expire and repurchase
- Less modification flexibility than AWS/Azure

### RI/SP Marketplace

**AWS Reserved Instance Marketplace**:
- **Sell**: Unused Standard RIs (not Convertible)
- **Buy**: Purchase RIs from other AWS customers (often at discount)
- **Use Cases**: Exit commitment early, find shorter-term RIs
- **Fees**: AWS charges 12% service fee to seller

**Selling Process**:
1. Register as seller (one-time)
2. List RI for sale (set price)
3. Buyer purchases
4. Seller receives payment (minus 12% fee)

**Buying Process**:
1. Browse marketplace listings
2. Purchase at listed price
3. RI immediately available

### Expiration Management

**90-Day Expiration Process**:

**90 Days Before**:
- Review expiring RIs/SPs
- Analyze current utilization
- Assess workload changes
- Preliminary renewal decision

**60 Days Before**:
- Gather updated utilization data
- Generate new recommendations
- Review with engineering teams
- Update forecasts

**30 Days Before**:
- Final decision: renew, modify, or let expire
- Calculate new coverage needed
- Prepare purchase request
- Get approvals

**At Expiration**:
- Purchase new RIs/SPs/CUDs
- Monitor transition to new commitments
- Verify coverage and utilization
- Update tracking systems

**Post-Expiration**:
- Analyze cost impact
- Validate savings projections
- Document learnings
- Adjust strategy as needed

## Advanced Strategies

### Instance Size Flexibility (AWS)

**How It Works**:
- Regional Linux RIs provide instance size flexibility
- One RI can apply to different sizes within same family
- Normalization factor determines coverage

**Normalization Factor**:
```
nano:    0.25
micro:   0.5
small:   1
medium:  2
large:   4
xlarge:  8
2xlarge: 16
4xlarge: 32
(continues doubling)
```

**Example**:
- Purchase: 1 × m5.2xlarge RI (normalization factor: 16)
- Can cover:
  - 1 × m5.2xlarge, OR
  - 2 × m5.xlarge, OR
  - 4 × m5.large, OR
  - 16 × m5.small, OR
  - Any combination totaling 16 units

**Benefits**:
- Flexibility without losing discount
- Adapt to changing workloads
- Simpler management (fewer RIs needed)

**Limitations**:
- Linux/Unix only (not Windows, RHEL)
- Regional RIs only (not zonal)
- Same instance family

### Stacking Discounts

**GCP: Sustained Use + CUD**:
- Sustained use discounts apply first (up to 30%)
- CUDs apply to remaining usage
- Combined savings can exceed 70% for memory-optimized

**AWS: RIs + Savings Plans**:
- Both can exist, applied in order
- RIs apply first, then Savings Plans
- Can strategically use both for optimal savings

**Azure: Reservations + Dev/Test Pricing**:
- Combine reservations with dev/test subscription pricing
- Additional savings for development workloads

### Zone Balancing (AWS)

**Challenge**: Uneven instance distribution across AZs

**Solution**:
- Use regional RIs (not zonal)
- Enable EC2 Auto Scaling AZ balancing
- Regional RIs apply regardless of AZ distribution

### Layered Commitment Strategy

**Layer 1: Long-Term Core (3-year)**:
- 30-40% of total usage
- Most stable, critical workloads
- Maximum discount

**Layer 2: Medium-Term Baseline (1-year)**:
- 30-40% of total usage
- Predictable but may evolve
- Balance of discount and flexibility

**Layer 3: Short-Term Optimization (On-Demand + Spot)**:
- 20-30% of total usage
- Variable, unpredictable workloads
- Maximum flexibility

**Benefits**:
- Balanced risk and reward
- Flexibility for changes
- Optimized savings

## RI/SP/CUD Optimization Tools

### Native Cloud Tools

**AWS**:
- **Cost Explorer RI Recommendations**: Built-in recommendations
- **Savings Plans Recommendations**: In Cost Explorer
- **Utilization Reports**: Track RI/SP utilization and coverage
- **Budgets**: Alert on RI/SP utilization

**Azure**:
- **Azure Advisor**: Reservation recommendations
- **Cost Management**: Utilization and coverage tracking
- **Reservation Transactions**: Purchase history
- **Reservation Utilization API**: Programmatic access

**GCP**:
- **Recommender**: CUD recommendations
- **Committed Use Discount Reports**: Utilization tracking
- **Cloud Billing Reports**: Coverage and savings analysis

### Third-Party Optimization Platforms

**ProsperOps**:
- Autonomous RI/SP management
- Continuously optimizes portfolio
- Manages term, type, payment option
- No-touch automation

**CloudHealth**:
- RI/SP recommendations
- Utilization and coverage tracking
- Optimization strategies
- Multi-cloud support

**Apptio Cloudability**:
- Advanced RI/SP analytics
- What-if scenario modeling
- Automated recommendations
- Commitment lifecycle management

**Spot.io**:
- Automated commitment management
- Covers commitment shortfalls with spot
- Multi-cloud support
- Risk-free commitments (guaranteed utilization)

## Financial Considerations

### ROI Calculation

**Payback Period**:
```
Payback = Upfront Payment / (Monthly On-Demand Cost - Monthly RI Cost)
```

**Example**:
- On-Demand monthly cost: $1,000
- RI upfront payment: $6,000
- RI monthly cost: $0 (all upfront 1-year)
- Payback period: $6,000 / $1,000 = 6 months

**Net Present Value (NPV)**:
Consider time value of money when comparing payment options.

**Total Cost of Ownership**:
Include management overhead, monitoring tools, opportunity cost of capital.

### Budget Planning

**RI/SP Budget Allocation**:
- Separate budget line for commitment purchases
- Amortized costs for chargeback/showback
- Reserve for expiration renewals
- Buffer for optimization opportunities

**Cash Flow Management**:
- All Upfront: Large upfront cash outlay
- Partial Upfront: Balance of upfront and monthly
- No Upfront: Spread cost over term (higher total cost)

### Accounting Treatment

**Amortization**:
- Spread upfront cost over commitment term
- More accurate daily/monthly cost representation
- Recommended for internal reporting

**Unblended vs Blended vs Amortized**:
- **Unblended**: Actual charges as they appear
- **Blended**: Average cost across on-demand and commitments
- **Amortized**: Upfront costs spread over term (recommended)

## Best Practices

1. **Start Conservative**: Begin with 1-year terms, increase to 3-year as confidence grows
2. **Monitor Continuously**: Track utilization and coverage daily, optimize monthly
3. **Diversify**: Mix of term lengths, types, payment options
4. **Data-Driven Decisions**: Analyze 30-90 days of usage before purchasing
5. **Rightsize First**: Optimize instance sizes before purchasing commitments
6. **Document**: Track all purchases, decisions, rationale
7. **Automate**: Use tools to manage lifecycle, not spreadsheets
8. **Review Regularly**: Monthly optimization reviews, quarterly strategy reviews
9. **Align with Roadmap**: Consider planned changes, migrations, growth
10. **Flexibility Premium**: Accept slightly lower discount for flexibility (Savings Plans, Convertible RIs)

## Common Pitfalls

1. **Over-Purchasing**: Buying too many commitments, leading to low utilization
2. **Under-Purchasing**: Leaving easy savings on the table
3. **Ignoring Changes**: Not accounting for planned migrations or architecture changes
4. **Wrong Instance Types**: Purchasing RIs for instances about to be decommissioned
5. **Analysis Paralysis**: Overthinking and delaying purchases
6. **Set and Forget**: Not monitoring utilization after purchase
7. **All 3-Year Terms**: Locking in too long without flexibility
8. **Ignoring Marketplace**: Not considering marketplace for early exit
9. **Zonal RIs**: Purchasing zonal RIs when regional would suffice
10. **No Documentation**: Not tracking purchase rationale and ownership

## Resources

### AWS
- Reserved Instances: aws.amazon.com/ec2/pricing/reserved-instances
- Savings Plans: aws.amazon.com/savingsplans
- RI Marketplace: aws.amazon.com/ec2/purchasing-options/reserved-instances/marketplace
- Best Practices: docs.aws.amazon.com/cost-management

### Azure
- Azure Reservations: azure.microsoft.com/pricing/reservations
- Reservation Recommendations: docs.microsoft.com/azure/advisor
- Cost Management: azure.microsoft.com/services/cost-management

### GCP
- Committed Use Discounts: cloud.google.com/compute/docs/instances/signing-up-committed-use-discounts
- CUD Recommendations: cloud.google.com/recommender/docs/commitment-recommender
- Billing Best Practices: cloud.google.com/billing/docs/best-practices

### Tools
- ProsperOps: prosperops.com
- CloudHealth: cloudhealth.vmware.com
- Spot.io: spot.io
