# Natural Language Processing (NLP) Reference Guide

A comprehensive reference for modern NLP techniques, models, and best practices with production-ready implementations.

## Table of Contents

1. [Text Preprocessing](#text-preprocessing)
2. [Word Embeddings](#word-embeddings)
3. [Transformer Models](#transformer-models)
4. [Text Classification & Sentiment Analysis](#text-classification--sentiment-analysis)
5. [Named Entity Recognition (NER)](#named-entity-recognition-ner)
6. [Question Answering Systems](#question-answering-systems)
7. [Sequence-to-Sequence Models](#sequence-to-sequence-models)
8. [Evaluation Metrics](#evaluation-metrics)
9. [HuggingFace Transformers](#huggingface-transformers)
10. [Best Practices](#best-practices)

---

## Text Preprocessing

Text preprocessing is the foundation of any NLP pipeline. It involves cleaning and normalizing text data.

### 1. Tokenization

Tokenization breaks text into individual tokens (words, subwords, or characters).

```python
from typing import List, Dict, Any
import re
from dataclasses import dataclass
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data (one-time)
# nltk.download('punkt')
# nltk.download('stopwords')

@dataclass
class TokenizationConfig:
    """Configuration for tokenization."""
    lowercase: bool = True
    remove_punctuation: bool = False
    remove_numbers: bool = False
    remove_stopwords: bool = False
    language: str = "english"

class TextTokenizer:
    """Production-ready text tokenizer with multiple strategies."""

    def __init__(self, config: TokenizationConfig) -> None:
        """Initialize tokenizer with configuration."""
        self.config = config
        self.stopwords = set(stopwords.words(config.language))

    def word_tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if self.config.lowercase:
            text = text.lower()

        tokens = word_tokenize(text)

        if self.config.remove_punctuation:
            tokens = [t for t in tokens if re.match(r'\w', t)]

        if self.config.remove_numbers:
            tokens = [t for t in tokens if not t.isdigit()]

        if self.config.remove_stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]

        return tokens

    def sentence_tokenize(self, text: str) -> List[str]:
        """Tokenize text into sentences."""
        return sent_tokenize(text)

    def subword_tokenize(self, text: str, max_tokens: int = 100) -> List[str]:
        """Simple subword tokenization using BPE-like approach."""
        # In production, use tokenizers from HuggingFace
        tokens = self.word_tokenize(text)
        return tokens[:max_tokens]

# Usage
config = TokenizationConfig(lowercase=True, remove_stopwords=False)
tokenizer = TextTokenizer(config)
text = "Natural Language Processing is fascinating!"
tokens = tokenizer.word_tokenize(text)
print(f"Tokens: {tokens}")
```

### 2. Normalization

Normalization ensures consistent text representation.

```python
import unicodedata
from typing import Optional

class TextNormalizer:
    """Production-ready text normalizer."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize unicode characters to NFKC form."""
        return unicodedata.normalize('NFKC', text)

    @staticmethod
    def remove_accents(text: str) -> str:
        """Remove diacritical marks."""
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])

    @staticmethod
    def expand_contractions(text: str) -> str:
        """Expand English contractions."""
        contractions_dict = {
            "can't": "cannot",
            "won't": "will not",
            "don't": "do not",
            "didn't": "did not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
        }

        pattern = re.compile(r'\b(' + '|'.join(contractions_dict.keys()) + r')\b')
        return pattern.sub(lambda x: contractions_dict[x.group()], text)

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace: remove extra spaces and newlines."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def lowercase(text: str) -> str:
        """Convert to lowercase."""
        return text.lower()

    @classmethod
    def normalize_pipeline(
        cls,
        text: str,
        steps: Optional[List[str]] = None
    ) -> str:
        """Apply normalization pipeline."""
        if steps is None:
            steps = ['unicode', 'contractions', 'whitespace', 'lowercase']

        for step in steps:
            if step == 'unicode':
                text = cls.normalize_unicode(text)
            elif step == 'accents':
                text = cls.remove_accents(text)
            elif step == 'contractions':
                text = cls.expand_contractions(text)
            elif step == 'whitespace':
                text = cls.normalize_whitespace(text)
            elif step == 'lowercase':
                text = cls.lowercase(text)

        return text

# Usage
normalizer = TextNormalizer()
text = "Don't  worry!   It's   working correctly."
normalized = normalizer.normalize_pipeline(text)
print(f"Normalized: {normalized}")
```

### 3. Stemming and Lemmatization

Reduce words to their root forms.

```python
from nltk.stem import PorterStemmer, SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
# nltk.download('wordnet')
# nltk.download('omw-1.4')

class MorphologyProcessor:
    """Production-ready stemming and lemmatization."""

    def __init__(self, language: str = "english") -> None:
        """Initialize morphology processor."""
        self.porter_stemmer = PorterStemmer()
        self.snowball_stemmer = SnowballStemmer(language)
        self.lemmatizer = WordNetLemmatizer()

    def porter_stem(self, token: str) -> str:
        """Apply Porter stemming."""
        return self.porter_stemmer.stem(token)

    def snowball_stem(self, token: str) -> str:
        """Apply Snowball stemming (more aggressive)."""
        return self.snowball_stemmer.stem(token)

    def lemmatize(self, token: str, pos: str = "v") -> str:
        """
        Lemmatize token.

        Args:
            token: Word to lemmatize
            pos: Part of speech ('n' for noun, 'v' for verb, 'a' for adjective)
        """
        return self.lemmatizer.lemmatize(token, pos=pos)

    def process_tokens(
        self,
        tokens: List[str],
        method: str = "lemmatize"
    ) -> List[str]:
        """Process list of tokens."""
        if method == "porter":
            return [self.porter_stem(t) for t in tokens]
        elif method == "snowball":
            return [self.snowball_stem(t) for t in tokens]
        elif method == "lemmatize":
            return [self.lemmatize(t) for t in tokens]
        else:
            raise ValueError(f"Unknown method: {method}")

# Usage
morphology = MorphologyProcessor()
words = ["running", "runs", "ran", "easily", "studied"]
print(f"Porter stemming: {[morphology.porter_stem(w) for w in words]}")
print(f"Lemmatization: {[morphology.lemmatize(w, 'v') for w in words]}")
```

---

## Word Embeddings

Word embeddings map words to dense vector representations.

### 1. Word2Vec

Creates word vectors through context prediction.

```python
from typing import Tuple, Optional
import numpy as np
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

class Word2VecEmbedder:
    """Production-ready Word2Vec implementation."""

    def __init__(
        self,
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 2,
        workers: int = 4,
        sg: int = 0  # 0 for CBOW, 1 for Skip-gram
    ) -> None:
        """Initialize Word2Vec embedder."""
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.workers = workers
        self.sg = sg
        self.model: Optional[Word2Vec] = None

    def train(self, sentences: List[List[str]]) -> None:
        """Train Word2Vec model."""
        self.model = Word2Vec(
            sentences=sentences,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=self.workers,
            sg=self.sg,
            epochs=5
        )

    def get_vector(self, word: str) -> np.ndarray:
        """Get embedding for a word."""
        if self.model is None:
            raise ValueError("Model not trained")
        if word in self.model.wv:
            return self.model.wv[word]
        else:
            raise KeyError(f"Word '{word}' not in vocabulary")

    def most_similar(self, word: str, topn: int = 10) -> List[Tuple[str, float]]:
        """Find most similar words."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.wv.most_similar(word, topn=topn)

    def similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.wv.similarity(word1, word2)

    def save(self, path: str) -> None:
        """Save model to disk."""
        if self.model is None:
            raise ValueError("Model not trained")
        self.model.save(path)

    def load(self, path: str) -> None:
        """Load model from disk."""
        self.model = Word2Vec.load(path)

# Usage
embedder = Word2VecEmbedder(vector_size=100, sg=1)  # Skip-gram
sentences = [
    ['natural', 'language', 'processing'],
    ['machine', 'learning', 'algorithms'],
    ['deep', 'neural', 'networks']
]
embedder.train(sentences)
print(f"Vector shape: {embedder.get_vector('natural').shape}")
```

### 2. GloVe-like Approach

Global vectors for word representation.

```python
class GloVeStyleEmbedding:
    """
    Production-ready GloVe-style embedding.
    Uses word co-occurrence statistics.
    """

    def __init__(self, vector_size: int = 100) -> None:
        """Initialize GloVe-style embedding."""
        self.vector_size = vector_size
        self.vocab: Dict[str, int] = {}
        self.cooccurrence_matrix: Optional[np.ndarray] = None
        self.embeddings: Optional[np.ndarray] = None

    def build_cooccurrence_matrix(
        self,
        sentences: List[List[str]],
        window_size: int = 5
    ) -> None:
        """Build word co-occurrence matrix."""
        # Build vocabulary
        word_freq: Dict[str, int] = {}
        for sentence in sentences:
            for word in sentence:
                word_freq[word] = word_freq.get(word, 0) + 1

        self.vocab = {word: idx for idx, word in enumerate(sorted(word_freq.keys()))}
        vocab_size = len(self.vocab)

        # Build co-occurrence matrix
        self.cooccurrence_matrix = np.zeros((vocab_size, vocab_size))

        for sentence in sentences:
            for i, word in enumerate(sentence):
                for j in range(max(0, i - window_size), min(len(sentence), i + window_size + 1)):
                    if i != j:
                        word_idx = self.vocab[word]
                        context_idx = self.vocab[sentence[j]]
                        self.cooccurrence_matrix[word_idx, context_idx] += 1.0

    def get_embeddings(self) -> np.ndarray:
        """Get learned embeddings."""
        if self.cooccurrence_matrix is None:
            raise ValueError("Cooccurrence matrix not built")

        # Use SVD for dimensionality reduction (simplified GloVe)
        from sklearn.decomposition import TruncatedSVD
        svd = TruncatedSVD(n_components=self.vector_size)
        self.embeddings = svd.fit_transform(self.cooccurrence_matrix)
        return self.embeddings

    def get_word_vector(self, word: str) -> np.ndarray:
        """Get embedding for a word."""
        if word not in self.vocab:
            raise KeyError(f"Word '{word}' not in vocabulary")
        if self.embeddings is None:
            self.get_embeddings()

        word_idx = self.vocab[word]
        return self.embeddings[word_idx]

# Usage
glove = GloVeStyleEmbedding(vector_size=100)
glove.build_cooccurrence_matrix(sentences, window_size=5)
embeddings = glove.get_embeddings()
print(f"Embeddings shape: {embeddings.shape}")
```

### 3. FastText

Subword-aware embeddings.

```python
from gensim.models import FastText

class FastTextEmbedder:
    """Production-ready FastText implementation."""

    def __init__(
        self,
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 2,
        workers: int = 4
    ) -> None:
        """Initialize FastText embedder."""
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.workers = workers
        self.model: Optional[FastText] = None

    def train(self, sentences: List[List[str]]) -> None:
        """Train FastText model."""
        self.model = FastText(
            sentences=sentences,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=self.workers,
            epochs=5
        )

    def get_vector(self, word: str) -> np.ndarray:
        """Get embedding for a word (handles OOV)."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.wv[word]  # FastText handles OOV automatically

    def most_similar(self, word: str, topn: int = 10) -> List[Tuple[str, float]]:
        """Find most similar words."""
        if self.model is None:
            raise ValueError("Model not trained")
        return self.model.wv.most_similar(word, topn=topn)

# Usage
ft_embedder = FastTextEmbedder(vector_size=100)
ft_embedder.train(sentences)
vector = ft_embedder.get_vector("natural")
print(f"FastText vector shape: {vector.shape}")
```

---

## Transformer Models

Modern transformer-based models for NLP tasks.

### 1. BERT (Bidirectional Encoder Representations from Transformers)

```python
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
from transformers import PreTrainedTokenizer, PreTrainedModel
import torch
from torch import Tensor

class BERTEmbedder:
    """Production-ready BERT embedding extractor."""

    def __init__(self, model_name: str = "bert-base-uncased") -> None:
        """Initialize BERT embedder."""
        self.model_name = model_name
        self.tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model: PreTrainedModel = AutoModel.from_pretrained(model_name, output_hidden_states=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def get_embeddings(
        self,
        text: str,
        layer: int = -1,
        pooling: str = "mean"
    ) -> np.ndarray:
        """
        Extract embeddings from BERT.

        Args:
            text: Input text
            layer: Which layer to extract (-1 for last, -2 for second-to-last, etc.)
            pooling: Pooling strategy ('mean', 'cls', or 'max')
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            hidden_states = outputs.hidden_states

        # Get embeddings from specified layer
        embeddings = hidden_states[layer].squeeze(0).cpu().numpy()

        # Apply pooling
        if pooling == "mean":
            return np.mean(embeddings, axis=0)
        elif pooling == "cls":
            return embeddings[0]
        elif pooling == "max":
            return np.max(embeddings, axis=0)
        else:
            raise ValueError(f"Unknown pooling: {pooling}")

    def encode_sentences(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts."""
        embeddings = [self.get_embeddings(text) for text in texts]
        return np.array(embeddings)

# Usage
bert = BERTEmbedder("bert-base-uncased")
embedding = bert.get_embeddings("Natural language processing is fascinating")
print(f"BERT embedding shape: {embedding.shape}")
```

### 2. RoBERTa

```python
class RoBERTaClassifier:
    """Production-ready RoBERTa text classifier."""

    def __init__(
        self,
        model_name: str = "roberta-base",
        num_labels: int = 2
    ) -> None:
        """Initialize RoBERTa classifier."""
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Make predictions on text.

        Returns:
            Dict with predicted label and confidence scores
        """
        self.model.eval()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        predicted_label = np.argmax(probabilities)

        return {
            "predicted_label": int(predicted_label),
            "confidence": float(probabilities[predicted_label]),
            "probabilities": probabilities.tolist()
        }

    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Make predictions on multiple texts."""
        return [self.predict(text) for text in texts]

# Usage
roberta = RoBERTaClassifier("roberta-base", num_labels=2)
result = roberta.predict("This movie was fantastic!")
print(f"Prediction: {result}")
```

### 3. T5 (Text-to-Text Transfer Transformer)

```python
from transformers import T5Tokenizer, T5ForConditionalGeneration

class T5TextGenerator:
    """Production-ready T5 model for text generation tasks."""

    def __init__(self, model_name: str = "t5-base") -> None:
        """Initialize T5 generator."""
        self.model_name = model_name
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def generate(
        self,
        text: str,
        task_prefix: str = "",
        max_length: int = 100,
        num_beams: int = 4
    ) -> str:
        """
        Generate text using T5.

        Args:
            text: Input text
            task_prefix: Task prefix (e.g., 'summarize:', 'translate English to French:')
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
        """
        input_text = f"{task_prefix}{text}".strip()
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=num_beams,
            temperature=1.0,
            do_sample=False
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def summarize(self, text: str, max_length: int = 100) -> str:
        """Summarize text."""
        return self.generate(text, task_prefix="summarize:", max_length=max_length)

    def translate(self, text: str, source_lang: str = "en", target_lang: str = "fr") -> str:
        """Translate text."""
        prefix = f"translate {source_lang} to {target_lang}:"
        return self.generate(text, task_prefix=prefix)

# Usage
t5 = T5TextGenerator("t5-base")
summary = t5.summarize("Natural language processing enables computers to understand human language.")
print(f"Summary: {summary}")
```

### 4. ELECTRA

```python
class ELECTRAModel:
    """Production-ready ELECTRA model for text classification."""

    def __init__(self, model_name: str = "google/electra-base-discriminator") -> None:
        """Initialize ELECTRA model."""
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def get_representation(self, text: str, pooling: str = "cls") -> np.ndarray:
        """Get text representation from ELECTRA."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            last_hidden = outputs.last_hidden_state

        if pooling == "cls":
            return last_hidden[:, 0, :].squeeze(0).cpu().numpy()
        elif pooling == "mean":
            return last_hidden.mean(dim=1).squeeze(0).cpu().numpy()
        else:
            raise ValueError(f"Unknown pooling: {pooling}")

# Usage
electra = ELECTRAModel()
rep = electra.get_representation("ELECTRA is efficient and effective")
print(f"Representation shape: {rep.shape}")
```

---

## Text Classification & Sentiment Analysis

### Complete Text Classification Pipeline

```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

@dataclass
class TextClassificationConfig:
    """Configuration for text classification."""
    model_name: str = "distilbert-base-uncased"
    num_labels: int = 2
    max_length: int = 128
    batch_size: int = 32
    learning_rate: float = 2e-5
    num_epochs: int = 3
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

class TextDataset(Dataset):
    """Custom dataset for text classification."""

    def __init__(
        self,
        texts: List[str],
        labels: List[int],
        tokenizer: PreTrainedTokenizer,
        max_length: int
    ) -> None:
        """Initialize dataset."""
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, Tensor]:
        """Get a single example."""
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(label, dtype=torch.long)
        }

class TextClassifier:
    """Production-ready text classifier."""

    def __init__(self, config: TextClassificationConfig) -> None:
        """Initialize classifier."""
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            config.model_name,
            num_labels=config.num_labels
        )
        self.model.to(config.device)
        self.optimizer = AdamW(self.model.parameters(), lr=config.learning_rate)

    def train(
        self,
        train_texts: List[str],
        train_labels: List[int],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[int]] = None
    ) -> Dict[str, List[float]]:
        """Train the classifier."""
        train_dataset = TextDataset(train_texts, train_labels, self.tokenizer, self.config.max_length)
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)

        history = {"loss": [], "accuracy": []}

        for epoch in range(self.config.num_epochs):
            self.model.train()
            total_loss = 0
            correct = 0
            total = 0

            for batch in train_loader:
                self.optimizer.zero_grad()

                input_ids = batch["input_ids"].to(self.config.device)
                attention_mask = batch["attention_mask"].to(self.config.device)
                labels = batch["labels"].to(self.config.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()
                predictions = torch.argmax(outputs.logits, dim=-1)
                correct += (predictions == labels).sum().item()
                total += labels.size(0)

            avg_loss = total_loss / len(train_loader)
            accuracy = correct / total

            history["loss"].append(avg_loss)
            history["accuracy"].append(accuracy)

            print(f"Epoch {epoch + 1}/{self.config.num_epochs} - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")

        return history

    def predict(self, text: str) -> Dict[str, Any]:
        """Predict label for a single text."""
        self.model.eval()
        inputs = self.tokenizer(text, return_tensors="pt", max_length=self.config.max_length, truncation=True)
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        predicted_label = np.argmax(probabilities)

        return {
            "label": int(predicted_label),
            "confidence": float(probabilities[predicted_label]),
            "probabilities": probabilities.tolist()
        }

    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predict labels for multiple texts."""
        return [self.predict(text) for text in texts]

    def save(self, path: str) -> None:
        """Save model and tokenizer."""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)

    def load(self, path: str) -> None:
        """Load model and tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForSequenceClassification.from_pretrained(path)
        self.model.to(self.config.device)

# Usage
config = TextClassificationConfig()
classifier = TextClassifier(config)

# Example data
texts = ["This is great!", "This is terrible!", "Amazing product", "Worst ever"]
labels = [1, 0, 1, 0]

history = classifier.train(texts, labels)
prediction = classifier.predict("I love this!")
print(f"Prediction: {prediction}")
```

### Sentiment Analysis

```python
from transformers import pipeline

class SentimentAnalyzer:
    """Production-ready sentiment analysis."""

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english") -> None:
        """Initialize sentiment analyzer."""
        self.model_name = model_name
        self.pipeline = pipeline("sentiment-analysis", model=model_name)

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        result = self.pipeline(text[:512])[0]  # Limit to 512 chars

        return {
            "label": result["label"],
            "score": float(result["score"]),
            "sentiment": "positive" if result["label"] == "POSITIVE" else "negative"
        }

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts."""
        return [self.analyze(text) for text in texts]

    def analyze_with_confidence(
        self,
        text: str,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Analyze sentiment with confidence threshold."""
        result = self.analyze(text)

        return {
            **result,
            "is_confident": result["score"] >= threshold,
            "threshold": threshold
        }

# Usage
analyzer = SentimentAnalyzer()
result = analyzer.analyze("I absolutely loved this movie!")
print(f"Sentiment: {result}")
```

---

## Named Entity Recognition (NER)

```python
from transformers import AutoModelForTokenClassification, pipeline

class NamedEntityRecognizer:
    """Production-ready NER using transformers."""

    def __init__(self, model_name: str = "dbmdz/bert-base-cased-finetuned-conll03-english") -> None:
        """Initialize NER model."""
        self.model_name = model_name
        self.pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple")

    def recognize_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text."""
        entities = self.pipeline(text[:512])

        # Post-process results
        processed_entities = []
        for entity in entities:
            processed_entities.append({
                "word": entity["word"],
                "entity_type": entity["entity_group"],
                "score": float(entity["score"]),
                "start": entity["start"],
                "end": entity["end"]
            })

        return processed_entities

    def group_entities_by_type(self, text: str) -> Dict[str, List[str]]:
        """Group extracted entities by type."""
        entities = self.recognize_entities(text)
        grouped = {}

        for entity in entities:
            entity_type = entity["entity_type"]
            word = entity["word"]

            if entity_type not in grouped:
                grouped[entity_type] = []
            grouped[entity_type].append(word)

        return grouped

    def filter_entities_by_confidence(
        self,
        text: str,
        min_confidence: float = 0.9
    ) -> List[Dict[str, Any]]:
        """Extract entities with minimum confidence."""
        entities = self.recognize_entities(text)
        return [e for e in entities if e["score"] >= min_confidence]

# Usage
ner = NamedEntityRecognizer()
entities = ner.recognize_entities("John Smith works at Google in Mountain View, California.")
print(f"Entities: {entities}")

grouped = ner.group_entities_by_type("John Smith works at Google in Mountain View, California.")
print(f"Grouped entities: {grouped}")
```

---

## Question Answering Systems

```python
class QuestionAnsweringSystem:
    """Production-ready QA system using transformers."""

    def __init__(self, model_name: str = "distilbert-base-cased-distilled-squad") -> None:
        """Initialize QA system."""
        self.model_name = model_name
        self.pipeline = pipeline("question-answering", model=model_name)

    def answer(self, question: str, context: str) -> Dict[str, Any]:
        """
        Answer a question based on context.

        Args:
            question: The question to answer
            context: The context/passage to search for the answer

        Returns:
            Dict with answer, score, and span information
        """
        result = self.pipeline(question=question, context=context)

        return {
            "answer": result["answer"],
            "confidence": float(result["score"]),
            "start": result["start"],
            "end": result["end"],
            "context_snippet": context[max(0, result["start"] - 20):min(len(context), result["end"] + 20)]
        }

    def answer_multiple_questions(
        self,
        questions: List[str],
        context: str
    ) -> List[Dict[str, Any]]:
        """Answer multiple questions from the same context."""
        return [self.answer(q, context) for q in questions]

    def retrieve_and_answer(
        self,
        question: str,
        documents: List[str],
        top_k: int = 1
    ) -> List[Dict[str, Any]]:
        """Retrieve top documents and answer question from each."""
        # Simple retrieval (in production, use dense retrievers)
        results = []
        for doc in documents[:top_k]:
            result = self.answer(question, doc)
            result["source_document"] = doc[:100]  # Store snippet
            results.append(result)

        return results

# Usage
qa = QuestionAnsweringSystem()
context = "Machine learning is a subset of artificial intelligence that enables systems to learn from data."
question = "What is machine learning?"
answer = qa.answer(question, context)
print(f"Answer: {answer}")
```

---

## Sequence-to-Sequence Models

```python
class Seq2SeqModel:
    """Production-ready Seq2Seq model for translation, summarization, etc."""

    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        task: str = "summarization"
    ) -> None:
        """Initialize Seq2Seq model."""
        self.model_name = model_name
        self.task = task
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def generate(
        self,
        text: str,
        max_length: int = 128,
        min_length: int = 30,
        num_beams: int = 4,
        temperature: float = 1.0,
        length_penalty: float = 2.0,
        early_stopping: bool = True
    ) -> str:
        """Generate output sequence."""
        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            min_length=min_length,
            num_beams=num_beams,
            temperature=temperature,
            length_penalty=length_penalty,
            early_stopping=early_stopping,
            do_sample=False
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def summarize(self, text: str, max_length: int = 100, min_length: int = 30) -> str:
        """Summarize text."""
        return self.generate(text, max_length=max_length, min_length=min_length)

    def batch_generate(self, texts: List[str], max_length: int = 128) -> List[str]:
        """Generate for multiple inputs."""
        return [self.generate(text, max_length=max_length) for text in texts]

class TransformerFromScratch:
    """Educational transformer implementation from scratch."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 2048,
        max_seq_length: int = 512
    ) -> None:
        """Initialize transformer."""
        self.d_model = d_model
        self.vocab_size = vocab_size

        # Token embeddings
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = self._create_positional_encoding(max_seq_length, d_model)

        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Output projection
        self.linear_out = nn.Linear(d_model, vocab_size)

    @staticmethod
    def _create_positional_encoding(max_seq_length: int, d_model: int) -> Tensor:
        """Create positional encoding."""
        position = torch.arange(max_seq_length).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * -(torch.log(torch.tensor(10000.0)) / d_model))

        pe = torch.zeros(max_seq_length, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        return pe.unsqueeze(0)

    def forward(self, input_ids: Tensor) -> Tensor:
        """Forward pass."""
        # Embedding with positional encoding
        x = self.embedding(input_ids) * np.sqrt(self.d_model)
        x = x + self.positional_encoding[:, :input_ids.size(1), :]

        # Encoder
        x = self.encoder(x)

        # Output projection
        logits = self.linear_out(x)

        return logits

# Usage
from transformers import AutoModelForSeq2SeqLM

seq2seq = Seq2SeqModel("facebook/bart-large-cnn")
summary = seq2seq.summarize("Natural language processing is a field of artificial intelligence that focuses on enabling computers to understand and process human language in a meaningful and useful way.")
print(f"Summary: {summary}")
```

---

## Evaluation Metrics

```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import numpy as np

class NLPMetrics:
    """Production-ready NLP evaluation metrics."""

    @staticmethod
    def bleu_score(
        reference: List[str],
        hypothesis: List[str],
        weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)
    ) -> float:
        """Calculate BLEU score."""
        smoothing = SmoothingFunction().method1
        return sentence_bleu(
            [reference],
            hypothesis,
            weights=weights,
            smoothing_function=smoothing
        )

    @staticmethod
    def rouge_score(
        reference: str,
        hypothesis: str,
        rouge_types: List[str] = ["rouge1", "rouge2", "rougeL"]
    ) -> Dict[str, float]:
        """Calculate ROUGE scores."""
        scorer = rouge_scorer.RougeScorer(rouge_types)
        scores = scorer.score(reference, hypothesis)

        results = {}
        for rouge_type in rouge_types:
            results[rouge_type] = scores[rouge_type].fmeasure

        return results

    @staticmethod
    def f1_score(
        references: List[List[str]],
        predictions: List[List[str]]
    ) -> float:
        """Calculate F1 score for token-level predictions."""
        tp = sum(len(set(ref) & set(pred)) for ref, pred in zip(references, predictions))
        fp = sum(len(set(pred) - set(ref)) for ref, pred in zip(references, predictions))
        fn = sum(len(set(ref) - set(pred)) for ref, pred in zip(references, predictions))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    @staticmethod
    def meteor_score(reference: str, hypothesis: str) -> float:
        """
        Simplified METEOR score implementation.
        For production, use: nltk.meteor_score.meteor_score()
        """
        ref_tokens = reference.lower().split()
        hyp_tokens = hypothesis.lower().split()

        matches = len(set(ref_tokens) & set(hyp_tokens))
        recall = matches / len(ref_tokens) if ref_tokens else 0
        precision = matches / len(hyp_tokens) if hyp_tokens else 0

        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    @staticmethod
    def bert_score(references: List[str], candidates: List[str]) -> Dict[str, float]:
        """
        Calculate BERTScore.
        Requires: pip install bert-score
        """
        try:
            from bert_score import score as bert_score_fn
            P, R, F1 = bert_score_fn(candidates, references, lang="en", verbose=False)

            return {
                "precision": float(P.mean()),
                "recall": float(R.mean()),
                "f1": float(F1.mean())
            }
        except ImportError:
            raise ImportError("Install bert-score: pip install bert-score")

    @staticmethod
    def perplexity(log_probabilities: List[float]) -> float:
        """Calculate perplexity from log probabilities."""
        return np.exp(-np.mean(log_probabilities))

# Usage
metrics = NLPMetrics()
reference = ["the", "cat", "sat", "on", "the", "mat"]
hypothesis = ["the", "cat", "is", "on", "the", "mat"]
bleu = metrics.bleu_score(reference, hypothesis)
print(f"BLEU score: {bleu}")

rouge_scores = metrics.rouge_score(
    "The cat sat on the mat.",
    "The cat is on the mat."
)
print(f"ROUGE scores: {rouge_scores}")
```

---

## HuggingFace Transformers

Complete examples and utilities for HuggingFace Transformers library.

```python
from transformers import (
    AutoTokenizer,
    AutoModel,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering,
    pipeline,
    TextClassificationPipeline
)

class HuggingFaceModelHub:
    """Utility class for HuggingFace model management."""

    # Popular model names
    MODELS = {
        "bert_base": "bert-base-uncased",
        "bert_large": "bert-large-uncased",
        "roberta_base": "roberta-base",
        "distilbert": "distilbert-base-uncased",
        "electra": "google/electra-base-discriminator",
        "albert": "albert-base-v2",
        "xlnet": "xlnet-base-cased",
        "t5_base": "t5-base",
        "t5_large": "t5-large",
        "bart_base": "facebook/bart-base",
        "bart_large": "facebook/bart-large",
        "gpt2": "gpt2",
        "gpt2_medium": "gpt2-medium"
    }

    @classmethod
    def load_tokenizer(cls, model_key: str) -> PreTrainedTokenizer:
        """Load tokenizer by key."""
        model_name = cls.MODELS.get(model_key, model_key)
        return AutoTokenizer.from_pretrained(model_name)

    @classmethod
    def load_model(cls, model_key: str) -> PreTrainedModel:
        """Load model by key."""
        model_name = cls.MODELS.get(model_key, model_key)
        return AutoModel.from_pretrained(model_name)

    @classmethod
    def load_classification_model(cls, model_key: str, num_labels: int = 2) -> PreTrainedModel:
        """Load classification model."""
        model_name = cls.MODELS.get(model_key, model_key)
        return AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )

class PipelineFactory:
    """Factory for creating HuggingFace pipelines."""

    TASK_PIPELINES = {
        "text-classification": "sentiment-analysis",
        "ner": "ner",
        "question-answering": "question-answering",
        "summarization": "summarization",
        "translation": "translation_en_to_fr",
        "text-generation": "text-generation",
        "zero-shot-classification": "zero-shot-classification"
    }

    @classmethod
    def create_pipeline(
        cls,
        task: str,
        model: Optional[str] = None,
        device: int = 0
    ) -> Any:
        """Create a pipeline for a given task."""
        if torch.cuda.is_available() and device >= 0:
            device = device
        else:
            device = -1  # CPU

        return pipeline(task, model=model, device=device)

class HuggingFaceFineTuner:
    """Fine-tune HuggingFace models on custom datasets."""

    def __init__(
        self,
        model_name: str,
        output_dir: str,
        learning_rate: float = 2e-5,
        batch_size: int = 16,
        num_epochs: int = 3
    ) -> None:
        """Initialize fine-tuner."""
        self.model_name = model_name
        self.output_dir = output_dir
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def prepare_dataset(
        self,
        texts: List[str],
        labels: List[int],
        max_length: int = 128
    ) -> Dataset:
        """Prepare dataset for training."""
        class CustomDataset(Dataset):
            def __init__(self, texts, labels, tokenizer, max_length):
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
                    max_length=self.max_length,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt"
                )

                return {
                    "input_ids": encoding["input_ids"].squeeze(0),
                    "attention_mask": encoding["attention_mask"].squeeze(0),
                    "labels": torch.tensor(label)
                }

        return CustomDataset(texts, labels, self.tokenizer, max_length)

    def fine_tune(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        num_labels: int = 2
    ) -> None:
        """Fine-tune the model."""
        from transformers import Trainer, TrainingArguments

        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels
        )

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{self.output_dir}/logs",
            logging_steps=100,
            evaluation_strategy="epoch" if eval_dataset else "no"
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset
        )

        trainer.train()
        trainer.save_model(self.output_dir)

# Usage
hub = HuggingFaceModelHub()
tokenizer = hub.load_tokenizer("bert_base")
model = hub.load_model("bert_base")
print(f"Model loaded: {model}")

pipeline_factory = PipelineFactory()
sentiment_pipeline = pipeline_factory.create_pipeline("text-classification")
result = sentiment_pipeline("I love NLP!")
print(f"Sentiment: {result}")
```

---

## Best Practices

### 1. Production Deployment

```python
@dataclass
class DeploymentConfig:
    """Configuration for production deployment."""
    model_path: str
    batch_size: int = 32
    max_workers: int = 4
    cache_size: int = 1000
    timeout: int = 30
    log_level: str = "INFO"

class ProductionNLPModel:
    """Production-ready NLP model wrapper."""

    def __init__(self, config: DeploymentConfig) -> None:
        """Initialize production model."""
        self.config = config
        self.model = AutoModel.from_pretrained(config.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()
        self.cache = {}

    def predict_with_cache(self, text: str) -> np.ndarray:
        """Predict with caching."""
        text_hash = hash(text)

        if text_hash in self.cache:
            return self.cache[text_hash]

        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        result = outputs.last_hidden_state.mean(dim=1).cpu().numpy()

        if len(self.cache) < self.config.cache_size:
            self.cache[text_hash] = result

        return result

    def batch_predict(self, texts: List[str]) -> List[np.ndarray]:
        """Batch prediction with error handling."""
        results = []
        for text in texts:
            try:
                result = self.predict_with_cache(text)
                results.append(result)
            except Exception as e:
                print(f"Error processing text: {e}")
                results.append(None)

        return results
```

### 2. Error Handling and Validation

```python
class NLPPipelineValidator:
    """Validate NLP pipeline inputs and outputs."""

    @staticmethod
    def validate_text(text: str, min_length: int = 1, max_length: int = 512) -> bool:
        """Validate text input."""
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text)}")

        if len(text) < min_length or len(text) > max_length:
            raise ValueError(f"Text length {len(text)} not in range [{min_length}, {max_length}]")

        return True

    @staticmethod
    def validate_batch(texts: List[str], max_batch_size: int = 100) -> bool:
        """Validate batch of texts."""
        if len(texts) > max_batch_size:
            raise ValueError(f"Batch size {len(texts)} exceeds maximum {max_batch_size}")

        for i, text in enumerate(texts):
            try:
                NLPPipelineValidator.validate_text(text)
            except Exception as e:
                raise ValueError(f"Error in text {i}: {e}")

        return True

    @staticmethod
    def validate_predictions(predictions: List[Dict], required_keys: List[str]) -> bool:
        """Validate model predictions."""
        for i, pred in enumerate(predictions):
            if not isinstance(pred, dict):
                raise TypeError(f"Prediction {i} is not a dict")

            for key in required_keys:
                if key not in pred:
                    raise KeyError(f"Prediction {i} missing key: {key}")

        return True

class RobustNLPPipeline:
    """Robust NLP pipeline with error handling."""

    def __init__(self, model_name: str) -> None:
        """Initialize pipeline."""
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.validator = NLPPipelineValidator()

    def process(self, text: str) -> Dict[str, Any]:
        """Process text with error handling."""
        try:
            self.validator.validate_text(text)

            inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            outputs = self.model(**inputs)

            return {
                "status": "success",
                "embeddings": outputs.last_hidden_state.numpy().tolist(),
                "error": None
            }

        except Exception as e:
            return {
                "status": "error",
                "embeddings": None,
                "error": str(e)
            }
```

### 3. Monitoring and Logging

```python
import logging
from datetime import datetime

class NLPMonitor:
    """Monitor NLP model performance."""

    def __init__(self, model_name: str) -> None:
        """Initialize monitor."""
        self.model_name = model_name
        self.logger = self._setup_logger()
        self.metrics = {
            "total_requests": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "average_latency": 0.0
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_request(self, text: str) -> None:
        """Log incoming request."""
        self.metrics["total_requests"] += 1
        self.logger.info(f"Processing request #{self.metrics['total_requests']}: {text[:50]}...")

    def log_success(self, latency: float) -> None:
        """Log successful prediction."""
        self.metrics["successful_predictions"] += 1
        self.logger.info(f"Successful prediction. Latency: {latency:.3f}s")

    def log_error(self, error: str) -> None:
        """Log error."""
        self.metrics["failed_predictions"] += 1
        self.logger.error(f"Prediction error: {error}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            **self.metrics,
            "success_rate": self.metrics["successful_predictions"] / max(self.metrics["total_requests"], 1)
        }
```

---

## Summary

This comprehensive NLP reference covers:

- **Text Preprocessing**: Tokenization, normalization, stemming, lemmatization
- **Word Embeddings**: Word2Vec, GloVe, FastText implementations
- **Transformer Models**: BERT, RoBERTa, T5, ELECTRA with examples
- **Text Classification**: Complete pipelines with training and evaluation
- **Sentiment Analysis**: Production-ready sentiment analyzer
- **NER**: Named entity recognition with HuggingFace
- **Question Answering**: QA systems and retrieval
- **Seq2Seq Models**: Summarization and translation
- **Metrics**: BLEU, ROUGE, F1, BERTScore, Perplexity
- **HuggingFace Integration**: Model hub, pipelines, fine-tuning
- **Best Practices**: Production deployment, error handling, monitoring

All code includes type hints and is production-ready.
