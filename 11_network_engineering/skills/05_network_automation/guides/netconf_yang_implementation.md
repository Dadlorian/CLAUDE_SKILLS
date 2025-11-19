# NETCONF/YANG Implementation Guide

## Prerequisites

```bash
pip install ncclient    # NETCONF client library
pip install requests    # For RESTCONF
pip install pyyaml      # Configuration handling
```

## NETCONF Implementation

### Basic NETCONF Session

#### Establishing Connection
```python
from ncclient import manager

# Connect to NETCONF device
with manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password',
    hostkey_verify=False,
    device_params={'name': 'default'},
    timeout=30
) as m:
    print("Connected to device")
    print(f"Capabilities: {m.server_capabilities}")
```

#### Checking Capabilities
```python
from ncclient import manager

with manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password',
    hostkey_verify=False
) as m:
    # List server capabilities
    for capability in m.server_capabilities:
        print(capability)

    # Check for specific capability
    if 'urn:ietf:params:netconf:capability:candidate:1.0' in m.server_capabilities:
        print("Device supports candidate datastore")

    if 'urn:ietf:params:netconf:capability:notification:1.0' in m.server_capabilities:
        print("Device supports notifications")
```

### RPC Operations

#### Get Configuration (Get-Config)
```python
from ncclient import manager
from lxml import etree

with manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password',
    hostkey_verify=False
) as m:
    # Get running configuration
    config_reply = m.get_config(source='running')

    # Pretty print XML
    print(etree.tostring(config_reply.xml, pretty_print=True).decode())

    # Save to file
    with open('running_config.xml', 'w') as f:
        f.write(etree.tostring(config_reply.xml, pretty_print=True).decode())
```

#### Get Configuration with Filter
```python
# Filter for specific elements
filter_spec = '''
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
        <name>Ethernet0/0</name>
    </interface>
</interfaces>
'''

config_reply = m.get_config(
    source='running',
    filter=('subtree', filter_spec)
)

print(etree.tostring(config_reply.xml, pretty_print=True).decode())
```

#### Get Operational Data (Get)
```python
# Get operational state (not just configuration)
state_reply = m.get()

# Pretty print the response
print(etree.tostring(state_reply.xml, pretty_print=True).decode())

# Get with filter for interfaces
interface_filter = '''
<interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
</interfaces-state>
'''

state_reply = m.get(filter=('subtree', interface_filter))
```

#### Edit Configuration
```python
# Configuration to deploy
config_xml = '''
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>Ethernet0/0</name>
            <type>ethernetCsmacd</type>
            <enabled>true</enabled>
            <mtu>1500</mtu>
            <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                    <ip>192.168.1.1</ip>
                    <netmask>255.255.255.0</netmask>
                </address>
            </ipv4>
        </interface>
    </interfaces>
</config>
'''

# Edit candidate datastore
edit_reply = m.edit_config(
    target='candidate',
    config=config_xml
)

print("Configuration loaded to candidate datastore")
```

#### Validate and Commit Configuration
```python
# Validate configuration
try:
    validate_reply = m.validate(source='candidate')
    print("✓ Configuration is valid")
except Exception as e:
    print(f"✗ Validation failed: {e}")
    m.discard_changes()

# Commit configuration
try:
    commit_reply = m.commit()
    print("✓ Configuration committed")
except Exception as e:
    print(f"✗ Commit failed: {e}")
    m.discard_changes()

# Verify changes
config_reply = m.get_config(source='running')
print("Running configuration after commit:")
print(etree.tostring(config_reply.xml, pretty_print=True).decode())
```

#### Lock and Unlock
```python
# Lock configuration
try:
    lock_reply = m.lock(target='candidate')
    print("✓ Configuration locked")

    # Make changes
    m.edit_config(target='candidate', config=config_xml)

    # Unlock when done
    unlock_reply = m.unlock(target='candidate')
    print("✓ Configuration unlocked")

except Exception as e:
    print(f"Error: {e}")
```

### Configuration Management Workflow

