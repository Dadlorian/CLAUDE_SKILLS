# AARRR Metrics: Pirate Metrics Deep Dive

## Overview

AARRR (pronounced "aarrr" like a pirate) stands for **Acquisition → Activation → Retention → Revenue → Referral**. Coined by Dave McClure and popularized by Reforge, these five metrics form the complete picture of product growth and business health.

AARRR is NOT a funnel—it's a framework for measuring all critical business drivers:

```
                    ┌─────────────────────────┐
                    │    NEW USER SOURCES     │
                    │   (Acquisition Channel) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   AHA MOMENT REACHED    │
                    │   (Activation Metric)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │  USERS RETURN REGULARLY │
                    │  (Retention Cohort)     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   USERS PAY / MONETIZE  │
                    │   (Revenue & Economics) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │    USERS TELL OTHERS    │
                    │   (Viral & Referral)    │
                    └────────────┴────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   COMPOUNDING GROWTH    │
                    └─────────────────────────┘
```

---

## 1. Acquisition (Getting Users)

### Definition
Acquisition is the total number of users entering your product, measured by their source and cost.

### Core Metrics

#### Monthly/Quarterly/Annual New Users
- **Definition**: Total new user signups in period
- **Calculation**: Today's cumulative users - Last month's cumulative users
- **Example**: 50,000 new signups in October

**Why it matters**:
- Measures market demand
- Indicates if you're growing (positive) or shrinking (negative)
- Foundation for all other metrics

**Benchmarks** (varies wildly by industry):
- SaaS: 5-10% MoM growth (doubling every 1-2 years)
- Mobile apps: 10-30% MoM growth (higher velocity)
- Mature products: 0-5% MoM growth

#### Acquisition by Channel
Breaking down new users by source provides strategic insight:

**Channels**:
1. **Paid (Ads)**
   - Google Ads
   - Facebook/Instagram
   - LinkedIn
   - Programmatic display
   - Cost-based (CAC measurable)

2. **Organic/Search**
   - Google searches
   - SEO-driven traffic
   - Content discovery
   - Cost-based (content investment)

3. **Direct**
   - Bookmarks/remembering URL
   - Brand searches
   - Customer requests
   - Cost: 0

4. **Referral**
   - Referred by existing users
   - Affiliate programs
   - Partner mentions
   - Cost: Incentive-based

5. **Social**
   - Viral sharing
   - Influencer mentions
   - Social media
   - Cost: Variable

6. **Partnerships**
   - API integrations
   - Cross-promotions
   - Strategic partnerships
   - Cost: Revenue share or fixed

**Channel Analysis Example**:
```
October New Users: 50,000

Source           Users    %      CAC      Revenue Impact
Paid Ads         15,000   30%    $50      Controlled but expensive
Organic/SEO      20,000   40%    $10      Growing, lower cost
Direct           8,000    16%    $0       Brand strength signal
Referral         5,000    10%    $20      Product-driven growth
Social/Viral     2,000    4%     $5       Network effects
Total            50,000   100%   $24      Blended CAC
```

**Strategic insights from channel mix**:
- Organic/SEO growing? Product-market fit, content working
- Paid ads dominant? Growth reliant on continued spend
- Referral high? Network effects strong, product loved
- Direct growing? Brand building working

#### Cost of Acquisition (CAC)

**Definition**: Total cost to acquire one customer

**Calculation**:
```
CAC = Total Sales & Marketing Spend / New Customers Acquired

Example:
Spent $1,000,000 on ads/marketing in October
Got 15,000 new customers
CAC = $1M / 15,000 = $66.67 per customer
```

**CAC by Channel**:
```
Channel          Spend      Signups    CAC
Google Ads       $500k      5,000      $100
Facebook Ads     $300k      7,500      $40
Content/SEO      $150k      15,000     $10
Events           $50k       2,500      $20
Total            $1M        30,000     $33
```

**What's a good CAC?**

Depends on LTV (Lifetime Value). Rule of thumb:

**LTV:CAC Ratio Target**: 3:1 or higher
- LTV:CAC = 1:1 = Unsustainable
- LTV:CAC = 2:1 = Acceptable but risky
- LTV:CAC = 3:1 = Healthy
- LTV:CAC = 5:1+ = Excellent
- LTV:CAC = 10:1+ = Exceptional (rare)

