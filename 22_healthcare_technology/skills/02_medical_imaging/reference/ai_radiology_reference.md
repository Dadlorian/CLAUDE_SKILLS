# AI in Radiology Reference

## Overview of AI in Medical Imaging

### Types of AI Applications
1. **Computer-Aided Detection (CAD)**: Find abnormalities
2. **Computer-Aided Diagnosis (CADx)**: Classify/characterize findings
3. **Segmentation**: Delineate anatomical structures
4. **Quantification**: Measure volumes, densities, features
5. **Triage**: Prioritize urgent cases
6. **Report Generation**: Automated structured reporting
7. **Workflow Optimization**: Study routing, protocol selection

### AI Workflow Integration
```
Image Acquisition → PACS → AI Processing → Results Storage → Radiologist Review → Final Report
                           ↓
                    Worklist Prioritization
```

## Deep Learning Architectures

### Convolutional Neural Networks (CNNs)

**Classic Architectures:**
- **AlexNet**: 2012 breakthrough, 8 layers
- **VGGNet**: Deep architecture (16-19 layers)
- **GoogLeNet/Inception**: Multi-scale feature extraction
- **ResNet**: Residual connections, 50-152 layers
- **DenseNet**: Dense connections between layers

**Medical Imaging Specific:**
- **U-Net**: Encoder-decoder for segmentation
- **V-Net**: 3D segmentation
- **nnU-Net**: Self-configuring U-Net
- **Attention U-Net**: Attention mechanisms for focus

### U-Net Architecture
```
Input Image (512x512x1)
    ↓
Encoder:
  Conv → ReLU → Conv → ReLU → MaxPool (256x256x64)
  Conv → ReLU → Conv → ReLU → MaxPool (128x128x128)
  Conv → ReLU → Conv → ReLU → MaxPool (64x64x256)
  Conv → ReLU → Conv → ReLU → MaxPool (32x32x512)
    ↓
Bottleneck:
  Conv → ReLU → Conv → ReLU (32x32x1024)
    ↓
Decoder:
  Upsample → Concat with Encoder → Conv → ReLU (64x64x512)
  Upsample → Concat with Encoder → Conv → ReLU (128x128x256)
  Upsample → Concat with Encoder → Conv → ReLU (256x256x128)
  Upsample → Concat with Encoder → Conv → ReLU (512x512x64)
    ↓
Output: Segmentation Mask (512x512x1)
```

**Key Features:**
- **Skip Connections**: Preserve spatial information
- **Symmetric**: Encoder-decoder symmetry
- **Efficient**: Works with limited training data
- **Versatile**: Adaptable to 2D and 3D

### Vision Transformers (ViT)

**Architecture:**
- Patch-based input (16×16 patches)
- Position embeddings
- Multi-head self-attention
- Feed-forward networks

**Medical Imaging Adaptations:**
- **Medical ViT**: Pretrained on ImageNet, fine-tuned
- **TransUNet**: Combines U-Net with Transformer
- **Swin Transformer**: Shifted windows, hierarchical
- **UNETR**: Transformer encoder + CNN decoder

**Advantages:**
- Global context understanding
- Long-range dependencies
- State-of-the-art performance

**Challenges:**
- Requires large datasets
- Computational cost
- Interpretability

## Clinical AI Applications

### Chest Radiography

**Pathologies Detected:**
- Pneumonia
- Pneumothorax
- Pleural effusion
- Cardiomegaly
- Nodules/masses
- Fractures
- Medical devices (lines, tubes)

**FDA-Cleared Products:**
- **Aidoc**: Pneumothorax, rib fractures
- **Lunit INSIGHT CXR**: 10+ findings
- **Annalise.ai CXR**: Comprehensive chest X-ray
- **qXR by Qure.ai**: Tuberculosis, COVID-19

**Performance:**
- **Sensitivity**: 85-95% for pneumonia
- **Specificity**: 80-90%
- **AUC**: 0.90-0.97 for various findings

### Chest CT

