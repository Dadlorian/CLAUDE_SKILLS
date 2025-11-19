# Git Workflows for Network Automation

## Repository Structure

### Best Practices Layout
```
network-automation/
├── .gitignore
├── README.md
├── .gitlab-ci.yml              # CI/CD pipeline
├── ansible/
│   ├── ansible.cfg
│   ├── inventory/
│   │   ├── hosts.yaml
│   │   ├── group_vars/
│   │   │   ├── routers.yaml
│   │   │   ├── switches.yaml
│   │   │   └── firewalls.yaml
│   │   └── host_vars/
│   │       ├── router1.yaml
│   │       └── switch1.yaml
│   ├── playbooks/
│   │   ├── deploy_config.yaml
│   │   ├── backup_config.yaml
│   │   ├── pre_checks.yaml
│   │   └── post_checks.yaml
│   ├── roles/
│   │   ├── base_config/
│   │   ├── routing/
│   │   ├── security/
│   │   └── monitoring/
│   └── templates/
│       ├── router_config.j2
│       └── switch_config.j2
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── vpc/
│   │   └── security_group/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── python/
│   ├── requirements.txt
│   ├── network_automation.py
│   └── tests/
│       └── test_automation.py
├── configs/
│   ├── backups/
│   ├── templates/
│   └── deploy/
├── docs/
│   ├── README.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
└── scripts/
    ├── backup_devices.sh
    ├── validate_syntax.sh
    └── rollback.sh
```

### .gitignore Best Practices
```bash
# Sensitive files
*.key
*.pem
secrets.yaml
credentials.json
.vault_pass
.env
.env.local

# Temporary files
*.tmp
*.bak
*.swp
*~
.DS_Store

# Terraform
*.tfstate
*.tfstate.backup
.terraform/
terraform.tfvars
override.tf
override.tf.json

# Ansible
*.retry
!.gitkeep

# Python
__pycache__/
*.pyc
.pytest_cache/
venv/
.venv/

# IDE
.vscode/
.idea/
*.sublime-project
*.sublime-workspace

# Generated files
reports/
*.log
```

## Branching Strategy

### Git Flow for Network Automation
```
main (production)
├── release/1.0.0
├── hotfix/urgent-firewall-rule
└── develop
    ├── feature/bgp-config
    ├── feature/interface-templating
    └── bugfix/ospf-priority
```

### Branch Naming Conventions
```
feature/description          # New features
bugfix/description          # Bug fixes
hotfix/description          # Production fixes
release/version             # Release branches
docs/description            # Documentation updates
test/description            # Testing branches
automation/description      # CI/CD improvements
```

## Commit Message Standards

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Example Network Commits
```
feat(cisco-ios): add BGP configuration for ISP peering

- Configure BGP AS 65001
- Add neighbor 10.0.0.1 remote-as 65002
- Enable NLRI for IPv4 unicast
- Set local preference to 200

Closes #123
```

```
fix(ospf): correct interface priority calculation

The priority value was not being applied correctly
on secondary interfaces due to order-of-operations.

Fixes #456
```

```
docs(ansible): add BGP playbook documentation

Added comprehensive guide for BGP configuration
including examples for multiple vendors.
```

## Merge Strategies

### Feature Branch Workflow
```bash
# Create feature branch
git checkout -b feature/new-vlan-configuration develop

# Make changes, commit frequently
git add playbooks/configure_vlans.yaml
git commit -m "feat(vlans): add VLAN configuration playbook"

# Push to remote
git push origin feature/new-vlan-configuration

# Create merge request / pull request
# Review, approve, test in CI/CD

# Merge to develop
git merge feature/new-vlan-configuration

# Delete branch
git branch -d feature/new-vlan-configuration
```

### Merge Commit vs Squash vs Rebase
```
# Merge commit (preserves branch history)
git merge feature/branch

# Squash commits (clean history)
git merge --squash feature/branch
git commit -m "Add new feature"

# Rebase (linear history)
git rebase develop
git merge feature/branch
```

**Recommendation**: Use merge commits for features, squash for bugfixes

## Tag Management

### Version Tags
```bash
# Create annotated tag
git tag -a v1.2.0 -m "Release version 1.2.0 - BGP enhancements"

# Create lightweight tag
git tag v1.2.0

# Push tags to remote
git push origin v1.2.0
git push origin --tags

# List tags
git tag -l
```

