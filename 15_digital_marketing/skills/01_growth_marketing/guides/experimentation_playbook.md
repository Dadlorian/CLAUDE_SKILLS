# Growth Experimentation Playbook

A comprehensive guide to building a systematic testing culture for sustainable growth through data-driven experimentation.

## Table of Contents
1. [Experimentation Fundamentals](#fundamentals)
2. [Building an Experimentation Culture](#culture)
3. [Prioritization Frameworks](#prioritization)
4. [Experiment Design](#design)
5. [Statistical Rigor](#statistics)
6. [Execution & Analysis](#execution)
7. [Scaling Winners](#scaling)
8. [Common Pitfalls](#pitfalls)

---

## Experimentation Fundamentals {#fundamentals}

### Why Experimentation Matters

**Traditional approach problems:**
- HiPPO (Highest Paid Person's Opinion) driven decisions
- Confirmation bias in data interpretation
- No systematic learning from failures
- Slow iteration cycles
- Unclear ROI on initiatives

**Experimentation approach benefits:**
- Data-driven decision making
- Objective measurement of impact
- Compound learning over time
- Rapid iteration velocity
- Clear attribution of results

### The Experimentation Mindset

**Core Principles:**
1. **Everything is a hypothesis** - No assumptions, only testable beliefs
2. **Failures are learning** - Negative results teach as much as wins
3. **Start small, scale fast** - MVT (Minimum Viable Test) first
4. **Velocity over perfection** - Run more tests, learn faster
5. **Document everything** - Build institutional knowledge

---

## Building an Experimentation Culture {#culture}

### Organizational Requirements

**Leadership Buy-In:**
- Executive sponsorship for experimentation program
- Budget allocation for testing infrastructure
- Protection of test velocity over short-term metrics
- Celebration of both wins and learning failures

**Cross-Functional Alignment:**
- Product, Engineering, Marketing, Data Science collaboration
- Shared OKRs around learning velocity
- Regular experiment review sessions
- Transparent results sharing

**Infrastructure Needs:**
- A/B testing platform (Optimizely, VWO, GrowthBook, etc.)
- Analytics instrumentation (Mixpanel, Amplitude, Segment)
- Data warehouse for deep analysis
- Experiment tracking system
- Statistical significance calculators

### Team Structure

**Roles in Growth Experimentation:**

1. **Growth Product Manager**
   - Define experiment roadmap
   - Prioritize test queue
   - Own success metrics
   - Coordinate cross-functional teams

2. **Growth Engineer**
   - Implement test variations
   - Build experimentation infrastructure
   - Ensure tracking accuracy
   - Optimize test velocity

3. **Data Analyst/Scientist**
   - Design statistical methodology
   - Calculate sample sizes
   - Analyze results
   - Generate insights

4. **Growth Designer**
   - Design test variations
   - Create prototypes rapidly
   - Balance brand consistency with test velocity

---

## Prioritization Frameworks {#prioritization}

### ICE Scoring Framework

**Formula:** ICE Score = (Impact + Confidence + Ease) / 3

**Impact (1-10):** How much will this move the North Star Metric?
- 10: Transformational (>50% improvement)
- 7-9: Major impact (20-50% improvement)
- 4-6: Moderate impact (5-20% improvement)
- 1-3: Marginal impact (<5% improvement)

**Confidence (1-10):** How sure are we this will work?
- 10: We have strong data/precedent
- 7-9: Good reasoning, some evidence
- 4-6: Hypothesis based on partial data
- 1-3: Total guess, needs validation

**Ease (1-10):** How simple is implementation?
- 10: Can be done in hours
- 7-9: Can be done in days
- 4-6: Takes 1-2 weeks
- 1-3: Multiple weeks or dependencies

**Example ICE Scoring:**

| Experiment | Impact | Confidence | Ease | ICE Score | Priority |
|-----------|--------|-----------|------|-----------|----------|
| Reduce signup fields from 8 to 3 | 8 | 9 | 9 | 8.7 | 1 |
| Add social proof on pricing page | 7 | 7 | 8 | 7.3 | 2 |
| Referral program with $10 credit | 9 | 5 | 4 | 6.0 | 3 |
| AI-powered personalization | 9 | 4 | 2 | 5.0 | 4 |

### RICE Scoring Framework

**Formula:** RICE Score = (Reach × Impact × Confidence) / Effort

**Reach:** How many users will experience this? (absolute number per quarter)
**Impact (scale):** Massive (3), High (2), Medium (1), Low (0.5), Minimal (0.25)
**Confidence (%):** High (100%), Medium (80%), Low (50%)
**Effort:** Person-weeks required

**Example RICE Scoring:**

| Experiment | Reach | Impact | Confidence | Effort | RICE Score |
|-----------|-------|--------|-----------|--------|-----------|
| Email re-engagement campaign | 10,000 | 2 | 80% | 1 | 16,000 |
| Onboarding flow redesign | 5,000 | 3 | 100% | 4 | 3,750 |
| SMS notification feature | 8,000 | 1 | 50% | 3 | 1,333 |

### When to Use Which Framework

**Use ICE when:**
- Early-stage company with limited data
- Need quick prioritization
- Testing wide range of ideas
- Team is smaller (<10 people)

**Use RICE when:**
- Established company with good data
- Need to justify resource allocation
- Comparing very different initiatives
- Working with larger cross-functional teams

---

## Experiment Design {#design}

### The Experiment Canvas

**1. PROBLEM STATEMENT**
What problem are we solving?
- Current state metrics
- Why this matters
- Who is affected

**2. HYPOTHESIS**
We believe that [doing X] will cause [Y outcome] because [reasoning].

*Example:* "We believe that reducing signup form fields from 8 to 3 will increase signup completion rate by 20% because users are dropping off due to form fatigue."

**3. SUCCESS METRICS**

**Primary Metric:** The one metric that determines success
- Must be measurable
- Tied to business outcomes
- Clear success threshold

**Secondary Metrics:** Supporting indicators
- User engagement metrics
- Downstream conversion impacts
- Quality controls

**Guardrail Metrics:** Must not degrade
- Revenue per user
- Retention rates
- Customer satisfaction

**4. EXPERIMENT DESIGN**

**Control (A):** Current experience
**Treatment (B):** Variation being tested

**Traffic allocation:**
- 50/50 split (most common)
- 90/10 (when testing risky changes)
- Multi-armed bandit (when optimizing continuously)

**Targeting:**
- Who sees this test? (all users, new only, specific segment)
- Any exclusions?

**5. SAMPLE SIZE & DURATION**

Calculate required sample size based on:
- Baseline conversion rate
- Minimum detectable effect (MDE)
- Statistical power (typically 80%)
- Significance level (typically 95%)

**Duration considerations:**
- Run full weekly cycles (account for day-of-week effects)
- Minimum 1 week, ideally 2 weeks
- Stop only when reaching statistical significance OR conclusive negative result

**6. IMPLEMENTATION PLAN**

- Engineering requirements
- Design assets needed
- QA checklist
- Rollout plan
- Rollback criteria

---

## Statistical Rigor {#statistics}

### Sample Size Calculation

**Formula:**
```
n = (Z_α/2 + Z_β)² × (p₁(1-p₁) + p₂(1-p₂)) / (p₁ - p₂)²

Where:
- Z_α/2 = 1.96 (for 95% confidence)
- Z_β = 0.84 (for 80% power)
- p₁ = baseline conversion rate
- p₂ = expected new conversion rate
```

**Practical Example:**
- Baseline conversion: 10%
- Expected lift: 20% (new conversion: 12%)
- Required sample size: ~3,000 per variation

**Online Calculators:**
- Evan Miller's Sample Size Calculator
- Optimizely's Sample Size Calculator
- AB Testguide Calculator

### Statistical Significance

**What it means:**
95% confidence = Only 5% chance result is due to random chance

**Common Mistakes:**
1. **Peeking:** Stopping test early when reaching significance
   - Solution: Pre-determine sample size, wait for completion
2. **Multiple comparisons:** Testing 20 variations without correction
   - Solution: Bonferroni correction or limit variations
3. **Ignoring practical significance:** 0.1% lift that's statistically significant but meaningless
   - Solution: Set minimum practical effect threshold

### P-values and Confidence Intervals

**P-value:** Probability of seeing this result by chance
- p < 0.05: Statistically significant (standard threshold)
- p < 0.01: Highly significant
- p > 0.05: Not significant, inconclusive

**Confidence Interval:** Range where true effect likely falls
- 95% CI: [8%, 14%] means we're 95% confident true effect is between 8-14%
- Non-overlapping CIs = likely significant difference

### Bayesian vs Frequentist

**Frequentist (traditional):**
- "What's the probability of seeing this data, assuming no effect?"
- Fixed sample size
- Binary result (significant or not)

**Bayesian:**
- "What's the probability of an effect, given this data?"
- Can stop early with confidence
- Probability of being best variation

**When to use Bayesian:**
- Continuous optimization (e.g., pricing)
- Need to act quickly
- Multi-armed bandit scenarios

---

## Execution & Analysis {#execution}

### Pre-Launch Checklist

**Technical Validation:**
- [ ] Variations render correctly across devices
- [ ] Tracking fires properly (test in staging)
- [ ] No JavaScript errors
- [ ] Page load time not impacted
- [ ] Variations are properly randomized

**QA Process:**
- [ ] Cross-browser testing (Chrome, Safari, Firefox, Edge)
- [ ] Mobile responsive check
- [ ] Screen reader accessibility
- [ ] Force variation assignment to QA specific variants

**Stakeholder Alignment:**
- [ ] Experiment documented in shared tracker
- [ ] Key stakeholders notified of launch
- [ ] Customer support briefed on changes
- [ ] Rollback plan communicated

### Monitoring During Test

**Daily Checks (first 3 days):**
- Traffic split is correct (50/50 or as planned)
- No technical errors
- Sample ratio mismatch (SRM) check
- Preliminary results trending

**Weekly Reviews:**
- Progress toward sample size goal
- Secondary metrics health check
- Guardrail metrics stable
- User feedback or support tickets

### Analysis Framework

**1. Check Test Validity**
- Sample Ratio Mismatch (SRM): Are control/treatment roughly equal?
- Data quality: Any tracking issues?
- Outliers: Any extreme values skewing results?

**2. Primary Metric Analysis**
- What's the observed effect?
- Is it statistically significant? (p < 0.05)
- What's the confidence interval?
- Is the lift practically significant? (meets minimum threshold)

**3. Secondary Metrics Analysis**
- Do secondary metrics support the primary result?
- Any unexpected negative impacts?
- Segment analysis: Does effect vary by user type?

**4. Guardrail Metrics Check**
- Revenue impact neutral or positive?
- Retention unaffected?
- Other quality metrics stable?

**5. Qualitative Insights**
- User feedback or comments
- Support ticket themes
- Observed user behavior patterns

### Results Classification

**Clear Winner (Treatment B):**
- Statistically significant (p < 0.05)
- Practically significant (meets MDE threshold)
- Secondary metrics positive or neutral
- Guardrails healthy
- **Action:** Ship to 100%

**Clear Loser (Control A):**
- Treatment significantly underperforms
- Negative impact on key metrics
- **Action:** Turn off immediately

**Inconclusive:**
- Not statistically significant
- OR confidence interval too wide
- **Action:** Run longer, or redesign & retest

**Directionally Positive:**
- Trending positive but not significant
- Close to significance threshold
- **Action:** Consider running longer or larger test

---

## Scaling Winners {#scaling}

### Gradual Rollout Strategy

**Phase 1: Validate (5% traffic)**
- Monitor for any technical issues
- Check for segment-specific problems
- Duration: 2-3 days

**Phase 2: Ramp (25% traffic)**
- Confirm results hold at scale
- Watch for capacity/performance issues
- Duration: 3-5 days

**Phase 3: Majority (75% traffic)**
- Final validation before full launch
- Monitor all systems
- Duration: 3-5 days

**Phase 4: Full Rollout (100% traffic)**
- Complete migration
- Monitor for 1-2 weeks
- Document final results

### Compound Effects

**Test Stacking:**
Multiple winning tests compound over time

*Example:*
- Test 1: +10% signup rate
- Test 2: +15% activation rate
- Test 3: +8% retention rate
- **Combined Impact:** 1.10 × 1.15 × 1.08 = 1.37 = **+37% overall**

**Velocity Matters:**
- 1 test/month = 12 insights/year
- 2 tests/week = 100+ insights/year
- Compounding learning accelerates growth

### Building on Insights

**From Test Results to Strategic Themes:**

*Example: Signup form test succeeds*
1. **Immediate:** Reduce form fields
2. **Follow-up:** Test progressive disclosure
3. **Theme:** Minimize friction hypothesis
4. **Expansion:** Apply to other funnels (checkout, upgrade, etc.)

**Knowledge Base:**
Document learnings in shared wiki:
- What worked and why
- What failed and why
- Reusable patterns
- Avoid repeating failed tests

---

## Common Pitfalls {#pitfalls}

### Top 10 Experiment Mistakes

**1. Testing without clear hypothesis**
- Problem: Fishing for significance
- Solution: Write hypothesis before testing

**2. Stopping tests too early**
- Problem: Peeking problem, false positives
- Solution: Pre-calculate sample size, wait for completion

**3. Ignoring external factors**
- Problem: Holiday, PR spike, etc. skew results
- Solution: Be aware of context, compare to historical patterns

**4. Testing too many variations**
- Problem: Dilutes traffic, takes forever to reach significance
- Solution: Limit to 2-3 variations max

**5. Not segmenting results**
- Problem: Miss important differences by user type
- Solution: Plan segment analysis upfront

**6. Shipping based on trends, not significance**
- Problem: Ship false positives
- Solution: Wait for statistical significance

**7. Ignoring mobile vs desktop differences**
- Problem: Ship change that helps desktop but hurts mobile
- Solution: Always check device-level impact

**8. Testing vanity metrics**
- Problem: Improve clicks but hurt conversions
- Solution: Focus on business outcomes, not intermediary metrics

**9. Poor test instrumentation**
- Problem: Can't trust data, inconclusive results
- Solution: QA tracking thoroughly before launch

**10. Not documenting learnings**
- Problem: Repeat same failed tests, lose institutional knowledge
- Solution: Maintain experiment knowledge base

---

## Experiment Templates

### Template 1: Conversion Optimization Test

**Experiment Name:** [Descriptive name]

**Problem:**
[What's not working? Include current metrics]

**Hypothesis:**
We believe that [change] will [outcome] because [reasoning].

**Metrics:**
- Primary: [e.g., Signup conversion rate]
- Secondary: [e.g., Time to complete signup]
- Guardrail: [e.g., Signup quality (activation rate)]

**Design:**
- Control: [Current experience]
- Treatment: [New experience]
- Split: 50/50
- Audience: [All users / Specific segment]

**Sample Size:** [X per variation]
**Duration:** [Y days/weeks]
**MDE:** [Minimum detectable effect: X%]

**Implementation:**
- [ ] Engineering tasks
- [ ] Design assets
- [ ] Tracking implementation
- [ ] QA checklist

**Success Criteria:**
- Primary metric improves by ≥X%
- p-value < 0.05
- Guardrail metrics remain stable

---

### Template 2: Feature Launch A/B Test

**Feature:** [Feature name]

**Goals:** [What business problem does this solve?]

**Rollout Strategy:**
- Phase 1: 10% for 3 days (technical validation)
- Phase 2: 50% for 1 week (impact measurement)
- Phase 3: 100% if metrics positive

**Success Metrics:**
- Adoption: [X% of users engage with feature]
- Engagement: [Y actions per user]
- Retention: [Z% return rate]

**Risk Mitigation:**
- Rollback plan if errors occur
- Feature flag for quick disable
- Support team briefed

---

## Velocity Optimization

### How to Run More Tests

**1. Reduce Implementation Time**
- Standardized design system
- Reusable component library
- No-code tools where possible
- Parallel track design + engineering

**2. Simplify Test Designs**
- Start with MVT (Minimum Viable Test)
- Test one variable at a time
- Quick prototypes over pixel-perfect

**3. Faster Analysis**
- Automated reporting dashboards
- Pre-calculated statistical significance
- Template analysis frameworks
- Regular review cadence

**4. Pipeline Management**
- Maintain backlog of ready-to-test ideas
- Prioritize monthly
- Run tests in parallel on different pages
- Queue next test before current completes

**Velocity Targets by Company Stage:**
- Early-stage (<50 people): 2-4 tests/month
- Growth-stage (50-200 people): 8-12 tests/month
- Scale-stage (200+ people): 20+ tests/month

---

## Resources

### Tools
- **A/B Testing:** Optimizely, VWO, Google Optimize, GrowthBook
- **Analytics:** Mixpanel, Amplitude, Heap
- **Sample Size:** Evan Miller Calculator, Optimizely Calculator
- **Statistical Analysis:** R, Python (scipy.stats), Excel

### Books
- "Trustworthy Online Controlled Experiments" by Kohavi, Tang, & Xu
- "Testing with Humans" by Jason Hreha
- "Experimentation Works" by Stefan Thomke

### Courses
- Reforge: Experimentation & Testing
- Udacity: A/B Testing by Google
- CXL Institute: Conversion Optimization

### Communities
- Experimentation Hub (Slack)
- Online Controlled Experiments (LinkedIn)
- CXL Community

---

## Appendix: Statistical Formulas

### Conversion Rate Test

**Sample Size Formula:**
```
n = (Z_α/2 + Z_β)² × 2 × p × (1 - p) / (d²)

Where:
- p = pooled conversion rate
- d = minimum detectable effect (absolute)
- Z_α/2 = 1.96 (95% confidence)
- Z_β = 0.84 (80% power)
```

### T-Test for Continuous Metrics

**Test Statistic:**
```
t = (x̄₁ - x̄₂) / √(s₁²/n₁ + s₂²/n₂)

Where:
- x̄ = sample mean
- s² = sample variance
- n = sample size
```

### Confidence Interval

```
CI = p ± Z × √(p(1-p)/n)

95% CI: Z = 1.96
99% CI: Z = 2.58
```

---

**Remember:** The goal of experimentation isn't just to improve metrics—it's to build a sustainable learning engine that compounds over time. Focus on velocity, rigor, and documentation.