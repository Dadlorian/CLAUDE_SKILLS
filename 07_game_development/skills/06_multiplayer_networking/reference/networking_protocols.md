# Networking Protocols Reference

## Overview

Choosing the right networking protocol is crucial for multiplayer games. Different protocols offer different trade-offs between reliability, latency, and ordering. This reference covers the major protocols and their applications in game networking.

## Transport Protocols

### TCP (Transmission Control Protocol)

**Characteristics**:
- **Reliable**: Guarantees packet delivery
- **Ordered**: Packets arrive in order sent
- **Connection-oriented**: Requires handshake
- **Flow control**: Prevents overwhelming receiver
- **Congestion control**: Adapts to network conditions

**Pros**:
- No packet loss (automatic retransmission)
- No duplicate packets
- Built-in error checking
- Widely supported

**Cons**:
- **Head-of-line blocking**: One lost packet blocks entire stream
- Higher latency (acknowledgments, retransmission)
- Connection overhead
- Not suitable for real-time gameplay

**Use Cases**:
- Game lobbies and matchmaking
- Chat systems
- Login/authentication
- Asset downloads
- Turn-based games
- HTTP/REST APIs

**Example - TCP Head-of-Line Blocking**:
```
Packet 1: Sent at t=0ms
Packet 2: Sent at t=16ms (lost!)
Packet 3: Sent at t=32ms (arrives)
Packet 4: Sent at t=48ms (arrives)

Application receives:
- Packet 1 at t=50ms
- Waiting for Packet 2... (blocks)
- Packet 2 retransmitted and arrives at t=200ms
- Packet 3 delivered at t=200ms (was waiting)
- Packet 4 delivered at t=200ms (was waiting)

Result: 150ms delay for packets 3 & 4 due to Packet 2
```

### UDP (User Datagram Protocol)

**Characteristics**:
- **Unreliable**: No delivery guarantee
- **Unordered**: Packets may arrive out of order
- **Connectionless**: No handshake required
- **Low overhead**: Minimal protocol overhead
- **No congestion control**: Sender controls rate

**Pros**:
- Minimal latency (no retransmission delay)
- No head-of-line blocking
- Simple protocol
- Full control over reliability

**Cons**:
- Packets can be lost (1-10% loss typical)
- Packets can arrive out of order
- Packets can be duplicated
- Must implement reliability yourself
- NAT traversal challenges

**Use Cases**:
- Fast-paced multiplayer (FPS, racing, fighting)
- Real-time movement and position updates
- Voice chat (VoIP)
- Live streaming
- Any latency-sensitive gameplay

**Implementation Pattern**:
```csharp
// UDP sending
using (var udpClient = new UdpClient())
{
    byte[] data = SerializeGameState();
    udpClient.Send(data, data.Length, serverEndpoint);
}

// UDP receiving
using (var udpClient = new UdpClient(port))
{
    IPEndPoint remoteEndpoint = new IPEndPoint(IPAddress.Any, 0);
    byte[] data = udpClient.Receive(ref remoteEndpoint);
    ProcessGameState(data);
}
```

### Reliable UDP Implementations

Since games often need *selective* reliability, many games implement reliability on top of UDP:

**Reliability Options**:
1. **Unreliable**: Send and forget (position updates)
2. **Reliable**: Guarantee delivery (player death, item pickup)
3. **Ordered**: Guarantee order (chat messages)
4. **Sequenced**: Only latest matters (discard old position updates)

**Custom Reliable UDP Pattern**:
```csharp
public class ReliableUDP
{
    private Dictionary<ushort, PendingPacket> awaitingAck;
    private ushort nextSequenceNumber = 0;

    public void SendReliable(byte[] data)
    {
        ushort sequence = nextSequenceNumber++;

        var packet = new ReliablePacket
        {
            SequenceNumber = sequence,
            Data = data,
            SentTime = DateTime.Now
        };

        // Send packet
        SendUDP(packet.Serialize());

        // Store for potential retransmission
        awaitingAck[sequence] = new PendingPacket
        {
            Packet = packet,
            SendTime = DateTime.Now,
            RetryCount = 0
        };
    }

    public void OnAckReceived(ushort sequence)
    {
        // Remove from pending
        awaitingAck.Remove(sequence);
    }

    public void Update()
    {
        var now = DateTime.Now;

        foreach (var kvp in awaitingAck.ToList())
        {
            var pending = kvp.Value;

            // Retransmit if timeout
            if ((now - pending.SendTime).TotalMilliseconds > 200)
            {
                if (pending.RetryCount < 5)
                {
                    SendUDP(pending.Packet.Serialize());
                    pending.SendTime = now;
                    pending.RetryCount++;
                }
                else
                {
                    // Give up after 5 retries
                    OnPacketLost(pending.Packet);
                    awaitingAck.Remove(kvp.Key);
                }
            }
        }
    }
}
```

