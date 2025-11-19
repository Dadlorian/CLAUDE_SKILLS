# Compute Engine Machine Types Reference

## Machine Type Families Overview

Google Compute Engine offers multiple machine families optimized for different workloads with varying CPU, memory, and networking characteristics.

### Machine Family Categories

1. **General Purpose** (E2, N2, N2D, N1, Tau T2D, Tau T2A)
2. **Compute Optimized** (C2, C2D, C3)
3. **Memory Optimized** (M1, M2, M3)
4. **Accelerator Optimized** (A2, A3, G2)
5. **Storage Optimized** (Z3)

## General Purpose Machine Families

### E2 - Cost-Optimized
- **CPU**: Intel or AMD (no CPU selection)
- **vCPUs**: 2-32
- **Memory**: 0.5-8 GB per vCPU
- **Use Cases**: Web serving, small databases, development environments, microservices
- **Pricing**: Lowest cost option (~31% cheaper than N1)
- **Characteristics**:
  - No local SSD support
  - Shared-core options (e2-micro, e2-small, e2-medium)
  - Suitable for workloads that don't require dedicated CPU

**Predefined Types**:
```
e2-micro:        2 vCPUs (shared),  1 GB memory
e2-small:        2 vCPUs (shared),  2 GB memory
e2-medium:       2 vCPUs (shared),  4 GB memory
e2-standard-2:   2 vCPUs,           8 GB memory
e2-standard-4:   4 vCPUs,          16 GB memory
e2-standard-8:   8 vCPUs,          32 GB memory
e2-standard-16: 16 vCPUs,          64 GB memory
e2-standard-32: 32 vCPUs,         128 GB memory
e2-highmem-2:    2 vCPUs,          16 GB memory
e2-highmem-4:    4 vCPUs,          32 GB memory
e2-highmem-8:    8 vCPUs,          64 GB memory
e2-highmem-16:  16 vCPUs,         128 GB memory
e2-highcpu-2:    2 vCPUs,           2 GB memory
e2-highcpu-4:    4 vCPUs,           4 GB memory
e2-highcpu-8:    8 vCPUs,           8 GB memory
e2-highcpu-16:  16 vCPUs,          16 GB memory
e2-highcpu-32:  32 vCPUs,          32 GB memory
```

### N2 - Balanced Performance
- **CPU**: Intel Cascade Lake or Ice Lake
- **vCPUs**: 2-128
- **Memory**: 0.5-8 GB per vCPU
- **Use Cases**: Web applications, databases, cache servers, media transcoding
- **Features**:
  - Up to 3.4 GHz sustained all-core turbo
  - Support for local SSDs
  - Custom machine types
  - Live migration
- **Extended Memory**: Up to 624 GB with n2-highmem-128

**Predefined Types**:
```
n2-standard-2:    2 vCPUs,   8 GB memory
n2-standard-4:    4 vCPUs,  16 GB memory
n2-standard-8:    8 vCPUs,  32 GB memory
n2-standard-16:  16 vCPUs,  64 GB memory
n2-standard-32:  32 vCPUs, 128 GB memory
n2-standard-48:  48 vCPUs, 192 GB memory
n2-standard-64:  64 vCPUs, 256 GB memory
n2-standard-80:  80 vCPUs, 320 GB memory
n2-standard-96:  96 vCPUs, 384 GB memory
n2-standard-128: 128 vCPUs, 512 GB memory

n2-highmem-2:    2 vCPUs,  16 GB memory
n2-highmem-4:    4 vCPUs,  32 GB memory
n2-highmem-8:    8 vCPUs,  64 GB memory
n2-highmem-16:  16 vCPUs, 128 GB memory
n2-highmem-32:  32 vCPUs, 256 GB memory
n2-highmem-48:  48 vCPUs, 384 GB memory
n2-highmem-64:  64 vCPUs, 512 GB memory
n2-highmem-80:  80 vCPUs, 640 GB memory
n2-highmem-96:  96 vCPUs, 768 GB memory
n2-highmem-128: 128 vCPUs, 864 GB memory

n2-highcpu-2:    2 vCPUs,   2 GB memory
n2-highcpu-4:    4 vCPUs,   4 GB memory
n2-highcpu-8:    8 vCPUs,   8 GB memory
n2-highcpu-16:  16 vCPUs,  16 GB memory
n2-highcpu-32:  32 vCPUs,  32 GB memory
n2-highcpu-48:  48 vCPUs,  48 GB memory
n2-highcpu-64:  64 vCPUs,  64 GB memory
n2-highcpu-80:  80 vCPUs,  80 GB memory
n2-highcpu-96:  96 vCPUs,  96 GB memory
```

