# A/B Testing Guide: Run Rigorous Experiments and Drive Evidence-Based Decisions

Complete guide to designing, running, and analyzing A/B tests that generate statistically valid and actionable insights.

## A/B Testing Fundamentals

### What is A/B Testing?

An A/B test (randomized controlled experiment) compares two versions (control and variant) to measure which performs better on a specific metric.

**Key Components:**
- Control (A): Current version (baseline)
- Variant (B): Proposed change
- Random assignment: Users randomly assigned to one version
- Metric: Quantifiable outcome we're measuring
- Duration: Fixed time period

**Why It Matters:**
- Establishes causation (not just correlation)
- Removes bias from decision-making
- Scales learnings across user base
- Prevents expensive mistakes
- Builds data culture

### Random Assignment is Critical

**Why Randomization?**
- Makes control and variant groups statistically equivalent before treatment
- Ensures any difference is due to the change, not user differences
- Allows for valid statistical inference

**Bad Assignment Strategies:**
❌ New users see variant, old users see control (different audiences)
❌ Users self-select (motivated users vs. others)
❌ Geographic split (different markets)
❌ Assigned by cohort date (temporal confounding)

**Good Assignment Strategies:**
✓ Random user_id hash modulo 2
✓ Random assignment at session level
✓ Random assignment at account level (for B2B)
✓ Stratified random sampling by segment

## Pre-Launch Planning

### Phase 1: Hypothesis Development

**Great Hypothesis Includes:**
1. What we're changing and why
2. Expected user behavior change
3. Expected direction of impact
4. Reasonable estimate of effect size
5. Mechanism of how change drives impact

**Example Hypothesis:**
```
GOOD:
"Reducing the number of required fields in sign-up from 5 to 3 will
increase sign-up conversion rate by 15-20% because users often abandon
complex forms. We'll measure by comparing overall sign-up completion rate."

BAD:
"The sign-up flow is probably not good, let's try a shorter form
and see if it helps."
```

**Hypothesis Sources:**
- User research and interviews
- Competitor analysis
- Industry best practices
- Past A/B test learnings
- Product team intuition (but validate with research first)
- Behavioral data showing friction points

### Phase 2: Metric Selection

**Choose Metrics Before Running Test**

**Primary Metric:**
- Directly measures success of hypothesis
- Should be moveable by change
- Must not be a vanity metric
- Example: Sign-up completion rate

**Secondary Metrics:**
- Related outcomes we care about
- Example: Email verification rate, Day 7 retention
- Help understand if improvement is real or local optimization

**Guardrail Metrics:**
- Critical business metrics we must not harm
- Example: Revenue, customer satisfaction, DAU
- If guardrails worsen, declare test failure
- Prevents optimizing for wrong metric

**Bad Metric Choices:**
- Page load time (not user-facing outcome)
- Clicks on variant (people might click more but not convert)
- Bounce rate (too noisy, influenced by outside factors)
- Vanity metrics (signups without quality)

### Phase 3: Sample Size and Duration Calculation

**Inputs You Need:**
1. **Baseline conversion rate** - Historical data
2. **Minimum detectable effect (MDE)** - Smallest improvement you care about
3. **Significance level** - Usually 95% (α = 0.05)
4. **Power** - Usually 80% (β = 0.20)
5. **Variant exposure rate** - % of users in variant group

**Sample Size Formula:**
```
For 95% confidence and 80% power (most common):

n = 2 * ((1.96 + 0.84) / MDE/Baseline)² * Baseline*(1-Baseline)

Example:
Baseline: 5% conversion
MDE: 10% improvement (to 5.5%)
n = 2 * ((2.8) / (0.5/5))² * 0.05*0.95
n ≈ 5,247 per variant = 10,494 total
```

**Duration Calculation:**
```
Required traffic per variant = Sample size
Daily variant exposure = Daily users * % in variant
Duration = Sample size / Daily variant exposure

Example:
Sample needed: 5,247 per variant
Daily traffic: 1,000 users/day
Variant exposure: 50% (500/day)
Duration = 5,247 / 500 = ~10.5 days
```

**Typical Test Durations:**
- Small experiments (high baseline rate): 3-5 days
- Medium experiments (medium baseline): 1-2 weeks
- Large experiments (low baseline rate or small MDE): 2-4 weeks
- Mobile apps: Often 2-4 weeks due to weekly patterns

