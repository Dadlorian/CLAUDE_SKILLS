# Model Optimization Guide

A comprehensive guide to optimizing deep learning models for production deployment with quantization, pruning, knowledge distillation, and advanced optimization techniques.

## Table of Contents

1. [Introduction](#introduction)
2. [Quantization](#quantization)
3. [Pruning](#pruning)
4. [Knowledge Distillation](#knowledge-distillation)
5. [ONNX Conversion & Optimization](#onnx-conversion--optimization)
6. [TensorRT Optimization](#tensorrt-optimization)
7. [Model Compression Techniques](#model-compression-techniques)
8. [Inference Optimization](#inference-optimization)
9. [Benchmarking Tools](#benchmarking-tools)
10. [Production Workflows](#production-workflows)
11. [Best Practices](#best-practices)

---

## Introduction

Model optimization is critical for deploying deep learning models in production environments. Key goals include:

- **Reduced Latency**: Faster inference times
- **Lower Memory Footprint**: Reduced RAM and storage requirements
- **Energy Efficiency**: Lower computational cost and power consumption
- **Edge Deployment**: Enable models to run on resource-constrained devices
- **Cost Reduction**: Smaller models = cheaper infrastructure

### Optimization Hierarchy

```
Accuracy → Speed
  ↓
Base Model Performance
  ↓
Quantization (30-90% speedup)
  ↓
Pruning (20-50% compression)
  ↓
Knowledge Distillation (student efficiency)
  ↓
Inference Framework Optimization
  ↓
Hardware-Specific Optimization (TensorRT, OpenVINO)
  ↓
Deployment & Monitoring
```

---

## Quantization

Quantization reduces model size and increases inference speed by using lower precision data types.

### Types of Quantization

#### 1. Post-Training Quantization (PTQ)

**Approach**: Apply quantization after training without retraining.

**Pros**:
- No retraining required
- Fast deployment
- Simple implementation

**Cons**:
- Potential accuracy loss
- Less control over quantization parameters

#### 2. Quantization-Aware Training (QAT)

**Approach**: Simulate quantization during training.

**Pros**:
- Better accuracy preservation
- More controlled quantization
- Near-lossless compression

**Cons**:
- Requires retraining
- Longer training time

### INT8 Quantization

**Characteristics**:
- 4x memory reduction
- 4x speedup (on supported hardware)
- Minimal accuracy loss (typically < 1%)

### INT4 Quantization

**Characteristics**:
- 8x memory reduction
- Limited hardware support
- Greater accuracy loss (1-5%)
- Suitable for LLMs

### Code Examples

#### Example 1: PyTorch INT8 PTQ with TorchScript

```python
import torch
import torch.nn as nn
from torch.quantization import quantize_dynamic, quantize

class OptimizedModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# 1. Dynamic Quantization (easiest)
model = OptimizedModel()
model.eval()

quantized_model = quantize_dynamic(
    model,
    {nn.Linear},
    dtype=torch.qint8
)

print(f"Model size before: {calculate_model_size(model):.2f} MB")
print(f"Model size after: {calculate_model_size(quantized_model):.2f} MB")

# 2. Static Quantization (requires calibration)
# Prepare model for static quantization
model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
torch.quantization.prepare(model, inplace=True)

# Calibration with representative data
def calibrate_model(model, calibration_dataloader):
    model.eval()
    with torch.no_grad():
        for images, _ in calibration_dataloader:
            model(images)

calibrate_model(model, calibration_loader)

# Convert to quantized model
torch.quantization.convert(model, inplace=True)

# Benchmark
def benchmark_model(model, inputs, num_runs=100):
    model.eval()

    import time
    start = time.time()
    with torch.no_grad():
        for _ in range(num_runs):
            _ = model(inputs)
    end = time.time()

    avg_time = (end - start) / num_runs * 1000  # ms
    return avg_time

dummy_input = torch.randn(1, 784)
original_time = benchmark_model(model, dummy_input)
quantized_time = benchmark_model(quantized_model, dummy_input)

print(f"Original: {original_time:.3f} ms")
print(f"Quantized: {quantized_time:.3f} ms")
print(f"Speedup: {original_time / quantized_time:.2f}x")
```

#### Example 2: Quantization-Aware Training (QAT)

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.quantization import QuantStub, DeQuantStub

class QuantAwareModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.quant = QuantStub()
        self.fc1 = nn.Linear(784, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 10)
        self.dequant = DeQuantStub()

    def forward(self, x):
        x = self.quant(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.dequant(x)
        return x

# Prepare model for QAT
model = QuantAwareModel()
model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
torch.quantization.prepare_qat(model, inplace=True)

# Training loop with quantization simulation
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

def train_qat(model, dataloader, epochs=10):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for images, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")

# After training, convert to quantized model
torch.quantization.convert(model, inplace=True)
```

#### Example 3: TensorFlow INT8 Quantization

```python
import tensorflow as tf
import numpy as np

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 1. PTQ with representative dataset
def representative_dataset():
    """Generate representative data for quantization"""
    for _ in range(100):
        yield [np.random.randn(1, 784).astype(np.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset

# Enable full integer quantization
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

quantized_tflite_model = converter.convert()

# Save quantized model
with open('model_quantized.tflite', 'wb') as f:
    f.write(quantized_tflite_model)

# 2. Quantization-Aware Training
quantize_model = tf.keras.experimental.enable_mixed_precision_graph_rewrite(model)

# Or use TensorFlow Model Optimization Toolkit
import tensorflow_model_optimization as tfmot

quantize_aware_model = tfmot.quantization.keras.quantize_model(model)
quantize_aware_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
```

#### Example 4: INT4 Quantization for Large Language Models

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# INT4 Quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    quantization_config=bnb_config,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")

# Memory-efficient inference
inputs = tokenizer("Hello, how are you?", return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(**inputs, max_length=100)

print(tokenizer.decode(outputs[0]))

# Model size comparison
print(f"INT4 Model: ~7GB")
print(f"FP16 Model: ~14GB")
print(f"Compression: 2x")
```

---

## Pruning

Pruning removes redundant weights and connections to reduce model size and latency.

### Pruning Types

#### 1. Magnitude Pruning
- Removes weights with absolute values below threshold
- Unstructured sparsity
- High compression, lower hardware efficiency

#### 2. Structured Pruning
- Removes entire filters, channels, or layers
- Maintains hardware efficiency
- Lower compression but better inference speedup

#### 3. Unstructured Pruning
- Removes individual weights
- Maximum compression
- Requires special kernels for inference

### Code Examples

#### Example 1: PyTorch Magnitude Pruning

```python
import torch
import torch.nn as nn
import torch.nn.utils.prune as prune

class PrunableModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x

# 1. Magnitude Pruning (one layer)
model = PrunableModel()
prune.l1_unstructured(model.fc1, name='weight', amount=0.5)

# 2. Magnitude Pruning (all layers)
def prune_model(model, pruning_amount=0.3):
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            prune.l1_unstructured(module, name='weight', amount=pruning_amount)
            prune.remove(module, 'weight')  # Make pruning permanent

prune_model(model, pruning_amount=0.3)

# 3. Structured Pruning (channel pruning)
class StructuredPruningModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, 3, padding=1)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        return x

model = StructuredPruningModel()

# Prune 50% of channels in conv2
prune.ln_structured(
    model.conv2,
    name='weight',
    amount=0.5,
    n=2,  # n=2 for channel pruning
    dim=0  # Output channels
)

# Verify sparsity
def get_sparsity(model):
    total_params = 0
    pruned_params = 0

    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            total_params += module.weight.numel()
            pruned_params += (module.weight == 0).sum().item()

    sparsity = pruned_params / total_params * 100
    return sparsity

print(f"Model Sparsity: {get_sparsity(model):.1f}%")

# 4. Iterative Magnitude Pruning
def iterative_pruning(model, target_sparsity=0.9, num_iterations=10):
    """Gradually increase sparsity to maintain accuracy"""
    current_sparsity = 0
    sparsity_step = target_sparsity / num_iterations

    for iteration in range(num_iterations):
        current_sparsity += sparsity_step
        prune_model(model, pruning_amount=current_sparsity)

        # Retrain model (not shown here)
        # train_epoch(model, train_loader)
        # evaluate(model, val_loader)

        print(f"Iteration {iteration+1}: Sparsity {current_sparsity*100:.1f}%")

# 5. Movement Pruning (pruning by movement)
def movement_pruning(model, threshold=0.5):
    """Prune based on gradient movement during training"""
    for name, param in model.named_parameters():
        if 'weight' in name and param.grad is not None:
            movement = torch.abs(param.grad * param)
            mask = movement > threshold
            param.data = param.data * mask.float()

print(f"Pruned model size: {calculate_model_size(model):.2f} MB")
```

#### Example 2: TensorFlow Structured Pruning

```python
import tensorflow as tf
import tensorflow_model_optimization as tfmot

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(28, 28, 1)),
    tf.keras.layers.MaxPooling2D(2),
    tf.keras.layers.Conv2D(64, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Define pruning schedule
pruning_schedule = tfmot.sparsity.keras.PolynomialDecay(
    initial_sparsity=0.35,
    final_sparsity=0.85,
    begin_step=0,
    end_step=2000,
    frequency=100
)

# Apply pruning
pruned_model = tfmot.sparsity.keras.prune_low_magnitude(
    model,
    pruning_schedule=pruning_schedule
)

pruned_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Fine-tune pruned model
pruned_model.fit(
    train_images, train_labels,
    batch_size=128,
    epochs=10,
    validation_data=(test_images, test_labels)
)

# Remove pruning wrappers before deployment
stripped_model = tfmot.sparsity.keras.strip_pruning(pruned_model)

# Quantize after pruning for maximum compression
converter = tf.lite.TFLiteConverter.from_keras_model(stripped_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
quantized_tflite_model = converter.convert()
```

#### Example 3: NVIDIA Structured Pruning (ASP)

```python
# NVIDIA Automatic Sparsity (ASP) for structured pruning
import torch
from torch.nn.utils import prune
import nvidia_pytriton_pruning as pruning

class NvidiaSparsityModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(1024, 512)
        self.fc2 = torch.nn.Linear(512, 256)
        self.fc3 = torch.nn.Linear(256, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = NvidiaSparsityModel()

# Apply ASP for semi-structured sparsity (2:4 pattern)
# Every 4 weights, at least 2 must be zero
pruning.apply_semi_structured_sparsity(model)

# Convert to TensorRT for optimized inference
import tensorrt as trt

# (See TensorRT section for full conversion)
```

---

## Knowledge Distillation

Knowledge distillation trains a smaller student model to mimic a larger teacher model.

### Benefits

- Smaller model size
- Faster inference
- Comparable accuracy to larger models
- Better generalization

### Code Example

#### PyTorch Knowledge Distillation

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# Teacher Model (large)
class TeacherModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Student Model (small)
class StudentModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Knowledge Distillation Loss
class DistillationLoss(nn.Module):
    def __init__(self, temperature=4.0, alpha=0.7):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.ce_loss = nn.CrossEntropyLoss()
        self.kl_div = nn.KLDivLoss(reduction='batchmean')

    def forward(self, student_logits, teacher_logits, labels):
        # Cross-entropy loss on original task
        ce = self.ce_loss(student_logits, labels)

        # Distillation loss (KL divergence on soft targets)
        teacher_soft = F.softmax(teacher_logits / self.temperature, dim=1)
        student_soft = F.log_softmax(student_logits / self.temperature, dim=1)

        kld = self.kl_div(student_soft, teacher_soft)

        # Combined loss
        total_loss = self.alpha * ce + (1 - self.alpha) * kld

        return total_loss

# Training with Knowledge Distillation
def train_with_distillation(teacher, student, train_loader, epochs=10):
    teacher.eval()  # Teacher doesn't learn
    student.train()

    optimizer = optim.Adam(student.parameters(), lr=0.001)
    distillation_loss = DistillationLoss(temperature=4.0, alpha=0.7)

    for epoch in range(epochs):
        total_loss = 0
        for images, labels in train_loader:
            # Forward pass
            with torch.no_grad():
                teacher_logits = teacher(images)

            student_logits = student(images)

            # Compute loss
            loss = distillation_loss(student_logits, teacher_logits, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

# Load pre-trained teacher
teacher = TeacherModel()
teacher.load_state_dict(torch.load('teacher_model.pt'))

# Create and train student
student = StudentModel()
train_with_distillation(teacher, student, train_loader, epochs=10)

# Comparison
print(f"Teacher params: {sum(p.numel() for p in teacher.parameters())}")
print(f"Student params: {sum(p.numel() for p in student.parameters())}")
print(f"Compression: {sum(p.numel() for p in teacher.parameters()) / sum(p.numel() for p in student.parameters()):.1f}x")
```

---

## ONNX Conversion & Optimization

ONNX (Open Neural Network Exchange) is a standard format for model interoperability.

### Benefits

- Cross-framework compatibility
- Performance optimization
- Hardware acceleration support

### Code Examples

#### PyTorch to ONNX

```python
import torch
import torch.onnx
import onnxruntime as ort
from onnxruntime.transformers import optimizer

# Model definition
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = SimpleModel()
model.eval()

# Export to ONNX
dummy_input = torch.randn(1, 784)

torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=['input'],
    output_names=['output'],
    opset_version=14,
    do_constant_folding=True,
    dynamic_axes={
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

# Inference with ONNX Runtime
def onnx_inference(onnx_path, inputs):
    sess = ort.InferenceSession(onnx_path)
    input_name = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    result = sess.run([output_name], {input_name: inputs})
    return result[0]

# ONNX Model Optimization
model_path = "model.onnx"
optimized_model_path = "model_optimized.onnx"

# Level 0: Basic optimizations
# Level 1: Extended optimizations (recommended)
# Level 2: Layout optimizations
# Level 3: All optimizations

from onnxruntime.transformers.onnx_model_bert import BertOptimizationOptions

# Optimize for inference
optimized_model = optimizer.optimize_model(
    model_path,
    model_type="bert",  # or other types
    num_heads=12,
    hidden_size=768,
    optimization_options=BertOptimizationOptions('all')
)

optimized_model.save_model_to_file(optimized_model_path)

# Benchmark comparison
import time

dummy_input_np = dummy_input.numpy().astype('float32')

# Original ONNX
sess_original = ort.InferenceSession(model_path)
start = time.time()
for _ in range(100):
    sess_original.run(None, {'input': dummy_input_np})
original_time = time.time() - start

# Optimized ONNX
sess_optimized = ort.InferenceSession(optimized_model_path)
start = time.time()
for _ in range(100):
    sess_optimized.run(None, {'input': dummy_input_np})
optimized_time = time.time() - start

print(f"Original: {original_time:.3f}s")
print(f"Optimized: {optimized_time:.3f}s")
print(f"Speedup: {original_time / optimized_time:.2f}x")
```

#### TensorFlow to ONNX

```python
import tensorflow as tf
import tf2onnx.convert

# Define and train model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Save as SavedModel format first
model.save('saved_model')

# Convert to ONNX
spec = (tf.TensorSpec((None, 784), tf.float32, name="input"),)

output_path = "model.onnx"

model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, output_path=output_path)
print(f"ONNX model saved to {output_path}")

# Verify ONNX model
import onnx

onnx_model = onnx.load(output_path)
onnx.checker.check_model(onnx_model)
print("ONNX model is valid")
```

#### ONNX Graph Optimization

```python
import onnx
from onnxruntime.transformers import optimizer as ort_optimizer

# Load ONNX model
model = onnx.load("model.onnx")

# Apply optimizations
from onnxruntime.transformers.onnx_model_bert import BertOptimizationOptions

optimization_options = BertOptimizationOptions('all')
optimization_options.enable_embed_layer_norm = True

# Run optimizer
model_optimizer = ort_optimizer.optimize_model(
    "model.onnx",
    model_type="bert",
    num_heads=12,
    hidden_size=768,
    optimization_options=optimization_options,
    opt_level=3  # Maximum optimization
)

# Save optimized model
model_optimizer.save_model_to_file("model_optimized.onnx")

# Inspect optimizations
print("Graph optimizations applied:")
print("- Constant folding")
print("- Common subexpression elimination")
print("- Dead code elimination")
print("- Layer fusion")
```

---

## TensorRT Optimization

NVIDIA TensorRT is a high-performance inference runtime for NVIDIA GPUs.

### Key Features

- FP32, FP16, INT8 precision support
- Layer and tensor fusion
- Kernel auto-tuning
- Dynamic shape support
- Plugin support for custom layers

### Code Examples

#### PyTorch to TensorRT via ONNX

```python
import torch
import torch.onnx
import tensorrt as trt
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit

# Step 1: Export PyTorch model to ONNX
model = SimpleModel()
model.eval()

dummy_input = torch.randn(1, 784)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=14,
    do_constant_folding=True,
    dynamic_axes={'input': {0: 'batch_size'}}
)

# Step 2: Convert ONNX to TensorRT Engine
def build_engine(onnx_file_path, engine_file_path, max_batch_size=1):
    """Build TensorRT engine from ONNX model"""

    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

    with trt.Builder(TRT_LOGGER) as builder, \
         builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)) as network, \
         trt.OnnxParser(network, TRT_LOGGER) as parser:

        builder.max_batch_size = max_batch_size
        builder.max_workspace_size = 1 << 30  # 1GB

        # Enable FP16 precision
        if builder.platform_has_fast_fp16:
            builder.fp16_mode = True

        # Enable INT8 precision (requires calibration)
        # builder.int8_mode = True
        # builder.calibration_cache = "calibration.cache"

        # Parse ONNX file
        with open(onnx_file_path, 'rb') as model:
            if not parser.parse(model.read()):
                print('Failed to parse the ONNX file.')
                for error in range(parser.num_errors):
                    print(parser.get_error(error))
                return None

        # Build engine
        engine = builder.build_cuda_engine(network)

        # Serialize engine
        with open(engine_file_path, 'wb') as f:
            f.write(engine.serialize())

        return engine

# Build and save engine
engine = build_engine("model.onnx", "model.trt", max_batch_size=32)

# Step 3: Inference with TensorRT Engine
class TensorRTInference:
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.logger = trt.Logger(trt.Logger.WARNING)

        # Deserialize engine
        with open(engine_path, 'rb') as f:
            self.engine = trt.Runtime(self.logger).deserialize_cuda_engine(f.read())

        self.context = self.engine.create_execution_context()

        # Get input/output info
        self.input_size = trt.volume(self.engine.get_binding_shape(0))
        self.output_size = trt.volume(self.engine.get_binding_shape(1))

    def infer(self, input_data):
        # Allocate device memory
        d_input = cuda.mem_alloc(input_data.nbytes)
        d_output = cuda.mem_alloc(self.output_size * 4)  # 4 bytes for float32

        # Copy input to device
        cuda.memcpy_htod(d_input, input_data)

        # Execute inference
        self.context.execute(batch_size=1, bindings=[int(d_input), int(d_output)])

        # Copy output to host
        output = np.empty(self.output_size, dtype=np.float32)
        cuda.memcpy_dtoh(output, d_output)

        # Free device memory
        d_input.free()
        d_output.free()

        return output

# Inference
trt_inferencer = TensorRTInference("model.trt")

test_input = np.random.randn(1, 784).astype(np.float32)
result = trt_inferencer.infer(test_input)
```

#### INT8 Calibration for TensorRT

```python
import tensorrt as trt
import numpy as np
from torch.utils.data import DataLoader

class TensorRTCalibrator(trt.IInt8Calibrator):
    def __init__(self, data_loader, cache_file):
        super().__init__()
        self.data_loader = data_loader
        self.cache_file = cache_file
        self.data_iter = iter(data_loader)

    def get_batch_size(self):
        return self.data_loader.batch_size

    def get_batch(self, names):
        try:
            batch = next(self.data_iter)
            return [batch[0].numpy()]
        except StopIteration:
            return None

    def read_calibration_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return f.read()
        return None

    def write_calibration_cache(self, cache):
        with open(self.cache_file, 'wb') as f:
            f.write(cache)

# Build INT8 engine
def build_int8_engine(onnx_file_path, calibration_data, engine_file_path):
    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

    with trt.Builder(TRT_LOGGER) as builder, \
         builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)) as network, \
         trt.OnnxParser(network, TRT_LOGGER) as parser:

        builder.int8_mode = True
        builder.int8_calibrator = TensorRTCalibrator(calibration_data, "calibration.cache")
        builder.max_workspace_size = 1 << 30

        with open(onnx_file_path, 'rb') as model:
            parser.parse(model.read())

        engine = builder.build_cuda_engine(network)

        with open(engine_file_path, 'wb') as f:
            f.write(engine.serialize())

        return engine
```

---

## Model Compression Techniques

### Techniques Summary

| Technique | Speedup | Memory Reduction | Complexity |
|-----------|---------|-----------------|-----------|
| Quantization (INT8) | 3-4x | 75% | Low |
| Pruning (30%) | 1.2x | 30% | Medium |
| Pruning (90%) | 5x | 90% | High |
| Distillation | 2-3x | 50% | Medium |
| Low-Rank Factorization | 2-3x | 40% | Medium |
| Combined | 10-100x | 95%+ | High |

### Low-Rank Decomposition

```python
import torch
import torch.nn as nn
from torch.linalg import svd

class LowRankLinear(nn.Module):
    def __init__(self, in_features, out_features, rank=16):
        super().__init__()
        self.fc_u = nn.Linear(in_features, rank)
        self.fc_v = nn.Linear(rank, out_features)

    def forward(self, x):
        x = self.fc_u(x)
        x = self.fc_v(x)
        return x

# Decompose original linear layer
def decompose_linear_layer(linear_layer, rank=16):
    """Decompose weight matrix using SVD"""

    weight = linear_layer.weight.data  # [out_features, in_features]

    # SVD decomposition
    U, S, Vh = svd(weight, full_matrices=False)

    # Keep top-k singular values
    U = U[:, :rank]
    S = S[:rank]
    Vh = Vh[:rank, :]

    # Create low-rank approximation
    W_low_rank = U @ torch.diag(S) @ Vh

    compression_ratio = weight.numel() / (U.numel() + Vh.numel())

    return U, S, Vh, compression_ratio

# Apply to model
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

# Replace layers with low-rank versions
def apply_low_rank(model, rank=64):
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            U, S, Vh, ratio = decompose_linear_layer(module, rank)
            print(f"{name}: compression {ratio:.1f}x")
```

### Knowledge Distillation + Quantization Pipeline

```python
def combined_optimization_pipeline(
    teacher_model,
    student_config,
    train_loader,
    val_loader,
    epochs=10
):
    """
    Combined: Knowledge Distillation + Quantization
    """

    # Step 1: Knowledge Distillation
    student = student_config
    student = train_with_distillation(teacher_model, student, train_loader, epochs)

    # Step 2: Pruning
    prune_model(student, pruning_amount=0.3)

    # Step 3: Quantization-Aware Training
    quantize_aware_student = torch.quantization.quantize_dynamic(student, {nn.Linear}, dtype=torch.qint8)

    # Step 4: Export to ONNX
    torch.onnx.export(quantize_aware_student, torch.randn(1, 784), "student_optimized.onnx")

    # Step 5: TensorRT Conversion
    build_engine("student_optimized.onnx", "student_optimized.trt")

    return student
```

---

## Inference Optimization

### Batch Processing

```python
def batch_inference(model, data_loader, batch_size=32):
    """Optimized batch inference"""
    model.eval()
    results = []

    with torch.no_grad():
        for images in data_loader:
            # Batch processing is faster than single samples
            outputs = model(images)
            results.append(outputs)

    return torch.cat(results, dim=0)
```

### Mixed Precision Inference

```python
import torch
from torch.cuda.amp import autocast

@autocast()  # Automatic mixed precision
def inference_mixed_precision(model, inputs):
    return model(inputs)

# Or with explicit context
with torch.cuda.amp.autocast():
    output = model(inputs)
```

### Model Caching & Compilation

```python
# PyTorch 2.0+ Model Compilation
model = MyModel()
optimized_model = torch.compile(model, mode="reduce-overhead")

# Inference is now faster due to compilation
output = optimized_model(input_tensor)
```

### Asynchronous Inference

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncInference:
    def __init__(self, model, num_workers=4):
        self.model = model
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    async def predict_async(self, input_data):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.model,
            input_data
        )
```

---

## Benchmarking Tools

### PyTorch Benchmarking

```python
import torch
import time
from torch.profiler import profile, record_function, ProfilerActivity

# 1. Simple timing
def benchmark_model(model, inputs, num_runs=100):
    model.eval()

    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(inputs)

    # Benchmark
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    times = []
    with torch.no_grad():
        for _ in range(num_runs):
            start.record()
            _ = model(inputs)
            end.record()
            torch.cuda.synchronize()
            times.append(start.elapsed_time(end))

    mean_time = sum(times) / len(times)
    median_time = sorted(times)[len(times) // 2]

    return {
        'mean': mean_time,
        'median': median_time,
        'min': min(times),
        'max': max(times)
    }

# 2. Detailed profiling
def profile_model(model, inputs):
    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        record_shapes=True,
        profile_memory=True
    ) as prof:
        with record_function("model_inference"):
            model(inputs)

    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

# 3. Memory profiling
def memory_benchmark(model, inputs):
    torch.cuda.reset_peak_memory_stats()

    with torch.no_grad():
        model(inputs)

    peak_memory = torch.cuda.max_memory_allocated() / 1024**2  # MB
    return peak_memory

# 4. Throughput benchmark
def throughput_benchmark(model, batch_sizes=[1, 4, 8, 16, 32], num_batches=10):
    results = {}

    model.eval()

    for batch_size in batch_sizes:
        inputs = torch.randn(batch_size, 3, 224, 224)

        if torch.cuda.is_available():
            inputs = inputs.cuda()
            model = model.cuda()

        # Warmup
        with torch.no_grad():
            for _ in range(5):
                _ = model(inputs)

        # Benchmark
        start = time.time()
        with torch.no_grad():
            for _ in range(num_batches):
                _ = model(inputs)
        elapsed = time.time() - start

        throughput = (batch_size * num_batches) / elapsed  # samples/sec
        latency = elapsed / num_batches * 1000  # ms per batch

        results[batch_size] = {
            'throughput': throughput,
            'latency': latency
        }

    return results
```

### ONNX Runtime Benchmarking

```python
import onnxruntime as ort
import time
import numpy as np

def benchmark_onnx(model_path, input_shape=(1, 3, 224, 224), num_runs=100):
    """Benchmark ONNX model"""

    sess = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider'])

    input_name = sess.get_inputs()[0].name
    input_data = np.random.randn(*input_shape).astype(np.float32)

    # Warmup
    for _ in range(10):
        sess.run(None, {input_name: input_data})

    # Benchmark
    start = time.perf_counter()
    for _ in range(num_runs):
        sess.run(None, {input_name: input_data})
    elapsed = time.perf_counter() - start

    avg_latency = elapsed / num_runs * 1000  # ms
    throughput = num_runs / elapsed  # inferences/sec

    return {
        'latency_ms': avg_latency,
        'throughput_fps': throughput
    }

def compare_models(models_dict, input_shape=(1, 3, 224, 224)):
    """Compare performance of multiple models"""

    results = {}

    for name, model_path in models_dict.items():
        metrics = benchmark_onnx(model_path, input_shape)
        results[name] = metrics
        print(f"{name}:")
        print(f"  Latency: {metrics['latency_ms']:.2f} ms")
        print(f"  Throughput: {metrics['throughput_fps']:.2f} fps")

    return results
```

### Comparison Framework

```python
class BenchmarkComparison:
    def __init__(self):
        self.results = {}

    def benchmark_pytorch(self, model, inputs, name="PyTorch"):
        metrics = benchmark_model(model, inputs)
        self.results[name] = metrics

    def benchmark_onnx(self, model_path, inputs, name="ONNX"):
        metrics = benchmark_onnx(model_path, inputs.shape)
        self.results[name] = metrics

    def benchmark_tensorrt(self, engine_path, inputs, name="TensorRT"):
        # Implementation for TensorRT
        pass

    def report(self):
        print("\n=== Benchmark Comparison ===")
        baseline = list(self.results.values())[0]['latency_ms']

        for name, metrics in self.results.items():
            latency = metrics['latency_ms']
            speedup = baseline / latency
            print(f"{name}: {latency:.3f}ms ({speedup:.2f}x speedup)")
```

---

## Production Workflows

### Complete Optimization Pipeline

```python
import yaml

class OptimizationPipeline:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def run(self):
        """Execute full optimization pipeline"""

        print("Step 1: Loading model...")
        model = self._load_model()

        print("Step 2: Knowledge distillation...")
        if self.config['distillation']['enabled']:
            model = self._apply_distillation(model)

        print("Step 3: Pruning...")
        if self.config['pruning']['enabled']:
            model = self._apply_pruning(model)

        print("Step 4: Quantization...")
        if self.config['quantization']['enabled']:
            model = self._apply_quantization(model)

        print("Step 5: ONNX conversion...")
        if self.config['onnx']['enabled']:
            model = self._convert_to_onnx(model)

        print("Step 6: TensorRT optimization...")
        if self.config['tensorrt']['enabled']:
            model = self._convert_to_tensorrt(model)

        print("Step 7: Benchmarking...")
        metrics = self._benchmark(model)

        print("Step 8: Deployment...")
        self._deploy(model, metrics)

        return model, metrics

    def _load_model(self):
        # Implementation
        pass

    def _apply_distillation(self, model):
        # Implementation
        pass

    def _apply_pruning(self, model):
        # Implementation
        pass

    def _apply_quantization(self, model):
        # Implementation
        pass

    def _convert_to_onnx(self, model):
        # Implementation
        pass

    def _convert_to_tensorrt(self, model):
        # Implementation
        pass

    def _benchmark(self, model):
        # Implementation
        pass

    def _deploy(self, model, metrics):
        # Implementation
        pass
```

### Configuration File Example

```yaml
optimization:
  target_latency_ms: 50
  target_throughput_fps: 20
  max_accuracy_loss: 0.5  # percent

distillation:
  enabled: true
  temperature: 4.0
  alpha: 0.7
  teacher_model: /path/to/teacher.pt

pruning:
  enabled: true
  method: "magnitude"  # magnitude, structured
  target_sparsity: 0.3
  iterative: true
  num_iterations: 10

quantization:
  enabled: true
  method: "qat"  # ptq, qat
  precision: "int8"  # int8, int4
  calibration_samples: 1000

onnx:
  enabled: true
  opset_version: 14
  optimize: true

tensorrt:
  enabled: true
  precision: "fp16"  # fp32, fp16, int8
  max_workspace_gb: 1
  max_batch_size: 32

deployment:
  target_device: "nvidia_a100"
  framework: "tensorrt"
  batch_processing: true
  async_inference: true
```

### Production Monitoring

```python
import logging
from prometheus_client import Counter, Histogram, Gauge
import time

class OptimizationMonitor:
    def __init__(self):
        self.inference_latency = Histogram(
            'inference_latency_ms',
            'Inference latency in milliseconds',
            buckets=[5, 10, 25, 50, 100, 250, 500, 1000]
        )
        self.inference_errors = Counter(
            'inference_errors_total',
            'Total number of inference errors'
        )
        self.model_accuracy = Gauge(
            'model_accuracy',
            'Model accuracy on validation set'
        )
        self.gpu_memory = Gauge(
            'gpu_memory_mb',
            'GPU memory usage in MB'
        )

    def record_inference(self, latency_ms, success=True):
        if success:
            self.inference_latency.observe(latency_ms)
        else:
            self.inference_errors.inc()

    def record_accuracy(self, accuracy):
        self.model_accuracy.set(accuracy)

    def record_memory(self, memory_mb):
        self.gpu_memory.set(memory_mb)

# Usage
monitor = OptimizationMonitor()

def inference_with_monitoring(model, inputs):
    start = time.time()
    try:
        outputs = model(inputs)
        latency = (time.time() - start) * 1000
        monitor.record_inference(latency, success=True)
        return outputs
    except Exception as e:
        monitor.record_inference(0, success=False)
        raise e
```

---

## Best Practices

### From NVIDIA

1. **Profile First**: Use NVIDIA Nsight to identify bottlenecks
2. **Mixed Precision**: Use FP16 for faster computation
3. **Batch Processing**: Larger batches = better throughput
4. **Memory Optimization**: Minimize device memory transfers
5. **Kernel Fusion**: Combine operations to reduce overhead
6. **TensorRT**: Always use for production deployment on NVIDIA GPUs

### From Intel

1. **OpenVINO Toolkit**: Convert to OpenVINO format for optimization
2. **CPU Optimization**: Use AVX-512 instructions when available
3. **Multi-threading**: Leverage multi-core processors
4. **Quantization**: INT8 is standard for CPU inference
5. **Memory Layout**: Use optimized tensor formats (NHWC vs NCHW)
6. **Model Ensemble**: Sometimes faster than single large model

### General Best Practices

1. **Accuracy-Performance Trade-off**:
   - Monitor accuracy throughout optimization
   - Set acceptable accuracy threshold
   - Use validation set for verification

2. **Incremental Optimization**:
   - Apply one optimization at a time
   - Measure impact of each step
   - Combine complementary techniques

3. **Testing Strategy**:
   - Unit tests for individual optimizations
   - Integration tests for complete pipeline
   - Performance regression tests
   - Accuracy validation tests

4. **Version Control**:
   ```
   models/
   ├── baseline/
   │   └── model.pt
   ├── distilled/
   │   └── model.pt
   ├── pruned/
   │   └── model.pt
   ├── quantized/
   │   └── model.pt
   ├── onnx/
   │   └── model.onnx
   └── tensorrt/
       └── model.trt
   ```

5. **Documentation**:
   - Record optimization decisions
   - Document accuracy/performance metrics
   - Keep optimization parameters
   - Track hardware/software dependencies

6. **Continuous Benchmarking**:
   ```python
   def ci_benchmark_suite():
       """Run in CI/CD pipeline"""
       baseline = load_baseline_metrics()
       current = benchmark_optimized_model()

       assert current['latency'] <= baseline['latency'] * 1.05
       assert current['accuracy'] >= baseline['accuracy'] * 0.98
       assert current['memory'] <= baseline['memory'] * 0.9
   ```

7. **A/B Testing in Production**:
   ```python
   def route_inference(request_id):
       if request_id % 2 == 0:
           return baseline_model.predict(request)
       else:
           return optimized_model.predict(request)

       # Monitor both for accuracy and performance
   ```

### Optimization Decision Tree

```
Start
 │
 ├─ Latency bottleneck?
 │   ├─ Yes → TensorRT (GPU) / OpenVINO (CPU)
 │   └─ No → Continue
 │
 ├─ Memory bottleneck?
 │   ├─ Yes → Quantization → Pruning → Distillation
 │   └─ No → Continue
 │
 ├─ Accuracy critical?
 │   ├─ Yes → Distillation → Light quantization
 │   └─ No → Aggressive pruning + quantization
 │
 ├─ Edge deployment?
 │   ├─ Yes → Combine all techniques
 │   └─ No → Focus on throughput
 │
 └─ Deploy and Monitor
```

---

## Summary Table

| Technique | Speedup | Memory | Accuracy Loss | Effort | GPU | CPU |
|-----------|---------|--------|----------------|--------|-----|-----|
| Quantization (INT8) | 3-4x | 75% | < 1% | Low | ✓ | ✓ |
| Quantization (INT4) | 8-10x | 75% | 1-5% | Low | ✓ | ✗ |
| Pruning (30%) | 1.2x | 30% | < 0.5% | Medium | ✓ | ✓ |
| Pruning (90%) | 5x | 90% | 5-10% | High | ✓ | ✓ |
| Distillation | 2-3x | 50% | 1-2% | High | ✓ | ✓ |
| Distillation + Quantization | 10x | 90% | 2-3% | High | ✓ | ✓ |
| ONNX Optimization | 1.2-1.5x | 0% | 0% | Low | ✓ | ✓ |
| TensorRT | 5-10x | 75% | 0-1% | Medium | ✓ | ✗ |

---

## References & Tools

### Tools
- **PyTorch**: `torch.quantization`, `torch.nn.utils.prune`
- **TensorFlow**: `tf.lite`, `tf.quantization`
- **NVIDIA**: TensorRT, NVIDIA Apex, Triton
- **Intel**: OpenVINO Toolkit, Neural Compressor
- **ONNX**: ONNX Runtime, ONNX Model Zoo

### Frameworks
- NVIDIA TensorRT
- ONNX Runtime
- TensorFlow Lite
- OpenVINO
- Apache TVM
- PyTorch Mobile

### Key Papers
- "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic Only Inference" (Google)
- "DistilBERT, a distilled version of BERT" (Hugging Face)
- "Learning both Weights and Connections for Efficient Neural Networks" (Song Han)
- "TensorRT: An Open Source High Performance Deep Learning Inference Platform"

---

## Quick Start Checklist

- [ ] Profile baseline model
- [ ] Set accuracy and latency targets
- [ ] Apply knowledge distillation (if accuracy critical)
- [ ] Apply structured pruning (for GPU)
- [ ] Apply quantization-aware training
- [ ] Convert to ONNX
- [ ] Optimize ONNX graph
- [ ] Convert to TensorRT (if using NVIDIA GPU)
- [ ] Benchmark against targets
- [ ] Deploy with monitoring
- [ ] A/B test in production
- [ ] Document all decisions and metrics
