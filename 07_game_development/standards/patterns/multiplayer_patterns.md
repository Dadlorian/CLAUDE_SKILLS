# Multiplayer Networking Patterns
## Elite Professional Patterns for Game Networking

### Philosophy
This guide synthesizes networking patterns from:
- **Gaffer on Games** - Glenn Fiedler's authoritative networking series
- **Valve** - Source Engine multiplayer networking
- **Epic Games** - Unreal replication system
- **Gabriel Gambetta** - Fast-Paced Multiplayer guide
- **Riot Games** - League of Legends networking architecture
- **Bungie** - Destiny netcode (GDC talks)

---

## Core Networking Architectures

### 1. Client-Server Architecture (Authoritative Server)

**Problem**: Maintaining game state consistency across multiple clients

**Solution**: Server is the authority, clients send inputs and receive authoritative state

**When to Use**:
- Most multiplayer games (FPS, RPG, MOBA, Battle Royale)
- When cheat prevention is important
- When consistency matters more than absolute lowest latency

**Architecture**:

```
Client 1 → [Input] → Server (Authority) → [State Update] → Client 1
Client 2 → [Input] → Server (Authority) → [State Update] → Client 2
Client 3 → [Input] → Server (Authority) → [State Update] → Client 3
```

**Implementation**:

```csharp
// Server-authoritative movement (Unity + Mirror)
public class ServerAuthoritativeMovement : NetworkBehaviour
{
    [SyncVar] private Vector3 serverPosition;
    [SyncVar] private Quaternion serverRotation;

    private float moveSpeed = 5f;
    private Vector3 velocity;

    // Client sends input to server
    [Command]
    void CmdMove(Vector3 inputDirection)
    {
        // Server validates and processes input
        if (inputDirection.magnitude > 1f)
            inputDirection = inputDirection.normalized;  // Prevent cheating

        velocity = inputDirection * moveSpeed;
    }

    // Server updates (authoritative)
    void FixedUpdate()
    {
        if (isServer)
        {
            serverPosition += velocity * Time.fixedDeltaTime;
            serverRotation = Quaternion.LookRotation(velocity);
            transform.position = serverPosition;
            transform.rotation = serverRotation;
        }
    }

    // Client syncs to server state
    void Update()
    {
        if (!isServer)
        {
            transform.position = Vector3.Lerp(transform.position, serverPosition, Time.deltaTime * 10f);
            transform.rotation = Quaternion.Slerp(transform.rotation, serverRotation, Time.deltaTime * 10f);
        }
    }
}
```

**Benefits**:
- ✅ Server has complete authority (cheat prevention)
- ✅ Consistent state across all clients
- ✅ Easier to implement than P2P

**Drawbacks**:
- ❌ Requires dedicated servers
- ❌ Input latency for player actions
- ❌ Server costs

---

### 2. Client-Side Prediction

**Problem**: Server authority causes input lag (player presses jump, waits for server response)

**Solution**: Client predicts result locally, server validates and corrects if needed

**When to Use**:
- Fast-paced games (FPS, racing, sports)
- When responsive controls are critical
- Always combined with authoritative server

**Implementation**:

```csharp
public class PredictedMovement : NetworkBehaviour
{
    // Movement state
    [System.Serializable]
    public struct MovementState
    {
        public Vector3 position;
        public Vector3 velocity;
        public uint tick;
    }

    // Input command
    [System.Serializable]
    public struct InputCommand
    {
        public Vector3 direction;
        public bool jump;
        public uint tick;
        public float deltaTime;
    }

    [SyncVar] private MovementState serverState;

    private Queue<InputCommand> pendingCommands = new Queue<InputCommand>();
    private uint clientTick = 0;

    [Header("Settings")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;

    void Update()
    {
        if (!isLocalPlayer) return;

        // Gather input
        InputCommand input = new InputCommand
        {
            direction = new Vector3(
                Input.GetAxisRaw("Horizontal"),
                0,
                Input.GetAxisRaw("Vertical")
            ).normalized,
            jump = Input.GetButtonDown("Jump"),
            tick = clientTick++,
            deltaTime = Time.deltaTime
        };

        // Predict locally
        ApplyInput(input);

        // Store for reconciliation
        pendingCommands.Enqueue(input);

        // Send to server
        CmdSendInput(input);

        // Limit pending commands (prevent memory leak)
        while (pendingCommands.Count > 60)  // 1 second at 60fps
            pendingCommands.Dequeue();
    }

    [Command]
    void CmdSendInput(InputCommand input)
    {
        // Server processes input
        ApplyInput(input);

        // Send back authoritative state
        RpcReconcile(serverState.tick, transform.position, GetComponent<Rigidbody>().velocity);
    }

    [ClientRpc]
    void RpcReconcile(uint serverTick, Vector3 serverPosition, Vector3 serverVelocity)
    {
        if (!isLocalPlayer) return;

        // Remove acknowledged inputs
        while (pendingCommands.Count > 0 && pendingCommands.Peek().tick <= serverTick)
            pendingCommands.Dequeue();

        // Check for mismatch (threshold prevents jitter from floating point errors)
        if (Vector3.Distance(transform.position, serverPosition) > 0.1f)
        {
            // Reconciliation needed
            transform.position = serverPosition;
            GetComponent<Rigidbody>().velocity = serverVelocity;

            // Re-simulate pending inputs
            foreach (var input in pendingCommands)
                ApplyInput(input);
        }
    }

    void ApplyInput(InputCommand input)
    {
        Rigidbody rb = GetComponent<Rigidbody>();

        // Apply movement
        Vector3 movement = input.direction * moveSpeed * input.deltaTime;
        transform.position += movement;

        // Apply jump
        if (input.jump && IsGrounded())
        {
            rb.velocity = new Vector3(rb.velocity.x, jumpForce, rb.velocity.z);
        }
    }

    bool IsGrounded()
    {
        return Physics.Raycast(transform.position, Vector3.down, 1.1f);
    }
}
```

**Benefits**:
- ✅ Responsive local controls
- ✅ Hides network latency
- ✅ Still server-authoritative

**Drawbacks**:
- ❌ Complex implementation
- ❌ Requires reconciliation logic
- ❌ Can cause "rubber-banding" on corrections

**Reference**:
- Gaffer on Games: "Client-Server Game Architecture"
- Valve: "Source Multiplayer Networking"
- Gabriel Gambetta: "Client-Side Prediction and Server Reconciliation"

---

### 3. Server Reconciliation

**Problem**: Client prediction diverges from server truth (cheating, lag, bugs)

**Solution**: Server sends authoritative state, client corrects and re-simulates

**Key Points**:
- Server processes inputs sequentially
- Server sends back latest authoritative state
- Client checks for mismatch
- If mismatch detected, reset to server state and re-apply pending inputs

**Already shown in Client-Side Prediction implementation above**

---

### 4. Entity Interpolation (for Remote Players)

**Problem**: Remote players appear jittery due to discrete network updates

**Solution**: Interpolate between received states for smooth visual movement

**When to Use**:
- All remote entities in client-server games
- Any networked object that moves
- Non-player controlled entities

**Implementation**:

```csharp
public class NetworkedEntityInterpolation : NetworkBehaviour
{
    // Buffered states for interpolation
    private struct StateMessage
    {
        public double timestamp;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 velocity;
    }

    private readonly CircularBuffer<StateMessage> stateBuffer = new CircularBuffer<StateMessage>(32);

    [SyncVar] private Vector3 syncPosition;
    [SyncVar] private Quaternion syncRotation;

    [Header("Interpolation Settings")]
    [SerializeField] private float interpolationDelay = 0.1f;  // 100ms buffer

    void OnSyncPositionChanged(Vector3 oldPos, Vector3 newPos)
    {
        // Add new state to buffer
        stateBuffer.Add(new StateMessage
        {
            timestamp = NetworkTime.time,
            position = newPos,
            rotation = syncRotation,
            velocity = (newPos - oldPos) / Time.fixedDeltaTime
        });
    }

    void Update()
    {
        if (isLocalPlayer) return;  // Don't interpolate local player

        // Calculate interpolation timestamp
        double interpolationTime = NetworkTime.time - interpolationDelay;

        // Find states to interpolate between
        StateMessage from = default;
        StateMessage to = default;
        bool foundStates = false;

        for (int i = 0; i < stateBuffer.Count - 1; i++)
        {
            if (stateBuffer[i].timestamp <= interpolationTime &&
                interpolationTime <= stateBuffer[i + 1].timestamp)
            {
                from = stateBuffer[i];
                to = stateBuffer[i + 1];
                foundStates = true;
                break;
            }
        }

        if (foundStates)
        {
            // Interpolate
            float t = (float)((interpolationTime - from.timestamp) / (to.timestamp - from.timestamp));

            transform.position = Vector3.Lerp(from.position, to.position, t);
            transform.rotation = Quaternion.Slerp(from.rotation, to.rotation, t);
        }
        else if (stateBuffer.Count > 0)
        {
            // Extrapolate (if we're ahead of received states)
            StateMessage latest = stateBuffer[stateBuffer.Count - 1];
            float extrapolationTime = (float)(interpolationTime - latest.timestamp);

            transform.position = latest.position + latest.velocity * extrapolationTime;
            transform.rotation = latest.rotation;
        }
    }
}

// Circular buffer utility
public class CircularBuffer<T>
{
    private T[] buffer;
    private int start = 0;
    private int count = 0;

    public int Count => count;

    public CircularBuffer(int capacity)
    {
        buffer = new T[capacity];
    }

    public void Add(T item)
    {
        if (count < buffer.Length)
        {
            buffer[count] = item;
            count++;
        }
        else
        {
            buffer[start] = item;
            start = (start + 1) % buffer.Length;
        }
    }

    public T this[int index]
    {
        get
        {
            if (index >= count) throw new IndexOutOfRangeException();
            return buffer[(start + index) % buffer.Length];
        }
    }
}
```

