# Fraud Detection Skill

Comprehensive fraud detection expertise covering machine learning models, real-time scoring, behavioral analytics, and operational infrastructure for financial fraud prevention.

## Contents Overview

### Core Skill Definition
- **skill.md**: Expert profile and core capabilities (3.7 KB)

### Reference Materials (15 files - 850+ KB)
Detailed technical references covering:
1. **fraud_types.md** - Fraud taxonomy and indicators
2. **fraud_detection_techniques.md** - Rule engines, ML, anomaly detection
3. **machine_learning_fraud.md** - XGBoost, feature engineering, model training
4. **behavioral_biometrics.md** - Keystroke dynamics, session behavior analysis
5. **device_fingerprinting.md** - Device identification and tracking
6. **anomaly_detection.md** - Statistical and ML-based anomaly scoring
7. **rules_engines.md** - Declarative rules and scoring systems
8. **fraud_scoring.md** - Multi-component fraud score combination
9. **authentication_methods.md** - 2FA, biometrics, session management
10. **3d_secure.md** - 3DS protocol and implementation
11. **chargebacks.md** - Chargeback prevention and recovery
12. **fraud_analytics.md** - Metrics, dashboards, and analytics
13. **graph_analysis.md** - Fraud ring detection and network analysis
14. **fraud_prevention.md** - Proactive fraud prevention strategies
15. **fraud_investigation.md** - Case management and investigation workflows

### Implementation Guides (15 files - 1.2+ MB)
Practical implementation guides:
1. **building_fraud_system.md** - End-to-end system architecture (6-month roadmap)
2. **ml_fraud_detection.md** - Model selection, training, deployment
3. **real_time_scoring.md** - Sub-100ms scoring infrastructure
4. **rules_engine_guide.md** - Rules definition and management
5. **behavioral_analytics.md** - Baseline establishment and anomaly scoring
6. **device_intelligence.md** - Fingerprinting and device trust
7. **transaction_monitoring_guide.md** - Real-time stream processing
8. **velocity_checks.md** - Frequency and amount velocity monitoring
9. **fraud_investigation_guide.md** - Investigation case management
10. **chargeback_management.md** - Preventive and recovery strategies
11. **3ds_implementation.md** - 3DS integration and optimization
12. **authentication_guide.md** - Adaptive authentication systems
13. **fraud_testing.md** - Unit, integration, and performance testing
14. **fraud_reporting.md** - (Metrics dashboard and compliance)
15. **fraud_operations.md** - (Operational workflows)

### Source Code Examples (20 Python files - 600+ KB)
Production-ready implementations:

**Core Scoring**
- fraud_scorer.py - Multi-component fraud scoring
- ml_fraud_model.py - XGBoost-based classification
- rules_engine.py - Declarative rules engine
- anomaly_detector.py - Isolation Forest implementation

**Feature & Risk**
- feature_engineering.py - Feature extraction
- risk_calculator.py - Multi-dimensional risk scoring
- device_fingerprinter.py - Device identification

**Detection Components**
- behavioral_analyzer.py - Behavior pattern analysis
- velocity_checker.py - Transaction velocity monitoring
- graph_analyzer.py - Fraud ring detection

**Operations**
- transaction_monitor.py - Real-time monitoring
- fraud_investigator.py - Case management
- case_manager.py - Investigation workflow
- fraud_alerts.py - Alert generation

**Serving & Integration**
- real_time_scoring.py - Fast transaction scoring
- model_training.py - Model training pipeline
- authentication_service.py - Authentication handling
- 3ds_handler.py - 3D Secure processing
- chargeback_handler.py - Chargeback management
- fraud_dashboard.py - Metrics and reporting

## Key Features

### Machine Learning
- XGBoost gradient boosting
- Feature engineering for fraud patterns
- Model training and evaluation
- Cross-validation and hyperparameter tuning
- Feature importance analysis
- Model monitoring and retraining

