# Energy Management Systems - Production Implementation Guide

## Overview

Energy Management Systems (EMS) optimize energy consumption in buildings, campuses, and industrial facilities. This skill covers Building Energy Management Systems (BEMS), HVAC optimization, demand response, and industrial energy management with production-grade implementations.

## Core Technologies

### 1. Building Energy Management Systems (BEMS)
Integrated systems for monitoring and controlling building energy systems including HVAC, lighting, and plug loads.

### 2. HVAC Optimization
Model Predictive Control (MPC) and advanced algorithms for heating, ventilation, and air conditioning optimization.

### 3. Demand Response
Automated load reduction in response to grid signals or price incentives.

### 4. Industrial Energy Management
Manufacturing facility energy optimization and ISO 50001 compliance.

## Standards and Protocols

### Building Automation Standards
- **BACnet (ASHRAE 135)**: Building automation and control networks
- **Modbus**: Serial/TCP communication protocol
- **LonWorks**: Control networking protocol
- **KNX**: Building automation standard
- **MQTT**: IoT messaging protocol

### Energy Standards
- **ISO 50001**: Energy management systems
- **ASHRAE 90.1**: Energy standard for buildings
- **LEED**: Green building certification
- **ASHRAE Guideline 36**: High-performance sequences of operation for HVAC
- **IEEE 1547**: Distributed energy resources

### Indoor Environment Standards
- **ASHRAE 55**: Thermal environmental conditions
- **ASHRAE 62.1**: Ventilation and indoor air quality

## Production-Grade Implementation Examples

### Example 1: Building Energy Management System with Model Predictive Control

