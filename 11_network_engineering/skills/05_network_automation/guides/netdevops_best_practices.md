# NetDevOps Best Practices

## Project Organization

### Directory Structure
```
network-devops/
├── .github/workflows/               # GitHub Actions
├── .gitlab-ci.yml                   # GitLab CI configuration
├── ansible/
│   ├── ansible.cfg
│   ├── playbooks/
│   ├── roles/
│   ├── inventory/
│   ├── group_vars/
│   ├── host_vars/
│   └── tasks/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   └── environments/
├── python/
│   ├── scripts/
│   ├── requirements.txt
│   └── tests/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── conftest.py
├── docs/
│   ├── README.md
│   ├── DEPLOYMENT.md
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
├── configs/
│   ├── backups/
│   ├── templates/
│   └── current/
├── scripts/
│   ├── backup.sh
│   ├── validate.sh
│   └── deploy.sh
├── .gitignore
└── Makefile
```

## Version Control Best Practices

### .gitignore
```bash
# Never commit
*.key
*.pem
secrets.yaml
.vault_pass
credentials.json
.env
.env.local

# Generated files
*.log
__pycache__/
*.pyc
.pytest_cache/
venv/
.venv/
*.tfstate
*.tfstate.backup
.terraform/
terraform.tfvars
!terraform.tfvars.example

# IDE
.vscode/
.idea/
*.sublime-*

# OS
.DS_Store
Thumbs.db
```

### Commit Message Standards
```
<type>(<scope>): <subject>

<body>

<footer>

# Example:
feat(bgp): implement BGP route aggregation

- Aggregate 10.0.0.0/8 to reduce route table size
- Implement no-export community for aggregated routes
- Document aggregation policy in runbook

Closes #234
Tested-on: router1, router2
```

### Branch Strategy
```
main (production)
  ↑
release/v1.2.0
  ↑
develop
  ↑
feature/bgp-aggregation (created from develop)
```

## Code Quality

### Linting and Validation

#### Ansible
```bash
# Lint Ansible playbooks
ansible-lint playbooks/

# Validate YAML
yamllint ansible/

# Test playbook syntax
ansible-playbook playbooks/deploy.yaml --syntax-check
```

#### Terraform
```bash
# Validate syntax
terraform validate

# Format code
terraform fmt -recursive

# Plan changes
terraform plan -out=tfplan
```

#### Python
```bash
# Code quality
pylint scripts/
flake8 scripts/

# Type checking
mypy scripts/

# Format code
black scripts/
autopep8 scripts/ -i

# Test code
pytest tests/
```

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# Check for secrets
git diff --cached | grep -i "password\|secret\|token" && {
    echo "ERROR: Secrets found in commit"
    exit 1
}

# Validate YAML
for file in $(git diff --cached --name-only | grep '\.yaml$'); do
    python3 -m yaml.safe_load "$file" || exit 1
done

# Lint Ansible
[ -d "ansible/" ] && ansible-lint ansible/ || exit 1

# Format Terraform
[ -d "terraform/" ] && terraform -chdir=terraform fmt -check -recursive || exit 1

echo "✓ Pre-commit checks passed"
exit 0
```

## Testing Strategy

### Test Pyramid
```
    /\
   /  \  E2E Tests (10%)
  /____\  Integration Tests (30%)
 /      \ Unit Tests (60%)
```

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution
- High coverage

### Integration Tests
- Test components together
- Use test devices/lab
- Verify interfaces
- Check routing protocols

### E2E Tests
- Full deployment workflow
- Production-like environment
- Comprehensive validation
- Approval gates

## Security

### Secrets Management

#### Using Ansible Vault
```bash
# Create vault
ansible-vault create secrets.yaml

# Edit vault
ansible-vault edit secrets.yaml

# Run with vault
ansible-playbook playbooks/deploy.yaml --vault-password-file .vault_pass
```

#### Using Environment Variables
```bash
# Set environment variables
export ANSIBLE_USER=$ADMIN_USER
export ANSIBLE_PASSWORD=$ADMIN_PASSWORD

# Or use CI/CD secrets
# GitLab CI: Store in Settings > CI/CD > Variables
# GitHub Actions: Store in Settings > Secrets
```

### Credential Rotation
```yaml
---
- name: Rotate credentials
  hosts: all_devices
  gather_facts: no

  tasks:
    - name: Set new password
      cisco.ios.ios_config:
        lines:
          - "username admin privilege 15 password 0 {{ new_password }}"
          - "username readonly privilege 1 password 0 {{ readonly_password }}"
        save_when: changed

    - name: Update vault
      local_action:
        module: template
        src: credentials.j2
        dest: secrets.yaml
      become_user: "{{ vault_user }}"
```

## Monitoring and Observability

### Configuration Tracking
```yaml
# Track all changes
---
- name: Configuration audit
  hosts: all_devices
  gather_facts: no

  tasks:
    - name: Get config and timestamp
      cisco.ios.ios_command:
        commands: show running-config
      register: config

    - name: Save to file with timestamp
      copy:
        content: "{{ config.stdout[0] }}"
        dest: "configs/{{ inventory_hostname }}_{{ ansible_date_time.iso8601 }}.conf"
      delegate_to: localhost

    - name: Commit to Git
      shell: |
        git add configs/{{ inventory_hostname }}_*.conf
        git commit -m "audit: config snapshot for {{ inventory_hostname }}"
        git push
      delegate_to: localhost
