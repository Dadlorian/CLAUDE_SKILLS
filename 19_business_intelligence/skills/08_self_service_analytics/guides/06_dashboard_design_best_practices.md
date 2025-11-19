# Dashboard Design Best Practices Guide

## Core Principles

```yaml
1. Purpose Over Prettiness:
   - Every element serves a purpose
   - Remove decorative clutter
   - Focus on insights, not decoration

2. Show, Don't Tell:
   - Visualize trends, don't just show numbers
   - Use appropriate chart types
   - Highlight key insights

3. Design for Your Audience:
   - Executive: High-level, actionable
   - Analyst: Detailed, exploratory
   - Operational: Real-time, focused
```

## Layout Strategy

### The F-Pattern
```
Most Important Metric (Top Left)
├─ Supporting Metric
├─ Supporting Metric
└─ Trend Chart (Wide)

Secondary Metrics
├─ Chart 1
├─ Chart 2
└─ Chart 3

Details / Tables (Bottom)
```

### Information Hierarchy
```yaml
Level 1 - Headline (Top):
  - 1-3 key metrics (big numbers)
  - Trend indicators (↑ 15%)
  - Color coded (green=good, red=bad)

Level 2 - Context (Middle):
  - Trend charts
  - Comparisons
  - Breakdowns

Level 3 - Details (Bottom):
  - Tables
  - Drill-downs
  - Full data
```

## Chart Selection

```yaml
Trend Over Time → Line Chart:
  - Clear time progression
  - Multiple series comparable
  - Easy to spot patterns

Compare Categories → Bar Chart:
  - Easy to compare lengths
  - Sorted by value
  - Horizontal for long labels

Part-of-Whole → Stacked Bar or Treemap:
  - Avoid pie charts (>3 slices)
  - Stacked bars show trend + composition
  - Treemap for many categories

Distribution → Histogram or Box Plot:
  - Show data spread
  - Identify outliers
  - Understand variability

Correlation → Scatter Plot:
  - Relationship between variables
  - Clusters and outliers
  - Trend line helpful
```

## Performance Optimization

```yaml
Dashboard Load Time Target: <3 seconds

Optimization Techniques:

1. Limit Visualizations:
   - 5-8 charts maximum
   - Use tabs for more
   - Lazy load below fold

2. Pre-Aggregate Data:
   - Don't query raw tables
   - Use summary tables
   - Cache results

3. Efficient Filters:
   - Apply filters early
   - Use indexed columns
   - Reasonable default ranges

4. Simplify Queries:
   - Avoid complex calculations
   - Pre-compute in warehouse
   - Limit result sets
```

## Dashboard Checklist

```yaml
Before Publishing:
  □ Clear title and purpose
  □ Appropriate chart types
  □ Consistent color scheme
  □ Readable fonts (≥12pt)
  □ Filters work correctly
  □ Mobile-friendly layout
  □ Fast load time (<3s)
  □ Data source documented
  □ Owner/contact listed
  □ Tested with real users

Accessibility:
  □ Color-blind friendly palette
  □ Descriptive alt text
  □ High contrast
  □ Keyboard navigable
```

## Common Mistakes to Avoid

```yaml
❌ Too Many Charts:
   Problem: Overwhelming, slow
   Fix: Focus on 5-8 key insights

❌ Pie Charts with 10 Slices:
   Problem: Impossible to read
   Fix: Use bar chart or treemap

❌ 3D Charts:
   Problem: Misleading, hard to read
   Fix: Flat 2D always better

❌ Truncated Y-Axis:
   Problem: Exaggerates changes
   Fix: Start at zero or clearly label

❌ No Context:
   Problem: Numbers without meaning
   Fix: Add comparisons, trends, targets

❌ Rainbow Color Scheme:
   Problem: Confusing, no meaning
   Fix: Purposeful color (green=good, etc.)
```

## Quick Start Template

```yaml
Executive Dashboard:
  Row 1: KPI Summary
    - [Big Number: MRR] [Trend: ↑12%]
    - [Big Number: Customers] [Trend: ↑8%]
    - [Big Number: Churn] [Trend: ↓2%]

  Row 2: Trends
    - [Line Chart: Revenue Last 12 Months]
    - [Bar Chart: Top 10 Products]

  Row 3: Segments
    - [Stacked Bar: Revenue by Segment]
    - [Table: Regional Performance]

  Filters: Date Range, Segment, Region
```
