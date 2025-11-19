# Customer Segmentation Reference

Comprehensive guide to customer segmentation methods, analysis, and strategies for targeted marketing and product development.

## Types of Segmentation

### 1. Demographic Segmentation

**Basic Demographics**:
```sql
-- Segment customers by demographic attributes
SELECT
  CASE
    WHEN age < 25 THEN '18-24'
    WHEN age < 35 THEN '25-34'
    WHEN age < 45 THEN '35-44'
    WHEN age < 55 THEN '45-54'
    ELSE '55+'
  END as age_group,
  gender,
  country,
  COUNT(DISTINCT user_id) as customers,
  AVG(total_lifetime_value) as avg_ltv,
  AVG(order_frequency) as avg_frequency
FROM customers
GROUP BY 1, 2, 3
ORDER BY 4 DESC;
```

### 2. Firmographic Segmentation (B2B)

```sql
-- B2B customer segmentation
SELECT
  CASE
    WHEN company_size < 50 THEN 'SMB (1-50)'
    WHEN company_size < 500 THEN 'Mid-Market (50-500)'
    ELSE 'Enterprise (500+)'
  END as company_segment,
  industry,
  COUNT(DISTINCT customer_id) as accounts,
  SUM(arr) as total_arr,
  AVG(arr) as avg_arr,
  AVG(contract_length_months) as avg_contract_length
FROM b2b_customers
GROUP BY 1, 2
ORDER BY 4 DESC;
```

### 3. Behavioral Segmentation

**Purchase Behavior**:
```sql
-- Segment by purchase patterns
WITH customer_behavior AS (
  SELECT
    customer_id,
    COUNT(DISTINCT order_id) as total_orders,
    SUM(order_total) as total_spent,
    AVG(order_total) as avg_order_value,
    EXTRACT(DAY FROM (MAX(order_date) - MIN(order_date))) / NULLIF(COUNT(DISTINCT order_id) - 1, 0) as avg_days_between_orders,
    COUNT(DISTINCT product_category) as categories_purchased
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '365 days'
  GROUP BY 1
)
SELECT
  CASE
    WHEN total_orders = 1 THEN 'One-Time Buyer'
    WHEN total_orders <= 3 THEN 'Occasional Buyer'
    WHEN total_orders <= 10 THEN 'Regular Buyer'
    ELSE 'Frequent Buyer'
  END as purchase_frequency_segment,
  CASE
    WHEN avg_order_value < 50 THEN 'Low Value'
    WHEN avg_order_value < 200 THEN 'Medium Value'
    ELSE 'High Value'
  END as order_value_segment,
  COUNT(*) as customers,
  AVG(total_spent) as avg_total_spent,
  AVG(avg_days_between_orders) as avg_purchase_interval
FROM customer_behavior
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Product Affinity**:
```sql
-- Segment by product preferences
WITH product_preferences AS (
  SELECT
    customer_id,
    product_category,
    COUNT(*) as purchases_in_category,
    SUM(order_total) as spend_in_category,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY COUNT(*) DESC) as category_rank
  FROM orders
  JOIN order_items USING (order_id)
  WHERE order_date >= CURRENT_DATE - INTERVAL '365 days'
  GROUP BY 1, 2
)
SELECT
  product_category as primary_category,
  COUNT(DISTINCT customer_id) as customers,
  AVG(purchases_in_category) as avg_purchases,
  AVG(spend_in_category) as avg_spend
FROM product_preferences
WHERE category_rank = 1  -- Primary category for each customer
GROUP BY 1
ORDER BY 2 DESC;
```

### 4. Geographic Segmentation

```sql
-- Segment by geography with performance metrics
SELECT
  country,
  region,
  city,
  COUNT(DISTINCT customer_id) as customers,
  SUM(total_revenue) as revenue,
  AVG(total_revenue) as avg_revenue_per_customer,
  AVG(order_frequency) as avg_orders_per_customer,
  -- Market penetration
  COUNT(DISTINCT customer_id) * 100.0 / population as penetration_rate
