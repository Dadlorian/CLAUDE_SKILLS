# Dashboard Templates and Code Examples

This directory contains practical templates, code examples, and configuration files for building effective business intelligence dashboards based on the principles of Stephen Few, Edward Tufte, and Cole Nussbaumer Knaflic.

## Directory Contents

### Color and Design
- `color_schemes.json` - Comprehensive color palette definitions (Few/Tufte compliant)
- `dashboard_layout.css` - 12-column responsive grid system
- `responsive_utilities.css` - Mobile-first responsive utilities

### Platform-Specific Templates
- `powerbi_theme.json` - Power BI theme configuration
- `tableau_dashboard_xml.xml` - Tableau dashboard XML structure
- `looker_dashboard_example.lkml` - Looker LookML dashboard example

### HTML Templates
- `executive_dashboard_template.html` - Executive dashboard HTML template
- `mobile_dashboard_layout.html` - Mobile-first dashboard layout
- `sparkline_examples.html` - Tufte sparkline implementations
- `bullet_chart_examples.html` - Stephen Few bullet charts

### JavaScript Patterns
- `filter_patterns.js` - Filter interaction patterns (single-apply, cascading, searchable)
- `drill_down_example.js` - Three-level drill-down implementation
- `accessibility_helpers.js` - WCAG 2.1 AA compliance utilities

### Data and Configuration
- `kpi_calculations.sql` - SQL queries for common business KPIs
- `parameter_configurations.json` - Reusable filter and parameter configs

## Usage

### Quick Start - Executive Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="src/dashboard_layout.css">
    <link rel="stylesheet" href="src/responsive_utilities.css">
</head>
<body>
    <!-- Use executive_dashboard_template.html as starting point -->
</body>
</html>
```

### Implementing Filters

```javascript
import { SingleApplyFilter } from './src/filter_patterns.js';

const filter = new SingleApplyFilter('my-dashboard');
filter.selectFilter('date_range', 'last_30_days');
filter.selectFilter('region', 'north');
filter.applyFilters();
```

### Creating Sparklines

```javascript
// See sparkline_examples.html for SVG-based sparklines
// Or use the JavaScript generator:
const data = [100, 110, 105, 120, 115, 130];
const sparkline = generateSparkline(data, 100, 20);
```

### KPI Calculations

```sql
-- See kpi_calculations.sql for common metrics
-- Example: Monthly Recurring Revenue
SELECT
  DATE_TRUNC('month', subscription_start_date) AS month,
  SUM(monthly_amount) AS mrr
FROM subscriptions
WHERE status = 'active'
GROUP BY 1;
```

## Platform-Specific Usage

### Tableau
1. Import `tableau_dashboard_xml.xml` as starting structure
2. Use color_schemes.json for palette configuration
3. Apply Few-Tufte principles from documentation

### Power BI
1. Import `powerbi_theme.json` as custom theme
2. Use accessibility_helpers.js patterns for compliance
3. Reference dashboard_layout.css for design patterns

### Looker
1. Use `looker_dashboard_example.lkml` as template
2. Adapt KPI calculations from kpi_calculations.sql
3. Apply color schemes from color_schemes.json

## Best Practices

1. **Start with Templates**: Use provided templates as starting point
2. **Mobile-First**: Use responsive utilities for all dashboards
3. **Accessibility**: Implement helpers from accessibility_helpers.js
4. **Color**: Use palettes from color_schemes.json (color-blind safe)
5. **Performance**: Optimize queries using kpi_calculations.sql patterns

## Color Palette Usage

```javascript
// Load color scheme
import colors from './src/color_schemes.json';

// Use Few's recommended palette
const palette = colors.few_recommended.colors;
console.log(palette.blue); // #5DA5DA

// Check accessibility
const statusColors = colors.status_colors.accessible;
console.log(statusColors.critical); // {color: "#DC143C", icon: "⚠️"}
```

## Contributing

When adding new templates or examples:
1. Follow Few-Tufte-Knaflic principles
2. Include accessibility features
3. Provide usage documentation
4. Test on mobile devices
5. Validate color contrast

## References

- Stephen Few: "Information Dashboard Design"
- Edward Tufte: "The Visual Display of Quantitative Information"  
- Cole Nussbaumer Knaflic: "Storytelling with Data"
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
