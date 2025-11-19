# Network Automation Subskill

## Overview

Master network automation across multiple platforms and frameworks, enabling infrastructure-as-code practices for network management, deployment, and validation.

## Core Competencies

### 1. **Ansible Network Automation**
- Network module collections (Cisco, Juniper, Arista, etc.)
- Playbooks for configuration management and deployment
- Role-based architecture for reusability
- Handlers for configuration changes
- Async operations for long-running tasks
- Network device fact gathering

### 2. **Python Network Libraries**
- **Netmiko**: Multi-vendor SSH library for command execution
- **NAPALM**: Unified API for network device interaction
- **Nornir**: Task execution framework with inventory management
- **PyATS**: Cisco's testing framework for network validation
- **Paramiko**: SSH protocol implementation
- **Requests**: RESTful API interactions with network devices

### 3. **Infrastructure as Code (IaC)**
- **Terraform**: Network resource provisioning (Cisco, Juniper, AWS VPC)
- **CloudFormation**: AWS network infrastructure
- **Ansible**: Configuration management as code
- Module development and custom providers

### 4. **Configuration Management Protocols**
- **NETCONF (RFC 6241)**: XML-based network device configuration
- **RESTCONF (RFC 8040)**: REST-based NETCONF interface
- **gRPC**: High-performance service definition
- YANG data models for device configuration

### 5. **Template-Based Configuration**
- **Jinja2**: Dynamic configuration template rendering
- Variable substitution and conditional logic
- Looping and filtering constructs
- Custom Jinja2 filters for network operations
- Configuration backup and restoration

### 6. **Network Testing & Validation**
- Pre/post deployment validation
- Connectivity testing and reachability verification
- Configuration compliance checking
- Automated regression testing
- Network state verification

### 7. **CI/CD Integration**
- **GitLab CI**: Network pipeline automation
- **Jenkins**: Network job orchestration
- **GitHub Actions**: Workflow automation for network code
- Pre-commit hooks for validation
- Automated testing gates

### 8. **Network DevOps Best Practices**
- Git-based configuration management
- Code review workflows for network changes
- Change management integration
- Network configuration backup automation
- Disaster recovery procedures
- Multi-vendor network orchestration

## Key Technologies

- **Orchestration**: Ansible, Nornir, Terraform
- **SSH/Telnet**: Netmiko, Paramiko
- **REST APIs**: Requests, Nornir, Napalm
- **Templating**: Jinja2, ERB
- **Testing**: PyATS, Network Test Automation
- **VCS**: Git, GitLab, GitHub
- **Monitoring**: Netbox Integration, Network Facts Collection
- **Container**: Docker for automation environments

## Learning Path

1. Start with **Ansible** for foundational network automation
2. Progress to **Python scripting** with Netmiko and NAPALM
3. Learn **Terraform** for infrastructure provisioning
4. Master **NETCONF/RESTCONF** for vendor-agnostic automation
5. Implement **testing frameworks** for validation
6. Build **CI/CD pipelines** for network changes
7. Adopt **DevOps practices** for network operations

## Use Cases

- **Configuration Management**: Automated device configuration across hundreds of devices
- **Deployment Automation**: Rapid deployment of new network services
- **Network Compliance**: Enforcing network policies and standards
- **Disaster Recovery**: Automated backup and restoration procedures
- **Multi-Vendor Networks**: Unified management across different vendors
- **Version Control**: Full network configuration in Git
- **Change Management**: Audited, reversible network changes
- **Scalability**: Managing network growth without manual overhead

## Directory Structure

