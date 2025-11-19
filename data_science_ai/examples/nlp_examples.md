# NLP Examples with HuggingFace Transformers

Production-ready examples for various NLP tasks using HuggingFace Transformers library.

## Table of Contents

1. [Text Classification with BERT](#text-classification-with-bert)
2. [Named Entity Recognition (NER)](#named-entity-recognition-ner)
3. [Question Answering System](#question-answering-system)
4. [Text Summarization](#text-summarization)
5. [Machine Translation](#machine-translation)
6. [Sentiment Analysis](#sentiment-analysis)
7. [Text Generation](#text-generation)
8. [Custom Tokenizer Training](#custom-tokenizer-training)

---

## Text Classification with BERT

### 1.1 Complete Training Pipeline

```python
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import numpy as np
import pandas as pd
from tqdm import tqdm
import json

class TextClassificationDataset(Dataset):
    """Custom dataset for text classification."""

    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.texts = texts
        self.labels = labels
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'token_type_ids': encoding['token_type_ids'].squeeze(0),
            'label': torch.tensor(label, dtype=torch.long)
        }

class BertClassifier:
    """BERT-based text classifier."""

    def __init__(self, model_name='bert-base-uncased', num_classes=2, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_classes)
        self.model.to(self.device)

    def prepare_data(self, texts, labels, test_size=0.2, batch_size=32, max_length=128):
        """Prepare data loaders for training."""
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42
        )

        train_dataset = TextClassificationDataset(X_train, y_train, self.tokenizer, max_length)
        test_dataset = TextClassificationDataset(X_test, y_test, self.tokenizer, max_length)

        self.train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        self.test_loader = DataLoader(test_dataset, batch_size=batch_size)

        return self.train_loader, self.test_loader

    def train(self, epochs=3, learning_rate=2e-5, warmup_steps=0):
        """Train the classifier."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(self.train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )

        training_stats = []

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')
            print('-' * 50)

            # Training phase
            self.model.train()
            total_train_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                token_type_ids = batch['token_type_ids'].to(self.device)
                labels = batch['label'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids,
                    labels=labels
                )

                loss = outputs.loss
                total_train_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                optimizer.step()
                scheduler.step()

            avg_train_loss = total_train_loss / len(self.train_loader)

            # Validation phase
            val_loss, val_accuracy, val_precision, val_recall, val_f1 = self.evaluate()

            training_stats.append({
                'epoch': epoch + 1,
                'train_loss': avg_train_loss,
                'val_loss': val_loss,
                'val_accuracy': val_accuracy,
                'val_precision': val_precision,
                'val_recall': val_recall,
                'val_f1': val_f1
            })

            print(f'Train Loss: {avg_train_loss:.4f}')
            print(f'Val Loss: {val_loss:.4f}, Val Accuracy: {val_accuracy:.4f}')
            print(f'Val F1: {val_f1:.4f}')

        return training_stats

    def evaluate(self):
        """Evaluate the classifier."""
        self.model.eval()
        total_eval_loss = 0
        predictions, true_labels = [], []

        with torch.no_grad():
            for batch in tqdm(self.test_loader, desc='Evaluating'):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                token_type_ids = batch['token_type_ids'].to(self.device)
                labels = batch['label'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids,
                    labels=labels
                )

                loss = outputs.loss
                total_eval_loss += loss.item()

                logits = outputs.logits
                predictions.extend(torch.argmax(logits, dim=1).cpu().numpy())
                true_labels.extend(labels.cpu().numpy())

        avg_eval_loss = total_eval_loss / len(self.test_loader)
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='weighted'
        )

        return avg_eval_loss, accuracy, precision, recall, f1

    def predict(self, texts):
        """Make predictions on new texts."""
        self.model.eval()
        predictions = []

        with torch.no_grad():
            for text in texts:
                encoding = self.tokenizer(
                    text,
                    max_length=128,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )

                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                token_type_ids = encoding['token_type_ids'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids
                )

                logits = outputs.logits
                prediction = torch.argmax(logits, dim=1).cpu().numpy()[0]
                confidence = torch.softmax(logits, dim=1).cpu().numpy()[0]

                predictions.append({
                    'text': text,
                    'predicted_label': int(prediction),
                    'confidence': float(confidence[prediction])
                })

        return predictions

    def save_model(self, save_path):
        """Save model and tokenizer."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        print(f'Model saved to {save_path}')

    @classmethod
    def load_model(cls, model_path, num_classes=2, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load model and tokenizer."""
        classifier = cls(device=device)
        classifier.model = BertForSequenceClassification.from_pretrained(model_path, num_labels=num_classes)
        classifier.tokenizer = BertTokenizer.from_pretrained(model_path)
        classifier.model.to(device)
        return classifier

# Usage Example
if __name__ == '__main__':
    # Sample data
    texts = [
        "This movie is absolutely fantastic!",
        "Terrible film, waste of time",
        "Best movie ever made",
        "Boring and predictable",
    ] * 50  # Repeat for more samples

    labels = [1, 0, 1, 0] * 50  # 1 = positive, 0 = negative

    # Initialize classifier
    classifier = BertClassifier(num_classes=2)

    # Prepare data
    classifier.prepare_data(texts, labels, batch_size=16)

    # Train model
    training_stats = classifier.train(epochs=3, learning_rate=2e-5)

    # Make predictions
    new_texts = [
        "This is an amazing movie!",
        "I hated this film"
    ]
    predictions = classifier.predict(new_texts)

    for pred in predictions:
        print(f"Text: {pred['text']}")
        print(f"Label: {pred['predicted_label']}, Confidence: {pred['confidence']:.4f}\n")

    # Save model
    classifier.save_model('./bert_classifier')
```

### 1.2 Production Deployment with FastAPI

```python
from fastapi import FastAPI, BaseModel
from transformers import BertTokenizer, BertForSequenceClassification
import torch

app = FastAPI()

class TextInput(BaseModel):
    text: str

class PredictionOutput(BaseModel):
    text: str
    label: int
    confidence: float

# Load model and tokenizer
device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = BertTokenizer.from_pretrained('./bert_classifier')
model = BertForSequenceClassification.from_pretrained('./bert_classifier')
model.to(device)
model.eval()

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: TextInput):
    text = input_data.text

    encoding = tokenizer(
        text,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )

    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).cpu().numpy()[0]
        confidence = torch.softmax(logits, dim=1).cpu().numpy()[0]

    return PredictionOutput(
        text=text,
        label=int(prediction),
        confidence=float(confidence[prediction])
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

---

## Named Entity Recognition (NER)

### 2.1 Complete NER Pipeline

```python
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForTokenClassification, AdamW, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from seqeval.metrics import classification_report, f1_score
import numpy as np
from tqdm import tqdm

class NERDataset(Dataset):
    """Dataset for Named Entity Recognition."""

    def __init__(self, texts, tags, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.texts = texts
        self.tags = tags
        self.max_length = max_length
        self.tag2id = {tag: idx for idx, tag in enumerate(set(tag for tags_list in tags for tag in tags_list))}
        self.id2tag = {idx: tag for tag, idx in self.tag2id.items()}

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        tags = self.tags[idx]

        # Tokenize with word_ids tracking
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
            is_split_into_words=True
        )

        # Align labels with tokens
        labels = [-100] * len(encoding['input_ids'][0])  # -100 is ignored in loss calculation
        word_ids = encoding.word_ids(batch_index=0)

        previous_word_idx = None
        for word_idx, tag in zip(word_ids, tags):
            if word_idx is None:
                continue
            if word_idx != previous_word_idx:
                labels[word_idx] = self.tag2id.get(tag, 0)
            previous_word_idx = word_idx

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(labels, dtype=torch.long)
        }

class NERModel:
    """Named Entity Recognition model."""

    def __init__(self, model_name='bert-base-cased', num_labels=7, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=num_labels)
        self.model.to(device)
        self.num_labels = num_labels

    def prepare_data(self, texts, tags, test_size=0.2, batch_size=16, max_length=512):
        """Prepare data loaders."""
        X_train, X_test, y_train, y_test = train_test_split(
            texts, tags, test_size=test_size, random_state=42
        )

        train_dataset = NERDataset(X_train, y_train, self.tokenizer, max_length)
        test_dataset = NERDataset(X_test, y_test, self.tokenizer, max_length)

        self.tag2id = train_dataset.tag2id
        self.id2tag = train_dataset.id2tag

        self.train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        self.test_loader = DataLoader(test_dataset, batch_size=batch_size)

        return self.train_loader, self.test_loader

    def train(self, epochs=3, learning_rate=5e-5):
        """Train the NER model."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(self.train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')
            print('-' * 50)

            # Training phase
            self.model.train()
            total_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                optimizer.step()
                scheduler.step()

            avg_train_loss = total_loss / len(self.train_loader)

            # Evaluation
            val_loss, val_f1 = self.evaluate()

            print(f'Train Loss: {avg_train_loss:.4f}')
            print(f'Val Loss: {val_loss:.4f}, Val F1: {val_f1:.4f}')

    def evaluate(self):
        """Evaluate the model."""
        self.model.eval()
        total_loss = 0
        predictions_all = []
        labels_all = []

        with torch.no_grad():
            for batch in tqdm(self.test_loader, desc='Evaluating'):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                predictions = torch.argmax(outputs.logits, dim=2)
                predictions_all.append(predictions)
                labels_all.append(labels)

        avg_loss = total_loss / len(self.test_loader)

        # Calculate F1 score
        f1 = f1_score(labels_all, predictions_all)

        return avg_loss, f1

    def predict(self, text):
        """Make predictions on new text."""
        self.model.eval()

        encoding = self.tokenizer(
            text.split(),
            truncation=True,
            is_split_into_words=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        predictions = torch.argmax(outputs.logits, dim=2)
        predicted_tokens = predictions[0].cpu().numpy()

        # Get word tokens
        word_ids = encoding.word_ids()
        entities = []

        for word_idx, token_idx in enumerate(word_ids):
            if token_idx is not None:
                tag = self.id2tag[predicted_tokens[token_idx]]
                if tag != 'O':
                    entities.append({
                        'word': text.split()[word_idx],
                        'tag': tag
                    })

        return entities

    def save_model(self, save_path):
        """Save model and tokenizer."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    @classmethod
    def load_model(cls, model_path, num_labels=7, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load saved model."""
        ner_model = cls(device=device)
        ner_model.model = AutoModelForTokenClassification.from_pretrained(model_path, num_labels=num_labels)
        ner_model.tokenizer = AutoTokenizer.from_pretrained(model_path)
        ner_model.model.to(device)
        return ner_model

# Usage Example
if __name__ == '__main__':
    texts = [
        "John Smith works at Google in Mountain View",
        "Apple Inc. is located in Cupertino",
    ] * 20

    tags = [
        ['B-PER', 'I-PER', 'O', 'O', 'B-ORG', 'O', 'B-LOC', 'I-LOC'],
        ['B-ORG', 'I-ORG', 'O', 'O', 'O', 'B-LOC'],
    ] * 20

    ner_model = NERModel(num_labels=7)
    ner_model.prepare_data(texts, tags)
    ner_model.train(epochs=3)

    # Make prediction
    entities = ner_model.predict("Barack Hussein Obama was born in Hawaii")
    print("Entities:", entities)

    ner_model.save_model('./ner_model')
```

---

## Question Answering System

### 3.1 Complete QA Pipeline

```python
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, AdamW
from sklearn.metrics import exact_match_score, f1_score
import json
from tqdm import tqdm

class QADataset(Dataset):
    """Dataset for Question Answering."""

    def __init__(self, contexts, questions, answers, tokenizer, max_length=384, stride=128):
        self.tokenizer = tokenizer
        self.contexts = contexts
        self.questions = questions
        self.answers = answers
        self.max_length = max_length
        self.stride = stride

    def __len__(self):
        return len(self.contexts)

    def __getitem__(self, idx):
        context = self.contexts[idx]
        question = self.questions[idx]
        answer = self.answers[idx]

        # Tokenize
        encoding = self.tokenizer(
            question,
            context,
            max_length=self.max_length,
            stride=self.stride,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding='max_length',
            truncation='only_second',
            return_tensors='pt'
        )

        # Find answer span
        answer_start = context.find(answer['text'])
        if answer_start == -1:
            answer_start_token = 0
            answer_end_token = 0
        else:
            answer_end = answer_start + len(answer['text'])

            # Convert character positions to token positions
            offset_mapping = encoding['offset_mapping'][0]
            answer_start_token = None
            answer_end_token = None

            for i, (start, end) in enumerate(offset_mapping):
                if start <= answer_start < end:
                    answer_start_token = i
                if start < answer_end <= end:
                    answer_end_token = i
                    break

            if answer_start_token is None or answer_end_token is None:
                answer_start_token = 0
                answer_end_token = 0

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'start_positions': torch.tensor(answer_start_token, dtype=torch.long),
            'end_positions': torch.tensor(answer_end_token, dtype=torch.long)
        }

class QAModel:
    """Question Answering model."""

    def __init__(self, model_name='bert-base-uncased', device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        self.model.to(device)

    def prepare_data(self, contexts, questions, answers, batch_size=16):
        """Prepare data loaders."""
        dataset = QADataset(contexts, questions, answers, self.tokenizer)
        self.train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        return self.train_loader

    def train(self, epochs=3, learning_rate=3e-5):
        """Train the QA model."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')

            self.model.train()
            total_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                start_positions = batch['start_positions'].to(self.device)
                end_positions = batch['end_positions'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    start_positions=start_positions,
                    end_positions=end_positions
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

            print(f'Epoch {epoch + 1} Loss: {total_loss / len(self.train_loader):.4f}')

    def predict(self, context, question, top_k=3):
        """Make predictions."""
        self.model.eval()

        encoding = self.tokenizer(
            question,
            context,
            max_length=384,
            truncation='only_second',
            return_tensors='pt',
            padding='max_length'
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        start_scores = outputs.start_logits[0]
        end_scores = outputs.end_logits[0]

        # Get top-k predictions
        predictions = []
        start_indices = torch.argsort(start_scores, descending=True)[:top_k]

        for start_idx in start_indices:
            end_indices = torch.argsort(end_scores[start_idx:], descending=True)[:top_k]

            for end_idx_offset in end_indices:
                end_idx = start_idx + end_idx_offset

                if end_idx < start_idx:
                    continue

                tokens = encoding.tokens()
                answer_tokens = tokens[start_idx:end_idx+1]
                answer_text = self.tokenizer.decode(
                    self.tokenizer.convert_tokens_to_ids(answer_tokens)
                )

                score = (start_scores[start_idx] + end_scores[end_idx]).item() / 2

                predictions.append({
                    'answer': answer_text.strip(),
                    'score': float(score)
                })

        return sorted(predictions, key=lambda x: x['score'], reverse=True)[:top_k]

    def save_model(self, save_path):
        """Save model."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    @classmethod
    def load_model(cls, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load model."""
        qa_model = cls(device=device)
        qa_model.model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        qa_model.tokenizer = AutoTokenizer.from_pretrained(model_path)
        qa_model.model.to(device)
        return qa_model

# Usage Example
if __name__ == '__main__':
    contexts = [
        "The Great Wall of China is a series of fortifications made of stone, brick, tamped earth, and wood.",
        "Python is a high-level programming language.",
    ] * 10

    questions = [
        "What is the Great Wall of China made of?",
        "What type of programming language is Python?",
    ] * 10

    answers = [
        {'text': 'stone, brick, tamped earth, and wood'},
        {'text': 'high-level'},
    ] * 10

    qa_model = QAModel()
    qa_model.prepare_data(contexts, questions, answers)
    qa_model.train(epochs=2)

    # Make prediction
    answer = qa_model.predict(
        "The Statue of Liberty was a gift from France to the United States.",
        "Who gave the Statue of Liberty?"
    )
    print("Answer:", answer)

    qa_model.save_model('./qa_model')
```

---

## Text Summarization

### 4.1 Complete Summarization Pipeline

```python
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AdamW
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import json

class SummarizationDataset(Dataset):
    """Dataset for text summarization."""

    def __init__(self, documents, summaries, tokenizer, max_source_length=1024, max_target_length=128):
        self.tokenizer = tokenizer
        self.documents = documents
        self.summaries = summaries
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.documents)

    def __getitem__(self, idx):
        document = self.documents[idx]
        summary = self.summaries[idx]

        # Tokenize source
        source_encoding = self.tokenizer(
            document,
            max_length=self.max_source_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        # Tokenize target
        target_encoding = self.tokenizer(
            summary,
            max_length=self.max_target_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': source_encoding['input_ids'].squeeze(0),
            'attention_mask': source_encoding['attention_mask'].squeeze(0),
            'labels': target_encoding['input_ids'].squeeze(0)
        }

class SummarizationModel:
    """Text summarization model using seq2seq."""

    def __init__(self, model_name='facebook/bart-base', device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(device)

    def prepare_data(self, documents, summaries, batch_size=8):
        """Prepare data loader."""
        dataset = SummarizationDataset(documents, summaries, self.tokenizer)
        self.train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        return self.train_loader

    def train(self, epochs=3, learning_rate=5e-5):
        """Train the summarization model."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')

            self.model.train()
            total_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

            print(f'Epoch {epoch + 1} Loss: {total_loss / len(self.train_loader):.4f}')

    def summarize(self, document, max_length=128, min_length=32, num_beams=4):
        """Generate summary for a document."""
        self.model.eval()

        encoding = self.tokenizer(
            document,
            max_length=1024,
            truncation=True,
            return_tensors='pt',
            padding='max_length'
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        with torch.no_grad():
            summary_ids = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=max_length,
                min_length=min_length,
                num_beams=num_beams,
                early_stopping=True
            )

        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def save_model(self, save_path):
        """Save model."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    @classmethod
    def load_model(cls, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load model."""
        summarization_model = cls(device=device)
        summarization_model.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        summarization_model.tokenizer = AutoTokenizer.from_pretrained(model_path)
        summarization_model.model.to(device)
        return summarization_model

# Usage Example
if __name__ == '__main__':
    documents = [
        "The United Nations is an international organization that aims to maintain international peace and security. It was established in 1945 after World War II.",
        "Climate change is a long-term shift in the Earth's climate and weather patterns. It is primarily caused by human activities."
    ] * 10

    summaries = [
        "The UN maintains international peace and was established in 1945.",
        "Climate change is caused by human activities and affects global weather."
    ] * 10

    summarization_model = SummarizationModel()
    summarization_model.prepare_data(documents, summaries)
    summarization_model.train(epochs=2)

    # Generate summary
    document = "Artificial Intelligence is revolutionizing industries worldwide. From healthcare to finance, AI applications are improving efficiency and accuracy. Machine learning, a subset of AI, enables systems to learn from data without explicit programming."
    summary = summarization_model.summarize(document)
    print("Original:", document)
    print("Summary:", summary)

    summarization_model.save_model('./summarization_model')
```

---

## Machine Translation

### 5.1 Complete Translation Pipeline

```python
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AdamW
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import json

class TranslationDataset(Dataset):
    """Dataset for machine translation."""

    def __init__(self, source_texts, target_texts, tokenizer, source_lang='en_XX', target_lang='fr_XX', max_length=256):
        self.tokenizer = tokenizer
        self.source_texts = source_texts
        self.target_texts = target_texts
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_length = max_length

    def __len__(self):
        return len(self.source_texts)

    def __getitem__(self, idx):
        source_text = self.source_texts[idx]
        target_text = self.target_texts[idx]

        # Tokenize source with language prefix
        source_encoding = self.tokenizer(
            source_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
            src_lang=self.source_lang
        )

        # Tokenize target
        target_encoding = self.tokenizer(
            target_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': source_encoding['input_ids'].squeeze(0),
            'attention_mask': source_encoding['attention_mask'].squeeze(0),
            'labels': target_encoding['input_ids'].squeeze(0)
        }

class TranslationModel:
    """Machine translation model."""

    def __init__(self, model_name='facebook/mbart-large-cc25', source_lang='en_XX', target_lang='fr_XX',
                 device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang=source_lang)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(device)

    def prepare_data(self, source_texts, target_texts, batch_size=8):
        """Prepare data loader."""
        dataset = TranslationDataset(
            source_texts, target_texts, self.tokenizer,
            source_lang=self.source_lang, target_lang=self.target_lang
        )
        self.train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        return self.train_loader

    def train(self, epochs=3, learning_rate=5e-5):
        """Train the translation model."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')

            self.model.train()
            total_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

            print(f'Epoch {epoch + 1} Loss: {total_loss / len(self.train_loader):.4f}')

    def translate(self, text, max_length=256, num_beams=4):
        """Translate text."""
        self.model.eval()

        encoding = self.tokenizer(
            text,
            max_length=256,
            truncation=True,
            return_tensors='pt',
            src_lang=self.source_lang
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        # Set decoder language
        self.model.config.decoder_start_token_id = self.tokenizer.convert_tokens_to_ids(self.target_lang)

        with torch.no_grad():
            translated_ids = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.target_lang)
            )

        translation = self.tokenizer.decode(translated_ids[0], skip_special_tokens=True)
        return translation

    def save_model(self, save_path):
        """Save model."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    @classmethod
    def load_model(cls, model_path, source_lang='en_XX', target_lang='fr_XX',
                   device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load model."""
        translation_model = cls(source_lang=source_lang, target_lang=target_lang, device=device)
        translation_model.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        translation_model.tokenizer = AutoTokenizer.from_pretrained(model_path, src_lang=source_lang)
        translation_model.model.to(device)
        return translation_model

# Usage Example
if __name__ == '__main__':
    # English to French examples
    english_texts = [
        "Hello, how are you?",
        "The weather is beautiful today."
    ] * 10

    french_texts = [
        "Bonjour, comment allez-vous?",
        "Le temps est magnifique aujourd'hui."
    ] * 10

    translation_model = TranslationModel(source_lang='en_XX', target_lang='fr_XX')
    translation_model.prepare_data(english_texts, french_texts)
    translation_model.train(epochs=2)

    # Translate
    translation = translation_model.translate("The food is delicious")
    print("Original:", "The food is delicious")
    print("Translation:", translation)

    translation_model.save_model('./translation_model')
```

---

## Sentiment Analysis

### 6.1 Complete Sentiment Analysis Pipeline

```python
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from tqdm import tqdm

class SentimentDataset(Dataset):
    """Dataset for sentiment analysis."""

    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.tokenizer = tokenizer
        self.texts = texts
        self.labels = labels
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'label': torch.tensor(label, dtype=torch.long)
        }

class SentimentAnalyzer:
    """Sentiment analysis model."""

    def __init__(self, model_name='distilbert-base-uncased', num_labels=3,
                 device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
        self.model.to(device)
        self.label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}

    def prepare_data(self, texts, labels, test_size=0.2, batch_size=32):
        """Prepare data loaders."""
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42
        )

        train_dataset = SentimentDataset(X_train, y_train, self.tokenizer)
        test_dataset = SentimentDataset(X_test, y_test, self.tokenizer)

        self.train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        self.test_loader = DataLoader(test_dataset, batch_size=batch_size)

        return self.train_loader, self.test_loader

    def train(self, epochs=3, learning_rate=5e-5):
        """Train the sentiment analyzer."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')

            self.model.train()
            total_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

            # Evaluate
            val_acc = self.evaluate()

            print(f'Epoch {epoch + 1} Loss: {total_loss / len(self.train_loader):.4f}')
            print(f'Validation Accuracy: {val_acc:.4f}')

    def evaluate(self):
        """Evaluate the model."""
        self.model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in tqdm(self.test_loader, desc='Evaluating'):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                predictions = torch.argmax(outputs.logits, dim=1)
                correct += (predictions == labels).sum().item()
                total += labels.size(0)

        return correct / total

    def predict(self, texts):
        """Predict sentiment for texts."""
        self.model.eval()
        predictions = []

        with torch.no_grad():
            for text in texts:
                encoding = self.tokenizer(
                    text,
                    max_length=256,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt'
                )

                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                logits = outputs.logits[0]
                probabilities = torch.softmax(logits, dim=0)
                prediction = torch.argmax(logits, dim=0).item()

                predictions.append({
                    'text': text,
                    'sentiment': self.label_map[prediction],
                    'scores': {
                        'negative': float(probabilities[0]),
                        'neutral': float(probabilities[1]),
                        'positive': float(probabilities[2])
                    }
                })

        return predictions

    def save_model(self, save_path):
        """Save model."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    @classmethod
    def load_model(cls, model_path, num_labels=3, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load model."""
        analyzer = cls(device=device)
        analyzer.model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=num_labels)
        analyzer.tokenizer = AutoTokenizer.from_pretrained(model_path)
        analyzer.model.to(device)
        return analyzer

# Usage Example
if __name__ == '__main__':
    texts = [
        "This product is amazing! I love it!",
        "Terrible quality, very disappointed",
        "It's okay, nothing special",
        "Excellent service and support",
        "Poor customer experience"
    ] * 20

    labels = [2, 0, 1, 2, 0] * 20  # 0=negative, 1=neutral, 2=positive

    analyzer = SentimentAnalyzer(num_labels=3)
    analyzer.prepare_data(texts, labels)
    analyzer.train(epochs=3)

    # Predict sentiment
    new_texts = [
        "This is fantastic!",
        "I don't like this",
        "It's acceptable"
    ]

    predictions = analyzer.predict(new_texts)
    for pred in predictions:
        print(f"Text: {pred['text']}")
        print(f"Sentiment: {pred['sentiment']}")
        print(f"Scores: {pred['scores']}\n")

    analyzer.save_model('./sentiment_analyzer')
```

---

## Text Generation

### 7.1 Complete Text Generation Pipeline

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AdamW, TextDataset, DataCollatorForLanguageModeling
from torch.utils.data import DataLoader
from tqdm import tqdm

class TextGenerator:
    """Text generation model using causal language modeling."""

    def __init__(self, model_name='gpt2', device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(device)

        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def prepare_data(self, file_path, block_size=128, batch_size=8):
        """Prepare dataset from file."""
        dataset = TextDataset(
            tokenizer=self.tokenizer,
            file_path=file_path,
            block_size=block_size
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        self.train_loader = DataLoader(
            dataset,
            batch_size=batch_size,
            collate_fn=data_collator,
            shuffle=True
        )

        return self.train_loader

    def train(self, epochs=3, learning_rate=5e-5):
        """Train the text generation model."""
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            print(f'\nEpoch {epoch + 1}/{epochs}')

            self.model.train()
            total_loss = 0

            for batch in tqdm(self.train_loader, desc='Training'):
                optimizer.zero_grad()

                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

            print(f'Epoch {epoch + 1} Loss: {total_loss / len(self.train_loader):.4f}')

    def generate(self, prompt, max_length=100, temperature=0.7, top_p=0.9, num_return_sequences=1):
        """Generate text given a prompt."""
        self.model.eval()

        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                input_ids=input_ids,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                top_k=50,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_texts = []
        for seq in output:
            text = self.tokenizer.decode(seq, skip_special_tokens=True)
            generated_texts.append(text)

        return generated_texts

    def generate_with_beam_search(self, prompt, max_length=100, num_beams=5):
        """Generate text using beam search."""
        self.model.eval()

        input_ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                input_ids=input_ids,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def save_model(self, save_path):
        """Save model."""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    @classmethod
    def load_model(cls, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """Load model."""
        text_gen = cls(device=device)
        text_gen.model = AutoModelForCausalLM.from_pretrained(model_path)
        text_gen.tokenizer = AutoTokenizer.from_pretrained(model_path)
        text_gen.model.to(device)
        return text_gen

# Usage Example
if __name__ == '__main__':
    generator = TextGenerator(model_name='gpt2')

    # Generate text with sampling
    prompt = "Once upon a time"
    generated = generator.generate(
        prompt,
        max_length=100,
        temperature=0.7,
        top_p=0.9,
        num_return_sequences=3
    )

    print(f"Prompt: {prompt}\n")
    for i, text in enumerate(generated, 1):
        print(f"Generated {i}: {text}\n")

    # Generate with beam search
    beam_search_output = generator.generate_with_beam_search(
        prompt,
        max_length=100,
        num_beams=5
    )
    print(f"Beam Search: {beam_search_output}")

    generator.save_model('./text_generator')
```

---

## Custom Tokenizer Training

### 8.1 Complete Custom Tokenizer Pipeline

```python
from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, decoders, trainers
from tokenizers.processors import TemplateProcessing
from transformers import PreTrainedTokenizerFast
import json
from pathlib import Path

class CustomTokenizerTrainer:
    """Train custom tokenizers from scratch."""

    def __init__(self, vocab_size=30000, min_frequency=2):
        self.vocab_size = vocab_size
        self.min_frequency = min_frequency
        self.tokenizer = None

    def train_wordpiece_tokenizer(self, files, output_path):
        """
        Train a WordPiece tokenizer.

        Args:
            files: List of file paths to train on
            output_path: Path to save the tokenizer
        """
        # Initialize tokenizer with WordPiece model
        tokenizer = Tokenizer(models.WordPiece(unk_token="[UNK]"))

        # Normalizer
        tokenizer.normalizer = normalizers.Sequence([
            normalizers.NFD(),
            normalizers.Lowercase(),
            normalizers.StripAccents()
        ])

        # Pre-tokenizer
        tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
            pre_tokenizers.Whitespace(),
            pre_tokenizers.Punctuation()
        ])

        # Decoder
        tokenizer.decoder = decoders.WordPiece()

        # Post-processor for BERT-style tokens
        tokenizer.post_processor = TemplateProcessing(
            single="[CLS] $A [SEP]",
            pair="[CLS] $A [SEP] $B:1 [SEP]:1",
            special_tokens=[
                ("[CLS]", 101),
                ("[SEP]", 102),
            ]
        )

        # Trainer
        trainer = trainers.WordPieceTrainer(
            vocab_size=self.vocab_size,
            special_tokens=["[UNK]", "[CLS]", "[SEP]", "[MASK]", "[PAD]"],
            min_frequency=self.min_frequency
        )

        # Train
        print("Training WordPiece tokenizer...")
        tokenizer.train(files, trainer=trainer)

        # Save
        tokenizer.save(f"{output_path}/tokenizer.json")
        self.tokenizer = tokenizer
        print(f"Tokenizer saved to {output_path}")

        return tokenizer

    def train_bpe_tokenizer(self, files, output_path):
        """
        Train a Byte Pair Encoding (BPE) tokenizer.

        Args:
            files: List of file paths to train on
            output_path: Path to save the tokenizer
        """
        tokenizer = Tokenizer(models.BPE())

        # Normalizer
        tokenizer.normalizer = normalizers.Sequence([
            normalizers.NFC(),
            normalizers.Lowercase()
        ])

        # Pre-tokenizer
        tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
            pre_tokenizers.ByteLevel(add_prefix_space=True),
            pre_tokenizers.Whitespace()
        ])

        # Decoder
        tokenizer.decoder = decoders.ByteLevel()

        # Trainer
        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            special_tokens=["<|endoftext|>"],
            min_frequency=self.min_frequency
        )

        # Train
        print("Training BPE tokenizer...")
        tokenizer.train(files, trainer=trainer)

        # Save
        tokenizer.save(f"{output_path}/tokenizer.json")
        self.tokenizer = tokenizer
        print(f"Tokenizer saved to {output_path}")

        return tokenizer

    def train_unigram_tokenizer(self, files, output_path):
        """
        Train a Unigram tokenizer (used in ALBERT).

        Args:
            files: List of file paths to train on
            output_path: Path to save the tokenizer
        """
        tokenizer = Tokenizer(models.Unigram())

        # Normalizer
        tokenizer.normalizer = normalizers.NFD()

        # Pre-tokenizer
        tokenizer.pre_tokenizer = pre_tokenizers.Metaspace()

        # Decoder
        tokenizer.decoder = decoders.Metaspace()

        # Trainer
        trainer = trainers.UnigramTrainer(
            vocab_size=self.vocab_size,
            special_tokens=["<unk>", "<s>", "</s>"],
            min_frequency=self.min_frequency
        )

        # Train
        print("Training Unigram tokenizer...")
        tokenizer.train(files, trainer=trainer)

        # Save
        tokenizer.save(f"{output_path}/tokenizer.json")
        self.tokenizer = tokenizer
        print(f"Tokenizer saved to {output_path}")

        return tokenizer

    def encode(self, text, add_special_tokens=True):
        """Encode text using the trained tokenizer."""
        if self.tokenizer is None:
            raise ValueError("No tokenizer loaded. Train or load a tokenizer first.")

        encoding = self.tokenizer.encode(text)
        return encoding.tokens, encoding.ids

    def decode(self, token_ids):
        """Decode token IDs back to text."""
        if self.tokenizer is None:
            raise ValueError("No tokenizer loaded. Train or load a tokenizer first.")

        return self.tokenizer.decode(token_ids)

    def save_hf_tokenizer(self, json_path, output_path):
        """
        Save tokenizer in HuggingFace format.

        Args:
            json_path: Path to tokenizer.json
            output_path: Path to save HF-compatible tokenizer
        """
        fast_tokenizer = PreTrainedTokenizerFast(
            tokenizer_file=json_path,
            unk_token="[UNK]",
            cls_token="[CLS]",
            sep_token="[SEP]",
            pad_token="[PAD]",
            mask_token="[MASK]"
        )

        fast_tokenizer.save_pretrained(output_path)
        print(f"HuggingFace tokenizer saved to {output_path}")

    def load_tokenizer(self, json_path):
        """Load a tokenizer from JSON."""
        self.tokenizer = Tokenizer.from_file(json_path)
        return self.tokenizer

# Usage Example
if __name__ == '__main__':
    # Create sample training data
    sample_data = """
    The quick brown fox jumps over the lazy dog.
    Natural Language Processing is a subfield of linguistics, computer science, and artificial intelligence.
    Machine learning enables computer systems to learn and improve from experience without being explicitly programmed.
    Deep learning uses neural networks with multiple layers to learn hierarchical representations of data.
    Transformers have revolutionized the field of NLP since their introduction in 2017.
    """ * 100

    # Save sample data
    Path('sample_data.txt').write_text(sample_data)

    # Train custom tokenizers
    trainer = CustomTokenizerTrainer(vocab_size=5000)

    # Train WordPiece tokenizer
    print("Training WordPiece tokenizer...")
    trainer.train_wordpiece_tokenizer(['sample_data.txt'], './custom_wp_tokenizer')

    # Encode and decode
    text = "The quick brown fox"
    tokens, token_ids = trainer.encode(text)
    print(f"Text: {text}")
    print(f"Tokens: {tokens}")
    print(f"Token IDs: {token_ids}")
    print(f"Decoded: {trainer.decode(token_ids)}\n")

    # Train BPE tokenizer
    print("Training BPE tokenizer...")
    trainer.train_bpe_tokenizer(['sample_data.txt'], './custom_bpe_tokenizer')

    # Save as HuggingFace format
    trainer.save_hf_tokenizer('./custom_wp_tokenizer/tokenizer.json', './hf_custom_tokenizer')

    # Clean up
    import os
    os.remove('sample_data.txt')
```

---

## Requirements

```txt
torch>=2.0.0
transformers>=4.30.0
datasets>=2.10.0
scikit-learn>=1.2.0
tqdm>=4.60.0
pandas>=1.5.0
numpy>=1.23.0
seqeval>=1.2.2
fastapi>=0.95.0
uvicorn>=0.21.0
tokenizers>=0.13.0
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Tips for Production

1. **Model Optimization**
   - Use quantization (ONNX, TensorRT)
   - Prune less important weights
   - Use distillation to create smaller models

2. **Inference Optimization**
   - Batch predictions for better throughput
   - Use GPU inference servers (Triton, BentoML)
   - Cache model outputs when possible

3. **Deployment**
   - Use Docker containers
   - Implement proper error handling
   - Add monitoring and logging
   - Version your models

4. **Data Management**
   - Clean and validate data before training
   - Use data augmentation for better generalization
   - Implement data versioning

5. **Model Evaluation**
   - Use appropriate metrics for your task
   - Evaluate on test sets, not training data
   - Conduct error analysis
   - Get human feedback when needed

6. **Security**
   - Validate input data
   - Implement rate limiting
   - Add authentication
   - Sanitize model outputs

---

## References

- [HuggingFace Transformers Documentation](https://huggingface.co/docs/transformers)
- [PyTorch Documentation](https://pytorch.org/docs)
- [Papers with Code](https://paperswithcode.com)
- [NLP Papers](https://github.com/topics/nlp-papers)
