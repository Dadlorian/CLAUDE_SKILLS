"""
TAR Continuous Active Learning (CAL) Example
Demonstrates iterative machine learning for document review
"""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.uncertainty_sampling import UncertaintySampling

class CALStrategy:
    """Implements Continuous Active Learning for TAR"""

    def __init__(self, model_trainer, initial_sample_size: int = 500):
        """
        Initialize CAL strategy

        Args:
            model_trainer: TARModelTrainer instance
            initial_sample_size: Documents for initial training
        """
        self.model_trainer = model_trainer
        self.initial_sample_size = initial_sample_size
        self.iteration = 0
        self.total_reviewed = 0
        self.cal_log = []

    def select_next_batch(self, unlabeled_documents: List[Dict],
                         batch_size: int = 100) -> List[Dict]:
        """
        Select most valuable documents for next review batch

        Uses uncertainty sampling to select documents closest to decision boundary

        Args:
            unlabeled_documents: Remaining unlabeled documents
            batch_size: Number of documents to select

        Returns:
            Selected documents ranked by uncertainty
        """
        texts = [doc.get('text', '') for doc in unlabeled_documents]
        doc_ids = [doc.get('id') for doc in unlabeled_documents]

        # Vectorize
        X = self.model_trainer.vectorizer.transform(texts)

        # Get prediction probabilities
        probabilities = self.model_trainer.classifier.predict_proba(X)

        # Calculate uncertainty (distance from 0.5 probability)
        uncertainty = np.abs(probabilities[:, 1] - 0.5)

        # Select documents with highest uncertainty
        top_indices = np.argsort(-uncertainty)[:batch_size]

        selected = []
        for idx in top_indices:
            selected.append({
                "document_id": doc_ids[idx],
                "uncertainty": float(uncertainty[idx]),
                "probability": float(probabilities[idx, 1]),
                "text": texts[idx]
            })

        return selected

    def apply_feedback_and_retrain(self, review_batch: List[Dict],
                                  feedback: List[Dict]) -> Dict:
        """
        Incorporate human feedback and retrain model

        Args:
            review_batch: Original selected documents
            feedback: List with 'document_id' and 'responsive' fields

        Returns:
            Updated model metrics
        """
        self.iteration += 1

        # Create feedback map
        feedback_map = {item['document_id']: item['responsive']
                       for item in feedback}

        # Add reviewed documents to training set
        new_training_docs = []
        for doc in review_batch:
            if doc['document_id'] in feedback_map:
                new_training_docs.append({
                    'id': doc['document_id'],
                    'text': doc['text'],
                    'responsive': feedback_map[doc['document_id']]
                })

        # Retrain model
        metrics = self.model_trainer.train_initial_model(new_training_docs)

        self.total_reviewed += len(feedback)

        # Log iteration
        self.cal_log.append({
            "iteration": self.iteration,
            "batch_size": len(feedback),
            "total_reviewed": self.total_reviewed,
            "metrics": metrics
        })

        return metrics

    def get_convergence_status(self) -> Dict:
        """
        Evaluate model convergence

        Returns:
            Convergence metrics
        """
        if len(self.cal_log) < 2:
            return {"status": "insufficient_data"}

        # Check F1 score trend
        f1_scores = [log['metrics']['f1_score'] for log in self.cal_log]
        recent_improvement = f1_scores[-1] - f1_scores[-2]

        # Calculate average improvement
        improvements = [f1_scores[i] - f1_scores[i-1]
                       for i in range(1, len(f1_scores))]
        avg_improvement = np.mean(improvements) if improvements else 0

        # Estimate convergence
        if avg_improvement < 0.001:
            convergence_status = "converged"
        elif avg_improvement < 0.01:
            convergence_status = "converging"
        else:
            convergence_status = "improving"

        return {
            "iteration": self.iteration,
            "convergence_status": convergence_status,
            "current_f1": f1_scores[-1],
            "recent_improvement": recent_improvement,
            "average_improvement": avg_improvement,
            "total_reviewed": self.total_reviewed
        }


