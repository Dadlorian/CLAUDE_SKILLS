# Occupancy-Based Control Guide

## Sensor Placement
- Conference rooms: Ceiling-mounted PIR
- Open offices: Wall or ceiling, 500-1000 sqft coverage
- Restrooms: Ultrasonic (detects fine movement)
- Perimeter: Dual-technology

## Control Logic

### HVAC Control
```javascript
async function controlZone(zoneId, occupancy) {
  const zone = await getZone(zoneId);
  
  if (occupancy.occupied) {
    // Occupied mode
    await setTemperature(zoneId, zone.occupied_setpoint);
    await setVentilation(zoneId, 'normal');
  } else {
    // Grace period before setback
    const minutesVacant = (Date.now() - occupancy.last_occupied) / 60000;
    
    if (minutesVacant > 30) {
      await setTemperature(zoneId, zone.unoccupied_setpoint);
      await setVentilation(zoneId, 'minimum');
    }
  }
}
```

### Lighting Control
```javascript
function controlLighting(occupancy, lightLevel) {
  if (occupancy.occupied) {
    // Daylight harvesting
    if (lightLevel < 300) {  // lux
      return 100;  // Full brightness
    } else if (lightLevel < 500) {
      return 50;   // Dimmed
    } else {
      return 0;    // Lights off (sufficient daylight)
    }
  } else {
    return 0;  // Unoccupied, lights off
  }
}
```

## Advanced Strategies

### Predictive Occupancy
```python
# Learn patterns and pre-condition
from sklearn.ensemble import RandomForestClassifier

# Train on historical data
model.fit(X_train, y_train)  # Features: time, day, historical patterns

# Predict future occupancy
predicted_occupancy = model.predict(future_time)

# Pre-cool/heat if occupancy expected
if predicted_occupancy > 0.5:
    start_hvac(30_minutes_before)
```

### Meeting Room Booking Integration
```javascript
// Sync with calendar system
const bookings = await getCalendarBookings(roomId, today);

bookings.forEach(booking => {
  // Pre-condition 15 min before meeting
  scheduleHVAC(booking.start_time - 15*60*1000, 'occupied');
  scheduleHVAC(booking.end_time, 'unoccupied');
});
```

## Energy Savings
- HVAC: 20-30% reduction
- Lighting: 30-50% reduction
- Total: 25-40% building energy

## See Also
- sensor_deployment_guide.md
- energy_optimization_guide.md
