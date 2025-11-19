using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// A* pathfinding implementation for grid-based and graph-based navigation.
/// Optimized with binary heap and heuristic tuning.
/// </summary>
namespace GameAI.Pathfinding
{
    public class AStarPathfinder
    {
        private class Node : System.IComparable<Node>
        {
            public Vector2Int Position;
            public Node Parent;
            public float GCost; // Distance from start
            public float HCost; // Heuristic distance to goal
            public float FCost => GCost + HCost;

            public int CompareTo(Node other)
            {
                int compare = FCost.CompareTo(other.FCost);
                if (compare == 0)
                    compare = HCost.CompareTo(other.HCost);
                return compare;
            }
        }

        private int gridWidth;
        private int gridHeight;
        private bool[,] walkable; // true = walkable, false = obstacle

        public AStarPathfinder(int width, int height)
        {
            gridWidth = width;
            gridHeight = height;
            walkable = new bool[width, height];

            // Initialize all cells as walkable
            for (int x = 0; x < width; x++)
                for (int y = 0; y < height; y++)
                    walkable[x, y] = true;
        }

        /// <summary>
        /// Set whether a cell is walkable.
        /// </summary>
        public void SetWalkable(int x, int y, bool isWalkable)
        {
            if (IsValidPosition(x, y))
                walkable[x, y] = isWalkable;
        }

        /// <summary>
        /// Find path from start to goal using A* algorithm.
        /// </summary>
        public List<Vector2Int> FindPath(Vector2Int start, Vector2Int goal, bool allowDiagonal = true)
        {
            if (!IsValidPosition(start) || !IsValidPosition(goal))
                return null;

            if (!IsWalkable(goal))
                return null; // Goal is not walkable

            // Priority queue for open set (nodes to evaluate)
            MinHeap<Node> openSet = new MinHeap<Node>();
            HashSet<Vector2Int> closedSet = new HashSet<Vector2Int>();

            Node startNode = new Node
            {
                Position = start,
                GCost = 0,
                HCost = Heuristic(start, goal)
            };

            openSet.Add(startNode);

            while (openSet.Count > 0)
            {
                // Get node with lowest F cost
                Node current = openSet.RemoveFirst();

                // Reached goal
                if (current.Position == goal)
                    return ReconstructPath(current);

                closedSet.Add(current.Position);

                // Check all neighbors
                foreach (Vector2Int neighborPos in GetNeighbors(current.Position, allowDiagonal))
                {
                    if (closedSet.Contains(neighborPos))
                        continue; // Already evaluated

                    if (!IsWalkable(neighborPos))
                        continue; // Obstacle

                    // Calculate cost to neighbor
                    float tentativeGCost = current.GCost + Distance(current.Position, neighborPos);

                    // Create neighbor node
                    Node neighbor = new Node
                    {
                        Position = neighborPos,
                        Parent = current,
                        GCost = tentativeGCost,
                        HCost = Heuristic(neighborPos, goal)
                    };

                    // Check if this path to neighbor is better
                    bool inOpenSet = openSet.Contains(node => node.Position == neighborPos);

                    if (!inOpenSet || tentativeGCost < neighbor.GCost)
                    {
                        if (inOpenSet)
                            openSet.Remove(node => node.Position == neighborPos);

                        openSet.Add(neighbor);
                    }
                }
            }

            // No path found
            return null;
        }

        /// <summary>
        /// Heuristic function (Manhattan distance for grid, can be switched to Euclidean)
        /// </summary>
        private float Heuristic(Vector2Int a, Vector2Int b)
        {
            // Manhattan distance (good for 4-directional movement)
            // return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y);

            // Euclidean distance (better for 8-directional movement)
            int dx = a.x - b.x;
            int dy = a.y - b.y;
            return Mathf.Sqrt(dx * dx + dy * dy);
        }

        /// <summary>
        /// Distance between adjacent cells.
        /// </summary>
        private float Distance(Vector2Int a, Vector2Int b)
        {
            int dx = Mathf.Abs(a.x - b.x);
            int dy = Mathf.Abs(a.y - b.y);

            // Diagonal movement costs more (sqrt(2) ≈ 1.414)
            if (dx == 1 && dy == 1)
                return 1.414f;

            return 1.0f;
        }

        /// <summary>
        /// Get valid neighbors of a position.
        /// </summary>
        private List<Vector2Int> GetNeighbors(Vector2Int pos, bool allowDiagonal)
        {
            List<Vector2Int> neighbors = new List<Vector2Int>();

            // Cardinal directions
            AddNeighbor(neighbors, pos.x + 1, pos.y); // Right
            AddNeighbor(neighbors, pos.x - 1, pos.y); // Left
            AddNeighbor(neighbors, pos.x, pos.y + 1); // Up
            AddNeighbor(neighbors, pos.x, pos.y - 1); // Down

            // Diagonal directions
            if (allowDiagonal)
            {
                // Only allow diagonal if both adjacent cardinals are walkable
                if (IsWalkable(pos.x + 1, pos.y) && IsWalkable(pos.x, pos.y + 1))
                    AddNeighbor(neighbors, pos.x + 1, pos.y + 1); // Up-Right

                if (IsWalkable(pos.x - 1, pos.y) && IsWalkable(pos.x, pos.y + 1))
                    AddNeighbor(neighbors, pos.x - 1, pos.y + 1); // Up-Left

                if (IsWalkable(pos.x + 1, pos.y) && IsWalkable(pos.x, pos.y - 1))
                    AddNeighbor(neighbors, pos.x + 1, pos.y - 1); // Down-Right

                if (IsWalkable(pos.x - 1, pos.y) && IsWalkable(pos.x, pos.y - 1))
                    AddNeighbor(neighbors, pos.x - 1, pos.y - 1); // Down-Left
            }

            return neighbors;
        }

