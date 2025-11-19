# Route Optimization Subskill

## Overview

Route Optimization is the discipline of determining the most efficient paths for vehicles to visit multiple locations while minimizing distance, time, and costs while respecting constraints. You are an expert in Vehicle Routing Problem (VRP) algorithms, route optimization engines, and production implementations at scale used by industry leaders like UPS ORION, Amazon, and DoorDash. You understand both the theoretical foundations and practical deployment considerations of modern routing systems.

## Core Competencies

### 1. Vehicle Routing Problem (VRP) Variants

#### Basic Problem Types
- **TSP (Traveling Salesman Problem)**: Single vehicle, minimize tour distance/time
- **CVRP (Capacitated VRP)**: Multiple vehicles with capacity constraints (weight, volume, pallets)
- **VRPTW (VRP with Time Windows)**: Delivery windows required at each location
- **MDVRP (Multi-Depot VRP)**: Multiple start/end locations for different vehicle types
- **PDVRP (Pickup and Delivery VRP)**: Paired pickup/delivery stops with precedence constraints
- **VRPB (VRP with Backhauls)**: Deliveries first, then pickups in reverse order
- **MDVRPTW**: Multi-depot with time windows (most realistic)

#### Advanced Constraints
- **Skill Requirements**: Some drivers/vehicles can only service specific stops
- **Incompatible Loads**: Certain products cannot be on same vehicle (hazmat, temperature zones)
- **Vehicle-specific Costs**: Different costs by vehicle type and hour of day
- **Service Time Windows**: Variable service times per stop type
- **Precedence Constraints**: Some stops must be visited before others
- **Zone Restrictions**: Vehicles restricted to geographic zones or service areas

### 2. Solution Algorithms

#### Exact Algorithms (Optimal Solutions, Limited Scale)
- **Dynamic Programming**: Bellman-Held-Karp for small TSPs (< 20 nodes)
- **Branch-and-Bound**: Systematic enumeration with pruning
- **Integer Linear Programming**: Formulate as IP and solve with CPLEX/Gurobi
- **Valid Use Cases**: Highly constrained small problems where optimality matters more than speed
- **Limitations**: Exponential time complexity, impractical for real-world problems

#### Constructive Heuristics (Fast, Good Solutions)
- **Nearest Neighbor**: Greedy selection of closest unvisited node
  - Advantage: O(n²) time, simple to implement
  - Disadvantage: Often 20-30% worse than optimal
- **Clarke-Wright Savings**: Merge routes based on savings metric
  - Better quality than nearest neighbor
  - Good for initialization
- **Sweep Algorithm**: Rotate ray around depot, assigning nodes in order
  - Excellent for geographic clusters
  - Fast and practical
- **Christofides Algorithm**: Use MST to guarantee ≤1.5× optimal (for metric TSP)

#### Local Search Metaheuristics (Iterative Improvement)
- **2-opt**: Reverse segments of route to remove crossing edges
  - Simple, fast, effective
  - Can improve nearest neighbor by 15-25%
- **3-opt**: More complex moves, better results but slower
- **Lin-Kernighan**: Variable-depth local search, very effective
- **Tabu Search**: Track recently visited solutions to escape local optima
- **Simulated Annealing**: Accept worse solutions probabilistically to escape local optima
- **Genetic Algorithms**: Population-based approach, good for multi-objective problems

#### Hybrid and Advanced Approaches
- **Constraint Programming**: OR-Tools uses constraint programming + local search
  - Flexible for complex constraints
  - Excellent solution quality in reasonable time
- **Large Neighborhood Search**: Destroy and rebuild large portions of solution
- **Ant Colony Optimization**: Swarm intelligence approach
- **Guided Local Search**: Add penalties to guide search away from local optima

### 3. Production Implementations

