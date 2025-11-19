# Collision Detection Quick Reference

## Collision Detection Phases

### Broad Phase
**Purpose**: Quickly eliminate pairs that can't collide
**Techniques**:
- Spatial Hashing
- Sweep and Prune (Sort and Sweep)
- Bounding Volume Hierarchy (BVH)
- Quadtree/Octree

### Narrow Phase
**Purpose**: Precise collision detection
**Techniques**:
- SAT (Separating Axis Theorem)
- GJK (Gilbert-Johnson-Keerthi)
- EPA (Expanding Polytope Algorithm)

## Unity Collision

### Collision Detection Modes
- **Discrete**: Fast, can tunnel
- **Continuous**: Prevents tunneling (fast objects)
- **Continuous Dynamic**: Most accurate, most expensive
- **Continuous Speculative**: Best for character controllers

### Layer Matrix
```csharp
// Edit → Project Settings → Physics → Layer Collision Matrix
// Disable unnecessary collision pairs
```

### Callbacks
```csharp
void OnCollisionEnter(Collision collision) { }
void OnCollisionStay(Collision collision) { }
void OnCollisionExit(Collision collision) { }

void OnTriggerEnter(Collider other) { }  // No physics response
void OnTriggerStay(Collider other) { }
void OnTriggerExit(Collider other) { }
```

## Unreal Collision

### Collision Channels
- WorldStatic, WorldDynamic, Pawn, Visibility, Camera
- Custom channels: Edit → Project Settings → Collision

### Collision Presets
- BlockAll, OverlapAll, IgnoreAll
- Custom presets

### Collision Queries
```cpp
// Line trace
FHitResult Hit;
FCollisionQueryParams Params;
GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);

// Sphere sweep
GetWorld()->SweepSingleByChannel(Hit, Start, End, FQuat::Identity,
    ECC_Pawn, FCollisionShape::MakeSphere(Radius), Params);
```

## Optimization

### 1. Use Simple Colliders
- Sphere > Capsule > Box > Convex Mesh > Concave Mesh
- Compound colliders for complex shapes

### 2. Reduce Active Rigidbodies
```csharp
rigidbody.Sleep();  // Manually sleep static objects
```

### 3. Adjust Physics Timestep
```csharp
// Edit → Project Settings → Time
// Fixed Timestep: 0.02 (50Hz) balance of accuracy/performance
```

### 4. Collision Layers
Only check necessary pairs

## Common Shapes

### Sphere
**Use For**: Projectiles, simple objects
**Collision**: Fastest
**Formula**: `distance < r1 + r2`

### Box
**Use For**: Walls, platforms, simple obstacles
**Collision**: Fast (SAT)

### Capsule
**Use For**: Characters, pills
**Collision**: Fast
**Benefits**: No edge snagging

### Mesh
**Use For**: Complex static geometry
**Collision**: Slow
**Note**: Use simplified collision mesh

## Raycasting Best Practices

✅ Specify max distance
✅ Use layer masks
✅ Cache results
✅ Pool raycast commands

## References
- "Real-Time Collision Detection" - Christer Ericson
- Unity Physics Best Practices
- PhysX Documentation
