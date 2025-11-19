# Medical Device Cybersecurity Implementation Guide

## Pre-Development Phase

### Step 1: Threat Modeling

**Use STRIDE:**
```markdown
# Threat Model

## Assets
1. Patient data (PHI)
2. Treatment parameters
3. Device firmware
4. Configuration data
5. Authentication credentials

## Entry Points
1. Network interface (Wi-Fi, Ethernet)
2. USB ports
3. Web interface
4. Mobile app
5. Physical access

## Threats

### Spoofing
- Attacker impersonates authorized user
- Fake device on network
- Man-in-the-middle attack

### Tampering
- Modify treatment parameters
- Alter patient data
- Inject malicious code

### Repudiation
- User denies actions
- No audit trail

### Information Disclosure
- PHI leaked
- Proprietary algorithms exposed

### Denial of Service
- Device unavailable
- Network flooding

### Elevation of Privilege
- Gain admin access
- Bypass security controls
```

### Step 2: Security Requirements

**Derive from threats:**
```markdown
# Security Requirements

## Authentication
SEC-001: System shall require unique user credentials
SEC-002: System shall enforce password complexity (≥8 chars, mixed case, numbers)
SEC-003: System shall lock account after 5 failed attempts
SEC-004: System shall require password change every 90 days

## Authorization
SEC-010: System shall implement role-based access control
SEC-011: System shall enforce principle of least privilege

## Data Protection  
SEC-020: System shall encrypt data at rest (AES-256)
SEC-021: System shall encrypt data in transit (TLS 1.3)
SEC-022: System shall protect PHI per HIPAA

## Audit Trail
SEC-030: System shall log all user actions
SEC-031: System shall log security events
SEC-032: System shall protect logs from tampering

## Software Updates
SEC-040: System shall verify update authenticity (digital signature)
SEC-041: System shall verify update integrity (hash)
SEC-042: System shall support rollback

## Network Security
SEC-050: System shall support firewall configuration
SEC-051: System shall use secure protocols only
```

## Development Phase

### Secure Coding Practices

**Use CERT C/CERT C++ or MISRA-C:**
```c
// GOOD: Input validation
int setDoseLimit(int limit) {
    if (limit < MIN_DOSE || limit > MAX_DOSE) {
        logError("Invalid dose limit: %d", limit);
        return ERROR_INVALID_PARAMETER;
    }
    doseLimit = limit;
    logAudit("Dose limit changed to %d", limit);
    return SUCCESS;
}

// BAD: No validation
int setDoseLimit(int limit) {
    doseLimit = limit;  // Could be negative or excessive
    return SUCCESS;
}

// GOOD: Prevent buffer overflow
void processCommand(const char* command) {
    char buffer[256];
    strncpy(buffer, command, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';  // Ensure null termination
}

// BAD: Buffer overflow vulnerability
void processCommand(const char* command) {
    char buffer[256];
    strcpy(buffer, command);  // Dangerous!
}
```

### Cryptographic Implementation

**Use established libraries (OpenSSL, mbedTLS):**
```c
// Use AES-256 for data at rest
#include <openssl/evp.h>

int encryptData(const unsigned char* plaintext, int plaintext_len,
                unsigned char* key, unsigned char* iv,
                unsigned char* ciphertext) {
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    int len, ciphertext_len;
    
    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv);
    EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len);
    ciphertext_len = len;
    EVP_EncryptFinal_ex(ctx, ciphertext + len, &len);
    ciphertext_len += len;
    
    EVP_CIPHER_CTX_free(ctx);
    return ciphertext_len;
}

// Use TLS 1.3 for network communication
SSL_CTX* ctx = SSL_CTX_new(TLS_method());
SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION);
```

### Audit Trail Implementation

```javascript
// Comprehensive audit logging
class AuditLogger {
  logUserAction(userId, action, details) {
    const entry = {
      timestamp: new Date().toISOString(),
      userId: userId,
      action: action,
      details: details,
      ipAddress: this.getClientIP(),
      sessionId: this.getSessionId()
    };
    
    // Sign entry for tamper protection
    entry.signature = this.signEntry(entry);
    
    // Store in tamper-evident log
    this.writeToLog(entry);
  }
  
  logSecurityEvent(eventType, severity, details) {
    const entry = {
      timestamp: new Date().toISOString(),
      eventType: eventType,
      severity: severity,  // Critical, High, Medium, Low
      details: details
    };
    
    entry.signature = this.signEntry(entry);
    this.writeToLog(entry);
    
    // Alert on critical events
    if (severity === 'Critical') {
      this.sendAlert(entry);
    }
  }
}

// Usage
auditLogger.logUserAction(userId, 'DOSE_CHANGED', {from: 10, to: 15});
auditLogger.logSecurityEvent('FAILED_LOGIN', 'High', {userId: 'user123', attempts: 5});
```

### Secure Update Mechanism

```python
# Firmware update with signature verification
import hashlib
import rsa

def verifyAndInstallUpdate(update_file, signature_file):
    # Load public key
    with open('public_key.pem', 'rb') as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
    
    # Read update file
    with open(update_file, 'rb') as f:
        update_data = f.read()
    
    # Read signature
    with open(signature_file, 'rb') as f:
        signature = f.read()
    
    # Verify signature
    try:
        rsa.verify(update_data, signature, public_key)
        print("Signature valid")
    except rsa.VerificationError:
        print("Signature invalid - update rejected")
        return False
    
    # Verify hash
    expected_hash = hashlib.sha256(update_data).hexdigest()
    if expected_hash != PUBLISHED_HASH:
        print("Hash mismatch - update rejected")
        return False
    
    # Install update
    installUpdate(update_data)
    
    # Verify installation
    if not verifyInstallation():
        rollback()
        return False
    
    return True
```

