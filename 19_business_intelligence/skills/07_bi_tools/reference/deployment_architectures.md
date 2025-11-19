# BI Platform Deployment Architectures

## Deployment Models Overview

### Cloud vs On-Premises vs Hybrid

| Model | Pros | Cons | Best For |
|-------|------|------|----------|
| **Cloud SaaS** | Easy setup, auto-scaling, managed updates | Vendor lock-in, less control | Most organizations, rapid deployment |
| **On-Premises** | Full control, data sovereignty, customization | High maintenance, CapEx investment | Regulated industries, data residency requirements |
| **Hybrid** | Flexibility, gradual migration | Complex management, integration challenges | Large enterprises, mixed requirements |

## Tableau Architecture

### Tableau Server (On-Premises)

#### Single-Server Architecture
```
┌─────────────────────────────────────────┐
│        Tableau Server (Single Node)     │
├─────────────────────────────────────────┤
│  Application Server                     │
│  ├─ VizQL Server (visualization)        │
│  ├─ Application Server (web app)        │
│  ├─ Data Server (extract queries)       │
│  ├─ Backgrounder (extract refreshes)    │
│  ├─ Repository (PostgreSQL metadata)    │
│  └─ Gateway (Apache/IIS proxy)          │
├─────────────────────────────────────────┤
│  File Store (extracts, workbooks)       │
└─────────────────────────────────────────┘
```

**Suitable for:**
- < 100 users
- Development/test environments
- Departments

#### Multi-Node High Availability Architecture
```
                    Load Balancer
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Node 1          Node 2          Node 3
    ├─ VizQL        ├─ VizQL        ├─ VizQL
    ├─ App Server   ├─ App Server   ├─ App Server
    ├─ Data Server  ├─ Data Server  ├─ Data Server
    └─ Backgrounder └─ Backgrounder └─ Backgrounder
         │               │               │
         └───────────────┼───────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
         Repository          File Store
      (Active/Passive)    (Shared/NFS)
```

**Suitable for:**
- 100-1,000+ users
- Mission-critical deployments
- High availability requirements

#### Installation Script (Linux)
```bash
#!/bin/bash
# Tableau Server installation on Ubuntu

# Prerequisites
sudo apt-get update
sudo apt-get install -y gdebi-core

# Download Tableau Server
wget https://downloads.tableau.com/esdalt/2024.1.0/tableau-server-2024-1-0_amd64.deb

# Install
sudo gdebi -n tableau-server-2024-1-0_amd64.deb

# Initialize TSM
sudo /opt/tableau/tableau_server/packages/scripts.*/initialize-tsm \
  --accepteula \
  -a "tableau-admin"

# Activate license
tsm licenses activate -k <license-key>

# Register
tsm register --template > /tmp/registration.json
# Edit registration.json with company details
tsm register --file /tmp/registration.json

# Configure identity store
tsm configuration set -k wgserver.domain.username -v "DOMAIN\\tableauservice"
tsm configuration set -k wgserver.domain.password -v "password"

# Configure repository
tsm configuration set -k pgsql.adminpassword -v "strong-password"
tsm configuration set -k pgsql.port -v "8060"

# Apply configuration
tsm pending-changes apply

# Initialize and start
tsm initialize --start-server --request-timeout 1800

# Create admin user
tabcmd initialuser --server localhost --username "admin" --password "admin-password"
```

### Tableau Cloud (SaaS)
```
User Browser
     │
     ▼
Tableau Cloud (Managed by Tableau)
     │
     ├─ Regional Data Center (US/EU/APAC)
     │   ├─ Multi-tenant Infrastructure
     │   ├─ Automatic Scaling
     │   ├─ Managed Backups
     │   └─ 99.9% SLA
     │
     ├─ Data Connections
     │   ├─ Direct: Cloud databases
     │   └─ Bridge: On-premises data sources
     │
     └─ Authentication
         ├─ SAML/SSO
         └─ Multi-factor Auth
```

**Tableau Bridge for Hybrid**
```powershell
# Install Tableau Bridge on-premises
# Connect to on-prem data sources
# Relay to Tableau Cloud

# Bridge configuration
bridge.exe -c config.json

# Config.json
{
  "server": "https://10ax.online.tableau.com",
  "site": "your-site",
  "username": "bridge-service-account",
  "token": "personal-access-token"
}
```

