# Network Automation Patterns

## Executive Summary

This document defines reusable patterns and best practices for network automation using industry-standard tools (Ansible, Terraform, Python). These patterns enable consistent, scalable, and maintainable network infrastructure automation across enterprise environments.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: Ansible Best Practices, Terraform Design Patterns, Python Style Guide (PEP 8)

---

## 1. Ansible Network Automation Patterns

### 1.1 Device Inventory Pattern

**Best Practice: Organize inventory by site, device role, and attributes**

```yaml
# Inventory Structure: inventory/
# ├─ hosts.yml (device definitions)
# ├─ group_vars/
# │   ├─ all.yml (global variables)
# │   ├─ core_routers.yml
# │   ├─ access_switches.yml
# │   └─ dfw_site.yml (site-specific)
# └─ host_vars/
#     ├─ dfw-core-01.yml
#     └─ nyc-core-01.yml

---
# inventory/hosts.yml

all:
  vars:
    # Global defaults
    ansible_connection: local
    ansible_python_interpreter: "{{ ansible_playbook_dir }}/../venv/bin/python"

  children:
    # Group by site
    dfw_site:
      hosts:
        dfw-core-01:
          ansible_host: 10.1.4.1
          device_type: cisco_ios_xr
          role: core_router
        dfw-core-02:
          ansible_host: 10.1.4.2
          device_type: cisco_ios_xr
          role: core_router
        dfw-agg-01:
          ansible_host: 10.1.4.11
          device_type: cisco_nxos
          role: aggregation_switch

    nyc_site:
      hosts:
        nyc-core-01:
          ansible_host: 10.2.4.1
          device_type: cisco_ios_xr
          role: core_router

    # Group by function
    core_routers:
      hosts:
        dfw-core-01:
        dfw-core-02:
        nyc-core-01:

    access_switches:
      hosts:
        dfw-agg-01:

---
# inventory/group_vars/dfw_site.yml
site_code: dfw
site_region: north_america
site_location: Dallas, TX
site_timezone: America/Chicago
snmp_community: "community_string"
ntp_servers:
  - 10.0.0.1
  - 10.0.0.2

---
# inventory/group_vars/core_routers.yml
device_auth_method: key
ssh_key_path: ~/.ssh/network_key
privileged_password_file: ./secrets/privileged.yml
router_id_base: "10.0.1"
snmp_traps_enabled: true

---
# inventory/host_vars/dfw-core-01.yml
local_asn: 65001
router_id: 10.0.1.1
loopback_ip: 10.0.1.1/32
upstream_neighbor:
  address: 10.0.1.2
  asn: 65001
```

### 1.2 Task Organization Pattern

**Pattern: Organize tasks into logical roles**

