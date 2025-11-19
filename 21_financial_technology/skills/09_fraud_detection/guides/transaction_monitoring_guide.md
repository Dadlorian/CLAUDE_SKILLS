# Transaction Monitoring Guide

## Real-Time Transaction Monitoring Pipeline

### Architecture
```
Transaction Input Stream
    ↓
Feature Extraction
    ↓
Real-Time Enrichment
    ├── Customer Profile
    ├── Device Information
    ├── Merchant Risk
    └── Network Relationships
    ↓
Multi-Layer Scoring
    ├── Rules Engine (10-20ms)
    ├── ML Model (30-50ms)
    ├── Behavioral (15-30ms)
    └── Network Analysis (20-50ms)
    ↓
Decision Logic
    ├── Threshold Application
    ├── Risk Adjustment
    └── Action Determination
    ↓
Output Actions
    ├── Allow
    ├── Review
    ├── Challenge (2FA)
    └── Block
    ↓
Alert & Logging
    ├── Investigation Queue
    ├── Event Logging
    └── Dashboard Updates
```

## Stream Processing Implementation

### Kafka-Based Monitoring
```python
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging

class TransactionMonitor:
    def __init__(self, kafka_brokers, topic='transactions'):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_brokers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='fraud_detection',
            auto_offset_reset='earliest',
            max_poll_records=100
        )
        self.feature_store = FeatureStore()
        self.scorer = FraudScorer()

    def start_monitoring(self):
        """Start consuming and processing transactions"""
        for message in self.consumer:
            try:
                transaction = message.value

                # Process transaction
                result = self.process_transaction(transaction)

                # Store result
                self.store_result(result)

                # Generate alerts if needed
                if result['action'] != 'allow':
                    self.generate_alert(result)

            except Exception as e:
                logging.error(f"Error processing transaction: {e}")

    def process_transaction(self, transaction):
        """Process single transaction"""
        start_time = time.time()

        # 1. Extract features (target: 20ms)
        features = self.feature_store.extract_features(transaction)

        # 2. Score transaction (target: 80ms total)
        fraud_score = self.scorer.score(features)

        # 3. Determine action (target: 10ms)
        action = self.determine_action(fraud_score)

        # 4. Add metadata
        result = {
            'transaction_id': transaction['id'],
            'fraud_score': fraud_score,
            'action': action,
            'latency_ms': (time.time() - start_time) * 1000,
            'timestamp': datetime.now().isoformat()
        }

        return result

    def determine_action(self, fraud_score):
        """Determine action based on fraud score"""
        if fraud_score < 0.3:
            return 'allow'
        elif fraud_score < 0.6:
            return 'monitor'
        elif fraud_score < 0.8:
            return 'challenge'
        else:
            return 'block'

    def store_result(self, result):
        """Store result in database"""
        # Store in transaction results table
        self.db.insert_transaction_result(result)

    def generate_alert(self, result):
        """Generate alert for investigation"""
        alert = {
            'transaction_id': result['transaction_id'],
            'fraud_score': result['fraud_score'],
            'action': result['action'],
            'priority': self.calculate_priority(result),
            'created_at': datetime.now()
        }

        # Add to investigation queue
        self.investigation_queue.put(alert)

    def calculate_priority(self, result):
        """Calculate alert priority"""
        score = result['fraud_score']

        if result['action'] == 'block':
            return 1  # Critical
        elif score > 0.7:
            return 2  # High
        elif score > 0.5:
            return 3  # Medium
        else:
            return 4  # Low
```

## Feature Enrichment at Scale

### Distributed Feature Store
```python
import redis
from functools import lru_cache

class DistributedFeatureStore:
    def __init__(self, redis_cluster):
        self.redis = redis_cluster
        self.feature_cache = {}

    def extract_features(self, transaction):
        """Extract and enrich features"""
        features = {
            # Transaction details
            'amount': transaction['amount'],
            'currency': transaction['currency'],
            'merchant_id': transaction['merchant_id'],
            'merchant_category': transaction['merchant_category'],
            'timestamp': transaction['timestamp'],

            # Customer features
            'customer_id': transaction['customer_id'],
        }

        # Enrich with cached data (parallel fetch)
        enrichments = {
            'customer': self._get_customer_features(
                transaction['customer_id']
            ),
            'device': self._get_device_features(
                transaction['device_id']
            ),
            'card': self._get_card_features(
                transaction['card_id']
            ),
            'merchant': self._get_merchant_features(
                transaction['merchant_id']
            )
        }

        # Add enrichments
        for key, values in enrichments.items():
            for k, v in values.items():
                features[f'{key}_{k}'] = v

        # Add computed features
        features.update(self._compute_velocity_features(
            transaction['customer_id']
        ))

        return features

    def _get_customer_features(self, customer_id):
        """Get customer features from cache"""
        cache_key = f'customer:{customer_id}'

        # Try cache first
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch from database
        features = self._fetch_from_db('customers', customer_id)

        # Cache for 1 hour
        self.redis.setex(
            cache_key,
            3600,
            json.dumps(features)
        )

        return features

    def _compute_velocity_features(self, customer_id):
        """Compute real-time velocity"""
        key_1h = f'velocity_1h:{customer_id}'
        key_1d = f'velocity_1d:{customer_id}'

        # Increment counters
        count_1h = self.redis.incr(key_1h)
        count_1d = self.redis.incr(key_1d)

        # Set expiration
        self.redis.expire(key_1h, 3600)
        self.redis.expire(key_1d, 86400)

        return {
            'velocity_1h': count_1h,
            'velocity_1d': count_1d
        }
```

