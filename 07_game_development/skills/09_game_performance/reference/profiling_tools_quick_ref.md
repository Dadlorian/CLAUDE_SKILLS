# Profiling Tools Quick Reference

## Unity Profiling

### Unity Profiler
**Access**: Window → Analysis → Profiler

**Key Modules**:
- **CPU Usage**: Method timings, main thread bottlenecks
- **GPU Usage**: Rendering bottlenecks
- **Memory**: Allocations, GC spikes
- **Rendering**: Draw calls, batches, vertices
- **Physics**: Rigidbody count, collision checks
- **Audio**: Voice count, memory usage

**Workflow**:
```csharp
// 1. Build Development Build with "Autoconnect Profiler"
// 2. Run on target device
// 3. Window → Analysis → Profiler
// 4. Record data while playing
// 5. Analyze spikes and bottlenecks
```

**Custom Profiling Markers**:
```csharp
using Unity.Profiling;

static readonly ProfilerMarker s_MyMarker = new ProfilerMarker("MyExpensiveOperation");

void MyMethod()
{
    using (s_MyMarker.Auto())
    {
        // Code to profile
    }
}
```

### Frame Debugger
**Access**: Window → Analysis → Frame Debugger

**Use For**:
- Step through draw calls one-by-one
- See exactly what's being rendered
- Identify overdraw issues
- Verify batching

### Memory Profiler (Package)
**Install**: Package Manager → Memory Profiler

**Features**:
- Memory snapshots
- Object reference tracking
- Memory leak detection
- Managed vs Native memory breakdown

## Unreal Profiling

### Unreal Insights
**Access**: Launch with `-trace=cpu,frame,bookmark,gpu`

```bash
UnrealEditor-Cmd.exe MyProject -game -trace=cpu,frame,bookmark,gpu
UnrealInsights.exe
```

**Features**:
- CPU timeline (Game, Render threads)
- GPU timeline
- Frame timing
- Asset loading
- Memory allocations

### Console Commands

```
stat fps              // Show FPS
stat unit             // Frame time breakdown (Game, Draw, GPU)
stat game             // Game thread stats
stat gpu              // GPU stats
stat scenerendering   // Rendering stats
stat memory           // Memory usage
profilegpu            // Detailed GPU profiling
dumpticks             // List all ticking actors
```

**Example Session**:
```
1. stat unit          // Identify bottleneck (Game vs Render vs GPU)
2. stat gpu           // If GPU bound, drill into rendering
3. stat game          // If Game bound, check actor ticks
4. dumpticks          // Find expensive actors
```

### Rendering Debugger
**Access**: Viewport → Show → Visualize

**View Modes**:
- **Shader Complexity**: Red = expensive shaders
- **Quad Overdraw**: Identify overdraw
- **Lightmap Density**: Check lightmap resolution
- **LOD Coloration**: Verify LOD transitions

## Platform-Specific Tools

### Mobile (iOS)

**Instruments** (Apple):
```bash
# 1. Build from Xcode
# 2. Product → Profile (⌘I)
# 3. Choose template:
#    - Time Profiler: CPU profiling
#    - Allocations: Memory profiling
#    - Energy Log: Battery usage
```

**Metal Debugger**:
- Xcode → Debug → Capture GPU Frame
- Analyze draw calls, shaders, memory

### Mobile (Android)

**Android Studio Profiler**:
```bash
# 1. Build APK with Debug symbols
# 2. View → Tool Windows → Profiler
# 3. Attach to process
```

**Modules**:
- CPU: Method tracing
- Memory: Java heap, native heap
- Network: Bandwidth usage
- Energy: Battery drain

**Snapdragon Profiler** (Qualcomm devices):
- CPU, GPU, Memory, Thermal monitoring
- Shader analysis
- Frame analysis

### PC

**Intel VTune**:
- CPU microarchitecture analysis
- Hotspot analysis
- Threading analysis
- Memory access patterns

**NVIDIA Nsight**:
- GPU profiling
- Shader debugging
- Memory analysis
- API tracing

**PIX** (Xbox/Windows):
- DirectX profiling
- GPU timeline
- HLSL shader debugging

**RenderDoc**:
- Frame capture and analysis
- Shader debugging
- Resource inspection
- Cross-platform (DX, Vulkan, OpenGL)

## Quick Diagnostic Workflows

### FPS Drops

```
1. stat fps           // Confirm FPS drop
2. stat unit          // Game, Draw, or GPU bound?
3. If GPU: stat gpu   // What's expensive?
4. If Game: stat game // Which systems?
5. Profile specific system
```

### Memory Issues

```
Unity:
1. Profiler → Memory
2. Look for growing allocations
3. Take snapshot
4. Garbage collect
5. Take another snapshot
6. Compare differences

Unreal:
1. stat memory
2. Look for texture streaming
3. dumpticks (object count)
4. Check asset loading
```

### Stuttering

```
1. Look for GC spikes (Unity)
2. Check asset streaming
3. Profile shader compilation
4. Verify vsync/frame pacing
5. Check for background processes
```

## Best Practices

✅ **Always Profile on Target Hardware**
- Editor is not representative
- Mobile << PC performance

✅ **Profile Release Builds**
- Debug builds have overhead
- Compiler optimizations matter

✅ **Reproduce Worst-Case Scenarios**
- Max enemies on screen
- Complex scenes
- Extended play sessions

✅ **Establish Baselines**
- Record performance before changes
- Track regressions

✅ **Profile Regularly**
- Don't wait until the end
- Catch issues early

## Performance Budgets

Set target budgets and monitor:

**Frame Time (60 FPS = 16.67ms)**:
- Game Logic: 8-10ms
- Rendering: 4-6ms
- Physics: 1-2ms
- Audio: 0.5-1ms

**Memory (Mobile)**:
- Textures: < 200MB
- Meshes: < 50MB
- Audio: < 30MB
- Code: < 50MB

**Draw Calls**:
- Mobile: < 500
- Console: < 2000
- PC: < 3000

**Batches**:
- Mobile: < 150
- Console: < 500
- PC: < 1000

## Common Bottlenecks

**CPU (Game Thread)**:
- Too many `Update()` calls
- GetComponent in loops
- Expensive AI/pathfinding
- Physics calculations

**CPU (Render Thread)**:
- Too many draw calls
- Complex materials
- Expensive shaders
- Shadow cascades

**GPU**:
- High resolution
- Complex shaders
- Overdraw (transparency)
- Post-processing

**Memory**:
- Large textures
- Uncompressed audio
- Too many loaded assets
- Memory leaks

## References

- Unity Manual: Profiler
- Unreal Documentation: Performance and Profiling
- NVIDIA Developer: GPU Profiling
- Intel VTune User Guide
