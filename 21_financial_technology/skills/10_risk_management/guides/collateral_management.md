# Collateral Management Guide

## Haircuts & Valuation

### Haircut Application
```
Collateral type: Corporate bonds (BBB rated)
Market value: $1,000,000

Haircuts:
- Normal times: 5% haircut
- Stress times: 15% haircut

Loan amount:
- Normal: $950,000 (95% LTV)
- Stress: $850,000 (85% LTV)

If bonds decline 10% in value:
- Market value: $900,000
- Available collateral: $850,000 (stressed basis)
- Loan shortfall: $50,000
- Margin call: Borrower must provide $50,000 more collateral
```

### Recovery Rates by Collateral
```
Type                 Normal Recovery   Stress Recovery
Cash                 100%             100%
Government bonds     98%              96%
AAA Corporate        95%              92%
Investment Grade     90%              85%
High yield bonds     75%              60%
Real estate         85%              65%
Equipment           70%              40%
Inventory           50%              20%
Equities            70%              40%
```

## Monitoring Collateral
```
Daily:
- Mark collateral to market
- Calculate LTV/coverage ratio
- Identify margin call requirements
- Monitor concentration

Weekly:
- Report to risk committee
- Adjust haircuts if needed
- Monitor stress scenarios

Monthly:
- Independent collateral valuations
- Aging analysis
- Concentration by type
```
