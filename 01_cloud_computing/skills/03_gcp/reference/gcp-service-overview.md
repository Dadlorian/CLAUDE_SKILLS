# Google Cloud Platform Service Overview

## Complete GCP Service Catalog Reference

### Compute Services

#### Compute Engine
- **Description**: Infrastructure as a Service (IaaS) - Virtual machines running in Google's data centers
- **Use Cases**: Custom applications, lift-and-shift migrations, Windows workloads, GPU/TPU workloads
- **Key Features**:
  - Machine types: predefined, custom, memory-optimized, compute-optimized
  - Preemptible/Spot VMs (up to 91% discount)
  - Live migration for maintenance
  - Persistent disks (SSD/HDD), local SSDs, persistent disk snapshots
  - Instance templates and managed instance groups
  - Sole-tenant nodes for compliance
- **Pricing**: Per-second billing, sustained use discounts, committed use discounts
- **SLA**: 99.99% for regional MIGs, 99.5% for single instance

#### Google Kubernetes Engine (GKE)
- **Description**: Managed Kubernetes service
- **Modes**: Standard (full control), Autopilot (Google-managed)
- **Key Features**:
  - Auto-upgrade, auto-repair
  - Workload Identity for secure pod authentication
  - Binary Authorization for container security
  - GKE Enterprise (formerly Anthos) for hybrid/multi-cloud
  - Node pools, cluster autoscaling, pod autoscaling
  - Integrated logging and monitoring
- **Use Cases**: Microservices, containerized applications, hybrid cloud
- **SLA**: 99.95% for regional clusters, 99.5% for zonal

#### Cloud Run
- **Description**: Fully managed serverless platform for containers
- **Key Features**:
  - Autoscaling from 0 to N
  - Pay per use (CPU, memory, requests)
  - Custom domains, traffic splitting
  - Cloud Run for Anthos (run on GKE)
  - Request timeout up to 60 minutes
  - Support for HTTP/2, gRPC, WebSockets
- **Use Cases**: APIs, web apps, microservices, event processing
- **SLA**: 99.95%

#### Cloud Functions
- **Description**: Event-driven serverless functions
- **Generations**: 1st gen (Cloud Functions), 2nd gen (built on Cloud Run)
- **Runtimes**: Node.js, Python, Go, Java, .NET, Ruby, PHP
- **Triggers**: HTTP, Pub/Sub, Cloud Storage, Firestore, Firebase
- **Use Cases**: Webhooks, data processing, IoT backends, mobile backends
- **Limits**: 9 min timeout (1st gen), 60 min (2nd gen)

#### App Engine
- **Description**: Platform as a Service (PaaS)
- **Environments**: Standard (sandboxed, instant scaling), Flexible (Docker containers)
- **Languages**: Python, Java, Node.js, Go, PHP, Ruby, .NET
- **Features**: Traffic splitting, version management, cron jobs, task queues
- **Use Cases**: Web applications, mobile backends, RESTful APIs

### Storage Services

#### Cloud Storage
- **Description**: Object storage for unstructured data
- **Storage Classes**:
  - Standard: Hot data, frequent access
  - Nearline: Accessed < once/month, 30-day minimum
  - Coldline: Accessed < once/quarter, 90-day minimum
  - Archive: Accessed < once/year, 365-day minimum
- **Key Features**:
  - 11 nines of durability
  - Versioning, lifecycle management
  - Signed URLs, IAM, ACLs
  - Object holds, retention policies
  - Customer-managed encryption keys (CMEK)
- **Use Cases**: Media storage, backups, data lakes, archives

#### Persistent Disk
- **Types**: Standard (HDD), Balanced (SSD), Performance (SSD), Extreme (customizable IOPS)
- **Features**: Snapshots, regional persistent disks, encryption
- **Performance**: Up to 100,000 IOPS, 2,400 MB/s throughput per VM
- **Use Cases**: VM boot disks, database storage

#### Filestore
- **Description**: Managed NFS file storage
- **Tiers**: Basic (HDD/SSD), High Scale, Enterprise
- **Capacity**: 1 TB to 320 TB
- **Use Cases**: Shared file storage, media rendering, genomics

### Database Services

