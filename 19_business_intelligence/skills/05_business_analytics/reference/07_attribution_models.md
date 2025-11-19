# Attribution Models Reference

Comprehensive guide to marketing attribution models and multi-touch attribution analysis.

## What is Attribution?

**Definition**: The process of assigning credit to marketing touchpoints that lead to a conversion.

**Why Attribution Matters**:
- Optimize marketing spend allocation
- Understand customer journey
- Measure channel effectiveness
- Inform budget decisions
- Calculate true ROI per channel

## Single-Touch Attribution Models

### 1. First-Touch Attribution

**All credit goes to the first touchpoint**.

```sql
-- First-touch attribution
WITH first_touch AS (
  SELECT
    user_id,
    conversion_id,
    FIRST_VALUE(channel) OVER (
      PARTITION BY user_id, conversion_id
      ORDER BY touchpoint_timestamp
    ) as first_touch_channel,
    FIRST_VALUE(campaign) OVER (
      PARTITION BY user_id, conversion_id
      ORDER BY touchpoint_timestamp
    ) as first_touch_campaign
  FROM touchpoints
)
SELECT
  first_touch_channel,
  first_touch_campaign,
  COUNT(DISTINCT conversion_id) as conversions,
  SUM(conversion_value) as attributed_revenue
FROM first_touch ft
JOIN conversions c ON ft.conversion_id = c.id
GROUP BY 1, 2
ORDER BY 4 DESC;
```

**Use Cases**:
- Top-of-funnel awareness campaigns
- Brand building initiatives
- Understanding discovery channels

**Limitations**:
- Ignores nurturing touchpoints
- Over-values awareness channels
- Doesn't reflect full customer journey

### 2. Last-Touch Attribution

**All credit goes to the last touchpoint before conversion**.

```sql
-- Last-touch attribution
WITH last_touch AS (
  SELECT
    user_id,
    conversion_id,
    LAST_VALUE(channel) OVER (
      PARTITION BY user_id, conversion_id
      ORDER BY touchpoint_timestamp
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_touch_channel,
    LAST_VALUE(campaign) OVER (
      PARTITION BY user_id, conversion_id
      ORDER BY touchpoint_timestamp
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_touch_campaign
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
)
SELECT
  last_touch_channel,
  last_touch_campaign,
  COUNT(DISTINCT conversion_id) as conversions,
  SUM(conversion_value) as attributed_revenue
FROM last_touch lt
JOIN conversions c ON lt.conversion_id = c.id
GROUP BY 1, 2
ORDER BY 4 DESC;
```

**Use Cases**:
- Bottom-of-funnel optimization
- Direct response campaigns
- Short sales cycles

**Limitations**:
- Ignores all earlier touchpoints
- May over-value retargeting/branded search
- Misses assisted conversions

### 3. Last Non-Direct Click

**Credit to last touchpoint excluding direct traffic** (Google Analytics default).

```sql
-- Last non-direct click attribution
WITH last_non_direct AS (
  SELECT
    user_id,
    conversion_id,
    LAST_VALUE(channel) OVER (
      PARTITION BY user_id, conversion_id
      ORDER BY touchpoint_timestamp
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as attributed_channel
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
    AND channel != 'Direct'
)
SELECT
  attributed_channel,
  COUNT(DISTINCT conversion_id) as conversions,
  SUM(conversion_value) as attributed_revenue
FROM last_non_direct lnd
JOIN conversions c ON lnd.conversion_id = c.id
GROUP BY 1
ORDER BY 3 DESC;
```

## Multi-Touch Attribution Models

### 4. Linear Attribution

**Equal credit to all touchpoints**.

```sql
-- Linear attribution (equal weight)
WITH touchpoint_counts AS (
  SELECT
    conversion_id,
    channel,
    campaign,
    COUNT(*) as num_touchpoints,
    COUNT(*) OVER (PARTITION BY conversion_id) as total_touchpoints
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
  GROUP BY 1, 2, 3
),
attributed_conversions AS (
  SELECT
    tc.channel,
    tc.campaign,
    tc.conversion_id,
    c.conversion_value,
    c.conversion_value * (tc.num_touchpoints * 1.0 / tc.total_touchpoints) as attributed_value
  FROM touchpoint_counts tc
  JOIN conversions c ON tc.conversion_id = c.id
)
SELECT
  channel,
  campaign,
  COUNT(DISTINCT conversion_id) as assisted_conversions,
  SUM(attributed_value) as attributed_revenue
FROM attributed_conversions
GROUP BY 1, 2
ORDER BY 4 DESC;
```

