# Stakeholder Mapping Reference

## Stakeholder Analysis Frameworks

Understanding and mapping your stakeholders is critical for successful roadmap alignment. Different stakeholders have different interests, levels of influence, and communication preferences.

---

## Framework 1: Power/Interest Matrix

The most common stakeholder analysis framework. Maps stakeholders by their **level of influence** (power) and **level of interest** in your product.

### The Grid

```
                HIGH INTEREST
                     ▲
                     │
    MANAGE CLOSELY   │    KEEP SATISFIED
                     │
    ◆ CEO            │    ◆ HR/Finance
    ◆ VP Eng         │    ◆ Legal
    ◆ VP Product     │    ◆ Compliance
    ◆ Key Customers  │    ◆ IT/Infra
                     │
    ─────────────────┼─────────────────► HIGH POWER
                     │
    KEEP INFORMED    │    MONITOR
                     │
    ◆ Support Team   │    ◆ Junior Eng
    ◆ Marketing      │    ◆ Prospective Customers
    ◆ Sales          │    ◆ End Users
    ◆ Customer Succ. │    ◆ Interns
                     │
                  LOW INTEREST
```

### Strategies by Quadrant

#### Manage Closely (High Power + High Interest)
- **Who**: CEO, VP Engineering, VP Product, major customers
- **Strategy**:
  - Regular deep engagement (weekly or bi-weekly)
  - Collaborative decision-making
  - Detailed updates and explanations
  - Their approval is critical
- **Communication**:
  - Executive presentations with data
  - Written strategic documents
  - One-on-one discussions
  - Regular office hours

**Example Communications**:
- CEO: Monthly strategic reviews with metrics impact
- VP Engineering: Weekly technical architecture reviews
- Major Customers: Quarterly business reviews with roadmap preview

#### Keep Satisfied (Low Power + High Interest)
- **Who**: Sales VP (depending on structure), Marketing VP, certain board members
- **Strategy**:
  - Keep them informed regularly
  - Don't overwhelm with details they don't need
  - Address their concerns promptly
  - Make sure they feel heard
- **Communication**:
  - Monthly email updates
  - Quarterly strategic summaries
  - Respond promptly to questions
  - Invite input on specific topics

**Example Communications**:
- Finance: Monthly revenue impact updates
- HR: Quarterly team capacity and hiring needs

#### Keep Informed (High Power + Low Interest)
- **Who**: Compliance officers, IT security, some board members
- **Strategy**:
  - Proactive but not excessive communication
  - Share information relevant to their domain
  - Be prepared if their interest increases
  - Monitor for signs of disengagement that could become problems
- **Communication**:
  - Quarterly emails with relevant updates
  - Project-specific deep dives (when needed)
  - One-pagers on critical decisions

**Example Communications**:
- Security Officer: Quarterly security features and compliance updates
- Board Members: Quarterly board-level updates on strategy

#### Monitor (Low Power + Low Interest)
- **Who**: End users, prospect customers, junior team members
- **Strategy**:
  - Minimal formal communication
  - Monitor for changes in interest/power
  - Be prepared to engage if status changes
  - Share information through existing channels
- **Communication**:
  - Product announcements via in-app/email
  - Blog posts and social media
  - Product documentation updates
  - Community channels

**Example Communications**:
- End Users: Release notes, in-app notifications, blog posts
- Prospective Customers: Public roadmap, webinars, case studies

---

## Framework 2: Detailed Stakeholder Profile

### Template for Each Stakeholder

```markdown
## [Stakeholder Name/Role]

### Basic Information
- **Title/Role**: [e.g., VP Engineering]
- **Department**: [e.g., Engineering]
- **Years in Role**: [e.g., 2 years]
- **Reporting Structure**: [Who do they report to?]

### Stakeholder Characteristics

#### Power & Interest
- **Level of Influence**: [High / Medium / Low]
- **Level of Interest**: [High / Medium / Low]
- **Quadrant**: [Manage Closely / Keep Satisfied / Keep Informed / Monitor]

#### Motivations & Goals
- **Primary Goal**: [What does success look like for them?]
- **Secondary Goals**: [What else do they care about?]
- **Success Metrics**: [How are they evaluated?]

#### Product Involvement
- **How They Use Product**: [Are they a user? How deeply?]
- **Their Concerns**: [What keeps them up at night?]
- **Their Requests**: [What do they want to see?]

#### Communication Preferences
- **Preferred Format**: [Email, meetings, documents, visual, etc.]
- **Communication Frequency**: [Weekly, monthly, quarterly]
- **Best Time/Day**: [When to reach out?]
- **Escalation Path**: [Who do they report to?]

#### Relationship Management
- **Current Sentiment**: [Ally / Neutral / Skeptical / Opposing]
- **Key Influencers**: [Who influences them?]
- **Building Rapport**: [What connects with them?]
- **Potential Issues**: [What could cause conflict?]

### Engagement Strategy
- **Regular Check-In Cadence**: [Weekly 1:1 / Monthly meeting / etc.]
- **Updates Provided**: [What information?]
- **Input Solicited**: [What decisions need their input?]
- **Win-Win Opportunities**: [How can we align interests?]
```

