# Setting Up Product Analytics: Complete Instrumentation Guide

Step-by-step guide for implementing analytics infrastructure that supports data-driven product decisions.

## Phase 1: Foundation and Planning

### 1.1 Define Your Analytics Philosophy

**What Gets Measured:**
- User actions that indicate value delivery
- Not vanity metrics (pageviews, signups alone)
- Not implementation details (API calls, server logs)
- Focus on behavior and outcomes

**Example Good Events:**
- document_created, document_edited, document_shared (indicates value in docs tool)
- message_sent, thread_viewed (for messaging product)
- filter_applied, results_viewed (for discovery/search)
- payment_processed, subscription_activated (for monetization)

**Example Bad Events:**
- page_loaded, component_rendered (too granular)
- api_call, database_query (implementation detail)
- user_loggedin (actually good if it indicates engagement)

### 1.2 Define North Star Metric

**Choose ONE metric that:**
- Correlates with user value and company success
- Moves with good product decisions
- Can be influenced by team
- Is measurable and reliable

**SaaS North Stars:**
- Monthly Active Users (MAU) - platform health
- Transactions per user - usage intensity
- Engagement score - combined daily + feature usage
- Revenue per user - monetization

**Marketplace North Stars:**
- Gross Merchandise Value (GMV)
- Transactions per active month
- Supply growth rate

**Creator/Content Platform North Stars:**
- Daily Active Creators - supply side
- Creator Earnings - monetization of supply
- Feed engagement - demand side

### 1.3 Design Metric Hierarchy

```
North Star Metric
├── Key Result Area 1
│   ├── Core Metric 1.1
│   ├── Core Metric 1.2
│   └── Core Metric 1.3
├── Key Result Area 2
│   ├── Core Metric 2.1
│   └── Core Metric 2.2
└── Key Result Area 3
    └── Core Metric 3.1
```

**Example for SaaS (Slack-like):**
```
Monthly Active Users (North Star)
├── Engagement (30% weight)
│   ├── DAU
│   ├── Message Volume
│   ├── Workspace Activity
├── Retention (40% weight)
│   ├── 7-day Retention
│   ├── 30-day Retention
│   ├── Churn Rate
└── Monetization (30% weight)
    ├── Workspace Tier Distribution
    ├── ARPU
    └── Expansion Revenue
```

## Phase 2: Event Instrumentation

### 2.1 Event Naming Convention

**Standard Format:**
```
<Object>_<Action>
OR
<Section>_<Action>_<Object>
```

**Rules:**
- All lowercase
- Use underscores (snake_case)
- Verb-noun or section-action-object
- Avoid vague terms ("click", "event", "action")
- Avoid names that are too specific to implementation

**Good Examples:**
```
message_sent
document_shared
workspace_created
team_member_invited
settings_updated
feature_enabled
payment_processed
onboarding_step_completed
```

**Bad Examples:**
```
user_click (too vague)
component_rendered (implementation)
api_request (technical detail)
onclick_button (technical)
event_occurred (meaningless)
```

### 2.2 Required Event Properties

**Every Event Must Include:**
```json
{
  "event_id": "unique-identifier",
  "event_name": "message_sent",
  "timestamp": "2025-11-19T10:30:00Z",
  "user_id": "user_12345",
  "session_id": "session_abc123",
  "device_type": "web|mobile_ios|mobile_android",
  "platform": "web|ios|android",
  "app_version": "2.1.5",
  "os_version": "14.5"
}
```

**Context Properties (Add as Relevant):**
```json
{
  "workspace_id": "workspace_789",
  "team_id": "team_456",
  "plan_tier": "pro|basic|enterprise",
  "is_paying": true,
  "cohort_date": "2025-01-15",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "growth_retargeting",
  "referrer": "product_hunt"
}
```

**Feature-Specific Properties:**
```json
{
  "message_type": "text|image|video",
  "message_length": 245,
  "recipient_count": 5,
  "thread_id": "thread_123",
  "attachment_count": 2
}
```

**NO PII in Events:**
- No email addresses
- No user names
- No passwords
- No payment details
- Encrypt/hash sensitive data if needed

### 2.3 Event Implementation by Platform

**Web (JavaScript/Segment)**
```javascript
// Segment SDK pattern
analytics.track('message_sent', {
  message_id: 'msg_123',
  message_type: 'text',
  message_length: 245,
  recipient_count: 5,
  context: {
    workspace_id: 'ws_789'
  }
});
```