```yaml
# Playbook Structure: playbooks/
# ├─ site_deployment.yml (main playbook)
# └─ roles/
#     ├─ common/
#     │   ├─ tasks/main.yml
#     │   ├─ handlers/main.yml
#     │   └─ templates/
#     ├─ routing/
#     │   ├─ tasks/main.yml
#     │   └─ templates/bgp.j2
#     ├─ security/
#     │   ├─ tasks/main.yml
#     │   └─ templates/acl.j2
#     └─ monitoring/

---
# playbooks/site_deployment.yml

---
- name: Deploy network configuration across site
  hosts: dfw_site
  gather_facts: no
  vars:
    config_backup_dir: "./backups"
    deploy_mode: "check"  # or "apply"

  pre_tasks:
    - name: Pre-deployment validation
      include_role:
        name: validation
      vars:
        validation_type: pre_deployment

    - name: Backup current configuration
      include_role:
        name: backup
      vars:
        backup_path: "{{ config_backup_dir }}/{{ inventory_hostname }}"

  tasks:
    - name: Configure common settings (NTP, SNMP, etc.)
      include_role:
        name: common

    - name: Configure routing protocols (OSPF, BGP)
      include_role:
        name: routing
      when: device_type in ['cisco_ios_xr', 'juniper_junos']

    - name: Configure security (ACLs, firewall)
      include_role:
        name: security
      when: '"firewall" in role'

    - name: Configure monitoring (SNMP, telemetry)
      include_role:
        name: monitoring

  post_tasks:
    - name: Validate configuration
      include_role:
        name: validation
      vars:
        validation_type: post_deployment

    - name: Generate compliance report
      include_role:
        name: reporting

---
# playbooks/roles/routing/tasks/main.yml

---
- name: Configure BGP for DFW core routers
  block:
    - name: Backup running configuration
      cisco.ios.ios_command:
        commands:
          - "show run"
      register: running_config
      when: device_type == "cisco_ios_xr"

    - name: Render BGP configuration from template
      template:
        src: bgp.j2
        dest: "/tmp/bgp_config_{{ inventory_hostname }}.txt"
        mode: "0600"
      register: bgp_config_rendered

    - name: Apply BGP configuration
      cisco.iosxr.iosxr_config:
        src: "bgp_config_{{ inventory_hostname }}.txt"
        save: yes
        backup: yes
        match: line
        replace: line
      when: deploy_mode == "apply"

    - name: Verify BGP neighbor status
      cisco.iosxr.iosxr_command:
        commands:
          - "show bgp neighbors"
      register: bgp_neighbors
      until:
        - "bgp_neighbors.stdout | regex_search('Established')"
      retries: 3
      delay: 10

    - name: Display BGP status
      debug:
        msg: "BGP neighbors: {{ bgp_neighbors.stdout }}"

  rescue:
    - name: BGP configuration failed - rollback
      debug:
        msg: "Configuration failed. Initiating rollback..."

    - name: Restore from backup
      cisco.iosxr.iosxr_config:
        src: "{{ config_backup_dir }}/{{ inventory_hostname }}/running_config"
      when: deploy_mode == "apply"

---
# playbooks/roles/routing/templates/bgp.j2

router bgp {{ local_asn }}
  bgp log-neighbor-changes
  bgp graceful-restart
  bgp gr-restart-time 120
  bgp gr-stale-path-time 300
  !
  address-family ipv4 unicast
    redistribute connected
    redistribute static
  !
  !
  neighbor {{ upstream_neighbor.address }} remote-as {{ upstream_neighbor.asn }}
  neighbor {{ upstream_neighbor.address }} description {{ upstream_neighbor_name }}
  neighbor {{ upstream_neighbor.address }} password {{ bgp_neighbor_password }}
  !
  address-family ipv4 unicast
    neighbor {{ upstream_neighbor.address }} activate
    neighbor {{ upstream_neighbor.address }} soft-reconfiguration inbound
  !
!
```

### 1.3 Dynamic Inventory Pattern

**Pattern: Generate inventory from external sources (NetBox, cloud APIs)**

```python
#!/usr/bin/env python3
# plugins/inventory/netbox_inventory.py

"""
Dynamic inventory plugin pulling from NetBox
"""

import json
import requests
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable

class InventoryModule(BaseInventoryPlugin):
    NAME = 'netbox_inventory'
    PLUGIN_TYPE = 'inventory'
    CACHE_KEY = 'netbox_devices'
    CACHE_PREFIX = 'netbox_'

    def __init__(self):
        super().__init__()
        self.inventory = self.inventory

    def verify_file(self, path):
        """Verify this is a valid NetBox inventory file"""
        if path.endswith(('netbox_inventory.yml', 'netbox.yml')):
            return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        """Main entry point"""
        super().__init__(inventory, loader, path)

        # Load configuration
        config = self._read_config_data(path)
        netbox_url = config.get('plugin_settings', {}).get('url')
        netbox_token = config.get('plugin_settings', {}).get('token')

        # Fetch devices from NetBox
        devices = self._fetch_devices(netbox_url, netbox_token)

        # Add devices to inventory
        for device in devices:
            self._add_device(device)

    def _fetch_devices(self, url, token):
        """Fetch devices from NetBox API"""
        headers = {
            'Authorization': f'Token {token}',
            'Accept': 'application/json'
        }

        devices = []
        page = 1

        while True:
            response = requests.get(
                f'{url}/api/dcim/devices/',
                params={'page': page, 'limit': 50},
                headers=headers
            )

            if response.status_code != 200:
                raise Exception(f'NetBox API error: {response.status_code}')

            data = response.json()
            devices.extend(data['results'])

            if not data.get('next'):
                break

            page += 1

        return devices

    def _add_device(self, device):
        """Add device to Ansible inventory"""
        hostname = device['name']
        device_type = device.get('device_type', {}).get('model', 'unknown')
        site = device.get('site', {}).get('name', 'unknown')

        # Add host
        self.inventory.add_host(hostname)

        # Add hostvars
        self.inventory.get_host(hostname).set_variable('device_type', device_type)
        self.inventory.get_host(hostname).set_variable('site', site)
        self.inventory.get_host(hostname).set_variable('mgmt_ip', device.get('primary_ip4', {}).get('address'))

        # Add to site group
        self.inventory.add_group(site)
        self.inventory.add_host(hostname, group=site)

        # Add to device type group
        self.inventory.add_group(device_type)
        self.inventory.add_host(hostname, group=device_type)

# Usage in playbook:
# ansible-inventory -i netbox_inventory.yml --graph
```

