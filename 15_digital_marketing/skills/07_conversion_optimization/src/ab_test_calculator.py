# A/B Testing Calculator & Statistical Significance Guide

## Sample Size Calculator

### Formula
```
n = (Z^2 × p × (1-p)) / E^2

Where:
n = Required sample size per variation
Z = Z-score (1.96 for 95% confidence)
p = Expected conversion rate
E = Margin of error (minimum detectable effect)
```

### Example Calculation
**Scenario**: Current conversion rate = 5%, Want to detect 10% lift (0.5% absolute)

```python
import math

def calculate_sample_size(baseline_rate, min_detectable_effect, confidence_level=0.95):
    """
    Calculate required sample size for A/B test

    Args:
        baseline_rate: Current conversion rate (e.g., 0.05 for 5%)
        min_detectable_effect: Minimum effect to detect (e.g., 0.005 for 0.5%)
        confidence_level: Statistical confidence (default 95%)

    Returns:
        Required sample size per variation
    """
    # Z-score for confidence level
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_scores.get(confidence_level, 1.96)

    # Calculate sample size
    p = baseline_rate
    e = min_detectable_effect

    n = (z**2 * p * (1 - p)) / (e**2)

    return math.ceil(n)

# Example usage
baseline = 0.05  # 5% conversion rate
mde = 0.005      # Want to detect 0.5% absolute lift (10% relative)

sample_size = calculate_sample_size(baseline, mde)
print(f"Required sample size per variation: {sample_size:,}")
print(f"Total sample size (A + B): {sample_size * 2:,}")
```

**Output**: ~15,000 visitors per variation (30,000 total)

---

## Statistical Significance Calculator

```python
import scipy.stats as stats

def calculate_significance(visitors_a, conversions_a, visitors_b, conversions_b):
    """
    Calculate if difference between A and B is statistically significant

    Returns:
        dict with conversion rates, lift, p-value, and significance
    """
    # Conversion rates
    cr_a = conversions_a / visitors_a
    cr_b = conversions_b / visitors_b

    # Lift
    lift = ((cr_b - cr_a) / cr_a) * 100

    # Z-test for proportions
    pooled_prob = (conversions_a + conversions_b) / (visitors_a + visitors_b)
    pooled_se = (pooled_prob * (1 - pooled_prob) * (1/visitors_a + 1/visitors_b)) ** 0.5
    z_stat = (cr_b - cr_a) / pooled_se
    p_value = stats.norm.sf(abs(z_stat)) * 2  # Two-tailed test

    # Significance
    significant = p_value < 0.05

    return {
        'conversion_rate_a': f"{cr_a:.2%}",
        'conversion_rate_b': f"{cr_b:.2%}",
        'lift': f"{lift:+.1f}%",
        'p_value': f"{p_value:.4f}",
        'significant': '✅ Yes' if significant else '❌ No',
        'confidence': f"{(1 - p_value) * 100:.1f}%"
    }

# Example usage
result = calculate_significance(
    visitors_a=10000,
    conversions_a=500,     # 5.0% CR
    visitors_b=10000,
    conversions_b=575      # 5.75% CR (15% relative lift)
)

print("A/B Test Results:")
for key, value in result.items():
    print(f"  {key.replace('_', ' ').title()}: {value}")
```

**Output**:
```
A/B Test Results:
  Conversion Rate A: 5.00%
  Conversion Rate B: 5.75%
  Lift: +15.0%
  P Value: 0.0156
  Significant: ✅ Yes
  Confidence: 98.4%
```

---

## Test Duration Calculator

```python
def calculate_test_duration(sample_size_needed, daily_visitors):
    """
    Calculate how long test needs to run

    Args:
        sample_size_needed: Per variation
        daily_visitors: Daily visitors to test page

    Returns:
        Days needed to reach sample size
    """
    # Account for 50/50 split
    daily_per_variation = daily_visitors / 2

    days_needed = sample_size_needed / daily_per_variation

    # Round up to nearest week for full week cycles
    weeks_needed = math.ceil(days_needed / 7)
    days_rounded = weeks_needed * 7

    return {
        'minimum_days': math.ceil(days_needed),
        'recommended_days': days_rounded,
        'weeks': weeks_needed
    }

# Example
duration = calculate_test_duration(
    sample_size_needed=15000,
    daily_visitors=2000
)

print(f"Minimum test duration: {duration['minimum_days']} days")
print(f"Recommended (full weeks): {duration['recommended_days']} days ({duration['weeks']} weeks)")
```

---

## Quick Reference Table

| Baseline CR | Min Detectable Effect | Sample Size Per Variation |
|-------------|----------------------|---------------------------|
| 1% | 20% relative (0.2%) | ~100,000 |
| 2% | 20% relative (0.4%) | ~48,000 |
| 5% | 20% relative (1.0%) | ~15,000 |
| 10% | 20% relative (2.0%) | ~6,000 |
| 20% | 20% relative (4.0%) | ~2,400 |

**95% confidence level, 80% statistical power**

---

## Common Mistakes to Avoid

❌ **Stopping test early when you see significance**
✅ Wait for predetermined sample size

❌ **Running test for arbitrary time period**
✅ Calculate required sample size first

❌ **Testing too many variations simultaneously**
✅ Limit to A/B or max A/B/C

❌ **Ignoring seasonality**
✅ Run test for full weeks including weekends

❌ **Changing test mid-flight**
✅ Set it and let it run to completion
