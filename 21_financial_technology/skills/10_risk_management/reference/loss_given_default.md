# Loss Given Default (LGD) Models

## Overview
LGD is the percentage of exposure that is lost if a counterparty defaults, accounting for recoveries. It's a critical input to credit loss calculations and pricing, varying significantly with collateral, seniority, and market conditions.

## LGD Definition

### Mathematical Definition
```
LGD = (EAD - Recovery Amount) / EAD

Or:
LGD = 1 - (Recovery Rate)

Example:
Loan amount (EAD): $1,000,000
Recovery amount: $600,000
LGD = ($1,000,000 - $600,000) / $1,000,000 = 40%

Recovery rate: 60%
LGD = 1 - 0.60 = 40%
```

### LGD vs. Recovery Rate
```
Recovery Rate = (Amounts Recovered) / (Total Defaulted Amounts)
LGD = 1 - Recovery Rate

If recovery = 70%, then LGD = 30%
```

## LGD Drivers

### 1. Collateral Type & Value
**Most Important Factor**

```
Collateral Type          Typical Recovery    Typical LGD
Mortgages (1st lien)     80-95%             5-20%
Auto loans               75-85%             15-25%
Equipment financing      65-75%             25-35%
Corporate bonds (Sr.)    50-70%             30-50%
Corporate bonds (Sub.)   30-50%             50-70%
Unsecured loans          20-40%             60-80%
Equity/mezzanine         0-20%              80-100%

Key factors:
- Type of collateral (real estate > equipment > inventory)
- Location (real estate valuation varies)
- Condition (equipment degradation)
- Liquidity (can be sold quickly)
- Legal precedence (1st lien vs. 2nd lien)
```

### 2. Seniority
**Who gets paid first in bankruptcy**

```
Priority       Typical Recovery
Senior Secured 70%
Senior Unsecured 40%
Subordinated   20%

Example - Company bankrupt with $100M assets:
Senior secured debt: $30M → recover 70% = $21M
Senior unsecured debt: $40M → recover 40% = $16M
Subordinated debt: $30M → no recovery = $0M
Equity: $0M (always wiped out)

Equity holders lose everything
Subordinated creditors lose 100%
Senior unsecured lose 60%
Senior secured lose 30%
```

### 3. Loan-to-Value (LTV) Ratio
**Exposure relative to collateral value**

```
For mortgages:
LTV 60%: LGD ≈ 5% (lots of cushion)
LTV 80%: LGD ≈ 15% (moderate cushion)
LTV 95%: LGD ≈ 30% (little cushion)
LTV 105%: LGD ≈ 50% (underwater, sell at loss)

Reason: Higher LTV = less collateral to cover default
Recovery depends on home sale price
If home worth $400k (borrower paid $400k at LTV 80%)
Now worth $350k (13% decline)
Recovery = $350k (covers 80% loan)
LGD = 0% (covered)

But if home worth $300k (25% decline)
Recovery = $300k (covers only 75% of loan)
Loss = $100k / $400k = 25% LGD
```

### 4. Time to Recovery

**Recovery Timeline**:
```
Days  Recovery %
30    10% (quick asset sales)
60    25% (equipment auction)
90    45% (asset liquidation)
180   60% (legal proceedings)
365   70% (court awards)
730   75% (appeals resolved)

Present value adjustment:
If recovery is $100k in 2 years:
PV = $100k / (1.05)² = $90.70k
Loss increased due to time value

LGD adjustment:
Nominal recovery: 70%
PV recovery (at 5% discount): 60%
LGD: 40% instead of 30%
```

### 5. Economic Cycle
**LGD varies with economic conditions**

```
Normal times: LGD = 30% (good asset values, active markets)
Mild recession: LGD = 35% (asset values decline 10-15%)
Severe recession: LGD = 45% (asset values decline 30-40%)
Depression: LGD = 60% (asset values collapse, no buyers)

2008 Crisis example:
Expected home value recovery: 85%
Actual recovery: 60% (homes fell 35%)
LGD increased from 15% to 40%

Fire sales:
If must sell quickly: LGD increases 10-20%
Due to discount from market value
Buyer knows seller desperate
```

