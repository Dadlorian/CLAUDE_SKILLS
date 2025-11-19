# Network Security Hardening Guide

## Security Baseline Framework

### Hardening Approach

```
Layers:
1. Perimeter: Firewall, DDoS, WAF
2. Network: Segmentation, VLANs, ACLs
3. Host: OS hardening, EDR, antivirus
4. Application: Input validation, auth, encryption
5. Data: Encryption, DLP, access control
6. Identity: MFA, RBAC, session management
7. Monitoring: Logging, SIEM, threat detection
8. Response: Incident response, forensics
```

## Perimeter Hardening

### Firewall Configuration

```
Basic Rules:
1. Ingress Filtering (RFC 2827)
   - Drop spoofed IP addresses
   - Verify source in connected networks
   - Drop private ranges from internet

2. Egress Filtering (RFC 5210)
   - Control internal → external traffic
   - Prevent data exfiltration
   - Block known malware C&C

3. Stateful Inspection
   - Track connection states
   - Allow return traffic only
   - Drop invalid states

Configuration (Cisco ASA):
! Ingress filtering
access-list INGRESS extended deny ip 10.0.0.0 255.255.0.0 any
access-list INGRESS extended deny ip 172.16.0.0 255.240.0.0 any
access-list INGRESS extended deny ip 192.168.0.0 255.255.0.0 any
access-list INGRESS extended deny ip any host 127.0.0.1
access-list INGRESS extended permit ip any any

! Apply to WAN interface
access-group INGRESS in interface outside

! Deny logging
logging enable
logging buffer-size 512000
logging class attacks
logging class default-implementation-level notifications
```

## Network Hardening

### VLAN Hardening

```
VLAN Configuration Best Practices:

1. Remove Default VLAN
vlan 1
 no active

2. Disable all ports initially
switchport port-security
switchport port-security max-mac-addrs 1
switchport port-security violation shutdown

3. Enable only needed ports
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security mac-address sticky

4. Trunk configuration
interface GigabitEthernet0/48
 switchport mode trunk
 switchport trunk allowed vlan 10,20,50,100
 switchport nonegotiate

5. Management access hardening
interface Vlan100
 ip address 10.1.100.1 255.255.255.0
 no ip directed-broadcast

line vty 0 4
 access-class MANAGEMENT in
 transport input ssh
 no transport input telnet
```

### DHCP Snooping

```
Prevent rogue DHCP servers:

Configuration:
ip dhcp snooping
ip dhcp snooping vlan 10,20,50

interface GigabitEthernet0/1
 ip dhcp snooping trust  (server port)

interface GigabitEthernet0/2
 ip dhcp snooping limit rate 15  (client port)

Verification:
show ip dhcp snooping
show ip dhcp snooping binding

Result:
- Only trusted ports can offer DHCP
- Client ports have rate limiting
- Prevents DHCP starvation attacks
- Tracks bindings
```

### Dynamic ARP Inspection (DAI)

```
Prevent ARP spoofing:

Configuration:
ip arp inspection vlan 10,20,50

interface GigabitEthernet0/1
 ip arp inspection trust  (DHCP server)

interface GigabitEthernet0/2
 ip arp inspection limit rate 15

Verification:
show ip arp inspection vlan 10
show ip arp inspection statistics

DHCP Snooping + DAI combination:
- DHCP snooping builds bindings
- DAI validates ARP against bindings
- Prevents ARP spoofing
- Prevents gratuitous ARP attacks
```

## Host Hardening

### Windows Hardening

