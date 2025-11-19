# A/B Testing Framework Reference

Comprehensive guide to designing, running, and analyzing A/B tests (randomized controlled experiments).

## What is A/B Testing?

**Definition**: A randomized experiment comparing two or more variants to determine which performs better on a specific metric.

**Components**:
- **Control (A)**: Baseline/current experience
- **Treatment (B)**: New variant being tested
- **Randomization**: Users randomly assigned to variants
- **Metrics**: Quantifiable outcomes to measure
- **Statistical Analysis**: Determine if differences are significant

## Experimental Design

### 1. Define Hypothesis

```markdown
**Good Hypothesis Template**:

IF [change we make]
THEN [expected outcome]
BECAUSE [reasoning/theory]

**Example**:
IF we change the CTA button from blue to green
THEN conversion rate will increase by at least 10%
BECAUSE green creates more urgency and stands out more
```

### 2. Select Metrics

**Primary Metric**: Main outcome of interest
```python
class ABTestMetrics:
    """Define A/B test metrics"""

    PRIMARY_METRICS = {
        'conversion_rate': 'Percentage of users who convert',
        'revenue_per_user': 'Average revenue per user',
        'retention_rate': 'Percentage of users retained',
        'engagement_rate': 'Percentage of users engaged'
    }

    SECONDARY_METRICS = {
        'clicks': 'Number of clicks',
        'time_on_page': 'Average time spent',
        'bounce_rate': 'Percentage who leave immediately',
        'pages_per_session': 'Average pages viewed'
    }

    GUARDRAIL_METRICS = {
        'page_load_time': 'Ensure performance not degraded',
        'error_rate': 'Monitor for technical issues',
        'support_tickets': 'Watch for user confusion'
    }
```

### 3. Calculate Sample Size

**Sample Size Formula**:
```python
import numpy as np
from scipy import stats

def calculate_sample_size(
    baseline_rate,
    minimum_detectable_effect,
    alpha=0.05,
    power=0.80,
    two_tailed=True
):
    """
    Calculate required sample size for A/B test

    Args:
        baseline_rate: Current conversion rate (e.g., 0.10 for 10%)
        minimum_detectable_effect: Minimum relative improvement (e.g., 0.10 for 10% lift)
        alpha: Significance level (Type I error rate)
        power: Statistical power (1 - Type II error rate)
        two_tailed: Whether test is two-tailed

    Returns:
        Required sample size per variant
    """
    # Calculate effect size
    treatment_rate = baseline_rate * (1 + minimum_detectable_effect)

    # Pooled probability
    p_pooled = (baseline_rate + treatment_rate) / 2

    # Z-scores
    if two_tailed:
        z_alpha = stats.norm.ppf(1 - alpha / 2)
    else:
        z_alpha = stats.norm.ppf(1 - alpha)

    z_beta = stats.norm.ppf(power)

    # Sample size calculation
    numerator = (z_alpha + z_beta) ** 2 * 2 * p_pooled * (1 - p_pooled)
    denominator = (treatment_rate - baseline_rate) ** 2

    n = numerator / denominator

    return int(np.ceil(n))

# Example
baseline_conversion = 0.10  # 10%
mde = 0.15  # Want to detect 15% relative improvement

sample_size = calculate_sample_size(
    baseline_rate=baseline_conversion,
    minimum_detectable_effect=mde,
    alpha=0.05,
    power=0.80
)

print(f"Required sample size per variant: {sample_size:,}")
print(f"Total sample needed: {sample_size * 2:,}")
```

**Runtime Calculation**:
```python
def calculate_test_duration(required_sample_size, daily_traffic):
    """Calculate how long test needs to run"""
    days = required_sample_size / daily_traffic
    weeks = days / 7

    return {
        'days': np.ceil(days),
        'weeks': np.ceil(weeks),
        'recommended_weeks': np.ceil(weeks) + 1  # Add buffer
    }

# Example
duration = calculate_test_duration(
    required_sample_size=10000,
    daily_traffic=1000
)

print(f"Test duration: {duration['days']} days ({duration['weeks']} weeks)")
print(f"Recommended: {duration['recommended_weeks']} weeks (includes full week cycles)")
```

## Test Implementation

### Randomization