### Phase 4: Pre-Registration

**Document Before Launching:**
- [ ] Primary success metric and threshold
- [ ] Secondary metrics to monitor
- [ ] Guardrail metrics that must not drop
- [ ] Minimum sample size per variant
- [ ] Expected duration
- [ ] What counts as test success
- [ ] Who has decision authority
- [ ] Go/no-go criteria

**Example Pre-Registration:**
```
Test: Simplified Sign-Up Form
Hypothesis: Removing phone number field increases completion

Primary: Sign-up completion rate
  Target: ≥ 15% relative improvement
  Baseline: 5%
  Success: ≥ 5.75%

Secondary:
  - Email verification rate
  - Day 1 retention
  - Day 7 retention

Guardrails:
  - Revenue per new user (must not decline)
  - Customer satisfaction (NPS must not decline)

Sample Size: 5,247 per arm
Duration: ~10-11 days (assuming 500/day per variant)

Success Criteria:
  ✓ Primary metric achieves statistical significance
  ✓ Effect size aligns with hypothesis (15-20%)
  ✓ Secondary metrics don't show concerning changes
  ✓ Guardrails remain healthy
```

## Running the Test

### Launch Checklist

- [ ] Code reviewed and approved
- [ ] Variant tested in staging environment
- [ ] Events tracking correctly (firing, properties, no PII)
- [ ] Random assignment working (validate distribution)
- [ ] Both control and variant are clearly identifiable
- [ ] Team notified of test launch
- [ ] Alerts set up for data anomalies
- [ ] Dashboards ready to monitor test
- [ ] Metrics pre-calculated for baseline
- [ ] No concurrent tests affecting same users (unless testing for interaction)

### Monitoring During Test

**Daily Checks:**
1. ✓ Traffic is flowing as expected
2. ✓ Both variants receiving equal traffic
3. ✓ No unexpected technical errors
4. ✓ Event tracking is working
5. ✓ Primary metric moving as expected

**Red Flags:**
- ❌ Users heavily skewed to one variant (randomization broken?)
- ❌ Event volume drops significantly (tracking issue?)
- ❌ Variant has much higher error rate (bug?)
- ❌ Guardrail metric dropping rapidly (stop test)
- ❌ Opposite effect from hypothesis (stop test)

**Avoid:**
- 🚫 Don't look at p-values until test is fully mature
- 🚫 Don't stop early if looking positive
- 🚫 Don't adjust metrics mid-test
- 🚫 Don't increase sample size mid-test based on results
- 🚫 Don't run multiple concurrent tests on same users

### Minimum Test Duration Rules

**ALWAYS run minimum of 1 week**
- Captures day-of-week variation (Monday ≠ Friday)
- Users have different patterns by day

**BETTER: 2 weeks**
- Captures full week patterns
- New users who signup early have more time to convert
- More mature test statistics

**SOMETIMES NEED 4 weeks**
- Monthly-cadence products (SaaS annual billing)
- Mobile apps with weekly usage patterns
- Holiday/seasonal effects

**Exception: Stop Early If**
- Critical bug discovered in variant
- Guardrail metrics plummet (revenue, safety, compliance)
- Even then: only if pre-registered stopping rule

## Analysis and Interpretation

### Phase 1: Validity Check

**Does the test data look valid?**

```
Control Group:
- Sample size: 5,247 users
- Completions: 262 (5.0%)
- Time range: Full 2 weeks, uniform distribution

Variant Group:
- Sample size: 5,251 users
- Completions: 290 (5.5%)
- Time range: Full 2 weeks, uniform distribution

Checks:
✓ Sample sizes roughly equal
✓ Both have sufficient sample size
✓ Completion rates make sense
✓ No suspicious outliers
```

### Phase 2: Statistical Analysis

**Calculate Standard Error:**
```
SE = √(p₀(1-p₀)/n₀ + p₁(1-p₁)/n₁)
SE = √(0.05*0.95/5247 + 0.055*0.945/5251)
SE = √(0.0000907 + 0.0000978)
SE = √(0.0001885) = 0.01373
```

**Calculate Z-Score:**
```
Z = (p₁ - p₀) / SE
Z = (0.055 - 0.05) / 0.01373
Z = 0.005 / 0.01373
Z = 0.364
```

**Calculate P-Value:**
```
For two-tailed test: p = 2 * P(Z > 0.364)
p = 2 * 0.358
p = 0.716 (NOT statistically significant)
```