```
OS Configuration:

1. Disable Unnecessary Services
Get-Service | Where-Object {$_.Status -eq 'Running'} | Format-Table

Services to disable:
- BITS
- Windows Update (use WSUS)
- Remote Registry
- Telemetry
- Unused print services

powershell:
Stop-Service -Name WSearch -Force
Set-Service -Name WSearch -StartupType Disabled

2. Enable Firewall
Set-NetFirewallProfile -Enabled True
Get-NetFirewallProfile

3. Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false
Start-MpScan -ScanType QuickScan

4. Windows Update
Get-WindowsUpdate -Install -AcceptAll -AutoReboot

5. Audit Logging
auditpol /set /category:* /success:enable /failure:enable

6. Encryption
Enable-BitLocker -MountPoint "C:" -EncryptionMethod Aes256

7. Password Policy
secedit /export /cfg C:\windows\security\local.sdb
secedit /configure /db C:\windows\security\local.sdb /cfg C:\windows\security\local.sdb /areas SECURITYPOLICY

8. User Account Control (UAC)
Set-ItemProperty -Path REGISTRY::HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System -Name EnableLUA -Value 1

9. Credential Guard (Windows 10/11)
New-Item -Path REGISTRY::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa -Name LsaCfgFlags -Value 1 -PropertyType DWORD -Force
```

### Linux Hardening

```
Basic Hardening:

1. Disable Unnecessary Services
systemctl list-unit-files --state=enabled
systemctl disable avahi-daemon
systemctl disable cups
systemctl stop avahi-daemon
systemctl stop cups

2. Firewall (UFW/iptables)
ufw enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw status

3. SSH Hardening
/etc/ssh/sshd_config:
Port 2222  (non-standard port)
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
X11Forwarding no
UsePAM yes
PermitUserEnvironment no
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org

service ssh restart
ssh-keygen -A

4. File Permissions
chmod 644 /etc/passwd
chmod 644 /etc/group
chmod 600 /etc/shadow
chmod 600 /etc/gshadow
chmod 755 /etc
chmod 755 /var

5. Disable Unnecessary Protocols
echo "install sctp /bin/true" >> /etc/modprobe.d/sctp.conf

6. SELinux/AppArmor
semanage port -a -t ssh_port_t -p tcp 2222
getenforce

7. Audit Logging
apt-get install auditd
systemctl enable auditd
auditctl -w /etc/passwd -p wa -k passwd_changes
auditctl -w /etc/shadow -p wa -k shadow_changes
```

## Application Hardening

### Web Application Security

```
Input Validation:

Principle: Never trust user input

Implementation:
1. Whitelist validation
   Valid chars only
   Length limits
   Type checking

2. Output encoding
   HTML encoding for HTML context
   URL encoding for URLs
   JavaScript encoding for JS
   CSS encoding for CSS

3. SQL Injection Prevention
   Use parameterized queries
   Use ORM frameworks
   Input validation
   Least privilege DB accounts

Example (Java):
String sql = "SELECT * FROM users WHERE id = ?";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, userId);
ResultSet rs = pstmt.executeQuery();

4. Cross-Site Scripting (XSS) Prevention
   Output encoding
   Content Security Policy
   HTTPOnly cookies
   X-XSS-Protection header

5. Cross-Site Request Forgery (CSRF) Prevention
   CSRF tokens
   SameSite cookies
   Verify referrer headers
```

### API Security

```
API Hardening:

1. Authentication
   - Require API key
   - Use OAuth 2.0
   - Use JWT tokens
   - Implement MFA for sensitive operations

2. Authorization
   - Role-based access control (RBAC)
   - Check user permissions
   - Implement least privilege
   - Rate limiting per user

3. Encryption
   - TLS 1.2 minimum for all API calls
   - Sign requests (HMAC)
   - Encrypt sensitive data in transit

4. Logging
   - Log all API calls
   - Include: user, timestamp, endpoint, params, response
   - Log authentication failures
   - Alert on suspicious patterns

5. Rate Limiting
   - Global: 10,000 requests/hour
   - Per-user: 1,000 requests/hour
   - Per-endpoint: 100 requests/minute
   - Return 429 Too Many Requests

Example (Node.js):
const rateLimit = require("express-rate-limit");
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: "Too many requests"
});
app.use(limiter);
```

## Data Hardening

### Encryption Standards

