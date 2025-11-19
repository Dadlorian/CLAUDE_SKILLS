# SSL VPN Deployment Guide

## Overview
Deploy SSL/TLS VPN gateway for remote user access with centralized authentication and device compliance checking.

## Pre-Deployment Planning

### Architecture Decision

**Portal-Based (Clientless)**
- No client installation
- Browser-based access
- Limited functionality
- Good for: Contractors, one-time access

**Client-Based (Full Tunnel)**
- Dedicated client application
- Full network access
- Advanced features
- Good for: Full-time remote workers

**Hybrid Approach (Recommended)**
- Portal for general access
- Client for power users
- Flexibility in deployment

### Capacity Planning

```
User Concurrent Sessions: 500
Average Bandwidth per User: 2 Mbps
Peak Hour Load: 60% (300 users)
Aggregate Bandwidth: 600 Mbps

Hardware Requirements:
- CPU: 8+ cores for 500 users
- RAM: 16 GB minimum
- NIC: 10 Gbps recommended
- Storage: 500 GB SSD
```

## Phase 1: Cisco AnyConnect Deployment

### Portal Configuration

```
Gateway IP: 203.0.113.1
Gateway Hostname: vpn.company.com
Portal Theme: Company branding
Authentication: Active Directory + Duo MFA
```

### Installation and Initial Setup

**1. Download AnyConnect Package**
```bash
# From Cisco website or internal repository
wget https://cisco.company.com/anyconnect/
tar -xzf anyconnect-enterprise.tar.gz
```

**2. Configure Deployment Package**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AnyConnectProfile>
  <ServerList>
    <HostEntry>
      <HostName>vpn.company.com</HostName>
      <HostAddress>203.0.113.1</HostAddress>
      <PrimaryProtocol>ssl</PrimaryProtocol>
    </HostEntry>
  </ServerList>
  <ClientInitialization>
    <UseStartBeforeLogon>false</UseStartBeforeLogon>
    <AutoConnectOnStart>false</AutoConnectOnStart>
  </ClientInitialization>
  <AuthenticationMethods>
    <AuthenticationMethod Priority="0">
      <AuthType>UsernamePassword</AuthType>
    </AuthenticationMethod>
  </AuthenticationMethods>
</AnyConnectProfile>
```

### ASA Configuration (Cisco Example)

**SSL/TLS Settings**
```cisco
! Enable SSL
ssl encryption encipher-aes-256 encipher-aes-192 encipher-aes-128 encipher-3des
ssl trust-point INTERNAL-CA peer-id-validation nocheck

! TLS version enforcement
ssl protocol tlsv1.2 tlsv1.3
ssl security renegotiate-on-lifetime-expiry
```

**Portal Configuration**
```cisco
! Create webvpn session
webvpn
  enable outside
  secondary-color white
  tertiary-color #003366
  logo file logos/company-logo.png
  title "Corporate VPN Portal"

  tunnel-group-list enable
  enable csd
  enable client-firewall-filter
```

**User Authorization**
```cisco
group-policy RemoteAccess internal
  attributes
    banner value "Authorized Access Only"
    windows-client-admin admin
    split-dns value internal.corp.com
    split-tunnel-policy tunnelspecified
    split-tunnel-network-list value REMOTE-SPLIT-TUNNEL
    dns-server value 10.0.0.1 8.8.8.8
    default-domain value corp.internal
    pfs enable
    re-xauth disable
    address-pools value REMOTE-USERS
    ssl-vpn keep-alive interval 300
    ssl-vpn keep-alive type dpd
    session-timeout 28800
    password-storage disable
```

**Split Tunnel Access List**
```cisco
access-list REMOTE-SPLIT-TUNNEL extended permit ip any 10.0.0.0 255.0.0.0
access-list REMOTE-SPLIT-TUNNEL extended permit ip any 192.168.0.0 255.255.0.0
```

**Tunnel Group Configuration**
```cisco
tunnel-group RemoteVPN type remote-access
tunnel-group RemoteVPN general-attributes
  authentication-server-group LDAP LOCAL
  accounting-server-group LDAP
  default-group-policy RemoteAccess
  address-pool REMOTE-USERS

tunnel-group RemoteVPN webvpn-attributes
  group-alias RemoteVPN enable
  reuse-sso enable
  required-client-firewall-versions 5.1
  required-client-firewall-action block
  authentication aaa
  authentication-portal enable
  authentication-server-group LDAP LOCAL
  accounting-server-group LDAP
  url-list value webvpn-urls
  file-access enable
  file-browse enable
  bookmarks enable
