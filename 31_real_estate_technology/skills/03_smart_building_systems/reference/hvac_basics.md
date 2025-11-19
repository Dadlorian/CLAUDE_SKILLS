# HVAC Basics Reference

Comprehensive reference for HVAC system types, control strategies, and optimization techniques in commercial real estate.

## HVAC System Types

### Central Air Handling Systems

#### VAV (Variable Air Volume)
- **Description**: Adjusts airflow to each zone based on demand while maintaining constant supply temperature
- **Components**: AHU, VAV boxes with dampers, reheat coils (optional), zone thermostats
- **Capacity Range**: 5,000 - 100,000+ CFM
- **Applications**: Office buildings, hospitals, schools (>20,000 sq ft)
- **Energy Efficiency**: Excellent (30-50% savings vs. CAV)
- **Cost**: $8-15 per sq ft installed
- **Advantages**:
  - Individual zone control
  - Reduced fan energy at partial loads
  - Better humidity control
  - Quiet operation
- **Disadvantages**:
  - Higher initial cost
  - More complex controls
  - Requires minimum airflow for ventilation

**Typical VAV Box Types:**
- **Cooling-only**: Damper modulates airflow, economical
- **Reheat**: Adds heat for zones requiring warming, higher energy use
- **Dual-duct**: Separate hot and cold ducts, maximum flexibility
- **Fan-powered**: Series or parallel fan for better air distribution

#### CAV (Constant Air Volume)
- **Description**: Constant airflow with temperature modulation
- **Applications**: Process areas, laboratories, critical environments
- **Energy Efficiency**: Lower than VAV (baseline)
- **Cost**: $6-10 per sq ft installed
- **Advantages**:
  - Simple, reliable
  - Lower first cost
  - Predictable ventilation
- **Disadvantages**:
  - Higher energy consumption
  - Less flexible zone control
  - Simultaneous heating/cooling waste

#### Fan Coil Units (FCU)
- **Description**: Individual units in each zone with dedicated outside air system (DOAS)
- **Capacity**: 200-2000 CFM per unit
- **Applications**: Hotels, condos, perimeter zones, retrofit projects
- **Cost**: $1,500-$4,000 per unit
- **Configurations**:
  - 2-pipe: Heating OR cooling (seasonal changeover)
  - 4-pipe: Simultaneous heating and cooling capability
- **Control**: Local thermostat, 3-speed fan or ECM variable speed
- **Maintenance**: Quarterly filter changes, annual coil cleaning

### Packaged Systems

#### RTU (Rooftop Unit)
- **Description**: Packaged DX cooling with gas heat or heat pump
- **Capacity**: 3-150 tons (1 ton = 12,000 BTU/hr)
- **Applications**: Retail, warehouses, small office buildings
- **Energy Efficiency**:
  - Standard: EER 9-11, SEER 13-16
  - High efficiency: EER 12-14, SEER 16-20
- **Cost**: $400-$800 per ton installed
- **Lifespan**: 15-20 years with proper maintenance
- **Advantages**:
  - Factory-assembled, tested
  - Quick installation
  - Roof installation saves floor space
  - Easy replacement
- **Disadvantages**:
  - Exposed to weather (shorter lifespan)
  - Rooftop access required for maintenance
  - Duct losses in unconditioned spaces

**RTU Control Options:**
- Basic: Single-stage, thermostat control
- Economizer: Free cooling with outside air
- Variable capacity: 2-stage or modulating compressors
- Demand control ventilation: CO2-based
- Smart controls: Remote monitoring, fault detection

#### Split Systems
- **Description**: Outdoor condensing unit, indoor evaporator/air handler
- **Capacity**: 1.5-5 tons typical residential, up to 20 tons commercial
- **Applications**: Residential, small retail, tenant spaces
- **Efficiency**: SEER 14-25+, HSPF 8-13 (heat pumps)
- **Cost**: $3,000-$8,000 per ton installed
- **Refrigerant**: R-410A (current), R-32 or R-454B (future)
- **Installation**: Requires refrigerant line set (up to 150 ft)

#### VRF (Variable Refrigerant Flow)
- **Description**: Multi-zone system with one outdoor unit serving multiple indoor units
- **Capacity**: 6-150 tons per system
- **Applications**: Office buildings, hotels, multi-tenant, renovations
- **Technology**: Inverter-driven compressor, electronic expansion valves
- **Efficiency**: SEER 15-20+, EER 11-16, IEER 17-25
- **Cost**: $15-25 per sq ft installed
- **Advantages**:
  - Simultaneous heating and cooling (heat recovery models)
  - 50+ indoor units per outdoor unit
  - Individual zone control
  - No ductwork (or minimal)
  - 30-40% energy savings vs. conventional systems
  - Compact, no mechanical rooms
- **Disadvantages**:
  - High initial cost
  - Specialized installation and service
  - Refrigerant leak detection required
  - Backup heating may be needed in cold climates

