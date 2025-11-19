# Revenue Metrics Reference

Comprehensive guide to measuring and analyzing revenue across different business models.

## Core Revenue Metrics

### 1. Monthly Recurring Revenue (MRR)

**Definition**: Predictable revenue generated each month from subscriptions.

```sql
-- Basic MRR calculation
SELECT
  DATE_TRUNC('month', billing_date) as month,
  SUM(subscription_amount) as mrr
FROM subscriptions
WHERE status = 'active'
  AND billing_cycle = 'monthly'
GROUP BY 1
ORDER BY 1;
```

**Components**:
- **New MRR**: Revenue from new customers
- **Expansion MRR**: Revenue from upgrades/upsells
- **Contraction MRR**: Lost revenue from downgrades
- **Churned MRR**: Lost revenue from cancellations

```sql
-- MRR movements
WITH mrr_changes AS (
  SELECT
    user_id,
    DATE_TRUNC('month', change_date) as month,
    CASE
      WHEN previous_mrr = 0 AND current_mrr > 0 THEN 'new'
      WHEN previous_mrr > 0 AND current_mrr = 0 THEN 'churned'
      WHEN current_mrr > previous_mrr THEN 'expansion'
      WHEN current_mrr < previous_mrr THEN 'contraction'
      ELSE 'retained'
    END as movement_type,
    current_mrr - previous_mrr as mrr_change
  FROM subscription_changes
)
SELECT
  month,
  movement_type,
  SUM(mrr_change) as total_change,
  COUNT(DISTINCT user_id) as customer_count
FROM mrr_changes
GROUP BY 1, 2
ORDER BY 1, 2;
```

### 2. Annual Recurring Revenue (ARR)

**Definition**: MRR multiplied by 12, or sum of annual contract values.

```sql
-- ARR calculation
SELECT
  DATE_TRUNC('year', contract_date) as year,
  SUM(
    CASE
      WHEN billing_cycle = 'monthly' THEN amount * 12
      WHEN billing_cycle = 'quarterly' THEN amount * 4
      WHEN billing_cycle = 'annual' THEN amount
    END
  ) as arr
FROM contracts
WHERE status IN ('active', 'trial')
GROUP BY 1
ORDER BY 1;
```

**Key Metrics**:
- **ARR Growth Rate**: (Current ARR - Previous ARR) / Previous ARR
- **Net New ARR**: New + Expansion - Contraction - Churn
- **ARR per Customer**: Total ARR / Number of Customers

### 3. Revenue Growth Rate

**Month-over-Month (MoM)**:
```sql
SELECT
  current_month,
  current_revenue,
  previous_revenue,
  ((current_revenue - previous_revenue) / previous_revenue) * 100 as mom_growth_pct
FROM (
  SELECT
    DATE_TRUNC('month', date) as current_month,
    SUM(revenue) as current_revenue,
    LAG(SUM(revenue)) OVER (ORDER BY DATE_TRUNC('month', date)) as previous_revenue
  FROM transactions
  GROUP BY 1
) growth;
```

**Year-over-Year (YoY)**:
```sql
SELECT
  current_month,
  current_revenue,
  prior_year_revenue,
  ((current_revenue - prior_year_revenue) / prior_year_revenue) * 100 as yoy_growth_pct
FROM (
  SELECT
    DATE_TRUNC('month', date) as current_month,
    SUM(revenue) as current_revenue,
    LAG(SUM(revenue), 12) OVER (ORDER BY DATE_TRUNC('month', date)) as prior_year_revenue
  FROM transactions
  GROUP BY 1
) growth;
```

**Compound Annual Growth Rate (CAGR)**:
```python
def calculate_cagr(beginning_value, ending_value, num_years):
    """Calculate Compound Annual Growth Rate"""
    return ((ending_value / beginning_value) ** (1 / num_years) - 1) * 100

# Example
beginning_arr = 1000000
ending_arr = 5000000
years = 3
cagr = calculate_cagr(beginning_arr, ending_arr, years)
print(f"CAGR: {cagr:.2f}%")  # Output: 71.00%
```

### 4. Average Revenue Per User (ARPU)

**Definition**: Total revenue divided by number of users.

