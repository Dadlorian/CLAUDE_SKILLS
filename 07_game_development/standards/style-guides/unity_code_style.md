# Unity C# Code Style Guide
## Elite Professional Standards for Unity Development

### Philosophy
This guide synthesizes best practices from:
- **Microsoft C# Coding Conventions** - Industry standard for C#
- **Unity Technologies Official Guidelines** - Unity-specific best practices
- **Google C# Style Guide** - Additional professional standards
- **Rider/ReSharper Conventions** - IDE-enforced quality
- **DOTS/ECS Best Practices** - Modern Unity architecture

---

## Core Principles

### 1. Readability Over Cleverness
**Standard**: Code should be immediately understandable by other developers
- Favor explicit over implicit
- Use meaningful names over comments
- Keep methods small and focused (max 20-30 lines)
- Reference: "Clean Code" by Robert C. Martin

### 2. Performance Awareness
**Standard**: Write performant code by default, optimize hot paths
- Avoid allocations in Update/FixedUpdate
- Cache component references in Awake/Start
- Use object pooling for frequently instantiated objects
- Reference: Unity "Best Practice Guides - Performance"

### 3. Unity-Specific Patterns
**Standard**: Follow Unity's component-based architecture
- Composition over inheritance
- Scriptable objects for data-driven design
- Prefer UnityEvents for loose coupling
- Reference: Unity "Game Architecture with Scriptable Objects"

---

## Naming Conventions

### Files and Classes

```csharp
// GOOD: PascalCase for classes, matches filename
public class PlayerController : MonoBehaviour { }
// File: PlayerController.cs

// GOOD: Interfaces start with 'I'
public interface IDamageable { }

// GOOD: ScriptableObject classes
[CreateAssetMenu(menuName = "Game/Weapon Data")]
public class WeaponData : ScriptableObject { }

// AVOID: Abbreviations (except common: UI, AI, NPC, HP, MP)
public class PlayerCtrl { }  // ❌ Bad
public class PlayerController { }  // ✅ Good
```

### Variables and Fields

```csharp
public class ExampleNaming : MonoBehaviour
{
    // Public fields: camelCase (serialized in Inspector)
    public float moveSpeed = 5f;
    public int maxHealth = 100;

    // Private fields: camelCase (Unity convention, different from C# standard)
    private Rigidbody rb;
    private Transform targetTransform;

    // Properties: PascalCase
    public int CurrentHealth { get; private set; }
    public bool IsAlive => CurrentHealth > 0;

    // Constants: PascalCase
    private const int MaxInventorySize = 40;
    private const string PlayerTag = "Player";

    // Static fields: PascalCase with 's_' prefix (optional but clear)
    private static int s_instanceCount = 0;

    // Events: PascalCase with 'On' prefix
    public event System.Action OnDeath;
    public event System.Action<int> OnHealthChanged;
}
```

### Methods

```csharp
// GOOD: PascalCase, verb-based, descriptive
public void TakeDamage(int amount) { }
public bool IsGrounded() { }
public Vector3 CalculateVelocity() { }

// GOOD: Async methods end with 'Async'
public async Task LoadSceneAsync(string sceneName) { }

// GOOD: Unity message methods (keep standard names)
private void Awake() { }
private void Start() { }
private void Update() { }
private void FixedUpdate() { }
private void OnCollisionEnter(Collision collision) { }
```

### Prefabs and Assets

```
// Scene naming: PascalCase, descriptive
MainMenu.unity
Level_01_Forest.unity
Gameplay_Tutorial.unity

// Prefabs: PascalCase, descriptive
Player.prefab
Enemy_Zombie.prefab
Weapon_Sword_Iron.prefab

// Materials: PascalCase with 'Mat_' prefix (optional but clear)
Mat_Metal_Rusty.mat
Mat_Grass.mat

// ScriptableObjects: PascalCase with type suffix
PlayerStats_Default.asset
WeaponData_Sword.asset
```

---

## Code Organization

### File Structure

