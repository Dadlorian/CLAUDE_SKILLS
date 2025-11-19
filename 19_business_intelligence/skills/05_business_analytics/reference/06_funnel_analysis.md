# Funnel Analysis Reference

Comprehensive guide to building, analyzing, and optimizing conversion funnels for product and marketing analytics.

## What is Funnel Analysis?

**Definition**: A method to track user progression through a series of steps toward a desired outcome (conversion).

**Purpose**:
- Identify drop-off points in user journey
- Measure conversion rates at each stage
- Prioritize optimization efforts
- Compare performance across segments
- Track impact of product changes

## Types of Funnels

### 1. Linear Funnels

**Sequential steps that must occur in order**:

```sql
-- Classic signup to purchase funnel
WITH funnel_stages AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_name = 'page_view' THEN 1 ELSE 0 END) as viewed,
    MAX(CASE WHEN event_name = 'signup_started' THEN 1 ELSE 0 END) as started_signup,
    MAX(CASE WHEN event_name = 'signup_completed' THEN 1 ELSE 0 END) as completed_signup,
    MAX(CASE WHEN event_name = 'profile_completed' THEN 1 ELSE 0 END) as completed_profile,
    MAX(CASE WHEN event_name = 'first_purchase' THEN 1 ELSE 0 END) as purchased
  FROM events
  WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1
)
SELECT
  COUNT(*) as total_users,
  SUM(viewed) as step1_viewed,
  SUM(started_signup) as step2_started_signup,
  SUM(completed_signup) as step3_completed_signup,
  SUM(completed_profile) as step4_completed_profile,
  SUM(purchased) as step5_purchased,

  -- Conversion rates
  ROUND(SUM(started_signup) * 100.0 / NULLIF(SUM(viewed), 0), 2) as view_to_start_pct,
  ROUND(SUM(completed_signup) * 100.0 / NULLIF(SUM(started_signup), 0), 2) as start_to_complete_pct,
  ROUND(SUM(completed_profile) * 100.0 / NULLIF(SUM(completed_signup), 0), 2) as signup_to_profile_pct,
  ROUND(SUM(purchased) * 100.0 / NULLIF(SUM(completed_profile), 0), 2) as profile_to_purchase_pct,

  -- Overall conversion
  ROUND(SUM(purchased) * 100.0 / NULLIF(SUM(viewed), 0), 2) as overall_conversion_pct
FROM funnel_stages;
```

### 2. Time-Bound Funnels

**Steps must occur within a time window**:

```sql
-- 7-day conversion window funnel
WITH user_first_events AS (
  SELECT
    user_id,
    MIN(CASE WHEN event_name = 'landing_page_view' THEN event_timestamp END) as landing_time,
    MIN(CASE WHEN event_name = 'signup' THEN event_timestamp END) as signup_time,
    MIN(CASE WHEN event_name = 'activation' THEN event_timestamp END) as activation_time,
    MIN(CASE WHEN event_name = 'purchase' THEN event_timestamp END) as purchase_time
  FROM events
  GROUP BY 1
),
funnel_with_timing AS (
  SELECT
    user_id,
    landing_time,
    CASE WHEN signup_time <= landing_time + INTERVAL '7 days' THEN 1 ELSE 0 END as signed_up,
    CASE WHEN activation_time <= landing_time + INTERVAL '7 days' THEN 1 ELSE 0 END as activated,
    CASE WHEN purchase_time <= landing_time + INTERVAL '7 days' THEN 1 ELSE 0 END as purchased
  FROM user_first_events
  WHERE landing_time >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
  COUNT(*) as landed,
  SUM(signed_up) as signups_7d,
  SUM(activated) as activations_7d,
  SUM(purchased) as purchases_7d,
  ROUND(SUM(signed_up) * 100.0 / COUNT(*), 2) as signup_rate_7d,
  ROUND(SUM(activated) * 100.0 / NULLIF(SUM(signed_up), 0), 2) as activation_rate_7d,
  ROUND(SUM(purchased) * 100.0 / NULLIF(SUM(activated), 0), 2) as purchase_rate_7d
FROM funnel_with_timing;
```

