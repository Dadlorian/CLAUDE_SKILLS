# Python Netmiko Guide

## Installation and Setup

```bash
pip install netmiko
pip install paramiko  # SSH implementation
pip install pyyaml    # For inventory files
```

## Basic Connection

### Simple SSH Connection
```python
from netmiko import ConnectHandler

# Define device parameters
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
    'port': 22,
    'secret': 'enable_password',  # For enable mode
}

# Connect to device
net_connect = ConnectHandler(**device)

# Send command
output = net_connect.send_command('show version')
print(output)

# Disconnect
net_connect.disconnect()
```

### Context Manager
```python
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
}

with ConnectHandler(**device) as net_connect:
    output = net_connect.send_command('show version')
    print(output)
# Automatically disconnects
```

## Sending Commands

### Single Command
```python
# Send non-interactive command
output = net_connect.send_command('show running-config')

# Send command expecting a string
output = net_connect.send_command(
    'reload',
    expect_string=r'Proceed with reload?'
)

# Send command with timing (buffer clearance)
output = net_connect.send_command_timing(
    'show running-config',
    delay_factor=2
)
```

### Multiple Commands
```python
commands = [
    'show version',
    'show ip interface brief',
    'show ip route',
    'show ip bgp summary'
]

for cmd in commands:
    output = net_connect.send_command(cmd)
    print(f"\n{'='*60}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    print(output)
```

### Batch Command Execution
```python
import json

commands = {
    'show_version': 'show version',
    'show_interfaces': 'show ip interface brief',
    'show_routes': 'show ip route',
    'show_bgp': 'show ip bgp summary'
}

outputs = {}
for key, command in commands.items():
    outputs[key] = net_connect.send_command(command)

# Save to file
with open('device_output.json', 'w') as f:
    json.dump(outputs, f, indent=2)
```

## Sending Configuration

### Single Configuration Line
```python
# Send single config command
output = net_connect.send_command_config('ip domain-name example.com')

# Send configuration line by line
net_connect.send_command_config('interface Ethernet0/0')
net_connect.send_command_config('ip address 192.168.1.1 255.255.255.0')
net_connect.send_command_config('no shutdown')
```

### Multiple Configuration Lines
```python
config_commands = [
    'interface Ethernet0/0',
    'description WAN Interface',
    'ip address 10.0.0.1 255.255.255.0',
    'no shutdown',
    'exit',
    'interface Ethernet0/1',
    'description LAN Interface',
    'ip address 192.168.1.1 255.255.255.0',
    'no shutdown'
]

# Send as list
output = net_connect.send_config_set(config_commands)
print(output)
```

### Configuration from File
```python
# Read configuration from file
with open('router_config.txt', 'r') as f:
    config_lines = f.readlines()

# Send configuration
output = net_connect.send_config_set(config_lines)
print(output)
```

## Interactive Commands

### Enable Mode on Cisco IOS
```python
# Send command requiring enable mode
net_connect.enable()

# Or specify secret password
net_connect.send_command(
    'configure terminal',
    secret='enable_password'
)
```

### Commands with User Interaction
```python
# Reload device with confirmation
output = net_connect.send_command(
    'reload',
    expect_string=r'Proceed with reload',
    delay_factor=2
)

# Confirm the reload
output = net_connect.send_command(
    'y',
    delay_factor=5
)

print("Device reloading...")
```

## Error Handling

### Exception Handling
```python
from netmiko import ConnectHandler
from netmiko.ssh_exception import (
    NetmikoTimeoutException,
    AuthenticationException,
    NetmikoAuthenticationException,
    NetmikoCommandTimeoutException
)

device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
    'timeout': 30
}

try:
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command('show version')
    print(output)

except AuthenticationException:
    print("Authentication failed - check credentials")

except NetmikoTimeoutException:
    print("Connection timeout - device may be unreachable")

except NetmikoCommandTimeoutException:
    print("Command execution timeout")

except Exception as e:
    print(f"Error: {e}")

finally:
    try:
        net_connect.disconnect()
    except:
        pass
```

## Multi-Device Management

### Device List Processing
```python
device_list = [
    {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password',
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.1.2',
        'username': 'admin',
        'password': 'password',
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.1.3',
        'username': 'admin',
        'password': 'password',
    }
]

for device in device_list:
    try:
        net_connect = ConnectHandler(**device)
        hostname = net_connect.send_command('show running-config | include hostname')
        print(f"{device['host']}: {hostname}")
        net_connect.disconnect()

    except Exception as e:
        print(f"Error connecting to {device['host']}: {e}")
```

