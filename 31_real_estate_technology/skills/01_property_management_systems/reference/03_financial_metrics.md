# Property Management Financial Metrics Reference

## Overview
Key financial metrics and calculations used in property management for performance analysis, investment evaluation, and operational decision-making.

## Income Metrics

### Gross Potential Rent (GPR)
**Definition**: Total rental income if all units were occupied at market rent.

**Formula**:
```
GPR = Σ(Market Rent per Unit × Number of Units)
```

**Example**:
```
50 units @ $2,000/month = $100,000/month
Annual GPR = $1,200,000
```

**Use Case**: Baseline for calculating vacancy loss and economic occupancy

---

### Gross Scheduled Rent (GSR)
**Definition**: Total rent based on actual lease agreements (in-place rent).

**Formula**:
```
GSR = Σ(Actual Lease Rent per Unit)
```

**Example**:
```
50 units with actual rents totaling $95,000/month
Annual GSR = $1,140,000
```

**Difference from GPR**: Loss-to-Lease = $60,000/year

---

### Effective Gross Income (EGI)
**Definition**: Actual revenue after accounting for vacancy and other income.

**Formula**:
```
EGI = GSR - Vacancy Loss - Concessions + Other Income
```

**Components**:
- **Vacancy Loss**: Rent lost from unoccupied units
- **Concessions**: Move-in specials, free rent periods
- **Other Income**: Parking, laundry, pet fees, amenity fees, late fees

**Example**:
```
GSR:              $1,140,000
Vacancy Loss:      ($57,000)    5% vacancy
Concessions:       ($11,400)    1% for move-in specials
Other Income:       $85,000     Parking, pets, fees
---------------------------------
EGI:              $1,156,600
```

---

### Net Operating Income (NOI)
**Definition**: Income after operating expenses, before debt service and capital expenses.

**Formula**:
```
NOI = EGI - Operating Expenses
```

**Operating Expenses Include**:
- Property management fees
- Maintenance and repairs
- Utilities
- Property taxes
- Insurance
- Marketing and leasing costs
- Administrative expenses

**Operating Expenses Exclude**:
- Mortgage payments
- Capital improvements
- Depreciation
- Owner's income taxes

**Example**:
```
EGI:                      $1,156,600
Operating Expenses:        ($462,640)   40% of EGI
-----------------------------------------
NOI:                        $693,960
```

---

### Cash Flow Before Taxes (CFBT)
**Definition**: Cash available after debt service, before income taxes.

**Formula**:
```
CFBT = NOI - Debt Service
```

**Example**:
```
NOI:                    $693,960
Annual Debt Service:   ($480,000)   $40,000/month
------------------------------------
CFBT:                   $213,960
```

---

## Profitability Ratios

### Cap Rate (Capitalization Rate)
**Definition**: Rate of return based on NOI and property value.

**Formula**:
```
Cap Rate = NOI / Property Value
```

**Example**:
```
NOI: $693,960
Property Value: $10,500,000
Cap Rate = 6.61%
```

**Interpretation**:
- Higher cap rate = Higher risk, higher return
- Lower cap rate = Lower risk, lower return
- Market cap rates vary by: location, property type, market conditions

**Typical Ranges**:
- Class A Multifamily (major metros): 4-5%
- Class B Multifamily (secondary markets): 5-7%
- Class C Multifamily (tertiary markets): 7-10%
- Commercial (varies widely): 5-12%

**Use Cases**:
- Property valuation
- Investment comparison
- Market analysis

---

### Cash-on-Cash Return (CoC)
**Definition**: Annual return on actual cash invested.

**Formula**:
```
CoC Return = CFBT / Total Cash Invested
```

**Example**:
```
CFBT: $213,960
Cash Invested: $2,625,000 (25% down payment)
CoC Return = 8.15%
```

**Interpretation**:
- Measures return on leveraged investment
- Accounts for financing impact
- Target: 8-12% for most investors

---

### Debt Service Coverage Ratio (DSCR)
**Definition**: Ability to cover debt payments with NOI.

**Formula**:
```
DSCR = NOI / Annual Debt Service
```

**Example**:
```
NOI: $693,960
Annual Debt Service: $480,000
DSCR = 1.45x
```

**Lender Requirements**:
- Minimum: 1.20x (NOI 20% higher than debt service)
- Preferred: 1.25x - 1.35x
- Strong: 1.40x+

**Interpretation**:
- DSCR < 1.0: Insufficient income to cover debt (default risk)
- DSCR = 1.0: Breaking even on debt service
- DSCR > 1.25: Comfortable cushion for lenders

---

### Return on Investment (ROI)
**Definition**: Total return including appreciation and cash flow.

**Formula**:
```
ROI = (Current Value - Purchase Price + Total Cash Flow) / Total Investment
```