**Confidence Interval:**
```
CI = (p₁ - p₀) ± 1.96*SE
CI = 0.005 ± 1.96*0.01373
CI = 0.005 ± 0.0269
CI = [-2.19%, 7.19%]

Interpretation: We're 95% confident the true effect is between -2.19% and 7.19%
Since this interval includes zero, not statistically significant.
```

### Phase 3: Interpret Results

**Example 1: Statistically Significant Positive Result**
```
Result:
- Control: 5.0% completion
- Variant: 5.75% completion
- Relative Lift: 15%
- P-value: 0.032 (significant at 95%)
- 95% CI: [0.3%, 1.2%]

Decision: LAUNCH
Reason: Achieved statistical significance AND practical significance.
Effect size aligns with hypothesis. No guardrail concerns.

Launch Plan:
- Implement variant for 100% of users
- Monitor for 1 week post-launch to confirm
- Document learnings and move to next test
```

**Example 2: Statistically Significant Negative Result**
```
Result:
- Control: 5.0% completion
- Variant: 4.2% completion
- Relative Lift: -16%
- P-value: 0.021 (significant)
- 95% CI: [-1.8%, -0.2%]

Decision: REVERT
Reason: Variant is significantly worse than control.

Learning: Our hypothesis was wrong. Why?
- Maybe phone number helps with trust/payment compliance
- Maybe form length wasn't the friction point
- Follow-up: User research to understand real blocker

Action: Return to drawing board with new hypothesis
```

**Example 3: Not Statistically Significant**
```
Result:
- Control: 5.0% completion
- Variant: 5.2% completion
- Relative Lift: 4%
- P-value: 0.428 (NOT significant)
- 95% CI: [-1.0%, 1.4%]

Decision: REVERT (or run longer test if...)
Reason: Can't differentiate this result from random chance.

Options:
1. Accept that change doesn't matter, move to next hypothesis
2. Run longer test if hypothesis still viable (need 10x more users)
3. Try different implementation of same idea

Likely action: Accept and move on. Small 4% improvement unlikely worth effort.
```

**Example 4: Large Confidence Interval (Low Confidence)**
```
Result:
- Control: 5.0% completion
- Variant: 5.5% completion
- Relative Lift: 10%
- P-value: 0.058 (borderline)
- 95% CI: [-0.2%, 2.2%]

Decision: INCONCLUSIVE - Run longer
Reason: P-value just barely misses significance (0.058 vs 0.05)
And confidence interval is wide - could be 0% to 2.2% effect.

Action:
- Run additional 1-2 weeks
- Need more users per variant
- CI will narrow as sample size increases
- Better to be sure than to make wrong decision
```

### Segment Analysis (Secondary)

**Important: Only pre-registered segments matter**

```
Overall Result: +1.5% (significant, p=0.042)

By Device:
- Desktop: +2.1% (significant, p=0.028) ✓
- Mobile: +0.3% (not significant, p=0.52) ⚠️

By User Type:
- New users: +2.5% (significant, p=0.018) ✓
- Returning users: +0.8% (not significant, p=0.41) ⚠️

Interpretation:
- Overall positive effect is robust
- Effect is stronger for mobile and new users
- Consider: Mobile design issue? Or new users more sensitive to form friction?
- Replicable in future test? Don't over-optimize to this finding.

Action: Launch to all, but note segment differences for future work.
```

## Common Analysis Mistakes

### ❌ Mistake 1: Stopping Early Because Results Look Good

**The Problem:**
- You peek at day 5 and see p=0.08 (not quite significant)
- Day 7: p=0.04 (significant!)
- You declare victory and stop

**Why It's Wrong:**
- Each peek inflates false positive rate
- Actual false positive rate might be 10%+ not 5%
- You can't just look when results look good

**Solution:**
- Pre-commit to duration
- Set calendar stop date
- If tempted to peek, use proper sequential testing rules

### ❌ Mistake 2: p-hacking (Choosing Metrics Post-Hoc)

**The Problem:**
- You ran 5 different tests
- 1 shows statistical significance
- You declare the 1 success and ignore the others

**Why It's Wrong:**
- With 5 tests at 95% confidence, expect ~1 false positive
- You're reporting only the false positive

**Solution:**
- Pre-register primary metric
- Correct for multiple comparisons if testing multiple metrics
- Report all tests, not just wins

