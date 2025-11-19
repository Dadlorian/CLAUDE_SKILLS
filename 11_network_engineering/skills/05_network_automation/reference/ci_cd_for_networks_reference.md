# CI/CD for Network Automation Reference

## Pipeline Architecture

### Standard Network CI/CD Pipeline
```
Code Commit
    ↓
Syntax Validation
    ↓
Linting & Style Checks
    ↓
Lab Testing
    ↓
Security Scanning
    ↓
Approval Gate
    ↓
Staging Deployment
    ↓
Staging Validation
    ↓
Production Deployment
    ↓
Production Validation
    ↓
Rollback Ready
```

## GitLab CI/CD

### Basic Pipeline
```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - staging
  - production

variables:
  ANSIBLE_LIBRARY: "./roles"

# Validation stage
validate_syntax:
  stage: validate
  image: alpine:latest
  script:
    - apk add --no-cache python3 py3-pip
    - pip3 install yamllint ansible
    - ansible-lint ansible/
    - yamllint ansible/

validate_terraform:
  stage: validate
  image: hashicorp/terraform:latest
  script:
    - terraform init -upgrade
    - terraform validate
  artifacts:
    reports:
      sast: terraform-report.json

# Test stage
test_lab:
  stage: test
  image: ansible:latest
  script:
    - ansible-playbook -i inventory/lab playbooks/test.yaml
  only:
    - merge_requests

# Staging deployment
deploy_staging:
  stage: staging
  image: ansible:latest
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yaml
  when: manual
  only:
    - develop

# Production deployment
deploy_production:
  stage: production
  image: ansible:latest
  script:
    - ansible-playbook -i inventory/prod playbooks/deploy.yaml
  when: manual
  only:
    - main
```

### Advanced Pipeline with Testing
```yaml
stages:
  - validate
  - unit_test
  - integration_test
  - staging
  - smoke_test
  - production
  - post_deploy

validate:
  stage: validate
  script:
    - ansible-lint
    - yamllint ansible/
    - terraform validate
  artifacts:
    reports:
      container_scanning: scan.json

unit_tests:
  stage: unit_test
  script:
    - python -m pytest tests/unit/ -v
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      junit: report.xml

integration_test:
  stage: integration_test
  services:
    - docker:dind
  script:
    - docker-compose -f tests/docker-compose.yml up -d
    - python -m pytest tests/integration/ -v
    - docker-compose down
  artifacts:
    reports:
      junit: integration-report.xml

deploy_staging:
  stage: staging
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yaml
  when: manual
  only:
    - develop

smoke_tests:
  stage: smoke_test
  script:
    - python scripts/smoke_tests.py --environment staging
  only:
    - develop

deploy_production:
  stage: production
  environment:
    name: production
    url: https://prod.example.com
  script:
    - ansible-playbook -i inventory/prod playbooks/deploy.yaml
  when: manual
  only:
    - main

validation_post_deploy:
  stage: post_deploy
  script:
    - python scripts/post_deployment_validation.py --environment prod
  artifacts:
    reports:
      junit: post-deploy-report.xml

rollback_production:
  stage: production
  environment:
    name: production
    action: rollback
  script:
    - ansible-playbook -i inventory/prod playbooks/rollback.yaml
  when: manual
  only:
    - main
```

## GitHub Actions

### Workflow File
```yaml
# .github/workflows/network-automation.yml
name: Network Automation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install ansible yamllint ansible-lint

      - name: Validate YAML
        run: yamllint ansible/

      - name: Lint Ansible
        run: ansible-lint ansible/

  test:
    needs: validate
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest tests/ -v --cov=./ --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2

  deploy_staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/checkout@v2

      - name: Set up Ansible
        run: |
          pip install ansible

      - name: Deploy to staging
        run: |
          ansible-playbook -i inventory/staging playbooks/deploy.yaml
        env:
          ANSIBLE_USER: ${{ secrets.ANSIBLE_USER }}
          ANSIBLE_PASSWORD: ${{ secrets.ANSIBLE_PASSWORD }}

  deploy_production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://prod.example.com
    steps:
      - uses: actions/checkout@v2

      - name: Set up Ansible
        run: |
          pip install ansible

      - name: Deploy to production
        run: |
          ansible-playbook -i inventory/prod playbooks/deploy.yaml
        env:
          ANSIBLE_USER: ${{ secrets.ANSIBLE_USER }}
          ANSIBLE_PASSWORD: ${{ secrets.ANSIBLE_PASSWORD }}
```

## Jenkins Pipeline

