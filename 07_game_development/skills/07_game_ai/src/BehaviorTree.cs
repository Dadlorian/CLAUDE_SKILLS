using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Production-ready Behavior Tree implementation for game AI.
/// Modular, reusable, and easy to debug.
/// </summary>
namespace GameAI.BehaviorTree
{
    // ========================================
    // Core Node Types
    // ========================================

    public enum NodeStatus
    {
        Success,
        Failure,
        Running
    }

    public abstract class Node
    {
        public abstract NodeStatus Tick(AIContext context);

        public virtual void Reset() { }
    }

    // ========================================
    // Composite Nodes
    // ========================================

    /// <summary>
    /// Executes children in sequence. Fails if any child fails.
    /// </summary>
    public class Sequence : Node
    {
        private List<Node> children = new List<Node>();
        private int currentChild = 0;

        public Sequence(params Node[] nodes)
        {
            children.AddRange(nodes);
        }

        public override NodeStatus Tick(AIContext context)
        {
            while (currentChild < children.Count)
            {
                NodeStatus status = children[currentChild].Tick(context);

                if (status == NodeStatus.Failure)
                {
                    Reset();
                    return NodeStatus.Failure;
                }

                if (status == NodeStatus.Running)
                    return NodeStatus.Running;

                // Success, move to next child
                currentChild++;
            }

            // All children succeeded
            Reset();
            return NodeStatus.Success;
        }

        public override void Reset()
        {
            currentChild = 0;
            foreach (var child in children)
                child.Reset();
        }
    }

    /// <summary>
    /// Executes children in order. Succeeds if any child succeeds.
    /// </summary>
    public class Selector : Node
    {
        private List<Node> children = new List<Node>();
        private int currentChild = 0;

        public Selector(params Node[] nodes)
        {
            children.AddRange(nodes);
        }

        public override NodeStatus Tick(AIContext context)
        {
            while (currentChild < children.Count)
            {
                NodeStatus status = children[currentChild].Tick(context);

                if (status == NodeStatus.Success)
                {
                    Reset();
                    return NodeStatus.Success;
                }

                if (status == NodeStatus.Running)
                    return NodeStatus.Running;

                // Failed, try next child
                currentChild++;
            }

            // All children failed
            Reset();
            return NodeStatus.Failure;
        }

        public override void Reset()
        {
            currentChild = 0;
            foreach (var child in children)
                child.Reset();
        }
    }

    /// <summary>
    /// Executes all children in parallel.
    /// </summary>
    public class Parallel : Node
    {
        private List<Node> children = new List<Node>();
        private int successThreshold;

        public Parallel(int successThreshold, params Node[] nodes)
        {
            this.successThreshold = successThreshold;
            children.AddRange(nodes);
        }

        public override NodeStatus Tick(AIContext context)
        {
            int successCount = 0;
            int failureCount = 0;

            foreach (var child in children)
            {
                NodeStatus status = child.Tick(context);

                if (status == NodeStatus.Success)
                    successCount++;
                else if (status == NodeStatus.Failure)
                    failureCount++;
            }

            if (successCount >= successThreshold)
                return NodeStatus.Success;

            if (failureCount > children.Count - successThreshold)
                return NodeStatus.Failure;

            return NodeStatus.Running;
        }
    }

    // ========================================
    // Decorator Nodes
    // ========================================

    /// <summary>
    /// Inverts the result of child node.
    /// </summary>
    public class Inverter : Node
    {
        private Node child;

        public Inverter(Node child)
        {
            this.child = child;
        }

        public override NodeStatus Tick(AIContext context)
        {
            NodeStatus status = child.Tick(context);

            if (status == NodeStatus.Success)
                return NodeStatus.Failure;
            else if (status == NodeStatus.Failure)
                return NodeStatus.Success;

            return status; // Running stays running
        }
    }

    /// <summary>
    /// Repeats child node N times or until failure.
    /// </summary>
    public class Repeater : Node
    {
        private Node child;
        private int repeatCount;
        private int currentCount = 0;

        public Repeater(Node child, int repeatCount = -1)
        {
            this.child = child;
            this.repeatCount = repeatCount; // -1 = infinite
        }

        public override NodeStatus Tick(AIContext context)
        {
            while (repeatCount == -1 || currentCount < repeatCount)
            {
                NodeStatus status = child.Tick(context);

                if (status == NodeStatus.Running)
                    return NodeStatus.Running;

                if (status == NodeStatus.Failure)
                {
                    Reset();
                    return NodeStatus.Failure;
                }

                currentCount++;
                child.Reset();
            }

            Reset();
            return NodeStatus.Success;
        }