**Applications:**
- **Lung Nodule Detection**: CAD systems
- **Lung Nodule Characterization**: Benign vs. malignant
- **Pulmonary Embolism**: Automated detection
- **COVID-19**: Severity scoring, lesion quantification
- **Interstitial Lung Disease**: Pattern classification

**FDA-Cleared Products:**
- **Viz.ai Pulmonary Embolism**: PE detection and notification
- **Aidoc PE**: Pulmonary embolism triage
- **ClearRead CT**: Bone suppression for chest CT

**Quantification:**
- **Lung nodule volume**: Automated measurement
- **Growth rate**: Longitudinal tracking
- **COVID-19 burden**: % lung involvement

### Brain Imaging

**Stroke Detection:**
- **RAPID (iSchemaView)**: Perfusion analysis
- **Viz.ai Stroke**: Large vessel occlusion (LVO) detection
- **Brainomix e-Stroke**: Acute stroke assessment

**Key Metrics:**
- **Core infarct volume**: Irreversibly damaged tissue
- **Penumbra**: Tissue at risk (salvageable)
- **Mismatch ratio**: Penumbra/core (treatment decision)
- **Time to notification**: < 5 minutes critical

**Other Applications:**
- **Hemorrhage detection**: ICH, SAH, subdural
- **Aneurysm detection**: Screening CT angiography
- **Brain tumor segmentation**: Glioma, metastases
- **MS lesion quantification**: Longitudinal tracking
- **Alzheimer's**: Atrophy measurement, amyloid PET

### Cardiac Imaging

**Coronary Artery Calcium (CAC) Scoring:**
- **Automated calcium detection**: Agatston score
- **ClearRead CT**: Automated CAC quantification
- **HeartFlow**: FFR-CT (fractional flow reserve)

**Cardiac MRI:**
- **Chamber segmentation**: LV, RV volumes and function
- **Myocardial scar**: Late gadolinium enhancement quantification
- **Strain analysis**: Deformation imaging

**Echocardiography:**
- **EF automation**: Ejection fraction measurement
- **View classification**: Automated view recognition
- **Caption guidance**: Real-time image quality feedback

### Oncology Imaging

**Lung Cancer:**
- **Screening**: Nodule detection in LDCT
- **Risk prediction**: Malignancy probability scores
- **Response assessment**: RECIST measurement automation

**Breast Imaging:**
- **Mammography CAD**: Traditional and AI-based
- **Tomosynthesis**: 3D mammography detection
- **MRI**: Breast lesion segmentation and characterization

**Liver Metastases:**
- **Detection**: Automated lesion finding
- **Segmentation**: Volume measurement
- **Response**: Automated RECIST tracking

**Prostate:**
- **PI-RADS scoring**: Automated lesion scoring
- **Segmentation**: Prostate and zone delineation
- **Fusion**: MRI-ultrasound registration

### Musculoskeletal

**Fracture Detection:**
- **Extremities**: Automated fracture identification
- **Spine**: Vertebral fracture assessment
- **Ribs**: Rib fracture detection on CT

**Bone Age:**
- **Automated assessment**: Greulich-Pyle method
- **Accuracy**: Within 6 months of expert

**Arthritis:**
- **Joint space**: Automated measurement
- **Erosions**: Detection and quantification

## Training AI Models

### Data Preparation

**Dataset Requirements:**
- **Size**: Thousands to millions of images
- **Diversity**: Multiple institutions, demographics, scanners
- **Quality**: Expert annotations, ground truth
- **Balance**: Representative class distribution

**Annotation:**
- **Bounding boxes**: Object detection
- **Segmentation masks**: Pixel-level delineation
- **Labels**: Classification categories
- **Measurements**: Quantitative ground truth

**Tools:**
- **Labelbox**: Cloud annotation platform
- **CVAT**: Computer Vision Annotation Tool
- **3D Slicer**: Medical image annotation
- **ITK-SNAP**: Segmentation annotation

### Data Augmentation
```python
import albumentations as A

transform = A.Compose([
    A.RandomRotate90(p=0.5),
    A.Flip(p=0.5),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.3),
    A.GridDistortion(p=0.3),
    A.GaussNoise(var_limit=(10, 50), p=0.3),
])
```

