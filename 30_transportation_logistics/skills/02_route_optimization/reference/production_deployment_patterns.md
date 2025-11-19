# Production Deployment Patterns for Route Optimization

## Overview

This document provides practical patterns and best practices for deploying route optimization systems in production environments, based on implementations at companies like Amazon, UPS, DoorDash, and enterprise logistics providers.

## Table of Contents

1. [System Architecture Patterns](#system-architecture-patterns)
2. [Real-Time vs. Batch Optimization](#real-time-vs-batch-optimization)
3. [Scalability Strategies](#scalability-strategies)
4. [Fallback and Resilience](#fallback-and-resilience)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Integration Patterns](#integration-patterns)
7. [Deployment Strategies](#deployment-strategies)

---

## System Architecture Patterns

### Microservices Architecture

**Pattern**: Decompose routing into independent services

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Distance       │     │  Optimization    │     │  Route          │
│  Calculator     │────▶│  Engine          │────▶│  Validator      │
│  Service        │     │  Service         │     │  Service        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │                         │
        │                       │                         │
        ▼                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Message Bus (Kafka/RabbitMQ)               │
└─────────────────────────────────────────────────────────────────┘
```

**Services**:
- **Distance Calculator**: Computes distance/time matrices using maps APIs
- **Optimization Engine**: Core VRP solving algorithms
- **Route Validator**: Validates feasibility and compliance
- **Route Dispatcher**: Assigns routes to drivers
- **Tracking Service**: Monitors actual performance vs. plan

**Benefits**:
- Independent scaling of compute-intensive optimization
- Technology diversity (Python for ML, Go for high-performance services)
- Isolated failures don't crash entire system
- Easier to test and deploy individual components

### Event-Driven Architecture

**Pattern**: Use event streams for asynchronous optimization

```javascript
// Producer: New orders arrive
const produceOrderEvent = async (order) => {
  await kafka.send({
    topic: 'orders.created',
    messages: [
      {
        key: order.id,
        value: JSON.stringify(order),
        headers: { priority: order.priority }
      }
    ]
  });
};

// Consumer: Optimization service processes orders
const consumeOrders = async () => {
  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const order = JSON.parse(message.value);

      // Batch orders for optimization window
      orderBuffer.add(order);

      if (shouldTriggerOptimization()) {
        const solution = await optimizeRoutes(orderBuffer.getOrders());
        await publishRoutes(solution);
        orderBuffer.clear();
      }
    }
  });
};
```

**Benefits**:
- Decouples order entry from route optimization
- Natural batching for efficiency
- Replay capability for disaster recovery
- Audit trail of all routing decisions

---

## Real-Time vs. Batch Optimization

### Batch Optimization (Traditional)

**When to Use**:
- Daily route planning (delivery windows known in advance)
- High volume with stable demand patterns
- Computational complexity requires longer solve times
- Routes planned 12-24 hours ahead

**Implementation Pattern**:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class BatchOptimizer:
    def __init__(self, optimizer):
        self.optimizer = optimizer
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # Run optimization daily at 6 PM for next day
        self.scheduler.add_job(
            self.optimize_next_day,
            'cron',
            hour=18,
            minute=0
        )
        self.scheduler.start()

    async def optimize_next_day(self):
        # Fetch all orders for tomorrow
        orders = await self.fetch_orders_for_tomorrow()

        # Fetch vehicle availability
        vehicles = await self.get_available_vehicles()

        # Run optimization (can take 5-30 minutes)
        solution = await self.optimizer.solve(
            orders=orders,
            vehicles=vehicles,
            time_limit_seconds=1800  # 30 minutes
        )

        # Publish routes to drivers
        await self.publish_routes(solution)

        # Store for tracking
        await self.save_solution(solution)

        # Send notifications
        await self.notify_drivers(solution)
```

**Characteristics**:
- **Optimization Time**: 5-60 minutes acceptable
- **Solution Quality**: Can achieve 95-99% of optimal
- **Flexibility**: Limited (routes locked after publication)
- **Cost Efficiency**: Maximum (global optimization)

### Real-Time Optimization

**When to Use**:
- On-demand services (rideshare, food delivery)
- Dynamic order arrival throughout the day
- Customer expects immediate confirmation
- Need to respond to real-time events (traffic, delays)

**Implementation Pattern**:

```python
from fastapi import FastAPI, BackgroundTasks
import asyncio
from typing import List

app = FastAPI()

class RealtimeRouter:
    def __init__(self):
        self.current_routes = {}
        self.optimization_lock = asyncio.Lock()
        self.last_optimization = time.time()
        self.min_optimization_interval = 30  # seconds

    async def add_order(self, order: Order) -> RouteAssignment:
        """
        Fast insertion heuristic for immediate response.
        """
        # Find best vehicle/route for insertion
        best_route = None
        best_cost_increase = float('inf')

        for vehicle_id, route in self.current_routes.items():
            # Quick feasibility check
            if not self.is_feasible(route, order):
                continue

            # Calculate insertion cost (fast heuristic)
            cost_increase = self.calculate_insertion_cost(route, order)

            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_route = (vehicle_id, route)

        if best_route:
            vehicle_id, route = best_route
            # Insert order into route
            self.insert_order(route, order)

            # Trigger background re-optimization if threshold met
            if self.should_reoptimize():
                await self.trigger_reoptimization()

            return RouteAssignment(
                order_id=order.id,
                vehicle_id=vehicle_id,
                eta=self.calculate_eta(route, order)
            )
        else:
            # Cannot fit in existing routes, need new vehicle
            return await self.assign_new_vehicle(order)

    def should_reoptimize(self) -> bool:
        """Decide if full re-optimization is warranted."""
        elapsed = time.time() - self.last_optimization

        # Re-optimize every 30 seconds minimum
        if elapsed < self.min_optimization_interval:
            return False

        # Check if quality has degraded significantly
        current_cost = self.calculate_total_cost()
        baseline_cost = self.baseline_cost

        if current_cost > baseline_cost * 1.15:  # 15% degradation
            return True

        return elapsed > 300  # Or every 5 minutes

    async def trigger_reoptimization(self):
        """Background task for full re-optimization."""
        async with self.optimization_lock:
            # Extract all pending stops from current routes
            all_stops = self.extract_pending_stops()

            # Run full optimization (with time limit)
            solution = await self.optimize(
                stops=all_stops,
                current_routes=self.current_routes,
                time_limit_seconds=5
            )

            # Only apply if significantly better and not too disruptive
            if self.should_apply_solution(solution):
                await self.apply_solution(solution)
                self.last_optimization = time.time()
                self.baseline_cost = solution.total_cost

@app.post("/orders")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    router = get_router_instance()

    # Fast initial assignment (<100ms)
    assignment = await router.add_order(order)

    return {
        "order_id": order.id,
        "vehicle_id": assignment.vehicle_id,
        "estimated_arrival": assignment.eta,
        "status": "assigned"
    }
```

**Characteristics**:
- **Response Time**: <100ms for assignment, 1-5 sec for optimization
- **Solution Quality**: 85-95% of optimal (trade-off for speed)
- **Flexibility**: High (continuous re-optimization)
- **Scalability**: Requires careful architecture

---

## Scalability Strategies

### Horizontal Scaling

**Pattern**: Partition problem space for parallel processing

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

class DistributedRouter:
    def __init__(self, num_workers=None):
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.num_workers)

    def optimize_large_problem(self, stops, vehicles):
        """
        Split problem into geographic zones and solve in parallel.
        """
        # Geographic clustering
        zones = self.cluster_by_geography(stops, num_clusters=self.num_workers)

        # Submit optimization jobs to worker pool
        futures = []
        for zone_id, zone_stops in zones.items():
            future = self.executor.submit(
                optimize_zone,
                zone_stops,
                vehicles,
                zone_id
            )
            futures.append(future)

        # Collect results
        zone_solutions = []
        for future in as_completed(futures):
            solution = future.result()
            zone_solutions.append(solution)

        # Merge solutions and optimize inter-zone boundaries
        final_solution = self.merge_solutions(zone_solutions)

        return final_solution

    def cluster_by_geography(self, stops, num_clusters):
        """Use K-means to create geographic zones."""
        from sklearn.cluster import KMeans

        coords = np.array([[s.location.lat, s.location.lon] for s in stops])
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        labels = kmeans.fit_predict(coords)

        zones = {}
        for stop, label in zip(stops, labels):
            if label not in zones:
                zones[label] = []
            zones[label].append(stop)

        return zones
```

### Caching Strategy

**Pattern**: Cache intermediate results for speed

```python
from functools import lru_cache
import hashlib
import json

class CachedDistanceCalculator:
    def __init__(self, maps_client):
        self.client = maps_client
        self.cache = {}  # In production, use Redis

    @lru_cache(maxsize=10000)
    def get_distance(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """Cache distance calculations."""
        key = self._cache_key(origin_lat, origin_lon, dest_lat, dest_lon)

        if key in self.cache:
            return self.cache[key]

        # Call external API
        distance = self.client.distance_matrix(
            origins=[(origin_lat, origin_lon)],
            destinations=[(dest_lat, dest_lon)]
        )

        self.cache[key] = distance
        return distance

    def _cache_key(self, *coords):
        """Create cache key from coordinates (rounded to reduce variations)."""
        rounded = [round(c, 4) for c in coords]  # ~11 meter precision
        return tuple(rounded)

    def precompute_matrix(self, locations):
        """Pre-warm cache with all pairwise distances."""
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                self.get_distance(
                    loc1.lat, loc1.lon,
                    loc2.lat, loc2.lon
                )
```

### Database Optimization

**Pattern**: Efficient data access patterns

```sql
-- Spatial indexing for location queries
CREATE INDEX idx_stops_location ON stops USING GIST(location);

-- Fetch nearby pending stops efficiently
SELECT s.id, s.location, s.demand, s.time_window
FROM stops s
WHERE s.status = 'pending'
  AND ST_DWithin(
    s.location::geography,
    ST_Point(-74.0060, 40.7128)::geography,
    50000  -- 50km radius
  )
ORDER BY s.priority DESC, s.time_window_start ASC
LIMIT 500;

-- Materialized view for daily optimization
CREATE MATERIALIZED VIEW daily_optimization_input AS
SELECT
  s.*,
  c.service_level,
  c.preferred_time_window
FROM stops s
JOIN customers c ON s.customer_id = c.id
WHERE s.scheduled_date = CURRENT_DATE + INTERVAL '1 day'
  AND s.status = 'pending';

-- Refresh before optimization
REFRESH MATERIALIZED VIEW daily_optimization_input;
```

---

## Fallback and Resilience

### Graceful Degradation

```python
class ResilientRouter:
    def __init__(self, primary_optimizer, fallback_optimizer):
        self.primary = primary_optimizer
        self.fallback = fallback_optimizer
        self.timeout = 5.0  # seconds

    async def optimize(self, stops, vehicles):
        try:
            # Try advanced optimizer with timeout
            solution = await asyncio.wait_for(
                self.primary.solve(stops, vehicles),
                timeout=self.timeout
            )
            return solution

        except asyncio.TimeoutError:
            logger.warning("Primary optimizer timeout, using fallback")
            # Fall back to fast heuristic
            solution = await self.fallback.solve(stops, vehicles)
            solution.metadata = {"method": "fallback", "reason": "timeout"}
            return solution

        except Exception as e:
            logger.error(f"Primary optimizer failed: {e}")
            # Fall back to simple nearest neighbor
            solution = self.nearest_neighbor_solution(stops, vehicles)
            solution.metadata = {"method": "emergency", "reason": str(e)}
            return solution
```

### Circuit Breaker Pattern

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, use fallback
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

---

## Monitoring and Observability

### Key Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
optimization_requests = Counter(
    'route_optimization_requests_total',
    'Total number of optimization requests',
    ['status', 'method']
)

# Performance metrics
optimization_duration = Histogram(
    'route_optimization_duration_seconds',
    'Time spent optimizing routes',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Solution quality metrics
route_distance = Histogram(
    'route_total_distance_miles',
    'Total distance of optimized routes',
    buckets=[10, 25, 50, 100, 200, 500, 1000]
)

stops_per_route = Histogram(
    'route_stops_count',
    'Number of stops per route',
    buckets=[5, 10, 20, 30, 50, 100]
)

vehicle_utilization = Gauge(
    'vehicle_capacity_utilization_ratio',
    'Average vehicle capacity utilization'
)

# Usage
def optimize_with_metrics(stops, vehicles):
    start_time = time.time()

    try:
        solution = optimize(stops, vehicles)

        # Record metrics
        duration = time.time() - start_time
        optimization_duration.observe(duration)
        optimization_requests.labels(status='success', method='primary').inc()

        route_distance.observe(solution.total_distance)

        for route in solution.routes:
            stops_per_route.observe(len(route.stops))

        avg_utilization = sum(r.load / v.capacity
                             for r, v in zip(solution.routes, vehicles)) / len(vehicles)
        vehicle_utilization.set(avg_utilization)

        return solution

    except Exception as e:
        optimization_requests.labels(status='error', method='primary').inc()
        raise e
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

def optimize_and_log(order_ids, vehicle_ids):
    log = logger.bind(
        optimization_id=generate_id(),
        num_orders=len(order_ids),
        num_vehicles=len(vehicle_ids)
    )

    log.info("optimization.started")

    start = time.time()
    solution = optimize(orders, vehicles)
    duration = time.time() - start

    log.info(
        "optimization.completed",
        duration_seconds=duration,
        total_distance=solution.total_distance,
        total_cost=solution.total_cost,
        num_routes=len(solution.routes),
        unassigned_stops=len(solution.unassigned_stops)
    )

    return solution
```

---

## Integration Patterns

### API Design for Route Optimization Service

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Route Optimization API")

class OptimizationRequest(BaseModel):
    stops: List[Stop]
    vehicles: List[Vehicle]
    options: Optional[OptimizationOptions] = None

class OptimizationResponse(BaseModel):
    optimization_id: str
    status: str  # "completed", "pending", "failed"
    solution: Optional[Solution] = None
    error: Optional[str] = None

# Synchronous API (small problems)
@app.post("/api/v1/optimize", response_model=OptimizationResponse)
async def optimize_sync(request: OptimizationRequest):
    """
    Synchronous optimization for small problems (<100 stops).
    Returns solution immediately within 5 seconds.
    """
    if len(request.stops) > 100:
        raise HTTPException(
            status_code=400,
            detail="Use async endpoint for >100 stops"
        )

    try:
        solution = await optimizer.solve(
            stops=request.stops,
            vehicles=request.vehicles,
            time_limit=5
        )

        return OptimizationResponse(
            optimization_id=str(uuid.uuid4()),
            status="completed",
            solution=solution
        )
    except Exception as e:
        return OptimizationResponse(
            optimization_id=str(uuid.uuid4()),
            status="failed",
            error=str(e)
        )

# Asynchronous API (large problems)
@app.post("/api/v1/optimize/async", response_model=OptimizationResponse)
async def optimize_async(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Asynchronous optimization for large problems.
    Returns optimization_id immediately, solution retrieved via GET.
    """
    optimization_id = str(uuid.uuid4())

    # Store request
    await store_optimization_request(optimization_id, request)

    # Start background optimization
    background_tasks.add_task(
        run_optimization_async,
        optimization_id,
        request
    )

    return OptimizationResponse(
        optimization_id=optimization_id,
        status="pending"
    )

@app.get("/api/v1/optimize/{optimization_id}", response_model=OptimizationResponse)
async def get_optimization_result(optimization_id: str):
    """Poll for optimization results."""
    result = await get_optimization_status(optimization_id)

    if not result:
        raise HTTPException(status_code=404, detail="Optimization not found")

    return result

# WebSocket for real-time updates
@app.websocket("/api/v1/optimize/ws/{optimization_id}")
async def optimization_updates(websocket: WebSocket, optimization_id: str):
    await websocket.accept()

    # Subscribe to optimization progress
    async for update in optimization_progress_stream(optimization_id):
        await websocket.send_json({
            "optimization_id": optimization_id,
            "status": update.status,
            "progress": update.progress,
            "current_best": update.current_best_solution
        })
```

---

## Deployment Strategies

### Blue-Green Deployment

```yaml
# Kubernetes deployment for blue-green routing optimization service
apiVersion: v1
kind: Service
metadata:
  name: route-optimizer
spec:
  selector:
    app: route-optimizer
    version: blue  # Switch to 'green' for deployment
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: route-optimizer-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: route-optimizer
      version: blue
  template:
    metadata:
      labels:
        app: route-optimizer
        version: blue
    spec:
      containers:
      - name: optimizer
        image: route-optimizer:v1.2.3
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        env:
        - name: OPTIMIZATION_TIMEOUT
          value: "30"
        - name: MAX_STOPS_PER_REQUEST
          value: "500"
```

### Canary Deployment

```python
# Route a small percentage of traffic to new algorithm
from random import random

class CanaryRouter:
    def __init__(self, stable_optimizer, canary_optimizer, canary_percentage=5):
        self.stable = stable_optimizer
        self.canary = canary_optimizer
        self.canary_percentage = canary_percentage

    async def optimize(self, request):
        # Randomly select canary vs stable
        use_canary = (random() * 100) < self.canary_percentage

        if use_canary:
            try:
                solution = await self.canary.solve(request)
                solution.metadata["algorithm"] = "canary"

                # Also run stable for comparison (don't return)
                stable_solution = await self.stable.solve(request)
                self.compare_solutions(solution, stable_solution)

                return solution
            except Exception as e:
                logger.error(f"Canary failed, falling back: {e}")
                # Fall back to stable
                return await self.stable.solve(request)
        else:
            solution = await self.stable.solve(request)
            solution.metadata["algorithm"] = "stable"
            return solution

    def compare_solutions(self, canary, stable):
        """Log comparison metrics for analysis."""
        logger.info(
            "canary.comparison",
            canary_cost=canary.total_cost,
            stable_cost=stable.total_cost,
            cost_diff_percent=(canary.total_cost - stable.total_cost) / stable.total_cost * 100,
            canary_distance=canary.total_distance,
            stable_distance=stable.total_distance
        )
```

---

## Conclusion

Successful production deployment of route optimization systems requires careful consideration of architecture, scalability, resilience, and monitoring. The patterns described here provide a foundation for building robust, scalable routing systems that deliver value in real-world logistics operations.

### Key Takeaways

1. **Start Simple**: Begin with batch optimization and simple heuristics before adding real-time complexity
2. **Design for Failure**: Implement fallbacks, circuit breakers, and graceful degradation
3. **Monitor Everything**: Track both technical metrics (latency, errors) and business metrics (cost savings, utilization)
4. **Scale Gradually**: Use canary deployments and A/B testing when introducing new algorithms
5. **Optimize for Business Value**: Sometimes a "good enough" solution delivered quickly is better than optimal solution delivered slowly
