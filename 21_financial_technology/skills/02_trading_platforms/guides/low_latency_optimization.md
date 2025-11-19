# Low-Latency Optimization Guide

## Latency Budget Analysis

### Target: 100µs End-to-End Latency

```
Component                   Target      Typical     Optimized
─────────────────────────────────────────────────────────────
Market Data Reception       10µs        50µs        10µs
NIC Processing              5µs         20µs        5µs
Kernel/Driver               0µs         10µs        0µs (bypass)
Data Processing             20µs        100µs       20µs
Decision Making             10µs        50µs        10µs
Order Generation            5µs         20µs        5µs
FIX Encoding                5µs         20µs        5µs
Network Send                10µs        50µs        10µs
NIC Transmission            20µs        100µs       20µs
Network Propagation         5µs         5µs         5µs
─────────────────────────────────────────────────────────────
Total Round-Trip            90µs        500µs       90µs
```

## Optimization Layer 1: Hardware Selection

### CPU Selection

**Intel Xeon Platinum 8490H** (Recommended for Trading)
```
- Frequency: 3.0-4.0 GHz
- Cores: 60 cores (select subset)
- Cache: 260MB L3 cache
- Thermal: 350W TDP (heat management required)
- Cost: $8,000-12,000
- Advantage: Turbo Boost, large caches, stable frequency
```

**AMD EPYC 9654** (Alternative)
```
- Frequency: 2.4-3.8 GHz
- Cores: 128 cores
- Cache: 768MB L3 cache per socket
- Thermal: 360W TDP
- Cost: $10,000-14,000
- Advantage: More cores, higher throughput
```

**Key Specifications for Trading**:
- Avoid: P-core/E-core hybrid designs (unpredictable latency)
- Prefer: Consistent frequency (no frequency scaling)
- Select: High base clock (3.5+ GHz)

### Network Interface Card (NIC)

**High-Performance NIC Requirements**:
- **Throughput**: 40+ Gbps
- **Latency**: <1µs per frame
- **Offloads**: TSO, GSO, RSS, RPS
- **Hardware Time Stamping**: Nanosecond precision
- **Recommended**: Mellanox Connect-X 6/7, Intel E810

```
Example: Mellanox Connect-X 7
- 100 Gbps capable (often run at 40 Gbps)
- Sub-100ns latency per packet
- Hardware timestamping (±20ns)
- DirectAccess memory (DMA)
- Cost: $3,000-5,000
```

### Memory System

**Requirements**:
- **Capacity**: 128GB-512GB DRAM
- **Speed**: DDR5-6400 (latest generation)
- **Configuration**: Multiple channels for bandwidth
- **Thermal**: Passive cooling (no active fans = less jitter)

**Key Metric**: Memory bandwidth
```
Required: 50GB/s for quote processing
DDR5-6400, 12-channel: ~1TB/s (more than enough)
```

## Optimization Layer 2: Kernel & Network Stack

### Kernel Bypass Networking

**Standard TCP/IP Stack Latency**:
```
Application → Socket API → Kernel Network Stack → Driver
Latency: 10-100µs per message
Throughput: Limited by kernel serialization
```

**Kernel Bypass Approach**:
```
Application → User-Space Driver → NIC
Latency: <1µs per message
Throughput: Limited only by NIC
```

### DPDK (Data Plane Development Kit) Setup

```bash
# Install DPDK
git clone http://dpdk.org/git/dpdk
cd dpdk
meson build
ninja -C build
ninja -C build install

# Configure huge pages (critical!)
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# Mount hugepages
mkdir /mnt/hugepages
mount -t hugetlbfs nodev /mnt/hugepages

# Bind NIC to DPDK driver
./usertools/dpdk-devbind.py --bind=igb_uio 0000:02:00.0

# Compile with DPDK
gcc -O3 -march=native trading_system.c \
    -I/usr/local/include/dpdk \
    -L/usr/local/lib/x86_64-linux-gnu \
    -ldpdk -o trading_system
```

### DPDK Trading Application Example

```c
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>

#define BATCH_SIZE 32
#define RX_RING_SIZE 4096
#define TX_RING_SIZE 4096

int main(int argc, char *argv[]) {
    // Initialize DPDK
    rte_eal_init(argc, argv);

    // Setup port
    uint16_t port = 0;
    rte_eth_dev_configure(port, 1, 1, &port_conf);

    // Setup RX queue
    rte_eth_rx_queue_setup(port, 0, RX_RING_SIZE,
        rte_eth_dev_socket_id(port), NULL, mbuf_pool);

    // Setup TX queue
    rte_eth_tx_queue_setup(port, 0, TX_RING_SIZE,
        rte_eth_dev_socket_id(port), NULL);

    // Start port
    rte_eth_dev_start(port);

    // Main loop
    while (1) {
        // Receive batch of packets (32 at a time)
        struct rte_mbuf *bufs[BATCH_SIZE];
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BATCH_SIZE);

        // Process each packet
        for (int i = 0; i < nb_rx; i++) {
            struct rte_mbuf *pkt = bufs[i];

            // Parse packet (FIX message, market data, etc.)
            parse_packet(rte_pktmbuf_mtod(pkt, void*));

            // Process quote/trade
            process_market_data();

            // Generate order if needed
            if (should_send_order()) {
                build_order(pkt);
                rte_eth_tx_burst(port, 0, &pkt, 1);
            }

            rte_pktmbuf_free(pkt);
        }
    }

    return 0;
}
```

## Optimization Layer 3: Application Code

### Lock-Free Data Structures

**Problem**: Locks cause unpredictable latency
```cpp
// BAD: Lock contention
std::mutex m;
std::map<uint32_t, Order> orders;

void submit_order(const Order& order) {
    std::lock_guard<std::mutex> lock(m);  // Block here!
    orders[order.id] = order;
}
```