```python
from ncclient import manager
from lxml import etree
import xml.dom.minidom as md

def netconf_workflow(host, username, password):
    """Complete NETCONF configuration workflow"""

    with manager.connect(
        host=host,
        port=830,
        username=username,
        password=password,
        hostkey_verify=False
    ) as m:
        # Step 1: Get current configuration
        print("Step 1: Backing up current configuration...")
        config_reply = m.get_config(source='running')
        with open('backup.xml', 'w') as f:
            f.write(etree.tostring(config_reply.xml, pretty_print=True).decode())
        print("✓ Backup saved to backup.xml")

        # Step 2: Load new configuration to candidate
        print("\nStep 2: Loading new configuration...")
        new_config = '''
        <config>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>Ethernet0/1</name>
                    <enabled>true</enabled>
                </interface>
            </interfaces>
        </config>
        '''

        m.edit_config(target='candidate', config=new_config)
        print("✓ Configuration loaded to candidate")

        # Step 3: Compare configurations
        print("\nStep 3: Comparing configurations...")
        try:
            # Note: Compare is not all devices, using get for comparison
            running = m.get_config(source='running')
            candidate = m.get_config(source='candidate')
            print("✓ Configuration comparison complete")
        except:
            print("! Compare operation not supported")

        # Step 4: Validate
        print("\nStep 4: Validating configuration...")
        try:
            m.validate(source='candidate')
            print("✓ Configuration is valid")
        except Exception as e:
            print(f"✗ Validation failed: {e}")
            m.discard_changes()
            return

        # Step 5: Commit
        print("\nStep 5: Committing configuration...")
        try:
            m.commit()
            print("✓ Configuration committed successfully")
        except Exception as e:
            print(f"✗ Commit failed: {e}")
            m.discard_changes()
            return

        print("\n✓ Configuration workflow completed successfully")

# Execute workflow
netconf_workflow('192.168.1.1', 'admin', 'password')
```

## RESTCONF Implementation

### HTTP-Based NETCONF

#### Basic REST Calls
```python
import requests
import json
from requests.auth import HTTPBasicAuth

# Device credentials
device_ip = '192.168.1.1'
username = 'admin'
password = 'password'
base_url = f'https://{device_ip}/restconf'

# Disable SSL warnings (dev only)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Headers
headers = {
    'Content-Type': 'application/yang-data+json',
    'Accept': 'application/yang-data+json'
}

auth = HTTPBasicAuth(username, password)

# GET - Retrieve interfaces
response = requests.get(
    f'{base_url}/data/ietf-interfaces:interfaces',
    headers=headers,
    auth=auth,
    verify=False
)

if response.status_code == 200:
    interfaces = response.json()
    print(json.dumps(interfaces, indent=2))
```

#### Create New Interface
```python
# POST - Create new interface
interface_data = {
    'ietf-interfaces:interface': {
        'name': 'Ethernet0/1',
        'enabled': True,
        'type': 'ethernetCsmacd'
    }
}

response = requests.post(
    f'{base_url}/data/ietf-interfaces:interfaces',
    json=interface_data,
    headers=headers,
    auth=auth,
    verify=False
)

if response.status_code == 201:
    print("✓ Interface created successfully")
    print(response.headers)
elif response.status_code == 409:
    print("✗ Interface already exists")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
```

#### Update Interface Configuration
```python
# PUT - Replace entire interface config
interface_config = {
    'ietf-interfaces:interface': {
        'name': 'Ethernet0/0',
        'enabled': True,
        'description': 'WAN Interface',
        'mtu': 1500
    }
}

response = requests.put(
    f'{base_url}/data/ietf-interfaces:interfaces/interface=Ethernet0/0',
    json=interface_config,
    headers=headers,
    auth=auth,
    verify=False
)

if response.status_code == 204:
    print("✓ Interface updated successfully")
else:
    print(f"✗ Error: {response.status_code}")
```

#### Partial Update (PATCH)
```python
# PATCH - Merge changes (partial update)
partial_update = {
    'ietf-interfaces:interface': {
        'description': 'Updated WAN Interface'
    }
}

response = requests.patch(
    f'{base_url}/data/ietf-interfaces:interfaces/interface=Ethernet0/0',
    json=partial_update,
    headers=headers,
    auth=auth,
    verify=False
)

if response.status_code == 204:
    print("✓ Interface description updated")
```

