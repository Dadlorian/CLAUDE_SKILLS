# Azure Virtual Machine Sizes Reference

## VM Naming Convention

Azure VM sizes follow this pattern: `[Family]_[Sub-family]_[# of vCPUs]_[Additive Features]_[Accelerator Type]_[Version]`

Example: **Standard_D8s_v5**
- **Standard**: Pricing tier
- **D**: General purpose family
- **8**: 8 vCPUs
- **s**: Premium storage capable
- **v5**: 5th generation

### Common Additive Features
- **s**: Premium storage support
- **i**: Isolated (dedicated hardware)
- **a**: AMD-based processor
- **d**: Local temp disk included
- **l**: Low memory configuration
- **m**: Memory intensive
- **t**: Tiny (smallest in series)
- **p**: ARM-based processor

## VM Families

### B-Series (Burstable)
**Use Case**: Dev/test, low-traffic web servers, small databases, micro services
**CPU Credits**: Accumulate credits when idle, consume during bursts
**Cost**: Most economical option

| Size | vCPUs | RAM | Temp Storage | Base CPU % | Max CPU % | Cost/Month (Est) |
|------|-------|-----|--------------|------------|-----------|------------------|
| B1s | 1 | 1 GB | 4 GB | 10% | 100% | $8 |
| B1ms | 1 | 2 GB | 4 GB | 20% | 100% | $16 |
| B2s | 2 | 4 GB | 8 GB | 40% | 200% | $40 |
| B2ms | 2 | 8 GB | 16 GB | 60% | 200% | $67 |
| B4ms | 4 | 16 GB | 32 GB | 90% | 400% | $134 |

**Recommendation**: Perfect for workloads with variable CPU usage. Not suitable for sustained high CPU workloads.

### D-Series (General Purpose)
**Use Case**: Enterprise applications, web servers, application servers, small to medium databases
**Characteristics**: Balanced CPU-to-memory ratio

#### Dv5 Series (Latest Generation)
| Size | vCPUs | RAM | Temp Storage | Max IOPS | Max NICs | Cost/Month (Est) |
|------|-------|-----|--------------|----------|----------|------------------|
| D2s_v5 | 2 | 8 GB | None* | 3,750 | 2 | $96 |
| D4s_v5 | 4 | 16 GB | None* | 6,400 | 2 | $192 |
| D8s_v5 | 8 | 32 GB | None* | 12,800 | 4 | $384 |
| D16s_v5 | 16 | 64 GB | None* | 25,600 | 8 | $768 |
| D32s_v5 | 32 | 128 GB | None* | 51,200 | 8 | $1,536 |
| D64s_v5 | 64 | 256 GB | None* | 80,000 | 8 | $3,072 |
| D96s_v5 | 96 | 384 GB | None* | 80,000 | 8 | $4,608 |

*Use Dds_v5 for local temp storage

**Processor**: Intel Ice Lake or AMD EPYC 3rd Gen
**Features**: Premium SSD support, accelerated networking
**Recommendation**: Default choice for most workloads

### E-Series (Memory Optimized)
**Use Case**: Large databases (SAP HANA, SQL Server), in-memory analytics, Redis cache
**Characteristics**: High memory-to-CPU ratio (8 GB per vCPU)

#### Ev5 Series
| Size | vCPUs | RAM | Temp Storage | Max IOPS | Cost/Month (Est) |
|------|-------|-----|--------------|----------|------------------|
| E2s_v5 | 2 | 16 GB | None* | 3,750 | $122 |
| E4s_v5 | 4 | 32 GB | None* | 6,400 | $243 |
| E8s_v5 | 8 | 64 GB | None* | 12,800 | $486 |
| E16s_v5 | 16 | 128 GB | None* | 25,600 | $973 |
| E32s_v5 | 32 | 256 GB | None* | 51,200 | $1,946 |
| E64s_v5 | 64 | 512 GB | None* | 80,000 | $3,891 |
| E96s_v5 | 96 | 672 GB | None* | 80,000 | $5,102 |

*Use Eds_v5 for local temp storage

**Recommendation**: When your application needs more than 4 GB RAM per vCPU

### F-Series (Compute Optimized)
**Use Case**: Batch processing, web servers, analytics, gaming servers, machine learning inference
**Characteristics**: High CPU-to-memory ratio (2 GB per vCPU)

#### Fv2 Series
| Size | vCPUs | RAM | Temp Storage | Max IOPS | Cost/Month (Est) |
|------|-------|-----|--------------|----------|------------------|
| F2s_v2 | 2 | 4 GB | 16 GB | 3,200 | $85 |
| F4s_v2 | 4 | 8 GB | 32 GB | 6,400 | $169 |
| F8s_v2 | 8 | 16 GB | 64 GB | 12,800 | $338 |
| F16s_v2 | 16 | 32 GB | 128 GB | 25,600 | $676 |
| F32s_v2 | 32 | 64 GB | 256 GB | 51,200 | $1,352 |
| F64s_v2 | 64 | 128 GB | 512 GB | 80,000 | $2,703 |
| F72s_v2 | 72 | 144 GB | 576 GB | 80,000 | $3,041 |

