# Sanctions Screening Reference

## Overview
Comprehensive guide to sanctions screening and compliance programs.

## Sanctions Frameworks

### US Sanctions (OFAC)

**Office of Foreign Assets Control (OFAC)**
- **Parent Agency**: US Department of Treasury
- **Jurisdiction**: All US persons and US entities
- **Extraterritorial**: Applies to non-US entities doing business with US persons

**Sanctioned Lists**
1. **SDN List**: Specially Designated Nationals list (individuals and entities)
2. **Blocked Persons**: Entities blocked under specific programs
3. **Consolidated List**: Consolidated list of sanctioned parties
4. **Foreign Sanctions Evaders List**: Persons evading sanctions

**Sanction Programs**
- **IEEPA**: International Emergency Economic Powers Act
- **Trading with the Enemy Act**: War-time sanctions
- **Specific Country Programs**: Iran, North Korea, Syria, Cuba, Crimea
- **Sectoral Sanctions**: Russian sectoral sanctions
- **CAATSA**: Countering America's Adversaries Through Sanctions Act

**Penalties**
- **Civil Penalties**: Up to $250,000 per violation or 2x transaction value
- **Criminal Penalties**: Up to $1 million and 20 years imprisonment
- **Reputational Risk**: Significant reputational damage
- **Licensing**: Need for specific OFAC license

---

### UN Sanctions

**United Nations Security Council Sanctions**
- **Format**: Consolidated UN list
- **Updates**: Regular additions and removals
- **Scope**: Applies to all UN member states

**Designation Criteria**
- Support for terrorism
- Weapons of mass destruction
- Regional threats
- Human rights violations
- Other matters of international concern

---

### EU Sanctions

**European Union Sanctions**
- **Legal Basis**: Common Foreign and Security Policy (CFSP)
- **Consolidated List**: EU consolidated list
- **National Implementation**: Each member state implements
- **Extraterritorial**: Applies to EU persons and EU-based entities

**Sanction Types**
- **Asset Freeze**: Freezing of funds and assets
- **Travel Bans**: Restriction on entry to EU
- **Sector Sanctions**: Restrictions on specific economic sectors
- **Arms Embargo**: Restrictions on military equipment

---

### UK Sanctions

**UK Sanctions**
- **OFSI**: Office of Financial Sanctions Implementation
- **Implementation**: UK sanctions post-Brexit
- **Coverage**: Russia, Iran, North Korea, Syria, Myanmar, and others

---

## Screening Entities

### Screening Data

**Screening Scope**
- **Customers**: Screen all customers (individuals and entities)
- **Beneficial Owners**: Screen beneficial owners (>25% ownership)
- **Transaction Counterparties**: Screen transaction participants
- **Employees**: Screen employees and contractors (for sensitive roles)
- **Vendors**: Screen third-party vendors (especially financial services)

**Screening Information**
- **Name**: Full legal name and any known aliases
- **Address**: Current and historical addresses
- **Identity Document**: Passport, ID number, tax ID
- **Ownership**: Beneficial ownership information
- **Nationality**: Country of citizenship
- **Risk Indicators**: PEP status, legal proceedings, etc.

---

### Matching Methodology

**Exact Matching**
- **Name Matching**: Exact full name matches
- **ID Matching**: Exact identification document matches
- **Limited Matches**: Limited to obvious matches
- **False Negative Risk**: Miss variations and aliases

**Phonetic/Fuzzy Matching**
- **Name Variations**: Match similar sounding names
- **Misspellings**: Match misspelled names
- **Nickname Variations**: Match common name variations
- **False Positive Risk**: Increase in false positives

**Advanced Matching**
- **Machine Learning**: ML-based matching algorithms
- **Context Analysis**: Consider context clues
- **Relationship Analysis**: Analyze family and business relationships
- **Risk Assessment**: Assess match confidence and risk

---

## Sanctions Screening Processes

### Customer Onboarding Screening

**Screening Workflow**
1. **Information Collection**: Collect customer information
2. **Sanctions Screening**: Screen against sanctions lists
3. **Alert Generation**: Generate alert if match found
4. **Investigation**: Investigate potential matches
5. **Resolution**: Determine if true match or false positive
6. **Blocking/Approval**: Block account if true match, approve if false positive
7. **Documentation**: Document screening and decision

