# Data Modeling Best Practices Checklist

## Pre-Design Phase

### Business Requirements
- [ ] **Business processes identified** and prioritized
- [ ] **Key stakeholders** engaged and available
- [ ] **Business questions** documented (what decisions will be made?)
- [ ] **Success metrics** defined (how will we measure success?)
- [ ] **Data sources** identified and accessible
- [ ] **Data quality** assessed (completeness, accuracy, consistency)
- [ ] **Update frequency** requirements understood
- [ ] **Historical requirements** defined (how much history?)
- [ ] **User community** characterized (technical level, tool preferences)

### Project Planning
- [ ] **Methodology chosen** (Kimball, Inmon, Data Vault, hybrid)
- [ ] **Scope defined** (start small, expand incrementally)
- [ ] **Team roles** assigned (data modeler, ETL developer, BI developer)
- [ ] **Tool stack** selected (database, ETL, BI, modeling tools)
- [ ] **Development environment** provisioned
- [ ] **Naming conventions** established
- [ ] **Coding standards** documented
- [ ] **Version control** implemented

---

## Dimensional Modeling (Kimball)

### Grain Declaration
- [ ] **Grain explicitly stated**: "One row per..."
- [ ] **Atomic grain preferred** unless compelling reason otherwise
- [ ] **Single grain per fact table** (never mixed grains)
- [ ] **Grain validated** with business users (concrete examples)
- [ ] **Future flexibility** considered

### Dimension Design
- [ ] **Dimensions denormalized** (star schema, not snowflake)
- [ ] **Surrogate keys** used for all dimensions
- [ ] **Natural keys** preserved in dimensions
- [ ] **Descriptive attributes** included (business-friendly names)
- [ ] **Hierarchies** embedded in dimensions
- [ ] **Unknown members** defined (key = 0 or -1)
- [ ] **SCD strategy** chosen per dimension/attribute
  - [ ] Type 0: Retain original value
  - [ ] Type 1: Overwrite (current state only)
  - [ ] Type 2: Add new row (history tracking)
  - [ ] Type 3: Add new column (one previous value)
  - [ ] Type 4: Mini-dimension (rapidly changing)
- [ ] **Effective/expiration dates** for Type 2 dimensions
- [ ] **Current flag** for Type 2 dimensions
- [ ] **Junk dimensions** for low-cardinality flags
- [ ] **Role-playing dimensions** handled with views
- [ ] **Mini-dimensions** for rapidly changing attributes

### Fact Table Design
- [ ] **Grain matches all facts** (no mixed grains)
- [ ] **Additive facts** preferred (can sum across all dimensions)
- [ ] **Semi-additive facts** documented (e.g., balances)
- [ ] **Non-additive facts** avoided or stored as attributes
- [ ] **Foreign keys NOT NULL** (use unknown members)
- [ ] **Surrogate keys** used for foreign keys (not natural keys)
- [ ] **Degenerate dimensions** identified (transaction numbers)
- [ ] **No dimension attributes** in fact table
- [ ] **Fact table types** chosen appropriately:
  - [ ] Transaction (event-level)
  - [ ] Periodic snapshot (regular intervals)
  - [ ] Accumulating snapshot (process/pipeline)
  - [ ] Factless (events without measures)
- [ ] **Aggregate fact tables** planned for performance

### Conformed Dimensions
- [ ] **Bus matrix created** (dimensions × fact tables)
- [ ] **Conformed dimensions identified** (customer, date, product)
- [ ] **Dimension structure** standardized across data marts
- [ ] **Dimension values** consistent across uses
- [ ] **Dimension ownership** assigned (steward)
- [ ] **Change control process** established
- [ ] **Update SLA** defined

---

## Enterprise Data Warehouse (Inmon)

### EDW Design
- [ ] **Subject areas** identified (customer, product, order, etc.)
- [ ] **3NF normalization** applied in EDW
- [ ] **Atomic data** stored (lowest level of detail)
- [ ] **Time-variant** structures for history
- [ ] **Non-volatile** (insert-only preferred)
- [ ] **Integrated** across source systems
- [ ] **Enterprise data model** documented
- [ ] **Data quality rules** enforced in EDW

