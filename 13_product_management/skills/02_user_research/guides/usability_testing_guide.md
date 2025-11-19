# Usability Testing Guide: Step-by-Step

A practical guide to running user testing sessions that identify real usability problems before launch.

Based on Nielsen Norman Group's usability research methodology.

---

## What Usability Testing Is (And Isn't)

### Usability Testing Is:
- Observing real users attempting to accomplish specific tasks
- Identifying where the interface creates friction
- Understanding why users struggle
- Validating that a design is intuitive
- De-risking major design changes before development

### Usability Testing Is NOT:
- Validating whether users want a feature (use interviews for that)
- Gathering statistics about popularity (use surveys for that)
- A focus group or preference testing
- An opportunity to pitch or educate
- A way to get feature requests

---

## The Nielsen Norman Principle: Test with 5 Users

### Why 5?

Research shows:
- **Users 1-2**: Reveal obvious usability issues
- **User 3-4**: Confirm patterns; reveal additional issues
- **User 5**: Mostly duplicate findings
- **Users 6-10**: Diminishing returns

**The math**: 5 users will uncover ~85% of usability issues. Additional users mostly confirm what you already know.

**Cost-benefit**: 5 users is efficient; 15 users is wasteful.

### When You Might Need More

- Testing 2-3 different user segments (5 per segment)
- Unmoderated testing at scale (30+ users for statistical confidence)
- High-risk products (healthcare, finance)

---

## Pre-Testing: Setting Up for Success

### 1. Define Your Testing Goals

**Write down**: "What usability questions do we need answered?"

**Bad goal**: "See how people react to our app"
**Good goal**: "Can new users complete account setup without help? Do they find key features in first 5 minutes?"

**Good goals include**:
- Specific tasks
- Success criteria
- Which segments matter most

### 2. Select Participants (5 Users)

**Best source**: People matching your target user

**Who to recruit**:
- Existing users (if testing iteration)
- People in target role/industry
- Mix of experience levels (new + experienced if relevant)

**Who to avoid**:
- Employees, friends, colleagues
- UI designers (they think like designers, not users)
- Your power users only (not representative)
- Professional research participants (professional testers behave differently)

**How to recruit**:

**Option A: Reach existing users** (best)
```
Email: "We're testing our product with real users. Can you spend
60 minutes this week helping us get feedback? Totally low pressure—
just trying to understand how people use it."
```

**Option B: LinkedIn/Slack communities**
- Find relevant communities
- Post: "Looking for [user type] to test our product (30-60 min)"
- Screen: Ask about their role, use case

**Option C: Research platforms**
- UserTesting.com (managed, higher cost, faster)
- Respondent.io (expert recruitment)
- TrueLancer
- Cost: $50-200 per user

### 3. Create Testing Tasks

**Task design is critical**. Poor tasks = wasted sessions.

**The task structure**:
1. Describe the goal (not the steps)
2. Provide realistic context
3. Be specific enough to measure success

**Bad task**: "Explore the app and tell me what you think"
**Good task**: "You want to track your team's weekly meetings. Create a new meeting that's 1 hour every Monday at 10am with 5 team members."

**Good task examples**:

Example 1 (Onboarding):
```
You just signed up for [product]. Go ahead and set up your first [account/profile/project]—
whatever you need to do to start using it. I'll be here if you get completely stuck,
but try to figure it out on your own.
```

Example 2 (Feature discovery):
```
Let's say your manager asked you to get a report on [specific metric].
Using the dashboard, find that information and show me.
```

Example 3 (Specific workflow):
```
You need to [realistic task]. Go ahead and do that now.
```

**Critical**: Don't say "click on X" or guide them through steps. Let them figure it out.

### 4. Set Up the Testing Environment

**Quiet, comfortable space**:
- No distractions for participant or you
- Comfortable chair
- Screen large enough to see clearly
- Quiet enough to hear them think aloud

**Equipment**:
- Screen recording: Zoom, OBS, or Monosnap
- Audio recording: Built into video
- Participant camera on (see their face/reactions)
- Permission to record (verbal + written if using external participants)

