# Feature Prioritization Workshop - Facilitation Script

Use this detailed script to run your feature prioritization workshop. Adapt as needed for your context.

---

## PRE-WORKSHOP (Do These Things)

### 3 Days Before

**Send Pre-Work Email**:

```
Subject: Feature Prioritization Workshop [DATE] - Please Prepare

Hi team,

We're running our Q[X] feature prioritization workshop to decide our
focus for the next 6 months.

WORKSHOP DETAILS:
Date: [DATE]
Time: [TIME] - [TIME] (2.5 hours)
Location: [LOCATION]
Goal: Prioritize 15 candidate features and commit to Q[X] roadmap

PRE-WORK (Please complete by [DATE]):
1. Read: RICE Framework Overview (attached)
2. Review: 15 candidate features list (attached)
3. Reflect: Which 3 features do you think are highest priority? Why?
4. Come ready to debate and discuss - this is collaborative

See you then!
[Your name]
```

### 1 Day Before

**Prep Materials**:
- [ ] Print 2 copies of feature list
- [ ] Print RICE scoring worksheet (blank)
- [ ] Have whiteboard/markers ready
- [ ] Test any technology
- [ ] Arrange room with good sightlines
- [ ] Have laptops out for reference/note-taking
- [ ] Post agenda on wall

**Send Reminder**:
```
Quick reminder: Feature prioritization workshop tomorrow at [TIME].
See you then! Please bring [laptop/notes/questions].
```

---

## WORKSHOP AGENDA (2.5 HOURS)

### **0:00-0:10 | Welcome & Opening (10 minutes)**

**Objective**: Set tone, explain purpose, build excitement

**YOUR SCRIPT**:

```
"Welcome everyone! Thanks for being here. Today's workshop is all
about deciding what we build next.

Here's the reality: We have more ideas and requests than we have
engineering capacity. That's actually a good problem to have - it
means there's demand. But it also means we need to be strategic about
what we prioritize.

The goal of this workshop is to:
1. Have transparent discussion about what matters most
2. Use a systematic framework to rank features
3. Leave today with a clear roadmap that the whole team believes in
4. Align the organization around our priorities

This is NOT my decision to make alone. I'll facilitate, but the
prioritization reflects what we collectively believe is most important.

A few norms for today:
- Everyone's perspective matters - please share
- It's OK to disagree and debate
- Data is great, intuition is OK too
- We're aiming for 'good enough,' not perfect

Let's get started."
```

**What To Do**:
- Make eye contact, smile, seem confident
- Take a breath before starting
- Welcome people as they arrive
- Check if anyone needs coffee before starting

---

### **0:10-0:25 | Strategic Context (15 minutes)**

**Objective**: Align on "why" - what are we trying to accomplish?

**YOUR SCRIPT**:

```
"Before we rank features, let's align on our strategic goals.
Here's where we are:

OUR GOALS FOR 2024:
1. Double our user base (grow from 10K to 20K)
2. Improve user retention (move from 60% to 70% 12-month retention)
3. Increase revenue per user (move from $100 to $150 annual)

WHAT THIS MEANS FOR PRODUCT:
- Growth: We need features that attract new users and drive adoption
- Retention: We need to reduce churn, improve satisfaction
- Revenue: We need features that justify higher pricing

CURRENT STATE:
- We've surveyed 20 customers
- We've analyzed our usage data
- We've looked at what competitors are doing

KEY FINDINGS:
1. Users are churning because of weak onboarding (60% leave after day 1)
2. Power users want advanced search (not beginners)
3. Mobile usage is growing 30% quarter over quarter
4. Customers mention 'dark mode' frequently (nice to have, not critical)

STRATEGIC IMPLICATIONS:
This tells us we should prioritize:
- First: Retention (fixing onboarding is critical)
- Second: Power user features (if we keep users, they'll upgrade)
- Third: Mobile experience (where usage is growing)
- Fourth: Nice-to-haves (dark mode is good but not critical)

Does anyone have questions on our strategy or what we learned?"
```

**Wait For Questions** (2-3 minutes):
- Answer briefly and directly
- If philosophical debate emerges: "Good question, let's address this
in prioritization discussion"

**What To Do**:
- Show your data (even just 1-2 slides)
- Be confident in your analysis
- Invite disagreement: "Thoughts? Do you agree with these findings?"

---

### **0:25-0:40 | Framework Tutorial (15 minutes)**

**Objective**: Ensure everyone understands RICE before we use it

**YOUR SCRIPT**:

```
"Now, let's go over the framework we'll use: RICE.

RICE stands for:
- Reach (number of users affected)
- Impact (how significantly affected)
- Confidence (how certain we are)
- Effort (how much work required)

FORMULA: RICE = (Reach × Impact × Confidence) / Effort

Let me walk through each component:

[REACH]
Reach is: How many users will this feature affect in the next 6 months?
- We use data from our analytics when possible
- We estimate conservatively (assume not everyone will use it)
- Example: 'Better search' affects 5,000 active users who search 2+
times per week

[IMPACT]
Impact is: How significantly will each user be affected?
- 3x = Solves a critical problem (game changer)
- 2x = Significant improvement (meaningful)
- 1x = Clear improvement (noticeable)
- 0.5x = Small improvement (nice to have)
- 0.25x = Minimal (barely noticeable)

This is multiplicative. So if Reach is 1000 but Impact is 3x,
we're looking at massive impact overall.

[CONFIDENCE]
Confidence is: How sure are we in our estimates?
- 100% = We have lots of data, we're confident
- 80% = Pretty confident, good data
- 50% = Some data, reasonable assumptions
- 25% = Not much data, mostly assumptions

This is important because it accounts for uncertainty.
If we estimate reach but we're not sure, confidence is low.

[EFFORT]
Effort is: How much engineering work? (In person-months)
- 0.5 = Tiny (few days)
- 1 = Small (1-2 weeks)
- 2 = Small-medium (1 month)
- 4 = Medium (2 months)
- 8 = Large (4 months)
- 16+ = Very large (6+ months)

This is effort, not timeline. So 16 person-months means 4 engineers
for 4 months, or 1 engineer for 16 months.

THE CALCULATION:
Let's walk through an example.

EXAMPLE: Dark Mode Feature

Reach: How many users?
- We have night usage data: 8,000 users search between 8 PM-6 AM
- Assume 90% would use dark mode if available = 7,200
- REACH = 7,200

Impact: How significantly?
- Dark mode makes app pleasant for night users
- Doesn't solve critical problem, more convenience
- IMPACT = 1x

Confidence: How sure?
- We have analytics showing night usage: high confidence
- We don't have data on dark mode adoption: medium confidence
- Blended: CONFIDENCE = 100%

Effort: How much work?
- CSS refactoring: 2 weeks
- Testing: 1 week
- EFFORT = 1 person-month

CALCULATION:
(7,200 × 1 × 1.0) / 1 = 7,200

ANOTHER EXAMPLE: AI-Powered Search

Reach: 2,000 users search actively

Impact: If it works, 3x. Uncertain if it will work well.

Confidence: Limited data on AI search quality = 50%

Effort: 3 person-months

CALCULATION:
(2,000 × 3 × 0.5) / 3 = 1,000

COMPARISON:
Dark Mode scores 7,200
AI Search scores 1,000

Why? Dark mode is low effort, wide reach, we're confident.
AI Search is high effort, uncertain impact, risky.

This is what RICE tells us: Dark Mode is a better bet right now.

Questions on the framework?"
```

**Invite Questions** (2-3 minutes):
- "Who has questions on RICE?"
- Explain patiently
- If debate: "Good question, we'll see how it plays out when we
calculate"

**Interactive Element**:

```
"Let's do a practice calculation together as a team. Here's a
feature: 'Export to PDF'

Help me estimate this:

Reach: How many users would use 'Export to PDF'? What's your guess?
[Wait for responses, discuss]

Impact: How significantly would this affect them?
[Wait for responses, discuss]

Confidence: How sure are we?
[Wait for responses, discuss]

Effort: How much work?
[Ask the engineer on team]

[Calculate together]

OK, so that scores around [X]. That's [low/medium/high] priority.

Ready to do this for 15 features?"
```

**What To Do**:
- This section is critical - if people understand RICE, rest goes fast
- Use hand raising to check understanding
- Do one full practice example
- Be encouraging: "You've got this"

---

### **0:40-2:00 | Feature-by-Feature Scoring (80 minutes)**

**Objective**: Score 15-20 features systematically

**YOUR SCRIPT** (for each feature):