FROM customers
JOIN geographic_data USING (city)
GROUP BY 1, 2, 3
HAVING COUNT(DISTINCT customer_id) >= 10
ORDER BY 5 DESC;
```

### 5. Psychographic Segmentation

**Lifestyle/Values-Based**:
```sql
-- Segment by interests and values (from survey/behavioral data)
WITH customer_interests AS (
  SELECT
    customer_id,
    MAX(CASE WHEN interest = 'sustainability' THEN 1 ELSE 0 END) as sustainability_focused,
    MAX(CASE WHEN interest = 'luxury' THEN 1 ELSE 0 END) as luxury_oriented,
    MAX(CASE WHEN interest = 'budget' THEN 1 ELSE 0 END) as price_sensitive,
    MAX(CASE WHEN interest = 'innovation' THEN 1 ELSE 0 END) as early_adopter
  FROM customer_survey_responses
  GROUP BY 1
)
SELECT
  CASE
    WHEN sustainability_focused = 1 THEN 'Eco-Conscious'
    WHEN luxury_oriented = 1 THEN 'Premium Seekers'
    WHEN price_sensitive = 1 THEN 'Value Hunters'
    WHEN early_adopter = 1 THEN 'Innovators'
    ELSE 'Mainstream'
  END as psychographic_segment,
  COUNT(*) as customers,
  AVG(c.total_lifetime_value) as avg_ltv,
  AVG(c.nps_score) as avg_nps
FROM customer_interests ci
JOIN customers c ON ci.customer_id = c.customer_id
GROUP BY 1
ORDER BY 2 DESC;
```

## Advanced Segmentation Methods

### K-Means Clustering

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def kmeans_segmentation(customer_data, n_clusters=4):
    """
    Perform K-means clustering for customer segmentation

    Args:
        customer_data: DataFrame with customer metrics
        n_clusters: Number of clusters to create

    Returns:
        DataFrame with cluster assignments
    """
    # Select features for clustering
    features = ['recency', 'frequency', 'monetary', 'avg_order_value',
                'product_diversity', 'engagement_score']

    X = customer_data[features].copy()

    # Handle missing values
    X = X.fillna(X.median())

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    # Add cluster assignments
    customer_data['cluster'] = clusters

    # Calculate cluster statistics
    cluster_summary = customer_data.groupby('cluster')[features].agg(['mean', 'median', 'count'])

    print("Cluster Summary:")
    print(cluster_summary)

    return customer_data, kmeans, scaler

# Determine optimal number of clusters (Elbow method)
def find_optimal_clusters(X_scaled, max_clusters=10):
    """Find optimal number of clusters using elbow method"""
    inertias = []
    K_range = range(2, max_clusters + 1)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)

    # Plot elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(K_range, inertias, 'bo-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method For Optimal k')
    plt.grid(True, alpha=0.3)
    plt.show()

    return inertias
```

### Hierarchical Clustering

```python
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def hierarchical_segmentation(customer_data, features, method='ward'):
    """
    Perform hierarchical clustering

    Args:
        customer_data: DataFrame with customer metrics
        features: List of feature columns to use
        method: Linkage method ('ward', 'complete', 'average')

    Returns:
        Linkage matrix
    """
    X = customer_data[features].fillna(customer_data[features].median())

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Perform hierarchical clustering
    linkage_matrix = linkage(X_scaled, method=method)

    # Plot dendrogram
    plt.figure(figsize=(15, 7))
    dendrogram(linkage_matrix, truncate_mode='lastp', p=30)
    plt.xlabel('Cluster Size')
    plt.ylabel('Distance')
    plt.title('Hierarchical Clustering Dendrogram')
    plt.show()

    return linkage_matrix
```

### DBSCAN (Density-Based Clustering)

```python
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def dbscan_segmentation(customer_data, features, eps=0.5, min_samples=5):
    """
    Perform DBSCAN clustering (good for finding outliers)

    Args:
        customer_data: DataFrame with customer metrics
        features: List of feature columns
        eps: Maximum distance between samples
        min_samples: Minimum samples in neighborhood

    Returns:
        DataFrame with cluster assignments
    """
    X = customer_data[features].fillna(customer_data[features].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(X_scaled)

    customer_data['cluster'] = clusters

    # -1 indicates outliers/noise points
    print(f"Number of clusters: {len(set(clusters)) - (1 if -1 in clusters else 0)}")
    print(f"Number of outliers: {list(clusters).count(-1)}")

    return customer_data
```

