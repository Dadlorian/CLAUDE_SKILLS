# Claims Processing

## Claims Processing Overview

Claims processing is the core operational function of insurance companies, involving the receipt, investigation, valuation, and settlement of insurance claims. Modern claims systems use automation and analytics to improve speed and accuracy.

## Claims Lifecycle

### 1. First Notice of Loss (FNOL)
**Purpose**: Capture claim information and initiate the process

**Key Activities**:
- Claim initiation: Policyholder reports loss
- Initial data capture: Claim number, policy, loss date, description
- Policy verification: Verify policy is active and covers loss type
- Contact information: Obtain claimant contact details
- Preliminary assessment: Quick determination of coverage
- Claim assignment: Route to appropriate adjuster/handler

**FNOL Channels**:
- **Phone**: Call center representatives
- **Web Portal**: Self-service claim reporting
- **Mobile App**: Smartphone claim submission
- **Email**: Automated email capture
- **Third Parties**: Emergency services, vendors

**FNOL Data**:
```
Claim
├── Claim Number: Unique identifier
├── Policy Number: Associated policy
├── Date of Loss: When incident occurred
├── Report Date: When reported
├── Claimant: Person reporting claim
├── Loss Type: Category of loss
├── Loss Description: Details of incident
├── Loss Amount: Claimed loss amount
├── Status: Initial triage status
└── Assigned To: Handler/adjuster
```

### 2. Investigation Phase
**Purpose**: Verify claim validity and assess damages

**Key Activities**:
- Coverage verification: Confirm coverage for loss type
- Policy review: Check effective dates and exclusions
- Loss investigation: Gather facts about incident
- Damage assessment: Evaluate extent of loss
- Documentation review: Collect supporting documents
- Expert inspection: Property inspection if needed
- Fraud indicators: Assess fraud risk

**Investigation Elements**:
- **Claimant Verification**: Confirm identity and authority
- **Incident Verification**: Confirm loss actually occurred
- **Coverage Verification**: Loss is covered by policy
- **Damage Verification**: Assess actual damage amount
- **Causation**: Confirm proximate cause is covered peril

**Investigation Methods**:
- **Desk Review**: Document analysis
- **Phone Investigation**: Telephone interviews
- **On-Site Inspection**: Physical inspection of damage
- **Medical Records Review**: For health claims
- **Police Reports**: For theft/accident claims
- **Expert Appraisal**: For specialty items

### 3. Assessment Phase
**Purpose**: Determine claim value and coverage

**Key Activities**:
- Coverage analysis: Apply policy terms to loss
- Valuation: Determine claim amount
- Deductible application: Subtract policyholder responsibility
- Limit application: Cap at policy limit
- Comparative negligence: Apply fault percentages if applicable
- Reserve setting: Establish estimated liability

**Valuation Methods**:
- **Replacement Cost**: Cost to replace damaged item
- **Actual Cash Value**: Replacement cost minus depreciation
- **Agreed Value**: Pre-determined value (jewelry, art)
- **Repairable Loss**: Cost to repair rather than replace
- **Medical Billing**: Actual charges or fee schedule

### 4. Adjudication Phase
**Purpose**: Make coverage decision

**Key Activities**:
- Coverage decision: Approve or deny claim
- Partial denial: Approve portion, deny portion
- Conditions: Set conditions for approval
- Documentation: Create adjudication decision document
- Claimant notification: Inform of decision
- Reason documentation: Explain basis for decision

**Adjudication Outcomes**:
- **Approved**: Full coverage, pay approved amount
- **Partial Approval**: Partial coverage or reduced amount
- **Denial**: No coverage due to exclusion or other reason
- **Pending Additional Info**: Awaiting information for decision
- **Referral**: Escalate for special handling

### 5. Settlement Phase
**Purpose**: Pay the claim and close

**Key Activities**:
- Settlement approval: Final authorization to pay
- Payee identification: Determine who to pay
- Settlement method: Check, ACH, credit card
- Payment processing: Execute payment
- Documentation: Create settlement records
- Lien resolution: Pay liens if applicable

**Settlement Options**:
- **Direct Payment to Claimant**: Straight payment
- **Lien Payment**: Pay provider/lienholder directly
- **Structured Settlement**: Payments over time
- **Compromise Settlement**: Settled for less due to dispute

### 6. Closure Phase
**Purpose**: Close claim and capture lessons learned

**Key Activities**:
- Final documentation: Complete all documentation
- Recovery pursuit: Subrogation if applicable
- Salvage: Recover value from damaged items
- Archive: Store for record retention
- Analytics: Capture metrics for reporting
- Litigation resolution: Final legal outcome if applicable

**Closure Actions**:
- **Standard Closure**: Claim fully resolved and paid
- **Denied Closure**: Claim denied and not paid
- **Salvage Closure**: Claim paid with salvage recovery
- **Litigation Closure**: Settled after legal action

