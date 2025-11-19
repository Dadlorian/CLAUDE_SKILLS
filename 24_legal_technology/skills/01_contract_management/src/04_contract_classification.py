"""
Contract Classification - Classify contracts by type using ML
Uses scikit-learn for text classification
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pickle
import json
from typing import List, Tuple

class ContractClassifier:
    """Classify contracts by type"""
    
    CONTRACT_TYPES = [
        'Service Agreement',
        'Purchase Agreement',
        'NDA',
        'Employment Agreement',
        'License Agreement',
        'Partnership Agreement',
        'Lease Agreement',
        'Vendor Agreement',
    ]
    
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB())
        ])
        self.is_trained = False
    
    def train(self, texts: List[str], labels: List[str]):
        """Train classifier on labeled contract texts"""
        self.pipeline.fit(texts, labels)
        self.is_trained = True
        return self
    
    def predict(self, text: str) -> Tuple[str, float]:
        """Predict contract type and confidence"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        prediction = self.pipeline.predict([text])[0]
        probabilities = self.pipeline.predict_proba([text])[0]
        max_prob = max(probabilities)
        
        return prediction, max_prob
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float]]:
        """Predict types for multiple contracts"""
        results = []
        for text in texts:
            pred, conf = self.predict(text)
            results.append({'text': text[:100], 'type': pred, 'confidence': float(conf)})
        return results
    
    def extract_keywords(self, contract_type: str) -> List[str]:
        """Get top keywords for each contract type"""
        feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
        coef = self.pipeline.named_steps['classifier'].feature_log_prob_
        
        type_index = list(self.CONTRACT_TYPES).index(contract_type)
        top_indices = coef[type_index].argsort()[-10:][::-1]
        
        return [feature_names[i] for i in top_indices]
    
    def save_model(self, filepath: str):
        """Save trained model"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.pipeline, f)
    
    def load_model(self, filepath: str):
        """Load trained model"""
        with open(filepath, 'rb') as f:
            self.pipeline = pickle.load(f)
        self.is_trained = True
        return self


# Example usage
if __name__ == "__main__":
    classifier = ContractClassifier()
    
    # Sample training data
    training_texts = [
        "This Service Agreement is between the Provider and Client...",
        "The Vendor shall supply products as specified in the schedule...",
        "This Non-Disclosure Agreement protects confidential information...",
        # ... more training examples
    ]
    
    training_labels = [
        'Service Agreement',
        'Purchase Agreement',
        'NDA',
    ]
    
    # Train and predict
    classifier.train(training_texts, training_labels)
    pred, conf = classifier.predict("Services include cloud infrastructure...")
    print(f"Predicted type: {pred} (confidence: {conf:.2f})")