### 3. Strict Order Funnels

**Steps must occur in exact sequence**:

```sql
-- Ordered funnel (steps must happen in sequence)
WITH ordered_events AS (
  SELECT
    user_id,
    event_name,
    event_timestamp,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_timestamp) as event_order
  FROM events
  WHERE event_name IN ('view_product', 'add_to_cart', 'checkout', 'purchase')
    AND event_date >= CURRENT_DATE - INTERVAL '30 days'
),
funnel_sequences AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_name = 'view_product' AND event_order = 1 THEN 1 ELSE 0 END) as started_correctly,
    MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) as added_to_cart,
    MAX(CASE WHEN event_name = 'checkout' THEN 1 ELSE 0 END) as checked_out,
    MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) as purchased
  FROM ordered_events
  GROUP BY 1
)
SELECT
  SUM(started_correctly) as viewed_product,
  SUM(CASE WHEN started_correctly = 1 AND added_to_cart = 1 THEN 1 ELSE 0 END) as added_after_view,
  SUM(CASE WHEN started_correctly = 1 AND added_to_cart = 1 AND checked_out = 1 THEN 1 ELSE 0 END) as checked_out_after_add,
  SUM(CASE WHEN started_correctly = 1 AND added_to_cart = 1 AND checked_out = 1 AND purchased = 1 THEN 1 ELSE 0 END) as purchased_after_checkout
FROM funnel_sequences;
```

### 4. Multi-Path Funnels

**Multiple routes to conversion**:

```sql
-- Funnel with multiple paths to conversion
WITH user_paths AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_name IN ('landing_page_view', 'homepage_view') THEN 1 ELSE 0 END) as entered,
    MAX(CASE WHEN event_name = 'free_trial' THEN 1 ELSE 0 END) as took_trial,
    MAX(CASE WHEN event_name = 'demo_requested' THEN 1 ELSE 0 END) as requested_demo,
    MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) as purchased
  FROM events
  WHERE event_date >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY 1
)
SELECT
  'Overall' as path,
  SUM(entered) as entered,
  SUM(purchased) as converted,
  ROUND(SUM(purchased) * 100.0 / NULLIF(SUM(entered), 0), 2) as conversion_rate
FROM user_paths

UNION ALL

SELECT
  'Trial Path',
  SUM(CASE WHEN entered = 1 AND took_trial = 1 THEN 1 ELSE 0 END),
  SUM(CASE WHEN entered = 1 AND took_trial = 1 AND purchased = 1 THEN 1 ELSE 0 END),
  ROUND(SUM(CASE WHEN entered = 1 AND took_trial = 1 AND purchased = 1 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(CASE WHEN entered = 1 AND took_trial = 1 THEN 1 ELSE 0 END), 0), 2)
FROM user_paths

UNION ALL

SELECT
  'Demo Path',
  SUM(CASE WHEN entered = 1 AND requested_demo = 1 THEN 1 ELSE 0 END),
  SUM(CASE WHEN entered = 1 AND requested_demo = 1 AND purchased = 1 THEN 1 ELSE 0 END),
  ROUND(SUM(CASE WHEN entered = 1 AND requested_demo = 1 AND purchased = 1 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(CASE WHEN entered = 1 AND requested_demo = 1 THEN 1 ELSE 0 END), 0), 2)
FROM user_paths;
```

## Funnel Metrics

### Key Performance Indicators

**1. Stage Conversion Rate**:
```
Conversion Rate = (Users in Next Stage / Users in Current Stage) × 100
```

**2. Overall Conversion Rate**:
```
Overall Rate = (Users Who Completed / Users Who Started) × 100
```

**3. Drop-off Rate**:
```
Drop-off Rate = (Users Who Left / Users in Stage) × 100 = 100 - Conversion Rate
```

