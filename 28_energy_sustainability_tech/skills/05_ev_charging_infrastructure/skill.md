# EV Charging Infrastructure - Production Implementation Guide

## Overview

EV Charging Infrastructure encompasses the hardware, software, and network systems that enable electric vehicle charging. This skill covers production-grade implementations of charging station management, OCPP protocol integration, smart charging optimization, load management, and Vehicle-to-Grid (V2G) systems.

## Core Technologies

### 1. Charging Levels
- **Level 1**: 120V AC, 1.4-1.9 kW, 3-5 miles/hour
- **Level 2**: 240V AC, 3.3-19.2 kW, 10-60 miles/hour
- **DC Fast Charging (Level 3)**: 50-350 kW, 3-20 miles/minute

### 2. Open Charge Point Protocol (OCPP)
Standard communication protocol between charging stations and central management systems.

### 3. Smart Charging
Dynamic power allocation based on grid conditions, pricing, and user preferences.

### 4. Vehicle-to-Grid (V2G)
Bidirectional power flow allowing EVs to provide grid services.

## Standards and Protocols

### Communication Standards
- **OCPP 1.6 / 2.0.1**: Open Charge Point Protocol
- **ISO 15118**: Vehicle-to-Grid communication
- **IEC 61851**: EV charging system standard
- **SAE J1772**: North American charging connector
- **CCS (Combined Charging System)**: Fast charging standard
- **CHAdeMO**: Japanese DC fast charging

### Payment and Roaming
- **OCPI**: Open Charge Point Interface (roaming)
- **OICP**: Open InterCharge Protocol
- **eMIP**: eMobility Interoperation Protocol

## Production-Grade Implementation Examples

### Example 1: OCPP 2.0.1 Charging Station Management System

