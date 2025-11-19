# Model Migration & Enhancement Template

## Purpose
Migrate models between frameworks, convert to deployment formats, upgrade model versions, and implement cutting-edge research techniques. Follows best practices from HuggingFace, ONNX Runtime, and framework migration patterns.

## When to Use

- Migrating between ML frameworks (PyTorch ↔ TensorFlow ↔ JAX)
- Converting models to deployment formats (ONNX, TensorRT, TorchScript)
- Upgrading to newer model versions while maintaining compatibility
- Implementing new research techniques (Flash Attention, RoPE, LoRA, etc.)
- Refactoring legacy ML code to modern standards
- Optimizing models for production deployment

## Prerequisites

- [ ] Source model checkpoint available
- [ ] Target framework/format requirements defined
- [ ] Validation dataset for correctness checking
- [ ] Baseline performance metrics documented
- [ ] Deployment constraints known (latency, memory, hardware)

## Configuration

```python
migration_config = {
    # Source
    "source_framework": "pytorch",  # pytorch, tensorflow, jax
    "source_model_path": "checkpoints/model.pt",
    "source_model_class": "ResNet50",

    # Target
    "target_framework": "onnx",  # onnx, tensorrt, torchscript, tensorflow, jax
    "target_model_path": "exports/model.onnx",

    # Migration Settings
    "opset_version": 17,  # For ONNX
    "dynamic_axes": True,  # Support variable batch size
    "optimize_for_inference": True,

    # Validation
    "validation_data": "data/val",
    "tolerance": 1e-4,  # Numerical tolerance for outputs
    "compare_intermediate": True,  # Compare intermediate layer outputs

    # Enhancement (if applicable)
    "enhancements": [
        "quantization",  # int8, fp16
        "flash_attention",  # For transformers
        "lora",  # Parameter-efficient fine-tuning
    ],
}
```

## Migration Patterns

### Pattern 1: PyTorch → ONNX

**Use case**: Deploy PyTorch models in production with ONNX Runtime

```python
import torch
import onnx
import onnxruntime as ort
from onnxsim import simplify
import numpy as np


def export_pytorch_to_onnx(
    model: torch.nn.Module,
    sample_input: torch.Tensor,
    output_path: str,
    opset_version: int = 17,
    dynamic_axes: dict = None,
    simplify_model: bool = True,
):
    """
    Export PyTorch model to ONNX format.

    Args:
        model: PyTorch model
        sample_input: Example input tensor
        output_path: Path to save ONNX model
        opset_version: ONNX opset version
        dynamic_axes: Dict specifying dynamic axes
        simplify_model: Whether to simplify ONNX graph

    Example:
        >>> model = ResNet50()
        >>> sample_input = torch.randn(1, 3, 224, 224)
        >>> export_pytorch_to_onnx(model, sample_input, "model.onnx")
    """
    model.eval()

    # Default dynamic axes (batch size)
    if dynamic_axes is None:
        dynamic_axes = {
            "input": {0: "batch_size"},
            "output": {0: "batch_size"},
        }

    # Export to ONNX
    torch.onnx.export(
        model,
        sample_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes=dynamic_axes,
    )

    # Simplify ONNX graph
    if simplify_model:
        onnx_model = onnx.load(output_path)
        onnx_model_simplified, check = simplify(onnx_model)

        if check:
            onnx.save(onnx_model_simplified, output_path)
            print(f"✓ Simplified ONNX model saved to {output_path}")
        else:
            print("⚠️  Simplification failed, using original model")

    # Validate ONNX model
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print(f"✓ ONNX model validation passed")

    return output_path


def validate_onnx_conversion(
    pytorch_model: torch.nn.Module,
    onnx_path: str,
    test_inputs: list,
    tolerance: float = 1e-4,
):
    """
    Validate ONNX conversion by comparing outputs.

    Args:
        pytorch_model: Original PyTorch model
        onnx_path: Path to ONNX model
        test_inputs: List of test input tensors
        tolerance: Numerical tolerance for comparison
    """
    pytorch_model.eval()

    # Load ONNX model
    ort_session = ort.InferenceSession(
        onnx_path,
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
    )

    print("\n" + "=" * 80)
    print("VALIDATING ONNX CONVERSION")
    print("=" * 80)

    max_diff = 0
    for i, test_input in enumerate(test_inputs):
        # PyTorch inference
        with torch.no_grad():
            pytorch_output = pytorch_model(test_input).cpu().numpy()

        # ONNX inference
        ort_inputs = {ort_session.get_inputs()[0].name: test_input.numpy()}
        onnx_output = ort_session.run(None, ort_inputs)[0]

        # Compare outputs
        diff = np.abs(pytorch_output - onnx_output).max()
        max_diff = max(max_diff, diff)

        print(f"Sample {i+1}: Max difference = {diff:.2e}")

        if diff > tolerance:
            print(f"⚠️  Warning: Difference exceeds tolerance ({tolerance})")

    print(f"\nOverall max difference: {max_diff:.2e}")

    if max_diff <= tolerance:
        print("✓ ONNX conversion validated successfully")
    else:
        print("❌ Validation failed - outputs differ significantly")

    return max_diff <= tolerance


def benchmark_onnx_vs_pytorch(
    pytorch_model: torch.nn.Module,
    onnx_path: str,
    sample_input: torch.Tensor,
    num_runs: int = 100,
):
    """
    Benchmark ONNX vs PyTorch inference speed.

    Args:
        pytorch_model: PyTorch model
        onnx_path: Path to ONNX model
        sample_input: Sample input tensor
        num_runs: Number of benchmark runs
    """
    import time

    pytorch_model.eval()

    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = pytorch_model(sample_input)

    # Benchmark PyTorch
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    start = time.perf_counter()

    with torch.no_grad():
        for _ in range(num_runs):
            _ = pytorch_model(sample_input)

    torch.cuda.synchronize() if torch.cuda.is_available() else None
    pytorch_time = (time.perf_counter() - start) / num_runs * 1000

    # Load ONNX and benchmark
    ort_session = ort.InferenceSession(
        onnx_path,
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
    )

    ort_inputs = {ort_session.get_inputs()[0].name: sample_input.numpy()}

    # Warmup
    for _ in range(10):
        _ = ort_session.run(None, ort_inputs)

    # Benchmark
    start = time.perf_counter()
    for _ in range(num_runs):
        _ = ort_session.run(None, ort_inputs)
    onnx_time = (time.perf_counter() - start) / num_runs * 1000

    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    print(f"PyTorch inference time: {pytorch_time:.2f} ms")
    print(f"ONNX inference time:    {onnx_time:.2f} ms")
    print(f"Speedup:                {pytorch_time / onnx_time:.2f}x")
```

