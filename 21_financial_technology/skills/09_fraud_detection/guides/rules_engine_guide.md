# Rules Engine Guide

## Rules Engine Architecture

### Components
```
Rule Definition (YAML/JSON)
        ↓
Rule Parser (Parse rules)
        ↓
Feature Evaluator (Evaluate conditions)
        ↓
Decision Engine (Combine results)
        ↓
Action Engine (Generate output)
```

## Rule Definition Format

### YAML Format
```yaml
rules:
  - id: high_amount_001
    name: High Transaction Amount
    enabled: true
    priority: 8
    conditions:
      - field: amount
        operator: gt
        value: 5000
    action: score = HIGH
    tags: [amount, new_account]

  - id: velocity_spike_001
    name: Transaction Velocity Spike
    enabled: true
    priority: 7
    conditions:
      - field: transactions_1h
        operator: gt
        value: 5
      - field: amount
        operator: gt
        value: 100
    operator: AND
    action: score = MEDIUM
    tags: [velocity]

  - id: geographic_impossible
    name: Geographic Impossibility
    enabled: true
    priority: 9
    conditions:
      - field: time_since_last_txn_minutes
        operator: lt
        value: 120
      - field: distance_miles
        operator: gt
        value: 1000
    operator: AND
    action: score = CRITICAL
    tags: [geography]
```

### JSON Format
```json
{
  "rules": [
    {
      "id": "new_device_001",
      "name": "New Device Usage",
      "enabled": true,
      "priority": 5,
      "conditions": [
        {
          "field": "device_days_old",
          "operator": "lt",
          "value": 1
        }
      ],
      "action": "score = MEDIUM",
      "tags": ["device"]
    }
  ]
}
```

## Operators & Conditions

### Comparison Operators
```
gt: Greater than >
gte: Greater than or equal >=
lt: Less than <
lte: Less than or equal <=
eq: Equal ==
neq: Not equal !=
in: Value in list
nin: Value not in list
```

### String Operators
```
contains: String contains substring
not_contains: String doesn't contain
starts_with: String starts with
ends_with: String ends with
regex: Regex pattern match
```

### Logical Operators
```
AND: All conditions must be true
OR: Any condition must be true
NOT: Negation
```

## Rule Implementation

### Python Rules Engine
```python
import json
import re
from datetime import datetime

class Rule:
    def __init__(self, rule_dict):
        self.id = rule_dict['id']
        self.name = rule_dict['name']
        self.enabled = rule_dict['enabled']
        self.priority = rule_dict['priority']
        self.conditions = rule_dict['conditions']
        self.operator = rule_dict.get('operator', 'AND')
        self.action = rule_dict['action']

    def evaluate(self, features):
        """Evaluate rule against features"""
        if not self.enabled:
            return None

        results = []
        for condition in self.conditions:
            result = self._evaluate_condition(condition, features)
            results.append(result)

        # Combine results
        if self.operator == 'AND':
            triggered = all(results)
        elif self.operator == 'OR':
            triggered = any(results)
        else:
            triggered = all(results)

        return triggered

    def _evaluate_condition(self, condition, features):
        """Evaluate single condition"""
        field = condition['field']
        operator = condition['operator']
        value = condition['value']

        if field not in features:
            return False

        feature_value = features[field]

        # Numerical operators
        if operator == 'gt':
            return feature_value > value
        elif operator == 'gte':
            return feature_value >= value
        elif operator == 'lt':
            return feature_value < value
        elif operator == 'lte':
            return feature_value <= value
        elif operator == 'eq':
            return feature_value == value
        elif operator == 'neq':
            return feature_value != value

        # List operators
        elif operator == 'in':
            return feature_value in value
        elif operator == 'nin':
            return feature_value not in value

        # String operators
        elif operator == 'contains':
            return value.lower() in str(feature_value).lower()
        elif operator == 'not_contains':
            return value.lower() not in str(feature_value).lower()
        elif operator == 'starts_with':
            return str(feature_value).startswith(str(value))
        elif operator == 'regex':
            return bool(re.search(value, str(feature_value)))

        return False

class RulesEngine:
    def __init__(self, rules_path):
        self.rules = []
        self.load_rules(rules_path)

    def load_rules(self, rules_path):
        """Load rules from JSON/YAML file"""
        with open(rules_path, 'r') as f:
            rules_data = json.load(f)

        for rule_dict in rules_data['rules']:
            rule = Rule(rule_dict)
            self.rules.append(rule)

        # Sort by priority (descending)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def evaluate_transaction(self, features):
        """Evaluate all rules for transaction"""
        triggered_rules = []
        score = 0.0

        for rule in self.rules:
            triggered = rule.evaluate(features)
            if triggered:
                triggered_rules.append({
                    'id': rule.id,
                    'name': rule.name,
                    'priority': rule.priority,
                    'action': rule.action
                })

        # Calculate score from triggered rules
        score = self._calculate_score_from_rules(triggered_rules)

        return {
            'score': score,
            'triggered_rules': triggered_rules,
            'rule_count': len(triggered_rules)
        }

    def _calculate_score_from_rules(self, triggered_rules):
        """Calculate combined score"""
        if not triggered_rules:
            return 0.0

        # Weight by priority
        total_score = 0.0
        max_score = 0.0

        for rule in triggered_rules:
            priority = rule['priority']
            weight = priority / 10.0  # Normalize to 0-1

            total_score += weight
            max_score += 1.0

        # Return normalized score (0-1)
        return min(total_score / max_score, 1.0)

# Usage
engine = RulesEngine('rules.json')
features = {
    'amount': 6000,
    'transactions_1h': 3,
    'device_days_old': 0.5,
    'distance_miles': 1500,
    'time_since_last_txn_minutes': 45
}

result = engine.evaluate_transaction(features)
print(f"Score: {result['score']:.2f}")
print(f"Triggered Rules: {len(result['triggered_rules'])}")
for rule in result['triggered_rules']:
    print(f"  - {rule['name']} (priority: {rule['priority']})")
```

