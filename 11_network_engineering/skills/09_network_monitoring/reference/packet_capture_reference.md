# Packet Capture Reference

## Packet Capture Tools

### Tcpdump

#### Basic Syntax
```
tcpdump [options] [filter]

Common options:
  -i interface      Interface to capture on
  -n               Don't resolve hostnames
  -nn              Don't resolve hostnames or port numbers
  -A               Print in ASCII
  -X               Print in hex and ASCII
  -v               Verbose output
  -vv              More verbose
  -w file          Write to file (libpcap format)
  -r file          Read from file
  -c count         Capture specified number of packets
  -s snaplen       Snapshot length (bytes to capture per packet)
  -D               List available interfaces
  -t               Don't print timestamps
  -tt              Print timestamps in seconds since epoch
  -tttt            Print timestamps with date
  -e               Print MAC addresses
```

#### Capture Examples

##### All Traffic on Interface
```
tcpdump -i eth0 -v
```

##### Specific Host
```
tcpdump -i eth0 host 192.168.1.100
```

##### Specific Network
```
tcpdump -i eth0 net 192.168.1.0/24
```

##### Specific Protocol
```
tcpdump -i eth0 icmp
tcpdump -i eth0 tcp
tcpdump -i eth0 udp
tcpdump -i eth0 arp
```

##### Port Specific
```
tcpdump -i eth0 port 80
tcpdump -i eth0 src port 22
tcpdump -i eth0 dst port 443
tcpdump -i eth0 portrange 5000-6000
```

##### Complex Filters
```
tcpdump -i eth0 'tcp port 22 and host 192.168.1.100'
tcpdump -i eth0 'not (arp or stp or lldp)'
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'  # SYN packets
tcpdump -i eth0 '(src 192.168.1.0/24) and (dst port 80 or dst port 443)'
```

### Wireshark

#### Installation
```
Linux:
sudo apt-get install wireshark wireshark-common

macOS:
brew install wireshark

Windows:
Download installer from wireshark.org
```

#### Capture Filters
Limit capture volume before processing
```
tcp port 443
host 192.168.1.1
ip and not tcp
src net 10.0.0.0/8
```

#### Display Filters
Post-capture filtering for analysis
```
ip.addr == 192.168.1.100
tcp.port == 22
http
dns.qry.name contains "example.com"
frame.time_relative > 5
```

## Capture Filter Expressions

### Primitives

#### Protocol
```
tcp, udp, icmp, arp, ip, ip6, vlan
```

#### Direction
```
src    - Source address
dst    - Destination address
src or dst - Either
```

#### Type
```
host    - Single host
net     - Network (CIDR)
port    - Port number
portrange - Port range
```

#### Logical Operators
```
and, or, not
( )     - Grouping
! or not - Negation
```

### Common Filters

#### TCP SYN Scan Detection
```
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack = 0'
```

#### DNS Traffic
```
tcpdump -i eth0 'udp port 53'
```

#### Web Traffic
```
tcpdump -i eth0 'tcp port 80 or tcp port 443'
```

#### Specific VLAN
```
tcpdump -i eth0 'vlan 100'
```

#### Large Packets (potential fragments)
```
tcpdump -i eth0 'greater 1500'
```

## Display Filters (Wireshark/Tshark)

### Common Filters

#### Application Layer
```
http.request.method == "GET"
http.response.code == 200
dns.qry.type == "A"
ssh.message
ftp.request.command == "USER"
```

#### Transport Layer
```
tcp.flags.syn == 1
tcp.flags.fin == 1
tcp.analysis.retransmission
udp.length > 500
```

#### Network Layer
```
ip.src == 192.168.1.1
ip.dst_host == example.com
ip.ttl < 64
icmp.type == 8
```

#### Data Link Layer
```
eth.src == 00:11:22:33:44:55
eth.type == 0x0800
arp.opcode == 1
vlan.id == 100
```

## Packet Analysis Workflow

### 1. Capture Phase
```
tcpdump -i eth0 -w capture.pcap 'tcp port 80'
```

### 2. Initial Review
```
tcpdump -r capture.pcap -n
```

### 3. Statistics
```
tcpdump -r capture.pcap -nn | awk '{print $3}' | sort | uniq -c | sort -rn | head
```

