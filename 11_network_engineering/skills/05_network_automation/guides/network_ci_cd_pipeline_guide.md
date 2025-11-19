# Network CI/CD Pipeline Guide

## Pipeline Stages

### Stage 1: Validation
```yaml
validate:
  stage: validate
  script:
    - ansible-lint ansible/
    - yamllint ansible/
    - terraform validate terraform/
    - python -m py_compile python/scripts/*.py
  artifacts:
    reports:
      sast: lint-report.json
```

### Stage 2: Unit Tests
```yaml
unit_test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/unit -v --cov=.
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Stage 3: Lab Deployment
```yaml
deploy_lab:
  stage: deploy
  script:
    - ansible-playbook -i inventory/lab playbooks/deploy.yaml
  environment:
    name: lab
  only:
    - merge_requests
```

### Stage 4: Integration Tests
```yaml
integration_test:
  stage: test
  script:
    - pytest tests/integration -v
  environment:
    name: lab
  only:
    - merge_requests
  dependencies:
    - deploy_lab
```

### Stage 5: Staging Deployment
```yaml
deploy_staging:
  stage: deploy_staging
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yaml
  when: manual
  environment:
    name: staging
  only:
    - develop
```

### Stage 6: Smoke Tests
```yaml
smoke_test:
  stage: test
  script:
    - python scripts/smoke_tests.py --environment staging
  environment:
    name: staging
  only:
    - develop
  dependencies:
    - deploy_staging
```

### Stage 7: Production Approval
```yaml
approve_production:
  stage: approval
  script:
    - echo "Awaiting manual approval for production deployment"
  when: manual
  only:
    - main
```

### Stage 8: Production Deployment
```yaml
deploy_production:
  stage: deploy_production
  script:
    - ansible-playbook -i inventory/prod playbooks/deploy.yaml
  environment:
    name: production
  only:
    - main
  dependencies:
    - approve_production
```

## Complete Pipeline Example

### GitLab CI Configuration
```yaml
image: ansible:latest

variables:
  ANSIBLE_HOST_KEY_CHECKING: "False"
  TERRAFORM_VERSION: "1.5.0"

stages:
  - validate
  - build
  - test_lab
  - test_staging
  - deploy_staging
  - approval
  - deploy_prod

before_script:
  - pip install --upgrade pip
  - pip install -r requirements.txt

validate_ansible:
  stage: validate
  script:
    - ansible-lint --version
    - ansible-lint ansible/
    - yamllint ansible/
  allow_failure: false

validate_terraform:
  stage: validate
  image: hashicorp/terraform:latest
  script:
    - terraform -chdir=terraform validate
    - terraform -chdir=terraform fmt -check -recursive

