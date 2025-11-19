# Database Engineering Expert Skill

## Purpose

This Claude Code skill provides comprehensive database engineering expertise across SQL, NoSQL, distributed databases, query optimization, schema design, replication, sharding, and production database operations. It helps you design scalable database architectures, optimize query performance, implement high availability solutions, and troubleshoot complex database issues.

## Capabilities

### 1. Database Design & Architecture
- Schema design for relational and NoSQL databases
- Normalization and denormalization strategies
- Database technology selection (SQL vs NoSQL)
- Multi-database architecture patterns
- Data modeling for specific access patterns

### 2. Query Optimization
- Slow query identification and analysis
- Execution plan interpretation
- Index strategy design and optimization
- Query rewriting for performance
- Pagination and batching strategies

### 3. Performance Tuning
- Database server configuration
- Connection pooling setup
- Multi-layer caching architectures
- Buffer pool and memory optimization
- I/O performance tuning

### 4. High Availability & Replication
- Streaming replication setup (PostgreSQL, MySQL)
- Failover automation with Patroni
- Multi-region deployment strategies
- Read replica configuration
- Disaster recovery planning

### 5. Data Migration & Schema Evolution
- Zero-downtime migration strategies
- Dual-write patterns
- Schema evolution best practices
- Online DDL operations
- Data backfill procedures

### 6. Monitoring & Observability
- Key metrics and golden signals
- Performance monitoring queries
- Alerting rule configuration
- Capacity planning
- Slow query analysis

### 7. Security
- Role-based access control (RBAC)
- Encryption at rest and in transit
- SQL injection prevention
- Row-level security (RLS)
- Audit logging

### 8. Troubleshooting
- Deadlock analysis and resolution
- Connection pool exhaustion
- Replication lag debugging
- Lock contention resolution
- Performance regression investigation

## Supported Database Systems

### Relational Databases
- **PostgreSQL** - Primary expertise, advanced features
- **MySQL** - InnoDB optimization, replication
- **Oracle** - Enterprise features, PL/SQL
- **SQL Server** - T-SQL, Always On
- **MariaDB** - MySQL fork with enhancements
- **CockroachDB** - Distributed SQL

### NoSQL Databases
- **MongoDB** - Document store, sharding
- **Cassandra** - Wide-column, high write throughput
- **DynamoDB** - AWS managed NoSQL
- **Redis** - In-memory cache and data store
- **Couchbase** - JSON document database
- **ScyllaDB** - Cassandra-compatible, high performance

### Specialized Databases
- **Time-Series**: InfluxDB, TimescaleDB, Prometheus
- **Graph**: Neo4j, Amazon Neptune, ArangoDB
- **Search**: Elasticsearch, OpenSearch, Meilisearch
- **Vector**: Pinecone, Weaviate, pgvector, Milvus

## When to Use This Skill

Use this skill when you need help with:

- ✅ Designing database schemas for new applications
- ✅ Optimizing slow queries or poor database performance
- ✅ Setting up replication and high availability
- ✅ Migrating databases with zero or minimal downtime
- ✅ Implementing caching strategies
- ✅ Troubleshooting deadlocks, connection issues, or replication lag
- ✅ Configuring database monitoring and alerting
- ✅ Choosing between database technologies
- ✅ Implementing database security best practices
- ✅ Scaling databases horizontally or vertically

## Usage Examples

### Example 1: Schema Design

**User**: "I'm building an e-commerce platform. Help me design the database schema for orders, users, and products."

**Skill Response**: Provides comprehensive schema design with:
- Entity-relationship analysis
- Normalized table structures
- Strategic index placement
- Constraint definitions
- Partitioning strategy for large tables
- Query pattern optimization

### Example 2: Query Optimization

**User**: "This query is taking 30 seconds to return results. How can I optimize it?"

**Skill Response**:
- Analyzes execution plan
- Identifies missing indexes
- Suggests query rewrites
- Provides before/after performance comparison
- Recommends monitoring to prevent regression

### Example 3: Migration Strategy

**User**: "We need to migrate our 500GB PostgreSQL database to a new server with zero downtime."

**Skill Response**:
- Outlines replication-based migration strategy
- Provides step-by-step execution plan
- Includes rollback procedures
- Suggests monitoring and validation steps
- Estimates migration timeline

