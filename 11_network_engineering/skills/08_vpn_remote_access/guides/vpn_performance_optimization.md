# VPN Performance Optimization Guide

## Performance Baseline Establishment

### Metrics to Track

```
Throughput Metrics:
  - TCP throughput (Mbps)
  - UDP throughput (Mbps)
  - Encryption throughput (Gbps for hardware)
  - Decryption throughput

Latency Metrics:
  - One-way latency (ms)
  - Round-trip time (RTT)
  - Jitter (variance in latency)
  - Packet loss (%)

Resource Metrics:
  - CPU utilization (%)
  - Memory usage (MB)
  - Bandwidth utilization (%)
  - Cache hit ratio (%)

Connection Metrics:
  - Active connections
  - Connection establishment time
  - Session duration
  - Reconnection time
```

### Baseline Testing Procedure

```bash
# 1. No VPN Baseline
iperf3 -c <direct_server> -t 60 -J > baseline.json

# 2. With VPN (same encryption as production)
iperf3 -c <vpn_resource> -t 60 -J > vpn_performance.json

# 3. Multiple runs for average
for i in {1..5}; do
  iperf3 -c <vpn_resource> -t 60 >> results.txt
done

# 4. Calculate statistics
# Expected VPN overhead: 10-30% depending on encryption
```

## Encryption Algorithm Optimization

### Algorithm Selection Matrix

```
Performance Priority:
┌─────────────────────┬────────────────┬──────────────────────┐
│ Algorithm           │ Throughput     │ Security Level       │
├─────────────────────┼────────────────┼──────────────────────┤
│ ChaCha20-Poly1305   │ Excellent      │ Very High (modern)   │
│ AES-256-GCM (HW)    │ Excellent      │ Very High            │
│ AES-128-GCM (HW)    │ Excellent      │ High                 │
│ AES-256-CBC         │ Good           │ Very High            │
│ AES-128-CBC         │ Very Good      │ High                 │
│ 3DES                │ Poor           │ Medium (deprecated)  │
└─────────────────────┴────────────────┴──────────────────────┘

Recommendations:
  For maximum security: AES-256-GCM
  For best balance: AES-256-GCM with hardware acceleration
  For older hardware: ChaCha20-Poly1305 (CPU efficient)
  For compliance: AES-256 variants
```

### Hardware Acceleration

**Check for AES-NI Support**

```bash
# Linux/macOS
grep aes /proc/cpuinfo
# Output: aes (if supported)

# Windows PowerShell
Get-WmiObject win32_processor | Select-Object Name

# macOS
sysctl -a | grep machdep.cpu.features
```

**Enable Hardware Acceleration**

```
Cisco ASA:
  crypto ikev2 proposal PROPOSAL
    encryption aes-256  ! Uses AES-NI automatically
    integrity sha256
    group 14

OpenVPN:
  cipher AES-256-GCM  ! Automatically uses AES-NI if available

WireGuard:
  ! Uses ChaCha20 by default (CPU efficient)
  ! Intel: Automatically uses AES-NI for interoperability

Linux Kernel:
  # Enable AES-NI module
  modprobe aesni_intel

  # Verify
  grep aesni /proc/crypto
```

**Performance Impact**

```
Without AES-NI:
  AES-256-GCM: 1.5 Gbps (CPU bound)

With AES-NI:
  AES-256-GCM: 8-10 Gbps (memory bound)

Improvement: 5-6x performance gain
```

## MTU and MSS Optimization

### Understanding MTU Overhead

```
Standard Network MTU: 1500 bytes

VPN Overhead Examples:
  IPsec ESP: 50-73 bytes
  OpenVPN: 14-50 bytes
  WireGuard: 60 bytes
  GRE: 24 bytes

Calculation:
  Optimal VPN MTU = Network MTU - VPN Overhead
  = 1500 - 60 = 1440 bytes (for OpenVPN)
  = 1500 - 73 = 1427 bytes (for IPsec)
```

### MTU Tuning

**Linux**

```bash
# Test current MTU
ping -M do -s 1472 <vpn_server>
# If fails: fragmentation occurring

# Find maximum MTU
for size in 1500 1480 1460 1440 1420 1400; do
  echo "Testing $size..."
  ping -M do -s $size <vpn_server>
done

# Set optimal MTU
ip link set mtu 1400 dev tun0

# Verify
ip link show tun0
# Output: mtu 1400
```

**Windows**

```cmd
REM View current MTU
netsh interface ipv4 show subinterface

REM Set MTU for specific interface
netsh interface ipv4 set subinterface "VPN" mtu=1400 store=persistent

REM For WireGuard
netsh interface ipv4 set subinterface "WireGuard" mtu=1380 store=persistent
```

### MSS Clamping

```bash
# Linux: TCP MSS clamping (negotiation optimization)
iptables -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --clamp-mss-to-pmtu

# Cisco ASA
policy-map PMTUD
class all
  set connection mss-clamp 1350

service-policy PMTUD interface outside
```