**Solution**: Atomic operations and lock-free structures
```cpp
// GOOD: Lock-free
std::atomic<Order*> current_order;

void submit_order(Order* order) {
    current_order.store(order, std::memory_order_release);
    // No blocking!
}
```

### Pre-allocation Strategy

```cpp
// Pre-allocate all objects upfront
class OrderPool {
    static constexpr size_t POOL_SIZE = 1000000;
    std::array<Order, POOL_SIZE> orders;
    std::atomic<size_t> next_index = {0};

public:
    Order* allocate() {
        size_t idx = next_index.fetch_add(1);
        if (idx >= POOL_SIZE) return nullptr;
        return &orders[idx];
    }

    void deallocate(Order* order) {
        // No-op, reuse after reset
        memset(order, 0, sizeof(Order));
    }
};
```

### Cache-Aware Programming

```cpp
// Align frequently accessed data to cache line (64 bytes)
struct __attribute__((aligned(64))) OrderBookEntry {
    uint32_t price;
    uint32_t volume;
    uint64_t timestamp;
    // Total: 16 bytes, fits in single cache line
};

// Keep hot data together
struct __attribute__((aligned(64))) HotPath {
    uint64_t current_time;
    uint32_t security_id;
    int32_t delta_position;
    double risk_factor;
    // All on one cache line, zero-cost access
};
```

## Optimization Layer 4: Real-Time Kernel Tuning

### Disable CPU Power Management

```bash
# Disable turbo boost (unpredictable frequency scaling)
echo 0 > /sys/devices/system/cpu/intel_pstate/no_turbo

# Set CPU scaling to performance
for i in {0..63}; do
    echo performance > /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor
done

# Disable C-states (power saving sleep states)
echo 1 > /sys/module/intel_idle/parameters/max_cstate
```

### CPU Isolation

```bash
# Isolate cores for trading application (prevent kernel interrupts)
# Add to /etc/default/grub:
# GRUB_CMDLINE_LINUX="isolcpus=2-19 nohz_full=2-19 rcu_nocbs=2-19"

# Verify isolation
cat /proc/cmdline
```

### Network Interrupt Handling

```bash
# Disable softirq (network stack) on isolated cores
# For NIC interrupt at IRQ 32:
echo 0 > /proc/irq/32/smp_affinity_list

# Move RPS (Receive Packet Steering) away from trading cores
echo 0x0 > /sys/class/net/eth0/queues/rx-0/rps_cpus
```

## Optimization Layer 5: Latency Measurement

### High-Resolution Timing

```cpp
// Use RDTSC (Read Time Stamp Counter) for nanosecond precision
inline uint64_t rdtsc() {
    unsigned int lo, hi;
    asm volatile("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// Convert cycles to nanoseconds
double cycles_to_ns(uint64_t cycles) {
    static const double CPU_FREQ_GHZ = 3.5;  // Measure actual frequency
    return cycles / CPU_FREQ_GHZ;
}
```

### Latency Histogram

```cpp
class LatencyHistogram {
    static constexpr int BUCKETS = 1000;
    std::array<uint64_t, BUCKETS> histogram = {};
    uint64_t total_samples = 0;

public:
    void record_ns(uint64_t latency_ns) {
        int bucket = std::min((int)(latency_ns / 100), BUCKETS - 1);
        histogram[bucket]++;
        total_samples++;
    }

    void print_stats() {
        printf("Latency distribution:\n");
        printf("  P50:   %ld ns\n", percentile(50));
        printf("  P95:   %ld ns\n", percentile(95));
        printf("  P99:   %ld ns\n", percentile(99));
        printf("  P99.9: %ld ns\n", percentile(99.9));
        printf("  Max:   %ld ns\n", percentile(100));
    }

private:
    uint64_t percentile(double p) {
        uint64_t count = 0;
        uint64_t target = (uint64_t)(total_samples * p / 100);
        for (int i = 0; i < BUCKETS; i++) {
            count += histogram[i];
            if (count >= target) {
                return (uint64_t)i * 100;
            }
        }
        return 0;
    }
};
```

## Verification & Profiling

### perf (Performance Counters)

```bash
# Measure cache misses and branch mispredictions
perf record -e cycles,cache-misses,branch-misses -g ./trading_system

# View results
perf report

# Generate flame graph
perf script > out.perf
./FlameGraph/stackcollapse-perf.pl out.perf > out.folded
./FlameGraph/flamegraph.pl out.folded > out.svg
```

### Hardware Event Monitoring

```bash
# Monitor only cycles and cache misses
perf stat -e cycles,L1-dcache-load-misses,LLC-load-misses \
    ./trading_system

# Output example:
#  10,000,000,000 cycles
#      500,000,000 L1 cache misses (5%)
#       50,000,000 LLC misses (0.5%)
```

## Final Optimization Checklist

- [ ] CPU frequency fixed (no scaling)
- [ ] Cores isolated from kernel
- [ ] DPDK or kernel bypass in use
- [ ] Hugepages configured
- [ ] NIC driver optimized
- [ ] Hardware timestamping enabled
- [ ] Lock-free data structures
- [ ] Pre-allocated memory pools
- [ ] Cache-line alignment
- [ ] Minimal system calls
- [ ] Latency histograms monitored
- [ ] P99.9 latency target met (<100µs)
- [ ] Thermal management in place
- [ ] Power consumption managed
- [ ] Stress testing completed

## Expected Results

**After full optimization**:
- Mean latency: 10-20µs
- P99 latency: 50-100µs
- P99.9 latency: 100-200µs
- Throughput: 1M+ orders/second
- Jitter: <50µs
- CPU utilization: 80-90%
- Power consumption: 200-300W
