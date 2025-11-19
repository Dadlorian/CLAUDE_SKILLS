# EC2 Instance Types Reference

## Instance Families Overview

### General Purpose (Balanced CPU, Memory, Network)
**Use Cases**: Web servers, code repositories, development environments, small databases

#### T Family (Burstable Performance)
- **T4g** (AWS Graviton2): Up to 40% better price-performance, up to 32 vCPUs, 128 GiB RAM
- **T3/T3a**: Up to 8 vCPUs, 32 GiB RAM, unlimited mode available
- **T2**: Previous generation, up to 8 vCPUs, 32 GiB RAM
- **Best For**: Variable workloads, development, testing
- **CPU Credits**: Accumulate during low usage, spend during bursts
- **Pricing**: 20-30% lower than M instances

#### M Family (General Purpose)
- **M7g** (Graviton3): Up to 64 vCPUs, 256 GiB RAM, 20% better performance than M6g
- **M7i** (Sapphire Rapids): Up to 192 vCPUs, 768 GiB RAM, DDR5 memory
- **M6g** (Graviton2): Up to 64 vCPUs, 256 GiB RAM, 40% better price-performance
- **M6i/M6a**: Up to 128 vCPUs, 512 GiB RAM, 15% better performance than M5
- **M5/M5a/M5n**: Up to 96 vCPUs, 384 GiB RAM, proven workloads
- **Best For**: Application servers, enterprise applications, gaming servers
- **Network**: Up to 100 Gbps, ENA enabled, EFA on some sizes

### Compute Optimized (High Performance Processors)
**Use Cases**: Batch processing, media transcoding, HPC, gaming, scientific modeling

#### C Family (Compute Intensive)
- **C7g** (Graviton3): Up to 64 vCPUs, 128 GiB RAM, 25% better performance than C6g
- **C7i** (Sapphire Rapids): Up to 192 vCPUs, 384 GiB RAM, DDR5, fastest x86
- **C6g/C6gn** (Graviton2): Up to 64 vCPUs, 128 GiB RAM, C6gn with 100 Gbps network
- **C6i/C6a**: Up to 128 vCPUs, 256 GiB RAM, 15% better than C5
- **C5/C5n**: Up to 96 vCPUs, 192 GiB RAM, C5n optimized for network
- **Best For**: High-performance web servers, scientific modeling, ad serving
- **vCPU to Memory Ratio**: 1:2 (higher compute density)

#### Hpc Family (High Performance Computing)
- **Hpc7g** (Graviton3E): 64 vCPUs, 128 GiB RAM, optimized for HPC
- **Hpc6id** (Xeon): 64 vCPUs, 1024 GiB RAM, 3.2 TB local NVMe
- **Best For**: Computational fluid dynamics, weather simulation, molecular dynamics
- **Network**: EFA enabled, ultra-low latency

### Memory Optimized (High Memory to CPU Ratio)
**Use Cases**: In-memory databases, real-time big data analytics, in-memory caches

#### R Family (Memory Intensive)
- **R7g** (Graviton3): Up to 64 vCPUs, 512 GiB RAM, DDR5
- **R7i** (Sapphire Rapids): Up to 192 vCPUs, 1536 GiB RAM, DDR5
- **R6g** (Graviton2): Up to 64 vCPUs, 512 GiB RAM, 40% better price-performance
- **R6i/R6a**: Up to 128 vCPUs, 1024 GiB RAM, 15% better than R5
- **R5/R5a/R5n**: Up to 96 vCPUs, 768 GiB RAM
- **vCPU to Memory Ratio**: 1:8
- **Best For**: SAP HANA, Redis, Memcached, Apache Spark

#### X Family (Extreme Memory)
- **X2gd** (Graviton2): Up to 64 vCPUs, 1024 GiB RAM, lowest cost per GiB
- **X2idn/X2iedn**: Up to 128 vCPUs, 2048 GiB RAM, up to 8 TB NVMe SSD
- **X2iezn**: Up to 48 vCPUs, 1536 GiB RAM, all-core turbo 4.5 GHz
- **X1e/X1**: Previous generation, up to 3904 GiB RAM
- **vCPU to Memory Ratio**: 1:16 to 1:32
- **Best For**: SAP HANA, Apache Spark, Presto, high-performance databases

#### High Memory (u-*)
- **u-6tb1** to **u-24tb1**: 448-448 vCPUs, 6-24 TiB RAM
- **Purpose-built**: For SAP HANA workloads
- **Dedicated Hosts**: Available by request
- **Best For**: Large in-memory databases, mission-critical SAP HANA

