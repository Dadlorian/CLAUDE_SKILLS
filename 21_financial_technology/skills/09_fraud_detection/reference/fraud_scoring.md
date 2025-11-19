# Fraud Scoring Reference

## Overview
Fraud scoring assigns a numerical risk value to transactions, enabling differentiated responses from automatic approval to manual review to blocking.

## Scoring Architecture

### Score Components
```
Overall_Fraud_Score =
  0.25 * ML_Model_Score +
  0.25 * Rules_Engine_Score +
  0.20 * Behavioral_Risk_Score +
  0.15 * Device_Risk_Score +
  0.15 * Network_Risk_Score
```

### Score Range & Interpretation
```
Score Range    Fraud Probability    Action
0.0 - 0.2      0-5% fraud risk      Auto-approve
0.2 - 0.4      5-15% fraud risk     Monitor/Log
0.4 - 0.6      15-30% fraud risk    Optional verification
0.6 - 0.8      30-50% fraud risk    Require verification
0.8 - 1.0      50-100% fraud risk   Block/Decline
```

## Scoring Methods

### Simple Averaging
```
Fraud_Score = (Score1 + Score2 + Score3 + Score4 + Score5) / 5

Equal weight to all components
```

### Weighted Averaging
```
Fraud_Score =
  0.3 * ML_Score +
  0.25 * Rules_Score +
  0.25 * Behavioral_Score +
  0.1 * Device_Score +
  0.1 * Network_Score

Weights based on component effectiveness
```

### Linear Score Combination
```
Fraud_Score = w1*f1(x) + w2*f2(x) + w3*f3(x) + ...

Where:
  w_i = component weight
  f_i(x) = component score function
  x = feature vector
```

### Non-Linear Combination
```
Fraud_Score = max(Score1, Score2, Score3)

Use maximum score to emphasize extreme risks
```

## Component Scoring

### ML Model Score
```
Probability of fraud from trained model
Output: 0.0 - 1.0
Calibration: Match predicted probability to actual fraud rate

Example:
  Raw model output: 0.45
  Calibrated score: 0.42 (matches data)
  Final score: 0.42
```

### Rules Engine Score
```
Weighted sum of triggered rules

Example:
  Rule 1 (velocity): weight 0.3, triggered = 1.0 -> 0.3
  Rule 2 (amount): weight 0.2, triggered = 0.5 -> 0.1
  Rule 3 (device): weight 0.2, not triggered = 0.0 -> 0.0
  Rule 4 (merchant): weight 0.3, triggered = 1.0 -> 0.3

  Total Rules Score = 0.3 + 0.1 + 0.0 + 0.3 = 0.7
```

### Behavioral Risk Score
```
User deviation from baseline

Calculation:
  Deviation = |Current_Behavior - Baseline| / Baseline_Std_Dev
  Score = min(Deviation / 3.0, 1.0)  # Normalize to 0-1

Example:
  Typing speed baseline: 45 WPM ± 8
  Current typing: 20 WPM
  Deviation = (45-20)/8 = 3.125 std devs
  Score = min(3.125/3, 1.0) = 1.0 (very anomalous)
```

### Device Risk Score
```
Device reputation and history

Components:
  Device Age: 0.1 * (days_since_first_seen / 365)
  Device History: 0.4 * (confirmed_fraud_count / total_transactions)
  Device Velocity: 0.3 * min(transactions_today / avg_daily, 1.0)
  Device Spread: 0.2 * (unique_customers_count / total_uses)

Score = sum of weighted components
```

### Network Risk Score
```
Graph-based fraud ring detection

Components:
  Card Network Risk: 0.3 * (risk_of_connected_cards)
  Customer Network Risk: 0.3 * (risk_of_customers_same_device)
  Device Network Risk: 0.2 * (fraud_ring_proximity)
  Merchant Network Risk: 0.2 * (high_risk_merchant_cluster)

Score = max(component scores) or weighted average
```

## Score Normalization

### Min-Max Normalization
```
Normalized_Score = (Score - Min) / (Max - Min)

Range: 0.0 - 1.0
Linear transformation
```

### Z-Score Normalization
```
Normalized_Score = (Score - Mean) / Std_Dev

Then clip to 0-1: min(max(z, 0), 1)
Handles outliers well
```

### Sigmoid Normalization
```
Normalized_Score = 1 / (1 + e^(-Score))

Smooth 0-1 mapping
Values near 0 stay low, near 1 stay high
Emphasizes mid-range distinction
```

## Contextual Score Adjustment

### Customer Segment Adjustment
```
VIP Customer: Reduce score by 0.1
  If base_score = 0.6, adjusted = 0.5

High-Risk Customer: Increase score by 0.15
  If base_score = 0.4, adjusted = 0.55

New Customer: Increase score by 0.05
  If base_score = 0.3, adjusted = 0.35
```

