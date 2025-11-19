"""
LegalBERT Fine-tuning for Contract Clause Classification

This example demonstrates how to fine-tune LegalBERT for classifying
contract clauses into categories like indemnification, liability, termination, etc.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd
import numpy as np

# Configuration
MODEL_NAME = "nlpaueb/legal-bert-base-uncased"
MAX_LENGTH = 512
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
NUM_EPOCHS = 5

# Clause categories
CLAUSE_LABELS = [
    "confidentiality",
    "indemnification",
    "limitation_of_liability",
    "termination",
    "payment_terms",
    "intellectual_property",
    "warranties",
    "dispute_resolution",
    "governing_law",
    "assignment"
]

class ContractClauseDataset(Dataset):
    """Dataset for contract clause classification"""

    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def prepare_data():
    """Prepare training data from contract clauses"""

    # Sample data (in practice, load from your annotated dataset)
    data = {
        "text": [
            "The Disclosing Party agrees to keep all Confidential Information strictly confidential.",
            "Supplier shall indemnify and hold harmless Client from any third-party claims.",
            "In no event shall either party's liability exceed the fees paid under this Agreement.",
            "Either party may terminate this Agreement upon 30 days written notice.",
            "Client shall pay Supplier within 30 days of invoice date.",
            "All intellectual property rights shall remain with the creating party.",
            "Supplier warrants that the services will be performed in a professional manner.",
            "Any disputes shall be resolved through binding arbitration.",
            "This Agreement shall be governed by the laws of Delaware.",
            "Neither party may assign this Agreement without prior written consent."
        ],
        "label": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # Indices into CLAUSE_LABELS
    }

    df = pd.DataFrame(data)

    # Split into train/val/test
    train_df = df.sample(frac=0.8, random_state=42)
    temp_df = df.drop(train_df.index)
    val_df = temp_df.sample(frac=0.5, random_state=42)
    test_df = temp_df.drop(val_df.index)

    return train_df, val_df, test_df

def compute_metrics(pred):
    """Compute evaluation metrics"""

    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted'
    )
    acc = accuracy_score(labels, preds)

    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def main():
    """Main training function"""

    print("Loading LegalBERT tokenizer and model...")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(CLAUSE_LABELS)
    )

    print(f"Model loaded with {len(CLAUSE_LABELS)} output labels")

    # Prepare data
    print("Preparing data...")
    train_df, val_df, test_df = prepare_data()

    # Create datasets
    train_dataset = ContractClauseDataset(
        train_df['text'].tolist(),
        train_df['label'].tolist(),
        tokenizer,
        MAX_LENGTH
    )

    val_dataset = ContractClauseDataset(
        val_df['text'].tolist(),
        val_df['label'].tolist(),
        tokenizer,
        MAX_LENGTH
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        learning_rate=LEARNING_RATE
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Evaluate
    print("\nEvaluating on test set...")
    test_dataset = ContractClauseDataset(
        test_df['text'].tolist(),
        test_df['label'].tolist(),
        tokenizer,
        MAX_LENGTH
    )

    test_results = trainer.evaluate(test_dataset)
    print("\nTest Results:")
    for metric, value in test_results.items():
        print(f"  {metric}: {value:.4f}")

    # Save model
    print("\nSaving model...")
    model.save_pretrained('./legal_clause_classifier')
    tokenizer.save_pretrained('./legal_clause_classifier')
    print("Model saved to ./legal_clause_classifier")

    # Example inference
    print("\n" + "="*50)
    print("Example Inference:")
    print("="*50)

    test_clauses = [
        "The parties agree to keep all information confidential.",
        "Liability shall be limited to direct damages only."
    ]

    for clause in test_clauses:
        inputs = tokenizer(
            clause,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LENGTH,
            padding='max_length'
        )

        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.softmax(outputs.logits, dim=1)
            predicted_class = predictions.argmax().item()
            confidence = predictions[0][predicted_class].item()

        print(f"\nClause: {clause}")
        print(f"Predicted Type: {CLAUSE_LABELS[predicted_class]}")
        print(f"Confidence: {confidence:.2%}")

if __name__ == "__main__":
    main()