**4. Time to Convert**:
```sql
-- Average time between funnel stages
WITH funnel_timing AS (
  SELECT
    user_id,
    MIN(CASE WHEN event_name = 'signup' THEN event_timestamp END) as signup_time,
    MIN(CASE WHEN event_name = 'activation' THEN event_timestamp END) as activation_time,
    MIN(CASE WHEN event_name = 'purchase' THEN event_timestamp END) as purchase_time
  FROM events
  GROUP BY 1
)
SELECT
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM (activation_time - signup_time)) / 3600
  ) as median_hours_signup_to_activation,
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM (purchase_time - activation_time)) / 3600
  ) as median_hours_activation_to_purchase,
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM (purchase_time - signup_time)) / 3600
  ) as median_hours_signup_to_purchase
FROM funnel_timing
WHERE activation_time IS NOT NULL
  AND purchase_time IS NOT NULL;
```

## Segmented Funnel Analysis

### By Acquisition Channel

```sql
-- Funnel comparison by channel
WITH channel_funnels AS (
  SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) as total_users,
    COUNT(DISTINCT CASE WHEN e.event_name = 'signup' THEN u.user_id END) as signups,
    COUNT(DISTINCT CASE WHEN e.event_name = 'activation' THEN u.user_id END) as activations,
    COUNT(DISTINCT CASE WHEN e.event_name = 'purchase' THEN u.user_id END) as purchases
  FROM users u
  LEFT JOIN events e ON u.user_id = e.user_id
  WHERE u.signup_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1
)
SELECT
  acquisition_channel,
  total_users,
  signups,
  activations,
  purchases,
  ROUND(signups * 100.0 / total_users, 2) as signup_rate,
  ROUND(activations * 100.0 / NULLIF(signups, 0), 2) as activation_rate,
  ROUND(purchases * 100.0 / NULLIF(activations, 0), 2) as purchase_rate,
  ROUND(purchases * 100.0 / total_users, 2) as overall_conversion
FROM channel_funnels
ORDER BY overall_conversion DESC;
```

### By Device/Platform

```sql
-- Device-specific funnel performance
SELECT
  device_type,
  platform,
  COUNT(*) as sessions,
  SUM(CASE WHEN product_viewed THEN 1 ELSE 0 END) as product_views,
  SUM(CASE WHEN added_to_cart THEN 1 ELSE 0 END) as cart_adds,
  SUM(CASE WHEN checkout_started THEN 1 ELSE 0 END) as checkouts,
  SUM(CASE WHEN purchased THEN 1 ELSE 0 END) as purchases,
  ROUND(SUM(CASE WHEN purchased THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as conversion_rate
FROM session_funnels
GROUP BY 1, 2
ORDER BY 1, 8 DESC;
```

### By User Cohort

```sql
-- Funnel performance by signup cohort
SELECT
  DATE_TRUNC('month', u.signup_date) as cohort_month,
  COUNT(DISTINCT u.user_id) as cohort_size,
  COUNT(DISTINCT CASE WHEN o.order_id IS NOT NULL THEN u.user_id END) as purchasers,
  ROUND(COUNT(DISTINCT CASE WHEN o.order_id IS NOT NULL THEN u.user_id END) * 100.0 /
        COUNT(DISTINCT u.user_id), 2) as conversion_rate,
  AVG(EXTRACT(DAY FROM (o.order_date - u.signup_date))) as avg_days_to_purchase
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
  AND o.order_date <= u.signup_date + INTERVAL '30 days'
GROUP BY 1
ORDER BY 1 DESC;
```

## Advanced Funnel Analysis

### Micro-Conversions

**Breaking down major steps into sub-steps**:

```sql
-- Detailed checkout funnel with sub-steps
WITH checkout_steps AS (
  SELECT
    session_id,
    MAX(CASE WHEN event_name = 'checkout_started' THEN 1 ELSE 0 END) as started,
    MAX(CASE WHEN event_name = 'shipping_info_added' THEN 1 ELSE 0 END) as added_shipping,
    MAX(CASE WHEN event_name = 'payment_info_added' THEN 1 ELSE 0 END) as added_payment,
    MAX(CASE WHEN event_name = 'order_reviewed' THEN 1 ELSE 0 END) as reviewed,
    MAX(CASE WHEN event_name = 'purchase_completed' THEN 1 ELSE 0 END) as completed
  FROM events
  WHERE event_date >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY 1
)
SELECT
  SUM(started) as started_checkout,
  SUM(added_shipping) as added_shipping_info,
  SUM(added_payment) as added_payment_info,
  SUM(reviewed) as reviewed_order,
  SUM(completed) as completed_purchase,

  ROUND(SUM(added_shipping) * 100.0 / NULLIF(SUM(started), 0), 2) as shipping_conversion,
  ROUND(SUM(added_payment) * 100.0 / NULLIF(SUM(added_shipping), 0), 2) as payment_conversion,
  ROUND(SUM(reviewed) * 100.0 / NULLIF(SUM(added_payment), 0), 2) as review_conversion,
  ROUND(SUM(completed) * 100.0 / NULLIF(SUM(reviewed), 0), 2) as completion_conversion
FROM checkout_steps;
```

### Reverse Funnels (Working Backwards)

```sql
-- Start from purchasers and work backwards
WITH purchaser_journey AS (
  SELECT
    p.user_id,
    p.purchase_date,
    MAX(CASE WHEN e.event_name = 'landing_page_view'
             AND e.event_timestamp <= p.purchase_date THEN 1 ELSE 0 END) as had_landing,
    MAX(CASE WHEN e.event_name = 'product_view'
             AND e.event_timestamp <= p.purchase_date THEN 1 ELSE 0 END) as had_product_view,
    MAX(CASE WHEN e.event_name = 'add_to_cart'
             AND e.event_timestamp <= p.purchase_date THEN 1 ELSE 0 END) as had_cart_add
  FROM purchases p
  LEFT JOIN events e ON p.user_id = e.user_id
  WHERE p.purchase_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1, 2
)
SELECT
  COUNT(*) as total_purchases,
  SUM(had_cart_add) as came_through_cart,
  SUM(had_product_view) as viewed_product_page,
  SUM(had_landing) as came_through_landing,
  ROUND(SUM(had_cart_add) * 100.0 / COUNT(*), 2) as pct_through_cart,
  ROUND(SUM(CASE WHEN had_cart_add = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pct_skip_cart
FROM purchaser_journey;
```

### Funnel Abandonment Analysis

```sql
-- Analyze where users abandon the funnel
WITH funnel_progress AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_name = 'step_1' THEN 1 ELSE 0 END) as reached_step_1,
    MAX(CASE WHEN event_name = 'step_2' THEN 1 ELSE 0 END) as reached_step_2,
    MAX(CASE WHEN event_name = 'step_3' THEN 1 ELSE 0 END) as reached_step_3,
    MAX(CASE WHEN event_name = 'step_4' THEN 1 ELSE 0 END) as reached_step_4,
    MAX(CASE WHEN event_name = 'conversion' THEN 1 ELSE 0 END) as converted
  FROM events
  WHERE event_date >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY 1
),
abandonment_points AS (
  SELECT
    user_id,
    CASE
      WHEN converted = 1 THEN 'Completed'
      WHEN reached_step_4 = 1 THEN 'Abandoned at Step 4'
      WHEN reached_step_3 = 1 THEN 'Abandoned at Step 3'
      WHEN reached_step_2 = 1 THEN 'Abandoned at Step 2'
      WHEN reached_step_1 = 1 THEN 'Abandoned at Step 1'
      ELSE 'Did not start'
    END as abandonment_point
  FROM funnel_progress
)
SELECT
  abandonment_point,
  COUNT(*) as user_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM abandonment_points
GROUP BY 1
ORDER BY user_count DESC;
```