### 1.4 Error Handling and Rollback Pattern

```yaml
---
# playbooks/roles/config_deploy/tasks/main.yml

- name: Network configuration deployment with rollback
  block:
    # BACKUP PHASE
    - name: Create backup of current configuration
      block:
        - name: Backup device config
          cisco.iosxr.iosxr_command:
            commands:
              - "show run"
          register: current_config

        - name: Save backup to file
          copy:
            content: "{{ current_config.stdout[0] }}"
            dest: "{{ backup_dir }}/{{ inventory_hostname }}-{{ ansible_date_time.iso8601 }}.backup"
          delegate_to: localhost
          become: no

        - name: Store backup for rollback
          set_fact:
            rollback_config: "{{ current_config.stdout[0] }}"

      rescue:
        - name: Backup failed - abort deployment
          fail:
            msg: "Unable to backup configuration. Aborting deployment."

    # VALIDATION PHASE
    - name: Validate proposed configuration
      block:
        - name: Render configuration from template
          template:
            src: "{{ device_type }}_config.j2"
            dest: "/tmp/proposed_config_{{ inventory_hostname }}.txt"
          register: proposed_config

        - name: Check for configuration syntax errors
          cisco.iosxr.iosxr_config:
            lines: "{{ proposed_config.stdout }}"
            replace: "block"
            backup: no
            match: "none"
            state: "absent"  # Don't apply, just validate
          check_mode: yes
          register: validation_result

        - name: Abort if validation fails
          fail:
            msg: "Configuration validation failed: {{ validation_result.msg }}"
          when: validation_result.failed

      rescue:
        - name: Validation failed
          debug:
            msg: "Configuration validation failed. No changes applied."

    # APPLICATION PHASE (only if validation passes)
    - name: Apply configuration to device
      block:
        - name: Apply proposed configuration
          cisco.iosxr.iosxr_config:
            src: "/tmp/proposed_config_{{ inventory_hostname }}.txt"
            save: yes
            backup: yes

        - name: Wait for device to stabilize
          pause:
            seconds: 5

      rescue:
        - name: Configuration application failed - initiating rollback
          block:
            - name: Restore from backup
              cisco.iosxr.iosxr_config:
                lines: "{{ rollback_config }}"
                match: "line"
                replace: "config"
                save: yes

            - name: Verify rollback completed
              cisco.iosxr.iosxr_command:
                commands:
                  - "show config differences startup"
              register: diff_output

            - name: Alert: Rollback completed
              debug:
                msg: "Configuration deployment failed. Rolled back to previous config."

            - name: Fail the playbook
              fail:
                msg: "Deployment failed and rolled back. Check device logs."

    # VERIFICATION PHASE
    - name: Verify deployed configuration
      block:
        - name: Retrieve running configuration
          cisco.iosxr.iosxr_command:
            commands:
              - "show run"
          register: deployed_config

        - name: Compare deployed vs proposed
          assert:
            that:
              - "proposed_config.stdout in deployed_config.stdout[0]"
            fail_msg: "Deployed configuration does not match proposed"
            success_msg: "Configuration deployed successfully"

  always:
    - name: Cleanup temporary files
      file:
        path: "/tmp/proposed_config_{{ inventory_hostname }}.txt"
        state: absent
      delegate_to: localhost
```

---

## 2. Terraform Network Automation Patterns

### 2.1 Multi-Environment Module Pattern

