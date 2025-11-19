# Cohort Analysis Guide: Step-by-Step Tutorial

## Introduction

This guide walks through performing cohort analysis from data preparation to actionable insights.

## Prerequisites

- SQL database with user activity data
- Basic understanding of SQL
- Python (optional for visualizations)

## Step 1: Define Your Cohort

Choose cohort grouping:
- **Time-based**: Signup month/week
- **Feature-based**: Users who tried feature X
- **Channel-based**: Users from specific acquisition channel

## Step 2: Build the Base Query

```sql
-- Step 2a: Identify user cohorts
CREATE TEMP TABLE user_cohorts AS
SELECT
    user_id,
    DATE_TRUNC('month', signup_date) as cohort_month
FROM users;

-- Step 2b: Track activity by period
CREATE TEMP TABLE user_activity AS
SELECT
    user_id,
    DATE_TRUNC('month', activity_date) as activity_month
FROM activities
WHERE activity_type = 'active_session';

-- Step 2c: Calculate cohort size
CREATE TEMP TABLE cohort_sizes AS
SELECT
    cohort_month,
    COUNT(DISTINCT user_id) as cohort_size
FROM user_cohorts
GROUP BY 1;
```

## Step 3: Calculate Retention

```sql
-- Calculate retention by cohort and period
SELECT
    uc.cohort_month,
    ua.activity_month,
    EXTRACT(MONTH FROM AGE(ua.activity_month, uc.cohort_month)) as months_since_cohort,
    COUNT(DISTINCT ua.user_id) as active_users,
    cs.cohort_size,
    ROUND(COUNT(DISTINCT ua.user_id) * 100.0 / cs.cohort_size, 2) as retention_pct
FROM user_cohorts uc
JOIN user_activity ua ON uc.user_id = ua.user_id
JOIN cohort_sizes cs ON uc.cohort_month = cs.cohort_month
WHERE ua.activity_month >= uc.cohort_month
GROUP BY 1, 2, 3, 5
ORDER BY 1, 2;
```

## Step 4: Visualize Results

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load cohort data
cohort_data = pd.read_sql(query, connection)

# Pivot for heatmap
cohort_pivot = cohort_data.pivot_table(
    index='cohort_month',
    columns='months_since_cohort',
    values='retention_pct'
)

# Create heatmap
plt.figure(figsize=(16, 10))
sns.heatmap(cohort_pivot, annot=True, fmt='.1f', cmap='RdYlGn',
            vmin=0, vmax=100, center=50)
plt.title('Cohort Retention Analysis')
plt.ylabel('Cohort Month')
plt.xlabel('Months Since Signup')
plt.show()
```

## Step 5: Analyze Patterns

Look for:
1. **Retention curve shape**: How quickly does retention stabilize?
2. **Cohort quality trends**: Are newer cohorts better/worse?
3. **Seasonal patterns**: Do certain months have better retention?
4. **Inflection points**: Where does retention flatten out?

## Step 6: Generate Insights

Example insights:
- "Month 3 retention improved from 25% to 35% after product update"
- "Q4 cohorts show 40% better 6-month retention than Q1 cohorts"
- "Retention stabilizes at month 6 (platform our power users)"

## Step 7: Take Action

Based on insights, implement:
- **Improve early retention**: Focus on months 0-3 experience
- **Replicate success**: What did high-performing cohorts do differently?
- **Segment interventions**: Different strategies for different cohort types

## Common Pitfalls

- **Too many small cohorts**: Need minimum size for statistical significance
- **Ignoring seasonality**: Account for calendar effects
- **Not acting on insights**: Analysis without action wastes time

## Next Steps

- Analyze revenue cohorts (not just retention)
- Compare cohorts across dimensions (channel, segment, feature)
- Build automated cohort monitoring dashboard
