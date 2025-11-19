# SDN Security Guide

## Security Architecture

### Layered Defense Model

```
Layer 1: Control Plane Security
├─ Controller authentication (certificates)
├─ TLS encryption (controller ↔ devices)
├─ API authentication and authorization
└─ Audit logging of all changes

Layer 2: Data Plane Security
├─ Flow-based access control (firewall)
├─ Microsegmentation (zero-trust)
├─ DPI (Deep Packet Inspection)
└─ Encryption (optional)

Layer 3: Management Plane Security
├─ RBAC (Role-Based Access Control)
├─ Separation of duties
├─ Change management approval
└─ Compliance monitoring
```

## Control Plane Security

### TLS for Controller Communication

```bash
# Generate certificate for controller
openssl genrsa -out controller.key 2048
openssl req -new -x509 -key controller.key -out controller.crt -days 365

# Configure ONOS for TLS
# etc/onos/certs/
├─ onos.crt (server certificate)
├─ onos.key (private key)
└─ onos.truststore (trusted CAs)

# Configure switches for TLS
# OpenFlow over TLS (port 6643)
openflow controller ipv4 10.0.0.1 port 6643 security tls certificate-id onos.crt
```

### API Security

```python
# Secure API endpoint configuration
from flask import Flask, request
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return {'error': 'Missing authorization header'}, 401

        try:
            token = auth_header.split()[1]
            payload = jwt.decode(token, app.config['SECRET_KEY'])
            request.user = payload
        except:
            return {'error': 'Invalid token'}, 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/api/networks', methods=['POST'])
@require_auth
def create_network():
    """Only authenticated users can create networks"""
    # Implementation
    pass

# Use HTTPS (TLS 1.2+)
# Use secure password hashing (bcrypt, not plaintext)
# Implement rate limiting
# Log all access
```

### Multi-Factor Authentication

```yaml
# Enable MFA for SDN controller
Authentication:
  ├─ Primary: Username/password (bcrypt hashed)
  ├─ Secondary: TOTP token (Google Authenticator)
  └─ Backup: Recovery codes

Configuration:
  mfa_enabled: true
  mfa_provider: "google-authenticator"
  session_timeout: 3600  # seconds
```

## Data Plane Security

### Microsegmentation with DFW

```bash
# VMware NSX Distributed Firewall Rules
Rules:
├─ Web Tier (10.100.0.0/24)
│  ├─ Ingress: Any → TCP 443 (allowed)
│  ├─ Egress: → App tier (10.101.0.0/24) TCP 8080 (allowed)
│  └─ Default: DENY all other
│
├─ App Tier (10.101.0.0/24)
│  ├─ Ingress: Web tier (10.100.0.0/24) TCP 8080 (allowed)
│  ├─ Egress: → DB tier (10.102.0.0/24) TCP 3306 (allowed)
│  └─ Default: DENY all other
│
└─ DB Tier (10.102.0.0/24)
   ├─ Ingress: App tier (10.101.0.0/24) TCP 3306 (allowed)
   ├─ Egress: Logging server (10.200.0.0/24) UDP 514 (allowed)
   └─ Default: DENY all other
```

### ONOS Security Policy

```python
# ONOS security policy enforcement
class SecurityPolicy:
    def create_isolation_policy(self, tenant_id, epgs):
        """Create zero-trust isolation between EPGs"""

        policies = []

        # Default deny all
        deny_all = {
            'action': 'DROP',
            'priority': 10000,
            'description': 'Default deny all'
        }
        policies.append(deny_all)

        # Explicit allow rules
        for source_epg in epgs:
            for dest_epg in epgs:
                if source_epg != dest_epg:
                    allow = {
                        'priority': 1000,
                        'source': source_epg,
                        'destination': dest_epg,
                        'protocol': 'tcp',
                        'port': dest_epg['allowed_port'],
                        'action': 'ALLOW',
                        'logging': True
                    }
                    policies.append(allow)

        return policies

    def enforce_policies(self, controller, policies):
        """Deploy policies to controller"""
        for policy in policies:
            controller.add_flow_rule(policy)
```

