# Sensor Types Reference

Comprehensive guide to sensors used in smart building systems, including specifications, deployment strategies, and integration patterns.

## Temperature Sensors

### Thermistors (NTC/PTC)
- **Type**: Negative/Positive Temperature Coefficient resistors
- **Accuracy**: ±0.2°C to ±0.5°C
- **Range**: -40°C to 150°C (-40°F to 302°F)
- **Response Time**: 5-30 seconds
- **Cost**: $5-$25 per unit
- **Best For**: Room temperature, water temperature, surface monitoring
- **Advantages**: Low cost, high sensitivity, self-powered
- **Disadvantages**: Non-linear response, limited range, calibration drift over time

**Deployment Tips:**
- Mount away from direct sunlight and heat sources
- Install at breathing height (4-6 feet) for accurate room sensing
- Use weatherproof enclosures for outdoor applications
- Calibrate annually for critical applications

### RTD (Resistance Temperature Detector)
- **Type**: Platinum (PT100, PT1000), Nickel, Copper
- **Accuracy**: ±0.1°C to ±0.3°C
- **Range**: -200°C to 850°C (-328°F to 1562°F)
- **Response Time**: 1-50 seconds
- **Cost**: $50-$300 per unit
- **Best For**: HVAC systems, process control, critical environments
- **Advantages**: Excellent accuracy, stability, linear response
- **Disadvantages**: Higher cost, slower response, requires excitation current

**Common Configurations:**
- 2-wire: Budget applications, shorter cable runs
- 3-wire: Most common, compensates for lead resistance
- 4-wire: Highest accuracy, laboratory grade

### Thermocouples
- **Type**: K, J, T, E, N (various metal combinations)
- **Accuracy**: ±1°C to ±2°C
- **Range**: -270°C to 1372°C (-454°F to 2501°F)
- **Response Time**: 0.1-10 seconds
- **Cost**: $15-$100 per unit
- **Best For**: Boilers, chillers, extreme temperature monitoring
- **Advantages**: Wide temperature range, fast response, durable, self-powered
- **Disadvantages**: Lower accuracy, requires cold junction compensation

## Occupancy Sensors

### PIR (Passive Infrared)
- **Detection Method**: Infrared radiation from body heat
- **Coverage**: 20-2000 sq ft depending on mounting height
- **Field of View**: 90° to 360°
- **Detection Range**: 6-50 feet
- **Cost**: $20-$150
- **Power**: 12-24VDC, 0.5-2W
- **Best For**: Office spaces, conference rooms, restrooms

**Key Specifications:**
- **Sensitivity**: Adjustable to prevent false triggers
- **Time Delay**: 30 seconds to 30 minutes programmable
- **Dual Technology**: Often combined with ultrasonic for accuracy
- **False Positives**: HVAC air movement, sunlight, small animals

**Installation Guidelines:**
- Mount at 8-12 feet for optimal coverage
- Avoid direct view of windows or HVAC vents
- Consider occupant traffic patterns
- Use corner mounting for maximum coverage

### Ultrasonic Sensors
- **Detection Method**: High-frequency sound waves (25-40 kHz)
- **Coverage**: Up to 1000 sq ft
- **Detection**: Fine movements, breathing
- **Cost**: $50-$200
- **Best For**: Restrooms, cubicles, spaces with partitions

**Advantages:**
- Detects minor movements
- Works around corners and partitions
- Less affected by temperature changes

**Limitations:**
- More false positives
- Can be affected by soft surfaces
- Higher power consumption

### CO2-Based Occupancy
- **Detection Method**: CO2 concentration above baseline
- **Threshold**: Typically 100-200 ppm above ambient
- **Response Time**: 2-5 minutes
- **Accuracy**: ±50 ppm
- **Cost**: $200-$500
- **Best For**: Conference rooms, classrooms, high-density spaces

**Benefits:**
- True occupancy count estimation
- Supports demand-controlled ventilation
- No privacy concerns
- Very low false positives

## Air Quality Sensors

### CO2 Sensors (NDIR)
- **Technology**: Non-Dispersive Infrared
- **Range**: 0-5000 ppm (some up to 10,000 ppm)
- **Accuracy**: ±30-50 ppm or ±3% of reading
- **Response Time**: T90 < 60 seconds
- **Calibration**: ABC (Automatic Baseline Correction) or manual
- **Lifespan**: 10-15 years
- **Cost**: $100-$400

**Target Levels:**
- Outdoor: 400-450 ppm
- Good IAQ: <800 ppm
- Acceptable: 800-1000 ppm
- Poor: >1000 ppm
- ASHRAE 62.1 guideline: <1000 ppm

### VOC (Volatile Organic Compounds) Sensors
- **Technology**: Metal oxide semiconductor (MOX), PID
- **Measurement**: TVOC in ppb or mg/m³
- **Range**: 0-10,000 ppb
- **Compounds Detected**: Formaldehyde, benzene, toluene, cleaning chemicals
- **Cost**: $50-$300
- **Applications**: Indoor air quality, sick building syndrome detection

### Particulate Matter Sensors
- **Types**: PM1.0, PM2.5, PM10
- **Technology**: Laser scattering, optical particle counter
- **Range**: 0-1000 µg/m³
- **Accuracy**: ±10% at 100 µg/m³
- **Cost**: $30-$250
- **Health Impact**:
  - PM2.5 <12 µg/m³: Good
  - 12-35 µg/m³: Moderate
  - >35 µg/m³: Unhealthy for sensitive groups

