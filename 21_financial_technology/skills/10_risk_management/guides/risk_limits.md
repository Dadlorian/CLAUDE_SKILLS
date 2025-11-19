# Risk Limits Framework Guide

## Setting Limits

### Process
1. Determine risk appetite (Board)
2. Calculate available budget (Risk Committee)
3. Allocate to business units
4. Set position limits
5. Monitor daily
6. Escalate breaches

### Example
```
Bank capital: $1B
Risk appetite: Use 50% for risk-weighted assets
Available budget: $500M

Allocation:
- Credit risk: 60% = $300M
- Market risk: 25% = $125M
- Operational: 15% = $75M

Credit Risk Limits:
Total portfolio: $300M capital budget
- Single name: Max 5% of capital = $50M
- Sector: Max 10% each = $100M per sector
- Top 10: Max 25% = $250M

Market Risk Limits:
- Desk VaR: $50M per desk
- Daily loss: $5M maximum
- Greeks: Delta $100M, Gamma $20M, Vega $10M

Position Limits:
- Interest rate swap: $500M notional
- Bond portfolio: $1B notional
- Equity positions: $250M
```

## Monitoring Limits

### Daily Monitoring
```
Market Risk Dashboard:
Desk/Product    VaR Limit   Current VaR   % of Limit   Status
Rates           $50M        $35M          70%          ✓ Green
Credit          $40M        $32M          80%          ⚠ Yellow
Equity          $30M        $25M          83%          ⚠ Yellow
FX              $10M        $8M           80%          ⚠ Yellow
Total           $130M       $100M         77%          ⚠ Yellow

Credit Risk Dashboard:
Counterparty     Exposure    Limit    % of Limit   Status
Bank A           $45M        $50M     90%          ⚠ Yellow
Corp B           $35M        $50M     70%          ✓ Green
Corp C           $50M        $50M     100%         ✗ RED!
Energy Sector    $95M        $100M    95%          ⚠ Yellow
Real Estate      $75M        $100M    75%          ✓ Green
```

### Escalation Procedures
```
Green (0-80%): No action, monitoring continues

Yellow (80-100%): 
- Notify desk manager
- Discuss position reduction within 1-2 days
- No new positions in this area
- Daily monitoring

Red (>100%):
- Immediate escalation to CRO
- Stop new positions immediately
- Urgent remediation (within same trading day)
- Risk committee briefed

Persistent breach (>1 day):
- Senior management/CEO involved
- Potential enforcement action
- Capital add-on may be required
- Compensation may be clawed back
```

## Limit Types

### VaR Limits
- Daily VaR maximum by desk
- Usually 95% or 99% confidence
- Monitored real-time
- Fastest to monitor

### Greeks Limits
- Delta (directional exposure)
- Gamma (convexity, optionality)
- Vega (volatility exposure)
- Theta (time decay)
- Rho (interest rate sensitivity)

### Notional Limits
- Maximum notional exposure per product
- Simple to calculate
- Used for off-balance sheet
- Less risk-sensitive than VaR

### Loss Limits
- Daily loss threshold
- Monthly loss threshold
- Year-to-date loss threshold
- Triggered when actual loss exceeds limit

### Concentration Limits
- Single-name exposure caps
- Sector caps
- Geographic caps
- Product concentration