**Example**:
- CAC = $100
- LTV = $500
- LTV:CAC = 5:1 (healthy)
- Company can spend $100 to acquire $500 customer

#### CAC Payback Period

**Definition**: How many months until customer revenue covers acquisition cost

**Calculation**:
```
CAC Payback = CAC / (ARPU × Gross Margin)

Example:
CAC = $100
ARPU = $50/month
Gross Margin = 60%
CAC Payback = $100 / ($50 × 0.60) = $100 / $30 = 3.3 months
```

**Benchmarks**:
- SaaS: 10-16 months acceptable
- SaaS: 6-12 months healthy
- SaaS: <6 months excellent
- Mobile: <3 months (faster payback due to high churn)

**Why it matters**:
- Measures how quickly company recoups investment
- Affects cash flow and sustainability
- Longer payback = need more capital

### Acquisition Optimization

**Decrease CAC**:
1. Improve product virality (reduce paid dependency)
2. Build organic/SEO traffic
3. Optimize paid ad performance
4. Partner with complementary products
5. Improve conversion funnel (fewer clicks to signup)

**Increase quality of acquired users**:
1. Segment campaigns by ICP (Ideal Customer Profile)
2. Test different messaging
3. Improve landing page relevance
4. Use product-qualified leads (PQL)
5. Partner with sources that attract fit users

---

## 2. Activation (First Value Moment)

### Definition
Activation is when a user experiences the core value of the product. It's the "aha moment."

### Why It's Different from Signup

**Signup** = User creates account
**Activation** = User finds value in product

These are NOT the same. A user can sign up and never activate.

**Data from typical product**:
```
Signup: 100% (all new users)
Activation (day 1): 60% (reach aha moment)
Activation (day 7): 40% (still using meaningfully)
Activation (day 30): 30% (regular engagement)
```

A 40% drop from signup to day 7 is typical.

### Defining Your Aha Moment

The aha moment is specific to each product. It's the moment when user realizes they need you.

**Method 1: Survey Users**
Ask paying, happy customers: "When did you first realize [product] was valuable?"

**Common answers**:
- Gmail: "When I could search my emails"
- Slack: "When my team was all online and I could message"
- Figma: "When I could share a design and get realtime feedback"
- Dropbox: "When I could access my files anywhere"
- Uber: "When I got my first ride in <5 minutes"

**Method 2: Analyze Engaged Users**
What do your best (high-LTV, high-retention) users do in first session?

Look for common actions among users with:
- 30-day retention > 50%
- 6-month retention > 30%
- High engagement (multiple sessions/day)

**Method 3: Trace Conversion Funnels**
Which first-session actions most predict future retention?

```
Action                  Day-7 Retention
Complete profile        45%
Invite first colleague  62%
Upload first file       38%
Create first project    58%
View template           32%
```

The actions that predict retention are your aha moments.

### Activation Metrics

#### Activation Rate
**Definition**: % of users reaching aha moment within X days

```
Activation Rate = (Users who reached aha moment) / (Total new users)

Example:
100 new users
60 users sent first message (aha moment)
Activation rate = 60%
```

**Benchmarks**:
- SaaS: 15-30% by day 7
- Mobile apps: 20-40% by day 1
- High LTV products: 40-50%+
- Low LTV products: 5-15%

#### Time to Activation
**Definition**: Days from signup to reaching aha moment

```
Average TTA = Sum of (signup date - aha date) / activated users

Example:
User A: Day 1 activation (TTA = 1 day)
User B: Day 3 activation (TTA = 3 days)
User C: Day 7 activation (TTA = 7 days)
Average TTA = 11/3 = 3.67 days
```

**Why it matters**:
- Faster activation = higher retention
- First week is critical (70% of churn happens)
- Each additional day increases drop-off
- Example: Slack - activation on day 1 = 80% retention, day 3 = 40% retention

**Benchmarks**:
- Product-market fit: < 3 days average
- Good products: 3-7 days
- Struggling products: > 7 days

#### Feature Adoption Rate
**Definition**: % of users adopting key features

```
Feature Adoption = (Users who used feature) / (Total active users)

Example:
Active users: 10,000
Users who used "Collaboration" feature: 3,000
Adoption rate = 30%
```

**Which features matter?**

Not all features contribute to aha moment. Focus on features most correlated with:
- Retention
- Revenue
- Referral
- Engagement

### Activation Optimization Tactics

