# Product Analytics Reference

Comprehensive guide to measuring and analyzing product usage, engagement, and performance.

## Core Product Metrics

### 1. Active Users

**Daily Active Users (DAU)**:
```sql
-- Calculate DAU
SELECT
  DATE(event_timestamp) as date,
  COUNT(DISTINCT user_id) as dau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  AND event_type = 'activity'
GROUP BY 1
ORDER BY 1;
```

**Monthly Active Users (MAU)**:
```sql
-- Calculate MAU
SELECT
  DATE_TRUNC('month', event_timestamp) as month,
  COUNT(DISTINCT user_id) as mau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;
```

**Weekly Active Users (WAU)**:
```sql
-- Calculate WAU
SELECT
  DATE_TRUNC('week', event_timestamp) as week,
  COUNT(DISTINCT user_id) as wau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY 1
ORDER BY 1;
```

**DAU/MAU Ratio (Stickiness)**:
```sql
-- Calculate DAU/MAU ratio (stickiness metric)
WITH daily_active AS (
  SELECT
    DATE(event_timestamp) as date,
    user_id
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1, 2
),
monthly_active AS (
  SELECT
    DATE_TRUNC('month', event_timestamp) as month,
    user_id
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1, 2
)
SELECT
  da.date,
  COUNT(DISTINCT da.user_id) as dau,
  COUNT(DISTINCT ma.user_id) as mau,
  ROUND(COUNT(DISTINCT da.user_id) * 100.0 / NULLIF(COUNT(DISTINCT ma.user_id), 0), 2) as dau_mau_ratio
FROM daily_active da
CROSS JOIN monthly_active ma
WHERE DATE_TRUNC('month', da.date) = ma.month
GROUP BY 1
ORDER BY 1;
```

### 2. Engagement Metrics

**Session Duration**:
```sql
-- Average session duration
SELECT
  DATE(session_start) as date,
  COUNT(DISTINCT session_id) as sessions,
  AVG(EXTRACT(EPOCH FROM (session_end - session_start)) / 60) as avg_duration_minutes,
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM (session_end - session_start)) / 60
  ) as median_duration_minutes
FROM sessions
WHERE session_start >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1;
```

**Feature Adoption Rate**:
```sql
-- Feature adoption by active users
WITH active_users AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
),
feature_users AS (
  SELECT DISTINCT
    user_id,
    feature_name
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
    AND event_type = 'feature_usage'
)
SELECT
  fu.feature_name,
  COUNT(DISTINCT fu.user_id) as users_using_feature,
  COUNT(DISTINCT au.user_id) as total_active_users,
  ROUND(COUNT(DISTINCT fu.user_id) * 100.0 / COUNT(DISTINCT au.user_id), 2) as adoption_rate_pct
FROM active_users au
LEFT JOIN feature_users fu ON au.user_id = fu.user_id
WHERE fu.feature_name IS NOT NULL
GROUP BY 1
ORDER BY 4 DESC;
```

**Engagement Score**:
```python
def calculate_engagement_score(user_activity_df):
    """
    Calculate user engagement score based on multiple factors

    Args:
        user_activity_df: DataFrame with columns
            [user_id, days_active_last_30, sessions_last_30,
             features_used_last_30, actions_completed_last_30]

    Returns:
        DataFrame with engagement scores
    """
    import pandas as pd
    import numpy as np

    # Normalize each metric to 0-1 scale
    df = user_activity_df.copy()

    metrics = {
        'days_active_last_30': (0, 30),
        'sessions_last_30': (0, df['sessions_last_30'].quantile(0.95)),
        'features_used_last_30': (0, df['features_used_last_30'].max()),
        'actions_completed_last_30': (0, df['actions_completed_last_30'].quantile(0.95))
    }

    # Normalize and weight
    weights = {
        'days_active_last_30': 0.3,
        'sessions_last_30': 0.2,
        'features_used_last_30': 0.3,
        'actions_completed_last_30': 0.2
    }

    normalized_scores = []

    for metric, (min_val, max_val) in metrics.items():
        normalized = (df[metric] - min_val) / (max_val - min_val)
        normalized = normalized.clip(0, 1)  # Cap at 0 and 1
        weighted = normalized * weights[metric]
        normalized_scores.append(weighted)

    df['engagement_score'] = sum(normalized_scores) * 100  # Scale to 0-100

    # Categorize engagement
    df['engagement_level'] = pd.cut(
        df['engagement_score'],
        bins=[0, 25, 50, 75, 100],
        labels=['Low', 'Medium', 'High', 'Very High']
    )

    return df[['user_id', 'engagement_score', 'engagement_level']]
```

