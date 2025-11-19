# Anomaly Detection Reference

## Overview
Anomaly detection identifies transactions and behaviors that significantly deviate from established patterns, flagging them for review without requiring labeled fraud data.

## Anomaly Detection Methods

### Statistical Methods

#### Z-Score Analysis
```
Z-Score = (X - μ) / σ

Where:
  X = observation value
  μ = mean of distribution
  σ = standard deviation

Classification:
  |Z-Score| < 2: Normal (95% confidence)
  |Z-Score| 2-3: Anomalous (95-99.7% confidence)
  |Z-Score| > 3: Highly anomalous (99.7%+ confidence)
```

**Application**
- Transaction amount anomaly
- Transaction velocity anomaly
- Deviation from historical patterns
- Customer-specific baselines

**Advantages**
- Simple and fast
- Interpretable results
- No training required
- Handles numerical data well

**Disadvantages**
- Assumes normal distribution
- Sensitive to outliers
- Doesn't capture multimodal distributions
- Limited for high-dimensional data

#### Interquartile Range (IQR)
```
Q1 = 25th percentile
Q3 = 75th percentile
IQR = Q3 - Q1

Lower Bound = Q1 - 1.5 * IQR
Upper Bound = Q3 + 1.5 * IQR

Points outside bounds = anomalies
```

**Application**
- Transaction amount boundaries
- Velocity thresholds
- Distribution-free approach
- Robust to outliers

### Machine Learning Methods

#### Isolation Forest
- Isolates anomalies by random tree splits
- Anomalies isolated in fewer splits
- Anomaly score: average path length
- Unsupervised learning
- Efficient for high-dimensional data

**Implementation**
```
1. Create random forest with isolation trees
2. Random feature selection for splits
3. Random split values for each feature
4. Score transaction by isolation efficiency
5. Anomaly if path length is short
```

**Advantages**
- No distance metric required
- Handles high-dimensional data
- Efficient computation
- Works on unlabeled data

#### Local Outlier Factor (LOF)
- Measures local density deviation
- Compares local density to neighbors
- High deviation = anomaly
- Detects contextual anomalies

**Implementation**
```
1. Calculate k-nearest neighbors
2. Compute local reachability density
3. Compare to neighbor densities
4. LOF = density ratio (>1 = anomaly)
```

**Advantages**
- Detects density-based anomalies
- Context-aware detection
- Handles varying densities

**Disadvantages**
- Computationally expensive
- Parameter k sensitivity
- Difficult to scale

#### Gaussian Mixture Models (GMM)
- Models normal data as mixture of Gaussians
- Fits multiple distributions
- Probability density estimation
- Anomaly = low probability regions

**Implementation**
```
1. Train GMM on normal transactions
2. Estimate mixing coefficients
3. For new transaction: calculate likelihood
4. Low likelihood = anomaly
```

**Advantages**
- Flexible distribution modeling
- Probabilistic framework
- Multi-modal distribution handling

#### Autoencoders (Neural Networks)
- Learns compact representation
- Reconstruction error indicates anomaly
- Bottleneck layer = compressed features
- Works on complex patterns

**Architecture**
```
Input (features) ->
Encoder -> Bottleneck (lower dim) ->
Decoder -> Output (reconstructed)

Anomaly Score = Reconstruction Error
```

**Advantages**
- Learns complex non-linear patterns
- Handles high-dimensional data
- Unsupervised learning
- Transfer learning possible

**Disadvantages**
- Training data required
- Parameter tuning complex
- Black-box decision making

### Time-Series Anomaly Detection

#### ARIMA (AutoRegressive Integrated Moving Average)
- Models temporal patterns
- Predicts expected value
- Deviation = anomaly
- Good for stationary series

#### Seasonal Decomposition
```
Time Series = Trend + Seasonal + Residual

Anomaly Detection on Residual Component
```

#### Change Point Detection
- Sudden shift in distribution
- Cumulative sum (CUSUM)
- Dynamic programming
- Bayesian methods

## Anomaly Scoring

### Single Feature Anomaly
```
Feature_Anomaly_Score = |Feature_Value - Baseline| / Baseline_Std_Dev

Normalization:
  0-1 range: min(Feature_Score / Threshold, 1.0)
```

### Multi-Feature Aggregation
```
Composite_Score = sqrt(
  w1 * (amount_score)^2 +
  w2 * (velocity_score)^2 +
  w3 * (location_score)^2
)
```

### Contextual Scoring
- Customer risk profile adjustment
- Merchant category adjustment
- Time-of-day adjustment
- Day-of-week adjustment
- Geographic risk factor

## Threshold Setting

### Static Thresholds
```
Score < 0.3: Normal, allow
Score 0.3-0.6: Monitor, optional review
Score 0.6-0.8: Require verification
Score > 0.8: Block and investigate
```

### Dynamic Thresholds
- Adjust by customer segment
- Merchant category variation
- Time-based adjustment
- Seasonal variations
- VIP customer lower thresholds

### Adaptive Thresholds
- Learn from feedback
- Adjust based on false positive rate
- Optimization for business metrics
- Regular recalibration

## Baseline Establishment

### Initialization Period
- 2-4 weeks of normal activity
- Ignore first few days (extreme variability)
- Exclude known fraud transactions
- Establish statistical distributions

### Feature Baselines
```
For each customer:
  - Transaction amount: mean, std dev, min, max
  - Transaction velocity: hourly rate, daily rate
  - Typical merchants: categories, frequency
  - Geographic: typical locations
  - Temporal: time-of-day patterns
  - Device: typical device usage
```

### Adaptive Baselines
- Gradual baseline updates
- Detect permanent behavior changes
- Weight recent activity higher
- Seasonal adjustment factors
- Trend incorporation

## Anomaly Investigation

### Feature Contribution
- Which features most anomalous?
- Feature-level anomaly scores
- Top 5 contributing features
- Explanation of deviation

### Contextual Information
- Recent account activity
- Device history
- Merchant history
- Geographic patterns
- Comparison to peer group

### Risk Escalation
```
Single Anomaly (low) ->
Multiple Anomalies (medium) ->
Persistent Anomalies (high) ->
Investigation & Verification (action)
```

## Advantages & Limitations

### Advantages of Anomaly Detection
- No labeled fraud data required
- Detects unknown fraud patterns
- Captures novelty in fraud
- Complements supervised models
- Explainable decisions

### Limitations
- High false positive rate
- Baseline establishment required
- Struggle with gradual fraud evolution
- Need appropriate feature engineering
- Threshold setting challenges

## Anomaly Detection Applications

### Transaction-Level Detection
- Single transaction amount anomaly
- Unusual merchant type
- Atypical transaction time
- Different location

### Account-Level Detection
- Account velocity spike
- New device addition
- Geographic impossibility
- Behavior pattern change

### Network-Level Detection
- Multiple accounts anomaly
- Device sharing anomaly
- Fraud ring patterns
- Collusion indicators

## Hybrid Approach

```
Anomaly_Risk =
  0.4 * Statistical_Anomaly +
  0.3 * ML_Anomaly (Isolation Forest) +
  0.2 * Behavioral_Anomaly +
  0.1 * Network_Anomaly

Combines multiple anomaly perspectives
```

## Monitoring & Maintenance

### Performance Metrics
- Anomaly detection rate
- False positive rate
- Precision and recall
- Coverage (% of transactions)

### Baseline Recalibration
- Weekly baseline updates
- Seasonal adjustment factors
- Trend incorporation
- Outlier exclusion

### Feedback Loop
- Investigator feedback
- Verified fraud cases
- Customer confirmation
- Model retraining