## Rule Testing

### Unit Testing
```python
import unittest

class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RulesEngine('rules.json')

    def test_high_amount_rule(self):
        """Test high amount rule triggers correctly"""
        features = {'amount': 6000}
        result = self.engine.evaluate_transaction(features)

        # Should have triggered rules
        self.assertGreater(result['rule_count'], 0)

        # Should have high amount rule
        rule_ids = [r['id'] for r in result['triggered_rules']]
        self.assertIn('high_amount_001', rule_ids)

    def test_velocity_rule(self):
        """Test velocity rule"""
        features = {
            'transactions_1h': 6,
            'amount': 150
        }
        result = self.engine.evaluate_transaction(features)
        self.assertGreater(result['rule_count'], 0)

    def test_no_false_positives(self):
        """Test no rules trigger for legitimate transaction"""
        features = {
            'amount': 50,
            'transactions_1h': 1,
            'device_days_old': 30,
            'distance_miles': 5,
            'time_since_last_txn_minutes': 1440
        }
        result = self.engine.evaluate_transaction(features)
        self.assertEqual(result['rule_count'], 0)
        self.assertEqual(result['score'], 0.0)
```

### Integration Testing
```python
def test_against_historical_data():
    """Test rules against known fraud and legitimate cases"""
    engine = RulesEngine('rules.json')

    # Load historical transactions
    fraud_cases = load_labeled_fraud_cases()
    legitimate_cases = load_labeled_legitimate_cases()

    # Test fraud detection
    fraud_detected = 0
    for case in fraud_cases:
        result = engine.evaluate_transaction(case['features'])
        if result['score'] > 0.5:
            fraud_detected += 1

    fraud_rate = fraud_detected / len(fraud_cases)
    print(f"Fraud Detection Rate: {fraud_rate:.1%}")

    # Test false positives
    false_positives = 0
    for case in legitimate_cases:
        result = engine.evaluate_transaction(case['features'])
        if result['score'] > 0.5:
            false_positives += 1

    fp_rate = false_positives / len(legitimate_cases)
    print(f"False Positive Rate: {fp_rate:.1%}")

    # Verify acceptable performance
    assert fraud_rate > 0.85, "Fraud detection rate too low"
    assert fp_rate < 0.02, "False positive rate too high"
```

