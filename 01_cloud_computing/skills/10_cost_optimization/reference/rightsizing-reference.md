# Rightsizing Reference

## Overview

Rightsizing is the process of matching cloud resource capacity (CPU, memory, storage, network) to actual workload requirements. It's one of the most impactful cost optimization strategies, typically reducing costs by 20-40% while maintaining or improving performance.

## What is Rightsizing?

**Definition**: Analyzing resource utilization and modifying instance types, sizes, or configurations to eliminate waste while ensuring performance requirements are met.

**Goals**:
- Eliminate over-provisioning and waste
- Match resources to actual demand
- Maintain or improve application performance
- Reduce costs without sacrificing reliability
- Optimize resource efficiency

**Types of Rightsizing**:
1. **Vertical Rightsizing**: Change instance type/size (more or less CPU/memory)
2. **Horizontal Rightsizing**: Change number of instances (scale in/out)
3. **Architecture Rightsizing**: Fundamentally redesign for efficiency
4. **Service Rightsizing**: Move to more appropriate service type

## Why Rightsizing Matters

### Cost Impact
- **Over-Provisioning**: Most common issue, 30-50% of cloud resources over-provisioned
- **Typical Savings**: 20-40% reduction in compute costs
- **Compounding Effect**: Savings apply to both on-demand and reserved capacity
- **Quick Wins**: Often the fastest path to meaningful cost reduction

### Performance Impact
- **Right-Sizing Up**: Under-provisioned resources cause performance issues
- **Right-Sizing Down**: Properly sized resources often perform better (less resource contention)
- **Predictable Performance**: Consistent resource allocation improves reliability

### Operational Impact
- **Resource Efficiency**: Better utilization means fewer instances to manage
- **Sustainability**: Lower resource consumption reduces carbon footprint
- **Capacity Planning**: Understanding actual needs improves forecasting

## Rightsizing Methodology

### 1. Data Collection

**Metrics to Monitor** (minimum 2-4 weeks, ideally 30-90 days):

**Compute Metrics**:
- CPU Utilization (average, max, p95, p99)
- Memory Utilization (average, max, p95, p99)
- Network throughput (in/out)
- Disk I/O operations and throughput
- Instance metadata (type, size, region, tags)

**Application Metrics**:
- Request rate and latency
- Queue depth
- Error rates
- Application-specific performance indicators

**Time Dimensions**:
- Hourly patterns (identify peaks and valleys)
- Daily patterns (business hours vs after-hours)
- Weekly patterns (weekday vs weekend)
- Seasonal patterns (month-end, quarter-end, holidays)

**Data Sources**:
- **AWS**: CloudWatch metrics, Compute Optimizer, CloudWatch Agent
- **Azure**: Azure Monitor, Azure Advisor, VM Insights
- **GCP**: Cloud Monitoring, GCP Recommender, Cloud Trace
- **Third-Party**: Datadog, New Relic, Dynatrace, CloudHealth

### 2. Analysis

**Utilization Thresholds**:

**Over-Provisioned Indicators**:
- CPU: Max utilization < 40% consistently
- Memory: Max utilization < 60% consistently
- Network: Max throughput < 40% of available bandwidth
- Duration: Pattern persists for > 95% of observation period

**Under-Provisioned Indicators**:
- CPU: Average utilization > 80% or sustained periods > 90%
- Memory: Average utilization > 85%, swap activity
- Network: Throttling or saturation
- Application: Increased latency, errors, timeouts

**Appropriate Sizing**:
- CPU: Average 40-60%, peaks 70-80%
- Memory: Average 60-75%, max < 90%
- Headroom for burst capacity and growth
- Meets performance SLAs consistently

### 3. Recommendation Generation

**Considerations**:
- Performance requirements and SLAs
- Cost reduction potential
- Risk and impact assessment
- Implementation effort
- Application architecture constraints

**Recommendation Confidence Levels**:
- **High Confidence**: Consistent low utilization, low risk (e.g., 10% CPU for 30 days)
- **Medium Confidence**: Moderate opportunity, some variability
- **Low Confidence**: High variability, requires deeper analysis

### 4. Testing and Validation

