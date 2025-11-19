# Incident Response Playbook

## Phase 1: Preparation

### Before an Incident
- [ ] Incident response team identified
- [ ] Contact list updated
- [ ] Tools and access ready
- [ ] Runbooks documented
- [ ] Communication channels tested
- [ ] Legal/PR contacts identified
- [ ] Backup and recovery tested

### IR Tools Checklist
- [ ] Forensics toolkit ready
- [ ] Log aggregation configured
- [ ] Network capture tools
- [ ] Memory analysis tools
- [ ] Malware analysis sandbox
- [ ] Ticketing system configured

## Phase 2: Detection & Analysis

### Initial Detection
1. **Alert Received**
   - Source: SIEM, EDR, User report, External notification
   - Timestamp of detection
   - Initial scope assessment

2. **Triage**
   ```
   Priority Matrix:
   - P1 (Critical): Active breach, data exfiltration
   - P2 (High): Malware infection, unauthorized access
   - P3 (Medium): Suspicious activity, policy violation
   - P4 (Low): False positive investigation
   ```

3. **Initial Analysis**
   - Confirm true positive
   - Identify affected systems
   - Determine attack vector
   - Assess data at risk

### Investigation Checklist

#### Network Analysis
- [ ] Review firewall logs
- [ ] Analyze NetFlow data
- [ ] Check IDS/IPS alerts
- [ ] Review proxy logs
- [ ] Examine DNS queries
- [ ] Capture suspicious traffic

#### Host Analysis
- [ ] Check running processes
- [ ] Review scheduled tasks
- [ ] Examine registry changes (Windows)
- [ ] Check system logs
- [ ] Analyze file modifications
- [ ] Review user accounts
- [ ] Check persistence mechanisms

#### Log Analysis
```bash
# Search for failed login attempts
grep "Failed password" /var/log/auth.log | tail -100

# Search for privilege escalation
grep -i "sudo" /var/log/auth.log | grep "COMMAND"

# Check for new user accounts
grep -i "useradd\|adduser" /var/log/secure

# Unusual network connections
netstat -antp | grep ESTABLISHED
```

## Phase 3: Containment

### Short-term Containment
**Goals**: Stop spread, preserve evidence

1. **Network Isolation**
   ```bash
   # Isolate infected host (preserve state)
   iptables -P INPUT DROP
   iptables -P OUTPUT DROP
   iptables -P FORWARD DROP
   
   # Allow only IR team access
   iptables -A INPUT -s <IR_IP> -j ACCEPT
   ```

2. **Account Lockout**
   ```bash
   # Disable compromised account
   usermod -L username
   
   # Expire password
   passwd -l username
   
   # Revoke active sessions
   pkill -u username
   ```

3. **Evidence Preservation**
   ```bash
   # Capture memory dump
   sudo dd if=/dev/mem of=/mnt/usb/memory.dump bs=1M
   
   # Capture disk image
   sudo dd if=/dev/sda of=/mnt/storage/disk.img bs=4M
   
   # Capture network traffic
   tcpdump -i eth0 -w /mnt/storage/capture.pcap
   ```

### Long-term Containment
**Goals**: Restore operations while investigating

1. **System Segregation**
   - Move to isolated VLAN
   - Monitor all traffic
   - Maintain business continuity

2. **Patch Vulnerabilities**
   - Apply security updates
   - Close attack vector
   - Harden configurations

## Phase 4: Eradication

### Remove Threat
1. **Malware Removal**
   ```bash
   # Identify malware processes
   ps aux | grep suspicious_process
   
   # Kill malicious process
   kill -9 <PID>
   
   # Remove malware files
   find / -name "malware.sh" -delete
   
   # Clean persistence
   crontab -l | grep -v malware | crontab -
   ```

2. **Account Cleanup**
   - Remove unauthorized accounts
   - Reset compromised passwords
   - Revoke stolen credentials
   - Rotate API keys/tokens

3. **System Hardening**
   - Close unnecessary ports
   - Update firewall rules
   - Enable security controls
   - Apply patches

## Phase 5: Recovery

### System Restoration
1. **Rebuild vs Restore Decision Matrix**
   ```
   Rebuild if:
   - Rootkit suspected
   - Extensive compromise
   - Regulatory requirement
   
   Restore if:
   - Limited compromise
   - Clean backup available
   - Time-critical system
   ```

2. **Restore from Backup**
   ```bash
   # Verify backup integrity
   sha256sum backup.tar.gz
   
   # Restore files
   tar -xzf backup.tar.gz -C /restore/location
   
   # Verify restoration
   diff -r /original /restored
   ```

3. **Gradual Return to Production**
   - Phase 1: Isolated testing
   - Phase 2: Limited users
   - Phase 3: Full production
   - Monitoring: Enhanced for 30 days

## Phase 6: Post-Incident

### Lessons Learned Meeting
**Within 2 weeks of incident**

Agenda:
1. Incident timeline
2. What went well?
3. What could be improved?
4. Action items

### Documentation
- [ ] Complete incident report
- [ ] Update runbooks
- [ ] Document new IOCs
- [ ] Update detection rules
- [ ] Share threat intelligence

### Improvements
- [ ] Implement technical controls
- [ ] Update policies
- [ ] Training for staff
- [ ] Test improvements

## Ransomware-Specific Response

### Immediate Actions
1. **Isolate infected systems**
   - Disconnect from network
   - Do NOT power off (preserve evidence)
   - Document ransom note

2. **Assess scope**
   - Number of encrypted systems
   - Data affected
   - Backup status

3. **Do NOT pay ransom** (initial position)
   - No guarantee of decryption
   - Funds criminal activity
   - May violate sanctions

4. **Check for decryptors**
   - NoMoreRansom.org
   - Security vendor tools
   - Ransomware identification

5. **Engage stakeholders**
   - Legal team
   - Law enforcement (FBI IC3)
   - Cyber insurance
   - PR team

### Recovery Decision Tree
```
Can restore from backup?
├── Yes → Restore from clean backup
└── No
    ├── Decryptor available?
    │   ├── Yes → Use decryptor
    │   └── No
    │       └── Ransom payment?
    │           ├── Last resort only
    │           └── Requires executive approval
```

## Communication Templates

### Internal Communication
```
Subject: Security Incident - [P1/P2/P3/P4]

Summary: [Brief description]
Impact: [Affected systems/data]
Status: [Contained/Under Investigation/Resolved]
Actions Required: [What users should do]
Contact: [IR team contact]
```

### External Communication
```
Subject: Security Incident Notification

[Company] has identified a security incident involving [description].

Actions taken:
- [Containment measures]
- [Investigation status]
- [Recovery steps]

Impact:
- [What data/systems affected]
- [Customer impact]

Next steps:
- [What we're doing]
- [What customers should do]

Contact: security@company.com
```

## Severity Definitions

| Level | Definition | Response Time | Escalation |
|-------|------------|---------------|------------|
| P1 | Active breach, data loss | 15 minutes | CISO, CEO |
| P2 | Malware outbreak, system compromise | 1 hour | Security Director |
| P3 | Suspicious activity, attempted breach | 4 hours | IR Team Lead |
| P4 | Policy violation, false positive | 24 hours | Analyst |

---

**Remember**: Document everything, preserve evidence, communicate clearly
