# RICE Scoring Calculator Template

Use this template to score your features using the RICE framework. Copy this and fill in your features.

## RICE Calculator Instructions

**RICE Score = (Reach × Impact × Confidence) / Effort**

### Scoring Parameters

**Reach**: Number of users affected in your timeframe (numeric)
- Use analytics data when available
- Be conservative on adoption assumptions
- Example: 5,000 users will use this feature in 6 months

**Impact**: How significantly each user is affected (multiplier)
- 3x = Massive impact (solves critical problem, major workflow change)
- 2x = High impact (significant improvement, noticeable time savings)
- 1x = Medium impact (clear improvement, helps but not critical)
- 0.5x = Low impact (nice to have, modest benefit)
- 0.25x = Minimal impact (barely noticeable)

**Confidence**: Your certainty in reach and impact estimates (percentage)
- 100% = Extensive data, proven patterns, shipped similar features
- 80% = Strong data signals, multiple information sources
- 50% = Some data, reasonable assumptions
- 25% = Limited data, mostly assumptions

**Effort**: Engineering effort in person-months
- 0.5 = Very small (1-2 weeks, single engineer)
- 1 = Small (2-4 weeks)
- 2 = Small-medium (1 month)
- 4 = Medium (2 months)
- 8 = Large (4 months)
- 16 = Very large (6+ months)

---

## RICE Calculation Spreadsheet

### Format 1: Simple Spreadsheet (Best for 10-20 features)

```
| # | Feature | Reach | Impact | Confidence | Effort | RICE Score | Priority | Notes |
|----|---------|-------|--------|-----------|--------|-----------|----------|-------|
| 1  | [Name]  | [#]   | [x]    | [%]       | [#]    | =ROUND((B*C*D)/E,0) | =RANK(F,F$2:F$30) | [Assumptions] |
| 2  | Better Onboarding | 10000 | 1 | 80% | 2 | 4000 | 1 | Improves signup completion |
| 3  | Dark Mode | 8000 | 1 | 100% | 4 | 2000 | 2 | Analytics shows night usage |
| 4  | AI Search | 2000 | 3 | 50% | 8 | 375 | 3 | Confidence low, worth piloting |
| 5  | Mobile App | 5000 | 2 | 70% | 16 | 437.5 | 2b | Major strategic initiative |
| 6  | Analytics Dashboard | 300 | 3 | 90% | 6 | 135 | 5 | Few users but high impact |
|    | ... | ... | ... | ... | ... | ... | ... | ... |
```

**Excel Formula**:
```
Cell F2: =ROUND((B2*C2*D2)/E2,0)
Cell G2: =RANK(F2,F$2:F$30)
```

### Format 2: Detailed Scoring Template (Best for 5-10 features, with notes)

