# RICE Scoring Framework: Deep Dive Guide

Based on Intercom's industry-leading prioritization methodology, RICE provides a systematic, quantitative approach to feature prioritization. This guide provides comprehensive instruction on implementing RICE scoring in your organization.

## Overview

**RICE = (Reach × Impact × Confidence) / Effort**

RICE is ideal for:
- Product teams with 5+ feature candidates
- Cross-functional organizations needing objective comparison
- Data-driven cultures comfortable with quantitative models
- Teams managing complex trade-offs between multiple initiatives

---

## Component 1: REACH

**Definition**: The number of users or customers impacted by the feature within a defined timeframe.

**Key Principle**: Reach must be quantified, not estimated casually. Use data whenever possible.

### Determining Reach

#### Step 1: Define Your Timeframe
Choose a single, consistent timeframe for all features:
- **Quarterly (3 months)**: Typical for rapid iteration products
- **Semi-annual (6 months)**: Balanced for mid-cycle planning
- **Annual (12 months)**: Longer-term strategic planning

**Important**: Use same timeframe for all features being compared.

#### Step 2: Define "Impacted Users"

**Impacted** means:
- User directly uses the feature, OR
- User significantly benefits from feature (even if not primary user)
- Time-bounded impact (not lifetime, just timeframe)

**Examples**:
- "Customers who currently search 2+ times per week" → Reach = 15,000
- "Users in US, UK, Canada markets" → Reach = 85,000
- "Enterprise customers with 10+ team members" → Reach = 2,500

#### Step 3: Estimate Adoption

If feature is new, estimate adoption:
- **Conservative approach**: Assume 20-30% of eligible users adopt
- **Research-backed**: Use industry benchmarks or similar feature data
- **Historical data**: Look at adoption curves from previous features

**Formula**: Reach = Total Eligible Users × Adoption Rate

**Example**:
- Total users: 100,000
- Users in paid tier (eligible): 40,000
- Estimated adoption (research-backed): 50%
- **Reach = 40,000 × 0.5 = 20,000**

#### Step 4: Consider Time-Based Adjustments

**Seasonal features**:
- Budget app (used heavily tax season): 3x reach in Q1
- Holiday features: High reach Dec, low other months
- **Adjust**: Use realistic, time-bound reach

**Viral features**:
- Feature that grows through network effects
- Start conservative, acknowledge uncertainty in confidence
- **Example**: Referral feature - reach grows as more users adopt

### Reach Estimation Data Sources

**Ranked by Reliability** (use highest available):

1. **Product Analytics** (Highest)
   - Current usage data for similar features
   - Segment sizes from analytics platform
   - Actual user behavior patterns
   - Upgrade likelihood from cohort analysis

2. **User Research**
   - Customer interviews (qualitative confirmation)
   - Survey data (quantitative preference signals)
   - Beta testing engagement metrics
   - User feedback volume and intensity

3. **Historical Data**
   - Adoption of previous similar features
   - Upsell/upgrade conversion rates
   - Churn rates by segment
   - Feature usage curves

4. **Benchmarking**
   - Industry adoption rates
   - Competitor feature usage
   - Similar product benchmarks
   - Market research reports

5. **Assumptions** (Lowest)
   - Market segment estimates
   - Projected growth rates
   - Estimated customer lifetime value impact
   - **Use only when no other data available**

### Reach Estimation Example Template

```
Feature: Advanced Search Filters

Step 1: Timeframe = 6 months

Step 2: Define Impacted Users
- Feature for: All search users (not admin-only)
- Current search users: 45,000/100,000 total users
- Frequency: 2+ searches per month in past 6 months
- Eligible pool: 45,000 users

Step 3: Adoption Rate
- Similar feature (custom reports) adopted by 60% of eligible
- Advanced search lower friction (no setup required)
- Estimated adoption: 60%
- Calculation: 45,000 × 0.60 = 27,000

Step 4: Validation
- Compare to similar features
- Reality-check with team
- Document assumptions

REACH = 27,000
```

### Common Reach Mistakes

**Mistake 1: Using Lifetime Instead of Timeframe Reach**
- Wrong: "50,000 customers could eventually use this"
- Right: "8,000 customers will likely use this in next 6 months"

**Mistake 2: Double-Counting Users**
- Wrong: Counting same user multiple times
- Right: Unique users affected in timeframe

