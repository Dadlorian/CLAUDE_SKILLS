# Renewable Energy Systems - Production Implementation Guide

## Overview

Renewable Energy Systems encompass the technologies, monitoring platforms, and optimization algorithms for solar PV, wind turbines, hydro, and other clean energy sources. This skill covers production-grade implementations for monitoring, forecasting, and optimizing renewable energy systems at scale.

## Core Technologies

### 1. Solar Photovoltaic (PV) Systems
Monitoring and optimization of solar installations from residential to utility-scale.

### 2. Wind Energy Systems
SCADA integration, turbine monitoring, and wind forecasting.

### 3. Hydroelectric Systems
Run-of-river and reservoir hydro monitoring and dispatch.

### 4. Hybrid Systems
Integration of multiple renewable sources with storage.

## Standards and Protocols

### Solar Standards
- **IEC 61724-1**: PV system performance monitoring
- **IEC 61853**: PV module performance testing
- **IEEE 1547**: Interconnection and interoperability
- **UL 1741**: Inverter certification
- **IEC 62446**: PV system installation documentation

### Wind Standards
- **IEC 61400**: Wind turbine design and testing series
- **IEC 61850**: SCADA communication
- **IEEE 2030.5**: Smart Energy Profile

### Communication Protocols
- **SunSpec Modbus**: Solar inverter communication
- **DNP3**: SCADA protocol for wind farms
- **IEC 61850**: Substation automation
- **MQTT**: IoT telemetry

## Production-Grade Implementation Examples

### Example 1: Solar PV Monitoring and Performance Analysis