```
RICE SCORING SHEET - Q[X] Prioritization

FEATURE 1: Better Onboarding
-------------------------------------------
Reach:
  - Current signups: 500/month
  - Target: New users completing onboarding in next 6 months
  - Estimate: 3000 new sign-ups × 100% (all must onboard)
  - REACH = 3000

  (Alternative for upgrade feature: active users × upgrade rate)

Impact:
  - Current completion rate: 60%
  - With better onboarding: 80%
  - Incremental impact: 20% of users stay vs. leave
  - This directly impacts retention and LTV
  - IMPACT = 1x (clear improvement, but not critical)

Confidence:
  - Have data: Current completion rate (analytics)
  - Have data: Impact of onboarding quality (customer research)
  - Missing data: Specific impact of this redesign
  - Research: 5 customer interviews on onboarding
  - CONFIDENCE = 80%

Effort:
  - Content/copy updates: 1 week
  - Design/UX work: 1 week
  - Frontend implementation: 1 week
  - Testing & polish: 1 week
  - EFFORT = 1 person-month

RICE CALCULATION:
(3000 × 1 × 0.80) / 1 = 2400

---

FEATURE 2: Dark Mode
-------------------------------------------
Reach:
  - Analyzed log data: 8000 users search between 8 PM - 6 AM
  - Assumption: 90% of night users would use dark mode if available
  - REACH = 8000 × 0.9 = 7200

Impact:
  - Reduces eye strain for night users
  - Makes app pleasant during evening hours
  - Not solving critical problem, convenience feature
  - Customer feedback: "I'd love this" (nice to have)
  - IMPACT = 1x

Confidence:
  - Have data: User activity by hour (analytics)
  - Have data: Feature exists in competitor products
  - Have research: NPS comments mention "dark mode" 3 times
  - High confidence in reach and impact
  - CONFIDENCE = 100%

Effort:
  - CSS refactoring: 2 weeks
  - Testing across browsers: 1 week
  - EFFORT = 0.75 ≈ 1 person-month

RICE CALCULATION:
(7200 × 1 × 1.0) / 1 = 7200

---

FEATURE 3: AI-Powered Search
-------------------------------------------
Reach:
  - Users performing searches: 2000/month active searchers
  - Question: Will AI search drive more searches?
  - Conservative estimate: Reach = 2000 users
  - (Some increase in usage, but hard to estimate)

Impact:
  - Current search success rate: 60%
  - With AI: Could reach 90% (if it works)
  - This would be massive - users find what they want
  - But: Relies on AI model working well
  - IMPACT = 3x (if it works)

Confidence:
  - Have data: Current search satisfaction (NPS comments)
  - Have research: 3 customer interviews want better search
  - Missing: Data on AI search quality in our domain
  - Risk: AI might not be accurate for our use case
  - CONFIDENCE = 50% (high risk, uncertain)

Effort:
  - Model training & tuning: 4 weeks
  - Search API refactor: 2 weeks
  - UI updates: 1 week
  - Testing & reliability: 2 weeks
  - EFFORT = 2.5 ≈ 3 person-months

RICE CALCULATION:
(2000 × 3 × 0.50) / 3 = 1000

---

FEATURE 4: Mobile Web App
-------------------------------------------
Reach:
  - Current mobile traffic: 25% of users
  - Question: Would mobile app change usage?
  - Assumption: Mobile app enables 30% increase in mobile usage
  - Mobile users currently: 5000
  - With app: 5000 × 1.3 = 6500
  - REACH = 6500 (incremental mobile usage)

Impact:
  - Mobile experience currently: Poor (web responsive but slow)
  - Mobile app would: Fast, offline capable, native feel
  - For mobile users: This would be major improvement
  - IMPACT = 2x (significant improvement for mobile users)

Confidence:
  - Have data: Mobile usage patterns (analytics)
  - Have research: Support tickets mention mobile issues (10+ tickets)
  - Missing: Data on app vs. web usage (no comparison)
  - Assumption: Assuming 30% usage increase is speculative
  - CONFIDENCE = 60%

Effort:
  - Choose platform (React Native? Native? PWA?): 1 week
  - Core features: 8 weeks
  - Testing & release: 2 weeks
  - Ongoing maintenance (platform specific): 4 weeks
  - EFFORT = 4 person-months

RICE CALCULATION:
(6500 × 2 × 0.60) / 4 = 1950

---

SUMMARY RANKING:
1. Dark Mode: 7200
2. Mobile App: 1950
3. Better Onboarding: 2400
4. AI Search: 1000

Wait, let me reorder by score:
1. Dark Mode: 7200
2. Better Onboarding: 2400
3. Mobile App: 1950
4. AI Search: 1000

RECOMMENDED PRIORITY:
Q1: Dark Mode (quick win)
Q2: Better Onboarding (high priority)
Q3: Mobile App (strategic initiative)
Future: AI Search (validate concept first)
```

---

## Blank RICE Template (Copy and Fill In)

