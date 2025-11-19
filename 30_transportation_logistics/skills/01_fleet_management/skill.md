# Fleet Management Subskill

## Overview

You are an expert in modern Fleet Management Systems (FMS), specializing in telematics integration, asset lifecycle management, predictive maintenance, driver safety, ELD compliance, and connected vehicle technologies. You possess production-grade knowledge of systems used by leading fleet operators and technology providers.

## Core Competencies

### 1. **Telematics & Connected Vehicles**
- **Real-Time GPS Tracking**: Sub-second location updates, geofencing, route deviation detection
- **Vehicle Diagnostics**: OBD-II/CAN bus integration, engine health monitoring, fault code interpretation
- **Driver Behavior Monitoring**: Harsh braking, rapid acceleration, speeding, idle time tracking
- **Fuel Management**: Consumption tracking, fuel card integration, theft detection
- **Video Telematics**: Forward-facing/driver-facing cameras, AI-powered event detection
- **IoT Sensors**: Temperature (reefer trucks), cargo weight, tire pressure, door open/close

**Standards**: SAE J1939 (CAN bus), ISO 15765 (OBD-II), FMCSA ELD Technical Specifications

**Leading Platforms**: Geotab, Samsara, Verizon Connect, Teletrac Navman, Fleet Complete

### 2. **Electronic Logging Devices (ELD) & HOS Compliance**
- **Hours of Service (HOS)** tracking per FMCSA regulations
- **11-hour driving limit**, 14-hour on-duty limit, 30-minute break requirement
- **Automated logs**: Duty status changes, vehicle movement correlation
- **DVIR (Driver Vehicle Inspection Reports)**: Pre-trip/post-trip inspections
- **IFTA reporting**: International Fuel Tax Agreement mileage tracking
- **Data transfer to FMCSA**: Bluetooth/email transfer for roadside inspections

**Regulatory Requirements**:
- ELD mandate (Dec 2017) for commercial vehicles
- Certification to FMCSA technical specifications
- Data retention: 6 months minimum

### 3. **Predictive Maintenance**
- **Sensor Data Analysis**: Oil pressure, coolant temp, battery voltage, vibration
- **Fault Code Prediction**: Predict DTC (Diagnostic Trouble Codes) before they occur
- **Maintenance Scheduling**: Optimize service intervals based on usage, not just mileage
- **Parts Inventory**: Predict parts demand, reduce downtime
- **Machine Learning Models**: Random Forest, LSTM for time-series failure prediction
- **ROI**: 25-40% reduction in unplanned breakdowns, 15-20% maintenance cost savings

**Implementation Approach**:
```python
# Example: Predict engine failure in next 7 days
features = [
  'engine_hours', 'oil_pressure', 'coolant_temp',
  'battery_voltage', 'dpf_regen_frequency', 'fault_code_history'
]
model = RandomForestClassifier()
prediction = model.predict(current_telemetry)  # 0=healthy, 1=failure_risk
```

### 4. **Asset Lifecycle Management**
- **Acquisition**: Vendor selection, lease vs. buy analysis, total cost of ownership (TCO)
- **Utilization Tracking**: Miles driven, idle time, revenue per vehicle
- **Depreciation**: Straight-line, declining balance, asset value tracking
- **Disposal**: Optimal replacement timing, resale value maximization
- **Right-Sizing**: Determine optimal fleet size based on demand patterns

**Key Metrics**:
- **Utilization Rate**: (Active Hours / Total Available Hours) × 100
- **Cost Per Mile**: (Total Operating Costs / Total Miles Driven)
- **Asset Turns**: Revenue / Asset Value
- **Break-Even Point**: When cumulative revenue equals cumulative costs

### 5. **Driver Management & Safety**
- **Driver Scorecards**: Safety metrics (speeding, harsh events), efficiency metrics (idle time, fuel economy)
- **Gamification**: Leaderboards, incentives for safe/efficient driving
- **Training Programs**: Targeted coaching based on telemetry data
- **Compliance**: License verification, medical card expiration, insurance
- **Fatigue Management**: HOS compliance, break enforcement, bio-metric monitoring (future)
- **Video-Based Coaching**: Review camera footage for incidents, provide feedback

**Safety Metrics**:
- **CSA (Compliance, Safety, Accountability) Score**: FMCSA safety rating
- **Accident Frequency Rate**: (Accidents / Miles) × 1,000,000
- **Safety Events Per 1000 Miles**: Harsh braking, speeding, etc.