### 6. Haircuts & Valuation
**Applied to collateral in lending decisions**

```
Collateral valuation before default:
Home market value: $500,000

Market haircut: 10% (expect 10% decline from current value)
Haircut value: $500,000 × 90% = $450,000

Stress haircut: 25% (could decline 25% in crisis)
Stressed value: $500,000 × 75% = $375,000

Loan amount: $400,000 at LTV 80%
Conservative LGD: ($400,000 - $375,000) / $400,000 = 6.25%
```

## LGD Estimation Approaches

### 1. Historical LGD
**Approach**: Use actual defaults from past to estimate LGD.

```
Company defaults, 2010-2015:

Default  EAD        Recovery   LGD
1        $1,000,000 $600,000   40%
2        $500,000   $350,000   30%
3        $2,000,000 $800,000   60%
4        $1,500,000 $900,000   40%
5        $800,000   $300,000   62.5%

Average LGD: (40+30+60+40+62.5) / 5 = 46.5%

Weighted by exposure:
Σ(EAD × LGD) / Σ(EAD) = $3,845,000 / $5,800,000 = 66.3%

Advantages:
- Based on actual recoveries
- Simple to calculate
- Incorporates real-world dynamics

Disadvantages:
- Limited sample size
- May not represent current conditions
- Historical defaults may not predict future LGD
```

### 2. Regression Model for LGD
**Approach**: Model LGD as function of loan characteristics.

```
LGD = α + β₁×LTV + β₂×Seniority + β₃×Collateral_Type + ε

Example from data:
α = 10% (intercept)
β₁ = 0.30 (LTV coefficient)
β₂ = -20% (seniority: -20% for senior secured vs. unsecured)
β₃ = -40% (if commercial real estate vs. other)

Prediction for new loan:
LTV: 80%
Senior secured
Commercial real estate

LGD = 10% + 0.30×80% + (-20%) + (-40%)
    = 10% + 24% - 20% - 40%
    = -26% → 0% (cannot be negative)
    Use: 5% (minimum possible LGD)

Advantages:
- Can leverage large default sample
- Incorporates multiple drivers
- Can validate with statistical tests

Disadvantages:
- Model dependent
- Relationships may not be stable
- Limited by available data
```

### 3. Expert Judgment & Collateral Appraisals
**Approach**: Use domain experts and independent valuations.

```
Mortgage LGD calculation:
Current home value: $500,000 (appraised by independent appraiser)

Stress scenarios:
Base case: Home worth $450,000 in 12 months (10% decline)
  Recovery: $450,000, LGD = 10%

Stress case: Home worth $350,000 in 12 months (30% decline)
  Recovery: $350,000, LGD = 30%

Severe stress: Home worth $250,000 (50% decline)
  Recovery: $250,000, LGD = 50%

Use weighted average:
Probability:
- Base (prob 50%): LGD = 10%
- Stress (prob 35%): LGD = 30%
- Severe (prob 15%): LGD = 50%

Expected LGD = 0.50×10% + 0.35×30% + 0.15×50%
            = 5% + 10.5% + 7.5%
            = 23%
```

## LGD by Product Type

### Secured Mortgages
```
First Lien (primary mortgage):
- LTV < 80%: LGD = 5-10%
- LTV 80-90%: LGD = 10-20%
- LTV 90-100%: LGD = 20-35%
- LTV > 100%: LGD = 50%+

Second Lien (home equity):
- LGD = 50-70% (subordinated)

Sub-prime mortgages (2008 Crisis):
- Expected LGD: 20-30%
- Actual LGD: 50-70% (due to price collapse)
```