**Benefits**:
- ✅ Smooth visual movement
- ✅ Hides network jitter
- ✅ Low CPU cost

**Drawbacks**:
- ❌ Introduces visual delay (intentional)
- ❌ Remote players appear slightly in the past

**Reference**:
- Gaffer on Games: "Snapshot Interpolation"
- Valve Source networking documentation

---

### 5. Lag Compensation (Server-Side Rewind)

**Problem**: Player shoots at enemy, but enemy already moved on server (latency)

**Solution**: Server "rewinds" time to where entities were when player fired

**When to Use**:
- FPS games with hitscan weapons
- Any game with instant actions (e.g., fighting game strikes)

**Implementation**:

```csharp
public class LagCompensationManager : MonoBehaviour
{
    private struct Snapshot
    {
        public float timestamp;
        public Dictionary<int, TransformState> entityStates;
    }

    private struct TransformState
    {
        public Vector3 position;
        public Quaternion rotation;
    }

    [SerializeField] private float snapshotRate = 60f;  // 60 snapshots/second
    [SerializeField] private float maxHistoryTime = 1f;  // 1 second history

    private readonly Queue<Snapshot> snapshotHistory = new Queue<Snapshot>();
    private float nextSnapshotTime = 0f;

    void FixedUpdate()
    {
        if (Time.time >= nextSnapshotTime)
        {
            TakeSnapshot();
            nextSnapshotTime = Time.time + (1f / snapshotRate);
        }

        // Remove old snapshots
        while (snapshotHistory.Count > 0 &&
               Time.time - snapshotHistory.Peek().timestamp > maxHistoryTime)
        {
            snapshotHistory.Dequeue();
        }
    }

    void TakeSnapshot()
    {
        Snapshot snapshot = new Snapshot
        {
            timestamp = Time.time,
            entityStates = new Dictionary<int, TransformState>()
        };

        // Capture all networked entities
        foreach (var entity in FindObjectsOfType<NetworkIdentity>())
        {
            snapshot.entityStates[entity.netId] = new TransformState
            {
                position = entity.transform.position,
                rotation = entity.transform.rotation
            };
        }

        snapshotHistory.Enqueue(snapshot);
    }

    public void PerformLagCompensatedRaycast(
        float clientTime,
        Vector3 origin,
        Vector3 direction,
        float maxDistance,
        out RaycastHit hit)
    {
        // Find snapshot closest to client's time
        Snapshot targetSnapshot = FindSnapshotAtTime(clientTime);

        // Temporarily move entities to their historical positions
        Dictionary<int, TransformState> currentStates = new Dictionary<int, TransformState>();

        foreach (var kvp in targetSnapshot.entityStates)
        {
            NetworkIdentity entity = NetworkServer.spawned[kvp.Key];

            // Save current state
            currentStates[kvp.Key] = new TransformState
            {
                position = entity.transform.position,
                rotation = entity.transform.rotation
            };

            // Rewind to historical state
            entity.transform.position = kvp.Value.position;
            entity.transform.rotation = kvp.Value.rotation;
        }

        // Perform raycast in rewound state
        bool hitSomething = Physics.Raycast(origin, direction, out hit, maxDistance);

        // Restore current states
        foreach (var kvp in currentStates)
        {
            NetworkIdentity entity = NetworkServer.spawned[kvp.Key];
            entity.transform.position = kvp.Value.position;
            entity.transform.rotation = kvp.Value.rotation;
        }
    }

    Snapshot FindSnapshotAtTime(float targetTime)
    {
        Snapshot closest = snapshotHistory.ElementAt(0);
        float minDelta = Mathf.Abs(targetTime - closest.timestamp);

        foreach (var snapshot in snapshotHistory)
        {
            float delta = Mathf.Abs(targetTime - snapshot.timestamp);
            if (delta < minDelta)
            {
                minDelta = delta;
                closest = snapshot;
            }
        }

        return closest;
    }
}

// Usage in weapon system
public class HitscanWeapon : NetworkBehaviour
{
    [Command]
    void CmdFire(float clientTime, Vector3 origin, Vector3 direction)
    {
        LagCompensationManager lagComp = FindObjectOfType<LagCompensationManager>();

        lagComp.PerformLagCompensatedRaycast(
            clientTime,
            origin,
            direction,
            100f,
            out RaycastHit hit
        );

        if (hit.collider != null)
        {
            // Process hit
            if (hit.collider.TryGetComponent<Health>(out var health))
            {
                health.TakeDamage(damage);
            }
        }
    }
}
```