**Mistake 3: Overestimating Adoption**
- Wrong: Assuming 90% adoption for non-critical feature
- Right: Historical data shows 30-40% adoption for similar features

**Mistake 4: Ignoring Cannibalization**
- Wrong: Reach for new report = all users
- Right: Many users switch from old report → net new reach lower

**Mistake 5: Unclear Definition**
- Wrong: "Power users will use this"
- Right: "Users generating 100+ API calls/day will use this"

---

## Component 2: IMPACT

**Definition**: How significantly each impacted user will be affected by the feature.

**Key Principle**: Impact is multiplicative, not descriptive. Use standardized scale.

### Impact Scoring Scale

Standard 4-level scale (avoid middle values like 1.5x):

| Impact | Multiplier | User Experience | Example |
|--------|-----------|-----------------|---------|
| Massive | 3x | Solves critical pain point, dramatically improves workflow | Dark mode (for night workers), fixing crashed app |
| High | 2x | Significantly improves experience, noticeable time/effort savings | Improved search speed, better notifications |
| Medium | 1x | Noticeable improvement, but not critical | UI refinement, new dashboard view |
| Low | 0.5x | Small positive effect, nice-to-have | Minor UX polish, keyboard shortcut |
| Minimal | 0.25x | Very small improvement, barely noticeable | Color change, small copy improvement |

**Visual Scale**:
```
3x  |█████████ Massive impact
2x  |███████ High impact
1x  |█████ Medium impact
0.5x|██ Low impact
0.25x|█ Minimal impact
```

### Determining Impact

#### Method 1: Customer Research (Most Reliable)

**Conduct impact research**:
1. Interview 5-10 target users about problem severity
2. Ask: "How much time does this problem cost you weekly?"
3. Ask: "How frustrated are you with current solution?"
4. Ask: "How would this feature change your workflow?"

**Scoring based on research**:
- Users consistently mention critical problem → 3x
- Problem causes moderate frustration → 2x
- Convenience improvement mentioned → 1x
- Minor improvement → 0.5x or 0.25x

#### Method 2: Analogous Feature Analysis

**Compare to past features**:
- Similar feature released 6 months ago
- What was actual impact on user satisfaction, productivity, retention?
- Apply similar impact score

**Example**:
- Keyboard shortcuts feature: Released last year, measured 1.5x adoption rate increase
- This feature similar in scope: Estimate 1x impact

#### Method 3: Workflow Analysis

**Map impact to user workflow**:
- Current state: User manual task takes 15 minutes, 3 times/week = 45 min/week
- With feature: Task takes 3 minutes = 9 min/week
- Time saved: 36 minutes/week = ~26 hours/year per user
- User perception: High efficiency gain → 2x impact

#### Method 4: Business Metrics

**Impact on key metrics**:
- Revenue impact: $100 increased LTV per user → 2x-3x
- Retention impact: 5% improvement in 12-month retention → 2x
- Activation impact: 10% improvement in onboarding completion → 2x
- Cost savings: 20% reduction in support tickets → 1.5x

### Impact Estimation Example

```
Feature: Custom Workflow Automation

Research Findings:
- Interviewed 8 enterprise customers
- Current workaround: Manual monthly reconciliation, 8 hours
- Feature reduces to: 15 minutes (mostly system running)
- Time saved: 7.75 hours/month = 93 hours/year per user
- Emotional impact: "Would be transformative for team operations"

Impact Assessment:
- Time savings: 93 hours/year = massive
- Emotional/strategic value: Very high ("transformative")
- Competitive disadvantage without: Moderate
- Job-to-be-done impact: Core job enablement

IMPACT = 3x (Massive)
```

### Impact in Different Contexts

**For Features Targeting Different User Segments**:

Use weighted approach:
```
Overall Impact = (Segment A Impact × % Reach in A) + (Segment B Impact × % Reach in B)

Example:
- Free users (50% reach): 1x impact
- Paid users (50% reach): 3x impact
- Overall Impact = (1x × 0.5) + (3x × 0.5) = 2x
```

### Impact Scoring Common Mistakes

**Mistake 1: Confusing Popularity with Impact**
- Wrong: "All users will use this, so 3x impact"
- Right: "All users will use this, but it's just convenience, so 1x impact"

**Mistake 2: Using 5-10 Scale Instead of 4 Multipliers**
- Wrong: Rating on 1-10 scale
- Right: Using standardized 0.25x, 0.5x, 1x, 2x, 3x multipliers