**Pre-Implementation**:
- Review with application team
- Understand workload characteristics
- Identify performance testing approach
- Plan rollback procedure

**Implementation Approach**:
- Start with non-production environments
- Test during low-traffic periods initially
- Gradual rollout (blue-green, canary)
- Monitor closely during and after changes

**Validation**:
- Compare pre/post performance metrics
- Verify SLA compliance
- Confirm cost savings realized
- Document learnings

### 5. Continuous Rightsizing

**Ongoing Process**:
- Monthly rightsizing reviews
- Automated recommendation generation
- Integration into change management
- Regular optimization cycles

## Rightsizing Strategies by Workload Type

### Steady-State Applications
**Characteristics**: Consistent, predictable load
**Strategy**: Rightsize to average utilization + headroom, use RIs/SPs for savings
**Example**: Internal tools, CRM systems, email servers

### Burstable Workloads
**Characteristics**: Low baseline, periodic spikes
**Strategy**: Use burstable instances (T-series), auto-scaling, or serverless
**Examples**: Development servers, small websites, batch jobs

### Batch Processing
**Characteristics**: Scheduled or ad-hoc processing jobs
**Strategy**: Spot instances, serverless, scheduled scaling
**Examples**: ETL jobs, report generation, data processing

### Highly Variable Workloads
**Characteristics**: Unpredictable patterns
**Strategy**: Auto-scaling with diverse instance types, serverless
**Examples**: Consumer applications, marketing campaigns

### Performance-Critical
**Characteristics**: Strict latency/performance requirements
**Strategy**: Conservative rightsizing, performance testing, headroom
**Examples**: Trading systems, real-time analytics, gaming

## Cloud Provider Rightsizing Tools

### AWS Compute Optimizer

**Features**:
- ML-powered recommendations for EC2, Auto Scaling Groups, EBS, Lambda
- Analysis of CloudWatch metrics (up to 14 days)
- Considers instance types within same family and across families
- Provides cost and performance risk assessment
- Three finding levels: under-provisioned, over-provisioned, optimized

**Instance Recommendations Include**:
- Current instance type and utilization
- Recommended instance types (up to 3 options)
- Estimated monthly savings
- Performance risk (very low, low, medium, high)
- CPU, memory, network utilization projections

**Supported Resources**:
- EC2 instances
- Auto Scaling Groups
- EBS volumes
- Lambda functions
- ECS services on Fargate

**Limitations**:
- Requires CloudWatch metrics
- 14-day lookback period (can extend to 93 days with opt-in)
- Doesn't consider all instance types
- No cost consideration for RIs/SPs

**Access**:
- AWS Console: Compute Optimizer service
- AWS CLI: `aws compute-optimizer get-ec2-instance-recommendations`
- API: Programmatic access for automation

### Azure Advisor

**Features**:
- Recommendations across cost, security, reliability, performance, operational excellence
- Cost recommendations include rightsizing and reserved capacity
- Analyzes 7-30 days of utilization data
- Integration with Azure Cost Management

**VM Rightsizing Recommendations**:
- Identifies underutilized VMs (average CPU < 5%, max CPU < 10%)
- Recommends shutdown or resize
- Estimates annual savings
- Considers VM family and series

**Additional Cost Recommendations**:
- Reserved Instance purchases
- Unused resources (public IPs, disks)
- App Service plan optimization

**Access**:
- Azure Portal: Advisor service
- Azure CLI: `az advisor recommendation list`
- PowerShell: `Get-AzAdvisorRecommendation`
- REST API: Programmatic access

### GCP Recommender

**Features**:
- Recommendations across cost, security, performance, sustainability
- Machine learning-driven insights
- Considers 8-day historical data
- Provides impact assessment and confidence level

**VM Rightsizing Recommendations**:
- Machine type recommendations
- Idle VM detection
- Disk size and type recommendations
- Underutilized persistent disk

**Recommendation Details**:
- Current configuration
- Recommended configuration
- Estimated cost savings
- Confidence level (high, medium, low)
- Impact assessment

**Access**:
- GCP Console: Recommender in Compute Engine
- gcloud CLI: `gcloud recommender recommendations list`
- API: Recommender API for automation

### Comparison Matrix

