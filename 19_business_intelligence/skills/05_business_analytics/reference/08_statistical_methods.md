# Statistical Methods Reference

Comprehensive guide to statistical techniques commonly used in business analytics.

## Descriptive Statistics

### Central Tendency

**Mean (Average)**:
```sql
-- Calculate mean
SELECT
  AVG(order_value) as mean_order_value,
  AVG(session_duration) as mean_session_duration
FROM orders;
```

```python
import numpy as np

# Mean
mean_value = np.mean(data)

# Weighted mean
weighted_mean = np.average(data, weights=weights)
```

**Median**:
```sql
-- Median using PERCENTILE_CONT
SELECT
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY order_value) as median_order_value
FROM orders;
```

```python
# Median
median_value = np.median(data)
```

**Mode**:
```sql
-- Mode (most frequent value)
SELECT
  order_value,
  COUNT(*) as frequency
FROM orders
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1;
```

### Spread/Dispersion

**Variance and Standard Deviation**:
```sql
-- Population variance and standard deviation
SELECT
  VARIANCE(order_value) as variance,
  STDDEV(order_value) as std_dev,
  STDDEV(order_value) / NULLIF(AVG(order_value), 0) * 100 as coefficient_of_variation
FROM orders;
```

```python
import numpy as np

# Population std dev
std_pop = np.std(data)

# Sample std dev (Bessel's correction)
std_sample = np.std(data, ddof=1)

# Variance
variance = np.var(data)

# Coefficient of variation
cv = (std_sample / np.mean(data)) * 100
```

**Range and Interquartile Range**:
```sql
-- Range and IQR
SELECT
  MAX(order_value) - MIN(order_value) as range,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY order_value) -
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY order_value) as iqr,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY order_value) as q1,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY order_value) as q2_median,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY order_value) as q3
FROM orders;
```

```python
# Quartiles and IQR
q1 = np.percentile(data, 25)
q2 = np.percentile(data, 50)  # median
q3 = np.percentile(data, 75)
iqr = q3 - q1

# Outlier bounds (Tukey's method)
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
```

### Distribution Shape

**Skewness and Kurtosis**:
```python
from scipy import stats

# Skewness (measure of asymmetry)
# 0 = symmetric, >0 = right-skewed, <0 = left-skewed
skewness = stats.skew(data)

# Kurtosis (measure of tail heaviness)
# 0 = normal, >0 = heavy tails, <0 = light tails
kurtosis = stats.kurtosis(data)

print(f"Skewness: {skewness:.3f}")
print(f"Kurtosis: {kurtosis:.3f}")
```

## Hypothesis Testing

### T-Tests

**One-Sample T-Test**:
```python
from scipy import stats

# Test if sample mean is significantly different from hypothesized value
data = [23, 25, 27, 24, 26, 28, 22, 25, 24, 26]
hypothesized_mean = 20

t_stat, p_value = stats.ttest_1samp(data, hypothesized_mean)

print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("Reject null hypothesis: Mean is significantly different from 20")
else:
    print("Fail to reject null hypothesis")
```

**Independent Two-Sample T-Test**:
```python
# Compare means of two independent groups
control_group = [45, 50, 52, 48, 51, 49, 47, 50]
treatment_group = [55, 58, 60, 56, 59, 57, 61, 58]

t_stat, p_value = stats.ttest_ind(control_group, treatment_group)

print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_value:.4f}")

# Calculate effect size (Cohen's d)
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

effect_size = cohens_d(treatment_group, control_group)
print(f"Effect size (Cohen's d): {effect_size:.3f}")
```

**Paired T-Test**:
```python
# Compare paired observations (before/after)
before = [120, 135, 128, 142, 138, 130, 125, 133]
after = [115, 130, 125, 138, 135, 128, 122, 130]

t_stat, p_value = stats.ttest_rel(before, after)

print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_value:.4f}")
```

### Chi-Square Tests

**Chi-Square Test for Independence**:
```python
from scipy.stats import chi2_contingency
import pandas as pd

# Contingency table: Channel vs Conversion
data = {
    'Converted': [150, 180, 120],
    'Not Converted': [350, 320, 380]
}
df = pd.DataFrame(data, index=['Email', 'Social', 'Search'])

print("Contingency Table:")
print(df)

# Perform chi-square test
chi2, p_value, dof, expected = chi2_contingency(df)

print(f"\nChi-square statistic: {chi2:.3f}")
print(f"P-value: {p_value:.4f}")
print(f"Degrees of freedom: {dof}")
print("\nExpected frequencies:")
print(pd.DataFrame(expected, index=df.index, columns=df.columns))

if p_value < 0.05:
    print("\nResult: Channel and conversion are significantly associated")
else:
    print("\nResult: No significant association between channel and conversion")
```

