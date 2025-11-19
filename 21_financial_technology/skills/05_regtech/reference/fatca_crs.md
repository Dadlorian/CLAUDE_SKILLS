# FATCA and CRS Compliance

## FATCA (Foreign Account Tax Compliance Act)

### Overview

FATCA is a US tax law requiring financial institutions worldwide to identify US persons and report their account information to the US IRS (Internal Revenue Service).

```
Key Provisions:
├── Financial Account Tax Compliance
├── US Person Identification
├── Account Classification
├── Withholding Requirements (30%)
├── Reporting to IRS
└── Intergovernmental Agreements (IGAs)
```

### US Person Definition

```
US PERSONS INCLUDE:
├── US Citizens
├── US Residents (green card holders)
├── US Tax Residents (substantial presence test)
├── US Corporations/Partnerships/Trusts
├── US Estates (deceased citizens)
├── Persons with US address
├── Persons with US phone number
├── Persons with US driver's license/ID
├── Power of attorney in US
└── Instructions to maintain US account

NON-US PERSONS:
├── Non-US citizens
├── Non-US residents
├── Fail substantial presence test
├── Have valid W-8BEN form
└── Claim treaty protection
```

### Account Classification

```
REPORTABLE ACCOUNTS:
├── Account holder is US person
├── Beneficial owner is US person
├── Mandatorily redeemable entity controlled by US person
└── Any account with nexus to US person

NON-REPORTABLE ACCOUNTS:
├── US Financial Institution accounts
├── Exempt accounts:
│   ├── Retirement accounts (401(k), IRA, etc.)
│   ├── Tax-exempt accounts
│   ├── Approved investment entities
│   ├── Foreign government accounts
│   ├── International organizations
│   └── Certain foreign central banks
└── Lower-value accounts (< $50,000) aggregate
```

### FATCA Compliance Steps

```
Step 1: Identify Financial Institution Status
├── US Financial Institution (FFI)
├── Foreign Financial Institution (FFI)
├── Non-Financial Foreign Entity (NFFE)
└── Determine self-certification path

Step 2: Customer Due Diligence
├── Obtain W-8BEN (non-US person) or W-9 (US person)
├── Certify account holder status
├── Verify beneficial ownership
├── Document documentation process
└── Maintain for 6 years

Step 3: Account Classification
├── US Reportable Account
├── Non-US Account
├── Exempt Account
└── Lower-value Account

Step 4: Withholding Determination
├── If reportable: Withhold 30% on US-source income
├── Withholding not required:
│   ├── Exempt accounts
│   ├── FFI in IGA compliance
│   ├── Account holder compliant
│   └── Income not US-source
└── Track withholding obligations

Step 5: Reporting
├── Form 1099-B (brokerage transactions)
├── Form 1042-S (withholding reporting)
├── Report to IRS
├── Maintain records
└── Provide copies to account holders

Step 6: Compliance Certification
├── Obtain FATCA compliance certification
├── Participate in FFI program
├── Enter into IGA (if applicable)
├── Annual recertification
└── Reporting to government
```

### Withholding Requirements

```
WITHHOLDING ON US SOURCE INCOME:

30% Withholding Applied To:
├── Interest income
├── Dividends
├── Rents
├── Royalties
├── Annuities
├── Compensation for services
├── Gain on property sale (certain cases)
└── Other US-source income

Withholding Exceptions:
├── Non-US source income (foreign interest, etc.)
├── Treaty-qualified income
├── Effectively connected income (ECI)
├── Non-reportable accounts
├── Exempt accounts
├── Withholding exemption certificate
└── Withholding agreement in place

Withholding Mechanics:
├── 30% withholding rate
├── Applied to gross payment
├── Deposited to IRS
├── Documented in reporting
├── Account credited after withholding
└── Annual reconciliation and reporting
```

## CRS (Common Reporting Standard)

### Overview

CRS is a global automatic exchange of financial account information between 100+ countries' tax authorities. Modeled after FATCA but multilateral and broader in scope.

```
Key Features:
├── Automatic Exchange of Information (AEoI)
├── Financial Account Identification
├── Tax Resident Reporting
├── Annual Reporting to Tax Authorities
├── Country-by-Country Information Exchange
├── Participating 100+ Jurisdictions
└── OECD-Developed Standard
```

### Reportable Accounts

```
ACCOUNT CRITERIA FOR REPORTING:

Account Holder Status:
├── Account holder is tax resident of another jurisdiction
├── Account holder resides in reportable jurisdiction
├── Beneficial owner is tax resident of another jurisdiction
├── Beneficial owner resides in reportable jurisdiction
└── Control person is tax resident of another jurisdiction

Account Type:
├── Depository accounts
├── Custodial accounts
├── Equity/debt interest accounts
├── Insurance contracts
├── Annuity contracts
├── Cash value insurance
└── Funds/trusts with financial accounts

NOT REPORTABLE:
├── Lower-value accounts (< €25,000 aggregate)
├── Certain exempt accounts:
│   ├── Retirement accounts
│   ├── Tax-exempt accounts
│   ├── Government accounts
│   ├── International organization accounts
│   └── Central bank accounts
└── Certain financial entities
```

### CRS vs. FATCA Comparison

```
COMPARISON:

Scope:
├── FATCA: US persons only
├── CRS: All non-resident tax persons

Coverage:
├── FATCA: Global institutions
├── CRS: 100+ participating countries

Reporting:
├── FATCA: To US IRS only
├── CRS: Between participating countries

Account Types:
├── FATCA: Investment accounts primarily
├── CRS: Broader (deposits, insurance, etc.)

Threshold:
├── FATCA: Varies by account type
├── CRS: €25,000 aggregate threshold

Timing:
├── FATCA: 2014+
├── CRS: 2017+ (first exchanges)
```

