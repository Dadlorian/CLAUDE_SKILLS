# Fraud Analytics Reference

## Overview
Fraud analytics transforms raw transaction and investigation data into actionable insights for improved fraud prevention and system performance.

## Analytical Frameworks

### Fraud Funnel Analysis
```
All Transactions (1M/day)
  ↓ 98% pass rules (20K decline)
Allowed Transactions (980K)
  ↓ 99.5% legitimate (4,900 suspected fraud)
Transactions Submitted (475K)
  ↓ 99% legitimate (475 suspected chargebacks)
Confirmed Fraud Cases (475)
  ↓ Analysis to improve detection

Metrics:
  - Catch rate: 475/500 confirmed fraud = 95%
  - False decline rate: 20K/1M = 2%
  - True positive: 475
  - False positive: 20K - 475 = 19,525
```

### RFM Analysis (Recency, Frequency, Monetary)

**Recency**: Days since last transaction
```
Active (0-30 days): High engagement, lower fraud
Dormant (31-90 days): Moderate risk
Inactive (>90 days): Higher risk if suddenly active
```

**Frequency**: Transaction count in period
```
High (>10/month): Established behavior
Medium (2-10/month): Regular customer
Low (1/month): Occasional buyer, higher risk for new behavior
```

**Monetary**: Total transaction amount
```
High: Valuable customer, fraud loss high
Medium: Standard customer
Low: Small transaction customer, lower risk
```

### Cohort Analysis
```
Group 1: Acquired January 2024
  - Fraud rate: 2.5%
  - Chargeback rate: 0.8%
  - Refund rate: 5%
  - Average order value: $150

Group 2: Acquired February 2024
  - Fraud rate: 1.8%
  - Chargeback rate: 0.6%
  - Refund rate: 4%
  - Average order value: $165

Insights:
  - January cohort higher fraud
  - Potential marketing campaign issue
  - Adjust targeting/verification for January-like segments
```

### Attribution Analysis
```
Which factors most predict fraud?

Single-Factor Analysis:
- New account: 5x fraud rate
- High amount: 3x fraud rate
- Velocity spike: 4x fraud rate
- New device: 2x fraud rate

Multi-Factor Analysis:
- New account + velocity: 12x fraud rate
- New account + new device + velocity: 25x fraud rate
- Weighted combinations: 18x fraud rate

Insights:
  - New accounts + velocity = highest risk
  - Device importance grows with account age
  - Multiple factors compound risk exponentially
```

## Performance Metrics

### Detection Performance

**Precision & Recall**
```
Precision = TP / (TP + FP) = Fraud caught / Total flagged
Recall = TP / (TP + FN) = Fraud caught / Total fraud

Trade-off:
- High precision: Few false positives, some fraud misses
- High recall: Catches fraud, many false positives

Optimal balance varies by business:
  - Fraud-heavy merchant: Optimize for recall
  - High-value merchant: Optimize for precision
```

**ROC & AUC**
```
ROC Curve: Plot TPR vs FPR at different thresholds

AUC (Area Under Curve):
  - 0.5: Random classifier
  - 0.7-0.8: Good classifier
  - 0.8-0.9: Very good classifier
  - >0.9: Excellent classifier

Interpretation:
  - AUC = 0.85: 85% chance model ranks fraud higher than legitimate
```

**F1-Score**
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)

Harmonic mean of precision and recall
Values 0-1 (higher = better)
Balanced metric for imbalanced datasets
```

### Business Metrics

**Fraud Loss Rate**
```
Fraud_Loss_Rate = Confirmed_Fraud_Loss / Total_Transaction_Amount

Example:
  Total transactions: $10M
  Confirmed fraud: $50K
  Fraud loss rate: 0.5%

Benchmark varies by industry:
  - Low-risk: <0.1%
  - Standard: 0.1-0.5%
  - High-risk: 0.5-2%
```

**Cost per Transaction**
```
Operating costs:
  - Model training/serving: $X/month
  - Rules engine operation: $X/month
  - Investigation staff: $X/month
  - False positive cost: $X (customer friction)

Total monthly cost / Total transactions
= Cost per transaction

Justification:
  - Must be less than fraud saved per transaction
  - ROI = Fraud prevented - Costs
```

**Detection Efficiency**
```
Fraud caught without false decline: High value
Fraud caught with false decline: Moderate value (customer impact)
Fraud missed: Negative impact

Efficiency = (Fraud Caught * Weight) / Total Cost
```

### Operational Metrics

**Alert Volume & Throughput**
```
Daily alerts generated
Alerts requiring investigation
Investigation capacity

Alert-to-case ratio:
  - 1,000 alerts/day
  - 10% investigated (100 cases)
  - 50% confirmed fraud (50 confirmed)

Precision of alerts: 50% (high precision)
```

**Investigator Productivity**
```
Cases per investigator per day
Time to case resolution
Case complexity distribution
Investigator agreement rate
```

**Case Management Metrics**
```
Cases opened: 100
Cases closed: 95
Cases pending: 5
Average case duration: 5 days
Backlog age: 10 days

Investigation quality:
  - False positive rate: 5% (over-investigate)
  - True positive rate: 85% (confirmation rate)
```

## Dashboards & Visualization

### Executive Dashboard
```
Real-Time Metrics:
- Fraud detected today: $25K (0.2% of transactions)
- False decline rate: 1.8%
- Investigation backlog: 45 cases
- Investigator utilization: 92%

Trend Charts:
- Weekly fraud rate trend
- Detection rate by method
- Chargeback rate trend
- Customer satisfaction score