| Feature | AWS Compute Optimizer | Azure Advisor | GCP Recommender |
|---------|----------------------|---------------|-----------------|
| **Lookback Period** | 14 days (93 opt-in) | 7-30 days | 8 days |
| **ML-Powered** | Yes | Yes | Yes |
| **Cost Savings Estimate** | Yes | Yes | Yes |
| **Performance Risk** | Yes | Limited | Yes (confidence) |
| **Cross-Family Recommendations** | Yes | Limited | Yes |
| **API Access** | Yes | Yes | Yes |
| **Automation Support** | Good | Good | Good |
| **Lambda/Functions** | Yes | Yes (limited) | Yes |
| **Container Services** | Yes (ECS Fargate) | Yes (ACI) | Yes (GKE) |

## Third-Party Rightsizing Tools

### Enterprise Platforms

**CloudHealth by VMware**:
- Multi-cloud rightsizing recommendations
- Historical data analysis
- Policy-based automation
- Custom thresholds and rules
- Integration with change management

**Apptio Cloudability**:
- Advanced analytics and ML-based recommendations
- Workload-aware rightsizing
- Risk scoring
- Implementation tracking
- ROI analysis

**Densify**:
- Specialized in rightsizing and optimization
- Container and VM rightsizing
- Continuous optimization
- What-if scenario modeling
- Integration with cloud platforms

**Spot.io**:
- Automated rightsizing
- Reserved capacity optimization
- Spot instance management
- Autonomous scaling

### Open Source Tools

**Kubernetes-Specific**:
- **Kubecost**: K8s resource rightsizing, container optimization
- **Goldilocks**: Vertical Pod Autoscaler recommendations
- **KRR (Kubernetes Resource Recommender)**: Resource request/limit recommendations

**Multi-Cloud**:
- **Cloud Custodian**: Policy-based resource optimization
- **Komiser**: Resource inventory and rightsizing insights

## Instance Type Selection Guide

### AWS EC2 Instance Families

**General Purpose** (T, M, A series):
- **Use Case**: Balanced compute, memory, networking
- **T Series (Burstable)**: Low baseline, burst capability
  - T4g, T3, T3a: Cost-effective for variable workloads
  - CPU credits system
- **M Series**: Balance of resources
  - M7g, M6i, M6a: Latest generation, ARM and x86
  - Good for most applications

**Compute Optimized** (C series):
- **Use Case**: CPU-intensive workloads
- **C7g, C6i, C6a**: High CPU-to-memory ratio
- **Examples**: Batch processing, HPC, web servers, gaming

**Memory Optimized** (R, X, z series):
- **Use Case**: Memory-intensive workloads
- **R7g, R6i, R6a**: High memory-to-CPU ratio
- **X Series**: Extreme memory (up to 4 TB RAM)
- **Examples**: Databases, in-memory caches, real-time analytics

**Storage Optimized** (I, D, H series):
- **Use Case**: High sequential read/write, IOPS
- **I4i, I3, I3en**: NVMe SSD storage
- **D Series**: Dense HDD storage
- **Examples**: NoSQL databases, data warehousing, Hadoop

**Accelerated Computing** (P, G, F, Inf series):
- **Use Case**: GPU, FPGA workloads
- **P Series**: GPU compute (ML training)
- **G Series**: Graphics-intensive (ML inference, gaming)
- **Examples**: Machine learning, video processing

### Azure VM Sizes

**General Purpose**: B, Dsv3, Dv3, Dasv4, Dav4
- **B Series**: Burstable VMs
- **D Series**: Balanced performance

**Compute Optimized**: Fsv2
- High CPU-to-memory ratio
- Compute-intensive workloads

**Memory Optimized**: Esv3, Ev3, Easv4, Eav4, M, Mv2
- High memory-to-CPU ratio
- In-memory databases, analytics

**Storage Optimized**: Lsv2
- High disk throughput and IOPS
- NoSQL databases, data warehousing

**GPU**: NC, ND, NV
- GPU-accelerated workloads
- Deep learning, rendering

### GCP Machine Types

**General Purpose**: E2, N2, N2D, N1
- **E2**: Cost-effective, burstable
- **N2**: Balanced performance
- **N2D**: AMD processors

