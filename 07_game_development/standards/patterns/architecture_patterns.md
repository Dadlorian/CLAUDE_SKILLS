# Game Architecture Patterns
## Elite Professional Design Patterns for Game Development

### Philosophy
This guide synthesizes architectural patterns from:
- **Epic Games** - Gameplay Ability System, Lyra architecture
- **Unity Technologies** - DOTS/ECS, ScriptableObject architecture
- **Valve** - Source engine entity-component system
- **id Software** - Fast-paced action game architecture
- **"Game Programming Patterns"** - Robert Nystrom
- **"Game Engine Architecture"** - Jason Gregory (Naughty Dog)

---

## Core Architectural Patterns

### 1. Entity-Component System (ECS)

**Problem**: Object-oriented inheritance hierarchies become complex and inflexible

**Solution**: Composition-based architecture where entities are containers for components

**When to Use**:
- Large numbers of similar entities
- Need for performance optimization through data-oriented design
- Flexible entity definitions

**Implementation**:

```csharp
// Component: Pure data, no logic
public struct TransformComponent : IComponentData
{
    public float3 Position;
    public quaternion Rotation;
    public float3 Scale;
}

public struct VelocityComponent : IComponentData
{
    public float3 Value;
}

public struct HealthComponent : IComponentData
{
    public int Current;
    public int Maximum;
}

// System: Logic that operates on components
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class MovementSystem : SystemBase
{
    protected override void OnUpdate()
    {
        float deltaTime = Time.DeltaTime;

        // Operate on all entities with Transform and Velocity components
        Entities
            .WithAll<TransformComponent, VelocityComponent>()
            .ForEach((ref TransformComponent transform, in VelocityComponent velocity) =>
            {
                transform.Position += velocity.Value * deltaTime;
            })
            .ScheduleParallel();
    }
}

// Entity creation
Entity CreatePlayer(EntityManager entityManager)
{
    Entity player = entityManager.CreateEntity();

    entityManager.AddComponentData(player, new TransformComponent
    {
        Position = float3.zero,
        Rotation = quaternion.identity,
        Scale = new float3(1, 1, 1)
    });

    entityManager.AddComponentData(player, new VelocityComponent
    {
        Value = float3.zero
    });

    entityManager.AddComponentData(player, new HealthComponent
    {
        Current = 100,
        Maximum = 100
    });

    return player;
}
```

**Benefits**:
- ✅ Cache-friendly data layout (better performance)
- ✅ Easy parallelization
- ✅ Flexible entity definitions
- ✅ Clear separation of data and logic

**Drawbacks**:
- ❌ Steeper learning curve
- ❌ More complex debugging
- ❌ Requires different thinking from OOP

**Reference**:
- Unity DOTS documentation
- "Data-Oriented Design" by Richard Fabian
- GDC: "A Data-Oriented Approach to Using Component Systems"

---

### 2. Event System / Observer Pattern

**Problem**: Tight coupling between game systems

**Solution**: Decoupled communication through events

**When to Use**:
- UI updates in response to game state
- Achievement/quest systems
- Audio triggers
- Analytics tracking

**Implementation**:

```csharp
// ScriptableObject-based event system (Unity)
[CreateAssetMenu(menuName = "Events/Game Event")]
public class GameEvent : ScriptableObject
{
    private readonly HashSet<IGameEventListener> listeners = new HashSet<IGameEventListener>();

    public void Raise()
    {
        foreach (var listener in listeners)
            listener.OnEventRaised();
    }

    public void RegisterListener(IGameEventListener listener)
        => listeners.Add(listener);

    public void UnregisterListener(IGameEventListener listener)
        => listeners.Remove(listener);
}

public interface IGameEventListener
{
    void OnEventRaised();
}

// Typed events with parameters
[CreateAssetMenu(menuName = "Events/Int Event")]
public class IntGameEvent : ScriptableObject
{
    private event Action<int> OnEventRaised;

    public void Raise(int value) => OnEventRaised?.Invoke(value);
    public void RegisterListener(Action<int> listener) => OnEventRaised += listener;
    public void UnregisterListener(Action<int> listener) => OnEventRaised -= listener;
}

// Usage
public class PlayerHealth : MonoBehaviour
{
    [SerializeField] private IntGameEvent onHealthChanged;
    [SerializeField] private GameEvent onPlayerDied;

    private int currentHealth;

    public void TakeDamage(int amount)
    {
        currentHealth -= amount;
        onHealthChanged.Raise(currentHealth);

        if (currentHealth <= 0)
            onPlayerDied.Raise();
    }
}

public class HealthUI : MonoBehaviour
{
    [SerializeField] private IntGameEvent onHealthChanged;
    [SerializeField] private Text healthText;

    private void OnEnable()
    {
        onHealthChanged.RegisterListener(UpdateHealthDisplay);
    }

    private void OnDisable()
    {
        onHealthChanged.UnregisterListener(UpdateHealthDisplay);
    }

    private void UpdateHealthDisplay(int health)
    {
        healthText.text = $"Health: {health}";
    }
}
```