```
"Next feature: [FEATURE NAME]

Quick reminder of what this is: [1-sentence description]

Here's what we know about this feature:
- [Customer feedback: Who asked for it?]
- [Supporting data: What data do we have?]
- [Competitive context: Are competitors doing this?]

Now, let's estimate:

REACH: Who's familiar with this? How many users affected?
[Open discussion, 2-3 minutes]

[Summarize]: "So we're thinking ~[X] users in next 6 months?"

IMPACT: If we build this, how significantly would each user be affected?
- Is this solving a critical problem? (3x)
- Significant improvement? (2x)
- Clear improvement? (1x)
- Nice to have? (0.5x or 0.25x)

[Open discussion, 2-3 minutes]

[Engineer], any technical concerns about the effort?

CONFIDENCE: How confident are we in these estimates?
- Do we have good data? (80-100%)
- Or is this mostly educated guessing? (25-50%)

[Brief discussion]

EFFORT: [Engineer name], realistically, how much effort for this feature?
[Engineer responds with estimate]

Any other blockers, dependencies, or concerns?

[Listen for 30 seconds]

OK, let me calculate: ([Reach] × [Impact] × [Confidence]) / [Effort] = [SCORE]

So [FEATURE] scores [SCORE]. [Interpretation: high/medium/low priority]

Let me jot this down... Next feature:"
```

**What To Do During Scoring**:

**Manage Air Time**:
- If one person dominates: "Thanks for that. Let's hear from [quieter person]"
- If you do all talking: "What do others think?"
- Aim for 2-3 voices per feature

**Handle Disagreement**:

If Reach estimates vary widely:
```
"I'm hearing [low estimate] from you and [high estimate] from you.
Walk me through your thinking on each."

[Listen to both]

"OK, I think [middle estimate] is reasonable. Let's use that."
```

**If Effort estimate seems wrong**:
```
"[Engineer], that seems high/low. Walk me through the components."

[Engineer explains]

"Got it. Let's go with [estimate]."
```

**If discussion gets stuck**:
```
"This is a tough one. Let's make our best estimate and move on.
We can revisit if data changes our view."
```

**Keep Momentum**:
- Allocate ~5 minutes per feature
- Keep discussion focused
- Move to next feature when estimate is clear
- Note questions for later

**Document As You Go**:

Have someone (not you) tracking on shared doc:
```
| # | Feature | Reach | Impact | Conf | Effort | Score | Notes |
|----|---------|-------|--------|------|--------|-------|-------|
| 1  | Better Onboarding | 10000 | 1x | 80% | 2 | 4000 | Highest priority |
| 2  | Dark Mode | 7200 | 1x | 100% | 1 | 7200 | Quick win |
```

**Take 5-Minute Break Halfway** (around 1:15):
```
"Let's take a quick 5-minute break. Back here at [TIME]."

[Stretch, bathroom, water]
```

**Watch The Pace**:
- If moving too fast (done in 60 min): Maybe rush discussions
- Slow down, have richer conversation
- If moving too slow (still going at 90 min): Accelerate
- Make quicker decisions on less controversial items

---

### **2:00-2:20 | Review & Ranking (20 minutes)**

**Objective**: Look at final scores and confirm they make sense

**YOUR SCRIPT**:

```
"OK, we've scored all [NUMBER] features. Let's look at the results.

[DISPLAY RANKING ON SCREEN/WHITEBOARD]

RECAP OF TOP 10:
1. [Feature]: 7200 (Quick win - high value, low effort)
2. [Feature]: 4000 (Strategic priority)
3. [Feature]: 3500 (High priority)
...

Looking at this, a few things stand out:

[OBSERVATION 1]: "[Feature X] is really high because [reason]"
[OBSERVATION 2]: "[Feature Y] is lower than I expected, but makes sense
because [reason]"

ALIGNMENT CHECK: Does this ranking feel right to you?
- Are the top 5 aligned with our strategy?
- Is anything surprising?
- Does anything feel wrong?

[Open discussion, 3-5 minutes]

[Address any major concerns]

OK, I think we have our prioritization. Here's what I'm proposing for
Q[X]:

Q1 FOCUS (Start next sprint):
1. [Feature] - Highest priority, start immediately
2. [Feature] - Should start within month

Q2 PLANNING (Plan but don't start yet):
3. [Feature] - Strategic initiative, plan for quarter 2
4. [Feature] - Plan for quarter 2

Q2/Q3 FUTURE (Worth doing, will revisit):
5+ [Features] - Future roadmap

DEPRIORITIZED (Not doing, but understanding why):
- [Feature]: Scored too low relative to other priorities
- [Feature]: Too much effort for impact right now

Questions on this sequence?"

[Address questions]

"Alright, I think we have alignment. Let me note any dependencies or
sequencing issues..."

[Discuss any sequencing/blocking issues]

"Last thing - are we confident in this? Does the team feel good about
this roadmap?"

[Gauge thumbs up, verbal confirmation]
```

**What To Do**:
- Don't over-explain rankings (trust the RICE math)
- Acknowledge if something unexpected happened
- Confirm team feels good about results
- Note any strong disagreements (may want follow-up)

---

