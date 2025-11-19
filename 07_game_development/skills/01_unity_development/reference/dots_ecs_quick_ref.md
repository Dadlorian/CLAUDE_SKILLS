# Unity DOTS/ECS Quick Reference

## What is DOTS?

Data-Oriented Technology Stack - Unity's high-performance multithreaded programming paradigm.

**Components**:
- **ECS** (Entity Component System) - Architecture
- **Jobs System** - Multithreading
- **Burst Compiler** - Optimized native code

## Core Concepts

### Entities
```csharp
EntityManager entityManager = World.DefaultGameObjectInjectionWorld.EntityManager;

// Create entity
Entity entity = entityManager.CreateEntity();

// Create with archetype
EntityArchetype archetype = entityManager.CreateArchetype(
    typeof(Translation),
    typeof(Rotation),
    typeof(VelocityComponent)
);
Entity entity2 = entityManager.CreateEntity(archetype);
```

### Components (IComponentData)
```csharp
public struct VelocityComponent : IComponentData
{
    public float3 Value;
}

public struct HealthComponent : IComponentData
{
    public int Current;
    public int Maximum;
}

// Add component
entityManager.AddComponentData(entity, new VelocityComponent { Value = new float3(1, 0, 0) });

// Get component
VelocityComponent velocity = entityManager.GetComponentData<VelocityComponent>(entity);

// Set component
entityManager.SetComponentData(entity, new VelocityComponent { Value = float3.zero });
```

### Systems
```csharp
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class MovementSystem : SystemBase
{
    protected override void OnUpdate()
    {
        float deltaTime = Time.DeltaTime;

        Entities.ForEach((ref Translation translation, in VelocityComponent velocity) =>
        {
            translation.Value += velocity.Value * deltaTime;
        }).ScheduleParallel();
    }
}
```

## Jobs System

### IJob (Single-threaded job)
```csharp
public struct MyJob : IJob
{
    public float DeltaTime;
    public NativeArray<float3> Positions;

    public void Execute()
    {
        for (int i = 0; i < Positions.Length; i++)
        {
            Positions[i] += new float3(0, 1, 0) * DeltaTime;
        }
    }
}

// Schedule
MyJob job = new MyJob { DeltaTime = Time.deltaTime, Positions = positions };
JobHandle handle = job.Schedule();
handle.Complete();
```

### IJobParallelFor (Multi-threaded)
```csharp
[BurstCompile]
public struct ParallelMovementJob : IJobParallelFor
{
    public float DeltaTime;
    public NativeArray<float3> Positions;
    [ReadOnly] public NativeArray<float3> Velocities;

    public void Execute(int index)
    {
        Positions[index] += Velocities[index] * DeltaTime;
    }
}

// Schedule
ParallelMovementJob job = new ParallelMovementJob
{
    DeltaTime = Time.deltaTime,
    Positions = positions,
    Velocities = velocities
};
JobHandle handle = job.Schedule(positions.Length, 64); // 64 = batch size
handle.Complete();
```

## Burst Compiler

```csharp
[BurstCompile]
public struct BurstOptimizedJob : IJobParallelFor
{
    public void Execute(int index)
    {
        // Math operations compiled to SIMD instructions
        float result = math.sqrt(index) * math.sin(index);
    }
}
```

**Benefits**:
- 10-100x faster than regular C#
- SIMD optimizations
- No garbage collection

## Common Patterns

### Query Entities
```csharp
EntityQuery query = entityManager.CreateEntityQuery(typeof(Translation), typeof(VelocityComponent));
NativeArray<Entity> entities = query.ToEntityArray(Allocator.Temp);
```

### Singleton Components
```csharp
// Set singleton
entityManager.CreateEntity(typeof(GameSettingsComponent));
SetSingleton(new GameSettingsComponent { Difficulty = 5 });

// Get singleton
GameSettingsComponent settings = GetSingleton<GameSettingsComponent>();
```

### Buffer Components (dynamic arrays)
```csharp
public struct InventoryItem : IBufferElementData
{
    public int ItemID;
    public int Quantity;
}

// Add buffer
DynamicBuffer<InventoryItem> inventory = entityManager.AddBuffer<InventoryItem>(entity);
inventory.Add(new InventoryItem { ItemID = 1, Quantity = 5 });
```

## Performance Tips

✅ Use `[ReadOnly]` on job data that doesn't change
✅ Use `ScheduleParallel()` instead of `Schedule()` when possible
✅ Add `[BurstCompile]` to all jobs
✅ Use `math` library (Unity.Mathematics) instead of `Mathf`
✅ Avoid managed references in components

❌ Don't use `class` types in components (use `struct`)
❌ Don't access entity manager in jobs
❌ Don't allocate memory in jobs (use NativeContainers)

## Memory Management

```csharp
// Always specify allocator
NativeArray<float> array = new NativeArray<float>(100, Allocator.TempJob);

// Dispose when done
array.Dispose();

// Or use dependency system
JobHandle handle = job.Schedule(dependency);
array.Dispose(handle); // Disposes after job completes
```

**Allocator Types**:
- `Temp` - Single frame (fast)
- `TempJob` - 4 frames (for jobs)
- `Persistent` - Manual disposal required

## References

- Unity DOTS documentation
- Unity.Mathematics API
- "Data-Oriented Design" - Richard Fabian