#### Google OR-Tools
```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from datetime import datetime, timedelta

class RoutingOptimizer:
    def __init__(self, locations, vehicles=1):
        """
        Initialize routing problem.
        locations: list of (lat, lon) tuples or distance matrix
        """
        self.locations = locations
        self.vehicles = vehicles
        self.manager = None
        self.routing = None

    def create_distance_callback(self, distance_matrix):
        """Create distance callback for routing engine."""
        def distance_callback(from_index, to_index):
            return int(distance_matrix[from_index][to_index])
        return distance_callback

    def create_time_callback(self, time_matrix, service_times):
        """Create time callback including service time at each location."""
        def time_callback(from_index, to_index):
            transit_time = int(time_matrix[from_index][to_index])
            service_time = service_times.get(to_index, 0) if to_index > 0 else 0
            return transit_time + service_time
        return time_callback

    def solve_vrptw(self, distance_matrix, time_matrix, time_windows,
                    service_times, vehicle_capacities, max_time=8*3600):
        """
        Solve VRP with Time Windows and capacity constraints.

        time_windows: list of (open_time, close_time) in seconds since start
        max_time: maximum route duration (default 8 hours)
        """
        num_locations = len(distance_matrix)

        # Create routing index manager
        self.manager = pywrapcp.RoutingIndexManager(
            num_locations, self.vehicles, 0)  # 0 is depot

        # Create routing model
        self.routing = pywrapcp.RoutingModel(self.manager)

        # Add distance dimension (for distance-based constraints)
        distance_callback = self.create_distance_callback(distance_matrix)
        distance_transit_callback_index = self.routing.RegisterTransitCallback(
            distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(distance_transit_callback_index)

        # Add time dimension (for time windows)
        time_callback = self.create_time_callback(time_matrix, service_times)
        time_transit_callback_index = self.routing.RegisterTransitCallback(
            time_callback)

        self.routing.AddDimension(
            time_transit_callback_index,
            max_time,  # slack (vehicles can wait)
            max_time,  # vehicle max time
            False,  # start cumul at 0
            'Time'
        )

        time_dimension = self.routing.GetDimensionOrDie('Time')

        # Set time windows
        for location_idx, time_window in enumerate(time_windows):
            if location_idx == 0:
                continue  # Skip depot
            index = self.manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(
                int(time_window[0]), int(time_window[1]))

        # Set vehicle time window (start at depot at 0)
        for vehicle_id in range(self.vehicles):
            index = self.routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(0, 0)

        # Add capacity dimension
        def capacity_callback(from_index):
            return int(time_matrix[from_index][0])  # Dummy demand values

        # Solve with search parameters
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_params.time_limit.seconds = 10  # 10 second time limit

        solution = self.routing.SolveWithParameters(search_params)

        if solution:
            return self._extract_solution(solution)
        return None

    def _extract_solution(self, solution):
        """Extract routes from solution."""
        routes = []
        for vehicle_id in range(self.vehicles):
            route = []
            index = self.routing.Start(vehicle_id)
            while not self.routing.IsEnd(index):
                node_index = self.manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(self.routing.NextVar(index))
            route.append(self.manager.IndexToNode(index))  # Add depot at end
            routes.append(route)
        return routes

    def solve_cvrp(self, distance_matrix, demands, vehicle_capacities):
        """Solve Capacitated VRP."""
        num_locations = len(distance_matrix)
        self.manager = pywrapcp.RoutingIndexManager(
            num_locations, len(vehicle_capacities), 0)
        self.routing = pywrapcp.RoutingModel(self.manager)

        # Distance callback
        def distance_callback(from_index, to_index):
            return int(distance_matrix[from_index][to_index])

        distance_callback_index = self.routing.RegisterTransitCallback(
            distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

        # Capacity dimension
        def demand_callback(from_index):
            node = self.manager.IndexToNode(from_index)
            return demands[node]

        demand_callback_index = self.routing.RegisterTransitCallback(
            demand_callback)
        self.routing.AddDimension(
            demand_callback_index,
            0,  # slack
            vehicle_capacities,  # vehicle capacities
            True,  # start cumul at 0
            'Capacity'
        )

        # Solve
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        solution = self.routing.SolveWithParameters(search_params)

        return self._extract_solution(solution) if solution else None
```

