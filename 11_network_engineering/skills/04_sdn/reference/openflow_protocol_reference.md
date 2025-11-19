# OpenFlow Protocol Reference

## Overview
OpenFlow is an open standard that specifies how SDN controllers communicate with switches and routers to determine the forwarding of network packets. It enables network switches to be managed by remote controllers.

## OpenFlow Versions

### OpenFlow 1.0
**Release**: 2009
**Key Features**:
- Basic flow table architecture
- MAC learning and forwarding
- Port statistics
- Basic QoS support

### OpenFlow 1.3
**Release**: 2012
**Key Features**:
- Multiple flow tables with goto_table
- Meters for QoS and rate limiting
- IPv6 support
- Group tables for multicast

### OpenFlow 1.4
**Release**: 2013
**Key Features**:
- Table features discovery
- Bundle transactions (atomic operations)
- Optical extensions

### OpenFlow 1.5+
**Release**: 2014+
**Key Features**:
- Hardware-independent packet processing
- Evolvable architecture
- EXT-256 for larger match fields

## Protocol Structure

### Message Types

#### Controller-to-Switch Messages
**Feature Request/Reply**: Discover switch capabilities
**Configuration**: Get/set switch configuration
**Modify-State**: Add, delete, modify flow rules
**Read-State**: Query statistics
**Packet-Out**: Send packets to switch

#### Switch-to-Controller Messages
**Packet-In**: Switch sends packet to controller (no matching rule)
**Flow-Removed**: Flow rule expired or deleted
**Port-Status**: Physical port status changes
**Error**: Error messages from switch
**Statistics-Reply**: Response to statistics requests

#### Symmetric Messages (Both Directions)
**Hello**: Identify protocol version and capabilities
**Echo-Request/Reply**: Keepalive and latency measurement
**Vendor**: Vendor-specific extensions

### Message Format
```
OpenFlow Header (8 bytes)
├─ Version (1 byte)
├─ Type (1 byte)
├─ Length (2 bytes)
└─ Transaction ID (4 bytes)

Message Payload (variable)
```

## Flow Table Architecture

### Flow Table Entry
```
Match Fields
├─ Ingress Port
├─ Ethernet (Source MAC, Dest MAC, Type)
├─ VLAN (ID, Priority)
├─ IP (Source IP, Dest IP, DSCP, ECN, Protocol)
├─ Transport (TCP/UDP ports, ICMP type/code)
├─ MPLS (Label, TC, BoS)
└─ Tunnel (ID, IPv6 Flabel)

Instructions
├─ Apply-Actions: Immediate actions
├─ Goto-Table: Forward to next table
├─ Write-Metadata: Store value for next table
└─ Meter: Rate limiting

Statistics
├─ Packet count
├─ Byte count
└─ Duration
```

### Actions
**Forwarding**:
- output: Send to port
- group: Apply group actions
- drop: Discard packet

**Modification**:
- set-field: Modify header fields
- push/pop-vlan: Add/remove VLAN tags
- push/pop-mpls: Add/remove MPLS labels
- dec-ttl: Decrement Time-to-Live

**Queuing**:
- set-queue: Select output queue
- meter: Apply meter (rate limit)

**Encapsulation**:
- push-tunnel: Tunnel encapsulation
- pop-tunnel: Tunnel decapsulation

## Group Tables

### Group Types
**All**: Execute all buckets (broadcast/multicast)
**Select**: Execute one bucket (load balancing)
**Indirect**: Simple pointer indirection
**Fast Failover**: Execute first live bucket

### Group Bucket Structure
```
Bucket
├─ Weight (for select groups)
├─ Watch Port
├─ Watch Group
└─ Actions
```

## Meters

### Meter Bands
**Drop**: Discard exceeding packets
**Remark DSCP**: Mark packets and forward
**Experimenter**: Vendor-specific actions

### Configuration
```
Meter ID
├─ Flags (kbps, pps, burst, stats)
├─ Meter Bands (drop rate, burst)
└─ Statistics (packet/byte count)
```

## Statistics

### Query Types
- **Port Statistics**: Physical port counters
- **Flow Statistics**: Per-flow packet/byte counts
- **Table Statistics**: Flow table utilization
- **Group Statistics**: Per-group counters
- **Meter Statistics**: Per-meter counters
- **Queue Statistics**: Per-queue packet counts

### Counters
- Sent packets/bytes
- Received packets/bytes
- Dropped packets
- Errors and collisions

## Match Fields Priority

**Exact Match** (highest priority)
- All fields must match exactly

**Prefix Match**
- IP addresses (CIDR notation)
- MAC addresses (with mask)

**Wildcard**
- Any value acceptable
- Represented as 0x0/0x0

## Transaction Handling

### Request/Response Pattern
```
Controller → Switch: OpenFlow Message
                     (with Transaction ID)
                     ↓
           Switch → Controller: Reply
                     (with same Transaction ID)
```

### Multi-Message Transactions
- Bundle transactions (OpenFlow 1.4+)
- Atomic execution of multiple commands
- All-or-nothing semantics

## Packet-In Message Flow

### Typical Reactive Forwarding Sequence
1. **Packet arrives** at switch without matching flow
2. **Packet-In sent** to controller with:
   - Ingress port
   - Reason (no match, action)
   - Packet data (full or buffered)
3. **Controller processes** packet (destination learning, path computation)
4. **Flow-Mod sent** to install rules on switches along path
5. **Packet-Out sent** to inject packet into switch
6. **Subsequent packets** match installed rules (no controller involvement)

## Connection Management

### Switch-to-Controller Connection
- **Primary Channel**: Main OpenFlow channel (6653 or custom)
- **Auxiliary Channels**: Optional additional connections
- **Connection Failover**: Switch supports multiple controllers
- **TLS Security**: Encrypted communication option

### Controller Discovery
- **Out-of-Band**: Manual configuration
- **In-Band**: DHCP option, DNS lookup

## Capabilities Negotiation

### Version Negotiation
```
Controller (1.5) ──Hello──> Switch
                  <──Hello── (supports 1.3)
                  ↓
           Use OpenFlow 1.3
```

### Feature Discovery
- Supported match fields
- Supported actions
- Group types supported
- Meter capabilities
- Flow table depth
- Maximum packet buffer size

## Common OpenFlow Extensions

### NICIRA Extensions (Now OVS Standard)
- Extended actions
- Connection tracking
- Advanced match fields
- Register operations

### PISA (Packet In-Network Service Abstractions)
- Hardware-independent packet processing

## Implementation Considerations

### Flow Timeout Handling
**Idle Timeout**: Remove rule if no packets seen
**Hard Timeout**: Remove rule after absolute time

### Buffer Management
- **Max Entries**: Limited switch buffer
- **Buffer IDs**: Referenced in Packet-Out messages
- **Overflow**: Oldest packets discarded

### Performance Tuning
- **Table Size**: Hardware dependent (thousands to millions)
- **Bandwidth**: Protocol overhead typically <1%
- **Latency**: Sub-millisecond for installed rules

## Security Aspects

### Threats
- Unauthorized flow rule installation
- Denial of service (flooding packet-in)
- Eavesdropping on flow information

### Mitigations
- TLS encryption and authentication
- Rate limiting on packet-in messages
- Access control on OpenFlow channels
- Signing of critical messages
