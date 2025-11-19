# Comprehensive Deep Learning Reference Guide

A production-grade reference for deep learning fundamentals, architectures, and best practices from leading AI organizations.

**Version**: 1.0.0
**Last Updated**: 2024
**Status**: Production-Ready

---

## Table of Contents

1. [Neural Network Fundamentals](#neural-network-fundamentals)
2. [CNN Architectures](#cnn-architectures)
3. [RNN/LSTM/GRU](#rnnlstmgru)
4. [Transformers Architecture](#transformers-architecture)
5. [Training Techniques](#training-techniques)
6. [Optimization Algorithms](#optimization-algorithms)
7. [Distributed Training](#distributed-training)
8. [Mixed Precision Training](#mixed-precision-training)
9. [Production Best Practices](#production-best-practices)
10. [Benchmarking & Profiling](#benchmarking--profiling)

---

## Neural Network Fundamentals

### Perceptrons

The perceptron is the foundational building block of neural networks.

#### Mathematical Definition

```
y = activation(w·x + b)
```

#### Implementation

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class Perceptron(nn.Module):
    """
    Single-layer perceptron.

    Args:
        input_size: Dimension of input features
        output_size: Dimension of output (number of classes)
        activation: Activation function to use
    """

    def __init__(self,
                 input_size: int,
                 output_size: int,
                 activation: str = 'relu'):
        super().__init__()
        self.linear = nn.Linear(input_size, output_size)

        activations = {
            'relu': nn.ReLU(),
            'sigmoid': nn.Sigmoid(),
            'tanh': nn.Tanh(),
            'gelu': nn.GELU(),
        }
        self.activation = activations.get(activation, nn.Identity())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the perceptron."""
        return self.activation(self.linear(x))


class MultiLayerPerceptron(nn.Module):
    """
    Multi-layer fully connected network (MLP).

    Follows Google Research best practices for architecture design.
    """

    def __init__(self,
                 input_size: int,
                 hidden_sizes: list,
                 output_size: int,
                 activation: str = 'relu',
                 dropout_rate: float = 0.1,
                 use_batch_norm: bool = True):
        super().__init__()

        layers = []
        prev_size = input_size

        # Hidden layers
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))

            if use_batch_norm:
                layers.append(nn.BatchNorm1d(hidden_size))

            if activation == 'relu':
                layers.append(nn.ReLU(inplace=True))
            elif activation == 'gelu':
                layers.append(nn.GELU())
            elif activation == 'silu':
                layers.append(nn.SiLU(inplace=True))

            if dropout_rate > 0:
                layers.append(nn.Dropout(dropout_rate))

            prev_size = hidden_size

        # Output layer
        layers.append(nn.Linear(prev_size, output_size))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the MLP."""
        return self.network(x)


# Example usage
if __name__ == "__main__":
    batch_size, input_size = 32, 784
    x = torch.randn(batch_size, input_size)

    mlp = MultiLayerPerceptron(
        input_size=input_size,
        hidden_sizes=[512, 256, 128],
        output_size=10,
        activation='gelu',
        dropout_rate=0.1,
        use_batch_norm=True
    )

    output = mlp(x)
    print(f"Output shape: {output.shape}")  # [32, 10]
```

### Activation Functions

Activation functions introduce non-linearity, enabling networks to learn complex patterns.

#### Common Activation Functions

```python
class ActivationFunctions:
    """
    Comparison of modern activation functions.
    Based on studies from Meta AI and Google Research.
    """

    @staticmethod
    def sigmoid(x: torch.Tensor) -> torch.Tensor:
        """
        Sigmoid: σ(x) = 1 / (1 + e^(-x))
        Range: (0, 1)
        Use case: Binary classification, gate mechanisms
        """
        return torch.sigmoid(x)

    @staticmethod
    def tanh(x: torch.Tensor) -> torch.Tensor:
        """
        Tanh: tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))
        Range: (-1, 1)
        Use case: RNNs, hidden layers
        """
        return torch.tanh(x)

    @staticmethod
    def relu(x: torch.Tensor) -> torch.Tensor:
        """
        ReLU: f(x) = max(0, x)
        Range: [0, ∞)
        Advantages: Computationally efficient, mitigates vanishing gradient
        Use case: Most modern CNNs and MLPs
        """
        return F.relu(x)

    @staticmethod
    def leaky_relu(x: torch.Tensor, negative_slope: float = 0.01) -> torch.Tensor:
        """
        Leaky ReLU: f(x) = max(negative_slope * x, x)
        Advantages: Allows negative gradient flow
        Use case: Deep networks, GANs
        """
        return F.leaky_relu(x, negative_slope=negative_slope)

    @staticmethod
    def gelu(x: torch.Tensor) -> torch.Tensor:
        """
        GELU: Gaussian Error Linear Unit
        Smooth approximation of ReLU
        Use case: Transformers (BERT, GPT), state-of-the-art models
        """
        return F.gelu(x)

    @staticmethod
    def swish(x: torch.Tensor) -> torch.Tensor:
        """
        Swish: f(x) = x * sigmoid(β * x)
        Use case: EfficientNet, modern architectures
        """
        return x * torch.sigmoid(x)

    @staticmethod
    def mish(x: torch.Tensor) -> torch.Tensor:
        """
        Mish: f(x) = x * tanh(softplus(x))
        Use case: Recent architectures, improved training dynamics
        """
        return x * torch.tanh(F.softplus(x))


# Comparison visualization code
import matplotlib.pyplot as plt
import numpy as np

def compare_activations():
    """Visualize activation functions."""
    x_range = np.linspace(-5, 5, 200)
    x_tensor = torch.tensor(x_range, dtype=torch.float32)

    activations = {
        'ReLU': F.relu(x_tensor),
        'Sigmoid': torch.sigmoid(x_tensor),
        'Tanh': torch.tanh(x_tensor),
        'GELU': F.gelu(x_tensor),
        'Swish': x_tensor * torch.sigmoid(x_tensor),
    }

    fig, axes = plt.subplots(1, len(activations), figsize=(15, 3))

    for ax, (name, y) in zip(axes, activations.items()):
        ax.plot(x_range, y.numpy())
        ax.set_title(name)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig
```

### Backpropagation Algorithm

The backpropagation algorithm computes gradients efficiently using the chain rule.

#### Mathematical Foundation

```
For a loss function L and parameters θ:

dL/dθ = dL/dz * dz/dθ  (Chain Rule)

where z = w·x + b (linear transformation)
```

#### Implementation

```python
class BackpropagationDemo:
    """
    Demonstrate backpropagation with detailed gradient flow.
    Useful for understanding how gradients flow through networks.
    """

    @staticmethod
    def simple_network_example():
        """
        Simple 2-layer network showing gradient computation.

        Network:
        x -> [Linear(2, 3)] -> [ReLU] -> [Linear(3, 1)] -> y
        """
        # Input
        x = torch.tensor([[1.0, 2.0]], requires_grad=True)
        y_true = torch.tensor([[1.0]])

        # Create network manually for clarity
        W1 = torch.randn(2, 3, requires_grad=True)
        b1 = torch.zeros(3, requires_grad=True)
        W2 = torch.randn(3, 1, requires_grad=True)
        b2 = torch.zeros(1, requires_grad=True)

        # Forward pass
        z1 = x @ W1 + b1
        a1 = F.relu(z1)
        z2 = a1 @ W2 + b2
        y_pred = z2

        # Loss (MSE)
        loss = ((y_pred - y_true) ** 2).mean()

        # Backward pass (automatic)
        loss.backward()

        # Display gradients
        print(f"Loss: {loss.item():.4f}")
        print(f"dL/dW2: {W2.grad}")
        print(f"dL/dW1: {W1.grad}")

        return loss, W1.grad, W2.grad

    @staticmethod
    def gradient_accumulation_example():
        """
        Show how to accumulate gradients (useful for large batch sizes).
        Based on Meta AI's training techniques.
        """
        model = MultiLayerPerceptron(784, [512, 256], 10)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        # Simulate gradient accumulation
        accumulation_steps = 4

        for step in range(accumulation_steps):
            # Forward
            x = torch.randn(32, 784)
            y = torch.randint(0, 10, (32,))
            output = model(x)
            loss = criterion(output, y)

            # Backward (accumulate)
            loss.backward()

            # Only step optimizer every accumulation_steps
            if (step + 1) % accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()

        return loss
```

---

## CNN Architectures

### ResNet (Residual Networks)

ResNet introduced skip connections, enabling training of very deep networks.

```python
class ResidualBlock(nn.Module):
    """
    Residual block with skip connection.

    Based on He et al., "Deep Residual Learning for Image Recognition" (2015)
    From Meta AI/Microsoft Research.
    """

    def __init__(self,
                 in_channels: int,
                 out_channels: int,
                 stride: int = 1,
                 downsample: bool = False):
        super().__init__()

        self.conv1 = nn.Conv2d(in_channels, out_channels, 3,
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)

        self.conv2 = nn.Conv2d(out_channels, out_channels, 3,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # Skip connection
        if downsample or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        else:
            self.shortcut = nn.Identity()

        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with residual connection:
        y = ReLU(x + F(x))
        """
        identity = x

        # Main path
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        # Skip connection
        out = out + self.shortcut(identity)
        out = self.relu(out)

        return out


class ResNet(nn.Module):
    """
    ResNet backbone for image classification.

    Supports ResNet-18, 34, 50, 101, 152 based on configuration.
    """

    def __init__(self,
                 block: type = ResidualBlock,
                 num_blocks: list = [2, 2, 2, 2],
                 num_classes: int = 1000,
                 in_channels: int = 3):
        super().__init__()

        self.in_channels = 64

        # Initial conv layer
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7,
                              stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        # Residual layers
        self.layer1 = self._make_layer(block, 64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], stride=2)

        # Classification head
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)

        # Weight initialization
        self._init_weights()

    def _make_layer(self,
                    block: type,
                    out_channels: int,
                    num_blocks: int,
                    stride: int) -> nn.Sequential:
        """Create a residual layer with multiple blocks."""
        layers = []

        # First block (may have stride)
        layers.append(block(self.in_channels, out_channels, stride=stride,
                           downsample=(stride != 1)))
        self.in_channels = out_channels

        # Remaining blocks
        for _ in range(1, num_blocks):
            layers.append(block(self.in_channels, out_channels, stride=1))

        return nn.Sequential(*layers)

    def _init_weights(self):
        """Initialize weights following He initialization."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out',
                                       nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through ResNet."""
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x


# Predefined configurations
def resnet18(num_classes: int = 1000) -> ResNet:
    """ResNet-18: 18 layers"""
    return ResNet(ResidualBlock, [2, 2, 2, 2], num_classes)

def resnet34(num_classes: int = 1000) -> ResNet:
    """ResNet-34: 34 layers"""
    return ResNet(ResidualBlock, [3, 4, 6, 3], num_classes)

def resnet50(num_classes: int = 1000) -> ResNet:
    """ResNet-50: 50 layers"""
    return ResNet(ResidualBlock, [3, 4, 6, 3], num_classes)
```

### EfficientNet

EfficientNet scales networks using compound scaling principles.

```python
from collections import namedtuple
from dataclasses import dataclass

@dataclass
class EfficientNetConfig:
    """EfficientNet scaling configuration."""
    width_coefficient: float  # Channel scaling
    depth_coefficient: float  # Layer scaling
    resolution: int           # Input resolution
    dropout_rate: float


# EfficientNet-B0 to B7 configurations
EFFICIENTNET_CONFIGS = {
    'b0': EfficientNetConfig(1.0, 1.0, 224, 0.2),
    'b1': EfficientNetConfig(1.0, 1.1, 240, 0.2),
    'b2': EfficientNetConfig(1.1, 1.2, 260, 0.3),
    'b3': EfficientNetConfig(1.2, 1.4, 300, 0.3),
    'b4': EfficientNetConfig(1.4, 1.8, 380, 0.4),
    'b5': EfficientNetConfig(1.6, 2.2, 456, 0.4),
    'b6': EfficientNetConfig(1.8, 2.6, 528, 0.5),
    'b7': EfficientNetConfig(2.0, 3.1, 600, 0.5),
}


class MBConvBlock(nn.Module):
    """
    Mobile Inverted Bottleneck Convolution (MBConv) block.
    From Google EfficientNet paper.
    """

    def __init__(self,
                 in_channels: int,
                 out_channels: int,
                 kernel_size: int = 3,
                 stride: int = 1,
                 expansion_factor: float = 6.0,
                 dropout_rate: float = 0.2):
        super().__init__()

        expanded_channels = int(in_channels * expansion_factor)
        padding = (kernel_size - 1) // 2

        # Expansion phase
        self.expand_conv = nn.Conv2d(in_channels, expanded_channels, 1, bias=False)
        self.expand_bn = nn.BatchNorm2d(expanded_channels)

        # Depthwise convolution
        self.depthwise_conv = nn.Conv2d(expanded_channels, expanded_channels,
                                       kernel_size, stride=stride, padding=padding,
                                       groups=expanded_channels, bias=False)
        self.depthwise_bn = nn.BatchNorm2d(expanded_channels)

        # Squeeze-and-excitation
        self.se = SqueezeExcitation(expanded_channels)

        # Projection phase
        self.project_conv = nn.Conv2d(expanded_channels, out_channels, 1, bias=False)
        self.project_bn = nn.BatchNorm2d(out_channels)

        # Skip connection
        self.use_skip = (stride == 1 and in_channels == out_channels)
        if self.use_skip:
            self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with skip connection."""
        identity = x

        # Expansion
        out = self.expand_conv(x)
        out = self.expand_bn(out)
        out = F.silu(out, inplace=True)

        # Depthwise
        out = self.depthwise_conv(out)
        out = self.depthwise_bn(out)
        out = F.silu(out, inplace=True)

        # SE block
        out = self.se(out)

        # Projection
        out = self.project_conv(out)
        out = self.project_bn(out)

        # Skip
        if self.use_skip:
            out = self.dropout(out)
            out = out + identity

        return out


class SqueezeExcitation(nn.Module):
    """Squeeze-and-Excitation block for channel attention."""

    def __init__(self, channels: int, reduction: int = 4):
        super().__init__()
        reduced_channels = max(1, channels // reduction)

        self.fc1 = nn.Conv2d(channels, reduced_channels, 1)
        self.fc2 = nn.Conv2d(reduced_channels, channels, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply channel-wise attention."""
        # Global average pooling
        scale = F.adaptive_avg_pool2d(x, 1)

        # Excitation
        scale = F.silu(self.fc1(scale))
        scale = torch.sigmoid(self.fc2(scale))

        return x * scale


class EfficientNet(nn.Module):
    """EfficientNet: Scaling CNNs with Compound Coefficients."""

    def __init__(self,
                 config: EfficientNetConfig,
                 num_classes: int = 1000):
        super().__init__()

        self.config = config
        w = config.width_coefficient
        d = config.depth_coefficient

        # Stem
        self.stem = nn.Sequential(
            nn.Conv2d(3, int(32 * w), 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(int(32 * w)),
            nn.SiLU(inplace=True)
        )

        # MBConv blocks: (in_c, out_c, k_size, stride, expansion, num_repeat)
        block_config = [
            (32, 16, 3, 1, 1, 1),
            (16, 24, 3, 2, 6, 2),
            (24, 40, 5, 2, 6, 2),
            (40, 80, 3, 2, 6, 3),
            (80, 112, 5, 1, 6, 3),
            (112, 192, 5, 2, 6, 4),
            (192, 320, 3, 1, 6, 1),
        ]

        blocks = []
        for in_c, out_c, k, s, e, num_repeat in block_config:
            in_c = int(in_c * w)
            out_c = int(out_c * w)
            num_repeat = int(num_repeat * d)

            for i in range(num_repeat):
                stride = s if i == 0 else 1
                blocks.append(MBConvBlock(in_c if i == 0 else out_c, out_c,
                                         k, stride, e, config.dropout_rate))

        self.blocks = nn.Sequential(*blocks)

        # Head
        self.head = nn.Sequential(
            nn.Conv2d(int(320 * w), int(1280 * w), 1, bias=False),
            nn.BatchNorm2d(int(1280 * w)),
            nn.SiLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(int(1280 * w), num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through EfficientNet."""
        x = self.stem(x)
        x = self.blocks(x)
        x = self.head(x)
        return x
```

### Vision Transformers (ViT)

Vision Transformers apply transformer architecture directly to image patches.

```python
class PatchEmbedding(nn.Module):
    """Convert image to patch embeddings."""

    def __init__(self,
                 img_size: int = 224,
                 patch_size: int = 16,
                 in_channels: int = 3,
                 embed_dim: int = 768):
        super().__init__()

        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2

        self.proj = nn.Conv2d(in_channels, embed_dim,
                             kernel_size=patch_size,
                             stride=patch_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Convert image to patches and embed."""
        x = self.proj(x)  # [B, C, H', W']
        x = x.flatten(2)   # [B, C, N]
        x = x.transpose(1, 2)  # [B, N, C]
        return x


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""

    def __init__(self,
                 embed_dim: int = 768,
                 num_heads: int = 12,
                 attention_dropout: float = 0.0,
                 dropout: float = 0.0):
        super().__init__()

        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(embed_dim, embed_dim * 3)
        self.attn_drop = nn.Dropout(attention_dropout)
        self.proj = nn.Linear(embed_dim, embed_dim)
        self.proj_drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Multi-head self-attention.

        Args:
            x: Input tensor [B, N, C]
            mask: Optional attention mask
        """
        B, N, C = x.shape

        # Linear projection + reshape for multi-head
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # [3, B, num_heads, N, head_dim]
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Scaled dot-product attention
        attn = (q @ k.transpose(-2, -1)) * self.scale

        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))

        attn = attn.softmax(dim=-1)
        attn = self.attn_drop(attn)

        # Combine heads
        x = (attn @ v).transpose(1, 2).reshape(B, N, C)
        x = self.proj(x)
        x = self.proj_drop(x)

        return x


class TransformerBlock(nn.Module):
    """Transformer encoder block (from ViT)."""

    def __init__(self,
                 embed_dim: int = 768,
                 num_heads: int = 12,
                 mlp_ratio: float = 4.0,
                 dropout: float = 0.0,
                 attention_dropout: float = 0.0):
        super().__init__()

        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = MultiHeadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            attention_dropout=attention_dropout,
            dropout=dropout
        )

        self.norm2 = nn.LayerNorm(embed_dim)

        mlp_hidden_dim = int(embed_dim * mlp_ratio)
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, mlp_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden_dim, embed_dim),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Transformer block with pre-normalization."""
        # Self-attention with residual
        x = x + self.attn(self.norm1(x))

        # MLP with residual
        x = x + self.mlp(self.norm2(x))

        return x


class VisionTransformer(nn.Module):
    """
    Vision Transformer (ViT) for image classification.

    Reference: Dosovitskiy et al., "An Image is Worth 16x16 Words" (2021)
    From Google Research.
    """

    def __init__(self,
                 img_size: int = 224,
                 patch_size: int = 16,
                 in_channels: int = 3,
                 num_classes: int = 1000,
                 embed_dim: int = 768,
                 num_heads: int = 12,
                 depth: int = 12,
                 mlp_ratio: float = 4.0,
                 dropout: float = 0.1,
                 attention_dropout: float = 0.0):
        super().__init__()

        self.patch_embed = PatchEmbedding(img_size, patch_size,
                                         in_channels, embed_dim)
        num_patches = self.patch_embed.num_patches

        # Class token
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))

        # Position embeddings
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, embed_dim))
        self.pos_drop = nn.Dropout(dropout)

        # Transformer blocks
        self.blocks = nn.Sequential(*[
            TransformerBlock(
                embed_dim=embed_dim,
                num_heads=num_heads,
                mlp_ratio=mlp_ratio,
                dropout=dropout,
                attention_dropout=attention_dropout
            )
            for _ in range(depth)
        ])

        self.norm = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, num_classes)

        # Initialize weights
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through Vision Transformer."""
        B = x.shape[0]

        # Patch embedding
        x = self.patch_embed(x)  # [B, N, C]

        # Add class token
        cls_tokens = self.cls_token.expand(B, -1, -1)  # [B, 1, C]
        x = torch.cat([cls_tokens, x], dim=1)  # [B, N+1, C]

        # Add position embeddings
        x = x + self.pos_embed
        x = self.pos_drop(x)

        # Transformer blocks
        x = self.blocks(x)

        # Classification
        x = self.norm(x)
        x = x[:, 0]  # Take class token
        x = self.head(x)

        return x
```

---

## RNN/LSTM/GRU

### Recurrent Neural Networks (RNNs)

```python
class SimpleRNN(nn.Module):
    """
    Simple RNN cell for sequence processing.

    h_t = tanh(W_ih @ x_t + b_ih + W_hh @ h_{t-1} + b_hh)
    """

    def __init__(self,
                 input_size: int,
                 hidden_size: int,
                 num_layers: int = 1,
                 dropout: float = 0.0,
                 batch_first: bool = True):
        super().__init__()

        self.rnn = nn.RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=batch_first
        )
        self.hidden_size = hidden_size
        self.num_layers = num_layers

    def forward(self,
                x: torch.Tensor,
                h0: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through RNN.

        Args:
            x: Input [B, T, input_size] if batch_first=True
            h0: Initial hidden state [num_layers, B, hidden_size]

        Returns:
            output: [B, T, hidden_size]
            h_n: [num_layers, B, hidden_size]
        """
        return self.rnn(x, h0)


class LSTMCell(nn.Module):
    """
    LSTM cell implementation.

    Gates:
    - Input gate: i_t = σ(W_ii @ x_t + b_ii + W_hi @ h_{t-1} + b_hi)
    - Forget gate: f_t = σ(W_if @ x_t + b_if + W_hf @ h_{t-1} + b_hf)
    - Cell gate: g_t = tanh(W_ig @ x_t + b_ig + W_hg @ h_{t-1} + b_hg)
    - Output gate: o_t = σ(W_io @ x_t + b_io + W_ho @ h_{t-1} + b_ho)

    State updates:
    - c_t = f_t ⊙ c_{t-1} + i_t ⊙ g_t
    - h_t = o_t ⊙ tanh(c_t)
    """

    def __init__(self,
                 input_size: int,
                 hidden_size: int):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size

        # Input to hidden
        self.weight_ih = nn.Parameter(torch.randn(4 * hidden_size, input_size))
        self.bias_ih = nn.Parameter(torch.zeros(4 * hidden_size))

        # Hidden to hidden
        self.weight_hh = nn.Parameter(torch.randn(4 * hidden_size, hidden_size))
        self.bias_hh = nn.Parameter(torch.zeros(4 * hidden_size))

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize weights using uniform distribution."""
        std = 1.0 / (self.hidden_size ** 0.5)
        for weight in self.parameters():
            weight.data.uniform_(-std, std)

    def forward(self,
                x: torch.Tensor,
                states: Tuple[torch.Tensor, torch.Tensor]) -> Tuple[torch.Tensor, Tuple]:
        """
        Forward pass through LSTM cell.

        Args:
            x: Input [B, input_size]
            states: (h, c) where h and c are [B, hidden_size]

        Returns:
            h_new: [B, hidden_size]
            (h_new, c_new): New states
        """
        h, c = states

        # Compute all gates
        gates = F.linear(x, self.weight_ih, self.bias_ih) + \
                F.linear(h, self.weight_hh, self.bias_hh)

        # Split into 4 gates
        i, f, g, o = gates.chunk(4, 1)

        i = torch.sigmoid(i)  # Input gate
        f = torch.sigmoid(f)  # Forget gate
        g = torch.tanh(g)     # Cell gate
        o = torch.sigmoid(o)  # Output gate

        # Update cell state
        c_new = f * c + i * g

        # Update hidden state
        h_new = o * torch.tanh(c_new)

        return h_new, (h_new, c_new)


class LSTM(nn.Module):
    """
    Multi-layer LSTM for sequence-to-sequence tasks.
    Based on PyTorch's optimized implementation.
    """

    def __init__(self,
                 input_size: int,
                 hidden_size: int,
                 num_layers: int = 1,
                 dropout: float = 0.0,
                 batch_first: bool = True,
                 bidirectional: bool = False):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=batch_first,
            bidirectional=bidirectional
        )

        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional

    def forward(self,
                x: torch.Tensor,
                states: Tuple[torch.Tensor, torch.Tensor] = None) -> Tuple:
        """
        Forward pass through LSTM.

        Args:
            x: [B, T, input_size] if batch_first=True
            states: (h0, c0) or None

        Returns:
            output: [B, T, hidden_size * (2 if bidirectional)]
            (h_n, c_n): Final states
        """
        return self.lstm(x, states)


class GRUCell(nn.Module):
    """
    GRU cell - simplified LSTM with gating mechanism.

    Gates:
    - Reset gate: r_t = σ(W_ir @ x_t + b_ir + W_hr @ h_{t-1} + b_hr)
    - Update gate: z_t = σ(W_iz @ x_t + b_iz + W_hz @ h_{t-1} + b_hz)

    Candidate:
    - h'_t = tanh(W_ih @ x_t + b_ih + r_t ⊙ (W_hh @ h_{t-1} + b_hh))

    Update:
    - h_t = (1 - z_t) ⊙ h'_t + z_t ⊙ h_{t-1}
    """

    def __init__(self,
                 input_size: int,
                 hidden_size: int):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size

        # Gates
        self.weight_ih = nn.Parameter(torch.randn(3 * hidden_size, input_size))
        self.bias_ih = nn.Parameter(torch.zeros(3 * hidden_size))

        self.weight_hh = nn.Parameter(torch.randn(3 * hidden_size, hidden_size))
        self.bias_hh = nn.Parameter(torch.zeros(3 * hidden_size))

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize weights."""
        std = 1.0 / (self.hidden_size ** 0.5)
        for weight in self.parameters():
            weight.data.uniform_(-std, std)

    def forward(self,
                x: torch.Tensor,
                h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through GRU cell.

        Args:
            x: Input [B, input_size]
            h: Hidden state [B, hidden_size]

        Returns:
            h_new: [B, hidden_size]
            h_new: Same as output
        """
        gi = F.linear(x, self.weight_ih, self.bias_ih)
        gh = F.linear(h, self.weight_hh, self.bias_hh)

        i_r, i_z, i_n = gi.chunk(3, 1)
        h_r, h_z, h_n = gh.chunk(3, 1)

        r = torch.sigmoid(i_r + h_r)
        z = torch.sigmoid(i_z + h_z)
        n = torch.tanh(i_n + r * h_n)

        h_new = (1 - z) * n + z * h

        return h_new, h_new


class GRU(nn.Module):
    """Multi-layer GRU for sequence processing."""

    def __init__(self,
                 input_size: int,
                 hidden_size: int,
                 num_layers: int = 1,
                 dropout: float = 0.0,
                 batch_first: bool = True):
        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=batch_first
        )

    def forward(self,
                x: torch.Tensor,
                h0: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through GRU."""
        return self.gru(x, h0)


# Practical example: Sequence classification
class SequenceClassifier(nn.Module):
    """
    LSTM-based sequence classifier for variable-length sequences.
    Useful for NLP tasks like sentiment analysis.
    """

    def __init__(self,
                 vocab_size: int,
                 embedding_dim: int,
                 hidden_size: int,
                 num_classes: int,
                 num_layers: int = 2,
                 dropout: float = 0.3,
                 bidirectional: bool = True):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim)

        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
            bidirectional=bidirectional
        )

        lstm_output_size = hidden_size * (2 if bidirectional else 1)

        self.classifier = nn.Sequential(
            nn.Linear(lstm_output_size, lstm_output_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(lstm_output_size // 2, num_classes)
        )

    def forward(self,
                x: torch.Tensor,
                lengths: torch.Tensor = None) -> torch.Tensor:
        """
        Forward pass with optional sequence packing.

        Args:
            x: [B, T] token indices
            lengths: [B] actual sequence lengths (for packing)
        """
        # Embedding
        x = self.embedding(x)  # [B, T, embed_dim]

        # Pack padded sequences (optimization)
        if lengths is not None:
            x = nn.utils.rnn.pack_padded_sequence(x, lengths.cpu(),
                                                   batch_first=True,
                                                   enforce_sorted=False)

        # LSTM
        lstm_out, (h_n, c_n) = self.lstm(x)

        # Unpack if needed
        if lengths is not None:
            lstm_out, _ = nn.utils.rnn.pad_packed_sequence(lstm_out, batch_first=True)

        # Use last hidden state
        last_hidden = h_n[-1]  # [B, hidden_size]

        # Classify
        output = self.classifier(last_hidden)

        return output
```

---

## Transformers Architecture

### Self-Attention Mechanism

```python
class ScaledDotProductAttention(nn.Module):
    """
    Scaled Dot-Product Attention.

    Attention(Q, K, V) = softmax((Q @ K^T) / sqrt(d_k)) @ V
    """

    def __init__(self, dropout: float = 0.0):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

    def forward(self,
                query: torch.Tensor,
                key: torch.Tensor,
                value: torch.Tensor,
                mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute attention weights and apply to values.

        Args:
            query: [B, num_heads, T_q, d_k]
            key: [B, num_heads, T_k, d_k]
            value: [B, num_heads, T_k, d_v]
            mask: Optional mask for attention

        Returns:
            output: [B, num_heads, T_q, d_v]
            attention_weights: [B, num_heads, T_q, T_k]
        """
        d_k = query.shape[-1]

        # Compute attention scores
        scores = query @ key.transpose(-2, -1) / (d_k ** 0.5)

        # Apply mask (for causal attention, padding, etc.)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        # Softmax
        attention_weights = torch.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply to values
        output = attention_weights @ value

        return output, attention_weights


class MultiHeadAttention(nn.Module):
    """
    Multi-Head Attention (from "Attention is All You Need").

    Allows the model to attend to information from different representation subspaces.
    """

    def __init__(self,
                 d_model: int = 512,
                 num_heads: int = 8,
                 dropout: float = 0.1):
        super().__init__()

        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        self.attention = ScaledDotProductAttention(dropout)
        self.dropout = nn.Dropout(dropout)

    def forward(self,
                query: torch.Tensor,
                key: torch.Tensor,
                value: torch.Tensor,
                mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Multi-head attention forward pass.

        Args:
            query: [B, T_q, d_model]
            key: [B, T_k, d_model]
            value: [B, T_k, d_model]
            mask: Optional attention mask
        """
        B = query.shape[0]

        # Linear projections
        Q = self.W_q(query).reshape(B, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).reshape(B, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).reshape(B, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Attention
        attn_out, attn_weights = self.attention(Q, K, V, mask)

        # Concatenate heads
        attn_out = attn_out.transpose(1, 2).reshape(B, -1, self.d_model)

        # Final linear projection
        output = self.W_o(attn_out)

        return output, attn_weights


class FeedForward(nn.Module):
    """
    Feed-Forward Network (Position-Wise Feed-Forward Network).

    FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
    """

    def __init__(self,
                 d_model: int = 512,
                 d_ff: int = 2048,
                 dropout: float = 0.1,
                 activation: str = 'gelu'):
        super().__init__()

        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'gelu':
            self.activation = nn.GELU()
        elif activation == 'swish':
            self.activation = nn.SiLU()
        else:
            self.activation = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply feed-forward network."""
        return self.linear2(self.dropout(self.activation(self.linear1(x))))


class TransformerEncoder(nn.Module):
    """
    Transformer Encoder Layer (from "Attention is All You Need").

    Applies multi-head attention and feed-forward networks with residual connections.
    """

    def __init__(self,
                 d_model: int = 512,
                 num_heads: int = 8,
                 d_ff: int = 2048,
                 dropout: float = 0.1,
                 activation: str = 'gelu'):
        super().__init__()

        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout, activation)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self,
                x: torch.Tensor,
                mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Transformer encoder forward pass with pre-normalization.

        Args:
            x: [B, T, d_model]
            mask: Optional attention mask
        """
        # Self-attention with residual
        attn_out, attn_weights = self.self_attn(x, x, x, mask)
        x = x + self.dropout(attn_out)
        x = self.norm1(x)

        # Feed-forward with residual
        ff_out = self.feed_forward(x)
        x = x + self.dropout(ff_out)
        x = self.norm2(x)

        return x, attn_weights


class TransformerDecoder(nn.Module):
    """
    Transformer Decoder Layer.

    Includes self-attention, cross-attention to encoder, and feed-forward.
    """

    def __init__(self,
                 d_model: int = 512,
                 num_heads: int = 8,
                 d_ff: int = 2048,
                 dropout: float = 0.1,
                 activation: str = 'gelu'):
        super().__init__()

        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout, activation)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self,
                x: torch.Tensor,
                encoder_output: torch.Tensor,
                self_attn_mask: torch.Tensor = None,
                cross_attn_mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Decoder forward pass.

        Args:
            x: Decoder input [B, T_tgt, d_model]
            encoder_output: Encoder output [B, T_src, d_model]
            self_attn_mask: Causal mask for decoder
            cross_attn_mask: Padding mask for encoder
        """
        # Self-attention on decoder inputs
        self_attn_out, self_attn_weights = self.self_attn(x, x, x, self_attn_mask)
        x = x + self.dropout(self_attn_out)
        x = self.norm1(x)

        # Cross-attention to encoder
        cross_attn_out, cross_attn_weights = self.cross_attn(
            x, encoder_output, encoder_output, cross_attn_mask
        )
        x = x + self.dropout(cross_attn_out)
        x = self.norm2(x)

        # Feed-forward
        ff_out = self.feed_forward(x)
        x = x + self.dropout(ff_out)
        x = self.norm3(x)

        return x, self_attn_weights, cross_attn_weights


class PositionalEncoding(nn.Module):
    """
    Positional Encoding using sinusoidal functions.

    PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """

    def __init__(self,
                 d_model: int = 512,
                 max_len: int = 5000):
        super().__init__()

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() *
                            -(math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to embeddings."""
        return x + self.pe[:, :x.shape[1], :]


class Transformer(nn.Module):
    """
    Complete Transformer model for sequence-to-sequence tasks.

    Based on "Attention is All You Need" (Vaswani et al., 2017)
    From Google Brain.
    """

    def __init__(self,
                 src_vocab_size: int,
                 tgt_vocab_size: int,
                 d_model: int = 512,
                 num_heads: int = 8,
                 num_encoder_layers: int = 6,
                 num_decoder_layers: int = 6,
                 d_ff: int = 2048,
                 max_len: int = 5000,
                 dropout: float = 0.1):
        super().__init__()

        self.d_model = d_model

        # Embeddings
        self.src_embed = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embed = nn.Embedding(tgt_vocab_size, d_model)
        self.pos_enc = PositionalEncoding(d_model, max_len)

        # Encoder
        self.encoder = nn.Sequential(*[
            TransformerEncoder(d_model, num_heads, d_ff, dropout)
            for _ in range(num_encoder_layers)
        ])

        # Decoder
        self.decoder = nn.Sequential(*[
            TransformerDecoder(d_model, num_heads, d_ff, dropout)
            for _ in range(num_decoder_layers)
        ])

        # Output layer
        self.fc_out = nn.Linear(d_model, tgt_vocab_size)

        # Scale embeddings
        self.src_embed.weight.data.mul_(math.sqrt(d_model))
        self.tgt_embed.weight.data.mul_(math.sqrt(d_model))

    def forward(self,
                src: torch.Tensor,
                tgt: torch.Tensor,
                src_mask: torch.Tensor = None,
                tgt_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Forward pass through Transformer.

        Args:
            src: Source sequences [B, T_src]
            tgt: Target sequences [B, T_tgt]
            src_mask: Source attention mask
            tgt_mask: Target causal mask
        """
        # Embed and add positional encoding
        src_emb = self.pos_enc(self.src_embed(src) * math.sqrt(self.d_model))
        tgt_emb = self.pos_enc(self.tgt_embed(tgt) * math.sqrt(self.d_model))

        # Encoder
        enc_out, _ = self.encoder[0](src_emb, src_mask)
        for encoder_layer in self.encoder[1:]:
            enc_out, _ = encoder_layer(enc_out, src_mask)

        # Decoder
        dec_out = tgt_emb
        for decoder_layer in self.decoder:
            dec_out, _, _ = decoder_layer(dec_out, enc_out, tgt_mask, src_mask)

        # Output
        output = self.fc_out(dec_out)

        return output


import math
```

---

## Training Techniques

### Batch Normalization

```python
class BatchNormalizationDemo:
    """
    Batch Normalization reduces internal covariate shift.

    BN(x) = γ * (x - μ_batch) / sqrt(σ_batch^2 + ε) + β

    During training: uses batch statistics
    During inference: uses running statistics (EMA)
    """

    @staticmethod
    def batch_norm_example():
        """Demonstrate batch normalization."""
        # Create a simple network with BN
        model = nn.Sequential(
            nn.Linear(784, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, 10)
        )

        # Training mode (uses batch statistics)
        model.train()
        x = torch.randn(32, 784)
        out_train = model(x)

        # Evaluation mode (uses running statistics)
        model.eval()
        with torch.no_grad():
            out_eval = model(x)

        return model

    @staticmethod
    def layer_norm_example():
        """LayerNorm normalizes features, not samples."""
        layer = nn.LayerNorm(768)

        x = torch.randn(32, 100, 768)  # [batch, seq_len, features]
        y = layer(x)

        return y


class LayerNormalization(nn.Module):
    """
    Layer Normalization (from "Layer Normalization" - Ba et al., 2016).

    More stable than batch normalization, especially for RNNs and Transformers.
    """

    def __init__(self, normalized_shape, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))
        self.eps = eps

    def forward(self, x):
        """Apply layer normalization."""
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.weight * (x - mean) / (std + self.eps) + self.bias


class GroupNormalization(nn.Module):
    """
    Group Normalization (from "Group Normalization" - Yuxin Wu & Kaiming He, 2018).

    Better than batch norm for small batch sizes. Less dependent on batch size.
    """

    def __init__(self, num_groups, num_channels, eps=1e-6):
        super().__init__()
        self.num_groups = num_groups
        self.num_channels = num_channels
        self.weight = nn.Parameter(torch.ones(num_channels))
        self.bias = nn.Parameter(torch.zeros(num_channels))
        self.eps = eps

    def forward(self, x):
        """Apply group normalization."""
        B, C, H, W = x.shape

        # Reshape to separate groups
        x = x.reshape(B, self.num_groups, C // self.num_groups, H, W)

        # Normalize per group
        mean = x.mean([2, 3, 4], keepdim=True)
        std = x.std([2, 3, 4], keepdim=True)
        x = (x - mean) / (std + self.eps)

        # Reshape back
        x = x.reshape(B, C, H, W)

        return self.weight.reshape(1, -1, 1, 1) * x + self.bias.reshape(1, -1, 1, 1)
```

### Dropout

```python
class DropoutVariants:
    """
    Dropout and its variants for regularization.
    """

    @staticmethod
    def standard_dropout():
        """
        Standard dropout: randomly set activations to 0.

        During training: y = (x / p) * bernoulli(p)
        During inference: y = x (no dropout)
        """
        model = nn.Sequential(
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 10)
        )
        return model

    @staticmethod
    def spatial_dropout():
        """Dropout that drops entire channels."""
        dropout = nn.Dropout2d(p=0.5)
        x = torch.randn(32, 64, 28, 28)
        out = dropout(x)
        return out

    @staticmethod
    def monte_carlo_dropout():
        """
        Use dropout during inference for uncertainty estimation.
        """
        class MCDropoutModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = nn.Linear(784, 256)
                self.dropout = nn.Dropout(0.5)
                self.fc2 = nn.Linear(256, 10)

            def forward(self, x):
                x = F.relu(self.fc1(x))
                x = self.dropout(x)
                return self.fc2(x)

        model = MCDropoutModel()

        # Multiple forward passes with dropout enabled
        model.train()  # Keep dropout enabled
        predictions = []

        with torch.no_grad():
            for _ in range(10):
                pred = model(torch.randn(32, 784))
                predictions.append(pred)

        # Compute mean and variance
        predictions = torch.stack(predictions)  # [10, 32, 10]
        mean = predictions.mean(0)
        std = predictions.std(0)

        return mean, std


class DropConnect(nn.Module):
    """DropConnect: drop weights instead of activations."""

    def __init__(self, in_features, out_features, dropout_rate=0.5):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.dropout_rate = dropout_rate

    def forward(self, x):
        if self.training and self.dropout_rate > 0:
            # Drop weights
            mask = torch.bernoulli(torch.ones_like(self.linear.weight) * (1 - self.dropout_rate))
            weight = self.linear.weight * mask
            return F.linear(x, weight, self.linear.bias)
        return self.linear(x)
```

### Gradient Clipping

```python
class GradientClippingDemo:
    """
    Prevent exploding gradients through gradient clipping.
    Essential for RNNs and very deep networks.
    """

    @staticmethod
    def norm_based_clipping():
        """
        Clip gradients by norm.

        Useful for: RNNs, ensuring stable training
        """
        model = LSTM(input_size=100, hidden_size=256, num_layers=2)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        # Training loop
        x = torch.randn(32, 50, 100)  # [B, T, input_size]
        y = torch.randint(0, 10, (32,))

        output = model(x)[0][:, -1, :]
        loss = criterion(output, y)

        loss.backward()

        # Clip gradients by norm
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        optimizer.zero_grad()

        return loss

    @staticmethod
    def value_based_clipping():
        """
        Clip gradients by value (element-wise).

        Useful for: preventing NaN/Inf values
        """
        model = nn.Linear(100, 10)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

        x = torch.randn(32, 100)
        y = torch.randint(0, 10, (32,))

        output = model(x)
        loss = nn.functional.cross_entropy(output, y)

        loss.backward()

        # Clip gradients by value
        torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=0.1)

        optimizer.step()
        optimizer.zero_grad()


class GradientAccumulation:
    """
    Accumulate gradients over multiple batches.
    Useful for training with large effective batch size on limited memory.
    """

    @staticmethod
    def example():
        """
        Simulate gradient accumulation with 4x steps.
        Effective batch size = 32 * 4 = 128
        """
        model = nn.Linear(784, 10)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        accumulation_steps = 4

        for step in range(accumulation_steps):
            x = torch.randn(32, 784)
            y = torch.randint(0, 10, (32,))

            output = model(x)
            loss = criterion(output, y)

            # Scale loss by accumulation steps (important!)
            loss = loss / accumulation_steps

            loss.backward()  # Accumulate gradients

            # Update weights only every accumulation_steps
            if (step + 1) % accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()
```

### Learning Rate Schedules

```python
class LearningRateSchedules:
    """
    Various learning rate schedules for training.
    """

    @staticmethod
    def warmup_cosine_schedule():
        """
        Warmup + Cosine decay schedule (used in BERT, GPT).

        Common in transformer training.
        """
        model = nn.Linear(784, 10)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)

        num_epochs = 100
        warmup_epochs = 10
        total_steps = num_epochs * 100  # 100 batches per epoch
        warmup_steps = warmup_epochs * 100

        def warmup_cosine(current_step):
            if current_step < warmup_steps:
                return current_step / warmup_steps
            else:
                progress = (current_step - warmup_steps) / (total_steps - warmup_steps)
                return 0.5 * (1 + math.cos(math.pi * progress))

        scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            lr_lambda=warmup_cosine
        )

        return optimizer, scheduler

    @staticmethod
    def exponential_decay():
        """Exponential learning rate decay."""
        model = nn.Linear(784, 10)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

        scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)

        for epoch in range(100):
            # Training...
            scheduler.step()

        return optimizer, scheduler

    @staticmethod
    def polynomial_decay():
        """Polynomial decay schedule (used in LAMB optimizer)."""
        model = nn.Linear(784, 10)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

        num_epochs = 100
        total_steps = num_epochs * 100

        def polynomial_decay(current_step):
            return (1 - current_step / total_steps) ** 2

        scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            lr_lambda=polynomial_decay
        )

        return optimizer, scheduler

    @staticmethod
    def constant_warmup():
        """Constant warmup followed by linear decay (used in ELECTRA)."""
        model = nn.Linear(784, 10)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001)

        warmup_steps = 10000
        total_steps = 100000

        def warmup_linear(current_step):
            if current_step < warmup_steps:
                return current_step / warmup_steps
            else:
                return (total_steps - current_step) / (total_steps - warmup_steps)

        scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            lr_lambda=warmup_linear
        )

        return optimizer, scheduler
```

---

## Optimization Algorithms

### SGD with Momentum and Nesterov

```python
class SGDOptimizer(torch.optim.Optimizer):
    """
    Stochastic Gradient Descent with momentum and Nesterov acceleration.

    Update rule (with momentum):
    v_t = β * v_{t-1} + ∇f(θ_t)
    θ_t+1 = θ_t - α * v_t

    With Nesterov:
    θ_t+1 = θ_t - α * (β * v_{t-1} + ∇f(θ_t - α * β * v_{t-1}))
    """

    def __init__(self, params, lr=0.01, momentum=0, nesterov=False, weight_decay=0):
        if lr < 0:
            raise ValueError("Invalid learning rate: {}".format(lr))

        defaults = dict(lr=lr, momentum=momentum, nesterov=nesterov, weight_decay=weight_decay)
        super().__init__(params, defaults)

    def step(self, closure=None):
        """Perform a single optimization step."""
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            weight_decay = group['weight_decay']
            momentum = group['momentum']
            nesterov = group['nesterov']

            for p in group['params']:
                if p.grad is None:
                    continue

                d_p = p.grad.data

                # Weight decay
                if weight_decay != 0:
                    d_p = d_p.add(p.data, alpha=weight_decay)

                # Momentum
                if momentum != 0:
                    param_state = self.state[p]
                    if 'momentum_buffer' not in param_state:
                        buf = param_state['momentum_buffer'] = torch.clone(d_p).detach()
                    else:
                        buf = param_state['momentum_buffer']
                        buf.mul_(momentum).add_(d_p)

                    if nesterov:
                        d_p = d_p.add(buf, alpha=momentum)
                    else:
                        d_p = buf

                p.data.add_(d_p, alpha=-group['lr'])

        return loss
```

### Adam and AdamW

```python
class AdamOptimizer(torch.optim.Optimizer):
    """
    Adam optimizer (Adaptive Moment Estimation).

    From Kingma & Ba, "Adam: A Method for Stochastic Optimization" (2014)

    Update rules:
    m_t = β_1 * m_{t-1} + (1 - β_1) * ∇f(θ_t)
    v_t = β_2 * v_{t-1} + (1 - β_2) * (∇f(θ_t))^2
    m̂_t = m_t / (1 - β_1^t)
    v̂_t = v_t / (1 - β_2^t)
    θ_t+1 = θ_t - α * m̂_t / (sqrt(v̂_t) + ε)
    """

    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0, amsgrad=False):
        if not 0.0 <= lr:
            raise ValueError("Invalid learning rate: {}".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter at index 0: {}".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter at index 1: {}".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {}".format(eps))

        defaults = dict(lr=lr, betas=betas, eps=eps,
                       weight_decay=weight_decay, amsgrad=amsgrad)
        super().__init__(params, defaults)

    def step(self, closure=None):
        """Perform a single optimization step."""
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad.data
                amsgrad = group['amsgrad']

                # Weight decay
                if group['weight_decay'] != 0:
                    grad = grad.add(p.data, alpha=group['weight_decay'])

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p.data)
                    state['exp_avg_sq'] = torch.zeros_like(p.data)
                    if amsgrad:
                        state['max_exp_avg_sq'] = torch.zeros_like(p.data)

                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                if amsgrad:
                    max_exp_avg_sq = state['max_exp_avg_sq']

                state['step'] += 1

                bias_correction1 = 1 - group['betas'][0] ** state['step']
                bias_correction2 = 1 - group['betas'][1] ** state['step']

                # Update biased first moment estimate
                exp_avg.mul_(group['betas'][0]).add_(grad, alpha=1 - group['betas'][0])

                # Update biased second raw moment estimate
                exp_avg_sq.mul_(group['betas'][1]).addcmul_(grad, grad, value=1 - group['betas'][1])

                if amsgrad:
                    # Maintains max of all 2nd moment running avg.
                    torch.max(max_exp_avg_sq, exp_avg_sq, out=max_exp_avg_sq)
                    denom = max_exp_avg_sq.sqrt() / (bias_correction2 ** 0.5)
                else:
                    denom = (exp_avg_sq.sqrt() / (bias_correction2 ** 0.5))

                step_size = group['lr'] / bias_correction1

                p.data.addcdiv_(exp_avg, denom + group['eps'], value=-step_size)

        return loss


class AdamW(torch.optim.Optimizer):
    """
    AdamW optimizer with decoupled weight decay.

    From Loshchilov & Hutter, "Decoupled Weight Decay Regularization" (2019)

    Fixes the weight decay issue in Adam by decoupling it from the gradient-based update.
    """

    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0.01, amsgrad=False):
        if not 0.0 <= lr:
            raise ValueError("Invalid learning rate")
        if not 0.0 <= weight_decay:
            raise ValueError("Invalid weight_decay value")

        defaults = dict(lr=lr, betas=betas, eps=eps,
                       weight_decay=weight_decay, amsgrad=amsgrad)
        super().__init__(params, defaults)

    def step(self, closure=None):
        """Perform a single optimization step."""
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad.data
                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p.data)
                    state['exp_avg_sq'] = torch.zeros_like(p.data)

                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']

                state['step'] += 1
                beta1, beta2 = group['betas']

                # Decay the first and second moment running average coefficient
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                bias_correction1 = 1 - beta1 ** state['step']
                bias_correction2 = 1 - beta2 ** state['step']

                denom = (exp_avg_sq.sqrt() / (bias_correction2 ** 0.5)).add_(group['eps'])
                step_size = group['lr'] / bias_correction1

                p.data.addcdiv_(exp_avg, denom, value=-step_size)

                # Decoupled weight decay
                if group['weight_decay'] != 0:
                    p.data.mul_(1 - group['lr'] * group['weight_decay'])

        return loss
