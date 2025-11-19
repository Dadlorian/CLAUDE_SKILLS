# Dashboard Design Guide

## Table of Contents
1. [Design Principles](#design-principles)
2. [Visual Design Foundations](#visual-design-foundations)
3. [Color Theory for Data Visualization](#color-theory-for-data-visualization)
4. [Chart Type Selection](#chart-type-selection)
5. [Dashboard Layout Patterns](#dashboard-layout-patterns)
6. [Mobile Responsiveness](#mobile-responsiveness)
7. [Accessibility Standards](#accessibility-standards)
8. [Performance Optimization](#performance-optimization)
9. [Interactive Elements](#interactive-elements)
10. [Platform-Specific Best Practices](#platform-specific-best-practices)
11. [Real-World Examples](#real-world-examples)

---

## Design Principles

### The Tufte Principles

Based on Edward Tufte's "The Visual Display of Quantitative Information":

#### 1. Show Data Variation, Not Design Variation

**Good**: Focus attention on data
```
Revenue: $1.2M (+8% vs. prior period)
[Simple bar chart showing monthly trends]
```

**Bad**: Decorative elements that don't add information
```
Revenue: $1.2M [with animated dollar signs, gradient fills, 3D effects]
[Overly stylized chart with shadows, bevels, unnecessary gridlines]
```

#### 2. Maximize Data-Ink Ratio

**Data-ink ratio** = (Data-ink) / (Total ink used in graphic)

**Principles**:
- Remove non-data ink (chartjunk)
- Erase redundant data-ink
- Revise and edit

**Example - Before (Low Data-Ink Ratio)**:
```
┌─────────────────────────────────────┐
│ ████ Revenue by Quarter █████████   │  <- Unnecessary title box
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   │
│ ┃ ╔══════╗                      ┃   │  <- Heavy borders
│ ┃ ║  Q1  ║ $500K                ┃   │  <- 3D bars
│ ┃ ║▓▓▓▓▓▓║                      ┃   │
│ ┃ ╚══════╝                      ┃   │
│ ┃   ...                         ┃   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛   │
└─────────────────────────────────────┘
```

**After (High Data-Ink Ratio)**:
```
Revenue by Quarter

Q1  ████████████ $500K
Q2  ████████████████ $600K
Q3  ███████████████████ $700K
Q4  ██████████████████████ $800K
    |    |    |    |    |
   $0  $200K $400K $600K $800K
```

#### 3. Data Density and Small Multiples

**Dense, information-rich displays** are better than sparse ones (if well-designed).

**Small multiples** - repeat the same chart type across different categories:

```
User Growth by Platform

Web                 iOS                 Android
1000 ┤              1000 ┤              1000 ┤
 800 ┤  ╱           800 ┤     ╱         800 ┤      ╱
 600 ┤ ╱            600 ┤   ╱           600 ┤    ╱
 400 ┤╱             400 ┤ ╱             400 ┤  ╱
   Jan Feb Mar        Jan Feb Mar         Jan Feb Mar
```

### The Stephen Few Principles

Based on "Information Dashboard Design":

#### 1. Dashboard Definition

> "A dashboard is a visual display of the most important information needed to achieve one or more objectives, consolidated and arranged on a single screen so the information can be monitored at a glance."

**Key attributes**:
- **Visual**: Predominantly graphical
- **Important**: Contains only essential information
- **Single screen**: No scrolling required (for primary view)
- **At a glance**: Immediate comprehension (5-second rule)

#### 2. Dashboard Types

**Strategic Dashboard**:
- Audience: Executives, senior management
- Update frequency: Daily/weekly
- Focus: High-level KPIs, trends over time
- Interaction: Minimal, mostly static

**Analytical Dashboard**:
- Audience: Analysts, data scientists
- Update frequency: Real-time/hourly
- Focus: Exploration, root cause analysis
- Interaction: Rich filtering, drill-down, ad-hoc analysis

**Operational Dashboard**:
- Audience: Operations teams, front-line managers
- Update frequency: Real-time/streaming
- Focus: Current status, alerts, immediate action items
- Interaction: Action buttons, real-time updates

#### 3. The 5-Second Rule

Users should comprehend the main message within 5 seconds of viewing the dashboard.

**Techniques**:
- Use pre-attentive attributes (color, size, position)
- Highlight exceptions and outliers
- Use comparison indicators (vs. goal, vs. prior period)
- Minimize cognitive load

**Example**:
```
Revenue Performance

$1.2M  ↑ 8% vs. target    [Green indicator]
       ↑ 12% vs. last month

Top 3 Performers:          Bottom 3 Performers:
1. Product A  $450K ↑ 15%  1. Product X  $80K ↓ 22%  [Red]
2. Product B  $380K ↑ 10%  2. Product Y  $75K ↓ 18%  [Red]
3. Product C  $270K ↑ 8%   3. Product Z  $70K ↓ 12%  [Red]
```

#### 4. Avoid Common Dashboard Mistakes

**Mistake #1: Exceeding the boundaries of a single screen**
- Solution: Use drill-down for details, keep summary on main screen

**Mistake #2: Supplying inadequate context**
- Solution: Always include comparisons (vs. target, prior period, benchmark)

**Mistake #3: Using inappropriate display media**
- Solution: Match chart type to data type (see Chart Selection Matrix)

**Mistake #4: Introducing meaningless variety**
- Solution: Use consistent chart types for similar data

**Mistake #5: Poorly designed graphs**
- Solution: Follow data visualization best practices (Tufte, Few)

**Mistake #6: Encoding quantitative data inaccurately**
- Solution: Use position/length for precise values, not angle/area

**Mistake #7: Displaying excessive detail or precision**
- Solution: Round to appropriate precision ($1.2M not $1,234,567.89)

---

## Visual Design Foundations

### Typography

#### Font Selection

**Sans-serif fonts** for dashboards (better readability on screens):
- Primary: Inter, Roboto, Open Sans, Source Sans Pro
- Monospace (for numbers/tables): Roboto Mono, Source Code Pro

**Font Sizes**:
```
Dashboard Title:        24-32px  (bold)
Section Headers:        18-20px  (semi-bold)
Chart Titles:           14-16px  (semi-bold)
Axis Labels:            11-12px  (regular)
Data Labels:            10-12px  (regular)
Footnotes/Metadata:     9-10px   (regular)
```

**Number Formatting**:
- Use tabular figures (monospace numbers) for alignment
- Right-align numbers in tables
- Use consistent decimal precision within a metric

```
Good (Tabular):        Bad (Proportional):
Revenue                Revenue
$1,234,567            $1,234,567
$  456,789            $456,789
$   89,012            $89,012
```

### White Space

**Importance**: White space (negative space) is not wasted space - it improves comprehension.

**Guidelines**:
- Minimum 20px padding around dashboard edges
- 15-20px spacing between charts
- 8-12px padding inside cards/containers
- Use consistent spacing throughout

### Visual Hierarchy

**Establish hierarchy through**:
1. **Size**: Larger elements draw attention first
2. **Color**: High contrast = high importance
3. **Position**: Top-left is primary focal point (Western reading pattern)
4. **Weight**: Bold/semi-bold for emphasis

**Example Layout Hierarchy**:
```
┌─────────────────────────────────────────────┐
│  Executive Dashboard                  [L]   │  <- Level 1: Title
├─────────────────────────────────────────────┤
│  ┌───────┐  ┌───────┐  ┌───────┐           │
│  │ KPI 1 │  │ KPI 2 │  │ KPI 3 │           │  <- Level 2: Primary KPIs
│  │ $1.2M │  │  45%  │  │ 8,234 │           │     (largest, top)
│  └───────┘  └───────┘  └───────┘           │
│                                             │
│  Revenue Trend                              │  <- Level 3: Section headers
│  ┌────────────────────────────────────┐    │
│  │ [Line chart]                       │    │  <- Level 4: Charts
│  └────────────────────────────────────┘    │
│                                             │
│  Detailed Breakdown                         │
│  ┌────────┐ ┌────────┐                     │
│  │[Chart] │ │[Chart] │                     │  <- Level 5: Supporting charts
│  └────────┘ └────────┘                     │
└─────────────────────────────────────────────┘
```

### Grid System

**Use 12-column grid** for flexible layouts:
```
┌─1──2──3──4──5──6──7──8──9─10─11─12┐
│                                     │
│  ┌────────6────────┐┌────────6────┐│  <- Two 6-column elements
│  │                 ││             ││
│  └─────────────────┘└─────────────┘│
│                                     │
│  ┌──4──┐┌──4──┐┌──4──┐             │  <- Three 4-column elements
│  │     ││     ││     │             │
│  └─────┘└─────┘└─────┘             │
│                                     │
│  ┌──3──┐┌──3──┐┌──3──┐┌──3──┐     │  <- Four 3-column elements
│  │     ││     ││     ││     │     │
│  └─────┘└─────┘└─────┘└─────┘     │
└─────────────────────────────────────┘
```

---

## Color Theory for Data Visualization

### Color Palettes

#### Categorical Colors (Qualitative)

For **distinct categories** with no inherent order:

**Tableau 10 (Default)**:
```
#4E79A7  Blue
#F28E2B  Orange
#E15759  Red
#76B7B2  Teal
#59A14F  Green
#EDC948  Yellow
#B07AA1  Purple
#FF9DA7  Pink
#9C755F  Brown
#BAB0AC  Gray
```

**Best Practices**:
- Use 5-7 colors maximum in a single chart
- Reserve highly saturated colors for emphasis
- Use muted colors for less important categories
- Maintain consistent color-category mapping across dashboard

#### Sequential Colors (Quantitative)

For **continuous data** from low to high:

**Single Hue (Blue)**:
```
Low → High
#EFF3FF → #BDD7E7 → #6BAED6 → #3182BD → #08519C
```

**Multi-Hue (Yellow-Orange-Red)**:
```
Low → High
#FFFFCC → #FFEDA0 → #FED976 → #FEB24C → #FD8D3C → #FC4E2A → #E31A1C → #BD0026
```

**Use for**:
- Heatmaps
- Choropleth maps
- Intensity scales

#### Diverging Colors

For data with **meaningful midpoint** (e.g., zero, average, target):

**Red-White-Blue**:
```
Low ← Midpoint → High
#CA0020 → #F4A582 → #FFFFFF → #92C5DE → #0571B0
```

**Use for**:
- Variance from target
- Positive/negative changes
- Above/below average

### Color Accessibility

#### Colorblind-Friendly Palettes

**8% of men** and **0.5% of women** have color vision deficiency.

**Colorblind-Safe Palette**:
```
Blue:    #0173B2  (safe)
Orange:  #DE8F05  (safe)
Green:   #029E73  (safe)
Yellow:  #ECE133  (safe)
Red:     #CC78BC  (distinguishable from green)
Purple:  #CA9161  (safe)
Gray:    #949494  (safe)
```

**Test your colors**: Use tools like Color Oracle or Coblis to simulate colorblindness.

#### Contrast Ratios (WCAG)

**WCAG AA Standard** (minimum):
- Normal text: 4.5:1 contrast ratio
- Large text (18pt+): 3:1 contrast ratio
- Non-text elements: 3:1 contrast ratio

**WCAG AAA Standard** (enhanced):
- Normal text: 7:1
- Large text: 4.5:1

**Examples**:
```
Good Contrast:
- White text (#FFFFFF) on dark blue background (#0066CC) = 6.3:1 ✓

Poor Contrast:
- Light gray text (#CCCCCC) on white background (#FFFFFF) = 1.6:1 ✗
```

**Tool**: Use WebAIM Contrast Checker

### Color Usage Guidelines

#### Do's

1. **Use color functionally**, not decoratively
   - Green = positive, red = negative, gray = neutral
   - Consistent meaning across dashboard

2. **Limit color palette** to 5-7 colors per view

3. **Use saturation** to show magnitude
   - More saturated = more important/extreme

4. **Provide redundant encoding**
   - Don't rely on color alone (add icons, patterns, labels)

#### Don'ts

1. **Don't use rainbow color schemes** for sequential data
   - Human perception doesn't see rainbow as ordered

2. **Don't use red/green only** for comparisons
   - Problematic for colorblind users
   - Add blue or use red/blue instead

3. **Don't use high-chroma backgrounds**
   - White or light gray backgrounds work best
   - Dark backgrounds can work but require careful color adjustment

4. **Don't use 3D effects** or gradients on charts
   - Reduces accuracy of perception

### Color Strategy by Dashboard Type

**Executive Dashboard**:
- Minimal color (2-3 colors max)
- High contrast
- Green/red for performance indicators
- Muted palette overall

**Analytical Dashboard**:
- Full categorical palette (up to 10 colors)
- Sequential/diverging as needed
- Focus on differentiation

**Operational Dashboard**:
- Strong use of red for alerts
- Yellow for warnings
- Green for healthy states
- Gray for neutral

---

## Chart Type Selection

### Chart Selection Matrix

| Data Relationship | Best Chart Type | Alternatives | Avoid |
|-------------------|----------------|--------------|-------|
| **Comparison** | | | |
| Compare values across categories | Bar chart (horizontal) | Column chart (if few categories) | Pie chart (>5 categories) |
| Compare values over time | Line chart | Area chart, Column chart | Pie chart |
| Compare parts of whole | Stacked bar (100%) | Treemap, Pie (≤5 slices) | 3D pie, Donut (many slices) |
| Compare multiple measures | Grouped bar chart | Small multiples | Radar chart |
| **Distribution** | | | |
| Show distribution of values | Histogram | Box plot, Violin plot | Pie chart |
| Compare distributions | Box plot | Violin plot, Ridge plot | Multiple histograms overlaid |
| Show individual data points | Scatter plot | Strip plot, Beeswarm | Table |
| **Composition** | | | |
| Part-to-whole (static) | Stacked bar (100%) | Pie (≤5), Treemap | Multiple pies |
| Part-to-whole over time | Stacked area chart | Stacked bar chart | Multiple line charts |
| Hierarchical composition | Treemap | Sunburst | Stacked bars (many levels) |
| **Relationship** | | | |
| Correlation between 2 variables | Scatter plot | Hexbin (many points) | Line chart |
| Correlation matrix | Heatmap | Scatter plot matrix | Table |
| 3+ variables | Scatter plot + color/size | Bubble chart | 3D scatter |
| **Spatial** | | | |
| Geographic distribution | Choropleth map | Symbol map | 3D map |
| Point locations | Symbol map | Hexbin map | Pie charts on map |
| **Time Series** | | | |
| Single metric over time | Line chart | Area chart | Bar chart (many periods) |
| Multiple metrics over time | Multi-line chart | Small multiples | Stacked area (many series) |
| Cyclical patterns | Line chart with annotations | Heatmap (calendar) | Radar chart |

### Detailed Chart Guidelines

#### 1. Bar Charts

**When to use**:
- Comparing discrete categories
- Showing rankings
- Displaying survey results

**Best practices**:
```
Revenue by Product Category

Electronics      ████████████████████████ $450K
Home & Garden    ███████████████████ $380K
Apparel          ███████████████ $290K
Sports           ████████████ $240K
Books            ██████ $120K
                 0    100K   200K   300K   400K   500K
```

- **Horizontal bars** for long category names
- **Start axis at zero** (or use truncated axis indicator)
- **Sort bars** by value (descending) unless natural order exists
- **Direct labeling** preferred over axis labels for exact values
- **Keep bar width consistent**
- **Use spacing** = 50% of bar width

**Avoid**:
- 3D bars (distorts perception)
- Overly decorative patterns
- Starting axis at non-zero without clear indication

#### 2. Line Charts

**When to use**:
- Showing trends over time
- Continuous data
- Multiple series comparison

**Best practices**:
```
Monthly Active Users

500K ┤                                    ╱─
     │                              ╱────╯
400K ┤                        ╱────╯
     │                  ╱────╯
300K ┤            ╱────╯
     │      ╱────╯
200K ┤─────╯
     └─┬────┬────┬────┬────┬────┬────┬────┬────┬──
      Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep
```

- **Maximum 5 lines** per chart (use small multiples for more)
- **Direct labeling** of lines preferred over legend
- **Consistent line thickness** (2-3px)
- **Use dashed lines** for projections/targets
- **Highlight** most important series with color
- **Remove unnecessary gridlines**

**Avoid**:
- More than 7-8 lines (becomes spaghetti chart)
- 3D effects
- Decorative backgrounds

#### 3. Scatter Plots

**When to use**:
- Showing correlation/relationship
- Identifying outliers
- Displaying 2+ dimensions (with color/size)

**Best practices**:
```
Customer Lifetime Value vs. Acquisition Cost

CLV  │
$500 │           •
     │         •   •
$400 │       •   •     •
     │     •   •   •
$300 │   •   •       • [Outlier - investigate]
     │ •   •
$200 │•
     └─┬───┬───┬───┬───┬───┬──
      $0  $50 $100 $150 $200 $250
               Acquisition Cost (CAC)

Ideal zone: CLV > 3x CAC (shaded region)
```

- **Show trend line** if correlation exists
- **Annotate outliers** if story-relevant
- **Use transparency** if points overlap
- **Add reference lines** (e.g., y=x, targets)
- **Size bubbles** proportionally to square root of value (not value directly)

#### 4. Heatmaps

**When to use**:
- Showing patterns in 2D data
- Correlation matrices
- Calendar/hourly patterns

**Best practices**:
```
User Activity by Day & Hour

Hour  Mon  Tue  Wed  Thu  Fri  Sat  Sun
────────────────────────────────────────
00:00 ░░░  ░░░  ░░░  ░░░  ░░░  ▓▓▓  ▓▓▓
06:00 ▒▒▒  ▒▒▒  ▒▒▒  ▒▒▒  ▒▒▒  ░░░  ░░░
12:00 ███  ███  ███  ███  ███  ▓▓▓  ▓▓▓
18:00 ▓▓▓  ▓▓▓  ▓▓▓  ▓▓▓  ███  ███  ███
23:00 ░░░  ░░░  ░░░  ░░░  ▒▒▒  ▓▓▓  ▓▓▓

░ Low   ▒ Medium   ▓ High   █ Very High
```

- **Use diverging colors** for positive/negative values
- **Use sequential colors** for magnitude only
- **Add white borders** between cells for clarity
- **Include color scale/legend**
- **Sort rows/columns** meaningfully

#### 5. Tables (When Charts Won't Work)

**When to use**:
- Exact values needed
- Mixed data types (text + numbers)
- Lookup/reference use case
- Small datasets (<20 rows)

**Best practices**:
```
Product Performance Summary

Product    Revenue    Change  Margin  Status
─────────────────────────────────────────────
Widget A   $450K     ▲ 15%   42%     ● On track
Widget B   $380K     ▲ 8%    38%     ● On track
Widget C   $290K     ▼ 3%    35%     ◐ At risk
Widget D   $240K     ▼ 12%   28%     ○ Below target
Widget E   $120K     ▲ 22%   45%     ● On track

▲ = Increase  ▼ = Decrease
● = Green    ◐ = Yellow    ○ = Red
```

- **Right-align numbers**, left-align text
- **Use monospace font** for number columns
- **Zebra striping** for >10 rows (alternating row colors)
- **Highlight** totals or key rows
- **Minimize grid lines** (use white space)
- **Sort** by most important column
- **Add sparklines** for trends within tables

**Avoid**:
- Tables for data that could be visualized
- Too many decimal places
- Heavy borders/gridlines

---

## Dashboard Layout Patterns

### F-Pattern Layout

**Users scan in F-pattern** (eye-tracking research):
1. Horizontal scan across top
2. Vertical scan down left side
3. Second horizontal scan (shorter)

**Design implication**: Place most important information in top-left.

```
┌─────────────────────────────────────────┐
│  [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]    │ ← First scan (horizontal)
│  ★ Most important                       │
├─────────────────────────────────────────┤
│  ▌                                      │
│  ▌ [Large Chart]                        │ ← Vertical scan
│  ▌                                      │
│  ▌                                      │
├─────────────────────────────────────────┤
│  ▌ [Chart]    [Chart]                   │ ← Second horizontal
│  ▌                                      │
└─────────────────────────────────────────┘
   ↓ Left edge is anchor
```

### Common Layout Patterns

#### 1. KPI + Trend Pattern

**Use case**: Executive dashboards, monitoring

```
┌─────────────────────────────────────────┐
│  Revenue          Orders      Avg Order │
│  $1.2M  ↑ 8%     15,234      $78.99     │ <- Big numbers
│  ───╱──          ───╱──      ─────╱──   │ <- Sparklines
├─────────────────────────────────────────┤
│  Revenue Trend (Last 30 Days)           │
│  ┌──────────────────────────────────┐   │
│  │  [Line chart with annotations]   │   │ <- Detailed trend
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

#### 2. Comparison Dashboard

**Use case**: Period-over-period, segment analysis

```
┌─────────────────────────────────────────┐
│  This Month        vs.    Last Month    │
│  ┌──────────────┐       ┌──────────────┐│
│  │ $1.2M        │   +8% │ $1.1M        ││
│  │ [Chart]      │       │ [Chart]      ││
│  └──────────────┘       └──────────────┘│
├─────────────────────────────────────────┤
│  Key Changes:                           │
│  • Widget A: ▲ 15%  [$450K → $518K]    │
│  • Widget B: ▲ 8%   [$380K → $410K]    │
│  • Widget D: ▼ 12%  [$240K → $211K]    │
└─────────────────────────────────────────┘
```

#### 3. Drill-Down Dashboard

**Use case**: Analytical dashboards

```
┌─────────────────────────────────────────┐
│  [Filters: Date | Region | Product]     │
├─────────────────────────────────────────┤
│  Overview                               │
│  ┌──────────────────────────────────┐   │
│  │  [Summary chart] ← Click to drill │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  Detail View (Region: West)             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │
│  │      │ │      │ │      │ │      │   │
│  └──────┘ └──────┘ └──────┘ └──────┘   │
└─────────────────────────────────────────┘
```

#### 4. Operational Dashboard

**Use case**: Real-time monitoring, alerts

```
┌─────────────────────────────────────────┐
│  System Status      [Updated: 14:32:45] │
├─────────────────────────────────────────┤
│  ● API Latency: 45ms     [Normal]       │
│  ● Error Rate: 0.02%     [Normal]       │
│  ⚠ Queue Depth: 15,234   [Warning]      │
│  🔴 Database CPU: 87%    [Critical]     │
├─────────────────────────────────────────┤
│  Real-Time Metrics                      │
│  ┌──────────────────────────────────┐   │
│  │  [Streaming line chart]          │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  Active Alerts (3)          [View All]  │
│  • Database CPU high (2 min ago)        │
│  • Queue backlog growing (5 min ago)    │
│  • Disk space low (15 min ago)          │
└─────────────────────────────────────────┘
```

### Grid Alignment

**Always use a grid**. Misaligned elements look unprofessional.

**Good**:
```
┌───────┬───────┬───────┐
│   A   │   B   │   C   │  <- Aligned to grid
├───────┴───────┴───────┤
│         D             │
├───────────┬───────────┤
│     E     │     F     │
└───────────┴───────────┘
```

**Bad**:
```
┌──────┐ ┌────────┐
│  A   │ │   B    │  <- Misaligned
└──────┘ └────────┘
  ┌────────────┐
  │      D     │     <- Not aligned with above
  └────────────┘
┌────┐     ┌─────────┐
│ E  │     │    F    │  <- Inconsistent spacing
└────┘     └─────────┘
```

---

## Mobile Responsiveness

### Mobile-First Principles

#### 1. Vertical Layout

Desktop (16:9):
```
┌────────────────────────────────┐
│ [KPI 1] [KPI 2] [KPI 3]       │
│ [Chart 1]    [Chart 2]         │
└────────────────────────────────┘
```

Mobile (9:16):
```
┌──────────┐
│ [KPI 1]  │
│ [KPI 2]  │
│ [KPI 3]  │
│ [Chart 1]│
│ [Chart 2]│
└──────────┘
```

#### 2. Touch-Friendly Targets

**Minimum touch target**: 44x44 pixels (iOS HIG) / 48x48 pixels (Material Design)

```
Good:
┌──────────────┐
│   Button     │  48px height
└──────────────┘

Bad:
┌─────┐
│ Btn │  20px height - too small!
└─────┘
```

#### 3. Responsive Breakpoints

```css
/* Mobile first */
.dashboard-card {
  grid-column: span 12;  /* Full width on mobile */
}

/* Tablet */
@media (min-width: 768px) {
  .dashboard-card {
    grid-column: span 6;  /* Half width */
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .dashboard-card {
    grid-column: span 4;  /* Third width */
  }
}

/* Large desktop */
@media (min-width: 1440px) {
  .dashboard-card {
    grid-column: span 3;  /* Quarter width */
  }
}
```

#### 4. Simplified Mobile Views

**Desktop version**: 12 charts
**Mobile version**: Top 4 KPIs + 2-3 key charts + "View More" button

**Progressive disclosure**: Show summary, allow drill-down to details

### Platform-Specific Considerations

#### iOS

- Use native iOS gestures (swipe to navigate, pinch to zoom)
- Follow iOS Human Interface Guidelines
- Safe area insets for notched devices
- Support dark mode

#### Android

- Material Design principles
- Floating action buttons for primary actions
- Navigation drawer for menu
- Support various screen sizes/densities

#### Web/Responsive

- Test on actual devices, not just browser resize
- Consider hover vs. touch interactions
- Lazy load images and charts
- Use CSS Grid/Flexbox for responsive layouts

---

## Accessibility Standards

### WCAG 2.1 Compliance

**Level A** (minimum):
- Text alternatives for non-text content
- Captions for audio/video
- Keyboard accessible
- Sufficient time to read content

**Level AA** (recommended):
- 4.5:1 contrast ratio for normal text
- 3:1 for large text and UI components
- Resize text up to 200%
- Multiple ways to navigate

**Level AAA** (enhanced):
- 7:1 contrast ratio
- No timing requirements
- Enhanced contrast for UI components

### ARIA Labels for Charts

```html
<!-- Screen reader accessible chart -->
<div role="img" aria-label="Line chart showing monthly revenue increasing from $1M in January to $1.5M in December">
  <svg>
    <!-- Chart visualization -->
  </svg>

  <!-- Fallback table for screen readers -->
  <table class="sr-only">
    <caption>Monthly Revenue</caption>
    <thead>
      <tr>
        <th>Month</th>
        <th>Revenue</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>January</td><td>$1,000,000</td></tr>
      <tr><td>February</td><td>$1,100,000</td></tr>
      <!-- ... -->
    </tbody>
  </table>
</div>
```

### Keyboard Navigation

**All interactive elements** must be keyboard accessible:

- `Tab`: Move to next element
- `Shift+Tab`: Move to previous element
- `Enter/Space`: Activate button/link
- `Arrow keys`: Navigate within component (dropdowns, sliders)
- `Esc`: Close modal/dialog

**Focus indicators**: Always show clear focus state (don't disable outline)

```css
/* Good: Visible focus */
button:focus {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

/* Bad: Removed focus indicator */
button:focus {
  outline: none;  /* Never do this! */
}
```

### Alt Text for Data Visualizations

**Pattern**: "Chart type showing main insight"

**Examples**:
```
Good:
"Line chart showing daily active users increasing 35% from 100K to 135K over the last quarter"

Bad:
"Chart"  (too vague)
"Line chart of DAU by date from January 1 to March 31..."  (too detailed)
```

### Color Blindness Accommodations

**Don't rely on color alone**:

```
Good:
Revenue:  ▲ 8% (green up arrow)
Costs:    ▼ 3% (red down arrow)

Bad:
Revenue:  8% (green text only)
Costs:    3% (red text only)
```

**Use patterns/textures** in addition to color:
```
[Chart with both color AND pattern]
■ Category A (solid blue)
▨ Category B (hatched red)
▦ Category C (dotted green)
```

---

## Performance Optimization

### Load Time Optimization

**Target**: Dashboard loads in <3 seconds on 3G connection

#### 1. Query Optimization

**Pre-aggregate data**:
```sql
-- Bad: Scanning millions of rows
SELECT
    DATE(order_timestamp) AS order_date,
    SUM(order_total_amount_usd) AS revenue
FROM orders
WHERE order_timestamp >= '2020-01-01'
GROUP BY 1;

-- Good: Pre-aggregated daily table
SELECT
    order_date,
    revenue
FROM daily_order_summary
WHERE order_date >= CURRENT_DATE - 90;
```

**Use materialized views/tables**:
- Refresh overnight for dashboards that don't need real-time
- Incremental refresh for large datasets

**Limit data pulled to frontend**:
```javascript
// Bad: Pull 1M rows to browser
fetch('/api/events?days=365')

// Good: Aggregate server-side, pull 365 rows
fetch('/api/daily-events?days=365')
```

#### 2. Caching Strategy

**Multi-layer caching**:
```
User Request
    ↓
[CDN Cache] - 5 min TTL
    ↓ (miss)
[Application Cache] - 15 min TTL
    ↓ (miss)
[Database Query]
    ↓
[Cache Write] - Update all cache layers
    ↓
Response
```

**Cache invalidation**: Tag-based or time-based
```python
# Time-based
cache.set('dashboard_data', data, ttl=300)  # 5 minutes

# Tag-based (invalidate on data update)
cache.set('dashboard_data', data, tags=['orders', 'daily'])
# When orders update:
cache.invalidate_tags(['orders'])
```

#### 3. Lazy Loading

**Load critical content first**:
```javascript
// Load immediately
- KPI cards (small data volume)
- Key chart above fold

// Load on scroll/interaction
- Below-fold charts
- Detailed tables
- Export functionality
```

**Skeleton screens** while loading:
```
┌─────────────────┐
│ ████ Loading... │  <- Skeleton placeholder
│ ░░░░░░░░░░      │
│ ░░░░░░░░░░      │
└─────────────────┘
```

#### 4. Data Sampling

For **exploratory dashboards** with massive datasets:

```sql
-- Sample 10% of data for fast preview
SELECT *
FROM events TABLESAMPLE BERNOULLI(10)
WHERE event_date >= CURRENT_DATE - 30;

-- User can toggle "Full Data" if needed
```

**Display sampling indicator**:
```
Note: Showing 10% sample (N=1.2M). [Load Full Dataset]
```

### Query Efficiency

#### Partition Pruning

```sql
-- Good: Filters on partition key
SELECT *
FROM events
WHERE partition_date >= '2024-03-01'  -- Uses partition
  AND event_type = 'purchase';

-- Bad: Scans all partitions
SELECT *
FROM events
WHERE event_timestamp >= '2024-03-01'  -- Not partition key
```

#### Incremental Loads

```sql
-- Only process new data
SELECT *
FROM events
WHERE partition_date = CURRENT_DATE - 1  -- Yesterday only
```

#### Index Usage

```sql
-- Ensure indexes on filter/join columns
CREATE INDEX idx_user_id ON events(user_id);
CREATE INDEX idx_event_date ON events(event_date, event_type);
```

### Frontend Performance

#### Chart Rendering Optimization

**Limit data points rendered**:
```javascript
// For line chart with 10,000+ points, downsample to ~500 visible points
const visiblePoints = downsampleData(allPoints, pixelWidth);
```

**Use canvas instead of SVG** for >1000 points:
- SVG: Better for interactivity, accessibility (DOM nodes)
- Canvas: Better for performance at scale (bitmap)

**Virtualization** for large tables:
```javascript
// Only render visible rows
<VirtualizedTable
  rowCount={1000000}
  visibleRows={20}
  rowHeight={40}
/>
```

#### Code Splitting

```javascript
// Load chart libraries on demand
const loadChartLib = () => import('chart-library');

// Only load when chart component needed
if (showChart) {
  const Chart = await loadChartLib();
}
```

---

## Interactive Elements

### Filters

#### Filter Placement

**Global filters**: Top of dashboard, always visible
```
┌─────────────────────────────────────┐
│ [Date Range ▾] [Region ▾] [Apply]  │  <- Global filters
├─────────────────────────────────────┤
│ [Dashboard content]                 │
└─────────────────────────────────────┘
```

**Local filters**: Within specific cards/charts
```
┌─────────────────────────────────────┐
│ Revenue by Product                  │
│ [Category: All ▾] [Sort: Value ▾]   │  <- Local filters
│ ─────────────────────────────────   │
│ [Bar chart]                         │
└─────────────────────────────────────┘
```

#### Filter Types

**Date Range Picker**:
```
[Last 7 Days ▾]
  Quick picks:
  • Today
  • Last 7 days
  • Last 30 days
  • Last quarter
  • Last year
  • Custom range...
```

**Multi-Select**:
```
[Regions: 3 selected ▾]
  ☑ North America
  ☑ Europe
  ☐ Asia Pacific
  ☑ Latin America
  ☐ Middle East
```

**Search/Autocomplete**:
```
[Search products... 🔍]
  Start typing to filter...

  Showing: 3 matches
  • Product A
  • Product B
  • Product C
```

#### Filter Best Practices

- **Show active filters** clearly
- **Allow clear/reset** filters easily
- **Persist filters** in URL (shareable links)
- **Default to sensible** values (e.g., Last 30 Days)
- **Limit cascading filters** (max 2-3 levels)

### Tooltips and Hover States

#### Data Tooltips

```
[Hover over bar chart]

┌─────────────────────┐
│ Electronics         │
│ Revenue: $450,234   │
│ 32% of total        │
│ ▲ 15% vs. last month│
└─────────────────────┘
```

**Include in tooltips**:
- Exact values (chart shows approximate)
- Additional context (% of total, change)
- Related metrics
- Timestamp (for time series)

**Best practices**:
- Delay: 200-500ms hover before showing
- Position: Near cursor, not covering data
- Contrast: High contrast background
- Brevity: 3-5 lines max

#### Help Tooltips

```
Weekly Active Users (i)
     ↓ (hover)
┌───────────────────────────────────┐
│ Count of users who performed ≥1  │
│ core action in the last 7 days.  │
│                                   │
│ [Learn more →]                    │
└───────────────────────────────────┘
```

### Drill-Down

#### Click-to-Filter

```
[Click on "Electronics" bar in chart]
     ↓
[Dashboard filters to Electronics category]
[Shows breadcrumb: All Categories > Electronics]
[Click breadcrumb to go back]
```

#### Modal Drill-Down

```
[Click on KPI card]
     ↓
┌────────────────────────────────────────┐
│ Weekly Active Users - Detail           │
│                                    [×] │
├────────────────────────────────────────┤
│ [Detailed chart]                       │
│ [Segmentation table]                   │
│ [Related metrics]                      │
└────────────────────────────────────────┘
```

#### Separate View Drill-Down

```
[Click "View Details" link]
     ↓
[Navigates to separate detailed dashboard]
[Maintains filter context via URL params]
```

### Export and Sharing

#### Export Options

```
[⋮ Menu]
  ├─ Download as PDF
  ├─ Download as PNG
  ├─ Export data (CSV)
  ├─ Export data (Excel)
  ├─ Schedule email
  └─ Share link
```

#### Share Links

```
[Share button]
  ↓
┌────────────────────────────────────┐
│ Share Dashboard                    │
├────────────────────────────────────┤
│ Link (includes current filters):  │
│ https://...?date=2024-03&region=na │
│                                    │
│ [Copy Link]  [Email]  [Slack]     │
└────────────────────────────────────┘
```

---

## Platform-Specific Best Practices

### Tableau

#### Design Best Practices

1. **Dashboards vs. Stories**:
   - Dashboard: Single view, interactive
   - Story: Guided narrative, sequential

2. **Device Layouts**:
   - Design separate layouts for Desktop/Tablet/Phone
   - Use device-specific sizing

3. **Actions**:
   - Filter actions for click-to-filter
   - Highlight actions for cross-chart highlighting
   - URL actions for external links
   - Parameter actions for dynamic control

4. **Performance**:
   - Use extracts instead of live connections for large datasets
   - Aggregate data at appropriate grain
   - Limit number of marks (< 50K per sheet)
   - Use context filters to reduce query scope

#### Tableau-Specific Features

```
Dashboard Size: Automatic (responsive)
or
Dashboard Size: Fixed (1280x800 for desktop)

Performance Recording:
  - Help > Settings and Performance > Start Performance Recording
  - Identify slow queries/rendering

Level of Detail (LOD) Expressions:
  { FIXED [Customer ID] : SUM([Sales]) }
```

### Power BI

#### Design Best Practices

1. **Report vs. Dashboard**:
   - Report: Multi-page, detailed, interactive
   - Dashboard: Single page, KPIs, high-level

2. **Visual Types**:
   - Use built-in visuals when possible (performance)
   - Custom visuals for specialized needs
   - AppSource for vetted community visuals

3. **Slicers**:
   - Sync slicers across pages (View > Sync Slicers)
   - Use hierarchy slicers for drill-down

4. **Performance**:
   - Import mode > DirectQuery (when possible)
   - Reduce cardinality in relationships
   - Use aggregations for large datasets
   - Performance Analyzer (View > Performance Analyzer)

#### Power BI-Specific Features

```
Bookmarks:
  - Save state (filters, focus, visibility)
  - Create navigation menu
  - Button > Action > Bookmark

Drill-through:
  - Right-click data point > Drill through > [Page]
  - Pass filters to detail page

Mobile Layout:
  - View > Mobile Layout
  - Reorganize visuals for portrait orientation
```

### Looker

#### Design Best Practices

1. **Looks vs. Dashboards**:
   - Look: Single query/visualization
   - Dashboard: Combination of Looks + text

2. **LookML**:
   - Define metrics in LookML (centralized definitions)
   - Use derived tables for complex logic
   - Leverage persistent derived tables for performance

3. **Filters**:
   - Dashboard-level filters for global filtering
   - Listen to filters in dashboard tiles
   - Default filter values in LookML

4. **Performance**:
   - Use persistent derived tables (PDTs) for pre-aggregation
   - Aggregate awareness to auto-query summary tables
   - Cache warming for scheduled refreshes

#### Looker-Specific Features

```lookml
# LookML metric definition
measure: total_revenue {
  type: sum
  sql: ${order_total_amount_usd} ;;
  value_format_name: usd
  drill_fields: [order_details*]
}

# Dashboard filter
dashboard: executive_metrics {
  filters: {
    field: date_range
    default: "30 days"
  }
}
```

---

## Real-World Examples

### Netflix Experimentation Dashboard

**Key Features**:
1. **Traffic Light System**: Green/Yellow/Red for metric performance
2. **Confidence Intervals**: Always show statistical significance
3. **Guardrail Metrics**: Highlight if any guardrails violated
4. **Heterogeneous Treatment Effects**: Breakdowns by segment

**Layout**:
```
┌──────────────────────────────────────────────┐
│ Experiment: Homepage Redesign (Test 12345)  │
│ Status: ● Running  |  Runtime: 14 days      │
├──────────────────────────────────────────────┤
│ Primary Metric: Session Duration            │
│ Control: 18.2 min  │  Treatment: 19.5 min   │
│ Lift: +7.1% [+5.2%, +9.0%] ✓ Significant    │
├──────────────────────────────────────────────┤
│ Guardrail Metrics:                           │
│ • Sign-ups: -0.3% [—] ✓ Not significant     │
│ • Error rate: +0.02% [—] ✓ Not significant  │
│ • Streaming hours: +2.1% [+0.5%, +3.7%] ✓   │
├──────────────────────────────────────────────┤
│ Treatment Effect by Segment:                │
│ New users:      +12.3% ✓                     │
│ Returning:      +3.2% ✓                      │
│ Power users:    -1.1% ✗                      │
└──────────────────────────────────────────────┘
```

### Airbnb Host Dashboard

**Key Features**:
1. **Personalized Insights**: Compare to similar listings
2. **Actionable Recommendations**: "Your response time impacts..."
3. **Gamification**: Superhost status, badges
4. **Revenue Forecast**: Projected earnings based on availability

**Layout**:
```
┌──────────────────────────────────────────────┐
│ Your Listing Performance                     │
├──────────────────────────────────────────────┤
│ This Month:        vs Similar Listings:      │
│ $4,250 ↑ 12%      $3,800 (avg)              │
│ 22 bookings        18 bookings (avg)         │
│ 4.9★ rating       4.7★ (avg)                │
├──────────────────────────────────────────────┤
│ Insights:                                    │
│ ✓ Your pricing is competitive                │
│ ⚠ Response time: 2.3 hrs (target: <1 hr)    │
│ ✓ Great reviews on cleanliness               │
├──────────────────────────────────────────────┤
│ Recommendations:                             │
│ 1. Enable Instant Book → +8% bookings       │
│ 2. Update calendar → +$430 potential         │
│ 3. Improve response time → Superhost status │
└──────────────────────────────────────────────┘
```

### Stripe Revenue Dashboard

**Key Features**:
1. **Real-Time Updates**: Streaming data
2. **Multi-Currency**: Auto-convert with exchange rates shown
3. **MRR Movements**: Visualize new/churned/expansion
4. **Cohort Analysis**: Revenue retention by signup cohort

**Layout**:
```
┌──────────────────────────────────────────────┐
│ Revenue Overview                    [Live ●]│
├──────────────────────────────────────────────┤
│ MRR: $125,450  ↑ $8,230 (+7.0%) vs last month│
│                                              │
│ MRR Movement Waterfall:                      │
│  $117K ──→ [+$12K New] ──→ [+$3K Expansion]─│
│       └→ [-$4K Churn] ──→ [-$3K Downgrade]─→│
│                                   $125K ←────│
├──────────────────────────────────────────────┤
│ Cohort Retention (% of MRR retained):        │
│        M1   M2   M3   M6   M12               │
│ Jan24: 100% 95% 89% 78% 65%                  │
│ Feb24: 100% 93% 87% 76%                      │
│ Mar24: 100% 94% 88%                          │
└──────────────────────────────────────────────┘
```

### Shopify Merchant Dashboard

**Key Features**:
1. **Benchmarking**: Compare to similar stores
2. **Product Insights**: Top/bottom performers
3. **Customer Lifetime Value**: Segment analysis
4. **Abandoned Carts**: Recovery opportunities

**Layout**:
```
┌──────────────────────────────────────────────┐
│ Store Performance - Last 30 Days             │
├──────────────────────────────────────────────┤
│ Sales: $45,230     Orders: 892               │
│ ↑ 15% vs last month  ↑ 12%                   │
│ vs Similar Stores: ▲ Above avg               │
├──────────────────────────────────────────────┤
│ Top Products (by Revenue):                   │
│ 1. Widget Pro   $12,450  ↑ 22%  [350 sold]  │
│ 2. Gadget Plus  $8,930   ↑ 8%   [220 sold]  │
│ 3. Tool Deluxe  $7,200   ↓ 3%   [180 sold]  │
├──────────────────────────────────────────────┤
│ Opportunities:                               │
│ • 47 abandoned carts ($3,240 value)          │
│   [Send recovery email →]                    │
│ • 23 customers ready for repeat purchase     │
│   [Create campaign →]                        │
└──────────────────────────────────────────────┘
```

---

## Checklist: Pre-Launch Review

### Design Quality
- [ ] Follows platform style guide (Tableau/Power BI/Looker)
- [ ] Consistent colors across all charts
- [ ] Adequate white space and visual breathing room
- [ ] All text readable (min 10-11px font size)
- [ ] Proper alignment and grid usage
- [ ] Data-ink ratio optimized (minimal chartjunk)

### Data Quality
- [ ] All metrics defined and documented
- [ ] Data sources identified and validated
- [ ] Calculations verified against source systems
- [ ] Null/missing data handled appropriately
- [ ] Data freshness indicated (last updated timestamp)
- [ ] Known limitations documented

### Usability
- [ ] Dashboard purpose clear from title/description
- [ ] Target audience identified
- [ ] 5-second rule: main insight visible at a glance
- [ ] Filters intuitive and well-labeled
- [ ] Drill-down paths logical
- [ ] Help text provided for complex metrics
- [ ] Export functionality available

### Accessibility
- [ ] WCAG AA contrast ratios met (4.5:1)
- [ ] Color not used as only indicator
- [ ] Alt text provided for charts
- [ ] Keyboard navigation functional
- [ ] Screen reader compatible
- [ ] Works without mouse/touch

### Performance
- [ ] Loads in <3 seconds on target connection
- [ ] Queries optimized (indexed, partitioned)
- [ ] Appropriate caching strategy
- [ ] Large datasets sampled or pre-aggregated
- [ ] Mobile version loads quickly

### Mobile/Responsive
- [ ] Mobile layout provided (if applicable)
- [ ] Touch targets min 44x44px
- [ ] Readable on small screens
- [ ] Charts simplified for mobile
- [ ] Tested on actual devices

### Documentation
- [ ] Dashboard documentation complete
- [ ] Metric definitions documented
- [ ] Data lineage documented
- [ ] Change log initialized
- [ ] Owner identified
- [ ] Support contact provided

### Business Validation
- [ ] Stakeholder review completed
- [ ] Metrics validated against business logic
- [ ] Edge cases tested
- [ ] User acceptance testing done
- [ ] Training materials prepared (if needed)

---

## Further Resources

### Books
- **"The Visual Display of Quantitative Information"** - Edward Tufte
- **"Envisioning Information"** - Edward Tufte
- **"Information Dashboard Design"** - Stephen Few
- **"Show Me the Numbers"** - Stephen Few
- **"Storytelling with Data"** - Cole Nussbaumer Knaflic
- **"The Functional Art"** - Alberto Cairo

### Online Resources
- **Tableau Public**: Best-in-class dashboard examples
- **Power BI Community**: Dashboard gallery and templates
- **Observable**: D3.js visualization examples
- **Datawrapper Academy**: Data visualization training
- **FlowingData**: Data viz blog by Nathan Yau

### Style Guides
- **Financial Times Visual Vocabulary**: Chart selection guide
- **Uber Visualization Design**: Brand guidelines for data viz
- **US Digital Services Playbook**: Government dashboard standards
- **BBC GEL (Global Experience Language)**: Data visualization guidelines

### Tools
- **Color Oracle**: Colorblindness simulator
- **WebAIM Contrast Checker**: WCAG compliance testing
- **Figma/Sketch**: Dashboard mockups and design
- **Coolors.co**: Color palette generator
- **ColorBrewer**: Colorblind-safe palettes for maps

### Communities
- **Data Visualization Society**: Professional community
- **r/dataisbeautiful**: Reddit community
- **Tableau Community Forums**: Platform-specific help
- **Power BI Community**: Platform-specific help
- **Looker Community**: Platform-specific help
