"""
Matter Cost Prediction Model
Predicts total cost and duration of legal matters using machine learning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib


class MatterCostPredictor:
    """Predicts legal matter costs using historical data and ML models."""

    def __init__(self):
        """Initialize the predictor."""
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.training_data = None

    def generate_training_data(self, num_matters: int = 500) -> pd.DataFrame:
        """Generate synthetic historical matter data for model training."""
        np.random.seed(42)

        practice_areas = ['Corporate', 'Litigation', 'IP', 'Labor', 'Tax', 'Real Estate']
        matter_types = ['M&A', 'Contract', 'Dispute', 'IPR', 'Employment', 'Other']
        complexity_levels = ['Low', 'Medium', 'High', 'Very High']
        jurisdictions = ['Federal', 'State', 'International']

        # Base costs by complexity
        complexity_cost_map = {'Low': 25000, 'Medium': 75000, 'High': 150000, 'Very High': 300000}

        data = {
            'matter_id': [f'MAT-{i:05d}' for i in range(num_matters)],
            'practice_area': np.random.choice(practice_areas, num_matters),
            'matter_type': np.random.choice(matter_types, num_matters),
            'complexity_level': np.random.choice(complexity_levels, num_matters),
            'jurisdiction': np.random.choice(jurisdictions, num_matters),
            'number_of_parties': np.random.randint(2, 10, num_matters),
            'estimated_duration_months': np.random.randint(1, 48, num_matters),
            'number_of_documents': np.random.randint(100, 50000, num_matters),
            'outside_counsel_required': np.random.choice([0, 1], num_matters),
        }

        df = pd.DataFrame(data)

        # Calculate actual costs with some noise
        df['actual_cost'] = df['complexity_level'].map(complexity_cost_map)
        df['actual_cost'] += df['number_of_documents'] * 5
        df['actual_cost'] += df['estimated_duration_months'] * 8000
        df['actual_cost'] += (df['outside_counsel_required'] * 30000)
        df['actual_cost'] += np.random.normal(0, 20000, num_matters)  # Add noise
        df['actual_cost'] = df['actual_cost'].clip(lower=5000)

        self.training_data = df
        return df

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data for model training."""
        df_processed = df.copy()

        # Encode categorical variables
        categorical_cols = ['practice_area', 'matter_type', 'complexity_level', 'jurisdiction']

        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df_processed[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                df_processed[col] = self.label_encoders[col].transform(df[col])

        return df_processed

    def train_model(self, df: pd.DataFrame = None) -> Dict:
        """Train cost prediction model."""
        if df is None:
            df = self.training_data

        df_processed = self.preprocess_data(df)

        # Feature engineering
        feature_cols = ['practice_area', 'matter_type', 'complexity_level', 'jurisdiction',
                       'number_of_parties', 'estimated_duration_months', 'number_of_documents',
                       'outside_counsel_required']

        X = df_processed[feature_cols]
        y = df_processed['actual_cost']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train ensemble model
        self.model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
        self.model.fit(X_train_scaled, y_train)

        self.feature_names = feature_cols

        # Evaluate
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)

        metrics = {
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test))
        }

        return metrics

    def predict_cost(self, matter_details: dict) -> float:
        """Predict cost for a new matter."""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")

        df_input = pd.DataFrame([matter_details])
        df_processed = self.preprocess_data(df_input)

        X = df_processed[self.feature_names]
        X_scaled = self.scaler.transform(X)

        prediction = self.model.predict(X_scaled)[0]
        return max(prediction, 0)

    def predict_batch(self, matters_df: pd.DataFrame) -> pd.DataFrame:
        """Predict costs for multiple matters."""
        df_processed = self.preprocess_data(matters_df)
        X = df_processed[self.feature_names]
        X_scaled = self.scaler.transform(X)

        predictions = self.model.predict(X_scaled)

        result = matters_df.copy()
        result['predicted_cost'] = predictions
        result['predicted_cost'] = result['predicted_cost'].clip(lower=0)

        return result

    def feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores."""
        if self.model is None:
            raise ValueError("Model not trained.")

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importance_df

    def save_model(self, filepath: str) -> None:
        """Save trained model to disk."""
        joblib.dump(self.model, f'{filepath}_model.pkl')
        joblib.dump(self.scaler, f'{filepath}_scaler.pkl')
        joblib.dump(self.label_encoders, f'{filepath}_encoders.pkl')
        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str) -> None:
        """Load trained model from disk."""
        self.model = joblib.load(f'{filepath}_model.pkl')
        self.scaler = joblib.load(f'{filepath}_scaler.pkl')
        self.label_encoders = joblib.load(f'{filepath}_encoders.pkl')
        print(f"Model loaded from {filepath}")


# Example usage
if __name__ == "__main__":
    predictor = MatterCostPredictor()

    # Generate training data
    print("Generating training data...")
    training_data = predictor.generate_training_data(500)

    # Train model
    print("Training model...")
    metrics = predictor.train_model()

    print("\n=== MODEL PERFORMANCE ===")
    for metric, value in metrics.items():
        print(f"{metric}: {value:,.2f}")

    print("\n=== FEATURE IMPORTANCE ===")
    print(predictor.feature_importance())

    # Make predictions
    new_matter = {
        'practice_area': 'Litigation',
        'matter_type': 'Dispute',
        'complexity_level': 'High',
        'jurisdiction': 'Federal',
        'number_of_parties': 4,
        'estimated_duration_months': 18,
        'number_of_documents': 10000,
        'outside_counsel_required': 1
    }

    predicted_cost = predictor.predict_cost(new_matter)
    print(f"\n=== COST PREDICTION ===")
    print(f"Predicted matter cost: ${predicted_cost:,.2f}")