**Server-Side Randomization**:
```python
import hashlib

def assign_variant(user_id, test_name, variants=['control', 'treatment'], salt=''):
    """
    Deterministic random assignment using hashing

    Args:
        user_id: Unique user identifier
        test_name: Name of the test
        variants: List of variant names
        salt: Optional salt for hash

    Returns:
        Assigned variant name
    """
    # Create hash of user_id + test_name + salt
    hash_input = f"{user_id}:{test_name}:{salt}".encode()
    hash_value = hashlib.md5(hash_input).hexdigest()

    # Convert hash to integer and map to variant
    hash_int = int(hash_value, 16)
    variant_index = hash_int % len(variants)

    return variants[variant_index]

# Example usage
user_variant = assign_variant(
    user_id='user_12345',
    test_name='cta_button_test',
    variants=['control', 'treatment']
)
print(f"User assigned to: {user_variant}")
```

**Traffic Allocation**:
```python
def assign_variant_weighted(user_id, test_name, variant_weights):
    """
    Assign variant with custom traffic allocation

    Args:
        user_id: Unique user identifier
        test_name: Name of the test
        variant_weights: Dict of variant names to weights
                        e.g., {'control': 50, 'treatment_a': 25, 'treatment_b': 25}

    Returns:
        Assigned variant name
    """
    import hashlib
    import numpy as np

    # Create hash
    hash_input = f"{user_id}:{test_name}".encode()
    hash_value = hashlib.md5(hash_input).hexdigest()
    hash_int = int(hash_value, 16)

    # Normalize weights to percentages
    total_weight = sum(variant_weights.values())
    cumulative = 0
    thresholds = {}

    for variant, weight in variant_weights.items():
        cumulative += weight / total_weight
        thresholds[variant] = cumulative

    # Map hash to [0, 1] range
    random_value = (hash_int % 10000) / 10000

    # Assign based on thresholds
    for variant, threshold in thresholds.items():
        if random_value < threshold:
            return variant

# Example
variant = assign_variant_weighted(
    user_id='user_12345',
    test_name='multivariate_test',
    variant_weights={'control': 50, 'treatment_a': 25, 'treatment_b': 25}
)
```

### Event Tracking

```sql
-- Create events table for A/B test tracking
CREATE TABLE ab_test_events (
    event_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    variant VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,  -- 'exposure', 'conversion', 'engagement'
    event_timestamp TIMESTAMP NOT NULL,
    session_id VARCHAR(255),
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast queries
CREATE INDEX idx_test_variant ON ab_test_events(test_name, variant);
CREATE INDEX idx_user_test ON ab_test_events(user_id, test_name);
CREATE INDEX idx_event_timestamp ON ab_test_events(event_timestamp);

-- Track user exposure
INSERT INTO ab_test_events (user_id, test_name, variant, event_type, event_timestamp, session_id)
VALUES ('user_123', 'cta_test', 'treatment', 'exposure', NOW(), 'session_456');

-- Track conversion
INSERT INTO ab_test_events (user_id, test_name, variant, event_type, event_timestamp, properties)
VALUES ('user_123', 'cta_test', 'treatment', 'conversion', NOW(), '{"revenue": 49.99}');
```

## Analysis Methods

### 1. Frequentist Analysis (Classical)

**Two-Proportion Z-Test**:
```python
from scipy.stats import norm
import numpy as np

def two_proportion_ztest(conversions_a, total_a, conversions_b, total_b):
    """
    Perform two-proportion z-test

    Args:
        conversions_a: Number of conversions in control
        total_a: Total users in control
        conversions_b: Number of conversions in treatment
        total_b: Total users in treatment

    Returns:
        Dictionary with test results
    """
    # Conversion rates
    p_a = conversions_a / total_a
    p_b = conversions_b / total_b

    # Pooled proportion
    p_pooled = (conversions_a + conversions_b) / (total_a + total_b)

    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/total_a + 1/total_b))

    # Z-statistic
    z_score = (p_b - p_a) / se

    # P-value (two-tailed)
    p_value = 2 * (1 - norm.cdf(abs(z_score)))

    # Confidence interval for difference
    se_diff = np.sqrt(p_a * (1-p_a) / total_a + p_b * (1-p_b) / total_b)
    ci_lower = (p_b - p_a) - 1.96 * se_diff
    ci_upper = (p_b - p_a) + 1.96 * se_diff

    # Relative improvement
    relative_improvement = (p_b - p_a) / p_a if p_a > 0 else float('inf')

    return {
        'control_rate': p_a,
        'treatment_rate': p_b,
        'absolute_difference': p_b - p_a,
        'relative_improvement': relative_improvement,
        'z_score': z_score,
        'p_value': p_value,
        'confidence_interval': (ci_lower, ci_upper),
        'significant': p_value < 0.05
    }

# Example
results = two_proportion_ztest(
    conversions_a=450,  # Control: 450 conversions
    total_a=10000,      # out of 10,000 users
    conversions_b=520,  # Treatment: 520 conversions
    total_b=10000       # out of 10,000 users
)

print(f"Control rate: {results['control_rate']:.2%}")
print(f"Treatment rate: {results['treatment_rate']:.2%}")
print(f"Absolute difference: {results['absolute_difference']:.2%}")
print(f"Relative improvement: {results['relative_improvement']:.2%}")
print(f"P-value: {results['p_value']:.4f}")
print(f"95% CI: [{results['confidence_interval'][0]:.2%}, {results['confidence_interval'][1]:.2%}]")
print(f"Significant: {results['significant']}")
```