Red indicators:
- Fraud spike alert
- High false decline warning
- Backlog growing
```

### Operational Dashboard
```
Daily Monitoring:
- Alert count by type
- Detection rate by model
- Rules triggered frequency
- Top fraud patterns today

Investigation Queue:
- Cases by priority
- Average case age
- Cases assigned per investigator
- Cases pending analyst review

Performance:
- Fraud detected vs. estimated
- Detection latency
- System uptime
```

### Analytical Dashboard
```
Model Performance:
- Precision/Recall curves
- ROC curves
- Model scores distribution
- Feature importance ranking

Fraud Patterns:
- Fraud types distribution
- Geographic fraud hotspots
- Merchant category fraud rates
- Customer segment fraud rates

Trends:
- Fraud evolution over time
- Detection method effectiveness
- Seasonal patterns
- New fraud techniques
```

## Deep Dive Analysis Techniques

### Fraud Pattern Discovery

**Transaction Timeline Analysis**
```
Fraudster activity pattern:
Day 1: Small test transaction ($5)
Day 2: Medium transaction ($50)
Day 3: Large transaction ($500)
Day 4: Multiple rapid transactions ($100 each)

Pattern recognition:
- Escalation over time
- Testing behavior
- Rapid acceleration

Detection: Flag accounts showing escalation
```

**Temporal Analysis**
```
By hour of day:
- Legitimate: Primarily 9-17 (business hours)
- Fraud: Concentrated 2-4 AM (off-hours)

By day of week:
- Legitimate: Spread across week
- Fraud: Weekends, late nights

By season:
- Legitimate: Peaks around holidays
- Fraud: More consistent year-round

Adjustment: Different rules/thresholds by time
```

**Geographic Analysis**
```
Fraud hot spots:
- Country X: 2% fraud rate (vs. 0.5% average)
- Region Y: 3x fraud rate

Legitimate patterns:
- Customers travel: Expected variation
- Seasonal tourism: Expected

Fraudulent patterns:
- Multiple countries in short time
- Impossible travel distances
- High-risk regions only

Mitigation: Geographic rules, velocity checks
```

### Segment Analysis

**Customer Segment Performance**
```
Segment A (VIP customers):
- Fraud rate: 0.1%
- Chargeback rate: 0.2%
- Refund rate: 1%

Segment B (Standard):
- Fraud rate: 0.5%
- Chargeback rate: 0.6%
- Refund rate: 4%

Segment C (New/High-risk):
- Fraud rate: 2%
- Chargeback rate: 1.5%
- Refund rate: 10%

Insight: Risk varies significantly by segment
Adjustment: Segment-specific rules/thresholds
```

**Merchant Performance**
```
Category A (High-risk):
- Fraud rate: 2%
- Chargeback rate: 1.5%
- Decline rate: 3%

Category B (Standard):
- Fraud rate: 0.5%
- Chargeback rate: 0.6%
- Decline rate: 1%

Category C (Low-risk):
- Fraud rate: 0.1%
- Chargeback rate: 0.2%
- Decline rate: 0.5%

Insight: Merchant type critical to risk
Adjustment: Merchant-specific scoring
```

### Root Cause Analysis

**Fraud Spike Investigation**
```
Observation: Fraud rate jumped 50% (0.5% to 0.75%)

Investigation:
1. New fraud pattern? Check top 20 cases
2. Marketing change? Check campaigns started
3. System change? Check recent deployments
4. Competitor closure? Check market events
5. Data quality? Check alert data accuracy

Finding: New marketing campaign acquired risky customer segment
Action: Tighten rules for similar segment
Result: Return to baseline fraud rate
```

**False Positive Investigation**
```
Observation: Decline rate increased from 2% to 3.5%

Investigation:
1. Which rule triggered more? Rule X
2. When did spike start? After rule update
3. Was threshold too low? Yes, reduce alert rate
4. What's actual fraud rate? Check investigated cases
5. Is user friction increasing? Survey feedback

Finding: Rule threshold too aggressive
Action: Rebalance rule weight or threshold
Result: Decline rate back to 2%, fraud control maintained
```

## Reporting & Communication

### Executive Reporting
```
Weekly Report:
- Fraud prevented ($ and # cases)
- Performance vs. targets
- Key metrics trend
- Issues/risks identified
- Recommended actions

Monthly Report:
- Comprehensive performance analysis
- Strategic metrics
- Investment justification
- Competitive analysis
- Roadmap items
```

### Investigator Reporting
```
Daily:
- Case assignments
- Priority cases
- System alerts

Weekly:
- Case productivity
- Investigation efficiency
- Training needs
- Process improvements

Monthly:
- Team performance
- Case outcomes
- Fraud pattern summary
- Operational metrics
```

## Metrics Tracking

### KPI Dashboard Updates
```
Real-time:
- Transactions per minute
- Fraud rate
- False decline rate
- Alert volume

Hourly:
- Cumulative fraud
- Detection rate by method
- Investigation capacity

Daily:
- Fraud metrics finalized
- Performance vs. targets
- Exceptions/alerts

Weekly:
- Trend analysis
- Comparative periods
- Forecasting
```

### Data Quality Monitoring
```
Track:
- Missing data percentage
- Data latency
- Data accuracy
- Alert accuracy

Alert if:
- Data quality drops
- Latency increases
- Accuracy falls
- System issues detected
```

## Best Practices

1. **Continuous Monitoring**: Real-time KPI tracking
2. **Regular Analysis**: Weekly deep dives into data
3. **A/B Testing**: Validate changes with testing
4. **Feedback Integration**: Use investigation outcomes
5. **Stakeholder Alignment**: Share insights regularly
6. **Documentation**: Record findings and decisions
7. **Automation**: Automate routine analyses
8. **Benchmarking**: Compare to industry standards
