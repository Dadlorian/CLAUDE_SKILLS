# Authoritative Server Implementation Guide

## Overview

Server-authoritative architecture is the gold standard for multiplayer games, especially competitive ones. The server maintains the "source of truth" for game state, validates all client actions, and prevents cheating. This guide covers practical implementation patterns for production-ready authoritative servers.

## Core Architecture

### The Golden Rule

**Clients request, servers decide, all clients observe.**

```
Client: "I want to move to (10, 5)"
Server: "Validated. You are now at (10, 5)"
Everyone: Observes the new state
```

Never trust the client. Ever.

### Three-Layer Model

```
┌─────────────────┐
│  Client Layer   │ ← Prediction, rendering, input collection
├─────────────────┤
│  Network Layer  │ ← Serialization, compression, transport
├─────────────────┤
│  Server Layer   │ ← Validation, simulation, authority
└─────────────────┘
```

Each layer has distinct responsibilities:
- **Client**: Optimistic UI, immediate feedback, render smooth motion
- **Network**: Reliable delivery, bandwidth optimization, latency hiding
- **Server**: Game rules, physics, validation, anti-cheat

## Server Implementation

### Game Server Loop

```csharp
public class GameServer
{
    private const float TICK_RATE = 60.0f; // 60 Hz
    private const float TICK_INTERVAL = 1.0f / TICK_RATE;

    private GameState state;
    private List<ConnectedClient> clients;
    private Queue<ClientInput> inputQueue;

    public void Run()
    {
        float accumulator = 0.0f;
        DateTime lastTime = DateTime.Now;

        while (running)
        {
            DateTime currentTime = DateTime.Now;
            float deltaTime = (float)(currentTime - lastTime).TotalSeconds;
            lastTime = currentTime;

            accumulator += deltaTime;

            // Fixed timestep updates
            while (accumulator >= TICK_INTERVAL)
            {
                ProcessInputs();      // Handle client commands
                UpdateGameState();    // Simulate physics, AI, etc.
                BroadcastState();     // Send updates to clients

                accumulator -= TICK_INTERVAL;
            }

            // Prevent spiral of death
            if (accumulator > TICK_INTERVAL * 5)
                accumulator = TICK_INTERVAL;

            Thread.Sleep(1); // Don't hog CPU
        }
    }
}
```

**Key Principles**:
- **Fixed timestep**: Deterministic simulation requires consistent timing
- **Accumulator pattern**: Catch up if server lags, but cap to prevent death spiral
- **Process-Update-Broadcast**: Clear separation of concerns

### Input Processing

```csharp
public void ProcessInputs()
{
    while (inputQueue.Count > 0)
    {
        ClientInput input = inputQueue.Dequeue();

        // 1. Get player entity
        PlayerEntity player = GetPlayer(input.ClientId);
        if (player == null) continue;

        // 2. Validate input
        if (!ValidateInput(player, input))
        {
            LogCheatAttempt(input.ClientId, input);
            continue;
        }

        // 3. Apply input to game state
        ApplyInput(player, input);

        // 4. Record for reconciliation
        RecordProcessedInput(input);
    }
}

private bool ValidateInput(PlayerEntity player, ClientInput input)
{
    // Check timing
    if (input.Timestamp < player.LastInputTime)
        return false; // Out-of-order input

    // Check action validity
    if (input.Action == ActionType.Jump && !player.IsGrounded)
        return false; // Can't jump in air

    // Check movement bounds
    float maxSpeed = player.GetMaxSpeed();
    if (input.Movement.magnitude > maxSpeed * 1.1f) // 10% tolerance
        return false; // Speed hacking attempt

    // Check cooldowns
    if (input.Action == ActionType.Shoot && player.WeaponOnCooldown())
        return false; // Shooting too fast

    return true;
}
```

**Validation Checklist**:
- [ ] Input timestamp is sequential
- [ ] Action is legal in current state
- [ ] Movement doesn't exceed physical limits
- [ ] Cooldowns are respected
- [ ] Resources are available (mana, ammo)
- [ ] Target is in range (for targeted actions)

### State Management

