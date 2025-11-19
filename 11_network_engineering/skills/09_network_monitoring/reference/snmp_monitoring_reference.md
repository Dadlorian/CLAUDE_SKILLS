# SNMP Monitoring Reference

## Overview
SNMP (Simple Network Management Protocol) is the foundational protocol for network device management and monitoring in enterprise networks.

## SNMP Versions & Features

### SNMP v1 (RFC 1155)
- **Security**: Community string only (plaintext)
- **PDU Types**: GET, SET, GETNEXT, TRAP, RESPONSE
- **Scope**: Basic device monitoring
- **Limitations**: No encryption, poor scalability
- **Use Case**: Legacy devices, simple monitoring

### SNMP v2c (RFC 1901)
- **Security**: Community string (still plaintext)
- **Enhancements**:
  - GETBULK for efficient queries
  - Better error handling
  - 64-bit counters
- **Limitations**: No encryption, same community vulnerability
- **Use Case**: Most common in legacy networks

### SNMPv3 (RFC 3413-3415)
- **Security Levels**:
  - `noAuthNoPriv`: No authentication or privacy
  - `authNoPriv`: Authentication only (HMAC-MD5/SHA)
  - `authPriv`: Authentication + privacy (DES/AES)
- **User-Based Security Model (USM)**
- **View-Based Access Control Model (VACM)**
- **Engine ID**: Unique identifier for SNMPv3 engine
- **Use Case**: Enterprise standard for secure monitoring

## MIB (Management Information Base)

### MIB Structure
```
.1 (iso)
├── .1.3.6.1.2.1 (mgmt)
│   ├── .1.1 (system) - sysDescr, sysUptime, sysContact
│   ├── .1.2 (interfaces) - ifName, ifSpeed, ifInOctets
│   ├── .1.3 (at) - ARP translation table
│   ├── .1.4 (ip) - IP routing and statistics
│   ├── .1.5 (transmission) - Media-specific
│   └── .1.6 (snmp) - SNMP statistics
├── .1.3.6.1.4.1 (enterprises) - Vendor-specific OIDs
```

### Standard MIBs
- **SNMPv2-MIB**: Core system and interface MIBs
- **IF-MIB**: Interface statistics
- **IP-MIB**: IP layer statistics
- **TCP-MIB**: TCP-specific metrics
- **UDP-MIB**: UDP-specific metrics
- **ENTITY-MIB**: Physical component inventory
- **BRIDGE-MIB**: Bridge/switch functionality
- **POWER-ETHERNET-MIB**: PoE management

### Vendor-Specific MIBs
- **Cisco**: CISCO-PROCESS-MIB, CISCO-BGP-MIB
- **Juniper**: JUNIPER-MIB, JNPR-SYSTEM-MIB
- **Arista**: ARISTA-ENTITY-MIB

## Common OIDs

### System Information
```
.1.3.6.1.2.1.1.1.0    sysDescr           - System description
.1.3.6.1.2.1.1.2.0    sysObjectID        - System object identifier
.1.3.6.1.2.1.1.3.0    sysUptime          - System uptime
.1.3.6.1.2.1.1.4.0    sysContact         - System contact
.1.3.6.1.2.1.1.5.0    sysName            - System name
.1.3.6.1.2.1.1.6.0    sysLocation        - System location
.1.3.6.1.2.1.1.7.0    sysServices        - System services
```

### Interface Statistics
```
.1.3.6.1.2.1.2.1.0    ifNumber           - Number of interfaces
.1.3.6.1.2.1.2.2.1.1  ifIndex            - Interface index
.1.3.6.1.2.1.2.2.1.2  ifDescr            - Interface description
.1.3.6.1.2.1.2.2.1.3  ifType             - Interface type
.1.3.6.1.2.1.2.2.1.4  ifMtu              - Interface MTU
.1.3.6.1.2.1.2.2.1.5  ifSpeed            - Interface speed
.1.3.6.1.2.1.2.2.1.8  ifOperStatus       - Operational status (1=up, 2=down)
.1.3.6.1.2.1.2.2.1.9  ifLastChange       - Last status change
.1.3.6.1.2.1.2.2.1.10 ifInOctets         - Input bytes
.1.3.6.1.2.1.2.2.1.11 ifInUcastPkts      - Input unicast packets
.1.3.6.1.2.1.2.2.1.12 ifInNUcastPkts     - Input non-unicast packets
.1.3.6.1.2.1.2.2.1.13 ifInDiscards       - Input discards
.1.3.6.1.2.1.2.2.1.14 ifInErrors         - Input errors
.1.3.6.1.2.1.2.2.1.16 ifOutOctets        - Output bytes
.1.3.6.1.2.1.2.2.1.17 ifOutUcastPkts     - Output unicast packets
.1.3.6.1.2.1.2.2.1.19 ifOutDiscards      - Output discards
.1.3.6.1.2.1.2.2.1.20 ifOutErrors        - Output errors
```

