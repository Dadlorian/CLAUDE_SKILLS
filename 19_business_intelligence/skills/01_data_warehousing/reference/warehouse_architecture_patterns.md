# Data Warehouse Architecture Patterns

Reference guide for modern and traditional data warehouse architectures, including medallion, lambda, kappa, and data mesh patterns.

## Traditional Architectures

### Kimball Bus Architecture

**Concept**: Dimensional modeling with conformed dimensions across business processes

```
Data Sources → ETL → Dimensional Data Warehouse → BI Tools
                     ├── Sales Mart (Star Schema)
                     ├── Inventory Mart (Star Schema)
                     └── Finance Mart (Star Schema)
                          └── Conformed Dimensions
                              (Customer, Product, Date, Location)
```

**Characteristics**:
- Bottom-up approach
- Start with one business process
- Conformed dimensions shared across marts
- Star schema design
- Optimized for query performance

**When to Use**:
- BI and reporting focused
- Business user self-service
- Need fast query performance
- Iterative development preferred

### Inmon Enterprise Data Warehouse (EDW)

**Concept**: Normalized enterprise data warehouse feeding dimensional data marts

```
Data Sources → ETL → Normalized EDW (3NF) → ETL → Data Marts → BI Tools
                     └── Subject Areas            ├── Sales Mart
                         (Customer, Product,      ├── Inventory Mart
                          Transaction, Location)  └── Finance Mart
```

**Characteristics**:
- Top-down approach
- Normalized (3NF) central repository
- Data marts built from EDW
- Single version of truth
- Strict data governance

**When to Use**:
- Enterprise-wide consistency critical
- Complex data relationships
- Multiple departments with different needs
- Long-term strategic initiative

## Modern Cloud Architectures

### Medallion Architecture (Lakehouse)

**Concept**: Bronze → Silver → Gold layering for progressive data refinement

```
Data Sources → Bronze Layer → Silver Layer → Gold Layer → Consumption
              (Raw/Landing)  (Cleaned)      (Business)   (BI, ML, Apps)
```

**Layers:**

**Bronze (Raw)**:
- Exact copy of source data
- Schema on read
- Parquet/Delta format
- Append-only
- Purpose: Data lake landing zone

**Silver (Cleaned)**:
- Deduplicated
- Validated
- Conformed data types
- Quality checks applied
- Purpose: Clean, queryable data

**Gold (Business)**:
- Aggregated
- Business-ready
- Star schema or denormalized
- Optimized for consumption
- Purpose: Analytics and reporting

**Implementation:**
```sql
-- Bronze: Raw ingestion
CREATE TABLE bronze.customers AS
SELECT * FROM external_source;

-- Silver: Cleaned
CREATE TABLE silver.customers AS
SELECT
    customer_id,
    LOWER(TRIM(email)) as email,
    UPPER(country_code) as country_code,
    CAST(signup_date AS DATE) as signup_date
FROM bronze.customers
WHERE customer_id IS NOT NULL;

-- Gold: Business ready
CREATE TABLE gold.customer_summary AS
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as lifetime_orders,
    SUM(o.amount) as lifetime_value,
    MAX(o.order_date) as last_order_date
FROM silver.customers c
LEFT JOIN silver.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;
```

**Benefits**:
- Clear separation of concerns
- Incremental refinement
- Easy to debug (trace through layers)
- Supports both ML and BI workloads

**When to Use**:
- Cloud data lakehouse (Databricks, Delta Lake)
- Combined analytics and data science
- Large-scale data processing
- Need for both structured and semi-structured data

### Lambda Architecture

**Concept**: Separate batch and real-time processing paths

```
Data Sources
├── Batch Layer → Batch Processing → Batch Views → Serving Layer → Queries
└── Speed Layer → Stream Processing → Real-time Views ─────↗
```

**Components**:

**Batch Layer**:
- Processes complete dataset
- High latency (hours)
- High accuracy
- Immutable append-only
- Example: Spark batch jobs

**Speed Layer**:
- Processes real-time data
- Low latency (seconds)
- Eventual consistency
- Mutable (updates batch results)
- Example: Kafka Streams, Flink