#### 1. Reduce Path to Aha
Remove friction before core value moment.

**Tactics**:
- Reduce signup fields (remove all non-critical data)
- Auto-fill data from email/social
- Skip email verification (verify later)
- Use one-tap login (social/SSO)
- Allow guest access

**Example - Figma's approach**:
- Click "start designing"
- No signup required
- Create, design, collaborate
- Signup prompt only when saving

**Result**: 70% of new users reach aha before ever signing up

#### 2. Guided Onboarding
Show users exactly what to do in first session.

**Tactics**:
- Interactive tutorials (coachmarks)
- Empty state guidance
- Contextual tooltips
- Follow-the-leader walkthroughs
- Simplified first-session UI

**Example - Slack's onboarding**:
1. "Let's create a workspace" (step-by-step)
2. "Invite your team" (copy email list)
3. "Send your first message" (text field pre-focused)
4. Result: 70% complete message in first session

#### 3. Template and Example Data
Show users what's possible before they create.

**Tactics**:
- Sample projects/files
- Example boards/lists
- Starter templates
- "Inspiration" gallery
- Pre-loaded data for exploration

**Example - Notion's approach**:
- Shows 50+ templates on signup
- Users duplicate templates
- See what's possible
- Customize for their use case
- Activation much higher than blank-slate

#### 4. Motivating Context
Explain why they should care about each step.

**Tactics**:
- Show benefits ("Get real-time feedback on designs")
- Show social proof ("1M designers use this")
- Create FOMO ("Limited time: Free team collaboration")
- Appeal to job-to-be-done

**Example - Canva's onboarding**:
- "Design beautiful graphics in minutes"
- Shows example designs
- User can pick template
- Immediately productive
- Feels like success

#### 5. Incentivize Activation
Reward reaching aha moment.

**Tactics**:
- Celebration animation/notification
- Streak counter starts
- Unlock features
- Bonus credits/currency
- Progress badges

**Example - Duolingo**:
- First lesson completion triggers celebration
- Confetti animation
- +10 XP
- "You're on a 1-day streak!"
- Creates psychological momentum

### Activation Cohort Analysis

Different user cohorts (by source, date, etc.) activate at different rates.

**Example**:
```
Signup Source    Day-1 Activation    Day-7 Activation
Paid ads         35%                 45%
Organic          45%                 55%
Referral         55%                 65%
Social/Viral     25%                 35%
```

**Insights**:
- Referral users are higher quality (more motivated)
- Organic users better than paid (self-selected)
- Social/viral users lowest quality (lowest motivation)

**Action**: Adjust acquisition strategy to favor higher-quality sources

---

## 3. Retention (Users Returning)

### Definition
Retention measures what % of users continue using product over time.

### Core Retention Metrics

#### Daily Active Users (DAU)
**Definition**: Number of unique users with activity on given day

```
DAU = Unique users with ≥1 activity on Day X

Example:
Day 1: 10,000 unique users logged in
DAU = 10,000
```

#### Monthly Active Users (MAU)
**Definition**: Number of unique users with activity in given month

```
MAU = Unique users with ≥1 activity in Month X

Example:
October: 100,000 unique users logged in at least once
MAU = 100,000
```

#### DAU/MAU Ratio
**Definition**: Engagement ratio showing what % of monthly users are daily active

```
DAU/MAU = DAU / MAU

Example:
DAU = 30,000
MAU = 100,000
DAU/MAU = 30,000 / 100,000 = 0.30 = 30%
```

**What it means**:
- 30% of monthly users are daily active
- 70% are occasional users (monthly but not daily)

**Benchmarks**:
- Poor: < 10% (people barely use it)
- Average: 15-25%
- Good: 25-40%
- Excellent: 40-60%
- Exceptional: 60%+ (obsessive usage)

**By product type**:
- Messaging apps (WhatsApp, iMessage): 80-90% (people use daily)
- Social (Facebook, Instagram): 50-70%
- Productivity (Slack, Notion): 30-50%
- B2B SaaS (HubSpot, Salesforce): 10-20%
- Mobile games: 5-15%

#### Retention Cohort Analysis

**Definition**: Tracking what % of a user cohort (group) stays active over time

**Cohort** = Group of users who signed up in same period (day, week, month)