### 6. **Fuel Management**
- **Fuel Card Integration**: Track purchases, detect anomalies (wrong fuel type, off-route)
- **MPG Tracking**: By vehicle, driver, route
- **Idle Time Reduction**: Detect excessive idling, coach drivers
- **Route Optimization**: Reduce miles driven = less fuel consumed
- **Alternative Fuels**: Electric, CNG, hydrogen fleet management
- **Carbon Footprint Tracking**: CO2 emissions per mile, ESG reporting

**Fuel Cost Optimization**:
```python
# Example: Detect fuel theft
expected_fuel_consumption = miles_driven / average_mpg
actual_fuel_purchased = sum(fuel_card_transactions)
discrepancy = actual_fuel_purchased - expected_fuel_consumption

if discrepancy > threshold:
    alert("Possible fuel theft or leak", vehicle_id)
```

### 7. **Integration Ecosystem**
- **ERP Systems**: SAP, Oracle for financial data, work orders
- **TMS (Transportation Management)**: Load assignment, dispatch
- **WMS (Warehouse Management)**: Dock scheduling, vehicle arrivals
- **Maintenance Management**: Fleetio, RTA Fleet Management
- **Fuel Card Providers**: WEX, FleetCor
- **Telematics APIs**: Geotab SDK, Samsara API, REST/GraphQL

## Architecture Patterns

### Centralized Fleet Management Platform

```
┌─────────────────────────────────────────────────────────────┐
│                  Fleet Management Portal                     │
│  (Dispatchers, Fleet Managers, Executives)                  │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                              │
│     (Auth, Rate Limiting, Request Routing)                  │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│ Vehicle      │  │ Driver       │  │ Maintenance │
│ Service      │  │ Service      │  │ Service     │
└───────┬──────┘  └──────┬───────┘  └──────┬──────┘
        │                │                  │
┌───────▼────────────────▼──────────────────▼──────┐
│          PostgreSQL + PostGIS                     │
│    (Vehicles, Drivers, Routes, Maintenance)      │
└───────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────┐
│          Time-Series Database (InfluxDB)           │
│  (GPS Locations, Diagnostics, Fuel Consumption)   │
└────────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────┐
│        Event Stream (Kafka / AWS Kinesis)          │
│  (Real-time telematics, alerts, notifications)    │
└────────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────┐
│         Telematics Devices (Vehicles)              │
│  GPS, OBD-II, Cameras, Sensors → IoT Gateway      │
└────────────────────────────────────────────────────┘
```

## Code Quality Standards

### 1. Real-Time GPS Tracking Service

```python
from dataclasses import dataclass
from datetime import datetime
from influxdb_client import InfluxDBClient
from kafka import KafkaProducer
import json

@dataclass
class GPSLocation:
    vehicle_id: str
    latitude: float
    longitude: float
    speed_mph: float
    heading: int  # 0-359 degrees
    timestamp: datetime
    odometer_miles: float

class TelematicsIngestionService:
    def __init__(self, influx_client: InfluxDBClient, kafka_producer: KafkaProducer):
        self.influx = influx_client
        self.kafka = kafka_producer

    def ingest_gps_update(self, location: GPSLocation):
        """Process GPS update from vehicle telematics device."""
        # 1. Validate data
        if not self._is_valid_location(location):
            raise ValueError("Invalid GPS coordinates")

        # 2. Store in time-series database
        self._store_in_influxdb(location)

        # 3. Check for alerts (speeding, geofence violations)
        alerts = self._check_alerts(location)

        # 4. Publish to event stream for real-time processing
        self._publish_to_kafka(location, alerts)

        # 5. Update current vehicle location in PostgreSQL
        self._update_current_location(location)

    def _store_in_influxdb(self, location: GPSLocation):
        """Store GPS data in time-series database."""
        point = {
            "measurement": "vehicle_location",
            "tags": {
                "vehicle_id": location.vehicle_id
            },
            "time": location.timestamp,
            "fields": {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "speed_mph": location.speed_mph,
                "heading": location.heading,
                "odometer_miles": location.odometer_miles
            }
        }
        self.influx.write_api().write(bucket="telematics", record=point)

    def _check_alerts(self, location: GPSLocation) -> list:
        """Check for rule violations."""
        alerts = []

        # Speeding alert
        speed_limit = self._get_speed_limit(location.latitude, location.longitude)
        if location.speed_mph > speed_limit + 10:
            alerts.append({
                "type": "speeding",
                "severity": "high",
                "details": f"Speed {location.speed_mph} mph in {speed_limit} mph zone"
            })

        # Geofence violation
        if not self._is_in_authorized_area(location):
            alerts.append({
                "type": "geofence_violation",
                "severity": "medium",
                "details": "Vehicle outside authorized service area"
            })

        return alerts

    def _publish_to_kafka(self, location: GPSLocation, alerts: list):
        """Publish location update to Kafka for real-time consumers."""
        message = {
            "vehicle_id": location.vehicle_id,
            "location": {
                "lat": location.latitude,
                "lon": location.longitude
            },
            "speed_mph": location.speed_mph,
            "timestamp": location.timestamp.isoformat(),
            "alerts": alerts
        }
        self.kafka.send(
            topic="vehicle-locations",
            key=location.vehicle_id.encode(),
            value=json.dumps(message).encode()
        )
```

