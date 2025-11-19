# DevOps & Site Reliability Engineering (SRE)

**Elite professional practices for continuous delivery, infrastructure automation, observability, and reliability engineering**

---

## 🎯 Domain Overview

This domain provides comprehensive, production-grade knowledge and practices for DevOps and Site Reliability Engineering, based on industry leaders like Google, Netflix, Amazon, Microsoft, Spotify, and other technology pioneers.

### What This Domain Covers

- **CI/CD Pipelines**: Automated software delivery from commit to production
- **Infrastructure as Code**: Declarative, version-controlled infrastructure management
- **Configuration Management**: Automated, consistent system configuration
- **Monitoring & Observability**: Metrics, logs, traces, and alerting for system insights
- **Incident Management**: Structured response, mitigation, and learning from failures
- **Capacity Planning**: Resource forecasting, optimization, and performance engineering
- **Release Engineering**: Deployment strategies, rollbacks, and progressive delivery
- **GitOps**: Git as source of truth for declarative infrastructure and applications
- **Platform Engineering**: Internal developer platforms and self-service infrastructure
- **Chaos Engineering**: Proactive resilience testing through controlled failure injection

---

## 📚 Repository Structure

```
05_devops_sre/
├── skill.md                          # Core DevOps & SRE expertise
├── README.md                         # This file
│
├── standards/                        # Domain-specific standards
│   ├── style-guides/                # DevOps documentation and code standards
│   ├── api-guides/                  # API design for DevOps tools
│   ├── legacy-integration-guides/   # Migration from legacy systems
│   ├── evidence/                    # Research, benchmarks, case studies
│   └── patterns/                    # Common DevOps & SRE patterns
│
└── skills/                          # 10 specialized subskills
    ├── 01_cicd_pipelines/
    ├── 02_infrastructure_as_code/
    ├── 03_configuration_management/
    ├── 04_monitoring_observability/
    ├── 05_incident_management/
    ├── 06_capacity_planning/
    ├── 07_release_engineering/
    ├── 08_gitops/
    ├── 09_platform_engineering/
    └── 10_chaos_engineering/
```

---

## 🚀 Core Competencies

### Site Reliability Engineering (SRE)

Based on Google's SRE model, this domain covers:

**Service Level Objectives (SLOs)**
- Defining measurable reliability targets (availability, latency, error rate)
- Setting SLIs (Service Level Indicators) that matter to users
- Calculating and managing error budgets
- Balancing reliability with feature velocity

**Toil Reduction**
- Identifying automatable operational work
- Building self-service platforms
- Creating runbook automation
- Target: <50% time on toil, >50% on engineering projects

**Incident Management**
- Structured incident response with defined roles
- Blameless post-mortems and organizational learning
- On-call best practices and sustainable rotations
- Incident metrics: MTTD, MTTR, incident frequency

### DevOps Practices

**CALMS Framework**
- **C**ulture: Collaboration, shared ownership, psychological safety
- **A**utomation: CI/CD, infrastructure, testing, deployment
- **L**ean: Small batches, WIP limits, value stream optimization
- **M**easurement: Metrics-driven decisions, observability
- **S**haring: Knowledge sharing, documentation, learning culture

**DORA Metrics** (Key Performance Indicators)
- **Deployment Frequency**: How often you deploy to production
- **Lead Time for Changes**: Time from commit to production
- **Change Failure Rate**: Percentage of deployments causing issues
- **Time to Restore Service**: How quickly you recover from incidents

**Elite Performance Targets**
- Deploy on-demand (multiple deploys per day)
- Lead time < 1 hour
- Change failure rate < 15%
- MTTR < 1 hour

---

## 🛠️ Technology Stack

### CI/CD & Automation
- **Jenkins**: Open-source automation server, extensible plugins
- **GitLab CI/CD**: Integrated with GitLab, YAML pipelines
- **GitHub Actions**: Native GitHub automation, marketplace ecosystem
- **CircleCI**: Cloud-native CI/CD
- **ArgoCD**: GitOps continuous delivery for Kubernetes
- **Tekton**: Kubernetes-native CI/CD building blocks
- **Spinnaker**: Multi-cloud continuous delivery (Netflix)