### Humidity Sensors
- **Technology**: Capacitive, resistive
- **Range**: 0-100% RH
- **Accuracy**: ±2-3% RH
- **Operating Temperature**: -40°C to 85°C
- **Cost**: $10-$100
- **Target Range**: 30-60% RH for comfort and mold prevention

## Energy Meters

### Current Transformers (CT)
- **Type**: Split-core, solid-core, Rogowski coil
- **Ratios**: 100:5, 200:5, 500:5, up to 5000:5
- **Accuracy Class**: 0.5%, 1%, 3%, 5%
- **Cost**: $25-$300 per CT
- **Installation**: Non-invasive (split-core) or permanent (solid-core)
- **Applications**: Submetering, power monitoring, tenant billing

**Selection Criteria:**
- Match CT ratio to expected load
- Consider conductor size for split-core selection
- Class 0.5 for revenue-grade metering
- Class 1-3 for energy monitoring

### Smart Meters
- **Communication**: Modbus RTU/TCP, BACnet, M-Bus, wireless
- **Measurements**: kWh, kW, kVA, kVAR, power factor, harmonics
- **Accuracy**: Class 1 (1%) or Class 0.5 (0.5%)
- **Cost**: $200-$800
- **Features**: Time-of-use tracking, demand monitoring, data logging
- **Pulse Output**: 1-10,000 pulses/kWh

### Sub-Meters for Tenant Billing
- **Types**: kWh (electricity), BTU (thermal), cubic meters (water/gas)
- **Certification**: Revenue-grade (MID, ANSI C12.20)
- **Data Collection**: AMR (Automated Meter Reading), AMI (Advanced Metering Infrastructure)
- **Integration**: Building management system, tenant billing software

## Water Sensors

### Leak Detection Sensors
- **Types**:
  - Spot detectors (flood sensors)
  - Cable sensors (rope/tape, 3-300 feet)
  - Flow-based (abnormal flow patterns)
- **Technology**: Conductivity probes, capacitive
- **Response**: Audible alarm, relay output, network notification
- **Cost**: $20-$200 per point
- **Placement**: Under sinks, near water heaters, below pipes, mechanical rooms

**Wireless Leak Detectors:**
- Battery life: 3-5 years
- Range: 300-1000 feet
- Protocols: Z-Wave, Zigbee, LoRaWAN

### Flow Meters
- **Types**: Electromagnetic, turbine, ultrasonic, positive displacement
- **Applications**:
  - Domestic water measurement
  - Cooling tower makeup
  - Irrigation monitoring
- **Accuracy**: ±1-5% of reading
- **Communication**: Pulse output, 4-20mA, Modbus
- **Cost**: $100-$2000 depending on size and type

### Water Quality Sensors
- **Parameters**: pH, conductivity, temperature, TDS
- **Applications**: Cooling tower, domestic water, wastewater
- **Maintenance**: Monthly calibration, quarterly probe replacement
- **Cost**: $200-$1000 per parameter

## Light Sensors (Photosensors)

### Daylight Sensors
- **Type**: Silicon photodiode, photocell
- **Measurement**: Foot-candles (fc) or lux
- **Range**: 0-10,000 fc (0-100,000 lux)
- **Accuracy**: ±10-20%
- **Cost**: $50-$200
- **Applications**: Daylight harvesting, automated shade control

**Deployment Strategies:**
- Closed-loop: Sensor measures light at work surface
- Open-loop: Sensor measures daylight only (at window)
- Multi-zone control for perimeter vs. interior
- Integration with motorized shades

**Energy Savings:**
- Perimeter zones: 30-60% lighting energy reduction
- Interior daylight zones: 20-40% reduction
- ROI: Typically 2-5 years

### Outdoor Light Sensors (Photocells)
- **Type**: Photoresistor (CdS), photodiode
- **Purpose**: Dusk-to-dawn control for outdoor/parking lighting
- **Hysteresis**: 10-20 fc to prevent cycling
- **Fail-safe**: Default to ON on sensor failure
- **Cost**: $15-$75
- **NEMA ratings**: Type 3R or 4 for weather resistance

## Sensor Integration Protocols

### Common Communication Protocols
- **BACnet**: Building automation standard (MS/TP, IP)
- **Modbus**: Industrial standard (RTU, TCP)
- **MQTT**: Lightweight IoT protocol
- **LoRaWAN**: Long-range wireless (miles), low power
- **Zigbee/Z-Wave**: Short-range mesh networks
- **KNX**: European building automation standard

### Sensor Network Architecture
- **Star Topology**: Direct connections to central controller
- **Mesh Network**: Self-healing, redundant paths
- **Gateway Architecture**: Protocol conversion, edge processing
- **Cloud Integration**: Remote monitoring, analytics, ML

## Sensor Maintenance and Calibration

### Calibration Schedules
- **Temperature**: Annually for critical, bi-annually for general
- **CO2**: Auto-calibration (ABC) or manual every 1-2 years
- **Flow meters**: Annually or per manufacturer specs
- **Humidity**: Bi-annually
- **Energy meters**: Class 0.5 annually, Class 1 every 2 years

### Common Issues and Troubleshooting
- **Drift**: Regular calibration, sensor replacement
- **Environmental**: Dust, moisture, extreme temperatures
- **Communication**: Cable integrity, network configuration
- **Power**: Verify voltage, check power supplies
- **Placement**: Avoid heat sources, airflow disruption, direct sunlight

### Sensor Lifecycle Management
- **Typical Lifespan**: 5-15 years depending on type and environment
- **Replacement Indicators**: Calibration drift, communication errors, physical damage
- **Spare Parts**: Stock 10% spares for critical sensors
- **Documentation**: Maintain sensor inventory, calibration records, replacement history
