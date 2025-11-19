# Operational Risk Framework

## Definition & Scope
Operational risk is the risk of loss resulting from inadequate or failed internal processes, people, systems, or external events. It includes legal and regulatory risk, but excludes strategic and reputational risk (though these can be consequences).

## Operational Risk Categories

### Basel III Classification (7 Loss Event Types)

#### 1. Internal Fraud
Losses from acts of deception, embezzlement, or unauthorized activity by internal staff.

**Examples**:
- Employee theft of funds or securities
- Unauthorized trading (Barings, Société Générale)
- Falsification of records
- Embezzlement by finance department
- IT system sabotage by disgruntled employee

**Frequency**: Low (few events)
**Severity**: High (can be very large)
**Mitigation**: Segregation of duties, monitoring, background checks, employee hotlines

#### 2. External Fraud
Losses from fraud or dishonesty by external third parties.

**Examples**:
- Check fraud, forged documents
- Cyber theft, account takeover
- Vendor fraud
- Insurance fraud
- Card fraud

**Frequency**: High (many events)
**Severity**: Medium to high
**Mitigation**: Authentication controls, encryption, fraud detection, vendor management

#### 3. Employment Practices & Workplace Safety
Losses from violation of employment laws or workplace safety regulations.

**Examples**:
- Discrimination lawsuits
- Wrongful termination
- Workplace injuries
- Sexual harassment settlements
- Failed background checks causing injury

**Frequency**: Medium
**Severity**: Medium
**Mitigation**: HR policies, training, workplace safety programs, legal compliance

#### 4. Clients, Products & Business Practices
Losses from unintentional or negligent failure to meet client needs.

**Examples**:
- Inadequate disclosure (misselling)
- Product design flaws
- Breach of trust or fiduciary duty
- Suitability violations
- Account errors affecting client

**Frequency**: High
**Severity**: Medium
**Mitigation**: Product testing, client suitability assessment, compliance monitoring

#### 5. Damage to Physical Assets
Losses from external events damaging physical assets.

**Examples**:
- Natural disasters (floods, earthquakes, hurricanes)
- Fires
- Terrorism
- Vandalism
- Accidents

**Frequency**: Low to medium
**Severity**: High
**Mitigation**: Insurance, disaster recovery, business continuity planning

#### 6. Business Disruption & Systems Failures
Losses from systems unavailability or service disruption.

**Examples**:
- Data center outage
- Network failure
- Software bugs causing trading halt
- Cyber attack
- Pandemic disruption

**Frequency**: Low to medium
**Severity**: Very high
**Mitigation**: Redundant systems, disaster recovery, backup sites, testing

#### 7. Execution, Delivery & Process Management
Losses from failure to properly execute processes or deliver commitments.

**Examples**:
- Failed settlement
- Data entry errors
- Reconciliation errors
- Operational failure in trade execution
- Failed clearance/settlement

**Frequency**: Medium to high
**Severity**: Medium
**Mitigation**: Process automation, controls, quality assurance, reconciliation

## Operational Risk Assessment

### Risk & Control Self-Assessment (RCSA)

**Process**:
1. Identify key processes and activities
2. Identify risks within each process
3. Assess inherent risk (without controls)
4. Identify and assess control effectiveness
5. Calculate residual risk (after controls)
6. Develop mitigation plans for high residual risks

**Risk Rating**: Frequency × Severity
- Frequency: 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost certain
- Severity: 1=Minimal, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic
- Risk = Frequency × Severity (1-25 scale)

### Loss Event Data Collection

**Objectives**:
- Track actual loss events
- Identify patterns and trends
- Calculate loss distribution
- Estimate tail losses
- Allocate capital

**Data Requirements**:
- Event date
- Loss amount
- Loss type (one of 7 categories above)
- Process/activity affected
- Root cause
- Contributing factors
- Preventive/corrective actions

**Data Quality**:
- Completeness: Capture all significant events
- Accuracy: Correct amounts, classification
- Timeliness: Recorded promptly
- Governance: Clear definitions and accountabilities

### Key Risk Indicators (KRIs)

**Purpose**: Early warning signals of elevated operational risk.

**Examples**:
- **Staffing**: Staff turnover rate, open positions, training hours
- **Systems**: System uptime %, unresolved incidents, change failures
- **Processes**: Process cycle time, error rate, rework %
- **Compliance**: Exceptions to control, audit findings, regulatory violations
- **Fraud**: Unusual transaction alerts, investigation count
- **Operational**: Customer complaints, failed trades, late settlements

**Governance**:
- KRI owner defined for each indicator
- Thresholds set (green, yellow, red)
- Monthly monitoring and reporting
- Escalation if yellow/red