### **2:20-2:30 | Closing & Next Steps (10 minutes)**

**Objective**: Secure commitment and set expectations

**YOUR SCRIPT**:

```
"Great work today. Let me recap what we're committing to:

Q1 PRIORITIES:
- [Feature 1]
- [Feature 2]
- [Feature 3]

These are what we're shipping next quarter. Engineering will start on
[Feature 1] next sprint.

WHAT HAPPENS NEXT:

This week:
- I'll document the prioritization and share with everyone
- Sales and CS will get talking points for customer conversations
- I'll update the roadmap

Next week:
- Engineering starts detailed scoping for [Feature 1]
- Design starts on [Feature 2] if not already started
- We'll have roadmap presentation at all-hands

Monthly:
- We'll review progress on [Feature 1], [Feature 2], [Feature 3]
- Any urgent things come up, we'll discuss

Quarterly:
- We'll do this again - revisit prioritization with new data

A few final notes:

One: This roadmap will change. It's not set in stone. But we're not
changing it on a whim. We'll adjust when:
- We learn something major about customer demand
- Competitive threat emerges
- We hit blockers we didn't anticipate

Two: Just because something's not on this roadmap doesn't mean it's
bad. We said yes to [Feature 1] and [Feature 2] which means saying no
to everything else right now.

Three: I might ask you for help on follow-up. Some items need more
customer research before we commit. Others need technical validation.
I'll ask for volunteers.

Questions?"

[Answer final questions]

"Thank you for your time and thoughtful input. I really valued the
discussion today. See you at the [TIME] all-hands where we'll present
the roadmap."
```

**What To Do**:
- Seem confident and energized
- Thank the team sincerely
- Set clear expectations for what's next
- Invite final questions
- End on time

---

## POST-WORKSHOP (Next 3-5 Days)

### Within 24 Hours

**Send Email With Results**:

```
Subject: Q[X] Feature Prioritization Results

Hi team,

Thanks for your thoughtful input in yesterday's prioritization
workshop. Here's our prioritized roadmap for the next 6 months:

Q1 FOCUS (Starting next sprint):
1. [Feature] - [Business impact]
2. [Feature] - [Business impact]

Q2 PLANNING (Plan this quarter, ship next):
3. [Feature] - [Business impact]
4. [Feature] - [Business impact]

Q2/Q3 FUTURE:
5. [Feature] - [Why it's interesting]
6. [Feature] - [Why it's interesting]

DECISION-MAKING APPROACH:

We used RICE scoring - (Reach × Impact × Confidence) / Effort

Top-scoring items automatically prioritized. You can see the full
scoring details attached.

IMPACT ON REQUESTS:

If you're wondering about [Feature X] that didn't make the list:
It scored [low score] because [reason]. We'll revisit in [time].

WHAT'S NEXT:

- Engineering starts on [Feature 1] next Monday
- I'll share detailed customer talking points with sales
- We'll review quarterly and adjust as we learn

Thanks for your professionalism in this process.
[Name]
```

### Within 1 Week

**Create Detailed Documentation**:
- RICE scoring worksheet (all features with notes)
- Updated roadmap (internal + external version)
- Customer talking points
- Timeline and dependencies

**Share With Key Stakeholders**:
- Executive summary for leadership
- Detailed roadmap for engineering/design
- Customer version for sales/CS

---

## Workshop Facilitation Tips

### Managing Different Personalities

**The Dominator** (talks a lot, strong opinions):
- "Thanks for that perspective. [Name], what do you think?"
- Use to drive engagement, but balance with others
- "Your point is noted. Let's hear from the engineering side too."