### PMTUD (Path MTU Discovery) Issues

```
Problem: Large packets silently dropped
  - ICMP "too big" responses filtered
  - Packets lost without notification
  - Connection stalls

Solutions:
1. Manual MSS adjustment (most reliable)
2. Enable DF (Don't Fragment) handling
3. Reduce local MTU conservatively
4. Use tcp-mss-adjust

Testing:
  ping -M do -s 1500 <destination>
  # -M do = Don't Fragment

Troubleshooting:
  if no response -> likely fragmentation issue
  if response -> MTU is fine
```

## Compression Strategy

### When to Use Compression

```
Use Compression If:
  ✓ Bandwidth-limited WAN links (< 10 Mbps)
  ✓ Text-based protocols (HTTP, SMTP, SSH)
  ✓ Large file transfers over slow links
  ✓ Log transmission to central server

Avoid Compression If:
  ✓ High-speed links (> 100 Mbps)
  ✓ Already-compressed data (MP4, ZIP, JPEG)
  ✓ Latency-sensitive traffic (VoIP, gaming)
  ✓ Real-time applications
```

### Compression Configuration

**OpenVPN**

```
Enable compression:
  Server: compress lz4-v2
  Client: push "compress lz4-v2"

Disable compression:
  compress none    ! Explicitly disable

LZO vs LZ4:
  LZ4: Faster (modern, recommended)
  LZO: Legacy (older, slower)

Test performance:
  With compression: iperf3 -c <server>
  Without compression: iperf3 -c <server>
  Compare results
```

**IPsec**

```
IPsec compression:
  crypto ipsec transform-set COMPRESS esp-aes 256 esp-sha compress lzs

  Note: Rarely used (increases latency, marginal gains)
```

### Compression Performance Trade-offs

```
Text Compression Results:
  Original: 1000 KB
  Compressed: 250 KB (75% reduction)
  CPU cost: 5% CPU to compress/decompress
  Network savings: 750 KB
  Benefit: YES (saves bandwidth)

Video Compression Results:
  Original: 1000 KB (already compressed)
  Compressed: 995 KB (0.5% reduction)
  CPU cost: 15% CPU wasted
  Network savings: 5 KB
  Benefit: NO (CPU cost exceeds gain)

Recommendation:
  Compress text, log, and JSON
  Skip video, images, and archives
```

## Buffer and Queue Optimization

### Tuning Socket Buffers

**Linux**

```bash
# View current settings
cat /proc/sys/net/ipv4/tcp_rmem
# Output: 4096 131072 6291456

cat /proc/sys/net/ipv4/tcp_wmem
# Output: 4096 16384 4194304

# Optimize for VPN (high latency, high BW)
sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"
sysctl -w net.core.rmem_max=67108864
sysctl -w net.core.wmem_max=67108864

# Make permanent
cat >> /etc/sysctl.conf << EOF
net.ipv4.tcp_rmem=4096 87380 67108864
net.ipv4.tcp_wmem=4096 65536 67108864
net.core.rmem_max=67108864
net.core.wmem_max=67108864
EOF

sysctl -p
```

**Windows**

```powershell
# Set TCP receive buffer
netsh int tcp set global autotuninglevel=normal

# Set receive buffer size (bytes)
netsh int tcp set global recvbuf=2097152

# Enable TCP auto-tuning
netsh int tcp set global autotuninglevel=restricted
```

**IPsec Device Tuning**

```
Cisco ASA:
  sndbuf 393216   ! 384 KB send buffer
  rcvbuf 393216   ! 384 KB receive buffer

These settings increase memory but improve throughput
```

### Queue Configuration

```
IKE Retransmission:
  Default: Retransmit every 500ms (too aggressive)
  Optimized: Retransmit every 1-2 seconds

  crypto ikev2 policy 1
    lifetime 28800
    dpd 10 3 on-demand

Traffic Queue:
  Default: FIFO (First In, First Out)
  For VPN: Can add QoS shaping
```

## Multi-Core and Threading

### Parallelization Strategies

**OpenVPN Multi-Threading**

```bash
# Enable multi-threading
server.conf:
thread-pool-size 8    ! Use 8 threads
```

**IPsec Multiple Workers**

```
IPsec processing:
  Default: Single threaded
  Optimized: Multiple workers (per core)

For N cores:
  ipsec-worker-threads N
```

**Load Distribution**

```
Multiple VPN Instances (OpenVPN):
  Instance 1: port 1194 (core 0-1)
  Instance 2: port 1195 (core 2-3)
  Instance 3: port 1196 (core 4-5)

Clients connected to:
  DNS round-robin or load balancer
  Distributes connections evenly
  Better CPU utilization
```

**CPU Affinity**

```bash
# Bind process to specific CPU
taskset -c 0-3 openvpn --config server.conf

# Verify
ps aux | grep openvpn
# Check CPU binding in logs
```

## QoS and Traffic Shaping

