# Incident Response Runbook

## DDoS Attack Response

### Detection
- Threshold: Inbound > 500 Mbps OR 10x baseline
- Indicators: High packet rate, volumetric increase, single target
- Detection time: < 5 minutes

### Response
1. **Alert (T+0-5 min)**
   - Alert security team
   - Validate DDoS (not ISP issue)
   - Contact incident commander

2. **Mitigation (T+5-15 min)**
   - Activate DDoS mitigation service
   - Rate limit at edge
   - Blackhole attack traffic if needed
   - Notify upstream provider

3. **Investigation (T+15-60 min)**
   - Analyze attack patterns
   - Identify attack type
   - Determine attack source
   - Review impact

4. **Recovery (T+60+ min)**
   - Monitor mitigation effectiveness
   - Adjust rules as needed
   - Restore services gradually
   - Document findings

### Escalation
- DDoS < 1 Gbps: Team lead
- DDoS 1-10 Gbps: Manager + Team lead
- DDoS > 10 Gbps: Executive + Team lead

---

## Malware Detection Response

### Detection
- EDR alert: Suspicious behavior detected
- Indicators: Ransomware pattern, privilege escalation, lateral movement
- Detection time: < 10 minutes

### Response
1. **Isolation (T+0-10 min)**
   - Isolate affected host
   - Preserve memory dump
   - Don't shutdown
   - Revoke user sessions

2. **Analysis (T+10-30 min)**
   - Retrieve malware sample
   - Analyze behavior
   - Identify impact
   - Check for lateral movement

3. **Eradication (T+30-90 min)**
   - Clean malware
   - Patch vulnerability
   - Reset credentials
   - Update detection rules

4. **Recovery (T+90+ min)**
   - Rebuild system
   - Restore data
   - Monitor for re-infection
   - Post-incident review

### Escalation
- Single host: SOC team
- Multiple hosts: Incident commander + SOC
- Ransomware: Executive + Legal + Incident commander

---

## Network Intrusion Response

### Detection
- IPS/IDS alert: Exploit attempt detected
- Port scan detected
- Unusual traffic pattern
- Detection time: < 5 minutes

### Response
1. **Block (T+0-5 min)**
   - Block source IP at firewall
   - Alert network team
   - Review logs

2. **Investigation (T+5-30 min)**
   - Determine attack source
   - Identify target systems
   - Review affected data
   - Check for successful exploitation

3. **Remediation (T+30-120 min)**
   - Patch vulnerability if exploited
   - Update firewall rules
   - Enhanced monitoring
   - Notify affected users

4. **Follow-up**
   - Security assessment
   - Penetration testing
   - Update procedures
   - Training

### Escalation
- Reconnaissance: Log and monitor
- Intrusion attempt: Network team lead
- Successful intrusion: Incident commander
- Data breach: Executive + Legal

---

## Data Breach Response

### Detection
- Unauthorized data access
- Data exfiltration detected
- Sensitive data exposure
- Detection time: Varies

### Immediate Actions (T+0-1 hour)
1. Confirm breach
2. Preserve evidence
3. Identify affected data
4. Determine exposure scope
5. Notify incident commander
6. Notify legal/compliance

### Investigation (T+1-24 hours)
1. Determine attack vector
2. Identify compromised systems
3. Assess data exposure
4. Identify affected individuals
5. Determine breach timeline

### Notification (T+24-72 hours)
1. Legal review
2. Determine notification requirement
3. Notify affected individuals
4. Notify regulatory bodies (if required)
5. Public disclosure (if required)

### Recovery
1. Remediate vulnerability
2. Implement additional controls
3. Monitor for re-breach
4. Communication with stakeholders
5. Post-incident review

### Escalation
- Always escalate to executive level
- Involve legal immediately
- Involve compliance team
- Prepare for regulatory response

---

## Contact Information

### Internal Escalation
- SOC Lead: [Phone]
- Security Manager: [Phone]
- CISO: [Phone]
- Incident Commander: [Phone]

### External Resources
- Legal: [Contact]
- PR/Communications: [Contact]
- Cyber Insurance: [Contact]
- Law Enforcement: [Contact]

### Working Hours
- Weekday escalation: [Contact]
- After-hours escalation: [Contact]
- Executive on-call: [Phone]

---

## Documentation

After any incident:
1. Complete incident report
2. Timeline documentation
3. Root cause analysis
4. Improvement recommendations
5. Share lessons learned
6. Update this runbook

---

## Testing Schedule

- Quarterly: Tabletop exercises
- Annually: Full-scale drills
- Continuously: Targeted team drills
- Update runbook after each incident
