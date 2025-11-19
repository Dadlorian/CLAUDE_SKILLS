# ACL Configuration Guide

## Planning ACL Strategy

### Step 1: Requirements Definition

```
Determine ACL Scope:
- Which interfaces need ACLs?
- Inbound or outbound filtering?
- Which traffic to permit/deny?
- Performance requirements?
- Logging requirements?
- Policy documentation?

Traffic Analysis:
- Identify allowed services
- Identify blocked services
- Determine source/destination networks
- Document business justification
- Plan for growth/changes
```

### Step 2: Design Approach

```
Choose Strategy:

Strategy 1: Standard ACLs (IP-based only)
- Simple filtering by source IP
- Limited functionality
- Fast processing
- Use for: Basic filtering, NAS access

Strategy 2: Extended ACLs (full packet inspection)
- Protocol, port, source, destination
- Complex filtering capability
- Moderate processing
- Use for: Most filtering requirements

Strategy 3: Named ACLs (organized, reusable)
- Organized with descriptive names
- Easy to modify
- Scalable
- Use for: Production networks (recommended)

Recommendation: Use Named ACLs for all new deployments
```

## Basic ACL Creation

### Standard Named ACL

```
Create ACL (Cisco):
ip access-list standard INTERNAL_NETWORKS
 10 permit 10.1.0.0 0.0.255.255
 20 permit 172.16.0.0 0.15.255.255
 30 permit 192.168.0.0 0.0.255.255
 40 deny any

Apply to Interface:
interface Ethernet0
 ip access-group INTERNAL_NETWORKS in
 description WAN Link - Restrict to internal

Apply to Line (SSH):
line vty 0 4
 access-class INTERNAL_NETWORKS in

Verify:
show access-lists
show access-lists INTERNAL_NETWORKS
show ip interface Ethernet0 | include access list
```

### Extended Named ACL

```
Create ACL (Cisco):
ip access-list extended ALLOW_WEB
 10 permit tcp any any eq 80
 20 permit tcp any any eq 443
 30 permit tcp any any eq 8080
 40 deny tcp any any log

Alternative with object groups:
object-group network WEB_CLIENTS
 network-object 10.1.0.0 255.255.0.0
 network-object 172.16.0.0 255.240.0.0

object-group service WEB_SERVICES tcp
 port-object eq 80
 port-object eq 443
 port-object eq 8080

ip access-list extended ALLOW_WEB_OG
 10 permit tcp object-group WEB_CLIENTS any object-group WEB_SERVICES
 20 deny tcp any any log
 30 permit ip any any

Apply to Interface:
interface FastEthernet0/0
 ip access-group ALLOW_WEB in
 description Allow Web Traffic

Verify:
show access-lists ALLOW_WEB
show ip interface FastEthernet0/0
```

## Advanced ACL Features

### Using Object Groups

```
Benefits:
- Reduce ACL size
- Easier modifications
- Reusable across ACLs
- Better documentation

Network Object Group Example:
object-group network DMZ_SERVERS
 description DMZ Server Pool
 network-object host 10.1.10.5
 network-object host 10.1.10.6
 network-object host 10.1.10.7
 network-object host 10.1.10.8

Service Object Group Example:
object-group service CRITICAL_APPS tcp
 description Critical applications
 port-object eq 443
 port-object eq 8443
 port-object eq 8080
 port-object range 9000 9100

Protocol Object Group Example:
object-group protocol SECURE_PROTOCOLS
 description Secure protocols
 protocol-object tcp
 protocol-object udp

ACL Using Object Groups:
ip access-list extended WEB_ACL
 10 permit tcp any object-group DMZ_SERVERS object-group CRITICAL_APPS
 20 permit tcp object-group DMZ_SERVERS any eq 53
 30 deny ip any any log
```

### Logging and Monitoring

```
Enable Logging:
ip access-list extended ACL_WITH_LOGGING
 10 permit tcp any host 10.1.10.5 eq 443 log
 20 permit tcp any host 10.1.10.6 eq 443 log
 30 deny tcp any any log
 40 permit ip any any

Centralize Logs:
ip syslog-server 10.1.50.10

Adjust Log Rates:
logging rate-limit 100000 10 000000
logging rate-limit console 100 warnings

Clear Counters:
clear access-list counters ACL_NAME

View Hit Counters:
show access-lists ACL_NAME

Example Output:
ACL_WITH_LOGGING (applied inbound on Eth0)
 10 permit tcp any host 10.1.10.5 eq 443 log (9234 match(es))
 20 permit tcp any host 10.1.10.6 eq 443 log (8121 match(es))
 30 deny tcp any any log (456 match(es))
 40 permit ip any any (12345678 match(es))
```