```
05_network_automation/
├── skill.md                          # This file
├── reference/                        # Technical reference materials (12 files)
│   ├── ansible_network_modules_reference.md
│   ├── python_network_libraries_reference.md
│   ├── netconf_restconf_reference.md
│   ├── yang_models_reference.md
│   ├── terraform_network_providers.md
│   ├── network_automation_tools_comparison.md
│   ├── git_workflows_for_networks.md
│   ├── jinja2_templating_reference.md
│   ├── network_testing_frameworks.md
│   ├── ci_cd_for_networks_reference.md
│   ├── napalm_reference.md
│   └── nornir_reference.md
├── guides/                           # Practical implementation guides (12 files)
│   ├── ansible_network_automation_guide.md
│   ├── python_netmiko_guide.md
│   ├── terraform_network_infrastructure.md
│   ├── netconf_yang_implementation.md
│   ├── git_based_network_automation.md
│   ├── jinja2_config_templates_guide.md
│   ├── network_ci_cd_pipeline_guide.md
│   ├── automated_network_testing_guide.md
│   ├── napalm_configuration_guide.md
│   ├── nornir_automation_guide.md
│   ├── pyats_testing_guide.md
│   └── netdevops_best_practices.md
└── src/                              # Code examples and templates (20+ items)
    ├── ansible_cisco_playbook.yaml
    ├── ansible_juniper_playbook.yaml
    ├── ansible_roles_example/
    ├── netmiko_config_script.py
    ├── napalm_get_config.py
    ├── napalm_replace_config.py
    ├── nornir_inventory.yaml
    ├── nornir_automation_script.py
    ├── terraform_cisco_provider.tf
    ├── terraform_network_module/
    ├── netconf_get_config.py
    ├── restconf_api_client.py
    ├── jinja2_router_template.j2
    ├── jinja2_switch_template.j2
    ├── pyats_test_suite.py
    ├── network_validation_script.py
    ├── gitlab_ci_network_pipeline.yml
    ├── pre_deployment_checks.py
    ├── post_deployment_validation.py
    └── network_backup_automation.py
```

## Quick Start Commands

```bash
# Ansible network automation
ansible-playbook -i inventory playbooks/deploy_config.yaml

# Run Python network script
python netmiko_config_script.py

# Deploy infrastructure with Terraform
terraform init && terraform plan && terraform apply

# Execute Nornir tasks
python nornir_automation_script.py

# Run network tests
python pyats_test_suite.py

# Execute CI/CD pipeline
gitlab-runner exec docker deploy:network
```

## Integration Points

- **Version Control**: Git for all automation code
- **Monitoring**: Integration with network monitoring tools
- **Ticketing**: Change request tracking (ServiceNow, Jira)
- **Inventory**: NetBox, Infoblox, custom sources
- **Documentation**: Auto-generated network configuration docs
- **Compliance**: Automated compliance checking and reporting

## Practical Implementation Examples

### Example 1: Multi-Vendor Configuration Deployment

```python
# Using Nornir for multi-vendor automation
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config
from nornir_utils.plugins.functions import print_result

def deploy_acl(task):
    """Deploy access control lists across multiple vendors"""
    if task.host.platform == "cisco_ios":
        commands = [
            "ip access-list extended SECURE_ACL",
            "permit tcp any any eq 443",
            "permit tcp any any eq 80",
            "deny ip any any log"
        ]
    elif task.host.platform == "juniper_junos":
        commands = [
            "set firewall family inet filter SECURE_ACL term 1 from protocol tcp",
            "set firewall family inet filter SECURE_ACL term 1 from port 443",
            "set firewall family inet filter SECURE_ACL term 1 then accept"
        ]

    result = task.run(task=netmiko_send_config, config_commands=commands)
    return result

nr = InitNornir(config_file="config.yaml")
result = nr.run(task=deploy_acl)
print_result(result)
```

### Example 2: Pre/Post Validation with PyATS