```python
"""
Production-grade solar PV monitoring system
Implements IEC 61724-1 performance analysis standards
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InverterStatus(Enum):
    """Inverter operational status"""
    RUNNING = "running"
    STANDBY = "standby"
    FAULT = "fault"
    MAINTENANCE = "maintenance"
    CURTAILED = "curtailed"

class AlarmType(Enum):
    """Solar system alarm types"""
    UNDERPERFORMANCE = "underperformance"
    INVERTER_FAULT = "inverter_fault"
    STRING_FAILURE = "string_failure"
    GRID_DISCONNECT = "grid_disconnect"
    TEMPERATURE_HIGH = "temperature_high"
    COMMUNICATION_LOSS = "communication_loss"

@dataclass
class SolarTelemetry:
    """
    Solar PV telemetry data point

    Follows IEC 61724-1 measurement requirements
    """
    timestamp: datetime
    site_id: str
    inverter_id: str

    # Power measurements (kW)
    dc_power_kw: float
    ac_power_kw: float
    reactive_power_kvar: float

    # Voltage and current (DC side)
    dc_voltage_v: float
    dc_current_a: float

    # AC side
    ac_voltage_v: float
    ac_current_a: float
    ac_frequency_hz: float
    power_factor: float

    # Energy (kWh) - cumulative
    daily_energy_kwh: float
    lifetime_energy_kwh: float

    # Environmental
    irradiance_wm2: float  # W/m²
    module_temp_c: float
    ambient_temp_c: float

    # Status
    status: InverterStatus
    efficiency_percent: float = 0.0

    def __post_init__(self):
        """Calculate derived metrics"""
        # Calculate inverter efficiency
        if self.dc_power_kw > 0:
            self.efficiency_percent = (self.ac_power_kw / self.dc_power_kw) * 100

    def calculate_performance_ratio(
        self,
        rated_capacity_kw: float,
        standard_irradiance: float = 1000.0
    ) -> float:
        """
        Calculate Performance Ratio (PR) per IEC 61724-1

        PR = (Actual Energy / Expected Energy) × 100%

        Typical PR values:
        - Excellent: 85-90%
        - Good: 80-85%
        - Fair: 75-80%
        - Poor: <75%
        """
        if self.irradiance_wm2 <= 0:
            return 0.0

        # Expected power at current irradiance
        expected_power_kw = rated_capacity_kw * (self.irradiance_wm2 / standard_irradiance)

        if expected_power_kw <= 0:
            return 0.0

        pr = (self.ac_power_kw / expected_power_kw) * 100
        return min(pr, 100.0)  # Cap at 100%

@dataclass
class SolarSite:
    """Solar PV site/installation"""
    site_id: str
    site_name: str
    location: Dict[str, float]  # lat, lon, elevation
    rated_capacity_kwp: float  # kWp (kilowatt-peak)
    num_inverters: int
    num_modules: int
    module_type: str
    inverter_type: str
    commissioning_date: datetime
    timezone: str = "UTC"

    # System design parameters
    azimuth_degrees: float = 180.0  # South-facing (Northern hemisphere)
    tilt_degrees: float = 30.0
    module_efficiency: float = 0.20  # 20%
    system_losses: float = 0.15  # 15% (soiling, wiring, etc.)

@dataclass
class PerformanceReport:
    """Daily or monthly performance report"""
    site_id: str
    period_start: datetime
    period_end: datetime
    total_energy_kwh: float
    expected_energy_kwh: float
    performance_ratio: float
    availability_percent: float
    capacity_factor: float
    specific_yield_kwh_kwp: float
    alarms: List[str] = field(default_factory=list)

class SolarMonitoringSystem:
    """
    Production-grade solar PV monitoring system

    Features:
    - Real-time performance monitoring
    - IEC 61724-1 performance metrics
    - Anomaly detection
    - Inverter-level diagnostics
    - Automated alerting
    - Historical analytics
    """

    def __init__(self, site: SolarSite):
        self.site = site
        self.telemetry_buffer: List[SolarTelemetry] = []
        self.alarms: List[Dict] = []

    def process_telemetry(self, telemetry: SolarTelemetry) -> Dict:
        """
        Process incoming telemetry and detect anomalies

        Returns: Dictionary with status and any alerts
        """
        self.telemetry_buffer.append(telemetry)

        # Calculate performance ratio
        pr = telemetry.calculate_performance_ratio(self.site.rated_capacity_kwp)

        # Detect anomalies
        alerts = self._detect_anomalies(telemetry, pr)

        return {
            'timestamp': telemetry.timestamp,
            'performance_ratio': pr,
            'efficiency': telemetry.efficiency_percent,
            'status': telemetry.status.value,
            'alerts': alerts
        }

    def _detect_anomalies(self, telemetry: SolarTelemetry, pr: float) -> List[Dict]:
        """Detect performance anomalies"""
        alerts = []

        # Low performance ratio alert
        if pr < 75.0 and telemetry.irradiance_wm2 > 200:
            alerts.append({
                'type': AlarmType.UNDERPERFORMANCE.value,
                'severity': 'high',
                'message': f'Low PR: {pr:.1f}% (expected >75%)',
                'timestamp': telemetry.timestamp
            })

        # Inverter efficiency alert
        if telemetry.efficiency_percent < 90.0 and telemetry.dc_power_kw > 1.0:
            alerts.append({
                'type': AlarmType.INVERTER_FAULT.value,
                'severity': 'medium',
                'message': f'Low efficiency: {telemetry.efficiency_percent:.1f}%',
                'timestamp': telemetry.timestamp
            })

        # High temperature alert
        if telemetry.module_temp_c > 85.0:
            alerts.append({
                'type': AlarmType.TEMPERATURE_HIGH.value,
                'severity': 'medium',
                'message': f'High module temperature: {telemetry.module_temp_c:.1f}°C',
                'timestamp': telemetry.timestamp
            })

        # Grid disconnect detection
        if telemetry.ac_power_kw == 0 and telemetry.dc_power_kw > 1.0:
            alerts.append({
                'type': AlarmType.GRID_DISCONNECT.value,
                'severity': 'critical',
                'message': 'Grid disconnection detected',
                'timestamp': telemetry.timestamp
            })

        # Voltage out of range (per IEEE 1547)
        if not (106 <= telemetry.ac_voltage_v <= 132):  # For 120V nominal
            alerts.append({
                'type': AlarmType.GRID_DISCONNECT.value,
                'severity': 'high',
                'message': f'Voltage out of range: {telemetry.ac_voltage_v:.1f}V',
                'timestamp': telemetry.timestamp
            })

        # Frequency out of range (per IEEE 1547)
        if not (59.3 <= telemetry.ac_frequency_hz <= 60.5):
            alerts.append({
                'type': AlarmType.GRID_DISCONNECT.value,
                'severity': 'high',
                'message': f'Frequency out of range: {telemetry.ac_frequency_hz:.2f}Hz',
                'timestamp': telemetry.timestamp
            })

        if alerts:
            self.alarms.extend(alerts)
            logger.warning(f"Detected {len(alerts)} alerts for {telemetry.inverter_id}")

        return alerts

    def generate_daily_report(self, date: datetime) -> PerformanceReport:
        """
        Generate daily performance report per IEC 61724-1

        Metrics include:
        - Total energy production
        - Performance ratio
        - Specific yield (kWh/kWp)
        - Capacity factor
        - Availability
        """
        # Filter telemetry for the specified date
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        daily_data = [
            t for t in self.telemetry_buffer
            if day_start <= t.timestamp < day_end
        ]

        if not daily_data:
            logger.warning(f"No data for {date.date()}")
            return None

        # Calculate total energy
        total_energy_kwh = daily_data[-1].daily_energy_kwh

        # Calculate expected energy
        total_irradiance = sum(t.irradiance_wm2 for t in daily_data)
        avg_irradiance = total_irradiance / len(daily_data) if daily_data else 0
        # Expected energy = capacity × hours × (irradiance/1000) × (1 - losses)
        expected_energy_kwh = (
            self.site.rated_capacity_kwp *
            24 *
            (avg_irradiance / 1000) *
            (1 - self.site.system_losses)
        )

        # Performance ratio
        if expected_energy_kwh > 0:
            pr = (total_energy_kwh / expected_energy_kwh) * 100
        else:
            pr = 0.0

        # Specific yield (kWh per kWp installed)
        specific_yield = total_energy_kwh / self.site.rated_capacity_kwp

        # Capacity factor
        max_possible_energy = self.site.rated_capacity_kwp * 24  # kWh
        capacity_factor = (total_energy_kwh / max_possible_energy) * 100

        # Availability (% of time online)
        online_count = sum(1 for t in daily_data if t.status == InverterStatus.RUNNING)
        availability = (online_count / len(daily_data)) * 100 if daily_data else 0.0

        # Collect alarm summaries
        alarm_summary = [
            f"{alarm['type']}: {alarm['message']}"
            for alarm in self.alarms
            if day_start <= alarm['timestamp'] < day_end
        ]

        report = PerformanceReport(
            site_id=self.site.site_id,
            period_start=day_start,
            period_end=day_end,
            total_energy_kwh=total_energy_kwh,
            expected_energy_kwh=expected_energy_kwh,
            performance_ratio=pr,
            availability_percent=availability,
            capacity_factor=capacity_factor,
            specific_yield_kwh_kwp=specific_yield,
            alarms=alarm_summary
        )

        logger.info(
            f"Daily Report {date.date()}: "
            f"Energy={total_energy_kwh:.1f} kWh, "
            f"PR={pr:.1f}%, "
            f"Availability={availability:.1f}%"
        )

        return report


class SolarForecaster:
    """
    Solar generation forecasting using weather data

    Implements:
    - Day-ahead forecasting
    - Intraday updates
    - Clear sky modeling
    - Weather forecast integration
    """

    def __init__(self, site: SolarSite):
        self.site = site

    def forecast_generation(
        self,
        weather_forecast: List[Dict],
        horizon_hours: int = 24
    ) -> List[Dict]:
        """
        Forecast solar generation for next N hours

        Args:
            weather_forecast: List of weather forecasts with:
                - timestamp
                - irradiance (W/m²)
                - temperature (°C)
                - cloud_cover (%)
            horizon_hours: Forecast horizon

        Returns:
            List of generation forecasts with:
                - timestamp
                - forecasted_power_kw
                - confidence_interval
        """
        forecasts = []

        for weather in weather_forecast[:horizon_hours]:
            # Calculate expected power using simple model
            # In production, use ML models or detailed physics models

            irradiance = weather['irradiance']  # W/m²
            temperature = weather['temperature']  # °C
            cloud_cover = weather.get('cloud_cover', 0)  # %

            # Adjust irradiance for cloud cover
            effective_irradiance = irradiance * (1 - cloud_cover / 100)

            # Temperature coefficient (typically -0.4% to -0.5% per °C above 25°C)
            temp_coefficient = -0.0045  # per °C
            temp_factor = 1 + temp_coefficient * (temperature - 25)

            # Calculate expected power
            expected_power_kw = (
                self.site.rated_capacity_kwp *
                (effective_irradiance / 1000) *
                temp_factor *
                (1 - self.site.system_losses)
            )

            # Confidence interval (wider for longer horizons)
            uncertainty = 0.10 + (0.02 * weather.get('hour', 0))  # 10-20%
            confidence_lower = expected_power_kw * (1 - uncertainty)
            confidence_upper = expected_power_kw * (1 + uncertainty)

            forecasts.append({
                'timestamp': weather['timestamp'],
                'forecasted_power_kw': max(0, expected_power_kw),
                'confidence_lower_kw': max(0, confidence_lower),
                'confidence_upper_kw': confidence_upper
            })

        return forecasts

    def calculate_clear_sky_irradiance(
        self,
        timestamp: datetime,
        latitude: float,
        longitude: float
    ) -> float:
        """
        Calculate clear sky irradiance using simplified model

        In production, use libraries like pvlib-python for accurate modeling
        """
        # This is a simplified placeholder
        # Real implementation would use solar position algorithms
        # and atmospheric models (pvlib, pysolar, etc.)

        import math
        from datetime import timezone

        # Get day of year
        day_of_year = timestamp.timetuple().tm_yday

        # Solar declination (simplified)
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))

        # Hour angle
        hour = timestamp.hour + timestamp.minute / 60.0
        hour_angle = 15 * (hour - 12)

        # Solar elevation angle (simplified)
        lat_rad = math.radians(latitude)
        decl_rad = math.radians(declination)
        hour_angle_rad = math.radians(hour_angle)

        sin_elevation = (
            math.sin(lat_rad) * math.sin(decl_rad) +
            math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_angle_rad)
        )
        elevation = math.degrees(math.asin(max(0, sin_elevation)))

        # Clear sky irradiance (simplified)
        if elevation > 0:
            # Extraterrestrial irradiance
            solar_constant = 1367  # W/m²
            irradiance = solar_constant * sin_elevation * 0.7  # Atmospheric transmission ~0.7
        else:
            irradiance = 0

        return max(0, irradiance)


# Example usage
def main():
    """Example usage of solar monitoring system"""

    # Define solar site
    site = SolarSite(
        site_id="SITE-001",
        site_name="Downtown Solar Farm",
        location={'lat': 37.7749, 'lon': -122.4194, 'elevation': 100},
        rated_capacity_kwp=1000.0,  # 1 MW
        num_inverters=10,
        num_modules=3000,
        module_type="Tier-1 Monocrystalline 330W",
        inverter_type="SMA Sunny Central 100",
        commissioning_date=datetime(2023, 1, 1),
        azimuth_degrees=180.0,
        tilt_degrees=30.0
    )

    # Initialize monitoring system
    monitor = SolarMonitoringSystem(site)

    # Simulate telemetry data
    telemetry = SolarTelemetry(
        timestamp=datetime.utcnow(),
        site_id=site.site_id,
        inverter_id="INV-001",
        dc_power_kw=105.0,
        ac_power_kw=100.0,
        reactive_power_kvar=5.0,
        dc_voltage_v=650.0,
        dc_current_a=161.5,
        ac_voltage_v=480.0,
        ac_current_a=120.3,
        ac_frequency_hz=60.0,
        power_factor=0.998,
        daily_energy_kwh=450.0,
        lifetime_energy_kwh=125000.0,
        irradiance_wm2=850.0,
        module_temp_c=55.0,
        ambient_temp_c=28.0,
        status=InverterStatus.RUNNING
    )

    # Process telemetry
    result = monitor.process_telemetry(telemetry)
    print(f"\nTelemetry Processing Result:")
    print(f"  Performance Ratio: {result['performance_ratio']:.1f}%")
    print(f"  Efficiency: {result['efficiency']:.1f}%")
    print(f"  Status: {result['status']}")
    print(f"  Alerts: {len(result['alerts'])}")

    for alert in result['alerts']:
        print(f"    - {alert['severity'].upper()}: {alert['message']}")

    # Generate forecasts
    forecaster = SolarForecaster(site)

    # Mock weather forecast
    weather_forecast = [
        {
            'timestamp': datetime.utcnow() + timedelta(hours=i),
            'irradiance': 800 - (i * 20),  # Decreasing
            'temperature': 25 + (i * 0.5),
            'cloud_cover': i * 2,
            'hour': i
        }
        for i in range(24)
    ]

    forecasts = forecaster.forecast_generation(weather_forecast, horizon_hours=24)

    print(f"\n24-Hour Generation Forecast:")
    print(f"  Total forecasted generation: {sum(f['forecasted_power_kw'] for f in forecasts):.1f} kWh")
    print(f"  Peak forecasted power: {max(f['forecasted_power_kw'] for f in forecasts):.1f} kW")

    # Print first 6 hours
    print(f"\n  First 6 hours:")
    for forecast in forecasts[:6]:
        print(
            f"    {forecast['timestamp'].strftime('%H:%M')}: "
            f"{forecast['forecasted_power_kw']:.1f} kW "
            f"({forecast['confidence_lower_kw']:.1f} - {forecast['confidence_upper_kw']:.1f})"
        )

if __name__ == "__main__":
    main()
```

