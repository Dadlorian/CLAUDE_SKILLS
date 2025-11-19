# Smart Building Systems

## Overview

Smart building systems integrate IoT sensors, automation, and data analytics to optimize building operations, energy efficiency, and occupant comfort. This skill covers BACnet protocol, HVAC control, occupancy sensors, energy management, and predictive maintenance for commercial and residential properties.

## Key Concepts

### Building Automation Systems (BAS)

**Components**:
- HVAC controllers
- Lighting control systems
- Access control and security
- Energy monitoring
- Occupancy sensors
- Building Management System (BMS) software

**Protocols**:
- **BACnet**: Standard protocol for building automation
- **Modbus**: Industrial protocol for device communication
- **MQTT**: Lightweight IoT messaging protocol
- **LonWorks**: Legacy building automation protocol

### IoT Sensor Network

**Sensor Types**:
- **Temperature/Humidity**: Climate monitoring
- **Occupancy**: PIR, ultrasonic, CO2-based detection
- **Energy**: Power consumption, demand monitoring
- **Air Quality**: CO2, VOC, particulate matter
- **Water**: Leak detection, flow monitoring
- **Light**: Daylight harvesting, occupancy-based control

**Network Architecture**:
```
Sensors → Gateways → Edge Computing → Cloud Platform → Analytics/Control
```

### BACnet Protocol

**BACnet Objects**:
- Analog Input (AI): Temperature, pressure sensors
- Analog Output (AO): Damper positions, valve control
- Analog Value (AV): Setpoints, calculated values
- Binary Input (BI): Switch states, alarms
- Binary Output (BO): Relay control
- Multi-State: Mode selection (auto/manual)

**BACnet Services**:
- ReadProperty: Read device values
- WriteProperty: Control devices
- SubscribeCOV: Subscribe to change notifications
- WhoIs/I-Am: Device discovery

### HVAC Control

**Control Strategies**:
- **Setpoint Control**: Maintain target temperature
- **Scheduled Control**: Time-based operation
- **Demand Control Ventilation**: CO2-based fresh air
- **Economizer Control**: Free cooling when outdoor temp permits
- **Variable Air Volume (VAV)**: Zone-based airflow control

**Energy Optimization**:
- Pre-cooling/heating during off-peak hours
- Optimal start/stop algorithms
- Night setback temperatures
- Daylight harvesting
- Demand response participation

### Energy Management

**Monitoring**:
- Real-time power consumption
- Peak demand tracking
- Energy by zone/tenant
- Renewable generation (solar)
- Battery storage status

**Analytics**:
- Energy benchmarking
- Anomaly detection
- Load forecasting
- Cost optimization
- Carbon footprint tracking

## Industry Tools & Platforms

### BMS Platforms
- **Tridium Niagara** - Leading BAS platform
- **Honeywell Forge** - Cloud-based building management
- **Johnson Controls Metasys** - Enterprise BAS
- **Siemens Desigo CC** - Building automation
- **Schneider Electric EcoStruxure** - IoT-enabled platform

### IoT Platforms
- **AWS IoT Core** - Cloud IoT platform
- **Azure IoT Hub** - Microsoft IoT services
- **Google Cloud IoT** - Google's IoT platform
- **ThingWorx** - Industrial IoT platform

### Energy Management
- **EnergyCAP** - Energy management software
- **Lucid BuildingOS** - Building performance platform
- **eSight** - Energy analytics
- **Pulse Energy** - Real-time energy monitoring

### Sensors & Hardware
- **Particle** - IoT hardware platform
- **Disruptive Technologies** - Wireless sensors
- **Enlighted** - Occupancy and energy sensors
- **Verdigris** - AI-powered energy sensors

## Implementation Patterns

### Sensor Data Pipeline

```javascript
// MQTT sensor data ingestion
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
  client.subscribe('building/+/temperature');
  client.subscribe('building/+/occupancy');
});

client.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  processSensorData(topic, data);
});

async function processSensorData(topic, data) {
  // Parse topic (e.g., building/floor2_room201/temperature)
  const [, location, sensorType] = topic.split('/');

  // Store in time-series database
  await influx.writePoints([{
    measurement: sensorType,
    tags: { location },
    fields: { value: data.value },
    timestamp: new Date()
  }]);

  // Check for anomalies
  if (sensorType === 'temperature' && (data.value < 60 || data.value > 80)) {
    await sendAlert({
      type: 'temperature_anomaly',
      location,
      value: data.value
    });
  }
}
```