```

### Compliance Reporting
```python
# Generate compliance report
def generate_compliance_report(devices):
    """Generate compliance report for all devices"""

    report = {
        'generated': datetime.now().isoformat(),
        'devices': {},
        'summary': {
            'total': 0,
            'compliant': 0,
            'non_compliant': 0
        }
    }

    for device in devices:
        compliance = check_device_compliance(device)

        report['devices'][device['host']] = compliance
        report['summary']['total'] += 1

        if compliance['compliant']:
            report['summary']['compliant'] += 1
        else:
            report['summary']['non_compliant'] += 1

    # Save report
    with open('compliance_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    return report
```

## Documentation

### Code Documentation
```python
def deploy_bgp_configuration(device, asn, neighbors):
    """
    Deploy BGP configuration to device.

    Args:
        device: Device connection object
        asn: BGP Autonomous System Number
        neighbors: List of neighbor dictionaries with 'ip' and 'remote_asn'

    Returns:
        dict: Deployment status and any errors

    Raises:
        ConnectionException: If device connection fails
        ConfigurationException: If configuration deployment fails

    Example:
        >>> device = ConnectHandler(**device_params)
        >>> deploy_bgp_configuration(device, 65001, [{'ip': '10.0.0.1', 'remote_asn': 65002}])
        {'status': 'success', 'changes': 1}
    """
```

### README Standards
```markdown
# Network Automation Project

## Description
Brief description of project

## Getting Started

### Prerequisites
- Python 3.8+
- Ansible 2.9+
- Terraform 1.0+

### Installation
```bash
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

### Configuration
1. Create `inventory.yaml`
2. Set environment variables
3. Configure credentials

## Usage

### Running Playbooks
```bash
ansible-playbook playbooks/deploy.yaml
```

### Running Terraform
```bash
terraform init
terraform apply
```

## Testing
```bash
pytest tests/
```

## Troubleshooting
[See TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Contributing
See CONTRIBUTING.md

## License
MIT
```

## Change Management

### Change Request Workflow
```
Feature Branch
    ↓
Pull Request (Code Review)
    ↓
Lab Testing
    ↓
Staging Deployment
    ↓
Production Approval
    ↓
Production Deployment
    ↓
Post-Deployment Validation
```

### Rollback Procedure
```yaml
---
- name: Rollback configuration
  hosts: all_devices
  gather_facts: no

  tasks:
    - name: Find latest backup
      find:
        path: "backups/"
        patterns: "{{ inventory_hostname }}_*.cfg"
        recurse: no
      register: backups

    - name: Get most recent backup
      set_fact:
        latest_backup: "{{ backups.files | sort(attribute='mtime', reverse=true) | first }}"

    - name: Restore configuration
      cisco.ios.ios_config:
        src: "{{ latest_backup.path }}"
        save_when: always

    - name: Verify restoration
      cisco.ios.ios_command:
        commands: show version
      register: verification

    - name: Log rollback
      debug:
        msg: "Rollback completed on {{ inventory_hostname }}"
```

## Performance Optimization

### Parallel Execution
```yaml
---
- name: Deploy to multiple devices
  hosts: all_devices
  serial: 5  # 5 devices at a time

  tasks:
    - name: Deploy configuration
      ansible.builtin.include_role:
        name: base_config
```

### Caching
```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_device_interfaces(device_ip):
    """Cache interface data for 5 minutes"""
    # Get interfaces from device
    pass
```

## Disaster Recovery

### Backup Strategy
- Daily automated backups
- Weekly snapshots
- Monthly archives
- Off-site replication
- Tested restore procedures

### Recovery Testing
```bash
#!/bin/bash
# scripts/test_recovery.sh

# Simulate device failure
echo "Testing recovery from backup..."

# Restore configuration
ansible-playbook playbooks/restore.yaml

# Verify functionality
python tests/post_restore_validation.py

echo "✓ Recovery test completed"
```

## Continuous Improvement

### Metrics to Track
- Deployment success rate
- Mean time to recovery (MTTR)
- Configuration change frequency
- Test coverage percentage
- Automation coverage

### Lessons Learned
```markdown
# Deployment #456

## What Went Well
- Configuration validation caught errors before deployment
- Team collaboration was smooth
- Rollback procedure was quick

## What Could Improve
- Better communication with operations
- More comprehensive testing
- Clearer change documentation

## Action Items
- [ ] Implement additional monitoring
- [ ] Improve test coverage
- [ ] Document common issues
```

## Tool Integration

### Popular Combinations
```
Ansible + Git + GitLab CI → Configuration Management Pipeline
Terraform + GitHub + Actions → Infrastructure Provisioning Pipeline
Nornir + Python + pytest → Advanced Automation Framework
PyATS + CI/CD → Automated Network Testing
```

## Training and Onboarding

### Documentation Checklist
- [ ] Architecture diagram
- [ ] Installation guide
- [ ] Usage examples
- [ ] Troubleshooting guide
- [ ] Developer guide
- [ ] Runbook procedures
- [ ] Change log/release notes

---

**Last Updated**: 2025-11-19
**Key Principles**: Automate everything, test thoroughly, document clearly, improve continuously
