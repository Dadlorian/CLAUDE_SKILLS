# Dashboard Design Principles (Universal)

## Core Principles

### 1. Know Your Audience
```
Executive Dashboard:
- High-level KPIs
- Trends and exceptions
- Minimal interaction needed
- Mobile-friendly

Manager Dashboard:
- Team performance
- Actionable insights
- Some drill-down capability
- Regular monitoring

Analyst Dashboard:
- Detailed data access
- Full exploration capability
- Export functionality
- Complex filtering
```

### 2. Tell a Story
```
Structure:
1. Context: What are we looking at?
2. Insight: What's happening?
3. Action: What should we do?

Example Flow:
┌─────────────────────────┐
│ Sales Performance       │ ← Context
│ Q4 2024 | All Regions   │
├─────────────────────────┤
│ ⚠ Revenue down 15% YoY  │ ← Insight
│ West region declining   │
├─────────────────────────┤
│ Details: Product Mix    │ ← Deep Dive
│ Changed significantly   │
├─────────────────────────┤
│ Recommended Actions:    │ ← Action
│ - Investigate West      │
│ - Review pricing        │
└─────────────────────────┘
```

### 3. Keep It Simple
```
7±2 Rule:
- 5-9 visualizations per dashboard
- More than 9 = overwhelming
- Less than 5 = underutilized

Cognitive Load:
- Each chart requires mental processing
- Too many charts = analysis paralysis
- Group related information
```

## Layout Principles

### F-Pattern Layout
```
Users scan in F-pattern (eye-tracking studies)

┌─────────────────────────────────┐
│ ➊ KPI | KPI | KPI              │ ← Top row: Most important
├──────────────┬──────────────────┤
│ ➋ Primary    │ ➌ Supporting    │ ← Main content
│   Chart      │   Chart         │
├──────────────┴──────────────────┤
│ ➍ Detail / Trends               │ ← Additional context
└─────────────────────────────────┘

Priority Order:
1. Top-left: Most critical metric
2. Top-center: Key visualization
3. Right: Supporting info
4. Bottom: Details on demand
```

### Responsive Grid
```
Desktop (1920x1080):
┌──────────┬──────────┬──────────┐
│    A     │    B     │    C     │
├──────────┴──────────┴──────────┤
│             D                  │
└────────────────────────────────┘

Tablet (1024x768):
┌──────────┬──────────┐
│    A     │    B     │
├──────────┴──────────┤
│         C           │
├─────────────────────┤
│         D           │
└─────────────────────┘

Mobile (414x896):
┌───────────┐
│     A     │
├───────────┤
│     B     │
├───────────┤
│     C     │
├───────────┤
│     D     │
└───────────┘
```

## Color Strategy

### Purposeful Color Use
```
Semantic Colors:
✓ Green: Positive, on-target, safe
⚠ Yellow/Orange: Warning, attention needed
✗ Red: Negative, off-target, danger

Brand Colors:
- Primary: Headers, key metrics
- Secondary: Supporting elements
- Neutral: Body text, backgrounds

Accessibility (WCAG AA):
- Contrast ratio ≥ 4.5:1 (text)
- Contrast ratio ≥ 3:1 (graphics)
- Don't rely on color alone
- Use patterns/icons with color
```

### Color Palette Examples
```
Sequential (for continuous data):
Light Blue → Dark Blue
0% ━━━━━━━━━━ 100%

Diverging (for variance):
Red ← White → Green
-50% ━ 0% ━ +50%

Categorical (for dimensions):
Blue, Orange, Green, Red, Purple
(Max 5-7 distinct colors)

Avoid:
❌ Rainbow colors (hard to interpret)
❌ Red-Green only (colorblind issues)
❌ Neon colors (eye strain)
```

## Typography

### Hierarchy
```
Dashboard Title: 24-28pt, Bold
Section Header: 18-20pt, Semi-bold
Chart Title: 14-16pt, Medium
Axis Labels: 11-12pt, Regular
Data Labels: 10-11pt, Regular

Font Families:
- Sans-serif for dashboards (cleaner)
- Consistent across all elements
- Max 2 font families

Examples:
✓ Inter, Roboto, Open Sans
✓ Segoe UI (Windows default)
✓ SF Pro (Apple default)
```