```

## Phase 2: Palo Alto GlobalProtect Deployment

### Portal Setup

**Network Configuration**
```
Portal IP: 192.0.2.1
Gateway IP: 192.0.2.2
Internal Subnet: 10.0.0.0/8
VPN Subnet: 10.255.0.0/24
```

**Client Deployment Package**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GlobalProtectXML>
  <ClientVersion>5.1.0</ClientVersion>
  <AuthenticationProfile>
    <AuthenticationMethod>saml-sso</AuthenticationMethod>
    <SSOProxyAddress>portal.company.com</SSOProxyAddress>
  </AuthenticationProfile>
  <Gateway>
    <Name>Primary Gateway</Name>
    <Address>gw.company.com</Address>
    <Priority>1</Priority>
  </Gateway>
  <Gateway>
    <Name>Secondary Gateway</Name>
    <Address>gw-backup.company.com</Address>
    <Priority>2</Priority>
  </Gateway>
</GlobalProtectXML>
```

### Portal Configuration (Palo Alto)

**Object > Administrators > Admin Users**
```
Username: vpn-admin
Role: GlobalProtect Admin
Authentication: LDAP
```

**Objects > Authentication**
```
Server Profile: corporate-ldap
Type: LDAP
Server: 10.0.0.50
Base DN: cn=users,dc=corp,dc=com
Bind DN: cn=bind-user,cn=users,dc=corp,dc=com
```

**Device > Certificate Management**
```
Generate Self-Signed: No
Import CA Certificate: Corporate-CA
Certificate File: /ssl/certs/vpn.company.com.crt
Private Key: /ssl/private/vpn.company.com.key
```

**Network > GlobalProtect > Portals**
```
Portal Name: Corporate Portal
Interface: Ethernet1/1
Authentication Profile: LDAP-Corporate
Client Version: 5.1.0
App-ID: Enable
Mobile Profile: Enabled
User Domain: corp.internal
```

**Network > GlobalProtect > Gateways**
```
Gateway Name: Primary Gateway
Interface: Ethernet1/2
Authentication Profile: LDAP-Corporate
Tunnel Protocol: IPsec
IPsec Protocol: IKEv2
Encryption: AES-256-GCM
Authentication: SHA-256
DH Group: Group 14
Tunnel Monitor: Enable
```

## Phase 3: Authentication Integration

### Active Directory Integration

**Cisco ASA Configuration**
```cisco
aaa-server LDAP protocol ldap
aaa-server LDAP host 10.0.0.50
  server-port 389
  ldap-base-dn cn=Users,dc=corp,dc=com
  ldap-scope subtree
  ldap-naming-attribute sAMAccountName
  ldap-login-password-attr userPassword

! Test connection
test aaa-server authentication LDAP user testuser password testpass
```

**Palo Alto GlobalProtect**
```
Network > GlobalProtect > Portals > Authentication Profile
  Server Profile: Select corporate-ldap
  User Domain: corp.internal
  Allow List: specific-domains
  Domain: corp.internal
```

### Multi-Factor Authentication (Duo)

**Cisco AnyConnect + Duo**
```cisco
! Configure Duo integration
tunnel-group RemoteVPN general-attributes
  duo-auth-server primary
  duo-client-id [INTEGRATION_KEY]
  duo-client-secret [SECRET_KEY]
  duo-api-host api-xxxxxxxx.duosecurity.com

group-policy RemoteAccess internal
  attributes
    mfa required
    mfa-mode dual
```

**Palo Alto + Okta (SAML)**
```
Device > Certificate Management > Import
  Certificate: okta-saml-cert.pem

Network > GlobalProtect > Portals
  Authentication Profile: SAML-OKTA
  IdP Server: https://corp.okta.com
  IdP Port: 443
  IdP Path: /app/amazon_aws/exk123456/sso/saml
```

## Phase 4: Device Posture Policies

### Client Security Requirements

**Cisco ASA Posture Enforcement**
```cisco
! AnyConnect posture profile
posture-profile DefaultProfile
  require ips-software Microsoft-Defender
  require av-software Symantec-Endpoint
  require fw-software Windows-Firewall
  require os-version windows-10-or-later
  require patch-level current
  require encrypted-disk BitLocker

! Apply posture check
group-policy RemoteAccess internal
  attributes
    posture-profile DefaultProfile
    posture-non-compliant-action remediate
```

