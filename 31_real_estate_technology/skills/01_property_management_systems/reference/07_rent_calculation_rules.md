# Rent Calculation Rules Reference

## Pro-Rated Rent Calculations

### Daily Pro-Ration Method (Most Common)
```
Pro-rated Rent = (Monthly Rent / Days in Month) × Days Occupied
```

**Example 1**: Move-in on January 15th
```
Monthly Rent: $2,000
Days in January: 31
Days Occupied: 17 (Jan 15-31)

Pro-rated Rent = ($2,000 / 31) × 17 = $1,096.77
```

**Example 2**: Move-out on March 22nd
```
Monthly Rent: $2,000
Days in March: 31
Days Occupied: 22 (Mar 1-22)

Pro-rated Rent = ($2,000 / 31) × 22 = $1,419.35
```

### 30-Day Month Method (Alternative)
```
Pro-rated Rent = (Monthly Rent / 30) × Days Occupied
```

**Pros**: Consistent across all months
**Cons**: Less accurate for actual month lengths

### Banker's Method (365/12)
```
Daily Rate = (Monthly Rent × 12) / 365
Pro-rated Rent = Daily Rate × Days Occupied
```

**Example**:
```
Monthly Rent: $2,000
Daily Rate = ($2,000 × 12) / 365 = $65.75
Days Occupied: 17

Pro-rated Rent = $65.75 × 17 = $1,117.75
```

## Rent Components

### Base Rent
Primary rental amount for unit occupancy

### Additional Monthly Charges

#### Pet Rent
- **Typical Range**: $25-$75 per pet per month
- **Calculation**: Fixed amount added to monthly rent
- **Non-refundable**: Unlike pet deposit

```
Total Rent = Base Rent + (Pet Rent × Number of Pets)
Example: $2,000 + ($50 × 2) = $2,100/month
```

#### Parking Fees
- **Covered Parking**: $50-$150/month
- **Uncovered Parking**: $25-$75/month
- **Reserved Parking**: $75-$200/month
- **Garage Parking**: $150-$400/month (urban)

#### Storage Fees
- **Climate-Controlled**: $50-$150/month
- **Standard Storage Unit**: $25-$75/month

#### Amenity Fees
- **Gym Access**: Often included, sometimes $25-$50/month
- **Pool Maintenance**: Usually included
- **Package Locker**: $5-$15/month
- **Trash Valet**: $10-$30/month

### Utility Charges

#### RUBS (Ratio Utility Billing System)
Allocate common utilities proportionally among tenants

**Common Allocation Methods**:

**By Unit**:
```
Tenant Share = Total Bill / Number of Units
```

**By Square Footage**:
```
Tenant Share = (Unit SF / Total SF) × Total Bill
```

**By Occupancy**:
```
Tenant Share = (# of Occupants / Total Occupants) × Total Bill
```

**Combined Formula** (weighted):
```
Tenant Share = Total Bill × [
  (Unit SF / Total SF) × 50% +
  (# Occupants / Total Occupants) × 50%
]
```

**Example**:
```
Water Bill: $1,500
Total Units: 50
Per Unit: $1,500 / 50 = $30/unit
```

#### Submetering
Direct billing based on individual meters
- Water: Per gallon or unit
- Electric: Per kWh
- Gas: Per therm

## Late Fees

### Fixed Amount
```
Late Fee = Fixed Dollar Amount
Example: $75 flat fee
```

### Percentage-Based
```
Late Fee = Monthly Rent × Percentage
Example: $2,000 × 5% = $100
```

### Daily Late Fee
```
Daily Late Fee = Daily Rate × Days Late
Example: $25/day after grace period
```

### Grace Period
- **Typical**: 3-5 days
- **Legal Requirement**: Varies by state
- **Example**: Rent due 1st, late fee applies on 6th

**Complete Example**:
```
Rent Due: December 1st
Grace Period: 5 days (through Dec 5th)
Payment Made: December 8th
Days Late: 3 days (Dec 6, 7, 8)
Late Fee: $75 flat or $25/day = $75
```

### State-Specific Limits
- **California**: Reasonable amount (courts often cap at 6-10%)
- **New York**: No statutory limit, must be reasonable
- **Texas**: No specific limit
- **Oregon**: 5% after 4-day grace period (flat or 5% of monthly)

## NSF (Non-Sufficient Funds) Fees

### Bank Fee Pass-Through
```
NSF Fee = Bank's NSF Charge ($25-$35 typical)
```

### Administrative Fee
```
NSF Fee = Bank Fee + Administrative Charge
Example: $30 (bank) + $25 (admin) = $55
```

### State Limits
- Check state laws for maximum NSF fees
- Some states limit to actual bank charges
- Must be disclosed in lease

## Security Deposit Calculations

### Standard Calculation
```
Security Deposit = 1× to 2× Monthly Rent
```

**State Limits**:
- **California**: 2× (unfurnished), 3× (furnished)
- **New York**: 1× monthly rent
- **Illinois**: No statutory limit
- **Washington**: No limit, but must be reasonable

### Pet Deposit (One-Time)
```
Pet Deposit = $200-$500 per pet (refundable)
Non-Refundable Pet Fee = $100-$300 (one-time)
```

### Additional Deposits
- **Key Deposit**: $25-$100 (refundable)
- **Cleaning Deposit**: $100-$300 (sometimes separate)
- **Parking Deposit**: $50-$150 (if separate from security)

## Concessions and Specials

### Free Rent Calculation
**1 Month Free on 12-Month Lease**:
```
Effective Rent = (Monthly Rent × 11) / 12
Example: ($2,000 × 11) / 12 = $1,833.33/month effective
```

