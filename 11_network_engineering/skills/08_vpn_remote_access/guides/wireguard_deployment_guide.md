# WireGuard Deployment Guide

## Overview
Deploy WireGuard VPN for high-performance site-to-site and peer-to-peer connectivity with minimal complexity.

## Phase 1: Planning

### Architecture Design

```
Topology: Hub-and-Spoke with WireGuard
  HQ Server (10.0.0.1): Private key A
  Branch 1 (192.168.1.0/24): Private key B
  Branch 2 (192.168.2.0/24): Private key C
  Branch 3 (192.168.3.0/24): Private key D

Interface: wg0
Subnet: 10.255.0.0/24
UDP Port: 51820
```

### Capacity Planning

```
Server Requirements:
  - CPU: 2 cores minimum (scales linearly)
  - RAM: 512 MB minimum
  - Network: 1 Gbps + connection
  - Storage: 10 GB
  - OS: Linux 5.6+, FreeBSD 12.1+, or Windows

Client Requirements:
  - Any device with WireGuard client
  - Bandwidth: > 1 Mbps
  - Latency: < 100 ms to server
```

## Phase 2: Server Setup (Linux)

### Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install wireguard wireguard-tools

# CentOS/RHEL
sudo yum install wireguard-tools

# Verify installation
wg --version
  WireGuard version 1.0.20210124

# Check kernel module
modprobe wireguard
lsmod | grep wireguard
```

### Key Generation

```bash
# Generate server private key
wg genkey | tee server_private.key | wg pubkey > server_public.key

# Generate client keys (repeat for each peer)
wg genkey | tee client1_private.key | wg pubkey > client1_public.key
wg genkey | tee client2_private.key | wg pubkey > client2_public.key
wg genkey | tee client3_private.key | wg pubkey > client3_public.key

# Generate pre-shared keys (optional, adds extra security)
wg genpsk > preshared_key1.key
wg genpsk > preshared_key2.key
wg genpsk > preshared_key3.key

# Secure the keys
chmod 600 *.key
```

### Interface Configuration

```bash
# Create configuration file
sudo nano /etc/wireguard/wg0.conf

[Interface]
Address = 10.255.0.1/24
ListenPort = 51820
PrivateKey = <server_private_key_content>
SaveConfig = false

# Peer 1 (Branch 1)
[Peer]
PublicKey = <client1_public_key>
AllowedIPs = 10.255.0.2/32, 192.168.1.0/24
PersistentKeepalive = 25  # Mobile client or NAT

# Peer 2 (Branch 2)
[Peer]
PublicKey = <client2_public_key>
AllowedIPs = 10.255.0.3/32, 192.168.2.0/24
PersistentKeepalive = 25

# Peer 3 (Branch 3)
[Peer]
PublicKey = <client3_public_key>
AllowedIPs = 10.255.0.4/32, 192.168.3.0/24
PersistentKeepalive = 25
```

### Firewall Configuration

```bash
# Allow WireGuard traffic
sudo ufw allow 51820/udp

# Alternative (iptables)
sudo iptables -A INPUT -p udp --dport 51820 -j ACCEPT
sudo iptables -A INPUT -i wg0 -j ACCEPT
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -A FORWARD -o wg0 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Enable IP forwarding
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Bring Up Interface

```bash
# Enable interface
sudo wg-quick up wg0

# Verify status
sudo wg show

# Output:
# interface: wg0
#   public key: <server_public_key>
#   private key: (hidden)
#   listening port: 51820
#
# peer: <client1_public_key>
#   endpoint: 203.0.113.100:51820
#   allowed ips: 10.255.0.2/32, 192.168.1.0/24
#   latest handshake: 30 seconds ago
#   transfer: 1.23 MiB received, 4.56 MiB sent

# Enable at boot
sudo systemctl enable wg-quick@wg0
```

## Phase 3: Client Configuration

### Linux Client

```bash
# Create client config file
mkdir -p ~/wireguard
sudo nano /etc/wireguard/wg-client.conf

[Interface]
Address = 10.255.0.2/32
PrivateKey = <client_private_key>
DNS = 10.0.0.1, 8.8.8.8

[Peer]
PublicKey = <server_public_key>
Endpoint = 203.0.113.1:51820  # Server public IP
AllowedIPs = 10.255.0.0/24, 10.0.0.0/8  # What goes through tunnel
PersistentKeepalive = 25

# Bring up interface
sudo wg-quick up wg-client

# Test connectivity
ping 10.0.0.1
```

