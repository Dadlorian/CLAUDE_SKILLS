# Experiment Tracker Template

Use this template to design, execute, and document growth experiments. Maintains institutional knowledge and prevents repeat experiments.

---

## Experiment Details

**Experiment ID**: [EXP-2024-001]
**Date Started**: [YYYY-MM-DD]
**Date Completed**: [YYYY-MM-DD]
**Owner**: [Name]
**Status**: (Planning / Running / Complete / Analyzing)

---

## 1. Hypothesis and Design

### 1.1 Hypothesis

**Clear, testable hypothesis**:
[If we [CHANGE], then [METRIC] will [IMPROVE BY]% because [REASONING]]

Example:
"If we reduce signup form from 7 to 3 fields, then signup completion rate will increase by 20% because form friction is high"

**Reasoning**:
[Why do you believe this? What evidence supports it?]
- Observation: ________________________
- Data point: ________________________
- User feedback: ________________________

### 1.2 Expected Impact

**Primary metric**:
[What metric are you optimizing for?]

**Current value**: _________
**Target value**: _________
**Percent improvement**: _________%

**Secondary metrics**:
1. ___________________ (measurement: ________)
2. ___________________ (measurement: ________)

**Failure case**:
[What would make this experiment unsuccessful? At what point do you kill it?]

---

## 2. Experiment Design

### 2.1 Control vs. Test Groups

**Control Group** (A):
[Description of current/baseline experience]

**Test Group** (B):
[Description of new experience/change]

**Change Summary**:
[Single clear sentence of what changed]

### 2.2 Randomization and Sample Size

**Sample size calculation**:
- Baseline metric value: __________%
- Target improvement: __________%
- Statistical power: 80% (standard)
- Confidence level: 95% (standard)
- Calculated sample size per group: __________

**Actual sample size**:
- Control group: __________ users
- Test group: __________ users

**Duration**: __________ days/weeks

**Timing considerations**:
- Start date: __________
- End date: __________
- Any holidays/events affecting?: __________

### 2.3 Implementation Details

**Where in product**:
[Where is this change visible? E.g., "Signup form on web"]

**How to implement**:
[Technical implementation details]
- Dev effort: __________ hours
- Testing complexity: Low / Medium / High

**Rollout method**:
(Feature flag / Split traffic / Beta group / Staged rollout)

**Rollback plan**:
[How will you quickly revert if something goes wrong?]

---

## 3. Metrics and Success Criteria

### 3.1 Key Metrics

| Metric | Control (A) | Test (B) | Difference | % Change | Statistical Significance |
|--------|------------|---------|-----------|----------|--------------------------|
| **Primary**: [Metric name] | | | | | |
| Secondary: [Metric name] | | | | | |
| Secondary: [Metric name] | | | | | |
| Guardrail: [Metric name] | | | | | |

### 3.2 Success Criteria

**Declare winner if**:
- Primary metric improves by _________%
- AND no negative impact on guardrail metrics
- AND statistically significant (p < 0.05)

**Declare loser if**:
- Primary metric declines
- OR guardrail metric significantly harmed
- OR negative user feedback

---

## 4. Execution Log

### 4.1 Timeline

| Phase | Date | Status | Notes |
|-------|------|--------|-------|
| Planning | | | |
| Design review | | | |
| Development | | | |
| QA/Testing | | | |
| Launch to 50% | | | |
| Launch to 100% | | | |
| Analysis | | | |

### 4.2 Issues and Adjustments

**Issue 1**: [Description]
- **Date discovered**: __________
- **Impact**: High / Medium / Low
- **Resolution**: __________
- **Adjusted**: Yes / No

**Issue 2**: [Description]
- **Date discovered**: __________
- **Impact**: High / Medium / Low
- **Resolution**: __________
- **Adjusted**: Yes / No

---

## 5. Results and Analysis

### 5.1 Raw Data

**Control Group (A)**:
- Users exposed: __________
- [Metric 1]: __________
- [Metric 2]: __________
- [Metric 3]: __________

**Test Group (B)**:
- Users exposed: __________
- [Metric 1]: __________
- [Metric 2]: __________
- [Metric 3]: __________

### 5.2 Statistical Analysis

**Primary Metric Analysis**:
- Control mean: __________ (±[confidence interval])
- Test mean: __________ (±[confidence interval])
- Difference: __________
- P-value: __________
- Statistically significant?: Yes / No

**Statistical power**:
- Achieved: __________%
- Note: If < 80%, insufficient statistical power

### 5.3 Segmented Analysis

Did results vary by user segment?

**Segment 1** [e.g., "Paid users"]:
- Control: __________%
- Test: __________%
- Difference: __________%
- Significant?: Yes / No

**Segment 2** [e.g., "Mobile users"]:
- Control: __________%
- Test: __________%
- Difference: __________%
- Significant?: Yes / No

**Segment 3** [e.g., "New users"]:
- Control: __________%
- Test: __________%
- Difference: __________%
- Significant?: Yes / No

### 5.4 Guardrail Metrics

Did any negative impacts occur?

| Guardrail Metric | Control | Test | Change | Status |
|------------------|---------|------|--------|--------|
| [Metric] | | | | ✓/✗ |
| [Metric] | | | | ✓/✗ |
| [Metric] | | | | ✓/✗ |

---

## 6. Qualitative Feedback

### 6.1 User Feedback

**Positive feedback**:
- "[Quote about what users liked]"
- "[Quote about what users liked]"

