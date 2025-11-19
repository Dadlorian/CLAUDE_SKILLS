# Risk Assessment and Scoring

## Risk Assessment Framework

### Components of Risk Assessment

```
Customer Risk Profile = Σ(Factor_i × Weight_i)

Where:
├── Customer Attributes (25%): Type, size, ownership
├── Geographic Risk (20%): Customer and counterparty locations
├── Industry Risk (15%): Business type and practices
├── Transaction Profile (20%): Amount, frequency, patterns
├── Behavioral Risk (10%): Actual vs. expected activity
└── Regulatory/Reputational (10%): PEP, sanctions, adverse media
```

### Risk Scoring Methodology

#### Quantitative Scoring

```
Individual Risk Factors:

1. Customer Type Risk (Individual)
   ├── Individual: 20 points
   ├── Small business: 30 points
   ├── Medium enterprise: 40 points
   ├── Large corporation: 50 points
   └── Financial institution: 25 points

2. Geographic Risk (Customer Location)
   ├── Low-risk jurisdiction: 10 points
   ├── Medium-risk jurisdiction: 30 points
   ├── High-risk jurisdiction: 50 points
   ├── OFAC-embargoed country: 100 points
   └── Jurisdiction rating: Dynamic per FATF

3. Industry Risk
   ├── Low-risk industry: 15 points
   ├── Medium-risk industry: 40 points
   ├── High-risk industry: 70 points
   └── FATF-designated DNFBP: 85 points

4. Transaction Volume Risk
   ├── Low: 10 points
   ├── Medium: 30 points
   ├── High: 50 points
   └── Unexplained increase: Additional 30 points

5. PEP/Sanctions/Adverse Media Risk
   ├── No indicators: 0 points
   ├── Minor indicators: 25 points
   ├── Significant indicators: 60 points
   └── Confirmed designation: 100 points

Total Score Calculation:
Risk_Score = Σ(Factor_Score × Assigned_Weight)
Normalized to 0-100 scale
```

#### Risk Rating Categories

```
LOW RISK (Score: 0-25)
├── Characteristics:
│   ├── Individual in low-risk jurisdiction
│   ├── Clear legitimate business purpose
│   ├── Low-risk industry
│   ├── Consistent transaction patterns
│   └── No adverse indicators
├── CDD Requirements:
│   ├── Basic identity verification
│   ├── Source of funds documentation
│   └── Annual review
└── Monitoring: Quarterly

MEDIUM RISK (Score: 25-50)
├── Characteristics:
│   ├── Medium-risk jurisdiction or industry
│   ├── Some transaction complexity
│   ├── Emerging business relationship
│   └── Normal business indicators
├── CDD Requirements:
│   ├── Enhanced identity verification
│   ├── Source of wealth documentation
│   ├── Business purpose clarity
│   └── Beneficial ownership verification
└── Monitoring: Monthly

HIGH RISK (Score: 50-75)
├── Characteristics:
│   ├── High-risk jurisdiction/industry
│   ├── Complex transaction patterns
│   ├── PEP or high-profile status
│   ├── Substantial cash transactions
│   └── Some adverse indicators
├── CDD Requirements:
│   ├── Enhanced due diligence (EDD)
│   ├── Senior management review
│   ├── Source of funds deep dive
│   ├── Beneficial ownership chains
│   └── Enhanced ongoing monitoring
└── Monitoring: Weekly

VERY HIGH RISK (Score: 75-100)
├── Characteristics:
│   ├── OFAC/high-risk jurisdiction
│   ├── Confirmed adverse indicators
│   ├── High-profile political figure
│   ├── Complex shell structures
│   └── Significant sanctions concerns
├── CDD Requirements:
│   ├── Comprehensive due diligence
│   ├── Source of wealth verification
│   ├── Third-party investigation
│   ├── Board approval required
│   └── Enhanced ongoing monitoring
└── Decision: Likely decline
```

## Beneficial Ownership Risk Assessment

### Ownership Structure Complexity