**Screening Timing**
- **Immediate**: Screen before account opening
- **Documentation**: Within 24-48 hours for account setup
- **Approval**: Account approval contingent on screening

**Matching Thresholds**
- **High Confidence (>95%)**: Presumed match, requires investigation
- **Medium Confidence (75-95%)**: Possible match, requires investigation
- **Low Confidence (<75%)**: Unlikely match, typically screened out

---

### Ongoing Screening

**Periodic Re-Screening**
- **Frequency**: Annual or semi-annual re-screening
- **Purpose**: Identify newly sanctioned entities
- **Coverage**: All existing customers
- **Documentation**: Document results

**Transaction Screening**
- **Real-Time**: Screen transactions as they occur
- **Parties**: Screen transaction initiator and beneficiary
- **Counterparty**: Screen any counterparty to transaction
- **Beneficial Owner**: Screen beneficial owners
- **Alert Routing**: Route matches for investigation
- **Blocking**: Block transaction if sanctioned match found

---

### Investigation Process

**Match Investigation**
1. **Initial Assessment**: Assess match confidence
2. **Information Review**: Review available information
3. **Additional Research**: Conduct additional research if needed
4. **Determination**: Determine if true match or false positive
5. **Documentation**: Document investigation and conclusion
6. **Resolution**: Implement decision

**Investigation Factors**
- **Name Similarity**: Assess how similar names are
- **Address Proximity**: Assess address similarity
- **Birthdate/Age**: Compare age and birthdate if available
- **Identification Document**: Compare ID information
- **Business Type**: Does type of business match?
- **Geographic Risk**: Is geographic location consistent?
- **Relationship**: Any relationship between similar entities

---

## Sanctions Screening Technology

### OFAC Screening Providers

**Thomson Reuters**
- **Data**: OFAC, UN, EU, and other sanctions lists
- **Matching**: Advanced fuzzy matching algorithms
- **Integration**: API and batch processing
- **Reporting**: Screening reports and analytics
- **Updates**: Regular list updates

**Refinitiv**
- **Data**: Multiple sanctions lists integrated
- **Screening**: Real-time screening capability
- **Matching**: Advanced name matching algorithms
- **Integration**: API, batch, and real-time integration
- **Analytics**: Screening analytics and reporting

**Accuity (LexisNexis)**
- **Data**: Sanctions lists and watchlists
- **Screening**: Real-time and batch screening
- **Matching**: Fuzzy matching with PEP screening
- **Integration**: API and batch processing
- **Reporting**: Detailed screening reports

**GBG**
- **Data**: Global sanctions and watchlists
- **Screening**: Real-time screening
- **Matching**: Advanced matching algorithms
- **Integration**: Cloud-based API
- **Reporting**: Detailed reporting and audit trails

---

### Sanctions Screening Platform Architecture

**Integration Architecture**
```
Customer Data
  ↓
Sanctions Screening Engine
  ↓
Sanctions Data Sources (OFAC, UN, EU, etc.)
  ↓
Match Detection
  ↓
Alert Generation
  ↓
Investigation Workflow
  ↓
Compliance Decision
  ↓
Action (Block/Approve)
```

---

## Sanctions Compliance Program

### Governance & Policy

**Written Policies**
- **Sanctions Screening Policy**: Document screening requirements
- **Escalation Procedures**: Clear escalation procedures
- **Investigation Standards**: Investigation documentation requirements
- **Blocking Procedures**: Procedure for blocking transactions
- **Reporting**: Regulatory reporting procedures
- **Training**: Annual staff training requirements

**Roles & Responsibilities**
- **Compliance Officer**: Overall responsibility for program
- **Front-Line Staff**: Initial screening responsibility
- **Investigation Team**: Investigation of potential matches
- **Management**: Approval and escalation
- **Board**: Board oversight of program

---

### Risk-Based Approach

**Customer Risk Factors**
- **Geographic Risk**: High-risk jurisdictions (Iran, North Korea, etc.)
- **Customer Type**: Financial institutions, money services, import/export
- **Transaction Type**: Cash, wire transfers, trade finance
- **Beneficial Owner**: PEP status or high-risk background
- **Transaction Pattern**: Unusual transaction patterns

