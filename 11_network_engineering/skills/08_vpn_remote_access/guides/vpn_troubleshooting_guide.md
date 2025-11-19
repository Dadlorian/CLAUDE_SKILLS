# VPN Troubleshooting Guide

## Troubleshooting Framework

### 1. Identify Problem Category

```
Categories:
  A. Connection Issues (tunnel not established)
  B. Authentication Failures (login problems)
  C. Traffic Flow Problems (connected but no data)
  D. Performance Issues (slow, packet loss)
  E. Intermittent Issues (flapping, dropouts)
```

### 2. Gather Information

```
Essential Details:
  - When did problem start?
  - Affects all users or specific user?
  - Which protocol (IPsec, SSL, WireGuard, OpenVPN)?
  - Which platform (Windows, Mac, Linux, mobile)?
  - Recent changes to network or VPN?
  - Error messages (exact text)?
  - Network conditions (latency, packet loss)?
```

## Category A: Connection Issues

### Symptom: Cannot Connect to VPN Server

**Step 1: Verify Network Connectivity**

```bash
# Test basic connectivity
ping <vpn_server_ip>
# Expected: Response received

# If ping fails:
  - Check ISP connectivity
  - Verify DNS resolution
  - Test from different network
  - Check firewall rules

# Test port connectivity
nmap -p <vpn_port> <vpn_server_ip>
# Expected: port open

# Alternative (Windows)
telnet <vpn_server_ip> <vpn_port>
# Expected: Connected
```

**Step 2: Check VPN Server Status**

```
For Cisco ASA:
  show crypto session brief
  show vpn-sessiondb summary
  # Output: Should show listening status

For OpenVPN:
  sudo systemctl status openvpn@server
  # Should be: active (running)

For WireGuard:
  sudo wg show
  # Should show: interface wg0 [listening]

For Palo Alto:
  Monitor > System Resources > SSL/TLS VPN
  # Should show: Service running
```

**Step 3: Verify VPN Configuration**

```cisco
! Cisco ASA example
show run | include tunnel-group
# Should show tunnel group defined

show run | include crypto map
# Should show crypto map applied

show crypto ikev2 policy 1
# Should show policy configured
```

**Step 4: Check Firewall Rules**

```bash
# Allow VPN traffic
sudo ufw allow 1194/udp
sudo ufw allow 443/tcp
sudo ufw allow 500/udp
sudo ufw allow 4500/udp
sudo ufw allow 51820/udp

# Verify rules
sudo ufw status | grep VPN
```

**Step 5: Enable Debug Logging**

```
IPsec (Cisco):
  debug crypto ikev2 protocol
  debug crypto ipsec

SSL VPN (Cisco):
  debug webvpn protocol
  debug aaa authentication

OpenVPN:
  sudo openvpn --config server.conf --verb 9
  # Look for specific errors in output
```

### Symptom: IKE Phase 1 Failure (IPsec)

**Diagnosis Steps**

```
Error: IKE negotiation failed
Cause: Authentication or proposal mismatch

Check 1: Firewall
  - Port 500 (IKE) open?
  - Port 4500 (NAT-T) open?
  - IPS/IDS blocking?

Check 2: Pre-shared Key
  - PSK matches on both sides exactly?
  - Check for special characters
  - Verify copy/paste accuracy

Check 3: Encryption Proposal
  - IKE encryption matches?
  - DH group matches?
  - Integrity algorithm matches?

Check 4: Peer Address
  - Is peer IP reachable?
  - Correct IP in configuration?
  - NAT affecting IP?
```

**Resolution**

```
1. Verify PSK:
   Both sides must have identical PSK
   crypto ikev2 keyring MY-KEYRING
   peer <ip>
     pre-shared-key MyPassword123!

2. Verify Proposals:
   crypto ikev2 proposal MY-PROPOSAL
   encryption aes-256
   integrity sha256
   group 14

3. Test Connectivity:
   ping <peer_ip>

4. Monitor Negotiation:
   debug crypto ikev2 protocol
   # Look for: IKE_SA_INIT, no errors

5. Restart IKE:
   clear crypto ikev2 sa
```

## Category B: Authentication Failures

### Symptom: Invalid Username or Password

**For LDAP Authentication**

```
Check LDAP Server:
  1. Is LDAP server reachable?
     ping <ldap_server>
  2. Is LDAP service running?
     # Check status on LDAP server
  3. Test LDAP connectivity:
     ldapsearch -x -H ldap://<server> -b "dc=example,dc=com"
  4. Verify bind user exists and has permissions
  5. Check for account lockout

Check VPN Configuration:
  tunnel-group RemoteVPN general-attributes
    authentication-server-group LDAP
  # Verify LDAP server configured

Test Manually:
  test aaa-server authentication LDAP user testuser password testpass
  # Should show: successful
```

**For Certificate Authentication**

