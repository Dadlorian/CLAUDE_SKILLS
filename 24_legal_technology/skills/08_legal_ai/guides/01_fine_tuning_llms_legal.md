# Fine-tuning LLMs for Legal Work

## Overview
This guide provides a comprehensive walkthrough for fine-tuning large language models (LLMs) on legal data to create specialized legal AI assistants. We'll cover data preparation, training strategies, evaluation, and deployment.

## Prerequisites

```bash
# Required libraries
pip install transformers==4.35.0
pip install datasets==2.14.0
pip install accelerate==0.24.0
pip install peft==0.6.0  # For LoRA
pip install bitsandbytes==0.41.0  # For quantization
pip install wandb  # For experiment tracking
pip install torch torchvision torchaudio
```

## Step 1: Data Preparation

### 1.1 Collecting Legal Training Data

```python
import pandas as pd
from datasets import Dataset, DatasetDict

class LegalDataCollector:
    """Collect and prepare legal training data"""

    def __init__(self):
        self.sources = {}

    def collect_legal_memos(self, directory_path):
        """Collect legal memoranda for training"""

        import glob
        import os

        memos = []

        for file_path in glob.glob(f"{directory_path}/**/*.pdf", recursive=True):
            # Extract text from PDF
            text = self.extract_text_from_pdf(file_path)

            # Parse memo structure
            memo = self.parse_memo(text)

            if memo:
                memos.append({
                    "source": file_path,
                    "type": "legal_memo",
                    "question": memo['question_presented'],
                    "answer": memo['brief_answer'],
                    "analysis": memo['discussion'],
                    "full_text": text
                })

        return memos

    def collect_contracts(self, directory_path):
        """Collect contracts for training"""

        contracts = []

        for file_path in glob.glob(f"{directory_path}/**/*.pdf", recursive=True):
            text = self.extract_text_from_pdf(file_path)

            contract = {
                "source": file_path,
                "type": "contract",
                "contract_type": self.classify_contract(text),
                "full_text": text,
                "clauses": self.extract_clauses(text)
            }

            contracts.append(contract)

        return contracts

    def create_instruction_dataset(self, legal_data):
        """Create instruction-tuning dataset"""

        instructions = []

        for item in legal_data:
            if item['type'] == 'legal_memo':
                # Create Q&A pairs
                instructions.append({
                    "instruction": f"Analyze the following legal issue: {item['question']}",
                    "input": "",
                    "output": item['answer']
                })

                instructions.append({
                    "instruction": "Provide a detailed legal analysis of this issue.",
                    "input": item['question'],
                    "output": item['analysis']
                })

            elif item['type'] == 'contract':
                # Create contract analysis tasks
                instructions.append({
                    "instruction": f"Review this {item['contract_type']} and identify key provisions.",
                    "input": item['full_text'][:2000],  # Truncate if too long
                    "output": self.summarize_key_provisions(item['clauses'])
                })

        return Dataset.from_pandas(pd.DataFrame(instructions))

# Usage
collector = LegalDataCollector()

# Collect legal memos
memos = collector.collect_legal_memos("/path/to/legal/memos")

# Collect contracts
contracts = collector.collect_contracts("/path/to/contracts")

# Create instruction dataset
all_data = memos + contracts
instruction_dataset = collector.create_instruction_dataset(all_data)

# Split into train/validation
dataset = instruction_dataset.train_test_split(test_size=0.1)

print(f"Training samples: {len(dataset['train'])}")
print(f"Validation samples: {len(dataset['test'])}")
```

### 1.2 Data Quality and Preprocessing

```python
class LegalDataPreprocessor:
    """Clean and prepare legal data for training"""

    def clean_legal_text(self, text):
        """Clean legal text while preserving important formatting"""

        import re

        # Remove headers/footers (page numbers, etc.)
        text = re.sub(r'\n\s*Page \d+ of \d+\s*\n', '\n', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Preserve legal citations
        # Example: "123 F.3d 456" should stay as is
        text = re.sub(r'(\d+)\s+([A-Z]\.\s*\d+[a-z]?)', r'\1 \2', text)

        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def validate_data_quality(self, dataset):
        """Validate data quality before training"""

        quality_report = {
            "total_examples": len(dataset),
            "empty_inputs": 0,
            "empty_outputs": 0,
            "too_short": 0,
            "too_long": 0,
            "duplicates": 0
        }

        seen_outputs = set()

        for example in dataset:
            # Check for empty inputs/outputs
            if not example['input'].strip() and not example['instruction'].strip():
                quality_report['empty_inputs'] += 1

            if not example['output'].strip():
                quality_report['empty_outputs'] += 1

            # Check length
            if len(example['output'].split()) < 10:
                quality_report['too_short'] += 1

            if len(example['output'].split()) > 2000:
                quality_report['too_long'] += 1

            # Check for duplicates
            if example['output'] in seen_outputs:
                quality_report['duplicates'] += 1
            else:
                seen_outputs.add(example['output'])

        return quality_report

preprocessor = LegalDataPreprocessor()

# Validate data quality
quality_report = preprocessor.validate_data_quality(dataset['train'])
print("Data Quality Report:")
for metric, value in quality_report.items():
    print(f"  {metric}: {value}")
```

