# Data Science & AI Skill: Elite ML/DL/NLP/LLM Expert

A comprehensive skill for world-class data science and AI work, covering machine learning, deep learning, natural language processing, and large language models from research to production.

## What It Does

This skill transforms you into an elite ML/AI expert who can:
- Design and implement end-to-end ML pipelines
- Build and optimize deep learning models
- Create production-grade NLP systems
- Fine-tune and deploy large language models
- Debug and optimize model performance
- Implement MLOps best practices
- Follow industry-leading standards from FAANG companies

## When to Use

### Machine Learning Projects
- Building classical ML models (regression, classification, clustering)
- Feature engineering and selection
- Hyperparameter optimization
- Model evaluation and validation
- AutoML implementations

### Deep Learning Projects
- Implementing neural network architectures (CNNs, RNNs, Transformers)
- Training optimization and debugging
- Transfer learning and fine-tuning
- Model compression and optimization
- Distributed training setups

### NLP Projects
- Text classification and sentiment analysis
- Named Entity Recognition (NER)
- Question answering systems
- Text generation and summarization
- Machine translation

### LLM Projects
- Fine-tuning large language models (GPT, BERT, T5)
- Implementing parameter-efficient fine-tuning (LoRA, QLoRA)
- Building RAG (Retrieval-Augmented Generation) systems
- Prompt engineering and optimization
- LLM evaluation and benchmarking
- Production LLM deployment

### MLOps & Production
- ML pipeline orchestration
- Model serving and deployment
- Monitoring and drift detection
- Feature stores and data versioning
- CI/CD for ML systems

## Skill Patterns

This skill provides 5 specialized patterns for different ML/AI workflows:

### 1. ML Pipeline Automation
**Use for**: End-to-end ML workflows, training pipelines, automated retraining

**What it does**:
- Designs complete ML pipelines from data to deployment
- Implements orchestration (Kubeflow, Airflow, Prefect)
- Sets up experiment tracking (MLflow, W&B)
- Creates automated hyperparameter tuning
- Implements data validation and monitoring

**Example**: "Build a production ML pipeline for customer churn prediction"

---

### 2. Model Analysis & Optimization
**Use for**: Debugging models, analyzing performance, optimizing inference

**What it does**:
- Comprehensive error analysis and diagnostics
- Feature importance and explainability (SHAP, LIME)
- Identifies performance bottlenecks
- Recommends optimization strategies
- Profiles memory and compute usage

**Example**: "Analyze why my transformer model is underperforming on long documents"

---

### 3. ML Project Scaffolding
**Use for**: Starting new projects, implementing architectures, building components

**What it does**:
- Generates project structure following best practices
- Creates dataset classes and data loaders
- Implements model architectures
- Sets up training and evaluation scripts
- Adds configuration management
- Scaffolds unit tests

**Example**: "Set up a new computer vision project for object detection"

---

### 4. Model Migration & Enhancement
**Use for**: Upgrading models, framework migration, implementing new techniques

**What it does**:
- Migrates between frameworks (PyTorch ↔ TensorFlow ↔ JAX)
- Converts models to deployment formats (ONNX, TorchScript)
- Implements new research techniques
- Refactors legacy ML code
- Upgrades to newer model versions

**Example**: "Convert my TensorFlow model to PyTorch and add Flash Attention"

---

### 5. Interactive ML Assistant
**Use for**: Learning, debugging, exploring, code review

**What it does**:
- Guides through exploratory data analysis
- Helps debug training issues
- Recommends architectures for your problem
- Explains ML concepts with examples
- Reviews ML code for best practices
- Suggests relevant papers and resources

**Example**: "Help me understand why my GAN training is unstable"

## Usage Examples

### Example 1: Fine-tuning an LLM for Code Generation

