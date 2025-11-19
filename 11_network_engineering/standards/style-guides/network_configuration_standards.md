# Network Configuration Standards

## Overview

This document establishes comprehensive configuration standards for network devices across multi-vendor environments including Cisco IOS/IOS-XE/NX-OS, Juniper JunOS, Arista EOS, and other network operating systems. Consistent configuration practices improve operational efficiency, reduce errors, and facilitate automation.

**Key References:**
- Cisco IOS Configuration Fundamentals Configuration Guide
- Juniper Networks JunOS Configuration Guide
- Arista EOS Configuration Fundamentals
- NIST SP 800-41 Rev. 1: Guidelines on Firewalls and Firewall Policy
- CIS Benchmark for Cisco IOS
- NSA Router Security Configuration Guide

## Configuration Management Principles

### Core Principles

1. **Idempotency**: Configuration changes should produce the same result regardless of how many times applied
2. **Atomicity**: Related configuration changes should be applied as a single unit
3. **Reversibility**: All changes must have documented rollback procedures
4. **Auditability**: All configurations must include metadata (who, what, when, why)
5. **Minimal Privilege**: Apply principle of least privilege to all configurations
6. **Defense in Depth**: Layer security controls at multiple points

### Configuration Hierarchy

```
Configuration Structure:
├─ Global Configuration (device-wide settings)
│  ├─ Hostname and domain
│  ├─ Management access (SSH, HTTPS)
│  ├─ AAA configuration
│  ├─ Logging and SNMP
│  ├─ NTP and timezone
│  └─ DNS servers
│
├─ Interface Configuration (per-interface settings)
│  ├─ Layer 2 (switchport, VLANs)
│  ├─ Layer 3 (IP addressing, routing)
│  ├─ Physical (speed, duplex, media type)
│  ├─ Security (port-security, DHCP snooping)
│  └─ QoS (classification, policing, shaping)
│
├─ Routing Configuration
│  ├─ Static routes
│  ├─ Dynamic routing protocols (OSPF, BGP, EIGRP)
│  ├─ Route filtering and manipulation
│  └─ Redistribution policies
│
└─ Security Configuration
   ├─ Access control lists (ACLs)
   ├─ Prefix lists and route maps
   ├─ Control plane policing
   └─ Management plane security
```

## Device Naming Conventions

### Hostname Standards

**Format Structure:**
```
<SITE>-<ROLE>-<FUNCTION>-<NUMBER>

Components:
- SITE: 2-4 character site code (NYC, LON, SIN)
- ROLE: Device role (CORE, DIST, ACCESS, WAN, FW)
- FUNCTION: Specific function (SW, RTR, ASA, FTD)
- NUMBER: Sequential number (01-99)

Examples:
NYC-CORE-SW-01      (New York core switch #1)
NYC-CORE-SW-02      (New York core switch #2)
NYC-DIST-SW-01      (New York distribution switch #1)
NYC-ACCESS-SW-15    (New York access switch #15)
LON-WAN-RTR-01      (London WAN router #1)
SIN-FW-ASA-01       (Singapore firewall #1)
```

**Site Code Registry:**
```
North America:
- NYC: New York City Data Center
- LAX: Los Angeles Data Center
- CHI: Chicago Data Center
- TOR: Toronto Data Center

Europe:
- LON: London Data Center
- FRA: Frankfurt Data Center
- AMS: Amsterdam Data Center

Asia Pacific:
- SIN: Singapore Data Center
- TOK: Tokyo Data Center
- SYD: Sydney Data Center
```

**Role Definitions:**
```
CORE:       Core/backbone devices
DIST:       Distribution layer devices
ACCESS:     Access layer devices
WAN:        WAN edge routers
FW:         Firewalls/security appliances
LB:         Load balancers
INET:       Internet edge devices
MGMT:       Out-of-band management devices
```

### Domain Configuration

**DNS Domain Standards:**
```
Production Devices:  company.local
Management Network:  mgmt.company.local
Lab/Test Devices:    lab.company.local
DMZ Devices:         dmz.company.local

Example FQDNs:
nyc-core-sw-01.company.local
nyc-core-sw-01.mgmt.company.local  (OOB management interface)
```

## Interface Naming and Description Standards

### Interface Description Format

**Format Template:**
```
<CONNECTION_TYPE> | <REMOTE_DEVICE> | <REMOTE_INTERFACE> | <CIRCUIT_ID> | <PURPOSE>

Examples:
description TRUNK | NYC-DIST-SW-01 | Gi1/0/1 | Layer2 Uplink
description ACCESS | User VLAN 100 | Building A Floor 3
description P2P | NYC-WAN-RTR-01 | Gi0/0/0 | MPLS-12345 | Primary WAN
description MGMT | OOB Management | VLAN 10
description UNUSED | Disabled per security policy
```