## Step 2: Model Selection and Configuration

### 2.1 Choose Base Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Options for base models:

models = {
    "legal_specialized": {
        "name": "nlpaueb/legal-bert-base-uncased",
        "pros": "Pre-trained on legal data",
        "cons": "Smaller, encoder-only"
    },
    "general_powerful": {
        "name": "meta-llama/Llama-2-7b-hf",
        "pros": "Powerful, good at instruction following",
        "cons": "Requires legal fine-tuning"
    },
    "efficient": {
        "name": "mistralai/Mistral-7B-v0.1",
        "pros": "Efficient, high performance",
        "cons": "May need more legal data"
    }
}

# Load base model
model_name = "meta-llama/Llama-2-7b-hf"

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token  # Set padding token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # Automatically distribute across GPUs
    load_in_8bit=True,  # Quantize to save memory
    trust_remote_code=True
)

print(f"Model loaded: {model_name}")
print(f"Model parameters: {model.num_parameters():,}")
```

### 2.2 LoRA Configuration (Parameter-Efficient Fine-tuning)

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Prepare model for LoRA training
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,  # LoRA rank
    lora_alpha=32,  # LoRA alpha
    target_modules=[  # Which modules to apply LoRA to
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA to model
model = get_peft_model(model, lora_config)

# Print trainable parameters
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())

print(f"Trainable parameters: {trainable_params:,}")
print(f"Total parameters: {total_params:,}")
print(f"Percentage trainable: {100 * trainable_params / total_params:.2f}%")
```

## Step 3: Training

### 3.1 Prepare Training Data

```python
def format_instruction_prompt(example):
    """Format examples as instruction prompts"""

    if example['input']:
        prompt = f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
    else:
        prompt = f"""### Instruction:
{example['instruction']}

### Response:
{example['output']}"""

    return {"text": prompt}

# Apply formatting
formatted_dataset = dataset.map(format_instruction_prompt)

# Tokenize
def tokenize_function(examples):
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=2048,  # Adjust based on your data
        padding="max_length"
    )

tokenized_dataset = formatted_dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=formatted_dataset['train'].column_names
)
```

### 3.2 Training Configuration

```python
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling

# Training arguments
training_args = TrainingArguments(
    output_dir="./legal-llm-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,  # Effective batch size: 16
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",

    # Evaluation
    evaluation_strategy="steps",
    eval_steps=100,
    save_steps=100,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",

    # Logging
    logging_dir="./logs",
    logging_steps=10,
    report_to="wandb",  # Track with Weights & Biases

    # Optimization
    fp16=True,  # Mixed precision training
    gradient_checkpointing=True,  # Save memory

    # Other
    remove_unused_columns=False,
    push_to_hub=False
)

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False  # Causal LM, not masked LM
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['test'],
    data_collator=data_collator
)

# Start training
print("Starting training...")
trainer.train()

# Save model
trainer.save_model("./legal-llm-final")
print("Training complete!")
```

### 3.3 Monitor Training

```python
import wandb

# Initialize Weights & Biases
wandb.init(
    project="legal-llm-finetuning",
    name="legal-memo-llama2-7b",
    config={
        "model": model_name,
        "lora_r": 16,
        "learning_rate": 2e-4,
        "epochs": 3,
        "batch_size": 16
    }
)

# Training metrics will be automatically logged
# View at https://wandb.ai
```

## Step 4: Evaluation

### 4.1 Quantitative Evaluation