### 3. Feature Usage Patterns

**Feature Usage Frequency**:
```sql
-- How often is each feature used?
SELECT
  feature_name,
  COUNT(*) as total_uses,
  COUNT(DISTINCT user_id) as unique_users,
  COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_id), 0) as avg_uses_per_user,
  COUNT(DISTINCT session_id) as sessions_with_feature
FROM feature_events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY 2 DESC;
```

**Feature Co-Usage**:
```sql
-- Which features are used together?
WITH feature_pairs AS (
  SELECT
    a.session_id,
    a.feature_name as feature_a,
    b.feature_name as feature_b
  FROM feature_events a
  JOIN feature_events b
    ON a.session_id = b.session_id
    AND a.feature_name < b.feature_name  -- Avoid duplicates
  WHERE a.event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
  feature_a,
  feature_b,
  COUNT(DISTINCT session_id) as sessions_with_both,
  ROUND(
    COUNT(DISTINCT session_id) * 100.0 /
    (SELECT COUNT(DISTINCT session_id) FROM feature_events
     WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'),
    2
  ) as pct_of_sessions
FROM feature_pairs
GROUP BY 1, 2
HAVING COUNT(DISTINCT session_id) >= 100
ORDER BY 3 DESC
LIMIT 20;
```

**Feature Adoption Funnel**:
```sql
-- Track progression through feature discovery
WITH feature_progression AS (
  SELECT
    user_id,
    MIN(CASE WHEN feature_name = 'basic_feature' THEN event_timestamp END) as basic_time,
    MIN(CASE WHEN feature_name = 'intermediate_feature' THEN event_timestamp END) as intermediate_time,
    MIN(CASE WHEN feature_name = 'advanced_feature' THEN event_timestamp END) as advanced_time
  FROM feature_events
  GROUP BY 1
)
SELECT
  COUNT(*) as total_users,
  COUNT(basic_time) as reached_basic,
  COUNT(intermediate_time) as reached_intermediate,
  COUNT(advanced_time) as reached_advanced,
  ROUND(COUNT(basic_time) * 100.0 / COUNT(*), 2) as basic_adoption_pct,
  ROUND(COUNT(intermediate_time) * 100.0 / NULLIF(COUNT(basic_time), 0), 2) as basic_to_intermediate_pct,
  ROUND(COUNT(advanced_time) * 100.0 / NULLIF(COUNT(intermediate_time), 0), 2) as intermediate_to_advanced_pct
FROM feature_progression;
```

## Activation Metrics

### Activation Rate

**Definition**: Percentage of users who complete key actions that indicate value realization.

```sql
-- Calculate activation rate
WITH new_users AS (
  SELECT
    user_id,
    signup_date,
    DATE_TRUNC('week', signup_date) as signup_week
  FROM users
  WHERE signup_date >= CURRENT_DATE - INTERVAL '12 weeks'
),
activated_users AS (
  SELECT DISTINCT
    nu.user_id,
    nu.signup_week,
    CASE WHEN
      -- Define activation criteria (customize based on product)
      COUNT(DISTINCT CASE WHEN e.event_type = 'key_action_1' THEN e.event_id END) >= 1 AND
      COUNT(DISTINCT CASE WHEN e.event_type = 'key_action_2' THEN e.event_id END) >= 1 AND
      COUNT(DISTINCT CASE WHEN e.event_type = 'key_action_3' THEN e.event_id END) >= 1
    THEN 1 ELSE 0 END as activated
  FROM new_users nu
  LEFT JOIN events e ON nu.user_id = e.user_id
    AND e.event_timestamp BETWEEN nu.signup_date AND nu.signup_date + INTERVAL '7 days'
  GROUP BY 1, 2
)
SELECT
  signup_week,
  COUNT(*) as new_users,
  SUM(activated) as activated_users,
  ROUND(SUM(activated) * 100.0 / COUNT(*), 2) as activation_rate_pct
FROM activated_users
GROUP BY 1
ORDER BY 1;
```