### Example Stakeholder Profile

```markdown
## Sarah Chen, VP Engineering

### Basic Information
- **Title**: VP Engineering
- **Department**: Engineering
- **Years in Role**: 3 years
- **Reporting**: Reports to CEO

### Stakeholder Characteristics

#### Power & Interest
- **Level of Influence**: High (can approve/block technical direction)
- **Level of Interest**: High (responsible for delivery)
- **Quadrant**: Manage Closely

#### Motivations & Goals
- **Primary Goal**: Deliver high-quality product on time with sustainable team velocity
- **Secondary Goals**: Build world-class engineering culture, scale team, improve tech infrastructure
- **Success Metrics**: On-time delivery %, team retention, code quality, deployment velocity

#### Product Involvement
- **How They Use Product**: Uses daily, deep technical knowledge
- **Their Concerns**: Technical debt accumulation, hiring and retention, scaling infrastructure
- **Their Requests**: More time for infrastructure work, reduce feature bloat, better scope discipline

#### Communication Preferences
- **Preferred Format**: In-person meetings, well-documented written decisions
- **Communication Frequency**: Weekly (2x preferred)
- **Best Time/Day**: Tuesday-Thursday mornings
- **Escalation Path**: CEO

#### Relationship Management
- **Current Sentiment**: Ally (generally supportive, sometimes pushes back on scope)
- **Key Influencers**: CTO (architect), engineering team leads
- **Building Rapport**: Weekly tech sync, involving her early in architecture decisions, respecting her constraints
- **Potential Issues**: Over-committing to features without engineering input; ignoring tech debt

### Engagement Strategy
- **Regular Check-In Cadence**: Weekly 1:1 + weekly cross-functional sync
- **Updates Provided**:
  - Weekly progress on commitments
  - Monthly tech debt assessment
  - Quarterly strategic planning input
- **Input Solicited**:
  - Technical feasibility of all roadmap items
  - Capacity and effort estimates
  - Tech debt priorities
  - Infrastructure planning
- **Win-Win Opportunities**:
  - Allocate 20% capacity to her tech priorities in exchange for commitment to product roadmap
  - Involve her in strategic planning to ensure engineer perspective
  - Feature flags to unblock product velocity while building infrastructure
```

---

## Framework 3: Stakeholder Assessment Matrix

Create a comprehensive view of all your stakeholders:

| Stakeholder | Role | Influence | Interest | Quadrant | Motivation | Communication | Frequency | Issues |
|-------------|------|-----------|----------|----------|-----------|-----------------|-----------|--------|
| CEO | Executive | High | High | Manage | Business growth, profitability | Strategic docs, metrics | Weekly | Impatience with execution |
| VP Eng | Leader | High | High | Manage | On-time delivery, quality | Tech design docs, estimates | Weekly | Tech debt vs features |
| VP Sales | Leader | Medium | High | Keep Sat. | Revenue growth, customer wins | Sales materials, GTM | Monthly | Wants everything quickly |
| Marketing VP | Leader | Medium | Medium | Keep Sat. | Marketing campaigns, launches | Feature lists, positioning | Monthly | Lack of detail sometimes |
| Support Lead | Manager | Low | High | Keep Inform. | User satisfaction, bug fixes | Feature impact, user feedback | Monthly | Feels unheard |
| Engineering Team | Individual | Low | High | Keep Inform. | Clear requirements, stability | Detailed specs, PRDs | Weekly | Scope creep, unclear spec |
| Sales Team | Individual | Low | Low | Monitor | Commission, easy sales | Product announcements | Ad hoc | Feature expectations |
| Customers | User | Low | High | Keep Inform. | Product works well, solves problems | Public roadmap, webinars | Quarterly | Timelines not met |

---

## Specific Stakeholder Types & Strategies

