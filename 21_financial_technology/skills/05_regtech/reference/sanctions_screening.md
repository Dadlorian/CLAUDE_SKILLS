# Sanctions and PEP Screening

## Sanctions Overview

### Definition
Economic sanctions are restrictions imposed by governments on individuals, entities, or countries to protect national security, foreign policy, or economic interests.

### Types of Sanctions Programs

#### 1. Country-Based Sanctions
- Comprehensive embargoes (e.g., North Korea, Iran, Syria, Cuba)
- Sectoral sanctions (targeting specific industries)
- Secondary sanctions (restrictions on countries trading with sanctioned nations)
- Graduated sanctions (with escalation triggers)

#### 2. Targeted/Specific Sanctions
- Sanctions against individuals and entities
- Asset freezes and transaction prohibitions
- Travel bans and restrictions
- Enforcement against designated persons

#### 3. UN Security Council Sanctions
- Mandatory international compliance
- Country-wide or entity-specific designations
- Asset freezes and travel restrictions
- Exemptions and licensing possibilities

## Regulatory Authorities

### United States
**OFAC (Office of Foreign Assets Control)**
- Part of US Treasury Department
- Maintains Specially Designated Nationals (SDN) List
- Issues Consolidated Sanctions List (CSL)
- Country-based embargo programs
- Sectoral Targeted Sanctions (SSS)
- Non-SDN Foreign Sanctions Evaders List (FSE List)

**Key Lists:**
- SDN List: Primary designations (~8,000+ entries)
- Consolidated Sanctions List (CSL): Aggregated lists
- Entity List (BIS): Export control designations
- Debarred List (SBA): Government contract restrictions
- Consolidated Non-SDN List: Related party designations

### European Union
**OFAC & EU Official Journal Consolidated Lists**
- EU Member State sanctions
- Global designation authorities
- Updated regularly (multiple times per week)
- Freeze List and Financial Sanctions Database
- EU sanctions against persons, entities, and countries

### United Nations
**UN Security Council Consolidated List**
- Consolidated list of individuals and entities
- Target of Al-Qaeda Sanctions Committee
- ISIS/Daesh Sanctions Committee
- Various regional security concerns

### Additional Authorities
- **UK**: Her Majesty's Treasury (HMT) consolidated list
- **Canada**: Global Affairs Canada (GAC) list
- **Australia**: Department of Foreign Affairs and Trade (DFAT)
- **Singapore**: MAS sanctions list
- **Hong Kong**: Monetary Authority sanctions list

## Screening Process

### 1. Pre-Screening (Match Preparation)
```
Customer Data
├── Name Extraction & Parsing
│   ├── Full legal name
│   ├── Common names and aliases
│   ├── Name variations (spelling, transliteration)
│   └── Historical names
├── Entity Information
│   ├── Legal entity type
│   ├── Beneficial owners
│   ├── Directors and officers
│   └── Associated parties
└── Location Data
    ├── Country of residence
    ├── Country of operation
    ├── Jurisdiction of incorporation
    └── Document issue country
```

### 2. Matching Algorithms

#### Exact Match
- Direct name and identity number matching
- Typically not sufficient for sanctions compliance
- First-pass filtering mechanism
- False negative risk due to name variations

#### Fuzzy Matching
- Accounts for spelling variations
- Handles transliteration differences
- Considers phonetic similarities
- Tolerance levels adjustable (70-99%)
- Levenshtein distance calculation
- Soundex or similar phonetic algorithms

#### Boolean Search
- Multiple matching criteria
- Name + DOB + Country combinations
- Title, role, or business type matching
- Document number matching (passport, ID, etc.)
- Hierarchical matching with weighted scoring

#### Machine Learning Matching
- Named Entity Recognition (NER)
- Entity linking and resolution
- Embedding-based similarity
- Context-aware matching
- Dynamic threshold optimization

### 3. Manual Review
- Potential matches above threshold
- Contextual examination
- Risk-based decision making
- Documentation of findings
- Escalation procedures
- Override procedures with approval

### 4. Resolution & Documentation
- True match vs. false positive determination
- Decision documentation
- Approval workflow
- Customer notification (if required)
- Escalation for true positives

## PEP (Politically Exposed Person) Screening

### Definition
A PEP is an individual holding prominent public positions (executive, legislative, military, judicial positions) or family members/close associates of such individuals.

### PEP Categories

#### Tier 1: Direct PEPs
- Current heads of state/government
- Government ministers
- Central bank governors
- Constitutional court judges
- Military commanders
- Senior parliamentary members

#### Tier 2: Senior Officials
- Senior government officials
- Managers of state-owned enterprises
- High-ranking military/police
- Supreme court judges
- Senior UN/international organization officials

