# Python Network Libraries Reference

## Netmiko - Multi-Vendor SSH Library

### Installation
```bash
pip install netmiko
```

### Basic Connection
```python
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
    'port': 22,
}

net_connect = ConnectHandler(**device)
print(net_connect.send_command('show ip interface brief'))
net_connect.disconnect()
```

### Sending Commands
```python
# Single command
output = net_connect.send_command('show running-config')

# List of commands
commands = ['show ip route', 'show ip bgp summary']
for cmd in commands:
    print(net_connect.send_command(cmd))

# Command with expect string
output = net_connect.send_command('reload', expect_string=r'Proceed?')

# Expecting full output
config = net_connect.send_command_timing('show running-config')
```

### Sending Configuration
```python
# Single config line
net_connect.send_config_set(['interface Ethernet0/0', 'ip address 10.0.0.1 255.255.255.0'])

# Configuration from file
with open('config.txt') as f:
    config_lines = f.readlines()
net_connect.send_config_set(config_lines)

# Interactive configuration
net_connect.send_config_set([
    'reload',
    '\n'  # Press Enter when prompted
], delay_factor=2)
```

### Device Types Supported
```
cisco_ios, cisco_xe, cisco_xr, juniper_junos, arista_eos,
hp_comware, dell_os10, netgate_pfense, checkpoint_gaia,
and 50+ more...
```

## NAPALM - Unified Network API

### Installation
```bash
pip install napalm
```

### Basic Usage
```python
from napalm import get_network_driver

driver = get_network_driver('ios')
device = driver('192.168.1.1', 'admin', 'password')

device.open()

# Get device info
facts = device.get_facts()
print(facts)

# Get interfaces
interfaces = device.get_interfaces()
for iface, data in interfaces.items():
    print(f"{iface}: {data['speed']} Mbps")

device.close()
```

### Multi-Device Operations
```python
from napalm import get_network_driver

devices = [
    {'host': '10.0.0.1', 'user': 'admin', 'pass': 'pass'},
    {'host': '10.0.0.2', 'user': 'admin', 'pass': 'pass'},
]

driver = get_network_driver('cisco_xr')

for device_params in devices:
    device = driver(device_params['host'], device_params['user'], device_params['pass'])
    device.open()
    print(device.get_facts())
    device.close()
```

### Configuration Management
```python
# Load configuration
device.load_candidate_config(config='interface Ethernet0/0\nip address 10.0.0.1 255.255.255.0')

# Compare configurations
diff = device.compare_config()
print(diff)

# Apply or discard
if 'changes' in diff:
    device.commit_config()
else:
    device.discard_config()
```

### Available Methods
```python
# Getters
get_facts()              # Device information
get_interfaces()         # Interface status
get_interfaces_ip()      # IP configuration
get_routing()           # BGP/OSPF routes
get_users()             # User accounts
get_bgp_neighbors_detail() # BGP session details
get_ntp_servers()       # NTP configuration
get_config()            # Running/startup configs
get_arp_table()         # ARP entries
get_mac_address_table() # MAC table
get_lldp_neighbors()    # LLDP information
```

## Nornir - Task Execution Framework

### Installation
```bash
pip install nornir
```

### Basic Setup
```python
from nornir import InitNornir

nr = InitNornir(config_file="config.yaml")

# Filter devices
routers = nr.filter(role="router")

# Run tasks
results = nr.run(task=my_task_function)

# Print results
print_result(results)
```

### Task Definition
```python
from nornir.core.task import Task, Result

def config_backup(task: Task) -> Result:
    """Backup device configuration"""
    r = task.run(
        name="Get running config",
        task=netmiko_commands,
        command_string="show running-config"
    )

    with open(f"backups/{task.host}.cfg", "w") as f:
        f.write(r[0].result)

    return Result(
        host=task.host,
        result=f"Backup completed for {task.host}"
    )
```

