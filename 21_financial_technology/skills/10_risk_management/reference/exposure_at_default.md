# Exposure at Default (EAD)

## Overview
EAD is the gross amount of exposure when a counterparty defaults. It includes drawn amounts, undrawn commitments that are drawn, and interest/fees accrued. EAD is uncertain for off-balance sheet items that depend on future drawdowns.

## EAD Definition

### Mathematical Definition
```
EAD = Drawn Amount + Undrawn Amount Expected to be Drawn

Example:
Credit Card:
- Current balance (drawn): $5,000
- Available credit (undrawn): $15,000
- If default today: EAD = $5,000

But model must account for future drawing:
- If card-holder draws another $5,000 before default
- New EAD = $10,000 at time of default

Expected future drawing: Credit Conversion Factor (CCF)
Expected EAD = $5,000 + $15,000 × CCF
```

## EAD Components

### 1. Drawn Exposure
**Amount already borrowed/used**

```
Loan example:
- Loan originated: $1,000,000
- Currently drawn: $800,000
- Drawn EAD = $800,000

Credit card example:
- Credit limit: $50,000
- Current balance: $12,500
- Drawn EAD = $12,500

Revolving line of credit:
- Commitment: $5,000,000
- Current utilization: $2,500,000
- Drawn EAD = $2,500,000
```

### 2. Undrawn Commitments
**Amount available but not yet used**

```
Loan example:
- Loan commitment: $1,000,000
- Currently drawn: $800,000
- Undrawn: $200,000

Credit card:
- Credit limit: $50,000
- Current balance: $12,500
- Undrawn: $37,500

Revolver:
- Commitment: $5,000,000
- Current utilization: $2,500,000
- Undrawn: $2,500,000

Question: What is EAD if default occurs?
Expected drawn amount = Current drawn + (Undrawn × CCF)
```

### 3. Accrued Interest & Fees
**Amount owed but not yet paid**

```
Corporate loan:
- Principal: $100,000,000
- Interest accrued but not paid: $250,000
- Fees accrued: $50,000
- Total EAD: $100,300,000

For simplicity, often ignored in EAD calc
(small relative to principal)
```

## Credit Conversion Factor (CCF)

### Definition
**Percentage of undrawn commitment expected to be drawn at default**

```
EAD = Drawn + (Undrawn × CCF)

Where:
CCF = % of undrawn expected drawn if default
Range: 0% to 100%

Example:
Drawn: $1,000,000
Undrawn: $500,000
CCF: 50%
EAD = $1,000,000 + ($500,000 × 50%) = $1,250,000
```

### CCF by Product Type

```
Product                          Typical CCF
Mortgages (fixed)               0-5%   (borrow rest, don't draw)
Auto loans (fixed)              0-10%
Term loans (fixed draw)         25-50% (may draw commitment)
Revolving lines (credit cards)  50-100%
Trade credit (LC, guarantee)    25-75%
Derivatives (marked-to-market)  50-100%
Securities lending repo         100%

Rationale for CCF variations:
- Mortgages: Full amount disbursed at origination, CCF ≈ 0
- Credit cards: Customer likely draws more if in distress
- Revolving: May draw undrawn commitment pre-default
- Derivatives: Full collateral owed on default
```

### CCF Variation by Condition
```
Drawn amount (indicator of utilization):

If drawn < 20%:
- Customer not desperate
- CCF low (5-20%)
- Example: New borrower with $1M commitment, drew $100k
- At default, expected draw = $100k + $900k × 10% = $190k

If drawn 50-80%:
- Customer utilizing facility
- CCF moderate (40-60%)
- Example: Customer drew $500k of $1M
- At default, expected draw = $500k + $500k × 50% = $750k

If drawn > 90%:
- Customer maxed out
- CCF low (5-20%)
- Little ability to draw more (already at limit)
- Example: Customer drew $950k of $1M
- At default, expected draw = $950k + $50k × 20% = $960k

Non-linear: CCF highest at 40-80% utilization
```

### Time Decay of Commitments
```
New commitment (drawn 0%):
- CCF = 50% (if drawn, likely to draw full facility)

Commitment aging:
- Year 1: CCF = 50%
- Year 2: CCF = 40% (less likely to draw as time passes)
- Year 3: CCF = 30%
- Year 4+: CCF = 20% (old commitments rarely drawn)

Effect: Older undrawn amounts contribute less to EAD
```

## EAD by Product

### Revolving Credit (Credit Cards)
```
High utilization:
- Drawn: $4,000
- Limit: $5,000
- Undrawn: $1,000
- CCF: 80% (likely to use remaining credit)
- EAD = $4,000 + $1,000 × 80% = $4,800

Low utilization:
- Drawn: $500
- Limit: $5,000
- Undrawn: $4,500
- CCF: 50% (may or may not draw)
- EAD = $500 + $4,500 × 50% = $2,750
```

### Term Loans (Mortgages, Auto)
```
Mortgage:
- Loan amount: $300,000
- Drawn: $300,000 (fully drawn at origination)
- Undrawn: $0
- EAD = $300,000

Auto loan:
- Loan amount: $30,000
- Drawn: $30,000 (fully drawn at purchase)
- Undrawn: $0
- EAD = $30,000

Because: Both funded in full at origination
No additional drawing expected
```

### Corporate Loans (Revolving, Committed, Uncommitted)
```
Committed Revolver (guaranteed access):
- Commitment: $100,000,000
- Current draw: $60,000,000
- Undrawn: $40,000,000
- CCF: 60% (likely to draw in distress)
- EAD = $60M + $40M × 60% = $84M

Uncommitted Line (bank can refuse):
- Commitment: $100,000,000
- Current draw: $60,000,000
- Undrawn: $40,000,000
- CCF: 20% (bank may refuse to draw more)
- EAD = $60M + $40M × 20% = $68M

Difference: Commitment status affects CCF
```

