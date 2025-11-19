-- Self-Service Analytics Dashboard Data Model
-- Build efficient, aggregated tables for dashboard performance
-- Purpose: Enable fast, interactive dashboard experience for business users

-- ============================================================================
-- 1. Dashboard Metadata Base Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.dashboard_registry (
    dashboard_id STRING NOT NULL PRIMARY KEY,
    dashboard_name STRING NOT NULL,
    description STRING,
    owner_id STRING NOT NULL,
    owner_email STRING NOT NULL,
    owner_team STRING NOT NULL,
    created_date DATE NOT NULL,
    last_modified_date DATE NOT NULL,
    published_date TIMESTAMP,
    status STRING,  -- draft, published, archived
    category STRING,  -- finance, sales, operations, product, marketing
    sub_category STRING,
    refresh_interval_minutes INT DEFAULT 60,
    is_certified BOOLEAN DEFAULT FALSE,
    certification_date TIMESTAMP,
    view_count INT DEFAULT 0,
    unique_users INT DEFAULT 0,
    avg_load_time_seconds DECIMAL(10, 2),
    data_freshness_sla_minutes INT,
    requires_approval_for_access BOOLEAN DEFAULT FALSE,
    UNIQUE (dashboard_name, owner_id)
);


-- ============================================================================
-- 2. KPI Summary Table (Daily aggregation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_daily_kpi_summary (
    kpi_date DATE NOT NULL,
    kpi_id STRING NOT NULL,
    kpi_name STRING NOT NULL,
    kpi_category STRING NOT NULL,
    metric_value DECIMAL(20, 4),
    metric_currency STRING,
    metric_unit STRING,
    target_value DECIMAL(20, 4),
    variance_amount DECIMAL(20, 4),
    variance_percent DECIMAL(10, 2),
    variance_direction STRING,  -- up, down, neutral
    target_met BOOLEAN,
    threshold_warning BOOLEAN,
    threshold_critical BOOLEAN,
    comparison_prior_period DECIMAL(20, 4),
    comparison_prior_year DECIMAL(20, 4),
    trend_direction STRING,  -- increasing, decreasing, flat
    data_quality_score DECIMAL(5, 2),
    PRIMARY KEY (kpi_date, kpi_id)
) CLUSTER BY kpi_date DESC, kpi_category;


-- ============================================================================
-- 3. Financial Metrics Summary (Daily)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_financial_daily (
    financial_date DATE NOT NULL,
    revenue_total DECIMAL(20, 2),
    revenue_recurring DECIMAL(20, 2),
    revenue_new DECIMAL(20, 2),
    revenue_expansion DECIMAL(20, 2),
    gross_profit DECIMAL(20, 2),
    gross_margin_percent DECIMAL(5, 2),
    operating_expense DECIMAL(20, 2),
    operating_margin_percent DECIMAL(5, 2),
    net_profit DECIMAL(20, 2),
    cash_flow DECIMAL(20, 2),
    refund_amount DECIMAL(20, 2),
    refund_rate_percent DECIMAL(5, 2),
    average_order_value DECIMAL(15, 2),
    total_orders INT,
    PRIMARY KEY (financial_date)
) CLUSTER BY financial_date DESC;


-- ============================================================================
-- 4. Customer Metrics Summary (Daily)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_customer_daily (
    customer_date DATE NOT NULL,
    total_customers INT,
    active_customers INT,
    new_customers INT,
    churned_customers INT,
    returning_customers INT,
    customer_acquisition_cost DECIMAL(10, 2),
    customer_lifetime_value DECIMAL(15, 2),
    net_revenue_retention_percent DECIMAL(5, 2),
    customer_satisfaction_score DECIMAL(3, 2),
    nps_score DECIMAL(5, 2),
    repeat_purchase_rate_percent DECIMAL(5, 2),
    average_customer_age_days INT,
    customer_retention_rate_percent DECIMAL(5, 2),
    PRIMARY KEY (customer_date)
) CLUSTER BY customer_date DESC;


-- ============================================================================
-- 5. Sales Pipeline Summary (Daily)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_sales_pipeline_daily (
    pipeline_date DATE NOT NULL,
    sales_stage STRING,  -- lead, prospect, opportunity, negotiation, won, lost
    opportunity_count INT,
    potential_revenue DECIMAL(20, 2),
    conversion_rate_percent DECIMAL(5, 2),
    average_deal_size DECIMAL(15, 2),
    average_sales_cycle_days INT,
    win_rate_percent DECIMAL(5, 2),
    PRIMARY KEY (pipeline_date, sales_stage)
) CLUSTER BY pipeline_date DESC;


-- ============================================================================
-- 6. Product Performance Summary (Daily)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_product_daily (
    product_date DATE NOT NULL,
    product_id STRING NOT NULL,
    product_name STRING NOT NULL,
    category STRING NOT NULL,
    units_sold INT,
    revenue DECIMAL(20, 2),
    gross_profit DECIMAL(20, 2),
    gross_margin_percent DECIMAL(5, 2),
    customer_count INT,
    repeat_customer_count INT,
    return_rate_percent DECIMAL(5, 2),
    customer_satisfaction_rating DECIMAL(3, 2),
    PRIMARY KEY (product_date, product_id)
) CLUSTER BY product_date DESC, category;


-- ============================================================================
-- 7. Marketing Campaign Performance (Daily)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_marketing_daily (
    campaign_date DATE NOT NULL,
    campaign_id STRING NOT NULL,
    campaign_name STRING NOT NULL,
    channel STRING NOT NULL,  -- email, paid_search, social, display, affiliate
    spend DECIMAL(15, 2),
    impressions BIGINT,
    clicks BIGINT,
    click_through_rate_percent DECIMAL(5, 2),
    conversions INT,
    conversion_rate_percent DECIMAL(5, 2),
    revenue_attributed DECIMAL(20, 2),
    return_on_ad_spend DECIMAL(10, 2),
    cost_per_acquisition DECIMAL(10, 2),
    PRIMARY KEY (campaign_date, campaign_id)
) CLUSTER BY campaign_date DESC, channel;


-- ============================================================================
-- 8. Operational Metrics Summary (Daily)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.fct_operational_daily (
    operations_date DATE NOT NULL,
    customer_support_tickets INT,
    avg_resolution_time_hours DECIMAL(8, 2),
    customer_satisfaction_percent DECIMAL(5, 2),
    data_quality_issues INT,
    data_pipeline_failures INT,
    system_uptime_percent DECIMAL(5, 2),
    api_response_time_ms DECIMAL(10, 2),
    PRIMARY KEY (operations_date)
) CLUSTER BY operations_date DESC;


-- ============================================================================
-- 9. Dimension: Time (for easy joining)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.dim_date (
    date_id INT NOT NULL PRIMARY KEY,
    calendar_date DATE NOT NULL UNIQUE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    week_of_year INT,
    day_of_month INT,
    day_name VARCHAR(20),
    is_weekday BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INT,
    fiscal_quarter INT,
    fiscal_month INT,
    date_formatted VARCHAR(20)
);


-- ============================================================================
-- 10. Dimension: Organization (for hierarchy navigation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.dim_organization (
    org_id STRING NOT NULL PRIMARY KEY,
    org_name STRING NOT NULL,
    parent_org_id STRING,
    org_level INT,  -- 0: company, 1: division, 2: department, 3: team
    org_type STRING,  -- business_unit, department, team, function
    region STRING,
    country STRING,
    manager_id STRING,
    manager_name STRING,
    employee_count INT,
    created_date DATE,
    UNIQUE (org_name, org_level)
);


-- ============================================================================
-- 11. Dimension: User (for self-service access control)
-- ============================================================================

CREATE TABLE IF NOT EXISTS analytics.dashboards.dim_user (
    user_id STRING NOT NULL PRIMARY KEY,
    user_email STRING NOT NULL UNIQUE,
    user_name STRING NOT NULL,
    user_department STRING,
    user_team STRING,
    user_role STRING,  -- analyst, manager, executive, etc
    org_id STRING,
    manager_id STRING,
    is_active BOOLEAN DEFAULT TRUE,
    access_level STRING,  -- bronze, silver, gold
    created_date DATE,
    last_active_date DATE,
    FOREIGN KEY (org_id) REFERENCES analytics.dashboards.dim_organization(org_id)
);


-- ============================================================================
-- 12. Views: Revenue KPI Dashboard
-- ============================================================================

CREATE OR REPLACE VIEW analytics.dashboards.v_revenue_kpi_dashboard AS
SELECT
    kd.calendar_date,
    kd.month_name,
    kd.fiscal_quarter,
    fd.revenue_total,
    fd.revenue_recurring,
    fd.revenue_new,
    fd.revenue_expansion,
    fd.gross_profit,
    fd.gross_margin_percent,
    fd.operating_margin_percent,
    fd.refund_rate_percent,
    ROUND(fd.revenue_total / NULLIF(fd.total_orders, 0), 2) AS avg_order_value,
    LAG(fd.revenue_total) OVER (ORDER BY kd.calendar_date) AS revenue_prior_day,
    ROUND(((fd.revenue_total - LAG(fd.revenue_total) OVER (ORDER BY kd.calendar_date)) /
           NULLIF(LAG(fd.revenue_total) OVER (ORDER BY kd.calendar_date), 0) * 100), 2) AS revenue_growth_pct
FROM analytics.dashboards.fct_financial_daily fd
INNER JOIN analytics.dashboards.dim_date kd ON fd.financial_date = kd.calendar_date
ORDER BY kd.calendar_date DESC;


-- ============================================================================
-- 13. Views: Customer Health Dashboard
-- ============================================================================

CREATE OR REPLACE VIEW analytics.dashboards.v_customer_health_dashboard AS
SELECT
    kd.calendar_date,
    kd.month_name,
    cd.total_customers,
    cd.active_customers,
    cd.new_customers,
    cd.churned_customers,
    cd.customer_retention_rate_percent,
    cd.net_revenue_retention_percent,
    cd.customer_lifetime_value,
    cd.customer_acquisition_cost,
    ROUND(cd.customer_lifetime_value / NULLIF(cd.customer_acquisition_cost, 0), 2) AS ltv_cac_ratio,
    cd.customer_satisfaction_score,
    cd.nps_score,
    cd.repeat_purchase_rate_percent,
    LAG(cd.total_customers) OVER (ORDER BY kd.calendar_date) AS customers_prior_day,
    ROUND(((cd.total_customers - LAG(cd.total_customers) OVER (ORDER BY kd.calendar_date)) /
           NULLIF(LAG(cd.total_customers) OVER (ORDER BY kd.calendar_date), 0) * 100), 2) AS customer_growth_pct
FROM analytics.dashboards.fct_customer_daily cd
INNER JOIN analytics.dashboards.dim_date kd ON cd.customer_date = kd.calendar_date
ORDER BY kd.calendar_date DESC;


-- ============================================================================
-- 14. Views: Marketing Effectiveness Dashboard
-- ============================================================================

CREATE OR REPLACE VIEW analytics.dashboards.v_marketing_effectiveness AS
SELECT
    kd.calendar_date,
    kd.week_of_year,
    md.channel,
    SUM(md.spend) AS total_spend,
    SUM(md.impressions) AS total_impressions,
    SUM(md.clicks) AS total_clicks,
    AVG(md.click_through_rate_percent) AS avg_ctr_percent,
    SUM(md.conversions) AS total_conversions,
    AVG(md.conversion_rate_percent) AS avg_conversion_rate,
    SUM(md.revenue_attributed) AS attributed_revenue,
    AVG(md.return_on_ad_spend) AS avg_roas,
    ROUND(SUM(md.spend) / NULLIF(SUM(md.conversions), 0), 2) AS cost_per_conversion,
    ROUND(SUM(md.revenue_attributed) / NULLIF(SUM(md.spend), 0), 2) AS revenue_per_dollar_spent
FROM analytics.dashboards.fct_marketing_daily md
INNER JOIN analytics.dashboards.dim_date kd ON md.campaign_date = kd.calendar_date
GROUP BY
    kd.calendar_date,
    kd.week_of_year,
    md.channel
ORDER BY
    kd.calendar_date DESC,
    md.channel;


-- ============================================================================
-- 15. Views: Executive Summary (All KPIs)
-- ============================================================================

CREATE OR REPLACE VIEW analytics.dashboards.v_executive_summary AS
SELECT
    kd.calendar_date,
    kd.fiscal_quarter,
    'FINANCIAL' AS category,
    'Revenue' AS metric_name,
    fd.revenue_total AS metric_value
FROM analytics.dashboards.fct_financial_daily fd
INNER JOIN analytics.dashboards.dim_date kd ON fd.financial_date = kd.calendar_date

UNION ALL

SELECT
    kd.calendar_date,
    kd.fiscal_quarter,
    'CUSTOMER' AS category,
    'Active Customers' AS metric_name,
    cd.active_customers AS metric_value
FROM analytics.dashboards.fct_customer_daily cd
INNER JOIN analytics.dashboards.dim_date kd ON cd.customer_date = kd.calendar_date

UNION ALL

SELECT
    kd.calendar_date,
    kd.fiscal_quarter,
    'OPERATIONAL' AS category,
    'System Uptime %' AS metric_name,
    od.system_uptime_percent AS metric_value
FROM analytics.dashboards.fct_operational_daily od
INNER JOIN analytics.dashboards.dim_date kd ON od.operations_date = kd.calendar_date
ORDER BY calendar_date DESC;


-- ============================================================================
-- 16. Materialized View: Weekly Performance Summary
-- ============================================================================

CREATE OR REPLACE VIEW analytics.dashboards.v_weekly_performance AS
SELECT
    DATETRUNC(WEEK, kd.calendar_date) AS week_start,
    COUNT(DISTINCT kd.calendar_date) AS days_in_week,
    SUM(fd.revenue_total) AS weekly_revenue,
    AVG(fd.revenue_total) AS avg_daily_revenue,
    SUM(cd.new_customers) AS new_customers,
    SUM(cd.churned_customers) AS churned_customers,
    AVG(cd.customer_satisfaction_score) AS avg_satisfaction,
    SUM(md.spend) AS marketing_spend,
    SUM(md.revenue_attributed) AS marketing_attributed_revenue,
    AVG(md.return_on_ad_spend) AS avg_marketing_roas,
    SUM(od.customer_support_tickets) AS support_tickets,
    AVG(od.system_uptime_percent) AS avg_uptime_percent
FROM analytics.dashboards.dim_date kd
LEFT JOIN analytics.dashboards.fct_financial_daily fd ON kd.calendar_date = fd.financial_date
LEFT JOIN analytics.dashboards.fct_customer_daily cd ON kd.calendar_date = cd.customer_date
LEFT JOIN analytics.dashboards.fct_marketing_daily md ON kd.calendar_date = md.campaign_date
LEFT JOIN analytics.dashboards.fct_operational_daily od ON kd.calendar_date = od.operations_date
GROUP BY DATETRUNC(WEEK, kd.calendar_date)
ORDER BY week_start DESC;


-- ============================================================================
-- 17. Stored Procedure: Refresh Dashboard Tables
-- ============================================================================

CREATE OR REPLACE PROCEDURE analytics.dashboards.sp_refresh_dashboard_metrics()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Refresh daily financial metrics
    INSERT INTO analytics.dashboards.fct_financial_daily
    SELECT CURRENT_DATE,
           COALESCE(SUM(order_amount), 0) as revenue_total,
           COALESCE(SUM(CASE WHEN subscription_type = 'recurring' THEN order_amount END), 0),
           COALESCE(SUM(CASE WHEN is_new_customer THEN order_amount END), 0),
           COALESCE(SUM(CASE WHEN is_expansion THEN order_amount END), 0),
           COALESCE(SUM(gross_profit), 0),
           COALESCE(ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(order_amount), 0), 2), 0),
           COALESCE(ROUND(100.0 * SUM(net_profit) / NULLIF(SUM(order_amount), 0), 2), 0),
           COALESCE(ROUND(100.0 * COUNT(CASE WHEN order_status = 'refunded' THEN 1 END) / NULLIF(COUNT(*), 0), 2), 0),
           COALESCE(AVG(order_amount), 0),
           COUNT(*)
    FROM analytics.marts.fct_orders
    WHERE order_date = CURRENT_DATE
    ON CONFLICT (financial_date) DO UPDATE SET
        revenue_total = EXCLUDED.revenue_total;

    RETURN 'Dashboard metrics refreshed successfully';
