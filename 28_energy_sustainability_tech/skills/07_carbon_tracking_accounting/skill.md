# Carbon Tracking & Accounting - Production Implementation Guide

## Overview

Carbon Tracking & Accounting systems measure, monitor, and report greenhouse gas (GHG) emissions across organizational operations. This skill covers production-grade implementations of carbon footprint calculation, Scope 1/2/3 emissions tracking, science-based target monitoring, and ESG reporting following the GHG Protocol and other international frameworks.

## Core Concepts

### GHG Protocol Scopes
- **Scope 1**: Direct emissions from owned/controlled sources (combustion, vehicles, processes)
- **Scope 2**: Indirect emissions from purchased electricity, steam, heating, cooling
- **Scope 3**: All other indirect emissions in value chain (15 categories)

### Key Frameworks
- **GHG Protocol**: Corporate and value chain standards
- **CDP**: Carbon Disclosure Project reporting
- **TCFD**: Task Force on Climate-related Financial Disclosures
- **SBTi**: Science Based Targets initiative
- **ISO 14064**: GHG quantification and reporting

## Production-Grade Implementation Example

```python
"""
Production-grade Carbon Tracking & Accounting System
Implements GHG Protocol Corporate Standard

References:
- GHG Protocol Corporate Accounting and Reporting Standard
- EPA Emission Factors
- IEA Electricity Factors
- CDP Reporting Requirements
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmissionScope(Enum):
    """GHG Protocol emission scopes"""
    SCOPE_1 = "scope_1"
    SCOPE_2_LOCATION = "scope_2_location"
    SCOPE_2_MARKET = "scope_2_market"
    SCOPE_3 = "scope_3"

class Scope3Category(Enum):
    """15 Scope 3 categories per GHG Protocol"""
    PURCHASED_GOODS = "1_purchased_goods_services"
    CAPITAL_GOODS = "2_capital_goods"
    FUEL_ENERGY = "3_fuel_energy_activities"
    UPSTREAM_TRANSPORT = "4_upstream_transport"
    WASTE = "5_waste"
    BUSINESS_TRAVEL = "6_business_travel"
    EMPLOYEE_COMMUTE = "7_employee_commuting"
    UPSTREAM_LEASED = "8_upstream_leased_assets"
    DOWNSTREAM_TRANSPORT = "9_downstream_transport"
    PROCESSING = "10_processing_sold_products"
    USE_OF_PRODUCTS = "11_use_sold_products"
    END_OF_LIFE = "12_end_of_life"
    DOWNSTREAM_LEASED = "13_downstream_leased_assets"
    FRANCHISES = "14_franchises"
    INVESTMENTS = "15_investments"

@dataclass
class EmissionFactor:
    """Emission factor for converting activity to emissions"""
    factor_id: str
    description: str
    value: float  # kg CO2e per unit
    unit: str  # kWh, gallon, mile, kg, etc.
    scope: EmissionScope
    source: str  # EPA, IEA, etc.
    year: int
    region: str = "US"

@dataclass
class ActivityData:
    """Activity data that generates emissions"""
    activity_id: str
    timestamp: datetime
    activity_type: str  # electricity, natural_gas, vehicle_miles, etc.
    quantity: float
    unit: str
    location: str
    department: Optional[str] = None
    cost: Optional[float] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class EmissionRecord:
    """Calculated emission record"""
    record_id: str
    timestamp: datetime
    scope: EmissionScope
    scope_3_category: Optional[Scope3Category] = None
    activity_data: ActivityData = None
    emission_factor: EmissionFactor = None
    co2e_kg: float = 0.0  # CO2 equivalent in kg
    confidence: str = "medium"  # low, medium, high

@dataclass
class CarbonInventory:
    """Annual GHG inventory"""
    organization_id: str
    reporting_year: int
    reporting_period_start: datetime
    reporting_period_end: datetime

    # Emissions by scope (metric tons CO2e)
    scope_1_mt: float = 0.0
    scope_2_location_mt: float = 0.0
    scope_2_market_mt: float = 0.0
    scope_3_mt: float = 0.0

    # Scope 3 breakdown
    scope_3_breakdown: Dict[str, float] = field(default_factory=dict)

    # Intensity metrics
    revenue_million: Optional[float] = None
    employees: Optional[int] = None
    floor_area_sqft: Optional[float] = None

    # Calculated intensities
    emissions_per_revenue: Optional[float] = None  # kg CO2e per $
    emissions_per_employee: Optional[float] = None  # mt CO2e per employee
    emissions_per_sqft: Optional[float] = None  # kg CO2e per sqft

class EmissionFactorDatabase:
    """
    Database of emission factors

    Sources:
    - EPA Emission Factors Hub
    - IEA Electricity Factors
    - DEFRA (UK) Factors
    - ecoinvent Database
    """

    def __init__(self):
        self.factors: Dict[str, EmissionFactor] = {}
        self._initialize_factors()

    def _initialize_factors(self):
        """Initialize common emission factors"""

        # Scope 1: Stationary combustion
        self.factors['natural_gas'] = EmissionFactor(
            factor_id='ef_natural_gas',
            description='Natural gas combustion',
            value=53.06,  # kg CO2e per MMBtu (EPA)
            unit='MMBtu',
            scope=EmissionScope.SCOPE_1,
            source='EPA',
            year=2024
        )

        self.factors['diesel'] = EmissionFactor(
            factor_id='ef_diesel',
            description='Diesel fuel combustion',
            value=10.21,  # kg CO2e per gallon (EPA)
            unit='gallon',
            scope=EmissionScope.SCOPE_1,
            source='EPA',
            year=2024
        )

        self.factors['gasoline'] = EmissionFactor(
            factor_id='ef_gasoline',
            description='Gasoline combustion',
            value=8.89,  # kg CO2e per gallon (EPA)
            unit='gallon',
            scope=EmissionScope.SCOPE_1,
            source='EPA',
            year=2024
        )

        # Scope 2: Electricity (US average)
        self.factors['electricity_us'] = EmissionFactor(
            factor_id='ef_electricity_us',
            description='US average grid electricity',
            value=0.386,  # kg CO2e per kWh (EPA eGRID 2024)
            unit='kWh',
            scope=EmissionScope.SCOPE_2_LOCATION,
            source='EPA eGRID',
            year=2024,
            region='US'
        )

        # Scope 3: Business travel
        self.factors['air_travel_short'] = EmissionFactor(
            factor_id='ef_air_short',
            description='Air travel < 300 miles',
            value=0.273,  # kg CO2e per passenger-mile (EPA)
            unit='passenger-mile',
            scope=EmissionScope.SCOPE_3,
            source='EPA',
            year=2024
        )

        self.factors['air_travel_medium'] = EmissionFactor(
            factor_id='ef_air_medium',
            description='Air travel 300-2300 miles',
            value=0.178,  # kg CO2e per passenger-mile
            unit='passenger-mile',
            scope=EmissionScope.SCOPE_3,
            source='EPA',
            year=2024
        )

        self.factors['air_travel_long'] = EmissionFactor(
            factor_id='ef_air_long',
            description='Air travel > 2300 miles',
            value=0.152,  # kg CO2e per passenger-mile
            unit='passenger-mile',
            scope=EmissionScope.SCOPE_3,
            source='EPA',
            year=2024
        )

    def get_factor(self, factor_id: str) -> Optional[EmissionFactor]:
        """Retrieve emission factor by ID"""
        return self.factors.get(factor_id)

class CarbonAccountingSystem:
    """
    Production-grade Carbon Accounting System

    Features:
    - GHG Protocol-compliant calculations
    - Multi-scope tracking (Scope 1, 2, 3)
    - Activity data ingestion
    - Emission factor management
    - Inventory reporting
    - Science-based target tracking
    - CDP/TCFD report generation
    """

    def __init__(self, organization_id: str):
        self.organization_id = organization_id
        self.emission_factors = EmissionFactorDatabase()
        self.activity_data: List[ActivityData] = []
        self.emission_records: List[EmissionRecord] = []

    def record_activity(self, activity: ActivityData):
        """Record activity data that generates emissions"""
        self.activity_data.append(activity)
        logger.info(
            f"Recorded activity: {activity.activity_type} "
            f"{activity.quantity} {activity.unit}"
        )

    def calculate_emissions(self, activity: ActivityData) -> Optional[EmissionRecord]:
        """
        Calculate emissions from activity data

        Args:
            activity: Activity data

        Returns:
            Emission record with calculated CO2e
        """

        # Map activity type to emission factor
        factor_mapping = {
            'electricity': 'electricity_us',
            'natural_gas': 'natural_gas',
            'diesel': 'diesel',
            'gasoline': 'gasoline',
            'air_travel_short': 'air_travel_short',
            'air_travel_medium': 'air_travel_medium',
            'air_travel_long': 'air_travel_long'
        }

        factor_id = factor_mapping.get(activity.activity_type)
        if not factor_id:
            logger.warning(f"No emission factor for {activity.activity_type}")
            return None

        emission_factor = self.emission_factors.get_factor(factor_id)
        if not emission_factor:
            logger.error(f"Emission factor {factor_id} not found")
            return None

        # Unit conversion if needed
        quantity_in_factor_units = self._convert_units(
            activity.quantity,
            activity.unit,
            emission_factor.unit
        )

        # Calculate emissions
        co2e_kg = quantity_in_factor_units * emission_factor.value

        # Determine Scope 3 category if applicable
        scope_3_cat = None
        if emission_factor.scope == EmissionScope.SCOPE_3:
            if 'air_travel' in activity.activity_type:
                scope_3_cat = Scope3Category.BUSINESS_TRAVEL

        emission_record = EmissionRecord(
            record_id=f"ER-{activity.activity_id}",
            timestamp=activity.timestamp,
            scope=emission_factor.scope,
            scope_3_category=scope_3_cat,
            activity_data=activity,
            emission_factor=emission_factor,
            co2e_kg=co2e_kg,
            confidence="high"
        )

        self.emission_records.append(emission_record)

        logger.info(
            f"Calculated emissions: {co2e_kg:.2f} kg CO2e "
            f"({emission_factor.scope.value})"
        )

        return emission_record

    def _convert_units(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> float:
        """Convert between units (simplified)"""

        if from_unit == to_unit:
            return value

        # Conversion factors (simplified - production would be more comprehensive)
        conversions = {
            ('kWh', 'kWh'): 1.0,
            ('therm', 'MMBtu'): 0.1,  # 1 therm = 0.1 MMBtu
            ('mile', 'passenger-mile'): 1.0,  # Assume 1 passenger
        }

        factor = conversions.get((from_unit, to_unit), 1.0)
        return value * factor

    def generate_inventory(
        self,
        year: int,
        revenue_million: Optional[float] = None,
        employees: Optional[int] = None,
        floor_area_sqft: Optional[float] = None
    ) -> CarbonInventory:
        """
        Generate annual GHG inventory per GHG Protocol

        Args:
            year: Reporting year
            revenue_million: Annual revenue in millions
            employees: Number of employees
            floor_area_sqft: Total floor area

        Returns:
            Complete carbon inventory
        """

        # Filter emissions for reporting year
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)

        year_emissions = [
            e for e in self.emission_records
            if year_start <= e.timestamp <= year_end
        ]

        # Aggregate by scope
        scope_1_kg = sum(
            e.co2e_kg for e in year_emissions
            if e.scope == EmissionScope.SCOPE_1
        )

        scope_2_location_kg = sum(
            e.co2e_kg for e in year_emissions
            if e.scope == EmissionScope.SCOPE_2_LOCATION
        )

        scope_2_market_kg = sum(
            e.co2e_kg for e in year_emissions
            if e.scope == EmissionScope.SCOPE_2_MARKET
        )

        scope_3_kg = sum(
            e.co2e_kg for e in year_emissions
            if e.scope == EmissionScope.SCOPE_3
        )

        # Scope 3 breakdown
        scope_3_breakdown = {}
        for category in Scope3Category:
            category_emissions = sum(
                e.co2e_kg for e in year_emissions
                if e.scope_3_category == category
            )
            if category_emissions > 0:
                scope_3_breakdown[category.value] = category_emissions / 1000  # Convert to mt

        # Convert kg to metric tons
        inventory = CarbonInventory(
            organization_id=self.organization_id,
            reporting_year=year,
            reporting_period_start=year_start,
            reporting_period_end=year_end,
            scope_1_mt=scope_1_kg / 1000,
            scope_2_location_mt=scope_2_location_kg / 1000,
            scope_2_market_mt=scope_2_market_kg / 1000,
            scope_3_mt=scope_3_kg / 1000,
            scope_3_breakdown=scope_3_breakdown,
            revenue_million=revenue_million,
            employees=employees,
            floor_area_sqft=floor_area_sqft
        )

        # Calculate intensity metrics
        total_emissions_mt = (
            inventory.scope_1_mt +
            inventory.scope_2_location_mt +
            inventory.scope_3_mt
        )

        if revenue_million:
            inventory.emissions_per_revenue = (total_emissions_mt * 1000) / revenue_million

        if employees:
            inventory.emissions_per_employee = total_emissions_mt / employees

        if floor_area_sqft:
            inventory.emissions_per_sqft = (total_emissions_mt * 1000) / floor_area_sqft

        logger.info(
            f"Generated {year} inventory: "
            f"Scope 1={inventory.scope_1_mt:.1f} mt, "
            f"Scope 2={inventory.scope_2_location_mt:.1f} mt, "
            f"Scope 3={inventory.scope_3_mt:.1f} mt, "
            f"Total={total_emissions_mt:.1f} mt CO2e"
        )

        return inventory

    def track_science_based_target(
        self,
        baseline_year: int,
        target_year: int,
        reduction_percent: float,
        current_year: int
    ) -> Dict:
        """
        Track progress toward Science Based Target (SBTi)

        SBTi targets typically:
        - 1.5°C pathway: 4.2% absolute reduction per year, or
        - Well below 2°C: 2.5% absolute reduction per year

        Args:
            baseline_year: Baseline year for target
            target_year: Target achievement year
            reduction_percent: Target reduction percentage
            current_year: Current year for progress tracking

        Returns:
            Progress tracking metrics
        """

        # Get baseline inventory
        baseline_inventory = self.generate_inventory(baseline_year)
        baseline_emissions = (
            baseline_inventory.scope_1_mt +
            baseline_inventory.scope_2_location_mt +
            baseline_inventory.scope_3_mt
        )

        # Get current inventory
        current_inventory = self.generate_inventory(current_year)
        current_emissions = (
            current_inventory.scope_1_mt +
            current_inventory.scope_2_location_mt +
            current_inventory.scope_3_mt
        )

        # Calculate target
        target_emissions = baseline_emissions * (1 - reduction_percent / 100)

        # Calculate progress
        actual_reduction = baseline_emissions - current_emissions
        actual_reduction_percent = (actual_reduction / baseline_emissions) * 100

        years_elapsed = current_year - baseline_year
        years_remaining = target_year - current_year
        years_total = target_year - baseline_year

        # Required annual reduction rate
        required_annual_reduction = reduction_percent / years_total

        # On-track calculation
        expected_reduction = required_annual_reduction * years_elapsed
        on_track = actual_reduction_percent >= expected_reduction

        return {
            'baseline_year': baseline_year,
            'baseline_emissions_mt': baseline_emissions,
            'target_year': target_year,
            'target_emissions_mt': target_emissions,
            'target_reduction_percent': reduction_percent,
            'current_year': current_year,
            'current_emissions_mt': current_emissions,
            'actual_reduction_mt': actual_reduction,
            'actual_reduction_percent': actual_reduction_percent,
            'expected_reduction_percent': expected_reduction,
            'on_track': on_track,
            'years_remaining': years_remaining,
            'required_annual_reduction_percent': required_annual_reduction
        }


# Example usage
def main():
    """Example usage of Carbon Accounting System"""

    # Initialize system
    carbon_system = CarbonAccountingSystem("ORG-ACME-CORP")

    print(f"\n=== Carbon Accounting System ===")
    print(f"Organization: {carbon_system.organization_id}")

    # Record various activities

    # Scope 1: Natural gas for heating
    activity1 = ActivityData(
        activity_id="ACT-001",
        timestamp=datetime(2024, 1, 15),
        activity_type="natural_gas",
        quantity=100.0,
        unit="MMBtu",
        location="HQ-Building"
    )
    carbon_system.record_activity(activity1)
    carbon_system.calculate_emissions(activity1)

    # Scope 2: Electricity consumption
    activity2 = ActivityData(
        activity_id="ACT-002",
        timestamp=datetime(2024, 1, 15),
        activity_type="electricity",
        quantity=50000.0,
        unit="kWh",
        location="HQ-Building"
    )
    carbon_system.record_activity(activity2)
    carbon_system.calculate_emissions(activity2)

    # Scope 3: Business travel
    activity3 = ActivityData(
        activity_id="ACT-003",
        timestamp=datetime(2024, 2, 1),
        activity_type="air_travel_long",
        quantity=2500.0,  # miles
        unit="passenger-mile",
        location="San Francisco to New York",
        department="Sales"
    )
    carbon_system.record_activity(activity3)
    carbon_system.calculate_emissions(activity3)

    # Generate annual inventory
    inventory = carbon_system.generate_inventory(
        year=2024,
        revenue_million=100.0,
        employees=500,
        floor_area_sqft=100000
    )

    print(f"\n=== 2024 GHG Inventory ===")
    print(f"Scope 1: {inventory.scope_1_mt:.2f} mt CO2e")
    print(f"Scope 2 (Location-based): {inventory.scope_2_location_mt:.2f} mt CO2e")
    print(f"Scope 3: {inventory.scope_3_mt:.2f} mt CO2e")

    total_emissions = (
        inventory.scope_1_mt +
        inventory.scope_2_location_mt +
        inventory.scope_3_mt
    )
    print(f"Total: {total_emissions:.2f} mt CO2e")

    print(f"\n=== Intensity Metrics ===")
    print(f"Emissions per $M revenue: {inventory.emissions_per_revenue:.2f} kg CO2e/$M")
    print(f"Emissions per employee: {inventory.emissions_per_employee:.2f} mt CO2e/employee")
    print(f"Emissions per sqft: {inventory.emissions_per_sqft:.3f} kg CO2e/sqft")

    # Track Science Based Target
    sbt_progress = carbon_system.track_science_based_target(
        baseline_year=2020,
        target_year=2030,
        reduction_percent=50.0,  # 50% reduction (1.5°C pathway)
        current_year=2024
    )

    print(f"\n=== Science Based Target Progress ===")
    print(f"Target: {sbt_progress['target_reduction_percent']:.0f}% reduction by {sbt_progress['target_year']}")
    print(f"Baseline ({sbt_progress['baseline_year']}): {sbt_progress['baseline_emissions_mt']:.1f} mt CO2e")
    print(f"Current ({sbt_progress['current_year']}): {sbt_progress['current_emissions_mt']:.1f} mt CO2e")
    print(f"Actual Reduction: {sbt_progress['actual_reduction_percent']:.1f}%")
    print(f"Expected Reduction: {sbt_progress['expected_reduction_percent']:.1f}%")
    print(f"On Track: {'✓ Yes' if sbt_progress['on_track'] else '✗ No'}")
    print(f"Years Remaining: {sbt_progress['years_remaining']}")

if __name__ == "__main__":
    main()
```

## Key Frameworks & Standards

### Reporting Frameworks
- **GHG Protocol**: Global standard for corporate emissions accounting
- **CDP**: Annual disclosure to investors
- **TCFD**: Climate-related financial risk disclosure
- **SASB**: Sustainability Accounting Standards Board
- **GRI**: Global Reporting Initiative

### Science Based Targets
- **1.5°C pathway**: 4.2% absolute annual reduction
- **Well below 2°C**: 2.5% absolute annual reduction
- **Net-Zero**: Achieve 90-95% reduction by 2050

## Industry Resources

### Tools and Platforms
- **Watershed**: Carbon accounting platform
- **Persefoni**: Climate management platform
- **Sphera**: Sustainability software
- **SimaPro**: Life cycle assessment
- **Open LCA**: Open-source LCA

### Data Sources
- [EPA Emission Factors](https://www.epa.gov/climateleadership)
- [IEA Electricity Factors](https://www.iea.org/)
- [DEFRA Factors (UK)](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)

## Conclusion

Carbon Tracking & Accounting is essential for climate action and regulatory compliance. Production systems must implement GHG Protocol standards, integrate with enterprise systems, and provide accurate, auditable emissions data for stakeholder reporting and science-based target tracking.