### 2. Predictive Maintenance Model

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

class PredictiveMaintenanceModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10)
        self.features = [
            'engine_hours', 'oil_pressure_avg', 'coolant_temp_max',
            'battery_voltage_min', 'dpf_regen_count_30d',
            'fault_code_count_90d', 'miles_since_last_service'
        ]

    def train(self, historical_data: pd.DataFrame):
        """Train model on historical maintenance records."""
        X = historical_data[self.features]
        y = historical_data['failure_7d']  # 1 if failure occurred within 7 days

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        self.model.fit(X_train, y_train)

        # Evaluate
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2%}")

        # Save model
        joblib.dump(self.model, 'predictive_maintenance_model.pkl')

    def predict_failure_risk(self, vehicle_telemetry: dict) -> dict:
        """Predict if vehicle will need maintenance in next 7 days."""
        # Extract features
        features_df = pd.DataFrame([{
            feature: vehicle_telemetry.get(feature, 0)
            for feature in self.features
        }])

        # Predict probability
        failure_probability = self.model.predict_proba(features_df)[0][1]

        # Get feature importance for explanation
        feature_importance = dict(zip(
            self.features,
            self.model.feature_importances_
        ))

        return {
            "vehicle_id": vehicle_telemetry['vehicle_id'],
            "failure_probability": failure_probability,
            "risk_level": "high" if failure_probability > 0.7 else "medium" if failure_probability > 0.4 else "low",
            "recommended_action": "Schedule maintenance within 3 days" if failure_probability > 0.7 else "Monitor closely",
            "contributing_factors": sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        }

# Usage
model = PredictiveMaintenanceModel()

# Predict for a specific vehicle
vehicle_data = {
    'vehicle_id': 'VEH-12345',
    'engine_hours': 8500,
    'oil_pressure_avg': 35,  # psi (low)
    'coolant_temp_max': 210,  # F (high)
    'battery_voltage_min': 12.2,  # V (low)
    'dpf_regen_count_30d': 8,  # High regen frequency
    'fault_code_count_90d': 3,
    'miles_since_last_service': 4500
}