```
Check Certificate:
  1. Certificate valid (not expired)?
     openssl x509 -in client.crt -noout -dates
  2. Signed by correct CA?
     openssl verify -CAfile ca.crt client.crt
  3. Server trusts CA?
     Verify CA cert on server
  4. Client has private key?
     Check client.key file exists
  5. Key/cert match?
     openssl x509 -noout -pubkey -in client.crt > pubkey1.pem
     openssl pkey -pubout -in client.key > pubkey2.pem
     diff pubkey1.pem pubkey2.pem  # Should match
```

**For MFA Failures**

```
Check MFA Provider:
  1. Is provider reachable?
     Ping/telnet to provider
  2. API key/secret correct?
     Test with provider API
  3. User enrolled in MFA?
     Check user account on provider
  4. Device/token synchronized?
     Resync token if needed
  5. Time synchronized?
     NTP on all servers correct
```

### Symptom: Certificate Rejected

**Diagnosis**

```
Check CA Certificate:
  1. Server's CA cert matches client's CA cert?
     diff server_ca.crt client_ca.crt
  2. Client cert in CA revocation list (CRL)?
     # Check if revoked

Check Certificate Chain:
  1. Certificate validity dates:
     openssl x509 -in cert.crt -noout -dates
  2. Subject/issuer correct:
     openssl x509 -in cert.crt -noout -subject -issuer
  3. Key usage appropriate:
     openssl x509 -in cert.crt -noout -text | grep -A 5 "Key Usage"

Verify Certificate Type:
  - Server cert for server side
  - Client cert for client side
  - Not using same cert for both
```

## Category C: Traffic Flow Issues

### Symptom: Connected but Cannot Access Resources

**Diagnosis Steps**

```
Step 1: Verify Tunnel Status
  IPsec:
    show crypto ipsec sa
    # Should show: #pkts encaps increasing

  OpenVPN:
    netstat -tulpn | grep 1194
    # Should show: ESTABLISHED

  WireGuard:
    sudo wg show
    # Should show: latest handshake recent

Step 2: Check Routing
  show ip route | include <destination>
  # Should have route to destination

Step 3: Check Access Lists
  show access-list | include 192.168
  # Should permit traffic

Step 4: Verify NAT
  show nat | include VPN
  # VPN traffic should be exempted from NAT

Step 5: Test from Client
  ping <internal_resource_ip>
  # Should get response
```

**Common Issues**

```
Issue 1: Wrong Subnet in Tunnel
  OpenVPN AllowedIPs: 10.0.0.0/8
  But server is: 192.168.0.0/16
  Solution: Add route or update AllowedIPs

Issue 2: NAT Breaking VPN
  VPN traffic getting translated
  Solution: Exempt VPN traffic from NAT

Issue 3: Return Traffic Blocked
  Outbound traffic allowed, inbound blocked
  Solution: Check reverse firewall rules

Issue 4: MTU Causing Fragmentation
  Large packets fragmented, reassembly fails
  Solution: Reduce MTU to account for overhead
```

**Resolution**

```
For Missing Routes:
  1. Identify required subnet
  2. Add static route or redistribute
  3. Verify route appears in routing table
  4. Test with ping

For Firewall Blocking:
  1. Check inbound rules on destination
  2. Verify ACL allows source IP
  3. Check for implicit deny
  4. Add explicit allow rule

For NAT Issues:
  1. Identify VPN traffic
  2. Exempt from NAT
  3. Verify configuration
  4. Clear NAT translation table
```

## Category D: Performance Issues

### Symptom: Slow Throughput

**Diagnosis**

```
Baseline Test:
  1. Test without VPN
     iperf3 -c <server> -t 60
     # Record baseline speed

  2. Test with VPN
     iperf3 -c <vpn_resource> -t 60
     # Compare to baseline

  Expected: 80-90% of baseline
  Actual < 50%: Investigation needed
```

**Root Cause Analysis**

```
Check Encryption Overhead:
  - Algorithm used?
  - Hardware acceleration available?
  - CPU utilization during transfer?

Check Compression:
  - Compression enabled?
  - Helping or hurting (test both)?
  - Compression overhead?

Check Network Path:
  - Latency to VPN server?
  - Jitter (consistent latency)?
  - Packet loss percentage?
  - MTU size appropriate?

Check Processor:
  - CPU at 100%?
  - Multiple cores available?
  - Switch to faster cipher?
  - Enable hardware acceleration?
```

**Performance Optimization**

```
1. Increase MTU (if not causing fragmentation)
   ip link set mtu 1500 dev <interface>

2. Disable compression (often faster)
   Remove compress directive

3. Enable hardware acceleration
   Verify AES-NI support: grep aes /proc/cpuinfo

4. Use faster cipher (if acceptable)
   ChaCha20-Poly1305 > AES-256-GCM > AES-128-CBC

5. Tune TCP window
   netsh int tcp set global autotuninglevel=normal (Windows)

6. Add more processing power
   Multi-core CPU, crypto offload card, or additional gateways
```

### Symptom: High Latency

**Measurement**