### Cisco IOS/IOS-XE Interface Configuration

**Physical Interface Template:**
```
interface GigabitEthernet1/0/1
  description TRUNK | NYC-DIST-SW-01 | Gi1/0/1 | Layer2 Uplink
  switchport trunk encapsulation dot1q
  switchport mode trunk
  switchport trunk native vlan 999
  switchport trunk allowed vlan 10,100,200,300
  spanning-tree portfast trunk
  spanning-tree bpduguard enable
  no shutdown
  !
  ! Interface notes:
  ! Last modified: 2024-01-15 by NetOps
  ! Change request: CR-2024-0115
```

**Access Port Template:**
```
interface GigabitEthernet1/0/24
  description ACCESS | User Workstation | VLAN 100
  switchport mode access
  switchport access vlan 100
  switchport voice vlan 200
  spanning-tree portfast
  spanning-tree bpduguard enable
  storm-control broadcast level 10.00
  storm-control multicast level 10.00
  !
  ! Security features
  switchport port-security
  switchport port-security maximum 2
  switchport port-security violation restrict
  switchport port-security aging time 5
  switchport port-security aging type inactivity
  !
  ! QoS trust boundary
  mls qos trust cos
  no shutdown
```

**Routed Interface Template:**
```
interface GigabitEthernet0/0/0
  description P2P | NYC-WAN-RTR-02 | Gi0/0/0 | OSPF Area 0
  ip address 10.128.0.1 255.255.255.252
  no ip redirects
  no ip unreachables
  no ip proxy-arp
  ip mtu 1500
  load-interval 30
  !
  ! Routing protocol configuration
  ip ospf 1 area 0
  ip ospf network point-to-point
  ip ospf hello-interval 1
  ip ospf dead-interval 3
  !
  ! QoS policy
  service-policy output WAN-QOS-POLICY
  no shutdown
```

**Loopback Interface Template:**
```
interface Loopback0
  description MGMT | Router ID for OSPF/BGP
  ip address 10.129.0.1 255.255.255.255
  !
  ! Used for:
  ! - OSPF Router ID
  ! - BGP Router ID
  ! - Management/SSH destination
  ! - SNMP source
```

### Cisco NX-OS Interface Configuration

**vPC Configuration Template:**
```
! vPC Domain Configuration
feature vpc
feature lacp

vpc domain 1
  role priority 10
  peer-keepalive destination 10.1.10.2 source 10.1.10.1 vrf management
  peer-gateway
  layer3 peer-router
  auto-recovery
  delay restore 150
  ip arp synchronize

! vPC Peer-Link
interface port-channel1
  description vPC Peer-Link to NYC-CORE-SW-02
  switchport mode trunk
  switchport trunk allowed vlan 1-4094
  spanning-tree port type network
  vpc peer-link

interface Ethernet1/1-2
  description vPC Peer-Link Member
  switchport mode trunk
  switchport trunk allowed vlan 1-4094
  channel-group 1 mode active
  no shutdown

! vPC to Access Switch
interface port-channel10
  description vPC to NYC-ACCESS-SW-01
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200,300
  vpc 10

interface Ethernet1/10-11
  description vPC Member to NYC-ACCESS-SW-01
  switchport mode trunk
  switchport trunk allowed vlan 10,100,200,300
  channel-group 10 mode active
  no shutdown
```

### Juniper JunOS Interface Configuration

**Interface Configuration Template:**
```
interfaces {
    ge-0/0/0 {
        description "TRUNK | NYC-DIST-SW-01 | ge-0/0/1 | Layer2 Uplink";
        unit 0 {
            family ethernet-switching {
                interface-mode trunk;
                vlan {
                    members [ vlan-100 vlan-200 vlan-300 ];
                }
                native-vlan-id 999;
            }
        }
    }

    ge-0/0/24 {
        description "ACCESS | User Workstation | VLAN 100";
        unit 0 {
            family ethernet-switching {
                interface-mode access;
                vlan {
                    members vlan-100;
                }
                storm-control {
                    broadcast-level 10;
                    multicast-level 10;
                }
            }
        }
    }

    /* Routed Interface */
    ge-0/0/1 {
        description "P2P | NYC-WAN-RTR-02 | ge-0/0/1 | OSPF Area 0";
        unit 0 {
            family inet {
                address 10.128.0.1/30;
                mtu 1500;
            }
        }
    }

    /* Loopback Interface */
    lo0 {
        description "MGMT | Router ID for OSPF/BGP";
        unit 0 {
            family inet {
                address 10.129.0.1/32;
            }
        }
    }
}
```

