# Ansible Network Automation Guide

## Getting Started

### Installation
```bash
# Install Ansible
pip install ansible

# Install network collections
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install cisco.iosxr
ansible-galaxy collection install junipernetworks.junos
ansible-galaxy collection install arista.eos
```

### Project Structure
```
network-automation/
├── ansible.cfg
├── inventory/
│   ├── hosts.yaml
│   ├── group_vars/
│   │   └── all.yaml
│   └── host_vars/
│       └── router1.yaml
├── playbooks/
│   ├── deploy_config.yaml
│   ├── backup_config.yaml
│   └── pre_checks.yaml
├── roles/
│   ├── base_config/
│   ├── routing/
│   └── security/
├── templates/
│   └── interfaces.j2
└── group_vars/
    └── routers.yaml
```

## Inventory Setup

### hosts.yaml
```yaml
---
all:
  children:
    routers:
      hosts:
        router1:
          ansible_host: 192.168.1.1
          ansible_network_os: cisco.ios.ios
          ansible_user: admin
          ansible_password: password
          ansible_connection: network_cli
          device_role: core
          site: DC1

        router2:
          ansible_host: 192.168.1.2
          ansible_network_os: junipernetworks.junos.junos
          ansible_user: admin
          ansible_password: password
          ansible_connection: netconf
          device_role: edge
          site: DC2

    switches:
      hosts:
        switch1:
          ansible_host: 192.168.1.3
          ansible_network_os: cisco.ios.ios
          ansible_user: admin
          ansible_password: password
```

## Basic Playbooks

### Gathering Facts
```yaml
---
- name: Gather device facts
  hosts: routers
  gather_facts: no

  tasks:
    - name: Gather facts from Cisco IOS devices
      cisco.ios.ios_facts:
        gather_subset: all
      register: device_facts

    - name: Display device information
      debug:
        msg: |
          Device: {{ inventory_hostname }}
          Version: {{ ansible_net_version }}
          Serial: {{ ansible_net_serialnum }}
          Uptime: {{ ansible_net_uptime }}
          Interfaces: {{ ansible_net_interfaces | join(', ') }}
```

### Configuration Deployment
```yaml
---
- name: Deploy configuration to routers
  hosts: routers
  gather_facts: no

  vars:
    device_configs:
      - interface: Ethernet0/0
        ip_address: 192.168.1.1
        subnet_mask: 255.255.255.0
        description: WAN Interface

  tasks:
    - name: Backup current configuration
      cisco.ios.ios_command:
        commands: show running-config
      register: config_backup

    - name: Save backup to file
      copy:
        content: "{{ config_backup.stdout[0] }}"
        dest: "backups/{{ inventory_hostname }}_{{ ansible_date_time.iso8601_basic_short }}.cfg"
      delegate_to: localhost

    - name: Configure interfaces
      cisco.ios.ios_config:
        lines:
          - "ip address {{ item.ip_address }} {{ item.subnet_mask }}"
          - "description {{ item.description }}"
          - "no shutdown"
        parents: "interface {{ item.interface }}"
        save_when: changed
      loop: "{{ device_configs }}"

    - name: Verify configuration
      cisco.ios.ios_command:
        commands: show ip interface brief
      register: interface_status

    - name: Display interface status
      debug:
        msg: "{{ interface_status.stdout[0] }}"
```

### Configuration from Templates
```yaml
---
- name: Deploy configurations from Jinja2 templates
  hosts: routers
  gather_facts: yes

  vars:
    ntp_servers:
      - 8.8.8.8
      - 8.8.4.4
    snmp_community: public
    snmp_location: "Data Center 1"

  tasks:
    - name: Generate router configuration from template
      template:
        src: router_config.j2
        dest: "/tmp/{{ inventory_hostname }}_config.txt"
      register: generated_config

    - name: Deploy generated configuration
      cisco.ios.ios_config:
        src: "/tmp/{{ inventory_hostname }}_config.txt"
        save_when: changed

    - name: Notify on changes
      debug:
        msg: "Configuration deployed to {{ inventory_hostname }}"
      when: generated_config is changed
```

## Roles

### Role Structure
```
roles/
└── base_config/
    ├── tasks/
    │   ├── main.yaml
    │   ├── ntp.yaml
    │   ├── snmp.yaml
    │   └── logging.yaml
    ├── templates/
    │   └── syslog_config.j2
    ├── vars/
    │   └── main.yaml
    ├── defaults/
    │   └── main.yaml
    └── handlers/
        └── main.yaml
```

### Role Implementation
```yaml
# roles/base_config/tasks/main.yaml
---
- name: Base configuration tasks
  block:
    - name: Configure NTP
      include_tasks: ntp.yaml

    - name: Configure SNMP
      include_tasks: snmp.yaml

    - name: Configure logging
      include_tasks: logging.yaml

# roles/base_config/tasks/ntp.yaml
---
- name: Configure NTP
  cisco.ios.ios_config:
    lines:
      - ntp server {{ item }}
  loop: "{{ ntp_servers }}"

# roles/base_config/handlers/main.yaml
---
- name: Reload device
  cisco.ios.ios_command:
    commands: reload
    confirm: yes
```

### Using Roles
```yaml
---
- name: Apply roles to devices
  hosts: routers

  roles:
    - base_config
    - routing
    - security

  post_tasks:
    - name: Verify deployment
      cisco.ios.ios_command:
        commands: show version
      register: version_output

    - name: Display version
      debug:
        msg: "{{ version_output.stdout[0] }}"
```