### Declarative Pipeline
```groovy
pipeline {
    agent any

    triggers {
        pollSCM('H */4 * * *')
        githubPush()
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
    }

    environment {
        ANSIBLE_VAULT_PASSWORD = credentials('ansible-vault-pass')
        NETBOX_API_TOKEN = credentials('netbox-api-token')
    }

    stages {
        stage('Validate') {
            steps {
                echo 'Validating code...'
                sh '''
                    pip install ansible yamllint ansible-lint
                    yamllint ansible/
                    ansible-lint ansible/
                    terraform validate terraform/
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    pip install pytest napalm netmiko
                    pytest tests/unit/ -v
                '''
            }
        }

        stage('Lab Deploy') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to lab...'
                sh '''
                    ansible-playbook -i inventory/lab playbooks/deploy.yaml
                '''
            }
        }

        stage('Staging Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to staging...'
                sh '''
                    ansible-playbook -i inventory/staging playbooks/deploy.yaml
                '''
            }
        }

        stage('Approve Production') {
            when {
                branch 'main'
            }
            steps {
                input 'Deploy to Production?'
            }
        }

        stage('Production Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                sh '''
                    ansible-playbook -i inventory/prod playbooks/deploy.yaml
                '''
            }
        }

        stage('Post-Deploy Validation') {
            steps {
                echo 'Validating deployment...'
                sh '''
                    python scripts/post_deployment_validation.py
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
            junit testResults: 'test-results.xml', allowEmptyResults: true
        }

        failure {
            mail to: 'network-team@example.com',
                 subject: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                 body: "Build failed. Check logs at ${env.BUILD_URL}"
        }

        success {
            mail to: 'network-team@example.com',
                 subject: "Build Success: ${env.JOB_NAME} ${env.BUILD_NUMBER}",
                 body: "Build successful. Details at ${env.BUILD_URL}"
        }
    }
}
```

## Pre-commit Hooks

### Local Validation
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Running pre-commit hooks..."

# Check for secrets
echo "Checking for secrets..."
if git diff --cached | grep -i "password\|secret\|token" | grep -v ".gitignore"; then
    echo -e "${RED}ERROR: Secrets found in commit!${NC}"
    exit 1
fi

# Validate YAML
echo "Validating YAML..."
for file in $(git diff --cached --name-only | grep '\.yaml$\|\.yml$'); do
    python3 -m yaml.safe_load "$file" || exit 1
done

# Validate JSON
echo "Validating JSON..."
for file in $(git diff --cached --name-only | grep '\.json$'); do
    python3 -m json.tool "$file" > /dev/null || exit 1
done

# Lint Ansible
echo "Linting Ansible..."
if [ -d "ansible/" ]; then
    ansible-lint ansible/ || exit 1
fi

# Validate Terraform
echo "Validating Terraform..."
if [ -d "terraform/" ]; then
    cd terraform/
    terraform validate || exit 1
    cd ..
fi

echo -e "${GREEN}All pre-commit checks passed!${NC}"
exit 0
```

## Integration with Change Management

### Ticket-Based Deployment
```python
import requests
from datetime import datetime

class ChangeManagement:
    def __init__(self, ticket_id, servicenow_url, credentials):
        self.ticket_id = ticket_id
        self.url = servicenow_url
        self.auth = credentials

    def create_change_record(self, description, devices):
        """Create change request in ServiceNow"""
        payload = {
            'short_description': f'Network Configuration Change: {description}',
            'description': f'Deploy configuration to {len(devices)} devices',
            'assignment_group': 'Network Team',
            'urgency': '3',
            'impact': '2'
        }

        response = requests.post(
            f'{self.url}/api/now/table/change_request',
            json=payload,
            auth=self.auth
        )

        return response.json()['result']['sys_id']

    def approve_change(self, change_id):
        """Approve change request"""
        payload = {
            'state': '2',  # Approved
            'work_notes': 'Auto-approved via CI/CD pipeline'
        }

        requests.patch(
            f'{self.url}/api/now/table/change_request/{change_id}',
            json=payload,
            auth=self.auth
        )

    def update_change_status(self, change_id, status, notes):
        """Update change status"""
        payload = {
            'state': status,
            'work_notes': notes,
            'close_notes': notes if status == '3' else ''  # Closed
        }

        requests.patch(
            f'{self.url}/api/now/table/change_request/{change_id}',
            json=payload,
            auth=self.auth
        )
```

## Rollback Strategy

### Automated Rollback
```yaml
# rollback.yaml
- name: Network Configuration Rollback
  hosts: all_devices
  gather_facts: no

  tasks:
    - name: Find latest backup
      find:
        path: backups/
        patterns: "{{ inventory_hostname }}_*.cfg"
        age: -1h
      register: latest_backup

    - name: Restore configuration
      netmiko_command:
        command_string: "copy {{ latest_backup.files[0].path }} running-config"

    - name: Verify restoration
      napalm_get:
        getters: facts
      register: post_rollback

    - name: Send notification
      mail:
        host: smtp.example.com
        to: network-team@example.com
        subject: "ROLLBACK COMPLETED: {{ inventory_hostname }}"
        body: "Configuration rolled back to {{ latest_backup.files[0].path }}"
```

---

**Last Updated**: 2025-11-19
**Reference**: gitlab.com/help/ci/cd, docs.github.com/en/actions, jenkins.io/doc
