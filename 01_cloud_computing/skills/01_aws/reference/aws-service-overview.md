# AWS Service Overview Reference

## Compute Services

### Amazon EC2 (Elastic Compute Cloud)
**Purpose**: Virtual servers in the cloud
**Use Cases**:
- Web application hosting
- Batch processing
- Enterprise applications
- Game servers
**Pricing Models**: On-Demand, Reserved, Spot, Dedicated Hosts
**Key Features**: Auto Scaling, Placement Groups, Elastic IPs, Instance Store
**SLA**: 99.99% for Multi-AZ deployments

### AWS Lambda
**Purpose**: Serverless compute service
**Use Cases**:
- Event-driven processing
- Backend APIs
- Data transformation
- Scheduled tasks
**Pricing**: Pay per request and compute time (GB-seconds)
**Limits**: 15-minute max execution, 10GB memory, 512MB-10GB ephemeral storage
**Key Features**: Automatic scaling, built-in fault tolerance, integration with 200+ AWS services

### Amazon ECS (Elastic Container Service)
**Purpose**: Container orchestration service
**Use Cases**: Microservices, batch processing, ML model hosting
**Launch Types**: EC2 (self-managed) or Fargate (serverless)
**Key Features**: Service discovery, load balancing, auto scaling, blue/green deployments

### Amazon EKS (Elastic Kubernetes Service)
**Purpose**: Managed Kubernetes service
**Use Cases**: Complex microservices, multi-cloud portability, existing K8s workloads
**Key Features**: Multi-AZ control plane, automatic version upgrades, EKS Anywhere
**Integration**: AWS Load Balancer Controller, EBS CSI Driver, IAM for RBAC

### AWS Fargate
**Purpose**: Serverless compute for containers
**Use Cases**: Run containers without managing servers
**Pricing**: Pay per vCPU and memory per second
**Key Features**: Integrated with ECS and EKS, automatic scaling, built-in security

## Storage Services

### Amazon S3 (Simple Storage Service)
**Purpose**: Object storage service
**Use Cases**: Data lakes, backup/archive, static website hosting, media storage
**Storage Classes**:
- S3 Standard: Frequent access
- S3 Intelligent-Tiering: Unknown access patterns
- S3 Standard-IA: Infrequent access
- S3 One Zone-IA: Infrequent, non-critical
- S3 Glacier Instant Retrieval: Archive with instant access
- S3 Glacier Flexible Retrieval: Archive, minutes-hours retrieval
- S3 Glacier Deep Archive: Long-term archive, 12-hour retrieval
**Durability**: 99.999999999% (11 nines)
**Availability**: 99.99% (Standard), 99.9% (IA), 99.5% (One Zone-IA)

### Amazon EBS (Elastic Block Store)
**Purpose**: Block storage for EC2 instances
**Volume Types**:
- gp3/gp2: General Purpose SSD
- io2/io1: Provisioned IOPS SSD
- st1: Throughput Optimized HDD
- sc1: Cold HDD
**Key Features**: Snapshots, encryption, multi-attach (io2), elastic volumes
**Performance**: Up to 256,000 IOPS, 4,000 MB/s throughput

### Amazon EFS (Elastic File System)
**Purpose**: Managed NFS file system
**Use Cases**: Content management, web serving, shared file storage, container storage
**Performance Modes**: General Purpose, Max I/O
**Throughput Modes**: Bursting, Provisioned, Elastic
**Storage Classes**: Standard, Infrequent Access
**Key Features**: Multi-AZ, automatic scaling, POSIX-compliant

### AWS Storage Gateway
**Purpose**: Hybrid cloud storage integration
**Types**:
- File Gateway: NFS/SMB access to S3
- Volume Gateway: iSCSI block storage
- Tape Gateway: Virtual tape library
**Use Cases**: Cloud backup, disaster recovery, tiered storage

## Database Services

### Amazon RDS (Relational Database Service)
**Engines**: Aurora, PostgreSQL, MySQL, MariaDB, Oracle, SQL Server
**Key Features**: Automated backups, Multi-AZ, read replicas, automated patching
**Storage**: General Purpose (gp3), Provisioned IOPS (io1)
**Max Storage**: 64 TiB (128 TiB for Aurora)

### Amazon Aurora
**Purpose**: MySQL and PostgreSQL-compatible relational database
**Performance**: 5x MySQL, 3x PostgreSQL throughput
**Features**: Up to 15 read replicas, global database, serverless v2, backtrack
**Storage**: Distributed, self-healing, auto-scaling up to 128 TiB
**High Availability**: 6-way replication across 3 AZs