### N2D - AMD-Based Performance
- **CPU**: AMD EPYC Rome or Milan
- **vCPUs**: 2-224
- **Memory**: 0.5-8 GB per vCPU
- **Use Cases**: General purpose workloads, cost-sensitive applications
- **Advantages**: ~10% lower cost than N2, higher max vCPUs

**Predefined Types**:
```
n2d-standard-2:    2 vCPUs,   8 GB memory
n2d-standard-4:    4 vCPUs,  16 GB memory
n2d-standard-8:    8 vCPUs,  32 GB memory
n2d-standard-16:  16 vCPUs,  64 GB memory
n2d-standard-32:  32 vCPUs, 128 GB memory
n2d-standard-48:  48 vCPUs, 192 GB memory
n2d-standard-64:  64 vCPUs, 256 GB memory
n2d-standard-80:  80 vCPUs, 320 GB memory
n2d-standard-96:  96 vCPUs, 384 GB memory
n2d-standard-128: 128 vCPUs, 512 GB memory
n2d-standard-224: 224 vCPUs, 896 GB memory

n2d-highmem-2:    2 vCPUs,  16 GB memory
n2d-highmem-4:    4 vCPUs,  32 GB memory
n2d-highmem-8:    8 vCPUs,  64 GB memory
n2d-highmem-16:  16 vCPUs, 128 GB memory
n2d-highmem-32:  32 vCPUs, 256 GB memory
n2d-highmem-48:  48 vCPUs, 384 GB memory
n2d-highmem-64:  64 vCPUs, 512 GB memory
n2d-highmem-80:  80 vCPUs, 640 GB memory
n2d-highmem-96:  96 vCPUs, 768 GB memory

n2d-highcpu-2:    2 vCPUs,   2 GB memory
n2d-highcpu-4:    4 vCPUs,   4 GB memory
n2d-highcpu-8:    8 vCPUs,   8 GB memory
n2d-highcpu-16:  16 vCPUs,  16 GB memory
n2d-highcpu-32:  32 vCPUs,  32 GB memory
n2d-highcpu-48:  48 vCPUs,  48 GB memory
n2d-highcpu-64:  64 vCPUs,  64 GB memory
n2d-highcpu-80:  80 vCPUs,  80 GB memory
n2d-highcpu-96:  96 vCPUs,  96 GB memory
n2d-highcpu-128: 128 vCPUs, 128 GB memory
n2d-highcpu-224: 224 vCPUs, 224 GB memory
```

### N1 - First Generation (Legacy)
- **CPU**: Intel Skylake, Broadwell, Haswell, Ivy Bridge
- **vCPUs**: 1-96
- **Memory**: 0.9-6.5 GB per vCPU
- **Use Cases**: Legacy workloads, maximum compatibility
- **Note**: Being superseded by N2/N2D, but still widely used

### Tau T2D - Scale-Out Optimized
- **CPU**: AMD EPYC Milan
- **vCPUs**: 1-60
- **Memory**: 1-4 GB per vCPU
- **Use Cases**: Scale-out workloads, web serving, containerized microservices, media transcoding
- **Advantages**: Up to 56% better price-performance than N1 for scale-out workloads

### Tau T2A - Arm-Based
- **CPU**: Ampere Altra (Arm Neoverse N1)
- **vCPUs**: 1-48
- **Memory**: 4 GB per vCPU
- **Use Cases**: Web servers, containerized microservices, data logging, media transcoding
- **Advantages**: Up to 65% better price-performance for scale-out workloads

## Compute Optimized Machine Families

### C2 - High Performance Computing
- **CPU**: Intel Cascade Lake (3.8 GHz all-core turbo)
- **vCPUs**: 4-60
- **Memory**: 4 GB per vCPU
- **Use Cases**: Gaming servers, HPC, computational workloads, ad serving, high-performance databases
- **Features**:
  - Highest per-core performance
  - Optimized for compute-bound workloads

**Predefined Types**:
```
c2-standard-4:  4 vCPUs,  16 GB memory
c2-standard-8:  8 vCPUs,  32 GB memory
c2-standard-16: 16 vCPUs,  64 GB memory
c2-standard-30: 30 vCPUs, 120 GB memory
c2-standard-60: 60 vCPUs, 240 GB memory
```

### C2D - AMD Compute Optimized
- **CPU**: AMD EPYC Milan (3.4 GHz all-core turbo)
- **vCPUs**: 2-112
- **Memory**: 4 GB per vCPU
- **Use Cases**: Compute-intensive workloads, HPC, gaming, media transcoding
- **Advantages**: ~10% better price-performance than C2

