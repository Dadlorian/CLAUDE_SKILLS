# Rent Calculations Reference

## Base Rent
```
Monthly Rent = Annual Rent / 12
Daily Rent = Monthly Rent / Days in Month
```

## Prorated Rent
```
Prorated = (Daily Rent × Days Occupied) or
Prorated = (Monthly Rent / Days in Month) × Days Occupied
```

## Rent Escalations
```
Year 2 Rent = Year 1 Rent × (1 + Escalation %)
CPI Adjustment = Base Rent × (CPI Current / CPI Base)
```

## CAM Charges (Commercial)
```
CAM = (Tenant Sqft / Total Sqft) × Total CAM Expenses
```

## Late Fees
```
Late Fee = Greater of ($50 or 5% of Monthly Rent)
```

## Example
```python
def calculate_rent(base_rent, days_occupied, days_in_month, late=False):
    daily_rent = base_rent / days_in_month
    rent = daily_rent * days_occupied
    
    if late:
        late_fee = max(50, rent * 0.05)
        rent += late_fee
        
    return round(rent, 2)
```

## See Also
- lease_types_reference.md