### Semantic Versioning
```
v1.2.3
│ │ └─ Patch (bugfixes, non-breaking changes)
│ └─── Minor (new features, backward compatible)
└───── Major (breaking changes)
```

### Examples
```
v1.0.0 - Initial release
v1.1.0 - Added OSPF support
v1.1.1 - Fixed BGP peer validation
v2.0.0 - Multi-vendor support (breaking changes)
```

## Collaborative Workflows

### Pull Request Template
```markdown
## Description
Brief description of changes

## Related Issues
Closes #123

## Changes Made
- Added BGP configuration
- Updated interface templates
- Added validation tests

## Testing Done
- [x] Syntax validation
- [x] Device testing
- [x] Configuration backup verified

## Deployment Notes
- Requires BGP AS number configuration
- Can be deployed during maintenance window
- No device reboot required

## Rollback Plan
- Previous configuration backed up in backups/
- Use rollback.sh to revert if needed
```

### Code Review Checklist
```markdown
## Network Code Review Checklist

- [ ] Configuration syntax is correct
- [ ] YAML/HCL formatting follows standards
- [ ] All variables are defined
- [ ] No hardcoded credentials or secrets
- [ ] Jinja2 templates render correctly
- [ ] Changes tested on lab devices
- [ ] Backup taken before changes
- [ ] Rollback plan documented
- [ ] Documentation updated
- [ ] No breaking changes to existing configs
- [ ] Follows network standards/policies
- [ ] Security review passed
```

## Continuous Integration Workflow

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for secrets
git diff --cached | grep -i "password\|secret" && \
  echo "ERROR: Secrets found in commit" && exit 1

# Validate YAML syntax
for file in $(git diff --cached --name-only | grep '\.yaml$'); do
  python -m yaml.safe_load "$file" || exit 1
done

# Validate Terraform
terraform validate || exit 1

# Run linters
ansible-lint playbooks/ || exit 1

exit 0
```

### GitLab CI Pipeline Integration
```yaml
stages:
  - validate
  - test
  - deploy

validate_syntax:
  stage: validate
  script:
    - ansible-lint playbooks/
    - yamllint ansible/
    - terraform validate terraform/

test_lab:
  stage: test
  script:
    - python -m pytest tests/
    - ansible-playbook -i ansible/inventory/lab playbooks/deploy_config.yaml --check

deploy_prod:
  stage: deploy
  script:
    - ansible-playbook -i ansible/inventory/prod playbooks/deploy_config.yaml
  when: manual
  only:
    - main
```

## History and Troubleshooting

### Viewing Commit History
```bash
# Show recent commits
git log --oneline -10

# Show changes to specific file
git log -p ansible/playbooks/deploy.yaml

# Show commits by author
git log --author="john"

# Show commits since tag
git log v1.0.0..HEAD --oneline
```

### Undoing Changes
```bash
# Undo uncommitted changes
git checkout -- playbooks/router_config.yaml

# Amend last commit
git commit --amend --no-edit

# Revert commit
git revert <commit-hash>

# Hard reset (use with caution!)
git reset --hard <commit-hash>
```

## Backup and Recovery

### Configuration Backups in Git
```bash
# Automated backup script
#!/bin/bash
for device in $(cat inventory.txt); do
  ansible-playbook backup_playbook.yaml -e "target=$device"
  git add backups/$device*.conf
  git commit -m "backup: automatic config backup for $device"
done
git push origin backup-branch
```

### Disaster Recovery
```bash
# Restore from specific commit
git show commit-hash:path/to/config > restore.conf

# Compare configurations
git diff v1.0.0 v1.0.1 -- configs/

# Find when change was made
git blame configs/router.conf
```

## Multi-Site/Team Collaboration

### Remote Management
```bash
# Add remote repository
git remote add origin https://gitlab.example.com/network-automation.git

# Fetch from remote
git fetch origin

# Pull changes
git pull origin develop

# Push changes
git push origin feature/branch
```

### Conflict Resolution
```bash
# View conflicts
git diff

# Accept all remote changes
git checkout --theirs playbooks/deploy.yaml

# Accept all local changes
git checkout --ours playbooks/deploy.yaml

# Manual resolution then commit
git add playbooks/deploy.yaml
git commit -m "resolve: merge conflict in deploy playbook"
```

---

**Last Updated**: 2025-11-19
**Best Practice**: Commit frequently, write clear messages, use branches for all work
