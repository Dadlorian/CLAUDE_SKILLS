# Dashboard Patterns - Proven Design Solutions

## Layout Patterns

### 1. The Billboard Pattern
**Use Case:** Executive dashboards, high-level KPIs

**Structure:**
```
┌─────────────────────────────────────────┐
│  Big Number    Big Number    Big Number │
│   ±Change       ±Change       ±Change   │
├─────────────────────────────────────────┤
│                                         │
│         Supporting Trend Chart         │
│                                         │
└─────────────────────────────────────────┘
```

**Characteristics:**
- 3-5 prominent KPIs at top
- Large, readable numbers
- Directional indicators (▲▼)
- Percent or absolute change
- Optional sparkline or trend below each KPI
- Minimal detail, maximum impact

**Best For:**
- C-suite dashboards
- Public displays
- High-level status at a glance

**Stephen Few Principle:** Information scent - immediate recognition of status

### 2. The Quadrant Pattern
**Use Case:** Balanced scorecards, multiple focus areas

**Structure:**
```
┌─────────────┬─────────────┐
│   Finance   │   Customer  │
│   Metrics   │   Metrics   │
├─────────────┼─────────────┤
│  Internal   │   Learning  │
│  Process    │   & Growth  │
└─────────────┴─────────────┘
```

**Characteristics:**
- Equal-sized quadrants
- Thematic grouping
- Each quadrant self-contained
- Often maps to BSC perspectives
- Consistent chart types within quadrants

**Best For:**
- Balanced scorecards
- Multi-departmental views
- Strategic dashboards

### 3. The Waterfall Pattern
**Use Case:** Operational dashboards, monitoring workflows

**Structure:**
```
┌─────────────────────────────────────────┐
│  Critical Alerts (if any)               │
├─────────────────────────────────────────┤
│  High-Priority Metrics                  │
├─────────────────────────────────────────┤
│  Standard Monitoring Metrics            │
├─────────────────────────────────────────┤
│  Detailed Drill-Down Section            │
└─────────────────────────────────────────┘
```

**Characteristics:**
- Vertical priority flow
- Exceptions at top
- Progressive detail disclosure
- Scrolling acceptable (unlike executive)
- Alert-driven design

**Best For:**
- Operations centers
- Real-time monitoring
- Support dashboards

**Tufte Principle:** Small multiples for comparisons

### 4. The Left Panel Pattern
**Use Case:** Analytical dashboards with heavy filtering

**Structure:**
```
┌────┬──────────────────────────┐
│    │                          │
│ F  │   Main Visualization     │
│ I  │                          │
│ L  ├──────────────────────────┤
│ T  │                          │
│ E  │   Supporting Charts      │
│ R  │                          │
│ S  │                          │
└────┴──────────────────────────┘
```

**Characteristics:**
- Fixed left sidebar (150-250px)
- Filters and parameters stacked vertically
- Main content area responsive
- Clear visual separation
- Consistent filter placement

**Best For:**
- Analytical dashboards
- Self-service BI
- Exploration-focused tools

### 5. The Metrics Grid Pattern
**Use Case:** Departmental dashboards, team performance

**Structure:**
```
┌──────┬──────┬──────┬──────┐
│ KPI  │ KPI  │ KPI  │ KPI  │
│ Card │ Card │ Card │ Card │
├──────┼──────┼──────┼──────┤
│ KPI  │ KPI  │ KPI  │ KPI  │
│ Card │ Card │ Card │ Card │
└──────┴──────┴──────┴──────┘
```

**Characteristics:**
- Uniform card sizes
- Each card: metric + context + trend
- Scannable layout
- 2-4 columns typical
- Vertical scrolling for many metrics

**Best For:**
- Tactical dashboards
- Team metrics
- SaaS metrics dashboards

### 6. The Comparison Pattern
**Use Case:** A/B testing, cohort analysis, regional comparisons

**Structure:**
```
┌──────────────┬──────────────┐
│   Region A   │   Region B   │
│              │              │
│   [Chart]    │   [Chart]    │
│              │              │
├──────────────┼──────────────┤
│   Region C   │   Region D   │
│              │              │
│   [Chart]    │   [Chart]    │
│              │              │
└──────────────┴──────────────┘
```