**Mobile iOS (Swift/Amplitude)**
```swift
Amplitude.instance().logEvent("message_sent", withEventProperties: [
  "message_id": "msg_123",
  "message_type": "text",
  "recipient_count": 5,
  "workspace_id": "ws_789"
])
```

**Mobile Android (Kotlin/Amplitude)**
```kotlin
val eventProperties = JSONObject().apply {
  put("message_id", "msg_123")
  put("message_type", "text")
  put("recipient_count", 5)
  put("workspace_id", "ws_789")
}
Amplitude.getInstance().logEvent("message_sent", eventProperties)
```

**Server-Side Event (Python/Analytics)**
```python
import analytics

analytics.track(
  user_id=user_id,
  event='message_sent',
  properties={
    'message_id': 'msg_123',
    'message_type': 'text',
    'recipient_count': 5,
    'workspace_id': 'ws_789'
  },
  timestamp=datetime.now()
)
```

### 2.4 Event Quality Validation

**Before Deploying Events:**

1. **Naming Consistency Check**
   - Ensure name matches convention
   - Check for similar events (avoid duplication)
   - Verify verb and object are clear

2. **Property Validation**
   - All required properties present?
   - Properties are strings/numbers/booleans?
   - No PII included?
   - Property names consistent with conventions?

3. **Volume Check**
   - Is event fired at right frequency?
   - Not firing on every render or scroll
   - Fires on meaningful user action
   - Can filter for users who perform action

4. **Type Validation**
   - Numeric properties are numbers (not strings)
   - Boolean properties are true/false (not "yes"/"no")
   - Timestamps are ISO format
   - User IDs are consistent

### 2.5 Testing Event Instrumentation

**During Development:**
```javascript
// Enable debug mode to see events in console
analytics.debug();

// Or inspect Amplitude directly
window.amplitude.getInstance().logEvent('test_event', {
  test_property: 'value'
});
```

**In Staging:**
```
1. Create test user account
2. Perform action that should trigger event
3. Check in analytics dashboard within 1-2 minutes
4. Verify all properties populated correctly
5. Check no PII included
6. Validate property types
```

**Before Production:**
```
1. Run through full user journey as test user
2. Verify all events firing in sequence
3. Spot-check 5-10 events in analytics tool
4. Have QA perform cross-browser/device testing
5. Monitor event volume for first hour post-deployment
```

## Phase 3: Analytics Infrastructure Setup

### 3.1 Choose Your Analytics Stack

**Typical Setup:**
```
Events
├── Web SDK (Amplitude, Mixpanel, Segment)
├── Mobile SDK (Amplitude, Mixpanel, Firebase)
└── Server-side SDK (Amplitude, Mixpanel, custom)
    ↓
Analytics Platform (Primary)
├── Amplitude (best for power users, retention, experiments)
├── Mixpanel (best for funnel analysis, funnels)
├── Heap (best for autocapture, minimal setup)
└── Pendo (best for user analytics + guidance)
    ↓
Data Warehouse (Optional but Recommended)
└── Snowflake, BigQuery, or Redshift
    ├── Raw events table
    ├── User profiles table
    └── Custom metrics views
    ↓
BI Tool (Dashboarding)
└── Looker, Tableau, Metabase, Data Studio
```

**Decision Framework:**

| Tool | Best For | Cost | Ease |
|------|----------|------|------|
| **Amplitude** | Retention, cohorts, experiments | $$$$ | Medium |
| **Mixpanel** | Funnels, behavior flows, segmentation | $$$ | Medium |
| **Segment** | Multi-tool integration, data pipeline | $$$ | Hard |
| **Heap** | Minimal setup, autocapture | $$ | Easy |
| **Firebase** | Mobile apps, free tier | $ | Easy |

**Recommended Stack by Company Size:**

**Early Stage (< $1M ARR):**
- Amplitude (free tier) OR Firebase (mobile)
- Google Sheets + manual SQL queries
- Google Data Studio for basic dashboards

**Growth Stage ($1M-$10M ARR):**
- Amplitude + Google BigQuery
- Metabase for dashboarding
- dbt for data transformation

**Scale Stage ($10M+ ARR):**
- Amplitude + Snowflake
- Looker for dashboarding
- Custom dbt models
- Experimentation platform (Statsig, Optimizely)

