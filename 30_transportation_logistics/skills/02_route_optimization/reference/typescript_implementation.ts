/**
 * Route Optimization Implementation in TypeScript
 *
 * Production-ready implementation of Vehicle Routing Problem (VRP) algorithms
 * including CVRP, VRPTW, and advanced heuristics for real-world scenarios.
 */

// ============================================================================
// Type Definitions
// ============================================================================

interface Location {
  id: string;
  lat: number;
  lon: number;
  name?: string;
}

interface TimeWindow {
  start: number;  // seconds since start of day
  end: number;    // seconds since start of day
}

interface Stop {
  location: Location;
  demand: number;  // units (weight, volume, pallets)
  serviceTime: number;  // seconds
  timeWindow?: TimeWindow;
  priority?: number;  // higher = more important
  skills?: string[];  // required driver/vehicle skills
}

interface Vehicle {
  id: string;
  capacity: number;
  startLocation: Location;
  endLocation?: Location;
  maxDistance?: number;
  maxTime?: number;  // seconds
  skills?: string[];
  costPerMile?: number;
  fixedCost?: number;
}

interface Route {
  vehicleId: string;
  stops: Stop[];
  distance: number;
  duration: number;
  load: number;
  cost: number;
}

interface Solution {
  routes: Route[];
  totalDistance: number;
  totalDuration: number;
  totalCost: number;
  unassignedStops: Stop[];
}

// ============================================================================
// Distance Calculation Utilities
// ============================================================================

/**
 * Calculate Haversine distance between two coordinates (in miles)
 */
function haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 3959; // Earth's radius in miles
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Create distance matrix from locations
 */
function createDistanceMatrix(locations: Location[]): number[][] {
  const n = locations.length;
  const matrix: number[][] = Array(n).fill(null).map(() => Array(n).fill(0));

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i !== j) {
        matrix[i][j] = haversineDistance(
          locations[i].lat, locations[i].lon,
          locations[j].lat, locations[j].lon
        );
      }
    }
  }

  return matrix;
}

/**
 * Estimate travel time from distance (includes average speed and traffic)
 */
function estimateTravelTime(distanceMiles: number, avgSpeedMph: number = 35): number {
  return (distanceMiles / avgSpeedMph) * 3600; // convert to seconds
}

// ============================================================================
// Nearest Neighbor Heuristic (Simple, Fast)
// ============================================================================

class NearestNeighborSolver {
  private distanceMatrix: number[][];

  constructor(private stops: Stop[], private vehicles: Vehicle[]) {
    const locations = stops.map(s => s.location);
    this.distanceMatrix = createDistanceMatrix(locations);
  }

  solve(): Solution {
    const routes: Route[] = [];
    const unassigned: Stop[] = [];
    const visited = new Set<number>();

    for (const vehicle of this.vehicles) {
      const route = this.buildRouteForVehicle(vehicle, visited);
      if (route.stops.length > 0) {
        routes.push(route);
      }
    }

    // Collect unassigned stops
    this.stops.forEach((stop, idx) => {
      if (!visited.has(idx)) {
        unassigned.push(stop);
      }
    });

    return {
      routes,
      totalDistance: routes.reduce((sum, r) => sum + r.distance, 0),
      totalDuration: routes.reduce((sum, r) => sum + r.duration, 0),
      totalCost: routes.reduce((sum, r) => sum + r.cost, 0),
      unassignedStops: unassigned
    };
  }