**Characteristics:**
- Identical chart types
- Consistent scales
- Side-by-side or small multiples
- Easy visual comparison
- Shared axes when possible

**Best For:**
- Regional performance
- A/B test results
- Cohort analysis

**Tufte Principle:** Small multiples with consistent design

## Navigation Patterns

### Tab Pattern
**Structure:**
```
┌─────┬─────┬─────┬─────────┐
│ Tab1│ Tab2│ Tab3│         │
├─────┴─────┴─────┴─────────┤
│                            │
│     Tab Content            │
│                            │
└────────────────────────────┘
```

**Use When:**
- Distinct user workflows
- Different user roles
- Thematic grouping

**Best Practices:**
- 3-7 tabs maximum
- Clear, concise labels
- Most important tab first
- Consistent layout across tabs

### Drill-Down Pattern
**Flow:** Overview → Detail → Transaction

**Implementation:**
```
Level 1: Summary metrics
  ↓ Click
Level 2: Category breakdown
  ↓ Click
Level 3: Individual transactions
```

**Best Practices:**
- Maintain context (breadcrumbs)
- Easy return to previous level
- Consistent interaction model
- Maximum 3 levels deep

### Filter-Focus Pattern
**User Flow:**
1. Select filters in sidebar/top
2. All visualizations update
3. Context preserved across views

**Best Practices:**
- Visible filter state
- "Clear all" option
- Filter counts (e.g., "3 filters applied")
- Sticky filter panel

## Interaction Patterns

### Hover for Detail
**Use For:**
- Additional context
- Exact values
- Metadata

**Best Practices:**
- 300-500ms delay before show
- Consistent positioning
- Clear, concise content
- Not for critical information

### Click for Action
**Common Actions:**
- Drill down to detail
- Navigate to related view
- Apply filter
- Open detailed report

**Best Practices:**
- Clear affordance (cursor change)
- Predictable result
- Easy undo/back

### Cross-Filtering
**Pattern:** Click element in one chart filters all other charts

**Best Practices:**
- Visual indication of filter state
- Easy to clear
- Works across all charts
- Performance optimized

### Brush and Zoom
**Pattern:** Select region to zoom in, brush to filter

**Best Practices:**
- Clear selection rectangle
- Easy reset
- Maintain context (overview+detail)
- Use for time-series exploration

## Responsive Patterns

### Mobile-First Dashboard
**Priority Stack:**
```
Mobile (320-768px):
├─ Most critical KPI
├─ Second most critical KPI
├─ Primary trend chart
└─ [Additional content below fold]

Tablet (768-1024px):
├─ Top KPIs in 2-column grid
├─ Primary charts (larger)
└─ Secondary metrics

Desktop (1024px+):
└─ Full layout with all details
```

**Principles:**
- Progressive enhancement
- Content priority ranking
- Touch-friendly targets (44px min)
- Simplified charts on mobile

### Adaptive Visualization Pattern
**Technique:** Change chart type based on screen size

**Example:**
- Desktop: Multi-series line chart
- Tablet: Simplified line chart (fewer series)
- Mobile: Sparklines or single selected series

### Collapsible Sections Pattern
**Structure:**
```
▼ Finance Metrics (expanded)
  └─ [Charts and data]

▶ Operations Metrics (collapsed)

▶ Customer Metrics (collapsed)
```

**Best For:**
- Mobile dashboards
- Long dashboards
- Progressive disclosure

## Data Update Patterns

### Real-Time Update Pattern
**Use Case:** Operations centers, live monitoring

**Implementations:**
- Auto-refresh every N seconds
- WebSocket live updates
- Visual indication of new data
- Pause/resume control

**Best Practices:**
- Don't interrupt user interaction
- Show last update timestamp
- Smooth transitions (not jarring)
- User control over refresh rate

### Scheduled Refresh Pattern
**Use Case:** Daily/weekly reports, batch processing

**Implementation:**
- Display last refresh time
- Next refresh countdown
- Manual refresh button
- Stale data warning

### Incremental Load Pattern
**Use Case:** Large datasets, performance optimization

**Implementation:**
- Load summary first
- Lazy-load details on demand
- Progressive enhancement
- Loading indicators

