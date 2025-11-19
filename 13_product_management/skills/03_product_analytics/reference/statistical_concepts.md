# Statistical Concepts for A/B Testing

Essential statistical knowledge for running valid experiments and interpreting results correctly.

## Foundational Concepts

### Hypothesis and P-Value

**Null Hypothesis (H0)**
- Assumption that there is no difference between control and variant
- What you're trying to disprove with your experiment
- Example: "Variant button color has no effect on click-through rate"

**Alternative Hypothesis (H1)**
- What you expect to be true
- If null hypothesis is disproven, alternative is supported
- Example: "Variant button color increases click-through rate"

**P-Value**
- Probability that observed result occurred by chance if null hypothesis is true
- NOT "probability that hypothesis is true"
- Lower = stronger evidence against null hypothesis
- Standard threshold: p < 0.05 (5% chance of false positive)
- In practice: use 0.05 for 95% confidence level

**Significance Level (α)**
- The probability threshold you set in advance
- Common choices: 0.05 (95%), 0.01 (99%)
- Higher confidence = need larger sample size
- 95% (p < 0.05) is standard for most product decisions

### Statistical Power and Sample Size

**Power (1 - β)**
- Ability to detect a real effect when one exists
- Probability of correctly rejecting false null hypothesis
- Standard: 80% power (β = 0.20)
- Higher power = larger sample size needed
- Inverse relationship: higher confidence or smaller expected effect = larger sample

**Type I Error (False Positive)**
- Rejecting null hypothesis when it's actually true
- Seeing effect that doesn't exist
- Controlled by significance level (α)
- If α = 0.05, false positive rate is 5%

**Type II Error (False Negative)**
- Failing to reject null hypothesis when it's false
- Missing a real effect
- Controlled by power (1 - β)
- If power = 80%, false negative rate is 20%

**Minimum Detectable Effect (MDE)**
- Smallest difference you want to reliably detect
- Defines practical significance
- Larger MDE = smaller sample size needed
- Smaller MDE = larger sample size needed
- Example: "We care about 5% improvement in conversion rate"

### Sample Size Calculation

**Key Inputs:**
1. Baseline conversion rate
2. Minimum detectable effect (% improvement)
3. Significance level (typically 0.05)
4. Power (typically 0.80)
5. Whether test is one-tailed or two-tailed (almost always two-tailed)

**Formula (Two-Proportion Z-Test):**
```
n = 2 * ((Z_α/2 + Z_β) / (2p - 1))² / (p * (1-p))

Where:
- p = baseline conversion rate
- Z_α/2 = critical value for significance level (1.96 for 95%)
- Z_β = critical value for power (0.84 for 80% power)
```

**Practical Examples:**

| Baseline Rate | MDE | Sample per Arm | Total Needed | Duration (1k/day) |
|---------------|-----|---|---|---|
| 5% | 10% | 5,247 | 10,494 | 10-11 days |
| 5% | 20% | 1,311 | 2,622 | 3 days |
| 10% | 10% | 6,888 | 13,776 | 14 days |
| 10% | 20% | 1,722 | 3,444 | 3-4 days |
| 50% | 5% | 31,936 | 63,872 | 64 days |
| 50% | 10% | 7,984 | 15,968 | 16 days |

**Key Insights:**
- Harder to detect small improvements on already-high baselines
- Easier to detect improvements on low baselines
- Very small MDEs require huge sample sizes
- Typical SaaS test: 1-4 weeks duration

### Confidence Intervals

**Definition**
- Range of values where true effect likely lies
- 95% confidence interval: if test repeated 100 times, true value in range 95 times
- NOT "95% probability true value in range" (Bayesian, not frequentist)

**Interpretation**
- Narrower interval = more precision
- Wider interval = less precise estimate
- Large sample size = narrower interval
- Small sample size = wider interval

**Example:**
- Control CTR: 5.0%
- Variant CTR: 5.5%
- 95% CI: [4.8%, 6.2%]
- Interpretation: We're 95% confident the true variant effect is between 4.8% and 6.2%
- If interval crosses zero or includes null, not statistically significant

## A/B Testing Calculations

### Conversion Rate Comparison

