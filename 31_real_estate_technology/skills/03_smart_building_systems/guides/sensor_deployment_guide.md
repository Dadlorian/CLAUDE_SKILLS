# Sensor Deployment Guide

## Planning Phase

### 1. Define Objectives
- Energy monitoring and optimization
- Occupancy-based control
- Predictive maintenance
- Indoor air quality
- Water conservation

### 2. Zone Analysis
```
Building: Office Building
Total Area: 50,000 sq ft
Zones:
  - Open office areas (8 zones)
  - Conference rooms (12 rooms)
  - Common areas (lobbies, cafeteria)
  - Mechanical rooms
```

### 3. Sensor Selection

**Temperature Sensors**:
- Quantity: 1 per zone + outdoor
- Location: Wall-mounted, 5ft height
- Type: BACnet or MQTT-enabled

**Occupancy Sensors**:
- Conference rooms: Ceiling PIR
- Open areas: Dual-technology
- Restrooms: Ultrasonic

**Energy Meters**:
- Main service: 1 meter
- HVAC equipment: 1 per unit
- Tenant spaces: Sub-meters

## Installation

### Network Infrastructure
```
Gateway (BACnet/IP) → Ethernet Switch → Cloud Platform

Sensor → Wireless (LoRa/Zigbee) → Gateway
OR
Sensor → Hardwired (RS-485) → Controller
```

### Mounting Guidelines
- Height: 5-6 ft for temperature
- Coverage: Check sensor datasheet
- Avoid: Direct sunlight, vents, doors
- Access: Maintainable location

## Configuration

### MQTT Topics
```
building/{id}/zone/{zone}/temperature
building/{id}/zone/{zone}/occupancy
building/{id}/equipment/{id}/power
```

### BACnet Configuration
```
Device ID: Unique per sensor
IP Address: Static or DHCP reservation
Object IDs: Sequential numbering
COV Increment: 0.5°F for temperature
```

## Testing & Validation
1. Verify sensor readings
2. Check wireless signal strength
3. Validate data in platform
4. Test alerts and notifications

## See Also
- iot_protocols_reference.md
- bacnet_integration.md