### Parallel Device Processing
```python
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

devices = [
    {'device_type': 'cisco_ios', 'host': '192.168.1.1', 'username': 'admin', 'password': 'pass'},
    {'device_type': 'cisco_ios', 'host': '192.168.1.2', 'username': 'admin', 'password': 'pass'},
    {'device_type': 'cisco_ios', 'host': '192.168.1.3', 'username': 'admin', 'password': 'pass'},
]

def get_version(device):
    """Get device version"""
    try:
        net_connect = ConnectHandler(**device)
        output = net_connect.send_command('show version | include Version')
        net_connect.disconnect()
        return {device['host']: output}
    except Exception as e:
        return {device['host']: f"Error: {e}"}

# Execute in parallel
results = {}
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_device = {
        executor.submit(get_version, device): device
        for device in devices
    }

    for future in as_completed(future_to_device):
        results.update(future.result())

# Print results
for host, version in results.items():
    print(f"{host}: {version}")
```

## Configuration Backup

### Automated Backup
```python
from netmiko import ConnectHandler
from datetime import datetime
import os

device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
}

def backup_device(device_params, backup_dir='backups'):
    """Backup device configuration"""

    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)

    try:
        net_connect = ConnectHandler(**device_params)

        # Get running config
        config = net_connect.send_command('show running-config')

        # Get device hostname
        hostname_output = net_connect.send_command('show running-config | include hostname')
        hostname = hostname_output.split()[-1] if hostname_output else 'unknown'

        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{backup_dir}/{hostname}_{timestamp}.cfg"

        with open(filename, 'w') as f:
            f.write(config)

        net_connect.disconnect()

        print(f"✓ Backup saved: {filename}")
        return filename

    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return None

# Backup device
backup_file = backup_device(device)
```

## Device Type Reference

### Common Device Types
```python
device_types = {
    # Cisco
    'cisco_ios': 'Cisco IOS',
    'cisco_xe': 'Cisco IOS-XE',
    'cisco_xr': 'Cisco IOS-XR',
    'cisco_nxos': 'Cisco NX-OS',
    'cisco_asa': 'Cisco ASA',

    # Juniper
    'juniper': 'Juniper Junos',
    'juniper_junos': 'Juniper Junos',

    # Arista
    'arista_eos': 'Arista EOS',

    # HP
    'hp_comware': 'HP Comware',

    # Other
    'checkpoint_gaia': 'Check Point Gaia',
    'dell_os10': 'Dell OS10',
    'opengear_os': 'OpenGear OS',
    'paloalto_panos': 'Palo Alto PAN-OS',
}
```

## Advanced Features

### Session Logging
```python
# Enable session logging
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
    'session_log': 'device_session.log',  # Log to file
}

net_connect = ConnectHandler(**device)
```

### Keepalive and Timeouts
```python
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
    'timeout': 60,           # Connection timeout
    'conn_timeout': 30,      # Socket timeout
    'banner_timeout': 15,    # Banner read timeout
    'global_delay_factor': 2,  # Delay factor for all operations
}

net_connect = ConnectHandler(**device)
```

### Using SSH Keys
```python
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'use_keys': True,
    'key_file': '/home/user/.ssh/id_rsa',
    'timeout': 30,
}

net_connect = ConnectHandler(**device)
```

## Best Practices

1. **Always Use Context Manager**
   ```python
   with ConnectHandler(**device) as net_connect:
       output = net_connect.send_command('show version')
   ```

2. **Handle Exceptions**
   ```python
   try:
       net_connect = ConnectHandler(**device)
   except AuthenticationException:
       # Handle auth failure
   except NetmikoTimeoutException:
       # Handle timeout
   ```

3. **Use Delay Factors for Slow Devices**
   ```python
   output = net_connect.send_command(
       'copy running-config tftp://10.0.0.100/backup.cfg',
       delay_factor=5,
       max_loops=20
   )
   ```

4. **Backup Before Making Changes**
   ```python
   config = net_connect.send_command('show running-config')
   with open('backup.cfg', 'w') as f:
       f.write(config)
   ```

5. **Use Timing for Interactive Commands**
   ```python
   output = net_connect.send_command_timing(
       'reload',
       delay_factor=2
   )
   ```

---

**Last Updated**: 2025-11-19
**Reference**: github.com/ktbyers/netmiko, pynet.twb-tech.com
