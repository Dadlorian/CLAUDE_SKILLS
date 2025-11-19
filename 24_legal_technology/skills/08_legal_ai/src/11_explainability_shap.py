"""
Model Explainability using SHAP
Explain legal AI predictions with SHAP values
"""

import shap
import matplotlib.pyplot as plt

class LegalAIExplainer:
    """Explain legal AI model predictions"""

    def __init__(self, model, X_train):
        self.model = model
        self.explainer = shap.TreeExplainer(model)
        self.X_train = X_train

    def explain_prediction(self, instance, feature_names):
        """Explain single prediction"""

        shap_values = self.explainer.shap_values(instance)

        # Get feature contributions
        feature_contributions = []
        for i, name in enumerate(feature_names):
            feature_contributions.append({
                "feature": name,
                "value": instance[i],
                "shap_value": shap_values[i],
                "contribution": "positive" if shap_values[i] > 0 else "negative"
            })

        # Sort by absolute SHAP value
        feature_contributions.sort(key=lambda x: abs(x['shap_value']), reverse=True)

        return feature_contributions

    def plot_waterfall(self, instance, feature_names):
        """Create waterfall plot"""

        shap_values = self.explainer.shap_values(instance)

        shap.plots.waterfall(
            shap.Explanation(
                values=shap_values,
                base_values=self.explainer.expected_value,
                data=instance,
                feature_names=feature_names
            )
        )

    def generate_explanation(self, instance, feature_names, prediction):
        """Generate natural language explanation"""

        contributions = self.explain_prediction(instance, feature_names)

        explanation = f"Prediction: {prediction}\n\n"
        explanation += "Top factors influencing this prediction:\n\n"

        for i, contrib in enumerate(contributions[:5], 1):
            direction = "increased" if contrib['shap_value'] > 0 else "decreased"
            explanation += f"{i}. {contrib['feature']} = {contrib['value']}\n"
            explanation += f"   Impact: {direction} prediction by {abs(contrib['shap_value']):.3f}\n\n"

        return explanation
