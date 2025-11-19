# Network Security Subskill

## Overview

Advanced network security expertise covering enterprise-grade firewall deployment, VPN technologies, network segmentation, zero trust architecture, and intrusion detection/prevention systems. Provides comprehensive knowledge of security zones, access control, threat mitigation, and compliance frameworks. This skill enables professionals to architect and implement defense-in-depth security strategies protecting against evolving threats.

## Core Competencies

### 1. Firewall Technologies & Configuration

#### Stateful Inspection Firewalls
- **Packet Filtering**: Examining packet headers for allow/deny decisions
- **Connection Tracking**: Maintaining state table of active connections
- **State Tables**: Memory requirements, TCP state tracking, timeout values
- **Dynamic Rule Generation**: Temporary rules for return traffic
- **Session Management**: Connection establishment and termination tracking
- **Protocol-Specific Handling**: TCP, UDP, ICMP, GRE processing

#### Next-Generation Firewalls (NGFW)
- **Application Layer Inspection**: Identifying and controlling applications
- **Threat Prevention**: IPS integration, malware detection, vulnerability exploitation blocking
- **SSL Inspection**: Decrypting and inspecting HTTPS traffic
- **User Identity**: Identifying traffic by user, not just IP address
- **Advanced Threat Protection**: Sandboxing, behavioral analysis, zero-day defense
- **Integration Capabilities**: Threat intelligence, cloud APIs, AI/ML detection

#### Firewall Architectures
- **Perimeter Firewalls**: Protecting network edge from internet
- **Internal Firewalls**: East-west traffic segmentation between zones
- **Distributed Firewalls**: Per-server or per-VM enforcement
- **Inline Deployment**: Actively monitoring and blocking traffic
- **Out-of-band Deployment**: Monitoring without blocking (IDS mode)
- **Redundancy**: Active-passive, active-active configurations

#### Vendor Platforms
- **Cisco ASA**: Cisco's enterprise firewall, routing, VPN capabilities
- **Palo Alto Networks**: Application-centric security, cloud integration
- **Fortinet FortiGate**: Performance-optimized, AI-driven threat detection
- **Checkpoint**: Enterprise security, zero-trust features
- **Juniper SRX**: Branch and data center firewalls, advanced routing

#### Rule Management
- **Policy Organization**: Hierarchical policy structure
- **Rule Ordering**: Processing order impact on security
- **Default Policies**: Implicit allow or deny defaults
- **Rule Consolidation**: Combining overlapping rules for efficiency
- **Logging and Auditing**: Tracking rule matches and violations
- **Version Control**: Tracking policy changes over time

#### High Availability
- **Active-Passive**: One firewall active, one standby
- **Active-Active**: Both firewalls processing traffic simultaneously
- **Stateful Failover**: Preserving connection state during failover
- **Health Monitoring**: Detecting and responding to failures
- **Failover Testing**: Regular HA validation

### 2. Access Control Lists (ACLs)

#### ACL Types
- **Standard ACLs**: Single criteria (source IP only)
- **Extended ACLs**: Multiple criteria (protocol, port, destination)
- **Named ACLs**: Using descriptive names instead of numbers
- **Dynamic ACLs**: Lock-and-key access for temporary credentials
- **Reflexive ACLs**: Automatically creating return path rules
- **Time-Based ACLs**: Rules active only during specified times

#### ACL Design
- **Permit-Based**: Start with deny-all, explicitly permit traffic
- **Deny-Based**: Start with allow-all, explicitly block
- **Organization**: Grouping related rules, DNE conventions
- **Optimization**: Ordering for performance (most common rules first)
- **Scalability**: Managing thousands of rules

#### Object Groups
- **Network Object Groups**: Collections of IP addresses or networks
- **Service Object Groups**: Collections of ports and protocols
- **Protocol Object Groups**: Multiple protocols grouped
- **Reusability**: Using groups across multiple rules
- **Maintenance**: Central management of address and service lists

### 3. Virtual Private Networks (VPNs)
- **IPsec VPN**: Site-to-site encryption, authentication, key management
- **SSL/TLS VPN**: Remote access, clientless access, application-level security
- **WireGuard**: Modern VPN protocol, performance optimization
- **IKEv2/IKEv1**: Key exchange protocols, security considerations
- **DMVPN**: Dynamic multipoint VPN, hub-and-spoke topologies
- **VPN Failover**: Redundancy and high availability designs
- **Encryption Standards**: AES, 3DES, key lengths and security implications

### 4. Network Segmentation & Micro-Segmentation

