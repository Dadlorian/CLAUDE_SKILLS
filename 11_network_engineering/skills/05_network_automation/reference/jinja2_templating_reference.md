# Jinja2 Templating Reference for Network Automation

## Basic Syntax

### Variable Substitution
```jinja2
hostname {{ device_name }}
!
ip domain-name {{ domain_name }}
```

### Data Types
```jinja2
{# Strings #}
description {{ interface_description }}

{# Numbers #}
metric {{ ospf_metric }}

{# Booleans #}
{% if is_enabled %}enabled{% endif %}

{# Lists #}
{% for vlan in vlans %}
  vlan {{ vlan }}
{% endfor %}

{# Dictionaries #}
ip address {{ interfaces['eth0']['ip'] }} {{ interfaces['eth0']['mask'] }}
```

## Control Structures

### If/Else Statements
```jinja2
{# Simple if #}
{% if device_type == "router" %}
  router bgp {{ asn }}
{% endif %}

{# If/else #}
{% if device_role == "core" %}
  redundancy
  mode sso
{% else %}
  no redundancy
{% endif %}

{# Else if #}
{% if device_vendor == "cisco" %}
  ios configuration
{% elif device_vendor == "juniper" %}
  junos configuration
{% else %}
  generic configuration
{% endif %}
```

### For Loops
```jinja2
{# Basic loop #}
{% for interface in interfaces %}
interface {{ interface.name }}
  description {{ interface.description }}
  ip address {{ interface.ip }} {{ interface.mask }}
{% endfor %}

{# Loop with index #}
{% for item in items %}
  {{ loop.index }}: {{ item }}
{% endfor %}

{# Loop with conditions #}
{% for vlan in vlans %}
  {% if vlan.status == "active" %}
    vlan {{ vlan.id }}
      name {{ vlan.name }}
  {% endif %}
{% endfor %}

{# Nested loops #}
{% for device in devices %}
  Device: {{ device.name }}
  {% for interface in device.interfaces %}
    Interface: {{ interface.name }}
  {% endfor %}
{% endfor %}
```

### Loop Variables
```jinja2
{% for item in items %}
  {% if loop.first %}First: {{ item }}{% endif %}
  {% if loop.last %}Last: {{ item }}{% endif %}
  Item #{{ loop.index }} ({{ loop.index0 }}): {{ item }}
  Remaining: {{ loop.revindex }}
{% endfor %}
```

## Filters

### String Filters
```jinja2
{# Lowercase #}
hostname {{ device_name | lower }}

{# Uppercase #}
{% if {{ status | upper }} == "ACTIVE" %}

{# Title case #}
description {{ description | title }}

{# Replace #}
{% set interface_name = name | replace("-", "_") %}

{# Split #}
{% for part in vlan_list | split(",") %}
  vlan {{ part.strip() }}
{% endfor %}

{# Join #}
static route {{ networks | join(" ") }}
```

### List Filters
```jinja2
{# Length #}
{% if vlans | length > 0 %}

{# Sort #}
{% for vlan in vlans | sort %}

{# Unique #}
{% for ip in ip_list | unique %}

{# Select (filter) #}
{% for device in devices | select("equalto", "active") %}

{# Reject (inverse filter) #}
{% for device in devices | reject("equalto", "failed") %}

{# Sum #}
Total bandwidth: {{ interfaces | map(attribute='bandwidth') | sum }}
```

### Arithmetic Filters
```jinja2
{# Default value #}
metric {{ ospf_metric | default(100) }}

{# Int conversion #}
vlan {{ vlan_id | int }}

{# Abs value #}
priority {{ priority_value | abs }}

{# Round #}
reserved memory: {{ memory | round(0) }} MB
```

### Custom Filters
```python
# Define custom filter in Python
from jinja2 import Environment

def network_to_wildcard(network):
    """Convert network to wildcard mask"""
    from ipaddress import ip_network
    net = ip_network(network)
    wildcard = ip_network((net.broadcast_address ^ net.netmask).__str__())
    return str(wildcard.network_address)

env = Environment()
env.filters['to_wildcard'] = network_to_wildcard
```

