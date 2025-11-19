# Dashboard Implementation Guide

Step-by-step guide to building a dashboard using the templates and patterns in this directory.

## Quick Start: Build an Executive Dashboard in 30 Minutes

### Step 1: Set Up HTML Structure (5 min)

```bash
# Copy the executive dashboard template
cp executive_dashboard_template.html my-dashboard.html

# Link the CSS files
# Add these to your HTML <head>:
<link rel="stylesheet" href="src/dashboard_layout.css">
<link rel="stylesheet" href="src/responsive_utilities.css">
```

### Step 2: Configure Colors and Theme (5 min)

```javascript
// Load color scheme
import colors from './src/color_schemes.json';

// Apply to your charts
const chartColors = {
    primary: colors.few_recommended.colors.blue,
    highlight: colors.few_recommended.colors.orange,
    text: '#2C3E50'
};
```

### Step 3: Implement KPI Cards (10 min)

```html
<!-- Use this pattern for each KPI -->
<div class="kpi-card third-width">
    <div class="kpi-label">Monthly Revenue</div>
    <div class="kpi-value" id="revenue-value">$0</div>
    <div class="kpi-change positive" id="revenue-change">
        <span aria-label="increased by">▲</span> 0%
    </div>
    <div class="kpi-context">Target: $1.0M</div>
    <div class="kpi-sparkline" id="revenue-sparkline"></div>
</div>
```

```javascript
// Populate with data
async function loadKPIs() {
    const data = await fetch('/api/kpis').then(r => r.json());
    
    document.getElementById('revenue-value').textContent =
        DataTransformers.formatLargeNumber(data.revenue);
    document.getElementById('revenue-change').textContent =
        `▲ ${data.revenueChange}%`;
}
```

### Step 4: Add Filters (5 min)

```javascript
import { SingleApplyFilter } from './src/filter_patterns.js';

const filter = new SingleApplyFilter('my-dashboard');

// Attach to HTML controls
document.getElementById('date-range').addEventListener('change', (e) => {
    filter.selectFilter('date_range', e.target.value);
});

document.getElementById('apply-btn').addEventListener('click', () => {
    filter.applyFilters();
});
```

### Step 5: Implement Performance Monitoring (5 min)

```javascript
import PerformanceMonitor from './src/performance_monitor.js';

const monitor = new PerformanceMonitor('my-dashboard');
monitor.startLoad();

// Monitor queries
const data = await monitor.monitorQuery('main_query', loadData);

// Monitor renders
monitor.monitorRender('revenue-chart', () => renderChart(data));

// End monitoring
monitor.endLoad();
```

## Detailed Implementations

### Implementing Sparklines

```javascript
// Use the sparkline generator
function addSparkline(containerId, data) {
    const svg = generateSparkline(data, 100, 20);
    document.getElementById(containerId).innerHTML = svg;
}

// Add to KPI card
addSparkline('revenue-sparkline', [100, 110, 105, 120, 115, 130]);
```

### Implementing Bullet Charts

```javascript
// Create bullet chart from template
function createBulletChart(actual, target, max) {
    return `
        <svg width="300" height="30">
            <!-- Ranges -->
            <rect x="0" y="0" width="${300 * 0.6}" height="30" fill="#F0F0F0"/>
            <rect x="${300 * 0.6}" y="0" width="${300 * 0.2}" height="30" fill="#D0D0D0"/>
            <rect x="${300 * 0.8}" y="0" width="${300 * 0.2}" height="30" fill="#B0B0B0"/>
            
            <!-- Actual bar -->
            <rect x="0" y="7.5" width="${300 * (actual / max)}" height="15" fill="#2C3E50"/>
            
            <!-- Target line -->
            <line x1="${300 * (target / max)}" y1="0" 
                  x2="${300 * (target / max)}" y2="30" 
                  stroke="#E74C3C" stroke-width="2"/>
        </svg>
    `;
}
```

### Implementing Drill-Down

```javascript
import { DrillDownController } from './src/drill_down_example.js';

const drillDown = new DrillDownController();

// Start at overview
drillDown.renderOverview();

// Click handler for chart elements
chart.on('click', (event) => {
    if (drillDown.currentLevel === 1) {
        drillDown.drillToRegion(event.data.region);
    }
});
```

### Implementing Accessibility