#### Z Family (High Frequency)
- **Z1d**: Up to 48 vCPUs, 384 GiB RAM, 4.0 GHz all-core turbo
- **Best For**: Electronic Design Automation, gaming, single-threaded workloads
- **Features**: High single-thread performance, large local NVMe storage

### Accelerated Computing (GPU, FPGA, Inference)
**Use Cases**: Machine learning, graphics processing, data pattern matching

#### P Family (GPU General Purpose)
- **P5** (H100 GPUs): 192 vCPUs, 2048 GiB RAM, 8x NVIDIA H100 GPUs
- **P4d** (A100 GPUs): 96 vCPUs, 1152 GiB RAM, 8x NVIDIA A100 (40/80GB)
- **P3** (V100 GPUs): Up to 64 vCPUs, 768 GiB RAM, up to 8x V100
- **GPU Memory**: Up to 640 GB (P5)
- **Best For**: ML training, HPC, computational fluid dynamics
- **Network**: 3200 Gbps EFA on P5

#### G Family (GPU Graphics Intensive)
- **G5g** (T4G GPU + Graviton2): Up to 64 vCPUs, 256 GiB RAM, AWS GPUs
- **G5** (A10G GPUs): Up to 192 vCPUs, 768 GiB RAM, up to 8x A10G
- **G4dn** (T4 GPUs): Up to 96 vCPUs, 384 GiB RAM, up to 8x T4
- **G4ad** (Radeon Pro V520): Up to 64 vCPUs, 256 GiB RAM, up to 4 GPUs
- **Best For**: Graphics workstations, rendering, game streaming, ML inference

#### Inf Family (AWS Inferentia)
- **Inf2** (Inferentia2): Up to 192 vCPUs, 768 GiB RAM, up to 12 chips
- **Inf1** (Inferentia1): Up to 96 vCPUs, 192 GiB RAM, up to 16 chips
- **Best For**: ML inference, 70% lower cost than GPU-based instances
- **Performance**: Up to 4x higher throughput than Inf1

#### Trn Family (AWS Trainium)
- **Trn1** (Trainium): Up to 128 vCPUs, 512 GiB RAM, up to 16 chips
- **Best For**: ML training, 50% cost savings over GPU instances
- **Frameworks**: PyTorch, TensorFlow via AWS Neuron SDK

#### DL Family (Deep Learning)
- **DL1** (Gaudi accelerators): 96 vCPUs, 768 GiB RAM, 8x Gaudi accelerators
- **Best For**: Deep learning training, 40% better price-performance than P4d
- **Network**: 400 Gbps EFA

#### F Family (FPGA)
- **F1**: Up to 64 vCPUs, 976 GiB RAM, up to 8 FPGAs
- **FPGA**: Xilinx Virtex UltraScale+ VU9P
- **Best For**: Genomics, financial analytics, real-time video processing
- **Features**: Reconfigurable hardware, custom acceleration

#### VT Family (Video Transcoding)
- **VT1**: 96 vCPUs, 192 GiB RAM, up to 8x Xilinx U30 accelerators
- **Best For**: Live video transcoding, broadcast, streaming
- **Performance**: 30% better price-performance than GPU instances

### Storage Optimized (High Sequential I/O, Local Storage)
**Use Cases**: NoSQL databases, data warehousing, distributed file systems, log processing

#### I Family (High Random I/O, NVMe SSD)
- **I4g** (Graviton2): Up to 64 vCPUs, 512 GiB RAM, up to 30 TB NVMe
- **I4i** (Intel): Up to 128 vCPUs, 1024 GiB RAM, up to 30 TB NVMe
- **I3/I3en**: Up to 96 vCPUs, 768 GiB RAM, up to 60 TB NVMe (I3en)
- **IOPS**: Up to 2 million random read IOPS
- **Best For**: NoSQL databases (Cassandra, MongoDB), Elasticsearch, analytics

#### D Family (Dense HDD Storage)
- **D3/D3en**: Up to 96 vCPUs, 768 GiB RAM, up to 336 TB HDD
- **D2**: Previous generation, up to 36 vCPUs, 244 GiB RAM, up to 48 TB HDD
- **Throughput**: Up to 6.2 GB/s (D3en)
- **Best For**: Distributed file systems (HDFS, MapR), data warehouses

#### H Family (HDD, High Disk Throughput)
- **H1**: Up to 64 vCPUs, 256 GiB RAM, up to 16 TB HDD
- **Throughput**: 2.8 GB/s sequential reads
- **Best For**: MapReduce, distributed file systems, log processing

#### Im4gn/Is4gen (AWS Graviton2 + SSD)
- **Im4gn**: Up to 64 vCPUs, 1024 GiB RAM, up to 30 TB NVMe
- **Is4gen**: Up to 96 vCPUs, 768 GiB RAM, up to 30 TB NVMe
- **Best For**: Storage-optimized with better price-performance (Graviton2)