### Example 2: Wind Farm SCADA Integration

```python
"""
Wind farm SCADA monitoring and control
Implements IEC 61400 standards
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TurbineStatus(Enum):
    """Wind turbine operational status"""
    RUNNING = "running"
    STANDBY = "standby"
    FAULT = "fault"
    MAINTENANCE = "maintenance"
    PARKED = "parked"
    IDLING = "idling"

@dataclass
class WindTurbineTelemetry:
    """Wind turbine telemetry following IEC 61400-25"""
    timestamp: datetime
    turbine_id: str

    # Power
    active_power_kw: float
    reactive_power_kvar: float

    # Wind conditions
    wind_speed_ms: float  # m/s
    wind_direction_deg: float
    turbulence_intensity: float

    # Mechanical
    rotor_speed_rpm: float
    generator_speed_rpm: float
    pitch_angle_deg: float
    yaw_angle_deg: float

    # Electrical
    voltage_v: float
    current_a: float
    frequency_hz: float
    power_factor: float

    # Environmental
    ambient_temp_c: float
    nacelle_temp_c: float
    gearbox_temp_c: float

    # Status
    status: TurbineStatus
    availability: bool = True

    # Cumulative energy
    daily_energy_kwh: float = 0.0
    lifetime_energy_kwh: float = 0.0

class WindFarmController:
    """
    Wind farm SCADA controller

    Features:
    - Turbine monitoring and control
    - Power output optimization
    - Wake effect mitigation
    - Grid code compliance
    """

    def __init__(self, farm_id: str, rated_capacity_mw: float):
        self.farm_id = farm_id
        self.rated_capacity_mw = rated_capacity_mw
        self.turbines: Dict[str, WindTurbineTelemetry] = {}

    def update_turbine_status(self, telemetry: WindTurbineTelemetry):
        """Update turbine telemetry"""
        self.turbines[telemetry.turbine_id] = telemetry

    def get_farm_output(self) -> float:
        """Get total farm power output"""
        return sum(
            t.active_power_kw
            for t in self.turbines.values()
            if t.status == TurbineStatus.RUNNING
        )

    def optimize_farm_output(self):
        """
        Optimize wind farm output accounting for wake effects

        Uses wake steering and yaw optimization
        """
        # In production, implement wake modeling and optimization
        # Libraries: FLORIS, PyWake
        pass

    def implement_curtailment(self, target_power_mw: float):
        """
        Curtail wind farm to target power output

        Required for grid stability and market participation
        """
        current_output_kw = self.get_farm_output()
        target_power_kw = target_power_mw * 1000

        if current_output_kw <= target_power_kw:
            return  # No curtailment needed

        # Proportional curtailment across all turbines
        curtailment_factor = target_power_kw / current_output_kw

        for turbine in self.turbines.values():
            if turbine.status == TurbineStatus.RUNNING:
                # In production, send pitch angle commands
                # to reduce power output
                pass
```