**Mistake 3: Not Differentiating from Reach**
- Wrong: High reach features always get high impact
- Right: High reach + low impact per user = medium score

**Mistake 4: Ignoring Segment Differences**
- Wrong: "Everyone will find this valuable"
- Right: "Power users find it 3x valuable, casual users find it 0.5x valuable"

**Mistake 5: Optimism Bias**
- Wrong: Assuming maximum impact without evidence
- Right: Using conservative estimates, documenting assumptions

---

## Component 3: CONFIDENCE

**Definition**: Your certainty level in the Reach and Impact estimates.

**Key Principle**: Be honest about uncertainty. Low confidence should pull down score, not be ignored.

### Confidence Scoring Scale

| Confidence Level | Percentage | Criteria | Example |
|-----------------|-----------|----------|---------|
| High | 100% | Extensive data, proven pattern, shipped similar feature | Released similar feature, measured actual impact |
| Medium-High | 80% | Strong data signals, multiple sources, recent research | Customer research + usage patterns confirm |
| Medium | 50% | Some data, reasonable assumptions, modest uncertainty | Basic customer feedback + analytics |
| Low | 25% | Limited data, mostly assumptions, high uncertainty | Market trends, competitor analysis |
| Very Low | 10% | Speculation, few data points, high risk | Early market, emerging need, unproven segment |

### Determining Confidence

#### Step 1: Assess Reach Confidence
- Do you have actual usage data? → High confidence
- Did you survey relevant user segment? → Medium-high confidence
- Are you extrapolating from limited data? → Medium confidence
- Making market assumptions? → Low confidence

#### Step 2: Assess Impact Confidence
- Did you interview target users extensively? → High confidence
- Did similar feature show this impact? → High confidence
- Did customer support report this problem? → Medium-high confidence
- Customer mentions suggest problem? → Medium confidence
- Assumption about problem importance? → Low confidence

#### Step 3: Calculate Blended Confidence
```
Confidence = (Reach Confidence + Impact Confidence) / 2

Example:
- Reach Confidence: 80% (good usage data + some assumptions)
- Impact Confidence: 50% (limited research data)
- Blended Confidence: (80% + 50%) / 2 = 65% → Round to 50%
```

### Confidence Assessment Example

```
Feature: AI-Powered Recommendations

Reach Confidence Assessment:
- Have: User search/browse data → +40%
- Have: Historical feature adoption data → +20%
- Missing: Segment preferences → -10%
- Missing: Cross-product usage patterns → -5%
- Reach Confidence: 45% → Round to 50%

Impact Confidence Assessment:
- Have: Customer interviews (n=5) → +30%
- Have: Support ticket patterns → +15%
- Missing: Long-term adoption data → -20%
- Missing: Comparison to competitors → -10%
- Impact Confidence: 15% → Round to 25%

Blended Confidence:
- (50% + 25%) / 2 = 37.5% → Round down to 25%

CONFIDENCE = 25%
```

### Increasing Confidence

**To improve Reach Confidence**:
1. Analyze product analytics for current behavior
2. Run user survey with statistically significant sample
3. Study competitor adoption data
4. Interview sales/CS teams on customer requests

**To improve Impact Confidence**:
1. Conduct user interviews with 8-10 target users
2. Run prototype test with target segment
3. Measure impact of analogous feature released previously
4. Review support tickets for problem frequency/severity

### When Confidence Should Affect Prioritization

**High Confidence (80-100%)**
- Trust the score, prioritize accordingly
- Risk: Execution risk, not prioritization risk

**Medium Confidence (50-75%)**
- Trust the relative ranking
- Consider slight downward adjustment for higher uncertainty
- Plan for post-launch validation

**Low Confidence (25-50%)**
- Heavily weight against in prioritization
- Consider splitting feature into phases
- Plan for early learning/validation
- May warrant experiment first

**Very Low Confidence (<25%)**
- Lowest priority unless strategic must-have
- Recommend pre-validation/prototype
- Consider explicit learning initiative
- May not be appropriate for core roadmap

### Confidence in RICE Scoring Example