### Pattern 2: PyTorch → TensorRT

**Use case**: Maximum performance on NVIDIA GPUs

```python
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit


def build_tensorrt_engine(
    onnx_path: str,
    engine_path: str,
    precision: str = "fp16",
    max_batch_size: int = 32,
    workspace_size: int = 1 << 30,  # 1GB
):
    """
    Build TensorRT engine from ONNX model.

    Args:
        onnx_path: Path to ONNX model
        engine_path: Path to save TensorRT engine
        precision: Precision mode (fp32, fp16, int8)
        max_batch_size: Maximum batch size
        workspace_size: Maximum workspace size in bytes

    Example:
        >>> build_tensorrt_engine("model.onnx", "model.engine", precision="fp16")
    """
    logger = trt.Logger(trt.Logger.INFO)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    # Parse ONNX
    with open(onnx_path, "rb") as model:
        if not parser.parse(model.read()):
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            raise RuntimeError("Failed to parse ONNX model")

    # Build configuration
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, workspace_size)

    # Set precision
    if precision == "fp16":
        config.set_flag(trt.BuilderFlag.FP16)
        print("✓ FP16 precision enabled")
    elif precision == "int8":
        config.set_flag(trt.BuilderFlag.INT8)
        print("✓ INT8 precision enabled (requires calibration)")

    # Build engine
    print("Building TensorRT engine (this may take a while)...")
    serialized_engine = builder.build_serialized_network(network, config)

    if serialized_engine is None:
        raise RuntimeError("Failed to build TensorRT engine")

    # Save engine
    with open(engine_path, "wb") as f:
        f.write(serialized_engine)

    print(f"✓ TensorRT engine saved to {engine_path}")

    return engine_path


class TensorRTInference:
    """TensorRT inference wrapper."""

    def __init__(self, engine_path: str):
        """
        Initialize TensorRT inference.

        Args:
            engine_path: Path to TensorRT engine
        """
        self.logger = trt.Logger(trt.Logger.WARNING)

        # Load engine
        with open(engine_path, "rb") as f:
            runtime = trt.Runtime(self.logger)
            self.engine = runtime.deserialize_cuda_engine(f.read())

        self.context = self.engine.create_execution_context()

        # Allocate buffers
        self.inputs = []
        self.outputs = []
        self.bindings = []
        self.stream = cuda.Stream()

        for binding in self.engine:
            size = trt.volume(self.engine.get_binding_shape(binding))
            dtype = trt.nptype(self.engine.get_binding_dtype(binding))

            # Allocate host and device buffers
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)

            self.bindings.append(int(device_mem))

            if self.engine.binding_is_input(binding):
                self.inputs.append({"host": host_mem, "device": device_mem})
            else:
                self.outputs.append({"host": host_mem, "device": device_mem})

    def __call__(self, input_data: np.ndarray) -> np.ndarray:
        """
        Run inference.

        Args:
            input_data: Input array

        Returns:
            Output array
        """
        # Copy input to device
        np.copyto(self.inputs[0]["host"], input_data.ravel())
        cuda.memcpy_htod_async(
            self.inputs[0]["device"],
            self.inputs[0]["host"],
            self.stream,
        )

        # Run inference
        self.context.execute_async_v2(
            bindings=self.bindings,
            stream_handle=self.stream.handle,
        )

        # Copy output to host
        cuda.memcpy_dtoh_async(
            self.outputs[0]["host"],
            self.outputs[0]["device"],
            self.stream,
        )

        self.stream.synchronize()

        return self.outputs[0]["host"]
```