## Funnel Visualization

### Python Funnel Analysis

```python
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class FunnelAnalyzer:
    """Comprehensive funnel analysis toolkit"""

    def __init__(self, data):
        """
        Initialize with event data

        Args:
            data: DataFrame with columns [user_id, event_name, event_timestamp]
        """
        self.data = data.copy()
        self.data['event_timestamp'] = pd.to_datetime(self.data['event_timestamp'])

    def build_funnel(self, steps, time_window_hours=None):
        """
        Build funnel with specified steps

        Args:
            steps: List of event names in funnel order
            time_window_hours: Optional time window for funnel completion

        Returns:
            DataFrame with funnel metrics
        """
        user_events = self.data[self.data['event_name'].isin(steps)].copy()

        # Get first occurrence of each event per user
        first_events = user_events.groupby(['user_id', 'event_name'])[
            'event_timestamp'
        ].min().reset_index()

        # Pivot to wide format
        user_funnel = first_events.pivot(
            index='user_id',
            columns='event_name',
            values='event_timestamp'
        ).reset_index()

        # Check if steps occur in order and within time window
        funnel_metrics = []
        total_users = len(user_funnel)

        for i, step in enumerate(steps):
            if step not in user_funnel.columns:
                user_funnel[step] = pd.NaT

            # Count users who reached this step
            reached = user_funnel[step].notna().sum()

            # Calculate conversion from previous step
            if i == 0:
                conversion_from_previous = 100.0
                overall_conversion = 100.0
            else:
                previous_step = steps[i-1]
                previous_reached = user_funnel[previous_step].notna().sum()
                conversion_from_previous = (reached / previous_reached * 100) if previous_reached > 0 else 0
                overall_conversion = (reached / total_users * 100) if total_users > 0 else 0

            # Apply time window if specified
            if time_window_hours and i > 0:
                within_window = user_funnel[
                    (user_funnel[step].notna()) &
                    ((user_funnel[step] - user_funnel[steps[0]]) <= pd.Timedelta(hours=time_window_hours))
                ]
                reached = len(within_window)
                conversion_from_previous = (reached / previous_reached * 100) if previous_reached > 0 else 0
                overall_conversion = (reached / total_users * 100) if total_users > 0 else 0

            funnel_metrics.append({
                'step': step,
                'step_number': i + 1,
                'users': reached,
                'conversion_from_previous': conversion_from_previous,
                'overall_conversion': overall_conversion,
                'drop_off': 100 - conversion_from_previous if i > 0 else 0
            })

        return pd.DataFrame(funnel_metrics)

    def plot_funnel(self, funnel_df):
        """Create funnel visualization"""
        fig = go.Figure()

        fig.add_trace(go.Funnel(
            name='Users',
            y=funnel_df['step'],
            x=funnel_df['users'],
            textinfo="value+percent initial",
            marker={"color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"][:len(funnel_df)]}
        ))

        fig.update_layout(
            title="Conversion Funnel",
            height=500,
            showlegend=False
        )

        return fig

    def segment_funnel(self, steps, segment_col):
        """Compare funnels across segments"""
        segments = self.data[segment_col].unique()
        results = []

        for segment in segments:
            segment_data = self.data[self.data[segment_col] == segment]
            analyzer = FunnelAnalyzer(segment_data)
            segment_funnel = analyzer.build_funnel(steps)
            segment_funnel['segment'] = segment
            results.append(segment_funnel)

        return pd.concat(results, ignore_index=True)

    def time_to_convert(self, start_event, end_event):
        """Calculate time between funnel steps"""
        user_times = self.data[
            self.data['event_name'].isin([start_event, end_event])
        ].groupby(['user_id', 'event_name'])['event_timestamp'].min().unstack()

        if start_event in user_times.columns and end_event in user_times.columns:
            time_diff = (user_times[end_event] - user_times[start_event]).dt.total_seconds() / 3600

            return {
                'mean_hours': time_diff.mean(),
                'median_hours': time_diff.median(),
                'p25_hours': time_diff.quantile(0.25),
                'p75_hours': time_diff.quantile(0.75),
                'p90_hours': time_diff.quantile(0.90)
            }
        return None
```

