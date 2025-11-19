# Network Troubleshooting Tools Reference

## Command-Line Utilities

### Ping
```bash
# Basic connectivity test
ping -c 4 8.8.8.8

# Specify packet size
ping -s 1472 -c 4 8.8.8.8

# Count hops and RTT
ping -R 8.8.8.8

# Continuous ping with statistics
ping -i 0.2 -c 100 8.8.8.8
# Analyze: loss, rtt min/avg/max/stddev

# Timeout specification
ping -W 2 -c 4 8.8.8.8  # 2 second timeout
```

### Traceroute
```bash
# Trace path to destination
traceroute 8.8.8.8

# UDP probes (default)
traceroute -U 8.8.8.8

# ICMP probes (better through firewalls)
traceroute -I 8.8.8.8

# TCP probes to specific port
traceroute -T -p 443 8.8.8.8

# Limit hop count
traceroute -m 15 8.8.8.8

# Set timeout
traceroute -w 2 8.8.8.8

# Don't resolve hostnames (faster)
traceroute -n 8.8.8.8
```

### Path MTU Discovery
```bash
# Detect path MTU
ping -M do -s 1472 destination

# Incremental MTU finding
ping -M do -s 1472 8.8.8.8  # Works
ping -M do -s 1473 8.8.8.8  # Fails - actual MTU is 1472

# Using -c to send multiple packets
for size in 1500 1490 1480 1472 1460; do
  ping -M do -s $size -c 1 8.8.8.8
done
```

### Route Lookup
```bash
# View routing table
route -n
netstat -rn
ip route show

# Specific route lookup
ip route get 8.8.8.8

# Detailed route information
netstat -rn -A inet

# Default gateway
route | grep default
ip route show | grep default
```

### DNS Resolution
```bash
# Simple host lookup
nslookup example.com
host example.com
dig example.com

# Specific record type
dig example.com A
dig example.com AAAA
dig example.com MX
dig example.com NS

# Authoritative response
dig +norecurse example.com @ns1.example.com

# Trace DNS resolution path
dig +trace example.com

# Query stats
dig +stats example.com

# Reverse DNS
dig -x 8.8.8.8
```

### Netstat/ss
```bash
# Network statistics
netstat -i                  # Interface statistics
netstat -s                  # Protocol statistics
netstat -an | grep ESTABLISHED | wc -l  # Count connections

# Socket statistics (modern replacement)
ss -an                      # All sockets
ss -i                       # Interface statistics
ss -s                       # Summary statistics
ss -tan                     # TCP statistics only
ss -uan                     # UDP statistics only
ss -tnan | grep :22         # SSH connections
ss -tnan | grep LISTEN      # Listening ports
```

### ifconfig/ip
```bash
# Interface configuration (legacy)
ifconfig eth0
ifconfig -a                 # All interfaces

# Modern replacement
ip addr show
ip addr show eth0
ip link show                # Link layer info

# Interface statistics
ip -s link show
ethtool -S eth0            # Detailed interface stats
```

### MTR (My Trace Route)
```bash
# Combined ping + traceroute
mtr -c 100 8.8.8.8

# Report mode (non-interactive)
mtr -r -c 100 8.8.8.8 > mtr_report.txt

# UDP mode
mtr -u 8.8.8.8

# Show only loss percentage
mtr -c 100 -n -o LR 8.8.8.8
```

### Iperf/iPerf3
```bash
# Server mode
iperf3 -s

# Client mode
iperf3 -c server_ip

# Bandwidth test with duration
iperf3 -c server_ip -t 60

# Reverse direction (server to client)
iperf3 -c server_ip -R

# UDP test with bitrate
iperf3 -c server_ip -u -b 100M

# Parallel streams
iperf3 -c server_ip -P 4

# JSON output
iperf3 -c server_ip -J > results.json
```

## Packet Analysis Tools

### Tcpdump Summary Commands
```bash
# Capture count by source IP
tcpdump -r capture.pcap -nn ip | awk '{print $1}' | sort | uniq -c | sort -rn | head

# Top 10 protocols
tcpdump -r capture.pcap -nn | awk '{print $5}' | sed 's/,.*//' | sort | uniq -c | sort -rn | head

# Extract unique destinations
tcpdump -r capture.pcap -nn 'ip' | awk '{print $(NF-2)}' | sort | uniq

# Count packets by port
tcpdump -r capture.pcap -nn 'tcp' | awk -F. '{print $(NF-1)"."$NF}' | sort | uniq -c | sort -rn
```

### Tshark Commands
```bash
# Convert capture to text
tshark -r capture.pcap > output.txt

# Extract specific fields
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.dstport

# Statistics
tshark -r capture.pcap -q -z conv,ip

# Protocol distribution
tshark -r capture.pcap -q -z io,phs

# Endpoint statistics
tshark -r capture.pcap -q -z endpoints,ip
```

