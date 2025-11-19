# Cost Optimization Reference

## Overview

Self-service analytics can become expensive without proper cost management. This reference provides strategies to optimize costs while maintaining performance and accessibility.

## Cost Components

### 1. Platform Costs

```yaml
Data Warehouse:
  Snowflake:
    - Compute credits (per-second billing)
    - Storage costs
    - Data transfer
    - Cloud services layer

  BigQuery:
    - On-demand: $5-$6 per TB scanned
    - Flat-rate: Monthly slot commitment
    - Storage: $0.02 per GB active, $0.01 per GB long-term
    - Streaming inserts

  Redshift:
    - Node hours (reserved vs. on-demand)
    - Storage (included in node pricing)
    - Spectrum (S3 query): Per TB scanned
    - Concurrency scaling

BI Tools:
  Looker: ~$3,000/month + ~$50/user
  Tableau: ~$70/user/month (Creator)
  Mode: ~$50-$200/user/month
  Power BI: ~$10-$20/user/month

Data Catalog:
  Alation: ~$100,000+/year
  Atlan: ~$50,000+/year
  Open source (Amundsen): Hosting costs only
```

### 2. Personnel Costs

```yaml
Data Team:
  - Data engineers: $120-180k/year
  - Analytics engineers: $100-150k/year
  - Data analysts: $80-120k/year
  - Data platform lead: $150-220k/year

Support & Training:
  - Training development: ~$50k one-time
  - Ongoing support: 2-3 FTEs
  - Office hours coverage
  - Documentation maintenance

External Costs:
  - Consultants: $150-300/hour
  - Implementation partners
  - Training providers
  - Audit/compliance
```

### 3. Hidden Costs

```yaml
User Time:
  - Learning curve (hours per user)
  - Failed/slow queries (wasted time)
  - Support tickets (user + support time)
  - Troubleshooting

Technical Debt:
  - Poorly optimized queries
  - Duplicate workloads
  - Unused resources
  - Legacy tools

Opportunity Cost:
  - Wrong tool selection
  - Delayed value realization
  - Limited functionality
  - Vendor lock-in
```

## Cost Optimization Strategies

### 1. Compute Optimization

#### Snowflake

```yaml
Warehouse Sizing:
  - Start small (X-Small/Small)
  - Scale up for specific workloads
  - Use multi-cluster for concurrency
  - Separate workloads by warehouse

  # Example warehouse strategy
  Warehouses:
    ETL_WH:
      Size: Large
      Auto-suspend: 5 minutes
      Auto-resume: Yes
      Use: Data pipelines

    ANALYTICS_WH:
      Size: Medium
      Auto-suspend: 2 minutes
      Auto-resume: Yes
      Multi-cluster: Yes (2-5)
      Use: BI tools, analysts

    ADHOC_WH:
      Size: Small
      Auto-suspend: 1 minute
      Auto-resume: Yes
      Use: Exploration, testing

Cost Savings:
  - Auto-suspend aggressively (1-5 min)
  - Right-size warehouses
  - Use resource monitors
  - Set statement timeouts
  - Optimize query patterns

  # Resource monitor example
  CREATE RESOURCE MONITOR monthly_quota
    WITH CREDIT_QUOTA = 1000
    TRIGGERS
      ON 75 PERCENT DO NOTIFY
      ON 100 PERCENT DO SUSPEND
      ON 110 PERCENT DO SUSPEND_IMMEDIATE;
```

#### BigQuery

```yaml
Cost Control:
  Query Optimization:
    - Partition pruning (scan less data)
    - Clustering (better filtering)
    - Avoid SELECT *
    - Use materialized views
    - Implement quotas

  # Partitioning example
  CREATE TABLE orders
  PARTITION BY DATE(order_date)
  CLUSTER BY customer_id, product_id
  AS SELECT * FROM source_orders;

  Pricing Models:
    On-Demand:
      - Pay per TB scanned
      - Good for: Variable workloads
      - Risk: Unpredictable costs

    Flat-Rate:
      - Monthly slot commitment
      - Good for: Predictable workloads
      - Benefit: Cost predictability
      - Break-even: ~$8,000/month in scanning

  Cost Controls:
    - Set project-level quotas
    - Custom cost controls per user
    - Query cost estimation
    - Dashboard for monitoring

  # Cost control example
  - Max bytes billed: 10 TB per query
  - Daily quota: 100 TB
  - User quotas by role
```

### 2. Storage Optimization

