# Airbyte Connectors Reference

## Overview
Airbyte is an open-source data integration platform with 300+ pre-built connectors for extracting data from various sources and loading into destinations.

## Connector Categories

### Databases

#### Relational Databases
| Source | Type | CDC Support | Incremental | Notes |
|--------|------|-------------|-------------|-------|
| **PostgreSQL** | Source | ✅ (via WAL) | ✅ | Most popular, production-ready |
| **MySQL** | Source | ✅ (via binlog) | ✅ | Full featured, reliable |
| **SQL Server** | Source | ✅ (via CT) | ✅ | Enterprise-ready |
| **Oracle** | Source | ✅ (via LogMiner) | ✅ | Requires license |
| **MariaDB** | Source | ✅ (via binlog) | ✅ | MySQL compatible |
| **Amazon RDS** | Source | ✅ | ✅ | All RDS engines supported |
| **Amazon Aurora** | Source | ✅ | ✅ | PostgreSQL & MySQL |
| **Google Cloud SQL** | Source | ✅ | ✅ | Managed instances |

#### NoSQL Databases
| Source | Type | CDC Support | Incremental | Notes |
|--------|------|-------------|-------------|-------|
| **MongoDB** | Source | ✅ (via Change Streams) | ✅ | Atlas & self-hosted |
| **DynamoDB** | Source | ✅ (via Streams) | ✅ | AWS service |
| **Cassandra** | Source | ❌ | ✅ | Snapshot only |
| **Redis** | Source | ❌ | ❌ | Cache/session data |
| **Elasticsearch** | Source | ❌ | ✅ | Search index data |
| **CouchDB** | Source | ✅ | ✅ | Document store |

### SaaS Applications

#### Marketing & Advertising
| Source | Sync Mode | Key Streams | Rate Limits |
|--------|-----------|-------------|-------------|
| **Google Ads** | Full/Incremental | campaigns, ad_groups, ads, keywords | 15K req/day |
| **Facebook Ads** | Full/Incremental | campaigns, adsets, ads, insights | 200 calls/hour |
| **LinkedIn Ads** | Full/Incremental | campaigns, creatives, analytics | 1000 req/day |
| **Twitter Ads** | Full/Incremental | campaigns, tweets, analytics | Varies |
| **Snapchat Ads** | Full/Incremental | campaigns, ads, stats | 1000 req/hour |
| **TikTok Ads** | Full/Incremental | campaigns, ads, reports | 1000 req/day |
| **Pinterest Ads** | Full/Incremental | campaigns, ads, analytics | 1000 req/hour |
| **HubSpot** | Full/Incremental | contacts, companies, deals, emails | 10K req/day |
| **Mailchimp** | Full/Incremental | campaigns, lists, members | 10 calls/sec |
| **SendGrid** | Full/Incremental | messages, stats, bounces | 600 req/min |

#### CRM & Sales
| Source | Sync Mode | Key Streams | Notes |
|--------|-----------|-------------|-------|
| **Salesforce** | Full/Incremental/CDC | accounts, leads, opportunities, custom | Enterprise CRM |
| **HubSpot** | Full/Incremental | contacts, companies, deals | Free tier available |
| **Pipedrive** | Full/Incremental | deals, persons, organizations | Simple CRM |
| **Zendesk** | Full/Incremental | tickets, users, organizations | Support platform |
| **Intercom** | Full/Incremental | conversations, users, companies | Customer messaging |
| **Freshdesk** | Full/Incremental | tickets, contacts, companies | Help desk |
| **Close** | Full/Incremental | leads, opportunities, activities | Sales CRM |

#### E-Commerce & Payments
| Source | Sync Mode | Key Streams | Notes |
|--------|-----------|-------------|-------|
| **Shopify** | Full/Incremental | orders, customers, products, inventory | Leading e-commerce |
| **Stripe** | Full/Incremental | charges, customers, subscriptions, invoices | Payment processing |
| **PayPal** | Full/Incremental | transactions, orders, disputes | Payment gateway |
| **Square** | Full/Incremental | payments, orders, customers | POS + payments |
| **WooCommerce** | Full/Incremental | orders, products, customers | WordPress plugin |
| **Magento** | Full/Incremental | orders, products, customers | Adobe Commerce |
| **Amazon Seller** | Full/Incremental | orders, inventory, returns | Marketplace |

#### Analytics & Product
| Source | Sync Mode | Key Streams | Notes |
|--------|-----------|-------------|-------|
| **Google Analytics** | Full/Incremental | sessions, users, events, goals | GA4 & Universal |
| **Mixpanel** | Full/Incremental | events, users, funnels | Product analytics |
| **Amplitude** | Full/Incremental | events, users, cohorts | Behavioral analytics |
| **Segment** | Full/Incremental | events, users, identifies | CDP platform |
| **Heap** | Full/Incremental | events, users, sessions | Auto-capture |