```
Simple Structures (Low Risk):
├── Individual owner: Direct ownership
├── Sole proprietorship: One person
├── Direct partnership: 2-3 partners
└── Small family business: Family ownership

Moderate Structures (Medium Risk):
├── LLC with institutional investor
├── Partnership with 5-10 partners
├── Multi-level corporate structure (2 levels)
├── Trust with professional trustee
└── Holding company with few subsidiaries

Complex Structures (High Risk):
├── Multiple holding companies (> 3 levels)
├── Shell companies in opaque jurisdictions
├── Bearer shares or non-registered ownership
├── Trusts with multiple beneficiaries
├── International fund structures
├── Pyramid ownership chains
└── Beneficial owner obscured by intermediaries
```

### Red Flags for Beneficial Ownership

```
FLAG 1: Ownership Obscuration
├── Unwillingness to disclose beneficial owners
├── Use of nominees for ownership
├── Use of trusts with undisclosed beneficiaries
├── Bearer shares or similar instruments
└── Ownership chains through opaque jurisdictions

FLAG 2: High-Risk Jurisdictions
├── Delaware LLCs with unknown beneficiary
├── BVI/Cayman Island companies
├── Panamanian shell companies
├── Russian/Chinese holdings
└── Jurisdictions known for weak disclosure

FLAG 3: Suspicious Beneficiary Characteristics
├── Beneficiary is another legal entity
├── Beneficiary refuses direct contact
├── Beneficiary has no operational role
├── Multiple unrelated beneficiaries
└── Beneficiary in sanctioned jurisdiction

FLAG 4: Structural Indicators
├── Excessive number of ownership tiers
├── Regular ownership restructuring
├── Beneficial owner frequently changes
├── Ownership inconsistent with business model
└── Ownership documents are contradictory

FLAG 5: Transaction Mismatch
├── Ownership structure inconsistent with transactions
├── Beneficial owner doesn't direct operations
├── Funds flow inconsistent with ownership
├── Control exercised by non-owner
└── Transactions at odds with stated purpose
```

## Transaction Risk Assessment

### Transaction Attributes

```
RISK FACTORS:

1. Amount vs. Customer Profile
   Score = |Actual_Amount - Expected_Amount| / Expected_Amount
   ├── 0-1: Normal (5 points)
   ├── 1-5: Unusual (25 points)
   ├── 5-10: Very unusual (50 points)
   └── > 10: Extreme outlier (80 points)

2. Frequency Anomaly
   Score = (Actual_Frequency - Baseline) / StDev_Frequency
   ├── Within 1 SD: Normal (5 points)
   ├── 1-2 SD: Unusual (25 points)
   ├── 2-3 SD: Very unusual (50 points)
   └── > 3 SD: Extreme (80 points)

3. Geographic Concentration
   ├── Single country: 10 points
   ├── 2-3 countries: 20 points
   ├── 4-7 countries: 35 points
   ├── > 7 countries: 50 points
   └── If high-risk jurisdiction: +25 points

4. Velocity
   ├── Standard business hours: 5 points
   ├── Off-hours/weekend: 15 points
   ├── Rapid sequence (< 1 hour): 30 points
   ├── Very rapid (< 5 minutes): 60 points
   └── Potential structuring pattern: +40 points

5. Counterparty Risk
   ├── Known business partner: 5 points
   ├── New counterparty: 25 points
   ├── High-risk jurisdiction: 45 points
   ├── Sanctioned/PEP entity: 100 points
   └── Adverse media match: 75 points

6. Transaction Purpose Clarity
   ├── Clear business purpose: 5 points
   ├── Purpose identified: 20 points
   ├── Purpose unclear: 40 points
   ├── Contradictory purpose: 60 points
   └── Obfuscated/circular: 80 points
```

### Transaction Risk Scoring Model

```
Transaction_Risk = Σ(Factor_Weight_i × Factor_Score_i)

Example Weights:
├── Amount & Frequency: 30%
├── Geographic factors: 25%
├── Counterparty risk: 25%
├── Customer profile: 15%
├── Behavioral anomalies: 5%

Alert Thresholds:
├── Score 0-20: Monitor
├── Score 20-50: Review
├── Score 50-75: Investigate
├── Score 75-100: Escalate
```