**Augmentation Techniques:**
- **Geometric**: Rotation, flipping, scaling, translation
- **Intensity**: Brightness, contrast, gamma adjustment
- **Elastic Deformation**: Simulate anatomical variation
- **Noise**: Gaussian noise for robustness
- **Cropping**: Random crops for scale invariance

### Training Strategies

**Transfer Learning:**
1. **Pretrain**: ImageNet or large medical dataset (ChestX-ray14, MIMIC-CXR)
2. **Fine-tune**: Target dataset with lower learning rate
3. **Benefits**: Faster convergence, better performance with limited data

**Cross-Validation:**
- **K-Fold**: 5-fold or 10-fold typical
- **Stratified**: Maintain class distribution
- **Purpose**: Robust performance estimation

**Loss Functions:**
- **Binary Cross-Entropy**: Binary classification
- **Categorical Cross-Entropy**: Multi-class
- **Dice Loss**: Segmentation, handles class imbalance
- **Focal Loss**: Addresses class imbalance
- **Combined**: Dice + Cross-Entropy for segmentation

**Regularization:**
- **Dropout**: 0.3-0.5 typical
- **L2 Regularization**: Weight decay
- **Batch Normalization**: Stabilize training
- **Early Stopping**: Prevent overfitting

### Evaluation Metrics

**Classification:**
- **Accuracy**: Overall correct predictions
- **Sensitivity (Recall)**: True positive rate
- **Specificity**: True negative rate
- **Precision**: Positive predictive value
- **F1 Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under ROC curve

**Segmentation:**
- **Dice Coefficient**: 2×overlap / (pred + truth)
- **IoU (Intersection over Union)**: Overlap / union
- **Hausdorff Distance**: Maximum surface distance
- **Average Surface Distance**: Mean distance

**Detection:**
- **Precision**: True detections / total detections
- **Recall**: True detections / total ground truth
- **mAP (mean Average Precision)**: Average precision across classes
- **FROC**: Free-Response ROC for CAD

### MONAI Framework
```python
from monai.networks.nets import UNet
from monai.losses import DiceLoss
from monai.transforms import (
    Compose, LoadImaged, EnsureChannelFirstd, Spacingd,
    Orientationd, ScaleIntensityRanged, RandRotate90d
)

# Define transforms
train_transforms = Compose([
    LoadImaged(keys=["image", "label"]),
    EnsureChannelFirstd(keys=["image", "label"]),
    Spacingd(keys=["image", "label"], pixdim=(1.5, 1.5, 2.0)),
    Orientationd(keys=["image", "label"], axcodes="RAS"),
    ScaleIntensityRanged(keys=["image"], a_min=-175, a_max=250, b_min=0, b_max=1),
    RandRotate90d(keys=["image", "label"], prob=0.5),
])

# Define model
model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=2,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
)

# Define loss
loss_function = DiceLoss(to_onehot_y=True, softmax=True)
```

## Deployment

### Model Optimization

**Quantization:**
- **FP32 → FP16**: 2× faster inference, minimal accuracy loss
- **INT8**: 4× faster, slight accuracy loss
- **Mixed Precision**: Critical layers in FP32, others in FP16

**Pruning:**
- Remove redundant weights
- 20-50% reduction with minimal accuracy loss
- Structured vs. unstructured pruning

**Knowledge Distillation:**
- Train small model (student) to mimic large model (teacher)
- Retain performance, reduce size

**ONNX Runtime:**
```python
import onnx
import torch

# Export PyTorch model to ONNX
dummy_input = torch.randn(1, 1, 512, 512)
torch.onnx.export(model, dummy_input, "model.onnx")

# Load and run with ONNX Runtime
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
outputs = session.run(None, {"input": input_data})
```

**TensorRT (NVIDIA):**
- Optimize for NVIDIA GPUs
- 2-10× speedup
- FP16 and INT8 support

### DICOM Integration

**Input:**
```python
import pydicom

# Read DICOM
ds = pydicom.dcmread("ct_image.dcm")
pixel_array = ds.pixel_array

# Preprocess
hu_image = pixel_array * ds.RescaleSlope + ds.RescaleIntercept
normalized = (hu_image - window_center) / window_width
```

