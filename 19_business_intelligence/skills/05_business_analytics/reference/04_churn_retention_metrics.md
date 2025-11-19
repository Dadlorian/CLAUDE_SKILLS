# Churn and Retention Metrics Reference

Comprehensive guide to measuring, analyzing, and reducing customer churn while improving retention.

## Core Churn Metrics

### 1. Customer Churn Rate

**Definition**: Percentage of customers who stop doing business with you during a time period.

**Formula**: (Customers Lost / Customers at Start) × 100

```sql
-- Monthly customer churn rate
WITH monthly_customers AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    COUNT(DISTINCT CASE WHEN status = 'active'
          AND date = DATE_TRUNC('month', date) THEN user_id END) as customers_start,
    COUNT(DISTINCT CASE WHEN churned_date BETWEEN DATE_TRUNC('month', date)
          AND DATE_TRUNC('month', date) + INTERVAL '1 month' - INTERVAL '1 day'
          THEN user_id END) as customers_churned
  FROM customer_status_daily
  GROUP BY 1
)
SELECT
  month,
  customers_start,
  customers_churned,
  (customers_churned * 100.0 / NULLIF(customers_start, 0)) as churn_rate_pct
FROM monthly_customers
ORDER BY 1;
```

**Adjusted Churn** (accounting for new customers):
```sql
-- Churn rate excluding new customers acquired in period
WITH monthly_metrics AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    COUNT(DISTINCT CASE WHEN status = 'active'
          AND signup_date < DATE_TRUNC('month', date)
          THEN user_id END) as existing_customers_start,
    COUNT(DISTINCT CASE WHEN churned_date IS NOT NULL
          AND signup_date < DATE_TRUNC('month', churned_date)
          THEN user_id END) as existing_customers_churned
  FROM users
  GROUP BY 1
)
SELECT
  month,
  existing_customers_start,
  existing_customers_churned,
  (existing_customers_churned * 100.0 / NULLIF(existing_customers_start, 0)) as adjusted_churn_rate
FROM monthly_metrics
ORDER BY 1;
```

### 2. Revenue Churn (MRR Churn)

**Definition**: Percentage of recurring revenue lost due to churn and downgrades.

```sql
-- Monthly MRR churn
WITH mrr_movements AS (
  SELECT
    DATE_TRUNC('month', change_date) as month,
    SUM(CASE WHEN change_type = 'churned' THEN -mrr_change ELSE 0 END) as churned_mrr,
    SUM(CASE WHEN change_type = 'contraction' THEN -mrr_change ELSE 0 END) as contraction_mrr,
    SUM(CASE WHEN change_type = 'expansion' THEN mrr_change ELSE 0 END) as expansion_mrr,
    LAG(SUM(total_mrr)) OVER (ORDER BY DATE_TRUNC('month', change_date)) as starting_mrr
  FROM subscription_changes
  GROUP BY 1
)
SELECT
  month,
  starting_mrr,
  churned_mrr,
  contraction_mrr,
  expansion_mrr,
  (churned_mrr * 100.0 / NULLIF(starting_mrr, 0)) as gross_mrr_churn_pct,
  ((churned_mrr + contraction_mrr) * 100.0 / NULLIF(starting_mrr, 0)) as total_mrr_churn_pct,
  ((churned_mrr + contraction_mrr - expansion_mrr) * 100.0 / NULLIF(starting_mrr, 0)) as net_mrr_churn_pct
FROM mrr_movements
ORDER BY 1;
```

**Logo Churn vs Revenue Churn**:
```sql
-- Compare logo churn (customer count) vs revenue churn
SELECT
  month,
  customer_churn_pct,
  revenue_churn_pct,
  CASE
    WHEN revenue_churn_pct > customer_churn_pct
    THEN 'High-value customers churning'
    WHEN revenue_churn_pct < customer_churn_pct
    THEN 'Low-value customers churning'
    ELSE 'Proportional churn'
  END as churn_composition
FROM monthly_churn_analysis
ORDER BY 1;
```

### 3. Retention Rate

**Definition**: Percentage of customers who remain active over a time period.

**Formula**: Retention Rate = 100% - Churn Rate

