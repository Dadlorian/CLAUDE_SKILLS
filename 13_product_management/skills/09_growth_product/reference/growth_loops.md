# Growth Loops: Comprehensive Reference

## Introduction

A growth loop is a self-reinforcing cycle where users' actions within a product create conditions for growth without relying on paid marketing. Every loop has the same structure: **Trigger → Action → Value → Growth Output**.

This reference provides detailed analysis of six major growth loop types with real examples, mechanisms, and metrics.

---

## 1. Viral Loops (Network Effects)

### Overview
Viral loops occur when the core product value is amplified by the presence of more users. Growth is a natural consequence of the product experience.

### Mechanism

```
User A joins
    ↓
Value depends on User B being present
    ↓
User A invites User B (implicit or explicit)
    ↓
User B joins
    ↓
Both get more value
    ↓
They invite User C & D
    ↓
Exponential growth if Viral Coefficient (K) > 1
```

### Viral Coefficient Formula

**K = Invites per user × Acceptance rate**

Example:
- Average user sends 2 invites
- 40% of invites convert to signups
- K = 2 × 0.40 = 0.8

**Growth trajectory**:
- K = 1.5: Quadruples every cycle
- K = 1.2: Doubles every 3-4 cycles
- K = 0.8: Eventually declines
- K = 0.5: Slower decline

### Cycle Time
Time from referral to referred user being active and generating new referrals.

**Impact**: Shorter cycles = faster exponential growth
- WhatsApp: ~1 day (friend sends message, recipient responds immediately)
- LinkedIn: ~5 days (invitation sits, acceptance, profile setup)
- Slack: ~2 days (workspace created, teammates invited, first message)

### Requirements for Strong Viral Loops

1. **High Initial Value**: Users must see value BEFORE inviting
   - Must achieve aha moment in first session
   - No user wants to look foolish inviting to value-less product

2. **Network Dependency**: Value increases with more users
   - Communication: Bigger network = more valuable
   - Marketplace: More supply/demand = lower frictions
   - Collaboration: More teammates = more capable
   - Social: More friends = more content

3. **Easy Invitation Mechanism**: Frictionless sharing
   - One-click or integrated sharing
   - Works across contexts (email, SMS, in-app, etc.)
   - Doesn't disrupt core experience

4. **Invitation Incentive**: Both parties benefit
   - Referrer: Gets social proof, status, utility
   - Invitee: Gets immediate value from network
   - Don't rely on external incentives (quality matters more)

### Real Examples

#### WhatsApp
**Loop**:
- User 1 downloads WhatsApp
- First value: Person-to-person messaging
- User 1 messages User 2 (explicit invitation)
- User 2 downloads to receive message
- User 2 immediately has 1-on-1 with User 1
- User 2 messages User 3, User 4...

**Metrics**:
- Viral coefficient: 0.7-0.8
- Cycle time: 1 day
- Growth: Reached 1 billion users with minimal advertising

**Why it works**:
- Network mandatory for core value
- Immediate messaging works cross-platform
- Mobile perfect distribution mechanism
- Solved friction of cross-border calling

#### LinkedIn
**Loop**:
- User 1 joins LinkedIn (professional network)
- Sends connection request to 10 contacts (explicit)
- Includes message: "Let's stay connected"
- User 2 receives email invitation
- Clicks link, creates account
- LinkedIn auto-fills contacts from User 2's email
- User 2 sends invites to their 10 people
- Loop continues

**Metrics**:
- Viral coefficient: 0.3-0.4
- Cycle time: 5-7 days
- Grew to 900 million users

**Why it works**:
- Direct contact database seeding
- Email provides credibility
- Professional context makes invites natural
- Each user has Rolodex to work through

#### Figma
**Loop**:
- Designer creates design file
- Shares link with developer
- Developer clicks link, starts viewing (no signup needed)
- Can comment, request changes
- Developer gets value from real-time feedback
- Developer's team asks for access
- Team members join to collaborate
- Becomes de-facto standard for team

**Metrics**:
- Viral coefficient: 0.8-1.0
- Cycle time: 2-3 days
- Grew 2x YoY at scale

