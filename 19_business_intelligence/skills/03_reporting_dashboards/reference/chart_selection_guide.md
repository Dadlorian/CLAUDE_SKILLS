# Chart Selection Guide - The Few-Tufte Method

## Decision Framework

### Step 1: Identify the Relationship
What are you trying to show?
- **Comparison**: How do values compare to each other?
- **Distribution**: How is data spread across a range?
- **Composition**: What are the parts of a whole?
- **Relationship**: How do two or more variables relate?
- **Trend**: How do values change over time?

### Step 2: Select the Appropriate Chart

## Comparison Charts

### Bar Chart (Horizontal)
**Use When:**
- Comparing categories (nominal data)
- Category names are long
- More than 5-7 categories

**Best Practices:**
- Order bars by value (descending) unless natural order exists
- Start axis at zero
- Use single color unless highlighting specific bars
- Label values directly on or near bars
- Maximum ~20 bars before considering alternatives

**Avoid:**
- 3D effects
- Unnecessary gridlines
- Decorative fills or patterns

### Column Chart (Vertical)
**Use When:**
- Comparing categories with short labels
- Showing time series with discrete periods
- 5-7 or fewer categories

**Best Practices:**
- Start axis at zero (exception: showing small variations in large values)
- Consistent bar width
- Adequate spacing between bars
- Direct labeling when space permits

### Bullet Chart (Stephen Few)
**Use When:**
- Showing performance against target
- Limited space
- Multiple related metrics in small multiples

**Components:**
- Featured measure (actual value) - dark bar
- Comparative measure (target) - vertical line
- Qualitative ranges (poor/satisfactory/good) - background shades

**Best Practices:**
- Use grayscale for ranges, color for featured measure only if needed
- Align multiple bullet charts for easy comparison
- Keep scale consistent across related metrics

## Time Series Charts

### Line Chart
**Use When:**
- Showing continuous change over time
- Multiple series comparison (max 4-5 lines)
- Dense time periods (many data points)

**Best Practices:**
- Direct labeling of lines (avoid legend when possible)
- Highlight most important line with color/weight
- Use different line styles only if color unavailable
- Show full time range relevant to context
- Remove chartjunk (gridlines, 3D, backgrounds)

**Tufte Enhancement:**
- Consider sparklines for small multiples
- Use data-ink ratio principle
- Remove redundant axis labels

### Sparkline (Edward Tufte)
**Use When:**
- Showing trend in context of other data
- Space is limited (table cells, scorecards)
- Pattern recognition more important than exact values

**Best Practices:**
- Keep simple - line only, no axes or labels
- Optionally highlight first, last, min, max points
- Use consistent scale across related sparklines
- Typical size: 1-2cm wide, 0.5cm high

### Area Chart
**Use When:**
- Showing cumulative total over time
- Part-to-whole over time (stacked area)

**Caution:**
- Difficult to read values for middle layers in stacked version
- Use only when total is as important as components
- Consider small multiples of line charts as alternative

## Distribution Charts

### Histogram
**Use When:**
- Showing distribution of continuous variable
- Understanding data shape (normal, skewed, bimodal)

**Best Practices:**
- Choose bin width carefully (too few = loss of detail, too many = noise)
- Start y-axis at zero
- No gaps between bars (continuous data)
- Label axes clearly including units

### Box Plot (Box and Whisker)
**Use When:**
- Comparing distributions across categories
- Identifying outliers
- Showing median and quartiles

**Best Practices:**
- Order boxes by median or natural order
- Explain components clearly (many users unfamiliar)
- Consider violin plot for detailed distribution shape
- Limit to comparing 5-7 distributions

### Dot Plot (Cleveland)
**Use When:**
- Showing distribution with small datasets
- Each data point matters
- Alternative to bar chart for precise comparison

**Best Practices:**
- Align dots on baseline for comparison
- Use sparingly with categorical data
- Excellent for small multiples

## Composition Charts

### Stacked Bar Chart
**Use When:**
- Showing part-to-whole across categories
- Total value is important
- Limited number of components (2-4 ideal, max 6)

**Best Practices:**
- Place most important segment at baseline
- Use diverging stack for positive/negative
- Direct labeling of segments when possible
- Consistent color scheme across charts

### Treemap
**Use When:**
- Showing hierarchical part-to-whole
- Space efficiency needed
- Many categories to display

**Caution:**
- Difficult to compare similar-sized rectangles
- Poor for precise value comparison
- Use size + color encoding carefully

