# Credit Scoring Guide

## Building a Scorecard

### Variable Selection
```
Candidate variables:
1. Income: Ability to repay
2. Assets: Backup payment source
3. Debt ratio: Leverage
4. Payment history: Willingness to pay
5. Employment stability: Income stability
6. Loan purpose: Risk of use
7. Collateral: Recovery source
8. Credit bureau score: Comprehensive assessment

Statistical testing (Information Value):
Income: IV = 0.45 ✓ Excellent
Assets: IV = 0.35 ✓ Excellent
Debt ratio: IV = 0.28 ✓ Good
Payment history: IV = 0.52 ✓ Excellent
Employment: IV = 0.18 ✓ Fair
Loan purpose: IV = 0.08 ✗ Weak
Collateral: IV = 0.32 ✓ Good
Credit score: IV = 0.55 ✓ Excellent

Select: Income, Assets, Debt Ratio, Payment History, Collateral, Credit Score
(Drop Employment, Loan Purpose for weak predictive power)
```

### Score Card Development
```
Raw Score Calculation:
z = β₀ + β₁(Income) + β₂(Assets) + β₃(Debt) + β₄(Payment) + β₅(Collateral) + β₆(Score)

Scaling:
Factor: 20
Offset: 600
Scaled Score = 600 + 20 × z

Score interpretation:
z = -1.0 → Score = 580 (high risk)
z = 0.0 → Score = 600 (average)
z = +1.0 → Score = 620 (low risk)
z = +2.0 → Score = 640 (very low risk)
```

### Decision Rules
```
Score Range    Rating    Decision       Rate
700+          A         Auto-approve   Tier 1 (best)
680-699       B         Manual review  Tier 2
650-679       C         Manual review  Tier 3
600-649       D         Likely decline Tier 4
< 600         E         Auto-decline   Tier 5 (worst)

Rate adjustments:
- Tier 1: Prime rate + 2%
- Tier 2: Prime rate + 3%
- Tier 3: Prime rate + 5%
- Tier 4: Prime rate + 8%
- Tier 5: Decline
```

### Monitoring & Maintenance
```
Monthly:
- Default rate by score band
- Compare actual vs predicted
- Population stability index

Quarterly:
- Refresh data
- Recalculate coefficients if PSI > 10%
- Update decision rules if needed

Annual:
- Full retraining
- Validation testing
- Board approval of updates
```
