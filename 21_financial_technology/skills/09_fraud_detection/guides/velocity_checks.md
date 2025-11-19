# Velocity Checks Guide

## Overview
Velocity checks detect fraudulent activity by monitoring transaction frequency, amounts, and patterns over time periods.

## Types of Velocity Checks

### Transaction Count Velocity
```
Check: Number of transactions in time period

Time Windows:
- Per minute: < 10 transactions
- Per hour: < 100 transactions
- Per day: < 1000 transactions
- Per week: < 5000 transactions

Implementation:
```python
class TransactionVelocity:
    def __init__(self, redis_client):
        self.redis = redis_client

    def check_transaction_count(self, customer_id, time_window='1h'):
        """Check transaction count in time window"""
        key = f'txn_count_{time_window}:{customer_id}'

        # Increment counter
        count = self.redis.incr(key)

        # Set expiration if first increment
        if count == 1:
            if time_window == '1m':
                self.redis.expire(key, 60)
            elif time_window == '1h':
                self.redis.expire(key, 3600)
            elif time_window == '1d':
                self.redis.expire(key, 86400)

        return count

    def is_velocity_exceeded(self, customer_id):
        """Check if transaction velocity exceeded"""
        count_1h = self.check_transaction_count(customer_id, '1h')
        count_1d = self.check_transaction_count(customer_id, '1d')

        # Thresholds
        if count_1h > 50:
            return True, 'exceeded_hourly_limit'
        elif count_1d > 500:
            return True, 'exceeded_daily_limit'

        return False, 'normal'
```

### Amount Velocity
```
Check: Total transaction amount in time period

Thresholds (Configurable):
- Per hour: < $5,000
- Per day: < $20,000
- Per week: < $100,000

Implementation:
```python
def check_amount_velocity(self, customer_id, amount, time_window='1d'):
    """Check total amount in time window"""
    key = f'amt_velocity_{time_window}:{customer_id}'

    # Get current total
    current = float(self.redis.get(key) or 0)

    # Check if would exceed limit
    new_total = current + amount
    daily_limit = 20000

    if time_window == '1d' and new_total > daily_limit:
        return False, f'Daily limit of {daily_limit} exceeded'

    # Update counter
    self.redis.incrbyfloat(key, amount)
    self.redis.expire(key, 86400 if time_window == '1d' else 3600)

    return True, f'Amount OK (total: {new_total:.2f})'
```

### Merchant Velocity
```
Check: Number of transactions with same merchant in time period

Threshold: <= 3 transactions per merchant per hour

Implementation:
```python
def check_merchant_velocity(self, customer_id, merchant_id):
    """Check transaction frequency with same merchant"""
    key = f'merchant_velocity:{customer_id}:{merchant_id}'

    count = self.redis.incr(key)
    self.redis.expire(key, 3600)  # Reset every hour

    if count > 3:
        return False, 'Merchant velocity exceeded'

    return True, 'Normal'
```

### Card Velocity
```
Check: Number of different customers using same card in time period

Threshold: <= 5 transactions per card per hour from different customers

Purpose: Detect stolen card usage
```

## Dynamic Velocity Thresholds

### Customer Segment Thresholds
```python
class DynamicVelocityThresholds:
    def __init__(self):
        self.thresholds = {
            'new_customer': {
                'txn_per_hour': 5,
                'amount_per_day': 500,
                'merchants_per_hour': 2
            },
            'standard_customer': {
                'txn_per_hour': 20,
                'amount_per_day': 5000,
                'merchants_per_hour': 5
            },
            'vip_customer': {
                'txn_per_hour': 50,
                'amount_per_day': 50000,
                'merchants_per_hour': 20
            },
            'high_risk_customer': {
                'txn_per_hour': 3,
                'amount_per_day': 200,
                'merchants_per_hour': 1
            }
        }

    def get_thresholds(self, customer):
        """Get thresholds for customer"""
        segment = self._classify_customer(customer)
        return self.thresholds[segment]

    def _classify_customer(self, customer):
        """Classify customer to get thresholds"""
        if customer['account_age_days'] < 7:
            return 'new_customer'
        elif customer['fraud_flag']:
            return 'high_risk_customer'
        elif customer['vip']:
            return 'vip_customer'
        else:
            return 'standard_customer'
```

### Time-Based Adjustments
```python
def adjust_velocity_threshold(self, base_threshold, context):
    """Adjust threshold based on time of day"""
    hour = context['hour_of_day']
    day = context['day_of_week']

    adjustment = 1.0

    # Weekend relaxation
    if day > 5:  # Saturday, Sunday
        adjustment *= 1.2

    # Time-of-day adjustment
    if hour < 6 or hour > 22:
        # Off-hours - more strict
        adjustment *= 0.8

    return int(base_threshold * adjustment)
