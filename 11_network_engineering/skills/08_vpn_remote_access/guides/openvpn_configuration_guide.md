# OpenVPN Configuration Guide

## Overview
Deploy OpenVPN server for remote access and site-to-site connectivity with TLS-based encryption.

## Phase 1: Server Setup (Linux)

### Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install openvpn easy-rsa

# CentOS/RHEL
sudo yum install openvpn easy-rsa

# Verify installation
openvpn --version
```

### PKI Setup (Certificate Authority)

```bash
# Initialize PKI directory
mkdir -p ~/openvpn-ca
cd ~/openvpn-ca
easyrsa init-pki

# Create CA
easyrsa build-ca nopass

# Output: ca.crt created in pki/

# Create server certificate
easyrsa gen-req server nopass
easyrsa sign-req server server
easyrsa gen-dh

# Output: server.crt, server.key, dh.pem

# Create test client certificate
easyrsa gen-req client1 nopass
easyrsa sign-req client client1

# Output: client1.crt, client1.key
```

### OpenVPN Server Configuration

```bash
# Create server config
sudo nano /etc/openvpn/server.conf

# Network and Protocol
port 1194
proto udp
dev tun
topology subnet

# Certificates
ca ca.crt
cert server.crt
key server.key
dh dh.pem
tls-crypt ta.key direction 0

# IP Pool for Clients
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt

# DNS
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 1.1.1.1"

# Routes (what networks clients can access)
push "route 10.0.0.0 255.0.0.0"
push "route 192.168.0.0 255.255.0.0"

# Enable client communication
client-to-client

# Keepalive
keepalive 10 120

# Compression
compress lz4-v2
push "compress lz4-v2"

# Encryption
cipher AES-256-GCM
auth SHA256

# Logging
status openvpn-status.log
log openvpn.log
log-append openvpn.log
verb 3

# Security
user nobody
group nogroup
persist-key
persist-tun

# Increase performance
sndbuf 393216
rcvbuf 393216

# Output directory
cd /etc/openvpn/
```

### TLS-Crypt Key Generation

```bash
# Generate additional TLS encryption key
cd ~/openvpn-ca
openvpn --genkey --secret ta.key

# Copy to OpenVPN directory
sudo cp ta.key /etc/openvpn/

# This adds extra layer of security
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 1194/udp
sudo ufw allow in on tun0

# iptables
sudo iptables -A INPUT -p udp --dport 1194 -j ACCEPT
sudo iptables -A FORWARD -i tun0 -j ACCEPT
sudo iptables -A FORWARD -o tun0 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Enable IP forwarding
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Start OpenVPN Server

```bash
# Start service
sudo systemctl start openvpn@server
sudo systemctl status openvpn@server

# Enable at boot
sudo systemctl enable openvpn@server

# Verify listening
sudo netstat -tulpn | grep 1194
# Output: udp 0 0 0.0.0.0:1194 0.0.0.0:* 1194/openvpn
```

## Phase 2: Client Configuration

### Generate Client Certificates

```bash
# For each client, generate certificate
cd ~/openvpn-ca
easyrsa gen-req client2 nopass
easyrsa sign-req client client2

# Repeat for additional clients
easyrsa gen-req client3 nopass
easyrsa sign-req client client3
```

### Create Client Configuration

```bash
# Create directory for configs
mkdir -p ~/openvpn-configs

# Create config file
cat > ~/openvpn-configs/client.conf << 'EOF'
client
remote vpn.example.com 1194 udp
remote vpn2.example.com 1194 udp        # Fallback server
float
nobind

dev tun
topology subnet
proto udp

# Certificates
ca ca.crt
cert client1.crt
key client1.key
tls-crypt ta.key 1

# Encryption
cipher AES-256-GCM
auth SHA256

# DNS
dhcp-option DNS 8.8.8.8
dhcp-option DNS 1.1.1.1

# Keepalive
keepalive 10 120

# Compression
compress lz4-v2

# Security
persist-key
persist-tun
comp-lzo no
mute-replay-warnings

# Split Tunneling (route only corporate traffic through VPN)
route 10.0.0.0 255.0.0.0
route 192.168.0.0 255.255.0.0

# Full tunnel (all traffic through VPN)
# redirect-gateway def1

# Logging
verb 3
mute 20
log openvpn.log
EOF
```

### Client File Preparation

