# NETCONF/RESTCONF Integration Standards

## Executive Summary

This document provides comprehensive standards and best practices for implementing NETCONF and RESTCONF APIs in network infrastructure. These protocols enable programmatic configuration and monitoring of network devices, supporting infrastructure as code, network automation, and modern DevOps practices.

**Version**: 1.0
**Last Updated**: 2025-11-19
**Reference Standards**: RFC 6241 (NETCONF), RFC 8040 (RESTCONF), OpenConfig, YANG Data Models

---

## 1. NETCONF Protocol Fundamentals

### 1.1 NETCONF Overview

NETCONF (Network Configuration Protocol) is an XML-based protocol that enables retrieval, deployment, and manipulation of network device configurations.

**Key Characteristics**:
- Transport-agnostic (SSH, TLS, SOAP)
- Separation of control and data operations
- Atomic transactions with rollback capability
- Secure, robust configuration management
- RFC 6241 standardized

**NETCONF Operations**:

| Operation | Purpose | Example |
|-----------|---------|---------|
| `<get>` | Retrieve running configuration and state | Get current interface status |
| `<get-config>` | Retrieve stored configuration | Get startup configuration |
| `<edit-config>` | Modify configuration | Add BGP neighbor |
| `<copy-config>` | Copy configuration between datastores | Backup running to startup |
| `<delete-config>` | Delete entire configuration | Clear test configuration |
| `<lock>` | Lock configuration datastore | Prevent concurrent changes |
| `<unlock>` | Unlock configuration datastore | Release after change |
| `<close-session>` | Gracefully terminate session | Clean shutdown |
| `<kill-session>` | Forcefully terminate session | Emergency termination |

### 1.2 NETCONF Datastores

**Standard Datastores**:

```
Running (default operational state):
├── Active configuration
├── Current device state
└── Reflects actual device behavior

Candidate (staging area):
├── Temporary configuration changes
├── Not yet applied to device
└── Requires <commit> to activate

Startup (device boot configuration):
├── Configuration loaded on device reboot
├── May differ from running
└── Synchronized via <copy-config>
```

**Datastore Lifecycle**:
```
Startup
   |
   v
[Device Boot]
   |
   v
Running (operational)
   ^     ^
   |     |
   +-----+
    Edit via
   Candidate
```

### 1.3 NETCONF Session Establishment

**SSH Transport (Recommended)**:
```xml
<!-- NETCONF over SSH Connection -->
SSH: client:port → device:830 (default NETCONF SSH port)

Client sends:
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
    <capability>urn:ietf:params:netconf:capability:writable-running:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
  </capabilities>
</hello>

Device responds:
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
    <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:commit:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:validate:1.0</capability>
    <capability>urn:ietf:params:yang:ietf-interfaces?module=ietf-interfaces&amp;revision=2018-02-20</capability>
  </capabilities>
  <session-id>8</session-id>
</hello>
```

### 1.4 NETCONF Message Format

**RPC Structure**:
```xml
<!-- Example: Configure BGP neighbor -->
<?xml version="1.0" encoding="UTF-8"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
     message-id="101">
  <edit-config>
    <target>
      <candidate/>
    </target>
    <default-operation>merge</default-operation>
    <test-option>test-and-set</test-option>
    <error-option>rollback-on-error</error-option>
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>GigabitEthernet0/0/1</name>
          <enabled>true</enabled>
          <mtu>1500</mtu>
        </interface>
      </interfaces>
    </config>
  </edit-config>
</rpc>

<!-- Device Response -->
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
           message-id="101">
  <ok/>
</rpc-reply>
```

---

## 2. YANG Data Models

### 2.1 YANG Overview

YANG (RFC 7950) is a hierarchical data model language that defines network device data and operations.

**Key Advantages**:
- Language-independent data model
- Machine-parseable (enables code generation)
- Validates configuration and state
- Supports constraints and automation
- Open standards (IETF, OpenConfig)

### 2.2 Standard YANG Module Hierarchy

