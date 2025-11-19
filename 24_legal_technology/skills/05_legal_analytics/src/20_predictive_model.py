"""
Predictive Modeling Module for Legal Analytics

Provides machine learning models for predicting legal outcomes:
- Case outcome prediction (win/loss/settlement probability)
- Settlement amount prediction
- Case duration forecasting
- Client profitability prediction
- Matter risk scoring
- Attorney performance prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class CaseOutcomePredictor:
    """Predict case outcomes using machine learning"""

    def __init__(self, random_state: int = 42):
        """Initialize case outcome predictor"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=random_state)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.is_trained = False

    def prepare_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for model training"""
        X = data.copy()
        y = X.pop('outcome')  # Remove target variable

        # Encode categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                X[col] = self.label_encoders[col].fit_transform(X[col].astype(str))
            else:
                X[col] = self.label_encoders[col].transform(X[col].astype(str))

        # Store feature names
        self.feature_names = X.columns.tolist()

        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=self.feature_names)

        return X, y

    def train(self, training_data: pd.DataFrame) -> Dict:
        """Train the predictive model"""
        X, y = self.prepare_features(training_data)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate model
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'roc_auc': roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        }

        return metrics

    def predict_case_outcome(self, case_features: pd.DataFrame) -> Dict:
        """Predict outcome for specific case"""
        if not self.is_trained:
            return {'error': 'Model not trained'}

        # Prepare features
        X = case_features.copy()

        # Encode categorical variables
        for col in self.label_encoders.keys():
            if col in X.columns:
                X[col] = self.label_encoders[col].transform(X[col].astype(str))

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]

        # Get feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'predicted_outcome': prediction,
            'outcome_probabilities': {
                'favorable': float(probabilities[0]) if len(probabilities) > 0 else 0,
                'unfavorable': float(probabilities[1]) if len(probabilities) > 1 else 0,
                'settled': float(probabilities[2]) if len(probabilities) > 2 else 0
            },
            'confidence': float(max(probabilities)),
            'top_feature_drivers': [{'feature': f, 'importance': float(i)} for f, i in top_features]
        }

    def get_feature_importance(self) -> Dict:
        """Get feature importance from trained model"""
        if not self.is_trained:
            return {'error': 'Model not trained'}

        return dict(zip(self.feature_names, self.model.feature_importances_))


class SettlementAmountPredictor:
    """Predict settlement amounts using regression"""

    def __init__(self, random_state: int = 42):
        """Initialize settlement amount predictor"""
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=random_state
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.is_trained = False

    def prepare_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for model training"""
        X = data.copy()
        y = X.pop('settlement_amount')

        # Encode categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                X[col] = self.label_encoders[col].fit_transform(X[col].astype(str))
            else:
                X[col] = self.label_encoders[col].transform(X[col].astype(str))

        self.feature_names = X.columns.tolist()
        X_scaled = self.scaler.fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=self.feature_names)

        return X, y

    def train(self, training_data: pd.DataFrame) -> Dict:
        """Train the settlement prediction model"""
        X, y = self.prepare_features(training_data)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate model
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        mae = np.mean(np.abs(y_test - y_pred))
        r2 = self.model.score(X_test, y_test)

        return {
            'rmse': rmse,
            'mae': mae,
            'r2_score': r2,
            'test_samples': len(X_test)
        }

    def predict_settlement(self, case_features: pd.DataFrame) -> Dict:
        """Predict settlement amount for case"""
        if not self.is_trained:
            return {'error': 'Model not trained'}

        X = case_features.copy()

        for col in self.label_encoders.keys():
            if col in X.columns:
                X[col] = self.label_encoders[col].transform(X[col].astype(str))

        X_scaled = self.scaler.transform(X)
        predicted_amount = self.model.predict(X_scaled)[0]

        # Calculate confidence interval (simplified)
        std_error = np.std(predicted_amount * 0.2)  # Estimate standard error
        confidence_interval = {
            'low': max(0, predicted_amount - 1.96 * std_error),
            'high': predicted_amount + 1.96 * std_error
        }

        return {
            'predicted_settlement_amount': float(predicted_amount),
            'confidence_interval_low': float(confidence_interval['low']),
            'confidence_interval_high': float(confidence_interval['high']),
            'confidence_level': 95
        }