### CPU & Memory
```
.1.3.6.1.2.1.25.3.2.1.5   hrProcessorLoad   - CPU utilization
.1.3.6.1.2.1.25.2.3.1.6   hrStorageUsed     - Storage used
.1.3.6.1.2.1.25.2.3.1.5   hrStorageSize     - Storage size
```

## SNMP Operations

### GET Request
```
snmpget -v 3 -u username -a SHA -A authpass \
  -x AES -X privpass 192.168.1.1 \
  1.3.6.1.2.1.1.1.0
```

### GETNEXT Request (Walk)
```
snmpwalk -v 3 -u username -a SHA -A authpass \
  -x AES -X privpass 192.168.1.1 \
  1.3.6.1.2.1.2.2
```

### GETBULK (Efficient retrieval)
```
snmpbulkwalk -v 2c -c public 192.168.1.1 \
  1.3.6.1.2.1.2.2
```

### SET Request
```
snmpset -v 3 -u username -a SHA -A authpass \
  -x AES -X privpass 192.168.1.1 \
  1.3.6.1.2.1.1.4.0 s "New Contact"
```

## SNMP Traps & Notifications

### Trap Types
- **coldStart (0)**: Device restart
- **warmStart (1)**: Device soft reset
- **linkDown (2)**: Interface down
- **linkUp (3)**: Interface up
- **authenticationFailure (4)**: Auth attempt failed
- **egpNeighborLoss (5)**: EGP neighbor lost
- **enterpriseSpecific (6)**: Vendor-specific trap

### SNMPv3 Informed (Inform)
- Similar to traps but with acknowledgment
- More reliable than traps
- Higher overhead

### Trap Receiver Configuration
```
# snmptrapd.conf
authCommunity log,execute,net public
disableAuthorization no
traphandle default /usr/bin/logger "TRAP: %a"
```

## Metrics & Thresholds

### Availability
```
sysUptime > 99.5% - Excellent
sysUptime 95-99.5% - Good
sysUptime 90-95% - Fair
sysUptime < 90% - Poor
```

### Interface Utilization
```
ifInOctets / ifSpeed / sampling_period
Healthy: < 70% utilization
Caution: 70-85%
Critical: > 85%
```

### Error Thresholds
```
ifInErrors: 0 errors (target)
ifInDiscards: 0 discards (target)
Rising trend: Investigate immediately
```

### CPU Utilization
```
< 50%: Healthy
50-80%: Monitor
80-95%: Caution
> 95%: Critical
```

## Performance Optimization

### Polling Strategy
1. **Baseline**: Determine device capability
2. **Frequency**: Balance visibility vs overhead
   - Interface stats: 5-minute intervals
   - System stats: 5-10 minute intervals
   - Event-driven: Real-time traps
3. **Bulk Operations**: Use GETBULK for efficiency
4. **Caching**: Store results to reduce queries

### SNMP Limitations
- **Overhead**: Each query consumes bandwidth
- **Latency**: Poll-based detection has delay
- **Scalability**: Linear scaling with device count
- **Reliability**: UDP-based, no guarantees

## Security Considerations

### SNMPv3 Best Practices
1. **Use authPriv**: Never deploy without encryption
2. **Strong Passwords**: Minimum 16 characters
3. **Access Control**: Use VACM views
4. **Engine ID**: Keep private and unique
5. **Monitor**: Track failed auth attempts

### Common Vulnerabilities
- **Default credentials**: Change community strings
- **Plaintext v1/v2c**: Never expose to internet
- **Trap floods**: Rate limiting and filtering
- **Information disclosure**: Limit MIB access

## Tools & Utilities

### Command-line Tools
- **snmpget/snmpset/snmpwalk**: Net-SNMP
- **snmptrapd**: Trap receiver daemon
- **snmpbulkwalk**: Efficient bulk retrieval
- **snmptranslate**: OID translation

### Monitoring Integration
- **Prometheus SNMP Exporter**: Convert SNMP to Prometheus
- **Telegraf SNMP Plugin**: Agent-based SNMP collection
- **Zabbix SNMP**: Native SNMP support
- **Nagios**: SNMP check plugins

## Implementation Checklist

- [ ] Identify SNMPv3 support on target devices
- [ ] Plan community structure (read-only, read-write, trap)
- [ ] Generate SNMPv3 credentials with proper hashing
- [ ] Configure VACM views for least privilege
- [ ] Deploy trap receivers with logging
- [ ] Test polling from management station
- [ ] Verify baseline metrics collection
- [ ] Establish alerting thresholds
- [ ] Document custom MIBs
- [ ] Schedule credential rotation

---

**Reference Type**: Protocol Standards
**Applicable Devices**: All SNMP-capable network devices
**Current Version**: SNMPv3 (RFC 3413-3415)
**Last Updated**: 2025-11-19
