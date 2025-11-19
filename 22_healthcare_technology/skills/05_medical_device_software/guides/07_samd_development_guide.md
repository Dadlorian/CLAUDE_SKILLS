# Software as a Medical Device (SaMD) Development Guide

## SaMD Definition and Classification

### What Constitutes SaMD
- Software runs on general-purpose computing platform
- Addresses or treats a disease/condition
- Aids in diagnosis, treatment, or monitoring
- NOT part of hardware medical device

### Classification Framework

**Tier 1: Minimal Risk**
- Wellness or informational only
- No clinical decision support
- Example: General fitness tracking app

**Tier 2: Moderate Risk**
- Supports clinical decisions (decision aid)
- Serious health condition
- Moderate risk if malfunction
- Example: Blood glucose calculator

**Tier 3: Significant Risk**
- Autonomous treatment decisions
- Serious/critical health condition
- High risk if malfunction
- Example: Automated insulin dosing

## Clinical Validation Strategy

### Performance Metrics for Diagnostic SaMD
- Sensitivity (true positive rate)
- Specificity (true negative rate)
- Positive predictive value
- Negative predictive value
- Overall accuracy
- ROC curve and AUC

### Validation Approaches
1. Retrospective analysis of historical data
2. Prospective study in target population
3. External validation (different institution)
4. Real-world performance monitoring

## Algorithm Documentation

### Model Card (FDA Expects This)
- Algorithm name and version
- Intended clinical use
- Target population characteristics
- Training data: source, size, diversity
- Performance metrics achieved
- Limitations and failure modes
- Bias analysis by demographic group
- Update/retraining procedures

### Dataset Characterization
- Number of subjects
- Demographics (age, gender, race/ethnicity)
- Disease characteristics
- Data quality and completeness
- Temporal and geographic distribution
- Annotation methodology

## Labeling for SaMD

### Required Elements
- Intended use statement (specific)
- Algorithm explanation (plain language)
- Performance metrics (sensitivity, specificity)
- Limitations and failure modes
- Who should/shouldn't use device
- Instructions for use
- Warnings and contraindications
- Data quality requirements

## Real-World Performance Monitoring

### Monitoring Plan Components
- How will real-world data be collected?
- What metrics will be tracked?
- How frequently will data be analyzed?
- What thresholds trigger action?
- How will updates be communicated?

### Postmarket Surveillance Methods
- Electronic integration with EHR systems
- Patient registries
- Periodic comparative studies
- Complaint and feedback analysis
- Performance trending
