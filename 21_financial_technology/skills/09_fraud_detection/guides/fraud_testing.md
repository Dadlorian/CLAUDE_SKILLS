# Fraud Testing Guide

## Test Categories

### Unit Testing
```python
import unittest
from fraud_detection import FraudDetector

class TestFraudDetection(unittest.TestCase):
    def setUp(self):
        self.detector = FraudDetector()

    def test_high_amount_detection(self):
        """Test detection of high-amount transactions"""
        transaction = {
            'amount': 5000,
            'customer_id': 123,
            'merchant_category': 'groceries'
        }

        score = self.detector.score(transaction)

        self.assertGreater(score, 0.5, 'High amount should flag')

    def test_velocity_detection(self):
        """Test velocity-based detection"""
        # Multiple transactions in short time
        transactions = [
            {'customer_id': 123, 'amount': 100, 'timestamp': now()},
            {'customer_id': 123, 'amount': 100, 'timestamp': now() + 2 minutes},
            {'customer_id': 123, 'amount': 100, 'timestamp': now() + 4 minutes},
            {'customer_id': 123, 'amount': 100, 'timestamp': now() + 6 minutes},
        ]

        # Score last transaction
        score = self.detector.score(transactions[-1])

        self.assertGreater(score, 0.6, 'High velocity should flag')

    def test_legitimate_transaction(self):
        """Test legitimate transaction passes"""
        transaction = {
            'amount': 50,
            'customer_id': 123,
            'merchant': 'grocery_store',
            'device_known': True,
            'location': 'home'
        }

        score = self.detector.score(transaction)

        self.assertLess(score, 0.3, 'Legitimate transaction should have low score')
```

### Integration Testing
```python
class TestFraudSystemIntegration(unittest.TestCase):
    def setUp(self):
        self.system = FraudDetectionSystem()
        self.test_db = create_test_database()

    def test_end_to_end_fraud_detection(self):
        """Test complete fraud detection flow"""
        # 1. Set up test customer
        customer = self.test_db.create_customer({
            'name': 'Test Customer',
            'account_age_days': 30
        })

        # 2. Submit suspicious transaction
        transaction = {
            'customer_id': customer['id'],
            'amount': 2000,
            'merchant': 'crypto_exchange',
            'device_new': True,
            'location': 'unknown'
        }

        # 3. Process transaction
        result = self.system.process_transaction(transaction)

        # 4. Verify alert generated
        self.assertEqual(result['action'], 'review')
        self.assertGreater(result['fraud_score'], 0.6)

        # 5. Verify alert in queue
        alerts = self.test_db.get_investigation_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['transaction_id'], transaction['id'])

    def test_fraud_ring_detection(self):
        """Test fraud ring detection"""
        # Create device used by multiple customers
        device_id = 'device_12345'

        # Create multiple customers using same device
        customer_ids = []
        for i in range(5):
            customer = self.test_db.create_customer({
                'name': f'Test Customer {i}',
                'created_at': datetime.now() - timedelta(days=1)
            })
            customer_ids.append(customer['id'])

        # All customers use same device
        for cid in customer_ids:
            transaction = {
                'customer_id': cid,
                'device_id': device_id,
                'amount': 500,
                'merchant': 'high_risk'
            }

            self.system.process_transaction(transaction)

        # Analyze network
        network_analysis = self.system.analyze_device_network(device_id)

        self.assertEqual(network_analysis['customer_count'], 5)
        self.assertEqual(network_analysis['fraud_risk'], 'high')
```

### Historical Data Testing
```python
def test_against_historical_data():
    """Test system against known fraud and legitimate cases"""
    detector = FraudDetector()

    # Load test dataset
    fraud_cases = load_fraud_cases()
    legitimate_cases = load_legitimate_cases()

    # Test fraud detection
    fraud_scores = []
    for case in fraud_cases:
        score = detector.score(case['features'])
        fraud_scores.append(score)

    fraud_rate = sum(1 for s in fraud_scores if s > 0.5) / len(fraud_scores)

    print(f'Fraud Detection Rate: {fraud_rate:.1%}')
    print(f'Average Score: {np.mean(fraud_scores):.2f}')

    # Test false positives
    legit_scores = []
    for case in legitimate_cases:
        score = detector.score(case['features'])
        legit_scores.append(score)

    fp_rate = sum(1 for s in legit_scores if s > 0.5) / len(legit_scores)

    print(f'False Positive Rate: {fp_rate:.1%}')
    print(f'Average Score: {np.mean(legit_scores):.2f}')

    # Assertions
    assert fraud_rate > 0.85, f'Fraud detection rate too low: {fraud_rate}'
    assert fp_rate < 0.02, f'False positive rate too high: {fp_rate}'
```

## Fraud Scenario Testing