## Instance Size Patterns

### Naming Convention
```
[Family][Generation][Additional Capabilities].[Size]

Examples:
- m7g.xlarge: M family, 7th gen, Graviton (g), xlarge size
- c6i.2xlarge: C family, 6th gen, Intel (i), 2xlarge size
- r5n.4xlarge: R family, 5th gen, network optimized (n), 4xlarge size
```

### Size Multipliers
- nano: 0.25x (T instances only)
- micro: 0.5x (T instances only)
- small: 1x base unit
- medium: 2x
- large: 4x
- xlarge: 8x
- 2xlarge: 16x
- 4xlarge: 32x
- 8xlarge: 64x
- 12xlarge: 96x
- 16xlarge: 128x
- 24xlarge: 192x
- 32xlarge: 256x (largest for most families)
- metal: Bare metal, no virtualization overhead

### Additional Capability Suffixes
- **a**: AMD processors
- **d**: NVMe SSD instance store
- **n**: Network optimized (up to 100 Gbps)
- **e**: Extra storage or RAM
- **g**: AWS Graviton processors
- **i**: Intel processors
- **z**: High frequency
- **flex**: Flexible instance size

## Specialized Instance Features

### AWS Nitro System
**Benefits**: Better performance, security, innovation velocity
**Features**:
- Dedicated hardware for networking and storage
- NitroTPM for attestation
- NitroEnclaves for confidential computing
- Near bare-metal performance

### Enhanced Networking
**Elastic Network Adapter (ENA)**: Up to 100 Gbps
**Elastic Fabric Adapter (EFA)**: Low-latency, high-throughput for HPC/ML
**SR-IOV**: Single Root I/O Virtualization for network performance

### Placement Groups
**Cluster**: Low-latency, high-throughput (same AZ)
**Partition**: Spread across logical partitions (different hardware)
**Spread**: Each instance on distinct hardware (max 7 per AZ)

### Instance Store (Ephemeral Storage)
**Characteristics**:
- Physically attached to host
- Lost on stop/terminate/hardware failure
- No additional cost
- Sub-millisecond latency
**Use Cases**: Temporary data, cache, buffers, scratch data

## Pricing Models

### On-Demand
**Pricing**: Per-second billing (60-second minimum)
**Use Cases**: Short-term, unpredictable workloads, dev/test
**Commitment**: None
**Savings**: Baseline (0%)

### Reserved Instances
**Terms**: 1-year or 3-year
**Payment Options**: All Upfront, Partial Upfront, No Upfront
**Types**: Standard (up to 72% savings), Convertible (up to 66% savings, exchangeable)
**Scope**: Regional or Zonal
**Best For**: Steady-state workloads

### Savings Plans
**Types**:
- Compute Savings Plans: Up to 66% savings, any instance family/region/OS
- EC2 Instance Savings Plans: Up to 72% savings, specific family/region
**Flexibility**: Change instance size, OS, tenancy, region (Compute only)
**Commitment**: $/hour for 1 or 3 years

### Spot Instances
**Discount**: Up to 90% off On-Demand
**Interruption**: 2-minute warning when AWS needs capacity back
**Use Cases**: Fault-tolerant, flexible, batch processing, big data
**Strategies**: Diversification across types/AZs, Spot Fleet, EC2 Fleet

### Dedicated Hosts
**Use Cases**: License compliance (BYOL), regulatory requirements
**Pricing**: Per-host hourly rate
**Features**: Socket/core visibility, host affinity, placement control

### Dedicated Instances
**Isolation**: Single-tenant hardware
**Pricing**: $2/hour per-region fee + instance charges
**Difference from Hosts**: No host-level visibility or control

## Selection Strategy

### Performance Requirements
1. **CPU**: Compute-optimized (C) for CPU-bound workloads
2. **Memory**: Memory-optimized (R, X, Z) for in-memory operations
3. **Storage**: Storage-optimized (I, D, H) for I/O intensive workloads
4. **Network**: Network-optimized variants (n suffix) for high throughput
5. **GPU**: Accelerated (P, G, Inf, Trn) for ML/graphics

### Cost Optimization
1. **Right-size**: Start small, scale up based on metrics
2. **Graviton**: 40% better price-performance for compatible workloads
3. **AMD**: Often 10% cheaper than Intel equivalents
4. **Burstable**: T instances for variable workloads
5. **Spot**: Up to 90% savings for fault-tolerant workloads