## Network Configuration Troubleshooting

### Verify Configuration
```bash
# Check interface status
ip link show
ethtool eth0

# Check IP configuration
ip addr show
ip route show

# Check DNS
cat /etc/resolv.conf
nslookup example.com @8.8.8.8

# Check network services
netstat -tlnp | grep LISTEN
ss -tlnp | grep LISTEN
```

### ARP Troubleshooting
```bash
# View ARP cache
arp -a
ip neigh show

# Clear ARP cache (Linux)
ip -s neigh flush all

# Add static ARP entry
arp -s 192.168.1.1 00:11:22:33:44:55
ip neigh add 192.168.1.1 lladdr 00:11:22:33:44:55 dev eth0

# Monitor ARP activity
tcpdump -i eth0 arp
arp-watch (package needed)
```

## Device-Specific Commands

### Cisco IOS
```
# Interface status
show interfaces
show interfaces brief

# Routing table
show ip route
show ip route 8.8.8.8

# BGP status
show ip bgp summary
show ip bgp neighbors

# SNMP test
snmp-server group TEST v3 auth

# Ping from device
ping 8.8.8.8
ping -df -s 1472 8.8.8.8  # Test MTU
```

### Juniper Junos
```
# Interface status
show interfaces terse
show interfaces ge-0/0/0 extensive

# Routing table
show route table inet.0
show route 8.8.8.8

# Connectivity test
request ping 8.8.8.8
request traceroute 8.8.8.8

# SNMP traps
show snmp trap

# Statistics
show interfaces statistics
```

### Linux Network Namespace
```bash
# Create namespace
ip netns add nettest

# Run commands in namespace
ip netns exec nettest ping 8.8.8.8
ip netns exec nettest ifconfig

# Debug namespace routing
ip netns exec nettest ip route show

# Delete namespace
ip netns delete nettest
```

## Performance Measurement Tools

### Qperf
```bash
# Latency measurement
qperf server_ip latency

# Bandwidth measurement
qperf server_ip bandwidth

# Combined test
qperf server_ip latency bandwidth

# TCP vs UDP
qperf server_ip tcp_lat tcp_bw
qperf server_ip udp_lat udp_bw
```

### Netperf
```bash
# TCP throughput
netperf -H server_ip -t TCP_STREAM

# TCP latency
netperf -H server_ip -t TCP_RR

# UDP throughput
netperf -H server_ip -t UDP_STREAM

# Detailed output
netperf -H server_ip -t TCP_STREAM -- -m 1024
```

### Hping3
```bash
# TCP connectivity
hping3 -S -p 80 8.8.8.8

# Traceroute
hping3 --traceroute -S -p 443 8.8.8.8

# MTU discovery
hping3 -S -p 22 -d 1472 --mtu 8.8.8.8

# Firewall testing
hping3 -F -S -R -p 22 8.8.8.8
```

## Advanced Diagnostic Tools

### Netcat/Socat
```bash
# Port listening
nc -l 5000

# Port connectivity test
nc -zv -w2 example.com 22
nc -zv -w2 example.com 80-443

# TCP relay
nc -l 5000 | nc 192.168.1.2 5000
```

### Scapy (Python)
```python
from scapy.all import *

# Send custom packet
packet = IP(dst="8.8.8.8")/ICMP()
send(packet)

# Receive response
response = sr1(IP(dst="8.8.8.8")/ICMP(), timeout=2)

# Port scanning
for p in range(20,25):
    pkt = sr1(IP(dst="target")/TCP(dport=p),timeout=0.5)
    if pkt.haslayer(TCP):
        print(f"Port {p}: {pkt[TCP].flags}")

# Packet crafting and analysis
pkt = IP()/TCP(dport=443,flags="S")
```

## Network Monitoring Tools

### Iftop
```bash
# Top bandwidth consumers
iftop -i eth0

# Show source/dest
iftop -i eth0 -n

# Filter to specific host
iftop -i eth0 -n -f "host 192.168.1.1"
```

### nethogs
```bash
# PID-based traffic statistics
nethogs eth0

# Combined interface view
nethogs
```

## Implementation Checklist

- [ ] Master ping for connectivity testing
- [ ] Learn traceroute for path analysis
- [ ] Understand netstat/ss output
- [ ] Practice tcpdump filtering
- [ ] Become proficient with Wireshark
- [ ] Learn device-specific commands
- [ ] Set up performance measurement tools
- [ ] Create troubleshooting procedures
- [ ] Document known issues and resolutions
- [ ] Build automated diagnostic scripts
- [ ] Test tools on lab network first
- [ ] Maintain tool documentation

---

**Reference Type**: Diagnostic Tools
**Primary Use**: Network troubleshooting
**Common Tools**: tcpdump, Wireshark, ping, traceroute, netstat
**Last Updated**: 2025-11-19