```bash
# Collect all needed files into one directory
mkdir -p ~/openvpn-client
cd ~/openvpn-configs

cp client.conf ~/openvpn-client/
cp ~/openvpn-ca/pki/ca.crt ~/openvpn-client/
cp ~/openvpn-ca/pki/issued/client1.crt ~/openvpn-client/
cp ~/openvpn-ca/pki/private/client1.key ~/openvpn-client/
cp ~/openvpn-ca/ta.key ~/openvpn-client/

# Set permissions
chmod 600 ~/openvpn-client/*
```

### Bundled Configuration (Single File)

```bash
# Create .ovpn file with everything embedded
cat > ~/openvpn-client/client1.ovpn << 'EOF'
client
remote vpn.example.com 1194 udp
float
nobind
dev tun
proto udp
topology subnet

cipher AES-256-GCM
auth SHA256
compress lz4-v2

persist-key
persist-tun
keepalive 10 120
verb 3

route 10.0.0.0 255.0.0.0
route 192.168.0.0 255.255.0.0

# CA certificate
<ca>
-----BEGIN CERTIFICATE-----
[CA cert content]
-----END CERTIFICATE-----
</ca>

# Client certificate
<cert>
-----BEGIN CERTIFICATE-----
[Client cert content]
-----END CERTIFICATE-----
</cert>

# Client key
<key>
-----BEGIN PRIVATE KEY-----
[Client key content]
-----END PRIVATE KEY-----
</key>

# TLS crypt
<tls-crypt>
-----BEGIN OpenVPN Static key V1-----
[TLS crypt key content]
-----END OpenVPN Static key V1-----
</tls-crypt>
EOF

# Distribute this single file to clients
```

### Linux Client

```bash
# Install OpenVPN
sudo apt-get install openvpn

# Copy client config
sudo cp client.conf /etc/openvpn/client/

# Copy certificates
sudo cp ca.crt /etc/openvpn/client/
sudo cp client1.crt /etc/openvpn/client/
sudo cp client1.key /etc/openvpn/client/
sudo cp ta.key /etc/openvpn/client/

# Set permissions
sudo chmod 600 /etc/openvpn/client/*

# Start client
sudo systemctl start openvpn-client@client
sudo systemctl status openvpn-client@client

# Enable at boot
sudo systemctl enable openvpn-client@client

# Check interface
ip addr show tun0
```

### Windows Client

```
Installation:
  1. Download from https://openvpn.net/community-downloads/
  2. Run installer
  3. Choose components (include OpenSSL)
  4. Complete setup

Configuration:
  1. Create folder: C:\Users\[username]\OpenVPN\config\
  2. Copy client.ovpn file
  3. Copy ca.crt, client1.crt, client1.key, ta.key
  4. Right-click OpenVPN GUI > Run as administrator
  5. Right-click system tray icon > Connect
```

### macOS Client

```bash
# Install via Homebrew
brew install openvpn

# Or download: https://openvpn.net/community-downloads/

# Copy config
mkdir -p ~/OpenVPN/
cp client.ovpn ~/OpenVPN/

# Connect via command line
sudo openvpn ~/OpenVPN/client.ovpn

# Or use tunnelblick (GUI)
brew install tunnelblick
# Then import .ovpn file
```

## Phase 3: Advanced Configuration

### User Authentication (RADIUS)

```bash
# Install RADIUS plugin
sudo apt-get install openvpn-auth-radius

# Modify server config
cat >> /etc/openvpn/server.conf << 'EOF'
# Use RADIUS authentication
auth-user-pass-verify /usr/libexec/openvpn-radiusplugin.pl via file
plugin /usr/lib/openvpn/openvpn-plugin-auth-pam.so openvpn

# RADIUS configuration
radius_server auth 10.0.0.50 secret 49
radius_connect_timeout 5
EOF
```

### Multi-Factor Authentication

```bash
# Require username/password + certificate
modify server.conf:
auth-user-pass-optional    # Username/password optional
verify-client-cert require  # Certificate required
```

### Site-to-Site Configuration

```bash
# Server side
cat /etc/openvpn/server.conf
# ... existing config ...
client-to-client      # Allow peer-to-peer

# Client side (for gateway router)
cat > /etc/openvpn/office-site-to-site.conf << 'EOF'
client
remote vpn.hq.example.com 1194
proto udp
dev tun
topology subnet

# Static IP for this gateway
ifconfig 10.8.0.2 255.255.255.0

# Route entire network
route 192.168.100.0 255.255.255.0

# Certificates
ca ca.crt
cert gateway1.crt
key gateway1.key
tls-crypt ta.key 1

cipher AES-256-GCM
auth SHA256
compress lz4-v2
keepalive 10 120
persist-key
persist-tun
verb 3
EOF
```

