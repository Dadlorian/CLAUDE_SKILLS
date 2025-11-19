# Git-Based Network Automation Guide

## Repository Setup

### Initialize Repository
```bash
# Create new repo
git init network-automation
cd network-automation

# Clone existing repo
git clone https://gitlab.example.com/network-automation.git
cd network-automation

# Configure user
git config user.name "Network Automation"
git config user.email "network-automation@example.com"
```

### Repository Structure
```
network-automation/
├── .git/
├── .github/
│   └── workflows/                    # GitHub Actions
├── .gitlab-ci.yml                    # GitLab CI/CD
├── ansible/
│   ├── playbooks/
│   ├── roles/
│   ├── inventory/
│   └── group_vars/
├── terraform/
│   ├── modules/
│   ├── environments/
│   └── providers.tf
├── python/
│   ├── scripts/
│   ├── requirements.txt
│   └── tests/
├── docs/
│   ├── README.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── configs/
│   ├── backups/
│   ├── templates/
│   └── current/
└── .gitignore
```

### .gitignore
```bash
# Sensitive files
*.key
*.pem
*.pub
secrets.yaml
.vault_pass
.env
.env.local
credentials.json

# Temporary files
*.tmp
*.bak
*.swp
*~
.DS_Store

# Generated files
*.log
reports/
__pycache__/
*.pyc
.pytest_cache/
venv/
.venv/
node_modules/

# IDE
.vscode/
.idea/
*.sublime-*

# Terraform
*.tfstate
*.tfstate.backup
.terraform/
terraform.tfvars
override.tf

# Ansible
*.retry
!.gitkeep

# OS
.DS_Store
Thumbs.db
```

## Workflow Management

### Feature Branch Development
```bash
# Create feature branch
git checkout -b feature/ospf-configuration develop

# Make changes
vim ansible/playbooks/routing/ospf.yaml

# Stage changes
git add ansible/playbooks/routing/ospf.yaml

# Commit with descriptive message
git commit -m "feat(ospf): add OSPF configuration playbook

- Configure OSPF process on core routers
- Set router ID from loopback interface
- Add all interfaces to OSPF area 0
- Enable OSPF authentication

Closes #123"

# Push to remote
git push origin feature/ospf-configuration

# Create merge request
# (via GitLab/GitHub web interface)
```

### Code Review
```bash
# Fetch and review PR
git fetch origin pull/456/head:pr-456
git checkout pr-456

# Review the changes
git log -1 --pretty=fuller
git show

# Make local modifications if needed
git add .
git commit -m "fix: address review comments"
git push

# After approval, merge
git checkout develop
git merge pr-456
git push origin develop
```

### Release Management
```bash
# Create release branch
git checkout -b release/1.2.0 develop

# Update version
vim VERSION
git commit -m "bump: version 1.2.0"

# Create release notes
vim RELEASE_NOTES.md
git add RELEASE_NOTES.md
git commit -m "docs: add release notes for v1.2.0"

# Merge to main
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"

# Merge back to develop
git checkout develop
git merge --no-ff release/1.2.0

# Push everything
git push origin main develop --tags

# Delete release branch
git branch -d release/1.2.0
```

## Configuration as Code Pattern

### Storing Network Configs in Git

#### Ansible Playbooks in Git
```yaml
# ansible/playbooks/deploy_prod.yaml
- name: Deploy to production
  hosts: prod_routers
  gather_facts: no

  vars:
    deployment_date: "{{ ansible_date_time.iso8601 }}"

  pre_tasks:
    - name: Pre-deployment validation
      include_tasks: "../tasks/pre_checks.yaml"

  tasks:
    - name: Backup current config
      cisco.ios.ios_command:
        commands: show running-config
      register: current_config

    - name: Save backup to file
      copy:
        content: "{{ current_config.stdout[0] }}"
        dest: "backups/{{ inventory_hostname }}_{{ deployment_date }}.cfg"
      delegate_to: localhost

    - name: Deploy from Git-stored configuration
      include_role:
        name: "{{ deployment_role }}"

  post_tasks:
    - name: Post-deployment validation
      include_tasks: "../tasks/post_checks.yaml"
```

#### Terraform in Git
```hcl
# terraform/prod/main.tf
terraform {
  backend "s3" {
    bucket  = "terraform-state-prod"
    key     = "network/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

module "production_network" {
  source = "../modules/network"

  environment = "prod"
  vpc_cidr    = "10.0.0.0/16"

  subnets = {
    public-1  = { cidr = "10.0.1.0/24", availability_zone = "us-east-1a", public = true }
    public-2  = { cidr = "10.0.2.0/24", availability_zone = "us-east-1b", public = true }
    private-1 = { cidr = "10.0.10.0/24", availability_zone = "us-east-1a", public = false }
    private-2 = { cidr = "10.0.11.0/24", availability_zone = "us-east-1b", public = false }
  }
}
```

## Version Control Workflows

### Commit Message Standards
```bash
# Good commit message
git commit -m "feat(bgp): add BGP route aggregation

- Implement route aggregation for 10.0.0.0/8
- Add no-export community to aggregated routes
- Update BGP policy documentation

Closes #234
Tested-on: router1, router2"

# Bad commit message
git commit -m "update stuff"  # Too vague
git commit -m "WIP"            # Not descriptive
```

### Branching Strategy
```bash
# Feature branches
git checkout -b feature/vlan-management develop

# Bugfix branches
git checkout -b bugfix/ospf-cost-calculation develop

# Hotfix branches (from main)
git checkout -b hotfix/critical-security-fix main

# Documentation branches
git checkout -b docs/network-design develop

# Automation branches
git checkout -b automation/ci-cd-pipeline develop
```

