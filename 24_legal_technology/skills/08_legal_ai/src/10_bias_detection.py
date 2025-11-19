"""
Bias Detection in Legal AI
Detect and measure bias in legal AI models
"""

import numpy as np
from sklearn.metrics import confusion_matrix

class LegalAIBiasDetector:
    """Detect bias in legal AI systems"""

    def __init__(self):
        self.protected_attributes = ['gender', 'race', 'age', 'nationality']

    def calculate_disparate_impact(self, predictions, protected_group_indicator):
        """Calculate disparate impact ratio"""

        protected_approval = predictions[protected_group_indicator == 1].mean()
        unprotected_approval = predictions[protected_group_indicator == 0].mean()

        if unprotected_approval == 0:
            return None

        disparate_impact = protected_approval / unprotected_approval
        return disparate_impact

    def test_demographic_parity(self, predictions, protected_attribute):
        """Test if predictions are independent of protected attribute"""

        # Group by protected attribute
        groups = np.unique(protected_attribute)

        approval_rates = {}
        for group in groups:
            group_mask = protected_attribute == group
            approval_rates[group] = predictions[group_mask].mean()

        # Calculate range
        min_rate = min(approval_rates.values())
        max_rate = max(approval_rates.values())

        disparity = max_rate - min_rate

        return {
            "approval_rates": approval_rates,
            "disparity": disparity,
            "passes_parity": disparity < 0.2  # 20% threshold
        }

    def calculate_equalized_odds(self, y_true, y_pred, protected_attribute):
        """Calculate equalized odds metric"""

        groups = np.unique(protected_attribute)

        metrics = {}

        for group in groups:
            group_mask = protected_attribute == group
            group_true = y_true[group_mask]
            group_pred = y_pred[group_mask]

            # True positive rate
            tpr = ((group_pred == 1) & (group_true == 1)).sum() / (group_true == 1).sum()

            # False positive rate
            fpr = ((group_pred == 1) & (group_true == 0)).sum() / (group_true == 0).sum()

            metrics[group] = {"tpr": tpr, "fpr": fpr}

        return metrics

    def audit_model(self, model, X_test, y_test, protected_attributes_dict):
        """Comprehensive bias audit"""

        predictions = model.predict(X_test)

        audit_results = {}

        for attr_name, attr_values in protected_attributes_dict.items():
            # Disparate impact
            di = self.calculate_disparate_impact(predictions, attr_values)

            # Demographic parity
            dp = self.test_demographic_parity(predictions, attr_values)

            # Equalized odds
            eo = self.calculate_equalized_odds(y_test, predictions, attr_values)

            audit_results[attr_name] = {
                "disparate_impact": di,
                "demographic_parity": dp,
                "equalized_odds": eo,
                "bias_detected": di is not None and (di < 0.8 or di > 1.25)
            }

        return audit_results