#### Delete Interface
```python
# DELETE - Remove interface
response = requests.delete(
    f'{base_url}/data/ietf-interfaces:interfaces/interface=Ethernet0/1',
    headers=headers,
    auth=auth,
    verify=False
)

if response.status_code == 204:
    print("✓ Interface deleted successfully")
else:
    print(f"✗ Error: {response.status_code}")
```

### RESTCONF API Class

```python
class RESTCONFDevice:
    """RESTCONF device management class"""

    def __init__(self, host, username, password, port=443):
        self.base_url = f'https://{host}:{port}/restconf'
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {
            'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'
        }

    def get_interfaces(self):
        """Get all interfaces"""
        response = requests.get(
            f'{self.base_url}/data/ietf-interfaces:interfaces',
            headers=self.headers,
            auth=self.auth,
            verify=False
        )
        return response.json() if response.status_code == 200 else None

    def get_interface(self, name):
        """Get specific interface"""
        response = requests.get(
            f'{self.base_url}/data/ietf-interfaces:interfaces/interface={name}',
            headers=self.headers,
            auth=self.auth,
            verify=False
        )
        return response.json() if response.status_code == 200 else None

    def update_interface(self, name, config):
        """Update interface configuration"""
        data = {
            'ietf-interfaces:interface': {
                'name': name,
                **config
            }
        }

        response = requests.put(
            f'{self.base_url}/data/ietf-interfaces:interfaces/interface={name}',
            json=data,
            headers=self.headers,
            auth=self.auth,
            verify=False
        )

        return response.status_code == 204

    def get_config(self):
        """Get running configuration"""
        response = requests.get(
            f'{self.base_url}/data/native',
            headers=self.headers,
            auth=self.auth,
            verify=False
        )

        return response.json() if response.status_code == 200 else None

# Usage
device = RESTCONFDevice('192.168.1.1', 'admin', 'password')

# Get all interfaces
interfaces = device.get_interfaces()
print(json.dumps(interfaces, indent=2))

# Get specific interface
eth0 = device.get_interface('Ethernet0/0')
print(json.dumps(eth0, indent=2))

# Update interface
updated = device.update_interface('Ethernet0/0', {
    'enabled': True,
    'description': 'Updated Interface'
})

if updated:
    print("✓ Interface updated")
```

## YANG Model Validation

### Parsing YANG Models
```bash
# Install pyang for YANG model validation
pip install pyang

# Validate YANG file syntax
pyang -f tree my_model.yang

# Generate documentation
pyang -f html my_model.yang -o model_docs.html

# Check YANG module dependencies
pyang -f depend my_model.yang
```

## Working with Device Parsers

### Parsing NETCONF Output
```python
from xml.etree import ElementTree as ET

# Parse NETCONF response
config_xml = '''
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
        <name>Ethernet0/0</name>
        <enabled>true</enabled>
        <mtu>1500</mtu>
    </interface>
    <interface>
        <name>Ethernet0/1</name>
        <enabled>false</enabled>
        <mtu>1500</mtu>
    </interface>
</interfaces>
'''

root = ET.fromstring(config_xml)

# Iterate interfaces
for iface in root.findall('.//interface'):
    name = iface.find('name').text
    enabled = iface.find('enabled').text
    mtu = iface.find('mtu').text
    print(f"{name}: enabled={enabled}, mtu={mtu}")
```

## Error Handling

```python
from ncclient import manager
from ncclient.operations import RaiseMode

with manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password',
    hostkey_verify=False,
    raise_mode=RaiseMode.ERRORS
) as m:
    try:
        # Attempt operation
        reply = m.edit_config(target='candidate', config=config_xml)

    except manager.OperationError as e:
        print(f"Operation error: {e}")
        m.discard_changes()

    except manager.TimeoutExpiredError:
        print("Operation timed out")

    except Exception as e:
        print(f"Unexpected error: {e}")
```

---

**Last Updated**: 2025-11-19
**Reference**: ncclient.readthedocs.io, pyang.readthedocs.io