### Infrastructure as Code
- **Terraform**: Multi-cloud infrastructure provisioning (HashiCorp)
- **Pulumi**: IaC using TypeScript, Python, Go, C#
- **CloudFormation**: AWS native infrastructure templates
- **Ansible**: Configuration management and automation
- **Crossplane**: Kubernetes-native infrastructure management
- **Helm**: Kubernetes package manager

### Observability & Monitoring
- **Prometheus**: Open-source metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Datadog**: Unified metrics, logs, traces (commercial)
- **New Relic**: Application performance monitoring
- **Elastic Stack (ELK)**: Elasticsearch, Logstash, Kibana for logs
- **Jaeger**: Distributed tracing (CNCF project)
- **Honeycomb**: Observability platform for debugging production

### Incident Management
- **PagerDuty**: On-call scheduling, alerting, escalation
- **Opsgenie**: Incident management and team collaboration
- **VictorOps/Splunk On-Call**: Incident response platform
- **Statuspage**: External status communication
- **Slack/Microsoft Teams**: War room coordination

### Container & Orchestration
- **Docker**: Container runtime and packaging
- **Kubernetes**: Container orchestration at scale
- **containerd**: Industry-standard container runtime
- **Helm**: Kubernetes application packaging
- **Istio**: Service mesh for traffic, security, observability
- **Linkerd**: Lightweight service mesh

### Secrets & Security
- **HashiCorp Vault**: Centralized secrets management
- **AWS Secrets Manager**: Cloud-native secrets for AWS
- **Azure Key Vault**: Azure secrets management
- **Google Secret Manager**: GCP secrets management
- **Sealed Secrets**: Encrypted Kubernetes secrets in Git
- **SOPS**: Secrets encrypted in version control

### Chaos Engineering
- **Gremlin**: Enterprise chaos engineering platform
- **Chaos Mesh**: Kubernetes-native chaos orchestrator
- **Litmus Chaos**: Cloud-native chaos framework (CNCF)
- **AWS Fault Injection Simulator**: Managed chaos for AWS
- **Chaos Monkey**: Netflix's instance termination tool

---

## 📖 Subskills Deep Dive

### 1. CI/CD Pipelines (`skills/01_cicd_pipelines/`)

**What you'll learn:**
- Pipeline architecture and design patterns
- Build automation and artifact management
- Automated testing strategies (unit, integration, E2E)
- Deployment automation and rollback procedures
- Pipeline security and compliance scanning
- Multi-stage pipelines (dev → staging → prod)

**Key technologies:** Jenkins, GitLab CI, GitHub Actions, CircleCI, ArgoCD, Tekton

**Use cases:**
- Automating application builds and deployments
- Implementing trunk-based development workflows
- Setting up quality gates and security scanning
- Creating reusable pipeline templates

---

### 2. Infrastructure as Code (`skills/02_infrastructure_as_code/`)

**What you'll learn:**
- IaC principles: declarative, idempotent, versioned
- Terraform fundamentals and advanced patterns
- State management and remote backends
- Module design and composition
- Multi-cloud and hybrid cloud strategies
- Testing infrastructure code

**Key technologies:** Terraform, Pulumi, CloudFormation, Ansible, Crossplane

**Use cases:**
- Provisioning cloud infrastructure (AWS, Azure, GCP)
- Managing Kubernetes clusters and resources
- Creating reusable infrastructure modules
- Implementing policy as code (OPA, Sentinel)

---

### 3. Configuration Management (`skills/03_configuration_management/`)

**What you'll learn:**
- Configuration management patterns and anti-patterns
- Environment-specific configurations (dev, staging, prod)
- Secrets management and rotation
- Feature flags and progressive rollouts
- Configuration validation and testing
- 12-factor app configuration principles

**Key technologies:** Ansible, Chef, Puppet, Consul, Vault, LaunchDarkly

**Use cases:**
- Managing server and application configurations
- Implementing secure secrets management
- Rolling out configuration changes safely
- Feature flag strategies

---

### 4. Monitoring & Observability (`skills/04_monitoring_observability/`)

**What you'll learn:**
- Three pillars: metrics, logs, traces
- Prometheus and Grafana ecosystem
- Distributed tracing in microservices
- SLI/SLO/SLA definitions and monitoring
- Alert design and on-call best practices
- Observability-driven development

**Key technologies:** Prometheus, Grafana, Datadog, ELK Stack, Jaeger, Loki