```
Data at Rest:
- Encryption: AES-256
- Key management: HSM or AWS KMS
- Key rotation: Annual minimum

Data in Transit:
- Protocol: TLS 1.2 minimum (1.3 preferred)
- Cipher: AES-256-GCM
- Certificate: Valid, trusted CA
- Pinning: For critical APIs

Database Encryption:
- Column-level: Sensitive data (PII, payment cards)
- Transparent Data Encryption (TDE): Entire DB
- Always Encrypted: Client-side encryption

Configuration (PostgreSQL):
-- Column encryption with pgcrypto
CREATE EXTENSION pgcrypto;
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username TEXT,
  ssn BYTEA,  -- encrypted
  email TEXT
);
INSERT INTO users VALUES (1, 'john', encrypt('123-45-6789'::bytea, 'key'::bytea, 'aes'), 'john@example.com');
```

### Key Management

```
Key Management Best Practices:

1. Generation
   - Use cryptographically secure random source
   - Sufficient entropy (256-bit+)
   - Stored immediately after generation

2. Storage
   - Hardware Security Module (HSM)
   - Vault software (HashiCorp, AWS Secrets Manager)
   - Never in source code
   - Never in logs
   - Never in plaintext

3. Rotation
   - Annual minimum
   - Upon personnel change
   - Upon suspected compromise
   - Automated rotation process

4. Retirement
   - Archive encrypted
   - Maintain for legal holds (7 years)
   - Destroy unneeded keys
   - Document retirement

Configuration (HashiCorp Vault):
vault write -f transit/keys/myapp
vault write transit/encrypt/myapp plaintext=@secret.txt
vault write transit/decrypt/myapp ciphertext=vault:v1:...
```

## Monitoring and Response

### Security Logging

```
Log Sources:
- Firewall (all denied traffic, policy changes)
- Network (unusual traffic patterns)
- Authentication (failed logins, privilege escalation)
- Application (errors, security events)
- System (changes, access)
- Database (queries, access)

Centralization:
- Syslog server or SIEM
- Real-time processing
- Alert on suspicious patterns

Log Retention:
- Hot: 30 days
- Warm: 90 days
- Cold: 1 year (compliance)

Configuration:
logging host 10.1.50.10
logging level 5
logging buffered 512000
logging timestamp
```

### Incident Response

```
Detection:
- IDS/IPS alerts
- EDR events
- SIEM correlation
- User reports

Containment:
- Isolate affected system
- Revoke access rights
- Block malicious IP
- Disconnect VPN sessions

Eradication:
- Patch vulnerability
- Remove malware
- Reset credentials
- Update configurations

Recovery:
- Restore from clean backup
- Monitor for re-infection
- Verify security controls

Post-Incident:
- Root cause analysis
- Improve security
- Train team
- Update playbooks
```

## Security Assessment

### Regular Testing

```
Schedule:
- Monthly: Vulnerability scanning
- Quarterly: Penetration testing
- Annually: Full security assessment

Vulnerability Scanning:
- Nessus, OpenVAS, Qualys
- Identify missing patches
- Detect misconfigurations
- Remediate critical findings

Penetration Testing:
- Internal testing
- External testing
- Social engineering
- Physical security

Compliance Audits:
- Verify controls
- Check documentation
- Test access
- Review logs
```

## Continuous Improvement

### Processes

```
1. Threat Intelligence
   - Subscribe to threat feeds
   - Monitor for new CVEs
   - Track emerging attacks
   - Share with team

2. Security Training
   - Annual mandatory training
   - Department-specific training
   - Incident simulation exercises
   - Phishing simulations

3. Policy Updates
   - Annual review
   - Update for new threats
   - Incorporate lessons learned
   - Communicate changes

4. Technology Refresh
   - OS upgrade cycles
   - Firewall/security tool updates
   - Encryption standard updates
   - Protocol version updates

5. Metrics
   - Track security events
   - Measure response time
   - Monitor compliance
   - Report to leadership
```