END
$$;


-- ============================================================================
-- 18. Create Performance Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_financial_daily_date ON analytics.dashboards.fct_financial_daily (financial_date DESC);
CREATE INDEX IF NOT EXISTS idx_customer_daily_date ON analytics.dashboards.fct_customer_daily (customer_date DESC);
CREATE INDEX IF NOT EXISTS idx_product_daily_date_category ON analytics.dashboards.fct_product_daily (product_date DESC, category);
CREATE INDEX IF NOT EXISTS idx_marketing_daily_channel ON analytics.dashboards.fct_marketing_daily (campaign_date DESC, channel);
CREATE INDEX IF NOT EXISTS idx_user_email ON analytics.dashboards.dim_user (user_email);
CREATE INDEX IF NOT EXISTS idx_organization_type ON analytics.dashboards.dim_organization (org_type, org_level);

-- ============================================================================
-- 19. Grant Permissions to Self-Service Roles
-- ============================================================================

GRANT SELECT ON ALL TABLES IN SCHEMA analytics.dashboards TO ROLE analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics.dashboards TO ROLE executive;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics.dashboards TO ROLE viewer;
GRANT SELECT, INSERT, UPDATE ON TABLE analytics.dashboards.dashboard_registry TO ROLE senior_analyst;

-- ============================================================================
-- 20. Documentation Comment
-- ============================================================================

/*
  SELF-SERVICE DASHBOARD DATA MODEL

  This schema provides optimized tables and views for the self-service analytics
  platform. Tables are aggregated daily and designed for fast query performance.

  Key Features:
  - Pre-aggregated daily metrics for responsive dashboards
  - Dimension tables for self-service filtering and drill-down
  - Materialized views for common dashboard patterns
  - Row-level security ready (can integrate with RLS policies)

  Refresh Schedule:
  - Daily at 2:00 AM UTC via sp_refresh_dashboard_metrics()
  - Incremental updates for tables modified after last refresh

  Usage:
  - Use v_* views for dashboard queries
  - Join with dim_* tables for context
  - Use fct_* tables for custom analyses

  Owner: BI Platform Team
  SLA: 99.9% uptime, <5 second query response time
*/