### Synthetic Fraud Scenarios
```python
class FraudScenarioTests:
    def scenario_stolen_card(self):
        """Test detection of stolen card usage"""
        # Create legitimate customer baseline
        customer = create_customer()
        add_baseline_transactions(customer, amount=100, daily_count=2)

        # Now use card from different location
        fraudulent_transaction = {
            'customer_id': customer['id'],
            'amount': 2000,  # Higher than baseline
            'location': 'different_country',
            'device_new': True,
            'merchant': 'high_risk'
        }

        result = self.detector.score(fraudulent_transaction)

        self.assertGreater(result, 0.7, 'Stolen card should be detected')

    def scenario_account_takeover(self):
        """Test ATO detection"""
        customer = create_customer()

        # Legitimate baseline
        baseline_login = {
            'customer_id': customer['id'],
            'device_fingerprint': 'device_123',
            'ip_address': '192.168.1.1',
            'time': '14:00',
            'day': 'Wednesday'
        }

        # Now different device, IP, time
        takeover_login = {
            'customer_id': customer['id'],
            'device_fingerprint': 'device_999',
            'ip_address': '10.0.0.1',
            'time': '03:00',
            'day': 'Saturday'
        }

        result = self.detector.score_login(takeover_login)

        self.assertGreater(result, 0.8, 'Account takeover should be detected')

    def scenario_velocity_spike(self):
        """Test velocity spike detection"""
        customer = create_customer()

        # Add multiple transactions in 1 hour
        for i in range(10):
            transaction = {
                'customer_id': customer['id'],
                'amount': 100,
                'timestamp': datetime.now() + timedelta(minutes=i*5)
            }

            self.detector.process_transaction(transaction)

        # Score next transaction
        final_txn = {
            'customer_id': customer['id'],
            'amount': 100,
            'timestamp': datetime.now() + timedelta(minutes=50)
        }

        result = self.detector.score(final_txn)

        self.assertGreater(result, 0.7, 'Velocity spike should be detected')
```

## Performance Testing

### Latency Testing
```python
def test_scoring_latency():
    """Test that scoring meets latency targets"""
    detector = FraudDetector()

    latencies = []

    for _ in range(1000):
        transaction = generate_random_transaction()

        start = time.time()
        score = detector.score(transaction)
        latency_ms = (time.time() - start) * 1000

        latencies.append(latency_ms)

    # Calculate percentiles
    latencies.sort()

    p50 = latencies[int(len(latencies) * 0.5)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f'P50 latency: {p50:.2f}ms')
    print(f'P95 latency: {p95:.2f}ms')
    print(f'P99 latency: {p99:.2f}ms')

    # Assertions
    assert p50 < 50, f'P50 latency too high: {p50}ms'
    assert p95 < 100, f'P95 latency too high: {p95}ms'
    assert p99 < 150, f'P99 latency too high: {p99}ms'
```

### Throughput Testing
```python
def test_throughput():
    """Test transaction throughput"""
    detector = FraudDetector()

    transaction_count = 10000
    start_time = time.time()

    for i in range(transaction_count):
        transaction = generate_random_transaction()
        detector.score(transaction)

    elapsed = time.time() - start_time
    tps = transaction_count / elapsed

    print(f'Throughput: {tps:.0f} transactions/second')

    # Assert minimum throughput
    assert tps > 5000, f'Throughput too low: {tps} TPS'
```

## A/B Testing Framework

### Model Comparison
```python
class ABTestFramework:
    def compare_models(self, control_model, treatment_model, test_data):
        """Compare two models A/B test style"""
        results = {
            'control': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0},
            'treatment': {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
        }

        for transaction in test_data:
            true_label = transaction['is_fraud']

            # Score with control model
            control_score = control_model.score(transaction)
            control_prediction = control_score > 0.5

            # Score with treatment model
            treatment_score = treatment_model.score(transaction)
            treatment_prediction = treatment_score > 0.5

            # Calculate confusion matrix values
            if control_prediction and true_label:
                results['control']['tp'] += 1
            elif control_prediction and not true_label:
                results['control']['fp'] += 1
            elif not control_prediction and true_label:
                results['control']['fn'] += 1
            else:
                results['control']['tn'] += 1

            # Same for treatment
            if treatment_prediction and true_label:
                results['treatment']['tp'] += 1
            elif treatment_prediction and not true_label:
                results['treatment']['fp'] += 1
            elif not treatment_prediction and true_label:
                results['treatment']['fn'] += 1
            else:
                results['treatment']['tn'] += 1

        # Calculate metrics
        return self._calculate_metrics(results)

    def _calculate_metrics(self, results):
        """Calculate performance metrics"""
        metrics = {}

        for model_name, confusion in results.items():
            tp = confusion['tp']
            fp = confusion['fp']
            fn = confusion['fn']
            tn = confusion['tn']

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (
                precision + recall
            ) > 0 else 0

            metrics[model_name] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'confusion_matrix': confusion
            }

        return metrics
```

## Continuous Testing

### Regression Testing
```python
def regression_test():
    """Test that new changes don't break existing functionality"""
    detector = FraudDetector()

    # Load historical test cases
    test_cases = load_regression_test_cases()

    failures = []

    for case in test_cases:
        expected_score = case['expected_score']
        actual_score = detector.score(case['transaction'])

        # Allow 5% variance
        if abs(actual_score - expected_score) > 0.05:
            failures.append({
                'case_id': case['id'],
                'expected': expected_score,
                'actual': actual_score
            })

    if failures:
        print(f'Regression test failed: {len(failures)} cases')
        for failure in failures:
            print(f"  Case {failure['case_id']}: expected {failure['expected']}, got {failure['actual']}")

    assert len(failures) == 0, 'Regression test failures'
```

## Best Practices

1. **Comprehensive Coverage**: Unit + integration + end-to-end tests
2. **Historical Data**: Test against known fraud patterns
3. **Performance Monitoring**: Latency and throughput targets
4. **Scenario Testing**: Real fraud scenarios
5. **Continuous Testing**: Regular regression testing
6. **A/B Testing**: Compare improvements
7. **Documentation**: Document test purpose
8. **Automation**: Automated test execution
