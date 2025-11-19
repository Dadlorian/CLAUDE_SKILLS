# Spot Instances Reference

## Overview

Spot instances (AWS Spot, Azure Spot VMs, GCP Preemptible/Spot VMs) offer significant discounts (up to 90% vs on-demand) by utilizing spare cloud provider capacity. They are ideal for fault-tolerant, flexible workloads that can handle interruptions.

## What Are Spot Instances?

**Definition**: Spare cloud computing capacity available at steep discounts with the caveat that instances can be interrupted by the cloud provider with short notice.

**Key Characteristics**:
- **Discount**: 70-90% vs on-demand pricing
- **Interruption**: Can be terminated with 2-30 seconds notice
- **Availability**: Subject to capacity availability
- **Pricing**: Variable based on supply and demand
- **Best For**: Fault-tolerant, flexible, stateless workloads

## AWS Spot Instances

### Pricing and Availability

**Pricing Model**:
- Spot price fluctuates based on supply/demand
- You pay current spot price (not a bidding system anymore)
- Prices typically 60-90% lower than on-demand
- Different prices for each instance type and AZ

**Interruption**:
- 2-minute warning via EC2 metadata and EventBridge
- Instance can be stopped, hibernated, or terminated
- Interruption reasons: Capacity, price (if max price set), constraints

**Spot Instance Advisor**:
- Shows average frequency of interruption (< 5%, 5-10%, 10-15%, 15-20%, > 20%)
- Displays average discount vs on-demand
- Historical pricing data
- Helps choose appropriate instance types and AZs

### Spot Request Types

#### One-Time Spot Request
- Request instances once
- When interrupted, request fulfillment ends
- Simple, for single batch jobs

#### Persistent Spot Request
- Re-requests instances if interrupted
- Maintains target capacity
- Good for stateless applications that should restart

#### Spot Fleet
- Request mix of instance types and AZs
- Maintains target capacity
- Diversification strategy
- Allocation strategies: lowestPrice, diversified, capacityOptimized, priceCapacityOptimized

**Spot Fleet Allocation Strategies**:
```
lowestPrice: Cheapest instances (highest interruption risk)
diversified: Spread across pools (better availability)
capacityOptimized: Pools with highest capacity (lowest interruption)
priceCapacityOptimized: Balance price and capacity (recommended)
```

### Spot Interruption Handling

**Interruption Notice**:
- 2-minute warning
- Available via EC2 instance metadata
- CloudWatch Events / EventBridge
- Instance action: Stop, Hibernate, or Terminate

**Graceful Shutdown**:
```bash
# Poll instance metadata for interruption notice
while true; do
  TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
  INTERRUPTION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/spot/instance-action)

  if [ -n "$INTERRUPTION" ]; then
    echo "Spot interruption notice received"
    # Graceful shutdown: stop accepting work, finish current tasks, save state
    graceful_shutdown
    exit 0
  fi
  sleep 5
done
```

**Best Practices**:
- Monitor spot/instance-action endpoint
- Save state/checkpoints regularly
- Design for rapid recovery
- Use hibernation for resumable workloads

### Spot Instance Integration

**EC2 Auto Scaling**:
- Mix spot and on-demand instances
- Define base capacity (on-demand) + additional capacity (spot)
- Automatic replacement on interruption
- Cost-optimized allocation strategy

**ECS with Spot**:
- Spot instances in ECS cluster
- Tasks automatically rescheduled on interruption
- Capacity providers with spot and on-demand mix

**EKS with Spot**:
- Spot instance node groups
- Mix spot and on-demand nodes
- Pod disruption budgets
- Node termination handler for graceful shutdown

**EMR with Spot**:
- Core nodes: on-demand (persistence)
- Task nodes: spot (processing)
- Automatic scaling and replacement

**Batch with Spot**:
- Compute environments with spot
- Automatic retry on interruption
- Mix of spot and on-demand

### Spot Instance Best Practices

**Diversification**:
- Use multiple instance types (similar CPU/memory)
- Spread across multiple AZs
- Reduces interruption risk
- Spot Fleet or Auto Scaling with mixed instances

**Capacity Optimized**:
- Use capacityOptimized or priceCapacityOptimized allocation
- Reduces interruption frequency
- May cost slightly more but better availability

**Checkpointing**:
- Save work in progress regularly
- S3, EFS, or database
- Resume from checkpoint on new instance

**Stateless Design**:
- Don't rely on instance persistence
- Store state externally
- Containers and orchestration work well

