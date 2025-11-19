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

## Certification Alignment

- Cisco DevNet Associate/Expert
- HashiCorp Certified Terraform Associate
- Arista Certified Automation Engineer
- Juniper Networks Automation Engineer

---

**Last Updated**: 2025-11-19
**Skill Level**: Advanced
**Prerequisites**: Network fundamentals, Python basics, Git basics
