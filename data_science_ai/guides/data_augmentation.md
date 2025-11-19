# Data Augmentation Guide: Comprehensive Techniques & Best Practices

Complete guide to data augmentation across multiple domains with production-ready implementations.

## Table of Contents
1. [Overview](#overview)
2. [Image Augmentation](#image-augmentation)
3. [Text Augmentation](#text-augmentation)
4. [Audio Augmentation](#audio-augmentation)
5. [Time-Series Augmentation](#time-series-augmentation)
6. [Advanced Techniques](#advanced-techniques)
7. [Best Practices](#best-practices)
8. [Production Pipelines](#production-pipelines)

---

## Overview

Data augmentation artificially increases dataset size by creating modified copies of existing data. This helps:
- **Reduce overfitting**: Models learn generalizable features
- **Improve robustness**: Handle variations in real-world data
- **Balance datasets**: Address class imbalance
- **Enhance performance**: Especially with limited labeled data
- **Increase diversity**: Expose models to more variations

**Key Principle**: Augmentations should preserve the label while introducing meaningful variations.

---

## Image Augmentation

### 1. Albumentations Library

**Installation**:
```bash
pip install albumentations opencv-python
```

**Why Albumentations?**
- Extremely fast (optimized C++ implementation)
- GPU-accelerated operations
- Extensive geometric and color transformations
- Automatic bbox/mask transformations
- Production-ready

#### Example 1: Image Classification Pipeline

```python
import albumentations as A
import cv2
from albumentations.pytorch import ToTensorV2
import numpy as np

# Classification augmentation pipeline
transform = A.Compose([
    # Geometric transformations
    A.Rotate(limit=45, p=0.5),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.Perspective(scale=(0.05, 0.1), p=0.5),

    # Crops and resizes
    A.RandomResizedCrop(height=224, width=224, p=0.5),

    # Color augmentations
    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
    A.RandomRain(p=0.2),
    A.RandomFog(p=0.2),

    # Pixel-level transformations
    A.GaussNoise(p=0.2),
    A.Blur(blur_limit=3, p=0.2),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=45, p=0.5),

    # Normalization and tensor conversion
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
        max_pixel_value=255.0,
    ),
    ToTensorV2(),
], bbox_params=A.BboxParams(format='pascal_voc', label_fields=['labels']))

# Usage
image = cv2.imread('image.jpg')
bboxes = [[100, 100, 200, 200], [300, 300, 400, 400]]
labels = [0, 1]

augmented = transform(image=image, bboxes=bboxes, labels=labels)
augmented_image = augmented['image']
augmented_bboxes = augmented['bboxes']
augmented_labels = augmented['labels']
```

#### Example 2: Object Detection Pipeline

```python
# Detection-specific augmentation
detection_transform = A.Compose([
    A.SmallestMaxSize(max_size=416, p=1),
    A.PadIfNeeded(min_height=416, min_width=416, border_mode=cv2.BORDER_CONSTANT, p=1),

    # Detection-friendly augmentations
    A.Rotate(limit=25, p=0.5),
    A.HorizontalFlip(p=0.5),
    A.Blur(blur_limit=3, p=0.1),
    A.MedianBlur(blur_limit=3, p=0.1),
    A.GaussNoise(p=0.1),

    A.OneOf([
        A.OpticalDistortion(p=0.2),
        A.GridDistortion(p=0.2),
    ], p=0.2),

    # Brightness/contrast
    A.OneOf([
        A.CLAHE(clip_limit=2),
        A.Sharpen(),
        A.Emboss(),
    ], p=0.3),

    A.HueSaturationValue(p=0.3),

    A.Normalize(),
    ToTensorV2(),
], bbox_params=A.BboxParams(format='yolo', label_fields=['labels'], min_area=0))
```

#### Example 3: Segmentation Pipeline

```python
# Segmentation with mask support
segmentation_transform = A.Compose([
    A.Resize(height=512, width=512),
    A.Rotate(limit=30, p=0.5),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),

    A.ElasticTransform(p=0.3),
    A.GridDistortion(p=0.3),
    A.OpticalDistortion(p=0.3),

    A.OneOf([
        A.GaussNoise(),
        A.GaussianBlur(),
        A.MotionBlur(),
    ], p=0.2),

    A.OneOf([
        A.RandomBrightnessContrast(),
        A.RandomGamma(),
        A.CLAHE(clip_limit=4),
    ], p=0.3),

    A.Normalize(),
    ToTensorV2(),
], is_check_shapes=False)

# Usage with mask
image = cv2.imread('image.jpg')
mask = cv2.imread('mask.jpg', cv2.IMREAD_GRAYSCALE)

augmented = segmentation_transform(image=image, mask=mask)
augmented_image = augmented['image']
augmented_mask = augmented['mask']
```

### 2. TorchVision Transforms

**Fast integration with PyTorch**

```python
from torchvision import transforms
from PIL import Image
import torch

# Standard augmentation pipeline
train_transforms = transforms.Compose([
    transforms.RandomCrop(224, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.9, 1.1)),
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
    transforms.RandomPerspective(distortion_scale=0.2, p=0.5),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Advanced: AutoAugment (learned augmentation)
auto_augment = transforms.Compose([
    transforms.AutoAugment(transforms.AutoAugmentPolicy.IMAGENET),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]),
])

# Usage
image = Image.open('image.jpg')
augmented = train_transforms(image)
```

---

## Text Augmentation

### 1. Back-Translation

Translate text to another language and back to original language.

```python
from transformers import pipeline
import torch

class BackTranslationAugmentation:
    def __init__(self, intermediate_language='de'):
        """
        Args:
            intermediate_language: Language to translate to/from ('de', 'fr', 'es', etc.)
        """
        self.intermediate = intermediate_language

        # Translation pipelines
        self.to_intermediate = pipeline(
            f"translation_en_to_{intermediate_language}",
            device=0 if torch.cuda.is_available() else -1
        )
        self.back_to_english = pipeline(
            f"translation_{intermediate_language}_to_en",
            device=0 if torch.cuda.is_available() else -1
        )

    def augment(self, text):
        """Perform back-translation augmentation"""
        try:
            # Translate to intermediate language
            intermediate_text = self.to_intermediate(text)[0]['translation_text']

            # Translate back to English
            augmented_text = self.back_to_english(intermediate_text)[0]['translation_text']

            return augmented_text
        except Exception as e:
            print(f"Error in back-translation: {e}")
            return text

# Usage
augmentor = BackTranslationAugmentation(intermediate_language='de')
original = "This is a great example of data augmentation."
augmented = augmentor.augment(original)
print(f"Original: {original}")
print(f"Augmented: {augmented}")
```

### 2. Synonym Replacement

Replace words with their synonyms using NLTK or WordNet.

```python
import nltk
from nltk.corpus import wordnet
import random

nltk.download('wordnet')
nltk.download('punkt')

class SynonymAugmentation:
    def __init__(self, aug_percent=0.3):
        """
        Args:
            aug_percent: Percentage of words to augment (0-1)
        """
        self.aug_percent = aug_percent

    def get_synonyms(self, word, pos=None):
        """Get synonyms for a word"""
        synonyms = set()
        for synset in wordnet.synsets(word, pos=pos):
            for lemma in synset.lemmas():
                synonyms.add(lemma.name().replace('_', ' '))
        return list(synonyms - {word})

    def augment(self, text):
        """Replace random words with synonyms"""
        words = nltk.word_tokenize(text)
        num_words = len(words)
        num_to_replace = max(1, int(num_words * self.aug_percent))

        # Randomly select positions to replace
        positions = random.sample(range(num_words), min(num_to_replace, num_words))

        for pos in positions:
            word = words[pos]
            synonyms = self.get_synonyms(word)
            if synonyms:
                words[pos] = random.choice(synonyms)

        return ' '.join(words)

# Usage
augmentor = SynonymAugmentation(aug_percent=0.3)
original = "The quick brown fox jumps over the lazy dog"
augmented = augmentor.augment(original)
```

### 3. Paraphrasing with T5

Generate paraphrases using pre-trained models.

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class ParaphraseAugmentation:
    def __init__(self, model_name='humarin/chatgpt_paraphrase_paws_paraphrase_diverse'):
        """
        Args:
            model_name: Hugging Face model ID for paraphrase generation
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        self.max_length = 256

    def augment(self, text, num_return_sequences=1, temperature=0.8):
        """Generate paraphrases"""
        input_ids = self.tokenizer.encode(text, return_tensors='pt').to(self.device)

        # Generate paraphrases with sampling
        outputs = self.model.generate(
            input_ids,
            max_length=self.max_length,
            num_return_sequences=num_return_sequences,
            temperature=temperature,
            top_p=0.95,
            do_sample=True,
            no_repeat_ngram_size=2,
        )

        paraphrases = [
            self.tokenizer.decode(output, skip_special_tokens=True)
            for output in outputs
        ]

        return paraphrases

# Usage
augmentor = ParaphraseAugmentation()
original = "Machine learning is transforming the world."
paraphrases = augmentor.augment(original, num_return_sequences=3)
for i, paraphrase in enumerate(paraphrases, 1):
    print(f"Paraphrase {i}: {paraphrase}")
```

### 4. Contextual Word Embeddings Substitution

Replace words with contextually similar words.

```python
from transformers import pipeline
import torch

class ContextualWordSubstitution:
    def __init__(self, num_candidates=5):
        """Replace masked words with contextually similar alternatives"""
        self.pipeline = pipeline(
            "fill-mask",
            model="roberta-base",
            device=0 if torch.cuda.is_available() else -1
        )
        self.num_candidates = num_candidates

    def augment(self, text):
        """Mask and replace random words"""
        words = text.split()
        if len(words) < 2:
            return text

        # Randomly select a word to mask
        mask_idx = torch.randint(0, len(words), (1,)).item()
        masked_text = ' '.join(
            words[:mask_idx] + ['<mask>'] + words[mask_idx+1:]
        )

        try:
            results = self.pipeline(masked_text, top_k=self.num_candidates)
            replacement = results[0]['token_str'].strip()
            words[mask_idx] = replacement
            return ' '.join(words)
        except Exception as e:
            print(f"Error: {e}")
            return text

# Usage
augmentor = ContextualWordSubstitution()
original = "The quick brown fox jumps"
augmented = augmentor.augment(original)
```

---

## Audio Augmentation

### Audio Transformations with librosa and audiomentations

```python
import numpy as np
import librosa
import soundfile as sf
from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, Shift

class AudioAugmentation:
    def __init__(self, sr=22050):
        """
        Args:
            sr: Sample rate
        """
        self.sr = sr
        self.augment = Compose([
            AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
            TimeStretch(min_rate=0.8, max_rate=1.25, p=0.5),
            PitchShift(min_semitones=-4, max_semitones=4, p=0.5),
            Shift(min_fraction=-0.5, max_fraction=0.5, p=0.5),
        ])

    def load_audio(self, audio_path):
        """Load audio file"""
        y, sr = librosa.load(audio_path, sr=self.sr)
        return y, sr

    def augment_audio(self, audio_array):
        """Apply augmentation to audio array"""
        augmented = self.augment(audio_array, sample_rate=self.sr)
        return augmented

    def save_audio(self, audio_array, output_path):
        """Save augmented audio"""
        sf.write(output_path, audio_array, self.sr)

class AdvancedAudioAugmentation:
    """Advanced audio augmentation techniques"""

    def __init__(self, sr=22050):
        self.sr = sr

    def time_stretch(self, audio, rate):
        """Change speed without changing pitch"""
        return librosa.effects.time_stretch(audio, rate=rate)

    def pitch_shift(self, audio, n_steps):
        """Change pitch without changing speed"""
        return librosa.effects.pitch_shift(audio, sr=self.sr, n_steps=n_steps)

    def add_background_noise(self, audio, noise_path, noise_factor=0.01):
        """Add background noise from another audio file"""
        noise, _ = librosa.load(noise_path, sr=self.sr)
        # Match lengths
        min_len = min(len(audio), len(noise))
        noise = noise[:min_len]
        audio = audio[:min_len]
        return audio + noise_factor * noise

    def dynamic_time_warping_augment(self, audio, num_steps=5):
        """Simulate slight time deformations"""
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Apply random frequency shifting
        shift = np.random.randint(-num_steps, num_steps)
        magnitude = np.roll(magnitude, shift, axis=0)

        return librosa.istft(magnitude * np.exp(1j * phase))

    def spectral_masking(self, audio, mask_percent=0.1):
        """Mask random frequency bands"""
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)

        num_freqs = magnitude.shape[0]
        num_to_mask = int(num_freqs * mask_percent)
        mask_indices = np.random.choice(num_freqs, num_to_mask, replace=False)
        magnitude[mask_indices] = 0

        phase = np.angle(stft)
        return librosa.istft(magnitude * np.exp(1j * phase))

# Usage
augmentor = AudioAugmentation(sr=16000)
audio, sr = augmentor.load_audio('audio.wav')
augmented = augmentor.augment_audio(audio)
augmentor.save_audio(augmented, 'augmented_audio.wav')
```

---

## Time-Series Augmentation

### Time-Series Specific Techniques

```python
import numpy as np
import pandas as pd
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesAugmentation:
    """Comprehensive time-series augmentation"""

    def __init__(self, data):
        """
        Args:
            data: 1D or 2D numpy array (samples, features)
        """
        self.data = np.array(data)
        if self.data.ndim == 1:
            self.data = self.data.reshape(-1, 1)

    def jittering(self, sigma=0.03):
        """Add small random noise to values"""
        return self.data + np.random.normal(0, sigma, self.data.shape)

    def scaling(self, sigma=0.1):
        """Scale the time series by a random factor"""
        scale_factor = np.random.normal(1.0, sigma)
        return self.data * scale_factor

    def magnitude_warping(self, knot_num=4, sigma=0.1):
        """Warp the magnitude of time series"""
        n_samples = self.data.shape[0]
        n_features = self.data.shape[1]

        # Generate random control points
        knots = np.linspace(0, n_samples - 1, knot_num)
        values = np.random.normal(1.0, sigma, knot_num)

        # Interpolate
        from scipy.interpolate import interp1d
        f = interp1d(knots, values, kind='cubic', fill_value='extrapolate')
        warping_function = f(np.arange(n_samples))

        return self.data * warping_function.reshape(-1, 1)

    def time_warping(self, knot_num=4, sigma=0.1):
        """Warp time axis"""
        n_samples = self.data.shape[0]
        n_features = self.data.shape[1]

        # Generate random control points
        knots = np.linspace(0, n_samples - 1, knot_num)
        values = np.linspace(0, n_samples - 1, knot_num) + \
                 np.random.normal(0, sigma, knot_num) * (n_samples / knot_num)
        values = np.clip(values, 0, n_samples - 1)

        from scipy.interpolate import interp1d
        f = interp1d(knots, values, kind='cubic', fill_value='extrapolate')
        warped_indices = f(np.arange(n_samples))
        warped_indices = np.clip(warped_indices, 0, n_samples - 1).astype(int)

        return self.data[warped_indices]

    def window_slicing(self, num_slices=4):
        """Randomly shift subsections"""
        n_samples = self.data.shape[0]
        augmented = self.data.copy()

        slice_len = n_samples // num_slices

        for i in range(num_slices):
            start = i * slice_len
            end = start + slice_len
            shift = np.random.randint(-slice_len // 2, slice_len // 2)
            shift_start = max(0, start + shift)
            shift_end = min(n_samples, end + shift)

            if shift_end - shift_start == slice_len:
                augmented[start:end] = self.data[shift_start:shift_end]

        return augmented

    def window_warping(self, window_ratio=0.1, num_warps=4):
        """Compress/stretch random windows"""
        n_samples = self.data.shape[0]
        augmented = self.data.copy()

        window_len = int(n_samples * window_ratio)

        for _ in range(num_warps):
            start = np.random.randint(0, n_samples - window_len)
            end = start + window_len

            # Random stretch/compress factor
            warp_factor = np.random.uniform(0.5, 1.5)

            # Get window data
            window = self.data[start:end]

            # Resample window
            indices = np.linspace(0, window_len - 1, int(window_len / warp_factor))
            from scipy.interpolate import interp1d
            f = interp1d(np.arange(window_len), window, axis=0, kind='linear',
                        fill_value='extrapolate')
            warped = f(indices)

            # Place back (with proper size adjustment)
            new_size = min(len(warped), n_samples - start)
            augmented[start:start + new_size] = warped[:new_size]

        return augmented

    def rotation(self):
        """Rotate time series"""
        n_samples = self.data.shape[0]
        rotation_amount = np.random.randint(0, n_samples)
        return np.roll(self.data, rotation_amount, axis=0)

    def permutation(self, block_size=None):
        """Permute blocks of time series"""
        n_samples = self.data.shape[0]
        if block_size is None:
            block_size = max(1, n_samples // 10)

        num_blocks = n_samples // block_size
        blocks = [self.data[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
        np.random.shuffle(blocks)

        return np.vstack(blocks)

# Usage
data = np.sin(np.linspace(0, 4*np.pi, 100)).reshape(-1, 1)
augmentor = TimeSeriesAugmentation(data)

augmented_jitter = augmentor.jittering(sigma=0.05)
augmented_scaling = augmentor.scaling(sigma=0.1)
augmented_magnitude = augmentor.magnitude_warping(knot_num=4, sigma=0.1)
augmented_time = augmentor.time_warping(knot_num=4, sigma=0.1)
```

---

## Advanced Techniques

### 1. MixUp - Linear Interpolation

Blend pairs of examples and their labels.

```python
import torch
import torch.nn.functional as F
import numpy as np

class MixUp:
    """MixUp data augmentation for images and features"""

    def __init__(self, alpha=1.0):
        """
        Args:
            alpha: Beta distribution parameter for mixing coefficient
        """
        self.alpha = alpha

    def get_lam(self, batch_size):
        """Sample lambda from Beta distribution"""
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1.0
        return lam

    def mixup_data(self, x, y, lam=None):
        """
        Mix inputs and targets

        Args:
            x: Input batch (N, C, H, W)
            y: Target batch (N,) or (N, C)
            lam: Mixing coefficient

        Returns:
            Augmented x, y_a, y_b, lam
        """
        batch_size = x.size(0)

        if lam is None:
            lam = self.get_lam(batch_size)

        # Random shuffle
        index = torch.randperm(batch_size)

        # Mix inputs
        mixed_x = lam * x + (1 - lam) * x[index, :]

        return mixed_x, y, y[index], lam

    def mixup_criterion(self, criterion, pred, y_a, y_b, lam):
        """Compute loss with mixup targets"""
        return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

# Usage with training loop
def train_with_mixup(model, train_loader, optimizer, criterion, device, alpha=1.0):
    mixup = MixUp(alpha=alpha)
    model.train()

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        # Apply mixup
        mixed_data, target_a, target_b, lam = mixup.mixup_data(data, target)

        # Forward pass
        optimizer.zero_grad()
        output = model(mixed_data)

        # Compute loss
        loss = mixup.mixup_criterion(criterion, output, target_a, target_b, lam)

        # Backward pass
        loss.backward()
        optimizer.step()
```

### 2. CutMix - Region Mixing

Cut and paste patches between images.

```python
import torch
import torch.nn.functional as F
import numpy as np

class CutMix:
    """CutMix data augmentation"""

    def __init__(self, alpha=1.0, prob=0.5):
        """
        Args:
            alpha: Beta distribution parameter
            prob: Probability of applying CutMix
        """
        self.alpha = alpha
        self.prob = prob

    def get_cutmix_box(self, img_h, img_w, lam):
        """Generate random box for cutting"""
        cut_ratio = np.sqrt(1 - lam)
        cut_h = int(img_h * cut_ratio)
        cut_w = int(img_w * cut_ratio)

        # Uniform distribution for center point
        cx = np.random.randint(0, img_w)
        cy = np.random.randint(0, img_h)

        # Box coordinates
        x1 = np.clip(cx - cut_w // 2, 0, img_w)
        y1 = np.clip(cy - cut_h // 2, 0, img_h)
        x2 = np.clip(cx + cut_w // 2, 0, img_w)
        y2 = np.clip(cy + cut_h // 2, 0, img_h)

        return x1, y1, x2, y2

    def cutmix_data(self, x, y):
        """
        Apply CutMix augmentation

        Args:
            x: Input batch (N, C, H, W)
            y: Target batch (N,)

        Returns:
            Augmented x, y_a, y_b, lam
        """
        if np.random.rand(1) > self.prob:
            return x, y, y, 1.0

        batch_size, _, img_h, img_w = x.size()

        # Sample lambda
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1.0

        # Random shuffle
        index = torch.randperm(batch_size)

        # Get cut box
        x1, y1, x2, y2 = self.get_cutmix_box(img_h, img_w, lam)

        # Apply cutmix
        x[..., y1:y2, x1:x2] = x[index, ..., y1:y2, x1:x2]

        # Adjust lambda based on actual box area
        lam = 1 - ((x2 - x1) * (y2 - y1)) / (img_h * img_w)

        return x, y, y[index], lam

# Usage
cutmix = CutMix(alpha=1.0, prob=0.5)
mixed_data, target_a, target_b, lam = cutmix.cutmix_data(data, target)
```

### 3. AutoAugment - Learned Augmentation Policy

```python
import torch
import torchvision.transforms as transforms
from torchvision.transforms import AutoAugment, AutoAugmentPolicy

class AutoAugmentPolicy:
    """Apply learned augmentation policies"""

    def __init__(self, policy='imagenet'):
        """
        Args:
            policy: 'imagenet', 'cifar10', or 'svhn'
        """
        self.policy_map = {
            'imagenet': AutoAugmentPolicy.IMAGENET,
            'cifar10': AutoAugmentPolicy.CIFAR10,
            'svhn': AutoAugmentPolicy.SVHN,
        }

        self.transform = transforms.Compose([
            AutoAugment(self.policy_map[policy]),
            transforms.ToTensor(),
        ])

    def augment(self, image):
        """Apply AutoAugment to image"""
        return self.transform(image)

# Usage
auto_augment = AutoAugmentPolicy(policy='imagenet')
augmented_image = auto_augment.augment(image)
```

### 4. RandAugment - Simplified Random Augmentation

```python
from torchvision.transforms import RandAugment
import torchvision.transforms as transforms

class RandAugmentPolicy:
    """RandAugment - simpler and more efficient than AutoAugment"""

    def __init__(self, num_ops=2, magnitude=9):
        """
        Args:
            num_ops: Number of augmentation operations to apply
            magnitude: Magnitude of each operation (0-10)
        """
        self.transform = transforms.Compose([
            RandAugment(num_ops=num_ops, magnitude=magnitude),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def augment(self, image):
        """Apply RandAugment to image"""
        return self.transform(image)

# Usage
rand_augment = RandAugmentPolicy(num_ops=2, magnitude=9)
augmented_image = rand_augment.augment(image)
```

---

## Best Practices

### 1. Image Augmentation Best Practices

```python
# DO: Use composition of multiple transforms
image_augmentation = A.Compose([
    # Geometric transforms (keep aspect ratio)
    A.Rotate(limit=30, p=0.5),
    A.HorizontalFlip(p=0.5),

    # Color/brightness transforms
    A.RandomBrightnessContrast(p=0.3),

    # Normalization
    A.Normalize(),
    ToTensorV2(),
])

# DON'T: Apply extreme transforms that change label
# Avoid: A.VerticalFlip() for objects that have orientation (6 vs 9)

# DO: Use different augmentations for train vs test
train_aug = A.Compose([...])  # Aggressive augmentation
val_aug = A.Compose([A.Normalize(), ToTensorV2()])  # No augmentation

# DO: Preserve bounding boxes/masks
# Set proper format and label fields

# DON'T: Over-augment small datasets (causes overfitting to augmentations)
# For very small datasets (< 1000 samples): Use lighter augmentations
# For medium datasets (1000-10000): Use moderate augmentations
# For large datasets (> 10000): Can use aggressive augmentations
```

### 2. Text Augmentation Best Practices

```python
# DO: Validate semantic preservation
original = "The model achieved 95% accuracy"
augmented = "The model obtained 95% accuracy"
# Similar meaning preserved

# DON'T: Lose important information
original = "Temperature must be < 100°C"
augmented = "Temperature must be ~ 100°C"  # Wrong!

# DO: Use ensemble of augmentation methods
augmentation_methods = [
    back_translation,
    synonym_replacement,
    paraphrasing,
]

# Random selection or combination
selected_method = np.random.choice(augmentation_methods)

# DON'T: Over-augment sentiment-critical text
# "Great product!" -> "Terrible product!" changes label!

# DO: Use multiple languages for back-translation
back_translation_languages = ['de', 'fr', 'es', 'ja']
```

### 3. Audio Augmentation Best Practices

```python
# DO: Preserve speech intelligibility
augmentation = Compose([
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
    TimeStretch(min_rate=0.8, max_rate=1.25, p=0.5),
    PitchShift(min_semitones=-4, max_semitones=4, p=0.5),
])

# DON'T: Use transforms that degrade quality too much
# Avoid: TimeStretch with extreme rates (< 0.5 or > 2.0)

# DO: Use task-specific augmentations
# For speech recognition: Pitch shift, time stretch, background noise
# For music: Keep pitch more consistent, use spectral masking
# For speaker recognition: Pitch shift OK, time stretch should be limited

# DO: Keep loudness normalized
from pyloudnorm import Loudness
loudness_normalizer = Loudness()
normalized_audio = loudness_normalizer.normalize(augmented_audio)
```

### 4. Time-Series Augmentation Best Practices

```python
# DO: Maintain temporal consistency
# Use smooth augmentations (magnitude warping, time warping)

# DON'T: Break time-series structure with random permutations
# Avoid: Permuting entire sequence for time-series forecasting

# DO: Use domain-specific augmentations
# For stock prices: Scaling, magnitude warping (preserve trends)
# For IoT sensor data: Jittering, noise, small scale variations
# For health data: Magnitude warping, time stretching (preserve patterns)

# DO: Validate augmented data makes sense
original_trend = np.mean(original_data)
augmented_trend = np.mean(augmented_data)
# Should be similar for trend-based tasks

# DON'T: Augment in a way that violates physical constraints
# Example: Temperature can't jump from 20°C to -50°C instantly
```

---

## Production Pipelines

### Complete Image Classification Pipeline

```python
import torch
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import numpy as np
from pathlib import Path

class AugmentedImageDataset(Dataset):
    """Production-ready image dataset with augmentation"""

    def __init__(self, image_dir, labels_file, split='train',
                 image_size=224, augmentation_strength='medium'):
        """
        Args:
            image_dir: Directory containing images
            labels_file: CSV file with image_name, label columns
            split: 'train', 'val', or 'test'
            image_size: Input image size
            augmentation_strength: 'light', 'medium', 'heavy'
        """
        self.image_dir = Path(image_dir)
        self.split = split

        # Load labels
        import pandas as pd
        self.labels_df = pd.read_csv(labels_file)
        self.image_paths = [str(self.image_dir / img) for img in self.labels_df['image']]
        self.labels = self.labels_df['label'].values

        # Define augmentations
        self.transforms = self._get_augmentation_pipeline(
            image_size, augmentation_strength
        )

    def _get_augmentation_pipeline(self, image_size, strength):
        """Get augmentation pipeline based on strength"""

        if self.split == 'train':
            if strength == 'light':
                return A.Compose([
                    A.Resize(image_size, image_size),
                    A.HorizontalFlip(p=0.5),
                    A.ColorJitter(brightness=0.1, contrast=0.1, p=0.3),
                    A.Normalize(),
                    ToTensorV2(),
                ])
            elif strength == 'medium':
                return A.Compose([
                    A.RandomResizedCrop(image_size, image_size, p=0.5),
                    A.Rotate(limit=30, p=0.5),
                    A.HorizontalFlip(p=0.5),
                    A.OneOf([
                        A.GaussianBlur(blur_limit=3),
                        A.MedianBlur(blur_limit=3),
                    ], p=0.2),
                    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, p=0.5),
                    A.GaussNoise(p=0.2),
                    A.Normalize(),
                    ToTensorV2(),
                ])
            else:  # heavy
                return A.Compose([
                    A.RandomResizedCrop(image_size, image_size, scale=(0.7, 1.0), p=0.5),
                    A.Rotate(limit=45, p=0.5),
                    A.HorizontalFlip(p=0.5),
                    A.VerticalFlip(p=0.3),
                    A.Perspective(scale=(0.05, 0.1), p=0.3),
                    A.ElasticTransform(p=0.2),
                    A.OneOf([
                        A.GaussianBlur(),
                        A.MedianBlur(),
                        A.MotionBlur(),
                    ], p=0.3),
                    A.OneOf([
                        A.RandomBrightnessContrast(),
                        A.RandomGamma(),
                        A.CLAHE(),
                    ], p=0.3),
                    A.OneOf([
                        A.GaussNoise(),
                        A.ISONoise(),
                    ], p=0.2),
                    A.Normalize(),
                    ToTensorV2(),
                ])
        else:  # val/test
            return A.Compose([
                A.Resize(image_size, image_size),
                A.Normalize(),
                ToTensorV2(),
            ])

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        # Load image
        image = cv2.imread(self.image_paths[idx])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Apply augmentations
        augmented = self.transforms(image=image)
        image = augmented['image']

        # Get label
        label = torch.tensor(self.labels[idx], dtype=torch.long)

        return image, label

# Usage
def create_augmented_dataloaders(image_dir, labels_file, batch_size=32,
                                 num_workers=4, image_size=224):
    """Create training and validation dataloaders"""

    train_dataset = AugmentedImageDataset(
        image_dir, labels_file, split='train',
        image_size=image_size, augmentation_strength='medium'
    )
    val_dataset = AugmentedImageDataset(
        image_dir, labels_file, split='val',
        image_size=image_size, augmentation_strength='light'
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    return train_loader, val_loader
```

### Complete Text Augmentation Pipeline

```python
import random
from typing import List, Tuple
from transformers import pipeline
import torch

class AugmentedTextDataset:
    """Production-ready text dataset with augmentation"""

    def __init__(self, texts: List[str], labels: List[int],
                 augmentation_strength='medium', augmentation_methods=None):
        """
        Args:
            texts: List of text samples
            labels: List of labels
            augmentation_strength: 'light', 'medium', 'heavy'
            augmentation_methods: Custom list of augmentation methods
        """
        self.texts = texts
        self.labels = labels
        self.augmentation_strength = augmentation_strength

        # Initialize augmentation methods
        self.back_translator = BackTranslationAugmentation(intermediate_language='de')
        self.synonym_augmentor = SynonymAugmentation(aug_percent=0.3)
        self.paraphrase_augmentor = ParaphraseAugmentation()
        self.contextual_augmentor = ContextualWordSubstitution(num_candidates=5)

        self.augmentation_methods = augmentation_methods or \
            [self.back_translate, self.synonym_replace, self.paraphrase]

    def back_translate(self, text):
        """Apply back-translation"""
        return self.back_translator.augment(text)

    def synonym_replace(self, text):
        """Apply synonym replacement"""
        return self.synonym_augmentor.augment(text)

    def paraphrase(self, text):
        """Apply paraphrasing"""
        paraphrases = self.paraphrase_augmentor.augment(text, num_return_sequences=1)
        return paraphrases[0] if paraphrases else text

    def contextual_replace(self, text):
        """Apply contextual word substitution"""
        return self.contextual_augmentor.augment(text)

    def get_augmentation_strategy(self):
        """Get augmentation strategy based on strength"""
        if self.augmentation_strength == 'light':
            return [self.synonym_replace]
        elif self.augmentation_strength == 'medium':
            return [self.back_translate, self.synonym_replace]
        else:  # heavy
            return [self.back_translate, self.synonym_replace,
                   self.paraphrase, self.contextual_replace]

    def augment_sample(self, text: str) -> Tuple[str, str]:
        """Augment a single sample"""
        strategy = self.get_augmentation_strategy()
        augmentation_method = random.choice(strategy)

        try:
            augmented_text = augmentation_method(text)
            # Validate semantic similarity (optional)
            return text, augmented_text
        except Exception as e:
            print(f"Augmentation error: {e}")
            return text, text

    def create_augmented_dataset(self, augmentation_ratio=1.0):
        """Create augmented dataset"""
        augmented_texts = []
        augmented_labels = []

        # Original data
        augmented_texts.extend(self.texts)
        augmented_labels.extend(self.labels)

        # Augmented data
        num_augmentations = int(len(self.texts) * augmentation_ratio)
        augmentation_indices = random.sample(range(len(self.texts)),
                                            min(num_augmentations, len(self.texts)))

        for idx in augmentation_indices:
            text = self.texts[idx]
            label = self.labels[idx]

            _, augmented_text = self.augment_sample(text)
            augmented_texts.append(augmented_text)
            augmented_labels.append(label)

        return augmented_texts, augmented_labels

# Usage
texts = ["Sample text 1", "Sample text 2"]
labels = [0, 1]

augmented_dataset = AugmentedTextDataset(
    texts, labels, augmentation_strength='medium'
)
aug_texts, aug_labels = augmented_dataset.create_augmented_dataset(
    augmentation_ratio=1.0
)
```

### Complete Time-Series Pipeline

```python
class AugmentedTimeSeriesDataset:
    """Production-ready time-series dataset with augmentation"""

    def __init__(self, data: np.ndarray, labels: np.ndarray,
                 augmentation_strength='medium', lookback=100):
        """
        Args:
            data: Shape (num_samples, num_timesteps, num_features)
            labels: Shape (num_samples,)
            augmentation_strength: 'light', 'medium', 'heavy'
            lookback: Lookback window
        """
        self.data = data
        self.labels = labels
        self.lookback = lookback
        self.augmentor = TimeSeriesAugmentation(data[0])
        self.augmentation_strength = augmentation_strength

    def get_augmentation_methods(self):
        """Get augmentation methods based on strength"""
        if self.augmentation_strength == 'light':
            return [self.augmentor.jittering]
        elif self.augmentation_strength == 'medium':
            return [self.augmentor.jittering, self.augmentor.scaling,
                   self.augmentor.magnitude_warping]
        else:  # heavy
            return [self.augmentor.jittering, self.augmentor.scaling,
                   self.augmentor.magnitude_warping, self.augmentor.time_warping,
                   self.augmentor.window_warping]

    def augment_sample(self, sample: np.ndarray) -> np.ndarray:
        """Augment a single time-series sample"""
        methods = self.get_augmentation_methods()
        method = random.choice(methods)

        self.augmentor.data = sample
        return method()

    def create_augmented_dataset(self, augmentation_ratio=1.0):
        """Create augmented time-series dataset"""
        augmented_data = []
        augmented_labels = []

        # Original data
        augmented_data.extend(self.data)
        augmented_labels.extend(self.labels)

        # Augmented data
        num_augmentations = int(len(self.data) * augmentation_ratio)
        augmentation_indices = random.sample(range(len(self.data)),
                                            min(num_augmentations, len(self.data)))

        for idx in augmentation_indices:
            sample = self.data[idx]
            label = self.labels[idx]

            augmented_sample = self.augment_sample(sample)
            augmented_data.append(augmented_sample)
            augmented_labels.append(label)

        return np.array(augmented_data), np.array(augmented_labels)
```

---

## Decision Tree: When to Use Which Technique

```
IMAGE DATA?
├─ Classification?
│  ├─ Large dataset (>50k)?
│  │  └─ Use: RandAugment + MixUp
│  └─ Small dataset (<5k)?
│     └─ Use: Light augmentation + AutoAugment
├─ Object Detection?
│  └─ Use: Geometric transforms + CutMix
└─ Segmentation?
   └─ Use: Elastic transforms + mask-preserving augmentations

TEXT DATA?
├─ Sentiment Analysis?
│  └─ Use: Back-translation + Paraphrasing (preserve sentiment)
├─ NER/Sequence Tagging?
│  └─ Use: Synonym replacement (preserve entity positions)
├─ Machine Translation?
│  └─ Use: Back-translation (preserve semantics)
└─ General NLP?
   └─ Use: Contextual word substitution + Paraphrasing

AUDIO DATA?
├─ Speech Recognition?
│  └─ Use: Pitch shift + Time stretch + Background noise
├─ Speaker Recognition?
│  └─ Use: Light pitch shift + Time stretch
└─ Music?
   └─ Use: Spectral masking + Limited pitch shift

TIME-SERIES DATA?
├─ Forecasting?
│  └─ Use: Magnitude warping + Time warping (preserve trends)
├─ Classification?
│  └─ Use: Jittering + Scaling + Magnitude warping
└─ Anomaly Detection?
   └─ Use: Light augmentations (preserve anomalies)

IMBALANCED DATA?
└─ Use: SMOTE-like + Augmentations for minority class

LIMITED LABELED DATA (<1000 samples)?
└─ Use: Aggressive augmentation + Pretrained models
```

---

## Summary Table: Augmentation Techniques

| Technique | Domain | Speed | Quality | Use Case |
|-----------|--------|-------|---------|----------|
| Horizontal Flip | Image | Very Fast | High | Classification |
| Rotation | Image | Fast | High | Classification |
| ColorJitter | Image | Fast | High | Classification |
| CutMix | Image | Fast | Very High | Classification |
| MixUp | Image | Very Fast | High | Classification |
| AutoAugment | Image | Medium | Very High | Limited data |
| RandAugment | Image | Fast | High | Efficient training |
| Back-translation | Text | Slow | Very High | Limited data |
| Synonym Replacement | Text | Fast | Medium | Data augmentation |
| Paraphrasing | Text | Slow | Very High | Semantic preservation |
| TimeStretch | Audio | Fast | High | Speech recognition |
| PitchShift | Audio | Fast | High | Robust models |
| Jittering | Time-Series | Very Fast | Medium | Noise robustness |
| Magnitude Warping | Time-Series | Medium | High | Pattern preservation |
| Time Warping | Time-Series | Slow | Very High | Temporal flexibility |

---

## Key Takeaways

1. **Preserve Labels**: Augmentations should never change the true label
2. **Domain-Specific**: Use augmentations appropriate for your data type
3. **Strength Matters**: Tune augmentation intensity based on dataset size
4. **Validation**: Always validate augmented samples are realistic
5. **Production**: Use composition of augmentations, not single techniques
6. **Efficiency**: Consider computational cost in production pipelines
7. **Monitoring**: Track model performance on augmented vs. original data

---

## References

- Albumentations: https://albumentations.ai/
- torchvision Transforms: https://pytorch.org/vision/stable/transforms.html
- AutoAugment: https://arxiv.org/abs/1805.09501
- RandAugment: https://arxiv.org/abs/1909.13719
- MixUp: https://arxiv.org/abs/1710.09412
- CutMix: https://arxiv.org/abs/1905.04412
- TimeSeriesAugmentation: https://arxiv.org/abs/2003.08719
