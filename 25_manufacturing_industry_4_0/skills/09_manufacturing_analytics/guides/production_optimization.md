# AI-Driven Production Scheduling and Optimization Guide

## Executive Summary

This guide provides a comprehensive approach to implementing AI-driven production scheduling and optimization. Advanced algorithms intelligently allocate resources, minimize downtime, reduce changeovers, and maximize throughput while meeting due date commitments.

### Expected Benefits
- 15-25% improvement in production throughput
- 20-30% reduction in changeover time
- 10-20% reduction in work-in-progress (WIP) inventory
- 5-15 percentage point improvement in on-time delivery
- 10-15% reduction in production costs

### Implementation Timeline
- **Phase 1** (Weeks 1-2): Problem definition and data collection
- **Phase 2** (Weeks 3-6): Algorithm development and testing
- **Phase 3** (Weeks 7-10): Pilot deployment and validation
- **Phase 4** (Weeks 11-16): Full deployment and optimization

---

## Phase 1: Problem Definition and Data Collection

### Step 1.1: Understand Current Operations

**Current State Assessment**:
```python
import pandas as pd
import numpy as np

# Load production data
production_data = pd.read_csv('production_history.csv')

# Analyze current performance
print("Current Production Metrics:")
print(f"  Total orders: {production_data.shape[0]}")
print(f"  Average order size: {production_data['quantity'].mean():.0f} units")
print(f"  Average cycle time: {production_data['cycle_time'].mean():.1f} hours")
print(f"  Average setup time: {production_data['setup_time'].mean():.1f} hours")

# On-time delivery analysis
production_data['on_time'] = production_data['completion_date'] <= production_data['due_date']
otd = production_data['on_time'].mean() * 100
print(f"\nCurrent On-Time Delivery: {otd:.1f}%")

# WIP analysis
production_data['wip_time'] = (
    production_data['completion_date'] - production_data['start_date']
).dt.total_seconds() / 3600
print(f"Average WIP Time: {production_data['wip_time'].mean():.1f} hours")

# Equipment utilization
print("\nEquipment Utilization:")
equipment_util = production_data.groupby('equipment')['run_time'].sum() / production_data['run_time'].sum()
print(equipment_util.sort_values(ascending=False))
```

**Production Constraints**:
1. **Equipment Constraints**:
   - Available equipment and capacity
   - Sequence-dependent setup times
   - Maintenance schedules
   - Equipment capabilities (what products it can run)

2. **Resource Constraints**:
   - Labor availability and skill requirements
   - Material availability and lead times
   - Batch size constraints
   - Quality hold requirements

3. **Temporal Constraints**:
   - Order due dates
   - Delivery time requirements
   - Production windows
   - Shift schedules

4. **Business Constraints**:
   - Minimum batch sizes
   - Family/campaign production rules
   - Priority rules (customer importance)
   - Quality first rules

### Step 1.2: Data Collection

**Data Requirements**:

**Historical Production Data**:
```python
# Track each job/order through production
production_data = pd.DataFrame({
    'job_id': [1, 2, 3, ...],
    'product_id': ['A123', 'B456', ...],
    'equipment': ['Mill1', 'Assembly2', ...],
    'order_date': pd.to_datetime([...]),
    'due_date': pd.to_datetime([...]),
    'start_date': pd.to_datetime([...]),
    'completion_date': pd.to_datetime([...]),
    'quantity': [100, 500, ...],
    'process_time': [2.5, 3.2, ...],  # hours
    'setup_time': [0.5, 1.0, ...],    # hours
    'previous_job': ['B456', 'A123', ...],  # for setup time calculation
})
```

**Equipment Capability Matrix**:
```python
# Define which equipment can run which products
equipment_capability = pd.DataFrame({
    'product_id': ['A123', 'A123', 'B456', 'B456'],
    'equipment': ['Mill1', 'Mill2', 'Assembly1', 'Assembly2'],
    'setup_time': [0.5, 0.6, 1.0, 0.9],
    'production_rate': [50, 45, 100, 95],  # units per hour
})
```