**Use cases:**
- Building comprehensive monitoring dashboards
- Implementing distributed tracing
- Setting up SLO-based alerting
- Creating effective on-call runbooks

---

### 5. Incident Management (`skills/05_incident_management/`)

**What you'll learn:**
- Incident response framework and roles
- Severity classification and escalation
- War room coordination and communication
- Blameless post-mortem process
- Incident metrics and continuous improvement
- On-call rotation best practices

**Key technologies:** PagerDuty, Opsgenie, Statuspage, Slack, Zoom

**Use cases:**
- Responding to production incidents effectively
- Conducting blameless post-mortems
- Building sustainable on-call rotations
- Improving MTTR and reducing incident frequency

---

### 6. Capacity Planning (`skills/06_capacity_planning/`)

**What you'll learn:**
- Demand forecasting and growth modeling
- Resource utilization analysis
- Load testing strategies (stress, soak, spike)
- Auto-scaling patterns and configuration
- Cost optimization and right-sizing
- Performance engineering principles

**Key technologies:** k6, JMeter, Gatling, Locust, AWS Auto Scaling, Kubernetes HPA

**Use cases:**
- Planning for traffic growth and seasonal spikes
- Optimizing cloud costs
- Validating system capacity before launches
- Implementing effective auto-scaling

---

### 7. Release Engineering (`skills/07_release_engineering/`)

**What you'll learn:**
- Deployment strategies (blue-green, canary, rolling)
- Progressive delivery and feature flags
- Rollback procedures and safety mechanisms
- Release trains and versioning strategies
- Database migration patterns
- Zero-downtime deployment techniques

**Key technologies:** Spinnaker, ArgoCD, Flagger, LaunchDarkly, Flyway, Liquibase

**Use cases:**
- Implementing canary deployments
- Rolling out changes with feature flags
- Managing database schema migrations
- Coordinating multi-service releases

---

### 8. GitOps (`skills/08_gitops/`)

**What you'll learn:**
- GitOps principles and workflows
- Git as single source of truth
- Pull-based deployment models
- Environment promotion strategies
- Drift detection and reconciliation
- Multi-cluster management

**Key technologies:** ArgoCD, Flux, Rancher Fleet, Tekton

**Use cases:**
- Implementing GitOps for Kubernetes
- Managing infrastructure through Git
- Automating environment synchronization
- Multi-cluster application deployment

---

### 9. Platform Engineering (`skills/09_platform_engineering/`)

**What you'll learn:**
- Internal Developer Platform (IDP) design
- Self-service infrastructure provisioning
- Developer portal implementation (Backstage)
- Golden paths and paved roads
- Platform API design
- Developer experience (DevEx) optimization

**Key technologies:** Backstage, Crossplane, Terraform Cloud, Kubernetes Operators

**Use cases:**
- Building internal developer platforms
- Creating self-service database provisioning
- Implementing service catalogs
- Reducing developer cognitive load

---

### 10. Chaos Engineering (`skills/10_chaos_engineering/`)

**What you'll learn:**
- Chaos engineering principles (Netflix model)
- Experiment design and execution
- Failure injection techniques
- Steady-state hypothesis definition
- GameDay exercises and war games
- Building resilient systems

**Key technologies:** Gremlin, Chaos Mesh, Litmus Chaos, AWS FIS, Chaos Monkey

**Use cases:**
- Testing system resilience proactively
- Validating disaster recovery procedures
- Building confidence in production systems
- Identifying hidden failure modes

---

## 📊 Key Frameworks & Models

### 1. Google SRE Model
- **Error Budgets**: Quantify acceptable unreliability
- **Toil Budget**: Limit operational work to 50%
- **SLO-Based Alerting**: Alert on user impact, not symptoms
- **Blameless Culture**: Learn from failures without blame

### 2. DORA Research
- **Four Key Metrics**: Deployment frequency, lead time, change failure rate, MTTR
- **Capabilities**: Technical, process, and cultural practices that drive performance
- **Performance Clusters**: Elite, high, medium, low performers

### 3. Three Ways of DevOps
- **First Way (Flow)**: Fast, smooth flow from dev to production
- **Second Way (Feedback)**: Amplify feedback loops at all stages
- **Third Way (Learning)**: Culture of continuous experimentation and learning

