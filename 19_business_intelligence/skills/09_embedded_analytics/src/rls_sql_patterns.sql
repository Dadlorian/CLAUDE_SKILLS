-- Production Row-Level Security SQL Patterns

-- =======================
-- Pattern 1: PostgreSQL RLS with tenant_id
-- =======================

-- Enable RLS on table
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY tenant_isolation_sales ON sales
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant')::int);

CREATE POLICY tenant_isolation_customers ON customers
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant')::int);

-- Policy with multiple conditions
CREATE POLICY tenant_and_date_filter ON sales
    FOR SELECT
    TO app_user
    USING (
        tenant_id = current_setting('app.current_tenant')::int
        AND date >= CURRENT_DATE - INTERVAL '2 years'
    );

-- =======================
-- Pattern 2: Role-based RLS
-- =======================

-- Admin role sees everything
CREATE POLICY admin_all_access ON sales
    FOR ALL
    TO admin_role
    USING (true);

-- Manager sees department data
CREATE POLICY manager_department_access ON sales
    FOR ALL
    TO manager_role
    USING (
        department_id = current_setting('app.current_department')::int
    );

-- Analyst sees limited columns
CREATE POLICY analyst_limited_access ON sales
    FOR SELECT
    TO analyst_role
    USING (tenant_id = current_setting('app.current_tenant')::int);

-- =======================
-- Pattern 3: Hierarchical RLS
-- =======================

-- Users see their team's data (manager + subordinates)
CREATE POLICY hierarchical_access ON sales
    FOR ALL
    TO app_user
    USING (
        created_by_user_id IN (
            WITH RECURSIVE team AS (
                SELECT user_id FROM users
                WHERE user_id = current_setting('app.current_user_id')::int

                UNION ALL

                SELECT u.user_id FROM users u
                INNER JOIN team t ON u.manager_id = t.user_id
            )
            SELECT user_id FROM team
        )
    );

-- =======================
-- Pattern 4: Time-based RLS (subscription tiers)
-- =======================

CREATE POLICY subscription_tier_access ON sales
    FOR ALL
    TO app_user
    USING (
        CASE
            -- Enterprise: all data
            WHEN (SELECT tier FROM tenants WHERE id = tenant_id) = 'enterprise'
                THEN true

            -- Professional: 1 year
            WHEN (SELECT tier FROM tenants WHERE id = tenant_id) = 'professional'
                THEN date >= CURRENT_DATE - INTERVAL '1 year'

            -- Basic: 90 days
            WHEN (SELECT tier FROM tenants WHERE id = tenant_id) = 'basic'
                THEN date >= CURRENT_DATE - INTERVAL '90 days'

            ELSE false
        END
    );

-- =======================
-- Pattern 5: Geographic RLS (GDPR compliance)
-- =======================

CREATE POLICY geo_isolation ON customer_data
    FOR ALL
    TO app_user
    USING (
        data_region = (SELECT region FROM users WHERE id = current_setting('app.current_user_id')::int)
        OR EXISTS (
            SELECT 1 FROM users
            WHERE id = current_setting('app.current_user_id')::int
            AND has_global_access = true
        )
    );

-- =======================
-- Pattern 6: Column-level security with RLS
-- =======================

-- Create view with conditional column masking
CREATE OR REPLACE VIEW sales_filtered AS
SELECT
    id,
    tenant_id,
    date,
    product_id,
    -- Mask sensitive data based on role
    CASE
        WHEN current_setting('app.user_role') IN ('admin', 'finance')
            THEN amount
        ELSE NULL
    END AS amount,

    CASE
        WHEN current_setting('app.user_role') = 'admin'
            THEN customer_name
        ELSE 'REDACTED'
    END AS customer_name

FROM sales
WHERE tenant_id = current_setting('app.current_tenant')::int;

-- Grant access only to filtered view
GRANT SELECT ON sales_filtered TO app_user;
REVOKE SELECT ON sales FROM app_user;

-- =======================
-- Pattern 7: Composite RLS (tenant + department + region)
-- =======================

CREATE POLICY composite_filter ON sales
    FOR ALL
    TO app_user
    USING (
        tenant_id = current_setting('app.current_tenant')::int
        AND (
            department_id = current_setting('app.current_department')::int
            OR current_setting('app.user_role') = 'admin'
        )
        AND (
            region = current_setting('app.current_region')
            OR current_setting('app.user_role') IN ('admin', 'regional_manager')
        )
    );

-- =======================
-- Indexes for RLS Performance
-- =======================

-- Compound indexes for common RLS filters
CREATE INDEX idx_sales_tenant_date ON sales(tenant_id, date DESC);
CREATE INDEX idx_sales_tenant_dept ON sales(tenant_id, department_id);
CREATE INDEX idx_sales_composite ON sales(tenant_id, department_id, region);

-- Covering index to avoid table lookups
CREATE INDEX idx_sales_covering ON sales(tenant_id, date)
    INCLUDE (amount, product_id, customer_id);

-- Partial index for active data only
CREATE INDEX idx_sales_active ON sales(tenant_id, date)
    WHERE archived = false;

-- =======================
-- Testing RLS
-- =======================

-- Test as specific tenant
SET app.current_tenant = '123';
SET app.current_user_id = '456';
SET app.user_role = 'analyst';

-- Should only return tenant 123 data
SELECT * FROM sales;

-- Verify row count matches expectation
SELECT COUNT(*) FROM sales;
SELECT COUNT(*) FROM sales WHERE tenant_id = 123;
-- These should match!

-- Reset
RESET app.current_tenant;
RESET app.current_user_id;
RESET app.user_role;

-- =======================
-- Monitoring RLS Performance
-- =======================

-- Check if RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE tablename IN ('sales', 'customers');

-- List all policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
ORDER BY tablename, policyname;

-- Analyze query with RLS
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM sales
WHERE date >= '2024-01-01';

-- Check for sequential scans (bad performance)
-- Should see "Index Scan" not "Seq Scan"