### Dependent Data Marts
- [ ] **Dimensional models** derived from EDW
- [ ] **Data marts** built from EDW (not directly from sources)
- [ ] **Star schemas** in data marts
- [ ] **Business-specific** aggregations and calculations
- [ ] **Extract logic** optimized (EDW as single source)

---

## Data Vault 2.0

### Hub Design
- [ ] **Business keys** identified (immutable, unique)
- [ ] **One hub** per business concept
- [ ] **Hash keys** used for performance
- [ ] **Load metadata** included (load_date, record_source)
- [ ] **Insert-only** (never update or delete)

### Link Design
- [ ] **Relationships** between hubs captured
- [ ] **Links connect hubs** only (no links to links)
- [ ] **Foreign keys** to participating hubs
- [ ] **Hash keys** based on hub keys
- [ ] **Degenerate data** limited (transaction IDs only)
- [ ] **Load metadata** included

### Satellite Design
- [ ] **Descriptive attributes** separated from keys
- [ ] **Hash diff** for change detection
- [ ] **Composite PK**: (hash_key, load_date)
- [ ] **Load_end_date** for end-dating (optional)
- [ ] **Insert-only** (new row for each change)
- [ ] **Source-specific** satellites when needed

### Raw Vault
- [ ] **Source-aligned** (no business rules)
- [ ] **Complete audit trail** maintained
- [ ] **Insert-only** strictly enforced
- [ ] **Parallel loading** enabled

### Business Vault
- [ ] **Business rules** applied in business vault
- [ ] **Calculated fields** in computed satellites
- [ ] **Derived relationships** in business links
- [ ] **Soft business rules** documented

### Performance
- [ ] **PIT tables** created for time-variant queries
- [ ] **Bridge tables** for dimensional views
- [ ] **Hash keys** indexed
- [ ] **Partitioning** by load_date

---

## Physical Design

### Database Objects
- [ ] **Naming conventions** applied consistently
- [ ] **Table prefixes** used (DIM_, FACT_, HUB_, SAT_, LINK_)
- [ ] **Primary keys** defined on all tables
- [ ] **Foreign keys** defined for referential integrity
- [ ] **Unique constraints** on natural keys
- [ ] **Check constraints** for data quality
- [ ] **Default values** for audit columns

### Indexes
- [ ] **Primary key indexes** created
- [ ] **Foreign key indexes** on fact tables
- [ ] **Natural key indexes** on dimensions
- [ ] **SCD indexes** (natural_key, current_flag)
- [ ] **Bitmap indexes** on low-cardinality columns (if supported)
- [ ] **Columnstore indexes** on large facts (if beneficial)
- [ ] **Covering indexes** for critical queries
- [ ] **Filtered indexes** for sparse data
- [ ] **Index usage** monitored, unused indexes removed

### Partitioning
- [ ] **Large fact tables** partitioned (by date typically)
- [ ] **Partition strategy** aligned with query patterns
- [ ] **Partition maintenance** automated
- [ ] **Partition pruning** verified in query plans

### Performance
- [ ] **Statistics** updated regularly
- [ ] **Compression** enabled where beneficial
- [ ] **Parallel processing** configured
- [ ] **Memory allocation** optimized
- [ ] **Query plans** analyzed for critical queries
- [ ] **Execution time** benchmarked

---

## Data Quality

### Validation
- [ ] **NULL handling** defined (allow or use defaults?)
- [ ] **Referential integrity** enforced
- [ ] **Data type** validation
- [ ] **Value range** validation (min/max, allowed values)
- [ ] **Business rule** validation
- [ ] **Duplicate detection** and handling
- [ ] **Orphaned records** prevented

### Error Handling
- [ ] **Error logging** implemented
- [ ] **Reject records** captured and reviewed
- [ ] **Data quality metrics** tracked
- [ ] **Quality dimension/flags** in tables
- [ ] **Reconciliation reports** automated
- [ ] **Data quality dashboard** created

