# Packet Capture Analysis Guide

## Capture Planning

### Determine What to Capture
```
Problem: Application not working
Capture:
  - All traffic to application server
  - Specific TCP/UDP ports
  - Related DNS queries

Decision tree:
  - Layer 3 issue? → Capture IP layer
  - Layer 4 issue? → Capture TCP/UDP
  - Application issue? → Capture full packets
  - Performance issue? → Capture to analyze timing
```

### Capture Duration
```
Short term (troubleshooting):
  - 5-15 minutes
  - Capture during problem occurrence
  - Start before issue, stop after

Baseline (characterization):
  - 1-4 hours
  - Capture during normal operation
  - Multiple times of day

Long term (trending):
  - Daily captures
  - Rotating files
  - 30-90 day retention
```

## Capture Implementation

### Basic tcpdump Commands

#### Capture to File
```bash
# Capture all traffic on interface
sudo tcpdump -i eth0 -w capture.pcap

# Capture with size limit
sudo tcpdump -i eth0 -w capture.pcap -C 100 -W 5
# Creates 5 files of 100MB each (total 500MB)

# Capture with time rotation
sudo tcpdump -i eth0 -w 'capture_%Y%m%d_%H%M%S.pcap' -G 3600
# Creates new file every 3600 seconds (1 hour)

# Capture with filter
sudo tcpdump -i eth0 -w capture.pcap 'tcp port 443'

# Rotate and compress
sudo tcpdump -i eth0 -w - 'tcp port 22' | gzip > ssh_capture.pcap.gz
```

#### Live Display (Limited)
```bash
# Show first 100 packets
sudo tcpdump -i eth0 -c 100

# Show verbose headers
sudo tcpdump -i eth0 -v

# Show hex dump of packets
sudo tcpdump -i eth0 -XX

# Show ASCII payload
sudo tcpdump -i eth0 -A
```

### Advanced Filter Combinations

#### Problem: Slow Web Response
```bash
# Capture HTTP traffic to specific server
sudo tcpdump -i eth0 -w http_slow.pcap \
  'host webserver.example.com and tcp port 80'

# Analysis: Compare request/response timing
```

#### Problem: Packet Loss
```bash
# Capture all traffic on link
sudo tcpdump -i eth0 -w loss_capture.pcap -s 65535

# Later analyze for:
# - Retransmissions
# - Out-of-order packets
# - Duplicate ACKs
```

#### Problem: DDoS Investigation
```bash
# Capture attack traffic
sudo tcpdump -i eth0 -w ddos.pcap \
  'src net 10.0.0.0/24' -W 100 -C 50

# Analyze for:
# - Source IP distribution
# - Port scanning patterns
# - Packet type distribution
```

## Wireshark Analysis Workflow

### Step 1: Load Capture
```
1. Open Wireshark
2. File → Open
3. Select capture file
4. Wait for indexing to complete
```

### Step 2: Initial Inspection
```
1. Review packet list
   - Check timestamp range
   - Identify protocols present
   - Count packets

2. Check expert info
   - Analyze → Expert Info
   - Look for warnings/errors
   - Identify issues

3. Protocol hierarchy
   - Statistics → Protocol Hierarchy
   - Understand traffic composition
```

### Step 3: Focused Analysis

#### TCP Connection Analysis
```
Find connection:
  1. Right-click SYN packet
  2. Filter → By Color
  3. Follow → TCP Stream

Analyze:
  - Trace SYN, SYN-ACK, ACK
  - Identify FIN/RST
  - Measure RTT per segment
  - Look for retransmissions
```

#### HTTP Analysis
```
1. Apply display filter: http
2. Right-click on request packet
3. Follow → HTTP Stream
4. Examine:
   - Request headers
   - Response code
   - Response time
   - Payload content
```

#### DNS Analysis
```
1. Apply filter: dns
2. Statistics → DNS
3. Review:
   - Query types
   - Response codes (0=ok, 3=NXDOMAIN)
   - Resolution times
   - Failed queries
```

## Command-Line Analysis

### Extract Statistics
```bash
# Total packets
tcpdump -r capture.pcap -q | wc -l

# Source IPs
tcpdump -r capture.pcap -nn 'ip' | awk '{print $1}' | sort | uniq -c | sort -rn

# Destination ports
tcpdump -r capture.pcap -nn 'tcp' | awk '{print $(NF-2)}' | sort | uniq -c | sort -rn

# Protocol distribution
tcpdump -r capture.pcap -q | awk '{print $5}' | sed 's/,$//' | sort | uniq -c | sort -rn
```

### tshark Commands
```bash
# Extract specific fields
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.dstport

# Count packets by protocol
tshark -r capture.pcap -q -z io,phs

# Extract HTTP URLs
tshark -r capture.pcap -Y http.request -T fields -e http.host -e http.request.uri

# Find retransmissions
tshark -r capture.pcap -Y 'tcp.analysis.retransmission'

# Create CSV output
tshark -r capture.pcap -T fields \
  -e frame.time -e ip.src -e ip.dst -e tcp.dstport \
  -E header=y -E separator=, > output.csv
```

## Performance Analysis

### Latency Measurement

