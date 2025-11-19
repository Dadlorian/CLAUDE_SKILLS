# Legal Document Classification Guide

## Overview
Classify legal documents by type using ML.

## Document Types
- Contracts (MSA, NDA, SOW, Purchase Orders)
- Legal Memos
- Pleadings (Complaints, Answers, Motions)
- Discovery (Interrogatories, Requests for Production)
- Briefs
- Opinion Letters
- Settlement Agreements

## Approach

### Feature Extraction
Use TF-IDF with legal-specific features:
- Section headings (e.g., "WHEREAS", "WITNESSETH")
- Legal boilerplate ("party of the first part")
- Citation patterns
- Signature blocks

### Model Selection
- Naive Bayes: Fast, good baseline (85% accuracy)
- SVM: Better performance (90% accuracy)
- LegalBERT: Best performance (95% accuracy)

### Training Data
- Minimum 100 examples per class
- Balanced across document types
- Diverse sources (different firms, jurisdictions)

## Implementation
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000)),
    ('classifier', MultinomialNB())
])

pipeline.fit(training_docs, labels)
prediction = pipeline.predict([new_doc])
```