#### DMZ (Demilitarized Zone) Design
- **Single-Tier DMZ**: Simple perimeter protection
- **Multi-Tier DMZ**: Separate zones for different trust levels
- **Web Servers**: Internet-facing public services
- **Application Servers**: Middle tier for business logic
- **Database Tier**: Innermost tier with sensitive data
- **Management Network**: Protected management access
- **Fail-Open/Fail-Closed**: Handling firewall failures

#### VLAN Segmentation
- **VLAN Planning**: Matching VLANs to business units or function
- **VLAN Routing**: Inter-VLAN communication control
- **Access Control**: Which VLANs can communicate
- **Isolation**: Complete vs. partial VLAN isolation
- **Scalability**: Managing hundreds or thousands of VLANs
- **Voice/Video VLANs**: Special handling for QoS-sensitive traffic

#### Network Zones
- **Untrusted/External Zone**: Internet-facing, highest risk
- **Demilitarized Zone (DMZ)**: Limited trust, controlled resources
- **Internal Zone**: Corporate network, higher trust
- **Restricted Zone**: Sensitive systems, highest protection
- **Guest Zone**: Visitor network, isolated from production

#### Micro-Segmentation
- **Granular Control**: Per-application or per-workload isolation
- **Zero-Trust Enforcement**: No implicit trust between segments
- **Lateral Movement Prevention**: Limiting breach propagation
- **Compliance Alignment**: Meeting regulatory isolation requirements
- **Technology**: VLAN-based, software-defined, overlay networks

#### Routing Between Zones
- **Inter-Zone Routing**: Controlled communication between zones
- **Firewall Rules**: Explicit allow/deny policies
- **Route Propagation**: Controlling routing information flow
- **Policy Routing**: Conditional routing based on rules
- **Monitoring**: Tracking inter-zone traffic for anomalies

### 5. Zero Trust Architecture

#### Core Principles
- **Never Trust, Always Verify**: Every request authenticated and authorized
- **Least Privilege Access**: Minimum necessary permissions
- **Assume Breach**: Designing for inevitable compromises
- **Verify Explicitly**: Using all data points for decisions
- **Secure by Default**: Deny-all, explicitly allow model

#### Identity & Access Management
- **User Authentication**: Strong identity verification
- **Device Authentication**: Device identity and integrity
- **Context-Aware Access**: Location, time, device health factors
- **Multi-Factor Authentication**: Multiple authentication methods
- **Continuous Verification**: Real-time security posture checks

#### Network Architecture
- **Micro-Segmentation**: Applying zero-trust per-application
- **Software-Defined Perimeter**: Dynamic network boundaries
- **Centralized Policy Enforcement**: Single point of control
- **Transparent Inspection**: Analyzing all traffic
- **Encrypted Communications**: All traffic encrypted by default

#### Implementation
- **Phased Approach**: Gradual zero-trust adoption
- **Pilot Programs**: Testing in limited scope first
- **Tool Integration**: Combining identity, endpoint, network tools
- **Policy Definition**: Translating business rules to security policies
- **User Experience**: Balancing security with usability

### 6. Authentication & Authorization

#### 802.1X Port-Based Access Control
- **Supplicant**: Device requesting network access
- **Authenticator**: Switch or WAP controlling port access
- **Authentication Server**: RADIUS or TACACS+ backend
- **EAP Protocol**: Extensible Authentication Protocol variants
- **Port States**: Blocked, authorized, multi-auth modes
- **Dynamic VLAN Assignment**: Assigning VLANs based on identity

#### RADIUS & TACACS+
- **RADIUS**: UDP-based, simpler protocol, wide support
- **TACACS+**: TCP-based, more granular authorization
- **Accounting**: Tracking resource usage and audit trails
- **Server Redundancy**: Primary/secondary server configuration
- **Failover**: Handling authentication server failures

#### EAP Methods
- **EAP-TLS**: Certificate-based, highest security
- **EAP-TTLS**: Password-based inside encrypted tunnel
- **PEAP**: Protected EAP for Windows environments
- **EAP-FAST**: Lightweight version for mobile devices
- **Mutual Authentication**: Both device and server verify identity

#### Multi-Factor Authentication
- **Something You Know**: Passwords, PINs
- **Something You Have**: Certificates, tokens, hardware keys
- **Something You Are**: Biometrics (fingerprint, face)
- **Somewhere You Are**: Geographic location verification
- **Adaptive Authentication**: Risk-based MFA requirements

#### Network Access Control (NAC)
- **Pre-Access NAC**: Checking compliance before allowing access
- **Post-Access NAC**: Continuous monitoring after access granted
- **Compliance Checking**: Antivirus, patches, firewall status
- **Non-Compliant Handling**: Quarantine, restricted access, remediation
- **Integration**: Working with Active Directory, certificates, endpoints