**Chi-Square Goodness of Fit**:
```python
# Test if observed distribution matches expected
observed = [45, 38, 42, 50, 25]  # Observed frequencies
expected_proportions = [0.2, 0.2, 0.2, 0.2, 0.2]  # Expected uniform distribution
expected = [sum(observed) * p for p in expected_proportions]

chi2, p_value = stats.chisquare(observed, expected)

print(f"Chi-square: {chi2:.3f}, P-value: {p_value:.4f}")
```

### ANOVA (Analysis of Variance)

**One-Way ANOVA**:
```python
# Compare means across multiple groups
group_a = [23, 25, 27, 24, 26]
group_b = [28, 30, 29, 31, 28]
group_c = [32, 34, 33, 35, 32]

f_stat, p_value = stats.f_oneway(group_a, group_b, group_c)

print(f"F-statistic: {f_stat:.3f}")
print(f"P-value: {p_value:.4f}")

# Post-hoc test (Tukey HSD) if ANOVA is significant
if p_value < 0.05:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    import pandas as pd

    data = pd.DataFrame({
        'value': group_a + group_b + group_c,
        'group': ['A']*len(group_a) + ['B']*len(group_b) + ['C']*len(group_c)
    })

    tukey = pairwise_tukeyhsd(data['value'], data['group'])
    print("\nPost-hoc Tukey HSD:")
    print(tukey)
```

## Correlation and Regression

### Correlation Analysis

**Pearson Correlation**:
```python
from scipy.stats import pearsonr

# Linear correlation
ad_spend = [1000, 1500, 2000, 2500, 3000]
revenue = [15000, 20000, 25000, 28000, 32000]

correlation, p_value = pearsonr(ad_spend, revenue)

print(f"Pearson correlation: {correlation:.3f}")
print(f"P-value: {p_value:.4f}")

# Interpretation
if abs(correlation) < 0.3:
    strength = "weak"
elif abs(correlation) < 0.7:
    strength = "moderate"
else:
    strength = "strong"

print(f"This is a {strength} {'positive' if correlation > 0 else 'negative'} correlation")
```

**Spearman Rank Correlation** (for non-linear relationships):
```python
from scipy.stats import spearmanr

correlation, p_value = spearmanr(ad_spend, revenue)
print(f"Spearman correlation: {correlation:.3f}")
```

**Correlation Matrix**:
```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Create correlation matrix
df = pd.DataFrame({
    'ad_spend': [1000, 1500, 2000, 2500, 3000],
    'email_sends': [5000, 6000, 7000, 7500, 8000],
    'website_visits': [12000, 15000, 18000, 20000, 22000],
    'revenue': [15000, 20000, 25000, 28000, 32000]
})

correlation_matrix = df.corr()

# Visualize
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
            vmin=-1, vmax=1, square=True)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()
```

### Linear Regression

**Simple Linear Regression**:
```python
from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt

# Simple linear regression
x = np.array([1, 2, 3, 4, 5])
y = np.array([2.1, 3.9, 6.2, 7.8, 10.1])

slope, intercept, r_value, p_value, std_err = linregress(x, y)

print(f"Equation: y = {slope:.2f}x + {intercept:.2f}")
print(f"R-squared: {r_value**2:.3f}")
print(f"P-value: {p_value:.4f}")
print(f"Standard error: {std_err:.3f}")

# Predictions
x_pred = np.array([6, 7, 8])
y_pred = slope * x_pred + intercept
print(f"\nPredictions for x={x_pred}: {y_pred}")

# Plot
plt.scatter(x, y, label='Actual')
plt.plot(x, slope*x + intercept, 'r-', label='Fitted line')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

**Multiple Linear Regression**:
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

# Multiple predictors
X = np.array([
    [1000, 50],   # ad_spend, email_campaigns
    [1500, 60],
    [2000, 70],
    [2500, 65],
    [3000, 80]
])
y = np.array([15000, 20000, 25000, 28000, 32000])  # revenue

model = LinearRegression()
model.fit(X, y)

# Model coefficients
print(f"Intercept: {model.intercept_:.2f}")
print(f"Coefficients: {model.coef_}")
print(f"Equation: Revenue = {model.intercept_:.2f} + {model.coef_[0]:.2f}*ad_spend + {model.coef_[1]:.2f}*emails")

# Model performance
y_pred = model.predict(X)
r2 = r2_score(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))

print(f"\nR-squared: {r2:.3f}")
print(f"RMSE: {rmse:.2f}")

# Predictions
new_data = np.array([[3500, 85]])
prediction = model.predict(new_data)
print(f"\nPredicted revenue for ad_spend=3500, emails=85: ${prediction[0]:.2f}")
```