### AVOID: Pie Charts (Stephen Few's Position)
**Why to Avoid:**
- Humans poor at comparing angles and areas
- Difficult with more than 2-3 slices
- Labels often cluttered
- Takes more space than alternatives

**Better Alternative:**
- Horizontal bar chart (easier comparison)
- Bullet chart with % of total
- Treemap for hierarchical data

**Only Acceptable Use:**
- Exactly 2 categories showing simple proportion
- Better: use text "X% of total" or small bar

## Relationship Charts

### Scatter Plot
**Use When:**
- Showing relationship between 2 variables
- Identifying correlation or clusters
- Detecting outliers

**Best Practices:**
- Add trend line if relationship exists
- Use size for 3rd dimension (bubble chart)
- Color for categorical 4th dimension
- Label outliers and important points
- Include R² if showing correlation

**Tufte Enhancement:**
- Remove gridlines or make very subtle
- Consider rug plot on margins
- Use small multiples for categories

### Scatter Plot Matrix
**Use When:**
- Exploring relationships among multiple variables
- Initial data exploration
- Identifying interesting correlations

**Best Practices:**
- Limit to 5-7 variables
- Use consistent scales
- Highlight interesting correlations

## Specialized Charts

### Heatmap
**Use When:**
- Showing patterns in matrix data
- Time + category combinations
- Correlation matrices

**Best Practices:**
- Use sequential color scheme for continuous data
- Use diverging scheme for data with meaningful midpoint
- Keep color scheme simple (2-3 colors max)
- Provide clear legend
- Consider sorting by value to reveal patterns

### Slope Chart (Tufte)
**Use When:**
- Comparing exactly 2 time points
- Showing change for multiple categories
- Before/after comparisons

**Best Practices:**
- Direct labeling of all lines
- Highlight most important changes
- Limit to 15-20 lines maximum
- Use rank order if many lines

### Waterfall Chart
**Use When:**
- Showing cumulative effect of sequential values
- Revenue/cost breakdowns
- Bridge from one value to another

**Best Practices:**
- Use color to distinguish positive/negative
- Label all segments
- Show clear baseline
- Connect segments with lines

## Chart Selection Matrix

| Purpose | Best Choice | Alternative | Avoid |
|---------|-------------|-------------|-------|
| Compare categories | Horizontal bar | Dot plot | Pie, 3D column |
| Part-to-whole | Stacked bar | Treemap | Pie (>2 slices) |
| Trend over time | Line chart | Sparkline | Area (unless cumulative) |
| Distribution | Histogram | Box plot | Pie |
| Correlation | Scatter plot | Heatmap | Line chart |
| Performance vs target | Bullet chart | Bar + reference line | Gauge |
| 2-point comparison | Slope chart | Paired bar | Line (only 2 points) |
| Small space trend | Sparkline | Tiny line | Any complex chart |

## Tufte's Principles Applied

1. **Data-Ink Ratio**: Maximize proportion of ink used for data
   - Remove gridlines or make subtle
   - Eliminate backgrounds
   - Remove redundant labels
   - Eliminate chartjunk

2. **Chartjunk**: Elements that don't add information
   - 3D effects
   - Shadows and gradients
   - Decorative pictures
   - Excessive color
   - Unnecessary gridlines

3. **Data Density**: Good graphics are information-dense
   - Use small multiples instead of overlays
   - Direct labeling instead of legends
   - Integrated text and graphics
   - Maximize information per square inch

## Quick Decision Tree

```
What are you showing?

├─ Values over time?
│  ├─ Continuous change → Line chart
│  ├─ Discrete periods → Column chart
│  └─ Space limited → Sparkline
│
├─ Comparing categories?
│  ├─ Simple comparison → Horizontal bar
│  ├─ With target → Bullet chart
│  └─ Two time points → Slope chart
│
├─ Part of whole?
│  ├─ Single total → Stacked bar (not pie)
│  ├─ Hierarchical → Treemap
│  └─ Over time → Stacked area
│
├─ Distribution?
│  ├─ Single variable → Histogram
│  ├─ Multiple groups → Box plot
│  └─ Small data → Dot plot
│
└─ Relationship?
   ├─ Two variables → Scatter plot
   ├─ Many variables → Scatter matrix
   └─ Matrix patterns → Heatmap
```

## References
- Stephen Few: "Show Me the Numbers" and "Information Dashboard Design"
- Edward Tufte: "The Visual Display of Quantitative Information"
- William Cleveland: "The Elements of Graphing Data"
- Cole Nussbaumer Knaflic: "Storytelling with Data"