**IETF Base Modules** (RFC-defined):
```
ietf-interfaces (RFC 7223)
├── ietf-ip (RFC 7277) - IPv4/IPv6 configuration
├── ietf-yang-types (RFC 6991) - Common type definitions
└── ietf-inet-types (RFC 6991) - Internet type definitions

ietf-routing (RFC 8349)
├── ietf-routing-policy
├── ietf-bgp
└── ietf-ospf

ietf-netconf (RFC 6241)
├── NETCONF protocol operations
└── Base data model
```

**OpenConfig Modules** (Vendor-neutral):
```
openconfig-interfaces
├── Interface configuration and state
└── Vendor-agnostic definitions

openconfig-routing-policy
├── Route filtering and policy

openconfig-bgp
├── BGP configuration and state
├── Neighbor configuration
├── Address family policies
└── Route reflection

openconfig-network-instance
├── VRF/VPN configuration
└── Protocol instance management
```

### 2.3 YANG Model Structure Example

```yang
module ietf-bgp {
  yang-version 1.1;
  namespace "urn:ietf:params:xml:ns:yang:ietf-bgp";
  prefix bgp;

  import ietf-routing {
    prefix rt;
  }

  container bgp {
    presence "Enables BGP operation";
    description "BGP configuration and state data";

    container global {
      leaf router-id {
        type string;
        description "BGP Router ID";
      }
      leaf local-asn {
        type uint32;
        description "Local AS number";
      }
      leaf as-path-ignore {
        type empty;
      }
    }

    container neighbors {
      list neighbor {
        key "neighbor-address";
        description "BGP neighbor configuration";

        leaf neighbor-address {
          type string;
          description "Neighbor IP address";
        }
        leaf remote-asn {
          type uint32;
          description "Neighbor AS number";
        }
        leaf enabled {
          type boolean;
          default "true";
        }
        leaf password {
          type string;
          description "BGP authentication password";
        }
        container timers {
          leaf keepalive-interval {
            type uint16;
            default 60;
            description "Keepalive in seconds";
          }
          leaf holddown-interval {
            type uint16;
            default 180;
            description "Holddown in seconds";
          }
        }
      }
    }
  }

  rpc clear-bgp-neighbors {
    description "Clear BGP neighbor sessions";
    input {
      leaf neighbor-address {
        type string;
        description "Specific neighbor to clear";
      }
    }
  }
}
```

### 2.4 YANG Implementation for Network Devices

**Cisco IOS XR YANG Models**:
```
Cisco-IOS-XR-bgp-cfg       BGP configuration
Cisco-IOS-XR-bgp-oper      BGP operational state
Cisco-IOS-XR-ifmgr-cfg     Interface management
Cisco-IOS-XR-ip-rip-cfg    RIP configuration
Cisco-IOS-XR-ospf-cfg      OSPF configuration
```

**Juniper Junos YANG Models**:
```
junos:configuration         Configuration data
junos:operational           Operational state
juniper-bgp@2019-01-01      BGP module
juniper-ospf@2019-01-01     OSPF module
```

---

## 3. RESTCONF Protocol Standards

### 3.1 RESTCONF Overview

RESTCONF (RFC 8040) is a REST API for accessing YANG data models. It provides familiar HTTP/REST semantics for network device management.

**Key Characteristics**:
- Uses standard HTTP methods (GET, POST, PATCH, DELETE)
- Maps YANG hierarchy to REST paths
- Returns JSON or XML representations
- Supports HTTPS for security
- Better for synchronous operations and monitoring

**HTTP Methods**:

| Method | YANG Operation | Purpose | Idempotent |
|--------|----------------|---------|-----------|
| GET | <get>, <get-config> | Retrieve data | Yes |
| POST | Create new resource | Create config or RPC | No |
| PUT | Replace entire resource | Complete replacement | Yes |
| PATCH | Partial modification | Merge/modify config | Yes |
| DELETE | Remove resource | Delete config | Yes |
| OPTIONS | Discover capabilities | Check available operations | Yes |

### 3.2 RESTCONF API Path Structure

**Base URL**:
```
https://device:8443/restconf/
```

