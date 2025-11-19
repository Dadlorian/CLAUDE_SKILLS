# Behavioral Analytics Guide

## Behavioral Profile Creation

### Data Collection Period
```
Duration: 2-4 weeks of normal activity
Purpose: Establish baseline
Data needed: All user interactions

Events to Track:
- Login times
- Transaction patterns
- Device usage
- Navigation behavior
- Form completion time
- Session duration
```

### Feature Extraction
```python
import numpy as np
from datetime import datetime, timedelta

class BehavioralProfiler:
    def __init__(self, customer_id, lookback_days=30):
        self.customer_id = customer_id
        self.lookback_days = lookback_days

    def create_profile(self, interaction_data):
        """Create behavioral profile from raw data"""
        profile = {}

        # Temporal patterns
        profile['temporal'] = self._extract_temporal(interaction_data)

        # Transaction patterns
        profile['transaction'] = self._extract_transaction_patterns(
            interaction_data
        )

        # Device patterns
        profile['device'] = self._extract_device_patterns(interaction_data)

        # Navigation patterns
        profile['navigation'] = self._extract_navigation_patterns(
            interaction_data
        )

        # Typing patterns
        profile['typing'] = self._extract_typing_patterns(interaction_data)

        return profile

    def _extract_temporal(self, data):
        """Extract time-based patterns"""
        login_times = [d['timestamp'].hour for d in data]

        return {
            'active_hours': list(set(login_times)),
            'average_active_hour': np.mean(login_times),
            'typical_session_duration': np.mean(
                [d['session_duration'] for d in data]
            ),
            'access_days': self._get_access_days(data),
            'timezone': self._detect_timezone(data)
        }

    def _extract_transaction_patterns(self, data):
        """Extract transaction behavior patterns"""
        amounts = [d['amount'] for d in data if d['type'] == 'transaction']

        return {
            'mean_amount': np.mean(amounts),
            'std_amount': np.std(amounts),
            'median_amount': np.median(amounts),
            'typical_merchants': self._get_top_merchants(data),
            'typical_categories': self._get_top_categories(data),
            'transaction_frequency': len([
                d for d in data if d['type'] == 'transaction'
            ]) / self.lookback_days
        }

    def _extract_device_patterns(self, data):
        """Extract device usage patterns"""
        devices = [d['device_id'] for d in data if 'device_id' in d]

        return {
            'primary_device': max(set(devices), key=devices.count),
            'device_count': len(set(devices)),
            'typical_devices': list(set(devices))[:5],
            'os_distribution': self._get_os_distribution(data),
            'browser_distribution': self._get_browser_distribution(data)
        }

    def _extract_navigation_patterns(self, data):
        """Extract navigation behavior patterns"""
        sequences = [d['page_sequence'] for d in data if 'page_sequence' in d]

        return {
            'typical_pages': self._get_top_pages(data),
            'typical_sequences': self._get_common_sequences(sequences),
            'average_pages_per_session': self._get_avg_pages_per_session(data),
            'bounce_rate': self._calculate_bounce_rate(data)
        }

    def _extract_typing_patterns(self, data):
        """Extract keystroke dynamics"""
        typing_events = [d for d in data if d['type'] == 'typing']

        if not typing_events:
            return {}

        speeds = [e['speed'] for e in typing_events]
        dwell_times = [e['dwell_time'] for e in typing_events]

        return {
            'typing_speed_wpm': np.mean(speeds),
            'typing_speed_std': np.std(speeds),
            'dwell_time_ms': np.mean(dwell_times),
            'dwell_time_std': np.std(dwell_times)
        }

    # Helper methods...
    def _get_access_days(self, data):
        dates = set([d['timestamp'].date() for d in data])
        return {day.isoweekday(): day in dates for day in dates}

    def _get_top_merchants(self, data):
        merchants = [d.get('merchant') for d in data if d.get('merchant')]
        return [m for m, _ in Counter(merchants).most_common(10)]

    def _get_top_categories(self, data):
        categories = [d.get('category') for d in data if d.get('category')]
        return [c for c, _ in Counter(categories).most_common(10)]
```

## Anomaly Detection from Behavior