```csharp
public class GameState
{
    // World state
    public Dictionary<int, PlayerEntity> Players;
    public Dictionary<int, WorldEntity> Entities;
    public int CurrentTick;

    // History for lag compensation
    private CircularBuffer<GameStateSnapshot> history;
    private const int HISTORY_SIZE = 256; // ~4 seconds at 60Hz

    public GameState()
    {
        Players = new Dictionary<int, PlayerEntity>();
        Entities = new Dictionary<int, WorldEntity>();
        history = new CircularBuffer<GameStateSnapshot>(HISTORY_SIZE);
    }

    public void Update(float deltaTime)
    {
        // Physics simulation
        foreach (var entity in Entities.Values)
        {
            entity.Update(deltaTime);
        }

        // Collision detection
        DetectCollisions();

        // Game rules
        ProcessGameLogic();

        // Save snapshot for lag compensation
        SaveSnapshot();

        CurrentTick++;
    }

    private void SaveSnapshot()
    {
        var snapshot = new GameStateSnapshot
        {
            Tick = CurrentTick,
            Timestamp = DateTime.Now,
            Entities = CloneEntities()
        };

        history.Add(snapshot);
    }

    public GameStateSnapshot GetHistoricalState(int ticksAgo)
    {
        int targetTick = CurrentTick - ticksAgo;
        return history.Find(s => s.Tick == targetTick);
    }
}
```

**State Management Patterns**:
- **Snapshot System**: Save historical states for lag compensation
- **Circular Buffer**: Fixed memory, O(1) lookups
- **Delta Tracking**: Track what changed each tick for efficient sync

### Broadcasting Updates

```csharp
public void BroadcastState()
{
    foreach (var client in clients)
    {
        // Get entities relevant to this client
        var relevantEntities = GetRelevantEntities(client);

        // Create update packet
        var update = new StateUpdate
        {
            Tick = state.CurrentTick,
            Entities = new List<EntityUpdate>()
        };

        foreach (var entity in relevantEntities)
        {
            // Delta compression: only send changes
            var lastState = client.GetLastSentState(entity.Id);
            var delta = ComputeDelta(lastState, entity);

            if (delta.HasChanges)
            {
                update.Entities.Add(delta);
                client.UpdateLastSentState(entity.Id, entity);
            }
        }

        // Send only if there are changes
        if (update.Entities.Count > 0)
        {
            client.Send(update);
        }
    }
}

private List<Entity> GetRelevantEntities(ConnectedClient client)
{
    var playerPos = client.Player.Position;
    var radius = 1000.0f; // Visibility radius

    return SpatialGrid.Query(playerPos, radius);
}

private EntityDelta ComputeDelta(EntityState last, Entity current)
{
    var delta = new EntityDelta { Id = current.Id };

    if (last.Position != current.Position)
    {
        delta.Position = current.Position;
        delta.Flags |= DeltaFlags.Position;
    }

    if (last.Health != current.Health)
    {
        delta.Health = current.Health;
        delta.Flags |= DeltaFlags.Health;
    }

    // ... other fields

    return delta;
}
```

**Broadcast Optimizations**:
- **Relevancy filtering**: Only send nearby entities
- **Delta compression**: Only send changed fields
- **Priority system**: Critical updates sent first
- **Update frequency**: Vary rate by distance/importance

## Client Implementation

### Client Prediction

```csharp
public class ClientGameState
{
    private LocalPlayer localPlayer;
    private Dictionary<int, RemotePlayer> remotePlayers;

    // Input history for reconciliation
    private Queue<PendingInput> pendingInputs;
    private int lastAcknowledgedInput;

    public void OnPlayerInput(InputState input)
    {
        // 1. Apply input locally (prediction)
        ApplyInput(localPlayer, input);

        // 2. Store for reconciliation
        var pending = new PendingInput
        {
            SequenceNumber = GetNextSequence(),
            Input = input,
            PredictedState = localPlayer.Clone()
        };
        pendingInputs.Enqueue(pending);

        // 3. Send to server
        SendInputToServer(input, pending.SequenceNumber);
    }

    public void OnServerStateUpdate(StateUpdate update)
    {
        // 1. Update acknowledged input
        lastAcknowledgedInput = update.LastProcessedInput;

        // 2. Remove acknowledged inputs
        while (pendingInputs.Count > 0 &&
               pendingInputs.Peek().SequenceNumber <= lastAcknowledgedInput)
        {
            pendingInputs.Dequeue();
        }

        // 3. Apply server state
        localPlayer.Position = update.YourPosition;
        localPlayer.Velocity = update.YourVelocity;

        // 4. Reconcile: Re-apply unacknowledged inputs
        var savedState = localPlayer.Clone();

        foreach (var pending in pendingInputs)
        {
            ApplyInput(localPlayer, pending.Input);
        }

        // 5. Check for misprediction
        if (Vector3.Distance(savedState.Position, localPlayer.Position) > 0.1f)
        {
            // Prediction was wrong, snap to corrected position
            Debug.Log("Misprediction corrected");
        }
    }

    private void ApplyInput(PlayerEntity player, InputState input)
    {
        // Same logic as server (deterministic)
        Vector3 movement = input.Movement * player.Speed * Time.deltaTime;
        player.Position += movement;

        if (input.Jump && player.IsGrounded)
        {
            player.Velocity.y = player.JumpForce;
        }
    }
}
```