## Claims Management System

### CMS Components
- **FNOL Module**: Intake and initial processing
- **Investigation Module**: Evidence gathering and assessment
- **Valuation Module**: Damage appraisal and estimating
- **Adjudication Module**: Coverage decisions
- **Settlement Module**: Payment processing
- **Reporting Module**: Claims analytics
- **Integration Layer**: Connect with policy, payment, accounting

### Key System Features
- **Workflow Management**: Route claims through approval steps
- **Case Management**: Organize information by claim
- **Document Management**: Store all claim documents
- **Collaboration Tools**: Communication between adjusters
- **Audit Trail**: Track all decisions and changes
- **SLA Monitoring**: Track time to resolution

## Claims Types

### Auto Claims
- **Liability Claims**: Bodily injury, property damage from at-fault accidents
- **Collision Claims**: Damage from hitting objects
- **Comprehensive Claims**: Non-collision damage (theft, weather, vandalism)
- **Medical Payment Claims**: Medical expenses regardless of fault
- **Uninsured Motorist**: Injury from uninsured driver

### Home Claims
- **Water Damage**: Burst pipes, flooding, ice dam damage
- **Fire Damage**: Structural fire loss and smoke damage
- **Weather Damage**: Wind, hail, storm damage
- **Theft/Burglary**: Stolen property and break-in damage
- **Liability Claims**: Injury to third parties on property

### Health Claims
- **Inpatient**: Hospital and facility claims
- **Outpatient**: Doctor visits and procedures
- **Pharmacy**: Prescription drug claims
- **Mental Health**: Psychological and behavioral health claims
- **Preventive**: Covered preventive care services

## Claims Automation

### Automated Functions
- **FNOL Intake**: Automated claim intake from digital channels
- **Policy Verification**: Automatic policy lookup and coverage check
- **Claims Triage**: Route to appropriate handler/system
- **Initial Assessment**: Use rules to auto-assess straightforward claims
- **Documentation**: Automated document requests and collection
- **Payments**: Straight-through processing for approved claims
- **Correspondence**: Automated claim status notifications

### Rules Engine for Claims
- **Coverage Rules**: Determine if loss is covered
- **Eligibility Rules**: Check policy requirements
- **Valuation Rules**: Auto-assess damage amounts
- **Payment Rules**: Straight-through processing criteria
- **Escalation Rules**: Route to manual review criteria

### AI/Analytics in Claims
- **Fraud Detection**: Pattern recognition for suspicious claims
- **Predictive Analytics**: Estimate claim resolution time
- **Image Analysis**: Analyze claim photos for damage assessment
- **Natural Language Processing**: Extract information from documents
- **Chatbots**: Answer common claim questions

## Claims Analytics and Reporting

### Key Metrics
- **Average Time to Close**: Days from report to closure
- **Straight-Through Processing Rate**: % of claims processed automatically
- **First Contact Resolution**: % resolved without escalation
- **Customer Satisfaction**: Claims handling satisfaction
- **Fraud Rate**: % of claims with fraud indicators
- **Average Claim Payout**: Mean claim amount
- **Claims Ratio**: Claims paid / premiums earned

### Claims Reporting
- **Claims Trending**: Growth and volume trends
- **Cause Analysis**: Loss causes and frequency
- **Severity Analysis**: Claims by amount and severity
- **Geographic Analysis**: Claims by region
- **Product Performance**: Claims by product line
- **Adjuster Performance**: Metrics by handler

## Regulatory Compliance in Claims

### Claims Handling Standards
- **Prompt Payment**: Pay claims within regulatory timeframes
- **Fair Treatment**: Treat all claimants fairly
- **Clear Communication**: Explain decisions clearly
- **Reasonable Investigation**: Conduct thorough investigations
- **Proper Procedures**: Follow documented procedures

### Documentation Requirements
- **Coverage Decision**: Documented basis for approval/denial
- **Investigation Notes**: Document investigation steps
- **Valuation Support**: Backup for damage estimates
- **Settlement Records**: Record of payment
- **Correspondence**: Keep all communications

### Record Retention
- **Claims Records**: Typically 6+ years
- **Investigation Files**: Typically 6+ years
- **Settlement Records**: Typically 6+ years
- **Litigation Records**: Until litigation resolved

## Digital Claims Management

### Self-Service Claims
- **Online Claim Filing**: Report claims via web portal
- **Mobile Claim Filing**: Report via mobile app
- **Document Upload**: Upload supporting documents
- **Status Tracking**: Track claim progress
- **Communication**: Chat with adjuster
- **Payment Status**: View settlement and payment status

### Real-Time Capabilities
- **Live Chat Support**: Real-time support for claims questions
- **Video Inspection**: Virtual property assessment
- **Digital Documents**: Electronic forms and signatures
- **Mobile Adjusters**: Field adjusters with mobile access
- **Payment Notifications**: Real-time payment alerts
