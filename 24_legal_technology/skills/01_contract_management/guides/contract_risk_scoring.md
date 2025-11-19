# Contract Risk Scoring Guide

## Overview
Risk scoring systematically evaluates contracts to identify potential issues, prioritize management attention, and support decision-making in contract execution and renewal.

## Risk Categories

### Financial Risks
- Unlimited liability exposure
- Unfavorable payment terms
- Currency exposure
- Unindexed pricing
- Cost escalation rates above market
- Minimum commitment obligations

### Operational Risks
- Unclear performance requirements
- Unrealistic timelines
- Resource constraints
- Dependency on third parties
- Continuity and disaster recovery gaps
- Change management limitations

### Legal/Compliance Risks
- Governing law misalignment
- Unilateral amendment rights
- Unfavorable dispute resolution
- Inadequate insurance coverage
- Regulatory non-compliance
- IP infringement risks

### Commercial Risks
- Lock-in duration
- Early termination penalties
- Supplier financial instability
- Market condition changes
- Relationship deterioration risks
- Competitive disadvantage

## Scoring Methodology

### Risk Factor Definition
Each risk factor includes:
- Clear definition
- Scoring scale (1-5)
- Evaluation criteria
- Threshold values
- Weighting factor

### Scoring Scale
- 1: No risk or favorable terms
- 2: Low risk; manageable
- 3: Moderate risk; requires monitoring
- 4: High risk; mitigation required
- 5: Critical risk; escalation required

### Weighting Framework
```
Financial Risk:      35%
Operational Risk:    25%
Legal/Compliance:    25%
Commercial Risk:     15%
```

## Risk Factors to Evaluate

### Key Financial Metrics
| Factor | Weight | Scale |
|--------|--------|-------|
| Liability Cap | High | 1-5 |
| Payment Terms | Medium | 1-5 |
| Price Lock Period | Medium | 1-5 |
| Minimum Commitment | Medium | 1-5 |
| Termination Penalties | High | 1-5 |

### Operational Factors
| Factor | Weight | Scale |
|--------|--------|-------|
| SLA Clarity | High | 1-5 |
| Performance Metrics | Medium | 1-5 |
| Escalation Rights | Medium | 1-5 |
| Change Management | Medium | 1-5 |
| Continuity Provisions | High | 1-5 |

### Legal Factors
| Factor | Weight | Scale |
|--------|--------|-------|
| IP Ownership | High | 1-5 |
| Data Security | High | 1-5 |
| Insurance Coverage | High | 1-5 |
| Compliance Requirements | High | 1-5 |
| Dispute Resolution | Medium | 1-5 |

## Risk Scoring Formula

### Overall Risk Score
```
Risk Score = (Financial_Score × 0.35) +
             (Operational_Score × 0.25) +
             (Legal_Score × 0.25) +
             (Commercial_Score × 0.15)

Range: 1-5
- 1.0-1.9: Green (Low Risk)
- 2.0-2.9: Yellow (Moderate Risk)
- 3.0-3.9: Orange (High Risk)
- 4.0-5.0: Red (Critical Risk)
```

## Implementation Process

### Step 1: Clause Extraction
- Identify relevant clauses
- Extract key provisions
- Normalize language variations
- Categorize by risk type

### Step 2: Assessment
- Evaluate each risk factor
- Assign scores based on criteria
- Document rationale
- Flag outliers

### Step 3: Scoring
- Calculate component scores
- Compute overall risk score
- Identify primary risk drivers
- Determine risk color

### Step 4: Review and Action
- Legal review of scoring
- Business review and discussion
- Risk mitigation planning
- Action item tracking

## Remediation Strategies

### Green (1.0-1.9)
- Standard terms acceptable
- Routine contract management
- Regular monitoring
- No special action required

### Yellow (2.0-2.9)
- Review and consider mitigation
- Identify specific high-risk clauses
- Negotiate improvements if possible
- Enhanced monitoring

### Orange (3.0-3.9)
- Significant risk management required
- Executive review required
- Risk mitigation negotiation essential
- Close monitoring and reporting

### Red (4.0-5.0)
- Executive decision required
- Major risk mitigation or rejection
- Legal review mandatory
- Only proceed with executive approval

## Continuous Improvement

### Model Refinement
- Collect historical data
- Analyze prediction accuracy
- Adjust weighting factors
- Update risk criteria
- Regular model validation

### Benchmarking
- Compare scores across contracts
- Identify trends
- Assess risk tolerance
- Share insights across organization
- Build institutional knowledge

## Technology and Automation
- ML models for clause classification
- Automated score calculation
- Dashboard reporting
- Trend analysis
- Alert generation for high-risk contracts