### Pattern 3: Framework Migration (PyTorch → JAX)

**Use case**: Leverage JAX's automatic differentiation and compilation

```python
import jax
import jax.numpy as jnp
import torch
from flax import linen as nn
from typing import Dict, Any


def convert_pytorch_to_jax_params(
    pytorch_state_dict: Dict[str, torch.Tensor]
) -> Dict[str, jnp.ndarray]:
    """
    Convert PyTorch state dict to JAX parameters.

    Args:
        pytorch_state_dict: PyTorch state dict

    Returns:
        JAX parameters dict
    """
    jax_params = {}

    for name, param in pytorch_state_dict.items():
        # Convert to numpy then JAX
        numpy_param = param.cpu().numpy()

        # PyTorch uses (out_channels, in_channels) for Conv2D
        # JAX/Flax uses (out_channels, in_channels, H, W)
        # Handle transposition if needed

        if "weight" in name and numpy_param.ndim == 2:
            # Linear layer: transpose for JAX
            numpy_param = numpy_param.T

        jax_params[name] = jnp.array(numpy_param)

    return jax_params


class FlaxResNetBlock(nn.Module):
    """ResNet block in Flax (JAX)."""

    features: int
    stride: int = 1

    @nn.compact
    def __call__(self, x, train: bool = False):
        residual = x

        # Conv1
        x = nn.Conv(
            features=self.features,
            kernel_size=(3, 3),
            strides=(self.stride, self.stride),
            padding="SAME",
        )(x)
        x = nn.BatchNorm(use_running_average=not train)(x)
        x = nn.relu(x)

        # Conv2
        x = nn.Conv(
            features=self.features,
            kernel_size=(3, 3),
            padding="SAME",
        )(x)
        x = nn.BatchNorm(use_running_average=not train)(x)

        # Skip connection
        if self.stride != 1:
            residual = nn.Conv(
                features=self.features,
                kernel_size=(1, 1),
                strides=(self.stride, self.stride),
            )(residual)
            residual = nn.BatchNorm(use_running_average=not train)(residual)

        x = nn.relu(x + residual)
        return x


def migrate_model_pytorch_to_jax():
    """
    Complete migration workflow from PyTorch to JAX.

    Example:
        >>> migrate_model_pytorch_to_jax()
    """
    # 1. Load PyTorch model
    pytorch_model = torch.load("model.pt")
    state_dict = pytorch_model.state_dict()

    # 2. Convert parameters
    jax_params = convert_pytorch_to_jax_params(state_dict)

    # 3. Initialize JAX model
    jax_model = FlaxResNetBlock(features=64)

    # 4. Validate conversion
    # Create same input for both models
    test_input_torch = torch.randn(1, 3, 224, 224)
    test_input_jax = jnp.array(test_input_torch.numpy())

    # PyTorch forward
    pytorch_model.eval()
    with torch.no_grad():
        pytorch_output = pytorch_model(test_input_torch).numpy()

    # JAX forward
    jax_output = jax_model.apply({"params": jax_params}, test_input_jax, train=False)

    # Compare
    diff = jnp.abs(pytorch_output - jax_output).max()
    print(f"Max difference: {diff}")

    if diff < 1e-4:
        print("✓ Migration validated successfully")
    else:
        print("⚠️  Outputs differ - check layer mappings")
```