#### Real-World Applications and Results
- **UPS ORION**:
  - Optimizes 250,000 routes per day
  - Saves 100M+ miles annually
  - 2-3% reduction in total miles traveled
  - Prevents 5M+ gallons of fuel waste per year

- **Amazon Logistics**:
  - Sub-5-second optimization for 200+ stops
  - Real-time re-optimization as new orders arrive
  - Zone-based clustering for scalability

- **DoorDash**:
  - Real-time batching and matching
  - 1.4× orders per delivery through pooling
  - ML-based demand prediction for supply positioning

- **Last-Mile Delivery Services**:
  - 30-40% reduction in delivery costs through optimization
  - Improved on-time delivery rates
  - Better driver utilization and satisfaction

### 4. Performance Characteristics & Benchmarks

| Problem Size | Algorithm | Time | Solution Quality |
|---|---|---|---|
| 20 stops | Exact (DP) | 10ms | 100% optimal |
| 50 stops | OR-Tools | <1 sec | 95-99% of optimal |
| 200 stops | OR-Tools + clustering | <5 sec | 90-95% of optimal |
| 500 stops | Cluster-first approach | 10-30 sec | 85-90% of optimal |
| 1000+ stops | Zone decomposition | 1-5 min | 80-85% of optimal |

### 5. Implementation Patterns

#### Cluster-First, Route-Second
```python
def cluster_first_route_second(locations, num_clusters, vehicles):
    """
    Large-scale optimization pattern:
    1. Cluster geographically close locations
    2. Solve VRP separately for each cluster
    3. Combine routes
    """
    from sklearn.cluster import KMeans

    # Cluster locations
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(locations)

    all_routes = []
    for cluster_id in range(num_clusters):
        cluster_stops = [i for i, c in enumerate(clusters) if c == cluster_id]

        # Solve VRP for this cluster
        if cluster_stops:
            sub_distance_matrix = compute_sub_matrix(locations, cluster_stops)
            routes = solve_vrp(sub_distance_matrix, vehicles)
            # Map back to original indices
            mapped_routes = [[cluster_stops[i] for i in route] for route in routes]
            all_routes.extend(mapped_routes)

    return all_routes
```

#### Real-Time Re-Optimization
```python
class RealtimeRouter:
    """Handle dynamic orders arriving throughout the day."""

    def __init__(self, initial_orders, vehicles):
        self.orders = initial_orders
        self.vehicles = vehicles
        self.routes = self.initial_solve()
        self.last_optimization_time = time.time()

    def add_order(self, new_order):
        """Add new order and re-optimize if beneficial."""
        self.orders.append(new_order)

        # Only re-optimize every 30 seconds to avoid constant changes
        if time.time() - self.last_optimization_time > 30:
            new_routes = self.solve_vrp()

            # Calculate improvement
            current_cost = self.calculate_cost(self.routes)
            new_cost = self.calculate_cost(new_routes)
            improvement = (current_cost - new_cost) / current_cost

            # Only apply if significant improvement (>5%) and disruption is small
            if improvement > 0.05 and self.calculate_disruption(new_routes) < 0.2:
                self.routes = new_routes
                self.last_optimization_time = time.time()
```

#### Vehicle-Specific Constraints
```python
def add_vehicle_constraints(routing, vehicle_specs):
    """
    Add vehicle-specific constraints.
    vehicle_specs: list of dicts with vehicle capabilities/limits
    """
    for vehicle_id, specs in enumerate(vehicle_specs):
        # Maximum distance
        if 'max_distance' in specs:
            distance_dimension = routing.GetDimensionOrDie('Distance')
            distance_dimension.CumulVar(routing.End(vehicle_id)).SetMax(
                specs['max_distance'])

        # Compatible locations (e.g., only large vehicles for heavy items)
        if 'compatible_stops' in specs:
            for stop_id in range(len(all_stops)):
                if stop_id not in specs['compatible_stops']:
                    routing.SetDisallowedTransitType(vehicle_id, stop_id)

        # Cost multiplier (e.g., premium vehicles cost more)
        if 'hourly_cost' in specs:
            # Adjust arc costs for this vehicle
            pass
```