### Arista EOS Interface Configuration

**Interface Configuration Template:**
```
interface Ethernet1
   description TRUNK | NYC-DIST-SW-01 | Ethernet1 | Layer2 Uplink
   switchport trunk encapsulation dot1q
   switchport mode trunk
   switchport trunk native vlan 999
   switchport trunk allowed vlan 10,100,200,300
   spanning-tree portfast
   spanning-tree bpduguard enable
   no shutdown
   !
   comment
   Last modified: 2024-01-15 by NetOps
   Change request: CR-2024-0115
   comment

interface Ethernet48
   description ACCESS | User Workstation | VLAN 100
   switchport access vlan 100
   switchport mode access
   spanning-tree portfast
   spanning-tree bpduguard enable
   storm-control broadcast level 10
   storm-control multicast level 10
   no shutdown

! MLAG Configuration
mlag configuration
   domain-id MLAG-DOMAIN-1
   local-interface Vlan4094
   peer-address 10.255.255.2
   peer-link Port-Channel1
   reload-delay mlag 300
   reload-delay non-mlag 330

interface Port-Channel1
   description MLAG Peer-Link to NYC-CORE-SW-02
   switchport mode trunk
   switchport trunk group mlagpeer

interface Ethernet49-50
   description MLAG Peer-Link Member
   channel-group 1 mode active
   no shutdown
```

## Configuration Header Standards

### Configuration Banner

**Cisco IOS/NX-OS Banner Template:**
```
banner motd ^
================================================================================
                        AUTHORIZED ACCESS ONLY
================================================================================

This system is the property of COMPANY NAME. Unauthorized access is prohibited.
All connections are monitored and recorded. By accessing this system, you
consent to monitoring. Disconnect immediately if you are not an authorized user.

Device Information:
- Hostname: NYC-CORE-SW-01
- Location: New York Data Center, Rack A12, U24
- Contact: Network Operations Center (NOC)
- Phone: +1-555-0100
- Email: noc@company.com

For emergencies, contact the 24/7 NOC at +1-555-0911

Last Configuration Change: 2024-01-15 14:30:00 EST
Change Request: CR-2024-0115

================================================================================
^
```

**Juniper JunOS Banner Template:**
```
system {
    login {
        message "\n\
================================================================================\n\
                        AUTHORIZED ACCESS ONLY\n\
================================================================================\n\
\n\
This system is the property of COMPANY NAME. Unauthorized access is prohibited.\n\
All connections are monitored and recorded. By accessing this system, you \n\
consent to monitoring. Disconnect immediately if you are not an authorized user.\n\
\n\
Device Information:\n\
- Hostname: NYC-CORE-RTR-01\n\
- Location: New York Data Center, Rack A12, U28\n\
- Contact: Network Operations Center (NOC)\n\
- Phone: +1-555-0100\n\
- Email: noc@company.com\n\
\n\
For emergencies, contact the 24/7 NOC at +1-555-0911\n\
\n\
Last Configuration Change: 2024-01-15 14:30:00 EST\n\
Change Request: CR-2024-0115\n\
\n\
================================================================================\n";
    }
}
```

### Configuration Comments

**Inline Comments Best Practices:**

Cisco IOS:
```
! ============================================================================
! Section: Global Configuration
! Purpose: Basic device settings and management access
! Author: NetOps Team
! Last Modified: 2024-01-15
! ============================================================================

hostname NYC-CORE-SW-01
!
! Domain configuration for DNS resolution
ip domain-name company.local
ip name-server 10.1.10.7 10.1.10.8
!
! ============================================================================
! Section: Management Access
! Purpose: Enable secure management protocols
! ============================================================================
!
! Disable insecure protocols
no ip http server
!
! Enable HTTPS for web management
ip http secure-server
ip http authentication local
!
! SSH Configuration (version 2 only for security)
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3
```

Juniper JunOS:
```
/*
 * ============================================================================
 * Section: System Configuration
 * Purpose: Basic device settings and management access
 * Author: NetOps Team
 * Last Modified: 2024-01-15
 * ============================================================================
 */

system {
    host-name NYC-CORE-RTR-01;
    domain-name company.local;

    /* Time and date configuration */
    time-zone America/New_York;

    /* NTP servers for time synchronization */
    ntp {
        server 10.1.10.5 prefer;
        server 10.1.10.6;
    }

    /* Name servers for DNS resolution */
    name-server {
        10.1.10.7;
        10.1.10.8;
    }
}
```

## AAA Configuration Standards

### TACACS+ Configuration (Preferred)