```python
# Network state validation before and after changes
from genie.testbed import load
from genie.utils.diff import Diff

def validate_change(testbed_file, device_name):
    testbed = load(testbed_file)
    device = testbed.devices[device_name]
    device.connect()

    # Pre-change snapshot
    pre_routes = device.parse("show ip route")
    pre_interfaces = device.parse("show interfaces")

    # Make changes (placeholder)
    print("Making configuration changes...")

    # Post-change snapshot
    post_routes = device.parse("show ip route")
    post_interfaces = device.parse("show interfaces")

    # Compare
    route_diff = Diff(pre_routes, post_routes)
    route_diff.findDiff()

    if route_diff.diffs:
        print("Route changes detected:")
        print(route_diff)
    else:
        print("No route changes detected")

    device.disconnect()
```

### Example 3: GitOps Workflow for Network Changes

```yaml
# .gitlab-ci.yml for network automation
stages:
  - validate
  - test
  - deploy

validate_configs:
  stage: validate
  script:
    - python -m yamllint configs/
    - ansible-playbook --syntax-check playbooks/deploy.yml
    - terraform validate

test_in_staging:
  stage: test
  script:
    - ansible-playbook -i inventory/staging playbooks/deploy.yml --check
    - python tests/pre_deployment_checks.py staging

deploy_to_production:
  stage: deploy
  when: manual
  script:
    - python tests/pre_deployment_checks.py production
    - ansible-playbook -i inventory/production playbooks/deploy.yml
    - python tests/post_deployment_validation.py production
  only:
    - main
```

## Troubleshooting Common Issues

### Issue 1: SSH Connection Timeouts

**Problem**: Netmiko or Paramiko connections timeout when connecting to network devices.

**Solutions**:
- Increase timeout values: `device = {'timeout': 60, 'blocking_timeout': 30}`
- Check network connectivity: `ping`, `traceroute` to device
- Verify SSH is enabled: `show ip ssh` on device
- Check firewall rules allowing SSH from automation host
- Use `fast_cli=False` for slower devices
- Enable verbose logging: `logging.basicConfig(level=logging.DEBUG)`

### Issue 2: Ansible Task Failures

**Problem**: Ansible network modules fail with "authentication failed" or "timeout" errors.

**Solutions**:
```yaml
# Increase timeouts in playbook
- hosts: routers
  gather_facts: no
  connection: network_cli
  vars:
    ansible_command_timeout: 60
    ansible_connect_timeout: 30
  tasks:
    - name: Configure interface
      cisco.ios.ios_interfaces:
        config:
          - name: GigabitEthernet0/1
            enabled: true
```

**Additional checks**:
- Verify credentials in vault or inventory
- Test manual SSH connection from Ansible host
- Check device privilege level (enable mode required)
- Review ansible logs: `ansible-playbook -vvvv`

### Issue 3: NETCONF/YANG Model Errors

**Problem**: NETCONF operations fail with "invalid YANG path" errors.

**Solutions**:
- Validate YANG model compatibility: Check device OS version
- Use vendor-specific YANG models, not generic OpenConfig
- Install required YANG models: `pip install yang`
- Test YANG paths with `pyang` before deployment

```python
# Verify YANG model before use
from ncclient import manager

with manager.connect(host='router', username='admin', password='pass',
                     hostkey_verify=False) as m:
    # Get supported capabilities
    for capability in m.server_capabilities:
        print(capability)
```

### Issue 4: Configuration Drift Detection

**Problem**: Configurations drift from intended state over time.

**Solutions**:
```python
# Automated drift detection with NAPALM
from napalm import get_network_driver
import difflib

def detect_drift(device_info, intended_config_file):
    driver = get_network_driver(device_info['driver'])
    device = driver(device_info['hostname'],
                   device_info['username'],
                   device_info['password'])
    device.open()

    # Get current config
    current_config = device.get_config()['running']

    # Load intended config
    with open(intended_config_file, 'r') as f:
        intended_config = f.read()

    # Compare
    diff = difflib.unified_diff(
        intended_config.splitlines(keepends=True),
        current_config.splitlines(keepends=True),
        fromfile='intended',
        tofile='current'
    )

    drift = ''.join(diff)
    if drift:
        print(f"Configuration drift detected on {device_info['hostname']}:")
        print(drift)
        return True
    else:
        print(f"No drift detected on {device_info['hostname']}")
        return False

    device.close()
```