### Architecture Considerations
1. **Multi-AZ**: Use placement groups for low latency
2. **HPC**: P5, Hpc7g with EFA for tightly coupled workloads
3. **Microservices**: General purpose (M, T) with auto-scaling
4. **Databases**: Memory-optimized (R, X) with provisioned IOPS EBS
5. **Big Data**: Storage-optimized (I, D) with instance store

### Generation Selection
- **Latest (7th gen)**: Best performance, DDR5, newest features
- **Current (6th gen)**: Proven, wide availability, good price-performance
- **Previous (5th gen)**: Lower cost, still well-supported
- **Graviton**: Best price-performance for compatible workloads

## Instance Metadata Service (IMDS)

### IMDSv2 (Session-oriented, recommended)
```bash
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
```

### Common Metadata Endpoints
- `/latest/meta-data/instance-id`: Instance ID
- `/latest/meta-data/instance-type`: Instance type
- `/latest/meta-data/local-ipv4`: Private IP
- `/latest/meta-data/public-ipv4`: Public IP
- `/latest/meta-data/placement/availability-zone`: AZ
- `/latest/user-data`: User data script
- `/latest/dynamic/instance-identity/document`: Instance identity

## Best Practices

1. **Use Latest Generation**: Better price-performance ratio
2. **Enable Detailed Monitoring**: 1-minute CloudWatch metrics
3. **Right-Size Regularly**: Review CloudWatch metrics monthly
4. **Use Auto Scaling**: Match capacity to demand
5. **Leverage Spot for Fault-Tolerant**: 90% cost savings
6. **Consider Graviton**: 40% better price-performance
7. **Use Savings Plans**: Flexible commitment-based savings
8. **Enable IMDSv2**: Improved security
9. **Tag Resources**: Cost allocation, automation, governance
10. **Test Before Committing**: Validate performance before Reserved Instances

## Practical Implementation Examples

### Example 1: Launch EC2 Instance with Best Practices (AWS CLI)

```bash
# Launch EC2 instance with security best practices
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name my-key-pair \
  --security-group-ids sg-0123456789abcdef0 \
  --subnet-id subnet-0123456789abcdef0 \
  --iam-instance-profile Name=EC2-SSM-Role \
  --metadata-options "HttpTokens=required,HttpPutResponseHopLimit=1,HttpEndpoint=enabled" \
  --monitoring Enabled=true \
  --block-device-mappings '[
    {
      "DeviceName": "/dev/xvda",
      "Ebs": {
        "VolumeSize": 30,
        "VolumeType": "gp3",
        "Iops": 3000,
        "Throughput": 125,
        "Encrypted": true,
        "DeleteOnTermination": true
      }
    }
  ]' \
  --tag-specifications '
    ResourceType=instance,Tags=[
      {Key=Name,Value=web-server-prod},
      {Key=Environment,Value=production},
      {Key=Application,Value=web-app},
      {Key=CostCenter,Value=engineering},
      {Key=ManagedBy,Value=terraform}
    ]
  ' \
  --user-data file://user-data.sh \
  --credit-specification CpuCredits=unlimited

# user-data.sh - Bootstrap script
#!/bin/bash
yum update -y
yum install -y amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c ssm:CloudWatch-Config
```

### Example 2: Launch Spot Instance with Auto Scaling (Python Boto3)