```yaml
Data Lifecycle Management:
  Active Data (frequent access):
    - Keep in standard storage
    - Optimized for performance
    - Higher cost acceptable

  Warm Data (occasional access):
    - Move to lower-cost tier after 90 days
    - Acceptable slightly slower access
    - 50% cost reduction

  Cold Data (rare access):
    - Archive after 1 year
    - 75% cost reduction
    - OK with slower retrieval

  Example Snowflake:
    # Data retention policy
    CREATE TABLE historical_orders
      DATA_RETENTION_TIME_IN_DAYS = 90;

    # Move to long-term storage
    ALTER TABLE old_data SET STAGE_COPY_OPTIONS = (
      STAGE_FILE_FORMAT = PARQUET
    );

Compression:
  - Automatic in modern warehouses
  - Snowflake: 3-5x compression
  - BigQuery: Columnar storage
  - Parquet/ORC for data lakes

Deduplication:
  - Remove duplicate data
  - Consolidate similar datasets
  - Drop unused tables
  - Archive instead of keeping live

  # Find duplicate tables
  SELECT
    table_name,
    row_count,
    bytes
  FROM information_schema.tables
  WHERE table_name LIKE '%_copy%'
     OR table_name LIKE '%_backup%'
  ORDER BY bytes DESC;
```

### 3. Query Optimization for Cost

```sql
-- Bad: Scans entire table
SELECT *
FROM large_table
WHERE processed_date >= '2025-01-01';
-- Cost: High (full scan)

-- Good: Uses partition pruning
SELECT
  user_id,
  event_type,
  event_timestamp
FROM events
WHERE date = '2025-01-01'  -- Partition column
  AND event_type = 'purchase';
-- Cost: Low (single partition)

-- Bad: Aggregation on raw data
SELECT
  DATE(order_timestamp) as date,
  SUM(amount) as revenue
FROM orders
GROUP BY date;
-- Cost: High (aggregates billions of rows)

-- Good: Query pre-aggregated table
SELECT
  date,
  revenue
FROM daily_revenue_summary
WHERE date >= '2025-01-01';
-- Cost: Low (queries summary table)

-- Use approximation for large datasets
SELECT APPROX_COUNT_DISTINCT(user_id)
FROM large_events_table;
-- Much faster and cheaper than exact count
```

### 4. Caching & Pre-Computation

```yaml
Result Caching:
  Benefits:
    - Zero compute cost for cached queries
    - Instant results
    - Reduced load

  Strategies:
    - BI tool caching (1-24 hours)
    - Database result cache (Snowflake: 24h)
    - Application-level cache (Redis)

  Example Looker:
    persist_for: "1 hour"
    # Serves cached results, no query cost

Pre-Aggregations:
  When to Use:
    - Dashboard KPIs
    - Common aggregations
    - Slowly changing data
    - Repeated queries

  Implementation:
    # dbt incremental model
    {{ config(materialized='incremental') }}

    SELECT
      date,
      product_id,
      SUM(quantity) as units_sold,
      SUM(revenue) as total_revenue
    FROM {{ ref('orders') }}
    {% if is_incremental() %}
      WHERE date > (SELECT MAX(date) FROM {{ this }})
    {% endif %}
    GROUP BY 1, 2

  ROI:
    - Query cost: $50/day on raw data
    - Pre-agg cost: $5/day to maintain
    - Savings: $45/day = $16,425/year
```

### 5. User Behavior Optimization

```yaml
Education:
  - Train users on cost-effective queries
  - Discourage SELECT *
  - Promote filter usage
  - Encourage incremental development

  Query Cost Dashboard:
    - Top queries by cost
    - Cost by user
    - Trends over time
    - Optimization opportunities

Governance:
  - Query time limits
  - Result size limits
  - Concurrent query limits
  - Fair usage policies

  # Snowflake timeout example
  ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 300;

  # BigQuery quota
  - Maximum bytes billed per query
  - Daily quota per user
  - Project-level quotas

Automation:
  - Kill runaway queries
  - Alert on expensive queries
  - Suggest optimizations
  - Auto-limit result sets

  # Monitor expensive queries
  SELECT
    query_id,
    user_name,
    total_elapsed_time,
    bytes_scanned,
    credits_used
  FROM query_history
  WHERE credits_used > 10  -- Alert threshold
  ORDER BY credits_used DESC;
```

## Cost Monitoring

### Cost Dashboard