**Why it works**:
- Sharing is core to workflow
- No signup needed to see value
- Collaboration creates coordination problem
- Team effect (hard to leave once team adopts)

### Optimizing Viral Loops

**Increase viral coefficient**:
- Make invitations easier (reduce friction)
- Increase value for network (make group experience better)
- Make both parties better off (alignment)
- Optimize display of network size (social proof)

**Reduce cycle time**:
- Eliminate email verification steps
- Pre-fill data from inviter
- Show value immediately (not after setup)
- Push referrer to start inviting faster

**Expand addressable market**:
- Make invitations work cross-network
- Support multiple invitation channels
- Allow guest access before signup

### Viral Loop Risks

1. **Activation dependency**: Product must deliver value immediately
   - If activation is low, viral coefficient is moot
   - Can't viralize a product nobody understands

2. **Quality ceiling**: Invites can invite low-quality users
   - Network becomes noisy/spammy
   - Retention declines
   - Example: Early Airbnb faced this with spam listings

3. **Market saturation**: Loop eventually slows
   - Everyone's already invited
   - Requires retention to continue
   - Need secondary loops

---

## 2. Referral Loops (Incentivized Sharing)

### Overview
Referral loops explicitly incentivize users to invite others. Unlike viral loops, growth isn't automatic—users must be motivated through rewards.

### Mechanism

```
User A achieves satisfaction
    ↓
Sees referral incentive ("Get $50 credit")
    ↓
Sends referral to User B
    ↓
User B signs up with discount
    ↓
Both get reward
    ↓
Both can refer more
    ↓
Linear/polynomial growth (K often < 1)
```

### Types of Referral Incentives

#### 1. Direct Financial
- Dropbox: "+250MB free storage per referral"
- Uber: "$20 credit per referral"
- Airbnb: "$25-50 credit per referral"

**Pros**:
- Clear and motivating
- Easy to measure
- Works across all users

**Cons**:
- Attracts low-quality users (discount shoppers)
- Expensive at scale
- Creates incentive to refer everyone, not selectively

#### 2. Social/Status
- Robinhood: Diamond badge for top referrers
- Duolingo: Leaderboard position
- PayPal: Founder bonus

**Pros**:
- Scalable (no cost)
- Attracts quality users (status-motivated)
- Creates community

**Cons**:
- Only motivates competitive users
- Requires large leaderboard (top 5% motivated)
- Hard to measure impact

#### 3. Product Features/Access
- Slack: Unlock features for referring
- Notion: Higher free tier for referrals
- Figma: Extra projects/storage

**Pros**:
- Aligns with product usage
- Increases engagement (more features used)
- Leverages product value

**Cons**:
- Only works if features valuable
- Creates inequality (rich get richer)
- Can upset non-referrers

#### 4. Mutual Benefit
- Dropbox: Both referrer and referee get benefit
- Uber: Referrer and rider both get credits
- Airbnb: Both host and guest get credit

**Pros**:
- Fair, reciprocal
- Increases conversion (referee benefits too)
- Creates good brand feeling

**Cons**:
- More expensive than one-sided
- Creates gaming potential

### Referral Metrics

**Referral Rate (RR)**: % of users who make at least one referral
- Benchmark: 2-5% for most products
- High performers: 10%+
- Typically lower than viral loops

**Referral Conversion Rate (RCR)**: % of referred users who convert
- Benchmark: 20-40%
- Varies by incentive strength
- Tends higher than cold visitors

**Viral Coefficient from Referral**:
- K = RR × RCR × Repeat referral rate
- Example: 5% × 30% × 1.5 = 0.225
- Usually << 1 (linear, not exponential growth)

**Net CAC Impact**:
- Referral CAC: (Incentive cost) / (Signups from referrals)
- Benchmark: $5-20 per referred signup
- Should be < half of paid CAC

### Real Examples

#### Dropbox
**Loop**:
- User signs up
- Gets 2GB free storage
- Sees "Get more space" referral link
- Invites friends via email/social
- Friend signs up, both get +250MB
- User can earn up to 16GB (64 referrals)