```python
import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2', region_name='us-east-1')

def create_spot_instance_request():
    """
    Create spot instance request with proper configuration
    """
    # Get current spot price to set intelligent max price
    spot_price_history = ec2.describe_spot_price_history(
        InstanceTypes=['c6i.xlarge'],
        ProductDescriptions=['Linux/UNIX'],
        StartTime=datetime.now() - timedelta(hours=24),
        MaxResults=1
    )

    current_spot_price = float(spot_price_history['SpotPriceHistory'][0]['SpotPrice'])
    max_price = str(current_spot_price * 1.2)  # 20% buffer

    launch_specification = {
        'ImageId': 'ami-0c55b159cbfafe1f0',
        'InstanceType': 'c6i.xlarge',
        'KeyName': 'my-key-pair',
        'SecurityGroupIds': ['sg-0123456789abcdef0'],
        'SubnetId': 'subnet-0123456789abcdef0',
        'IamInstanceProfile': {
            'Name': 'EC2-Spot-Fleet-Role'
        },
        'BlockDeviceMappings': [
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': 50,
                    'VolumeType': 'gp3',
                    'Encrypted': True,
                    'DeleteOnTermination': True
                }
            }
        ],
        'Monitoring': {'Enabled': True},
        'UserData': '''#!/bin/bash
            yum update -y
            yum install -y docker
            systemctl start docker
            docker run -d -p 80:80 my-app:latest
        '''
    }

    response = ec2.request_spot_instances(
        SpotPrice=max_price,
        InstanceCount=1,
        Type='one-time',  # or 'persistent'
        LaunchSpecification=launch_specification,
        InstanceInterruptionBehavior='terminate',  # or 'stop', 'hibernate'
        TagSpecifications=[
            {
                'ResourceType': 'spot-instances-request',
                'Tags': [
                    {'Key': 'Name', 'Value': 'batch-processor'},
                    {'Key': 'Environment', 'Value': 'production'},
                    {'Key': 'Workload', 'Value': 'batch'}
                ]
            }
        ]
    )

    request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
    print(f"Spot instance request created: {request_id}")
    print(f"Max price: ${max_price}/hour (current: ${current_spot_price}/hour)")

    return request_id

def create_spot_fleet():
    """
    Create diversified spot fleet for high availability
    """
    response = ec2.request_spot_fleet(
        SpotFleetRequestConfig={
            'IamFleetRole': 'arn:aws:iam::123456789012:role/aws-ec2-spot-fleet-tagging-role',
            'AllocationStrategy': 'diversified',  # or 'lowestPrice', 'capacityOptimized'
            'TargetCapacity': 10,
            'SpotPrice': '0.50',
            'LaunchSpecifications': [
                # Diversify across instance types and AZs
                {
                    'ImageId': 'ami-0c55b159cbfafe1f0',
                    'InstanceType': 'c6i.xlarge',
                    'KeyName': 'my-key-pair',
                    'SecurityGroups': [{'GroupId': 'sg-0123456789abcdef0'}],
                    'SubnetId': 'subnet-us-east-1a',
                    'WeightedCapacity': 1.0
                },
                {
                    'ImageId': 'ami-0c55b159cbfafe1f0',
                    'InstanceType': 'c5.xlarge',
                    'KeyName': 'my-key-pair',
                    'SecurityGroups': [{'GroupId': 'sg-0123456789abcdef0'}],
                    'SubnetId': 'subnet-us-east-1b',
                    'WeightedCapacity': 1.0
                },
                {
                    'ImageId': 'ami-0c55b159cbfafe1f0',
                    'InstanceType': 'c6a.xlarge',
                    'KeyName': 'my-key-pair',
                    'SecurityGroups': [{'GroupId': 'sg-0123456789abcdef0'}],
                    'SubnetId': 'subnet-us-east-1c',
                    'WeightedCapacity': 1.0
                }
            ],
            'Type': 'maintain',  # Maintain target capacity
            'ReplaceUnhealthyInstances': True,
            'TerminateInstancesWithExpiration': True,
            'TagSpecifications': [
                {
                    'ResourceType': 'spot-fleet-request',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'web-fleet'},
                        {'Key': 'Environment', 'Value': 'production'}
                    ]
                }
            ]
        }
    )

    print(f"Spot fleet created: {response['SpotFleetRequestId']}")
    return response['SpotFleetRequestId']

# Usage
spot_request_id = create_spot_instance_request()
# fleet_id = create_spot_fleet()
```

### Example 3: Right-Sizing Analysis

```python
import boto3
from datetime import datetime, timedelta
import statistics

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
ec2 = boto3.client('ec2', region_name='us-east-1')

def analyze_instance_utilization(instance_id, days=7):
    """
    Analyze EC2 instance utilization for right-sizing recommendations
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    # Get CPU utilization
    cpu_metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,  # 1 hour
        Statistics=['Average', 'Maximum']
    )

    # Get network metrics
    network_in = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='NetworkIn',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average', 'Maximum']
    )

    # Get instance details
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    instance_type = instance['Reservations'][0]['Instances'][0]['InstanceType']

    # Calculate statistics
    cpu_values = [point['Average'] for point in cpu_metrics['Datapoints']]
    cpu_avg = statistics.mean(cpu_values) if cpu_values else 0
    cpu_p95 = statistics.quantiles(cpu_values, n=20)[18] if len(cpu_values) > 20 else 0

    network_values = [point['Average'] for point in network_in['Datapoints']]
    network_avg = statistics.mean(network_values) if network_values else 0

    # Right-sizing recommendations
    recommendation = {
        'instance_id': instance_id,
        'current_type': instance_type,
        'cpu_average': cpu_avg,
        'cpu_p95': cpu_p95,
        'network_avg_mbps': network_avg / (1024 * 1024 / 8),
        'recommendation': None,
        'potential_savings': None
    }

    # Simple right-sizing logic
    if cpu_avg < 10 and cpu_p95 < 20:
        recommendation['recommendation'] = 'Downsize to smaller instance type'
        recommendation['action'] = 'Consider t3.micro or t3.small'
    elif cpu_avg < 30 and cpu_p95 < 50:
        recommendation['recommendation'] = 'Instance is underutilized'
        recommendation['action'] = 'Consider smaller instance or burstable type'
    elif cpu_p95 > 80:
        recommendation['recommendation'] = 'Instance may be overutilized'
        recommendation['action'] = 'Consider larger instance type'
    else:
        recommendation['recommendation'] = 'Instance is appropriately sized'
        recommendation['action'] = 'No action needed'

    return recommendation

def bulk_right_sizing_analysis(tag_key='Environment', tag_value='production'):
    """
    Analyze all instances with specific tag for right-sizing
    """
    # Get all instances with tag
    instances = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    recommendations = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(f"Analyzing {instance_id}...")

            analysis = analyze_instance_utilization(instance_id)
            recommendations.append(analysis)

    # Print summary
    print("\n=== RIGHT-SIZING RECOMMENDATIONS ===")
    for rec in recommendations:
        print(f"\nInstance: {rec['instance_id']} ({rec['current_type']})")
        print(f"  CPU Average: {rec['cpu_average']:.2f}%")
        print(f"  CPU P95: {rec['cpu_p95']:.2f}%")
        print(f"  Recommendation: {rec['recommendation']}")
        print(f"  Action: {rec['action']}")

    return recommendations

# Usage
recommendations = bulk_right_sizing_analysis('Environment', 'production')
```