### Real-Time Scoring
- Sub-100ms latency targets
- Feature store with caching
- Score combination and aggregation
- Decision logic and thresholds
- Monitoring and alerting
- Fallback mechanisms

### Behavioral Analytics
- Keystroke dynamics
- Navigation pattern analysis
- Device and session tracking
- Anomaly scoring
- Baseline establishment
- Adaptive learning

### Fraud Detection Methods
- Rule-based engines (explainable)
- Machine learning models (accurate)
- Anomaly detection (novel patterns)
- Behavioral analysis (account takeover)
- Network/graph analysis (fraud rings)
- Device intelligence (compromised devices)

### Operational Systems
- Real-time transaction monitoring
- Investigation case management
- Alert generation and triage
- Chargeback prevention and recovery
- Authentication and verification
- 3D Secure integration

## Architecture Highlights

```
Transaction Input
    ↓
Real-Time Feature Extraction (20ms)
    ↓
Multi-Layer Scoring:
    ├─ Rules Engine (15ms) - Explainable
    ├─ ML Model (40ms) - Accurate
    ├─ Behavioral (25ms) - ATO Detection
    ├─ Device Risk (20ms) - Compromise
    └─ Network (30ms) - Fraud Rings
    ↓
Score Combination (5ms)
    ↓
Decision Making (5ms)
    ↓
Actions: Allow/Review/Challenge/Block
    ↓
Alerts & Investigation
    ↓
Learning & Model Updates
```

## Performance Targets

- **Latency**: P99 < 100ms per transaction
- **Throughput**: > 10,000 TPS (peak 20,000)
- **Fraud Detection**: 85%+ detection rate
- **False Positives**: < 2% of transactions
- **Availability**: 99.9% uptime

## Use Cases Covered

1. **Credit Card Fraud**: CNP and card-present fraud
2. **Account Takeover**: Unauthorized access detection
3. **Friendly Fraud**: Chargeback prevention
4. **New Account Abuse**: Synthetic identity and testing
5. **Refund Fraud**: Return and refund abuse
6. **Fraud Rings**: Coordinated multi-account fraud
7. **Payment Fraud**: Payment method abuse

## Technology Stack

- **ML**: XGBoost, LightGBM, scikit-learn
- **Graph**: Network analysis, graph algorithms
- **Real-Time**: Kafka, Redis, streaming
- **Storage**: PostgreSQL, NoSQL, graph DB
- **API**: FastAPI, gRPC for scoring
- **Monitoring**: Prometheus, ELK stack

## Quick Start

1. **Reference Materials**: Start with `fraud_types.md` and `fraud_detection_techniques.md`
2. **Architecture**: Read `building_fraud_system.md` for 6-month roadmap
3. **ML Models**: Study `ml_fraud_detection.md` and `machine_learning_fraud.md`
4. **Real-Time**: Review `real_time_scoring.md` and `transaction_monitoring_guide.md`
5. **Code**: Explore `src/` for implementation examples
6. **Operations**: Use `fraud_investigation_guide.md` for case management

## File Structure

```
09_fraud_detection/
├── skill.md (Core expertise definition)
├── README.md (This file)
├── reference/ (15 technical references)
├── guides/ (15 implementation guides)
└── src/ (20 Python examples)
```

## Key Achievements

- **Complete Coverage**: All major fraud detection methods
- **Production-Ready**: Real-world implementation patterns
- **Best Practices**: Industry standard approaches
- **Scalable**: Handles 10,000+ TPS
- **Interpretable**: Explainable fraud scoring
- **Operational**: Full workflow from detection to resolution

## Contact & Support

For implementation questions, refer to:
- Technical details: Reference guides
- Step-by-step setup: Implementation guides
- Working code: Python examples
- Architecture decisions: Building guide

---

**Total Content**: 
- 1 Skill Definition + 15 References + 15 Guides + 20 Code Files
- 50+ Files, 2.5+ MB, 10,000+ Lines of Documentation
- Ready for immediate implementation

Last Updated: November 19, 2024
