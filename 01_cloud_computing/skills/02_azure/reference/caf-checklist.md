# Cloud Adoption Framework (CAF) Checklist

## Strategy Phase

### Define Business Justification
- [ ] Document business outcomes and objectives
- [ ] Identify stakeholders and decision makers
- [ ] Establish success criteria and KPIs
- [ ] Create financial model (TCO, ROI)
- [ ] Define timeline and milestones
- [ ] Assess current state vs desired state

### Motivations
- [ ] **Migration**: Lift-and-shift from on-premises
- [ ] **Innovation**: Cloud-native applications
- [ ] **Cost Optimization**: Reduce infrastructure costs
- [ ] **Agility**: Faster time to market
- [ ] **Scale**: Handle growth and variability
- [ ] **Security**: Improve security posture

### Expected Outcomes
- [ ] Revenue impact (new capabilities, markets)
- [ ] Cost savings (infrastructure, operations)
- [ ] Performance improvements (speed, reliability)
- [ ] Customer experience enhancements
- [ ] Employee productivity gains

## Plan Phase

### Digital Estate Assessment
- [ ] Inventory all applications and workloads
- [ ] Catalog dependencies and integrations
- [ ] Assess data sovereignty requirements
- [ ] Evaluate licensing and contracts
- [ ] Classify workloads by criticality
- [ ] Identify quick wins vs complex migrations

### Rationalization (5 Rs)
- [ ] **Rehost** (lift-and-shift): VMs to Azure
- [ ] **Refactor** (re-platform): Minimal changes (e.g., Azure SQL)
- [ ] **Rearchitect**: Significant redesign for cloud
- [ ] **Rebuild**: Rewrite as cloud-native
- [ ] **Replace**: SaaS alternatives

### Skills Readiness
- [ ] Assess current team capabilities
- [ ] Identify skill gaps
- [ ] Create training plan
- [ ] Assign cloud roles and responsibilities
- [ ] Establish center of excellence (CoE)
- [ ] Plan for managed services where needed

### Cloud Adoption Plan
- [ ] Prioritize workloads (complexity, value, risk)
- [ ] Create migration waves/sprints
- [ ] Define success criteria per workload
- [ ] Establish testing and validation process
- [ ] Plan for rollback scenarios
- [ ] Create communication plan

## Ready Phase

### Landing Zone Design
- [ ] Choose landing zone approach (Start small, Enterprise-scale)
- [ ] Define management group hierarchy
- [ ] Establish subscription strategy
- [ ] Design hub-spoke network topology
- [ ] Configure hybrid connectivity (VPN/ExpressRoute)
- [ ] Implement core services (DNS, NTP, monitoring)

### Management Group Hierarchy
```
Tenant Root Group
├── Platform
│   ├── Management (monitoring, backup)
│   ├── Connectivity (networking, VPN)
│   └── Identity (AD, RBAC)
├── Landing Zones
│   ├── Corp (internal apps)
│   └── Online (internet-facing apps)
├── Sandbox (experimentation)
└── Decommissioned
```

### Networking
- [ ] Define address space allocation (non-overlapping)
- [ ] Implement hub-spoke topology
- [ ] Configure network security (NSGs, firewall)
- [ ] Set up DNS (Azure DNS, Private DNS)
- [ ] Implement DDoS protection
- [ ] Configure network monitoring
- [ ] Plan for multi-region if needed

### Identity and Access
- [ ] Establish Azure AD as identity provider
- [ ] Configure hybrid identity (Azure AD Connect)
- [ ] Implement MFA for all users
- [ ] Set up Conditional Access policies
- [ ] Define RBAC strategy (least privilege)
- [ ] Create break-glass admin accounts
- [ ] Enable Privileged Identity Management (P2)

### Resource Organization
- [ ] Define naming conventions
- [ ] Establish tagging strategy (cost center, owner, environment)
- [ ] Create resource groups aligned with lifecycle
- [ ] Implement resource locks on production
- [ ] Document resource organization guidelines

**Naming Convention Example**:
```
Format: {resource-type}-{workload}-{environment}-{region}-{instance}

Examples:
- rg-webapp-prod-eastus-001
- vm-sqlserver-prod-eastus-001
- vnet-hub-prod-eastus-001
- law-monitoring-prod-eastus-001
```

**Tagging Strategy**:
```
Required Tags:
- Environment: dev, test, staging, prod
- CostCenter: department or project code
- Owner: email of responsible party
- Application: application name
- Criticality: low, medium, high, mission-critical
- DataClassification: public, internal, confidential, restricted
```