#### Cloud SQL
- **Engines**: MySQL 5.6/5.7/8.0, PostgreSQL 9.6-15, SQL Server 2017/2019
- **Features**: Automated backups, point-in-time recovery, read replicas, high availability
- **Max Size**: 64 TB MySQL/PostgreSQL, 10 TB SQL Server
- **Use Cases**: Web apps, transactional workloads, CMS
- **SLA**: 99.95% (HA configuration)

#### Cloud Spanner
- **Description**: Horizontally scalable, strongly consistent, relational database
- **Features**: Multi-region support, external consistency, automatic sharding
- **Scale**: Unlimited (petabytes), 10,000+ QPS per node
- **Use Cases**: Financial services, gaming leaderboards, global e-commerce
- **SLA**: 99.99% regional, 99.999% multi-region

#### Firestore
- **Description**: NoSQL document database
- **Modes**: Native (mobile/web), Datastore (server)
- **Features**: Real-time sync, offline support, ACID transactions, composite indexes
- **Scale**: 1 million concurrent connections, 10,000 writes/sec
- **Use Cases**: Mobile apps, real-time collaboration, gaming

#### Bigtable
- **Description**: Wide-column NoSQL database
- **API**: HBase-compatible
- **Features**: Petabyte-scale, single-digit ms latency, replication
- **Use Cases**: Time series, IoT, financial data, AdTech
- **SLA**: 99.9% (single-cluster), 99.99% (multi-cluster routing)

#### Memorystore
- **Engines**: Redis, Memcached
- **Tiers**: Basic (no replication), Standard (HA with automatic failover)
- **Features**: Sub-millisecond latency, automatic patching, VPC peering
- **Use Cases**: Caching, session management, gaming leaderboards

### Analytics & Big Data

#### BigQuery
- **Description**: Serverless, petabyte-scale data warehouse
- **Features**:
  - Standard SQL, streaming inserts
  - Partitioned and clustered tables
  - Materialized views, BI Engine
  - ML with BigQuery ML
  - Omni for multi-cloud analytics
- **Pricing**: On-demand ($5/TB), flat-rate slots
- **Performance**: Analyze terabytes in seconds
- **SLA**: 99.99% (flat-rate), 99.9% (on-demand)

#### Dataflow
- **Description**: Fully managed Apache Beam for batch and streaming
- **Features**: Autoscaling, templates, SQL, shuffle service
- **Use Cases**: ETL, real-time analytics, data enrichment
- **Pricing**: CPU, memory, disk per second

#### Dataproc
- **Description**: Managed Hadoop and Spark
- **Features**: Fast cluster creation (90 sec), autoscaling, component gateway
- **Versions**: Hadoop, Spark, Hive, Pig, Presto
- **Use Cases**: Data lake modernization, ML pipelines
- **Pricing**: Compute + 1¢ per vCPU-hour Dataproc fee

#### Pub/Sub
- **Description**: Asynchronous messaging service
- **Features**:
  - At-least-once delivery, exactly-once processing
  - Message ordering, dead-letter topics
  - Schema validation, push/pull subscriptions
  - Message retention up to 31 days
- **Scale**: Millions of messages/sec
- **Use Cases**: Event-driven systems, streaming analytics
- **SLA**: 99.95%

#### Datastream
- **Description**: Serverless change data capture (CDC)
- **Sources**: Oracle, MySQL, PostgreSQL, AlloyDB
- **Targets**: Cloud Storage, BigQuery, Pub/Sub
- **Use Cases**: Database replication, analytics, event-driven architectures

### AI & Machine Learning

#### Vertex AI
- **Components**:
  - AutoML: No-code ML model training
  - Custom Training: TensorFlow, PyTorch, scikit-learn
  - Prediction: Batch and online predictions
  - Workbench: Managed Jupyter notebooks
  - Feature Store: Centralized feature management
  - Model Monitoring: Drift detection, explanations
- **Pre-trained APIs**: Vision, NLP, Speech, Translation, Video
- **Use Cases**: Custom ML models, AutoML, MLOps

#### AI Platform (Legacy)
- **Status**: Being migrated to Vertex AI
- **Features**: Training, prediction, pipelines, notebooks

### Networking Services