**Metrics**:
- Referral rate: ~5% of users make at least one referral
- Conversion rate: ~25%
- Viral coefficient: ~0.25
- Contributed ~25-30% of signups at peak

**Why it works**:
- Storage is tangible, valuable asset
- Everyone understands storage benefit
- Mutual benefit (both get)
- Referral link is easy to share

**Math**:
- CAC from referral: ~$1-2 per signup
- CAC from paid: $30-40 per signup
- Payback: Free (already paid for storage)

#### Uber
**Loop**:
- Rider takes trip
- Gets notification: "Refer a friend, get $20 credit"
- Clicks share button
- Sends code to 5 friends via text
- Friend signs up, takes first ride with code
- Both get $20 credit

**Metrics**:
- Referral rate: ~8-10%
- Conversion: ~15-20%
- Each referral worth $40 (both sides)
- Cost per acquisition: $40

**Why it works**:
- Cash incentive clear and valuable
- Mutual benefit (both win)
- Easy sharing mechanism (SMS, in-app)
- First ride is natural conversion point

**Challenge**:
- Expensive at scale (costs $40 to acquire $50 LTV user)
- Had to change model when growth prioritized over profitability

#### Airbnb
**Loop**:
- Host lists property
- See referral program: "Get $25 credit per referral"
- Shares link in property description
- Friend books stay
- Both get credit (host toward future stays, guest toward current booking)

**Metrics**:
- Viral coefficient: ~0.3
- Network size: Both supply (hosts) and demand (guests) expanding
- Contributed ~20% of growth

**Why it works**:
- Mutual benefit reduces friction
- Natural sharing point (in listings)
- Incentivizes both sides of marketplace

---

## 3. Content Loops (SEO & Discovery)

### Overview
Users create content that attracts new users through search and discovery. The loop:

```
User 1 creates valuable content
    ↓
Content ranks in search / shared by others
    ↓
New user (User 2) discovers via content
    ↓
User 2 finds value in product
    ↓
User 2 creates content
    ↓
More discovery
```

### Viral Coefficient Mechanics
- K = (Content creators) × (Content discoverability) × (Conversion to signup) × (Repeat creation rate)
- Example: (10%) × (50% reach target audience) × (2% convert) × (80% create again) = 0.0008
- Seems low, but compounds over years

### Content Creation Flywheel

```
More Users → More Content Created → Better Search Results
     ↑                                       ↓
     └───────────────────────────────────────┘
```

### Search Engine Optimization (SEO)

**How it drives growth**:
1. User creates content optimized for keywords
2. Content ranks on Google for valuable search terms
3. Searches convert to traffic
4. Traffic converts to signups
5. New users create more content
6. Index grows exponentially
7. Traffic accelerates

**Content loop example - Quora**:
- User asks "How do I learn Python?" (indexed)
- Experts answer with detailed guides (indexed)
- Google ranks Quora #1 for "learn Python"
- Millions of searches → millions of clicks
- 50% of clickers create account
- New members answer other questions
- Quora has 300M+ monthly users largely from organic

### Discovery and Curation

**How recommendation engines drive growth**:
- User creates content (video, post, listing, etc.)
- Recommendation algorithm serves to relevant audience
- Viewers find product valuable
- Some viewers sign up
- More creators = more content = more viewers

**Example - TikTok**:
- Creator posts 30-second video
- Algorithm analyzes (audio, hashtags, viewing patterns)
- Serves to 10,000-100,000 potential fans
- If engaged, pushes to millions
- Viewers install app and sign up
- Creator gets followers and motivation to create more

### User-Generated Content (UGC) Dynamics

**Requirements for strong content loop**:
1. **Easy creation**: Simple tools, low friction
2. **Discoverable by others**: Algorithm or search-based
3. **Creator incentives**: Audience, monetization, status
4. **Quality control**: Spam prevention
5. **Network effects**: More content = more valuable

### Real Examples

