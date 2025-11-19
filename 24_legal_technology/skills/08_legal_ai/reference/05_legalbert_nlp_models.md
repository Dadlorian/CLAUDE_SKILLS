# Legal NLP Models: LegalBERT and Variants

## Overview
Legal NLP models are transformer-based language models specifically fine-tuned or pre-trained on legal corpora to understand legal language, concepts, and reasoning. These models significantly outperform general-purpose models on legal tasks due to domain-specific training.

## LegalBERT Family

### 1. LegalBERT (Original)
**Source**: Chalkidis et al., 2020
**Training Data**: 12GB of legal text from various sources
**Base Model**: BERT-base architecture (110M parameters)

```python
# LegalBERT Model Card
model_info = {
    "name": "nlpaueb/legal-bert-base-uncased",
    "architecture": "BERT-base",
    "parameters": "110M",
    "vocabulary": "30,522 WordPiece tokens",
    "training_data": {
        "sources": [
            "EU legislation (EUR-Lex)",
            "UK legislation (legislation.gov.uk)",
            "US court decisions (Case Law Access Project)",
            "US contracts (EDGAR)",
            "European Court of Human Rights cases"
        ],
        "size": "12GB raw text",
        "documents": "~1M legal documents",
        "tokens": "~3.5B tokens"
    },
    "training": {
        "objective": "Masked Language Modeling (MLM)",
        "steps": "1M steps",
        "hardware": "8x V100 GPUs",
        "duration": "~10 days"
    }
}
```

**Usage Example**:
```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load LegalBERT
tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
model = AutoModel.from_pretrained("nlpaueb/legal-bert-base-uncased")

# Encode legal text
text = """
The defendant hereby indemnifies and holds harmless the plaintiff
from any and all claims arising out of the breach of this agreement.
"""

inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
outputs = model(**inputs)

# Get contextual embeddings
embeddings = outputs.last_hidden_state
# Shape: [batch_size, sequence_length, hidden_size=768]
```

### 2. LegalBERT Variants

#### Legal-BERT-BASE
**Source**: Chalkidis et al., Findings of EMNLP 2020
**Hugging Face**: `nlpaueb/legal-bert-base-uncased`

#### Legal-BERT-SMALL
**Source**: Smaller, faster version
**Hugging Face**: `nlpaueb/legal-bert-small-uncased`
**Parameters**: 33M (1/3 size of base)

#### Legal-BERT-FP (Further Pre-trained)
Additional pre-training on specific legal domains:
```python
specialized_models = {
    "contracts": "nlpaueb/legal-bert-base-uncased-contracts",
    "case_law": "nlpaueb/legal-bert-base-uncased-caselaw",
    "legislation": "nlpaueb/legal-bert-base-uncased-legislation"
}
```

### 3. CaseLaw-BERT
**Purpose**: Specialized for judicial opinions and case law
**Training Data**: Case Law Access Project (6.4M US court cases)

```python
# CaseLaw-BERT Usage
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "pile-of-law/legalbert-large-1.7M-2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=6  # e.g., for case outcome prediction
)

# Fine-tune for case outcome prediction
case_text = """
SUPREME COURT OF THE UNITED STATES
No. 21-1333
ISSUE: Whether the First Amendment prohibits...
HOLDING: The Court holds that...
"""

inputs = tokenizer(case_text, return_tensors="pt", max_length=512, truncation=True)
outputs = model(**inputs)
logits = outputs.logits
prediction = torch.argmax(logits, dim=1)
```

### 4. EU-Specific Legal Models

#### MultiLegalPile
**Source**: Multi-jurisdictional legal corpus
**Coverage**: 24 EU languages + English legal text
**Size**: 689GB of legal documents

#### EUR-LegalBERT
**Purpose**: EU law and multilingual legal understanding
**Languages**: All 24 official EU languages

```python
# EU-LegalBERT for multilingual legal NER
from transformers import pipeline

ner_pipeline = pipeline(
    "ner",
    model="joelito/legal-xlm-roberta-base",
    tokenizer="joelito/legal-xlm-roberta-base"
)

# Works on multiple languages
texts = [
    "The European Commission filed suit against France.",  # English
    "La Commission européenne a intenté une action contre la France.",  # French
    "Die Europäische Kommission reichte Klage gegen Frankreich ein."  # German
]

for text in texts:
    entities = ner_pipeline(text)
    print(entities)
```

### 5. Domain-Specific Legal Models

#### InCaseLaw BERT
**Source**: Legal case outcome prediction
**Hugging Face**: Various fine-tuned versions