---

## ETL/ELT

### Extract
- [ ] **Change data capture** implemented (if needed)
- [ ] **Full vs incremental** strategy defined
- [ ] **Source system impact** minimized
- [ ] **Extract windows** defined and monitored

### Transform
- [ ] **Data cleansing** rules documented
- [ ] **Standardization** applied (names, addresses, codes)
- [ ] **Derived values** calculated
- [ ] **Surrogate keys** generated
- [ ] **SCD logic** implemented correctly
- [ ] **Business rules** applied consistently
- [ ] **Hash keys** generated (Data Vault)

### Load
- [ ] **Load order** correct (dimensions before facts)
- [ ] **Batch processing** for efficiency
- [ ] **Incremental loading** where possible
- [ ] **Idempotent** (can re-run safely)
- [ ] **Transaction management** for atomicity
- [ ] **Error recovery** procedures defined

### Metadata
- [ ] **Data lineage** documented
- [ ] **Source-to-target** mapping documented
- [ ] **Transformation rules** documented
- [ ] **Refresh schedules** documented
- [ ] **Dependencies** identified

---

## Testing

### Unit Testing
- [ ] **Dimension loading** tested
- [ ] **Fact loading** tested
- [ ] **SCD logic** tested (all types)
- [ ] **Aggregations** verified
- [ ] **Calculations** validated

### Integration Testing
- [ ] **End-to-end** data flow tested
- [ ] **Source-to-report** tested
- [ ] **Cross-data mart** queries tested
- [ ] **Conformed dimensions** validated

### Data Validation
- [ ] **Row counts** reconciled (source vs target)
- [ ] **Sum totals** reconciled
- [ ] **NULL values** acceptable or investigated
- [ ] **Duplicate keys** detected and resolved
- [ ] **Referential integrity** violations caught
- [ ] **Business rules** validated

### Performance Testing
- [ ] **Query performance** benchmarked
- [ ] **ETL performance** measured
- [ ] **Scalability** tested (with larger data volumes)
- [ ] **Concurrent users** tested

---

## Documentation

### Design Documentation
- [ ] **Conceptual model** (business view)
- [ ] **Logical model** (entities and relationships)
- [ ] **Physical model** (tables, columns, datatypes)
- [ ] **Grain declarations** for all facts
- [ ] **SCD strategies** per dimension/attribute
- [ ] **Business rules** documented

### Technical Documentation
- [ ] **ERD diagrams** created and maintained
- [ ] **Data dictionary** (table and column descriptions)
- [ ] **ETL specifications** documented
- [ ] **Data lineage** diagrams
- [ ] **Index strategy** documented
- [ ] **Naming conventions** documented

### User Documentation
- [ ] **Business glossary** created
- [ ] **Metric definitions** documented
- [ ] **Report catalog** maintained
- [ ] **User guides** for BI tools
- [ ] **Training materials** prepared

---

## Governance

### Ownership
- [ ] **Data stewards** assigned per subject area
- [ ] **Dimension owners** assigned for conformed dimensions
- [ ] **ETL owners** assigned
- [ ] **BI report owners** assigned

### Change Control
- [ ] **Change request process** defined
- [ ] **Impact analysis** required for changes
- [ ] **Approval workflow** established
- [ ] **Deployment procedures** documented
- [ ] **Rollback procedures** prepared

### Security
- [ ] **Row-level security** implemented (if needed)
- [ ] **Column-level security** implemented (if needed)
- [ ] **User roles** defined
- [ ] **Access permissions** granted per role
- [ ] **Audit logging** enabled
- [ ] **Compliance** requirements met (GDPR, HIPAA, etc.)

### Monitoring
- [ ] **ETL monitoring** automated (success/failure alerts)
- [ ] **Data quality monitoring** (thresholds and alerts)
- [ ] **Performance monitoring** (query time, ETL duration)
- [ ] **Storage monitoring** (growth trends)
- [ ] **User activity** monitored

