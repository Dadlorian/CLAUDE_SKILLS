# Unity Animation Quick Reference

## Animator Controller
- State machines for animation transitions
- Parameters: Float, Int, Bool, Trigger
- Blend trees for smooth blending

## Code
```csharp
Animator animator = GetComponent<Animator>();
animator.SetFloat("Speed", speed);
animator.SetBool("IsGrounded", isGrounded);
animator.SetTrigger("Jump");
```

## Animation Events
- Call methods at specific animation frames
- Add in Animation window

## IK (Inverse Kinematics)
```csharp
void OnAnimatorIK(int layerIndex)
{
    animator.SetIKPositionWeight(AvatarIKGoal.RightHand, 1);
    animator.SetIKPosition(AvatarIKGoal.RightHand, target.position);
}
```
