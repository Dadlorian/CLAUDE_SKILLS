# Telematics API Quick Reference

## Geotab SDK

### Authentication
```python
from mygeotab import API

api = API(username='user@company.com', password='password', database='database_name')
api.authenticate()
```

### Get Vehicle Locations
```python
# Get current location of all vehicles
devices = api.get('Device')
device_status = api.get('DeviceStatusInfo', search={'deviceSearch': {'id': device['id']}})

for status in device_status:
    print(f"Vehicle: {status['device']['name']}")
    print(f"Lat/Lon: {status['latitude']}, {status['longitude']}")
    print(f"Speed: {status['speed']} km/h")
```

### Get Fault Codes (DTCs)
```python
faults = api.get('FaultData', search={
    'deviceSearch': {'id': device_id},
    'fromDate': '2025-01-01T00:00:00.000Z'
})

for fault in faults:
    print(f"Code: {fault['diagnostic']['code']}")
    print(f"Description: {fault['diagnostic']['name']}")
    print(f"Timestamp: {fault['dateTime']}")
```

---

## Samsara API

### Authentication
```bash
curl -X GET "https://api.samsara.com/fleet/vehicles" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Get Vehicle Stats
```python
import requests

headers = {'Authorization': 'Bearer YOUR_API_TOKEN'}
response = requests.get('https://api.samsara.com/fleet/vehicles/stats', headers=headers)

for vehicle in response.json()['data']:
    print(f"Vehicle: {vehicle['name']}")
    print(f"Odometer: {vehicle['odometerMeters']} meters")
    print(f"Fuel: {vehicle['fuelPercent']}%")
```

### Get Driver Safety Events
```python
params = {
    'startTime': '2025-01-01T00:00:00Z',
    'endTime': '2025-01-31T23:59:59Z'
}
response = requests.get(
    'https://api.samsara.com/fleet/drivers/safetyEvents',
    headers=headers,
    params=params
)

for event in response.json()['data']:
    print(f"Event: {event['eventType']}")  # harsh_braking, speeding, etc.
    print(f"Driver: {event['driverName']}")
    print(f"Severity: {event['severity']}")
```

---

## CAN Bus Data (SAE J1939)

### Common PIDs (Parameter IDs)

| PID | Name | Units | Range |
|-----|------|-------|-------|
| 0x00 | Engine Speed | RPM | 0-8000 |
| 0x05 | Coolant Temperature | °C | -40 to 210 |
| 0x0C | Engine Oil Pressure | kPa | 0-1000 |
| 0x0D | Vehicle Speed | km/h | 0-250 |
| 0x11 | Throttle Position | % | 0-100 |
| 0x2F | Fuel Level | % | 0-100 |

### Parse CAN Data (Python)
```python
import can

bus = can.interface.Bus(channel='can0', bustype='socketcan')

for message in bus:
    if message.arbitration_id == 0x0CF00400:  # Engine Speed PID
        rpm = int.from_bytes(message.data[3:5], byteorder='big') * 0.125
        print(f"Engine RPM: {rpm}")

    elif message.arbitration_id == 0x18FEF100:  # Fuel Level
        fuel_percent = message.data[1] * 0.4
        print(f"Fuel Level: {fuel_percent}%")
```

---

## GPS Data Formats

### NMEA 0183 (Standard GPS Protocol)

**GPRMC Sentence (Recommended Minimum)**:
```
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
```

Fields:
- 123519: Time (12:35:19 UTC)
- A: Status (A=active, V=void)
- 4807.038,N: Latitude (48°07.038' N)
- 01131.000,E: Longitude (11°31.000' E)
- 022.4: Speed (22.4 knots)
- 084.4: Heading (84.4°)
- 230394: Date (23 Mar 1994)

**Parse NMEA in Python**:
```python
import pynmea2

nmea_sentence = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
msg = pynmea2.parse(nmea_sentence)

print(f"Latitude: {msg.latitude}")
print(f"Longitude: {msg.longitude}")
print(f"Speed: {msg.spd_over_grnd} knots")
print(f"Heading: {msg.true_course}°")
```

---

## ELD Data Export Format

### FMCSA-Required Fields

```json
{
  "driver": {
    "first_name": "John",
    "last_name": "Doe",
    "license_number": "D1234567",
    "license_state": "CA"
  },
  "duty_status_logs": [
    {
      "status": "driving",
      "start_time": "2025-01-15T08:00:00Z",
      "end_time": "2025-01-15T11:30:00Z",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "description": "San Francisco, CA"
      },
      "odometer_miles": 12543.2,
      "engine_hours": 8453.5
    },
    {
      "status": "on_duty_not_driving",
      "start_time": "2025-01-15T11:30:00Z",
      "end_time": "2025-01-15T12:00:00Z",
      "location": {...}
    }
  ],
  "certifications": [
    {
      "date": "2025-01-15",
      "signature": "base64_encoded_signature"
    }
  ]
}
```

---

## Fuel Card APIs

### WEX Fuel Card API

```python
import requests

headers = {'Authorization': 'Bearer YOUR_API_KEY'}

# Get fuel transactions
params = {
    'from_date': '2025-01-01',
    'to_date': '2025-01-31',
    'card_number': '1234567890'
}

response = requests.get(
    'https://api.wexinc.com/v1/transactions',
    headers=headers,
    params=params
)

for transaction in response.json()['transactions']:
    print(f"Date: {transaction['date']}")
    print(f"Gallons: {transaction['quantity']}")
    print(f"Price: ${transaction['amount']}")
    print(f"Location: {transaction['merchant_name']}")
```

---

## Common Calculations

### Fuel Efficiency (MPG)
```python
def calculate_mpg(miles_driven: float, gallons_consumed: float) -> float:
    return miles_driven / gallons_consumed

# Example
mpg = calculate_mpg(miles_driven=450, gallons_consumed=30)
# Output: 15.0 MPG
```

### Idle Time Percentage
```python
def calculate_idle_percentage(idle_minutes: int, total_minutes: int) -> float:
    return (idle_minutes / total_minutes) * 100

# Example
idle_pct = calculate_idle_percentage(idle_minutes=120, total_minutes=600)
# Output: 20.0% idle time
```

### Cost Per Mile
```python
def calculate_cost_per_mile(total_costs: float, miles_driven: float) -> float:
    """
    Total costs include: fuel, maintenance, insurance, depreciation, driver wages
    """
    return total_costs / miles_driven

# Example
cpm = calculate_cost_per_mile(total_costs=15000, miles_driven=10000)
# Output: $1.50 per mile
```

---

## Error Codes & Troubleshooting

### Common OBD-II/CAN Bus Errors

| Code | Description | Action |
|------|-------------|--------|
| P0128 | Coolant thermostat malfunction | Check coolant level, thermostat |
| P0300 | Random cylinder misfire | Inspect spark plugs, fuel injectors |
| P0420 | Catalyst system efficiency below threshold | Check catalytic converter, O2 sensors |
| P0715 | Input/Turbine speed sensor malfunction | Check transmission sensor |

### Telematics Device Not Reporting

**Checklist**:
1. Check power connection (12V supply)
2. Verify cellular signal (check SIM card, antenna)
3. Confirm GPS antenna connection
4. Check device LED status codes
5. Verify account/subscription is active
6. Check firewall rules (if using private APN)

---

**Version**: 1.0
**Platform Coverage**: Geotab, Samsara, Verizon Connect, Generic OBD-II
**Last Updated**: 2025-01-19
