# Level of Detail (LOD) System Guide

## LOD Concept
Reduce geometry complexity based on distance

## LOD Levels
```
LOD 0 (Highest): 0-30% distance (10,000 tris)
LOD 1 (High):    30-50% distance (5,000 tris)
LOD 2 (Medium):  50-70% distance (2,000 tris)
LOD 3 (Low):     70-90% distance (500 tris)
LOD 4 (Culled):  90-100% distance (invisible)
```

## Unity LOD Group
```csharp
LODGroup lodGroup = gameObject.AddComponent<LODGroup>();

LOD[] lods = new LOD[3];

// LOD 0 (60% screen height)
lods[0] = new LOD(0.6f, new Renderer[] { highPolyRenderer });

// LOD 1 (30% screen height)
lods[1] = new LOD(0.3f, new Renderer[] { mediumPolyRenderer });

// LOD 2 (10% screen height)
lods[2] = new LOD(0.1f, new Renderer[] { lowPolyRenderer });

lodGroup.SetLODs(lods);
lodGroup.RecalculateBounds();
```

## Unreal LOD
- Import mesh with LODs
- Or: Static Mesh Editor → LOD Settings → Auto-generate

## Creating LOD Meshes

### Manual Reduction
- Retopology in Blender/Maya
- Preserve silhouette
- Reduce hidden geometry first

### Automatic
- Unity: Mesh Simplification package
- Unreal: Auto LOD generation
- External: Simplygon, InstaLOD

## Performance Impact
**Without LOD** (100 objects):
- 1,000,000 triangles
- 30 FPS

**With LOD** (100 objects):
- 200,000 triangles
- 60+ FPS

## Best Practices
✅ At least 3 LOD levels
✅ 50% triangle reduction per level
✅ Test LOD transitions (avoid popping)
✅ Use imposters for distant objects
✅ LOD bias for important objects