```sql
-- Classic retention rate
SELECT
  DATE_TRUNC('month', date) as month,
  COUNT(DISTINCT CASE WHEN status = 'active' THEN user_id END) as active_customers,
  COUNT(DISTINCT CASE WHEN status = 'active'
        AND user_id IN (
          SELECT user_id FROM customer_status
          WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
            AND status = 'active'
        ) THEN user_id END) as retained_customers,
  COUNT(DISTINCT CASE WHEN status = 'active'
        AND user_id IN (
          SELECT user_id FROM customer_status
          WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
            AND status = 'active'
        ) THEN user_id END) * 100.0 /
    NULLIF(COUNT(DISTINCT CASE WHEN status = 'active' THEN user_id END), 0) as retention_rate
FROM customer_status
GROUP BY 1
ORDER BY 1;
```

### 4. Cohort Retention

**Definition**: Percentage of a cohort that remains active over time.

```sql
-- Cohort retention analysis
WITH cohorts AS (
  SELECT
    user_id,
    DATE_TRUNC('month', signup_date) as cohort_month
  FROM users
),
cohort_activity AS (
  SELECT
    c.cohort_month,
    DATE_TRUNC('month', a.activity_date) as activity_month,
    EXTRACT(MONTH FROM AGE(
      DATE_TRUNC('month', a.activity_date),
      c.cohort_month
    )) as months_since_signup,
    COUNT(DISTINCT a.user_id) as active_users
  FROM cohorts c
  JOIN user_activity a ON c.user_id = a.user_id
  WHERE a.activity_date >= c.cohort_month
  GROUP BY 1, 2, 3
),
cohort_sizes AS (
  SELECT
    cohort_month,
    COUNT(DISTINCT user_id) as cohort_size
  FROM cohorts
  GROUP BY 1
)
SELECT
  ca.cohort_month,
  ca.months_since_signup,
  cs.cohort_size,
  ca.active_users,
  (ca.active_users * 100.0 / cs.cohort_size) as retention_rate
FROM cohort_activity ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
ORDER BY 1, 2;
```

**Visualization-Ready Cohort Table**:
```sql
-- Cohort retention table (pivot format)
SELECT
  cohort_month,
  MAX(CASE WHEN months_since_signup = 0 THEN retention_rate END) as month_0,
  MAX(CASE WHEN months_since_signup = 1 THEN retention_rate END) as month_1,
  MAX(CASE WHEN months_since_signup = 2 THEN retention_rate END) as month_2,
  MAX(CASE WHEN months_since_signup = 3 THEN retention_rate END) as month_3,
  MAX(CASE WHEN months_since_signup = 6 THEN retention_rate END) as month_6,
  MAX(CASE WHEN months_since_signup = 12 THEN retention_rate END) as month_12
FROM cohort_retention_data
GROUP BY 1
ORDER BY 1 DESC;
```

## Advanced Retention Metrics

### 5. N-Day Retention

**Definition**: Percentage of users active exactly N days after signup.

```sql
-- Day 1, 7, 30 retention
WITH user_cohorts AS (
  SELECT
    user_id,
    DATE(signup_date) as signup_date
  FROM users
),
retention_days AS (
  SELECT
    uc.signup_date,
    COUNT(DISTINCT uc.user_id) as cohort_size,
    COUNT(DISTINCT CASE WHEN a.activity_date = uc.signup_date + INTERVAL '1 day'
          THEN uc.user_id END) as day_1_retained,
    COUNT(DISTINCT CASE WHEN a.activity_date = uc.signup_date + INTERVAL '7 days'
          THEN uc.user_id END) as day_7_retained,
    COUNT(DISTINCT CASE WHEN a.activity_date = uc.signup_date + INTERVAL '30 days'
          THEN uc.user_id END) as day_30_retained
  FROM user_cohorts uc
  LEFT JOIN activities a ON uc.user_id = a.user_id
  GROUP BY 1
)
SELECT
  DATE_TRUNC('week', signup_date) as week,
  AVG(day_1_retained * 100.0 / cohort_size) as avg_day_1_retention,
  AVG(day_7_retained * 100.0 / cohort_size) as avg_day_7_retention,
  AVG(day_30_retained * 100.0 / cohort_size) as avg_day_30_retention
FROM retention_days
GROUP BY 1
ORDER BY 1;
```