**Example - Monthly Cohorts**:
```
Cohort   M0    M1    M2    M3    M4    M5
Oct '23  100%  45%   32%   24%   18%   14%
Nov '23  100%  48%   35%   27%   20%   15%
Dec '23  100%  50%   38%   30%   23%   18%
Jan '24  100%  47%   36%   28%   21%   16%

Key patterns:
- Month 0 to 1: 45-50% retention (majority churn in first month)
- Month 1 to 2: 15% additional churn
- Month 3+: Stabilizes (remaining users are "sticky")
```

**Interpreting cohort data**:
- Improving cohorts = Product getting better
- Declining cohorts = Product degrading
- Steep Month 0→1 drop = Activation problem
- Cliff at Month 1 = Onboarding/trial expiration issue
- Flat line after Month 3 = Good quality retention

#### N-Day Retention
**Definition**: % of users active on day N

```
N-Day Retention = (Users active on day N who signed up on day 0) / (Total users who signed up on day 0)

Day 1 Retention = users active day after signup
Day 7 Retention = users active 7 days later
Day 30 Retention = users active 30 days later
```

**Example**:
```
Users signed up on October 1: 1,000

October 2 (Day 1): 700 active (70% day 1 retention)
October 8 (Day 7): 450 active (45% day 7 retention)
November 1 (Day 30): 300 active (30% day 30 retention)
```

**Benchmarks** (varies by type):
- Day 1 retention: 30-50%
- Day 7 retention: 15-30%
- Day 30 retention: 10-20%

**Poor products**: Day 1 < 25%
**Average products**: Day 1 30-50%
**Good products**: Day 1 > 60%

#### Churn Rate
**Definition**: % of users lost in period

```
Monthly Churn = (Users at month start - Users at month end) / Users at month start

Example:
October 1: 100,000 MAU
November 1: 95,000 MAU
Churn = (100k - 95k) / 100k = 5%

Inverse: 95% retention rate
```

**Rule of 40**:
For healthy SaaS:
```
Growth Rate + Retention Rate ≥ 40%

Examples:
- 30% growth + 20% churn (80% retention) = 110% ✓
- 50% growth + 30% churn (70% retention) = 120% ✓
- 10% growth + 5% churn (95% retention) = 105% ✓
- 2% growth + 5% churn (95% retention) = 97% ✓
```

### Retention by Segment

Retention varies dramatically by user type:

**Example**:
```
Segment          Day-7 Ret   Day-30 Ret   LTV
Enterprise       85%         65%          $50k+
Mid-market       60%         40%          $5k
SMB              35%         15%          $500
Free tier        10%         3%           $0
```

**Implications**:
- Enterprise worth retaining (high value)
- Free tier expected to churn (low value)
- Different product strategies for each

### Retention Improvement Levers

#### 1. Fix Aha Moment
If activation is strong but retention weak:
- Product delivers first value but not sustainable value
- Need continuous value delivery

**Example**: Social app where first session is fun but becomes boring
- Improve recommendation algorithm
- Add user-generated content
- Create community features

#### 2. Build Habit Loops
Create reasons to return daily/weekly

**Tactics**:
- Notifications (timely, valuable, not spammy)
- Streaks/progress (motivation)
- Social features (FOMO)
- New content (always something fresh)

#### 3. Improve Network Effects
Make product more valuable as others use it

**Tactics**:
- Encourage team adoption
- Show presence of others
- Enable collaboration/communication
- Create coordination problems

#### 4. Add Features Over Time
Keep product fresh and new

**Tactics**:
- New feature rollouts
- Content additions
- UI/UX improvements
- Competitive features

#### 5. Community and Content
Create reasons to stay engaged

**Tactics**:
- Creator programs
- Community forums
- User-generated content
- Educational content

---

## 4. Revenue (Monetization)

### Definition
Revenue measures how much money users generate, both per user and in aggregate.

### Core Revenue Metrics

#### Average Revenue Per User (ARPU)
**Definition**: Average revenue per user across all users (paying and non-paying)

```
ARPU = Total Revenue / Total Active Users

Example:
Total monthly revenue: $1,000,000
Total monthly active users: 50,000
ARPU = $1,000,000 / 50,000 = $20/user/month
```

**Calculation variations**:
- Monthly ARPU: Monthly revenue / monthly active users
- Lifetime ARPU: Total revenue per user from signup to churn

#### Average Revenue Per Paying User (ARPPU)
**Definition**: Average revenue per paying user (excludes non-paying free users)