**Time to Activation**:
```sql
-- How long does it take users to activate?
WITH activations AS (
  SELECT
    u.user_id,
    u.signup_date,
    MIN(e.event_timestamp) as first_key_action_time
  FROM users u
  JOIN events e ON u.user_id = e.user_id
  WHERE e.event_type IN ('key_action_1', 'key_action_2', 'key_action_3')
    AND e.event_timestamp >= u.signup_date
  GROUP BY 1, 2
)
SELECT
  CASE
    WHEN EXTRACT(EPOCH FROM (first_key_action_time - signup_date)) / 3600 < 1 THEN 'Within 1 hour'
    WHEN EXTRACT(EPOCH FROM (first_key_action_time - signup_date)) / 3600 < 24 THEN '1-24 hours'
    WHEN EXTRACT(DAY FROM (first_key_action_time - signup_date)) <= 3 THEN '1-3 days'
    WHEN EXTRACT(DAY FROM (first_key_action_time - signup_date)) <= 7 THEN '4-7 days'
    ELSE '8+ days'
  END as time_to_activation,
  COUNT(*) as users,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM activations
GROUP BY 1
ORDER BY MIN(EXTRACT(EPOCH FROM (first_key_action_time - signup_date)));
```

## User Journey Analysis

### Path Analysis

```sql
-- Most common user paths (sequence of actions)
WITH user_paths AS (
  SELECT
    session_id,
    STRING_AGG(
      event_type,
      ' > '
      ORDER BY event_timestamp
    ) as path,
    COUNT(*) as steps
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY 1
)
SELECT
  path,
  COUNT(*) as frequency,
  AVG(steps) as avg_steps,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_paths
FROM user_paths
GROUP BY 1
HAVING COUNT(*) >= 100
ORDER BY 2 DESC
LIMIT 20;
```

**Sankey Diagram Data**:
```python
def generate_sankey_data(events_df, max_steps=5):
    """
    Generate data for Sankey diagram of user flows

    Args:
        events_df: DataFrame with [user_id, session_id, event_type, timestamp]
        max_steps: Maximum number of steps to include

    Returns:
        DataFrame with source, target, value for Sankey diagram
    """
    import pandas as pd

    # Sort by timestamp
    events_df = events_df.sort_values(['session_id', 'timestamp'])

    # Create step sequences
    paths = []
    for session, group in events_df.groupby('session_id'):
        events = group['event_type'].tolist()[:max_steps]
        for i in range(len(events) - 1):
            paths.append({
                'source': f"Step {i+1}: {events[i]}",
                'target': f"Step {i+2}: {events[i+1]}",
                'session_id': session
            })

    paths_df = pd.DataFrame(paths)

    # Aggregate flows
    sankey_data = paths_df.groupby(['source', 'target']).size().reset_index(name='value')

    return sankey_data
```

### Drop-off Analysis

```sql
-- Where do users drop off in key flows?
WITH flow_steps AS (
  SELECT
    user_id,
    MAX(CASE WHEN event_type = 'step_1' THEN 1 ELSE 0 END) as completed_step_1,
    MAX(CASE WHEN event_type = 'step_2' THEN 1 ELSE 0 END) as completed_step_2,
    MAX(CASE WHEN event_type = 'step_3' THEN 1 ELSE 0 END) as completed_step_3,
    MAX(CASE WHEN event_type = 'step_4' THEN 1 ELSE 0 END) as completed_step_4,
    MAX(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as converted
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
  GROUP BY 1
)
SELECT
  SUM(completed_step_1) as reached_step_1,
  SUM(completed_step_2) as reached_step_2,
  SUM(completed_step_3) as reached_step_3,
  SUM(completed_step_4) as reached_step_4,
  SUM(converted) as conversions,

  -- Drop-off rates
  ROUND((1 - SUM(completed_step_2) * 1.0 / NULLIF(SUM(completed_step_1), 0)) * 100, 2) as dropoff_step_1_pct,
  ROUND((1 - SUM(completed_step_3) * 1.0 / NULLIF(SUM(completed_step_2), 0)) * 100, 2) as dropoff_step_2_pct,
  ROUND((1 - SUM(completed_step_4) * 1.0 / NULLIF(SUM(completed_step_3), 0)) * 100, 2) as dropoff_step_3_pct,
  ROUND((1 - SUM(converted) * 1.0 / NULLIF(SUM(completed_step_4), 0)) * 100, 2) as dropoff_step_4_pct
FROM flow_steps;
```