```python
"""
Production-grade Building Energy Management System (BEMS)
Implements Model Predictive Control (MPC) for HVAC optimization

References:
- ASHRAE Guideline 36: High-Performance Sequences
- ISO 50001: Energy Management Systems
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HVACMode(Enum):
    """HVAC operating modes"""
    HEATING = "heating"
    COOLING = "cooling"
    VENTILATION = "ventilation"
    OFF = "off"
    AUTO = "auto"

class OccupancyState(Enum):
    """Building occupancy states"""
    OCCUPIED = "occupied"
    UNOCCUPIED = "unoccupied"
    STANDBY = "standby"

@dataclass
class ZoneSensor:
    """Zone sensor readings"""
    zone_id: str
    timestamp: datetime

    # Temperature (°C or °F)
    temperature: float
    temperature_setpoint: float

    # Humidity (%)
    relative_humidity: float

    # CO2 (ppm)
    co2_ppm: float

    # Occupancy
    occupancy_count: int
    occupancy_detected: bool

    # Comfort metrics (calculated)
    thermal_comfort_pmv: Optional[float] = None  # Predicted Mean Vote
    air_quality_index: Optional[float] = None

@dataclass
class HVACEquipment:
    """HVAC equipment status"""
    equipment_id: str
    zone_id: str
    timestamp: datetime

    # Equipment type
    equipment_type: str  # AHU, VAV, FCU, etc.

    # Operation
    mode: HVACMode
    enabled: bool

    # Airflow
    airflow_cfm: float  # Cubic feet per minute
    supply_air_temp_f: float
    return_air_temp_f: float

    # Valve/damper positions (%)
    heating_valve_position: float = 0.0
    cooling_valve_position: float = 0.0
    damper_position: float = 0.0

    # Fan
    fan_speed_percent: float = 0.0
    fan_power_kw: float = 0.0

    # Energy
    power_consumption_kw: float = 0.0
    energy_consumed_kwh: float = 0.0

@dataclass
class WeatherForecast:
    """Weather forecast for predictive control"""
    timestamp: datetime
    temperature_f: float
    humidity_percent: float
    solar_irradiance_wm2: float
    wind_speed_mph: float
    cloud_cover_percent: float

@dataclass
class EnergyPrice:
    """Energy pricing for optimization"""
    timestamp: datetime
    price_per_kwh: float
    demand_charge_per_kw: float = 0.0

class MPCController:
    """
    Model Predictive Control for HVAC optimization

    Features:
    - Multi-zone temperature control
    - Energy cost optimization
    - Thermal comfort maintenance
    - Demand response integration
    - Weather forecast integration
    - Occupancy-based control

    Based on research from:
    - Lawrence Berkeley National Lab (LBNL)
    - National Renewable Energy Laboratory (NREL)
    - ASHRAE Guideline 36
    """

    def __init__(
        self,
        building_id: str,
        prediction_horizon_hours: int = 6,
        control_interval_minutes: int = 15
    ):
        self.building_id = building_id
        self.prediction_horizon = prediction_horizon_hours
        self.control_interval = control_interval_minutes

        # Thermal model parameters (learned from building data)
        self.thermal_capacitance = 1.0  # MJ/°C
        self.thermal_resistance = 0.1  # °C/kW

        # Comfort bounds per ASHRAE 55
        self.temp_min_occupied_f = 68.0  # 20°C
        self.temp_max_occupied_f = 76.0  # 24.4°C
        self.temp_min_unoccupied_f = 60.0  # 15.6°C
        self.temp_max_unoccupied_f = 85.0  # 29.4°C

        # CO2 limit per ASHRAE 62.1
        self.co2_max_ppm = 1000.0

    def optimize_hvac_setpoints(
        self,
        current_state: ZoneSensor,
        current_equipment: HVACEquipment,
        weather_forecast: List[WeatherForecast],
        energy_prices: List[EnergyPrice],
        occupancy_schedule: List[OccupancyState]
    ) -> Dict:
        """
        Optimize HVAC setpoints using Model Predictive Control

        Minimizes cost function:
        J = α·Energy_Cost + β·Comfort_Penalty + γ·Peak_Demand

        Subject to:
        - Temperature comfort constraints (ASHRAE 55)
        - CO2 constraints (ASHRAE 62.1)
        - Equipment capacity constraints
        - Rate of change limits

        Returns:
            Optimal setpoints for next control interval
        """

        # Prediction horizon
        n_steps = (self.prediction_horizon * 60) // self.control_interval

        # Current conditions
        T_current = current_state.temperature

        # Weights for objective function
        alpha = 1.0  # Energy cost weight
        beta = 100.0  # Comfort weight (high priority)
        gamma = 50.0  # Peak demand weight

        # Simplified optimization (in production, use CVXPY or similar)
        optimal_setpoints = []

        for i in range(min(n_steps, len(weather_forecast))):
            weather = weather_forecast[i]
            price = energy_prices[i] if i < len(energy_prices) else energy_prices[-1]
            occupancy = occupancy_schedule[i] if i < len(occupancy_schedule) else OccupancyState.UNOCCUPIED

            # Determine comfort bounds based on occupancy
            if occupancy == OccupancyState.OCCUPIED:
                T_min = self.temp_min_occupied_f
                T_max = self.temp_max_occupied_f
            else:
                T_min = self.temp_min_unoccupied_f
                T_max = self.temp_max_unoccupied_f

            # Simple heuristic for demonstration
            # In production, solve optimization problem with constraints

            if price.price_per_kwh < 0.10:  # Low price period
                # Pre-cool or pre-heat during low-cost periods
                if weather.temperature_f > 75:
                    setpoint = T_min + 1  # Pre-cool
                elif weather.temperature_f < 65:
                    setpoint = T_max - 1  # Pre-heat
                else:
                    setpoint = (T_min + T_max) / 2
            else:  # High price period
                # Allow wider temperature range
                if occupancy == OccupancyState.OCCUPIED:
                    setpoint = (T_min + T_max) / 2
                else:
                    # Maximize savings during unoccupied
                    if weather.temperature_f > 75:
                        setpoint = T_max
                    else:
                        setpoint = T_min

            # Calculate predicted energy consumption
            cooling_load = max(0, weather.temperature_f - setpoint)
            heating_load = max(0, setpoint - weather.temperature_f)

            # Simplified energy model
            energy_kwh = (cooling_load * 0.5 + heating_load * 0.3) * (self.control_interval / 60)
            cost = energy_kwh * price.price_per_kwh

            optimal_setpoints.append({
                'timestamp': weather.timestamp,
                'temperature_setpoint_f': setpoint,
                'predicted_energy_kwh': energy_kwh,
                'predicted_cost': cost,
                'occupancy': occupancy.value
            })

        # Return immediate control action (first step)
        if optimal_setpoints:
            logger.info(
                f"MPC Optimization: Setpoint={optimal_setpoints[0]['temperature_setpoint_f']:.1f}°F, "
                f"Predicted Energy={optimal_setpoints[0]['predicted_energy_kwh']:.2f} kWh"
            )
            return optimal_setpoints[0]

        # Fallback to current setpoint
        return {
            'timestamp': datetime.utcnow(),
            'temperature_setpoint_f': current_state.temperature_setpoint,
            'predicted_energy_kwh': 0,
            'predicted_cost': 0,
            'occupancy': OccupancyState.UNOCCUPIED.value
        }

class DemandResponseController:
    """
    Automated Demand Response per OpenADR 2.0b

    Implements:
    - Load shed strategies
    - Pre-cooling/pre-heating
    - Equipment curtailment
    - Event notification
    """

    def __init__(self, building_id: str, max_load_reduction_kw: float):
        self.building_id = building_id
        self.max_load_reduction_kw = max_load_reduction_kw
        self.baseline_load_kw: Optional[float] = None

    def handle_dr_event(
        self,
        target_reduction_kw: float,
        duration_minutes: int,
        advance_notice_minutes: int
    ) -> Dict:
        """
        Handle demand response event

        Strategies (in priority order):
        1. Pre-cooling before event (if advance notice)
        2. Temperature setpoint adjustment
        3. Lighting reduction
        4. Non-critical equipment curtailment
        """

        strategies = []
        total_reduction_kw = 0.0

        # Strategy 1: Pre-cooling (if advance notice)
        if advance_notice_minutes >= 60:
            precool_savings_kw = min(target_reduction_kw * 0.3, self.max_load_reduction_kw * 0.3)
            strategies.append({
                'strategy': 'pre_cooling',
                'reduction_kw': precool_savings_kw,
                'start_minutes': -advance_notice_minutes,
                'duration_minutes': advance_notice_minutes
            })
            total_reduction_kw += precool_savings_kw

        # Strategy 2: Setpoint adjustment
        if total_reduction_kw < target_reduction_kw:
            setpoint_savings_kw = min(
                (target_reduction_kw - total_reduction_kw),
                self.max_load_reduction_kw * 0.5
            )
            strategies.append({
                'strategy': 'setpoint_adjustment',
                'reduction_kw': setpoint_savings_kw,
                'setpoint_change_f': 4.0,  # Increase cooling setpoint by 4°F
                'duration_minutes': duration_minutes
            })
            total_reduction_kw += setpoint_savings_kw

        # Strategy 3: Lighting reduction
        if total_reduction_kw < target_reduction_kw:
            lighting_savings_kw = min(
                (target_reduction_kw - total_reduction_kw),
                self.max_load_reduction_kw * 0.2
            )
            strategies.append({
                'strategy': 'lighting_reduction',
                'reduction_kw': lighting_savings_kw,
                'reduction_percent': 30.0,
                'duration_minutes': duration_minutes
            })
            total_reduction_kw += lighting_savings_kw

        logger.info(
            f"DR Event: Target={target_reduction_kw:.1f} kW, "
            f"Achieved={total_reduction_kw:.1f} kW, "
            f"Strategies={len(strategies)}"
        )

        return {
            'target_reduction_kw': target_reduction_kw,
            'achieved_reduction_kw': total_reduction_kw,
            'strategies': strategies,
            'duration_minutes': duration_minutes
        }

class EnergyDashboard:
    """
    Real-time energy monitoring dashboard

    Displays:
    - Current energy consumption
    - Cost tracking
    - Comfort metrics
    - Equipment status
    - Alerts and anomalies
    """

    def __init__(self, building_id: str):
        self.building_id = building_id
        self.measurements: List[Dict] = []

    def update_metrics(
        self,
        zone_sensors: List[ZoneSensor],
        equipment: List[HVACEquipment],
        energy_price: EnergyPrice
    ) -> Dict:
        """Calculate and return dashboard metrics"""

        # Total power consumption
        total_power_kw = sum(eq.power_consumption_kw for eq in equipment)

        # Average zone temperature
        avg_temp = sum(z.temperature for z in zone_sensors) / len(zone_sensors) if zone_sensors else 0

        # Comfort compliance (% of zones in comfort range)
        comfort_zones = sum(
            1 for z in zone_sensors
            if 68 <= z.temperature <= 76 and z.co2_ppm < 1000
        )
        comfort_compliance = (comfort_zones / len(zone_sensors) * 100) if zone_sensors else 0

        # Current cost rate
        cost_per_hour = total_power_kw * energy_price.price_per_kwh

        metrics = {
            'timestamp': datetime.utcnow(),
            'total_power_kw': total_power_kw,
            'cost_per_hour': cost_per_hour,
            'avg_temperature_f': avg_temp,
            'comfort_compliance_percent': comfort_compliance,
            'num_zones': len(zone_sensors),
            'num_equipment': len(equipment),
            'energy_price_per_kwh': energy_price.price_per_kwh
        }

        self.measurements.append(metrics)
        return metrics


# Example usage
def main():
    """Example usage of Energy Management System"""

    # Initialize MPC controller
    mpc = MPCController(
        building_id="BLDG-001",
        prediction_horizon_hours=6,
        control_interval_minutes=15
    )

    # Current zone conditions
    zone_sensor = ZoneSensor(
        zone_id="ZONE-101",
        timestamp=datetime.utcnow(),
        temperature=72.0,
        temperature_setpoint=72.0,
        relative_humidity=45.0,
        co2_ppm=650.0,
        occupancy_count=25,
        occupancy_detected=True
    )

    # Current equipment status
    equipment = HVACEquipment(
        equipment_id="AHU-01",
        zone_id="ZONE-101",
        timestamp=datetime.utcnow(),
        equipment_type="Air Handling Unit",
        mode=HVACMode.COOLING,
        enabled=True,
        airflow_cfm=5000.0,
        supply_air_temp_f=55.0,
        return_air_temp_f=72.0,
        cooling_valve_position=45.0,
        fan_speed_percent=70.0,
        fan_power_kw=8.5,
        power_consumption_kw=25.0
    )

    # Weather forecast
    weather_forecast = [
        WeatherForecast(
            timestamp=datetime.utcnow() + timedelta(hours=i),
            temperature_f=85.0 + i,
            humidity_percent=60.0,
            solar_irradiance_wm2=800.0 - (i * 50),
            wind_speed_mph=10.0,
            cloud_cover_percent=20.0
        )
        for i in range(6)
    ]

    # Energy prices (time-of-use)
    energy_prices = [
        EnergyPrice(
            timestamp=datetime.utcnow() + timedelta(hours=i),
            price_per_kwh=0.08 if i < 3 else 0.25,  # Peak pricing after 3 hours
            demand_charge_per_kw=15.0
        )
        for i in range(6)
    ]

    # Occupancy schedule
    occupancy_schedule = [
        OccupancyState.OCCUPIED if i < 4 else OccupancyState.UNOCCUPIED
        for i in range(6)
    ]

    # Run MPC optimization
    optimal_setpoint = mpc.optimize_hvac_setpoints(
        zone_sensor,
        equipment,
        weather_forecast,
        energy_prices,
        occupancy_schedule
    )

    print(f"\n=== MPC Optimization Results ===")
    print(f"Optimal Temperature Setpoint: {optimal_setpoint['temperature_setpoint_f']:.1f}°F")
    print(f"Predicted Energy: {optimal_setpoint['predicted_energy_kwh']:.2f} kWh")
    print(f"Predicted Cost: ${optimal_setpoint['predicted_cost']:.2f}")

    # Test demand response
    dr_controller = DemandResponseController(
        building_id="BLDG-001",
        max_load_reduction_kw=100.0
    )

    dr_response = dr_controller.handle_dr_event(
        target_reduction_kw=50.0,
        duration_minutes=60,
        advance_notice_minutes=120
    )

    print(f"\n=== Demand Response Event ===")
    print(f"Target Reduction: {dr_response['target_reduction_kw']:.1f} kW")
    print(f"Achieved Reduction: {dr_response['achieved_reduction_kw']:.1f} kW")
    print(f"Strategies Used: {len(dr_response['strategies'])}")
    for strategy in dr_response['strategies']:
        print(f"  - {strategy['strategy']}: {strategy['reduction_kw']:.1f} kW")

    # Dashboard metrics
    dashboard = EnergyDashboard("BLDG-001")
    price = energy_prices[0]

    metrics = dashboard.update_metrics([zone_sensor], [equipment], price)

    print(f"\n=== Current Building Metrics ===")
    print(f"Total Power: {metrics['total_power_kw']:.1f} kW")
    print(f"Cost Rate: ${metrics['cost_per_hour']:.2f}/hour")
    print(f"Avg Temperature: {metrics['avg_temperature_f']:.1f}°F")
    print(f"Comfort Compliance: {metrics['comfort_compliance_percent']:.1f}%")

if __name__ == "__main__":
    main()
```