```

## Implementing Velocity Engine

### Redis-Based Velocity Tracking
```python
class VelocityEngine:
    def __init__(self, redis_cluster):
        self.redis = redis_cluster
        self.thresholds = DynamicVelocityThresholds()

    def check_all_velocities(self, transaction):
        """Check all velocity metrics"""
        violations = []

        customer_id = transaction['customer_id']
        customer = self.get_customer(customer_id)
        thresholds = self.thresholds.get_thresholds(customer)

        # Transaction count velocity
        if not self.check_txn_count_velocity(customer_id, thresholds):
            violations.append('transaction_count_velocity')

        # Amount velocity
        if not self.check_amount_velocity(
            customer_id,
            transaction['amount'],
            thresholds
        ):
            violations.append('amount_velocity')

        # Merchant velocity
        if not self.check_merchant_velocity(
            customer_id,
            transaction['merchant_id'],
            thresholds
        ):
            violations.append('merchant_velocity')

        # Card velocity
        if not self.check_card_velocity(
            transaction['card_id'],
            customer_id
        ):
            violations.append('card_velocity')

        # Device velocity
        if not self.check_device_velocity(
            transaction['device_id'],
            customer_id
        ):
            violations.append('device_velocity')

        return {
            'has_violations': len(violations) > 0,
            'violations': violations,
            'violation_count': len(violations)
        }

    def check_txn_count_velocity(self, customer_id, thresholds):
        """Check transaction count"""
        key = f'velocity_txn_count_1h:{customer_id}'
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)

        limit = thresholds['txn_per_hour']
        return count <= limit

    def check_amount_velocity(self, customer_id, amount, thresholds):
        """Check amount velocity"""
        key = f'velocity_amount_1d:{customer_id}'
        current = float(self.redis.get(key) or 0)

        new_total = current + amount
        limit = thresholds['amount_per_day']

        if new_total > limit:
            return False

        self.redis.incrbyfloat(key, amount)
        self.redis.expire(key, 86400)

        return True

    def check_merchant_velocity(self, customer_id, merchant_id, thresholds):
        """Check merchant velocity"""
        key = f'velocity_merchant_1h:{customer_id}:{merchant_id}'
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)

        limit = thresholds['merchants_per_hour']
        return count <= limit

    def check_card_velocity(self, card_id, customer_id):
        """Check card used by different customers"""
        key = f'card_customer_1h:{card_id}'

        customers = self.redis.scard(key)
        self.redis.sadd(key, customer_id)
        self.redis.expire(key, 3600)

        # Threshold: <= 5 different customers per hour
        return customers <= 5

    def check_device_velocity(self, device_id, customer_id):
        """Check device used by different customers"""
        key = f'device_customer_1h:{device_id}'

        customers = self.redis.scard(key)
        self.redis.sadd(key, customer_id)
        self.redis.expire(key, 3600)

        # Threshold: <= 10 different customers per hour
        return customers <= 10
```

## Soft Limits vs Hard Blocks

### Soft Limit Response
```
When soft limit exceeded:
- Log alert (not blocking)
- Add risk score (+0.2)
- Monitor next transaction
- Prepare for potential block

Example Soft Limits:
- Transaction count: 80% of limit triggers
- Amount: 75% of limit triggers
```

### Hard Block Response
```
When hard limit exceeded:
- Block transaction immediately
- Alert investigator
- Lock account temporarily
- Contact customer

Example Hard Limits:
- Transaction count: > 100% of limit
- Amount: > 120% of limit
- Card velocity: > 10 transactions/hour
```

## Whitelist & Exceptions

### Whitelisting High-Volume Customers
```python
def can_skip_velocity_checks(self, customer_id):
    """Check if customer is whitelisted"""
    # Check whitelist
    whitelist = self.get_whitelist()

    if customer_id in whitelist:
        # Get whitelist config
        config = whitelist[customer_id]

        # Check if still valid
        if config['expires_at'] > datetime.now():
            return True, config['reason']

    return False, None

def add_to_whitelist(self, customer_id, reason, duration_days=30):
    """Add customer to whitelist"""
    expires_at = datetime.now() + timedelta(days=duration_days)

    whitelist = self.get_whitelist()
    whitelist[customer_id] = {
        'reason': reason,
        'expires_at': expires_at,
        'added_at': datetime.now(),
        'added_by': 'system'
    }

    self.save_whitelist(whitelist)
```

## Monitoring & Tuning

### Velocity Check Performance
```python
class VelocityMonitor:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            'checked': 0,
            'violations': 0,
            'false_positives': 0
        })

    def record_check(self, violation_type, was_fraud):
        """Record velocity check result"""
        self.stats[violation_type]['checked'] += 1

        if was_fraud:
            self.stats[violation_type]['violations'] += 1
        else:
            self.stats[violation_type]['false_positives'] += 1

    def get_effectiveness(self):
        """Calculate effectiveness metrics"""
        effectiveness = {}

        for check_type, stats in self.stats.items():
            checked = stats['checked']
            violations = stats['violations']
            fps = stats['false_positives']

            if checked > 0:
                precision = violations / (violations + fps) if (
                    violations + fps
                ) > 0 else 0
                detection_rate = violations / checked

                effectiveness[check_type] = {
                    'precision': precision,
                    'detection_rate': detection_rate,
                    'total_checks': checked
                }

        return effectiveness
```

## Best Practices

1. **Tiered Thresholds**: Different limits for different customer types
2. **Dynamic Adjustment**: Adjust for time of day, seasonality
3. **Multiple Checks**: Use multiple velocity metrics
4. **Whitelist Management**: Don't over-block legitimate users
5. **Monitoring**: Track false positive rate
6. **Tuning**: Regular threshold adjustment based on data
7. **Documentation**: Clear reasoning for thresholds