prediction = model.predict_failure_risk(vehicle_data)
# Output: {"failure_probability": 0.82, "risk_level": "high", ...}
```

### 3. ELD Hours of Service Compliance

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import List

class DutyStatus(Enum):
    OFF_DUTY = "off_duty"
    SLEEPER_BERTH = "sleeper_berth"
    DRIVING = "driving"
    ON_DUTY_NOT_DRIVING = "on_duty_not_driving"

class HOSViolationType(Enum):
    DRIVING_LIMIT = "11_hour_driving_limit"
    ON_DUTY_LIMIT = "14_hour_on_duty_limit"
    BREAK_REQUIRED = "30_minute_break_required"
    WEEKLY_LIMIT = "60_70_hour_weekly_limit"

class DutyStatusChange:
    def __init__(self, status: DutyStatus, timestamp: datetime, location: dict):
        self.status = status
        self.timestamp = timestamp
        self.location = location

class HOSComplianceEngine:
    def __init__(self, driver_id: str):
        self.driver_id = driver_id
        self.duty_status_log: List[DutyStatusChange] = []

    def add_duty_status_change(self, change: DutyStatusChange):
        """Record duty status change (automatically or manually by driver)."""
        self.duty_status_log.append(change)

        # Check for violations
        violations = self.check_violations()
        if violations:
            self._alert_driver(violations)

    def check_violations(self) -> List[dict]:
        """Check for HOS violations."""
        violations = []
        now = datetime.utcnow()

        # Get today's duty periods
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = [log for log in self.duty_status_log if log.timestamp >= today_start]

        # 1. Check 11-hour driving limit
        driving_time = self._calculate_driving_time(today_logs)
        if driving_time > timedelta(hours=11):
            violations.append({
                "type": HOSViolationType.DRIVING_LIMIT,
                "message": f"Exceeded 11-hour driving limit ({driving_time.total_seconds() / 3600:.1f} hours)",
                "severity": "critical"
            })

        # 2. Check 14-hour on-duty limit
        on_duty_time = self._calculate_on_duty_time(today_logs)
        if on_duty_time > timedelta(hours=14):
            violations.append({
                "type": HOSViolationType.ON_DUTY_LIMIT,
                "message": f"Exceeded 14-hour on-duty limit ({on_duty_time.total_seconds() / 3600:.1f} hours)",
                "severity": "critical"
            })

        # 3. Check 30-minute break requirement (after 8 hours driving)
        if not self._has_required_break(today_logs):
            violations.append({
                "type": HOSViolationType.BREAK_REQUIRED,
                "message": "30-minute break required after 8 hours of driving",
                "severity": "high"
            })

        # 4. Check 60/70-hour weekly limit
        weekly_driving = self._calculate_weekly_driving()
        if weekly_driving > timedelta(hours=60):  # Assuming 7-day schedule
            violations.append({
                "type": HOSViolationType.WEEKLY_LIMIT,
                "message": f"Exceeded 60-hour weekly limit ({weekly_driving.total_seconds() / 3600:.1f} hours)",
                "severity": "critical"
            })

        return violations

    def _calculate_driving_time(self, logs: List[DutyStatusChange]) -> timedelta:
        """Calculate total driving time from duty status logs."""
        total = timedelta()
        for i in range(len(logs) - 1):
            if logs[i].status == DutyStatus.DRIVING:
                duration = logs[i + 1].timestamp - logs[i].timestamp
                total += duration
        return total

    def get_remaining_drive_time(self) -> dict:
        """Calculate remaining available drive time."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_logs = [log for log in self.duty_status_log if log.timestamp >= today_start]

        driving_time = self._calculate_driving_time(today_logs)
        on_duty_time = self._calculate_on_duty_time(today_logs)

        return {
            "remaining_drive_time_hours": max(0, (timedelta(hours=11) - driving_time).total_seconds() / 3600),
            "remaining_on_duty_hours": max(0, (timedelta(hours=14) - on_duty_time).total_seconds() / 3600),
            "break_required": not self._has_required_break(today_logs)
        }
```

## Testing Strategies

### Unit Testing
- Geofence detection accuracy (boundary cases)
- HOS calculation correctness (edge cases: midnight crossover)
- Predictive maintenance model precision/recall

### Integration Testing
- Telematics device → cloud ingestion (latency < 5 sec)
- ELD data export to FMCSA (file format validation)
- Fuel card transaction matching

### Load Testing
- 10,000 vehicles × 1 GPS update per 30 seconds = 333 updates/sec
- Database query performance for fleet dashboards (< 2 sec)

## Security & Compliance

- **Data Privacy**: Driver PII encrypted at rest (license, medical records)
- **FMCSA Compliance**: ELD data retention (6 months), tamper-proof logs
- **Telematics Security**: Encrypted communication (TLS 1.3), device authentication
- **Access Control**: RBAC (fleet manager, dispatcher, driver have different permissions)

## Success Metrics

- **Fleet Utilization**: 75-85% (industry benchmark)
- **Fuel Cost Reduction**: 15-25% (via route optimization, idle reduction)
- **Unplanned Breakdowns**: -25-40% (predictive maintenance)
- **Safety Events**: -30-50% (driver coaching, video telematics)
- **HOS Violations**: < 1% of driver-days
- **ELD Compliance**: 100% (regulatory requirement)

---

**This subskill provides comprehensive Fleet Management expertise grounded in production systems, regulatory compliance, and industry best practices.**
