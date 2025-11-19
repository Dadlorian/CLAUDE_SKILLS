# Medical Imaging Modalities Reference

## Computed Tomography (CT)

### Physical Principles
- **X-ray Attenuation**: Different tissues absorb X-rays differently
- **Rotation**: X-ray tube rotates 360° around patient
- **Detectors**: Opposite the tube, measure transmitted radiation
- **Reconstruction**: Mathematical algorithms create cross-sectional images

### CT Numbers (Hounsfield Units)
```
Air:          -1000 HU
Lung:         -500 to -900 HU
Fat:          -120 to -90 HU
Water:        0 HU
Soft Tissue:  20 to 70 HU
Blood:        30 to 45 HU
Muscle:       10 to 40 HU
Bone:         300 to 3000 HU
```

### Acquisition Modes
- **Axial (Step-and-Shoot)**: Scan one slice, move table, repeat
- **Helical/Spiral**: Continuous table motion during scanning
- **Multislice CT (MSCT)**: Multiple detector rows, faster scanning

### Image Reconstruction
- **Filtered Back Projection (FBP)**: Classic, fast, noisy
- **Iterative Reconstruction (IR)**: Reduced noise, lower dose
- **Model-Based Iterative (MBIR)**: Best quality, slow
- **Deep Learning Reconstruction**: AI-based, latest advancement

### Clinical Applications
- **Trauma**: Fast whole-body assessment
- **Oncology**: Tumor detection, staging, follow-up
- **Vascular**: CT Angiography (CTA) for vessels
- **Cardiac**: Coronary artery calcium scoring, CTA
- **Chest**: Lung nodules, pulmonary embolism, COVID-19
- **Abdomen**: Appendicitis, bowel obstruction, kidney stones
- **Brain**: Stroke, hemorrhage, trauma

### Specialized CT
- **Dual-Energy CT**: Two different energies, material decomposition
- **Cardiac CT**: ECG-gating for heart imaging
- **CT Perfusion**: Blood flow measurement
- **CT Colonography**: Virtual colonoscopy
- **Dental CT (CBCT)**: Cone-beam for dental/maxillofacial

### Dose Considerations
- **CTDI (CT Dose Index)**: Standard dose metric
- **DLP (Dose Length Product)**: CTDI × scan length
- **ALARA**: As Low As Reasonably Achievable
- **Dose Reduction**: Lower kVp, tube current modulation, IR

### DICOM Specifics
- **SOP Class**: CT Image Storage (1.2.840.10008.5.1.4.1.1.2)
- **Multi-frame**: Enhanced CT Image Storage
- **Key Tags**: (0018,0060) KVP, (0018,1150) Exposure Time, (0028,1050) Window Center

## Magnetic Resonance Imaging (MRI)

### Physical Principles
- **Magnetic Field**: Strong magnet (1.5T, 3T, 7T) aligns hydrogen protons
- **RF Pulse**: Radio frequency pulse tips protons
- **Relaxation**: Protons return to alignment, emit signal
- **Spatial Encoding**: Gradients localize signal in 3D space

### Pulse Sequences
- **T1-Weighted**: Fat bright, water dark, anatomy
- **T2-Weighted**: Water bright, fat intermediate, pathology
- **FLAIR**: T2 with CSF suppressed, brain lesions
- **Diffusion-Weighted (DWI)**: Water diffusion, stroke detection
- **Gradient Echo (GRE)**: Fast imaging, susceptibility effects
- **Spin Echo (SE)**: Classic, reduced artifacts
- **Inversion Recovery**: Nulls specific tissue signals

### Contrast Mechanisms
- **T1 Relaxation**: Time for longitudinal magnetization recovery
- **T2 Relaxation**: Time for transverse magnetization decay
- **Proton Density**: Number of hydrogen protons
- **Diffusion**: Random water molecule motion
- **Perfusion**: Blood flow in capillaries
- **Susceptibility**: Local field distortions (blood products, iron)

### Advanced Techniques
- **Diffusion Tensor Imaging (DTI)**: White matter tractography
- **Functional MRI (fMRI)**: Brain activation mapping
- **MR Spectroscopy (MRS)**: Metabolite quantification
- **MR Angiography (MRA)**: Vascular imaging without contrast
- **Cardiac MRI**: Function, viability, delayed enhancement
- **MR Elastography (MRE)**: Tissue stiffness measurement

### Contrast Agents
- **Gadolinium-Based**: Shortens T1, enhances lesions
- **Safety**: Avoid in severe renal impairment (NSF risk)
- **Dose**: 0.1 mmol/kg body weight
- **Types**: Linear vs. macrocyclic (macrocyclic safer)