## Product Health Metrics

### North Star Metric

**Definition**: The single metric that best captures core product value.

```python
# Examples of North Star metrics by product type:

NORTH_STAR_METRICS = {
    'Social Network': {
        'metric': 'DAU/MAU (Stickiness)',
        'calculation': 'Daily Active Users / Monthly Active Users'
    },
    'Marketplace': {
        'metric': 'Gross Merchandise Value (GMV)',
        'calculation': 'Total value of transactions'
    },
    'SaaS': {
        'metric': 'Weekly Active Teams',
        'calculation': 'Number of teams with at least 1 active user per week'
    },
    'Ecommerce': {
        'metric': 'Number of Purchases',
        'calculation': 'Count of completed orders'
    },
    'Media/Content': {
        'metric': 'Time Spent',
        'calculation': 'Total hours of content consumed'
    },
    'Communication': {
        'metric': 'Messages Sent',
        'calculation': 'Total messages sent by all users'
    }
}
```

```sql
-- Example: Calculate North Star metric (Weekly Active Teams for SaaS)
SELECT
  DATE_TRUNC('week', event_timestamp) as week,
  COUNT(DISTINCT team_id) as weekly_active_teams,
  COUNT(DISTINCT CASE WHEN action_type = 'core_action' THEN team_id END) as teams_with_core_action
FROM events e
JOIN users u ON e.user_id = u.user_id
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '12 weeks'
  AND event_type = 'activity'
GROUP BY 1
ORDER BY 1;
```

### Product-Market Fit Indicators

**Sean Ellis Test**:
```sql
-- "How would you feel if you could no longer use this product?"
-- >40% answering "Very disappointed" indicates PMF

SELECT
  response,
  COUNT(*) as respondents,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct
FROM survey_responses
WHERE question_id = 'pmf_question'
  AND survey_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1;
```

**Usage Intensity**:
```sql
-- High-frequency users indicate strong PMF
WITH user_frequency AS (
  SELECT
    user_id,
    COUNT(DISTINCT DATE(event_timestamp)) as days_active,
    DATE_TRUNC('month', MIN(event_timestamp)) as first_month
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1
)
SELECT
  CASE
    WHEN days_active >= 20 THEN 'Power Users (20+ days)'
    WHEN days_active >= 10 THEN 'Regular Users (10-19 days)'
    WHEN days_active >= 3 THEN 'Casual Users (3-9 days)'
    ELSE 'Rare Users (1-2 days)'
  END as user_type,
  COUNT(*) as users,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total
FROM user_frequency
GROUP BY 1
ORDER BY MIN(days_active) DESC;
```

## Feature Impact Analysis

### Before/After Comparison

```sql
-- Compare metrics before and after feature launch
WITH pre_launch AS (
  SELECT
    'Pre-Launch' as period,
    COUNT(DISTINCT user_id) as dau,
    COUNT(DISTINCT session_id) as sessions,
    AVG(session_duration_minutes) as avg_session_duration,
    SUM(conversions) as conversions
  FROM daily_metrics
  WHERE date BETWEEN '2024-01-01' AND '2024-01-31'  -- Month before launch
),
post_launch AS (
  SELECT
    'Post-Launch' as period,
    COUNT(DISTINCT user_id) as dau,
    COUNT(DISTINCT session_id) as sessions,
    AVG(session_duration_minutes) as avg_session_duration,
    SUM(conversions) as conversions
  FROM daily_metrics
  WHERE date BETWEEN '2024-02-01' AND '2024-02-29'  -- Month after launch
)
SELECT
  period,
  dau,
  sessions,
  avg_session_duration,
  conversions,
  dau - LAG(dau) OVER (ORDER BY period) as dau_change,
  ROUND((dau - LAG(dau) OVER (ORDER BY period)) * 100.0 /
        NULLIF(LAG(dau) OVER (ORDER BY period), 0), 2) as dau_change_pct
FROM (
  SELECT * FROM pre_launch
  UNION ALL
  SELECT * FROM post_launch
) combined;
```