class ActiveLearningOptimizer:
    """Optimizes active learning strategy parameters"""

    @staticmethod
    def calculate_optimal_batch_size(total_documents: int,
                                    confidence_threshold: float = 0.90) -> int:
        """
        Calculate optimal batch size for active learning

        Args:
            total_documents: Total documents to review
            confidence_threshold: Desired confidence level

        Returns:
            Recommended batch size
        """
        # Batch size scales with sqrt of total documents
        # Typical range: 50-500 documents per iteration
        base_batch = int(np.sqrt(total_documents))
        return min(500, max(50, base_batch))

    @staticmethod
    def estimate_review_cost(total_documents: int,
                            initial_sample: int = 500,
                            cost_per_doc: float = 5.0) -> Dict:
        """
        Estimate total review cost using CAL

        Args:
            total_documents: Total document universe
            initial_sample: Initial training set size
            cost_per_doc: Cost per document review

        Returns:
            Cost estimation
        """
        # Typical CAL reaches 95% certainty with 20-30% review
        estimated_review_rate = 0.25  # 25% of documents

        total_to_review = initial_sample + int(total_documents * estimated_review_rate)
        total_cost = total_to_review * cost_per_doc

        return {
            "total_documents": total_documents,
            "estimated_review_count": total_to_review,
            "estimated_review_rate": estimated_review_rate,
            "total_cost": total_cost,
            "cost_savings_vs_manual": (total_documents - total_to_review) * cost_per_doc
        }

    @staticmethod
    def compare_strategies(total_docs: int,
                          cost_per_doc: float = 5.0) -> Dict:
        """
        Compare cost of different review strategies

        Args:
            total_docs: Total documents
            cost_per_doc: Cost per document

        Returns:
            Comparison of strategies
        """
        manual_cost = total_docs * cost_per_doc

        # TAR: ~70% auto-coded with 5% error rate
        tar_auto_coded = int(total_docs * 0.70)
        tar_review = total_docs - tar_auto_coded
        tar_cost = tar_review * cost_per_doc + (tar_auto_coded * 0.05 * 50)

        # CAL: ~25% manual review, better accuracy
        cal_review = int(total_docs * 0.25)
        cal_cost = cal_review * cost_per_doc + (total_docs * 0.02 * 50)  # 2% error rate

        return {
            "manual_review": {
                "documents_reviewed": total_docs,
                "total_cost": manual_cost
            },
            "tar": {
                "auto_coded": tar_auto_coded,
                "documents_reviewed": tar_review,
                "total_cost": tar_cost,
                "savings": manual_cost - tar_cost
            },
            "cal": {
                "documents_reviewed": cal_review,
                "total_cost": cal_cost,
                "savings": manual_cost - cal_cost
            }
        }


# Example usage
if __name__ == "__main__":
    from tar_model_training import TARModelTrainer

    # Initialize CAL strategy
    trainer = TARModelTrainer("cal_model")

    # Initial training on sample
    initial_training = [
        {"id": i, "text": "Contract text sample", "responsive": True}
        for i in range(1, 251)
    ] + [
        {"id": i, "text": "Email about meetings", "responsive": False}
        for i in range(251, 501)
    ]

    trainer.train_initial_model(initial_training)

    # CAL iterations
    cal = CALStrategy(trainer)

    # Simulate additional documents
    unlabeled = [
        {"id": i, "text": f"Document {i} with various content", "responsive": False}
        for i in range(501, 5001)
    ]

    # Select next batch using active learning
    batch = cal.select_next_batch(unlabeled, batch_size=100)
    print(f"Selected {len(batch)} documents for review")
    print(f"Top uncertainty: {batch[0]['uncertainty']:.3f}")

    # Cost estimation
    optimizer = ActiveLearningOptimizer()
    cost_est = optimizer.estimate_review_cost(5000)
    print(f"\nEstimated Review Cost: ${cost_est['total_cost']:,.0f}")
    print(f"Savings vs Manual: ${cost_est['cost_savings_vs_manual']:,.0f}")