### Example 4: Auto Scaling Group with Mixed Instances

```python
import boto3

autoscaling = boto3.client('autoscaling', region_name='us-east-1')

def create_mixed_instances_asg():
    """
    Create Auto Scaling Group with mixed instance types for cost optimization
    """
    response = autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='web-app-asg',
        MixedInstancesPolicy={
            'LaunchTemplate': {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': 'web-app-template',
                    'Version': '$Latest'
                },
                'Overrides': [
                    {
                        'InstanceType': 'c6i.large',
                        'WeightedCapacity': '1'
                    },
                    {
                        'InstanceType': 'c6a.large',
                        'WeightedCapacity': '1'
                    },
                    {
                        'InstanceType': 'c6g.large',  # Graviton2
                        'WeightedCapacity': '1'
                    },
                    {
                        'InstanceType': 'c5.large',
                        'WeightedCapacity': '1'
                    }
                ]
            },
            'InstancesDistribution': {
                'OnDemandAllocationStrategy': 'prioritized',
                'OnDemandBaseCapacity': 2,  # Minimum on-demand instances
                'OnDemandPercentageAboveBaseCapacity': 20,  # 20% on-demand, 80% spot
                'SpotAllocationStrategy': 'capacity-optimized',  # or 'lowest-price'
                'SpotInstancePools': 4,
                'SpotMaxPrice': ''  # Use on-demand price as max
            }
        },
        MinSize=2,
        MaxSize=20,
        DesiredCapacity=4,
        DefaultCooldown=300,
        HealthCheckType='ELB',
        HealthCheckGracePeriod=300,
        VPCZoneIdentifier='subnet-1,subnet-2,subnet-3',
        TargetGroupARNs=[
            'arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/abc123'
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'web-app-instance',
                'PropagateAtLaunch': True
            },
            {
                'Key': 'Environment',
                'Value': 'production',
                'PropagateAtLaunch': True
            }
        ]
    )

    print(f"Auto Scaling Group created: web-app-asg")

    # Add target tracking scaling policy
    autoscaling.put_scaling_policy(
        AutoScalingGroupName='web-app-asg',
        PolicyName='target-tracking-cpu',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'ASGAverageCPUUtilization'
            },
            'TargetValue': 70.0,
            'ScaleInCooldown': 300,
            'ScaleOutCooldown': 60
        }
    )

    print("Target tracking scaling policy added")

    return response

# Usage
create_mixed_instances_asg()
```

### Example 5: Graviton Migration Assessment

