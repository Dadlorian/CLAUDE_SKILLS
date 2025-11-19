# Gameplay Ability System (GAS) Quick Reference

## What is GAS?

Unreal's framework for implementing abilities, attributes, and effects. Used in Fortnite, Paragon, and recommended for all games with RPG-like systems.

## Core Components

### 1. Ability System Component (ASC)

The main component that owns abilities, attributes, and effects.

```cpp
UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    class UAbilitySystemComponent* AbilitySystemComponent;
};
```

### 2. Gameplay Abilities

```cpp
UCLASS()
class UGA_Jump : public UGameplayAbility
{
    GENERATED_BODY()

    virtual void ActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        const FGameplayEventData* TriggerEventData) override;

    virtual bool CanActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayTagContainer* SourceTags,
        const FGameplayTagContainer* TargetTags,
        FGameplayTagContainer* OptionalRelevantTags) const override;
};

void UGA_Jump::ActivateAbility(...)
{
    // Check if can activate (costs, cooldowns, tags)
    if (!CommitAbility(Handle, ActorInfo, ActivationInfo))
    {
        EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
        return;
    }

    // Execute ability
    ACharacter* Character = Cast<ACharacter>(ActorInfo->AvatarActor.Get());
    if (Character)
    {
        Character->Jump();
    }

    // End ability
    EndAbility(Handle, ActorInfo, ActivationInfo, true, false);
}
```

### 3. Attribute Sets

Define character stats (health, mana, stamina, etc.)

```cpp
UCLASS()
class UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, Category = "Attributes", ReplicatedUsing = OnRep_Health)
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, Category = "Attributes", ReplicatedUsing = OnRep_MaxHealth)
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)

    UPROPERTY(BlueprintReadOnly, Category = "Attributes", ReplicatedUsing = OnRep_Mana)
    FGameplayAttributeData Mana;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Mana)

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

protected:
    UFUNCTION()
    virtual void OnRep_Health(const FGameplayAttributeData& OldHealth);

    UFUNCTION()
    virtual void OnRep_MaxHealth(const FGameplayAttributeData& OldMaxHealth);

    UFUNCTION()
    virtual void OnRep_Mana(const FGameplayAttributeData& OldMana);

    // Called before attribute changes
    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;

    // Called after attribute changes
    virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;
};

void UMyAttributeSet::PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data)
{
    Super::PostGameplayEffectExecute(Data);

    if (Data.EvaluatedData.Attribute == GetHealthAttribute())
    {
        // Clamp health
        SetHealth(FMath::Clamp(GetHealth(), 0.0f, GetMaxHealth()));

        // Trigger death if health reaches 0
        if (GetHealth() <= 0.0f)
        {
            // Handle death
        }
    }
}
```

### 4. Gameplay Effects

Modify attributes (damage, healing, buffs, debuffs)

```cpp
// Instant damage effect
UCLASS()
class UGE_Damage : public UGameplayEffect
{
    GENERATED_BODY()

public:
    UGE_Damage()
    {
        DurationPolicy = EGameplayEffectDurationType::Instant;

        FGameplayModifierInfo ModifierInfo;
        ModifierInfo.ModifierMagnitude = FScalableFloat(10.0f);
        ModifierInfo.ModifierOp = EGameplayModOp::Additive;
        ModifierInfo.Attribute = UMyAttributeSet::GetHealthAttribute();

        Modifiers.Add(ModifierInfo);
    }
};

// Duration-based buff
UCLASS()
class UGE_SpeedBuff : public UGameplayEffect
{
    GENERATED_BODY()

public:
    UGE_SpeedBuff()
    {
        DurationPolicy = EGameplayEffectDurationType::HasDuration;
        DurationMagnitude = FScalableFloat(5.0f); // 5 seconds

        FGameplayModifierInfo ModifierInfo;
        ModifierInfo.ModifierMagnitude = FScalableFloat(1.5f); // 150% speed
        ModifierInfo.ModifierOp = EGameplayModOp::Multiply;
        ModifierInfo.Attribute = UMyAttributeSet::GetMoveSpeedAttribute();

        Modifiers.Add(ModifierInfo);
    }
};

// Applying effects
void ApplyDamage(AActor* Target, float DamageAmount)
{
    UAbilitySystemComponent* TargetASC = UAbilitySystemBlueprintLibrary::GetAbilitySystemComponent(Target);

    if (TargetASC)
    {
        FGameplayEffectContextHandle EffectContext = TargetASC->MakeEffectContext();
        FGameplayEffectSpecHandle SpecHandle = TargetASC->MakeOutgoingSpec(
            UGE_Damage::StaticClass(),
            1.0f, // Level
            EffectContext
        );

        if (SpecHandle.IsValid())
        {
            TargetASC->ApplyGameplayEffectSpecToSelf(*SpecHandle.Data.Get());
        }
    }
}
```