**Predefined Types**:
```
c2d-standard-2:   2 vCPUs,   8 GB memory
c2d-standard-4:   4 vCPUs,  16 GB memory
c2d-standard-8:   8 vCPUs,  32 GB memory
c2d-standard-16:  16 vCPUs,  64 GB memory
c2d-standard-32:  32 vCPUs, 128 GB memory
c2d-standard-56:  56 vCPUs, 224 GB memory
c2d-standard-112: 112 vCPUs, 448 GB memory

c2d-highcpu-2:   2 vCPUs,   4 GB memory
c2d-highcpu-4:   4 vCPUs,   8 GB memory
c2d-highcpu-8:   8 vCPUs,  16 GB memory
c2d-highcpu-16:  16 vCPUs,  32 GB memory
c2d-highcpu-32:  32 vCPUs,  64 GB memory
c2d-highcpu-56:  56 vCPUs, 112 GB memory
c2d-highcpu-112: 112 vCPUs, 224 GB memory

c2d-highmem-2:   2 vCPUs,  16 GB memory
c2d-highmem-4:   4 vCPUs,  32 GB memory
c2d-highmem-8:   8 vCPUs,  64 GB memory
c2d-highmem-16:  16 vCPUs, 128 GB memory
c2d-highmem-32:  32 vCPUs, 256 GB memory
c2d-highmem-56:  56 vCPUs, 448 GB memory
c2d-highmem-112: 112 vCPUs, 896 GB memory
```

### C3 - Next Generation Compute
- **CPU**: Intel Sapphire Rapids (3.9 GHz all-core turbo)
- **vCPUs**: 4-176
- **Memory**: 2 or 4 GB per vCPU
- **Use Cases**: Demanding compute-intensive workloads, AI/ML inference, HPC
- **Features**: Latest generation, highest performance

## Memory Optimized Machine Families

### M1 - Ultra High Memory
- **CPU**: Intel Skylake
- **vCPUs**: 40-160
- **Memory**: 961 GB - 3.75 TB
- **Memory per vCPU**: 24 GB (ultramem-40), 14.9 GB (megamem-96)
- **Use Cases**: SAP HANA, in-memory databases, real-time analytics
- **Predefined Types**:
```
m1-ultramem-40:  40 vCPUs,  961 GB memory
m1-ultramem-80:  80 vCPUs, 1922 GB memory
m1-ultramem-160: 160 vCPUs, 3844 GB memory

m1-megamem-96:   96 vCPUs, 1433 GB memory
```

### M2 - Second Generation Memory Optimized
- **CPU**: Intel Cascade Lake
- **vCPUs**: 208-416
- **Memory**: 2.9 TB - 5.9 TB
- **Use Cases**: Extremely large in-memory databases, SAP HANA
- **Predefined Types**:
```
m2-ultramem-208: 208 vCPUs, 5888 GB memory
m2-ultramem-416: 416 vCPUs, 11776 GB memory

m2-megamem-416:  416 vCPUs, 5888 GB memory
```

### M3 - Latest Memory Optimized
- **CPU**: Intel Ice Lake
- **vCPUs**: 32-128
- **Memory**: 256 GB - 1 TB
- **Use Cases**: Medium to large in-memory databases, in-memory analytics
- **Predefined Types**:
```
m3-ultramem-32:  32 vCPUs,  976 GB memory
m3-ultramem-64:  64 vCPUs, 1952 GB memory
m3-ultramem-128: 128 vCPUs, 3904 GB memory

m3-megamem-64:   64 vCPUs,  976 GB memory
m3-megamem-128:  128 vCPUs, 1952 GB memory
```

## Accelerator Optimized Machine Families

### A2 - GPU Accelerated
- **CPU**: Intel Cascade Lake
- **GPU**: NVIDIA A100 (40 GB or 80 GB)
- **vCPUs**: 12-96
- **Memory**: 85 GB - 680 GB
- **Use Cases**: ML training, HPC, batch inference
- **Predefined Types**:
```
a2-highgpu-1g:  12 vCPUs,  85 GB memory, 1x A100 40GB
a2-highgpu-2g:  24 vCPUs, 170 GB memory, 2x A100 40GB
a2-highgpu-4g:  48 vCPUs, 340 GB memory, 4x A100 40GB
a2-highgpu-8g:  96 vCPUs, 680 GB memory, 8x A100 40GB

a2-megagpu-16g: 96 vCPUs, 1360 GB memory, 16x A100 40GB
a2-ultragpu-1g: 12 vCPUs,  170 GB memory, 1x A100 80GB
a2-ultragpu-2g: 24 vCPUs,  340 GB memory, 2x A100 80GB
a2-ultragpu-4g: 48 vCPUs,  680 GB memory, 4x A100 80GB
a2-ultragpu-8g: 96 vCPUs, 1360 GB memory, 8x A100 80GB
```

### A3 - Next Generation GPU
- **CPU**: Intel Sapphire Rapids
- **GPU**: NVIDIA H100 80GB
- **Use Cases**: Large-scale ML training, generative AI
- **Features**: NVLink, NVSwitch, GPUDirect-TCPX