**Compute Optimized**: C2, C2D
- Ultra-high performance
- Compute-intensive workloads

**Memory Optimized**: M2, M1
- High memory configurations
- In-memory databases, SAP HANA

**Accelerator Optimized**: A2
- GPU VMs for ML and HPC

**Custom Machine Types**: Customize vCPU and memory

## Rightsizing Automation

### Automated Rightsizing Approaches

**1. Fully Automated** (Highest Risk, Highest Efficiency)
- **Approach**: Auto-apply recommendations meeting criteria
- **Criteria**: High confidence, non-production, specific tags
- **Tools**: Custom scripts, Spot.io, ProsperOps
- **Validation**: Automated rollback on performance degradation

**2. Semi-Automated** (Balanced Risk and Efficiency)
- **Approach**: Auto-generate recommendations, require approval
- **Workflow**: Alert → Review → Approve → Apply
- **Tools**: CloudHealth, Cloudability with ITSM integration
- **Validation**: Manual review before implementation

**3. Recommendation Engine** (Lowest Risk, Manual Implementation)
- **Approach**: Generate and report recommendations only
- **Review**: Regular (weekly/monthly) review meetings
- **Implementation**: Manual change management process
- **Tools**: Native cloud tools, custom dashboards

### Sample Automation Workflow

```
1. Daily: Collect utilization metrics (CloudWatch/Monitor/GCP Monitoring)
2. Weekly: Analyze and generate rightsizing recommendations
3. Filter: Apply confidence and impact thresholds
4. Categorize: High confidence/low risk → Medium → Low confidence/high risk
5. Auto-apply: High confidence + non-production + specific tags
6. Create tickets: Medium confidence recommendations
7. Report: Dashboard and email summary
8. Monitor: Track implementation and savings realized
```

## Container and Kubernetes Rightsizing

### Container Resource Rightsizing

**Challenges**:
- Dynamic workloads
- Thousands of containers vs. hundreds of VMs
- Request vs. limit confusion
- Multi-tenant clusters

**Key Concepts**:
- **Requests**: Guaranteed resources, used for scheduling
- **Limits**: Maximum resources, throttled if exceeded
- **Quality of Service**: Guaranteed, Burstable, BestEffort classes

### Kubernetes Rightsizing Strategies

**1. Vertical Pod Autoscaler (VPA)**
- Automatically adjusts CPU/memory requests and limits
- Based on historical usage
- Can update running pods or on restart
- Three modes: Off, Initial, Auto

**2. Horizontal Pod Autoscaler (HPA)**
- Scales number of pods based on metrics
- Complements rightsizing
- Custom metrics support

**3. Cluster Autoscaler**
- Scales node count based on pod requirements
- Works with HPA and VPA
- Removes empty nodes

### Kubernetes Rightsizing Tools

**Kubecost**:
- Namespace, pod, container cost visibility
- Rightsizing recommendations
- Request and limit optimization
- Cost allocation

**Goldilocks**:
- VPA recommendation dashboard
- Multiple modes: Off, Initial, Auto
- Visualizes recommendations vs. current configuration

**KRR (Kubernetes Resource Recommender)**:
- CLI tool for resource recommendations
- Analyzes Prometheus metrics
- Provides request/limit recommendations
- Open source and lightweight

## Database Rightsizing

### RDS/Azure SQL/Cloud SQL Rightsizing

**Metrics to Monitor**:
- CPU utilization
- Memory utilization (freeable memory)
- Storage utilization
- IOPS and throughput
- Connection count
- Read/write latency

**Rightsizing Options**:

**1. Instance Type/Size**
- Change instance class (db.m5.large → db.m5.medium)
- Different families (general purpose → memory optimized)

**2. Storage Optimization**
- Reduce allocated storage
- Change storage type (io1 → gp3)
- Adjust IOPS allocation

**3. Read Replicas**
- Offload read traffic
- Different sizing for replicas vs. primary

**4. Serverless Options**
- Aurora Serverless (AWS)
- Azure SQL Serverless
- Scale to zero when idle

### NoSQL Database Rightsizing

**DynamoDB**:
- On-demand vs. provisioned capacity
- Right-size RCUs/WCUs for provisioned
- Use auto-scaling
- Monitor throttling events