### Statistical Approach
```python
class BehavioralAnomalyDetector:
    def __init__(self, profile):
        self.profile = profile

    def score_session(self, session_data):
        """Score session for behavioral anomalies"""
        scores = {}

        # Check typing patterns
        if 'typing' in self.profile and 'typing' in session_data:
            scores['typing'] = self._score_typing(session_data['typing'])

        # Check temporal patterns
        if 'temporal' in session_data:
            scores['temporal'] = self._score_temporal(
                session_data['temporal']
            )

        # Check device patterns
        if 'device' in session_data:
            scores['device'] = self._score_device(session_data['device'])

        # Check navigation patterns
        if 'navigation' in session_data:
            scores['navigation'] = self._score_navigation(
                session_data['navigation']
            )

        # Combine scores
        overall_score = np.mean(list(scores.values())) if scores else 0.0

        return {
            'component_scores': scores,
            'overall_score': overall_score,
            'is_anomalous': overall_score > 0.7
        }

    def _score_typing(self, current_typing):
        """Score typing pattern anomaly"""
        profile_typing = self.profile.get('typing', {})

        if not profile_typing:
            return 0.5  # Unknown

        # Typing speed deviation
        baseline_speed = profile_typing.get('typing_speed_wpm', 50)
        baseline_std = profile_typing.get('typing_speed_std', 10)

        current_speed = current_typing.get('typing_speed_wpm', baseline_speed)

        z_score = abs(current_speed - baseline_speed) / baseline_std

        # Normalize to 0-1
        anomaly_score = min(z_score / 3.0, 1.0)

        return anomaly_score

    def _score_temporal(self, current_temporal):
        """Score temporal pattern anomaly"""
        profile_temporal = self.profile.get('temporal', {})

        current_hour = current_temporal.get('hour', 12)
        active_hours = profile_temporal.get('active_hours', [9, 10, 11, 13, 14])

        # Is current hour in typical active hours?
        if current_hour in active_hours:
            return 0.0  # Normal

        # Off-hours activity
        return 0.5

    def _score_device(self, current_device):
        """Score device anomaly"""
        profile_device = self.profile.get('device', {})
        typical_devices = profile_device.get('typical_devices', [])

        current_device_id = current_device.get('device_id')

        if current_device_id in typical_devices:
            return 0.0  # Known device

        return 0.8  # New device (high anomaly)

    def _score_navigation(self, current_navigation):
        """Score navigation pattern anomaly"""
        profile_nav = self.profile.get('navigation', {})

        current_sequence = current_navigation.get('page_sequence', [])
        typical_sequences = profile_nav.get('typical_sequences', [])

        # Calculate sequence similarity
        similarity = self._calculate_sequence_similarity(
            current_sequence,
            typical_sequences
        )

        # Invert to get anomaly score
        anomaly_score = 1.0 - similarity

        return anomaly_score

    def _calculate_sequence_similarity(self, current, typical):
        """Calculate similarity to typical sequences"""
        if not typical:
            return 0.5

        similarities = []
        for seq in typical:
            # Simple similarity: matching pages
            matching = len(set(current) & set(seq))
            possible = len(set(current) | set(seq))
            sim = matching / possible if possible > 0 else 0
            similarities.append(sim)

        return max(similarities)
```

## Baseline Establishment

### Initial Baseline
```
Week 1-2: Collect raw data
Week 3: Feature extraction
Week 4: Statistical analysis
Week 5: Threshold setting
```

### Adaptive Baselines
```python
class AdaptiveBaseline:
    def __init__(self, initial_profile, learning_rate=0.1):
        self.profile = initial_profile
        self.learning_rate = learning_rate
        self.update_count = 0

    def update_with_confirmed_legitimate(self, new_data):
        """Update baseline when confirmed legitimate activity"""
        self.update_count += 1

        # Gradually incorporate new data
        for component, values in new_data.items():
            if component in self.profile:
                # Weighted average
                old_val = self.profile[component]
                new_val = (1 - self.learning_rate) * old_val + \
                          self.learning_rate * values

                self.profile[component] = new_val

        # Increase learning rate as confidence grows
        if self.update_count > 100:
            self.learning_rate = 0.05  # Slow down adaptation

    def get_current_profile(self):
        """Get evolved baseline"""
        return self.profile
```

## Multi-Dimensional Risk Scoring

