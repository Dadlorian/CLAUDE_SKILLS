# Ride-Hailing Algorithms: Matching and Dispatch Optimization

## Executive Summary
Ride-hailing platforms operate as two-sided marketplaces requiring real-time optimization of driver-passenger matching. This document covers fundamental and advanced algorithms used by Uber, Lyft, Didi, and other platforms to minimize wait times, maximize utilization, and ensure marketplace efficiency.

## Core Matching Problems

### 1. Online Bipartite Matching
**Problem Statement**: Match incoming ride requests to available drivers in real-time, optimizing for system-wide metrics.

**Objective Functions**:
- Minimize passenger wait time (pickup ETA)
- Minimize driver deadhead distance (distance to pickup)
- Maximize long-term driver utilization
- Balance supply-demand across zones
- Optimize for future demand (anticipatory matching)

**Algorithms**:

#### Greedy Nearest-Driver Matching
```
Input: New ride request R at location L
Output: Assigned driver D

1. Query available drivers within radius r of L
2. Filter by vehicle type, rating, driver preferences
3. Calculate ETA for each driver to L
4. Select driver with minimum ETA
5. Send dispatch notification to D
6. Update driver state to "assigned"
```

**Pros**: Simple, fast (O(k) for k nearby drivers), intuitive
**Cons**: Locally optimal, may strand drivers in low-demand areas, ignores future demand

#### Batch Matching (Market Clearing)
```
Input: Set of N ride requests, M available drivers
Output: Matching M that maximizes global utility

Every T seconds (e.g., T=5):
1. Collect pending requests R = {r1, r2, ..., rn}
2. Identify available drivers D = {d1, d2, ..., dm}
3. Construct bipartite graph G = (R ∪ D, E)
   - Edge (ri, dj) has weight w(ri, dj) = utility of match
4. Solve assignment problem:
   maximize Σ w(ri, dj) * x(ri, dj)
   subject to:
     - Each request matched to at most one driver
     - Each driver matched to at most one request
5. Dispatch matched pairs
6. Return unmatched requests to queue
```

**Weight Function Design**:
```python
w(request, driver) =
    α * (1 / pickup_eta) +           # Faster pickup is better
    β * (1 / pickup_distance) +      # Closer driver is better
    γ * future_demand(driver.zone) + # Keep drivers in high-demand zones
    δ * driver_rating +              # Prefer higher-rated drivers
    ε * request_wait_time            # Prioritize long-waiting requests
```

**Solving Methods**:
- **Hungarian Algorithm**: O(n³) exact solution for balanced assignment
- **Auction Algorithm**: O(nk) for sparse graphs, parallel-friendly
- **Linear Programming**: Flexible constraints, handles complex objectives
- **Greedy Approximations**: Sub-optimal but fast for large-scale systems

#### Online Primal-Dual Algorithm
For large-scale systems, online algorithms provide theoretical guarantees:

```
Competitive Ratio: 1 - 1/e ≈ 0.632 for random arrival model

Algorithm:
- Maintain dual variables yj for each driver j
- On request i arrival:
  1. Find driver j* that maximizes (wij - yj)
  2. If (wij* - yj*) > 0:
     - Match i to j*
     - Update yj* = yj* + Δ (penalty for assignment)
  3. Else: reject request
```

### 2. Zone-Based Matching

Modern platforms partition cities into zones (hexagons, S2 cells) for scalability:

```
Zone Structure:
- City divided into H hexagonal zones
- Each zone maintains:
  * Queue of available drivers (priority: idle time)
  * Queue of pending requests (priority: wait time)
  * Demand forecast (next 15/30/60 minutes)
  * Supply forecast (expected driver arrivals)

Matching Process:
1. Request arrives in zone z
2. Check for available drivers in z
3. If drivers available: dispatch best match
4. Else: search adjacent zones (1-hop neighbors)
5. If still no match: search 2-hop neighbors
6. If still no match: add to zone queue
7. On driver becoming available:
   - Check local zone queue first
   - Consider pre-positioning to high-demand zone
```

### 3. Advanced Matching Strategies

