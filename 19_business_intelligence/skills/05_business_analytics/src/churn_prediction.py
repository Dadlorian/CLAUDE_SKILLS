"""
Churn Prediction Model
Predict customer churn using Random Forest
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

def prepare_churn_features(df):
    """Create features for churn prediction"""
    features = pd.DataFrame()
    
    # Recency features
    features['days_since_last_order'] = df['days_since_last_order']
    features['days_since_signup'] = df['days_since_signup']
    
    # Frequency features
    features['total_orders'] = df['total_orders']
    features['orders_last_30d'] = df['orders_last_30d']
    features['orders_last_90d'] = df['orders_last_90d']
    
    # Monetary features
    features['total_revenue'] = df['total_revenue']
    features['avg_order_value'] = df['avg_order_value']
    
    # Engagement trends
    features['order_frequency_trend'] = (
        df['orders_last_30d'] - df['orders_30_60d_ago']
    )
    
    return features

def train_churn_model(X_train, y_train):
    """Train Random Forest churn model"""
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate churn prediction model"""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print(f"\nROC AUC Score: {roc_auc_score(y_test, y_prob):.3f}")
    
    return y_prob

if __name__ == "__main__":
    # Load data
    df = pd.read_csv('customer_data.csv')
    
    # Prepare features
    X = prepare_churn_features(df)
    y = df['churned']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train and evaluate
    model = train_churn_model(X_train, y_train)
    probabilities = evaluate_model(model, X_test, y_test)