### Logistic Regression

**Binary Classification**:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import numpy as np

# Features: [pages_viewed, time_on_site, previous_purchases]
X = np.array([
    [3, 45, 0],
    [5, 120, 1],
    [2, 30, 0],
    [8, 180, 2],
    [4, 90, 0],
    [10, 240, 3],
    [1, 15, 0],
    [7, 150, 1]
])
y = np.array([0, 1, 0, 1, 0, 1, 0, 1])  # 1 = purchased, 0 = did not purchase

model = LogisticRegression()
model.fit(X, y)

# Predictions
y_pred = model.predict(X)
y_prob = model.predict_proba(X)[:, 1]  # Probability of class 1

print("Classification Report:")
print(classification_report(y, y_pred))

print(f"\nROC AUC Score: {roc_auc_score(y, y_prob):.3f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y, y_pred))

# Feature importance (coefficients)
print("\nFeature coefficients:")
for i, coef in enumerate(model.coef_[0]):
    print(f"Feature {i}: {coef:.3f}")
```

## Time Series Analysis

### Trend Analysis

**Moving Average**:
```python
import pandas as pd

df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=30, freq='D'),
    'revenue': np.random.normal(1000, 100, 30)
})

# Simple moving average
df['ma_7'] = df['revenue'].rolling(window=7).mean()
df['ma_14'] = df['revenue'].rolling(window=14).mean()

# Exponential moving average
df['ema_7'] = df['revenue'].ewm(span=7, adjust=False).mean()

print(df.head(15))
```

**Seasonality Detection**:
```python
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd

# Create time series with seasonality
dates = pd.date_range('2023-01-01', periods=365, freq='D')
trend = np.linspace(100, 200, 365)
seasonality = 50 * np.sin(2 * np.pi * np.arange(365) / 365)
noise = np.random.normal(0, 10, 365)
values = trend + seasonality + noise

df = pd.DataFrame({'date': dates, 'value': values})
df.set_index('date', inplace=True)

# Decompose
decomposition = seasonal_decompose(df['value'], model='additive', period=7)

# Plot components
fig, axes = plt.subplots(4, 1, figsize=(12, 10))
decomposition.observed.plot(ax=axes[0], title='Observed')
decomposition.trend.plot(ax=axes[1], title='Trend')
decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
decomposition.resid.plot(ax=axes[3], title='Residual')
plt.tight_layout()
plt.show()
```

### Forecasting

**ARIMA Model**:
```python
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

# Fit ARIMA model
model = ARIMA(df['value'], order=(1, 1, 1))  # (p, d, q)
fitted_model = model.fit()

print(fitted_model.summary())

# Forecast
forecast_steps = 30
forecast = fitted_model.forecast(steps=forecast_steps)

print(f"\nForecast for next {forecast_steps} periods:")
print(forecast)
```

**Simple Exponential Smoothing**:
```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Fit model
model = ExponentialSmoothing(df['value'], seasonal=None, trend=None)
fitted = model.fit()

# Forecast
forecast = fitted.forecast(steps=30)
print(forecast)
```

## Statistical Power and Sample Size

### Power Analysis

```python
from statsmodels.stats.power import ttest_power, tt_ind_solve_power

# Calculate required sample size for desired power
effect_size = 0.5  # Cohen's d
alpha = 0.05  # Significance level
power = 0.80  # Desired power (1 - beta)

required_n = tt_ind_solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    alternative='two-sided'
)

print(f"Required sample size per group: {int(np.ceil(required_n))}")

# Calculate power for given sample size
actual_power = ttest_power(
    effect_size=effect_size,
    nobs=100,  # Sample size
    alpha=alpha,
    alternative='two-sided'
)

print(f"Statistical power with n=100: {actual_power:.2%}")
```

## Confidence Intervals

```python
from scipy import stats
import numpy as np

def confidence_interval(data, confidence=0.95):
    """Calculate confidence interval for mean"""
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)  # Standard error of mean

    # t-distribution for small samples, normal for large
    if n < 30:
        margin_of_error = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    else:
        margin_of_error = std_err * stats.norm.ppf((1 + confidence) / 2)

    ci_lower = mean - margin_of_error
    ci_upper = mean + margin_of_error

    return mean, ci_lower, ci_upper

# Example
data = [45, 50, 52, 48, 51, 49, 47, 50, 53, 46]
mean, ci_lower, ci_upper = confidence_interval(data, confidence=0.95)

