# Common Dashboard Design Mistakes

## The Big Three (Most Critical Mistakes)

### 1. No Clear Purpose or Audience

**Mistake**: Building a dashboard without knowing who will use it or what decisions it should support.

**Symptoms**:
- "Dashboard for everything and everyone"
- Mixing strategic and operational metrics
- Users don't know what to do with the information

**Example**:
```
❌ BAD: "Company Dashboard"
- Revenue (CEO cares)
- Server uptime (DevOps cares)
- Support tickets (Support cares)
- Marketing spend (CMO cares)
- Code commits (Engineering cares)

Who is this for? What decision does it support?
```

**Solution**:
```
✓ Define audience: Executive team
✓ Define purpose: Monitor company health
✓ Define decision: Investment allocation

✓ GOOD: "Executive Health Dashboard"
- Revenue vs target
- Customer acquisition
- Customer retention
- Profitability
- Cash runway
```

**Pre-Design Questions**:
1. Who is the primary user?
2. What decision does this dashboard support?
3. What action should users take after viewing it?
4. How often will it be viewed?
5. What's the most important metric?

---

### 2. Too Much Information (Chartjunk & Clutter)

**Mistake**: Trying to show everything, resulting in cognitive overload.

**Symptoms**:
- 20+ charts on one page
- Tiny, unreadable charts
- Users say "I can't find anything"
- Requires extensive scrolling

**Example**:
```
❌ BAD Dashboard:
┌─────────────────────────────────┐
│ [Chart][Chart][Chart][Chart]    │
│ [Chart][Chart][Chart][Chart]    │
│ [Chart][Chart][Chart][Chart]    │
│ [Chart][Chart][Chart][Chart]    │
│ [Chart][Chart][Chart][Chart]    │
│ [Chart][Chart][Chart][Chart]    │
│                                 │
│ (25 charts, all small, none     │
│  stand out, information chaos)  │
└─────────────────────────────────┘
```

**Solution (Stephen Few's Rule)**:
- **Executive dashboards**: 5-7 key metrics maximum
- **Operational dashboards**: 10-15 metrics
- **Analytical dashboards**: 15-20 metrics (with drill-down)

**Better**:
```
✓ GOOD Dashboard:
┌─────────────────────────────────┐
│  Revenue: $1.2M (+15%)          │ ← Clear hierarchy
│  [━━━━━━━━━━━━] Trend          │
│                                 │
│  ┌─────────────┬─────────────┐ │
│  │ KPI 2       │ KPI 3       │ │
│  │             │             │ │
│  └─────────────┴─────────────┘ │
│                                 │
│  [Main supporting chart]        │
│                                 │
│  [See detailed analysis →]      │
└─────────────────────────────────┘
```

---

### 3. Misleading Visualizations

**Mistake**: Chart design that distorts perception of data.

**Common Issues**:

**A) Truncated Y-Axis (Exaggerating Differences)**
```
❌ BAD: Y-axis 90-100
     100 ┤     ▄▄
      98 ┤   ▄▄
      96 ┤ ▄▄
      94 ┤▄▄
     Jan Feb Mar Apr

Looks like HUGE growth!

✓ GOOD: Y-axis 0-100
     100 ┤────────────
      75 ┤
      50 ┤
      25 ┤
       0 ┤▬▬▬▬▬▬▬▬▬▬
     Jan Feb Mar Apr

Actual: Minor variation
```

**Exception**: Showing small variations in large numbers (with clear labeling)

**B) 3D Charts (Visual Distortion)**
```
❌ BAD: 3D Pie Chart
    A appears larger due to perspective
    C appears smaller due to foreshortening
    Impossible to compare accurately

✓ GOOD: Simple bar chart
    Clear, accurate comparison
```

**C) Dual-Axis Manipulation**
```
❌ BAD: Two Y-axes with different scales
    making unrelated trends look correlated

✓ GOOD: Separate charts or indexed to common baseline
```

---

## Category-Specific Mistakes

## Visual Design Mistakes

### 4. Poor Color Choices

**A) Christmas Tree Dashboard**
```
❌ Too many bright colors:
- Red bars
- Green lines
- Blue areas
- Yellow highlights
- Purple text

Result: Visual chaos, no clear emphasis
```

**Solution**: Grayscale first, color for emphasis only