  private buildRouteForVehicle(vehicle: Vehicle, visited: Set<number>): Route {
    const routeStops: Stop[] = [];
    let currentLocation = vehicle.startLocation;
    let totalDistance = 0;
    let totalDuration = 0;
    let currentLoad = 0;
    let currentTime = 0;

    while (true) {
      // Find nearest unvisited feasible stop
      let nearestIdx = -1;
      let nearestDist = Infinity;

      for (let i = 0; i < this.stops.length; i++) {
        if (visited.has(i)) continue;

        const stop = this.stops[i];

        // Check capacity constraint
        if (currentLoad + stop.demand > vehicle.capacity) continue;

        // Check skill requirements
        if (stop.skills && vehicle.skills) {
          const hasAllSkills = stop.skills.every(skill => vehicle.skills!.includes(skill));
          if (!hasAllSkills) continue;
        }

        const dist = haversineDistance(
          currentLocation.lat, currentLocation.lon,
          stop.location.lat, stop.location.lon
        );

        // Check time window if specified
        if (stop.timeWindow) {
          const travelTime = estimateTravelTime(dist);
          const arrivalTime = currentTime + travelTime;

          // Can't arrive after window closes
          if (arrivalTime > stop.timeWindow.end) continue;
        }

        if (dist < nearestDist) {
          nearestDist = dist;
          nearestIdx = i;
        }
      }

      // No more feasible stops
      if (nearestIdx === -1) break;

      // Add stop to route
      const stop = this.stops[nearestIdx];
      visited.add(nearestIdx);
      routeStops.push(stop);

      totalDistance += nearestDist;
      const travelTime = estimateTravelTime(nearestDist);
      totalDuration += travelTime + stop.serviceTime;
      currentTime += travelTime;

      // Wait if arriving before time window opens
      if (stop.timeWindow && currentTime < stop.timeWindow.start) {
        const waitTime = stop.timeWindow.start - currentTime;
        totalDuration += waitTime;
        currentTime = stop.timeWindow.start;
      }

      currentTime += stop.serviceTime;
      currentLoad += stop.demand;
      currentLocation = stop.location;

      // Check vehicle constraints
      if (vehicle.maxDistance && totalDistance > vehicle.maxDistance) break;
      if (vehicle.maxTime && totalDuration > vehicle.maxTime) break;
    }

    // Return to depot
    const endLocation = vehicle.endLocation || vehicle.startLocation;
    const returnDist = haversineDistance(
      currentLocation.lat, currentLocation.lon,
      endLocation.lat, endLocation.lon
    );
    totalDistance += returnDist;
    totalDuration += estimateTravelTime(returnDist);

    // Calculate cost
    const distanceCost = (vehicle.costPerMile || 2.5) * totalDistance;
    const fixedCost = vehicle.fixedCost || 100;
    const totalCost = distanceCost + fixedCost;

    return {
      vehicleId: vehicle.id,
      stops: routeStops,
      distance: totalDistance,
      duration: totalDuration,
      load: currentLoad,
      cost: totalCost
    };
  }
}

// ============================================================================
// 2-Opt Local Search Optimization
// ============================================================================

class TwoOptOptimizer {
  private distanceMatrix: number[][];

  constructor(private locations: Location[]) {
    this.distanceMatrix = createDistanceMatrix(locations);
  }

  /**
   * Improve a route using 2-opt local search
   * Attempts to remove crossing edges by reversing route segments
   */
  optimize(route: number[], maxIterations: number = 1000): number[] {
    let improved = true;
    let iterations = 0;
    let currentRoute = [...route];

    while (improved && iterations < maxIterations) {
      improved = false;
      iterations++;

      for (let i = 1; i < currentRoute.length - 2; i++) {
        for (let j = i + 1; j < currentRoute.length - 1; j++) {
          const delta = this.calculate2OptDelta(currentRoute, i, j);

          if (delta < -0.001) { // Improvement found
            currentRoute = this.apply2OptSwap(currentRoute, i, j);
            improved = true;
          }
        }
      }
    }

    return currentRoute;
  }

  private calculate2OptDelta(route: number[], i: number, j: number): number {
    const a = route[i - 1];
    const b = route[i];
    const c = route[j];
    const d = route[j + 1];

    const currentDist =
      this.distanceMatrix[a][b] +
      this.distanceMatrix[c][d];

    const newDist =
      this.distanceMatrix[a][c] +
      this.distanceMatrix[b][d];

    return newDist - currentDist;
  }

  private apply2OptSwap(route: number[], i: number, j: number): number[] {
    const newRoute = [...route];

    // Reverse segment between i and j
    let left = i;
    let right = j;

    while (left < right) {
      [newRoute[left], newRoute[right]] = [newRoute[right], newRoute[left]];
      left++;
      right--;
    }

    return newRoute;
  }

