# AI Radiology Deployment Guide

## Deployment Architecture

### On-Premises Deployment
```
PACS → AI Gateway → AI Server (GPU) → Results Storage → PACS/Worklist
```

### Cloud Deployment
```
PACS → VPN/Gateway → Cloud AI Service → Results → On-Prem Integration
```

### Hybrid Deployment  
```
PACS → Edge AI (Screening) → Cloud AI (Deep Analysis) → Results
```

## Model Preparation

### ONNX Export
```python
import torch
import torch.onnx

# Load PyTorch model
model = torch.load('lung_nodule_model.pth')
model.eval()

# Dummy input
dummy_input = torch.randn(1, 1, 512, 512)

# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    'lung_nodule_model.onnx',
    export_params=True,
    opset_version=11,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)
```

### TensorRT Optimization (NVIDIA)
```python
import tensorrt as trt

# Load ONNX model
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network()
parser = trt.OnnxParser(network, logger)

with open('model.onnx', 'rb') as model:
    parser.parse(model.read())

# Build engine
config = builder.create_builder_config()
config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB
config.set_flag(trt.BuilderFlag.FP16)  # Enable FP16

engine = builder.build_serialized_network(network, config)

# Save engine
with open('model.trt', 'wb') as f:
    f.write(engine)
```

## Inference Server

### FastAPI Inference Service
```python
from fastapi import FastAPI, File, UploadFile
import onnxruntime as ort
import numpy as np
import pydicom
from io import BytesIO

app = FastAPI()

# Load model once at startup
session = ort.InferenceSession('lung_nodule_model.onnx')

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read DICOM
    contents = await file.read()
    ds = pydicom.dcmread(BytesIO(contents))
    
    # Preprocess
    pixel_array = ds.pixel_array.astype(np.float32)
    pixel_array = (pixel_array - pixel_array.mean()) / pixel_array.std()
    pixel_array = np.expand_dims(pixel_array, axis=(0, 1))  # Add batch and channel dims
    
    # Inference
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: pixel_array})
    
    # Post-process
    probability = float(output[0][0][1])  # Probability of nodule
    
    return {
        'study_uid': ds.StudyInstanceUID,
        'series_uid': ds.SeriesInstanceUID,
        'sop_uid': ds.SOPInstanceUID,
        'nodule_probability': probability,
        'prediction': 'positive' if probability > 0.5 else 'negative'
    }

# Start server: uvicorn server:app --host 0.0.0.0 --port 8000
```

### Docker Deployment
```dockerfile
FROM nvcr.io/nvidia/pytorch:23.04-py3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY model.onnx .
COPY server.py .

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  ai-inference:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## PACS Integration

### AI Gateway Service
```python
from pynetdicom import AE, evt, StoragePresentationContexts
import requests
import threading
import queue