#### Collaboration & Productivity
| Source | Sync Mode | Key Streams | Notes |
|--------|-----------|-------------|-------|
| **Google Sheets** | Full | sheets, tabs, cells | Simple data source |
| **Airtable** | Full/Incremental | tables, records | Flexible database |
| **Notion** | Full/Incremental | pages, databases, blocks | Knowledge management |
| **Slack** | Full/Incremental | messages, channels, users | Team chat |
| **Jira** | Full/Incremental | issues, projects, sprints | Issue tracking |
| **GitHub** | Full/Incremental | repos, commits, PRs, issues | Code hosting |
| **GitLab** | Full/Incremental | projects, commits, MRs | DevOps platform |

#### File & Object Storage
| Source | Sync Mode | Format Support | Notes |
|--------|-----------|----------------|-------|
| **Amazon S3** | Full/Incremental | CSV, JSON, Parquet, Avro | Object storage |
| **Google Cloud Storage** | Full/Incremental | CSV, JSON, Parquet, Avro | GCP storage |
| **Azure Blob** | Full/Incremental | CSV, JSON, Parquet, Avro | Azure storage |
| **SFTP** | Full/Incremental | CSV, JSON, XML | Secure file transfer |
| **Google Drive** | Full/Incremental | Sheets, CSV, JSON | Cloud storage |
| **Dropbox** | Full/Incremental | CSV, JSON | File sync |

### Data Warehouses (Destinations)

#### Cloud Warehouses
| Destination | Features | Best For | Limitations |
|-------------|----------|----------|-------------|
| **Snowflake** | All features, fast loading | Enterprise, large scale | Cost at scale |
| **BigQuery** | Streaming insert, partitioning | Google Cloud, real-time | Data residency |
| **Redshift** | S3 staging, COPY command | AWS ecosystem | Concurrency |
| **Databricks** | Delta Lake, Unity Catalog | Data science, ML | Complexity |
| **Azure Synapse** | PolyBase, distributed | Azure ecosystem | Learning curve |
| **ClickHouse** | High performance, compression | Real-time analytics | Limited SQL |
| **Postgres** | Standard SQL, extensions | Self-hosted, small data | Not for big data |

#### Data Lakes
| Destination | Format | Features | Use Case |
|-------------|--------|----------|----------|
| **S3** | Parquet, JSON, CSV | Durable, cheap storage | Data lake |
| **GCS** | Parquet, JSON, CSV | GCP native | GCP data lake |
| **Azure Blob** | Parquet, JSON, CSV | Azure native | Azure data lake |
| **Delta Lake** | Delta format | ACID transactions | Lakehouse |

## Sync Modes Explained

### Full Refresh
```yaml
sync_mode: full_refresh
destination_sync_mode: overwrite
```
- Extracts all data from source each sync
- Overwrites destination table completely
- **Use when**: Small tables, no reliable cursor, data frequently changes everywhere

### Incremental - Append
```yaml
sync_mode: incremental
destination_sync_mode: append
```
- Extracts only new/modified records (via cursor)
- Appends to destination without deduplication
- **Use when**: Event logs, immutable records, time-series data

### Incremental - Deduped
```yaml
sync_mode: incremental
destination_sync_mode: append_dedup
```
- Extracts only new/modified records
- Deduplicates based on primary key
- **Use when**: Mutable records, standard database tables

### Change Data Capture (CDC)
```yaml
sync_mode: incremental
destination_sync_mode: append_dedup
replication_method: CDC
```
- Captures changes from database transaction log
- Low-latency, minimal source impact
- Includes deletes (marked as `_ab_cdc_deleted_at`)
- **Use when**: Large databases, need real-time, want deletes

## Configuration Patterns

### PostgreSQL CDC Setup
```yaml
source:
  type: postgres
  host: database.example.com
  port: 5432
  database: production
  username: airbyte_user
  password: ${POSTGRES_PASSWORD}
  schemas:
    - public
    - analytics
  replication_method:
    method: CDC
    plugin: pgoutput  # or wal2json
    publication: airbyte_publication
    replication_slot: airbyte_slot
```

### Salesforce Incremental
```yaml
source:
  type: salesforce
  client_id: ${SF_CLIENT_ID}
  client_secret: ${SF_CLIENT_SECRET}
  refresh_token: ${SF_REFRESH_TOKEN}
  is_sandbox: false
  start_date: '2024-01-01T00:00:00Z'
  streams:
    - name: Account
      sync_mode: incremental
      cursor_field: SystemModstamp
    - name: Opportunity
      sync_mode: incremental
      cursor_field: LastModifiedDate
```

### API Rate Limiting
```yaml
source:
  type: google-ads
  credentials:
    developer_token: ${GOOGLE_ADS_DEV_TOKEN}
    client_id: ${GOOGLE_ADS_CLIENT_ID}
    client_secret: ${GOOGLE_ADS_CLIENT_SECRET}
    refresh_token: ${GOOGLE_ADS_REFRESH_TOKEN}
  customer_id: '1234567890'
  start_date: '2024-01-01'
  # Automatic rate limiting built-in
  # Airbyte handles retries and backoff
```