```
Feature A: Dark Mode (High Confidence)
- Reach: 8000 (analytics data, 100% confidence)
- Impact: 1x (user research validates, 100% confidence)
- Confidence: 90% (blended high confidence)
- Effort: 4
- RICE: (8000 × 1 × 0.9) / 4 = 1800

Feature B: AI Search (Low Confidence)
- Reach: 2000 (assumptions, 25% confidence)
- Impact: 3x (research indicates, 50% confidence)
- Confidence: 25% (low blended)
- Effort: 8
- RICE: (2000 × 3 × 0.25) / 8 = 187.5

Dark Mode scores 10x higher, partly due to confidence difference.
This is appropriate - invest in high confidence initiatives first.
```

---

## Component 4: EFFORT

**Definition**: Engineering effort required to build the feature, typically measured in person-months.

**Key Principle**: Get engineering input. Account for testing, documentation, infrastructure.

### Effort Estimation Scale

Standard effort scale (log scale to reflect complexity doubling):

| Effort (Person-Months) | Relative Size | Timeline | Team Size | Example |
|--------|----------|----------|-----------|---------|
| 0.5 | Tiny | 1-2 weeks | 1 engineer | Change button color, fix typo |
| 1 | Very Small | 2-4 weeks | 1 engineer | Single feature flag, small bug fix |
| 2 | Small | 1 month | 1-2 engineers | Simple form, API endpoint |
| 4 | Medium | 2 months | 2 engineers | Dashboard view, moderate API work |
| 8 | Large | 4 months | 3-4 engineers | Mobile feature, major refactor |
| 16 | Very Large | 6+ months | 4+ engineers | Mobile app, platform shift |

### Effort Estimation Process

#### Step 1: Engineering Scope Definition
- Define feature scope precisely (avoid scope creep)
- Identify required technical work
- List dependencies and blockers
- Consider edge cases and error handling

#### Step 2: Get Engineering Input
- Have senior engineer estimate
- Include:
  - Core development (coding)
  - Testing and QA
  - Infrastructure changes
  - Documentation
  - Integration with other systems

#### Step 3: Add Buffers
- **Optimistic estimate**: Best case, no issues
- **Add buffer**: 30-50% contingency for unknowns
- **Total effort**: Optimistic + buffer

#### Step 4: Reality Check
- Compare to similar features shipped
- Does timeline feel realistic?
- Adjust if optimism bias detected

### Effort Estimation Example

```
Feature: Advanced Analytics Dashboard

Scope Definition:
- Real-time data visualization for 5 key metrics
- Customizable widgets
- Role-based permissions
- Export to PDF
- Mobile responsive

Core Development Breakdown:
- Frontend (React component library): 3 weeks
- Backend API layer: 2 weeks
- Database optimization: 1 week
- Authentication/permissions: 1 week
- Testing: 2 weeks
- Documentation: 1 week

Optimistic Total: 10 weeks = 2.5 months

Buffer for unknowns:
- Unexpected dependencies: +20%
- Performance optimization: +10%
- Edge cases: +10%
- Buffer: +40%

Total Effort: 2.5 months × 1.4 = 3.5 months ≈ 4 person-months

EFFORT = 4
```

### Effort Considerations

**Scaling Effort with Team**:
- Small task (1 PM): 1 engineer, 4 weeks
- Medium task (4 PM): 2 engineers, 8 weeks
- Large task (8 PM): Can't reduce to < 4 weeks with single team
- **Effort = person-months, not calendar months**

**Infrastructure & Maintenance**:
- Include ongoing maintenance (first 3 months)
- Include monitoring and alerts setup
- Include potential rollback preparation

**Unknown Complexity**:
- New technology: +50% to estimate
- Complex integration: +30% to estimate
- Architectural change: +50% to estimate
- Clear/straightforward: No buffer needed

### Effort Estimation Common Mistakes

**Mistake 1: Optimism Bias**
- Wrong: "Engineer says 2 weeks, we'll estimate 2 weeks"
- Right: "Engineer says 2 weeks, we estimate 3-4 weeks with buffer"

**Mistake 2: Forgetting Invisible Work**
- Wrong: Only counting development hours
- Right: Including testing, debugging, documentation, deployment

**Mistake 3: Not Including Integration Work**
- Wrong: Estimating feature in isolation
- Right: Including integration with existing systems

**Mistake 4: Using Calendar Months Instead of Person-Months**
- Wrong: "We can parallelize, so 16 PM effort = 4 calendar months"
- Right: Keep effort in person-months for scoring consistency

