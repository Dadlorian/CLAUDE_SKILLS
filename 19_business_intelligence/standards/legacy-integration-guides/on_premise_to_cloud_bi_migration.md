# On-Premise to Cloud BI Migration Guide
## Tableau Server to Tableau Cloud & Power BI On-Premise to Power BI Service

**Version:** 1.0
**Last Updated:** 2025-11-19
**Status:** Production-Ready

---

## Executive Summary

This guide provides comprehensive strategies for migrating on-premise Business Intelligence platforms to cloud-native SaaS solutions. The focus is on two primary migration paths: Tableau Server to Tableau Cloud and Power BI Report Server to Power BI Service. These migrations require careful planning around network architecture, data connectivity, security, governance, and user adoption.

### Key Benefits of Cloud BI Migration

- **Reduced Infrastructure Costs:** Eliminate server maintenance, hardware refresh cycles, and data center costs
- **Automatic Updates:** Always on the latest version without manual upgrades
- **Scalability:** Auto-scaling to handle peak usage without over-provisioning
- **Accessibility:** Access from anywhere, enhanced mobile experience
- **Collaboration:** Built-in sharing, commenting, and collaboration features
- **Security:** Enterprise-grade security with SOC 2, ISO 27001 certifications
- **Faster Time to Value:** Rapid deployment without infrastructure setup

### Migration Timeline Overview

- **Assessment & Planning:** 4-8 weeks
- **Proof of Concept:** 4-6 weeks
- **Pilot Migration:** 8-12 weeks
- **Full Production Migration:** 3-9 months
- **Optimization & Decommission:** 1-3 months

---

## Table of Contents

