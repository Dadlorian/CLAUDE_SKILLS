# NETCONF/RESTCONF Reference Guide

## NETCONF (RFC 6241)

### Overview
NETCONF is an XML-based protocol for network device management, offering structured configuration and real-time capabilities.

### Key Concepts

#### Session Management
```xml
<!-- Client: Hello Message -->
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
    </capabilities>
</hello>

<!-- Server: Hello Response -->
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
        <capability>urn:ietf:params:yang:ietf-netconf-with-defaults</capability>
    </capabilities>
    <session-id>1</session-id>
</hello>
```

#### RPC Operations

##### Get (Retrieve Configuration/State)
```xml
<rpc message-id="1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <get>
        <filter type="subtree">
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>eth0</name>
                </interface>
            </interfaces>
        </filter>
    </get>
</rpc>

<rpc-reply message-id="1" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>eth0</name>
                <type>ethernetCsmacd</type>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </data>
</rpc-reply>
```

##### Get-Config (Retrieve Configuration Only)
```xml
<rpc message-id="2" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <get-config>
        <source>
            <running/>
        </source>
    </get-config>
</rpc>
```

##### Edit-Config (Modify Configuration)
```xml
<rpc message-id="3" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <edit-config>
        <target>
            <candidate/>
        </target>
        <config>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>eth0</name>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                        <address>
                            <ip>192.168.1.1</ip>
                            <netmask>255.255.255.0</netmask>
                        </address>
                    </ipv4>
                </interface>
            </interfaces>
        </config>
    </edit-config>
</rpc>
```

##### Copy-Config (Copy Configuration)
```xml
<rpc message-id="4" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <copy-config>
        <source>
            <candidate/>
        </source>
        <target>
            <running/>
        </target>
    </copy-config>
</rpc>
```

##### Lock/Unlock
```xml
<!-- Lock configuration -->
<rpc message-id="5" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <lock>
        <target>
            <candidate/>
        </target>
    </lock>
</rpc>

<!-- Unlock configuration -->
<rpc message-id="6" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <unlock>
        <target>
            <candidate/>
        </target>
    </unlock>
</rpc>
```

##### Kill-Session
```xml
<rpc message-id="7" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <kill-session>
        <session-id>2</session-id>
    </kill-session>
</rpc>
```

### Base Capabilities

```
urn:ietf:params:netconf:base:1.0         # NETCONF 1.0
urn:ietf:params:netconf:base:1.1         # NETCONF 1.1
urn:ietf:params:netconf:capability:writable-running:1.0
urn:ietf:params:netconf:capability:candidate:1.0
urn:ietf:params:netconf:capability:confirmed-commit:1.0
urn:ietf:params:netconf:capability:rollback-on-error:1.0
urn:ietf:params:netconf:capability:startup:1.0
urn:ietf:params:netconf:capability:xpath:1.0
```

### Data Models (YANG)

NETCONF uses YANG data models to define configuration structure.

```
/ietf-interfaces:interfaces/
  /interface/
    /name (string, key)
    /description (string)
    /enabled (boolean)
    /mtu (uint16)
    /ipv4/ (container for IP configuration)
    /ipv6/ (container for IPv6 configuration)
    /statistics/ (container for interface statistics)
```

## RESTCONF (RFC 8040)

### Overview
RESTCONF is the REST implementation of NETCONF, providing HTTP-based access to network devices.

### Key Concepts

#### HTTP Methods
- `GET` - Retrieve data (equivalent to NETCONF `get` and `get-config`)
- `PUT` - Replace data (equivalent to NETCONF `copy-config` with merge)
- `PATCH` - Merge data (equivalent to NETCONF `edit-config`)
- `DELETE` - Remove data
- `POST` - Create new data or invoke RPC operations

#### URL Structure
```
https://device:port/restconf/
  data/                      # Configuration and state data
    {module}:{container}/
      {leaf}/
  operations/                # RPC operations
    {module}:{rpc}/
  yang-library-version       # YANG library information
  schemas/                   # YANG modules
```

#### Examples

##### GET - Retrieve Configuration
```bash
curl -u admin:password \
  -H "Accept: application/yang-data+json" \
  https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces

# Response
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "Ethernet0/0",
        "type": "ethernetCsmacd",
        "enabled": true,
        "mtu": 1500
      }
    ]
  }
}
```