**Standard Error:**
```
SE = √(p₀(1-p₀)/n₀ + p₁(1-p₁)/n₁)

Where:
- p₀ = control conversion rate
- p₁ = variant conversion rate
- n₀ = control sample size
- n₁ = variant sample size
```

**Test Statistic (Z-score):**
```
Z = (p₁ - p₀) / SE
```

**P-value:**
- For two-tailed test: p = 2 * (1 - Φ(|Z|))
- Where Φ = standard normal cumulative distribution
- Compare to significance level (α = 0.05)

**Confidence Interval:**
```
CI = (p₁ - p₀) ± Z_α/2 * SE
```

### Revenue-Based Metrics

**Testing Average Order Value (AOV)**
- Use t-test instead of z-test
- Account for variance in values
- More conservative (requires larger sample)
- Example: Testing different pricing strategy

**Testing Revenue Per User (RPU)**
- Similar to AOV but across all users
- Many users with $0 (didn't purchase)
- May have skewed distribution with outliers
- Consider log transformation for analysis

**Important:** Revenue tests require 2-4x sample size of conversion tests

### Relative Lift vs. Absolute Difference

**Relative Lift:**
- (Variant - Control) / Control * 100%
- What marketers care about ("20% improvement")
- Example: 5% → 6% = 20% relative lift

**Absolute Difference:**
- Variant - Control
- What impact assessment needs
- Example: 5% → 6% = 1 percentage point lift
- More important for unit economics

**Be Clear About Which You're Using:**
- "20% lift" (relative) sounds better than "1 percentage point" (absolute)
- But both describe the same effect
- Always report both for clarity

### Multiple Comparisons Problem

**The Issue:**
- Testing multiple variants against control increases false positive rate
- With 3 variants and α = 0.05, actual false positive rate ≈ 14% (not 5%)
- The more tests, the higher chance of seeing "significant" random differences

**Bonferroni Correction:**
- Divide significance threshold by number of comparisons
- Testing 3 variants: Use α = 0.05 / 3 = 0.0167 instead of 0.05
- Conservative but safe approach
- Reduces power but eliminates false positive inflation

**Sequential Testing (Peek Correction):**
- If you peek at results before experiment ends, p-values are invalid
- Each peek increases false positive rate
- Proper approach: Pre-register stopping rule and stick to it
- Don't stop early even if results look good

## Common A/B Testing Mistakes

### 1. Peeking at Results

**The Problem:**
- Looking at results before achieving statistical significance
- Each peek inflates false positive rate
- Temptation to stop early if winning

**The Math:**
- One peek: ~10% false positive rate (not 5%)
- Multiple peeks: Even higher
- Invalidates p-value calculations

**The Solution:**
- Decide sample size in advance
- Set calendar stop date
- Don't look until power is reached
- Use sequential testing if you want to peek responsibly

### 2. Running Test Too Short

**The Problem:**
- Day-of-week effects (Monday ≠ Friday)
- Weekly patterns in user behavior
- Seasonal effects
- Test appears significant but won't replicate

**Duration Rules:**
- Minimum: 1 full week (7 days) to capture day-of-week
- Better: 2 weeks (14 days) to capture full week pattern
- Mobile apps: Sometimes need 4 weeks for monthly pattern
- Holiday periods: Longer tests needed

### 3. Segmentation and Slicing

**The Problem:**
- Splitting data into subgroups looks for effects
- With 20 subgroups and 5% significance, expect 1 false positive
- "Segment hunting" finds random differences

**The Rule:**
- Decide segments in advance
- Limit to 3-5 key segments
- Document pre-registered primary and secondary
- Multiple segment analysis = need correction
- Replicate in new test before acting on segment finding

### 4. Ignoring Practical Significance

**The Problem:**
- Statistically significant ≠ practically significant
- Large sample size makes small effects significant
- Example: 0.1% improvement that costs $50k to implement

**Consider:**
- Effect size relative to baseline
- Implementation cost and effort
- Customer impact
- Sustainability over time

**When in doubt:**
- Ask: "Would we make different decision if p=0.03 vs p=0.06?"
- If no, it's not practically significant
- Statistical significance is necessary but not sufficient

### 5. Wrong Sample Size Calculation

**Common Errors:**
- Using wrong baseline rate
- Confusing sample size with power
- Not accounting for users who don't see variant
- Assuming you'll reach 50/50 split (often wrong)
- Not including design effect for clustered users

**Get Right:**
- Use actual baseline from past data
- Account for traffic distribution
- Ask: "How many users see variant vs control?"
- Consider user behavior clusters (workplace users cluster together)

### 6. Ignoring Interaction Effects

**The Problem:**
- Feature might work differently for different segments
- Treatment effect varies by user type
- Change good for new users, bad for power users

**How to Check:**
- Segment analysis (but pre-registered)
- User stratification in analysis
- Domain expertise reasoning

**When Significant:**
- May need segment-specific rollout
- Or different implementation per segment
- Or accept trade-off

## Bayesian Approaches

**When to Use Bayesian Methods:**
- Small sample sizes (easier interpretation)
- Looking for "probability true effect is positive" (natural Bayesian question)
- Combining with prior knowledge
- Sequential testing with valid peeking

**Advantages:**
- More intuitive interpretation (% confidence effect is real)
- Can use prior knowledge
- Natural sequential testing
- Smaller samples sometimes needed

**Disadvantages:**
- More complex to calculate
- Prior choice can be subjective
- Less standardized in industry

## Practical Decision Rules

**For Primary Metric:**
- Achieve statistical significance (p < 0.05)
- Run minimum planned duration (usually 2 weeks)
- Effect passes common sense test
- No critical guardrail metrics harmed

**Red Flags:**
- Opposite effect in different segments
- Declining effectiveness over time
- Negative impact on guardrail metrics
- Practical significance too small
- Inconsistent with prior knowledge

**When to Extend Test:**
- Approaching significance but not quite there
- Large confidence interval still includes zero
- Need more data for segment analysis
- Test duration too short

**When to Stop Early:**
- Critical bug in variant (customer safety)
- Variant clearly worse than control (decision-driven by guardrails)
- Achieving enormous positive effect (rare)
- Even then: only if pre-registered stopping rule

## Tools and Calculators

**Sample Size Calculators:**
- VWO Sample Size Calculator
- Amplitude Experiment Sample Size Calculator
- Optimizely Statistics Calculator
- Online power calculators (search "sample size calculator")

**A/B Test Validators:**
- AB Tasty
- Statsig (great for statistical literacy)
- Optimizely
- Custom Python script with scipy.stats

**Python Analysis Code:**
```python
from scipy import stats
import numpy as np

# Two-proportion z-test
control_converts = 500
control_n = 10000
variant_converts = 550
variant_n = 10000

p1 = control_converts / control_n
p2 = variant_converts / variant_n

# Pooled proportion
p_pool = (control_converts + variant_converts) / (control_n + variant_n)

# Standard error
se = np.sqrt(p_pool * (1 - p_pool) * (1/control_n + 1/variant_n))

# Z-score and p-value
z_score = (p2 - p1) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

# Confidence interval
ci_lower = (p2 - p1) - 1.96 * se
ci_upper = (p2 - p1) + 1.96 * se

print(f"Relative Lift: {((p2 - p1) / p1 * 100):.2f}%")
print(f"P-value: {p_value:.4f}")
print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"Statistically Significant: {p_value < 0.05}")
```

## Executive Summary for Non-Statistical Stakeholders

**Simple Explanation of A/B Testing:**
1. We run two versions (control and variant) simultaneously
2. We measure if variant performs meaningfully better
3. "Meaningful" means both:
   - Likely to happen again (statistical significance)
   - Big enough to justify the effort (practical significance)
4. We wait for enough data (typically 2 weeks) before deciding
5. If both conditions met, we fully launch variant

**What Significant Means:**
- "If we ran this test 100 times with no real difference, we'd expect to see this result only 5 times by random chance"
- NOT "We're 95% sure the variant is better"
- NOT "There's a 95% chance this will work with users"

**What Confidence Interval Means:**
- "We're 95% confident the true effect is in this range"
- Wider range = less precise estimate
- Should get narrower as test runs longer

**When to Trust Results:**
- ✓ Ran for full 2+ weeks
- ✓ Achieved statistical significance
- ✓ Effect is practically meaningful
- ✗ If any guardrail metrics hurt
- ✗ If result contradicts prior tests