## Operational Risk Mitigation

### Risk Avoidance
Decide not to engage in activity due to unacceptable operational risk.

**Examples**:
- Refusing to do business in certain high-risk jurisdictions
- Not offering certain complex products with compliance risk
- Declining high-risk client types

### Risk Reduction

#### Process Improvements
- **Automation**: Reduce manual errors
- **Standardization**: Use consistent processes across locations
- **Documentation**: Clear procedures and training
- **Segregation of Duties**: Prevent fraud, increase accountability

#### System Enhancements
- **Monitoring**: Real-time alerts for anomalies
- **Controls**: Automated controls in systems
- **Redundancy**: Backup systems for critical functions
- **Disaster Recovery**: Tested plans for system failures

#### Training & Competency
- **Mandatory Training**: Compliance, risk awareness, product training
- **Competency Assessment**: Ensure staff capability
- **Succession Planning**: Retain key personnel
- **Management Review**: Evaluate people performance

#### Governance & Controls
- **Policies**: Clear risk policies and procedures
- **Oversight**: Board/management committees
- **Compliance**: Regular audits, testing
- **Whistleblower Programs**: Confidential reporting channels

### Risk Mitigation (Insurance)
Transfer operational risk to insurance companies.

**Types of Coverage**:
- **Professional Indemnity**: Covers professional errors/omissions
- **Cyber Insurance**: Covers cyber attacks, data breaches
- **Directors & Officers (D&O)**: Covers liability of board/executives
- **Employment Practices Liability (EPL)**: Covers employment-related claims
- **Crime Insurance**: Covers theft, embezzlement, fraud

**Limitations**:
- Insurance has exclusions, deductibles, limits
- Not all operational risks insurable
- May not cover catastrophic events
- Insurance cost can be significant

## Operational Risk Capital

### Standardized Approach (Basel III)
Regulatory capital based on gross income by business line.

**Capital Charge = Σ(Gross Income × Beta by business line)**

**Business Lines & Betas**:
- Corporate Finance: 18%
- Trading & Sales: 18%
- Retail Banking: 12%
- Commercial Banking: 15%
- Payment & Settlement: 18%
- Agency Services: 15%
- Asset Management: 12%

**Example**:
- Trading & Sales gross income: $100M
- Beta: 18%
- Capital charge: $100M × 18% = $18M

### Advanced Measurement Approach (AMA)
Banks use internal loss data and models to calculate capital.

**Components**:
- **Internal Loss Data**: Historical losses (typically 5+ years)
- **External Data**: Industry loss database, consortium data
- **Scenario Analysis**: Expert assessment of potential scenarios
- **Business Environment & Internal Control Factors (BEICF)**:
  - Risk factors: How environment affects risk
  - Control factors: How controls mitigate risk

**Capital Formula**:
Typically uses extreme value theory to estimate 99.9% confidence level loss.

K = Σ(EPij) where EPij = empirical probability of loss at (i, j) event type/loss size

## Operational Risk Governance

### Board & Management Oversight
- Board Risk Committee: Oversees operational risk framework
- Chief Risk Officer: Senior executive responsible
- Operational Risk Committee: Reviews policies, loss events, KRIs
- Business Unit Risk Owners: Responsible for their area

### Operational Risk Framework
- Policy: Operational risk policy approved by board
- Limits: Risk appetite, concentration limits
- Monitoring: KRIs, loss events, controls
- Reporting: Monthly/quarterly to board
- Escalation: Clear procedures for material events

### Model Risk Management
- **Model Governance**: Approval, periodic review
- **Model Validation**: Independent testing
- **Model Monitoring**: Track model performance
- **Model Documentation**: Clear documentation of methodology
- **Limits on Model Risk**: Capital charge for model uncertainty

## Emerging Operational Risks

### Cyber Risk
- Increasing frequency and severity
- Potential for large-scale losses (2020 SolarWinds: billions in risk)
- Regulatory focus (NYDFS, SEC, BoE)

### Third-Party Risk
- Outsourcing increases dependence on vendors
- Single point of failure (cloud providers, payment processors)
- Vendor due diligence and monitoring critical

### Conduct Risk
- Regulatory focus post-2008 crisis
- Employee misconduct (LIBOR, FX fixing, misselling)
- Significant fines and reputational damage

### Model Risk
- Complex models in credit, market risk, AML
- Model uncertainty and parameter risk
- Validation and monitoring essential

### Regulatory/Compliance Risk
- Increasing regulation globally
- Complex rules (GDPR, MiFID II, Dodd-Frank)
- Non-compliance can result in significant fines
