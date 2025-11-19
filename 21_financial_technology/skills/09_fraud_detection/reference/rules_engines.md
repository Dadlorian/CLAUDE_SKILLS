# Rules Engines Reference

## Overview
Rules engines provide fast, interpretable fraud detection through declarative business rules. Enable rapid rule updates without model retraining.

## Rule Engine Architecture

### Components

#### Rule Engine Core
- **Rule parser**: Parse rule definitions
- **Rule evaluator**: Execute rules against data
- **Decision engine**: Combine rule results
- **Action engine**: Generate outputs/alerts

#### Data Flow
```
Input Transaction ->
Feature Extraction ->
Rule Evaluation ->
Decision Making ->
Score/Alert Generation ->
Output (Block/Review/Allow)
```

### Rule Storage & Management
- Rule repository (database, JSON, YAML)
- Rule versioning
- Rule enable/disable toggles
- Rule testing and validation
- Rule deployment pipelines

## Rule Types

### Simple Rules
```
IF amount > 5000 THEN risk = HIGH

IF (amount > 3000 AND first_transaction) THEN risk = MEDIUM

IF is_weekend AND is_night AND amount > 1000 THEN review = TRUE
```

### Conditional Rules
```
IF amount > customer_avg_transaction * 5 THEN
  IF merchant_type IN ['money_transfer', 'gambling'] THEN
    risk = HIGH
  ELSE
    risk = MEDIUM
  ENDIF
ENDIF
```

### Time-Based Rules
```
IF (transactions_in_1hour > 5) AND (amount > 100) THEN
  velocity_risk = HIGH
ENDIF

IF transaction_count_today > 20 THEN
  daily_velocity_risk = MEDIUM
ENDIF
```

### Geographic Rules
```
IF distance_from_last_transaction_miles > 1000 THEN
  travel_time_min = distance_miles / 400
  IF time_since_last_transaction_mins < travel_time_min THEN
    geographic_risk = HIGH
  ENDIF
ENDIF

IF country NOT IN customer_allowed_countries THEN
  region_risk = HIGH
ENDIF
```

### Device Rules
```
IF device_new_to_customer THEN
  device_risk = MEDIUM
ENDIF

IF device_count > 5 THEN
  device_risk = MEDIUM
ENDIF

IF device_flagged_fraud_count > 0 THEN
  device_risk = HIGH
ENDIF
```

### Network Rules
```
IF card_used_by_multiple_customers > 2 THEN
  network_risk = HIGH
ENDIF

IF device_connected_to_fraud_ring THEN
  network_risk = CRITICAL
ENDIF
```

### Merchant Rules
```
IF merchant_high_risk_category THEN
  merchant_risk = MEDIUM
ENDIF

IF merchant_chargeback_rate > 0.05 THEN
  merchant_risk = HIGH
ENDIF

IF merchant_new_to_platform THEN
  merchant_risk = MEDIUM
ENDIF
```

## Rule Composition

### AND Logic
```
IF (amount > 1000) AND
   (merchant_type = 'cryptocurrency') AND
   (is_new_account)
THEN risk = HIGH
```

**All conditions must be true**

### OR Logic
```
IF (amount > 5000) OR
   (geographic_impossible) OR
   (velocity_spike)
THEN review = TRUE
```

**Any condition triggers**

### Nested Conditions
```
IF (is_new_account) THEN
  IF amount > 500 THEN
    risk = MEDIUM
  ELSE IF amount > 1000 THEN
    risk = HIGH
  ENDIF
ELSE
  IF amount > 2000 THEN
    risk = MEDIUM
  ENDIF
ENDIF
```

### Rule Groups & Priorities
```
Group 1 (CRITICAL):
  - Geographic impossibility
  - Fraud ring involvement

Group 2 (HIGH):
  - New account + high velocity
  - Multiple risk factors

Group 3 (MEDIUM):
  - Single risk indicator
  - Merchant category concerns
```

## Rule Scoring

### Binary Scoring
```
IF rule_triggered THEN risk = 1
ELSE risk = 0
```

### Multi-Level Scoring
```
Risk Levels: LOW=0, MEDIUM=0.5, HIGH=1.0

IF amount > 5000 THEN risk = HIGH (1.0)
ELSE IF amount > 2000 THEN risk = MEDIUM (0.5)
ELSE risk = LOW (0.0)
```

### Weighted Scoring
```
Total_Risk =
  0.3 * amount_risk +
  0.2 * velocity_risk +
  0.2 * geographic_risk +
  0.15 * device_risk +
  0.15 * merchant_risk

Normalized to 0-1 scale
```

