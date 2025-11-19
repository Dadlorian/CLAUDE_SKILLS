# Ansible Network Modules Reference

## Core Network Modules

### Device Configuration Modules

#### ios_config / ios_command
```yaml
# Cisco IOS configuration management
- name: Configure interface
  cisco.ios.ios_config:
    lines:
      - description "WAN Interface"
      - ip address 192.168.1.1 255.255.255.0
      - no shutdown
    parents: interface Ethernet0/0
    backup: yes

- name: Execute show command
  cisco.ios.ios_command:
    commands: show ip interface brief
```

#### iosxr_config / iosxr_command
```yaml
# Cisco IOS-XR configuration
- name: Configure BGP
  cisco.iosxr.iosxr_config:
    lines:
      - router bgp 65001
      - neighbor 10.0.0.1 remote-as 65002

- name: Get running config
  cisco.iosxr.iosxr_command:
    commands: show running-config
```

#### junos_config / junos_command
```yaml
# Juniper Junos configuration
- name: Configure Junos interface
  junipernetworks.junos.junos_config:
    lines:
      - set interfaces ge-0/0/0 unit 0 family inet address 10.0.0.1/24
      - set interfaces ge-0/0/0 description "WAN-Link"

- name: Get Junos facts
  junipernetworks.junos.junos_command:
    commands: show interface brief
```

### Fact Gathering Modules

#### ios_facts / iosxr_facts / junos_facts
```yaml
- name: Gather Cisco IOS facts
  cisco.ios.ios_facts:
    gather_subset: all
  register: ios_facts

- name: Gather Juniper Junos facts
  junipernetworks.junos.junos_facts:
    gather_subset: all
  register: junos_facts

- name: Display gathered facts
  debug:
    msg: "Device: {{ inventory_hostname }} - Version: {{ ansible_net_version }}"
```

### Network Interface Modules

#### ios_interface / junos_interface
```yaml
- name: Configure interface
  cisco.ios.ios_interface:
    name: GigabitEthernet0/0/1
    description: "Core-Link"
    mtu: 1500
    enabled: yes
    speed: 1000
    duplex: full

- name: Configure Junos interface
  junipernetworks.junos.junos_interface:
    name: ge-0/0/0
    description: "WAN-Interface"
    mtu: 1500
    enabled: yes
```

### Routing Protocol Modules

#### ios_bgp / ios_ospf
```yaml
- name: Configure BGP
  cisco.ios.ios_bgp:
    config:
      bgp_as: 65001
      router_id: 10.1.1.1
      log_neighbor_changes: yes
      neighbors:
        - neighbor: 10.0.0.1
          remote_as: 65002

- name: Configure OSPF
  cisco.ios.ios_ospf:
    ospf: 1
    state: present
    process_id: 1
    router_id: 10.1.1.1
    redistribute:
      - connected
      - static
```

### ACL and Policy Modules

#### ios_acl / ios_acl_interfaces
```yaml
- name: Create access list
  cisco.ios.ios_acl:
    name: ALLOW_SSH
    acl_type: standard
    entries:
      - sequence: 10
        action: permit
        source: 10.0.0.0
        wildcard_bits: 0.0.0.255

- name: Apply ACL to interface
  cisco.ios.ios_acl_interfaces:
    name: GigabitEthernet0/0/1
    access_groups:
      - afi: ipv4
        acl_name: ALLOW_SSH
        direction: in
```

### VLAN Management Modules

#### ios_vlan
```yaml
- name: Create VLANs
  cisco.ios.ios_vlan:
    name: "Production"
    vlan_id: 100
    description: "Production VLAN"
    state: present

- name: Configure trunk
  cisco.ios.ios_config:
    lines:
      - switchport mode trunk
      - switchport trunk allowed vlan 100,200,300
    parents: interface GigabitEthernet0/0/1
```

### Static Routes

#### ios_static_routes / iosxr_static_routes
```yaml
- name: Configure static route
  cisco.ios.ios_static_routes:
    config:
      - destination:
          prefix: "192.168.0.0"
          mask: "255.255.255.0"
        next_hops:
          - next_hop_address: "10.0.0.1"

- name: Configure IOS-XR static route
  cisco.iosxr.iosxr_static_routes:
    config:
      - destination:
          prefix: "192.168.0.0"
          length: 24
        next_hops:
          - next_hop_address: "10.0.0.1"
```

### SNMP Configuration

#### ios_snmp_server
```yaml
- name: Configure SNMP
  cisco.ios.ios_snmp_server:
    state: present
    config:
      contact: "network-team@example.com"
      location: "Data Center 1"
      traps:
        - name: snmp
        - name: bgp
        - name: ospf
      engine_id: "800007E5"
```

### Logging Configuration

#### ios_logging
```yaml
- name: Configure syslog
  cisco.ios.ios_logging:
    dest: server
    name: 10.0.0.50
    facility: local7
    level: debugging
    state: present
```

## Execution Options

### Synchronous Execution
```yaml
- name: Configure device
  cisco.ios.ios_config:
    lines: interface Ethernet0/0
    async: false
```

### Asynchronous Execution
```yaml
- name: Long-running config
  cisco.ios.ios_config:
    lines: copy flash: tftp:
  async: 300  # 5 minute timeout
  poll: 0
  register: long_task

- name: Wait for async task
  async_status:
    jid: "{{ long_task.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 30
  delay: 10
```

## Common Patterns

### Rolling Configuration Updates
```yaml
- name: Update configuration serially
  hosts: all_routers
  serial: 2  # Update 2 devices at a time

  tasks:
    - name: Backup current config
      cisco.ios.ios_command:
        commands: show running-config
      register: config_backup

    - name: Apply new configuration
      cisco.ios.ios_config:
        lines: "{{ lookup('file', 'configs/{{ inventory_hostname }}.conf') }}"
        backup: yes
```

### Conditional Configuration
```yaml
- name: Configure based on device type
  cisco.ios.ios_config:
    lines:
      - "{% if device_type == 'router' %}router bgp 65001{% endif %}"
      - "{% if device_type == 'switch' %}vtp domain production{% endif %}"
```

### Gathering and Using Facts
```yaml
- name: Get device facts
  cisco.ios.ios_facts:
    gather_subset: all

- name: Configure based on current version
  cisco.ios.ios_config:
    lines: version 16
  when: ansible_net_version is version('16.0', '<')
```

## Error Handling

```yaml
- name: Configuration with error handling
  block:
    - name: Apply configuration
      cisco.ios.ios_config:
        lines: interface Ethernet0/0

  rescue:
    - name: Revert on failure
      debug:
        msg: "Configuration failed, reverting..."

  always:
    - name: Backup after attempt
      cisco.ios.ios_command:
        commands: show running-config
      register: post_config
```

## Best Practices

1. **Always backup before config changes**
   ```yaml
   backup: yes
   backup_options:
     filename: "{{ inventory_hostname }}_{{ ansible_date_time.iso8601_basic_short }}.cfg"
     dir_path: "./backups/"
   ```

2. **Use check mode for validation**
   ```bash
   ansible-playbook -i inventory playbook.yaml --check
   ```

3. **Implement idempotency**
   - Use exact line matching
   - Verify configuration states
   - Don't rely on ordering

4. **Leverage become for privilege escalation**
   ```yaml
   tasks:
     - name: Enable task
       cisco.ios.ios_config:
         commands: enable password cisco
       become: yes
       become_method: enable
   ```

---

**Reference**: ansible.com/docs/plugins/network.html