### 5. Gameplay Tags

Hierarchical tags for abilities, effects, and states

```cpp
// GameplayTags.ini
[/Script/GameplayTags.GameplayTagsSettings]
GameplayTagList=(Tag="Ability.Attack.Melee",DevComment="Melee attack ability")
GameplayTagList=(Tag="Ability.Attack.Ranged",DevComment="Ranged attack ability")
GameplayTagList=(Tag="State.Stunned",DevComment="Character is stunned")
GameplayTagList=(Tag="State.Invulnerable",DevComment="Cannot take damage")

// Usage
FGameplayTagContainer Tags;
Tags.AddTag(FGameplayTag::RequestGameplayTag(FName("State.Stunned")));

// Check tags
bool bIsStunned = AbilitySystemComponent->HasMatchingGameplayTag(
    FGameplayTag::RequestGameplayTag(FName("State.Stunned"))
);

// Block abilities based on tags
AbilitySystemComponent->BlockAbilitiesWithTags(Tags);
```

### 6. Gameplay Cues

Visual and audio effects triggered by gameplay events

```cpp
UCLASS()
class AGC_Explosion : public AGameplayCueNotify_Actor
{
    GENERATED_BODY()

    virtual bool OnExecute_Implementation(
        AActor* MyTarget,
        const FGameplayCueParameters& Parameters) override
    {
        // Spawn explosion VFX
        UGameplayStatics::SpawnEmitterAtLocation(
            GetWorld(),
            ExplosionParticles,
            Parameters.Location
        );

        // Play sound
        UGameplayStatics::PlaySoundAtLocation(
            GetWorld(),
            ExplosionSound,
            Parameters.Location
        );

        return true;
    }
};
```

## Common Patterns

### Granting Abilities
```cpp
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (AbilitySystemComponent && HasAuthority())
    {
        for (TSubclassOf<UGameplayAbility>& Ability : DefaultAbilities)
        {
            AbilitySystemComponent->GiveAbility(
                FGameplayAbilitySpec(Ability, 1, INDEX_NONE, this)
            );
        }
    }
}
```

### Ability Tasks
```cpp
UAbilityTask_WaitTargetData* Task = UAbilityTask_WaitTargetData::WaitTargetData(
    this,
    FName("WaitTargetData"),
    EGameplayTargetingConfirmation::UserConfirmed,
    TargetActor
);

Task->ValidData.AddDynamic(this, &UMyAbility::OnTargetDataReady);
Task->ReadyForActivation();
```

### Cooldowns
```cpp
// Define cooldown in ability
FGameplayEffectSpecHandle CooldownEffectSpec = MakeOutgoingGameplayEffectSpec(CooldownEffectClass);
ApplyGameplayEffectSpecToOwner(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, CooldownEffectSpec);

// Check cooldown
const FGameplayTagContainer* CooldownTags = GetCooldownTags();
if (AbilitySystemComponent->HasAnyMatchingGameplayTags(*CooldownTags))
{
    // On cooldown
    float TimeRemaining = AbilitySystemComponent->GetCooldownTimeRemaining(*CooldownTags);
}
```

## Best Practices

✅ Use Gameplay Tags for all ability/effect classification
✅ Keep AttributeSets focused (separate combat, movement, etc.)
✅ Use Gameplay Cues for all VFX/SFX
✅ Implement PreAttributeChange for clamping
✅ Use Ability Tasks for async operations

❌ Don't modify attributes directly (use Gameplay Effects)
❌ Don't hardcode tag names (use constants)
❌ Don't skip CommitAbility (validates costs/cooldowns)

## References

- Unreal Documentation: Gameplay Ability System
- Lyra Starter Game (Epic's GAS example)
- Tranek's GASDocumentation (Community guide)
