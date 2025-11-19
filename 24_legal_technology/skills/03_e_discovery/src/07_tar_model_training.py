"""
TAR Model Training Example
Demonstrates technology-assisted review model development
"""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import json

class TARModelTrainer:
    """Trains and manages TAR (predictive coding) models"""

    def __init__(self, model_name: str):
        """
        Initialize TAR model trainer

        Args:
            model_name: Name for the model
        """
        self.model_name = model_name
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        self.training_history = []
        self.is_trained = False

    def train_initial_model(self, training_set: List[Dict]) -> Dict:
        """
        Train initial TAR model on manually coded sample

        Args:
            training_set: List of documents with 'id', 'text', and 'responsive' fields

        Returns:
            Model performance metrics
        """
        if len(training_set) < 50:
            raise ValueError("Minimum 50 training documents required")

        # Extract features and labels
        texts = [doc.get('text', '') for doc in training_set]
        labels = [1 if doc.get('responsive', False) else 0 for doc in training_set]

        # Vectorize
        X = self.vectorizer.fit_transform(texts)

        # Train classifier
        self.classifier.fit(X, labels)
        self.is_trained = True

        # Evaluate on training set
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)

        metrics = {
            "training_docs": len(training_set),
            "responsive_count": sum(labels),
            "non_responsive_count": len(labels) - sum(labels),
            "precision": float(precision_score(labels, predictions)),
            "recall": float(recall_score(labels, predictions)),
            "f1_score": float(f1_score(labels, predictions))
        }

        self.training_history.append({
            "iteration": 1,
            "training_size": len(training_set),
            "metrics": metrics
        })

        return metrics

    def predict_documents(self, documents: List[Dict],
                         confidence_threshold: float = 0.5) -> Dict[str, List]:
        """
        Predict responsiveness for unlabeled documents

        Args:
            documents: List of documents with 'id' and 'text'
            confidence_threshold: Probability threshold for automatic coding (0-1)

        Returns:
            Dict with auto-coded, review, and uncertain documents
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        texts = [doc.get('text', '') for doc in documents]
        doc_ids = [doc.get('id') for doc in documents]

        # Vectorize and predict
        X = self.vectorizer.transform(texts)
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)

        # Get probability of responsive class (index 1)
        responsive_probs = probabilities[:, 1]

        results = {
            "responsive_auto_coded": [],
            "non_responsive_auto_coded": [],
            "uncertain_for_review": []
        }

        for i, doc_id in enumerate(doc_ids):
            prob = responsive_probs[i]
            doc_info = {
                "document_id": doc_id,
                "predicted_responsive": bool(predictions[i]),
                "confidence": float(prob)
            }

            if prob >= (1 - confidence_threshold) and prob >= 0.75:
                results["responsive_auto_coded"].append(doc_info)
            elif prob <= confidence_threshold and prob <= 0.25:
                results["non_responsive_auto_coded"].append(doc_info)
            else:
                results["uncertain_for_review"].append(doc_info)

        return results

    def get_model_features(self, top_n: int = 20) -> Dict[str, List]:
        """
        Get most influential features for model predictions

        Args:
            top_n: Number of top features to return

        Returns:
            Dict with top responsive and non-responsive features
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")

        feature_names = self.vectorizer.get_feature_names_out()
        coefficients = self.classifier.coef_[0]

        # Top positive features (indicate responsive)
        top_responsive_indices = np.argsort(coefficients)[-top_n:][::-1]
        top_responsive = [feature_names[i] for i in top_responsive_indices]

        # Top negative features (indicate non-responsive)
        top_non_responsive_indices = np.argsort(coefficients)[:top_n]
        top_non_responsive = [feature_names[i] for i in top_non_responsive_indices]

        return {
            "responsive_indicators": top_responsive,
            "non_responsive_indicators": top_non_responsive
        }

    def iterative_training(self, seed_documents: List[Dict],
                          predicted_batch: List[Dict],
                          feedback: List[Dict]) -> Dict:
        """
        Train model with new labeled documents for next iteration

        Args:
            seed_documents: Previous training set
            predicted_batch: Previously predicted documents
            feedback: Corrections to predictions (with 'id' and 'responsive')

        Returns:
            Updated model performance
        """
        # Combine previous training with new feedback
        new_training_set = list(seed_documents)

        # Create document map for feedback application
        feedback_map = {item['id']: item['responsive'] for item in feedback}

        for doc in predicted_batch:
            if doc['document_id'] in feedback_map:
                new_training_set.append({
                    'id': doc['document_id'],
                    'text': doc.get('text', ''),
                    'responsive': feedback_map[doc['document_id']]
                })

        # Retrain model
        metrics = self.train_initial_model(new_training_set)
        iteration = len(self.training_history)

        self.training_history.append({
            "iteration": iteration,
            "training_size": len(new_training_set),
            "new_feedback": len(feedback),
            "metrics": metrics
        })

        return metrics

    def get_training_progress(self) -> Dict:
        """
        Get model training progression

        Returns:
            Training history and convergence metrics
        """
        if not self.training_history:
            return {}

        return {
            "model_name": self.model_name,
            "total_iterations": len(self.training_history),
            "training_history": self.training_history,
            "current_f1": self.training_history[-1]['metrics']['f1_score']
        }


