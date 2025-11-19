# Data Visualization Style Guide

## Overview

This guide establishes standards for creating effective, accessible, and professional data visualizations and dashboards. Based on seminal works by Edward Tufte, Stephen Few, and Cole Nussbaumer Knaflic.

**Key References:**
- Edward Tufte: "The Visual Display of Quantitative Information"
- Stephen Few: "Information Dashboard Design" and "Show Me the Numbers"
- Cole Nussbaumer Knaflic: "Storytelling with Data"
- Tamara Munzner: "Visualization Analysis and Design"

---

## Table of Contents

1. [Design Principles (Tufte)](#design-principles-tufte)
2. [Color Palette Standards](#color-palette-standards)
3. [Chart Selection Matrix](#chart-selection-matrix)
4. [Dashboard Layout Patterns](#dashboard-layout-patterns)
5. [Typography and Labeling](#typography-and-labeling)
6. [Mobile-Responsive Design](#mobile-responsive-design)
7. [Accessibility Standards](#accessibility-standards)

---

## Design Principles (Tufte)

### 1. Data-Ink Ratio

**Definition**: Proportion of a graphic's ink devoted to the non-redundant display of data-information.

**Formula**: Data-Ink Ratio = Data-Ink / Total Ink

**Principle**: "Above all else show the data." - Edward Tufte

**To Maximize Data-Ink Ratio:**

❌ **Before (Low Data-Ink Ratio):**
```
Revenue by Quarter
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ╔═══════════╗                   ┃  Heavy borders
┃ ║    Q1     ║  $500K            ┃  3D effects
┃ ║ ▓▓▓▓▓▓▓▓▓ ║                   ┃  Grid lines
┃ ╚═══════════╝                   ┃  Box shadows
┃ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

✅ **After (High Data-Ink Ratio):**
```
Revenue by Quarter

Q1  ████████████ $500K
Q2  ████████████████ $600K
Q3  ███████████████████ $700K
Q4  ██████████████████████ $800K
    |    |    |    |    |
   $0  $200K $400K $600K $800K
```

**Tufte's Rules:**
1. **Erase non-data ink** - Remove decorative elements
2. **Erase redundant data-ink** - Don't show same data twice
3. **Revise and edit** - Simplify relentlessly

### 2. Chartjunk Elimination

**Chartjunk**: Non-data elements that distract from information.

**Common Chartjunk to Avoid:**

```markdown
❌ 3D effects (distort perception)
❌ Unnecessary gridlines (faint is acceptable)
❌ Decorative fills and patterns
❌ Heavy borders and frames
❌ Drop shadows
❌ Gradients on data elements
❌ Pictograms that replace simple bars
❌ Vibrating patterns (moiré effects)
```

**Example - Before/After:**

```
BEFORE:
[3D Pie Chart with gradients, drop shadows, and explosion effects]

AFTER:
Revenue by Category (% of Total)

Electronics      32%  ████████████████
Home & Garden    24%  ████████████
Apparel          21%  ██████████▌
Sports           15%  ███████▌
Books             8%  ████
```

### 3. Small Multiples

**Definition**: Series of similar graphs using same scale and axes, allowing comparison.

**Principle**: "At the heart of quantitative reasoning is a single question: Compared to what?" - Tufte

**Example:**

```
User Growth by Platform (Monthly Active Users)

Web                 iOS                 Android
1000 ┤              1000 ┤              1000 ┤
 800 ┤  ╱           800 ┤     ╱         800 ┤      ╱
 600 ┤ ╱            600 ┤   ╱           600 ┤    ╱
 400 ┤╱             400 ┤ ╱             400 ┤  ╱
     Jan Feb Mar        Jan Feb Mar         Jan Feb Mar

All platforms use same Y-axis scale for comparison
```

**Best Practices:**
- Use identical axes and scales
- Arrange in meaningful order (chronological, by value)
- Keep individual charts small but legible
- Limit to 6-12 multiples per view

### 4. Graphical Integrity

**Lie Factor** = Size of effect shown in graphic / Size of effect in data

**Acceptable:** Lie Factor between 0.95 - 1.05

**Violations:**

❌ **Truncated Y-Axis Without Warning:**
```
Revenue "Growth"
$1,000,100 ┤      ███
$1,000,075 ┤  ███ ███
$1,000,050 ┤ ███  ███
$1,000,025 ┤ ███  ███
           └──────────
            Q1    Q2

Misleading: Looks like huge growth, actually only 0.0025%
```

✅ **Honest Representation:**
```
Revenue Growth
$1.5M ┤
$1.0M ┤ ███  ███
$0.5M ┤ ███  ███
    0 ┤ ███  ███
      └──────────
       Q1    Q2

Or clearly indicate: "Y-axis starts at $1M (detail view)"
```

**Guidelines:**
1. Start bar charts at zero (or use truncated axis indicator)
2. Use consistent scales across comparisons
3. Represent numbers proportionally
4. Include context (baselines, benchmarks, targets)

### 5. Layering and Separation

**Principle**: Distinguish between data, grid, and labels through subtle visual hierarchy.

**Layering Order (Front to Back):**
1. **Data** (darkest, highest contrast)
2. **Labels** (medium contrast)
3. **Grid lines** (lightest, lowest contrast)
4. **Background** (white or very light gray)

**Example:**

```
Revenue Trend

$1.2M ┤                                ●━━━ Actual (dark blue, solid)
      │                            ●━━┘
$1.0M ┤                        ●━━┘      - - - Target (gray, dashed)
      │                    ●━━┘
$0.8M ┤                ●━━┘
      │            ●━━┘
$0.6M ┤        ●━━┘
      └────┬────┬────┬────┬────┬────   (light gray grid)
          Jan  Mar  May  Jul  Sep  Nov
```

**Color Hierarchy:**
- Data: #0066CC (strong blue)
- Labels: #333333 (dark gray)
- Grid: #E0E0E0 (light gray)
- Background: #FFFFFF (white)

---

## Color Palette Standards

### Categorical Palettes (Qualitative Data)

Use for **distinct categories** with no inherent order.

**Primary Palette (Colorblind-Safe):**

```
Blue:     #0173B2  ■  Primary
Orange:   #DE8F05  ■  Secondary
Green:    #029E73  ■  Success/Positive
Yellow:   #ECE133  ■  Warning/Caution
Purple:   #CA9161  ■  Neutral
Red:      #CC78BC  ■  Error/Negative (distinguishable from green)
Gray:     #949494  ■  Inactive/Disabled
```

**Best Practices:**
- Limit to 5-7 colors per chart
- Use most saturated colors for most important categories
- Maintain consistent color-category mapping across dashboards
- Reserve red/green for semantic meaning (negative/positive)

**Example Usage:**

```yaml
# dashboard_config.yml
categorical_colors:
  Product:
    Electronics: "#0173B2"  # Blue
    Apparel: "#DE8F05"      # Orange
    Home: "#029E73"         # Green
    Sports: "#ECE133"       # Yellow
    Books: "#CA9161"        # Purple

status_colors:
  Healthy: "#029E73"    # Green
  Warning: "#ECE133"    # Yellow
  Critical: "#CC78BC"   # Red (colorblind-safe)
```

### Sequential Palettes (Quantitative Data)

Use for **continuous data** from low to high values.

**Single Hue (Recommended for most use cases):**

```
Blue Scale (Light → Dark):
#EFF6FB → #C6DBEF → #9ECAE1 → #6BAED6 → #3182BD → #08519C

Usage: Heatmaps, choropleth maps, intensity scales
```

**Multi-Hue (For broader ranges):**

```
Yellow-Orange-Red (Cool → Warm):
#FFFFCC → #FFEDA0 → #FED976 → #FEB24C → #FC4E2A → #E31A1C → #BD0026

Usage: Temperature, risk levels, age data
```

### Diverging Palettes

Use for data with **meaningful midpoint** (zero, average, target).

**Red-White-Blue (Standard):**

```
Below Target ← Target → Above Target
#CA0020 → #F4A582 → #F7F7F7 → #92C5DE → #0571B0

Usage: Variance from budget, +/- growth rates, survey scales
```

**Example:**

```
Budget Variance by Department

IT          ████████░░░░░░░░ -15%  (red)
Sales       ░░░░░░░░░░░░████  +8%  (blue)
Marketing   ░░░░░░░░░░░░░░░░   0%  (white/neutral)
HR          ████░░░░░░░░░░░░  -5%  (light red)
Finance     ░░░░░░░░░░████    +5%  (light blue)
```

### Accessibility: Colorblind-Friendly Design

**8% of men and 0.5% of women** have some form of color vision deficiency.

**Rules:**
1. **Never rely on color alone** - Add patterns, labels, or icons
2. **Avoid red-green only comparisons** - Use red-blue or include third differentiator
3. **Test with colorblindness simulators** - Color Oracle, Coblis

**Accessible Comparison:**

```
❌ Bad: Revenue (green) vs. Costs (red) - Colorblind users can't distinguish

✅ Good:
Revenue  ▲ $1.2M  (blue, up arrow)
Costs    ▼ $0.8M  (orange, down arrow)
```

### WCAG Contrast Requirements

**Level AA (Minimum):**
- Normal text: 4.5:1 contrast ratio
- Large text (18pt+): 3:1
- UI components: 3:1

**Level AAA (Enhanced):**
- Normal text: 7:1
- Large text: 4.5:1

**Examples:**

```
✅ Good Contrast (7.2:1):
#FFFFFF (white) on #0066CC (dark blue)

❌ Poor Contrast (1.6:1):
#CCCCCC (light gray) on #FFFFFF (white)
```

**Tool**: Use WebAIM Contrast Checker

---

## Chart Selection Matrix

### By Data Relationship

| Objective | Recommended Chart | Avoid |
|-----------|-------------------|-------|
| **Compare values across categories** | Horizontal bar chart | Pie chart (>5 slices) |
| **Show trend over time** | Line chart | Bar chart (many periods) |
| **Part-to-whole (static)** | Stacked bar (100%) | Multiple pie charts |
| **Part-to-whole over time** | Stacked area chart | Pie charts |
| **Distribution** | Histogram, Box plot | Pie chart |
| **Correlation** | Scatter plot | Line chart |
| **Ranking** | Horizontal bar (sorted) | Unsorted bar chart |
| **Deviation from baseline** | Diverging bar chart | Stacked bar |

### Detailed Chart Guidelines

#### 1. Bar Charts (Categorical Comparison)

**When to Use:**
- Comparing discrete categories
- Showing rankings
- Displaying magnitudes

**Best Practices:**

```
✅ Good:
Revenue by Product Category

Electronics      ████████████████████████ $450K
Home & Garden    ███████████████████ $380K
Apparel          ███████████████ $290K
Sports           ████████████ $240K
Books            ██████ $120K
                 0    100K  200K  300K  400K  500K

- Horizontal bars (better for long labels)
- Sorted by value (descending)
- Direct labels (no legend needed)
- Start axis at zero
- Consistent bar width

❌ Bad:
- 3D bars
- Vertical bars with long rotated labels
- Unsorted (random order)
- Truncated Y-axis without indicator
- Decorative patterns instead of solid fills
```

**Code Example (Python/Plotly):**

```python
import plotly.graph_objects as go

fig = go.Figure(go.Bar(
    y=['Electronics', 'Home & Garden', 'Apparel', 'Sports', 'Books'],
    x=[450000, 380000, 290000, 240000, 120000],
    orientation='h',
    marker=dict(color='#0173B2'),  # Single color, no gradient
    text=['$450K', '$380K', '$290K', '$240K', '$120K'],
    textposition='outside'
))

fig.update_layout(
    title='Revenue by Product Category',
    xaxis_title='Revenue (USD)',
    yaxis_title='',
    showlegend=False,
    plot_bgcolor='white',
    font=dict(family='Inter, sans-serif', size=12),
    margin=dict(l=150, r=50, t=50, b=50)
)
```

#### 2. Line Charts (Trends Over Time)

**When to Use:**
- Continuous data over time
- Multiple series comparison
- Showing trends and patterns

**Best Practices:**

```
Monthly Active Users

500K ┤                                    ●━━━
     │                              ●━━━━━┘
400K ┤                        ●━━━━━┘
     │                  ●━━━━━┘
300K ┤            ●━━━━━┘
     │      ●━━━━━┘
200K ┤━━━━━━┘
     └─┬────┬────┬────┬────┬────┬────┬────┬────┬──
      Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep

- Maximum 5 lines per chart
- Direct labeling (not legend)
- Consistent line thickness (2-3px)
- Dashed lines for projections/targets
- Remove unnecessary gridlines
```

**Rules:**
1. **Limit lines**: Max 5 lines; use small multiples for more
2. **Time on X-axis**: Always left-to-right chronological
3. **Zero baseline**: Not required (unlike bar charts)
4. **Aspect ratio**: Typically 1.5:1 to 2:1 (width:height)

#### 3. Scatter Plots (Correlation)

**When to Use:**
- Showing relationship between two variables
- Identifying outliers
- Displaying distribution

**Example:**

```
Customer Lifetime Value vs. Acquisition Cost

CLV  │
$500 │           ●
     │         ●   ●
$400 │       ●   ●     ●
     │     ●   ●   ●         Target Zone:
$300 │   ●   ●       ●       CLV > 3× CAC
     │ ●   ●                 (shaded area)
$200 │●      [Outlier - Investigate]
     └─┬───┬───┬───┬───┬───┬──
      $0  $50 $100 $150 $200 $250
               Acquisition Cost (CAC)
```

**Best Practices:**
- Show trend line if correlation exists
- Annotate outliers if relevant
- Use transparency (alpha) if points overlap
- Add reference lines (y=x, targets)
- Size bubbles by √value (not value directly)

#### 4. Heatmaps (Two-Dimensional Patterns)

**When to Use:**
- Calendar/time patterns
- Correlation matrices
- Geographic distributions

**Example:**

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

**Best Practices:**
- Use diverging colors for +/- values
- Use sequential colors for magnitude only
- Add white borders between cells
- Include clear color scale
- Sort rows/columns meaningfully

#### 5. Tables (Precision Required)

**When to Use:**
- Exact values needed
- Mixed data types
- Lookup/reference
- Small datasets (<20 rows)

**Example:**

```
Product Performance Summary

Product    Revenue    Change  Margin  Status
─────────────────────────────────────────────
Widget A   $450K     ▲ 15%   42%     ● On track
Widget B   $380K     ▲ 8%    38%     ● On track
Widget C   $290K     ▼ 3%    35%     ◐ At risk
Widget D   $240K     ▼ 12%   28%     ○ Below
Widget E   $120K     ▲ 22%   45%     ● On track

Legend: ▲ Increase  ▼ Decrease  ● Green  ◐ Yellow  ○ Red
```

**Best Practices:**
- Right-align numbers, left-align text
- Use monospace font for numbers
- Zebra striping for >10 rows
- Highlight totals or key rows
- Minimize grid lines
- Sort by most important column
- Add sparklines for trends

---

## Dashboard Layout Patterns

### Design Principles (Stephen Few)

#### Dashboard Definition

> "A dashboard is a visual display of the most important information needed to achieve one or more objectives, consolidated and arranged on a single screen so the information can be monitored at a glance." - Stephen Few

**Key Characteristics:**
- **Visual**: Predominantly graphical
- **Important**: Only essential information
- **Single screen**: No scrolling for primary view
- **At a glance**: 5-second rule for comprehension

#### Dashboard Types

**1. Strategic Dashboard**
```
┌─────────────────────────────────────┐
│  Executive Scorecard           [i]  │
├─────────────────────────────────────┤
│  Revenue    Orders    Customers     │
│  $1.2M ↑8%  15,234    8,450        │
│  ───╱──     ───╱──    ─────╱──     │
├─────────────────────────────────────┤
│  KPI Performance vs. Target         │
│  [Bullet charts showing key metrics]│
└─────────────────────────────────────┘

Audience: Executives
Update: Daily/Weekly
Interaction: Minimal
```

**2. Analytical Dashboard**
```
┌─────────────────────────────────────┐
│ [Filters: Date|Region|Product|...]  │
├─────────────────────────────────────┤
│  Detailed Metrics with Drill-Down   │
│  [Multiple interactive charts]      │
│  [Segmentation capabilities]        │
│  [Export and analysis tools]        │
└─────────────────────────────────────┘

Audience: Analysts
Update: Real-time/Hourly
Interaction: Rich filtering, drill-down
```

**3. Operational Dashboard**
```
┌─────────────────────────────────────┐
│  System Status      [Live: 14:32:45]│
├─────────────────────────────────────┤
│  ● API Latency: 45ms     [Normal]   │
│  ⚠ Queue Depth: 15,234   [Warning]  │
│  🔴 Database CPU: 87%    [Critical] │
├─────────────────────────────────────┤
│  Real-Time Metrics                  │
│  [Streaming charts and alerts]      │
└─────────────────────────────────────┘

Audience: Operations teams
Update: Real-time/Streaming
Interaction: Action buttons, alerts
```

### The 5-Second Rule

Users should comprehend main message within 5 seconds.

**Techniques:**
- Use pre-attentive attributes (color, size, position)
- Highlight exceptions and outliers
- Include comparison indicators
- Minimize cognitive load

**Example:**

```
Revenue Performance

$1.2M  ↑ 8% vs. target    [GREEN]
       ↑ 12% vs. last month

Top 3:                    Bottom 3:
1. Product A  $450K ↑15%  1. Product X  $80K ↓22% [RED]
2. Product B  $380K ↑10%  2. Product Y  $75K ↓18% [RED]
3. Product C  $270K ↑8%   3. Product Z  $70K ↓12% [RED]
```

### Layout Patterns

#### F-Pattern Layout

Based on eye-tracking research - users scan in F-pattern:

```
┌─────────────────────────────────────┐
│  [KPI 1]  [KPI 2]  [KPI 3]  [KPI 4]│ ← First scan
│  ★ Most important                   │
├─────────────────────────────────────┤
│  ▌                                  │
│  ▌ [Large primary chart]            │ ← Vertical scan
│  ▌                                  │
│  ▌                                  │
├─────────────────────────────────────┤
│  ▌ [Chart]    [Chart]               │ ← Second scan
│  ▌                                  │
└─────────────────────────────────────┘
   ↑ Left edge anchor
```

**Implication**: Place most important information in **top-left**.

#### Grid System (12-Column)

Use consistent grid for alignment:

```
┌─1──2──3──4──5──6──7──8──9─10─11─12┐
│  ┌────────6────────┐┌────────6────┐│
│  │   KPI Card      ││  KPI Card   ││  2×6 columns
│  └─────────────────┘└─────────────┘│
├─────────────────────────────────────┤
│  ┌──────────────────12────────────┐ │
│  │     Main Chart                 │ │  1×12 columns
│  └────────────────────────────────┘ │
├─────────────────────────────────────┤
│  ┌──4──┐┌──4──┐┌──4──┐             │
│  │Chart││Chart││Chart│             │  3×4 columns
│  └─────┘└─────┘└─────┘             │
└─────────────────────────────────────┘
```

---

## Typography and Labeling

### Font Selection

**Sans-serif fonts** for dashboards (better screen readability):

```
Primary: Inter, Roboto, Open Sans, Source Sans Pro
Monospace (numbers/tables): Roboto Mono, Source Code Pro
```

### Font Sizes

```
Dashboard Title:        24-32px  (bold)
Section Headers:        18-20px  (semi-bold)
Chart Titles:           14-16px  (semi-bold)
Axis Labels:            11-12px  (regular)
Data Labels:            10-12px  (regular)
Footnotes/Metadata:     9-10px   (regular)
```

### Number Formatting

**Use tabular figures** (monospace numbers):

```
✅ Good (Tabular):     ❌ Bad (Proportional):
Revenue                Revenue
$1,234,567            $1,234,567
$  456,789            $456,789
$   89,012            $89,012
```

**Guidelines:**
- Right-align numbers in tables
- Use consistent decimal precision
- Add thousand separators (1,234,567)
- Round to appropriate precision ($1.2M not $1,234,567)

**Number Abbreviation:**

```
Amount          Display
$1,234          $1.2K
$1,234,567      $1.2M
$1,234,567,890  $1.2B

0.15            15%
0.0042          0.42%
```

### Label Best Practices

```
✅ Good:
Revenue (USD, millions)
Q1 2024 vs. Q1 2023

❌ Bad:
rev (ambiguous unit)
Revenue (is it USD? Millions?)
```

---

## Mobile-Responsive Design

### Mobile-First Principles

#### 1. Vertical Layout

**Desktop (16:9):**
```
┌────────────────────────────────┐
│ [KPI 1] [KPI 2] [KPI 3]       │
│ [Chart 1]    [Chart 2]         │
└────────────────────────────────┘
```

**Mobile (9:16):**
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

**Minimum touch target**: 44×44px (iOS) / 48×48px (Android)

```
✅ Good:
┌──────────────┐
│   Button     │  48px height
└──────────────┘

❌ Bad:
┌─────┐
│ Btn │  20px height - too small!
└─────┘
```

#### 3. Responsive Breakpoints

```css
/* Mobile first */
.dashboard-card {
  grid-column: span 12;  /* Full width */
}

/* Tablet (768px+) */
@media (min-width: 768px) {
  .dashboard-card {
    grid-column: span 6;  /* Half width */
  }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .dashboard-card {
    grid-column: span 4;  /* Third width */
  }
}
```

---

## Accessibility Standards

### WCAG 2.1 Levels

**Level AA (Target):**
- 4.5:1 contrast for normal text
- 3:1 for large text & UI
- Keyboard accessible
- No timing requirements

**Implementation Checklist:**

```markdown
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible (don't remove outline!)
- [ ] Color not used as only differentiator
- [ ] Alt text for all visualizations
- [ ] ARIA labels for screen readers
- [ ] Text resizable to 200%
- [ ] Contrast ratios meet WCAG AA
```

### Screen Reader Support

**ARIA Labels for Charts:**

```html
<div role="img" 
     aria-label="Line chart showing monthly revenue 
                 increasing from $1M in January to 
                 $1.5M in December">
  <svg><!-- Chart --></svg>
  
  <!-- Fallback table for screen readers -->
  <table class="sr-only">
    <caption>Monthly Revenue</caption>
    <tr><th>Month</th><th>Revenue</th></tr>
    <tr><td>January</td><td>$1,000,000</td></tr>
    <!-- ... -->
  </table>
</div>
```

### Keyboard Navigation

**Required shortcuts:**
```
Tab         → Next element
Shift+Tab   → Previous element
Enter/Space → Activate button
Arrow keys  → Navigate dropdown
Esc         → Close modal
```

---

## References and Further Reading

### Books

1. **Edward Tufte**
   - "The Visual Display of Quantitative Information" (1983)
   - "Envisioning Information" (1990)
   - "Visual Explanations" (1997)
   - "Beautiful Evidence" (2006)

2. **Stephen Few**
   - "Information Dashboard Design" (2nd Edition, 2013)
   - "Show Me the Numbers" (2nd Edition, 2012)
   - "Now You See It" (2009)

3. **Cole Nussbaumer Knaflic**
   - "Storytelling with Data" (2015)
   - "Storytelling with Data: Let's Practice!" (2019)

4. **Others**
   - Alberto Cairo: "The Functional Art" (2012)
   - Nathan Yau: "Visualize This" (2011)
   - Tamara Munzner: "Visualization Analysis and Design" (2014)

### Online Resources

- **Financial Times Visual Vocabulary**: Chart selection guide
- **Datawrapper Academy**: Free visualization courses
- **Observable**: D3.js examples and tutorials
- **FlowingData**: Nathan Yau's visualization blog
- **Tableau Public**: Gallery of best-in-class dashboards

### Tools

- **Color Oracle**: Colorblindness simulator
- **WebAIM Contrast Checker**: WCAG compliance
- **Coolors.co**: Color palette generator
- **ColorBrewer**: Cartography color schemes
- **Figma/Sketch**: Dashboard design mockups

---

**Document Version:** 1.0.0
**Last Updated:** 2024-01-15
**Maintained By:** BI Design Team
**Review Frequency:** Quarterly
