# Running an Effective Prioritization Workshop

This guide provides complete instructions for planning and executing a prioritization workshop that drives consensus and builds team alignment.

## Workshop Overview

### Purpose
Move from competing views on feature importance to a single, transparent, data-informed prioritization that the organization commits to execute against.

### Outcomes
- Prioritized feature list for next 6 months
- Shared understanding of decision rationale
- Team alignment on trade-offs
- Clear communication plan for organization
- Buy-in from key stakeholders

### Time Investment
- **Preparation**: 1-2 weeks
- **Workshop**: 2-3 hours
- **Documentation**: 1 week
- **Total**: 3-4 weeks from start to finished roadmap

## Pre-Workshop Phase (1-2 weeks)

### Step 1: Assemble Team (Day 1)

**Core Participants**:
- Product Manager (facilitator)
- Engineering Lead (effort estimation)
- Design Lead (feasibility input)
- Key stakeholder/executive (strategic context)
- Customer Success or Sales (customer voice)
- Analytics person (optional, if available)

**Ideal Size**: 4-6 people (more than 6, break into smaller sessions)

**Logistics**:
- 2-3 hour time block
- Conference room with whiteboard/digital board
- Laptop for note-taking/sharing
- Printer for pre-work materials

### Step 2: Collect Feature Candidates (Days 2-7)

**Sources of Candidates**:
- Product roadmap (existing commitments)
- Customer feedback (support, sales, interviews)
- Analytics (usage patterns, drop-off points)
- Competitive analysis (what are competitors doing)
- Employee suggestions (team ideas)
- Strategic initiatives (OKR-related features)

**Target**: 15-25 features (sweet spot for workshop)
- Too few (< 10): Workshop not valuable
- Too many (> 30): Becomes overwhelming

**Documentation Template**:

```
Feature: [Name]
Description: [1-2 sentence description]
Customer Requests: [Any relevant feedback]
Strategic Alignment: [Which OKRs/goals does this support?]
Competitive Context: [Competitor doing this? How urgent?]
Rough Effort: [Small/Medium/Large] (rough only)
```

### Step 3: Prepare Research Data (Days 3-7)

**Data to Gather** (in priority order):

**1. Customer Understanding**
- Interview notes (5-10 target customers)
- Support ticket themes
- Churn analysis (why are customers leaving?)
- Customer request frequency
- Net Promoter Score (NPS) verbatims

**2. Usage Analytics**
- Feature usage frequency
- Churn by feature absence
- User segment breakdown
- Adoption curves for similar features
- Time-on-task for current workflows

**3. Competitive Intelligence**
- Competitor feature matrix
- Recent competitor launches
- Differentiation opportunities
- Market trends

**4. Business Context**
- Revenue impact by customer segment
- Retention impact by feature
- Support cost reduction opportunities
- Upsell/upgrade potential

**5. Technical Feasibility**
- Known blockers or dependencies
- Infrastructure gaps
- Team skills/knowledge gaps
- Historical velocity data

**Presentation Prep**:
- Create 1-2 page summary of context
- 5-10 minute presentation of findings
- Share data with workshop team before session

### Step 4: Create Pre-Work for Participants (Days 8-10)

**Send to team 5-7 days before workshop**:

**Pre-Work Materials**:
1. Context presentation (background, strategic goals)
2. Feature list with descriptions
3. Any supporting data
4. Framework explanation (which prioritization method you'll use)
5. Pre-workshop reflection questions

**Pre-Workshop Reflection Template**:

```
For each major feature area, please reflect:

[Feature Area]:
- What makes this important?
- What concerns do you have?
- What data would help you decide?
- What's your preliminary view on priority?

Please come to workshop ready to discuss and debate.
```

**Email Template**:

```
Subject: [Date] Feature Prioritization Workshop - Pre-Work

Hi team,

We're holding our Q[X] prioritization workshop on [DATE]
from [TIME] to [TIME] to decide our feature focus for the
next 6 months.

I've attached:
1. Strategic context for the workshop
2. Customer research summary
3. List of 20 feature candidates
4. Pre-workshop reflection (please complete)

Please review materials before the session. We'll use this
time to build alignment on our priorities.

The workshop will use RICE scoring (Reach, Impact, Confidence, Effort).
You'll get a tutorial during the meeting, but skimming
[attached RICE overview] ahead of time is helpful.

See you on [DATE]!
[PM name]
```

## Workshop Day (2-3 hours)

### Pre-Workshop Setup (15 min before)

**Logistics**:
- Arrive early to set up
- Have all materials ready (printed or digital)
- Test any technology
- Post agenda visibly
- Arrange seating for collaboration

**Materials Needed**:
- Blank prioritization worksheet template
- List of 20 features
- Data summary sheets
- Notes from pre-work
- Whiteboard/markers
- Laptops for reference
- Calculator (for RICE if needed)

### Workshop Agenda

#### 1. Opening & Context (15 minutes)

**Objective**: Align on why we're doing this and what success looks like

**Activities**:
- Welcome and explain workshop purpose
- Review strategic context (OKRs, market position)
- Explain decision criteria
- Set norms for respectful debate

**Key Messages**:
- "We have more ideas than capacity - need to be strategic"
- "No perfect answer - we're aiming for 'defensible and transparent'"
- "Data informs but doesn't decide - team judgment matters"
- "This is a living roadmap - we'll revisit quarterly"

**Facilitator Tips**:
- Keep this short (people are ready to engage)
- Show confidence in the process
- Acknowledge this may feel uncomfortable (making trade-offs is hard)

#### 2. Framework Tutorial (15 minutes)

**Objective**: Ensure everyone understands the framework being used

**If using RICE**:
- Explain Reach (number of users in timeframe)
- Explain Impact (how significantly affected)
- Explain Confidence (certainty in estimates)
- Explain Effort (person-months)
- Walk through 2-3 examples
- Show how final scores drive ranking

**If using Value vs Effort**:
- Show 2x2 matrix
- Explain value axis (importance)
- Explain effort axis (complexity)
- Show quadrants and decision rules
- Walk through 2-3 examples

**Interactive Element**:
- "Let's practice on [sample feature]"
- Get team to estimate Reach/Impact/Effort
- Calculate together
- Show how their estimates led to the ranking

**Facilitator Tips**:
- Use examples relevant to your product
- Encourage questions
- Normalize that estimates will be rough
- Emphasize this is about relative ranking, not precision

#### 3. Feature-by-Feature Discussion (90-120 minutes)

**Process**:
For each feature:

1. **Context** (2 min)
   - Read feature description
   - Provide key data (customer requests, support issues)
   - Show competitive context if relevant

2. **Discussion** (5-7 min)
   - "What do people think? Is this important? Why?"
   - Encourage debate and questions
   - Surface disagreements
   - Share relevant data/research

3. **Estimation** (3-5 min)
   - "Let's estimate Reach/Impact/Effort"
   - Facilitate discussion
   - Reach consensus estimate
   - Document assumptions

4. **Move to Next** (1 min)
   - Record scores
   - Note any outstanding questions
   - Move on

**Example Discussion Flow**:

```
PM: "Let's talk about Advanced Search. This came up in 3 customer
conversations and we have support tickets about search not finding
specific items."

Engineer: "This would be maybe 4 person-months to do right, accounting
for infrastructure work."

Sales: "Actually, I think more than 3 customers mentioned this -
maybe 5-6 in the last 6 months."

PM: "Good point. So Reach maybe higher than we thought. Let's say
5000 users who search regularly. Impact is probably high - search is
core to the product. Maybe 2x because it improves efficiency but
doesn't solve a critical pain point. Confidence is 80% - we have
good data. Effort is 4 person-months. Let's calculate:
(5000 × 2 × 0.8) / 4 = 2000. That's a pretty strong score."

Designer: "One note - we should consider the redesign we're planning.
This might be easier after that's done."

PM: "Great point. Let's note that as a dependency for sequencing
later."
```

**Managing Discussion**:

**If discussion gets stuck**:
- "Let's park this and come back" (note to revisit)
- Move to next feature
- Return to contentious ones if time allows

**If estimates vary widely**:
- "Why do you estimate higher/lower?"
- Listen to the reasoning
- Adjust if new data emerges
- Use average if continuing to disagree
- Note the disagreement

**If someone dominates**:
- "Thanks for that perspective. Let's hear from [quieter person]"
- "What do you think about that?"
- Balance air time across team

**If someone seems disengaged**:
- "Engineer, we'd value your input on feasibility here"
- "Sales, does this align with what you're hearing?"
- Draw people in

**Tracking Format** (on whiteboard/shared doc):

```
Feature | Reach | Impact | Confidence | Effort | RICE Score | Notes
--------|-------|--------|-----------|--------|-----------|--------
Better  | 5000  | 2x     | 80%       | 4      | 2000      | Dependency:
Search  |       |        |           |        |           | Design work
--------|-------|--------|-----------|--------|-----------|--------
AI      | 2000  | 3x     | 50%       | 8      | 375       | Confidence
Suggest |       |        |           |        |           | low, may
        |       |        |           |        |           | want to pilot
--------|-------|--------|-----------|--------|-----------|--------
```

#### 4. Review & Ranking (20 minutes)

**Objective**: Summarize results and confirm top priorities

**Activities**:
- Sort features by RICE score
- Review top 10 features
- Ask: "Does this ranking feel right?"
- Adjust if needed (often top 3-5 are clear, debate mid-tier)

**Discussion**:
- "Are the top 5 aligned with our strategy?"
- "Does anything surprising stand out?"
- "Do we need to change any estimates?"

**Sequencing**:
- Identify dependencies
- Note any reason to reorder (strategic, team momentum, etc.)
- Confirm first-quarter priorities
- Group second and third quarter items

#### 5. Closing (10 minutes)

**Objectives**: Secure commitment and set next steps

**Activities**:
- Summarize top priorities
- Confirm alignment
- Explain what comes next
- Thank the team

**Key Messages**:
- "Here's our prioritized roadmap for the next 6 months"
- "We'll review and update this quarterly"
- "We'll communicate this to the organization this week"
- "Engineering starts on [top priority] next sprint"

**Commitment Check**:
- "Does everyone feel good about this?"
- Address any remaining concerns
- Confirm team is ready to execute

## Post-Workshop Phase (1 week)

### Step 1: Finalize Documentation

**Create**:
- Final ranked feature list
- RICE scoring worksheet (all features)
- Prioritization assumptions document
- Dependency map
- Timeline/sequencing plan

**Document Format**:
```
Q1 PRIORITIES
1. Feature A (RICE: 2000)
   - Owner: [Name]
   - Effort: 4 person-months
   - Key Success Metric: [Metric]
   - Timeline: Weeks 1-8

Q2 EXPLORE
2. Feature B (RICE: 1500)
3. Feature C (RICE: 900)

Q2-Q3 STRATEGIC
4. Feature D (RICE: 500)

FUTURE CONSIDERATION
5. Feature E (RICE: 75)
```

### Step 2: Create Roadmap for Organization

**External Roadmap** (for customers, stakeholders):
- High-level themes (not detailed features)
- When launching (Q, not specific date)
- Why priorities (business value, customer needs)
- What's not included this cycle (manage expectations)

**Internal Roadmap** (for team):
- Detailed feature list
- Effort estimates
- Dependencies
- Success metrics
- Team assignments

### Step 3: Communicate Results

**Executive Presentation**:
- Prioritization results
- Key decisions and why
- Impact on business metrics
- Timeline and risk mitigation

**Team Communication**:
- Roadmap review (engineering, design, CS)
- Answer questions
- Build excitement for top priorities
- Clarify dependencies

**Customer Communication**:
- Share themes/vision
- Manage expectations for requests
- "We're focusing on [area], this feature is in the future"

**Roadmap Sharing**:
- Public roadmap (if you have one)
- Executive dashboard
- Engineering wiki
- Monthly all-hands update

### Step 4: Establish Cadence

**Quarterly Review** (every 3 months):
- Review actual vs. planned progress
- Incorporate learnings
- Assess new opportunities
- Re-prioritize if needed
- Adjust confidence levels based on reality

**Monthly Check-in** (lightweight):
- Any major context changes?
- Any new competitive threats?
- Any customer feedback requiring immediate attention?
- Minor reprioritization as needed

**Weekly Refinement** (backlog grooming):
- Detailed engineering scoping of next items
- Dependency confirmation
- Resource planning

## Workshop Facilitation Tips

### Creating Psychological Safety

**Do**:
- Encourage questions and debate
- Praise good questions
- Acknowledge uncertainty ("We don't know everything")
- Share reasoning ("Here's why I'm thinking...")
- Admit when you don't know ("Let's find out")

**Don't**:
- Mock anyone's contribution
- Cut off discussion too quickly
- Shut down disagreement
- Act like there's one right answer
- Dismiss concerns

### Managing Strong Opinions

**If someone advocates strongly for a feature**:

1. Listen fully without interrupting
2. Acknowledge validity of their view
3. Ask questions to understand
4. Provide counter-data if you have it
5. Work toward consensus estimate
6. Document their perspective
7. Move forward

**Example Response**:
"I hear you - this is important to [stakeholder]. The data we have shows reach might be lower than expected, but I trust your judgment on the importance. Let's estimate reach at [number] and see where this lands. If it scores in top 20%, we'll make it happen."

### Handling Conflict

**If team strongly disagrees on scoring**:

**Option 1: More Discussion**
- "Why does reach feel different to you?"
- "What data would convince you otherwise?"
- Discuss until consensus

**Option 2: Average the Estimates**
- "We have [low estimate] and [high estimate]"
- "Let's use [midpoint] and move forward"
- Document the disagreement

**Option 3: Note for Later**
- "This feels important but contentious"
- "Let's revisit after we see initial customer response"
- Make it a planned re-evaluation point

**Example**:
Engineer: "This will take 8 person-months, for sure"
PM: "I'm thinking 4-6"
Engineer: "No way, there's infrastructure work"
PM: "Help me understand the infrastructure work"
[Discussion]
PM: "OK, I see the scope better. Let's say 6 person-months"

### Keeping Energy

**2-3 hour workshop is long. Keep energy high**:

- Take 5-minute break mid-way
- Keep discussion moving (don't dwell on single feature)
- Use humor and lightness
- Praise good contributions ("Great insight")
- Vary who's speaking
- Show visible progress (list grows, ranking changes)

### Documenting Decisions

**Assign someone** (not the PM) to track:
- Features discussed
- Final estimates
- Key assumptions
- Disagreements
- Next steps

**Why not PM?**
PM is facilitating, hard to also take detailed notes

**Note Format** (real-time):
```
FEATURE: Dark Mode
DISCUSSION:
- UX says some users request this
- Data shows about 8000 users search in evening hours
- Engineering estimates 4 person-months
- Not core to business but good for retention
ESTIMATES: Reach 8000, Impact 1x, Confidence 100%, Effort 4
RICE: 2000
ASSUMPTION: Assume 100% adoption (everyone who searches at night will use)
NOTES: Could be quicker with third-party library
DECISION: Go with 2000 score, include in Q2
```

## Sample Workshop Agenda (Print This)

```
FEATURE PRIORITIZATION WORKSHOP
Date: [DATE], [TIME]-[TIME]
Location: [LOCATION]

AGENDA:

0:00-0:15 | Opening & Context
- Purpose of workshop
- Strategic goals
- Decision process
- Norms for discussion

0:15-0:30 | Framework Tutorial
- [Framework] explained
- Example calculations
- Scoring practice

0:30-2:00 | Feature Evaluation
- 15-20 features
- Discussion + estimation
- Break at 1:15-1:20

2:00-2:20 | Results Review
- Rankings
- Top 10 features
- Strategic alignment check
- Sequencing

2:20-2:30 | Closing
- Confirmation of priorities
- Next steps
- Thank you

MATERIALS:
- Feature list
- Data summary
- Scoring worksheet
- Whiteboard/markers
- Laptops
```

## Post-Workshop Communication Template

```
Subject: Q[X] Feature Prioritization Complete

Hi everyone,

We completed our feature prioritization workshop yesterday.
Here are our priorities for the next 6 months:

QUARTER 1 FOCUS:
1. Better Search ([reason])
2. Improved Onboarding ([reason])
3. Dark Mode ([reason])

QUARTER 2 PLANNING:
4. Mobile App (early planning)
5. Advanced Analytics (mid-cycle decision)

These priorities reflect:
- Customer feedback (survey, interviews, support tickets)
- Business opportunity (reach and impact)
- Strategic goals (OKR alignment)
- Team capacity (realistic effort estimates)

We deprioritized:
- [Feature X] (lower reach/impact)
- [Feature Y] (strategic misalignment)

We'll review this quarterly and adjust as we learn. We may
also accelerate items if customer feedback or competition warrants.

Engineering starts Q1 work next sprint. Sales/CS, I'll share
how to talk about priorities with customers.

Questions? Let's talk.

[PM name]
```

## Troubleshooting

### Issue: Workshop took too long

**Cause**: Too many features or too much debate

**Prevention**:
- Cap at 20 features (drop clearly lower priority ones)
- Set time limits per feature
- Pre-score contentious items before workshop

### Issue: Team still doesn't agree after workshop

**Cause**: Legitimate disagreement on importance

**Solutions**:
- "Let's try this for a quarter and see"
- "We're doing [higher priority] first, [your feature] next"
- "Let's get customer data on this"
- Schedule follow-up discussion

### Issue: Prioritization immediately becomes wrong

**Cause**: Major market/competitive change, customer urgency

**Response**:
- This is normal, not failure
- Adjust quickly
- Note how estimate was wrong
- Learn for next prioritization
- Document emergency request process

### Issue: Engineering doesn't feel heard

**Cause**: Either over-estimated in workshop or blocked in execution

**Prevention**:
- Involve engineering earlier
- Get detailed estimates
- Reduce dependencies and blockers
- Surface concerns in workshop
- Plan for unblocking

### Issue: Customers upset about deprioritization

**Cause**: Poor communication, unrealistic expectations

**Prevention**:
- Clear communication early
- Explain decision process
- Set expectations in sales process
- Have talking points for conversations

## Tools & Templates

See:
- rice_calculator_template.md (Scoring sheet)
- prioritization_workshop_script.md (Detailed facilitation script)
- prioritization_comparison.md (Framework selection)

