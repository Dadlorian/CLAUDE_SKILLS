# Unreal Niagara VFX Guide

## Creating Particle System
1. Content Browser → FX → Niagara System
2. Choose template (Fountain, Sprite, etc.)
3. Edit in Niagara Editor

## Common Modules
- **Spawn Rate**: Particles per second
- **Lifetime**: Duration
- **Color**: RGB over lifetime
- **Size**: Scale over lifetime
- **Velocity**: Movement direction/speed

## Spawn in Code
```cpp
UNiagaraComponent* VFXComponent = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
    GetWorld(),
    ExplosionVFX,
    Location,
    Rotation
);
```

## Parameters
```cpp
VFXComponent->SetVariableFloat("Size", 2.0f);
VFXComponent->SetVariableLinearColor("Color", FLinearColor::Red);
```

## Performance
- Use GPU particles for large counts
- LOD systems for distance
- Particle limits