## Power BI Architecture

### Power BI Service (Cloud)
```
                Power BI Service (Azure)
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
Workspaces         Premium Capacity      Shared Capacity
(Tenants)          (Dedicated)           (Multi-tenant)
    │                    │                    │
    ├─ Reports           ├─ P1/P2/P3          ├─ Pro/PPU
    ├─ Dashboards        ├─ Dedicated VMs     ├─ Shared Resources
    ├─ Datasets          ├─ Guaranteed        └─ Best Effort
    └─ Dataflows         │   Performance
                         └─ AutoScale

        Authentication: Azure AD
        Data: Azure Data Lake, SQL Database
        Compute: Azure VMs
        CDN: Azure CDN (static content)
```

### Power BI Report Server (On-Premises)
```bash
# Installation on Windows Server

# 1. Download Power BI Report Server
# 2. Run installer: PowerBIReportServer.exe

# 3. Configure SQL Server for catalog database
# Connection string: Server=sql-server;Database=ReportServer

# 4. Configure scale-out (multiple instances)
# All instances connect to same ReportServer database

# 5. Service account configuration
# Use domain account for PBIRS service
```

**Architecture:**
```
            Load Balancer (Optional)
                    │
        ┌───────────┴───────────┐
        │                       │
   Instance 1             Instance 2
        │                       │
        └───────────┬───────────┘
                    │
        Report Server Database (SQL Server)
                    │
                    ├─ Report Catalog
                    ├─ Execution Log
                    └─ Security Data
```

### Gateway Architecture (Hybrid)
```
Cloud: Power BI Service
    │
    │ (HTTPS Outbound)
    ├─ On-Premises Data Gateway
    │      │
    │      ├─ Gateway Service
    │      ├─ Connection Pooling
    │      └─ Query Routing
    │
    └─→ On-Premises Data Sources
         ├─ SQL Server
         ├─ Oracle
         ├─ File Shares
         └─ SAP
```

**Gateway Setup (PowerShell):**
```powershell
# Install On-Premises Data Gateway
# Download from: https://aka.ms/opdg

# Configure gateway
$gatewayName = "Corporate-Gateway"
$recoveryKey = "your-recovery-key-32-chars-long"

# Install silently
Start-Process -FilePath "GatewayInstaller.exe" -ArgumentList "/quiet /norestart" -Wait

# Configure with PowerShell module
Install-Module -Name DataGateway

# Register gateway
Add-DataGatewayCluster -GatewayName $gatewayName -RecoveryKey $recoveryKey -Region "eastus"

# Add data source
Add-DataGatewayClusterDataSource -GatewayClusterName $gatewayName `
  -DataSourceName "SQL-Prod" `
  -DataSourceType "SQL" `
  -ConnectionDetails '{"server":"sql-prod.company.local","database":"Sales"}' `
  -CredentialType "Windows" `
  -Username "DOMAIN\svc-gateway" `
  -Password $securePassword
```

## Looker Architecture

### Google Cloud Looker (SaaS)
```
        Looker Instance (GCP)
              │
    ┌─────────┴─────────┐
    │                   │
Application         Database
    │                   │
    ├─ Web UI           ├─ Internal DB (MySQL)
    ├─ Scheduler        │   ├─ User metadata
    ├─ Renderer         │   ├─ LookML models
    ├─ API Server       │   └─ Query cache
    └─ PDT Builder      │
                        └─ Customer Databases
                            ├─ BigQuery
                            ├─ Snowflake
                            ├─ Redshift
                            └─ Others (60+)
```

### Clustered Deployment
```
                Load Balancer
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   Node 1        Node 2        Node 3
   (Web/API)     (Web/API)     (Web/API)
        │             │             │
        └─────────────┼─────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
    Shared MySQL         Shared File Store
    (Metadata)           (PDTs, Images)
            │
            └─→ Customer Data Warehouses
```

