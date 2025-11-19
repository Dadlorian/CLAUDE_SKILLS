# Energy Optimization Guide

## Baseline Analysis
1. Collect 12 months of utility bills
2. Calculate EUI (kBtu/sqft/year)
3. Compare to benchmarks
4. Identify opportunities

## Optimization Strategies

### 1. Scheduling
```javascript
const schedules = {
  weekday: {
    occupied: { start: '07:00', end: '18:00', temp: 72 },
    unoccupied: { temp: 78 }
  },
  weekend: {
    unoccupied: { temp: 80 }
  }
};
```

### 2. Setpoint Optimization
- Cooling: Increase 1°F = 3% savings
- Heating: Decrease 1°F = 3% savings
- Deadband: 70-74°F (no simultaneous heating/cooling)

### 3. Demand Control Ventilation
```python
def calculate_fresh_air(co2_level):
    # ASHRAE 62.1 requirement
    min_cfm = occupants * 5  # 5 CFM per person
    
    if co2_level > 1000:  # ppm
        return min_cfm * 1.5
    elif co2_level > 800:
        return min_cfm * 1.2
    else:
        return min_cfm
```

### 4. Economizer Control
```python
if outdoor_temp < indoor_temp and outdoor_temp > 55:
    # Free cooling
    damper_position = 100  # % open
else:
    damper_position = minimum_outdoor_air
```

### 5. Load Shifting
- Pre-cool before peak hours
- Delay non-critical loads
- Participate in demand response

## Monitoring & Verification
- Track monthly energy use
- Compare to baseline
- Calculate savings
- Adjust strategies

## Expected Savings
- Scheduling: 10-20%
- Setpoint optimization: 5-15%
- DCV: 20-30% on ventilation
- Economizer: 20-40% on cooling
- **Total potential: 30-50%**

## See Also
- energy_metrics.md
- hvac_basics.md