**Setup Time Matrix**:
```python
# Sequence-dependent setup times
setup_matrix = pd.DataFrame({
    'from_product': ['A123', 'A123', 'B456', 'B456'],
    'to_product': ['B456', 'C789', 'A123', 'C789'],
    'setup_time': [1.0, 1.5, 0.8, 1.2],  # hours
})
```

### Step 1.3: Problem Formulation

**Optimization Objective**:

Choose one or more objectives:
```python
# Define optimization problem
class ProductionSchedulingProblem:
    def __init__(self, jobs, equipment, constraints):
        self.jobs = jobs
        self.equipment = equipment
        self.constraints = constraints

    def objective_minimize_makespan(self, schedule):
        """Minimize total time to complete all jobs"""
        return max([self._job_completion_time(j, schedule) for j in self.jobs])

    def objective_minimize_tardiness(self, schedule):
        """Minimize total lateness (sum of days late)"""
        tardiness = 0
        for job in self.jobs:
            completion = self._job_completion_time(job, schedule)
            due_date = job.due_date
            if completion > due_date:
                tardiness += (completion - due_date).days
        return tardiness

    def objective_minimize_wip(self, schedule):
        """Minimize average work-in-progress time"""
        wip_times = []
        for job in self.jobs:
            start = self._job_start_time(job, schedule)
            completion = self._job_completion_time(job, schedule)
            wip_times.append((completion - start).total_seconds() / 3600)
        return np.mean(wip_times)

    def objective_minimize_changeovers(self, schedule):
        """Minimize number of equipment changeovers"""
        changeovers = 0
        for equipment in self.equipment:
            jobs_on_equip = [j for j in self.jobs if schedule[j] == equipment]
            changeovers += len(jobs_on_equip) - 1  # minus 1 because transitions are changeovers
        return changeovers

    def _job_completion_time(self, job, schedule):
        """Calculate when job finishes"""
        # Implementation
        pass

    def _job_start_time(self, job, schedule):
        """Calculate when job starts"""
        # Implementation
        pass
```

---

## Phase 2: Algorithm Development

### Step 2.1: Constraint Programming Solution

**Mixed Integer Programming Formulation**:

```python
from pulp import *

def create_scheduling_model(jobs, equipment, setup_times, due_dates, max_hours=8*24):
    """
    Create a Mixed Integer Programming model for job shop scheduling
    """
    # Decision variables
    # x[i,j,t] = 1 if job i runs on equipment j starting at time t
    start_times = {}
    for job in jobs:
        start_times[job] = LpVariable(f"start_{job}", lowBound=0)

    # Objective: Minimize makespan
    makespan = LpVariable("makespan", lowBound=0)

    model = LpProblem("Production_Scheduling", LpMinimize)

    # Objective function
    model += makespan

    # Constraints
    # 1. Each job must be assigned to one equipment
    for job in jobs:
        available_equip = [e for e in equipment if can_run(job, e)]
        # ... constraint formulation

    # 2. No overlapping on equipment
    for equip in equipment:
        jobs_on_equip = [j for j in jobs if can_run(j, equip)]
        for i in range(len(jobs_on_equip)):
            for j in range(i + 1, len(jobs_on_equip)):
                # job i and j cannot overlap on same equipment
                # ... constraint formulation

    # 3. Due date constraints (soft - penalize lateness)
    for job in jobs:
        # ... constraint formulation

    # 4. Setup time between jobs
    # ... constraint formulation

    return model

# Solve
# model.solve(PULP_CBC_CMD(msg=0))
```

### Step 2.2: Reinforcement Learning Approach

**RL Agent for Scheduling**:

```python
import numpy as np
from collections import deque
import tensorflow as tf

class SchedulingAgent:
    """
    Reinforcement Learning agent for job scheduling
    Uses Deep Q-Network (DQN)
    """
    def __init__(self, num_jobs, num_equipment, state_size=64):
        self.num_jobs = num_jobs
        self.num_equipment = num_equipment
        self.state_size = state_size

        # Q-Network
        self.q_network = self._build_network()
        self.target_network = self._build_network()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

        # Experience replay
        self.memory = deque(maxlen=2000)
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.gamma = 0.95  # discount factor

    def _build_network(self):
        """Build the Q-Network"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(self.state_size,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(self.num_equipment, activation='linear')
        ])
        return model

    def encode_state(self, jobs, equipment_states, current_time):
        """
        Encode production state into a fixed-size vector
        """
        state_vector = []

        # Job characteristics
        for job in jobs:
            state_vector.extend([
                job.processing_time,
                job.due_date_offset,
                job.priority,
                job.num_required_steps
            ])

        # Equipment states
        for equip in equipment_states:
            state_vector.extend([
                equip.available_at,
                equip.utilization,
                equip.num_pending_jobs
            ])

        return np.array(state_vector[:self.state_size])

    def select_action(self, state, available_actions):
        """
        Epsilon-greedy action selection
        """
        if np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(available_actions)
        else:
            # Exploit: best Q-value action
            q_values = self.q_network.predict(state.reshape(1, -1))[0]
            return available_actions[np.argmax(q_values[available_actions])]

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        """Train network from random samples of memory"""
        if len(self.memory) < batch_size:
            return

        minibatch = np.random.choice(len(self.memory), batch_size, replace=False)

        states = np.array([self.memory[i][0] for i in minibatch])
        actions = np.array([self.memory[i][1] for i in minibatch])
        rewards = np.array([self.memory[i][2] for i in minibatch])
        next_states = np.array([self.memory[i][3] for i in minibatch])
        dones = np.array([self.memory[i][4] for i in minibatch])

        # Predict Q-values for starting state
        target = self.q_network.predict(states)

        # Predict Q-values for next state
        target_next = self.target_network.predict(next_states)

        for i in range(batch_size):
            if dones[i]:
                target[i][actions[i]] = rewards[i]
            else:
                target[i][actions[i]] = rewards[i] + self.gamma * np.max(target_next[i])

        # Train the network
        with tf.GradientTape() as tape:
            predictions = self.q_network(states)
            loss = tf.keras.losses.MSE(target, predictions)

        gradients = tape.gradient(loss, self.q_network.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.q_network.trainable_variables))

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target_network(self):
        """Update target network weights"""
        self.target_network.set_weights(self.q_network.get_weights())

# Training loop
agent = SchedulingAgent(num_jobs=100, num_equipment=10)

for episode in range(1000):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        state_encoded = agent.encode_state(state)
        available_actions = env.get_available_actions()
        action = agent.select_action(state_encoded, available_actions)

        next_state, reward, done, info = env.step(action)
        agent.remember(state_encoded, action, reward, agent.encode_state(next_state), done)
        agent.replay(batch_size=32)

        state = next_state
        total_reward += reward

    if episode % 10 == 0:
        agent.update_target_network()
        print(f"Episode {episode}, Total Reward: {total_reward}")
```

### Step 2.3: Heuristic Methods

**Greedy Algorithms**:

```python
class GreedyScheduler:
    """
    Fast heuristic scheduling using greedy rules
    """
    def __init__(self, jobs, equipment, setup_times):
        self.jobs = jobs
        self.equipment = equipment
        self.setup_times = setup_times

    def schedule_by_earliest_due_date(self):
        """
        Prioritize jobs with earliest due dates
        """
        schedule = {}
        sorted_jobs = sorted(self.jobs, key=lambda j: j.due_date)

        equipment_available_at = {eq: 0 for eq in self.equipment}

        for job in sorted_jobs:
            # Find equipment that can run this job and becomes available earliest
            best_equipment = None
            earliest_available = float('inf')

            for equip in self.equipment:
                if self._can_run(job, equip):
                    available_at = equipment_available_at[equip]
                    if available_at < earliest_available:
                        earliest_available = available_at
                        best_equipment = equip

            # Schedule job on best equipment
            schedule[job.id] = {
                'equipment': best_equipment,
                'start_time': earliest_available
            }

            # Update equipment availability
            processing_time = self._get_processing_time(job, best_equipment)
            equipment_available_at[best_equipment] = earliest_available + processing_time

        return schedule

    def schedule_by_shortest_processing_time(self):
        """
        Prioritize jobs with shortest processing time
        """
        schedule = {}
        sorted_jobs = sorted(self.jobs, key=lambda j: self._get_avg_processing_time(j))
        # Similar implementation as above

        return schedule

    def _can_run(self, job, equipment):
        # Check if equipment can run this job
        pass

    def _get_processing_time(self, job, equipment):
        # Get processing time for job on equipment
        pass

    def _get_avg_processing_time(self, job):
        # Average processing time across equipment
        pass
```

