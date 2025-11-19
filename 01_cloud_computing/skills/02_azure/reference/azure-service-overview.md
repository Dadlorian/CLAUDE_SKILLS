# Azure Service Overview Reference

## Compute Services

### Virtual Machines
**Description**: Infrastructure as a Service (IaaS) offering for Windows and Linux VMs
**Use Cases**: Legacy apps, custom software, full OS control, lift-and-shift migrations
**Pricing Model**: Pay-per-hour based on VM size, can use reserved instances for discounts
**Key Features**: Multiple series (D, E, F, B), availability sets, scale sets, managed disks

### Azure Kubernetes Service (AKS)
**Description**: Managed Kubernetes container orchestration service
**Use Cases**: Microservices, containerized applications, cloud-native development
**Pricing Model**: Free control plane, pay for worker nodes (VMs)
**Key Features**: Auto-scaling, auto-upgrades, Azure Monitor integration, RBAC

### Azure Functions
**Description**: Serverless compute for event-driven applications
**Use Cases**: Event processing, scheduled tasks, API backends, data transformations
**Pricing Model**: Consumption (pay per execution), Premium (always-ready instances), Dedicated (App Service plan)
**Key Features**: Multiple language support, bindings and triggers, Durable Functions for workflows

### App Service
**Description**: Managed platform for web apps, mobile backends, and REST APIs
**Use Cases**: Web applications, RESTful APIs, mobile backends
**Pricing Model**: Tiered (Free, Shared, Basic, Standard, Premium, Isolated)
**Key Features**: Auto-scaling, deployment slots, custom domains, SSL certificates

### Container Instances
**Description**: Run containers without managing servers
**Use Cases**: Burst computing, batch jobs, isolated containers
**Pricing Model**: Per-second billing based on CPU/memory
**Key Features**: Fast startup, custom sizes, Windows and Linux containers

### Azure Batch
**Description**: Large-scale parallel and high-performance computing
**Use Cases**: Rendering, financial modeling, genomic sequencing
**Pricing Model**: Pay for underlying compute resources
**Key Features**: Auto-scaling, task scheduling, cloud-scale job orchestration

## Storage Services

### Blob Storage
**Description**: Object storage for unstructured data
**Use Cases**: Documents, images, videos, backups, data lakes
**Pricing Model**: Tiered (Hot, Cool, Archive), pay per GB stored and operations
**Key Features**: Lifecycle management, versioning, soft delete, immutability policies
**Performance Tiers**: Standard (HDD), Premium (SSD)

### Azure Files
**Description**: Fully managed file shares accessible via SMB and NFS
**Use Cases**: Shared application data, lift-and-shift scenarios, hybrid file sync
**Pricing Model**: Pay per GB stored and operations
**Key Features**: Azure File Sync, snapshot support, AD authentication
**Performance Tiers**: Standard, Premium

### Queue Storage
**Description**: Message queue service for reliable async messaging
**Use Cases**: Decoupling components, work queue patterns
**Pricing Model**: Pay per million operations
**Key Features**: At-least-once delivery, messages up to 64 KB, 7-day retention

### Table Storage
**Description**: NoSQL key-value store for structured data
**Use Cases**: Flexible schemas, web app user data, metadata
**Pricing Model**: Pay per GB stored and operations
**Key Features**: Schemaless design, OData queries, automatic indexing

### Disk Storage
**Description**: Persistent block storage for VMs
**Use Cases**: VM OS and data disks, database workloads
**Pricing Model**: Tiered (Ultra, Premium SSD, Standard SSD, Standard HDD)
**Key Features**: Managed disks, snapshots, encryption, shared disks

### Data Lake Storage Gen2
**Description**: Massively scalable data lake for big data analytics
**Use Cases**: Big data analytics, data warehousing, machine learning
**Pricing Model**: Similar to Blob Storage with hierarchical namespace
**Key Features**: Hadoop-compatible, fine-grained ACLs, atomic operations