### 6. Rolling Retention

**Definition**: Percentage of users active on or after day N.

```sql
-- Rolling 7-day retention
WITH cohort_activity AS (
  SELECT
    DATE(u.signup_date) as cohort_date,
    u.user_id,
    MIN(DATE(a.activity_date)) as first_return_date,
    DATE(a.activity_date) - DATE(u.signup_date) as days_since_signup
  FROM users u
  LEFT JOIN activities a ON u.user_id = a.user_id
    AND DATE(a.activity_date) >= DATE(u.signup_date) + INTERVAL '7 days'
  GROUP BY 1, 2, 4
)
SELECT
  cohort_date,
  COUNT(DISTINCT user_id) as cohort_size,
  COUNT(DISTINCT CASE WHEN first_return_date IS NOT NULL THEN user_id END) as returned_users,
  COUNT(DISTINCT CASE WHEN first_return_date IS NOT NULL THEN user_id END) * 100.0 /
    COUNT(DISTINCT user_id) as rolling_7day_retention
FROM cohort_activity
GROUP BY 1
ORDER BY 1;
```

### 7. Unbounded Retention

**Definition**: Percentage active at any point during a time window.

```sql
-- Unbounded monthly retention
WITH monthly_activity AS (
  SELECT
    DATE_TRUNC('month', u.signup_date) as cohort_month,
    u.user_id,
    DATE_TRUNC('month', a.activity_date) as activity_month,
    EXTRACT(MONTH FROM AGE(
      DATE_TRUNC('month', a.activity_date),
      DATE_TRUNC('month', u.signup_date)
    )) as months_since_signup
  FROM users u
  JOIN activities a ON u.user_id = a.user_id
  WHERE a.activity_date >= u.signup_date
)
SELECT
  cohort_month,
  months_since_signup,
  COUNT(DISTINCT user_id) as active_users,
  COUNT(DISTINCT user_id) * 100.0 / FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (
    PARTITION BY cohort_month
    ORDER BY months_since_signup
  ) as unbounded_retention_rate
FROM monthly_activity
GROUP BY 1, 2
ORDER BY 1, 2;
```

## Churn Prediction

### 8. Churn Risk Scoring

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

class ChurnPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = None

    def create_features(self, df):
        """
        Create features for churn prediction

        Features:
        - Recency: Days since last activity
        - Frequency: Number of activities in last 30/60/90 days
        - Engagement: Active days percentage
        - Monetary: Revenue metrics
        - Product usage: Features used, depth of usage
        - Support: Tickets opened, NPS score
        """
        features = pd.DataFrame()

        # Recency features
        features['days_since_last_activity'] = df['days_since_last_activity']
        features['days_since_last_purchase'] = df['days_since_last_purchase']

        # Frequency features
        features['activities_last_30d'] = df['activities_last_30d']
        features['activities_last_60d'] = df['activities_last_60d']
        features['purchases_last_30d'] = df['purchases_last_30d']

        # Engagement trends
        features['activity_trend'] = (
            df['activities_last_30d'] - df['activities_30_60d_ago']
        )
        features['pct_days_active_last_month'] = df['pct_days_active_last_month']

        # Monetary features
        features['total_revenue'] = df['total_revenue']
        features['avg_order_value'] = df['avg_order_value']
        features['revenue_trend'] = (
            df['revenue_last_30d'] - df['revenue_30_60d_ago']
        )

        # Product usage
        features['features_used'] = df['features_used']
        features['feature_usage_depth'] = df['feature_usage_depth']

        # Customer service
        features['support_tickets'] = df['support_tickets']
        features['nps_score'] = df['nps_score'].fillna(0)

        # Tenure
        features['customer_age_days'] = df['customer_age_days']

        self.feature_names = features.columns.tolist()
        return features

    def train(self, training_data):
        """Train churn prediction model"""
        X = self.create_features(training_data)
        y = training_data['churned']  # 1 = churned, 0 = retained

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]

        print("Classification Report:")
        print(classification_report(y_test, y_pred))
        print(f"\nROC AUC Score: {roc_auc_score(y_test, y_prob):.3f}")

        # Feature importance
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\nTop 10 Features:")
        print(importance_df.head(10))

        return importance_df

    def predict_churn_probability(self, customer_data):
        """Predict churn probability for customers"""
        X = self.create_features(customer_data)
        churn_probabilities = self.model.predict_proba(X)[:, 1]

        results = customer_data[['user_id']].copy()
        results['churn_probability'] = churn_probabilities
        results['churn_risk_category'] = pd.cut(
            churn_probabilities,
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low', 'Medium', 'High']
        )

        return results
