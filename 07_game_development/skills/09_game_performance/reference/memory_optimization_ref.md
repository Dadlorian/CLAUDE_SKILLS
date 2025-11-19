# Memory Optimization Reference

## Memory Profiling

### Unity Memory Profiler
```
Window → Analysis → Memory Profiler
1. Capture snapshot
2. Analyze allocations
3. Find memory leaks
4. Track references
```

### Common Memory Leaks
- Event handlers not unsubscribed
- Static references to destroyed objects
- Coroutines not stopped
- Unloaded asset bundles

## Texture Optimization

### Compression
```
Mobile:
- Android: ASTC, ETC2
- iOS: ASTC, PVRTC

PC:
- DXT5/BC7
```

### Max Size
```
UI: 512x512
Characters: 2048x2048
Environment: 1024x1024
Effects: 256x256
```

### Mipmaps
- Generate for 3D textures
- Disable for UI
- **Savings**: 33% memory, better performance

## Mesh Optimization

### Compression
```csharp
// Inspector → Mesh
Compression: High
Read/Write: Disabled (saves copy in RAM)
```

### LOD (Level of Detail)
```
LOD0: 100% detail (0-60%)
LOD1: 50% detail (60-80%)
LOD2: 25% detail (80-95%)
LOD3: 10% detail (95-100%)
```

## Audio Compression

### Settings
```
Music: Vorbis, Streaming
SFX: ADPCM, Decompress On Load
Voice: Vorbis, Compressed In Memory
```

## Addressables

### Benefits
- Load on demand
- Unload when not needed
- Reduced initial memory

```csharp
async void LoadEnemy()
{
    var handle = Addressables.LoadAssetAsync<GameObject>("Enemy");
    await handle.Task;

    // Use enemy

    Addressables.Release(handle); // Unload
}
```

## Memory Budgets

### Mobile (1GB total)
- Textures: 400MB
- Meshes: 150MB
- Audio: 200MB
- Code: 100MB
- Other: 150MB

### Console (10GB total)
- Textures: 4GB
- Meshes: 2GB
- Audio: 1.5GB
- Other: 2.5GB
