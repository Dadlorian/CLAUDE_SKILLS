"""Goal Tracker - Monitors progress toward financial goals"""
from datetime import datetime
from typing import Dict, List


class GoalTracker:
    """Tracks goals and monitors achievement probability"""

    def __init__(self):
        self.goals = []

    def add_goal(self, name: str, target_amount: float, years: int,
                 current_value: float = 0):
        """Add new financial goal"""
        self.goals.append({
            'name': name,
            'target': target_amount,
            'years': years,
            'current': current_value,
            'created_date': datetime.now()
        })

    def calculate_required_contribution(self, goal_name: str,
                                       annual_return: float = 0.07) -> float:
        """Calculate monthly contribution needed for goal"""
        goal = next((g for g in self.goals if g['name'] == goal_name), None)
        if not goal:
            return 0

        remaining = goal['target'] - goal['current']
        months = goal['years'] * 12
        monthly_rate = annual_return / 12

        if monthly_rate == 0:
            return remaining / months

        monthly = remaining / (((1 + monthly_rate) ** months - 1) / monthly_rate)
        return max(0, monthly)

    def calculate_probability_success(self, goal_name: str,
                                     projected_return: float = 0.07) -> float:
        """Estimate probability of achieving goal"""
        goal = next((g for g in self.goals if g['name'] == goal_name), None)
        if not goal:
            return 0

        years = goal['years']
        current = goal['current']
        target = goal['target']

        # Simple future value calculation
        projected_value = current * (1 + projected_return) ** years

        # Probability based on buffer
        if projected_value >= target:
            buffer_pct = (projected_value - target) / target
            return min(0.99, 0.5 + (buffer_pct * 0.25))
        else:
            shortfall_pct = (target - projected_value) / target
            return max(0.01, 0.5 - (shortfall_pct * 0.25))