class AIGateway:
    def __init__(self, ai_service_url):
        self.ai_service_url = ai_service_url
        self.ae = AE(ae_title='AI_GATEWAY')
        self.ae.supported_contexts = StoragePresentationContexts
        self.processing_queue = queue.Queue()
        
    def handle_store(self, event):
        """Receive study from PACS"""
        ds = event.dataset
        ds.file_meta = event.file_meta
        
        # Queue for AI processing
        self.processing_queue.put(ds)
        
        # Also forward to PACS if needed
        self.forward_to_pacs(ds)
        
        return 0x0000
    
    def forward_to_pacs(self, ds):
        """Forward to primary PACS"""
        ae = AE()
        ae.add_requested_context(ds.SOPClassUID)
        assoc = ae.associate('pacs.hospital.org', 104, ae_title='PACS')
        if assoc.is_established:
            assoc.send_c_store(ds)
            assoc.release()
    
    def process_ai_queue(self):
        """Worker thread for AI processing"""
        while True:
            ds = self.processing_queue.get()
            
            try:
                # Send to AI service
                with open('temp.dcm', 'wb') as f:
                    ds.save_as(f)
                
                with open('temp.dcm', 'rb') as f:
                    response = requests.post(
                        f'{self.ai_service_url}/predict',
                        files={'file': f}
                    )
                
                result = response.json()
                
                # Create DICOM SR with results
                sr = self.create_dicom_sr(ds, result)
                
                # Send SR to PACS
                self.send_sr_to_pacs(sr)
                
                # Update worklist if priority case
                if result['nodule_probability'] > 0.8:
                    self.prioritize_study(ds.StudyInstanceUID)
                    
            except Exception as e:
                print(f"Error processing: {e}")
            
            self.processing_queue.task_done()
    
    def create_dicom_sr(self, original_ds, ai_result):
        """Create DICOM Structured Report with AI results"""
        from pydicom.dataset import Dataset
        from pydicom.uid import generate_uid
        from datetime import datetime
        
        sr = Dataset()
        sr.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.22'  # Basic Text SR
        sr.SOPInstanceUID = generate_uid()
        sr.Modality = 'SR'
        sr.SeriesInstanceUID = generate_uid()
        sr.StudyInstanceUID = original_ds.StudyInstanceUID
        sr.PatientID = original_ds.PatientID
        sr.PatientName = original_ds.PatientName
        
        now = datetime.now()
        sr.ContentDate = now.strftime('%Y%m%d')
        sr.ContentTime = now.strftime('%H%M%S')
        
        # Add AI findings
        sr.ContentSequence = [{
            'ValueType': 'TEXT',
            'ConceptNameCodeSequence': [
                {'CodeValue': '121071', 'CodingSchemeDesignator': 'DCM', 'CodeMeaning': 'Finding'}
            ],
            'TextValue': f"AI-detected lung nodule probability: {ai_result['nodule_probability']:.2%}"
        }]
        
        return sr
    
    def start(self, port=11112):
        # Start AI processing workers
        for _ in range(4):
            worker = threading.Thread(target=self.process_ai_queue)
            worker.daemon = True
            worker.start()
        
        # Start DICOM server
        handlers = [(evt.EVT_C_STORE, self.handle_store)]
        self.ae.start_server(('', port), evt_handlers=handlers, block=True)

# Usage
gateway = AIGateway('http://localhost:8000')
gateway.start()
```

## Result Storage

### Store as DICOM SR
```python
def create_comprehensive_sr(study_uid, findings):
    """Create detailed DICOM SR with AI findings"""
    sr = Dataset()
    
    # ... (SR headers as above)
    
    # Container with multiple findings
    sr.ContentSequence = []
    
    for finding in findings:
        sr.ContentSequence.append({
            'ValueType': 'CONTAINER',
            'ContinuityOfContent': 'SEPARATE',
            'ConceptNameCodeSequence': [{
                'CodeValue': '121071',
                'CodingSchemeDesignator': 'DCM',
                'CodeMeaning': 'Finding'
            }],
            'ContentSequence': [
                {
                    'ValueType': 'TEXT',
                    'ConceptNameCodeSequence': [{
                        'CodeValue': '121072',
                        'CodingSchemeDesignator': 'DCM',
                        'CodeMeaning': 'Finding Site'
                    }],
                    'TextValue': finding['location']
                },
                {
                    'ValueType': 'NUM',
                    'ConceptNameCodeSequence': [{
                        'CodeValue': '121073',
                        'CodingSchemeDesignator': 'DCM',
                        'CodeMeaning': 'Confidence'
                    }],
                    'MeasuredValueSequence': [{
                        'NumericValue': finding['confidence'],
                        'MeasurementUnitsCodeSequence': [{
                            'CodeValue': '1',
                            'CodingSchemeDesignator': 'UCUM',
                            'CodeMeaning': 'probability'
                        }]
                    }]
                }
            ]
        })
    
    return sr
```

## Monitoring and Logging

### Performance Tracking
```python
import time
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
inference_count = Counter('ai_inference_total', 'Total AI inferences')
inference_duration = Histogram('ai_inference_duration_seconds', 'Inference duration')
positive_detections = Counter('ai_positive_detections_total', 'Positive detections')