## Alert Patterns

### Traffic Light Pattern (AVOID - Few/Tufte)
**Problem:** Over-reliance on red/yellow/green

**Better Alternative:**
```
Below target: Show value + gap + subtle orange highlight
At target: Show value (neutral color)
Above target: Show value + overage + subtle blue highlight
```

### Exception Highlight Pattern (RECOMMENDED)
**Philosophy:** Show normal in gray, exceptions in color

**Implementation:**
- Most data points: gray
- Outliers: orange or red
- Targets met/exceeded: subtle blue or green
- Always include numeric context

### Notification Pattern
**Types:**
1. **Persistent Alert** (critical): Stays until dismissed
2. **Toast Notification** (info): Auto-dismisses
3. **Badge Count** (summary): Shows number of issues
4. **Inline Alert** (contextual): Near affected chart

## Performance Patterns

### Progressive Loading
```
1. Show skeleton/placeholder
2. Load summary metrics
3. Load visible charts
4. Lazy-load below-fold content
```

### Aggregation Pattern
**Levels:**
- Summary: Pre-aggregated, fast
- Detail: Load on demand
- Transaction: Only when drilled into

### Caching Strategy
- Client-side cache for static reference data
- Server-side cache for common queries
- Invalidate on data refresh
- Cache summary, not details

## Anti-Patterns to Avoid

### ❌ The Christmas Tree
**Problem:** Too many colors, no hierarchy
**Solution:** Grayscale first, color for emphasis

### ❌ The Chart Junk Gallery
**Problem:** 3D effects, shadows, gradients everywhere
**Solution:** Flat design, high data-ink ratio

### ❌ The Packed Sardine
**Problem:** No white space, cluttered
**Solution:** Generous padding, clear grouping

### ❌ The Rainbow Explosion
**Problem:** Different color scheme for each chart
**Solution:** Consistent palette across dashboard

### ❌ The Scrolling Novel
**Problem:** Requires extensive scrolling
**Solution:** Filter-focus pattern or multi-page dashboard

### ❌ The Pie Chart Parade
**Problem:** Multiple pie charts for comparison
**Solution:** Bar charts or bullet charts

### ❌ The Gauge Gauntlet
**Problem:** Multiple gauge charts wasting space
**Solution:** Bullet charts (Few's recommendation)

### ❌ The 3D Nightmare
**Problem:** 3D charts distorting data perception
**Solution:** 2D charts with clear encoding

## Pattern Selection Matrix

| Dashboard Type | Recommended Pattern | Layout | Navigation |
|----------------|-------------------|---------|------------|
| Executive | Billboard | Horizontal KPIs | Single page |
| Operational | Waterfall | Vertical priority | Scrolling |
| Analytical | Left Panel | Filter + content | Tabs + drill |
| Tactical | Metrics Grid | Card grid | Tabs |
| Balanced Scorecard | Quadrant | 2x2 or 4x1 | Single page |
| Comparison | Small Multiples | Grid | Filters |
| Mobile | Priority Stack | Single column | Collapsible |

## Implementation Checklist

**Layout:**
- [ ] Most important content in top-left
- [ ] Logical grouping with white space
- [ ] Consistent alignment and spacing
- [ ] Z-pattern or F-pattern flow

**Navigation:**
- [ ] Clear, predictable
- [ ] Maximum 3 levels deep
- [ ] Breadcrumbs for context
- [ ] Back/reset options

**Interaction:**
- [ ] Hover states defined
- [ ] Click targets ≥44px on mobile
- [ ] Cross-filtering intuitive
- [ ] Filter state visible

**Performance:**
- [ ] Load time <5 seconds
- [ ] Progressive enhancement
- [ ] Optimized queries
- [ ] Appropriate caching

**Accessibility:**
- [ ] Keyboard navigation
- [ ] Screen reader friendly
- [ ] Sufficient contrast
- [ ] Alternative text for charts

## References
- Stephen Few: "Information Dashboard Design"
- Edward Tufte: "Envisioning Information"
- Cole Nussbaumer Knaflic: "Storytelling with Data"
- Nielsen Norman Group: Dashboard Design Pattern Library