**Processor**: Intel Cascade Lake
**Recommendation**: Best price/performance for CPU-intensive workloads

### M-Series (Memory Intensive)
**Use Case**: SAP HANA, large SQL Server databases, massive in-memory workloads
**Characteristics**: Extreme memory configurations (up to 12 TB RAM)

| Size | vCPUs | RAM | Temp Storage | Max Data Disks | Cost/Month (Est) |
|------|-------|-----|--------------|----------------|------------------|
| M8ms | 8 | 218 GB | 256 GB | 8 | $1,500 |
| M16ms | 16 | 437 GB | 512 GB | 16 | $3,000 |
| M32ms | 32 | 875 GB | 1,024 GB | 32 | $6,000 |
| M64ms | 64 | 1,792 GB | 2,048 GB | 64 | $12,000 |
| M128ms | 128 | 3,892 GB | 4,096 GB | 64 | $25,000 |
| M208ms_v2 | 208 | 5,700 GB | 4,096 GB | 64 | $40,000 |

**Recommendation**: Only for massive memory requirements; very expensive

### L-Series (Storage Optimized)
**Use Case**: NoSQL databases (Cassandra, MongoDB), data warehousing, large transactional databases
**Characteristics**: High disk throughput and IOPS, large local NVMe storage

#### Lsv3 Series
| Size | vCPUs | RAM | Temp Storage (NVMe) | Max IOPS | Cost/Month (Est) |
|------|-------|-----|---------------------|----------|------------------|
| L8s_v3 | 8 | 64 GB | 1.92 TB | 400,000 | $624 |
| L16s_v3 | 16 | 128 GB | 3.84 TB | 800,000 | $1,248 |
| L32s_v3 | 32 | 256 GB | 7.68 TB | 1,600,000 | $2,496 |
| L48s_v3 | 48 | 384 GB | 11.52 TB | 2,400,000 | $3,744 |
| L64s_v3 | 64 | 512 GB | 15.36 TB | 3,200,000 | $4,992 |
| L80s_v3 | 80 | 640 GB | 19.20 TB | 4,000,000 | $6,240 |

**Recommendation**: When you need extreme local disk performance

### N-Series (GPU)
**Use Case**: AI/ML training, rendering, video encoding, visualization, VDI

#### NCv3 Series (NVIDIA Tesla V100)
| Size | vCPUs | RAM | GPUs | GPU Memory | Cost/Month (Est) |
|------|-------|-----|------|------------|------------------|
| NC6s_v3 | 6 | 112 GB | 1 | 16 GB | $2,070 |
| NC12s_v3 | 12 | 224 GB | 2 | 32 GB | $4,140 |
| NC24s_v3 | 24 | 448 GB | 4 | 64 GB | $8,280 |

#### NDv2 Series (NVIDIA Tesla V100 - 32 GB)
**Use Case**: Deep learning training at scale
- 8 GPUs with NVLink interconnect
- 200 Gbps InfiniBand

#### NVv4 Series (AMD Radeon Instinct MI25)
**Use Case**: VDI, remote visualization
**Fractional GPU**: Can provision partial GPU (1/8, 1/4, 1/2, or full)

### DC-Series (Confidential Computing)
**Use Case**: Sensitive data processing, healthcare, finance
**Characteristics**: Intel SGX (Software Guard Extensions) for encrypted memory

| Size | vCPUs | RAM | Encrypted Memory | Cost/Month (Est) |
|------|-------|-----|------------------|------------------|
| DC2s_v3 | 2 | 16 GB | 8 GB | $180 |
| DC4s_v3 | 4 | 32 GB | 16 GB | $360 |
| DC8s_v3 | 8 | 64 GB | 32 GB | $720 |

## Disk Performance Limits

VM sizes have maximum uncached disk IOPS and throughput limits:

### Example D-Series Limits
| Size | Max Data Disks | Max IOPS | Max Throughput |
|------|----------------|----------|----------------|
| D2s_v5 | 4 | 3,750 | 85 MB/s |
| D4s_v5 | 8 | 6,400 | 145 MB/s |
| D8s_v5 | 16 | 12,800 | 290 MB/s |
| D16s_v5 | 32 | 25,600 | 600 MB/s |
| D32s_v5 | 32 | 51,200 | 865 MB/s |

**Important**: VM size limits may be lower than disk limits. The effective IOPS/throughput is the minimum of VM and disk limits.

## Network Performance

### Accelerated Networking
- Available on most modern VM sizes (Dv3+, Ev3+, Fv2+)
- SR-IOV for high-performance networking
- Up to 30 Gbps network bandwidth
- Reduced latency and jitter

