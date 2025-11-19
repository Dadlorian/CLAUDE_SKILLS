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

This reference covers EC2 instance types comprehensively. For latest specifications and pricing, consult AWS documentation as new instances are released quarterly.