**VRF System Types:**
- **2-pipe heat pump**: Cooling OR heating mode for all zones
- **3-pipe heat recovery**: Simultaneous heating and cooling, heat transfer between zones

## Control Strategies

### Temperature Control

#### Setpoint Control
- **Definition**: Target temperature maintained by HVAC system
- **Typical Setpoints**:
  - Office (occupied): 72-74°F cooling, 68-70°F heating
  - Office (unoccupied): 78-85°F cooling, 60-65°F heating
  - Retail: 70-72°F year-round
  - Data centers: 65-75°F (ASHRAE recommended)
- **Adjustability**: ±2-4°F user adjustment range to prevent energy waste

#### Deadband
- **Purpose**: Temperature range with no heating or cooling to save energy
- **Width**: 3-5°F typical (e.g., heat below 68°F, cool above 72°F)
- **Savings**: 5-10% energy per degree of deadband
- **Occupant Comfort**: May require education to prevent complaints
- **ASHRAE 55**: Recommends 73-79°F in summer, 68-74°F in winter (PMV model)

#### PID Control
- **Algorithm**: Proportional-Integral-Derivative control for smooth, accurate response
- **Proportional (P)**: Response proportional to error magnitude
- **Integral (I)**: Eliminates steady-state error over time
- **Derivative (D)**: Anticipates future error based on rate of change
- **Tuning**: Critical for comfort and efficiency
  - Aggressive: Fast response, potential overshoot
  - Conservative: Slower, smoother, better for most applications
- **Applications**: VAV damper control, valve positioning, temperature loops

### Scheduling

#### Occupancy-Based Scheduling
- **Occupied Hours**: HVAC at comfort setpoints
  - Office: 6 AM - 7 PM weekdays
  - Retail: 8 AM - 10 PM daily
  - School: 6 AM - 5 PM weekdays during school year
- **Unoccupied Hours**: Setback/setup to save energy
- **Override**: Temporary occupied mode (1-2 hours) via button or BMS

#### Optimal Start/Stop
- **Optimal Start**: Pre-heat or pre-cool building to reach comfort at occupancy time
- **Learning Algorithm**: Adjusts start time based on outdoor temperature and building thermal mass
- **Savings**: Reduces runtime by 20-40% vs. fixed start time
- **Optimal Stop**: Coasts through end of occupancy using thermal mass
- **Configuration**: Requires accurate occupancy schedule and outdoor temp sensor

#### Holiday/Exception Schedules
- **Purpose**: Override normal schedule for holidays, special events
- **Examples**: Thanksgiving, Christmas, building events
- **Programming**: Annual calendar or date-specific exceptions

### Economizer Operation

#### Air-Side Economizer
- **Principle**: Use cool outdoor air instead of mechanical cooling
- **Types**:
  - **Differential**: Compare outdoor vs. return air enthalpy or temperature
  - **Temperature-based**: Use outdoor air when <65-70°F
  - **Enthalpy-based**: Accounts for humidity (more accurate)
- **Dampers**: Outdoor air (OA), return air (RA), exhaust air (EA)
- **Control Sequence**:
  1. 100% OA when outdoor conditions favorable and cooling needed
  2. Modulate to minimum OA when not economizing
  3. Mechanical cooling as needed
- **Savings**: 20-40% annual cooling energy in most climates
- **Maintenance**: Quarterly damper actuator checks, linkage inspection

#### Water-Side Economizer (Free Cooling)
- **Principle**: Use cooling tower water for cooling when outdoor wet-bulb is low
- **Types**:
  - Integrated: Cooling tower water through plate-and-frame heat exchanger
  - Non-integrated: Bypass chiller completely
- **Applications**: Data centers, process cooling, 24/7 facilities
- **Climate**: Most effective in cool, dry climates
- **Savings**: Up to 75% chiller energy during favorable conditions

## Energy Optimization

### Setback/Setup Strategies

#### Temperature Setback
- **Occupied**: 72°F cooling, 68°F heating
- **Unoccupied**: 78-85°F cooling, 60-65°F heating
- **Savings**: 1-3% per degree F of setback per 8 hours
- **Thermal Mass Consideration**: Heavy buildings can tolerate wider setback
- **Recovery Time**: Allow sufficient optimal start time (30 min - 2 hours)

#### Night Purge/Pre-Cooling
- **Strategy**: Cool building mass at night using outdoor air
- **Climate**: Hot days with cool nights (>15°F diurnal swing)
- **Savings**: 10-30% cooling energy
- **Control**: Exhaust fans + outdoor air dampers when outdoor <65°F and indoor >72°F

### Demand Control Ventilation (DCV)

#### CO2-Based DCV
- **Principle**: Modulate outdoor air based on occupancy (measured by CO2)
- **Setpoint**: Maintain <1000 ppm (ASHRAE 62.1)
- **Control**: Reduce OA to minimum when CO2 <800 ppm
- **Savings**: 20-30% on ventilation fan energy and heating/cooling load
- **Applications**: Variable occupancy spaces (auditoriums, gyms, conference rooms)
- **Sensors**: NDIR CO2 sensor, locate in return air stream or representative zone