```csharp
// 1. Using directives (sorted, Unity first, then System, then custom)
using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections;
using System.Collections.Generic;
using MyGame.Utilities;

// 2. Namespace (optional but recommended for larger projects)
namespace MyGame.Player
{
    // 3. Class documentation
    /// <summary>
    /// Controls player movement and handles input.
    /// Requires Rigidbody component for physics-based movement.
    /// </summary>
    [RequireComponent(typeof(Rigidbody))]
    public class PlayerController : MonoBehaviour
    {
        // 4. Nested types
        [System.Serializable]
        public class MovementSettings
        {
            public float speed = 5f;
            public float jumpForce = 10f;
        }

        // 5. Constants
        private const float GroundCheckDistance = 0.1f;

        // 6. Static fields
        private static int s_playerCount = 0;

        // 7. Serialized fields (Inspector-visible)
        [Header("Movement")]
        [SerializeField] private MovementSettings movementSettings;
        [SerializeField] private LayerMask groundLayer;

        [Header("References")]
        [SerializeField] private Transform cameraTransform;

        // 8. Public properties
        public bool IsGrounded { get; private set; }
        public Vector3 Velocity => rb.velocity;

        // 9. Private fields (cached references)
        private Rigidbody rb;
        private Vector3 moveInput;

        // 10. Events
        public event Action OnJump;

        // 11. Unity lifecycle methods
        private void Awake()
        {
            rb = GetComponent<Rigidbody>();
            s_playerCount++;
        }

        private void Update()
        {
            HandleInput();
            CheckGrounded();
        }

        private void FixedUpdate()
        {
            ApplyMovement();
        }

        private void OnDestroy()
        {
            s_playerCount--;
        }

        // 12. Public methods
        public void Jump()
        {
            if (IsGrounded)
            {
                rb.AddForce(Vector3.up * movementSettings.jumpForce, ForceMode.Impulse);
                OnJump?.Invoke();
            }
        }

        // 13. Private methods
        private void HandleInput()
        {
            moveInput = new Vector3(
                Input.GetAxisRaw("Horizontal"),
                0f,
                Input.GetAxisRaw("Vertical")
            ).normalized;
        }

        private void ApplyMovement()
        {
            Vector3 movement = cameraTransform.TransformDirection(moveInput) * movementSettings.speed;
            movement.y = rb.velocity.y; // Preserve vertical velocity
            rb.velocity = movement;
        }

        private void CheckGrounded()
        {
            IsGrounded = Physics.Raycast(
                transform.position,
                Vector3.down,
                GroundCheckDistance,
                groundLayer
            );
        }
    }
}
```

### Component Organization

```csharp
// GOOD: Single responsibility, focused components
public class Health : MonoBehaviour
{
    public event Action OnDeath;

    [SerializeField] private int maxHealth = 100;
    public int CurrentHealth { get; private set; }

    private void Awake() => CurrentHealth = maxHealth;

    public void TakeDamage(int amount)
    {
        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
        if (CurrentHealth == 0)
            OnDeath?.Invoke();
    }
}

public class PlayerCombat : MonoBehaviour
{
    [SerializeField] private int attackDamage = 10;
    [SerializeField] private LayerMask enemyLayer;

    public void Attack()
    {
        // Attack logic
    }
}

// AVOID: God classes that do everything
public class Player : MonoBehaviour
{
    // Movement, combat, inventory, dialogue, all in one ❌
}
```

---

## Performance Best Practices

### Avoid Allocations in Hot Paths

```csharp
// ❌ BAD: Allocates every frame
void Update()
{
    string message = "Health: " + currentHealth;  // String allocation
    var enemies = GameObject.FindGameObjectsWithTag("Enemy");  // Array allocation
}

// ✅ GOOD: Minimize allocations
private readonly List<Enemy> cachedEnemies = new List<Enemy>();
private int currentHealth;

void Update()
{
    // Cache references in Awake/Start
    // Use object pooling for temporary objects
    // Avoid string concatenation in hot paths
}
```

### Cache Component References

```csharp
// ❌ BAD: GetComponent every frame (very slow)
void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// ✅ GOOD: Cache in Awake/Start
private Rigidbody rb;

private void Awake()
{
    rb = GetComponent<Rigidbody>();
}

private void Update()
{
    rb.AddForce(Vector3.up);
}
```

### Use Object Pooling

