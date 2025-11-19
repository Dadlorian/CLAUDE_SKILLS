# Underwriting

## Underwriting Overview

Underwriting is the process of evaluating insurance risk, determining whether to accept it, and setting appropriate premium rates. Modern underwriting combines traditional expert judgment with data analytics and automation.

## Underwriting Process

### 1. Risk Evaluation
**Purpose**: Assess the risk characteristics of the applicant and subject matter

**Key Activities**:
- Information gathering: Collect applicant and risk information
- Risk classification: Determine risk category/class
- Risk comparison: Compare to expected risk profiles
- Model evaluation: Apply predictive models
- Expert judgment: Underwriter assessment

**Risk Information by Type**:

**Auto Insurance Risk Factors**:
- Driver age and experience
- Driving record (accidents, violations)
- Vehicle type and safety features
- Vehicle use (commute vs leisure)
- Annual mileage
- Coverage limits requested

**Home Insurance Risk Factors**:
- Property age and construction
- Square footage and configuration
- Fire protection systems
- Alarm systems
- Distance from fire station
- Claim history

**Health Insurance Risk Factors**:
- Age and gender
- Medical history
- Current medications
- Lifestyle (smoking, alcohol)
- Family medical history
- Pre-existing conditions

### 2. Risk Classification
**Purpose**: Assign risk to appropriate underwriting class

**Classification Approaches**:
- **Class Rating**: Broad categories (Standard, Preferred, Non-standard)
- **Score-Based**: Quantitative risk score
- **Parametric**: Multiple rating factors
- **Behavioral**: Risk based on behavior indicators

**Risk Classes**:
```
Auto Insurance
├── Preferred: Excellent driver, clean record, good vehicle
├── Standard: Good driver, minor incidents, standard vehicle
└── Non-standard: Poor driver, multiple incidents, high risk

Home Insurance
├── Preferred: New construction, excellent maintenance
├── Standard: Well-maintained older home
└── Non-standard: Poor condition, high loss history
```

### 3. Rating and Pricing
**Purpose**: Determine appropriate premium for the risk

**Rating Factors**:
- **Base Rate**: Starting rate for risk class
- **Rating Adjustments**: Percentage adjustments for factors
- **Surcharges**: Additional charges for poor history
- **Discounts**: Reductions for positive factors
- **Territory**: Geographic rating adjustments

**Rating Formula**:
```
Premium = Base Rate × Adjustment 1 × Adjustment 2 × ... × (1 + Surcharge) × (1 - Discount)
```

**Common Discounts**:
- **Multi-policy**: Bundle discounts
- **Loss-free**: No claims in period
- **Safety Features**: Anti-theft, fire suppression
- **Protective Devices**: Alarm systems
- **Occupational**: Employment-based discounts
- **Group**: Membership-based discounts

### 4. Acceptance Decision
**Purpose**: Approve or decline the risk

**Underwriting Decisions**:
- **Standard Acceptance**: Accept at standard rate
- **Substandard Acceptance**: Accept at increased rate
- **Conditional Acceptance**: Accept with conditions
- **Decline**: Reject the application
- **Refer**: Escalate to senior underwriter

**Acceptance Conditions**:
- Additional information required
- Risk modification required (e.g., home repair)
- Increased deductible
- Coverage limitations
- Premium adjustment pending verification

## Automated Underwriting

### Rules-Based Underwriting
- **Decision Trees**: Yes/no decision logic
- **Scoring Models**: Quantitative risk assessment
- **Rate Tables**: Lookup table for rates
- **Validation Rules**: Check for consistency
- **Coverage Rules**: Ensure valid coverage combinations

### Straight-Through Processing (STP)
**Automated Approval Workflow**:
- Receive application
- Verify information
- Apply business rules
- Check against policy guidelines
- Generate approval/decline
- Create policy documents
- No manual intervention required

**STP Rates**:
- 70-80%: Favorable risk profiles
- 90%+: Simple products with good data

### Predictive Analytics
- **Credit Scoring**: Predict likelihood of loss
- **Churn Prediction**: Identify likely cancellations
- **Loss Prediction**: Estimate expected loss severity
- **Fraud Propensity**: Assess fraud likelihood
- **Claims Prediction**: Predict future claims

## Underwriting Guidelines

