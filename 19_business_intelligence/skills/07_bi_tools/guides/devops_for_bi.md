# DevOps for BI Guide

## CI/CD Pipeline

```
Development
   ↓
Git Commit → Trigger CI
   ↓
Automated Tests
   ├─ LookML validation
   ├─ DAX syntax check
   ├─ Data quality tests
   └─ Performance tests
   ↓
Deploy to QA
   ↓
User Acceptance Testing
   ↓
Deploy to Production
   ↓
Monitor & Alert
```

## Version Control

### Git Workflow
```bash
# Feature branch
git checkout -b feature/new-dashboard
# Make changes
git add .
git commit -m "Add sales dashboard"
git push origin feature/new-dashboard

# Pull request → Code review
# Merge to main
git checkout main
git merge feature/new-dashboard

# Tag release
git tag -a v1.0.0 -m "Release 1.0"
git push origin v1.0.0
```

### What to Version Control
```
✓ Include:
- LookML files (.lkml)
- Tableau workbooks (.twb)
- Power BI templates (.pbit)
- SQL scripts
- Documentation
- Configuration files

❌ Exclude (.gitignore):
- Data extracts (.hyper, .tde)
- Credentials
- Cache files
- User-specific settings
```

## Automated Testing

### Pre-Commit Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash

# LookML validation
lookml-tools validate --project .

# DAX formatting check
dax-formatter --check *.dax

# Run data tests
pytest tests/
```

### Continuous Integration
```yaml
# .github/workflows/bi-ci.yml
name: BI CI/CD

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Validate LookML
        run: lookml-tools validate
      
      - name: Run data tests
        run: pytest tests/
      
      - name: Check performance
        run: python scripts/perf_test.py

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Production
        run: |
          tableau-cli publish workbooks/*.twbx
```

## Deployment Strategies

### Blue-Green Deployment
```
Blue (Current):  Users → Production v1.0
Green (New):     Testing → Production v1.1

After validation:
Switch: Users → Production v1.1 (Green becomes Blue)
```

### Canary Deployment
```
99% users → Current version
1% users → New version

Monitor for issues
If stable: Gradually increase to 100%
If problems: Roll back
```

## Infrastructure as Code

### Terraform Example
```hcl
# tableau-server.tf
resource "aws_instance" "tableau_server" {
  ami           = var.tableau_ami
  instance_type = "r5.4xlarge"
  
  tags = {
    Name = "Tableau Production"
    Environment = "prod"
  }
}

resource "aws_db_instance" "tableau_repo" {
  engine         = "postgres"
  instance_class = "db.r5.large"
  allocated_storage = 100
  
  backup_retention_period = 7
  multi_az = true
}
```

## Monitoring & Observability

### Key Metrics
```python
# metrics_collector.py
metrics = {
    'dashboard_load_time_p95': dashboard_perf.p95(),
    'failed_refresh_count': refresh_log.failures.count(),
    'active_users_count': analytics.active_users(),
    'query_error_rate': errors.rate(),
    'cpu_usage_percent': system.cpu_percent(),
    'memory_usage_percent': system.memory_percent()
}

send_to_monitoring(metrics)
```

### Alerting Rules
```yaml
# alerts.yml
alerts:
  - name: HighErrorRate
    condition: error_rate > 0.05
    severity: critical
    notification: pagerduty
    
  - name: SlowDashboard
    condition: load_time_p95 > 10
    severity: warning
    notification: slack
    
  - name: FailedRefresh
    condition: failed_refreshes > 0
    severity: high
    notification: email
```

## Environment Management

### Development → QA → Production
```
Development:
- Individual workspaces
- Sample data
- Frequent changes
- Minimal governance

QA/Staging:
- Shared environment
- Full data (or representative)
- Testing and validation
- Approval process

Production:
- Published content only
- Full data
- Change control
- Monitoring and SLA
```

## Automation Scripts

### Automated Publishing
```python
# publish.py
import tableauserverclient as TSC

server = TSC.Server(server_url)
server.auth.sign_in(tableau_auth)

# Publish workbooks
for workbook_file in glob.glob('workbooks/*.twbx'):
    workbook = TSC.WorkbookItem(project_id)
    server.workbooks.publish(
        workbook,
        workbook_file,
        mode=TSC.Server.PublishMode.Overwrite
    )

print("Published successfully")
```

## Resources
- GitOps for BI: Best practices articles
- Looker CI/CD: https://cloud.google.com/looker/docs/
- Tableau REST API: https://help.tableau.com/current/api/rest_api/