### Amazon DynamoDB
**Purpose**: Managed NoSQL database
**Use Cases**: Mobile apps, gaming, IoT, serverless applications
**Capacity Modes**: On-Demand, Provisioned
**Key Features**: Single-digit ms latency, auto scaling, global tables, streams, TTL
**Consistency**: Eventually consistent or strongly consistent reads
**Max Item Size**: 400 KB

### Amazon ElastiCache
**Purpose**: In-memory caching service
**Engines**: Redis, Memcached
**Use Cases**: Session storage, leaderboards, real-time analytics, caching
**Redis Features**: Persistence, replication, Multi-AZ, backup/restore, cluster mode
**Memcached Features**: Multithreading, simple scaling

### Amazon Redshift
**Purpose**: Data warehouse service
**Use Cases**: Business intelligence, analytics, historical data analysis
**Node Types**: RA3 (managed storage), DC2 (compute-intensive)
**Key Features**: Columnar storage, parallel processing, Redshift Spectrum, materialized views
**Performance**: PB-scale queries, result caching, concurrency scaling

## Networking Services

### Amazon VPC (Virtual Private Cloud)
**Purpose**: Isolated network environment
**Components**: Subnets, route tables, IGW, NAT Gateway, VPC peering, Transit Gateway
**IP Addressing**: RFC 1918 private ranges, Elastic IPs
**Key Features**: Flow logs, network ACLs, security groups, VPC endpoints
**CIDR**: /16 to /28 netmasks

### Elastic Load Balancing
**Types**:
- Application Load Balancer: HTTP/HTTPS, Layer 7
- Network Load Balancer: TCP/UDP/TLS, Layer 4, ultra-low latency
- Gateway Load Balancer: Layer 3, third-party appliances
- Classic Load Balancer: Legacy
**Features**: Health checks, SSL termination, sticky sessions, connection draining

### Amazon Route 53
**Purpose**: DNS web service
**Routing Policies**: Simple, weighted, latency-based, failover, geolocation, geoproximity, multivalue
**Health Checks**: Endpoint, CloudWatch alarm, calculated
**Key Features**: Domain registration, DNSSEC, traffic flow, private hosted zones

### Amazon CloudFront
**Purpose**: Content Delivery Network (CDN)
**Use Cases**: Static/dynamic content acceleration, streaming, API acceleration
**Edge Locations**: 400+ globally
**Key Features**: Lambda@Edge, CloudFront Functions, origin failover, field-level encryption
**Protocols**: HTTP/2, HTTP/3, WebSockets

### AWS Direct Connect
**Purpose**: Dedicated network connection to AWS
**Connection Speeds**: 50 Mbps to 100 Gbps
**Use Cases**: Hybrid cloud, large data transfers, consistent network performance
**Components**: Virtual interfaces (private, public, transit)

## Security & Identity

### AWS IAM (Identity and Access Management)
**Components**: Users, groups, roles, policies
**Policy Types**: Identity-based, resource-based, permissions boundaries, SCPs
**Authentication**: MFA, access keys, temporary credentials, IAM Identity Center
**Key Features**: Cross-account access, SAML/OIDC federation, policy simulator

### AWS KMS (Key Management Service)
**Purpose**: Managed encryption key service
**Key Types**: AWS managed, customer managed, AWS owned
**Key Specs**: Symmetric (AES-256), asymmetric (RSA, ECC)
**Key Features**: Automatic key rotation, audit logging, key policies, grants
**Integration**: Native integration with 100+ AWS services

### AWS Secrets Manager
**Purpose**: Manage secrets lifecycle
**Use Cases**: Database credentials, API keys, OAuth tokens
**Key Features**: Automatic rotation, fine-grained access control, encryption with KMS
**Pricing**: $0.40 per secret per month + $0.05 per 10,000 API calls

### AWS WAF (Web Application Firewall)
**Purpose**: Protect web applications from common exploits
**Use Cases**: SQL injection, XSS, DDoS protection, bot mitigation
**Rule Types**: Managed rules, custom rules, rate-based rules
**Integration**: CloudFront, ALB, API Gateway, AppSync

## Analytics & Data

### Amazon Athena
**Purpose**: Interactive query service for S3
**Query Language**: ANSI SQL
**Use Cases**: Log analysis, ad-hoc queries, data exploration
**Pricing**: $5 per TB scanned
**Features**: Federated queries, ACID transactions, time travel

