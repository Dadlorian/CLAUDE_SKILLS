# KPI Dashboards Reference

Comprehensive guide to designing, building, and maintaining effective KPI dashboards for business analytics.

## Dashboard Design Principles

### 1. Know Your Audience

**Executive Dashboard** (C-Suite):
- High-level metrics only
- Trend indicators
- Year-over-year comparisons
- Exception highlighting
- Minimal detail, maximum insight

**Operational Dashboard** (Managers):
- Real-time or daily metrics
- Drill-down capabilities
- Comparative analysis
- Actionable insights
- Team performance tracking

**Analytical Dashboard** (Analysts):
- Detailed metrics
- Custom date ranges
- Segmentation options
- Export capabilities
- Deep-dive analysis tools

### 2. Visual Hierarchy

```python
DASHBOARD_LAYOUT_PRIORITIES = {
    'Top Left': 'Most important metric (primary focus)',
    'Top Right': 'Secondary important metric',
    'Center': 'Main visualization/trend chart',
    'Bottom': 'Supporting details and breakdowns',
    'Sidebar': 'Filters and controls'
}

VISUAL_BEST_PRACTICES = {
    'KPI Cards': 'Single metrics with context (vs previous period)',
    'Line Charts': 'Trends over time',
    'Bar Charts': 'Comparisons across categories',
    'Pie Charts': 'Composition (use sparingly, max 5-6 segments)',
    'Tables': 'Detailed data (bottom of dashboard)',
    'Heatmaps': 'Multi-dimensional patterns',
    'Sparklines': 'Inline trends in tables'
}
```

### 3. The 5-Second Rule

**Users should understand the key insight within 5 seconds of viewing.**

## Essential Dashboard Components

### 1. KPI Summary Cards

```sql
-- Executive summary metrics
WITH current_period AS (
  SELECT
    SUM(revenue) as revenue,
    COUNT(DISTINCT customer_id) as customers,
    COUNT(DISTINCT order_id) as orders,
    SUM(revenue) / COUNT(DISTINCT customer_id) as revenue_per_customer
  FROM orders
  WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE)
),
previous_period AS (
  SELECT
    SUM(revenue) as revenue,
    COUNT(DISTINCT customer_id) as customers,
    COUNT(DISTINCT order_id) as orders,
    SUM(revenue) / COUNT(DISTINCT customer_id) as revenue_per_customer
  FROM orders
  WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
    AND order_date < DATE_TRUNC('month', CURRENT_DATE)
)
SELECT
  'Total Revenue' as metric,
  TO_CHAR(cp.revenue, '$999,999,999') as current_value,
  TO_CHAR(pp.revenue, '$999,999,999') as previous_value,
  ROUND((cp.revenue - pp.revenue) * 100.0 / NULLIF(pp.revenue, 0), 1) as change_pct,
  CASE
    WHEN cp.revenue > pp.revenue THEN '↑'
    WHEN cp.revenue < pp.revenue THEN '↓'
    ELSE '→'
  END as trend_indicator
FROM current_period cp
CROSS JOIN previous_period pp

UNION ALL

SELECT
  'Total Customers',
  TO_CHAR(cp.customers, '999,999'),
  TO_CHAR(pp.customers, '999,999'),
  ROUND((cp.customers - pp.customers) * 100.0 / NULLIF(pp.customers, 0), 1),
  CASE
    WHEN cp.customers > pp.customers THEN '↑'
    WHEN cp.customers < pp.customers THEN '↓'
    ELSE '→'
  END
FROM current_period cp
CROSS JOIN previous_period pp

UNION ALL

SELECT
  'Total Orders',
  TO_CHAR(cp.orders, '999,999'),
  TO_CHAR(pp.orders, '999,999'),
  ROUND((cp.orders - pp.orders) * 100.0 / NULLIF(pp.orders, 0), 1),
  CASE
    WHEN cp.orders > pp.orders THEN '↑'
    WHEN cp.orders < pp.orders THEN '↓'
    ELSE '→'
  END
FROM current_period cp
CROSS JOIN previous_period pp

UNION ALL

SELECT
  'Revenue per Customer',
  TO_CHAR(cp.revenue_per_customer, '$999,999'),
  TO_CHAR(pp.revenue_per_customer, '$999,999'),
  ROUND((cp.revenue_per_customer - pp.revenue_per_customer) * 100.0 /
        NULLIF(pp.revenue_per_customer, 0), 1),
  CASE
    WHEN cp.revenue_per_customer > pp.revenue_per_customer THEN '↑'
    WHEN cp.revenue_per_customer < pp.revenue_per_customer THEN '↓'
    ELSE '→'
  END
FROM current_period cp
CROSS JOIN previous_period pp;
```