## Network Encryption

### IPsec Configuration

```bash
# Encrypt inter-VTEP traffic
# On Cisco switches
interface Tunnel1
  ip address 192.168.1.1 255.255.255.0
  tunnel source 10.0.0.1
  tunnel destination 10.0.0.2
  tunnel mode ipsec ipv4
  ip mtu 1400
  no ip unreachables

crypto ipsec transform-set TS esp-aes esp-sha-hmac
  mode transport

crypto map CRYPTOMAP 10 ipsec-isakmp
  set peer 10.0.0.2
  set transform-set TS
  match address 100

access-list 100 permit tcp 10.0.0.1 0.0.0.0 10.0.0.2 0.0.0.0

# Enable on interface
interface ethernet 1/1
  crypto map CRYPTOMAP
```

### TLS for Data Plane (Optional)

```python
# Encrypt overlay traffic with TLS
# Typically done at application level, not network level

import ssl
import socket

def create_secure_tunnel(source_ip, dest_ip, port=4789):
    """Create TLS-encrypted tunnel"""

    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = context.wrap_socket(sock, server_hostname=dest_ip)

    try:
        sock.connect((dest_ip, port))
        return sock
    except ssl.SSLError as e:
        print(f"SSL connection failed: {e}")
        return None
```

## DPI and Threat Detection

### Deep Packet Inspection

```python
# DPI configuration for threat detection
class ThreatDetection:
    def configure_dpi(self):
        """Configure DPI rules"""
        rules = {
            'malware_patterns': [
                'wannacry',
                'ransomware_signatures',
                'botnet_c2_domains'
            ],
            'anomalies': [
                'port_scan',
                'syn_flood',
                'dns_exfil',
                'unusual_volume'
            ],
            'blocking_enabled': True,
            'alert_enabled': True
        }
        return rules

    def detect_anomalies(self, flow_stats):
        """Detect abnormal traffic patterns"""

        alerts = []

        # Check for port scan
        if len(flow_stats['unique_ports']) > 100:
            alerts.append({
                'type': 'PORT_SCAN',
                'source': flow_stats['source_ip'],
                'severity': 'HIGH'
            })

        # Check for DDoS patterns
        if flow_stats['packet_rate'] > 10000:
            alerts.append({
                'type': 'POSSIBLE_DDoS',
                'source': flow_stats['source_ip'],
                'severity': 'CRITICAL'
            })

        # Check for data exfiltration
        if flow_stats['bytes_out'] / flow_stats['bytes_in'] > 10:
            alerts.append({
                'type': 'DATA_EXFIL',
                'source': flow_stats['source_ip'],
                'severity': 'HIGH'
            })

        return alerts
```

## Compliance & Audit

### Compliance Framework

```yaml
# Compliance requirements tracking
Compliance:
  PCI-DSS:
    ├─ Firewall: ✓ (DFW rules enforced)
    ├─ Access Control: ✓ (RBAC implemented)
    ├─ Encryption: ✓ (TLS for management)
    ├─ Logging: ✓ (Centralized syslog)
    └─ Regular audits: ✓ (Monthly)

  HIPAA:
    ├─ PHI Encryption: ✓ (TLS 1.2+)
    ├─ Access Control: ✓ (Role-based)
    ├─ Audit Trails: ✓ (Immutable logs)
    └─ Data Segregation: ✓ (VRF isolation)

  SOC 2:
    ├─ Access: ✓ (Documented RBAC)
    ├─ Change Control: ✓ (Approval workflow)
    ├─ Monitoring: ✓ (24/7 surveillance)
    └─ Incident Response: ✓ (Defined procedures)
```

### Audit Logging

```python
class AuditLogger:
    def log_action(self, user, action, resource, result):
        """Log all security-relevant actions"""

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'action': action,
            'resource': resource,
            'result': result,
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string
        }

        # Send to immutable log storage
        self.send_to_siem(log_entry)

        # Examples of logged actions:
        # - Policy creation/modification/deletion
        # - User login/logout
        # - Flow rule installation
        # - Security rule changes
        # - Configuration changes
        # - Privilege escalation attempts
```

