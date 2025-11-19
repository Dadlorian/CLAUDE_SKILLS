"""Sepsis Prediction Model using ML"""
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SepsisFeatures:
    hr: float; temp: float; rr: float; sbp: float
    wbc: float; lactate: float; age: int

class SepsisPredictionModel:
    def __init__(self):
        self.model = GradientBoostingClassifier()
        self.threshold = 0.15
    
    def predict_sepsis_risk(self, features: SepsisFeatures) -> Dict:
        X = self._extract_features(features)
        prob = self.model.predict_proba([X])[0][1]
        return {'probability': prob, 'risk_tier': self._classify_risk(prob)}
    
    def _classify_risk(self, prob: float) -> str:
        if prob >= 0.30: return 'CRITICAL'
        if prob >= 0.15: return 'HIGH'
        if prob >= 0.05: return 'MODERATE'
        return 'LOW'
    
    def _extract_features(self, f: SepsisFeatures) -> List[float]:
        return [f.hr, f.temp, f.rr, f.sbp, f.wbc, f.lactate, f.age]
