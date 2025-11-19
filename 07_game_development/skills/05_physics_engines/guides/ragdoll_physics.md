# Ragdoll Physics Guide

## Unity Ragdoll

### Automatic Setup
1. GameObject → 3D Object → Ragdoll
2. Assign bones (hips, spine, head, limbs)
3. Unity creates colliders + joints

### Manual Setup
```csharp
public class RagdollController : MonoBehaviour
{
    private Animator animator;
    private Rigidbody[] ragdollRigidbodies;

    void Awake()
    {
        animator = GetComponent<Animator>();
        ragdollRigidbodies = GetComponentsInChildren<Rigidbody>();

        DisableRagdoll();
    }

    public void EnableRagdoll()
    {
        animator.enabled = false;

        foreach (Rigidbody rb in ragdollRigidbodies)
        {
            rb.isKinematic = false;
            rb.detectCollisions = true;
        }
    }

    public void DisableRagdoll()
    {
        animator.enabled = true;

        foreach (Rigidbody rb in ragdollRigidbodies)
        {
            rb.isKinematic = true;
            rb.detectCollisions = false;
        }
    }

    public void ApplyForce(Vector3 force, Vector3 position)
    {
        EnableRagdoll();

        // Find closest rigidbody to impact point
        Rigidbody closest = ragdollRigidbodies[0];
        float minDist = Vector3.Distance(position, closest.position);

        foreach (Rigidbody rb in ragdollRigidbodies)
        {
            float dist = Vector3.Distance(position, rb.position);
            if (dist < minDist)
            {
                minDist = dist;
                closest = rb;
            }
        }

        closest.AddForceAtPosition(force, position, ForceMode.Impulse);
    }
}
```

## Unreal Ragdoll
```cpp
void AMyCharacter::EnableRagdoll()
{
    GetMesh()->SetSimulatePhysics(true);
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
}

void AMyCharacter::ApplyRagdollImpulse(FVector Impulse, FVector Location)
{
    GetMesh()->AddImpulseAtLocation(Impulse, Location);
}
```

## Best Practices
✅ Limit angular velocity (prevent spinning)
✅ Set appropriate mass (70kg for human)
✅ Use joint limits (realistic movement)
✅ Disable ragdoll after settling (performance)
✅ Blend back to animation for "get up"

## Performance
- Ragdolls are expensive (physics calculations)
- Limit active ragdolls (< 10-20)
- Simplify distant ragdolls
- Remove/freeze after 5-10 seconds