```
FEATURE: [Name]
-------------------------------------------
Reach:
  - [Source of data or assumption]
  - [How many users affected?]
  - [Timeframe: 6 months? 12 months?]
  - REACH = [Number]

Impact:
  - [Current state]
  - [With feature]
  - [How significantly affected?]
  - IMPACT = [0.25x / 0.5x / 1x / 2x / 3x]

Confidence:
  - Have data: [What do we know?]
  - Missing data: [What's uncertain?]
  - Risk factors: [What could be wrong?]
  - CONFIDENCE = [25% / 50% / 80% / 100%]

Effort:
  - [Component 1]: [Estimate]
  - [Component 2]: [Estimate]
  - [Component 3]: [Estimate]
  - EFFORT = [Person-months]

RICE CALCULATION:
([Reach] × [Impact] × [Confidence]) / [Effort] = [Score]

---
```

---

## RICE Scoring Workshop Reference Sheet

Use this during your prioritization workshop.

```
QUICK REFERENCE: RICE PARAMETERS

REACH SCALE:
100 → 1,000 → 10,000 → 100,000 → 1,000,000
(Small segment | Team | Large segment | Whole product | Market)

IMPACT SCALE:
0.25x (barely noticeable)
0.5x (small benefit)
1x (clear benefit)
2x (significant improvement)
3x (solves critical problem)

CONFIDENCE SCALE:
25% (mostly guessing)
50% (some data, assumptions)
80% (good data, high confidence)
100% (extensive data, proven)

EFFORT SCALE:
0.5 (few days)
1 (1-2 weeks)
2 (1 month)
4 (2 months)
8 (4 months)
16 (6+ months)

---

SCORE INTERPRETATION:

2000+ → Exceptional priority, start immediately
1000-2000 → High priority, plan for this quarter
500-1000 → Medium priority, include in planning
100-500 → Lower priority, consider for later
<100 → Deprioritize unless strategic requirement

---

SAMPLE CALCULATION:

Feature: Search Improvement
Reach: 5000 users search regularly
Impact: 2x (significantly faster search)
Confidence: 80% (have data, some assumptions)
Effort: 2 person-months

Score = (5000 × 2 × 0.80) / 2
Score = 8000 / 2
Score = 4000

INTERPRETATION: Exceptional priority
```

---

## Google Sheets RICE Calculator

If using Google Sheets, use this formula:

```
COLUMN HEADERS:
A: Feature Name
B: Reach
C: Impact
D: Confidence (as decimal, so 80% = 0.8)
E: Effort
F: RICE Score
G: Priority Rank
H: Notes

FORMULAS:

Cell F2 (RICE Score):
=ROUND((B2*C2*D2)/E2, 0)

Cell G2 (Priority Rank):
=RANK(F2, F$2:F$100, 0)

Then copy down for all features.

Sort by Column F (descending) to see ranking.
```

### Google Sheets Template URL

Create a copy of this template:
https://docs.google.com/spreadsheets/d/[TEMPLATE_ID]/

Or create your own with the formulas above.

---

## Multi-Quarter RICE Planning

If planning across multiple quarters:

```
| Feature | Q1 Reach | Q1 Effort | Q1 RICE | Q2 Reach | Q2 Effort | Q2 RICE | Notes |
|---------|----------|-----------|---------|----------|-----------|---------|-------|
| Search Improvement | 5000 | 2 | 4000 | 7000 | 1 | 7000 | Grows usage post-launch |
| Dark Mode | 8000 | 1 | 2000 | 8000 | 0 | [Done] | One-time effort |
| Mobile | 6500 | 4 | 1950 | 9000 | 2 | 2700 | Grows over time |

Use time-aware reach estimates - how does adoption/reach grow?
```

---

## Sensitivity Analysis Template

After calculating RICE, test your assumptions:

```
BASE CASE:
Feature: [Name]
Base Score: [Score]

SENSITIVITY ANALYSIS:

What if Reach is 50% higher?
New Reach: [Higher number]
New Score: [New RICE score]
Impact: [How much does this change ranking?]

What if Effort is 50% higher?
New Effort: [Higher number]
New Score: [New RICE score]
Impact: [How much does this change ranking?]

What if Impact is lower than expected?
New Impact: [Lower multiplier]
New Score: [New RICE score]
Impact: [How much does this change ranking?]

What if Confidence is lower?
New Confidence: [Lower percentage]
New Score: [New RICE score]
Impact: [How much does this change ranking?]

CONCLUSION:
Most sensitive to: [Which parameter most affects score?]
Least sensitive to: [Which parameter matters least?]
Recommendation: [Get more data on sensitive areas]
```