**Monitoring**:
- Track interruption rates
- Monitor actual costs vs expected
- Alert on unexpected interruptions
- Use Spot Instance Advisor

## Azure Spot VMs

### Pricing and Eviction

**Pricing Model**:
- Pay current spot price
- Up to 90% discount vs pay-as-you-go
- Pricing varies by VM size and region

**Eviction**:
- 30-second eviction notice (shorter than AWS)
- Evicted when Azure needs capacity back
- Eviction policies: Deallocate or Delete
- Events published to Azure Scheduled Events

**Max Price**:
- Set maximum price you're willing to pay (optional)
- Default: Pay up to pay-as-you-go price
- If spot price exceeds max price, VM evicted
- Most users leave at default (pay-as-you-go price)

### Eviction Policies

**Deallocate** (Default):
- VM deallocated on eviction
- Disks and NICs retained
- Can restart when capacity available
- Stopped VM still incurs disk storage costs

**Delete**:
- VM and associated resources deleted
- No ongoing costs
- Cannot restart same VM
- Good for stateless workloads

### Azure Spot Integration

**VM Scale Sets**:
- Mix spot and regular VMs
- Define max price and eviction policy
- Automatic scaling and replacement
- Ideal for stateless applications

**AKS with Spot**:
- Spot node pools in AKS clusters
- Mix spot and regular node pools
- Taints and tolerations for spot workloads
- Automatic node replacement

**Azure Batch with Spot**:
- Low-priority nodes (similar to spot)
- Automatic retry on eviction
- Cost-effective batch processing

**Azure Container Instances (ACI)**:
- Spot pricing for container groups
- Short-lived, stateless containers

### Eviction Handling

**Scheduled Events API**:
```bash
# Query scheduled events
curl -H Metadata:true http://169.254.169.254/metadata/scheduledevents?api-version=2020-07-01

# Response includes Preempt event for spot eviction
{
  "Events": [{
    "EventType": "Preempt",
    "EventSource": "Platform",
    "NotBefore": "2024-01-15T10:30:00Z"
  }]
}
```

**Best Practices**:
- Poll Scheduled Events API regularly
- Graceful shutdown on Preempt event
- Save state and checkpoints
- Use Azure Monitor for eviction metrics

## GCP Preemptible and Spot VMs

### Two Spot Options

**Preemptible VMs** (Original):
- Up to 80% discount vs on-demand
- Maximum 24-hour lifetime
- 30-second shutdown script notice
- Automatically terminated after 24 hours
- No live migration

**Spot VMs** (Newer, Recommended):
- Up to 91% discount vs on-demand
- No maximum lifetime (can run indefinitely)
- 30-second termination notice
- Otherwise similar to preemptible
- More flexible than preemptible

### Preemption and Termination

**Preemption Triggers**:
- GCP needs capacity for regular instances
- Maintenance events
- 24-hour limit (preemptible VMs only)

**Termination Notice**:
- 30-second shutdown script
- ACPI G3 Mechanical Off signal
- Shutdown script runs (max 30 seconds)
- VM terminated after 30 seconds regardless

**Shutdown Script**:
```bash
#!/bin/bash
# /etc/systemd/system/shutdown-script.service

# Detect preemption
if curl -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/preempted \
  | grep -q TRUE; then

  echo "Preemption detected, graceful shutdown"
  # Save state, finish current task, cleanup
  save_state_and_cleanup
fi
```

### GCP Spot Integration

**Managed Instance Groups (MIGs)**:
- Mix preemptible/spot and regular instances
- Automatic replacement on termination
- Auto-scaling with spot instances
- Regional MIGs for multi-zone distribution

**GKE with Spot**:
- Spot/preemptible node pools
- Mix with regular node pools
- Taints and tolerations for spot workloads
- Automatic node replacement

**Dataflow with Spot**:
- Use preemptible workers for batch pipelines
- Automatic retry and recovery
- Significant cost savings

**Batch Jobs**:
- Cloud Run Jobs with spot (upcoming)
- Compute Engine for batch processing
- Auto-retry on preemption

### Best Practices

**Diversification**:
- Use multiple machine types
- Spread across multiple zones
- Reduces preemption risk

**Checkpointing**:
- Save progress to Cloud Storage or persistent disk
- Resume from checkpoint
- Critical for long-running jobs

**Monitoring**:
- Track preemption rates
- Monitor cost savings
- Alert on excessive preemptions

## Ideal Workloads for Spot Instances

### Perfect Fit Workloads