```javascript
import {
    ARIALabelGenerator,
    ScreenReaderAnnouncer,
    ContrastChecker
} from './src/accessibility_helpers.js';

// Add ARIA labels to charts
const chartLabel = ARIALabelGenerator.forChart(
    'line chart',
    data,
    'Revenue Trend'
);
chart.setAttribute('aria-label', chartLabel);

// Announce updates to screen readers
const announcer = new ScreenReaderAnnouncer();
filter.on('apply', () => {
    announcer.announce('Dashboard updated with new filters');
});

// Check color contrast
const contrast = ContrastChecker.meetsWCAG_AA('#2C3E50', '#FFFFFF');
console.log(`Contrast ratio: ${contrast.ratio}, Passes: ${contrast.passes}`);
```

## Platform-Specific Implementations

### Tableau

1. Create dashboard shell in Tableau Desktop
2. Import color scheme from `color_schemes.json`
3. Use XML structure from `tableau_dashboard_xml.xml` as guide
4. Apply KPI SQL from `kpi_calculations.sql`
5. Use performance recording to optimize

### Power BI

1. Create new report
2. Import theme from `powerbi_theme.json`
3. Use DAX equivalents of SQL from `kpi_calculations.sql`
4. Apply layout patterns from `dashboard_layout.css`
5. Use accessibility features from `accessibility_helpers.js` concepts

### Looker

1. Create new dashboard
2. Use `looker_dashboard_example.lkml` as template
3. Adapt KPI calculations to LookML
4. Apply color schemes from JSON
5. Use parameter configurations for filters

## Common Patterns

### Loading State

```javascript
function showLoading(isLoading) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = isLoading ? 'flex' : 'none';
}

async function loadDashboard() {
    showLoading(true);
    try {
        const data = await fetchData();
        renderDashboard(data);
    } catch (error) {
        showError(error);
    } finally {
        showLoading(false);
    }
}
```

### Error Handling

```javascript
function showError(error) {
    const alertBanner = document.createElement('div');
    alertBanner.className = 'alert-banner alert-critical';
    alertBanner.innerHTML = `
        <strong>Error loading dashboard:</strong> ${error.message}
        <button onclick="retry()">Retry</button>
    `;
    document.querySelector('.dashboard-container').prepend(alertBanner);
}
```

### Responsive Charts

```javascript
import chartConfigs from './src/chart_configs.json';

function createResponsiveChart(containerId, data) {
    const width = window.innerWidth;
    let config;
    
    if (width < 768) {
        config = chartConfigs.responsive_breakpoints.mobile;
    } else if (width < 1024) {
        config = chartConfigs.responsive_breakpoints.tablet;
    } else {
        config = chartConfigs.responsive_breakpoints.desktop;
    }
    
    return createChart(containerId, data, config);
}

window.addEventListener('resize', debounce(() => {
    recreateAllCharts();
}, 250));
```

## Testing Checklist

Before deploying your dashboard:

- [ ] Load time < 3 seconds
- [ ] All KPIs display correctly
- [ ] Filters work and update all charts
- [ ] Drill-down navigation functions
- [ ] Mobile layout tested on real device
- [ ] Accessibility: keyboard navigation works
- [ ] Accessibility: screen reader tested
- [ ] Accessibility: color contrast checked
- [ ] Performance: no console errors
- [ ] Performance: all queries < 2 seconds

## Troubleshooting

### Dashboard loads slowly
1. Check query performance using `performance_monitor.js`
2. Review SQL optimization in `kpi_calculations.sql`
3. Implement caching
4. Reduce number of simultaneous queries

### Colors don't look right
1. Verify using color_schemes.json palettes
2. Check color contrast with `accessibility_helpers.js`
3. Test with color blindness simulator

### Mobile layout broken
1. Review responsive_utilities.css breakpoints
2. Test with mobile_dashboard_layout.html as reference
3. Ensure touch targets >= 44px

### Filters not working
1. Check filter_patterns.js implementation
2. Verify filter state is being applied
3. Check browser console for errors

## Next Steps

1. Customize templates for your specific data
2. Add company branding (logo, colors)
3. Implement automated testing
4. Set up monitoring and analytics
5. Gather user feedback and iterate

## Support

- Review reference/ directory for design patterns
- Check guides/ directory for detailed tutorials
- See README.md for additional documentation