## Testing Phase

### Vulnerability Testing

**Static Analysis:**
```bash
# Run static analysis tools
coverity --build ./build.sh
klocwork --project medical_device
sonarqube-scanner

# Check for vulnerabilities
bandit -r ./src/  # Python
cppcheck --enable=all ./src/  # C++
```

**Dynamic Analysis:**
```bash
# Memory safety
valgrind --leak-check=full ./device_software

# Fuzz testing
AFL_FUZZ ./device_software @@
```

### Penetration Testing

**Test Plan:**
```markdown
# Penetration Test Plan

## Network Testing
- Port scanning
- Service enumeration
- Protocol analysis
- Man-in-the-middle attempts
- Network injection

## Authentication Testing
- Brute force attacks
- Credential stuffing
- Session hijacking
- Token manipulation

## Authorization Testing
- Privilege escalation
- Access control bypass
- Horizontal/vertical privilege violations

## Input Validation
- SQL injection (if applicable)
- Command injection
- Buffer overflow attempts
- Format string vulnerabilities

## Cryptography
- Weak cipher detection
- Key management review
- Certificate validation

## Web Interface (if applicable)
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Session management
- Authentication bypass
```

### Fuzz Testing

```python
# Example fuzzer for network protocol
import socket
import random

def fuzz_protocol():
    # Generate random malformed packets
    for i in range(10000):
        payload = generate_random_payload()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('device_ip', 5000))
            sock.send(payload)
            response = sock.recv(1024)
            # Monitor for crashes, hangs, error messages
        except Exception as e:
            log_exception(i, payload, e)
        finally:
            sock.close()

def generate_random_payload():
    # Create malformed data
    length = random.randint(0, 10000)
    return bytes([random.randint(0, 255) for _ in range(length)])
```

## Post-Market Phase

### Vulnerability Monitoring

**Daily Monitoring:**
```python
# Automated vulnerability scanner
import requests
import json

def check_vulnerabilities():
    # Check NVD for component vulnerabilities
    components = load_sbom()  # Software Bill of Materials
    
    for component in components:
        nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/1.0?keyword={component['name']}"
        response = requests.get(nvd_url)
        cves = response.json()
        
        for cve in cves.get('result', {}).get('CVE_Items', []):
            if is_applicable(cve, component):
                severity = get_cvss_score(cve)
                if severity >= 7.0:  # High/Critical
                    alert_security_team(component, cve)
                log_vulnerability(component, cve)

def is_applicable(cve, component):
    # Check if CVE affects our specific version
    affected_versions = parse_cve_versions(cve)
    return component['version'] in affected_versions
```

### Patch Management

**Process:**
```markdown
# Patch Management Procedure

## 1. Vulnerability Assessment
- Confirm vulnerability applicability
- Assess exploitability
- Determine patient safety impact
- Assign priority (Critical/High/Medium/Low)

## 2. Patch Development
- Develop fix
- Code review
- Unit testing
- Security testing
- Regression testing

## 3. Validation
- IQ/OQ/PQ testing
- Penetration testing
- Verify vulnerability resolved

## 4. Regulatory Assessment
- Determine if 510(k)/PMA supplement needed
- Prepare regulatory notification if required

## 5. Deployment
- Phased rollout
- Customer notification
- Installation support
- Verify deployment

## 6. Monitoring
- Monitor for issues
- Track deployment status
- Verify effectiveness
```

### Incident Response

**Incident Response Plan:**
```markdown
# Cybersecurity Incident Response Plan

## Detection
- Security alerts
- User reports
- Log analysis
- Threat intelligence

## Analysis
- Confirm incident
- Assess scope
- Identify affected systems
- Determine impact

## Containment
- Isolate affected devices
- Block malicious traffic
- Prevent further exploitation
- Preserve evidence

## Eradication
- Remove threat
- Patch vulnerability
- Verify removal

## Recovery
- Restore normal operations
- Monitor for recurrence
- Verify device functionality

## Lessons Learned
- Document incident
- Analyze root cause
- Update procedures
- Improve defenses
```

## SBOM Management

### Create and Maintain SBOM

**SBOM in SPDX format:**
```json
{
  "spdxVersion": "SPDX-2.2",
  "dataLicense": "CC0-1.0",
  "name": "Medical Device Software SBOM",
  "documentNamespace": "https://example.com/sbom/device-v1.0",
  "packages": [
    {
      "name": "OpenSSL",
      "versionInfo": "3.0.1",
      "supplier": "Organization: OpenSSL Foundation",
      "downloadLocation": "https://openssl.org/",
      "filesAnalyzed": false,
      "externalRefs": [
        {
          "referenceCategory": "SECURITY",
          "referenceType": "cpe23Type",
          "referenceLocator": "cpe:2.3:a:openssl:openssl:3.0.1:*:*:*:*:*:*:*"
        }
      ]
    },
    {
      "name": "SQLite",
      "versionInfo": "3.40.0",
      "supplier": "Organization: SQLite Consortium",
      "licenseConcluded": "Public-Domain"
    }
  ]
}
```

**Update Process:**
- Generate SBOM for each release
- Track all dependencies
- Monitor for vulnerabilities
- Update SBOM with changes

---

**Key Takeaway**: Medical device cybersecurity requires security by design, defense in depth, continuous monitoring, and rapid response. Threat modeling drives requirements, secure coding prevents vulnerabilities, comprehensive testing finds issues, and post-market vigilance maintains security.
