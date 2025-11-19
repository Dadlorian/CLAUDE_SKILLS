"""
Credit Scoring Model Implementation

Implements logistic regression-based credit scoring for loan evaluation.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class CreditScorer:
    """Credit scoring model using logistic regression."""

    def __init__(self, model_coefficients=None):
        """Initialize scorer with optional coefficients."""
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.coefficients = model_coefficients

    def train(self, X_train, y_train):
        """
        Train credit scoring model.

        Args:
            X_train: Feature matrix (shape: n_samples x n_features)
            y_train: Target binary (0=non-default, 1=default)
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)

        # Train logistic regression
        self.model.fit(X_scaled, y_train)
        self.coefficients = self.model.coef_[0]

    def predict_probability(self, features_df):
        """
        Predict probability of default.

        Args:
            features_df: DataFrame with features [income, assets, debt_ratio,
                        payment_history, collateral, credit_score]

        Returns:
            Array of PD probabilities (0-1)
        """
        X_scaled = self.scaler.transform(features_df)
        return self.model.predict_proba(X_scaled)[:, 1]

    def score(self, features_df):
        """
        Generate credit score (0-1000 scale).

        Args:
            features_df: DataFrame with features

        Returns:
            Array of scores (0-1000)
        """
        pd_probs = self.predict_probability(features_df)
        # Scale 0-1 probability to 0-1000 score
        scores = (1 - pd_probs) * 1000
        return scores

    def rate_assignment(self, scores):
        """
        Assign credit rating based on score.

        Args:
            scores: Array of credit scores

        Returns:
            Array of ratings (AAA, AA, A, BBB, BB, B, CCC)
        """
        ratings = []
        for score in scores:
            if score >= 800:
                ratings.append('AAA')
            elif score >= 700:
                ratings.append('AA')
            elif score >= 650:
                ratings.append('A')
            elif score >= 600:
                ratings.append('BBB')
            elif score >= 550:
                ratings.append('BB')
            elif score >= 500:
                ratings.append('B')
            else:
                ratings.append('CCC')
        return np.array(ratings)

    def decision(self, scores, ratings):
        """
        Generate lending decision.

        Args:
            scores: Array of credit scores
            ratings: Array of credit ratings

        Returns:
            Array of decisions (Approve, Review, Decline)
        """
        decisions = []
        for rating in ratings:
            if rating in ['AAA', 'AA', 'A']:
                decisions.append('Approve')
            elif rating in ['BBB']:
                decisions.append('Review')
            else:
                decisions.append('Decline')
        return np.array(decisions)


# Example usage
if __name__ == "__main__":
    # Sample data
    data = {
        'income': [60000, 75000, 50000, 90000, 40000],
        'assets': [50000, 100000, 30000, 150000, 20000],
        'debt_ratio': [0.35, 0.25, 0.45, 0.20, 0.60],
        'payment_history': [8, 9, 6, 9, 4],
        'collateral': [80000, 120000, 40000, 180000, 25000],
        'credit_score': [750, 800, 650, 820, 550],
        'default': [0, 0, 1, 0, 1]
    }

    df = pd.DataFrame(data)
    X = df[['income', 'assets', 'debt_ratio', 'payment_history', 'collateral', 'credit_score']]
    y = df['default']

    # Train model
    scorer = CreditScorer()
    scorer.train(X, y)

    # Score new applicant
    applicant = pd.DataFrame({
        'income': [65000],
        'assets': [60000],
        'debt_ratio': [0.40],
        'payment_history': [7],
        'collateral': [75000],
        'credit_score': [720]
    })

    pd_prob = scorer.predict_probability(applicant)[0]
    score = scorer.score(applicant)[0]
    rating = scorer.rate_assignment(np.array([score]))[0]
    decision = scorer.decision(np.array([score]), np.array([rating]))[0]

    print(f"Applicant PD: {pd_prob:.2%}")
    print(f"Credit Score: {score:.0f}")
    print(f"Rating: {rating}")
    print(f"Decision: {decision}")
