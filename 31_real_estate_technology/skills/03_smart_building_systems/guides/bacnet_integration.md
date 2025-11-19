# BACnet Integration Guide

## Setup BACnet/IP Network

### Network Configuration
```
Network: 192.168.10.0/24
Gateway: 192.168.10.1
Controllers: 192.168.10.10-50
Sensors: 192.168.10.51-200
BACnet Port: 47808 (UDP)
```

### Device Discovery
```python
import BAC0

# Connect to network
bacnet = BAC0.connect(ip='192.168.10.100/24')

# Discover all devices
bacnet.whois()
time.sleep(5)

# List discovered devices
for device in bacnet.devices:
    print(f"Device {device.id}: {device.name}")
```

## Reading Data

### Single Property
```python
# Read temperature
temp = bacnet.read('101:1 analogInput 1 presentValue')
print(f"Temperature: {temp}°F")

# Read with units
result = bacnet.readMultiple('101:1 analogInput 1 presentValue units')
print(f"Value: {result[0]}, Units: {result[1]}")
```

### Multiple Properties
```python
# Read all zone data
zone_data = bacnet.readMultiple('''
    101:1 analogInput 1 presentValue
    101:1 analogInput 2 presentValue
    101:1 binaryInput 1 presentValue
''')
```

## Writing Values

### Setpoint Control
```python
# Write with priority (1-16)
bacnet.write('101:1 analogValue 1 presentValue 72 - 8')

# Release priority
bacnet.write('101:1 analogValue 1 presentValue null - 8')
```

## Change-of-Value (COV) Subscriptions
```python
def on_temperature_change(data):
    print(f"Temperature changed to {data}")

# Subscribe
bacnet.subscribe_cov('101:1 analogInput 1', callback=on_temperature_change)
```

## Troubleshooting
- Verify network connectivity
- Check firewall (allow UDP 47808)
- Confirm device IDs are unique
- Validate COV increment settings

## See Also
- iot_protocols_reference.md
- hvac_basics.md
