# State Machines for AI Guide

## Finite State Machine (FSM)

### Basic Implementation
```csharp
public enum AIState
{
    Idle,
    Patrol,
    Chase,
    Attack,
    Retreat
}

public class AIStateMachine : MonoBehaviour
{
    private AIState currentState = AIState.Idle;
    private GameObject target;

    void Update()
    {
        switch (currentState)
        {
            case AIState.Idle:
                UpdateIdle();
                break;
            case AIState.Patrol:
                UpdatePatrol();
                break;
            case AIState.Chase:
                UpdateChase();
                break;
            case AIState.Attack:
                UpdateAttack();
                break;
            case AIState.Retreat:
                UpdateRetreat();
                break;
        }
    }

    void UpdateIdle()
    {
        // Look for target
        target = FindNearestEnemy();

        if (target != null)
            TransitionTo(AIState.Chase);
        else if (Random.value < 0.01f)
            TransitionTo(AIState.Patrol);
    }

    void UpdateChase()
    {
        if (target == null)
        {
            TransitionTo(AIState.Idle);
            return;
        }

        float distance = Vector3.Distance(transform.position, target.transform.position);

        if (distance < attackRange)
            TransitionTo(AIState.Attack);
        else if (distance > 20f)
            TransitionTo(AIState.Idle);
        else
            MoveTowards(target.transform.position);
    }

    void TransitionTo(AIState newState)
    {
        ExitState(currentState);
        currentState = newState;
        EnterState(newState);
    }

    void EnterState(AIState state)
    {
        Debug.Log($"Entering {state}");
        // State-specific setup
    }

    void ExitState(AIState state)
    {
        // State-specific cleanup
    }
}
```

## Hierarchical FSM

```csharp
public class HierarchicalFSM
{
    private State currentState;
    private State previousState;

    public void Update()
    {
        currentState?.Update();
    }

    public void TransitionTo(State newState)
    {
        currentState?.Exit();
        previousState = currentState;
        currentState = newState;
        currentState?.Enter();
    }
}

public abstract class State
{
    protected HierarchicalFSM subStateMachine;

    public virtual void Enter() { }
    public virtual void Update() { }
    public virtual void Exit() { }
}

// Example: Combat state has sub-states
public class CombatState : State
{
    public override void Enter()
    {
        subStateMachine = new HierarchicalFSM();
        subStateMachine.TransitionTo(new MeleeAttackState());
    }

    public override void Update()
    {
        subStateMachine.Update();
    }
}
```

## Advantages
✅ Simple to understand
✅ Easy to visualize
✅ Deterministic behavior
✅ Clear state transitions

## Disadvantages
❌ Can become complex with many states
❌ Doesn't handle uncertainty well
❌ Hard to share behaviors across states

## When to Use
- Clear, distinct behaviors
- Predictable transitions
- Simple AI (< 10 states)

## Alternatives
- **Behavior Trees**: More modular
- **Utility AI**: Handles uncertainty
- **GOAP**: For complex planning
