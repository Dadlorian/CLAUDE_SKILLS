# ACL Design Reference

## Access Control List Fundamentals

### ACL Types Overview

| Type | Use Case | Processing | Performance |
|------|----------|-----------|-------------|
| Standard | Source IP filtering | Slower (linear search) | Lower |
| Extended | Protocol/port filtering | Moderate | Moderate |
| Named | Reusable, organized | Moderate | Moderate |
| Dynamic | Temporary access | High overhead | Lower |
| Reflexive | Stateful filtering | High overhead | Lower |
| Time-based | Schedule-based rules | Very high overhead | Lower |

### ACL Processing Order

1. **Packet arrives at interface**
2. **Look up inbound ACL** (if configured)
3. **Verify protocol-specific rules** (TCP/UDP/ICMP)
4. **Implicit deny** (if no match found)
5. **Route lookup** (if permitted)
6. **Look up outbound ACL** (if configured)
7. **Forward or drop** packet

## Standard ACLs (1-99, 1300-1999)

### Purpose
- Filter based on source IP address only
- No protocol or port information
- Simple, fast filtering

### Syntax
```
access-list [number] [permit|deny] [source] [wildcard]
access-list 10 permit 10.1.1.0 0.0.0.255
access-list 10 deny 10.1.1.5 0.0.0.0
access-list 10 permit any
```

### Wildcard Mask Reference

| Wildcard | Network | CIDR | Hosts |
|----------|---------|------|-------|
| 0.0.0.0 | /32 | Single host | 1 |
| 0.0.0.255 | /24 | Class C subnet | 256 |
| 0.0.255.255 | /16 | Class B subnet | 65,536 |
| 0.255.255.255 | /8 | Class A subnet | 16.7M |
| 255.255.255.255 | /0 | Any | All IPs |

### Common Patterns

```
! Permit all traffic from specific subnet
access-list 10 permit 10.0.0.0 0.0.255.255

! Permit all except one host
access-list 10 permit 10.0.0.0 0.0.0.255
access-list 10 deny 10.0.0.50 0.0.0.0
access-list 10 permit any

! Permit only specific hosts
access-list 10 permit 10.1.1.1 0.0.0.0
access-list 10 permit 10.1.1.2 0.0.0.0
access-list 10 permit 10.1.1.3 0.0.0.0
```

## Extended ACLs (100-199, 2000-2699)

### Purpose
- Filter by source, destination, protocol, port
- Application-level filtering
- Complex traffic control

### Syntax
```
access-list [number] [permit|deny] [protocol]
  [source] [source-wildcard] [destination] [dest-wildcard]
  [operator port]
```

### Operators
```
eq = equal
ne = not equal
gt = greater than
lt = less than
range = range (e.g., 1024 1534)
```

### Protocol Numbers Reference

| Protocol | Number | Common |
|----------|--------|--------|
| ICMP | 1 | Ping, traceroute |
| TCP | 6 | HTTP, HTTPS, SSH, FTP |
| UDP | 17 | DNS, DHCP, NTP, SNMP |
| GRE | 47 | VPN tunnels |
| ESP | 50 | IPsec |
| AH | 51 | IPsec authentication |
| OSPF | 89 | Routing protocol |
| PIM | 103 | Multicast |
| EIGRP | 88 | Routing protocol |

### Port Numbers Reference

| Service | Port | Protocol | Common |
|---------|------|----------|--------|
| SSH | 22 | TCP | Secure shell |
| TELNET | 23 | TCP | Unencrypted (avoid) |
| SMTP | 25 | TCP | Email submission |
| DNS | 53 | TCP/UDP | Name resolution |
| HTTP | 80 | TCP | Web |
| POP3 | 110 | TCP | Email retrieval |
| IMAP | 143 | TCP | Email retrieval |
| HTTPS | 443 | TCP | Secure web |
| SYSLOG | 514 | UDP | Logging |
| SNMP | 161 | UDP | Management |
| SNMPTRAP | 162 | UDP | Management alerts |
| BGP | 179 | TCP | Routing |
| LDAP | 389 | TCP/UDP | Authentication |
| HTTPS | 443 | TCP | Secure web |
| MySQL | 3306 | TCP | Database |
| RDP | 3389 | TCP/UDP | Remote desktop |
| HTTPS Alt | 8443 | TCP | Alternative HTTPS |

### Common Extended ACL Patterns

```
! Allow web traffic
access-list 101 permit tcp any any eq 80
access-list 101 permit tcp any any eq 443

! Allow DNS queries and responses
access-list 101 permit udp any any eq 53
access-list 101 permit tcp any any eq 53

! Allow SSH from management network
access-list 101 permit tcp 10.1.50.0 0.0.0.255 any eq 22

! Allow database access from specific servers
access-list 101 permit tcp 10.1.10.0 0.0.0.255 10.1.20.5 eq 3306

! Deny specific host, allow subnet
access-list 101 deny tcp host 10.1.1.100 any
access-list 101 permit tcp 10.1.1.0 0.0.0.255 any

! High port range for client connections
access-list 101 permit tcp any any range 49152 65535
```

## Named ACLs

### Syntax
```
ip access-list standard [name]
 [line-number] permit|deny source wildcard

ip access-list extended [name]
 [line-number] permit|deny protocol source-spec dest-spec
```