### Example 4: High Availability Setup

**User**: "How do I set up automatic failover for my PostgreSQL database?"

**Skill Response**:
- Explains Patroni with etcd/Consul
- Provides complete configuration files
- Includes health check setup
- Describes failover scenarios and testing
- Recommends monitoring and alerting

## Prerequisites

To get the most out of this skill:

- **Basic SQL knowledge**: Familiarity with SELECT, INSERT, UPDATE, DELETE
- **Database access**: Connection credentials and permissions
- **Monitoring tools**: Access to database logs and metrics
- **Backup**: Always have backups before making schema changes

## Best Practices Applied

This skill follows industry best practices from:

- 📘 **PostgreSQL Official Documentation**
- 📘 **MySQL Reference Manual**
- 📘 **AWS Well-Architected Framework** (Database Lens)
- 📘 **Google Cloud Architecture Center** (Database Best Practices)
- 📘 **Use The Index, Luke** (SQL Performance Explained)
- 📘 **Designing Data-Intensive Applications** (Martin Kleppmann)
- 📘 **Database Reliability Engineering** (O'Reilly)

## Example Interactions

### Quick Query Optimization
```
User: "Optimize this query: SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC LIMIT 10"

Skill: Analyzes query, suggests composite index on (user_id, created_at DESC),
provides EXPLAIN ANALYZE comparison, estimates performance improvement
```

### Architecture Review
```
User: "Review my database setup: PostgreSQL primary + 2 read replicas, no connection pooling"

Skill: Identifies missing connection pooling layer, recommends PgBouncer configuration,
suggests monitoring for replication lag, provides implementation guide
```

### Troubleshooting
```
User: "My application is getting 'too many connections' errors"

Skill: Diagnoses connection pool exhaustion, identifies connection leaks in application code,
provides fixed code examples, recommends connection pooling best practices
```

## Safety Features

This skill prioritizes safety:

- ✅ Always recommends backups before schema changes
- ✅ Suggests testing in staging environments first
- ✅ Provides rollback procedures for migrations
- ✅ Warns about potentially dangerous operations
- ✅ Uses online DDL methods when available
- ✅ Includes data validation steps
- ✅ Recommends gradual rollouts for major changes

## Advanced Features

### Performance Analysis
- Execution plan interpretation
- Index strategy optimization
- Query pattern analysis
- Cache hit ratio optimization

### Scalability Planning
- Horizontal scaling strategies (sharding)
- Vertical scaling recommendations
- Read replica architecture
- Connection pooling configuration

### Operations
- Automated failover setup
- Backup and restore procedures
- Point-in-time recovery
- Capacity planning

## Getting Started

To use this skill:

1. **Describe your database challenge** - Be specific about your setup, data volume, and requirements
2. **Provide context** - Include database system, version, current performance metrics
3. **Share relevant code/queries** - The skill can analyze and optimize your specific queries
4. **Ask for clarification** - The skill will ask questions to fully understand your needs

## Templates Available

This skill includes templates for common database operations:

- `/templates/schema-design-template.md` - Relational database schema design
- `/templates/nosql-design-template.md` - NoSQL database modeling
- `/templates/query-optimization-template.md` - Query performance optimization
- `/templates/migration-plan-template.md` - Database migration planning
- `/templates/ha-setup-template.md` - High availability configuration
- `/templates/monitoring-template.md` - Database monitoring setup
- `/templates/troubleshooting-template.md` - Issue diagnosis checklist

## Troubleshooting This Skill

If the skill doesn't provide the help you need:

- **Be more specific** - Include database system, version, data volumes
- **Share error messages** - Exact error text helps diagnosis
- **Provide metrics** - Query times, connection counts, resource usage
- **Describe attempts** - What have you tried already?

## Contributing

Have suggestions for improving this skill? Want to add support for additional database systems? Feedback is welcome!

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [Database Reliability Engineering (O'Reilly)](https://www.oreilly.com/library/view/database-reliability-engineering/9781491925935/)
- [AWS Database Blog](https://aws.amazon.com/blogs/database/)
- [Percona Blog](https://www.percona.com/blog/)

---

**Ready to solve your database challenges?** Activate this skill and describe what you need help with!
