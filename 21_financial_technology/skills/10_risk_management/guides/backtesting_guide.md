# Backtesting Guide

## VaR Backtesting

### Monthly Backtesting
```
250 trading days of data
95% confidence level expected: 5% × 250 = 12-13 exceptions
99% confidence level expected: 1% × 250 = 2-3 exceptions

Track exceptions (days where loss > VaR):
Month 1: 2 at 99% ✓ (expect 2-3)
Month 2: 1 at 99% ✓
...
12 months: Total 30 exceptions at 99% ✓ (expect 24-36)

Green zone: 0-4 exceptions at 95% VaR for month ✓
Yellow zone: 5-9 exceptions ⚠
Red zone: 10+ exceptions ✗
```

### Backtesting Report
```
VaR 99% (1-day) Backtesting Results:

Date Range: 2024 Q1
Expected exceptions: 2-3 per month
Actual by day:
- Jan: 2 exceptions ✓
- Feb: 1 exception ✓
- Mar: 3 exceptions ⚠

Q1 Total: 6 exceptions (expect 6-9) ✓ ACCEPTABLE
No major issues detected
Model remains valid
```

## Credit Model Backtesting

### Default Rate by Rating
```
Rating    Predicted PD   Loans    Actual Defaults   Actual DR
AAA       0.10%         1,000    1                 0.10%  ✓
AA        0.30%         2,000    6                 0.30%  ✓
A         0.70%         5,000    35                0.70%  ✓
BBB       1.50%         8,000    120               1.50%  ✓
BB        4.00%         4,000    160               4.00%  ✓
B         8.00%         2,000    160               8.00%  ✓

Conclusion: Model well-calibrated
Predicted ≈ Actual across all ratings
```

## Limits Backtesting

### Stress Test Validation
```
Stress test scenario: 2008 Crisis
Predicted loss: $25M
Actual loss in 2008: $24.8M
Error: -0.2M (0.8%) ✓ Excellent

Hypothetical scenario: 200 bps rate shock
Predicted loss: $8M
Actual loss in 2004 steepening: $7.5M
Error: -$0.5M (6.25%) ✓ Good
```

## Sign-off
Validation team: Risk Management
Review date: Monthly/Quarterly
Approval: CRO, Board Risk Committee
