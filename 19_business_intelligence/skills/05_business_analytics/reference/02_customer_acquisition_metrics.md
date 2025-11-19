# Customer Acquisition Metrics Reference

Comprehensive guide to measuring and optimizing customer acquisition efficiency.

## Core CAC Metrics

### 1. Customer Acquisition Cost (CAC)

**Definition**: Total cost of acquiring a new customer.

```sql
-- Basic CAC calculation
WITH marketing_spend AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    SUM(amount) as total_spend
  FROM marketing_expenses
  GROUP BY 1
),
new_customers AS (
  SELECT
    DATE_TRUNC('month', signup_date) as month,
    COUNT(DISTINCT user_id) as new_customers
  FROM users
  GROUP BY 1
)
SELECT
  m.month,
  m.total_spend,
  n.new_customers,
  m.total_spend / NULLIF(n.new_customers, 0) as cac
FROM marketing_spend m
JOIN new_customers n ON m.month = n.month
ORDER BY 1;
```

**Detailed CAC by Channel**:
```sql
-- CAC by acquisition channel
WITH channel_spend AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    channel,
    SUM(amount) as spend
  FROM marketing_expenses
  GROUP BY 1, 2
),
channel_acquisitions AS (
  SELECT
    DATE_TRUNC('month', signup_date) as month,
    acquisition_channel as channel,
    COUNT(DISTINCT user_id) as customers
  FROM users
  WHERE acquisition_channel IS NOT NULL
  GROUP BY 1, 2
)
SELECT
  s.month,
  s.channel,
  s.spend,
  a.customers,
  s.spend / NULLIF(a.customers, 0) as cac_per_channel
FROM channel_spend s
LEFT JOIN channel_acquisitions a
  ON s.month = a.month AND s.channel = a.channel
ORDER BY 1, 2;
```

**Blended vs Paid CAC**:
```sql
-- Comparing blended and paid CAC
WITH all_spend AS (
  SELECT
    DATE_TRUNC('month', date) as month,
    SUM(amount) as total_marketing_spend,
    SUM(CASE WHEN channel_type = 'paid' THEN amount ELSE 0 END) as paid_spend
  FROM marketing_expenses
  GROUP BY 1
),
acquisitions AS (
  SELECT
    DATE_TRUNC('month', signup_date) as month,
    COUNT(DISTINCT user_id) as total_customers,
    COUNT(DISTINCT CASE WHEN acquisition_channel IN ('paid_search', 'paid_social', 'display')
          THEN user_id END) as paid_customers
  FROM users
  GROUP BY 1
)
SELECT
  s.month,
  s.total_marketing_spend / NULLIF(a.total_customers, 0) as blended_cac,
  s.paid_spend / NULLIF(a.paid_customers, 0) as paid_cac,
  a.total_customers,
  a.paid_customers
FROM all_spend s
JOIN acquisitions a ON s.month = a.month
ORDER BY 1;
```

### 2. LTV:CAC Ratio

**Definition**: Customer Lifetime Value divided by Customer Acquisition Cost.

```sql
-- LTV:CAC ratio
WITH customer_metrics AS (
  SELECT
    DATE_TRUNC('month', signup_date) as cohort,
    AVG(lifetime_value) as avg_ltv,
    AVG(acquisition_cost) as avg_cac
  FROM (
    SELECT
      u.user_id,
      u.signup_date,
      SUM(p.amount) as lifetime_value,
      m.acquisition_cost
    FROM users u
    LEFT JOIN payments p ON u.user_id = p.user_id
    LEFT JOIN marketing_attribution m ON u.user_id = m.user_id
    GROUP BY 1, 2, 4
  ) customer_data
  GROUP BY 1
)
SELECT
  cohort,
  avg_ltv,
  avg_cac,
  avg_ltv / NULLIF(avg_cac, 0) as ltv_cac_ratio
FROM customer_metrics
ORDER BY 1;
```

**Target Ratios**:
- **3:1 or higher**: Healthy, sustainable growth
- **1:1 to 3:1**: Acceptable but needs improvement
- **Below 1:1**: Unsustainable (losing money on each customer)

### 3. CAC Payback Period

**Definition**: Number of months to recover customer acquisition cost.

