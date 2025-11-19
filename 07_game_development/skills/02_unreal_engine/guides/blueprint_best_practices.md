# Unreal Blueprint Best Practices

## When to Use Blueprints vs C++

### Use Blueprints For:
✅ Level scripting and sequences
✅ Designer-friendly gameplay tuning
✅ Rapid prototyping
✅ Visual effects and animation logic
✅ UI (UMG) logic

### Use C++ For:
✅ Core gameplay systems
✅ Performance-critical code
✅ Complex algorithms
✅ Network replication logic
✅ Plugin development

## Organization

### Folder Structure
```
Content/
├── Blueprints/
│   ├── Characters/
│   ├── Weapons/
│   ├── AI/
│   └── Systems/
```

### Naming Conventions
- Blueprint Classes: `BP_ClassName`
- Blueprint Interfaces: `BPI_InterfaceName`
- Enums: `E_EnumName`
- Structures: `S_StructName`

## Performance Optimization

### 1. Avoid Event Tick When Possible
❌ **Bad**:
```
Event Tick → Complex Logic
```

✅ **Good**:
```
Use Timers for periodic checks:
Set Timer by Function Name (UpdateAI, 0.1s, true)
```

### 2. Use Interfaces Instead of Casting
❌ **Bad**:
```
Cast to Enemy → Take Damage
```

✅ **Good**:
```
Call Interface (IDamageable) → Take Damage
```

### 3. Cache References
❌ **Bad**:
```
Get All Actors of Class (every frame)
```

✅ **Good**:
```
Cache in BeginPlay → Store reference
```

### 4. Disable Tick When Not Needed
```
Set Actor Tick Enabled (false)
```

## Blueprint Nativization

For shipping builds:
- Project Settings → Packaging
- Blueprint Nativization Method: Inclusive/Exclusive
- Converts Blueprints to C++ for performance

## Debugging

### Print String
```
Print String (message, duration, color)
```

### Breakpoints
- Right-click node → Add Breakpoint
- F9 to toggle breakpoint

### Watch Values
- Right-click variable → Watch This Value

## References
- Unreal Documentation: Blueprint Best Practices
- Epic's Lyra Starter Game
