# Dashboard Layout Templates

## Grid Systems for Dashboards

### 12-Column Grid (Standard)
Most flexible, industry standard for responsive design

```
┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
│1│2│3│4│5│6│7│8│9│10│11│12│
└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘

Full width:  12 columns
Half:        6 columns
Third:       4 columns
Quarter:     3 columns
```

### 16-Column Grid (High Precision)
For complex, data-dense dashboards

### 8-Column Grid (Simplified)
For mobile-first or simpler dashboards

---

## Executive Dashboard Templates

### Template 1: KPI Hero Layout

**Use Case:** C-suite, high-level monitoring
**Focus:** 3-5 critical metrics with minimal detail

```
┌────────────────────────────────────────────────────────┐
│  Dashboard Title                         Last Update   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────┬─────────────┬─────────────┐        │
│  │   KPI #1    │   KPI #2    │   KPI #3    │        │
│  │             │             │             │        │
│  │   $1.2M     │    89%      │   1,234     │        │
│  │   +15% ▲    │   +3% ▲     │   -5% ▼     │        │
│  │ [Sparkline] │ [Sparkline] │ [Sparkline] │        │
│  └─────────────┴─────────────┴─────────────┘        │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │                                              │    │
│  │        Primary Trend Chart                   │    │
│  │        (12-month revenue trend)              │    │
│  │                                              │    │
│  │        [Line chart - clean, minimal]         │    │
│  │                                              │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌─────────────────┬──────────────────┐              │
│  │  Supporting     │   Supporting     │              │
│  │  Metric/Chart   │   Metric/Chart   │              │
│  └─────────────────┴──────────────────┘              │
│                                                        │
└────────────────────────────────────────────────────────┘

Grid Layout:
- Header: 12 columns
- KPIs: 4 columns each (3 total)
- Main chart: 12 columns
- Supporting: 6 columns each (2 total)
```

**CSS Grid:**
```css
.executive-dashboard {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  padding: 24px;
}

.header {
  grid-column: 1 / -1;
}

.kpi {
  grid-column: span 4;
}

.main-chart {
  grid-column: 1 / -1;
  min-height: 400px;
}

.supporting {
  grid-column: span 6;
}
```

### Template 2: Balanced Scorecard

**Use Case:** Strategic management, multi-perspective view

```
┌────────────────────────────────────────────────────────┐
│  Balanced Scorecard - Q4 2024                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │   FINANCIAL         │   CUSTOMER           │      │
│  │                     │                      │      │
│  │  Revenue: $1.2M     │  NPS: 45             │      │
│  │  [Bullet chart]     │  [Gauge chart]       │      │
│  │                     │                      │      │
│  │  Profit: 23%        │  CSAT: 4.5/5         │      │
│  │  [Bullet chart]     │  [Star rating]       │      │
│  │                     │                      │      │
│  │  ROI: 18%           │  Retention: 94%      │      │
│  │  [Bullet chart]     │  [Bullet chart]      │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │   INTERNAL PROCESS  │   LEARNING & GROWTH  │      │
│  │                     │                      │      │
│  │  Cycle Time: 12d    │  Training: 40hrs     │      │
│  │  [Trend line]       │  [Progress bar]      │      │
│  │                     │                      │      │
│  │  Quality: 99.2%     │  Satisfaction: 87%   │      │
│  │  [Bullet chart]     │  [Bullet chart]      │      │
│  │                     │                      │      │
│  │  Efficiency: 85%    │  Innovation: 12      │      │
│  │  [Bullet chart]     │  [Count + trend]     │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
└────────────────────────────────────────────────────────┘

Grid Layout:
- Each quadrant: 6 columns
- Equal visual weight
- 3 KPIs per quadrant
```

---

## Operational Dashboard Templates

### Template 3: Operations Center

**Use Case:** Real-time monitoring, alert-driven
**Focus:** Current status, exceptions, drill-down