**Cisco IOS/IOS-XE Template:**
```
! ============================================================================
! AAA Configuration using TACACS+
! Primary: 10.1.10.20 (ISE-1)
! Secondary: 10.1.10.21 (ISE-2)
! ============================================================================

aaa new-model
!
! TACACS+ server configuration
tacacs server ISE-1
  address ipv4 10.1.10.20
  key 7 <encrypted_key>
  timeout 5
  single-connection

tacacs server ISE-2
  address ipv4 10.1.10.21
  key 7 <encrypted_key>
  timeout 5
  single-connection

! AAA server groups
aaa group server tacacs+ ISE-GROUP
  server name ISE-1
  server name ISE-2
  ip tacacs source-interface Loopback0

! Authentication methods
aaa authentication login default group ISE-GROUP local
aaa authentication enable default group ISE-GROUP enable
aaa authentication dot1x default group ISE-GROUP

! Authorization methods
aaa authorization exec default group ISE-GROUP local
aaa authorization commands 1 default group ISE-GROUP local
aaa authorization commands 15 default group ISE-GROUP local
aaa authorization network default group ISE-GROUP

! Accounting
aaa accounting exec default start-stop group ISE-GROUP
aaa accounting commands 1 default start-stop group ISE-GROUP
aaa accounting commands 15 default start-stop group ISE-GROUP
aaa accounting network default start-stop group ISE-GROUP
aaa accounting connection default start-stop group ISE-GROUP

! Local users (fallback)
username admin privilege 15 secret 9 <encrypted_password>
username netops privilege 15 secret 9 <encrypted_password>
!
! Enable secret (for console access)
enable secret 9 <encrypted_password>
```

**Cisco NX-OS Template:**
```
! ============================================================================
! AAA Configuration using TACACS+ (NX-OS)
! ============================================================================

feature tacacs+

tacacs-server host 10.1.10.20 key 7 <encrypted_key>
tacacs-server host 10.1.10.21 key 7 <encrypted_key>
ip tacacs source-interface loopback0

aaa group server tacacs+ ISE-GROUP
  server 10.1.10.20
  server 10.1.10.21
  use-vrf management
  source-interface loopback0

aaa authentication login default group ISE-GROUP local
aaa authentication login console local
aaa authorization commands default group ISE-GROUP local
aaa authorization config-commands default group ISE-GROUP local
aaa accounting default group ISE-GROUP

! Local users
username admin password 5 <encrypted_password> role network-admin
username netops password 5 <encrypted_password> role network-admin
```

**Juniper JunOS Template:**
```
system {
    authentication-order [ tacplus password ];

    tacplus-server {
        10.1.10.20 {
            secret "<encrypted_key>";
            timeout 5;
            source-address 10.129.0.1;
        }
        10.1.10.21 {
            secret "<encrypted_key>";
            timeout 5;
            source-address 10.129.0.1;
        }
    }

    accounting {
        events [ login change-log interactive-commands ];
        destination {
            tacplus {
                server {
                    10.1.10.20 {
                        secret "<encrypted_key>";
                    }
                    10.1.10.21 {
                        secret "<encrypted_key>";
                    }
                }
            }
        }
    }

    login {
        /* Local users for fallback */
        user admin {
            uid 2000;
            class super-user;
            authentication {
                encrypted-password "<encrypted_password>";
            }
        }

        user netops {
            uid 2001;
            class super-user;
            authentication {
                encrypted-password "<encrypted_password>";
            }
        }
    }
}
```

### RADIUS Configuration (Alternative)

**Cisco IOS RADIUS Template:**
```
! RADIUS configuration (typically used for wireless, NAC)
aaa new-model

radius server ISE-1
  address ipv4 10.1.10.20 auth-port 1812 acct-port 1813
  key 7 <encrypted_key>
  timeout 5
  retransmit 3

radius server ISE-2
  address ipv4 10.1.10.21 auth-port 1812 acct-port 1813
  key 7 <encrypted_key>
  timeout 5
  retransmit 3

aaa group server radius ISE-RADIUS
  server name ISE-1
  server name ISE-2
  ip radius source-interface Loopback0

! Use for 802.1X authentication
aaa authentication dot1x default group ISE-RADIUS
aaa authorization network default group ISE-RADIUS
```

## Logging and Monitoring Configuration

### Syslog Configuration

**Cisco IOS/IOS-XE Template:**
```
! ============================================================================
! Logging Configuration
! Syslog servers: Splunk cluster
! ============================================================================

! Set logging buffer size
logging buffered 131072 informational
!
! Enable logging timestamps with milliseconds
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
!
! Set logging source interface
logging source-interface Loopback0
!
! Syslog servers
logging host 10.1.10.30 transport udp port 514
logging host 10.1.10.31 transport udp port 514
!
! Set logging severity
logging trap informational
logging facility local6
!
! Enable logging for specific features
logging event link-status default
logging event trunk-status default
logging event bundle-status default
!
! Rate limiting to prevent log flooding
logging rate-limit console 10 except errors
logging rate-limit all 100 except critical
```