```
User: I want to fine-tune CodeLlama on my company's internal codebase

Skill Response:
I'll guide you through fine-tuning CodeLlama using the ML Pipeline Automation pattern.

**Step 1: Data Preparation**
First, let's prepare your codebase data:

[Provides code for data cleaning, tokenization, creating train/val splits]

**Step 2: Fine-tuning Strategy**
For your use case, I recommend QLoRA (Quantized LoRA) because:
- Memory efficient (can run on consumer GPUs)
- Fast training while maintaining quality
- Easy to deploy (merge weights or use adapters)

[Provides complete QLoRA implementation with best practices]

**Step 3: Training Pipeline**
Here's a production-ready training setup:

[Provides training script with:
- Gradient accumulation
- Mixed precision training
- Checkpoint management
- Evaluation during training
- W&B integration for tracking]

**Step 4: Evaluation**
[Sets up code generation benchmarks and evaluation metrics]

**Step 5: Deployment**
[Provides deployment options: vLLM, TGI, local serving]
```

---

### Example 2: Building a RAG System

```
User: Build a RAG system for our technical documentation

Skill Response:
I'll implement a production-grade RAG system using the ML Project Scaffolding pattern.

**Architecture Design**:
1. Document Processing Pipeline
   - PDF/Markdown parsing
   - Intelligent chunking (semantic splitting)
   - Metadata extraction

2. Embedding & Indexing
   - Embedding model: sentence-transformers/all-mpnet-base-v2
   - Vector DB: Qdrant (good balance of features/performance)
   - Hybrid search: dense + sparse (BM25)

3. Retrieval & Generation
   - Retriever: top-k with re-ranking
   - Generator: GPT-4 or fine-tuned Llama-2
   - Context management for long documents

**Implementation**:
[Provides complete code for:
- Document ingestion pipeline
- Embedding and indexing
- Retrieval with hybrid search
- Generation with context window management
- Evaluation framework (faithfulness, relevance)
- FastAPI serving endpoint
- Monitoring and logging]

**Evaluation**:
[Sets up evaluation metrics:
- Retrieval: MRR, NDCG, Recall@k
- Generation: Faithfulness, answer relevance
- End-to-end: Human eval framework]

**Production Considerations**:
- Incremental index updates
- Caching strategies
- Rate limiting
- Cost optimization
```

---

### Example 3: Debugging a Vision Model

```
User: My ResNet model for medical image classification isn't learning.
      Training loss stays at 0.693 (random chance).

Skill Response:
Let me use the Model Analysis & Optimization pattern to diagnose this.

**Initial Diagnostics**:

1. Checking training loss of 0.693:
   - This is exactly -ln(0.5), suggesting binary classification
   - Model is outputting random predictions
   - Let's verify the model is actually learning

**Systematic Analysis**:

[Provides diagnostic code to check:
1. Data loading - verify images and labels are correct
2. Model forward pass - check output ranges
3. Loss computation - verify gradients flow
4. Learning rate - check if too low/high
5. Data preprocessing - check normalization]

**Likely Issues** (ranked by probability):

1. **Label mismatch** (60% likely)
   - Your images might not match labels
   - Verification code: [provides code to visualize samples]

2. **Incorrect preprocessing** (25% likely)
   - Medical images need specific normalization
   - Check: windowing, HU normalization
   - Code: [provides correct preprocessing]

3. **Learning rate too high** (10% likely)
   - Try 1e-4 instead of 1e-3
   - Use learning rate finder: [provides code]

4. **Class imbalance** (5% likely)
   - Medical datasets often highly imbalanced
   - Solution: weighted loss or focal loss

**Recommended Actions**:
1. Run this data verification script: [script]
2. Add training monitoring: [gradient norms, activation stats]
3. Try this modified training loop: [improved version]

After fixes, we'll add:
- Proper evaluation metrics (AUROC, sensitivity, specificity)
- Cross-validation
- Uncertainty quantification
```

---

### Example 4: Implementing Research Paper

```
User: Implement the FlashAttention-2 paper for my transformer

Skill Response:
I'll implement FlashAttention-2 following the paper's algorithm.

**Paper Understanding**:
- Paper: "FlashAttention-2: Faster Attention with Better Parallelism"
- Key innovation: Better GPU utilization via parallelization
- Speed: 2x faster than FlashAttention-1

**Implementation Strategy**:

Option 1: Use official implementation (recommended for production)
```python
# Install official package
pip install flash-attn --no-build-isolation