```python
import boto3

def assess_graviton_compatibility(instance_id):
    """
    Assess if an instance can be migrated to Graviton (ARM)
    """
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')

    # Get instance details
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    instance_data = instance['Reservations'][0]['Instances'][0]

    current_type = instance_data['InstanceType']
    architecture = instance_data['Architecture']

    assessment = {
        'instance_id': instance_id,
        'current_type': current_type,
        'current_architecture': architecture,
        'graviton_compatible': False,
        'recommended_graviton_type': None,
        'estimated_savings': None,
        'compatibility_notes': []
    }

    # Check if already on Graviton
    if 'g' in current_type.split('.')[0][-1]:
        assessment['compatibility_notes'].append("Already running on Graviton")
        return assessment

    # Map current instance to Graviton equivalent
    graviton_mapping = {
        'm6i': 'm7g',
        'm6a': 'm7g',
        'm5': 'm6g',
        'c6i': 'c7g',
        'c6a': 'c7g',
        'c5': 'c6g',
        'r6i': 'r7g',
        'r6a': 'r7g',
        'r5': 'r6g',
        't3': 't4g',
        't3a': 't4g'
    }

    family = current_type.split('.')[0]
    size = current_type.split('.')[1]

    if family in graviton_mapping:
        graviton_family = graviton_mapping[family]
        assessment['recommended_graviton_type'] = f"{graviton_family}.{size}"
        assessment['graviton_compatible'] = True
        assessment['estimated_savings'] = "20-40%"

        assessment['compatibility_notes'].extend([
            "Graviton processors use ARM architecture",
            "Requires ARM-compatible AMI",
            "Application must be compiled for ARM64",
            "Most modern software supports ARM64",
            "Test thoroughly before production migration"
        ])
    else:
        assessment['compatibility_notes'].append(
            f"No direct Graviton equivalent for {current_type}"
        )

    return assessment

def generate_migration_plan(instance_ids):
    """
    Generate Graviton migration plan for multiple instances
    """
    migration_plan = []

    for instance_id in instance_ids:
        assessment = assess_graviton_compatibility(instance_id)
        if assessment['graviton_compatible']:
            migration_plan.append(assessment)

    print("=== GRAVITON MIGRATION PLAN ===")
    total_instances = len(migration_plan)
    print(f"Compatible instances: {total_instances}/{len(instance_ids)}")

    for plan in migration_plan:
        print(f"\nInstance: {plan['instance_id']}")
        print(f"  Current: {plan['current_type']}")
        print(f"  Recommended: {plan['recommended_graviton_type']}")
        print(f"  Estimated savings: {plan['estimated_savings']}")
        print(f"  Notes:")
        for note in plan['compatibility_notes']:
            print(f"    - {note}")

    return migration_plan

# Usage
instances = ['i-0123456789abcdef0', 'i-0abcdef123456789']
migration_plan = generate_migration_plan(instances)
```

### Example 6: Reserved Instance Purchase Recommendation

```python
import boto3
from datetime import datetime, timedelta
from collections import Counter

ec2 = boto3.client('ec2', region_name='us-east-1')
ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer

def analyze_instance_usage(days=30):
    """
    Analyze instance usage patterns for RI recommendations
    """
    # Get all running instances
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    # Count instance types
    instance_types = []
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime'].replace(tzinfo=None)
            age_days = (datetime.now() - launch_time).days

            # Only consider instances running > 30 days
            if age_days >= days:
                instance_types.append(instance['InstanceType'])

    # Calculate recommendations
    type_counts = Counter(instance_types)

    recommendations = []
    for instance_type, count in type_counts.most_common():
        # Get on-demand pricing (simplified - use AWS Price List API in production)
        recommendation = {
            'instance_type': instance_type,
            'count': count,
            'term': '1-year' if count >= 2 else 'No RI',
            'payment_option': 'Partial Upfront',
            'estimated_savings': f"{count * 0.30 * 100:.0f}%",  # Rough estimate
            'action': 'Purchase Reserved Instance' if count >= 2 else 'Continue on-demand'
        }
        recommendations.append(recommendation)

    return recommendations

def get_ri_purchase_recommendations():
    """
    Get RI purchase recommendations from AWS Cost Explorer
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    response = ce.get_reservation_purchase_recommendation(
        Service='Amazon Elastic Compute Cloud - Compute',
        LookbackPeriodInDays='THIRTY_DAYS',
        TermInYears='ONE_YEAR',
        PaymentOption='PARTIAL_UPFRONT'
    )

    recommendations = response['Recommendations']

    print("=== RESERVED INSTANCE RECOMMENDATIONS ===")
    for rec in recommendations:
        details = rec['RecommendationDetails'][0]
        print(f"\nInstance Type: {details.get('InstanceType', 'N/A')}")
        print(f"  Quantity: {details.get('RecommendedNumberOfInstancesToPurchase', 0)}")
        print(f"  Estimated Monthly Savings: ${details.get('EstimatedMonthlySavingsAmount', 0)}")
        print(f"  Estimated Savings Percentage: {details.get('EstimatedSavingsPercentage', 0)}%")

    return recommendations

# Usage
recommendations = analyze_instance_usage(days=30)
for rec in recommendations:
    print(f"{rec['instance_type']}: {rec['count']} instances - {rec['action']}")
```

### Example 7: Performance Testing Across Instance Types