#### Tier 3: Affiliated Persons
- Immediate family members of Tier 1-2
- Known close business associates
- Joint beneficial ownership relationships
- Individuals acting as fronts for PEPs

#### Tier 4: Politically Connected Persons
- Family members of lower-level officials
- Persons exercising significant influence
- Relationship to PEPs less direct
- Risk-based approach to classification

### Risk Assessment
```
PEP Risk Matrix:

HIGH RISK
├── Current head of state
├── Active government minister
├── Recent PEP transition (< 12 months)
└── Associated with high-risk jurisdiction

MEDIUM RISK
├── Senior official (lower rank)
├── PEP transition (1-5 years ago)
├── Family of current PEP
└── Close business associate of active PEP

LOW RISK
├── Former government official (> 5 years ago)
├── Distant family relationship to PEP
└── Weak association basis
```

### Ongoing PEP Monitoring
- Automatic updates based on news sources
- Integration with government announcements
- Relationship tracking and review
- Risk score recalculation
- Enhanced due diligence triggers

## Adverse Media Monitoring

### Information Sources
- Major news outlets (Reuters, AP, Bloomberg, etc.)
- Government sources and official announcements
- Financial crime databases
- Regulatory decision publications
- Court records and judgments
- Law enforcement databases

### Screening Categories
```
Adverse Media Categories:

FINANCIAL CRIME
├── Money laundering
├── Fraud and embezzlement
├── Corruption and bribery
├── Asset misappropriation
└── Financial sanctions violations

SANCTIONS & ENFORCEMENT
├── Sanctions violations
├── Export control violations
├── OFAC/EU enforcement actions
└── Government restrictions

CRIMINAL ACTIVITY
├── Drug trafficking
├── Terrorism financing
├── Human trafficking
├── Organized crime
└── Violent crime

REGULATORY VIOLATIONS
├── Banking violations
├── Market manipulation
├── Securities fraud
├── Environmental violations
└── Tax evasion

REPUTATIONAL CONCERNS
├── Negative news coverage
├── Controversial associations
├── Civil litigation
├── Professional misconduct
└── Environmental concerns
```

## Screening Rules Engine

### Sample Rules
```
Rule 1: High-Risk Jurisdiction Match
IF Country ∈ {Iran, Syria, North Korea, Cuba}
THEN Alert = TRUE, Risk_Level = CRITICAL

Rule 2: Exact Name Match to SDN List
IF Name = SDN_List.Name AND
   (DOB = SDN.DOB OR PassportID = SDN.PassportID)
THEN Alert = TRUE, Risk_Level = CRITICAL

Rule 3: Fuzzy Name Match with Country
IF FuzzyMatch(Name, SDN_List.Name) > 95% AND
   Country = SDN.Country
THEN Alert = TRUE, Risk_Level = HIGH

Rule 4: PEP with High-Risk Country
IF PEP_Status = CURRENT AND
   Country ∈ {High-Risk List}
THEN Enhanced_Due_Diligence = TRUE

Rule 5: Adverse Media + Transaction
IF Adverse_Media_Events > 3 AND
   Transaction_Amount > $100,000
THEN Manual_Review = TRUE

Rule 6: Name Variation with High-Risk Indicators
IF FuzzyMatch(Name, SDN) > 85% AND
   (Multiple_Aliases = TRUE OR
    Name_Changes_Recent = TRUE)
THEN Escalate = TRUE, Risk_Level = HIGH
```

## Screening Performance Metrics

| Metric | Target | Impact |
|--------|--------|--------|
| False Positive Rate | < 10% | Operational cost, customer experience |
| False Negative Rate | < 0.1% | Regulatory risk, compliance failure |
| Screening Coverage | 100% | No exposed risk |
| Average Review Time | < 30 min | Case resolution speed |
| Sanctions Match Accuracy | > 99% | Detection quality |
| System Uptime | > 99.99% | Business continuity |

## Best Practices

1. **Real-Time Screening**
   - Screen at account opening
   - Screen on transaction initiation
   - Continuous monitoring for status changes

2. **Database Management**
   - Daily/weekly list updates
   - Version control and audit trail
   - Duplicate removal and deduplication
   - Historical record retention

3. **Threshold Management**
   - Risk-based threshold configuration
   - Regular threshold review and optimization
   - Exception processes documented
   - Audit trail for threshold changes

4. **Documentation**
   - Screen results recorded
   - Match confidence scores documented
   - Disposition decisions documented
   - Approval trail maintained

5. **Periodic Review**
   - Quarterly accuracy assessments
   - Annual process effectiveness review
   - Regulatory examination preparation
   - Testing and validation procedures

## Integration Requirements

- Customer Onboarding System Integration
- Transaction Processing System Integration
- Batch Screening Capabilities
- Real-time API Access
- Webhook Notification System
- List Update Automation
- Reporting and Analytics
- Manual Case Management System
