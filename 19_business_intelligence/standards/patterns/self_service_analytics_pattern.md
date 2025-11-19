# Self-Service Analytics Pattern

## Overview

Self-service analytics enables business users to explore data, create reports, and derive insights independently without heavy reliance on data teams. This pattern balances democratization with governance, ensuring data quality, security, and consistency while empowering users.

## Core Principles

1. **Governed Flexibility**: Freedom within guardrails
2. **Discoverability**: Easy-to-find, well-documented data
3. **Trust**: Certified, validated data sources
4. **Enablement**: Training and support systems
5. **Scalability**: Infrastructure that grows with adoption

## Architecture Components

### 1. Data Catalog
- Asset discovery and search
- Metadata management
- Lineage tracking
- Data quality indicators
- Usage analytics

### 2. Semantic Layer
- Business-friendly terminology
- Pre-joined data models
- Certified metrics
- Row-level security

### 3. Access Control
- Role-based permissions
- Column/row-level security
- Dynamic data masking
- Audit logging

### 4. User Enablement
- Documentation and training
- Templates and examples
- Community forums
- Expert support channels

## Implementation Patterns

### Data Catalog Implementation

#### Using Atlan

```yaml
# atlan_config.yml
version: 1.0

# Asset configuration
assets:
  - type: table
    source: snowflake
    database: ANALYTICS
    schema: CORE
    table: DIM_CUSTOMERS

    metadata:
      display_name: "Customer Dimension"
      description: |
        Central customer dimension table containing all customer attributes.
        Updated daily at 2 AM UTC via dbt pipeline.

      business_glossary:
        domain: "Customer Analytics"
        subdomain: "Customer Master Data"

      tags:
        - certified
        - pii
        - daily-refresh

      custom_metadata:
        data_owner: "Customer Analytics Team"
        business_owner: "VP of Sales"
        sla: "99.9% availability"
        retention_policy: "7 years"
        pii_fields: ["email", "phone_number", "address"]

      quality_rules:
        - name: "Primary key uniqueness"
          column: customer_id
          rule: unique
          severity: critical

        - name: "Email format validation"
          column: email
          rule: regex
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
          severity: high

        - name: "Null check critical fields"
          columns: [customer_id, created_date, customer_status]
          rule: not_null
          severity: critical

        - name: "Referential integrity"
          column: country_code
          reference_table: DIM_COUNTRIES
          reference_column: country_code
          severity: medium

  - type: dashboard
    source: tableau
    workbook: "Executive Dashboard"

    metadata:
      description: "Executive KPI dashboard with revenue, customer, and operational metrics"
      refresh_schedule: "Hourly"
      data_sources:
        - ANALYTICS.CORE.FCT_ORDERS
        - ANALYTICS.CORE.DIM_CUSTOMERS
        - ANALYTICS.CORE.DIM_PRODUCTS

      certified: true
      certification_date: "2024-01-15"
      certified_by: "Analytics Governance Committee"

# Glossary terms
glossary:
  - term: "Active Customer"
    definition: "A customer who has made at least one purchase in the last 90 days"
    related_terms: ["Customer", "Churn", "Retention"]
    business_owner: "Customer Success Team"

  - term: "Monthly Recurring Revenue (MRR)"
    definition: "Predictable revenue generated from subscription products on a monthly basis"
    calculation: "SUM(subscription_amount) WHERE billing_frequency = 'monthly'"
    related_metrics: ["ARR", "Revenue", "Subscription Revenue"]
    business_owner: "Finance Team"

# Data lineage
lineage:
  - source: RAW.SALESFORCE.ACCOUNTS
    transformations:
      - type: dbt_model
        model: staging.stg_salesforce__accounts
        description: "Basic cleaning and type casting"

      - type: dbt_model
        model: intermediate.int_customers__joined
        description: "Join with contact and subscription data"

      - type: dbt_model
        model: core.dim_customers
        description: "Final customer dimension with business logic"

    destination: ANALYTICS.CORE.DIM_CUSTOMERS

# Access policies
access_policies:
  - asset_pattern: "ANALYTICS.CORE.*"
    roles: ["analyst", "data_scientist"]
    permissions: ["read", "query"]

  - asset_pattern: "*.FCT_REVENUE*"
    roles: ["finance", "executive"]
    permissions: ["read", "query", "export"]
    row_filters:
      - column: region
        user_attribute: allowed_regions

  - asset_pattern: "*"
    columns_containing: ["email", "ssn", "phone"]
    data_masking:
      type: "hash"
      algorithm: "SHA256"
      exceptions_roles: ["compliance_admin"]
```

