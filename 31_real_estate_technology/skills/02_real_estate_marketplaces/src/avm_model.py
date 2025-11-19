"""
Automated Valuation Model (AVM)
Machine learning model for property valuation
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyAVM:
    """Automated Valuation Model for real estate"""

    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.trained_at = None

    def train(self, sales_data: pd.DataFrame):
        """
        Train AVM model on historical sales data

        Args:
            sales_data: DataFrame with columns:
                - sale_price (target)
                - bedrooms, bathrooms, sqft, lot_size, year_built
                - latitude, longitude
                - property_type, condition_rating
                - sale_date
        """
        logger.info(f"Training AVM on {len(sales_data)} sales")

        # Feature engineering
        X = self._engineer_features(sales_data.copy())
        y = sales_data['sale_price']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=20,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train, y_train)
        self.feature_columns = X.columns.tolist()
        self.trained_at = datetime.now()

        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Calculate percentage errors
        percentage_errors = np.abs((y_test - y_pred) / y_test)
        median_error = np.median(percentage_errors)
        within_10pct = (percentage_errors < 0.10).mean()

        logger.info(f"Model Performance:")
        logger.info(f"  MAE: ${mae:,.0f}")
        logger.info(f"  R²: {r2:.4f}")
        logger.info(f"  Median Error: {median_error*100:.2f}%")
        logger.info(f"  Within 10%: {within_10pct*100:.1f}%")

        return {
            'mae': mae,
            'r2': r2,
            'median_error': median_error,
            'within_10pct': within_10pct
        }

    def predict(self, property_data: dict) -> dict:
        """
        Predict property value

        Args:
            property_data: Dict with property features

        Returns:
            Dict with estimated_value, confidence_low, confidence_high
        """
        if self.model is None:
            raise Exception("Model not trained")

        # Convert to DataFrame
        df = pd.DataFrame([property_data])

        # Engineer features
        X = self._engineer_features(df)

        # Ensure same feature columns as training
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0

        X = X[self.feature_columns]

        # Predict
        predicted_value = self.model.predict(X)[0]

        # Estimate confidence interval using tree predictions
        tree_predictions = np.array([
            tree.predict(X)[0] for tree in self.model.estimators_
        ])

        confidence_low = np.percentile(tree_predictions, 10)
        confidence_high = np.percentile(tree_predictions, 90)

        return {
            'estimated_value': int(predicted_value),
            'confidence_low': int(confidence_low),
            'confidence_high': int(confidence_high),
            'confidence_score': self._calculate_confidence(property_data)
        }

    def predict_with_comps(self, property_data: dict, comparable_sales: list) -> dict:
        """
        Predict value using both ML model and comparable sales

        Args:
            property_data: Property features
            comparable_sales: List of recent comparable sales

        Returns:
            Combined valuation with both methods
        """
        # ML prediction
        ml_result = self.predict(property_data)

        # Comp-based prediction
        comp_result = self._comps_based_valuation(
            property_data, comparable_sales
        )

        # Weighted average (60% ML, 40% comps)
        combined_value = int(
            ml_result['estimated_value'] * 0.6 +
            comp_result['estimated_value'] * 0.4
        )

        return {
            'estimated_value': combined_value,
            'ml_estimate': ml_result['estimated_value'],
            'comps_estimate': comp_result['estimated_value'],
            'confidence_low': min(ml_result['confidence_low'], comp_result['confidence_low']),
            'confidence_high': max(ml_result['confidence_high'], comp_result['confidence_high']),
            'comp_count': len(comparable_sales),
            'method': 'hybrid'
        }

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features"""
        X = df.copy()

        # Age of property
        current_year = datetime.now().year
        X['age'] = current_year - X['year_built']
        X['age_squared'] = X['age'] ** 2

        # Size ratios
        X['price_per_sqft'] = X.get('sale_price', 0) / (X['sqft'] + 1)
        X['bed_bath_ratio'] = X['bedrooms'] / (X['bathrooms'] + 0.1)
        X['lot_to_building_ratio'] = X['lot_size'] / (X['sqft'] + 1)

        # Location features (simplified - in production use clustering)
        X['lat_rounded'] = (X['latitude'] * 100).round() / 100
        X['lon_rounded'] = (X['longitude'] * 100).round() / 100

        # Property type encoding
        property_type_dummies = pd.get_dummies(
            X['property_type'], prefix='type'
        )
        X = pd.concat([X, property_type_dummies], axis=1)

        # Select numeric features
        feature_cols = [
            'bedrooms', 'bathrooms', 'sqft', 'lot_size',
            'age', 'age_squared', 'latitude', 'longitude',
            'bed_bath_ratio', 'lot_to_building_ratio',
            'condition_rating'
        ] + [col for col in X.columns if col.startswith('type_')]

        return X[feature_cols]

    def _comps_based_valuation(self, subject: dict, comps: list) -> dict:
        """Value using comparable sales"""
        if not comps:
            return {'estimated_value': 0, 'confidence_low': 0, 'confidence_high': 0}

        adjusted_prices = []

        for comp in comps:
            adjusted_price = comp['sale_price']

            # Adjust for size difference
            sqft_diff = subject['sqft'] - comp['sqft']
            adjusted_price += sqft_diff * (comp['sale_price'] / comp['sqft'])

            # Adjust for bedroom difference
            bed_diff = subject['bedrooms'] - comp['bedrooms']
            adjusted_price += bed_diff * 15000

            # Adjust for bathroom difference
            bath_diff = subject['bathrooms'] - comp['bathrooms']
            adjusted_price += bath_diff * 8000

            # Time adjustment (assume 0.5% monthly appreciation)
            months_ago = (datetime.now() - comp['sale_date']).days / 30
            appreciation = 1 + (0.005 * months_ago)
            adjusted_price *= appreciation

            adjusted_prices.append(adjusted_price)

        # Use median of adjusted comps
        estimated_value = int(np.median(adjusted_prices))
        std_dev = np.std(adjusted_prices)

        return {
            'estimated_value': estimated_value,
            'confidence_low': int(estimated_value - std_dev),
            'confidence_high': int(estimated_value + std_dev)
        }

    def _calculate_confidence(self, property_data: dict) -> float:
        """
        Calculate confidence score (0-1) based on data completeness

        Higher confidence when:
        - All features are present
        - Property is not unusual (e.g., normal bed/bath count)
        - Recent training data
        """
        confidence = 1.0

        # Penalize missing features
        required_features = ['bedrooms', 'bathrooms', 'sqft', 'year_built']
        for feature in required_features:
            if not property_data.get(feature):
                confidence *= 0.9

        # Penalize unusual properties
        if property_data.get('bedrooms', 0) > 8:
            confidence *= 0.8
        if property_data.get('sqft', 0) > 10000:
            confidence *= 0.8

        # Penalize old training data
        if self.trained_at:
            days_since_training = (datetime.now() - self.trained_at).days
            if days_since_training > 30:
                confidence *= 0.95

        return round(confidence, 2)

    def get_feature_importance(self) -> dict:
        """Get feature importance from model"""
        if self.model is None or self.feature_columns is None:
            return {}

        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_columns, importances))

        # Sort by importance
        return dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))

    def save(self, filepath: str):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'feature_columns': self.feature_columns,
            'trained_at': self.trained_at
        }, filepath)
        logger.info(f"Model saved to {filepath}")

    def load(self, filepath: str):
        """Load model from disk"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.feature_columns = data['feature_columns']
        self.trained_at = data['trained_at']
        logger.info(f"Model loaded from {filepath}")


# Usage example
if __name__ == '__main__':
    # Generate sample training data
    np.random.seed(42)
    n_samples = 1000

    sales_data = pd.DataFrame({
        'sale_price': np.random.randint(200000, 800000, n_samples),
        'bedrooms': np.random.randint(2, 6, n_samples),
        'bathrooms': np.random.randint(1, 4, n_samples),
        'sqft': np.random.randint(1000, 4000, n_samples),
        'lot_size': np.random.randint(3000, 10000, n_samples),
        'year_built': np.random.randint(1950, 2023, n_samples),
        'latitude': np.random.uniform(30.2, 30.4, n_samples),
        'longitude': np.random.uniform(-97.8, -97.6, n_samples),
        'property_type': np.random.choice(['single_family', 'condo', 'townhouse'], n_samples),
        'condition_rating': np.random.randint(1, 6, n_samples),
        'sale_date': [datetime.now() - timedelta(days=np.random.randint(0, 365)) for _ in range(n_samples)]
    })

    # Train model
    avm = PropertyAVM()
    metrics = avm.train(sales_data)

    # Predict for new property
    property_data = {
        'bedrooms': 3,
        'bathrooms': 2,
        'sqft': 2000,
        'lot_size': 6000,
        'year_built': 2010,
        'latitude': 30.2672,
        'longitude': -97.7431,
        'property_type': 'single_family',
        'condition_rating': 4
    }

    valuation = avm.predict(property_data)
    print(f"Estimated Value: ${valuation['estimated_value']:,}")
    print(f"Range: ${valuation['confidence_low']:,} - ${valuation['confidence_high']:,}")

    # Feature importance
    importance = avm.get_feature_importance()
    print("\nTop Features:")
    for feature, score in list(importance.items())[:5]:
        print(f"  {feature}: {score:.4f}")