**SQL Analysis**:
```sql
-- Calculate A/B test results
WITH test_summary AS (
  SELECT
    variant,
    COUNT(DISTINCT CASE WHEN event_type = 'exposure' THEN user_id END) as users,
    COUNT(DISTINCT CASE WHEN event_type = 'conversion' THEN user_id END) as conversions,
    COUNT(DISTINCT CASE WHEN event_type = 'conversion' THEN user_id END) * 1.0 /
      NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'exposure' THEN user_id END), 0) as conversion_rate
  FROM ab_test_events
  WHERE test_name = 'cta_button_test'
    AND event_timestamp >= '2024-01-01'
  GROUP BY 1
),
control_metrics AS (
  SELECT conversion_rate as control_rate
  FROM test_summary
  WHERE variant = 'control'
)
SELECT
  ts.variant,
  ts.users,
  ts.conversions,
  ts.conversion_rate,
  (ts.conversion_rate - cm.control_rate) as absolute_lift,
  (ts.conversion_rate - cm.control_rate) / NULLIF(cm.control_rate, 0) * 100 as relative_lift_pct
FROM test_summary ts
CROSS JOIN control_metrics cm
ORDER BY ts.variant;
```

### 2. Bayesian Analysis

**Bayesian A/B Test**:
```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def bayesian_ab_test(conversions_a, total_a, conversions_b, total_b, prior_alpha=1, prior_beta=1):
    """
    Bayesian A/B test using Beta-Binomial model

    Args:
        conversions_a, total_a: Control group data
        conversions_b, total_b: Treatment group data
        prior_alpha, prior_beta: Beta prior parameters

    Returns:
        Dictionary with Bayesian analysis results
    """
    # Posterior distributions (Beta distribution)
    posterior_a = stats.beta(prior_alpha + conversions_a, prior_beta + total_a - conversions_a)
    posterior_b = stats.beta(prior_alpha + conversions_b, prior_beta + total_b - conversions_b)

    # Draw samples from posteriors
    n_samples = 100000
    samples_a = posterior_a.rvs(n_samples)
    samples_b = posterior_b.rvs(n_samples)

    # Probability B beats A
    prob_b_beats_a = np.mean(samples_b > samples_a)

    # Expected loss (if we choose wrong variant)
    expected_loss_a = np.mean(np.maximum(samples_b - samples_a, 0))  # Loss if we choose A
    expected_loss_b = np.mean(np.maximum(samples_a - samples_b, 0))  # Loss if we choose B

    # Credible interval for difference
    diff_samples = samples_b - samples_a
    credible_interval = np.percentile(diff_samples, [2.5, 97.5])

    # Expected improvement
    expected_improvement = np.mean(samples_b - samples_a)

    return {
        'prob_b_beats_a': prob_b_beats_a,
        'prob_a_beats_b': 1 - prob_b_beats_a,
        'expected_improvement': expected_improvement,
        'expected_loss_if_choose_a': expected_loss_a,
        'expected_loss_if_choose_b': expected_loss_b,
        'credible_interval': credible_interval,
        'samples_a': samples_a,
        'samples_b': samples_b
    }

# Example
bayes_results = bayesian_ab_test(
    conversions_a=450,
    total_a=10000,
    conversions_b=520,
    total_b=10000
)

print(f"Probability B beats A: {bayes_results['prob_b_beats_a']:.2%}")
print(f"Expected improvement: {bayes_results['expected_improvement']:.2%}")
print(f"95% Credible Interval: [{bayes_results['credible_interval'][0]:.2%}, {bayes_results['credible_interval'][1]:.2%}]")
print(f"Expected loss if choose A: {bayes_results['expected_loss_if_choose_a']:.4f}")
print(f"Expected loss if choose B: {bayes_results['expected_loss_if_choose_b']:.4f}")

# Visualization
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
x = np.linspace(0.03, 0.07, 1000)
plt.hist(bayes_results['samples_a'], bins=50, alpha=0.5, label='Control', density=True)
plt.hist(bayes_results['samples_b'], bins=50, alpha=0.5, label='Treatment', density=True)
plt.xlabel('Conversion Rate')
plt.ylabel('Density')
plt.title('Posterior Distributions')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
diff_samples = bayes_results['samples_b'] - bayes_results['samples_a']
plt.hist(diff_samples, bins=50, alpha=0.7, edgecolor='black')
plt.axvline(0, color='r', linestyle='--', label='No difference')
plt.xlabel('Difference (Treatment - Control)')
plt.ylabel('Frequency')
plt.title('Posterior Distribution of Difference')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 3. Sequential Testing

**Sequential Probability Ratio Test (SPRT)**:
```python
import numpy as np

