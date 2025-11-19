# BACnet Reference Guide

## BACnet Basics

**Version**: BACnet 2020 (ANSI/ASHRAE Standard 135-2020)
**Purpose**: Standardized building automation protocol

## Network Types

- **BACnet/IP**: Over Ethernet/IP (most common)
- **BACnet MS/TP**: Master-Slave/Token-Passing over RS-485
- **BACnet/SC**: Secure Connect (encrypted, cloud-ready)

## Object Identifier Format

```
Object_Type : Instance_Number

Examples:
device:101            # Building controller
analogInput:1         # Temperature sensor
analogOutput:2        # Damper control
binaryInput:5         # Door status
analogValue:10        # Setpoint
schedule:1            # HVAC schedule
```

## Common Properties

```
present-value         # Current value
units                 # Engineering units
description           # Human-readable name
status-flags          # Alarm/fault/overridden/out-of-service
reliability           # No-fault-detected, sensor-failure, etc.
out-of-service        # Device disabled for maintenance
priority-array        # 16-level priority (1=highest, 16=lowest)
```

## Priority Array

```
1  - Manual override (critical)
2  - Manual override  
3  - High level automation
4  - Medium level automation
5  - Low level automation
6  - Unoccupied
7  - Occupied
8  - Default/scheduled
9-15 - Available
16 - Minimum (default)
```

## Python BACnet Example

```python
import BAC0

# Connect
bacnet = BAC0.connect(ip='192.168.1.10/24')

# Device discovery
bacnet.whois()

# Read temperature
temp = bacnet.read('101:1 analogInput 1 presentValue')

# Write setpoint with priority
bacnet.write('101:1 analogValue 1 presentValue 72 - 8')

# Read multiple properties
props = bacnet.readMultiple('101:1 analogInput 1 presentValue units description')
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Device not responding | Network issue, wrong IP | Check connectivity, verify IP |
| Cannot write value | Priority conflict | Check priority array |
| Stale data | COV subscription lost | Re-subscribe |
| Device offline | Power/network failure | Physical check |

## See Also
- iot_protocols_reference.md
- hvac_basics.md