## Funnel Optimization Framework

### 1. Identify Bottlenecks

```python
def identify_bottlenecks(funnel_df, threshold=0.3):
    """
    Identify funnel steps with high drop-off

    Args:
        funnel_df: DataFrame from build_funnel()
        threshold: Drop-off threshold to flag (default 30%)

    Returns:
        List of problematic steps
    """
    bottlenecks = funnel_df[
        funnel_df['drop_off'] > threshold * 100
    ][['step', 'drop_off', 'users']].to_dict('records')

    return bottlenecks
```

### 2. A/B Test Impact on Funnel

```sql
-- Compare funnel performance between test variants
SELECT
  variant,
  COUNT(DISTINCT user_id) as users,
  SUM(CASE WHEN step_1 THEN 1 ELSE 0 END) as step_1_count,
  SUM(CASE WHEN step_2 THEN 1 ELSE 0 END) as step_2_count,
  SUM(CASE WHEN step_3 THEN 1 ELSE 0 END) as step_3_count,
  SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions,
  ROUND(SUM(CASE WHEN converted THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT user_id), 2) as conversion_rate
FROM ab_test_funnels
GROUP BY 1
ORDER BY 7 DESC;
```

### 3. Time-Based Funnel Analysis

```sql
-- Funnel performance by time period
SELECT
  DATE_TRUNC('week', first_event_date) as week,
  COUNT(DISTINCT user_id) as entered_funnel,
  SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions,
  ROUND(SUM(CASE WHEN converted THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT user_id), 2) as conversion_rate,
  AVG(time_to_convert_hours) as avg_conversion_time
FROM funnel_summary
GROUP BY 1
ORDER BY 1 DESC;
```

## Best Practices

### Funnel Design
1. **Define Clear Steps**: Each step should be meaningful and measurable
2. **Limit Funnel Depth**: 3-7 steps typically optimal
3. **Consider Time Windows**: Set realistic conversion windows
4. **Account for Sequences**: Decide if order matters
5. **Handle Re-entries**: Decide how to count repeat attempts

### Analysis Approach
1. **Start Broad**: Look at overall funnel first
2. **Segment Deep**: Break down by relevant dimensions
3. **Track Trends**: Monitor over time
4. **Identify Patterns**: Look for day-of-week, time-of-day effects
5. **Measure Velocityuate**: How long does conversion take?

### Optimization Strategy
1. **Prioritize**: Focus on steps with biggest impact
2. **Test Hypotheses**: A/B test improvements
3. **Remove Friction**: Simplify complex steps
4. **Add Clarity**: Improve messaging and CTAs
5. **Reduce Steps**: Combine when possible

## Common Pitfalls

- Mixing time periods (comparing unequal cohorts)
- Not accounting for user re-entry
- Ignoring statistical significance in small samples
- Over-optimizing early funnel at expense of late funnel
- Not segmenting by quality (all users aren't equal)
- Forgetting to exclude test users/employees
- Not validating data accuracy

## Funnel Benchmarks

### E-commerce
- Browse to Cart: 10-20%
- Cart to Checkout: 40-60%
- Checkout to Purchase: 50-70%
- Overall Conversion: 2-4%

### SaaS
- Visitor to Signup: 5-15%
- Signup to Activation: 30-50%
- Activation to Paid: 2-5%
- Overall Conversion: 0.3-3%

### Mobile Apps
- Install to Open: 70-90%
- Open to Register: 25-40%
- Register to Active: 30-40%
- Overall to Active: 5-15%