### Derivative Exposures
```
Spot market exposure: Marked-to-market
Example - Interest rate swap:
- Notional: $100,000,000
- Current mark-to-market: $2,000,000 (in-the-money)
- Potential Future Exposure (PFE): $5,000,000 (could be more in-the-money)

EAD = Current Exposure + PFE
    = $2,000,000 + $5,000,000
    = $7,000,000

Or with collateral adjustment:
If collateral posted: $3,000,000
EAD = MAX(0, $7,000,000 - $3,000,000)
    = $4,000,000
```

### Off-Balance Sheet Commitments
```
Letters of Credit (LC):
- Commitment: $10,000,000
- Typical CCF: 75% (likely to be drawn)
- Accrual: Customer pays fees but amount may be drawn
- EAD = $10,000,000 × 75% = $7,500,000

Guarantees:
- Maximum guarantee: $50,000,000
- CCF: 75-100% (if primary borrower defaults, guarantor drawn)
- EAD = $50,000,000 × 85% = $42,500,000

Price commitments:
- Commitment: $20,000,000
- CCF: 50% (firm may not exercise if unprofitable)
- EAD = $20,000,000 × 50% = $10,000,000
```

## EAD Modelling

### Regression Model
```
EAD_i = α + β₁ × Utilization_i + β₂ × Loan_Age_i + ε_i

Where:
EAD_i = Exposure at default (% of commitment)
Utilization_i = Current drawn / commitment
Loan_Age_i = Years since origination

Estimated coefficients:
α = 0.20 (base EAD if nothing drawn)
β₁ = 0.50 (50% of additional utilization becomes EAD)
β₂ = -0.02 (decreases 2% per year of age)

Prediction for new commitment:
Utilization: 60%
Age: 2 years

EAD% = 0.20 + 0.50 × 0.60 + (-0.02) × 2
     = 0.20 + 0.30 - 0.04
     = 0.46 = 46% of commitment

If commitment = $1,000,000:
EAD = $460,000
```

### Lookup Tables / Matrices
```
By utilization and product type:

Utilization   Credit Card   Revolver   Committed LC
0-20%         25%          20%        40%
20-40%        45%          35%        55%
40-60%        65%          50%        70%
60-80%        80%          65%        85%
80-100%       90%          75%        95%
>100%         100%         85%        100%

Example for credit card at 50% utilization:
CCF = 65%
If commitment = $10,000 and drawn = $5,000:
EAD = $5,000 + ($5,000 × 65%) = $8,250
```

## EAD in Downturns

### Downturn EAD (d-EAD)
**EAD in stress scenario, used for capital calculation**

```
Normal environment EAD: $1,000,000
Downturn EAD: $1,200,000

In downturn:
- Customers may draw more (stressed for cash)
- CCF increases (50% → 70%)
- Customers may accumulate more debt before default

Used in Basel III capital:
RWA = d-EAD × Risk Weight
Results in higher capital requirement
```

### Stress Drawdown Pattern
```
Normal: Customer draws commitment gradually
Stress: Customer draws aggressively before default

Normal drawdown pattern:
- Month 1-6: Average utilization 40%
- Default in month 12: EAD = 40% of commitment

Stress pattern (2008 type crisis):
- Month 1-3: Utilization up to 60%
- Month 4-6: Utilization up to 80%
- Month 7-9: Utilization up to 95%
- Default in month 12: EAD = 95% of commitment

Model adjustment:
Normal EAD assumption: 50%
Downturn EAD assumption: 80%
```

## EAD Aggregation & Netting

### Bilateral Netting
```
Company A with Counterparty B:
Assets (owed to us): $5,000,000
Liabilities (owed to them): $3,000,000
Gross EAD: $5,000,000

With bilateral netting agreement:
Net position: $5,000,000 - $3,000,000 = $2,000,000
Net EAD: $2,000,000 (50% reduction)

Reduction in EAD: $3,000,000 / $5,000,000 = 60% reduction
Reduces capital requirement significantly
```

### Portfolio Aggregation
```
Counterparty X across all products:
- Term Loan: $10,000,000
- Revolver: $5,000,000 drawn + $5,000,000 undrawn (CCF 50%)
- Derivatives: $2,000,000 MtM + $1,000,000 PFE
- LC: $3,000,000 × 75% CCF

Total EAD:
- Term Loan: $10,000,000
- Revolver: $5,000,000 + $2,500,000 = $7,500,000
- Derivatives: $3,000,000
- LC: $2,250,000

Gross EAD: $22,750,000

Net of collateral ($5,000,000):
Final EAD: $17,750,000
```

## EAD Backtesting

### Actual vs. Predicted EAD
```
Default cohort from 2008-2010:
Defaulted 100 commitments

Predicted EAD    Count    Actual EAD    Bias
$500k-$750k      20       $600k         +$100k
$750k-$1M        35       $850k         +$100k
$1M-$1.5M        30       $1.1M         +$100k
$1.5M+           15       $1.8M         +$300k

Average predicted: $1.0M
Average actual: $1.1M
Bias: +$100k per commitment (10% underestimate)

Reason: In 2008 crisis, customers drew more undrawn
commitments than model predicted
CCF should have been higher in downturns
```

### Benchmark Analysis
```
Our EAD model vs. industry standards:

Product            Our CCF    Industry Avg    Difference
Credit Card        55%        60%             -5% (conservative)
Revolving Line     50%        55%             -5% (conservative)
Committed LC       80%        75%             +5% (aggressive)
Guarantee          75%        70%             +5% (aggressive)

Impact on capital:
+5% CCF = ~2% higher capital requirement
Our model more conservative on revolvers
More aggressive on guarantees
```