#### Wikipedia
**Loop**:
- Expert edits or creates Wikipedia article
- Article ranks #1 on Google (Wikipedia trust)
- 100k searches/month drive traffic
- 5% of traffic creates Wikipedia accounts
- New editors expand existing articles
- More complete Wikipedia attracts more traffic

**Metrics**:
- 6.6 million articles
- 300+ million monthly visitors
- Powered by ~300k active editors
- ~99% organic traffic from search

**Why it works**:
- Authority (Wikipedia brand)
- Search rankings (trust signals)
- Editor community (intrinsic motivation)
- Coverage (breadth of topics)

#### Medium
**Loop**:
- Writer publishes article
- Medium promotes to readers on platform
- Readers clap (like) and follow
- Articles get tagged, recommended
- Tags bring discovery
- External search drives traffic
- Readers sign up to publish
- New writers create more content

**Metrics**:
- 100+ million monthly readers
- Powered by organic traffic (70%+)
- 50k+ publishers monthly

**Why it works**:
- Curation (editor and algorithmic)
- Community quality (follower model)
- Distribution (homepage + recommendations)
- SEO (content ages well)

#### Airbnb Blog/SEO
**Loop**:
- User publishes review of stay in Santorini
- Review on listing, indexed by Google
- Search: "Things to do in Santorini" includes Airbnb listings
- Tourist finds Airbnb
- Books stay, leaves review
- Reviews attract more searches
- Each review adds indexable content

**Metrics**:
- 7M+ listings (each with reviews, photos)
- Each listing indexed individually
- Combined: Dominates local travel searches
- 50%+ traffic from organic/search

---

## 4. Marketplace Loops

### Overview
Two-sided marketplaces have intertwined growth loops for supply and demand. Supply attracts demand, demand attracts supply.

### Chicken-and-Egg Problem

**The problem**:
- Riders won't use Uber with few drivers (long waits)
- Drivers won't drive for Uber with few riders (no income)
- Which comes first?

### Solution Strategies

#### 1. Supply-First Approach
- Recruit suppliers aggressively
- Subsidize until demand catches up
- Example: Uber's early days (driver incentives)

#### 2. Demand-First Approach
- Market heavily to demand side
- High transaction fees pay for supply recruitment
- Example: DoorDash (customer acquisition heavy)

#### 3. Concentrated Launch
- Focus geographic area until reaches critical mass
- Then expand
- Example: Uber's city-by-city approach

#### 4. Horizontal Marketplace
- Encourage high-quality supply
- Curated listings attract demand
- Demand sustains supply
- Example: Airbnb (focused on beautiful properties)

### Marketplace Growth Loops

#### Loop 1: Liquidity Begets Liquidity
```
More Supply (Sellers/Providers)
    ↓
Wait times decrease / selection increases
    ↓
Demand increases (Buyers/Customers)
    ↓
More fulfillment opportunities for supply
    ↓
More supply attracted
```

#### Loop 2: Network Effects
```
More Users (Either Side)
    ↓
More transactions
    ↓
More data on preferences/quality
    ↓
Better matching (algorithm)
    ↓
Better outcomes for both sides
    ↓
Network stronger
```

#### Loop 3: Reputation System
```
Transactions occur
    ↓
Reviews/ratings posted
    ↓
High-quality providers visible (reputation)
    ↓
Buyers prefer quality providers
    ↓
Quality providers gain more business
    ↓
New quality providers attracted
```

### Marketplace Metrics

**Supply-side**:
- Active providers (% of registered still active)
- Inventory (listings, capacity)
- Utilization rate (% of supply generating transactions)

**Demand-side**:
- Active buyers/customers
- Transaction frequency
- Transaction value (ARPU)

**Matching**:
- Acceptance rate (% of offers accepted)
- Match rate (% of demand filled)
- Wait time / friction

**Quality**:
- Ratings and reviews
- Return rate (repeat customers)
- Provider sustainability (retention)

### Real Examples

#### Uber
**Loops**:
1. **Liquidity loop**: More drivers → Lower wait → More riders → More driver income
2. **Surge pricing loop**: High demand → Higher rates → More drivers available → Lower wait times
3. **Geographic expansion**: Density increases at supply/demand → Critical mass → Profitability