**The Silent Type** (quiet, doesn't speak up):
- "Designer, I'd value your input on feasibility here"
- "Does that seem right from your perspective?"
- Name them directly to include them

**The Debater** (wants to argue everything):
- Listen fully without interrupting
- "Good point. Let's note this and move forward."
- "If this debate significantly impacts scoring, we'll revisit"

**The Devil's Advocate** (questions everything):
- These people are valuable - they poke holes in thinking
- "What would need to be true for you to feel good about this?"
- Use them to stress-test assumptions

### Handling Conflict

**If two people strongly disagree on feature importance**:

```
"I hear different views here. [Person A], you think this is critical.
[Person B], you think it's lower priority. What data would convince
you each?"

[Listen to both]

"Let me make a decision: We're going with [decision] because [reason].
[Person B], I hear your concern. If we learn [new information], we'll
revisit. Fair?"
```

**If team consensus seems off**:

```
"I'm sensing some disagreement here. Is everyone OK with this ranking?"

[Wait for honesty]

"Let's spend 5 more minutes on this."

[Deeper discussion]

"Alright, I think [ranking] is right. Let's move forward."
```

### Energy Management

**If energy is dropping**:
- Stand up, move around
- "Let's do the next few features faster"
- Pause for break earlier than planned
- Bring up more controversial features (more engaging)

**If discussion is getting heated**:
- "This shows how much you care. Let's make sure we hear everyone."
- Slow it down
- Reframe as collaborative, not competitive

### Time Management

**If you're behind schedule**:
- Skip deep details on less important features
- Use faster estimation for items scoring <500
- "Let's move faster on these lower-priority items"

**If you're ahead of schedule**:
- Spend more time on top features (they matter more)
- Do sensitivity analysis on contentious ones
- Discussion is valuable - let it breathe

---

## What Happens If Things Go Wrong

### Scenario 1: Score Seems Way Off

```
"Wait, [Feature] scored really high, but intuitively that doesn't
feel right. Let me recalculate...

[Recalculate with team]

Oh, I see - we estimated reach at [high number] because [reason].
Is that right? Should we lower it to [lower number]?"

[Discuss and adjust if needed]

"OK, new score is [adjusted score]. That feels better."
```

### Scenario 2: Someone Leaves Midway

```
"I notice [person] left. Let me check in after we're done in case I
missed their perspective."

[After workshop, reach out one-on-one]
```

### Scenario 3: Strong Executive Disagreement

```
If executive attending says: "I don't think [Feature] should be
this low."

Response: "That's important input. What's your thinking? Help me
understand why this should be higher."

[Listen to their reasoning]

"I hear you. Let me think about this and come back to you. Do you
want to make a decision now, or let me reconsider?"

[Take it offline if needed]
```

### Scenario 4: Team Is Clearly Gaming Scores

```
If engineer says: "I'm going to estimate effort at 16 months so we
don't have to do this."

Response: "I appreciate you being direct. Let's be honest about effort.
What's the real estimate? We'll find a way to make priorities work."

[Reset expectations on honesty]
```

---

## Quick Reference: Key Phrases

**Opening**:
- "Thanks for being here. Today we're deciding what we build next."
- "We have more ideas than capacity, so we need to be strategic."

**Keeping Discussion Moving**:
- "That's valuable input. Let's jot that down and move forward."
- "Good question - let's see how it affects the scoring."
- "I hear you. Help me understand that better."

**Closing Debate**:
- "I think we've explored this enough. Let me make a call..."
- "Let's go with [estimate] and revisit if data changes."
- "I'm going to decide [X]. Can you live with that?"

**Handling Disagreement**:
- "You and I see this differently, and that's OK."
- "I respect your view. Here's mine..."
- "Let me make the call here. If I'm wrong, we'll learn and adjust."

**Confirming Alignment**:
- "Does everyone feel good about this?"
- "Can you commit to this roadmap?"
- "Any major concerns before we move forward?"

**Closing**:
- "Great work today. I really appreciated the discussion."
- "Here's what we're committing to..."
- "Let's execute and learn."

---

## One Hour Before Workshop

**Checklist**:
- [ ] Room is set up, chairs arranged
- [ ] Whiteboard/digital board ready
- [ ] Feature list printed and visible
- [ ] RICE calculator ready
- [ ] Note-taker ready
- [ ] Technology tested (projector, screen)
- [ ] Water, coffee available
- [ ] Bathroom breaks planned
- [ ] Agenda posted
- [ ] You feel ready and energized

**Mental Prep**:
- "I'm running this workshop to help us make a good decision."
- "I'm not trying to control outcome, I'm facilitating discussion."
- "If something goes wrong, I'll improvise and keep going."
- "My job is to ensure everyone has voice and we reach alignment."

**Starting**:
- Greet people as they arrive
- Have them sit as they come in
- Start right on time
- Begin with confidence

---

## After Workshop

**Share Results Quickly** (within 24 hours):
- Momentum matters
- Decisions lose credibility if delayed
- Team wants to know outcome

**Execute Visibly**:
- Start on Feature #1 immediately
- Tell people you're working on priorities
- Build credibility by shipping prioritized items

**Track Reality vs. Prediction**:
- What actually took longer?
- What was more impactful than expected?
- Use learnings for next prioritization

**Revisit Regularly**:
- Monthly check-in (light)
- Quarterly deep dive (like this workshop)
- Adjust as circumstances change

---

## Final Note

This workshop works best when:
- You've done prep work (data collection, pre-work)
- You facilitate, not dictate
- You create psychological safety (people can disagree)
- You move forward with confidence
- You execute on what you decided

Good luck! You've got this.