```

### LAMB (Large Batch Optimization)

```python
class LAMB(torch.optim.Optimizer):
    """
    LAMB optimizer for large batch training.

    From You, Gitman & Ginsburg, "LAMB: Large Batch Optimization for Deep Learning" (2020)

    Enables training with very large batch sizes (e.g., 32K) without accuracy loss.
    """

    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0, adam=False, gradient_averaging=False):
        if not 0.0 <= lr:
            raise ValueError("Invalid learning rate: {}".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter at index 0: {}".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter at index 1: {}".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {}".format(eps))

        defaults = dict(
            lr=lr, betas=betas, eps=eps,
            weight_decay=weight_decay, adam=adam,
            gradient_averaging=gradient_averaging
        )
        super().__init__(params, defaults)

    def step(self, closure=None):
        """Perform a single optimization step."""
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad.data
                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p.data)
                    state['exp_avg_sq'] = torch.zeros_like(p.data)

                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                beta1, beta2 = group['betas']

                state['step'] += 1

                # Decay the first and second moment running average coefficient
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)

                bias_correction1 = 1 - beta1 ** state['step']
                bias_correction2 = 1 - beta2 ** state['step']

                m_hat = exp_avg / bias_correction1
                v_hat = exp_avg_sq / bias_correction2

                adam_step = m_hat / (v_hat.sqrt() + group['eps'])

                # Compute the norm of the weights
                weight_norm = torch.norm(p.data)

                # Compute the norm of the Adam step
                adam_norm = torch.norm(adam_step)

                # Trust ratio
                if weight_norm > 0 and adam_norm > 0:
                    trust_ratio = weight_norm / adam_norm
                else:
                    trust_ratio = 1.0

                # Apply LAMB update
                p.data.mul_(1 - group['lr'] * group['weight_decay'])
                p.data.add_(adam_step, alpha=-group['lr'] * trust_ratio)

        return loss
