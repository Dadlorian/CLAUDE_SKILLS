# Documentation Analytics Tools

## Overview
Comprehensive guide to selecting, implementing, and optimizing analytics tools for technical documentation tracking. Covers major platforms, integration approaches, and metrics collection strategies.

---

## 1. Google Analytics 4 (GA4)

### 1.1 Overview
GA4 is a comprehensive analytics platform offering free tier with detailed event tracking.

**Strengths:**
- Free tier: 1 million hits/month
- Event-based data model
- Advanced segmentation
- Excellent for traffic analysis
- Integrates with Google ecosystem

**Limitations:**
- Limited real-time data (90-minute delay)
- Complex custom event setup
- Documentation-specific features minimal

### 1.2 Implementation

**Setup Steps:**
```bash
1. Create Google Analytics property for documentation domain
2. Add GA4 tracking code to documentation site
3. Configure custom events for doc-specific actions
```

**Key Events to Track:**
```javascript
// Page view (automatic)
// Custom events
gtag('event', 'page_helpful', {
  'page_path': document.location.pathname,
  'rating': 'helpful'
});

gtag('event', 'documentation_search', {
  'search_query': query,
  'results_count': resultsCount
});

gtag('event', 'code_copy', {
  'code_snippet_id': snippetId,
  'language': programmingLanguage
});

gtag('event', 'feedback_submitted', {
  'feedback_type': 'bug_report',
  'topic': documentTopic
});
```

### 1.3 Key Metrics & Reports

**Traffic Reports:**
- Realtime: Current active users
- Users: New vs returning
- Sessions: Session duration, bounce rate
- Pages & Screens: Most visited pages
- Landing pages: Entry points

**Engagement Reports:**
- Events: Custom event tracking
- Conversions: Goal completions
- Content groups: Category performance
- Scroll depth: How far users read

**Retention Reports:**
- Returning user patterns
- User retention curves
- Cohort analysis

### 1.4 Custom Metrics Setup

**Create User-Defined Conversion:**
```
Event name: page_helpful
Mark as conversion: Yes
```

**Create Custom Dimension:**
```
Parameter name: doc_category
Scope: Event
Example values: api, tutorial, troubleshooting
```

### 1.5 Data Analysis

**SQL Query Examples:**
```sql
-- Top 20 pages by views
SELECT
  page_title,
  COUNT(*) as page_views,
  COUNT(DISTINCT user_id) as unique_users
FROM `project.dataset.events_*`
WHERE event_name = 'page_view'
GROUP BY page_title
ORDER BY page_views DESC
LIMIT 20;

-- Page helpfulness rate
SELECT
  page_path,
  COUNTIF(event_name = 'page_helpful') as helpful,
  COUNTIF(event_name = 'page_not_helpful') as not_helpful,
  ROUND(COUNTIF(event_name = 'page_helpful') /
    (COUNTIF(event_name IN ('page_helpful', 'page_not_helpful')) + 0.0001) * 100, 2) as helpful_rate
FROM `project.dataset.events_*`
WHERE event_date >= FORMAT_DATE('%Y%m%d', CURRENT_DATE() - 30)
GROUP BY page_path
ORDER BY helpful_rate DESC;
```

### 1.6 Pricing
- Free: $0/month, 1M hits/month
- GA360: $150K+/year (enterprise)

---

## 2. Amplitude

### 2.1 Overview
Product analytics platform optimized for user behavior and engagement tracking.

**Strengths:**
- Event-based analytics
- User cohort analysis
- Funnel analysis
- Retention curves
- Behavioral segmentation
- Excellent documentation dashboards

**Limitations:**
- Minimum $4,995/year (SaaS)
- Learning curve steeper than GA4
- Requires developer integration

### 2.2 Implementation