## Phase 4: Performance Tuning

### Optimize for Throughput

```bash
# Server config optimizations
sndbuf 393216          # 384 KB send buffer
rcvbuf 393216          # 384 KB receive buffer
thread-pool-size 8     # Multiple threads

# Compression trade-off (may reduce throughput)
compress lz4-v2
# Or disable compression
compress none

# Disable compression on client too:
client.conf:
compress none
```

### Encryption Performance

```bash
# Fastest (still secure)
cipher AES-128-GCM
auth SHA256

# Standard
cipher AES-256-GCM
auth SHA256

# Maximum security (slower)
cipher AES-256-GCM
auth SHA512

# Check system support for hardware acceleration
cat /proc/cpuinfo | grep aes
# Output: aes = Hardware AES support available
```

## Phase 5: Testing and Verification

### Server Status

```bash
# Check active connections
sudo cat /etc/openvpn/openvpn-status.log

Output:
OpenVPN CLIENT LIST
Updated,Fri Dec 10 10:00:00 2021
Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
client1,203.0.113.100:55123,512000,1024000,Fri Dec 10 09:55:30 2021
client2,203.0.113.101:55124,256000,512000,Fri Dec 10 09:58:15 2021

ROUTING TABLE
Virtual Address,Common Name,Real Address,Last Ref
10.8.0.6,client1,203.0.113.100:55123,Fri Dec 10 10:00:00 2021
10.8.0.7,client2,203.0.113.101:55124,Fri Dec 10 10:00:00 2021
```

### Client Connection Test

```bash
# Linux client
sudo openvpn ~/openvpn-client/client.conf &

# Wait for connection
sleep 5

# Test connectivity
ping -c 5 10.0.1.1        # Server network
ping -c 5 192.168.1.1     # Another subnet

# Check routing
ip route | grep 10.0
ip route | grep 192.168

# Verify tunnel
ip link show tun0
ip addr show tun0
```

### Bandwidth Test

```bash
# Server (listen)
iperf3 -s

# Client (test)
iperf3 -c 10.8.0.1 -t 60 -b 100M

# Expected: 50-100 Mbps depending on hardware
```

## Phase 6: Maintenance

### Key Rotation

```bash
# Generate new CA certificate (yearly)
cd ~/openvpn-ca
easyrsa gen-req new-server nopass
easyrsa sign-req server new-server
easyrsa gen-dh

# Gradually deploy new certificates
# 1. Deploy to test clients first
# 2. Monitor for issues
# 3. Roll out to production
```

### Client Revocation

```bash
# Revoke client certificate
cd ~/openvpn-ca
easyrsa revoke client1

# Generate CRL (Certificate Revocation List)
easyrsa gen-crl

# Update server config
cat >> /etc/openvpn/server.conf << 'EOF'
crl-verify crl.pem
EOF

# Copy CRL to server
sudo cp pki/crl.pem /etc/openvpn/

# Restart server
sudo systemctl restart openvpn@server
```

### Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/openvpn

/var/log/openvpn/*.log {
  daily
  rotate 7
  compress
  missingok
  notifempty
  create 0640 nobody nobody
  sharedscripts
  postrotate
    systemctl reload openvpn@server > /dev/null 2>&1 || true
  endscript
}
```

## Troubleshooting

### Cannot Connect

```bash
# Check server status
sudo systemctl status openvpn@server

# Verify port open
sudo netstat -tulpn | grep 1194

# Check firewall
sudo ufw status
sudo iptables -L | grep 1194

# Client debug
openvpn --config client.conf --verb 9
# Check for specific errors
```

### Low Throughput

```bash
# Disable compression
cipher AES-256-GCM
compress none     # Remove this line

# Increase buffers
sndbuf 524288
rcvbuf 524288

# Check encryption overhead
# Reduce cipher strength if not needed
cipher AES-128-GCM
```

### High Latency

```bash
# Reduce processing overhead
proto udp         # UDP faster than TCP
compress none     # Disable compression
mssfix 1400       # Prevent fragmentation

# Check network path
mtr vpn.example.com
```

## Best Practices Checklist

- [ ] Use AES-256-GCM minimum
- [ ] Enable TLS-crypt
- [ ] Rotate keys annually
- [ ] Monitor active connections
- [ ] Log authentication attempts
- [ ] Implement rate limiting
- [ ] Use strong firewall rules
- [ ] Keep OpenVPN updated
- [ ] Test failover scenario
- [ ] Backup CA certificate
- [ ] Document all procedures
- [ ] Enable compression only if needed
