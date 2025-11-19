# Network Access Control (NAC) Implementation Guide

## NAC Fundamentals

### Purpose and Benefits

```
NAC Goals:
1. Enforce device compliance
2. Control network access
3. Ensure security baseline
4. Detect threats
5. Automate remediation

Benefits:
- Reduce breach risk (non-compliant devices blocked)
- Automate access control
- Improve visibility
- Enforce compliance
- Faster threat response
```

### NAC Deployment Phases

```
Phase 1: Monitoring (Read-only)
- Assess device compliance
- Identify non-compliant devices
- No enforcement
- Build baseline

Phase 2: Alerting
- Alert on non-compliance
- Notify users
- Track trends
- Plan enforcement

Phase 3: Enforcement (Active)
- Block non-compliant
- Quarantine VLAN
- Require remediation
- Force device updates
```

## Cisco ISE Deployment

### Lab Environment Setup

```
ISE Architecture:
┌──────────────┐
│  ISE (Policy │
│  Admin Node) │
└──────┬───────┘
       │
    ┌──┴──────┐
    │ Monitor  │ (optional)
    └──────────┘

PAD (Policy Administration Device):
- Policy rules
- User groups
- Device profiles
- Authentication policies

OP (Operational Node):
- Process authentications
- Lookup user/device info
- Enforce policies

MNT (Monitoring Node):
- Collect logs
- Analytics
- Reports
```

### ISE Deployment Steps

```
Step 1: Install ISE (7.1+)

Requirements:
- VM or appliance
- 4 vCPU minimum
- 16 GB RAM
- 200 GB disk
- Network: 2 NICs (management, data)

Post-Installation:
1. Set management IP
2. Set DNS/NTP
3. Configure certificates
4. Register with AD (optional)
5. Configure backup

Step 2: Configure Authentication Sources

Active Directory:
ISE → Administration → Identity Management → Active Directory
- Add AD domain
- Service account credentials
- Test connection

RADIUS:
ISE → Administration → Identity Management → External RADIUS
- Add RADIUS server
- Shared secret
- NAS source filter (optional)

Local Users:
ISE → Administration → User & Device Provisioning → Users
- Username: [AD user or local]
- Password: [Set or use AD]
- Group: [Assign to role group]

Step 3: Configure Network Devices

Cisco Switch:
aaa server radius dynamic-author
 client 10.1.50.10 server-key MyISEKey123!
 server-key MyISEKey123!

Fortinet FortiGate:
config user radius
 edit ISE_RADIUS
  set server 10.1.50.10
  set secret MyISEKey123!
 next
end

Step 4: Create Compliance Policies

Policy Rule:
ISE → Policy → Network Access → Compliance
Rule Name: Windows-Compliance
Condition:
  Device Type = Windows
  OS Vendor = Microsoft
  OS Version >= 10.0

Required Posture:
- Windows Defender: Active
- Windows Firewall: Enabled
- Antivirus: Updated
- Patches: Current (30 days)

Remediation:
- Notify user: "Update required"
- Provide guidance: Link to KB
- Quarantine VLAN: 999
```

### ISE Authorization Policies

```
Create Authorization Rule:

Rule: Standard-User-Auth
Priority: 10
Condition:
  User in group: All_Employees
  Device Type: Windows
  Compliant: Yes

Authorization:
- VLAN: 10 (User VLAN)
- ACL: USER_ACCESS_ACL
- AUP: Company-AUP
- Session timeout: 8 hours

Rule: Non-Compliant-Device
Priority: 20
Condition:
  Device non-compliant: Yes

Authorization:
- VLAN: 999 (Quarantine)
- ACL: QUARANTINE_ACL (Internet only + ISE)
- Remediation portal access
- Session timeout: 2 hours

Rule: Guest-Access
Priority: 30
Condition:
  Authentication Method: Guest

Authorization:
- VLAN: 12 (Guest VLAN)
- ACL: GUEST_ACL (Internet only)
- Data Rate Limit: 5 Mbps
- Session timeout: 4 hours
```

## Device Compliance Assessment

### Windows Compliance

```
Check Requirements:
1. Windows Defender (Antivirus)
   - Status: Running
   - Signature date: < 7 days old
   - Real-time protection: Enabled

2. Windows Firewall
   - Domain profile: Enabled
   - Private profile: Enabled
   - Public profile: Enabled

3. Windows Update
   - Status: Up to date
   - Last check: < 7 days
   - Failed updates: 0

4. Encryption
   - BitLocker: Enabled (optional)
   - Disk encryption: Required for sensitive roles

ISE Configuration:
Agent: Cisco ISE Posture Agent
Deploy via:
- Group Policy (AD)
- Manual installation
- Intune

Verification:
- Agent runs on startup
- Checks compliance hourly
- Reports to ISE
- Remediation available
```

### macOS Compliance

```
Check Requirements:
1. Antivirus
   - Installed and running
   - Signatures current

2. Firewall
   - System Preferences → Security & Privacy → Firewall
   - Enabled

3. OS Updates
   - Security patches current
   - Automatic updates: On

4. Encryption
   - FileVault: Enabled

ISE Configuration:
Agent: Cisco ISE Agent for macOS
Install via:
- DMG installer (manual)
- Jamf (MDM)
- MacAdmins deployment

Verification:
- Agent startup item
- Checks compliance
- Reports to ISE
```

### Mobile Device Compliance

