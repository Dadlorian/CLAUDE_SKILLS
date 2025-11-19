# Unreal Animation Blueprints Guide

## State Machine
- Idle → Run → Jump
- Blend transitions
- Transition rules

## Blend Spaces
- 2D: Speed X, Direction Y
- 1D: Speed only
- Samples: Walk, Run, Sprint animations

## Animation Notifies
```cpp
UFUNCTION()
void AnimNotify_FootStep()
{
    // Play footstep sound
    UGameplayStatics::PlaySoundAtLocation(this, FootstepSound, GetActorLocation());
}
```

## Code Control
```cpp
UAnimInstance* AnimInstance = GetMesh()->GetAnimInstance();
if (AnimInstance)
{
    AnimInstance->Montage_Play(AttackMontage);
}
```

## IK (Inverse Kinematics)
- Two Bone IK node
- Foot placement
- Look at target
