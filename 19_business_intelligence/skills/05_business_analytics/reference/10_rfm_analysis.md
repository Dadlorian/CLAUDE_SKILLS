# RFM Analysis Reference

Comprehensive guide to RFM (Recency, Frequency, Monetary) analysis for customer segmentation and value assessment.

## What is RFM Analysis?

**Definition**: A customer segmentation method based on three dimensions:
- **Recency**: How recently a customer made a purchase
- **Frequency**: How often they purchase
- **Monetary**: How much they spend

**Why RFM Works**:
- Simple yet powerful segmentation
- Actionable customer insights
- Data-driven marketing prioritization
- Easy to calculate and understand
- Strong predictor of future behavior

## Calculating RFM Scores

### Basic RFM Calculation

```sql
-- Calculate RFM metrics for each customer
WITH customer_rfm AS (
  SELECT
    customer_id,
    -- Recency: days since last purchase
    EXTRACT(DAY FROM (CURRENT_DATE - MAX(order_date))) as recency_days,
    -- Frequency: number of orders
    COUNT(DISTINCT order_id) as frequency,
    -- Monetary: total spend
    SUM(order_total) as monetary_value
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '365 days'  -- Last 12 months
  GROUP BY 1
)
SELECT
  customer_id,
  recency_days,
  frequency,
  monetary_value
FROM customer_rfm
ORDER BY recency_days, frequency DESC, monetary_value DESC;
```

### RFM Scoring (Quintiles)

```sql
-- Assign RFM scores using quintiles (1-5 scale)
WITH customer_metrics AS (
  SELECT
    customer_id,
    EXTRACT(DAY FROM (CURRENT_DATE - MAX(order_date))) as recency_days,
    COUNT(DISTINCT order_id) as frequency,
    SUM(order_total) as monetary_value
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '365 days'
  GROUP BY 1
),
rfm_scores AS (
  SELECT
    customer_id,
    recency_days,
    frequency,
    monetary_value,
    -- Lower recency is better, so reverse the score
    NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,
    NTILE(5) OVER (ORDER BY frequency) as f_score,
    NTILE(5) OVER (ORDER BY monetary_value) as m_score
  FROM customer_metrics
)
SELECT
  customer_id,
  recency_days,
  frequency,
  monetary_value,
  r_score,
  f_score,
  m_score,
  -- Combined RFM score
  r_score || f_score || m_score as rfm_score,
  -- Simple numeric score
  (r_score + f_score + m_score) as rfm_total
FROM rfm_scores
ORDER BY r_score DESC, f_score DESC, m_score DESC;
```

### Python Implementation

```python
import pandas as pd
import numpy as np
from datetime import datetime

def calculate_rfm(orders_df, customer_id_col='customer_id',
                  order_date_col='order_date', revenue_col='revenue',
                  analysis_date=None):
    """
    Calculate RFM scores for customers

    Args:
        orders_df: DataFrame with order data
        customer_id_col: Name of customer ID column
        order_date_col: Name of order date column
        revenue_col: Name of revenue column
        analysis_date: Reference date for recency calculation

    Returns:
        DataFrame with RFM scores
    """
    if analysis_date is None:
        analysis_date = datetime.now()

    # Ensure date column is datetime
    orders_df[order_date_col] = pd.to_datetime(orders_df[order_date_col])

    # Calculate RFM metrics
    rfm = orders_df.groupby(customer_id_col).agg({
        order_date_col: lambda x: (analysis_date - x.max()).days,  # Recency
        customer_id_col: 'count',  # Frequency (using customer_id as proxy for order count)
        revenue_col: 'sum'  # Monetary
    }).reset_index()

    rfm.columns = [customer_id_col, 'recency', 'frequency', 'monetary']

    # Calculate quintile scores (1-5)
    rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1])  # Reverse for recency
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])

    # Convert to int
    rfm['r_score'] = rfm['r_score'].astype(int)
    rfm['f_score'] = rfm['f_score'].astype(int)
    rfm['m_score'] = rfm['m_score'].astype(int)

    # Combined RFM score
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    rfm['rfm_total'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']

    return rfm

# Example usage
orders = pd.DataFrame({
    'customer_id': ['C1', 'C1', 'C2', 'C2', 'C2', 'C3'],
    'order_date': ['2024-01-15', '2024-06-20', '2024-03-10', '2024-07-15', '2024-10-01', '2023-12-20'],
    'revenue': [100, 150, 200, 250, 300, 50]
})

rfm_scores = calculate_rfm(orders)
print(rfm_scores)
```

## RFM Segmentation

### Standard Segments