### Auto Loans
```
Typical characteristics:
- Vehicles depreciate 15-20% annually
- Loan matures as vehicle depreciates

LTV at origination:
LTV 80%: LGD = 5% (car worth more than loan)

Year 1: Car value down to 85% of original
LTV increased to 94%: LGD = 15%

Year 3: Car value down to 60% of original
LTV = 135% (underwater)
If repossess & sell: LGD = 40-50%
```

### Commercial Real Estate (CRE) Loans
```
Senior Secured:
- Average recovery: 60-75%
- LGD: 25-40%
- Good collateral, long sales cycles

Mezzanine (Junior):
- Average recovery: 20-40%
- LGD: 60-80%
- Subordinated to senior debt

2008 Crisis impact:
- Expected LGD: 30-40%
- Actual LGD: 60-80% (values fell 40-50%)
```

### Corporate Bonds
```
Senior Secured Bonds:
- Average recovery: 65%
- LGD: 35%

Senior Unsecured Bonds:
- Average recovery: 40%
- LGD: 60%

Subordinated/Mezzanine:
- Average recovery: 25%
- LGD: 75%

Historical variation:
- Best case (court case, assets realization): 90%
- Typical case: 40%
- Worst case (total loss): 0%

Average: 40% across corporate defaults
```

### Credit Cards
```
Unsecured revolving credit:
- No collateral
- LGD = 100% - (recovery efforts)

Collections:
- Internal collections: 10-20% recovery
- External agency: 5-10% recovery
- Legal: 2-5% recovery

Net recovery: 15-25%
LGD: 75-85%

High because:
- Unsecured
- Small balances (not worth pursuing)
- Data mining helps find active collectors
```

## Downturn LGD (d-LGD)

### Concept
**LGD in economic downturn stress scenario, used for capital calculation**

```
Through-the-Cycle (average) LGD: 30%
Downturn LGD (stress): 50%

Why higher in downturn:
- Asset values decline (collateral worth less)
- Liquidity dries up (harder to sell)
- Recovery takes longer
- Sale may be at distressed prices
```

### Calculation
```
Base LGD (normal times): 30%
Stress adjustment:
- Asset value decline: +10%
- Liquidity drag: +5%
- Time to recovery: +3%
- Distress sale discount: +2%

Downturn LGD: 30% + 20% = 50%

Used in Basel III IRB:
RWA calculated using d-LGD = 50%
Results in higher capital requirement
More conservative than using LGD = 30%
```

## LGD in IFRS 9 / ECL Calculation

### Expected LGD
```
IFRS 9 requires forward-looking ECL:
ECL = Σ P(scenario_i) × LGD_i × EAD_i

Example:
Loan: $100k, Stage 1 (low risk)

Scenario 1 (prob 95%): No default
  LGD = 0

Scenario 2 (prob 4%): Economic decline, default
  LGD = 30% (good recovery expected)

Scenario 3 (prob 1%): Crisis, default
  LGD = 50% (poor recovery)

ECL = 0.95×0% + 0.04×30% + 0.01×50%
    = 0 + 1.2% + 0.5%
    = 1.7% of exposure
    = $1,700 loan loss reserve
```

## LGD Validation & Backtesting

### Comparing Predicted to Realized LGD
```
Cohort of defaults:
Predicted LGD    Count    Realized LGD    Variance
10%              50       12%             +2%
20%              80       22%             +2%
30%              120      28%             -2%
40%              100      44%             +4%
50%+             50       55%             +5%

Average bias: +2.2% (model understates LGD by 2.2%)
Some variance expected due to:
- Individual loan differences
- Economic conditions
- Collateral valuation
```

### Stress Scenario LGD Testing
```
Test if model captures downturn LGD:

Model assumption: d-LGD = 50% in 2008 scenario
Actual 2008 realized LGD: 55%
Error: +5% (underestimated by 5%)

2008 impact: -48% equity market, -35% home prices
Model predicted -35% collateral value decline
Actual was -40% decline
Reason: Model underestimated crisis severity
```
