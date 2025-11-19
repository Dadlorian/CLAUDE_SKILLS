# Comprehensive LLM Reference Guide

A professional guide to Large Language Models covering architecture, fine-tuning, alignment, deployment, and best practices from industry leaders.

**Table of Contents**
1. [LLM Architecture Overview](#llm-architecture-overview)
2. [Fine-Tuning Strategies](#fine-tuning-strategies)
3. [RLHF and Alignment](#rlhf-and-alignment)
4. [Prompt Engineering](#prompt-engineering)
5. [RAG: Retrieval-Augmented Generation](#rag-retrieval-augmented-generation)
6. [LLM Evaluation](#llm-evaluation)
7. [Inference Optimization](#inference-optimization)
8. [Production Deployment](#production-deployment)
9. [Best Practices](#best-practices)

---

## LLM Architecture Overview

### Transformer Foundation

All modern LLMs are built on the Transformer architecture (Vaswani et al., 2017):

```python
import torch
import torch.nn as nn
import math

class TransformerBlock(nn.Module):
    """Core Transformer building block with self-attention and feed-forward networks"""

    def __init__(self, d_model=768, num_heads=12, d_ff=3072, dropout=0.1):
        super().__init__()

        # Multi-head self-attention
        self.attention = nn.MultiheadAttention(
            d_model, num_heads, dropout=dropout, batch_first=True
        )

        # Feed-forward network (MLPs)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model)
        )

        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Multi-head self-attention with residual connection
        attn_output, _ = self.attention(x, x, x, attn_mask=mask)
        x = x + self.dropout(attn_output)
        x = self.norm1(x)

        # Feed-forward with residual connection
        ffn_output = self.ffn(x)
        x = x + self.dropout(ffn_output)
        x = self.norm2(x)

        return x


class RotaryPositionalEmbedding(nn.Module):
    """RoPE - Rotary Position Embedding (used by LLaMA, Mistral)"""

    def __init__(self, d_model, max_seq_len=2048):
        super().__init__()
        self.d_model = d_model

        # Pre-compute rotation matrices
        inv_freq = 1.0 / (10000 ** (torch.arange(0, d_model, 2).float() / d_model))
        self.register_buffer('inv_freq', inv_freq)

    def forward(self, x, seq_len):
        """Apply rotary embeddings to query and key projections"""
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum('i,j->ij', t, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)

        # Apply complex rotation
        cos = emb.cos()
        sin = emb.sin()

        x1 = x[..., : self.d_model // 2]
        x2 = x[..., self.d_model // 2 :]

        return x1 * cos + x2 * sin
```

### GPT Architecture

**Decoder-only transformer** optimized for autoregressive text generation:

```python
class GPTBlock(nn.Module):
    """GPT-style decoder block with causal masking"""

    def __init__(self, config):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model)
        self.attn = nn.MultiheadAttention(
            config.d_model,
            config.num_heads,
            dropout=config.dropout,
            batch_first=True
        )
        self.ln2 = nn.LayerNorm(config.d_model)
        self.mlp = nn.Sequential(
            nn.Linear(config.d_model, config.d_ff),
            nn.GELU(),
            nn.Linear(config.d_ff, config.d_model),
            nn.Dropout(config.dropout)
        )

    def forward(self, x, causal_mask=None):
        # Pre-normalization (GPT-2 style)
        attn_out, _ = self.attn(
            self.ln1(x), self.ln1(x), self.ln1(x),
            attn_mask=causal_mask,
            is_causal=True
        )
        x = x + attn_out

        x = x + self.mlp(self.ln2(x))
        return x


class GPTLikeModel(nn.Module):
    """GPT-2/GPT-3 style language model"""

    def __init__(self, vocab_size=50257, d_model=768, num_layers=12, **kwargs):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(2048, d_model)

        self.layers = nn.ModuleList([
            GPTBlock({'d_model': d_model, 'num_heads': 12, 'dropout': 0.1, 'd_ff': d_model * 4})
            for _ in range(num_layers)
        ])

        self.ln_final = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def forward(self, input_ids, causal_mask=None):
        seq_len = input_ids.shape[1]

        # Embeddings
        x = self.embedding(input_ids)
        x = x + self.position_embedding(torch.arange(seq_len, device=input_ids.device))

        # Transformer layers
        for layer in self.layers:
            x = layer(x, causal_mask=causal_mask)

        # Output
        x = self.ln_final(x)
        logits = self.lm_head(x)

        return logits
```

### LLaMA Architecture

**Key differences from GPT:**
- RoPE (Rotary Position Embeddings)
- Pre-normalization with RMSNorm
- SwiGLU activation
- Grouped-query attention (GQA) for efficiency

```python
class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization (LLaMA)"""

    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm_x = x / (torch.norm(x, dim=-1, keepdim=True) + self.eps)
        return norm_x * self.weight


class SwiGLU(nn.Module):
    """SwiGLU activation function (LLaMA)"""

    def forward(self, x):
        x, gate = x.chunk(2, dim=-1)
        return x * torch.nn.functional.silu(gate)


class GroupedQueryAttention(nn.Module):
    """Grouped-query attention for efficiency (LLaMA 2)"""

    def __init__(self, d_model, num_heads, num_kv_heads=None, dropout=0.0):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads or num_heads

        assert num_heads % self.num_kv_heads == 0
        self.num_kv_groups = num_heads // self.num_kv_heads

        self.head_dim = d_model // num_heads

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model // self.num_kv_groups)
        self.v_proj = nn.Linear(d_model, d_model // self.num_kv_groups)
        self.o_proj = nn.Linear(d_model, d_model)

    def forward(self, x):
        batch_size, seq_len, _ = x.shape

        q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(batch_size, seq_len, self.num_kv_heads, self.head_dim)
        v = self.v_proj(x).view(batch_size, seq_len, self.num_kv_heads, self.head_dim)

        # Repeat k, v for each query group
        k = k.repeat_interleave(self.num_kv_groups, dim=2)
        v = v.repeat_interleave(self.num_kv_groups, dim=2)

        # Standard attention
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn_weights = torch.softmax(scores, dim=-1)
        attn_output = torch.matmul(attn_weights, v)

        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, seq_len, self.d_model)

        output = self.o_proj(attn_output)
        return output


class LLaMABlock(nn.Module):
    """LLaMA transformer block"""

    def __init__(self, d_model=4096, num_heads=32, num_kv_heads=8, d_ff=11008):
        super().__init__()

        self.attention_norm = RMSNorm(d_model)
        self.attention = GroupedQueryAttention(d_model, num_heads, num_kv_heads)

        self.ffn_norm = RMSNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 2 * d_ff),
            SwiGLU(),
            nn.Linear(d_ff, d_model)
        )

    def forward(self, x):
        # Pre-norm attention
        attn_out = self.attention(self.attention_norm(x))
        x = x + attn_out

        # Pre-norm FFN
        ffn_out = self.ffn(self.ffn_norm(x))
        x = x + ffn_out

        return x
```

### Mistral Architecture

**Efficient design with:**
- Sliding Window Attention (SWA) - reduces memory to O(n) vs O(n²)
- Grouped-query attention
- Byte-pair encoding
- Modern innovations for 7B model surpassing 13B models

```python
class SlidingWindowAttention(nn.Module):
    """Sliding Window Attention (Mistral)"""

    def __init__(self, d_model, num_heads, window_size=4096):
        super().__init__()
        self.window_size = window_size
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.o_proj = nn.Linear(d_model, d_model)

    def forward(self, x, attention_mask=None):
        batch_size, seq_len, _ = x.shape

        q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        v = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)

        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        # Apply sliding window
        output = []
        for i in range(seq_len):
            start = max(0, i - self.window_size)
            window_k = k[:, :, start:i+1, :]
            window_v = v[:, :, start:i+1, :]

            scores = torch.matmul(q[:, :, i:i+1, :], window_k.transpose(-2, -1))
            scores = scores / math.sqrt(self.head_dim)

            if attention_mask is not None:
                scores = scores + attention_mask[:, :, i:i+1, start:i+1]

            attn = torch.softmax(scores, dim=-1)
            attn_out = torch.matmul(attn, window_v)
            output.append(attn_out)

        output = torch.cat(output, dim=2).transpose(1, 2).contiguous()
        output = output.view(batch_size, seq_len, self.d_model)

        return self.o_proj(output)
```

---

## Fine-Tuning Strategies

### 1. Full Fine-Tuning

Update all model parameters on your task:

```python
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

class TextDataset(Dataset):
    """Dataset for fine-tuning"""

    def __init__(self, texts, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.texts = texts
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        encodings = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encodings['input_ids'].squeeze()
        attention_mask = encodings['attention_mask'].squeeze()

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': input_ids.clone()
        }


def full_fine_tune(model, train_loader, num_epochs=3, learning_rate=2e-5, device='cuda'):
    """Full parameter fine-tuning"""

    optimizer = AdamW(model.parameters(), lr=learning_rate)
    model = model.to(device)

    model.train()

    for epoch in range(num_epochs):
        total_loss = 0
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")

        for batch in progress_bar:
            optimizer.zero_grad()

            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            # Forward pass
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss

            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            progress_bar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1} - Average Loss: {avg_loss:.4f}")

    return model


# Usage
# model = GPTLikeModel(vocab_size=50257)
# train_dataset = TextDataset(texts, tokenizer)
# train_loader = DataLoader(train_dataset, batch_size=8)
# model = full_fine_tune(model, train_loader)
```

### 2. LoRA (Low-Rank Adaptation)

Efficient fine-tuning by updating low-rank decompositions:

```python
class LoRALinear(nn.Module):
    """LoRA-adapted Linear layer"""

    def __init__(self, in_features, out_features, lora_rank=8, lora_alpha=16):
        super().__init__()

        self.in_features = in_features
        self.out_features = out_features
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha

        # Original weight (frozen)
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.register_parameter('bias', None)

        # LoRA weights
        self.lora_a = nn.Parameter(torch.randn(in_features, lora_rank) * 0.01)
        self.lora_b = nn.Parameter(torch.zeros(lora_rank, out_features))

        # Scaling factor
        self.scale = lora_alpha / lora_rank

    def forward(self, x):
        # Original weight matrix output
        y = torch.nn.functional.linear(x, self.weight)

        # Add LoRA adaptation
        lora_out = torch.matmul(x, self.lora_a)
        lora_out = torch.matmul(lora_out, self.lora_b)
        lora_out = lora_out * self.scale

        return y + lora_out


class LoRAModel(nn.Module):
    """Wrap existing model with LoRA"""

    def __init__(self, base_model, lora_rank=8, lora_alpha=16, lora_layers=None):
        super().__init__()
        self.base_model = base_model

        # Replace linear layers in specified layers with LoRA
        self.apply_lora(lora_rank, lora_alpha, lora_layers)

    def apply_lora(self, lora_rank, lora_alpha, lora_layers=None):
        """Apply LoRA to model layers"""
        for name, module in self.base_model.named_modules():
            if isinstance(module, nn.Linear):
                # Check if this layer should get LoRA
                if lora_layers is None or any(layer in name for layer in lora_layers):
                    # Create LoRA wrapper
                    lora_linear = LoRALinear(
                        module.in_features,
                        module.out_features,
                        lora_rank=lora_rank,
                        lora_alpha=lora_alpha
                    )

                    # Copy original weights
                    lora_linear.weight.data.copy_(module.weight.data)

                    # Replace in parent
                    parent_name, child_name = name.rsplit('.', 1)
                    parent = dict(self.base_model.named_modules())[parent_name]
                    setattr(parent, child_name, lora_linear)

    def forward(self, *args, **kwargs):
        return self.base_model(*args, **kwargs)


def get_lora_parameters(model):
    """Get only LoRA parameters for optimization"""
    for name, param in model.named_parameters():
        if 'lora_' in name:
            yield param


# Usage
# base_model = GPTLikeModel(vocab_size=50257)
# lora_model = LoRAModel(base_model, lora_rank=8)
#
# # Only train LoRA parameters
# optimizer = AdamW(get_lora_parameters(lora_model), lr=1e-4)
```

### 3. QLoRA (Quantized LoRA)

Combine quantization with LoRA for memory-efficient fine-tuning:

```python
import bitsandbytes as bnb

class QLoRAConfig:
    """Configuration for QLoRA fine-tuning"""

    def __init__(
        self,
        lora_rank=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bnb_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype="float16"
    ):
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.bnb_4bit = bnb_4bit
        self.bnb_4bit_quant_type = bnb_4bit_quant_type
        self.bnb_4bit_use_double_quant = bnb_4bit_use_double_quant
        self.bnb_4bit_compute_dtype = bnb_4bit_compute_dtype


def quantize_and_apply_lora(model, qlora_config):
    """
    Apply 4-bit quantization and LoRA adaptation

    Requirements:
        pip install bitsandbytes peft
    """
    from peft import get_peft_model, LoraConfig, TaskType

    # LoRA configuration
    lora_config = LoraConfig(
        r=qlora_config.lora_rank,
        lora_alpha=qlora_config.lora_alpha,
        lora_dropout=qlora_config.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=["q_proj", "v_proj"],  # Adapt to your model
    )

    # Apply LoRA
    model = get_peft_model(model, lora_config)

    return model


# Example with Hugging Face transformers
def qlora_fine_tune_example():
    """
    Complete QLoRA fine-tuning pipeline

    pip install transformers peft bitsandbytes
    """
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
        Trainer
    )

    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype="float16"
    )

    # Load model with 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b",
        quantization_config=bnb_config,
        device_map="auto"
    )

    # Apply LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )

    model = get_peft_model(model, lora_config)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./qlora-model",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_steps=10,
        save_steps=100,
        max_grad_norm=0.3,
        optim="paged_adamw_8bit",  # Memory efficient
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=None,  # Your dataset here
    )

    return trainer


print("QLoRA Example - Check docstring for complete setup")
```

### 4. Prefix Tuning

Prepend learnable tokens to input:

```python
class PrefixTuning(nn.Module):
    """Prefix Tuning - prepend learnable tokens"""

    def __init__(self, prefix_len=20, embed_dim=768, num_layers=12):
        super().__init__()

        self.prefix_len = prefix_len
        self.embed_dim = embed_dim
        self.num_layers = num_layers

        # Learnable prefix embeddings
        self.prefix_embeddings = nn.Parameter(
            torch.randn(num_layers, prefix_len, embed_dim)
        )

        # Optional MLP projection for smoother learning
        self.prefix_mlp = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.Tanh(),
            nn.Linear(embed_dim, embed_dim)
        )

    def forward(self, hidden_states, layer_idx):
        """
        Add prefix to hidden states at specific layer

        Args:
            hidden_states: (batch_size, seq_len, embed_dim)
            layer_idx: which transformer layer

        Returns:
            Concatenated [prefix, hidden_states]
        """
        batch_size = hidden_states.shape[0]

        # Get prefix for this layer
        prefix = self.prefix_embeddings[layer_idx]  # (prefix_len, embed_dim)

        # Project through MLP
        prefix = self.prefix_mlp(prefix)

        # Expand for batch
        prefix = prefix.unsqueeze(0).expand(batch_size, -1, -1)

        # Concatenate with input
        return torch.cat([prefix, hidden_states], dim=1)


class PrefixTunedModel(nn.Module):
    """Base model with prefix tuning"""

    def __init__(self, base_model, prefix_len=20):
        super().__init__()
        self.base_model = base_model
        self.prefix_tuning = PrefixTuning(
            prefix_len=prefix_len,
            embed_dim=base_model.d_model,
            num_layers=len(base_model.layers)
        )

        # Freeze base model
        for param in self.base_model.parameters():
            param.requires_grad = False

    def forward(self, input_ids):
        # Get embeddings
        hidden_states = self.base_model.embedding(input_ids)

        # Apply prefix at each layer
        for layer_idx, layer in enumerate(self.base_model.layers):
            hidden_states = self.prefix_tuning(hidden_states, layer_idx)
            hidden_states = layer(hidden_states)

        logits = self.base_model.lm_head(hidden_states)
        return logits
```

### 5. Prompt Tuning

Optimize continuous task-specific prompts:

```python
class PromptTuning(nn.Module):
    """Prompt Tuning - learn continuous prompts"""

    def __init__(self, num_prompts=10, prompt_len=20, embed_dim=768):
        super().__init__()

        self.num_prompts = num_prompts
        self.prompt_len = prompt_len
        self.embed_dim = embed_dim

        # Learnable prompts for each task
        self.prompts = nn.Parameter(
            torch.randn(num_prompts, prompt_len, embed_dim)
        )

        # Initialize from reasonable distribution
        nn.init.normal_(self.prompts, std=0.02)

    def get_prompt(self, prompt_idx):
        """Get prompt embeddings for specific task"""
        return self.prompts[prompt_idx]

    def forward(self, hidden_states, prompt_idx):
        """
        Prepend learned prompt to input

        Args:
            hidden_states: (batch_size, seq_len, embed_dim)
            prompt_idx: which prompt to use

        Returns:
            (batch_size, prompt_len + seq_len, embed_dim)
        """
        batch_size = hidden_states.shape[0]

        # Get prompt
        prompt = self.get_prompt(prompt_idx)  # (prompt_len, embed_dim)
        prompt = prompt.unsqueeze(0).expand(batch_size, -1, -1)

        # Concatenate
        return torch.cat([prompt, hidden_states], dim=1)


# Training with prompt tuning
def train_with_prompt_tuning(model, tokenizer, train_loader, prompt_tuning, task_id=0):
    """Train with prompt tuning"""

    optimizer = torch.optim.AdamW(prompt_tuning.parameters(), lr=1e-3)

    for epoch in range(3):
        for batch in train_loader:
            optimizer.zero_grad()

            # Get embeddings
            input_ids = batch['input_ids']
            embeddings = model.embedding(input_ids)

            # Apply prompt tuning
            embeddings = prompt_tuning(embeddings, task_id)

            # Forward through model
            outputs = model(embeddings)
            loss = compute_loss(outputs, batch['labels'])

            loss.backward()
            optimizer.step()
```

---

## RLHF and Alignment

### RLHF (Reinforcement Learning from Human Feedback)

Four-stage process: SFT → RM training → PPO → Evaluation

```python
import torch
import torch.nn as nn
from torch.distributions import Categorical

class RewardModel(nn.Module):
    """Reward Model for RLHF"""

    def __init__(self, base_model, hidden_size=768):
        super().__init__()

        self.base_model = base_model
        self.value_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )

    def forward(self, input_ids, attention_mask=None):
        # Get last hidden state
        outputs = self.base_model(input_ids, attention_mask=attention_mask)
        hidden_states = outputs[:, -1, :]  # Take last token

        # Predict reward
        reward = self.value_head(hidden_states)
        return reward.squeeze(-1)


def train_reward_model(model, train_pairs, learning_rate=2e-5):
    """
    Train reward model on preference pairs

    train_pairs: List[{
        'chosen': input_ids_chosen,
        'rejected': input_ids_rejected
    }]
    """
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    for epoch in range(3):
        for pair in train_pairs:
            chosen_ids = pair['chosen']
            rejected_ids = pair['rejected']

            # Forward pass
            reward_chosen = model(chosen_ids)
            reward_rejected = model(rejected_ids)

            # Ranking loss: maximize (reward_chosen - reward_rejected)
            loss = -torch.nn.functional.logsigmoid(reward_chosen - reward_rejected).mean()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model


class PPOTrainer:
    """Proximal Policy Optimization for LLM alignment"""

    def __init__(self, model, reward_model, learning_rate=1e-5, epsilon=0.2):
        self.model = model
        self.reward_model = reward_model
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        self.epsilon = epsilon  # PPO clipping parameter

    def compute_advantages(self, rewards, values, gamma=0.99, lambda_=0.95):
        """Compute GAE (Generalized Advantage Estimation)"""
        advantages = []
        gae = 0

        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]

            delta = rewards[t] + gamma * next_value - values[t]
            gae = delta + gamma * lambda_ * gae
            advantages.insert(0, gae)

        return torch.tensor(advantages)

    def ppo_step(self, rollout_data, num_epochs=4, batch_size=32):
        """
        PPO optimization step

        rollout_data: {
            'observations': sequence of states,
            'actions': sequence of actions,
            'log_probs': log probabilities of taken actions,
            'rewards': trajectory rewards,
            'values': value function estimates
        }
        """
        observations = rollout_data['observations']
        actions = rollout_data['actions']
        old_log_probs = rollout_data['log_probs']
        rewards = rollout_data['rewards']
        values = rollout_data['values']

        # Compute advantages
        advantages = self.compute_advantages(rewards.numpy(), values.numpy())
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # PPO epochs
        for epoch in range(num_epochs):
            # Shuffle and batch
            indices = torch.randperm(len(observations))

            for i in range(0, len(observations), batch_size):
                batch_indices = indices[i:i + batch_size]

                obs_batch = observations[batch_indices]
                action_batch = actions[batch_indices]
                old_logp_batch = old_log_probs[batch_indices]
                adv_batch = advantages[batch_indices]

                # Forward pass
                logits = self.model(obs_batch)
                dist = Categorical(logits=logits)

                # New log probabilities
                new_log_probs = dist.log_prob(action_batch)

                # Probability ratio
                ratio = torch.exp(new_log_probs - old_logp_batch)

                # Clipped surrogate objective
                surr1 = ratio * adv_batch
                surr2 = torch.clamp(ratio, 1 - self.epsilon, 1 + self.epsilon) * adv_batch
                loss = -torch.min(surr1, surr2).mean()

                # Optimization step
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()


# Complete RLHF pipeline
def rlhf_pipeline(base_model, tokenizer, human_feedback_data):
    """
    Full RLHF pipeline

    human_feedback_data: List of {
        'prompt': str,
        'chosen_completion': str,
        'rejected_completion': str
    }
    """
    print("Stage 1: Supervised Fine-Tuning (SFT)")
    # ... SFT code (see fine-tuning section)

    print("Stage 2: Train Reward Model")
    reward_model = RewardModel(base_model)
    reward_model = train_reward_model(reward_model, human_feedback_data)

    print("Stage 3: PPO Training")
    ppo_trainer = PPOTrainer(base_model, reward_model)
    # ... PPO training loop

    print("Stage 4: Evaluation")
    # ... Evaluation on benchmark

    return base_model
```

### DPO (Direct Preference Optimization)

Simpler alignment without explicit reward model:

```python
class DPOTrainer:
    """Direct Preference Optimization - simpler than RLHF"""

    def __init__(self, model, beta=0.5, learning_rate=1e-5):
        self.model = model
        self.beta = beta  # Inverse temperature
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    def dpo_loss(self, log_probs_chosen, log_probs_rejected):
        """
        DPO loss - directly optimize preference differences

        Args:
            log_probs_chosen: Log probabilities for chosen completions
            log_probs_rejected: Log probabilities for rejected completions
        """
        # Log likelihood ratio
        log_ratio = log_probs_chosen - log_probs_rejected

        # DPO objective: maximize log(sigmoid(beta * log_ratio))
        loss = -torch.nn.functional.logsigmoid(self.beta * log_ratio).mean()

        return loss

    def train_step(self, prompts, chosen_completions, rejected_completions):
        """Single DPO training step"""

        # Forward pass for chosen
        logits_chosen = self.model(chosen_completions)
        log_probs_chosen = torch.nn.functional.log_softmax(logits_chosen, dim=-1).mean()

        # Forward pass for rejected
        logits_rejected = self.model(rejected_completions)
        log_probs_rejected = torch.nn.functional.log_softmax(logits_rejected, dim=-1).mean()

        # Compute loss
        loss = self.dpo_loss(log_probs_chosen, log_probs_rejected)

        # Optimization
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()

        return loss.item()
```

---

## Prompt Engineering

### Techniques and Best Practices

```python
class PromptTemplate:
    """Template system for consistent prompting"""

    def __init__(self, template, input_variables):
        self.template = template
        self.input_variables = input_variables

    def format(self, **kwargs):
        """Format prompt with variables"""
        return self.template.format(**kwargs)


# 1. Zero-shot prompting
zero_shot_template = PromptTemplate(
    template="Complete the following task:\n{task_description}\n\nInput: {input}\nOutput:",
    input_variables=['task_description', 'input']
)

prompt = zero_shot_template.format(
    task_description="Classify the sentiment of the text",
    input="I love this product!"
)
# Output: "Complete the following task:\nClassify the sentiment of the text\n\nInput: I love this product!\nOutput:"


# 2. Few-shot prompting with examples
few_shot_template = PromptTemplate(
    template="""Classify the sentiment of movie reviews.

Examples:
Review: "This movie is terrible"
Sentiment: Negative

Review: "Absolutely amazing film!"
Sentiment: Positive

Review: {review}
Sentiment:""",
    input_variables=['review']
)


# 3. Chain-of-Thought prompting
cot_template = PromptTemplate(
    template="""Solve this step by step.

Question: {question}

Let's think through this:
Step 1: {step1_instruction}
Step 2: {step2_instruction}
Step 3: {step3_instruction}

Answer:""",
    input_variables=['question', 'step1_instruction', 'step2_instruction', 'step3_instruction']
)


# 4. Role-based prompting
role_template = PromptTemplate(
    template="""You are an expert {role}. Answer the following question:

Question: {question}

As an expert {role}, your response:""",
    input_variables=['role', 'question']
)


# 5. Instruction-based prompting
instruction_template = PromptTemplate(
    template="""[INST] {instruction} [/INST]

Input:
{input}

Response:""",
    input_variables=['instruction', 'input']
)


class PromptOptimizer:
    """Optimize prompts through evaluation"""

    def __init__(self, model, eval_metric):
        self.model = model
        self.eval_metric = eval_metric

    def evaluate_prompt(self, prompt, test_cases):
        """Evaluate prompt quality"""
        scores = []

        for test_case in test_cases:
            # Generate response
            response = self.model(prompt + test_case['input'])

            # Evaluate
            score = self.eval_metric(response, test_case['expected_output'])
            scores.append(score)

        return sum(scores) / len(scores)

    def optimize_prompts(self, prompt_variants, test_cases):
        """Find best prompt variant"""
        best_prompt = None
        best_score = -1

        for prompt in prompt_variants:
            score = self.evaluate_prompt(prompt, test_cases)

            if score > best_score:
                best_score = score
                best_prompt = prompt

        return best_prompt, best_score


# Best Practices
BEST_PRACTICES = """
1. Be Specific and Clear
   ❌ Bad: "Write about climate change"
   ✅ Good: "Write a 200-word summary explaining the causes of climate change and their effects on sea levels"

2. Provide Context
   Include relevant background information to help the model understand

3. Use Examples (Few-shot)
   Provide 2-5 examples of desired output format

4. Use Delimiters
   Use ### or --- to separate sections clearly

5. Specify Output Format
   "Output as JSON" or "Use bullet points"

6. Break Complex Tasks
   Chain multiple prompts together (chain-of-thought)

7. Ask for Reasoning
   "Explain your reasoning" or "Think step by step"

8. Temperature Setting
   - Lower temperature (0.1-0.3): Factual tasks
   - Higher temperature (0.7-1.0): Creative tasks

9. Avoid Bias
   Don't include answer hints in the prompt

10. Iterate and Improve
    Test prompts, measure results, refine iteratively
"""

print(BEST_PRACTICES)
```

---

## RAG: Retrieval-Augmented Generation

### Implementation

```python
import numpy as np
from typing import List, Tuple

class SimpleVectorStore:
    """Simple in-memory vector store for RAG"""

    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadata = []

    def add_document(self, text, embedding, metadata=None):
        """Add document to store"""
        self.documents.append(text)
        self.embeddings.append(embedding)
        self.metadata.append(metadata or {})

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents using cosine similarity"""
        if not self.embeddings:
            return []

        embeddings = np.array(self.embeddings)

        # Cosine similarity
        query_norm = np.linalg.norm(query_embedding)
        doc_norms = np.linalg.norm(embeddings, axis=1)

        similarities = np.dot(embeddings, query_embedding) / (doc_norms * query_norm + 1e-8)

        # Get top k
        top_indices = np.argsort(similarities)[::-1][:k]

        return [(self.documents[i], similarities[i]) for i in top_indices]


class RAGPipeline:
    """RAG pipeline: retrieve documents, augment prompt, generate"""

    def __init__(self, llm, embedding_model, vector_store):
        """
        Args:
            llm: Language model for generation
            embedding_model: Model to encode text to embeddings
            vector_store: Document store with search
        """
        self.llm = llm
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """Retrieve relevant documents"""
        # Encode query
        query_embedding = self.embedding_model.encode(query)

        # Search
        results = self.vector_store.search(query_embedding, k=k)

        return [doc for doc, score in results]

    def augment_prompt(self, query: str, context_docs: List[str]) -> str:
        """Build augmented prompt with context"""
        context_str = "\n".join([f"- {doc}" for doc in context_docs])

        augmented_prompt = f"""Answer the following question using the provided context.

Context:
{context_str}

Question: {query}

Answer:"""

        return augmented_prompt

    def generate(self, query: str, k: int = 5, temperature: float = 0.7) -> Tuple[str, List[str]]:
        """Full RAG pipeline"""
        # Retrieve
        context_docs = self.retrieve(query, k=k)

        # Augment
        augmented_prompt = self.augment_prompt(query, context_docs)

        # Generate
        response = self.llm.generate(augmented_prompt, temperature=temperature)

        return response, context_docs


class HybridRetrieval:
    """Combine dense (semantic) and sparse (keyword) retrieval"""

    def __init__(self, vector_store, inverted_index):
        """
        Args:
            vector_store: Dense retrieval
            inverted_index: Sparse retrieval (TF-IDF, BM25, etc.)
        """
        self.vector_store = vector_store
        self.inverted_index = inverted_index

    def hybrid_search(self, query: str, k: int = 5, dense_weight: float = 0.7):
        """Combine dense and sparse retrieval"""

        # Dense retrieval
        dense_results = self.vector_store.search(query, k=k)
        dense_scores = {doc: score for doc, score in dense_results}

        # Sparse retrieval
        sparse_results = self.inverted_index.search(query, k=k)
        sparse_scores = {doc: score for doc, score in sparse_results}

        # Combine scores
        all_docs = set(list(dense_scores.keys()) + list(sparse_scores.keys()))
        combined_scores = {}

        for doc in all_docs:
            dense_score = dense_scores.get(doc, 0)
            sparse_score = sparse_scores.get(doc, 0)

            combined_scores[doc] = (
                dense_weight * dense_score +
                (1 - dense_weight) * sparse_score
            )

        # Sort and return
        sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in sorted_docs[:k]]


class IterativeRAG:
    """RAG with query reformulation and iterative retrieval"""

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def reformulate_query(self, original_query: str, conversation_history: List[str]) -> str:
        """Reformulate query based on conversation"""

        prompt = f"""Given the conversation history and original query,
        reformulate the query to be more specific and standalone.

History: {' -> '.join(conversation_history[-3:])}
Original Query: {original_query}

Reformulated Query:"""

        return self.llm.generate(prompt)

    def iterative_retrieve(self, query: str, num_iterations: int = 3):
        """Retrieve, then reformulate, then retrieve again"""

        current_query = query
        all_docs = set()

        for iteration in range(num_iterations):
            # Retrieve
            docs = self.retriever.retrieve(current_query)
            all_docs.update(docs)

            if iteration < num_iterations - 1:
                # Reformulate for next iteration
                context = "\n".join(list(all_docs)[:3])
                prompt = f"""Based on these retrieved documents:
{context}

Original query: {query}

Generate a follow-up retrieval query to find more relevant information:"""

                current_query = self.llm.generate(prompt)

        return list(all_docs)
```

### Practical Example with Embeddings

```python
# Example using sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Install: pip install sentence-transformers")

def rag_example():
    """Complete RAG example"""

    # Initialize components
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    vector_store = SimpleVectorStore()

    # Add documents
    documents = [
        "Python is a high-level programming language",
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks with multiple layers",
        "Natural language processing deals with text analysis",
        "Computer vision focuses on image understanding"
    ]

    for doc in documents:
        embedding = embedding_model.encode(doc)
        vector_store.add_document(doc, embedding)

    # Create RAG pipeline
    class SimpleLLM:
        def generate(self, prompt, temperature=0.7):
            return f"Response to: {prompt[:50]}..."

    llm = SimpleLLM()
    rag = RAGPipeline(llm, embedding_model, vector_store)

    # Query
    query = "Tell me about neural networks"
    response, context = rag.generate(query, k=3)

    print(f"Query: {query}")
    print(f"Context: {context}")
    print(f"Response: {response}")
```

---

## LLM Evaluation

### Metrics and Benchmarks

```python
from typing import List, Dict
import numpy as np
import math

class PerplexityMetric:
    """Perplexity - inverse probability of test set"""

    @staticmethod
    def compute(logits: np.ndarray, labels: np.ndarray) -> float:
        """
        Args:
            logits: (seq_len, vocab_size)
            labels: (seq_len,)
        """
        log_probs = logits[np.arange(len(labels)), labels]
        average_log_prob = np.mean(log_probs)
        perplexity = math.exp(-average_log_prob)

        return perplexity


class BleuScore:
    """BLEU - Bilingual Evaluation Understudy"""

    @staticmethod
    def compute(reference: str, hypothesis: str, n_gram: int = 4) -> float:
        """Simple BLEU implementation"""
        ref_tokens = reference.split()
        hyp_tokens = hypothesis.split()

        matches = 0
        for n in range(1, n_gram + 1):
            ref_ngrams = {
                ' '.join(ref_tokens[i:i+n]): 1
                for i in range(len(ref_tokens) - n + 1)
            }

            for i in range(len(hyp_tokens) - n + 1):
                ngram = ' '.join(hyp_tokens[i:i+n])
                if ngram in ref_ngrams:
                    matches += 1

        brevity_penalty = min(1.0, len(hyp_tokens) / len(ref_tokens))
        bleu = brevity_penalty * (matches / len(hyp_tokens)) if hyp_tokens else 0

        return bleu


class RougeScore:
    """ROUGE - Recall-Oriented Understudy for Gisting Evaluation"""

    @staticmethod
    def rouge_n(reference: str, hypothesis: str, n: int = 1) -> Dict[str, float]:
        """ROUGE-N implementation"""
        ref_tokens = reference.split()
        hyp_tokens = hypothesis.split()

        # n-grams
        ref_ngrams = [
            ' '.join(ref_tokens[i:i+n])
            for i in range(len(ref_tokens) - n + 1)
        ]
        hyp_ngrams = [
            ' '.join(hyp_tokens[i:i+n])
            for i in range(len(hyp_tokens) - n + 1)
        ]

        # Overlap
        overlap = len(set(ref_ngrams) & set(hyp_ngrams))

        # Recall and Precision
        recall = overlap / len(ref_ngrams) if ref_ngrams else 0
        precision = overlap / len(hyp_ngrams) if hyp_ngrams else 0
        f1 = 2 * (recall * precision) / (recall + precision) if (recall + precision) > 0 else 0

        return {
            'recall': recall,
            'precision': precision,
            'f1': f1
        }

    @staticmethod
    def rouge_l(reference: str, hypothesis: str) -> Dict[str, float]:
        """ROUGE-L using LCS (Longest Common Subsequence)"""
        ref_tokens = reference.split()
        hyp_tokens = hypothesis.split()

        # Compute LCS
        lcs_len = BleuScore._lcs_length(ref_tokens, hyp_tokens)

        recall = lcs_len / len(ref_tokens) if ref_tokens else 0
        precision = lcs_len / len(hyp_tokens) if hyp_tokens else 0
        f1 = 2 * (recall * precision) / (recall + precision) if (recall + precision) > 0 else 0

        return {
            'recall': recall,
            'precision': precision,
            'f1': f1
        }

    @staticmethod
    def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
        """Longest Common Subsequence length"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[m][n]


class HumanEvaluation:
    """Framework for human evaluation"""

    def __init__(self, evaluators: int = 3, agreement_threshold: float = 0.67):
        self.evaluators = evaluators
        self.agreement_threshold = agreement_threshold
        self.scores = []

    def evaluate(self, prompt: str, completion: str, rubric: Dict[str, str]):
        """
        Have humans evaluate following a rubric

        rubric: {
            'relevance': 'Does the response address the prompt?',
            'accuracy': 'Is the information correct?',
            'fluency': 'Is the text well-written?'
        }
        """
        evaluation = {
            'prompt': prompt,
            'completion': completion,
            'scores': {}
        }

        for criterion, description in rubric.items():
            print(f"\n{criterion}: {description}")
            print(f"Completion: {completion}")
            score = int(input("Score (1-5): "))
            evaluation['scores'][criterion] = score

        self.scores.append(evaluation)
        return evaluation

    def aggregate_scores(self) -> Dict[str, float]:
        """Aggregate evaluation scores"""
        if not self.scores:
            return {}

        all_criteria = set()
        for score_dict in self.scores:
            all_criteria.update(score_dict['scores'].keys())

        aggregated = {}
        for criterion in all_criteria:
            scores = [
                s['scores'][criterion]
                for s in self.scores
                if criterion in s['scores']
            ]
            aggregated[criterion] = np.mean(scores) if scores else 0

        return aggregated


class BenchmarkEvaluator:
    """Evaluate on standard benchmarks"""

    # Major LLM benchmarks
    BENCHMARKS = {
        'HellaSwag': 'Commonsense reasoning - video understanding',
        'MMLU': 'Multitask language understanding - 57 subjects',
        'TruthfulQA': 'Truthfulness - how much generated text is true',
        'GSM8K': 'Grade school math - 8.5K problems',
        'HumanEval': 'Code generation - 164 programming problems',
        'BLEU': 'Machine translation quality',
        'DropEmoji': 'Common sense reasoning',
        'Arc': 'Science question answering',
    }

    @staticmethod
    def evaluate_on_benchmark(model, benchmark_name: str):
        """Evaluate model on standard benchmark"""

        if benchmark_name == 'HumanEval':
            return BenchmarkEvaluator._eval_human_eval(model)
        elif benchmark_name == 'MMLU':
            return BenchmarkEvaluator._eval_mmlu(model)
        else:
            print(f"Benchmark {benchmark_name} requires external setup")

    @staticmethod
    def _eval_human_eval(model):
        """Code generation evaluation"""
        print("Evaluating on HumanEval...")
        print("Install: pip install human-eval")
        # Actual evaluation requires human_eval package

    @staticmethod
    def _eval_mmlu(model):
        """Multi-task language understanding"""
        print("Evaluating on MMLU...")
        print("Requires downloading MMLU dataset")


# Evaluation example
def evaluate_model_example():
    """Complete evaluation pipeline"""

    # Test data
    reference = "The quick brown fox jumps over the lazy dog"
    hypothesis = "A quick brown fox jumps over a lazy dog"

    # BLEU
    bleu = BleuScore.compute(reference, hypothesis)
    print(f"BLEU: {bleu:.4f}")

    # ROUGE
    rouge_1 = RougeScore.rouge_n(reference, hypothesis, n=1)
    print(f"ROUGE-1: {rouge_1}")

    rouge_l = RougeScore.rouge_l(reference, hypothesis)
    print(f"ROUGE-L: {rouge_l}")

    # Human eval
    evaluator = HumanEvaluation()
    rubric = {
        'relevance': 'Is the response relevant to the prompt?',
        'accuracy': 'Is the information accurate?',
        'completeness': 'Does it cover all aspects?'
    }

    # Note: This would require interactive input
    # evaluation = evaluator.evaluate("What is AI?", "AI is...", rubric)
```

---

## Inference Optimization

### KV Cache

```python
class KVCache:
    """Key-Value cache for efficient inference"""

    def __init__(self, max_seq_len: int, batch_size: int, head_dim: int, num_heads: int):
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size
        self.head_dim = head_dim
        self.num_heads = num_heads

        # Pre-allocate cache
        self.k_cache = torch.zeros(batch_size, max_seq_len, num_heads, head_dim)
        self.v_cache = torch.zeros(batch_size, max_seq_len, num_heads, head_dim)
        self.seq_len = 0

    def update(self, k_new: torch.Tensor, v_new: torch.Tensor):
        """Update cache with new keys and values"""
        seq_len = k_new.shape[1]

        self.k_cache[:, self.seq_len:self.seq_len + seq_len, :, :] = k_new
        self.v_cache[:, self.seq_len:self.seq_len + seq_len, :, :] = v_new

        self.seq_len += seq_len

    def get(self, up_to: int = None):
        """Get cached keys and values"""
        if up_to is None:
            up_to = self.seq_len

        return self.k_cache[:, :up_to, :, :], self.v_cache[:, :up_to, :, :]

    def reset(self):
        """Clear cache for new sequence"""
        self.seq_len = 0


class AttentionWithCache(nn.Module):
    """Attention that uses KV cache during inference"""

    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.o_proj = nn.Linear(d_model, d_model)

    def forward(self, x, kv_cache=None, use_cache=False):
        """
        Args:
            x: (batch_size, seq_len, d_model)
            kv_cache: KVCache object or None
            use_cache: whether to use/update cache
        """
        batch_size, seq_len, d_model = x.shape

        # Projections
        q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)
        v = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim)

        # Use cache if provided
        if kv_cache is not None and use_cache:
            # During generation, x is single token (seq_len=1)
            # Use cached k,v from previous tokens + new k,v for current token
            kv_cache.update(k, v)
            k_full, v_full = kv_cache.get()
        else:
            k_full, v_full = k, v

        # Attention
        q = q.transpose(1, 2)  # (batch, num_heads, seq_len, head_dim)
        k_full = k_full.transpose(1, 2)
        v_full = v_full.transpose(1, 2)

        scores = torch.matmul(q, k_full.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn = torch.softmax(scores, dim=-1)
        output = torch.matmul(attn, v_full)

        # Reshape
        output = output.transpose(1, 2).contiguous()
        output = output.view(batch_size, seq_len, d_model)

        return self.o_proj(output)
```

### Quantization

```python
class Int8Quantizer:
    """8-bit quantization for inference"""

    @staticmethod
    def quantize(x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Quantize to int8

        Returns:
            quantized values, scale factor
        """
        # Find scale
        max_val = x.abs().max()
        scale = max_val / 127.0

        # Quantize
        q = (x / scale).round().clamp(-128, 127).to(torch.int8)

        return q, scale

    @staticmethod
    def dequantize(q: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        """Dequantize from int8"""
        return q.float() * scale


class DynamicQuantization(nn.Module):
    """Dynamically quantize activations"""

    def __init__(self, module):
        super().__init__()
        self.module = module

    def forward(self, x):
        # Quantize input
        x_q, x_scale = Int8Quantizer.quantize(x)
        x_q = x_q.float() / 127.0  # Scale to [-1, 1]

        # Forward through module
        y = self.module(x_q)

        # Dequantize output (for next layer)
        return y


class QuantizedLinear(nn.Module):
    """Linear layer with quantized weights"""

    def __init__(self, in_features, out_features):
        super().__init__()

        # Store as quantized int8
        weight = torch.randn(out_features, in_features)
        q_weight, w_scale = Int8Quantizer.quantize(weight)

        self.register_buffer('weight_q', q_weight)
        self.register_buffer('weight_scale', w_scale)

        self.bias = nn.Parameter(torch.zeros(out_features))

    def forward(self, x):
        # Dequantize weights
        weight = Int8Quantizer.dequantize(self.weight_q, self.weight_scale)

        # Forward
        return torch.nn.functional.linear(x, weight, self.bias)


# Example: Quantize model
def quantize_model(model):
    """Replace linear layers with quantized versions"""
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            parent_name, child_name = name.rsplit('.', 1)
            parent = dict(model.named_modules())[parent_name]

            q_linear = QuantizedLinear(module.in_features, module.out_features)
            setattr(parent, child_name, q_linear)

    return model
```

### Speculative Decoding

```python
class SpeculativeDecoding:
    """Speculative decoding for faster inference"""

    def __init__(self, main_model, draft_model, num_speculations=5):
        """
        Args:
            main_model: Large, accurate model
            draft_model: Small, fast model for speculation
            num_speculations: How many tokens to draft ahead
        """
        self.main_model = main_model
        self.draft_model = draft_model
        self.num_speculations = num_speculations

    def decode_step(self, input_ids):
        """Single decoding step with speculation"""

        # Draft: generate k tokens with draft model
        draft_tokens = []
        draft_logits = []

        current_ids = input_ids.clone()
        for _ in range(self.num_speculations):
            draft_out = self.draft_model(current_ids)
            draft_logit = draft_out[:, -1, :]  # Last token
            draft_token = torch.argmax(draft_logit, dim=-1, keepdim=True)

            draft_tokens.append(draft_token)
            draft_logits.append(draft_logit)

            current_ids = torch.cat([current_ids, draft_token], dim=1)

        # Verify: run main model on drafted sequence
        main_out = self.main_model(input_ids)
        main_logits = main_out[:, :]

        # Compare probabilities
        acceptance_ratio = []
        accepted_tokens = []

        for i, draft_token in enumerate(draft_tokens):
            # Get main model's logit for this position
            position = input_ids.shape[1] + i

            # Check if draft matches main
            draft_prob = torch.softmax(draft_logits[i], dim=-1)
            main_prob = torch.softmax(main_logits[:, position, :], dim=-1)

            draft_token_logit = draft_logits[i].gather(1, draft_token)
            main_token_logit = main_logits[:, position, :].gather(1, draft_token)

            # Acceptance probability
            ratio = torch.clamp(
                torch.exp(main_token_logit - draft_token_logit),
                max=1.0
            )

            # Accept or reject
            if torch.rand(1) < ratio:
                accepted_tokens.append(draft_token)
                acceptance_ratio.append(ratio.item())
            else:
                # Reject: sample from main model
                accepted_tokens.append(
                    torch.multinomial(main_prob, 1)
                )
                break

        return torch.cat(accepted_tokens, dim=1) if accepted_tokens else torch.tensor([])
```

---

## Production Deployment

### vLLM

```python
# vLLM - High-throughput inference engine
# Install: pip install vllm

class vLLMDeployment:
    """Production deployment with vLLM"""

    @staticmethod
    def example():
        """vLLM usage example"""
        from vllm import LLM, SamplingParams

        # Initialize LLM
        llm = LLM(
            model="meta-llama/Llama-2-7b-hf",
            tensor_parallel_size=2,  # Multi-GPU
            gpu_memory_utilization=0.9,  # Use 90% GPU memory
            dtype="half",  # FP16
            swap_space=4,  # CPU swap
            max_seq_len_to_capture=4096
        )

        # Batched inference
        prompts = [
            "Explain machine learning",
            "What is deep learning?",
            "Tell me about transformers"
        ]

        sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.95,
            max_tokens=128,
            use_beam_search=False,
            repetition_penalty=1.05
        )

        # Fast batched generation
        outputs = llm.generate(prompts, sampling_params)

        for output in outputs:
            print(output.outputs[0].text)

        return llm


print("vLLM requires installation: pip install vllm")
```

### TensorRT-LLM

```python
class TensorRTDeployment:
    """NVIDIA TensorRT-LLM for optimized inference"""

    @staticmethod
    def setup_example():
        """TensorRT-LLM setup"""
        print("""
        Installation:
        pip install tensorrt-llm

        Key Features:
        - Multi-GPU tensor parallelism
        - Multi-head attention optimizations
        - Custom kernels for transformers
        - Memory-optimized generation
        """)


class TGIDeployment:
    """Text Generation Inference - Hugging Face's serving framework"""

    @staticmethod
    def docker_example():
        """Deploy with TGI using Docker"""
        dockerfile = """
# Dockerfile for TGI deployment
FROM ghcr.io/huggingface/text-generation-inference:1.0

# Model to load
ENV MODEL_ID=meta-llama/Llama-2-7b-hf
ENV NUM_SHARD=2

# Run TGI server
CMD ["--model-id", "$MODEL_ID", "--num-shard", "$NUM_SHARD"]
        """

        docker_compose = """
version: '3.8'

services:
  tgi:
    image: ghcr.io/huggingface/text-generation-inference:latest
    environment:
      MODEL_ID: meta-llama/Llama-2-7b-hf
      NUM_SHARD: 2
      CUDA_VISIBLE_DEVICES: 0,1
    volumes:
      - ./models:/models
      - ./data:/data
    ports:
      - "8080:80"
    gpus: all

  api:
    build: .
    depends_on:
      - tgi
    ports:
      - "5000:5000"
    environment:
      TGI_URL: http://tgi:80
        """

        return dockerfile, docker_compose


class APIServer:
    """Production API server for LLM inference"""

    def __init__(self, model_path, device='cuda'):
        """Initialize with model"""
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load model for serving"""
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype="auto",
            device_map="auto"
        )

    def generate(self, prompt: str, max_tokens: int = 128) -> str:
        """Generate text"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )

        return self.tokenizer.decode(outputs[0])


# FastAPI example
def fastapi_server_example():
    """Complete FastAPI server for LLM"""

    code = '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

app = FastAPI()

# Model loading
MODEL_PATH = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)

class GenerationRequest(BaseModel):
    prompt: str
    max_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.95

class GenerationResponse(BaseModel):
    prompt: str
    generated_text: str
    tokens_generated: int

@app.post("/generate")
async def generate(request: GenerationRequest) -> GenerationResponse:
    try:
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)

        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=True
        )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return GenerationResponse(
            prompt=request.prompt,
            generated_text=generated_text,
            tokens_generated=outputs.shape[1] - inputs.input_ids.shape[1]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run with: uvicorn server:app --host 0.0.0.0 --port 8000
    '''

    return code


print("Production Deployment Frameworks")
print("=" * 50)
print(TensorRTDeployment.setup_example())
```

---

## Best Practices

### From Industry Leaders

```python
BEST_PRACTICES = {
    "OpenAI": {
        "principles": [
            "Start with GPT-3.5-turbo for cost-efficiency",
            "Use function calling for structured outputs",
            "Implement rate limiting and retry logic",
            "Monitor token usage and costs",
            "Use system prompts for consistent behavior"
        ],
        "code_example": """
from openai import OpenAI

client = OpenAI(api_key="sk-...")

# System prompt for consistent behavior
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant specializing in Python."
        },
        {
            "role": "user",
            "content": "Explain decorators in Python"
        }
    ],
    temperature=0.7,
    max_tokens=500,
    top_p=0.95
)

print(response.choices[0].message.content)
        """
    },

    "Anthropic": {
        "principles": [
            "Claude excels at complex reasoning",
            "Use extended thinking (claude-opus) for difficult problems",
            "Leverage constitutional AI for safety",
            "Provide clear context and examples",
            "Use XML tags for structured prompting"
        ],
        "code_example": """
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-3-opus-20250219",
    max_tokens=2048,
    system="You are an expert data scientist.",
    messages=[
        {
            "role": "user",
            "content": \"\"\"
<task>
Analyze the following data and provide insights.
</task>

<data>
[Your data here]
</data>
            \"\"\"
        }
    ]
)

print(response.content[0].text)
        """
    },

    "Meta (LLaMA)": {
        "principles": [
            "Open-source and fine-tuning-friendly",
            "Excellent for domain-specific applications",
            "Strong performance on reasoning tasks",
            "Use Llama-2 or Llama-3 for production",
            "Consider LoRA for efficient fine-tuning"
        ],
        "code_example": """
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "meta-llama/Llama-2-7b-chat"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

prompt = "[INST] What is machine learning? [/INST]"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=128,
    temperature=0.7,
    top_p=0.95
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
        """
    }
}

# Core principles for all LLM work
UNIVERSAL_PRINCIPLES = """
1. START SIMPLE
   - Begin with smaller models and basic prompts
   - Scale up complexity only when needed

2. MEASURE EVERYTHING
   - Track latency, cost, quality metrics
   - A/B test different approaches
   - Monitor in production continuously

3. HANDLE FAILURES GRACEFULLY
   - Implement retry logic with exponential backoff
   - Set timeouts appropriately
   - Fall back to alternative strategies

4. OPTIMIZE COSTS
   - Use smaller models when they suffice
   - Cache frequent queries
   - Batch requests when possible
   - Use quantization for inference

5. ENSURE SAFETY AND ETHICS
   - Implement content filtering
   - Add user authentication/rate limiting
   - Monitor for harmful outputs
   - Respect privacy and data regulations

6. CONTINUOUS IMPROVEMENT
   - Collect user feedback
   - Evaluate on diverse test sets
   - Implement A/B testing
   - Update models and prompts regularly

7. DOCUMENTATION AND REPRODUCIBILITY
   - Document all prompts and configurations
   - Version control everything
   - Keep experiment logs
   - Share learnings with team

8. PERFORMANCE OPTIMIZATION
   - Use KV cache for generation
   - Implement batching
   - Quantize models
   - Consider distributed inference

9. MONITOR AND OBSERVABILITY
   - Log all API calls
   - Track token usage
   - Monitor error rates
   - Set up alerts

10. TESTING STRATEGY
    - Unit tests for prompt functions
    - Integration tests with mock models
    - Human evaluation for quality
    - Load testing before production
"""

print(UNIVERSAL_PRINCIPLES)
```

### Prompt Engineering Checklist

```python
PROMPT_ENGINEERING_CHECKLIST = """
BEFORE DEPLOYMENT:

□ Specificity
  - [ ] Prompt clearly states what output is expected
  - [ ] Example outputs provided if helpful
  - [ ] Ambiguous language removed

□ Context
  - [ ] Relevant background provided
  - [ ] Key information highlighted
  - [ ] Constraints clearly stated

□ Format
  - [ ] Output format explicitly specified
  - [ ] Examples of desired format included
  - [ ] Delimiters used for clarity

□ Robustness
  - [ ] Tested on diverse inputs
  - [ ] Edge cases considered
  - [ ] Failure modes identified

□ Efficiency
  - [ ] Prompt is concise
  - [ ] No unnecessary information
  - [ ] Token count optimized

□ Evaluation
  - [ ] Quality metrics defined
  - [ ] Baseline performance established
  - [ ] Human evaluation completed

□ Version Control
  - [ ] Prompt versioned
  - [ ] Changes documented
  - [ ] Previous versions archived

DURING DEPLOYMENT:

□ Monitoring
  - [ ] Track generation latency
  - [ ] Monitor output quality
  - [ ] Watch for cost increases
  - [ ] Alert on error rates

□ User Feedback
  - [ ] Collect user ratings
  - [ ] Track user corrections
  - [ ] Identify failure patterns
  - [ ] Log edge cases

AFTER DEPLOYMENT:

□ Continuous Improvement
  - [ ] Analyze feedback regularly
  - [ ] Update based on failures
  - [ ] Re-evaluate on new data
  - [ ] Document improvements
"""

print(PROMPT_ENGINEERING_CHECKLIST)
```

---

## Production Considerations

### Error Handling and Resilience

```python
import time
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ResilientLLMClient:
    """Robust LLM client with error handling"""

    def __init__(self, max_retries=3, timeout=30, backoff_factor=2):
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor

    def call_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """Call function with exponential backoff retry"""

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} attempts: {e}")
                    return None

                wait_time = self.backoff_factor ** attempt
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        return None


class CacheManager:
    """Simple caching for frequent queries"""

    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
        self.timestamps = {}

    def get(self, key: str):
        """Get cached value if not expired"""
        if key not in self.cache:
            return None

        age = time.time() - self.timestamps[key]
        if age > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None

        return self.cache[key]

    def set(self, key: str, value: Any):
        """Cache value"""
        self.cache[key] = value
        self.timestamps[key] = time.time()

    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, max_requests_per_minute=60):
        self.max_rate = max_requests_per_minute / 60  # Per second
        self.bucket = max_requests_per_minute
        self.last_update = time.time()

    def can_proceed(self):
        """Check if request is allowed"""
        now = time.time()
        elapsed = now - self.last_update

        # Refill bucket
        self.bucket = min(
            self.bucket + elapsed * self.max_rate,
            self.bucket  # Max capacity
        )
        self.last_update = now

        if self.bucket >= 1:
            self.bucket -= 1
            return True

        return False

    def wait_if_needed(self):
        """Wait until request is allowed"""
        while not self.can_proceed():
            time.sleep(0.1)
```

---

## Summary and Resources

### Key Takeaways

1. **Architecture**: Understand transformer fundamentals - they power all modern LLMs
2. **Fine-tuning**: Use LoRA/QLoRA for efficiency, full fine-tuning only when resources allow
3. **Alignment**: RLHF is standard, but DPO offers simpler alternatives
4. **Prompting**: Clear, specific, structured prompts work better than vague ones
5. **RAG**: Essential for incorporating external knowledge
6. **Evaluation**: Use multiple metrics (BLEU, ROUGE, human eval)
7. **Optimization**: KV cache, quantization, batching are non-negotiable for production
8. **Deployment**: Use vLLM, TGI, or TensorRT-LLM for production serving

### Further Reading

```python
RESOURCES = {
    "Papers": [
        "Attention is All You Need (Vaswani et al., 2017)",
        "Language Models are Unsupervised Multitask Learners (Radford et al., 2019)",
        "LLaMA: Open and Efficient Foundation Language Models (Touvron et al., 2023)",
        "Mistral 7B (Jiang et al., 2023)",
        "QLoRA: Efficient Finetuning of Quantized LLMs (Dettmers et al., 2023)",
        "Direct Preference Optimization (Rafailov et al., 2023)",
        "Retrieval-Augmented Generation (Lewis et al., 2020)"
    ],
    "Libraries": {
        "Transformers": "https://huggingface.co/transformers/",
        "PyTorch": "https://pytorch.org/",
        "vLLM": "https://github.com/lm-sys/vllm",
        "PEFT": "https://github.com/huggingface/peft",
        "LangChain": "https://python.langchain.com/",
        "Llama Index": "https://www.llamaindex.ai/"
    },
    "Benchmarks": [
        "MMLU - Multitask Language Understanding",
        "HumanEval - Code Generation",
        "TruthfulQA - Truthfulness",
        "HellaSwag - Commonsense Reasoning",
        "GSM8K - Grade School Math"
    ]
}
```

---

**Document Version**: 1.0
**Last Updated**: 2024
**Status**: Production Ready

This comprehensive guide covers the full LLM development lifecycle from architecture
understanding through production deployment, with practical code examples and best
practices from industry leaders.
