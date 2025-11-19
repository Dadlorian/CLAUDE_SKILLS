# Setting Up Object Pooling in Unity

## Why Object Pooling?

- **Problem**: Instantiate() and Destroy() are expensive operations
- **Solution**: Reuse objects instead of creating/destroying them
- **Use Cases**: Bullets, particles, enemies in wave-based games, UI elements

## Step-by-Step Implementation

### Step 1: Create Generic Pool Class

```csharp
using System.Collections.Generic;
using UnityEngine;

public class ObjectPool<T> where T : Component
{
    private readonly T prefab;
    private readonly Queue<T> objects = new Queue<T>();
    private readonly Transform parent;

    public ObjectPool(T prefab, int initialSize = 10, Transform parent = null)
    {
        this.prefab = prefab;
        this.parent = parent;

        // Pre-populate pool
        for (int i = 0; i < initialSize; i++)
        {
            T obj = Object.Instantiate(prefab, parent);
            obj.gameObject.SetActive(false);
            objects.Enqueue(obj);
        }
    }

    public T Get()
    {
        if (objects.Count > 0)
        {
            T obj = objects.Dequeue();
            obj.gameObject.SetActive(true);
            return obj;
        }

        // Pool exhausted, create new instance
        return Object.Instantiate(prefab, parent);
    }

    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        obj.transform.SetParent(parent);
        objects.Enqueue(obj);
    }
}
```

### Step 2: Create Pool Manager

```csharp
using UnityEngine;
using System.Collections.Generic;

public class PoolManager : MonoBehaviour
{
    public static PoolManager Instance { get; private set; }

    [System.Serializable]
    public class Pool
    {
        public string tag;
        public GameObject prefab;
        public int size;
    }

    [SerializeField] private List<Pool> pools;
    private Dictionary<string, Queue<GameObject>> poolDictionary;

    private void Awake()
    {
        Instance = this;
        poolDictionary = new Dictionary<string, Queue<GameObject>>();

        foreach (Pool pool in pools)
        {
            Queue<GameObject> objectPool = new Queue<GameObject>();

            for (int i = 0; i < pool.size; i++)
            {
                GameObject obj = Instantiate(pool.prefab);
                obj.SetActive(false);
                objectPool.Enqueue(obj);
            }

            poolDictionary.Add(pool.tag, objectPool);
        }
    }

    public GameObject SpawnFromPool(string tag, Vector3 position, Quaternion rotation)
    {
        if (!poolDictionary.ContainsKey(tag))
        {
            Debug.LogWarning($"Pool with tag {tag} doesn't exist.");
            return null;
        }

        GameObject objectToSpawn = poolDictionary[tag].Dequeue();

        objectToSpawn.SetActive(true);
        objectToSpawn.transform.position = position;
        objectToSpawn.transform.rotation = rotation;

        poolDictionary[tag].Enqueue(objectToSpawn);

        return objectToSpawn;
    }
}
```

### Step 3: Using the Pool

```csharp
public class Gun : MonoBehaviour
{
    [SerializeField] private GameObject bulletPrefab;
    [SerializeField] private Transform firePoint;
    [SerializeField] private float fireRate = 0.1f;

    private float nextFireTime;
    private ObjectPool<Bullet> bulletPool;

    private void Awake()
    {
        // Create pool for bullets
        bulletPool = new ObjectPool<Bullet>(
            bulletPrefab.GetComponent<Bullet>(),
            initialSize: 30
        );
    }

    private void Update()
    {
        if (Input.GetButton("Fire1") && Time.time >= nextFireTime)
        {
            Fire();
            nextFireTime = Time.time + fireRate;
        }
    }

    private void Fire()
    {
        // Get bullet from pool
        Bullet bullet = bulletPool.Get();
        bullet.transform.position = firePoint.position;
        bullet.transform.rotation = firePoint.rotation;

        // Initialize bullet (custom logic)
        bullet.OnSpawn(this);
    }

    public void ReturnBullet(Bullet bullet)
    {
        bulletPool.Return(bullet);
    }
}
```

### Step 4: Auto-Return to Pool

```csharp
public class Bullet : MonoBehaviour
{
    [SerializeField] private float lifetime = 3f;
    private float spawnTime;
    private Gun owner;

    public void OnSpawn(Gun gun)
    {
        owner = gun;
        spawnTime = Time.time;
        GetComponent<Rigidbody>().velocity = transform.forward * 20f;
    }

    private void Update()
    {
        if (Time.time - spawnTime >= lifetime)
        {
            ReturnToPool();
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        // Hit something, return to pool
        ReturnToPool();
    }

    private void ReturnToPool()
    {
        owner.ReturnBullet(this);
    }
}
```

## Performance Comparison

**Without Pooling** (spawning 100 bullets):
- Instantiate: ~50ms total
- Destroy: ~30ms total
- GC pressure: High

**With Pooling** (spawning 100 bullets):
- Get from pool: ~0.5ms total
- Return to pool: ~0.3ms total
- GC pressure: Near zero

## Best Practices

✅ Pre-populate pools on load (not during gameplay)
✅ Set reasonable initial sizes (avoid pool exhaustion)
✅ Parent pooled objects to keep hierarchy clean
✅ Reset object state when returning to pool
✅ Use for objects spawned/destroyed frequently

❌ Don't pool objects that are rarely spawned
❌ Don't forget to return objects to pool
❌ Don't modify pooled object prefabs at runtime

## Testing

```csharp
[Test]
public void ObjectPool_ReusesObjects()
{
    // Arrange
    GameObject prefab = new GameObject();
    ObjectPool<Transform> pool = new ObjectPool<Transform>(
        prefab.GetComponent<Transform>(),
        initialSize: 5
    );

    // Act
    Transform obj1 = pool.Get();
    pool.Return(obj1);
    Transform obj2 = pool.Get();

    // Assert
    Assert.AreEqual(obj1, obj2, "Pool should reuse objects");

    Object.DestroyImmediate(prefab);
}
```

## References

- Unity Manual: Object Pooling
- "Game Programming Patterns" - Robert Nystrom (Object Pool chapter)
