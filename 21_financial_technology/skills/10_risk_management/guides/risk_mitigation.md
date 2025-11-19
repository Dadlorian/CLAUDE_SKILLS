# Risk Mitigation Strategies

## Credit Risk Mitigation

### Collateral
```
Loan: $100M corporate credit
Collateral posted: Real estate worth $120M
Loan-to-value: 83%
Recovery in default: $120M × 80% (hair cut) = $96M
LGD: ($100M - $96M) / $100M = 4%

vs. Unsecured:
LGD: 60%

Collateral reduces LGD by 56 percentage points
```

### Diversification
```
Before diversification:
- Single counterparty: $50M
- Exposure concentration: 50% of capital

After diversification:
- 10 counterparties × $5M = $50M
- Exposure concentration: 5% of capital
- Default of one: $5M loss vs. $50M

Benefit: Reduces idiosyncratic risk
```

### Hedging
```
Position: $100M in corporate bonds
Risk: Credit spreads widen (bonds decline)

Hedge: Buy CDS protection on same reference
Cost: 100 bps = $1M annually

If spreads widen 300 bps:
- Bond loss: -$3M
- CDS gain: +$3M
- Net loss: $0 (minus hedge cost $1M)
```

## Market Risk Mitigation

### Duration Management
```
Current: Duration 5 years
Risk: Rates increase 100 bps → -5% loss = -$5M

Hedge: Reduce duration to 2 years
New risk: Rates increase 100 bps → -2% loss = -$2M
Hedge benefit: $3M protection

Cost: May give up some income
```

### Diversification
```
Portfolio 1 (No diversification):
- 100% equities
- Volatility: 20%
- VaR (95%): 3.3%

Portfolio 2 (With diversification):
- 50% equities + 50% bonds
- Correlation: -0.3
- Combined volatility: 10%
- VaR (95%): 1.6%

Diversification benefit: Reduce VaR by 50%
```

## Operational Risk Mitigation

### Control Environment
```
Risk: Data entry errors in loan system
Mitigation:
1. System validation rules (positive numbers only)
2. Dual entry verification (two people verify)
3. Reconciliation (daily vs. GL)
4. Audit trail (all changes logged)
5. Management review (monthly spot check)

Residual risk: <0.1% error rate
```

## Liquidity Risk Mitigation

### Funding Diversification
```
Current:
- Deposits: 80% of funding
- Wholesale: 20%

Risk: Deposit flight in crisis

Target:
- Deposits: 60% of funding
- Wholesale: 25%
- Capital: 15%

Benefit: More stable funding base
Achieve: Over 3-year plan