## Database Services

### Azure SQL Database
**Description**: Fully managed relational database (SQL Server engine)
**Use Cases**: OLTP workloads, business applications, SaaS apps
**Pricing Model**: DTU-based or vCore-based, serverless option available
**Key Features**: Auto-tuning, threat detection, geo-replication, elastic pools
**Service Tiers**: Basic, Standard, Premium, Hyperscale

### Cosmos DB
**Description**: Globally distributed, multi-model NoSQL database
**Use Cases**: Globally distributed apps, low-latency access, flexible schemas
**Pricing Model**: Request Units (RU/s), serverless option available
**Key Features**: Five consistency levels, multi-region writes, automatic indexing
**APIs**: SQL (Core), MongoDB, Cassandra, Gremlin, Table

### Azure Database for PostgreSQL
**Description**: Managed PostgreSQL database service
**Use Cases**: Open-source database workloads, web/mobile apps
**Pricing Model**: vCore-based, flexible server model
**Key Features**: High availability, automated backups, read replicas
**Deployment Options**: Single Server, Flexible Server, Hyperscale (Citus)

### Azure Database for MySQL
**Description**: Managed MySQL database service
**Use Cases**: LAMP stack apps, WordPress, e-commerce
**Pricing Model**: vCore-based
**Key Features**: High availability, automated backups, point-in-time restore

### Azure Synapse Analytics
**Description**: Unified analytics platform combining data warehousing and big data
**Use Cases**: Enterprise data warehousing, big data analytics
**Pricing Model**: Dedicated SQL pools, serverless SQL, Spark pools
**Key Features**: Integration with Power BI, Azure ML, data flows

### Azure Cache for Redis
**Description**: In-memory data store based on Redis
**Use Cases**: Session state, caching, real-time analytics
**Pricing Model**: Tiered (Basic, Standard, Premium, Enterprise)
**Key Features**: Clustering, persistence, geo-replication

## Networking Services

### Virtual Network (VNet)
**Description**: Private network in Azure for resources
**Use Cases**: Network isolation, hybrid connectivity, multi-tier apps
**Pricing Model**: Free, pay for VPN Gateway, peering egress
**Key Features**: Subnets, service endpoints, private endpoints, peering

### Network Security Groups (NSG)
**Description**: Stateful packet filtering firewall
**Use Cases**: Network traffic control, security boundaries
**Pricing Model**: Free
**Key Features**: Inbound/outbound rules, service tags, application security groups

### Azure Firewall
**Description**: Managed cloud-based network security service
**Use Cases**: Centralized network protection, threat intelligence
**Pricing Model**: Per deployment hour + data processed
**Key Features**: FQDN filtering, threat intelligence, forced tunneling

### Application Gateway
**Description**: Layer 7 load balancer and application delivery controller
**Use Cases**: Web app load balancing, SSL termination, URL-based routing
**Pricing Model**: Per gateway hour + capacity units
**Key Features**: WAF, autoscaling, session affinity, multi-site hosting

### Load Balancer
**Description**: Layer 4 load balancer for high availability
**Use Cases**: Distributing traffic across VMs, TCP/UDP load balancing
**Pricing Model**: Standard has per-rule and data processing charges
**Key Features**: Health probes, outbound rules, HA ports
**SKUs**: Basic (free), Standard

### VPN Gateway
**Description**: Encrypted connection between Azure and on-premises
**Use Cases**: Hybrid cloud, site-to-site VPN, point-to-site VPN
**Pricing Model**: Per gateway hour based on SKU
**Key Features**: BGP support, active-active, ExpressRoute coexistence

### Azure Front Door
**Description**: Global application delivery network and CDN
**Use Cases**: Global load balancing, CDN, SSL offload
**Pricing Model**: Per routing rule + data transfer
**Key Features**: WAF, SSL offload, URL rewriting, caching