### Windows Client

```
Installation:
  1. Download from https://www.wireguard.com/install/
  2. Run installer
  3. Accept admin privileges
  4. Complete installation

Configuration:
  1. Create config file (wg-client.conf)
  2. Right-click > Open with > Notepad
  3. Add interface and peer info
  4. Save to %AppData%\WireGuard\Configs\
  5. Open WireGuard application
  6. Activate tunnel

Registry Optimization (for better performance):
  netsh int tcp set global autotuninglevel=normal
```

### macOS Client

```bash
# Installation via Homebrew
brew install wireguard-tools

# Or download from App Store
# https://apps.apple.com/us/app/wireguard/id1451685025

# Create configuration
cat > /etc/wireguard/wg-mac.conf << EOF
[Interface]
Address = 10.255.0.3/32
PrivateKey = <client_private_key>
DNS = 10.0.0.1, 8.8.8.8

[Peer]
PublicKey = <server_public_key>
Endpoint = 203.0.113.1:51820
AllowedIPs = 10.255.0.0/24, 10.0.0.0/8
PersistentKeepalive = 25
EOF

# Enable at login
# Use macOS app: Add tunnel > Import from file
```

### Mobile (iOS/Android)

```
iOS:
  1. Download WireGuard from App Store
  2. Create new empty tunnel
  3. Scan QR code (or import config)
  4. Activate tunnel
  5. Authorize VPN permissions

Android:
  1. Download WireGuard from Google Play
  2. Create new tunnel
  3. Import from config file
  4. Activate tunnel
  5. Authorize VPN permissions

Generate QR Code (for easy client setup):
  qrencode -t ansiutf8 < client.conf
```

## Phase 4: Advanced Configuration

### Site-to-Site VPN (AllowedIPs for Networks)

```
Server Config (updated):
[Peer]
PublicKey = <branch1_public_key>
AllowedIPs = 192.168.1.0/24   # Entire network, not just one peer
Endpoint = 203.0.113.10:51820

Client Config (Branch 1):
[Interface]
Address = 10.255.0.2/32
PrivateKey = <branch1_private_key>

[Peer]
PublicKey = <server_public_key>
Endpoint = <server_public_ip>:51820
AllowedIPs = 10.255.0.0/24, 10.0.0.0/8    # Access hub and other networks
```

### Pre-Shared Keys (Additional Security)

```
Generate PSK:
wg genpsk > preshared.key

Server Config:
[Peer]
PublicKey = <client_public_key>
AllowedIPs = 10.255.0.2/32, 192.168.1.0/24
PresharedKey = <content_of_preshared.key>

Client Config:
[Peer]
PublicKey = <server_public_key>
Endpoint = <server_ip>:51820
AllowedIPs = 10.255.0.0/24, 10.0.0.0/8
PresharedKey = <same_preshared_key>
```

### Routing with Dynamic IP (Roaming Clients)

```
Server Config:
[Peer]
PublicKey = <mobile_client_public_key>
AllowedIPs = 10.255.0.5/32      # Only this client IP
# Note: No Endpoint (client initiates, endpoint learned)

Client Config (Mobile):
[Interface]
Address = 10.255.0.5/32
PrivateKey = <mobile_private_key>

[Peer]
PublicKey = <server_public_key>
Endpoint = 203.0.113.1:51820
AllowedIPs = 10.255.0.0/24, 10.0.0.0/8
PersistentKeepalive = 25        # Maintains connection through NAT
```

## Phase 5: Testing and Verification

### Connectivity Tests

```bash
# From server
sudo wg show

# From client
ping 10.255.0.1        # Server interface
ping 10.0.0.1          # HQ resource

# Check tunnel status
sudo wg show wg0
curl https://10.0.1.1  # Test corporate web service
```

### Performance Benchmarking

```bash
# Throughput test (server -> client)
# Server: iperf3 -s
# Client: iperf3 -c 10.255.0.1 -t 60

# Expected: 1000+ Mbps on modern hardware

# Latency
ping -c 10 10.255.0.1
# Expected: 1-5 ms average

# Packet loss
ping -c 100 10.255.0.1 | grep received
# Expected: 0% packet loss
```

### Handshake Monitoring

```bash
# Watch for recent handshakes
watch sudo wg show

# Should show "latest handshake" for active peers
# If empty or very old: Connection problem
```

## Phase 6: Advanced Features

### Load Balancing with Multiple Servers

