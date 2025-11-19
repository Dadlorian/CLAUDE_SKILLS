using UnityEngine;
using UnityEngine.Events;

/// <summary>
/// Production-ready health system with damage, healing, and death events.
/// </summary>
public class HealthSystem : MonoBehaviour
{
    [Header("Settings")]
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private bool invulnerable = false;
    [SerializeField] private float invulnerabilityDuration = 1f;

    [Header("Events")]
    public UnityEvent<int> OnHealthChanged;
    public UnityEvent OnDeath;
    public UnityEvent<int, GameObject> OnDamageTaken;
    public UnityEvent<int> OnHealed;

    public int CurrentHealth { get; private set; }
    public int MaxHealth => maxHealth;
    public bool IsAlive => CurrentHealth > 0;
    public float HealthPercentage => (float)CurrentHealth / maxHealth;

    private float invulnerabilityTimer;

    private void Awake()
    {
        CurrentHealth = maxHealth;
    }

    private void Update()
    {
        if (invulnerabilityTimer > 0)
            invulnerabilityTimer -= Time.deltaTime;
    }

    public void TakeDamage(int amount, GameObject source = null)
    {
        if (!IsAlive || invulnerable || invulnerabilityTimer > 0)
            return;

        amount = Mathf.Max(0, amount);
        CurrentHealth = Mathf.Max(0, CurrentHealth - amount);

        OnHealthChanged?.Invoke(CurrentHealth);
        OnDamageTaken?.Invoke(amount, source);

        if (CurrentHealth == 0)
        {
            Die();
        }
        else
        {
            invulnerabilityTimer = invulnerabilityDuration;
        }
    }

    public void Heal(int amount)
    {
        if (!IsAlive)
            return;

        amount = Mathf.Max(0, amount);
        int oldHealth = CurrentHealth;
        CurrentHealth = Mathf.Min(maxHealth, CurrentHealth + amount);

        if (CurrentHealth != oldHealth)
        {
            OnHealthChanged?.Invoke(CurrentHealth);
            OnHealed?.Invoke(amount);
        }
    }

    public void SetHealth(int health)
    {
        CurrentHealth = Mathf.Clamp(health, 0, maxHealth);
        OnHealthChanged?.Invoke(CurrentHealth);

        if (CurrentHealth == 0)
            Die();
    }

    private void Die()
    {
        OnDeath?.Invoke();
    }

    public void Revive(int health = -1)
    {
        if (health == -1)
            health = maxHealth;

        CurrentHealth = Mathf.Clamp(health, 1, maxHealth);
        OnHealthChanged?.Invoke(CurrentHealth);
    }
}
