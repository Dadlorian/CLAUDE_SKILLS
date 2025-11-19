# YANG Data Models Reference

## YANG Overview

YANG (RFC 6020, RFC 7950) is a data modeling language for NETCONF and RESTCONF, providing structured schema for network devices.

## YANG Basic Structure

### Module Definition
```yang
module ietf-interfaces {
  yang-version 1.1;
  namespace "urn:ietf:params:xml:ns:yang:ietf-interfaces";
  prefix if;

  organization "IETF NETMOD (NETCONF Data Modeling Language)";
  contact "WG Web: <http://tools.ietf.org/wg/netmod/>";
  description "IETF interfaces module";

  revision 2018-02-20 {
    description "Updated version";
    reference "RFC 8343";
  }

  // Typedefs, groupings, RPC, data model definitions
}
```

## Common Data Types

### Built-in Types
```yang
// String types
leaf hostname {
  type string;
  mandatory true;
}

// Numeric types
leaf mtu {
  type uint16;
  default 1500;
}

leaf metric {
  type int32;
  range "0..4294967295";
}

// Boolean
leaf enabled {
  type boolean;
  default true;
}

// Enumeration
leaf status {
  type enumeration {
    enum "up" {
      value 1;
    }
    enum "down" {
      value 2;
    }
  }
}

// IP address
leaf ip-address {
  type string {
    pattern '([0-9]{1,3}\.){3}[0-9]{1,3}';
  }
}

// Binary
leaf fingerprint {
  type binary;
}

// Empty (presence container)
leaf shutdown {
  type empty;
}

// Union (multiple types)
leaf port {
  type union {
    type uint16;
    type string;
  }
}

// Bits (multiple flags)
leaf features {
  type bits {
    bit ipv4;
    bit ipv6;
    bit mpls;
  }
}
```

## Container and Leaf Organization

### Basic Structure
```yang
container interfaces {
  description "Interface management";

  list interface {
    key "name";
    description "List of interfaces";

    leaf name {
      type string;
      description "Interface name";
    }

    leaf type {
      type enumeration {
        enum ethernetCsmacd;
        enum fastEther;
        enum gigabitEthernet;
      }
    }

    leaf enabled {
      type boolean;
      default true;
    }

    leaf mtu {
      type uint16;
      default 1500;
    }

    leaf speed {
      type uint64;
      units "bits per second";
    }

    leaf description {
      type string;
    }

    leaf mac-address {
      type string;
      config false;  // Read-only operational data
    }

    container statistics {
      config false;  // Operational data only

      leaf in-octets {
        type yang:counter64;
      }

      leaf out-octets {
        type yang:counter64;
      }

      leaf in-discards {
        type yang:counter64;
      }

      leaf out-discards {
        type yang:counter64;
      }
    }
  }
}
```

## Cisco IOS-XE YANG Model Example

### Native Configuration
```yang
container native {
  description "IOS-XE native data model";

  container hostname {
    description "Set system hostname";
    leaf hostname {
      type string;
    }
  }

  container interface {
    description "Interface configuration";

    container Ethernet {
      list Ethernet {
        key "number";
        leaf number {
          type string;
        }

        leaf description {
          type string;
        }

        leaf enabled {
          type boolean;
          default true;
        }

        container ip {
          leaf address {
            type string;  // IP address
          }

          leaf mask {
            type string;  // Subnet mask
          }
        }

        container ipv6 {
          list address {
            key "ipaddress";
            leaf ipaddress {
              type string;  // IPv6 address
            }
          }
        }

        container switchport {
          presence "Enable switchport";
          leaf mode {
            type enumeration {
              enum access;
              enum trunk;
            }
          }

          leaf access {
            container vlan {
              leaf vlan-id {
                type uint16;
                range "1..4094";
              }
            }
          }
        }
      }
    }
  }

  container router {
    description "Routing protocols";

    container bgp {
      list bgp {
        key "id";
        leaf id {
          type uint32;  // AS number
        }

        container bgp-global-config {
          leaf router-id {
            type string;  // IP address
          }

          leaf log-neighbor-changes {
            type empty;
          }
        }

        container address-family {
          list address-family-af {
            key "af-name";
            leaf af-name {
              type string;  // ipv4 unicast, ipv6 unicast, etc.
            }

            leaf redistribute {
              type string;
            }
          }
        }

        container neighbor {
          list neighbor {
            key "id";
            leaf id {
              type string;  // IP address or hostname
            }

            leaf remote-as {
              type uint32;
            }

            leaf description {
              type string;
            }
          }
        }
      }
    }

    container ospf {
      list ospf {
        key "id";
        leaf id {
          type uint16;  // OSPF process ID
        }

        leaf router-id {
          type string;  // IP address
        }

        container network {
          list network {
            key "area";
            leaf area {
              type string;
            }

            leaf ip {
              type string;
            }

            leaf mask {
              type string;
            }
          }
        }
      }
    }
  }

  container line {
    description "Line configuration";

    container console {
      leaf speed {
        type uint32;
      }

      leaf exec-timeout {
        type string;  // minutes seconds
      }
    }

    container vty {
      leaf transport {
        type enumeration {
          enum ssh;
          enum telnet;
        }
      }
    }
  }
}
```