**Serving Layer**:
- Merges batch and speed views
- Serves queries
- Example: Druid, Snowflake

**When to Use**:
- Need both real-time and batch analytics
- Can accept eventual consistency
- Have team expertise for two systems
- Large-scale event streaming

**Challenges**:
- Maintain two codebases
- Complex to operate
- Eventual consistency issues

### Kappa Architecture

**Concept**: Stream processing only, no separate batch layer

```
Data Sources → Stream Processing → Serving Layer → Queries
              (Kafka, Flink)     (Real-time Views)
```

**Characteristics**:
- Single technology stack
- All data as streams
- Reprocess by replaying stream
- Simpler than Lambda
- Lower latency

**When to Use**:
- Real-time requirements
- Team has stream processing expertise
- Can model all data as events
- Want to avoid complexity of Lambda

**Implementation Example:**
```sql
-- Kafka topic as source
-- Flink/Kafka Streams for processing
-- Materialize views in serving layer

-- Flink SQL example
CREATE TABLE orders_stream (
    order_id STRING,
    customer_id STRING,
    amount DECIMAL,
    order_time TIMESTAMP(3),
    WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'orders',
    'properties.bootstrap.servers' = 'localhost:9092'
);

CREATE TABLE customer_aggregates WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://localhost:5432/db'
) AS
SELECT
    customer_id,
    COUNT(*) as order_count,
    SUM(amount) as total_amount,
    TUMBLE_END(order_time, INTERVAL '1' HOUR) as window_end
FROM orders_stream
GROUP BY customer_id, TUMBLE(order_time, INTERVAL '1' HOUR);
```

### Data Mesh Architecture

**Concept**: Decentralized, domain-oriented data ownership

```
Domain A (Sales) → Sales Data Products → Data Catalog
Domain B (Marketing) → Marketing Data Products → Data Catalog
Domain C (Finance) → Finance Data Products → Data Catalog
                           ↓
                   Federated Governance
                   Shared Infrastructure
```

**Four Principles**:

1. **Domain-Oriented Ownership**:
   - Domains own their data products
   - Treat data as a product
   - Domain teams responsible for quality

2. **Data as a Product**:
   - Discoverable (in catalog)
   - Addressable (clear APIs)
   - Trustworthy (quality SLAs)
   - Self-describing (metadata)
   - Interoperable (standards)

3. **Self-Serve Data Platform**:
   - Infrastructure as a platform
   - Low-code/no-code for domains
   - Automated pipelines
   - Common tooling

4. **Federated Computational Governance**:
   - Standards and policies
   - Automated policy enforcement
   - Decentralized execution

**When to Use**:
- Large organization (1000+ employees)
- Multiple domains/business units
- Monolithic data platform is bottleneck
- Want to scale data teams

**Implementation Considerations**:
```
Data Product Requirements:
- Clear ownership
- SLA commitments (freshness, quality)
- Documentation
- Access controls
- Versioning
- Monitoring/alerting

Technology Enablers:
- Data catalog (Collibra, Alation, DataHub)
- dbt for transformations
- Great Expectations for quality
- Infrastructure as code (Terraform)
- API layer for data access
```

## Hybrid Architectures

### Hub-and-Spoke

**Concept**: Central hub with domain-specific spokes

```
Central Data Hub (Snowflake/BigQuery)
├── Sales Spoke (Sales-specific transformations)
├── Marketing Spoke (Marketing-specific transformations)
└── Finance Spoke (Finance-specific transformations)
```

**Characteristics**:
- Central storage layer
- Domain-specific processing
- Shared infrastructure
- Conformed dimensions in hub
- Department-specific in spokes

### Multi-Hop Architecture

**Concept**: Multiple stages of refinement

```
Raw → Standardized → Enriched → Application
```

**Example (dbt structure)**:
```
models/
├── l10_raw/          # Source extracts
├── l20_standardized/ # Clean, conformed
├── l30_enriched/     # Joined, calculated
├── l40_aggregated/   # Summary tables
└── l50_application/  # App-specific views
```

## Specific Use Case Patterns

### Real-Time Analytics Pattern