### Pattern 4: Model Enhancement - Adding Flash Attention

**Use case**: Speed up transformer inference by 2-3x

```python
from flash_attn import flash_attn_func
import torch
import torch.nn as nn


def replace_attention_with_flash_attention(model: nn.Module) -> nn.Module:
    """
    Replace standard attention with Flash Attention.

    Args:
        model: Model with standard attention

    Returns:
        Model with Flash Attention
    """
    for name, module in model.named_modules():
        if isinstance(module, nn.MultiheadAttention):
            # Replace with Flash Attention
            flash_attn = FlashMultiheadAttention(
                embed_dim=module.embed_dim,
                num_heads=module.num_heads,
            )

            # Copy weights
            flash_attn.load_state_dict(module.state_dict())

            # Replace module
            parent_name = ".".join(name.split(".")[:-1])
            child_name = name.split(".")[-1]
            parent = model.get_submodule(parent_name) if parent_name else model
            setattr(parent, child_name, flash_attn)

    return model


class FlashMultiheadAttention(nn.Module):
    """Flash Attention drop-in replacement for nn.MultiheadAttention."""

    def __init__(self, embed_dim: int, num_heads: int):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.qkv = nn.Linear(embed_dim, 3 * embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, query, key, value, attn_mask=None):
        """
        Forward pass with Flash Attention.

        Args:
            query: Query tensor (seq_len, batch, embed_dim)
            key: Key tensor
            value: Value tensor
            attn_mask: Attention mask (optional)

        Returns:
            Output tensor and attention weights (None for Flash Attention)
        """
        seq_len, batch, embed_dim = query.shape

        # Linear projection
        qkv = self.qkv(query)  # (seq_len, batch, 3 * embed_dim)

        # Reshape for multi-head attention
        qkv = qkv.reshape(seq_len, batch, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 1, 0, 3, 4)  # (3, batch, seq_len, num_heads, head_dim)

        q, k, v = qkv[0], qkv[1], qkv[2]

        # Flash Attention
        # Input shape: (batch, seq_len, num_heads, head_dim)
        output = flash_attn_func(q, k, v, causal=False)

        # Reshape output
        output = output.reshape(batch, seq_len, embed_dim)
        output = output.permute(1, 0, 2)  # (seq_len, batch, embed_dim)

        # Output projection
        output = self.out_proj(output)

        return output, None  # Flash Attention doesn't return attention weights
```

### Pattern 5: Model Enhancement - Adding LoRA

**Use case**: Parameter-efficient fine-tuning with <1% trainable parameters

```python
import torch
import torch.nn as nn
from typing import Optional


class LoRALinear(nn.Module):
    """
    LoRA (Low-Rank Adaptation) layer.

    Adds trainable low-rank matrices to frozen pre-trained weights.

    Args:
        in_features: Input dimension
        out_features: Output dimension
        rank: Rank of low-rank matrices
        alpha: Scaling factor
        dropout: Dropout probability

    Reference:
        LoRA: Low-Rank Adaptation of Large Language Models
        https://arxiv.org/abs/2106.09685
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 8,
        alpha: int = 16,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.rank = rank
        self.alpha = alpha

        # Frozen pre-trained weights (will be loaded)
        self.weight = nn.Parameter(torch.zeros(out_features, in_features))
        self.weight.requires_grad = False

        # LoRA trainable parameters
        self.lora_A = nn.Parameter(torch.zeros(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))

        # Initialize
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        nn.init.zeros_(self.lora_B)

        self.scaling = self.alpha / self.rank
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor (batch, ..., in_features)

        Returns:
            Output tensor (batch, ..., out_features)
        """
        # Original frozen weights
        result = nn.functional.linear(x, self.weight)

        # LoRA adaptation
        lora_result = (self.dropout(x) @ self.lora_A.T @ self.lora_B.T) * self.scaling

        return result + lora_result


def add_lora_to_model(
    model: nn.Module,
    rank: int = 8,
    alpha: int = 16,
    target_modules: list = ["q_proj", "v_proj"],
) -> nn.Module:
    """
    Add LoRA layers to specific modules in the model.

    Args:
        model: Model to add LoRA to
        rank: LoRA rank
        alpha: LoRA alpha
        target_modules: Names of modules to replace with LoRA

    Returns:
        Model with LoRA layers

    Example:
        >>> model = GPT2Model.from_pretrained("gpt2")
        >>> model = add_lora_to_model(model, rank=8, target_modules=["q_proj", "v_proj"])
        >>> # Only LoRA parameters are trainable now
    """
    for name, module in model.named_modules():
        # Check if this module should be replaced
        if any(target in name for target in target_modules):
            if isinstance(module, nn.Linear):
                # Create LoRA layer
                lora_layer = LoRALinear(
                    in_features=module.in_features,
                    out_features=module.out_features,
                    rank=rank,
                    alpha=alpha,
                )

                # Copy frozen weights
                lora_layer.weight.data = module.weight.data.clone()

                # Replace module
                parent_name = ".".join(name.split(".")[:-1])
                child_name = name.split(".")[-1]
                parent = model.get_submodule(parent_name) if parent_name else model
                setattr(parent, child_name, lora_layer)

    # Freeze all parameters except LoRA
    for name, param in model.named_parameters():
        if "lora_" not in name:
            param.requires_grad = False

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Trainable %: {100 * trainable_params / total_params:.2f}%")

    return model
```