def sequential_test(conversions_a, total_a, conversions_b, total_b, alpha=0.05, beta=0.20):
    """
    Perform sequential testing to enable early stopping

    Args:
        conversions_a, total_a: Control group cumulative data
        conversions_b, total_b: Treatment group cumulative data
        alpha: Type I error rate
        beta: Type II error rate (1 - power)

    Returns:
        Decision: 'continue', 'stop_b_wins', or 'stop_no_difference'
    """
    # Log likelihood ratio
    p_a = conversions_a / total_a if total_a > 0 else 0
    p_b = conversions_b / total_b if total_b > 0 else 0

    # Thresholds
    threshold_upper = np.log((1 - beta) / alpha)
    threshold_lower = np.log(beta / (1 - alpha))

    # Simple likelihood ratio (simplified version)
    if p_b > p_a and total_a > 100 and total_b > 100:
        # Calculate log likelihood ratio (simplified)
        llr = (
            conversions_b * np.log(p_b / p_a) +
            (total_b - conversions_b) * np.log((1 - p_b) / (1 - p_a))
        )

        if llr > threshold_upper:
            return 'stop_b_wins'
        elif llr < threshold_lower:
            return 'stop_no_difference'

    return 'continue'
```

## Advanced Topics

### Multi-Variate Testing (MVT)

```python
def multivariate_test_analysis(variants_data):
    """
    Analyze multi-variate test with multiple variants

    Args:
        variants_data: List of dicts with keys 'name', 'conversions', 'total'

    Returns:
        Results comparing all variants to control
    """
    from scipy.stats import chi2_contingency

    # Prepare contingency table
    conversions = [v['conversions'] for v in variants_data]
    non_conversions = [v['total'] - v['conversions'] for v in variants_data]

    contingency_table = np.array([conversions, non_conversions])

    # Chi-square test
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    # Pairwise comparisons with control
    control = variants_data[0]
    comparisons = []

    for variant in variants_data[1:]:
        result = two_proportion_ztest(
            control['conversions'], control['total'],
            variant['conversions'], variant['total']
        )
        result['variant_name'] = variant['name']
        comparisons.append(result)

    # Bonferroni correction for multiple comparisons
    corrected_alpha = 0.05 / len(comparisons)

    return {
        'overall_p_value': p_value,
        'overall_significant': p_value < 0.05,
        'comparisons': comparisons,
        'corrected_alpha': corrected_alpha
    }
```

### Sample Ratio Mismatch (SRM) Detection

```sql
-- Check for Sample Ratio Mismatch
WITH variant_counts AS (
  SELECT
    variant,
    COUNT(DISTINCT user_id) as actual_users
  FROM ab_test_events
  WHERE test_name = 'cta_button_test'
    AND event_type = 'exposure'
  GROUP BY 1
),
expected_split AS (
  SELECT 0.5 as expected_ratio  -- 50/50 split expected
)
SELECT
  variant,
  actual_users,
  SUM(actual_users) OVER () as total_users,
  actual_users * 1.0 / SUM(actual_users) OVER () as actual_ratio,
  es.expected_ratio,
  ABS(actual_users * 1.0 / SUM(actual_users) OVER () - es.expected_ratio) as ratio_difference
FROM variant_counts
CROSS JOIN expected_split es;
```

```python
from scipy.stats import chisquare

def check_sample_ratio_mismatch(observed_counts, expected_ratios):
    """
    Check for sample ratio mismatch using chi-square test

    Args:
        observed_counts: List of actual user counts per variant
        expected_ratios: List of expected proportions per variant

    Returns:
        Dictionary with SRM check results
    """
    total = sum(observed_counts)
    expected_counts = [ratio * total for ratio in expected_ratios]

    chi2_stat, p_value = chisquare(observed_counts, expected_counts)

    return {
        'observed': observed_counts,
        'expected': expected_counts,
        'chi2_statistic': chi2_stat,
        'p_value': p_value,
        'srm_detected': p_value < 0.01  # Use strict threshold
    }