class TAREvaluator:
    """Evaluates TAR model performance"""

    @staticmethod
    def evaluate_on_test_set(model_trainer: TARModelTrainer,
                            test_set: List[Dict]) -> Dict:
        """
        Evaluate trained model on hold-out test set

        Args:
            model_trainer: Trained TARModelTrainer instance
            test_set: List of documents with 'text' and 'responsive'

        Returns:
            Comprehensive evaluation metrics
        """
        texts = [doc.get('text', '') for doc in test_set]
        labels = [1 if doc.get('responsive', False) else 0 for doc in test_set]

        X = model_trainer.vectorizer.transform(texts)
        predictions = model_trainer.classifier.predict(X)

        tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()

        return {
            "test_documents": len(test_set),
            "precision": float(precision_score(labels, predictions)),
            "recall": float(recall_score(labels, predictions)),
            "f1_score": float(f1_score(labels, predictions)),
            "accuracy": float((tp + tn) / (tp + tn + fp + fn)),
            "specificity": float(tn / (tn + fp)) if (tn + fp) > 0 else 0,
            "sensitivity": float(tp / (tp + fn)) if (tp + fn) > 0 else 0,
            "confusion_matrix": {
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp)
            }
        }

    @staticmethod
    def calculate_cost_benefit(predictions: Dict,
                             cost_per_review: float = 5.0,
                             cost_per_auto_code_error: float = 50.0) -> Dict:
        """
        Calculate cost-benefit of using TAR vs manual review

        Args:
            predictions: Output from predict_documents
            cost_per_review: Cost per document manual review
            cost_per_auto_code_error: Cost of incorrect auto-coding

        Returns:
            Cost analysis
        """
        auto_coded = (len(predictions.get('responsive_auto_coded', [])) +
                     len(predictions.get('non_responsive_auto_coded', [])))
        to_review = len(predictions.get('uncertain_for_review', []))

        # Calculate costs
        manual_review_cost = (auto_coded + to_review) * cost_per_review
        tar_review_cost = to_review * cost_per_review

        # Assume 5% error rate on auto-coded documents
        estimated_errors = auto_coded * 0.05
        error_cost = estimated_errors * cost_per_auto_code_error

        tar_total_cost = tar_review_cost + error_cost

        return {
            "manual_review_total_cost": manual_review_cost,
            "tar_total_cost": tar_total_cost,
            "cost_savings": manual_review_cost - tar_total_cost,
            "auto_coded_documents": auto_coded,
            "documents_for_review": to_review,
            "estimated_errors": int(estimated_errors),
            "roi_percentage": ((manual_review_cost - tar_total_cost) / manual_review_cost * 100)
            if manual_review_cost > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    # Sample training data
    training_docs = [
        {"id": i, "text": "Contract regarding services and payment terms", "responsive": True}
        for i in range(1, 26)
    ] + [
        {"id": i, "text": "General company email about meetings", "responsive": False}
        for i in range(26, 51)
    ]

    # Train model
    trainer = TARModelTrainer("contract_review_model")
    metrics = trainer.train_initial_model(training_docs)

    print(f"Initial Model Metrics:")
    print(f"  Precision: {metrics['precision']:.2%}")
    print(f"  Recall: {metrics['recall']:.2%}")
    print(f"  F1 Score: {metrics['f1_score']:.2%}")

    # Get important features
    features = trainer.get_model_features()
    print(f"\nTop Responsive Indicators: {features['responsive_indicators'][:5]}")
