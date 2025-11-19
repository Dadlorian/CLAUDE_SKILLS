#!/usr/bin/env python3
"""
Stage-Gate Innovation Portfolio Tracker
Production-ready innovation project management system
"""

import pandas as pd
from datetime import datetime, timedelta
from enum import Enum
import json

class Stage(Enum):
    """Innovation project stages"""
    DISCOVERY = "Discovery"
    SCOPING = "Scoping"
    BUSINESS_CASE = "Business Case"
    DEVELOPMENT = "Development"
    TESTING = "Testing & Validation"
    LAUNCH = "Launch"
    POST_LAUNCH = "Post-Launch Review"

class GateDecision(Enum):
    """Gate review decisions"""
    GO = "Go"
    KILL = "Kill"
    HOLD = "Hold"
    RECYCLE = "Recycle"
    PENDING = "Pending Review"

class InnovationProject:
    """Represents a single innovation project"""

    def __init__(self, project_id, name, description, innovation_type="Incremental"):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.innovation_type = innovation_type  # Incremental, Radical, Disruptive
        self.current_stage = Stage.DISCOVERY
        self.gate_decisions = []
        self.metrics = {
            'budget_allocated': 0,
            'budget_spent': 0,
            'team_size': 0,
            'expected_npv': 0,
            'risk_level': 'Medium'  # Low, Medium, High
        }
        self.start_date = datetime.now()
        self.milestones = []
        self.status = "Active"

    def add_gate_decision(self, decision, notes="", reviewer=""):
        """Record a gate decision"""
        self.gate_decisions.append({
            'date': datetime.now().isoformat(),
            'stage': self.current_stage.value,
            'decision': decision.value,
            'notes': notes,
            'reviewer': reviewer
        })

        if decision == GateDecision.GO:
            self._advance_stage()
        elif decision == GateDecision.KILL:
            self.status = "Killed"
        elif decision == GateDecision.HOLD:
            self.status = "On Hold"

    def _advance_stage(self):
        """Move project to next stage"""
        stages_list = list(Stage)
        current_index = stages_list.index(self.current_stage)
        if current_index < len(stages_list) - 1:
            self.current_stage = stages_list[current_index + 1]

    def update_metrics(self, **kwargs):
        """Update project metrics"""
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value

    def add_milestone(self, name, target_date, completed=False):
        """Add a project milestone"""
        self.milestones.append({
            'name': name,
            'target_date': target_date.isoformat() if isinstance(target_date, datetime) else target_date,
            'completed': completed,
            'completion_date': None
        })

    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'innovation_type': self.innovation_type,
            'current_stage': self.current_stage.value,
            'status': self.status,
            'start_date': self.start_date.isoformat(),
            'metrics': self.metrics,
            'gate_decisions': self.gate_decisions,
            'milestones': self.milestones
        }