## Handlers

### Event-Driven Actions
```yaml
---
- name: Configuration with handlers
  hosts: routers
  gather_facts: no

  tasks:
    - name: Configure BGP
      cisco.ios.ios_config:
        lines:
          - "router bgp 65001"
          - "neighbor 10.0.0.1 remote-as 65002"
        save_when: changed
      notify: Restart BGP

  handlers:
    - name: Restart BGP
      cisco.ios.ios_command:
        commands: clear ip bgp *
      listen: Restart BGP
```

## Error Handling

### Block and Rescue
```yaml
---
- name: Error handling example
  hosts: routers
  gather_facts: no

  tasks:
    - name: Configuration block
      block:
        - name: Apply configuration
          cisco.ios.ios_config:
            lines:
              - interface Ethernet0/0
              - ip address 10.0.0.1 255.255.255.0
            save_when: changed

      rescue:
        - name: Configuration failed
          debug:
            msg: "Failed to apply configuration, rolling back..."

        - name: Revert to backup
          cisco.ios.ios_config:
            src: "backups/{{ inventory_hostname }}_last.cfg"

      always:
        - name: Save config after attempt
          cisco.ios.ios_command:
            commands: show running-config
          register: post_config
```

## Async Operations

### Long-Running Tasks
```yaml
---
- name: Long-running operations
  hosts: routers
  gather_facts: no

  tasks:
    - name: Start backup job
      cisco.ios.ios_command:
        commands: copy running-config tftp://10.0.0.100/backup.cfg
      async: 300
      poll: 0
      register: backup_job

    - name: Wait for backup to complete
      async_status:
        jid: "{{ backup_job.ansible_job_id }}"
      register: job_result
      until: job_result.finished
      retries: 30
      delay: 10
```

## Check Mode and Diff

### Dry Run
```bash
# Run playbook in check mode (no changes)
ansible-playbook -i inventory playbooks/deploy.yaml --check

# Show differences
ansible-playbook -i inventory playbooks/deploy.yaml --check --diff
```

### In Playbook
```yaml
---
- name: Configuration with check
  hosts: routers
  gather_facts: no

  tasks:
    - name: Apply configuration (dry run)
      cisco.ios.ios_config:
        lines:
          - hostname {{ new_hostname }}
        backup: yes
      check_mode: yes
      register: config_diff

    - name: Show changes
      debug:
        var: config_diff
      when: config_diff is changed
```

## Parallelization

### Serial Execution
```yaml
---
- name: Serial deployment
  hosts: routers
  serial: 2  # Update 2 devices at a time, with rest waiting

  tasks:
    - name: Deploy configuration
      cisco.ios.ios_config:
        lines:
          - hostname {{ inventory_hostname }}

    - name: Verify change
      cisco.ios.ios_command:
        commands: show version
      register: version_output
```

## Variable Management

### Group and Host Variables
```yaml
# group_vars/routers.yaml
---
ansible_network_os: cisco.ios.ios
ansible_connection: network_cli
ntp_servers:
  - 8.8.8.8
  - 8.8.4.4

# host_vars/router1.yaml
---
site: DC1
device_type: core
bgp_asn: 65001
bgp_peers:
  - ip: 10.0.0.1
    asn: 65002
```

## Testing and Validation

### Pre-Deployment Checks
```yaml
---
- name: Pre-deployment validation
  hosts: routers
  gather_facts: no

  tasks:
    - name: Check device accessibility
      wait_for:
        host: "{{ ansible_host }}"
        port: 22
        timeout: 10

    - name: Verify minimum free memory
      cisco.ios.ios_command:
        commands: show memory | include Processor
      register: memory_output

    - name: Fail if low memory
      fail:
        msg: "Insufficient memory on {{ inventory_hostname }}"
      when: "'Free Memory' not in memory_output.stdout[0]"
```

### Post-Deployment Validation
```yaml
---
- name: Post-deployment validation
  hosts: routers
  gather_facts: no

  tasks:
    - name: Verify interface status
      cisco.ios.ios_command:
        commands: show interfaces | include {{ item }}
      register: interface_status
      failed_when: "'up' not in interface_status.stdout[0]"
      loop: "{{ interfaces_to_verify }}"

    - name: Verify routing adjacencies
      cisco.ios.ios_command:
        commands: show ip bgp summary
      register: bgp_summary

    - name: Check BGP neighbors
      assert:
        that:
          - "'Established' in bgp_summary.stdout[0]"
        fail_msg: "BGP neighbors not established"
```

## Best Practices

1. **Idempotency**: Ensure playbooks can be run multiple times safely
   ```yaml
   - cisco.ios.ios_config:
       lines: "{{ config_lines }}"
       match: line  # Only change lines that differ
   ```

2. **Backup Before Changes**: Always backup configuration
   ```yaml
   - cisco.ios.ios_config:
       backup: yes
       backup_options:
         dir_path: ./backups
   ```

3. **Use Variables**: Never hardcode values
   ```yaml
   vars:
     site_bgp_asn: "{{ hostvars[inventory_hostname]['bgp_asn'] }}"
   ```

4. **Tag Tasks**: Enable selective execution
   ```yaml
   - name: Apply routing config
     tags: routing
   ```

5. **Use Blocks**: Organize and handle errors
   ```yaml
   - block:
       - task1
       - task2
     rescue:
       - recovery_task
   ```

---

**Last Updated**: 2025-11-19