```

## Common Pitfalls

### 1. Peeking Problem

**Don't repeatedly check results**: Increases false positive rate.

**Solution**: Pre-specify sample size or use sequential testing.

### 2. Simpson's Paradox

Segment-level patterns may reverse at aggregate level.

```sql
-- Check for Simpson's Paradox
SELECT
  variant,
  segment,
  SUM(conversions) / SUM(users) as conversion_rate
FROM (
  SELECT
    variant,
    CASE
      WHEN user_type = 'new' THEN 'New Users'
      ELSE 'Returning Users'
    END as segment,
    COUNT(DISTINCT user_id) as users,
    COUNT(DISTINCT CASE WHEN converted THEN user_id END) as conversions
  FROM ab_test_results
  GROUP BY 1, 2
) segments
GROUP BY 1, 2
ORDER BY 2, 1;
```

### 3. Novelty Effects

**Problem**: Users may respond differently to changes initially.

**Solution**: Run test for at least 1-2 full business cycles (usually 2 weeks minimum).

## Best Practices Checklist

- [ ] Define clear hypothesis and success metrics
- [ ] Calculate required sample size before starting
- [ ] Implement proper randomization
- [ ] Run test for at least 1 full business cycle
- [ ] Check for sample ratio mismatch
- [ ] Validate data quality regularly
- [ ] Consider both statistical and practical significance
- [ ] Analyze segments (device, new vs returning, etc.)
- [ ] Document test setup and results
- [ ] Have rollback plan ready

## Decision Framework

```python
def make_test_decision(results, min_sample_size, business_threshold=0.02):
    """
    Structured decision framework for A/B test results

    Args:
        results: Dictionary from two_proportion_ztest
        min_sample_size: Minimum required sample size
        business_threshold: Minimum practical improvement needed (e.g., 2%)

    Returns:
        Decision and reasoning
    """
    decision = {
        'action': None,
        'reasoning': []
    }

    # Check sample size
    if results.get('total_users', 0) < min_sample_size:
        decision['action'] = 'CONTINUE'
        decision['reasoning'].append('Sample size not yet reached')
        return decision

    # Check statistical significance
    if not results['significant']:
        decision['action'] = 'NO_WINNER'
        decision['reasoning'].append('No statistically significant difference')
        return decision

    # Check practical significance
    if abs(results['relative_improvement']) < business_threshold:
        decision['action'] = 'NO_WINNER'
        decision['reasoning'].append(f'Improvement below business threshold ({business_threshold:.0%})')
        return decision

    # Winner found
    if results['relative_improvement'] > 0:
        decision['action'] = 'TREATMENT_WINS'
        decision['reasoning'].append(
            f"Treatment shows {results['relative_improvement']:.1%} improvement "
            f"(p={results['p_value']:.4f})"
        )
    else:
        decision['action'] = 'CONTROL_WINS'
        decision['reasoning'].append(
            f"Control performs better by {abs(results['relative_improvement']):.1%}"
        )

    return decision
```

## Reporting Template

```markdown
# A/B Test Results: [Test Name]

## Test Overview
- **Hypothesis**: [Your hypothesis]
- **Primary Metric**: [e.g., Conversion Rate]
- **Test Period**: [Start Date] to [End Date]
- **Sample Size**: [Total users tested]

## Results

### Summary
| Variant | Users | Conversions | Rate | Rel. Improvement |
|---------|-------|-------------|------|------------------|
| Control | 10,000 | 450 | 4.50% | - |
| Treatment | 10,000 | 520 | 5.20% | +15.6% |

### Statistical Significance
- **P-value**: 0.0023
- **Confidence Level**: 99.77%
- **95% Confidence Interval**: [+0.2%, +1.2%]

### Decision
**Winner**: Treatment variant
- Statistically significant (p < 0.01)
- Practically significant (>10% improvement)
- Recommend full rollout

### Secondary Metrics
- Engagement: No significant change
- Revenue per user: +12% (p=0.04)
- Page load time: No degradation

### Segments
- Mobile: +18% improvement
- Desktop: +12% improvement
- New users: +20% improvement
- Returning: +10% improvement

## Next Steps
1. Roll out treatment to 100% of users
2. Monitor for 2 weeks
3. Plan follow-up iteration
```
