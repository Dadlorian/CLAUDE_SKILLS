"""
Route Optimization Module - Vehicle Routing Problem (VRP) Solutions

This module provides route optimization algorithms for:
- Traveling Salesman Problem (TSP) - single vehicle
- Vehicle Routing Problem (VRP) - multiple vehicles
- Capacity Constrained VRP (CVRP)
- VRP with Time Windows (VRPTW)
- Dynamic routing optimization
- Cost optimization vs. speed optimization
"""

import math
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import heapq
from datetime import datetime, timedelta
import random


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Data Classes
# ============================================================================

class OptimizationObjective(Enum):
    """Route optimization objectives"""
    MINIMIZE_DISTANCE = "minimize_distance"
    MINIMIZE_TIME = "minimize_time"
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_VEHICLES = "minimize_vehicles"
    MAXIMIZE_UTILIZATION = "maximize_utilization"


class DistanceMetric(Enum):
    """Distance calculation methods"""
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    HAVERSINE = "haversine"  # For lat/lon coordinates


@dataclass
class Location:
    """Location/Stop information"""
    location_id: str
    latitude: float
    longitude: float
    name: str = ""
    address: str = ""
    service_time_minutes: int = 0  # Time to serve this location
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    demand: float = 0  # Units to deliver
    priority: int = 1  # 1=high, 3=low


@dataclass
class Vehicle:
    """Vehicle configuration"""
    vehicle_id: str
    capacity: float
    start_location: str
    end_location: str
    availability_start: Optional[str] = None
    availability_end: Optional[str] = None
    cost_per_mile: float = 1.0
    cost_per_hour: float = 25.0
    max_hours: float = 8.0


@dataclass
class Route:
    """Optimized route"""
    vehicle_id: str
    stops: List[str]  # Location IDs in order
    distance_miles: float = 0.0
    duration_minutes: float = 0.0
    stops_order: List[int] = None  # Stop indices
    total_demand: float = 0.0
    total_cost: float = 0.0
    utilization_percent: float = 0.0
    time_windows_met: bool = True

    def __post_init__(self):
        if self.stops_order is None:
            self.stops_order = list(range(len(self.stops)))


# ============================================================================
# Distance Calculations
# ============================================================================