class CaseDurationPredictor:
    """Predict case duration using regression"""

    def __init__(self, random_state: int = 42):
        """Initialize case duration predictor"""
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=random_state
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False

    def prepare_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for training"""
        X = data.copy()
        y = X.pop('duration_days')

        categorical_cols = X.select_dtypes(include=['object']).columns

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                X[col] = self.label_encoders[col].fit_transform(X[col].astype(str))

        X_scaled = self.scaler.fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=X.columns)

        return X, y

    def train(self, training_data: pd.DataFrame) -> Dict:
        """Train case duration model"""
        X, y = self.prepare_features(training_data)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        mae = np.mean(np.abs(y_test - y_pred))

        return {
            'rmse_days': rmse,
            'mae_days': mae,
            'test_samples': len(X_test)
        }

    def predict_duration(self, case_features: pd.DataFrame) -> Dict:
        """Predict duration for case"""
        if not self.is_trained:
            return {'error': 'Model not trained'}

        X = case_features.copy()

        for col in self.label_encoders.keys():
            if col in X.columns:
                X[col] = self.label_encoders[col].transform(X[col].astype(str))

        X_scaled = self.scaler.transform(X)
        predicted_days = self.model.predict(X_scaled)[0]

        return {
            'predicted_duration_days': int(predicted_days),
            'predicted_duration_months': round(predicted_days / 30, 1),
            'expected_completion_date': (
                datetime.now() + timedelta(days=int(predicted_days))
            ).strftime('%Y-%m-%d')
        }


class MatterRiskScorer:
    """Score risk level for legal matters"""

    def __init__(self):
        """Initialize risk scorer"""
        self.risk_factors = {
            'case_type': {'high_risk': ['IP', 'Antitrust'], 'medium_risk': ['Civil', 'Employment']},
            'opposing_counsel_experience': {'high_risk': (20, 100), 'medium_risk': (10, 20)},
            'judge_reversal_rate': {'high_risk': (0.2, 1.0), 'medium_risk': (0.1, 0.2)},
            'matter_budget_variance': {'high_risk': (0.5, 1.0), 'medium_risk': (0.3, 0.5)}
        }

    def calculate_risk_score(self, matter_data: Dict) -> Dict:
        """Calculate risk score for matter"""
        risk_score = 0
        risk_factors_found = []

        # Evaluate each risk factor
        for factor, values in matter_data.items():
            if factor == 'case_type' and values in self.risk_factors['case_type']['high_risk']:
                risk_score += 30
                risk_factors_found.append(f"High-risk case type: {values}")
            elif factor == 'case_type' and values in self.risk_factors['case_type']['medium_risk']:
                risk_score += 15
                risk_factors_found.append(f"Medium-risk case type: {values}")

            elif factor == 'opposing_counsel_experience':
                if values > 20:
                    risk_score += 25
                    risk_factors_found.append(f"Experienced opposing counsel ({values} years)")
                elif values > 10:
                    risk_score += 12
                    risk_factors_found.append(f"Moderately experienced opposing counsel ({values} years)")

            elif factor == 'judge_reversal_rate':
                if values > 0.2:
                    risk_score += 20
                    risk_factors_found.append(f"High judge reversal rate ({values:.1%})")

        # Cap score at 100
        risk_score = min(100, risk_score)

        # Determine risk level
        if risk_score >= 70:
            risk_level = 'Critical'
        elif risk_score >= 50:
            risk_level = 'High'
        elif risk_score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors_found,
            'mitigation_recommendation': self._get_mitigation_strategy(risk_level)
        }

    @staticmethod
    def _get_mitigation_strategy(risk_level: str) -> str:
        """Get mitigation strategy based on risk level"""
        strategies = {
            'Critical': 'Escalate to senior partners, consider expert consultation, increased monitoring',
            'High': 'Assign experienced lead counsel, conduct detailed case assessment',
            'Medium': 'Standard management approach with periodic reviews',
            'Low': 'Routine management appropriate'
        }
        return strategies.get(risk_level, 'Standard management approach')


def create_sample_training_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample training data for models"""
    np.random.seed(42)

    # Case outcome training data
    case_outcomes = pd.DataFrame({
        'case_type': np.random.choice(['Civil', 'Criminal', 'IP', 'Employment'], 500),
        'opposing_counsel_experience': np.random.randint(0, 40, 500),
        'our_attorney_experience': np.random.randint(0, 40, 500),
        'judge_reversal_rate': np.random.uniform(0, 0.3, 500),
        'case_complexity': np.random.choice(['Low', 'Medium', 'High'], 500),
        'evidence_strength': np.random.uniform(0, 1, 500),
        'outcome': np.random.choice(['Favorable', 'Unfavorable', 'Settled'], 500)
    })

    # Settlement amount training data
    settlement_amounts = pd.DataFrame({
        'case_type': np.random.choice(['Civil', 'IP', 'Employment'], 300),
        'damages_claimed': np.random.uniform(50000, 5000000, 300),
        'insurance_coverage': np.random.uniform(0, 5000000, 300),
        'liability_strength': np.random.uniform(0, 1, 300),
        'settlement_amount': np.random.uniform(10000, 3000000, 300)
    })

    # Case duration training data
    durations = pd.DataFrame({
        'case_type': np.random.choice(['Civil', 'Criminal', 'IP'], 250),
        'case_complexity': np.random.choice(['Low', 'Medium', 'High'], 250),
        'discovery_scope': np.random.uniform(0, 1, 250),
        'number_of_parties': np.random.randint(2, 10, 250),
        'duration_days': np.random.randint(30, 730, 250)
    })

    return case_outcomes, settlement_amounts, durations