```hcl
# Directory structure:
# terraform/
# ├─ environments/
# │   ├─ prod/
# │   │   ├─ main.tf
# │   │   ├─ terraform.tfvars
# │   │   └─ backend.tf
# │   └─ dev/
# │       ├─ main.tf
# │       ├─ terraform.tfvars
# │       └─ backend.tf
# └─ modules/
#     ├─ core_router/
#     ├─ access_switch/
#     └─ firewall/

# terraform/environments/prod/main.tf

terraform {
  required_version = ">= 1.0"
  required_providers {
    cisco-iosxr = {
      source  = "CiscoDevNet/iosxr"
      version = "~> 0.3.0"
    }
    juniper = {
      source  = "terraform-providers/juniper"
      version = "~> 1.3.0"
    }
  }

  backend "s3" {
    bucket         = "network-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "region" {
  type = string
}

variable "core_routers" {
  type = map(object({
    ip_address = string
    asn        = number
    router_id  = string
  }))
}

# Configure providers
provider "cisco-iosxr" {
  alias    = "dfw-core"
  host     = var.core_routers["dfw-core-01"].ip_address
  username = var.admin_username
  password = var.admin_password
  insecure = false
}

# Deploy core routers module
module "dfw_core_routers" {
  source = "../../modules/core_router"

  for_each = var.core_routers

  device_name   = each.key
  device_ip     = each.value.ip_address
  router_id     = each.value.router_id
  local_asn     = each.value.asn
  environment   = var.environment
  region        = var.region

  providers = {
    cisco-iosxr = cisco-iosxr.dfw-core
  }

  depends_on = [
    null_resource.prerequisites_check
  ]
}

# terraform/modules/core_router/main.tf

variable "device_name" {
  type = string
}

variable "device_ip" {
  type = string
}

variable "router_id" {
  type = string
}

variable "local_asn" {
  type = number
}

variable "environment" {
  type = string
}

# Configure router hostname
resource "cisco-iosxr_config" "hostname" {
  device = var.device_name
  value  = "hostname ${var.device_name}"
}

# Configure loopback interface
resource "cisco-iosxr_config" "loopback_interface" {
  device = var.device_name

  config = templatefile("${path.module}/templates/loopback.tftpl", {
    interface_ip = var.router_id
    description  = "Loopback for BGP router-id"
  })
}

# Configure BGP
resource "cisco-iosxr_config" "bgp_configuration" {
  device = var.device_name

  config = templatefile("${path.module}/templates/bgp.tftpl", {
    local_asn  = var.local_asn
    router_id  = var.router_id
    environment = var.environment
  })

  depends_on = [
    cisco-iosxr_config.loopback_interface
  ]
}

# Validate configuration
resource "null_resource" "validation" {
  provisioner "local-exec" {
    command = "echo 'Validating config for ${var.device_name}'"
  }

  depends_on = [
    cisco-iosxr_config.bgp_configuration
  ]
}

# terraform/modules/core_router/templates/bgp.tftpl

router bgp ${local_asn}
  bgp log-neighbor-changes
  bgp graceful-restart
  !
  bgp router-id ${router_id}
  !
  address-family ipv4 unicast
    redistribute connected
  !
  !
exit
```

### 2.2 State Management and Testing Pattern

```hcl
# terraform/main.tf

# Import existing infrastructure (for legacy migration)
import {
  to = module.existing_core_routers[0]
  id = "dfw-core-01"
}

# Implement local-exec for testing
resource "null_resource" "terraform_tests" {
  provisioner "local-exec" {
    command = <<EOT
      # Validate all Terraform files
      terraform validate

      # Format check
      terraform fmt -check

      # Security scanning (tfsec)
      tfsec .

      # Cost estimation
      terraform plan -json | jq '.resource_changes'
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}

# terraform/tests/main.test.hcl (Terraform testing framework)

run "valid_environment_prod" {
  command = plan

  assert {
    condition     = module.dfw_core_routers["dfw-core-01"].device_name == "dfw-core-01"
    error_message = "Device name mismatch"
  }

  assert {
    condition     = try(module.dfw_core_routers["dfw-core-01"].bgp_asn, null) != null
    error_message = "BGP ASN not configured"
  }
}

run "router_configuration_syntax" {
  command = plan

  assert {
    condition     = try(cisco-iosxr_config.bgp_configuration.config, null) != null
    error_message = "BGP config not rendered properly"
  }
}
```

---

## 3. Python Network Automation Patterns

### 3.1 Device Abstraction Layer Pattern