**Standard Paths**:
```
/restconf/data                      Configuration and state data
/restconf/data/ietf-interfaces:interfaces
/restconf/data/openconfig-bgp:bgp
/restconf/operations                RPC operations
/restconf/operations/ietf-netconf-operational:clear-bgp
/restconf/yang-library              YANG module information
/restconf/yang-library/modules-state
```

**Query Parameters**:
```
?depth=2                            Limit hierarchy depth
?fields=leaf1;leaf2                 Select specific fields
?content=config                     Return only config (not state)
?content=nonconfig                  Return only state (not config)
?with-defaults=report-all           Include default values
```

### 3.3 RESTCONF Request/Response Examples

**Example 1: Retrieve interface configuration**

```http
GET /restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F0%2F1?content=config HTTP/1.1
Host: 10.1.4.1:8443
Authorization: Basic dXNlcjpwYXNz
Accept: application/yang-data+json

HTTP/1.1 200 OK
Content-Type: application/yang-data+json

{
  "ietf-interfaces:interface": {
    "name": "GigabitEthernet0/0/1",
    "type": "ethernetCsmacd",
    "enabled": true,
    "mtu": 1500,
    "ietf-ip:ipv4": {
      "address": [
        {
          "ip": "10.1.2.1",
          "netmask": "255.255.255.0"
        }
      ]
    }
  }
}
```

**Example 2: Configure BGP neighbor via PATCH**

```http
PATCH /restconf/data/openconfig-bgp:bgp/global/config HTTP/1.1
Host: 10.1.4.1:8443
Authorization: Basic dXNlcjpwYXNz
Content-Type: application/yang-data+json

{
  "openconfig-bgp:config": {
    "as": 65001,
    "router-id": "10.0.1.1"
  }
}

HTTP/1.1 204 No Content
```

**Example 3: Add BGP neighbor via POST**

```http
POST /restconf/data/openconfig-bgp:bgp/neighbors HTTP/1.1
Host: 10.1.4.1:8443
Authorization: Basic dXNlcjpwYXNz
Content-Type: application/yang-data+json

{
  "openconfig-bgp:neighbor": {
    "neighbor-address": "10.0.1.2",
    "config": {
      "neighbor-address": "10.0.1.2",
      "peer-asn": 65001,
      "local-asn": 65001,
      "auth-password": "bgp-secret123"
    }
  }
}

HTTP/1.1 201 Created
Location: /restconf/data/openconfig-bgp:bgp/neighbors/neighbor=10.0.1.2
```

**Example 4: Execute RPC operation**

```http
POST /restconf/operations/openconfig-bgp:clear-bgp-neighbors HTTP/1.1
Host: 10.1.4.1:8443
Authorization: Basic dXNlcjpwYXNz
Content-Type: application/yang-data+json

{
  "openconfig-bgp:input": {
    "neighbor-address": "10.0.1.2"
  }
}

HTTP/1.1 200 OK
Content-Type: application/yang-data+json

{
  "openconfig-bgp:output": {
    "status": "success",
    "neighbors-cleared": 1
  }
}
```

### 3.4 Status Codes and Error Handling

**Standard HTTP Status Codes**:

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | GET/PATCH/DELETE successful |
| 201 | Created | POST successful, resource created |
| 204 | No Content | Successful operation with no response body |
| 400 | Bad Request | Invalid syntax, malformed YANG |
| 401 | Unauthorized | Authentication failed |
| 403 | Forbidden | Permission denied (RBAC) |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Operation conflicts with device state |
| 422 | Unprocessable Entity | Semantic error (constraint violation) |
| 500 | Internal Server Error | Device processing error |
| 503 | Service Unavailable | Device temporarily unavailable |

**Error Response Example**:
```json
{
  "ietf-restconf:errors": {
    "error": [
      {
        "error-type": "application",
        "error-tag": "operation-failed",
        "error-app-tag": "invalid-neighbor-address",
        "error-message": "BGP neighbor 10.0.1.2 already exists",
        "error-path": "/openconfig-bgp:bgp/neighbors/neighbor=10.0.1.2"
      }
    ]
  }
}
```

---

## 4. OpenConfig Standards