**Use Cases**:
- Simple, easy to explain
- Equal importance across journey
- Long, complex sales cycles

**Limitations**:
- All touchpoints may not be equally important
- Doesn't account for recency or position

### 5. Time-Decay Attribution

**More recent touchpoints get more credit**.

```sql
-- Time-decay attribution (exponential decay)
WITH touchpoint_weights AS (
  SELECT
    conversion_id,
    channel,
    campaign,
    touchpoint_timestamp,
    conversion_timestamp,
    -- Calculate days before conversion
    EXTRACT(DAY FROM (conversion_timestamp - touchpoint_timestamp)) as days_before_conversion,
    -- Exponential decay: weight = e^(-days/halflife)
    -- Using 7-day half-life
    EXP(-EXTRACT(DAY FROM (conversion_timestamp - touchpoint_timestamp)) / 7.0) as weight
  FROM touchpoints t
  JOIN conversions c ON t.conversion_id = c.id
  WHERE t.touchpoint_timestamp < c.conversion_timestamp
),
normalized_weights AS (
  SELECT
    conversion_id,
    channel,
    campaign,
    weight,
    SUM(weight) OVER (PARTITION BY conversion_id) as total_weight,
    weight / SUM(weight) OVER (PARTITION BY conversion_id) as normalized_weight
  FROM touchpoint_weights
)
SELECT
  nw.channel,
  nw.campaign,
  COUNT(DISTINCT nw.conversion_id) as assisted_conversions,
  SUM(c.conversion_value * nw.normalized_weight) as attributed_revenue
FROM normalized_weights nw
JOIN conversions c ON nw.conversion_id = c.id
GROUP BY 1, 2
ORDER BY 4 DESC;
```

**Python Implementation**:
```python
import pandas as pd
import numpy as np

def time_decay_attribution(touchpoints_df, half_life_days=7):
    """
    Calculate time-decay attribution

    Args:
        touchpoints_df: DataFrame with [conversion_id, channel, timestamp, conversion_timestamp, value]
        half_life_days: Number of days for weight to decay by half

    Returns:
        DataFrame with attributed revenue per channel
    """
    # Calculate days before conversion
    touchpoints_df['days_before'] = (
        touchpoints_df['conversion_timestamp'] - touchpoints_df['timestamp']
    ).dt.total_seconds() / (24 * 3600)

    # Calculate exponential decay weight
    touchpoints_df['weight'] = np.exp(-touchpoints_df['days_before'] / half_life_days)

    # Normalize weights per conversion
    touchpoints_df['total_weight'] = touchpoints_df.groupby('conversion_id')['weight'].transform('sum')
    touchpoints_df['normalized_weight'] = touchpoints_df['weight'] / touchpoints_df['total_weight']

    # Calculate attributed value
    touchpoints_df['attributed_value'] = (
        touchpoints_df['value'] * touchpoints_df['normalized_weight']
    )

    # Aggregate by channel
    attribution = touchpoints_df.groupby('channel').agg({
        'conversion_id': 'nunique',
        'attributed_value': 'sum'
    }).reset_index()

    attribution.columns = ['channel', 'conversions', 'attributed_revenue']

    return attribution
```

### 6. Position-Based (U-Shaped) Attribution

**40% to first touch, 40% to last touch, 20% split among middle touches**.

```sql
-- Position-based attribution (40-20-40 model)
WITH touchpoint_positions AS (
  SELECT
    conversion_id,
    channel,
    campaign,
    ROW_NUMBER() OVER (PARTITION BY conversion_id ORDER BY touchpoint_timestamp) as position,
    COUNT(*) OVER (PARTITION BY conversion_id) as total_touches
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
),
position_weights AS (
  SELECT
    conversion_id,
    channel,
    campaign,
    CASE
      WHEN position = 1 THEN 0.4  -- First touch gets 40%
      WHEN position = total_touches THEN 0.4  -- Last touch gets 40%
      ELSE 0.2 / NULLIF(total_touches - 2, 0)  -- Middle touches split 20%
    END as weight
  FROM touchpoint_positions
)
SELECT
  pw.channel,
  pw.campaign,
  COUNT(DISTINCT pw.conversion_id) as assisted_conversions,
  SUM(c.conversion_value * pw.weight) as attributed_revenue
FROM position_weights pw
JOIN conversions c ON pw.conversion_id = c.id
GROUP BY 1, 2
ORDER BY 4 DESC;
```