```sql
-- Assign customer segments based on RFM scores
WITH customer_rfm AS (
  -- Use RFM calculation from above
  SELECT *
  FROM rfm_scores
)
SELECT
  customer_id,
  r_score,
  f_score,
  m_score,
  rfm_score,
  CASE
    -- Champions: Best customers (RFM 555, 554, 545, 544)
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'

    -- Loyal Customers: Buy regularly (RF high, M varies)
    WHEN r_score >= 3 AND f_score >= 4 THEN 'Loyal Customers'

    -- Potential Loyalists: Recent customers with potential
    WHEN r_score >= 4 AND f_score >= 2 AND f_score <= 3 THEN 'Potential Loyalists'

    -- New Customers: Recent first-time buyers
    WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'

    -- Promising: Recent shoppers with average frequency
    WHEN r_score >= 3 AND f_score >= 2 AND f_score <= 3 THEN 'Promising'

    -- Need Attention: Above average recency, frequency & monetary
    WHEN r_score >= 3 AND f_score >= 3 THEN 'Need Attention'

    -- About to Sleep: Below average recency, frequency & monetary
    WHEN r_score >= 2 AND r_score <= 3 THEN 'About To Sleep'

    -- At Risk: Spent big but long ago, need to reactivate
    WHEN r_score <= 2 AND f_score >= 2 AND m_score >= 3 THEN 'At Risk'

    -- Can't Lose Them: Made big purchases, but long time ago
    WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN "Can't Lose Them"

    -- Hibernating: Last purchase long ago, low spenders
    WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating'

    -- Lost: Lowest recency, frequency & monetary
    WHEN r_score = 1 THEN 'Lost'

    ELSE 'Others'
  END as segment,

  -- Segment priority for targeting
  CASE
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 1  -- Champions
    WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 2  -- Can't Lose
    WHEN r_score <= 2 AND f_score >= 2 AND m_score >= 3 THEN 3  -- At Risk
    WHEN r_score >= 3 AND f_score >= 4 THEN 4  -- Loyal
    WHEN r_score >= 4 AND f_score >= 2 AND f_score <= 3 THEN 5  -- Potential Loyalists
    ELSE 6
  END as priority

FROM customer_rfm
ORDER BY priority, rfm_total DESC;
```

### Segment Characteristics

```sql
-- Analyze segment characteristics
WITH segmented_customers AS (
  -- Use segmentation query from above
  SELECT *
  FROM customer_segments
)
SELECT
  segment,
  COUNT(*) as customer_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_total,
  ROUND(AVG(recency_days), 1) as avg_recency_days,
  ROUND(AVG(frequency), 1) as avg_frequency,
  ROUND(AVG(monetary_value), 2) as avg_monetary,
  SUM(monetary_value) as total_revenue,
  ROUND(SUM(monetary_value) * 100.0 / SUM(SUM(monetary_value)) OVER (), 2) as revenue_contribution_pct
FROM segmented_customers
GROUP BY 1
ORDER BY total_revenue DESC;
```

### Python Segmentation

```python
def segment_customers(rfm_df):
    """
    Assign customer segments based on RFM scores

    Args:
        rfm_df: DataFrame with RFM scores

    Returns:
        DataFrame with segment assignments
    """
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']

        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 4:
            return 'Loyal Customers'
        elif r >= 4 and 2 <= f <= 3:
            return 'Potential Loyalists'
        elif r >= 4 and f == 1:
            return 'New Customers'
        elif r >= 3 and 2 <= f <= 3:
            return 'Promising'
        elif r >= 3 and f >= 3:
            return 'Need Attention'
        elif 2 <= r <= 3:
            return 'About To Sleep'
        elif r <= 2 and f >= 2 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f >= 4 and m >= 4:
            return "Can't Lose Them"
        elif r <= 2 and f <= 2:
            return 'Hibernating'
        elif r == 1:
            return 'Lost'
        else:
            return 'Others'

    rfm_df['segment'] = rfm_df.apply(assign_segment, axis=1)

    return rfm_df

# Apply segmentation
rfm_with_segments = segment_customers(rfm_scores)

# Segment summary
segment_summary = rfm_with_segments.groupby('segment').agg({
    'customer_id': 'count',
    'recency': 'mean',
    'frequency': 'mean',
    'monetary': ['mean', 'sum']
}).round(2)

print(segment_summary)
```

## Action Strategies by Segment

### Marketing Recommendations