**B) Red/Green Color Blindness Ignorance**
```
❌ Red = Bad, Green = Good (no other indicator)
   8% of men cannot distinguish

✓ Red = Bad + ✗ icon + text label
  Green = Good + ✓ icon + text label
```

**C) Insufficient Contrast**
```
❌ Light gray text (#CCCCCC) on white background
   Ratio: 1.6:1 (FAIL)

✓ Dark gray text (#595959) on white background
  Ratio: 7:1 (PASS WCAG AA)
```

### 5. Chartjunk (Tufte's Nemesis)

**Examples**:
```
❌ 3D effects
❌ Drop shadows
❌ Gradient fills
❌ Decorative backgrounds
❌ Clipart and icons (non-functional)
❌ Heavy gridlines
❌ Unnecessary borders
❌ Patterned backgrounds
```

**Impact**: Reduces data-ink ratio, slows comprehension

**Solution**: Remove every non-data element that doesn't add value

### 6. Bad Typography

**A) Too Many Fonts**
```
❌ Title: Arial Bold
   KPI: Georgia
   Labels: Comic Sans (never!)
   Body: Times New Roman

✓ Maximum 2 font families
  Use weight and size for hierarchy
```

**B) Too Small Text**
```
❌ 8px font on dashboard viewed from 2 feet away

✓ Minimum 12px for body text
  14-16px recommended
  Larger for KPI values (32-48px)
```

**C) Poor Hierarchy**
```
❌ All text same size and weight

✓ Clear hierarchy through size and weight:
  Title: 32px, Bold
  KPI Value: 48px, Semi-Bold
  KPI Label: 16px, Regular
  Metadata: 12px, Light
```

## Chart Selection Mistakes

### 7. Wrong Chart for Data Type

**A) Pie Chart for Comparisons**
```
❌ Pie chart with 8 slices
   - Hard to compare angles
   - Labels cluttered
   - Poor space utilization

✓ Horizontal bar chart
  - Easy comparison
  - Clear labels
  - Better use of space
```

**B) Line Chart for Categories**
```
❌ Line chart connecting unrelated categories
   (North → South → East → West)
   Line implies continuous relationship

✓ Bar chart for categorical comparison
```

**C) Bar Chart for Trends**
```
❌ Bar chart for 100 time periods
   - Too many bars
   - Hard to see trend

✓ Line chart for continuous time series
```

**D) Area Chart for Non-Cumulative Data**
```
❌ Area chart for independent categories
   Implies stacking/cumulation

✓ Line chart or bar chart
```

### 8. Too Many Series on One Chart

**Mistake**: Spaghetti chart - 10+ lines on one chart

**Problem**:
- Impossible to distinguish
- Legend required (extra eye movement)
- Cognitive overload

**Solution**:
```
✓ Maximum 4-5 series on one chart
✓ Use small multiples for more series
✓ Allow interactive selection (show/hide series)
```

**Example**:
```
❌ One chart with 12 product lines
   [Tangled mess of lines]

✓ 12 small charts, one per product (small multiples)
   [Clean, easy to compare patterns]
```

### 9. Inappropriate Gauge Charts

**Stephen Few's Position**: Gauge charts waste space

**Problem**:
```
❌ Gauge chart showing 75%
   Takes up 200×200px
   Shows only one number
   Decorative, not functional
```

**Solution**:
```
✓ Bullet chart showing 75%
   Takes up 200×30px
   Shows: actual, target, ranges
   Functional, space-efficient

  75%  ▬▬▬▬▬▬▬▬|▬▬▬▬
       Poor  Good  Exc
       (Target: 80%)
```

**Only Acceptable Gauge Use**:
- Large displays (TV monitors in office)
- Single critical metric
- Glanceable from distance

## Data & Content Mistakes

### 10. Data Without Context

**Mistake**: Showing metric without comparison point

**Example**:
```
❌ Revenue: $1.2M

Questions:
- Is that good or bad?
- Up or down from last period?
- On track for target?
```

**Solution**: Always provide context
```
✓ Revenue: $1.2M
  Target: $1.0M (+20%)
  Last Month: $1.05M (+14%)
  YoY: +15%
  [12-month trend line]
```

**Context Types**:
- vs Target/Goal
- vs Previous Period (MoM, QoQ, YoY)
- vs Benchmark (industry, competitors)
- Trend (improving or declining?)
- Distribution (where does this fall?)

