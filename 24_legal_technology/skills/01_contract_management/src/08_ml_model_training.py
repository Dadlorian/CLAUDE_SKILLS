"""
ML Model Training - Train models for contract analysis
Trains models for clause extraction, risk scoring, and classification
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import json
from typing import Tuple, Dict

class ContractMLTrainer:
    """Train ML models for contract analysis"""
    
    def __init__(self):
        self.clause_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.risk_scorer = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.le_clauses = LabelEncoder()
        self.models_trained = False
    
    def prepare_training_data(self, contracts_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features from contract data"""
        
        features = []
        
        for _, row in contracts_df.iterrows():
            text = row['content']
            
            # Text features
            word_count = len(text.split())
            sentence_count = len(text.split('.'))
            avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
            
            # Keyword features
            liability_count = text.lower().count('liability')
            termination_count = text.lower().count('termination')
            indemnif_count = text.lower().count('indemnif')
            insurance_count = text.lower().count('insurance')
            payment_count = text.lower().count('payment')
            
            feature_vector = [
                word_count,
                sentence_count,
                avg_word_length,
                liability_count,
                termination_count,
                indemnif_count,
                insurance_count,
                payment_count
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train_clause_classifier(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict:
        """Train clause type classifier"""
        
        # Encode labels
        y_encoded = self.le_clauses.fit_transform(y_train)
        
        # Train model
        self.clause_classifier.fit(X_train, y_encoded)
        
        # Evaluate
        train_accuracy = self.clause_classifier.score(X_train, y_encoded)
        
        return {
            'model': 'clause_classifier',
            'accuracy': train_accuracy,
            'classes': list(self.le_clauses.classes_)
        }
    
    def train_risk_scorer(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict:
        """Train risk scoring model"""
        
        # Ensure y_train is numeric
        y_numeric = np.array([float(y) for y in y_train])
        
        # Train model
        self.risk_scorer.fit(X_train, y_numeric)
        
        # Evaluate
        train_mse = np.mean((self.risk_scorer.predict(X_train) - y_numeric) ** 2)
        train_r2 = self.risk_scorer.score(X_train, y_numeric)
        
        return {
            'model': 'risk_scorer',
            'mse': train_mse,
            'r2_score': train_r2
        }
    
    def predict_clause_type(self, features: np.ndarray) -> Dict:
        """Predict clause type for new data"""
        
        if not hasattr(self.clause_classifier, 'classes_'):
            raise ValueError("Model not trained. Train first.")
        
        prediction = self.clause_classifier.predict(features.reshape(1, -1))[0]
        probabilities = self.clause_classifier.predict_proba(features.reshape(1, -1))[0]
        
        clause_type = self.le_clauses.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        return {
            'clause_type': clause_type,
            'confidence': float(confidence),
            'probabilities': {
                str(cls): float(prob)
                for cls, prob in zip(self.le_clauses.classes_, probabilities)
            }
        }
    
    def predict_risk_score(self, features: np.ndarray) -> Dict:
        """Predict risk score for new data"""
        
        score = self.risk_scorer.predict(features.reshape(1, -1))[0]
        
        # Map score to risk level
        if score < 2:
            risk_level = 'LOW'
        elif score < 3:
            risk_level = 'MODERATE'
        elif score < 4:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'
        
        return {
            'risk_score': float(score),
            'risk_level': risk_level
        }
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from trained models"""
        
        feature_names = [
            'word_count', 'sentence_count', 'avg_word_length',
            'liability_count', 'termination_count', 'indemnif_count',
            'insurance_count', 'payment_count'
        ]
        
        clause_importance = dict(
            zip(feature_names, self.clause_classifier.feature_importances_)
        )
        risk_importance = dict(
            zip(feature_names, self.risk_scorer.feature_importances_)
        )
        
        return {
            'clause_classifier': clause_importance,
            'risk_scorer': risk_importance
        }
    
    def save_models(self, filepath_prefix: str):
        """Save trained models to disk"""
        
        with open(f"{filepath_prefix}_clause_classifier.pkl", 'wb') as f:
            pickle.dump(self.clause_classifier, f)
        
        with open(f"{filepath_prefix}_risk_scorer.pkl", 'wb') as f:
            pickle.dump(self.risk_scorer, f)
        
        with open(f"{filepath_prefix}_label_encoder.pkl", 'wb') as f:
            pickle.dump(self.le_clauses, f)
    
    def load_models(self, filepath_prefix: str):
        """Load trained models from disk"""
        
        with open(f"{filepath_prefix}_clause_classifier.pkl", 'rb') as f:
            self.clause_classifier = pickle.load(f)
        
        with open(f"{filepath_prefix}_risk_scorer.pkl", 'rb') as f:
            self.risk_scorer = pickle.load(f)
        
        with open(f"{filepath_prefix}_label_encoder.pkl", 'rb') as f:
            self.le_clauses = pickle.load(f)


# Example usage
if __name__ == "__main__":
    # Load training data
    contracts_df = pd.read_csv('training_contracts.csv')
    
    trainer = ContractMLTrainer()
    
    # Prepare data
    X = trainer.prepare_training_data(contracts_df)
    y_clauses = contracts_df['clause_type'].values
    y_risk = contracts_df['risk_score'].values
    
    # Split data
    X_train, X_test, y_clause_train, y_clause_test = train_test_split(
        X, y_clauses, test_size=0.2, random_state=42
    )
    
    # Train models
    clause_results = trainer.train_clause_classifier(X_train, y_clause_train)
    print(f"Clause classifier accuracy: {clause_results['accuracy']:.4f}")
    
    # Train risk scorer
    risk_results = trainer.train_risk_scorer(X_train, y_risk[:len(y_clause_train)])
    print(f"Risk scorer R2: {risk_results['r2_score']:.4f}")
    
    # Save models
    trainer.save_models("trained_models")
