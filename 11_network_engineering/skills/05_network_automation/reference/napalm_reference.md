# NAPALM Reference Guide

## Overview

NAPALM (Network Automation and Programmability Abstraction Layer with Multivendor support) provides a unified API for device management across multiple vendors.

## Installation
```bash
pip install napalm
pip install napalm[ios,iosxr,junos,eos,nxos]  # Install specific drivers
```

## Supported Vendors
- Cisco IOS
- Cisco IOS-XR
- Cisco NX-OS
- Juniper Junos
- Arista EOS
- HP Comware
- Dell OS10
- Checkpoint Gaia
- Checkpoint SMG
- And more...

## Basic Usage

### Connection
```python
from napalm import get_network_driver

# Initialize driver
driver = get_network_driver('ios')

# Create device connection
device = driver('192.168.1.1', 'admin', 'password')

# Open connection
device.open()

# Close connection
device.close()

# Context manager (recommended)
with driver('192.168.1.1', 'admin', 'password') as device:
    facts = device.get_facts()
    print(facts)
```

## Available Getters

### Device Information

#### get_facts()
```python
device.open()
facts = device.get_facts()

# Returns:
{
    'uptime': 2592000,  # seconds
    'vendor': 'Cisco',
    'os_version': '17.6.1',
    'serial_number': 'FCW2220A1234',
    'model': 'Cisco 4331',
    'hostname': 'router1',
    'fqdn': 'router1.example.com',
    'interface_list': ['Gi0/0/0', 'Gi0/0/1']
}

for key, value in facts.items():
    print(f"{key}: {value}")
```

### Interface Management

#### get_interfaces()
```python
interfaces = device.get_interfaces()

# Returns:
{
    'Gi0/0/0': {
        'is_up': True,
        'is_enabled': True,
        'mtu': 1500,
        'description': 'WAN Interface',
        'last_flapped': -1,
        'speed': 1000,
        'mac_address': '00:11:22:33:44:55'
    },
    'Gi0/0/1': {
        'is_up': True,
        'is_enabled': True,
        'mtu': 1500,
        'description': '',
        'last_flapped': -1,
        'speed': 1000,
        'mac_address': '00:11:22:33:44:66'
    }
}

for intf_name, intf_data in interfaces.items():
    print(f"{intf_name}: {'up' if intf_data['is_up'] else 'down'}")
```

#### get_interfaces_ip()
```python
interfaces_ip = device.get_interfaces_ip()

# Returns:
{
    'Gi0/0/0': {
        'ipv4': {
            '192.168.1.1': {
                'prefix_length': 24
            }
        },
        'ipv6': {
            '2001:db8::1': {
                'prefix_length': 64
            }
        }
    }
}

for intf, config in interfaces_ip.items():
    if config.get('ipv4'):
        for ip, data in config['ipv4'].items():
            print(f"{intf}: {ip}/{data['prefix_length']}")
```

### Network Routing

#### get_route_to()
```python
# Get route to specific destination
route = device.get_route_to('8.8.8.8')

# Returns:
{
    '8.8.8.8/32': {
        'protocol': 'bgp',
        'current_active': True,
        'last_active': True,
        'age': 3600,
        'next_hop': {
            'IP': '10.0.0.1',
            'global_neighbor_id': '',
            'local_neighbor_id': '',
            'vrf': 'default',
            'interface': 'Gi0/0/0'
        },
        'routing_table': 'default',
        'selected_next_hop': True,
        'preference': 20,
        'inactive_reason': '',
        'install_date': 1234567890,
        'metric': 100
    }
}
```

#### get_bgp_neighbors_detail()
```python
bgp_neighbors = device.get_bgp_neighbors_detail()

# Returns:
{
    'default': {
        'peers': {
            '10.0.0.1': {
                'local_as': 65001,
                'remote_as': 65002,
                'remote_id': '10.0.0.1',
                'last_event': 'RecvOpen',
                'previous_connection_state': 'Connect',
                'routing_table': 'default',
                'sent_open': 0,
                'last_event_changed': 3600,
                'previous_session_state': 'OpenConfirm',
                'session_state': 'Established',
                'enabled': True,
                'description': 'ISP Router'
            }
        }
    }
}

for neighbor_ip, neighbor_data in bgp_neighbors['default']['peers'].items():
    state = neighbor_data['session_state']
    print(f"{neighbor_ip}: {state}")
```

#### get_lldp_neighbors()
```python
lldp = device.get_lldp_neighbors()

# Returns:
{
    'Gi0/0/0': [
        {
            'hostname': 'switch1',
            'port': 'Gi0/0/10'
        }
    ],
    'Gi0/0/1': [
        {
            'hostname': 'router2',
            'port': 'Gi0/0/0'
        }
    ]
}

for intf, neighbors in lldp.items():
    for neighbor in neighbors:
        print(f"{intf} -> {neighbor['hostname']} ({neighbor['port']})")
```

### Configuration Management

#### get_config()
```python
config = device.get_config(retrieve='running')

# Or specific source
running = device.get_config(retrieve='running')
startup = device.get_config(retrieve='startup')
candidate = device.get_config(retrieve='candidate')

print(running['running_config'])
```

