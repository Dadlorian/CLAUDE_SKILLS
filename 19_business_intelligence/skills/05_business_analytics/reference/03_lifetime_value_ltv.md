# Customer Lifetime Value (LTV) Reference

Comprehensive guide to calculating, analyzing, and optimizing customer lifetime value.

## Core LTV Concepts

### What is LTV?

**Definition**: The total revenue a business can expect from a single customer account throughout their relationship.

**Why It Matters**:
- Determines how much to spend on acquisition (CAC)
- Guides customer retention investments
- Informs product and pricing strategy
- Drives customer segmentation
- Enables revenue forecasting

## LTV Calculation Methods

### 1. Historical LTV (Actual)

**Simple Average**:
```sql
-- Average revenue per customer (all-time)
SELECT
  AVG(total_revenue) as avg_ltv
FROM (
  SELECT
    user_id,
    SUM(revenue) as total_revenue
  FROM transactions
  GROUP BY 1
) customer_revenue;
```

**By Cohort**:
```sql
-- Historical LTV by signup cohort
SELECT
  DATE_TRUNC('month', u.signup_date) as cohort_month,
  COUNT(DISTINCT u.user_id) as customers,
  SUM(t.revenue) / COUNT(DISTINCT u.user_id) as avg_ltv,
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY customer_revenue.total_revenue
  ) as median_ltv
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
LEFT JOIN (
  SELECT user_id, SUM(revenue) as total_revenue
  FROM transactions
  GROUP BY 1
) customer_revenue ON u.user_id = customer_revenue.user_id
GROUP BY 1
ORDER BY 1;
```

### 2. Predictive LTV (Forward-Looking)

**Simple Formula**:
```
LTV = ARPU × Average Customer Lifespan
```

```sql
-- Simple predictive LTV
WITH customer_metrics AS (
  SELECT
    AVG(monthly_revenue) as arpu,
    AVG(lifespan_months) as avg_lifespan
  FROM (
    SELECT
      user_id,
      SUM(revenue) / COUNT(DISTINCT DATE_TRUNC('month', transaction_date)) as monthly_revenue,
      EXTRACT(MONTH FROM AGE(MAX(last_seen), MIN(signup_date))) as lifespan_months
    FROM customers
    GROUP BY 1
  ) customer_data
)
SELECT
  arpu,
  avg_lifespan,
  arpu * avg_lifespan as simple_ltv
FROM customer_metrics;
```

**Advanced Formula with Margins**:
```
LTV = (ARPU × Gross Margin) × (1 / Churn Rate)
```

```sql
-- LTV with gross margin and churn
WITH metrics AS (
  SELECT
    AVG(monthly_revenue) as arpu,
    AVG(gross_margin) as avg_margin,
    AVG(churn_rate) as monthly_churn_rate
  FROM (
    SELECT
      DATE_TRUNC('month', date) as month,
      SUM(revenue) / COUNT(DISTINCT user_id) as monthly_revenue,
      SUM(revenue - cost) / NULLIF(SUM(revenue), 0) as gross_margin,
      COUNT(DISTINCT CASE WHEN churned THEN user_id END) * 1.0 /
        COUNT(DISTINCT user_id) as churn_rate
    FROM customer_monthly_summary
    GROUP BY 1
  ) monthly_data
)
SELECT
  arpu,
  avg_margin,
  monthly_churn_rate,
  (arpu * avg_margin) * (1.0 / NULLIF(monthly_churn_rate, 0)) as ltv
FROM metrics;
```

### 3. Cohort-Based LTV Projection

