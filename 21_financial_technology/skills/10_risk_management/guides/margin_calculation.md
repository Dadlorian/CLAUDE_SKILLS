# Margin & Collateral Calculation Guide

## Initial Margin

### Haircut Calculation
```
Collateral: Corporate bonds worth $1,000,000
Credit rating: BBB

Haircut components:
- Credit risk (default): 2%
- Interest rate risk (duration): 2%
- Liquidity risk (spread): 1%
- Total haircut: 5%

Available collateral value:
$1,000,000 × (1 - 0.05) = $950,000

Loan amount:
$950,000 (100% of haircut collateral)

Loan-to-value (LTV):
$950,000 / $1,000,000 = 95% LTV
```

### Stress Haircuts
```
Normal haircuts: 5%
Stress haircuts (crisis): 15%

If market stress occurs:
Stress collateral value: $1,000,000 × (1 - 0.15) = $850,000
Margin call: Borrower must provide $100,000 more collateral
```

## Variation Margin

### Daily Mark-to-Market
```
Day 1:
- Loan amount: $950,000
- Collateral value: $1,000,000
- Collateral available: $950,000
- Variation margin: $0 (balanced)

Day 2:
- Loan amount: Still $950,000
- Collateral market value: $990,000 (declined 1%)
- Collateral available: $990,000 × (1 - 0.05) = $940,500
- Variation margin: $940,500 - $950,000 = -$9,500
- Margin call: Borrower owes $9,500

Day 3:
- Collateral value: $1,010,000 (increased)
- Collateral available: $1,010,000 × 0.95 = $959,500
- Margin surplus: $959,500 - $950,000 = $9,500
- Return to borrower: $9,500
```

## Aggregate Exposure with Netting
```
Derivatives exposure with counterparty:
- Interest rate swap MTM: $2M (in-the-money)
- FX forward MTM: -$0.5M (out-of-the-money)
- Equity swap MTM: $1M (in-the-money)

Gross exposure: $2M + $1M = $3M (just positive MTMs)
With netting: $2M - $0.5M + $1M = $2.5M net
Potential future exposure: +$1M
Collateral requirement: $2.5M + $1M = $3.5M

Collateral posted: $3M
Shortfall: $0.5M → Margin call