```

---

## Distributed Training

### Data Parallel (DDP)

```python
class DistributedTrainingExample:
    """
    Distributed Data Parallel training with PyTorch.

    From Meta AI/PyTorch team - standard for large-scale training.
    """

    @staticmethod
    def setup(rank: int, world_size: int):
        """Initialize the distributed environment."""
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'

        # Initialize the process group
        torch.distributed.init_process_group(
            backend='nccl',  # Use NCCL for GPUs, gloo for CPUs
            rank=rank,
            world_size=world_size
        )

    @staticmethod
    def cleanup():
        """Clean up the distributed environment."""
        torch.distributed.destroy_process_group()

    @staticmethod
    def train_ddp(rank: int, world_size: int):
        """Training loop with DDP."""
        DistributedTrainingExample.setup(rank, world_size)

        # Model
        model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000)
        model = model.to(rank)

        # Wrap with DDP
        ddp_model = torch.nn.parallel.DistributedDataParallel(
            model,
            device_ids=[rank],
            output_device=rank
        )

        # Optimizer
        optimizer = torch.optim.SGD(ddp_model.parameters(), lr=0.01, momentum=0.9)

        # DataLoader with DistributedSampler
        dataset = torch.utils.data.TensorDataset(
            torch.randn(1000, 3, 224, 224),
            torch.randint(0, 1000, (1000,))
        )

        sampler = torch.utils.data.distributed.DistributedSampler(
            dataset,
            num_replicas=world_size,
            rank=rank,
            shuffle=True
        )

        train_loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=32,
            sampler=sampler
        )

        # Training loop
        criterion = torch.nn.CrossEntropyLoss()

        for epoch in range(10):
            sampler.set_epoch(epoch)  # Important for shuffling

            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(rank), target.to(rank)

                optimizer.zero_grad()
                output = ddp_model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

                if batch_idx % 100 == 0 and rank == 0:
                    print(f"Epoch {epoch}, Batch {batch_idx}, Loss {loss.item():.4f}")

        DistributedTrainingExample.cleanup()