**Prediction Requirements**:
- **Determinism**: Client and server must produce same result for same input
- **History**: Keep unacknowledged inputs for replay
- **Reconciliation**: Correct mispredictions smoothly

### Entity Interpolation

```csharp
public class RemotePlayer
{
    private Vector3 currentPosition;
    private Vector3 targetPosition;
    private float interpolationTime;

    private Queue<PositionSnapshot> snapshots;
    private const float INTERPOLATION_DELAY = 0.1f; // 100ms

    public void OnServerUpdate(Vector3 newPosition, float timestamp)
    {
        snapshots.Enqueue(new PositionSnapshot
        {
            Position = newPosition,
            Timestamp = timestamp
        });

        // Keep only recent snapshots
        while (snapshots.Count > 10)
            snapshots.Dequeue();
    }

    public void Update()
    {
        float renderTime = Time.time - INTERPOLATION_DELAY;

        // Find snapshots to interpolate between
        PositionSnapshot from = null;
        PositionSnapshot to = null;

        foreach (var snapshot in snapshots)
        {
            if (snapshot.Timestamp <= renderTime)
                from = snapshot;
            else
            {
                to = snapshot;
                break;
            }
        }

        if (from != null && to != null)
        {
            // Interpolate
            float duration = to.Timestamp - from.Timestamp;
            float t = (renderTime - from.Timestamp) / duration;

            currentPosition = Vector3.Lerp(from.Position, to.Position, t);
        }
        else if (to != null)
        {
            currentPosition = to.Position;
        }

        // Render at interpolated position
        transform.position = currentPosition;
    }
}
```

**Interpolation Strategies**:
- **Delay buffer**: Render slightly in the past (100ms) for smooth interpolation
- **Linear interpolation**: Simple, works for most cases
- **Cubic interpolation**: Smoother curves for important entities
- **Extrapolation**: Predict future (risky, can snap when wrong)

## Lag Compensation

### Time Rewinding for Hitscan

```csharp
public class LagCompensationSystem
{
    public bool ProcessHitscanShot(PlayerEntity shooter, Vector3 direction, int clientTimestamp)
    {
        // 1. Calculate player's latency
        int latency = GetPlayerLatency(shooter.ClientId);

        // 2. Rewind world to when player fired on their screen
        int ticksAgo = latency / TICK_INTERVAL_MS;
        GameStateSnapshot historicalState = state.GetHistoricalState(ticksAgo);

        if (historicalState == null)
        {
            // Too much lag, use current state
            historicalState = state.GetCurrentSnapshot();
        }

        // 3. Perform raycast in historical state
        RaycastHit hit;
        if (Physics.Raycast(shooter.Position, direction, out hit,
                           maxRange: 100f, state: historicalState))
        {
            // 4. Hit detected! Apply damage in current state
            var target = state.GetEntity(hit.EntityId);
            if (target != null)
            {
                target.TakeDamage(shooter.WeaponDamage);
                return true;
            }
        }

        return false;
    }
}
```

**Lag Compensation Fairness**:
- **Pro**: Shooter sees what they shoot (feels responsive)
- **Con**: Target might feel hit "around corners"
- **Balance**: Limit compensation to reasonable latency (<200ms)

### Projectile Lag Compensation

```csharp
public class ProjectileSystem
{
    public void FireProjectile(PlayerEntity shooter, Vector3 direction)
    {
        // 1. Create projectile on server
        var projectile = new Projectile
        {
            Position = shooter.Position + shooter.Forward * 2f,
            Velocity = direction * projectileSpeed,
            Owner = shooter.Id,
            Timestamp = state.CurrentTick
        };

        state.AddEntity(projectile);

        // 2. Broadcast to all clients
        BroadcastProjectileSpawn(projectile);
    }

    public void UpdateProjectiles(float deltaTime)
    {
        foreach (var projectile in state.GetProjectiles())
        {
            // Move projectile
            projectile.Position += projectile.Velocity * deltaTime;

            // Check collisions
            var hits = Physics.OverlapSphere(projectile.Position, projectile.Radius);

            foreach (var hit in hits)
            {
                if (hit.EntityId != projectile.Owner)
                {
                    // Hit something!
                    OnProjectileHit(projectile, hit);
                    state.RemoveEntity(projectile.Id);
                    break;
                }
            }

            // Check lifetime
            if (projectile.Age > maxLifetime)
            {
                state.RemoveEntity(projectile.Id);
            }
        }
    }
}
```