```
ARPPU = Total Revenue / Paying Users

Example:
Total revenue: $1,000,000
Paying users: 10,000
ARPPU = $1,000,000 / 10,000 = $100/user/month
```

**Context**:
- ARPU = $20 (all users)
- ARPPU = $100 (paying only)
- Free-to-paid conversion: 10,000 / 50,000 = 20%

#### Lifetime Value (LTV)

**Definition**: Total revenue expected from customer over their lifetime

**Simple formula** (assumes stable ARPU and churn):
```
LTV = ARPU / Monthly Churn Rate

Example:
ARPU = $20/month
Monthly churn = 5% (95% retention)
LTV = $20 / 0.05 = $400
```

**More detailed calculation** (cohort method):
Track actual revenue per cohort over time

```
Cohort    Month 1   Month 2   Month 3   Month 4   Total LTV
Oct '23   $100      $90       $80       $65       $335
Nov '23   $110      $98       $85       $70       $363
Dec '23   $120      $105      $92       $75       $392

Average LTV = ~$363
```

**Relationship to other metrics**:
```
LTV = (ARPU × Months customer lasts)
    = ARPU / Churn rate
    = (ARPPU × Free-to-paid%) / Churn rate
```

**Benchmarks**:
- SaaS: $1000-10,000+ (depends on price point)
- Mobile apps: $50-500
- Marketplace: Varies by transaction value

#### LTV:CAC Ratio (Most Important)
**Definition**: How many dollars of lifetime value per dollar acquired

```
LTV:CAC = Lifetime Value / Cost of Acquisition

Example:
LTV = $500
CAC = $100
LTV:CAC = 5:1

Interpretation: Earn $5 for every $1 spent on acquisition
```

**Targets**:
- < 1:1: Unsustainable (losing money per customer)
- 1:1 to 2:1: Risky
- 2:1 to 3:1: Acceptable
- 3:1 to 5:1: Healthy
- 5:1+: Excellent
- 10:1+: Exceptional

**Example breakdown**:
```
Company A:
CAC = $50, LTV = $150
LTV:CAC = 3:1 (healthy)

Company B:
CAC = $50, LTV = $500
LTV:CAC = 10:1 (excellent)
Can spend more on acquisition

Company C:
CAC = $50, LTV = $40
LTV:CAC = 0.8:1 (unsustainable)
Losing $10 per customer
```

#### CAC Payback Period

**Definition**: Months until customer revenue covers acquisition cost

```
Payback = CAC / (ARPU × Gross Margin)

Example:
CAC = $100
ARPU = $50/month
Gross margin = 60% (60% revenue is profit)
Payback = $100 / ($50 × 0.60) = $100 / $30 = 3.3 months
```

**Benchmarks**:
- SaaS acceptable: 10-16 months
- SaaS healthy: 6-12 months
- SaaS excellent: <6 months
- Mobile: <3 months (higher churn)

**Why it matters**:
- Shorter payback = Company sustainable with less capital
- Longer payback = Need lots of funding or slow growth

#### Free-to-Paid Conversion Rate
**Definition**: % of free users who convert to paid

```
F2P Rate = Paying Users / Total Users

Example:
Total users: 100,000
Paying users: 3,000
F2P rate = 3%
```

**Benchmark** (varies by model):
- B2B SaaS: 2-5%
- B2C SaaS: 0.5-2%
- Mobile apps: 2-10%
- Games: 1-5%

**Improving F2P**:
1. Make free tier valuable (activate users)
2. Create upgrade triggers (hit limits)
3. Improve premium positioning (clear value)
4. Test pricing and positioning
5. Create scarcity/urgency

### Revenue Model Impact

Different models have different unit economics:

#### Freemium Model
```
Free users: 100,000 (90%)
Paid users: 10,000 (10%)
ARPPU: $100/month
F2P conversion: 10%

Monthly revenue: 10,000 × $100 = $1,000,000
ARPU (all users): $1,000,000 / 100,000 = $10/user/month

Strength: Large addressable market, high-quality paying users
Weakness: Low ARPU from free users, churn from free tier
```

#### Subscription Model
```
Total users: 50,000 (all paying)
ARPU: $30/month
Monthly retention: 95%

Monthly revenue: $1,500,000
Predictable recurring revenue

Strength: Predictable MRR, no freemium dilution
Weakness: Slower growth (paid from day 1)
```