**Batch Processing**:
- Big data processing (Spark, Hadoop, Presto)
- ETL jobs
- Data analytics
- Video/image processing
- Scientific computing

**CI/CD and Build**:
- Build workers
- Test runners
- Code analysis
- Container image builds

**Machine Learning**:
- Model training (with checkpointing)
- Hyperparameter tuning
- Data preprocessing
- Inference (with fallback)

**Web Crawling and Scraping**:
- Distributed crawlers
- Data collection
- Content indexing

**Stateless Web Applications**:
- Behind load balancer
- Session state externalized
- Auto-scaling groups
- Graceful connection draining

**Rendering**:
- Video rendering
- 3D rendering
- Image processing

**High-Throughput Computing**:
- Monte Carlo simulations
- Genomics analysis
- Financial modeling
- Research computing

### Poor Fit Workloads

**Databases**:
- Primary database instances
- Stateful data stores
- Critical persistence layers
- Exception: Read replicas, analytics replicas

**Long-Running Jobs Without Checkpointing**:
- Jobs that cannot be interrupted
- No intermediate state saved
- All-or-nothing processing

**Strict SLA Applications**:
- Customer-facing apps requiring 99.9%+ uptime
- Real-time processing with no tolerance for delay
- Mission-critical systems

**Singleton Services**:
- Single-instance services without redundancy
- Master/coordinator nodes
- Non-distributed applications

## Spot Instance Strategies

### Diversification Strategy

**Instance Type Diversification**:
```
Instead of: 100 × m5.large
Use: 25 × m5.large + 25 × m5a.large + 25 × m4.large + 25 × t3.large
```

**Availability Zone Diversification**:
```
Instead of: All instances in us-east-1a
Use: 33% us-east-1a + 33% us-east-1b + 33% us-east-1c
```

**Benefits**:
- Lower interruption rate
- Better capacity availability
- More stable total capacity

### Hybrid Strategy (Spot + On-Demand)

**Layered Approach**:
```
Base Layer (50%): On-demand instances (guaranteed capacity)
Variable Layer (50%): Spot instances (cost optimization)
```

**Auto Scaling Configuration**:
```
Base capacity: 10 on-demand instances (always running)
Scale-out: Spot instances (cost-effective growth)
Scale-in: Remove spot first (preserve base)
```

**Benefits**:
- Guaranteed baseline capacity
- Cost optimization on scale
- Risk mitigation

### Capacity Optimized Strategy

**Prioritize Availability Over Price**:
- Use capacity-optimized allocation
- Choose instance types with low interruption rates
- Slightly higher cost but better availability

**When to Use**:
- Workloads sensitive to interruptions
- Need high availability within spot
- Balance cost and stability

### Checkpointing Strategy

**Regular State Saves**:
```
Every N minutes: Save progress to persistent storage
On interruption: Save final state
On restart: Resume from last checkpoint
```

**Storage Options**:
- S3 / Cloud Storage / Blob Storage (cheap, durable)
- EFS / Filestore (shared file system)
- Persistent disks (attached to spot instances)
- Database (for small state)

**Benefits**:
- Minimize lost work
- Fast recovery
- Support long-running jobs on spot

### Fallback Strategy

**Spot-to-On-Demand Failover**:
```
1. Try to launch spot instance
2. If unavailable or interrupted repeatedly: fallback to on-demand
3. Return to spot when capacity available
```

**Implementation**:
- AWS Auto Scaling: SpotMaxPrice, OnDemandBaseCapacity
- Azure: VM Scale Sets with priority mix
- GCP: MIGs with instance templates

## Cost Analysis and ROI

### Cost Savings Calculation

**Example**:
```
Workload: 100 m5.large instances (24x7)
On-demand cost: $0.096/hour × 100 × 730 hours = $7,008/month
Spot cost (85% discount): $0.0144/hour × 100 × 730 = $1,051/month
Monthly savings: $5,957 (85%)
Annual savings: $71,484
```

**With Interruptions**:
```
Spot uptime: 95% (5% interruption time)
Effective spot hours: 100 × 730 × 0.95 = 69,350 hours
Fallback on-demand: 100 × 730 × 0.05 = 3,650 hours

Spot cost: 69,350 × $0.0144 = $998
Fallback cost: 3,650 × $0.096 = $350
Total cost: $1,348
Savings vs on-demand: 81%
```

### TCO Considerations

**Additional Costs**:
- Engineering time for spot-aware architecture
- Monitoring and tooling
- Potential lost work from interruptions
- Data transfer costs (restarts, checkpointing)