```yaml
Metrics to Track:

Overall Costs:
  - Total monthly cost
  - Cost by service (compute, storage, BI)
  - Trend vs. budget
  - Cost per user
  - Cost per query

Compute Costs:
  - Credits/slots used
  - Cost by warehouse/project
  - Cost by user
  - Cost by query type
  - Idle time

Storage Costs:
  - Storage used
  - Growth rate
  - Cost by schema
  - Archivable data

Efficiency Metrics:
  - Cost per insight
  - Cache hit rate
  - Query optimization opportunities
  - Unused resources

Example Query (Snowflake):
  SELECT
    DATE_TRUNC('day', start_time) as date,
    warehouse_name,
    user_name,
    SUM(credits_used_cloud_services) as credits,
    COUNT(*) as query_count,
    AVG(execution_time) / 1000 as avg_seconds
  FROM query_history
  WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  GROUP BY 1, 2, 3
  ORDER BY credits DESC;
```

### Alerts & Thresholds

```yaml
Alert Types:

Budget Alerts:
  - 75% of monthly budget
  - 90% of monthly budget
  - 100% of monthly budget
  - Unexpected spike (>50% daily average)

Query Alerts:
  - Query cost > $10
  - Query time > 5 minutes
  - User hitting limits
  - Repeated failed queries

Resource Alerts:
  - Warehouse running continuously
  - High concurrency (queueing)
  - Low cache hit rate
  - Storage growth >20%/month

Example Snowflake Resource Monitor:
  CREATE RESOURCE MONITOR analytics_budget
    WITH CREDIT_QUOTA = 5000  -- Monthly quota
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS
      ON 80 PERCENT DO NOTIFY
      ON 100 PERCENT DO SUSPEND
      ON 110 PERCENT DO SUSPEND_IMMEDIATE;
```

## Cost Optimization Checklist

```yaml
Monthly Reviews:
  □ Review total spend vs. budget
  □ Identify top cost drivers
  □ Check for unused resources
  □ Review warehouse/cluster sizing
  □ Analyze query patterns
  □ Check cache hit rates
  □ Review user activity
  □ Identify optimization opportunities

Quarterly Optimization:
  □ Archive old data
  □ Drop unused tables
  □ Consolidate warehouses
  □ Review BI tool licenses
  □ Renegotiate contracts
  □ Benchmark against alternatives
  □ Update resource monitors
  □ Train users on cost-effective practices

Annual Planning:
  □ Review total cost of ownership
  □ Evaluate pricing models
  □ Consider reserved capacity
  □ Assess tool consolidation
  □ Plan infrastructure upgrades
  □ Budget for next year
  □ Set cost optimization goals
```

## ROI Calculation

```yaml
Self-Service Analytics ROI:

Costs (Annual):
  - Platform costs: $200,000
  - Personnel: $400,000
  - Training: $50,000
  - Total: $650,000

Benefits (Annual):
  - Analyst time saved: $300,000
    (200 hours/month × $75/hour × 12 months)

  - Faster decisions: $500,000
    (10% faster time to market, 5% revenue impact)

  - Reduced tools: $150,000
    (Consolidation savings)

  - Total: $950,000

ROI = (Benefits - Costs) / Costs
ROI = ($950k - $650k) / $650k = 46%

Payback Period: ~9 months
```

## Best Practices Summary

```yaml
Compute:
  ✓ Auto-suspend warehouses aggressively
  ✓ Right-size for workload
  ✓ Separate workloads
  ✓ Use resource monitors
  ✓ Optimize queries

Storage:
  ✓ Archive old data
  ✓ Drop unused tables
  ✓ Compress where possible
  ✓ Deduplicate datasets
  ✓ Lifecycle management

Queries:
  ✓ Use partition pruning
  ✓ Avoid SELECT *
  ✓ Limit result sets
  ✓ Cache frequently used results
  ✓ Pre-aggregate where possible

Users:
  ✓ Train on cost-effective practices
  ✓ Set quotas and limits
  ✓ Monitor usage
  ✓ Provide cost visibility
  ✓ Encourage optimization

Monitoring:
  ✓ Track costs daily
  ✓ Alert on anomalies
  ✓ Review monthly
  ✓ Optimize quarterly
  ✓ Report on ROI
```

## References

- Snowflake Cost Optimization Guide
- BigQuery Pricing Best Practices
- "FinOps: Cloud Financial Management" - Cloud FinOps Foundation
- dbt Cost Optimization Tips
- Looker Performance & Cost Optimization