```sql
-- ARPU calculation
SELECT
  DATE_TRUNC('month', date) as month,
  SUM(revenue) / COUNT(DISTINCT user_id) as arpu
FROM transactions
GROUP BY 1
ORDER BY 1;
```

**By Segment**:
```sql
-- ARPU by customer segment
SELECT
  DATE_TRUNC('month', t.date) as month,
  u.segment,
  SUM(t.revenue) / COUNT(DISTINCT t.user_id) as arpu,
  COUNT(DISTINCT t.user_id) as paying_users
FROM transactions t
JOIN users u ON t.user_id = u.id
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Related Metrics**:
- **ARPPU** (Average Revenue Per Paying User)
- **ARPDAU** (Average Revenue Per Daily Active User)
- **ARPMAU** (Average Revenue Per Monthly Active User)

### 5. Revenue Per Employee

**Definition**: Total revenue divided by number of employees.

```sql
-- Revenue per employee
WITH monthly_revenue AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    SUM(revenue) as total_revenue
  FROM transactions
  GROUP BY 1
),
employee_count AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    AVG(headcount) as avg_employees
  FROM headcount_daily
  GROUP BY 1
)
SELECT
  r.month,
  r.total_revenue,
  e.avg_employees,
  r.total_revenue / e.avg_employees as revenue_per_employee
FROM monthly_revenue r
JOIN employee_count e ON r.month = e.month
ORDER BY 1;
```

### 6. Bookings vs Revenue

**Bookings**: Total value of contracts signed
**Revenue**: Recognized revenue (GAAP/accrual basis)

```sql
-- Bookings vs Revenue
SELECT
  DATE_TRUNC('month', contract_date) as month,
  SUM(contract_value) as total_bookings,
  SUM(
    CASE
      WHEN contract_term_months > 0
      THEN contract_value / contract_term_months
      ELSE contract_value
    END
  ) as monthly_revenue_recognized
FROM contracts
GROUP BY 1
ORDER BY 1;
```

## SaaS Specific Metrics

### Net Revenue Retention (NRR)

**Definition**: Percentage of recurring revenue retained from existing customers, including expansion.

```sql
-- Net Revenue Retention
WITH cohort_mrr AS (
  SELECT
    DATE_TRUNC('month', first_payment_date) as cohort_month,
    user_id,
    SUM(
      CASE
        WHEN DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', first_payment_date)
        THEN amount
      END
    ) as initial_mrr,
    SUM(
      CASE
        WHEN DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', first_payment_date) + INTERVAL '12 months'
        THEN amount
      END
    ) as mrr_12_months_later
  FROM payments
  GROUP BY 1, 2
)
SELECT
  cohort_month,
  SUM(mrr_12_months_later) / SUM(initial_mrr) * 100 as nrr_pct
FROM cohort_mrr
WHERE initial_mrr > 0
GROUP BY 1
ORDER BY 1;
```

**Interpretation**:
- NRR > 100%: Expansion exceeds churn (ideal)
- NRR = 100%: Break-even (expansion = churn)
- NRR < 100%: Churn exceeds expansion

### Gross Revenue Retention (GRR)

**Definition**: Percentage of recurring revenue retained, excluding expansion.

```sql
-- Gross Revenue Retention
WITH cohort_retention AS (
  SELECT
    cohort_month,
    user_id,
    initial_mrr,
    LEAST(mrr_12_months_later, initial_mrr) as retained_mrr
  FROM cohort_mrr
)
SELECT
  cohort_month,
  SUM(retained_mrr) / SUM(initial_mrr) * 100 as grr_pct
FROM cohort_retention
WHERE initial_mrr > 0
GROUP BY 1
ORDER BY 1;
```

### Quick Ratio

**Definition**: (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)

```sql
-- Quick Ratio
WITH mrr_movements AS (
  SELECT
    month,
    SUM(CASE WHEN type = 'new' THEN amount ELSE 0 END) as new_mrr,
    SUM(CASE WHEN type = 'expansion' THEN amount ELSE 0 END) as expansion_mrr,
    SUM(CASE WHEN type = 'churned' THEN amount ELSE 0 END) as churned_mrr,
    SUM(CASE WHEN type = 'contraction' THEN amount ELSE 0 END) as contraction_mrr
  FROM mrr_changes
  GROUP BY 1
)
SELECT
  month,
  (new_mrr + expansion_mrr) / NULLIF(churned_mrr + contraction_mrr, 0) as quick_ratio