### 4.1 OpenConfig Initiative

OpenConfig is a collaborative effort to develop vendor-neutral models for network device configuration and telemetry.

**Key OpenConfig Modules**:

```
openconfig-interfaces          Interface management
openconfig-routing-policy      Route policies and filters
openconfig-bgp                 BGP configuration and state
openconfig-ospf                OSPF configuration and state
openconfig-isis                IS-IS configuration
openconfig-bgp-policy          BGP policy models
openconfig-bgp-multicast       BGP multicast extensions
openconfig-network-instance    VRF and VPN management
openconfig-mpls                MPLS configuration
openconfig-segment-routing     Segment routing models
openconfig-firewall            ACL and firewall rules
openconfig-qos                 QoS configuration
openconfig-system              System configuration
openconfig-lldp                LLDP protocol
openconfig-platform            Hardware platform information
```

### 4.2 OpenConfig BGP Model Example

```json
{
  "openconfig-bgp:bgp": {
    "global": {
      "config": {
        "as": 65001,
        "router-id": "10.0.1.1"
      },
      "state": {
        "as": 65001,
        "router-id": "10.0.1.1",
        "total-paths": 12,
        "total-prefixes": 245
      }
    },
    "neighbors": {
      "neighbor": [
        {
          "neighbor-address": "10.0.1.2",
          "config": {
            "neighbor-address": "10.0.1.2",
            "peer-asn": 65001,
            "local-asn": 65001,
            "auth-password": "secret123",
            "description": "DFW-Core-02",
            "send-community": "EXTENDED"
          },
          "state": {
            "neighbor-address": "10.0.1.2",
            "session-state": "ESTABLISHED",
            "last-established": "2025-11-19T10:30:00Z",
            "messages": {
              "sent": 45320,
              "received": 45310
            },
            "queues": {
              "input": 0,
              "output": 0
            }
          },
          "timers": {
            "config": {
              "keepalive-interval": 60,
              "hold-time": 180,
              "connect-retry": 30
            },
            "state": {
              "keepalive-interval": 60,
              "hold-time": 180,
              "uptime": 864000
            }
          },
          "afi-safis": {
            "afi-safi": [
              {
                "afi-safi-name": "IPV4_UNICAST",
                "config": {
                  "afi-safi-name": "IPV4_UNICAST",
                  "enabled": true,
                  "send-community": "EXTENDED"
                },
                "state": {
                  "afi-safi-name": "IPV4_UNICAST",
                  "enabled": true,
                  "prefixes": {
                    "received": 245,
                    "sent": 350,
                    "installed": 240
                  }
                }
              }
            ]
          }
        }
      ]
    }
  }
}
```

---

## 5. Security and Authentication

### 5.1 NETCONF Security

**SSH Key-Based Authentication** (Recommended):
```
1. Generate SSH keypair on management host
2. Configure SSH public key on device
3. Authenticate via SSH without password
4. Encrypt all traffic over SSH tunnel

ssh -i ~/.ssh/netconf_key -p 830 \
  -s netconf admin@10.1.4.1
```

**Username/Password Authentication**:
```
Less secure than key-based authentication.
Use with HTTPS/TLS only.
Enable failed login delays on device.
```

### 5.2 RESTCONF Security

**HTTPS/TLS Requirements**:
- Mandatory for production deployments
- Minimum TLS 1.2 (prefer 1.3)
- Valid certificates (not self-signed in production)
- Strong cipher suites (AES-256, ECDHE)

**HTTP Basic Authentication**:
```
Authorization: Basic base64(username:password)

Example:
Authorization: Basic dXNlcjpwYXNz  (user:pass)
```

**OAuth 2.0 / SAML Integration**:
```
POST /restconf/auth/token HTTP/1.1
Content-Type: application/json

{
  "username": "netadmin",
  "password": "secure-password",
  "grant_type": "password"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}

Subsequent request:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5.3 RBAC (Role-Based Access Control)

**Configuration Example (Cisco IOS XR)**:
```
aaa authorization commands default local

username admin
 group root-lr
 group netconf-operators
 secret 9 $7$Ehjk4VrV...