#### load_candidate_config()
```python
# Load from string
new_config = """
interface Gi0/0/1
 ip address 10.0.0.1 255.255.255.0
 no shutdown
"""

device.load_candidate_config(config=new_config)

# Load from file
device.load_candidate_config(filename='new_config.conf')
```

#### compare_config()
```python
# Compare loaded candidate with running
diff = device.compare_config()

if diff:
    print("Changes to be applied:")
    print(diff)
else:
    print("No changes")

# Returns:
"""
+interface Gi0/0/1
+ip address 10.0.0.1 255.255.255.0
+no shutdown
-interface Gi0/0/2
"""
```

#### commit_config()
```python
# Apply candidate config
device.commit_config()

# Or with message
device.commit_config(message="Deploy new interface configuration")
```

#### discard_config()
```python
# Discard loaded candidate config
device.discard_config()
```

### Table Operations

#### get_arp_table()
```python
arp = device.get_arp_table()

# Returns:
{
    'interface': 'Gi0/0/0',
    'mac_address': '00:11:22:33:44:55',
    'ip': '192.168.1.100',
    'age': 245
}

for entry in arp:
    print(f"{entry['ip']} -> {entry['mac_address']}")
```

#### get_mac_address_table()
```python
mac_table = device.get_mac_address_table()

# Returns:
{
    'mac': '00:11:22:33:44:55',
    'interface': 'Gi0/0/0',
    'vlan': 100,
    'static': False,
    'active': True,
    'moves': 0,
    'last_move': 0.0
}

for entry in mac_table:
    print(f"VLAN {entry['vlan']}: {entry['mac']} on {entry['interface']}")
```

#### get_vlan_interfaces()
```python
vlan_ifaces = device.get_vlan_interfaces()

# Returns:
{
    'vlan_name': 'Management',
    'vlan_id': 1,
    'interfaces': ['Gi0/0/0', 'Gi0/0/1', 'Gi0/0/2']
}

for vlan in vlan_ifaces:
    print(f"VLAN {vlan['vlan_id']}: {', '.join(vlan['interfaces'])}")
```

### Network Services

#### get_ntp_servers()
```python
ntp = device.get_ntp_servers()

# Returns:
{
    '8.8.8.8': {
        'stratum': 1,
        'ref_clock_id': 'GPS',
        'prefer': True
    }
}

for server_ip, server_data in ntp.items():
    print(f"NTP Server: {server_ip} (Stratum {server_data['stratum']})")
```

#### get_snmp_information()
```python
snmp = device.get_snmp_information()

# Returns:
{
    'snmp_community': [
        {
            'name': 'public',
            'acl': '',
            'mode': 'RO'
        }
    ],
    'contact': 'network@example.com',
    'location': 'Data Center 1'
}
```

### User Management

#### get_users()
```python
users = device.get_users()

# Returns:
{
    'admin': {
        'level': 15,
        'password': '',
        'sshkeys': []
    },
    'readonly': {
        'level': 1,
        'password': '',
        'sshkeys': ['ssh-rsa AAAAB3NzaC1yc2E...']
    }
}
```

## Configuration Deployment

### Multi-Device Deployment
```python
from napalm import get_network_driver

devices = [
    {'host': '192.168.1.1', 'user': 'admin', 'pass': 'pass'},
    {'host': '192.168.1.2', 'user': 'admin', 'pass': 'pass'},
    {'host': '192.168.1.3', 'user': 'admin', 'pass': 'pass'},
]

driver = get_network_driver('ios')

for device_params in devices:
    device = driver(
        device_params['host'],
        device_params['user'],
        device_params['pass']
    )

    device.open()

    # Load configuration
    config_text = """
    interface Gi0/0/0
     ip address 10.0.0.1 255.255.255.0
     no shutdown
    """

    device.load_candidate_config(config=config_text)

    # Compare
    diff = device.compare_config()
    print(f"\n{device_params['host']}:")
    print(diff)

    # Commit if approved
    if input("Apply changes? (y/n): ").lower() == 'y':
        device.commit_config()
    else:
        device.discard_config()

    device.close()
```

## Error Handling

```python
from napalm import get_network_driver
from napalm.base.exceptions import ConnectionException

try:
    driver = get_network_driver('ios')
    device = driver('192.168.1.1', 'admin', 'password')
    device.open()

    facts = device.get_facts()
    print(facts)

except ConnectionException as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    device.close()
```

## Limitations

- Read-only on some operations (OS-dependent)
- Some vendor-specific features may not be available
- Configuration deployment is template-based (no rollback on error)
- Async operations not natively supported

## Comparison with Alternatives

| Feature | NAPALM | Netmiko | Ansible | Nornir |
|---------|--------|---------|---------|--------|
| Multi-vendor | Excellent | Excellent | Excellent | Excellent |
| Unified API | Yes | No | Yes | No |
| Config parsing | Yes | No | Yes | No |
| State validation | Yes | No | Limited | No |
| Ease of use | Easy | Easy | Medium | Medium |

---

**Last Updated**: 2025-11-19
**Reference**: napalm.readthedocs.io, github.com/napalm-automation/napalm