### ❌ Mistake 3: Ignoring Practical Significance

**The Problem:**
- Test with 100,000 users
- Find 0.1% improvement
- It's statistically significant (huge sample)
- But costs $50k to implement

**Why It's Wrong:**
- Statistical significance ≠ practical significance
- Small effects might not be worth effort

**Solution:**
- Ask: "Is the effect size meaningful?"
- Consider: Implementation cost, opportunity cost, complexity
- Rule of thumb: Effect should be 5%+ for most decisions

### ❌ Mistake 4: Confounding Variables

**The Problem:**
- You test new button color during holiday season
- Sales go up 25%
- You attribute to button color

**Why It's Wrong:**
- Seasonal effect much bigger than button color
- Can't isolate cause

**Solution:**
- Run tests when business is stable
- If can't avoid, compare to control baseline for same period
- Holiday tests need longer duration or analysis correction

### ❌ Mistake 5: Changing Test Definition Mid-Flight

**The Problem:**
- You start measuring conversion rate
- On day 10, you decide to measure click-through instead
- Now you have 10 days of one metric, 4 days of another

**Why It's Wrong:**
- Invalid comparison
- Looks like p-hacking

**Solution:**
- Pre-register metrics
- Stick with plan
- If need to change, document clearly and note impact

## Dos and Don'ts Summary

### ✓ DO:
- ✓ Pre-register hypothesis and metrics
- ✓ Calculate sample size before launching
- ✓ Run full planned duration
- ✓ Compare primary metric only
- ✓ Report confidence interval along with p-value
- ✓ Report relative and absolute lift
- ✓ Consider practical significance
- ✓ Document all tests and results
- ✓ Segment only pre-registered segments
- ✓ Be honest about null results

### ✗ DON'T:
- ✗ Peek at results before finish
- ✗ Stop early if looking positive
- ✗ Choose metrics after test runs
- ✗ Test multiple variants on same users without correction
- ✗ Run test too short (less than 7 days)
- ✗ Change test parameters mid-flight
- ✗ Ignore guardrail metrics
- ✗ Over-interpret secondary metrics
- ✗ Report only winning tests
- ✗ Assume causation from correlation data

## Decision Framework

```
Does test achieve statistical significance?
├─ YES
│  └─ Is effect practically significant? (5%+ usually)
│     ├─ YES
│     │  └─ Did we harm any guardrail metrics?
│     │     ├─ NO → LAUNCH
│     │     └─ YES → REVERT & ITERATE
│     └─ NO (effect too small)
│        └─ Cost of implementation > value of improvement?
│           ├─ YES → REVERT
│           └─ NO → Consider launching (rare)
└─ NO
   ├─ Could we run longer to achieve significance?
   │  ├─ YES (hypothesis still valid) → EXTEND TEST
   │  └─ NO (not worth effort) → REVERT & LEARN
   └─ Document null result and iterate on next hypothesis
```

## Tracking Test Results

**Create Test Registry:**
```
Date Launched: 2025-01-15
Test Name: Simplified Sign-Up Form
Status: Complete

Hypothesis:
Removing phone field will increase sign-up completion by 15-20%

Results:
- Primary: 5.0% → 5.75% (+15%, p=0.032) ✓ PASSED
- Secondary: Email verification 85% → 84% (no sig. change)
- Guardrail: Revenue/user (no significant change) ✓
- Duration: 11 days, 5,247 users per variant

Decision: LAUNCHED

Learnings:
- Phone number was friction point in sign-up
- Effect sustained in subsequent cohorts
- Mobile users especially benefited (+18% vs 12% desktop)

Follow-up: Test removing additional fields
```

## Key Takeaways

1. **Statistics isn't magic** - It's a tool to separate signal from noise
2. **Randomization is everything** - Controls for confounding variables
3. **Pre-registration prevents bias** - Document your plan before seeing results
4. **Sample size matters** - Too small = inconclusive, too large = slow
5. **Duration matters** - Minimum 1 week, ideally 2+ weeks
6. **Never stop early** - Resist temptation to declare victory early
7. **Practical > Statistical significance** - A tiny effect isn't worth pursuing
8. **Monitor guardrails** - Don't optimize one metric at cost of others
9. **Document everything** - Build playbook from test results
10. **Move fast but smart** - Run many tests, but run them right