```bash
# Measure RTT to VPN server
ping -c 10 <vpn_server>
# Normal: 1-20 ms
# High: > 100 ms

# Measure through VPN
ping -c 10 <internal_resource>
# Normal: baseline + 1-5 ms
# High: > baseline + 50 ms

# Trace route
tracert <resource>
# Identify hop with high latency
```

**Causes and Fixes**

```
Cause: Geographic Distance
  Fix: Use geographically closer VPN server
  Verify: Ping different regional servers

Cause: Network Congestion
  Fix: Identify bottleneck
  Monitor: Bandwidth usage during test
  Solution: QoS, load balancing

Cause: Processing Delay
  Fix: Faster encryption
  Check: CPU utilization
  Solution: Reduce cipher strength or add hardware

Cause: Multiple Hops
  Fix: Direct path optimization
  Verify: Fewest hops possible
  Solution: Review routing topology
```

## Category E: Intermittent Issues

### Symptom: VPN Drops/Reconnects

**Diagnosis**

```
Identify Pattern:
  - How often? (seconds, minutes, hours)
  - Time of day? (off-hours, peak hours)
  - Specific users or all?
  - Triggered by activity? (downloads, uploads)

Check Logs:
  # Look for timestamps of drops
  show log | include crypto
  tail -f /var/log/openvpn.log | grep dropped
```

**Common Causes**

```
Cause 1: Idle Timeout
  Solution: Configure keepalive
  IPsec: keepalive 10 120
  OpenVPN: keepalive 10 120

Cause 2: DPD Timeout
  Solution: Increase DPD timeout
  IKEv2: dpd 10 3 on-demand -> dpd 30 5 on-demand

Cause 3: NAT Session Expiration
  Solution: Increase keepalive frequency
  PersistentKeepalive = 10 (WireGuard)

Cause 4: Certificate Renewal
  Solution: Reload certificates before expiry
  Monitor expiration dates

Cause 5: Network Instability
  Solution: Monitor packet loss and jitter
  May indicate network provider issues
```

**Resolution**

```
1. Review logs at time of drop
2. Identify error message
3. Apply appropriate fix
4. Monitor for recurrence
5. Escalate if unresolved
```

### Symptom: Flapping (Rapid Connect/Disconnect)

**Causes**

```
Common Triggers:
  - Duplicate peer discovery (remove duplicates)
  - Route oscillation (clarify routing)
  - Certificate mismatch (verify certs)
  - Clock skew (synchronize NTP)
  - Conflicting configurations (review all configs)
```

**Debugging**

```
# Enable detailed logging
debug crypto ikev2 protocol
debug crypto ipsec

# Monitor in real time
show crypto session brief (repeat every few seconds)

# Look for pattern
- How long between drops?
- What triggers reconnect?
- Error before disconnect?
```

## Advanced Troubleshooting

### Packet Capture and Analysis

```bash
# Capture VPN traffic
sudo tcpdump -i <interface> -w vpn_capture.pcap udp port 500 or udp port 4500

# Analyze with Wireshark
wireshark vpn_capture.pcap

# Filter for IKE
ikev2

# Look for:
- Proposal mismatch (IKE_INVALID_KE_PAYLOAD)
- Authentication failure
- Encryption errors
```

### Protocol Analysis

**IKE Analysis**
```
Normal IKEv2 exchange:
  1. IKE_SA_INIT request
  2. IKE_SA_INIT response
  3. IKE_AUTH request
  4. IKE_AUTH response
  (Tunnel established)

If stuck at step 1:
  - Firewall blocking response
  - Proposal mismatch
  - Server crash/overload

If stuck at step 3:
  - Authentication failure
  - Certificate issue
  - Algorithm mismatch
```

**OpenVPN Analysis**
```
Normal OpenVPN handshake:
  1. TCP/UDP connection
  2. TLS handshake
  3. Auth
  4. Encryption key derivation
  (Tunnel ready)

Issues:
  - Slow handshake: Check TLS session caching
  - Certificate errors: Verify CA and certs
  - Timeout: Check TCP window size
```

## Escalation Guide

### When to Escalate

```
Escalate to Vendor Support When:
  - Configuration correct, still failing
  - Reproducible but cause unknown
  - Affecting multiple users/branches
  - Potential bug in VPN software
  - Need access to internal VPN logs

Information to Provide:
  - Exact error messages
  - Configuration (sanitized)
  - Client details (OS, version)
  - Server details (model, firmware)
  - Network diagram
  - Packet captures (if applicable)
  - Timeline (when started, any changes)
```

## Best Practices Checklist

- [ ] Keep logs for minimum 90 days
- [ ] Monitor VPN metrics continuously
- [ ] Test failover regularly
- [ ] Document all troubleshooting steps
- [ ] Maintain runbooks for common issues
- [ ] Train support team on debugging
- [ ] Use packet captures for complex issues
- [ ] Keep vendor contact info accessible
- [ ] Maintain spare appliances
- [ ] Regular backup of configurations