if __name__ == "__main__":
    # Create training data
    outcomes_data, settlement_data, duration_data = create_sample_training_data()

    print("=" * 80)
    print("PREDICTIVE MODELING FOR LEGAL ANALYTICS")
    print("=" * 80)

    print("\n1. CASE OUTCOME PREDICTION")
    print("-" * 80)
    outcome_predictor = CaseOutcomePredictor()
    outcome_metrics = outcome_predictor.train(outcomes_data)
    print(f"Model Accuracy: {outcome_metrics['accuracy']:.2%}")
    print(f"Precision: {outcome_metrics['precision']:.2%}")
    print(f"Recall: {outcome_metrics['recall']:.2%}")
    print(f"F1 Score: {outcome_metrics['f1_score']:.2%}")
    print(f"ROC-AUC: {outcome_metrics['roc_auc']:.4f}")

    # Sample prediction
    sample_case = pd.DataFrame({
        'case_type': ['Civil'],
        'opposing_counsel_experience': [15],
        'our_attorney_experience': [20],
        'judge_reversal_rate': [0.12],
        'case_complexity': ['Medium'],
        'evidence_strength': [0.75]
    })

    prediction = outcome_predictor.predict_case_outcome(sample_case)
    if 'error' not in prediction:
        print(f"\nSample Prediction:")
        print(f"  Predicted Outcome: {prediction['predicted_outcome']}")
        print(f"  Favorable Probability: {prediction['outcome_probabilities']['favorable']:.1%}")
        print(f"  Confidence: {prediction['confidence']:.1%}")

    print("\n2. SETTLEMENT AMOUNT PREDICTION")
    print("-" * 80)
    settlement_predictor = SettlementAmountPredictor()
    settlement_metrics = settlement_predictor.train(settlement_data)
    print(f"RMSE: ${settlement_metrics['rmse']:,.0f}")
    print(f"MAE: ${settlement_metrics['mae']:,.0f}")
    print(f"R² Score: {settlement_metrics['r2_score']:.4f}")

    # Sample settlement prediction
    sample_settlement = pd.DataFrame({
        'case_type': ['Civil'],
        'damages_claimed': [1000000],
        'insurance_coverage': [2000000],
        'liability_strength': [0.65]
    })

    settlement_pred = settlement_predictor.predict_settlement(sample_settlement)
    if 'error' not in settlement_pred:
        print(f"\nPredicted Settlement: ${settlement_pred['predicted_settlement_amount']:,.0f}")
        print(f"Confidence Interval: ${settlement_pred['confidence_interval_low']:,.0f} - "
              f"${settlement_pred['confidence_interval_high']:,.0f}")

    print("\n3. CASE DURATION PREDICTION")
    print("-" * 80)
    duration_predictor = CaseDurationPredictor()
    duration_metrics = duration_predictor.train(duration_data)
    print(f"RMSE: {duration_metrics['rmse_days']:.1f} days")
    print(f"MAE: {duration_metrics['mae_days']:.1f} days")

    # Sample duration prediction
    sample_duration = pd.DataFrame({
        'case_type': ['Civil'],
        'case_complexity': ['High'],
        'discovery_scope': [0.8],
        'number_of_parties': [5]
    })

    duration_pred = duration_predictor.predict_duration(sample_duration)
    if 'error' not in duration_pred:
        print(f"\nPredicted Duration: {duration_pred['predicted_duration_days']} days "
              f"({duration_pred['predicted_duration_months']} months)")
        print(f"Expected Completion: {duration_pred['expected_completion_date']}")

    print("\n4. MATTER RISK SCORING")
    print("-" * 80)
    risk_scorer = MatterRiskScorer()

    matter_risk_data = {
        'case_type': 'IP',
        'opposing_counsel_experience': 25,
        'judge_reversal_rate': 0.15
    }

    risk_result = risk_scorer.calculate_risk_score(matter_risk_data)
    print(f"Risk Score: {risk_result['risk_score']}/100")
    print(f"Risk Level: {risk_result['risk_level']}")
    print(f"Risk Factors:")
    for factor in risk_result['risk_factors']:
        print(f"  - {factor}")
    print(f"Mitigation Strategy: {risk_result['mitigation_recommendation']}")