### LookML Deployment Pipeline
```bash
# Git-based LookML development workflow

# 1. Development
git checkout -b feature/new-dashboard
# Make LookML changes
git add .
git commit -m "Add revenue dashboard"
git push origin feature/new-dashboard

# 2. Code Review (Pull Request)
# Review in Looker IDE or GitHub
# Validate LookML
# Run tests

# 3. Merge to master
git checkout master
git merge feature/new-dashboard

# 4. Deploy to production (in Looker)
# Project → Deploy to Production
# Or API:
curl -X POST "https://instance.looker.com/api/4.0/projects/my_project/deploy_to_production" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 5. Automated testing (optional)
# Use Looker API to validate
python validate_lookml.py --project my_project
```

## Qlik Sense Architecture

### Qlik Sense Enterprise (On-Premises)
```
                    Central Node
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Proxy Node      Engine Node     Scheduler Node
        │                │                │
    ├─ Qlik Proxy    ├─ QIX Engine  ├─ Repository
    ├─ Load          ├─ In-Memory   ├─ Scheduler
    │   Balancing    │   Processing  └─ Job Manager
    └─ Auth          └─ Apps/Data
        │
  PostgreSQL Repository Database
        │
        ├─ App metadata
        ├─ User data
        ├─ Security rules
        └─ Task definitions

  Shared File Persistence
        │
        ├─ .qvf files (apps)
        ├─ .qvd files (data)
        └─ Logs
```

### Multi-Node Installation
```powershell
# Central Node installation
# 1. Install Qlik Sense
.\Qlik_Sense_setup.exe

# 2. Configure shared persistence
# Create file share: \\fileserver\QlikShare
# Set permissions: Full control for service account

# 3. Join additional nodes
# On new server, install Qlik Sense
# During installation, select "Join existing site"
# Provide: Central node hostname, shared persistence path

# 4. Assign node roles
# QMC → Nodes → Select node → Edit
# Assign service roles:
# - Engine (data processing)
# - Proxy (user access)
# - Scheduler (reload tasks)
# - Printing (export PDFs)
```

### Qlik Sense SaaS (Cloud)
```
Qlik Cloud Platform
    │
    ├─ Tenant (company.region.qlikcloud.com)
    │   ├─ Multi-cloud support (AWS/Azure/GCP)
    │   ├─ Regional deployment
    │   └─ Auto-scaling
    │
    ├─ Data Integration
    │   ├─ Qlik Data Gateway (hybrid)
    │   ├─ Cloud data connectors
    │   └─ Qlik DataMarket
    │
    └─ Governance
        ├─ Spaces (collaborative)
        ├─ Managed spaces (controlled)
        └─ Personal spaces
```

## Apache Superset Architecture

### Standalone Deployment
```dockerfile
# Docker Compose for Superset
version: '3.7'

services:
  superset:
    image: apache/superset:latest
    container_name: superset
    environment:
      - SUPERSET_SECRET_KEY=your-secret-key
      - SUPERSET_ENV=production
    ports:
      - "8088:8088"
    volumes:
      - ./superset_config.py:/app/pythonpath/superset_config.py
      - superset_home:/app/superset_home
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:13
    container_name: superset-postgres
    environment:
      POSTGRES_DB: superset
      POSTGRES_USER: superset
      POSTGRES_PASSWORD: superset
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    container_name: superset-redis

volumes:
  superset_home:
  postgres_data:
```

### Production Kubernetes Deployment
```yaml
# superset-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: superset
  template:
    metadata:
      labels:
        app: superset
    spec:
      containers:
      - name: superset
        image: apache/superset:2.0.0
        ports:
        - containerPort: 8088
        env:
        - name: SUPERSET_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: superset-secrets
              key: secret-key
        - name: SQLALCHEMY_DATABASE_URI
          valueFrom:
            secretKeyRef:
              name: superset-secrets
              key: database-uri
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8088
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8088
          initialDelaySeconds: 30
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: superset-service
spec:
  type: LoadBalancer
  selector:
    app: superset
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8088
```

### Celery Workers for Async Queries
```yaml
# celery-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: superset-worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: superset-worker
  template:
    metadata:
      labels:
        app: superset-worker
    spec:
      containers:
      - name: worker
        image: apache/superset:2.0.0
        command: ["celery", "--app=superset.tasks.celery_app:app", "worker"]
        env:
        - name: SUPERSET_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: superset-secrets
              key: secret-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

## High Availability Patterns

### Active-Active (Horizontal Scaling)
```
            Load Balancer (L7)
                   │
    ┌──────────────┼──────────────┐
    │              │              │
