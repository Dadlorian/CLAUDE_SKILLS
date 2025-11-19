# Sanctions Screening and Watchlist Management Reference

## Global Sanctions Compliance and Screening Technology

### Overview

Sanctions screening is the process of checking customers, transactions, and business partners against government sanctions lists, watchlists, and restricted party lists to ensure compliance with economic sanctions programs. Effective sanctions screening prevents prohibited transactions and relationships with sanctioned individuals, entities, vessels, and jurisdictions.

### Regulatory Framework

#### U.S. Office of Foreign Assets Control (OFAC)

**Authority:**
- Primary U.S. sanctions authority
- Administers and enforces economic and trade sanctions
- Issues regulations under various statutory authorities

**Key Sanctions Programs:**
- **Country-Based:** Cuba, Iran, North Korea, Syria, Russia, Venezuela, Belarus
- **List-Based:** Specially Designated Nationals (SDN), Sectoral Sanctions, Non-SDN entities
- **Activity-Based:** Narcotics trafficking, terrorism, cyber attacks, human rights abuses

**OFAC Lists:**
- **Specially Designated Nationals (SDN) List:** ~12,000+ entries of blocked persons and entities
- **Consolidated Sanctions List:** Combines all OFAC lists
- **Sectoral Sanctions Identifications (SSI) List:** Russia/Ukraine-related sectoral sanctions
- **Non-SDN Lists:** Various non-blocking sanctions (Palestinian Legislative Council, etc.)
- **Foreign Sanctions Evaders (FSE) List**
- **Specially Designated Narcotics Traffickers (SDNT)**
- **Specially Designated Global Terrorists (SDGT)**

**Prohibited Transactions:**
- **Blocking (Freezing):** Assets of SDNs must be blocked/frozen
- **Rejection:** Transactions to/from sanctioned countries or persons must be rejected
- **50% Rule:** Entities owned 50%+ by SDNs are also blocked (even if not on list)

**OFAC Compliance Requirements:**
- Risk-based sanctions compliance program
- Screening customers, transactions, trade partners
- Blocking and rejecting prohibited transactions
- Reporting blocked property and rejected transactions
- Sanctions list updates (real-time or near real-time)
- Record retention

#### United Nations (UN) Sanctions

**UN Security Council Sanctions:**
- Country and entity-specific sanctions
- Terrorism-related sanctions (Al-Qaeda, ISIS, Taliban)
- Arms embargoes, travel bans, asset freezes
- Mandatory for all UN member states

**UN Consolidated List:**
- Combines all UN sanctions lists
- Updated regularly by UN Sanctions Committees

#### European Union (EU) Sanctions

**EU Sanctions Programs:**
- Country-based sanctions (Russia, Belarus, Iran, North Korea, Syria, etc.)
- Thematic sanctions (terrorism, cyber attacks, chemical weapons, human rights)
- EU Consolidated List of persons, groups, and entities subject to sanctions

**EU Sanctions Regulations:**
- Legally binding on all EU member states
- Directly applicable EU regulations
- National implementation measures

#### United Kingdom (UK) Sanctions

**UK Sanctions Post-Brexit:**
- Independent UK sanctions regime (since January 2021)
- UK Sanctions List (replaces EU list for UK)
- Largely aligned with UN, EU, and U.S. sanctions but independent
- HM Treasury Office of Financial Sanctions Implementation (OFSI)

**UK Sanctions Programs:**
- Country-based (Russia, Belarus, Iran, North Korea, Syria, etc.)
- Thematic (terrorism, cyber, chemical weapons, human rights, corruption)

#### Other Jurisdictions
- **Canada:** Global Affairs Canada sanctions
- **Australia:** Department of Foreign Affairs and Trade sanctions
- **Switzerland:** State Secretariat for Economic Affairs (SECO)
- **Japan:** Ministry of Economy, Trade and Industry (METI)
- **Hong Kong:** Hong Kong Monetary Authority (HKMA)

### Sanctions Screening Process

#### 1. List Management

**Sanctions List Sources:**
- **Primary Sources:** Direct from regulators (OFAC, UN, EU, UK, etc.)
- **Commercial Providers:** Dow Jones, Refinitiv, Accuity, ComplyAdvantage, LexisNexis
- **Frequency:** Real-time or daily updates

