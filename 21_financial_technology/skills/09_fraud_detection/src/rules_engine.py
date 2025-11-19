"""
Rules Engine - Declarative fraud detection rules
"""

import json
from typing import Dict, List


class RulesEngine:
    """Fraud detection rules engine"""

    def __init__(self, rules_path: str = None):
        self.rules = []
        if rules_path:
            self.load_rules(rules_path)

    def load_rules(self, rules_path: str):
        """Load rules from JSON file"""
        with open(rules_path, 'r') as f:
            rules_data = json.load(f)

        for rule_dict in rules_data.get('rules', []):
            self.rules.append(Rule(rule_dict))

        # Sort by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def evaluate_transaction(self, features: Dict) -> Dict:
        """Evaluate all rules"""
        triggered_rules = []
        score = 0.0

        for rule in self.rules:
            if rule.enabled and rule.evaluate(features):
                triggered_rules.append(rule)
                score += rule.priority / 10.0

        # Normalize score
        score = min(score, 1.0)

        return {
            'score': score,
            'triggered_rules': [r.id for r in triggered_rules],
            'rule_count': len(triggered_rules)
        }


class Rule:
    """Single fraud detection rule"""

    def __init__(self, rule_dict: Dict):
        self.id = rule_dict['id']
        self.name = rule_dict['name']
        self.enabled = rule_dict.get('enabled', True)
        self.priority = rule_dict.get('priority', 5)
        self.conditions = rule_dict['conditions']
        self.operator = rule_dict.get('operator', 'AND')

    def evaluate(self, features: Dict) -> bool:
        """Evaluate rule against features"""
        results = []

        for condition in self.conditions:
            results.append(self._eval_condition(condition, features))

        if self.operator == 'AND':
            return all(results)
        elif self.operator == 'OR':
            return any(results)
        else:
            return all(results)

    def _eval_condition(self, condition: Dict, features: Dict) -> bool:
        """Evaluate single condition"""
        field = condition['field']
        operator = condition['operator']
        value = condition['value']

        feature_value = features.get(field)

        if operator == 'gt':
            return feature_value > value
        elif operator == 'lt':
            return feature_value < value
        elif operator == 'eq':
            return feature_value == value
        elif operator == 'in':
            return feature_value in value

        return False