---

## Phase 3: Pilot Deployment and Validation

### Step 3.1: Real-Time Optimization Framework

**Architecture**:

```python
class ProductionScheduler:
    """
    Real-time production scheduling system
    """
    def __init__(self, planning_horizon_hours=72):
        self.planning_horizon = planning_horizon_hours
        self.pending_orders = []
        self.scheduled_jobs = {}
        self.equipment_state = {}

    def add_order(self, order):
        """Add new order to scheduling"""
        self.pending_orders.append(order)
        self.reoptimize()

    def reoptimize(self, event='new_order'):
        """
        Run optimization when triggered by:
        - New order arrival
        - Equipment failure
        - Order cancellation
        - Scheduled time (e.g., hourly)
        """
        # Get current state
        current_schedule = self.scheduled_jobs
        pending = self.pending_orders

        # Run optimization
        if self._should_optimize(event):
            new_schedule = self._optimize(current_schedule, pending)

            # Calculate disruption cost
            disruption = self._calculate_disruption_cost(current_schedule, new_schedule)

            # Apply if improvement significant
            if self._is_improvement_worth(new_schedule, disruption):
                self.scheduled_jobs = new_schedule
                self._notify_updates()

    def _optimize(self, current_schedule, pending_orders):
        """
        Run optimization algorithm
        """
        # Choose algorithm based on problem size
        if len(pending_orders) < 50:
            # Use exact method for small problems
            return self._optimize_exact(current_schedule, pending_orders)
        else:
            # Use heuristic for large problems
            return self._optimize_heuristic(current_schedule, pending_orders)

    def _optimize_exact(self, current, pending):
        """Mixed Integer Programming solution"""
        # Create MIP model
        # Solve to optimality
        pass

    def _optimize_heuristic(self, current, pending):
        """Fast heuristic solution"""
        # Use greedy or RL approach
        pass

    def _should_optimize(self, event):
        """Decide if reoptimization is needed"""
        optimization_triggers = {
            'new_order': True,
            'equipment_failure': True,
            'order_cancellation': True,
            'scheduled': (self._time_since_last_optimization() > 60),  # 60 minutes
        }
        return optimization_triggers.get(event, False)

    def _calculate_disruption_cost(self, old_schedule, new_schedule):
        """
        Measure cost of rescheduling
        """
        changes = 0
        for job in old_schedule:
            if job in new_schedule:
                if old_schedule[job] != new_schedule[job]:
                    changes += 1
        return changes

    def _is_improvement_worth(self, new_schedule, disruption):
        """
        Evaluate if new schedule improvement justifies disruption
        """
        old_objective = self._evaluate_schedule(self.scheduled_jobs)
        new_objective = self._evaluate_schedule(new_schedule)
        disruption_cost = disruption * 100  # Cost per rescheduling

        improvement = (old_objective - new_objective) - disruption_cost
        return improvement > 0

    def _evaluate_schedule(self, schedule):
        """
        Calculate objective value (minimize tardiness + WIP)
        """
        # Implementation
        pass

    def get_current_schedule(self):
        """Return current production schedule for MES"""
        return self.scheduled_jobs

    def handle_equipment_failure(self, equipment_id, estimated_downtime):
        """React to equipment failure"""
        self.equipment_state[equipment_id]['available_at'] += estimated_downtime
        self.reoptimize(event='equipment_failure')

    def _notify_updates(self):
        """Send updates to MES and operators"""
        # Push to MES system
        # Alert operators of changes
        # Log schedule changes
        pass
```