```
┌────────────────────────────────────────────────────────┐
│  Operations Dashboard            🔴 2 Alerts   [⟳ Live]│
├────────────────────────────────────────────────────────┤
│                                                        │
│  ⚠️  ACTIVE ALERTS                                     │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 🔴 Server response time >500ms (Last 5 min)      │ │
│  │ 🟠 Error rate 2.3% (Threshold: 2%)               │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  REAL-TIME METRICS                                     │
│  ┌────────┬────────┬────────┬────────┬────────┐      │
│  │Uptime  │Response│Requests│Errors  │Active  │      │
│  │99.98%  │234ms   │1.2K/s  │0.8%    │Users   │      │
│  │[Green] │[Green] │[Chart] │[Orange]│2,345   │      │
│  └────────┴────────┴────────┴────────┴────────┘      │
│                                                        │
│  MONITORING CHARTS                                     │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Response Time      │   Error Rate         │      │
│  │  (Last Hour)        │   (Last Hour)        │      │
│  │                     │                      │      │
│  │  [Time series]      │   [Time series]      │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Traffic by Region  │   Top Errors         │      │
│  │                     │                      │      │
│  │  [Horizontal bars]  │   [Table]            │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
└────────────────────────────────────────────────────────┘

Priority Hierarchy:
1. Alerts (top, attention-grabbing)
2. Real-time KPIs (quick scan)
3. Trend charts (context)
4. Detailed breakdown (drill-down)
```

### Template 4: Support Dashboard

**Use Case:** Customer support team monitoring

```
┌────────────────────────────────────────────────────────┐
│  Support Dashboard - Today           [Filters ▾]       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  CURRENT STATUS                                        │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐        │
│  │Open  │In    │First │Avg   │CSAT  │SLA   │        │
│  │      │Prog  │Resp. │Resol.│      │Met   │        │
│  │ 23   │ 45   │12min │2.3hr │4.5/5 │94%   │        │
│  │[Red] │[~]   │[✓]   │[✓]   │[✓]   │[~]   │        │
│  └──────┴──────┴──────┴──────┴──────┴──────┘        │
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Ticket Volume      │   Resolution Time    │      │
│  │  (Last 7 Days)      │   Distribution       │      │
│  │                     │                      │      │
│  │  [Area chart]       │   [Histogram]        │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Tickets by         │   Agent Performance  │      │
│  │  Category           │                      │      │
│  │                     │                      │      │
│  │  [Horizontal bars]  │   [Table with        │      │
│  │                     │    sparklines]       │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  OPEN TICKETS (High Priority)                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ #1234 | Customer A | Login issue | 2h open       │ │
│  │ #1235 | Customer B | Billing     | 45m open      │ │
│  │ #1236 | Customer C | Bug report  | 1h open       │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Analytical Dashboard Templates

### Template 5: Left-Panel Filter Layout

**Use Case:** Self-service analysis, data exploration
**Focus:** Filtering and drilling down

```
┌────┬───────────────────────────────────────────────────┐
│    │  Sales Analysis Dashboard                        │
│ F  ├───────────────────────────────────────────────────┤
│ I  │                                                   │
│ L  │  ┌────────┬────────┬────────┬────────┐          │
│ T  │  │Revenue │ Margin │Customers│ AOV   │          │
│ E  │  │$1.2M   │ 23%    │ 1,234  │ $975  │          │
│ R  │  └────────┴────────┴────────┴────────┘          │
│ S  │                                                   │
│    │  ┌──────────────────────────────────────┐        │
│ 📅 │  │  Revenue Trend (Filtered Data)       │        │
│ Date│  │                                      │        │
│    │  │  [Interactive line chart]            │        │
│ 🌍 │  │                                      │        │
│ Reg.│  │                                      │        │
│    │  └──────────────────────────────────────┘        │
│ 📦 │                                                   │
│ Prod│  ┌────────────────┬─────────────────┐          │
│    │  │  Sales by      │  Top Products   │          │
│ 👥 │  │  Region        │                 │          │
│ Seg.│  │                │                 │          │
│    │  │  [Map/Bars]    │  [Table]        │          │
│ 💰 │  │                │                 │          │
│ Range│  │                │                 │          │
│    │  └────────────────┴─────────────────┘          │
│    │                                                   │
│ [Apply]                                               │
│ [Clear]                                               │
│    │                                                   │
└────┴───────────────────────────────────────────────────┘

Left Panel: 2-3 columns (fixed width 200-300px)
Main Area: 9-10 columns (flexible)
```

**HTML Structure:**
```html
<div class="analytical-dashboard">
  <aside class="filter-panel">
    <!-- Filters -->
  </aside>
  <main class="dashboard-content">
    <!-- KPIs and charts -->
  </main>