### 11. Precision Overkill

**Mistake**: Showing unnecessary decimal places

**Example**:
```
❌ Revenue: $1,234,567.89
   Makes number harder to read
   False precision (not significant)

✓ Revenue: $1.23M
  Easier to scan and compare
```

**Rules**:
- KPI values: Round to 2-3 significant figures
- Percentages: 1 decimal max (23.5%, not 23.456%)
- Currency: Round to thousands or millions
- Exception: When precision matters (error rates, SLAs)

### 12. Metric Overload

**Mistake**: Showing every possible metric

**Problem**: Users don't know what to focus on

**Solution**: Prioritize ruthlessly
```
Ask for each metric:
1. Does this support a decision?
2. Will action be taken based on this?
3. Is this the best way to show this information?

If no to any: Remove it
```

**Drill-Down Strategy**:
```
Dashboard: 5-7 key metrics
Drill-down 1: 10-15 supporting metrics
Drill-down 2: Detailed analysis
Raw data: Export to CSV
```

## Interaction & UX Mistakes

### 13. Confusing Filters

**A) Hidden Filters**
```
❌ Filters buried in menu
   Users don't know dashboard is filtered
   Wrong conclusions drawn

✓ Filters always visible
  Clear indication of active filters
  Easy to modify or clear
```

**B) Non-Intuitive Filter Behavior**
```
❌ Filters on different pages independent
   Page 1: Filtered to 2024
   Page 2: Shows all years
   Inconsistent, confusing

✓ Global filters affect all pages
  Page-specific filters clearly labeled
```

**C) Filter Overload**
```
❌ 20 filters on left sidebar
   Overwhelming, unclear which to use

✓ 3-5 key filters visible
  "Advanced filters" collapsed
  Smart defaults (e.g., Last 30 days)
```

### 14. Poor Mobile Experience

**Mistake**: Desktop dashboard squeezed onto mobile

**Problems**:
- Tiny, unreadable text
- Charts too small to interpret
- Touch targets too small
- Horizontal scrolling required

**Solution**:
```
✓ Dedicated mobile layout
  Priority-based content
  Simplified charts
  Touch-friendly targets (44px min)
  Vertical scrolling only
```

### 15. No Drill-Down or Too Much Drill-Down

**No Drill-Down**:
```
❌ Summary metrics with no way to investigate
   User sees problem but can't explore
```

**Too Much Drill-Down**:
```
❌ 5+ levels deep to find information
   Lost in navigation
```

**Solution**:
```
✓ 2-3 levels maximum:
  1. Overview (what?)
  2. Detail (why?)
  3. Transaction (who/when?)

✓ Breadcrumbs for navigation
✓ "Back" button always available
```

## Technical Mistakes

### 16. Slow Performance

**Mistake**: Dashboard takes 10+ seconds to load

**Common Causes**:
- Live queries to large tables
- No aggregation
- Too many visuals
- Unoptimized queries
- No caching

**Solution**: See performance_benchmarks.md

**Quick Wins**:
- Use data extracts instead of live
- Aggregate at database level
- Limit to 8-15 visuals per page
- Implement caching
- Add query limits

### 17. No Error Handling

**Mistake**: Dashboard breaks silently or shows cryptic errors

**Problems**:
```
❌ Blank screen (no data, no message)
❌ "Error 500: Internal Server Error"
❌ Dashboard half-loaded with errors
```

**Solution**:
```
✓ Graceful degradation:
  "No data available for selected filters"
  "Data source temporarily unavailable. Last updated: 2:45 PM"

✓ Retry logic for transient errors
✓ Fallback to cached data
✓ Clear error messages (not technical jargon)
```

### 18. No Data Freshness Indicator

**Mistake**: Users don't know if data is current

**Problem**:
```
❌ No timestamp shown
   Is this real-time?
   Is this yesterday's data?
   Is this cached?
```

**Solution**:
```
✓ "Last updated: 2:45 PM"
✓ "Data as of: Dec 31, 2024"
✓ "Refreshes every: 5 minutes"
✓ Live indicator for real-time dashboards
```

## Accessibility Mistakes

### 19. Ignoring Color Blindness

**Mistake**: Using only red/green to convey information

**Problem**: 8% of men cannot distinguish