#### Predictive Pre-Positioning
```
Goal: Position idle drivers anticipating future demand

Model:
- Predict demand D(z, t+Δt) for each zone z at future time t+Δt
- Predict supply S(z, t+Δt) (drivers becoming available, entering zone)
- Calculate deficit: Deficit(z, t+Δt) = D(z, t+Δt) - S(z, t+Δt)

Repositioning:
for each idle driver d in zone z:
  if Deficit(z, t+15min) < 0:  # Surplus in current zone
    z* = argmax(Deficit(z', t+15min) - travel_time(z, z'))
    if value(z*) > value(z):
      send_repositioning_nudge(d, z*)
```

**Implementation Notes**:
- Use subtle incentives (surge notifications, bonus zones) rather than mandatory moves
- Consider driver preferences and historical response rates
- Balance exploration (new zones) vs exploitation (known profitable zones)

#### Contextual Matching (Machine Learning)
Train models to predict ride value and optimize match quality:

```
Features:
- Request: pickup location, time, destination estimate, rider rating, historical behavior
- Driver: current location, rating, acceptance rate, vehicle type, earnings today
- Context: time of day, day of week, weather, events, traffic conditions
- Market: current supply-demand ratio, active surge zones

Model:
- Predicted ride fare
- Predicted trip distance/duration
- Predicted driver acceptance probability
- Predicted rider cancellation probability
- Predicted driver post-trip position value

Matching Score:
score(request, driver) =
    E[fare] * P(acceptance) * (1 - P(cancellation)) +
    future_value(driver.position_after_trip)
```

## Pooling and Shared Rides

### Vehicle Routing Problem (VRP) Formulation
```
State: Vehicle v carrying passengers P = {p1, ..., pk}, k ≤ capacity
Request: New passenger r with pickup A, dropoff B

Feasibility Constraints:
1. Vehicle capacity: |P| + 1 ≤ capacity
2. Max detour: detour for existing passengers ≤ threshold (e.g., 5 minutes)
3. Wait time: ETA to pickup A ≤ max_wait (e.g., 10 minutes)
4. Compatibility: Rider preferences (e.g., gender matching in some markets)

Insertion Cost:
cost = travel_time(route_with_r) - travel_time(route_without_r)

Algorithm (Greedy Insertion):
1. For new request r, find all eligible vehicles V'
2. For each v in V':
   - Try all insertion positions for pickup A and dropoff B
   - Calculate cost and impact on existing passengers
   - Check feasibility constraints
3. Select vehicle and insertion position minimizing system cost
4. If no feasible match: dispatch as solo ride
```

### Batch Optimization for Pooling
```
Input: Set of N active requests, M vehicles (some with passengers)
Output: Assignment minimizing total travel time

Every 30 seconds:
1. Enumerate feasible insertion options for each request-vehicle pair
2. Formulate as Set Packing Problem:
   - Each "pack" = valid vehicle route serving subset of requests
   - Constraint: Each request served by exactly one pack
   - Objective: Minimize total travel time
3. Solve using:
   - Branch-and-bound for small instances
   - Genetic algorithms for larger instances
   - Greedy heuristics for very large scale
4. Implement route changes carefully (avoid excessive re-routing)
```

## Dispatch Acceptance Optimization

### Predicting Driver Acceptance
```
Features:
- Distance to pickup
- Direction match (pickup aligned with driver's heading)
- Historical earnings in dropoff zone
- Time since last trip
- Earnings today vs. driver's goal
- Surge multiplier
- Rider rating

Model: Logistic Regression, Gradient Boosted Trees, Neural Network
Output: P(acceptance | features)

Dispatch Strategy:
1. Rank drivers by matching score
2. Adjust for acceptance probability:
   adjusted_score = matching_score * P(acceptance)^α
   (α > 1 penalizes low acceptance probability)
3. Dispatch to top k drivers simultaneously (if allowed by regulations)
4. First to accept wins; cancel others
```

### Sequential vs. Parallel Dispatch
```
Sequential (Traditional):
- Offer to best driver
- Wait for response (15-30 seconds)
- If rejected/timed out, offer to next driver
- Pros: Simple, one driver per request
- Cons: High latency if multiple rejections

Parallel (Multiple Offers):
- Offer to top k drivers simultaneously (k=2-5)
- First to accept wins
- Pros: Lower wait time, higher acceptance rate
- Cons: Driver frustration (offer cancellations), regulatory concerns

Hybrid (Waterfall):
- Offer to driver 1
- After T seconds (e.g., T=5), also offer to driver 2
- After 2T seconds, offer to driver 3
- First to accept wins
- Balances latency and driver experience
```