**Benefits**:
- ✅ Fair gameplay despite latency
- ✅ "What you see is what you hit"
- ✅ Better player experience

**Drawbacks**:
- ❌ Complex implementation
- ❌ Memory cost for snapshot history
- ❌ Can feel unfair to victim (hit behind cover)

**Reference**:
- Valve: "Source Multiplayer Networking" (lag compensation section)
- "Fast-Paced Multiplayer" - Gabriel Gambetta

---

### 6. Interest Management

**Problem**: Sending all entity updates to all clients wastes bandwidth

**Solution**: Only send updates for entities near/relevant to each player

**When to Use**:
- Large worlds (MMOs, battle royale)
- Many concurrent players
- Bandwidth optimization

**Implementation**:

```csharp
public class InterestManagementSystem : NetworkBehaviour
{
    [SerializeField] private float relevanceRange = 50f;
    [SerializeField] private float updateFrequency = 10f;  // Updates per second

    private float nextUpdateTime = 0f;

    void Update()
    {
        if (!NetworkServer.active) return;

        if (Time.time >= nextUpdateTime)
        {
            UpdateInterestForAllConnections();
            nextUpdateTime = Time.time + (1f / updateFrequency);
        }
    }

    void UpdateInterestForAllConnections()
    {
        foreach (NetworkConnection conn in NetworkServer.connections.Values)
        {
            if (conn.identity == null) continue;

            UpdateInterestForConnection(conn);
        }
    }

    void UpdateInterestForConnection(NetworkConnection conn)
    {
        Vector3 observerPosition = conn.identity.transform.position;

        foreach (NetworkIdentity identity in NetworkServer.spawned.Values)
        {
            if (identity == conn.identity) continue;  // Don't check self

            float distance = Vector3.Distance(observerPosition, identity.transform.position);

            if (distance <= relevanceRange)
            {
                // In range - ensure spawned for this connection
                if (!identity.observers.ContainsKey(conn.connectionId))
                {
                    identity.AddObserver(conn);
                }
            }
            else
            {
                // Out of range - remove if observing
                if (identity.observers.ContainsKey(conn.connectionId))
                {
                    identity.RemoveObserver(conn);
                }
            }
        }
    }
}
```

**Benefits**:
- ✅ Reduced bandwidth per client
- ✅ Better scalability
- ✅ Improved performance

**Drawbacks**:
- ❌ Entities can "pop in"
- ❌ More complex to implement
- ❌ Needs tuning per game

---

### 7. Delta Compression

**Problem**: Sending full state every update wastes bandwidth

**Solution**: Only send what changed

**Implementation**:

```csharp
public class DeltaCompression : NetworkBehaviour
{
    private struct NetworkState
    {
        public Vector3 position;
        public Quaternion rotation;
        public int health;
        public int ammo;
    }

    private NetworkState lastSentState;

    [Server]
    void SendStateUpdate()
    {
        NetworkState currentState = new NetworkState
        {
            position = transform.position,
            rotation = transform.rotation,
            health = GetComponent<Health>().CurrentHealth,
            ammo = GetComponent<Weapon>().CurrentAmmo
        };

        // Build delta
        NetworkWriter writer = new NetworkWriter();

        // Use bit flags to indicate what changed
        byte changeFlags = 0;

        if (Vector3.Distance(currentState.position, lastSentState.position) > 0.01f)
            changeFlags |= (1 << 0);  // Position changed

        if (Quaternion.Angle(currentState.rotation, lastSentState.rotation) > 0.5f)
            changeFlags |= (1 << 1);  // Rotation changed

        if (currentState.health != lastSentState.health)
            changeFlags |= (1 << 2);  // Health changed

        if (currentState.ammo != lastSentState.ammo)
            changeFlags |= (1 << 3);  // Ammo changed

        writer.WriteByte(changeFlags);

        // Only write changed values
        if ((changeFlags & (1 << 0)) != 0)
            writer.WriteVector3(currentState.position);

        if ((changeFlags & (1 << 1)) != 0)
            writer.WriteQuaternion(currentState.rotation);

        if ((changeFlags & (1 << 2)) != 0)
            writer.WriteInt(currentState.health);

        if ((changeFlags & (1 << 3)) != 0)
            writer.WriteInt(currentState.ammo);

        // Send to clients
        RpcReceiveStateDelta(writer.ToArray());

        lastSentState = currentState;
    }

    [ClientRpc]
    void RpcReceiveStateDelta(byte[] delta)
    {
        NetworkReader reader = new NetworkReader(delta);
        byte changeFlags = reader.ReadByte();

        if ((changeFlags & (1 << 0)) != 0)
            transform.position = reader.ReadVector3();

        if ((changeFlags & (1 << 1)) != 0)
            transform.rotation = reader.ReadQuaternion();

        if ((changeFlags & (1 << 2)) != 0)
            GetComponent<Health>().CurrentHealth = reader.ReadInt();

        if ((changeFlags & (1 << 3)) != 0)
            GetComponent<Weapon>().CurrentAmmo = reader.ReadInt();
    }
}
```

**Benefits**:
- ✅ Significantly reduced bandwidth
- ✅ More players per server
- ✅ Better mobile performance

**Drawbacks**:
- ❌ More complex implementation
- ❌ Can't reconstruct state from single packet (need full state periodically)

---

## Advanced Patterns

### 8. Snapshot Compression
Use quantization and encoding to reduce snapshot size

### 9. Rollback Netcode (for Fighting Games)
Deterministic simulation with input delay reduction

### 10. Hybrid P2P/Client-Server
P2P for gameplay, server for matchmaking/validation

---

## Best Practices

### Tick Rate Guidelines
- **Competitive FPS**: 60-128 ticks/second
- **MOBA/RPG**: 20-30 ticks/second
- **Battle Royale**: 20-60 ticks/second (varies by player count)

### Bandwidth Budgets
- **Per Client**: 50-200 Kbps typical
- **Mobile**: 30-100 Kbps
- **Console/PC**: 100-300 Kbps

### Latency Thresholds
- **< 50ms**: Excellent (feels local)
- **50-100ms**: Good (playable for most genres)
- **100-150ms**: Acceptable (noticeable but okay)
- **> 150ms**: Poor (frustrating experience)

---

## Testing & Debugging

### Network Simulation
```csharp
// Simulate network conditions for testing
public class NetworkSimulator : MonoBehaviour
{
    [Header("Latency")]
    [Range(0, 500)] public int latencyMs = 50;
    [Range(0, 100)] public int jitterMs = 10;

    [Header("Packet Loss")]
    [Range(0, 50)] public float packetLoss = 0;  // Percentage

    [Header("Bandwidth")]
    public int maxKbps = 100;

    // Apply to outgoing packets
    public IEnumerator SimulatePacket(byte[] data, Action<byte[]> onReceive)
    {
        // Simulate packet loss
        if (Random.value < (packetLoss / 100f))
            yield break;  // Packet dropped

        // Simulate latency + jitter
        float delay = (latencyMs + Random.Range(-jitterMs, jitterMs)) / 1000f;
        yield return new WaitForSeconds(delay);

        onReceive(data);
    }
}
```

---

## References

- **Gaffer on Games**: https://gafferongames.com (entire networking series)
- **Gabriel Gambetta**: "Fast-Paced Multiplayer" (client prediction, reconciliation)
- **Valve**: "Source Multiplayer Networking" (lag compensation, interpolation)
- **GDC Talks**:
  - "Overwatch Gameplay Architecture and Netcode"
  - "Networking for Physics Programmers"
  - "I Shot You First: Networking the Gameplay of HALO: REACH"

---

**Version**: 1.0
**Last Updated**: 2025-11-19