**Cosmos DB**:
- Provisioned vs. serverless vs. autoscale
- Right-size RU/s allocation
- Partition strategy optimization

**Firestore**:
- Usage-based pricing
- Optimize read/write patterns
- Caching strategies

## Serverless Rightsizing

### Lambda Function Rightsizing

**Memory Allocation**:
- Memory determines CPU allocation (proportional)
- More memory = faster execution but higher cost per second
- Sweet spot varies by workload

**Optimization Process**:
1. Test function with various memory settings (128 MB to 10,240 MB)
2. Measure execution time and cost for each
3. Find optimal memory (fastest execution at lowest total cost)
4. Consider: (memory cost × duration) = total cost

**Tools**:
- AWS Lambda Power Tuning (open source)
- AWS Compute Optimizer (Lambda recommendations)
- Custom benchmarking scripts

**Other Optimizations**:
- Optimize package size (reduce cold start)
- Use provisioned concurrency strategically
- Appropriate timeout settings

### Azure Functions and Cloud Functions

Similar optimization approaches:
- Memory/CPU allocation tuning
- Execution time optimization
- Cold start reduction
- Appropriate service plan selection

## Best Practices

### 1. Start with Low-Hanging Fruit
- Focus on obvious over-provisioning (< 10% CPU)
- Non-production environments first
- Instances without reserved capacity
- Build momentum with quick wins

### 2. Establish Baselines and Thresholds
- Define what "over-provisioned" means for your organization
- Different thresholds for different workload types
- Document and communicate standards
- Review thresholds quarterly

### 3. Involve Application Teams
- Collaboration between FinOps and Engineering
- Application teams understand their workloads best
- Shared responsibility for optimization
- Celebrate savings together

### 4. Test Thoroughly
- Non-production testing first
- Performance testing before and after
- Gradual rollout to production
- Monitor closely post-implementation

### 5. Automate Where Possible
- Automated recommendation generation
- Automated implementation for low-risk changes
- Automated monitoring and alerting
- Continuous optimization, not one-time

### 6. Account for Headroom
- Don't rightsize to 100% utilization
- Leave headroom for:
  - Traffic spikes and growth
  - Failover scenarios
  - Performance buffers
  - Typical: 20-30% headroom

### 7. Consider Total Cost
- Evaluate cost of change vs. savings
- Implementation effort and risk
- Opportunity cost of engineering time
- Balance optimization with other priorities

### 8. Track and Measure
- Monitor savings realized
- Track implementation rate
- Report on rightsizing program success
- Continuous improvement

## Common Pitfalls

1. **Rightsizing Without Monitoring**: Don't optimize blind - collect data first
2. **Over-Optimization**: Rightsizing too aggressively, causing performance issues
3. **Ignoring Application Architecture**: Sometimes architecture change is better than rightsizing
4. **Not Testing**: Assuming recommendations are always safe
5. **One-Time Exercise**: Rightsizing is continuous, not a project
6. **Ignoring Burstable Instances**: T-series instances perfect for many workloads
7. **Not Considering RIs**: Rightsize before purchasing reservations
8. **Analysis Paralysis**: Don't over-analyze, start with clear over-provisioning

## Resources

### AWS
- AWS Compute Optimizer: aws.amazon.com/compute-optimizer
- EC2 Instance Types: aws.amazon.com/ec2/instance-types
- Rightsizing Guide: aws.amazon.com/aws-cost-management/aws-cost-optimization/right-sizing

### Azure
- Azure Advisor: azure.microsoft.com/services/advisor
- VM Sizes: docs.microsoft.com/azure/virtual-machines/sizes
- Cost Optimization Best Practices: docs.microsoft.com/azure/architecture/framework/cost

### GCP
- GCP Recommender: cloud.google.com/recommender
- Machine Types: cloud.google.com/compute/docs/machine-types
- Cost Optimization Guide: cloud.google.com/architecture/cost-optimization

### Tools
- AWS Lambda Power Tuning: github.com/alexcasalboni/aws-lambda-power-tuning
- Kubecost: kubecost.com
- Goldilocks: github.com/FairwindsOps/goldilocks