**Variations**:
- **W-Shaped**: 30% first, 30% lead conversion, 30% last, 10% middle
- **Z-Shaped**: 25% first, 25% lead, 25% opportunity, 25% last

### 7. Data-Driven Attribution

**Machine learning models determine optimal credit allocation**.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class DataDrivenAttribution:
    """Algorithmic attribution using logistic regression"""

    def __init__(self):
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.channel_importance = {}

    def prepare_features(self, journey_data):
        """
        Create features from user journey

        Args:
            journey_data: DataFrame with user journeys
                Columns: [user_id, converted, channel_1_count, channel_2_count, ...]

        Returns:
            Feature matrix
        """
        # Create channel touchpoint counts
        feature_cols = [col for col in journey_data.columns
                       if col not in ['user_id', 'converted']]

        X = journey_data[feature_cols].values
        y = journey_data['converted'].values

        return X, y, feature_cols

    def train(self, journey_data):
        """Train attribution model"""
        X, y, feature_cols = self.prepare_features(journey_data)

        # Standardize features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)

        # Extract channel importance from coefficients
        coefficients = self.model.coef_[0]

        self.channel_importance = dict(zip(feature_cols, coefficients))

        return self.channel_importance

    def attribute_conversion(self, user_journey):
        """
        Attribute a single conversion across touchpoints

        Args:
            user_journey: Dict with channel touchpoint counts

        Returns:
            Dict with attributed credit per channel
        """
        total_credit = sum([
            self.channel_importance.get(channel, 0) * count
            for channel, count in user_journey.items()
        ])

        attribution = {}
        for channel, count in user_journey.items():
            if count > 0:
                channel_credit = self.channel_importance.get(channel, 0) * count
                attribution[channel] = channel_credit / total_credit if total_credit > 0 else 0

        return attribution
```

## Markov Chain Attribution

**Models user journey as state transitions**.

```python
import numpy as np
from collections import defaultdict

class MarkovAttribution:
    """Markov chain attribution modeling"""

    def __init__(self):
        self.transition_probs = {}
        self.removal_effects = {}

    def build_transition_matrix(self, journeys):
        """
        Build transition probability matrix from user journeys

        Args:
            journeys: List of journeys, each journey is list of channels
                     Example: [['SEO', 'Email', 'Direct'], ['Paid', 'Direct'], ...]
        """
        transitions = defaultdict(lambda: defaultdict(int))
        total_from = defaultdict(int)

        for journey in journeys:
            journey_with_start_end = ['Start'] + journey + ['Conversion']

            for i in range(len(journey_with_start_end) - 1):
                from_channel = journey_with_start_end[i]
                to_channel = journey_with_start_end[i + 1]

                transitions[from_channel][to_channel] += 1
                total_from[from_channel] += 1

        # Calculate probabilities
        for from_channel in transitions:
            for to_channel in transitions[from_channel]:
                count = transitions[from_channel][to_channel]
                total = total_from[from_channel]
                prob = count / total if total > 0 else 0

                if from_channel not in self.transition_probs:
                    self.transition_probs[from_channel] = {}
                self.transition_probs[from_channel][to_channel] = prob

    def calculate_conversion_probability(self, exclude_channel=None):
        """Calculate probability of conversion, optionally excluding a channel"""
        # Implement forward probability calculation
        # Simplified version - in practice, use proper Markov chain algorithms
        pass

    def removal_effect_attribution(self, journeys):
        """
        Calculate attribution using removal effect

        For each channel, measure how much conversion probability drops
        when that channel is removed from the graph.
        """
        # Base conversion probability
        base_conversion_prob = self.calculate_conversion_probability()

        attribution = {}

        # Get all unique channels
        all_channels = set()
        for journey in journeys:
            all_channels.update(journey)

        # Calculate removal effect for each channel
        for channel in all_channels:
            prob_without_channel = self.calculate_conversion_probability(exclude_channel=channel)
            removal_effect = base_conversion_prob - prob_without_channel
            attribution[channel] = removal_effect

        # Normalize to sum to 1
        total_effect = sum(attribution.values())
        if total_effect > 0:
            attribution = {k: v / total_effect for k, v in attribution.items()}

        return attribution