### Clinical Applications
- **Neuroimaging**: MS, tumors, stroke, dementia
- **Musculoskeletal**: Ligaments, tendons, cartilage, bone marrow
- **Cardiac**: Cardiomyopathy, viability, congenital heart disease
- **Liver**: Lesion characterization, cirrhosis
- **Prostate**: Cancer detection, PI-RADS scoring
- **Breast**: Supplemental screening, implant evaluation

### Safety Considerations
- **Projectile Risk**: Ferromagnetic objects attracted to magnet
- **Implants**: Pacemakers, cochlear implants (MRI-conditional devices OK)
- **Pregnancy**: Generally safe, avoid first trimester if possible
- **Claustrophobia**: Open-bore MRI, sedation
- **Acoustic Noise**: Ear protection required

### DICOM Specifics
- **SOP Class**: MR Image Storage (1.2.840.10008.5.1.4.1.1.4)
- **Enhanced MR**: Multi-frame storage
- **Key Tags**: (0018,0080) Repetition Time, (0018,0081) Echo Time, (0018,0087) Field Strength

## X-ray (Radiography)

### Types
- **Computed Radiography (CR)**: Phosphor plates, scanner readout
- **Digital Radiography (DR)**: Direct digital detectors
- **Fluoroscopy**: Real-time X-ray imaging
- **Portable X-ray**: Bedside imaging

### Image Characteristics
- **Projection**: 2D representation of 3D anatomy
- **Superimposition**: Overlapping structures
- **Contrast**: Density differences (bone bright, air dark)
- **Resolution**: Line pairs per mm

### Standard Views
- **Chest**: PA, lateral, lordotic, decubitus
- **Abdomen**: Supine, upright, decubitus
- **Extremities**: AP, lateral, oblique
- **Spine**: AP, lateral, flexion/extension

### Clinical Applications
- **Chest X-ray**: Pneumonia, CHF, pneumothorax, masses
- **Abdominal X-ray**: Obstruction, perforation, stones
- **Skeletal X-ray**: Fractures, arthritis, bone lesions
- **Dental**: Caries, periodontal disease, impacted teeth

### Dose Optimization
- **Collimation**: Limit beam to area of interest
- **Filtration**: Remove low-energy photons
- **kVp/mAs**: Optimize technique factors
- **Shielding**: Protect radiosensitive organs

### DICOM Specifics
- **CR SOP Class**: 1.2.840.10008.5.1.4.1.1.1
- **DX SOP Class**: 1.2.840.10008.5.1.4.1.1.1.1
- **Key Tags**: (0018,1150) Exposure Time, (0018,1151) X-ray Tube Current

## Ultrasound

### Physical Principles
- **Sound Waves**: High-frequency sound (2-18 MHz)
- **Transducer**: Converts electrical to mechanical and vice versa
- **Reflection**: Echoes from tissue interfaces
- **Attenuation**: Sound weakens with depth

### Imaging Modes
- **B-Mode (Brightness)**: 2D grayscale image
- **M-Mode (Motion)**: Time-motion display, cardiac valves
- **Doppler**: Blood flow velocity and direction
- **Color Doppler**: Flow encoded in color overlay
- **Power Doppler**: More sensitive to flow, no directional info
- **3D/4D Ultrasound**: Volume rendering (4D = real-time 3D)

### Doppler Applications
- **Continuous Wave**: High velocities, no depth localization
- **Pulsed Wave**: Depth-specific velocity measurement
- **Spectral Doppler**: Velocity vs. time graph
- **Tissue Doppler**: Myocardial motion

### Advanced Techniques
- **Elastography**: Tissue stiffness (liver fibrosis, breast masses)
- **Contrast-Enhanced**: Microbubbles for perfusion
- **Harmonic Imaging**: Improved image quality
- **Compound Imaging**: Multiple angles for artifact reduction

### Clinical Applications
- **Obstetrics**: Fetal development, anatomy, biometry
- **Cardiac**: Echo for function, valves, pericardium
- **Vascular**: DVT detection, carotid stenosis
- **Abdominal**: Gallstones, liver, kidneys, appendicitis
- **Musculoskeletal**: Tendons, muscles, joints
- **Thyroid**: Nodule characterization
- **Breast**: Supplemental to mammography

### Limitations
- **Operator-Dependent**: Skill significantly affects quality
- **Body Habitus**: Limited penetration in obese patients
- **Bone/Air**: Cannot image through bone or gas
- **Field of View**: Limited compared to CT/MRI

### DICOM Specifics
- **SOP Class**: Ultrasound Image Storage (1.2.840.10008.5.1.4.1.1.6.1)
- **Multi-frame**: Cine loops stored as multi-frame
- **Key Tags**: (0018,6011) Sequence of Ultrasound Regions

## Positron Emission Tomography (PET)

### Physical Principles
- **Radiotracer**: Positron-emitting isotope (F-18, C-11)
- **Annihilation**: Positron meets electron, produces two 511 keV photons
- **Coincidence Detection**: Detectors capture opposing photons
- **Reconstruction**: Determine tracer distribution