```python
SEGMENT_STRATEGIES = {
    'Champions': {
        'description': 'Your best customers who buy frequently and recently',
        'actions': [
            'Reward them - early access to new products',
            'Ask for reviews and testimonials',
            'VIP programs and exclusive offers',
            'Referral programs (they can be brand advocates)'
        ],
        'messaging': 'Thank you for your loyalty!'
    },

    'Loyal Customers': {
        'description': 'Regular customers who buy often',
        'actions': [
            'Upsell higher value products',
            'Cross-sell complementary items',
            'Loyalty rewards program',
            'Premium member benefits'
        ],
        'messaging': 'Special offers just for you'
    },

    'Potential Loyalists': {
        'description': 'Recent customers with potential to become loyal',
        'actions': [
            'Onboarding campaigns',
            'Product recommendations',
            'Membership benefits education',
            'Time-limited offers to encourage repeat'
        ],
        'messaging': 'Welcome! Here\'s what you might also like...'
    },

    'New Customers': {
        'description': 'Newest customers, first purchase',
        'actions': [
            'Welcome series emails',
            'Product education',
            'Second purchase incentive',
            'Set expectations for future engagement'
        ],
        'messaging': 'Thanks for your first purchase!'
    },

    'At Risk': {
        'description': 'High-value customers showing decline',
        'actions': [
            'Win-back campaigns',
            'Personalized reactivation offers',
            'Survey to understand concerns',
            'Special discounts or incentives'
        ],
        'messaging': 'We miss you! Here\'s 20% off...'
    },

    "Can't Lose Them": {
        'description': 'Former best customers at risk of churning',
        'actions': [
            'Aggressive win-back campaigns',
            'Phone calls from account managers',
            'Deep discounts or special offers',
            'Product updates they might have missed'
        ],
        'messaging': 'Your loyalty matters - let\'s reconnect'
    },

    'Hibernating': {
        'description': 'Long dormant, low value',
        'actions': [
            'Minimal touch campaigns',
            'Newsletter inclusion only',
            'Cost-effective reactivation attempts',
            'Consider removing from expensive channels'
        ],
        'messaging': 'Still interested? Here\'s what\'s new...'
    },

    'Lost': {
        'description': 'Churned customers, unlikely to return',
        'actions': [
            'Sunset campaigns',
            'Final win-back attempt',
            'Unsubscribe option',
            'Learn why they left (survey)'
        ],
        'messaging': 'Last chance - we\'d love to have you back'
    }
}
```

### Campaign Prioritization

```sql
-- Prioritize segments for campaigns based on potential value
WITH segment_priority AS (
  SELECT
    segment,
    COUNT(*) as segment_size,
    AVG(monetary_value) as avg_ltv,
    AVG(frequency) as avg_purchase_frequency,
    -- Calculate potential value (size × avg_ltv × likelihood to respond)
    COUNT(*) * AVG(monetary_value) * (
      CASE
        WHEN segment IN ('Champions', 'Loyal Customers') THEN 0.9
        WHEN segment IN ('Potential Loyalists', 'Promising') THEN 0.7
        WHEN segment IN ('Need Attention', 'About To Sleep') THEN 0.5
        WHEN segment IN ('At Risk', "Can't Lose Them") THEN 0.3
        ELSE 0.1
      END
    ) as potential_campaign_value
  FROM customer_segments
  GROUP BY 1
)
SELECT
  segment,
  segment_size,
  avg_ltv,
  potential_campaign_value,
  RANK() OVER (ORDER BY potential_campaign_value DESC) as priority_rank
FROM segment_priority
ORDER BY potential_campaign_value DESC;
```

## RFM Trends Over Time

### Segment Migration

```sql
-- Track how customers move between segments over time
WITH segment_history AS (
  SELECT
    customer_id,
    '2024-Q1' as period,
    segment as q1_segment
  FROM customer_rfm_q1
),
current_segments AS (
  SELECT
    customer_id,
    '2024-Q2' as period,
    segment as q2_segment
  FROM customer_rfm_q2
)
SELECT
  sh.q1_segment as from_segment,
  cs.q2_segment as to_segment,
  COUNT(*) as customer_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY sh.q1_segment), 2) as migration_pct
FROM segment_history sh
JOIN current_segments cs ON sh.customer_id = cs.customer_id
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
```

### RFM Score Distribution