### BACnet Integration

```python
# BACnet device communication
import BAC0

# Connect to BACnet network
bacnet = BAC0.connect(ip='192.168.1.10/24')

# Discover devices
bacnet.whois()

# Read temperature from device
device = bacnet.read('101:1 analogInput 1 presentValue')
temp = device

# Write setpoint
bacnet.write('101:1 analogValue 1 presentValue 72')

# Subscribe to COV (Change of Value)
bacnet.subscribe('101:1 analogInput 1 presentValue')
```

### Occupancy-Based Control

```javascript
const controlHVAC = async (zoneId, occupancyData) => {
  const zone = await db.zones.findByPk(zoneId);

  if (occupancyData.occupied) {
    // Occupied mode
    await setTemperature(zoneId, zone.occupied_setpoint);
    await setLighting(zoneId, zone.occupied_lighting_level);
  } else {
    // Check if recently vacated
    const minutesSinceVacated = (Date.now() - occupancyData.last_occupied) / 60000;

    if (minutesSinceVacated > 30) {
      // Unoccupied mode
      await setTemperature(zoneId, zone.unoccupied_setpoint);
      await setLighting(zoneId, 0); // Off
    }
  }
};
```

### Predictive Maintenance

```python
# Detect HVAC anomalies using ML
import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_hvac_anomalies(equipment_id):
    # Get historical data
    data = db.query(f"""
        SELECT timestamp, supply_temp, return_temp,
               power_consumption, runtime_hours
        FROM hvac_data
        WHERE equipment_id = {equipment_id}
        AND timestamp > NOW() - INTERVAL '30 days'
    """)

    df = pd.DataFrame(data)

    # Feature engineering
    df['temp_diff'] = df['supply_temp'] - df['return_temp']
    df['efficiency'] = df['power_consumption'] / df['runtime_hours']

    # Anomaly detection
    features = ['supply_temp', 'return_temp', 'temp_diff', 'efficiency']
    model = IsolationForest(contamination=0.1)
    df['anomaly'] = model.fit_predict(df[features])

    # Alert on anomalies
    anomalies = df[df['anomaly'] == -1]
    if len(anomalies) > 5:
        create_maintenance_ticket(equipment_id, 'Potential issue detected')

    return anomalies
```

## Performance Metrics

| Metric | Target | Industry Avg |
|--------|--------|--------------|
| Energy savings | 20-30% | 15% |
| HVAC uptime | > 99% | 95% |
| Sensor data latency | < 5 sec | 15 sec |
| Maintenance cost reduction | 15-25% | 10% |
| Occupant satisfaction | > 85% | 70% |

## Best Practices

### System Design
1. **Layered Architecture**: Separate sensors, controllers, and analytics
2. **Redundancy**: Backup controllers and networks
3. **Security**: Encrypted communication, network segmentation
4. **Scalability**: Design for future expansion
5. **Interoperability**: Use open protocols (BACnet, MQTT)

### Energy Optimization
1. **Zoning**: Control areas independently
2. **Scheduling**: Align with occupancy patterns
3. **Setpoint Optimization**: Balance comfort and efficiency
4. **Demand Response**: Participate in utility programs
5. **Monitoring**: Track and analyze continuously

### Data Management
1. **Time-Series Database**: Use InfluxDB or TimescaleDB
2. **Data Retention**: Archive old data, keep recent hot
3. **Aggregation**: Pre-compute hourly/daily metrics
4. **Backup**: Regular backups of configuration and data

## Common Challenges

**Integration Complexity**
- Multiple protocols and vendors
- Legacy systems without API
- Solution: Use middleware/gateways

**Network Reliability**
- Wireless interference
- Cable failures
- Solution: Redundant networks, monitoring

**Cybersecurity**
- Vulnerable IoT devices
- Solution: Network segmentation, regular updates

**Data Overload**
- Millions of sensor readings
- Solution: Edge processing, aggregation

## Resources

### Standards
- ASHRAE 135 (BACnet)
- ISO 16484 (Building Automation)
- LEED Certification
- Energy Star Portfolio Manager

### Learning
- BACnet International Training
- Building Automation Monthly (publication)
- Smart Buildings Magazine
- IBCON (conference)

## Related Skills
- 01_property_management_systems
- 04_real_estate_analytics
- 09_construction_tech

## Version History
- 1.0.0 - Initial smart building systems documentation
