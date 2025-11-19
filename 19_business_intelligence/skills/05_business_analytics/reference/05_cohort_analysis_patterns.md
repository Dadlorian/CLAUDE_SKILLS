# Cohort Analysis Patterns Reference

Comprehensive guide to cohort analysis methodologies for understanding user behavior over time.

## What is Cohort Analysis?

**Definition**: Analyzing groups of users who share a common characteristic or experience within a defined time period.

**Why Use Cohorts**:
- Track behavior changes over time
- Identify product improvements impact
- Understand retention patterns
- Compare customer quality across segments
- Remove temporal biases from analysis

## Types of Cohorts

### 1. Time-Based Cohorts

**Acquisition Cohorts** (most common):
```sql
-- Monthly acquisition cohorts
SELECT
  DATE_TRUNC('month', signup_date) as cohort_month,
  COUNT(DISTINCT user_id) as cohort_size,
  AVG(total_revenue) as avg_revenue_per_user,
  AVG(lifetime_days) as avg_lifetime_days
FROM users
GROUP BY 1
ORDER BY 1 DESC;
```

**Activity Cohorts**:
```sql
-- Cohorts based on first activity date
SELECT
  DATE_TRUNC('week', first_activity_date) as cohort_week,
  COUNT(DISTINCT user_id) as cohort_size
FROM (
  SELECT
    user_id,
    MIN(activity_date) as first_activity_date
  FROM user_activities
  GROUP BY 1
) first_activities
GROUP BY 1
ORDER BY 1 DESC;
```

### 2. Behavioral Cohorts

**Feature Adoption Cohorts**:
```sql
-- Users who adopted a specific feature
WITH feature_adopters AS (
  SELECT DISTINCT
    user_id,
    MIN(event_date) as adoption_date
  FROM events
  WHERE event_name = 'premium_feature_used'
  GROUP BY 1
)
SELECT
  DATE_TRUNC('month', adoption_date) as adoption_cohort,
  COUNT(DISTINCT user_id) as adopters,
  AVG(total_revenue) as avg_revenue_post_adoption
FROM feature_adopters fa
JOIN user_metrics um ON fa.user_id = um.user_id
GROUP BY 1
ORDER BY 1;
```

**Purchase Behavior Cohorts**:
```sql
-- Cohorts by first purchase amount
SELECT
  CASE
    WHEN first_purchase_amount < 50 THEN '$0-$49'
    WHEN first_purchase_amount < 100 THEN '$50-$99'
    WHEN first_purchase_amount < 200 THEN '$100-$199'
    ELSE '$200+'
  END as purchase_cohort,
  COUNT(DISTINCT user_id) as cohort_size,
  AVG(total_lifetime_value) as avg_ltv,
  AVG(total_orders) as avg_orders_per_customer
FROM (
  SELECT
    user_id,
    first_purchase_amount,
    total_lifetime_value,
    total_orders
  FROM customer_summary
) customers
GROUP BY 1
ORDER BY MIN(first_purchase_amount);
```

### 3. Segment-Based Cohorts

**Channel Cohorts**:
```sql
-- Cohorts by acquisition channel
SELECT
  acquisition_channel,
  DATE_TRUNC('month', signup_date) as cohort_month,
  COUNT(DISTINCT user_id) as cohort_size,
  AVG(conversion_rate) as avg_conversion_rate,
  AVG(ltv) as avg_ltv
FROM users
WHERE acquisition_channel IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, 2;
```

## Standard Cohort Analysis Patterns

### 1. Retention Cohort Analysis