## CI/CD Integration

### GitLab CI Configuration
```yaml
# .gitlab-ci.yml
variables:
  ANSIBLE_VAULT_PASSWORD_FILE: .vault_pass

stages:
  - validate
  - test
  - deploy_staging
  - deploy_prod

validate:
  stage: validate
  image: alpine:latest
  script:
    - apk add --no-cache python3 py3-pip
    - pip install yamllint ansible-lint
    - yamllint ansible/
    - ansible-lint ansible/
  artifacts:
    reports:
      sast: lint-report.json

test_ansible:
  stage: test
  image: ansible:latest
  script:
    - ansible-playbook -i inventory/lab playbooks/test.yaml
  only:
    - merge_requests

deploy_staging:
  stage: deploy_staging
  image: ansible:latest
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yaml
  when: manual
  only:
    - develop
  environment:
    name: staging

deploy_prod:
  stage: deploy_prod
  image: ansible:latest
  script:
    - ansible-playbook -i inventory/prod playbooks/deploy.yaml
  when: manual
  only:
    - main
  environment:
    name: production
```

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# Check for secrets
if git diff --cached | grep -i "password\|secret\|token"; then
    echo "ERROR: Secrets detected in commit"
    exit 1
fi

# Validate YAML
for file in $(git diff --cached --name-only | grep '\.yaml$'); do
    python3 -m yaml.safe_load "$file" || exit 1
done

# Lint Ansible
ansible-lint ansible/ || exit 1

echo "✓ Pre-commit checks passed"
exit 0
```

Enable the hook:
```bash
chmod +x .git/hooks/pre-commit
```

## Collaborative Workflows

### Pull Request Template
```markdown
# Pull Request: Network Configuration Update

## Description
Brief description of changes

## Related Issues
Closes #123

## Changes
- Added OSPF configuration to core routers
- Updated interface templates
- Added validation tests

## Testing
- [x] Tested on lab devices
- [x] Syntax validation passed
- [x] Configuration backup verified
- [x] Rollback plan documented

## Deployment Notes
- Requires enable password for IOS devices
- No device reboot required
- Can be deployed during business hours

## Rollback Instructions
If issues arise:
```bash
git revert <commit-hash>
ansible-playbook playbooks/rollback.yaml
```

## Reviewers
@network-team @automation-lead
```

### Merge Conflicts Resolution
```bash
# Pull latest from develop
git fetch origin
git rebase origin/develop

# If conflicts occur
git status

# Edit conflicted files
vim ansible/playbooks/conflicted_file.yaml

# Mark as resolved
git add ansible/playbooks/conflicted_file.yaml
git rebase --continue

# Push the resolved branch
git push origin feature/branch-name -f
```

## Change Tracking

### Creating Release Notes
```bash
# Generate changelog
git log --oneline v1.0.0..v1.1.0 > CHANGELOG.md

# Manual changelog
cat > CHANGELOG.md << 'EOF'
# Changelog

## [1.2.0] - 2024-11-19

### Added
- BGP route aggregation support
- Enhanced interface monitoring
- Automated VLAN provisioning

### Changed
- Updated OSPF cost calculation algorithm
- Improved logging verbosity

### Fixed
- Fixed BGP neighbor authentication issue
- Corrected interface timeout values

### Deprecated
- Legacy interface configuration method

### Removed
- Old telnet-based management

### Security
- Updated SSH cipher suites
- Enhanced access control

[1.2.0]: https://gitlab.example.com/network-automation/compare/v1.1.0...v1.2.0
EOF

git add CHANGELOG.md
git commit -m "docs: update changelog for v1.2.0"
```

### Rollback Procedures
```bash
# Soft rollback (keep changes staged)
git reset --soft HEAD~1

# Mixed rollback (unstage changes)
git reset --mixed HEAD~1

# Hard rollback (discard changes)
git reset --hard HEAD~1

# Revert commit (create new commit that undoes changes)
git revert <commit-hash>

# Cherry-pick specific commit
git cherry-pick <commit-hash>
```

## Backup and Disaster Recovery

### Config Backups in Git
```bash
#!/bin/bash
# scripts/backup_configs.sh

BACKUP_DIR="configs/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup Cisco devices
ansible-playbook playbooks/backup_cisco.yaml \
  -e "backup_dir=$BACKUP_DIR backup_date=$TIMESTAMP"

# Backup Juniper devices
ansible-playbook playbooks/backup_juniper.yaml \
  -e "backup_dir=$BACKUP_DIR backup_date=$TIMESTAMP"

# Commit backups
cd /path/to/repo
git add $BACKUP_DIR/
git commit -m "backup: automated config backup $TIMESTAMP"
git push origin backup-branch
```

## Best Practices

1. **Branch Protection Rules**
   - Require pull request reviews
   - Require CI/CD to pass
   - Dismiss stale reviews on new commits
   - Require branches to be up to date

2. **Commit Frequently**
   ```bash
   # Good: Multiple small commits
   git commit -m "feat: add interface template"
   git commit -m "test: add validation tests"
   git commit -m "docs: update interface documentation"
   ```

3. **Keep Commits Atomic**
   - One feature per commit
   - Related changes together
   - Self-contained units

4. **Use Descriptive Branches**
   ```bash
   feature/ospf-optimization      # Good
   f/ospf                          # Bad
   ```

5. **Review Before Merging**
   - Always use pull/merge requests
   - Get peer review
   - Verify CI/CD passes
   - Test in staging first

---

**Last Updated**: 2025-11-19
**Reference**: git-scm.com/docs, git-flow.readthedocs.io