  calculateRouteDistance(route: number[]): number {
    let distance = 0;
    for (let i = 0; i < route.length - 1; i++) {
      distance += this.distanceMatrix[route[i]][route[i + 1]];
    }
    return distance;
  }
}

// ============================================================================
// Clarke-Wright Savings Algorithm
// ============================================================================

class ClarkeWrightSolver {
  private distanceMatrix: number[][];

  constructor(private stops: Stop[], private vehicles: Vehicle[]) {
    const locations = [vehicles[0].startLocation, ...stops.map(s => s.location)];
    this.distanceMatrix = createDistanceMatrix(locations);
  }

  solve(): Solution {
    // Calculate savings for all pairs of customers
    const savings = this.calculateSavings();

    // Sort savings in descending order
    savings.sort((a, b) => b.saving - a.saving);

    // Initialize routes (one per customer initially)
    const routes: Route[] = [];
    const stopToRoute = new Map<number, number>();

    this.stops.forEach((stop, idx) => {
      const route: Route = {
        vehicleId: '',
        stops: [stop],
        distance: this.distanceMatrix[0][idx + 1] * 2, // depot to stop and back
        duration: estimateTravelTime(this.distanceMatrix[0][idx + 1] * 2) + stop.serviceTime,
        load: stop.demand,
        cost: 0
      };
      routes.push(route);
      stopToRoute.set(idx, routes.length - 1);
    });

    // Merge routes based on savings
    for (const saving of savings) {
      const route1Idx = stopToRoute.get(saving.i);
      const route2Idx = stopToRoute.get(saving.j);

      if (route1Idx === undefined || route2Idx === undefined) continue;
      if (route1Idx === route2Idx) continue; // Already in same route

      const route1 = routes[route1Idx];
      const route2 = routes[route2Idx];

      // Check if merge is feasible
      const vehicle = this.vehicles[0]; // Simplified: use first vehicle constraints
      if (route1.load + route2.load > vehicle.capacity) continue;

      // Merge routes
      const mergedRoute: Route = {
        vehicleId: '',
        stops: [...route1.stops, ...route2.stops],
        distance: route1.distance + route2.distance - this.distanceMatrix[0][saving.i + 1] - this.distanceMatrix[0][saving.j + 1] + this.distanceMatrix[saving.i + 1][saving.j + 1],
        duration: route1.duration + route2.duration,
        load: route1.load + route2.load,
        cost: 0
      };

      routes[route1Idx] = mergedRoute;
      routes.splice(route2Idx, 1);

      // Update stop-to-route mapping
      route2.stops.forEach((stop) => {
        const stopIdx = this.stops.indexOf(stop);
        stopToRoute.set(stopIdx, route1Idx);
      });

      // Adjust indices after splice
      stopToRoute.forEach((routeIdx, stopIdx) => {
        if (routeIdx > route2Idx) {
          stopToRoute.set(stopIdx, routeIdx - 1);
        }
      });
    }

    // Assign vehicles and calculate costs
    routes.forEach((route, idx) => {
      const vehicle = this.vehicles[idx % this.vehicles.length];
      route.vehicleId = vehicle.id;
      route.cost = (vehicle.costPerMile || 2.5) * route.distance + (vehicle.fixedCost || 100);
    });

    return {
      routes: routes.filter(r => r.stops.length > 0),
      totalDistance: routes.reduce((sum, r) => sum + r.distance, 0),
      totalDuration: routes.reduce((sum, r) => sum + r.duration, 0),
      totalCost: routes.reduce((sum, r) => sum + r.cost, 0),
      unassignedStops: []
    };
  }

  private calculateSavings(): Array<{i: number; j: number; saving: number}> {
    const savings: Array<{i: number; j: number; saving: number}> = [];

    for (let i = 0; i < this.stops.length; i++) {
      for (let j = i + 1; j < this.stops.length; j++) {
        // Saving = distance(depot, i) + distance(depot, j) - distance(i, j)
        const saving =
          this.distanceMatrix[0][i + 1] +
          this.distanceMatrix[0][j + 1] -
          this.distanceMatrix[i + 1][j + 1];

        savings.push({ i, j, saving });
      }
    }

    return savings;
  }
}

// ============================================================================
// Usage Example
// ============================================================================

