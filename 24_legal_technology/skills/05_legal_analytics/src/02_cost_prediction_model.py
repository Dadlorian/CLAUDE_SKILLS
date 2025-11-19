#!/usr/bin/env python3
"""
Legal Matter Cost Prediction Model
Predicts litigation and matter costs using machine learning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

class CostPredictionModel:
    """Predict matter costs based on historical data"""

    def __init__(self):
        """Initialize the model"""
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = [
            'case_complexity',  # 1-5 scale
            'claim_amount',
            'discovery_volume',  # estimated documents
            'number_of_parties',
            'expert_witnesses',
            'judge_assignment',
            'case_type_code'  # litigation, transaction, etc
        ]
        self.is_trained = False

    def prepare_data(self, case_data):
        """Prepare data for model training"""
        X = case_data[self.feature_names].copy()
        y = case_data['actual_cost'].copy()

        # Handle missing values
        X = X.fillna(X.mean())

        # Normalize features
        X_scaled = self.scaler.fit_transform(X)

        return X_scaled, y

    def train(self, historical_cases):
        """Train model on historical case data"""
        X, y = self.prepare_data(historical_cases)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Calculate accuracy
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        return {
            'training_r2': train_score,
            'testing_r2': test_score,
            'model_status': 'Trained successfully'
        }

    def predict_cost(self, case_features):
        """Predict cost for a new case"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        # Ensure features are in correct order
        case_array = np.array([case_features[f] for f in self.feature_names]).reshape(1, -1)

        # Scale features
        case_scaled = self.scaler.transform(case_array)

        # Make prediction
        predicted_cost = self.model.predict(case_scaled)[0]

        # Add confidence interval (rough estimate)
        confidence = self.model.score(case_scaled, [predicted_cost])

        return {
            'predicted_cost': predicted_cost,
            'confidence': confidence,
            'estimated_range_low': predicted_cost * 0.85,
            'estimated_range_high': predicted_cost * 1.15
        }

    def get_feature_importance(self):
        """Get importance of each feature"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importance_df

    def batch_predict(self, cases_df):
        """Predict costs for multiple cases"""
        predictions = []

        for _, case in cases_df.iterrows():
            features = {col: case[col] for col in self.feature_names}
            prediction = self.predict_cost(features)
            prediction['case_id'] = case.get('case_id', '')
            predictions.append(prediction)

        return pd.DataFrame(predictions)


# Example cost prediction with phase breakdown
def predict_matter_cost_by_phase(case_complexity, claim_amount, case_type):
    """
    Predict cost breakdown by litigation phase

    Args:
        case_complexity: 1-5 scale
        claim_amount: Amount in dispute
        case_type: 'simple', 'moderate', 'complex'

    Returns:
        Dictionary with cost by phase
    """

    # Base costs by case type
    base_costs = {
        'simple': {
            'pleadings': 20000,
            'discovery': 60000,
            'motions': 15000,
            'trial': 25000
        },
        'moderate': {
            'pleadings': 35000,
            'discovery': 150000,
            'motions': 40000,
            'trial': 75000
        },
        'complex': {
            'pleadings': 50000,
            'discovery': 300000,
            'motions': 75000,
            'trial': 150000
        }
    }

    phases = base_costs[case_type].copy()

    # Adjust for complexity multiplier
    complexity_multiplier = 1 + (case_complexity - 1) * 0.15

    # Adjust for claim amount (higher claims = more resources)
    claim_multiplier = min(1 + (claim_amount / 1000000) * 0.2, 2.0)

    # Apply multipliers
    for phase in phases:
        phases[phase] = int(phases[phase] * complexity_multiplier * claim_multiplier)

    # Calculate totals
    total_cost = sum(phases.values())
    phases['total_estimated_cost'] = total_cost
    phases['cost_range_low'] = int(total_cost * 0.85)
    phases['cost_range_high'] = int(total_cost * 1.15)

    return phases


if __name__ == "__main__":
    # Example usage
    print("Cost Prediction Examples")
    print("=" * 50)

    # Example 1: Simple matter
    simple_case = predict_matter_cost_by_phase(
        case_complexity=2,
        claim_amount=100000,
        case_type='simple'
    )
    print("\nSimple Matter Cost Estimate:")
    print(f"Pleadings: ${simple_case['pleadings']:,}")
    print(f"Discovery: ${simple_case['discovery']:,}")
    print(f"Motions: ${simple_case['motions']:,}")
    print(f"Trial: ${simple_case['trial']:,}")
    print(f"Total: ${simple_case['total_estimated_cost']:,}")
    print(f"Range: ${simple_case['cost_range_low']:,} - ${simple_case['cost_range_high']:,}")

    # Example 2: Complex matter
    complex_case = predict_matter_cost_by_phase(
        case_complexity=5,
        claim_amount=5000000,
        case_type='complex'
    )
    print("\n\nComplex Matter Cost Estimate:")
    print(f"Pleadings: ${complex_case['pleadings']:,}")
    print(f"Discovery: ${complex_case['discovery']:,}")
    print(f"Motions: ${complex_case['motions']:,}")
    print(f"Trial: ${complex_case['trial']:,}")
    print(f"Total: ${complex_case['total_estimated_cost']:,}")
    print(f"Range: ${complex_case['cost_range_low']:,} - ${complex_case['cost_range_high']:,}")
