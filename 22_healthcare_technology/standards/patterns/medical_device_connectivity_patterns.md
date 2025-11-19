# Medical Device Connectivity Patterns

## Executive Summary

Production-grade patterns for integrating, managing, and orchestrating medical devices across healthcare ecosystems. Covers device protocols, data normalization, real-time monitoring, and regulatory compliance.

---

## Table of Contents

1. [Device Integration Patterns](#device-integration-patterns)
2. [Protocol Support](#protocol-support)
3. [Data Normalization](#data-normalization)
4. [Real-Time Monitoring](#real-time-monitoring)
5. [Device Management](#device-management)
6. [Security & Compliance](#security--compliance)
7. [Real-World Implementations](#real-world-implementations)

---

## Device Integration Patterns

### 1. Universal Device Gateway Pattern

**Pattern**: Single entry point for all medical devices, abstracting protocol differences.

**Implementation**:

```javascript
class UniversalDeviceGateway {
  constructor() {
    this.adapters = new Map();
    this.deviceRegistry = new Map();
    this.eventBus = new EventEmitter();
  }

  registerDeviceAdapter(deviceType, adapter) {
    this.adapters.set(deviceType, adapter);
  }

  async connectDevice(config) {
    const { deviceId, deviceType, model, protocol, connection } = config;

    const adapter = this.adapters.get(deviceType);
    if (!adapter) {
      throw new Error(`No adapter for device type: ${deviceType}`);
    }

    try {
      // Establish connection
      const connection = await adapter.connect(connection);

      // Register device
      const device = {
        id: deviceId,
        type: deviceType,
        model,
        protocol,
        connection,
        status: 'connected',
        connectedAt: new Date(),
        capabilities: adapter.getCapabilities()
      };

      this.deviceRegistry.set(deviceId, device);

      // Start data collection
      this.startDeviceListener(deviceId, adapter);

      // Emit connection event
      this.eventBus.emit('device.connected', {
        deviceId,
        deviceType,
        timestamp: new Date()
      });

      return device;
    } catch (error) {
      throw new Error(`Failed to connect device ${deviceId}: ${error.message}`);
    }
  }

  startDeviceListener(deviceId, adapter) {
    adapter.on('data', async (rawData) => {
      try {
        // Normalize device data
        const normalizedData = await this.normalizeDeviceData(
          deviceId,
          rawData
        );

        // Process and store
        await this.processDeviceData(deviceId, normalizedData);

        // Emit standardized event
        this.eventBus.emit('device.data', {
          deviceId,
          data: normalizedData,
          timestamp: new Date()
        });
      } catch (error) {
        this.handleDeviceDataError(deviceId, error);
      }
    });

    adapter.on('error', (error) => {
      this.handleDeviceError(deviceId, error);
    });

    adapter.on('disconnected', () => {
      this.handleDeviceDisconnection(deviceId);
    });
  }

  async normalizeDeviceData(deviceId, rawData) {
    const device = this.deviceRegistry.get(deviceId);
    const adapter = this.adapters.get(device.type);

    return adapter.normalizeData(rawData);
  }

  async processDeviceData(deviceId, data) {
    // Store in time-series database
    await TimeSeries.store({
      deviceId,
      data,
      timestamp: new Date(),
      retention: this.getRetentionPolicy(deviceId)
    });
  }

  handleDeviceError(deviceId, error) {
    const device = this.deviceRegistry.get(deviceId);
    device.status = 'error';
    device.lastError = error.message;
    device.lastErrorTime = new Date();

    this.eventBus.emit('device.error', {
      deviceId,
      error: error.message,
      timestamp: new Date()
    });

    // Attempt reconnection
    this.scheduleReconnection(deviceId);
  }

  handleDeviceDisconnection(deviceId) {
    const device = this.deviceRegistry.get(deviceId);
    device.status = 'disconnected';
    device.disconnectedAt = new Date();

    this.eventBus.emit('device.disconnected', {
      deviceId,
      timestamp: new Date()
    });

    this.scheduleReconnection(deviceId);
  }

  scheduleReconnection(deviceId, delayMs = 5000) {
    setTimeout(async () => {
      try {
        const device = this.deviceRegistry.get(deviceId);
        await this.connectDevice(device);
      } catch (error) {
        // Log and retry with exponential backoff
        this.scheduleReconnection(deviceId, delayMs * 2);
      }
    }, delayMs);
  }

  getRetentionPolicy(deviceId) {
    const device = this.deviceRegistry.get(deviceId);
    const policies = {
      'ECG': 30 * 24 * 3600,      // 30 days
      'Pulse-Oximeter': 7 * 24 * 3600,  // 7 days
      'Ventilator': 90 * 24 * 3600      // 90 days
    };
    return policies[device.type] || 24 * 3600;
  }
}
```

---

### 2. Device Adapter Pattern

**Pattern**: Create protocol-specific adapters that normalize different device communications.

**Implementation**:

```javascript
// Abstract base adapter
class BaseDeviceAdapter extends EventEmitter {
  async connect(config) {
    throw new Error('connect() must be implemented');
  }

  normalizeData(rawData) {
    throw new Error('normalizeData() must be implemented');
  }

  getCapabilities() {
    throw new Error('getCapabilities() must be implemented');
  }

  async disconnect() {
    throw new Error('disconnect() must be implemented');
  }
}

// HL7 v2 Adapter (Hospital Information System)
class HL7v2DeviceAdapter extends BaseDeviceAdapter {
  async connect(config) {
    this.socket = net.createConnection({
      host: config.host,
      port: config.port
    });

    this.socket.on('data', (buffer) => {
      const message = buffer.toString();
      this.parseHL7Message(message);
    });

    this.socket.on('error', (error) => {
      this.emit('error', error);
    });

    this.socket.on('close', () => {
      this.emit('disconnected');
    });

    return new Promise((resolve) => {
      this.socket.on('connect', () => resolve(this.socket));
    });
  }

  parseHL7Message(message) {
    // Remove MLLP framing characters
    const cleanMessage = message.replace(/[\x0B\x1C\x0D]/g, '');
    const segments = cleanMessage.split('\n');

    const data = {
      messageType: this.extractField(segments[0], 9, 1),
      patientId: this.extractField(segments[3], 2, 1),
      timestamp: this.extractField(segments[0], 7, 1),
      payload: {}
    };

    this.emit('data', data);
  }

  extractField(segment, fieldIndex, subFieldIndex = 1) {
    const fields = segment.split('|');
    if (fieldIndex >= fields.length) return null;

    const field = fields[fieldIndex];
    if (subFieldIndex > 1) {
      return field.split('^')[subFieldIndex - 1] || null;
    }
    return field;
  }

  normalizeData(rawData) {
    return {
      deviceId: rawData.deviceId,
      patientId: rawData.patientId,
      messageType: rawData.messageType,
      observations: this.extractObservations(rawData),
      timestamp: new Date(rawData.timestamp),
      raw: rawData
    };
  }

  extractObservations(data) {
    // Parse OBR/OBX segments to extract observations
    return [];
  }

  getCapabilities() {
    return {
      protocols: ['HL7v2'],
      supportedMessages: ['ORU', 'ADT', 'ORM'],
      encoding: 'ASCII',
      batchOperations: true
    };
  }
}

// DICOM Adapter (Medical Imaging)
class DICOMDeviceAdapter extends BaseDeviceAdapter {
  async connect(config) {
    this.dcm4chee = new DICOM.Client({
      host: config.host,
      port: config.port,
      applicationName: 'HealthcareGateway'
    });

    await this.dcm4chee.connect();

    // Setup DICOM event handlers
    this.dcm4chee.on('cstore', (dataset) => {
      this.emit('data', dataset);
    });

    return this.dcm4chee;
  }

  normalizeData(rawData) {
    const { dataset } = rawData;

    return {
      modality: dataset.getString(0x00080060),
      patientId: dataset.getString(0x00100020),
      studyDate: dataset.getDate(0x00080020),
      seriesInstanceUID: dataset.getString(0x0020000E),
      sopInstanceUID: dataset.getString(0x00080018),
      images: dataset.getItems(),
      timestamp: new Date()
    };
  }

  getCapabilities() {
    return {
      protocols: ['DICOM'],
      services: ['C-STORE', 'C-FIND', 'C-MOVE', 'C-GET'],
      mediaSupport: true
    };
  }
}

// Wireless Vital Signs Monitor (Proprietary Protocol)
class WirelessVitalsAdapter extends BaseDeviceAdapter {
  async connect(config) {
    this.mqtt = mqtt.connect(config.brokerUrl, {
      clientId: config.deviceId,
      username: config.username,
      password: config.password
    });

    this.mqtt.on('message', (topic, message) => {
      const data = JSON.parse(message.toString());
      this.emit('data', data);
    });

    await this.mqtt.subscribe(`device/${config.deviceId}/vitals`);

    return this.mqtt;
  }

  normalizeData(rawData) {
    return {
      deviceId: rawData.deviceId,
      patientId: rawData.patientId,
      vitals: {
        heartRate: rawData.hr,
        systolic: rawData.sbp,
        diastolic: rawData.dbp,
        spO2: rawData.spo2,
        temperature: rawData.temp
      },
      signalQuality: rawData.signal_quality,
      batteryLevel: rawData.battery,
      timestamp: new Date(rawData.timestamp)
    };
  }

  getCapabilities() {
    return {
      protocols: ['MQTT'],
      measurementTypes: ['ECG', 'Vitals', 'SpO2'],
      wireless: true,
      batteryOperated: true,
      recordingDuration: '24 hours'
    };
  }
}
```

---

## Protocol Support

### 3. Multi-Protocol Handler

**Pattern**: Unified interface for various healthcare device protocols.

**Implementation**:

```javascript
class ProtocolManager {
  constructor() {
    this.protocols = new Map();
  }

  registerProtocol(name, handler) {
    this.protocols.set(name, handler);
  }

  async communicateWithDevice(deviceId, command, options = {}) {
    const device = deviceRegistry.get(deviceId);
    const protocol = this.protocols.get(device.protocol);

    if (!protocol) {
      throw new Error(`Unsupported protocol: ${device.protocol}`);
    }

    return protocol.execute(device, command, options);
  }
}

// HL7 Protocol Handler
class HL7ProtocolHandler {
  execute(device, command, options) {
    const message = this.buildHL7Message(command, options);
    return this.sendHL7Message(device, message);
  }

  buildHL7Message(command, options) {
    const timestamp = new Date().toISOString().replace(/[^\d]/g, '');

    if (command === 'query-labs') {
      return `MSH|^~\\&|GATEWAY||LAB||${timestamp}||QRY^A19|||2.5
QRD|${timestamp}|R|I|||${options.patientId}||LAB`;
    }
  }

  async sendHL7Message(device, message) {
    return new Promise((resolve, reject) => {
      const ackTimeout = setTimeout(() => {
        reject(new Error('HL7 ACK timeout'));
      }, 5000);

      device.connection.write(`\x0B${message}\x1C\x0D`);

      device.connection.once('data', (data) => {
        clearTimeout(ackTimeout);
        resolve(this.parseHL7Response(data));
      });
    });
  }

  parseHL7Response(data) {
    // Parse response segments
    return { status: 'success' };
  }
}

// DICOM Protocol Handler
class DICOMProtocolHandler {
  execute(device, command, options) {
    if (command === 'find-studies') {
      return this.findStudies(device, options);
    } else if (command === 'retrieve-images') {
      return this.retrieveImages(device, options);
    }
  }

  async findStudies(device, { patientId, modality, dateRange }) {
    const query = {
      PatientID: patientId,
      Modality: modality,
      StudyDate: dateRange
    };

    return device.connection.find(query);
  }

  async retrieveImages(device, { studyUID, seriesUID }) {
    return device.connection.retrieve({
      StudyInstanceUID: studyUID,
      SeriesInstanceUID: seriesUID
    });
  }
}
```

---

## Data Normalization

### 4. Device Data Normalization Engine

**Pattern**: Convert device-specific formats to FHIR observations.

**Implementation**:

```javascript
class DeviceDataNormalizer {
  async normalizeToFHIR(deviceData) {
    const device = await this.getDeviceMetadata(deviceData.deviceId);

    const observations = deviceData.measurements.map(measurement => ({
      resourceType: 'Observation',
      status: 'final',
      category: [{ coding: [{ code: 'vital-signs' }] }],
      code: {
        coding: [
          {
            system: 'http://loinc.org',
            code: this.mapToLOINCCode(device.type, measurement.type),
            display: measurement.type
          }
        ]
      },
      subject: {
        reference: `Patient/${deviceData.patientId}`
      },
      effectiveDateTime: deviceData.timestamp.toISOString(),
      valueQuantity: {
        value: measurement.value,
        unit: measurement.unit,
        system: 'http://unitsofmeasure.org',
        code: this.mapToUCUMCode(measurement.unit)
      },
      device: {
        reference: `Device/${deviceData.deviceId}`
      },
      interpretation: [
        {
          coding: [
            {
              system: 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
              code: this.interpretValue(measurement)
            }
          ]
        }
      ]
    }));

    return observations;
  }

  mapToLOINCCode(deviceType, measurementType) {
    const mapping = {
      'ECG': { 'heart-rate': '8867-4' },
      'PulseOximeter': { 'spo2': '59408-5', 'heart-rate': '8867-4' },
      'BloodPressure': { 'systolic': '8480-6', 'diastolic': '8462-4' },
      'Thermometer': { 'temperature': '8310-5' }
    };

    return mapping[deviceType]?.[measurementType] || null;
  }

  mapToUCUMCode(unit) {
    const mapping = {
      'bpm': '/min',
      '%': '%',
      'mmHg': 'mm[Hg]',
      'C': 'Cel'
    };

    return mapping[unit] || unit;
  }

  interpretValue(measurement) {
    // Map numeric values to clinical interpretation
    if (measurement.type === 'spo2') {
      if (measurement.value >= 95) return 'N'; // Normal
      if (measurement.value >= 90) return 'L'; // Low
      return 'LL'; // Critical Low
    }
    return 'N';
  }

  async getDeviceMetadata(deviceId) {
    return deviceRegistry.get(deviceId);
  }
}

// Usage
const normalizer = new DeviceDataNormalizer();

const deviceData = {
  deviceId: 'pulse-ox-001',
  patientId: 'patient-123',
  measurements: [
    { type: 'spo2', value: 98, unit: '%' },
    { type: 'heart-rate', value: 72, unit: 'bpm' }
  ],
  timestamp: new Date()
};

const observations = await normalizer.normalizeToFHIR(deviceData);
// observations can now be stored as FHIR resources
```

---

## Real-Time Monitoring

### 5. Continuous Device Monitoring with Alerting

**Pattern**: Monitor device data streams and trigger alerts based on thresholds.

**Implementation**:

```javascript
class DeviceMonitoringService {
  constructor(eventBus, alertService) {
    this.eventBus = eventBus;
    this.alertService = alertService;
    this.monitors = new Map();
    this.thresholds = new Map();
  }

  registerMonitor(deviceId, monitorConfig) {
    this.monitors.set(deviceId, {
      config: monitorConfig,
      state: 'running',
      lastDataReceived: null,
      alertsTriggered: []
    });

    this.thresholds.set(deviceId, monitorConfig.thresholds);

    // Subscribe to device data
    this.eventBus.on(`device.data.${deviceId}`, (data) => {
      this.evaluateData(deviceId, data);
    });

    // Monitor for data gaps
    this.monitorDataGap(deviceId, monitorConfig.dataTimeout);
  }

  evaluateData(deviceId, data) {
    const thresholds = this.thresholds.get(deviceId);
    const monitor = this.monitors.get(deviceId);

    monitor.lastDataReceived = new Date();

    Object.entries(data.measurements).forEach(([key, value]) => {
      const threshold = thresholds[key];

      if (!threshold) return;

      // Check critical low
      if (value < threshold.criticalLow) {
        this.triggerAlert(deviceId, key, 'CRITICAL_LOW', value, threshold);
      }
      // Check warning low
      else if (value < threshold.low) {
        this.triggerAlert(deviceId, key, 'WARNING_LOW', value, threshold);
      }
      // Check warning high
      else if (value > threshold.high) {
        this.triggerAlert(deviceId, key, 'WARNING_HIGH', value, threshold);
      }
      // Check critical high
      else if (value > threshold.criticalHigh) {
        this.triggerAlert(deviceId, key, 'CRITICAL_HIGH', value, threshold);
      }
    });
  }

  async triggerAlert(deviceId, measurementType, severity, value, threshold) {
    const alert = {
      id: uuid(),
      deviceId,
      measurementType,
      severity,
      value,
      threshold,
      timestamp: new Date(),
      acknowledged: false
    };

    // Store alert
    await Alert.create(alert);

    // Send notifications
    if (severity === 'CRITICAL_LOW' || severity === 'CRITICAL_HIGH') {
      await this.alertService.notifyEmergency(alert);
    } else {
      await this.alertService.notifyWarning(alert);
    }

    // Emit event for real-time dashboards
    this.eventBus.emit('alert.triggered', alert);
  }

  monitorDataGap(deviceId, timeoutMs) {
    setInterval(() => {
      const monitor = this.monitors.get(deviceId);

      if (!monitor) return;

      const timeSinceLastData = Date.now() - monitor.lastDataReceived;

      if (timeSinceLastData > timeoutMs) {
        this.alertService.notifyDeviceError({
          deviceId,
          error: 'No data received',
          lastDataTime: monitor.lastDataReceived
        });
      }
    }, timeoutMs / 2);
  }
}

// Configuration example
const monitorConfig = {
  dataTimeout: 30000, // 30 seconds
  thresholds: {
    'heartRate': {
      criticalLow: 40,
      low: 50,
      high: 120,
      criticalHigh: 140
    },
    'spO2': {
      criticalLow: 85,
      low: 90,
      high: 100,
      criticalHigh: 100
    }
  }
};
```

---

## Device Management

### 6. Device Lifecycle Management

**Pattern**: Track device deployment, maintenance, and retirement.

**Implementation**:

```javascript
class DeviceLifecycleManager {
  async registerDevice(deviceInfo) {
    const device = {
      id: deviceInfo.id,
      serialNumber: deviceInfo.serialNumber,
      model: deviceInfo.model,
      manufacturer: deviceInfo.manufacturer,
      type: deviceInfo.type,
      location: deviceInfo.location,
      status: 'active',
      registeredAt: new Date(),
      calibrationDueDate: this.calculateNextCalibration(),
      maintenanceSchedule: this.getMaintenanceSchedule(deviceInfo.type),
      firmwareVersion: deviceInfo.firmwareVersion,
      lastChecked: null,
      alerts: []
    };

    await Device.create(device);
    return device;
  }

  async scheduleCalibration(deviceId, dueDate) {
    const device = await Device.findById(deviceId);
    device.calibrationDueDate = dueDate;
    device.calibrationScheduled = true;

    await device.save();

    // Notify biomedical team
    await Notification.send({
      type: 'CALIBRATION_DUE',
      deviceId,
      dueDate
    });
  }

  async recordMaintenance(deviceId, maintenanceRecord) {
    await MaintenanceLog.create({
      deviceId,
      ...maintenanceRecord,
      performedAt: new Date(),
      performedBy: maintenanceRecord.technician
    });

    const device = await Device.findById(deviceId);
    device.lastMaintenance = new Date();
    await device.save();
  }

  async updateFirmware(deviceId, firmwareVersion) {
    const device = await Device.findById(deviceId);

    // Schedule firmware update
    await FirmwareUpdate.schedule({
      deviceId,
      newVersion: firmwareVersion,
      scheduledFor: new Date(Date.now() + 3600000) // In 1 hour
    });

    // Notify affected units/departments
    const affectedUnits = await Unit.findByDevice(deviceId);
    affectedUnits.forEach(unit => {
      Notification.send({
        type: 'FIRMWARE_UPDATE_SCHEDULED',
        deviceId,
        newVersion: firmwareVersion,
        unitId: unit.id
      });
    });
  }

  async decommissionDevice(deviceId, reason) {
    const device = await Device.findById(deviceId);
    device.status = 'decommissioned';
    device.decommissionedAt = new Date();
    device.decommissionReason = reason;

    await device.save();

    // Archive device data
    await this.archiveDeviceData(deviceId);
  }

  calculateNextCalibration() {
    const nextDate = new Date();
    nextDate.setMonth(nextDate.getMonth() + 12);
    return nextDate;
  }

  getMaintenanceSchedule(deviceType) {
    const schedules = {
      'ECG': { frequency: 'quarterly', requiredTasks: ['electrode check', 'calibration'] },
      'PulseOximeter': { frequency: 'bi-annual', requiredTasks: ['sensor check'] },
      'Ventilator': { frequency: 'monthly', requiredTasks: ['pressure check', 'filter'] }
    };

    return schedules[deviceType];
  }
}
```

---

## Security & Compliance

### 7. Device Security & Authentication

**Implementation**:

```javascript
class DeviceSecurityManager {
  async authenticateDevice(deviceId, certificate) {
    const device = await Device.findById(deviceId);

    // Verify certificate chain
    const isValid = await this.verifyCertificate(certificate);
    if (!isValid) {
      throw new Error('Invalid device certificate');
    }

    // Check certificate not revoked
    const isRevoked = await this.checkCertificateRevocation(certificate);
    if (isRevoked) {
      throw new Error('Device certificate revoked');
    }

    // Generate session token
    const token = jwt.sign({
      deviceId,
      deviceType: device.type,
      serialNumber: device.serialNumber
    }, process.env.DEVICE_KEY, { expiresIn: '24h' });

    return token;
  }

  async verifyDeviceMessage(deviceId, message, signature) {
    const device = await Device.findById(deviceId);
    const publicKey = await this.getDevicePublicKey(device);

    return crypto.verify('sha256', message, publicKey, signature);
  }

  async encryptDeviceData(deviceId, data) {
    const device = await Device.findById(deviceId);
    const publicKey = await this.getDevicePublicKey(device);

    return crypto.publicEncrypt(publicKey, Buffer.from(JSON.stringify(data)));
  }

  async verifyCertificate(certificate) {
    // Verify certificate signature
    // Check certificate validity dates
    // Check certificate usage constraints
    return true;
  }

  async checkCertificateRevocation(certificate) {
    // Check against CRL (Certificate Revocation List)
    // Or use OCSP (Online Certificate Status Protocol)
    return false;
  }

  getDevicePublicKey(device) {
    // Retrieve from secure storage
    return KeyVault.get(`device.${device.id}.public_key`);
  }
}
```

---

## Real-World Implementations

### Example 1: ICU Monitoring Setup

```javascript
async function setupICUMonitoring(patientId, icuBedNumber) {
  // Connect vital signs monitor
  const vitalsDevice = await gateway.connectDevice({
    deviceId: `vitals-icu-${icuBedNumber}`,
    deviceType: 'WirelessVitalsMonitor',
    model: 'Philips IntelliVue',
    protocol: 'MQTT',
    connection: {
      brokerUrl: 'mqtt://icu-gateway:1883',
      deviceId: `vitals-icu-${icuBedNumber}`
    }
  });

  // Connect ventilator
  const ventilator = await gateway.connectDevice({
    deviceId: `vent-icu-${icuBedNumber}`,
    deviceType: 'Ventilator',
    model: 'Maquet Servo-u',
    protocol: 'HL7v2',
    connection: {
      host: 'ventilator-gateway',
      port: 2575
    }
  });

  // Register monitors
  const vitalsMonitor = new DeviceMonitoringService();
  vitalsMonitor.registerMonitor(vitalsDevice.id, {
    dataTimeout: 10000,
    thresholds: {
      heartRate: { criticalLow: 30, low: 50, high: 130, criticalHigh: 150 },
      spO2: { criticalLow: 85, low: 90, high: 100, criticalHigh: 100 },
      systolic: { criticalLow: 80, low: 100, high: 160, criticalHigh: 200 }
    }
  });

  // Setup data normalization
  const normalizer = new DeviceDataNormalizer();
  gateway.eventBus.on('device.data', async (event) => {
    const fhirObservations = await normalizer.normalizeToFHIR(event.data);
    await FHIRStore.saveObservations(fhirObservations);
  });

  return {
    patientId,
    devices: [vitalsDevice, ventilator],
    monitoringActive: true
  };
}
```

### Example 2: Radiology DICOM Integration

```javascript
async function integrateDICOMSystem(hospitalDepartment) {
  // Connect DICOM imaging system
  const dicomSystem = await gateway.connectDevice({
    deviceId: `pacs-${hospitalDepartment}`,
    deviceType: 'PACS',
    model: 'Agfa Impax',
    protocol: 'DICOM',
    connection: {
      host: 'dicom-server.hospital.local',
      port: 104,
      aet: 'HEALTHCARE_GW'
    }
  });

  // Listen for new studies
  gateway.eventBus.on('device.data', async (event) => {
    if (event.data.modality === 'CT' || event.data.modality === 'MR') {
      // Normalize to FHIR ImagingStudy
      const imagingStudy = {
        resourceType: 'ImagingStudy',
        subject: { reference: `Patient/${event.data.patientId}` },
        modality: event.data.modality,
        studyInstanceUID: event.data.studyInstanceUID,
        series: event.data.images
      };

      await FHIRStore.saveImagingStudy(imagingStudy);

      // Trigger analysis workflow
      await WorkflowEngine.startStudyAnalysis(imagingStudy);
    }
  });
}
```

---

## Summary

Medical device connectivity requires:
- Universal integration via adapters
- Protocol-agnostic communication
- FHIR normalization for interoperability
- Real-time monitoring and alerting
- Device lifecycle management
- Security and compliance enforcement

These patterns enable scalable, secure, and interoperable device ecosystems in healthcare.