```
Streaming Sources (Kafka)
└── Stream Processing (Flink)
    ├── Real-time OLAP (Druid, ClickHouse)
    └── Data Warehouse (Snowflake, BigQuery)
        └── BI Dashboards
```

**Components**:
- Event streaming (Kafka, Kinesis)
- Stream processing (Flink, Kafka Streams)
- Real-time OLAP (Druid, ClickHouse, Pinot)
- Batch warehouse for long-term storage

### Operational Analytics Pattern

```
Operational Systems → CDC → Warehouse → Reverse ETL → Operational Systems
(Salesforce, etc.)  (Debezium)         (Snowflake)   (Hightouch)
```

**Use Cases**:
- Customer 360 in CRM
- Lead scoring in marketing automation
- Inventory optimization in ERP

### ML Feature Store Pattern

```
Data Warehouse → Feature Engineering → Feature Store → ML Models
                                       (Feast, Tecton)
                                            ↓
                                    Online Serving
                                    Offline Training
```

## Architecture Selection Guide

### Choose Kimball If:
- BI/reporting primary use case
- Business users query directly
- Fast query performance critical
- Iterative development preferred

### Choose Inmon If:
- Enterprise-wide consistency required
- Complex data governance needs
- Multiple downstream systems
- Long-term strategic initiative

### Choose Medallion If:
- Cloud lakehouse platform (Databricks)
- Need both ML and analytics
- Large-scale data processing
- Want to avoid vendor lock-in

### Choose Lambda If:
- Need real-time AND batch
- Have expertise in both paradigms
- Can manage complexity
- Strict latency requirements

### Choose Kappa If:
- Real-time primary requirement
- Stream processing expertise
- Want simpler architecture than Lambda
- All data can be modeled as events

### Choose Data Mesh If:
- Large organization (1000+ employees)
- Multiple independent domains
- Monolithic platform is bottleneck
- Want to scale data teams

## Layering Strategies

### Three-Layer Architecture
```
Source → Staging → Presentation
```

**Staging**: Raw data, minimal transformation
**Presentation**: Business-ready, optimized for queries

### Four-Layer Architecture
```
Source → Raw → Curated → Presentation
```

**Raw**: Exact copy of source
**Curated**: Cleaned, validated
**Presentation**: Business models

### Five-Layer Architecture
```
Source → Raw → Cleansed → Conformed → Presentation
```

**Cleansed**: Data quality applied
**Conformed**: Standardized across sources

## Best Practices

### Separation of Concerns
- Keep ETL logic separate from business logic
- One layer per transformation type
- Clear boundaries between layers

### Idempotency
- Re-running same process produces same result
- Important for recovery and testing
- Use MERGE instead of INSERT for updates

### Incremental Processing
- Only process new/changed data
- Use watermarks/timestamps
- Improves performance and reduces costs

### Data Quality Gates
- Validate at each layer boundary
- Fail fast on quality issues
- Monitor data quality metrics

### Monitoring and Observability
- Track pipeline health
- Monitor data freshness
- Alert on anomalies
- Maintain data lineage

### Documentation
- Document architecture decisions
- Maintain data dictionaries
- Create data lineage diagrams
- Keep runbooks up-to-date

## Common Mistakes to Avoid

❌ **Over-engineering**: Keep it simple, add complexity only when needed
❌ **No clear layers**: Mixing raw and transformed data
❌ **Direct source queries**: Always stage data first
❌ **No version control**: All DDL, transformations in git
❌ **Monolithic transformations**: Break into logical, testable steps
❌ **Ignoring data quality**: Quality checks at every layer
❌ **No recovery strategy**: Plan for failures and re-runs
❌ **Poor naming conventions**: Use consistent, descriptive names

## Evolution Strategy

### Start Simple
```
Day 1: Single layer (raw → presentation)
Month 1: Add staging layer
Month 3: Add quality layer
Year 1: Implement medallion/layered architecture
```

### Grow with Needs
- Start with Kimball for BI
- Add real-time layer when needed
- Evolve to data mesh as organization scales
- Don't over-architect upfront

### Migration Path
```
1. Assess current state
2. Define target architecture
3. Implement in phases
4. Migrate domain by domain
5. Decommission legacy systems
```