validate_python:
  stage: validate
  script:
    - python -m py_compile python/scripts/*.py
    - pylint python/scripts/ --exit-zero
    - pytest python/tests -v --collect-only

build_artifacts:
  stage: build
  script:
    - mkdir -p build/configs
    - ansible-playbook -i inventory/lab playbooks/generate_configs.yaml
    - cp -r configs/* build/configs/
  artifacts:
    paths:
      - build/
    expire_in: 1 day

deploy_lab:
  stage: test_lab
  script:
    - ansible-playbook -i inventory/lab playbooks/deploy.yaml --check
    - ansible-playbook -i inventory/lab playbooks/deploy.yaml
  environment:
    name: lab
  only:
    - merge_requests

test_lab:
  stage: test_lab
  script:
    - pytest python/tests/lab_tests.py -v
    - python scripts/validate_lab.py
  artifacts:
    reports:
      junit: test-results.xml
  dependencies:
    - deploy_lab

deploy_staging:
  stage: deploy_staging
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yaml
  environment:
    name: staging
    url: https://staging.example.com
  when: manual
  only:
    - develop

test_staging:
  stage: test_staging
  script:
    - pytest python/tests/integration_tests.py -v -m staging
    - python scripts/validate_staging.py
  environment:
    name: staging
  only:
    - develop
  dependencies:
    - deploy_staging

approve_prod:
  stage: approval
  script:
    - echo "Production deployment ready. Awaiting approval."
  when: manual
  only:
    - main

deploy_prod:
  stage: deploy_prod
  script:
    - ansible-playbook -i inventory/prod playbooks/pre_deployment_checks.yaml
    - ansible-playbook -i inventory/prod playbooks/deploy.yaml
    - ansible-playbook -i inventory/prod playbooks/post_deployment_checks.yaml
  environment:
    name: production
    url: https://prod.example.com
  when: manual
  only:
    - main

notify_success:
  stage: .post
  script:
    - echo "Deployment successful to $CI_ENVIRONMENT_NAME"
    - curl -X POST https://slack.example.com/webhook -d "Deployment successful"
  when: on_success
  only:
    - main

notify_failure:
  stage: .post
  script:
    - echo "Deployment failed in stage $CI_JOB_NAME"
    - curl -X POST https://slack.example.com/webhook -d "Deployment failed"
  when: on_failure
```

## Pre-Deployment Checks

### Script Implementation
```python
#!/usr/bin/env python3
# scripts/pre_deployment_checks.py

import sys
import subprocess
from netmiko import ConnectHandler

def check_device_connectivity(devices):
    """Verify all devices are reachable"""
    print("Checking device connectivity...")
    for device_params in devices:
        try:
            net_connect = ConnectHandler(**device_params)
            net_connect.disconnect()
            print(f"✓ {device_params['host']} is reachable")
        except Exception as e:
            print(f"✗ {device_params['host']} is unreachable: {e}")
            return False
    return True

def check_disk_space(devices):
    """Verify sufficient disk space"""
    print("\nChecking disk space...")
    for device in devices:
        # Get device's available space
        # Implementation depends on device type
        print(f"✓ {device} has sufficient space")
    return True

def check_memory_available(devices):
    """Verify sufficient memory"""
    print("\nChecking available memory...")
    # Implementation details
    return True

def main():
    devices = [
        {'device_type': 'cisco_ios', 'host': '192.168.1.1', 'username': 'admin', 'password': 'pass'},
        {'device_type': 'cisco_ios', 'host': '192.168.1.2', 'username': 'admin', 'password': 'pass'},
    ]

    checks = [
        ('Connectivity', check_device_connectivity),
        ('Disk Space', check_disk_space),
        ('Memory', check_memory_available),
    ]

    failed = False
    for check_name, check_func in checks:
        try:
            if not check_func(devices):
                print(f"✗ {check_name} check failed")
                failed = True
        except Exception as e:
            print(f"✗ {check_name} check error: {e}")
            failed = True

    if failed:
        print("\n✗ Pre-deployment checks failed")
        sys.exit(1)
    else:
        print("\n✓ All pre-deployment checks passed")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

## Post-Deployment Validation

### Implementation
```python
#!/usr/bin/env python3
# scripts/post_deployment_checks.py

from napalm import get_network_driver
import json

def validate_configuration(device_ip):
    """Validate deployed configuration"""
    driver = get_network_driver('ios')
    device = driver(device_ip, 'admin', 'password')
    device.open()

    # Check interfaces are up
    interfaces = device.get_interfaces()
    for intf_name, intf_data in interfaces.items():
        if not intf_data['is_up']:
            print(f"✗ {intf_name} is down")
            return False

    # Check routing neighbors
    bgp = device.get_bgp_neighbors_detail()
    for neighbor_ip, neighbor_data in bgp['default']['peers'].items():
        if neighbor_data['session_state'] != 'Established':
            print(f"✗ BGP neighbor {neighbor_ip} not established")
            return False

    device.close()
    return True

def main():
    devices = ['192.168.1.1', '192.168.1.2']

    print("Running post-deployment validation...")
    all_valid = True

    for device_ip in devices:
        if validate_configuration(device_ip):
            print(f"✓ {device_ip} validation passed")
        else:
            print(f"✗ {device_ip} validation failed")
            all_valid = False

    if all_valid:
        print("\n✓ All post-deployment validations passed")
    else:
        print("\n✗ Some validations failed")
        exit(1)

if __name__ == '__main__':
    main()
```

## Rollback Procedures

### Automated Rollback
```yaml
rollback:
  stage: .post
  script:
    - ansible-playbook playbooks/rollback.yaml
  when: manual
  environment:
    name: production
    action: rollback
  only:
    - main
```

### Rollback Playbook
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
      register: backup_files

    - name: Get latest backup
      set_fact:
        latest_backup: "{{ backup_files.files | sort(attribute='mtime', reverse=true) | first }}"

    - name: Restore configuration
      cisco.ios.ios_config:
        src: "{{ latest_backup.path }}"
        save_when: always

    - name: Verify rollback
      cisco.ios.ios_command:
        commands: show version
      register: version

    - name: Confirm rollback success
      assert:
        that:
          - version.stdout[0] is defined
        fail_msg: "Rollback verification failed"

    - name: Notify rollback completion
      debug:
        msg: "Rollback completed on {{ inventory_hostname }}"
```

## Security Integration

### Secret Management
```yaml
deploy_prod:
  stage: deploy_prod
  script:
    - echo $ANSIBLE_VAULT_PASSWORD | ansible-vault decrypt secrets.yaml
    - ansible-playbook -i inventory/prod playbooks/deploy.yaml
  environment:
    name: production
  only:
    - main
```

### Compliance Scanning
```yaml
security_scan:
  stage: validate
  script:
    - pip install bandit
    - bandit -r python/scripts/ -f json -o bandit-report.json
    - bandit -r python/scripts/
  artifacts:
    reports:
      sast: bandit-report.json
```

---

**Last Updated**: 2025-11-19
**Reference**: gitlab.com/help/ci/cd, docs.github.com/en/actions