## ML-Based Risk Scoring

### Feature Engineering

```
Customer Features:
├── Historical transaction count
├── Historical transaction volume
├── Customer tenure
├── Account status changes
├── Document update frequency
├── Regulatory events
├── Geographic concentration
├── Industry concentration
├── Counterparty diversity
└── Periodic reviews

Temporal Features:
├── Days since account opening
├── Days since last transaction
├── Days since risk assessment update
├── Seasonal indicators
├── Regulatory calendar
└── Business cycle indicators

Network Features:
├── Shared counterparties
├── Geographic network
├── Beneficial owner connections
├── Industry peer analysis
└── Transaction flow networks

Behavioral Features:
├── Transaction time patterns
├── Amount distribution
├── Frequency distribution
├── Device fingerprints
├── IP address patterns
├── Geolocation anomalies
└── Device/behavior biometrics
```

### Model Approaches

```
Gradient Boosting (XGBoost/LightGBM):
├── Best for: Classification and ranking
├── Input: Structured features
├── Output: Risk probability (0-1)
├── Advantages:
│   ├── High accuracy
│   ├── Handles non-linear relationships
│   ├── Feature importance ranking
│   └── Fast inference
└── Disadvantage: Less explainable

Neural Networks (Deep Learning):
├── Best for: Complex pattern recognition
├── Input: High-dimensional feature sets
├── Output: Risk probability
├── Architecture:
│   ├── Input layer: Feature embedding
│   ├── Hidden layers: 3-5 layers, dropout regularization
│   ├── Output layer: Sigmoid (binary classification)
│   └── Loss: Binary cross-entropy
└── Advantage: Detects subtle patterns

Isolation Forest (Anomaly Detection):
├── Best for: Outlier detection
├── Input: Unsupervised learning
├── Output: Anomaly score
├── Use cases:
│   ├── Unusual behavior detection
│   ├── New fraud pattern discovery
│   └── Baseline deviation identification
└── Advantage: Works without labeled data

Ensemble Methods:
├── Combine multiple models
├── Voting mechanism
├── Weighted averaging
├── Stacking approaches
└── Better overall performance
```

## Risk Reassessment and Monitoring

### Reassessment Triggers

```
MANDATORY REASSESSMENT:
├── Significant transaction change (> 50% increase)
├── Geographic change (new countries)
├── Ownership/control change
├── Business model change
├── Regulatory event (PEP status change)
├── Adverse media mention
├── Customer request to update information
└── Post-SAR review

PERIODIC REASSESSMENT:
├── Low risk: Annually
├── Medium risk: Semi-annually
├── High risk: Quarterly
├── Very high risk: Ongoing monitoring

AUTOMATED REASSESSMENT:
├── Transaction monitoring
├── Regulatory screening
├── Adverse media alerts
├── Network analysis updates
└── Benchmark comparisons
```

## Risk Reporting and Dashboards

### Key Risk Metrics

```
Portfolio-Level Metrics:
├── % Low risk: Target > 60%
├── % Medium risk: Target 25-35%
├── % High risk: Target < 10%
├── % Very high risk: Target < 2%
├── Risk trend (increasing/decreasing)
├── Geographic risk concentration
└── Industry risk concentration

Performance Metrics:
├── Assessment timeliness: % completed on time
├── SAR generation rate: SARs/1000 customers
├── False positive rate: Alerts requiring manual review
├── Detection rate: % suspicious activity detected
└── Remediation effectiveness: Post-SAR compliance
```

## Best Practices

1. **Dynamic Scoring** - Update risk scores in real-time
2. **Explainability** - Document risk factors and rationale
3. **Regular Validation** - Test models quarterly
4. **False Positive Management** - Minimize alert fatigue
5. **Peer Benchmarking** - Compare performance metrics
6. **Regulatory Alignment** - Follow FATF and local guidance
7. **Documentation** - Maintain complete audit trail
8. **Continuous Improvement** - Refine models based on outcomes