**Installation:**
```javascript
// Initialize Amplitude
amplitude.getInstance().init("API_KEY");

// Track documentation page view
amplitude.getInstance().logEvent('doc_page_viewed', {
  page_title: document.title,
  page_path: window.location.pathname,
  doc_category: 'api',
  doc_topic: 'authentication'
});

// Track search action
amplitude.getInstance().logEvent('doc_search', {
  query: searchQuery,
  results_count: results.length,
  selected_result: selectedIndex,
  time_to_click: 5000 // ms
});

// Track helpful rating
amplitude.getInstance().logEvent('doc_rating', {
  rating: 'helpful', // or 'not_helpful'
  page_path: currentPage,
  improvement_suggestion: userComment
});

// Track code snippet interaction
amplitude.getInstance().logEvent('code_snippet_interaction', {
  action: 'copy', // or 'expand', 'run'
  language: 'python',
  snippet_id: 'auth_example_001'
});
```

### 2.3 Key Metrics & Features

**Engagement Analysis:**
- User timeline: Event sequence for individual users
- Funnel analysis: Multi-step user journeys
- Retention curves: How many users return daily/weekly
- Cohort comparison: Segment-to-segment analysis

**Documentation-Specific Dashboards:**

**Dashboard 1: Content Performance**
```
Metric: doc_page_viewed
Segmented by: doc_category, doc_topic
Trend: Day-over-day views
Compare: This week vs last week
```

**Dashboard 2: Engagement Funnel**
```
Step 1: doc_page_viewed
Step 2: code_snippet_interaction (action = 'copy')
Step 3: doc_rating (rating = 'helpful')
Conversion: Step 1 → Step 3
```

**Dashboard 3: Search Effectiveness**
```
Event: doc_search
Metrics:
  - Avg results per search
  - Avg time to click result
  - Search to view conversion
Segmented by: query topic, user type
```

### 2.4 Advanced Features

**User Profiles:**
- Total sessions
- First seen / last seen
- Events per session
- Custom properties (user_type, account_tier)

**Revenue Attribution:**
- Track conversion events
- Attribute revenue to content
- Calculate customer lifetime value

**Predictive Analytics:**
- Churn prediction
- Users at risk of churn
- High-value user identification

### 2.5 Pricing
- Growth: $4,995/year (up to 10M events)
- Plus: $9,995/year (up to 100M events)
- Enterprise: Custom pricing

---

## 3. Heap

### 3.1 Overview
Automatic event capture analytics - tracks all user interactions without code.

**Strengths:**
- Automatic event tracking (no code required)
- Retroactive data analysis
- Session replay capability
- Privacy-compliant
- Easy implementation

**Limitations:**
- Higher cost than GA4
- Less flexible event customization
- Smaller documentation-focused community

### 3.2 Implementation

**Installation:**
```html
<!-- Add single snippet to documentation site -->
<script type="text/javascript">
  window.heap=window.heap||[],heap.load=function(e,t){window.heap.appid=e,window.heap.config=t=t||{};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){return function(){heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)window[p[o]]=n(p[o])};
  heap.load("YOUR_APP_ID");
</script>
```

**Custom Event Tracking (Optional):**
```javascript
// Track specific documentation events
heap.track('doc_feedback_submitted', {
  page_title: document.title,
  rating: 'helpful',
  comment_length: feedbackText.length
});

heap.addUserProperties({
  doc_user_type: 'engineer',
  doc_experience_level: 'intermediate',
  company: 'acme_corp'
});
```

### 3.3 Key Analytics Features

**Session Replay:**
- Watch actual user interactions
- Identify usability issues
- See where users struggle
- Review failed searches

**Heatmaps:**
- Click patterns
- Scroll depth visualization
- Mobile vs desktop differences

**Segmentation:**
- By device type
- By user properties
- By behavioral patterns
- By traffic source

### 3.4 Documentation-Specific Setup

**Events to Capture:**
```
Automatic captures:
- All page views
- All clicks
- All form submissions
- Search inputs

Custom events:
- doc_search_completed
- rating_submitted
- code_copied
- external_link_clicked
- example_run_clicked
```

### 3.5 Pricing
- Growth: Starts at $10K+/year
- Plus: Custom enterprise pricing

