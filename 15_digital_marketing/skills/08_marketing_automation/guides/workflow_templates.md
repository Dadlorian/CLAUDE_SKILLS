# Marketing Automation Workflow Templates
## HubSpot, Marketo, Pardot Ready-to-Deploy Workflows

## Lead Scoring Workflow

**Trigger**: Contact is created or updated

**Demographic Scoring**:
- Title contains "VP" or "Director" → +20 points
- Title contains "Manager" → +10 points
- Title contains "C-Level" (CEO, CTO, CFO) → +25 points
- Company size 500-1000 employees → +10 points
- Company size 1000+ employees → +15 points
- Industry matches target → +10 points

**Behavioral Scoring**:
- Email opened → +2 points
- Email clicked → +5 points
- Website visit → +3 points
- Pricing page visit → +10 points
- Demo page visit → +15 points
- Form submission → +20 points
- Whitepaper download → +10 points
- Webinar attendance → +25 points

**Negative Scoring**:
- Email domain contains "gmail", "yahoo", "hotmail" → -10 points
- Email bounced → -50 points
- Unsubscribed from email → -100 points
- Competitor domain → -100 points

**Decay**:
- If no activity in 30 days → Reduce score by 10%
- If no activity in 90 days → Reduce score by 50%

**MQL Threshold**: 75 points
**Action when MQL**: Create task for sales, send internal notification

---

## Lead Nurture Workflow (Content Download)

**Trigger**: Contact downloads ebook/whitepaper

**Enrollment Criteria**:
- Lead score < 75 (not yet MQL)
- Not a customer
- Not unsubscribed

**Workflow**:

**Day 0**: Thank you email with download link
- Send asset immediately
- Set expectation for follow-up emails

**Day 3**: Related blog post
- IF opened previous email → Send blog post on related topic
- IF NOT opened → Wait 2 more days, try again

**Day 7**: Case study
- Send relevant customer success story
- Highlight results similar to their use case

**Day 10**: Webinar invitation
- IF attended webinar → Skip to Day 14 offer
- IF registered but didn't attend → Send recording

**Day 14**: Demo offer (if score > 50)
- Personalized demo invitation
- Include calendar booking link

**Day 21**: Educational series wrap-up
- Send comprehensive resource guide
- Survey: "Was this helpful? What else do you want to learn?"

**Exit Criteria**:
- Contact becomes MQL (score ≥ 75)
- Contact unsubscribes
- 30 days elapsed
- Contact becomes customer

---

## Sales Lead Routing Workflow

**Trigger**: Lead score reaches 75 (MQL threshold)

**Actions**:

**Step 1: Determine Owner**
- IF Company = Enterprise (1000+ employees) → Route to Enterprise Sales Team
- IF Company = Mid-Market (100-999 employees) → Route to Growth Sales Team
- IF Company = SMB (< 100 employees) → Route to SMB Sales Team

**Step 2: Geographic Assignment**
- IF Country = "United States" → Assign to rep based on state
- IF Country = "United Kingdom", "France", "Germany" → EMEA team
- IF Country = "Australia", "Singapore", "Japan" → APAC team

**Step 3: Create Sales Task**
- Create task: "Follow up with MQL: [Contact Name]"
- Due date: 24 hours from now
- Include: Lead source, score, recent activity, qualifying info

**Step 4: Internal Notification**
- Send Slack message to assigned rep's channel
- Include link to contact record
- Highlight hot activities (e.g., "Visited pricing page 3x this week")

**Step 5: Update Lifecycle Stage**
- Change lifecycle stage from "Lead" to "MQL"
- Set MQL date = Today
- Add to "MQL - Uncontacted" list for SLA tracking

**Step 6: Pause Other Workflows**
- Remove from all marketing nurture workflows
- Stop promotional emails
- Sales takes over communication

**SLA Tracking**:
- IF Task not completed within 24 hours → Send escalation email to sales manager
- IF Task not completed within 48 hours → Send escalation to VP Sales

---

## Customer Onboarding Workflow

**Trigger**: Deal stage changes to "Closed Won"

**Enrollment**:
- Contact = Decision Maker on closed deal
- Deal amount > $0

**Workflow**:

**Day 0** (Immediately):
- Send congratulations email
- CC: Customer success manager
- Include: Next steps, onboarding calendar invite, login credentials

**Day 1**:
- Create task for CSM: "Schedule kickoff call"
- Send customer: "What to expect in your first week"
- Invite to customer Slack/community

**Day 3**:
- Email: "Quick start guide" (most important features)
- Link to video tutorials
- Offer: Book 1:1 onboarding session

**Day 7**:
- Check usage data: IF no logins → Send re-engagement email
- IF active → Send best practices guide

**Day 14**:
- Send survey: "How is onboarding going?"
- Create task for CSM to check in

**Day 30**:
- Trigger health score calculation
- IF healthy → Send "You're doing great!" + upsell opportunity
- IF at-risk → Escalate to CSM for intervention

**Day 60**:
- Send case study template: "Share your story"
- Offer: Become a reference customer
- Incentive: $500 Amazon gift card for completed case study

**Day 90**:
- Send NPS survey
- IF Promoter (9-10) → Request review/testimonial
- IF Passive (7-8) → Ask for feedback
- IF Detractor (0-6) → Escalate to account manager

---

## Re-engagement Workflow (Inactive Leads)

**Trigger**: Contact has not engaged in 60 days

**Enrollment Criteria**:
- Previous engagement score > 30 (was somewhat engaged)
- Not a customer
- Not unsubscribed
- Not in active sales conversation

**Workflow**:

**Email 1** (Day 0): "We've missed you"
- Subject: "[Name], are we still relevant to you?"
- Content: Ask if still interested, update on what's new
- CTA: Update preferences or re-engage

**Delay 7 days**

**Email 2** (Day 7): Value reminder
- Subject: "Quick reminder: Here's what you're missing"
- Content: Highlight top resources, recent wins, new features
- CTA: Download latest whitepaper or watch demo

**Delay 7 days**

**Email 3** (Day 14): Special offer
- Subject: "Come back: Exclusive offer inside"
- Content: Limited-time offer (discount, extended trial, etc.)
- CTA: Claim offer

**Delay 14 days**

**Email 4** (Day 28): Final goodbye
- Subject: "Is it time to say goodbye?"
- Content: "We don't want to spam you. Stay or go?"
- CTA 1: "Keep me subscribed" (removes from this workflow, adds back to regular nurture)
- CTA 2: "Unsubscribe" (respects their choice)

**Exit Criteria**:
- Contact engages (opens + clicks)
- Contact becomes MQL
- Contact unsubscribes
- Workflow completes (28 days)

---

## Implementation Tips

**HubSpot**:
- Use "Workflows" tool
- Set re-enrollment rules carefully
- Use smart lists for dynamic enrollment
- Enable goal tracking for conversions

**Marketo**:
- Build in "Programs" with smart campaigns
- Use "Wait" steps between emails
- Leverage "Interesting Moments" for sales context
- Set up proper suppression lists

**Pardot (Salesforce)**:
- Use "Engagement Studio" for visual workflows
- Connect to Salesforce campaign sync
- Use dynamic lists for entry/exit
- Enable "Automation Rules" for complex logic

**Best Practices**:
- Always test with small segment first
- Set business hours for sending (9am-5pm recipient timezone)
- Respect frequency caps (max 3 emails per week)
- Monitor unsubscribe rates (>0.5% = red flag)
- A/B test subject lines and timing