## Rule Management

### Version Control
```
rules/
├── v1.0/
│   └── rules.json (2024-01-01)
├── v1.1/
│   └── rules.json (2024-02-01)
├── v1.2/
│   └── rules.json (2024-03-01)
└── active -> v1.2

Changes tracked:
- New rules added
- Rules modified
- Rules disabled
- Rule parameters adjusted
- Reason for change
- Approval tracking
```

### Deployment Process
```
1. Draft Rules
   - Define new rules
   - Test in sandbox
   - Review with stakeholders

2. Testing
   - Unit tests
   - Integration tests
   - Historical data validation
   - A/B test design

3. Review & Approval
   - Technical review
   - Business review
   - Compliance check
   - Sign-off

4. Deployment
   - Deploy to staging
   - Validate rules loaded
   - Monitor for 24 hours

5. Rollout
   - Gradual rollout (10% -> 100%)
   - Monitor key metrics
   - Fallback plan ready

6. Monitoring
   - Daily performance tracking
   - Alert on anomalies
   - Weekly review
```

## Rule Optimization

### Performance Tuning
```
Order rules by:
1. Execution time (fastest first)
2. Frequency (most common first)
3. Priority (highest first)

Example Ordering:
1. Amount check (10ms)
2. Device check (5ms)
3. Velocity check (15ms)
4. Network check (30ms)

Skip expensive checks if early rules trigger
```

### Threshold Optimization
```python
def find_optimal_threshold():
    """Find threshold maximizing F1-score"""
    thresholds = np.linspace(0, 1, 100)
    best_threshold = 0.5
    best_f1 = 0.0

    for threshold in thresholds:
        # Test against historical data
        tp, fp, fn, tn = 0, 0, 0, 0

        for case in all_cases:
            result = engine.evaluate_transaction(case['features'])
            predicted = result['score'] > threshold
            actual = case['is_fraud']

            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1

        # Calculate F1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

    return best_threshold, best_f1
```

## Rule Monitoring

### Performance Tracking
```python
class RuleMonitor:
    def __init__(self):
        self.rule_stats = {}

    def record_rule_trigger(self, rule_id, transaction_is_fraud):
        """Record rule trigger and actual outcome"""
        if rule_id not in self.rule_stats:
            self.rule_stats[rule_id] = {
                'triggers': 0,
                'fraud': 0,
                'legitimate': 0
            }

        self.rule_stats[rule_id]['triggers'] += 1

        if transaction_is_fraud:
            self.rule_stats[rule_id]['fraud'] += 1
        else:
            self.rule_stats[rule_id]['legitimate'] += 1

    def get_rule_effectiveness(self):
        """Calculate precision for each rule"""
        effectiveness = {}

        for rule_id, stats in self.rule_stats.items():
            if stats['triggers'] > 0:
                precision = stats['fraud'] / stats['triggers']
                effectiveness[rule_id] = {
                    'precision': precision,
                    'triggers': stats['triggers'],
                    'fraud_caught': stats['fraud']
                }

        return effectiveness

# Usage
monitor = RuleMonitor()

for transaction in daily_transactions:
    result = engine.evaluate_transaction(transaction['features'])

    for rule in result['triggered_rules']:
        monitor.record_rule_trigger(
            rule['id'],
            transaction['is_fraud']
        )

# Print effectiveness
effectiveness = monitor.get_rule_effectiveness()
for rule_id, stats in sorted(
    effectiveness.items(),
    key=lambda x: x[1]['precision'],
    reverse=True
):
    print(f"{rule_id}: {stats['precision']:.1%} precision ({stats['triggers']} triggers)")
```

## Best Practices

1. **Keep Rules Simple**: Single purpose per rule
2. **Document Rules**: Clear business rationale
3. **Version Control**: Track all changes
4. **Test Thoroughly**: Unit + integration tests
5. **Monitor Performance**: Track effectiveness
6. **Regular Review**: Update based on data
7. **A/B Testing**: Validate before deployment
8. **Gradual Rollout**: Minimize impact
9. **Fallback Plans**: Have alternative rules
10. **Feedback Loop**: Incorporate investigation outcomes