## Chart Selection

### Choose the Right Chart
```
Comparison:
├─ Few items (2-7): Bar chart
├─ Many items (>7): Sorted bar, lollipop
└─ Over time: Line chart

Distribution:
├─ Single variable: Histogram
├─ Two variables: Scatter plot
└─ Multiple groups: Box plot

Composition:
├─ Parts of whole: Stacked bar, pie (if 2-5 parts)
├─ Over time: Stacked area
└─ Hierarchy: Treemap, sunburst

Relationship:
├─ Two variables: Scatter plot
├─ Three variables: Bubble chart
└─ Network: Network diagram

Location:
├─ Regional data: Choropleth map
├─ Points: Symbol map
└─ Routes: Flow map
```

### Chart Anti-Patterns
```
❌ Avoid:
- 3D charts (distorts perception)
- Pie charts with >5 slices
- Dual-axis with different scales (misleading)
- Donuts (harder to read than pie)
- Radar charts (difficult to compare)

✓ Instead:
- 2D charts always
- Bar chart or treemap
- Separate charts or consistent scaling
- Simple bar chart
- Small multiples or grouped bar
```

## KPI Design

### Big Number (Single Value)
```
┌───────────────────┐
│ Total Revenue     │ ← Label
│                   │
│   $2.4M          │ ← Value (large, bold)
│   ↑ 12.5%        │ ← Trend indicator
│                   │
│ ▂▄▅▇▆▅▃          │ ← Sparkline (context)
└───────────────────┘

Best for:
- Most important metric
- Quick status check
- Executive dashboards
```

### KPI Card Elements
```
Essential:
- Clear label
- Large value
- Units (if not obvious)

Optional but recommended:
- Trend arrow (↑↓→)
- Percent change
- Comparison (vs target, vs prior period)
- Mini chart (sparkline)
- Color coding (green/red)

Avoid:
- Too many decimal places
- Ambiguous labels
- Missing context
```

## Interactivity

### Progressive Disclosure
```
Level 1: Overview
└─ Click → Level 2: Category Details
    └─ Click → Level 3: Individual Items

Example:
Revenue Dashboard
├─ Click region → Regional breakdown
    ├─ Click store → Store performance
        └─ Click product → Product details

Benefits:
- Reduces initial complexity
- Maintains context
- Supports exploration
```

### Filter Strategy
```
Global Filters (Top):
- Date range
- Geography
- Business unit

Local Filters (Per visual):
- Category-specific
- Metric-specific

Best Practices:
- Default to sensible values
- Show selected values clearly
- Minimize required clicks
- Consider preset views instead
```

## Performance Design

### Limit Data Points
```
Chart Visibility Limits:
Line chart: < 100 points per series
Bar chart: < 20 bars
Scatter: < 1,000 points
Table: < 100 rows (use pagination)

Solutions for more data:
- Increase aggregation level
- Top/Bottom N filter
- Sampling
- Drill-down on demand
```

### Lazy Loading
```
Initial Load:
- Above-the-fold content only
- Essential KPIs

On Scroll/Click:
- Secondary visualizations
- Detail views
- Historical trends

Implementation:
Tableau: Container actions
Power BI: Bookmarks
Looker: Dashboard elements
```

## Mobile Optimization

### Mobile-First Decisions
```
Simplify:
- 1-2 key metrics per screen
- Remove less critical visuals
- Larger touch targets (44×44px)
- Vertical scrolling OK

Avoid on Mobile:
- Complex multi-axis charts
- Small text
- Dense tables
- Hover interactions
- Extensive filtering
```

### Mobile Layout
```
Portrait (Phone):
┌────────┐
│  KPI   │  Full width cards
├────────┤
│  KPI   │
├────────┤
│ Chart  │  One per row
├────────┤
│ Chart  │
└────────┘

Landscape (Tablet):
┌─────────┬─────────┐
│   KPI   │   KPI   │  2-column grid
├─────────┴─────────┤
│      Chart        │
└───────────────────┘
```