#### Marketplace/Take Rate
```
Annual transaction volume: $100M
Take rate: 5%

Annual revenue: $5M
ARPU: $5M / (1M active transactors) = $5/user/year

Strength: Scales with volume, no incremental cost
Weakness: Volume-dependent, sensitive to take rate
```

#### Advertising Model
```
Monthly active users: 1M
CPM (cost per thousand impressions): $5
Monthly impressions: 1B
Monthly revenue: (1B / 1000) × $5 = $5M
ARPU: $5M / 1M users = $5/user/month

Strength: Monetizes all users (even free), scales
Weakness: User experience impacted, race to bottom on CPM
```

---

## 5. Referral (Viral Growth)

### Definition
Referral measures how much new growth comes from existing users inviting others.

### Core Referral Metrics

#### Viral Coefficient (K)
**Definition**: Average number of new users acquired per existing user

```
K = Invites per user × Invitation acceptance rate

Example:
Average user sends 2 invites
30% of invites convert to signup
K = 2 × 0.30 = 0.6
```

**Interpretation**:
- K > 1: Exponential growth (each user brings >1 new user)
- K = 1: Linear growth (each user brings exactly 1 new user)
- K < 1: Declining growth (each user brings <1 new user)
- K = 0: No viral growth

**Growth trajectory**:
```
K = 1.5: 100 users → 150 → 225 → 337 (doubling every 2 cycles)
K = 1.2: 100 users → 120 → 144 → 172 (doubling every 3 cycles)
K = 0.8: 100 users → 80 → 64 → 51 (declining)
K = 0.5: 100 users → 50 → 25 → 12 (rapid decline)
```

**Why it matters**:
- K > 1 means product can grow exponentially without paid acquisition
- K < 1 still helps (every acquisition brings +K new users)
- Compound effect over time is significant

#### Viral Cycle Time
**Definition**: Days from referral to referred user activation

```
Cycle time = Avg days from invite sent to invitee signup

Example:
User A sends invite Monday
User B clicks invite Wednesday
User B signs up Thursday (2-3 days)
Cycle time = 2-3 days
```

**Why it matters**:
- Shorter cycle = Faster exponential growth
- Longer cycle = Slower expansion, missed windows
- Related to CAC payback (faster cycle = faster payback)

**Examples**:
- WhatsApp: 1 day (message sends immediately, friend responds quickly)
- LinkedIn: 5-7 days (email sits, reminder sent, acceptance)
- Dropbox: 7-10 days (email, maybe reminder, click rate lower)

**Growth formula with cycle time**:
```
Total growth over 30 days = Initial × K^(30/cycle_time)

Example A: K=0.8, cycle=1 day
Growth = 100 × 0.8^30 = minimal (K < 1)

Example B: K=1.2, cycle=1 day
Growth = 100 × 1.2^30 = exponential (K > 1, fast cycle)

Example C: K=1.2, cycle=7 days
Growth = 100 × 1.2^(30/7) = 100 × 1.2^4.3 = ~2.5x (slower than Example B)
```

#### Referral Rate
**Definition**: % of users who make at least one referral

```
Referral rate = (Users who referred ≥1) / (Total users)

Example:
Total users: 100,000
Users who referred at least once: 3,000
Referral rate = 3%
```

**Benchmarks**:
- Low: <2% (minimal viral effect)
- Average: 2-5%
- Good: 5-10%
- Excellent: 10%+

**Factors affecting**:
- Product quality (great products get referred)
- Incentive strength (stronger incentive = higher rate)
- Ease of sharing (frictionless > difficult)
- Network value (more friends = more likely to refer)

#### Referral Conversion Rate
**Definition**: % of referred users who accept and sign up

```
Conversion rate = Signups from invites / Total invites sent

Example:
Users sent 5,000 invites
2,000 of invitees signed up
Conversion rate = 2,000 / 5,000 = 40%
```

**Benchmarks**:
- Email referrals: 10-30%
- SMS referrals: 15-40%
- In-app referrals: 20-50%
- Social referrals: 5-20%

**Factors affecting**:
- Trust (referred by friend = higher conversion)
- Incentive (both-sided incentive = higher)
- Relevance (friend network aligned with product)
- Friction (easy signup = higher conversion)

#### Net Promoter Score (NPS)

**Definition**: Measure of willingness to recommend (0-100)