**Screening Intensity**
- **High-Risk**: Immediate screening, real-time monitoring, frequent re-screening
- **Medium-Risk**: Standard screening at onboarding, periodic re-screening
- **Low-Risk**: Standard screening, annual re-screening

---

## Reporting & Documentation

### Regulatory Reporting

**OFAC Reporting**
- **Blocking Report**: Report blocking of transaction within 10 days
- **Form TD F 90-22.1**: Currency transaction reporting for over $10,000 cash
- **Penalty Payment**: Payment of sanctions violation penalties if discovered

**EU Reporting**
- **Competent Authority**: Report to member state authority
- **Timeline**: Prompt notification of blocked transactions
- **Documentation**: Document basis for blocking

---

### Internal Documentation

**Screening Records**
- **Screening Date**: Date of screening
- **Screening Results**: Match results and confidence scores
- **Investigation**: Investigation documentation
- **Decision**: Approval or blocking decision
- **Justification**: Justification for decision
- **Retention**: Maintain records per regulation (5-7 years typically)

**Escalation Documentation**
- **Alert Details**: Original alert information
- **Investigation Results**: Investigation findings
- **Decision Authority**: Who made the decision
- **Decision Rationale**: Rationale for decision
- **Date**: Decision date

---

## False Positive Management

### Reducing False Positives

**Matching Improvements**
- **Advanced Algorithms**: ML-based matching to reduce false positives
- **Contextual Analysis**: Consider context to reduce false positives
- **Relationship Mapping**: Map relationships to improve accuracy
- **Historical Data**: Use historical screening data to improve matching

**Whitelist Management**
- **Customer Whitelist**: Maintain list of cleared customers
- **Beneficial Owner Whitelist**: Whitelist cleared beneficial owners
- **Exemption Process**: Define process for whitelisting
- **Whitelist Review**: Periodic review of whitelist entries

**Investigation Standards**
- **Clear Criteria**: Clear investigation standards
- **Multiple Confirmations**: Require multiple confirmations
- **Additional Research**: Conduct additional research
- **Escalation**: Clear escalation for uncertain cases

---

## Metrics & KPIs

### Screening Metrics

**Coverage**
- **Customer Coverage**: % of customers screened
- **Beneficial Owner Coverage**: % of beneficial owners screened
- **Re-screening Rate**: % of customers re-screened
- **Transaction Coverage**: % of transactions screened

**Performance**
- **Screening Timeliness**: Time from customer onboarding to screening
- **Match Resolution Time**: Time from alert to resolution
- **False Positive Rate**: % of matches that are false positives
- **Investigation Quality**: Thoroughness of investigation

### Compliance Metrics

**Program Effectiveness**
- **Training Completion**: % of staff completing annual training
- **Policy Compliance**: Adherence to screening policies
- **Regulatory Compliance**: No regulatory violations or examiner findings
- **Blocking Rate**: Rate of blocked transactions (typically <0.1%)

---

## Best Practices

1. **Comprehensive Screening**: Screen customers, beneficial owners, and transaction counterparties
2. **Advanced Matching**: Use advanced matching algorithms to reduce false positives
3. **Continuous Monitoring**: Ongoing screening, not just onboarding
4. **Clear Procedures**: Clear investigation and blocking procedures
5. **Documentation**: Thorough documentation of all screening activities
6. **Training**: Regular staff training on sanctions requirements
7. **Governance**: Strong governance and board oversight
8. **Technology**: Use robust, validated sanctions screening technology
9. **Risk-Based**: Tailor screening to risk profile
10. **Cooperation**: Cooperate with regulatory agencies if required

---

## Regulatory Expectations

### OFAC Guidance
- **Annual Compliance Review**: Document annual compliance review
- **Risk Assessment**: Document risk assessment
- **Policies and Procedures**: Document policies and procedures
- **Training**: Document staff training
- **Testing**: Conduct testing of sanctions screening system
- **Audit**: Internal and external audit
- **Remediation**: Prompt remediation of violations

### EU Expectations
- **Risk Assessment**: Document risk assessment
- **Due Diligence**: Conduct proper customer due diligence
- **Monitoring**: Ongoing monitoring of transactions
- **Reporting**: Timely reporting to authorities
- **Training**: Regular staff training
- **Documentation**: Maintain proper documentation

---

**Last Updated**: 2025-11-19
**Focus**: Sanctions screening and compliance
