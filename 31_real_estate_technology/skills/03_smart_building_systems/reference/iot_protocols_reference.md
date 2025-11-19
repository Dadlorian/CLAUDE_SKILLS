# IoT Protocols Reference

## MQTT (Message Queuing Telemetry Transport)

### Basic Concepts
- **Lightweight**: Minimal overhead, ideal for IoT
- **Publish/Subscribe**: Decoupled communication
- **Quality of Service**: 0 (at most once), 1 (at least once), 2 (exactly once)
- **Retained Messages**: Last message saved for new subscribers

### Topic Structure
```
building/{building_id}/{floor}/{zone}/{sensor_type}

Examples:
building/main/floor2/zone_a/temperature
building/main/floor1/hvac/setpoint
building/main/outdoor/weather
```

### MQTT Client Example
```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://broker.example.com:1883', {
  clientId: 'building_controller_001',
  username: 'iot_user',
  password: 'secure_password'
});

// Subscribe to topics
client.on('connect', () => {
  client.subscribe('building/+/+/+/temperature', { qos: 1 });
  client.subscribe('building/main/+/hvac/#', { qos: 2 });
});

// Publish sensor data
client.publish('building/main/floor2/zone_a/temperature', JSON.stringify({
  value: 72.5,
  unit: 'F',
  timestamp: new Date().toISOString()
}), { qos: 1, retain: true });
```

## BACnet (Building Automation and Control Networks)

### Object Types
| Object | Purpose | Example |
|--------|---------|---------|
| Analog Input | Sensor readings | Temperature, pressure |
| Analog Output | Control signals | Damper position, valve |
| Binary Input | On/off status | Door closed, alarm |
| Binary Output | On/off control | Relay, switch |
| Multi-State | Mode selection | Heat/Cool/Auto |

### BACnet Services
```python
# Read property
temperature = bacnet.read('Device:101 AnalogInput:1 present-value')

# Write property
bacnet.write('Device:101 AnalogValue:1 present-value 72.0')

# Subscribe to COV
bacnet.subscribe_cov('Device:101 AnalogInput:1', callback=on_temperature_change)
```

## Modbus

### Register Types
- **Coils** (00001-09999): Read/write bits
- **Discrete Inputs** (10001-19999): Read-only bits
- **Input Registers** (30001-39999): Read-only 16-bit
- **Holding Registers** (40001-49999): Read/write 16-bit

### Function Codes
- 01: Read Coils
- 03: Read Holding Registers
- 04: Read Input Registers
- 05: Write Single Coil
- 06: Write Single Register
- 16: Write Multiple Registers

## LoRaWAN (Long Range WAN)

### Characteristics
- **Range**: 2-15 km
- **Power**: Ultra-low, battery life years
- **Data Rate**: 0.3-50 kbps
- **Use Cases**: Outdoor sensors, remote monitoring

## See Also
- bacnet_reference.md
- sensor_types.md