## Zero-Trust Architecture

### Principles

```
1. Never Trust, Always Verify
   ├─ Verify user identity
   ├─ Verify device compliance
   ├─ Verify network security
   └─ Verify application safety

2. Least Privilege Access
   ├─ Minimal permissions
   ├─ Time-limited access
   ├─ Activity-specific rights
   └─ Regular access reviews

3. Assume Breach
   ├─ Microsegmentation (prevent lateral movement)
   ├─ Continuous monitoring (detect intrusions)
   ├─ Rapid response (limit damage)
   └─ Regular testing (validate controls)
```

### Implementation

```python
class ZeroTrustNetwork:
    def enforce_zero_trust(self, user_id, app_id, resource):
        """Zero-trust access decision"""

        checks = {
            'user_identity': self.verify_identity(user_id),
            'device_compliance': self.check_device_health(user_id),
            'location': self.verify_trusted_location(user_id),
            'time': self.check_access_hours(user_id, app_id),
            'app_trusted': self.verify_app_signature(app_id),
            'network_segment': self.verify_network_segment(resource)
        }

        # All checks must pass
        if all(checks.values()):
            return self.grant_access(user_id, app_id, resource)
        else:
            self.deny_access_and_alert(user_id, app_id, checks)
            return False
```

## Security Testing

### Security Audit Checklist

```
Network Security Audit:
☐ TLS enabled on all controller connections
☐ Certificates valid and non-expired
☐ Strong password policies enforced
☐ MFA enabled for privileged accounts
☐ RBAC properly configured
☐ Audit logging enabled and working
☐ No default credentials in use
☐ DFW rules tested and validated
☐ DPI enabled and detecting threats
☐ Encryption working end-to-end
☐ Compliance requirements met
☐ Vulnerability scanning performed
☐ Penetration testing completed
☐ Incident response plan tested
☐ Backup/recovery tested
```

### Penetration Testing

```bash
# Common security test scenarios

# 1. Test unauthorized access
# Try to access SDN API without credentials
curl -X GET http://controller:8181/api/devices
# Expected: 401 Unauthorized

# 2. Test privilege escalation
# Try to modify policies with read-only user
# Expected: 403 Forbidden

# 3. Test DPI detection
# Send malware signature patterns
# Expected: Detected and blocked

# 4. Test DFW bypass
# Try to reach isolated VLAN
# Expected: Traffic blocked by DFW

# 5. Test encryption
# Capture traffic on wire
# Expected: Encrypted, unreadable
```

## Security Best Practices

### Controller Security
- Update immediately when patches available
- Disable all unnecessary services
- Use strong, unique passwords
- Change default credentials
- Implement certificate pinning
- Enable audit logging
- Regular security backups

### Network Security
- Implement defense-in-depth
- Default deny all, explicit allow
- Monitor all traffic flows
- Regular threat intelligence updates
- Automated anomaly detection
- Incident response automation
- Security awareness training

### Operational Security
- Change management approval required
- Separation of duties (admin ≠ network ops)
- Regular access reviews
- Principle of least privilege
- Immutable audit logs
- Regular penetration testing
- Compliance audits quarterly

---

## Common Vulnerabilities & Mitigations

| Vulnerability | Impact | Mitigation |
|--------------|--------|-----------|
| Weak controller credentials | Full compromise | Strong pwd + MFA |
| Unencrypted APIs | Eavesdropping | TLS 1.2+ required |
| No RBAC | Unauthorized access | Fine-grained RBAC |
| Missing DFW | Lateral movement | Microsegmentation |
| Weak DPI | Threats missed | Update signatures |
| No audit logs | Non-repudiation | Centralized logging |
| Default credentials | Backdoor access | Change immediately |
| Outdated firmware | Exploitable | Regular patching |