### 7. Intrusion Detection & Prevention

#### IDS Deployment Models
- **Network-Based IDS**: Monitoring network traffic on sensors
- **Host-Based IDS**: Running on individual systems
- **Hybrid IDS**: Combining network and host-based
- **Passive Monitoring**: Detecting without blocking
- **Inline Deployment**: Active packet analysis and blocking

#### IPS Technologies
- **Signature-Based Detection**: Known attack patterns
- **Anomaly-Based Detection**: Deviation from baseline behavior
- **Protocol Anomaly Detection**: Invalid protocol use
- **Behavioral Analysis**: Suspicious activity patterns
- **Machine Learning**: AI-driven threat detection

#### Threat Intelligence
- **Internal Threat Feeds**: Organization's own data
- **Commercial Feeds**: Third-party threat information
- **Open Source Feeds**: Community-contributed intelligence
- **Integration**: Feeding threat data into detection systems
- **Blocking**: Automatic blocking of known threats

#### Alert Management
- **Threshold Tuning**: Balancing detection and false positives
- **Alert Correlation**: Linking related alerts
- **Severity Classification**: Prioritizing critical alerts
- **SIEM Integration**: Centralized alert management
- **Response Playbooks**: Automated or guided responses

#### Forensics & Investigation
- **Packet Capture**: Preserving evidence of attacks
- **Log Analysis**: Examining system and application logs
- **Timeline Creation**: Reconstructing attack sequence
- **Root Cause Analysis**: Identifying vulnerability exploited
- **Evidence Preservation**: Maintaining chain of custody

### 8. DDoS Mitigation

#### Attack Types
- **Volumetric Attacks**: Flooding with massive traffic volume
- **Protocol Attacks**: Exploiting weaknesses in protocols
- **Application Attacks**: Targeting application layer

#### Detection Methods
- **Signature-Based**: Known attack patterns
- **Rate-Based**: Detecting unusual traffic rates
- **Behavioral Analysis**: Deviations from normal patterns
- **Threshold Setting**: Configuring detection sensitivity

#### Mitigation Strategies
- **Rate Limiting**: Throttling suspected attack traffic
- **Traffic Scrubbing**: Filtering malicious traffic
- **Blackhole Routing**: Dropping attack traffic
- **Upstream Filtering**: ISP-level protection
- **Anycast Distribution**: Spreading load across multiple sites

#### Service Provider Solutions
- **Cloud-Based Mitigation**: Third-party DDoS protection
- **Always-On Protection**: Continuous filtering
- **Scalable Capacity**: Absorbing massive attack volumes
- **Selective Activation**: Routing to scrubbing center only when attacked

#### On-Premises Solutions
- **Network Appliances**: Dedicated DDoS detection/mitigation
- **Server-Side Protection**: Application-level defense
- **Rate Limiting**: Bandwidth management
- **Redundancy**: Multiple paths and providers

### 9. Encryption & Cryptography

#### Symmetric Encryption
- **AES (Advanced Encryption Standard)**: 128, 192, 256-bit keys
- **3DES (Triple DES)**: Legacy but still used
- **ChaCha20**: Modern, performance-optimized cipher
- **Mode of Operation**: ECB, CBC, CTR, GCM modes
- **Key Management**: Generation, storage, rotation

#### Asymmetric Encryption
- **RSA**: Large key sizes (2048, 4096-bit)
- **ECC (Elliptic Curve)**: Smaller key sizes, similar security
- **Key Exchange**: Establishing shared secrets
- **Digital Signatures**: Proving authenticity and non-repudiation
- **Certificate Authority**: Issuing and managing certificates

#### Hashing & Integrity
- **SHA-256/384/512**: Industry-standard hash functions
- **HMAC**: Keyed hash for authentication
- **Integrity Verification**: Detecting tampering
- **Collision Resistance**: Ensuring uniqueness

#### Perfect Forward Secrecy (PFS)
- **Session Keys**: Unique key per session
- **Ephemeral Keys**: Temporary encryption keys
- **Compromise Isolation**: Session compromise doesn't affect other sessions
- **Implementation**: Diffie-Hellman, ECDH key exchange

#### SSL/TLS Implementation
- **TLS 1.2 & 1.3**: Modern protocol versions
- **Cipher Suite Selection**: Balancing security and performance
- **Certificate Management**: Provisioning, renewal, revocation
- **Certificate Pinning**: Preventing MITM with cert substitution
- **OCSP Stapling**: Efficient certificate status checking

### 10. Security Compliance Frameworks

