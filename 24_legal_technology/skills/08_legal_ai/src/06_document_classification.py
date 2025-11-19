"""
Legal Document Classification
Classify legal documents by type: contracts, memos, pleadings, etc.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib

class LegalDocumentClassifier:
    """Classify legal documents"""

    def __init__(self):
        self.categories = [
            "contract",
            "legal_memo",
            "pleading",
            "discovery_request",
            "motion",
            "brief",
            "opinion_letter",
            "settlement_agreement"
        ]

        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB())
        ])

    def train(self, documents, labels):
        """Train classifier"""

        X_train, X_test, y_train, y_test = train_test_split(
            documents, labels, test_size=0.2, random_state=42
        )

        self.pipeline.fit(X_train, y_train)

        accuracy = self.pipeline.score(X_test, y_test)
        return {"accuracy": accuracy}

    def classify(self, document_text):
        """Classify a legal document"""

        prediction = self.pipeline.predict([document_text])[0]
        probabilities = self.pipeline.predict_proba([document_text])[0]

        return {
            "predicted_type": self.categories[prediction],
            "confidence": probabilities[prediction],
            "all_probabilities": dict(zip(self.categories, probabilities))
        }