### 3.2 Setup Amplitude

**Step 1: Create Account**
- Go to amplitude.com
- Sign up with company email
- Create organization and project

**Step 2: Install SDK**
```javascript
// Web
<script type="text/javascript">
  (function(window, document) {
    if (window.amplitude) { return; }
    window.amplitude = window.amplitude || {};
    var key = "YOUR_API_KEY";
    var url = "https://cdn.amplitude.com/libs/amplitude-8.17.0-min.js.gz";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.onload = function() {
      if (xhr.status === 200) {
        eval(xhr.responseText);
        window.amplitude.getInstance().init(key);
      }
    }
    xhr.onerror = function() {
      // handle error
    }
    xhr.send();
  })(window, document);
</script>
```

**Step 3: Identify Users**
```javascript
// Identify with user ID (required for analysis)
amplitude.getInstance().setUserId(user_id);

// Set user properties
amplitude.getInstance().setUserProperties({
  'plan_tier': 'pro',
  'company_size': 'small',
  'signup_date': signup_date,
  'cohort_date': cohort_date
});
```

**Step 4: Track Events**
```javascript
amplitude.getInstance().logEvent('message_sent', {
  message_type: 'text',
  recipient_count: 5
});
```

### 3.3 Setup BigQuery Data Pipeline

**Step 1: Enable Amplitude Data Export**
- In Amplitude, go to Settings > Data Export
- Choose Amplitude Org ID and Project ID
- Authorize Amplitude to write to BigQuery
- Select which events to export

**Step 2: Create BigQuery Dataset**
```sql
-- Create dataset
CREATE SCHEMA analytics
OPTIONS(
  description="Product analytics data",
  location="US"
);

-- Create events table (auto-created by Amplitude)
-- Will appear as amplitude_<TIMESTAMP>_events

-- Create user properties table (auto-created by Amplitude)
-- Will appear as amplitude_<TIMESTAMP>_user_properties
```

**Step 3: Setup dbt Transformation Layer**
```yaml
# dbt_project.yml
name: product_analytics
version: 1.0.0

models:
  product_analytics:
    materialized: table
    schema: analytics

    users:
      +materialized: table

    events:
      +materialized: incremental
      +incremental_strategy: merge
      +unique_id: event_id
```

```sql
-- models/users.sql
SELECT
  user_id,
  first_event_date,
  last_event_date,
  plan_tier,
  cohort_date,
  acquisition_source
FROM amplitude_user_properties
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY insert_id DESC) = 1
```

## Phase 4: Dashboard Setup

### 4.1 Build Core Metrics Dashboard

**Essential Elements:**

1. **North Star Metric**
   - Current value
   - Day-over-day change
   - 7-day and 30-day trends
   - Comparison to target

2. **Key Result Areas**
   - 3-5 metrics breakdown
   - Trend lines (7 and 30 day)
   - Current vs. previous period

3. **Core Metrics**
   - 8-12 operational metrics
   - Segment breakdowns (new vs. established users)
   - Weekly view for daily metrics
   - Historical trend

4. **Alerts**
   - DAU drop >20%
   - Signup rate decline >30%
   - Revenue decline >10%
   - Feature adoption plateau
   - Error rate spike

### 4.2 Typical Metrics Dashboard Layout

**Top Section:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   North     │    Metric   │   Metric    │   Metric    │
│   Star      │    2        │    3        │    4        │
│   (Large)   │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Middle Section:**
```
┌───────────────────────┬───────────────────────┐
│  KRA 1 Trend          │  KRA 2 Trend          │
│  (Last 90 days)       │  (Last 90 days)       │
├───────────────────────┼───────────────────────┤
│  KRA 3 Trend          │  KRA 4 Trend          │
│  (Last 90 days)       │  (Last 90 days)       │
└───────────────────────┴───────────────────────┘
```

**Lower Section:**
```
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│Core │Core │Core │Core │Core │Core │Core │Core │
│ M1  │ M2  │ M3  │ M4  │ M5  │ M6  │ M7  │ M8  │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

### 4.3 Segment Dashboard

**Track by:**
- New users (0-7 days) vs. established (7+ days)
- By acquisition channel
- By device (web vs. mobile)
- By plan tier
- By geography

**For Each Segment:**
- Engagement rate
- Retention rate
- ARPU
- Churn rate
- Feature adoption rate

## Phase 5: Documentation and Governance

### 5.1 Event Documentation

**Create Event Catalog (Spreadsheet or Wiki)**
```
Event Name: message_sent
Description: User sends message to recipient(s)
Category: Engagement / Messaging
Platforms: Web, iOS, Android, API
Properties:
  - message_type (text|image|video) - Type of message
  - recipient_count (number) - How many recipients
  - message_length (number) - Character count