class FullyShardedDataParallel:
    """
    Fully Sharded Data Parallel (FSDP) for extreme scale training.

    Shards both model parameters and gradients across devices.
    Allows training models that don't fit in a single GPU.
    """

    @staticmethod
    def example():
        """FSDP training example."""
        from torch.distributed.fsdp import FSDP, CPUOffload
        from torch.distributed.fsdp.wrap import default_auto_wrap_policy

        # Model
        model = ResNet(ResidualBlock, [3, 4, 6, 3], 1000)

        # Wrap with FSDP
        auto_wrap_policy = default_auto_wrap_policy

        fsdp_model = FSDP(
            model,
            auto_wrap_policy=auto_wrap_policy,
            cpu_offload=CPUOffload(offload_params=True),
            device_id=torch.cuda.current_device()
        )

        return fsdp_model


class DeepSpeedIntegration:
    """
    DeepSpeed integration for advanced distributed training.

    From Microsoft Research - enables training of 1 trillion parameter models.
    """

    @staticmethod
    def example():
        """
        DeepSpeed configuration and training.

        Requires: pip install deepspeed
        """
        import deepspeed

        # Model
        model = ResNet(ResidualBlock, [3, 4, 6, 3], 1000)

        # DeepSpeed configuration
        ds_config = {
            "train_batch_size": 64,
            "train_micro_batch_size_per_gpu": 8,
            "gradient_accumulation_steps": 1,
            "optimizer": {
                "type": "Adam",
                "params": {
                    "lr": 1e-3,
                    "betas": [0.9, 0.999],
                    "eps": 1e-8,
                    "weight_decay": 0.01
                }
            },
            "scheduler": {
                "type": "WarmupLR",
                "params": {
                    "warmup_min_lr": 0,
                    "warmup_max_lr": 1e-3,
                    "warmup_num_steps": 1000
                }
            },
            "fp16": {
                "enabled": True,
                "loss_scale": 0,
                "loss_scale_window": 1000,
                "initial_scale_power": 16,
                "hysteresis": 2,
                "min_loss_scale": 1
            }
        }

        # Initialize DeepSpeed
        model, optimizer, train_loader, scheduler = deepspeed.initialize(
            model=model,
            model_parameters=model.parameters(),
            config_params=ds_config
        )

        return model, optimizer