### G2 - GPU Inference Optimized
- **CPU**: Intel Cascade Lake
- **GPU**: NVIDIA L4
- **vCPUs**: 4-96
- **Use Cases**: Video transcoding, AI inference, graphics workloads
- **Predefined Types**:
```
g2-standard-4:   4 vCPUs,  16 GB memory, 1x L4
g2-standard-8:   8 vCPUs,  32 GB memory, 1x L4
g2-standard-12: 12 vCPUs,  48 GB memory, 1x L4
g2-standard-16: 16 vCPUs,  64 GB memory, 1x L4
g2-standard-24: 24 vCPUs,  96 GB memory, 2x L4
g2-standard-32: 32 vCPUs, 128 GB memory, 1x L4
g2-standard-48: 48 vCPUs, 192 GB memory, 4x L4
g2-standard-96: 96 vCPUs, 384 GB memory, 8x L4
```

## Storage Optimized

### Z3 - High Storage Throughput
- **CPU**: Intel Cascade Lake or Sapphire Rapids
- **vCPUs**: 44-176
- **Memory**: 352 GB - 1408 GB
- **Local SSD**: 3 TB - 24 TB
- **Use Cases**: Storage-intensive workloads, distributed databases, Hadoop/Spark

## Custom Machine Types

Create custom machine types with:
- **vCPUs**: 1 vCPU or even number (2-96 for N1, up to 128 for N2)
- **Memory**: 0.9-6.5 GB per vCPU (N1), 0.5-8 GB per vCPU (N2/N2D)
- **Naming**: custom-VCPUS-MEMORY (e.g., custom-4-16384)

**CLI Example**:
```bash
gcloud compute instances create INSTANCE_NAME \
    --custom-cpu=4 \
    --custom-memory=16GB \
    --zone=us-central1-a
```

## Extended Memory
Add up to 624 GB additional memory to N1 machines:
```bash
gcloud compute instances create INSTANCE_NAME \
    --machine-type=n1-standard-96 \
    --custom-extensions \
    --custom-memory=1248 \
    --zone=us-central1-a
```

## Sole-Tenant Nodes

Dedicated hardware for compliance and licensing:
- Same machine types as regular VMs
- Node groups for management
- Node affinity labels
- Maintenance policies

## Preemptible and Spot VMs

- **Discount**: Up to 91% off regular pricing
- **Duration**: Up to 24 hours
- **Termination**: 30-second warning
- **Availability**: Not guaranteed
- **Use Cases**: Batch jobs, fault-tolerant workloads, CI/CD

## Machine Type Selection Guide

| Workload Type | Recommended Family |
|--------------|-------------------|
| General web applications | E2, N2 |
| Databases (general) | N2, N2D |
| In-memory databases | M1, M2, M3 |
| Compute-intensive | C2, C2D, C3 |
| ML training | A2, A3 |
| ML inference | G2, N1 with GPUs |
| High storage throughput | Z3 |
| SAP HANA | M1, M2 |
| Microservices | E2, T2D, T2A |
| Batch processing | Preemptible/Spot VMs |
| Cost-sensitive | E2, T2D, T2A |

## Performance Characteristics

### Network Performance
- **Per vCPU**: 2 Gbps egress (up to 32 Gbps total)
- **Tier 1 Networking**: 100 Gbps for select machine types
- **Example**: n2-standard-32 = 32 Gbps, n2-standard-128 = 100 Gbps

### Disk Performance
- **PD-SSD**: 30 IOPS/GB read, 30 IOPS/GB write
- **Local SSD**: 375,000 IOPS read, 170,000 IOPS write
- **Maximum**: Depends on vCPU count

### GPU Attachment
- N1: All GPU types
- A2/A3: Integrated GPUs
- N2, C2, M1: No GPU support (use N1)

## Regional Availability

Not all machine types available in all regions:
- E2, N2, N2D: All regions
- C2, C2D: Most regions
- M1, M2, M3: Select regions
- A2, A3, G2: Limited regions with GPU availability

Check current availability:
```bash
gcloud compute machine-types list --zones=us-central1-a
```

## Pricing Considerations

1. **On-Demand**: Standard per-second pricing
2. **Committed Use Discounts**: 1-year (25% off) or 3-year (52% off)
3. **Sustained Use Discounts**: Automatic 20-30% for usage >25% of month
4. **Preemptible/Spot**: Up to 91% discount
5. **Free Tier**: e2-micro (US regions only)

**Cost Optimization Tips**:
- Use E2 for cost-sensitive workloads
- Apply committed use discounts for steady-state workloads
- Use preemptible VMs for batch jobs
- Right-size based on monitoring data
- Use custom machine types to avoid over-provisioning