FROM mrr_movements
ORDER BY 1;
```

**Interpretation**:
- Quick Ratio > 4: Excellent growth
- Quick Ratio 1-4: Moderate growth
- Quick Ratio < 1: Negative growth

## E-commerce Metrics

### Average Order Value (AOV)

```sql
-- Average Order Value
SELECT
  DATE_TRUNC('month', order_date) as month,
  SUM(order_total) / COUNT(DISTINCT order_id) as aov,
  COUNT(DISTINCT order_id) as num_orders,
  SUM(order_total) as total_revenue
FROM orders
WHERE status = 'completed'
GROUP BY 1
ORDER BY 1;
```

### Revenue Per Session

```sql
-- Revenue per session
SELECT
  DATE_TRUNC('day', s.session_date) as date,
  COUNT(DISTINCT s.session_id) as total_sessions,
  COUNT(DISTINCT o.order_id) as orders,
  COALESCE(SUM(o.order_total), 0) as revenue,
  COALESCE(SUM(o.order_total), 0) / COUNT(DISTINCT s.session_id) as revenue_per_session
FROM sessions s
LEFT JOIN orders o ON s.session_id = o.session_id
GROUP BY 1
ORDER BY 1;
```

### Cart Abandonment Revenue Loss

```sql
-- Revenue lost to cart abandonment
SELECT
  DATE_TRUNC('month', cart_created_at) as month,
  COUNT(DISTINCT cart_id) as abandoned_carts,
  SUM(cart_value) as potential_revenue_lost
FROM carts
WHERE status = 'abandoned'
  AND cart_value > 0
GROUP BY 1
ORDER BY 1;
```

## Revenue Forecasting

### Linear Trend Forecast

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def forecast_revenue(historical_data, periods_ahead=3):
    """Forecast revenue using linear regression"""
    df = pd.DataFrame(historical_data)
    df['period'] = range(len(df))

    X = df[['period']].values
    y = df['revenue'].values

    model = LinearRegression()
    model.fit(X, y)

    # Forecast future periods
    future_periods = np.array([[len(df) + i] for i in range(periods_ahead)])
    forecasts = model.predict(future_periods)

    return forecasts

# Example usage
historical = {
    'month': ['2024-01', '2024-02', '2024-03', '2024-04'],
    'revenue': [100000, 110000, 125000, 140000]
}
forecast = forecast_revenue(historical, periods_ahead=3)
```

### Moving Average Forecast

```python
def moving_average_forecast(data, window=3):
    """Simple moving average forecast"""
    return np.mean(data[-window:])
```

## Best Practices

### Revenue Recognition
1. Follow GAAP/IFRS standards
2. Recognize revenue when earned, not when paid
3. Defer revenue for annual contracts
4. Account for refunds and chargebacks
5. Separate one-time from recurring revenue

### Reporting Guidelines
1. Use consistent time periods
2. Segment by product, channel, geography
3. Compare actuals to budget/forecast
4. Show trends over time
5. Highlight anomalies and explain drivers

### Common Pitfalls
1. Confusing bookings with revenue
2. Ignoring revenue deferrals
3. Not accounting for refunds
4. Mixing gross and net revenue
5. Inconsistent metric definitions

## Formulas Quick Reference

| Metric | Formula |
|--------|---------|
| MRR | Sum of monthly subscription revenue |
| ARR | MRR × 12 |
| ARPU | Total Revenue / Total Users |
| NRR | (Starting MRR + Expansion - Contraction - Churn) / Starting MRR |
| GRR | (Starting MRR - Contraction - Churn) / Starting MRR |
| Quick Ratio | (New + Expansion) / (Churn + Contraction) |
| AOV | Total Revenue / Number of Orders |
| MoM Growth | (Current Month - Previous Month) / Previous Month |
| YoY Growth | (Current Year - Previous Year) / Previous Year |
| CAGR | (Ending Value / Beginning Value)^(1/Years) - 1 |