**Solution**:
```
✓ Color + shape (▲ green, ▼ red)
✓ Color + text ("Above target", "Below target")
✓ Color + icon (✓, ✗, ⚠)
✓ Use color-blind safe palettes
```

### 20. Missing Alt Text & ARIA Labels

**Mistake**: Charts and interactive elements without accessible labels

**Problem**: Screen readers can't interpret

**Solution**:
```html
✓ <div role="img" aria-label="Revenue trend showing 15% growth from Jan to Dec">
✓ <button aria-label="Refresh dashboard data">
✓ Provide data table alternative for complex charts
```

### 21. Keyboard Navigation Impossible

**Mistake**: Dashboard only works with mouse

**Problem**: Excludes keyboard-only users

**Solution**:
```
✓ All interactive elements keyboard-accessible
✓ Logical tab order
✓ Visible focus indicators
✓ Keyboard shortcuts for common actions
```

## Organizational Mistakes

### 22. Dashboard Sprawl

**Mistake**: Creating new dashboard for every request

**Problem**:
- 100+ dashboards
- No one knows which to use
- Duplicated effort
- Inconsistent definitions

**Solution**:
```
✓ Dashboard governance:
  - Approval process for new dashboards
  - Consolidate similar dashboards
  - Deprecate unused dashboards
  - Standard templates
  - Metric definitions catalog
```

### 23. No Documentation

**Mistake**: Complex dashboard with no explanation

**Problem**:
- Users misinterpret metrics
- New users can't get started
- Metric calculation unknown

**Solution**:
```
✓ Metric definitions (hover tooltips)
✓ Getting started guide
✓ Video walkthrough
✓ Calculation explanations
✓ FAQ section
```

### 24. Static Dashboards (No Iteration)

**Mistake**: Build once, never improve

**Problem**:
- User needs change
- Data sources evolve
- Performance degrades
- Dashboards become irrelevant

**Solution**:
```
✓ Regular review cycle (quarterly)
✓ User feedback collection
✓ Usage analytics monitoring
✓ A/B testing for improvements
✓ Deprecation process for unused dashboards
```

## Avoiding These Mistakes

### Pre-Launch Checklist

**Purpose & Audience**:
- [ ] Primary audience clearly defined
- [ ] Decision supported clearly stated
- [ ] Success criteria established

**Visual Design**:
- [ ] Passed grayscale test (hierarchy without color)
- [ ] Color-blind tested
- [ ] Contrast ratios meet WCAG 2.1 AA
- [ ] No chartjunk
- [ ] Clear visual hierarchy

**Data & Content**:
- [ ] All metrics have context (target, comparison)
- [ ] Precision appropriate (no excessive decimals)
- [ ] 5-15 metrics maximum per page
- [ ] Metric definitions clear

**Charts**:
- [ ] Right chart for data type
- [ ] No misleading visualizations
- [ ] Maximum 4-5 series per chart
- [ ] Direct labels (minimal legends)

**Interaction**:
- [ ] Filters intuitive and visible
- [ ] Drill-down logical (max 3 levels)
- [ ] Mobile experience acceptable
- [ ] Load time <5 seconds

**Accessibility**:
- [ ] Keyboard navigable
- [ ] Screen reader friendly
- [ ] Alt text provided
- [ ] Touch targets ≥44px

**Technical**:
- [ ] Data freshness indicated
- [ ] Error handling graceful
- [ ] Performance acceptable
- [ ] Tested across browsers/devices

**Documentation**:
- [ ] Metric definitions available
- [ ] Getting started guide
- [ ] Calculation explanations

---

## Learn from Others' Mistakes

**Before deploying**:
1. Show dashboard to someone unfamiliar
2. Ask: "What's the most important thing here?"
3. Ask: "What action should you take?"
4. Ask: "Is anything confusing?"

If they can't answer easily, iterate.

**After deploying**:
1. Monitor usage analytics
2. Collect user feedback
3. Identify unused charts (remove them)
4. Identify pain points (fix them)

---

## References
- Stephen Few: "Information Dashboard Design" (common mistakes)
- Edward Tufte: "The Visual Display of Quantitative Information" (chartjunk)
- Cole Nussbaumer Knaflic: "Storytelling with Data" (chart selection)
- Nielsen Norman Group: "Dashboard Design Anti-Patterns"