```sql
-- Cumulative LTV by cohort over time
WITH cohort_revenue AS (
  SELECT
    DATE_TRUNC('month', u.signup_date) as cohort_month,
    DATE_TRUNC('month', t.transaction_date) as revenue_month,
    EXTRACT(MONTH FROM AGE(
      DATE_TRUNC('month', t.transaction_date),
      DATE_TRUNC('month', u.signup_date)
    )) as months_since_signup,
    COUNT(DISTINCT u.user_id) as cohort_size,
    SUM(t.revenue) / COUNT(DISTINCT u.user_id) as revenue_per_customer
  FROM users u
  LEFT JOIN transactions t ON u.user_id = t.user_id
  GROUP BY 1, 2, 3
)
SELECT
  cohort_month,
  months_since_signup,
  revenue_per_customer,
  SUM(revenue_per_customer) OVER (
    PARTITION BY cohort_month
    ORDER BY months_since_signup
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) as cumulative_ltv
FROM cohort_revenue
WHERE months_since_signup >= 0
ORDER BY 1, 2;
```

### 4. Discounted Cash Flow LTV

**Formula**:
```
LTV = Σ (Revenue_t × Margin) / (1 + Discount_Rate)^t
```

```python
def calculate_dcf_ltv(monthly_revenue, months, margin=0.8, discount_rate=0.01):
    """
    Calculate LTV using discounted cash flow method

    Args:
        monthly_revenue: List of expected monthly revenues
        months: Number of months to project
        margin: Gross margin (default 80%)
        discount_rate: Monthly discount rate (default 1%)

    Returns:
        Discounted LTV
    """
    ltv = 0
    for t in range(months):
        if t < len(monthly_revenue):
            revenue = monthly_revenue[t]
        else:
            # Use last known revenue for projection
            revenue = monthly_revenue[-1]

        discounted_value = (revenue * margin) / ((1 + discount_rate) ** t)
        ltv += discounted_value

    return ltv

# Example
monthly_rev = [100, 100, 95, 95, 90, 90, 85, 85, 80, 80, 75, 75]
ltv = calculate_dcf_ltv(monthly_rev, months=36, margin=0.75, discount_rate=0.01)
print(f"Discounted LTV: ${ltv:.2f}")
```

## LTV Segmentation

### By Customer Segment

```sql
-- LTV by customer segment
SELECT
  u.customer_segment,
  COUNT(DISTINCT u.user_id) as customers,
  AVG(cr.total_revenue) as avg_ltv,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY cr.total_revenue) as p25_ltv,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY cr.total_revenue) as median_ltv,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY cr.total_revenue) as p75_ltv,
  MAX(cr.total_revenue) as max_ltv
FROM users u
JOIN (
  SELECT
    user_id,
    SUM(revenue) as total_revenue
  FROM transactions
  GROUP BY 1
) cr ON u.user_id = cr.user_id
GROUP BY 1
ORDER BY 3 DESC;
```

### By Acquisition Channel

```sql
-- LTV by acquisition channel
SELECT
  u.acquisition_channel,
  COUNT(DISTINCT u.user_id) as customers,
  AVG(cr.total_revenue) as avg_ltv,
  AVG(cr.total_revenue) / NULLIF(AVG(u.acquisition_cost), 0) as ltv_cac_ratio,
  SUM(cr.total_revenue) - SUM(u.acquisition_cost) as total_profit
FROM users u
LEFT JOIN (
  SELECT user_id, SUM(revenue) as total_revenue
  FROM transactions
  GROUP BY 1
) cr ON u.user_id = cr.user_id
WHERE u.acquisition_channel IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;
```

### By Product/Plan

```sql
-- LTV by subscription plan
SELECT
  s.plan_name,
  s.plan_price,
  COUNT(DISTINCT s.user_id) as subscribers,
  AVG(metrics.ltv) as avg_ltv,
  AVG(metrics.lifetime_months) as avg_lifetime_months
FROM subscriptions s
JOIN (
  SELECT
    user_id,
    SUM(amount) as ltv,
    COUNT(DISTINCT DATE_TRUNC('month', payment_date)) as lifetime_months
  FROM payments
  GROUP BY 1
) metrics ON s.user_id = metrics.user_id
GROUP BY 1, 2
ORDER BY 4 DESC;
```

## LTV Components Analysis

### 1. Customer Lifespan