**Example** (5-year hold):
```
Purchase Price: $10,000,000
Total Cash Invested: $2,625,000
Total Cash Flow (5 years): $1,069,800
Current Value: $12,500,000
Appreciation: $2,500,000

ROI = ($12,500,000 - $10,000,000 + $1,069,800) / $2,625,000
ROI = 135.8% over 5 years
Annualized ROI = 18.7%
```

---

## Efficiency Metrics

### Occupancy Rate
**Definition**: Percentage of units occupied.

**Physical Occupancy**:
```
Physical Occupancy = Occupied Units / Total Units
```

**Economic Occupancy**:
```
Economic Occupancy = Actual Rent Collected / Gross Potential Rent
```

**Example**:
```
Total Units: 50
Occupied Units: 47
Physical Occupancy = 94%

Gross Potential Rent: $100,000/month
Actual Rent Collected: $91,000/month
Economic Occupancy = 91%
```

**Difference**: 3% loss-to-lease (occupied units paying below market)

**Industry Benchmarks**:
- Stabilized property target: 93-96%
- Class A properties: 95-97%
- New construction (lease-up): 85-95% (years 1-2)

---

### Operating Expense Ratio (OER)
**Definition**: Operating expenses as percentage of gross income.

**Formula**:
```
OER = Operating Expenses / EGI
```

**Example**:
```
Operating Expenses: $462,640
EGI: $1,156,600
OER = 40%
```

**Industry Benchmarks**:
- Multifamily: 35-45%
- Commercial Office: 30-40%
- Retail: 25-35%
- Industrial: 20-30%

**Components to Monitor**:
- Property management: 3-6% of EGI
- Maintenance: 8-12% of EGI
- Property taxes: 8-15% of EGI
- Insurance: 2-4% of EGI
- Utilities: 5-10% of EGI

---

### Revenue per Available Room (RevPAR)
**Definition**: Average revenue per unit, accounting for occupancy.

**Formula**:
```
RevPAR = Total Revenue / Total Units
OR
RevPAR = Average Rent × Occupancy Rate
```

**Example**:
```
Total Monthly Revenue: $95,000
Total Units: 50
RevPAR = $1,900/unit

OR

Average Rent: $2,000
Occupancy: 95%
RevPAR = $1,900
```

**Use Case**: Performance comparison across properties with different sizes

---

### Net Operating Income per Unit
**Definition**: NOI divided by total units.

**Formula**:
```
NOI per Unit = Annual NOI / Total Units
```

**Example**:
```
Annual NOI: $693,960
Total Units: 50
NOI per Unit = $13,879/year or $1,157/month
```

**Benchmarking**: Compare similar properties in same market

---

## Lease Metrics

### Average Rent per Square Foot
**Definition**: Revenue normalized by square footage.

**Formula**:
```
Rent per SF = Total Rent / Total Square Feet
```

**Example**:
```
Monthly Rent: $95,000
Total Rentable SF: 47,500
Rent per SF = $2.00/SF/month or $24.00/SF/year
```

**Typical Ranges**:
- Multifamily: $1.50-$3.50/SF/month (varies by market)
- Commercial Office: $20-$60/SF/year
- Retail: $15-$100/SF/year (highly variable)

---

### Lease Renewal Rate
**Definition**: Percentage of expiring leases that renew.

**Formula**:
```
Renewal Rate = Renewed Leases / Expiring Leases
```

**Example**:
```
Expiring Leases (12 months): 35
Renewed Leases: 20
Non-Renewals: 15
Renewal Rate = 57.1%
```

**Industry Benchmarks**:
- Multifamily: 50-60%
- Senior Living: 80-90%
- Commercial (long-term): 60-75%

**Impact on Operations**:
- Higher renewal rate = Lower turnover costs
- Turnover cost per unit: $1,000-$3,000
- Includes: marketing, cleaning, repairs, vacancy loss

---

### Average Lease Term
**Definition**: Average length of lease agreements.

**Formula**:
```
Average Lease Term = Σ(Lease Term in Months) / Total Leases
```

**Example**:
```
20 leases @ 12 months
10 leases @ 6 months
5 leases @ month-to-month
Average = (20×12 + 10×6 + 5×1) / 35 = 8.7 months
```

---

## Collection Metrics

### Collection Rate
**Definition**: Percentage of rent collected vs. charged.

**Formula**:
```
Collection Rate = Rent Collected / Rent Charged
```

**Example**:
```
Rent Charged: $100,000
Rent Collected: $98,500
Collection Rate = 98.5%
```

**Target**: >98% within 5 days of due date

---

### Average Days Delinquent
**Definition**: Average age of outstanding receivables.

**Formula**:
```
Average Days Delinquent = Σ(Balance × Days Outstanding) / Total Outstanding
```