**Output as DICOM SR:**
```python
from pydicom.dataset import Dataset

# Create Structured Report
sr = Dataset()
sr.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.22'  # Basic Text SR
sr.SOPInstanceUID = generate_uid()
sr.Modality = 'SR'
sr.ContentDate = datetime.now().strftime('%Y%m%d')
sr.ContentTime = datetime.now().strftime('%H%M%S')

# Add findings
sr.ContentSequence = [
    {
        'ValueType': 'TEXT',
        'ConceptNameCodeSequence': [{'CodeValue': '121071', 'CodingSchemeDesignator': 'DCM', 'CodeMeaning': 'Finding'}],
        'TextValue': 'Pneumothorax detected with 95% confidence'
    }
]

sr.save_as("ai_results.dcm")
```

### Cloud Deployment

**AWS SageMaker:**
```python
import sagemaker
from sagemaker.pytorch import PyTorchModel

# Deploy model
pytorch_model = PyTorchModel(
    model_data='s3://bucket/model.tar.gz',
    role=role,
    framework_version='1.8',
    py_version='py3',
    entry_point='inference.py'
)

predictor = pytorch_model.deploy(
    instance_type='ml.p3.2xlarge',
    initial_instance_count=1
)
```

**Google Cloud Vertex AI:**
```python
from google.cloud import aiplatform

# Upload model
model = aiplatform.Model.upload(
    display_name="lung_nodule_detector",
    artifact_uri="gs://bucket/model/",
    serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/pytorch-gpu:latest"
)

# Deploy endpoint
endpoint = model.deploy(
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1
)
```

### Edge Deployment

**NVIDIA Jetson:**
- Compact GPU-enabled edge device
- TensorRT optimization
- Real-time inference at acquisition

**Intel NUC with Movidius:**
- CPU + VPU acceleration
- OpenVINO toolkit
- Low power consumption

**Benefits:**
- Low latency
- No network dependency
- Privacy (data stays local)
- Real-time feedback to operator

## Explainable AI (XAI)

### Grad-CAM (Gradient-weighted Class Activation Mapping)
```python
import torch
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# Define target layer
target_layers = [model.layer4[-1]]

# Create GradCAM
cam = GradCAM(model=model, target_layers=target_layers)

# Generate heatmap
grayscale_cam = cam(input_tensor=input_image, targets=None)

# Overlay on image
visualization = show_cam_on_image(original_image, grayscale_cam, use_rgb=True)
```

**Purpose:**
- Visualize which regions influenced decision
- Validate model is looking at relevant anatomy
- Build radiologist trust

### SHAP (SHapley Additive exPlanations)
```python
import shap

# Create explainer
explainer = shap.DeepExplainer(model, background_data)

# Calculate SHAP values
shap_values = explainer.shap_values(test_images)

# Visualize
shap.image_plot(shap_values, test_images)
```

### Attention Maps
- Built-in for Transformer models
- Visualize which patches received attention
- Multi-head attention for different features

### Saliency Maps
- Gradient of output with respect to input
- Highlights important pixels
- Simple but effective

## Regulatory and Clinical Validation

### FDA Approval Process

**510(k) Clearance:**
- **Requirement**: Substantially equivalent to predicate device
- **Timeline**: 3-12 months
- **Cost**: $10K-$100K
- **Most AI CAD**: This pathway

**De Novo Classification:**
- **Requirement**: Novel device, low-moderate risk
- **Timeline**: 6-12 months
- **Example**: First-in-class AI algorithms

**PMA (Premarket Approval):**
- **Requirement**: High-risk devices
- **Timeline**: 1-3 years
- **Cost**: $100K-$1M+
- **Rare for AI CAD**

### Clinical Validation Study

**Study Design:**
- **Retrospective**: Existing datasets
- **Prospective**: Real-world deployment
- **Reader Study**: Radiologists with/without AI
- **Standalone Performance**: AI alone metrics

**Endpoints:**
- **Sensitivity/Specificity**: Diagnostic accuracy
- **AUC**: Overall performance
- **Reader Agreement**: Inter-reader reliability
- **Time Savings**: Efficiency improvement
- **Clinical Outcomes**: Patient impact (ideal)