### Private Link/Private Endpoint
**Description**: Private connectivity to Azure PaaS services
**Use Cases**: Secure access to PaaS, eliminate public exposure
**Pricing Model**: Per endpoint hour + data processed
**Key Features**: No public IP required, cross-region support

### Traffic Manager
**Description**: DNS-based global traffic routing
**Use Cases**: Multi-region failover, performance routing
**Pricing Model**: Per million DNS queries
**Key Features**: Multiple routing methods, nested profiles, endpoint monitoring

## Identity and Security Services

### Azure Active Directory (Azure AD)
**Description**: Cloud-based identity and access management
**Use Cases**: SSO, user management, B2B/B2C scenarios
**Pricing Model**: Free, Premium P1, Premium P2
**Key Features**: MFA, Conditional Access, Identity Protection, Privileged Identity Management

### Key Vault
**Description**: Secrets, keys, and certificates management
**Use Cases**: Secure credential storage, encryption key management
**Pricing Model**: Per operation, premium tier for HSM
**Key Features**: HSM-backed keys, access policies, soft-delete, purge protection

### Azure Policy
**Description**: Governance and compliance enforcement
**Use Cases**: Resource compliance, cost controls, security standards
**Pricing Model**: Free for built-in policies
**Key Features**: Policy definitions, initiatives, remediation tasks

### Microsoft Defender for Cloud
**Description**: Cloud security posture management and threat protection
**Use Cases**: Security recommendations, threat detection
**Pricing Model**: Free tier for posture, paid for workload protection
**Key Features**: Secure score, regulatory compliance, JIT access

### Azure Sentinel
**Description**: Cloud-native SIEM and SOAR solution
**Use Cases**: Security monitoring, threat hunting, incident response
**Pricing Model**: Per GB ingested or commitment tiers
**Key Features**: AI-driven analytics, workbooks, playbooks, threat intelligence

## Monitoring and Management Services

### Azure Monitor
**Description**: Comprehensive monitoring solution for Azure and hybrid resources
**Use Cases**: Metrics and logs collection, alerting, autoscaling
**Pricing Model**: Per GB ingested, data retention
**Key Features**: Metrics, logs, alerts, dashboards, workbooks

### Log Analytics
**Description**: Log aggregation and analysis service
**Use Cases**: Centralized logging, KQL queries, security analytics
**Pricing Model**: Per GB ingested, data retention
**Key Features**: KQL query language, workspaces, saved queries

### Application Insights
**Description**: Application Performance Monitoring (APM) service
**Use Cases**: Performance monitoring, distributed tracing, usage analytics
**Pricing Model**: Per GB ingested
**Key Features**: Live metrics, failure analysis, dependency tracking, custom events

### Azure Advisor
**Description**: Personalized cloud consultant for best practices
**Use Cases**: Cost optimization, security, reliability recommendations
**Pricing Model**: Free
**Key Features**: Recommendations across five pillars, actionable insights

### Service Health
**Description**: Personalized view of Azure service health
**Use Cases**: Service issue awareness, planned maintenance tracking
**Pricing Model**: Free
**Key Features**: Service issues, health alerts, health history

## Integration Services

### Service Bus
**Description**: Enterprise messaging service with queues and topics
**Use Cases**: Decoupling applications, reliable messaging, pub/sub patterns
**Pricing Model**: Tiered (Basic, Standard, Premium)
**Key Features**: FIFO, sessions, duplicate detection, dead-letter queues

### Event Grid
**Description**: Event routing service for event-driven architectures
**Use Cases**: Reactive programming, serverless workflows, resource monitoring
**Pricing Model**: Per million operations
**Key Features**: Event filtering, multiple destinations, custom topics

### Event Hubs
**Description**: Big data streaming platform and event ingestion
**Use Cases**: Telemetry ingestion, log aggregation, real-time analytics
**Pricing Model**: Throughput units or processing units
**Key Features**: Capture to storage, Kafka protocol support, partitioning