class DistanceCalculator:
    """Calculates distances between locations"""

    @staticmethod
    def euclidean_distance(loc1: Location, loc2: Location) -> float:
        """Calculate Euclidean distance"""
        dx = loc2.latitude - loc1.latitude
        dy = loc2.longitude - loc1.longitude
        return math.sqrt(dx*dx + dy*dy)

    @staticmethod
    def manhattan_distance(loc1: Location, loc2: Location) -> float:
        """Calculate Manhattan distance"""
        return abs(loc2.latitude - loc1.latitude) + abs(loc2.longitude - loc1.longitude)

    @staticmethod
    def haversine_distance(loc1: Location, loc2: Location) -> float:
        """
        Calculate Haversine distance (great-circle distance on Earth)
        Returns distance in miles
        """
        earth_radius_miles = 3959

        lat1, lon1 = math.radians(loc1.latitude), math.radians(loc1.longitude)
        lat2, lon2 = math.radians(loc2.latitude), math.radians(loc2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return earth_radius_miles * c

    @staticmethod
    def build_distance_matrix(locations: List[Location],
                            metric: DistanceMetric = DistanceMetric.EUCLIDEAN) -> Dict[str, Dict[str, float]]:
        """
        Build distance matrix between all locations

        Args:
            locations: List of locations
            metric: Distance metric to use

        Returns:
            Matrix[location_id][location_id] = distance
        """
        matrix = {}

        for i, loc1 in enumerate(locations):
            matrix[loc1.location_id] = {}
            for loc2 in locations:
                if loc1.location_id == loc2.location_id:
                    matrix[loc1.location_id][loc2.location_id] = 0
                else:
                    if metric == DistanceMetric.EUCLIDEAN:
                        dist = DistanceCalculator.euclidean_distance(loc1, loc2)
                    elif metric == DistanceMetric.MANHATTAN:
                        dist = DistanceCalculator.manhattan_distance(loc1, loc2)
                    else:  # HAVERSINE
                        dist = DistanceCalculator.haversine_distance(loc1, loc2)

                    matrix[loc1.location_id][loc2.location_id] = dist

        logger.info(f"Built distance matrix for {len(locations)} locations")
        return matrix


# ============================================================================
# Route Optimization Algorithms
# ============================================================================

class RouteOptimizer:
    """Base route optimization class"""

    def __init__(self, locations: List[Location],
                vehicles: List[Vehicle],
                distance_matrix: Optional[Dict] = None,
                objective: OptimizationObjective = OptimizationObjective.MINIMIZE_DISTANCE):
        """
        Initialize optimizer

        Args:
            locations: List of delivery locations
            vehicles: List of vehicles
            distance_matrix: Pre-computed distance matrix
            objective: Optimization objective
        """
        self.locations = {loc.location_id: loc for loc in locations}
        self.vehicles = {v.vehicle_id: v for v in vehicles}
        self.objective = objective

        if distance_matrix is None:
            self.distance_matrix = DistanceCalculator.build_distance_matrix(locations)
        else:
            self.distance_matrix = distance_matrix

    def _get_distance(self, from_loc: str, to_loc: str) -> float:
        """Get distance between locations"""
        return self.distance_matrix.get(from_loc, {}).get(to_loc, float('inf'))

    def _calculate_route_cost(self, route: Route, vehicle: Vehicle) -> float:
        """Calculate total cost for route"""
        return (route.distance_miles * vehicle.cost_per_mile +
                route.duration_minutes / 60 * vehicle.cost_per_hour)

    def _calculate_nearest_unvisited(self, current_location: str,
                                    unvisited: Set[str]) -> str:
        """Find nearest unvisited location"""
        nearest = None
        min_distance = float('inf')

        for location_id in unvisited:
            dist = self._get_distance(current_location, location_id)
            if dist < min_distance:
                min_distance = dist
                nearest = location_id

        return nearest


class NearestNeighborOptimizer(RouteOptimizer):
    """Nearest Neighbor heuristic for route optimization"""

    def optimize(self) -> List[Route]:
        """
        Generate routes using nearest neighbor heuristic

        1. Start at depot
        2. Find nearest unvisited location
        3. Add to current route if capacity allows
        4. If full, start new vehicle
        5. Repeat until all locations visited

        Returns:
            List of optimized routes
        """
        unvisited = set(self.locations.keys())

        # Remove start/end depots from delivery set
        depots = set()
        for vehicle in self.vehicles.values():
            depots.add(vehicle.start_location)
            depots.add(vehicle.end_location)

        unvisited = unvisited - depots

        routes = []
        vehicle_list = list(self.vehicles.values())
        vehicle_idx = 0

        while unvisited and vehicle_idx < len(vehicle_list):
            vehicle = vehicle_list[vehicle_idx]
            route_stops = [vehicle.start_location]
            current_location = vehicle.start_location
            route_demand = 0
            distance_traveled = 0

            while unvisited:
                # Find nearest neighbor
                nearest = self._calculate_nearest_unvisited(current_location, unvisited)

                if nearest is None:
                    break

                nearest_loc = self.locations[nearest]
                distance = self._get_distance(current_location, nearest)

                # Check capacity constraint
                if route_demand + nearest_loc.demand > vehicle.capacity:
                    break

                # Add to route
                route_stops.append(nearest)
                route_demand += nearest_loc.demand
                distance_traveled += distance
                current_location = nearest
                unvisited.remove(nearest)

            # Return to depot
            final_distance = self._get_distance(current_location, vehicle.end_location)
            distance_traveled += final_distance
            route_stops.append(vehicle.end_location)

            # Create route
            route = Route(
                vehicle_id=vehicle.vehicle_id,
                stops=route_stops,
                distance_miles=distance_traveled,
                total_demand=route_demand,
                utilization_percent=(route_demand / vehicle.capacity * 100)
            )

            route.total_cost = self._calculate_route_cost(route, vehicle)
            routes.append(route)

            logger.info(
                f"Route {vehicle.vehicle_id}: {len(route_stops)-2} stops, "
                f"{distance_traveled:.1f} miles, {route_demand:.1f} units"
            )

            vehicle_idx += 1

        if unvisited:
            logger.warning(f"Could not route {len(unvisited)} locations (insufficient vehicles)")

        return routes


class SavingsAlgorithmOptimizer(RouteOptimizer):
    """Clarke-Wright Savings algorithm for VRP"""

    def optimize(self) -> List[Route]:
        """
        Generate routes using Savings algorithm

        1. Calculate savings for combining routes
        2. Sort savings in descending order
        3. Merge routes with highest savings if feasible
        4. Repeat until no more feasible merges

        Returns:
            List of optimized routes
        """
        # Start with individual routes (each location is separate)
        individual_routes = {}

        # Get depot location
        first_vehicle = list(self.vehicles.values())[0]
        depot = first_vehicle.start_location

        for loc_id, location in self.locations.items():
            if loc_id != depot:
                individual_routes[loc_id] = [depot, loc_id, depot]

        # Calculate savings for each pair
        savings = []

        location_ids = [loc_id for loc_id in self.locations.keys() if loc_id != depot]

        for i in range(len(location_ids)):
            for j in range(i + 1, len(location_ids)):
                loc_i = location_ids[i]
                loc_j = location_ids[j]

                # Saving = distance(i->depot) + distance(depot->j) - distance(i->j)
                saving = (self._get_distance(loc_i, depot) +
                         self._get_distance(depot, loc_j) -
                         self._get_distance(loc_i, loc_j))

                savings.append((saving, loc_i, loc_j))

        # Sort by savings (highest first)
        savings.sort(reverse=True, key=lambda x: x[0])

        # Merge routes based on savings
        merged = set()
        for saving, loc_i, loc_j in savings:
            if loc_i in merged or loc_j in merged:
                continue

            # Try to merge routes
            route_i = individual_routes[loc_i]
            route_j = individual_routes[loc_j]

            # Check if locations are at ends of routes
            if (route_i[1] == loc_i and route_j[-2] == loc_j):
                # Merge: route_i -> depot -> route_j becomes route_i + route_j
                merged_route = route_i[:-1] + route_j[1:]
                individual_routes[loc_i] = merged_route
                del individual_routes[loc_j]
                merged.add(loc_j)

        # Convert to Route objects
        routes = []
        vehicle_list = list(self.vehicles.values())

        route_idx = 0
        for loc_id, route_stops in individual_routes.items():
            if route_idx >= len(vehicle_list):
                break

            vehicle = vehicle_list[route_idx]
            distance_traveled = 0

            for i in range(len(route_stops) - 1):
                distance_traveled += self._get_distance(route_stops[i], route_stops[i+1])

            # Calculate total demand
            total_demand = sum(
                self.locations[loc_id].demand
                for loc_id in route_stops[1:-1]
            )

            route = Route(
                vehicle_id=vehicle.vehicle_id,
                stops=route_stops,
                distance_miles=distance_traveled,
                total_demand=total_demand,
                utilization_percent=(total_demand / vehicle.capacity * 100)
            )

            route.total_cost = self._calculate_route_cost(route, vehicle)
            routes.append(route)

            route_idx += 1

        logger.info(f"Savings algorithm: {len(routes)} routes created")
        return routes


class LocalSearchOptimizer(RouteOptimizer):
    """Local search optimization (2-opt, 3-opt improvements)"""

    def optimize_route_2opt(self, route: Route, vehicle: Vehicle) -> Route:
        """
        Improve route using 2-opt swaps

        2-opt: Try reversing segments of the route to reduce distance

        Args:
            route: Current route
            vehicle: Vehicle for this route

        Returns:
            Improved route
        """
        stops = route.stops.copy()
        improved = True
        iterations = 0
        max_iterations = 100

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            # Try all possible 2-opt swaps
            for i in range(1, len(stops) - 2):
                for j in range(i + 1, len(stops) - 1):
                    # Current distance
                    current_dist = (self._get_distance(stops[i-1], stops[i]) +
                                  self._get_distance(stops[j], stops[j+1]))

                    # After swap distance
                    new_dist = (self._get_distance(stops[i-1], stops[j]) +
                               self._get_distance(stops[i], stops[j+1]))

                    # If improvement found
                    if new_dist < current_dist:
                        # Reverse segment between i and j
                        stops[i:j+1] = reversed(stops[i:j+1])
                        improved = True

                        # Recalculate distance
                        distance = 0
                        for k in range(len(stops) - 1):
                            distance += self._get_distance(stops[k], stops[k+1])

                        route.stops = stops
                        route.distance_miles = distance
                        route.total_cost = self._calculate_route_cost(route, vehicle)

                        logger.debug(f"2-opt improvement found: {distance:.1f} miles")
                        break

                if improved:
                    break

        logger.info(f"2-opt optimization completed in {iterations} iterations")
        return route


# ============================================================================
# Route Statistics and Analysis
# ============================================================================

class RouteAnalyzer:
    """Analyzes and reports on route optimization results"""

    @staticmethod
    def calculate_statistics(routes: List[Route], vehicles: Dict[str, Vehicle]) -> Dict:
        """
        Calculate statistics for route solution

        Args:
            routes: List of optimized routes
            vehicles: Dictionary of vehicles

        Returns:
            Statistics dictionary
        """
        total_distance = sum(r.distance_miles for r in routes)
        total_cost = sum(r.total_cost for r in routes)
        avg_distance = total_distance / len(routes) if routes else 0
        avg_cost = total_cost / len(routes) if routes else 0
        avg_stops = sum(len(r.stops) - 2 for r in routes) / len(routes) if routes else 0
        avg_utilization = sum(r.utilization_percent for r in routes) / len(routes) if routes else 0

        vehicle_utilization = {}
        for route in routes:
            vehicle = vehicles[route.vehicle_id]
            vehicle_utilization[route.vehicle_id] = route.utilization_percent

        return {
            'total_routes': len(routes),
            'total_distance_miles': total_distance,
            'total_cost': total_cost,
            'average_distance_per_route': avg_distance,
            'average_cost_per_route': avg_cost,
            'average_stops_per_route': avg_stops,
            'average_vehicle_utilization': avg_utilization,
            'vehicle_utilization': vehicle_utilization,
            'cost_per_stop': total_cost / sum(len(r.stops) - 2 for r in routes) if sum(len(r.stops) - 2 for r in routes) > 0 else 0
        }

    @staticmethod
    def generate_report(routes: List[Route], vehicles: Dict[str, Vehicle]) -> str:
        """Generate text report of route optimization"""
        stats = RouteAnalyzer.calculate_statistics(routes, vehicles)

        report = []
        report.append("="*60)
        report.append("ROUTE OPTIMIZATION REPORT")
        report.append("="*60)
        report.append(f"Total Routes: {stats['total_routes']}")
        report.append(f"Total Distance: {stats['total_distance_miles']:.1f} miles")
        report.append(f"Total Cost: ${stats['total_cost']:.2f}")
        report.append(f"Avg Distance per Route: {stats['average_distance_per_route']:.1f} miles")
        report.append(f"Avg Cost per Route: ${stats['average_cost_per_route']:.2f}")
        report.append(f"Avg Stops per Route: {stats['average_stops_per_route']:.1f}")
        report.append(f"Avg Vehicle Utilization: {stats['average_vehicle_utilization']:.1f}%")
        report.append(f"Cost per Stop: ${stats['cost_per_stop']:.2f}")
        report.append("")
        report.append("ROUTE DETAILS:")
        report.append("-"*60)

        for route in routes:
            report.append(f"Vehicle: {route.vehicle_id}")
            report.append(f"  Stops: {len(route.stops)-2} ({' -> '.join(route.stops[:3])}...)")
            report.append(f"  Distance: {route.distance_miles:.1f} miles")
            report.append(f"  Cost: ${route.total_cost:.2f}")
            report.append(f"  Utilization: {route.utilization_percent:.1f}%")
            report.append("")

        return "\n".join(report)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Create sample locations
    locations = [
        Location(location_id="depot", latitude=0, longitude=0, name="Distribution Center"),
        Location(location_id="loc1", latitude=1, longitude=1, name="Customer 1", demand=100),
        Location(location_id="loc2", latitude=2, longitude=2, name="Customer 2", demand=150),
        Location(location_id="loc3", latitude=1.5, longitude=2.5, name="Customer 3", demand=80),
        Location(location_id="loc4", latitude=2.5, longitude=1.5, name="Customer 4", demand=120),
        Location(location_id="loc5", latitude=1.2, longitude=-0.8, name="Customer 5", demand=90),
    ]

    # Create vehicles
    vehicles = [
        Vehicle(vehicle_id="vehicle_1", capacity=500, start_location="depot", end_location="depot"),
        Vehicle(vehicle_id="vehicle_2", capacity=500, start_location="depot", end_location="depot"),
    ]

    # Create optimizer
    optimizer = NearestNeighborOptimizer(
        locations=locations,
        vehicles=vehicles,
        objective=OptimizationObjective.MINIMIZE_DISTANCE
    )

    # Optimize routes
    routes = optimizer.optimize()

    # Analyze results
    analyzer = RouteAnalyzer()
    report = analyzer.generate_report(routes, {v.vehicle_id: v for v in vehicles})
    print(report)

    # Apply local search improvement
    local_search = LocalSearchOptimizer(locations, vehicles)
    for route in routes:
        vehicle = {v.vehicle_id: v for v in vehicles}[route.vehicle_id]
        improved_route = local_search.optimize_route_2opt(route, vehicle)
        print(f"Route {route.vehicle_id} improved: {route.distance_miles:.1f} -> {improved_route.distance_miles:.1f} miles")
