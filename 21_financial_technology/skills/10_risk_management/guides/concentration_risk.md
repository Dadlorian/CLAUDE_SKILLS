# Concentration Risk Guide

## Measuring Concentration

### Single-name Concentration
```
Portfolio: $1,000M total exposure

Counterparty A: $100M → 10% concentration
Counterparty B: $80M → 8%
Counterparty C: $70M → 7%
Counterparty D: $50M → 5%
Top 4: $300M → 30% concentrated

Limits:
- Single name: Max 5% = $50M
- Top 10: Max 25% = $250M

Current position:
- Counterparty A: 10% > 5% limit ✗ BREACH
- Top 4: 30% > 25% limit ✗ BREACH

Action: Reduce Counterparty A exposure by $50M
```

### Herfindahl-Hirschman Index (HHI)
```
HHI = Σ (Weight)²

Example:
3 equal exposures of 33% each:
HHI = 0.33² + 0.33² + 0.33² = 0.33

100 equal exposures of 1% each:
HHI = 100 × 0.01² = 0.01

More concentrated portfolio: Higher HHI
Perfectly diversified (infinite exposures): HHI = 0
Single exposure: HHI = 1
```

## Risk Aggregation
- Credit concentration
- Sector concentration
- Geographic concentration
- Funding concentration
- Collateral concentration

All must be measured and monitored
