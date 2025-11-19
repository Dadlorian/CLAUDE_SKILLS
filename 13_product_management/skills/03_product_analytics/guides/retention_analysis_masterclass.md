# Retention Analysis Masterclass

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Cohort Retention Methodology](#cohort-retention-methodology)
3. [Retention Curve Analysis](#retention-curve-analysis)
4. [Churn Prediction Models](#churn-prediction-models)
5. [Resurrection Tactics](#resurrection-tactics)
6. [SQL Queries for Retention](#sql-queries-for-retention)
7. [Case Studies: Netflix & Spotify](#case-studies-netflix--spotify)
8. [Benchmarks and KPIs](#benchmarks-and-kpis)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

Retention is the heartbeat of sustainable SaaS businesses. While acquisition gets the headlines, retention determines profitability, viral coefficient, and long-term viability. This masterclass provides battle-tested methodologies for analyzing, predicting, and improving retention metrics that matter.

**Key Insight**: Companies improving retention by 5% can increase lifetime value by 25-95%, depending on the business model.

---

## Cohort Retention Methodology

### 1.1 Understanding Cohorts

A cohort is a group of users who share a common characteristic or experience within a defined time period. The most common is **acquisition cohort** (users acquired in the same week, month, or quarter).

### 1.2 Building a Cohort Retention Table

The cohort retention table is your foundational analysis tool. It shows what percentage of users from each cohort remained active in subsequent periods.

#### Cohort Structure

```
Acquisition Cohort    Month 0    Month 1    Month 2    Month 3    Month 4    Month 5    Month 6
2024-01-01           100%       45%        28%        18%        12%        8%         6%
2024-02-01           100%       48%        31%        19%        14%        9%         7%
2024-03-01           100%       52%        34%        22%        16%        11%        8%
2024-04-01           100%       50%        32%        20%        15%        10%        -
2024-05-01           100%       46%        29%        18%        13%        -          -
2024-06-01           100%       49%        31%        19%        -          -          -
2024-07-01           100%       51%        33%        -          -          -          -
```

#### Cohort Retention Calculation Formula

```
Retention Rate (Month N) = (Active Users in Month N / Total Cohort Size) × 100

Where:
- Active Users = Users who performed a key action (login, transaction, etc.)
- Month N = Number of months after first acquisition
```

### 1.3 Calculating Retention: Step-by-Step

**Step 1: Define Activity**
- Login in last 7 days
- At least 1 transaction
- Session duration > 2 minutes
- Content consumed or action taken

**Step 2: Determine Cohort Period**
- Weekly (most granular)
- Monthly (most common for SaaS)
- Quarterly (for B2B with longer sales cycles)

**Step 3: Build User-Period Matrix**
- Row: User ID
- Column: Period
- Value: 1 (active) or 0 (inactive)

**Step 4: Aggregate and Calculate**
- Sum active users per period
- Divide by cohort size
- Multiply by 100

### 1.4 Cohort Retention Table Example (E-Commerce)

| Cohort | Week 1 | Week 2 | Week 3 | Week 4 | Week 5 | Week 6 | Week 7 | Week 8 |
|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| 2024-W01 | 100% | 32% | 18% | 11% | 7% | 5% | 3% | 2% |
| 2024-W02 | 100% | 35% | 21% | 13% | 8% | 6% | 4% | 3% |
| 2024-W03 | 100% | 38% | 24% | 15% | 10% | 7% | 5% | 4% |
| 2024-W04 | 100% | 34% | 19% | 12% | 8% | 6% | 4% | 3% |
| 2024-W05 | 100% | 36% | 22% | 14% | 9% | 7% | 5% | 4% |

### 1.5 Interpreting Cohort Patterns

**Healthy Retention Signature**
- Week 1: 100% (all users)
- Week 2-4: Steep drop-off (expected)
- Week 5+: Stabilization (~5-15%)
- Flat line: Core engaged users

**Red Flag Patterns**
1. **Cliff Drop**: Sharp drop after specific event (product change, paywall introduction)
2. **Consistent Decline**: Every metric decreases month-over-month
3. **No Stabilization**: Continues declining indefinitely
4. **Low Baseline**: < 5% retention by month 3 (high churn product)

---

## Retention Curve Analysis

### 2.1 Mathematical Models for Retention Curves

#### Model 1: Exponential Decay

```
Retention(t) = R₀ × e^(-λt)

Where:
- R₀ = Initial retention (100% at t=0)
- λ = Decay constant
- t = Time period
- e = Euler's number (2.71828)
```

**Example Calculation:**
```
R₀ = 100%
λ = 0.35 (35% drop per month)
Month 3: Retention = 100 × e^(-0.35 × 3) = 100 × e^(-1.05) = 35%
```

#### Model 2: Power Law (Zipf's Law Variant)

```
Retention(t) = R₀ × t^(-α)

Where:
- R₀ = Initial retention constant
- α = Power law exponent (typically 0.5-1.5)
- t = Time period
```

**Why Power Law?** Retention often decreases slower than exponential after initial drop-off.

#### Model 3: Segmented Hyperbolic

```
Retention(t) = (a × t) / (b + t)

Where:
- a = Maximum retention level
- b = Time constant (50% retention point)
- t = Time period
```

### 2.2 Fitting Retention Data

#### Excel/Google Sheets Method

1. Create columns: Month, Actual Retention, Exponential, Power Law
2. Use LINEST() function for exponential regression
3. Use LOGEST() for power law curve fitting
4. Calculate R² (coefficient of determination)

```
Exponential Formula: =R0 * EXP(-λ * t)
Power Law Formula: =R0 * (t^-α)
```

#### Python Implementation

```python
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Data
months = np.array([0, 1, 2, 3, 4, 5, 6])
retention = np.array([100, 45, 28, 18, 12, 8, 6])

# Exponential decay function
def exponential(t, R0, lambda_):
    return R0 * np.exp(-lambda_ * t)

# Power law function
def power_law(t, R0, alpha):
    return R0 / ((t + 1) ** alpha)

# Fit models
popt_exp, _ = curve_fit(exponential, months, retention)
popt_pow, _ = curve_fit(power_law, months, retention)

# Generate smooth curves
t_smooth = np.linspace(0, 6, 100)
exp_fit = exponential(t_smooth, *popt_exp)
pow_fit = power_law(t_smooth, *popt_pow)

# Visualization
plt.figure(figsize=(12, 6))
plt.scatter(months, retention, label='Actual Data', s=100)
plt.plot(t_smooth, exp_fit, label='Exponential Fit', linewidth=2)
plt.plot(t_smooth, pow_fit, label='Power Law Fit', linewidth=2)
plt.xlabel('Months')
plt.ylabel('Retention Rate (%)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.title('Retention Curve Analysis')
plt.show()

print(f"Exponential: R₀={popt_exp[0]:.2f}, λ={popt_exp[1]:.4f}")
print(f"Power Law: R₀={popt_pow[0]:.2f}, α={popt_pow[1]:.4f}")
```

### 2.3 Key Metrics from Retention Curves

#### Day 1 Retention (D1)
- First return after acquisition
- Industry average: 20-40%
- Netflix benchmark: 60%+

#### Day 7 Retention (D7)
- One week engagement metric
- Industry average: 15-25%
- Indicates habit formation

#### Day 30 Retention (D30)
- Monthly engagement (SaaS standard)
- Industry average: 5-10%
- Strong indicator of product-market fit

#### Month 3 Retention (M3)
- Long-term stickiness
- Predicts 12-month lifetime
- Industry average: 2-5%

#### Half-Life
The time it takes for retention to drop to 50%

```
Half-Life = ln(0.5) / λ (for exponential)
Half-Life = -t such that Retention(t) = 50%
```

### 2.4 Retention Curve Shapes and Meanings

#### Ideal (Netflix-like)
- High D1: 60%+ (strong product engagement)
- Sustained D7: 45%+
- Stabilization: 20%+ by month 3
- Flat tail: Engaged user base

#### Good (SaaS Standard)
- D1: 40-50%
- D7: 20-30%
- M3: 5-10%
- Stabilizes at 3-5%

#### Problematic (High Churn)
- D1: < 30%
- D7: < 15%
- M3: < 2%
- Continues declining

---

## Churn Prediction Models

### 3.1 Why Predict Churn?

**Business Impact**:
- Rescue at-risk customers before they leave
- Reduce CAC impact through early intervention
- Improve LTV through retention marketing
- Target marketing spend efficiently

### 3.2 Feature Engineering for Churn Prediction

#### Key Churn Predictors

```
Behavioral Features:
- Days since last login
- Session frequency (logins per week)
- Session duration
- Features used
- Support tickets filed
- Payment failures
- Feature adoption rate
- Engagement score trend

Account Features:
- Age of account (days)
- Plan type (price sensitivity)
- Company size
- Industry
- Geographic region
- Deployment type (cloud, on-premise)

Temporal Features:
- Day of week effect
- Seasonality pattern
- Time to first action
- Frequency decay

Financial Features:
- Monthly recurring revenue
- Payment method changes
- Usage rate relative to plan
- Previous price increases
```

### 3.3 Logistic Regression Model

#### Formula

```
P(Churn) = 1 / (1 + e^(-z))

Where z = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ

- β₀ = Intercept (baseline churn probability)
- β₁...βₙ = Feature coefficients (weight of each factor)
- x₁...xₙ = Feature values
- P(Churn) = Probability user will churn (0-1)
```

#### Python Implementation

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd

# Load data
df = pd.read_csv('user_features.csv')

# Feature engineering
features = [
    'days_since_login',
    'weekly_sessions',
    'avg_session_duration',
    'features_used',
    'support_tickets',
    'payment_failures',
    'account_age_days',
    'engagement_score'
]

X = df[features]
y = df['churned']  # 1 = churned, 0 = retained

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42
)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.3f}")

# Feature importance
feature_importance = pd.DataFrame({
    'Feature': features,
    'Coefficient': model.coef_[0]
}).sort_values('Coefficient', ascending=False)

print("\nFeature Importance (Coefficients):")
print(feature_importance)

# Churn probability for new user
new_user_features = scaler.transform([[
    7, 2, 15, 3, 0, 0, 30, 65
]])
churn_prob = model.predict_proba(new_user_features)[0, 1]
print(f"\nPredicted Churn Probability: {churn_prob:.2%}")
```

### 3.4 Random Forest Model

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_recall_curve
import numpy as np

# Train Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Feature importance
feature_importance_rf = pd.DataFrame({
    'Feature': features,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("Random Forest Feature Importance:")
print(feature_importance_rf)

# Evaluate
y_pred_rf = rf_model.predict(X_test)
y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]

print(f"ROC-AUC: {roc_auc_score(y_test, y_pred_proba_rf):.3f}")

# Precision-Recall Trade-off
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_proba_rf)

# Find optimal threshold
f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
optimal_idx = np.argmax(f1_scores)
optimal_threshold = thresholds[optimal_idx]

print(f"Optimal Churn Probability Threshold: {optimal_threshold:.3f}")
```

### 3.5 Churn Risk Scoring System

#### Risk Tiers

```
Risk Tier    Churn Probability    Action
High         > 60%                Immediate intervention
Medium       40-60%               Targeted outreach
Low          20-40%               Monitoring
Safe         < 20%                Upsell opportunity
```

#### Implementation

```sql
-- Create churn risk scores
CREATE TABLE user_churn_risk AS
SELECT
    user_id,
    email,
    account_age_days,
    days_since_login,
    weekly_sessions,
    payment_failures,
    -- Predict churn using model (simplified)
    CASE
        WHEN days_since_login > 30 AND weekly_sessions < 1 THEN 0.75
        WHEN days_since_login > 14 AND weekly_sessions < 2 THEN 0.55
        WHEN days_since_login > 7 AND weekly_sessions < 3 THEN 0.35
        WHEN payment_failures > 0 THEN 0.65
        ELSE 0.15
    END AS churn_probability,
    CASE
        WHEN (SELECT churn_probability) > 0.6 THEN 'High'
        WHEN (SELECT churn_probability) > 0.4 THEN 'Medium'
        WHEN (SELECT churn_probability) > 0.2 THEN 'Low'
        ELSE 'Safe'
    END AS risk_tier,
    NOW() AS scored_at
FROM users
WHERE status = 'active'
    AND account_age_days > 7  -- Skip very new users
ORDER BY churn_probability DESC;
```

---

## Resurrection Tactics

### 4.1 Churn Prevention Framework

#### Pre-Churn Interventions (Highest ROI)

**Trigger 1: Declining Usage**
```
Condition: Weekly sessions drop > 50% vs previous 4 weeks
Action: In-app message, feature reminder, personal email
Timing: Within 24 hours of trend detection
Message: "We noticed you haven't used [feature]. Here's how it saved [other user] time..."
Incentive: 20% discount on next plan renewal
Expected Impact: 25-40% reactivation rate
```

**Trigger 2: Payment Failures**
```
Condition: Billing decline or failed payment attempt
Action: Immediate notification, payment retry flow, support outreach
Timing: Within 1 hour
Message: "Payment issue with your account - let's fix it"
Incentive: Payment retry instructions, extension period
Expected Impact: 60-75% payment recovery
```

**Trigger 3: Support Escalation**
```
Condition: Multiple negative support tickets, unresolved issues
Action: Manager outreach, priority support, issue resolution
Timing: Within 24 hours of third ticket
Message: "We want to make this right"
Incentive: Account credit, priority support
Expected Impact: 30-50% saved accounts
```

**Trigger 4: Feature Adoption Plateau**
```
Condition: User enables <30% of available features
Action: Onboarding reminder, feature recommendations, walkthrough videos
Timing: Day 7 of inactivity
Message: "Unlock these features to maximize your results"
Incentive: Advanced features trial access
Expected Impact: 20-35% reactivation
```

### 4.2 Win-Back Campaign Strategy

#### Segmentation Strategy

```
Churned Segment           Days Since Churn    Win-Back Offer         Expected Recovery
Power Users              < 30 days            50% off 1 month         40-50%
Regular Users            30-90 days           60% off + 3 free users  25-35%
Occasional Users         90-180 days          70% off + migration aid 10-15%
Dormant Users            > 180 days           Free tier trial         2-5%
```

#### Email Sequence Template

```
Email 1 (Day 3 after churn): "We miss you"
- Focus on what they achieved with your product
- Highlight new features since they left
- Soft value prop without hard sell
- CTA: View what's new

Email 2 (Day 10): "Here's what's changed"
- Product updates, new users achieved success
- Case study from similar company
- Limited-time offer (not discount-first)
- CTA: Book a 15-min demo

Email 3 (Day 21): "Special offer just for you"
- Direct special offer (50% off, extended trial)
- Urgency: Valid for 5 days only
- Risk reversal: 30-day money-back guarantee
- CTA: Reactivate account

Email 4 (Day 45): Last chance offer
- Final discounted offer
- Testimonial from similar user
- Focus on ROI/outcomes
- CTA: Return to account
```

### 4.3 Resurrection Campaign SQL

```sql
-- Identify win-back candidates
CREATE TABLE winback_candidates AS
SELECT
    user_id,
    email,
    company_name,
    churned_date,
    churn_reason,
    days_since_churn,
    total_lifetime_value,
    last_nps_score,
    -- Calculate win-back priority
    CASE
        WHEN days_since_churn <= 30 AND total_lifetime_value > 1000 THEN 'Priority 1'
        WHEN days_since_churn <= 90 AND total_lifetime_value > 500 THEN 'Priority 2'
        WHEN days_since_churn <= 180 THEN 'Priority 3'
        ELSE 'Priority 4'
    END AS winback_priority,
    -- Determine offer tier
    CASE
        WHEN days_since_churn <= 30 THEN '50% off 1 month'
        WHEN days_since_churn <= 90 THEN '60% off + 3 free seats'
        ELSE '70% off + migration support'
    END AS offer,
    NOW() AS segment_date
FROM churned_users
WHERE churned_date > NOW() - INTERVAL 180 DAY
    AND churn_reason NOT IN ('too expensive', 'billing fraud')
    AND account_age_days > 30
ORDER BY days_since_churn ASC;

-- Track win-back campaign performance
CREATE TABLE winback_campaign_tracking (
    campaign_id VARCHAR(100),
    user_id VARCHAR(100),
    email_sent_date TIMESTAMP,
    email_opened BOOLEAN,
    email_clicked BOOLEAN,
    account_reactivated BOOLEAN,
    reactivation_date TIMESTAMP,
    discount_used DECIMAL(5,2),
    revenue_recovered DECIMAL(10,2),
    PRIMARY KEY (campaign_id, user_id)
);

-- Win-back ROI calculation
SELECT
    campaign_id,
    COUNT(*) AS emails_sent,
    SUM(CASE WHEN email_opened THEN 1 ELSE 0 END) AS emails_opened,
    ROUND(100.0 * SUM(CASE WHEN email_opened THEN 1 ELSE 0 END) / COUNT(*), 2) AS open_rate,
    SUM(CASE WHEN email_clicked THEN 1 ELSE 0 END) AS emails_clicked,
    SUM(CASE WHEN account_reactivated THEN 1 ELSE 0 END) AS accounts_reactivated,
    ROUND(100.0 * SUM(CASE WHEN account_reactivated THEN 1 ELSE 0 END) / COUNT(*), 2) AS reactivation_rate,
    ROUND(SUM(COALESCE(revenue_recovered, 0)), 2) AS total_revenue_recovered,
    ROUND(SUM(COALESCE(discount_used, 0)), 2) AS discount_cost,
    ROUND(SUM(COALESCE(revenue_recovered, 0)) - SUM(COALESCE(discount_used, 0)), 2) AS net_revenue,
    ROUND((SUM(COALESCE(revenue_recovered, 0)) - SUM(COALESCE(discount_used, 0))) / 1000, 2) AS campaign_roi
FROM winback_campaign_tracking
GROUP BY campaign_id
ORDER BY reactivation_rate DESC;
```

---

## SQL Queries for Retention

### 5.1 Cohort Retention Query

```sql
-- Master cohort retention query (Monthly cohorts)
WITH user_cohorts AS (
    -- Assign each user to acquisition month
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date)::DATE AS cohort_month,
        DATE_TRUNC('month', created_at)::DATE AS activity_month,
        EXTRACT(MONTH FROM created_at) - EXTRACT(MONTH FROM signup_date) +
            12 * (EXTRACT(YEAR FROM created_at) - EXTRACT(YEAR FROM signup_date))
            AS months_since_acquisition
    FROM events
    WHERE event_type IN ('login', 'transaction', 'session_start')
    GROUP BY user_id, DATE_TRUNC('month', signup_date), DATE_TRUNC('month', created_at)
),
cohort_data AS (
    SELECT
        cohort_month,
        months_since_acquisition,
        COUNT(DISTINCT user_id) AS active_users
    FROM user_cohorts
    GROUP BY cohort_month, months_since_acquisition
),
cohort_sizes AS (
    SELECT
        cohort_month,
        active_users AS cohort_size
    FROM cohort_data
    WHERE months_since_acquisition = 0
)
SELECT
    c.cohort_month,
    cs.cohort_size,
    c.months_since_acquisition,
    c.active_users,
    ROUND(100.0 * c.active_users / cs.cohort_size, 2) AS retention_percentage
FROM cohort_data c
JOIN cohort_sizes cs ON c.cohort_month = cs.cohort_month
ORDER BY c.cohort_month DESC, c.months_since_acquisition ASC;
```

### 5.2 Day-Level Retention Query

```sql
-- Day 1, 7, 30 retention calculation
WITH user_first_activity AS (
    SELECT
        user_id,
        MIN(DATE(created_at)) AS first_activity_date
    FROM events
    WHERE event_type IN ('login', 'transaction')
    GROUP BY user_id
),
user_activity_days AS (
    SELECT
        u.user_id,
        u.first_activity_date,
        DATE(e.created_at) AS activity_date,
        CAST(DATE(e.created_at) - u.first_activity_date AS INTEGER) AS days_since_first
    FROM user_first_activity u
    JOIN events e ON u.user_id = e.user_id
    WHERE e.event_type IN ('login', 'transaction')
    GROUP BY u.user_id, u.first_activity_date, DATE(e.created_at)
),
retention_days AS (
    SELECT
        first_activity_date,
        MAX(CASE WHEN days_since_first = 0 THEN 1 ELSE 0 END) AS day_0,
        MAX(CASE WHEN days_since_first = 1 THEN 1 ELSE 0 END) AS day_1,
        MAX(CASE WHEN days_since_first = 7 THEN 1 ELSE 0 END) AS day_7,
        MAX(CASE WHEN days_since_first = 30 THEN 1 ELSE 0 END) AS day_30,
        COUNT(DISTINCT user_id) AS cohort_size
    FROM user_activity_days
    GROUP BY first_activity_date
)
SELECT
    first_activity_date,
    cohort_size,
    ROUND(100.0 * SUM(day_1) / SUM(day_0), 2) AS d1_retention,
    ROUND(100.0 * SUM(day_7) / SUM(day_0), 2) AS d7_retention,
    ROUND(100.0 * SUM(day_30) / SUM(day_0), 2) AS d30_retention
FROM retention_days
GROUP BY first_activity_date, cohort_size
ORDER BY first_activity_date DESC;
```

### 5.3 Churn Detection Query

```sql
-- Identify users at risk of churning
WITH user_activity_window AS (
    SELECT
        user_id,
        DATE_TRUNC('week', created_at)::DATE AS activity_week,
        COUNT(*) AS events_count
    FROM events
    WHERE event_type IN ('login', 'transaction', 'feature_use')
    GROUP BY user_id, DATE_TRUNC('week', created_at)
),
user_engagement_trend AS (
    SELECT
        user_id,
        activity_week,
        events_count,
        LAG(events_count) OVER (PARTITION BY user_id ORDER BY activity_week) AS prev_week_events,
        ROUND(
            100.0 * (LAG(events_count) OVER (PARTITION BY user_id ORDER BY activity_week) - events_count) /
            NULLIF(LAG(events_count) OVER (PARTITION BY user_id ORDER BY activity_week), 0),
            2
        ) AS engagement_decline_pct
    FROM user_activity_window
)
SELECT
    u.user_id,
    u.email,
    u.signup_date,
    u.mrr,
    e.activity_week,
    e.events_count,
    e.prev_week_events,
    e.engagement_decline_pct,
    CASE
        WHEN e.events_count = 0 AND e.prev_week_events > 10 THEN 'High Risk'
        WHEN e.engagement_decline_pct > 75 THEN 'High Risk'
        WHEN e.engagement_decline_pct BETWEEN 50 AND 75 THEN 'Medium Risk'
        WHEN e.engagement_decline_pct BETWEEN 25 AND 50 THEN 'Low Risk'
        ELSE 'Stable'
    END AS churn_risk_level,
    NOW() - CAST(u.last_activity_date AS TIMESTAMP) AS days_since_activity
FROM users u
LEFT JOIN user_engagement_trend e ON u.user_id = e.user_id
WHERE u.status = 'active'
    AND e.activity_week = (SELECT MAX(activity_week) FROM user_activity_window)
ORDER BY churn_risk_level DESC, engagement_decline_pct DESC;
```

### 5.4 Segmented Retention Analysis

```sql
-- Retention by customer segment (plan, company size, industry)
WITH cohort_segment_data AS (
    SELECT
        DATE_TRUNC('month', u.signup_date)::DATE AS cohort_month,
        u.plan_type,
        CASE
            WHEN u.company_size < 10 THEN 'Micro'
            WHEN u.company_size < 100 THEN 'SMB'
            WHEN u.company_size < 1000 THEN 'Mid-Market'
            ELSE 'Enterprise'
        END AS segment,
        EXTRACT(MONTH FROM e.created_at) - EXTRACT(MONTH FROM u.signup_date) +
            12 * (EXTRACT(YEAR FROM e.created_at) - EXTRACT(YEAR FROM u.signup_date))
            AS months_since_signup,
        COUNT(DISTINCT u.user_id) AS active_users
    FROM users u
    JOIN events e ON u.user_id = e.user_id
    WHERE e.event_type IN ('login', 'transaction')
    GROUP BY
        DATE_TRUNC('month', u.signup_date),
        u.plan_type,
        segment,
        months_since_signup
),
cohort_sizes_segment AS (
    SELECT
        cohort_month,
        plan_type,
        segment,
        SUM(CASE WHEN months_since_signup = 0 THEN active_users ELSE 0 END) AS cohort_size
    FROM cohort_segment_data
    GROUP BY cohort_month, plan_type, segment
)
SELECT
    c.cohort_month,
    c.plan_type,
    c.segment,
    cs.cohort_size,
    c.months_since_signup AS month,
    c.active_users,
    ROUND(100.0 * c.active_users / cs.cohort_size, 2) AS retention_pct
FROM cohort_segment_data c
JOIN cohort_sizes_segment cs ON
    c.cohort_month = cs.cohort_month
    AND c.plan_type = cs.plan_type
    AND c.segment = cs.segment
ORDER BY c.cohort_month DESC, c.plan_type, c.segment, c.months_since_signup;
```

### 5.5 Retention Cohort Pivot (Monthly Format)

```sql
-- Creates readable pivot table of retention cohorts
WITH monthly_retention AS (
    -- [Use previous cohort retention query to generate base data]
    SELECT
        cohort_month,
        months_since_acquisition,
        retention_percentage
    FROM (
        -- Insert previous cohort query here
    ) base_data
)
SELECT
    cohort_month,
    ROUND(MAX(CASE WHEN months_since_acquisition = 0 THEN retention_percentage END), 1) AS M0,
    ROUND(MAX(CASE WHEN months_since_acquisition = 1 THEN retention_percentage END), 1) AS M1,
    ROUND(MAX(CASE WHEN months_since_acquisition = 2 THEN retention_percentage END), 1) AS M2,
    ROUND(MAX(CASE WHEN months_since_acquisition = 3 THEN retention_percentage END), 1) AS M3,
    ROUND(MAX(CASE WHEN months_since_acquisition = 4 THEN retention_percentage END), 1) AS M4,
    ROUND(MAX(CASE WHEN months_since_acquisition = 5 THEN retention_percentage END), 1) AS M5,
    ROUND(MAX(CASE WHEN months_since_acquisition = 6 THEN retention_percentage END), 1) AS M6
FROM monthly_retention
GROUP BY cohort_month
ORDER BY cohort_month DESC;
```

---

## Case Studies: Netflix & Spotify

### 6.1 Netflix Retention Strategy

#### Context
- Streaming video on-demand (SVOD) market leader
- Highly competitive with Amazon Prime, Disney+
- High customer acquisition cost (~$8-15 per user)
- Critical to maximize lifetime value through retention

#### Netflix's Retention Playbook

**1. Personalized Recommendations**
- Algorithm analyzes: watch history, ratings, completion rates
- 80% of watch time comes from recommendations
- Continuous A/B testing of recommendation algorithms
- Reduces decision fatigue (paradox of choice)

**Retention Impact**: 35-50% improvement in engagement
**Implementation**: ML models with 1B+ training parameters

**2. Content Refresh Cycle**
- New content 2-3x per week
- Reduces "nothing to watch" churn trigger
- Strategic release timing (especially Fridays)
- Data-driven content acquisition decisions

**Retention Impact**: 15-25% increase in monthly engagement

**3. Smart Downloads**
- Offline viewing prevents switching to competitors
- AI suggests content to download based on taste
- Mobile users especially engaged (higher retention)

**Retention Impact**: 5-10% increase in app engagement

**4. Personalized Notifications**
- Not push notification spam (high unsubscribe)
- Triggered by: new releases matching watch history, trending, recommendations
- Timing optimized per user
- A/B tested messaging

**Retention Impact**: 3-5% lift in session frequency

**5. Segmented Pricing**
- Ad-supported, Standard, Premium tiers
- Reduces churn from price sensitivity
- Easy tier upgrade path
- Family sharing (stickiness lever)

**Retention Impact**: 20-30% reduction in price-related churn

#### Netflix Retention Metrics

| Metric | Netflix | Industry Avg |
|--------|---------|-------------|
| D1 Retention | 60-70% | 30-40% |
| M1 Retention | 45-50% | 15-20% |
| M3 Retention | 35-40% | 5-10% |
| Annual Churn | 20-25% | 35-45% |
| LTV:CAC Ratio | 4.5x | 2.5x |

**Key Learning**: Investment in personalization compounds retention over time. Netflix spends ~2B annually on content/engineering—justified by retention metrics.

---

### 6.2 Spotify Retention Strategy

#### Context
- Music streaming with freemium + premium model
- Competition from Apple Music, Amazon Music, YouTube Music
- Freemium crucial for customer acquisition
- Audio-first experience with high usage variability

#### Spotify's Retention Playbook

**1. Freemium Conversion Funnel**
- Free tier: 30-hour/month limit, ads
- Paywall placement: After ~2 weeks of use
- Conversion rate: 2-5% (industry leading)
- Once premium → high switching costs (playlists, history)

**Retention Impact**: Freemium users 3x more likely to convert if retained 14 days

**2. Playlist Stickiness**
- User-generated + curated playlists
- Collaborative playlists (social stickiness)
- Algorithmic playlists (Discover Weekly, Release Radar)
- Search and playlist discovery reduces churn

**Retention Impact**: Users with 5+ playlists have 5x lower churn

**3. Social Features**
- Friend activity feed
- Shared listening sessions
- Collaborative playlists
- Social proof drives engagement

**Retention Impact**: 20-30% higher retention for social-active users

**4. Personalized Discovery**
- Discover Weekly (Friday release)
- Release Radar (personalized new releases)
- Song/artist recommendations in feed
- Weekly emails with personalized content

**Retention Impact**: 40-60% engagement lift from personalization

**5. Cross-Device Continuity**
- Seamless switching: phone → desktop → car
- Sync of listening history/preferences
- Offline download capability
- Removes friction

**Retention Impact**: Multi-device users 6x less likely to churn

#### Spotify Retention Metrics

| Metric | Spotify Free | Spotify Premium | Gap |
|--------|--------------|-----------------|-----|
| D1 Retention | 45% | 75% | 30pp |
| M1 Retention | 28% | 65% | 37pp |
| M3 Retention | 12% | 58% | 46pp |
| Annual Churn | 72% | 18% | 54pp |
| Free→Premium Conversion | 2.5% | - | - |

**Key Learning**: Freemium model drives massive user base, but conversion/retention is make-or-break. Spotify invested heavily in personalization (Discover Weekly alone retained 30M+ premium subscribers).

#### Spotify Churn Prediction Model

**Features Used** (inferred from public filings):
```
Behavioral:
- Days since last listen
- Listening hours per week
- Song skip rate
- New artist discovery rate
- Playlist creation frequency
- Social activity (follows, shares)

Account:
- Tenure (free vs premium)
- Device types used
- Geographic market
- Plan tier

Temporal:
- Seasonality (summer < winter listening)
- Time to premium conversion
- Engagement trend (improving/declining)
```

**Risk Scoring**:
```
Low Risk (Retention 90%+):
- Premium user 6+ months
- 10+ hours/week listening
- 2+ playlists created
- Active social features

Medium Risk (Retention 60-70%):
- Free user 2-4 weeks
- 5-10 hours/week listening
- No playlist creation

High Risk (Churn 40%+):
- Free user with <5 hours/week
- 0 playlist engagement
- No social activity
- All listening in one genre
```

---

## Benchmarks and KPIs

### 7.1 Industry Benchmarks by Category

#### SaaS (B2B)

| Metric | Enterprise | Mid-Market | SMB |
|--------|-----------|-----------|-----|
| D1 Retention | 65-75% | 55-65% | 45-55% |
| M1 Retention | 50-60% | 40-50% | 30-40% |
| M3 Retention | 25-35% | 15-25% | 8-15% |
| Annual Churn | 5-10% | 15-25% | 35-50% |
| LTV:CAC | 3.5-5x | 2-3x | 1-2x |

**Notes**:
- Enterprise: Lower churn, longer sales cycle, higher switching costs
- SMB: Higher churn, price-sensitive, feature-light
- Mid-Market: Balanced between two

#### Mobile Apps (Consumer)

| Metric | Gaming | Social | Utility | E-Commerce |
|--------|--------|--------|---------|-----------|
| D1 | 20-35% | 40-55% | 25-40% | 15-25% |
| D7 | 8-15% | 25-35% | 12-20% | 5-10% |
| D30 | 2-5% | 8-12% | 4-8% | 1-3% |
| M3 | <1% | 2-4% | 1-2% | <1% |

**Top performers**:
- Gaming: Pokemon GO (50%+ D30), Candy Crush (15-20% D30)
- Social: TikTok (60%+ D1), Snapchat (50%+ D30)
- Utility: Gmail (95%+ D30), Maps (80%+ D30)

#### Subscription (B2C)

| Service | D1 | M1 | M3 | Annual Churn |
|---------|-----|-----|-----|-------------|
| Streaming Video | 55-70% | 40-50% | 30-40% | 20-30% |
| Music Streaming | 45-60% | 30-40% | 18-28% | 25-35% |
| Fitness | 35-45% | 15-25% | 5-10% | 60-70% |
| Meal Kit | 30-40% | 10-20% | 3-8% | 70-80% |
| Cloud Storage | 50-65% | 40-50% | 30-40% | 10-20% |

### 7.2 Retention Maturity Levels

#### Level 1: Tracking Only
- Basic DAU/MAU metrics
- No cohort analysis
- Ad hoc reporting
- **Typical Churn**: 40-60% annually
- **Time to Insight**: 2-4 weeks

#### Level 2: Cohort Analysis
- Monthly cohort tables
- D1, D7, D30 metrics
- Segment-level retention
- **Typical Churn**: 30-45% annually
- **Time to Insight**: 1 week
- **Required Skills**: SQL + analytics

#### Level 3: Predictive Modeling
- Churn prediction models (Logistic Regression, Random Forest)
- Risk scoring system
- Targeted interventions
- **Typical Churn**: 20-35% annually
- **Time to Insight**: Real-time
- **Required Skills**: Data science, ML

#### Level 4: Personalized Retention
- AI-driven personalization
- Dynamic offer optimization
- Real-time intervention
- **Typical Churn**: 10-20% annually
- **Time to Insight**: Immediate
- **Required Skills**: Data science, engineering, product

#### Level 5: Retention Mastery
- Multi-touch attribution
- Optimal intervention timing
- Complex segmentation
- Lifecycle optimization
- **Typical Churn**: 5-15% annually
- **Time to Insight**: <1 minute
- **Required Skills**: Advanced analytics, ML, experimentation

### 7.3 Key Retention KPIs Dashboard

```
Dashboard: Retention Health Check (Updated Daily)

Core Metrics (Week-over-Week):
├─ D1 Retention: 45% (↑2% vs last week) [Target: 50%]
├─ D7 Retention: 22% (↓1% vs last week) [Target: 25%]
├─ D30 Retention: 8% (→ stable) [Target: 12%]
└─ Churn Rate: 12% monthly (↑0.5%) [Target: <10%]

Segment Performance:
├─ Free Users: 28% M1 retention (↓3%)
├─ Premium Users: 65% M1 retention (↑2%)
├─ Annual Users: 85% M1 retention (↑1%)
└─ Trial Users: 15% M1 retention (↓5%) [ACTION NEEDED]

Churn Risk:
├─ High Risk (>60%): 1,245 users [28 actions sent]
├─ Medium Risk (40-60%): 3,420 users [156 actions sent]
├─ Low Risk (<40%): 8,234 users [1,042 engaged]
└─ High-Value At Risk: 42 users >$10k MRR [URGENT]

Win-Back Performance:
├─ Emails Sent (30d): 5,234
├─ Open Rate: 28% (↓2%)
├─ Click Rate: 8% (stable)
├─ Reactivation Rate: 3.2% (↑0.5%)
└─ Revenue Recovered: $45,320

Content Engagement:
├─ Features Used by Users: 4.2 avg (target: 5+)
├─ Content Consumption: 2.3 items/user/week (target: 3+)
├─ Time Spent: 34 min/user/week (target: 45+)
└─ NPS Score: 42 (target: 50+)
```

---

## Implementation Roadmap

### 8.1 30-Day Quick Start

#### Week 1: Foundation
- [ ] Day 1-2: Set up retention tracking (events, user table)
- [ ] Day 3-4: Build cohort table (monthly cohorts)
- [ ] Day 5-7: Calculate D1, D7, D30, M3 metrics

**Deliverable**: Weekly cohort table with 8 weeks of data

#### Week 2: Analysis
- [ ] Day 8-9: Build trend analysis (retention improving/declining)
- [ ] Day 10-11: Segment cohorts (by plan, acquisition source)
- [ ] Day 12-14: Create visualizations (retention curves, heatmaps)

**Deliverable**: Cohort analysis dashboard with trends

#### Week 3: Prediction
- [ ] Day 15-16: Feature engineering (20 churn predictors)
- [ ] Day 17-19: Build logistic regression model
- [ ] Day 20-21: Validate model (ROC-AUC >0.75)

**Deliverable**: Churn risk scoring system

#### Week 4: Action
- [ ] Day 22-23: Build win-back campaign
- [ ] Day 24-26: A/B test retention interventions
- [ ] Day 27-28: Measure impact (% improvement)
- [ ] Day 29-30: Document and iterate

**Deliverable**: 5-10% retention improvement within 30 days

### 8.2 90-Day Growth Plan

#### Month 2: Sophistication
- Advanced segmentation (RFM, behavioral clusters)
- Multi-touch attribution (which touchpoint drives retention?)
- Cohort comparison (winners vs losers analysis)
- Competitive benchmarking
- **Goal**: Identify top 3 retention levers

#### Month 3: Optimization
- Implement top 3 interventions at scale
- A/B test messaging, timing, offers
- Predictive model improvement (add 10 new features)
- Win-back campaign automation
- **Goal**: Achieve 5-15% churn reduction

---

## Summary: Retention Excellence Checklist

```
Foundation (Must Have):
□ Cohort retention table (monthly)
□ D1, D7, D30 metrics tracked
□ Churn rate calculation
□ Segment-level analysis
□ Basic trend analysis

Intermediate (Should Have):
□ Churn prediction model (>0.75 ROC-AUC)
□ Risk scoring system
□ Win-back campaign framework
□ Retention curve fitting
□ Competitive benchmarking

Advanced (Nice to Have):
□ Multi-touch attribution
□ Dynamic offer optimization
□ Personalized intervention engine
□ Predictive LTV
□ Resurrection channel mix
```

---

## Appendix: Tools and Resources

### Analytics Platforms
- Amplitude: Event-based cohorts and retention
- Mixpanel: Funnel + retention analysis
- Segment: Data warehouse for retention queries
- Looker/Tableau: Retention dashboards

### SQL Databases
- Snowflake: Ideal for cohort analysis at scale
- BigQuery: Serverless SQL for retention
- Postgres: Open-source cohort queries

### Python Libraries
- scikit-learn: Churn prediction models
- pandas: Cohort table creation
- statsmodels: Statistical testing
- matplotlib/plotly: Retention visualizations

### Reading
- "Lean Product Playbook" by Dan Olsen
- "Metrics That Matter" by Kleiner Perkins
- Reforge: Retention Masterclass

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Product Analytics Team
**Maturity Level**: 5 - Retention Mastery

This guide provides battle-tested frameworks used by Netflix, Spotify, and leading SaaS companies. Implementation should begin with foundation metrics, progress to predictive modeling, and culminate in real-time personalized retention optimization.