### 2. Trend Visualizations

```sql
-- Daily revenue trend (last 30 days)
SELECT
  DATE(order_date) as date,
  SUM(revenue) as daily_revenue,
  AVG(SUM(revenue)) OVER (
    ORDER BY DATE(order_date)
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) as moving_avg_7day,
  SUM(revenue) - LAG(SUM(revenue), 7) OVER (ORDER BY DATE(order_date)) as wow_change
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1;
```

### 3. Comparison Charts

```sql
-- Year-over-year comparison by month
SELECT
  TO_CHAR(order_date, 'Mon') as month,
  EXTRACT(YEAR FROM order_date) as year,
  SUM(revenue) as revenue
FROM orders
WHERE order_date >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 year'
GROUP BY 1, 2
ORDER BY EXTRACT(MONTH FROM MIN(order_date)), 2;
```

## Dashboard Templates by Use Case

### Executive Dashboard

```sql
-- Executive KPI Dashboard
CREATE OR REPLACE VIEW executive_dashboard AS
WITH metrics AS (
  SELECT
    -- Time period
    DATE_TRUNC('month', CURRENT_DATE) as period,

    -- Revenue metrics
    (SELECT SUM(revenue) FROM orders WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE)) as mtd_revenue,
    (SELECT SUM(revenue) FROM orders WHERE order_date >= DATE_TRUNC('quarter', CURRENT_DATE)) as qtd_revenue,
    (SELECT SUM(revenue) FROM orders WHERE order_date >= DATE_TRUNC('year', CURRENT_DATE)) as ytd_revenue,

    -- Customer metrics
    (SELECT COUNT(DISTINCT customer_id) FROM orders WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE)) as mtd_customers,

    -- Growth metrics
    (SELECT AVG(mrr_growth_rate) FROM monthly_metrics WHERE month >= CURRENT_DATE - INTERVAL '3 months') as avg_growth_rate,

    -- Unit economics
    (SELECT AVG(ltv) / NULLIF(AVG(cac), 0) FROM customer_cohorts
     WHERE cohort_month >= CURRENT_DATE - INTERVAL '6 months') as ltv_cac_ratio,

    -- Retention
    (SELECT AVG(retention_rate) FROM monthly_retention WHERE month >= CURRENT_DATE - INTERVAL '3 months') as avg_retention_rate
)
SELECT * FROM metrics;
```

### Marketing Dashboard

```sql
-- Marketing Performance Dashboard
CREATE OR REPLACE VIEW marketing_dashboard AS
SELECT
  channel,
  -- Traffic
  SUM(sessions) as total_sessions,
  SUM(users) as total_users,

  -- Conversion
  SUM(conversions) as total_conversions,
  ROUND(SUM(conversions) * 100.0 / NULLIF(SUM(sessions), 0), 2) as conversion_rate,

  -- Revenue
  SUM(revenue) as total_revenue,
  SUM(revenue) / NULLIF(SUM(conversions), 0) as revenue_per_conversion,

  -- Cost & ROI
  SUM(cost) as total_cost,
  SUM(cost) / NULLIF(SUM(conversions), 0) as cac,
  SUM(revenue) / NULLIF(SUM(cost), 0) as roas,

  -- Efficiency
  SUM(cost) / NULLIF(SUM(sessions), 0) as cost_per_session,
  SUM(cost) / NULLIF(SUM(users), 0) as cost_per_user
FROM marketing_performance
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY total_revenue DESC;
```

### Product Analytics Dashboard

```sql
-- Product Engagement Dashboard
CREATE OR REPLACE VIEW product_dashboard AS
WITH daily_metrics AS (
  SELECT
    DATE(event_timestamp) as date,
    COUNT(DISTINCT user_id) as dau,
    COUNT(DISTINCT session_id) as sessions,
    COUNT(*) as events,
    AVG(session_duration_seconds) / 60 as avg_session_minutes
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY 1
),
monthly_metrics AS (
  SELECT
    COUNT(DISTINCT user_id) as mau
  FROM events
  WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
  dm.date,
  dm.dau,
  mm.mau,
  ROUND(dm.dau * 100.0 / NULLIF(mm.mau, 0), 2) as stickiness_ratio,
  dm.sessions,
  dm.sessions * 1.0 / dm.dau as sessions_per_user,
  dm.events * 1.0 / dm.sessions as events_per_session,
  dm.avg_session_minutes
FROM daily_metrics dm
CROSS JOIN monthly_metrics mm
ORDER BY dm.date DESC;
```

