# AI Perception Reference

## Vision System

### Field of View
```csharp
bool CanSee(Transform target)
{
    Vector3 directionToTarget = (target.position - transform.position).normalized;
    float angle = Vector3.Angle(transform.forward, directionToTarget);

    if (angle < fieldOfViewAngle / 2)
    {
        // Check line of sight
        if (Physics.Raycast(transform.position, directionToTarget, out RaycastHit hit, viewDistance))
        {
            return hit.transform == target;
        }
    }
    return false;
}
```

### Optimization
- Update at 10-20 Hz (not every frame)
- Use overlap sphere for nearby check first
- Spatial partitioning for multi-agent

## Hearing System

### Sound Propagation
```csharp
public class SoundEvent
{
    public Vector3 Position;
    public float Loudness;
    public float Radius => Loudness * 10f;
}

bool CanHear(SoundEvent sound)
{
    float distance = Vector3.Distance(transform.position, sound.Position);
    return distance < sound.Radius;
}
```

## Attention System

### Priority Scoring
```csharp
float CalculateThreatLevel(GameObject target)
{
    float distance = Vector3.Distance(transform.position, target.position);
    float proximity = 1.0f / (distance + 1.0f);

    bool isVisible = CanSee(target.transform);
    float visibility = isVisible ? 1.0f : 0.3f;

    return proximity * visibility;
}
```

## Memory System
- Track last known position
- Decay confidence over time
- Share information between agents