### Merchant Risk Adjustment
```
High-Risk Merchant (gambling): +0.1 to score
Medium-Risk Merchant (travel): +0.05 to score
Low-Risk Merchant (groceries): No adjustment

Base score = 0.3
Against high-risk merchant = 0.4
```

### Geographic Risk Adjustment
```
Domestic transaction: No adjustment
Different country: +0.05 to score
High-fraud region: +0.1 to score
Sanctioned country: +0.3 to score

Score capped at 1.0
```

### Temporal Adjustment
```
Business hours (9-5 M-F): No adjustment
Evening hours (5-11 PM): +0.05 to score
Night hours (11 PM-6 AM): +0.1 to score
Weekend: +0.05 to score
Holiday: +0.1 to score

Cumulative adjustments possible
```

## Score Thresholding

### Fixed Thresholds
```
Score < 0.3: AUTO-APPROVE
Score 0.3-0.5: MONITOR
Score 0.5-0.7: CHALLENGE (optional 2FA)
Score 0.7-0.85: BLOCK & REVIEW
Score >= 0.85: AUTO-BLOCK
```

### Dynamic Thresholds
```
Based on daily fraud rate:
  If fraud_rate < 0.5%:
    Aggressive thresholds (lower block threshold)
  If fraud_rate > 2%:
    Conservative thresholds (higher block threshold)

Daily adjustment of decision boundaries
```

### Percentile-Based Thresholds
```
Bottom 90%: AUTO-APPROVE
90-95%: MONITOR
95-98%: CHALLENGE
98-99%: BLOCK & REVIEW
Top 1%: AUTO-BLOCK

Dynamic based on actual score distribution
```

## Real-Time Score Caching

### Score Validity Period
```
Transaction Score: Valid for 5 minutes
  Scores expire due to changing context

Customer Baseline: Valid for 24 hours
  Behavior baseline changes daily

Device Risk: Valid for 24 hours
  Device risk scores updated daily

Rules Score: Valid for 1 minute
  Dynamic rules may change frequently
```

### Cache Key Structure
```
Cache Key = {transaction_id}_{timestamp}_{version}

Example: txn_12345_20231119130245_v2

Enables:
  - Version tracking
  - Replay analysis
  - Audit trails
```

## Score Explanation

### Feature Importance Ranking
```
Top 5 Features Contributing to Fraud Score:

1. Transaction Velocity (score impact: +0.25)
   - 6 transactions in 1 hour (normal: 1-2)

2. Geographic Impossibility (score impact: +0.15)
   - Transaction 1000 miles from previous in 30 mins

3. New Device (score impact: +0.12)
   - Device never used by customer before

4. High Amount (score impact: +0.08)
   - $2500 vs. typical $150 average

5. Merchant Risk (score impact: +0.05)
   - High-risk merchant category (crypto)
```

### Decision Explanation
```
Fraud Score: 0.72 (HIGH RISK)
Decision: REQUIRE VERIFICATION

Contributing Factors:
  + High transaction velocity (4 txns in 1hr)
  + Device not previously used
  + Late night transaction (11:45 PM)
  - Merchant is trusted (Amazon)
  - Amount reasonable for customer

Recommendation: Require OTP verification
```

## Score Monitoring & Calibration

### Score Distribution Monitoring
```
Daily Monitoring:
  - % of transactions in each score band
  - Mean score trend
  - Distribution changes

Alert if:
  - Mean score increases >20% daily
  - Score distribution skew changes
  - Score variance increases
```

### Score Calibration
```
Measure actual fraud rate at each score band:
  Score 0.0-0.2: Actual fraud rate = 1%
  Score 0.2-0.4: Actual fraud rate = 5%
  Score 0.4-0.6: Actual fraud rate = 15%
  Score 0.6-0.8: Actual fraud rate = 35%
  Score 0.8-1.0: Actual fraud rate = 65%

If calibration off:
  - Retrain models
  - Adjust weights
  - Update thresholds
```

### A/B Testing Score Changes
```
Control: Current scoring formula
Treatment: New scoring formula

Measure over 1 week:
  - Fraud detection rate
  - False positive rate
  - Customer acceptance
  - Overall impact

Rollout if positive
```

## Score Analytics

### Score by Dimension
```
Score breakdown by:
  - Customer segment
  - Merchant category
  - Geographic region
  - Device type
  - Time of day
  - Transaction amount
  - Account age
```

### Score Performance Metrics
```
For score band 0.5-0.7:
  - Transactions: 5,234
  - Fraud count: 523
  - Fraud rate: 10%
  - False positive rate: 8%
  - Precision: 0.55
  - Recall: 0.25
  - F1-score: 0.34
```

## Best Practices

1. **Simplicity**: Start with 2-3 weighted components
2. **Transparency**: Explain scores to customers
3. **Calibration**: Regularly measure actual fraud rates
4. **Monitoring**: Track score distribution daily
5. **Testing**: A/B test changes before rollout
6. **Documentation**: Record all scoring decisions
7. **Auditing**: Maintain audit trail of scores
8. **Feedback**: Use investigator feedback to improve
