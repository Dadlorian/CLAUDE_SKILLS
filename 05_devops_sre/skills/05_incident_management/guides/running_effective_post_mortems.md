# Running Effective Post-Mortems: A Facilitator's Guide

## Purpose

This guide helps facilitators lead productive, blameless post-mortem meetings that result in genuine learning and actionable improvements. Whether you're a first-time facilitator or looking to improve your skills, this guide provides practical techniques and frameworks.

---

## The Facilitator's Role

### What Makes a Good Facilitator

**Key Qualities:**
- **Neutral:** Not directly involved in the incident response (ideally)
- **Skilled in Group Dynamics:** Can manage different personalities
- **Technically Fluent:** Understands concepts without being expert in all domains
- **Committed to Blamelessness:** Models and enforces blameless culture
- **Time Manager:** Keeps discussion on track and on time
- **Active Listener:** Hears what's said and what's not said

**Your Job is NOT:**
- To be the technical expert
- To have all the answers
- To assign blame or praise
- To make all the decisions
- To write the entire post-mortem

**Your Job IS:**
- To guide the conversation
- To ensure all voices are heard
- To keep focus on learning
- To surface action items
- To maintain psychological safety
- To ensure productive use of time

---

## Pre-Meeting Preparation

### 1. Understand the Incident (24-48 hours before)

**Review materials:**
```
☐ Read incident timeline thoroughly
☐ Understand basic technical details
☐ Review monitoring data and graphs
☐ Identify key decision points
☐ Note areas of uncertainty or confusion
☐ Identify potential sensitive topics
```

**Prepare questions:**
- What were the critical moments?
- Where did things go well?
- Where were there delays or confusion?
- What information was missing?
- What assumptions proved incorrect?

**Identify potential challenges:**
- Sensitive interpersonal dynamics
- High-stakes political situations
- Complex technical issues
- Potential for blame or defensiveness

### 2. Prepare the Logistics

**Meeting setup:**
```
☐ Schedule 90-120 minutes
☐ Book appropriate room or video conference
☐ Ensure room has whiteboard or collaborative tools
☐ Test screen sharing and collaboration tools
☐ Prepare collaborative document (Google Docs, Miro, etc.)
☐ Set up timer for agenda items
```

**Invite the right people:**

**Core attendees (required):**
- Incident Commander
- Technical Lead(s)
- Communications Lead
- Scribe
- Subject matter experts who participated

**Additional attendees (as appropriate):**
- Engineering leadership
- Product/project managers
- Stakeholders from affected teams
- Customer support representatives

**Size guidance:**
- **Ideal:** 6-10 active participants
- **Maximum:** 15 active participants
- Additional observers welcome (muted/listen-only)

**Send invites with:**
- Meeting agenda
- Pre-read materials (timeline, graphs)
- Link to collaborative document
- Expectation to review materials beforehand
- Reminder about blameless culture

### 3. Prepare Your Facilitation Materials

**Create meeting agenda document:**

```markdown
# Post-Mortem: [Incident Name/ID]
Date: [Date]
Facilitator: [Your name]

## Attendees
[List]

## Agenda (90 minutes)
1. Welcome & Ground Rules (5 min)
2. Timeline Review (15-20 min)
3. Root Cause Analysis (20-30 min)
4. What Went Well (10 min)
5. What Could Be Improved (15-20 min)
6. Action Items (15-20 min)
7. Lessons Learned & Wrap-up (5-10 min)

## Notes
[Collaborative note-taking space]
```

**Prepare your opening:**
- Have your ground rules ready
- Prepare blameless culture reminder
- Have icebreaker ready (if appropriate for team culture)

---

## Facilitating the Meeting

### Opening: Set the Stage (5 minutes)

**Welcome everyone:**
```
"Thank you all for being here. We're here to learn from
[incident name] and improve our systems and processes.

This is a blameless space. We're focusing on what happened,
not who made mistakes. Everyone acted with the information
they had at the time, under pressure.

Our goals today:
1. Understand what happened and why
2. Identify what we did well and should continue
3. Identify improvements to prevent recurrence
4. Create actionable items with owners

Ground rules:
- Assume good intentions
- Focus on systems, not people
- All ideas are valid in brainstorming
- It's okay to say 'I don't know'
- Confidentiality: this discussion stays in the room
- One conversation at a time
- We'll keep this to 90 minutes

Any questions before we begin?"
```