### File-Based Source (S3)
```yaml
source:
  type: s3
  dataset: my_dataset
  path_pattern: 'data/orders/*.csv'
  format:
    filetype: csv
    delimiter: ','
    quote_char: '"'
    escape_char: '\\'
    encoding: 'utf-8'
    double_quote: true
    skip_rows_before_header: 0
    skip_rows_after_header: 0
  provider:
    bucket: my-bucket
    aws_access_key_id: ${AWS_ACCESS_KEY}
    aws_secret_access_key: ${AWS_SECRET_KEY}
    region_name: us-east-1
```

## Normalization

### Basic Normalization (dbt-based)
```yaml
# Airbyte creates:
# 1. Raw tables: _airbyte_raw_<stream_name>
# 2. Normalized tables: <stream_name> (via dbt)

normalization:
  option: basic
  # Generates dbt project in airbyte_normalization schema
  # Handles nested JSON, type casting, deduplication
```

### Custom Normalization
```yaml
normalization:
  option: none
  # Use your own dbt project for transformations
  # More control, easier to customize
  # Recommended for production
```

## Performance Optimization

### Connector Performance Tips

1. **Use CDC when possible** - Minimal source impact, fastest syncs
2. **Set appropriate sync frequency** - Don't sync more often than needed
3. **Select only needed streams** - Reduce data volume
4. **Use incremental sync** - Avoid full refresh for large tables
5. **Partition large files** - Split S3/GCS files by date
6. **Optimize cursor fields** - Index timestamp columns at source
7. **Monitor connector logs** - Identify bottlenecks

### Resource Allocation
```yaml
# docker-compose.yml or Kubernetes config
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"

# For heavy workloads:
# - Postgres CDC: 4GB RAM
# - Large API syncs: 8GB RAM
# - File parsing: 2-4GB RAM
```

## Error Handling

### Common Issues

#### Connection Timeout
```
Error: Connection timeout after 30 seconds
Solution: Check network, firewall, increase timeout in config
```

#### Rate Limit Exceeded
```
Error: 429 Too Many Requests
Solution: Airbyte auto-retries with exponential backoff
         Reduce sync frequency or contact provider
```

#### Schema Change
```
Error: Column 'new_field' not in destination
Solution: Enable auto-add columns or run schema refresh
```

#### CDC Slot Full
```
Error: Replication slot 'airbyte_slot' is full
Solution: Increase wal_keep_size, reduce sync lag
```

### Retry Configuration
```yaml
# Built into connectors
max_retries: 3
retry_delay_seconds: 30
backoff_multiplier: 2
# Will retry at 30s, 60s, 120s intervals
```

## Monitoring

### Key Metrics
- **Records Synced**: Track data volume trends
- **Sync Duration**: Identify performance degradation
- **Sync Frequency**: Ensure meets SLA
- **Error Rate**: Monitor connector health
- **Data Freshness**: Time since last successful sync

### Airbyte API for Monitoring
```bash
# Get connection status
curl -X POST http://localhost:8001/api/v1/connections/get \
  -H "Content-Type: application/json" \
  -d '{"connectionId": "your-connection-id"}'

# Get sync history
curl -X POST http://localhost:8001/api/v1/jobs/list \
  -H "Content-Type: application/json" \
  -d '{"configTypes": ["sync"], "configId": "connection-id"}'
```

## Custom Connector Development

### Connector Development Kit (CDK)
```python
# Low-code YAML connector
# connector-definition.yaml
streams:
  - name: users
    primary_key: id
    url_base: https://api.example.com
    path: /users
    http_method: GET
    retriever:
      type: SimpleRetriever
      paginator:
        type: DefaultPaginator
        page_size: 100
        page_token_option:
          type: RequestOption
          inject_into: request_parameter
          field_name: page
```

### Python CDK
```python
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http import HttpStream

class Users(HttpStream):
    url_base = "https://api.example.com/"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"

    def parse_response(self, response, **kwargs):
        return response.json()["data"]
```

## Best Practices

### Configuration
- ✅ Use secrets management for credentials
- ✅ Enable auto-schema detection
- ✅ Set appropriate primary keys
- ✅ Configure cursor fields for incremental
- ✅ Use CDC for large, frequently changing tables

### Operations
- ✅ Monitor sync success rates
- ✅ Set up alerts for failed syncs
- ✅ Regular connector version updates
- ✅ Test in dev before production changes
- ✅ Document connector configurations

### Performance
- ✅ Use incremental sync modes
- ✅ Sync only needed columns (when supported)
- ✅ Schedule syncs during low-traffic periods
- ✅ Use connection pooling for databases
- ✅ Monitor and optimize resource usage

## Resources

- **Connector Catalog**: https://docs.airbyte.com/integrations/
- **CDK Documentation**: https://docs.airbyte.com/connector-development/
- **Community Slack**: https://airbyte.com/community
- **GitHub**: https://github.com/airbytehq/airbyte
- **Status Page**: https://status.airbyte.io/