#### Programmatic Catalog Management

```python
# catalog_manager.py
from atlan import AtlanClient, Asset, Glossary, CustomMetadata
from typing import List, Dict

class DataCatalogManager:
    """Manage data catalog operations programmatically"""

    def __init__(self, api_key: str, base_url: str):
        self.client = AtlanClient(api_key=api_key, base_url=base_url)

    def register_table(
        self,
        database: str,
        schema: str,
        table: str,
        metadata: Dict
    ) -> Asset:
        """Register or update a table in the catalog"""

        asset = Asset.creator(
            name=f"{database}.{schema}.{table}",
            type_name="Table",
            connection_qualified_name=metadata.get("connection"),
        )

        # Set basic metadata
        asset.description = metadata.get("description")
        asset.user_description = metadata.get("user_description")
        asset.certificate_status = "VERIFIED" if metadata.get("certified") else None

        # Add tags
        if tags := metadata.get("tags"):
            asset.tags = tags

        # Add custom metadata
        if custom_meta := metadata.get("custom_metadata"):
            asset.custom_metadata = CustomMetadata(
                business_owner=custom_meta.get("business_owner"),
                data_owner=custom_meta.get("data_owner"),
                sla=custom_meta.get("sla"),
                pii_fields=custom_meta.get("pii_fields", [])
            )

        # Save to catalog
        response = self.client.save(asset)

        # Add to collections
        if collections := metadata.get("collections"):
            for collection in collections:
                self.add_to_collection(response.guid, collection)

        return response

    def add_quality_rules(
        self,
        asset_guid: str,
        rules: List[Dict]
    ):
        """Add data quality rules to an asset"""

        for rule in rules:
            quality_rule = {
                "name": rule["name"],
                "type": rule["rule"],
                "severity": rule.get("severity", "medium"),
                "parameters": rule.get("parameters", {})
            }

            self.client.quality.create_rule(
                asset_guid=asset_guid,
                rule=quality_rule
            )

    def track_lineage(
        self,
        source_guid: str,
        target_guid: str,
        process_name: str,
        process_type: str = "dbt"
    ):
        """Track data lineage between assets"""

        lineage = {
            "typeName": "Process",
            "attributes": {
                "name": process_name,
                "processType": process_type,
                "inputs": [{"guid": source_guid}],
                "outputs": [{"guid": target_guid}]
            }
        }

        return self.client.save(lineage)

    def search_assets(
        self,
        query: str,
        filters: Dict = None,
        limit: int = 100
    ) -> List[Asset]:
        """Search catalog for assets"""

        search_params = {
            "query": query,
            "size": limit,
            "from": 0
        }

        if filters:
            search_params["filters"] = filters

        results = self.client.search(search_params)
        return results.entities

    def get_popular_assets(
        self,
        asset_type: str = None,
        limit: int = 10,
        days: int = 30
    ) -> List[Dict]:
        """Get most queried/viewed assets"""

        usage_query = f"""
        SELECT
            asset_guid,
            asset_name,
            asset_type,
            COUNT(*) as query_count,
            COUNT(DISTINCT user_guid) as unique_users
        FROM analytics.catalog_usage_logs
        WHERE event_date >= CURRENT_DATE - INTERVAL '{days} days'
        """

        if asset_type:
            usage_query += f" AND asset_type = '{asset_type}'"

        usage_query += f"""
        GROUP BY asset_guid, asset_name, asset_type
        ORDER BY query_count DESC
        LIMIT {limit}
        """

        return self.client.query(usage_query)
```

### Self-Service BI Tool Configuration

#### Tableau Governance