### Sales Dashboard

```sql
-- Sales Performance Dashboard
CREATE OR REPLACE VIEW sales_dashboard AS
WITH sales_rep_metrics AS (
  SELECT
    sales_rep_id,
    sales_rep_name,
    -- Current month
    COUNT(DISTINCT CASE WHEN close_date >= DATE_TRUNC('month', CURRENT_DATE)
          THEN deal_id END) as mtd_deals,
    SUM(CASE WHEN close_date >= DATE_TRUNC('month', CURRENT_DATE)
        THEN deal_value ELSE 0 END) as mtd_revenue,

    -- Quarter
    COUNT(DISTINCT CASE WHEN close_date >= DATE_TRUNC('quarter', CURRENT_DATE)
          THEN deal_id END) as qtd_deals,
    SUM(CASE WHEN close_date >= DATE_TRUNC('quarter', CURRENT_DATE)
        THEN deal_value ELSE 0 END) as qtd_revenue,

    -- Pipeline
    COUNT(DISTINCT CASE WHEN stage = 'negotiation' THEN deal_id END) as deals_in_negotiation,
    SUM(CASE WHEN stage = 'negotiation' THEN deal_value ELSE 0 END) as pipeline_value,

    -- Win rate
    COUNT(DISTINCT CASE WHEN status = 'won'
          AND close_date >= CURRENT_DATE - INTERVAL '90 days' THEN deal_id END) * 100.0 /
    NULLIF(COUNT(DISTINCT CASE WHEN status IN ('won', 'lost')
          AND close_date >= CURRENT_DATE - INTERVAL '90 days' THEN deal_id END), 0) as win_rate
  FROM deals
  GROUP BY 1, 2
),
quotas AS (
  SELECT
    sales_rep_id,
    monthly_quota,
    quarterly_quota
  FROM sales_quotas
  WHERE period = DATE_TRUNC('month', CURRENT_DATE)
)
SELECT
  s.*,
  q.monthly_quota,
  q.quarterly_quota,
  ROUND(s.mtd_revenue * 100.0 / NULLIF(q.monthly_quota, 0), 1) as monthly_quota_attainment,
  ROUND(s.qtd_revenue * 100.0 / NULLIF(q.quarterly_quota, 0), 1) as quarterly_quota_attainment
FROM sales_rep_metrics s
LEFT JOIN quotas q ON s.sales_rep_id = q.sales_rep_id
ORDER BY s.mtd_revenue DESC;
```

## Real-Time Dashboard Patterns

### 1. Live Metrics

```sql
-- Real-time activity (last hour)
SELECT
  DATE_TRUNC('minute', event_timestamp) as minute,
  COUNT(DISTINCT user_id) as active_users,
  COUNT(*) as events,
  COUNT(DISTINCT CASE WHEN event_type = 'conversion' THEN user_id END) as conversions
FROM events
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY 1
ORDER BY 1 DESC;
```

### 2. Alert Thresholds

```sql
-- Dashboard alerts for anomalies
WITH current_metrics AS (
  SELECT
    COUNT(DISTINCT user_id) as current_hour_users,
    COUNT(*) as current_hour_events
  FROM events
  WHERE event_timestamp >= DATE_TRUNC('hour', CURRENT_TIMESTAMP)
),
baseline AS (
  SELECT
    AVG(hourly_users) as avg_users,
    STDDEV(hourly_users) as stddev_users,
    AVG(hourly_events) as avg_events,
    STDDEV(hourly_events) as stddev_events
  FROM (
    SELECT
      DATE_TRUNC('hour', event_timestamp) as hour,
      COUNT(DISTINCT user_id) as hourly_users,
      COUNT(*) as hourly_events
    FROM events
    WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
      AND event_timestamp < CURRENT_TIMESTAMP - INTERVAL '1 hour'
      AND EXTRACT(HOUR FROM event_timestamp) = EXTRACT(HOUR FROM CURRENT_TIMESTAMP)
    GROUP BY 1
  ) hourly_stats
)
SELECT
  cm.current_hour_users,
  b.avg_users,
  CASE
    WHEN cm.current_hour_users < b.avg_users - (2 * b.stddev_users) THEN 'ALERT: Traffic significantly below normal'
    WHEN cm.current_hour_users > b.avg_users + (2 * b.stddev_users) THEN 'ALERT: Traffic significantly above normal'
    ELSE 'Normal'
  END as users_alert,
  cm.current_hour_events,
  b.avg_events,
  CASE
    WHEN cm.current_hour_events < b.avg_events - (2 * b.stddev_events) THEN 'ALERT: Activity significantly below normal'
    WHEN cm.current_hour_events > b.avg_events + (2 * b.stddev_events) THEN 'ALERT: Activity significantly above normal'
    ELSE 'Normal'
  END as events_alert
FROM current_metrics cm
CROSS JOIN baseline b;
```