## Performance Metrics

### Matching Efficiency
```
Match Rate = successful_matches / total_requests
Time to Match = P50, P95 time from request to driver assignment
Match Quality = 1 / avg_pickup_ETA
Utilization = driver_time_with_passenger / driver_active_time
```

### Algorithmic KPIs
```
- Pickup ETA Accuracy: |predicted_ETA - actual_ETA| < threshold
- Driver Efficiency: minimize deadhead miles per trip
- Request Fulfillment: % of requests successfully matched
- Supply-Demand Balance: minimize zones with extreme imbalances
```

## Real-World Considerations

### System Constraints
- **Latency Requirements**: Matching decisions in <100ms
- **Scalability**: Handle 1M+ requests/hour in peak markets
- **Reliability**: Graceful degradation under load
- **Fairness**: Avoid driver/rider discrimination, comply with regulations

### Market Dynamics
- **Driver Gaming**: Avoid exploitable patterns (e.g., strategic positioning)
- **Surge Interaction**: Matching affects and is affected by pricing
- **Multi-App Behavior**: Drivers work for multiple platforms simultaneously
- **Geographic Constraints**: Physical barriers (rivers, highways), traffic patterns

### Regulatory Compliance
- **Non-discrimination**: Fair matching across rider/driver demographics
- **Transparency**: Explainable dispatch decisions (GDPR, CCPA)
- **Driver Classification**: Independent contractor vs. employee implications
- **Accessibility**: ADA compliance, wheelchair-accessible vehicle prioritization

## Research Frontiers

### Learning-Based Optimization
```
- Reinforcement Learning for dispatch policies
- Deep Q-Networks (DQN) for sequential decision-making
- Multi-agent RL for coordinated fleet behavior
- Imitation learning from expert dispatchers
```

### Fairness and Equity
```
- Individual fairness: similar drivers/riders treated similarly
- Group fairness: demographic parity in service quality
- Long-term fairness: earnings distribution across driver population
- Spatial equity: service quality across neighborhoods
```

### Resilience and Robustness
```
- Adversarial robustness: resistant to strategic manipulation
- Uncertainty handling: stochastic arrival rates, traffic variability
- Cold-start problems: new markets, limited historical data
- Disruption response: accidents, events, weather
```

## Implementation Architecture

```
High-Level System Flow:

1. Ride Request → API Gateway
2. Request Validation → Rate Limiting → Pricing Engine
3. Request → Matching Service
   - Query Driver Index (geospatial DB)
   - Filter available drivers (state, preferences)
   - Compute match scores
   - Select optimal driver(s)
4. Dispatch Notification → Driver Mobile App
5. Driver Response → Update State Management
6. Match Confirmed → Tracking & ETA Service
7. Trip Completion → Payment → Rating → Analytics

Key Components:
- Geospatial Index: PostGIS, Tile38, Redis Geo
- State Management: Redis, DynamoDB for driver/request state
- Matching Engine: In-memory compute, optimized for latency
- Event Bus: Kafka for state changes, analytics
- ML Serving: TensorFlow Serving, AWS SageMaker for prediction models
```

## References

1. Uber Engineering: "Dispatch at Uber" - https://eng.uber.com/tag/dispatch/
2. Lyft Engineering: "Marketplace Matching" - https://eng.lyft.com/
3. Algorithms for Matching in Marketplaces (EC'19 Tutorial)
4. "Online Matching and Ad Allocation" - Mehta (2013)
5. "The Power of Uncertainty: Information, Competition and Market Structure" - Cachon, Daniels, Lobel (2017)
6. "Spatial Pricing of Ride-Sourcing Services" - Bai et al. (2019)

## Appendix: Complexity Analysis

```
Greedy Matching: O(k) for k nearby drivers
Hungarian Algorithm: O(n³)
Auction Algorithm: O(nk) for k iterations
VRP Insertion: O(n) per request for n existing waypoints
Batch VRP: NP-Hard, exponential worst case
```

---

**Document Version**: 1.0
**Classification**: Technical Reference
**Last Updated**: 2025-11