## Practical ACL Examples

### Example 1: Restrict SSH to Management Subnet

```
Problem: SSH should only be accessible from management network

Solution:
ip access-list standard SSH_MANAGEMENT
 10 permit 10.1.100.0 0.0.0.255
 20 deny any

line vty 0 4
 access-class SSH_MANAGEMENT in
 logging

line vty 5 15
 access-class SSH_MANAGEMENT in
 logging

Verification:
- SSH from 10.1.100.x: Success
- SSH from other IP: Denied, logged

Testing:
ssh -v 10.1.0.5  (from 10.1.100.10) - SUCCESS
ssh -v 10.1.0.5  (from 10.1.10.5)  - DENIED
```

### Example 2: Allow Web Access, Restrict Database

```
Problem: Allow HTTP/HTTPS but block direct database access

Solution:
object-group service WEB_SERVICES tcp
 port-object eq 80
 port-object eq 443

object-group service DATABASE_SERVICES tcp
 port-object eq 3306  (MySQL)
 port-object eq 5432  (PostgreSQL)
 port-object eq 1433  (SQL Server)

ip access-list extended USER_ACL
 10 permit tcp any any object-group WEB_SERVICES
 20 permit tcp any any eq 53      (DNS)
 30 permit tcp any any eq 123     (NTP)
 40 deny tcp any any object-group DATABASE_SERVICES log
 50 permit ip any any

interface FastEthernet0/0
 ip access-group USER_ACL in
 description User traffic control

Result:
- Web traffic: Allowed
- DNS/NTP: Allowed
- Database: Blocked and logged
- Other: Allowed
```

### Example 3: DMZ to Internal Access Control

```
Problem: DMZ web servers can only access specific internal databases

Solution:
object-group network DMZ_WEB_SERVERS
 network-object 10.1.10.5
 network-object 10.1.10.6

object-group network INTERNAL_DB_SERVERS
 network-object 10.1.20.5
 network-object 10.1.20.6

ip access-list extended DMZ_TO_INTERNAL
 10 permit tcp object-group DMZ_WEB_SERVERS object-group INTERNAL_DB_SERVERS eq 3306
 20 permit tcp object-group DMZ_WEB_SERVERS 10.1.50.0 0.0.0.255 eq 53 (DNS)
 30 deny tcp object-group DMZ_WEB_SERVERS any log
 40 permit ip any any

interface Vlan20 (Internal VLAN)
 ip access-group DMZ_TO_INTERNAL in
 description Allow DMZ database queries

Result:
- DMZ → DB servers: Allowed on port 3306
- DMZ → Other internal: Blocked
- Other traffic: Allowed
```

## ACL Optimization

### Rule Ordering Best Practices

```
Rule Order Strategy:

1. Most Frequently Matched First
   - High-volume traffic rules
   - Reduces processing time

2. Specific Rules Before General Rules
   - Specific source/dest first
   - General catch-all last

3. Deny Rules Before Allow Rules (optional)
   - Can short-circuit evaluation
   - Depends on rule design

4. Group Related Rules
   - Similar services together
   - Improve cache efficiency

Example Order:
! High-volume, general traffic
10 permit tcp any any eq 443      (HTTPS - most common)
20 permit tcp any any eq 80       (HTTP)

! Medium-volume, specific
30 permit tcp 10.1.100.0 0.0.0.255 any eq 22
40 permit tcp 10.1.100.0 0.0.0.255 any eq 3389

! Low-volume, deny
50 deny tcp any any eq 1433 log
60 deny tcp any any eq 3306 log

! Final catch-all
70 permit ip any any
```

### ACL Consolidation