**Palo Alto Device Compliance**
```
Network > GlobalProtect > Gateways > Client Compliance
  Security Profile: Standard
  Checks:
    - Antivirus installed and running
    - Firewall enabled
    - OS patches current
    - Disk encryption enabled
    - No jailbreak/root

  Non-compliant Action: Block Access
```

## Phase 5: Testing and Validation

### Connectivity Testing

**Client Connection Test**
```bash
# Windows/macOS
# Open AnyConnect client
# Enter: vpn.company.com
# Username: testuser
# Password: [password]
# Approve Duo push notification

# Verify connection
ipconfig (Windows)
ifconfig (macOS)
  Should show: AnyConnect or tun interface with 10.255.x.x

# Test access
ping 10.0.1.1  # Corp resource
ping 192.168.1.1  # Another subnet
```

### Performance Baseline

```
Latency Test:
  Command: ping -c 100 10.0.1.1
  Expected: 5-20 ms average
  Packet Loss: < 1%

Throughput Test:
  Download: 50+ Mbps on corporate link
  Upload: 25+ Mbps on corporate link
  Connection stability: Consistent over 5 minutes

Session Duration:
  Connect time: < 30 seconds
  Idle keepalive: 300 seconds
  Reconnect time: < 15 seconds
```

### Authentication Audit

```
Gateway Logs:
  show admin-log | include authentication
  Expected: Successful auth for test account

Posture Check:
  Verify non-compliant device blocked
  Verify compliant device allowed
  Check endpoint profile download
```

## Phase 6: Production Rollout

### Phased Deployment

**Phase 1: Pilot (Week 1-2)**
- 10-20 test users
- IT staff and executives
- Daily monitoring
- Feedback collection

**Phase 2: Department Rollout (Week 3-6)**
- Sales team (200 users)
- Engineering team (150 users)
- Support team (50 users)
- Weekly status meetings

**Phase 3: Full Deployment (Week 7-8)**
- Remaining users
- Partner/contractor access
- Establish production support
- Final optimization

### Communication Plan

1. **Announcement** (1 week before)
   - Email explaining new VPN
   - Benefits of new system
   - Timeline for rollout

2. **Training** (2-3 days before)
   - Video tutorial
   - Live webinar
   - FAQ document

3. **Support**
   - Help desk training
   - Support ticket procedures
   - Escalation path

## Phase 7: Ongoing Management

### Monitoring Metrics

```
Daily Metrics:
  - Active sessions count
  - Peak concurrent users
  - Failed authentication attempts
  - Bandwidth utilization
  - Device compliance rate

Weekly Reports:
  - Connection success rate (target: >99.5%)
  - Average session duration
  - Geographic distribution
  - Top accessed resources
  - Performance metrics

Monthly Review:
  - User growth trends
  - Security event analysis
  - Firmware/software updates applied
  - Capacity planning adjustments
```

### Maintenance Windows

```
Scheduled Maintenance: Sundays 2-4 AM UTC
Notification: 2 weeks advance notice
Expected Downtime: 15-30 minutes
Rollback Plan: Documented and tested
```

### Certificate Management

```
Certificate Renewal: 90 days before expiry
Testing: Validated in test environment first
Deployment: Minimal disruption to users
Documentation: Updated CA bundle versions
```

## Troubleshooting Matrix

| Issue | Symptoms | Diagnosis | Solution |
|-------|----------|-----------|----------|
| Auth Failure | Cannot login | Check LDAP connection | Verify AD/LDAP config |
| Device Blocked | Posture failed | Check security requirements | Update OS, AV, patches |
| Slow Access | High latency | Monitor gateway CPU | Load balance users |
| DNS Issues | Cannot resolve hosts | Check split-DNS config | Verify DNS server push |
| Certificate Expired | SSL error | Check cert validity | Renew and deploy |

## Best Practices Checklist

- [ ] Use TLS 1.3 minimum
- [ ] Enforce MFA for all users
- [ ] Implement device compliance
- [ ] Monitor bandwidth per user
- [ ] Set idle timeout (30 min)
- [ ] Log all authentication
- [ ] Regular security updates
- [ ] Load test before production
- [ ] Establish incident response
- [ ] Document all procedures
- [ ] Backup certificates securely
- [ ] Plan for disaster recovery
