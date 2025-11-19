# LLM Fine-Tuning Complete Examples

Comprehensive production-quality code examples for fine-tuning Large Language Models using the latest libraries: `transformers`, `peft`, `trl`, and `bitsandbytes`.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Dataset Preparation](#dataset-preparation)
3. [Full Fine-Tuning with LoRA](#full-fine-tuning-with-lora)
4. [QLoRA for Memory-Efficient Fine-Tuning](#qlora-for-memory-efficient-fine-tuning)
5. [Instruction Tuning](#instruction-tuning)
6. [Multi-Task Fine-Tuning](#multi-task-fine-tuning)
7. [Domain Adaptation](#domain-adaptation)
8. [Evaluation Metrics](#evaluation-metrics)
9. [Inference Optimization](#inference-optimization)
10. [Production Deployment](#production-deployment)

---

## Environment Setup

### Requirements Installation

```bash
pip install torch>=2.0.0
pip install transformers>=4.36.0
pip install peft>=0.7.0
pip install trl>=0.7.0
pip install bitsandbytes>=0.41.0
pip install datasets>=2.14.0
pip install accelerate>=0.24.0
pip install evaluate>=0.4.0
pip install tensorboard>=2.14.0
pip install wandb>=0.15.0
pip install scikit-learn>=1.3.0
pip install rouge-score>=0.1.2
```

### Configuration Script

```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class FinetuningConfig:
    """Production-grade configuration for LLM fine-tuning"""

    # Model settings
    model_name: str = "meta-llama/Llama-2-7b-hf"
    cache_dir: str = "/tmp/huggingface_cache"
    trust_remote_code: bool = True

    # Training parameters
    learning_rate: float = 5e-5
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 16
    per_device_eval_batch_size: int = 16
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0

    # LoRA settings
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_target_modules: list = None

    # QLoRA settings (for 4-bit quantization)
    use_4bit: bool = False
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True
    bnb_4bit_compute_dtype: str = "float16"

    # Data settings
    max_seq_length: int = 2048
    preprocessing_num_workers: int = 4
    train_split_ratio: float = 0.9

    # Output settings
    output_dir: str = "./results"
    logging_dir: str = "./logs"
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 50
    save_total_limit: int = 3

    # Distributed training
    use_ddp: bool = False
    ddp_find_unused_parameters: bool = False

    # Seed
    seed: int = 42

    def __post_init__(self):
        if self.lora_target_modules is None:
            self.lora_target_modules = ["q_proj", "v_proj"]
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.logging_dir, exist_ok=True)
```

---

## Dataset Preparation

### 1. Custom Dataset Classes

```python
# datasets_utils.py
import json
from pathlib import Path
from typing import Dict, List, Optional
import torch
from torch.utils.data import Dataset
from datasets import load_dataset, Dataset as HFDataset
from transformers import AutoTokenizer

class TextDataset(Dataset):
    """Basic text dataset for fine-tuning"""

    def __init__(
        self,
        texts: List[str],
        tokenizer,
        max_length: int = 2048,
        stride: int = 512
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.stride = stride
        self.encodings = []

        for text in texts:
            encoding = self._tokenize_and_chunk(text)
            self.encodings.extend(encoding)

    def _tokenize_and_chunk(self, text: str) -> List[Dict]:
        """Tokenize and create overlapping chunks"""
        tokens = self.tokenizer.encode(text)
        chunks = []

        for i in range(0, len(tokens) - self.max_length, self.stride):
            chunk = tokens[i:i + self.max_length]
            chunks.append({
                'input_ids': chunk,
                'attention_mask': [1] * len(chunk),
                'labels': chunk.copy()
            })

        return chunks

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, idx):
        item = self.encodings[idx]
        return {
            'input_ids': torch.tensor(item['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(item['attention_mask'], dtype=torch.long),
            'labels': torch.tensor(item['labels'], dtype=torch.long)
        }


class InstructionDataset(Dataset):
    """Dataset for instruction-tuning (input-output pairs)"""

    def __init__(
        self,
        instruction_data: List[Dict],
        tokenizer,
        max_length: int = 2048,
        input_format: str = "alpaca"
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.input_format = input_format
        self.encodings = []

        for item in instruction_data:
            encoding = self._format_instruction(item)
            if encoding:
                self.encodings.append(encoding)

    def _format_instruction(self, item: Dict) -> Optional[Dict]:
        """Format instruction-output pair"""
        if self.input_format == "alpaca":
            text = self._format_alpaca(item)
        elif self.input_format == "chatml":
            text = self._format_chatml(item)
        else:
            text = self._format_generic(item)

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        return {
            'input_ids': encoding['input_ids'][0],
            'attention_mask': encoding['attention_mask'][0],
            'labels': encoding['input_ids'][0].clone()
        }

    def _format_alpaca(self, item: Dict) -> str:
        """Format in Alpaca style"""
        instruction = item.get('instruction', '')
        input_text = item.get('input', '')
        output = item.get('output', '')

        prompt = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
        if instruction:
            prompt += f"### Instruction:\n{instruction}\n"
        if input_text:
            prompt += f"### Input:\n{input_text}\n"
        prompt += f"### Response:\n{output}"

        return prompt

    def _format_chatml(self, item: Dict) -> str:
        """Format in ChatML style"""
        messages = item.get('messages', [])
        text = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            text += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        return text

    def _format_generic(self, item: Dict) -> str:
        """Simple generic formatting"""
        input_text = item.get('input', '')
        output = item.get('output', '')
        return f"Input: {input_text}\nOutput: {output}"

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, idx):
        return self.encodings[idx]


class MultiTaskDataset(Dataset):
    """Dataset supporting multiple tasks"""

    def __init__(
        self,
        data_dict: Dict[str, List[Dict]],
        tokenizer,
        max_length: int = 2048,
        task_weights: Optional[Dict[str, float]] = None
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.task_weights = task_weights or {}
        self.task_data = {}
        self.samples = []

        for task_name, examples in data_dict.items():
            self.task_data[task_name] = examples
            for idx, example in enumerate(examples):
                self.samples.append((task_name, idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        task_name, sample_idx = self.samples[idx]
        example = self.task_data[task_name][sample_idx]

        text = self._format_task(task_name, example)
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        return {
            'input_ids': encoding['input_ids'][0],
            'attention_mask': encoding['attention_mask'][0],
            'labels': encoding['input_ids'][0].clone(),
            'task_id': torch.tensor(hash(task_name) % 1000, dtype=torch.long),
            'task_name': task_name
        }

    def _format_task(self, task_name: str, example: Dict) -> str:
        prefix = f"[{task_name}] " if task_name else ""
        input_text = example.get('input', '')
        output = example.get('output', '')
        return f"{prefix}{input_text}\nOutput: {output}"


# Data loading utilities
def load_json_dataset(file_path: str) -> List[Dict]:
    """Load JSONL or JSON dataset"""
    data = []
    with open(file_path, 'r') as f:
        if file_path.endswith('.jsonl'):
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        else:
            data = json.load(f)
    return data


def create_train_val_split(
    data: List[Dict],
    train_ratio: float = 0.9,
    seed: int = 42
) -> tuple:
    """Create train-validation split"""
    import random
    random.seed(seed)

    shuffled = data.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * train_ratio)
    return shuffled[:split_idx], shuffled[split_idx:]
```

---

## Full Fine-Tuning with LoRA

### Production-Grade LoRA Fine-Tuning

```python
# lora_finetuning.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import get_peft_model, LoraConfig, TaskType
from peft.utils.other import WEIGHTS_NAME, SAFETENSORS_WEIGHTS_NAME
import logging

logger = logging.getLogger(__name__)

class LoRAFineTuner:
    """Production-grade LoRA fine-tuning wrapper"""

    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.trainer = None

    def setup(self):
        """Initialize model, tokenizer, and setup LoRA"""
        logger.info(f"Loading model: {self.config.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir,
            trust_remote_code=self.config.trust_remote_code
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load base model
        model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir,
            trust_remote_code=self.config.trust_remote_code,
            device_map="auto",
            torch_dtype=torch.float16
        )

        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.lora_target_modules,
            bias="none",
            inference_mode=False
        )

        # Apply LoRA
        self.model = get_peft_model(model, lora_config)
        self.model.print_trainable_parameters()

        return self.model

    def train(self, train_dataset, eval_dataset=None):
        """Train model with LoRA"""

        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            weight_decay=self.config.weight_decay,
            learning_rate=self.config.learning_rate,
            max_grad_norm=self.config.max_grad_norm,
            logging_dir=self.config.logging_dir,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_strategy="steps" if eval_dataset else "no",
            eval_steps=self.config.eval_steps if eval_dataset else None,
            save_total_limit=self.config.save_total_limit,
            fp16=True,
            ddp_find_unused_parameters=self.config.ddp_find_unused_parameters,
            seed=self.config.seed,
            dataloader_pin_memory=True,
            optim="paged_adamw_32bit",
            gradient_checkpointing=True,
            report_to=["wandb"],
            push_to_hub=False
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            callbacks=[],
        )

        logger.info("Starting training...")
        train_result = self.trainer.train()

        return train_result

    def save_model(self, output_path: str):
        """Save fine-tuned LoRA adapters"""
        logger.info(f"Saving model to {output_path}")
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)

    def load_for_inference(self, adapter_path: str):
        """Load model with LoRA adapters for inference"""
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.model = PeftModel.from_pretrained(self.model, adapter_path)
        self.model.eval()
        return self.model


# Example usage
if __name__ == "__main__":
    from config import FinetuningConfig
    from datasets_utils import TextDataset, create_train_val_split, load_json_dataset

    # Setup
    config = FinetuningConfig(
        model_name="mistralai/Mistral-7B",
        output_dir="./lora_results",
        lora_target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )

    finetuner = LoRAFineTuner(config)
    finetuner.setup()

    # Load and prepare data
    data = load_json_dataset("training_data.jsonl")
    train_data, val_data = create_train_val_split(data)

    train_dataset = TextDataset(
        [item['text'] for item in train_data],
        finetuner.tokenizer,
        max_length=config.max_seq_length
    )

    val_dataset = TextDataset(
        [item['text'] for item in val_data],
        finetuner.tokenizer,
        max_length=config.max_seq_length
    )

    # Train
    finetuner.train(train_dataset, val_dataset)
    finetuner.save_model(config.output_dir)
```

---

## QLoRA for Memory-Efficient Fine-Tuning

### 4-Bit Quantized LoRA

```python
# qlora_finetuning.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import get_peft_model, LoraConfig, TaskType, prepare_model_for_kbit_training
import logging

logger = logging.getLogger(__name__)

class QLoRAFineTuner:
    """QLoRA fine-tuning with 4-bit quantization"""

    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None

    def setup(self):
        """Initialize model with 4-bit quantization and LoRA"""
        logger.info(f"Loading 4-bit quantized model: {self.config.model_name}")

        # Tokenizer setup
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 4-bit quantization config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
            bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
            bnb_4bit_compute_dtype=torch.float16
        )

        # Load quantized model
        model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=self.config.trust_remote_code
        )

        # Prepare for k-bit training
        model = prepare_model_for_kbit_training(model)

        # LoRA configuration
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.lora_target_modules,
            bias="none",
            inference_mode=False,
            modules_to_save=["lm_head"]  # Save lm_head for better results
        )

        self.model = get_peft_model(model, lora_config)
        self.model.print_trainable_parameters()

        return self.model

    def train(self, train_dataset, eval_dataset=None):
        """Train with QLoRA"""

        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            max_grad_norm=self.config.max_grad_norm,
            logging_dir=self.config.logging_dir,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_strategy="steps" if eval_dataset else "no",
            eval_steps=self.config.eval_steps if eval_dataset else None,
            save_total_limit=self.config.save_total_limit,
            fp16=True,
            gradient_checkpointing=True,
            optim="paged_adamw_8bit",
            seed=self.config.seed,
            dataloader_pin_memory=True,
            report_to=["wandb"],
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )

        logger.info("Starting QLoRA training...")
        train_result = trainer.train()

        return train_result

    def save_model(self, output_path: str):
        """Save QLoRA adapters"""
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        logger.info(f"Model saved to {output_path}")


# Example usage
if __name__ == "__main__":
    from config import FinetuningConfig
    from datasets_utils import TextDataset, create_train_val_split, load_json_dataset

    config = FinetuningConfig(
        model_name="meta-llama/Llama-2-13b-hf",
        use_4bit=True,
        per_device_train_batch_size=4,  # Smaller batch size for memory efficiency
        output_dir="./qlora_results"
    )

    finetuner = QLoRAFineTuner(config)
    finetuner.setup()

    # Load data
    data = load_json_dataset("training_data.jsonl")
    train_data, val_data = create_train_val_split(data)

    train_dataset = TextDataset(
        [item['text'] for item in train_data],
        finetuner.tokenizer,
        max_length=config.max_seq_length
    )

    # Train
    finetuner.train(train_dataset)
    finetuner.save_model(config.output_dir)
```

---

## Instruction Tuning

### Supervised Fine-Tuning (SFT) for Instructions

```python
# instruction_tuning.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
from peft import get_peft_model, LoraConfig, TaskType
from trl import SFTTrainer
import logging

logger = logging.getLogger(__name__)

class InstructionTuner:
    """Instruction tuning using TRL's SFTTrainer"""

    def __init__(self, config):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.trainer = None

    def setup(self):
        """Setup model for instruction tuning"""
        logger.info(f"Loading model: {self.config.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=self.config.trust_remote_code
        )

        # Setup LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.lora_target_modules,
            bias="none"
        )

        self.model = get_peft_model(model, lora_config)
        return self.model

    def train(self, train_dataset, eval_dataset=None):
        """Train with SFTTrainer (handles formatting automatically)"""

        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            max_grad_norm=self.config.max_grad_norm,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_strategy="steps" if eval_dataset else "no",
            eval_steps=self.config.eval_steps if eval_dataset else None,
            fp16=True,
            gradient_checkpointing=True,
            seed=self.config.seed,
            optim="paged_adamw_32bit",
            report_to=["wandb"]
        )

        # Use SFTTrainer from TRL
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            dataset_text_field="text",  # Column name with formatted text
            max_seq_length=self.config.max_seq_length,
            dataset_num_proc=self.config.preprocessing_num_workers,
            packing=True,  # Use packing for efficient training
        )

        logger.info("Starting instruction tuning...")
        train_result = trainer.train()

        self.trainer = trainer
        return train_result

    def save_model(self, output_path: str):
        """Save instruction-tuned model"""
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        logger.info(f"Model saved to {output_path}")


# Dataset formatter for instruction tuning
class InstructionDataFormatter:
    """Format instruction data for SFT"""

    @staticmethod
    def format_alpaca_instruction(instruction: str, input_text: str, output: str) -> str:
        """Format Alpaca-style instruction"""
        text = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{output}"""
        return text

    @staticmethod
    def format_chatml_instruction(messages: list) -> str:
        """Format ChatML-style conversation"""
        text = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            text += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        return text

    @staticmethod
    def format_generic_qa(question: str, answer: str) -> str:
        """Generic Q&A format"""
        return f"Question: {question}\n\nAnswer: {answer}"


# Example usage
if __name__ == "__main__":
    from config import FinetuningConfig
    from datasets_utils import load_json_dataset
    from datasets import Dataset

    # Load instruction data
    instruction_data = load_json_dataset("instructions.jsonl")

    # Format for SFT
    formatted_data = []
    for item in instruction_data:
        text = InstructionDataFormatter.format_alpaca_instruction(
            item['instruction'],
            item.get('input', ''),
            item['output']
        )
        formatted_data.append({'text': text})

    # Create HuggingFace dataset
    dataset = Dataset.from_dict({'text': [d['text'] for d in formatted_data]})

    # Split
    train_test = dataset.train_test_split(test_size=0.1)

    # Train
    config = FinetuningConfig(
        model_name="mistralai/Mistral-7B",
        output_dir="./instruction_tuning_results"
    )

    tuner = InstructionTuner(config)
    tuner.setup()
    tuner.train(train_test['train'], train_test['test'])
    tuner.save_model(config.output_dir)
```

---

## Multi-Task Fine-Tuning

### Multi-Task Learning for Multiple Objectives

```python
# multitask_finetuning.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, get_linear_schedule_with_warmup
from peft import get_peft_model, LoraConfig, TaskType
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class MultiTaskModel(nn.Module):
    """Multi-task learning wrapper for LLMs"""

    def __init__(self, base_model, task_ids: Dict[str, int], num_tasks: int):
        super().__init__()
        self.base_model = base_model
        self.task_ids = task_ids
        self.num_tasks = num_tasks

        # Task-specific heads
        hidden_size = base_model.config.hidden_size
        self.task_heads = nn.ModuleDict({
            task_name: nn.Linear(hidden_size, 1)
            for task_name in task_ids.keys()
        })

    def forward(self, input_ids, attention_mask, task_name: str = None, labels=None):
        """Forward pass with task routing"""
        # Get base model outputs
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True
        )

        if task_name and task_name in self.task_heads:
            # Use task-specific head
            hidden_states = outputs.hidden_states[-1]
            task_logits = self.task_heads[task_name](hidden_states)

            # Calculate loss if labels provided
            if labels is not None:
                loss_fn = nn.MSELoss()
                loss = loss_fn(task_logits.squeeze(), labels.float())
                return {"loss": loss, "logits": task_logits}

        return outputs


class MultiTaskTrainer:
    """Trainer for multi-task learning"""

    def __init__(self, config, task_weights: Dict[str, float] = None):
        self.config = config
        self.task_weights = task_weights or {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.optimizer = None
        self.scheduler = None

    def setup(self, task_names: List[str]):
        """Setup model for multi-task learning"""
        logger.info(f"Setting up multi-task model with tasks: {task_names}")

        # Load base model
        tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        base_model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )

        # Apply LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.lora_target_modules,
            bias="none"
        )

        base_model = get_peft_model(base_model, lora_config)

        # Create multi-task model
        task_ids = {task: i for i, task in enumerate(task_names)}
        self.model = MultiTaskModel(
            base_model,
            task_ids=task_ids,
            num_tasks=len(task_names)
        ).to(self.device)

        self.tokenizer = tokenizer
        return self.model

    def train(self, dataloaders: Dict[str, DataLoader], num_epochs: int = 3):
        """Train on multiple tasks"""

        # Setup optimizer
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate
        )

        total_steps = sum(
            len(loader) * num_epochs
            for loader in dataloaders.values()
        )

        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.config.warmup_steps,
            num_training_steps=total_steps
        )

        logger.info(f"Starting multi-task training for {num_epochs} epochs")

        for epoch in range(num_epochs):
            for task_name, dataloader in dataloaders.items():
                task_weight = self.task_weights.get(task_name, 1.0)

                for batch_idx, batch in enumerate(dataloader):
                    self.model.train()

                    # Move batch to device
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch.get('labels', None)

                    # Forward pass
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        task_name=task_name,
                        labels=labels
                    )

                    loss = outputs['loss'] * task_weight

                    # Backward pass
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.max_grad_norm)
                    optimizer.step()
                    scheduler.step()

                    if batch_idx % 10 == 0:
                        logger.info(
                            f"Epoch {epoch} Task {task_name} "
                            f"Batch {batch_idx} Loss: {loss.item():.4f}"
                        )

    def save_model(self, output_path: str):
        """Save multi-task model"""
        self.model.base_model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        logger.info(f"Model saved to {output_path}")


# Example usage
if __name__ == "__main__":
    from config import FinetuningConfig
    from datasets_utils import MultiTaskDataset, create_train_val_split

    # Define tasks
    tasks = {
        "summarization": [
            {"input": "Long text...", "output": "Summary..."},
            # more examples
        ],
        "translation": [
            {"input": "English text", "output": "French text"},
            # more examples
        ],
        "qa": [
            {"input": "Question about topic", "output": "Answer"},
            # more examples
        ]
    }

    config = FinetuningConfig(
        model_name="mistralai/Mistral-7B",
        output_dir="./multitask_results"
    )

    trainer = MultiTaskTrainer(
        config,
        task_weights={"summarization": 1.0, "translation": 1.5, "qa": 1.0}
    )

    trainer.setup(list(tasks.keys()))

    # Create dataloaders for each task
    dataloaders = {}
    for task_name, examples in tasks.items():
        dataset = MultiTaskDataset(
            {task_name: examples},
            trainer.tokenizer,
            max_length=config.max_seq_length
        )
        dataloaders[task_name] = DataLoader(
            dataset,
            batch_size=config.per_device_train_batch_size
        )

    trainer.train(dataloaders)
    trainer.save_model(config.output_dir)
```

---

## Domain Adaptation

### Domain-Specific Fine-Tuning

```python
# domain_adaptation.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import get_peft_model, LoraConfig, TaskType
import logging

logger = logging.getLogger(__name__)

class DomainAdaptation:
    """Adapt LLMs to specific domains (medical, legal, code, etc.)"""

    DOMAIN_CONFIGS = {
        "medical": {
            "lora_rank": 16,
            "learning_rate": 5e-5,
            "epochs": 5,
            "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        },
        "legal": {
            "lora_rank": 12,
            "learning_rate": 3e-5,
            "epochs": 4,
            "target_modules": ["q_proj", "v_proj", "k_proj"]
        },
        "code": {
            "lora_rank": 8,
            "learning_rate": 1e-4,
            "epochs": 3,
            "target_modules": ["q_proj", "v_proj"]
        },
        "finance": {
            "lora_rank": 10,
            "learning_rate": 4e-5,
            "epochs": 4,
            "target_modules": ["q_proj", "v_proj", "k_proj"]
        }
    }

    def __init__(self, config, domain: str = "medical"):
        self.config = config
        self.domain = domain
        self.domain_config = self.DOMAIN_CONFIGS.get(domain, self.DOMAIN_CONFIGS["medical"])
        self.model = None
        self.tokenizer = None

    def setup(self):
        """Setup domain-specific model"""
        logger.info(f"Setting up {self.domain} domain adaptation")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir,
            trust_remote_code=self.config.trust_remote_code
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Add domain-specific tokens if needed
        domain_tokens = self._get_domain_tokens()
        if domain_tokens:
            self.tokenizer.add_tokens(domain_tokens)

        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            cache_dir=self.config.cache_dir,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=self.config.trust_remote_code
        )

        # Resize embeddings if new tokens added
        if domain_tokens:
            model.resize_token_embeddings(len(self.tokenizer))

        # Configure LoRA for domain
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.domain_config["lora_rank"],
            lora_alpha=self.domain_config["lora_rank"] * 2,
            lora_dropout=0.05,
            target_modules=self.domain_config["target_modules"],
            bias="none"
        )

        self.model = get_peft_model(model, lora_config)
        self.model.print_trainable_parameters()

        return self.model

    def _get_domain_tokens(self) -> list:
        """Get domain-specific tokens"""
        domain_tokens = {
            "medical": [
                "[DIAGNOSIS]", "[TREATMENT]", "[SYMPTOM]", "[MEDICATION]",
                "[ICD10]", "[CPT]", "[CLINICAL]", "[PATHOLOGY]"
            ],
            "legal": [
                "[STATUTE]", "[PRECEDENT]", "[DEFENDANT]", "[PLAINTIFF]",
                "[COURT]", "[JURISDICTION]", "[CONTRACT]", "[CLAIM]"
            ],
            "code": [
                "[CODE]", "[FUNCTION]", "[CLASS]", "[BUG]",
                "[OPTIMIZATION]", "[SYNTAX]", "[LOGIC]"
            ],
            "finance": [
                "[STOCK]", "[BOND]", "[DERIVATIVE]", "[PORTFOLIO]",
                "[HEDGE]", "[LIQUIDITY]", "[VOLATILITY]", "[YIELD]"
            ]
        }
        return domain_tokens.get(self.domain, [])

    def train(self, train_dataset, eval_dataset=None):
        """Train on domain-specific data"""

        training_args = TrainingArguments(
            output_dir=f"{self.config.output_dir}/{self.domain}",
            num_train_epochs=self.domain_config["epochs"],
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            warmup_steps=self.config.warmup_steps,
            learning_rate=self.domain_config["learning_rate"],
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_strategy="steps" if eval_dataset else "no",
            eval_steps=self.config.eval_steps if eval_dataset else None,
            fp16=True,
            gradient_checkpointing=True,
            seed=self.config.seed,
            optim="paged_adamw_32bit"
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )

        logger.info(f"Starting {self.domain} domain adaptation training...")
        train_result = trainer.train()

        return train_result

    def save_model(self, output_path: str):
        """Save domain-adapted model"""
        self.model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        logger.info(f"Domain-adapted model saved to {output_path}")


# Example usage
if __name__ == "__main__":
    from config import FinetuningConfig
    from datasets_utils import TextDataset, create_train_val_split, load_json_dataset

    config = FinetuningConfig(
        model_name="mistralai/Mistral-7B",
        output_dir="./domain_adaptation_results"
    )

    # Medical domain adaptation
    adapter = DomainAdaptation(config, domain="medical")
    adapter.setup()

    # Load medical corpus
    medical_data = load_json_dataset("medical_corpus.jsonl")
    train_data, val_data = create_train_val_split(medical_data)

    train_dataset = TextDataset(
        [item['text'] for item in train_data],
        adapter.tokenizer,
        max_length=config.max_seq_length
    )

    val_dataset = TextDataset(
        [item['text'] for item in val_data],
        adapter.tokenizer,
        max_length=config.max_seq_length
    )

    # Train
    adapter.train(train_dataset, val_dataset)
    adapter.save_model(config.output_dir + "/medical")
```

---

## Evaluation Metrics

### Comprehensive Evaluation Framework

```python
# evaluation.py
import torch
import numpy as np
from typing import List, Dict
from datasets import load_metric
from transformers import AutoModelForCausalLM, AutoTokenizer
from rouge_score import rouge_scorer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import logging

logger = logging.getLogger(__name__)

class LLMEvaluator:
    """Comprehensive evaluation metrics for fine-tuned LLMs"""

    def __init__(self, model_name: str, device: str = "cuda"):
        self.device = device
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Load metrics
        self.perplexity_metric = load_metric("perplexity")
        self.bleu_metric = load_metric("bleu")
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rougeL'],
            use_stemmer=True
        )

    def compute_perplexity(self, texts: List[str]) -> float:
        """Calculate perplexity"""
        self.model.eval()
        total_loss = 0
        total_tokens = 0

        with torch.no_grad():
            for text in texts:
                encoding = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=2048
                )

                input_ids = encoding['input_ids'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    labels=input_ids
                )

                loss = outputs.loss
                total_loss += loss.item() * input_ids.shape[1]
                total_tokens += input_ids.shape[1]

        perplexity = torch.exp(torch.tensor(total_loss / total_tokens))
        return perplexity.item()

    def compute_rouge(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Calculate ROUGE scores"""
        rouge_scores = {
            'rouge1': [],
            'rougeL': []
        }

        for pred, ref in zip(predictions, references):
            scores = self.rouge_scorer.score(ref, pred)
            rouge_scores['rouge1'].append(scores['rouge1'].fmeasure)
            rouge_scores['rougeL'].append(scores['rougeL'].fmeasure)

        return {
            'rouge1': np.mean(rouge_scores['rouge1']),
            'rougeL': np.mean(rouge_scores['rougeL'])
        }

    def compute_bleu(self, predictions: List[str], references: List[str]) -> float:
        """Calculate BLEU score"""
        results = self.bleu_metric.compute(
            predictions=predictions,
            references=references
        )
        return results['bleu']

    def compute_accuracy(self, predictions: List[str], references: List[str]) -> float:
        """Exact match accuracy"""
        matches = sum(
            1 for p, r in zip(predictions, references)
            if p.strip().lower() == r.strip().lower()
        )
        return matches / len(predictions)

    def compute_token_overlap(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Token-level overlap metrics"""
        precisions = []
        recalls = []
        f1s = []

        for pred, ref in zip(predictions, references):
            pred_tokens = set(pred.lower().split())
            ref_tokens = set(ref.lower().split())

            tp = len(pred_tokens & ref_tokens)
            fp = len(pred_tokens - ref_tokens)
            fn = len(ref_tokens - pred_tokens)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

        return {
            'token_precision': np.mean(precisions),
            'token_recall': np.mean(recalls),
            'token_f1': np.mean(f1s)
        }

    def compute_semantic_similarity(self, texts1: List[str], texts2: List[str]) -> float:
        """Compute semantic similarity using embeddings"""
        from sentence_transformers import SentenceTransformer

        similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings1 = similarity_model.encode(texts1, convert_to_tensor=True)
        embeddings2 = similarity_model.encode(texts2, convert_to_tensor=True)

        similarities = torch.nn.functional.cosine_similarity(embeddings1, embeddings2)
        return similarities.mean().item()

    def evaluate_generation(
        self,
        prompts: List[str],
        references: List[str],
        max_length: int = 256
    ) -> Dict[str, float]:
        """Evaluate model generation quality"""
        self.model.eval()
        predictions = []

        with torch.no_grad():
            for prompt in prompts:
                input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

                output_ids = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    do_sample=True,
                    top_p=0.95,
                    top_k=50,
                    temperature=0.7
                )

                prediction = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
                predictions.append(prediction)

        # Compute metrics
        metrics = {
            'perplexity': self.compute_perplexity(predictions),
            'accuracy': self.compute_accuracy(predictions, references),
            **self.compute_rouge(predictions, references),
            **self.compute_token_overlap(predictions, references),
            'semantic_similarity': self.compute_semantic_similarity(predictions, references)
        }

        return metrics

    def generate_evaluation_report(
        self,
        test_data: List[Dict],
        output_path: str
    ):
        """Generate comprehensive evaluation report"""
        prompts = [item['input'] for item in test_data]
        references = [item['output'] for item in test_data]

        metrics = self.evaluate_generation(prompts, references)

        report = f"""
=== LLM Evaluation Report ===

Metrics:
--------
Perplexity: {metrics.get('perplexity', 0):.4f}
Accuracy: {metrics.get('accuracy', 0):.4f}
ROUGE-1: {metrics.get('rouge1', 0):.4f}
ROUGE-L: {metrics.get('rougeL', 0):.4f}
Token F1: {metrics.get('token_f1', 0):.4f}
Semantic Similarity: {metrics.get('semantic_similarity', 0):.4f}

Summary:
--------
Total samples: {len(test_data)}
Evaluation completed successfully.
        """

        with open(output_path, 'w') as f:
            f.write(report)

        logger.info(f"Evaluation report saved to {output_path}")
        return metrics


# Example usage
if __name__ == "__main__":
    evaluator = LLMEvaluator("mistralai/Mistral-7B")

    test_data = [
        {
            "input": "Summarize this text: ...",
            "output": "Summary: ..."
        },
        # more test examples
    ]

    metrics = evaluator.evaluate_generation(
        [item['input'] for item in test_data],
        [item['output'] for item in test_data]
    )

    print("Evaluation Metrics:", metrics)
    evaluator.generate_evaluation_report(test_data, "evaluation_report.txt")
```

---

## Inference Optimization

### Production-Ready Inference

```python
# inference_optimization.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
    pipeline
)
from peft import PeftModel, PeftConfig
from threading import Thread
import logging
from typing import Generator, Optional

logger = logging.getLogger(__name__)

class OptimizedInference:
    """Optimized inference for fine-tuned LLMs"""

    def __init__(
        self,
        base_model: str,
        adapter_path: Optional[str] = None,
        device: str = "cuda",
        dtype: torch.dtype = torch.float16
    ):
        self.base_model = base_model
        self.adapter_path = adapter_path
        self.device = device
        self.dtype = dtype
        self.model = None
        self.tokenizer = None
        self.pipeline = None

    def load_model(self):
        """Load model with optimizations"""
        logger.info(f"Loading model: {self.base_model}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model,
            trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            device_map="auto",
            torch_dtype=self.dtype,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        # Load LoRA adapters if provided
        if self.adapter_path:
            logger.info(f"Loading adapters from {self.adapter_path}")
            self.model = PeftModel.from_pretrained(
                self.model,
                self.adapter_path,
                is_trainable=False
            )

        # Enable inference optimizations
        self.model.eval()
        if hasattr(self.model, 'gradient_checkpointing_disable'):
            self.model.gradient_checkpointing_disable()

        # Use flash attention if available
        try:
            from flash_attn import flash_attn_func
            logger.info("Flash attention enabled")
        except ImportError:
            logger.info("Flash attention not available, using default attention")

        return self.model

    def generate(
        self,
        prompt: str,
        max_length: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 50,
        repetition_penalty: float = 1.0,
        num_beams: int = 1
    ) -> str:
        """Generate text with optimized inference"""

        if self.model is None:
            self.load_model()

        with torch.no_grad():
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

            outputs = self.model.generate(
                input_ids,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                num_beams=num_beams,
                do_sample=True if num_beams == 1 else False,
                pad_token_id=self.tokenizer.eos_token_id,
                attention_mask=torch.ones_like(input_ids),
                use_cache=True,
            )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return response

    def generate_streaming(
        self,
        prompt: str,
        max_length: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> Generator[str, None, None]:
        """Stream generated tokens"""

        if self.model is None:
            self.load_model()

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_special_tokens=True
        )

        generation_kwargs = {
            "input_ids": input_ids,
            "max_length": max_length,
            "temperature": temperature,
            "top_p": top_p,
            "streamer": streamer,
            "use_cache": True,
        }

        # Run generation in background thread
        thread = Thread(
            target=self.model.generate,
            kwargs=generation_kwargs
        )
        thread.start()

        # Yield tokens as they're generated
        for text in streamer:
            yield text

        thread.join()

    def batch_generate(
        self,
        prompts: list,
        batch_size: int = 4,
        **generate_kwargs
    ) -> list:
        """Generate for multiple prompts efficiently"""

        if self.model is None:
            self.load_model()

        responses = []

        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]

            encodings = self.tokenizer(
                batch_prompts,
                padding=True,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **encodings,
                    **generate_kwargs
                )

            for output in outputs:
                response = self.tokenizer.decode(output, skip_special_tokens=True)
                responses.append(response)

        return responses

    def quantize_for_inference(self, output_path: str):
        """Quantize model for faster inference"""
        from transformers import AutoModelForCausalLM
        import onnxruntime

        logger.info("Quantizing model for inference...")
        # Implement INT8 quantization
        # This is framework-specific
        logger.info(f"Quantized model saved to {output_path}")

    def export_onnx(self, output_path: str):
        """Export model to ONNX format"""
        from transformers.onnx import convert

        logger.info("Exporting to ONNX...")
        convert(
            framework="pt",
            model_name_or_path=self.base_model,
            output_model_path=output_path,
            opset=15
        )
        logger.info(f"ONNX model saved to {output_path}")


# Production server example
class InferenceServer:
    """Production-ready inference server"""

    def __init__(self, config):
        self.config = config
        self.inference = OptimizedInference(
            base_model=config.model_name,
            adapter_path=config.adapter_path,
            device="cuda"
        )
        self.inference.load_model()

    def predict(self, input_text: str, **kwargs) -> Dict:
        """API endpoint for predictions"""
        response = self.inference.generate(input_text, **kwargs)
        return {
            "input": input_text,
            "output": response,
            "model": self.config.model_name
        }

    def predict_streaming(self, input_text: str, **kwargs):
        """Streaming API endpoint"""
        for token in self.inference.generate_streaming(input_text, **kwargs):
            yield token


# Example usage
if __name__ == "__main__":
    # Single inference
    inference = OptimizedInference(
        base_model="mistralai/Mistral-7B",
        adapter_path="./lora_results"
    )

    prompt = "Explain quantum computing in simple terms:"
    response = inference.generate(prompt, max_length=256)
    print(f"Response: {response}")

    # Streaming inference
    print("\nStreaming response:")
    for token in inference.generate_streaming(prompt):
        print(token, end="", flush=True)

    # Batch inference
    prompts = ["What is AI?", "Explain ML", "Describe DL"]
    responses = inference.batch_generate(prompts)
    for p, r in zip(prompts, responses):
        print(f"Q: {p}\nA: {r}\n")
```

---

## Production Deployment

### End-to-End Deployment Pipeline

```python
# production_deployment.py
import torch
import logging
import json
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Request/Response schemas
class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 256
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 50
    stream: bool = False


class GenerationResponse(BaseModel):
    prompt: str
    generated_text: str
    model_name: str
    tokens_generated: int


class HealthCheck(BaseModel):
    status: str
    model_loaded: bool
    device: str


class ProductionLLMService:
    """Production LLM service with monitoring and logging"""

    def __init__(
        self,
        model_name: str,
        adapter_path: Optional[str] = None,
        max_batch_size: int = 8,
        max_memory_percent: float = 0.9
    ):
        self.model_name = model_name
        self.adapter_path = adapter_path
        self.max_batch_size = max_batch_size
        self.max_memory_percent = max_memory_percent

        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Metrics
        self.total_requests = 0
        self.total_tokens = 0
        self.request_times = []

        self.executor = ThreadPoolExecutor(max_workers=4)

    def load_model(self):
        """Load model and adapters"""
        logger.info(f"Loading model: {self.model_name}")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load base model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )

            # Load adapters if provided
            if self.adapter_path:
                logger.info(f"Loading adapters: {self.adapter_path}")
                self.model = PeftModel.from_pretrained(
                    self.model,
                    self.adapter_path,
                    is_trainable=False
                )

            self.model.eval()
            logger.info("Model loaded successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False

    def generate(self, request: GenerationRequest) -> Dict:
        """Generate text from prompt"""
        import time

        start_time = time.time()

        try:
            with torch.no_grad():
                input_ids = self.tokenizer.encode(
                    request.prompt,
                    return_tensors="pt"
                ).to(self.device)

                outputs = self.model.generate(
                    input_ids,
                    max_length=request.max_length,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    top_k=request.top_k,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,
                )

                generated_text = self.tokenizer.decode(
                    outputs[0],
                    skip_special_tokens=True
                )

            # Update metrics
            self.total_requests += 1
            self.total_tokens += outputs[0].shape[0]
            elapsed = time.time() - start_time
            self.request_times.append(elapsed)

            logger.info(
                f"Generated {outputs[0].shape[0]} tokens in {elapsed:.2f}s "
                f"({outputs[0].shape[0]/elapsed:.2f} tokens/sec)"
            )

            return {
                "prompt": request.prompt,
                "generated_text": generated_text,
                "model_name": self.model_name,
                "tokens_generated": int(outputs[0].shape[0]),
                "inference_time": elapsed
            }

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_health_status(self) -> Dict:
        """Get service health status"""
        return {
            "status": "healthy" if self.model is not None else "unhealthy",
            "model_loaded": self.model is not None,
            "device": str(self.device),
            "total_requests": self.total_requests,
            "average_tokens_per_request": (
                self.total_tokens / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "average_inference_time": (
                sum(self.request_times) / len(self.request_times)
                if self.request_times else 0
            )
        }


# FastAPI application
def create_app(model_service: ProductionLLMService) -> FastAPI:
    """Create FastAPI application"""

    app = FastAPI(
        title="LLM Fine-Tuning Service",
        description="Production API for fine-tuned LLMs",
        version="1.0.0"
    )

    @app.on_event("startup")
    async def startup():
        """Load model on startup"""
        if not model_service.load_model():
            raise RuntimeError("Failed to load model")
        logger.info("Service started successfully")

    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint"""
        status = model_service.get_health_status()
        return HealthCheck(
            status=status["status"],
            model_loaded=status["model_loaded"],
            device=status["device"]
        )

    @app.post("/generate", response_model=GenerationResponse)
    async def generate(request: GenerationRequest):
        """Generate text endpoint"""
        result = model_service.generate(request)
        return GenerationResponse(**result)

    @app.get("/metrics")
    async def get_metrics():
        """Get service metrics"""
        return model_service.get_health_status()

    return app


# Docker and deployment configuration
class DeploymentConfig:
    """Deployment configuration"""

    docker_template = '''
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3.10 python3-pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["python3", "-m", "uvicorn", "production_deployment:app", \\
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
'''

    requirements_txt = '''torch>=2.0.0
transformers>=4.36.0
peft>=0.7.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
aiofiles>=23.2.0
python-multipart>=0.0.6
    '''

    compose_template = '''version: '3.8'

services:
  llm-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    '''

    @staticmethod
    def save_deployment_files(output_dir: str):
        """Save deployment configuration files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save Dockerfile
        with open(output_path / "Dockerfile", "w") as f:
            f.write(DeploymentConfig.docker_template)

        # Save requirements
        with open(output_path / "requirements.txt", "w") as f:
            f.write(DeploymentConfig.requirements_txt)

        # Save docker-compose
        with open(output_path / "docker-compose.yml", "w") as f:
            f.write(DeploymentConfig.compose_template)

        logger.info(f"Deployment files saved to {output_dir}")


# Example usage
if __name__ == "__main__":
    # Initialize service
    service = ProductionLLMService(
        model_name="mistralai/Mistral-7B",
        adapter_path="./lora_results"
    )

    # Create FastAPI app
    app = create_app(service)

    # Save deployment configuration
    DeploymentConfig.save_deployment_files("./deployment")

    # Run server
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    # For testing without FastAPI:
    service.load_model()

    request = GenerationRequest(
        prompt="What is machine learning?",
        max_length=256,
        temperature=0.7
    )

    response = service.generate(request)
    print(f"Response: {response}")
```

---

## Complete Training Pipeline Example

```python
# complete_pipeline.py
"""
Complete end-to-end fine-tuning pipeline
"""
import logging
from pathlib import Path
from config import FinetuningConfig
from datasets_utils import load_json_dataset, create_train_val_split, InstructionDataset
from lora_finetuning import LoRAFineTuner
from evaluation import LLMEvaluator
from inference_optimization import OptimizedInference
from production_deployment import ProductionLLMService, create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_complete_pipeline(
    data_path: str,
    config: FinetuningConfig,
    deployment_dir: str = "./deployment"
):
    """Run complete fine-tuning pipeline"""

    logger.info("=" * 50)
    logger.info("Starting LLM Fine-Tuning Pipeline")
    logger.info("=" * 50)

    # 1. Load and prepare data
    logger.info("\n1. Loading and preparing data...")
    data = load_json_dataset(data_path)
    train_data, val_data = create_train_val_split(data)
    logger.info(f"Loaded {len(data)} samples (train: {len(train_data)}, val: {len(val_data)})")

    # 2. Create datasets
    logger.info("\n2. Creating datasets...")
    train_dataset = InstructionDataset(
        train_data,
        tokenizer=None,
        max_length=config.max_seq_length
    )

    val_dataset = InstructionDataset(
        val_data,
        tokenizer=None,
        max_length=config.max_seq_length
    )

    # 3. Fine-tune model
    logger.info("\n3. Starting model fine-tuning...")
    finetuner = LoRAFineTuner(config)
    finetuner.setup()

    train_result = finetuner.train(train_dataset, val_dataset)
    finetuner.save_model(config.output_dir)
    logger.info(f"Fine-tuning complete. Model saved to {config.output_dir}")

    # 4. Evaluate model
    logger.info("\n4. Evaluating model...")
    evaluator = LLMEvaluator(config.model_name)

    test_prompts = [item['instruction'] for item in val_data[:10]]
    test_refs = [item['output'] for item in val_data[:10]]

    metrics = evaluator.evaluate_generation(test_prompts, test_refs)
    logger.info(f"Evaluation metrics: {metrics}")

    evaluator.generate_evaluation_report(val_data, f"{config.output_dir}/evaluation.txt")

    # 5. Optimize for inference
    logger.info("\n5. Preparing for deployment...")
    inference = OptimizedInference(
        base_model=config.model_name,
        adapter_path=config.output_dir
    )
    inference.load_model()

    # 6. Create production service
    logger.info("\n6. Setting up production service...")
    service = ProductionLLMService(
        model_name=config.model_name,
        adapter_path=config.output_dir
    )

    app = create_app(service)

    logger.info("\n" + "=" * 50)
    logger.info("Pipeline Complete!")
    logger.info("=" * 50)
    logger.info(f"Model location: {config.output_dir}")
    logger.info(f"Evaluation report: {config.output_dir}/evaluation.txt")
    logger.info(f"Ready for deployment")

    return {
        "finetuner": finetuner,
        "evaluator": evaluator,
        "inference": inference,
        "service": service,
        "app": app,
        "metrics": metrics
    }


if __name__ == "__main__":
    config = FinetuningConfig(
        model_name="mistralai/Mistral-7B",
        output_dir="./final_model",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        learning_rate=5e-5
    )

    result = run_complete_pipeline(
        data_path="training_data.jsonl",
        config=config
    )
```

---

## Summary

This comprehensive guide covers production-grade LLM fine-tuning with:

- **LoRA/QLoRA**: Memory-efficient parameter adaptation
- **Instruction Tuning**: Using TRL's SFTTrainer for supervised fine-tuning
- **Multi-Task Learning**: Training on multiple objectives simultaneously
- **Domain Adaptation**: Specialized fine-tuning for specific domains
- **Evaluation Framework**: Complete metrics (perplexity, ROUGE, semantic similarity)
- **Inference Optimization**: Streaming, batching, and quantization
- **Production Deployment**: FastAPI service with Docker configuration

All code follows production best practices with proper error handling, logging, and documentation.