**Classic Retention Table**:
```sql
-- Cohort retention matrix
WITH user_cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('month', signup_date) as cohort_month
  FROM users
),
monthly_activity AS (
  SELECT DISTINCT
    user_id,
    DATE_TRUNC('month', activity_date) as activity_month
  FROM activities
),
cohort_activity AS (
  SELECT
    uc.cohort_month,
    ma.activity_month,
    EXTRACT(MONTH FROM AGE(ma.activity_month, uc.cohort_month)) as month_number,
    COUNT(DISTINCT ma.user_id) as active_users
  FROM user_cohorts uc
  LEFT JOIN monthly_activity ma ON uc.user_id = ma.user_id
  WHERE ma.activity_month >= uc.cohort_month
  GROUP BY 1, 2, 3
),
cohort_sizes AS (
  SELECT
    cohort_month,
    COUNT(DISTINCT user_id) as cohort_size
  FROM user_cohorts
  GROUP BY 1
)
SELECT
  ca.cohort_month,
  ca.month_number,
  cs.cohort_size,
  ca.active_users,
  ROUND(ca.active_users * 100.0 / cs.cohort_size, 2) as retention_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
ORDER BY 1, 2;
```

**Retention Curves**:
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_retention_curves(cohort_data):
    """
    Plot retention curves for multiple cohorts

    Args:
        cohort_data: DataFrame with columns [cohort_month, month_number, retention_pct]
    """
    plt.figure(figsize=(14, 8))

    # Plot each cohort as a line
    for cohort in cohort_data['cohort_month'].unique():
        cohort_subset = cohort_data[cohort_data['cohort_month'] == cohort]
        plt.plot(
            cohort_subset['month_number'],
            cohort_subset['retention_pct'],
            marker='o',
            label=cohort.strftime('%Y-%m'),
            alpha=0.7
        )

    plt.xlabel('Months Since Signup')
    plt.ylabel('Retention Rate (%)')
    plt.title('Cohort Retention Curves')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_cohort_heatmap(cohort_data):
    """Create a heatmap of cohort retention"""
    # Pivot data for heatmap
    heatmap_data = cohort_data.pivot(
        index='cohort_month',
        columns='month_number',
        values='retention_pct'
    )

    plt.figure(figsize=(16, 10))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        center=50,
        vmin=0,
        vmax=100,
        cbar_kws={'label': 'Retention %'}
    )
    plt.title('Cohort Retention Heatmap')
    plt.xlabel('Months Since Signup')
    plt.ylabel('Cohort Month')
    plt.tight_layout()
    plt.show()
```

### 2. Revenue Cohort Analysis

**Cumulative Revenue per Cohort**:
```sql
-- Cumulative revenue by cohort over time
WITH user_cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('month', signup_date) as cohort_month
  FROM users
),
cohort_revenue AS (
  SELECT
    uc.cohort_month,
    DATE_TRUNC('month', t.transaction_date) as revenue_month,
    EXTRACT(MONTH FROM AGE(
      DATE_TRUNC('month', t.transaction_date),
      uc.cohort_month
    )) as months_since_signup,
    SUM(t.amount) as revenue
  FROM user_cohorts uc
  JOIN transactions t ON uc.user_id = t.user_id
  WHERE t.transaction_date >= uc.cohort_month
  GROUP BY 1, 2, 3
),
cohort_sizes AS (
  SELECT
    cohort_month,
    COUNT(DISTINCT user_id) as cohort_size
  FROM user_cohorts
  GROUP BY 1
)
SELECT
  cr.cohort_month,
  cr.months_since_signup,
  cs.cohort_size,
  cr.revenue,
  cr.revenue / cs.cohort_size as revenue_per_user,
  SUM(cr.revenue) OVER (
    PARTITION BY cr.cohort_month
    ORDER BY cr.months_since_signup
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) / cs.cohort_size as cumulative_revenue_per_user
FROM cohort_revenue cr
JOIN cohort_sizes cs ON cr.cohort_month = cs.cohort_month
ORDER BY 1, 2;
```

**LTV Evolution by Cohort**:
```sql
-- Track how LTV has evolved across cohorts
WITH cohort_ltv AS (
  SELECT
    DATE_TRUNC('month', signup_date) as cohort_month,
    user_id,
    SUM(revenue) as lifetime_value,
    EXTRACT(MONTH FROM AGE(CURRENT_DATE, signup_date)) as customer_age_months
  FROM users u
  JOIN transactions t ON u.user_id = t.user_id
  GROUP BY 1, 2, 4
)
SELECT
  cohort_month,
  customer_age_months,
  COUNT(DISTINCT user_id) as customers,
  AVG(lifetime_value) as avg_ltv,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lifetime_value) as median_ltv,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY lifetime_value) as p90_ltv
