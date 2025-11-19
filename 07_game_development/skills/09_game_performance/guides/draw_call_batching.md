# Draw Call Batching Guide

## What are Draw Calls?

CPU → GPU: "Draw this mesh with this material"
**Problem**: Each call has overhead
**Target**: Minimize draw calls

## Static Batching

### Unity
```csharp
// Mark static in Inspector
gameObject.isStatic = true;

// Or via code
StaticBatchingUtility.Combine(gameObjects, parentObject);
```

**Requirements**:
- Same material
- Marked static
- Won't move

**Benefits**:
- 1000 objects → 1 draw call
- Minimal CPU overhead

**Drawbacks**:
- Increased memory (combined mesh)
- Objects can't move

## Dynamic Batching

### Unity Auto-Batching
**Requirements**:
- < 300 vertices
- Same material
- Same scale (uniform)
- No shadows (mobile)

**Automatic**: Unity batches at runtime

### GPU Instancing

```csharp
// Enable on material
material.enableInstancing = true;

// Use MaterialPropertyBlock for per-instance data
MaterialPropertyBlock props = new MaterialPropertyBlock();
props.SetColor("_Color", color);
renderer.SetPropertyBlock(props);
```

**Benefits**:
- 1 draw call for many instances
- Can have per-instance properties
- Objects can move

**Use Cases**:
- Grass, trees, rocks
- Particle systems
- Crowds

## SRP Batcher (Unity)

### Setup
```csharp
// Use URP or HDRP
// Ensure materials use same shader
// Enable: Edit → Project Settings → Graphics → SRP Batcher
```

**Benefits**:
- Batches different materials
- Same shader = batched
- Reduces GPU state changes

## Unreal Batching

### Automatic Merging
- Project Settings → Rendering → Optimize Mesh
- Merges static meshes automatically

### Instanced Static Mesh
```cpp
UInstancedStaticMeshComponent* ISM = CreateDefaultSubobject<UInstancedStaticMeshComponent>("ISM");
ISM->SetStaticMesh(TreeMesh);

for (int i = 0; i < 100; i++)
{
    FTransform transform;
    transform.SetLocation(FVector(i * 100, 0, 0));
    ISM->AddInstance(transform);
}
```

## Optimization Strategy

### Texture Atlasing
```
Before: 50 materials (50 textures) = 50 draw calls
After: 1 atlas material (1 texture) = 1 draw call
```

### Mesh Combining
```csharp
CombineInstance[] combine = new CombineInstance[meshes.Length];
for (int i = 0; i < meshes.Length; i++)
{
    combine[i].mesh = meshes[i];
    combine[i].transform = transforms[i].localToWorldMatrix;
}

Mesh combinedMesh = new Mesh();
combinedMesh.CombineMeshes(combine);
GetComponent<MeshFilter>().mesh = combinedMesh;
```

## Profiling

### Unity Frame Debugger
```
Window → Analysis → Frame Debugger
- Shows each draw call
- Identifies batching opportunities
- Highlights why batching failed
```

### Target Numbers
- **Mobile**: < 500 draw calls
- **Console**: < 2000 draw calls
- **PC**: < 3000 draw calls

## Best Practices
✅ Share materials whenever possible
✅ Use texture atlases
✅ Enable GPU instancing for repeated objects
✅ Static batch non-moving objects
✅ Use SRP Batcher (Unity URP/HDRP)
✅ Profile to identify bottlenecks