```python
#!/usr/bin/env python3
"""
Device abstraction layer for multi-vendor support
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging
from paramiko import SSHClient
from netmiko import ConnectHandler
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkDevice(ABC):
    """Abstract base class for network devices"""

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.connection = None

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to device"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection gracefully"""
        pass

    @abstractmethod
    def send_command(self, command: str) -> str:
        """Send CLI command and return output"""
        pass

    @abstractmethod
    def configure(self, commands: List[str]) -> bool:
        """Apply configuration commands"""
        pass

    @abstractmethod
    def get_interfaces(self) -> Dict:
        """Get all interface status"""
        pass

    @abstractmethod
    def get_routes(self) -> Dict:
        """Get routing table"""
        pass


class CiscoIOSXRDevice(NetworkDevice):
    """Cisco IOS XR implementation"""

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        super().__init__(host, username, password)
        self.port = port
        self.device_type = 'cisco_iosxr'

    def connect(self) -> bool:
        try:
            self.connection = ConnectHandler(
                device_type=self.device_type,
                host=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=30
            )
            logger.info(f"Connected to {self.host}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        try:
            if self.connection:
                self.connection.disconnect()
            return True
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            return False

    def send_command(self, command: str) -> str:
        try:
            output = self.connection.send_command(command)
            return output
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return ""

    def configure(self, commands: List[str]) -> bool:
        try:
            output = self.connection.send_config_set(commands)
            logger.info(f"Configuration applied: {len(commands)} commands")
            return True
        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return False

    def get_interfaces(self) -> Dict:
        """Parse interface data from IOS XR output"""
        output = self.send_command("show interface")
        interfaces = {}
        # Parse output into structured format
        return interfaces

    def get_routes(self) -> Dict:
        """Retrieve routing table"""
        output = self.send_command("show route")
        routes = {}
        # Parse routing table
        return routes


class JuniperJunosDevice(NetworkDevice):
    """Juniper Junos implementation"""

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        super().__init__(host, username, password)
        self.port = port
        self.device_type = 'juniper_junos'

    def connect(self) -> bool:
        try:
            self.connection = ConnectHandler(
                device_type=self.device_type,
                host=self.host,
                username=self.username,
                password=self.password,
                port=self.port
            )
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def send_command(self, command: str) -> str:
        try:
            output = self.connection.send_command(command)
            return output
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return ""

    def configure(self, commands: List[str]) -> bool:
        # Junos-specific configuration
        try:
            output = self.connection.send_config_set(commands)
            return True
        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return False

    def get_interfaces(self) -> Dict:
        """Juniper-specific interface retrieval"""
        pass

    def get_routes(self) -> Dict:
        pass


class DeviceFactory:
    """Factory for creating device instances"""

    DEVICE_TYPES = {
        'cisco_iosxr': CiscoIOSXRDevice,
        'cisco_nxos': CiscoIOSXRDevice,  # Could have separate impl
        'juniper_junos': JuniperJunosDevice,
        'arista_eos': CiscoIOSXRDevice,  # Similar to Cisco
    }

    @staticmethod
    def create(device_type: str, host: str, username: str, password: str) -> NetworkDevice:
        """Create device instance based on type"""
        if device_type not in DeviceFactory.DEVICE_TYPES:
            raise ValueError(f"Unknown device type: {device_type}")

        DeviceClass = DeviceFactory.DEVICE_TYPES[device_type]
        return DeviceClass(host, username, password)


# Usage example
if __name__ == "__main__":
    # Create device using factory
    device = DeviceFactory.create(
        'cisco_iosxr',
        '10.1.4.1',
        'admin',
        'password'
    )

    if device.connect():
        # Send command
        output = device.send_command("show version")
        print(output)

        # Configure
        commands = [
            "router ospf 1",
            "network 10.0.0.0 0.255.255.255 area 0"
        ]
        device.configure(commands)

        device.disconnect()
```

### 3.2 Configuration Management Pattern