**Test environment**:
- Use realistic scenario (their computer if possible, or similar setup)
- Real data if possible (not demo data or lorem ipsum)
- Realistic network speed (not super fast; test real conditions)

### 5. Create Backup Plan

**If participant is remote**:
- Test your screen sharing setup beforehand
- Have backup video platform (Zoom + Google Meet)
- Have backup participant recruited (someone doesn't show)

**If testing interruptions**:
- Have a second quick task ready
- Have screenshare working if they need visual walkthrough

---

## The Testing Session: Step-by-Step

### Pre-Test: Welcome & Rapport (5 minutes)

**Script** (adapt to your style):
```
"Thanks for taking time to help us today. I'm going to ask you to try
something on our product, and I'm watching to learn, not to judge. There
are no wrong answers.

Here's what's important to understand: we're testing the product, not YOU.
If something is confusing, that's helpful information for us. If you can't
figure something out, it doesn't mean you're not smart—it means we can improve.

You can think out loud as you go. If you get completely stuck, I can help,
but I'm going to try to let you figure it out first.

Questions before we start?"
```

**Why this matters**:
- Reduces anxiety (they might think it's a test of their ability)
- Sets expectation you want honesty, not politeness
- Encourages thinking aloud

### Background Questions (3-5 minutes)

Quick context questions relevant to your testing:

**Standard questions**:
- "What's your role?"
- "How long have you been [doing this job/in this role]?"
- "How familiar are you with [product category]?"
- "What product do you currently use for [this job]?"

**Your goal**: Understand their context, not make them defensive. Keep it light.

### Introduce the Task (1-2 minutes)

**Read or display the task clearly**:
"Here's what I'd like you to do: [read task exactly as written]. Go ahead when you're ready."

**Don't repeat or clarify** unless they ask. If they ask, repeat exactly as written (don't over-explain).

### Observation (3-10 minutes per task)

**Your job**: Watch and take notes. Don't help unless they're completely stuck.

**What to watch for**:

| What I See | What It Means | Note This |
|---|---|---|
| Immediate action without hesitation | Intuitive; matched their mental model | ✓ |
| Pause before clicking | Uncertainty; not obvious | ✓ |
| Try one thing, then backtrack | Wrong assumption about how it works | ✓ |
| Verbal frustration ("Where is this?") | Confusion; can't find element | ✓ |
| Long time on one screen | Task is complex or unclear | ✓ |
| Successful completion | Design is working | Note time |
| Unsuccessful completion | Design failure | ✓ Very important |
| Sigh or facial expression | Emotion tells you importance | ✓ |

**Your note-taking**:
```
TASK: Find the settings button
- 0:00 Looks at top navigation
- 0:05 Pauses, scans menu bar
- 0:10 Clicks three-dot menu (success)
- Observation: Not immediately obvious; needed to find menu icon
```

**When to help**:

Don't help until they:
1. Ask for help ("Where do I find...?")
2. Are stuck for 30+ seconds on same thing
3. Give up ("I don't think this is working")

When you help, help minimally:
- Don't tell them the answer
- Ask questions: "What are you trying to do?" or "Where would you normally look for that?"
- Let them continue trying

### Follow-Up Questions (2-3 minutes per task)

After each task, ask:

**What they expected**:
- "What were you looking for when you paused?"
- "Why did you try that?"
- "What did you expect to see?"

**Why they struggled** (if they did):
- "What made that hard?"
- "What would you have expected instead?"

**Emotional reaction** (if you noticed frustration):
- "I noticed you seemed frustrated there—what was going on?"
- "That took longer than expected—why do you think?"

**Don't**: "That was confusing, right?" (leading question)

**Do**: "What was your impression of that?" (open-ended)

### Task 2 & 3 (If Testing Multiple Tasks)

Repeat task → observation → follow-up for each task (if testing 3-4 tasks).

**Keep sessions to 45 min max**: People's attention drops after 45 minutes.

### Closing Questions (5 minutes)

After all tasks:

**Overall impressions**:
- "What's your overall impression of [product]?"
- "What surprised you?"
- "What worked well?"
- "What was confusing?"

**Wrap-up**:
- "Is there anything else you'd want to tell me?"
- "Thank you so much for your time."
- Process incentive if promised

---

## Synthesis: What to Look For

### Critical Failures (Major Problems)

**Definition**: User fails task or gets completely stuck

Example problems:
- Can't find key feature
- Doesn't understand navigation
- Feature works opposite of expectation
- Error message is unclear

**Action**: Redesign required before launch

### Struggles (Medium Problems)

**Definition**: User completes task but with confusion, multiple attempts, or longer than expected

Example problems:
- Takes 2 minutes instead of 30 seconds
- Tries 3 things before finding right one
- Frustrated but eventually succeeds

**Action**: Improvement helpful but not critical

### Hesitations (Minor Issues)

**Definition**: User pauses before acting correctly

Example problems:
- Not immediately obvious where button is
- Hesitates before clicking save
- Pauses before finding next step

**Action**: Polish helpful but works

### Patterns vs. One-Offs

**Real problem**: 3+ of 5 users struggled with X

Example:
- 4 users couldn't find export button = real problem
- 1 user couldn't find it = might be their edge case

**Only count it if 2+ users had it** (or 1 user completely failed a critical task)

---

## Analysis: Turning Sessions into Insights

### Watch the Videos

After running 5 sessions:
- Re-watch each video (15-20 min per video)
- Pause to note moments of struggle
- Note successful patterns
- Collect quotes for later

### Extract Problem List

Create simple list:
```
USABILITY ISSUES FOUND:

1. Users couldn't find export button
   - Affected: 4 of 5 users
   - Severity: Critical (user failed task)
   - Where: Located in Settings > Advanced; users expected main menu
   - Fix opportunity: Move to main toolbar or add onboarding tip

2. Confusion about what "projects" means
   - Affected: 2 of 5 users
   - Severity: Medium (recovered quickly)
   - Where: During setup
   - Fix opportunity: Better explanation or rename

3. Checkbox not obviously clickable
   - Affected: 1 of 5 users
   - Severity: Low (easily recovered)
   - Where: Workflow screen
   - Fix opportunity: Visual polish (better affordance)
```

### Identify Successful Patterns

Also note what worked:
```
WHAT WORKED WELL:
- Clean dashboard immediately clear (4/5 understood use case immediately)
- Search functionality intuitive (5/5 found it)
- Help text in modals helpful (3/5 referenced it)
```

### Create Recommendations

For each issue:
1. **Describe the problem** (what did users struggle with?)
2. **Why it matters** (did they fail the task? Or just struggle?)
3. **Recommend fix** (redesign, copy change, feature addition)

---

## Unmoderated Remote Testing (Scaling Up)

### When to Use Unmoderated

- Need sample of 20-50 users
- Testing specific workflows on live product
- Budget is limited
- Geographically distributed users

### How to Set It Up

**Platforms**:
- UserTesting.com (most popular, managed)
- Maze (DIY, integrated with design tools)
- Validately (affordable, DIY)

**Setup**:
1. Write tasks clearly (no chance to clarify)
2. Screen participants (role, experience)
3. Record video + audio (participant does it themselves)
4. Ask follow-up questions after tasks
5. Run 20-30 participants for patterns

**What you get back**:
- Video of user doing task
- Transcription of thinking
- Time on task
- Success/failure rate
- Written feedback

**Cost**: $200-1500 for 20-30 users

### Interpreting Unmoderated Results

Look for:
- **Success rates** (% completing task)
- **Time on task** (how long did it take?)
- **Verbatim feedback** (why did they struggle?)
- **Patterns** (3+ users saying same thing = issue)

**Example interpretation**:
- 70% success rate on checkout = concerning
- 5 of 30 users couldn't find discount code field = major UX issue
- Multiple users saying "confusing" about feature = labeling problem

---

## Prototype Testing: Before You Build

### Testing Mockups vs. Live Product

**Prototype testing**: Test design before building (faster, cheaper)

**Levels of fidelity**:
- **Paper prototype**: Sketches, user points to interactions
- **Wireframe**: Basic layout, low-fidelity digital
- **Mockup**: High-fidelity visual, static (can't click)
- **Interactive prototype**: Functional simulation (Figma, Framer, InVision)

### How to Test Prototypes

**Same methodology**:
- 5 users
- Realistic tasks
- Think aloud
- Observe what works/what doesn't

**Different prompts**:
- "Pretend this is real and you can click on things" (for interactive)
- "Walk me through how you'd use this" (for static mockups)
- "Point to where you'd click" (for paper prototypes)

**What to measure**:
- Do they understand the concept?
- Where do they expect elements to be?
- What's confusing?
- Does it match their mental model?

**Example prototype task**:
```
"Imagine you're trying to share a document with your manager.
Show me how you'd do that in this design."
```

### Rapid Iteration

Prototype testing should be fast:
1. Test prototype (1 week)
2. Identify top 3 issues (1 day)
3. Iterate design (2-3 days)
4. Test iteration with 3-5 users (1 week)
5. Build (now you're confident)

Total: 3-4 weeks to validate design, vs. building and iterating.

---

## Common Mistakes

### Mistake 1: Recruiting the Wrong People

**Problem**: Friends, employees, or power users

**Why it happens**: They're easy to recruit

**Fix**:
- Recruit from user research platforms
- Screen for target role/use case
- Avoid internal users

### Mistake 2: Vague or Leading Tasks

**Problem**: "What do you think?" or "Isn't this better?"

**Fix**:
- Write specific tasks (not open-ended)
- Describe goal, not steps
- Stay neutral; don't ask leading questions

### Mistake 3: Helping Too Much

**Problem**: Explaining how things work or redirecting them

**Why it happens**: Feels rude to watch them struggle

**Fix**:
- Remind yourself: their struggle is valuable data
- Only help if explicitly stuck (30+ seconds)
- Ask guiding questions instead of giving answers

### Mistake 4: Too Few Tasks / Too Many Tasks

**Problem**: Can't identify patterns with 1 task; attention drops after 45 min

**Fix**:
- 3-4 tasks per session (10-15 min per task)
- Keep session to 45 minutes max

### Mistake 5: Premature Attachment to Your Design

**Problem**: Seeing criticism as personal; defending the design instead of learning

**Fix**:
- Remember: you're learning, not being judged
- Assume users are right; the design can be improved
- Thank them for honest feedback

### Mistake 6: Not Documenting Issues

**Problem**: Remember the big picture, miss specific problems

**Fix**:
- Watch videos again; make detailed notes
- Create problem list with severity
- Track which users had which issues

---

## Quick Testing Checklist

**Before Session**:
- [ ] 5 participants recruited (matching your target)
- [ ] 3-4 realistic tasks written (not scripts; goal + context)
- [ ] Environment quiet and comfortable
- [ ] Screenshare tested
- [ ] Recording set up and permission obtained
- [ ] Backup participant in case someone cancels

**During Session**:
- [ ] Explained that you're testing product, not them
- [ ] Brief background context questions
- [ ] One task at a time
- [ ] Watched without helping (unless stuck 30+ seconds)
- [ ] Took notes on struggles
- [ ] Asked follow-up "why" questions

**After Session**:
- [ ] Thanked them
- [ ] Paid incentive if promised
- [ ] Watched video and made detailed notes
- [ ] Marked moments of struggle

**After All 5 Sessions**:
- [ ] Created list of usability issues
- [ ] Counted: how many users had each issue?
- [ ] Prioritized by severity (critical vs. nice-to-have)
- [ ] Recommended fixes
- [ ] Shared findings with team

---

## Tools

**Moderated testing** (you facilitate):
- Zoom, Google Meet (video call)
- Monosnap, OBS (screen recording)
- Paper + pen (notes)

**Unmoderated testing** (participants test alone):
- UserTesting.com (most popular)
- Maze (integrated with Figma)
- Validately (affordable)
- Respondent (good for expert users)

**Prototyping** (for testing before build):
- Figma (wireframes + interactive prototypes)
- Framer (interactive prototypes)
- InVision (prototyping + testing)

---

## Resources

- Nielsen Norman Group: Usability testing articles
- "Don't Make Me Think" by Steve Krug: UX principles
- UserTesting Academy: Free courses on usability testing
- "System Usability Scale" (SUS): Standard scale for rating usability