**Example**:
```
Tenant A: $2,000 @ 15 days = 30,000
Tenant B: $1,500 @ 30 days = 45,000
Tenant C: $500 @ 45 days = 22,500
Total Outstanding: $4,000
Average Days = 97,500 / 4,000 = 24.4 days
```

---

### Bad Debt Percentage
**Definition**: Uncollectible rent as percentage of gross rent.

**Formula**:
```
Bad Debt % = Write-offs / Gross Scheduled Rent
```

**Target**: <2% for well-managed properties

---

## Maintenance Metrics

### Maintenance Cost per Unit
**Definition**: Total maintenance expenses per unit.

**Formula**:
```
Maintenance Cost per Unit = Annual Maintenance Expenses / Total Units
```

**Industry Benchmarks**:
- New construction (0-5 years): $300-$500/unit/year
- Mid-age (6-15 years): $500-$800/unit/year
- Older properties (15+ years): $800-$1,500/unit/year

---

### Work Order Response Time
**Definition**: Average time to complete work orders by priority.

**Targets**:
- Emergency: <24 hours
- Urgent: 24-72 hours
- Normal: 5-7 business days
- Preventive: As scheduled

---

### Turnover Cost per Unit
**Definition**: Average cost to make unit rent-ready after move-out.

**Components**:
- Cleaning: $150-$300
- Painting: $300-$600
- Repairs: $200-$800
- Carpet cleaning/replacement: $200-$1,500
- Lost rent during turnover: $500-$2,000

**Total Typical Range**: $1,000-$3,000 per turn

**Formula**:
```
Turnover Cost = (Total Turnover Expenses + Vacancy Loss) / Number of Turnovers
```

---

## Market Metrics

### Loss-to-Lease
**Definition**: Difference between market rent and in-place rent.

**Formula**:
```
Loss-to-Lease = Market Rent - In-Place Rent
Loss-to-Lease % = (Market Rent - In-Place Rent) / Market Rent
```

**Example**:
```
Market Rent: $2,000
In-Place Rent: $1,850
Loss-to-Lease = $150/month or 7.5%
```

**Interpretation**:
- Positive loss-to-lease: Potential for rent increases
- Negative loss-to-lease: Units over-rented (risk in renewals)

---

### Concession Rate
**Definition**: Value of concessions as percentage of gross rent.

**Formula**:
```
Concession Rate = Total Concession Value / Gross Potential Rent
```

**Example**:
```
1 month free on 12-month lease = 8.33% concession
$500 move-in special on $2,000/month = 2.08% concession (first month)
```

---

## Investment Metrics

### Price per Unit
**Definition**: Property value divided by total units.

**Formula**:
```
Price per Unit = Purchase Price / Total Units
```

**Example**:
```
Purchase Price: $10,500,000
Total Units: 50
Price per Unit = $210,000
```

**Market Comparison**: Varies widely by location and property quality

---

### Price per Square Foot
**Definition**: Property value divided by total square footage.

**Formula**:
```
Price per SF = Purchase Price / Total Square Feet
```

**Example**:
```
Purchase Price: $10,500,000
Total SF: 50,000
Price per SF = $210/SF
```

---

### Internal Rate of Return (IRR)
**Definition**: Annualized return accounting for timing of cash flows.

**Calculation**: Uses time-weighted cash flows (requires financial calculator or software)

**Example** (simplified):
```
Year 0: -$2,625,000 (investment)
Year 1-5: +$213,960 annually (cash flow)
Year 5: +$12,500,000 (sale proceeds)

IRR ≈ 22.4%
```

**Interpretation**:
- Target IRR: 15-20% for value-add multifamily
- Higher risk = higher IRR target
- Compare to alternative investments

---

## Performance Dashboards

### Monthly KPI Scorecard
```
Metric                  Actual    Target    Status
------------------------------------------------
Occupancy Rate          94.0%     95.0%     ⚠️
Collection Rate         98.2%     98.0%     ✅
NOI (MTD)              $57,830   $57,800    ✅
Expense Ratio           39.5%     40.0%     ✅
Renewal Rate (TTM)      58.0%     55.0%     ✅
Avg Days to Lease       28 days   30 days   ✅
Work Order Completion   85%       90%       ⚠️
Tenant Satisfaction     4.2/5     4.0/5     ✅
```

### Annual Performance Summary
```
Financial Performance
- Total Revenue: $1,156,600
- NOI: $693,960
- NOI Margin: 60%
- Cap Rate: 6.61%
- Cash-on-Cash Return: 8.15%

Operational Performance
- Average Occupancy: 94.5%
- Average Rent: $1,900/unit
- Lease Renewals: 58%
- Turnover Cost: $2,150/unit

Portfolio Health
- DSCR: 1.45x
- Debt Yield: 6.6%
- LTV: 75%
- Days Receivable: 12 days
```

This comprehensive metrics framework enables data-driven property management decisions and performance tracking.