**Benefits**:
- ✅ Decoupled systems
- ✅ Easy to add new listeners
- ✅ Designer-friendly (ScriptableObjects)
- ✅ No dependencies between systems

**Drawbacks**:
- ❌ Can be harder to trace execution flow
- ❌ Potential performance cost with many listeners

**Reference**:
- Ryan Hipple (Unity): "Game Architecture with Scriptable Objects"
- "Design Patterns" - Gang of Four (Observer pattern)

---

### 3. Command Pattern

**Problem**: Need to undo/redo actions, replay inputs, or log player actions

**Solution**: Encapsulate actions as objects that can be executed, undone, and stored

**When to Use**:
- Undo/redo systems
- Input recording and replay
- Network input serialization
- Tutorial/replay systems

**Implementation**:

```csharp
// Command interface
public interface ICommand
{
    void Execute();
    void Undo();
}

// Concrete command
public class MoveCommand : ICommand
{
    private readonly Transform target;
    private readonly Vector3 direction;
    private readonly float distance;
    private Vector3 previousPosition;

    public MoveCommand(Transform target, Vector3 direction, float distance)
    {
        this.target = target;
        this.direction = direction;
        this.distance = distance;
    }

    public void Execute()
    {
        previousPosition = target.position;
        target.position += direction.normalized * distance;
    }

    public void Undo()
    {
        target.position = previousPosition;
    }
}

// Command manager
public class CommandManager
{
    private readonly Stack<ICommand> commandHistory = new Stack<ICommand>();
    private readonly Stack<ICommand> redoStack = new Stack<ICommand>();

    public void ExecuteCommand(ICommand command)
    {
        command.Execute();
        commandHistory.Push(command);
        redoStack.Clear();
    }

    public void Undo()
    {
        if (commandHistory.Count > 0)
        {
            ICommand command = commandHistory.Pop();
            command.Undo();
            redoStack.Push(command);
        }
    }

    public void Redo()
    {
        if (redoStack.Count > 0)
        {
            ICommand command = redoStack.Pop();
            command.Execute();
            commandHistory.Push(command);
        }
    }
}

// Input recording for replays
public class InputRecorder
{
    private readonly List<(ICommand command, float timestamp)> recording = new List<(ICommand, float)>();
    private float startTime;

    public void StartRecording()
    {
        recording.Clear();
        startTime = Time.time;
    }

    public void RecordCommand(ICommand command)
    {
        recording.Add((command, Time.time - startTime));
    }

    public IEnumerator PlaybackRecording()
    {
        float playbackStartTime = Time.time;

        foreach (var (command, timestamp) in recording)
        {
            float currentTime = Time.time - playbackStartTime;
            float waitTime = timestamp - currentTime;

            if (waitTime > 0)
                yield return new WaitForSeconds(waitTime);

            command.Execute();
        }
    }
}
```

**Benefits**:
- ✅ Undo/redo functionality
- ✅ Input replay for testing/tutorials
- ✅ Network input serialization
- ✅ Macro recording

**Drawbacks**:
- ❌ Memory overhead for command history
- ❌ Some actions difficult to undo

**Reference**:
- "Game Programming Patterns" - Robert Nystrom (Command chapter)
- GDC: "Replay Technology in Overwatch"

---

### 4. State Machine Pattern

**Problem**: Managing complex state transitions and behaviors

**Solution**: Explicit state objects with defined transitions

**When to Use**:
- Character controllers (idle, running, jumping, etc.)
- AI behavior management
- Game flow (menu → loading → gameplay → pause)
- Animation controllers

**Implementation**:

```csharp
// State interface
public interface IState
{
    void Enter();
    void Update();
    void FixedUpdate();
    void Exit();
}

// Concrete states
public class IdleState : IState
{
    private readonly PlayerController player;

    public IdleState(PlayerController player)
    {
        this.player = player;
    }

    public void Enter()
    {
        player.Animator.Play("Idle");
    }

    public void Update()
    {
        if (player.MoveInput.magnitude > 0.1f)
            player.StateMachine.TransitionTo(player.RunState);

        if (player.JumpInput && player.IsGrounded)
            player.StateMachine.TransitionTo(player.JumpState);
    }

    public void FixedUpdate() { }

    public void Exit() { }
}

public class RunState : IState
{
    private readonly PlayerController player;

    public RunState(PlayerController player)
    {
        this.player = player;
    }

    public void Enter()
    {
        player.Animator.Play("Run");
    }

    public void Update()
    {
        if (player.MoveInput.magnitude < 0.1f)
            player.StateMachine.TransitionTo(player.IdleState);

        if (player.JumpInput && player.IsGrounded)
            player.StateMachine.TransitionTo(player.JumpState);
    }

    public void FixedUpdate()
    {
        player.Rigidbody.MovePosition(
            player.transform.position + player.MoveInput * player.MoveSpeed * Time.fixedDeltaTime
        );
    }

    public void Exit() { }
}

// State machine
public class StateMachine
{
    private IState currentState;

    public void Initialize(IState startingState)
    {
        currentState = startingState;
        currentState.Enter();
    }

    public void TransitionTo(IState newState)
    {
        currentState.Exit();
        currentState = newState;
        currentState.Enter();
    }

    public void Update() => currentState?.Update();
    public void FixedUpdate() => currentState?.FixedUpdate();
}

// Usage in PlayerController
public class PlayerController : MonoBehaviour
{
    public StateMachine StateMachine { get; private set; }
    public IdleState IdleState { get; private set; }
    public RunState RunState { get; private set; }
    public JumpState JumpState { get; private set; }

    public Animator Animator { get; private set; }
    public Rigidbody Rigidbody { get; private set; }
    public Vector3 MoveInput { get; private set; }
    public bool JumpInput { get; private set; }
    public bool IsGrounded { get; private set; }
    public float MoveSpeed = 5f;

    private void Awake()
    {
        Animator = GetComponent<Animator>();
        Rigidbody = GetComponent<Rigidbody>();

        StateMachine = new StateMachine();
        IdleState = new IdleState(this);
        RunState = new RunState(this);
        JumpState = new JumpState(this);
    }

    private void Start()
    {
        StateMachine.Initialize(IdleState);
    }

    private void Update()
    {
        GatherInput();
        StateMachine.Update();
    }

    private void FixedUpdate()
    {
        CheckGrounded();
        StateMachine.FixedUpdate();
    }

    private void GatherInput()
    {
        MoveInput = new Vector3(
            Input.GetAxisRaw("Horizontal"),
            0f,
            Input.GetAxisRaw("Vertical")
        ).normalized;

        JumpInput = Input.GetButtonDown("Jump");
    }

    private void CheckGrounded()
    {
        IsGrounded = Physics.Raycast(transform.position, Vector3.down, 1.1f);
    }
}
```

**Benefits**:
- ✅ Clear state definitions
- ✅ Easy to debug and visualize
- ✅ Explicit transition logic
- ✅ Scalable to complex behaviors

**Drawbacks**:
- ❌ Can become verbose with many states
- ❌ Transitions can become complex

**Reference**:
- "Game Programming Patterns" - Robert Nystrom (State chapter)
- "AI for Games" - Ian Millington, John Funge

---

### 5. Object Pool Pattern

**Problem**: Frequent instantiation/destruction causes performance issues and garbage collection

**Solution**: Reuse objects instead of creating/destroying them

**When to Use**:
- Projectiles (bullets, arrows)
- Particles and VFX
- Enemies in wave-based games
- UI elements that appear/disappear frequently

**Implementation**:

```csharp
// Generic object pool
public class ObjectPool<T> where T : Component
{
    private readonly T prefab;
    private readonly int initialSize;
    private readonly Transform parent;
    private readonly Queue<T> availableObjects = new Queue<T>();
    private readonly HashSet<T> activeObjects = new HashSet<T>();

    public ObjectPool(T prefab, int initialSize = 10, Transform parent = null)
    {
        this.prefab = prefab;
        this.initialSize = initialSize;
        this.parent = parent;

        // Pre-populate pool
        for (int i = 0; i < initialSize; i++)
        {
            T obj = GameObject.Instantiate(prefab, parent);
            obj.gameObject.SetActive(false);
            availableObjects.Enqueue(obj);
        }
    }

    public T Get()
    {
        T obj;

        if (availableObjects.Count > 0)
        {
            obj = availableObjects.Dequeue();
        }
        else
        {
            // Pool exhausted, create new instance
            obj = GameObject.Instantiate(prefab, parent);
        }

        obj.gameObject.SetActive(true);
        activeObjects.Add(obj);
        return obj;
    }

    public void Return(T obj)
    {
        if (activeObjects.Remove(obj))
        {
            obj.gameObject.SetActive(false);
            availableObjects.Enqueue(obj);
        }
    }

    public void ReturnAll()
    {
        foreach (T obj in activeObjects)
        {
            obj.gameObject.SetActive(false);
            availableObjects.Enqueue(obj);
        }
        activeObjects.Clear();
    }

    public int ActiveCount => activeObjects.Count;
    public int AvailableCount => availableObjects.Count;
}

// Pool manager for multiple pools
public class PoolManager : MonoBehaviour
{
    private static PoolManager instance;
    public static PoolManager Instance
    {
        get
        {
            if (instance == null)
            {
                instance = FindObjectOfType<PoolManager>();
                if (instance == null)
                {
                    GameObject go = new GameObject("PoolManager");
                    instance = go.AddComponent<PoolManager>();
                }
            }
            return instance;
        }
    }

    [System.Serializable]
    public class PoolConfig
    {
        public GameObject prefab;
        public int initialSize = 10;
    }

    [SerializeField] private List<PoolConfig> poolConfigs;
    private Dictionary<string, ObjectPool<GameObject>> pools = new Dictionary<string, ObjectPool<GameObject>>();

    private void Awake()
    {
        instance = this;

        foreach (var config in poolConfigs)
        {
            CreatePool(config.prefab, config.initialSize);
        }
    }

    public void CreatePool(GameObject prefab, int initialSize)
    {
        string key = prefab.name;
        if (!pools.ContainsKey(key))
        {
            Transform poolParent = new GameObject($"Pool_{key}").transform;
            poolParent.SetParent(transform);

            pools[key] = new ObjectPool<GameObject>(
                prefab,
                initialSize,
                poolParent
            );
        }
    }

    public GameObject Spawn(GameObject prefab, Vector3 position, Quaternion rotation)
    {
        string key = prefab.name;

        if (!pools.ContainsKey(key))
            CreatePool(prefab, 10);

        GameObject obj = pools[key].Get();
        obj.transform.position = position;
        obj.transform.rotation = rotation;
        return obj;
    }

    public void Despawn(GameObject obj)
    {
        string key = obj.name.Replace("(Clone)", "").Trim();

        if (pools.TryGetValue(key, out var pool))
            pool.Return(obj);
        else
            Destroy(obj);
    }
}

// Auto-return to pool component
public class PooledObject : MonoBehaviour
{
    [SerializeField] private float lifetime = 5f;
    private float spawnTime;

    private void OnEnable()
    {
        spawnTime = Time.time;
    }

    private void Update()
    {
        if (Time.time - spawnTime >= lifetime)
        {
            PoolManager.Instance.Despawn(gameObject);
        }
    }
}
```

**Benefits**:
- ✅ Eliminates instantiation/destruction overhead
- ✅ Reduces garbage collection
- ✅ Predictable memory usage
- ✅ Better performance

**Drawbacks**:
- ❌ Objects must be carefully reset when returned
- ❌ Requires more upfront setup

**Reference**:
- "Game Programming Patterns" - Robert Nystrom (Object Pool chapter)
- Unity Manual: "Object Pooling"

---

### 6. Service Locator Pattern

**Problem**: Need global access to services without tight coupling

**Solution**: Centralized registry for service lookup

**When to Use**:
- Audio manager
- Save system
- Analytics
- Input manager
- Any singleton-style service

**Implementation**:

```csharp
// Service locator
public class ServiceLocator
{
    private static readonly Dictionary<Type, object> services = new Dictionary<Type, object>();

    public static void Register<T>(T service)
    {
        Type type = typeof(T);

        if (services.ContainsKey(type))
        {
            Debug.LogWarning($"Service of type {type} already registered. Replacing.");
            services[type] = service;
        }
        else
        {
            services.Add(type, service);
        }
    }

    public static T Get<T>()
    {
        Type type = typeof(T);

        if (services.TryGetValue(type, out object service))
        {
            return (T)service;
        }

        Debug.LogError($"Service of type {type} not found!");
        return default;
    }

    public static bool TryGet<T>(out T service)
    {
        Type type = typeof(T);

        if (services.TryGetValue(type, out object obj))
        {
            service = (T)obj;
            return true;
        }

        service = default;
        return false;
    }

    public static void Unregister<T>()
    {
        Type type = typeof(T);
        services.Remove(type);
    }

    public static void Clear()
    {
        services.Clear();
    }
}

// Service interface
public interface IAudioService
{
    void PlaySound(AudioClip clip);
    void PlayMusic(AudioClip clip);
    void StopMusic();
}

// Service implementation
public class AudioService : MonoBehaviour, IAudioService
{
    private AudioSource musicSource;
    private AudioSource sfxSource;

    private void Awake()
    {
        // Register this service
        ServiceLocator.Register<IAudioService>(this);

        musicSource = gameObject.AddComponent<AudioSource>();
        sfxSource = gameObject.AddComponent<AudioSource>();
    }

    private void OnDestroy()
    {
        ServiceLocator.Unregister<IAudioService>();
    }

    public void PlaySound(AudioClip clip)
    {
        sfxSource.PlayOneShot(clip);
    }

    public void PlayMusic(AudioClip clip)
    {
        musicSource.clip = clip;
        musicSource.loop = true;
        musicSource.Play();
    }

    public void StopMusic()
    {
        musicSource.Stop();
    }
}

// Usage
public class Player : MonoBehaviour
{
    [SerializeField] private AudioClip jumpSound;

    public void Jump()
    {
        // Get audio service and play sound
        var audioService = ServiceLocator.Get<IAudioService>();
        audioService.PlaySound(jumpSound);
    }
}
```

**Benefits**:
- ✅ Decoupled access to services
- ✅ Easy to swap implementations
- ✅ Testable (can inject mock services)
- ✅ Centralized service management

**Drawbacks**:
- ❌ Can hide dependencies
- ❌ Runtime errors if service not registered
- ❌ Global state

**Reference**:
- "Game Programming Patterns" - Robert Nystrom (Service Locator chapter)

---

## Additional Key Patterns

### 7. Update Method Pattern
Separate update logic from MonoBehaviour to avoid performance cost of Unity messages

### 8. Dirty Flag Pattern
Only recalculate values when underlying data changes

### 9. Flyweight Pattern
Share data between similar objects to reduce memory usage

### 10. Subclass Sandbox Pattern
Define behavior in base class, let subclasses combine them

---

## Architecture Anti-Patterns to Avoid

### ❌ God Classes
Classes that know too much and do too much

**Fix**: Use composition, single responsibility principle

### ❌ Spaghetti Code
Tangled dependencies and unclear flow

**Fix**: Use events, interfaces, and clear architecture

### ❌ Premature Optimization
Optimizing before profiling

**Fix**: Profile first, optimize hot paths

### ❌ Not Invented Here Syndrome
Rewriting everything instead of using proven solutions

**Fix**: Use middleware, packages, and proven patterns

---

## Recommended Architectures by Game Type

### Action/FPS Games
- **Core**: State machines for player, ECS for enemies
- **Networking**: Client prediction, authoritative server
- **Performance**: Object pooling, LOD systems

### RPG Games
- **Core**: Data-driven design with ScriptableObjects
- **Systems**: Event-driven quest/achievement systems
- **Save**: Command pattern for undo, serialization

### Strategy/Simulation
- **Core**: ECS for many entities
- **Performance**: Spatial partitioning, dirty flags
- **AI**: Utility AI, GOAP for complex decisions

### Multiplayer Games
- **Networking**: Lag compensation, server reconciliation
- **Anti-cheat**: Server authority, validation
- **Scalability**: Interest management, replication graph

---

## References

- **"Game Programming Patterns"** - Robert Nystrom (free online)
- **"Game Engine Architecture"** - Jason Gregory
- **Unity "Game Architecture with Scriptable Objects"** - Ryan Hipple (Unite talk)
- **Epic Games Lyra Starter Game** - Production-quality architecture example
- **Gaffer on Games** - Physics and networking architecture
- **GDC Vault** - Architecture talks from production games

---

**Version**: 1.0
**Last Updated**: 2025-11-19