```bash
#!/bin/bash
# Script to benchmark different instance types for cost-performance optimization

INSTANCE_TYPES=("t3.medium" "t3a.medium" "t4g.medium" "c6i.large" "c6g.large")
AMI_ID="ami-0c55b159cbfafe1f0"  # Amazon Linux 2
KEY_NAME="benchmark-key"
SECURITY_GROUP="sg-0123456789abcdef0"
SUBNET_ID="subnet-0123456789abcdef0"

RESULTS_FILE="benchmark_results.csv"
echo "Instance Type,vCPUs,Memory,Cost/Hour,Benchmark Score,Cost Performance Ratio" > $RESULTS_FILE

for INSTANCE_TYPE in "${INSTANCE_TYPES[@]}"; do
    echo "Testing $INSTANCE_TYPE..."

    # Launch instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-group-ids $SECURITY_GROUP \
        --subnet-id $SUBNET_ID \
        --user-data '#!/bin/bash
            yum install -y sysbench
        ' \
        --query 'Instances[0].InstanceId' \
        --output text)

    echo "Launched instance: $INSTANCE_ID"

    # Wait for instance to be running
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID

    # Get instance IP
    INSTANCE_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)

    # Wait for instance to be reachable
    sleep 60

    # Run benchmark via SSH
    BENCHMARK_SCORE=$(ssh -o StrictHostKeyChecking=no ec2-user@$INSTANCE_IP \
        'sysbench cpu --cpu-max-prime=20000 --threads=4 run | grep "events per second" | awk "{print \$4}"')

    # Get pricing (simplified - use AWS Price List API in production)
    # This is just example pricing
    case $INSTANCE_TYPE in
        "t3.medium") COST_PER_HOUR=0.0416 ;;
        "t3a.medium") COST_PER_HOUR=0.0374 ;;
        "t4g.medium") COST_PER_HOUR=0.0336 ;;
        "c6i.large") COST_PER_HOUR=0.085 ;;
        "c6g.large") COST_PER_HOUR=0.068 ;;
    esac

    # Calculate cost-performance ratio (higher is better)
    COST_PERFORMANCE=$(echo "scale=2; $BENCHMARK_SCORE / $COST_PER_HOUR" | bc)

    # Get instance specs
    VCPUS=$(aws ec2 describe-instance-types \
        --instance-types $INSTANCE_TYPE \
        --query 'InstanceTypes[0].VCpuInfo.DefaultVCpus' \
        --output text)

    MEMORY=$(aws ec2 describe-instance-types \
        --instance-types $INSTANCE_TYPE \
        --query 'InstanceTypes[0].MemoryInfo.SizeInMiB' \
        --output text)

    # Save results
    echo "$INSTANCE_TYPE,$VCPUS,$MEMORY,$COST_PER_HOUR,$BENCHMARK_SCORE,$COST_PERFORMANCE" >> $RESULTS_FILE

    # Terminate instance
    aws ec2 terminate-instances --instance-ids $INSTANCE_ID
    echo "Terminated $INSTANCE_ID"
    echo ""
done

echo "Benchmark complete! Results saved to $RESULTS_FILE"
echo ""
echo "Results:"
cat $RESULTS_FILE | column -t -s ','
```

### Example 8: Instance Metadata Service v2 (IMDSv2) Enforcement

```python
import boto3

ec2 = boto3.client('ec2')

def enforce_imdsv2(instance_id):
    """
    Enforce IMDSv2 on existing instance for better security
    """
    response = ec2.modify_instance_metadata_options(
        InstanceId=instance_id,
        HttpTokens='required',  # Require IMDSv2
        HttpPutResponseHopLimit=1,  # Limit hop count
        HttpEndpoint='enabled'
    )

    print(f"IMDSv2 enforced on {instance_id}")
    return response

def bulk_enforce_imdsv2(tag_key='Environment', tag_value='production'):
    """
    Enforce IMDSv2 on all instances with specific tag
    """
    instances = ec2.describe_instances(
        Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
        ]
    )

    updated_instances = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            # Check current IMDSv2 status
            metadata_options = instance.get('MetadataOptions', {})
            http_tokens = metadata_options.get('HttpTokens', 'optional')

            if http_tokens != 'required':
                print(f"Enforcing IMDSv2 on {instance_id}...")
                enforce_imdsv2(instance_id)
                updated_instances.append(instance_id)
            else:
                print(f"{instance_id} already using IMDSv2")

    print(f"\nTotal instances updated: {len(updated_instances)}")
    return updated_instances

# Usage
updated = bulk_enforce_imdsv2('Environment', 'production')
```

This reference covers EC2 instance types comprehensively with practical implementation examples. For latest specifications and pricing, consult AWS documentation as new instances are released quarterly.