```

---

## Mixed Precision Training

```python
class MixedPrecisionTraining:
    """
    Mixed Precision Training with Automatic Mixed Precision (AMP).

    From NVIDIA/Apex and PyTorch - reduces memory usage and training time.
    """

    @staticmethod
    def training_with_amp():
        """
        Training with PyTorch's automatic mixed precision.
        """
        model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000)
        model = model.cuda()

        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        criterion = torch.nn.CrossEntropyLoss()

        # Create a gradient scaler
        scaler = torch.cuda.amp.GradScaler()

        # Dummy data
        train_loader = [
            (torch.randn(32, 3, 224, 224).cuda(),
             torch.randint(0, 1000, (32,)).cuda())
            for _ in range(10)
        ]

        for epoch in range(10):
            for images, labels in train_loader:
                optimizer.zero_grad()

                # Cast to float16 in forward pass
                with torch.cuda.amp.autocast(dtype=torch.float16):
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                # Scale loss and backward
                scaler.scale(loss).backward()

                # Unscale gradients and step
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

                scaler.step(optimizer)
                scaler.update()

        return model


class ExplicitMixedPrecision:
    """
    Explicit mixed precision for fine-grained control.
    """

    @staticmethod
    def example():
        """
        Manual mixed precision handling.
        """
        model = nn.Sequential(
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 10)
        )

        # Forward: float16 for memory efficiency
        x_fp32 = torch.randn(32, 784)

        # Convert to float16
        x_fp16 = x_fp32.to(torch.float16)

        # Forward pass in float16
        with torch.cuda.amp.autocast(dtype=torch.float16):
            with torch.no_grad():
                model_fp16 = model.to(torch.float16)
                output_fp16 = model_fp16(x_fp16)

        # Convert back to float32 for loss
        output_fp32 = output_fp16.to(torch.float32)

        return output_fp32
