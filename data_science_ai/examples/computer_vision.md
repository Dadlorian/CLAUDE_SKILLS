# Computer Vision Examples

Comprehensive, production-ready examples for computer vision tasks including classification, detection, segmentation, generation, and deployment.

## Table of Contents

1. [Image Classification](#image-classification)
2. [Object Detection](#object-detection)
3. [Semantic Segmentation](#semantic-segmentation)
4. [Instance Segmentation](#instance-segmentation)
5. [Image Generation](#image-generation)
6. [Data Augmentation](#data-augmentation)
7. [Transfer Learning](#transfer-learning)
8. [Model Deployment](#model-deployment)

---

## Image Classification

### ResNet Fine-Tuning with PyTorch

Production-ready image classification using transfer learning with ResNet50.

```python
import logging
import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageClassifier:
    """Production-ready ResNet50 image classifier with fine-tuning."""

    def __init__(
        self,
        num_classes: int,
        pretrained: bool = True,
        device: Optional[str] = None,
        model_save_dir: str = "./models"
    ):
        """
        Initialize the classifier.

        Args:
            num_classes: Number of output classes
            pretrained: Use pretrained ImageNet weights
            device: Device to use ('cuda' or 'cpu')
            model_save_dir: Directory to save models
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_classes = num_classes
        self.model_save_dir = Path(model_save_dir)
        self.model_save_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Using device: {self.device}")

        # Load pretrained ResNet50
        self.model = models.resnet50(pretrained=pretrained)

        # Replace final layer
        in_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )

        self.model.to(self.device)
        logger.info(f"Model initialized with {num_classes} output classes")

    def freeze_backbone(self, freeze: bool = True) -> None:
        """Freeze/unfreeze backbone layers for transfer learning."""
        for param in self.model.features.parameters() if hasattr(self.model, 'features') else self.model.layer1.parameters():
            param.requires_grad = not freeze
        for param in self.model.layer2.parameters():
            param.requires_grad = not freeze
        for param in self.model.layer3.parameters():
            param.requires_grad = not freeze

        logger.info(f"Backbone layers {'frozen' if freeze else 'unfrozen'}")

    def train_epoch(
        self,
        train_loader: DataLoader,
        criterion: nn.Module,
        optimizer: optim.Optimizer,
        epoch: int
    ) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        try:
            for batch_idx, (images, labels) in enumerate(train_loader):
                images, labels = images.to(self.device), labels.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()

                total_loss += loss.item()
                _, predicted = outputs.max(1)
                correct += predicted.eq(labels).sum().item()
                total += labels.size(0)

                if (batch_idx + 1) % 100 == 0:
                    logger.info(
                        f"Epoch {epoch} | Batch {batch_idx + 1} | "
                        f"Loss: {loss.item():.4f} | Accuracy: {correct/total:.4f}"
                    )

            return {
                'loss': total_loss / len(train_loader),
                'accuracy': correct / total
            }
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise

    def evaluate(
        self,
        test_loader: DataLoader
    ) -> Dict[str, Any]:
        """Evaluate model on test set."""
        self.model.eval()
        all_preds = []
        all_labels = []
        total_loss = 0.0
        criterion = nn.CrossEntropyLoss()

        try:
            with torch.no_grad():
                for images, labels in test_loader:
                    images, labels = images.to(self.device), labels.to(self.device)

                    outputs = self.model(images)
                    loss = criterion(outputs, labels)
                    total_loss += loss.item()

                    _, predicted = outputs.max(1)
                    all_preds.extend(predicted.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())

            all_preds = np.array(all_preds)
            all_labels = np.array(all_labels)

            metrics = {
                'loss': total_loss / len(test_loader),
                'accuracy': accuracy_score(all_labels, all_preds),
                'precision': precision_score(all_labels, all_preds, average='weighted', zero_division=0),
                'recall': recall_score(all_labels, all_preds, average='weighted', zero_division=0),
                'f1': f1_score(all_labels, all_preds, average='weighted', zero_division=0)
            }

            logger.info(f"Evaluation Results: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            raise

    def save_checkpoint(self, metrics: Dict[str, float], name: str = "best") -> str:
        """Save model checkpoint."""
        try:
            checkpoint = {
                'model_state_dict': self.model.state_dict(),
                'num_classes': self.num_classes,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }

            save_path = self.model_save_dir / f"{name}_model.pt"
            torch.save(checkpoint, save_path)
            logger.info(f"Checkpoint saved to {save_path}")
            return str(save_path)
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            raise

    def load_checkpoint(self, checkpoint_path: str) -> Dict[str, Any]:
        """Load model checkpoint."""
        try:
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"Checkpoint loaded from {checkpoint_path}")
            return checkpoint
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            raise

    def predict(self, images: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions on images."""
        self.model.eval()
        try:
            with torch.no_grad():
                images = images.to(self.device)
                outputs = self.model(images)
                probabilities = torch.softmax(outputs, dim=1)
                predictions = torch.argmax(outputs, dim=1)

            return predictions.cpu().numpy(), probabilities.cpu().numpy()
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise


# Usage Example
def example_image_classification():
    """Complete example of image classification workflow."""

    # Setup
    num_classes = 10
    batch_size = 32
    learning_rate = 0.001
    num_epochs = 10

    # Initialize classifier
    classifier = ImageClassifier(num_classes=num_classes)
    classifier.freeze_backbone(freeze=True)

    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        [param for param in classifier.model.parameters() if param.requires_grad],
        lr=learning_rate
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.1, patience=3, verbose=True
    )

    # Create dummy dataset (replace with actual dataset)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225])
    ])

    logger.info("Setup complete. Ready for training with actual data.")
```

---

## Object Detection

### YOLO v8 Implementation

Production-ready object detection using YOLO v8.

```python
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Detection result container."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # x_min, y_min, x_max, y_max

    def to_dict(self) -> Dict[str, Any]:
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'confidence': float(self.confidence),
            'bbox': [float(x) for x in self.bbox]
        }


class YOLODetector:
    """Production-ready YOLO v8 object detector."""

    def __init__(
        self,
        model_name: str = 'yolov8n.pt',
        device: Optional[str] = None,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45
    ):
        """
        Initialize YOLO detector.

        Args:
            model_name: YOLO model name (yolov8n/s/m/l/x)
            device: Device to use ('cuda' or 'cpu')
            conf_threshold: Confidence threshold
            iou_threshold: IOU threshold for NMS
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_name)
            self.device = device
            self.conf_threshold = conf_threshold
            self.iou_threshold = iou_threshold
            logger.info(f"YOLO model {model_name} loaded successfully")
        except ImportError:
            logger.error("ultralytics not installed. Install with: pip install ultralytics")
            raise

    def detect(self, image_path: str) -> List[Detection]:
        """
        Detect objects in image.

        Args:
            image_path: Path to image file

        Returns:
            List of Detection objects
        """
        try:
            results = self.model(
                image_path,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                device=self.device
            )

            detections = []
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    class_id = int(box.cls[0].item())
                    class_name = self.model.names[class_id]

                    detections.append(Detection(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x_min, y_min, x_max, y_max)
                    ))

            logger.info(f"Detected {len(detections)} objects in {image_path}")
            return detections
        except Exception as e:
            logger.error(f"Error during detection: {str(e)}")
            raise

    def detect_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        frame_skip: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Detect objects in video.

        Args:
            video_path: Path to video file
            output_path: Optional path to save annotated video
            frame_skip: Process every nth frame

        Returns:
            List of detections per frame
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            out = None
            if output_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            frame_results = []
            frame_id = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_id % frame_skip == 0:
                    results = self.model(frame, conf=self.conf_threshold)

                    detections = []
                    annotated_frame = results[0].plot()

                    if results[0].boxes is not None:
                        for box in results[0].boxes:
                            x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
                            detections.append({
                                'class': self.model.names[int(box.cls[0].item())],
                                'confidence': float(box.conf[0].item()),
                                'bbox': [x_min, y_min, x_max, y_max]
                            })

                    frame_results.append({
                        'frame_id': frame_id,
                        'detections': detections
                    })

                    if out:
                        out.write(annotated_frame)
                else:
                    if out:
                        out.write(frame)

                frame_id += 1

                if frame_id % 100 == 0:
                    logger.info(f"Processed {frame_id} frames")

            cap.release()
            if out:
                out.release()

            logger.info(f"Video processing complete. Processed {frame_id} frames")
            return frame_results
        except Exception as e:
            logger.error(f"Error during video detection: {str(e)}")
            raise

    def draw_detections(
        self,
        image_path: str,
        detections: List[Detection],
        output_path: str
    ) -> None:
        """Draw detections on image."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot read image: {image_path}")

            for detection in detections:
                x_min, y_min, x_max, y_max = detection.bbox
                cv2.rectangle(
                    image,
                    (int(x_min), int(y_min)),
                    (int(x_max), int(y_max)),
                    (0, 255, 0),
                    2
                )

                label = f"{detection.class_name}: {detection.confidence:.2f}"
                cv2.putText(
                    image,
                    label,
                    (int(x_min), int(y_min) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

            cv2.imwrite(output_path, image)
            logger.info(f"Annotated image saved to {output_path}")
        except Exception as e:
            logger.error(f"Error drawing detections: {str(e)}")
            raise


### Faster R-CNN Implementation

class FasterRCNNDetector:
    """Faster R-CNN detector using torchvision."""

    def __init__(
        self,
        num_classes: int,
        pretrained: bool = True,
        device: Optional[str] = None
    ):
        """Initialize Faster R-CNN detector."""
        try:
            from torchvision.models.detection import fasterrcnn_resnet50_fpn

            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.model = fasterrcnn_resnet50_fpn(
                pretrained=pretrained,
                num_classes=num_classes
            )
            self.model.to(self.device)
            self.model.eval()
            logger.info("Faster R-CNN model initialized")
        except ImportError:
            logger.error("torchvision not installed properly")
            raise

    def predict(
        self,
        images: torch.Tensor,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Make predictions."""
        try:
            with torch.no_grad():
                images = [img.to(self.device) for img in images]
                predictions = self.model(images)

            results = []
            for pred in predictions:
                boxes = pred['boxes']
                scores = pred['scores']
                labels = pred['labels']

                mask = scores > confidence_threshold
                results.append({
                    'boxes': boxes[mask].cpu().numpy(),
                    'scores': scores[mask].cpu().numpy(),
                    'labels': labels[mask].cpu().numpy()
                })

            return results
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise


# Usage Example
def example_object_detection():
    """Complete example of object detection workflow."""
    detector = YOLODetector(model_name='yolov8n.pt', conf_threshold=0.5)

    # Single image detection
    detections = detector.detect('path/to/image.jpg')
    print(f"Found {len(detections)} objects")

    # Video detection
    frame_results = detector.detect_video('path/to/video.mp4', output_path='output.mp4')
    print(f"Processed video with {len(frame_results)} results")
```

---

## Semantic Segmentation

### U-Net Implementation

Production-ready semantic segmentation with U-Net.

```python
import logging
import torch
import torch.nn as nn
from typing import Tuple, Optional, Dict, Any
import numpy as np
from sklearn.metrics import jaccard_score
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class DoubleConv(nn.Module):
    """Double convolution block."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class UNet(nn.Module):
    """U-Net segmentation network."""

    def __init__(
        self,
        in_channels: int = 3,
        num_classes: int = 1,
        base_channels: int = 64
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes

        # Encoder
        self.enc1 = DoubleConv(in_channels, base_channels)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.enc2 = DoubleConv(base_channels, base_channels * 2)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.enc3 = DoubleConv(base_channels * 2, base_channels * 4)
        self.pool3 = nn.MaxPool2d(2, 2)
        self.enc4 = DoubleConv(base_channels * 4, base_channels * 8)
        self.pool4 = nn.MaxPool2d(2, 2)

        # Bottleneck
        self.bottleneck = DoubleConv(base_channels * 8, base_channels * 16)

        # Decoder
        self.upconv4 = nn.ConvTranspose2d(base_channels * 16, base_channels * 8, 2, 2)
        self.dec4 = DoubleConv(base_channels * 16, base_channels * 8)
        self.upconv3 = nn.ConvTranspose2d(base_channels * 8, base_channels * 4, 2, 2)
        self.dec3 = DoubleConv(base_channels * 8, base_channels * 4)
        self.upconv2 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, 2, 2)
        self.dec2 = DoubleConv(base_channels * 4, base_channels * 2)
        self.upconv1 = nn.ConvTranspose2d(base_channels * 2, base_channels, 2, 2)
        self.dec1 = DoubleConv(base_channels * 2, base_channels)

        # Output layer
        self.final = nn.Conv2d(base_channels, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encoder with skip connections
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool1(enc1))
        enc3 = self.enc3(self.pool2(enc2))
        enc4 = self.enc4(self.pool3(enc3))

        # Bottleneck
        bottleneck = self.bottleneck(self.pool4(enc4))

        # Decoder with skip connections
        dec4 = self.dec4(torch.cat([self.upconv4(bottleneck), enc4], 1))
        dec3 = self.dec3(torch.cat([self.upconv3(dec4), enc3], 1))
        dec2 = self.dec2(torch.cat([self.upconv2(dec3), enc2], 1))
        dec1 = self.dec1(torch.cat([self.upconv1(dec2), enc1], 1))

        return self.final(dec1)


class SemanticSegmentation:
    """Production-ready semantic segmentation trainer."""

    def __init__(
        self,
        num_classes: int,
        device: Optional[str] = None,
        model_save_dir: str = "./models"
    ):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_classes = num_classes
        self.model = UNet(in_channels=3, num_classes=num_classes).to(self.device)
        self.model_save_dir = Path(model_save_dir)
        self.model_save_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SemanticSegmentation initialized on {self.device}")

    def train_epoch(
        self,
        train_loader: torch.utils.data.DataLoader,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int
    ) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0

        try:
            for batch_idx, (images, masks) in enumerate(train_loader):
                images = images.to(self.device)
                masks = masks.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, masks)

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

                total_loss += loss.item()

                if (batch_idx + 1) % 50 == 0:
                    logger.info(f"Epoch {epoch} | Batch {batch_idx + 1} | Loss: {loss.item():.4f}")

            return {'loss': total_loss / len(train_loader)}
        except Exception as e:
            logger.error(f"Error during training: {str(e)}")
            raise

    def evaluate(
        self,
        val_loader: torch.utils.data.DataLoader
    ) -> Dict[str, float]:
        """Evaluate on validation set."""
        self.model.eval()
        total_loss = 0.0
        iou_scores = []
        criterion = nn.CrossEntropyLoss()

        try:
            with torch.no_grad():
                for images, masks in val_loader:
                    images = images.to(self.device)
                    masks = masks.to(self.device)

                    outputs = self.model(images)
                    loss = criterion(outputs, masks)
                    total_loss += loss.item()

                    # Calculate IoU
                    preds = torch.argmax(outputs, dim=1)
                    for pred, mask in zip(preds, masks):
                        iou = jaccard_score(
                            mask.cpu().numpy().flatten(),
                            pred.cpu().numpy().flatten(),
                            average='weighted',
                            zero_division=0
                        )
                        iou_scores.append(iou)

            return {
                'loss': total_loss / len(val_loader),
                'mean_iou': np.mean(iou_scores) if iou_scores else 0.0
            }
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            raise

    def predict(self, image: torch.Tensor) -> np.ndarray:
        """Predict segmentation mask."""
        self.model.eval()
        try:
            with torch.no_grad():
                image = image.unsqueeze(0).to(self.device)
                output = self.model(image)
                prediction = torch.argmax(output, dim=1)

            return prediction.squeeze(0).cpu().numpy()
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise


### DeepLab Implementation

class DeepLabSegmentation:
    """DeepLabv3+ semantic segmentation."""

    def __init__(
        self,
        num_classes: int,
        backbone: str = 'resnet101',
        device: Optional[str] = None
    ):
        """Initialize DeepLab."""
        try:
            from torchvision.models.segmentation import deeplabv3_resnet101

            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.model = deeplabv3_resnet101(
                pretrained=True,
                num_classes=num_classes
            )
            self.model.to(self.device)
            logger.info("DeepLab model initialized")
        except ImportError:
            logger.error("torchvision not installed properly")
            raise

    def predict(self, image: torch.Tensor) -> np.ndarray:
        """Make segmentation prediction."""
        self.model.eval()
        try:
            with torch.no_grad():
                image = image.unsqueeze(0).to(self.device)
                output = self.model(image)['out']
                prediction = torch.argmax(output, dim=1)

            return prediction.squeeze(0).cpu().numpy()
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
```

---

## Instance Segmentation

### Mask R-CNN Implementation

Production-ready instance segmentation with Mask R-CNN.

```python
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import cv2

logger = logging.getLogger(__name__)


@dataclass
class InstanceSegmentationResult:
    """Instance segmentation result."""
    masks: np.ndarray  # [num_instances, height, width]
    boxes: np.ndarray  # [num_instances, 4]
    class_ids: np.ndarray  # [num_instances]
    scores: np.ndarray  # [num_instances]
    class_names: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'num_instances': len(self.masks),
            'boxes': self.boxes.tolist(),
            'class_ids': self.class_ids.tolist(),
            'scores': self.scores.tolist(),
            'class_names': self.class_names
        }


class MaskRCNNDetector:
    """Production-ready Mask R-CNN instance segmentation."""

    def __init__(
        self,
        num_classes: int,
        pretrained: bool = True,
        device: Optional[str] = None,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize Mask R-CNN.

        Args:
            num_classes: Number of classes
            pretrained: Use pretrained weights
            device: Device to use
            confidence_threshold: Minimum confidence for detections
        """
        try:
            from torchvision.models.detection import maskrcnn_resnet50_fpn

            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.confidence_threshold = confidence_threshold

            self.model = maskrcnn_resnet50_fpn(
                pretrained=pretrained,
                num_classes=num_classes
            )
            self.model.to(self.device)
            self.model.eval()

            # Class names (replace with actual class names)
            self.class_names = [f"class_{i}" for i in range(num_classes)]

            logger.info("Mask R-CNN model initialized")
        except ImportError:
            logger.error("torchvision not installed properly")
            raise

    def predict(
        self,
        images: torch.Tensor
    ) -> List[InstanceSegmentationResult]:
        """
        Predict instance segmentations.

        Args:
            images: Tensor of shape [batch_size, 3, height, width]

        Returns:
            List of InstanceSegmentationResult
        """
        try:
            self.model.eval()
            with torch.no_grad():
                images = [img.to(self.device) for img in images]
                predictions = self.model(images)

            results = []
            for pred in predictions:
                masks = pred['masks']
                boxes = pred['boxes']
                labels = pred['labels']
                scores = pred['scores']

                # Filter by confidence
                mask = scores > self.confidence_threshold
                masks = masks[mask]
                boxes = boxes[mask]
                labels = labels[mask]
                scores = scores[mask]

                # Convert to numpy
                masks = (masks > 0.5).squeeze(1).cpu().numpy().astype(np.uint8)
                boxes = boxes.cpu().numpy()
                labels = labels.cpu().numpy()
                scores = scores.cpu().numpy()

                class_names = [self.class_names[label] for label in labels]

                results.append(InstanceSegmentationResult(
                    masks=masks,
                    boxes=boxes,
                    class_ids=labels,
                    scores=scores,
                    class_names=class_names
                ))

            return results
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise

    def visualize(
        self,
        image: np.ndarray,
        result: InstanceSegmentationResult,
        output_path: str
    ) -> None:
        """
        Visualize instance segmentation results.

        Args:
            image: Input image
            result: Segmentation result
            output_path: Path to save visualization
        """
        try:
            vis_image = image.copy()
            colors = np.random.randint(0, 256, (len(result.masks), 3))

            for idx, (mask, box, score, class_name) in enumerate(zip(
                result.masks, result.boxes, result.scores, result.class_names
            )):
                # Draw mask
                color = tuple(map(int, colors[idx]))
                vis_image[mask > 0] = vis_image[mask > 0] * 0.5 + np.array(color) * 0.5

                # Draw bounding box
                x_min, y_min, x_max, y_max = box.astype(int)
                cv2.rectangle(vis_image, (x_min, y_min), (x_max, y_max), color, 2)

                # Draw label
                label = f"{class_name}: {score:.2f}"
                cv2.putText(
                    vis_image,
                    label,
                    (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

            cv2.imwrite(output_path, vis_image)
            logger.info(f"Visualization saved to {output_path}")
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            raise


# Usage Example
def example_instance_segmentation():
    """Complete example of instance segmentation."""
    detector = MaskRCNNDetector(num_classes=81, confidence_threshold=0.5)

    # Load image and convert to tensor
    # image = cv2.imread('path/to/image.jpg')
    # image_tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
    # results = detector.predict([image_tensor])

    logger.info("Instance segmentation example ready")
```

---

## Image Generation

### Stable Diffusion Implementation

Production-ready text-to-image generation with Stable Diffusion.

```python
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import torch
import numpy as np
from PIL import Image
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class StableDiffusionGenerator:
    """Production-ready Stable Diffusion image generator."""

    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        device: Optional[str] = None,
        enable_attention_slicing: bool = True,
        output_dir: str = "./generated_images"
    ):
        """
        Initialize Stable Diffusion generator.

        Args:
            model_id: Hugging Face model ID
            device: Device to use
            enable_attention_slicing: Enable attention slicing for lower memory usage
            output_dir: Directory to save generated images
        """
        try:
            from diffusers import StableDiffusionPipeline

            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Loading model: {model_id}")
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32
            )

            if enable_attention_slicing:
                self.pipe.enable_attention_slicing()

            self.pipe = self.pipe.to(self.device)
            logger.info("Stable Diffusion model loaded successfully")
        except ImportError:
            logger.error("diffusers not installed. Install with: pip install diffusers transformers")
            raise

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        height: int = 512,
        width: int = 512,
        seed: Optional[int] = None,
        num_images: int = 1
    ) -> List[Image.Image]:
        """
        Generate images from text prompt.

        Args:
            prompt: Text description of image to generate
            negative_prompt: Text description of what NOT to generate
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for classifier-free guidance
            height: Image height (must be multiple of 8)
            width: Image width (must be multiple of 8)
            seed: Random seed for reproducibility
            num_images: Number of images to generate

        Returns:
            List of generated PIL Images
        """
        try:
            # Validate dimensions
            if height % 8 != 0 or width % 8 != 0:
                raise ValueError("Height and width must be multiples of 8")

            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None

            logger.info(f"Generating {num_images} images with prompt: {prompt}")

            with torch.autocast("cuda") if self.device == 'cuda' else torch.no_grad():
                output = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=height,
                    width=width,
                    num_images_per_prompt=num_images,
                    generator=generator
                )

            images = output.images
            logger.info(f"Successfully generated {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise

    def generate_and_save(
        self,
        prompt: str,
        output_name: str,
        **kwargs
    ) -> List[str]:
        """
        Generate images and save to disk.

        Args:
            prompt: Text prompt
            output_name: Name for output files
            **kwargs: Additional arguments for generate()

        Returns:
            List of saved file paths
        """
        try:
            images = self.generate(prompt=prompt, **kwargs)

            saved_paths = []
            for idx, image in enumerate(images):
                filename = f"{output_name}_{idx}_{int(datetime.now().timestamp())}.png"
                filepath = self.output_dir / filename
                image.save(filepath)
                saved_paths.append(str(filepath))
                logger.info(f"Saved image to {filepath}")

            # Save metadata
            metadata = {
                'prompt': prompt,
                'num_images': len(images),
                'output_files': saved_paths,
                'timestamp': datetime.now().isoformat()
            }

            metadata_path = self.output_dir / f"{output_name}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            return saved_paths
        except Exception as e:
            logger.error(f"Error saving generated images: {str(e)}")
            raise

    def generate_with_upscaling(
        self,
        prompt: str,
        upscale_factor: int = 2,
        **kwargs
    ) -> Image.Image:
        """Generate image and upscale."""
        try:
            images = self.generate(prompt=prompt, **kwargs)
            image = images[0]

            new_size = (image.width * upscale_factor, image.height * upscale_factor)
            upscaled = image.resize(new_size, Image.LANCZOS)

            logger.info(f"Image upscaled from {image.size} to {upscaled.size}")
            return upscaled
        except Exception as e:
            logger.error(f"Error during upscaling: {str(e)}")
            raise


### GAN-based Image Generation

class GANGenerator:
    """GAN-based image generation with PyTorch."""

    def __init__(
        self,
        latent_dim: int = 100,
        device: Optional[str] = None
    ):
        """Initialize GAN generator."""
        self.latent_dim = latent_dim
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')

        # Define generator architecture
        self.generator = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 3 * 64 * 64),
            nn.Tanh()
        ).to(self.device)

        logger.info("GAN generator initialized")

    def generate(
        self,
        num_images: int = 1,
        seed: Optional[int] = None
    ) -> torch.Tensor:
        """Generate random images."""
        try:
            if seed is not None:
                torch.manual_seed(seed)

            self.generator.eval()
            with torch.no_grad():
                z = torch.randn(num_images, self.latent_dim, device=self.device)
                generated = self.generator(z)
                generated = generated.view(-1, 3, 64, 64)

            return generated.cpu()
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise


# Usage Example
def example_image_generation():
    """Complete example of image generation."""

    # Stable Diffusion
    generator = StableDiffusionGenerator(device='cuda')

    prompts = [
        "A beautiful sunset over mountains",
        "A futuristic city with flying cars",
        "A serene lake surrounded by pine trees"
    ]

    for prompt in prompts:
        images = generator.generate(
            prompt=prompt,
            num_inference_steps=50,
            guidance_scale=7.5,
            seed=42
        )
        logger.info(f"Generated image for: {prompt}")
```

---

## Data Augmentation

### Advanced Data Augmentation Strategies

Production-ready data augmentation implementations.

```python
import logging
import torch
import torchvision.transforms as transforms
from torchvision.transforms import functional as F
import numpy as np
from typing import List, Tuple, Optional, Callable
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2

logger = logging.getLogger(__name__)


class AdvancedAugmentation:
    """Advanced augmentation strategies for computer vision."""

    @staticmethod
    def create_pytorch_transforms(
        augmentation_strength: str = "medium",
        image_size: Tuple[int, int] = (224, 224)
    ) -> transforms.Compose:
        """
        Create PyTorch augmentation pipeline.

        Args:
            augmentation_strength: 'light', 'medium', or 'heavy'
            image_size: Target image size

        Returns:
            Composed transforms
        """
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )

        if augmentation_strength == "light":
            return transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.Resize(image_size),
                transforms.ToTensor(),
                normalize
            ])

        elif augmentation_strength == "medium":
            return transforms.Compose([
                transforms.RandomRotation(15),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.2),
                transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
                transforms.GaussianBlur(kernel_size=3),
                transforms.Resize(image_size),
                transforms.ToTensor(),
                normalize
            ])

        else:  # heavy
            return transforms.Compose([
                transforms.RandomRotation(20),
                transforms.RandomAffine(degrees=0, translate=(0.15, 0.15), scale=(0.8, 1.2)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.3),
                transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.3, hue=0.1),
                transforms.RandomErasing(p=0.5, scale=(0.02, 0.2)),
                transforms.GaussianBlur(kernel_size=3),
                transforms.Resize(image_size),
                transforms.ToTensor(),
                normalize
            ])

    @staticmethod
    def create_albumentations_transforms(
        augmentation_strength: str = "medium",
        image_size: Tuple[int, int] = (224, 224)
    ) -> A.Compose:
        """
        Create Albumentations pipeline (better for segmentation/detection).

        Args:
            augmentation_strength: 'light', 'medium', or 'heavy'
            image_size: Target image size

        Returns:
            Albumentations Compose object
        """
        if augmentation_strength == "light":
            transforms_list = [
                A.HorizontalFlip(p=0.5),
                A.Resize(*image_size),
                A.Normalize(),
                ToTensorV2()
            ]

        elif augmentation_strength == "medium":
            transforms_list = [
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.2),
                A.Rotate(limit=15, p=0.7),
                A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=15, p=0.7),
                A.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, p=0.5),
                A.GaussBlur(blur_limit=3, p=0.3),
                A.Resize(*image_size),
                A.Normalize(),
                ToTensorV2()
            ]

        else:  # heavy
            transforms_list = [
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.3),
                A.Rotate(limit=20, p=0.8),
                A.ShiftScaleRotate(shift_limit=0.15, scale_limit=0.3, rotate_limit=20, p=0.8),
                A.Perspective(scale=(0.05, 0.1), p=0.5),
                A.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.3, p=0.7),
                A.RandomRain(p=0.2),
                A.RandomFog(p=0.2),
                A.GaussNoise(p=0.2),
                A.GaussBlur(blur_limit=3, p=0.3),
                A.CoarseDropout(max_holes=8, max_height=32, max_width=32, p=0.3),
                A.Resize(*image_size),
                A.Normalize(),
                ToTensorV2()
            ]

        return A.Compose(transforms_list)

    @staticmethod
    def mixup(
        images: torch.Tensor,
        labels: torch.Tensor,
        alpha: float = 1.0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Mixup augmentation.

        Args:
            images: Batch of images
            labels: Batch of labels
            alpha: Beta distribution parameter

        Returns:
            Mixed images and soft labels
        """
        try:
            batch_size = images.size(0)
            index = torch.randperm(batch_size)

            lam = np.random.beta(alpha, alpha)
            mixed_images = lam * images + (1 - lam) * images[index]

            mixed_labels = lam * labels + (1 - lam) * labels[index]

            logger.info(f"Mixup applied with lambda: {lam:.4f}")
            return mixed_images, mixed_labels
        except Exception as e:
            logger.error(f"Error during mixup: {str(e)}")
            raise

    @staticmethod
    def cutmix(
        images: torch.Tensor,
        labels: torch.Tensor,
        alpha: float = 1.0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """CutMix augmentation."""
        try:
            batch_size, _, height, width = images.size()
            index = torch.randperm(batch_size)

            lam = np.random.beta(alpha, alpha)

            cut_ratio = np.sqrt(1 - lam)
            cut_h = int(height * cut_ratio)
            cut_w = int(width * cut_ratio)

            cx = np.random.randint(0, width)
            cy = np.random.randint(0, height)

            bbx1 = np.clip(cx - cut_w // 2, 0, width)
            bby1 = np.clip(cy - cut_h // 2, 0, height)
            bbx2 = np.clip(cx + cut_w // 2, 0, width)
            bby2 = np.clip(cy + cut_h // 2, 0, height)

            images[:, :, bby1:bby2, bbx1:bbx2] = images[index, :, bby1:bby2, bbx1:bbx2]

            lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (height * width))
            mixed_labels = lam * labels + (1 - lam) * labels[index]

            logger.info(f"CutMix applied with lambda: {lam:.4f}")
            return images, mixed_labels
        except Exception as e:
            logger.error(f"Error during cutmix: {str(e)}")
            raise


# Usage Example
def example_data_augmentation():
    """Complete example of data augmentation."""

    # PyTorch augmentation
    train_transforms = AdvancedAugmentation.create_pytorch_transforms(
        augmentation_strength="medium"
    )

    # Albumentations augmentation
    aug_transforms = AdvancedAugmentation.create_albumentations_transforms(
        augmentation_strength="medium"
    )

    logger.info("Data augmentation pipelines created successfully")
```

---

## Transfer Learning

### Complete Transfer Learning Workflow

Production-ready transfer learning implementation.

```python
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import models
import numpy as np

logger = logging.getLogger(__name__)


class TransferLearningPipeline:
    """Complete transfer learning pipeline."""

    def __init__(
        self,
        num_classes: int,
        base_model: str = "resnet50",
        pretrained: bool = True,
        device: Optional[str] = None,
        freeze_backbone: bool = True
    ):
        """
        Initialize transfer learning pipeline.

        Args:
            num_classes: Number of output classes
            base_model: Base model architecture
            pretrained: Use pretrained weights
            device: Device to use
            freeze_backbone: Freeze backbone weights
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_classes = num_classes
        self.base_model_name = base_model

        # Load pretrained model
        if base_model == "resnet50":
            base_model = models.resnet50(pretrained=pretrained)
            num_features = base_model.fc.in_features
        elif base_model == "resnet101":
            base_model = models.resnet101(pretrained=pretrained)
            num_features = base_model.fc.in_features
        elif base_model == "efficientnet_b0":
            base_model = models.efficientnet_b0(pretrained=pretrained)
            num_features = base_model.classifier[1].in_features
        else:
            raise ValueError(f"Unknown model: {base_model}")

        # Freeze backbone if requested
        if freeze_backbone:
            for param in base_model.parameters():
                param.requires_grad = False
            logger.info("Backbone frozen for transfer learning")

        # Replace classifier
        self.model = nn.Sequential(
            base_model,
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )

        self.model.to(self.device)
        logger.info(f"Transfer learning model initialized with {base_model}")

    def get_trainable_parameters(self) -> int:
        """Count trainable parameters."""
        return sum(p.numel() for p in self.model.parameters() if p.requires_grad)

    def unfreeze_backbone(self, num_layers: int = 2) -> None:
        """Gradually unfreeze backbone layers (fine-tuning)."""
        try:
            unfrozen = 0
            for param in reversed(list(self.model.parameters())):
                if unfrozen >= num_layers:
                    break
                param.requires_grad = True
                unfrozen += 1

            logger.info(f"Unfroze {unfrozen} backbone layers")
        except Exception as e:
            logger.error(f"Error unfreezing layers: {str(e)}")
            raise

    def train_step(
        self,
        images: torch.Tensor,
        labels: torch.Tensor,
        optimizer: optim.Optimizer,
        criterion: nn.Module
    ) -> float:
        """Execute single training step."""
        self.model.train()

        try:
            images, labels = images.to(self.device), labels.to(self.device)

            optimizer.zero_grad()
            outputs = self.model(images)
            loss = criterion(outputs, labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            optimizer.step()

            return loss.item()
        except Exception as e:
            logger.error(f"Error during training step: {str(e)}")
            raise

    def get_layer_wise_lr(
        self,
        base_lr: float = 0.001,
        decay: float = 0.1
    ) -> list:
        """
        Get layer-wise learning rates (lower LR for earlier layers).

        Args:
            base_lr: Base learning rate
            decay: Decay factor per layer

        Returns:
            List of parameter groups
        """
        param_groups = []
        for i, (name, params) in enumerate(self.model.named_parameters()):
            lr = base_lr * (decay ** i)
            param_groups.append({'params': params, 'lr': lr})

        return param_groups

    def setup_training(
        self,
        learning_rate: float = 0.001,
        use_layer_wise_lr: bool = False
    ) -> Tuple[optim.Optimizer, optim.lr_scheduler.LRScheduler]:
        """Setup optimizer and scheduler."""
        try:
            if use_layer_wise_lr:
                param_groups = self.get_layer_wise_lr(base_lr=learning_rate)
                optimizer = optim.Adam(param_groups)
            else:
                optimizer = optim.Adam(
                    [p for p in self.model.parameters() if p.requires_grad],
                    lr=learning_rate
                )

            scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode='max',
                factor=0.1,
                patience=3,
                verbose=True
            )

            logger.info("Optimizer and scheduler configured")
            return optimizer, scheduler
        except Exception as e:
            logger.error(f"Error setting up training: {str(e)}")
            raise


# Usage Example
def example_transfer_learning():
    """Complete transfer learning example."""

    num_classes = 10

    # Initialize pipeline
    pipeline = TransferLearningPipeline(
        num_classes=num_classes,
        base_model="resnet50",
        pretrained=True,
        freeze_backbone=True
    )

    # Setup training
    optimizer, scheduler = pipeline.setup_training(
        learning_rate=0.001,
        use_layer_wise_lr=True
    )

    # Training loop
    criterion = nn.CrossEntropyLoss()

    logger.info(f"Trainable parameters: {pipeline.get_trainable_parameters()}")
    logger.info("Transfer learning pipeline ready for training")
```

---

## Model Deployment

### Production Deployment Strategies

Production-ready model deployment implementations.

```python
import logging
import torch
import torch.nn as nn
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
import time
from dataclasses import asdict
from threading import Lock
import numpy as np

logger = logging.getLogger(__name__)


class ModelServer:
    """Production model server with batching and caching."""

    def __init__(
        self,
        model_path: str,
        device: Optional[str] = None,
        batch_size: int = 32,
        max_queue_size: int = 100
    ):
        """
        Initialize model server.

        Args:
            model_path: Path to saved model
            device: Device to use
            batch_size: Inference batch size
            max_queue_size: Maximum queue size
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = batch_size
        self.max_queue_size = max_queue_size
        self.lock = Lock()

        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model = self._load_model(checkpoint)
            self.model.eval()
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _load_model(self, checkpoint: Dict[str, Any]) -> nn.Module:
        """Load model from checkpoint."""
        # Implement based on your model architecture
        pass

    def warm_up(self, dummy_input_shape: tuple = (1, 3, 224, 224)) -> None:
        """Warm up model with dummy input."""
        try:
            with torch.no_grad():
                dummy_input = torch.randn(*dummy_input_shape).to(self.device)
                _ = self.model(dummy_input)
            logger.info("Model warm-up complete")
        except Exception as e:
            logger.error(f"Error during warm-up: {str(e)}")
            raise

    def predict(
        self,
        inputs: torch.Tensor,
        return_time: bool = False
    ) -> Union[torch.Tensor, tuple]:
        """
        Make predictions with timing.

        Args:
            inputs: Input tensor
            return_time: Return inference time

        Returns:
            Predictions (and time if requested)
        """
        try:
            with self.lock:
                start_time = time.time()

                with torch.no_grad():
                    inputs = inputs.to(self.device)
                    outputs = self.model(inputs)

                inference_time = time.time() - start_time

                if return_time:
                    return outputs, inference_time
                return outputs
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise

    def batch_predict(
        self,
        inputs_list: list,
        return_time: bool = False
    ) -> Union[list, tuple]:
        """
        Batch predict on multiple inputs.

        Args:
            inputs_list: List of input tensors
            return_time: Return inference time

        Returns:
            List of predictions (and time if requested)
        """
        try:
            all_outputs = []
            total_time = 0

            for i in range(0, len(inputs_list), self.batch_size):
                batch = torch.stack(inputs_list[i:i+self.batch_size])
                outputs, inf_time = self.predict(batch, return_time=True)
                all_outputs.extend(outputs)
                total_time += inf_time

            if return_time:
                return all_outputs, total_time
            return all_outputs
        except Exception as e:
            logger.error(f"Error during batch prediction: {str(e)}")
            raise


class ModelExporter:
    """Export models for deployment."""

    @staticmethod
    def export_to_onnx(
        model: nn.Module,
        dummy_input: torch.Tensor,
        output_path: str,
        input_names: list = None,
        output_names: list = None
    ) -> None:
        """
        Export model to ONNX format.

        Args:
            model: PyTorch model
            dummy_input: Sample input tensor
            output_path: Path to save ONNX model
            input_names: Names for input nodes
            output_names: Names for output nodes
        """
        try:
            import onnx

            input_names = input_names or ["input"]
            output_names = output_names or ["output"]

            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                input_names=input_names,
                output_names=output_names,
                opset_version=11,
                do_constant_folding=True,
                verbose=False
            )

            # Verify ONNX model
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)

            logger.info(f"Model exported to ONNX: {output_path}")
        except ImportError:
            logger.error("onnx not installed. Install with: pip install onnx")
            raise
        except Exception as e:
            logger.error(f"Error exporting to ONNX: {str(e)}")
            raise

    @staticmethod
    def export_to_torchscript(
        model: nn.Module,
        dummy_input: torch.Tensor,
        output_path: str,
        optimize: bool = True
    ) -> None:
        """
        Export model to TorchScript.

        Args:
            model: PyTorch model
            dummy_input: Sample input tensor
            output_path: Path to save TorchScript model
            optimize: Apply optimizations
        """
        try:
            model.eval()
            traced_model = torch.jit.trace(model, dummy_input)

            if optimize:
                traced_model = torch.jit.optimize_for_inference(traced_model)

            traced_model.save(output_path)
            logger.info(f"Model exported to TorchScript: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to TorchScript: {str(e)}")
            raise

    @staticmethod
    def export_to_tensorflow(
        model: nn.Module,
        output_dir: str
    ) -> None:
        """
        Export model to TensorFlow SavedModel format.

        Args:
            model: PyTorch model
            output_dir: Directory to save model
        """
        try:
            import onnx
            import onnx_tf.backend

            logger.info("Converting PyTorch -> ONNX -> TensorFlow")
            logger.info("TensorFlow export requires additional setup")
        except ImportError:
            logger.error("onnx-tf not installed. Install with: pip install onnx-tf")
            raise


class ModelOptimization:
    """Model optimization techniques."""

    @staticmethod
    def quantize_model(
        model: nn.Module,
        data_loader: torch.utils.data.DataLoader,
        device: str = 'cpu'
    ) -> nn.Module:
        """
        Post-training quantization.

        Args:
            model: PyTorch model
            data_loader: Calibration data loader
            device: Device to use

        Returns:
            Quantized model
        """
        try:
            model.eval()

            # Prepare model for quantization
            model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
            torch.quantization.prepare(model, inplace=True)

            # Calibrate
            with torch.no_grad():
                for inputs, _ in data_loader:
                    inputs = inputs.to(device)
                    model(inputs)

            # Convert
            torch.quantization.convert(model, inplace=True)

            logger.info("Model quantized successfully")
            return model
        except Exception as e:
            logger.error(f"Error during quantization: {str(e)}")
            raise

    @staticmethod
    def prune_model(
        model: nn.Module,
        amount: float = 0.3
    ) -> nn.Module:
        """
        Prune model weights.

        Args:
            model: PyTorch model
            amount: Fraction of weights to prune

        Returns:
            Pruned model
        """
        try:
            from torch.nn.utils import prune

            for name, module in model.named_modules():
                if isinstance(module, nn.Conv2d) or isinstance(module, nn.Linear):
                    prune.l1_unstructured(module, name='weight', amount=amount)
                    prune.remove(module, 'weight')

            logger.info(f"Model pruned with amount: {amount}")
            return model
        except Exception as e:
            logger.error(f"Error during pruning: {str(e)}")
            raise


# Usage Example
def example_model_deployment():
    """Complete example of model deployment."""
    logger.info("Model deployment examples ready")
```

---

## Summary and Best Practices

### Key Takeaways

1. **Always use error handling** - All examples include try-except blocks for robustness
2. **Logging is essential** - Configure logging for debugging and monitoring
3. **Resource management** - Handle GPU memory and cleanup properly
4. **Validation** - Always validate shapes, dimensions, and ranges
5. **Documentation** - Include docstrings and type hints
6. **Reproducibility** - Set seeds for deterministic results
7. **Performance** - Monitor inference time and memory usage
8. **Production-readiness** - Include checkpoints, metrics, and config management

### Dependencies

```bash
pip install torch torchvision torchaudio
pip install tensorflow  # Optional
pip install opencv-python pillow
pip install numpy scipy scikit-learn
pip install diffusers transformers
pip install ultralytics  # For YOLO
pip install albumentations
pip install onnx onnx-tf  # For model export
```

### Recommended Resources

- Official PyTorch Documentation: https://pytorch.org/docs
- Hugging Face Model Hub: https://huggingface.co/models
- OpenCV Documentation: https://docs.opencv.org
- Fast.ai Course: https://course.fast.ai
- Papers with Code: https://paperswithcode.com