**Cisco NX-OS Template:**
```
! ============================================================================
! Logging Configuration (NX-OS)
! ============================================================================

logging server 10.1.10.30 6 use-vrf management facility local6
logging server 10.1.10.31 6 use-vrf management facility local6
logging source-interface loopback0
logging timestamp milliseconds
logging monitor 6
logging level local6 6

! Log all configuration changes
logging logfile messages 6 size 16384
```

**Juniper JunOS Template:**
```
system {
    syslog {
        /* Archive local logs */
        archive size 10m files 10;

        /* Console logging */
        user * {
            any emergency;
        }

        /* Remote syslog servers */
        host 10.1.10.30 {
            any info;
            facility-override local6;
            source-address 10.129.0.1;
        }

        host 10.1.10.31 {
            any info;
            facility-override local6;
            source-address 10.129.0.1;
        }

        /* File logging */
        file messages {
            any info;
            authorization info;
        }

        file interactive-commands {
            interactive-commands any;
        }
    }
}
```

### SNMP Configuration

**SNMPv3 Configuration (Recommended):**

Cisco IOS:
```
! ============================================================================
! SNMPv3 Configuration (Secure)
! ============================================================================

! Enable SNMP
snmp-server manager
!
! SNMPv3 Groups
snmp-server group READONLY-GROUP v3 priv read READONLY-VIEW
snmp-server group READWRITE-GROUP v3 priv read READWRITE-VIEW write READWRITE-VIEW
!
! SNMPv3 Users
snmp-server user monitoring-user READONLY-GROUP v3 auth sha <auth_password> priv aes 256 <priv_password>
snmp-server user admin-user READWRITE-GROUP v3 auth sha <auth_password> priv aes 256 <priv_password>
!
! Views (limit accessible OIDs)
snmp-server view READONLY-VIEW iso included
snmp-server view READWRITE-VIEW iso included
!
! SNMP source interface
snmp-server source-interface traps Loopback0
snmp-server source-interface informs Loopback0
!
! Trap destination
snmp-server host 10.1.10.40 version 3 priv monitoring-user
!
! Enable specific traps
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart
snmp-server enable traps config
snmp-server enable traps entity
snmp-server enable traps envmon
snmp-server enable traps cpu threshold
!
! System information
snmp-server location "NYC Data Center - Rack A12 U24"
snmp-server contact "Network Operations Center - noc@company.com"
snmp-server chassis-id NYC-CORE-SW-01
```

Juniper JunOS:
```
snmp {
    location "NYC Data Center - Rack A12 U28";
    contact "Network Operations Center - noc@company.com";

    v3 {
        usm {
            local-engine {
                user monitoring-user {
                    authentication-sha {
                        authentication-password "<encrypted>";
                    }
                    privacy-aes128 {
                        privacy-password "<encrypted>";
                    }
                }
            }
        }

        vacm {
            security-to-group {
                security-model usm {
                    security-name monitoring-user {
                        group readonly-group;
                    }
                }
            }

            access {
                group readonly-group {
                    default-context-prefix {
                        security-model usm {
                            security-level privacy {
                                read-view all;
                            }
                        }
                    }
                }
            }
        }

        target-address monitoring-station {
            address 10.1.10.40;
            target-parameters monitoring-params;
        }

        target-parameters monitoring-params {
            parameters {
                message-processing-model v3;
                security-model usm;
                security-level privacy;
                security-name monitoring-user;
            }
        }
    }

    view all {
        oid .1 include;
    }
}
```

### NetFlow/IPFIX Configuration

**Cisco NetFlow v9 Configuration:**
```
! ============================================================================
! NetFlow Configuration for Traffic Analysis
! Collector: SolarWinds NTA at 10.1.10.50
! ============================================================================

! Define flow exporter
flow exporter NETFLOW-EXPORTER-1
  description Export to SolarWinds NTA
  destination 10.1.10.50
  source Loopback0
  transport udp 2055
  export-protocol netflow-v9
  template data timeout 60

! Define flow monitor
flow monitor NETFLOW-MONITOR-1
  description Monitor IPv4 traffic
  exporter NETFLOW-EXPORTER-1
  cache timeout active 60
  cache timeout inactive 15
  record netflow ipv4 original-input

! Apply to interfaces
interface GigabitEthernet1/0/1
  ip flow monitor NETFLOW-MONITOR-1 input
  ip flow monitor NETFLOW-MONITOR-1 output
```