## Higher-Level Protocols

### WebSocket

**Characteristics**:
- Built on TCP
- Bi-directional full-duplex
- HTTP-compatible (port 80/443)
- Frame-based messaging
- Text or binary data

**Pros**:
- Works through firewalls (HTTP/HTTPS)
- Widely supported (browsers, mobile)
- TLS/SSL support built-in
- No NAT traversal issues

**Cons**:
- TCP head-of-line blocking
- Higher latency than UDP
- Connection overhead

**Use Cases**:
- Browser-based games (HTML5)
- Mobile games (simpler than custom UDP)
- Turn-based or slower-paced games
- Games requiring firewall/proxy traversal

**Example - WebSocket Server**:
```csharp
public class WebSocketGameServer
{
    private WebSocketServer wss;

    public void Start(int port)
    {
        wss = new WebSocketServer($"ws://0.0.0.0:{port}");

        wss.AddWebSocketService<GameService>("/game");
        wss.Start();
    }
}

public class GameService : WebSocketBehavior
{
    protected override void OnMessage(MessageEventArgs e)
    {
        var input = Deserialize<PlayerInput>(e.Data);
        ProcessInput(input);

        var state = GetGameState();
        Send(Serialize(state));
    }
}
```

### WebRTC

**Characteristics**:
- Peer-to-peer capable
- Built-in NAT traversal (STUN/TURN)
- Multiple transport (UDP, TCP fallback)
- Encryption by default
- Data channels + media streams

**Pros**:
- P2P reduces server costs
- Low latency (direct connections)
- NAT traversal handled
- Secure by default

**Cons**:
- Complex setup (signaling server required)
- Browser-focused (limited native support)
- Difficult to debug
- Less control over transport

**Use Cases**:
- Peer-to-peer games
- Browser-based real-time games
- Voice/video chat in games
- Mobile games with P2P

### QUIC (Quick UDP Internet Connections)

**Characteristics**:
- Modern protocol by Google (HTTP/3 basis)
- Built on UDP
- Multiple independent streams
- Encryption built-in (TLS 1.3)
- Fast connection establishment

**Pros**:
- No head-of-line blocking (between streams)
- Faster than TCP connection setup
- Modern congestion control
- Connection migration (survives IP changes)

**Cons**:
- Less widely deployed
- Complex implementation
- Still maturing

**Use Cases**:
- Next-generation game protocols
- Mobile games (survives network switches)
- Future replacement for TCP

## Application-Level Protocols

### Serialization Formats

#### Binary Formats

**Custom Binary** (most efficient):
```csharp
// Write
writer.Write((ushort)playerId);        // 2 bytes
writer.Write((float)position.x);       // 4 bytes
writer.Write((float)position.y);       // 4 bytes
writer.Write((byte)health);            // 1 byte
// Total: 11 bytes

// Read
ushort playerId = reader.ReadUInt16();
float x = reader.ReadSingle();
float y = reader.ReadSingle();
byte health = reader.ReadByte();
```

**Pros**: Smallest size, fastest
**Cons**: Manual serialization, versioning challenges

**Protocol Buffers (protobuf)**:
```protobuf
message PlayerUpdate {
  uint32 player_id = 1;
  float position_x = 2;
  float position_y = 3;
  uint32 health = 4;
}
```

**Pros**: Efficient, versioning support, cross-language
**Cons**: Requires compilation, slightly larger than custom

**MessagePack**:
```csharp
var data = new { playerId = 42, position = new { x = 10.5f, y = 20.3f }, health = 80 };
byte[] bytes = MessagePackSerializer.Serialize(data);
```

**Pros**: JSON-like ease, binary efficiency
**Cons**: Slightly larger than protobuf