**Savings Beyond Compute**:
- Reduced RI/SP commitment needed
- Lower baseline capacity requirements
- More efficient resource utilization

**Break-Even Analysis**:
```
Implementation cost: $50,000 (eng time, tooling)
Monthly savings: $5,000
Break-even: 10 months
```

## Spot Instance Monitoring

### Key Metrics

**Interruption Metrics**:
- Interruption rate (interruptions per instance-hour)
- Interruption frequency by instance type
- Time to replacement
- Failed placement requests

**Cost Metrics**:
- Actual spot price paid vs on-demand
- Savings realized
- Spot vs on-demand ratio
- Total cost with fallback

**Availability Metrics**:
- Spot instance uptime percentage
- Capacity availability
- Fulfillment rate

**Performance Metrics**:
- Job completion time
- Throughput
- Work lost due to interruptions
- Recovery time

### Monitoring Tools

**AWS**:
- CloudWatch Metrics: SpotInstanceRequests, SpotInterruptions
- EventBridge: Spot instance interruption notices
- Spot Instance Advisor: Historical interruption data
- Cost Explorer: Spot cost analysis

**Azure**:
- Azure Monitor: Eviction metrics
- Azure Advisor: Spot recommendations
- Scheduled Events: Eviction notices
- Cost Management: Spot cost tracking

**GCP**:
- Cloud Monitoring: Preemption metrics
- Logs Explorer: Preemption events
- Cost Management: Spot cost analysis

**Third-Party**:
- Datadog, New Relic: Custom metrics and dashboards
- Spot.io: Specialized spot optimization
- CloudHealth: Multi-cloud spot analytics

## Advanced Spot Patterns

### Spot with Kubernetes

**Node Pools**:
```yaml
# Mix of spot and on-demand nodes
Spot Node Pool:
  - Labels: workload-type=batch
  - Taints: spot=true:NoSchedule

On-Demand Node Pool:
  - Labels: workload-type=critical
```

**Pod Tolerations**:
```yaml
tolerations:
- key: "spot"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
```

**Pod Disruption Budgets**:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

**Tools**:
- AWS Node Termination Handler
- Azure Spot Eviction Handler
- GKE node auto-repair

### Spot for Batch Processing

**AWS Batch**:
```
Compute Environment:
  - Type: SPOT
  - Bid percentage: 100% (pay up to on-demand price)
  - Instance types: [optimal] or [m5.large, m5.xlarge, c5.large]

Job Queue:
  - Priority: Lower for spot, higher for on-demand
```

**Retry Strategy**:
```json
{
  "retryStrategy": {
    "attempts": 3,
    "evaluateOnExit": [{
      "onStatusReason": "Host EC2*",
      "action": "RETRY"
    }]
  }
}
```

### Spot for Stateless Web Apps

**Architecture**:
```
Application Load Balancer
├── Target Group 1 (On-Demand Instances) - Priority
└── Target Group 2 (Spot Instances) - Lower Priority

Auto Scaling:
- Base: 2 on-demand (minimum capacity)
- Scale: Spot instances (cost optimization)
```

**Connection Draining**:
- 120-second drain time
- Gracefully finish in-flight requests
- Handle interruptions without errors

## Best Practices Summary

1. **Start Small**: Begin with non-critical workloads, expand gradually
2. **Diversify**: Multiple instance types and AZs
3. **Checkpoint**: Save state regularly for long-running jobs
4. **Monitor**: Track interruptions, costs, performance
5. **Graceful Shutdown**: Handle interruption notices properly
6. **Test**: Simulate interruptions in dev/test
7. **Document**: Spot-aware architecture and procedures
8. **Automate**: Use managed services and orchestration
9. **Fallback**: Have on-demand capacity as backup
10. **Continuous Optimization**: Review and refine spot strategy regularly

## Resources

### AWS Spot
- Spot Instances: aws.amazon.com/ec2/spot
- Spot Best Practices: docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html
- Spot Instance Advisor: aws.amazon.com/ec2/spot/instance-advisor

### Azure Spot
- Azure Spot VMs: azure.microsoft.com/services/virtual-machines/spot
- Spot Documentation: docs.microsoft.com/azure/virtual-machines/spot-vms

### GCP Spot
- Preemptible VMs: cloud.google.com/compute/docs/instances/preemptible
- Spot VMs: cloud.google.com/compute/docs/instances/spot

### Tools
- Spot.io: spot.io
- AWS Node Termination Handler: github.com/aws/aws-node-termination-handler