**Sample Size:**
- **Typical**: 300-1000 cases
- **Power Calculation**: Ensure statistical significance
- **Subgroup Analysis**: Performance across demographics

### Bias and Fairness

**Sources of Bias:**
- **Training Data**: Underrepresented populations
- **Scanner Variability**: Different manufacturers/protocols
- **Label Bias**: Annotator subjectivity
- **Selection Bias**: Non-representative sample

**Mitigation:**
- **Diverse Training Data**: Multiple institutions, demographics
- **Augmentation**: Simulate variability
- **Fairness Metrics**: Evaluate across subgroups
- **Continuous Monitoring**: Post-deployment surveillance

### Post-Market Surveillance
- **Performance Monitoring**: Track accuracy in production
- **Adverse Event Reporting**: FDA MedWatch
- **Software Updates**: Require FDA approval if significant
- **Real-World Evidence**: Ongoing validation

## AI Model Lifecycle

### Version Control
```
Git/DVC for code and data
Model Registry (MLflow, Weights & Biases)
Tagging: v1.0, v1.1, etc.
```

### Continuous Training
- **Trigger**: Performance degradation or new data
- **Retrain**: Incorporate new cases
- **Validate**: Ensure no regression
- **Deploy**: Update production model

### A/B Testing
- **Split Traffic**: 50% model A, 50% model B
- **Compare**: Metrics, user feedback
- **Gradual Rollout**: If B better, increase to 100%

### Monitoring
```python
from prometheus_client import Counter, Histogram

# Define metrics
inference_count = Counter('inference_total', 'Total inferences')
inference_time = Histogram('inference_duration_seconds', 'Inference time')

# Track
with inference_time.time():
    result = model.predict(image)
inference_count.inc()
```

## Datasets for AI Development

### Public Datasets

**Chest X-ray:**
- **ChestX-ray14 (NIH)**: 112K images, 14 labels
- **CheXpert (Stanford)**: 224K images, uncertainty labels
- **MIMIC-CXR**: 377K images, radiology reports
- **PadChest**: 160K images, multiple projections

**CT:**
- **LIDC-IDRI**: Lung nodule CT, expert annotations
- **LiTS**: Liver tumor segmentation
- **KiTS**: Kidney tumor segmentation
- **TCIA**: The Cancer Imaging Archive (multiple)

**Brain MRI:**
- **BraTS**: Brain tumor segmentation challenge
- **ADNI**: Alzheimer's Disease Neuroimaging Initiative
- **HCP**: Human Connectome Project
- **fastMRI**: Raw MRI data for reconstruction

**Pathology:**
- **Camelyon**: Breast cancer metastases
- **TCGA**: The Cancer Genome Atlas with imaging

## Future Directions

### Foundation Models
- **Large-scale pretraining**: Millions of medical images
- **Few-shot learning**: Adapt to new tasks with minimal data
- **Multi-modal**: Combine imaging with text, genomics

### Federated Learning
- **Privacy-preserving**: Train across institutions without sharing data
- **Collaborative**: Combine data diversity
- **Challenges**: Heterogeneity, communication cost

### Multimodal AI
- **Image + Clinical Data**: Demographics, labs, vitals
- **Image + Genomics**: Radiogenomics
- **Image + Text**: Radiology reports, clinical notes

### Real-time Acquisition Feedback
- **Quality Control**: Detect inadequate scans during acquisition
- **Protocol Optimization**: Adjust parameters on-the-fly
- **Operator Guidance**: Real-time coaching for technologists

### Generative AI
- **Synthetic Data**: Generate training data
- **Image Translation**: MRI to CT, low-dose to standard-dose
- **Report Generation**: Automated preliminary reports
- **Denoising**: Improve image quality

## Resources

- **MONAI**: Medical Open Network for AI (monai.io)
- **Grand Challenge**: Medical imaging competitions
- **RSNA AI Challenge**: Annual challenges with datasets
- **Medical Image Analysis**: Journal
- **MICCAI**: Medical Image Computing conference
