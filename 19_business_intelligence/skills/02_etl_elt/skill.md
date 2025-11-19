# ETL/ELT Engineering Mastery

## Purpose
Expert-level proficiency in Extract, Transform, Load (ETL) and Extract, Load, Transform (ELT) processes using modern data stack tools including dbt, Airflow, Airbyte, Fivetran, and Great Expectations. This skill enables building production-grade data pipelines with robust error handling, data quality checks, and operational excellence.

## Domain Overview
ETL/ELT engineering is the backbone of modern data platforms, responsible for moving, transforming, and validating data from source systems to analytical warehouses. The modern shift from ETL to ELT leverages cloud warehouse compute power, enabling SQL-based transformations and better separation of concerns.

## Core Competencies

### 1. Modern ELT Stack Mastery
- **dbt (data build tool)**: Transformation layer, testing, documentation, deployment
- **Ingestion Tools**: Airbyte (open-source), Fivetran (managed), Stitch, custom connectors
- **Orchestration**: Apache Airflow, Prefect, Dagster, dbt Cloud, Mage
- **Data Quality**: Great Expectations, dbt tests, Soda Core, custom validation
- **Change Data Capture (CDC)**: Debezium, AWS DMS, database log mining
- **Reverse ETL**: Census, Hightouch, warehouse to operational systems

### 2. dbt Development Excellence
- **Project Structure**: Sources, staging, intermediate, marts layers
- **Model Types**: Views, tables, incremental, ephemeral, snapshots
- **Testing Framework**: Schema tests, data tests, custom tests, unit tests
- **Macros & Packages**: Reusable SQL, dbt_utils, custom packages
- **Documentation**: Auto-generated docs, column descriptions, lineage
- **Deployment**: Environments, CI/CD, blue/green deployments, slim CI

### 3. Orchestration Patterns
- **Airflow DAG Design**: Task dependencies, XComs, sensors, branching
- **Operators**: BashOperator, PythonOperator, dbt operator, SQL operators
- **Error Handling**: Retries, alerting, SLAs, on_failure callbacks
- **Scheduling**: Cron expressions, data-driven triggers, event-based
- **Backfilling**: Historical data loads, idempotent pipelines
- **Monitoring**: Logs, metrics, alerting, performance tracking

### 4. Data Ingestion Strategies
- **Full Refresh**: Complete table replacement, simple but inefficient
- **Incremental Loading**: Append-only, merge/upsert, timestamp-based
- **Change Data Capture**: Real-time streaming, log-based replication
- **API Extraction**: Rate limiting, pagination, authentication, error recovery
- **File-Based**: CSV, JSON, Parquet, Delta Lake, schema evolution
- **Database Replication**: Logical replication, snapshots, triggers

### 5. Data Quality Engineering
- **Great Expectations**: Expectations, validation, profiling, data docs
- **dbt Tests**: Not null, unique, relationships, accepted values, custom SQL
- **Data Contracts**: Schema validation, breaking change detection
- **Anomaly Detection**: Statistical methods, ML-based, threshold monitoring
- **Reconciliation**: Source-to-target validation, row counts, checksums
- **Observability**: Data lineage, freshness monitoring, volume tracking

### 6. Incremental Processing
- **Strategies**: Append, merge, delete+insert, slowly changing dimensions
- **Performance**: Partitioning, clustering, micro-batching
- **State Management**: Checkpoints, watermarks, exactly-once semantics
- **Late Arriving Data**: Handling out-of-order records, lookback windows
- **Idempotency**: Deterministic transformations, safe re-runs
- **Recovery**: Failed batch handling, replay mechanisms

### 7. Error Handling & Recovery
- **Retry Logic**: Exponential backoff, circuit breakers, max attempts
- **Dead Letter Queues**: Failed record isolation, manual review
- **Alerting**: PagerDuty, Slack, email, severity levels
- **Logging**: Structured logging, correlation IDs, audit trails
- **Graceful Degradation**: Partial failures, downstream impact minimization
- **Rollback Procedures**: Transaction management, checkpoint restoration