##### POST - Create New Interface
```bash
curl -u admin:password \
  -H "Content-Type: application/yang-data+json" \
  -X POST \
  https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces \
  -d '{
    "ietf-interfaces:interface": {
      "name": "Ethernet0/1",
      "type": "ethernetCsmacd",
      "enabled": true
    }
  }'
```

##### PUT - Replace Interface Configuration
```bash
curl -u admin:password \
  -H "Content-Type: application/yang-data+json" \
  -X PUT \
  https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces/interface=Ethernet0/0 \
  -d '{
    "ietf-interfaces:interface": {
      "name": "Ethernet0/0",
      "enabled": false,
      "mtu": 9000
    }
  }'
```

##### PATCH - Merge Configuration
```bash
curl -u admin:password \
  -H "Content-Type: application/yang-data+json" \
  -X PATCH \
  https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces/interface=Ethernet0/0 \
  -d '{
    "ietf-interfaces:interface": {
      "description": "WAN Link"
    }
  }'
```

##### DELETE - Remove Resource
```bash
curl -u admin:password \
  -X DELETE \
  https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces/interface=Ethernet0/1
```

##### Query Parameters
```bash
# Retrieve specific fields
curl https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces?fields=interface/name,interface/enabled

# Filter data
curl https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces?filter=interface%5Benabled=true%5D

# Depth control
curl https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces?depth=1

# Content type (config, state, all)
curl https://192.168.1.1:830/restconf/data/ietf-interfaces:interfaces?content=config
```

### Content Types
```
application/yang-data+json
application/yang-data+xml
application/yang-patch+json
application/yang-patch+xml
```

## Cisco YANG Models

### Common Cisco Models
```
Cisco-IOS-XE:
  /native/         # IOS-XE configuration
  /native/interface/
  /native/router/

Cisco-IOS-XR:
  /config/         # IOS-XR configuration
  /state/          # IOS-XR operational state
  /Cisco-IOS-XR-ifmgr-cfg:interface-configurations/

Cisco NX-OS:
  /System/         # System configuration
  /System/interfaces-config/
```

## Python NETCONF/RESTCONF Examples

### ncclient - NETCONF Client
```python
from ncclient import manager

# Connect to device
with manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password',
    hostkey_verify=False,
    device_params={'name': 'default'}
) as m:
    # Get running config
    config = m.get_config(source='running')
    print(config)

    # Edit configuration
    config_text = '''
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Ethernet0/0</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    '''

    reply = m.edit_config(target='candidate', config=config_text)
    print(reply)

    # Commit
    m.commit()
```

### Requests - RESTCONF Client
```python
import requests
import json

# RESTCONF base URL
base_url = "https://192.168.1.1/restconf"
auth = ('admin', 'password')
headers = {'Content-Type': 'application/yang-data+json', 'Accept': 'application/yang-data+json'}

# GET interfaces
response = requests.get(
    f"{base_url}/data/ietf-interfaces:interfaces",
    auth=auth,
    headers=headers,
    verify=False
)

interfaces = response.json()
print(json.dumps(interfaces, indent=2))

# POST new interface
interface_data = {
    "ietf-interfaces:interface": {
        "name": "Ethernet0/1",
        "enabled": True
    }
}

response = requests.post(
    f"{base_url}/data/ietf-interfaces:interfaces",
    auth=auth,
    headers=headers,
    json=interface_data,
    verify=False
)

print(f"Status: {response.status_code}")
```

## Common YANG Modules

| Module | Namespace | Use |
|--------|-----------|-----|
| ietf-interfaces | urn:ietf:params:xml:ns:yang:ietf-interfaces | Interface configuration |
| ietf-ip | urn:ietf:params:xml:ns:yang:ietf-ip | IP configuration |
| ietf-routing | urn:ietf:params:xml:ns:yang:ietf-routing | Routing protocols |
| ietf-yang-types | urn:ietf:params:xml:ns:yang:ietf-yang-types | Common types |
| ietf-inet-types | urn:ietf:params:xml:ns:yang:ietf-inet-types | Internet types |

---

**Last Updated**: 2025-11-19
**Reference**: RFC 6241, RFC 8040, ietf.org/rfc/