## NTP Configuration Standards

### NTP Server Hierarchy

**Cisco IOS NTP Template:**
```
! ============================================================================
! NTP Configuration
! Stratum 2 servers: 10.1.10.5, 10.1.10.6 (company NTP servers)
! Stratum 1 public: 0.pool.ntp.org, 1.pool.ntp.org (fallback)
! ============================================================================

! Set timezone
clock timezone EST -5
clock summer-time EDT recurring

! Configure NTP authentication
ntp authenticate
ntp authentication-key 1 md5 <encrypted_key>
ntp trusted-key 1

! Internal NTP servers (preferred)
ntp server 10.1.10.5 key 1 prefer
ntp server 10.1.10.6 key 1

! Public NTP servers (fallback)
ntp server 0.pool.ntp.org
ntp server 1.pool.ntp.org

! Set NTP source interface
ntp source Loopback0

! Access control for NTP
ntp access-group serve-only NTP-ACL

! ACL for NTP access control
ip access-list standard NTP-ACL
  remark Allow NTP from management network
  permit 10.1.10.0 0.0.0.255
  deny any log
```

**Juniper JunOS NTP Template:**
```
system {
    time-zone America/New_York;

    ntp {
        boot-server 10.1.10.5;

        server 10.1.10.5 prefer;
        server 10.1.10.6;

        /* Fallback public NTP */
        server 0.pool.ntp.org;
        server 1.pool.ntp.org;

        source-address 10.129.0.1;
    }
}
```

## Security Hardening Standards

### Control Plane Protection

**Cisco IOS Control Plane Policing:**
```
! ============================================================================
! Control Plane Policing (CoPP)
! Purpose: Protect router CPU from DoS attacks
! Reference: Cisco Control Plane Protection Best Practices
! ============================================================================

! Define traffic classes
ip access-list extended CoPP-CRITICAL
  remark BGP traffic
  permit tcp any any eq bgp
  permit tcp any eq bgp any
  remark OSPF traffic
  permit ospf any any
  remark EIGRP traffic
  permit eigrp any any

ip access-list extended CoPP-IMPORTANT
  remark SSH management
  permit tcp 10.1.0.0 0.0.255.255 any eq 22
  remark SNMP
  permit udp 10.1.0.0 0.0.255.255 any eq snmp

ip access-list extended CoPP-NORMAL
  remark ICMP
  permit icmp any any echo
  permit icmp any any echo-reply
  permit icmp any any time-exceeded
  permit icmp any any unreachable

ip access-list extended CoPP-UNDESIRABLE
  remark Deny all other traffic to control plane
  deny ip any any

! Class maps
class-map match-all CoPP-CRITICAL-CLASS
  match access-group name CoPP-CRITICAL

class-map match-all CoPP-IMPORTANT-CLASS
  match access-group name CoPP-IMPORTANT

class-map match-all CoPP-NORMAL-CLASS
  match access-group name CoPP-NORMAL

class-map match-all CoPP-UNDESIRABLE-CLASS
  match access-group name CoPP-UNDESIRABLE

! Policy map
policy-map CoPP-POLICY
  class CoPP-CRITICAL-CLASS
    police 1000000 31250 31250 conform-action transmit exceed-action transmit
  class CoPP-IMPORTANT-CLASS
    police 500000 15625 15625 conform-action transmit exceed-action drop
  class CoPP-NORMAL-CLASS
    police 250000 7812 7812 conform-action transmit exceed-action drop
  class CoPP-UNDESIRABLE-CLASS
    police 8000 1000 1000 conform-action drop exceed-action drop

! Apply to control plane
control-plane
  service-policy input CoPP-POLICY
```

### Management Plane Security

**VTY Line Configuration:**

Cisco IOS:
```
! ============================================================================
! VTY Line Configuration (SSH Only)
! ============================================================================

! Disable Telnet, enable SSH only
line vty 0 15
  transport input ssh
  exec-timeout 10 0
  logging synchronous
  login authentication default
  authorization commands 15 default
  accounting commands 15 default
  !
  ! Apply access control
  access-class VTY-ACCESS in vrf-also

! Access control list for VTY access
ip access-list extended VTY-ACCESS
  remark Allow SSH from management network
  permit tcp 10.1.0.0 0.0.255.255 any eq 22
  remark Allow SSH from jump hosts
  permit tcp host 10.1.10.100 any eq 22
  deny ip any any log

! Console line configuration
line console 0
  exec-timeout 10 0
  logging synchronous
  login authentication default
  authorization commands 15 default
```

### Unused Service Disable