**List Consolidation:**
- Combine multiple sanctions lists into single screening database
- Standardize data formats
- Handle duplicates across lists
- Maintain list metadata (source, program, date added)

**List Updates:**
- **Real-Time Updates:** Immediate updates when lists change (critical for compliance)
- **Daily Updates:** Batch updates once per day
- **Change Notifications:** Alert when lists are updated
- **Version Control:** Track list versions and changes

**Enhanced List Data:**
- Additional identifiers (DOB, address, passport, national ID)
- Aliases and alternate spellings
- Associated entities and relationships
- Program and sanction type
- Images/photos

#### 2. Screening Methods

**Name Screening:**
- **Exact Match:** Identical names (rare due to variations)
- **Fuzzy Match:** Account for typos, misspellings, transliterations
- **Phonetic Match:** Sound-alike names (Soundex, Metaphone)
- **Nickname and Alias Matching:** Common nicknames and known aliases

**Additional Identifier Screening:**
- Date of birth (DOB)
- Address and country
- Passport number
- National ID number
- Tax ID / registration number
- Vessel IMO number
- Aircraft tail number
- Email address
- Phone number

**Entity Screening:**
- Company name
- Registered address
- Registration number
- Ownership structure
- Officers and directors

**Geographic Screening:**
- Country of origin/destination
- Sanctioned regions and territories
- Embargoed locations

#### 3. Screening Scenarios

**Customer Screening:**
- **Onboarding:** Screen all new customers before account opening
- **Periodic Re-Screening:** Regular re-screening of existing customers (daily, weekly, monthly)
- **Event-Driven Re-Screening:** When sanctions lists updated

**Transaction Screening:**
- **Payment Screening:** Screen all parties in payment transactions (originator, beneficiary, intermediaries)
- **Trade Finance Screening:** Screen parties in letters of credit, trade documents
- **Wire Transfer Screening:** Screen SWIFT and other wire transfers
- **Card Transaction Screening:** Screen merchant names and locations
- **Real-Time Screening:** Screen before transaction execution
- **Batch Screening:** Screen transactions after the fact (risk-based)

**Third-Party Screening:**
- Vendors and suppliers
- Business partners and agents
- Correspondent banks
- Counterparties in trades
- Beneficial owners

**Other Screening:**
- Vessel screening (shipping)
- Aircraft screening
- Email and communication monitoring
- Trade document screening (invoices, bills of lading)

#### 4. Match Quality and Scoring

**Fuzzy Matching Algorithms:**
- **Edit Distance:** Levenshtein distance (character insertions, deletions, substitutions)
- **Token-Based:** Jaccard, Dice, Cosine similarity
- **Phonetic:** Soundex, Metaphone, Double Metaphone
- **N-Grams:** Character or word n-gram matching

**Match Scoring:**
- Percentage match score (0-100%)
- Threshold-based filtering (e.g., >80% match)
- Weighted scoring (name, DOB, address weights)
- Context-aware scoring (customer risk, jurisdiction)

**False Positive Reduction:**
- **Secondary Identifiers:** Use DOB, address to confirm/eliminate matches
- **Whitelisting:** Pre-approved matches (common names verified as non-matches)
- **Machine Learning:** Learn from historical dispositioning
- **Business Rules:** Apply logic to filter obvious false positives
- **Data Quality:** Improve input data quality

#### 5. Alert Investigation and Dispositioning

**Alert Review Process:**
1. **Initial Screening:** System generates potential match alert
2. **Alert Assignment:** Route to sanctions analyst
3. **Investigation:**
   - Compare input data to list entry
   - Review additional identifiers
   - Research public information
   - Assess match quality
4. **Dispositioning:**
   - **True Match:** Confirmed sanctions match
   - **False Positive:** Not the sanctioned party
   - **Potential Match:** Uncertain, escalate for review
5. **Action:**
   - True Match: Block/reject transaction or customer
   - False Positive: Clear and allow
   - Potential Match: Enhanced due diligence or legal review

