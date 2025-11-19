# Optimizing Unity Performance - Complete Guide

## Profiling First

**Rule #1**: Always profile before optimizing

### Unity Profiler
- Window → Analysis → Profiler
- **CPU Usage**: Identify expensive methods
- **GPU Usage**: Rendering bottlenecks
- **Memory**: Allocations and GC spikes
- **Rendering**: Draw calls, batches, vertices

### Deep Profiling
```csharp
Profiler.BeginSample("MyExpensiveOperation");
// Code to profile
Profiler.EndSample();
```

## CPU Optimization

### 1. Avoid GetComponent in Update

❌ **Bad**:
```csharp
void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}
```

✅ **Good**:
```csharp
private Rigidbody rb;

void Awake()
{
    rb = GetComponent<Rigidbody>();
}

void Update()
{
    rb.AddForce(Vector3.up);
}
```

### 2. Object Pooling

❌ **Bad** (spawns 100 bullets/sec):
```csharp
void Shoot()
{
    Instantiate(bulletPrefab);
}
```

✅ **Good**:
```csharp
ObjectPool<Bullet> bulletPool;

void Awake()
{
    bulletPool = new ObjectPool<Bullet>(bulletPrefab, 50);
}

void Shoot()
{
    Bullet bullet = bulletPool.Get();
}
```

**Impact**: 50ms → 0.5ms per 100 spawns

### 3. Reduce Allocations

❌ **Bad** (allocates every frame):
```csharp
void Update()
{
    string text = "Score: " + score; // String allocation
    List<Enemy> enemies = new List<Enemy>(); // List allocation
}
```

✅ **Good**:
```csharp
private List<Enemy> enemyList = new List<Enemy>();
private StringBuilder scoreText = new StringBuilder();

void Update()
{
    scoreText.Clear();
    scoreText.Append("Score: ").Append(score);

    enemyList.Clear();
    // Reuse list
}
```

### 4. Use CompareTag

❌ **Bad**:
```csharp
if (other.tag == "Player") // String allocation
```

✅ **Good**:
```csharp
if (other.CompareTag("Player")) // No allocation
```

### 5. Camera.main Caching

❌ **Bad**:
```csharp
void Update()
{
    Camera.main.transform.position; // FindGameObjectsWithTag every time
}
```

✅ **Good**:
```csharp
private Camera mainCamera;

void Awake()
{
    mainCamera = Camera.main;
}

void Update()
{
    mainCamera.transform.position;
}
```

### 6. Use Jobs System

```csharp
[BurstCompile]
public struct ParallelUpdateJob : IJobParallelFor
{
    public NativeArray<float3> Positions;
    [ReadOnly] public NativeArray<float3> Velocities;
    public float DeltaTime;

    public void Execute(int index)
    {
        Positions[index] += Velocities[index] * DeltaTime;
    }
}

// 1000 entities: 5ms → 0.2ms
```

## GPU Optimization

### 1. Reduce Draw Calls

**Target**: < 1000 draw calls for mobile, < 3000 for PC

#### Static Batching
```csharp
// Mark static objects in Inspector
// Or via code:
gameObject.isStatic = true;
```

#### Dynamic Batching
- Meshes < 300 vertices
- Same material
- No shadows (for mobile)

#### GPU Instancing
```csharp
// Enable on material
material.enableInstancing = true;

// Use Graphics.DrawMeshInstanced
Matrix4x4[] matrices = new Matrix4x4[1000];
Graphics.DrawMeshInstanced(mesh, 0, material, matrices);
```

**Impact**: 1000 draw calls → 1 draw call

### 2. Texture Atlasing

❌ **Bad**: 50 materials with different textures = 50 draw calls

✅ **Good**: 1 atlas texture = 1 draw call

### 3. Level of Detail (LOD)

```csharp
LODGroup lodGroup = gameObject.AddComponent<LODGroup>();

LOD[] lods = new LOD[3];
lods[0] = new LOD(0.6f, highPolyRenderers); // 60% screen height
lods[1] = new LOD(0.3f, mediumPolyRenderers); // 30%
lods[2] = new LOD(0.1f, lowPolyRenderers); // 10%

lodGroup.SetLODs(lods);
```

### 4. Occlusion Culling