        public override void Reset()
        {
            currentCount = 0;
            child.Reset();
        }
    }

    // ========================================
    // Leaf Nodes (Actions & Conditions)
    // ========================================

    /// <summary>
    /// Condition node that checks a predicate.
    /// </summary>
    public class Condition : Node
    {
        private System.Func<AIContext, bool> predicate;

        public Condition(System.Func<AIContext, bool> predicate)
        {
            this.predicate = predicate;
        }

        public override NodeStatus Tick(AIContext context)
        {
            return predicate(context) ? NodeStatus.Success : NodeStatus.Failure;
        }
    }

    /// <summary>
    /// Action node that performs a task.
    /// </summary>
    public class Action : Node
    {
        private System.Func<AIContext, NodeStatus> action;

        public Action(System.Func<AIContext, NodeStatus> action)
        {
            this.action = action;
        }

        public override NodeStatus Tick(AIContext context)
        {
            return action(context);
        }
    }

    // ========================================
    // AI Context
    // ========================================

    /// <summary>
    /// Blackboard for sharing data between nodes.
    /// </summary>
    public class AIContext
    {
        private Dictionary<string, object> data = new Dictionary<string, object>();
        public GameObject Agent { get; set; }

        public void Set<T>(string key, T value)
        {
            data[key] = value;
        }

        public T Get<T>(string key, T defaultValue = default)
        {
            if (data.TryGetValue(key, out object value) && value is T typedValue)
                return typedValue;
            return defaultValue;
        }

        public bool Has(string key) => data.ContainsKey(key);

        public void Clear() => data.Clear();
    }

    // ========================================
    // Behavior Tree Component
    // ========================================

    public class BehaviorTreeAgent : MonoBehaviour
    {
        [Header("Update Settings")]
        [SerializeField] private float tickInterval = 0.1f; // 10 ticks per second

        private Node rootNode;
        private AIContext context;
        private float nextTickTime;

        protected virtual void Awake()
        {
            context = new AIContext();
            context.Agent = gameObject;

            rootNode = BuildTree();
        }

        protected virtual void Update()
        {
            if (Time.time >= nextTickTime)
            {
                rootNode.Tick(context);
                nextTickTime = Time.time + tickInterval;
            }
        }

        /// <summary>
        /// Override this to build your behavior tree.
        /// </summary>
        protected virtual Node BuildTree()
        {
            // Example tree: Patrol and attack if enemy seen
            return new Selector(
                new Sequence(
                    new Condition(ctx => ctx.Get<GameObject>("Enemy") != null),
                    new Action(ctx => AttackEnemy(ctx))
                ),
                new Action(ctx => Patrol(ctx))
            );
        }

        // Example actions
        protected NodeStatus AttackEnemy(AIContext ctx)
        {
            GameObject enemy = ctx.Get<GameObject>("Enemy");
            if (enemy == null)
                return NodeStatus.Failure;

            // Move towards enemy
            Vector3 direction = (enemy.transform.position - transform.position).normalized;
            transform.position += direction * 3f * Time.deltaTime;

            // Check if in attack range
            if (Vector3.Distance(transform.position, enemy.transform.position) < 2f)
            {
                // Perform attack
                Debug.Log($"{gameObject.name} attacks {enemy.name}!");
                return NodeStatus.Success;
            }

            return NodeStatus.Running;
        }

        protected NodeStatus Patrol(AIContext ctx)
        {
            // Simple patrol logic
            if (!ctx.Has("PatrolTarget"))
            {
                Vector3 randomPoint = transform.position + Random.insideUnitSphere * 10f;
                randomPoint.y = transform.position.y;
                ctx.Set("PatrolTarget", randomPoint);
            }

            Vector3 target = ctx.Get<Vector3>("PatrolTarget");
            Vector3 direction = (target - transform.position).normalized;
            transform.position += direction * 2f * Time.deltaTime;

            if (Vector3.Distance(transform.position, target) < 0.5f)
            {
                ctx.Set("PatrolTarget", null); // Reached target
                return NodeStatus.Success;
            }

            return NodeStatus.Running;
        }

        #region Debug

        private void OnDrawGizmosSelected()
        {
            if (context != null && context.Has("PatrolTarget"))
            {
                Gizmos.color = Color.blue;
                Gizmos.DrawLine(transform.position, context.Get<Vector3>("PatrolTarget"));
                Gizmos.DrawWireSphere(context.Get<Vector3>("PatrolTarget"), 0.5f);
            }
        }

        #endregion
    }
}