</div>
```

### Template 6: Metrics Grid (Product Analytics)

**Use Case:** Product metrics, SaaS dashboards

```
┌────────────────────────────────────────────────────────┐
│  Product Metrics - December 2024      [Export ⬇]      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┬──────────┬──────────┬──────────┐      │
│  │  DAU     │  MAU     │  WAU/MAU │  Stickiness│    │
│  │          │          │          │          │      │
│  │  12,345  │  45,678  │  23,456  │  27%     │      │
│  │  +8% ▲   │  +12% ▲  │  +5% ▲   │  +2% ▲   │      │
│  │ [Trend]  │ [Trend]  │ [Trend]  │ [Trend]  │      │
│  └──────────┴──────────┴──────────┴──────────┘      │
│                                                        │
│  ┌──────────┬──────────┬──────────┬──────────┐      │
│  │  New     │  Churn   │  MRR     │  NRR     │      │
│  │  Users   │  Rate    │          │          │      │
│  │  1,234   │  2.3%    │  $89K    │  105%    │      │
│  │  +15% ▲  │  -0.5%▼  │  +18% ▲  │  +3% ▲   │      │
│  │ [Trend]  │ [Trend]  │ [Trend]  │ [Trend]  │      │
│  └──────────┴──────────┴──────────┴──────────┘      │
│                                                        │
│  ┌──────────┬──────────┬──────────┬──────────┐      │
│  │  Avg     │  Feature │  API     │  Support │      │
│  │  Session │  Adoption│  Calls   │  Tickets │      │
│  │  8.5 min │  67%     │  1.2M    │  23      │      │
│  │  +1.2 ▲  │  +5% ▲   │  +8% ▲   │  -12% ▼  │      │
│  │ [Trend]  │ [Trend]  │ [Trend]  │ [Trend]  │      │
│  └──────────┴──────────┴──────────┴──────────┘      │
│                                                        │
│  DETAILED ANALYSIS                                     │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  User Growth        │   Cohort Retention   │      │
│  │  (6 Months)         │   (12 Weeks)         │      │
│  │                     │                      │      │
│  │  [Stacked area]     │   [Cohort heatmap]   │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
└────────────────────────────────────────────────────────┘

Grid: 4 columns × 3 rows of KPI cards
Each card: 3 columns wide
```

---

## Specialized Templates

### Template 7: Financial Dashboard

```
┌────────────────────────────────────────────────────────┐
│  Financial Dashboard - Q4 2024         [Print] [Export]│
├────────────────────────────────────────────────────────┤
│                                                        │
│  EXECUTIVE SUMMARY                                     │
│  ┌────────┬────────┬────────┬────────┬────────┐      │
│  │Revenue │ COGS   │ Gross  │EBITDA  │ Net    │      │
│  │        │        │ Margin │        │ Income │      │
│  │$1.2M   │$480K   │ 60%    │$240K   │ $180K  │      │
│  │+15% ▲  │+10% ▲  │ +3% ▲  │+20% ▲  │ +25% ▲ │      │
│  └────────┴────────┴────────┴────────┴────────┘      │
│                                                        │
│  REVENUE ANALYSIS                                      │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Revenue Waterfall  │  Revenue by Segment  │      │
│  │  (Q3 → Q4)          │                      │      │
│  │                     │                      │      │
│  │  [Waterfall chart]  │  [Stacked bar]       │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  PROFITABILITY                                         │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Margin Trend       │  Expense Breakdown   │      │
│  │  (12 Months)        │  (Current Quarter)   │      │
│  │                     │                      │      │
│  │  [Line chart with   │  [Treemap or         │      │
│  │   target band]      │   horizontal bars]   │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  CASH FLOW                                             │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Operating │  Investing |  Financing | Ending    │ │
│  │  +$500K    │  -$200K    │  +$100K    | $1.2M     │ │
│  │  [Waterfall showing cash flow]                   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Template 8: Sales Pipeline Dashboard

