# IoMT Device Integration Guide

## Comprehensive guide for integrating Internet of Medical Things devices into telehealth platforms, including device selection, data ingestion, and clinical workflows.

## Table of Contents
1. [IoMT Device Types](#iomt-device-types)
2. [Connectivity Protocols](#connectivity-protocols)
3. [Data Ingestion Architecture](#data-ingestion-architecture)
4. [FHIR Integration](#fhir-integration)
5. [Alert Configuration](#alert-configuration)
6. [Clinical Dashboards](#clinical-dashboards)
7. [Device Management](#device-management)
8. [Security and Compliance](#security-and-compliance)

## IoMT Device Types

### Common Remote Patient Monitoring Devices
```yaml
device_categories:
  vital_signs:
    - Blood pressure monitors
    - Pulse oximeters
    - Thermometers
    - Weight scales
    - Heart rate monitors

  chronic_disease_management:
    - Glucose monitors (CGM)
    - INR monitors (warfarin)
    - Peak flow meters (asthma)
    - Spirometers (COPD)

  cardiac_monitoring:
    - ECG monitors
    - Holter monitors
    - Implantable cardiac devices
    - Wearable cardiac sensors

  activity_tracking:
    - Fitness trackers
    - Fall detection sensors
    - Gait analysis devices
    - Sleep monitors

device_selection_criteria:
  clinical:
    - Clinical accuracy validation
    - FDA clearance/approval
    - Evidence-based use cases
    - Clinician adoption

  technical:
    - Connectivity options (Bluetooth, cellular, WiFi)
    - Battery life
    - API availability
    - Data format standards
    - Integration complexity

  patient:
    - Ease of use
    - Patient acceptance
    - Cost/insurance coverage
    - Support resources
```

## Connectivity Protocols

### Bluetooth Low Energy Integration
```javascript
// BLE device integration for patient mobile app
class BLEDeviceIntegration {
  constructor() {
    this.connectedDevices = new Map();
    this.supportedServices = {
      bloodPressure: '0x1810',
      glucoseMonitor: '0x1808',
      pulseOximeter: '0x1822',
      weightScale: '0x181D',
      thermometer: '0x1809'
    };
  }

  async scanForDevices(serviceUUIDs = null) {
    try {
      const device = await navigator.bluetooth.requestDevice({
        filters: this.getDeviceFilters(serviceUUIDs),
        optionalServices: Object.values(this.supportedServices)
      });

      return await this.connectDevice(device);
    } catch (error) {
      console.error('Device scan failed:', error);
      throw new Error(`Failed to find device: ${error.message}`);
    }
  }

  async connectDevice(device) {
    const server = await device.gatt.connect();

    // Discover services and characteristics
    const services = await server.getPrimaryServices();
    const deviceProfile = {
      id: device.id,
      name: device.name,
      type: this.identifyDeviceType(services),
      services: await this.mapServices(services),
      connected: true,
      lastSync: new Date()
    };

    this.connectedDevices.set(device.id, deviceProfile);

    // Set up notifications for measurements
    await this.setupNotifications(deviceProfile);

    return deviceProfile;
  }

  async setupNotifications(deviceProfile) {
    for (const service of deviceProfile.services) {
      for (const characteristic of service.characteristics) {
        if (characteristic.properties.notify) {
          await characteristic.startNotifications();

          characteristic.addEventListener('characteristicvaluechanged',
            (event) => this.handleMeasurement(event, deviceProfile));
        }
      }
    }
  }

  handleMeasurement(event, deviceProfile) {
    const value = event.target.value;
    const measurement = this.parseMeasurement(value, deviceProfile.type);

    // Send to backend
    this.uploadMeasurement({
      deviceId: deviceProfile.id,
      deviceType: deviceProfile.type,
      measurement: measurement,
      timestamp: new Date(),
      patientId: this.getPatientId()
    });
  }

  parseMeasurement(dataView, deviceType) {
    switch (deviceType) {
      case 'BLOOD_PRESSURE':
        return {
          systolic: dataView.getUint16(1, true),
          diastolic: dataView.getUint16(3, true),
          meanArterialPressure: dataView.getUint16(5, true),
          unit: 'mmHg'
        };

      case 'GLUCOSE':
        return {
          value: dataView.getFloat32(1, true),
          unit: 'mg/dL',
          mealContext: this.parseMealContext(dataView.getUint8(5))
        };

      case 'PULSE_OXIMETER':
        return {
          spo2: dataView.getUint8(1),
          pulseRate: dataView.getUint16(2, true),
          unit: '%'
        };

      default:
        return {raw: new Uint8Array(dataView.buffer)};
    }
  }
}
```

### Cellular IoT Gateway
```python
# Cellular gateway for devices without Bluetooth/WiFi
from mqtt import Client as MQTTClient
import json
from datetime import datetime

class CellularIoTGateway:
    def __init__(self):
        self.mqtt_broker = 'iot.healthcare.com'
        self.mqtt_port = 8883  # TLS
        self.client = MQTTClient()
        self.setup_mqtt_client()

    def setup_mqtt_client(self):
        """Configure MQTT client with TLS and auth"""
        self.client.tls_set(
            ca_certs='/path/to/ca.crt',
            certfile='/path/to/client.crt',
            keyfile='/path/to/client.key'
        )
        self.client.username_pw_set('gateway', 'secure_password')
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        """Subscribe to device topics on connect"""
        print(f'Connected to MQTT broker: {rc}')

        # Subscribe to all device telemetry
        self.client.subscribe('devices/+/telemetry')
        self.client.subscribe('devices/+/alerts')
        self.client.subscribe('devices/+/status')

    def on_message(self, client, userdata, msg):
        """Handle incoming device messages"""
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split('/')

            device_id = topic_parts[1]
            message_type = topic_parts[2]

            if message_type == 'telemetry':
                self.process_telemetry(device_id, payload)
            elif message_type == 'alerts':
                self.process_alert(device_id, payload)
            elif message_type == 'status':
                self.update_device_status(device_id, payload)

        except Exception as e:
            print(f'Error processing message: {e}')
            self.log_error(msg.topic, msg.payload, e)

    def process_telemetry(self, device_id, data):
        """Process and store device telemetry"""
        # Enrich with metadata
        telemetry = {
            'device_id': device_id,
            'patient_id': self.get_patient_id(device_id),
            'timestamp': datetime.fromisoformat(data['timestamp']),
            'measurements': data['measurements'],
            'device_metadata': {
                'battery_level': data.get('battery'),
                'signal_strength': data.get('signal'),
                'firmware_version': data.get('firmware')
            }
        }

        # Validate measurements
        if self.validate_measurements(telemetry['measurements']):
            # Store in time-series database
            self.store_telemetry(telemetry)

            # Check for alert conditions
            self.check_alert_conditions(telemetry)
        else:
            self.log_invalid_measurement(telemetry)

    def check_alert_conditions(self, telemetry):
        """Evaluate measurements against alert thresholds"""
        patient_id = telemetry['patient_id']
        thresholds = self.get_patient_thresholds(patient_id)

        for measurement_type, value in telemetry['measurements'].items():
            threshold = thresholds.get(measurement_type)
            if threshold:
                if value < threshold['min'] or value > threshold['max']:
                    self.trigger_alert({
                        'patient_id': patient_id,
                        'device_id': telemetry['device_id'],
                        'measurement_type': measurement_type,
                        'value': value,
                        'threshold': threshold,
                        'severity': threshold['severity'],
                        'timestamp': telemetry['timestamp']
                    })
```

## Data Ingestion Architecture

### High-Throughput Data Pipeline
```python
# Scalable data ingestion for thousands of devices
from kafka import KafkaProducer, KafkaConsumer
import asyncio
from typing import Dict, Any

class IoMTDataPipeline:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka1:9092', 'kafka2:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip'
        )

    async def ingest_measurement(self, measurement: Dict[str, Any]):
        """Ingest device measurement into pipeline"""

        # Validate measurement schema
        validated = await self.validate_schema(measurement)

        # Enrich with additional context
        enriched = await self.enrich_measurement(validated)

        # Route to appropriate topic based on device type
        topic = f"iomt.{enriched['device_type']}.measurements"

        # Publish to Kafka
        future = self.producer.send(
            topic,
            key=enriched['patient_id'].encode('utf-8'),
            value=enriched
        )

        # Wait for acknowledgment
        try:
            record_metadata = await asyncio.wrap_future(future)
            return {
                'status': 'success',
                'partition': record_metadata.partition,
                'offset': record_metadata.offset
            }
        except Exception as e:
            # Retry logic or dead letter queue
            await self.handle_ingestion_failure(measurement, e)
            raise

    async def enrich_measurement(self, measurement: Dict[str, Any]):
        """Enrich measurement with patient and device metadata"""
        patient_data = await self.get_patient_data(measurement['patient_id'])
        device_data = await self.get_device_data(measurement['device_id'])

        return {
            **measurement,
            'patient_metadata': {
                'age': patient_data['age'],
                'conditions': patient_data['active_conditions'],
                'care_team': patient_data['care_team_ids']
            },
            'device_metadata': {
                'manufacturer': device_data['manufacturer'],
                'model': device_data['model'],
                'calibration_date': device_data['last_calibration']
            },
            'processing_timestamp': datetime.now().isoformat()
        }

class IoMTDataProcessor:
    """Process ingested IoMT data"""

    def __init__(self):
        self.consumer = KafkaConsumer(
            'iomt.*.measurements',
            bootstrap_servers=['kafka1:9092'],
            group_id='iomt-processor',
            auto_offset_reset='earliest'
        )

    async def process_measurements(self):
        """Process measurements from Kafka"""
        for message in self.consumer:
            measurement = json.loads(message.value.decode('utf-8'))

            # Parallel processing
            await asyncio.gather(
                self.store_in_timeseries_db(measurement),
                self.update_fhir_observation(measurement),
                self.evaluate_clinical_rules(measurement),
                self.update_realtime_dashboard(measurement)
            )
```

## FHIR Integration

### Convert Device Data to FHIR Observations
```python
# Convert IoMT measurements to FHIR Observations
from fhir.resources.observation import Observation
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

class FHIRDeviceObservationMapper:
    def __init__(self):
        self.loinc_codes = {
            'blood_pressure_systolic': '8480-6',
            'blood_pressure_diastolic': '8462-4',
            'heart_rate': '8867-4',
            'spo2': '59408-5',
            'glucose': '2339-0',
            'weight': '29463-7',
            'temperature': '8310-5'
        }

    def create_observation(self, measurement: dict) -> Observation:
        """Create FHIR Observation from device measurement"""

        observation = Observation(
            status='final',
            category=[CodeableConcept(
                coding=[Coding(
                    system='http://terminology.hl7.org/CodeSystem/observation-category',
                    code='vital-signs',
                    display='Vital Signs'
                )]
            )],
            code=self.get_loinc_code(measurement['type']),
            subject={'reference': f"Patient/{measurement['patient_id']}"},
            effectiveDateTime=measurement['timestamp'],
            device={'reference': f"Device/{measurement['device_id']}"},
            valueQuantity=Quantity(
                value=measurement['value'],
                unit=measurement['unit'],
                system='http://unitsofmeasure.org',
                code=self.get_ucum_code(measurement['unit'])
            )
        )

        # Add components for multi-value measurements (e.g., blood pressure)
        if measurement['type'] == 'blood_pressure':
            observation.component = [
                {
                    'code': self.get_loinc_code('blood_pressure_systolic'),
                    'valueQuantity': Quantity(
                        value=measurement['systolic'],
                        unit='mmHg',
                        system='http://unitsofmeasure.org',
                        code='mm[Hg]'
                    )
                },
                {
                    'code': self.get_loinc_code('blood_pressure_diastolic'),
                    'valueQuantity': Quantity(
                        value=measurement['diastolic'],
                        unit='mmHg',
                        system='http://unitsofmeasure.org',
                        code='mm[Hg]'
                    )
                }
            ]

        return observation

    def get_loinc_code(self, measurement_type: str) -> CodeableConcept:
        """Get LOINC code for measurement type"""
        loinc_code = self.loinc_codes.get(measurement_type)

        return CodeableConcept(
            coding=[Coding(
                system='http://loinc.org',
                code=loinc_code,
                display=self.get_loinc_display(loinc_code)
            )]
        )
```

## Alert Configuration

### Clinical Alert Engine
```javascript
// Real-time alert processing for IoMT data
class ClinicalAlertEngine {
  constructor() {
    this.alertRules = new Map();
    this.alertCooldowns = new Map();
  }

  async configurePatientAlerts(patientId, conditions) {
    const rules = [];

    // Configure alerts based on patient conditions
    if (conditions.includes('DIABETES')) {
      rules.push({
        measurement: 'glucose',
        critical_low: {value: 70, severity: 'CRITICAL', action: 'IMMEDIATE_CALL'},
        low: {value: 80, severity: 'WARNING', action: 'NOTIFY'},
        high: {value: 250, severity: 'WARNING', action: 'NOTIFY'},
        critical_high: {value: 300, severity: 'CRITICAL', action: 'IMMEDIATE_CALL'},
        consecutive_readings: 2
      });
    }

    if (conditions.includes('HEART_FAILURE')) {
      rules.push({
        measurement: 'weight',
        threshold: {
          type: 'INCREASE',
          value: 3,  // pounds
          timeframe: '24_HOURS',
          severity: 'HIGH',
          action: 'NOTIFY_PROVIDER'
        }
      });
    }

    if (conditions.includes('HYPERTENSION')) {
      rules.push({
        measurement: 'blood_pressure',
        systolic_high: {value: 180, severity: 'CRITICAL'},
        diastolic_high: {value: 120, severity: 'CRITICAL'},
        consecutive_high_readings: 3
      });
    }

    this.alertRules.set(patientId, rules);
    return rules;
  }

  async evaluateMeasurement(patientId, measurement) {
    const rules = this.alertRules.get(patientId);
    if (!rules) return;

    for (const rule of rules) {
      if (rule.measurement === measurement.type) {
        const alertTriggered = await this.checkRule(rule, measurement, patientId);

        if (alertTriggered) {
          await this.triggerAlert(alertTriggered);
        }
      }
    }
  }

  async checkRule(rule, measurement, patientId) {
    // Check for critical thresholds
    if (rule.critical_low && measurement.value <= rule.critical_low.value) {
      return {
        patientId,
        type: 'CRITICAL_LOW',
        measurement: rule.measurement,
        value: measurement.value,
        threshold: rule.critical_low.value,
        severity: rule.critical_low.severity,
        action: rule.critical_low.action
      };
    }

    if (rule.critical_high && measurement.value >= rule.critical_high.value) {
      return {
        patientId,
        type: 'CRITICAL_HIGH',
        measurement: rule.measurement,
        value: measurement.value,
        threshold: rule.critical_high.value,
        severity: rule.critical_high.severity,
        action: rule.critical_high.action
      };
    }

    // Check for trend-based alerts
    if (rule.threshold && rule.threshold.type === 'INCREASE') {
      const historicalData = await this.getHistoricalData(
        patientId,
        rule.measurement,
        rule.threshold.timeframe
      );

      const increase = measurement.value - historicalData[0].value;
      if (increase >= rule.threshold.value) {
        return {
          patientId,
          type: 'TREND_ALERT',
          measurement: rule.measurement,
          currentValue: measurement.value,
          previousValue: historicalData[0].value,
          increase: increase,
          severity: rule.threshold.severity,
          action: rule.threshold.action
        };
      }
    }

    return null;
  }

  async triggerAlert(alert) {
    // Check cooldown to prevent alert fatigue
    const cooldownKey = `${alert.patientId}-${alert.type}`;
    if (this.alertCooldowns.has(cooldownKey)) {
      const lastAlert = this.alertCooldowns.get(cooldownKey);
      const timeSinceLastAlert = Date.now() - lastAlert;

      if (timeSinceLastAlert < 3600000) { // 1 hour cooldown
        console.log('Alert suppressed due to cooldown');
        return;
      }
    }

    // Execute alert action
    switch (alert.action) {
      case 'IMMEDIATE_CALL':
        await this.initiatePhoneCall(alert);
        break;
      case 'NOTIFY_PROVIDER':
        await this.notifyProvider(alert);
        break;
      case 'NOTIFY':
        await this.sendNotification(alert);
        break;
    }

    // Record alert
    await this.recordAlert(alert);
    this.alertCooldowns.set(cooldownKey, Date.now());
  }
}
```

## Clinical Dashboards

### Real-time Patient Monitoring Dashboard
```javascript
// React component for provider dashboard
import React, {useState, useEffect} from 'react';
import {Line, Gauge} from 'recharts';

const IoMTPatientDashboard = ({patientId}) => {
  const [realtimeData, setRealtimeData] = useState({});
  const [historicalData, setHistoricalData] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(`wss://api.hospital.com/iomt/stream/${patientId}`);

    ws.onmessage = (event) => {
      const measurement = JSON.parse(event.data);
      updateRealtimeData(measurement);
    };

    return () => ws.close();
  }, [patientId]);

  const updateRealtimeData = (measurement) => {
    setRealtimeData(prev => ({
      ...prev,
      [measurement.type]: {
        value: measurement.value,
        timestamp: measurement.timestamp,
        trend: calculateTrend(measurement)
      }
    }));

    // Add to historical data
    setHistoricalData(prev => [...prev, measurement].slice(-100));
  };

  return (
    <div className="iomt-dashboard">
      <div className="current-vitals">
        <VitalCard
          title="Blood Pressure"
          value={`${realtimeData.systolic}/${realtimeData.diastolic}`}
          unit="mmHg"
          timestamp={realtimeData.blood_pressure?.timestamp}
          trend={realtimeData.blood_pressure?.trend}
        />

        <VitalCard
          title="SpO2"
          value={realtimeData.spo2?.value}
          unit="%"
          gauge={true}
          min={85}
          max={100}
          timestamp={realtimeData.spo2?.timestamp}
        />

        <VitalCard
          title="Glucose"
          value={realtimeData.glucose?.value}
          unit="mg/dL"
          timestamp={realtimeData.glucose?.timestamp}
          trend={realtimeData.glucose?.trend}
        />
      </div>

      <div className="historical-trends">
        <TrendChart
          data={historicalData}
          measurements={['blood_pressure', 'glucose', 'weight']}
          timeRange="7_DAYS"
        />
      </div>

      <div className="alerts-panel">
        <AlertList alerts={alerts} onAcknowledge={acknowledgeAlert} />
      </div>
    </div>
  );
};
```

## Device Management

### Device Lifecycle Management
```python
# Comprehensive device management system
class IoMTDeviceManager:
    def __init__(self):
        self.device_registry = {}

    async def provision_device(self, device_info: dict, patient_id: str):
        """Provision new IoMT device for patient"""
        device = {
            'device_id': self.generate_device_id(),
            'patient_id': patient_id,
            'device_type': device_info['type'],
            'manufacturer': device_info['manufacturer'],
            'model': device_info['model'],
            'serial_number': device_info['serial_number'],
            'firmware_version': device_info['firmware_version'],
            'provisioned_date': datetime.now(),
            'status': 'ACTIVE',
            'last_communication': None,
            'calibration_due': self.calculate_calibration_date(device_info['type'])
        }

        # Generate device credentials
        credentials = await self.generate_device_credentials(device['device_id'])
        device['credentials'] = credentials

        # Register in device registry
        await self.register_device(device)

        # Assign to patient
        await self.assign_to_patient(device['device_id'], patient_id)

        # Send provisioning instructions to patient
        await self.send_setup_instructions(device, patient_id)

        return device

    async def monitor_device_health(self, device_id: str):
        """Monitor device connectivity and health"""
        device = await self.get_device(device_id)

        health_checks = {
            'connectivity': await self.check_connectivity(device_id),
            'battery_level': await self.get_battery_level(device_id),
            'data_quality': await self.assess_data_quality(device_id),
            'firmware_current': await self.check_firmware_version(device_id),
            'calibration_status': await self.check_calibration_status(device_id)
        }

        # Trigger maintenance if needed
        if not health_checks['calibration_status']:
            await self.schedule_calibration(device_id)

        if health_checks['battery_level'] < 20:
            await self.notify_low_battery(device_id)

        return health_checks
```

## Security and Compliance

### Device Security Framework
```yaml
security_requirements:
  authentication:
    - Device certificate-based authentication
    - Unique device credentials
    - Regular credential rotation (90 days)

  encryption:
    - TLS 1.3 for data in transit
    - AES-256 for data at rest
    - End-to-end encryption for sensitive measurements

  access_control:
    - Device-level access policies
    - Patient consent required for data sharing
    - Provider access audit logging

  compliance:
    - FDA medical device regulations
    - HIPAA security and privacy rules
    - ISO 27001 information security
    - IEC 62304 medical device software

  monitoring:
    - Anomaly detection for unusual data patterns
    - Security event logging
    - Incident response procedures
```