FROM cohort_ltv
WHERE customer_age_months >= 6  -- At least 6 months old
GROUP BY 1, 2
ORDER BY 1, 2;
```

### 3. Engagement Cohort Analysis

**Feature Usage by Cohort**:
```sql
-- Track feature adoption across cohorts
WITH cohort_feature_usage AS (
  SELECT
    DATE_TRUNC('month', u.signup_date) as cohort_month,
    EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', e.event_date), DATE_TRUNC('month', u.signup_date)))
      as months_since_signup,
    e.feature_name,
    COUNT(DISTINCT e.user_id) as users_using_feature,
    COUNT(DISTINCT u.user_id) as cohort_size
  FROM users u
  LEFT JOIN events e ON u.user_id = e.user_id
    AND e.event_type = 'feature_usage'
  WHERE e.event_date >= u.signup_date
  GROUP BY 1, 2, 3
)
SELECT
  cohort_month,
  months_since_signup,
  feature_name,
  users_using_feature,
  cohort_size,
  ROUND(users_using_feature * 100.0 / cohort_size, 2) as adoption_rate
FROM cohort_feature_usage
ORDER BY 1, 2, 6 DESC;
```

**Session Frequency by Cohort**:
```sql
-- Average sessions per user by cohort age
SELECT
  DATE_TRUNC('month', u.signup_date) as cohort_month,
  EXTRACT(MONTH FROM AGE(CURRENT_DATE, u.signup_date)) as cohort_age_months,
  COUNT(DISTINCT u.user_id) as users,
  COUNT(s.session_id) / COUNT(DISTINCT u.user_id) as avg_total_sessions,
  COUNT(CASE WHEN s.session_date >= CURRENT_DATE - INTERVAL '30 days'
        THEN s.session_id END) / COUNT(DISTINCT u.user_id) as avg_sessions_last_30d
FROM users u
LEFT JOIN sessions s ON u.user_id = s.user_id
WHERE u.signup_date <= CURRENT_DATE - INTERVAL '3 months'  -- At least 3 months old
GROUP BY 1, 2
HAVING COUNT(DISTINCT u.user_id) >= 100  -- Minimum cohort size
ORDER BY 1, 2;
```

## Advanced Cohort Patterns

### 4. Triangulation Analysis

**Compare Cohort Metrics at Same Age**:
```sql
-- Compare month 3 metrics across different cohorts
WITH cohort_month_3_metrics AS (
  SELECT
    cohort_month,
    AVG(CASE WHEN months_since_signup = 3 THEN retention_rate END) as month_3_retention,
    AVG(CASE WHEN months_since_signup = 3 THEN revenue_per_user END) as month_3_revenue,
    AVG(CASE WHEN months_since_signup = 3 THEN avg_sessions END) as month_3_sessions
  FROM cohort_metrics
  GROUP BY 1
)
SELECT
  cohort_month,
  month_3_retention,
  month_3_revenue,
  month_3_sessions,
  month_3_retention - LAG(month_3_retention) OVER (ORDER BY cohort_month) as retention_change,
  month_3_revenue - LAG(month_3_revenue) OVER (ORDER BY cohort_month) as revenue_change