```

### 9. Survival Analysis

```python
from lifetimes import KaplanMeierFitter
import matplotlib.pyplot as plt

def survival_analysis(customer_data):
    """
    Analyze customer survival/retention over time using Kaplan-Meier

    Args:
        customer_data: DataFrame with columns [duration, churned]
            duration: time customer has been active (in months)
            churned: 1 if churned, 0 if still active (censored)
    """
    kmf = KaplanMeierFitter()
    kmf.fit(
        durations=customer_data['duration'],
        event_observed=customer_data['churned']
    )

    # Plot survival curve
    plt.figure(figsize=(10, 6))
    kmf.plot_survival_function()
    plt.title('Customer Survival Curve')
    plt.xlabel('Months Since Signup')
    plt.ylabel('Probability of Survival (Retention)')
    plt.grid(True, alpha=0.3)

    # Calculate median survival time
    median_survival = kmf.median_survival_time_
    print(f"Median Customer Lifetime: {median_survival:.1f} months")

    # Survival probability at specific timepoints
    timepoints = [1, 3, 6, 12, 24]
    for t in timepoints:
        prob = kmf.predict(t)
        print(f"Retention at month {t}: {prob:.1%}")

    return kmf

# Survival by segment
def survival_by_segment(customer_data, segment_col='customer_tier'):
    """Compare survival curves across customer segments"""
    fig, ax = plt.subplots(figsize=(12, 6))

    for segment in customer_data[segment_col].unique():
        segment_data = customer_data[customer_data[segment_col] == segment]
        kmf = KaplanMeierFitter()
        kmf.fit(
            durations=segment_data['duration'],
            event_observed=segment_data['churned'],
            label=segment
        )
        kmf.plot_survival_function(ax=ax)

    plt.title(f'Customer Survival by {segment_col}')
    plt.xlabel('Months Since Signup')
    plt.ylabel('Retention Rate')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

## Churn Drivers Analysis

### 10. Churn Reason Analysis

```sql
-- Churn reasons distribution
SELECT
  churn_reason,
  COUNT(*) as churned_customers,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as pct_of_churn,
  AVG(customer_lifetime_days) as avg_lifetime_days,
  AVG(total_revenue) as avg_revenue_per_churned_customer
FROM churned_customers
WHERE churned_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1
ORDER BY 2 DESC;
```

### 11. Cohort Churn Comparison

```sql
-- Compare churn rates across cohorts
WITH cohort_churn AS (
  SELECT
    DATE_TRUNC('quarter', signup_date) as cohort,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN churned_date IS NOT NULL THEN 1 END) as churned_customers,
    COUNT(CASE WHEN churned_date IS NOT NULL THEN 1 END) * 100.0 /
      COUNT(*) as churn_rate,
    AVG(EXTRACT(DAY FROM (COALESCE(churned_date, CURRENT_DATE) - signup_date))) / 30.0
      as avg_lifetime_months
  FROM users
  WHERE signup_date >= CURRENT_DATE - INTERVAL '2 years'
  GROUP BY 1
)
SELECT
  cohort,
  total_customers,
  churned_customers,
  churn_rate,
  avg_lifetime_months,
  churn_rate - LAG(churn_rate) OVER (ORDER BY cohort) as churn_rate_change
FROM cohort_churn
ORDER BY 1;
```

### 12. Early Churn vs Late Churn

