# Jinja2 Configuration Templates Guide

## Template Basics

### Simple Variable Substitution
```jinja2
! Router Configuration
hostname {{ router_name }}
ip domain-name {{ domain_name }}
ip name-server {{ primary_dns }} {{ secondary_dns }}
```

### Template File Structure
```
templates/
├── cisco_router.j2
├── cisco_switch.j2
├── juniper_router.j2
├── base/
│   ├── ntp.j2
│   ├── logging.j2
│   └── aaa.j2
└── routing/
    ├── bgp.j2
    └── ospf.j2
```

## Control Structures

### Conditional Configuration
```jinja2
! Configure OSPF if enabled
{% if ospf_enabled %}
router ospf {{ ospf_pid }}
  router-id {{ router_id }}
  {% if ospf_authentication %}
  area 0 authentication message-digest
  {% endif %}
!
{% endif %}

! Configure BGP only for ASR devices
{% if device_model == "ASR1001-X" %}
router bgp {{ bgp_asn }}
  bgp router-id {{ router_id }}
!
{% endif %}
```

### Loops
```jinja2
! Configure multiple interfaces
{% for interface in interfaces %}
interface {{ interface.name }}
  description {{ interface.description }}
  ip address {{ interface.ip }} {{ interface.netmask }}
  {% if interface.ospf_cost %}
  ip ospf cost {{ interface.ospf_cost }}
  {% endif %}
  no shutdown
!
{% endfor %}

! Conditional loops
{% for vlan in vlans if vlan.active %}
vlan {{ vlan.id }}
  name {{ vlan.name }}
!
{% endfor %}
```

### Complex Nesting
```jinja2
! Multi-level configuration
{% for site in sites %}
! ===== {{ site.name }} =====
{% for device in site.devices %}
! Device: {{ device.hostname }}
interface {{ device.wan_interface }}
  ip address {{ device.wan_ip }} 255.255.255.0
  {% if device.bgp_enabled %}
  neighbor {{ site.bgp_neighbor }} remote-as {{ site.bgp_asn }}
  {% endif %}
!
{% endfor %}
{% endfor %}
```

## Filters

### String Filters
```jinja2
! Lowercase hostname
hostname {{ router_name | lower }}

! Uppercase description
description {{ interface_desc | upper }}

! Title case VLAN name
vlan {{ vlan_id }}
  name {{ vlan_name | title }}

! Replace characters
{% set clean_name = hostname | replace("-", "_") | replace(".", "_") %}
syslog source-interface {{ clean_name }}

! Split and join
ip route {% for subnet in subnets | split(",") %}{{ subnet.strip() }} null0
{% endfor %}
```

### List Filters
```jinja2
! Get list length
{% if dns_servers | length > 0 %}
! DNS servers configured
{% for server in dns_servers %}
ip name-server {{ server }}
{% endfor %}
{% endif %}

! Filter active devices
{% for device in devices | selectattr("state", "equalto", "active") %}
! Configure {{ device.name }}
!
{% endfor %}

! Get unique values
! NTP servers (unique only)
{% for server in ntp_servers | unique %}
ntp server {{ server }}
{% endfor %}

! Sort interfaces
{% for interface in interfaces | sort(attribute="name") %}
interface {{ interface.name }}
!
{% endfor %}

! Sum bandwidth
total-bandwidth: {{ interfaces | map(attribute="bandwidth") | sum }}
```

### Network-Specific Filters
```jinja2
! IP address filters
{% set subnet = "192.168.1.0/24" | cidr_subnet(size=26) %}
{% set broadcast = "10.0.0.0/8" | ipaddr("broadcast") %}

! Convert CIDR to netmask
network {{ ip_network }} netmask {{ ip_network | cidr_netmask }}
```

## Real-World Templates

### Cisco Router Template
```jinja2
! Configuration for {{ hostname }}
! Generated: {{ ansible_date_time.iso8601 }}
! Device Type: {{ device_type }}

hostname {{ hostname }}
!
ip domain-name {{ domain_name }}
ip domain-lookup
!
{# Logging Configuration #}
logging buffered 4096
logging level informational
{% if syslog_server %}
logging {{ syslog_server }}
{% endif %}
!
{# NTP Configuration #}
{% if ntp_servers %}
ntp authentication
ntp authenticate
ntp trusted-key 1
{% for server in ntp_servers %}
ntp server {{ server }}
{% endfor %}
!
{% endif %}

{# Interface Configuration #}
{% for interface in interfaces %}
interface {{ interface.name }}
  description {{ interface.description }}
  {% if interface.mtu %}
  mtu {{ interface.mtu }}
  {% endif %}
  {% if interface.enabled %}
  no shutdown
  {% else %}
  shutdown
  {% endif %}
  {% if interface.ip_address %}
  ip address {{ interface.ip_address }} {{ interface.netmask }}
  {% endif %}
  {% if interface.ospf_cost %}
  ip ospf cost {{ interface.ospf_cost }}
  {% endif %}
  {% if interface.vlan %}
  switchport mode access
  switchport access vlan {{ interface.vlan }}
  {% endif %}
!
{% endfor %}

{# BGP Configuration #}
{% if bgp_enabled %}
router bgp {{ bgp_asn }}
  bgp router-id {{ router_id }}
  bgp log-neighbor-changes
  !
  {% for neighbor in bgp_neighbors %}
  neighbor {{ neighbor.ip }} remote-as {{ neighbor.remote_asn }}
  neighbor {{ neighbor.ip }} description {{ neighbor.description }}
  {% endfor %}
  !
  address-family ipv4
  {% for network in bgp_networks %}
    network {{ network }} mask {{ bgp_mask }}
  {% endfor %}
  {% for neighbor in bgp_neighbors %}
    neighbor {{ neighbor.ip }} activate
  {% endfor %}
  exit-address-family
!
{% endif %}

{# OSPF Configuration #}
{% if ospf_enabled %}
router ospf {{ ospf_pid }}
  router-id {{ router_id }}
  passive-interface default
  {% for interface in interfaces %}
    {% if not interface.ospf_passive %}
  no passive-interface {{ interface.name }}
    {% endif %}
  {% endfor %}
  {% for network in ospf_networks %}
  network {{ network.address }} {{ network.wildcard }} area {{ network.area }}
  {% endfor %}
!
{% endif %}

{# ACL Configuration #}
{% for acl in access_lists %}
access-list {{ acl.number }} {{ acl.action }} {{ acl.source }}
{% endfor %}
!
end
```