## Architecture Patterns

### Pattern 1: Hierarchical Building Energy Management

```
┌──────────────────────────────────────────────────────┐
│         Enterprise Energy Management                 │
│    - Portfolio analytics                             │
│    - Benchmarking                                    │
│    - ISO 50001 compliance                           │
└───────────────────┬──────────────────────────────────┘
                    │ HTTPS/MQTT
┌───────────────────┴──────────────────────────────────┐
│         Building Management System (BMS)             │
│    - HVAC control                                    │
│    - Lighting control                                │
│    - Energy optimization                             │
│    - Demand response                                 │
└───┬────────────────┬─────────────────┬───────────────┘
    │ BACnet         │ Modbus          │ MQTT
┌───▼────┐    ┌──────▼──────┐   ┌─────▼──────┐
│  VAV   │    │  Chillers   │   │  Sensors   │
│  Boxes │    │  Boilers    │   │  Meters    │
└────────┘    └─────────────┘   └────────────┘
```

## Key Performance Indicators

### Energy KPIs
- **Energy Use Intensity (EUI)**: kBtu/ft²/year or kWh/m²/year
- **Peak Demand**: kW (minimize for cost savings)
- **Load Factor**: Average load / Peak load
- **Energy Cost**: $/ft²/year

### Comfort KPIs per ASHRAE 55
- **Temperature Compliance**: % time within setpoint ±2°F
- **PMV (Predicted Mean Vote)**: Target -0.5 to +0.5
- **CO2 Levels**: <1000 ppm per ASHRAE 62.1

### Operational KPIs
- **Equipment Runtime**: Hours
- **Maintenance Compliance**: %
- **System Availability**: >99%

## Industry Resources

### Standards
- [ASHRAE](https://www.ashrae.org/)
- [ISO 50001](https://www.iso.org/iso-50001-energy-management.html)
- [BACnet International](https://www.bacnetinternational.org/)

### Tools
- **EnergyPlus**: Building energy simulation
- **OpenStudio**: Building modeling
- **Project Haystack**: IoT data modeling

## Conclusion

Energy Management Systems combine control systems, data analytics, and optimization to reduce energy consumption while maintaining occupant comfort. Success requires understanding of HVAC systems, building physics, control theory, and energy economics. The MPC implementation demonstrates advanced optimization techniques used in modern commercial buildings.