**Amortized Over Lease**:
```
Year 1: $1,833.33/month
Year 2 (renewal): $2,000/month
```

**First Month Free**:
```
Month 1: $0
Months 2-12: $2,000
Total Year 1: $22,000
Effective: $1,833.33/month
```

### Reduced Rent Specials
**$200 Off for 3 Months**:
```
Months 1-3: $1,800
Months 4-12: $2,000
Total Year 1: $23,400
Effective: $1,950/month
```

### Move-In Special Calculations
**$500 Off Move-In Costs**:
```
Standard Move-In: $4,000 (1st month + deposit)
With Special: $3,500
```

## Lease Renewal Rent Calculations

### Market-Based Increase
```
New Rent = Current Rent × (1 + Market Increase %)
Example: $2,000 × 1.05 = $2,100 (5% increase)
```

### Loss-to-Lease Analysis
```
Market Rent: $2,200
Current Rent: $2,000
Loss-to-Lease: $200/month or 9.1%

Renewal Options:
- Bring to market: $2,200 (9.1% increase)
- Split difference: $2,100 (4.8% increase)
- Modest increase: $2,050 (2.4% increase)
```

### Renewal Incentive Calculation
```
Turnover Cost: $2,500
Vacancy Period: 30 days × $73.33/day = $2,200
Total Turnover Cost: $4,700

Value of Renewal:
- Save turnover: $2,500
- Save vacancy: $2,200
- Can afford concession: Up to $4,700 value
```

## Commercial Rent Calculations

### Base Rent (Per Square Foot)
```
Annual Rent = Square Feet × Rate per SF
Monthly Rent = Annual Rent / 12

Example:
5,000 SF × $25/SF/year = $125,000/year
Monthly: $125,000 / 12 = $10,416.67
```

### Triple Net (NNN) Lease
```
Total Rent = Base Rent + Property Taxes + Insurance + CAM

Example:
Base Rent: $20/SF/year
Property Tax: $3/SF/year
Insurance: $1/SF/year
CAM: $4/SF/year
Total: $28/SF/year (NNN)

For 5,000 SF:
Monthly Total = (5,000 × $28) / 12 = $11,666.67
```

### CAM Reconciliation
**Budgeted vs. Actual**:
```
Estimated CAM (charged monthly): $4/SF
Actual CAM (year-end): $4.50/SF
True-Up: $0.50/SF owed by tenant

For 5,000 SF tenant:
Annual Reconciliation = 5,000 × $0.50 = $2,500 due
```

### Percentage Rent (Retail)
```
Percentage Rent = (Gross Sales - Breakpoint) × Percentage

Example:
Breakpoint: $1,000,000/year
Percentage: 6% of sales over breakpoint
Actual Sales: $1,200,000

Percentage Rent = ($1,200,000 - $1,000,000) × 6%
                = $12,000/year
Monthly: $1,000
Total Rent = Base Rent + Percentage Rent
```

### Rent Escalations
**Fixed Annual Increase**:
```
Year 1: $25/SF
Year 2: $26/SF (+4%)
Year 3: $27/SF (+3.8%)
```

**CPI-Based**:
```
New Rent = Current Rent × (1 + CPI Increase)
Example: $25/SF × (1 + 0.03) = $25.75/SF
```

**Capped CPI**:
```
Increase = MIN(CPI, Cap)
Example: CPI = 5%, Cap = 3%
Increase = 3%
```

## Special Situations

### Lease Break Fee
```
Early Termination Fee = 2-3 months' rent
OR
Remaining Rent = Months Remaining × Monthly Rent
Fee = 50-60% of Remaining Rent
```

**Example**:
```
Monthly Rent: $2,000
Lease Ends: December 31, 2025
Break Date: June 30, 2025
Remaining: 6 months
Fee = 2 months' rent = $4,000
OR
Fee = 60% × (6 × $2,000) = $7,200
```

### Sublease Rent
```
Sublease Rent = Original Rent × (100% - 110%)
Often at or above original to cover admin
```

### Holdover Rent
```
Holdover Rent = Monthly Rent × 1.5 to 2×
Example: $2,000 × 1.5 = $3,000/month
Pro-rated daily: $100/day
```

### Section 8/Housing Voucher
```
Total Rent: $1,500
Tenant Income: $1,200/month (30% = $360)
Housing Authority Pays: $1,140
Tenant Pays: $360
```

## Rent Adjustment Formulas

### Affordable Housing (LIHTC)
```
Maximum Rent = (Area Median Income × Income Limit %) / 12
Then: Maximum Rent × 30% = Max Tenant Rent

Example:
AMI: $80,000
Limit: 60% AMI
Income Limit = $48,000
Monthly Income: $4,000
Maximum Rent = $4,000 × 30% = $1,200
```

### Rent-to-Income Ratio
```
Qualifying Income = Rent × Multiplier (2.5× to 3×)

Example:
Rent: $2,000
Minimum Income: $2,000 × 3 = $6,000/month ($72,000/year)
```

## Tax and Fee Calculations

### Sales Tax on Rent (If Applicable)
Some states/cities tax rental income:
```
Total Due = Base Rent + (Base Rent × Tax Rate)
Example: $2,000 + ($2,000 × 6%) = $2,120
```

### Occupancy Tax (Tourist Rentals)
```
Total Due = Rent + (Rent × Occupancy Tax Rate)
Example: $3,000 + ($3,000 × 12%) = $3,360
```

These calculation rules ensure accurate billing and compliance with lease terms and regulations.