### Combined Behavioral Score
```python
def calculate_behavioral_risk(
    detector,
    session_data,
    weights=None
):
    """Calculate overall behavioral risk"""
    if weights is None:
        weights = {
            'typing': 0.2,
            'temporal': 0.2,
            'device': 0.3,
            'navigation': 0.15,
            'session_duration': 0.15
        }

    result = detector.score_session(session_data)
    component_scores = result['component_scores']

    # Weight components
    weighted_score = 0.0
    total_weight = 0.0

    for component, score in component_scores.items():
        weight = weights.get(component, 0.0)
        weighted_score += score * weight
        total_weight += weight

    # Normalize
    if total_weight > 0:
        return weighted_score / total_weight
    else:
        return 0.5  # Unknown

    # Scale to 0-1
    return min(weighted_score, 1.0)
```

## Integration with Fraud Scoring

### Behavioral Risk Component
```
Overall Fraud Score =
  0.25 * ML_Score +
  0.25 * Rules_Score +
  0.25 * Behavioral_Risk +
  0.25 * Network_Risk

Behavioral Risk is weighted equally with other components
```

### Behavioral Verification Triggers
```
If Behavioral Risk > 0.7:
  - Require additional authentication
  - Request 2FA
  - Verify device
  - Confirm transaction details

If Behavioral Risk > 0.85:
  - Block transaction
  - Contact customer
  - Investigation required
```

## Use Cases

### Account Takeover Detection
```
ATO Indicators:
- Typing patterns change dramatically
- Login time completely different
- Device changes suddenly
- Navigation behavior unusual
- Language preference changes
- Multiple failed login attempts

Detection: Behavioral risk > 0.8
Response: Force password reset + 2FA
```

### Compromised Credentials Detection
```
Indicators:
- Subtle behavioral changes (not obvious)
- Patterns evolve gradually
- New devices mixed with old
- Some sessions normal, some anomalous
- Inconsistent timing

Detection: Track component scores over time
Response: Behavioral alert + optional 2FA
```

### Velocity Abuse Detection
```
Indicators:
- Timing compressed (rapid requests)
- Skipped steps in normal flow
- Rapid form fills (faster than typical)
- Batch processing patterns

Detection: Session duration analysis
Response: Rate limit + verify
```

## Monitoring & Maintenance

### Profile Freshness
```
Update frequency:
- New user (week 1): Daily
- Established user (month 1): Weekly
- Mature user (month 3+): Monthly

Monitor:
- Profile staleness
- Baseline drift
- Seasonal changes
- Legitimate behavior evolution
```

### Performance Metrics
```
Daily:
- False positive rate (false ATO alerts)
- True positive rate (actual ATO caught)
- Behavioral component accuracy

Weekly:
- Performance trend
- Segment performance (by user type)
- Effectiveness of thresholds

Monthly:
- Overall system performance
- Baseline quality assessment
- Improvement opportunities
```

## Implementation Challenges

### Cold Start Problem
```
New users with no baseline:

Solution 1: Cohort Baseline
- Use similar users' profile
- Gradually adapt to individual

Solution 2: Risk-Based Initial
- Start with higher thresholds
- Loosen thresholds as data accumulates

Solution 3: Pre-Fill Baseline
- Use KYC/registration data
- Customer-provided preferences
```

### Legitimate Behavior Changes
```
Users change behavior (vacation, job change, etc.)

Solution:
- Monitor for persistent behavior change
- Gradually accept new patterns
- Maintain historical "normal" range
- Alert on sudden changes

Implementation:
- Multi-week observation period
- Gradual threshold adjustment
- Historical data retention
```

### Privacy Considerations
```
Behavioral tracking concerns:

Mitigation:
- Anonymize profiles
- Limit data retention (30 days)
- User consent for tracking
- Transparency in privacy policy
- Data minimization
- Secure storage
```

## Best Practices

1. **Gradual Baseline**: 2-4 week establishment period
2. **Multiple Dimensions**: Don't rely on single behavior
3. **Adaptive Learning**: Update baselines with verified activity
4. **Privacy First**: Minimize personal data collection
5. **Transparency**: Users should know about monitoring
6. **Fallback**: Rules engine if behavioral data unavailable
7. **Verification**: Always verify before blocking
8. **Monitoring**: Track system performance continuously
