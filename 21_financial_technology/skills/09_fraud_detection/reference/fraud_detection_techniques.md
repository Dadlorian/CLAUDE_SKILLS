# Fraud Detection Techniques Reference

## Detection Method Categories

### 1. Rule-Based Detection
**Mechanism**: Predefined rules and thresholds trigger fraud alerts

**Advantages**
- Explainable and interpretable
- Fast execution (millisecond latency)
- Easy to maintain and update
- No training data required
- Deterministic and reliable

**Disadvantages**
- Requires manual rule creation
- Difficult to handle complex patterns
- High false positive rates
- Brittle to fraud evolution
- Labor-intensive maintenance

**Implementation Patterns**
- Simple threshold checks
- Multiple condition combinations
- Weighted scoring
- Dynamic thresholds based on context
- Exception handling

**Common Rules**
- Transaction amount > threshold
- Velocity checks (transactions per hour)
- Geographic impossibility detection
- Device/location mismatch
- Customer behavior deviation

### 2. Statistical Anomaly Detection
**Mechanism**: Detect transactions deviating from statistical norms

**Methods**
- **Z-score analysis**: Deviation from mean in standard deviations
- **Isolation Forest**: Anomaly as isolated data points
- **Local Outlier Factor**: Local density-based anomalies
- **Gaussian Mixture Models**: Probability density modeling
- **Interquartile Range (IQR)**: Quartile-based outliers

**Advantages**
- Unsupervised learning (no labels needed)
- Detects unknown fraud patterns
- Captures numerical anomalies
- Computationally efficient

**Disadvantages**
- Sensitive to distribution assumptions
- Difficulty with multimodal distributions
- High false positive rates
- Context-agnostic
- Requires baseline establishment

### 3. Machine Learning Classification
**Mechanism**: Trained models classify transactions as fraud/legitimate

**Supervised Approaches**
- **Logistic Regression**: Probability-based classification
- **Decision Trees**: Rule hierarchies
- **Random Forest**: Ensemble of decision trees
- **Gradient Boosting (XGBoost, LightGBM)**: Boosted ensemble trees
- **Neural Networks**: Deep learning classification
- **SVM**: Support Vector Machines
- **Naive Bayes**: Probabilistic classification

**Semi-Supervised Approaches**
- Self-training with unlabeled data
- Co-training with multiple views
- Pseudo-labeling techniques

**Advantages**
- Handles complex non-linear patterns
- Learns from historical fraud data
- Adaptable to new patterns
- High detection accuracy possible

**Disadvantages**
- Requires labeled training data
- Class imbalance issues
- Model drift over time
- Computational overhead
- Black-box nature (explainability)

### 4. Network & Graph Analysis
**Mechanism**: Detect fraud rings and collaborative fraud

**Techniques**
- **Community detection**: Identify fraud ring clusters
- **Graph clustering**: Group similar entities
- **Network motif detection**: Repeated fraud patterns
- **Shortest path analysis**: Relationship proximity
- **Ego networks**: First-degree connections

**Graph Components**
- Entities: Users, cards, devices, IPs, phones, emails
- Edges: Transactions, account links, shared attributes
- Edge weights: Frequency, amount, risk scores

**Advantages**
- Detects fraud rings and collusion
- Captures relationship patterns
- Scales to large networks
- Reveals hidden connections

**Disadvantages**
- Computational complexity for large graphs
- Latency challenges for real-time
- Requires relationship data
- Graph construction overhead

### 5. Behavioral Analytics
**Mechanism**: Track and analyze user behavior patterns

**Behavioral Dimensions**
- **Temporal patterns**: When user is active
- **Geographic patterns**: Where transactions occur
- **Device patterns**: Device types, fingerprints used
- **Amount patterns**: Typical transaction sizes
- **Merchant patterns**: Preferred merchants/categories
- **Frequency patterns**: Transaction velocity
- **Interaction patterns**: Login/interaction methods

**Profile Components**
- Baseline behavior establishment
- Deviation scoring
- Risk escalation
- Adaptive baselines

**Advantages**
- Detects account takeover
- Low false positives
- User-centric risk assessment
- Adaptive learning

**Disadvantages**
- Requires baseline establishment period
- Handles new user/account coldstart
- Requires rich behavioral data
- Privacy concerns with tracking

### 6. Device Fingerprinting
**Mechanism**: Identify and track devices through characteristics

**Fingerprint Components**
- Hardware characteristics
- Browser attributes
- Operating system details
- Network information
- Behavioral patterns
- Installation software

**Advantages**
- Persistent device identification
- Low false positive
- Helps with new user detection
- Supports velocity checks

**Disadvantages**
- Privacy and tracking concerns
- Legitimate device changes
- Mobile device variability
- Cross-device challenges

## Hybrid & Ensemble Approaches

### Multi-Model Ensembles
- Combine multiple model predictions
- Average, weighted, or voting methods
- Model confidence consideration
- Independent model monitoring

### Layered Detection
- **Layer 1**: Fast rules for obvious fraud
- **Layer 2**: Statistical anomalies
- **Layer 3**: ML-based scoring
- **Layer 4**: Behavioral analytics
- **Layer 5**: Network analysis

### Context-Aware Detection
- Customer risk profile integration
- Merchant risk classification
- Geographic risk assessment
- Time-of-day risk adjustment
- Device reputation integration

## Detection Metrics & Evaluation

### Key Metrics
- **True Positive Rate (TPR)**: Fraud correctly identified
- **False Positive Rate (FPR)**: Legitimate marked as fraud
- **Precision**: Fraud proportion in positive predictions
- **Recall**: Fraud proportion detected
- **F1-Score**: Harmonic mean of precision/recall
- **AUC-ROC**: Area under ROC curve
- **PR-AUC**: Area under Precision-Recall curve

### Business Metrics
- **Fraud Catch Rate**: % of fraud detected
- **False Decline Rate**: % of legitimate blocked
- **Case Coverage**: % of transactions scored
- **Investigation Backlog**: Cases needing review
- **Recovery Rate**: % of fraud loss recovered

## Detection Pipeline

1. **Data Collection**: Transaction and user data gathering
2. **Feature Engineering**: Feature creation and selection
3. **Preprocessing**: Data cleaning and normalization
4. **Score Calculation**: Rule and model scoring
5. **Threshold Application**: Decision boundary application
6. **Alert Generation**: Fraud alert creation
7. **Investigation**: Manual review and verification
8. **Feedback Loop**: Model retraining with verified cases

## Emerging Detection Technologies

- **Federated Learning**: Distributed model training
- **Adversarial Detection**: Defense against fraud adaptation
- **Transfer Learning**: Knowledge from related domains
- **Synthetic Data**: Oversampling fraud scenarios
- **Explainable AI**: Interpretable fraud decisions
- **Real-time Feature Streaming**: Dynamic feature computation