FROM cohort_month_3_metrics
ORDER BY 1;
```

### 5. Cohort Comparison Analysis

**A/B Test Impact on Cohorts**:
```sql
-- Compare cohorts before/after product change
WITH pre_change_cohorts AS (
  SELECT
    user_id,
    'pre_change' as cohort_type
  FROM users
  WHERE signup_date < '2024-06-01'
),
post_change_cohorts AS (
  SELECT
    user_id,
    'post_change' as cohort_type
  FROM users
  WHERE signup_date >= '2024-06-01'
),
all_cohorts AS (
  SELECT * FROM pre_change_cohorts
  UNION ALL
  SELECT * FROM post_change_cohorts
)
SELECT
  ac.cohort_type,
  EXTRACT(MONTH FROM AGE(a.activity_date, u.signup_date)) as months_since_signup,
  COUNT(DISTINCT a.user_id) * 100.0 / COUNT(DISTINCT u.user_id) as retention_rate,
  AVG(m.engagement_score) as avg_engagement,
  SUM(r.revenue) / COUNT(DISTINCT u.user_id) as revenue_per_user
FROM all_cohorts ac
JOIN users u ON ac.user_id = u.user_id
LEFT JOIN activities a ON u.user_id = a.user_id
LEFT JOIN metrics m ON u.user_id = m.user_id AND m.metric_date = a.activity_date
LEFT JOIN revenue r ON u.user_id = r.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
```

### 6. Multi-Dimensional Cohorts

**Cohort × Segment Analysis**:
```sql
-- Retention by cohort and customer segment
SELECT
  DATE_TRUNC('month', u.signup_date) as cohort_month,
  u.customer_segment,
  EXTRACT(MONTH FROM AGE(a.activity_month, DATE_TRUNC('month', u.signup_date))) as months_since_signup,
  COUNT(DISTINCT u.user_id) as cohort_segment_size,
  COUNT(DISTINCT a.user_id) as active_users,
  ROUND(COUNT(DISTINCT a.user_id) * 100.0 / COUNT(DISTINCT u.user_id), 2) as retention_rate
FROM users u
LEFT JOIN (
  SELECT DISTINCT user_id, DATE_TRUNC('month', activity_date) as activity_month
  FROM activities
) a ON u.user_id = a.user_id AND a.activity_month >= DATE_TRUNC('month', u.signup_date)
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
```

## Cohort Analysis Best Practices

### Data Preparation

```python
class CohortAnalyzer:
    """Comprehensive cohort analysis toolkit"""

    def __init__(self, df, user_id_col, date_col):
        """
        Initialize cohort analyzer

        Args:
            df: DataFrame with user activity data
            user_id_col: Name of user ID column
            date_col: Name of date column
        """
        self.df = df.copy()
        self.user_id_col = user_id_col
        self.date_col = date_col
        self.df[date_col] = pd.to_datetime(self.df[date_col])

    def create_cohorts(self, cohort_period='M'):
        """
        Create cohort assignments

        Args:
            cohort_period: 'D' (daily), 'W' (weekly), 'M' (monthly), 'Q' (quarterly)
        """
        cohort_df = self.df.groupby(self.user_id_col)[self.date_col].min().reset_index()
        cohort_df.columns = [self.user_id_col, 'cohort_date']
        cohort_df['cohort'] = cohort_df['cohort_date'].dt.to_period(cohort_period)

        self.df = self.df.merge(cohort_df, on=self.user_id_col)
        return self

    def calculate_cohort_periods(self, period='M'):
        """Calculate periods since cohort start"""
        self.df['activity_period'] = self.df[self.date_col].dt.to_period(period)
        self.df['cohort_period'] = self.df['cohort'].astype(str).apply(
            lambda x: pd.Period(x, freq=period)
        )
        self.df['periods_since_cohort'] = (
            self.df['activity_period'] - self.df['cohort_period']
        ).apply(lambda x: x.n)
        return self

    def retention_table(self):
        """Generate retention table"""
        # Count unique users per cohort-period combination
        cohort_data = self.df.groupby(['cohort', 'periods_since_cohort'])[
            self.user_id_col
        ].nunique().reset_index()

        # Get cohort sizes
        cohort_sizes = self.df.groupby('cohort')[self.user_id_col].nunique()

        # Calculate retention rates
        cohort_data['cohort_size'] = cohort_data['cohort'].map(cohort_sizes)
        cohort_data['retention_rate'] = (
            cohort_data[self.user_id_col] / cohort_data['cohort_size'] * 100
        )

        # Pivot for heatmap format
        retention_table = cohort_data.pivot_table(
            index='cohort',
            columns='periods_since_cohort',
            values='retention_rate'
        )

        return retention_table

    def revenue_table(self, revenue_col):
        """Generate revenue per user table"""
        cohort_revenue = self.df.groupby(['cohort', 'periods_since_cohort']).agg({
            self.user_id_col: 'nunique',
            revenue_col: 'sum'
        }).reset_index()

        cohort_sizes = self.df.groupby('cohort')[self.user_id_col].nunique()
        cohort_revenue['cohort_size'] = cohort_revenue['cohort'].map(cohort_sizes)
        cohort_revenue['revenue_per_user'] = (
            cohort_revenue[revenue_col] / cohort_revenue['cohort_size']
        )

        revenue_table = cohort_revenue.pivot_table(
            index='cohort',
            columns='periods_since_cohort',
            values='revenue_per_user'
        )

        return revenue_table

    def cumulative_metrics(self, metric_col):
        """Calculate cumulative metrics per cohort"""
        cohort_data = self.df.groupby(['cohort', 'periods_since_cohort']).agg({
            self.user_id_col: 'nunique',
            metric_col: 'sum'
        }).reset_index()

        cohort_sizes = self.df.groupby('cohort')[self.user_id_col].nunique()
        cohort_data['cohort_size'] = cohort_data['cohort'].map(cohort_sizes)
        cohort_data['metric_per_user'] = (
            cohort_data[metric_col] / cohort_data['cohort_size']
        )

        # Calculate cumulative
        cohort_data['cumulative_metric'] = cohort_data.groupby('cohort')[
            'metric_per_user'
        ].cumsum()

        return cohort_data