### 4. Detailed Analysis
```
# Use Wireshark GUI
# or tshark for CLI analysis

tshark -r capture.pcap -Y 'http' -T fields -e ip.src -e http.host -e http.request.uri
```

## Protocol Analysis

### TCP Connection Analysis
```
1. Identify SYN packets
2. Match SYN with SYN-ACK
3. Verify ACK response
4. Monitor data transfer
5. Identify FIN/RST termination
```

### Performance Metrics from Captures

#### Round Trip Time (RTT)
```
Measure: Request sent → Response received
Method: Track packet timestamps
Tool: Wireshark "Follow TCP Stream"
```

#### Retransmissions
```
Indicator: Duplicate sequence numbers
Analysis: Calculate retransmission rate
Threshold: >0.5% indicates issues
```

#### Timeouts
```
Detection: Idle connection > timeout value
TCP timeout: Typically 30-60 seconds
Application timeout: Variable by application
```

## Linux Command Examples

### Monitor Interface Statistics
```
# Real-time interface stats
watch -n 1 'ip -s link show eth0'

# Summary statistics
netstat -i

# Detailed counters
ethtool -S eth0
```

### Extract PCAP Statistics
```
# Packet count by source IP
tcpdump -r capture.pcap -nn | awk '{print $1}' | sort | uniq -c | sort -rn

# Protocol distribution
tcpdump -r capture.pcap -nn | awk '{print $5}' | sed 's/,.*//' | sort | uniq -c

# Port distribution
tcpdump -r capture.pcap -nn 'tcp' | awk -F. '{print $(NF-1)"."$NF}' | sort | uniq -c
```

### tcpstat for Traffic Analysis
```
tcpstat -f capture.pcap -o 'summary.txt' -d eth0
```

## Capture Size Considerations

### Snapshot Length (-s option)
```
Default: 65535 bytes (full packet)
Typical: 65535 (full capture)
Minimal: 0 (full length, same as -s0)
Limited: 128-256 (headers only)
```

### Ring Buffer Capture
```
tcpdump -i eth0 -w - | tee capture-$(date +%s).pcap | tcpdump -r -
```

### Rotating Capture Files
```
tcpdump -i eth0 -G 3600 -w 'capture-%s.pcap'
# Creates new file every 3600 seconds (1 hour)
```

## Privacy Considerations

### Payload Redaction
```
tcpdump -i eth0 -w capture.pcap -l | xxd -p | sed 's/../ XX /g'
```

### Header-Only Capture
```
tcpdump -i eth0 -s 64 -w capture.pcap
# Capture first 64 bytes (headers) only
```

### Packet De-identification
```
# Use editcap from Wireshark
editcap -C 65535 -S 64 capture.pcap output.pcap
```

## Common Network Issues

### Connectivity Problems
```
Capture at both ends:
- Source: tcpdump -i eth0 host <destination>
- Destination: tcpdump -i eth0 host <source>
- Compare traffic timing and sequence
```

### Performance Issues
```
Monitor for:
- Retransmissions
- Duplicate ACKs
- Window size reduction
- Out-of-order packets
```

### DNS Issues
```
tcpdump -i eth0 -A 'udp port 53'
# Watch for:
# - Query/response matching
# - Timeouts (no response)
# - NXDOMAIN responses
```

### VoIP/Latency Issues
```
tcpdump -i eth0 'udp port 5060 or udp portrange 5000-6000'
# Monitor for:
# - Packet loss
# - Latency spikes
# - Out-of-order delivery
```

## Implementation Checklist

- [ ] Install tcpdump and Wireshark
- [ ] Understand capture vs display filters
- [ ] Practice common filtering syntax
- [ ] Identify baseline traffic patterns
- [ ] Establish retention policies
- [ ] Automate routine captures
- [ ] Create filter templates
- [ ] Document capture procedures
- [ ] Consider privacy implications
- [ ] Plan disk space for captures
- [ ] Test capture rotation
- [ ] Establish evidence handling procedures

---

**Reference Type**: Network Analysis Tools
**Primary Use**: Packet-level troubleshooting
**Key Tools**: tcpdump, Wireshark, tshark
**Last Updated**: 2025-11-19
