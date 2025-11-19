"""
Process Optimization Algorithms for Manufacturing

This module provides optimization algorithms for production scheduling,
parameter tuning, and resource allocation in manufacturing environments.

Algorithms:
- Simulated Annealing
- Genetic Algorithm
- Greedy Heuristics
- Bayesian Optimization for parameter tuning
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import math


@dataclass
class Job:
    """Represents a production job"""
    job_id: str
    product_id: str
    quantity: int
    processing_time: float  # hours
    due_date: datetime
    priority: int = 1
    equipment_required: List[str] = None


@dataclass
class Equipment:
    """Represents production equipment"""
    equipment_id: str
    name: str
    available_from: float = 0.0
    processing_rate: float = 1.0  # units per hour
    setup_time: float = 0.0
    cost_per_hour: float = 50.0


@dataclass
class Schedule:
    """Represents a production schedule"""
    job_assignments: Dict[str, str]  # job_id -> equipment_id
    start_times: Dict[str, float]     # job_id -> start_time
    makespan: float = 0.0
    total_tardiness: float = 0.0
    total_cost: float = 0.0
    total_setup_time: float = 0.0
    on_time_delivery_rate: float = 0.0


class SimulatedAnnealing:
    """
    Simulated Annealing optimization for job shop scheduling
    """

    def __init__(self, initial_temperature: float = 100.0, cooling_rate: float = 0.95):
        self.temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.best_solution = None
        self.best_cost = float('inf')
        self.iteration_history = []

    def optimize(
        self,
        jobs: List[Job],
        equipment: List[Equipment],
        objective_func: Callable,
        max_iterations: int = 1000,
        setup_times: Optional[Dict[Tuple[str, str], float]] = None
    ) -> Schedule:
        """
        Optimize job schedule using Simulated Annealing

        Args:
            jobs: List of Job objects
            equipment: List of Equipment objects
            objective_func: Function to minimize
            max_iterations: Maximum iterations
            setup_times: Dict mapping (from_job, to_job) -> setup_time_hours

        Returns:
            Optimized Schedule
        """
        self.temperature = 100.0

        # Create initial solution
        current_solution = self._create_initial_solution(jobs, equipment)
        current_cost = objective_func(current_solution)
        self.best_solution = current_solution
        self.best_cost = current_cost

        for iteration in range(max_iterations):
            # Generate neighbor solution
            neighbor_solution = self._generate_neighbor(current_solution, jobs, equipment)
            neighbor_cost = objective_func(neighbor_solution)

            # Acceptance probability
            if neighbor_cost < current_cost:
                # Accept better solution
                current_solution = neighbor_solution
                current_cost = neighbor_cost

                if neighbor_cost < self.best_cost:
                    self.best_solution = neighbor_solution
                    self.best_cost = neighbor_cost
            else:
                # Accept worse solution with probability
                delta = neighbor_cost - current_cost
                acceptance_prob = math.exp(-delta / self.temperature)
                if random.random() < acceptance_prob:
                    current_solution = neighbor_solution
                    current_cost = neighbor_cost

            # Cool down
            self.temperature *= self.cooling_rate

            self.iteration_history.append({
                'iteration': iteration,
                'current_cost': current_cost,
                'best_cost': self.best_cost,
                'temperature': self.temperature
            })

            # Early stopping
            if self.temperature < 0.01:
                break

        return self.best_solution

    @staticmethod
    def _create_initial_solution(jobs: List[Job], equipment: List[Equipment]) -> Schedule:
        """Create initial schedule using greedy approach"""
        schedule = Schedule(
            job_assignments={},
            start_times={},
        )

        equipment_available_at = {e.equipment_id: e.available_from for e in equipment}

        for job in sorted(jobs, key=lambda j: j.due_date):
            # Find equipment that becomes available earliest
            best_equipment = min(equipment, key=lambda e: equipment_available_at[e.equipment_id])

            schedule.job_assignments[job.job_id] = best_equipment.equipment_id
            schedule.start_times[job.job_id] = equipment_available_at[best_equipment.equipment_id]

            # Update equipment availability
            processing_hours = job.quantity / best_equipment.processing_rate
            equipment_available_at[best_equipment.equipment_id] += processing_hours

        return schedule

    @staticmethod
    def _generate_neighbor(
        solution: Schedule,
        jobs: List[Job],
        equipment: List[Equipment]
    ) -> Schedule:
        """Generate neighboring solution by swapping job assignments"""
        new_solution = Schedule(
            job_assignments=solution.job_assignments.copy(),
            start_times=solution.start_times.copy(),
        )

        # Randomly select two jobs and swap their equipment
        if len(jobs) > 1:
            job1, job2 = random.sample(jobs, 2)

            # Swap equipment assignments
            temp = new_solution.job_assignments[job1.job_id]
            new_solution.job_assignments[job1.job_id] = new_solution.job_assignments[job2.job_id]
            new_solution.job_assignments[job2.job_id] = temp

        return new_solution


class GeneticAlgorithm:
    """
    Genetic Algorithm for job shop scheduling optimization
    """

    def __init__(self, population_size: int = 100, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.fitness_history = []

    def optimize(
        self,
        jobs: List[Job],
        equipment: List[Equipment],
        objective_func: Callable,
        generations: int = 100
    ) -> Schedule:
        """
        Optimize using Genetic Algorithm

        Args:
            jobs: List of Job objects
            equipment: List of Equipment objects
            objective_func: Function to minimize
            generations: Number of generations

        Returns:
            Best Schedule found
        """
        # Initialize population
        self.population = [
            self._create_random_schedule(jobs, equipment)
            for _ in range(self.population_size)
        ]

        best_individual = None
        best_fitness = float('inf')

        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = [objective_func(individual) for individual in self.population]

            # Track best
            gen_best_idx = np.argmin(fitness_scores)
            if fitness_scores[gen_best_idx] < best_fitness:
                best_fitness = fitness_scores[gen_best_idx]
                best_individual = self.population[gen_best_idx]

            self.fitness_history.append({
                'generation': generation,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(fitness_scores),
                'min_fitness': np.min(fitness_scores),
                'max_fitness': np.max(fitness_scores)
            })

            # Selection, Crossover, Mutation
            new_population = []

            # Elitism: keep best individuals
            elite_count = max(1, self.population_size // 10)
            elite_indices = np.argsort(fitness_scores)[:elite_count]
            new_population.extend([self.population[i] for i in elite_indices])

            # Generate rest of population
            while len(new_population) < self.population_size:
                # Tournament selection
                parent1 = self._tournament_selection(self.population, fitness_scores)
                parent2 = self._tournament_selection(self.population, fitness_scores)

                # Crossover
                child = self._crossover(parent1, parent2)

                # Mutation
                if random.random() < self.mutation_rate:
                    child = self._mutate(child, jobs)

                new_population.append(child)

            self.population = new_population

        return best_individual

    @staticmethod
    def _create_random_schedule(jobs: List[Job], equipment: List[Equipment]) -> Schedule:
        """Create random schedule"""
        schedule = Schedule(
            job_assignments={},
            start_times={},
        )

        equipment_available_at = {e.equipment_id: 0.0 for e in equipment}

        for job in jobs:
            # Randomly assign to equipment
            assigned_equipment = random.choice(equipment)
            schedule.job_assignments[job.job_id] = assigned_equipment.equipment_id
            schedule.start_times[job.job_id] = equipment_available_at[assigned_equipment.equipment_id]

            # Update equipment time
            processing_hours = job.quantity / assigned_equipment.processing_rate
            equipment_available_at[assigned_equipment.equipment_id] += processing_hours

        return schedule

    @staticmethod
    def _tournament_selection(population: List[Schedule], fitness_scores: List[float]) -> Schedule:
        """Select individual via tournament"""
        tournament_size = 5
        indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        best_idx = min(indices, key=lambda i: fitness_scores[i])
        return population[best_idx]

    @staticmethod
    def _crossover(parent1: Schedule, parent2: Schedule) -> Schedule:
        """Crossover operation"""
        child = Schedule(
            job_assignments=parent1.job_assignments.copy(),
            start_times=parent1.start_times.copy(),
        )

        # Copy half from parent1, half from parent2
        jobs = list(parent1.job_assignments.keys())
        crossover_point = len(jobs) // 2

        for job in jobs[crossover_point:]:
            child.job_assignments[job] = parent2.job_assignments[job]
            child.start_times[job] = parent2.start_times[job]

        return child

    @staticmethod
    def _mutate(schedule: Schedule, jobs: List[Job]) -> Schedule:
        """Mutation operation"""
        if len(jobs) < 2:
            return schedule

        job1, job2 = random.sample(jobs, 2)

        # Swap assignments
        temp = schedule.job_assignments[job1.job_id]
        schedule.job_assignments[job1.job_id] = schedule.job_assignments[job2.job_id]
        schedule.job_assignments[job2.job_id] = temp

        return schedule


class BayesianOptimization:
    """
    Bayesian Optimization for process parameter tuning
    """

    def __init__(self, bounds: Dict[str, Tuple[float, float]]):
        """
        Args:
            bounds: Dict mapping parameter names to (min, max) tuples
        """
        self.bounds = bounds
        self.observation_history = []

    def optimize(
        self,
        objective_func: Callable,
        n_iterations: int = 50,
        initial_points: int = 5
    ) -> Dict[str, float]:
        """
        Optimize parameters using Bayesian Optimization

        Args:
            objective_func: Function mapping parameters dict to score
            n_iterations: Total iterations
            initial_points: Initial random exploration points

        Returns:
            Best parameters found
        """
        from scipy.optimize import minimize
        from scipy.spatial.distance import cdist

        # Initial random exploration
        for _ in range(initial_points):
            params = {
                name: np.random.uniform(bounds[0], bounds[1])
                for name, bounds in self.bounds.items()
            }
            score = objective_func(params)
            self.observation_history.append({'params': params, 'score': score})

        # Iterative optimization
        for iteration in range(n_iterations - initial_points):
            # Fit GP surrogate model (simplified using RBF)
            X = np.array([list(obs['params'].values()) for obs in self.observation_history])
            y = np.array([obs['score'] for obs in self.observation_history])

            # Find next point to evaluate using Expected Improvement
            best_score = np.min(y)

            def ei_objective(x):
                # Simplified EI using distance-based uncertainty
                distances = cdist([x], X)[0]
                min_distance = np.min(distances) if len(distances) > 0 else 1e-6
                uncertainty = 1.0 / (1.0 + min_distance)

                predicted_value = np.interp(
                    min_distance, np.linspace(0, np.max(distances), len(y)), y
                )
                improvement = max(0, best_score - predicted_value)

                return -(improvement * uncertainty)  # Negative because we minimize

            # Optimize EI to find next point
            x0 = np.array([np.random.uniform(b[0], b[1]) for b in self.bounds.values()])
            bounds_list = list(self.bounds.values())

            result = minimize(ei_objective, x0, bounds=bounds_list, method='L-BFGS-B')

            # Evaluate next point
            param_names = list(self.bounds.keys())
            next_params = {name: result.x[i] for i, name in enumerate(param_names)}
            score = objective_func(next_params)

            self.observation_history.append({'params': next_params, 'score': score})

        # Return best parameters
        best_idx = np.argmin([obs['score'] for obs in self.observation_history])
        return self.observation_history[best_idx]['params']

    def get_optimization_history(self) -> pd.DataFrame:
        """Get optimization history"""
        data = []
        for obs in self.observation_history:
            row = obs['params'].copy()
            row['score'] = obs['score']
            data.append(row)

        return pd.DataFrame(data)


def calculate_schedule_makespan(schedule: Schedule, jobs: List[Job], equipment: List[Equipment]) -> float:
    """Calculate makespan (total time to complete all jobs)"""
    job_completion_times = {}

    for job in jobs:
        equipment_id = schedule.job_assignments[job.job_id]
        start_time = schedule.start_times[job.job_id]

        # Find equipment
        equip = next(e for e in equipment if e.equipment_id == equipment_id)

        processing_time = job.quantity / equip.processing_rate
        completion_time = start_time + processing_time

        job_completion_times[job.job_id] = completion_time

    return max(job_completion_times.values()) if job_completion_times else 0


def calculate_schedule_tardiness(schedule: Schedule, jobs: List[Job], equipment: List[Equipment]) -> float:
    """Calculate total tardiness (days late)"""
    total_tardiness = 0

    job_dict = {job.job_id: job for job in jobs}
    equip_dict = {e.equipment_id: e for e in equipment}

    for job_id, equipment_id in schedule.job_assignments.items():
        job = job_dict[job_id]
        equip = equip_dict[equipment_id]
        start_time = schedule.start_times[job_id]

        processing_hours = job.quantity / equip.processing_rate
        completion_time = start_time + processing_hours
        completion_datetime = datetime.now() + timedelta(hours=completion_time)

        if completion_datetime > job.due_date:
            tardiness = (completion_datetime - job.due_date).total_seconds() / 3600
            total_tardiness += tardiness

    return total_tardiness


def create_multi_objective_function(
    weights: Dict[str, float],
    jobs: List[Job],
    equipment: List[Equipment]
) -> Callable:
    """
    Create weighted multi-objective optimization function

    Args:
        weights: Dict with keys 'makespan', 'tardiness', 'cost'
        jobs: List of jobs
        equipment: List of equipment

    Returns:
        Objective function
    """
    def objective(schedule: Schedule) -> float:
        makespan = calculate_schedule_makespan(schedule, jobs, equipment)
        tardiness = calculate_schedule_tardiness(schedule, jobs, equipment)

        # Normalize
        makespan_norm = makespan / 1000  # Assume max 1000 hours
        tardiness_norm = tardiness / 100  # Assume max 100 hours late

        weighted_score = (
            weights.get('makespan', 0.3) * makespan_norm +
            weights.get('tardiness', 0.5) * tardiness_norm +
            weights.get('cost', 0.2) * 1.0  # Simplified cost
        )

        return weighted_score

    return objective


# Example usage
if __name__ == "__main__":
    # Create sample jobs and equipment
    jobs = [
        Job('J1', 'A123', 100, 2.0, datetime.now() + timedelta(hours=12)),
        Job('J2', 'B456', 150, 3.0, datetime.now() + timedelta(hours=18)),
        Job('J3', 'A123', 120, 2.5, datetime.now() + timedelta(hours=15)),
        Job('J4', 'C789', 200, 4.0, datetime.now() + timedelta(hours=24)),
    ]

    equipment = [
        Equipment('E1', 'Mill 1', 0.0, 50.0, 0.5, 75.0),
        Equipment('E2', 'Mill 2', 0.0, 45.0, 0.5, 70.0),
    ]

    # Create objective function
    objective = create_multi_objective_function(
        {'makespan': 0.3, 'tardiness': 0.5, 'cost': 0.2},
        jobs,
        equipment
    )

    print("Optimization Examples:")
    print("=" * 50)

    # 1. Simulated Annealing
    print("\n1. Simulated Annealing:")
    sa = SimulatedAnnealing()
    sa_solution = sa.optimize(jobs, equipment, objective, max_iterations=100)
    print(f"   Best cost: {sa.best_cost:.4f}")
    print(f"   Makespan: {calculate_schedule_makespan(sa_solution, jobs, equipment):.1f} hours")

    # 2. Genetic Algorithm
    print("\n2. Genetic Algorithm:")
    ga = GeneticAlgorithm(population_size=50)
    ga_solution = ga.optimize(jobs, equipment, objective, generations=50)
    ga_best_cost = objective(ga_solution)
    print(f"   Best cost: {ga_best_cost:.4f}")
    print(f"   Makespan: {calculate_schedule_makespan(ga_solution, jobs, equipment):.1f} hours")

    print("\n3. Bayesian Optimization (Parameter Tuning):")
    param_bounds = {
        'temperature': (50.0, 200.0),
        'speed': (0.5, 1.0),
        'pressure': (1.0, 5.0)
    }

    def param_objective(params):
        # Simulated objective: minimize (temp-100)^2 + (speed-0.8)^2 + (pressure-3)^2
        score = (
            (params['temperature'] - 100) ** 2 / 10000 +
            (params['speed'] - 0.8) ** 2 +
            (params['pressure'] - 3) ** 2
        )
        return score

    bo = BayesianOptimization(param_bounds)
    best_params = bo.optimize(param_objective, n_iterations=20, initial_points=5)
    print(f"   Best parameters: {best_params}")
    print(f"   Best score: {param_objective(best_params):.4f}")