# Integration code
from flash_attn import flash_attn_func
```

Option 2: Understand and implement core algorithm
[Provides educational implementation of the algorithm with:
- Detailed comments explaining each step
- References to paper sections
- Visualization of tiling strategy
- Performance profiling code]

**Integration into Your Model**:
[Provides complete integration:
- Replace standard attention
- Handle attention masks
- Support for causal and bidirectional attention
- Gradient checkpointing compatibility
- Mixed precision training]

**Validation**:
[Provides tests to verify:
- Numerical correctness vs standard attention
- Speed benchmarks
- Memory usage comparison
- Gradient correctness]

**Production Checklist**:
- ✅ Works with your model architecture
- ✅ Handles variable sequence lengths
- ✅ Compatible with DDP/FSDP
- ✅ Supports inference optimization
```

---

### Example 5: Setting Up MLOps Pipeline

```
User: Set up complete MLOps for our recommendation system

Skill Response:
I'll design a comprehensive MLOps pipeline using industry best practices.

**Architecture Overview**:

1. **Data Pipeline**
   - Feature engineering: Apache Spark
   - Feature store: Feast
   - Data validation: Great Expectations
   - Data versioning: DVC

2. **Training Pipeline**
   - Orchestration: Kubeflow Pipelines
   - Experiment tracking: MLflow
   - Hyperparameter tuning: Optuna
   - Distributed training: Ray

3. **Model Registry & Versioning**
   - Registry: MLflow Model Registry
   - Versioning: Git + DVC
   - Model validation: Custom gates

4. **Deployment**
   - Serving: TorchServe / BentoML
   - A/B testing: Istio + custom logic
   - Canary releases: Flagger
   - Load balancing: Kubernetes

5. **Monitoring**
   - Metrics: Prometheus + Grafana
   - Drift detection: Evidently AI
   - Performance tracking: Custom dashboards
   - Alerting: PagerDuty

**Implementation**:

[Provides complete implementation including:

1. Feature engineering pipeline (PySpark)
2. Feast feature store setup
3. Kubeflow pipeline definition
4. Training script with MLflow tracking
5. Model validation tests
6. Deployment manifests (Kubernetes)
7. Monitoring dashboards
8. CI/CD pipeline (GitHub Actions)
9. Documentation]

**Automation**:
- Scheduled retraining: Daily at 2 AM
- Automatic model validation
- Auto-deploy if metrics improve by >2%
- Rollback if error rate increases
- Weekly model performance reports
```

## Code Quality Standards

All code generated follows elite professional standards:

### Structure
- Type hints for all functions
- Comprehensive docstrings (Google style)
- Modular, testable design
- Configuration management (Hydra/OmegaConf)
- Logging with appropriate levels

### Testing
- Unit tests for all components
- Integration tests for pipelines
- Model validation tests
- Performance benchmarks

### Documentation
- Clear README with setup instructions
- API documentation
- Architecture diagrams
- Usage examples
- Troubleshooting guide

### ML-Specific
- Reproducibility (seed setting, versioning)
- Experiment tracking
- Model cards documenting capabilities/limitations
- Data sheets for datasets
- Bias and fairness considerations

## Best Practices Followed

### Data Science
- Proper train/val/test splits
- Cross-validation for robust evaluation
- Statistical significance testing
- Handle class imbalance appropriately
- Feature importance analysis

### Deep Learning
- Gradient clipping for stability
- Learning rate scheduling
- Early stopping with patience
- Model checkpointing (save best and last)
- Mixed precision training (AMP)
- Gradient accumulation for large batches

### NLP/LLMs
- Proper tokenization and preprocessing
- Attention mask handling
- Padding strategy optimization
- Efficient batching (pack sequences)
- Temperature and sampling control

### Production ML
- Input validation and sanitization
- Error handling and retries
- Graceful degradation
- Monitoring and alerting
- Model versioning and rollback
- A/B testing framework
- Cost optimization

## Knowledge Sources

This skill references elite, tier-1 sources:

### Research
- Top ML conferences: NeurIPS, ICML, ICLR, ACL, CVPR
- arXiv for latest papers
- Papers with Code for implementations
- Distill.pub for excellent explanations