```

## Attribution Analysis Queries

### Assisted Conversions

```sql
-- Channels that assisted but didn't get last-touch credit
WITH last_touch AS (
  SELECT
    conversion_id,
    LAST_VALUE(channel) OVER (
      PARTITION BY conversion_id
      ORDER BY touchpoint_timestamp
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_touch_channel
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
),
all_touches AS (
  SELECT DISTINCT
    conversion_id,
    channel as touch_channel
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
)
SELECT
  at.touch_channel,
  COUNT(DISTINCT at.conversion_id) as total_conversions_involved,
  COUNT(DISTINCT CASE WHEN at.touch_channel = lt.last_touch_channel
        THEN at.conversion_id END) as last_touch_conversions,
  COUNT(DISTINCT CASE WHEN at.touch_channel != lt.last_touch_channel
        THEN at.conversion_id END) as assisted_conversions,
  ROUND(
    COUNT(DISTINCT CASE WHEN at.touch_channel != lt.last_touch_channel THEN at.conversion_id END) * 100.0 /
    NULLIF(COUNT(DISTINCT CASE WHEN at.touch_channel = lt.last_touch_channel THEN at.conversion_id END), 0),
    2
  ) as assisted_to_last_ratio
FROM all_touches at
JOIN last_touch lt ON at.conversion_id = lt.conversion_id
GROUP BY 1
ORDER BY 5 DESC;
```

### Customer Journey Analysis

```sql
-- Most common conversion paths
WITH journey_paths AS (
  SELECT
    conversion_id,
    STRING_AGG(channel, ' > ' ORDER BY touchpoint_timestamp) as journey_path,
    COUNT(*) as touchpoint_count
  FROM touchpoints
  WHERE touchpoint_timestamp < conversion_timestamp
  GROUP BY 1
)
SELECT
  journey_path,
  touchpoint_count,
  COUNT(*) as num_conversions,
  SUM(conversion_value) as total_value,
  AVG(conversion_value) as avg_value
FROM journey_paths jp
JOIN conversions c ON jp.conversion_id = c.id
GROUP BY 1, 2
HAVING COUNT(*) >= 10  -- Minimum occurrences
ORDER BY 3 DESC
LIMIT 50;
```

### Channel Interaction Analysis

```sql
-- Which channel pairs work well together?
WITH channel_pairs AS (
  SELECT
    a.conversion_id,
    a.channel as channel_1,
    b.channel as channel_2,
    a.touchpoint_timestamp as touch_1_time,
    b.touchpoint_timestamp as touch_2_time
  FROM touchpoints a
  JOIN touchpoints b
    ON a.conversion_id = b.conversion_id
    AND a.touchpoint_timestamp < b.touchpoint_timestamp
  WHERE a.channel != b.channel
)
SELECT
  channel_1,
  channel_2,
  COUNT(DISTINCT conversion_id) as conversions_with_both,
  AVG(EXTRACT(EPOCH FROM (touch_2_time - touch_1_time)) / 3600) as avg_hours_between
FROM channel_pairs
GROUP BY 1, 2
HAVING COUNT(DISTINCT conversion_id) >= 20
ORDER BY 3 DESC;
```

## Attribution Window Analysis

```sql
-- Impact of attribution window length
WITH conversions_with_windows AS (
  SELECT
    c.id as conversion_id,
    c.conversion_value,
    COUNT(CASE WHEN t.touchpoint_timestamp >= c.conversion_timestamp - INTERVAL '1 day'
          THEN t.id END) as touches_1day,
    COUNT(CASE WHEN t.touchpoint_timestamp >= c.conversion_timestamp - INTERVAL '7 days'
          THEN t.id END) as touches_7day,
    COUNT(CASE WHEN t.touchpoint_timestamp >= c.conversion_timestamp - INTERVAL '30 days'
          THEN t.id END) as touches_30day,
    COUNT(CASE WHEN t.touchpoint_timestamp >= c.conversion_timestamp - INTERVAL '90 days'
          THEN t.id END) as touches_90day
  FROM conversions c
  LEFT JOIN touchpoints t ON c.user_id = t.user_id
    AND t.touchpoint_timestamp < c.conversion_timestamp
  GROUP BY 1, 2
)
SELECT
  'Avg Touchpoints' as metric,
  AVG(touches_1day) as window_1day,
  AVG(touches_7day) as window_7day,
  AVG(touches_30day) as window_30day,
  AVG(touches_90day) as window_90day
FROM conversions_with_windows;
```

## Comparing Attribution Models

```sql
-- Side-by-side attribution model comparison
WITH first_touch AS (
  SELECT conversion_id, channel, SUM(conversion_value) as attributed_value
  FROM first_touch_attribution
  GROUP BY 1, 2
),
last_touch AS (
  SELECT conversion_id, channel, SUM(conversion_value) as attributed_value
  FROM last_touch_attribution
  GROUP BY 1, 2
),
linear AS (
  SELECT conversion_id, channel, SUM(attributed_value) as attributed_value
  FROM linear_attribution
  GROUP BY 1, 2
)
SELECT
  COALESCE(ft.channel, lt.channel, ln.channel) as channel,
  SUM(ft.attributed_value) as first_touch_revenue,
  SUM(lt.attributed_value) as last_touch_revenue,
  SUM(ln.attributed_value) as linear_revenue,
  -- Calculate differences
  SUM(ln.attributed_value) - SUM(ft.attributed_value) as linear_vs_first_diff,
  SUM(ln.attributed_value) - SUM(lt.attributed_value) as linear_vs_last_diff
FROM first_touch ft
FULL OUTER JOIN last_touch lt USING (conversion_id, channel)
FULL OUTER JOIN linear ln USING (conversion_id, channel)
GROUP BY 1
ORDER BY 4 DESC;
```

## Best Practices

### Choosing an Attribution Model

1. **Business Goals**: Match model to objectives
2. **Sales Cycle Length**: Longer cycles need multi-touch
3. **Touchpoint Complexity**: More touchpoints need sophisticated models
4. **Data Quality**: Ensure complete journey tracking
5. **Stakeholder Buy-in**: Choose explainable models

### Implementation Checklist

- [ ] Track all touchpoints consistently
- [ ] Define clear conversion events
- [ ] Set appropriate attribution windows
- [ ] Handle cross-device journeys
- [ ] Account for offline touchpoints
- [ ] Validate data quality
- [ ] Compare multiple models
- [ ] Document methodology
- [ ] Communicate limitations
- [ ] Regular model updates

### Common Challenges

1. **Cross-Device Tracking**: Users switch devices
2. **Walled Gardens**: Limited data from platforms (Facebook, Google)
3. **Privacy Regulations**: GDPR, CCPA limit tracking
4. **Cookie Deprecation**: Third-party cookie phaseout
5. **Offline Integration**: Connecting online/offline touchpoints
6. **Sample Size**: Insufficient data for complex models
7. **Attribution Gaming**: Teams optimizing for model, not results

## Attribution Model Selection Guide

| Model | Best For | Limitations |
|-------|----------|-------------|
| First-Touch | Awareness campaigns, new customer acquisition | Ignores nurturing |
| Last-Touch | Direct response, short sales cycles | Ignores discovery |
| Linear | Equal importance across journey | No position weighting |
| Time-Decay | Recency matters, final decision touchpoints | May undervalue discovery |
| Position-Based | Discovery and conversion both important | Middle arbitrary |
| Data-Driven | Complex journeys, sufficient data | Black box, requires ML expertise |
| Markov Chain | True incremental impact | Complex, hard to explain |

## Key Takeaways

1. **No Perfect Model**: Each has tradeoffs
2. **Multi-Touch > Single-Touch**: For complex journeys
3. **Compare Models**: Understand differences in attribution
4. **Data Quality Critical**: Attribution only as good as tracking
5. **Business Context Matters**: Choose model aligned with goals
6. **Incremental Value**: Focus on true incremental contribution
7. **Regular Review**: Update as customer journeys evolve
8. **Action > Precision**: Directionally correct > perfectly wrong