#### Round Trip Time (RTT)
```
1. Open capture in Wireshark
2. Statistics → TCP Stream Analysis
3. Review RTT column
4. Identify:
   - High RTT values (>100ms)
   - RTT spikes
   - Increasing trends
```

#### One-Way Latency (Requires Special Setup)
```
1. Use network TAP and two capture points
2. Synchronize time between capture points
3. Compare timestamps
4. Calculate: response_time - request_time
```

### Throughput Analysis

#### Throughput Graph
```
Wireshark:
1. Statistics → TCP Stream Graphs
2. Select connection
3. Throughput graph shows:
   - Throughput over time
   - Throughput drop-offs
   - Stalled periods
```

#### Command-line
```bash
# Bytes per second
tcpdump -r capture.pcap -q | awk '{total+=$5} END {print "Total bytes:", total}'

# Calculate throughput
# bytes * 8 / (capture_duration_seconds)
```

## Common Issues Detection

### Retransmissions
```
Indicator: TCP.flags.syn=1 appearing multiple times from same source

Cause:
  - Network congestion
  - Packet loss
  - Application not responding

Detection:
  Display filter: tcp.analysis.retransmission
  Count occurrences
```

### Out-of-Order Packets
```
Detection:
  Display filter: tcp.analysis.out_of_order

Cause:
  - Route asymmetry
  - Buffer overflow
  - Network reordering

Analysis:
  1. Identify source/dest
  2. Correlate with loss
  3. Check if temporary
```

### Zero Window
```
Detection:
  Display filter: tcp.analysis.zero_window

Meaning:
  - Receiver buffer full
  - Cannot accept more data
  - Sender must wait

Action:
  1. Check receiver capacity
  2. Monitor for recovery
  3. If persistent, investigate app
```

### Duplicate ACKs
```
Detection:
  Display filter: tcp.analysis.duplicate_ack

Meaning:
  - Fast retransmit triggered
  - Indicates packet loss
  - Usually 3+ duplicates

Impact:
  - Triggers TCP fast recovery
  - Reduces window size
  - Decreases throughput
```

## Advanced Techniques

### Decryption
```
For HTTPS/TLS:
1. Capture with client private key
2. Wireshark → Preferences → Protocols → TLS
3. Add RSA key file
4. Restart Wireshark
5. Now can see decrypted content

Note: Requires access to private key
      HKDF format recommended
```

### Packet Carving
```
Extract files from traffic:
1. File → Export Objects
   - HTTP
   - SMB
   - FTP
   - DICOM

2. Select object
3. Save to disk
```

### Custom Columns
```
Wireshark:
1. Edit → Preferences
2. Appearance → Columns
3. Add custom column
4. Field name: http.response.code
5. View response codes in list
```

## Troubleshooting Scenarios

### Scenario: Database Connection Fails

Capture Plan:
```
1. Capture on client toward database server
2. Filter: tcp port 3306
3. Duration: 5 minutes
4. Analyze:
   - TCP SYN arrives
   - SYN-ACK response? (if not, firewall blocks)
   - Data exchange or RST? (if RST, app refuses)
   - Full conversation? (track errors)
```

### Scenario: Intermittent Connectivity

Capture Plan:
```
1. Long capture (4 hours)
2. Continuous traffic (ping, flow)
3. Rotate files every 30 minutes
4. When issue occurs:
   - Note time
   - Stop capture
   - Analyze that time window
5. Look for:
   - Packet loss bursts
   - High latency
   - Path changes
```

## Storage & Management

### File Management
```
Retain captures:
  - Active troubleshooting: 1 week on-disk
  - Archive: 1 month on external storage
  - Deep analysis: 6 months compressed

Compression:
  Original: capture.pcap (1GB)
  Compressed: capture.pcap.gz (100MB, 10% compression)
  Command: gzip -9 capture.pcap
```

### Automated Capture Script
```bash
#!/bin/bash
# Daily capture script

INTERFACE=eth0
CAPTURE_DIR=/var/captures
DATE=$(date +%Y%m%d_%H%M%S)
FILE="$CAPTURE_DIR/capture_$DATE.pcap"

# Rotate old captures (keep 30 days)
find $CAPTURE_DIR -name "capture_*.pcap" -mtime +30 -delete

# Capture for 24 hours
timeout 86400 tcpdump -i $INTERFACE \
  -w $FILE \
  -C 500 \
  -W 100 \
  'not (arp or broadcast)'

# Compress
gzip -9 $FILE

# Remove very old compressed files
find $CAPTURE_DIR -name "*.pcap.gz" -mtime +90 -delete
```

## Implementation Checklist

- [ ] Verify tcpdump/Wireshark installed
- [ ] Test basic capture commands
- [ ] Learn display filter syntax
- [ ] Practice protocol analysis
- [ ] Create filter templates
- [ ] Set up automated capture scripts
- [ ] Plan storage strategy
- [ ] Document procedures
- [ ] Create troubleshooting guide
- [ ] Train team
- [ ] Build baseline captures
- [ ] Test on non-prod first

---

**Guide Type**: Analysis Techniques
**Tools**: tcpdump, Wireshark, tshark
**Use Case**: Network troubleshooting
**Skill Level**: Intermediate to Advanced
**Last Updated**: 2025-11-19