### Juniper Configuration Template
```jinja2
# Configuration for {{ hostname }}
# Generated: {{ ansible_date_time.iso8601 }}

set system hostname {{ hostname }}
set system domain-name {{ domain_name }}

{# Interfaces #}
{% for interface in interfaces %}
# {{ interface.description }}
set interfaces {{ interface.name }} description "{{ interface.description }}"
set interfaces {{ interface.name }} mtu {{ interface.mtu | default(1500) }}
set interfaces {{ interface.name }} unit 0 family inet address {{ interface.ip }}/{{ interface.prefix_length }}
{% if interface.secondary_ip %}
set interfaces {{ interface.name }} unit 0 family inet address {{ interface.secondary_ip }}/{{ interface.prefix_length }}
{% endif %}
{% endfor %}

{# Routing #}
set routing-options router-id {{ router_id }}
set routing-options autonomous-system {{ bgp_asn }}

{# Static routes #}
{% for route in static_routes %}
set routing-options static route {{ route.destination }} next-hop {{ route.next_hop }}
{% endfor %}

{# BGP Configuration #}
{% for peer in bgp_peers %}
set protocols bgp group {{ peer.group }} neighbor {{ peer.ip }} remote-as {{ peer.remote_asn }}
{% endfor %}

{# OSPF Configuration #}
{% if ospf_enabled %}
{% for area in ospf_areas %}
set protocols ospf area {{ area.id }}
{% for interface in area.interfaces %}
  set protocols ospf area {{ area.id }} interface {{ interface }}
{% endfor %}
{% endfor %}
{% endif %}
```

## Dynamic Configuration Generation

### Ansible Playbook Using Templates
```yaml
---
- name: Generate and deploy network configurations
  hosts: routers
  gather_facts: no

  vars:
    template_dir: templates/

  tasks:
    - name: Load device variables
      include_vars:
        file: "host_vars/{{ inventory_hostname }}.yaml"

    - name: Generate configuration from template
      template:
        src: "{{ template_dir }}/{{ device_type }}_router.j2"
        dest: "/tmp/{{ inventory_hostname }}_generated.conf"
      register: generated_config

    - name: Show generated configuration
      debug:
        msg: "Generated config saved to {{ generated_config.dest }}"

    - name: Deploy configuration
      cisco.ios.ios_config:
        src: "/tmp/{{ inventory_hostname }}_generated.conf"
        save_when: changed
      register: deploy_result

    - name: Save configuration to Git repo
      copy:
        src: "/tmp/{{ inventory_hostname }}_generated.conf"
        dest: "configs/{{ inventory_hostname }}_{{ ansible_date_time.date }}.conf"
      delegate_to: localhost

    - name: Commit to Git
      shell: |
        cd {{ playbook_dir }}/..
        git add configs/
        git commit -m "config: update {{ inventory_hostname }} configuration"
        git push origin main
      delegate_to: localhost
      when: deploy_result is changed
```

## Template Variables Organization

### Host Variables (host_vars/router1.yaml)
```yaml
---
hostname: router-core-01
router_id: 10.1.1.1
bgp_asn: 65001
ospf_pid: 1

interfaces:
  - name: Ethernet0/0
    description: ISP Link
    ip_address: 203.0.113.1
    netmask: 255.255.255.0
    ospf_cost: 100

  - name: Ethernet0/1
    description: Internal Link
    ip_address: 10.0.0.1
    netmask: 255.255.255.0
    ospf_cost: 10

bgp_enabled: true
bgp_neighbors:
  - ip: 203.0.113.254
    remote_asn: 65000
    description: ISP Router

ospf_enabled: true
ospf_networks:
  - address: 10.0.0.0
    wildcard: 0.0.0.255
    area: 0
```

## Template Testing

### Validating Templates Locally
```bash
# Test Jinja2 rendering locally
python3 << EOF
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates/'))
template = env.get_template('cisco_router.j2')

vars = {
    'hostname': 'test-router',
    'domain_name': 'example.com',
    'interfaces': [
        {'name': 'Gi0/0/0', 'ip_address': '10.0.0.1', 'netmask': '255.255.255.0'}
    ]
}

output = template.render(vars)
print(output)
EOF
```

### Using Ansible Check Mode
```bash
# Generate templates without deploying
ansible-playbook playbooks/generate_configs.yaml --check

# Show what would change
ansible-playbook playbooks/generate_configs.yaml --check --diff
```

## Performance Optimization

### Lazy Evaluation
```jinja2
{# Avoid expensive operations #}
{% set interface_list = interfaces | list %}

{# Cache computed values #}
{% set active_interfaces = interfaces | selectattr("state", "equalto", "active") | list %}

{% for interface in active_interfaces %}
  {# Use cached list instead of recomputing #}
{% endfor %}
```

---

**Last Updated**: 2025-11-19
**Reference**: jinja.palletsprojects.com, docs.ansible.com/ansible/latest/user_guide/playbooks_templating.html