## Multi-Dimensional Segmentation

### Combining Multiple Segmentation Dimensions

```sql
-- Create multi-dimensional segments
WITH customer_profiles AS (
  SELECT
    customer_id,
    -- RFM
    NTILE(5) OVER (ORDER BY recency DESC) as r_score,
    NTILE(5) OVER (ORDER BY frequency) as f_score,
    NTILE(5) OVER (ORDER BY monetary) as m_score,
    -- Behavioral
    CASE
      WHEN total_orders = 1 THEN 'One-Time'
      WHEN total_orders <= 5 THEN 'Occasional'
      ELSE 'Regular'
    END as purchase_frequency,
    -- Product Affinity
    primary_category,
    -- Geographic
    region,
    -- Value
    CASE
      WHEN lifetime_value >= 1000 THEN 'High Value'
      WHEN lifetime_value >= 500 THEN 'Medium Value'
      ELSE 'Low Value'
    END as value_tier
  FROM customer_metrics
)
SELECT
  value_tier,
  purchase_frequency,
  primary_category,
  region,
  COUNT(*) as customers,
  AVG(r_score + f_score + m_score) as avg_rfm_score
FROM customer_profiles
GROUP BY 1, 2, 3, 4
HAVING COUNT(*) >= 10
ORDER BY 6 DESC, 5 DESC;
```

### Persona Development

```python
def create_personas(segmented_customers):
    """
    Create customer personas from segments

    Args:
        segmented_customers: DataFrame with cluster assignments

    Returns:
        Dictionary of personas with characteristics
    """
    personas = {}

    for cluster in segmented_customers['cluster'].unique():
        cluster_data = segmented_customers[segmented_customers['cluster'] == cluster]

        persona = {
            'size': len(cluster_data),
            'percentage': len(cluster_data) / len(segmented_customers) * 100,

            'demographics': {
                'age': cluster_data['age'].median(),
                'top_locations': cluster_data['country'].value_counts().head(3).to_dict()
            },

            'behavior': {
                'avg_orders': cluster_data['total_orders'].mean(),
                'avg_ltv': cluster_data['lifetime_value'].mean(),
                'avg_order_value': cluster_data['avg_order_value'].mean(),
                'top_categories': cluster_data['primary_category'].value_counts().head(3).to_dict()
            },

            'engagement': {
                'avg_days_between_orders': cluster_data['avg_days_between_orders'].mean(),
                'avg_session_duration': cluster_data['avg_session_duration'].mean(),
                'engagement_score': cluster_data['engagement_score'].mean()
            },

            'recommended_strategy': assign_strategy(cluster_data)
        }

        personas[f'Cluster_{cluster}'] = persona

    return personas

def assign_strategy(cluster_data):
    """Assign marketing strategy based on cluster characteristics"""
    avg_ltv = cluster_data['lifetime_value'].mean()
    avg_frequency = cluster_data['total_orders'].mean()
    avg_recency = cluster_data['recency'].mean()

    if avg_ltv > 1000 and avg_frequency > 10:
        return "VIP Treatment: Loyalty rewards, early access, premium support"
    elif avg_ltv > 500 and avg_recency < 60:
        return "Upsell Focus: Cross-sell, premium products, bundle offers"
    elif avg_frequency < 2:
        return "Activation: Second purchase incentives, education, engagement"
    elif avg_recency > 180:
        return "Win-back: Reactivation campaigns, special offers, surveys"
    else:
        return "Nurture: Regular communication, product recommendations"
```

## Segment Performance Tracking

### Segment Health Metrics

```sql
-- Track segment health over time
WITH monthly_segments AS (
  SELECT
    DATE_TRUNC('month', order_date) as month,
    customer_segment,
    COUNT(DISTINCT customer_id) as active_customers,
    SUM(order_total) as revenue,
    AVG(order_total) as avg_order_value,
    COUNT(DISTINCT order_id) as orders
  FROM orders
  JOIN customer_segments USING (customer_id)
  WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY 1, 2
)
SELECT
  month,
  customer_segment,
  active_customers,
  revenue,
  avg_order_value,
  orders,
  -- Month-over-month growth
  (active_customers - LAG(active_customers) OVER (PARTITION BY customer_segment ORDER BY month))
    * 100.0 / NULLIF(LAG(active_customers) OVER (PARTITION BY customer_segment ORDER BY month), 0) as customer_growth_pct,
  (revenue - LAG(revenue) OVER (PARTITION BY customer_segment ORDER BY month))
    * 100.0 / NULLIF(LAG(revenue) OVER (PARTITION BY customer_segment ORDER BY month), 0) as revenue_growth_pct
FROM monthly_segments
ORDER BY 1 DESC, 3 DESC;
```

