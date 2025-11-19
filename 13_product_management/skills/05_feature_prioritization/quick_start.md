# Feature Prioritization: 30-Minute Quick Start Guide

Make defensible feature decisions that maximize impact and align teams on trade-offs.

---

## Your 30-Minute Roadmap

- **Minutes 1-5**: Understand prioritization frameworks (RICE, Value vs. Effort, Kano)
- **Minutes 6-15**: Score your backlog using RICE framework
- **Minutes 16-25**: Facilitate stakeholder alignment on top priorities
- **Minutes 26-30**: Create prioritized backlog and communicate trade-offs

---

## 5 Essential Concepts Every PM Needs

### 1. RICE Scoring = (Reach × Impact × Confidence) / Effort
RICE forces you to estimate impact quantitatively rather than relying on gut feel. It's transparent and defensible.

**Reach**: How many users will be affected in next 3 months? (numeric: 100, 1000, 10000)
**Impact**: How much does each user benefit? (3x huge, 2x significant, 1x noticeable, 0.5x minor)
**Confidence**: How sure are you in estimates? (100% certain, 80% likely, 50% medium, 25% guessing)
**Effort**: How much work to build? (1 week, 2 weeks, 1 month, 2 months, 4+ months)

**Actionable**: Spend 15 min scoring your top 10 feature requests with RICE. Highest scores rise to top.

### 2. Value vs. Effort Framework: Simple but Powerful
Plot features on a 2x2 matrix: High value/Low effort (do first), High value/High effort (do later), Low value/Low effort (maybe), Low value/High effort (avoid).

**Actionable**: Quick visual prioritization for executive meetings. Helps kill ideas that are shiny but not valuable.

### 3. Kano Model: Different Kinds of Value
Not all features are equal. Some are **must-haves** (expectations), some are **satisfiers** (more is better), some are **delighters** (wow factor).

**Must-haves**: Missing them creates dissatisfaction; having them doesn't delight (e.g., mobile responsiveness, basic security)
**Satisfiers**: More is better; linear impact (e.g., speed, search results)
**Delighters**: Unexpected features that create strong positive emotion; differentiate you (e.g., smart recommendations, UI polish)

**Actionable**: Classify your top 10 features. Focus on must-haves first, then satisfiers, then delighters.

### 4. Prioritization is About Trade-Offs
Prioritizing one thing means deprioritizing others. Use frameworks to make these trade-offs explicit and defensible.

**Bad**: "Everything is high priority" (meaningless)
**Good**: "We're focusing on reducing churn (Tier 1) rather than adding new features (Tier 2) because retention is the bigger blocker to growth"

**Actionable**: When you prioritize feature A, explicitly state what you're NOT doing and why.

### 5. Validate Assumptions Before Major Development
A feature that scores high in RICE might be wrong. Validate with customer research, prototypes, or small MVPs before full build.

**Actionable**: For your top-3 features, identify your riskiest assumption. Plan one small test (user research, prototype feedback) before coding.

---

## First Steps Checklist

### Week 1: Backlog Inventory
- [ ] List all feature requests from last 3 months (from customers, sales, support, team)
- [ ] Group similar requests (consolidate duplicates)
- [ ] Aim for 30-50 total items to prioritize
- [ ] Remove obvious no's ("I want cheaper pricing"—can't prioritize this way)

### Week 2: Score with RICE
For each feature, estimate:

- [ ] **Reach**: "How many users affected in next 3 months?"
  - Talk to sales/support to understand frequency
  - Use customer interviews, surveys, support tickets
  - Be conservative (users expressing interest < users who will actually use)

- [ ] **Impact**: "How much better will each user's life/work be?"
  - 3x = saves 30+ min/week, critical blocker
  - 2x = saves 10-30 min/week, important problem
  - 1x = nice-to-have, saves <10 min/week
  - 0.5x = incremental improvement

- [ ] **Confidence**: "How sure are you in these estimates?"
  - 100% = validated data, customer interviews confirm
  - 80% = strong signals, some validation
  - 50% = reasonable assumptions, some uncertainty
  - 25% = guessing, minimal evidence

- [ ] **Effort**: "How much engineering effort?"
  - 1 = 1-2 weeks (single engineer, straightforward)
  - 2 = 3-4 weeks (one engineer, some complexity)
  - 4 = 1-2 months (two engineers, moderate complexity)
  - 8 = 2-4 months (team effort, significant work)
  - 16+ = major initiative, 4+ months

### Week 3: Rank and Align
- [ ] Calculate RICE scores: (Reach × Impact × Confidence) / Effort
- [ ] Sort by score (highest first)
- [ ] Review top 20 with engineering: "Are effort estimates realistic?"
- [ ] Review with leadership: "Any strategic objections?"
- [ ] Remove obvious outliers where estimates seem off

### Week 4: Create Prioritized Backlog
- [ ] Top 5 features: "Now" (next sprint/month)
- [ ] Next 10-15 features: "Later this quarter"
- [ ] Remaining: "Backlog for future consideration"
- [ ] Communicate to team: Why this order? What changed?