**FlatBuffers**:
```csharp
var builder = new FlatBufferBuilder(1024);
var pos = Vec2.CreateVec2(builder, 10.5f, 20.3f);
var player = Player.CreatePlayer(builder, 42, pos, 80);
builder.Finish(player.Value);
byte[] bytes = builder.SizedByteArray();
```

**Pros**: Zero-copy deserialization (fastest reads)
**Cons**: Complex API, write overhead

#### Text Formats

**JSON**:
```json
{
  "playerId": 42,
  "position": {"x": 10.5, "y": 20.3},
  "health": 80
}
```

**Pros**: Human-readable, debuggable, widespread support
**Cons**: Large size (5-10x binary), slow parsing

**Use Case**: Debugging, configuration, non-critical data

**XML**:
```xml
<player>
  <id>42</id>
  <position x="10.5" y="20.3"/>
  <health>80</health>
</player>
```

**Pros**: Self-documenting, validation support
**Cons**: Even larger than JSON, verbose

**Use Case**: Avoid for game networking; use config files only

### Comparison Table

| Format | Size (bytes) | Serialize (μs) | Deserialize (μs) | Readability |
|--------|--------------|----------------|------------------|-------------|
| Custom Binary | 11 | 0.5 | 0.5 | None |
| Protobuf | 14 | 2.0 | 1.5 | Low |
| MessagePack | 18 | 3.0 | 2.5 | Low |
| FlatBuffers | 16 | 5.0 | 0.1 | None |
| JSON | 65 | 15.0 | 20.0 | High |
| XML | 95 | 25.0 | 30.0 | High |

**Recommendation**: Custom binary for performance-critical, JSON for debugging/tooling

## Network Topologies

### Client-Server

```
    Client A ──┐
               │
    Client B ──┼── Server (Authority)
               │
    Client C ──┘
```

**Pros**:
- Server authority (cheat prevention)
- Scalable to many players
- Consistent game state

**Cons**:
- Server costs
- Server latency affects all players
- Single point of failure

**Use Cases**: Most competitive multiplayer games

### Peer-to-Peer (Full Mesh)

```
Client A ──────── Client B
    │                │
    │                │
    └───── Client C ─┘
```

**Pros**:
- No server costs
- Lowest possible latency (direct)
- No single point of failure

**Cons**:
- Cheating easier (no authority)
- NAT traversal required
- Scales poorly (N² connections)

**Use Cases**: Small party games, fighting games, co-op

### Peer-to-Peer (Host as Server)

```
    Client B ──┐
               │
    Client C ──┼── Host (Client A acting as server)
               │
    Client D ──┘
```

**Pros**:
- No dedicated server needed
- Host has authority (some cheat prevention)
- Scales better than mesh

**Cons**:
- Host has advantage (0ms latency)
- Host leaving breaks game
- Host must be trusted

**Use Cases**: Casual multiplayer, co-op campaigns

### Hybrid (Regional Servers + Matchmaking)

```
Matchmaking Server
       │
       ├── Regional Server (NA)
       │      └── Clients A, B, C
       │
       └── Regional Server (EU)
              └── Clients D, E, F
```

**Pros**:
- Low latency (regional proximity)
- Scalable infrastructure
- Centralized matchmaking

**Cons**:
- Complex infrastructure
- Higher costs
- Regional imbalances possible

**Use Cases**: Large-scale competitive games (Fortnite, Overwatch)

## NAT Traversal

### The NAT Problem

**Network Address Translation** (NAT) allows multiple devices to share one public IP. Problem: Incoming connections are blocked by default.

```
Home Network (192.168.1.x)        Internet
     │
Device A (192.168.1.2) ───┐
                          ├── Router (Public IP: 203.0.113.5) ─── Internet
Device B (192.168.1.3) ───┘
```

Device A wants to connect to Device B at another location:
- A doesn't know B's public IP (B is behind NAT)
- B's router blocks unsolicited incoming connections

### STUN (Session Traversal Utilities for NAT)

**Purpose**: Discover your public IP and port

```csharp
// Client queries STUN server
Request: "What's my public IP?"
STUN Server Response: "You appear as 203.0.113.5:42580"

// Client can now share this address with peers
```

**Limitation**: Only works for certain NAT types (Cone NAT)

### TURN (Traversal Using Relays around NAT)

**Purpose**: Relay traffic when direct connection impossible

```
Client A ─── TURN Server ─── Client B
        (relay)         (relay)
```

