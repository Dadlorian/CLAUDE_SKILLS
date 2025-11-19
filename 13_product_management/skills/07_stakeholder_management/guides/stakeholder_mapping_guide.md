# Stakeholder Mapping Guide

## Quick Start

A stakeholder map identifies and analyzes all individuals and groups who influence or are affected by your product decisions. This guide walks you through creating one.

**Time Required:** 2-4 hours for comprehensive map
**Tools Needed:** Spreadsheet, whiteboard, Miro, or Lucidchart
**Frequency:** Create initially, update monthly, refresh quarterly

---

## Step-by-Step Process

### Phase 1: Identification (30-45 minutes)

#### Step 1a: Brainstorm Stakeholders

Start broad. List everyone who could influence or be affected by your product.

**Trigger Questions:**
- Who makes budget decisions?
- Who has to implement decisions?
- Who is affected by product changes?
- Who influences others in the organization?
- Who could block progress?
- Who do I need to convince?
- Who has customers ears?
- Who has executive's ears?
- Who depends on my success?
- Who could help or hurt my career?

**Format:**
Create a simple list:
```
INTERNAL
- CEO
- CFO
- VP Engineering
- VP Sales
- VP Marketing
- Head of Customer Success
- Engineering Team Lead (Security)
- Engineering Team Lead (Platform)
- Product Manager (AI Features)
- Design Lead
- 3 Key Engineers
...

EXTERNAL
- 3 Key Customers
- Industry Analyst (Gartner)
- Key Partner (Stripe)
...
```

**Pro Tip:**
Don't filter this list yet. Include everyone who comes to mind. You'll prioritize later.

#### Step 1b: Organize by Category

Group stakeholders logically:

```
STAKEHOLDERS BY FUNCTION

EXECUTIVE (4)
- CEO
- CFO
- Chief Product Officer
- Chief Technology Officer

PRODUCT & DESIGN (6)
- VP Product
- Senior Product Manager
- Product Manager (AI)
- Head of Design
- User Research Lead
- Analytics Lead

ENGINEERING (12)
- VP Engineering
- Engineering Manager (Backend)
- Engineering Manager (Frontend)
- Engineering Manager (Security)
- Platform Lead (Infrastructure)
- 7 Individual Contributors (high influence)

SALES & CUSTOMER SUCCESS (8)
- VP Sales
- VP Customer Success
- 2 Account Executives
- 2 Customer Success Managers
- Sales Engineer
- Sales Operations

CUSTOMERS (5)
- Customer A (Fortune 500)
- Customer B (Series B startup)
- 3 Power Users

EXTERNAL (3)
- Industry Analyst
- Key Partner
- Potential Acquirer
```

**Typical Count:**
- Small company: 20-30 stakeholders
- Medium company: 50-80 stakeholders
- Large company: 100+ stakeholders

At this phase, you're just organizing, not prioritizing.

### Phase 2: Mapping (45 minutes)

#### Step 2a: Create Power/Interest Matrix

Place stakeholders on a 2x2 matrix:

```
                    HIGH INTEREST
                         │
HIGH POWER    QUADRANT 1 │ QUADRANT 2
        ┌───────────────────────────────┐
        │ CEO              CFO           │
        │ VP Eng           Board Member  │
        │ Key Customer     Regulator     │
        │ VP Sales                       │
        │                               │
        ├───────────────────────────────┤
        │                               │
LOW POWER │ Team Members    │ Champions  │
        │ 3 Engaged Eng    │ User Group │
        │ Support Team     │ Press      │
        │                               │
        └───────────────────────────────┘
             LOW INTEREST
```

**Scoring Guidance:**

**Power (Vertical Axis):**
- **High:** Can make unilateral decisions, control resources, block progress
- **Medium:** Can influence decisions, provide resources, create friction
- **Low:** Can influence through advocacy, provide feedback, limited direct power

**Interest (Horizontal Axis):**
- **High:** Actively engaged, asks for updates, raises objections, champions
- **Medium:** Periodically engaged, informed but not daily involved
- **Low:** Rarely asks for updates, affected indirectly, background awareness

**Tip:**
Err on the side of overestimating power for senior people and overestimating interest for engaged people. Better to over-invest in stakeholder management than under-invest.

#### Step 2b: Identify Your Quadrant 1 Key Stakeholders

Focus your detailed analysis on Quadrant 1 (high power, high interest):

These are your critical stakeholders requiring:
- Regular sync meetings
- Detailed communication
- Early involvement in decisions
- Risk escalation
- Relationship investment

**Typical Quadrant 1 Count:** 5-15 people (depending on organization size)

### Phase 3: Detailed Analysis (1-2 hours)

For each Quadrant 1 stakeholder, create a stakeholder profile. Use the template from the Stakeholder Analysis Framework reference document.

#### Key Questions to Answer