1. [Cloud Platform Comparison](#cloud-platform-comparison)
2. [Tableau Server to Tableau Cloud Migration](#tableau-server-to-tableau-cloud-migration)
3. [Power BI Report Server to Power BI Service](#power-bi-report-server-to-power-bi-service)
4. [Data Connectivity Strategies](#data-connectivity-strategies)
5. [Security & Governance](#security-governance)
6. [Performance Optimization](#performance-optimization)
7. [Cost Management](#cost-management)
8. [Migration Checklists](#migration-checklists)

---

## Cloud Platform Comparison

### 1.1 On-Premise vs Cloud Feature Comparison

#### Tableau Server vs Tableau Cloud

| Capability | Tableau Server (On-Prem) | Tableau Cloud (SaaS) | Migration Consideration |
|------------|--------------------------|----------------------|-------------------------|
| **Deployment** | Self-hosted, customer-managed | Fully managed by Tableau | No infrastructure management needed |
| **Scaling** | Manual hardware scaling | Auto-scaling | Better handling of peak loads |
| **Updates** | Manual (quarterly releases) | Automatic (weekly updates) | Always current with latest features |
| **Data Connections** | Direct connections, no limits | Requires Tableau Bridge or data extracts | Plan for Bridge deployment |
| **Custom Extensions** | Full support | Limited (Tableau-approved only) | Review custom viz extensions |
| **Single Sign-On** | SAML, OpenID, Kerberos | SAML, OpenID (no Kerberos) | Kerberos environments need planning |
| **Row-Level Security** | Full support | Full support | Direct migration |
| **Embedded Analytics** | Full API access | Connected Apps, Embedding API | API changes required |
| **Cost Model** | Upfront license + infrastructure | Per-user subscription | Shift from CapEx to OpEx |
| **Backup/Recovery** | Customer responsibility | Tableau managed (14-day retention) | Reduced operational burden |

#### Power BI Report Server vs Power BI Service

| Capability | Power BI Report Server | Power BI Service (Cloud) | Migration Consideration |
|------------|------------------------|--------------------------|-------------------------|
| **Deployment** | On-premise Windows Server | Fully managed SaaS | No Windows Server management |
| **Licensing** | Power BI Premium or SQL Server Enterprise | Per-user or Premium capacity | License model change |
| **Features** | Lags cloud by 3-6 months | Latest features immediately | Access to AI, ML features |
| **Report Types** | PBIX, Paginated (RDL), Excel | PBIX, Paginated (Premium), Excel | Direct compatibility |
| **Data Sources** | On-premise + cloud | Cloud-first, gateway for on-prem | Gateway deployment critical |
| **Refresh Frequency** | Unlimited | 8/day (Pro), 48/day (Premium) | Plan for refresh limits |
| **Capacity** | Fixed hardware | Elastic scaling | Better performance during peaks |
| **Mobile Apps** | Limited offline | Full native apps | Better mobile experience |
| **Collaboration** | Basic sharing | Teams integration, comments, subscriptions | Enhanced collaboration |
| **API Access** | Limited | Full REST API | Better automation potential |

### 1.2 Decision Framework: Stay On-Prem vs Migrate to Cloud

**When to Stay On-Premise (or Hybrid):**

```yaml
stay_on_premise_if:
  data_residency:
    - Data cannot leave specific geographic boundaries
    - Regulatory requirements prohibit cloud storage
    - Extremely sensitive data (military, healthcare)

  network_constraints:
    - Air-gapped networks (no internet connectivity)
    - Data sources that cannot be accessed from cloud
    - Very high data volumes with limited bandwidth

  customization_needs:
    - Heavy use of custom extensions not approved for cloud
    - Custom authentication mechanisms (non-SAML)
    - Deep integration with on-prem systems

  cost_factors:
    - Very large user base where per-user pricing is prohibitive
    - Existing hardware with significant remaining life
    - Dedicated infrastructure already optimized
```

**When to Migrate to Cloud:**

```yaml
migrate_to_cloud_if:
  infrastructure_pain:
    - Aging hardware requiring refresh
    - High operational burden of maintenance
    - Difficulty keeping up with patches/updates
    - Limited IT resources for BI platform management

  business_needs:
    - Need for rapid scaling (M&A, growth)
    - Remote/distributed workforce
    - Desire for latest features
    - Mobile-first requirements

  cost_optimization:
    - Reducing capital expenditure
    - Eliminating data center costs
    - Optimizing IT staff allocation

  collaboration_requirements:
    - Enhanced sharing and collaboration
    - Integration with cloud productivity tools (Teams, Slack)
    - Self-service requirements
```

**Hybrid Approach:**

```
Hybrid Model: On-Prem + Cloud
├── Critical/Sensitive Data: Keep on-premise
├── Departmental/General Use: Migrate to cloud
├── Data Gateway: Bridge on-prem data to cloud
└── Gradual Migration: Move workloads incrementally

Benefits:
- Risk mitigation
- Flexibility
- Gradual transition
- Learn before full commitment
```

---

## Tableau Server to Tableau Cloud Migration

### 2.1 Migration Planning & Assessment

#### Pre-Migration Assessment Checklist

```markdown
## Tableau Server Assessment

### Environment Inventory
- [ ] Tableau Server version: _________
- [ ] Number of sites: _________
- [ ] Total number of users: _________
- [ ] User licensing (Creator, Explorer, Viewer breakdown): _________
- [ ] Number of workbooks: _________
- [ ] Number of data sources: _________
- [ ] Total data extract size: _____ GB
- [ ] Server specifications (CPU, RAM, storage): _________

### Data Source Analysis
- [ ] List all data source types (SQL Server, Oracle, files, etc.)
- [ ] Identify live connections vs extracts
- [ ] Document custom SQL queries
- [ ] Map data source locations (on-prem, cloud, hybrid)
- [ ] Identify data sources requiring Tableau Bridge

### Authentication & Security
- [ ] Current authentication method: _________
- [ ] SSO provider (if applicable): _________
- [ ] Row-level security implementations
- [ ] Custom roles and permissions
- [ ] Embedded analytics use cases

### Customizations & Extensions
- [ ] Custom extensions/plugins in use: _________
- [ ] Custom branding/themes
- [ ] REST API integrations
- [ ] Webhooks configurations
- [ ] Subscription configurations

### Performance & Usage
- [ ] Peak concurrent users: _________
- [ ] Average daily active users: _________
- [ ] Largest workbook size: _____ MB
- [ ] Slowest-performing workbooks
- [ ] Extract refresh schedules
```

#### Tableau Cloud Readiness Assessment

```python
def assess_tableau_cloud_readiness(server_metadata):
    """
    Assess readiness for Tableau Cloud migration
    Returns readiness score and recommendations
    """
    readiness_score = 100
    blockers = []
    warnings = []
    recommendations = []

    # Authentication
    if server_metadata['auth_method'] == 'Kerberos':
        readiness_score -= 20
        blockers.append("Kerberos authentication not supported in Tableau Cloud")
        recommendations.append("Plan migration to SAML-based SSO")

    # Data Sources
    live_connections = server_metadata['live_connection_count']
    if live_connections > 0:
        readiness_score -= 10
        warnings.append(f"{live_connections} live connections will require Tableau Bridge")
        recommendations.append("Deploy Tableau Bridge for on-prem data access")

    # Custom Extensions
    custom_extensions = server_metadata['custom_extensions']
    unapproved_extensions = [ext for ext in custom_extensions
                            if not ext['tableau_approved']]
    if unapproved_extensions:
        readiness_score -= 15
        blockers.append(f"{len(unapproved_extensions)} custom extensions not approved for Tableau Cloud")
        recommendations.append("Review extension alternatives or request Tableau approval")

    # Extract Size
    total_extract_size_gb = server_metadata['total_extract_size_gb']
    if total_extract_size_gb > 100:
        readiness_score -= 10
        warnings.append(f"Large extract size ({total_extract_size_gb} GB) - plan for migration time")
        recommendations.append("Consider incremental extract migration")

    # Version
    if server_metadata['version'] < '2020.1':
        readiness_score -= 15
        warnings.append("Tableau Server version is outdated")
        recommendations.append("Upgrade Tableau Server before migration")

    # Network Access
    if server_metadata['air_gapped']:
        readiness_score -= 30
        blockers.append("Air-gapped environment cannot connect to Tableau Cloud")
        recommendations.append("Consider hybrid deployment or dedicated data center connectivity")

    # Embedded Analytics
    if server_metadata['has_embedded_analytics']:
        readiness_score -= 5
        warnings.append("Embedded analytics requires API migration to Connected Apps")
        recommendations.append("Plan for Connected Apps implementation")

    # Generate readiness level
    if readiness_score >= 80:
        readiness = "HIGH - Ready to proceed"
    elif readiness_score >= 60:
        readiness = "MEDIUM - Address warnings before proceeding"
    elif readiness_score >= 40:
        readiness = "LOW - Resolve blockers before migration"
    else:
        readiness = "NOT READY - Significant changes required"

    return {
        'readiness_score': readiness_score,
        'readiness_level': readiness,
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations
    }
```

### 2.2 Tableau Cloud Migration Strategies

#### Strategy 1: Lift and Shift (Quickest Path)

**Approach:** Migrate existing workbooks and data sources with minimal changes.

**Timeline:** 1-3 months

**Process:**

```yaml
# Phase 1: Preparation (Weeks 1-2)
setup:
  - Provision Tableau Cloud site
  - Configure SAML SSO
  - Setup user groups and permissions
  - Deploy Tableau Bridge (if needed)
  - Create migration project team

# Phase 2: Pilot Migration (Weeks 3-4)
pilot:
  - Select 5-10 representative workbooks
  - Download from Tableau Server
  - Upload to Tableau Cloud
  - Test data connections
  - Validate functionality
  - Train pilot users

# Phase 3: Bulk Migration (Weeks 5-8)
bulk_migration:
  - Export all workbooks and data sources
  - Migrate in batches (by department or project)
  - Reconfigure data source connections
  - Update extract refresh schedules
  - Test each workbook

# Phase 4: Cutover (Weeks 9-10)
cutover:
  - Parallel run (both systems active)
  - User communication and training
  - DNS/URL redirection
  - Monitor adoption
  - Decommission Tableau Server

# Phase 5: Optimization (Weeks 11-12)
optimization:
  - Performance tuning
  - Cost optimization
  - User feedback incorporation
  - Documentation updates
```

**Migration Script:**

```python
# Python script using Tableau Server Client library
import tableauserverclient as TSC
import os
from datetime import datetime

def migrate_tableau_server_to_cloud(source_server, target_cloud, migration_config):
    """
    Automated migration of Tableau Server content to Tableau Cloud
    """

    # Connect to source (Tableau Server)
    source_auth = TSC.TableauAuth(
        migration_config['source_username'],
        migration_config['source_password'],
        site_id=migration_config['source_site']
    )
    source_server_conn = TSC.Server(source_server, use_server_version=True)

    # Connect to target (Tableau Cloud)
    target_auth = TSC.PersonalAccessTokenAuth(
        migration_config['cloud_token_name'],
        migration_config['cloud_token_secret'],
        site_id=migration_config['target_site']
    )
    target_server_conn = TSC.Server(target_cloud, use_server_version=True)

    with source_server_conn.auth.sign_in(source_auth):
        with target_server_conn.auth.sign_in(target_auth):

            # Migrate Projects
            print("Migrating projects...")
            migrate_projects(source_server_conn, target_server_conn)

            # Migrate Data Sources
            print("Migrating data sources...")
            migrate_datasources(source_server_conn, target_server_conn, migration_config)

            # Migrate Workbooks
            print("Migrating workbooks...")
            migrate_workbooks(source_server_conn, target_server_conn, migration_config)

            # Migrate Schedules (converted to Cloud schedules)
            print("Migrating schedules...")
            migrate_schedules(source_server_conn, target_server_conn)

    print("Migration complete!")

def migrate_projects(source, target):
    """Migrate project hierarchy"""
    all_projects = list(TSC.Pager(source.projects))

    for project in all_projects:
        # Check if project exists in target
        existing = [p for p in TSC.Pager(target.projects) if p.name == project.name]

        if not existing:
            new_project = TSC.ProjectItem(
                name=project.name,
                description=project.description,
                content_permissions=project.content_permissions
            )
            target.projects.create(new_project)
            print(f"Created project: {project.name}")
        else:
            print(f"Project already exists: {project.name}")

def migrate_datasources(source, target, config):
    """Migrate data sources"""
    all_datasources = list(TSC.Pager(source.datasources))

    for ds in all_datasources:
        # Download from source
        file_path = source.datasources.download(ds.id, filepath=f"temp/{ds.name}.tdsx")

        # Update connection if needed
        if config.get('update_connections'):
            file_path = update_datasource_connection(file_path, config)

        # Upload to target
        target_project = get_matching_project(target, ds.project_name)
        new_ds = TSC.DatasourceItem(target_project.id, name=ds.name)

        target.datasources.publish(new_ds, file_path, mode='CreateNew')
        print(f"Migrated data source: {ds.name}")

        # Cleanup
        os.remove(file_path)

def migrate_workbooks(source, target, config):
    """Migrate workbooks"""
    all_workbooks = list(TSC.Pager(source.workbooks))

    migration_log = []

    for wb in all_workbooks:
        try:
            # Download from source
            file_path = source.workbooks.download(wb.id, filepath=f"temp/{wb.name}.twbx")

            # Upload to target
            target_project = get_matching_project(target, wb.project_name)
            new_wb = TSC.WorkbookItem(
                target_project.id,
                name=wb.name,
                show_tabs=wb.show_tabs
            )

            target.workbooks.publish(new_wb, file_path, mode='CreateNew')

            migration_log.append({
                'workbook': wb.name,
                'status': 'SUCCESS',
                'timestamp': datetime.now()
            })

            print(f"Migrated workbook: {wb.name}")

            # Cleanup
            os.remove(file_path)

        except Exception as e:
            migration_log.append({
                'workbook': wb.name,
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now()
            })
            print(f"Failed to migrate workbook {wb.name}: {e}")

    # Save migration log
    save_migration_log(migration_log)

def update_datasource_connection(file_path, config):
    """
    Update data source connection strings for cloud environment
    """
    # This is a simplified example
    # In practice, you'd use the Tableau Document API

    from tableaudocumentapi import Datasource

    source_doc = Datasource.from_file(file_path)

    # Update server name
    if config.get('new_server'):
        for conn in source_doc.connections:
            conn.server = config['new_server']

    # Update database name
    if config.get('new_database'):
        for conn in source_doc.connections:
            conn.dbname = config['new_database']

    # Save updated file
    output_path = file_path.replace('.tdsx', '_updated.tdsx')
    source_doc.save_as(output_path)

    return output_path
```

#### Strategy 2: Re-platform with Optimization

**Approach:** Migrate to Tableau Cloud while optimizing for cloud-native features.

**Timeline:** 3-6 months

**Optimization Opportunities:**

1. **Extract Optimization:**
   - Convert large extracts to live connections via Tableau Bridge
   - Implement incremental extracts
   - Use Tableau Cloud's materialized views

2. **Performance Improvements:**
   - Leverage Tableau Cloud's auto-scaling
   - Optimize data models
   - Implement data source filters

3. **Collaboration Features:**
   - Enable commenting and subscriptions
   - Integrate with Slack/Teams
   - Setup data-driven alerts

4. **Security Enhancements:**
   - Implement Connected Apps for embedded analytics
   - Enhance row-level security
   - Enable encryption at rest

**Re-platforming Process:**

```markdown
## Week-by-Week Re-platforming Plan

### Weeks 1-2: Assessment & Design
- Analyze current usage patterns
- Identify optimization opportunities
- Design target architecture
- Plan extract-to-live conversions
- Design security model

### Weeks 3-6: Foundation Build
- Configure Tableau Cloud site
- Setup SAML SSO
- Deploy and configure Tableau Bridge
- Create certified data sources
- Establish governance framework

### Weeks 7-10: Content Migration (Optimized)
- Migrate data sources with optimizations
- Convert extracts to live connections (where appropriate)
- Migrate workbooks in waves
- Implement new collaboration features
- Setup monitoring and alerts

### Weeks 11-14: User Enablement
- Training programs (role-based)
- Power user workshops
- Self-service enablement
- Change management activities
- Documentation and knowledge base

### Weeks 15-18: Transition & Optimization
- Parallel run period
- User feedback incorporation
- Performance tuning
- Cost optimization
- Decommission planning

### Weeks 19-24: Continuous Improvement
- Monitor usage and performance
- Iterate based on user feedback
- Expand cloud-native features
- Decommission on-prem server
- Post-migration review
```

### 2.3 Tableau Bridge Configuration

**What is Tableau Bridge?**

Tableau Bridge is a client software that runs on a machine within your network to facilitate connectivity between Tableau Cloud and on-premise data sources.

**Bridge Deployment Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Tableau Cloud (SaaS)                      │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │ Workbooks  │  │ Data       │  │ Extract Refresh     │   │
│  │            │←─┤ Sources    │←─┤ Schedules           │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │ (HTTPS/443)
                              ▼
                    ┌─────────────────────┐
                    │  Corporate Firewall  │
                    └──────────┬───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Tableau Bridge    │
                    │  (Windows Client)  │
                    └──────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ SQL     │          │ Oracle  │          │ File    │
   │ Server  │          │ Database│          │ Shares  │
   └─────────┘          └─────────┘          └─────────┘

   On-Premise Data Sources
```

**Bridge Deployment Best Practices:**

```yaml
bridge_deployment:
  # Sizing
  recommended_specs:
    cpu: 4+ cores
    ram: 8+ GB
    disk: 50+ GB SSD
    network: Low latency to data sources

  # High Availability
  ha_configuration:
    minimum_bridges: 2
    deployment: Active-Active pooling
    purpose: Failover and load balancing
    same_domain: Required for pooling

  # Security
  security_practices:
    - Run as dedicated service account
    - Limit permissions to read-only on data sources
    - Enable application allowlisting
    - Secure credential storage
    - Regular patching and updates

  # Monitoring
  monitoring:
    - Bridge health checks
    - Extract refresh success rates
    - Performance metrics
    - Error logging
    - Capacity planning
```

**Bridge Configuration Script:**

```powershell
# PowerShell script to deploy and configure Tableau Bridge

# Install Tableau Bridge
$installerPath = "\\fileserver\software\TableauBridge.exe"
Start-Process -FilePath $installerPath -ArgumentList "/silent /install" -Wait

# Configure Bridge as Windows Service
$serviceName = "TableauBridge"
$serviceAccount = "DOMAIN\svc_tableau_bridge"

# Grant service account permissions
$acl = Get-Acl "C:\Program Files\Tableau\Tableau Bridge"
$permission = "$serviceAccount", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "C:\Program Files\Tableau\Tableau Bridge" $acl

# Configure Bridge settings
$bridgeConfig = @"
{
  "site": "your-site-name",
  "clientId": "your-connected-app-client-id",
  "secretId": "your-secret-id",
  "secretValue": "your-secret-value",
  "pooling": true,
  "maxConcurrentRefreshes": 4
}
"@

$bridgeConfig | Out-File -FilePath "C:\ProgramData\Tableau\Tableau Bridge\config.json"

# Start Bridge service
Start-Service -Name $serviceName

# Verify Bridge is running
Get-Service -Name $serviceName
```

**Bridge Monitoring Dashboard (Tableau Metadata API):**

```python
# Python script to monitor Tableau Bridge health

import requests
import pandas as pd
from datetime import datetime, timedelta

def get_bridge_health(tableau_cloud_url, api_version, auth_token, site_id):
    """
    Query Tableau Cloud for Bridge health metrics
    """

    # GraphQL query for Bridge status
    query = """
    {
      bridgeClients(filter: {siteId: "%s"}) {
        id
        name
        status
        lastConnectionTime
        poolId
        concurrentRefreshLimit
      }
    }
    """ % site_id

    headers = {
        'Content-Type': 'application/json',
        'X-Tableau-Auth': auth_token
    }

    response = requests.post(
        f'{tableau_cloud_url}/api/metadata/graphql',
        json={'query': query},
        headers=headers
    )

    bridge_data = response.json()['data']['bridgeClients']

    # Convert to DataFrame for analysis
    df = pd.DataFrame(bridge_data)

    # Health check
    health_report = {
        'total_bridges': len(df),
        'active_bridges': len(df[df['status'] == 'ACTIVE']),
        'inactive_bridges': len(df[df['status'] != 'ACTIVE']),
        'bridges_needing_attention': []
    }

    # Check last connection time
    for idx, bridge in df.iterrows():
        last_connection = pd.to_datetime(bridge['lastConnectionTime'])
        if datetime.now() - last_connection > timedelta(minutes=15):
            health_report['bridges_needing_attention'].append({
                'name': bridge['name'],
                'issue': 'No connection in 15+ minutes',
                'last_seen': last_connection
            })

    return health_report

# Monitor extract refresh failures
def get_failed_refreshes(tableau_cloud_url, api_version, auth_token, site_id):
    """
    Get failed extract refreshes in last 24 hours
    """

    query = """
    {
      backgroundJobs(
        filter: {
          siteId: "%s",
          jobType: REFRESH_EXTRACT,
          finishCode: FAILED,
          startTimeRange: {
            start: "%s",
            end: "%s"
          }
        }
      ) {
        id
        jobType
        finishCode
        datasource {
          name
        }
        errorMessage
        startedAt
        endedAt
      }
    }
    """ % (
        site_id,
        (datetime.now() - timedelta(days=1)).isoformat(),
        datetime.now().isoformat()
    )

    headers = {
        'Content-Type': 'application/json',
        'X-Tableau-Auth': auth_token
    }

    response = requests.post(
        f'{tableau_cloud_url}/api/metadata/graphql',
        json={'query': query},
        headers=headers
    )

    failed_jobs = response.json()['data']['backgroundJobs']

    return pd.DataFrame(failed_jobs)
```

---

## Power BI Report Server to Power BI Service

### 3.1 Power BI Migration Planning

#### Power BI Report Server Assessment

```markdown
## Power BI Report Server Environment Assessment

### Server Configuration
- [ ] Report Server version: _________
- [ ] SQL Server version: _________
- [ ] Server hardware specs: _________
- [ ] Number of reports: _________
- [ ] Number of datasets: _________
- [ ] Total users: _________

### Content Inventory
**PBIX Reports:**
- Count: _________
- Using DirectQuery: _________
- Using Import Mode: _________
- With scheduled refresh: _________

**Paginated Reports (RDL):**
- Count: _________
- Data sources: _________
- Subscription count: _________

**Excel Workbooks:**
- Count: _________
- Usage frequency: _________

### Data Sources
- [ ] SQL Server: _________
- [ ] Analysis Services: _________
- [ ] Oracle: _________
- [ ] Other databases: _________
- [ ] File-based sources: _________
- [ ] Cloud sources: _________

### Authentication & Security
- [ ] Windows Authentication
- [ ] Custom authentication
- [ ] Row-level security implementations: _________
- [ ] Folder-level permissions
- [ ] Report subscriptions count: _________

### Licensing
- [ ] Current license: [ ] Power BI Premium [ ] SQL Server Enterprise
- [ ] Number of Pro licenses needed: _________
- [ ] Premium capacity required: [ ] Yes [ ] No
```

#### Power BI Service Readiness Assessment

```python
def assess_powerbi_service_readiness(report_server_metadata):
    """
    Assess readiness for Power BI Service migration
    """
    readiness_score = 100
    blockers = []
    warnings = []
    recommendations = []

    # Check data sources
    on_prem_sources = report_server_metadata.get('on_prem_datasources', 0)
    if on_prem_sources > 0:
        readiness_score -= 10
        warnings.append(f"{on_prem_sources} on-premise data sources require On-Premises Data Gateway")
        recommendations.append("Plan On-Premises Data Gateway deployment")

    # Check refresh schedules
    total_refresh_schedules = report_server_metadata.get('refresh_schedules', 0)
    if total_refresh_schedules > 8 * report_server_metadata.get('dataset_count', 0):
        readiness_score -= 15
        warnings.append("Refresh frequency exceeds Power BI Pro limits (8/day)")
        recommendations.append("Consider Power BI Premium for unlimited refreshes")

    # Check paginated reports
    rdl_count = report_server_metadata.get('paginated_report_count', 0)
    if rdl_count > 0:
        has_premium = report_server_metadata.get('has_premium_license', False)
        if not has_premium:
            readiness_score -= 20
            blockers.append(f"{rdl_count} paginated reports require Power BI Premium")
            recommendations.append("Acquire Power BI Premium license or convert to PBIX")

    # Check custom visuals
    custom_visuals = report_server_metadata.get('custom_visuals', [])
    org_visuals = [v for v in custom_visuals if v['type'] == 'organizational']
    if org_visuals:
        readiness_score -= 5
        warnings.append(f"{len(org_visuals)} organizational custom visuals need admin deployment")
        recommendations.append("Plan for custom visual approval and deployment")

    # Check dataset sizes
    large_datasets = report_server_metadata.get('datasets_over_1gb', 0)
    if large_datasets > 0:
        readiness_score -= 10
        warnings.append(f"{large_datasets} datasets exceed 1GB (Pro limit)")
        recommendations.append("Consider Premium capacity or optimize dataset size")

    # Check authentication
    if report_server_metadata.get('uses_windows_auth', False):
        readiness_score -= 5
        warnings.append("Windows Authentication requires On-Premises Data Gateway with SSO")
        recommendations.append("Configure Kerberos SSO for On-Premises Data Gateway")

    # Network connectivity
    if report_server_metadata.get('restricted_network', False):
        readiness_score -= 15
        warnings.append("Network restrictions may prevent gateway connectivity")
        recommendations.append("Review firewall rules for Power BI Service connectivity")

    # Generate readiness level
    if readiness_score >= 85:
        readiness = "HIGH - Ready to proceed with migration"
    elif readiness_score >= 70:
        readiness = "MEDIUM - Address warnings before proceeding"
    elif readiness_score >= 50:
        readiness = "LOW - Resolve blockers, significant planning needed"
    else:
        readiness = "NOT READY - Major changes required before migration"

    return {
        'readiness_score': readiness_score,
        'readiness_level': readiness,
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations
    }
```

### 3.2 Power BI Service Migration Strategies

#### Strategy 1: Direct Migration (Report Server to Service)

**Best For:** Organizations with:
- Modern PBIX reports
- Cloud or hybrid data sources
- Existing Power BI Pro/Premium licenses
- Small to medium report portfolio (<100 reports)

**Migration Process:**

```yaml
# Phase 1: Preparation (Weeks 1-2)
preparation:
  licensing:
    - Provision Power BI tenant (if not existing)
    - Assign Power BI Pro licenses
    - Acquire Premium capacity (if needed)

  infrastructure:
    - Deploy On-Premises Data Gateway
    - Configure gateway for data sources
    - Test gateway connectivity
    - Setup service principal authentication

  security:
    - Configure Azure AD groups
    - Map Report Server roles to Power BI roles
    - Plan row-level security migration
    - Setup sensitivity labels

# Phase 2: Pilot (Weeks 3-4)
pilot:
  report_selection:
    - Choose 5-10 representative reports
    - Include various data source types
    - Mix of DirectQuery and Import mode

  migration_steps:
    - Download PBIX from Report Server
    - Test in Power BI Desktop (latest version)
    - Update data source connections
    - Publish to Power BI Service workspace
    - Configure refresh schedules
    - Test functionality and performance

  validation:
    - Data accuracy verification
    - Visual rendering check
    - User acceptance testing
    - Performance benchmarking

# Phase 3: Bulk Migration (Weeks 5-10)
bulk_migration:
  organization:
    - Group reports by department/function
    - Create Power BI workspaces
    - Establish workspace access controls

  migration_batches:
    week_5_6:
      - Finance reports
      - Setup shared datasets
    week_7_8:
      - Sales & Marketing reports
      - Configure subscriptions
    week_9_10:
      - Operations & HR reports
      - Migrate remaining reports

  automation:
    - Use Power BI REST API for bulk operations
    - Script dataset refresh configurations
    - Automate workspace permissions

# Phase 4: Transition (Weeks 11-12)
transition:
  parallel_run:
    - Both systems active for 2 weeks
    - Side-by-side validation
    - User training sessions
    - Support ramp-up

  cutover:
    - Redirect users to Power BI Service
    - Update bookmarks and links
    - Disable Report Server uploads
    - Monitor adoption metrics

# Phase 5: Decommission (Weeks 13-14)
decommission:
  - Archive Report Server content
  - Backup databases
  - Document migration notes
  - Decommission server infrastructure
  - Post-migration review
```

**Migration Automation Script:**

```powershell
# PowerShell script to migrate Power BI reports using REST API

# Install Power BI Management module
Install-Module -Name MicrosoftPowerBIMgmt -Force -AllowClobber

# Connect to Power BI Service
Connect-PowerBIServiceAccount

# Configuration
$reportServerUrl = "http://reportserver/reports"
$powerBIWorkspaceName = "Migrated Reports"
$sourceReportsPath = "C:\ReportServerReports"

# Create or get workspace
$workspace = Get-PowerBIWorkspace -Name $powerBIWorkspaceName
if (-not $workspace) {
    $workspace = New-PowerBIWorkspace -Name $powerBIWorkspaceName
    Write-Host "Created workspace: $powerBIWorkspaceName"
}

# Download reports from Report Server
$reports = Get-ChildItem -Path $sourceReportsPath -Filter *.pbix

foreach ($report in $reports) {
    try {
        Write-Host "Processing report: $($report.Name)"

        # Publish to Power BI Service
        $publishResult = New-PowerBIReport `
            -Path $report.FullName `
            -WorkspaceId $workspace.Id `
            -ConflictAction CreateOrOverwrite

        Write-Host "Successfully published: $($report.Name)"

        # Configure refresh schedule (if dataset exists)
        $reportName = [System.IO.Path]::GetFileNameWithoutExtension($report.Name)
        $dataset = Get-PowerBIDataset -WorkspaceId $workspace.Id |
                   Where-Object { $_.Name -eq $reportName }

        if ($dataset) {
            # Configure daily refresh at 6 AM
            $refreshSchedule = @{
                days = @("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
                times = @("06:00")
                enabled = $true
                localTimeZoneId = "Eastern Standard Time"
            }

            Set-PowerBIDatasetRefreshSchedule `
                -DatasetId $dataset.Id `
                -WorkspaceId $workspace.Id `
                -Schedule $refreshSchedule

            Write-Host "Configured refresh schedule for: $reportName"
        }

        # Log success
        Add-Content -Path "migration_log.txt" -Value "$($report.Name),SUCCESS,$(Get-Date)"

    } catch {
        Write-Host "Failed to publish report: $($report.Name)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red

        # Log failure
        Add-Content -Path "migration_log.txt" -Value "$($report.Name),FAILED,$($_.Exception.Message),$(Get-Date)"
    }
}

Write-Host "Migration complete. Check migration_log.txt for details."
```

#### Strategy 2: Modernization Migration

**Best For:** Organizations looking to:
- Redesign reports for cloud-native features
- Optimize data models
- Implement modern BI best practices
- Enhance user experience

**Modernization Focus Areas:**

```markdown
## Report Modernization Opportunities

### Data Model Optimization
**Before (Report Server):**
- Star schema in SQL Server
- Pre-aggregated tables for performance
- Multiple similar datasets

**After (Power BI Service):**
- Shared certified datasets
- Incremental refresh for large tables
- Aggregations in Import mode
- Composite models (Import + DirectQuery)
- Dataflows for reusable ETL logic

### Visual Design Enhancement
**Before:**
- Basic visuals (tables, bar charts)
- Limited interactivity
- Static layouts

**After:**
- Modern custom visuals
- Drill-through pages
- Report page tooltips
- Buttons and bookmarks for navigation
- Mobile-optimized layouts
- Accessibility features

### Collaboration Features
**Before:**
- Email subscriptions
- Exported PDFs/Excel
- Limited sharing

**After:**
- Teams integration
- Commenting and @mentions
- Shared and Certified content
- Automatic page refresh
- Dataflows and datamarts
- Power BI apps for consumption

### Advanced Analytics
**Before:**
- Static reports
- Manual analysis

**After:**
- AI visuals (Key Influencers, Decomposition Tree)
- Q&A natural language queries
- Quick Insights
- Anomaly detection
- Forecasting
- Integration with Azure ML

### Governance & Security
**Before:**
- Folder-based permissions
- Windows authentication
- Limited auditability

**After:**
- Workspace roles (Admin, Member, Contributor, Viewer)
- Azure AD integration
- Sensitivity labels
- Endorsement (Certified, Promoted)
- Usage metrics and lineage view
- Activity log and audit capabilities
```

**Modernization Workflow:**

```python
# Python script to analyze and recommend modernization opportunities

import pandas as pd
import json

def analyze_report_for_modernization(pbix_metadata):
    """
    Analyze Power BI report and recommend modernization opportunities
    """
    recommendations = []

    # Data Model Analysis
    if pbix_metadata['tables_count'] > 20:
        recommendations.append({
            'category': 'Data Model',
            'priority': 'High',
            'finding': f"{pbix_metadata['tables_count']} tables in model",
            'recommendation': 'Consider splitting into shared datasets',
            'benefit': 'Improved governance and reusability'
        })

    if pbix_metadata['duplicate_tables'] > 0:
        recommendations.append({
            'category': 'Data Model',
            'priority': 'High',
            'finding': f"{pbix_metadata['duplicate_tables']} duplicate table structures found",
            'recommendation': 'Create shared certified dataset',
            'benefit': 'Single source of truth, reduced maintenance'
        })

    # Performance Optimization
    if pbix_metadata['dataset_size_mb'] > 1000:
        recommendations.append({
            'category': 'Performance',
            'priority': 'High',
            'finding': f"Large dataset: {pbix_metadata['dataset_size_mb']} MB",
            'recommendation': 'Implement incremental refresh',
            'benefit': 'Faster refresh times, reduced resource usage'
        })

    if pbix_metadata['calculated_columns_count'] > pbix_metadata['measures_count']:
        recommendations.append({
            'category': 'Performance',
            'priority': 'Medium',
            'finding': 'More calculated columns than measures',
            'recommendation': 'Convert calculated columns to measures where possible',
            'benefit': 'Reduced dataset size and improved performance'
        })

    # Visual Enhancements
    basic_visuals = ['table', 'matrix', 'card']
    advanced_visuals = ['keyInfluencers', 'decompositionTree', 'smartNarrative']

    has_only_basic = all(v in basic_visuals for v in pbix_metadata['visual_types'])
    has_no_advanced = not any(v in advanced_visuals for v in pbix_metadata['visual_types'])

    if has_only_basic:
        recommendations.append({
            'category': 'User Experience',
            'priority': 'Medium',
            'finding': 'Report uses only basic visuals',
            'recommendation': 'Enhance with modern visuals and interactivity',
            'benefit': 'Improved insights discovery and user engagement'
        })

    if has_no_advanced:
        recommendations.append({
            'category': 'Analytics',
            'priority': 'Low',
            'finding': 'No AI-powered visuals in use',
            'recommendation': 'Add Key Influencers, Decomposition Tree, or Smart Narrative',
            'benefit': 'Automated insights and deeper analysis'
        })

    # Mobile Optimization
    if not pbix_metadata.get('has_mobile_layout', False):
        recommendations.append({
            'category': 'User Experience',
            'priority': 'Medium',
            'finding': 'No mobile layout configured',
            'recommendation': 'Create mobile-optimized layouts',
            'benefit': 'Better mobile user experience'
        })

    # Security & Governance
    if not pbix_metadata.get('has_rls', False) and pbix_metadata.get('contains_sensitive_data', False):
        recommendations.append({
            'category': 'Security',
            'priority': 'High',
            'finding': 'Sensitive data without row-level security',
            'recommendation': 'Implement row-level security (RLS)',
            'benefit': 'Data protection and compliance'
        })

    # Generate modernization score
    high_priority = len([r for r in recommendations if r['priority'] == 'High'])
    medium_priority = len([r for r in recommendations if r['priority'] == 'Medium'])
    low_priority = len([r for r in recommendations if r['priority'] == 'Low'])

    modernization_score = 100 - (high_priority * 15 + medium_priority * 10 + low_priority * 5)

    return {
        'modernization_score': max(modernization_score, 0),
        'recommendations': recommendations,
        'priority_breakdown': {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority
        }
    }

# Example usage
report_metadata = {
    'report_name': 'Sales Analysis',
    'tables_count': 25,
    'duplicate_tables': 3,
    'dataset_size_mb': 1500,
    'calculated_columns_count': 20,
    'measures_count': 10,
    'visual_types': ['table', 'clusteredBarChart', 'lineChart'],
    'has_mobile_layout': False,
    'has_rls': False,
    'contains_sensitive_data': True
}

analysis = analyze_report_for_modernization(report_metadata)
print(f"Modernization Score: {analysis['modernization_score']}/100")
print(f"\nRecommendations:")
for rec in analysis['recommendations']:
    print(f"[{rec['priority']}] {rec['category']}: {rec['recommendation']}")
```

### 3.3 On-Premises Data Gateway Configuration

**Gateway Architecture:**

```
┌──────────────────────────────────────────────────────────┐
│            Power BI Service (Cloud)                       │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐     │
│  │ Reports  │  │ Datasets │  │ Scheduled Refresh  │     │
│  └──────────┘  └──────────┘  └────────────────────┘     │
└────────────────────────┬─────────────────────────────────┘
                         │ (Outbound HTTPS/443)
                         │ (Azure Service Bus)
                         ▼
              ┌──────────────────────┐
              │  Corporate Firewall   │
              │  (No Inbound Required)│
              └──────────┬────────────┘
                         │
              ┌──────────▼────────────┐
              │ On-Premises Data      │
              │ Gateway               │
              │ (Windows Server)      │
              └──────────┬────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ SQL     │    │ Oracle  │    │ Analysis│
    │ Server  │    │ Database│    │ Services│
    └─────────┘    └─────────┘    └─────────┘

    On-Premise Data Sources
```

**Gateway Deployment Best Practices:**

```yaml
gateway_deployment:
  # Server Requirements
  minimum_specs:
    os: Windows Server 2012 R2 or later
    cpu: 8+ cores
    ram: 16+ GB (32 GB for high load)
    disk: 100+ GB SSD
    network: Low latency (<50ms to data sources)

  # High Availability
  ha_setup:
    deployment_model: Cluster
    minimum_nodes: 2
    recommended_nodes: 3
    load_distribution: Round-robin
    failover: Automatic

  # Security
  security_configuration:
    service_account: Dedicated domain account (least privilege)
    encryption: TLS 1.2 minimum
    credentials: Encrypted in gateway
    authentication: Windows Auth or Service Principal
    network: Isolated network segment

  # Performance Optimization
  performance_tuning:
    mashup_engine:
      container_count: Based on CPU cores
      max_evaluation_workspace_memory_mb: 4096

    query_timeout: 600  # seconds
    max_concurrent_operations: 10

    monitoring:
      - Gateway performance counters
      - Query execution times
      - Refresh success rates
      - Resource utilization

  # Monitoring & Maintenance
  operations:
    monitoring:
      - Gateway health dashboard
      - Performance metrics
      - Error logging
      - Capacity planning

    maintenance:
      - Monthly updates
      - Quarterly performance reviews
      - Annual DR testing
      - Credential rotation
```

**Gateway Installation Script:**

```powershell
# PowerShell script for automated gateway deployment

# Configuration
$gatewayInstallerPath = "\\fileserver\software\OnPremisesDataGateway.exe"
$gatewayServiceAccount = "DOMAIN\svc_powerbi_gateway"
$recoveryKey = "YOUR-GATEWAY-RECOVERY-KEY"  # Store securely!

# Pre-requisites check
Write-Host "Checking pre-requisites..."

# Check OS version
$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion.Major -lt 6 -or ($osVersion.Major -eq 6 -and $osVersion.Minor -lt 3)) {
    Write-Error "Windows Server 2012 R2 or later is required"
    exit 1
}

# Check .NET Framework
$dotNetVersion = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full").Release
if ($dotNetVersion -lt 461808) {  # .NET 4.7.2
    Write-Error ".NET Framework 4.7.2 or later is required"
    exit 1
}

# Install gateway in silent mode
Write-Host "Installing On-Premises Data Gateway..."
Start-Process -FilePath $gatewayInstallerPath -ArgumentList "/quiet /norestart ENABLEGATEWAYTELEMETRY=0" -Wait

# Wait for installation
Start-Sleep -Seconds 30

# Configure gateway
Write-Host "Configuring gateway..."

# Import Power BI Data Gateway module
$gatewayPath = "C:\Program Files\On-premises data gateway"
Add-Type -Path "$gatewayPath\Microsoft.PowerBI.DataMovement.Pipeline.GatewayCore.dll"

# Configure gateway (this requires manual configuration or Azure AD app)
# For automated setup, use REST API or PowerShell commands

# Configure Windows Service to run as service account
$service = Get-WmiObject win32_service | Where-Object {$_.Name -eq "PBIEgwService"}
$service.Change($null,$null,$null,$null,$null,$null,$gatewayServiceAccount,$null,$null,$null,$null)

# Set service startup to Automatic
Set-Service -Name "PBIEgwService" -StartupType Automatic

# Configure Performance Counters
$perfCounterPath = "C:\Program Files\On-premises data gateway\PerfCounters"
& "$perfCounterPath\GatewayPerfCounterInstaller.exe" /install

# Configure Windows Firewall (outbound HTTPS)
New-NetFirewallRule -DisplayName "Power BI Gateway Outbound" `
    -Direction Outbound `
    -Protocol TCP `
    -LocalPort Any `
    -RemotePort 443 `
    -Action Allow `
    -Program "$gatewayPath\Microsoft.PowerBI.DataMovement.GatewayCore.exe"

# Start service
Start-Service -Name "PBIEgwService"

Write-Host "Gateway installation complete!"
Write-Host "Please complete registration in Power BI Service"
```

**Gateway Monitoring Dashboard (Power BI Template):**

```dax
-- DAX measures for Gateway monitoring dashboard

-- Gateway Health Score
Gateway Health Score =
VAR OnlineGateways = COUNTROWS(FILTER(Gateways, Gateways[Status] = "Online"))
VAR TotalGateways = COUNTROWS(Gateways)
VAR HealthPercentage = DIVIDE(OnlineGateways, TotalGateways, 0)
VAR SuccessRate = [Refresh Success Rate]
RETURN
    (HealthPercentage * 0.5 + SuccessRate * 0.5) * 100

-- Refresh Success Rate
Refresh Success Rate =
VAR SuccessfulRefreshes = COUNTROWS(FILTER(RefreshHistory, RefreshHistory[Status] = "Completed"))
VAR TotalRefreshes = COUNTROWS(RefreshHistory)
RETURN
    DIVIDE(SuccessfulRefreshes, TotalRefreshes, 0)

-- Average Refresh Duration
Average Refresh Duration (Minutes) =
AVERAGEX(
    FILTER(RefreshHistory, RefreshHistory[Status] = "Completed"),
    DATEDIFF(RefreshHistory[StartTime], RefreshHistory[EndTime], MINUTE)
)

-- Failed Refreshes (Last 24 Hours)
Failed Refreshes 24H =
CALCULATE(
    COUNTROWS(RefreshHistory),
    RefreshHistory[Status] = "Failed",
    RefreshHistory[StartTime] >= NOW() - 1
)

-- Gateway CPU Utilization
Avg Gateway CPU % =
AVERAGEX(
    GatewayMetrics,
    GatewayMetrics[CPUUtilization]
)

-- Gateway Memory Utilization
Avg Gateway Memory % =
AVERAGEX(
    GatewayMetrics,
    GatewayMetrics[MemoryUtilization]
)

-- Most Common Errors
Top Errors =
TOPN(
    10,
    SUMMARIZE(
        FILTER(RefreshHistory, RefreshHistory[Status] = "Failed"),
        RefreshHistory[ErrorMessage],
        "Error Count", COUNTROWS(RefreshHistory)
    ),
    [Error Count],
    DESC
)
```

---

## Data Connectivity Strategies

### 4.1 Data Source Migration Patterns

**Pattern 1: Cloud-First (Eliminate On-Prem Dependencies)**

```yaml
strategy: Migrate data sources to cloud before migrating BI platform

approach:
  phase_1:
    - Identify on-premise databases
    - Plan database migration to Azure SQL, Snowflake, or RDS
    - Execute database migration
    - Validate data integrity

  phase_2:
    - Update BI reports to cloud data sources
    - Test connectivity and performance
    - Configure cloud-native authentication

  phase_3:
    - Migrate BI platform to cloud
    - No gateway needed!
    - Simplified architecture

benefits:
  - No gateway management
  - Better performance (cloud-to-cloud)
  - Reduced complexity
  - Cloud-native security

challenges:
  - Database migration effort
  - Potential application impacts
  - Legacy system dependencies
```

**Pattern 2: Gateway-Enabled (Hybrid Architecture)**

```yaml
strategy: Keep data on-premise, use gateway for connectivity

approach:
  phase_1:
    - Deploy and configure data gateway
    - Test connectivity to all data sources
    - Configure service account permissions
    - Setup gateway clustering for HA

  phase_2:
    - Migrate BI platform to cloud
    - Configure data sources via gateway
    - Test refresh schedules
    - Monitor gateway performance

  phase_3:
    - Optimize gateway performance
    - Plan eventual cloud data migration
    - Maintain gateway as long as needed

benefits:
  - No data source changes required
  - Incremental migration
  - Flexibility
  - Risk mitigation

challenges:
  - Gateway management overhead
  - Performance dependency on gateway
  - Network latency considerations
  - Ongoing infrastructure costs
```

**Pattern 3: Data Virtualization (Best of Both Worlds)**

```yaml
strategy: Use data virtualization layer (Denodo, Starburst, etc.)

approach:
  phase_1:
    - Deploy data virtualization platform
    - Create virtual views of on-prem data
    - Expose via cloud-accessible endpoints
    - Implement caching and optimization

  phase_2:
    - BI platform connects to virtualization layer
    - Appears as cloud data source
    - No gateway needed for BI platform
    - Data remains on-premise

  phase_3:
    - Gradually migrate physical data to cloud
    - Update virtual views to point to cloud
    - BI reports unchanged

benefits:
  - Abstraction layer for future migrations
  - Performance optimization via caching
  - Unified data access
  - Gradual migration path

challenges:
  - Additional technology layer
  - Cost of virtualization platform
  - Learning curve
  - Potential performance overhead
```

### 4.2 Extract vs Live Connection Decision Framework

```python
def recommend_connection_mode(dataset_metadata):
    """
    Recommend Import (Extract) vs DirectQuery (Live) connection mode
    """
    score_import = 0
    score_directquery = 0

    # Data Volume
    rows = dataset_metadata['row_count']
    if rows < 1000000:  # < 1M rows
        score_import += 3
    elif rows < 10000000:  # 1M - 10M rows
        score_import += 1
        score_directquery += 1
    else:  # > 10M rows
        score_directquery += 3

    # Data Freshness Requirements
    freshness = dataset_metadata['freshness_requirement']
    if freshness == 'real-time':
        score_directquery += 3
    elif freshness == 'hourly':
        score_directquery += 2
    elif freshness == 'daily':
        score_import += 2
    else:  # weekly or less
        score_import += 3

    # Query Complexity
    complexity = dataset_metadata['query_complexity']
    if complexity == 'simple':  # Simple aggregations
        score_directquery += 2
    elif complexity == 'complex':  # Complex DAX, many relationships
        score_import += 3

    # Data Source Performance
    source_performance = dataset_metadata['source_performance']
    if source_performance == 'fast':  # Optimized DW
        score_directquery += 2
    elif source_performance == 'slow':  # Legacy OLTP
        score_import += 3

    # User Concurrency
    concurrent_users = dataset_metadata['concurrent_users']
    if concurrent_users > 50:
        score_import += 2  # Import handles concurrency better

    # Determine recommendation
    if score_import > score_directquery:
        mode = "Import (Extract)"
        reason = "Better performance for complex analysis and high concurrency"
    elif score_directquery > score_import:
        mode = "DirectQuery (Live)"
        reason = "Real-time data access and large dataset handling"
    else:
        mode = "Composite (Hybrid)"
        reason = "Mix of Import and DirectQuery for optimal balance"

    # Additional considerations
    considerations = []

    if dataset_metadata['row_count'] > 1000000 and mode == "Import":
        considerations.append("Implement incremental refresh to manage large dataset")

    if dataset_metadata['freshness_requirement'] == 'real-time' and mode == "Import":
        considerations.append("Consider automatic page refresh feature")

    if mode == "DirectQuery":
        considerations.append("Ensure data source can handle query load")
        considerations.append("Implement query optimization (indexes, partitioning)")

    return {
        'recommended_mode': mode,
        'reason': reason,
        'import_score': score_import,
        'directquery_score': score_directquery,
        'considerations': considerations
    }

# Example usage
dataset = {
    'name': 'Sales Transactions',
    'row_count': 5000000,
    'freshness_requirement': 'hourly',
    'query_complexity': 'complex',
    'source_performance': 'fast',
    'concurrent_users': 100
}

recommendation = recommend_connection_mode(dataset)
print(f"Recommended Mode: {recommendation['recommended_mode']}")
print(f"Reason: {recommendation['reason']}")
```

---

## Security & Governance

### 5.1 Authentication & Authorization Migration

#### Tableau Cloud Authentication

```markdown
## Tableau Cloud Authentication Options

### SAML Single Sign-On (Recommended)
**Supported IdPs:**
- Okta
- Microsoft Azure AD
- OneLogin
- PingFederate
- ADFS

**Configuration Steps:**
1. Configure SAML app in IdP
2. Download IdP metadata XML
3. Configure SAML in Tableau Cloud
4. Map SAML attributes to Tableau user attributes
5. Test with pilot users
6. Enable for all users

**SAML Attribute Mapping:**
```xml
<saml:Attribute Name="username" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic">
    <saml:AttributeValue>user@domain.com</saml:AttributeValue>
</saml:Attribute>
<saml:Attribute Name="displayName">
    <saml:AttributeValue>John Doe</saml:AttributeValue>
</saml:Attribute>
```

### Multi-Factor Authentication (MFA)
**Implementation:**
- Handled by IdP (Azure AD, Okta, etc.)
- Tableau Cloud supports IdP-enforced MFA
- Recommended for all users
- Conditional access policies

### Service Account Authentication
**For Automation:**
- Personal Access Tokens (PAT)
- Connected Apps (OAuth)
- Recommended: Connected Apps for production

**PAT Configuration:**
```python
import tableauserverclient as TSC

# Authenticate with Personal Access Token
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name='automation-token',
    personal_access_token='your-secret-token',
    site_id='your-site'
)

server = TSC.Server('https://10ax.online.tableau.com', use_server_version=True)

with server.auth.sign_in(tableau_auth):
    # Perform automated tasks
    pass
```

```markdown

#### Power BI Service Authentication

```markdown
## Power BI Service Authentication Options

### Azure Active Directory (Required)
**Single Sign-On:**
- Automatic for Microsoft 365 users
- Seamless authentication
- Conditional Access policies
- MFA support

**Guest Users (B2B):**
- External collaboration
- Azure AD B2B invitations
- Same security policies
- Audited access

### Service Principal Authentication
**For Automation:**
- Azure AD App Registration
- Client ID + Client Secret
- Recommended for production automation

**Setup Steps:**
1. Register app in Azure AD
2. Grant Power BI Service permissions
3. Enable service principal in Power BI Admin Portal
4. Add service principal to workspaces

**Example Code:**
```python
from msal import ConfidentialClientApplication
import requests

# Service Principal Authentication
app = ConfidentialClientApplication(
    client_id="your-client-id",
    client_credential="your-client-secret",
    authority="https://login.microsoftonline.com/your-tenant-id"
)

# Acquire token
token_response = app.acquire_token_for_client(
    scopes=["https://analysis.windows.net/powerbi/api/.default"]
)

access_token = token_response['access_token']

# Use token for Power BI API calls
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.powerbi.com/v1.0/myorg/groups',
    headers=headers
)
```
```

### 5.2 Row-Level Security Migration

#### Tableau RLS Migration

```sql
-- Tableau Server (On-Prem) User Filter
-- Created as calculated field in data source

[User Sales Region] = USERNAME()

-- Tableau Cloud (Same approach)
-- No migration needed for simple RLS

[User Sales Region] = USERNAME()

-- For more complex scenarios:
-- Option 1: Entitlements table
-- Create entitlements table mapping users to allowed data

-- Option 2: Dynamic RLS with parameters
-- Use parameters for role-based filtering
```

**Entitlements Table Approach:**

```sql
-- Entitlements table structure
CREATE TABLE user_entitlements (
    username VARCHAR(255),
    region VARCHAR(100),
    access_level VARCHAR(50)
);

-- Populate entitlements
INSERT INTO user_entitlements VALUES
('john.doe@company.com', 'North', 'Full'),
('jane.smith@company.com', 'South', 'Full'),
('bob.jones@company.com', 'East', 'Read-Only');

-- Tableau calculated field for RLS
[Region Filter] =
IF [Region] = [User Region] THEN TRUE
ELSEIF [User Access Level] = 'Admin' THEN TRUE
ELSE FALSE
END

-- Apply filter to data source
-- Add [Region Filter] = TRUE to Filters shelf
```

#### Power BI RLS Migration

```dax
-- Power BI RLS (same for Report Server and Service)

-- Static RLS (Role-based)
-- Create role "Sales Team"
[Region] = "North" || [Region] = "South"

-- Create role "Finance Team"
1=1  -- See all data

-- Dynamic RLS (User-based)
-- Requires user mapping table

-- User mapping table
Users =
DATATABLE(
    "Email", STRING,
    "AllowedRegion", STRING,
    {
        {"john.doe@company.com", "North"},
        {"jane.smith@company.com", "South"},
        {"bob.jones@company.com", "East"}
    }
)

-- RLS rule (applied to Sales table)
[Region] =
LOOKUPVALUE(
    Users[AllowedRegion],
    Users[Email],
    USERPRINCIPALNAME()
)

-- For multiple regions per user:
VAR UserEmail = USERPRINCIPALNAME()
VAR UserRegions =
    FILTER(
        Users,
        Users[Email] = UserEmail
    )
RETURN
    [Region] IN UserRegions
```

**Testing RLS:**

```python
# Python script to test Power BI RLS

from powerbiclient import QuickVisualize, get_dataset_config
from powerbiclient.authentication import DeviceCodeLoginAuthentication

# Authenticate
device_auth = DeviceCodeLoginAuthentication()

# Get dataset
dataset_id = "your-dataset-id"

# Test RLS for specific user
test_user = "john.doe@company.com"

# This would be done in Power BI Service UI:
# 1. Go to dataset settings
# 2. Click "Security" tab
# 3. Click "Test as role"
# 4. Select role
# 5. Enter user email
# 6. Click "View as"

# Alternative: Use Power BI REST API
import requests

# Get access token (service principal or user)
headers = {'Authorization': f'Bearer {access_token}'}

# Test RLS via API (requires Premium)
test_rls_url = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries'

test_query = {
    "queries": [
        {
            "query": "EVALUATE SUMMARIZE(Sales, Sales[Region], Sales[Amount])"
        }
    ],
    "impersonatedUserName": test_user
}

response = requests.post(test_rls_url, json=test_query, headers=headers)
print(response.json())
```

### 5.3 Governance Framework

```yaml
cloud_bi_governance:

  # Content Lifecycle
  content_lifecycle:
    development:
      - Personal workspaces
      - Experimentation allowed
      - No RLS required
      - Auto-delete after 90 days

    test:
      - Test workspaces
      - Limited user access
      - RLS testing
      - Quality assurance

    production:
      - Production workspaces
      - Certified content
      - Full RLS implementation
      - Change control process

  # Certification Process
  certification:
    dataset_certification:
      requirements:
        - Data quality validation
        - Performance testing
        - Security review
        - Documentation complete
        - Owner approval

      endorsement_levels:
        - Promoted: Meets basic standards
        - Certified: IT approved, production-ready

    report_certification:
      requirements:
        - Uses certified dataset
        - Design standards compliance
        - UAT completed
        - Accessibility check

  # Access Control
  access_control:
    workspace_roles:
      - Admin: Full control
      - Member: Create and publish
      - Contributor: Edit existing
      - Viewer: View only

    dataset_permissions:
      - Build: Can create reports
      - Read: Can view data
      - Reshare: Can share with others

    row_level_security:
      - Dynamic RLS for user-level
      - Role-based for group-level
      - Regular access reviews

  # Monitoring & Compliance
  monitoring:
    usage_analytics:
      - Active users tracking
      - Content usage metrics
      - Performance monitoring
      - Capacity utilization

    audit_logging:
      - User activities
      - Data access
      - Content changes
      - Export activities

    compliance:
      - Sensitivity labels
      - Data classification
      - Export controls
      - Regulatory reporting

  # Data Quality
  data_quality:
    refresh_monitoring:
      - Success rate targets: >99%
      - Failure alerting
      - Root cause analysis
      - Remediation tracking

    data_validation:
      - Automated quality checks
      - Anomaly detection
      - Business rule validation
      - Reconciliation reports
```

---

## Performance Optimization

### 6.1 Cloud BI Performance Best Practices

#### Tableau Cloud Optimization

```markdown
## Tableau Cloud Performance Optimization

### Data Extract Optimization
**Incremental Refresh:**
- Configure for tables >1M rows
- Define incremental key (date column)
- Reduces refresh time by 70-90%

**Extract Filters:**
- Filter unnecessary historical data
- Remove unused columns
- Aggregate where possible

**Example Configuration:**
```yaml
extract_config:
  table: Sales
  incremental_refresh:
    enabled: true
    key_column: OrderDate
    range: Last 2 years

  filters:
    - OrderDate >= DateAdd('year', -2, Today())
    - OrderStatus != 'Cancelled'

  aggregation:
    enabled: true
    dimensions: [Date, Product, Region]
    measures: [Sales, Quantity]
```

### Workbook Optimization
**Data Model:**
- Minimize data sources
- Use data blending sparingly
- Optimize join types
- Remove unused fields

**Calculations:**
- Use FIXED LOD instead of INCLUDE/EXCLUDE when possible
- Avoid nested table calculations
- Pre-calculate in data source when possible

**Dashboard Design:**
- Limit number of views per dashboard (5-7 max)
- Use dashboard actions instead of filters
- Implement lazy loading (show/hide containers)
- Optimize image sizes

**Performance Recording Analysis:**
```python
# Analyze Tableau Performance Recording (.twbr file)
import xml.etree.ElementTree as ET
import pandas as pd

def analyze_performance_recording(twbr_file_path):
    """
    Parse and analyze Tableau performance recording
    """
    tree = ET.parse(twbr_file_path)
    root = tree.getroot()

    # Extract query times
    queries = []
    for query in root.findall('.//query'):
        queries.append({
            'query_id': query.get('id'),
            'duration_ms': float(query.get('elapsed-time-ms', 0)),
            'query_text': query.findtext('query-text'),
            'row_count': int(query.get('rows-returned', 0))
        })

    df = pd.DataFrame(queries)

    # Identify slow queries (>2 seconds)
    slow_queries = df[df['duration_ms'] > 2000].sort_values('duration_ms', ascending=False)

    # Calculate statistics
    total_time = df['duration_ms'].sum()
    avg_time = df['duration_ms'].mean()

    analysis = {
        'total_queries': len(df),
        'total_execution_time_sec': total_time / 1000,
        'avg_query_time_ms': avg_time,
        'slow_query_count': len(slow_queries),
        'slow_queries': slow_queries.to_dict('records')
    }

    return analysis
```
```

#### Power BI Service Optimization

```markdown
## Power BI Service Performance Optimization

### Data Model Optimization
**Data Types:**
- Use smallest appropriate data type
- Integer instead of Decimal when possible
- DateTime instead of Text for dates

**Relationships:**
- Star schema preferred over snowflake
- Avoid many-to-many relationships
- Use surrogate keys for large tables

**Calculated Columns vs Measures:**
- Use measures instead of calculated columns
- Calculated columns consume memory
- Measures calculated at query time

### DAX Optimization
**Variables:**
```dax
-- Before (inefficient)
Profit Margin % =
DIVIDE(
    SUM(Sales[Revenue]) - SUM(Sales[Cost]),
    SUM(Sales[Revenue])
)

-- After (optimized with variables)
Profit Margin % =
VAR Revenue = SUM(Sales[Revenue])
VAR Cost = SUM(Sales[Cost])
VAR Profit = Revenue - Cost
RETURN
    DIVIDE(Profit, Revenue)
```

**Iterator Functions:**
```dax
-- Use CALCULATE instead of iterators when possible

-- Less efficient
Total Sales = SUMX(Sales, Sales[Quantity] * Sales[Price])

-- More efficient (if UnitPrice is pre-calculated)
Total Sales = SUM(Sales[TotalAmount])
```

**Avoid Expensive Functions:**
```dax
-- Avoid
Distinct Count = DISTINCTCOUNT(Sales[CustomerID])

-- Better (if appropriate)
Distinct Count = COUNT(Sales[CustomerID])  -- If CustomerID is unique per row
```

### Aggregations (Premium Feature)
**Setup:**
1. Create aggregation table
2. Define aggregation relationship
3. Power BI automatically uses aggregation

**Example:**
```dax
-- Aggregate table (daily summary)
Sales_Daily_Agg =
SUMMARIZECOLUMNS(
    'Date'[Date],
    'Product'[ProductKey],
    'Customer'[CustomerKey],
    "TotalSales", SUM(Sales[SalesAmount]),
    "TotalQuantity", SUM(Sales[Quantity])
)

-- Aggregation covers detail queries automatically
```

### Incremental Refresh
**Configuration:**
```json
{
  "incrementalRefresh": {
    "enabled": true,
    "rollingWindowGranularity": "Month",
    "rollingWindowPeriods": 24,
    "incrementalGranularity": "Day",
    "incrementalPeriods": 7,
    "detectDataChanges": true,
    "dataChangesColumn": "ModifiedDate"
  }
}
```

**Benefits:**
- Reduces refresh time
- Minimizes data transfer
- Partitions data automatically (Premium)

### Query Performance Analyzer
```python
# Analyze Power BI query performance using DAX Studio

# Connect to Power BI Service dataset
# Run query performance analysis
# Export metrics

import pandas as pd

def analyze_dax_query_performance(dax_studio_export_csv):
    """
    Analyze DAX query performance metrics
    """
    df = pd.read_csv(dax_studio_export_csv)

    # Identify expensive queries
    expensive_queries = df[df['Duration_ms'] > 1000].sort_values('Duration_ms', ascending=False)

    # Analyze query patterns
    storage_engine_time = df['SE_Duration_ms'].sum()
    formula_engine_time = df['FE_Duration_ms'].sum()

    # Recommendations
    recommendations = []

    if storage_engine_time > formula_engine_time * 2:
        recommendations.append("High Storage Engine time - optimize data model and relationships")

    if formula_engine_time > storage_engine_time * 2:
        recommendations.append("High Formula Engine time - optimize DAX measures")

    return {
        'total_queries': len(df),
        'expensive_query_count': len(expensive_queries),
        'storage_engine_percentage': storage_engine_time / (storage_engine_time + formula_engine_time) * 100,
        'formula_engine_percentage': formula_engine_time / (storage_engine_time + formula_engine_time) * 100,
        'recommendations': recommendations
    }
```
```

---

## Cost Management

### 7.1 Tableau Cloud Cost Optimization

```yaml
tableau_cloud_pricing:

  # User-Based Licensing
  user_licenses:
    creator:
      price_per_user_per_month: 70
      capabilities:
        - Full Tableau Desktop
        - Tableau Prep Builder
        - Web authoring
        - Publishing

    explorer:
      price_per_user_per_month: 42
      capabilities:
        - Web authoring (limited)
        - Editing published workbooks
        - Creating custom views

    viewer:
      price_per_user_per_month: 15
      capabilities:
        - View and interact
        - Commenting
        - Subscriptions

  # Cost Optimization Strategies
  optimization:
    right_sizing_licenses:
      - Audit user activity
      - Downgrade inactive Creators
      - Promote power users selectively
      - Expected savings: 20-40%

    extract_optimization:
      - Reduce extract sizes
      - Implement incremental refresh
      - Remove unnecessary data
      - Expected savings: 10-20% (storage)

    bridge_consolidation:
      - Reduce number of Bridges
      - Optimize refresh schedules
      - Batch similar refreshes
      - Expected savings: 5-15%
```

**Cost Monitoring Dashboard:**

```sql
-- Tableau Cloud usage analytics

-- User activity by license type
SELECT
    u.user_name,
    u.site_role,
    COUNT(DISTINCT DATE(h.created_at)) as active_days_30d,
    COUNT(h.hist_event_id) as total_views_30d,
    CASE
        WHEN COUNT(DISTINCT DATE(h.created_at)) < 5 THEN 'Underutilized'
        WHEN COUNT(DISTINCT DATE(h.created_at)) >= 20 THEN 'Highly Active'
        ELSE 'Moderate'
    END as utilization
FROM
    historical_events h
    JOIN users u ON h.user_id = u.user_id
WHERE
    h.created_at >= CURRENT_DATE - INTERVAL '30 days'
    AND h.hist_event_type_id = 2  -- View events
GROUP BY
    u.user_name, u.site_role
ORDER BY
    active_days_30d DESC;

-- Identify Creator license candidates
-- Users with Explorer who are creating content
SELECT
    u.user_name,
    u.site_role,
    COUNT(DISTINCT w.workbook_id) as workbooks_owned,
    COUNT(DISTINCT ds.datasource_id) as datasources_owned
FROM
    users u
    LEFT JOIN workbooks w ON u.user_id = w.owner_id
    LEFT JOIN datasources ds ON u.user_id = ds.owner_id
WHERE
    u.site_role = 'Explorer'
    AND (w.workbook_id IS NOT NULL OR ds.datasource_id IS NOT NULL)
GROUP BY
    u.user_name, u.site_role
HAVING
    COUNT(DISTINCT w.workbook_id) > 5 OR COUNT(DISTINCT ds.datasource_id) > 3;
```

### 7.2 Power BI Service Cost Optimization

```yaml
powerbi_pricing:

  # User-Based (Per-User)
  per_user_licenses:
    pro:
      price_per_user_per_month: 10
      limitations:
        - 10 GB per user
        - 8 refreshes per day
        - No paginated reports
        - 1 GB dataset limit

    premium_per_user:
      price_per_user_per_month: 20
      capabilities:
        - 100 GB per user
        - 48 refreshes per day
        - Paginated reports
        - Larger dataset limits
        - Deployment pipelines

  # Capacity-Based (Premium)
  premium_capacity:
    p1:
      price_per_month: 4995
      v_cores: 8
      memory_gb: 25
      max_parallel_refreshes: 6
      recommended_users: 500-1000

    p2:
      price_per_month: 9995
      v_cores: 16
      memory_gb: 50
      max_parallel_refreshes: 12
      recommended_users: 1000-2000

    p3:
      price_per_month: 19995
      v_cores: 32
      memory_gb: 100
      max_parallel_refreshes: 24
      recommended_users: 2000-4000

  # Embedded Analytics (Azure)
  power_bi_embedded:
    a1:
      price_per_hour: 1.00
      v_cores: 1
      memory_gb: 3
      use_case: Development/Testing

    a4:
      price_per_hour: 4.00
      v_cores: 8
      memory_gb: 25
      use_case: Production (small)

  # Cost Optimization Strategies
  optimization:
    license_optimization:
      - Convert Pro to Free for view-only users (if Premium)
      - Use Premium Per User for power users only
      - Expected savings: 30-50%

    capacity_optimization:
      - Auto-pause Premium capacity during off-hours
      - Use Embedded A SKUs with auto-scaling
      - Consolidate workspaces to fewer capacities
      - Expected savings: 20-40%

    data_optimization:
      - Implement incremental refresh
      - Use aggregations (Premium)
      - Optimize data models
      - Expected savings: 10-20% (refresh time)
```

**Cost Calculator:**

```python
def calculate_powerbi_cost(user_breakdown, capacity_needed):
    """
    Calculate Power BI Service costs
    """

    # Per-User Licensing
    per_user_cost = (
        user_breakdown['pro'] * 10 +
        user_breakdown['premium_per_user'] * 20
    )

    # Premium Capacity (monthly)
    capacity_costs = {
        'P1': 4995,
        'P2': 9995,
        'P3': 19995,
        'P4': 39990,
        'P5': 79990
    }

    capacity_cost = capacity_costs.get(capacity_needed, 0)

    # Embedded (hourly, assuming 730 hours/month)
    embedded_costs = {
        'A1': 1.00 * 730,
        'A2': 2.00 * 730,
        'A3': 3.00 * 730,
        'A4': 4.00 * 730,
        'A5': 8.00 * 730,
        'A6': 16.00 * 730
    }

    # Calculate total
    total_monthly = per_user_cost + capacity_cost

    # Recommendations
    recommendations = []

    if user_breakdown['pro'] > 500 and capacity_needed == None:
        potential_savings = user_breakdown['pro'] * 10 - 4995
        recommendations.append(f"Consider Premium P1 capacity instead of {user_breakdown['pro']} Pro licenses. Potential savings: ${potential_savings}/month")

    if user_breakdown['premium_per_user'] > 250:
        recommendations.append("High number of Premium Per User licenses. Evaluate if Premium capacity is more cost-effective.")

    return {
        'total_monthly_cost': total_monthly,
        'per_user_cost': per_user_cost,
        'capacity_cost': capacity_cost,
        'annual_cost': total_monthly * 12,
        'recommendations': recommendations
    }

# Example
users = {
    'pro': 300,
    'premium_per_user': 50
}

costs = calculate_powerbi_cost(users, 'P1')
print(f"Total Monthly Cost: ${costs['total_monthly_cost']:,.2f}")
print(f"Annual Cost: ${costs['annual_cost']:,.2f}")
```

---

## Migration Checklists

### 8.1 Pre-Migration Checklist

```markdown
## Cloud BI Migration Pre-Flight Checklist

### Business Readiness
- [ ] Executive sponsorship secured
- [ ] Business case approved (ROI, benefits)
- [ ] Budget allocated (licensing, services, training)
- [ ] Timeline agreed upon
- [ ] Success criteria defined
- [ ] Risk assessment completed
- [ ] Communication plan created

### Technical Readiness
- [ ] Current environment documented
- [ ] Cloud platform selected
- [ ] Licensing procured
- [ ] Network connectivity verified
- [ ] Data gateway deployed (if needed)
- [ ] Authentication configured (SAML/SSO)
- [ ] Security requirements validated
- [ ] Compliance review completed

### Team Readiness
- [ ] Migration team assembled
- [ ] Roles and responsibilities assigned
- [ ] Training plan created
- [ ] Support model defined
- [ ] Change management plan in place
- [ ] User champions identified
- [ ] Knowledge transfer plan

### Content Readiness
- [ ] Content inventory completed
- [ ] Priority reports identified
- [ ] Custom extensions reviewed
- [ ] Data source mapping done
- [ ] Dependencies documented
- [ ] Backup of current environment
- [ ] Test environment provisioned
```

### 8.2 Migration Execution Checklist

```markdown
## Tableau Server to Tableau Cloud Migration Checklist

### Week 1-2: Foundation
- [ ] Tableau Cloud site provisioned
- [ ] SAML SSO configured and tested
- [ ] User groups created in Tableau Cloud
- [ ] Projects created (matching on-prem structure)
- [ ] Tableau Bridge installed and configured
- [ ] Bridge pooling setup (for HA)
- [ ] Service account permissions configured

### Week 3-4: Pilot Migration
- [ ] 5-10 pilot workbooks selected
- [ ] Pilot users identified and trained
- [ ] Data sources migrated to Cloud
- [ ] Workbooks published to Cloud
- [ ] Permissions configured
- [ ] Extract refreshes tested
- [ ] Side-by-side comparison completed
- [ ] Pilot user feedback collected

### Week 5-8: Bulk Migration
- [ ] Batch 1: Executive dashboards
  - [ ] Content migrated
  - [ ] Validated by stakeholders
  - [ ] Performance tested
- [ ] Batch 2: Departmental reports
  - [ ] Content migrated
  - [ ] Validated by stakeholders
  - [ ] Performance tested
- [ ] Batch 3: Ad-hoc analyses
  - [ ] Content migrated
  - [ ] Validated by stakeholders
  - [ ] Performance tested

### Week 9-10: User Transition
- [ ] Training sessions conducted
- [ ] Documentation published
- [ ] Support channels established
- [ ] Parallel run period started
- [ ] Usage metrics monitored
- [ ] Issues logged and resolved

### Week 11-12: Optimization & Decommission
- [ ] Performance optimization completed
- [ ] Cost optimization implemented
- [ ] Final validation completed
- [ ] Tableau Server read-only mode
- [ ] Tableau Server decommissioned
- [ ] Post-migration review conducted
```

```markdown
## Power BI Report Server to Service Migration Checklist

### Week 1-2: Preparation
- [ ] Power BI Service tenant configured
- [ ] Azure AD authentication validated
- [ ] Power BI Pro licenses assigned
- [ ] Premium capacity provisioned (if needed)
- [ ] On-Premises Data Gateway installed
- [ ] Gateway cluster configured (for HA)
- [ ] Data source connections tested
- [ ] Workspace structure created

### Week 3-4: Pilot Migration
- [ ] 5-10 pilot reports selected
- [ ] Reports tested in latest Power BI Desktop
- [ ] Data sources reconfigured for gateway
- [ ] Reports published to Power BI Service
- [ ] Refresh schedules configured
- [ ] Row-level security validated
- [ ] Paginated reports migrated (Premium)
- [ ] Pilot user testing completed

### Week 5-10: Content Migration
- [ ] Batch 1: Finance reports
  - [ ] PBIX reports migrated
  - [ ] Paginated reports migrated
  - [ ] Datasets certified
  - [ ] UAT completed
- [ ] Batch 2: Sales & Marketing
  - [ ] PBIX reports migrated
  - [ ] Datasets certified
  - [ ] Refresh schedules configured
  - [ ] UAT completed
- [ ] Batch 3: Operations
  - [ ] PBIX reports migrated
  - [ ] Datasets certified
  - [ ] Refresh schedules configured
  - [ ] UAT completed

### Week 11-12: Transition
- [ ] User training completed
- [ ] Apps published to users
- [ ] Subscriptions configured
- [ ] Mobile apps tested
- [ ] Parallel run period
- [ ] Usage monitored
- [ ] Feedback incorporated

### Week 13-14: Decommission
- [ ] All users transitioned to Service
- [ ] Report Server set to read-only
- [ ] Final backup completed
- [ ] Report Server decommissioned
- [ ] Infrastructure freed up
- [ ] Project retrospective completed
```

### 8.3 Post-Migration Checklist

```markdown
## Post-Migration Validation & Optimization

### Immediate (Week 1)
- [ ] All reports accessible
- [ ] Data refresh schedules working
- [ ] User access verified
- [ ] Critical issues resolved
- [ ] Performance baseline established
- [ ] Cost tracking enabled

### Short-Term (Month 1)
- [ ] User adoption metrics tracked
- [ ] Performance optimization completed
- [ ] Cost optimization implemented
- [ ] Training feedback incorporated
- [ ] Documentation updated
- [ ] Support metrics reviewed

### Mid-Term (Months 2-3)
- [ ] User satisfaction survey
- [ ] Advanced features rollout
- [ ] Governance policies refined
- [ ] ROI measurement
- [ ] Lessons learned documented
- [ ] Best practices established

### Long-Term (Months 4-6)
- [ ] Continuous improvement program
- [ ] Center of Excellence established
- [ ] Self-service enablement
- [ ] Innovation roadmap
- [ ] Cloud-native features adopted
- [ ] Success metrics achieved
```

---

## Appendix

### A. Troubleshooting Guide
### B. Vendor Resources
### C. Sample Migration Scripts
### D. Cost Calculator Spreadsheet
### E. Training Materials

---

**Document Version:** 1.0
**Last Updated:** 2025-11-19
**Maintained By:** Cloud BI Migration Team
**Review Cycle:** Quarterly

---

*This guide is a living document. Please submit feedback and suggestions to the BI Center of Excellence.*