#### Outdoor Air Reset
- **Strategy**: Reduce outdoor air during warm-up/cool-down, maximize during occupied
- **Compliance**: Must meet ASHRAE 62.1 minimum ventilation rates
- **Energy Impact**: Reduces heating/cooling of outdoor air by 10-20%

### Supply Air Temperature (SAT) Reset

#### Strategies
- **Outdoor Air Reset**: Increase SAT as outdoor temp decreases
  - Example: 55°F SAT when outdoor >80°F, 65°F SAT when outdoor <50°F
- **Demand-Based Reset**: Increase SAT until one zone calls for full cooling
- **Time of Day**: Higher SAT during mild conditions
- **Savings**: 5-15% cooling energy, reduced reheat energy

#### Considerations
- Minimum SAT for dehumidification (typically 54-58°F)
- VAV box minimum airflow requirements
- Zone reheat energy trade-off

### Chilled Water Reset
- **Strategy**: Raise chilled water temperature as load decreases
- **Typical**: 44°F design, reset to 54-58°F at low loads
- **Savings**: 1.5-2% chiller efficiency per degree
- **Control**: Monitor valve positions, raise temp until one valve is 100% open
- **Limit**: Maintain minimum ΔT (typically 10-14°F) for proper chiller operation

## Common Issues and Solutions

### Comfort Issues

| Symptom | Likely Cause | Diagnostic Steps | Solution |
|---------|--------------|------------------|----------|
| Room too cold | Thermostat out of calibration | Verify actual temp with calibrated thermometer | Recalibrate or replace thermostat |
| Room too hot | Insufficient airflow | Measure airflow at diffuser, check VAV box position | Balance system, repair damper actuator |
| Temperature swings | Aggressive PID tuning | Monitor temp over time, check cycling | Retune PID parameters |
| Humidity too high | Insufficient dehumidification | Measure RH, check SAT and airflow | Lower SAT, increase airflow, add dehumidification |
| Drafts | Excessive air velocity | Measure air speed (target <50 FPM) | Adjust diffusers, reduce airflow |

### Energy Waste Issues

| Symptom | Likely Cause | Impact | Solution |
|---------|--------------|--------|----------|
| High energy bills | System running during unoccupied hours | 20-40% waste | Fix schedules, enable setback |
| Simultaneous heating/cooling | Zone temperature conflicts | 10-30% waste | Fix zone grouping, dual duct conversion |
| Outdoor air damper stuck open | Failed actuator or linkage | 15-25% waste | Repair/replace damper actuator |
| No economizer operation | Disabled or broken sensors | 15-30% lost savings | Enable economizer, calibrate sensors |
| Short cycling | Oversized equipment or controls | 10-20% waste | Adjust staging, add delays |

### Equipment Failures

| Issue | Root Cause | Prevention | Corrective Action |
|-------|------------|------------|-------------------|
| Compressor failure | Lack of maintenance, refrigerant issues | Quarterly inspections, annual maintenance | Replace compressor, check refrigerant circuit |
| Fan motor burnout | Bearing failure, overload | Lubrication, current monitoring | Replace motor, check drive belts/sheaves |
| Coil freeze-up | Low airflow, control failure | Monthly filter changes, flow monitoring | Thaw coil, repair root cause |
| Control system failure | Power surge, age, moisture | Surge protection, environmental controls | Replace controller, backup programs |
| Refrigerant leak | Vibration, corrosion | Annual leak detection | Find and repair leak, recharge system |

## Preventive Maintenance Schedule

### Monthly
- Change/clean filters
- Inspect belts for wear and tension
- Check refrigerant pressures (if accessible)
- Review energy consumption trends
- Test alarms and safeties

### Quarterly
- Lubricate motors and bearings
- Inspect damper operation and linkages
- Calibrate sensors (spot check)
- Clean condenser and evaporator coils (if needed)
- Check economizer operation

### Annual (Spring)
- Complete refrigeration system check (pressures, superheat, subcooling)
- Clean coils thoroughly
- Check/tighten electrical connections
- Calibrate all sensors and controls
- Test safety controls
- Measure and document system performance

### Annual (Fall)
- Inspect heat exchangers (if gas heat)
- Test combustion safety (CO, gas pressure)
- Check condensate drains
- Inspect insulation
- Review and update control schedules

## Energy Benchmarking

### Typical Energy Consumption
- **Office Building**: 10-25 kWh/sq ft/year HVAC
- **Retail**: 15-30 kWh/sq ft/year HVAC
- **High Performance Office**: <8 kWh/sq ft/year HVAC
- **ASHRAE 90.1 Baseline**: Reference for code compliance

### Performance Metrics
- **EUI (Energy Use Intensity)**: kBTU/sq ft/year or kWh/sq ft/year
- **Cooling Efficiency**: kW/ton (target: <0.8 kW/ton for chiller plant)
- **HVAC Percentage**: 40-60% of total building energy in commercial buildings