## Contextual Risk Adjustment

### Dynamic Thresholds Based on Context
```python
class ContextualRiskAdjuster:
    def adjust_score(self, fraud_score, context):
        """Adjust fraud score based on context"""
        adjustment = 0.0

        # Customer segment adjustment
        segment = context['customer_segment']
        if segment == 'VIP':
            adjustment -= 0.1  # Lower threshold for VIP
        elif segment == 'high_risk':
            adjustment += 0.15  # Higher threshold

        # Merchant risk adjustment
        merchant_risk = context['merchant_risk']
        adjustment += merchant_risk * 0.1

        # Time-based adjustment
        hour = context['transaction_hour']
        if hour < 6 or hour > 22:
            adjustment += 0.05  # Off-hours adjustment

        # Geographic adjustment
        if context['is_high_fraud_region']:
            adjustment += 0.1

        # Apply adjustment
        adjusted_score = min(max(fraud_score + adjustment, 0.0), 1.0)

        return {
            'original_score': fraud_score,
            'adjustment': adjustment,
            'adjusted_score': adjusted_score
        }

    def get_dynamic_threshold(self, context):
        """Get threshold based on context"""
        base_threshold = 0.6

        # Vary threshold by time of day
        hour = context['transaction_hour']
        if hour < 6 or hour > 22:
            base_threshold += 0.1

        # Vary by day of week
        day_of_week = context['day_of_week']
        if day_of_week > 5:  # Weekend
            base_threshold += 0.05

        # Vary by merchant category
        if context['merchant_category'] in ['cryptocurrency', 'money_transfer']:
            base_threshold += 0.2

        # Vary by customer segment
        if context['customer_segment'] == 'new':
            base_threshold += 0.1

        return base_threshold
```

## Monitoring & Alerting

### Real-Time Metrics Tracking
```python
class MonitoringSystem:
    def __init__(self):
        self.metrics = {
            'transactions_per_minute': 0,
            'average_latency_ms': 0,
            'fraud_detection_rate': 0,
            'false_positive_rate': 0,
            'alert_volume': 0
        }

    def track_transaction(self, result):
        """Track transaction metrics"""
        # Update latency
        self.metrics['average_latency_ms'] = (
            0.9 * self.metrics['average_latency_ms'] +
            0.1 * result['latency_ms']
        )

        # Track fraud rate
        if result['action'] != 'allow':
            self.metrics['alert_volume'] += 1

    def get_health_status(self):
        """Get system health"""
        status = {}

        # Latency health
        if self.metrics['average_latency_ms'] > 150:
            status['latency'] = 'WARNING'
        else:
            status['latency'] = 'HEALTHY'

        # Throughput health
        if self.metrics['transactions_per_minute'] < 1000:
            status['throughput'] = 'WARNING'
        else:
            status['throughput'] = 'HEALTHY'

        # Alert volume health
        if self.metrics['alert_volume'] > 5000:
            status['alert_volume'] = 'WARNING'
        else:
            status['alert_volume'] = 'NORMAL'

        return status
```

## Batch Monitoring for Non-Real-Time Scenarios

### Daily Batch Processing
```python
class BatchMonitor:
    def process_daily_batch(self, date):
        """Process all transactions from a date"""
        transactions = self.load_transactions(date)

        # Batch score
        batch_results = []
        for batch in self.batch_iterator(transactions, batch_size=1000):
            results = self.batch_score_transactions(batch)
            batch_results.extend(results)

        # Generate summary report
        report = self.generate_report(batch_results)

        # Store results
        self.store_results(batch_results)

        return report

    def batch_score_transactions(self, batch):
        """Score batch of transactions"""
        features = self.extract_batch_features(batch)

        # ML model batch inference
        scores = self.ml_model.predict_batch(features)

        # Combine with rules
        results = []
        for i, (transaction, score) in enumerate(zip(batch, scores)):
            result = {
                'transaction_id': transaction['id'],
                'fraud_score': score,
                'action': self.determine_action(score)
            }
            results.append(result)

        return results

    def generate_report(self, results):
        """Generate daily monitoring report"""
        total = len(results)
        blocked = sum(1 for r in results if r['action'] == 'block')
        reviewed = sum(1 for r in results if r['action'] == 'review')

        avg_score = np.mean([r['fraud_score'] for r in results])

        return {
            'date': datetime.now().date(),
            'total_transactions': total,
            'blocked_count': blocked,
            'blocked_rate': blocked / total if total > 0 else 0,
            'reviewed_count': reviewed,
            'average_fraud_score': avg_score
        }
```

## Best Practices

1. **Latency Targets**
   - P99: < 100ms
   - P95: < 80ms
   - Average: < 50ms

2. **Throughput**
   - Target: > 10,000 TPS
   - Burst: > 20,000 TPS
   - Auto-scaling: 2-4x peak

3. **Monitoring**
   - Real-time dashboards
   - Alert on anomalies
   - Daily reports
   - Weekly reviews

4. **Optimization**
   - Feature caching
   - Model optimization
   - Batch processing
   - Load balancing

5. **Reliability**
   - Fallback to rules
   - Circuit breakers
   - Error handling
   - Disaster recovery
