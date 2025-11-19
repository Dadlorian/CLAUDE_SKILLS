"""XGBoost AVM Implementation"""
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

class XGBoostAVM:
    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=6,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        self.feature_columns = None
        
    def prepare_features(self, df):
        """Engineer features for training"""
        X = df.copy()
        
        # Derived features
        X['age'] = 2025 - X['year_built']
        X['price_per_sqft'] = X.get('sale_price', 0) / (X['sqft'] + 1)
        X['bed_bath_ratio'] = X['bedrooms'] / (X['bathrooms'] + 0.1)
        
        # Select features
        feature_cols = [
            'bedrooms', 'bathrooms', 'sqft', 'lot_size',
            'age', 'latitude', 'longitude',
            'bed_bath_ratio'
        ]
        
        return X[feature_cols]
        
    def train(self, df):
        """Train model on sales data"""
        X = self.prepare_features(df)
        y = df['sale_price']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        self.feature_columns = X.columns.tolist()
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {'mae': mae, 'r2': r2}
        
    def predict(self, property_data):
        """Predict property value"""
        df = pd.DataFrame([property_data])
        X = self.prepare_features(df)
        return int(self.model.predict(X)[0])
