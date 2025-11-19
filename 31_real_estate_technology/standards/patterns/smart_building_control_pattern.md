# Smart Building Control Pattern

**Version:** 2.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**References:** ASHRAE Guideline 36, AWS IoT, Azure Digital Twins, Honeywell Forge

## Table of Contents

1. [Overview](#overview)
2. [Edge Computing for Real-Time Control](#edge-computing-for-real-time-control)
3. [Cloud-Edge Hybrid Architecture](#cloud-edge-hybrid-architecture)
4. [Occupancy-Based HVAC Control](#occupancy-based-hvac-control)
5. [Predictive Maintenance with ML](#predictive-maintenance-with-ml)
6. [Energy Optimization Strategies](#energy-optimization-strategies)
7. [Building Digital Twin Patterns](#building-digital-twin-patterns)

## Overview

Smart building control systems optimize energy efficiency, occupant comfort, and operational efficiency through real-time data collection, analytics, and automated control.

### Control System Architecture

```
Sensors → Edge Gateway → Local Control Loop (real-time)
                    ↓
         Cloud Analytics Platform (insights, optimization)
                    ↓
         Control Adjustments → Edge Gateway → Actuators
```

## Edge Computing for Real-Time Control

### Edge Control Loop

**Why Edge:** HVAC control requires sub-second response times. Cloud round-trip (50-500ms) is too slow.

**Pattern:** Process control logic at the edge, send analytics to cloud

```python
class EdgeControlLoop:
    """
    Real-time control loop running on edge device (Raspberry Pi, IoT gateway)
    """

    def __init__(self, update_interval_seconds=10):
        self.update_interval = update_interval_seconds
        self.running = False

    def start(self):
        """
        Start control loop
        """
        self.running = True

        while self.running:
            # Read sensor values
            current_temp = self.read_temperature_sensor()
            current_humidity = self.read_humidity_sensor()
            occupancy = self.read_occupancy_sensor()
            co2_level = self.read_co2_sensor()

            # Get setpoints (cached locally, updated from cloud periodically)
            setpoint_temp = self.get_temperature_setpoint()
            setpoint_co2 = self.get_co2_setpoint()

            # Control logic
            hvac_command = self.calculate_hvac_command(
                current_temp=current_temp,
                setpoint_temp=setpoint_temp,
                occupancy=occupancy,
                co2_level=co2_level
            )

            # Execute control
            self.send_hvac_command(hvac_command)

            # Log data (batch send to cloud every 5 minutes)
            self.log_sensor_data(current_temp, current_humidity, occupancy, co2_level)

            # Sleep until next iteration
            time.sleep(self.update_interval)

    def calculate_hvac_command(self, current_temp, setpoint_temp, occupancy, co2_level):
        """
        PID control for HVAC
        """
        # Temperature error
        error = setpoint_temp - current_temp

        # PID gains
        Kp = 2.0  # Proportional
        Ki = 0.1  # Integral
        Kd = 0.5  # Derivative

        # Calculate control output
        proportional = Kp * error
        integral = Ki * self.integral_term
        derivative = Kd * (error - self.previous_error)

        output = proportional + integral + derivative

        # Update state
        self.integral_term += error
        self.previous_error = error

        # Clamp output
        output = max(0, min(100, output))  # 0-100% valve position

        # Occupancy override
        if occupancy == 0:
            # Setback mode (reduce cooling/heating)
            output *= 0.5

        # CO2 override (increase ventilation)
        if co2_level > 1000:  # ppm
            output = max(output, 50)  # Minimum 50% to increase fresh air

        return {
            "mode": "auto",
            "cooling_valve": output if error > 0 else 0,
            "heating_valve": -output if error < 0 else 0,
            "fan_speed": self.calculate_fan_speed(output)
        }

    def calculate_fan_speed(self, valve_position):
        """
        Map valve position to fan speed
        """
        if valve_position < 10:
            return "off"
        elif valve_position < 30:
            return "low"
        elif valve_position < 70:
            return "medium"
        else:
            return "high"
```

### AWS IoT Greengrass Deployment

```python
import greengrasssdk
import json

# Initialize Greengrass SDK
iot_client = greengrasssdk.client('iot-data')

def lambda_handler(event, context):
    """
    Greengrass Lambda function for local HVAC control
    """
    # Read local sensor values (via MQTT subscribe)
    sensor_data = event

    # Local control logic
    hvac_command = calculate_hvac_command(sensor_data)

    # Publish command locally (no cloud round-trip)
    iot_client.publish(
        topic='building/hvac/zone1/command',
        payload=json.dumps(hvac_command)
    )

    # Also send to cloud for analytics (async)
    iot_client.publish(
        topic='$aws/rules/sendToCloud',
        payload=json.dumps({
            "timestamp": time.time(),
            "sensor_data": sensor_data,
            "hvac_command": hvac_command
        })
    )

    return {"statusCode": 200}
```

## Cloud-Edge Hybrid Architecture

### Cloud Responsibilities

**Functions handled in the cloud:**
1. Long-term data storage and analytics
2. Machine learning model training
3. Energy optimization algorithms
4. Reporting and dashboards
5. Predictive maintenance models
6. Setpoint optimization (updated hourly/daily)

### Edge Responsibilities

**Functions handled at the edge:**
1. Real-time control loops (sub-second)
2. Local data buffering (network outage resilience)
3. Immediate fault detection
4. Safety interlocks
5. Sensor data preprocessing

### Sync Pattern

```python
class CloudEdgeSync:
    """
    Synchronize setpoints and control parameters between cloud and edge
    """

    def __init__(self, cloud_api, edge_gateway):
        self.cloud_api = cloud_api
        self.edge_gateway = edge_gateway

    def sync_setpoints_from_cloud(self):
        """
        Pull optimized setpoints from cloud (every hour)
        """
        # Get optimized setpoints from cloud
        optimized_setpoints = self.cloud_api.get_optimized_setpoints()

        # Push to edge gateway
        for zone_id, setpoint in optimized_setpoints.items():
            self.edge_gateway.update_setpoint(zone_id, setpoint)

    def sync_sensor_data_to_cloud(self):
        """
        Push sensor data batch to cloud (every 5 minutes)
        """
        # Get buffered sensor data from edge
        sensor_data_batch = self.edge_gateway.get_sensor_data_buffer()

        # Upload to cloud
        if sensor_data_batch:
            self.cloud_api.upload_sensor_data(sensor_data_batch)

            # Clear buffer
            self.edge_gateway.clear_sensor_data_buffer()

    def handle_network_outage(self):
        """
        Edge continues operating autonomously during network outage
        """
        # Edge uses last known good setpoints
        # Local control continues uninterrupted
        # Data buffered locally (up to 24 hours)

        # When network restored:
        if self.cloud_api.is_connected():
            # Upload buffered data
            self.sync_sensor_data_to_cloud()

            # Get latest setpoints
            self.sync_setpoints_from_cloud()
```

## Occupancy-Based HVAC Control

### Occupancy Detection

```python
class OccupancyBasedControl:
    """
    Adjust HVAC based on real-time occupancy
    """

    def __init__(self):
        self.occupancy_sensors = self.load_occupancy_sensors()

    def get_zone_occupancy(self, zone_id):
        """
        Get current occupancy count for zone
        """
        sensors = [s for s in self.occupancy_sensors if s.zone_id == zone_id]

        # Aggregate occupancy from multiple sensors
        total_occupancy = sum(s.get_occupancy_count() for s in sensors)

        return total_occupancy

    def adjust_hvac_for_occupancy(self, zone_id):
        """
        Adjust HVAC setpoints based on occupancy
        """
        occupancy = self.get_zone_occupancy(zone_id)
        base_setpoint = self.get_base_setpoint(zone_id)

        # Occupancy-based adjustments
        if occupancy == 0:
            # Unoccupied: setback mode (save energy)
            setpoint = base_setpoint + 4 if self.is_cooling_season() else base_setpoint - 4
            fan_mode = "low"
            damper_position = "minimum"  # Minimum fresh air

        elif occupancy < 5:
            # Light occupancy: reduce conditioning
            setpoint = base_setpoint + 2 if self.is_cooling_season() else base_setpoint - 2
            fan_mode = "medium"
            damper_position = "partial"

        else:
            # Normal/high occupancy: comfort priority
            setpoint = base_setpoint
            fan_mode = "auto"
            damper_position = "auto"

        # Update HVAC
        self.update_hvac_setpoint(zone_id, setpoint, fan_mode, damper_position)

        return {
            "occupancy": occupancy,
            "setpoint": setpoint,
            "fan_mode": fan_mode,
            "energy_savings": self.estimate_energy_savings(occupancy)
        }

    def estimate_energy_savings(self, occupancy):
        """
        Estimate energy savings from occupancy-based control
        """
        if occupancy == 0:
            return "30-50% savings (unoccupied setback)"
        elif occupancy < 5:
            return "10-20% savings (reduced load)"
        else:
            return "0% (comfort priority)"
```

### Predictive Occupancy

```python
class PredictiveOccupancy:
    """
    Predict future occupancy to pre-condition spaces
    """

    def __init__(self, ml_model):
        self.model = ml_model

    def predict_occupancy(self, zone_id, timestamp):
        """
        Predict occupancy for zone at future timestamp
        """
        features = self.extract_features(zone_id, timestamp)

        # ML model prediction
        predicted_occupancy = self.model.predict(features)

        return predicted_occupancy

    def extract_features(self, zone_id, timestamp):
        """
        Extract features for occupancy prediction
        """
        return {
            "day_of_week": timestamp.weekday(),
            "hour_of_day": timestamp.hour,
            "is_holiday": self.is_holiday(timestamp.date()),
            "historical_avg_occupancy": self.get_historical_avg(zone_id, timestamp),
            "calendar_events": self.get_calendar_events(zone_id, timestamp)
        }

    def pre_condition_space(self, zone_id, target_timestamp):
        """
        Pre-condition space before predicted occupancy
        """
        predicted_occupancy = self.predict_occupancy(zone_id, target_timestamp)

        if predicted_occupancy > 10:
            # High occupancy predicted
            # Start conditioning 30 minutes early
            precondition_time = target_timestamp - timedelta(minutes=30)

            # Schedule pre-conditioning
            self.schedule_precondition(
                zone_id=zone_id,
                start_time=precondition_time,
                target_temp=self.get_comfort_setpoint(zone_id)
            )
```

## Predictive Maintenance with ML

### Anomaly Detection

```python
import numpy as np
from sklearn.ensemble import IsolationForest

class PredictiveMaintenance:
    """
    Predict equipment failures using ML
    """

    def __init__(self):
        self.model = IsolationForest(contamination=0.1)  # 10% anomaly rate
        self.trained = False

    def train_model(self, historical_data):
        """
        Train anomaly detection model on normal operation data
        """
        # Extract features
        features = self.extract_features(historical_data)

        # Train model
        self.model.fit(features)
        self.trained = True

    def extract_features(self, data):
        """
        Extract features from sensor data
        """
        features = []

        for record in data:
            feature_vector = [
                record["supply_air_temp"],
                record["return_air_temp"],
                record["temperature_differential"],
                record["airflow_cfm"],
                record["static_pressure"],
                record["compressor_runtime_hours"],
                record["fan_runtime_hours"],
                record["power_consumption_kw"],
                record["vibration_amplitude"]
            ]
            features.append(feature_vector)

        return np.array(features)

    def predict_failure(self, current_data):
        """
        Predict if equipment is likely to fail
        """
        if not self.trained:
            raise Exception("Model not trained")

        # Extract features
        features = self.extract_features([current_data])

        # Predict anomaly
        prediction = self.model.predict(features)[0]

        # -1 = anomaly (potential failure), 1 = normal
        if prediction == -1:
            # Calculate anomaly score
            anomaly_score = -self.model.score_samples(features)[0]

            # Determine severity
            if anomaly_score > 0.7:
                severity = "critical"
                action = "Schedule emergency maintenance"
            elif anomaly_score > 0.5:
                severity = "high"
                action = "Schedule maintenance within 48 hours"
            else:
                severity = "medium"
                action = "Monitor closely, schedule next available"

            return {
                "failure_predicted": True,
                "anomaly_score": anomaly_score,
                "severity": severity,
                "recommended_action": action,
                "features": self.identify_anomalous_features(current_data)
            }

        else:
            return {
                "failure_predicted": False,
                "anomaly_score": 0,
                "severity": "normal"
            }

    def identify_anomalous_features(self, data):
        """
        Identify which features are anomalous
        """
        # Compare to historical averages
        anomalies = []

        if data["temperature_differential"] > 30:  # Abnormally high
            anomalies.append("High temperature differential - possible refrigerant leak")

        if data["vibration_amplitude"] > 0.5:  # High vibration
            anomalies.append("High vibration - possible bearing failure")

        if data["power_consumption_kw"] > 1.5 * data["historical_avg_power"]:
            anomalies.append("High power consumption - possible compressor issue")

        return anomalies
```

### Remaining Useful Life Prediction

```python
import tensorflow as tf

class RemainingUsefulLife:
    """
    Predict remaining useful life of HVAC equipment
    """

    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def predict_rul(self, equipment_data):
        """
        Predict remaining useful life in hours
        """
        # Prepare input
        features = self.prepare_features(equipment_data)

        # Predict RUL
        rul_hours = self.model.predict(features)[0][0]

        # Convert to days
        rul_days = rul_hours / 24

        return {
            "remaining_useful_life_hours": rul_hours,
            "remaining_useful_life_days": rul_days,
            "estimated_failure_date": datetime.now() + timedelta(hours=rul_hours),
            "confidence_interval": self.calculate_confidence_interval(features)
        }

    def prepare_features(self, data):
        """
        Prepare features for LSTM model
        """
        # Time-series features (last 30 days)
        features = np.array([
            data["compressor_runtime_hours"][-720:],  # 30 days * 24 hours
            data["vibration_amplitude"][-720:],
            data["power_consumption"][-720:],
            data["temperature_differential"][-720:]
        ]).T

        # Reshape for LSTM (samples, timesteps, features)
        features = features.reshape(1, 720, 4)

        return features
```

## Energy Optimization Strategies

### Demand Response

```python
class DemandResponse:
    """
    Participate in utility demand response programs
    """

    def __init__(self, utility_api):
        self.utility_api = utility_api

    def handle_demand_response_event(self, event):
        """
        Respond to utility demand response event
        """
        # Event types: "peak_pricing", "grid_emergency", "voluntary_reduction"

        if event["type"] == "peak_pricing":
            # Reduce load during peak pricing hours
            self.implement_peak_shaving()

        elif event["type"] == "grid_emergency":
            # Aggressive load reduction
            self.implement_emergency_load_shed()

    def implement_peak_shaving(self):
        """
        Reduce load during peak hours (2-7 PM)
        """
        # Pre-cool building before peak period
        current_hour = datetime.now().hour

        if 10 <= current_hour < 14:
            # Pre-cool to 70°F (2°F below normal setpoint)
            self.adjust_all_zones_setpoint(70)

        elif 14 <= current_hour < 19:
            # Peak period: increase setpoint to 76°F (save energy)
            self.adjust_all_zones_setpoint(76)

        else:
            # Normal operation
            self.adjust_all_zones_setpoint(72)

    def estimate_cost_savings(self, baseline_cost, peak_reduction_kw):
        """
        Estimate cost savings from demand response participation
        """
        # Typical demand response incentive: $10-20 per kW reduced
        incentive_per_kw = 15

        demand_charge_savings = peak_reduction_kw * incentive_per_kw

        return {
            "baseline_cost": baseline_cost,
            "demand_charge_savings": demand_charge_savings,
            "total_savings": demand_charge_savings
        }
```

### Load Shifting

```python
class LoadShifting:
    """
    Shift energy-intensive operations to off-peak hours
    """

    def schedule_load_shifting(self):
        """
        Schedule non-critical loads during off-peak hours
        """
        schedule = {
            "chiller_pre_cool": {
                "start_time": "04:00",  # 4 AM (off-peak)
                "duration_hours": 2,
                "target_temp": 68,  # Pre-cool to 68°F
                "estimated_savings": "$50/day"
            },
            "hot_water_heating": {
                "start_time": "22:00",  # 10 PM (off-peak)
                "duration_hours": 6,
                "target_temp": 140,  # Heat to 140°F
                "estimated_savings": "$30/day"
            },
            "battery_charging": {
                "start_time": "23:00",  # 11 PM (off-peak)
                "duration_hours": 7,
                "estimated_savings": "$80/day"
            }
        }

        return schedule
```

## Building Digital Twin Patterns

### Azure Digital Twins Implementation

```python
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential

class BuildingDigitalTwin:
    """
    Building digital twin using Azure Digital Twins
    """

    def __init__(self, endpoint_url):
        credential = DefaultAzureCredential()
        self.client = DigitalTwinsClient(endpoint_url, credential)

    def create_building_model(self, building_data):
        """
        Create digital twin model for building
        """
        # Define building twin
        building_twin = {
            "$dtId": f"building-{building_data['id']}",
            "$metadata": {
                "$model": "dtmi:com:proptech:Building;1"
            },
            "name": building_data["name"],
            "address": building_data["address"],
            "totalArea": building_data["total_area_sqft"],
            "yearBuilt": building_data["year_built"]
        }

        # Create twin
        self.client.upsert_digital_twin(building_twin["$dtId"], building_twin)

        # Create HVAC zone twins
        for zone in building_data["zones"]:
            self.create_zone_twin(building_twin["$dtId"], zone)

    def create_zone_twin(self, building_id, zone_data):
        """
        Create digital twin for HVAC zone
        """
        zone_twin = {
            "$dtId": f"zone-{zone_data['id']}",
            "$metadata": {
                "$model": "dtmi:com:proptech:HVACZone;1"
            },
            "name": zone_data["name"],
            "area": zone_data["area_sqft"],
            "currentTemperature": 72,
            "temperatureSetpoint": 72,
            "occupancy": 0
        }

        # Create twin
        self.client.upsert_digital_twin(zone_twin["$dtId"], zone_twin)

        # Create relationship to building
        relationship = {
            "$relationshipId": f"building-{building_id}-contains-zone-{zone_data['id']}",
            "$sourceId": building_id,
            "$relationshipName": "contains",
            "$targetId": zone_twin["$dtId"]
        }

        self.client.upsert_relationship(
            building_id,
            relationship["$relationshipId"],
            relationship
        )

    def update_zone_telemetry(self, zone_id, sensor_data):
        """
        Update digital twin with real-time sensor data
        """
        patch = [
            {
                "op": "replace",
                "path": "/currentTemperature",
                "value": sensor_data["temperature"]
            },
            {
                "op": "replace",
                "path": "/occupancy",
                "value": sensor_data["occupancy"]
            }
        ]

        self.client.update_digital_twin(f"zone-{zone_id}", patch)

    def query_building_state(self, building_id):
        """
        Query current state of all zones in building
        """
        query = f"""
        SELECT zone
        FROM DIGITALTWINS building
        JOIN zone RELATED building.contains
        WHERE building.$dtId = '{building_id}'
        """

        results = self.client.query_twins(query)

        zones = []
        for result in results:
            zones.append(result["zone"])

        return zones
```

---

## References

1. **ASHRAE Guideline 36**: https://www.ashrae.org/technical-resources/bookstore/ashrae-guideline-36
2. **AWS IoT Greengrass**: https://aws.amazon.com/greengrass/
3. **Azure Digital Twins**: https://azure.microsoft.com/en-us/services/digital-twins/
4. **Honeywell Forge**: https://buildings.honeywell.com/us/en/brands/honeywell-forge

---

*This document is maintained by the PropTech Architecture Committee. For questions or updates, contact architecture@proptech.com.*