#### Virtual Private Cloud (VPC)
- **Types**: Auto mode, custom mode
- **Features**: Subnets, firewall rules, routes, Private Google Access
- **Sharing**: Shared VPC, VPC peering
- **Connectivity**: Cloud VPN, Cloud Interconnect
- **IP Addressing**: Internal, external, static, ephemeral

#### Cloud Load Balancing
- **Types**:
  - Global HTTP(S): Layer 7, global anycast
  - Global TCP Proxy: Layer 4, SSL offloading
  - Global SSL Proxy: SSL/TLS termination
  - Regional Network: Layer 4, pass-through
  - Regional Internal: Layer 4, internal traffic
  - Cross-region Internal: Layer 7, internal multi-region
- **Features**: Autoscaling, health checks, CDN integration, SSL certificates
- **SLA**: 99.99%

#### Cloud CDN
- **Description**: Content delivery network
- **Features**: Cache modes, signed URLs/cookies, QUIC support
- **PoPs**: 100+ locations worldwide
- **Integration**: Cloud Load Balancing, Cloud Storage

#### Cloud Armor
- **Description**: DDoS protection and WAF
- **Features**: Rate limiting, geo-blocking, custom rules, adaptive protection
- **Integration**: Cloud Load Balancing
- **Pricing**: Per policy, per rule, per request

#### Cloud DNS
- **Description**: Managed authoritative DNS service
- **Types**: Public zones, private zones
- **Features**: DNSSEC, split horizon DNS, forwarding, peering
- **SLA**: 100% uptime SLA
- **Performance**: Sub-second query response

#### Cloud VPN
- **Types**: HA VPN (99.99% SLA), Classic VPN (99.9% SLA)
- **Features**: IPsec, dynamic routing, multiple tunnels
- **Bandwidth**: Up to 3 Gbps per tunnel

#### Cloud Interconnect
- **Types**: Dedicated (10/100 Gbps), Partner (50 Mbps - 50 Gbps)
- **Use Cases**: Hybrid cloud, large data transfers
- **SLA**: 99.9% - 99.99% depending on configuration

### Security Services

#### Identity and Access Management (IAM)
- **Components**: Members, roles, policies
- **Role Types**: Primitive (owner/editor/viewer), predefined, custom
- **Features**: Conditions, policy inheritance, deny policies
- **Service Accounts**: Machine identities, workload identity

#### Cloud Key Management Service (KMS)
- **Key Types**: Symmetric, asymmetric, MAC
- **Protection Levels**: Software, HSM, external
- **Features**: Automatic rotation, versioning, Cloud EKM
- **Integration**: Encryption at rest for all GCP services

#### Secret Manager
- **Description**: Centralized secret management
- **Features**: Versioning, rotation, replication, IAM integration
- **Use Cases**: API keys, passwords, certificates

#### VPC Service Controls
- **Description**: Perimeter security for GCP resources
- **Features**: Access levels, ingress/egress rules, dry run mode
- **Use Cases**: Data exfiltration protection, compliance

#### Security Command Center
- **Tiers**: Standard (free), Premium (paid)
- **Features**: Asset discovery, vulnerability scanning, threat detection
- **Integration**: Event Threat Detection, Container Threat Detection

#### Binary Authorization
- **Description**: Deploy-time security for containers
- **Features**: Attestations, policy enforcement, vulnerability scanning integration
- **Use Cases**: GKE security, supply chain security

### Management & Operations

#### Cloud Monitoring
- **Metrics**: System, application, custom metrics
- **Features**: Dashboards, alerting, uptime checks, SLOs
- **Integration**: All GCP services
- **Retention**: 6 weeks (metrics), 400 days (logs-based metrics)

#### Cloud Logging
- **Features**: Real-time log ingestion, log sinks, exclusions, sampling
- **Log Types**: Audit logs, platform logs, application logs
- **Retention**: 30 days default, customizable with sinks
- **Query**: Advanced filters, SQL-like syntax

#### Cloud Trace
- **Description**: Distributed tracing
- **Features**: Latency analysis, automatic tracing for App Engine/Cloud Run
- **Integration**: OpenTelemetry, Zipkin
- **Retention**: 30 days

#### Cloud Profiler
- **Description**: Continuous production profiling
- **Types**: CPU, heap, wall time, contention
- **Languages**: Java, Go, Python, Node.js, .NET
- **Overhead**: < 5% performance impact