### NAPALM Integration
```python
from nornir.plugins.tasks.napalm import napalm_get
from nornir.plugins.functions.text import print_result

def get_device_facts(task):
    result = task.run(
        task=napalm_get,
        getters=["facts", "interfaces", "arp_table"]
    )
    return result

nr = InitNornir(config_file="config.yaml")
results = nr.run(task=get_device_facts)
print_result(results)
```

### Netmiko Integration
```python
from nornir.plugins.tasks.netmiko_tasks import netmiko_commands

def show_commands(task):
    results = task.run(
        task=netmiko_commands,
        command_string="show ip route"
    )
    return results
```

## PyATS - Cisco Testing Framework

### Installation
```bash
pip install pyats[full]
```

### Test Structure
```python
import unittest
from pyats import aetest
from pyats.log.utils import banner

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed):
        """Connect to devices"""
        testbed.connect()

class TestCase_1(aetest.TestCase):
    """Test BGP neighbors"""

    @aetest.setup
    def setup(self):
        """Setup for test"""
        pass

    @aetest.test
    def test_bgp_neighbors(self, testbed):
        """Verify BGP neighbors are up"""
        device = testbed.devices['router1']

        # Get BGP neighbors
        output = device.execute('show bgp ipv4 unicast summary')

        # Parse output
        parsed = device.parse('show bgp ipv4 unicast summary')

        # Assert neighbors are established
        assert len(parsed['bgp_instance']['default']['vrf']['default']['neighbor']) > 0

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        """Disconnect from devices"""
        testbed.disconnect()
```

### PyATS Parsing
```python
from pyats.conf import Config

# Uses device native parser (Genie)
parsed = device.parse('show ip interface brief')

# Structure varies by command, but generally:
for interface, data in parsed['interface'].items():
    print(f"{interface}: {data['status']}")
```

## Paramiko - SSH Protocol

### Installation
```bash
pip install paramiko
```

### Basic SSH Connection
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.1', username='admin', password='password')

stdin, stdout, stderr = ssh.exec_command('show version')
print(stdout.read().decode())

ssh.close()
```

### File Transfer
```python
sftp = ssh.open_sftp()
sftp.put('local_file.txt', 'remote_file.txt')
sftp.get('remote_file.txt', 'local_file.txt')
sftp.close()
```

## Requests - HTTP/REST API

### Installation
```bash
pip install requests
```

### Basic REST API Call
```python
import requests
from requests.auth import HTTPBasicAuth

# GET request
response = requests.get(
    'https://192.168.1.1/restconf/data/ietf-interfaces:interfaces',
    auth=HTTPBasicAuth('admin', 'password'),
    verify=False
)

if response.status_code == 200:
    interfaces = response.json()
    print(interfaces)

# POST request
payload = {
    "ietf-interfaces:interface": {
        "name": "Ethernet0/0",
        "enabled": True
    }
}

response = requests.post(
    'https://192.168.1.1/restconf/data/ietf-interfaces:interfaces',
    json=payload,
    auth=HTTPBasicAuth('admin', 'password'),
    verify=False
)
```

## Comparison Matrix

| Library | Best For | Sync/Async | Learning Curve |
|---------|----------|-----------|-----------------|
| Netmiko | Simple command execution | Sync | Easy |
| NAPALM | Unified device interface | Sync | Medium |
| Nornir | Task orchestration | Async | Medium |
| PyATS | Network testing | Sync | Hard |
| Paramiko | Low-level SSH | Sync | Medium |
| Requests | REST APIs | Sync | Easy |

## Error Handling

```python
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, AuthenticationException

try:
    device = {
        'device_type': 'cisco_ios',
        'host': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    net_connect = ConnectHandler(**device)
    output = net_connect.send_command('show ip route')
except AuthenticationException:
    print("Authentication failed")
except NetmikoTimeoutException:
    print("Connection timeout")
except Exception as e:
    print(f"Error: {e}")
finally:
    net_connect.disconnect()
```

---

**Last Updated**: 2025-11-19
**Reference**: pynetbox.com, napalm.readthedocs.io, nornir.readthedocs.io