```xml
<!-- tableau_server_config.xml -->
<configuration>
  <!-- Project structure for organization -->
  <projects>
    <project name="Certified Content">
      <description>Verified dashboards and data sources</description>
      <permissions>
        <grant role="Viewer" group="All Users"/>
        <grant role="Publisher" group="Analytics Team"/>
      </permissions>
      <certification_required>true</certification_required>
    </project>

    <project name="Sandbox">
      <description>Exploratory analysis and draft work</description>
      <permissions>
        <grant role="Publisher" group="All Users"/>
      </permissions>
      <auto_cleanup_days>90</auto_cleanup_days>
    </project>

    <project name="Departmental">
      <description>Department-specific analytics</description>
      <subprojects>
        <project name="Sales"/>
        <project name="Marketing"/>
        <project name="Finance"/>
        <project name="Operations"/>
      </subprojects>
    </project>
  </projects>

  <!-- Data source governance -->
  <data_sources>
    <certified_sources>
      <source name="Customer Data Warehouse">
        <connection>
          <server>snowflake.company.com</server>
          <database>ANALYTICS</database>
          <schema>CORE</schema>
        </connection>
        <refresh_schedule>Hourly</refresh_schedule>
        <extract_optimization>true</extract_optimization>
        <row_level_security>
          <filter>
            [Region] = USERNAME()
          </filter>
        </row_level_security>
      </source>
    </certified_sources>

    <templates>
      <template name="Standard Sales Dashboard">
        <data_source>Customer Data Warehouse</data_source>
        <worksheets>
          <worksheet name="Revenue Trend"/>
          <worksheet name="Top Products"/>
          <worksheet name="Regional Performance"/>
        </worksheets>
      </template>
    </templates>
  </data_sources>

  <!-- Governance policies -->
  <governance>
    <extract_limits>
      <max_rows>10000000</max_rows>
      <max_size_gb>5</max_size_gb>
    </extract_limits>

    <certification_workflow>
      <required_fields>
        <field>Description</field>
        <field>Data Owner</field>
        <field>Update Frequency</field>
      </required_fields>
      <approval_required>true</approval_required>
      <approvers group="Analytics Governance"/>
    </certification_workflow>

    <content_lifecycle>
      <unused_content_days>180</unused_content_days>
      <notification_days_before>30</notification_days_before>
      <auto_archive>false</auto_archive>
    </content_lifecycle>
  </governance>
</configuration>
```

#### Power BI Governance