**Negative feedback**:
- "[Quote about what users didn't like]"
- "[Quote about what users didn't like]"

**Neutral observations**:
- "[What users said/did]"

### 6.2 Usage Patterns

**Observations from session recordings**:
- "[What did users do?]"
- "[Where did they struggle?]"
- "[What surprised you?]"

**Behavior changes**:
- [Did users interact differently with test vs. control?]

---

## 7. Decision and Recommendation

### 7.1 Result

**Decision**: Ship / Iterate / Kill

**Rationale**:
[Clear explanation of decision based on data and user feedback]

### 7.2 If Shipping

**Impact projection** (annual):
- Users affected: __________
- Metric impact: +__________%
- Revenue impact: $__________
- Implementation: Already done (launch to 100%)

**Rollout timeline**: Immediate / Phased over _________ weeks

**Monitoring plan**:
- Key metric to watch: __________
- Check frequency: Daily / Weekly
- Success target: __________

### 7.3 If Iterating

**What did we learn?**
[The hypothesis was partially validated but needs adjustment]

**Next test**:
- Change: __________
- Expected impact: __________
- Timeline: __________

### 7.4 If Killing

**Why kill it?**
[Explain why this approach doesn't work]

**Learnings**:
[What did we learn that informs future experiments?]

**Alternative approaches to try**:
1. __________
2. __________

---

## 8. Learnings and Insights

### 8.1 Key Learnings

**Learning 1**:
[Actionable insight from this experiment]

**Learning 2**:
[Actionable insight from this experiment]

**Learning 3**:
[Actionable insight from this experiment]

### 8.2 Surprising Results

**Surprise 1**:
[What unexpected result did you find?]
Impact: __________ | Importance: High / Medium / Low

**Surprise 2**:
[What unexpected result did you find?]
Impact: __________ | Importance: High / Medium / Low

### 8.3 Follow-up Questions

[What new questions does this experiment raise?]

1. __________
2. __________
3. __________

---

## 9. Document References

**Hypothesis source**:
[Where did this idea come from? Link to discussion/document]

**Related experiments**:
[Have you tested similar things before? Link to previous experiments]

**User research supporting**:
[Any interviews, surveys, or observations that led to this?]

**Competitive research**:
[Is a competitor doing this? Any industry benchmarks?]

---

## 10. Experiment Library Entry

**Tags** (for searching/filtering):
- #[category]: e.g., #activation, #retention, #revenue
- #[product-area]: e.g., #onboarding, #notifications
- #[test-type]: e.g., #UI, #messaging, #feature

**Experiment category**:
(Acquisition / Activation / Retention / Revenue / Referral / Engagement / Quality)

**Replicable for other products?**: Yes / No
If yes, how?: __________

---

## 11. ROI Analysis

**Experiment cost**:
- Engineering time: __________ hours × $______/hr = $__________
- Design time: __________ hours × $______/hr = $__________
- Analysis time: __________ hours × $______/hr = $__________
- Infrastructure: $__________
- **Total cost**: $__________

**Annual value of improvement**:
- Metric improvement: __________%
- Affected users: __________
- ARPU per affected user: $__________
- Annual value: $__________ (calculation: __)

**ROI**: __________ × or __________ % return

**Payback period**: __________ days/weeks

---

## 12. Sign-Offs

**Run by**: __________________ (Date: __________)
**Analyzed by**: __________________ (Date: __________)
**Approved by**: __________________ (Date: __________)

---

## Template Instructions

### When Planning Experiment:
1. Complete sections 1-2 (Hypothesis, Design)
2. Share with team for feedback before starting
3. Get approval to launch

### During Experiment:
1. Update Timeline (4.2) regularly
2. Document any Issues (4.2)
3. Monitor metrics in real-time

### After Experiment:
1. Complete Results (Section 5)
2. Gather user feedback (Section 6)
3. Make decision (Section 7)
4. Document learnings (Section 8)

### For Team Learning:
1. Add Tags and Category for searchability
2. Summarize learnings for knowledge base
3. Reference in future experiment planning

---

## Sample Hypothesis Templates

**Activation focus**:
"If we [remove friction X], then [activation rate] will increase by [%] because [users currently drop off here]"

**Retention focus**:
"If we [add feature X], then [day-30 retention] will improve by [%] because [users get more value/habit]"

**Revenue focus**:
"If we [change pricing X], then [free-to-paid conversion] will increase by [%] because [price elasticity shows]"

**Referral focus**:
"If we [add incentive X], then [referral rate] will improve by [%] because [users are motivated by]"

**Engagement focus**:
"If we [add notification X], then [session frequency] will increase by [%] because [users need trigger to return]"

---

## Historical Experiments Log

Keep this section to reference all past experiments:

| Exp ID | Hypothesis | Result | Learning | Date |
|--------|-----------|--------|----------|------|
| EXP-001 | | | | |
| EXP-002 | | | | |
| EXP-003 | | | | |

[Create a separate entry for each historical experiment]

---

## Notes

[Space for experiment-specific notes, observations, or meta-commentary]

---

## How to Use This Template

1. **Copy this template** for each new experiment
2. **Name file**: EXP-YYYY-NNN (sequential numbering)
3. **Fill in as you go**: Start with planning, add results as they come
4. **Reference previous**: Look at related experiments before starting
5. **Share insights**: Add to team learnings document
6. **Archive**: Keep complete history for reference

This repository of experiments becomes your company's growth knowledge base. Over time, patterns emerge, and you avoid repeating failed experiments.