#### Regulatory Standards
- **PCI-DSS**: Payment Card Industry Data Security Standard
- **HIPAA**: Health Insurance Portability and Accountability Act
- **SOC 2**: Service Organization Control audits
- **GDPR**: General Data Protection Regulation
- **CCPA**: California Consumer Privacy Act

#### Industry Standards
- **NIST Cybersecurity Framework**: U.S. government standard
- **CIS Benchmarks**: Center for Internet Security best practices
- **NIST SP 800-53**: Detailed security controls
- **ISO 27001**: Information security management system

#### Compliance Requirements
- **Network Segmentation**: Isolation of sensitive data
- **Access Control**: Authentication and authorization
- **Audit Logging**: Recording security-relevant events
- **Encryption**: Protecting sensitive data in transit and at rest
- **Change Management**: Controlled modifications
- **Incident Response**: Breach detection and response

#### Assessment & Audit
- **Vulnerability Assessment**: Identifying weaknesses
- **Penetration Testing**: Simulated attacks
- **Compliance Audit**: Verifying control effectiveness
- **Gap Analysis**: Identifying compliance gaps
- **Risk Assessment**: Evaluating threat and impact

#### Reporting & Remediation
- **Security Metrics**: KPIs and dashboards
- **Audit Trails**: Detailed event logging
- **Compliance Reports**: Executive summaries
- **Remediation Plans**: Addressing identified gaps
- **Continuous Improvement**: Regular review and updates

## Key Topics

### Firewalls
- Stateful packet inspection and connection tracking
- Application layer filtering and inspection
- Policy-based routing and traffic management
- Threat prevention and advanced protection features
- Integration with other security systems
- Configuration management and version control
- Performance optimization and throughput considerations

### Network Segmentation
- Designing security zones (DMZ, internal, trusted networks)
- VLAN implementation and inter-VLAN routing
- Access control between network segments
- Perimeter security design
- Data center segmentation strategies
- Compliance-driven segmentation requirements

### VPN Technologies
- IPsec fundamentals and configuration
- Site-to-site and remote access implementations
- High availability and redundancy
- Performance optimization and monitoring
- Troubleshooting common VPN issues
- WireGuard and modern VPN protocols

### Zero Trust
- Moving from perimeter-based to zero trust models
- Identity and access management integration
- Continuous monitoring and verification
- Micro-segmentation strategies
- Application-level security controls
- Implementation best practices and roadmaps

### Threat Detection & Response
- IDS/IPS deployment strategies
- Signature and anomaly-based detection
- Alert tuning and false positive reduction
- Integration with SIEM systems
- Incident response procedures
- Forensic analysis capabilities

## Hands-On Lab Scenarios

1. **Firewall Policy Design**: Create multi-zone firewall policies for enterprise network
2. **VPN Implementation**: Deploy site-to-site IPsec VPN between data centers
3. **Network Segmentation**: Design and implement DMZ architecture
4. **Zero Trust Migration**: Plan and execute transition to zero trust model
5. **802.1X Deployment**: Configure port-based authentication for network access
6. **IDS/IPS Tuning**: Optimize intrusion detection rules and reduce false positives
7. **DDoS Response**: Implement mitigation strategies during simulated attack
8. **Security Audit**: Assess network security posture and recommend improvements
9. **Incident Investigation**: Analyze logs and network traffic for security breach
10. **Compliance Verification**: Verify network security controls meet regulatory requirements

## Practical Applications

- Enterprise network security architecture design
- Firewall and security appliance configuration and management
- VPN deployment for secure remote access and site-to-site connectivity
- Network segmentation implementation for compliance and risk reduction
- Zero trust architecture implementation and migration
- Intrusion detection and prevention system tuning
- DDoS mitigation and incident response
- Security assessment and compliance audits
- Threat intelligence integration and incident investigation
- Security baseline establishment and hardening

## Related Skills

- Network Design (01_network_design)
- Routing & Switching (02_routing_switching)
- Network Automation (05_network_automation)
- Network Monitoring (09_network_monitoring)
- VPN & Remote Access (08_vpn_remote_access)

## Prerequisites

- Solid understanding of networking fundamentals (OSI model, TCP/IP)
- Knowledge of routing and switching technologies
- Familiarity with network protocols and packet structure
- Basic understanding of cryptography and encryption
- Linux/Unix and command-line proficiency
- Scripting knowledge (Python, Bash) for automation

## Certification Alignment

- Cisco CCNP Security
- Palo Alto Networks Certified Network Security Engineer
- Fortinet Certified Associate FortiGate Administrator
- EC-Council Certified Security Analyst (ECSA)
- GIAC Certified Enterprise Defender (GCED)
- Certified Information Systems Security Professional (CISSP)
