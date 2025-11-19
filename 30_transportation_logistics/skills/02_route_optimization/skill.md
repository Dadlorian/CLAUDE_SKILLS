# Route Optimization Subskill

## Overview
Expert in Vehicle Routing Problem (VRP) algorithms, route optimization engines, and production implementations at scale (UPS ORION, Amazon routing).

## Core Competencies

### VRP Algorithm Types
- **TSP** (Traveling Salesman Problem): Single vehicle, minimize tour distance
- **CVRP** (Capacitated VRP): Multiple vehicles with capacity constraints
- **VRPTW** (VRP with Time Windows): Delivery windows required
- **MDVRP** (Multi-Depot VRP): Multiple start/end locations
- **PDVRP** (Pickup and Delivery VRP): Paired pickup/delivery stops
- **VRPB** (VRP with Backhauls): Deliveries then pickups

### Solution Algorithms
- **Exact**: Branch-and-bound, dynamic programming (small problems only)
- **Heuristic**: Clarke-Wright savings, nearest neighbor, sweep algorithm
- **Metaheuristic**: Genetic algorithms, simulated annealing, tabu search
- **Hybrid**: OR-Tools (constraint programming + local search)

### Google OR-Tools Implementation
```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def solve_vrptw(distance_matrix, time_windows, vehicle_capacities):
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # Add time window constraints
    routing.AddDimension(transit_callback, 0, max_time, False, 'Time')
    time_dimension = routing.GetDimensionOrDie('Time')

    for location_idx, time_window in enumerate(time_windows):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)
    return solution
```

## Real-World Applications
- **UPS ORION**: 250,000 routes/minute, saves 100M+ miles/year
- **Amazon**: Sub-5-second optimization for 200+ stops
- **DoorDash**: Real-time batching, 1.4x orders per delivery

## Performance Benchmarks
- 50 stops: < 1 second
- 200 stops: < 5 seconds
- 1000+ stops: Use clustering + parallel solving

## Key Metrics
- **Route Efficiency**: Total distance/optimal distance
- **Time Window Compliance**: % deliveries within window
- **Vehicle Utilization**: % capacity used
- **Cost Per Stop**: Total route cost / stops delivered