print(f"Mean: {mean:.2f}")
print(f"95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
```

**Confidence Interval for Proportions**:
```python
from statsmodels.stats.proportion import proportion_confint

# Conversion rate confidence interval
conversions = 45
total_visitors = 500

ci_lower, ci_upper = proportion_confint(
    conversions,
    total_visitors,
    alpha=0.05,  # 95% confidence
    method='wilson'  # Wilson score interval (recommended)
)

conversion_rate = conversions / total_visitors

print(f"Conversion rate: {conversion_rate:.2%}")
print(f"95% CI: [{ci_lower:.2%}, {ci_upper:.2%}]")
```

## Non-Parametric Tests

### Mann-Whitney U Test

```python
from scipy.stats import mannwhitneyu

# Non-parametric alternative to independent t-test
# Use when data is not normally distributed
group1 = [23, 25, 27, 24, 26, 45, 22]  # Contains outlier
group2 = [28, 30, 29, 31, 28, 27, 30]

statistic, p_value = mannwhitneyu(group1, group2, alternative='two-sided')

print(f"U-statistic: {statistic:.3f}")
print(f"P-value: {p_value:.4f}")
```

### Kruskal-Wallis Test

```python
from scipy.stats import kruskal

# Non-parametric alternative to one-way ANOVA
group_a = [23, 25, 27, 24, 26]
group_b = [28, 30, 29, 31, 28]
group_c = [32, 34, 33, 35, 32]

statistic, p_value = kruskal(group_a, group_b, group_c)

print(f"H-statistic: {statistic:.3f}")
print(f"P-value: {p_value:.4f}")
```

## Multiple Testing Correction

### Bonferroni Correction

```python
from statsmodels.stats.multitest import multipletests

# P-values from multiple tests
p_values = [0.01, 0.04, 0.03, 0.08, 0.002]

# Apply Bonferroni correction
reject, corrected_p, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method='bonferroni'
)

for i, (p, p_corr, rej) in enumerate(zip(p_values, corrected_p, reject)):
    print(f"Test {i+1}: p={p:.4f}, corrected p={p_corr:.4f}, reject={rej}")
```

### False Discovery Rate (FDR)

```python
# Benjamini-Hochberg procedure
reject, corrected_p, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method='fdr_bh'  # Benjamini-Hochberg
)

print("\nFDR correction:")
for i, (p, p_corr, rej) in enumerate(zip(p_values, corrected_p, reject)):
    print(f"Test {i+1}: p={p:.4f}, corrected p={p_corr:.4f}, reject={rej}")
```

## Practical Tips

### Assumptions Checking

```python
# Check normality (Shapiro-Wilk test)
from scipy.stats import shapiro

statistic, p_value = shapiro(data)
if p_value > 0.05:
    print("Data appears normally distributed")
else:
    print("Data does not appear normally distributed")

# Check homogeneity of variance (Levene's test)
from scipy.stats import levene

statistic, p_value = levene(group1, group2, group3)
if p_value > 0.05:
    print("Variances are homogeneous")
else:
    print("Variances are not homogeneous")
```

### Effect Size Calculation

```python
def calculate_effect_sizes(group1, group2):
    """Calculate multiple effect size measures"""
    mean1, mean2 = np.mean(group1), np.mean(group2)
    std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    n1, n2 = len(group1), len(group2)

    # Cohen's d
    pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))
    cohens_d = (mean1 - mean2) / pooled_std

    # Glass's delta (use control group std)
    glass_delta = (mean1 - mean2) / std2

    # Hedges' g (corrected for small samples)
    correction = 1 - (3 / (4 * (n1 + n2) - 9))
    hedges_g = cohens_d * correction

    return {
        'cohens_d': cohens_d,
        'glass_delta': glass_delta,
        'hedges_g': hedges_g
    }
```

## Quick Reference

| Test | Purpose | Assumptions |
|------|---------|-------------|
| T-test | Compare 2 means | Normal distribution, equal variance |
| ANOVA | Compare 3+ means | Normal distribution, equal variance |
| Chi-square | Test independence (categorical) | Expected frequency ≥ 5 |
| Mann-Whitney U | Compare 2 groups (non-parametric) | None |
| Kruskal-Wallis | Compare 3+ groups (non-parametric) | None |
| Pearson correlation | Linear relationship | Normal distribution |
| Spearman correlation | Monotonic relationship | None |

## Significance Levels

- **p < 0.001**: Highly significant (***)
- **p < 0.01**: Very significant (**)
- **p < 0.05**: Significant (*)
- **p ≥ 0.05**: Not significant (ns)
