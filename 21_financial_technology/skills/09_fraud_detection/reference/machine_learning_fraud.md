# Machine Learning for Fraud Detection Reference

## ML Model Selection & Architecture

### Classification Models for Fraud

#### Ensemble Tree Methods (Recommended)

**Random Forest**
- 100-500 trees with bagging
- Feature importance ranking
- Handles non-linear patterns well
- Fast training and prediction
- Less prone to overfitting than single trees

**Gradient Boosting (XGBoost)**
- Sequential tree building with loss minimization
- Handle class imbalance with scale_pos_weight
- Feature importance from gain/cover/frequency
- Regularization (L1/L2) prevents overfitting
- Learning rate tuning for convergence
- Sub-sampling and column sampling

**LightGBM**
- Faster training than XGBoost
- Lower memory consumption
- Leaf-wise tree growth
- Categorical feature native support
- Best for large datasets

**CatBoost**
- Excellent categorical feature handling
- Automatic feature interactions
- Reduced overfitting tendency
- Symmetric trees structure
- Built-in evaluation metrics

#### Neural Network Approaches

**Dense Neural Networks**
```
Input Layer (features) -> Hidden Layer 1 (256 units, ReLU) ->
Dropout -> Hidden Layer 2 (128 units, ReLU) ->
Dropout -> Hidden Layer 3 (64 units, ReLU) ->
Output Layer (1 unit, Sigmoid)
```

**LSTM Networks (Time-series patterns)**
- Capture temporal transaction patterns
- Sequential fraud progression
- Long-term dependencies
- Gate mechanisms (input, forget, output)

**Autoencoders (Anomaly Detection)**
- Reconstruction-based anomaly scoring
- Bottleneck layer (32-64 dimensions)
- Reconstruction error as anomaly score
- Unsupervised training possible

#### Linear Models
- **Logistic Regression**: Probability calibration
- **Linear SVM**: Binary classification
- **Ridge/Lasso**: Regularized linear models

### Model Training Pipeline

#### Data Preparation
```
Raw Data -> Cleaning -> Feature Engineering ->
Scaling/Normalization -> Train/Test Split
```

#### Class Imbalance Handling
- **Oversampling minority (fraud)**
  - SMOTE: Generate synthetic fraud samples
  - ADASYN: Adaptive synthetic sampling

- **Undersampling majority (legitimate)**
  - Random undersampling
  - Stratified sampling

- **Cost-sensitive learning**
  - Weighted loss functions
  - Higher penalty for fraud misclassification

- **Threshold adjustment**
  - Lower decision boundary to catch more fraud
  - Optimal threshold selection

#### Cross-Validation Strategy
- **Stratified K-Fold**: Maintain fraud ratio in each fold
- **Time-based split**: Avoid data leakage (train on past, test on future)
- **Group K-Fold**: Non-overlapping customer groups

#### Hyperparameter Tuning
- **Grid Search**: Exhaustive parameter combinations
- **Random Search**: Random sampling of parameters
- **Bayesian Optimization**: Probabilistic parameter search
- **Optuna/Hyperopt**: Sophisticated optimization libraries

### Feature Engineering for Fraud Detection

#### Transaction Features
- Amount (raw, log-transformed, normalized)
- Amount deviation from baseline
- Amount percentile for customer
- Amount Z-score
- Transaction velocity (count, sum in time window)
- Time since last transaction
- Merchant category code (MCC)
- Merchant country/region
- Card type
- Card age
- Authentication method

#### Customer Features
- Account age
- Account velocity (transactions per hour/day)
- Transaction count history
- Average transaction amount
- Transaction amount volatility
- Refund rate
- Chargeback rate
- Account flagged history
- Device count
- Geographic diversity
- Merchant diversity

#### Device Features
- Device type (mobile, desktop, tablet)
- Device fingerprint
- Device age (first seen)
- Device fraud history
- Device location
- Device OS
- Device browser
- Device risk score

#### Behavioral Features
- Typing speed and patterns
- Mouse movement patterns
- Touch pressure and size
- Swipe patterns
- Time on page
- Click sequences
- Form completion time
- Session duration
- Navigation patterns

#### Network Features
- Customer-card network
- Customer-device network
- Customer-IP network
- Customer-email network
- Card-merchant network
- Device-location network
- Graph clustering coefficient
- Degree centrality

#### Temporal Features
- Hour of day
- Day of week
- Is weekend
- Is holiday
- Time since account creation
- Time since last activity
- Seasonality indicators
- Trend components

### Model Evaluation & Validation

#### Performance Metrics

**Classification Metrics**
```
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
Specificity = TN / (TN + FP)
```

**Ranking Metrics**
- AUC-ROC: Area under Receiver Operating Characteristic
- PR-AUC: Area under Precision-Recall curve
- KS Statistic: Maximum separation between distributions

**Business Metrics**
- Fraud Detection Rate @ specific FPR
- Cost-benefit analysis
- Coverage (% of transactions scored)
- Latency (prediction time)

#### Model Monitoring
- Feature distribution drift detection
- Model performance degradation
- Fraud evolution adaptation
- Retraining triggers
- A/B testing for model updates

### Model Deployment & Serving

#### Low-Latency Scoring
- Model serialization (pickle, ONNX, ModelDB)
- In-memory model caching
- Batch prediction optimization
- Async scoring with fallback
- Model versioning

#### Scalability Considerations
- Distributed inference
- GPU acceleration for neural networks
- Model compression and quantization
- Horizontal scaling architecture
- Load balancing

#### Production Monitoring
- Prediction latency tracking
- Model version performance comparison
- Feature availability monitoring
- Model retraining schedules
- A/B testing of model versions

### Model Explainability

#### Feature Importance Methods
- **Tree-based importance**: Gain, cover, frequency
- **SHAP values**: Feature contribution to prediction
- **LIME**: Local interpretable model-agnostic explanations
- **Permutation importance**: Feature impact on performance

#### Decision Explanation
- Top contributing features to fraud score
- Feature value ranges triggering alerts
- Risk factor breakdown
- Comparison to customer baseline

### Continuous Learning & Adaptation

#### Model Retraining
- Regular retraining schedules (daily/weekly)
- Incremental learning on new data
- Feedback loop from investigators
- Verified fraud labels integration
- False positive feedback incorporation

#### Fraud Evolution Handling
- New fraud pattern detection
- Model performance tracking
- Adaptive threshold adjustment
- Ensemble model rotation
- Adversarial robustness testing