@app.post("/predict")
async def predict_with_metrics(file: UploadFile = File(...)):
    start_time = time.time()
    
    # ... (inference code)
    
    # Track metrics
    inference_count.inc()
    inference_duration.observe(time.time() - start_time)
    
    if probability > 0.5:
        positive_detections.inc()
    
    return result

# Start metrics server
start_http_server(9090)
```

### Logging
```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_inference.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ai_inference')

def log_inference(study_uid, prediction, confidence, duration):
    logger.info(json.dumps({
        'event': 'inference',
        'study_uid': study_uid,
        'prediction': prediction,
        'confidence': confidence,
        'duration_ms': duration * 1000
    }))
```

## Clinical Validation

### A/B Testing
```python
import random

class ABTestingAI:
    def __init__(self, model_a_path, model_b_path):
        self.model_a = load_model(model_a_path)
        self.model_b = load_model(model_b_path)
        self.assignment_ratio = 0.5  # 50/50 split
    
    def predict(self, image):
        # Randomly assign to model A or B
        use_model_a = random.random() < self.assignment_ratio
        
        if use_model_a:
            result = self.model_a.predict(image)
            model_version = 'A'
        else:
            result = self.model_b.predict(image)
            model_version = 'B'
        
        # Log assignment for analysis
        log_ab_test(image_id, model_version, result)
        
        return result
```

### Ground Truth Comparison
```python
def evaluate_against_radiologist(ai_predictions, radiologist_reads):
    """Compare AI predictions to radiologist interpretations"""
    tp = fp = tn = fn = 0
    
    for ai_pred, rad_read in zip(ai_predictions, radiologist_reads):
        if ai_pred['positive'] and rad_read['positive']:
            tp += 1
        elif ai_pred['positive'] and not rad_read['positive']:
            fp += 1
        elif not ai_pred['positive'] and not rad_read['positive']:
            tn += 1
        else:
            fn += 1
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    
    return {
        'sensitivity': sensitivity,
        'specificity': specificity,
        'ppv': ppv,
        'total_cases': len(ai_predictions)
    }
```

## Regulatory Compliance

### Audit Trail
```python
def audit_ai_decision(study_uid, model_version, prediction, confidence):
    """Log AI decision for regulatory compliance"""
    audit_entry = {
        'timestamp': datetime.now().isoformat(),
        'study_uid': study_uid,
        'model_name': 'Lung Nodule Detector',
        'model_version': model_version,
        'prediction': prediction,
        'confidence': confidence,
        'user': 'AI_SYSTEM',
        'workstation': 'AI_SERVER_01'
    }
    
    # Store in audit database
    audit_db.insert(audit_entry)
    
    # Also send to ATNA-compliant syslog
    send_atna_audit(audit_entry)
```

### Model Versioning
```python
# Store model metadata
model_metadata = {
    'name': 'Lung Nodule Detector',
    'version': '2.1.0',
    'training_date': '2024-03-01',
    'training_dataset': 'LIDC-IDRI + Internal (5000 cases)',
    'performance': {
        'sensitivity': 0.92,
        'specificity': 0.88,
        'auc': 0.94
    },
    'fda_clearance': '510(k) K243876',
    'intended_use': 'Detection of lung nodules in CT scans'
}
```

## Best Practices

1. **Phased Rollout**: Start with shadow mode, then limited deployment
2. **Continuous Monitoring**: Track performance metrics in production
3. **Radiologist Feedback Loop**: Collect feedback for model improvement
4. **Graceful Degradation**: Fall back to no-AI workflow if service fails
5. **Clear Disclaimers**: Label AI-generated findings appropriately
6. **Regular Revalidation**: Periodically validate against new ground truth
7. **Documentation**: Comprehensive documentation of model and deployment

## Resources
- FDA AI/ML Medical Device Guidance
- MONAI Deploy framework
- TorchServe for production
- NVIDIA Clara Deploy
- ACR Data Science Institute guidelines