Using custom filter:
```jinja2
access-list 101 permit ip {{ network }} {{ network | to_wildcard }}
```

## Advanced Features

### Set Variables
```jinja2
{% set device_ip = "192.168.1.1" %}
{% set bgp_peers = ["10.0.0.1", "10.0.0.2"] %}

hostname {{ device_name }}
ip address {{ device_ip }}

{% for peer in bgp_peers %}
  neighbor {{ peer }} remote-as {{ asn }}
{% endfor %}
```

### Whitespace Control
```jinja2
{# Default: preserves whitespace #}
{% for item in items %}
  {{ item }}
{% endfor %}

{# Strip leading whitespace #}
{%- for item in items %}
  {{ item }}
{%- endfor %}

{# Strip trailing whitespace #}
{% for item in items -%}
  {{ item }}
{% endfor -%}

{# Both sides #}
{%- for item in items -%}
  {{ item }}
{%- endfor -%}
```

### Comments
```jinja2
{# This is a comment and won't appear in output #}
hostname {{ device_name }}

{# Multi-line comment
   This won't be rendered either
   Useful for notes about template logic
#}
```

### Include Other Templates
```jinja2
{# Include base configuration #}
{% include 'base_config.j2' %}

{# Include with variables #}
{% include 'interface_config.j2' with context %}

{# Include specific file #}
{% include 'cisco/ios_config.j2' %}
```

### Extends for Template Inheritance
```jinja2
{# Base template: base_device_config.j2 #}
hostname {{ device_name }}
!
{% block interfaces %}{% endblock %}
!
{% block routing %}{% endblock %}

{# Child template: cisco_ios_config.j2 #}
{% extends "base_device_config.j2" %}

{% block interfaces %}
{% for iface in interfaces %}
interface {{ iface.name }}
  ip address {{ iface.ip }} {{ iface.mask }}
{% endfor %}
{% endblock %}

{% block routing %}
router ospf {{ ospf_pid }}
  router-id {{ router_id }}
{% endblock %}
```

## Network Automation Examples

### Router Configuration Template
```jinja2
! Generated configuration for {{ hostname }}
! Device type: {{ device_type }}
! Generated: {{ ansible_date_time.iso8601 }}

hostname {{ hostname }}
!
ip domain-name {{ domain_name }}
ip domain-lookup
!
{# IP address configuration #}
{% for interface in interfaces %}
interface {{ interface.name }}
  description {{ interface.description }}
  ip address {{ interface.ip_address }} {{ interface.subnet_mask }}
  {% if interface.secondary_ip %}
  ip address {{ interface.secondary_ip }} {{ interface.secondary_mask }} secondary
  {% endif %}
  {% if interface.ospf_cost %}
  ip ospf cost {{ interface.ospf_cost }}
  {% endif %}
  no shutdown
!
{% endfor %}

{# Routing configuration #}
{% if routing_protocol == "ospf" %}
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
{% elif routing_protocol == "bgp" %}
router bgp {{ bgp_asn }}
  router-id {{ router_id }}
  !
  {% for peer in bgp_peers %}
  neighbor {{ peer.ip }} remote-as {{ peer.remote_asn }}
  neighbor {{ peer.ip }} description {{ peer.description }}
  {% endfor %}
  !
  address-family ipv4
  {% for network in bgp_networks %}
    network {{ network }} mask {{ bgp_network_mask }}
  {% endfor %}
  {% for peer in bgp_peers %}
    neighbor {{ peer.ip }} activate
  {% endfor %}
  exit-address-family
!
{% endif %}

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

{# SNMP Configuration #}
{% if snmp_enabled %}
snmp-server community {{ snmp_community }} RO
snmp-server location {{ snmp_location }}
snmp-server contact {{ snmp_contact }}
{% for trap in snmp_traps %}
snmp-server enable traps {{ trap }}
{% endfor %}
!
{% endif %}

{# Logging #}
logging buffered 4096
logging {{ syslog_server }}
logging facility local7
!
end
```