```sql
-- CAC payback period calculation
WITH customer_revenue AS (
  SELECT
    u.user_id,
    u.signup_date,
    u.acquisition_cost as cac,
    p.payment_month,
    EXTRACT(MONTH FROM AGE(p.payment_month, u.signup_date)) as months_since_signup,
    SUM(p.amount) as monthly_revenue,
    SUM(SUM(p.amount)) OVER (
      PARTITION BY u.user_id
      ORDER BY p.payment_month
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as cumulative_revenue
  FROM users u
  JOIN (
    SELECT
      user_id,
      DATE_TRUNC('month', payment_date) as payment_month,
      SUM(amount) as amount
    FROM payments
    GROUP BY 1, 2
  ) p ON u.user_id = p.user_id
  GROUP BY 1, 2, 3, 4, 5, 6
)
SELECT
  user_id,
  cac,
  MIN(months_since_signup) as payback_months
FROM customer_revenue
WHERE cumulative_revenue >= cac
GROUP BY 1, 2;

-- Average payback period by cohort
WITH payback AS (
  -- Use above query
)
SELECT
  DATE_TRUNC('month', u.signup_date) as cohort,
  AVG(p.payback_months) as avg_payback_months,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.payback_months) as median_payback_months
FROM payback p
JOIN users u ON p.user_id = u.user_id
GROUP BY 1
ORDER BY 1;
```

**Industry Benchmarks**:
- **SaaS**: 5-12 months ideal
- **E-commerce**: 1-3 months typical
- **Marketplace**: 12-24 months acceptable

### 4. Conversion Rates

**Top of Funnel**:
```sql
-- Visitor to signup conversion
SELECT
  DATE_TRUNC('month', date) as month,
  COUNT(DISTINCT visitor_id) as unique_visitors,
  COUNT(DISTINCT CASE WHEN signup = true THEN visitor_id END) as signups,
  COUNT(DISTINCT CASE WHEN signup = true THEN visitor_id END) * 100.0 /
    COUNT(DISTINCT visitor_id) as visitor_to_signup_pct
FROM web_analytics
GROUP BY 1
ORDER BY 1;
```

**Multi-Stage Conversion**:
```sql
-- Full funnel conversion rates
WITH funnel_stages AS (
  SELECT
    DATE_TRUNC('week', date) as week,
    COUNT(DISTINCT visitor_id) as visitors,
    COUNT(DISTINCT CASE WHEN signed_up THEN visitor_id END) as signups,
    COUNT(DISTINCT CASE WHEN activated THEN visitor_id END) as activated,
    COUNT(DISTINCT CASE WHEN converted THEN visitor_id END) as paid_customers
  FROM user_funnel
  GROUP BY 1
)
SELECT
  week,
  visitors,
  signups,
  signups * 100.0 / NULLIF(visitors, 0) as visitor_to_signup_pct,
  activated * 100.0 / NULLIF(signups, 0) as signup_to_activation_pct,
  paid_customers * 100.0 / NULLIF(activated, 0) as activation_to_paid_pct,
  paid_customers * 100.0 / NULLIF(visitors, 0) as overall_conversion_pct
FROM funnel_stages
ORDER BY 1;
```

**Conversion by Channel**:
```sql
-- Channel-specific conversion rates
SELECT
  acquisition_channel,
  COUNT(DISTINCT user_id) as total_users,
  COUNT(DISTINCT CASE WHEN converted_to_paid THEN user_id END) as paid_customers,
  COUNT(DISTINCT CASE WHEN converted_to_paid THEN user_id END) * 100.0 /
    COUNT(DISTINCT user_id) as conversion_rate
FROM users
WHERE acquisition_channel IS NOT NULL
GROUP BY 1
ORDER BY 4 DESC;
```

### 5. Marketing Efficiency Ratio (MER)

**Definition**: Revenue generated / Marketing spend.

```sql
-- Marketing Efficiency Ratio
WITH monthly_metrics AS (
  SELECT
    DATE_TRUNC('month', r.date) as month,
    SUM(r.revenue) as total_revenue,
    MAX(m.spend) as marketing_spend
  FROM revenue r
  CROSS JOIN (
    SELECT
      DATE_TRUNC('month', date) as month,
      SUM(amount) as spend
    FROM marketing_expenses
    GROUP BY 1
  ) m
  WHERE DATE_TRUNC('month', r.date) = m.month
  GROUP BY 1
)
SELECT
  month,
  total_revenue,
  marketing_spend,
  total_revenue / NULLIF(marketing_spend, 0) as mer
FROM monthly_metrics
ORDER BY 1;
```

**Target MER**:
- **> 3**: Excellent efficiency
- **2-3**: Good efficiency
- **< 2**: Needs optimization

## Channel Performance Metrics

### 6. Cost Per Click (CPC)

```sql
-- CPC by channel and campaign
SELECT
  channel,
  campaign,
  SUM(spend) as total_spend,
  SUM(clicks) as total_clicks,
  SUM(spend) / NULLIF(SUM(clicks), 0) as avg_cpc
FROM ad_performance
GROUP BY 1, 2
ORDER BY 5 DESC;
```

### 7. Cost Per Lead (CPL)