usergroup netconf-operators
 taskgroup read-write
  task execute netconf-config
  task execute netconf-diagnostics
  task execute netconf-get-config

taskgroup read-write
 permission read
 permission write
 permission execute
```

**REST API Permissions Example**:
```json
{
  "user": "network_admin",
  "roles": [
    "netconf-admin",
    "restconf-operator"
  ],
  "permissions": {
    "/restconf/data/openconfig-bgp*": ["GET", "POST", "PATCH"],
    "/restconf/data/ietf-interfaces*": ["GET", "PATCH"],
    "/restconf/operations/*": ["POST"]
  }
}
```

---

## 6. Implementation Best Practices

### 6.1 NETCONF Best Practices

**Operational Guidelines**:

1. **Session Management**:
   - Lock configuration before editing: `<lock/>`
   - Use candidate datastore for complex changes
   - Always unlock after changes: `<unlock/>`
   - Set reasonable session timeouts (30 minutes)

2. **Configuration Safety**:
   - Use `<test-option>test-and-set</test-option>` to validate before commit
   - Enable `<error-option>rollback-on-error</error-option>` for atomicity
   - Test all changes in lab before production
   - Maintain configuration backups before changes

3. **Error Handling**:
   ```xml
   <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
     <edit-config>
       <target><candidate/></target>
       <error-option>rollback-on-error</error-option>
       <config>
         <!-- configuration -->
       </config>
     </edit-config>
   </rpc>
   ```

4. **Commit Strategy**:
   - Always validate before commit
   - Use confirmed commit with timeout for safety
   - Log all commits with change ID
   - Archive configuration after commit

### 6.2 RESTCONF Best Practices

**API Design Guidelines**:

1. **Request/Response Optimization**:
   - Use content=config to reduce response size
   - Specify fields parameter to retrieve only needed data
   - Implement pagination for large datasets
   - Cache responses when appropriate

2. **Error Handling**:
   ```python
   import requests

   try:
       response = requests.get(
           "https://10.1.4.1:8443/restconf/data/ietf-interfaces:interfaces",
           auth=("admin", "password"),
           verify="/path/to/ca.pem",
           timeout=10
       )
       response.raise_for_status()
       interfaces = response.json()
   except requests.exceptions.Timeout:
       print("Request timeout - device not responding")
   except requests.exceptions.ConnectionError:
       print("Connection failed - device unreachable")
   except requests.exceptions.HTTPError as e:
       print(f"HTTP error: {e.response.status_code}")
   ```

3. **Idempotency**:
   - Use PUT for complete replacement (idempotent)
   - Use PATCH for partial updates
   - Design operations to be repeatable without side effects
   - Document non-idempotent operations

### 6.3 YANG Model Validation

**Validation Checklist**:
- [ ] Model conforms to RFC 7950 (YANG 1.1)
- [ ] All leaf types have proper constraints
- [ ] Mandatory leaves are documented
- [ ] Default values are appropriate
- [ ] Namespace is unique and follows conventions
- [ ] Revision history is complete
- [ ] Descriptions are clear and comprehensive
- [ ] Example configurations provided
- [ ] Backward compatibility considered
- [ ] Tested with at least two vendors

---

## 7. Network Automation Integration

### 7.1 Ansible Integration with NETCONF/RESTCONF

**Ansible Network Modules**:
```yaml
---
- hosts: network_devices
  gather_facts: no
  vars:
    ansible_connection: netconf  # or restconf
    ansible_port: 830           # NETCONF port
    ansible_user: netadmin
    ansible_password: "{{ vault_password }}"

  tasks:
    # NETCONF RPC execution
    - name: Get BGP neighbors
      netconf_rpc:
        rpc: get-config
        content: running
        filter:
          type: xpath
          select: /bgp/neighbors

    # YANG model configuration
    - name: Configure BGP
      yang_config:
        model: openconfig-bgp
        data:
          global:
            config:
              as: 65001
              router_id: 10.0.1.1
          neighbors:
            - neighbor_address: 10.0.1.2
              config:
                peer_asn: 65001
                local_asn: 65001

    # RESTCONF GET
    - name: Retrieve interfaces
      uri:
        url: "https://{{ inventory_hostname }}:8443/restconf/data/openconfig-interfaces:interfaces"
        method: GET
        user: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        headers:
          Accept: application/yang-data+json
      register: interfaces_data

    # RESTCONF PATCH
    - name: Configure interface MTU
      uri:
        url: "https://{{ inventory_hostname }}:8443/restconf/data/openconfig-interfaces:interfaces/interface=eth0"
        method: PATCH
        user: "{{ ansible_user }}"
        password: "{{ ansible_password }}"
        body_format: json
        body:
          openconfig-interfaces:config:
            mtu: 9216