### 4. Infrastructure as Code Maturity
- **Level 1**: Scripts and manual processes
- **Level 2**: Basic automation with some IaC
- **Level 3**: Comprehensive IaC with CI/CD
- **Level 4**: Self-service platforms with policy as code

---

## 🎓 Learning Path

### Beginner (0-6 months)
1. Start with **CI/CD Pipelines**: Understand automated builds and deployments
2. Learn **Infrastructure as Code**: Terraform basics for cloud provisioning
3. Explore **Monitoring & Observability**: Set up metrics and dashboards
4. Practice **Incident Management**: Learn incident response fundamentals

**Projects:**
- Build a CI/CD pipeline for a simple application
- Provision cloud infrastructure with Terraform
- Set up monitoring and alerting for an application
- Simulate and respond to a practice incident

### Intermediate (6-18 months)
1. Deep dive into **Configuration Management**: Ansible, Vault, feature flags
2. Master **Release Engineering**: Canary deployments, feature flags
3. Learn **GitOps**: Implement ArgoCD or Flux
4. Study **Capacity Planning**: Load testing and auto-scaling

**Projects:**
- Implement GitOps for Kubernetes applications
- Set up blue-green or canary deployments
- Conduct load testing and optimize for scale
- Build a secrets management solution

### Advanced (18+ months)
1. **Platform Engineering**: Build internal developer platforms
2. **Chaos Engineering**: Implement chaos experiments
3. **Advanced Observability**: Distributed tracing, custom metrics
4. **Multi-Cloud**: Terraform across AWS, Azure, GCP

**Projects:**
- Build a self-service platform with Backstage
- Implement chaos engineering experiments
- Design and monitor SLOs for critical services
- Optimize cloud costs across multiple providers

---

## 🏆 Industry Best Practices

### From Google SRE
- Measure everything with SLIs and SLOs
- Use error budgets to balance velocity and stability
- Eliminate toil through automation
- Conduct blameless post-mortems
- On-call should be sustainable (<25% pages requiring action)

### From Netflix
- Chaos engineering in production builds confidence
- Freedom and responsibility culture
- Full-cycle developers own their services
- Regional evacuation and disaster recovery testing

### From Amazon
- Two-pizza teams with end-to-end ownership
- Everything fails all the time, design for failure
- Automate operations through APIs and tools
- Measure everything, optimize continuously

### From Microsoft
- DevOps is a cultural transformation, not just tools
- Inner source: share code and practices across the organization
- Shift left: security, testing, feedback early in the cycle
- Developer velocity drives business outcomes

---

## 📈 Success Metrics

### Technical Metrics
- **Deployment Frequency**: Multiple times per day (elite), weekly (high)
- **Lead Time**: < 1 hour (elite), 1 day to 1 week (high)
- **Change Failure Rate**: < 15% (elite), < 30% (high)
- **MTTR**: < 1 hour (elite), < 1 day (high)
- **Availability**: 99.9%+ for critical services
- **Incident Frequency**: Decreasing trend over time

### Operational Metrics
- **Toil Percentage**: < 50% of SRE time
- **On-Call Burden**: < 25% pages requiring immediate action
- **Automation Coverage**: > 80% of deployments automated
- **Post-Mortem Completion**: 100% of SEV-1/SEV-2 incidents

### Business Metrics
- **Time to Market**: Faster feature delivery
- **Customer Satisfaction**: Improved uptime and performance
- **Cost Efficiency**: Optimized cloud spending
- **Team Productivity**: Developer velocity and satisfaction

---

## 🛡️ Security & Compliance

### DevSecOps Practices
- Shift security left: integrate in CI/CD pipeline
- Automated security scanning (SAST, DAST, dependencies, containers)
- Secrets management: never commit credentials
- Policy as code: enforce standards programmatically
- Compliance as code: automate audits

### Tools
- **SAST**: SonarQube, Checkmarx, Semgrep
- **DAST**: OWASP ZAP, Burp Suite
- **Container Scanning**: Trivy, Snyk, Aqua, Clair
- **Secrets Detection**: GitGuardian, TruffleHog, Gitleaks
- **Policy Enforcement**: OPA, Sentinel, Kyverno

---

## 📚 Recommended Resources

