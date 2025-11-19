# Wireshark Reference

## Wireshark Fundamentals

### Starting a Capture

#### GUI Method
```
1. Open Wireshark
2. Select interface from main window
3. Click shark fin icon to start
4. Traffic appears in packet list
```

#### Command Line (tshark)
```bash
# Capture packets
tshark -i eth0 -w capture.pcap

# Display packets during capture
tshark -i eth0 -c 100

# Save to file with filter
tshark -i eth0 -w output.pcap -f 'tcp port 22'
```

### Capture Filters vs Display Filters

#### Capture Filter (Before Processing)
```
Reduces data captured initially
More efficient, less processing
Syntax: tcpdump format
Example: tcp port 22 and host 192.168.1.1
```

#### Display Filter (After Capture)
```
Filters already-captured data
Can be changed without re-capturing
Syntax: Wireshark format
Example: tcp.port == 22 and ip.addr == 192.168.1.1
```

## Display Filter Syntax

### Protocol Filters

#### Network Layer
```
ip                      # All IPv4 packets
ipv6                    # All IPv6 packets
arp                     # ARP packets
icmp                    # ICMP packets
igmp                    # IGMP packets
```

#### Transport Layer
```
tcp                     # All TCP packets
udp                     # All UDP packets
sctp                    # SCTP packets
```

#### Application Layer
```
http                    # HTTP packets
https                   # HTTPS packets
dns                     # DNS packets
ssh                     # SSH packets
ftp                     # FTP packets
smtp                    # SMTP packets
pop                     # POP packets
imap                    # IMAP packets
dhcp                    # DHCP packets
```

### Address Filters

#### IP Addresses
```
ip.src == 192.168.1.1               # Source IP
ip.dst == 192.168.1.1               # Destination IP
ip.addr == 192.168.1.1              # Either direction
ip.src_host == server.example.com   # Hostname resolution
ip.dst_host == server.example.com
```

#### MAC Addresses
```
eth.src == 00:11:22:33:44:55
eth.dst == 00:11:22:33:44:55
eth.addr == 00:11:22:33:44:55
```

#### Port Filters
```
tcp.port == 22              # Either source or dest port
tcp.srcport == 22           # Source port
tcp.dstport == 22           # Destination port
tcp.port >= 1024            # Range
tcp.port in {22,80,443}     # Multiple ports
```

### Comparison Operators

#### Text Comparisons
```
==                      # Equal
!=                      # Not equal
contains                # String contains
matches (regex support) # Regular expression
```

#### Numeric Comparisons
```
<, <=, >, >=, ==, !=
```

#### Logical Operators
```
and                     # Both conditions true
or                      # Either condition true
not                     # Negate condition
xor                     # Exclusive or
```

### Common Complex Filters

#### Exclude Traffic
```
not tcp.port == 53              # Exclude DNS
not arp and not stp             # Exclude ARP and STP
not (tcp.port == 22 or tcp.port == 443)
```

#### SYN Packets Only
```
tcp.flags.syn == 1
```

#### Retransmissions
```
tcp.analysis.retransmission
```

#### Duplicate ACKs
```
tcp.analysis.duplicate_ack
```

#### Connection Problems
```
tcp.analysis.flags                  # Any TCP analysis flag
tcp.analysis.lost_segment           # Lost packets
tcp.analysis.window_update          # Window changes
```

#### Large Packets
```
frame.len > 1500        # Jumbo frames
ip.len > 1500           # IP payload
tcp.len > 1000          # TCP payload
```

#### Conversation Filters
```
tcp.stream == 5         # Specific TCP stream
udp.stream == 3         # Specific UDP stream
```

## Protocol Analysis

### HTTP Analysis
```
# All HTTP requests and responses
http

# GET requests only
http.request.method == "GET"

# POST requests
http.request.method == "POST"

# Specific HTTP response codes
http.response.code == 200   # Success
http.response.code == 404   # Not Found
http.response.code == 500   # Server Error
```

### DNS Analysis
```
# All DNS queries
dns

# Successful DNS responses (no error)
dns.flags.response == 1

# DNS queries for specific domain
dns.qry.name == "example.com"

# DNS query types
dns.qry.type == 1       # A record
dns.qry.type == 28      # AAAA record
dns.qry.type == 5       # CNAME record
dns.qry.type == 15      # MX record
```

### TCP Analysis
```
# SYN packets (connection initiation)
tcp.flags.syn == 1 and tcp.flags.ack == 0

# FIN packets (connection termination)
tcp.flags.fin == 1

# RST packets (reset)
tcp.flags.rst == 1

# ACK packets
tcp.flags.ack == 1
```

### SSL/TLS Analysis
```
ssl
ssl.record.content_type == 22       # Handshake
ssl.record.version == 0x0303        # TLS 1.2
tls.handshake.type == 1             # Client Hello
tls.handshake.type == 2             # Server Hello
```

## Packet Inspection

### Following a Stream

#### TCP Stream
```
1. Right-click on packet → Follow → TCP Stream
2. View all packets in single conversation
3. Separate colors for each direction
4. Save stream to file if needed
```