**Metrics**:
- 3.9 million active drivers
- 147 million monthly active riders
- Operates in 70+ countries
- Time to profitability decreased as liquidity increased

**Why it works**:
- Regulatory advantage (first-mover in many cities)
- Unit economics work (LTV:CAC > 5:1)
- Viral loop + referral loop + network effects
- Liquidity begets liquidity

#### Airbnb
**Loops**:
1. **Supply quality loop**: Curated hosts → High-quality listings → More guests → More revenue for hosts → More hosts
2. **Demand loop**: More guests → More booking data → Better recommendations → More bookings → More host revenue
3. **Trust/reputation**: Reviews → Trustworthiness → More bookings → More reviews

**Metrics**:
- 7.7 million listings
- 150+ million bookings
- 220+ countries
- Revenue: $17B+ (largely from take rate)

**Why it works**:
- Solved trust problem (reviews, verification, insurance)
- Created network effects (more options = better experience)
- Host incentives aligned (higher bookings = more income)
- International scale (supply available everywhere)

#### Stripe Connect (B2B Marketplace)
**Loop**:
- Platform company uses Stripe
- Builds marketplace with creators/sellers
- Sellers paid out via Stripe Connect
- Sellers want to receive payments
- Sellers use Stripe's tools to accept payments
- More transaction volume
- Stripe captures more fee volume

**Why it works**:
- Solves payment problem for two-sided platform
- Reduces friction for supply (easy payouts)
- Creates network effects (more volume = better economics)
- Scales globally

---

## 5. Engagement Loops (Habit Formation)

### Overview
Engagement loops create habits through repeated trigger-action-reward cycles. They improve retention by increasing time spent in product.

### BJ Fogg Model

```
TRIGGER (internal or external cue)
    ↓
BEHAVIOR (habitual action)
    ↓
REWARD (emotional reinforcement)
    ↓
REPEAT 20+ TIMES
    ↓
HABIT (automatic)
```

### Types of Triggers

#### External Triggers
- Notifications (push, email, SMS)
- Calendar events (time-based)
- Location-based (when nearby)
- Ads and marketing

**Example**: LinkedIn weekly email digest
- Trigger: Email in inbox Friday morning
- Action: Click email, review top posts
- Reward: See what peers are doing (FOMO satisfaction)
- Repeat: 52 times per year (weekly)
- Habit: Checking LinkedIn Friday mornings becomes routine

#### Internal Triggers
- Emotional states (boredom, anxiety, loneliness)
- Contexts (morning coffee, commute, procrastination)
- Existing habits (after checking email)

**Example**: Instagram when bored
- Trigger: Boredom (internal emotional state)
- Action: Unlock phone, open Instagram
- Reward: Infinite scroll, see friends' posts, dopamine
- Repeat: 20+ times per day (average)
- Habit: Automatic phone check becomes compulsive

#### Network Triggers
- Other users taking actions that affect you
- Notifications from network
- Seeing activity of connections

**Example**: Slack mentions
- Trigger: Someone mentions you in channel (network action)
- Action: Click notification, read thread, respond
- Reward: Felt included, contributed, connection
- Repeat: Multiple times daily
- Habit: Checking Slack becomes constant

### Rewards That Drive Habits

#### 1. Completion/Achievement
- Percentage progress bars
- Level-ups and achievements
- Streak counters
- Example: Duolingo's streak counter (users obsess over not breaking streaks)

#### 2. Social
- Likes and comments
- Follower counts
- Leaderboards
- Social validation
- Example: Instagram likes (social feedback loop)