```

---

## Production Best Practices

### Model Checkpointing

```python
class ModelCheckpointing:
    """
    Best practices for saving and loading model checkpoints.
    """

    @staticmethod
    def save_checkpoint(epoch, model, optimizer, scheduler, metrics, path):
        """Save a comprehensive checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
            'metrics': metrics,
            'model_config': {
                'arch': 'ResNet50',
                'num_classes': 1000,
                'pretrained': False,
            }
        }

        torch.save(checkpoint, path)
        print(f"Checkpoint saved to {path}")

    @staticmethod
    def load_checkpoint(model, optimizer, scheduler, path):
        """Load a checkpoint and resume training."""
        checkpoint = torch.load(path)

        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if scheduler and checkpoint['scheduler_state_dict']:
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        return checkpoint['epoch'] + 1


class EarlyStoppingCallback:
    """
    Early stopping to prevent overfitting.
    """

    def __init__(self, patience=10, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None

    def __call__(self, val_loss):
        if self.best_score is None:
            self.best_score = val_loss
        elif val_loss > self.best_score - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                return True  # Stop training
        else:
            self.best_score = val_loss
            self.counter = 0

        return False  # Continue training
```

### Inference Optimization

```python
class InferenceOptimization:
    """
    Techniques for optimizing inference performance.
    """

    @staticmethod
    def quantization():
        """
        Post-training quantization for faster inference.
        """
        model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000)
        model.eval()

        # Quantization aware training
        model_quantized = torch.quantization.quantize_dynamic(
            model,
            {torch.nn.Linear},
            dtype=torch.qint8
        )

        return model_quantized

    @staticmethod
    def torch_jit_compilation():
        """
        JIT compilation for faster inference.
        """
        model = nn.Linear(784, 10)
        model.eval()

        # Trace the model
        dummy_input = torch.randn(1, 784)
        traced_model = torch.jit.trace(model, dummy_input)

        # Or use script (doesn't require dummy input)
        scripted_model = torch.jit.script(model)

        return traced_model


class BatchProcessing:
    """
    Efficient batch processing for inference.
    """

    @staticmethod
    def process_batches(model, data_loader):
        """Process data in batches for efficiency."""
        model.eval()
        predictions = []

        with torch.no_grad():
            for batch in data_loader:
                output = model(batch)
                predictions.append(output.cpu())

        return torch.cat(predictions, dim=0)
```

---

## Benchmarking & Profiling

```python
class ProfilingAndBenchmarking:
    """
    Tools for profiling and benchmarking deep learning models.
    """

    @staticmethod
    def pytorch_profiler():
        """
        PyTorch built-in profiler for identifying bottlenecks.
        """
        model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000).cuda()
        model.eval()

        x = torch.randn(32, 3, 224, 224).cuda()

        with torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA
            ],
            on_trace_ready=torch.profiler.tensorboard_trace_handler('./logs')
        ) as prof:
            for _ in range(10):
                model(x)

        return prof

    @staticmethod
    def memory_profiling():
        """
        Profile memory usage.
        """
        model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000).cuda()

        x = torch.randn(32, 3, 224, 224).cuda()

        # Reset peak memory
        torch.cuda.reset_peak_memory_stats()

        # Forward pass
        output = model(x)
        loss = output.sum()
        loss.backward()

        # Print memory stats
        print(f"Max allocated: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
        print(f"Max reserved: {torch.cuda.max_memory_reserved() / 1e9:.2f} GB")

    @staticmethod
    def throughput_benchmark():
        """
        Benchmark model throughput (samples per second).
        """
        model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000).cuda()
        model.eval()

        x = torch.randn(32, 3, 224, 224).cuda()

        # Warmup
        for _ in range(10):
            with torch.no_grad():
                model(x)

        # Benchmark
        torch.cuda.synchronize()
        start = time.time()

        num_iterations = 100
        for _ in range(num_iterations):
            with torch.no_grad():
                model(x)

        torch.cuda.synchronize()
        elapsed = time.time() - start

        throughput = (num_iterations * 32) / elapsed
        print(f"Throughput: {throughput:.2f} samples/sec")

        return throughput
```

---

## Complete Training Example

```python
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteTrainingPipeline:
    """
    Production-ready training pipeline combining all techniques.
    """

    def __init__(self,
                 model: nn.Module,
                 train_loader,
                 val_loader,
                 device: str = 'cuda'):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device

        # Optimizer with gradient accumulation
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=1e-3,
            weight_decay=0.01
        )

        # Learning rate schedule
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=10,
            T_mult=2
        )

        # Mixed precision
        self.scaler = torch.cuda.amp.GradScaler()

        # Metrics
        self.best_val_loss = float('inf')
        self.early_stopping = EarlyStoppingCallback(patience=10)

    def train_epoch(self):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0

        accumulation_steps = 4

        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)

            # Forward with AMP
            with torch.cuda.amp.autocast(dtype=torch.float16):
                output = self.model(data)
                loss = F.cross_entropy(output, target)
                loss = loss / accumulation_steps

            # Backward
            self.scaler.scale(loss).backward()

            # Step
            if (batch_idx + 1) % accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.scaler.step(self.optimizer)
                self.scaler.update()
                self.optimizer.zero_grad()

            total_loss += loss.item() * accumulation_steps

        avg_loss = total_loss / len(self.train_loader)
        return avg_loss

    def validate(self):
        """Validate the model."""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device)

                output = self.model(data)
                loss = F.cross_entropy(output, target)
                total_loss += loss.item()

        avg_loss = total_loss / len(self.val_loader)
        return avg_loss

    def train(self, num_epochs: int):
        """Complete training loop."""
        for epoch in range(num_epochs):
            train_loss = self.train_epoch()
            val_loss = self.validate()

            self.scheduler.step()

            logger.info(f"Epoch {epoch}: Train Loss={train_loss:.4f}, Val Loss={val_loss:.4f}")

            # Save best checkpoint
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self._save_checkpoint(epoch)

            # Early stopping
            if self.early_stopping(val_loss):
                logger.info("Early stopping triggered")
                break

    def _save_checkpoint(self, epoch: int):
        """Save checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_loss': self.best_val_loss,
        }
        torch.save(checkpoint, 'best_model.pth')