### Segment Migration

```sql
-- Track movement between segments
WITH segment_changes AS (
  SELECT
    cs_old.customer_id,
    cs_old.segment as previous_segment,
    cs_new.segment as current_segment,
    cs_old.segment_date as previous_date,
    cs_new.segment_date as current_date
  FROM customer_segments_historical cs_old
  JOIN customer_segments_current cs_new ON cs_old.customer_id = cs_new.customer_id
  WHERE cs_old.segment != cs_new.segment
)
SELECT
  previous_segment,
  current_segment,
  COUNT(*) as customers_migrated,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY previous_segment), 2) as pct_of_previous_segment
FROM segment_changes
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
```

## Segment Targeting

### Channel Preferences by Segment

```sql
-- Identify preferred channels for each segment
WITH channel_response AS (
  SELECT
    cs.segment,
    mc.channel,
    COUNT(DISTINCT mc.campaign_id) as campaigns,
    SUM(mc.clicks) as total_clicks,
    SUM(mc.conversions) as total_conversions,
    SUM(mc.conversions) * 100.0 / NULLIF(SUM(mc.clicks), 0) as conversion_rate,
    SUM(mc.revenue) as total_revenue,
    SUM(mc.revenue) / NULLIF(SUM(mc.spend), 0) as roas
  FROM customer_segments cs
  JOIN marketing_campaigns mc ON cs.customer_id = mc.customer_id
  WHERE mc.campaign_date >= CURRENT_DATE - INTERVAL '6 months'
  GROUP BY 1, 2
)
SELECT
  segment,
  channel,
  campaigns,
  conversion_rate,
  roas,
  RANK() OVER (PARTITION BY segment ORDER BY roas DESC) as channel_rank
FROM channel_response
WHERE campaigns >= 3  -- Minimum campaigns for statistical relevance
ORDER BY segment, roas DESC;
```

### Personalization Opportunities

```sql
-- Identify personalization opportunities per segment
SELECT
  segment,
  -- Product recommendations
  STRING_AGG(DISTINCT top_product, ', ' ORDER BY top_product) as recommended_products,
  -- Optimal contact frequency
  AVG(optimal_email_frequency) as avg_emails_per_month,
  -- Best time to engage
  MODE() WITHIN GROUP (ORDER BY preferred_contact_time) as best_contact_time,
  -- Price sensitivity
  AVG(discount_responsiveness) as avg_discount_response,
  -- Content preferences
  STRING_AGG(DISTINCT preferred_content_type, ', ') as content_preferences
FROM segment_preferences
GROUP BY 1
ORDER BY 1;
```

## Segmentation Best Practices

### 1. Segment Validation

```python
def validate_segments(segmented_data, features, cluster_col='cluster'):
    """
    Validate segmentation quality using multiple metrics

    Args:
        segmented_data: DataFrame with cluster assignments
        features: List of features used for segmentation
        cluster_col: Name of cluster column

    Returns:
        Dictionary with validation metrics
    """
    from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
    from sklearn.preprocessing import StandardScaler

    X = segmented_data[features].fillna(segmented_data[features].median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clusters = segmented_data[cluster_col]

    # Remove outliers (-1) if using DBSCAN
    mask = clusters != -1
    X_scaled_clean = X_scaled[mask]
    clusters_clean = clusters[mask]

    metrics = {
        # Higher is better (range: -1 to 1)
        'silhouette_score': silhouette_score(X_scaled_clean, clusters_clean),

        # Lower is better
        'davies_bouldin_score': davies_bouldin_score(X_scaled_clean, clusters_clean),

        # Higher is better
        'calinski_harabasz_score': calinski_harabasz_score(X_scaled_clean, clusters_clean),

        # Business metrics
        'num_segments': len(set(clusters_clean)),
        'avg_segment_size': len(clusters_clean) / len(set(clusters_clean)),
        'smallest_segment': (clusters_clean.value_counts().min(),
                            clusters_clean.value_counts().min() / len(clusters_clean) * 100),
        'largest_segment': (clusters_clean.value_counts().max(),
                           clusters_clean.value_counts().max() / len(clusters_clean) * 100)
    }

    return metrics
```