```python
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_rfm_distribution(rfm_df):
    """Create visualization of RFM score distributions"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # RFM Score distribution
    axes[0, 0].hist(rfm_df['rfm_total'], bins=range(3, 16), edgecolor='black')
    axes[0, 0].set_xlabel('RFM Total Score')
    axes[0, 0].set_ylabel('Number of Customers')
    axes[0, 0].set_title('Distribution of RFM Scores')
    axes[0, 0].grid(True, alpha=0.3)

    # Segment sizes
    segment_counts = rfm_df['segment'].value_counts()
    axes[0, 1].barh(segment_counts.index, segment_counts.values)
    axes[0, 1].set_xlabel('Number of Customers')
    axes[0, 1].set_title('Customers by Segment')
    axes[0, 1].grid(True, alpha=0.3)

    # Recency vs Monetary
    scatter = axes[1, 0].scatter(
        rfm_df['recency'],
        rfm_df['monetary'],
        c=rfm_df['frequency'],
        cmap='viridis',
        alpha=0.6
    )
    axes[1, 0].set_xlabel('Recency (days)')
    axes[1, 0].set_ylabel('Monetary Value ($)')
    axes[1, 0].set_title('Recency vs Monetary (colored by Frequency)')
    plt.colorbar(scatter, ax=axes[1, 0], label='Frequency')
    axes[1, 0].grid(True, alpha=0.3)

    # Revenue by segment
    segment_revenue = rfm_df.groupby('segment')['monetary'].sum().sort_values()
    axes[1, 1].barh(segment_revenue.index, segment_revenue.values)
    axes[1, 1].set_xlabel('Total Revenue ($)')
    axes[1, 1].set_title('Revenue by Segment')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# Create visualizations
visualize_rfm_distribution(rfm_with_segments)
```

## Advanced RFM Techniques

### Weighted RFM

```python
def calculate_weighted_rfm(rfm_df, r_weight=1.0, f_weight=1.0, m_weight=1.0):
    """
    Calculate weighted RFM score based on business priorities

    Args:
        rfm_df: DataFrame with RFM scores
        r_weight, f_weight, m_weight: Weights for each dimension

    Returns:
        DataFrame with weighted scores
    """
    # Normalize weights
    total_weight = r_weight + f_weight + m_weight

    rfm_df['weighted_score'] = (
        (rfm_df['r_score'] * r_weight +
         rfm_df['f_score'] * f_weight +
         rfm_df['m_score'] * m_weight) / total_weight
    )

    # Rank by weighted score
    rfm_df['weighted_rank'] = rfm_df['weighted_score'].rank(
        ascending=False,
        method='dense'
    )

    return rfm_df

# Example: Prioritize monetary value more
weighted_rfm = calculate_weighted_rfm(
    rfm_scores,
    r_weight=1.0,
    f_weight=1.5,
    m_weight=2.0  # Emphasize high spenders
)
```

### RFM with Additional Dimensions

**RFMP (Recency, Frequency, Monetary, Product diversity)**:
```sql
-- Add product diversity dimension
WITH customer_metrics AS (
  SELECT
    customer_id,
    EXTRACT(DAY FROM (CURRENT_DATE - MAX(order_date))) as recency_days,
    COUNT(DISTINCT order_id) as frequency,
    SUM(order_total) as monetary_value,
    COUNT(DISTINCT product_category) as product_diversity
  FROM orders o
  JOIN order_items oi ON o.order_id = oi.order_id
  WHERE order_date >= CURRENT_DATE - INTERVAL '365 days'
  GROUP BY 1
)
SELECT
  customer_id,
  NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,
  NTILE(5) OVER (ORDER BY frequency) as f_score,
  NTILE(5) OVER (ORDER BY monetary_value) as m_score,
  NTILE(5) OVER (ORDER BY product_diversity) as p_score
FROM customer_metrics;
```

## Best Practices

1. **Time Period Selection**: Choose appropriate analysis window (typically 12-24 months)
2. **Score Distribution**: Ensure even distribution across quintiles
3. **Regular Updates**: Recalculate RFM scores monthly or quarterly
4. **Segment Validation**: Validate that segments behave as expected
5. **Action-Oriented**: Always tie segments to specific marketing actions
6. **Track ROI**: Measure campaign performance by segment
7. **Iterate**: Refine segment definitions based on results

## Common Variations

| Variation | Use Case |
|-----------|----------|
| **RFM** | Standard e-commerce |
| **RFE** | Recency, Frequency, Engagement (SaaS/apps) |
| **RFD** | Recency, Frequency, Duration (subscription services) |
| **RFML** | Add Lifetime (customer tenure) dimension |
| **Weighted RFM** | Adjust importance of each dimension |

## Key Takeaways

- **Simple but Powerful**: RFM provides actionable segmentation with minimal complexity
- **Behavior-Based**: Segments based on actual customer actions, not demographics
- **Dynamic**: Customers move between segments - track transitions
- **ROI-Focused**: Prioritize marketing spend on high-value segments
- **Requires Action**: Segmentation alone doesn't drive value - targeted campaigns do
- **Regular Refresh**: Update scores frequently to reflect current behavior
- **Test and Learn**: Experiment with different thresholds and strategies