**Check-in round (optional, for smaller groups):**
- Quick name and role
- One word describing how you feel about the incident
- Builds psychological safety

### Timeline Review (15-20 minutes)

**Purpose:** Establish shared understanding of what happened

**Facilitation approach:**

1. **Display timeline:**
   - Show on screen or whiteboard
   - Make it visible to everyone
   - Include key graphs/metrics

2. **Walk through chronologically:**
   ```
   "Let's walk through what happened from beginning to end.
   [IC name], can you take us through the timeline?"
   ```

3. **Pause at key moments:**
   - "What were you thinking at this point?"
   - "What information did you have available?"
   - "Why did you make that decision?"

4. **Fill in gaps:**
   - "Did anything happen between 2:15 and 2:30?"
   - "What were other teams doing at this time?"

5. **Clarify technical details:**
   - Ask for explanations of jargon
   - Ensure everyone understands
   - Draw diagrams if helpful

**Facilitation techniques:**

✅ **Do:**
- Keep it factual and chronological
- Ask open-ended questions
- Seek to understand, not judge
- Note discrepancies for discussion later
- Keep pace moving (don't get stuck)

❌ **Don't:**
- Let people jump ahead to solutions
- Allow blame language
- Get lost in technical minutiae
- Skip over important moments
- Let one person dominate

**Watch for:**
- **Disagreement about facts:** Note for discussion
- **Missing information:** Identify gaps to fill later
- **Decision points:** Mark for deeper analysis
- **Emotions:** Acknowledge and validate

**Example facilitation:**
```
"Charlie mentioned error rates spiked at 2:23.
Alice, as IC, when did you become aware?"

"Bob, you mentioned you weren't sure whether to roll back.
Can you walk us through your thinking at that moment?"

"It sounds like there's some uncertainty about whether
the deployment caused this. Let's note that for the
root cause discussion."
```

### Root Cause Analysis (20-30 minutes)

**Purpose:** Understand why the incident happened (multiple contributing factors)

**Facilitation approach:**

1. **Transition from timeline:**
   ```
   "Now that we understand what happened, let's explore why.
   Remember, there's rarely a single root cause. We're looking
   for all the contributing factors."
   ```

2. **Start with initial hypotheses:**
   - "What did we think was happening during the incident?"
   - "Which hypotheses were correct? Incorrect?"
   - "What misled us?"

3. **Use 5 Whys technique:**
   ```
   Problem: Service went down
   "Why did the service go down?"
   → Database ran out of connections
   "Why did it run out of connections?"
   → Connection pool was exhausted
   "Why was the connection pool exhausted?"
   → Application wasn't closing connections
   "Why wasn't it closing connections?"
   → Recent code change introduced leak
   "Why didn't we catch this before production?"
   → Code review missed it, tests didn't cover it
   ```

4. **Identify contributing factors:**

   **Ask about each category:**

   **Technical factors:**
   - System design issues
   - Missing safeguards
   - Technical debt
   - Monitoring gaps
   - Scaling limits

   **Process factors:**
   - Change management
   - Code review
   - Testing gaps
   - Deployment process
   - Incident response procedure

   **Human factors:**
   - Knowledge gaps
   - Communication issues
   - Cognitive load during incident
   - Missing documentation
   - Training needs

5. **Use collaborative visualization:**
   - Draw fishbone diagram
   - Create mind map of causes
   - Use virtual whiteboard

**Facilitation techniques:**

✅ **Do:**
- Pursue multiple lines of inquiry
- Ask "what else contributed?"
- Challenge "human error" as root cause
- Dig deeper than surface causes
- Validate insights from all team members

❌ **Don't:**
- Accept "they made a mistake" as root cause
- Stop at first cause identified
- Dismiss ideas too quickly
- Let technical experts dominate
- Skip over organizational/process factors

**Watch for blame language:**

**Blameful → Blameless:**
- "You deployed without testing" → "Deployment lacked adequate testing"
- "They should have known" → "Information wasn't readily available"
- "Why didn't you check?" → "What prevented checking this?"
- "That was a stupid mistake" → "What system allowed this to happen?"

**Intervention examples:**
```
❌ Participant: "Charlie should have checked the error rate
   before deploying."
✅ Facilitator: "Let's reframe that. What monitoring or
   process could have surfaced error rates before deployment?"

❌ Participant: "This happened because someone messed up."
✅ Facilitator: "Let's look at the system. What could have
   prevented this mistake from reaching production?"
```

**Capture all contributing factors:**
- Write them down visibly
- Don't judge or dismiss
- Look for patterns
- Note which are systemic vs. one-off

### What Went Well (10 minutes)

**Purpose:** Identify and reinforce positive patterns

**Facilitation approach:**

1. **Frame positively:**
   ```
   "Even in challenging incidents, we usually do some things well.
   What worked effectively during this incident? What should
   we make sure to keep doing?"
   ```

2. **Prompt specific areas:**
   - "How did communication work?"
   - "What made the investigation effective?"
   - "Did any tools or processes help?"
   - "What made mitigation successful?"
   - "What went smoothly that we should replicate?"

3. **Encourage specific examples:**
   ```
   Not just: "Communication was good"
   But: "The dedicated Slack channel kept everyone informed"

   Not just: "Runbook helped"
   But: "Runbook's step-by-step rollback procedure was clear and accurate"
   ```

4. **Recognize contributions (without creating heroes):**
   ```
   "The team worked well together to isolate the issue quickly."
   "Cross-team collaboration between platform and application teams was effective."
   ```

**Why this matters:**
- Builds morale
- Identifies practices to preserve
- Balances negative focus
- Reinforces good behaviors

**Capture everything mentioned:**
- Write down all "went well" items
- These inform process documentation
- Some may become action items ("do more of this")

### What Could Be Improved (15-20 minutes)

**Purpose:** Identify improvement opportunities

**Facilitation approach:**

1. **Brainstorm improvements:**
   ```
   "Now let's think about what we could improve. This is
   brainstorming - all ideas are valid. We'll prioritize later.

   What could have helped us detect, respond to, or prevent
   this incident more effectively?"
   ```

2. **Prompt different areas:**

   **Detection:**
   - "How could we have detected this sooner?"
   - "What monitoring or alerting would have helped?"

   **Response:**
   - "What would have sped up investigation?"
   - "What information was missing?"
   - "What tools or access did we need?"

   **Prevention:**
   - "How could we prevent this from happening again?"
   - "What architectural changes would help?"
   - "What process changes would help?"

   **Recovery:**
   - "What would have made mitigation faster or safer?"
   - "What automation would have helped?"

3. **Encourage wild ideas:**
   - "What if cost wasn't a factor?"
   - "What would the ideal system look like?"
   - "What moonshot solution could we imagine?"
   - (Then bring back to realistic)

4. **Use "How might we..." framing:**
   ```
   Instead of: "Monitoring was inadequate"
   Try: "How might we improve our monitoring to detect this earlier?"

   Instead of: "Runbook was outdated"
   Try: "How might we keep runbooks up to date?"
   ```

**Facilitation techniques:**

✅ **Do:**
- Capture all ideas without judgment
- Draw out quiet participants
- Build on ideas from others
- Look for quick wins and long-term improvements
- Consider different types of solutions (technical, process, cultural)

❌ **Don't:**
- Shoot down ideas immediately
- Let cost/feasibility limit brainstorming
- Allow dominant voices to override others
- Focus only on technical solutions
- Forget about people and process improvements

**Organize improvement ideas:**

Create categories as you go:
- **Quick wins** (< 1 week effort)
- **Short-term** (1-4 weeks)
- **Long-term** (> 1 month)
- **Monitoring & Alerting**
- **Process & Documentation**
- **Architecture & Infrastructure**
- **Training & Knowledge**

### Action Items (15-20 minutes)

**Purpose:** Convert ideas into concrete, actionable next steps

**Facilitation approach:**

1. **Transition from brainstorming:**
   ```
   "We've identified many improvements. Now let's turn these
   into specific action items. We want items that are:
   - Specific and actionable
   - Have clear owners
   - Have realistic deadlines
   - Are things we'll actually complete"
   ```

2. **Prioritize improvements:**

   **Priority framework:**
   - **Critical:** Prevents recurrence of SEV-1 issue
   - **High:** Significantly improves detection/response
   - **Medium:** Incremental improvement
   - **Low:** Nice to have

   **Quick decision:**
   - Dot voting (everyone gets 3-5 votes)
   - Fist-to-five (5 fingers = highest priority)
   - IC/Tech Lead recommendation

   Focus on top 5-10 priorities

3. **Convert to action items:**

   **Bad action item:**
   "Improve monitoring"

   **Good action item:**
   "Add alerting for database connection pool utilization > 80%"
   - Owner: @alice
   - Deadline: 2025-12-01
   - Priority: High

   **Template for each action item:**
   ```
   Action: [Specific, concrete action]
   Owner: [Single person responsible - not a team]
   Deadline: [Specific date]
   Priority: [Critical/High/Medium/Low]
   Success criteria: [How we know it's done]
   ```

4. **Assign owners:**
   - Ask for volunteers first
   - Assign based on expertise if needed
   - Ensure owner is present and agrees
   - One owner per action item (not a team)
   - Owner can delegate but remains accountable

5. **Set realistic deadlines:**
   - Based on effort and priority
   - Consider owner's other commitments
   - Quick wins: 1-2 weeks
   - Larger items: 4-6 weeks max
   - Longer projects: create milestone action item

6. **Limit action item count:**
   - **Ideal:** 5-7 action items
   - **Maximum:** 10 action items
   - More than 10 → probably won't complete
   - Better to complete fewer than leave many undone

**Facilitation techniques:**

✅ **Do:**
- Be specific and concrete
- Ensure single owner for each
- Set realistic deadlines
- Write action items in shared document
- Confirm owner agreement
- Prioritize ruthlessly

❌ **Don't:**
- Create vague action items
- Assign to teams (assign to individuals)
- Set unrealistic deadlines
- Accept too many action items
- Leave items unassigned
- Skip the hard prioritization

**Action item review:**
```
"Let's review our action items:
[Read each action item aloud]

Do these capture our priorities?
Are owners clear and agreed?
Are deadlines realistic?
Is there anything critical we're missing?"
```

### Lessons Learned & Wrap-up (5-10 minutes)

**Purpose:** Synthesize key takeaways

**Facilitation approach:**

1. **Summarize key insights:**
   ```
   "Before we close, let's capture our key lessons:

   What are the 2-3 most important things we learned?
   What should the broader organization know about this?
   What surprised us?
   What will we do differently next time?"
   ```

2. **Capture broader lessons:**
   - Patterns that might apply to other systems
   - Process improvements that help beyond this incident
   - Cultural or organizational insights

3. **Acknowledge the team:**
   ```
   "Thank you all for your thoughtful participation and
   for responding to this incident. Your commitment to
   learning and improving makes us stronger."
   ```

4. **Set expectations for next steps:**
   ```
   "Next steps:
   - I'll complete the written post-mortem by [date]
   - Action items will be tracked in [system]
   - We'll review action item progress in [weekly meeting]
   - Written post-mortem will be shared with [audience]

   Questions or final thoughts?"
   ```

5. **Optional: Plus/Delta on meeting itself:**
   - What worked well about this post-mortem meeting?
   - What could we improve for next time?
   - Improves facilitation over time

**Close on positive note:**
- Thank everyone for their time and candor
- Acknowledge difficulty of discussing failures
- Emphasize learning and improvement
- Express confidence in the team

---

## Common Facilitation Challenges

### Challenge: Blame Language Emerges

**Scenario:**
```
"This happened because Alex deployed without checking."
```

**Intervention options:**

**Option 1: Gentle redirect**
```
"Let's reframe that - what in our deployment process could
have caught this before production?"
```

**Option 2: Reinforce blamelessness**
```
"Remember, we're focusing on systems, not individuals.
Alex made a decision with the information available at
the time. What could have provided better information?"
```

**Option 3: Private follow-up**
```
[After meeting, privately to blameful person]:
"I noticed some blame language in the post-mortem. I know
you didn't mean it that way, but it can discourage honesty.
Could we work together on more blameless framing?"
```

### Challenge: One Person Dominates

**Scenario:** Senior engineer or manager talking 90% of the time

**Intervention options:**

**Option 1: Redirect to others**
```
"Thanks, Jordan. Let's hear from others.
Sam, you were responding during this time - what was your experience?"
```

**Option 2: Use round-robin**
```
"Let's go around the table and hear from everyone on this question."
```

**Option 3: Private conversation**
```
[Break or after meeting]:
"Jordan, I really value your insights. I'm also trying to
draw out perspectives from the whole team. Can you help me
by giving others space to speak?"
```

**Option 4: Set explicit norm**
```
"I'd like to use the raise hand feature so we hear from
everyone. I'll call on people in order."
```

### Challenge: Group Goes Silent

**Scenario:** Awkward silence, no one responding to questions

**Responses:**

**Option 1: Rephrase question**
```
"Let me ask that differently - during the investigation,
what was most helpful? What slowed you down?"
```

**Option 2: Direct questions**
```
"Alex, you mentioned difficulty accessing logs.
Can you tell us more about that?"
```

**Option 3: Share observation**
```
"I notice we've gotten quiet. That's okay - this can be
uncomfortable. Let me share what I observed and you can
react to that..."
```

**Option 4: Use think-pair-share**
```
"Let's take 2 minutes to think individually about what
could be improved, then discuss with the person next to you,
then we'll share with the group."
```

**Option 5: Prompt with options**
```
"Would improved monitoring have helped? Better documentation?
Clearer escalation paths? Different architecture?"
```

### Challenge: Too Much Technical Detail

**Scenario:** Discussion goes deep into technical weeds, losing others

**Intervention:**

**Option 1: Parking lot**
```
"This is important technical detail. Let's capture it for
the written post-mortem, but keep this discussion at a level
everyone can follow. The key point is [summary]?"
```

**Option 2: Request summary**
```
"For those of us less familiar with this system, can you
summarize the key point in one sentence?"
```

**Option 3: Redirect**
```
"Let's move up a level - what does this mean for our
incident response process?"
```

### Challenge: Sensitive Personnel Issues

**Scenario:** Junior engineer made a mistake that caused a SEV-1

**Approach:**

**During meeting:**
- Extra vigilance on blameless language
- Focus relentlessly on systems
- Acknowledge difficulty and learning
- Don't single out the individual

```
"This was a complex situation and easy mistake to make.
What could have prevented this? What safeguards could we add?"
```

**After meeting:**
- Private conversation with affected individual
- Check on their emotional state
- Reinforce learning, not blame
- Involve manager if appropriate

**In written post-mortem:**
- Avoid naming individuals if possible
- Focus on system failures
- Emphasize improvements

### Challenge: Disagreement About Root Cause

**Scenario:** Team has conflicting theories about what caused the incident

**Approach:**

**Option 1: Acknowledge multiple causes**
```
"It sounds like there were multiple contributing factors.
Let's capture all of them rather than trying to identify
a single root cause."
```

**Option 2: Park the debate**
```
"There's clearly some uncertainty here. Let's note that
further investigation is needed and create an action item
to resolve this question."
```

**Option 3: Focus on prevention**
```
"Even if we're not certain about the exact cause, we can
identify improvements that would help regardless. What would
prevent or detect either scenario?"
```

### Challenge: Running Out of Time

**Scenario:** 20 minutes left and you haven't gotten to action items

**Responses:**

**Option 1: Prioritize action items**
```
"We're running short on time. Action items are critical,
so let's move there now. I'll capture remaining discussion
points for the written post-mortem."
```

**Option 2: Extend meeting**
```
"We need more time to finish effectively. Can everyone stay
an additional 30 minutes? [Check with group] If not, let's
get action items now and schedule follow-up."
```

**Option 3: Async follow-up**
```
"We've had a great discussion. I'll draft action items based
on what we've covered and circulate for feedback rather than
rush through them now."
```

**Prevention:** Watch time carefully, intervene earlier

---

## After the Meeting

### Complete the Written Post-Mortem

**Timeline:**
- Draft within 2-3 days
- Incorporate feedback
- Publish within 1 week

**See:** templates/post_mortem_template.md

**Include:**
- Complete timeline
- All contributing factors identified
- What went well
- Improvement areas
- Action items with owners and deadlines
- Lessons learned

### Create and Track Action Items

**Next steps:**
```
☐ Create ticket for each action item in tracking system
☐ Assign to owners
☐ Set due dates
☐ Tag with post-mortem ID
☐ Link to post-mortem document
☐ Add to weekly team review
```

### Share and Socialize

**Distribution:**
- Email to engineering org
- Post in wiki/knowledge base
- Discuss in team meetings
- Include in onboarding

**Broader sharing:**
- Engineering all-hands presentation
- Public blog post (if appropriate)
- Conference talk (if valuable to community)

### Follow Up on Action Items

**Ongoing:**
- Review action items in weekly meetings
- Check in with owners
- Unblock when needed
- Celebrate completions

**Monthly review:**
- Action item completion rate
- Overdue items and why
- Lessons from implementation

---

## Continuous Improvement

### Reflect on Your Facilitation

**After each post-mortem:**
```
☐ What went well in the meeting?
☐ What could I improve as facilitator?
☐ Were there moments I missed?
☐ Did everyone participate?
☐ Was the meeting productive?
☐ Did we achieve our goals?
```

### Get Feedback

**Ask participants:**
- One thing that worked well?
- One thing to improve?
- Did you feel safe being honest?
- Were action items clear and actionable?

**Anonymous survey (optional):**
- Rate effectiveness of post-mortem
- Suggestions for improvement
- Feedback on facilitation

### Develop Your Skills

**Training:**
- Facilitation workshops
- Blameless culture training
- Root cause analysis techniques
- Group dynamics and conflict resolution

**Practice:**
- Shadow experienced facilitators
- Start with lower-severity incidents
- Debrief with mentor after meetings
- Participate as non-facilitator to observe

**Resources:**
- Google SRE Book
- "Crucial Conversations"
- "Facilitator's Guide to Participatory Decision-Making"
- Etsy's Debriefing Facilitation Guide

---

## Facilitator's Checklist

### Before Meeting
```
☐ Review incident timeline and materials
☐ Prepare agenda and collaborative document
☐ Invite right participants
☐ Send pre-read materials
☐ Set up meeting logistics
☐ Prepare opening remarks
☐ Identify potential sensitive topics
```

### During Meeting
```
☐ Set blameless tone
☐ Guide through timeline
☐ Facilitate root cause analysis
☐ Capture what went well
☐ Brainstorm improvements
☐ Create action items with owners/deadlines
☐ Summarize lessons learned
☐ Thank participants
```

### After Meeting
```
☐ Complete written post-mortem
☐ Create action item tickets
☐ Share post-mortem broadly
☐ Track action items
☐ Reflect on facilitation
☐ Get feedback
```

---

## Key Takeaways

**For Effective Post-Mortems:**

1. **Blameless Culture is Non-Negotiable**
   - Model it, enforce it, protect it

2. **Preparation Matters**
   - Know the incident, prepare the agenda, invite right people

3. **Facilitation is Active**
   - Guide discussion, manage time, ensure participation

4. **Multiple Root Causes are Normal**
   - Look for contributing factors, not single cause

5. **Action Items Must Be Actionable**
   - Specific, owned, with deadlines, limited in number

6. **Follow-Through is Everything**
   - Track completion, unblock, celebrate success

7. **Learning is the Goal**
   - Not blame, not appearances, not checking boxes

**You'll Get Better:**
- Every post-mortem is practice
- Learn from each one
- Build your skills over time
- Ask for feedback and coaching

---

**Last Updated:** November 2025
**Questions or Feedback:** [Your internal contact]
**Additional Resources:** reference/post_mortem_process.md