### Security Baseline
- [ ] Enable Microsoft Defender for Cloud
- [ ] Configure security policies
- [ ] Implement network segmentation
- [ ] Enable encryption at rest and in transit
- [ ] Set up Azure Key Vault
- [ ] Configure vulnerability scanning
- [ ] Implement security monitoring and alerting

## Govern Phase

### Azure Policy
- [ ] Define policy definitions for compliance
- [ ] Create policy initiatives (policy sets)
- [ ] Assign policies at appropriate scope
- [ ] Configure policy remediation
- [ ] Review policy compliance regularly

**Common Policies**:
```json
// Require tag on resources
{
  "if": {
    "field": "tags['Environment']",
    "exists": "false"
  },
  "then": {
    "effect": "deny"
  }
}

// Allowed VM sizes
{
  "if": {
    "allOf": [
      {"field": "type", "equals": "Microsoft.Compute/virtualMachines"},
      {"not": {"field": "Microsoft.Compute/virtualMachines/sku.name", "in": ["Standard_D2s_v3", "Standard_D4s_v3"]}}
    ]
  },
  "then": {
    "effect": "deny"
  }
}

// Require HTTPS for storage
{
  "if": {
    "allOf": [
      {"field": "type", "equals": "Microsoft.Storage/storageAccounts"},
      {"field": "Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly", "equals": "false"}
    ]
  },
  "then": {
    "effect": "deny"
  }
}
```

### Cost Management
- [ ] Set up cost budgets and alerts
- [ ] Implement cost allocation (tags, subscriptions)
- [ ] Enable Azure Advisor cost recommendations
- [ ] Review and act on cost optimization opportunities
- [ ] Implement auto-shutdown for non-production
- [ ] Use reserved instances for predictable workloads
- [ ] Monitor and optimize storage tiers

**Budget Alert Example**:
```bash
az consumption budget create \
  --budget-name MyBudget \
  --amount 10000 \
  --time-grain Monthly \
  --time-period start-date=2024-01-01 end-date=2024-12-31 \
  --notifications amount=8000 contact-emails="finance@example.com" \
  --notifications amount=10000 contact-emails="finance@example.com,cto@example.com"
```

### Regulatory Compliance
- [ ] Identify applicable regulations (GDPR, HIPAA, PCI-DSS, SOC 2)
- [ ] Map Azure controls to compliance requirements
- [ ] Implement compliance policies
- [ ] Enable compliance reporting
- [ ] Regular compliance audits
- [ ] Document compliance posture

**Compliance Frameworks in Defender for Cloud**:
- Azure Security Benchmark
- PCI-DSS 3.2.1
- ISO 27001:2013
- NIST SP 800-53 Rev. 5
- HIPAA HITRUST
- SOC 2 Type 2

### Security Governance
- [ ] Define security baselines
- [ ] Implement least privilege access
- [ ] Regular access reviews
- [ ] Security incident response plan
- [ ] Vulnerability management process
- [ ] Security training for team

## Migrate Phase

### Migration Approach
- [ ] **Assess**: Discover and assess workloads (Azure Migrate)
- [ ] **Migrate**: Execute migration (Azure Migrate, Database Migration Service)
- [ ] **Optimize**: Right-size and optimize post-migration
- [ ] **Secure**: Apply security best practices
- [ ] **Manage**: Enable monitoring and management

### Assessment Checklist
- [ ] Run Azure Migrate discovery
- [ ] Assess readiness and compatibility
- [ ] Estimate Azure costs
- [ ] Identify dependencies
- [ ] Plan for downtime windows
- [ ] Create rollback plan

### Migration Waves
**Wave 1** (Pilot - Low Risk):
- [ ] Non-production workloads
- [ ] Stateless applications
- [ ] Validate processes
- [ ] Refine runbooks

**Wave 2** (Low Complexity):
- [ ] Simple web applications
- [ ] Development/test environments
- [ ] Build confidence

**Wave 3+** (Increasing Complexity):
- [ ] Business-critical applications
- [ ] Complex dependencies
- [ ] Databases with replication
- [ ] Full production workloads

### Post-Migration
- [ ] Validate functionality
- [ ] Performance testing
- [ ] Security validation
- [ ] Update documentation
- [ ] Decommission on-premises (after validation period)
- [ ] Conduct lessons learned

## Manage Phase

### Operations Management
- [ ] Centralized monitoring (Azure Monitor, Log Analytics)
- [ ] Alerting and incident response
- [ ] Patch management (Azure Update Management)
- [ ] Backup and disaster recovery (Azure Backup, Site Recovery)
- [ ] Performance management
- [ ] Change management process