### 8. Performance Optimization
- **Query Optimization**: Filter pushdown, partition pruning, join strategies
- **Parallelization**: Task-level, data-level, worker scaling
- **Materialization**: Incremental models, caching, pre-aggregation
- **Resource Management**: Warehouse sizing, concurrency limits, queueing
- **Cost Optimization**: Efficient queries, appropriate materializations, monitoring
- **Profiling**: Query plans, execution times, bottleneck identification

### 9. CI/CD for Data Pipelines
- **Version Control**: Git workflows, branching strategies, code review
- **Testing**: Unit tests, integration tests, data quality tests
- **Slim CI**: Modified models only, test selection, fast feedback
- **Deployment**: Blue/green, canary releases, rollback procedures
- **Environment Management**: Dev, staging, production, feature branches
- **Documentation**: Auto-generation, change tracking, impact analysis

### 10. Operational Excellence
- **Monitoring**: Pipeline health, SLA tracking, data freshness
- **Alerting**: Proactive notifications, on-call procedures, escalation
- **Documentation**: Runbooks, architecture diagrams, lineage
- **Cost Management**: Query cost tracking, warehouse optimization
- **Security**: Secrets management, access control, audit logging
- **Compliance**: GDPR, CCPA, data retention, PII handling

## Modern ELT Architecture Pattern

```
┌─────────────────┐
│  Source Systems │
│ (DBs, APIs,     │
│  Files, SaaS)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Extraction    │
│ Airbyte/Fivetran│
│  Stitch/Custom  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cloud Warehouse │
│ Snowflake/BQ/RS │
│  (Raw Layer)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transformation  │
│      dbt        │
│ (Staging→Marts) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analytics      │
│ Consumption     │
│ (BI/ML/Apps)    │
└─────────────────┘

Orchestrated by: Airflow/Prefect/dbt Cloud
Quality Checks: Great Expectations/dbt tests
```

## dbt Project Structure Best Practices

```
dbt_project/
├── models/
│   ├── staging/          # 1:1 with source tables
│   │   ├── _staging.yml  # Source definitions
│   │   ├── stg_customers.sql
│   │   └── stg_orders.sql
│   ├── intermediate/     # Reusable components
│   │   ├── int_customer_orders.sql
│   │   └── int_order_items_summary.sql
│   └── marts/           # Business-facing models
│       ├── core/        # Shared across teams
│       ├── marketing/   # Domain-specific
│       └── finance/
├── macros/              # Reusable SQL snippets
├── tests/               # Custom data tests
├── snapshots/           # SCD Type 2 tracking
├── analyses/            # Ad-hoc queries
├── seeds/               # Static lookup data
└── dbt_project.yml      # Configuration
```

## Key Patterns & Implementation Strategies

### 1. Medallion Architecture (Bronze → Silver → Gold)
- **Bronze**: Raw data, exactly as extracted, minimal transformations
- **Silver**: Cleaned, deduplicated, conformed, business keys
- **Gold**: Business-level aggregates, denormalized, analytics-ready

### 2. Incremental Model Pattern
```sql
-- dbt incremental model example
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'
) }}

SELECT *
FROM {{ source('ecommerce', 'orders') }}
{% if is_incremental() %}
WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

### 3. Data Quality Layering
1. **Source Quality**: Connector-level validations
2. **Ingestion Quality**: Row counts, schema checks, freshness
3. **Transformation Quality**: dbt tests, Great Expectations
4. **Business Logic Quality**: Custom SQL tests, acceptance criteria
5. **Consumption Quality**: BI-layer validations, user feedback

### 4. Error Handling Hierarchy
```python
# Airflow error handling pattern
def handle_failure(context):
    """On task failure callback"""
    ti = context['task_instance']
    log.error(f"Task {ti.task_id} failed")
    send_alert(severity='high', message=f"Pipeline failed: {ti}")
    # Store failed records in DLQ
    # Create incident ticket
    # Notify on-call engineer