```sql
-- Analyze churn timing
SELECT
  CASE
    WHEN lifetime_days <= 30 THEN '0-30 days'
    WHEN lifetime_days <= 90 THEN '31-90 days'
    WHEN lifetime_days <= 180 THEN '91-180 days'
    WHEN lifetime_days <= 365 THEN '181-365 days'
    ELSE '365+ days'
  END as churn_timing,
  COUNT(*) as churned_count,
  AVG(total_revenue) as avg_revenue,
  AVG(lifetime_days) as avg_lifetime_days
FROM (
  SELECT
    user_id,
    EXTRACT(DAY FROM (churned_date - signup_date)) as lifetime_days,
    total_revenue
  FROM churned_customers
) churn_analysis
GROUP BY 1
ORDER BY MIN(lifetime_days);
```

## Retention Improvement Strategies

### Win-Back Campaigns

```sql
-- Identify win-back opportunities
WITH churned_high_value AS (
  SELECT
    user_id,
    email,
    churned_date,
    total_revenue,
    avg_order_value,
    EXTRACT(DAY FROM (CURRENT_DATE - churned_date)) as days_since_churn
  FROM churned_customers
  WHERE total_revenue > 1000  -- High lifetime value
    AND churned_date >= CURRENT_DATE - INTERVAL '90 days'
    AND churned_date <= CURRENT_DATE - INTERVAL '30 days'
)
SELECT *
FROM churned_high_value
ORDER BY total_revenue DESC;
```

### Engagement Interventions

```sql
-- Users needing engagement boost
WITH engagement_metrics AS (
  SELECT
    user_id,
    AVG(CASE WHEN activity_date >= CURRENT_DATE - INTERVAL '30 days'
             THEN 1 ELSE 0 END) as recent_activity,
    AVG(CASE WHEN activity_date BETWEEN CURRENT_DATE - INTERVAL '60 days'
             AND CURRENT_DATE - INTERVAL '30 days'
             THEN 1 ELSE 0 END) as previous_activity
  FROM user_daily_activity
  GROUP BY 1
)
SELECT
  u.user_id,
  u.email,
  u.segment,
  em.recent_activity,
  em.previous_activity,
  em.recent_activity - em.previous_activity as activity_change
FROM users u
JOIN engagement_metrics em ON u.user_id = em.user_id
WHERE em.recent_activity < em.previous_activity * 0.5  -- 50% drop in activity
  AND u.status = 'active'
ORDER BY activity_change;
```

## Key Metrics Summary

| Metric | Formula | Good Benchmark |
|--------|---------|----------------|
| Monthly Churn Rate | Churned / Customers at Start | < 5% (SaaS) |
| Annual Churn Rate | 1 - (1 - Monthly Churn)^12 | < 50% |
| MRR Churn | Churned MRR / Starting MRR | < 2% monthly |
| Net MRR Churn | (Churn + Contraction - Expansion) / Starting MRR | Negative (best) |
| Logo Retention | 1 - Customer Churn Rate | > 90% |
| Revenue Retention | 1 - Revenue Churn Rate | > 95% |
| Day 1 Retention | Active Day 1 / New Users | > 40% |
| Month 1 Retention | Active Month 1 / Cohort Size | > 30% |

## Best Practices

1. **Measure Both Customer and Revenue Churn**
2. **Track Leading Indicators** (engagement drops before churn)
3. **Cohort Analysis** shows trends better than aggregate metrics
4. **Segment Churn** by customer type, plan, channel
5. **Understand Why** customers churn (exit surveys, interviews)
6. **Predict Before It Happens** using churn models
7. **Act Quickly** on early warning signs
8. **Calculate Full Impact** (lost LTV, not just MRR)
9. **Benchmark Regularly** against industry standards
10. **Test Retention Initiatives** rigorously

## Retention Benchmarks by Industry

**SaaS**:
- SMB: 5-7% monthly churn
- Mid-market: 1-2% monthly churn
- Enterprise: < 1% monthly churn

**E-commerce**:
- Monthly: 60-80% month 1 retention
- Subscription boxes: 30-50% month 1

**Mobile Apps**:
- Day 1: 40-50%
- Day 7: 15-25%
- Day 30: 5-10%
