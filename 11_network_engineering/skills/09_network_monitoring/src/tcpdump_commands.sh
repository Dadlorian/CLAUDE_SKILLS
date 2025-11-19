#!/bin/bash
# tcpdump Command Reference

# Basic capture
tcpdump -i eth0                     # Capture on interface
tcpdump -i eth0 -w file.pcap       # Write to file
tcpdump -r file.pcap               # Read from file

# Filtering by host/port
tcpdump -i eth0 host 192.168.1.1   # Specific host
tcpdump -i eth0 src 192.168.1.1    # Source IP
tcpdump -i eth0 dst 192.168.1.1    # Destination IP
tcpdump -i eth0 port 22            # Specific port
tcpdump -i eth0 tcp port 443       # TCP port 443

# Advanced filters
tcpdump -i eth0 'tcp port 22 and host 192.168.1.1'
tcpdump -i eth0 'not (arp or broadcast)'
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'  # SYN packets

# Output options
tcpdump -i eth0 -A                 # ASCII output
tcpdump -i eth0 -XX                # Hex and ASCII
tcpdump -i eth0 -v                 # Verbose
tcpdump -i eth0 -vvv               # Very verbose

# Rotation
tcpdump -i eth0 -w file.pcap -C 100 -W 10  # Rotate every 100MB (max 10 files)
tcpdump -i eth0 -G 3600 -w 'capture_%s.pcap'  # New file every hour

# Analysis
tcpdump -r file.pcap | wc -l                   # Packet count
tcpdump -r file.pcap -nn | awk '{print $1}' | sort | uniq -c  # Top sources