**Projectile Considerations**:
- **Server-authoritative**: Server simulates projectile movement
- **Client prediction**: Client shows projectile immediately
- **Reconciliation**: Correct if server disagrees with hit

## Performance Optimization

### Spatial Partitioning

```csharp
public class SpatialGrid
{
    private Dictionary<Vector2Int, List<Entity>> grid;
    private int cellSize = 100; // 100 units per cell

    public void Insert(Entity entity)
    {
        var cell = GetCell(entity.Position);

        if (!grid.ContainsKey(cell))
            grid[cell] = new List<Entity>();

        grid[cell].Add(entity);
        entity.GridCell = cell;
    }

    public List<Entity> Query(Vector3 position, float radius)
    {
        var results = new List<Entity>();
        var center = GetCell(position);

        int cellRadius = Mathf.CeilToInt(radius / cellSize);

        // Check surrounding cells
        for (int x = -cellRadius; x <= cellRadius; x++)
        {
            for (int y = -cellRadius; y <= cellRadius; y++)
            {
                var cell = new Vector2Int(center.x + x, center.y + y);

                if (grid.TryGetValue(cell, out var entities))
                {
                    foreach (var entity in entities)
                    {
                        if (Vector3.Distance(position, entity.Position) <= radius)
                        {
                            results.Add(entity);
                        }
                    }
                }
            }
        }

        return results;
    }

    private Vector2Int GetCell(Vector3 position)
    {
        return new Vector2Int(
            Mathf.FloorToInt(position.x / cellSize),
            Mathf.FloorToInt(position.z / cellSize)
        );
    }
}
```

**Performance Wins**:
- **O(n²) → O(n)**: Only check entities in nearby cells
- **Scalability**: Handles 10,000+ entities efficiently
- **Memory**: Trade memory for speed (worth it)

### Bandwidth Optimization

```csharp
public class PacketSerializer
{
    public byte[] SerializeEntityUpdate(EntityDelta delta)
    {
        using (var stream = new MemoryStream())
        using (var writer = new BinaryWriter(stream))
        {
            // Write header
            writer.Write(delta.EntityId);
            writer.Write((byte)delta.Flags);

            // Write only changed fields
            if ((delta.Flags & DeltaFlags.Position) != 0)
            {
                // Quantize position to reduce size
                writer.Write(QuantizePosition(delta.Position));
            }

            if ((delta.Flags & DeltaFlags.Health) != 0)
            {
                // Health as byte (0-255)
                writer.Write((byte)(delta.Health * 255f));
            }

            if ((delta.Flags & DeltaFlags.Rotation) != 0)
            {
                // Rotation as quaternion compressed to 32 bits
                writer.Write(CompressQuaternion(delta.Rotation));
            }

            return stream.ToArray();
        }
    }

    private uint QuantizePosition(Vector3 pos)
    {
        // Encode 3D position in 30 bits (10 bits per axis)
        // Range: -512 to 512 with 0.1 precision

        int x = Mathf.Clamp((int)(pos.x * 10f), -512, 511);
        int y = Mathf.Clamp((int)(pos.y * 10f), -512, 511);
        int z = Mathf.Clamp((int)(pos.z * 10f), -512, 511);

        uint packed = 0;
        packed |= (uint)(x & 0x3FF) << 20;
        packed |= (uint)(y & 0x3FF) << 10;
        packed |= (uint)(z & 0x3FF);

        return packed;
    }

    private uint CompressQuaternion(Quaternion q)
    {
        // Smallest-three compression
        // Find largest component, encode others

        int maxIndex = 0;
        float maxValue = Mathf.Abs(q.x);

        if (Mathf.Abs(q.y) > maxValue)
        {
            maxIndex = 1;
            maxValue = Mathf.Abs(q.y);
        }
        if (Mathf.Abs(q.z) > maxValue)
        {
            maxIndex = 2;
            maxValue = Mathf.Abs(q.z);
        }
        if (Mathf.Abs(q.w) > maxValue)
        {
            maxIndex = 3;
        }

        // Encode 3 components (10 bits each) + 2 bit index
        // Total: 32 bits instead of 128 bits (4x savings)

        uint packed = (uint)maxIndex << 30;
        // ... encode other three components

        return packed;
    }
}
```