```python
# Case outcome prediction
model = AutoModelForSequenceClassification.from_pretrained(
    "legal-outcome-predictor",
    num_labels=2  # affirm/reverse
)

# Predict whether appellate court will affirm or reverse
case_facts = "Defendant appealed on grounds of insufficient evidence..."
inputs = tokenizer(case_facts, return_tensors="pt")
prediction = model(**inputs).logits.argmax().item()
outcome = ["Affirm", "Reverse"][prediction]
```

#### LegalRoBERTa
**Base**: RoBERTa architecture (improved BERT training)
**Advantage**: Better performance on legal reasoning tasks

```python
# Legal-RoBERTa for legal question answering
from transformers import RobertaForQuestionAnswering

model = RobertaForQuestionAnswering.from_pretrained(
    "joelito/legal-roberta-base"
)

context = """
Under Delaware law, a contract is voidable if entered under duress.
Duress requires proof of wrongful threat that leaves no reasonable alternative.
"""

question = "What is required to prove duress in Delaware?"

inputs = tokenizer(question, context, return_tensors="pt")
outputs = model(**inputs)

answer_start = torch.argmax(outputs.start_logits)
answer_end = torch.argmax(outputs.end_logits) + 1
answer = tokenizer.decode(inputs.input_ids[0][answer_start:answer_end])
# Output: "proof of wrongful threat that leaves no reasonable alternative"
```

## Legal NLP Tasks and Models

### 1. Named Entity Recognition (NER)
Extract legal entities from text:

```python
from transformers import pipeline

# Legal NER pipeline
ner = pipeline(
    "ner",
    model="joelito/legal-english-roberta-base",
    tokenizer="joelito/legal-english-roberta-base",
    aggregation_strategy="simple"
)

legal_text = """
In Smith v. Jones, 123 F.3d 456 (9th Cir. 2020), the court held
that the defendant violated 17 U.S.C. § 106 by distributing
copyrighted materials. The plaintiff sought $500,000 in damages.
"""

entities = ner(legal_text)
# Output:
# [
#   {"entity_group": "CASE", "word": "Smith v. Jones"},
#   {"entity_group": "CITATION", "word": "123 F.3d 456 (9th Cir. 2020)"},
#   {"entity_group": "STATUTE", "word": "17 U.S.C. § 106"},
#   {"entity_group": "MONEY", "word": "$500,000"}
# ]
```

### 2. Contract Clause Classification

```python
# Fine-tune LegalBERT for clause classification
from transformers import TrainingArguments, Trainer

# Contract clause types
clause_labels = [
    "confidentiality",
    "indemnification",
    "limitation_of_liability",
    "termination",
    "governing_law",
    "assignment",
    "warranty",
    "payment_terms"
]

# Prepare dataset
from datasets import load_dataset
dataset = load_dataset("contract_clauses")

# Model setup
model = AutoModelForSequenceClassification.from_pretrained(
    "nlpaueb/legal-bert-base-uncased",
    num_labels=len(clause_labels)
)

# Training arguments
training_args = TrainingArguments(
    output_dir="./legal-clause-classifier",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs"
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"]
)

trainer.train()

# Inference
def classify_clause(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    prediction = clause_labels[outputs.logits.argmax().item()]
    confidence = torch.softmax(outputs.logits, dim=1).max().item()
    return prediction, confidence

clause = "The Company shall indemnify and hold harmless the Supplier..."
label, conf = classify_clause(clause)
print(f"Clause Type: {label} (confidence: {conf:.2%})")
```

### 3. Legal Document Summarization

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Legal summarization model
model_name = "nsi319/legal-pegasus"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Summarize legal document
legal_doc = """
[Long contract or case opinion text...]
"""

inputs = tokenizer(
    legal_doc,
    max_length=1024,
    truncation=True,
    return_tensors="pt"
)

summary_ids = model.generate(
    inputs.input_ids,
    max_length=150,
    min_length=50,
    num_beams=4,
    length_penalty=2.0,
    early_stopping=True
)

summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
```

### 4. Legal Question Answering

```python
# Legal QA system using LegalBERT
from transformers import pipeline

qa_pipeline = pipeline(
    "question-answering",
    model="law-ai/InLegalBERT",
    tokenizer="law-ai/InLegalBERT"
)

context = """
Under the Uniform Commercial Code Section 2-207, additional terms in
an acceptance become part of the contract unless: (1) the offer expressly
limits acceptance to the terms of the offer; (2) the additional terms
materially alter the contract; or (3) notification of objection has been given.
"""

