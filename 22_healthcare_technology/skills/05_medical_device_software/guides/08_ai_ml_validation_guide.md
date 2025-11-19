# AI/ML Medical Device Validation Guide

## Algorithm Development Documentation

### Model Card Format
**Algorithm Specification**
- Algorithm name and version
- Algorithm type (neural network, XGBoost, etc.)
- Key parameters and thresholds
- Mathematical basis/formula
- Training methodology

**Performance Documentation**
- Training set performance
- Validation set performance
- Test set performance (final evaluation)
- Performance by use case
- Cross-validation results

**Limitations**
- Documented failure modes
- Performance by patient subgroup
- Demographic bias analysis
- Edge cases and boundary conditions
- Data quality requirements

## Validation Strategy

### Data Split Approach
- **Training Set** (70-80%): Develop algorithm
- **Validation Set** (10-15%): Tune hyperparameters
- **Test Set** (10-15%): Final evaluation (untouched during development)

### Cross-Validation
- K-fold cross-validation (typically 5-10 folds)
- Prevents overfitting
- Estimates generalization performance

### External Validation
- Data from different institution/population
- Strongest validation evidence
- Demonstrates generalization
- Identifies population-specific biases

## Bias and Fairness Assessment

### Demographic Analysis
- Performance across age groups
- Performance across gender
- Performance across ethnicity
- Performance across disease severity
- Document any performance gaps

### Algorithm Limitations
- Where does algorithm perform poorly?
- Which patient populations at risk?
- What are failure modes?
- Document all in labeling

## Clinical Validation Study

### Study Design Considerations
- Patient population characteristics
- Sample size justification
- Study design (prospective, RCT, observational)
- Comparison standard (gold standard, clinician reading)
- Statistical analysis plan

### Performance Metrics
**For Classification (Diagnostic)**
- Sensitivity, specificity
- Positive/negative predictive values
- Accuracy, F1 score
- ROC curve, AUC

**For Segmentation**
- Dice coefficient
- Intersection over union
- Hausdorff distance

## Continuous Learning and Updates

### Algorithm Update Triggers
- Performance degradation detected
- New training data available
- Clinical feedback suggests improvement
- Regulatory requirement changes

### Safety Mechanisms for Updates
- Validation before deployment
- Staged rollout (10% → 50% → 100%)
- Monitoring during rollout
- Rollback capability if needed
- Version tracking

## Performance Monitoring

### Baseline Establishment
- Clinical trial performance
- Real-world baseline
- Expected variation range

### Real-World Tracking
- Automated performance monitoring
- Comparison to baseline
- Drift detection
- Performance by subgroup
- Alert thresholds for degradation

## FDA Submission Content

### Algorithm and Training
- Development approach documented
- Training methodology
- Dataset characteristics
- Model specifications
- Performance metrics

### Validation Evidence
- Cross-validation results
- External validation results
- Clinical study results
- Real-world performance plan

### Labeling
- Performance metrics included
- Limitations documented
- Appropriate use guidance
- Bias considerations