### VPN-Aware QoS

```
Network Priority Classification:
  Priority 1 (Critical): SAP, Oracle, SQL
  Priority 2 (Business): Office 365, WebEx
  Priority 3 (Best Effort): Web, FTP
  Priority 4 (Low): Video, Social media

VPN Configuration:
  Match traffic by port/protocol
  Apply priority in VPN gateway
  Enforce on both ingress/egress
```

**Cisco Configuration**

```cisco
! Define traffic classes
class-map VPN-CRITICAL
  match access-group 101

! Create policy
policy-map VPN-QOS
  class VPN-CRITICAL
    priority percent 40
  class class-default
    fair-queue

! Apply to interface
interface Tunnel0
  service-policy output VPN-QOS
```

### Bandwidth Management

```
Per-User Limits:
  Executive: 50 Mbps guaranteed, 100 Mbps burst
  Regular User: 10 Mbps guaranteed, 25 Mbps burst
  Contractor: 5 Mbps guaranteed, 10 Mbps burst

Implementation:
  IPsec: Per-SA policing
  OpenVPN: Per-client cgroups (Linux)
  WireGuard: Per-peer traffic rules
```

## Encryption Key Refresh

### Rekey Optimization

```
Default Rekey Frequency:
  IKEv1: Every 28800 seconds (8 hours)
  IKEv2: Every 28800 seconds (8 hours)
  OpenVPN: Every 3600 seconds (1 hour)

Tuning:
  More frequent: More secure, higher CPU
  Less frequent: Less secure, lower CPU

Recommendation:
  Security-critical: 1800 seconds (30 min)
  Standard: 3600 seconds (1 hour)
  Performance-sensitive: 28800 seconds (8 hours)

Configuration:
  lifetime 1800  ! Rekey every 30 minutes
```

### Session Resumption

```
TLS Session Caching:
  Speeds up handshake for reconnecting clients
  Default: 300 second cache

SSL VPN (OpenVPN):
  session-cache-size 20000  ! Cache 20k sessions
  # Significantly speeds reconnection

IPsec IKEv2:
  ! IKEv2 has built-in fast resumption
  Session resumption supported automatically
```

## Monitoring for Bottlenecks

### Real-time Monitoring

```bash
# Network throughput
iftop -i tun0       ! Shows per-flow throughput

# CPU usage per process
top -p <vpn_pid>    ! Monitor VPN process

# Detailed statistics
netstat -i          ! Interface statistics
ss -s               ! Socket statistics
iostat -x 1         ! Disk I/O (if disk-backed cache)
```

### Performance Indicators

```
Good Performance:
  ✓ CPU utilization < 70%
  ✓ Memory stable (not increasing)
  ✓ Throughput > 80% of baseline
  ✓ Latency < baseline + 10 ms
  ✓ Packet loss < 0.1%

Performance Issues:
  ✗ CPU at 100% (bottlenecked)
  ✗ Memory leaks (increasing over time)
  ✗ Throughput < 50% baseline
  ✗ Latency > baseline + 50 ms
  ✗ Packet loss > 1%
```

### Profiling

```bash
# Identify hotspots in encryption
perf record -g openvpn --config server.conf
perf report

# Flame graph visualization
# Shows which functions consume CPU
```

## End-to-End Performance Testing

### Comprehensive Test Plan

```
Phase 1: Baseline (No VPN)
  - TCP throughput
  - UDP throughput
  - Latency
  - Jitter

Phase 2: VPN Performance
  - Same tests through VPN
  - Record with different ciphers
  - Different compression settings

Phase 3: Scale Testing
  - 10 concurrent users
  - 50 concurrent users
  - 100 concurrent users
  - Monitor CPU, memory, connections

Phase 4: Stress Testing
  - Maximum connections
  - Maximum throughput
  - Monitor for failures
  - Record breaking point

Phase 5: Long-Duration
  - 24-hour continuous test
  - Monitor for memory leaks
  - Check for session drift
  - Verify stability
```

### Capacity Planning

```
From test results:
  Max connections per gateway: 500
  Max throughput per gateway: 8 Gbps
  CPU per connection: 1%
  Memory per connection: 5 MB

Planning:
  For 1000 users: 2 gateways needed
  For 5 Gbps throughput: 1 gateway sufficient
  For redundancy: Minimum 2 gateways
  Growth buffer: Add 50% capacity cushion
```

## Best Practices Summary

- [ ] Establish baseline before optimization
- [ ] Use hardware acceleration (AES-NI, etc.)
- [ ] Optimize MTU to minimize fragmentation
- [ ] Use compression only for text/log data
- [ ] Configure appropriate buffer sizes
- [ ] Implement QoS for traffic classification
- [ ] Use multi-core/threading when available
- [ ] Monitor performance continuously
- [ ] Test thoroughly before production
- [ ] Document all optimizations applied
- [ ] Plan for growth and redundancy
- [ ] Regular capacity planning reviews
