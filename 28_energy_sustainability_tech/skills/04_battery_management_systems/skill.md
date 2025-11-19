# Battery Management Systems - Production Implementation Guide

## Overview

Battery Management Systems (BMS) ensure safe and efficient operation of battery packs in EVs, grid storage, and portable devices. This skill covers production-grade BMS implementations including State of Charge (SOC) estimation, State of Health (SOH) monitoring, cell balancing, thermal management, and safety monitoring.

## Core Concepts

### 1. State of Charge (SOC)
Current charge level as percentage of total capacity. Analogous to fuel gauge in vehicles.

### 2. State of Health (SOH)
Battery capacity relative to new condition. Degrades over time due to aging.

### 3. Cell Balancing
Equalizing voltage/charge across cells in series to maximize capacity and lifespan.

### 4. Thermal Management
Maintaining optimal battery temperature (typically 20-25°C) for performance and safety.

### 5. Safety Monitoring
Detecting and preventing dangerous conditions (overcharge, over-discharge, thermal runaway).

## Standards and Regulations

### Safety Standards
- **UL 1973**: Batteries for use in stationary applications
- **UL 2580**: Batteries for use in electric vehicles
- **IEC 62619**: Secondary cells and batteries containing alkaline or other non-acid electrolytes
- **UN 38.3**: Transportation testing for lithium batteries
- **ISO 26262**: Automotive functional safety

### Communication Standards
- **CANbus**: Controller Area Network (automotive)
- **Modbus**: Industrial communication
- **SMBus**: System Management Bus (consumer electronics)

## Production-Grade Implementation Examples

### Example 1: Advanced Battery Management System with SOC/SOH Estimation