### Example: Standard Named ACL
```
ip access-list standard INTERNAL_NETWORKS
 10 permit 10.0.0.0 0.255.255.255
 20 permit 172.16.0.0 0.15.255.255
 30 permit 192.168.0.0 0.0.255.255

interface Ethernet0
 ip access-group INTERNAL_NETWORKS in
```

### Example: Extended Named ACL
```
ip access-list extended ALLOW_WEB_SERVERS
 10 permit tcp 10.1.1.0 0.0.0.255 10.1.10.0 0.0.0.255 eq 80
 20 permit tcp 10.1.1.0 0.0.0.255 10.1.10.0 0.0.0.255 eq 443
 30 permit icmp 10.1.1.0 0.0.0.255 10.1.10.0 0.0.0.255
 40 deny ip any any
```

## IPv6 ACLs

### Syntax
```
ipv6 access-list [name]
 [line-number] permit|deny [protocol]
  [source/prefix-length] [destination/prefix-length]
  [operator port]
```

### Example
```
ipv6 access-list ALLOW_IPV6_WEB
 10 permit tcp 2001:db8:1::/48 any eq 80
 20 permit tcp 2001:db8:1::/48 any eq 443
 30 permit icmp 2001:db8:1::/48 any
 40 deny ipv6 any any

interface GigabitEthernet0/0
 ipv6 traffic-filter ALLOW_IPV6_WEB in
```

## Object Groups

### Network Object Groups
```
object-group network INTERNAL_NETWORKS
 network-object 10.0.0.0 255.0.0.0
 network-object 172.16.0.0 255.240.0.0
 network-object 192.168.0.0 255.255.0.0

access-list 101 permit ip object-group INTERNAL_NETWORKS object-group INTERNAL_NETWORKS
```

### Service Object Groups
```
object-group service WEB_SERVICES tcp
 port-object eq 80
 port-object eq 443
 port-object eq 8080
 port-object eq 8443

object-group service DNS_SERVICES udp
 port-object eq 53

access-list 101 permit tcp any any object-group WEB_SERVICES
access-list 101 permit udp any any object-group DNS_SERVICES
```

### Protocol Object Groups
```
object-group protocol SECURE_PROTOCOLS
 protocol-object tcp
 protocol-object udp

object-group protocol VPN_PROTOCOLS
 protocol-object esp
 protocol-object gre
 protocol-object 50
 protocol-object 51
```

## Dynamic ACLs (Lock-and-Key)

### Use Cases
- Temporary access based on authentication
- Time-limited access grants
- Dynamic network access control

### Configuration

```
! Define dynamic ACL
ip access-list extended DYNAMIC_ACCESS
 10 permit ip 10.1.1.0 0.0.0.255 10.1.10.0 0.0.0.255
 20 dynamic TEMP_ACCESS
  timeout 60
  permit tcp 10.1.1.0 0.0.0.255 10.1.20.0 0.0.0.255 eq 3306

! Apply to interface
interface GigabitEthernet0/0
 ip access-group DYNAMIC_ACCESS in

! Authentication triggers creation of temporary entry
access-list 100 permit tcp any any eq 22
match access-list 100
set access-list 900 permit
```

## Reflexive ACLs

### Purpose
- Stateful filtering for reply traffic
- Automatic return traffic permission

### Configuration

```
ip access-list extended OUTBOUND
 permit tcp 10.1.1.0 0.0.0.255 any reflect TCP_CONNECTIONS
 permit udp 10.1.1.0 0.0.0.255 any reflect UDP_CONNECTIONS

ip access-list extended INBOUND
 evaluate TCP_CONNECTIONS
 evaluate UDP_CONNECTIONS
 deny ip any any

interface GigabitEthernet0/0
 ip access-group INBOUND in
 ip access-group OUTBOUND out
```

## ACL Optimization Techniques

### 1. Grouping Related Rules
```
! Group by service
access-list 101 permit tcp any any eq 80
access-list 101 permit tcp any any eq 443
access-list 101 permit tcp any any eq 8080

! Instead of scattered throughout list
```

### 2. Consolidating Subnets
```
! Before
access-list 101 permit ip 10.1.1.0 255.255.255.0 any
access-list 101 permit ip 10.1.2.0 255.255.255.0 any
access-list 101 permit ip 10.1.3.0 255.255.255.0 any

! After (supernet)
access-list 101 permit ip 10.1.0.0 255.255.0.0 any
```

### 3. Using Object Groups
```
! Reduces number of ACL entries
! Simplifies modifications
! Improves readability
```

### 4. Ordering Optimization
```
! Most frequently matched first
! Specific rules before general
! Deny rules that short-circuit
! Default deny at end
```

## Troubleshooting and Verification

### Verify Commands
```
show access-lists
show access-lists [number|name]
show ip access-lists
show ipv6 access-lists
show running-config | include access-list
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Traffic blocked unexpectedly | Implicit deny | Add explicit permit |
| Reverse traffic blocked | No reflexive ACL | Add established keyword or reflexive |
| Performance degradation | Too many rules | Consolidate, use object groups |
| Port conflicts | Overlapping ranges | Use specific port numbers |
| IPv4/IPv6 mix | Wrong ACL type | Create separate IPv6 ACL |

### Debugging

```
! Enable ACL logging
access-list 101 permit ip 10.1.1.0 0.0.0.255 any log

! View denied traffic
show access-lists | include deny

! Monitor in real-time
debug ip packet access-list 101

! Verify interface application
show ip interface GigabitEthernet0/0 | include access list
```