### CRS Compliance Process

```
Step 1: Classify Accounts
├── Reportable Account
├── Excluded Account
├── Lower-value Account
└── Document classification

Step 2: Identify Reportable Persons
├── Tax resident status determination
├── Beneficial owner identification
├── Control person identification
├── Multiple jurisdiction check
└── Document identification

Step 3: Gather Account Information
├── Account number
├── Account holder name, address, DOB
├── Account balance/value
├── Income generated (interest, dividends)
├── Gross proceeds from sales
└── Beneficial owner information

Step 4: Annual Reporting
├── Aggregate by country of tax residence
├── Report to local tax authority
├── Authority exchanges with other countries
├── Format: XML (OECD standard)
└── Due: Annual deadline (typically August 31)

Step 5: Record Retention
├── Maintain documentation
├── 6-year retention
├── Support for classifications
├── Support for identifications
└── Support for valuations
```

### Self-Certification

```
CUSTOMER DOCUMENTATION REQUIRED:

For Account Opening/Maintenance:

INDIVIDUALS:
├── Valid ID (passport, driver's license)
├── Proof of tax residency:
│   ├── Tax identification number
│   ├── Tax residence certificate
│   ├── Government issued ID
│   └── Recent tax return
├── Address verification
├── Beneficial owner (if applicable)
└── W-8BEN (if non-US) or W-9 (if US)

ENTITIES:
├── Corporate registration documents
├── Ownership structure documents
├── Beneficial ownership documentation
├── Tax identification numbers
├── Certificate of incorporation
├── Board resolutions (if applicable)
└── Beneficial owner identification

TRUSTS/PARTNERSHIPS:
├── Trust deed/partnership agreement
├── Beneficiary identification
├── Trustee/partner information
├── Control person identification
├── Tax identification
└── Certificate of existence

Updates Required:
├── Annually (at minimum)
├── On material change
├── When moving jurisdictions
├── When ownership changes
└── When tax residency changes
```

## Form Requirements

### Form W-8BEN (Certificate of Foreign Status)

```
PURPOSE: Claim non-US person status and treaty benefits

COMPLETION BY: Non-US financial account holders

KEY FIELDS:
├── Name and address
├── Foreign TIN (tax ID number)
├── Country of citizenship
├── US tax residency certification
├── Claim to treaty benefits (if applicable)
├── Exemption codes (FATCA, withholding, etc.)
├── Signature and date
└── Certification of accuracy

VALIDITY: 3 years from signing
UPDATES: Required on material change
RETENTION: Maintain for 6 years
```

### Form W-9 (US Persons)

```
PURPOSE: Identify US persons for tax reporting

COMPLETION BY: US citizens, residents, entities

KEY FIELDS:
├── Name and address
├── SSN (Social Security Number)
├── Tax classification
├── Business type
├── Exempt from withholding (if applicable)
├── Certification of accuracy
└── Signature and date

RETENTION: Maintain for 6 years
UPDATE: When information changes
USE: For 1099 and withholding determinations
```

### Form 1099-B (Brokerage Transactions)

```
FOR: Stocks, bonds, mutual funds, options sold

REPORTED: Gross proceeds from sales
├── Sale date
├── Date acquired
├── Cost basis (if known)
├── Gain/loss calculation
├── Corporate action adjustments
└── Money market fund interest

RECIPIENT: US persons only
TIMING: January 31 (following year)
COPIES: Customer and IRS
```

### Form 1042-S (Withholding Statement)

```
PURPOSE: Report income and withholding

REPORTED INCOME TYPES:
├── Interest
├── Dividends
├── Rents and royalties
├── Annuities
├── Compensation for services
├── Gain on property
├── Scholarships/grants
└── Other income

WITHHOLDING INFORMATION:
├── Withholding rate applied
├── Amount withheld
├── Exemption codes
├── Treaty benefits claimed
└── FATCA status

RECIPIENTS: Non-US persons
TIMING: March 15 (following year)
COPIES: Recipient and IRS
```

## Reporting Timelines and Deadlines

```
US REPORTING CALENDAR:

January 31: 1099 forms issued
February 28: 1099 files submitted to IRS
March 15: 1042-S forms issued
April 15: 1042-S files submitted to IRS

CRS REPORTING CALENDAR (By Jurisdiction):

Self-Certification Collection:
├── Ongoing for new accounts
├── Before first reportable event
├── Update on material change
└── At least annually

Data Aggregation:
├── Complete by June 30
├── Validate data quality
├── Prepare for transmission
└── XML file creation

Reporting Deadline:
├── OECD Common Standard
├── Typically August 31 (varies)
├── Automatic exchange with partners
└── Reciprocal reporting received
```

## Best Practices for FATCA/CRS Compliance

1. **Customer Documentation** - Maintain complete, updated self-certifications
2. **Account Monitoring** - Annual review of account status changes
3. **Training** - Staff training on FATCA/CRS requirements
4. **Technology** - Systems that identify and flag reportable accounts
5. **Controls** - Review processes for account classification
6. **Withholding** - Accurate withholding calculation and deposit
7. **Record Retention** - 6-year retention of all documentation
8. **Reporting** - Timely, accurate submission of required forms
9. **Updates** - Processes for updating customer information
10. **Penalties** - Understand penalties for non-compliance
    - Form 1099 incorrect: $50-$100+ per form
    - Failure to file: Penalties for late/incorrect reporting
    - FATCA withholding failures: 10-30% of amount not withheld
    - CRS non-compliance: Varies by jurisdiction