### The CEO/Founder

**Profile**:
- Cares most about business metrics (revenue, growth, profitability)
- Wants strategic clarity and monthly updates
- May be impatient with execution details
- Final decision-maker on major trade-offs

**Engagement Strategy**:
- Monthly strategic review (30 min) with metrics on a 1-pager
- Email update every 2 weeks (5 bullet points max)
- Quarterly deep-dive strategy session
- Escalate decisions above your authority quickly
- Frame everything in terms of business impact, not features

**Sample CEO Update**:
```
## Product Update - November

### Headlines
- Completed AI recommendation engine (Q1 priority)
- 30-day retention improved 5% vs. last month
- #1 customer churn reason: onboarding confusion (new insight)

### Key Metrics
- Monthly Active Users: 85K (+12% vs. October)
- Retention (D30): 65% (+5 points vs. October)
- Net Promoter Score: 42 (+3 points)
- Revenue: $1.2M ARR (+8% vs. October)

### Q1 Focus Areas
1. Enterprise onboarding (target 50K+ customer segment)
2. Mobile app (app store customers requesting)
3. Integrations marketplace (expand ecosystem)

### Blockers / Help Needed
- None currently blocking
- Will need sales input on enterprise pricing model (Q1)
```

### The VP of Engineering

**Profile**:
- Cares about technical feasibility, quality, and team velocity
- Needs detailed scope and clear requirements
- Concerned about accumulating technical debt
- Wants to be involved in architecture decisions early

**Engagement Strategy**:
- Weekly 30-min technical sync on Now items (architecture, tradeoffs)
- Monthly capacity planning review (are we committing too much?)
- Quarterly planning to get their input on priorities
- Involve them in all "how" decisions, own "what" and "why"
- Respect their engineering constraints and estimation

**Sample Eng Sync Agenda**:
```
## Product + Engineering Weekly Sync - Nov 15

### Progress on Current Initiatives
- Smart notifications: 60% complete, on track for launch Nov 28
- API v2 response optimization: Completed, ready to merge
- Mobile auth flow: Blocked on backend session handling

### Architecture Deep Dive
- OAuth2 integration approach review
- Database schema changes for multi-org support
- Discuss 2-3 technical options, pick direction

### Capacity & Constraints
- Holiday time and impact on Q4 finish dates
- Q1 capacity planning (hiring status, availability)
- Unforeseen issues or tech debt burning velocity

### Next Week Preview
- Code review for notification service
- Test plan for mobile auth
- Scope refinement for integrations API
```

### Sales & Customer Success

**Profile**:
- Care about customer value and competitive positioning
- Want to understand what they can sell and when
- Need ammunition to close deals and retain customers
- Often push for more features and earlier timelines

**Engagement Strategy**:
- Monthly sales enablement update (1 pager on new features to sell)
- Quarterly business review with competitive context
- Involve in customer research and feedback loops
- Share (filtered) customer roadmap they can discuss with prospects
- Be honest about timelines - early promises hurt your credibility

**Sample Sales Update**:
```
## Sales Enablement - November Features

### Launched This Month
**Smart Recommendations**
- Personalized suggestions for each user based on activity
- Pitch: "Give your users relevant content so they stay engaged"
- Competitive advantage: Only system with ML-powered recommendations
- Launch date: Nov 20
- Training session: Nov 22 @ 2pm

### Coming Q1
**Enterprise Security**
- SSO/SAML authentication
- Role-based access control
- Advanced audit logs
- Pitch: "Ready for enterprise deployments and compliance"
- Timeline: Jan 15 (soft launch), Feb 15 (full launch)

**Not in Plans** (Be transparent about "no" answers)
- Custom fields (low priority vs. other work)
- On-premise version (cloud-only strategy)
- Quarterly pricing (annual subscriptions only)
- Can revisit in Q3 if priority changes

### Competitive Context
- Competitor X launched real-time collaboration last month (good news: we're planning that for Q2)
- Competitor Y raising Series C (no product impact to us)
```

### Major Customers / Customer Advisory Board

**Profile**:
- Care about roadmap because it impacts their long-term use
- Want to feel heard and special
- May lobby for specific features
- Can be advocates or detractors

**Engagement Strategy**:
- Quarterly business reviews (30-60 min)
- Share roadmap (filtered - no dates, just themes)
- Solicit feedback on strategic direction
- Invite to user research sessions
- Make them part of product story (with permission)
- Be honest about timelines - don't over-promise