```sql
-- Average customer lifespan
SELECT
  DATE_TRUNC('quarter', signup_date) as cohort,
  AVG(EXTRACT(DAY FROM (last_activity_date - signup_date))) / 30.0 as avg_lifespan_months,
  PERCENTILE_CONT(0.5) WITHIN GROUP (
    ORDER BY EXTRACT(DAY FROM (last_activity_date - signup_date))
  ) / 30.0 as median_lifespan_months
FROM users
WHERE last_activity_date IS NOT NULL
GROUP BY 1
ORDER BY 1;
```

### 2. Purchase Frequency

```sql
-- Purchase frequency analysis
SELECT
  user_id,
  COUNT(*) as total_purchases,
  MIN(purchase_date) as first_purchase,
  MAX(purchase_date) as last_purchase,
  EXTRACT(DAY FROM (MAX(purchase_date) - MIN(purchase_date))) as days_active,
  COUNT(*) * 30.0 / NULLIF(
    EXTRACT(DAY FROM (MAX(purchase_date) - MIN(purchase_date))), 0
  ) as purchases_per_month
FROM orders
GROUP BY 1
HAVING COUNT(*) > 1;
```

### 3. Average Order Value Over Time

```sql
-- AOV evolution during customer lifecycle
WITH customer_orders AS (
  SELECT
    user_id,
    order_date,
    order_value,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date) as order_number,
    EXTRACT(MONTH FROM AGE(order_date, first_order_date)) as months_since_first_order
  FROM (
    SELECT
      user_id,
      order_date,
      order_value,
      MIN(order_date) OVER (PARTITION BY user_id) as first_order_date
    FROM orders
  ) orders_with_first
)
SELECT
  CASE
    WHEN order_number = 1 THEN 'First Order'
    WHEN order_number BETWEEN 2 AND 5 THEN 'Orders 2-5'
    WHEN order_number BETWEEN 6 AND 10 THEN 'Orders 6-10'
    ELSE 'Orders 11+'
  END as order_group,
  COUNT(*) as num_orders,
  AVG(order_value) as avg_order_value,
  SUM(order_value) as total_value
FROM customer_orders
GROUP BY 1
ORDER BY MIN(order_number);
```

## LTV Prediction Models

### Machine Learning Approach

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

class LTVPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_features(self, df):
        """
        Prepare features for LTV prediction

        Features:
        - First purchase amount
        - Days since first purchase
        - Purchase frequency (first 30/60/90 days)
        - Average order value
        - Product categories purchased
        - Acquisition channel
        - Geographic data
        """
        features = pd.DataFrame()

        features['first_purchase_amount'] = df['first_purchase_amount']
        features['days_since_first_purchase'] = df['days_since_first_purchase']
        features['purchases_first_30d'] = df['purchases_first_30d']
        features['purchases_first_60d'] = df['purchases_first_60d']
        features['purchases_first_90d'] = df['purchases_first_90d']
        features['avg_order_value'] = df['avg_order_value']
        features['product_diversity'] = df['product_categories'].apply(len)

        # Encode categorical variables
        features = pd.get_dummies(
            features,
            columns=['acquisition_channel', 'country'],
            drop_first=True
        )

        return features

    def train(self, training_data):
        """Train LTV prediction model"""
        X = self.prepare_features(training_data)
        y = training_data['actual_ltv']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Model Performance:")
        print(f"MAE: ${mae:.2f}")
        print(f"R² Score: {r2:.3f}")

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return feature_importance

    def predict(self, customer_data):
        """Predict LTV for new customers"""
        X = self.prepare_features(customer_data)
        predictions = self.model.predict(X)
        return predictions
```

### Probabilistic LTV (Buy 'Til You Die Models)

```python
from lifetimes import BetaGeoFitter, GammaGammaFitter
import pandas as pd