```
NPS = % Promoters - % Detractors

Promoter: Rated 9-10 ("likely to recommend")
Passive: Rated 7-8
Detractor: Rated 0-6 ("unlikely to recommend")

Example:
100 survey respondents
60 rated 9-10 (promoters)
20 rated 7-8 (passive)
20 rated 0-6 (detractors)

NPS = 60% - 20% = 40
```

**Benchmarks**:
- <0: Poor (more detractors than promoters)
- 0-30: Average (room to improve)
- 30-50: Good (recommendation happening)
- 50-70: Excellent (strong advocacy)
- 70+: World-class (exceptional product)

**Relationship to referral**:
- High NPS → Higher referral rate (people recommend)
- Low NPS → Low referral rate (people don't recommend)
- NPS predicts growth better than most metrics

### Viral Loop Economics

**When viral loops are valuable**:

Viral coefficient impact on growth:
```
Paid acquisition: 10,000 users/month (cost = $500k)

Scenario A: K = 0 (no viral)
Month 1: 10,000 users
Month 2: 20,000 users
Month 3: 30,000 users (linear)

Scenario B: K = 0.5 (some viral)
Month 1: 10,000 users + 5,000 (viral) = 15,000
Month 2: 20,000 paid + 10,000 (from month 1) + 7,500 (viral of month 2) = 37,500
Month 3: 30,000 paid + 18,750 (viral compounding) + 11,250 = 60,000

Scenario C: K = 1.2 (strong viral)
Month 1: 10,000 + 12,000 = 22,000
Month 2: 20,000 + 26,400 = 46,400
Month 3: 30,000 + 55,680 = 85,680

Impact of K over 12 months:
K=0: 120,000 users total
K=0.5: ~400,000 users total (3.3x)
K=1.2: ~1,200,000 users total (10x)
```

**CAC impact**:
- With viral coefficient, effective CAC decreases
- 10,000 acquired users @ $50 CAC = $500k
- But 40,000 total users (including viral) = $12.50 effective CAC

---

## Summary Table: AARRR Metrics at a Glance

| Stage | Key Metric | Formula | Benchmark | Impact |
|-------|-----------|---------|-----------|--------|
| **Acquisition** | CAC | Marketing spend / new customers | $20-100 | Unit economics health |
| | Channel mix | % from each source | 30% organic | Sustainability |
| **Activation** | Activation rate | % reaching aha moment | 20-50% | Foundation for retention |
| | Time to activation | Days to aha | 2-7 days | Churn predictor |
| **Retention** | DAU/MAU | Daily / Monthly active | 20-50% | User engagement |
| | Cohort retention | % active at month N | 40%+ month 1 | Product quality |
| | Churn rate | % lost per period | 5% monthly | Business sustainability |
| **Revenue** | ARPU | Total revenue / users | $5-50+ | Monetization effectiveness |
| | LTV | Total lifetime revenue | $100-5,000+ | Customer quality |
| | LTV:CAC | Lifetime value / acquisition cost | 3:1+ | Business health |
| **Referral** | Viral coefficient (K) | Invites × acceptance | >0.5 | Growth efficiency |
| | NPS | Recommendation likelihood | 40+ | Advocacy strength |
| | F2P conversion | % free users who pay | 2-10% | Monetization conversion |

---

## Integration: How AARRR Works Together

The power of AARRR is that each stage enables the next:

1. **Acquisition → Activation**: Only quality-activated users create long-term value
2. **Activation → Retention**: Can't retain users who didn't activate
3. **Retention → Revenue**: Can't monetize users who don't return
4. **Revenue → Referral**: Happy, paying users refer more than free users
5. **Referral → Acquisition**: Viral users lower CAC, improving unit economics
6. **Full loop**: Better acquisition quality improves activation, which improves retention, which enables better monetization, which funds referral and viral growth

**Example of virtuous cycle**:
- Improve activation (clearer onboarding) → More users reach aha → Better retention → Higher LTV → Better unit economics → Can spend more on acquisition → Growth accelerates → Viral effects compound

**Example of vicious cycle**:
- Activation drops → Retention drops → LTV drops → Can't afford acquisition → Growth stalls → Less viral because fewer users → Downward spiral

This is why AARRR thinking is powerful: Fix problems in earliest stage (acquisition quality, activation clarity) rather than trying to compensate later (retention features, pricing tricks). Prevention is better than cure.