### Expected Network Bandwidth
| VM Size | Expected Bandwidth |
|---------|-------------------|
| 2-4 vCPUs | 2-5 Gbps |
| 8 vCPUs | 5-10 Gbps |
| 16 vCPUs | 10-20 Gbps |
| 32+ vCPUs | 20-30 Gbps |

## Cost Optimization Strategies

### Reserved Instances
- 1-year: 20-30% discount
- 3-year: 40-60% discount
- Can exchange or cancel with flexibility

### Spot VMs
- 60-90% discount compared to pay-as-you-go
- Can be evicted with 30-second notice
- Best for stateless, fault-tolerant workloads

### Azure Hybrid Benefit
- Use existing Windows Server or SQL Server licenses
- Up to 49% savings on Windows VMs
- Up to 55% savings on SQL Server

### Azure Savings Plan
- Commit to spend ($/hour) for 1 or 3 years
- Flexible across VM series and regions
- 10-17% savings beyond reserved instances

## Selection Decision Tree

```
Start
│
├─ Need GPU? → Yes → N-Series
│              ↓ No
│
├─ Need massive memory (>384 GB)? → Yes → M-Series
│                                   ↓ No
│
├─ Need local NVMe storage? → Yes → L-Series
│                             ↓ No
│
├─ CPU:Memory ratio needed?
│   ├─ High CPU (< 2 GB/vCPU) → F-Series
│   ├─ Balanced (4 GB/vCPU) → D-Series
│   └─ High Memory (8+ GB/vCPU) → E-Series
│
├─ Variable workload? → Yes → B-Series
│
└─ Confidential computing? → Yes → DC-Series
```

## Performance Testing Recommendations

Before selecting a VM size for production:

1. **Baseline current workload**
   - CPU utilization patterns
   - Memory requirements
   - Disk IOPS and throughput
   - Network bandwidth needs

2. **Start with D-Series**
   - Best balance for most workloads
   - Easy to resize up or down

3. **Load test thoroughly**
   - Simulate peak load conditions
   - Monitor CPU, memory, disk, network
   - Use Azure Monitor metrics

4. **Right-size iteratively**
   - Start larger, then downsize
   - Monitor for 2-4 weeks
   - Adjust based on actual usage

5. **Consider auto-scaling**
   - VM Scale Sets for stateless workloads
   - Scale out instead of up when possible

## Common Workload Recommendations

| Workload Type | Recommended Series | Typical Size |
|---------------|-------------------|--------------|
| Development/Test | B-Series | B2s, B2ms |
| Web Server (Low Traffic) | B-Series | B2s, B4ms |
| Web Server (Production) | D-Series | D4s_v5, D8s_v5 |
| Application Server | D-Series | D8s_v5, D16s_v5 |
| SQL Server (Small) | E-Series | E4s_v5, E8s_v5 |
| SQL Server (Large) | E-Series | E16s_v5, E32s_v5 |
| SAP HANA | M-Series | M32ms+ |
| Batch Processing | F-Series | F8s_v2, F16s_v2 |
| ML Inference | F-Series | F16s_v2, F32s_v2 |
| ML Training | N-Series | NC6s_v3+ |
| Cassandra/MongoDB | L-Series | L8s_v3, L16s_v3 |
| Domain Controller | D-Series | D2s_v5, D4s_v5 |
| File Server | D-Series | D4s_v5, D8s_v5 |

## Region Availability

Not all VM sizes are available in all regions:
- **B, D, E, F Series**: Available in all regions
- **M-Series**: Limited to major regions
- **L-Series**: Limited availability
- **N-Series (GPU)**: Limited to regions with GPU capacity

Check current availability: `az vm list-skus --location <region> --output table`

## Constraints and Considerations

### vCPU Quotas
- Default quota: 10-20 vCPUs per region
- Increase via support request
- Separate quotas for Spot VMs

### Availability Sets
- Cannot mix different VM families
- 3 fault domains, 5 update domains (default)

### Availability Zones
- Not all sizes available in zones
- Generally D, E, F series v3+ are zone-capable

### Premium Storage
- Requires 's' designation (e.g., D4s_v5)
- Not available on basic A-Series

### Resize Limitations
- Can only resize within same family or generation (usually)
- Some resizes require VM deallocation
- Cross-family resize may require new deployment

## Quick Reference Commands

```bash
# List all sizes in a region
az vm list-sizes --location eastus --output table

# List available sizes for a VM
az vm list-vm-resize-options --resource-group myRG --name myVM --output table

# Get VM size details
az vm list-skus --location eastus --size Standard_D --output table

# Resize a VM
az vm resize --resource-group myRG --name myVM --size Standard_D8s_v5

# Get current vCPU usage
az vm list-usage --location eastus --output table
```
