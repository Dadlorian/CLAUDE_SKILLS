using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Generic object pool for efficient object reuse.
/// Eliminates Instantiate/Destroy overhead and reduces garbage collection.
/// </summary>
/// <typeparam name="T">Component type to pool</typeparam>
public class ObjectPool<T> where T : Component
{
    private readonly T prefab;
    private readonly int initialSize;
    private readonly Transform parent;
    private readonly Queue<T> availableObjects = new Queue<T>();
    private readonly HashSet<T> activeObjects = new HashSet<T>();

    /// <summary>
    /// Create a new object pool.
    /// </summary>
    /// <param name="prefab">Prefab to instantiate</param>
    /// <param name="initialSize">Initial pool size</param>
    /// <param name="parent">Optional parent transform for organization</param>
    public ObjectPool(T prefab, int initialSize = 10, Transform parent = null)
    {
        this.prefab = prefab;
        this.initialSize = initialSize;
        this.parent = parent;

        // Pre-populate pool
        for (int i = 0; i < initialSize; i++)
        {
            T obj = Object.Instantiate(prefab, parent);
            obj.gameObject.SetActive(false);
            availableObjects.Enqueue(obj);
        }
    }

    /// <summary>
    /// Get an object from the pool.
    /// If pool is exhausted, creates a new instance.
    /// </summary>
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
            obj = Object.Instantiate(prefab, parent);
            Debug.LogWarning($"ObjectPool<{typeof(T).Name}> exhausted. Creating new instance. Consider increasing pool size.");
        }

        obj.gameObject.SetActive(true);
        activeObjects.Add(obj);

        // Notify pooled object it was spawned
        if (obj is IPoolable poolable)
        {
            poolable.OnSpawnFromPool();
        }

        return obj;
    }

    /// <summary>
    /// Return an object to the pool.
    /// </summary>
    public void Return(T obj)
    {
        if (!activeObjects.Remove(obj))
        {
            Debug.LogWarning($"Trying to return object {obj.name} that wasn't from this pool.");
            return;
        }

        // Notify pooled object it was despawned
        if (obj is IPoolable poolable)
        {
            poolable.OnReturnToPool();
        }

        obj.gameObject.SetActive(false);
        obj.transform.SetParent(parent);
        availableObjects.Enqueue(obj);
    }

    /// <summary>
    /// Return all active objects to the pool.
    /// </summary>
    public void ReturnAll()
    {
        // Copy to array to avoid modification during iteration
        T[] active = new T[activeObjects.Count];
        activeObjects.CopyTo(active);

        foreach (T obj in active)
        {
            Return(obj);
        }
    }

    /// <summary>
    /// Get number of active objects.
    /// </summary>
    public int ActiveCount => activeObjects.Count;

    /// <summary>
    /// Get number of available objects in pool.
    /// </summary>
    public int AvailableCount => availableObjects.Count;

    /// <summary>
    /// Get total pool capacity (active + available).
    /// </summary>
    public int TotalCount => activeObjects.Count + availableObjects.Count;

    /// <summary>
    /// Destroy all objects and clear pool.
    /// </summary>
    public void Clear()
    {
        // Destroy active objects
        foreach (T obj in activeObjects)
        {
            if (obj != null)
                Object.Destroy(obj.gameObject);
        }

        // Destroy available objects
        while (availableObjects.Count > 0)
        {
            T obj = availableObjects.Dequeue();
            if (obj != null)
                Object.Destroy(obj.gameObject);
        }

        activeObjects.Clear();
    }
}

/// <summary>
/// Interface for objects that need to know when they're spawned/despawned from pool.
/// </summary>
public interface IPoolable
{
    /// <summary>
    /// Called when object is spawned from pool.
    /// Use this to reset state, play effects, etc.
    /// </summary>
    void OnSpawnFromPool();

    /// <summary>
    /// Called when object is returned to pool.
    /// Use this to clean up, stop effects, etc.
    /// </summary>
    void OnReturnToPool();
}

/// <summary>
/// Example pooled bullet that auto-returns after lifetime.
/// </summary>
public class PooledBullet : MonoBehaviour, IPoolable
{
    [SerializeField] private float lifetime = 3f;
    [SerializeField] private float speed = 20f;
    [SerializeField] private ParticleSystem hitEffect;

    private float spawnTime;
    private Rigidbody rb;
    private ObjectPool<PooledBullet> pool;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    public void Initialize(ObjectPool<PooledBullet> objectPool)
    {
        pool = objectPool;
    }

    public void OnSpawnFromPool()
    {
        spawnTime = Time.time;
        rb.velocity = transform.forward * speed;
    }

    public void OnReturnToPool()
    {
        rb.velocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
    }

    private void Update()
    {
        // Auto-return after lifetime
        if (Time.time - spawnTime >= lifetime)
        {
            pool?.Return(this);
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        // Play hit effect
        if (hitEffect != null)
        {
            Instantiate(hitEffect, transform.position, Quaternion.identity);
        }

        // Return to pool
        pool?.Return(this);
    }
}