```csharp
// ✅ GOOD: Object pool pattern
public class ObjectPool : MonoBehaviour
{
    [SerializeField] private GameObject prefab;
    [SerializeField] private int initialSize = 10;

    private Queue<GameObject> pool = new Queue<GameObject>();

    private void Awake()
    {
        for (int i = 0; i < initialSize; i++)
        {
            GameObject obj = Instantiate(prefab);
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }

    public GameObject Get()
    {
        if (pool.Count > 0)
        {
            GameObject obj = pool.Dequeue();
            obj.SetActive(true);
            return obj;
        }
        return Instantiate(prefab);
    }

    public void Return(GameObject obj)
    {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

### Optimize Physics

```csharp
// ✅ GOOD: Use layer-based collision
Physics.IgnoreLayerCollision(playerLayer, playerLayer);

// ✅ GOOD: Use Raycast with max distance
if (Physics.Raycast(origin, direction, out RaycastHit hit, maxDistance, layerMask))
{
    // Hit something
}

// ❌ BAD: Don't use Find in Update
void Update()
{
    GameObject.Find("Player");  // Very slow!
}

// ✅ GOOD: Cache references or use tags
private GameObject player;
void Awake()
{
    player = GameObject.FindGameObjectWithTag("Player");
}
```

---

## Unity-Specific Patterns

### Scriptable Objects for Data

```csharp
[CreateAssetMenu(fileName = "New Weapon", menuName = "Game/Weapon")]
public class WeaponData : ScriptableObject
{
    [Header("Stats")]
    public string weaponName;
    public int damage;
    public float fireRate;

    [Header("Visuals")]
    public Sprite icon;
    public GameObject prefab;

    public void Attack(Transform firePoint)
    {
        // Weapon-specific attack logic
    }
}

// Usage in component
public class WeaponController : MonoBehaviour
{
    [SerializeField] private WeaponData currentWeapon;

    public void Fire()
    {
        currentWeapon.Attack(firePoint);
    }
}
```

### Events with ScriptableObjects

```csharp
// GameEvent.cs
[CreateAssetMenu(menuName = "Events/Game Event")]
public class GameEvent : ScriptableObject
{
    private readonly List<GameEventListener> listeners = new List<GameEventListener>();

    public void Raise()
    {
        for (int i = listeners.Count - 1; i >= 0; i--)
            listeners[i].OnEventRaised();
    }

    public void RegisterListener(GameEventListener listener) => listeners.Add(listener);
    public void UnregisterListener(GameEventListener listener) => listeners.Remove(listener);
}

// GameEventListener.cs
public class GameEventListener : MonoBehaviour
{
    [SerializeField] private GameEvent gameEvent;
    [SerializeField] private UnityEvent response;

    private void OnEnable() => gameEvent.RegisterListener(this);
    private void OnDisable() => gameEvent.UnregisterListener(this);

    public void OnEventRaised() => response.Invoke();
}
```

### Coroutines vs Async/Await

```csharp
// GOOD: Coroutines for Unity-timing-dependent logic
public class CoroutineExample : MonoBehaviour
{
    IEnumerator Start()
    {
        yield return new WaitForSeconds(1f);
        Debug.Log("After 1 second");

        yield return new WaitUntil(() => playerReady);
        Debug.Log("Player is ready");

        yield return StartCoroutine(LoadScene());
    }

    IEnumerator LoadScene()
    {
        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync("NextScene");
        while (!asyncLoad.isDone)
        {
            float progress = asyncLoad.progress;
            yield return null;
        }
    }
}

// GOOD: Async/Await for non-Unity async operations
public class AsyncExample : MonoBehaviour
{
    async void Start()
    {
        string data = await LoadDataFromWebAsync();
        ProcessData(data);
    }

    async Task<string> LoadDataFromWebAsync()
    {
        using (var client = new HttpClient())
        {
            return await client.GetStringAsync("https://api.example.com/data");
        }
    }
}
```

---

## Code Documentation

### XML Documentation

```csharp
/// <summary>
/// Handles player health, damage, and death.
/// </summary>
public class Health : MonoBehaviour
{
    /// <summary>
    /// Invoked when health reaches zero.
    /// </summary>
    public event Action OnDeath;

    /// <summary>
    /// Applies damage to this entity.
    /// </summary>
    /// <param name="amount">The amount of damage to apply.</param>
    /// <param name="source">The source of the damage (optional).</param>
    public void TakeDamage(int amount, GameObject source = null)
    {
        // Implementation
    }
}
```

### Inspector Tooltips

```csharp
[Tooltip("Movement speed in units per second")]
[SerializeField] private float moveSpeed = 5f;