questions = [
    "When do additional terms become part of a contract?",
    "What is the UCC rule on additional terms?",
    "Under what conditions are additional terms excluded?"
]

for question in questions:
    result = qa_pipeline(question=question, context=context)
    print(f"Q: {question}")
    print(f"A: {result['answer']} (score: {result['score']:.2f})\n")
```

### 5. Legal Judgment Prediction

```python
# Predict case outcomes using fine-tuned LegalBERT
class LegalJudgmentPredictor:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.label_map = {
            0: "Plaintiff Victory",
            1: "Defendant Victory",
            2: "Partial Victory",
            3: "Dismissed"
        }

    def predict(self, case_facts):
        inputs = self.tokenizer(
            case_facts,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)[0]
            prediction = torch.argmax(probabilities).item()

        return {
            "outcome": self.label_map[prediction],
            "confidence": probabilities[prediction].item(),
            "all_probabilities": {
                self.label_map[i]: prob.item()
                for i, prob in enumerate(probabilities)
            }
        }

# Usage
predictor = LegalJudgmentPredictor("legal-judgment-model")
case = "Plaintiff alleges breach of contract for failure to deliver goods..."
result = predictor.predict(case)
print(f"Predicted Outcome: {result['outcome']} ({result['confidence']:.2%})")
```

## Advanced Legal NLP Architectures

### 1. Long Document Models
Legal documents often exceed standard BERT limits (512 tokens):

```python
# Longformer for legal documents
from transformers import LongformerModel, LongformerTokenizer

# Can handle up to 4,096 tokens
model = LongformerModel.from_pretrained("allenai/longformer-base-4096")
tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")

# Fine-tune on legal data
long_contract = """[10,000+ word contract text]"""

inputs = tokenizer(
    long_contract,
    return_tensors="pt",
    max_length=4096,
    truncation=True
)

