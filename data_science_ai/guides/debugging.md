# ML Debugging Guide

A comprehensive guide to diagnosing and fixing common machine learning issues with practical diagnostic code and systematic debugging workflows.

## Table of Contents

1. [Systematic Debugging Workflow](#systematic-debugging-workflow)
2. [Training Issues](#training-issues)
3. [Data Loading Problems](#data-loading-problems)
4. [Memory Issues](#memory-issues)
5. [Gradient Problems](#gradient-problems)
6. [Learning Rate Tuning](#learning-rate-tuning)
7. [Batch Size Selection](#batch-size-selection)
8. [Debugging Tools and Techniques](#debugging-tools-and-techniques)
9. [Visualization for Debugging](#visualization-for-debugging)
10. [Common Mistakes and Solutions](#common-mistakes-and-solutions)

---

## Systematic Debugging Workflow

When your model isn't performing as expected, follow this systematic approach:

### 1. **Sanity Check Phase**
```python
def sanity_check(model, data_loader, device='cuda'):
    """
    Perform basic sanity checks on your model setup.
    """
    print("=== SANITY CHECK ===\n")

    # Check 1: Model parameters exist and have gradients
    print("1. Checking model parameters:")
    param_count = 0
    for name, param in model.named_parameters():
        param_count += param.numel()
        if not param.requires_grad:
            print(f"   WARNING: {name} does not require grad!")
        if param.grad is None and param.requires_grad:
            print(f"   ✓ {name}: {param.shape} (no grad yet - normal)")
    print(f"   Total trainable parameters: {param_count:,}\n")

    # Check 2: Data loading
    print("2. Checking data loading:")
    try:
        batch = next(iter(data_loader))
        if isinstance(batch, (tuple, list)):
            for i, item in enumerate(batch):
                if hasattr(item, 'shape'):
                    print(f"   Item {i}: shape {item.shape}, dtype {item.dtype}")
        print("   ✓ Data loading works\n")
    except Exception as e:
        print(f"   ✗ Data loading failed: {e}\n")
        return False

    # Check 3: Forward pass
    print("3. Checking forward pass:")
    try:
        model.eval()
        with torch.no_grad():
            batch = next(iter(data_loader))
            if isinstance(batch, (tuple, list)):
                x, y = batch[0].to(device), batch[1].to(device) if len(batch) > 1 else None
            output = model(x)
            print(f"   ✓ Forward pass works, output shape: {output.shape}\n")
    except Exception as e:
        print(f"   ✗ Forward pass failed: {e}\n")
        return False

    # Check 4: Backward pass
    print("4. Checking backward pass:")
    try:
        model.train()
        batch = next(iter(data_loader))
        if isinstance(batch, (tuple, list)):
            x, y = batch[0].to(device), batch[1].to(device) if len(batch) > 1 else None
        output = model(x)
        loss = output.mean()  # Dummy loss
        loss.backward()
        print(f"   ✓ Backward pass works\n")

        # Check gradients exist
        has_grads = False
        for param in model.parameters():
            if param.grad is not None:
                has_grads = True
                break
        if has_grads:
            print("   ✓ Gradients computed successfully\n")
        else:
            print("   ✗ No gradients computed!\n")
    except Exception as e:
        print(f"   ✗ Backward pass failed: {e}\n")
        return False

    return True
```

### 2. **Data Validation Phase**
```python
def validate_data(data_loader, max_batches=5):
    """
    Validate data quality and consistency.
    """
    print("=== DATA VALIDATION ===\n")

    for batch_idx, batch in enumerate(data_loader):
        if batch_idx >= max_batches:
            break

        if isinstance(batch, (tuple, list)):
            x, y = batch[0], batch[1] if len(batch) > 1 else None
        else:
            x = batch
            y = None

        print(f"Batch {batch_idx}:")
        print(f"  X shape: {x.shape}, dtype: {x.dtype}")
        print(f"  X range: [{x.min():.4f}, {x.max():.4f}]")
        print(f"  X mean: {x.mean():.4f}, std: {x.std():.4f}")

        if torch.isnan(x).any():
            print(f"  ✗ NaN values detected in X!")
        if torch.isinf(x).any():
            print(f"  ✗ Inf values detected in X!")

        if y is not None:
            print(f"  Y shape: {y.shape}, dtype: {y.dtype}")
            if hasattr(y, 'unique'):
                print(f"  Y unique values: {y.unique()}")
            if torch.isnan(y).any():
                print(f"  ✗ NaN values detected in Y!")
        print()
```

### 3. **Training Dynamics Phase**
```python
def check_training_dynamics(model, data_loader, optimizer, criterion, device='cuda', num_batches=10):
    """
    Check basic training dynamics on a few batches.
    """
    print("=== TRAINING DYNAMICS ===\n")

    model.train()
    losses = []

    for batch_idx, batch in enumerate(data_loader):
        if batch_idx >= num_batches:
            break

        if isinstance(batch, (tuple, list)):
            x, y = batch[0].to(device), batch[1].to(device)
        else:
            x = batch.to(device)
            y = None

        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y) if y is not None else output.mean()

        print(f"Batch {batch_idx}: loss = {loss.item():.6f}")

        if torch.isnan(loss):
            print("  ✗ NaN loss detected!")
            break

        loss.backward()

        # Check gradient statistics
        grad_norm = 0.0
        param_count = 0
        for param in model.parameters():
            if param.grad is not None:
                grad_norm += param.grad.data.norm(2).item() ** 2
                param_count += 1

        if param_count > 0:
            grad_norm = grad_norm ** 0.5
            print(f"  Gradient norm: {grad_norm:.6f}")

        optimizer.step()
        losses.append(loss.item())

    if len(losses) > 1:
        loss_change = (losses[-1] - losses[0]) / abs(losses[0]) * 100
        print(f"\nLoss change: {loss_change:.2f}%")
        if loss_change > 0:
            print("✗ Loss is increasing!")
        else:
            print("✓ Loss is decreasing")
```

---

## Training Issues

### Loss Not Decreasing

**Symptoms:**
- Loss plateaus immediately
- Loss oscillates without improvement
- Loss decreases very slowly

**Diagnostic Code:**
```python
def diagnose_no_improvement(model, data_loader, optimizer, criterion,
                           device='cuda', num_epochs=3):
    """
    Diagnose why loss isn't decreasing.
    """
    print("=== DIAGNOSING NO IMPROVEMENT ===\n")

    # 1. Check if model is trainable
    print("1. Model trainable mode:")
    print(f"   model.training = {model.training}")
    model.train()
    print()

    # 2. Check learning rate
    print("2. Learning rate check:")
    for param_group in optimizer.param_groups:
        print(f"   Current LR: {param_group['lr']}")
    print()

    # 3. Check weight updates
    print("3. Weight update check:")
    initial_weights = {}
    for name, param in model.named_parameters():
        if param.requires_grad:
            initial_weights[name] = param.data.clone()

    # One training step
    batch = next(iter(data_loader))
    if isinstance(batch, (tuple, list)):
        x, y = batch[0].to(device), batch[1].to(device)
    else:
        x = batch.to(device)
        y = None

    optimizer.zero_grad()
    output = model(x)
    loss = criterion(output, y) if y is not None else output.mean()
    loss.backward()
    optimizer.step()

    print("   Weight changes:")
    max_change = 0
    for name, param in model.named_parameters():
        if param.requires_grad and name in initial_weights:
            change = (param.data - initial_weights[name]).abs().max().item()
            print(f"   {name}: {change:.8f}")
            max_change = max(max_change, change)

    if max_change < 1e-7:
        print("\n   ✗ Weights are not updating! Check:")
        print("      - Learning rate is too small")
        print("      - Optimizer not connected to model parameters")
        print("      - Gradients are zero")
    print()

    # 4. Check for zero gradients
    print("4. Gradient check:")
    zero_grad_layers = []
    for name, param in model.named_parameters():
        if param.grad is not None:
            if (param.grad == 0).all():
                zero_grad_layers.append(name)

    if zero_grad_layers:
        print(f"   ✗ Zero gradients in: {zero_grad_layers}")
    else:
        print("   ✓ Non-zero gradients found")
    print()
```

### NaN Loss

**Symptoms:**
- Loss becomes NaN during training
- Sudden explosion to infinity then NaN
- Model outputs become NaN

**Diagnostic Code:**
```python
def diagnose_nan_loss(model, data_loader, optimizer, criterion, device='cuda'):
    """
    Diagnose and locate NaN issues.
    """
    print("=== DIAGNOSING NAN LOSS ===\n")

    model.train()

    for batch_idx, batch in enumerate(data_loader):
        print(f"\nBatch {batch_idx}:")

        if isinstance(batch, (tuple, list)):
            x, y = batch[0].to(device), batch[1].to(device)
        else:
            x = batch.to(device)
            y = None

        # Check input
        if torch.isnan(x).any():
            print(f"  ✗ NaN in input X")
            print(f"    NaN count: {torch.isnan(x).sum().item()}")
            continue

        # Forward pass
        optimizer.zero_grad()
        output = model(x)

        if torch.isnan(output).any():
            print(f"  ✗ NaN in model output")
            print(f"    Output shape: {output.shape}")
            print(f"    NaN count: {torch.isnan(output).sum().item()}")

            # Find which layer produces NaN
            print("\n  Debugging forward pass:")
            debug_forward(model, x)
            break

        # Loss computation
        loss = criterion(output, y) if y is not None else output.mean()

        if torch.isnan(loss):
            print(f"  ✗ NaN in loss")
            print(f"    Output range: [{output.min():.4f}, {output.max():.4f}]")

            # Check loss calculation
            if hasattr(criterion, '__class__'):
                print(f"    Loss function: {criterion.__class__.__name__}")

            # Possible causes
            print("\n  Possible causes:")
            print("    - Numerical instability in loss function")
            print("    - Extreme output values (check activation functions)")
            print("    - Log of negative/zero values (for NLL loss)")
            print("    - Division by zero or very small numbers")
            break

        print(f"  Loss: {loss.item():.6f}")

        # Check backward pass
        loss.backward()

        if any(param.grad is not None and torch.isnan(param.grad).any()
               for param in model.parameters()):
            print(f"  ✗ NaN in gradients after backward pass")
            break

def debug_forward(model, x):
    """
    Step through forward pass to find NaN.
    """
    current = x

    for name, layer in model.named_children():
        current = layer(current)

        if torch.isnan(current).any():
            print(f"      Layer '{name}' produces NaN!")
            print(f"      Input range: [{current.min():.4f}, {current.max():.4f}]")
            return
```

### Overfitting

**Symptoms:**
- Training loss decreases, validation loss increases
- Model memorizes training data
- High train accuracy, low validation accuracy

**Diagnostic Code:**
```python
def diagnose_overfitting(train_loss_history, val_loss_history,
                        train_acc_history=None, val_acc_history=None):
    """
    Detect and diagnose overfitting.
    """
    print("=== OVERFITTING DIAGNOSIS ===\n")

    # Calculate gap
    if len(train_loss_history) >= 10:
        recent_train = np.mean(train_loss_history[-10:])
        recent_val = np.mean(val_loss_history[-10:])
        gap = recent_val - recent_train

        print(f"Recent train loss (last 10): {recent_train:.6f}")
        print(f"Recent val loss (last 10):   {recent_val:.6f}")
        print(f"Gap: {gap:.6f}")

        if gap > abs(recent_train) * 0.1:
            print("✗ OVERFITTING DETECTED: Val loss > Train loss\n")
        else:
            print("✓ Gap is acceptable\n")

    # Check generalization gap trend
    print("Generalization gap trend:")
    if len(train_loss_history) > 1:
        gaps = np.array(val_loss_history) - np.array(train_loss_history)
        gap_trend = gaps[-1] - gaps[0]
        print(f"  First gap: {gaps[0]:.6f}")
        print(f"  Last gap: {gaps[-1]:.6f}")
        print(f"  Trend: {gap_trend:.6f}")

        if gap_trend > 0:
            print("  ✗ Gap is widening (overfitting worsening)")
        else:
            print("  ✓ Gap is stable or shrinking")
    print()

    # Recommendations
    print("Recommendations for overfitting:")
    print("  1. Add regularization (L1/L2)")
    print("  2. Increase dropout rate")
    print("  3. Data augmentation")
    print("  4. Reduce model capacity")
    print("  5. Early stopping on validation loss")
    print("  6. More training data")
```

### Underfitting

**Symptoms:**
- Both training and validation loss remain high
- Slow convergence
- Model loss converges to suboptimal value

**Diagnostic Code:**
```python
def diagnose_underfitting(train_loss_history, val_loss_history):
    """
    Detect and diagnose underfitting.
    """
    print("=== UNDERFITTING DIAGNOSIS ===\n")

    if len(train_loss_history) < 2:
        print("Insufficient history for diagnosis")
        return

    # Check if loss is still decreasing
    recent_train = np.mean(train_loss_history[-10:]) if len(train_loss_history) >= 10 else train_loss_history[-1]

    print(f"Current train loss: {recent_train:.6f}")

    # Check improvement rate
    if len(train_loss_history) >= 20:
        early_loss = np.mean(train_loss_history[:10])
        recent_loss = np.mean(train_loss_history[-10:])
        improvement = (early_loss - recent_loss) / early_loss * 100

        print(f"Early train loss (first 10): {early_loss:.6f}")
        print(f"Recent train loss (last 10): {recent_loss:.6f}")
        print(f"Improvement: {improvement:.2f}%\n")

        if improvement < 10:
            print("✗ UNDERFITTING DETECTED: Minimal improvement\n")

    # Check if validation is close to training
    recent_val = np.mean(val_loss_history[-10:]) if len(val_loss_history) >= 10 else val_loss_history[-1]
    gap = abs(recent_val - recent_train) / recent_train

    if gap < 0.05:
        print("Note: Small generalization gap suggests underfitting")
        print("(model not complex enough to learn patterns)\n")

    print("Recommendations for underfitting:")
    print("  1. Increase model capacity (more layers/units)")
    print("  2. Remove or reduce regularization")
    print("  3. Increase training epochs")
    print("  4. Reduce learning rate decay")
    print("  5. Try different architecture")
    print("  6. Add features/improve feature engineering")
```

---

## Data Loading Problems

### Identifying Data Loading Issues

**Diagnostic Code:**
```python
def diagnose_data_issues(data_loader, num_batches=5):
    """
    Comprehensive data loading diagnostics.
    """
    print("=== DATA LOADING DIAGNOSTICS ===\n")

    print("1. Iterator test:")
    try:
        iterator = iter(data_loader)
        print("   ✓ Iterator created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create iterator: {e}")
        return

    print("\n2. Batch loading test:")
    try:
        batch = next(iterator)
        print(f"   ✓ First batch loaded")
        print(f"   Batch type: {type(batch)}")
    except Exception as e:
        print(f"   ✗ Failed to load batch: {e}")
        return

    print("\n3. Batch content analysis:")
    if isinstance(batch, (tuple, list)):
        print(f"   Batch is tuple/list with {len(batch)} items")
        for i, item in enumerate(batch):
            if hasattr(item, 'shape'):
                print(f"     Item {i}: shape={item.shape}, dtype={item.dtype}")
            else:
                print(f"     Item {i}: {type(item)}")
    elif isinstance(batch, dict):
        print(f"   Batch is dict with keys: {batch.keys()}")
        for k, v in batch.items():
            if hasattr(v, 'shape'):
                print(f"     {k}: shape={v.shape}, dtype={v.dtype}")
    else:
        print(f"   Batch type: {type(batch)}")

    print("\n4. Multiple batches test:")
    try:
        for i in range(min(num_batches, 5)):
            batch = next(iterator)
            if i == 0:
                first_batch_size = batch[0].shape[0] if isinstance(batch, (tuple, list)) else batch.shape[0]
            current_size = batch[0].shape[0] if isinstance(batch, (tuple, list)) else batch.shape[0]

            if current_size != first_batch_size and i < 4:
                print(f"   ✗ Batch {i}: inconsistent size {current_size} (expected {first_batch_size})")
            else:
                print(f"   ✓ Batch {i}: size={current_size}")
    except Exception as e:
        print(f"   ✗ Error loading batches: {e}")

    print("\n5. Value range check:")
    batch = next(iter(data_loader))
    if isinstance(batch, (tuple, list)):
        x = batch[0]
    else:
        x = batch

    print(f"   Min: {x.min():.4f}, Max: {x.max():.4f}")
    print(f"   Mean: {x.mean():.4f}, Std: {x.std():.4f}")
    print(f"   NaN count: {torch.isnan(x).sum().item()}")
    print(f"   Inf count: {torch.isinf(x).sum().item()}")
```

---

## Memory Issues

### Memory Leak Detection

**Diagnostic Code:**
```python
import tracemalloc

def detect_memory_leaks(model, data_loader, optimizer, criterion,
                       device='cuda', num_batches=5):
    """
    Detect memory leaks during training.
    """
    print("=== MEMORY LEAK DETECTION ===\n")

    tracemalloc.start()

    model.train()

    for batch_idx, batch in enumerate(data_loader):
        if batch_idx >= num_batches:
            break

        if isinstance(batch, (tuple, list)):
            x, y = batch[0].to(device), batch[1].to(device)
        else:
            x = batch.to(device)
            y = None

        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y) if y is not None else output.mean()
        loss.backward()
        optimizer.step()

        # Memory check
        current, peak = tracemalloc.get_traced_memory()
        print(f"Batch {batch_idx}: Current={current/1e6:.1f}MB, Peak={peak/1e6:.1f}MB")

        # Cleanup
        del x, y, output, loss
        if device == 'cuda':
            torch.cuda.empty_cache()

    tracemalloc.stop()

def check_gpu_memory(device='cuda'):
    """
    Check GPU memory usage.
    """
    if device == 'cuda' and torch.cuda.is_available():
        print("=== GPU MEMORY STATUS ===\n")
        print(f"Allocated: {torch.cuda.memory_allocated()/1e9:.2f}GB")
        print(f"Reserved:  {torch.cuda.memory_reserved()/1e9:.2f}GB")
        print(f"Available: {torch.cuda.get_device_properties(device).total_memory/1e9:.2f}GB")

        # Clear cache
        torch.cuda.empty_cache()
        print(f"\nAfter cache clear:")
        print(f"Allocated: {torch.cuda.memory_allocated()/1e9:.2f}GB")

def fix_memory_issues():
    """
    Strategies for reducing memory usage.
    """
    print("""
=== MEMORY REDUCTION STRATEGIES ===

1. Reduce batch size:
   - Smaller batches = less memory
   - Trade-off: slower training

2. Enable gradient checkpointing:
   checkpoint_sequential(model, 32, x)

3. Use mixed precision:
   from torch.cuda.amp import autocast
   with autocast():
       output = model(x)

4. Delete intermediate tensors:
   del x, y, intermediate_outputs
   torch.cuda.empty_cache()

5. Use model parallelism for large models:
   model = nn.DataParallel(model)

6. Reduce model size:
   - Fewer layers
   - Smaller hidden dimensions
   - Quantization

7. Use smaller data types:
   - float32 -> float16
   - int32 -> int8
""")
```

---

## Gradient Problems

### Vanishing Gradient

**Symptoms:**
- Gradients become very small (< 1e-6)
- Early layers learn slowly
- Loss plateaus after early training

**Diagnostic Code:**
```python
def diagnose_vanishing_gradients(model, data_loader, optimizer,
                                 criterion, device='cuda'):
    """
    Detect and diagnose vanishing gradients.
    """
    print("=== VANISHING GRADIENT DIAGNOSIS ===\n")

    model.train()
    batch = next(iter(data_loader))

    if isinstance(batch, (tuple, list)):
        x, y = batch[0].to(device), batch[1].to(device)
    else:
        x = batch.to(device)
        y = None

    optimizer.zero_grad()
    output = model(x)
    loss = criterion(output, y) if y is not None else output.mean()
    loss.backward()

    print("Gradient statistics by layer:\n")

    layer_idx = 0
    vanishing_layers = []

    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.data.norm(2).item()
            grad_mean = param.grad.data.mean().item()
            grad_std = param.grad.data.std().item()

            print(f"Layer {layer_idx} ({name}):")
            print(f"  Gradient norm: {grad_norm:.8f}")
            print(f"  Gradient mean: {grad_mean:.8f}")
            print(f"  Gradient std:  {grad_std:.8f}")

            if grad_norm < 1e-6:
                print(f"  ✗ VANISHING GRADIENT!")
                vanishing_layers.append(name)
            print()

            layer_idx += 1

    if vanishing_layers:
        print(f"Vanishing gradient detected in {len(vanishing_layers)} layers!")
        print("\nSolutions:")
        print("  1. Use batch normalization")
        print("  2. Use skip connections (ResNet-style)")
        print("  3. Reduce network depth")
        print("  4. Use ReLU instead of sigmoid/tanh")
        print("  5. Carefully initialize weights (Xavier initialization)")
        print("  6. Use gradient clipping")
    else:
        print("✓ No vanishing gradients detected")

def apply_gradient_clipping(model, max_norm=1.0):
    """
    Clip gradients to prevent explosion.
    """
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
```

### Exploding Gradient

**Symptoms:**
- Gradients become very large (> 1e3)
- Loss becomes NaN/Inf
- Training becomes unstable

**Diagnostic Code:**
```python
def diagnose_exploding_gradients(model, data_loader, optimizer,
                                criterion, device='cuda'):
    """
    Detect and diagnose exploding gradients.
    """
    print("=== EXPLODING GRADIENT DIAGNOSIS ===\n")

    model.train()
    batch = next(iter(data_loader))

    if isinstance(batch, (tuple, list)):
        x, y = batch[0].to(device), batch[1].to(device)
    else:
        x = batch.to(device)
        y = None

    optimizer.zero_grad()
    output = model(x)
    loss = criterion(output, y) if y is not None else output.mean()
    loss.backward()

    print("Gradient check:\n")

    max_grad = 0
    exploding_layers = []

    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.data.norm(2).item()
            max_grad = max(max_grad, grad_norm)

            if grad_norm > 100:
                print(f"✗ Layer {name}: gradient norm = {grad_norm:.2f}")
                exploding_layers.append(name)
            elif grad_norm > 10:
                print(f"⚠ Layer {name}: gradient norm = {grad_norm:.2f}")

    print(f"\nMax gradient norm: {max_grad:.6f}")

    if exploding_layers:
        print(f"\nExploding gradients in {len(exploding_layers)} layers!")
        print("\nSolutions:")
        print("  1. Gradient clipping (max_norm=1.0)")
        print("  2. Reduce learning rate")
        print("  3. Batch normalization")
        print("  4. Careful weight initialization")
        print("  5. Check for NaN in data")
    else:
        print("\n✓ No exploding gradients detected")
```

---

## Learning Rate Tuning

### Finding Optimal Learning Rate

**Diagnostic Code:**
```python
def learning_rate_range_test(model, data_loader, optimizer, criterion,
                           device='cuda', start_lr=1e-5, end_lr=1e-1,
                           num_iters=100):
    """
    LR range test to find optimal learning rate.
    Based on: https://arxiv.org/abs/1506.01186
    """
    print("=== LEARNING RATE RANGE TEST ===\n")

    model.train()
    losses = []
    lrs = []

    # Exponentially increasing LR
    lr_schedule = np.logspace(np.log10(start_lr), np.log10(end_lr), num_iters)

    for iter_idx, lr in enumerate(lr_schedule):
        # Update learning rate
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr

        # Get batch
        batch = next(iter(data_loader))
        if isinstance(batch, (tuple, list)):
            x, y = batch[0].to(device), batch[1].to(device)
        else:
            x = batch.to(device)
            y = None

        # Forward and backward
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y) if y is not None else output.mean()

        if torch.isnan(loss):
            print(f"NaN at LR={lr:.6f}, stopping")
            break

        loss.backward()
        optimizer.step()

        losses.append(loss.item())
        lrs.append(lr)

        if (iter_idx + 1) % 20 == 0:
            print(f"Iter {iter_idx}: LR={lr:.6f}, Loss={loss.item():.6f}")

    # Find best learning rate (steepest descent)
    losses = np.array(losses)
    loss_slopes = np.diff(losses)
    best_idx = np.argmin(loss_slopes)
    best_lr = lrs[best_idx]

    print(f"\nSuggested learning rate: {best_lr:.6f}")
    print(f"Loss at start: {losses[0]:.6f}")
    print(f"Loss at end: {losses[-1]:.6f}")

    return lrs, losses, best_lr

def plot_lr_range_test(lrs, losses):
    """
    Plot learning rate range test results.
    """
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Linear scale
    ax1.plot(lrs, losses)
    ax1.set_xlabel('Learning Rate')
    ax1.set_ylabel('Loss')
    ax1.set_title('LR Range Test (Linear Scale)')
    ax1.grid(True)

    # Log scale
    ax2.semilogx(lrs, losses)
    ax2.set_xlabel('Learning Rate (log scale)')
    ax2.set_ylabel('Loss')
    ax2.set_title('LR Range Test (Log Scale)')
    ax2.grid(True)

    plt.tight_layout()
    return fig
```

### Learning Rate Scheduling

**Diagnostic Code:**
```python
def diagnose_lr_schedule(optimizer, criterion='not_improving'):
    """
    Diagnose learning rate schedule effectiveness.
    """
    print("=== LEARNING RATE SCHEDULE DIAGNOSIS ===\n")

    current_lr = optimizer.param_groups[0]['lr']
    print(f"Current learning rate: {current_lr:.6f}")

    if criterion == 'not_improving':
        print("\nProblem: Loss not improving")
        print("Suggestions:")
        print("  1. Reduce learning rate (multiply by 0.1)")
        print("  2. Use learning rate scheduling:")
        print("     - StepLR: reduce every N epochs")
        print("     - ExponentialLR: decay by factor each epoch")
        print("     - CosineAnnealingLR: cosine decay schedule")
        print("     - ReduceLROnPlateau: reduce when no improvement")

    elif criterion == 'oscillating':
        print("\nProblem: Loss oscillating/diverging")
        print("Suggestions:")
        print("  1. Reduce learning rate")
        print("  2. Use learning rate warmup")
        print("  3. Use gradient clipping")
        print("  4. Use momentum-based optimizer (Adam, SGD+momentum)")

    elif criterion == 'converging_slowly':
        print("\nProblem: Convergence is very slow")
        print("Suggestions:")
        print("  1. Increase learning rate")
        print("  2. Use adaptive learning rate (Adam)")
        print("  3. Use learning rate scheduling")
        print("  4. Check batch size (too small may be noisy)")

# Example implementations
def create_lr_schedule_examples(optimizer, num_epochs):
    """
    Show common learning rate schedules.
    """
    from torch.optim.lr_scheduler import (
        StepLR, ExponentialLR, CosineAnnealingLR, ReduceLROnPlateau
    )

    print("Common learning rate schedules:\n")

    print("1. StepLR - Reduce by factor every N steps")
    print("   scheduler = StepLR(optimizer, step_size=30, gamma=0.1)")

    print("\n2. ExponentialLR - Exponential decay")
    print("   scheduler = ExponentialLR(optimizer, gamma=0.95)")

    print("\n3. CosineAnnealingLR - Cosine annealing")
    print("   scheduler = CosineAnnealingLR(optimizer, T_max=num_epochs)")

    print("\n4. ReduceLROnPlateau - Reduce when stuck")
    print("   scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1,")
    print("                                 patience=10, verbose=True)")

    print("\n5. LambdaLR - Custom schedule")
    print("   lambda_fn = lambda epoch: 0.1 ** (epoch // 30)")
    print("   scheduler = LambdaLR(optimizer, lr_lambda=lambda_fn)")

    print("\n6. Warmup + Cosine (common in transformers)")
    print("   from transformers import get_cosine_schedule_with_warmup")
    print("   scheduler = get_cosine_schedule_with_warmup(")
    print("       optimizer, num_warmup_steps=1000, num_training_steps=100000)")
```

---

## Batch Size Selection

### Batch Size Impact Analysis

**Diagnostic Code:**
```python
def analyze_batch_size_impact(model, data_loader, optimizer, criterion,
                             device='cuda', batch_sizes=[8, 16, 32, 64, 128]):
    """
    Analyze impact of batch size on training.
    """
    print("=== BATCH SIZE IMPACT ANALYSIS ===\n")

    results = {}

    for bs in batch_sizes:
        print(f"Testing batch size: {bs}")

        # Create data loader with specific batch size
        from torch.utils.data import DataLoader, TensorDataset

        # Reconstruct dataset (assuming it's in data_loader)
        # For this example, we sample from existing loader

        # Run a few batches
        model.train()
        total_loss = 0
        total_grad_norm = 0
        num_batches = 0

        for batch in data_loader:
            if isinstance(batch, (tuple, list)):
                x, y = batch[0].to(device), batch[1].to(device)
            else:
                x = batch.to(device)
                y = None

            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y) if y is not None else output.mean()
            loss.backward()

            # Compute gradient norm
            grad_norm = sum(p.grad.data.norm(2)**2 for p in model.parameters()
                           if p.grad is not None) ** 0.5

            total_loss += loss.item()
            total_grad_norm += grad_norm
            num_batches += 1

            if num_batches >= 5:  # Just sample 5 batches
                break

        avg_loss = total_loss / num_batches
        avg_grad_norm = total_grad_norm / num_batches

        results[bs] = {
            'loss': avg_loss,
            'grad_norm': avg_grad_norm
        }

        print(f"  Avg loss: {avg_loss:.6f}")
        print(f"  Avg grad norm: {avg_grad_norm:.6f}\n")

    # Analysis
    print("Analysis:")
    print("  - Larger batches: more stable gradients, less frequent updates")
    print("  - Smaller batches: noisier gradients, more frequent updates")
    print("  - GPU memory: larger batch size uses more memory")
    print("  - Training time: larger batch size trains faster per epoch")

    return results

def diagnose_batch_size(model, train_loss_history):
    """
    Diagnose batch size issues from loss history.
    """
    print("=== BATCH SIZE DIAGNOSIS ===\n")

    if len(train_loss_history) < 20:
        print("Need at least 20 iterations for diagnosis")
        return

    # Calculate loss variance
    loss_variance = np.var(train_loss_history)
    loss_mean = np.mean(train_loss_history)
    cv = np.sqrt(loss_variance) / loss_mean  # Coefficient of variation

    print(f"Loss mean: {loss_mean:.6f}")
    print(f"Loss std: {np.sqrt(loss_variance):.6f}")
    print(f"Coefficient of variation: {cv:.4f}\n")

    if cv > 0.5:
        print("✗ HIGH VARIANCE: Batch size may be too small")
        print("  Recommendations:")
        print("    - Increase batch size")
        print("    - Use gradient accumulation")
        print("    - Consider learning rate warmup")
    elif cv < 0.05:
        print("✓ LOW VARIANCE: Batch size is reasonable or large")
        print("  Note: Very low variance may indicate:")
        print("    - Batch size is very large")
        print("    - Model is underfitting")
    else:
        print("✓ MODERATE VARIANCE: Batch size appears reasonable")
```

---

## Debugging Tools and Techniques

### Hooks for Layer-wise Debugging

**Diagnostic Code:**
```python
class ActivationHook:
    """
    Hook to capture activation statistics.
    """
    def __init__(self):
        self.activation = None

    def __call__(self, model, input, output):
        self.activation = output.detach()

def register_activation_hooks(model):
    """
    Register hooks on all layers to monitor activations.
    """
    hooks = {}

    for name, module in model.named_modules():
        if isinstance(module, (torch.nn.ReLU, torch.nn.Sigmoid,
                              torch.nn.Tanh, torch.nn.Linear)):
            hook = ActivationHook()
            module.register_forward_hook(hook)
            hooks[name] = hook

    return hooks

def print_activation_stats(hooks):
    """
    Print statistics of activations from hooks.
    """
    print("\n=== ACTIVATION STATISTICS ===\n")

    for name, hook in hooks.items():
        if hook.activation is not None:
            act = hook.activation
            print(f"{name}:")
            print(f"  Shape: {act.shape}")
            print(f"  Min: {act.min():.6f}, Max: {act.max():.6f}")
            print(f"  Mean: {act.mean():.6f}, Std: {act.std():.6f}")
            print(f"  Sparsity (zeros): {(act == 0).float().mean():.4f}")
            print()

def watch_tensor(tensor, name=""):
    """
    Print detailed tensor information.
    """
    print(f"\n{name} Statistics:")
    print(f"  Shape: {tensor.shape}")
    print(f"  Dtype: {tensor.dtype}")
    print(f"  Device: {tensor.device}")
    print(f"  Min: {tensor.min():.6f}")
    print(f"  Max: {tensor.max():.6f}")
    print(f"  Mean: {tensor.mean():.6f}")
    print(f"  Std: {tensor.std():.6f}")
    print(f"  NaN count: {torch.isnan(tensor).sum()}")
    print(f"  Inf count: {torch.isinf(tensor).sum()}")
    print(f"  Gradient: {tensor.requires_grad}")
```

### Custom Debugging Context Manager

**Diagnostic Code:**
```python
class DebugMode:
    """
    Context manager for debugging model training.
    """
    def __init__(self, model, watch_layers=None):
        self.model = model
        self.watch_layers = watch_layers or []
        self.hooks = {}
        self.layer_outputs = {}

    def __enter__(self):
        # Register hooks on watched layers
        for name, module in self.model.named_modules():
            for watch_name in self.watch_layers:
                if watch_name in name:
                    def make_hook(layer_name):
                        def hook(m, input, output):
                            self.layer_outputs[layer_name] = output.detach()
                        return hook

                    h = module.register_forward_hook(make_hook(name))
                    self.hooks[name] = h

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove hooks
        for hook in self.hooks.values():
            hook.remove()

    def print_outputs(self):
        """Print captured layer outputs."""
        for name, output in self.layer_outputs.items():
            print(f"{name}:")
            print(f"  Shape: {output.shape}")
            print(f"  Range: [{output.min():.4f}, {output.max():.4f}]")

# Usage example:
# with DebugMode(model, watch_layers=['fc', 'conv']) as debug:
#     output = model(x)
#     debug.print_outputs()
```

---

## Visualization for Debugging

### Loss Curve Analysis

**Diagnostic Code:**
```python
def plot_training_curves(train_loss, val_loss=None, train_acc=None, val_acc=None):
    """
    Plot and analyze training curves.
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2 if val_loss is not None else 1, figsize=(12, 4))

    if not isinstance(axes, np.ndarray):
        axes = [axes]

    # Loss plot
    ax = axes[0]
    ax.plot(train_loss, label='Train Loss', alpha=0.7)
    if val_loss is not None:
        ax.plot(val_loss, label='Val Loss', alpha=0.7)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title('Training Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Detect issues
    if len(train_loss) > 10:
        recent_loss = np.mean(train_loss[-10:])
        early_loss = np.mean(train_loss[:10])

        if recent_loss > early_loss * 0.99:
            ax.axhline(early_loss, color='r', linestyle='--', alpha=0.5, label='Early loss')
            ax.text(0.5, 0.95, 'Loss not improving!', transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.5))

    # Accuracy plot
    if train_acc is not None:
        ax = axes[1] if len(axes) > 1 else plt.gca()
        ax.plot(train_acc, label='Train Acc', alpha=0.7)
        if val_acc is not None:
            ax.plot(val_acc, label='Val Acc', alpha=0.7)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Accuracy')
        ax.set_title('Training Accuracy')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

def plot_gradient_flow(model, data_loader, device='cuda'):
    """
    Visualize gradient flow through layers.
    """
    import matplotlib.pyplot as plt

    batch = next(iter(data_loader))
    if isinstance(batch, (tuple, list)):
        x, y = batch[0].to(device), batch[1].to(device)
    else:
        x = batch.to(device)
        y = None

    model.train()
    output = model(x)
    loss = output.mean()  # Dummy loss
    loss.backward()

    layers = []
    gradients = []

    for name, param in model.named_parameters():
        if param.grad is not None:
            layers.append(name.split('.')[-1])
            grad_norm = param.grad.data.norm(2).item()
            gradients.append(grad_norm)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(len(layers)), gradients)
    ax.set_xticks(range(len(layers)))
    ax.set_xticklabels(layers, rotation=45, ha='right')
    ax.set_ylabel('Gradient Norm')
    ax.set_title('Gradient Flow Across Layers')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig

def plot_weight_distribution(model):
    """
    Visualize weight distributions.
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    weights = []
    for param in model.parameters():
        if len(param.shape) > 1:  # Only weight matrices
            weights.extend(param.data.cpu().flatten().numpy())

    weights = np.array(weights)

    # Histogram
    axes[0, 0].hist(weights, bins=50, edgecolor='black')
    axes[0, 0].set_title('Weight Distribution')
    axes[0, 0].set_xlabel('Value')
    axes[0, 0].set_ylabel('Count')

    # Box plot
    axes[0, 1].boxplot(weights)
    axes[0, 1].set_title('Weight Box Plot')
    axes[0, 1].set_ylabel('Value')

    # Cumulative
    sorted_weights = np.sort(weights)
    axes[1, 0].plot(sorted_weights)
    axes[1, 0].set_title('Cumulative Weights (sorted)')
    axes[1, 0].set_xlabel('Index')
    axes[1, 0].set_ylabel('Value')

    # Statistics
    axes[1, 1].axis('off')
    stats_text = f"""
    Mean: {weights.mean():.6f}
    Std: {weights.std():.6f}
    Min: {weights.min():.6f}
    Max: {weights.max():.6f}
    Median: {np.median(weights):.6f}
    """
    axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, family='monospace')

    plt.tight_layout()
    return fig
```

---

## Common Mistakes and Solutions

### Mistake Summary Table

```python
COMMON_MISTAKES = {
    "Model not set to train mode": {
        "symptoms": ["Loss not decreasing", "No weight updates"],
        "solution": "model.train()  # before training loop",
        "severity": "CRITICAL"
    },

    "Forgot to zero gradients": {
        "symptoms": ["Incorrect loss computation", "Gradient accumulation"],
        "solution": "optimizer.zero_grad()  # before backward()",
        "severity": "CRITICAL"
    },

    "Tensor not on device": {
        "symptoms": ["RuntimeError about device mismatch", "Slow training on CPU"],
        "solution": "x = x.to(device)  # move to correct device",
        "severity": "CRITICAL"
    },

    "No backward pass": {
        "symptoms": ["Weights not updating", "All gradients are None"],
        "solution": "loss.backward()  # compute gradients",
        "severity": "CRITICAL"
    },

    "Wrong loss function": {
        "symptoms": ["NaN loss", "Unexpected loss values"],
        "solution": "Check loss function matches problem type",
        "severity": "HIGH"
    },

    "Data not normalized": {
        "symptoms": ["Numerical instability", "Very large gradients"],
        "solution": "Normalize features to [-1, 1] or [0, 1]",
        "severity": "HIGH"
    },

    "Wrong learning rate": {
        "symptoms": ["Loss not decreasing", "Loss diverging/oscillating"],
        "solution": "Use LR range test to find optimal LR",
        "severity": "HIGH"
    },

    "Batch size too small": {
        "symptoms": ["Very noisy training", "Slow convergence"],
        "solution": "Increase batch size if memory allows",
        "severity": "MEDIUM"
    },

    "Model overfitting": {
        "symptoms": ["Train loss decreases, val loss increases"],
        "solution": "Add regularization, dropout, or data augmentation",
        "severity": "MEDIUM"
    },

    "Memory leak": {
        "symptoms": ["GPU memory increasing over time", "OOM errors"],
        "solution": "Delete intermediate tensors, empty cache",
        "severity": "HIGH"
    },

    "Frozen weights": {
        "symptoms": ["Some layers not updating", "Selective learning"],
        "solution": "Check requires_grad is True for trainable layers",
        "severity": "HIGH"
    },

    "Wrong tensor shape": {
        "symptoms": ["Shape mismatch errors", "Unexpected outputs"],
        "solution": "Print shapes at each layer, use assert statements",
        "severity": "HIGH"
    },
}

def print_mistake_guide():
    """Print all common mistakes and solutions."""
    print("\n=== COMMON MISTAKES AND SOLUTIONS ===\n")

    for mistake, info in COMMON_MISTAKES.items():
        print(f"❌ {mistake}")
        print(f"   Severity: {info['severity']}")
        print(f"   Symptoms: {', '.join(info['symptoms'])}")
        print(f"   Solution: {info['solution']}")
        print()
```

### Quick Debugging Checklist

```python
def quick_debug_checklist():
    """Print quick debugging checklist."""
    print("""
=== QUICK DEBUGGING CHECKLIST ===

Before Training:
[ ] Model is correctly defined (forward pass works)
[ ] Data loader is working (batches load without error)
[ ] Loss function matches problem type
[ ] Optimizer connected to model parameters
[ ] Learning rate is reasonable (not too large/small)

During Training:
[ ] model.train() is called in training loop
[ ] optimizer.zero_grad() called each iteration
[ ] loss.backward() called to compute gradients
[ ] optimizer.step() called to update weights
[ ] Check loss is decreasing (roughly)
[ ] No NaN/Inf in loss or gradients

Debugging Signs:
[ ] If loss doesn't decrease: check LR, data, model
[ ] If loss is NaN: check for numerical instability
[ ] If memory full: reduce batch size or model size
[ ] If training very slow: check device placement
[ ] If overfitting: add regularization
[ ] If underfitting: increase model capacity

After Each Epoch:
[ ] Loss decreased
[ ] Validation loss improved
[ ] No NaN/Inf values
[ ] Memory usage stable
[ ] Training speed reasonable
""")
```

---

## Debugging Workflow Template

```python
import torch
import torch.nn as nn
from torch.optim import Adam
import numpy as np

class DebugTrainer:
    """
    Trainer with built-in debugging capabilities.
    """

    def __init__(self, model, train_loader, val_loader, optimizer, criterion, device='cuda'):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device

        self.train_loss_history = []
        self.val_loss_history = []
        self.train_acc_history = []
        self.val_acc_history = []

    def train_epoch(self, debug=False):
        """Train one epoch with optional debugging."""

        self.model.train()
        epoch_loss = 0
        epoch_acc = 0
        num_batches = 0

        for batch_idx, batch in enumerate(self.train_loader):
            # Data loading
            if isinstance(batch, (tuple, list)):
                x, y = batch[0].to(self.device), batch[1].to(self.device)
            else:
                x = batch.to(self.device)
                y = None

            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(x)
            loss = self.criterion(output, y) if y is not None else output.mean()

            # Check loss
            if debug and torch.isnan(loss):
                print(f"NaN loss at batch {batch_idx}")
                return False

            # Backward pass
            loss.backward()

            # Gradient check
            if debug:
                grad_norm = sum(p.grad.data.norm(2)**2 for p in self.model.parameters()
                               if p.grad is not None) ** 0.5
                if grad_norm > 1000:
                    print(f"Warning: Large gradient norm {grad_norm:.4f} at batch {batch_idx}")

            # Update
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1

            if debug and (batch_idx + 1) % 10 == 0:
                print(f"  Batch {batch_idx + 1}: loss={loss.item():.6f}")

        epoch_loss /= num_batches
        self.train_loss_history.append(epoch_loss)

        return True

    def validate(self):
        """Validate model."""
        self.model.eval()
        epoch_loss = 0
        num_batches = 0

        with torch.no_grad():
            for batch in self.val_loader:
                if isinstance(batch, (tuple, list)):
                    x, y = batch[0].to(self.device), batch[1].to(self.device)
                else:
                    x = batch.to(self.device)
                    y = None

                output = self.model(x)
                loss = self.criterion(output, y) if y is not None else output.mean()
                epoch_loss += loss.item()
                num_batches += 1

        epoch_loss /= num_batches
        self.val_loss_history.append(epoch_loss)

        return epoch_loss

    def train(self, num_epochs=10, debug=False):
        """Full training loop with debugging."""

        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch + 1}/{num_epochs}")

            # Train
            success = self.train_epoch(debug=debug)
            if not success:
                print("Training failed!")
                return

            # Validate
            val_loss = self.validate()

            # Report
            train_loss = self.train_loss_history[-1]
            print(f"Train loss: {train_loss:.6f}, Val loss: {val_loss:.6f}")

            # Check for issues
            if len(self.train_loss_history) > 1:
                if self.train_loss_history[-1] > self.train_loss_history[-2]:
                    print("⚠ Warning: Training loss increased!")

            if val_loss > train_loss * 1.5:
                print("⚠ Warning: Possible overfitting (val_loss >> train_loss)")

    def diagnose(self):
        """Run full diagnostics."""
        print("\n" + "="*50)
        print("RUNNING FULL DIAGNOSTICS")
        print("="*50)

        sanity_check(self.model, self.train_loader, self.device)
        validate_data(self.train_loader, max_batches=2)
        check_training_dynamics(self.model, self.train_loader, self.optimizer,
                              self.criterion, self.device, num_batches=5)

# Usage example:
# trainer = DebugTrainer(model, train_loader, val_loader, optimizer, criterion)
# trainer.diagnose()
# trainer.train(num_epochs=10, debug=True)
```

---

## Reference Links and Resources

- PyTorch Debugging: https://pytorch.org/docs/stable/debug_levels.html
- LR Range Test: https://arxiv.org/abs/1506.01186
- Batch Norm Issues: https://arxiv.org/abs/1502.03167
- Gradient Clipping: https://arxiv.org/abs/1211.1541
- Weight Initialization: https://arxiv.org/abs/1502.01852

## Summary

Key debugging principles:
1. **Systematic approach**: Follow the diagnostic workflow
2. **Check data first**: Most issues come from data problems
3. **Verify model setup**: Ensure model, optimizer, loss are connected
4. **Monitor gradients**: Check for vanishing/exploding gradients
5. **Validate hyperparameters**: LR, batch size, regularization
6. **Use visualization**: Plot loss curves, gradient flow, activations
7. **Test incrementally**: Start simple, add complexity
8. **Keep diagnostics handy**: Use the code snippets provided

Remember: Most training issues have straightforward solutions. The key is systematic diagnosis!