## Juniper Junos YANG Model Example

### Junos Configuration
```yang
container configuration {
  description "Junos configuration";

  leaf host-name {
    type string;
  }

  container system {
    leaf time-zone {
      type string;
    }

    leaf ntp {
      type empty;
    }

    container ntp {
      list server {
        key "name";
        leaf name {
          type string;  // NTP server address
        }
      }
    }

    container syslog {
      list file {
        key "name";
        leaf name {
          type string;  // Log filename
        }

        leaf any {
          type enumeration {
            enum emergency;
            enum alert;
            enum critical;
            enum error;
            enum warning;
            enum notice;
            enum info;
            enum debug;
          }
        }
      }

      leaf console {
        type enumeration {
          enum any;
          enum critical;
          enum error;
          enum warning;
        }
      }
    }
  }

  container interfaces {
    list interface {
      key "name";
      leaf name {
        type string;  // Interface name (e.g., ge-0/0/0)
      }

      leaf description {
        type string;
      }

      leaf mtu {
        type uint16;
      }

      container unit {
        list unit {
          key "name";
          leaf name {
            type string;  // Unit number
          }

          leaf family {
            type enumeration {
              enum inet;
              enum inet6;
            }
          }

          container address {
            list address {
              key "name";
              leaf name {
                type string;  // IP address with prefix
              }
            }
          }
        }
      }
    }
  }

  container routing-options {
    leaf router-id {
      type string;
    }

    container autonomous-system {
      leaf as-number {
        type uint32;
      }
    }

    list static {
      key "route";
      leaf route {
        type string;
      }

      leaf next-hop {
        type string;
      }
    }
  }

  container protocols {
    container bgp {
      leaf local-as {
        type uint32;
      }

      container group {
        list group {
          key "name";
          leaf name {
            type string;
          }

          leaf peer-as {
            type uint32;
          }

          container neighbor {
            list neighbor {
              key "name";
              leaf name {
                type string;  // Neighbor IP
              }
            }
          }
        }
      }
    }

    container ospf {
      list area {
        key "name";
        leaf name {
          type string;  // Area ID
        }

        container interface {
          list interface {
            key "name";
            leaf name {
              type string;  // Interface name
            }
          }
        }
      }
    }
  }

  container access {
    container profile {
      leaf radius-server {
        type string;
      }

      leaf tacplus-server {
        type string;
      }
    }
  }
}
```

## Working with YANG Models

### Retrieving YANG Modules
```bash
# Via NETCONF
ssh -s netconf://admin@192.168.1.1 < get_yang_modules.xml

# Via RESTCONF
curl https://192.168.1.1/restconf/data/ietf-yang-library:yang-library

# Device-specific
# Cisco: https://192.168.1.1/restconf/data/ietf-yang-library:modules-state
# Juniper: request yang model list
```

### Validating Configuration Against YANG
```python
from ncclient import manager

device = manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password'
)

# Validate configuration
config_xml = '''
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>Ethernet0/0</name>
      <enabled>true</enabled>
    </interface>
  </interfaces>
</config>
'''

# NETCONF will validate against YANG schema
reply = device.edit_config(target='candidate', config=config_xml)
print(reply)
```

## RPC Operations

### RPC Definitions in YANG
```yang
rpc reboot {
  description "Reboot the system";
  input {
    leaf delay {
      type uint32;
      units "seconds";
    }
  }
  output {
    leaf message {
      type string;
    }
  }
}
```

### Invoking RPC
```python
from ncclient import manager
from ncclient.xml_ import *

device = manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='password'
)

# Execute RPC
rpc_request = '''
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <reboot xmlns="http://example.com/custom">
    <delay>300</delay>
  </reboot>
</rpc>
'''

response = device.dispatch(rpc_request)
print(response)
```

## Common IETF YANG Modules

| Module | Purpose | RFC |
|--------|---------|-----|
| ietf-interfaces | Interface management | RFC 8343 |
| ietf-ip | IP configuration | RFC 8344 |
| ietf-routing | Routing configuration | RFC 8349 |
| ietf-yang-types | Common types | RFC 6991 |
| ietf-inet-types | Internet types | RFC 6991 |
| ietf-netconf | NETCONF operations | RFC 6241 |
| ietf-netconf-with-defaults | Default values | RFC 6243 |

---

**Last Updated**: 2025-11-19
**Reference**: RFC 6020, RFC 7950, pyang.readthedocs.io