```
iOS/Android Requirements:
1. Screen lock
   - Required: Yes
   - Timeout: < 5 minutes

2. OS Version
   - iOS: > 16.0
   - Android: > 12.0

3. Apps
   - No jailbroken/rooted apps
   - App management enabled

4. VPN
   - Corporate VPN available
   - Not required for all

ISE + MDM Integration:
- Jamf Pro (Apple)
- Intune (Android/Apple)
- MobileIron (Android/Apple)

Setup:
ISE → Administration → System → Third Party → MDM
- Configure MDM endpoint
- Sync device status
- Automatic remediation
```

## Quarantine and Remediation

### Quarantine VLAN Setup

```
Configure Quarantine VLAN:

VLAN Creation:
vlan 999
 name QUARANTINE

Switch Configuration:
interface Vlan999
 ip address 10.1.99.1 255.255.255.0
 description Quarantine VLAN

Route to ISE:
ip route 10.1.50.0 255.255.255.0 10.1.99.1
 (if ISE on different network)

Firewall Rules:
Quarantine → ISE:
permit tcp 10.1.99.0/24 10.1.50.10 eq 443 (HTTPS)
permit tcp 10.1.99.0/24 10.1.50.10 eq 8009 (ISE portal)
permit udp 10.1.99.0/24 10.1.50.10 eq 53 (DNS)

Quarantine → Internet:
permit tcp 10.1.99.0/24 any eq 80 (HTTP - portal)
permit tcp 10.1.99.0/24 any eq 443 (HTTPS - portal)

Quarantine → Internal:
deny ip 10.1.99.0/24 10.1.0.0/16 (Block internal)

All other:
deny ip any any log
```

### Remediation Portal

```
ISE Posture Remediation Portal:

When device non-compliant:
1. User connects to network
2. ISE detects non-compliance
3. Browser redirected to portal
4. Portal shows:
   - Compliance requirements
   - Missing items (e.g., patch KB)
   - How to fix (step-by-step)
   - Download link (if available)

Examples:

Missing Patch:
"Windows Update KB12345 Required"
Download: [Link to Windows Update]
Status: Click to recheck
Bypass: (if admin permits)

Antivirus Outdated:
"Antivirus Signatures 7 days old"
Update: [Instructions]
Status: Click to recheck

Firewall Disabled:
"Windows Firewall Disabled"
Enable: [Instructions]
Status: Click to recheck

Custom Portal:
- Brand with company logo
- Friendly instructions
- Self-service remediation
- Phone support contact
```

## Network Access Control Policies

### Example Policies

```
Policy 1: Employee - Fully Compliant
Condition:
  User in: Employees
  Device: Windows/Mac
  Compliant: Yes

Authorization:
  VLAN: 10 (User VLAN)
  Bandwidth: Unlimited
  Timeout: 8 hours
  Access: Full internal network

Policy 2: Contractor - Limited Access
Condition:
  User in: Contractors
  Device: Windows/Mac
  Compliant: Yes

Authorization:
  VLAN: 11 (Contractor VLAN)
  Bandwidth: Limited
  Access: Specific servers only
  Timeout: 4 hours

Policy 3: Guest - Internet Only
Condition:
  Authentication: Guest/Walk-in

Authorization:
  VLAN: 12 (Guest VLAN)
  Bandwidth: Limited (5 Mbps)
  Access: Internet only
  Timeout: 4 hours

Policy 4: Device Non-Compliant
Condition:
  Compliant: No

Authorization:
  VLAN: 999 (Quarantine)
  Bandwidth: Limited (1 Mbps)
  Access: ISE portal only
  Timeout: 2 hours
  Action: Notify + Remediate

Policy 5: Admin Access
Condition:
  User: Network Admins
  Device: Approved admin workstation

Authorization:
  VLAN: 100 (Management VLAN)
  Bandwidth: Unlimited
  Access: All systems
  Timeout: 1 hour
  MFA: Required
```

## Reporting and Analytics

### Key Metrics

```
Monitor:
- Total connected devices
- Compliant vs non-compliant
- Top non-compliance reasons
- Authentication success rate
- Failed authentication attempts
- Quarantine duration
- Time to remediation

Reports:
ISE → Operations → Reports & Monitoring

Standard Reports:
- Compliance Summary
- Device Inventory
- Non-Compliant Devices
- Authentication Summary
- Failed Logins
- Session Summary
```

## Troubleshooting

### Common Issues

```
Issue 1: Agent Not Reporting
Diagnosis:
1. Verify ISE connectivity
2. Check agent running
3. Review agent logs
4. Check firewall rules

Solution:
- Restart agent
- Verify ISE IP
- Check network connectivity
- Update agent

Issue 2: Compliance Check Not Running
Diagnosis:
1. Check agent status
2. Verify policies exist
3. Check user group
4. Review logs

Solution:
- Verify rule matches
- Check user group
- Re-authenticate
- Restart agent

Issue 3: Portal Not Loading
Diagnosis:
1. Check network connectivity
2. Verify ISE accessible
3. Check DNS resolution
4. Review firewall rules

Solution:
- Verify quarantine VLAN
- Check ISE portal service
- Verify DNS working
- Check firewall rules
```

## Best Practices

### Deployment Strategy

```
Phased Approach:
Month 1: Pilot with IT team
Month 2: Monitoring mode (read-only)
Month 3: Department pilots
Month 4: Soft enforcement (warning)
Month 5: Enforcement (blocking)
Month 6+: Optimization
```

### Maintenance

```
Daily:
- Monitor device compliance
- Check quarantine count
- Review failed auth attempts

Weekly:
- Compliance trending
- Top issue analysis
- User support tickets

Monthly:
- Full compliance report
- Policy effectiveness review
- Remediation metrics
- Update requirements

Quarterly:
- Policy review
- Technology update
- Security assessment
- Training refresher
```