### Common Radiotracers
- **F-18 FDG**: Glucose analog, oncology, inflammation, neurology
- **F-18 Florbetapir**: Amyloid imaging, Alzheimer's
- **F-18 Florbetaben**: Amyloid imaging
- **F-18 NaF**: Bone metastases, more sensitive than bone scan
- **Ga-68 DOTATATE**: Neuroendocrine tumors
- **F-18 PSMA**: Prostate cancer
- **C-11 PIB**: Amyloid research

### PET/CT Fusion
- **Workflow**: CT for attenuation correction and localization
- **Registration**: Align PET and CT anatomically
- **Benefits**: Precise lesion localization, superior to PET alone
- **Display**: Fused color PET on grayscale CT

### Quantification
- **SUV (Standardized Uptake Value)**: Semi-quantitative metric
- **SUVmax**: Maximum pixel value in ROI
- **SUVmean**: Average value in ROI
- **SUVpeak**: Average of 1 cm³ sphere around hottest point
- **Total Lesion Glycolysis (TLG)**: SUVmean × metabolic tumor volume

### Clinical Applications
- **Oncology**: Staging, restaging, treatment response (most common)
- **Cardiology**: Myocardial viability, sarcoid
- **Neurology**: Dementia, epilepsy focus, Parkinson's
- **Infection/Inflammation**: FUO, large vessel vasculitis

### Limitations
- **Resolution**: 4-6 mm, limited for small lesions
- **False Positives**: Inflammation, infection uptake FDG
- **False Negatives**: Small lesions, low-grade tumors
- **Cost**: Expensive, limited availability
- **Preparation**: Fasting required for FDG

### DICOM Specifics
- **SOP Class**: PET Image Storage (1.2.840.10008.5.1.4.1.1.128)
- **Units**: BQML (Bq/mL) or CNTS (counts)
- **Key Tags**: (0054,1001) Units, (0028,1053) Rescale Slope

## Mammography

### Types
- **Digital Mammography**: Full-field digital
- **Tomosynthesis (DBT)**: 3D mammography, multiple angles
- **Screening**: Asymptomatic women
- **Diagnostic**: Evaluation of abnormalities

### Standard Views
- **MLO (Mediolateral Oblique)**: Angled view, includes most tissue
- **CC (Craniocaudal)**: Top-to-bottom view
- **Spot Compression**: Targeted compression of area
- **Magnification**: Closer look at calcifications

### Image Interpretation
- **Masses**: Shape, margin, density
- **Calcifications**: Morphology, distribution
- **Asymmetry**: Compare to prior and contralateral
- **Architectural Distortion**: Disrupted normal tissue
- **BI-RADS Categories**: 0-6 standardized reporting

### Computer-Aided Detection (CAD)
- **Classic CAD**: Mark suspicious findings
- **AI CAD**: Deep learning for detection/classification
- **Sensitivity**: Improved detection of cancers
- **Specificity**: Reduce false positives with AI

### Dose Considerations
- **Low Dose**: Optimized for breast imaging
- **AGD (Average Glandular Dose)**: Typical 1-3 mGy per view
- **Compression**: Reduces dose and improves quality

### DICOM Specifics
- **SOP Class**: Digital Mammography (1.2.840.10008.5.1.4.1.1.1.2)
- **Breast Tomosynthesis**: (1.2.840.10008.5.1.4.1.1.13.1.3)
- **CAD SR**: Structured report for CAD results

## Nuclear Medicine (SPECT)

### Physical Principles
- **Gamma Emission**: Radiotracer emits single photon
- **Gamma Camera**: Detects photons, creates 2D projection
- **SPECT**: Rotate camera 360°, reconstruct 3D
- **Collimator**: Determines photon direction

### Common Radiotracers
- **Tc-99m**: Most common, 6-hour half-life, versatile
- **I-131**: Thyroid therapy and imaging
- **In-111**: Infection imaging
- **Tl-201**: Myocardial perfusion (older)
- **Ga-67**: Infection, lymphoma

### Common Studies
- **Bone Scan**: Metastases, fractures, infection (Tc-99m MDP)
- **Myocardial Perfusion**: Coronary artery disease (Tc-99m sestamibi)
- **Thyroid Scan**: Nodules, hyperthyroidism (I-123, Tc-99m)
- **Renal Scan**: Function, obstruction (Tc-99m MAG3, DTPA)
- **Hepatobiliary**: Gallbladder function (Tc-99m HIDA)
- **Lung V/Q**: Pulmonary embolism (Tc-99m MAA, Xe-133)

### SPECT/CT
- **Hybrid**: Combines SPECT with CT
- **Benefits**: Anatomic localization, attenuation correction
- **Applications**: Bone scan, parathyroid, neuroendocrine