        private void AddNeighbor(List<Vector2Int> neighbors, int x, int y)
        {
            if (IsValidPosition(x, y))
                neighbors.Add(new Vector2Int(x, y));
        }

        /// <summary>
        /// Reconstruct path from goal to start.
        /// </summary>
        private List<Vector2Int> ReconstructPath(Node goalNode)
        {
            List<Vector2Int> path = new List<Vector2Int>();
            Node current = goalNode;

            while (current != null)
            {
                path.Add(current.Position);
                current = current.Parent;
            }

            path.Reverse();
            return path;
        }

        private bool IsValidPosition(Vector2Int pos)
        {
            return IsValidPosition(pos.x, pos.y);
        }

        private bool IsValidPosition(int x, int y)
        {
            return x >= 0 && x < gridWidth && y >= 0 && y < gridHeight;
        }

        private bool IsWalkable(Vector2Int pos)
        {
            return IsWalkable(pos.x, pos.y);
        }

        private bool IsWalkable(int x, int y)
        {
            return IsValidPosition(x, y) && walkable[x, y];
        }
    }

    // ========================================
    // Min Heap (Priority Queue)
    // ========================================

    public class MinHeap<T> where T : System.IComparable<T>
    {
        private List<T> items = new List<T>();

        public int Count => items.Count;

        public void Add(T item)
        {
            items.Add(item);
            HeapifyUp(items.Count - 1);
        }

        public T RemoveFirst()
        {
            if (items.Count == 0)
                throw new System.InvalidOperationException("Heap is empty");

            T first = items[0];
            items[0] = items[items.Count - 1];
            items.RemoveAt(items.Count - 1);

            if (items.Count > 0)
                HeapifyDown(0);

            return first;
        }

        public bool Contains(System.Func<T, bool> predicate)
        {
            foreach (T item in items)
                if (predicate(item))
                    return true;
            return false;
        }

        public void Remove(System.Func<T, bool> predicate)
        {
            for (int i = 0; i < items.Count; i++)
            {
                if (predicate(items[i]))
                {
                    items[i] = items[items.Count - 1];
                    items.RemoveAt(items.Count - 1);
                    HeapifyDown(i);
                    return;
                }
            }
        }

        private void HeapifyUp(int index)
        {
            while (index > 0)
            {
                int parentIndex = (index - 1) / 2;
                if (items[index].CompareTo(items[parentIndex]) >= 0)
                    break;

                Swap(index, parentIndex);
                index = parentIndex;
            }
        }

        private void HeapifyDown(int index)
        {
            while (true)
            {
                int leftChild = index * 2 + 1;
                int rightChild = index * 2 + 2;
                int smallest = index;

                if (leftChild < items.Count && items[leftChild].CompareTo(items[smallest]) < 0)
                    smallest = leftChild;

                if (rightChild < items.Count && items[rightChild].CompareTo(items[smallest]) < 0)
                    smallest = rightChild;

                if (smallest == index)
                    break;

                Swap(index, smallest);
                index = smallest;
            }
        }

        private void Swap(int i, int j)
        {
            T temp = items[i];
            items[i] = items[j];
            items[j] = temp;
        }
    }

    // ========================================
    // Example Usage Component
    // ========================================

    public class PathfindingExample : MonoBehaviour
    {
        [SerializeField] private int gridWidth = 20;
        [SerializeField] private int gridHeight = 20;
        [SerializeField] private Transform startMarker;
        [SerializeField] private Transform goalMarker;

        private AStarPathfinder pathfinder;
        private List<Vector2Int> currentPath;

        private void Start()
        {
            pathfinder = new AStarPathfinder(gridWidth, gridHeight);

            // Add some obstacles (example)
            for (int x = 5; x < 15; x++)
                pathfinder.SetWalkable(x, 10, false);
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Space))
            {
                Vector2Int start = WorldToGrid(startMarker.position);
                Vector2Int goal = WorldToGrid(goalMarker.position);

                currentPath = pathfinder.FindPath(start, goal, allowDiagonal: true);

                if (currentPath != null)
                    Debug.Log($"Path found with {currentPath.Count} steps");
                else
                    Debug.Log("No path found");
            }
        }

        private Vector2Int WorldToGrid(Vector3 worldPos)
        {
            return new Vector2Int(Mathf.RoundToInt(worldPos.x), Mathf.RoundToInt(worldPos.z));
        }

        private Vector3 GridToWorld(Vector2Int gridPos)
        {
            return new Vector3(gridPos.x, 0, gridPos.y);
        }

        private void OnDrawGizmos()
        {
            if (currentPath != null)
            {
                Gizmos.color = Color.green;
                for (int i = 0; i < currentPath.Count - 1; i++)
                {
                    Vector3 from = GridToWorld(currentPath[i]);
                    Vector3 to = GridToWorld(currentPath[i + 1]);
                    Gizmos.DrawLine(from, to);
                    Gizmos.DrawWireSphere(from, 0.2f);
                }
            }
        }
    }
}