**Mistake 5: Ignoring Technical Debt**
- Wrong: Estimate assumes clean codebase
- Right: Add buffer for refactoring/cleanup if needed first

---

## Calculating RICE Scores

### Basic Calculation

```
RICE = (Reach × Impact × Confidence) / Effort
```

### Score Interpretation

- **Score 1000+**: Exceptional priority, start immediately
- **Score 500-1000**: High priority, plan for current quarter
- **Score 100-500**: Medium priority, include in planning
- **Score 10-100**: Lower priority, nice-to-have
- **Score <10**: Deprioritize unless strategic imperative

### Example RICE Calculation

| Feature | Reach | Impact | Confidence | Effort | RICE Score | Priority |
|---------|-------|--------|-----------|--------|-----------|----------|
| Better Onboarding | 10,000 | 1x | 80% | 2 | 4000 | 1 |
| AI Search | 2,000 | 3x | 50% | 8 | 375 | 3 |
| Dark Mode | 8,000 | 1x | 100% | 4 | 2000 | 2 |
| Mobile App | 5,000 | 2x | 70% | 16 | 437.5 | 2b |
| Analytics Dashboard | 300 | 3x | 90% | 6 | 135 | 5 |

### Handling Ties and Close Scores

When scores are close (within 10-20%), consider:
- **Strategic alignment**: Which better supports OKRs?
- **Team momentum**: Which builds on recent work?
- **Dependencies**: Which unblocks other work?
- **Risk**: Which has clearer path to success?

---

## RICE Scoring Workshop Agenda

**Duration**: 2-3 hours
**Participants**: PMs, engineers, designers, key stakeholders

### Pre-Work (1 week before)
- Identify 10-20 feature candidates
- Collect reach/impact/effort data
- Create estimation worksheet

### Workshop Agenda

**30 min - Framework Explanation**
- Review RICE framework and scoring rules
- Walk through 2-3 examples
- Answer clarifying questions

**90 min - Scoring Session**
- Feature by feature, discuss estimates
- Facilitate healthy debate
- Reach consensus on scores
- Document assumptions

**30 min - Results & Decisions**
- Review final rankings
- Discuss surprising results
- Confirm strategic alignment
- Plan next steps

### Post-Workshop (1 week)
- Document decisions and reasoning
- Communicate roadmap to organization
- Establish review cadence

---

## Sensitivity Analysis: Testing Assumptions

Once you've scored all features, test your assumptions:

### What If Analysis

**Scenario 1**: "What if adoption is 50% higher?"
- Recalculate reach with higher adoption
- How do rankings change?
- Which features become more attractive?

**Scenario 2**: "What if effort is 50% higher?"
- Recalculate effort with 50% buffer
- Which features drop in priority?
- What's the break-even point?

**Scenario 3**: "What if impact is moderate instead of high?"
- Recalculate with lower impact multiplier
- How sensitive is ranking to impact estimates?

### Sensitivity Analysis Example

```
Feature: AI Search Features
Base Case RICE: (2000 × 3 × 0.5) / 8 = 375

Sensitivity Tests:
- If Reach = 3000 (50% higher): (3000 × 3 × 0.5) / 8 = 562.5 (+50%)
- If Impact = 2x (not 3x): (2000 × 2 × 0.5) / 8 = 250 (-33%)
- If Effort = 12 (50% more): (2000 × 3 × 0.5) / 12 = 250 (-33%)

Key Insight: Score is sensitive to Impact and Effort estimates.
Lower confidence in these should warrant additional research.
```

---

## RICE Score Maintenance

### When to Re-Score

**Monthly**:
- New feature requests added
- Effort estimates significantly refined
- Market conditions dramatically changed

**Quarterly**:
- Full re-scoring of all features
- Incorporate learning from released features
- Adjust confidence levels
- Update reach estimates based on new data

**As-Needed**:
- Competitive threat emerges
- Major customer feedback
- Strategic pivot
- Resource availability changes

### Tracking Actual vs. Predicted

**After Feature Release**:
- Measure actual reach (vs. estimate)
- Measure actual impact (NPS, retention, revenue impact)
- Document in RICE estimation log
- Use to calibrate future estimates

---

## Tools & Templates

See accompanying:
- rice_calculator_template.md (Spreadsheet template)
- prioritization_workshop_script.md (Facilitation guide)
- prioritization_workshop_guide.md (Complete workshop planning)