### Cumulative Scoring
```
IF rule_1 THEN score += 0.2
IF rule_2 THEN score += 0.3
IF rule_3 THEN score += 0.25

IF score > 0.7 THEN action = REVIEW
```

## Rule Management Lifecycle

### Rule Creation
1. **Business requirement definition**
   - Fraud pattern identification
   - Rule success criteria
   - Expected impact

2. **Rule development & testing**
   - Draft rule definition
   - Test against historical data
   - Validate precision/recall

3. **Rule validation**
   - A/B testing
   - Fraud investigator review
   - False positive assessment

4. **Deployment**
   - Schedule activation
   - Monitoring setup
   - Fallback plan

### Rule Monitoring
```
Daily Metrics:
  - Times triggered
  - Transactions caught
  - True positive rate
  - False positive rate
  - Coverage percentage
  - Average score assigned
```

### Rule Maintenance
- Performance tracking
- False positive investigation
- Threshold adjustment
- Rule refinement
- Seasonal adjustments
- Rule deprecation

## Rule Definition Languages

### JSON Format
```json
{
  "rule_id": "velocity_spike_001",
  "name": "High transaction velocity",
  "priority": 8,
  "conditions": [
    {
      "field": "transactions_in_1hour",
      "operator": ">",
      "value": 5
    },
    {
      "field": "amount",
      "operator": ">",
      "value": 100
    }
  ],
  "operator": "AND",
  "action": "risk = HIGH",
  "enabled": true
}
```

### DSL Format
```
rule velocity_spike_001:
  when:
    - transactions_in_1hour > 5
    - amount > 100
  then:
    risk = HIGH
  priority: 8
  enabled: true
```

### SQL-like Format
```sql
SELECT transaction_id, customer_id, 'velocity_spike' as rule_name
FROM transactions
WHERE customer_id IN (
  SELECT customer_id
  FROM transactions
  WHERE timestamp > NOW() - INTERVAL '1 hour'
  GROUP BY customer_id
  HAVING COUNT(*) > 5
)
AND amount > 100
```

## Rule Testing & Validation

### Unit Testing
```
Test Rule: amount > 5000
  Input: transaction with amount = 6000
  Expected: rule triggers (true)
  Result: PASS
```

### Integration Testing
```
Scenario: New account, high velocity, high amount
Rule Set: velocity + amount + new account
Expected: Multiple rules trigger, combined score = HIGH
Result: Validate weighted scoring
```

### Historical Data Testing
```
Run rules against:
  - 100 known fraud transactions
  - 1000 legitimate transactions

Measure:
  - True positive rate
  - False positive rate
  - Precision, recall, F1-score
```

### Performance Testing
```
Latency: < 10ms per rule evaluation
Throughput: 10,000 transactions/second
Memory: < 100MB rule engine
```

## Rule Optimization

### Rule Performance
- Remove redundant rules
- Simplify complex conditions
- Order rules by cost/frequency
- Cache computed values

### Threshold Tuning
```
Current: amount > 5000
Data Analysis:
  - Fraud rate at 5000: 2%
  - Fraud rate at 4000: 3%
  - Decision: Lower to 4500 for better coverage
```

### Feature Importance
- Track which rules most effective
- Combine weak rules
- Remove low-impact rules
- Focus on high-value rules

## Advantages & Disadvantages

### Advantages
- Fast execution (milliseconds)
- Explainable decisions
- Easy to maintain and update
- No training data required
- Deterministic behavior
- Easy rule versioning

### Disadvantages
- Manual rule creation required
- Difficult for complex patterns
- High false positive rates
- Labor-intensive maintenance
- Brittle to fraud evolution
- Limited by human insight

## Hybrid Approach

```
Layer 1 (Rules): Fast blocklist/velocity checks
  ↓
Layer 2 (ML Model): Complex pattern detection
  ↓
Layer 3 (Behavioral): User deviation
  ↓
Combine scores: Final risk decision
```

## Rule Engine Tools

**Open Source**
- Drools (Java)
- Rete
- Jess

**Commercial**
- Experian Fraud Manager
- FICO Card Network Manager
- SAS Fraud Manager
- Kount Intelligence

## Best Practices

1. **Keep rules simple**: Single responsibility
2. **Document rules**: Business rationale
3. **Version control**: Track rule changes
4. **Test thoroughly**: Unit + integration tests
5. **Monitor performance**: Track metrics
6. **Regular review**: Update based on data
7. **Audit trail**: Log all rule changes
8. **A/B testing**: Validate effectiveness