#### Error Reporting
- **Features**: Automatic error grouping, notifications, stack trace analysis
- **Integration**: All GCP compute services
- **Languages**: All major languages

### Developer Tools

#### Cloud Build
- **Description**: Serverless CI/CD platform
- **Features**: Build triggers, Docker/Kaniko builds, custom builders
- **Integration**: GitHub, Bitbucket, Cloud Source Repositories
- **Pricing**: 120 build-minutes/day free, then $0.003/build-minute

#### Artifact Registry
- **Formats**: Docker, Maven, npm, Python, Apt, Yum
- **Features**: Vulnerability scanning, IAM integration, regional/multi-regional
- **Use Cases**: Container images, language packages

#### Cloud Source Repositories
- **Description**: Private Git repositories
- **Features**: Cloud Build integration, Cloud Debugger integration
- **Pricing**: Free for up to 5 users, 50 GB storage

#### Cloud Deploy
- **Description**: Managed continuous delivery
- **Features**: Delivery pipelines, progressive deployment, approval gates
- **Integration**: GKE, Cloud Run
- **Pricing**: Per release, per target

### Migration Services

#### Database Migration Service
- **Sources**: MySQL, PostgreSQL, Oracle, SQL Server
- **Targets**: Cloud SQL, AlloyDB
- **Features**: Minimal downtime, continuous replication

#### Storage Transfer Service
- **Sources**: AWS S3, Azure Blob, HTTP/HTTPS, Cloud Storage
- **Target**: Cloud Storage
- **Features**: Scheduled transfers, bandwidth control

#### Transfer Appliance
- **Description**: Physical device for offline data transfer
- **Capacity**: 40 TB, 300 TB
- **Use Cases**: Large-scale migrations, limited bandwidth

#### Migrate for Compute Engine
- **Description**: VM migration to GCP
- **Sources**: VMware, AWS, Azure, physical servers
- **Features**: Test clones, minimal downtime

### Hybrid & Multi-Cloud

#### Anthos
- **Description**: Application modernization platform
- **Components**: GKE Enterprise, Config Management, Service Mesh
- **Deployment**: GCP, on-premises, AWS, Azure
- **Use Cases**: Hybrid cloud, multi-cloud, application modernization

### Industry Solutions

#### Healthcare & Life Sciences
- Cloud Healthcare API, DICOM, FHIR, HL7v2
- HIPAA compliance, PHI protection

#### Financial Services
- Cloud Spanner, KMS, VPC Service Controls
- PCI DSS compliance

#### Retail
- Recommendations AI, Vision Product Search
- Inventory management, personalization

#### Media & Entertainment
- Transcoder API, Video Intelligence API
- Content delivery, live streaming

## Service Selection Matrix

| Requirement | Recommended Service |
|------------|-------------------|
| Relational database (regional) | Cloud SQL |
| Relational database (global) | Cloud Spanner |
| NoSQL document database | Firestore |
| Wide-column NoSQL | Bigtable |
| Object storage | Cloud Storage |
| File storage (NFS) | Filestore |
| Data warehouse | BigQuery |
| Real-time messaging | Pub/Sub |
| Batch processing | Dataflow, Dataproc |
| Serverless containers | Cloud Run |
| Kubernetes | GKE |
| Virtual machines | Compute Engine |
| Event-driven functions | Cloud Functions |
| CDN | Cloud CDN |
| Load balancing | Cloud Load Balancing |
| Secret management | Secret Manager |
| Encryption keys | Cloud KMS |
| CI/CD | Cloud Build, Cloud Deploy |
| Container registry | Artifact Registry |
| Monitoring | Cloud Monitoring |
| Logging | Cloud Logging |
| Tracing | Cloud Trace |

## Regional Availability

Services are available in 30+ regions globally across Americas, Europe, Asia Pacific, and Middle East.

**Multi-Regional Resources**:
- Cloud Storage (multi-region buckets)
- BigQuery (US, EU)
- Cloud Spanner (multi-region configurations)
- Cloud KMS (global)

**Global Resources**:
- Global HTTP(S) Load Balancing
- Cloud CDN
- Cloud DNS
- IAM

Check [Google Cloud Locations](https://cloud.google.com/about/locations) for current service availability.