---

## Production Deployment

### Pre-Deployment
- [ ] **Development** complete and tested
- [ ] **Code reviewed** by peers
- [ ] **Documentation** updated
- [ ] **Deployment plan** created
- [ ] **Rollback plan** prepared
- [ ] **Stakeholders** notified

### Deployment
- [ ] **Off-hours deployment** scheduled (if needed)
- [ ] **Backups** completed before deployment
- [ ] **Scripts** version-controlled
- [ ] **Deployment** automated where possible
- [ ] **Smoke tests** run post-deployment
- [ ] **Stakeholders** notified of completion

### Post-Deployment
- [ ] **Production data** validated
- [ ] **Reports** tested in production
- [ ] **Performance** monitored
- [ ] **User feedback** collected
- [ ] **Issues** logged and tracked
- [ ] **Lessons learned** documented

---

## Maintenance

### Regular Tasks
- [ ] **Index maintenance** (rebuild/reorganize)
- [ ] **Statistics updates** scheduled
- [ ] **Partition management** (add new, archive old)
- [ ] **Data archival** strategy implemented
- [ ] **Log file management**
- [ ] **Backup and recovery** tested

### Continuous Improvement
- [ ] **Query performance** reviewed regularly
- [ ] **ETL optimization** opportunities identified
- [ ] **User feedback** incorporated
- [ ] **New requirements** prioritized
- [ ] **Technology updates** evaluated
- [ ] **Best practices** updated

---

## Quick Decision Trees

### Choosing Methodology
- **Need enterprise integration + atomic data?** → Inmon (3NF EDW)
- **Need fast delivery + business-friendly?** → Kimball (dimensional)
- **Need flexibility + auditability?** → Data Vault 2.0
- **Have mature BI program?** → Hybrid approach

### Choosing SCD Type
- **Need full history?** → Type 2
- **Only current state matters?** → Type 1
- **Need one previous value?** → Type 3
- **Rapidly changing attributes?** → Type 4 (mini-dimension)
- **Need both historical and current?** → Type 6 (hybrid)

### Indexing Strategy
- **Small dimension (<10M rows)?** → B-tree indexes
- **Large fact (>100M rows, read-only)?** → Bitmap or columnstore
- **OLTP-style updates?** → B-tree only
- **Analytical queries only?** → Columnstore

### Fact Table Type
- **Event-level detail?** → Transaction fact
- **Regular interval snapshots?** → Periodic snapshot
- **Process/workflow tracking?** → Accumulating snapshot
- **Event occurrence without measures?** → Factless fact

---

## Common Anti-Patterns to Avoid

- [ ] **Snowflaking** dimensions excessively
- [ ] **NULL foreign keys** in facts (use unknown members)
- [ ] **Smart keys** (embedded meaning in keys)
- [ ] **Dimension attributes** in fact tables
- [ ] **Mixed grains** in single fact table
- [ ] **Natural keys** as foreign keys in facts (use surrogates)
- [ ] **Type 2 SCD** on rapidly changing attributes
- [ ] **No conformed dimensions** across data marts
- [ ] **Fact-to-fact** table joins (use drill-across instead)
- [ ] **Premature aggregation** (store atomic grain)

---

## Checklist Summary

### Must-Have
✓ Grain explicitly declared for all facts
✓ Surrogate keys for all dimensions
✓ Unknown members for all dimensions
✓ Atomic grain stored
✓ Conformed dimensions for enterprise
✓ Consistent naming conventions
✓ Documentation complete
✓ Data quality validation
✓ Testing comprehensive

### Should-Have
✓ SCD Type 2 for important history
✓ Bitmap or columnstore indexes for large facts
✓ Partitioning for very large tables
✓ Aggregate tables for performance
✓ ETL monitoring and alerting
✓ Change control process

### Nice-to-Have
✓ Automated documentation generation
✓ Self-service BI semantic layer
✓ Real-time/streaming data integration
✓ Machine learning integration
✓ Advanced analytics functions