### Step 3.2: Key Performance Indicators

**Monitoring Dashboard**:

```python
class SchedulingAnalytics:
    """
    Monitor optimization performance
    """
    def __init__(self):
        self.metrics_history = []

    def collect_metrics(self, schedule, actual_results):
        """
        Collect performance metrics from executed schedule
        """
        metrics = {
            'timestamp': datetime.now(),
            'makespan': self._calculate_makespan(actual_results),
            'on_time_delivery': self._calculate_otd(actual_results),
            'average_wip_time': self._calculate_wip(actual_results),
            'equipment_utilization': self._calculate_utilization(actual_results),
            'changeover_count': self._calculate_changeovers(actual_results),
            'schedule_adherence': self._calculate_adherence(schedule, actual_results),
            'total_setup_time': self._calculate_setup_time(actual_results),
        }
        self.metrics_history.append(metrics)
        return metrics

    def _calculate_makespan(self, results):
        """Total time to complete all jobs"""
        return max([r['completion_time'] for r in results])

    def _calculate_otd(self, results):
        """Percentage of jobs completed on time"""
        on_time = sum([1 for r in results if r['completion_time'] <= r['due_date']])
        return on_time / len(results) * 100

    def _calculate_wip(self, results):
        """Average work-in-progress time"""
        wip_times = [(r['completion_time'] - r['start_time']).total_seconds() / 3600
                     for r in results]
        return np.mean(wip_times)

    def _calculate_utilization(self, results):
        """Equipment utilization rate"""
        # ...
        pass

    def _calculate_changeovers(self, results):
        """Count changeovers between different products"""
        # ...
        pass

    def _calculate_adherence(self, schedule, actual):
        """Measure how closely actual follows planned schedule"""
        # ...
        pass

    def _calculate_setup_time(self, results):
        """Total setup/changeover time"""
        return sum([r['setup_time'] for r in results])

    def get_performance_summary(self):
        """Get summary metrics"""
        recent = self.metrics_history[-7:]  # Last 7 days
        return {
            'avg_on_time_delivery': np.mean([m['on_time_delivery'] for m in recent]),
            'avg_makespan': np.mean([m['makespan'] for m in recent]),
            'avg_wip_time': np.mean([m['average_wip_time'] for m in recent]),
        }
```

---

## Phase 4: Full Deployment and Optimization

### Step 4.1: Production Integration

**MES Integration**:

```python
# API to integrate with Manufacturing Execution System
from flask import Flask, jsonify, request

app = Flask(__name__)
scheduler = ProductionScheduler()

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Return current production schedule"""
    return jsonify({
        'schedule': scheduler.get_current_schedule(),
        'last_updated': datetime.now().isoformat(),
        'optimization_method': 'Mixed Integer Programming'
    })

@app.route('/api/order', methods=['POST'])
def add_order():
    """Accept new order and reoptimize"""
    order = request.json
    scheduler.add_order(order)
    return jsonify({
        'status': 'scheduled',
        'order_id': order['id'],
        'start_time': scheduler.scheduled_jobs[order['id']]['start_time']
    })

@app.route('/api/equipment/failure', methods=['POST'])
def equipment_failure():
    """Report equipment failure"""
    failure = request.json
    scheduler.handle_equipment_failure(
        failure['equipment_id'],
        failure['estimated_downtime']
    )
    return jsonify({'status': 'rescheduling_complete'})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Return current performance metrics"""
    analytics = SchedulingAnalytics()
    return jsonify(analytics.get_performance_summary())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Step 4.2: Continuous Improvement

**Optimization Refinement**:

1. **Monthly Reviews**: Analyze actual vs. planned performance
2. **Quarterly Updates**: Recalibrate models with new data
3. **Annual Strategic Review**: Assess algorithm effectiveness, consider algorithm updates