First Tracked: 2025-01-15
Last Updated: 2025-11-19
Status: Active
Owner: @product_team
```

### 5.2 Metric Definitions

**Create Metric Specification**
```
Metric Name: Daily Active Users (DAU)
Definition: Unique users with at least one event per day
Calculation: COUNT(DISTINCT user_id) WHERE DATE(event_timestamp) = CURRENT_DATE
Data Source: Events table
Freshness: Daily at 2 AM UTC
Owner: Analytics team
Status: Active
Alerts: If DAU < (7-day average * 0.80)
```

### 5.3 Access Control

**Organize by Role:**
- **Product Managers**: Can view all dashboards, create reports, no edits to core metrics
- **Executives**: High-level dashboards only, no raw data access
- **Engineers**: Full BigQuery access, can create custom views
- **Analytics**: Full access, owns metric definitions and dashboards
- **Data Science**: Full access, owns experimental analysis

**Secrets Management:**
- Store API keys in secure vault (LastPass, 1Password)
- Never commit credentials to git
- Rotate keys quarterly
- Use service accounts for automated tools

## Phase 6: Ongoing Operations

### 6.1 Weekly Metrics Review

**Process:**
1. Check for data anomalies
2. Compare metrics to trends
3. Update forecasts if needed
4. Document changes or issues
5. Share weekly summary with team

### 6.2 Monthly Deep Dives

**Topics:**
- Cohort retention analysis
- Feature adoption trends
- Funnel performance by segment
- Churn analysis
- Acquisition quality by channel
- Revenue growth drivers

### 6.3 Data Quality Monitoring

**Regular Checks:**
- Event volume by platform (should be stable)
- Event latency (should be <5 minutes)
- Property completion rates (>95% for key properties)
- Duplicate events (should be <1%)
- Unusual user session patterns

**Alert Triggers:**
- Event volume drops >30% from baseline
- Latency increases >10 minutes
- Property completion drops <90%
- New event with same name appearing (duplicate?)

## Common Mistakes to Avoid

### ❌ Tracking Too Many Events
- Creates noise and confusion
- Slower to load SDKs
- Harder to maintain naming consistency
- **Fix**: Start with 20-30 core events, add as needed

### ❌ Inconsistent Event Names
- "message_sent" vs "messageSent" vs "message sent"
- Analytics tool treats as separate events
- **Fix**: Document naming convention, enforce in code review

### ❌ Missing Required Properties
- Can't analyze event meaningfully
- Can't attribute to users
- **Fix**: Require user_id, timestamp, and workspace/account context always

### ❌ Including PII in Events
- Privacy risk
- Compliance violation (GDPR, CCPA)
- Blocks data use
- **Fix**: Never send email, name, payment data; use IDs instead

### ❌ Not Testing Events
- Events fire inconsistently
- Properties have wrong types
- Volume much higher/lower than expected
- **Fix**: Test in staging, spot-check in production

### ❌ Assuming Events Correlate Causally
- Event A increased means A caused success
- Correlation ≠ causation
- **Fix**: Only trust A/B tests for causation; use events for correlation signals

### ❌ One Person Owns Analytics
- Knowledge concentration risk
- Slows down adoption
- Single point of failure
- **Fix**: Train product team on self-service dashboards; document everything

## Implementation Checklist

- [ ] Define north star metric and metric hierarchy
- [ ] Create event naming convention document
- [ ] Instrument 20-30 core events across web/mobile
- [ ] Setup analytics tool (Amplitude, Mixpanel, etc.)
- [ ] Validate events in staging before production
- [ ] Setup data warehouse (BigQuery/Snowflake) if at scale
- [ ] Create core metrics dashboard
- [ ] Setup alerting for key anomalies
- [ ] Document all events and metrics
- [ ] Train team on dashboard access and usage
- [ ] Establish weekly metrics review cadence
- [ ] Setup experimentation platform
- [ ] Create data governance and access policy