[Tooltip("Layers that count as ground for jump detection")]
[SerializeField] private LayerMask groundLayer;
```

### Header Organization

```csharp
[Header("Movement Settings")]
[SerializeField] private float moveSpeed = 5f;
[SerializeField] private float jumpForce = 10f;

[Header("Combat Settings")]
[SerializeField] private int attackDamage = 10;
[SerializeField] private float attackCooldown = 0.5f;

[Header("References")]
[SerializeField] private Transform attackPoint;
[SerializeField] private LayerMask enemyLayer;
```

---

## Common Pitfalls to Avoid

### 1. Comparing Tags with ==

```csharp
// ❌ BAD: String allocation
if (other.gameObject.tag == "Player") { }

// ✅ GOOD: Use CompareTag (no allocation)
if (other.CompareTag("Player")) { }
```

### 2. Empty Unity Methods

```csharp
// ❌ BAD: Unity still calls empty methods
void Update() { }

// ✅ GOOD: Remove unused Unity methods
// Don't include Update if not needed
```

### 3. Not Null-Checking Serialized Fields

```csharp
// ✅ GOOD: Validate in Awake
[SerializeField] private Transform target;

private void Awake()
{
    if (target == null)
    {
        Debug.LogError($"{name}: Target not assigned!", this);
        enabled = false;
    }
}
```

### 4. Using SendMessage

```csharp
// ❌ BAD: SendMessage is slow and error-prone
SendMessage("TakeDamage", 10);

// ✅ GOOD: Direct reference or events
health.TakeDamage(10);
// Or
OnDamageEvent?.Invoke(10);
```

---

## Modern Unity (DOTS/ECS)

### DOTS Naming Conventions

```csharp
// Components: Struct with IComponentData
public struct PlayerMovementComponent : IComponentData
{
    public float Speed;
    public float3 Direction;
}

// Systems: Describe what they do
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class PlayerMovementSystem : SystemBase
{
    protected override void OnUpdate()
    {
        float deltaTime = Time.DeltaTime;

        Entities.ForEach((ref Translation translation,
            in PlayerMovementComponent movement) =>
        {
            translation.Value += movement.Direction * movement.Speed * deltaTime;
        }).ScheduleParallel();
    }
}
```

---

## Testing

### Unity Test Framework

```csharp
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using System.Collections;

public class HealthTests
{
    [Test]
    public void TakeDamage_ReducesHealth()
    {
        // Arrange
        var gameObject = new GameObject();
        var health = gameObject.AddComponent<Health>();
        int initialHealth = health.CurrentHealth;

        // Act
        health.TakeDamage(10);

        // Assert
        Assert.AreEqual(initialHealth - 10, health.CurrentHealth);

        // Cleanup
        Object.DestroyImmediate(gameObject);
    }

    [UnityTest]
    public IEnumerator Player_JumpsWithinOneFrame()
    {
        // Test coroutines and Unity timing
        yield return null;
    }
}
```

---

## Tools & Enforcement

### Recommended Tools
- **Rider** - Best Unity C# IDE (ReSharper included)
- **Visual Studio 2022** - Free, good Unity integration
- **Unity Code Snippets** - Speed up development
- **.editorconfig** - Enforce style across team

### Example .editorconfig

```ini
[*.cs]
# Naming conventions
dotnet_naming_rule.unity_serialized_field.severity = warning
dotnet_naming_rule.unity_serialized_field.symbols = unity_serialized_field
dotnet_naming_rule.unity_serialized_field.style = camel_case

# Code style
csharp_prefer_braces = true:warning
csharp_prefer_simple_using_statement = true:suggestion
```

---

## References

- **Microsoft C# Conventions**: https://docs.microsoft.com/dotnet/csharp/fundamentals/coding-style/coding-conventions
- **Unity Best Practices**: https://unity.com/how-to/naming-and-code-style-tips-c-scripting-unity
- **Clean Code**: Robert C. Martin
- **Unity Performance Guidelines**: https://docs.unity3d.com/Manual/BestPracticeUnderstandingPerformanceInUnity.html

---

**Version**: 1.0 (Unity 2022.3 LTS+)
**Last Updated**: 2025-11-19