# Usage example
if __name__ == "__main__":
    # Create synthetic dataset
    train_dataset = torch.utils.data.TensorDataset(
        torch.randn(1000, 3, 224, 224),
        torch.randint(0, 1000, (1000,))
    )
    val_dataset = torch.utils.data.TensorDataset(
        torch.randn(200, 3, 224, 224),
        torch.randint(0, 1000, (200,))
    )

    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=32, shuffle=True
    )
    val_loader = torch.utils.data.DataLoader(
        val_dataset, batch_size=32, shuffle=False
    )

    # Create model
    model = ResNet(ResidualBlock, [2, 2, 2, 2], 1000)

    # Train
    trainer = CompleteTrainingPipeline(model, train_loader, val_loader)
    trainer.train(num_epochs=100)
```

---

## References & Key Papers

### Foundational Papers
- **Attention is All You Need** (Vaswani et al., 2017) - Transformers
- **Deep Residual Learning for Image Recognition** (He et al., 2015) - ResNet
- **EfficientNet: Rethinking Model Scaling for CNNs** (Tan & Le, 2019) - Google
- **An Image is Worth 16x16 Words** (Dosovitskiy et al., 2021) - Vision Transformers

### Optimization Papers
- **Adam: A Method for Stochastic Optimization** (Kingma & Ba, 2014)
- **Decoupled Weight Decay Regularization** (Loshchilov & Hutter, 2019) - AdamW
- **LAMB: Large Batch Optimization for Deep Learning** (You et al., 2020)

### Distributed Training
- **ZeRO: Memory Optimizations Toward Training Trillion Parameter Models** (Rajbhandari et al., 2020)
- **Efficient Large-Scale Language Model Training on GPU Clusters** (Narayanan et al., 2021)

### Mixed Precision Training
- **Mixed Precision Training** (Micikevicius et al., 2018)
- **A Study of BFLOAT16 for Deep Learning Training** (Kalamkar et al., 2019)

---

## Conclusion

This reference guide provides production-grade implementations and best practices from leading organizations (Meta AI, Google Research, Microsoft). Use these techniques to:

1. **Build efficient models** - ResNet, EfficientNet, Vision Transformers
2. **Train effectively** - Batch norm, dropout, gradient clipping
3. **Scale training** - DDP, FSDP, DeepSpeed
4. **Optimize performance** - Mixed precision, quantization, JIT compilation
5. **Monitor progress** - Profiling, benchmarking, checkpointing

For the latest techniques, consult official documentation from PyTorch, TensorFlow, JAX, and papers from top conferences (NeurIPS, ICML, ICLR).