- Window → Rendering → Occlusion Culling
- Bake occlusion data
- **Impact**: Only render visible objects

### 5. Shader Optimization

❌ **Bad** (complex shader):
```hlsl
float4 frag() : SV_Target
{
    for (int i = 0; i < 100; i++) {
        // Expensive loop
    }
}
```

✅ **Good**:
- Use LOD shaders
- Mobile: < 50 shader instructions
- Avoid complex math in fragment shader

## Memory Optimization

### 1. Texture Compression

```csharp
// Mobile: ASTC, ETC2
// PC: DXT5, BC7
// Set max size appropriately (1024, 512, etc.)
```

**Impact**: 4MB → 0.5MB per texture

### 2. Mesh Compression

Inspector → Mesh Compression: High

### 3. Audio Compression

- Music: Vorbis, streaming
- SFX: ADPCM, decompress on load
- Voice: Vorbis

### 4. Addressables

```csharp
// Load only when needed
AsyncOperationHandle<GameObject> handle =
    Addressables.LoadAssetAsync<GameObject>("Enemy");
await handle.Task;

// Unload when done
Addressables.Release(handle);
```

### 5. Resources.UnloadUnusedAssets

```csharp
async void UnloadUnusedAssets()
{
    await Resources.UnloadUnusedAssets();
    GC.Collect();
}
```

## Physics Optimization

### 1. Use Layers for Collision

```csharp
// Physics settings → Layer Collision Matrix
// Disable unnecessary collision checks
```

### 2. Fixed Timestep

```csharp
// Edit → Project Settings → Time
// Fixed Timestep: 0.02 (50Hz) or 0.0166 (60Hz)
```

### 3. Collision Detection

- **Discrete**: Fast, can tunnel
- **Continuous**: Slower, prevents tunneling (fast objects)
- **Continuous Speculative**: Best for character controllers

### 4. Reduce Active Rigidbodies

```csharp
// Sleep threshold
rigidbody.sleepThreshold = 0.1f;

// Manually sleep
rigidbody.Sleep();
```

## Mobile-Specific

### 1. Reduce Resolution

```csharp
Screen.SetResolution(Screen.width / 2, Screen.height / 2, true);
```

### 2. Use URP (Universal Render Pipeline)

- Better mobile performance
- Shader stripping
- Single-pass rendering

### 3. Limit Post-Processing

- Bloom, SSAO, etc. are expensive
- Use baked lighting

### 4. Optimize UI

```csharp
// Disable raycasting when UI hidden
canvasGroup.blocksRaycasts = false;

// Use Canvas groups for batch enable/disable
```

## Performance Budgets

### Target: 60 FPS (16.67ms per frame)

- **CPU Game Logic**: 8-10ms
- **Rendering**: 4-6ms
- **Physics**: 1-2ms
- **Audio**: 0.5-1ms
- **Other**: 1-2ms

### Mobile: 30-60 FPS
- **Draw Calls**: < 500
- **Triangles**: < 100k visible
- **Texture Memory**: < 200MB
- **Audio Voices**: < 32

### PC: 60+ FPS
- **Draw Calls**: < 3000
- **Triangles**: < 1M visible
- **Texture Memory**: < 2GB

## Profiling Checklist

✅ Profile on target device (not editor)
✅ Test in release build (not debug)
✅ Monitor over extended gameplay session
✅ Check for memory leaks
✅ Verify GC spikes
✅ Test worst-case scenarios

## Common Bottlenecks

1. **Too many draw calls** → Batching, atlasing
2. **GC spikes** → Reduce allocations, object pooling
3. **Physics** → Reduce active rigidbodies, optimize layers
4. **Overdraw** → Reduce transparent objects, optimize UI
5. **Expensive shaders** → LOD shaders, simplify

## Tools

- **Unity Profiler**: CPU, GPU, Memory
- **Frame Debugger**: Draw call analysis
- **Memory Profiler Package**: Detailed memory inspection
- **Device Simulator**: Test different devices
- **Instruments (iOS)**: Apple's profiler
- **Android Studio Profiler**: Android profiling

## References

- Unity "Best Practice Guides"
- "Optimizing Unity Games" - Unity Technologies
- Unity Learn: Performance Optimization
