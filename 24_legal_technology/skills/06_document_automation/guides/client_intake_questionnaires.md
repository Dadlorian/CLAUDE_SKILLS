# Client Intake Questionnaires: Designing Effective Data Collection Interviews

## Executive Summary

Client intake questionnaires form the critical interface between clients and automated legal document systems. This guide covers the design, implementation, and optimization of intake questionnaires using HotDocs interview technology and Contract Express data collection interfaces. Effective questionnaires balance completeness with usability, ensuring accurate data collection while maintaining a positive user experience.

## Table of Contents

1. [Questionnaire Design Principles](#questionnaire-design-principles)
2. [User Experience and Navigation](#user-experience-and-navigation)
3. [Question Design and Phrasing](#question-design-and-phrasing)
4. [Question Types and Selection](#question-types-and-selection)
5. [Conditional Navigation Logic](#conditional-navigation-logic)
6. [Data Validation and Accuracy](#data-validation-and-accuracy)
7. [Progressive Disclosure](#progressive-disclosure)
8. [Accessibility and Usability](#accessibility-and-usability)
9. [Integration with Document Generation](#integration-with-document-generation)
10. [Testing and Optimization](#testing-and-optimization)

---

## Questionnaire Design Principles

### Core Objectives

A well-designed intake questionnaire should:

1. **Collect Necessary Data**: Gather all information required to generate accurate documents
2. **Minimize User Burden**: Ask only essential questions; avoid redundancy
3. **Ensure Accuracy**: Collect precise, valid data through validation and guidance
4. **Provide Clarity**: Use plain language and helpful guidance
5. **Maintain Engagement**: Keep users motivated to complete the process
6. **Respect User Time**: Minimize completion time without sacrificing quality
7. **Handle Complexity**: Address complex scenarios without overwhelming users

### Information Architecture

Organize questions logically:

**Hierarchical Structure**:
```
Intake Questionnaire
├── Party Information
│   ├── Primary Party
│   ├── Secondary Parties
│   └── Contact Information
├── Transaction Details
│   ├── Basic Transaction Info
│   ├── Financial Terms
│   └── Special Conditions
├── Legal Requirements
│   ├── Compliance Needs
│   ├── Jurisdiction Info
│   └── Special Clauses
└── Document Preferences
    ├── Output Options
    ├── Additional Exhibits
    └── Delivery Preferences
```

### Question Prioritization

Determine which information is:

- **Essential**: Must be collected; document cannot be generated without it
- **Important**: Significantly affects document content but has reasonable defaults
- **Optional**: Nice-to-have information that enhances but isn't required
- **Derivable**: Can be calculated from other fields

Place essential questions early, optional questions later.

---

## User Experience and Navigation

### Interview Flow Design

#### Linear vs. Branching Flow

**Linear Flow**: All users answer similar questions in sequence
- Pros: Simple, consistent, predictable
- Cons: May require irrelevant questions for some users

**Branching Flow**: Questions vary based on previous answers
- Pros: Tailored to user situation, efficient
- Cons: More complex, harder to explain

**Hybrid Approach**: Generally recommended
- Core questions required for all users
- Conditional sections for specific scenarios
- Optional sections for advanced users

#### Page Breaks and Sections

Organize questions into logical pages:

```
Page 1: Welcome and Overview
- Brief explanation of questionnaire purpose
- Estimated completion time
- Required vs. optional fields indicator

Page 2: Party Information (Required)
- Client name and address
- Client entity type
- Contact information

Page 3: Counterparty Information (Required)
- Other party details
- Relationship type
- Contact information

Page 4: Transaction Details (Required)
- Transaction type
- Transaction amount
- Effective date

Page 5: Legal Terms (Conditional)
[Appears only if certain conditions met]

Page 6: Additional Options (Optional)
- Advanced customization
- Exhibit selection
- Special provisions
```

### Navigation Elements

#### Progress Indicators

Show users where they are in the process:

```
Step 1 of 5: Party Information  [CURRENT]
Step 2 of 5: Transaction Details
Step 3 of 5: Legal Terms
Step 4 of 5: Special Conditions
Step 5 of 5: Review and Confirm
```

#### Help and Guidance

Provide context for complex questions:

```
Question: "What is the contract value?"

Help Text: "Enter the total monetary value of this contract. If the contract 
includes non-monetary benefits, estimate their fair market value."

Examples:
- Service contract with $50,000 annual cost
- License agreement with $100,000 upfront plus $25,000 annual renewal
```

#### Back and Next Navigation

Allow flexible movement through questionnaire:

- Back button: Return to previous page and modify answers
- Next button: Move forward after validation
- Save: Allow users to save progress and resume later
- Summary: Review all answers before finalizing

---

## Question Design and Phrasing

### Effective Question Characteristics

#### Clarity

- Use simple, plain language
- Avoid legal jargon when possible
- Define technical terms when necessary
- Use active voice

**Poor**: "What is the organizational status vis-à-vis regulatory compliance?"
**Good**: "Is your company registered with the SEC?"

#### Specificity

- Ask one concept per question
- Avoid double questions
- Be concrete and precise

**Poor**: "What are the client's business activities and revenue?"
**Good**: 
- "What is your primary business activity?" 
- "What was last year's annual revenue?"

#### Appropriateness

- Ask only relevant questions
- Use conditional logic to hide irrelevant questions
- Avoid assumptions about user knowledge

**Poor**: "What is the client's accounts receivable turnover ratio?" 
**Good** (only for financial institutions): "Do you need to track receivables aging?"

#### Neutrality

- Avoid biasing language
- Don't suggest preferred answers
- Remain objective

**Biased**: "Do you want to limit your significant liability exposure?"
**Neutral**: "Should this agreement include liability limitations?"

### Question Structure

#### Open-Ended Questions

Use for flexible responses:

```
Question: "Please describe the nature of the services to be provided."
Question: "Explain any special requirements or conditions."
Question: "Are there other terms you'd like included?"
```

Use when:
- Response format is unpredictable
- User expertise suggests open response
- Capturing nuance is important

Avoid when:
- Question is part of calculation
- Response must be standardized
- Conditional logic depends on specific values

#### Structured Questions

Use for consistent, comparable responses:

```
Question: "What is the contract amount?"
Type: Number field
Validation: Must be positive number

Question: "Select the payment method:"
Type: Multiple choice
Options: 
  - Credit Card
  - Wire Transfer
  - ACH
  - Check
```

Use when:
- Specific value needed
- Conditional logic depends on answer
- Value is used in calculations
- Comparison across documents needed

---

## Question Types and Selection

### HotDocs Question Types

#### Text Questions

Collect open-ended text:

```hotdocs
Question "What is the client's full legal name?" as "ClientName"

Question "Please describe the property location:" as "PropertyDescription"
    Hint "Include street address, city, state, zip code"
```

#### Number Questions

Collect numeric values:

```hotdocs
Question "What is the contract amount (in dollars)?" as "ContractAmount"
    Type: Number
    Default: 0
    Minimum: 0
    Maximum: 10000000

Question "What percentage of revenue should be allocated to reserves?" as "ReservePercentage"
    Type: Number with decimals
    Default: 10
    Minimum: 0
    Maximum: 100
```

#### Date Questions

Collect calendar dates:

```hotdocs
Question "What is the contract start date?" as "StartDate"
    Type: Date
    Default: Today
    
Question "What is the contract end date?" as "EndDate"
    Type: Date
    Default: One year from start date
```

#### True/False Questions

Collect binary decisions:

```hotdocs
Question "Should the agreement include a non-compete clause?" as "IncludeNonCompete"
    Type: True/False
    Default: True
```

#### Multiple Choice Questions

Present predefined options:

```hotdocs
Question "What type of legal entity is the client?" as "EntityType"
    Type: Multiple Choice (select one)
    Options:
        - Individual
        - Sole Proprietor
        - Partnership
        - Limited Liability Company (LLC)
        - Corporation
        - Non-Profit Organization

Question "Select all services that should be included:" as "ServicesIncluded"
    Type: Multiple Choice (select multiple)
    Options:
        - Consulting
        - Training
        - Implementation
        - Support
        - Maintenance
```

### Contract Express Data Elements

#### Element Definition

```
Data Element: ClientName
Type: Text
Length: Maximum 255 characters
Required: Yes
Default Value: [blank]
Help Text: "Enter the full legal name of the client organization"

Data Element: ContractAmount
Type: Number
Format: Currency
Required: Yes
Minimum: 0
Maximum: 99,999,999
Default Value: 0
Help Text: "Enter the total contract value in US dollars"

Data Element: EffectiveDate
Type: Date
Required: Yes
Default Value: Today
Help Text: "Select the date this contract becomes effective"

Data Element: EntityType
Type: Selection
Required: Yes
Options: Individual, Corporation, LLC, Partnership, Non-Profit
Default Value: Corporation
Help Text: "Select the legal structure of the organization"
```

#### Validation Rules

```
RULE RequireAmountForCommercialContracts WHEN ContractType = "Commercial" THEN
    REQUIRE ContractAmount to be specified
END

RULE ValidateDateSequence WHEN StartDate >= EndDate THEN
    VALIDATION ERROR "End date must be after start date"
END

RULE RequireCorporateApproval WHEN EntityType = "Corporation" AND Amount > 100000 THEN
    REQUIRE ApprovalLevel = "Executive"
END
```

---

## Conditional Navigation Logic

### Showing and Hiding Questions

#### Entity Type Branching

```hotdocs
Question "What type of entity is the client?" as "EntityType"
    Options: Individual, Corporation, LLC, Partnership

IF EntityType = "Corporation" THEN
    Question "Has the Board authorized this agreement?" as "BoardAuthorization"
    Question "What is the name of the Registered Agent?" as "RegisteredAgentName"
    Show Page "Corporate Authorization"
END IF

IF EntityType = "LLC" THEN
    Question "How many members does the LLC have?" as "NumberOfMembers"
    Question "Do you have an operating agreement?" as "HasOperatingAgreement"
    Show Page "LLC Authorization"
END IF

IF EntityType = "Individual" THEN
    Question "Is this person married?" as "IsMarried"
    IF IsMarried = TRUE THEN
        Question "Does spouse consent to this agreement?" as "SpouseConsent"
    END IF
END IF
```

#### Transaction Type Branching

```hotdocs
Question "What type of transaction is this?" as "TransactionType"
    Options: Purchase, Lease, License, Service Agreement, Loan

IF TransactionType = "Purchase" THEN
    Question "What is the purchase price?" as "PurchasePrice"
    Question "What is the down payment?" as "DownPayment"
    Question "Who is responsible for closing costs?" as "ClosingCostResponsibility"
    Show Page "Purchase Terms"
END IF

IF TransactionType = "Lease" THEN
    Question "What is the monthly lease amount?" as "MonthlyLease"
    Question "What is the lease term (in months)?" as "LeaseTerm"
    Question "Does the lease include renewal options?" as "IncludeRenewalOptions"
    Show Page "Lease Terms"
END IF

IF TransactionType = "License" THEN
    Question "What are the licensed rights?" as "LicensedRights"
    Question "Can the license be sublicensed?" as "AllowSublicense"
    Show Page "License Terms"
END IF
```

#### Amount-Based Branching

```hotdocs
Question "What is the contract amount?" as "ContractAmount"

IF ContractAmount < 50000 THEN
    Question "Who approved this smaller contract?" as "ApproverSmall"
ELSE IF ContractAmount < 250000 THEN
    Question "What is the name of the department manager approving this?" as "ApproverManager"
    Question "What is the cost center code?" as "CostCenterCode"
ELSE
    Question "What is the name of the executive approving this?" as "ApproverExecutive"
    Question "Has this been reviewed by legal?" as "LegalReview"
    Question "Is Board approval required?" as "BoardApprovalRequired"
END IF
```

### Conditional Defaults

Set default values based on previous answers:

```hotdocs
Question "What is the contract start date?" as "StartDate"

IF StartDate is blank THEN
    Set StartDate = Today
END IF

Question "What is the contract end date?" as "EndDate"

IF EndDate is blank THEN
    IF ContractLength = "1 Year" THEN
        Set EndDate = StartDate + 12 months
    ELSE IF ContractLength = "2 Years" THEN
        Set EndDate = StartDate + 24 months
    ELSE IF ContractLength = "3 Years" THEN
        Set EndDate = StartDate + 36 months
    END IF
END IF
```

---

## Data Validation and Accuracy

### Field-Level Validation

#### Required Fields

Mark fields as required and prevent progression without completion:

```hotdocs
Question "Client name:" as "ClientName"
    Required: Yes
    Error Message: "You must enter the client's legal name to proceed"

Question "Contract amount:" as "ContractAmount"
    Required: Yes
    Error Message: "Please enter the contract amount"
```

#### Format Validation

Ensure data matches expected format:

```hotdocs
Question "Email address:" as "ClientEmail"
    Validation: Must contain @ and valid domain
    Error Message: "Please enter a valid email address (e.g., name@company.com)"

Question "Phone number:" as "ClientPhone"
    Format: (XXX) XXX-XXXX
    Validation: Must be 10 digits
    Error Message: "Please enter a valid US phone number"

Question "Zip code:" as "ClientZipCode"
    Validation: Must be 5 digits
    Error Message: "Please enter a valid 5-digit zip code"
```

#### Range Validation

Ensure numeric values fall within acceptable ranges:

```hotdocs
Question "Annual revenue (in millions):" as "AnnualRevenue"
    Minimum: 0
    Maximum: 100000
    Error Message: "Please enter revenue between 0 and $100 billion"

Question "Interest rate (percent):" as "InterestRate"
    Minimum: 0
    Maximum: 50
    Error Message: "Please enter an interest rate between 0% and 50%"
```

#### Comparative Validation

Validate relationships between fields:

```hotdocs
Question "Contract start date:" as "StartDate"
Question "Contract end date:" as "EndDate"

IF EndDate <= StartDate THEN
    Error: "End date must be at least one day after start date"
END IF

Question "Down payment (dollars):" as "DownPayment"
Question "Purchase price (dollars):" as "PurchasePrice"

IF DownPayment > PurchasePrice THEN
    Error: "Down payment cannot exceed purchase price"
END IF
```

### Data Quality Checks

#### Completeness Checks

```hotdocs
/* Ensure all required party information is provided */
IF ClientName = "" OR ClientAddress = "" OR ClientCity = "" THEN
    Warning: "Complete client information is required before proceeding"
END IF

/* Ensure financial information is consistent */
IF TransactionAmount = 0 THEN
    Recommend: "Please enter a transaction amount for accurate document generation"
END IF
```

#### Consistency Checks

```hotdocs
/* Cross-field validation */
IF EntityType = "Individual" AND NumberOfMembers > 0 THEN
    Warning: "Individuals cannot have members. Did you mean to select LLC or Partnership?"
END IF

IF ContractType = "License" AND IncludeOwnershipTransfer = TRUE THEN
    Warning: "License agreements typically don't transfer ownership. Confirm this is correct."
END IF
```

#### Reasonableness Checks

```hotdocs
IF AnnualRevenue < 10000 AND RequestedLoanAmount > 1000000 THEN
    Warning: "Loan amount appears large relative to stated revenue. Please verify."
END IF

IF ContractAmount > 100000000 THEN
    Warning: "Contract amount exceeds $100M. Please confirm this is correct."
END IF
```

---

## Progressive Disclosure

### Layered Questionnaires

Start with basic questions, then reveal more based on complexity:

```
Level 1: Core Questions
- Party information
- Basic transaction details
- Effective date

Level 2: Transaction-Specific (Revealed if needed)
- Amount-specific terms
- Type-specific conditions
- Jurisdiction-specific language

Level 3: Advanced Options (Optional)
- Custom calculations
- Special provisions
- Specialized clauses
```

### Expandable Sections

Allow users to reveal additional options:

```
─ BASIC CONTRACT TERMS
  [Expanded] - Show core terms

OPTIONAL PROVISIONS
  [Collapsed]
  ├─ Warranties
  ├─ Indemnification
  ├─ Limitation of Liability
  └─ Insurance Requirements

ADVANCED OPTIONS
  [Collapsed]
  ├─ Force Majeure
  ├─ Assignment Restrictions
  ├─ Amendment Procedures
  └─ Dispute Resolution Methods
```

### Conditional Complexity

Increase complexity based on user experience or transaction size:

```hotdocs
Question "Is this your first contract using this system?" as "FirstTimeUser"

IF FirstTimeUser = TRUE THEN
    /* Show simplified version */
    Show simplified question set
    Skip advanced options automatically
ELSE
    /* Show full question set */
    Show all available options
    Show advanced customization options
END IF

/* Also based on transaction amount */
IF ContractAmount < 100000 THEN
    /* Simplified set */
    Skip complex payment term options
ELSE
    /* Full set */
    Show all payment term variations
END IF
```

---

## Accessibility and Usability

### Plain Language Principles

Use language appropriate for all educational backgrounds:

**Legal Jargon** → **Plain Language**

- "In perpetuity" → "Forever, without end"
- "Indemnify" → "Protect from loss or liability"
- "Whereas" → "Background/reason"
- "Hereinafter" → "Going forward"
- "Notwithstanding" → "Despite" or "Except for"

### Example Questions

**Complex**: "What is the appropriate non-compete restrictive covenant duration in consonance with reasonable business protectable interests?"

**Clear**: "How long should the non-compete clause prevent the employee from working for competitors? (e.g., 6 months, 1 year, 2 years)"

### Visual Design

- Use clear headings to organize sections
- Provide adequate white space
- Use consistent formatting
- Highlight required fields clearly
- Use color sparingly and meaningfully

### Mobile Responsiveness

Ensure questionnaire works on all devices:

```
Desktop View:
[Sidebar Menu] [Main Content Area]

Tablet View:
[Condensed Menu] [Main Content Area]

Mobile View:
[Hamburger Menu] [Full-Width Content]
```

### Keyboard Navigation

Enable full keyboard navigation without requiring mouse:

- Tab through fields in logical order
- Enter key to select and proceed
- Escape key to cancel or go back
- Clear focus indicators on current field

### Screen Reader Compatibility

- Use semantic HTML
- Provide alt text for icons
- Associate labels with form fields
- Use ARIA attributes for complex interactions
- Test with screen reader software

---

## Integration with Document Generation

### Variable Mapping

Ensure questionnaire fields map correctly to document variables:

**Questionnaire Question** → **Document Variable** → **Document Usage**

```
Question: "Client name"
Variable: ClientName
Usage: "This Agreement is between «ClientName»..."

Question: "Client address"
Variables: ClientAddress, ClientCity, ClientState, ClientZip
Usage: "Located at «ClientAddress», «ClientCity», «ClientState» «ClientZip»"

Question: "Annual revenue"
Variable: AnnualRevenue
Usage: "Based on annual revenue of «AnnualRevenue»..."
```

### Multi-Template Questionnaires

Single questionnaire that can generate multiple document types:

```hotdocs
Question "What type of agreement do you need?" as "AgreementType"
    Options:
        - Service Agreement
        - License Agreement
        - Purchase Agreement
        - Lease Agreement

/* Route to appropriate template */
IF AgreementType = "Service Agreement" THEN
    Load ServiceAgreementTemplate
    Include Service-specific questions
ELSE IF AgreementType = "License Agreement" THEN
    Load LicenseAgreementTemplate
    Include License-specific questions
/* etc. */
END IF
```

### Question to Clause Mapping

Track which questions control which document sections:

| Question | Variable | Affects Clause(s) |
|----------|----------|------------------|
| "Include non-compete?" | IncludeNonCompete | Article IV: Restrictive Covenants |
| "Non-compete duration" | NonCompeteDuration | Article IV, Section 2 |
| "Restricted territory" | RestrictedTerritory | Article IV, Section 3 |
| "Entity type" | EntityType | Recitals, Authorization section |
| "Contract amount" | ContractAmount | Article III: Fees, Exhibit A |

---

## Testing and Optimization

### User Testing

Conduct testing with actual users:

#### Usability Testing

- Observe users completing questionnaire
- Identify confusing questions or navigation
- Time completion and gather feedback
- Identify areas of difficulty

#### Think-Aloud Testing

Ask users to verbalize their thought process:

- "What do you understand this question to be asking?"
- "How would you answer this?"
- "Are there any terms you find confusing?"

#### Scenario Testing

Test with realistic scenarios:

- "Complete this questionnaire as if you were [specific client type]"
- "Imagine you need [specific document type]"
- "Try to complete this with incomplete information"

### Metrics and Optimization

#### Completion Rates

Track how many users complete questionnaires:

- Overall completion percentage
- Drop-off points (where users abandon)
- Time to completion
- Error/retry rates

#### Error Analysis

Monitor validation errors:

- Most common errors
- Fields that require clarification
- Validation rules that may be too strict

#### User Feedback

Collect feedback:

- "Was anything confusing?"
- "How long did this take?"
- "Would you want any questions added or removed?"

### Iterative Improvement

Use testing results to improve:

1. **Simplify Confusing Questions**: Reword unclear questions
2. **Add Clarification**: Provide better hints and examples
3. **Reorganize Logic**: Move conditional questions for better flow
4. **Reduce Burden**: Remove unnecessary questions
5. **Add Validation**: Prevent common errors
6. **Improve Navigation**: Make flow more intuitive

---

## Conclusion

Effective client intake questionnaires are the foundation of successful document automation. By balancing comprehensiveness with simplicity, using clear language, implementing intelligent conditional logic, and continuously optimizing based on user feedback, legal organizations can create questionnaires that users find easy and pleasant to complete while gathering all necessary information for accurate document generation.

The investment in well-designed questionnaires pays dividends in reduced errors, higher completion rates, greater user satisfaction, and ultimately, better legal documents.
