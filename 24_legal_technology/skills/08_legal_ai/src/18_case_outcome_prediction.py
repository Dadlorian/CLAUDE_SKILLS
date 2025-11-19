"""
Case Outcome Prediction
Predict litigation outcomes using historical data
"""

from sklearn.ensemble import RandomForestClassifier
import numpy as np

class CaseOutcomePredictor:
    """Predict case outcomes"""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.feature_names = [
            'case_type',
            'jurisdiction',
            'judge_id',
            'damages_sought',
            'case_complexity',
            'evidence_quality',
            'plaintiff_attorney_experience',
            'defendant_attorney_experience'
        ]

    def train(self, X_train, y_train):
        """Train prediction model"""

        self.model.fit(X_train, y_train)

    def predict(self, case_features):
        """Predict case outcome"""

        prediction_proba = self.model.predict_proba([case_features])[0]

        outcomes = ['defendant_win', 'plaintiff_win', 'settlement']

        return {
            "predicted_outcome": outcomes[prediction_proba.argmax()],
            "confidence": prediction_proba.max(),
            "probabilities": dict(zip(outcomes, prediction_proba))
        }

    def explain_prediction(self, case_features):
        """Explain prediction factors"""

        feature_importance = self.model.feature_importances_

        explanations = []
        for i, name in enumerate(self.feature_names):
            explanations.append({
                "feature": name,
                "value": case_features[i],
                "importance": feature_importance[i]
            })

        explanations.sort(key=lambda x: x['importance'], reverse=True)

        return explanations[:5]  # Top 5 factors