def calculate_probabilistic_ltv(transaction_data, time_period=12):
    """
    Calculate LTV using BG/NBD and Gamma-Gamma models

    Args:
        transaction_data: DataFrame with columns [customer_id, transaction_date, revenue]
        time_period: Months to predict forward

    Returns:
        DataFrame with predicted LTV per customer
    """
    # Create RFM summary
    from lifetimes.utils import summary_data_from_transaction_data

    rfm = summary_data_from_transaction_data(
        transaction_data,
        'customer_id',
        'transaction_date',
        'revenue',
        observation_period_end='2024-12-31'
    )

    # Fit BG/NBD model (purchase frequency)
    bgf = BetaGeoFitter(penalizer_coef=0.0)
    bgf.fit(rfm['frequency'], rfm['recency'], rfm['T'])

    # Predict future purchases
    rfm['predicted_purchases'] = bgf.conditional_expected_number_of_purchases_up_to_time(
        time_period,
        rfm['frequency'],
        rfm['recency'],
        rfm['T']
    )

    # Fit Gamma-Gamma model (monetary value)
    # Only for customers with at least one repeat purchase
    returning_customers = rfm[rfm['frequency'] > 0]

    ggf = GammaGammaFitter(penalizer_coef=0.0)
    ggf.fit(
        returning_customers['frequency'],
        returning_customers['monetary_value']
    )

    # Predict CLV
    rfm['predicted_ltv'] = ggf.customer_lifetime_value(
        bgf,
        rfm['frequency'],
        rfm['recency'],
        rfm['T'],
        rfm['monetary_value'],
        time=time_period,
        discount_rate=0.01  # Monthly discount rate
    )

    return rfm[['predicted_purchases', 'predicted_ltv']]
```

## LTV Optimization Strategies

### 1. Increase Purchase Frequency

```sql
-- Identify customers with declining purchase frequency
WITH purchase_trends AS (
  SELECT
    user_id,
    AVG(CASE WHEN order_date >= CURRENT_DATE - INTERVAL '90 days'
             THEN 1 ELSE 0 END) * 30 as recent_frequency,
    AVG(CASE WHEN order_date BETWEEN CURRENT_DATE - INTERVAL '180 days'
             AND CURRENT_DATE - INTERVAL '90 days'
             THEN 1 ELSE 0 END) * 30 as previous_frequency
  FROM orders
  GROUP BY 1
  HAVING COUNT(*) > 3
)
SELECT
  user_id,
  recent_frequency,
  previous_frequency,
  (recent_frequency - previous_frequency) as frequency_change,
  (recent_frequency - previous_frequency) / NULLIF(previous_frequency, 0) * 100 as pct_change
FROM purchase_trends
WHERE previous_frequency > 0
  AND recent_frequency < previous_frequency * 0.7  -- 30% decline
ORDER BY 5;
```

### 2. Increase Average Order Value

```sql
-- AOV improvement opportunities
SELECT
  u.user_id,
  u.email,
  COUNT(DISTINCT o.order_id) as total_orders,
  AVG(o.order_value) as avg_order_value,
  MAX(o.order_value) as max_order_value,
  MAX(o.order_value) - AVG(o.order_value) as upsell_potential
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY 1, 2
HAVING COUNT(DISTINCT o.order_id) >= 3
  AND MAX(o.order_value) > AVG(o.order_value) * 1.5
ORDER BY 6 DESC
LIMIT 1000;
```

### 3. Extend Customer Lifespan

```sql
-- At-risk customers (potential churn)
WITH customer_activity AS (
  SELECT
    user_id,
    MAX(activity_date) as last_activity,
    AVG(days_between_activities) as avg_days_between_activity,
    EXTRACT(DAY FROM (CURRENT_DATE - MAX(activity_date))) as days_since_last_activity
  FROM (
    SELECT
      user_id,
      activity_date,
      activity_date - LAG(activity_date) OVER (
        PARTITION BY user_id ORDER BY activity_date
      ) as days_between_activities
    FROM user_activities
  ) activity_gaps
  GROUP BY 1
)
SELECT
  ca.user_id,
  ca.last_activity,
  ca.avg_days_between_activity,
  ca.days_since_last_activity,
  cr.total_revenue as current_ltv,
  CASE
    WHEN ca.days_since_last_activity > ca.avg_days_between_activity * 2 THEN 'High Risk'
    WHEN ca.days_since_last_activity > ca.avg_days_between_activity * 1.5 THEN 'Medium Risk'
    ELSE 'Low Risk'
  END as churn_risk