### Business Continuity and Disaster Recovery
- [ ] Define RPO/RTO for each workload
- [ ] Implement backup strategy
- [ ] Configure Azure Site Recovery where appropriate
- [ ] Regular DR testing
- [ ] Document recovery procedures
- [ ] Geographic redundancy for critical workloads

**BCDR Requirements**:
| Tier | RTO | RPO | Solution |
|------|-----|-----|----------|
| Critical | < 1 hour | < 15 min | Multi-region active-active |
| High | < 4 hours | < 1 hour | Site Recovery, Geo-redundant |
| Medium | < 24 hours | < 4 hours | Azure Backup, Site Recovery |
| Low | < 72 hours | < 24 hours | Azure Backup |

### Operational Compliance
- [ ] Regular patching schedule
- [ ] Security baseline enforcement
- [ ] Configuration drift detection
- [ ] Compliance scanning
- [ ] Audit log retention
- [ ] Access review process

## Innovate Phase

### Modern Application Development
- [ ] Containerization (AKS, Container Instances)
- [ ] Serverless (Functions, Logic Apps)
- [ ] Microservices architecture
- [ ] API-first design
- [ ] DevOps and CI/CD pipelines
- [ ] Infrastructure as Code

### Data and Analytics
- [ ] Data lake implementation (Azure Data Lake)
- [ ] Data warehouse (Synapse Analytics)
- [ ] Real-time analytics (Stream Analytics, Event Hubs)
- [ ] Business intelligence (Power BI)
- [ ] Machine learning (Azure ML)

### IoT and Edge
- [ ] IoT Hub for device management
- [ ] IoT Edge for edge computing
- [ ] Time series data storage (Time Series Insights)
- [ ] Event processing (Event Hubs, Stream Analytics)

### AI and Machine Learning
- [ ] Cognitive Services for pre-built AI
- [ ] Azure Machine Learning for custom models
- [ ] MLOps for model lifecycle management
- [ ] Responsible AI practices

## Well-Architected Framework Integration

### Reliability
- [ ] Design for failure (redundancy, failover)
- [ ] Test failure scenarios
- [ ] Implement health checks
- [ ] Use availability zones
- [ ] Multi-region for critical workloads

### Security
- [ ] Defense in depth
- [ ] Zero trust architecture
- [ ] Encrypt data at rest and in transit
- [ ] Identity as primary security perimeter
- [ ] Regular security assessments

### Cost Optimization
- [ ] Right-size resources
- [ ] Use reserved instances/savings plans
- [ ] Implement auto-scaling
- [ ] Optimize storage tiers
- [ ] Regular cost reviews

### Operational Excellence
- [ ] Infrastructure as Code
- [ ] Automated deployments
- [ ] Comprehensive monitoring
- [ ] Incident response procedures
- [ ] Regular chaos engineering

### Performance Efficiency
- [ ] Performance testing
- [ ] Scalability planning
- [ ] CDN for global content
- [ ] Caching strategies
- [ ] Database optimization

## Success Metrics

### Business Metrics
- [ ] Cost reduction percentage
- [ ] Time to market improvement
- [ ] Revenue impact
- [ ] Customer satisfaction scores
- [ ] Employee productivity gains

### Technical Metrics
- [ ] Application availability (uptime %)
- [ ] Performance (response time, throughput)
- [ ] Security incidents (reduction)
- [ ] Deployment frequency
- [ ] Mean time to recovery (MTTR)

### Cloud Maturity
- [ ] Automation level (manual vs automated)
- [ ] Policy compliance percentage
- [ ] Security score improvement
- [ ] Cost optimization realized
- [ ] Skills development progress

## Common Pitfalls to Avoid

- [ ] **Lift-and-shift everything**: Consider refactoring for cloud benefits
- [ ] **Ignoring security**: Security should be built-in, not bolted-on
- [ ] **No governance**: Implement policies early
- [ ] **Undersized network**: Plan for growth, use appropriate subnet sizes
- [ ] **No cost controls**: Set budgets and alerts from day one
- [ ] **Inadequate monitoring**: Monitor business and technical metrics
- [ ] **Neglecting training**: Invest in team skills
- [ ] **No testing**: Test migrations, DR, and failure scenarios
- [ ] **Poor documentation**: Document architecture and processes
- [ ] **Skipping assessment**: Understand current state before migrating

## Quarterly Review Checklist

- [ ] Review cost against budget
- [ ] Security posture assessment
- [ ] Policy compliance review
- [ ] Performance optimization opportunities
- [ ] Backup and DR testing
- [ ] Review and update documentation
- [ ] Team skills assessment
- [ ] Stakeholder feedback collection
- [ ] Plan next quarter priorities