**Investigation Tools:**
- Side-by-side comparison of data
- Public records and internet search
- Enhanced profile information from commercial databases
- Link analysis (connections to other sanctioned parties)
- Historical investigation notes

**Documentation:**
- Document investigation steps and sources reviewed
- Rationale for dispositioning decision
- Approvals for clearing potential matches
- Audit trail of all actions

#### 6. Actions for Sanctions Matches

**Blocking (Asset Freeze):**
- Applicable to SDNs and blocked entities
- Freeze all assets and property
- Prohibit all transactions
- Report blocked property to OFAC within 10 days (Annual Report of Blocked Property)

**Rejection:**
- Applicable to transactions to/from sanctioned countries or programs
- Reject or return transaction
- Notify originator
- Report rejected transactions to OFAC (depends on program)

**Enhanced Due Diligence:**
- For potential matches or indirect sanctions exposure
- Gather additional information
- Assess ownership and control
- Determine applicability of 50% rule
- Legal review if needed

**Closing Accounts:**
- For confirmed SDN customers
- Block funds and close account
- Comply with blocking and reporting requirements

### Sanctions Screening Technology

#### Screening Software Solutions

**Leading Sanctions Screening Platforms:**
- **Accuity (a LexisNexis Risk Solutions company):** FIRCOSOFT, Bankers Almanac
- **Dow Jones Risk & Compliance:** Sanctions screening and watchlist data
- **Refinitiv (LSEG):** World-Check One, World-Check Risk Intelligence
- **ComplyAdvantage:** AI-powered sanctions and AML screening
- **NICE Actimize:** Integrated AML and sanctions screening
- **SAS:** Sanctions screening and trade compliance
- **Oracle Financial Services:** Sanctions screening and trade finance compliance
- **ACI Worldwide:** Real-time payment screening
- **Fiserv:** Sanctions screening solutions
- **FICO:** TONBELLER Siron (sanctions and AML screening)

**Screening Capabilities:**
- Real-time and batch screening
- Multi-list screening (OFAC, UN, EU, UK, etc.)
- Fuzzy matching and phonetic algorithms
- Configurable match thresholds
- Whitelisting and auto-dispositioning
- Alert management and case workflow
- Audit trails and reporting
- API and system integrations

#### Integration Points

**Core Banking Systems:**
- Customer Information File (CIF)
- Account opening systems
- Deposit and lending systems

**Payment Systems:**
- SWIFT payment processing
- ACH processing
- Wire transfer systems
- Card processing networks
- Real-Time Payment (RTP) systems

**Trade Finance Systems:**
- Letter of credit systems
- Trade document processing
- Trade finance platforms

**CRM and Onboarding:**
- Customer relationship management (CRM)
- Digital onboarding platforms
- Know Your Customer (KYC) systems

**Other Integrations:**
- Case management systems
- Regulatory reporting systems
- Data warehouses and analytics platforms

#### Screening Architectures

**Embedded Screening:**
- Screening logic within transactional system
- Real-time screening at point of transaction
- Tight integration

**Standalone Screening:**
- Separate screening platform
- Receive transactions/customers via API or file feed
- Return screening results to source system
- Centralized screening across multiple channels

**Hybrid Approach:**
- Embedded screening for real-time decisions
- Standalone screening for comprehensive review and case management

### Screening Best Practices

#### 1. Risk-Based Approach
- Screen based on risk (customer risk, transaction risk, geography)
- Apply different thresholds and matching rules based on risk
- More stringent screening for high-risk scenarios

#### 2. Comprehensive Coverage
- Screen all customers (new and existing)
- Screen all transactions (payments, trade, etc.)
- Screen all third parties (vendors, partners, counterparties)
- Don't rely solely on automated screening for high-risk situations

#### 3. Quality Matching Algorithms
- Use advanced fuzzy matching and phonetic algorithms
- Leverage secondary identifiers to reduce false positives
- Tune match thresholds to balance effectiveness and efficiency
- Implement whitelisting for known false positives

#### 4. Timely List Updates
- Update sanctions lists in real-time or daily
- Re-screen existing customers when lists updated
- Process urgent sanctions updates immediately

#### 5. Effective Investigation and Dispositioning
- Train analysts on sanctions requirements
- Provide robust investigation tools and data sources
- Document all investigations thoroughly
- Escalate uncertain cases appropriately
- Periodic quality assurance of dispositioning