```powershell
# power_bi_governance.ps1

# Connect to Power BI Service
Connect-PowerBIServiceAccount

# Configure workspace settings
function Set-WorkspaceGovernance {
    param(
        [string]$WorkspaceName,
        [string]$Type  # "Certified", "Sandbox", "Departmental"
    )

    $workspace = Get-PowerBIWorkspace -Name $WorkspaceName

    switch ($Type) {
        "Certified" {
            # Strict governance for certified content
            Set-PowerBIWorkspace -Id $workspace.Id -Settings @{
                "OnPremisesDataGatewayRequired" = $true
                "DataflowStorageAccountRequired" = $true
                "AllowFreeLicense" = $false
                "AllowSaveAsTemplate" = $false
                "ContributorsCanPublish" = $false
            }

            # Add certification metadata
            Set-PowerBIWorkspaceMetadata -Id $workspace.Id -Metadata @{
                "Certified" = $true
                "CertificationDate" = (Get-Date).ToString("yyyy-MM-dd")
                "DataOwner" = "Analytics Team"
            }
        }

        "Sandbox" {
            # Flexible settings for experimentation
            Set-PowerBIWorkspace -Id $workspace.Id -Settings @{
                "AllowFreeLicense" = $true
                "AllowSaveAsTemplate" = $true
                "ContributorsCanPublish" = $true
            }

            # Set auto-cleanup
            Set-WorkspaceRetention -Id $workspace.Id -Days 90
        }

        "Departmental" {
            # Balanced governance
            Set-PowerBIWorkspace -Id $workspace.Id -Settings @{
                "OnPremisesDataGatewayRequired" = $true
                "ContributorsCanPublish" = $true
            }
        }
    }
}

# Dataset certification workflow
function Submit-DatasetCertification {
    param(
        [string]$DatasetId,
        [hashtable]$Metadata
    )

    # Validation checks
    $dataset = Get-PowerBIDataset -Id $DatasetId

    $validationResults = @{
        "HasDescription" = -not [string]::IsNullOrEmpty($dataset.Description)
        "HasTags" = $dataset.Tags.Count -gt 0
        "HasOwner" = -not [string]::IsNullOrEmpty($Metadata.DataOwner)
        "RefreshConfigured" = $null -ne $dataset.RefreshSchedule
        "RLSConfigured" = Test-RLSConfiguration -DatasetId $DatasetId
    }

    if ($validationResults.Values -contains $false) {
        Write-Error "Dataset does not meet certification requirements"
        return $validationResults
    }

    # Submit for approval
    $approval = New-ApprovalRequest -Type "DatasetCertification" -Metadata $Metadata

    return @{
        "Status" = "Pending Approval"
        "ApprovalId" = $approval.Id
        "ValidationResults" = $validationResults
    }
}

# Row-level security configuration
function Set-DatasetRLS {
    param(
        [string]$DatasetId,
        [string]$TableName,
        [string]$RoleFilter
    )

    $dataset = Get-PowerBIDataset -Id $DatasetId

    # Create RLS role
    $role = @{
        "name" = "DynamicRegionFilter"
        "modelPermission" = "read"
        "tablePermissions" = @(
            @{
                "name" = $TableName
                "filterExpression" = $RoleFilter
            }
        )
    }

    Add-PowerBIDatasetRole -DatasetId $DatasetId -Role $role

    # Map users to roles based on attributes
    $users = Get-AzureADUsers -Filter "Department eq 'Sales'"

    foreach ($user in $users) {
        $region = Get-UserAttribute -UserId $user.Id -Attribute "Region"

        Add-PowerBIDatasetRoleMember `
            -DatasetId $DatasetId `
            -RoleName "DynamicRegionFilter" `
            -EmailAddress $user.UserPrincipalName `
            -Identity $user.Id
    }
}

# Usage monitoring and optimization
function Get-WorkspaceUsageReport {
    param(
        [string]$WorkspaceId,
        [int]$Days = 30
    )

    $startDate = (Get-Date).AddDays(-$Days)

    $activities = Get-PowerBIActivityEvent `
        -StartDateTime $startDate `
        -EndDateTime (Get-Date) `
        | Where-Object { $_.WorkspaceId -eq $WorkspaceId }

    $report = @{
        "TotalViews" = ($activities | Where-Object { $_.Activity -eq "ViewReport" }).Count
        "UniqueUsers" = ($activities | Select-Object -Unique UserId).Count
        "MostViewedReports" = $activities `
            | Group-Object ReportId `
            | Sort-Object Count -Descending `
            | Select-Object -First 10 Name, Count
        "PeakUsageHours" = $activities `
            | Group-Object { $_.CreationTime.Hour } `
            | Sort-Object Count -Descending `
            | Select-Object -First 5 Name, Count
        "UnusedReports" = Get-PowerBIReport -WorkspaceId $WorkspaceId `
            | Where-Object {
                $reportId = $_.Id
                ($activities | Where-Object { $_.ReportId -eq $reportId }).Count -eq 0
            }
    }

    return $report
}
```

### Self-Service Maturity Model

```yaml
# maturity_assessment.yml
maturity_model:
  name: "Self-Service Analytics Maturity Model"
  version: "2.0"

  levels:
    level_1_initial:
      name: "Initial / Ad-hoc"
      description: "Analytics requests go through centralized team"

      characteristics:
        - "All reports created by central BI team"
        - "Long queue times for new requests"
        - "Limited data access for business users"
        - "No standardized metrics"
        - "Heavy Excel usage"

      capabilities:
        data_access: "Restricted to IT/BI team"
        tools: "Excel, email-based requests"
        governance: "None or informal"
        training: "None"
        support: "Ad-hoc"

      metrics:
        request_fulfillment_time: "> 2 weeks"
        user_satisfaction: "< 50%"
        self_service_adoption: "< 10%"

    level_2_managed:
      name: "Managed / Repeatable"
      description: "Some self-service capabilities with governance"

      characteristics:
        - "Business users have read access to data warehouse"
        - "Standard BI tool deployment"
        - "Template dashboards available"
        - "Basic data dictionary"
        - "Some metric definitions documented"

      capabilities:
        data_access: "Read-only to curated datasets"
        tools: "Tableau/Power BI with templates"
        governance: "Basic policies documented"
        training: "Onboarding sessions"
        support: "Help desk tickets"

      requirements:
        - implement_data_catalog: true
        - create_certified_datasets: true
        - establish_governance_committee: true
        - deploy_bi_tools: true

      metrics:
        request_fulfillment_time: "1-2 weeks"
        user_satisfaction: "50-70%"
        self_service_adoption: "10-30%"

    level_3_defined:
      name: "Defined / Standardized"
      description: "Robust self-service with clear governance"

      characteristics:
        - "Comprehensive data catalog"
        - "Certified metrics layer"
        - "Role-based access control"
        - "Regular training programs"
        - "Data quality monitoring"
        - "Usage analytics"

      capabilities:
        data_access: "Governed self-service with semantic layer"
        tools: "Full BI suite with governance"
        governance: "Comprehensive policies, enforced"
        training: "Regular workshops, certification program"
        support: "Dedicated analytics support team"

      requirements:
        - semantic_layer_implemented: true
        - row_level_security: true
        - automated_quality_checks: true
        - usage_monitoring: true
        - community_of_practice: true

      metrics:
        request_fulfillment_time: "< 1 week (or self-served)"
        user_satisfaction: "70-85%"
        self_service_adoption: "30-60%"
        certified_assets_ratio: "> 50%"

    level_4_quantitatively_managed:
      name: "Quantitatively Managed / Measured"
      description: "Data-driven optimization of self-service"

      characteristics:
        - "AI-powered recommendations"
        - "Automated data quality enforcement"
        - "Predictive governance"
        - "Advanced lineage tracking"
        - "Impact analysis"
        - "Cost optimization"

      capabilities:
        data_access: "Dynamic with intelligent recommendations"
        tools: "Integrated platform with AI assistance"
        governance: "Automated policy enforcement"
        training: "Personalized learning paths"
        support: "Proactive support with usage prediction"

      requirements:
        - ai_metadata_generation: true
        - automated_lineage_tracking: true
        - impact_analysis: true
        - cost_attribution: true
        - predictive_usage_analytics: true

      metrics:
        request_fulfillment_time: "Instant (self-served)"
        user_satisfaction: "85-95%"
        self_service_adoption: "60-80%"
        certified_assets_ratio: "> 75%"
        cost_per_query: "Tracked and optimized"

    level_5_optimizing:
      name: "Optimizing / Innovative"
      description: "Continuous innovation and improvement"

      characteristics:
        - "Fully autonomous self-service"
        - "Natural language queries"
        - "Automated insight generation"
        - "Embedded analytics everywhere"
        - "Real-time governance"
        - "Continuous optimization"

      capabilities:
        data_access: "Unrestricted with intelligent guardrails"
        tools: "Unified analytics platform with NLQ"
        governance: "Self-healing, adaptive policies"
        training: "AI-powered just-in-time learning"
        support: "Predictive, automated resolution"

      metrics:
        request_fulfillment_time: "Instant"
        user_satisfaction: "> 95%"
        self_service_adoption: "> 80%"
        certified_assets_ratio: "> 90%"
        automation_rate: "> 80%"

# Assessment framework
assessment:
  dimensions:
    - name: "Data Access & Discovery"
      questions:
        - "Can users easily find relevant datasets?"
        - "Is there a searchable data catalog?"
        - "Are datasets documented with business context?"
        - "Is data lineage visible to users?"

    - name: "Governance & Security"
      questions:
        - "Are access controls clearly defined and enforced?"
        - "Is sensitive data automatically protected?"
        - "Are there certified vs uncertified data tiers?"
        - "Is there an audit trail of data access?"

    - name: "User Enablement"
      questions:
        - "Are training programs available?"
        - "Is there a community for knowledge sharing?"
        - "Are templates and examples provided?"
        - "Is support readily available?"

    - name: "Metrics & Standards"
      questions:
        - "Are business metrics centrally defined?"
        - "Is there a metrics layer or semantic model?"
        - "Are naming conventions standardized?"
        - "Are KPIs consistently calculated?"

    - name: "Tools & Technology"
      questions:
        - "Are modern BI tools deployed?"
        - "Is there a unified analytics platform?"
        - "Are tools integrated with governance?"
        - "Is performance optimized?"

  scoring:
    method: "weighted_average"
    weights:
      data_access: 0.25
      governance: 0.30
      enablement: 0.20
      metrics: 0.15
      tools: 0.10
```

### User Training Program

```markdown
# Self-Service Analytics Training Curriculum

## Level 1: Foundation (All Users)

### Module 1: Data Literacy Basics
- Understanding data types and structures
- Reading and interpreting charts
- Common statistical concepts
- Data quality and trust indicators

**Duration**: 2 hours
**Format**: Online course
**Assessment**: Quiz

### Module 2: Data Catalog Navigation
- Finding datasets
- Understanding metadata
- Identifying certified vs uncertified content
- Requesting access

**Duration**: 1 hour
**Format**: Interactive tutorial
**Assessment**: Practical exercise

### Module 3: Dashboard Consumption
- Navigating dashboards
- Applying filters
- Exporting data
- Asking questions about data

**Duration**: 1.5 hours
**Format**: Hands-on workshop
**Assessment**: Create filtered view

## Level 2: Creator (Analysts, Power Users)

### Module 4: BI Tool Training
- Connecting to data sources
- Creating visualizations
- Building dashboards
- Best practices for design

**Duration**: 8 hours (2 days)
**Format**: Instructor-led workshop
**Assessment**: Build sample dashboard

### Module 5: Semantic Layer & Metrics
- Using certified metrics
- Understanding business logic
- Creating calculations
- Metric governance

**Duration**: 3 hours
**Format**: Hands-on workshop
**Assessment**: Build metric-driven report

### Module 6: Governance & Publishing
- Certification process
- Documentation requirements
- Sharing and permissions
- Lifecycle management

**Duration**: 2 hours
**Format**: Online course
**Assessment**: Submit sample for certification

## Level 3: Advanced (Analytics Engineers)

### Module 7: Advanced Analytics
- Statistical functions
- Predictive analytics
- Cohort analysis
- Funnel analysis

**Duration**: 12 hours (3 days)
**Format**: Hands-on workshop
**Assessment**: Complex analysis project

### Module 8: Performance Optimization
- Query optimization
- Extract vs live connections
- Aggregation strategies
- Monitoring usage

**Duration**: 4 hours
**Format**: Technical workshop
**Assessment**: Optimization exercise

## Certification Paths

### Data Consumer Certification
- Complete Level 1 modules
- Pass assessment (80% minimum)
- Demonstrate dashboard usage

### Analytics Creator Certification
- Complete Level 1-2 modules
- Build 3 certified dashboards
- Peer review participation

### Analytics Expert Certification
- Complete all modules
- Lead 2 training sessions
- Contribute to governance
- Mentorship of 3 users
```

## Monitoring and Success Metrics

```python
# analytics_platform_metrics.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict

@dataclass
class PlatformMetrics:
    """Track self-service analytics platform health"""

    # Adoption metrics
    total_users: int
    active_users_30d: int
    new_users_30d: int
    power_users: int  # Created 10+ reports

    # Content metrics
    total_dashboards: int
    certified_dashboards: int
    avg_dashboards_per_user: float
    orphaned_content: int  # Not viewed in 90 days

    # Usage metrics
    total_queries_30d: int
    avg_queries_per_day: int
    peak_concurrent_users: int
    avg_query_time_seconds: float

    # Quality metrics
    data_quality_score: float  # 0-100
    user_satisfaction_score: float  # 0-10
    support_ticket_count: int
    avg_ticket_resolution_hours: float

    # Governance metrics
    policy_compliance_rate: float  # 0-100
    security_incidents: int
    audit_findings: int

    def adoption_rate(self) -> float:
        """Calculate platform adoption rate"""
        return (self.active_users_30d / self.total_users) * 100

    def content_certification_rate(self) -> float:
        """Calculate percentage of certified content"""
        return (self.certified_dashboards / self.total_dashboards) * 100

    def content_health_score(self) -> float:
        """Calculate overall content health"""
        orphan_rate = (self.orphaned_content / self.total_dashboards) * 100
        return 100 - orphan_rate

    def user_enablement_score(self) -> float:
        """Calculate user enablement effectiveness"""
        weights = {
            'satisfaction': 0.4,
            'support_efficiency': 0.3,
            'power_user_ratio': 0.3
        }

        satisfaction_norm = self.user_satisfaction_score / 10
        support_norm = 1 - min(self.avg_ticket_resolution_hours / 48, 1)
        power_user_norm = (self.power_users / self.active_users_30d)

        return (
            weights['satisfaction'] * satisfaction_norm +
            weights['support_efficiency'] * support_norm +
            weights['power_user_ratio'] * power_user_norm
        ) * 100

def generate_executive_report(metrics: PlatformMetrics) -> Dict:
    """Generate executive summary of platform health"""

    return {
        "summary": {
            "adoption_rate": f"{metrics.adoption_rate():.1f}%",
            "active_users": metrics.active_users_30d,
            "queries_per_day": metrics.avg_queries_per_day,
            "user_satisfaction": f"{metrics.user_satisfaction_score}/10"
        },
        "health_indicators": {
            "content_certification": {
                "value": f"{metrics.content_certification_rate():.1f}%",
                "status": "good" if metrics.content_certification_rate() > 60 else "needs_improvement"
            },
            "content_health": {
                "value": f"{metrics.content_health_score():.1f}%",
                "status": "good" if metrics.content_health_score() > 80 else "needs_improvement"
            },
            "enablement": {
                "value": f"{metrics.user_enablement_score():.1f}%",
                "status": "good" if metrics.user_enablement_score() > 70 else "needs_improvement"
            }
        },
        "areas_of_focus": generate_recommendations(metrics)
    }

def generate_recommendations(metrics: PlatformMetrics) -> List[str]:
    """Generate actionable recommendations"""

    recommendations = []

    if metrics.adoption_rate() < 50:
        recommendations.append(
            "Low adoption rate. Consider: enhanced training, better onboarding, or tool simplification"
        )

    if metrics.content_certification_rate() < 60:
        recommendations.append(
            "Low content certification. Implement certification workflow and incentives"
        )

    if metrics.orphaned_content > metrics.total_dashboards * 0.2:
        recommendations.append(
            "High orphaned content. Implement content lifecycle management and cleanup process"
        )

    if metrics.avg_ticket_resolution_hours > 24:
        recommendations.append(
            "Slow support response. Consider expanding support team or implementing self-service knowledge base"
        )

    if metrics.user_satisfaction_score < 7:
        recommendations.append(
            "Low user satisfaction. Conduct user interviews to identify pain points"
        )

    return recommendations
```

## Best Practices Summary

### Do's
1. **Start with governance**: Define policies before rolling out tools
2. **Invest in catalog**: Make data discoverable and trustworthy
3. **Create certification tiers**: Distinguish trusted from experimental content
4. **Provide templates**: Accelerate users with pre-built examples
5. **Monitor usage**: Track adoption and identify improvement areas
6. **Enable community**: Foster knowledge sharing among users
7. **Maintain semantic layer**: Single source of truth for metrics
8. **Automate governance**: Enforce policies through technology

### Don'ts
1. **Don't sacrifice governance for speed**: Chaos is costly
2. **Don't neglect training**: Tools without training lead to frustration
3. **Don't create data swamps**: Quality over quantity
4. **Don't ignore security**: Row-level security is essential
5. **Don't let content proliferate**: Manage lifecycle actively
6. **Don't work in isolation**: Collaborate with business stakeholders
7. **Don't forget to iterate**: Continuously improve based on feedback

## Conclusion

Successful self-service analytics requires balancing democratization with governance, investing in enablement, and continuously measuring and improving the program. The patterns and practices outlined here provide a framework for building a sustainable, scalable self-service analytics capability.