**Compression Techniques**:
- **Quantization**: Reduce precision (position from 96 to 30 bits)
- **Delta encoding**: Send changes only
- **Bit packing**: Multiple values per byte
- **Quaternion compression**: 128 → 32 bits

## Testing Strategies

### Network Simulation

```csharp
public class NetworkSimulator
{
    public float latency = 100f; // ms
    public float jitter = 20f;   // ms variance
    public float packetLoss = 0.05f; // 5%

    private Queue<DelayedPacket> outgoingPackets;

    public void SendPacket(byte[] data, Action<byte[]> onReceive)
    {
        // Simulate packet loss
        if (Random.value < packetLoss)
        {
            Debug.Log("Packet lost");
            return;
        }

        // Simulate latency + jitter
        float delay = latency + Random.Range(-jitter, jitter);

        outgoingPackets.Enqueue(new DelayedPacket
        {
            Data = data,
            DeliveryTime = Time.time + delay / 1000f,
            Callback = onReceive
        });
    }

    public void Update()
    {
        while (outgoingPackets.Count > 0 &&
               outgoingPackets.Peek().DeliveryTime <= Time.time)
        {
            var packet = outgoingPackets.Dequeue();
            packet.Callback(packet.Data);
        }
    }
}
```

### Automated Testing

```csharp
[Test]
public void TestMovementPrediction()
{
    // Setup
    var client = new ClientGameState();
    var server = new GameServer();

    // Client sends input
    var input = new InputState { Movement = Vector3.forward };
    client.OnPlayerInput(input);

    // Simulate network delay
    Thread.Sleep(100);

    // Server processes
    server.ProcessInput(input);
    var serverState = server.GetPlayerState(client.PlayerId);

    // Server responds
    Thread.Sleep(100);
    client.OnServerStateUpdate(serverState);

    // Assert: Client and server positions match
    Assert.AreEqual(serverState.Position, client.LocalPlayer.Position, 0.1f);
}
```

## Common Pitfalls

### Pitfall 1: Trusting Client Position

**Wrong**:
```csharp
// Server receives: "I'm at (100, 100)"
player.Position = clientPosition; // NEVER DO THIS
```

**Right**:
```csharp
// Server receives: "I want to move forward"
Vector3 desiredMovement = input.Movement * player.Speed * deltaTime;
Vector3 newPosition = player.Position + desiredMovement;

// Validate
if (IsPositionReachable(player.Position, newPosition))
{
    player.Position = newPosition;
}
```

### Pitfall 2: Not Handling Packet Loss

**Wrong**:
```csharp
// Assume all packets arrive
currentState = latestPacket;
```

**Right**:
```csharp
// Use sequence numbers, handle gaps
if (packet.SequenceNumber > lastReceivedSequence)
{
    lastReceivedSequence = packet.SequenceNumber;
    currentState = packet.State;
}
else
{
    // Out of order, ignore
}
```

### Pitfall 3: Synchronizing Floats Exactly

**Wrong**:
```csharp
if (clientPosition == serverPosition) // Floats rarely equal
```

**Right**:
```csharp
if (Vector3.Distance(clientPosition, serverPosition) < threshold)
```

## Production Checklist

Before shipping multiplayer:

- [ ] Server validates all client inputs
- [ ] Movement speed is capped server-side
- [ ] Cooldowns enforced server-side
- [ ] Damage calculation on server
- [ ] Lag compensation tested (50-200ms)
- [ ] Packet loss handled (1-10%)
- [ ] Bandwidth measured (<200 Kbps per player)
- [ ] Tick rate stable (60 Hz target)
- [ ] Spatial partitioning for 100+ entities
- [ ] Delta compression implemented
- [ ] Interest management (only send relevant entities)
- [ ] Reconnection handling
- [ ] Graceful degradation for high latency
- [ ] Cheating prevention (wallhacks, speedhacks, aimbots)
- [ ] Load testing (1000+ concurrent users)

## Conclusion

Authoritative server architecture requires:
1. **Server authority**: Never trust the client
2. **Client prediction**: Immediate local feedback
3. **Reconciliation**: Correct mispredictions gracefully
4. **Lag compensation**: Fairness for all latencies
5. **Optimization**: Bandwidth and CPU efficiency

The server is the source of truth. Clients are optimistic observers. All interactions flow through validation. This creates fair, responsive, and cheat-resistant multiplayer experiences.