**Role & Responsibilities:**
- What are they accountable for?
- What metrics do they measure?
- What's success in their role?

**Motivations:**
- What drives them professionally?
- What are their career goals?
- What would constitute a win?
- What keeps them up at night?

**Decision-Making:**
- Are they data-driven or intuition-based?
- How much detail do they need?
- Quick decider or deliberative?
- Do they seek input?

**Communication:**
- How do they prefer to communicate?
- How often do they want updates?
- Email, meetings, or casual chat?
- Big picture or detail-oriented?

**Influence:**
- Who influences them?
- Who do they influence?
- Allies and potential adversaries?

**Position on Your Initiative:**
- Are they champion, supporter, neutral, skeptic, or opponent?
- What are their concerns?
- What would move them?

**Engagement Approach:**
- How often should you touch base?
- What communication style works?
- How should you involve them?

### Phase 4: Documenting (30 minutes)

#### Create a Stakeholder Inventory

Spreadsheet format works well:

```
NAME │ TITLE │ DEPT │ POWER │ INTEREST │ ATTITUDE │ KEY CONCERN │ COMMUNICATION │ ENGAGEMENT PLAN
────────────────────────────────────────────────────────────────────────────────────────────────
John │ CEO   │ Exec │  HIGH │  HIGH    │ Champion │ Revenue growth│Monthly review│ Sponsor, biweekly sync
Mary │ VP Eng│ Eng  │  HIGH │  HIGH    │ Supporter│ Tech debt    │ Weekly design│ Key input on architecture
Sam  │ Sales │ Sales│  MED  │  HIGH    │ Skeptic  │ Feature delay│ Bi-weekly    │ Address concerns, pilot
```

**Columns:**
- Name: Obviously
- Title: Job title
- Department: What function
- Power: High/Medium/Low
- Interest: High/Medium/Low
- Attitude: Champion/Supporter/Neutral/Skeptic/Opponent
- Key Concern: What worries them about your initiative
- Communication: Their preferred channel and frequency
- Engagement Plan: How you'll manage them

#### Create a Visual Map

If helpful, create a visual:

**Option 1: Power/Interest Matrix (Simple)**
```
        HIGH INTEREST
             │
HIGH POWER   │ Manage Closely  │ Keep Satisfied
        ──────┼────────────────┼────────────────
LOW POWER    │ Monitor         │ Keep Informed
        ──────┼────────────────┼────────────────
             LOW INTEREST
```

**Option 2: Influence Network**
```
                CEO
                │
        ┌───────┼───────┐
        │       │       │
       CFO     VPE     VPS
        │       │       │
       F1      E1      S1
```

### Phase 5: Creating Engagement Plans (1 hour)

For each Quadrant 1 stakeholder, create an engagement plan:

```
ENGAGEMENT PLAN

Stakeholder: [Name]
Goal: Secure support and active involvement in [Initiative]
Current Attitude: [Champion/Supporter/Neutral/Skeptic/Opponent]
Target Attitude: [Champion/Supporter/Neutral]
Timeline: [3 months/6 months]

KEY MESSAGES FOR THIS STAKEHOLDER
─────────────────────────────────
1. [How this helps their goals]
2. [How this addresses their concerns]
3. [How this aligns to company strategy]

TOUCH POINTS
──────────────
Week 1-2:
  • Informal coffee to discuss initial thinking
  • Share draft proposal
  • Get early feedback
  • Frequency: 1x

Week 3-4:
  • Share refined proposal based on feedback
  • Present to leadership
  • Formal kick-off meeting
  • Frequency: 1-2x

Week 5-12:
  • Regular sync meetings (weekly or bi-weekly)
  • Early warning on issues
  • Progress updates
  • Frequency: 1-2x per week

ESCALATION POINTS
──────────────────
If they become skeptical:
  • Schedule deeper discussion
  • Understand specific concerns
  • Adjust approach
  • Provide additional data

ADVOCACY OPPORTUNITIES
───────────────────────
How can they help beyond approval?
  • Champion in executive meetings
  • Help address other stakeholders' concerns
  • Provide resources
  • Make introductions
  • Influence peers

SUCCESS METRICS
────────────────
How will you know they're supporting you?
  • They allocate resources
  • They advocate publicly
  • They defend you in meetings
  • They help unblock obstacles
```

---

## Common Mapping Mistakes

### ❌ Mistake 1: Only Including Obvious Stakeholders

**Problem:** Missing influential people who don't have formal authority

**Fix:** Include hidden stakeholders:
- Respected engineers or technical leaders
- Well-connected relationship builders
- Trusted advisors to decision-makers
- Informal leaders in teams

### ❌ Mistake 2: Static Maps

**Problem:** Creating a map once and never updating it

**Fix:** Update maps:
- Monthly: Track attitude changes
- Quarterly: Add/remove stakeholders
- On major events: Organizational changes, personnel changes