### 2. Actionability Checklist

Segments should be:
- [ ] **Measurable**: Can quantify size and characteristics
- [ ] **Accessible**: Can reach with marketing/sales
- [ ] **Substantial**: Large enough to be profitable
- [ ] **Differentiable**: Respond differently to marketing
- [ ] **Actionable**: Can develop specific strategies

### 3. Naming Segments

**Good Segment Names** (descriptive and memorable):
- "Deal Hunters" instead of "Cluster 3"
- "Premium Loyalists" instead of "High RFM Score"
- "At-Risk VIPs" instead of "Segment 7"

```python
def name_segments(segment_summary):
    """
    Auto-generate descriptive segment names

    Args:
        segment_summary: DataFrame with segment characteristics

    Returns:
        Dictionary mapping cluster numbers to names
    """
    segment_names = {}

    for idx, row in segment_summary.iterrows():
        cluster = row['cluster']
        ltv = row['avg_lifetime_value']
        frequency = row['avg_frequency']
        recency = row['avg_recency_days']

        if ltv > 1000 and frequency > 10:
            name = "Champions"
        elif ltv > 1000 and frequency <= 10:
            name = "High-Value Shoppers"
        elif ltv < 200 and recency > 180:
            name = "At-Risk Low-Value"
        elif frequency == 1:
            name = "One-Time Buyers"
        elif recency < 30:
            name = "Recent Actives"
        else:
            name = f"Segment {cluster}"

        segment_names[cluster] = name

    return segment_names
```

## Segment-Specific Strategies

### Strategy Matrix

| Segment | Characteristics | Strategy | Tactics |
|---------|-----------------|----------|---------|
| **Champions** | High RFM, High LTV | Retain & Leverage | VIP programs, referral rewards, early access |
| **Potential Champions** | High recent activity, medium LTV | Develop | Upsell, cross-sell, loyalty program |
| **New Customers** | Recent first purchase | Activate | Welcome series, second purchase offer, education |
| **At-Risk High Value** | High LTV, declining activity | Win-back | Personalized offers, phone outreach, surveys |
| **Deal Hunters** | High discount usage | Convert | Limited-time full-price offers, premium positioning |
| **Loyalists** | Regular purchase, medium value | Grow | Increase basket size, premium product intro |
| **Low Engagement** | Infrequent, low value | Nurture or Sunset | Cost-effective retention, segment or remove |

## Reporting Template

```markdown
# Segment Analysis Report

## Executive Summary
- [X] segments identified
- [Y]% of revenue from top 2 segments
- [Z]% potential revenue lift from optimization

## Segment Overview

### Segment 1: [Name]
**Size**: X customers (Y% of base)
**Revenue**: $XXX (Z% of total)
**Characteristics**:
- Avg LTV: $XXX
- Avg Order Value: $XX
- Purchase Frequency: X orders/year
- Primary Products: [List]

**Recommended Actions**:
1. [Action 1]
2. [Action 2]
3. [Action 3]

[Repeat for each segment]

## Key Insights
1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

## Recommendations
1. [Priority recommendation]
2. [Secondary recommendation]
3. [Long-term recommendation]

## Next Steps
- [ ] Implement targeting for Segment X
- [ ] A/B test messaging for Segment Y
- [ ] Develop retention program for Segment Z
```

## Key Takeaways

1. **Start Simple**: Begin with RFM or behavioral segmentation
2. **Make It Actionable**: Each segment needs a specific strategy
3. **Test and Iterate**: Validate assumptions with A/B tests
4. **Monitor Evolution**: Track segment migration over time
5. **Avoid Over-Segmentation**: Too many segments become unmanageable
6. **Combine Methods**: Use multiple segmentation approaches
7. **Business Context**: Align segments with business goals and capabilities