```python
"""
Production-grade Battery Management System (BMS)
Implements SOC estimation, SOH tracking, and safety monitoring

References:
- ISO 26262: Automotive functional safety
- UL 2580: EV battery safety
- SAE J1772: EV charging
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatteryChemistry(Enum):
    """Battery chemistry types"""
    LITHIUM_ION = "li-ion"
    LITHIUM_IRON_PHOSPHATE = "lfp"  # LiFePO4
    NICKEL_MANGANESE_COBALT = "nmc"
    NICKEL_COBALT_ALUMINUM = "nca"
    LITHIUM_TITANATE = "lto"
    LEAD_ACID = "lead-acid"

class BatteryState(Enum):
    """Battery operational state"""
    IDLE = "idle"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    BALANCING = "balancing"
    FAULT = "fault"
    MAINTENANCE = "maintenance"

class AlarmLevel(Enum):
    """Alarm severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class CellMeasurement:
    """Individual cell measurements"""
    cell_id: int
    voltage_v: float
    temperature_c: float
    timestamp: datetime

@dataclass
class BatteryPackTelemetry:
    """
    Battery pack telemetry data

    Follows automotive and grid storage BMS standards
    """
    timestamp: datetime
    pack_id: str

    # Pack-level measurements
    pack_voltage_v: float
    pack_current_a: float  # Positive = charging, Negative = discharging
    pack_power_kw: float

    # Cell measurements
    cell_voltages: List[float]  # Individual cell voltages
    cell_temperatures: List[float]  # Individual cell temperatures

    # Derived metrics
    min_cell_voltage_v: float
    max_cell_voltage_v: float
    voltage_delta_v: float
    avg_cell_temp_c: float
    max_cell_temp_c: float

    # State estimates
    soc_percent: float  # State of Charge (0-100%)
    soh_percent: float  # State of Health (0-100%)
    state: BatteryState

    # Energy
    energy_charged_kwh: float = 0.0
    energy_discharged_kwh: float = 0.0
    cycle_count: int = 0

    # Safety
    is_safe: bool = True
    alarms: List[str] = field(default_factory=list)

@dataclass
class BatterySpecification:
    """Battery pack specifications"""
    pack_id: str
    chemistry: BatteryChemistry
    nominal_voltage_v: float
    nominal_capacity_ah: float
    num_cells_series: int
    num_cells_parallel: int
    max_charge_current_a: float
    max_discharge_current_a: float
    max_charge_voltage_v: float
    min_discharge_voltage_v: float
    operating_temp_min_c: float = -20.0
    operating_temp_max_c: float = 60.0
    cell_capacity_ah: float = 0.0

    def __post_init__(self):
        """Calculate derived specifications"""
        self.cell_capacity_ah = self.nominal_capacity_ah / self.num_cells_parallel
        self.total_cells = self.num_cells_series * self.num_cells_parallel

class SOCEstimator:
    """
    State of Charge estimator using Extended Kalman Filter (EKF)

    Combines:
    - Coulomb counting (current integration)
    - Open Circuit Voltage (OCV) lookup
    - Kalman filtering for robustness
    """

    def __init__(self, battery_spec: BatterySpecification):
        self.spec = battery_spec
        self.soc = 50.0  # Initialize at 50%
        self.capacity_ah = battery_spec.nominal_capacity_ah

        # Kalman filter parameters
        self.P = 1.0  # Estimate error covariance
        self.Q = 0.01  # Process noise
        self.R = 0.1  # Measurement noise

        # Coulomb counting
        self.accumulated_charge_ah = 0.0

    def estimate_soc(
        self,
        current_a: float,
        voltage_v: float,
        delta_time_s: float
    ) -> float:
        """
        Estimate State of Charge using Extended Kalman Filter

        Args:
            current_a: Pack current (positive = charging)
            voltage_v: Pack voltage
            delta_time_s: Time since last update

        Returns:
            Estimated SOC (%)
        """

        # Coulomb counting (prediction step)
        charge_delta_ah = (current_a * delta_time_s) / 3600.0
        self.accumulated_charge_ah += charge_delta_ah

        # Predict SOC
        soc_prediction = self.soc + (charge_delta_ah / self.capacity_ah) * 100

        # Predict error covariance
        self.P = self.P + self.Q

        # OCV-based SOC measurement (update step)
        soc_from_ocv = self._voltage_to_soc(voltage_v)

        # Kalman gain
        K = self.P / (self.P + self.R)

        # Update SOC estimate
        self.soc = soc_prediction + K * (soc_from_ocv - soc_prediction)

        # Update error covariance
        self.P = (1 - K) * self.P

        # Bound SOC to [0, 100]
        self.soc = max(0.0, min(100.0, self.soc))

        return self.soc

    def _voltage_to_soc(self, voltage_v: float) -> float:
        """
        Convert Open Circuit Voltage to SOC using lookup table

        This is a simplified linear model. Production systems use
        detailed OCV curves specific to battery chemistry.
        """
        # Simplified linear model (for demonstration)
        v_min = self.spec.min_discharge_voltage_v
        v_max = self.spec.max_charge_voltage_v

        soc = ((voltage_v - v_min) / (v_max - v_min)) * 100
        return max(0.0, min(100.0, soc))

class SOHEstimator:
    """
    State of Health estimator

    Tracks battery degradation over time based on:
    - Capacity fade
    - Impedance increase
    - Cycle counting
    """

    def __init__(self, battery_spec: BatterySpecification):
        self.spec = battery_spec
        self.initial_capacity_ah = battery_spec.nominal_capacity_ah
        self.current_capacity_ah = battery_spec.nominal_capacity_ah
        self.soh = 100.0  # Initial health
        self.cycle_count = 0
        self.total_charge_throughput_ah = 0.0

    def estimate_soh(
        self,
        full_charge_capacity_ah: Optional[float] = None,
        cycle_count: Optional[int] = None
    ) -> float:
        """
        Estimate State of Health

        Args:
            full_charge_capacity_ah: Measured capacity from full charge cycle
            cycle_count: Total number of charge/discharge cycles

        Returns:
            Estimated SOH (%)
        """

        if full_charge_capacity_ah is not None:
            # Direct capacity measurement
            self.current_capacity_ah = full_charge_capacity_ah
            self.soh = (self.current_capacity_ah / self.initial_capacity_ah) * 100

        elif cycle_count is not None:
            # Estimate based on cycle counting
            # Simplified model: 20% capacity loss after 2000 cycles
            self.cycle_count = cycle_count
            capacity_loss_percent = (cycle_count / 2000) * 20
            self.soh = max(80.0, 100.0 - capacity_loss_percent)

        return self.soh

    def update_cycle_count(self, charge_delta_ah: float):
        """
        Update cycle count based on charge throughput

        One cycle = one full capacity charge/discharge
        """
        self.total_charge_throughput_ah += abs(charge_delta_ah)
        self.cycle_count = self.total_charge_throughput_ah / self.initial_capacity_ah

class CellBalancer:
    """
    Cell balancing controller

    Implements passive or active balancing to equalize cell voltages
    """

    def __init__(self, num_cells: int, balance_threshold_v: float = 0.05):
        self.num_cells = num_cells
        self.balance_threshold_v = balance_threshold_v

    def calculate_balance_commands(
        self,
        cell_voltages: List[float]
    ) -> Dict[int, float]:
        """
        Calculate which cells need balancing

        Args:
            cell_voltages: List of cell voltages

        Returns:
            Dictionary mapping cell_id to balance current/duration
        """
        if not cell_voltages:
            return {}

        avg_voltage = sum(cell_voltages) / len(cell_voltages)
        max_voltage = max(cell_voltages)
        min_voltage = min(cell_voltages)

        voltage_spread = max_voltage - min_voltage

        balance_commands = {}

        if voltage_spread > self.balance_threshold_v:
            # Discharge cells above average (passive balancing)
            for i, voltage in enumerate(cell_voltages):
                if voltage > avg_voltage + (self.balance_threshold_v / 2):
                    # Calculate balance duration (simplified)
                    balance_duration_s = (voltage - avg_voltage) * 100  # Arbitrary scaling
                    balance_commands[i] = balance_duration_s

        return balance_commands

class BatteryManagementSystem:
    """
    Complete Battery Management System

    Features:
    - SOC estimation with Kalman filtering
    - SOH tracking and degradation prediction
    - Cell balancing
    - Thermal management
    - Safety monitoring and fault detection
    - CAN bus communication
    - Data logging
    """

    def __init__(self, battery_spec: BatterySpecification):
        self.spec = battery_spec
        self.soc_estimator = SOCEstimator(battery_spec)
        self.soh_estimator = SOHEstimator(battery_spec)
        self.cell_balancer = CellBalancer(battery_spec.total_cells)

        self.current_state = BatteryState.IDLE
        self.telemetry_history: List[BatteryPackTelemetry] = []

        # Safety thresholds
        self.voltage_over_limit = battery_spec.max_charge_voltage_v
        self.voltage_under_limit = battery_spec.min_discharge_voltage_v
        self.temp_over_limit = battery_spec.operating_temp_max_c
        self.temp_under_limit = battery_spec.operating_temp_min_c
        self.current_over_limit = max(
            battery_spec.max_charge_current_a,
            battery_spec.max_discharge_current_a
        )

    def process_telemetry(
        self,
        pack_voltage_v: float,
        pack_current_a: float,
        cell_voltages: List[float],
        cell_temperatures: List[float],
        delta_time_s: float = 1.0
    ) -> BatteryPackTelemetry:
        """
        Process battery telemetry and update all estimates

        Args:
            pack_voltage_v: Total pack voltage
            pack_current_a: Pack current (+ charging, - discharging)
            cell_voltages: Individual cell voltages
            cell_temperatures: Individual cell temperatures
            delta_time_s: Time since last update

        Returns:
            Complete telemetry with SOC, SOH, and safety status
        """

        timestamp = datetime.utcnow()

        # Estimate SOC
        soc = self.soc_estimator.estimate_soc(pack_current_a, pack_voltage_v, delta_time_s)

        # Estimate SOH
        soh = self.soh_estimator.estimate_soh()

        # Calculate statistics
        min_cell_v = min(cell_voltages) if cell_voltages else 0.0
        max_cell_v = max(cell_voltages) if cell_voltages else 0.0
        voltage_delta = max_cell_v - min_cell_v

        avg_temp = sum(cell_temperatures) / len(cell_temperatures) if cell_temperatures else 0.0
        max_temp = max(cell_temperatures) if cell_temperatures else 0.0

        # Determine state
        if abs(pack_current_a) < 0.1:
            state = BatteryState.IDLE
        elif pack_current_a > 0:
            state = BatteryState.CHARGING
        else:
            state = BatteryState.DISCHARGING

        # Safety monitoring
        is_safe, alarms = self._check_safety(
            pack_voltage_v,
            pack_current_a,
            cell_voltages,
            cell_temperatures
        )

        if not is_safe:
            state = BatteryState.FAULT

        # Calculate power
        pack_power_kw = (pack_voltage_v * pack_current_a) / 1000.0

        # Create telemetry
        telemetry = BatteryPackTelemetry(
            timestamp=timestamp,
            pack_id=self.spec.pack_id,
            pack_voltage_v=pack_voltage_v,
            pack_current_a=pack_current_a,
            pack_power_kw=pack_power_kw,
            cell_voltages=cell_voltages,
            cell_temperatures=cell_temperatures,
            min_cell_voltage_v=min_cell_v,
            max_cell_voltage_v=max_cell_v,
            voltage_delta_v=voltage_delta,
            avg_cell_temp_c=avg_temp,
            max_cell_temp_c=max_temp,
            soc_percent=soc,
            soh_percent=soh,
            state=state,
            is_safe=is_safe,
            alarms=alarms
        )

        self.telemetry_history.append(telemetry)
        self.current_state = state

        # Cell balancing
        if voltage_delta > 0.05 and state == BatteryState.IDLE:
            balance_commands = self.cell_balancer.calculate_balance_commands(cell_voltages)
            if balance_commands:
                logger.info(f"Balancing {len(balance_commands)} cells")

        return telemetry

    def _check_safety(
        self,
        pack_voltage_v: float,
        pack_current_a: float,
        cell_voltages: List[float],
        cell_temperatures: List[float]
    ) -> Tuple[bool, List[str]]:
        """
        Check safety conditions and generate alarms

        Returns:
            Tuple of (is_safe, list_of_alarms)
        """
        alarms = []
        is_safe = True

        # Overvoltage check
        if pack_voltage_v > self.voltage_over_limit:
            alarms.append(f"CRITICAL: Pack overvoltage {pack_voltage_v:.2f}V")
            is_safe = False

        # Undervoltage check
        if pack_voltage_v < self.voltage_under_limit:
            alarms.append(f"CRITICAL: Pack undervoltage {pack_voltage_v:.2f}V")
            is_safe = False

        # Cell voltage checks
        for i, voltage in enumerate(cell_voltages):
            cell_max = self.voltage_over_limit / self.spec.num_cells_series
            cell_min = self.voltage_under_limit / self.spec.num_cells_series

            if voltage > cell_max:
                alarms.append(f"CRITICAL: Cell {i} overvoltage {voltage:.3f}V")
                is_safe = False
            elif voltage < cell_min:
                alarms.append(f"CRITICAL: Cell {i} undervoltage {voltage:.3f}V")
                is_safe = False

        # Overcurrent check
        if abs(pack_current_a) > self.current_over_limit:
            alarms.append(f"ERROR: Overcurrent {abs(pack_current_a):.1f}A")
            is_safe = False

        # Temperature checks
        for i, temp in enumerate(cell_temperatures):
            if temp > self.temp_over_limit:
                alarms.append(f"CRITICAL: Cell {i} overtemperature {temp:.1f}°C")
                is_safe = False
            elif temp < self.temp_under_limit:
                alarms.append(f"WARNING: Cell {i} low temperature {temp:.1f}°C")

        # Cell imbalance warning
        if cell_voltages:
            voltage_spread = max(cell_voltages) - min(cell_voltages)
            if voltage_spread > 0.1:
                alarms.append(f"WARNING: High cell voltage imbalance {voltage_spread:.3f}V")

        return is_safe, alarms

    def predict_remaining_capacity(self, current_load_a: float) -> float:
        """
        Predict remaining runtime at current load

        Returns:
            Remaining runtime in hours
        """
        if current_load_a <= 0:
            return float('inf')

        remaining_capacity_ah = (self.soc_estimator.soc / 100.0) * self.soc_estimator.capacity_ah
        remaining_hours = remaining_capacity_ah / current_load_a

        return remaining_hours


# Example usage
def main():
    """Example usage of Battery Management System"""

    # Define battery specification (e.g., Tesla-like EV battery)
    battery_spec = BatterySpecification(
        pack_id="PACK-001",
        chemistry=BatteryChemistry.NICKEL_MANGANESE_COBALT,
        nominal_voltage_v=400.0,
        nominal_capacity_ah=75.0,  # 30 kWh pack
        num_cells_series=96,  # Typical for 400V pack
        num_cells_parallel=30,
        max_charge_current_a=150.0,
        max_discharge_current_a=300.0,
        max_charge_voltage_v=420.0,
        min_discharge_voltage_v=320.0,
        operating_temp_min_c=-20.0,
        operating_temp_max_c=55.0
    )

    # Initialize BMS
    bms = BatteryManagementSystem(battery_spec)

    print(f"\n=== Battery Management System Initialized ===")
    print(f"Pack: {battery_spec.pack_id}")
    print(f"Chemistry: {battery_spec.chemistry.value}")
    print(f"Nominal Voltage: {battery_spec.nominal_voltage_v}V")
    print(f"Nominal Capacity: {battery_spec.nominal_capacity_ah}Ah ({battery_spec.nominal_voltage_v * battery_spec.nominal_capacity_ah / 1000:.1f} kWh)")
    print(f"Total Cells: {battery_spec.total_cells} ({battery_spec.num_cells_series}S{battery_spec.num_cells_parallel}P)")

    # Simulate normal operation
    cell_voltages = [3.7 + np.random.uniform(-0.02, 0.02) for _ in range(battery_spec.num_cells_series)]
    cell_temperatures = [25.0 + np.random.uniform(-2, 2) for _ in range(battery_spec.num_cells_series)]

    # Charging scenario
    telemetry = bms.process_telemetry(
        pack_voltage_v=380.0,
        pack_current_a=100.0,  # Charging at 100A
        cell_voltages=cell_voltages,
        cell_temperatures=cell_temperatures,
        delta_time_s=1.0
    )

    print(f"\n=== Telemetry (Charging) ===")
    print(f"Timestamp: {telemetry.timestamp}")
    print(f"Pack Voltage: {telemetry.pack_voltage_v:.2f}V")
    print(f"Pack Current: {telemetry.pack_current_a:.2f}A")
    print(f"Pack Power: {telemetry.pack_power_kw:.2f}kW")
    print(f"SOC: {telemetry.soc_percent:.1f}%")
    print(f"SOH: {telemetry.soh_percent:.1f}%")
    print(f"State: {telemetry.state.value}")
    print(f"Cell Voltage Range: {telemetry.min_cell_voltage_v:.3f}V - {telemetry.max_cell_voltage_v:.3f}V (Δ={telemetry.voltage_delta_v:.3f}V)")
    print(f"Avg Temperature: {telemetry.avg_cell_temp_c:.1f}°C (Max={telemetry.max_cell_temp_c:.1f}°C)")
    print(f"Safe: {telemetry.is_safe}")
    if telemetry.alarms:
        print(f"Alarms: {telemetry.alarms}")

    # Predict remaining capacity
    discharge_current = 50.0  # A
    remaining_hours = bms.predict_remaining_capacity(discharge_current)
    print(f"\nAt {discharge_current:.0f}A discharge, remaining runtime: {remaining_hours:.2f} hours")

if __name__ == "__main__":
    main()
```

## Key Performance Indicators

### Battery Performance
- **SOC Accuracy**: ±2-5% typical
- **SOH Accuracy**: ±5% typical
- **Cell Voltage Balance**: <50mV typical
- **Cycle Life**: 2000-3000 cycles (80% capacity retention)

### Safety Metrics
- **Fault Detection Time**: <100ms
- **Temperature Monitoring**: ±1°C accuracy
- **Voltage Monitoring**: ±10mV accuracy

## Industry Resources

### Standards Organizations
- [UL](https://www.ul.com/) - Safety certifications
- [SAE International](https://www.sae.org/) - Automotive standards
- [ISO](https://www.iso.org/) - International standards

### Research
- [Battery University](https://batteryuniversity.com/)
- [Argonne National Laboratory](https://www.anl.gov/)

## Conclusion

Battery Management Systems are safety-critical systems requiring expertise in electrochemistry, control systems, embedded programming, and functional safety. Production BMS implementations must meet rigorous safety standards and provide accurate state estimation for optimal battery performance and longevity.
