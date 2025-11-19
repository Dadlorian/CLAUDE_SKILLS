# Physics Materials Reference

## Properties

### Friction
- **Static Friction**: Resistance to start moving
- **Dynamic Friction**: Resistance while moving
- **Range**: 0 (ice) to 1 (rubber)

### Bounciness (Restitution)
- Energy retained after collision
- **Range**: 0 (clay) to 1 (superball)
- Formula: `v_after = v_before × restitution`

### Combine Modes
- **Average**: (a + b) / 2
- **Minimum**: min(a, b)
- **Maximum**: max(a, b)
- **Multiply**: a × b

## Unity Example
```csharp
PhysicMaterial ice = new PhysicMaterial();
ice.dynamicFriction = 0.1f;
ice.staticFriction = 0.1f;
ice.bounciness = 0.0f;
ice.frictionCombine = PhysicMaterialCombine.Minimum;

collider.material = ice;
```

## Common Materials
- **Ice**: Friction 0.05, Bounce 0
- **Rubber**: Friction 0.8, Bounce 0.7
- **Wood**: Friction 0.4, Bounce 0.2
- **Metal**: Friction 0.3, Bounce 0.1