### Industry Practices
- Google: Rules of ML, BERT, T5, PaLM
- Meta AI: PyTorch, LLaMA, FAIR research
- OpenAI: GPT series, CLIP, Whisper
- DeepMind: AlphaFold, Gato, Gemini
- Anthropic: Claude, Constitutional AI
- Microsoft Research: Phi models, DeepSpeed
- Hugging Face: Transformers ecosystem
- Scale AI: Data-centric AI

### Frameworks
- **Training**: PyTorch, JAX, TensorFlow
- **Libraries**: HuggingFace, LangChain, LlamaIndex
- **MLOps**: MLflow, W&B, Kubeflow, Ray
- **Serving**: TorchServe, Triton, vLLM, TGI
- **Data**: Pandas, Polars, Spark, Ray Data

## Troubleshooting Guide

### Model Not Learning
1. Check data pipeline (visualize samples)
2. Verify loss computation and gradients
3. Adjust learning rate (use LR finder)
4. Check for label leakage or mismatch
5. Simplify model to rule out architecture issues

### Out of Memory
1. Reduce batch size
2. Enable gradient accumulation
3. Use gradient checkpointing
4. Try mixed precision (FP16/BF16)
5. Consider model parallelism (FSDP/DeepSpeed)

### Poor Generalization
1. Add regularization (dropout, weight decay)
2. Increase training data (augmentation)
3. Simplify model (reduce capacity)
4. Better validation strategy (k-fold CV)
5. Analyze error cases

### Slow Training
1. Profile to find bottleneck (data loading vs compute)
2. Optimize data loading (num workers, prefetch)
3. Use faster data formats (parquet, tfrecord)
4. Enable compile (torch.compile, XLA)
5. Consider distributed training

### LLM Fine-tuning Issues
1. Check if sequence length truncation needed
2. Verify special tokens handled correctly
3. Use gradient accumulation for effective batch size
4. Monitor gradient norms (clip if exploding)
5. Try different learning rates (1e-5 to 5e-5)

## Advanced Topics

This skill also covers:

- **Distributed Training**: DDP, FSDP, DeepSpeed, Megatron
- **Model Optimization**: Quantization, pruning, distillation, ONNX
- **Multi-modal Learning**: CLIP, BLIP, Flamingo, GPT-4V patterns
- **Reinforcement Learning**: PPO, DQN, SAC, multi-agent
- **Graph Neural Networks**: GCN, GAT, GraphSAGE
- **Generative Models**: Diffusion, GANs, VAEs, flow-based
- **Few-shot Learning**: Meta-learning, prompt-based learning
- **Continual Learning**: Avoiding catastrophic forgetting
- **Federated Learning**: Privacy-preserving ML
- **Neural Architecture Search**: AutoML, NAS techniques

## Getting Started

To use this skill:

1. **Describe your ML/AI task**
   - What problem are you solving?
   - What data do you have?
   - What are your constraints?

2. **Skill selects appropriate pattern**
   - Pipeline Automation for end-to-end workflows
   - Analysis & Optimization for debugging
   - Project Scaffolding for new implementations
   - Migration & Enhancement for upgrades
   - Interactive Assistant for learning/exploring

3. **Receive expert guidance**
   - Production-grade code
   - Best practices from industry leaders
   - Comprehensive documentation
   - Testing and validation

## Example Invocations

**Quick help**: "Debug why my BERT fine-tuning loss is not decreasing"

**Project setup**: "Set up a new LLM project for legal document analysis"

**Implementation**: "Implement a production RAG system with hybrid search"

**Optimization**: "Optimize my transformer inference to reduce latency by 50%"

**Learning**: "Explain how to implement LoRA from scratch"

## Related Templates

Check the `templates/` directory for:
- `ml-pipeline-automation.md` - End-to-end ML workflows
- `model-analysis-optimization.md` - Debugging and optimization
- `ml-project-scaffolding.md` - Project structure and setup
- `model-migration-enhancement.md` - Framework migration and upgrades
- `interactive-ml-assistant.md` - Learning and exploration

---

**Ready to tackle any ML/AI challenge with elite professional standards, from research to production.**