```python
"""
Production-grade EV Charging Station Management System (CSMS)
Implements OCPP 2.0.1 protocol

References:
- OCPP 2.0.1 Specification
- ISO 15118: V2G communication
- IEC 61851: EV charging systems
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChargerStatus(Enum):
    """OCPP charger status"""
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    UNAVAILABLE = "Unavailable"
    RESERVED = "Reserved"
    FAULTED = "Faulted"

class ConnectorType(Enum):
    """EV connector types"""
    J1772 = "J1772"  # North America Level 2
    CCS1 = "CCS1"  # North America DC Fast
    CCS2 = "CCS2"  # Europe DC Fast
    CHADEMO = "CHAdeMO"  # Japanese DC Fast
    TESLA = "Tesla Supercharger"
    TYPE2 = "Type 2"  # Europe Level 2

class ChargingProfile(Enum):
    """Charging profile purpose"""
    CHARGE_POINT_MAX_PROFILE = "ChargePointMaxProfile"
    TX_DEFAULT_PROFILE = "TxDefaultProfile"
    TX_PROFILE = "TxProfile"

@dataclass
class Connector:
    """Charging station connector"""
    connector_id: int
    connector_type: ConnectorType
    max_power_kw: float
    status: ChargerStatus
    current_transaction_id: Optional[str] = None
    current_power_kw: float = 0.0
    energy_delivered_kwh: float = 0.0

@dataclass
class ChargingStation:
    """Physical charging station"""
    station_id: str
    name: str
    location: Dict[str, float]  # lat, lon
    connectors: List[Connector]
    total_power_capacity_kw: float
    firmware_version: str
    online: bool = True
    last_heartbeat: Optional[datetime] = None

@dataclass
class ChargingTransaction:
    """Active charging session"""
    transaction_id: str
    station_id: str
    connector_id: int
    id_tag: str  # RFID/user identifier
    start_time: datetime
    start_meter_kwh: float
    current_meter_kwh: float = 0.0
    charging_profile: Optional[Dict] = None
    stop_time: Optional[datetime] = None
    stop_reason: Optional[str] = None

@dataclass
class SmartChargingSchedule:
    """Smart charging power schedule"""
    start_time: datetime
    duration_minutes: int
    power_limits_kw: List[Tuple[datetime, float]]  # (time, power_kw)
    charging_rate_unit: str = "kW"

class OCPPMessage:
    """OCPP message structure"""
    def __init__(self, message_type: str, payload: Dict):
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.utcnow()

class ChargingStationManagementSystem:
    """
    Charging Station Management System (CSMS)

    Features:
    - OCPP 2.0.1 protocol implementation
    - Multi-station management
    - Smart charging optimization
    - Load management
    - Transaction processing
    - Billing integration
    - Real-time monitoring
    """

    def __init__(self, csms_id: str):
        self.csms_id = csms_id
        self.stations: Dict[str, ChargingStation] = {}
        self.transactions: Dict[str, ChargingTransaction] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> transaction_ids

    def register_station(self, station: ChargingStation) -> bool:
        """Register a new charging station"""
        if station.station_id in self.stations:
            logger.warning(f"Station {station.station_id} already registered")
            return False

        self.stations[station.station_id] = station
        logger.info(f"Registered station {station.station_id} with {len(station.connectors)} connectors")
        return True

    async def handle_boot_notification(
        self,
        station_id: str,
        charge_point_vendor: str,
        charge_point_model: str,
        firmware_version: str
    ) -> Dict:
        """
        Handle OCPP BootNotification message
        Sent by charging station on startup
        """
        if station_id not in self.stations:
            return {
                'status': 'Rejected',
                'currentTime': datetime.utcnow().isoformat(),
                'interval': 0
            }

        station = self.stations[station_id]
        station.online = True
        station.last_heartbeat = datetime.utcnow()
        station.firmware_version = firmware_version

        logger.info(f"Station {station_id} booted: {charge_point_vendor} {charge_point_model} v{firmware_version}")

        return {
            'status': 'Accepted',
            'currentTime': datetime.utcnow().isoformat(),
            'interval': 300  # Heartbeat interval in seconds
        }

    async def handle_status_notification(
        self,
        station_id: str,
        connector_id: int,
        status: ChargerStatus,
        error_code: Optional[str] = None
    ) -> Dict:
        """
        Handle OCPP StatusNotification message
        Sent when connector status changes
        """
        if station_id not in self.stations:
            return {'status': 'Rejected'}

        station = self.stations[station_id]

        # Find and update connector
        for connector in station.connectors:
            if connector.connector_id == connector_id:
                old_status = connector.status
                connector.status = status

                logger.info(
                    f"Station {station_id} Connector {connector_id}: "
                    f"{old_status.value} -> {status.value}"
                )

                if error_code:
                    logger.error(f"Station {station_id} Connector {connector_id}: Error {error_code}")

                break

        return {'status': 'Accepted'}

    async def start_transaction(
        self,
        station_id: str,
        connector_id: int,
        id_tag: str,
        meter_start_kwh: float
    ) -> Dict:
        """
        Start a charging transaction (OCPP StartTransaction)

        Returns transaction ID to charging station
        """
        if station_id not in self.stations:
            return {'idTagInfo': {'status': 'Invalid'}}

        station = self.stations[station_id]

        # Find connector
        connector = None
        for conn in station.connectors:
            if conn.connector_id == connector_id:
                connector = conn
                break

        if not connector or connector.status != ChargerStatus.AVAILABLE:
            return {'idTagInfo': {'status': 'Invalid'}}

        # Authorize user (simplified - production would check against backend)
        authorized = self._authorize_user(id_tag)
        if not authorized:
            return {'idTagInfo': {'status': 'Invalid'}}

        # Create transaction
        transaction_id = f"TXN-{station_id}-{connector_id}-{datetime.utcnow().timestamp()}"

        transaction = ChargingTransaction(
            transaction_id=transaction_id,
            station_id=station_id,
            connector_id=connector_id,
            id_tag=id_tag,
            start_time=datetime.utcnow(),
            start_meter_kwh=meter_start_kwh,
            current_meter_kwh=meter_start_kwh
        )

        self.transactions[transaction_id] = transaction
        connector.current_transaction_id = transaction_id
        connector.status = ChargerStatus.OCCUPIED

        # Track user sessions
        if id_tag not in self.user_sessions:
            self.user_sessions[id_tag] = []
        self.user_sessions[id_tag].append(transaction_id)

        logger.info(
            f"Started transaction {transaction_id} for user {id_tag} "
            f"at {station_id} connector {connector_id}"
        )

        return {
            'idTagInfo': {'status': 'Accepted'},
            'transactionId': transaction_id
        }

    async def stop_transaction(
        self,
        transaction_id: str,
        meter_stop_kwh: float,
        reason: str = "Local"
    ) -> Dict:
        """
        Stop a charging transaction (OCPP StopTransaction)
        """
        if transaction_id not in self.transactions:
            return {'idTagInfo': {'status': 'Invalid'}}

        transaction = self.transactions[transaction_id]
        transaction.stop_time = datetime.utcnow()
        transaction.stop_reason = reason
        transaction.current_meter_kwh = meter_stop_kwh

        # Update connector
        station = self.stations[transaction.station_id]
        for connector in station.connectors:
            if connector.connector_id == transaction.connector_id:
                connector.current_transaction_id = None
                connector.status = ChargerStatus.AVAILABLE
                connector.energy_delivered_kwh = 0.0
                connector.current_power_kw = 0.0
                break

        # Calculate charging session details
        energy_delivered = meter_stop_kwh - transaction.start_meter_kwh
        duration = (transaction.stop_time - transaction.start_time).total_seconds() / 3600  # hours

        logger.info(
            f"Stopped transaction {transaction_id}: "
            f"{energy_delivered:.2f} kWh delivered in {duration:.2f} hours"
        )

        # In production, send to billing system
        cost = self._calculate_cost(transaction)

        return {
            'idTagInfo': {'status': 'Accepted'},
            'energy_kwh': energy_delivered,
            'duration_hours': duration,
            'cost': cost
        }

    async def apply_smart_charging_profile(
        self,
        station_id: str,
        connector_id: int,
        schedule: SmartChargingSchedule
    ) -> bool:
        """
        Apply smart charging profile to limit power

        Used for:
        - Load management
        - Demand response
        - Time-of-use optimization
        - Grid constraints
        """
        if station_id not in self.stations:
            return False

        station = self.stations[station_id]

        # Find connector
        connector = None
        for conn in station.connectors:
            if conn.connector_id == connector_id:
                connector = conn
                break

        if not connector or not connector.current_transaction_id:
            return False

        transaction = self.transactions[connector.current_transaction_id]

        # Create OCPP SetChargingProfile message
        charging_profile = {
            'chargingProfileId': f"PROFILE-{station_id}-{connector_id}-{datetime.utcnow().timestamp()}",
            'stackLevel': 0,
            'chargingProfilePurpose': ChargingProfile.TX_PROFILE.value,
            'chargingProfileKind': 'Absolute',
            'chargingSchedule': {
                'startSchedule': schedule.start_time.isoformat(),
                'duration': schedule.duration_minutes * 60,
                'chargingRateUnit': schedule.charging_rate_unit,
                'chargingSchedulePeriod': [
                    {
                        'startPeriod': int((time - schedule.start_time).total_seconds()),
                        'limit': power_kw
                    }
                    for time, power_kw in schedule.power_limits_kw
                ]
            }
        }

        transaction.charging_profile = charging_profile

        logger.info(
            f"Applied smart charging profile to {station_id} connector {connector_id}: "
            f"Max {max(p[1] for p in schedule.power_limits_kw):.1f} kW"
        )

        return True

    def get_available_power(self, station_id: str) -> float:
        """Calculate available power capacity at station"""
        if station_id not in self.stations:
            return 0.0

        station = self.stations[station_id]
        used_power = sum(
            conn.current_power_kw
            for conn in station.connectors
            if conn.status == ChargerStatus.OCCUPIED
        )

        return station.total_power_capacity_kw - used_power

    def optimize_load_distribution(self, station_id: str, target_power_kw: float):
        """
        Distribute available power across active charging sessions

        Implements fair load sharing when total demand exceeds capacity
        """
        if station_id not in self.stations:
            return

        station = self.stations[station_id]

        # Get active connectors
        active_connectors = [
            conn for conn in station.connectors
            if conn.status == ChargerStatus.OCCUPIED
        ]

        if not active_connectors:
            return

        # Equal distribution
        power_per_connector = min(
            target_power_kw / len(active_connectors),
            max(conn.max_power_kw for conn in active_connectors)
        )

        for connector in active_connectors:
            # Apply power limit via smart charging profile
            schedule = SmartChargingSchedule(
                start_time=datetime.utcnow(),
                duration_minutes=15,
                power_limits_kw=[(datetime.utcnow(), power_per_connector)]
            )

            asyncio.create_task(
                self.apply_smart_charging_profile(
                    station_id,
                    connector.connector_id,
                    schedule
                )
            )

        logger.info(
            f"Optimized load at {station_id}: {power_per_connector:.1f} kW per connector "
            f"({len(active_connectors)} active)"
        )

    def _authorize_user(self, id_tag: str) -> bool:
        """Authorize user (simplified - production uses backend)"""
        # In production, check against user database, payment methods, etc.
        return True

    def _calculate_cost(self, transaction: ChargingTransaction) -> float:
        """Calculate charging session cost"""
        energy_kwh = transaction.current_meter_kwh - transaction.start_meter_kwh
        duration_hours = (transaction.stop_time - transaction.start_time).total_seconds() / 3600

        # Simplified pricing: $0.25/kWh + $2.00 session fee
        cost = (energy_kwh * 0.25) + 2.00

        return round(cost, 2)

    def get_station_statistics(self) -> Dict:
        """Get CSMS statistics"""
        total_stations = len(self.stations)
        online_stations = sum(1 for s in self.stations.values() if s.online)
        total_connectors = sum(len(s.connectors) for s in self.stations.values())
        available_connectors = sum(
            1 for s in self.stations.values()
            for c in s.connectors
            if c.status == ChargerStatus.AVAILABLE
        )
        active_transactions = len([t for t in self.transactions.values() if t.stop_time is None])

        return {
            'total_stations': total_stations,
            'online_stations': online_stations,
            'total_connectors': total_connectors,
            'available_connectors': available_connectors,
            'active_transactions': active_transactions,
            'total_power_capacity_kw': sum(s.total_power_capacity_kw for s in self.stations.values())
        }


# Example usage
async def main():
    """Example usage of Charging Station Management System"""

    # Initialize CSMS
    csms = ChargingStationManagementSystem("CSMS-001")

    # Register charging stations
    station1 = ChargingStation(
        station_id="CS-001",
        name="Downtown Station A",
        location={'lat': 37.7749, 'lon': -122.4194},
        connectors=[
            Connector(1, ConnectorType.J1772, 7.2, ChargerStatus.AVAILABLE),
            Connector(2, ConnectorType.CCS1, 50.0, ChargerStatus.AVAILABLE)
        ],
        total_power_capacity_kw=60.0,
        firmware_version="2.1.0"
    )

    csms.register_station(station1)

    print(f"\n=== Charging Station Management System ===")
    print(f"CSMS ID: {csms.csms_id}")

    # Simulate boot notification
    boot_response = await csms.handle_boot_notification(
        "CS-001",
        "ChargePoint",
        "CP-DC50",
        "2.1.0"
    )
    print(f"\nBoot Notification Response: {boot_response['status']}")

    # Simulate status notification
    await csms.handle_status_notification(
        "CS-001",
        1,
        ChargerStatus.AVAILABLE
    )

    # Start charging transaction
    start_response = await csms.start_transaction(
        "CS-001",
        1,
        "RFID-USER-123",
        0.0
    )

    transaction_id = start_response.get('transactionId')
    print(f"\nStarted Transaction: {transaction_id}")
    print(f"Authorization: {start_response['idTagInfo']['status']}")

    # Apply smart charging (limit to 5kW during peak hours)
    schedule = SmartChargingSchedule(
        start_time=datetime.utcnow(),
        duration_minutes=60,
        power_limits_kw=[
            (datetime.utcnow(), 5.0),
            (datetime.utcnow() + timedelta(minutes=30), 7.2)
        ]
    )

    await csms.apply_smart_charging_profile("CS-001", 1, schedule)
    print(f"\nApplied smart charging profile: 5kW for 30min, then 7.2kW")

    # Simulate charging completion
    await asyncio.sleep(0.1)  # Simulate time passing

    stop_response = await csms.stop_transaction(
        transaction_id,
        15.5,  # 15.5 kWh delivered
        "Local"
    )

    print(f"\nStopped Transaction:")
    print(f"  Energy Delivered: {stop_response['energy_kwh']:.2f} kWh")
    print(f"  Duration: {stop_response['duration_hours']:.2f} hours")
    print(f"  Cost: ${stop_response['cost']:.2f}")

    # Get statistics
    stats = csms.get_station_statistics()
    print(f"\n=== CSMS Statistics ===")
    print(f"Total Stations: {stats['total_stations']}")
    print(f"Online Stations: {stats['online_stations']}")
    print(f"Total Connectors: {stats['total_connectors']}")
    print(f"Available Connectors: {stats['available_connectors']}")
    print(f"Active Transactions: {stats['active_transactions']}")
    print(f"Total Power Capacity: {stats['total_power_capacity_kw']:.1f} kW")

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture Patterns

### Pattern 1: Distributed Charging Network

```
┌──────────────────────────────────────────────────────┐
│    Central Management System (CSMS)                  │
│  - Station management                                │
│  - User management                                   │
│  - Billing                                           │
│  - Analytics                                         │
└────────────────────┬─────────────────────────────────┘
                     │ OCPP 2.0.1 / WebSocket