Instance 1    Instance 2    Instance 3
    │              │              │
    └──────────────┴──────────────┘
                   │
        Shared State (Redis/DB)
```

**Pros:** True HA, load distribution, linear scaling
**Cons:** Requires sticky sessions for some platforms
**Platforms:** Tableau Server, Looker, Superset

### Active-Passive (Failover)
```
    Primary Instance (Active)
            │
            ├─ Health Check
            │
    ┌───────┴────────┐
    │                │
    ▼                ▼
 Healthy         Unhealthy
    │                │
    │                └─→ Failover to Secondary
    │                        │
 Continue                Secondary (Passive)
                            │
                      Becomes Active
```

**Pros:** Simpler configuration, cost-effective
**Cons:** Unused capacity, failover delay
**Platforms:** Qlik Sense, Power BI Report Server

## Network Architecture

### DMZ Deployment (Secure)
```
Internet
    │
    └─→ Firewall 1
         │
         ├─ DMZ (Perimeter Network)
         │   └─ Reverse Proxy / Load Balancer
         │       │
         │       └─→ Firewall 2
         │             │
         │             ├─ Internal Network
         │             │   ├─ BI Application Servers
         │             │   └─ Web Servers
         │             │
         │             └─→ Firewall 3
         │                   │
         │                   └─ Database Network
         │                       ├─ Metadata DB
         │                       └─ Data Warehouses
```

### Zero-Trust Architecture
```
User → Identity Provider (OAuth/SAML)
         │
         ├─ Authentication
         ├─ Authorization
         └─ MFA
              │
              └─→ BI Platform (least privilege)
                      │
                      ├─ Service Account per Data Source
                      ├─ Row-Level Security
                      ├─ Encrypted Connections (TLS)
                      └─ Audit Logging
```

## Disaster Recovery

### RPO/RTO Targets
| Tier | RPO | RTO | Strategy |
|------|-----|-----|----------|
| Tier 1 (Critical) | < 1 hour | < 4 hours | Active-Active, Real-time replication |
| Tier 2 (Important) | < 24 hours | < 8 hours | Active-Passive, Daily backups |
| Tier 3 (Standard) | < 72 hours | < 24 hours | Backups only |

### Backup Strategy
```bash
# Tableau Server backup
tsm maintenance backup -f backup.tsbak -d

# Power BI Report Server backup
# Backup SQL Server ReportServer database
sqlcmd -Q "BACKUP DATABASE ReportServer TO DISK = 'C:\Backups\ReportServer.bak'"

# Looker backup (LookML)
# Git repository = automatic version control
git clone git@github.com:company/lookml-project.git

# Qlik backup
# Backup shared persistence folder
robocopy "\\server\QlikShare" "\\backup\QlikShare" /MIR

# Superset backup
# Backup PostgreSQL metadata database
pg_dump superset > superset_backup.sql
```

## Monitoring & Observability

### Key Metrics
```python
# Example monitoring configuration
monitoring_metrics = {
    'availability': ['uptime', 'http_status', 'service_health'],
    'performance': ['response_time', 'query_duration', 'throughput'],
    'capacity': ['cpu_usage', 'memory_usage', 'disk_usage', 'concurrent_users'],
    'errors': ['error_rate', 'failed_queries', 'timeout_count']
}

# Alerting thresholds
alerts = {
    'response_time_p95': {'threshold': 5000, 'severity': 'warning'},
    'error_rate': {'threshold': 0.05, 'severity': 'critical'},
    'cpu_usage': {'threshold': 80, 'severity': 'warning'},
    'disk_usage': {'threshold': 90, 'severity': 'critical'}
}
```

## Scaling Guidelines

| Users | Architecture | Specs |
|-------|--------------|-------|
| < 100 | Single server | 8 CPU, 32GB RAM, 500GB SSD |
| 100-500 | Multi-node (3-5) | 16 CPU, 64GB RAM per node |
| 500-2,000 | Clustered (5-10) | 32 CPU, 128GB RAM per node |
| 2,000+ | Enterprise cluster | 64+ CPU, 256GB+ RAM, distributed architecture |