## Python Dashboard Examples

### Plotly Dash Dashboard

```python
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta

# Initialize Dash app
app = dash.Dash(__name__)

# Sample data function
def get_data(days=30):
    """Fetch dashboard data"""
    # In practice, this would query your database
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'revenue': np.random.randint(10000, 50000, days),
        'users': np.random.randint(500, 2000, days),
        'orders': np.random.randint(200, 800, days)
    })
    return data

# Layout
app.layout = html.Div([
    html.H1('Business Analytics Dashboard', style={'textAlign': 'center'}),

    # Filters
    html.Div([
        html.Label('Date Range:'),
        dcc.Dropdown(
            id='date-range',
            options=[
                {'label': 'Last 7 Days', 'value': 7},
                {'label': 'Last 30 Days', 'value': 30},
                {'label': 'Last 90 Days', 'value': 90}
            ],
            value=30
        )
    ], style={'width': '200px', 'margin': '20px'}),

    # KPI Cards
    html.Div([
        html.Div([
            html.H3('Total Revenue'),
            html.H2(id='total-revenue'),
            html.P(id='revenue-change')
        ], className='kpi-card'),

        html.Div([
            html.H3('Total Users'),
            html.H2(id='total-users'),
            html.P(id='users-change')
        ], className='kpi-card'),

        html.Div([
            html.H3('Total Orders'),
            html.H2(id='total-orders'),
            html.P(id='orders-change')
        ], className='kpi-card'),
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    # Charts
    dcc.Graph(id='revenue-trend'),
    dcc.Graph(id='metrics-comparison'),

    # Refresh interval (update every 60 seconds)
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)
])

# Callbacks
@app.callback(
    [Output('total-revenue', 'children'),
     Output('revenue-change', 'children'),
     Output('total-users', 'children'),
     Output('users-change', 'children'),
     Output('total-orders', 'children'),
     Output('orders-change', 'children'),
     Output('revenue-trend', 'figure'),
     Output('metrics-comparison', 'figure')],
    [Input('date-range', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(days, n):
    data = get_data(days)

    # Calculate current period metrics
    current_revenue = data['revenue'].sum()
    current_users = data['users'].sum()
    current_orders = data['orders'].sum()

    # Calculate previous period for comparison
    prev_data = get_data(days * 2).iloc[:days]
    prev_revenue = prev_data['revenue'].sum()
    prev_users = prev_data['users'].sum()
    prev_orders = prev_data['orders'].sum()

    # Calculate changes
    revenue_change = (current_revenue - prev_revenue) / prev_revenue * 100
    users_change = (current_users - prev_users) / prev_users * 100
    orders_change = (current_orders - prev_orders) / prev_orders * 100

    # Revenue trend chart
    revenue_fig = go.Figure()
    revenue_fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['revenue'],
        mode='lines+markers',
        name='Daily Revenue'
    ))
    revenue_fig.update_layout(
        title='Revenue Trend',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified'
    )

    # Metrics comparison chart
    metrics_fig = go.Figure()
    metrics_fig.add_trace(go.Bar(
        name='Users',
        x=data['date'],
        y=data['users']
    ))
    metrics_fig.add_trace(go.Bar(
        name='Orders',
        x=data['date'],
        y=data['orders']
    ))
    metrics_fig.update_layout(
        title='Users & Orders Comparison',
        barmode='group',
        xaxis_title='Date',
        yaxis_title='Count'
    )

    return (
        f'${current_revenue:,.0f}',
        f'{revenue_change:+.1f}% vs previous period',
        f'{current_users:,.0f}',
        f'{users_change:+.1f}% vs previous period',
        f'{current_orders:,.0f}',
        f'{orders_change:+.1f}% vs previous period',
        revenue_fig,
        metrics_fig
    )

if __name__ == '__main__':
    app.run_server(debug=True)
```