```

### 7.2 Python Integration Example

```python
#!/usr/bin/env python3
"""
Network device configuration via NETCONF and RESTCONF
"""

import requests
from ncclient import manager
import xml.etree.ElementTree as ET
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkDevice:
    def __init__(self, host, username, password, protocol='netconf'):
        self.host = host
        self.username = username
        self.password = password
        self.protocol = protocol
        self.session = None

    def connect_netconf(self):
        """Establish NETCONF SSH connection"""
        try:
            self.session = manager.connect(
                host=self.host,
                port=830,
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                device_params={'name': 'cisco'}
            )
            logger.info(f"Connected to {self.host} via NETCONF")
        except Exception as e:
            logger.error(f"NETCONF connection failed: {e}")
            raise

    def connect_restconf(self):
        """Establish RESTCONF HTTPS session"""
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = False  # For self-signed certs in lab
        self.base_url = f"https://{self.host}:8443/restconf"
        logger.info(f"Connected to {self.host} via RESTCONF")

    def get_interfaces_netconf(self):
        """Retrieve interfaces via NETCONF"""
        filter_spec = """
        <filter type="subtree">
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name/>
                    <enabled/>
                    <mtu/>
                </interface>
            </interfaces>
        </filter>
        """

        try:
            reply = self.session.get(filter=filter_spec)
            logger.info("Retrieved interfaces via NETCONF")
            return reply.data_xml
        except Exception as e:
            logger.error(f"Failed to retrieve interfaces: {e}")
            raise

    def get_interfaces_restconf(self):
        """Retrieve interfaces via RESTCONF"""
        url = f"{self.base_url}/data/openconfig-interfaces:interfaces"
        params = {
            'content': 'config'
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("Retrieved interfaces via RESTCONF")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"RESTCONF request failed: {e}")
            raise

    def configure_bgp_netconf(self, asn, router_id):
        """Configure BGP via NETCONF"""
        config_template = f"""
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <bgp xmlns="urn:ietf:params:xml:ns:yang:ietf-bgp">
                <global>
                    <config>
                        <local-asn>{asn}</local-asn>
                        <router-id>{router_id}</router-id>
                    </config>
                </global>
            </bgp>
        </config>
        """

        try:
            self.session.lock(target='candidate')
            reply = self.session.edit_config(
                target='candidate',
                config=config_template
            )

            # Validate configuration
            self.session.validate(source='candidate')

            # Commit changes
            self.session.commit()
            self.session.unlock(target='candidate')

            logger.info(f"BGP configured: ASN={asn}, Router-ID={router_id}")
        except Exception as e:
            self.session.unlock(target='candidate')
            logger.error(f"BGP configuration failed: {e}")
            raise

    def configure_bgp_restconf(self, asn, router_id):
        """Configure BGP via RESTCONF"""
        url = f"{self.base_url}/data/openconfig-bgp:bgp/global/config"

        payload = {
            "openconfig-bgp:config": {
                "as": asn,
                "router-id": router_id
            }
        }

        try:
            response = self.session.patch(
                url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"BGP configured: ASN={asn}, Router-ID={router_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"BGP configuration failed: {e}")
            raise

    def backup_configuration(self, filename=None):
        """Backup device configuration"""
        if filename is None:
            filename = f"{self.host}-config-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xml"

        try:
            reply = self.session.get_config(source='running')
            with open(filename, 'w') as f:
                f.write(ET.tostring(reply.data, encoding='unicode'))
            logger.info(f"Configuration backed up to {filename}")
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    def close(self):
        """Close device connection"""
        if self.session:
            if self.protocol == 'netconf':
                self.session.close_session()
            else:
                self.session.close()
            logger.info("Connection closed")

# Usage example
if __name__ == "__main__":
    # NETCONF example
    device = NetworkDevice("10.1.4.1", "netadmin", "password", protocol='netconf')
    device.connect_netconf()
    device.configure_bgp_netconf(asn=65001, router_id='10.0.1.1')
    device.backup_configuration()
    device.close()

    # RESTCONF example
    device_rest = NetworkDevice("10.1.4.1", "netadmin", "password", protocol='restconf')
    device_rest.connect_restconf()
    interfaces = device_rest.get_interfaces_restconf()
    print(interfaces)
    device_rest.close()
```

---

## 8. Troubleshooting and Diagnostics

### 8.1 Common NETCONF Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| SSH connection refused | NETCONF not enabled | Enable with `netconf-yang agent ssh` |
| Candidate locked | Previous session didn't unlock | Kill session or wait for timeout |
| Validation failure | Constraint violation | Review constraint rules in YANG model |
| RPC timeout | Device busy or crash | Check device CPU/memory, restart if needed |
| Encoding error | XML malformed | Validate XML structure before sending |

### 8.2 Common RESTCONF Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| 401 Unauthorized | Invalid credentials | Verify username/password, check account status |
| 422 Unprocessable Entity | Semantic error in data | Review YANG constraints, validate payload |
| 409 Conflict | State conflict on device | Check device state, resolve conflicts manually |
| Connection timeout | Device unreachable | Verify network connectivity, check firewall rules |
| SSL certificate error | Certificate validation failure | Add cert to trusted store or disable (lab only) |

### 8.3 Diagnostic Commands

**NETCONF Debugging**:
```xml
<!-- Enable logging on device -->
configure terminal
  netconf
    logging enable all
    logging file /var/log/netconf.log
  exit

<!-- Monitor NETCONF requests -->
monitor netconf operations

<!-- Check NETCONF capability -->
show netconf capabilities
```

**RESTCONF Debugging**:
```bash
# Test connectivity
curl -v -k -u admin:password \
  https://10.1.4.1:8443/restconf/yang-library/modules-state

# Check available modules
curl -s -k -u admin:password \
  https://10.1.4.1:8443/restconf/yang-library/modules-state \
  | jq '.ietf-yang-library:modules-state.module[] | select(.conformance-type=="implement") | .name'

# Test YANG model
curl -X OPTIONS \
  -H "Accept: application/yang-data+json" \
  https://10.1.4.1:8443/restconf/data
```

---

## 9. Standards Compliance

### 9.1 Reference Standards

- **RFC 6241**: NETCONF Protocol
- **RFC 8040**: RESTCONF API
- **RFC 7950**: YANG Data Model Language 1.1
- **RFC 6241 Section 8**: NETCONF Sessions
- **RFC 8341**: NETCONF Access Control
- **OpenConfig**: Network device models (https://github.com/openconfig)

### 9.2 Validation and Testing

**Compliance Checklist**:
- [ ] Device supports NETCONF 1.0 or 1.1
- [ ] Device supports RESTCONF per RFC 8040
- [ ] YANG models validate against RFC 7950
- [ ] All operations tested in lab environment
- [ ] Security requirements met (TLS, authentication)
- [ ] Error handling implemented for all operations
- [ ] Fallback procedures documented
- [ ] Performance benchmarks established

---

## References

- **IETF NETCONF Working Group**: https://tools.ietf.org/wg/netconf/
- **YANG Registry**: https://yang.ietf.org/
- **OpenConfig Models**: https://github.com/openconfig/public
- **Cisco NETCONF**: https://developer.cisco.com/docs/ios-xe/
- **Juniper NETCONF**: https://www.juniper.net/documentation/

**Last Revision**: 2025-11-19
**Next Review**: 2026-05-19
**Owner**: Network Architecture and Automation Team
