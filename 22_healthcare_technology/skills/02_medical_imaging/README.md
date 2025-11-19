# Medical Imaging Subskill

## Overview
Complete medical imaging skill covering DICOM, PACS, VNA, medical image processing, AI in radiology, and healthcare imaging standards.

## Structure

### skill.md
Main skill file with comprehensive coverage of:
- DICOM Protocol and Standard
- PACS/VNA Architecture  
- Medical Image Processing
- AI in Radiology
- Imaging Modalities (CT, MRI, X-ray, Ultrasound, PET)
- IHE Radiology Profiles
- Teleradiology
- Workflow Management

### Reference Files (10)
1. dicom_standard_reference.md - Complete DICOM specification
2. pacs_architecture_reference.md - PACS design and implementation
3. medical_imaging_modalities_reference.md - CT, MRI, X-ray, etc.
4. dicom_tags_reference.md - Critical DICOM tags and formats
5. ihe_radiology_profiles_reference.md - IHE integration profiles
6. image_formats_reference.md - DICOM, NIFTI, compression
7. ai_radiology_reference.md - Deep learning for medical imaging
8. teleradiology_reference.md - Remote radiology workflows
9. vna_reference.md - Vendor Neutral Archive architecture
10. imaging_workflow_reference.md - Clinical workflows

### Guide Files (10)
1. dicom_implementation_guide.md - Implementing DICOM
2. pacs_integration_guide.md - Integrating with PACS systems
3. medical_image_viewer_development_guide.md - Building viewers
4. dicom_networking_guide.md - DICOM networking (C-STORE, C-FIND, C-MOVE)
5. ai_radiology_deployment_guide.md - Deploying AI models
6. 3d_reconstruction_guide.md - 3D visualization
7. image_segmentation_guide.md - Segmentation algorithms
8. teleradiology_setup_guide.md - Setting up teleradiology
9. dicom_security_guide.md - Security and encryption
10. imaging_workflow_optimization_guide.md - Workflow optimization

### Code Examples (15)
1. dicom_server_orthanc.py - Orthanc PACS integration
2. dicom_parser.js - JavaScript DICOM parsing
3. dicom_viewer_cornerstone.html - Web-based DICOM viewer
4. pacs_query_retrieve.py - Complete C-FIND/C-MOVE implementation
5. dicom_networking_scu_scp.py - Full DIMSE service implementation
6. image_segmentation_unet.py - U-Net for medical image segmentation
7. 3d_reconstruction_marching_cubes.py - 3D volume rendering
8. dicom_anonymization.js - PHI removal
9. ai_lung_nodule_detection.py - AI detection model
10. dicom_to_png_converter.py - Format conversion
11. worklist_scp_server.py - Modality worklist server
12. dicom_metadata_extraction.js - Metadata extraction
13. image_quality_assessment.py - Quality metrics
14. teleradiology_transmission.js - Remote transmission
15. dicom_sr_parser.py - Structured report parsing

## Key Technologies
- **DICOM**: Standard for medical imaging
- **PACS**: Picture Archiving and Communication System
- **VNA**: Vendor Neutral Archive
- **IHE**: Integrating the Healthcare Enterprise profiles
- **AI/ML**: Deep learning for radiology (MONAI, PyTorch)
- **Web Viewers**: cornerstone.js, OHIF Viewer
- **Python Libraries**: pydicom, pynetdicom, SimpleITK
- **JavaScript Libraries**: dicom-parser, cornerstone

## Use Cases
- PACS/VNA implementation and integration
- DICOM viewer development (web and desktop)
- Medical image processing pipelines
- AI model deployment for radiology
- Teleradiology systems
- Healthcare IT integration (RIS, EMR)
- Research data management
- Clinical workflow optimization

## Production Ready
All code examples follow industry best practices:
- Error handling and logging
- DICOM standard compliance
- Security and PHI protection
- Performance optimization
- Comprehensive documentation

## Getting Started
1. Review skill.md for conceptual overview
2. Study reference files for detailed specifications
3. Follow guides for step-by-step implementation
4. Use code examples as production templates

## Standards Compliance
- DICOM 2023e
- IHE Radiology Technical Framework
- HL7 v2.x and FHIR
- HIPAA Security and Privacy Rules
- FDA regulations for AI/ML medical devices

---
Created as part of Healthcare Technology skill domain
