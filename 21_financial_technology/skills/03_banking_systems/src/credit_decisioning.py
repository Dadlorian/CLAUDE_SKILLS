from decimal import Decimal
from sklearn.linear_model import LogisticRegression
import numpy as np

class CreditDecisionEngine:
    def __init__(self, model):
        self.model = model

    def score_applicant(self, credit_score: int, income: Decimal, dti: Decimal) -> float:
        features = np.array([[credit_score, float(income), float(dti)]])
        return self.model.predict_proba(features)[0][1]

    def make_decision(self, score: float, threshold: float = 0.7) -> bool:
        return score >= threshold