**Disable Unnecessary Services:**

Cisco IOS:
```
! ============================================================================
! Disable Unnecessary Services (Security Hardening)
! Reference: CIS Cisco IOS Benchmark
! ============================================================================

! Disable CDP on WAN interfaces
no cdp run
!
! Disable HTTP server
no ip http server
!
! Disable BOOTP server
no ip bootp server
!
! Disable finger service
no service finger
!
! Disable TCP/UDP small servers
no service tcp-small-servers
no service udp-small-servers
!
! Disable IP source routing
no ip source-route
!
! Disable proxy ARP globally
no ip proxy-arp
!
! Disable ICMP redirects
no ip redirects
!
! Disable ICMP unreachables on WAN interfaces
no ip unreachables
!
! Disable IP directed-broadcast
no ip directed-broadcast
!
! Disable PAD service
no service pad
```

Juniper JunOS:
```
system {
    services {
        /* Disable unused services */
        ftp {
            connection-limit 0;
        }

        /* Only allow SSH */
        ssh {
            root-login deny;
            protocol-version v2;
            connection-limit 10;
            rate-limit 5;
        }

        /* Disable telnet */
        delete: telnet;

        /* Disable HTTP (use HTTPS) */
        delete: web-management {
            http;
        }

        /* Enable HTTPS with restrictions */
        web-management {
            https {
                system-generated-certificate;
                interface [ fxp0.0 ];
            }
        }

        /* Disable BOOTP */
        delete: dhcp;
    }

    /* Disable unused protocols */
    delete: protocols {
        mpls;
    }
}
```

## Configuration Templates by Device Type

### Core Switch Template (Cisco Catalyst 9500)

```
! ============================================================================
! Core Switch Configuration Template
! Device: Cisco Catalyst 9500
! Role: Campus Core / Distribution
! ============================================================================

version 17.6
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service password-encryption
service compress-config
service sequence-numbers
!
hostname NYC-CORE-SW-01
!
boot-start-marker
boot-end-marker
!
vrf definition MGMT
 description Management VRF
 address-family ipv4
 exit-address-family
!
enable secret 9 <encrypted>
!
! AAA configuration here (see AAA section)
!
ip routing
!
ip domain-name company.local
!
! SVIs for Layer 3 routing
interface Vlan10
  description MGMT Network
  ip address 10.1.10.1 255.255.255.0
  no ip redirects
  no ip unreachables
  no ip proxy-arp

interface Vlan100
  description User VLAN
  ip address 10.1.100.1 255.255.252.0
  ip helper-address 10.1.10.5
  no ip redirects
  no ip unreachables
  no ip proxy-arp

! Loopback for management
interface Loopback0
  description Management Loopback - Router ID
  ip address 10.129.0.1 255.255.255.255

! Uplinks to core
interface TenGigabitEthernet1/1/1
  description UPLINK | NYC-CORE-SW-02 | Te1/1/1 | vPC Peer-Link
  no switchport
  ip address 10.128.0.1 255.255.255.252
  ip ospf network point-to-point
  ip ospf 1 area 0

! OSPF configuration
router ospf 1
  router-id 10.129.0.1
  log-adjacency-changes
  passive-interface default
  no passive-interface TenGigabitEthernet1/1/1
  network 10.1.0.0 0.0.255.255 area 0
  network 10.128.0.0 0.0.0.3 area 0
  network 10.129.0.1 0.0.0.0 area 0

! Logging, SNMP, NTP configuration (see respective sections)
!
end
```

### Edge Router Template (Cisco ISR 4000)

```
! ============================================================================
! Edge Router Configuration Template
! Device: Cisco ISR 4451
! Role: WAN Edge / Internet Gateway
! ============================================================================

version 17.6
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service password-encryption
!
hostname NYC-WAN-RTR-01
!
! AAA configuration
!
ip routing
ip cef
ipv6 unicast-routing
ipv6 cef
!
! WAN Interface (to ISP)
interface GigabitEthernet0/0/0
  description WAN | ISP-1 | Circuit-ID-12345 | Primary Internet
  ip address dhcp
  ip nat outside
  ip virtual-reassembly in
  duplex auto
  speed auto

! LAN Interface (to internal)
interface GigabitEthernet0/0/1
  description LAN | To Core
  ip address 10.128.1.1 255.255.255.252
  ip nat inside
  duplex auto
  speed auto

! NAT configuration
ip nat inside source list NAT-ACL interface GigabitEthernet0/0/0 overload

ip access-list standard NAT-ACL
  permit 10.0.0.0 0.255.255.255

! Default route to ISP
ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/0

! Static route to internal
ip route 10.0.0.0 255.0.0.0 10.128.1.2

! BGP configuration (if using BGP with ISP)
router bgp 65001
  bgp log-neighbor-changes
  neighbor 203.0.113.1 remote-as 174
  neighbor 203.0.113.1 description ISP-1 (Cogent)
  !
  address-family ipv4
    network 203.0.113.0 mask 255.255.255.0
    neighbor 203.0.113.1 activate
    neighbor 203.0.113.1 prefix-list ISP-IN in
    neighbor 203.0.113.1 prefix-list ISP-OUT out
  exit-address-family

! Prefix lists for BGP filtering
ip prefix-list ISP-OUT seq 5 permit 203.0.113.0/24

ip prefix-list ISP-IN seq 5 permit 0.0.0.0/0
ip prefix-list ISP-IN seq 999 deny 0.0.0.0/0 le 32

!
end
```