function exampleUsage() {
  // Define depot
  const depot: Location = {
    id: 'depot',
    lat: 40.7128,
    lon: -74.0060,
    name: 'Distribution Center'
  };

  // Define stops
  const stops: Stop[] = [
    {
      location: { id: 's1', lat: 40.7580, lon: -73.9855, name: 'Customer 1' },
      demand: 500,
      serviceTime: 600, // 10 minutes
      timeWindow: { start: 28800, end: 57600 } // 8 AM - 4 PM
    },
    {
      location: { id: 's2', lat: 40.7489, lon: -73.9680, name: 'Customer 2' },
      demand: 750,
      serviceTime: 900, // 15 minutes
      timeWindow: { start: 32400, end: 61200 } // 9 AM - 5 PM
    },
    {
      location: { id: 's3', lat: 40.7614, lon: -73.9776, name: 'Customer 3' },
      demand: 300,
      serviceTime: 600,
      timeWindow: { start: 28800, end: 50400 } // 8 AM - 2 PM
    },
    {
      location: { id: 's4', lat: 40.7282, lon: -73.9942, name: 'Customer 4' },
      demand: 450,
      serviceTime: 720,
      priority: 1
    },
    {
      location: { id: 's5', lat: 40.7359, lon: -74.0014, name: 'Customer 5' },
      demand: 600,
      serviceTime: 600,
      skills: ['refrigerated']
    }
  ];

  // Define vehicles
  const vehicles: Vehicle[] = [
    {
      id: 'truck-1',
      capacity: 2000,
      startLocation: depot,
      maxTime: 28800, // 8 hours
      costPerMile: 3.0,
      fixedCost: 150,
      skills: ['refrigerated']
    },
    {
      id: 'truck-2',
      capacity: 2000,
      startLocation: depot,
      maxTime: 28800,
      costPerMile: 2.5,
      fixedCost: 100
    }
  ];

  // Solve using Nearest Neighbor
  console.log('=== Nearest Neighbor Solution ===');
  const nnSolver = new NearestNeighborSolver(stops, vehicles);
  const nnSolution = nnSolver.solve();
  console.log(`Total Distance: ${nnSolution.totalDistance.toFixed(2)} miles`);
  console.log(`Total Cost: $${nnSolution.totalCost.toFixed(2)}`);
  console.log(`Number of Routes: ${nnSolution.routes.length}`);
  console.log(`Unassigned Stops: ${nnSolution.unassignedStops.length}`);

  // Solve using Clarke-Wright
  console.log('\n=== Clarke-Wright Solution ===');
  const cwSolver = new ClarkeWrightSolver(stops, vehicles);
  const cwSolution = cwSolver.solve();
  console.log(`Total Distance: ${cwSolution.totalDistance.toFixed(2)} miles`);
  console.log(`Total Cost: $${cwSolution.totalCost.toFixed(2)}`);
  console.log(`Number of Routes: ${cwSolution.routes.length}`);

  // Apply 2-opt optimization to first route
  if (nnSolution.routes.length > 0) {
    const route = nnSolution.routes[0];
    const locations = [depot, ...route.stops.map(s => s.location), depot];
    const routeIndices = locations.map((_, idx) => idx);

    const optimizer = new TwoOptOptimizer(locations);
    const originalDist = optimizer.calculateRouteDistance(routeIndices);
    const optimizedRoute = optimizer.optimize(routeIndices);
    const optimizedDist = optimizer.calculateRouteDistance(optimizedRoute);

    console.log('\n=== 2-Opt Optimization ===');
    console.log(`Original Distance: ${originalDist.toFixed(2)} miles`);
    console.log(`Optimized Distance: ${optimizedDist.toFixed(2)} miles`);
    console.log(`Improvement: ${((originalDist - optimizedDist) / originalDist * 100).toFixed(2)}%`);
  }
}

// Run example if this file is executed directly
if (require.main === module) {
  exampleUsage();
}

export {
  Location,
  Stop,
  Vehicle,
  Route,
  Solution,
  NearestNeighborSolver,
  TwoOptOptimizer,
  ClarkeWrightSolver,
  haversineDistance,
  createDistanceMatrix,
  estimateTravelTime
};