### Cohort-Based Feature Impact

```python
def analyze_feature_impact_by_cohort(events_df, feature_launch_date):
    """
    Compare behavior of cohorts before/after feature launch

    Args:
        events_df: DataFrame with user events
        feature_launch_date: Date when feature was launched

    Returns:
        DataFrame comparing cohort metrics
    """
    import pandas as pd

    events_df['cohort'] = pd.to_datetime(events_df['signup_date']).apply(
        lambda x: 'Pre-Feature' if x < feature_launch_date else 'Post-Feature'
    )

    cohort_metrics = events_df.groupby('cohort').agg({
        'user_id': 'nunique',
        'session_id': 'nunique',
        'event_id': 'count',
        'revenue': 'sum'
    }).reset_index()

    cohort_metrics.columns = ['cohort', 'users', 'sessions', 'events', 'revenue']

    cohort_metrics['sessions_per_user'] = cohort_metrics['sessions'] / cohort_metrics['users']
    cohort_metrics['events_per_session'] = cohort_metrics['events'] / cohort_metrics['sessions']
    cohort_metrics['revenue_per_user'] = cohort_metrics['revenue'] / cohort_metrics['users']

    return cohort_metrics
```

## Best Practices

1. **Focus on Outcomes, Not Outputs**: Track what users accomplish, not just what they click
2. **Segment Everything**: Different user segments have different behaviors
3. **Track Leading Indicators**: Metrics that predict future performance
4. **Monitor Lagging Indicators**: Metrics that show historical performance
5. **Validate Instrumentation**: Ensure tracking is accurate and complete
6. **Consider Context**: External factors (seasonality, marketing, competition)
7. **Prioritize Actionability**: Metrics should drive decisions
8. **Avoid Vanity Metrics**: Total users, page views without context

## Key Product Analytics Frameworks

### AARRR (Pirate Metrics)
- **Acquisition**: How users find you
- **Activation**: First good experience
- **Retention**: Users come back
- **Revenue**: Monetization
- **Referral**: Users refer others

### HEART Framework (Google)
- **Happiness**: User satisfaction (NPS, surveys)
- **Engagement**: Level of involvement (DAU, sessions)
- **Adoption**: New feature usage
- **Retention**: Repeat usage over time
- **Task Success**: Can users accomplish goals?

## Product Analytics Stack

```python
# Typical product analytics tooling

ANALYTICS_TOOLS = {
    'Event Tracking': ['Segment', 'mParticle', 'RudderStack'],
    'Product Analytics': ['Amplitude', 'Mixpanel', 'Heap', 'Pendo'],
    'Session Replay': ['FullStory', 'LogRocket', 'Hotjar'],
    'Experimentation': ['Optimizely', 'LaunchDarkly', 'Split'],
    'Data Warehouse': ['Snowflake', 'BigQuery', 'Redshift'],
    'BI/Visualization': ['Looker', 'Tableau', 'Mode']
}
```

## Common Metrics by Product Type

**SaaS**:
- Monthly Active Users (MAU)
- Weekly Active Users (WAU)
- Feature adoption rate
- Time to value
- Customer lifetime value

**E-commerce**:
- Conversion rate
- Average order value
- Cart abandonment rate
- Product views to purchase
- Repeat purchase rate

**Marketplace**:
- Gross Merchandise Value (GMV)
- Take rate
- Liquidity (supply/demand balance)
- Time to first transaction
- Repeat transaction rate

**Social/Content**:
- Daily Active Users (DAU)
- Content creation rate
- Engagement rate (likes, shares, comments)
- Time spent
- Virality coefficient