```

## Interpretation Guidelines

### Reading Retention Cohorts

**Horizontal Reading (Cohort Performance)**:
- Read across a row to see how a single cohort retains over time
- Steeper drop indicates faster churn
- Flattening curve suggests stable retained base

**Vertical Reading (Time Period Comparison)**:
- Read down a column to compare cohorts at same age
- Improving metrics indicate product/market improvements
- Declining metrics signal issues to investigate

**Diagonal Reading (Current State)**:
- Recent cohorts at early stages, older cohorts at later stages
- Helps understand overall business health

### Key Questions to Ask

1. **Are newer cohorts performing better?**
   - If yes: Product improvements working
   - If no: Investigate customer quality or market fit

2. **At what point do cohorts stabilize?**
   - Identify when retention curve flattens
   - Informs payback period and LTV calculations

3. **Which cohorts have highest LTV?**
   - May indicate seasonality or successful campaigns
   - Guide future acquisition strategies

4. **How do segments compare within cohorts?**
   - Identify high-value segments
   - Optimize for quality over quantity

## Common Pitfalls

1. **Too Many Small Cohorts**: Insufficient statistical power
2. **Survivorship Bias**: Only analyzing retained users
3. **Inappropriate Cohort Definitions**: Mixing different user types
4. **Ignoring Seasonality**: Calendar effects on behavior
5. **Not Accounting for Maturity**: Comparing cohorts of different ages
6. **Over-Aggregation**: Missing important segments
7. **Cherry-Picking Data**: Selecting favorable time periods

## Cohort Analysis Checklist

- [ ] Define clear cohort criteria
- [ ] Ensure sufficient cohort size (typically 100+ users)
- [ ] Use consistent time periods
- [ ] Track multiple metrics (retention, revenue, engagement)
- [ ] Compare cohorts at same maturity level
- [ ] Segment by meaningful dimensions
- [ ] Document methodology
- [ ] Validate data quality
- [ ] Consider external factors (seasonality, competition)
- [ ] Act on insights discovered
