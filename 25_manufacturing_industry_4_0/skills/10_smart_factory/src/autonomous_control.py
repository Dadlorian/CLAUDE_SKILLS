"""
Autonomous Manufacturing Control System

This module provides a framework for autonomous control systems in Smart Factory
operations. It enables intelligent, self-optimizing production systems that make
decisions based on real-time data, machine learning models, and business rules.

Key Features:
- Intelligent decision-making engine
- Real-time constraint optimization
- Predictive control strategies
- Adaptive learning and self-tuning
- Risk assessment and mitigation
- Seamless human-machine interaction
- Audit trail for all autonomous decisions

Author: Smart Factory Expert
Version: 1.0
"""

import json
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import numpy as np


class AutonomyLevel(Enum):
    """Autonomy levels for manufacturing control"""
    MANUAL = 1                    # Operator makes all decisions
    ASSISTED = 2                  # System provides suggestions
    CONDITIONAL = 3               # System decides in defined conditions
    HIGH = 4                       # System handles most scenarios
    FULL = 5                       # Autonomous operation


class DecisionStatus(Enum):
    """Status of autonomous decisions"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"
    FAILED = "failed"


@dataclass
class ControlConstraint:
    """System constraint for optimization"""
    constraint_id: str
    name: str
    parameter: str  # Which parameter does this constrain
    min_value: float
    max_value: float
    priority: int = 1  # 1=critical, 5=nice-to-have
    description: str = ""

    def validate(self, value: float) -> tuple[bool, str]:
        """
        Validate value against constraint

        Args:
            value: Value to validate

        Returns:
            (is_valid, message)
        """
        if value < self.min_value:
            return False, f"Value {value} below minimum {self.min_value}"
        if value > self.max_value:
            return False, f"Value {value} above maximum {self.max_value}"
        return True, "Valid"


@dataclass
class ControlObjective:
    """Optimization objective for autonomous control"""
    objective_id: str
    name: str
    type: str  # maximize, minimize, maintain
    parameter: str  # Which metric to optimize
    target_value: float
    tolerance: float
    weight: float = 1.0  # Relative importance vs other objectives
    time_window_seconds: int = 300

    def evaluate(self, current_value: float) -> float:
        """
        Evaluate objective achievement

        Args:
            current_value: Current value of the parameter

        Returns:
            Score 0-1 (1.0 = perfect achievement)
        """
        if self.type == "maintain":
            deviation = abs(current_value - self.target_value)
            if deviation <= self.tolerance:
                return 1.0
            return max(0, 1.0 - (deviation / self.target_value))

        elif self.type == "maximize":
            if current_value >= self.target_value:
                return 1.0
            return current_value / self.target_value if self.target_value > 0 else 0

        elif self.type == "minimize":
            if current_value <= self.target_value:
                return 1.0
            return self.target_value / current_value if current_value > 0 else 0

        return 0.5


@dataclass
class ControlAction:
    """
    Proposed autonomous control action

    Represents a decision made by the autonomous system
    """
    action_id: str
    timestamp: int
    autonomy_level: AutonomyLevel
    action_type: str  # parameter_adjustment, process_change, maintenance_trigger
    equipment_id: str
    parameter: str
    proposed_value: float
    current_value: float
    reason: str
    confidence_score: float  # 0-1
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    approval_required: bool = False
    approved_by: str = ""
    status: DecisionStatus = DecisionStatus.PENDING
    execution_timestamp: int = 0
    actual_result: Optional[Dict] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["autonomy_level"] = self.autonomy_level.value
        data["status"] = self.status.value
        return data


@dataclass
class ProductionPlan:
    """Production plan for autonomous execution"""
    plan_id: str
    work_order_id: str
    target_throughput: int  # units per hour
    quality_target: float  # target first-pass yield 0-1
    energy_limit: float  # kWh maximum for job
    maintenance_window: Optional[tuple] = None  # (start_time, duration_minutes)
    changeover_allowed: bool = True
    estimated_completion_time: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


class AutonomousControlEngine:
    """
    Core autonomous control decision-making engine

    Manages:
    - Real-time monitoring of production state
    - Constraint satisfaction
    - Multi-objective optimization
    - Decision proposal and approval
    - Risk assessment
    """

    def __init__(self, autonomy_level: AutonomyLevel = AutonomyLevel.CONDITIONAL):
        """
        Initialize Autonomous Control Engine

        Args:
            autonomy_level: Initial autonomy level for the system
        """
        self.autonomy_level = autonomy_level
        self.constraints: Dict[str, ControlConstraint] = {}
        self.objectives: Dict[str, ControlObjective] = {}
        self.current_state: Dict[str, Any] = {}
        self.decision_history: List[ControlAction] = []
        self.approval_callbacks: List[Callable] = []
        self.execution_callbacks: List[Callable] = []

    def add_constraint(self, constraint: ControlConstraint):
        """Add a constraint to the control system"""
        self.constraints[constraint.constraint_id] = constraint

    def add_objective(self, objective: ControlObjective):
        """Add an optimization objective"""
        self.objectives[objective.objective_id] = objective

    def register_approval_callback(self, callback: Callable):
        """Register callback for manual approval of actions"""
        self.approval_callbacks.append(callback)

    def register_execution_callback(self, callback: Callable):
        """Register callback for action execution"""
        self.execution_callbacks.append(callback)

    def update_state(self, state: Dict[str, Any]):
        """Update current production state"""
        self.current_state = state

    def propose_action(self, equipment_id: str, parameter: str,
                      proposed_value: float, reason: str,
                      confidence: float) -> Optional[ControlAction]:
        """
        Propose an autonomous control action

        Args:
            equipment_id: Target equipment
            parameter: Parameter to adjust
            proposed_value: Proposed new value
            reason: Explanation for the action
            confidence: Confidence score 0-1

        Returns:
            ControlAction or None if rejected
        """
        action = ControlAction(
            action_id=f"ACTION_{int(time.time() * 1000)}",
            timestamp=int(time.time() * 1000),
            autonomy_level=self.autonomy_level,
            equipment_id=equipment_id,
            parameter=parameter,
            proposed_value=proposed_value,
            current_value=self.current_state.get(parameter, 0),
            reason=reason,
            confidence_score=confidence
        )

        # Validate constraints
        constraint_violations = self._validate_constraints(parameter, proposed_value)
        if constraint_violations:
            action.status = DecisionStatus.REJECTED
            action.risk_assessment["constraint_violations"] = constraint_violations
            return action

        # Assess risks
        action.risk_assessment = self._assess_risks(action)

        # Determine if approval is needed
        action.approval_required = (
            confidence < 0.7 or
            action.risk_assessment.get("risk_level") == "high" or
            self.autonomy_level in [AutonomyLevel.ASSISTED, AutonomyLevel.MANUAL]
        )

        if action.approval_required:
            self._request_approval(action)
        else:
            action.status = DecisionStatus.APPROVED
            action = self.execute_action(action)

        self.decision_history.append(action)
        return action

    def _validate_constraints(self, parameter: str, value: float) -> List[str]:
        """
        Validate value against all constraints

        Returns:
            List of constraint violations
        """
        violations = []

        for constraint in self.constraints.values():
            if constraint.parameter == parameter:
                is_valid, message = constraint.validate(value)
                if not is_valid:
                    violations.append(f"{constraint.name}: {message}")

        return violations

    def _assess_risks(self, action: ControlAction) -> Dict[str, Any]:
        """
        Assess risks of proposed action

        Returns:
            Risk assessment results
        """
        risks = {
            "risk_level": "low",
            "identified_risks": [],
            "mitigation_strategies": []
        }

        # Check for large parameter changes
        change_percentage = abs(
            (action.proposed_value - action.current_value) / action.current_value * 100
        ) if action.current_value != 0 else 0

        if change_percentage > 20:
            risks["identified_risks"].append(
                f"Large parameter change: {change_percentage:.1f}%"
            )
            risks["mitigation_strategies"].append(
                "Apply change incrementally in smaller steps"
            )

        # Check confidence
        if action.confidence_score < 0.6:
            risks["identified_risks"].append(
                f"Low confidence: {action.confidence_score:.1%}"
            )
            risks["risk_level"] = "high"

        # Determine overall risk level
        if risks["identified_risks"]:
            risks["risk_level"] = "medium" if change_percentage <= 50 else "high"

        return risks

    def _request_approval(self, action: ControlAction):
        """Request manual approval for action"""
        for callback in self.approval_callbacks:
            try:
                result = callback(action)
                if result:
                    action.status = DecisionStatus.APPROVED
                    action.approved_by = result.get("approved_by", "system")
                else:
                    action.status = DecisionStatus.REJECTED
            except Exception as e:
                print(f"Error in approval callback: {e}")

    def execute_action(self, action: ControlAction) -> ControlAction:
        """
        Execute an approved control action

        Args:
            action: Action to execute

        Returns:
            Updated action with execution results
        """
        if action.status != DecisionStatus.APPROVED:
            return action

        try:
            # Call execution callbacks
            results = []
            for callback in self.execution_callbacks:
                try:
                    result = callback(
                        action.equipment_id,
                        action.parameter,
                        action.proposed_value
                    )
                    results.append(result)
                except Exception as e:
                    print(f"Error executing action: {e}")
                    action.status = DecisionStatus.FAILED
                    return action

            action.status = DecisionStatus.EXECUTED
            action.execution_timestamp = int(time.time() * 1000)
            action.actual_result = {
                "execution_results": results,
                "execution_time_ms": action.execution_timestamp - action.timestamp
            }

        except Exception as e:
            action.status = DecisionStatus.FAILED
            action.actual_result = {"error": str(e)}

        return action

    def override_action(self, action_id: str, override_value: Optional[float] = None):
        """
        Override an autonomous action

        Args:
            action_id: ID of action to override
            override_value: Optional new value to apply instead
        """
        for action in self.decision_history:
            if action.action_id == action_id:
                action.status = DecisionStatus.OVERRIDDEN
                if override_value is not None:
                    # Execute override
                    for callback in self.execution_callbacks:
                        callback(
                            action.equipment_id,
                            action.parameter,
                            override_value
                        )
                break

    def get_action_history(self, equipment_id: Optional[str] = None) -> List[Dict]:
        """Get history of all autonomous actions"""
        actions = self.decision_history

        if equipment_id:
            actions = [a for a in actions if a.equipment_id == equipment_id]

        return [a.to_dict() for a in actions]

    def recommend_parameter_adjustment(self, equipment_id: str) -> Optional[ControlAction]:
        """
        Recommend optimal parameter adjustment based on objectives

        Args:
            equipment_id: Target equipment

        Returns:
            Recommended control action
        """
        if not self.objectives:
            return None

        # Evaluate current objective achievement
        scores = {}
        for obj_id, objective in self.objectives.items():
            current = self.current_state.get(objective.parameter, objective.target_value)
            score = objective.evaluate(current)
            scores[obj_id] = score * objective.weight

        # Find lowest-scoring objective
        worst_objective_id = min(scores, key=scores.get)
        worst_objective = self.objectives[worst_objective_id]

        # Calculate recommended adjustment
        current_value = self.current_state.get(worst_objective.parameter, 0)
        recommended_value = current_value

        if worst_objective.type == "maintain":
            if current_value < worst_objective.target_value - worst_objective.tolerance:
                recommended_value = current_value + (worst_objective.tolerance * 0.5)
            elif current_value > worst_objective.target_value + worst_objective.tolerance:
                recommended_value = current_value - (worst_objective.tolerance * 0.5)

        elif worst_objective.type == "maximize":
            recommended_value = current_value * 1.1  # 10% increase

        elif worst_objective.type == "minimize":
            recommended_value = current_value * 0.9  # 10% decrease

        return self.propose_action(
            equipment_id=equipment_id,
            parameter=worst_objective.parameter,
            proposed_value=recommended_value,
            reason=f"Optimize {worst_objective.name}",
            confidence=0.7
        )


class ProductionScheduler:
    """
    Autonomous production scheduler

    Automatically schedules production to meet objectives while respecting constraints
    """

    def __init__(self):
        """Initialize Production Scheduler"""
        self.plans: Dict[str, ProductionPlan] = {}
        self.current_schedule: List[ProductionPlan] = []

    def create_plan(self, plan: ProductionPlan) -> str:
        """Create a production plan"""
        self.plans[plan.plan_id] = plan
        return plan.plan_id

    def optimize_schedule(self) -> List[ProductionPlan]:
        """
        Optimize production schedule

        Considers:
        - Throughput targets
        - Quality targets
        - Energy limits
        - Maintenance windows
        - Changeover time

        Returns:
            Optimized production schedule
        """
        plans = list(self.plans.values())

        # Sort by priority: maintenance windows first, then deadlines
        prioritized = sorted(
            plans,
            key=lambda p: (
                p.maintenance_window is None,
                p.estimated_completion_time
            )
        )

        self.current_schedule = prioritized
        return prioritized

    def get_schedule(self) -> List[Dict]:
        """Get current production schedule"""
        return [p.to_dict() for p in self.current_schedule]

    def adjust_schedule(self, constraint_update: Dict[str, Any]):
        """
        Adjust schedule based on new constraints

        Args:
            constraint_update: Updated constraint values
        """
        # In a real system, this would reoptimize based on new constraints
        self.optimize_schedule()


class QualityController:
    """
    Autonomous quality control system

    Monitors quality in real-time and makes adjustments to maintain specification
    """

    def __init__(self, target_yield: float = 0.98):
        """
        Initialize Quality Controller

        Args:
            target_yield: Target first-pass yield (0-1)
        """
        self.target_yield = target_yield
        self.quality_history: List[Dict] = []
        self.adjustment_rules: List[Dict] = []

    def add_quality_rule(self, rule: Dict):
        """
        Add a quality control rule

        Rule format:
        {
            "parameter": "parameter_name",
            "defect_type": "defect_description",
            "adjustment_parameter": "param_to_adjust",
            "adjustment_amount": ±value
        }
        """
        self.adjustment_rules.append(rule)

    def analyze_quality(self, measurement: Dict) -> Optional[Dict]:
        """
        Analyze quality measurement and recommend adjustments

        Args:
            measurement: Quality measurement data

        Returns:
            Recommended adjustment or None
        """
        self.quality_history.append(measurement)

        # Calculate yield trend
        recent = self.quality_history[-10:]  # Last 10 measurements
        pass_count = sum(1 for m in recent if m.get("result") == "pass")
        recent_yield = pass_count / len(recent) if recent else 1.0

        # If yield is dropping, recommend adjustment
        if recent_yield < self.target_yield:
            # Find matching rule
            for rule in self.adjustment_rules:
                if rule.get("defect_type") == measurement.get("defect_type"):
                    return {
                        "action": "adjust_parameter",
                        "parameter": rule.get("adjustment_parameter"),
                        "adjustment": rule.get("adjustment_amount"),
                        "reason": f"Quality trend below target ({recent_yield:.1%})"
                    }

        return None


# Example usage and demonstration
if __name__ == "__main__":

    # Initialize autonomous control engine
    engine = AutonomousControlEngine(autonomy_level=AutonomyLevel.CONDITIONAL)

    # Add constraints
    constraints = [
        ControlConstraint(
            constraint_id="TEMP_LIMIT",
            name="Temperature Limit",
            parameter="temperature",
            min_value=0,
            max_value=100,
            priority=1
        ),
        ControlConstraint(
            constraint_id="PRESSURE_LIMIT",
            name="Pressure Limit",
            parameter="pressure",
            min_value=10,
            max_value=350,
            priority=1
        ),
        ControlConstraint(
            constraint_id="SPEED_LIMIT",
            name="Speed Limit",
            parameter="spindle_speed",
            min_value=100,
            max_value=3000,
            priority=2
        )
    ]

    for constraint in constraints:
        engine.add_constraint(constraint)

    # Add objectives
    objectives = [
        ControlObjective(
            objective_id="OBJ_QUALITY",
            name="Quality Target",
            type="maintain",
            parameter="temperature",
            target_value=65,
            tolerance=5,
            weight=2.0  # Higher priority
        ),
        ControlObjective(
            objective_id="OBJ_THROUGHPUT",
            name="Throughput Target",
            type="maximize",
            parameter="spindle_speed",
            target_value=2000,
            tolerance=100,
            weight=1.5
        ),
        ControlObjective(
            objective_id="OBJ_ENERGY",
            name="Energy Efficiency",
            type="minimize",
            parameter="power_consumption",
            target_value=50,
            tolerance=10,
            weight=1.0
        )
    ]

    for objective in objectives:
        engine.add_objective(objective)

    # Simulate state updates and decisions
    print("Autonomous Control System Demonstration")
    print("=" * 50)

    current_state = {
        "temperature": 62,
        "pressure": 250,
        "spindle_speed": 1800,
        "power_consumption": 55
    }
    engine.update_state(current_state)

    # Propose action: increase temperature for better quality
    action = engine.propose_action(
        equipment_id="MACHINE_001",
        parameter="temperature",
        proposed_value=68,
        reason="Improve surface finish quality based on recent defect analysis",
        confidence=0.85
    )

    print(f"\nProposed Action:")
    print(f"  Equipment: {action.equipment_id}")
    print(f"  Parameter: {action.parameter}")
    print(f"  Current Value: {action.current_value}")
    print(f"  Proposed Value: {action.proposed_value}")
    print(f"  Confidence: {action.confidence_score:.0%}")
    print(f"  Status: {action.status.value}")
    print(f"  Reason: {action.reason}")

    if action.risk_assessment:
        print(f"  Risk Level: {action.risk_assessment.get('risk_level')}")

    # Get recommendation
    print("\n" + "=" * 50)
    print("Parameter Adjustment Recommendation:")
    recommendation = engine.recommend_parameter_adjustment("MACHINE_001")
    if recommendation:
        print(f"  Recommended: {recommendation.parameter} → {recommendation.proposed_value}")
        print(f"  Reason: {recommendation.reason}")

    # Production scheduling
    print("\n" + "=" * 50)
    print("Production Scheduling:")
    scheduler = ProductionScheduler()

    plans = [
        ProductionPlan(
            plan_id="PLAN_001",
            work_order_id="WO_001",
            target_throughput=120,
            quality_target=0.98,
            energy_limit=500
        ),
        ProductionPlan(
            plan_id="PLAN_002",
            work_order_id="WO_002",
            target_throughput=100,
            quality_target=0.99,
            energy_limit=450
        )
    ]

    for plan in plans:
        scheduler.create_plan(plan)

    schedule = scheduler.optimize_schedule()
    for plan in schedule:
        print(f"  {plan.plan_id}: {plan.target_throughput} units/hr, "
              f"Energy: {plan.energy_limit} kWh")

    # Quality control
    print("\n" + "=" * 50)
    print("Quality Control:")
    qc = QualityController(target_yield=0.98)

    qc.add_quality_rule({
        "defect_type": "surface_roughness",
        "parameter": "feed_rate",
        "adjustment_parameter": "feed_rate",
        "adjustment_amount": -10
    })

    measurement = {
        "result": "fail",
        "defect_type": "surface_roughness",
        "value": 1.2
    }

    recommendation = qc.analyze_quality(measurement)
    if recommendation:
        print(f"  Quality Alert: {measurement['defect_type']}")
        print(f"  Recommendation: Adjust {recommendation['parameter']} "
              f"by {recommendation['adjustment']}")