## Performance Optimization Tips

### 1. Parallel Execution
- Use Nornir's threading for parallel device operations
- Ansible's `forks` parameter (default 5, increase for large deployments)
- AsyncIO for concurrent NETCONF/RESTCONF operations

### 2. Connection Reuse
```python
# Reuse SSH connections with Netmiko
from netmiko import ConnectHandler

connection = ConnectHandler(**device_params)
# Perform multiple commands without reconnecting
output1 = connection.send_command("show version")
output2 = connection.send_command("show interfaces")
output3 = connection.send_config_set(config_commands)
connection.disconnect()
```

### 3. Caching and State Management
- Cache device facts to avoid repeated API calls
- Use Ansible's fact caching: `fact_caching = jsonfile`
- Implement state files for idempotent operations

## Security Best Practices

### 1. Credential Management
```python
# Use environment variables or secret managers
import os
from dotenv import load_dotenv

load_dotenv()

device = {
    'host': os.getenv('DEVICE_HOST'),
    'username': os.getenv('DEVICE_USER'),
    'password': os.getenv('DEVICE_PASS'),
    'device_type': 'cisco_ios'
}
```

### 2. Ansible Vault for Sensitive Data
```bash
# Encrypt sensitive variables
ansible-vault encrypt vars/credentials.yml

# Use in playbooks
ansible-playbook playbook.yml --ask-vault-pass
```

### 3. Audit Trail and Change Logging
```python
# Log all configuration changes
import logging
from datetime import datetime

logging.basicConfig(
    filename=f'network_changes_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def deploy_config(device, commands):
    logging.info(f"Deploying to {device['host']}: {commands}")
    # Deployment logic
    logging.info(f"Successfully deployed to {device['host']}")
```

## Real-World Use Cases

### Use Case 1: Mass Configuration Rollout
**Scenario**: Deploy SNMP configuration to 500+ devices across multiple data centers.

**Solution**: Nornir with threading + Jinja2 templates
- Inventory: YAML-based with groups (dc1, dc2, etc.)
- Template: Jinja2 template for SNMP with variable substitution
- Execution: Parallel deployment with rollback capability
- Validation: Post-deployment SNMP connectivity checks

### Use Case 2: Automated Disaster Recovery
**Scenario**: Automated configuration backup and restoration for DR scenarios.

**Solution**: Scheduled Python scripts with version control
- Daily: Backup all device configs to Git repository
- Tagging: Git tags for stable configurations
- Restoration: Automated config restore from Git on device failure
- Testing: Regular DR drills using staging environment

### Use Case 3: Zero-Touch Provisioning (ZTP)
**Scenario**: Automate deployment of new branch office routers.

**Solution**: DHCP + TFTP/HTTP + Ansible automation
- DHCP: Provides IP and config file location
- Initial config: Basic connectivity and management access
- Ansible: Pull full configuration based on device serial/location
- Validation: Automated testing of WAN connectivity, VPN, routing

## Certification Alignment

- Cisco DevNet Associate/Expert
- HashiCorp Certified Terraform Associate
- Arista Certified Automation Engineer
- Juniper Networks Automation Engineer
- Red Hat Certified Specialist in Ansible Network Automation

## Additional Resources

- **Books**: "Network Programmability and Automation" (O'Reilly)
- **Training**: Cisco DevNet Learning Labs, Arista Automation Workshops
- **Community**: Network to Code Slack, Ansible Network Working Group
- **Tools**: Batfish (network validation), Suzieq (network observability)

---

**Last Updated**: 2025-11-19
**Skill Level**: Advanced
**Prerequisites**: Network fundamentals, Python basics, Git basics