## Architecture Patterns

### Pattern 1: Hierarchical Renewable Monitoring

```
┌─────────────────────────────────────────────────────────┐
│         Central Monitoring & Control Center             │
│    - Portfolio analytics                                │
│    - Forecasting & scheduling                           │
│    - Market bidding                                     │
│    - Asset management                                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/MQTT
┌────────────────────┴────────────────────────────────────┐
│              Site Controllers (Edge)                    │
│    - Local SCADA                                        │
│    - Real-time control                                  │
│    - Data aggregation                                   │
└────┬──────────────────┬──────────────────┬─────────────┘
     │                  │                  │
     │ Modbus/SunSpec  │ DNP3            │ IEC 61850
     │                  │                  │
┌────▼─────┐    ┌──────▼──────┐    ┌─────▼──────┐
│ Inverters│    │  Turbines   │    │  Meters    │
│  (Solar) │    │   (Wind)    │    │            │
└──────────┘    └─────────────┘    └────────────┘
```

## Key Performance Indicators

### Solar PV KPIs
- **Performance Ratio (PR)**: Target >80%
- **Availability**: Target >98%
- **Specific Yield**: kWh/kWp/year (location dependent)
- **Capacity Factor**: Typically 15-25% for solar

### Wind Energy KPIs
- **Availability**: Target >95%
- **Capacity Factor**: Typically 25-45% for wind
- **Wake Losses**: Minimize to <5%
- **Turbine Efficiency**: Target >95% of theoretical