FROM customer_activity ca
JOIN (
  SELECT user_id, SUM(revenue) as total_revenue
  FROM transactions
  GROUP BY 1
) cr ON ca.user_id = cr.user_id
WHERE ca.days_since_last_activity > ca.avg_days_between_activity
ORDER BY ca.days_since_last_activity / ca.avg_days_between_activity DESC;
```

## LTV Benchmarks by Industry

### SaaS
- **B2B SaaS**: $1,000 - $50,000+
- **B2C SaaS**: $100 - $1,000
- **LTV:CAC Ratio**: 3:1 to 5:1
- **Payback Period**: 5-12 months

### E-commerce
- **Fashion**: $200 - $500
- **Electronics**: $300 - $800
- **Subscription Boxes**: $500 - $2,000
- **LTV:CAC Ratio**: 3:1
- **Payback Period**: 1-3 months

### Financial Services
- **Banking**: $2,000 - $10,000+
- **Insurance**: $1,500 - $5,000
- **Investment Apps**: $500 - $3,000

## LTV Reporting Dashboard

```sql
-- Executive LTV dashboard
WITH ltv_metrics AS (
  SELECT
    DATE_TRUNC('month', signup_date) as cohort_month,
    COUNT(DISTINCT user_id) as customers,
    SUM(total_revenue) / COUNT(DISTINCT user_id) as avg_ltv,
    SUM(total_revenue) as cohort_revenue,
    AVG(acquisition_cost) as avg_cac,
    SUM(total_revenue) / NULLIF(SUM(acquisition_cost), 0) as ltv_cac_ratio
  FROM (
    SELECT
      u.user_id,
      u.signup_date,
      u.acquisition_cost,
      COALESCE(SUM(t.revenue), 0) as total_revenue
    FROM users u
    LEFT JOIN transactions t ON u.user_id = t.user_id
    GROUP BY 1, 2, 3
  ) customer_ltv
  GROUP BY 1
)
SELECT
  cohort_month,
  customers,
  avg_ltv,
  avg_cac,
  ltv_cac_ratio,
  cohort_revenue,
  SUM(cohort_revenue) OVER (
    ORDER BY cohort_month
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) as cumulative_revenue
FROM ltv_metrics
ORDER BY 1 DESC;
```

## Key Formulas Summary

| Method | Formula | Use Case |
|--------|---------|----------|
| Simple LTV | Average Revenue per Customer | Quick estimate |
| Predictive LTV | ARPU × (1 / Churn Rate) | Subscription businesses |
| Margin-Adjusted | (ARPU × Margin) / Churn Rate | Unit economics |
| DCF LTV | Σ (Revenue_t × Margin) / (1 + r)^t | Sophisticated analysis |
| Historical | Total Revenue / Total Customers | Mature cohorts |

## Best Practices

1. **Use Multiple Methods**: Combine historical and predictive LTV
2. **Segment Analysis**: Calculate LTV by customer segment
3. **Regular Updates**: Recalculate as more data becomes available
4. **Cohort-Based**: Track LTV evolution by acquisition cohort
5. **Include Costs**: Factor in gross margin and CAC
6. **Time Boundaries**: Define time horizon for predictions
7. **Validate Predictions**: Compare predicted vs actual LTV
8. **Account for Churn**: Adjust for expected customer attrition

## Common Pitfalls

- Using too short a time period for historical LTV
- Ignoring customer heterogeneity (segments)
- Not accounting for gross margin
- Confusing average with median LTV
- Failing to discount future cash flows
- Not updating LTV calculations regularly
- Ignoring seasonal patterns
- Treating all customers equally