#### UDP Stream
```
1. Right-click on packet → Follow → UDP Stream
2. View associated UDP packets
3. Manually track since UDP is connectionless
```

### Payload Examination

#### ASCII View
```
View → Packet Bytes
Select "ASCII" for readable content
```

#### Hexadecimal View
```
View → Packet Bytes
Select "Hex" for binary content examination
```

#### Decode As
```
Right-click payload → Decode As
Override protocol detection
Useful for non-standard port services
```

## Statistics & Analysis

### Conversation Statistics
```
Statistics → Conversations
Grouped by:
- IP addresses (Endpoints tab)
- TCP/UDP ports (Endpoints tab)
- Protocols (Protocol Hierarchy tab)

Shows:
- Packets
- Bytes
- Duration
- Bits/second
```

### Protocol Distribution
```
Statistics → Protocol Hierarchy
Shows percentage breakdown by protocol
Helps identify unusual traffic
```

### I/O Graph
```
Statistics → I/O Graph
Visual representation of traffic over time
X-axis: Time
Y-axis: Bytes/second
Multiple graphs for comparison
```

### Flow Graph
```
Statistics → Flow Graph
Visual representation of packet flows
Shows timing and sequence
Helpful for understanding communication patterns
```

## Advanced Features

### Expert Info
```
Analyze → Expert Info
Automatically flags:
- Warnings
- Notes
- Chats (informational)
- Errors
- Problems

Color coded by severity
```

### Reassembly
```
Wireshark auto-reassembles:
- TCP segments
- IP fragments
- DNS records

View reassembled data in separate tabs
```

### Decryption
```
Wireshark → Preferences → Protocols
Configure decryption for:
- SSL/TLS (with RSA private key)
- IPSec (with keys)
- WEP/WPA (with passphrase)

Limitations: DHCP key may be required
```

## Filtering for Common Issues

### Network Connectivity Issues
```
# Check if client can reach server
ip.src == 192.168.1.1 and ip.dst == 8.8.8.8

# Look for ICMP unreachable
icmp.type == 3

# Track TCP connection attempts
tcp.flags.syn == 1
```

### DNS Issues
```
# DNS timeouts (no response)
dns and dns.flags.response == 0
Filter[timeout > 5]

# NXDOMAIN responses
dns.flags.rcode == 3

# All DNS traffic from host
(ip.src == 192.168.1.1 or ip.dst == 192.168.1.1) and dns
```

### Performance Issues
```
# Out of order packets
tcp.analysis.out_of_order

# Fast retransmissions
tcp.analysis.fast_retransmission

# Duplicate ACKs
tcp.analysis.duplicate_ack

# Window full
tcp.analysis.zero_window
```

### Security Investigation
```
# Suspicious port scanning
tcp.flags.syn == 1 and tcp.flags.ack == 0

# Multiple SYN packets to same host
tcp.flags.syn == 1

# Possible port sweep
Conversa
tions → endpoints
Look for single source to many destinations
```

## Creating Custom Filters

### Save Filters
```
1. Analyze → Display Filters
2. Click "+" to add new filter
3. Name: "My Custom Filter"
4. Filter string: "tcp.port == 22 and ip.src == 192.168.1.1"
5. Apply and save
```

### Filter Combinations
```
Basic AND:
tcp and port 443

Multiple conditions:
tcp and (port 443 or port 80)

Negation:
not (tcp.port == 53)

Complex:
(ip.src == 192.168.1.1) and (tcp.dstport == 22 or tcp.dstport == 3389)
```

## Exporting Data

### Save Capture File
```
File → Export Specified Packets
- As pcap (for reloading in Wireshark)
- As pcapng (newer format, more metadata)
- As CSV (spreadsheet compatible)
- As JSON (data interchange)
```

### Extract Files
```
File → Export Objects
- HTTP
- SMB
- FTP
- DICOM

Extract transmitted files directly from capture
```

### Print Packets
```
File → Print
Select packet range
Choose format (summary, detail, bytes)
```

## Performance & Large Captures

### Handling Large Files
```
File → Merge files (combine multiple captures)
Editcap (command-line tool) to:
- Extract time ranges
- De-duplicate packets
- Change file format
- Reduce file size
```

### Filtering During Capture
```
Start with tight capture filter
Reduces disk I/O
Speeds processing
Preserves only needed packets
```

### Coloring Rules
```
View → Coloring Rules
Highlight:
- TCP errors in red
- Retransmissions in orange
- Specific hosts in different colors
- Suspicious patterns in bold
```

## Implementation Checklist

- [ ] Install Wireshark and tshark
- [ ] Learn capture filter syntax
- [ ] Learn display filter syntax
- [ ] Practice with sample captures
- [ ] Create filter templates
- [ ] Understand TCP stream analysis
- [ ] Practice protocol dissection
- [ ] Learn to identify common issues
- [ ] Set up coloring rules
- [ ] Create documented troubleshooting procedures
- [ ] Plan capture storage
- [ ] Document privacy requirements

---

**Reference Type**: Network Analysis Tool
**Primary Use**: Packet-level troubleshooting
**Current Version**: Wireshark 4.x
**Last Updated**: 2025-11-19