### Logic Apps
**Description**: Workflow automation and integration service
**Use Cases**: Business process automation, SaaS integration, B2B integration
**Pricing Model**: Per action execution
**Key Features**: 400+ connectors, visual designer, enterprise integration pack

### API Management
**Description**: API gateway for publishing, securing, and managing APIs
**Use Cases**: API facade, legacy modernization, microservices gateway
**Pricing Model**: Tiered (Consumption, Developer, Basic, Standard, Premium)
**Key Features**: Policies, developer portal, analytics, throttling

## DevOps and Development Services

### Azure DevOps
**Description**: Complete DevOps toolchain for teams
**Use Cases**: CI/CD, agile planning, version control
**Pricing Model**: Free for 5 users, paid plans available
**Key Features**: Repos, Pipelines, Boards, Artifacts, Test Plans

### Azure Artifacts
**Description**: Package management for Maven, npm, NuGet, Python
**Use Cases**: Private package hosting, dependency management
**Pricing Model**: Free for 2 GB, paid for additional storage
**Key Features**: Universal packages, upstream sources

### Container Registry
**Description**: Private Docker and OCI registry
**Use Cases**: Container image storage, CI/CD integration
**Pricing Model**: Tiered (Basic, Standard, Premium)
**Key Features**: Geo-replication, webhooks, content trust, vulnerability scanning

## AI and Machine Learning Services

### Azure Machine Learning
**Description**: End-to-end machine learning platform
**Use Cases**: Model training, deployment, MLOps
**Pricing Model**: Compute-based, per compute hour
**Key Features**: AutoML, designer, notebooks, model registry

### Cognitive Services
**Description**: Pre-built AI models and APIs
**Use Cases**: Vision, speech, language, decision making
**Pricing Model**: Per transaction or tiered pricing
**Key Features**: Computer Vision, Speech, Language, Decision APIs

### Azure Bot Service
**Description**: Managed bot development platform
**Use Cases**: Chatbots, conversational AI
**Pricing Model**: Free tier, standard per message
**Key Features**: Bot Framework SDK, channels, QnA Maker integration

## Service Comparison Matrix

| Service Category | Entry-Level | Mid-Tier | Enterprise |
|-----------------|-------------|----------|------------|
| Compute | Container Instances | App Service | AKS |
| Storage | Blob Standard | Blob Premium | Data Lake Gen2 |
| Database | Azure SQL Basic | Azure SQL Standard | Cosmos DB |
| Networking | NSG | Application Gateway | Azure Firewall |
| Identity | Azure AD Free | Azure AD Premium P1 | Azure AD Premium P2 |
| Messaging | Queue Storage | Service Bus Standard | Service Bus Premium |

## Regional Availability

### Global Services
- Azure AD
- Traffic Manager
- Azure Front Door
- Azure CDN

### Regional Services
Most Azure services are deployed regionally, including:
- Virtual Machines
- Storage Accounts
- Databases
- Networking components

Check https://azure.microsoft.com/global-infrastructure/services/ for specific service availability by region.

## Service Limits and Quotas

Common default limits:
- VMs per subscription per region: 25,000
- Storage accounts per subscription: 250
- VNets per subscription: 1,000
- Public IP addresses: 1,000
- Network Security Groups: 5,000

Most limits can be increased by submitting a support request.

## Service SLAs

- Virtual Machines: 99.9% (single VM with Premium SSD) to 99.99% (availability sets/zones)
- Azure SQL Database: 99.99% (Business Critical tier)
- Cosmos DB: 99.999% (multi-region with multi-region writes)
- Storage: 99.9% to 99.99% depending on redundancy
- AKS: 99.95% with Availability Zones
- App Service: 99.95%

Check https://azure.microsoft.com/support/legal/sla/ for complete SLA details.