---

## Handling Comparison Issues

### Features With Very Different Reach

If comparing:
- Feature A: Reach 100,000 (affects everyone)
- Feature B: Reach 1,000 (affects niche)

This is OK - RICE accounts for reach. Feature A's reach advantage should reflect in scores.

BUT: Don't compare dark mode (affects everyone) to "enterprise feature for 5 accounts" in same session.

**Better**: Separate portfolios for different segments.

### Features With Very Different Effort

If comparing:
- Feature A: Effort 0.5 (very small)
- Feature B: Effort 16 (very large)

This is OK - RICE accounts for effort. If A and B have similar total scores, A is more efficient per person-month.

**Insight**: Small, high-value features usually rank higher (quick wins).

### Comparing Across Teams/Products

If you have multiple products/teams, score separately and compare within product:

```
PRODUCT A FEATURES:
1. Feature A1: 3000
2. Feature A2: 2000
3. Feature A3: 1500

PRODUCT B FEATURES:
1. Feature B1: 2500
2. Feature B2: 2000
3. Feature B3: 1200

DON'T: Say "A1 has higher score, prioritize over B1"
DO: Allocate resources: 60% to A (given reach), 40% to B
```

---

## Common RICE Mistakes (Avoid These)

### Mistake 1: Over-Precision
- Wrong: "RICE score is 2,347"
- Right: "RICE score is 2,300, roughly 2-3K range"
- Reason: Estimates aren't precise

### Mistake 2: Confidence Too High
- Wrong: Always using 100% confidence
- Right: Use 50-80% for most estimates
- Reason: Estimates are inherently uncertain

### Mistake 3: Forgetting Timeframe
- Wrong: "Reach = all users"
- Right: "Reach = users affected in next 6 months"
- Reason: Timeframe matters for estimation

### Mistake 4: Mixing Multipliers
- Wrong: Impact 1.5 (between 1x and 2x)
- Right: Stick to 0.25x, 0.5x, 1x, 2x, 3x
- Reason: Consistency helps comparison

### Mistake 5: Not Documenting Assumptions
- Wrong: Score of 4000, no notes on how you got there
- Right: Document reach logic, impact logic, confidence basis
- Reason: Future-you won't remember, team needs to understand

---

## Using RICE Results

### What The Scores Mean

**Top 20% (1000+)**: Exceptional opportunities
- Execute immediately or very soon
- High confidence you should do this
- Strategic priority

**Second 20% (500-1000)**: High priority
- Plan for this quarter or next
- Worth committing resources to
- Good strategic fit

**Third 20% (100-500)**: Medium priority
- Include in longer-term planning
- Execute when capacity allows
- Lower urgency

**Bottom 40% (<100)**: Lower priority
- Deprioritize unless special reason
- Nice-to-haves
- Consider if team has spare capacity

### Using Scores For Sequencing

```
TOP TIER (Scores 3000+):
→ Do these immediately
→ Sequential or parallel based on dependencies

SECOND TIER (Scores 1000-3000):
→ Plan for this quarter
→ Schedule based on team capacity

THIRD TIER (Scores 500-1000):
→ Plan for next quarter
→ Rough sequencing

LONG TAIL (Scores <500):
→ Future/backlog
→ Revisit if circumstances change
```

---

## Final Tips

1. **Document assumptions** - Why you estimated reach/impact/confidence that way
2. **Update quarterly** - Scores change as market/data changes
3. **Track actual vs. predicted** - Learn for future estimation
4. **Use for discussion, not gospel** - RICE informs, doesn't decide
5. **Be consistent** - Use same framework, same rules, same definitions
6. **Involve team** - Engineering estimates effort, CS knows customer, design knows feasibility