## Accessibility

### WCAG Guidelines
```
Perceivable:
☑ Text alternatives for images
☑ Sufficient color contrast
☑ Resizable text
☑ Don't use color alone to convey info

Operable:
☑ Keyboard accessible
☑ No time limits on reading
☑ Descriptive link text

Understandable:
☑ Clear labels
☑ Consistent navigation
☑ Error prevention

Robust:
☑ Valid HTML/code
☑ Screen reader compatible
```

### Implementation
```
Alt Text:
"Bar chart showing sales by region.
West leads with $2.4M, followed by East at $1.8M."

Keyboard Navigation:
- Tab through filters
- Enter to select
- Arrow keys for lists
- Escape to close

Screen Readers:
- Semantic HTML (if web-based)
- ARIA labels
- Data tables with headers
- Form labels
```

## Testing Checklist

### Pre-Release
```
Functionality:
□ All filters work correctly
□ Actions/drill-downs function
□ Calculations are accurate
□ Data refreshes properly

Performance:
□ Loads < 5 seconds
□ Interactions smooth
□ No errors or timeouts

Design:
□ Readable on target devices
□ Color contrast sufficient
□ Consistent formatting
□ No overlapping elements

Content:
□ Titles clear and descriptive
□ Units shown where needed
□ Tooltips helpful
□ No typos
```

### User Testing
```
Questions:
1. Can you find [metric]?
2. What stands out to you?
3. What would you do next?
4. Is anything confusing?
5. Can you find more detail on [topic]?

Observe:
- Time to find information
- Incorrect interpretations
- Unused features
- Pain points
```

## Common Mistakes

### Data Viz Sins
```
❌ Truncated Y-axis
→ Exaggerates differences
✓ Start at zero (or break axis clearly)

❌ Too many colors
→ Confusing, overwhelming
✓ Limit to 5-7 max

❌ Pie chart with 10 slices
→ Hard to compare
✓ Bar chart instead

❌ 3D effects
→ Distorts perception
✓ 2D always

❌ Dual axis with different scales
→ Misleading comparisons
✓ Separate charts or same scale

❌ Chartjunk
→ Distracts from data
✓ Minimize non-data ink
```

## Templates & Patterns

### Executive Dashboard Template
```
┌─────────────────────────────────────────┐
│ Company Logo    Q4 2024    Refresh: Now │
├─────────────┬──────────┬────────────────┤
│  Revenue    │  Orders  │   Customers    │
│  $2.4M ↑15% │  1.2K ↑8%│   450 ↑12%    │
├─────────────┴──────────┴────────────────┤
│ Revenue Trend (Last 12 Months)          │
│ ▁▂▃▄▅▆▇█▇▆▅▄                           │
├─────────────────────────────────────────┤
│ Top Products        │ Regional Split    │
│ 1. Product A  $500K │ [Map Viz]        │
│ 2. Product B  $400K │                  │
│ 3. Product C  $350K │                  │
└─────────────────────────────────────────┘
```

### Operational Dashboard Template
```
┌─────────────────────────────────────────┐
│ Filters: [Date Range] [Region] [Status] │
├────────────────┬────────────────────────┤
│ Key Metrics    │  Today's Activity      │
│ - Orders: 150  │  [Real-time Chart]     │
│ - Shipped: 120 │                        │
│ - Pending: 30  │                        │
├────────────────┴────────────────────────┤
│ Detailed Table                          │
│ [Sortable, filterable, exportable]      │
└─────────────────────────────────────────┘
```

## Resources

### Inspiration
- Tableau Public: https://public.tableau.com/gallery
- Power BI Showcase: https://community.powerbi.com/
- Information is Beautiful: https://informationisbeautiful.net/

### Books
- "The Visual Display of Quantitative Information" - Edward Tufte
- "Storytelling with Data" - Cole Nussbaumer Knaflic
- "Dashboard Confessions" - Steve Wexler

### Guidelines
- Microsoft Fluent Design: https://www.microsoft.com/design/fluent/
- Apple HIG: https://developer.apple.com/design/
- Material Design: https://material.io/design