## Configuration Validation and Testing

### Pre-Deployment Checks

**Configuration Syntax Validation:**
```bash
# Cisco IOS - Use Cisco Modeling Labs (CML) or GNS3
# Load configuration in lab environment
# Validate syntax before deploying

# Juniper - Use commit check
user@router# load merge terminal
[paste configuration]
^D
user@router# commit check
configuration check succeeds

user@router# commit and-quit
```

**Automated Validation with NAPALM:**
```python
#!/usr/bin/env python3
"""
Configuration Validation Script
Uses NAPALM to validate configurations before deployment
"""

from napalm import get_network_driver
import json

def validate_config(device_type, hostname, username, password, config_file):
    """
    Validate configuration using NAPALM's compare_config
    """
    driver = get_network_driver(device_type)
    device = driver(hostname, username, password)

    device.open()

    # Load candidate configuration
    with open(config_file, 'r') as f:
        config_text = f.read()

    device.load_merge_candidate(config=config_text)

    # Get diff
    diff = device.compare_config()

    if diff:
        print(f"Configuration changes for {hostname}:")
        print(diff)

        # User confirmation
        confirm = input("Apply configuration? (yes/no): ")
        if confirm.lower() == 'yes':
            device.commit_config()
            print("Configuration applied successfully")
        else:
            device.discard_config()
            print("Configuration discarded")
    else:
        print("No configuration changes detected")

    device.close()

# Usage
validate_config('ios', '10.1.10.1', 'admin', 'password', 'NYC-CORE-SW-01.cfg')
```

## Configuration Backup and Archiving

### Automated Backup Solutions

**Oxidized Configuration:**
```yaml
---
# /etc/oxidized/config

username: oxidized
password: <encrypted_password>
model: junos
interval: 3600
use_syslog: false
debug: false
threads: 30
timeout: 20
retries: 3
prompt: !ruby/regexp /^([\w.@-]+[#>]\s?)$/

log: /var/log/oxidized/oxidized.log

crash:
  directory: /var/lib/oxidized/crashes
  hostnames: false

input:
  default: ssh, telnet
  debug: false
  ssh:
    secure: false

output:
  default: git
  git:
    user: Oxidized
    email: oxidized@company.com
    repo: "/var/lib/oxidized/configs.git"

source:
  default: csv
  csv:
    file: /etc/oxidized/router.db
    delimiter: !ruby/regexp /:/
    map:
      name: 0
      model: 1
      username: 2
      password: 3

model_map:
  cisco: ios
  juniper: junos
  arista: eos
```

**Router Database (router.db):**
```
NYC-CORE-SW-01:ios:oxidized:<password>
NYC-CORE-SW-02:ios:oxidized:<password>
NYC-WAN-RTR-01:ios:oxidized:<password>
LON-CORE-RTR-01:junos:oxidized:<password>
SIN-CORE-SW-01:eos:oxidized:<password>
```

## Conclusion

Following these configuration standards ensures:

1. **Consistency**: Uniform configurations across multi-vendor environments
2. **Security**: Hardened configurations following industry best practices
3. **Maintainability**: Clear naming, comments, and structure
4. **Auditability**: Comprehensive logging and tracking
5. **Automation**: Configuration patterns suitable for automation tools

**Key Principles to Remember:**
- Document everything with comments
- Use consistent naming conventions
- Implement defense-in-depth security
- Enable comprehensive logging and monitoring
- Version control all configurations
- Test in lab before production deployment
- Maintain configuration backups
- Regular audits and compliance checks

**References:**
- Cisco IOS Configuration Guides: https://www.cisco.com/c/en/us/support/ios-nx-os-software/
- Juniper Configuration Guides: https://www.juniper.net/documentation/
- CIS Benchmarks: https://www.cisecurity.org/cis-benchmarks/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- NAPALM Documentation: https://napalm.readthedocs.io/
