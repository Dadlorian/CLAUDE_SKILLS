# ScriptableObjects Quick Reference

## What are ScriptableObjects?

Data containers that exist as assets in your project. They don't need to be attached to GameObjects and can be shared across scenes.

## Common Use Cases

- **Game Configuration**: Settings, balance data, constants
- **Event Systems**: Decoupled communication between systems
- **Inventory Items**: Weapon data, consumables, equipment
- **Character Stats**: Base stats, progression tables
- **Audio/Visual Data**: Sound collections, VFX configurations

## Basic Creation

```csharp
[CreateAssetMenu(fileName = "NewWeapon", menuName = "Game/Weapon")]
public class WeaponData : ScriptableObject
{
    public string weaponName;
    public int damage;
    public float fireRate;
    public GameObject prefab;
}
```

## Event Pattern

```csharp
[CreateAssetMenu(menuName = "Events/Game Event")]
public class GameEvent : ScriptableObject
{
    private List<IGameEventListener> listeners = new List<IGameEventListener>();

    public void Raise()
    {
        for (int i = listeners.Count - 1; i >= 0; i--)
            listeners[i].OnEventRaised();
    }

    public void RegisterListener(IGameEventListener listener)
        => listeners.Add(listener);

    public void UnregisterListener(IGameEventListener listener)
        => listeners.Remove(listener);
}
```

## Runtime Sets

```csharp
[CreateAssetMenu(menuName = "Sets/Enemy Set")]
public class EnemyRuntimeSet : ScriptableObject
{
    public List<Enemy> Items = new List<Enemy>();

    public void Add(Enemy enemy) => Items.Add(enemy);
    public void Remove(Enemy enemy) => Items.Remove(enemy);
}
```

## Best Practices

✅ Use for data that doesn't change during gameplay
✅ Reference from MonoBehaviours instead of duplicating data
✅ Organize in folders by type
✅ Create menu items for easy creation

❌ Don't modify ScriptableObjects at runtime (creates asset changes)
❌ Don't use for per-instance data
❌ Don't serialize large runtime data

## References

- Unity Manual: ScriptableObject
- Ryan Hipple: "Game Architecture with Scriptable Objects" (Unite 2017)