```python
#!/usr/bin/env python3
"""
Configuration management with Git version control and diff comparison
"""

import os
import json
import git
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple
import difflib
import logging

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Manage device configurations with Git backend"""

    def __init__(self, repo_path: str = "./network-configs"):
        self.repo_path = repo_path
        self.repo = self._init_repo()

    def _init_repo(self) -> git.Repo:
        """Initialize or load Git repository"""
        if os.path.exists(self.repo_path):
            return git.Repo(self.repo_path)
        else:
            repo = git.Repo.init(self.repo_path)
            logger.info(f"Initialized repository at {self.repo_path}")
            return repo

    def backup_device_config(self, hostname: str, config: str) -> bool:
        """Backup device configuration to Git"""
        try:
            device_dir = Path(self.repo_path) / "devices" / hostname
            device_dir.mkdir(parents=True, exist_ok=True)

            config_file = device_dir / "running.conf"
            config_file.write_text(config)

            # Commit to Git
            self.repo.index.add(str(config_file))

            commit_message = (
                f"Backup {hostname} configuration\n"
                f"Time: {datetime.now().isoformat()}\n"
                f"Lines: {len(config.splitlines())}"
            )

            self.repo.index.commit(commit_message)
            logger.info(f"Backed up configuration for {hostname}")
            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def get_config_diff(self, hostname: str) -> Tuple[str, str]:
        """Get diff between running and previous backup"""
        try:
            device_dir = Path(self.repo_path) / "devices" / hostname
            config_file = device_dir / "running.conf"

            if not config_file.exists():
                return ("", "No previous configuration found")

            # Get previous version from Git
            git_show = self.repo.git.show(f"HEAD:{config_file}")
            current = config_file.read_text()

            # Generate diff
            diff = list(difflib.unified_diff(
                git_show.splitlines(keepends=True),
                current.splitlines(keepends=True),
                fromfile="Previous",
                tofile="Current"
            ))

            return ("".join(diff), "")

        except Exception as e:
            logger.error(f"Diff generation failed: {e}")
            return ("", str(e))

    def validate_config_compliance(self, hostname: str, config: str, rules: Dict) -> bool:
        """Validate configuration against compliance rules"""
        violations = []

        for rule_name, rule_check in rules.items():
            # Check for required patterns
            if "required_pattern" in rule_check:
                if rule_check["required_pattern"] not in config:
                    violations.append(f"Missing required: {rule_name}")

            # Check for forbidden patterns
            if "forbidden_pattern" in rule_check:
                if rule_check["forbidden_pattern"] in config:
                    violations.append(f"Forbidden pattern found: {rule_name}")

        if violations:
            logger.warning(f"Compliance violations on {hostname}: {violations}")
            return False

        logger.info(f"Configuration compliance passed for {hostname}")
        return True

    def export_config_json(self, hostname: str) -> Dict:
        """Export device configuration as structured JSON"""
        try:
            device_dir = Path(self.repo_path) / "devices" / hostname
            config_file = device_dir / "running.conf"

            if not config_file.exists():
                raise FileNotFoundError(f"Config not found for {hostname}")

            config_text = config_file.read_text()

            # Parse text configuration into JSON
            parsed_config = {
                "hostname": hostname,
                "timestamp": datetime.now().isoformat(),
                "raw_config": config_text,
                "parsed": self._parse_config(config_text)
            }

            return parsed_config

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {}

    def _parse_config(self, config_text: str) -> Dict:
        """Simple configuration parser (extend as needed)"""
        parsed = {
            "hostname": None,
            "interfaces": {},
            "routing": {}
        }

        lines = config_text.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("hostname"):
                parsed["hostname"] = line.split()[-1]

            elif line.startswith("interface"):
                iface_name = line.split()[1]
                parsed["interfaces"][iface_name] = {}

            elif line.startswith("router"):
                protocol = line.split()[1]
                parsed["routing"][protocol] = {}

        return parsed


# Usage
if __name__ == "__main__":
    config_mgr = ConfigurationManager()

    # Backup configuration
    sample_config = """
hostname dfw-core-01
!
interface GigabitEthernet0/0/1
 description Uplink to DFW-Core-02
 mtu 1500
 ip address 10.0.1.1 255.255.255.0
!
router ospf 1
 network 10.0.0.0 0.255.255.255 area 0
!
"""

    config_mgr.backup_device_config("dfw-core-01", sample_config)

    # Get diff
    diff, error = config_mgr.get_config_diff("dfw-core-01")
    print(f"Diff: {diff}")

    # Validate compliance
    rules = {
        "mtu_configured": {"required_pattern": "mtu 1500"},
        "ospf_configured": {"required_pattern": "router ospf"},
        "no_telnet": {"forbidden_pattern": "telnet"}
    }

    config_mgr.validate_config_compliance(
        "dfw-core-01",
        sample_config,
        rules
    )

    # Export as JSON
    config_json = config_mgr.export_config_json("dfw-core-01")
    print(json.dumps(config_json, indent=2))
```

---

## References

- **Ansible Best Practices**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
- **Terraform Design Patterns**: https://learn.hashicorp.com/terraform
- **NetBox Network Documentation**: https://netbox.dev/
- **Python for Network Engineers**: https://pynet.twb-tech.com/

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Automation and Infrastructure Team