---

## Common Mistakes to Avoid

### Mistake 1: Anchoring on Vocal Requests
The loudest customer or most insistent sales rep isn't always right. Use data, not volume.

**Fix**: Weight features by reach (number of customers affected), not by how many times you heard the request from one source.

### Mistake 2: Ignoring Effort (Optimism Bias)
"This should be easy to build." Then engineering says "Actually, 4 months."

**Fix**: Ask engineering directly. Don't guess. Effort significantly impacts prioritization (it's the denominator in RICE).

### Mistake 3: Changing Priorities Weekly
"Wait, feature X is more important" every week erodes trust and prevents momentum.

**Fix**: Commit to priorities for a quarter. Update monthly, not daily. Only pivot for emergencies (security, major churn).

### Mistake 4: Confusing Popularity with Impact
A feature 100 customers requested sounds important. But if only 5 of them will actually use it regularly, impact is lower.

**Fix**: Distinguish between "requests heard" and "actual usage if built." Will they really use it or just wanted to complain?

### Mistake 5: No Customer Validation
You prioritize feature based on RICE, then build it, then find out customers don't want it.

**Fix**: For top-3 features, validate with customer research before large development. Small MVP or prototype feedback helps.

---

## RICE Scoring Template

```
Feature: [Feature Name]

REACH (Users affected in next 3 months)
- Source: [Customer interviews? Support tickets? Survey?]
- Estimate: [Number]
- Confidence: High/Medium/Low

IMPACT (How much does each user benefit?)
- 3x Huge: Saves 30+ min/week or critical blocker
- 2x Significant: Saves 10-30 min/week or important problem
- 1x Noticeable: Nice-to-have, saves <10 min/week
- 0.5x Some: Incremental improvement
- Selection: [Pick one]

CONFIDENCE (How sure are you?)
- Evidence: [Customer interviews? Data? Assumptions?]
- Level: 100% / 80% / 50% / 25%

EFFORT (Engineering effort)
- Complexity: [High/Medium/Low]
- Timeline: [1-2 weeks / 1 month / 2-4 months / 4+ months]
- Estimate: [Person-weeks]

RICE SCORE: (Reach × Impact × Confidence) / Effort = [Score]
RANK: [1-20]
```

---

## Value vs. Effort Matrix Template

```
                 Low Effort ← → High Effort
High Value       ◆ DO FIRST     ◆ DO LATER
                 (Quick wins)    (Major investments)

Low Value        ◆ DO IF TIME   ◆ AVOID
                 (Nice-to-have) (Kill list)
```

Plot top 10 features on this matrix. DO FIRST quadrant should be your next sprint.

---

## Stakeholder Alignment Meeting

### Agenda (45 min)
1. **Context** (5 min): Why we're prioritizing (OKRs, strategic focus)
2. **Methodology** (5 min): How we scored (RICE framework, reasoning)
3. **Results** (20 min): Top 15 features, scores, trade-offs
4. **Discussion** (10 min): Any major objections? Missing context?
5. **Decision** (5 min): Confirm priorities, communicate to team

### Handling Objections
**"Feature X should be higher"**
→ "I hear you. Current score is [X]. Can you help me understand: How many users need this? How much does it improve their workflow? What effort would it take?"

**"We need to do everything"**
→ "I understand. We have limited capacity (team size, timeline). If we do everything, we do nothing well. How do we choose?"

**"Customer Y is demanding this"**
→ "What's the reach? How many customers have this need? Is this one customer's unique requirement or a broad pattern?"

---

## Success Metrics

- [ ] You prioritize using consistent framework (RICE or similar), not gut feel
- [ ] Effort estimates are realistic (engineering validates)
- [ ] Stakeholders understand rationale behind priority order
- [ ] Trade-offs are explicit ("We're not doing X to focus on Y")
- [ ] Priorities change monthly, not daily
- [ ] Top features are validated with customer research before large investment
- [ ] Your prioritization correlates with business impact (metrics improve)

---

## Quick Reference: When to Use Each Framework

| Framework | When to Use | Pros | Cons |
|-----------|------------|------|------|
| RICE | Scoring large backlog | Quantitative, defensible, comprehensive | Time-consuming, assumes estimability |
| Value vs. Effort | Quick visual | Simple, intuitive, good for execs | Less precise, binary thinking |
| Kano Model | Understand feature types | Reveals must-haves vs. delighters | Requires customer research to identify types |
| MoSCoW | Simple classification | Fast, easy | Less nuanced about trade-offs |

---

## Next Steps

1. **This week**: Inventory your backlog (30-50 features)
2. **Next week**: Score with RICE, validate effort estimates
3. **Week 3**: Rank, get leadership alignment
4. **Week 4**: Communicate prioritized backlog to team

---

**Remember**: Prioritization is about making explicit trade-offs. Use frameworks to be transparent about your reasoning. When stakeholders understand "why," they accept "no" better.