---

## 4. ReadMe Analytics

### 4.1 Overview
Native analytics for ReadMe-hosted documentation (popular for API docs).

**Strengths:**
- Built into ReadMe platform
- Native search analytics
- API documentation specific
- Usage tracking built-in
- No additional setup needed

**Limitations:**
- Only for ReadMe users
- Limited if not using ReadMe
- Integrations required for advanced features

### 4.2 Native Metrics

**Dashboard Metrics:**
- Page views
- Unique visitors
- Search analytics
- Search success rates
- API request success rates
- Error documentation correlation

**Visitor Analytics:**
```
Track:
- Total visitors
- New vs returning
- Traffic sources
- Geographic distribution
- Device types
```

**Content Performance:**
```
For each page:
- Views
- Unique visitors
- Avg time on page
- Bounce rate
- Helpful rating
- Search queries leading to page
```

### 4.3 Search Analytics

**Search Metrics:**
```
Tracked:
- Search volume
- Top search queries
- Search click-through rate
- Queries with no results
- Most-clicked results
- Bounce rate from search
```

**Search Improvements:**
```
Actions:
- Identify gaps (no results queries)
- Optimize for top queries
- Merge duplicate results
- Improve search ranking
- Add missing content
```

### 4.4 Integration with External Tools

**SendGrid Integration:**
```
Track API request rates
Correlate docs with email deliverability
Monitor spike in doc visits after outages
```

**GitHub Integration:**
```
Sync docs with repo
Track versions
Link to code examples
```

### 4.5 Pricing
- Free: $0 for ReadMe hosted docs (basic analytics)
- Pro: $89+/month (advanced analytics)
- Enterprise: Custom pricing

---

## 5. Mixpanel

### 5.1 Overview
Advanced product analytics focused on user behavior and retention.

**Strengths:**
- Powerful funnel analysis
- Retention curves
- User cohorts
- Advanced segmentation
- Excellent for SaaS

**Limitations:**
- Complex interface
- Requires implementation planning
- Higher learning curve

### 5.2 Documentation Implementation

**Code Example:**
```javascript
// Initialize Mixpanel
mixpanel.init("TOKEN");

// Track page view
mixpanel.track('doc_viewed', {
  'page_title': document.title,
  'doc_category': 'api',
  'doc_version': '2.0',
  'user_experience': 'intermediate'
});

// Track search
mixpanel.track('search_performed', {
  'query': searchTerm,
  'results_count': results.length,
  'search_time_ms': searchDuration
});

// Create user profile
mixpanel.identify(userId);
mixpanel.people.set({
  '$email': userEmail,
  'documentation_user': true,
  'docs_visited': 15,
  'total_time_on_docs': 3600
});
```

### 5.3 Key Dashboards

**Dashboard 1: Feature Adoption**
```
Event: code_example_copied
Funnel: View → Copy → Implement
Retention: Days to implementation
```

**Dashboard 2: Engagement Tracking**
```
Metric: Pages viewed per user
Cohort: By signup date
Trend: Month-over-month
```

### 5.4 Pricing
- Free: Up to 1000 data points/month
- Growth: $999+/month
- Enterprise: Custom pricing

---

## 6. Implementation Comparison Matrix

| Feature | GA4 | Amplitude | Heap | ReadMe | Mixpanel |
|---------|-----|-----------|------|--------|----------|
| **Cost** | Free | $5K+/yr | $10K+/yr | Free-Pro | Free-$999+/mo |
| **Setup Time** | Minutes | Hours | Minutes | Instant | Hours |
| **Event Tracking** | Manual | Manual | Automatic | Auto (ReadMe) | Manual |
| **Funnel Analysis** | Good | Excellent | Good | Basic | Excellent |
| **Retention Curves** | Basic | Excellent | Good | Basic | Excellent |
| **Session Replay** | No | No | Yes | No | No |
| **Search Analytics** | Basic | Basic | Yes | Excellent | Basic |
| **API Documentation** | General | General | General | Specialized | General |
| **Documentation Guides** | Limited | Limited | Limited | Excellent | Limited |