## Common Challenges and Solutions

### Challenge 1: Intermittency
**Problem**: Variable generation affects grid stability
**Solution**: Forecasting, storage integration, curtailment capability

### Challenge 2: Soiling and Degradation
**Problem**: PV modules lose efficiency over time
**Solution**: Automated soiling detection, predictive maintenance

### Challenge 3: Wake Effects (Wind)
**Problem**: Downstream turbines produce less power
**Solution**: Wake steering, yaw optimization, farm layout optimization

### Challenge 4: Grid Code Compliance
**Problem**: Must meet strict interconnection requirements
**Solution**: IEEE 1547 compliant inverters, voltage/frequency ride-through

## Industry Resources

### Tools and Libraries
- **pvlib-python**: Solar PV modeling
- **FLORIS**: Wake modeling for wind farms
- **SAM**: System Advisor Model (NREL)
- **PVWatts**: Solar energy calculator

### Standards Organizations
- **IEC TC 82**: Solar photovoltaic systems
- **IEC TC 88**: Wind energy systems
- **IEEE**: Interconnection standards

## Conclusion

Renewable energy systems require expertise in power systems, meteorology, data science, and control systems. Production implementations must handle variability, ensure grid compliance, and maximize energy capture while maintaining system health. The examples provided demonstrate industry best practices for monitoring and optimization.