### DICOM Specifics
- **SOP Class**: Nuclear Medicine Image Storage (1.2.840.10008.5.1.4.1.1.20)
- **Multi-frame**: Dynamic and gated studies
- **Radiopharmaceutical**: Tags (0018,0031) sequence

## Interventional Radiology

### Modalities Used
- **Fluoroscopy**: Real-time X-ray guidance
- **CT Fluoroscopy**: Real-time CT for needle placement
- **Ultrasound**: Real-time soft tissue visualization
- **Cone-Beam CT**: 3D reconstruction from fluoroscopy

### Common Procedures
- **Angiography**: Vascular imaging and intervention
- **Biopsy**: Tissue sampling under imaging
- **Drainage**: Abscess, pleural effusion
- **Ablation**: Tumor destruction (RFA, microwave)
- **Embolization**: Vascular occlusion for hemorrhage/tumor
- **Vertebroplasty**: Fracture stabilization

### Dose Considerations
- **High Dose**: Prolonged fluoroscopy procedures
- **Monitoring**: Track cumulative air kerma
- **Shielding**: Lead aprons, thyroid shields
- **Pulsed Fluoroscopy**: Reduce frame rate to lower dose

## Modality Comparison

| Modality | Ionizing Radiation | Soft Tissue Contrast | Bone Detail | Speed | Cost |
|----------|-------------------|---------------------|-------------|-------|------|
| X-ray | Yes | Poor | Excellent | Very Fast | $ |
| CT | Yes | Good | Excellent | Fast | $$ |
| MRI | No | Excellent | Poor | Slow | $$$ |
| Ultrasound | No | Good | Poor | Fast | $ |
| PET | Yes | N/A (functional) | Poor | Moderate | $$$$ |
| SPECT | Yes | N/A (functional) | Poor | Moderate | $$ |

## Imaging Protocol Selection

### Brain
- **Acute Stroke**: CT (rule out hemorrhage), MRI DWI (ischemia)
- **Tumor**: MRI with contrast
- **Trauma**: CT
- **MS**: MRI FLAIR, T2

### Chest
- **Pneumonia**: Chest X-ray
- **Pulmonary Embolism**: CT Angiography
- **Lung Cancer Screening**: Low-dose CT
- **Interstitial Lung Disease**: High-resolution CT

### Abdomen
- **Appendicitis**: CT with contrast
- **Kidney Stones**: Non-contrast CT
- **Liver Lesion**: MRI with hepatocyte-specific contrast
- **Bowel Obstruction**: CT

### Cardiac
- **Coronary Artery Disease**: Coronary CT Angiography, nuclear perfusion
- **Myocardial Infarction**: Cardiac MRI (delayed enhancement)
- **Pericarditis**: Cardiac MRI, echo
- **Congenital**: Cardiac MRI, echo

### Musculoskeletal
- **Fracture**: X-ray
- **Ligament Tear**: MRI
- **Tendinitis**: Ultrasound, MRI
- **Bone Tumor**: X-ray, MRI

## Quality Assurance

### CT QA
- **Daily**: CT number accuracy (water phantom)
- **Weekly**: Noise, uniformity
- **Monthly**: Spatial resolution, slice thickness
- **Annual**: Dose measurements, comprehensive tests

### MRI QA
- **Daily**: SNR, image quality check
- **Weekly**: Geometric accuracy
- **Monthly**: Uniformity, ghosting
- **Annual**: Safety checks, comprehensive tests

### Mammography QA
- **Daily**: Phantom imaging
- **Weekly**: Viewbox luminance
- **Monthly**: Compression force, repeat analysis
- **Annual**: Full equipment evaluation (physicist)

## Radiation Safety

### Dose Limits
- **Occupational**: 50 mSv/year, 100 mSv/5 years
- **Public**: 1 mSv/year
- **Embryo/Fetus**: 5 mSv over pregnancy

### Protection Principles
- **Time**: Minimize exposure duration
- **Distance**: Inverse square law (double distance = 1/4 dose)
- **Shielding**: Lead aprons, barriers, collimation

### Patient Dose
- **Chest X-ray**: 0.02 mSv
- **CT Chest**: 7 mSv
- **CT Abdomen**: 10 mSv
- **PET/CT**: 25 mSv
- **Background**: 3 mSv/year (average natural)

## Future Directions

- **Photon-Counting CT**: Improved resolution and dose efficiency
- **AI Reconstruction**: Deep learning for ultra-low dose imaging
- **Molecular Imaging**: Targeted tracers for specific biology
- **Ultra-High Field MRI**: 7T and beyond for research
- **Portable MRI**: Low-field MRI for bedside use
- **Spectral CT**: Energy-resolved imaging
- **Theranostics**: Same tracer for imaging and therapy