**Sample CAB Update**:
```
## Customer Advisory Board - Q1 2025 Roadmap

Thank you for being part of our advisory board. We'd love your input on our strategic direction for 2025.

### Strategic Themes We're Focusing On

1. **Enterprise-Grade Security**
   - Your feedback: Many of you operate in regulated industries
   - What we're building: SSO, audit logs, role-based access
   - How it helps: Enables deployment in enterprise environments

2. **Real-Time Collaboration**
   - Your feedback: Teams want to work on same items together
   - What we're building: Real-time sync, presence indicators
   - How it helps: Better team coordination, less friction

3. **Advanced Integrations**
   - Your feedback: You use our product with Salesforce, HubSpot, etc.
   - What we're building: Native integrations, API access
   - How it helps: Seamless workflow without manual syncing

### We'd Love Your Input On
1. Which of these themes is most important to you?
2. What's a use case we're not addressing?
3. What's preventing you from expanding use of our product?

### What We're Not Doing (At Least This Year)
- On-premise deployment (cloud-only strategy)
- Complex custom workflows (focus on simplicity)
- Mobile app (web is responsive, meets 95% of use cases)

Feedback form: [link] | Questions? Reply to this email
```

### Support / Customer Success Team

**Profile**:
- First to hear customer pain points
- Care about product stability and bug fixes
- Underutilized as insight source
- Often feel unheard in roadmap process

**Engagement Strategy**:
- Monthly meeting to review top customer requests
- Weekly Slack channel for bugs and issues
- Involve in user interviews
- Share roadmap so they understand "why" when customers ask
- Celebrate when roadmap items ship and help customers

**Sample Support Sync**:
```
## Product + Support Monthly Sync - Nov

### Top Customer Requests This Month
1. Export to CSV (5 requests)
2. Custom fields (3 requests)
3. Team permissions improvements (4 requests)
4. Dark mode (15 requests - meme status)

### Current Issues & Bugs
- Memory leak on mobile causing crash after 30 min (HIGH PRIORITY)
- Notification emails sometimes don't arrive (MEDIUM)
- Export feature occasionally cuts off data (MEDIUM)
- Dark mode still unavailable (LOW)

### What's Launching Soon (Help Your Customers)
- Smart recommendations engine (Nov 20)
- Advanced reporting dashboard (Dec 10)
- API access (Q1 2025)

### Product Education Opportunities
- We're doing webinar on Dec 5 about new reporting features
- Can we do a FAQ/help article series on best practices?
- Could support team do "Tip of the Week" tips with new features?

### Feedback for Roadmapping
- Customers report confusion in onboarding (potential roadmap item)
- Team permissions is biggest blocker for multi-user teams
```

---

## Creating Your Stakeholder Map

### Step 1: Identify All Stakeholders
List everyone who:
- Makes decisions about your product
- Is affected by your product decisions
- Can influence others' support for your roadmap
- Has a vested interest in product direction

### Step 2: Assess Power & Interest
For each stakeholder, rate 1-5:
- **Power**: How much influence do they have on product decisions?
- **Interest**: How much do they care about product direction?

### Step 3: Place in Matrix
Plot on Power/Interest grid to determine strategy

### Step 4: Document Communication Plan
For each stakeholder or stakeholder group:
- How often will you communicate?
- What format (email, meeting, doc)?
- What information will you share?
- What input do you want?

### Step 5: Set Reminders
- Calendar reminders for regular stakeholder updates
- Monthly check-in calendar
- Quarterly strategy session with key stakeholders

### Step 6: Adjust Based on Learning
- Quarterly stakeholder assessment
- Update strategies based on sentiment changes
- Add new stakeholders as organization evolves

---

## Red Flags in Stakeholder Management

🚩 **You're in trouble if**:
1. A "Manage Closely" stakeholder is surprised by roadmap changes
2. Stakeholders frequently complain "we weren't consulted"
3. The same questions keep coming up in meetings (communication issue)
4. Stakeholders are lobbying CEO against your roadmap
5. Support/Sales team learns about features from users, not from you
6. Key decision-makers don't understand why items are prioritized
7. Roadmap announcements create conflict instead of alignment

✅ **You're doing well if**:
1. Stakeholders feel heard even when you say "no"
2. Most stakeholders understand roadmap rationale
3. Decisions are questioned but ultimately supported
4. Your team feels ownership over roadmap
5. Customers feel like their input shaped direction
6. Decisions are made efficiently (not over-consulted)
7. Roadmap changes are handled proactively, not reactively
