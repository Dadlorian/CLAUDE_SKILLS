# Legal Entity Extraction Guide

## Entities to Extract

### Core Entities
- **PARTY**: Contract parties, litigants
- **DATE**: Effective dates, deadlines, filing dates
- **MONEY**: Damages, fees, payments
- **JURISDICTION**: Governing law, venue
- **CITATION**: Legal citations (cases, statutes)
- **TERM**: Contract duration
- **PERCENTAGE**: Interest rates, equity stakes

### Advanced Entities
- **OBLIGATION**: Contractual duties
- **RIGHT**: Legal rights granted
- **CONDITION**: Triggering events
- **DEFINITION**: Defined terms

## Techniques

### 1. Pattern Matching
```python
import re

citation_patterns = {
    "us_supreme": r'\d+ U\.S\. \d+',
    "federal": r'\d+ F\.\d+d? \d+'
}

def extract_citations(text):
    citations = []
    for pattern_type, pattern in citation_patterns.items():
        matches = re.findall(pattern, text)
        citations.extend([(m, pattern_type) for m in matches])
    return citations
```

### 2. spaCy NER
Train custom NER model on legal entities:
```python
import spacy
from spacy.training import Example

nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")
ner.add_label("PARTY")
ner.add_label("CITATION")
# Train on annotated data
```

### 3. Transformer-Based
Use Legal-RoBERTa fine-tuned for NER:
```python
from transformers import pipeline

ner = pipeline("ner", model="legal-roberta-ner")
entities = ner(legal_text)
```

## Validation
- Precision: 90%+ for critical entities (dates, amounts)
- Recall: 85%+ (better to overextract than miss)
- Manual review of extractions on sample