```sql
-- CPL calculation
WITH campaign_spend AS (
  SELECT
    campaign_id,
    SUM(spend) as total_spend
  FROM ad_spend
  GROUP BY 1
),
campaign_leads AS (
  SELECT
    campaign_id,
    COUNT(DISTINCT lead_id) as leads
  FROM leads
  GROUP BY 1
)
SELECT
  s.campaign_id,
  s.total_spend,
  l.leads,
  s.total_spend / NULLIF(l.leads, 0) as cpl
FROM campaign_spend s
JOIN campaign_leads l ON s.campaign_id = l.campaign_id
ORDER BY 4;
```

### 8. Return on Ad Spend (ROAS)

```sql
-- ROAS by campaign
WITH campaign_revenue AS (
  SELECT
    c.campaign_id,
    SUM(o.revenue) as attributed_revenue
  FROM campaigns c
  JOIN orders o ON c.user_id = o.user_id
    AND o.order_date >= c.click_date
    AND o.order_date <= c.click_date + INTERVAL '30 days'
  GROUP BY 1
),
campaign_spend AS (
  SELECT
    campaign_id,
    SUM(spend) as total_spend
  FROM ad_spend
  GROUP BY 1
)
SELECT
  s.campaign_id,
  r.attributed_revenue,
  s.total_spend,
  r.attributed_revenue / NULLIF(s.total_spend, 0) as roas
FROM campaign_spend s
LEFT JOIN campaign_revenue r ON s.campaign_id = r.campaign_id
ORDER BY 4 DESC;
```

**ROAS Benchmarks**:
- **> 4:1**: Strong performance
- **2:1 to 4:1**: Average performance
- **< 2:1**: Underperforming

## Cohort-Based CAC Analysis

### 9. CAC Trends Over Time

```python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_cac_trends(data):
    """Analyze CAC trends and identify inflection points"""
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(df['month'])

    # Calculate rolling average
    df['cac_rolling_3mo'] = df['cac'].rolling(window=3).mean()

    # Calculate month-over-month change
    df['cac_mom_change'] = df['cac'].pct_change() * 100

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # CAC over time
    ax1.plot(df['month'], df['cac'], label='Monthly CAC', marker='o')
    ax1.plot(df['month'], df['cac_rolling_3mo'], label='3-Month Rolling Avg', linestyle='--')
    ax1.set_ylabel('CAC ($)')
    ax1.set_title('Customer Acquisition Cost Trend')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # MoM change
    ax2.bar(df['month'], df['cac_mom_change'])
    ax2.axhline(y=0, color='r', linestyle='-', linewidth=0.5)
    ax2.set_ylabel('MoM Change (%)')
    ax2.set_title('Month-over-Month CAC Change')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return df
```

### 10. CAC by Customer Segment

```sql
-- CAC by customer segment/tier
WITH customer_segments AS (
  SELECT
    user_id,
    signup_date,
    CASE
      WHEN first_payment_amount >= 1000 THEN 'Enterprise'
      WHEN first_payment_amount >= 100 THEN 'Professional'
      ELSE 'Starter'
    END as segment
  FROM users
),
segment_cac AS (
  SELECT
    DATE_TRUNC('quarter', cs.signup_date) as quarter,
    cs.segment,
    COUNT(DISTINCT cs.user_id) as customers,
    SUM(m.acquisition_cost) / COUNT(DISTINCT cs.user_id) as avg_cac
  FROM customer_segments cs
  LEFT JOIN marketing_attribution m ON cs.user_id = m.user_id
  GROUP BY 1, 2
)
SELECT
  quarter,
  segment,
  customers,
  avg_cac,
  SUM(customers) OVER (PARTITION BY quarter) as total_customers,
  customers * 100.0 / SUM(customers) OVER (PARTITION BY quarter) as pct_of_total
FROM segment_cac
ORDER BY 1, 4 DESC;
```

## Advanced CAC Metrics

### 11. Organic vs Paid Ratio

```sql
-- Organic vs paid customer mix
SELECT
  DATE_TRUNC('month', signup_date) as month,
  COUNT(DISTINCT CASE WHEN acquisition_cost = 0 OR acquisition_channel IN ('organic', 'referral', 'direct')
        THEN user_id END) as organic_customers,
  COUNT(DISTINCT CASE WHEN acquisition_cost > 0 AND acquisition_channel NOT IN ('organic', 'referral', 'direct')
        THEN user_id END) as paid_customers,
  COUNT(DISTINCT CASE WHEN acquisition_cost = 0 OR acquisition_channel IN ('organic', 'referral', 'direct')
        THEN user_id END) * 100.0 / COUNT(DISTINCT user_id) as organic_pct
FROM users
GROUP BY 1
ORDER BY 1;
```

### 12. Viral Coefficient

**Definition**: Number of new users each existing user brings in.

