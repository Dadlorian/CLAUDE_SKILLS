# Clinical Decision Support Subskill

## Overview
Complete production-grade clinical decision support (CDS) implementation covering CDS Hooks, rules engines, medication safety, AI/ML models, clinical pathways, and alert optimization.

## Contents

### Main Skill (skill.md)
Comprehensive clinical decision support expertise including:
- CDS architectures and standards
- Medication safety systems
- Clinical pathways automation
- AI/ML clinical models
- Alert fatigue prevention
- Clinical risk scores and calculators

### Reference Files (10 files)
1. **cds_hooks_reference.md** - HL7 CDS Hooks standard specification
2. **clinical_rules_engine_reference.md** - Drools, Arden Syntax, CQL
3. **medication_interaction_databases_reference.md** - FDB, Micromedex, Lexicomp
4. **clinical_pathways_reference.md** - Sepsis, STEMI, stroke protocols
5. **cds_five_rights_reference.md** - Right information, person, format, channel, time
6. **alert_fatigue_reference.md** - Metrics, mitigation, optimization
7. **clinical_risk_scores_reference.md** - CHADS₂-VASc, LACE, APACHE, qSOFA
8. **ai_clinical_models_reference.md** - Sepsis prediction, readmission, AKI
9. **order_sets_reference.md** - Smart order sets, bundles
10. **clinical_guidelines_reference.md** - GRADE, guideline implementation

### Guide Files (10 files)
1. **cds_hooks_implementation_guide.md** - Step-by-step CDS Hooks setup
2. **rules_engine_development_guide.md** - Drools and Python rules engines
3. **medication_safety_cds_guide.md** - Drug interactions, allergies, renal dosing
4. **clinical_pathway_implementation_guide.md** - Pathway automation
5. **ai_model_deployment_clinical_guide.md** - ML model deployment
6. **alert_optimization_guide.md** - Reducing alert fatigue
7. **order_appropriateness_checking_guide.md** - Imaging/lab utilization
8. **clinical_calculator_development_guide.md** - Risk score implementation
9. **cds_governance_guide.md** - Clinical oversight and approval
10. **sepsis_prediction_deployment_guide.md** - Sepsis ML model deployment

### Code Examples (15 files)
#### JavaScript/Node.js
1. **cds_hooks_service.js** - Complete CDS Hooks server with drug interactions
2. **readmission_risk_calculator.js** - LACE index calculator
3. **clinical_pathway_engine.js** - Pathway automation engine
4. **alert_fatigue_analytics.js** - Alert performance tracking
5. **clinical_calculator_chadsvasc.js** - CHADS₂-VASc calculator
6. **duplicate_therapy_detection.js** - Duplicate medication checking
7. **qTc_prolongation_alert.js** - QT interval risk assessment

#### Python
8. **drug_interaction_checker.py** - FDB integration for DDI checking
9. **allergy_checking_engine.py** - Drug-allergy cross-reactivity
10. **sepsis_prediction_model.py** - ML-based sepsis prediction
11. **drug_dose_calculator.py** - Weight-based and BSA-based dosing
12. **contraindication_checker.py** - Drug-disease contraindications
13. **renal_dosing_adjustment.py** - GFR-based dose adjustment
14. **clinical_guidelines_parser.py** - Guideline engine implementation

#### Configuration
15. **order_appropriateness_rules.json** - Imaging/lab appropriateness rules

## Key Features

### Production-Grade Quality
- Error handling and graceful degradation
- Performance optimization (< 3 second response)
- Comprehensive testing examples
- Security best practices
- Monitoring and analytics

### Clinical Safety
- Evidence-based rules
- Alert fatigue prevention
- Override tracking
- Clinical validation
- Regulatory compliance (FDA SaMD)

### Standards Compliance
- HL7 CDS Hooks
- FHIR R4
- RxNorm, LOINC, SNOMED CT
- Clinical Quality Language (CQL)

## Use Cases

### Medication Safety
- Real-time drug-drug interaction checking
- Drug-allergy cross-reactivity alerts
- Renal/hepatic dose adjustments
- Duplicate therapy detection
- Contraindication screening

### Clinical Pathways
- Sepsis bundle automation
- STEMI pathway activation
- Stroke protocol management
- Care bundle compliance tracking

### Predictive Analytics
- Sepsis early warning
- Readmission risk stratification
- AKI prediction
- Patient deterioration detection

### Decision Support
- Clinical risk calculators
- Guideline-based recommendations
- Order appropriateness checking
- Care gap identification

## Implementation Patterns

### CDS Hooks Integration
Standard-compliant services that integrate with Epic, Cerner, and other EHRs through CDS Hooks specification.

### Rules Engine
Both production Java (Drools) and Python implementations for clinical logic execution.

### AI/ML Models
Real-time inference with explainability (SHAP values), continuous monitoring, and bias detection.

### Alert Optimization
Severity tiering, context-aware filtering, temporal suppression, and override analytics.

## Best Practices

1. **Clinical Validation** - Physician review and approval
2. **Evidence-Based** - Ground in clinical guidelines
3. **User-Centered** - Minimize workflow disruption
4. **Performance** - Sub-3-second response times
5. **Monitoring** - Track metrics and outcomes
6. **Iteration** - Continuous improvement based on data
7. **Governance** - Clinical committee oversight
8. **Safety** - Fail gracefully, never block critical care

## Technologies

- **Languages**: JavaScript/Node.js, Python, Java
- **Frameworks**: Express, Flask, Spring Boot
- **Standards**: HL7 FHIR, CDS Hooks, RxNorm, LOINC
- **Databases**: PostgreSQL, MongoDB, Redis (caching)
- **ML Libraries**: scikit-learn, XGBoost, TensorFlow
- **Rules Engines**: Drools, Custom Python/JS

## Getting Started

1. Review **skill.md** for comprehensive CDS expertise
2. Read relevant **reference/** files for domain knowledge
3. Follow **guides/** for step-by-step implementation
4. Study **src/** code examples for production patterns
5. Adapt to your specific EHR and clinical environment

## Resources

- CDS Hooks: https://cds-hooks.org
- HL7 FHIR: https://www.hl7.org/fhir/
- OpenCDS: https://www.opencds.org
- AHRQ CDS Connect: https://cds.ahrq.gov/cdsconnect
- FDA CDS Guidance: https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software

## License

These educational materials are provided for learning and reference purposes.