default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'on_failure_callback': handle_failure,
    'sla': timedelta(hours=2),
}
```

### 5. Idempotent Pipeline Design
- Generate deterministic surrogate keys
- Use merge/upsert over append
- Implement exactly-once semantics
- Enable safe re-runs without duplicates
- Timestamp all transformations

## Industry Standards & Tools

### Data Integration Platforms
- **Airbyte**: Open-source, 300+ connectors, custom connector SDK
- **Fivetran**: Managed SaaS, auto-schema migration, change tracking
- **Stitch**: Singer-based, simple setup, limited transformations
- **Meltano**: Open-source, GitOps-based, Singer + dbt integration

### Orchestration Solutions
- **Apache Airflow**: Industry standard, Python-based, complex DAGs
- **Prefect**: Modern alternative, dynamic workflows, better UX
- **Dagster**: Software-defined assets, type system, testing focus
- **dbt Cloud**: Built-in scheduler, CI/CD, integrated with dbt

### Data Quality Tools
- **Great Expectations**: Comprehensive, documentation-driven, integrations
- **Soda Core**: SQL-based, YAML configs, data contracts
- **dbt tests**: Built-in, SQL-native, fast execution
- **Monte Carlo**: ML-based anomaly detection, observability platform

## Performance Metrics

### Pipeline SLAs
- **Data Freshness**: <30 min for critical, <6 hrs for batch
- **Pipeline Success Rate**: >99.5% for production pipelines
- **Recovery Time**: <1 hour for failed critical pipelines
- **Test Coverage**: >80% of models with data quality tests

### Operational KPIs
- **Cost per GB Processed**: Track and optimize warehouse costs
- **Pipeline Execution Time**: Monitor for degradation trends
- **Incremental Efficiency**: % of data processed incrementally vs full refresh
- **Error Rate**: Failed tasks / total tasks, track by severity

### Quality Metrics
- **Test Pass Rate**: >99% for production data quality tests
- **Data Completeness**: % of expected records present
- **Data Accuracy**: Reconciliation match rate >99.9%
- **Timeliness**: % of pipelines meeting SLA targets

## Real-World Patterns

### E-Commerce Order Processing Pipeline
```
Sources (Postgres, Shopify API) →
Extraction (Airbyte, hourly CDC) →
Raw Layer (Snowflake, orders_raw) →
Staging (dbt, deduplication, type casting) →
Intermediate (order_items_enriched) →
Marts (daily_sales_summary, customer_ltv)
```

### SaaS Product Analytics
```
Events (Segment, Amplitude) →
Streaming (Kafka → Snowflake) →
Real-time aggregation (dbt incremental) →
Metrics layer (dbt metrics) →
Dashboard refresh (5-minute lag)
```

### Financial Reporting
```
Multiple ERPs (SAP, Oracle, NetSuite) →
Batch extraction (Fivetran, daily) →
Data vault model (historical tracking) →
Regulatory calculations (dbt) →
Audit trail (dbt snapshots) →
Compliance reports (Power BI)
```

## Best Practices Checklist

### Development
- [ ] Use version control for all pipeline code
- [ ] Implement comprehensive testing (unit, integration, data quality)
- [ ] Document data models with descriptions and lineage
- [ ] Follow naming conventions consistently
- [ ] Separate staging, intermediate, and mart layers
- [ ] Use incremental models for large tables
- [ ] Implement proper error handling and retries

### Operations
- [ ] Set up monitoring and alerting for all pipelines
- [ ] Define and track SLAs for data freshness
- [ ] Implement cost monitoring and optimization
- [ ] Create runbooks for common failure scenarios
- [ ] Schedule regular pipeline reviews and optimizations
- [ ] Maintain on-call rotation for production issues
- [ ] Track and analyze pipeline performance metrics

### Quality
- [ ] Test at multiple layers (source, transformation, business logic)
- [ ] Implement schema validation and evolution handling
- [ ] Set up data reconciliation checks
- [ ] Monitor data freshness and volume anomalies
- [ ] Create data quality dashboards
- [ ] Document known data quality issues
- [ ] Establish data quality SLAs

### Security & Compliance
- [ ] Use secrets management (Vault, AWS Secrets Manager)
- [ ] Implement row-level security where needed
- [ ] Audit and log all data access
- [ ] Handle PII according to regulations
- [ ] Implement data retention policies
- [ ] Ensure encryption in transit and at rest
- [ ] Regular security reviews and updates

## Common Challenges & Solutions

### Challenge: Slow Incremental Models
**Solutions**:
- Partition tables by date
- Use clustering keys for filter columns
- Optimize merge conditions
- Implement micro-batching
- Review query execution plans

### Challenge: Schema Evolution
**Solutions**:
- Use schema-on-read patterns
- Implement flexible column selection
- Version your models
- Set `on_schema_change` appropriately
- Test schema changes in dev first

### Challenge: Data Quality Issues
**Solutions**:
- Implement multi-layer testing
- Set up anomaly detection
- Create data quality dashboards
- Establish data contracts with source teams
- Automate reconciliation checks

### Challenge: Pipeline Failures
**Solutions**:
- Implement robust retry logic
- Create dead letter queues
- Set up proper alerting
- Design for idempotency
- Document recovery procedures

### Challenge: Cost Overruns
**Solutions**:
- Use incremental models instead of full refresh
- Implement query result caching
- Optimize warehouse sizing
- Monitor expensive queries
- Archive historical data

## Learning Path

### Beginner (0-6 months)
1. SQL fundamentals and window functions
2. dbt Fundamentals course (free)
3. Basic Airflow DAG creation
4. Understanding ELT vs ETL paradigms
5. Introduction to data quality testing

### Intermediate (6-18 months)
1. Advanced dbt: incremental models, snapshots, packages
2. Airflow advanced: sensors, XComs, custom operators
3. Great Expectations implementation
4. CI/CD for data pipelines
5. Performance optimization techniques

### Advanced (18+ months)
1. Architecture design: medallion, data vault, domain-driven
2. Custom connector development (Airbyte, Singer)
3. Advanced orchestration patterns
4. Data mesh and federated architectures
5. Cost optimization and performance tuning at scale

## Tool-Specific Resources

### dbt
- **Official Docs**: docs.getdbt.com
- **Community**: dbt Slack (30,000+ members)
- **Courses**: dbt Fundamentals, Analytics Engineering
- **Blog**: Locally Optimistic, dbt Labs blog

### Airflow
- **Official Docs**: airflow.apache.org
- **Book**: "Data Pipelines with Apache Airflow"
- **Community**: Apache Airflow Slack
- **Best Practices**: Astronomer guides

### Airbyte
- **Docs**: docs.airbyte.com
- **Connector Development**: airbyte.com/connector-development
- **Community**: Airbyte Slack

### Great Expectations
- **Docs**: docs.greatexpectations.io
- **Community**: Great Expectations Slack
- **Examples**: GE example gallery

## Success Criteria

### Technical Excellence
- All production pipelines have comprehensive tests
- Pipeline success rate >99.5%
- Data quality test coverage >80%
- Documented lineage for all data assets
- CI/CD deployed for all data pipelines

### Operational Maturity
- Clear SLAs defined and tracked
- Automated monitoring and alerting
- Runbooks for all critical pipelines
- Cost per GB trending downward
- Mean time to recovery (MTTR) <1 hour

### Business Impact
- Data freshness meets business requirements
- Self-service analytics enabled by reliable data
- Reduced manual data preparation work
- Increased trust in data accuracy
- Faster time to insights

## Version & Maintenance
- **Version**: 1.0
- **Last Updated**: 2025-11-19
- **Focus**: Modern ELT stack (dbt, Airflow, Airbyte, Great Expectations)
- **Review Cycle**: Quarterly (tools evolve rapidly)