class InnovationPortfolio:
    """Manage innovation project portfolio"""

    def __init__(self, organization_name=""):
        self.organization_name = organization_name
        self.projects = {}
        self.target_allocation = {
            'Incremental': 0.70,
            'Adjacent': 0.20,
            'Radical': 0.10
        }

    def add_project(self, project):
        """Add project to portfolio"""
        self.projects[project.project_id] = project

    def get_portfolio_metrics(self):
        """Calculate overall portfolio metrics"""
        active_projects = [p for p in self.projects.values() if p.status == "Active"]

        total_budget = sum(p.metrics['budget_allocated'] for p in active_projects)
        total_npv = sum(p.metrics['expected_npv'] for p in active_projects)

        # Innovation type distribution
        type_distribution = {}
        for p in active_projects:
            type_distribution[p.innovation_type] = type_distribution.get(p.innovation_type, 0) + 1

        # Stage distribution
        stage_distribution = {}
        for p in active_projects:
            stage_distribution[p.current_stage.value] = stage_distribution.get(p.current_stage.value, 0) + 1

        return {
            'total_active_projects': len(active_projects),
            'total_budget_allocated': total_budget,
            'expected_total_npv': total_npv,
            'portfolio_rodi': total_npv / total_budget if total_budget > 0 else 0,
            'innovation_type_distribution': type_distribution,
            'stage_distribution': stage_distribution
        }

    def check_portfolio_balance(self):
        """Check if portfolio aligns with 70-20-10 rule"""
        active_projects = [p for p in self.projects.values() if p.status == "Active"]
        if not active_projects:
            return "No active projects"

        type_counts = {}
        for p in active_projects:
            type_counts[p.innovation_type] = type_counts.get(p.innovation_type, 0) + 1

        total = len(active_projects)
        actual_allocation = {k: v/total for k, v in type_counts.items()}

        recommendations = []
        for innovation_type, target_pct in self.target_allocation.items():
            actual_pct = actual_allocation.get(innovation_type, 0)
            delta = actual_pct - target_pct

            if abs(delta) > 0.10:  # More than 10% deviation
                if delta < 0:
                    recommendations.append(f"Underweight in {innovation_type}: {actual_pct:.1%} vs target {target_pct:.1%}")
                else:
                    recommendations.append(f"Overweight in {innovation_type}: {actual_pct:.1%} vs target {target_pct:.1%}")

        return {
            'actual_allocation': actual_allocation,
            'target_allocation': self.target_allocation,
            'balanced': len(recommendations) == 0,
            'recommendations': recommendations
        }

    def generate_dashboard_data(self):
        """Generate data for portfolio dashboard"""
        return {
            'portfolio_metrics': self.get_portfolio_metrics(),
            'balance_check': self.check_portfolio_balance(),
            'projects_by_stage': self._projects_by_stage(),
            'at_risk_projects': self._identify_at_risk_projects()
        }

    def _projects_by_stage(self):
        """Group projects by stage"""
        projects_by_stage = {}
        for project in self.projects.values():
            if project.status == "Active":
                stage = project.current_stage.value
                if stage not in projects_by_stage:
                    projects_by_stage[stage] = []
                projects_by_stage[stage].append(project.project_id)
        return projects_by_stage

    def _identify_at_risk_projects(self):
        """Identify projects at risk"""
        at_risk = []
        for project in self.projects.values():
            if project.status == "Active":
                # Check if high risk
                if project.metrics['risk_level'] == 'High':
                    at_risk.append({
                        'project_id': project.project_id,
                        'name': project.name,
                        'reason': 'High risk level'
                    })

                # Check if over budget
                if project.metrics['budget_spent'] > project.metrics['budget_allocated'] * 0.9:
                    at_risk.append({
                        'project_id': project.project_id,
                        'name': project.name,
                        'reason': 'Budget nearly exhausted'
                    })

        return at_risk

    def export_to_json(self, filename):
        """Export portfolio to JSON"""
        data = {
            'organization': self.organization_name,
            'export_date': datetime.now().isoformat(),
            'projects': [p.to_dict() for p in self.projects.values()],
            'metrics': self.get_portfolio_metrics()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

# Example usage and demonstration
if __name__ == "__main__":
    # Create portfolio
    portfolio = InnovationPortfolio("TechCorp Innovation Labs")

    # Add sample projects
    p1 = InnovationProject("PROJ-001", "AI-Powered Analytics",
                          "Machine learning platform for data analysis",
                          innovation_type="Adjacent")
    p1.update_metrics(budget_allocated=500000, budget_spent=150000,
                     team_size=8, expected_npv=2000000)
    p1.add_milestone("Prototype Complete", datetime.now() + timedelta(days=90))
    p1.add_gate_decision(GateDecision.GO, "Strong preliminary results", "Innovation Committee")
    portfolio.add_project(p1)

    p2 = InnovationProject("PROJ-002", "Mobile App Enhancement",
                          "Add new features to existing mobile app",
                          innovation_type="Incremental")
    p2.update_metrics(budget_allocated=100000, budget_spent=50000,
                     team_size=4, expected_npv=300000)
    portfolio.add_project(p2)

    p3 = InnovationProject("PROJ-003", "Quantum Computing Research",
                          "Exploratory research in quantum algorithms",
                          innovation_type="Radical")
    p3.update_metrics(budget_allocated=1000000, budget_spent=200000,
                     team_size=5, expected_npv=10000000, risk_level='High')
    portfolio.add_project(p3)

    # Generate dashboard
    print("="*80)
    print("INNOVATION PORTFOLIO DASHBOARD")
    print("="*80)
    dashboard = portfolio.generate_dashboard_data()

    print("\nPortfolio Metrics:")
    print(f"  Active Projects: {dashboard['portfolio_metrics']['total_active_projects']}")
    print(f"  Total Budget: ${dashboard['portfolio_metrics']['total_budget_allocated']:,.0f}")
    print(f"  Expected NPV: ${dashboard['portfolio_metrics']['expected_total_npv']:,.0f}")
    print(f"  Portfolio RODI: {dashboard['portfolio_metrics']['portfolio_rodi']:.2f}x")

    print("\nPortfolio Balance:")
    balance = dashboard['balance_check']
    print(f"  Balanced: {balance['balanced']}")
    if balance['recommendations']:
        print("  Recommendations:")
        for rec in balance['recommendations']:
            print(f"    - {rec}")

    print("\nProjects by Stage:")
    for stage, projects in dashboard['projects_by_stage'].items():
        print(f"  {stage}: {len(projects)} projects")

    if dashboard['at_risk_projects']:
        print("\nAt-Risk Projects:")
        for project in dashboard['at_risk_projects']:
            print(f"  - {project['name']}: {project['reason']}")

    # Export to JSON
    portfolio.export_to_json("innovation_portfolio.json")
    print("\n✓ Portfolio exported to innovation_portfolio.json")