```
Before Consolidation:
access-list 101 permit tcp any 10.1.10.0 255.255.255.0 eq 80
access-list 101 permit tcp any 10.1.10.0 255.255.255.0 eq 443
access-list 101 permit tcp any 10.1.10.0 255.255.255.0 eq 8080
access-list 101 permit tcp any 10.1.10.0 255.255.255.0 eq 8443
access-list 101 permit tcp any 10.1.11.0 255.255.255.0 eq 80
access-list 101 permit tcp any 10.1.11.0 255.255.255.0 eq 443

After Consolidation (using object groups):
object-group network WEB_SUBNETS
 network-object 10.1.10.0 255.255.255.0
 network-object 10.1.11.0 255.255.255.0

object-group service WEB_PORTS tcp
 port-object eq 80
 port-object eq 443
 port-object eq 8080
 port-object eq 8443

ip access-list extended WEB_RULES
 10 permit tcp any object-group WEB_SUBNETS object-group WEB_PORTS

Result: Reduced from 6 lines to 1 line
Benefits: Easier maintenance, faster updates
```

## IPv6 ACLs

### IPv6 ACL Configuration

```
Create IPv6 ACL:
ipv6 access-list ALLOW_IPV6_WEB
 10 permit tcp 2001:db8:1::/48 any eq 80
 20 permit tcp 2001:db8:1::/48 any eq 443
 30 permit icmp 2001:db8:1::/48 any
 40 deny ipv6 any any

Apply to Interface:
interface GigabitEthernet0/0
 ipv6 traffic-filter ALLOW_IPV6_WEB in
 description IPv6 WEB TRAFFIC FILTER

IPv6 Address Notation:
2001:db8::/32 - CIDR notation
2001:db8::1 - Host address
::/0 - Any (0:0:0:0:0:0:0:0/0)
::1 - Loopback
fe80::/10 - Link-local

Verify:
show ipv6 access-lists
show ipv6 interface GigabitEthernet0/0
```

## Troubleshooting ACLs

### Diagnosis Steps

```
Step 1: Verify ACL is Applied
show ip interface Ethernet0 | include access list

Step 2: Review ACL Rules
show access-lists ACL_NAME

Step 3: Check Hit Counters
show access-lists ACL_NAME
  (look for hit counts on each rule)

Step 4: Enable Debug Logging
ip access-list extended DEBUG_ACL
 99 permit ip any any log

access-list 100 permit ip any any log

Step 5: Analyze Logs
show logging | include DENIED
show logging | include permit

Step 6: Test with Specific Traffic
ping 10.1.1.1  (from source of interest)
telnet 10.1.1.1 80  (test specific port)
```

### Common Issues and Solutions

```
Issue 1: Legitimate traffic blocked
Symptom: Users complain services unavailable
Cause: Incorrect rule logic
Fix:
1. Verify business requirement
2. Add specific permit rule
3. Test before deploying
4. Document justification

Issue 2: Unexpected traffic allowed
Symptom: Unwanted traffic passing through
Cause: Overly permissive rule or bad ordering
Fix:
1. Review rule ordering
2. Add deny rules
3. Use logging to identify
4. Tighten rules

Issue 3: Performance degradation
Symptom: Slow traffic through ACL
Cause: ACL too large or poorly ordered
Fix:
1. Reduce rule count (consolidation)
2. Optimize rule order
3. Use object groups
4. Split into multiple ACLs

Issue 4: Rule not matching expected traffic
Symptom: Traffic not caught by rule
Cause: Incorrect source/port/protocol specification
Fix:
1. Verify address ranges
2. Check port numbers
3. Verify protocol
4. Use logging to validate
```

## Maintenance and Management

### Regular Tasks

```
Daily:
- Monitor denied traffic
- Check for unusual patterns

Weekly:
- Review new rules added
- Check rule hit counts
- Identify unused rules

Monthly:
- Remove unused rules
- Consolidate rules
- Review for optimization
- Update documentation

Quarterly:
- Comprehensive ACL audit
- Performance review
- Security assessment
- Compliance verification

Annually:
- Full redesign review
- Technology assessment
- Compliance validation
- Complete documentation update
```

### Documentation Template

```
ACL Name: [Name]
Purpose: [Business justification]
Applied To: [Interface/Line]
Direction: [Inbound/Outbound]
Created: [Date]
Last Modified: [Date]
Owner: [Team/Person]

Rules:
Rule #10: [Description]
  - Permit/Deny: [Type]
  - Source: [IP/Network]
  - Destination: [IP/Network]
  - Protocol: [Protocol]
  - Port: [Port/Range]
  - Logging: [Yes/No]

Dependencies:
- Used by: [System/Policy]
- Related ACLs: [Other ACLs]
- Change Control: [Process]

Review Schedule:
- Last Review: [Date]
- Next Review: [Date + 90 days]
```