### AWS Glue
**Purpose**: Serverless ETL service
**Components**: Data Catalog, Crawlers, ETL jobs, DataBrew
**Languages**: Python, Scala
**Use Cases**: Data preparation, schema discovery, data integration

### Amazon Kinesis
**Services**:
- Kinesis Data Streams: Real-time data streaming
- Kinesis Data Firehose: Load streams into data stores
- Kinesis Data Analytics: SQL/Flink on streaming data
**Use Cases**: Real-time analytics, log processing, IoT data ingestion

### Amazon EMR (Elastic MapReduce)
**Purpose**: Managed Hadoop framework
**Frameworks**: Spark, Hive, HBase, Presto, Flink, Hudi
**Use Cases**: Big data processing, ML, log analysis, data transformation

## Management & Governance

### AWS CloudFormation
**Purpose**: Infrastructure as Code
**Template Formats**: JSON, YAML
**Key Features**: Nested stacks, stack sets, drift detection, change sets
**Use Cases**: Repeatable deployments, disaster recovery, multi-region deployments

### AWS CloudWatch
**Purpose**: Monitoring and observability
**Components**: Metrics, Logs, Alarms, Dashboards, Insights, Synthetics
**Key Features**: Custom metrics, log analytics, anomaly detection, cross-account monitoring

### AWS CloudTrail
**Purpose**: API audit logging
**Use Cases**: Compliance, security analysis, troubleshooting, governance
**Key Features**: Multi-region logging, log file validation, integration with CloudWatch Logs

### AWS Systems Manager
**Components**: Parameter Store, Session Manager, Patch Manager, State Manager, Automation
**Use Cases**: Configuration management, secure access, patch compliance, automation
**Key Features**: No SSH keys needed, audit trail, hybrid environment support

### AWS Organizations
**Purpose**: Multi-account management
**Key Features**: Consolidated billing, SCPs, account creation automation, StackSets
**Organization Units**: Hierarchical account grouping
**Use Cases**: Account isolation, cost allocation, security boundaries

## Developer Tools

### AWS CodeCommit
**Purpose**: Git-based source control
**Features**: Unlimited repositories, encryption at rest, IAM integration

### AWS CodeBuild
**Purpose**: Fully managed build service
**Features**: Pre-configured environments, custom build images, local debugging

### AWS CodeDeploy
**Purpose**: Automated deployment service
**Targets**: EC2, Lambda, ECS, on-premises
**Deployment Types**: In-place, blue/green, canary, linear

### AWS CodePipeline
**Purpose**: Continuous delivery service
**Stages**: Source, build, test, deploy, approval
**Integration**: GitHub, GitLab, Bitbucket, Jenkins

## Application Integration

### Amazon SQS (Simple Queue Service)
**Types**: Standard (at-least-once, best effort ordering), FIFO (exactly-once, ordered)
**Message Size**: Up to 256 KB
**Retention**: 1 minute to 14 days
**Features**: Dead letter queues, visibility timeout, long polling, delay queues

### Amazon SNS (Simple Notification Service)
**Purpose**: Pub/sub messaging service
**Protocols**: HTTP/S, email, SMS, SQS, Lambda, mobile push
**Message Size**: Up to 256 KB
**Features**: Message filtering, FIFO topics, message archiving

### AWS Step Functions
**Purpose**: Serverless orchestration service
**Workflow Types**: Standard (long-running), Express (high-volume, short-duration)
**States**: Task, Choice, Parallel, Wait, Pass, Succeed, Fail
**Integration**: 220+ AWS services, SDK integrations

### Amazon EventBridge
**Purpose**: Event bus service
**Components**: Event buses, rules, targets
**Sources**: AWS services, custom applications, SaaS partners
**Features**: Schema registry, archive/replay, cross-account events

## AI/ML Services

### Amazon SageMaker
**Purpose**: Build, train, and deploy ML models
**Components**: Studio, Notebooks, Training, Inference, Pipelines
**Features**: Built-in algorithms, bring your own model, automatic model tuning

### Amazon Rekognition
**Purpose**: Image and video analysis
**Use Cases**: Face detection, object recognition, content moderation, celebrity recognition

### Amazon Comprehend
**Purpose**: Natural language processing
**Features**: Entity recognition, sentiment analysis, topic modeling, PII detection

### Amazon Lex
**Purpose**: Build conversational interfaces
**Use Cases**: Chatbots, virtual agents, IVR systems
**Integration**: AWS Connect, Lambda, mobile/web applications

This reference provides a comprehensive overview of core AWS services. Each service integrates with others to build complete cloud solutions following AWS best practices and the Well-Architected Framework.