#### 6. Interdiction and Reporting
- Block SDN transactions immediately
- Report blocked property to OFAC timely (10 days)
- Reject sanctioned country transactions
- Maintain complete records of all screening and actions

#### 7. Governance and Oversight
- Senior management and board oversight
- Sanctions compliance officer
- Independent testing and audit
- Metrics and reporting
- Remediation of audit findings

#### 8. Technology and Automation
- Invest in effective screening technology
- Automate screening processes
- Integrate screening across all channels
- Leverage machine learning to reduce false positives
- Monitor screening system performance

### Key Metrics and KPIs

**Screening Effectiveness:**
- Percentage of customers screened
- Percentage of transactions screened
- Time to screen (real-time vs. batch)
- List update frequency and timeliness

**Alert Management:**
- Alert volume and trends
- False positive rate
- Average investigation time
- Alert backlog and aging
- Alert-to-block/reject ratio

**Compliance:**
- Blocked transactions and assets
- Rejected transactions
- OFAC reports filed (blocked property, rejected transactions)
- Regulatory findings and deficiencies
- Re-screening frequency

**Efficiency:**
- Cost per alert investigated
- Analyst productivity
- Automation rate (auto-cleared alerts)
- System uptime and performance

### Sanctions Screening Challenges

**High False Positive Rates:**
- Common names generate many false alerts
- Transliteration variations
- Insufficient identifying information
- Legacy screening technology

**Data Quality:**
- Incomplete or inaccurate customer data
- Lack of secondary identifiers (DOB, address)
- Inconsistent data formats
- Missing information on sanctions lists

**Complex Ownership Structures:**
- Determining 50% ownership for blocking
- Identifying beneficial owners
- Tracking entity restructuring

**Rapid List Changes:**
- Sanctions lists updated frequently (especially during crises)
- Need for real-time updates
- Re-screening existing customers

**Global Compliance:**
- Multiple jurisdictions with different lists
- Conflicting sanctions regimes
- Extraterritorial application of sanctions

**Technology Integration:**
- Integrating screening across multiple systems
- Legacy system limitations
- Real-time screening performance
- Handling high transaction volumes

### Emerging Trends

**Artificial Intelligence and Machine Learning:**
- Reduce false positives through learning
- Improve match quality
- Predict true matches
- Natural language processing for entity resolution

**Network Analysis:**
- Identify indirect sanctions exposure
- Map ownership and control relationships
- Detect sanctions evasion networks

**Blockchain and Cryptocurrency:**
- Screening crypto addresses and wallets
- Blockchain analytics for sanctions compliance
- Virtual asset service provider (VASP) screening

**Cloud-Based Screening:**
- Scalable, cost-effective solutions
- Faster deployment
- Automatic updates
- Global accessibility

**Consortium Data Sharing:**
- Share sanctions screening intelligence
- Collaborative false positive reduction
- Industry best practices

**Regulatory Technology (RegTech):**
- Innovative screening solutions
- Enhanced automation
- Better user experience
- Advanced analytics

### Sanctions Screening Checklist

- [ ] Identify sanctions lists applicable to business (OFAC, UN, EU, UK, etc.)
- [ ] Implement automated sanctions screening technology
- [ ] Screen all customers at onboarding and periodically
- [ ] Screen all transactions in real-time or near real-time
- [ ] Screen third parties (vendors, partners, counterparties)
- [ ] Update sanctions lists in real-time or daily
- [ ] Re-screen existing customers when lists updated
- [ ] Implement effective fuzzy matching algorithms
- [ ] Use secondary identifiers to reduce false positives
- [ ] Establish alert investigation and dispositioning procedures
- [ ] Train staff on sanctions compliance
- [ ] Block SDN transactions and report to OFAC
- [ ] Reject sanctioned country transactions
- [ ] Maintain complete audit trail and documentation
- [ ] Conduct independent testing and audit
- [ ] Report metrics to senior management and board
- [ ] Remediate audit findings timely
- [ ] Stay current on sanctions program changes

---

*Reference for sanctions screening technology implementation and compliance automation*