## Dashboard Best Practices

### Design Guidelines

1. **Clarity Over Cleverness**
   - Simple > Complex
   - Familiar chart types
   - Clear labeling
   - Consistent color scheme

2. **Actionable Insights**
   - Highlight anomalies
   - Show context (comparisons, targets)
   - Provide drill-down paths
   - Include recommended actions

3. **Performance**
   - Pre-aggregate data
   - Use materialized views
   - Implement caching
   - Lazy-load detailed views

4. **Accessibility**
   - Color-blind friendly palettes
   - Proper contrast ratios
   - Keyboard navigation
   - Screen reader support

### Color Coding Standards

```python
DASHBOARD_COLORS = {
    'positive': '#22c55e',  # Green for positive changes
    'negative': '#ef4444',  # Red for negative changes
    'neutral': '#6b7280',   # Gray for neutral
    'warning': '#f59e0b',   # Amber for warnings
    'info': '#3b82f6',      # Blue for information

    # Brand colors
    'primary': '#6366f1',
    'secondary': '#8b5cf6',

    # Chart colors (color-blind friendly)
    'chart_palette': [
        '#6366f1', '#8b5cf6', '#ec4899',
        '#f59e0b', '#10b981', '#06b6d4'
    ]
}
```

### Metric Selection Framework

```python
def select_dashboard_metrics(audience, goal):
    """
    Select appropriate metrics for dashboard

    Args:
        audience: 'executive', 'manager', 'analyst', 'customer_success', etc.
        goal: 'growth', 'retention', 'efficiency', 'revenue', etc.
    """
    metrics = {
        'executive': {
            'growth': ['MRR Growth', 'Customer Growth', 'ARR', 'LTV:CAC'],
            'retention': ['NRR', 'Churn Rate', 'Customer Satisfaction'],
            'revenue': ['Total Revenue', 'Revenue per Customer', 'Gross Margin']
        },
        'manager': {
            'growth': ['New Customers', 'Activation Rate', 'CAC by Channel'],
            'retention': ['Retention Rate', 'Engagement Score', 'Feature Adoption'],
            'efficiency': ['Conversion Rate', 'Time to Value', 'Support Tickets']
        },
        'analyst': {
            'growth': ['Funnel Metrics', 'Cohort Performance', 'Attribution'],
            'retention': ['Cohort Retention', 'Churn Drivers', 'Usage Patterns'],
            'revenue': ['Revenue by Segment', 'LTV Distribution', 'Price Sensitivity']
        }
    }

    return metrics.get(audience, {}).get(goal, [])
```

## Dashboard Maintenance

### Update Frequency

| Dashboard Type | Update Frequency | Data Latency |
|----------------|------------------|--------------|
| Executive | Daily | 1-24 hours |
| Marketing | Hourly/Real-time | Minutes |
| Sales | Real-time | Seconds |
| Product | Real-time | Seconds |
| Finance | Weekly/Monthly | 1-7 days |
| Customer Success | Daily | 1-24 hours |

### Quality Checklist

- [ ] Data accuracy validated
- [ ] Calculations verified
- [ ] No broken visualizations
- [ ] Filters working correctly
- [ ] Performance acceptable (<3s load)
- [ ] Mobile responsive
- [ ] Tooltips informative
- [ ] Export functionality working
- [ ] Access permissions correct
- [ ] Documentation updated

## Common Dashboard Mistakes

1. **Too Many Metrics**: Overwhelming, unclear focus
2. **No Context**: Numbers without comparison or targets
3. **Poor Visual Choice**: Wrong chart for data type
4. **Inconsistent Definitions**: Metrics calculated differently
5. **Stale Data**: Outdated information
6. **No Drill-Down**: Can't investigate anomalies
7. **Vanity Metrics**: Impressive but not actionable
8. **Missing Annotations**: No explanation for spikes/drops
9. **Bad Color Choices**: Hard to read, not accessible
10. **No Mobile Support**: Unusable on phones/tablets

## Key Takeaways

- **Purpose First**: Define goals before designing
- **Know Your Audience**: Tailor complexity and metrics
- **Less is More**: Focus on critical metrics
- **Make it Actionable**: Insights should drive decisions
- **Test and Iterate**: Gather feedback and improve
- **Maintain Quality**: Regular validation and updates
- **Performance Matters**: Fast dashboards get used
- **Tell a Story**: Guide users to insights