┌────────────────────┴─────────────────────────────────┐
│         Charging Stations (Distributed)              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  │
│  │ CS-1 │  │ CS-2 │  │ CS-3 │  │ CS-4 │  │ CS-5 │  │
│  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘  │
│     │         │         │         │         │       │
│  ┌──▼──┐   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐  │
│  │ EV  │   │ EV  │   │ EV  │   │ EV  │   │ EV  │  │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘  │
└──────────────────────────────────────────────────────┘
```

## Key Performance Indicators

### Operational KPIs
- **Uptime**: Target >99%
- **Utilization**: % of time connectors in use
- **Session Success Rate**: Target >95%
- **Average Session Duration**: Hours
- **Energy Throughput**: kWh/day

### Financial KPIs
- **Revenue per kWh**: $/kWh
- **Revenue per station**: $/month
- **Customer Acquisition Cost**: $
- **Return on Investment**: Years

## Industry Resources

### Standards Organizations
- [Open Charge Alliance](https://www.openchargealliance.org/)
- [CharIN](https://www.charin.global/) - CCS standard
- [ISO/IEC](https://www.iso.org/)

### Tools and Platforms
- **OCPP Testing Tools**: OCPP Compliance Testing
- **Steve**: Open-source CSMS
- **CitrineOS**: Open-source OCPP implementation

## Conclusion

EV Charging Infrastructure requires expertise in power systems, communication protocols, payment processing, and user experience. Production systems must be reliable, secure, and interoperable across multiple vendors and networks. OCPP provides the foundation for interoperability in the growing EV charging ecosystem.