```
┌────────────────────────────────────────────────────────┐
│  Sales Pipeline - December 2024        [By Rep ▾]     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PIPELINE OVERVIEW                                     │
│  ┌────────┬────────┬────────┬────────┬────────┐      │
│  │Total   │Weighted│Win Rate│Avg Deal│ Cycle  │      │
│  │Pipeline│Value   │        │ Size   │ Length │      │
│  │$5.2M   │$2.1M   │ 28%    │ $45K   │ 45 days│      │
│  │+12% ▲  │+8% ▲   │ +3% ▲  │ +5% ▲  │ -3 days│      │
│  └────────┴────────┴────────┴────────┴────────┘      │
│                                                        │
│  PIPELINE STAGES                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Lead  │Qualified│Proposal│Negotiation│Closed-Won│ │
│  │       │         │        │           │          │ │
│  │ $2.0M │  $1.5M  │ $800K  │   $600K   │  $300K   │ │
│  │  40   │   30    │   18   │    12     │    6     │ │
│  │       │         │        │           │          │ │
│  │ [Funnel chart with conversion rates]             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Pipeline by        │  Top Opportunities   │      │
│  │  Product Line       │  (Close This Month)  │      │
│  │                     │                      │      │
│  │  [Stacked bars]     │  [Table with deal    │      │
│  │                     │   details]           │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
│  ┌─────────────────────┬──────────────────────┐      │
│  │  Pipeline Velocity  │  Rep Performance     │      │
│  │  (Last 6 Months)    │  (This Month)        │      │
│  │                     │                      │      │
│  │  [Trend lines]      │  [Horizontal bars    │      │
│  │                     │   with targets]      │      │
│  │                     │                      │      │
│  └─────────────────────┴──────────────────────┘      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

### Desktop (1920×1080)
- 12-column grid
- Full feature set
- Multiple charts visible
- Generous white space

### Laptop (1366×768)
- 12-column grid (narrower)
- Slightly reduced spacing
- All features available
- Consider vertical scroll

### Tablet Landscape (1024×768)
- 8-10 column grid
- Simplified charts
- Possible tabs for sections
- Touch-optimized

### Tablet Portrait (768×1024)
- 4-6 column grid
- Stacked layout
- Simplified interactions
- Vertical scroll expected

### Mobile (375×667)
- Single column
- KPIs stacked
- Simplified charts or sparklines
- Priority-based content

---

## Layout Best Practices

### Visual Hierarchy
1. **Most important**: Top-left (F-pattern, Z-pattern)
2. **Supporting**: Center and right
3. **Detailed**: Bottom (scrollable)

### Spacing
```
Container padding:   24-32px
Between sections:    32-48px
Between cards:       16-24px
Within cards:        12-16px
```

### Card Design
```
┌─────────────────────────┐
│ Title              🔧  │  ← Header (action icons)
├─────────────────────────┤
│                         │
│   Content               │  ← Body
│   (chart/metric)        │
│                         │
├─────────────────────────┤
│ Last updated: 2:45 PM   │  ← Footer (metadata)
└─────────────────────────┘

Card padding: 16-24px
Header height: 48-60px
Minimum card height: 200px
```

### Alignment
- **Text**: Left-aligned (except numbers)
- **Numbers**: Right-aligned (easier comparison)
- **Charts**: Centered within cards
- **Actions**: Right-aligned in headers

### Z-Index Layers
```
1. Background
2. Cards and containers
3. Sticky headers/filters
4. Tooltips
5. Modals and dialogs
6. Alerts and notifications
```

---

## Grid Code Examples

### CSS Grid (Modern, Recommended)
```css
.dashboard {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  padding: 24px;
}

.full-width {
  grid-column: 1 / -1;
}

.half {
  grid-column: span 6;
}

.third {
  grid-column: span 4;
}

.quarter {
  grid-column: span 3;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
  }

  .half, .third, .quarter {
    grid-column: 1 / -1;
  }
}
```

### Flexbox (Alternative)
```css
.dashboard {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 24px;
}

.card {
  flex: 1 1 calc(33.333% - 24px);
  min-width: 300px;
}

@media (max-width: 768px) {
  .card {
    flex: 1 1 100%;
  }
}
```

---

## Platform Templates

### Tableau Dashboard Size Presets
```
Desktop:        1366 × 768
Laptop:         1024 × 768
iPad:           1024 × 1024
iPhone:         375 × 667
Automatic:      Responsive (recommended)
```

### Power BI Canvas
```
16:9 (1280 × 720)   - Standard
4:3 (1024 × 768)    - Classic
Letter (816 × 1056) - Print
Phone (360 × 720)   - Mobile portrait
```

---

## Anti-Patterns to Avoid

### ❌ Cramming
Too much in too little space - causes cognitive overload

### ❌ Inconsistent Sizing
Cards and charts of random sizes - looks unprofessional

### ❌ Poor Alignment
Elements not aligned to grid - appears sloppy

### ❌ Excessive Scrolling
Requiring extensive horizontal or vertical scrolling

### ❌ Hidden Navigation
Critical features buried in menus

---

## References
- Nielsen Norman Group: Dashboard Design Patterns
- Smashing Magazine: Designing Better Dashboards
- Tableau: Dashboard Design Best Practices
- Material Design: Layout Guidelines