### Books (Tier-1)
- **"Site Reliability Engineering"** (Google) - SRE fundamentals
- **"The Site Reliability Workbook"** (Google) - Practical SRE implementation
- **"The DevOps Handbook"** - Comprehensive DevOps practices
- **"Accelerate"** (Nicole Forsgren, Jez Humble, Gene Kim) - DORA research
- **"The Phoenix Project"** - DevOps transformation story
- **"Release It!"** (Michael Nygard) - Designing resilient systems
- **"Infrastructure as Code"** (Kief Morris) - IaC patterns and practices

### Engineering Blogs
- **Netflix Tech Blog**: https://netflixtechblog.com/ - Chaos engineering, cloud architecture
- **Google Cloud Blog**: https://cloud.google.com/blog - SRE, Kubernetes, GCP
- **AWS Architecture Blog**: https://aws.amazon.com/blogs/architecture/ - Well-Architected patterns
- **Uber Engineering**: https://eng.uber.com/ - Platform engineering, reliability
- **LinkedIn Engineering**: https://engineering.linkedin.com/ - Infrastructure, SRE
- **Spotify Engineering**: https://engineering.atspotify.com/ - Platform, Backstage
- **HashiCorp Blog**: https://www.hashicorp.com/blog - Terraform, Vault, infrastructure

### Online Platforms
- **DORA DevOps Research**: https://dora.dev/ - State of DevOps reports
- **SRE Weekly Newsletter**: https://sreweekly.com/ - Curated SRE content
- **DevOps Roadmap**: https://roadmap.sh/devops - Learning paths
- **CNCF Landscape**: https://landscape.cncf.io/ - Cloud-native tools ecosystem

### Certifications
- **AWS Certified DevOps Engineer - Professional**
- **Google Professional Cloud DevOps Engineer**
- **Microsoft Certified: DevOps Engineer Expert**
- **Certified Kubernetes Administrator (CKA)**
- **HashiCorp Certified: Terraform Associate**

---

## 🚀 Getting Started

### 1. Assess Your Current State
- What's your deployment frequency and lead time?
- How do you handle incidents and outages?
- Is your infrastructure defined as code?
- What observability do you have in place?

### 2. Set Goals
- Define target DORA metrics
- Identify pain points (slow deployments, frequent incidents, manual toil)
- Set SLOs for critical services
- Plan infrastructure automation roadmap

### 3. Choose Your Path
- **Need CI/CD?** → Start with `skills/01_cicd_pipelines/`
- **Managing infrastructure?** → Explore `skills/02_infrastructure_as_code/`
- **Frequent incidents?** → Learn `skills/05_incident_management/`
- **Visibility gaps?** → Dive into `skills/04_monitoring_observability/`
- **Building a platform?** → Check out `skills/09_platform_engineering/`

### 4. Implement Incrementally
- Start with quick wins: automate one manual process
- Build observability before optimizing
- Automate testing before deploying more frequently
- Iterate based on metrics and feedback

### 5. Measure & Improve
- Track DORA metrics over time
- Conduct regular retrospectives
- Share learnings across teams
- Continuously automate toil

---

## 🤝 Contributing

To enhance this domain:

1. **Add Real-World Examples**: Share production patterns that worked
2. **Update Tool References**: Keep technology stack current
3. **Include Case Studies**: Document successful transformations
4. **Expand Standards**: Add organization-specific guidelines
5. **Create Templates**: Runbooks, post-mortem templates, SLO definitions

---

## 📞 Support & Community

### Internal Resources
- Explore each subskill directory for detailed guides
- Review `standards/` for organizational patterns
- Check `evidence/` for research and case studies

### External Communities
- **SREcon**: https://www.usenix.org/conferences/byname/925 - SRE conference
- **DevOps Days**: https://devopsdays.org/ - Local DevOps events
- **CNCF Slack**: https://slack.cncf.io/ - Cloud-native community
- **Reddit r/devops**: Community discussions and Q&A
- **Kubernetes Slack**: https://slack.k8s.io/ - K8s community

---

## 📜 License

This skill domain follows elite professional practices from publicly available sources and industry leaders. Content is curated for educational and professional development purposes.

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Domain Expert Level**: Elite Professional (FAANG + Tier-1 Organizations)
**Coverage**: 10 comprehensive subskills across the DevOps & SRE landscape
**Quality Standard**: Production-grade, battle-tested practices

---

**Ready to build reliable, scalable systems with elite DevOps & SRE practices?**

Start exploring the subskills or dive into `skill.md` for comprehensive domain expertise.