---

## 7. Multi-Tool Strategy

### 7.1 Recommended Stack by Organization Size

**Startups (< $5M revenue):**
```
Primary: Google Analytics 4 (Free)
Secondary: ReadMe Analytics (if using ReadMe)
Optional: Heap (if budget allows)
```

**Growth Stage ($5M-$100M revenue):**
```
Primary: Amplitude ($5K/year)
Secondary: GA4 (supplemental)
Tertiary: Heap (session replay)
Specialized: ReadMe (if applicable)
```

**Enterprise (> $100M revenue):**
```
Primary: Mixpanel or Amplitude
Secondary: GA360
Tertiary: Heap
Specialized: ReadMe or custom solution
Internal: Custom data warehouse
```

### 7.2 Integration Architecture

```
┌─────────────────────────────────────┐
│   Documentation Site                │
├─────────────────────────────────────┤
│  Analytics Event Collection Layer   │
├─────────────────────────────────────┤
│  GA4    Amplitude    Heap    Custom  │
├─────────────────────────────────────┤
│  Data Warehouse / Lake              │
│  (BigQuery, Snowflake, etc)         │
├─────────────────────────────────────┤
│  Analysis Layer                     │
│  (BI Tools, Dashboards)             │
└─────────────────────────────────────┘
```

### 7.3 Data Pipeline Example

**Collect:**
```
- Event triggered on doc page
- SDK captures event data
- Event sent to collection endpoint
```

**Process:**
```
- Validate event schema
- Add server-side context
- Enrich with user data
- Store in data warehouse
```

**Analyze:**
```
- Query warehouse for insights
- Build dashboards
- Generate reports
- Alert on anomalies
```

---

## 8. Privacy & Compliance

### 8.1 GDPR Compliance

**Actions Required:**
- Anonymize personal data
- Get explicit consent
- Implement data retention policies
- Provide data export capability
- Right to deletion

**Tool Compliance:**
- GA4: Privacy-mode available
- Amplitude: GDPR features built-in
- Heap: Privacy-compliant by default
- ReadMe: GDPR compliant

### 8.2 Data Retention Policies

**Recommended Timeline:**
```
Raw events: 90 days
Aggregated data: 24 months
User profiles: Delete on request
PII: Minimum necessary, pseudonymized
```

---

## 9. Implementation Checklist

### Phase 1: Planning
- [ ] Define KPIs
- [ ] Choose primary tool
- [ ] Plan integration
- [ ] Set up property/app
- [ ] Create data schema

### Phase 2: Implementation
- [ ] Install tracking code
- [ ] Implement custom events
- [ ] Test event tracking
- [ ] Validate data quality
- [ ] Set up data export

### Phase 3: Analysis
- [ ] Create dashboards
- [ ] Set up alerts
- [ ] Train team
- [ ] Document processes
- [ ] Schedule reviews

### Phase 4: Optimization
- [ ] Analyze baseline metrics
- [ ] Identify improvement areas
- [ ] A/B test changes
- [ ] Iterate based on data
- [ ] Update roadmap

---

## 10. Troubleshooting Common Issues

**Issue: No events tracking**
```
Solutions:
1. Verify tracking code installed
2. Check event names match configuration
3. Verify network requests sent
4. Check browser console for errors
5. Whitelist analytics domain
```

**Issue: Inaccurate data**
```
Solutions:
1. Check event deduplication
2. Verify user ID consistency
3. Review data validation rules
4. Check for bot traffic filtering
5. Validate timestamp synchronization
```

**Issue: Query timeouts**
```
Solutions:
1. Reduce date range
2. Add more specific filters
3. Pre-aggregate data
4. Use sampled data
5. Consult tool support
```

---

## References
- Google Analytics 4 Documentation
- Amplitude Analytics Guides
- Heap Analytics Docs
- ReadMe API Documentation
- Mixpanel Documentation