## Validation Suite

After any migration or enhancement, run this validation suite:

```python
def validate_migration(
    original_model,
    migrated_model,
    test_loader,
    tolerance: float = 1e-3,
):
    """
    Comprehensive validation of model migration.

    Args:
        original_model: Original model
        migrated_model: Migrated/enhanced model
        test_loader: Test data loader
        tolerance: Numerical tolerance
    """
    print("\n" + "=" * 80)
    print("MIGRATION VALIDATION")
    print("=" * 80)

    # 1. Output comparison
    print("\n1. Comparing outputs...")
    max_diff = 0

    for batch in test_loader:
        inputs, _ = batch

        # Original
        with torch.no_grad():
            original_output = original_model(inputs)

        # Migrated
        with torch.no_grad():
            migrated_output = migrated_model(inputs)

        diff = (original_output - migrated_output).abs().max().item()
        max_diff = max(max_diff, diff)

    print(f"   Max output difference: {max_diff:.2e}")

    if max_diff < tolerance:
        print("   ✓ Output validation passed")
    else:
        print(f"   ⚠️  Output difference exceeds tolerance ({tolerance})")

    # 2. Performance comparison
    print("\n2. Comparing performance...")
    # (Implement accuracy/metric comparison)

    # 3. Inference speed
    print("\n3. Comparing inference speed...")
    # (Implement latency comparison)

    # 4. Memory usage
    print("\n4. Comparing memory usage...")
    # (Implement memory comparison)
```

## Success Criteria

Migration/enhancement is complete when:

- [ ] **Conversion**: Model successfully converted to target format
- [ ] **Validation**: Outputs match original within tolerance
- [ ] **Performance**: Metrics equivalent or better
- [ ] **Speed**: Inference latency meets requirements
- [ ] **Memory**: Memory usage within constraints
- [ ] **Documentation**: Changes documented with examples
- [ ] **Tests**: Validation tests passing

## Rollback Plan

If migration fails:

1. **Keep original model**: Never delete source until validated
2. **Document issues**: Log what failed and why
3. **Incremental approach**: Migrate one component at a time
4. **Fallback deployment**: Keep original model in production

## Best Practices

### From HuggingFace
- Use standardized conversion utilities
- Validate numerically before deployment
- Document model card updates
- Version converted models separately

### From ONNX
- Use latest opset version when possible
- Simplify graphs for efficiency
- Test with multiple batch sizes
- Profile before and after

### Production Checklist
- [ ] Original and migrated models produce same results
- [ ] Performance improvements measured and documented
- [ ] Deployment infrastructure supports new format
- [ ] Rollback procedure tested
- [ ] Model versioning updated
- [ ] Documentation updated

## Common Migration Issues

**Issue: Numerical differences in outputs**
- Check for different default behaviors (dropout, batchnorm)
- Verify layer order and connections
- Compare intermediate activations
- Check for precision differences (FP32 vs FP16)

**Issue: Unsupported operations in target framework**
- Find equivalent operations
- Implement custom ops if needed
- Consider alternative architectures
- Check framework compatibility matrices

**Issue: Performance degradation after migration**
- Profile to find bottlenecks
- Enable framework-specific optimizations
- Consider quantization or pruning
- Verify batch processing is optimal