**Pros**: Always works (fallback)
**Cons**: Increased latency, server bandwidth costs

### ICE (Interactive Connectivity Establishment)

**Purpose**: Comprehensive NAT traversal strategy

**Process**:
1. Try direct connection (if both have public IPs)
2. Try STUN (discover public endpoint)
3. Try TURN (relay if necessary)
4. Use best available connection

**Implementation** (WebRTC includes ICE):
```javascript
// WebRTC automatically handles ICE
peerConnection.createOffer()
  .then(offer => peerConnection.setLocalDescription(offer))
  .then(() => signaling.send({type: 'offer', sdp: peerConnection.localDescription}));
```

## Protocol Selection Guide

### Decision Matrix

**Choose UDP when**:
- Real-time gameplay (FPS, racing, fighting)
- Player movement and position
- Latency < 100ms critical
- Some packet loss acceptable

**Choose TCP when**:
- Turn-based gameplay
- Chat and lobby systems
- Login/authentication
- File transfers
- Order and reliability critical

**Choose WebSocket when**:
- Browser-based games
- Simpler implementation preferred
- Firewall/proxy traversal required
- Moderate latency acceptable (50-150ms)

**Choose WebRTC when**:
- Peer-to-peer desired
- Browser-based real-time game
- Voice/video chat integrated
- NAT traversal required

### Hybrid Approach (Recommended)

Most production games use **multiple protocols**:

```
TCP/WebSocket:
- Login and authentication
- Matchmaking
- Chat
- Inventory management
- Friend lists

UDP:
- Player movement
- Combat actions
- Projectiles
- Physics updates

HTTP/REST:
- Leaderboards
- Player profiles
- Store transactions
- Analytics
```

## Performance Characteristics

### Latency Comparison

| Protocol | Typical Latency | Notes |
|----------|-----------------|-------|
| UDP | 20-100ms | Direct, no retransmit |
| TCP | 50-150ms | Handshake + retransmit |
| WebSocket | 50-200ms | TCP + WebSocket overhead |
| WebRTC | 30-120ms | UDP-based, P2P advantage |
| QUIC | 40-130ms | Faster than TCP, slower than raw UDP |

### Bandwidth Comparison

**Example: 60Hz position update for one player**

| Protocol | Overhead | Total per packet |
|----------|----------|------------------|
| Raw UDP | 28 bytes (IP + UDP) | 40 bytes |
| TCP | 40 bytes (IP + TCP) | 52 bytes |
| WebSocket | 40 + 2-6 bytes (frame) | 54-58 bytes |

**At 60 packets/second**:
- UDP: 2.4 KB/s
- TCP: 3.1 KB/s
- WebSocket: 3.2-3.5 KB/s

**For 100 players**: UDP saves ~70 KB/s per client vs WebSocket

## Best Practices

### Protocol Guidelines

1. **Use UDP for game state**: Movement, combat, physics
2. **Use TCP for metadata**: Chat, matchmaking, transactions
3. **Implement selective reliability**: Not all UDP packets need reliability
4. **Compress data**: Bandwidth is precious
5. **Measure performance**: Profile packet sizes and frequencies
6. **Handle disconnections**: Timeouts, reconnection logic
7. **Version protocols**: Support multiple versions during updates
8. **Encrypt sensitive data**: Login, purchases, chat

### Common Mistakes

**Mistake 1**: Using TCP for real-time gameplay
- Symptom: Laggy feel, input delay
- Solution: Switch to UDP with client prediction

**Mistake 2**: Not handling packet loss
- Symptom: Choppy movement, missing events
- Solution: Implement reliability for critical events

**Mistake 3**: Sending too frequently
- Symptom: Bandwidth explosion
- Solution: Delta compression, interest management

**Mistake 4**: No protocol versioning
- Symptom: Broken compatibility after updates
- Solution: Version numbers in packet headers

## Conclusion

Choosing the right protocol is crucial:
- **Fast-paced games**: UDP with custom reliability
- **Browser games**: WebSocket or WebRTC
- **Turn-based/casual**: TCP or WebSocket
- **Hybrid**: Use multiple protocols for different needs

Always:
- Measure latency and bandwidth
- Test on real networks (not just LAN)
- Handle packet loss and disconnections
- Compress and optimize data
- Consider NAT traversal early

The protocol is your foundation. Choose wisely based on your game's needs, and build robust systems on top.