```python
from transformers import pipeline

class LegalLLMEvaluator:
    """Evaluate fine-tuned legal LLM"""

    def __init__(self, model_path):
        self.generator = pipeline(
            "text-generation",
            model=model_path,
            tokenizer=tokenizer,
            device=0
        )

    def evaluate_legal_qa(self, test_questions):
        """Evaluate on legal Q&A"""

        results = []

        for question in test_questions:
            prompt = f"""### Instruction:
{question['instruction']}

### Response:
"""

            response = self.generator(
                prompt,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )[0]['generated_text']

            # Extract just the response
            response = response.split("### Response:")[-1].strip()

            results.append({
                "question": question['instruction'],
                "expected": question['output'],
                "generated": response,
                "bleu_score": self.calculate_bleu(question['output'], response),
                "rouge_score": self.calculate_rouge(question['output'], response)
            })

        return results

    def calculate_bleu(self, reference, candidate):
        """Calculate BLEU score"""
        from nltk.translate.bleu_score import sentence_bleu

        reference_tokens = reference.split()
        candidate_tokens = candidate.split()

        return sentence_bleu([reference_tokens], candidate_tokens)

    def calculate_rouge(self, reference, candidate):
        """Calculate ROUGE score"""
        from rouge_score import rouge_scorer

        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
        scores = scorer.score(reference, candidate)

        return {
            "rouge1": scores['rouge1'].fmeasure,
            "rouge2": scores['rouge2'].fmeasure,
            "rougeL": scores['rougeL'].fmeasure
        }

# Usage
evaluator = LegalLLMEvaluator("./legal-llm-final")

test_questions = [
    {
        "instruction": "What are the requirements for a valid contract under common law?",
        "output": "A valid contract under common law requires: (1) offer, (2) acceptance..."
    }
]

evaluation_results = evaluator.evaluate_legal_qa(test_questions)

# Calculate average scores
avg_bleu = sum(r['bleu_score'] for r in evaluation_results) / len(evaluation_results)
print(f"Average BLEU Score: {avg_bleu:.3f}")
```

### 4.2 Qualitative Evaluation

```python
def human_evaluation_framework():
    """Framework for attorney evaluation of model outputs"""

    evaluation_criteria = {
        "legal_accuracy": {
            "score_range": "1-5",
            "description": "Is the legal analysis accurate?",
            "1": "Completely incorrect",
            "5": "Fully accurate"
        },
        "completeness": {
            "score_range": "1-5",
            "description": "Does it address all aspects of the question?",
            "1": "Missing key points",
            "5": "Comprehensive"
        },
        "citation_accuracy": {
            "score_range": "1-5",
            "description": "Are legal citations correct?",
            "1": "Hallucinated citations",
            "5": "All citations verified"
        },
        "professional_quality": {
            "score_range": "1-5",
            "description": "Is it attorney work product quality?",
            "1": "Unacceptable",
            "5": "Partner-level quality"
        },
        "harmful_content": {
            "score_range": "Yes/No",
            "description": "Does it contain incorrect legal advice that could cause harm?"
        }
    }

    return evaluation_criteria

# Conduct human evaluation
evaluation_template = """
LEGAL LLM OUTPUT EVALUATION

Question: {question}

Generated Response:
{response}

Please rate the response on:
1. Legal Accuracy (1-5): ___
2. Completeness (1-5): ___
3. Citation Accuracy (1-5): ___
4. Professional Quality (1-5): ___
5. Harmful Content (Yes/No): ___

Comments:
_______________________________
"""
```

## Step 5: Deployment

### 5.1 Optimize for Inference

```python
# Merge LoRA weights with base model for faster inference
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(model_name)
merged_model = PeftModel.from_pretrained(base_model, "./legal-llm-final")
merged_model = merged_model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("./legal-llm-merged")
tokenizer.save_pretrained("./legal-llm-merged")
```

### 5.2 Create API Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Load model once at startup
model = AutoModelForCausalLM.from_pretrained("./legal-llm-merged")
tokenizer = AutoTokenizer.from_pretrained("./legal-llm-merged")

class LegalQuery(BaseModel):
    question: str
    max_length: int = 512

@app.post("/legal-advice")
async def get_legal_advice(query: LegalQuery):
    """Generate legal advice (for internal use only)"""

    prompt = f"""### Instruction:
{query.question}

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=query.max_length,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response.split("### Response:")[-1].strip()

    return {
        "question": query.question,
        "response": response,
        "disclaimer": "AI-generated response. Requires attorney review."
    }

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000
```

## Best Practices

### 1. Data Privacy
- Never train on client confidential data without consent
- Use synthetic data or anonymized examples when possible
- Implement data retention policies

### 2. Validation
- Always validate outputs before use
- Maintain human-in-the-loop for all client-facing work
- Regular accuracy audits

### 3. Continuous Improvement
- Collect feedback from attorneys
- Retrain periodically with new legal developments
- Version control all models

### 4. Documentation
```python
model_card = """
# Legal LLM Model Card

## Model Details
- **Name**: Legal Memorandum Assistant
- **Version**: 1.0
- **Base Model**: Llama-2-7B
- **Fine-tuning Method**: LoRA
- **Training Data**: 10,000 legal memoranda (2018-2023)

## Intended Use
- Assist attorneys in drafting legal memoranda
- Internal use only, requires attorney review
- Not for direct client advice

## Limitations
- May hallucinate legal citations
- Training data through 2023 only
- US law focused (primarily federal and Delaware)

## Validation
- BLEU Score: 0.65
- Attorney Evaluation: 4.2/5.0 average
- Citation Accuracy: 85% (requires verification)
"""
```

---

*Fine-tuning legal LLMs requires careful attention to data quality, validation, and ethical deployment. Always maintain attorney oversight.*