```
Client Config (Load Balancing):
# Try first endpoint, fallback to second
[Peer]
PublicKey = <hub1_public_key>
Endpoint = hub1.example.com:51820
AllowedIPs = 10.255.0.0/24

# Second server with different subnet
[Peer]
PublicKey = <hub2_public_key>
Endpoint = hub2.example.com:51820
AllowedIPs = 10.255.100.0/24
```

### Split Tunneling

```
# Only route specific traffic through VPN
[Interface]
# ... existing config ...

[Peer]
PublicKey = <server_public_key>
Endpoint = 203.0.113.1:51820
AllowedIPs = 10.0.0.0/8, 192.168.0.0/16    # Only corporate networks
# Everything else uses local gateway
```

### Dynamic Configuration Updates

```bash
# Add new peer without stopping tunnel
sudo wg set wg0 peer <new_client_pubkey> allowed-ips 10.255.0.10/32 endpoint 203.0.113.20:51820

# Remove peer
sudo wg set wg0 peer <client_pubkey> remove

# Modify allowed IPs
sudo wg set wg0 peer <client_pubkey> allowed-ips 10.255.0.2/32,192.168.1.0/24,192.168.2.0/24

# Save configuration
wg-quick save wg0
```

## Phase 7: Monitoring and Maintenance

### Real-time Statistics

```bash
# View all stats
sudo wg show all

# Per-peer statistics
sudo wg show wg0 peers

# Extract transfer data
sudo wg show wg0 transfer | awk '{print $1, $2/$1024/$1024 "MB", $3/$1024/$1024 "MB"}'
```

### Health Checks

```bash
#!/bin/bash
# Check all peers reachable
for peer in $(sudo wg show wg0 peers); do
  endpoint=$(sudo wg show wg0 peer $peer endpoint)
  ip=$(echo $endpoint | cut -d: -f1)
  port=$(echo $endpoint | cut -d: -f2)
  timeout 1 bash -c "echo >/dev/tcp/$ip/$port" && echo "Peer $peer: OK" || echo "Peer $peer: FAIL"
done
```

### Log Monitoring

```bash
# Check system logs for WireGuard events
sudo journalctl -u wg-quick@wg0

# Monitor handshakes
sudo watch -n 1 'sudo wg show | grep "latest handshake"'

# Monitor traffic
watch -n 1 'sudo wg show wg0 transfer'
```

## Phase 8: Security Hardening

### Rate Limiting

```bash
# Limit connection attempts
sudo iptables -A INPUT -p udp --dport 51820 -m limit --limit 10/min -j ACCEPT
sudo iptables -A INPUT -p udp --dport 51820 -j DROP
```

### UFW Configuration

```bash
# Allow specific IPs
sudo ufw allow from 203.0.113.100 to any port 51820
sudo ufw allow from 203.0.113.101 to any port 51820

# Deny all others
sudo ufw deny 51820/udp
```

### Key Rotation

```bash
# Rotate client key (without downtime)
1. Generate new key pair
2. Add as new peer on server
3. Update client config
4. Test connectivity
5. Remove old peer
6. Repeat for all clients
```

## Troubleshooting

### No Connection

```bash
# Check firewall
sudo ufw status
sudo iptables -L | grep 51820

# Verify interface up
ip link show wg0
# Should show: mtu 1420

# Check configuration
sudo wg show
# Peers should be listed

# Test from outside
nc -u -z -v <server_ip> 51820
```

### High Latency

```bash
# Check MTU
ping -M do -s 1400 <remote_ip>
# If fails, reduce MTU

# Set lower MTU
ip link set mtu 1380 dev wg0

# Check buffer sizes
netstat -an | grep -i time_wait | wc -l
```

### Drops/Reconnections

```bash
# Increase keepalive
sudo wg set wg0 peer <key> persistent-keepalive 45

# Check system load
top
# High CPU = encryption overhead

# Verify NAT timeout
nmap -sU -p 51820 <server_ip>
```

## Best Practices

- [ ] Regularly rotate client keys (annually)
- [ ] Use PSK for additional security
- [ ] Monitor handshake timeouts
- [ ] Set appropriate MTU (1420 typical)
- [ ] Enable keepalive for mobile clients
- [ ] Log all configuration changes
- [ ] Document all peer configurations
- [ ] Backup private keys securely
- [ ] Use strong authentication on server
- [ ] Monitor bandwidth per client
- [ ] Implement rate limiting
- [ ] Keep WireGuard updated
