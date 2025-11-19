# KYC/AML Fundamentals

## Know Your Customer (KYC)

### Definition
KYC is a regulatory requirement for financial institutions to identify and verify the identity of their customers before establishing business relationships. It establishes the foundation for Anti-Money Laundering (AML) and Counter-Terrorist Financing (CFT) compliance.

### Core Components

#### 1. Customer Identification Program (CIP)
- Collect customer identifying information
- Verify customer identity using documents
- Compare against government-issued ID
- Document collection methods and results
- Retention of verification records

#### 2. Customer Due Diligence (CDD)
- Understand nature and purpose of customer relationships
- Know the source of customer funds
- Assess customer risk profile
- Document findings and rationale
- Establish risk-based policies

#### 3. Enhanced Due Diligence (EDD)
- Applied to high-risk customers
- Deeper investigation of beneficial ownership
- Source of funds/wealth investigation
- Business purpose clarification
- Ongoing monitoring and review

### Regulatory Requirements

**United States (FinCEN)**
- Currency Transaction Reports (CTRs) for transactions > $10,000
- Suspicious Activity Reports (SARs) for transactions ≥ $5,000
- Customer Identification Program Rule (31 CFR 1020)
- Customer Due Diligence Rule (31 CFR 1010.230)

**European Union**
- 5th EU Anti-Money Laundering Directive (5AMLD)
- Beneficial Ownership Registers
- Mandatory file reporting for suspicious activities
- Enhanced monitoring of high-risk jurisdictions

**Global Standards**
- FATF (Financial Action Task Force) Recommendations
- 40 core recommendations for AML/CFT
- Risk-based approach to compliance
- Mutual Evaluation Reports (MERs)

## Anti-Money Laundering (AML)

### Money Laundering Process

#### Stage 1: Placement
- Introduction of illicit funds into financial system
- Structuring/smurfing transactions to avoid detection
- Purchase of assets with proceeds
- Cross-border transfers

#### Stage 2: Layering
- Complex transactions to obscure origin
- Multiple jurisdictions and entity involvement
- Trade-based money laundering
- Shell company and trust usage
- Integration with legitimate business

#### Stage 3: Integration
- Return of funds to criminal
- Appears legitimate business income
- Asset purchase and real estate
- Business investment
- Complete integration into legitimate economy

### AML Compliance Pillars

1. **Transaction Monitoring**
   - Real-time screening of transactions
   - Pattern detection and anomalies
   - Comparison against suspicious activity indicators
   - Alert generation and investigation

2. **Sanctions Screening**
   - OFAC SDN (Specially Designated Nationals) list
   - EU consolidated list
   - UN Security Council lists
   - Country-based sanctions programs

3. **Customer Risk Assessment**
   - Risk scoring model
   - Periodic reassessment
   - Continuous monitoring
   - Risk-based CDD application

4. **Suspicious Activity Reporting**
   - Identification of suspicious patterns
   - Investigation and documentation
   - SAR filing requirements
   - Retention policies

5. **Recordkeeping & Reporting**
   - CTR filings
   - SAR filings
   - Currency Transaction Records
   - Retention periods (5-7 years)

## Beneficial Ownership

### Definition
The natural person(s) who ultimately owns or controls the customer entity, directly or indirectly.

### Requirements
- Identify ultimate beneficial owners
- Verify beneficial ownership information
- Update records at least annually
- Maintain BO registers/records
- Escalation for complex structures

### Risk Indicators
- Multiple layers of entities
- Jurisdictions with weak disclosure requirements
- Use of nominees or agents
- Privacy-focused jurisdictions (Panama, BVI, etc.)
- Bearer shares or similar instruments

## Red Flags & Suspicious Indicators

### Customer-Related
- Reluctance to provide information
- Inconsistent information
- Occupation inconsistent with wealth
- Legitimate business purpose unclear
- Previous regulatory violations

### Transaction-Related
- Rapid deposits followed by immediate withdrawal
- Frequent large cash deposits
- Wire transfers to high-risk jurisdictions
- Transactions inconsistent with business profile
- Round-dollar amounts
- Unexplained transaction patterns

### Behavioral
- Customer avoids eye contact
- Nervous behavior during verification
- Frequent address changes
- Multiple accounts with different names
- Use of intermediaries without clear reason

## Compliance Framework

```
┌─────────────────────────────────────────┐
│        KYC/AML Compliance Stack          │
├─────────────────────────────────────────┤
│ 1. Customer Identification Program       │
│ 2. Customer Due Diligence                │
│ 3. Enhanced Due Diligence (Risk-Based)   │
│ 4. Transaction Monitoring & Screening    │
│ 5. Suspicious Activity Investigation     │
│ 6. SAR/CTR Reporting & Filing            │
│ 7. Ongoing Monitoring & Review           │
│ 8. Record Retention & Audit Trail        │
└─────────────────────────────────────────┘
```

## Key Metrics

- **KYC Coverage**: % of customer base with complete KYC
- **EDD Application Rate**: % of customers requiring EDD
- **SAR Filing Rate**: SARs filed per 1,000 customer transactions
- **False Positive Rate**: % of alerts requiring manual investigation
- **Average Investigation Time**: Hours from alert to disposition
- **Sanctions Match Rate**: Detection accuracy for sanctioned entities

## Automation Opportunities

1. **Document Verification** - OCR and automated document validation
2. **Identity Verification** - Biometric matching and 3D liveness detection
3. **Customer Screening** - Automated sanctions and PEP matching
4. **Risk Scoring** - ML-based customer risk assessment
5. **Transaction Analysis** - Pattern detection and anomaly identification
6. **Alert Management** - Intelligent alert prioritization
7. **Reporting** - Automated SAR/CTR generation and filing