#### 3. Content/Novelty
- Infinite scroll (always new content)
- Algorithm personalization (always relevant)
- Variability (never sure what's next)
- Example: TikTok's "For You" page (perfect feed)

#### 4. Productive
- Accomplishment (task completed)
- Progress toward goal
- Utility delivered
- Example: Slack (productivity reward)

#### 5. Monetary
- Money earned
- Savings accrued
- Discounts unlocked
- Example: Robinhood (investing rewards)

### Habit Loop Examples

#### Duolingo
**Loop**:
- Trigger: Notification at 8am ("Time to practice!")
- Action: Open app, complete lesson (3-5 min)
- Reward:
  - Streak counter increases (+1)
  - XP points accumulate
  - Progress bar fills
  - Positive feedback ("Great job!")
- Frequency: Daily (users average 6-7 days/week)
- Habit: Checking Duolingo becomes morning ritual

**Metrics**:
- 90%+ of users have streaks > 7 days
- Average daily active user engagement: 15 minutes
- 40%+ return next day (highest in category)
- Viral through streak sharing

#### Snapchat
**Loop**:
- Trigger: Daily snapstreak (will break if not snap daily)
- Action: Send snap to friends (1-2 min)
- Reward:
  - Flame emoji next to friend
  - Number (days in streak) increases
  - Psychological fear of losing streak
- Frequency: Daily
- Habit: Daily Snapchat becomes mandatory check

**Metrics**:
- Snapstreaks drive 90%+ of daily engagement
- Users check Snapchat 18+ times per day
- Retention: 80% week 1, 30% month 1 for non-heavy users
- But streakers have nearly 100% retention

#### Starbucks Rewards
**Loop**:
- Trigger: Visit to Starbucks
- Action: Pay with app/card, unlock rewards
- Reward:
  - Stars accumulate visible in app
  - Free drink at milestones (25/50/100 stars)
  - Exclusive rewards for members
- Frequency: 15-20 visits per month (heavy users)
- Habit: Starbucks becomes daily ritual, preferring Starbucks over competition

**Metrics**:
- 18 million active Rewards members
- Members spend 2x more than non-members
- Habit frequency drives LTV significantly

### Engagement Loop Optimization

**Increase trigger frequency**:
- Add more touchpoints (push, email, SMS)
- Create natural reasons to return (new content, streaks)
- Lower friction to action

**Reduce friction to action**:
- Simplify the behavior (one-tap, pre-filled)
- Remove friction points
- Make it mobile-first

**Amplify reward**:
- Make progress visible
- Celebrate milestones
- Add social proof to rewards
- Use variable rewards (surprise and delight)

**Build social component**:
- Show what friends are doing
- Enable competition (leaderboards)
- Create FOMO (limited-time rewards)
- Facilitate connection

---

## 6. Revenue Loops

### Overview
Revenue loops are monetization mechanisms that align incentives and drive growth simultaneously.

### Mechanism

```
User achieves value
    ↓
Wants more/premium features
    ↓
Pays for premium version
    ↓
Gets higher quality experience
    ↓
Becomes more engaged / dependent
    ↓
Increased lifetime value
    ↓
PLG (product-led growth) | Organic expansion
```

### Freemium Model

**Concept**: Free tier gets users to activation, premium tier monetizes.

#### Slack (Freemium)
**Free tier**:
- Unlimited users
- Last 10k messages (searchable)
- All core features
- Free forever pricing

**Premium tier** ($8-12/user/month):
- Full message history
- Compliance features
- Priority support
- Advanced admin controls

**Loop**:
- Free tier drives activation and team adoption
- Growth accelerates (network effects)
- Team hits message limit (friction)
- Admin upgrades to unlock history
- Premium becomes necessary

**Metrics**:
- 50%+ of free teams eventually pay
- Viral coefficient in free tier creates high-quality upgrade base
- LTV:CAC ratio >5:1 (paying customers)

#### Figma (Freemium)
**Free tier**:
- 3 projects
- Shared libraries
- Basic plugins
- Free forever pricing

**Premium tier** ($12-200+/month):
- Unlimited projects
- Version history
- Team features
- Advanced permissions

**Loop**:
- Free tier drives designer adoption
- Designer creates, shares with team
- Team members sign up free
- Collaboration happens naturally
- As team grows, needs more projects
- Teams convert to paid

**Metrics**:
- 40%+ of free users eventually pay
- Strong network effects in free tier
- 50k+ paid teams

### Marketplace Monetization

**Concept**: Platform takes percentage of transactions.

#### Uber (Transaction Fee)
**Model**: 20-30% take rate per transaction
**Loop**:
- Riders and drivers join (free)
- Complete rides (platform takes cut)
- Riders spend $5-20 per ride (platform gets $1-6)
- Volume matters more than unit take rate
- Scale drives down costs, improves margins
- More profitable rides attract more drivers

**Metrics**:
- $17B revenue (largely from take rate)
- Gross margins: 35-40%
- Network effects: More volume → More profit

#### Stripe (Transaction Fee)
**Model**: 2.9% + 30¢ per transaction
**Loop**:
- Merchant sets up account (free)
- Takes payment from customer
- Stripe captures fee per transaction
- Volume drives economics
- More volume → Lower effective rate possible
- Scale attracts larger merchants

**Metrics**:
- $15B+ revenue
- 50%+ of online commerce
- Transaction volume drives all growth

### Subscription Monetization

**Concept**: Fixed recurring fee for access/features.

#### Netflix (Pure Subscription)
**Model**: $6.99-22.99/month
**Loop**:
- User signs up
- Watches content (becomes addicted)
- Hard to cancel (show dependencies)
- Retention > 60% month-to-month
- Continues paying as long as value > price

**Metrics**:
- 230+ million subscribers
- LTV: $300-500+
- Viral through shared accounts (positive for growth, negative for revenue)

#### LinkedIn Premium (Hybrid)
**Model**: Free + $35-60/month premium
**Loop**:
- 900M+ free users
- See premium features (InMail, profile views)
- High-value professionals convert to premium
- Premium users get recruiter tools, job alerts
- Premium attracts more premium users (status effect)

**Metrics**:
- Premium conversion: 2-3% of free users
- Premium LTV: $500+
- Net DAU (Daily Active Users) same for free and premium (retention)

---

## Comparative Analysis

| Loop Type | Viral Coefficient | Cycle Time | CAC | Scalability | Sustainability |
|-----------|------------------|-----------|-----|-------------|-----------------|
| **Viral** | 0.7-1.5 | 1-7 days | $0 | Very high | High (K>1) |
| **Referral** | 0.2-0.5 | 7-30 days | $5-20 | High | Medium (K<1) |
| **Content** | 0.01-0.1 | 30-90 days | $0 | High (long-term) | High (compounding) |
| **Marketplace** | 0.3-0.8 | 7-30 days | $20-100 | Very high | High (network effects) |
| **Engagement** | N/A | Recurring | Included | High | High (habit) |
| **Revenue** | N/A | Ongoing | Negative | High | Very high (LTV) |

---

## Combining Loops

**Most successful products use multiple loops**:

### Slack
1. **Viral loop**: Team collaboration (network effects)
2. **Engagement loop**: Daily streaks of communication (habits)
3. **Referral loop**: Invite teammates (incentive: team adoption)
4. **Revenue loop**: Freemium model (free → premium)

### Figma
1. **Viral loop**: Sharing designs (network effects)
2. **Marketplace loop**: Plugins and integrations
3. **Engagement loop**: Collaboration feedback loops
4. **Content loop**: Design community/templates
5. **Revenue loop**: Freemium model

### Uber
1. **Viral loop**: Marketplace liquidity (drivers ↔ riders)
2. **Referral loop**: $20 credit per referral
3. **Engagement loop**: Streak/habit of taking rides
4. **Revenue loop**: Surge pricing, premium tiers (Uber Black)

---

## Key Takeaways

1. **Viral loops are ideal but rare**: Only works with network-dependent products
2. **Referral loops are supplement**: Adds to other loops, rarely sole growth lever
3. **Content loops compound**: Slow start but exponential long-term (5+ year timescale)
4. **Marketplace loops are powerful**: Network effects on both sides amplify growth
5. **Engagement loops improve retention**: Foundation for all other monetization
6. **Revenue loops align incentives**: Growth and monetization reinforce each other
7. **Most successful products combine 3-5 loops**: Each addresses different growth stage

The best growth products don't rely on any single loop—they build a stack of reinforcing loops that compound over time.