### 6. Advanced Topics

#### Dynamic Traffic and Real-Time Conditions
- **Live traffic integration**: Leverage Google Maps, HERE, or TomTom APIs
- **ETAssessment**: Continuously update ETAs as traffic changes
- **Predictive delays**: Use historical patterns and current conditions
- **Route swapping**: Allow drivers to exchange remaining stops for better efficiency

#### Machine Learning Integration
- **Demand prediction**: Forecast stop locations and volumes
- **ETA models**: Neural networks for more accurate time predictions
- **Stop consolidation**: ML to identify stops that can be merged
- **Driver preference learning**: Personalize routes to driver preferences

#### Multi-Objective Optimization
- **Pareto frontier**: Balance cost, time, and fairness
- **Weighted objectives**: Cost + customer satisfaction + driver retention
- **Constraint hierarchies**: Must-have constraints vs. nice-to-have

## Key Performance Metrics

### Operational Metrics
- **Route Efficiency**: Total distance traveled / optimal distance (target: >85%)
- **Time Window Compliance**: % of stops visited within promised time window (target: >95%)
- **Vehicle Utilization**: Average capacity utilization (target: >80%)
- **Cost Per Stop**: Total routing costs / number of stops (target: <$3-5)
- **Average Route Duration**: Time from first to last stop (target: optimize based on max working hours)

### Service Metrics
- **On-Time Delivery Rate**: % of deliveries within promised window
- **First-Attempt Success**: % of stops completed without re-visit
- **Customer Satisfaction**: Satisfaction ratings by delivery experience

### System Metrics
- **Optimization Time**: Time to generate optimized routes
- **System Availability**: Uptime for routing engine
- **Accuracy**: Predicted costs vs. actual costs

## Best Practices

### Problem Formulation
1. **Gather accurate data**: Distance/time matrices, demand quantities, time windows
2. **Define constraints clearly**: Hard constraints (must obey) vs. soft constraints (prefer)
3. **Set realistic objectives**: Cost vs. service level trade-offs
4. **Include all relevant factors**: Vehicle costs, fuel, labor, time value

### Algorithm Selection
1. **Match algorithm to problem**: Small problems can use exact; large problems need heuristics
2. **Consider time constraints**: Real-time systems need fast algorithms (< 5 seconds)
3. **Start simple**: Begin with nearest neighbor, improve with local search
4. **Hybrid approaches**: Combine clustering with routing for large problems

### Implementation
1. **Validate solutions**: Check solution feasibility before deployment
2. **Gradual rollout**: Test optimized routes on subset before full deployment
3. **Monitor performance**: Track actual vs. predicted metrics
4. **Feedback loops**: Use actual results to improve models and algorithms

## Common Challenges & Solutions

| Challenge | Root Cause | Solution |
|---|---|---|
| Routes exceed time windows | Optimistic time estimates | Add buffers, validate with actual data |
| High re-optimization cost | Too frequent optimization | Batch updates, cost-benefit analysis |
| Poor driver satisfaction | Unintuitive routes | Add fairness constraints, driver input |
| Low utilization | Conservative estimates | Bin packing, load consolidation |

## Related Skills
- **Demand Forecasting**: Predict which stops and volumes
- **Network Design**: Determine depot and zone boundaries
- **Fleet Management**: Vehicle capabilities and costs
- **Supply Chain Visibility**: Tracking actual vs. optimized performance

---

**Expertise Level**: Advanced
**Typical Implementation Time**: 2-8 weeks depending on complexity
**ROI**: 15-30% reduction in transportation costs through optimization