### Cisco Switch VLAN Template
```jinja2
! VLAN Configuration for {{ switch_name }}

{% for vlan in vlans %}
vlan {{ vlan.id }}
  name {{ vlan.name }}
  {% if vlan.shutdown %}shutdown{% endif %}
!
{% endfor %}

{# VLAN Interfaces #}
{% for vlan in vlans %}
  {% if vlan.svi_ip %}
interface vlan {{ vlan.id }}
  description {{ vlan.name }} SVI
  ip address {{ vlan.svi_ip }} {{ vlan.subnet_mask }}
  {% if vlan.gateway %}
  ip default-gateway {{ vlan.gateway }}
  {% endif %}
  no shutdown
!
  {% endif %}
{% endfor %}

{# Port Configuration #}
{% for port in ports %}
interface {{ port.name }}
  description {{ port.description }}
  {% if port.mode == "trunk" %}
  switchport mode trunk
  switchport trunk allowed vlan {{ port.allowed_vlans | join(",") }}
  {% else %}
  switchport mode access
  switchport access vlan {{ port.access_vlan }}
  {% endif %}
  {% if port.spanning_tree %}
  spanning-tree portfast
  spanning-tree bpduguard enable
  {% endif %}
  no shutdown
!
{% endfor %}
```

### Juniper Configuration Template
```jinja2
# Configuration for {{ hostname }}
# Generated {{ ansible_date_time.iso8601 }}

set system hostname {{ hostname }}
set system domain-name {{ domain_name }}

{% for interface in interfaces %}
# Interface {{ interface.name }}
set interfaces {{ interface.name }} description "{{ interface.description }}"
{% if interface.mtu %}
set interfaces {{ interface.name }} mtu {{ interface.mtu }}
{% endif %}
set interfaces {{ interface.name }} unit 0 family inet address {{ interface.ip }}/{{ interface.prefix_length }}
{% endfor %}

{# Routing #}
{% if routing_protocol == "bgp" %}
set routing-options router-id {{ router_id }}
set routing-options autonomous-system {{ bgp_asn }}

{% for peer in bgp_peers %}
set protocols bgp group {{ peer.group }} neighbor {{ peer.ip }} remote-as {{ peer.remote_asn }}
{% endfor %}
{% endif %}
```

## Best Practices

### 1. Keep Templates Clean
```jinja2
# Good: Clear, organized
{% for interface in interfaces %}
  interface {{ interface.name }}
    ip address {{ interface.ip }}
{% endfor %}

# Bad: Unclear logic
{% for i in interfaces %} interface {{ i['n'] }} ip address {{ i['a'] }} {% endfor %}
```

### 2. Use Meaningful Variable Names
```jinja2
# Good
hostname {{ device_hostname }}
router-id {{ ospf_router_id }}

# Bad
hostname {{ h }}
router-id {{ rid }}
```

### 3. Comment Complex Logic
```jinja2
{# Filter only active interfaces and create IP config #}
{% for interface in interfaces | selectattr('state', 'equalto', 'active') %}
  interface {{ interface.name }}
    ip address {{ interface.ip }}
{% endfor %}
```

### 4. Use Defaults Wisely
```jinja2
hostname {{ hostname | default('router') }}
metric {{ metric | default(100) }}
```

### 5. Validate in Python
```python
from jinja2 import Environment, FileSystemLoader, undefined

# Strict mode catches undefined variables
env = Environment(
    loader=FileSystemLoader('templates/'),
    undefined=StrictUndefined
)

template = env.get_template('config.j2')
output = template.render(
    hostname='router1',
    interfaces=[...]
)
```

---

**Last Updated**: 2025-11-19
**Reference**: jinja.palletsprojects.com, docs.ansible.com/ansible/latest/user_guide/playbooks_templating.html