### ❌ Mistake 3: Assuming Power/Interest Are Fixed

**Problem:** Stakeholders' power and interest change

**Reality:**
- New priorities shift interest
- Organizational changes shift power
- Success or failure shifts attitude
- Relationships deepen or weaken

### ❌ Mistake 4: Treating All Quadrant 1s the Same

**Problem:** Giving equal attention to all high-power, high-interest stakeholders

**Reality:**
- Some are allies, some are skeptics
- Some need daily updates, others monthly
- Some value data, others value relationships
- Customize your approach

### ❌ Mistake 5: Ignoring Quadrant 2

**Problem:** Neglecting high-power, low-interest stakeholders

**Reality:**
- They can block progress despite low interest
- They need to maintain positive perception
- They may become interested if something changes
- Keep them satisfied but don't over-invest

---

## Stakeholder Mapping Tools

### Spreadsheet (Simple, Free)

**Pros:**
- Easy to create and update
- Good for sharing
- Can add filters and sorting
- Works for 50-100 stakeholders

**Cons:**
- Not visual
- Hard to see relationships
- Difficult to see patterns

**Recommended Fields:**
- Name
- Title
- Department
- Power Level
- Interest Level
- Attitude
- Key Concerns
- Communication Preference
- Engagement Plan
- Update Frequency

### Miro Board (Visual, Collaborative)

**Pros:**
- Visual and interactive
- Good for team brainstorming
- Easy to update
- Can include networks and relationships

**Cons:**
- Requires Miro account
- Harder to maintain structured data
- Not ideal for 100+ stakeholders

### Lucidchart (Professional, Network)

**Pros:**
- Professional appearance
- Good for influence networks
- Works well for 50-100 stakeholders
- Easy to share and present

**Cons:**
- Paid tool
- Less flexible than spreadsheet
- Harder to add details

### GitHub/GitLab (Markdown, Tracked)

**Pros:**
- Version controlled
- Tracked changes
- Integrated with workflows
- Good for teams

**Cons:**
- Less visual
- Requires markdown comfort
- Harder for non-technical stakeholders

---

## Quick Mapping Process (30 Minutes)

If you need a quick map for an upcoming decision:

1. **Brainstorm** (5 min): List key stakeholders
2. **Categorize** (5 min): Put on Power/Interest Matrix
3. **Identify Key People** (5 min): Focus on Quadrant 1
4. **Note Key Concerns** (10 min): What would each care about?
5. **Plan Engagement** (5 min): How will you involve them?

Result: Quick but useful map to guide your stakeholder management.

---

## Stakeholder Mapping for Different Scenarios

### Scenario 1: New Feature Launch

**Key Stakeholders:**
- VP Product (ownership)
- VP Engineering (resources)
- VP Sales (market fit)
- Key Customers (user feedback)
- Customer Success (support implications)

**Quadrant 1 Focus:**
- Executive sponsor
- Engineering technical lead
- Sales leader for target segment
- Key customer champion

### Scenario 2: Organizational Restructuring

**Key Stakeholders:**
- CEO (strategy)
- All VP-level (affected)
- HR (implementation)
- Team members (affected)
- Affected customers (if external impact)

**Quadrant 1 Focus:**
- Your leader
- Each VPs affected
- HR/Organizational development lead

### Scenario 3: Product Pivot

**Key Stakeholders:**
- CEO (strategic decision)
- VP Product (strategy)
- VP Engineering (effort)
- VP Sales (market implications)
- Existing customers (impact)
- Key employees (career implications)

**Quadrant 1 Focus:**
- CEO and board
- VPs affected
- Technical and sales leadership
- Key customer advocates

### Scenario 4: Technology Migration

**Key Stakeholders:**
- CTO/VP Engineering (technical)
- Team leads (implementation)
- VP Operations (impact)
- Security (if relevant)
- Teams dependent on systems

**Quadrant 1 Focus:**
- Technical decision-makers
- Team leads in scope
- Security and compliance
- Customer-impacting teams

---

## Next Steps After Mapping

Once you've created your stakeholder map:

1. **Create Engagement Plans** for Quadrant 1
2. **Schedule Initial Meetings** with key stakeholders
3. **Develop Key Messages** for different audiences
4. **Plan Communication Cadence** (weekly, monthly, etc.)
5. **Identify Potential Allies** for coalition building
6. **Assess Your Credibility** with each stakeholder
7. **Plan Trust-Building Efforts** where needed
8. **Update Quarterly** as situation evolves

---

## Key Takeaways

- **Start broad** when identifying stakeholders
- **Organize systematically** using Power/Interest Matrix
- **Focus on Quadrant 1** for detailed analysis
- **Customize engagement** by stakeholder type
- **Update regularly** as situation evolves
- **Document everything** for consistency and learning
- **Remember** that stakeholder maps are living documents, not one-time exercises