```python
def calculate_viral_coefficient(invites_sent, conversion_rate):
    """
    Calculate viral coefficient (k-factor)

    K > 1: Exponential growth
    K = 1: Linear growth
    K < 1: Growth slows over time
    """
    return invites_sent * conversion_rate

# Example
avg_invites_per_user = 3.5
invite_conversion_rate = 0.25  # 25%
k_factor = calculate_viral_coefficient(avg_invites_per_user, invite_conversion_rate)
print(f"Viral Coefficient: {k_factor:.2f}")  # 0.88
```

```sql
-- Viral coefficient from data
WITH referral_metrics AS (
  SELECT
    DATE_TRUNC('month', r.referral_date) as month,
    COUNT(DISTINCT r.referrer_id) as referring_users,
    COUNT(DISTINCT r.referred_user_id) as referred_users,
    COUNT(DISTINCT CASE WHEN u.converted THEN r.referred_user_id END) as converted_referrals
  FROM referrals r
  LEFT JOIN users u ON r.referred_user_id = u.user_id
  GROUP BY 1
)
SELECT
  month,
  referred_users * 1.0 / NULLIF(referring_users, 0) as avg_invites_per_user,
  converted_referrals * 1.0 / NULLIF(referred_users, 0) as invite_conversion_rate,
  (referred_users * 1.0 / NULLIF(referring_users, 0)) *
    (converted_referrals * 1.0 / NULLIF(referred_users, 0)) as viral_coefficient
FROM referral_metrics
ORDER BY 1;
```

## CAC Optimization Framework

### Analysis Checklist

1. **Benchmark CAC by Channel**
   - Identify lowest CAC channels
   - Compare to industry standards
   - Track trends over time

2. **Calculate Full Funnel Metrics**
   - Impression → Click → Lead → Customer
   - Identify highest drop-off points
   - Optimize weak conversion stages

3. **Segment Analysis**
   - CAC by customer type/value
   - Geographic differences
   - Device/platform variations

4. **Time-Based Patterns**
   - Seasonal variations
   - Day of week/time of day patterns
   - Campaign timing optimization

5. **Cohort Performance**
   - CAC trends by acquisition month
   - Quality of customers over time
   - Payback period evolution

### Optimization Strategies

**Reduce CAC**:
- Improve conversion rates at each funnel stage
- Optimize ad targeting and creative
- Focus on high-performing channels
- Leverage organic/referral channels
- Improve landing page experience
- A/B test messaging and offers

**Improve LTV:CAC Ratio**:
- Increase customer lifetime value
- Reduce churn rate
- Upsell/cross-sell existing customers
- Improve product value proposition
- Enhance customer success efforts

## Python Analytics Template

```python
import pandas as pd
import numpy as np

class CACAnalyzer:
    def __init__(self, marketing_data, customer_data):
        self.marketing_df = pd.DataFrame(marketing_data)
        self.customer_df = pd.DataFrame(customer_data)

    def calculate_cac(self, period='M'):
        """Calculate CAC by time period"""
        # Group marketing spend
        spend = self.marketing_df.groupby(
            pd.Grouper(key='date', freq=period)
        )['spend'].sum()

        # Group new customers
        customers = self.customer_df.groupby(
            pd.Grouper(key='signup_date', freq=period)
        ).size()

        # Calculate CAC
        cac_df = pd.DataFrame({
            'spend': spend,
            'customers': customers,
            'cac': spend / customers
        })

        return cac_df

    def calculate_payback_period(self, user_id):
        """Calculate CAC payback period for a user"""
        user_payments = self.customer_df[
            self.customer_df['user_id'] == user_id
        ].sort_values('payment_date')

        cac = user_payments.iloc[0]['acquisition_cost']
        cumulative_revenue = user_payments['revenue'].cumsum()

        payback_month = (cumulative_revenue >= cac).idxmax()
        return payback_month

    def channel_performance(self):
        """Compare performance across channels"""
        return self.customer_df.groupby('channel').agg({
            'user_id': 'count',
            'acquisition_cost': 'mean',
            'lifetime_value': 'mean'
        }).assign(
            ltv_cac_ratio=lambda x: x['lifetime_value'] / x['acquisition_cost']
        )
```

## Key Takeaways

1. **CAC must be measured consistently** across channels and time
2. **LTV:CAC ratio of 3:1** is generally healthy for sustainable growth
3. **Payback period** should align with business model (shorter for e-commerce, longer for SaaS)
4. **Channel-specific CAC** reveals optimization opportunities
5. **Blended CAC** can mask poor performing channels
6. **Organic growth** reduces overall CAC and improves unit economics
7. **Cohort analysis** shows CAC efficiency trends over time
8. **CAC optimization** requires full-funnel visibility

## Common Mistakes to Avoid

- Not including all acquisition costs (overhead, salaries, tools)
- Confusing CAC with cost per lead
- Ignoring organic customer acquisition
- Not segmenting by customer value
- Using inconsistent time periods for attribution
- Failing to track CAC payback period
- Optimizing for CAC without considering LTV
- Not accounting for customer quality differences