outputs = model(**inputs)
```

### 2. Hierarchical Models
Process documents in sections:

```python
class HierarchicalLegalBERT:
    """Process legal documents section by section"""

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.encoder = AutoModel.from_pretrained("nlpaueb/legal-bert-base-uncased")

    def encode_document(self, sections):
        """Encode each section, then aggregate"""
        section_embeddings = []

        for section in sections:
            inputs = self.tokenizer(
                section,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            outputs = self.encoder(**inputs)
            # Use [CLS] token embedding
            section_emb = outputs.last_hidden_state[:, 0, :]
            section_embeddings.append(section_emb)

        # Aggregate section embeddings (e.g., mean pooling)
        doc_embedding = torch.stack(section_embeddings).mean(dim=0)
        return doc_embedding

# Usage
contract_sections = [
    "1. DEFINITIONS\nFor purposes of this Agreement...",
    "2. SCOPE OF WORK\nThe Contractor shall provide...",
    "3. PAYMENT TERMS\nClient agrees to pay..."
]

model = HierarchicalLegalBERT()
doc_emb = model.encode_document(contract_sections)
```

### 3. Multi-task Learning
Train on multiple legal tasks simultaneously:

```python
class MultiTaskLegalBERT(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert = AutoModel.from_pretrained("nlpaueb/legal-bert-base-uncased")

        # Task-specific heads
        self.clause_classifier = nn.Linear(768, 10)  # 10 clause types
        self.ner_tagger = nn.Linear(768, 20)  # 20 entity types
        self.outcome_predictor = nn.Linear(768, 4)  # 4 outcomes

    def forward(self, input_ids, attention_mask, task):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)

        if task == "clause_classification":
            return self.clause_classifier(outputs.last_hidden_state[:, 0, :])
        elif task == "ner":
            return self.ner_tagger(outputs.last_hidden_state)
        elif task == "outcome_prediction":
            return self.outcome_predictor(outputs.last_hidden_state[:, 0, :])
```

## Performance Benchmarks

### LegalBERT vs. General BERT

```python
benchmark_results = {
    "task": "Contract Clause Classification",
    "dataset": "LEDGAR (100K contract provisions)",
    "metrics": {
        "BERT-base": {
            "accuracy": 0.87,
            "f1_macro": 0.82
        },
        "LegalBERT": {
            "accuracy": 0.94,
            "f1_macro": 0.91
        },
        "improvement": "+7% accuracy, +9% F1"
    }
}

ner_benchmark = {
    "task": "Legal Named Entity Recognition",
    "dataset": "Legal NER (10K annotated cases)",
    "metrics": {
        "BERT-base": {
            "f1": 0.79
        },
        "LegalBERT": {
            "f1": 0.88
        },
        "Legal-RoBERTa": {
            "f1": 0.91
        },
        "improvement": "+12% F1 for Legal-RoBERTa"
    }
}
```

## Fine-tuning Best Practices

### 1. Data Preparation
```python
def prepare_legal_dataset(contracts, labels):
    """Prepare contracts for fine-tuning"""
    from datasets import Dataset

    data = {
        "text": [],
        "label": []
    }

    for contract, label in zip(contracts, labels):
        # Clean text
        cleaned = clean_legal_text(contract)

        # Truncate if too long (keep most important parts)
        if len(cleaned.split()) > 500:
            # Keep beginning (parties, definitions) and end (signatures)
            words = cleaned.split()
            cleaned = " ".join(words[:250] + words[-250:])

        data["text"].append(cleaned)
        data["label"].append(label)

    return Dataset.from_dict(data)

def clean_legal_text(text):
    """Clean legal text for better model performance"""
    import re

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Normalize citations
    text = re.sub(r'(\d+)\s+F\.\s+(\d+)', r'\1 F.\2', text)

    # Remove page numbers
    text = re.sub(r'Page \d+ of \d+', '', text)

    return text.strip()
```

### 2. Training Configuration
```python
from transformers import TrainingArguments

# Optimal settings for legal domain
training_args = TrainingArguments(
    output_dir="./legal-model",

    # Training dynamics
    num_train_epochs=5,  # Legal data often needs more epochs
    learning_rate=2e-5,  # Lower LR for stability
    warmup_ratio=0.1,    # Warm up first 10% of steps

    # Batch size (adjust based on GPU memory)
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,  # Effective batch size: 32

    # Optimization
    weight_decay=0.01,
    adam_epsilon=1e-8,
    max_grad_norm=1.0,

    # Regularization
    fp16=True,  # Mixed precision training

    # Evaluation
    evaluation_strategy="steps",
    eval_steps=500,
    save_steps=500,
    load_best_model_at_end=True,
    metric_for_best_model="f1",

    # Logging
    logging_steps=100,
    report_to="wandb"  # Track experiments
)
```

### 3. Domain Adaptation
```python
# Continue pre-training on your legal corpus
from transformers import DataCollatorForLanguageModeling

def continue_pretraining(model, legal_texts):
    """Continue pre-training LegalBERT on firm-specific documents"""

    # Prepare for MLM
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability=0.15
    )

    # Create dataset
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            return_special_tokens_mask=True
        )

    tokenized_dataset = legal_texts.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"]
    )

    # Continue pre-training
    training_args = TrainingArguments(
        output_dir="./firm-legal-bert",
        num_train_epochs=10,
        per_device_train_batch_size=16,
        save_steps=5000,
        save_total_limit=2
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator
    )

    trainer.train()
    return model
```

## Resources

### Pre-trained Models (Hugging Face)
```python
legal_models = {
    "general_legal": [
        "nlpaueb/legal-bert-base-uncased",
        "nlpaueb/legal-bert-small-uncased"
    ],
    "case_law": [
        "pile-of-law/legalbert-large-1.7M-2",
        "lexlms/legal-roberta-base"
    ],
    "contracts": [
        "nlpaueb/legal-bert-base-uncased-contracts",
        "contract-bert-base"
    ],
    "multilingual": [
        "joelito/legal-xlm-roberta-base",
        "joelito/legal-xlm-longformer-base"
    ]
}
```

### Datasets
- **LEDGAR**: 100K contract provisions labeled by type
- **CaseHOLD**: Legal holdings from case law
- **MultiLegalPile**: 689GB multi-jurisdictional corpus
- **CUAD**: Contract Understanding Atticus Dataset
- **LexGLUE**: Legal language understanding benchmark

### Academic Papers
1. "LegalBERT: The Muppets straight out of Law School" (Chalkidis et al., 2020)
2. "LEGAL-BERT: The Muppets straight out of Law School" (Chalkidis et al., 2020)
3. "When Does Pretraining Help? Assessing Self-Supervised Learning for Law and the CaseHOLD Dataset" (Zheng et al., 2021)
4. "LexGLUE: A Benchmark Dataset for Legal Language Understanding" (Chalkidis et al., 2022)

---

*Legal NLP models like LegalBERT represent a significant advancement in AI for legal applications, providing domain-specific understanding that dramatically improves performance on legal tasks compared to general-purpose models.*