### Guidelines Document
Comprehensive document defining:
- **Underwriting Philosophy**: Risk appetite and strategy
- **Appetite Guidelines**: Acceptable vs unacceptable risks
- **Rating Guidelines**: How to apply rates
- **Underwriting Authority**: Decision authority levels
- **Exception Handling**: How to handle exceptions

### Authority Levels
```
Individual Underwriter: $0 - $500,000
Senior Underwriter: $500,000 - $2,000,000
Underwriting Manager: $2,000,000 - $10,000,000
VP Underwriting: $10,000,000+
```

### Guideline Updates
- **Annual Review**: Update based on loss experience
- **Market Changes**: Adjust for competitive dynamics
- **Product Changes**: Update for new products
- **Regulatory Changes**: Comply with regulations
- **Data Insights**: Incorporate analytics findings

## Risk Selection

### Risk Appetite
**Definition**: Total amount and type of risk willing to accept

**Risk Appetite Dimensions**:
- **Premium Volume**: Total premium to accept
- **Geographic**: Acceptable territories
- **Product Mix**: Mix of products to write
- **Customer Segment**: Target customer types
- **Risk Classes**: Accept standard vs non-standard

### Retention and Reinsurance
- **Net Retention**: Amount insurer keeps after reinsurance
- **Ceded Premium**: Premium transferred to reinsurer
- **Excess of Loss**: Reinsurance above certain amount
- **Proportional**: Share percentage with reinsurer

## Underwriting Metrics

### Performance Metrics
- **Issue Rate**: Percentage of applications approved
- **Decline Rate**: Percentage of applications denied
- **Average Premium**: Mean premium by segment
- **Loss Ratio**: Claims paid / premium earned
- **Combined Ratio**: (Claims + Expenses) / Premium
- **Retention Rate**: Renewal rate by segment

### Quality Metrics
- **Underwriting Quality**: Loss ratio by underwriter
- **Decision Consistency**: Consistency of decisions
- **Turn-Around Time**: Time to underwriting decision
- **Error Rate**: Percentage of incorrect decisions

## Regulatory Aspects of Underwriting

### Fair Lending and Discrimination
- **Non-discrimination**: Cannot discriminate on protected classes
- **Fair Assessment**: Must use consistent, non-discriminatory criteria
- **Geographic Redlining**: Cannot deny based solely on location
- **Transparency**: Must explain underwriting decisions

### Underwriting Records
- **Application Records**: Retain all applications
- **Underwriting Notes**: Document underwriting decisions
- **Rating Documentation**: Backup for rating decisions
- **Decline Letters**: Document reasons for decline
- **Retention**: Typically 6+ years

### Required Disclosures
- **Adverse Action Notice**: Explanation for decline or worse terms
- **Right to Explain**: Allow customer to dispute information
- **Information Correction**: Allow customer to correct data
- **Privacy Notice**: Explain data usage

## Advanced Underwriting Techniques

### Behavioral Underwriting
- **Social Media Analysis**: Review public social media
- **Telematics Data**: Vehicle driving behavior data
- **Health Wearables**: Physical activity data
- **Transaction Analysis**: Spending patterns
- **Mobile Behavior**: App usage patterns

### Usage-Based Insurance (UBI)
- **Device Monitoring**: Track user behavior
- **Real-time Adjustment**: Dynamic pricing based on behavior
- **Incentive Programs**: Rewards for good behavior
- **Risk Reduction**: Lower risk through behavior modification

### Alternative Data
- **Alternative Credit**: Non-traditional credit assessment
- **Utility Payment History**: Payment behavior indicator
- **Rent Payment**: Payment history indicator
- **Employment Data**: Income verification
- **Education**: Educational attainment indicator

## Underwriting by Product

### Auto Insurance Underwriting
- **Driving Record**: Most significant factor
- **Vehicle Type**: Safety and theft risk
- **Usage**: Business vs personal use
- **Claims History**: Prior loss experience
- **Coverage Limits**: Requested limits

### Home Insurance Underwriting
- **Property Condition**: Age, maintenance, construction
- **Fire Protection**: Proximity to fire station
- **Security**: Alarm systems
- **Claims History**: Prior home claims
- **Occupancy**: Owner-occupied vs investment

### Health Insurance Underwriting
- **Medical Underwriting**: Review of medical history
- **Guaranteed Issue**: Must accept regardless of health
- **Pre-existing Conditions**: Restrictions on coverage
- **Waiting Periods**: Time before coverage begins
- **Exclusions**: Specific conditions excluded
