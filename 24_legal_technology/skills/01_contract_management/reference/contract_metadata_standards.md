# Contract Metadata Standards

## Overview

Contract metadata standards define the structured data elements required to describe, classify, and manage contracts throughout their lifecycle. These standards enable organizations to create a uniform contract taxonomy, support advanced analytics, ensure regulatory compliance, and facilitate system integration.

## Core Metadata Categories

### 1. Contract Identification
- **Unique Identifier**: System-generated UUID or alphanumeric code
- **Contract Name**: Descriptive name following naming convention
- **Alternate Names**: Known-as references, legacy names
- **Contract Number**: Legacy system or manual reference number
- **Version Number**: Current version (major.minor format)
- **Status**: Draft, Pending Approval, Active, Executed, Expired, Terminated

### 2. Party Information
- **Party Type**: Customer, Vendor/Supplier, Partner, Affiliate, Government
- **Legal Entity Name**: Official registered name
- **Party Identifier**: DUNS, EIN, Tax ID, or vendor code
- **Address**: Billing and legal addresses
- **Contact Information**: Primary contact, email, phone
- **Counterparty Classification**: Strategic, standard, transactional
- **Party Hierarchy**: Parent company, subsidiary, division relationships
- **Counterparty Risk Rating**: Low, Medium, High, Critical

### 3. Contract Classification
- **Contract Type**: Service Agreement, NDA, Purchase Order, SLA, MSA, Statement of Work, License Agreement, Employment Agreement, Lease, Partnership Agreement
- **Sub-Type**: Specific category within type (e.g., SaaS vs. Professional Services for Service Agreements)
- **Industry Code**: NAICS or industry-specific classification
- **Procurement Category**: For supplier contracts (IT, Professional Services, Raw Materials, etc.)
- **Functional Owner**: Department responsible (Procurement, Legal, Finance, HR, Operations)
- **Business Unit**: Organizational unit involved
- **Cost Center**: Accounting cost center allocation
- **Product/Service**: Related product or service line
- **Geography**: Jurisdictions covered, primary location
- **Currency**: Contract currency denomination
- **Language**: Language of contract execution

### 4. Financial Terms
- **Contract Value**: Total contract amount (numeric)
- **Value Type**: One-time, annual, lifetime value
- **Payment Currency**: Currency of payment
- **Billing Period**: Monthly, quarterly, annual
- **Payment Terms**: Net 30, Net 60, Due on Receipt, etc.
- **Invoice Frequency**: How often invoiced
- **Discount Percentage**: Volume, early payment, or other discounts
- **Minimum Commitment**: Minimum annual or aggregate amount
- **Maximum Liability**: Cap on liability (if specified)
- **Price Adjustment Clause**: CPI, annual increase percentage, custom formula
- **Spend Band**: Categorization by value (e.g., <$100K, $100K-$1M, >$1M)

### 5. Temporal Information
- **Effective Date**: When contract became/becomes active
- **Expiration Date**: When contract terminates
- **Contract Duration**: Length of agreement (e.g., 3 years)
- **Renewal Date**: When contract eligible for renewal
- **Renewal Type**: Auto-renewal, manual renewal, evergreen
- **Renewal Notice Period**: Days required for renewal notification
- **Termination Notice Period**: Days required for termination notice
- **Created Date**: When contract created in system
- **Last Modified Date**: Last update timestamp
- **Executed Date**: When contract was signed
- **Go-Live Date**: When contract became operational
- **Termination Date**: If applicable, actual termination date

### 6. Compliance & Governance
- **Approval Status**: Not Started, In Progress, Approved, Rejected, Conditionally Approved
- **Required Approvals**: List of approvals still needed
- **Legal Review Status**: Reviewed, Issues Identified, Approved
- **Compliance Classification**: Standard, Sensitive, Regulated, Restricted
- **Applicable Regulations**: GDPR, HIPAA, SOX, FCPA, Export Control, etc.
- **Insurance Requirements**: Required coverage types and amounts
- **Audit Classification**: Auditable, Non-Auditable
- **Retention Period**: How long to retain after expiration
- **Authority Level**: Who approved (Chief Procurement Officer, General Counsel, etc.)
- **Risk Level**: Low, Medium, High, Critical

### 7. Relationship Mapping
- **Parent Agreement**: For amendments, SOWs, etc.
- **Related Contracts**: Cross-referenced agreements
- **Amendment Number**: If applicable
- **Master Agreement Reference**: Link to umbrella agreement
- **Amendment Date**: When amendment effective
- **Attachment References**: Related documents or exhibits
- **Framework Agreement ID**: Parent framework if applicable

### 8. Performance & Obligations
- **SLA Tracking Status**: Compliant, At Risk, Non-Compliant
- **Key Performance Indicators**: List of KPIs by name
- **Obligation Count**: Number of tracked obligations
- **Critical Obligations**: Number of high-priority obligations
- **Next Milestone Date**: Upcoming important date
- **Penalty Clause Present**: Yes/No indicator
- **Dispute Status**: None, In Discussion, In Progress, Resolved

### 9. Sourcing & Procurement
- **Sourcing Method**: Competitive Bid, RFP, Negotiated, Direct Award, Framework
- **Competitive Bid Count**: Number of bids received
- **Incumbent Vendor**: Whether incumbent or new vendor
- **Cost Savings Target**: Expected savings percentage or amount
- **Cost Avoidance**: Estimated costs avoided by this contract
- **Sourcing Owner**: Procurement professional responsible
- **Supplier Account Manager**: Main contact at supplier

### 10. Renewal & Management
- **Renewal Status**: Not Due, Due Soon (30-90 days), Due Now, Overdue, Renewed
- **Renewal Decision**: Renew, Non-Renew, Renegotiate, Replace
- **Decision Rationale**: Why not renewing (cost, performance, consolidation)
- **Renewal Owner**: Who responsible for renewal decision
- **Price Change in Renewal**: Percentage or amount
- **Scope Change in Renewal**: Description of changes
- **Next Review Date**: When to conduct contract review
- **Lessons Learned**: Notes from prior execution

## Metadata Standards by Platform

### Agiloft Metadata Model
- **Custom Fields**: Unlimited custom fields and field types
- **Picklists**: Controlled vocabularies for classification
- **Lookups**: Relationships to other entities (parties, users)
- **Calculated Fields**: Formula-based metadata derivation
- **Related Records**: Multi-level relationships and hierarchies
- **Field Permissions**: Role-based field visibility and editability
- **Metadata Validation**: Required fields, conditional requirements

### Icertis Metadata Model
- **Standard Fields**: Pre-defined metadata schema
- **Entity Model**: Contracts, parties, documents, obligations, milestones
- **Party Directory**: Centralized party master data
- **Obligation Model**: Standardized obligation structure
- **Relationships**: Contract relationships, party relationships
- **Custom Attributes**: Extensible custom metadata
- **AI-Extracted Fields**: Automatically extracted metadata

### DocuSign Metadata Model
- **Custom Fields**: Agreement custom metadata
- **Tagging System**: Tag-based classification
- **Relationship Links**: Agreement relationships
- **Participant Roles**: Define signing and approval roles
- **Event Streams**: Timeline-based metadata
- **Integration Data**: Data synchronized from external systems
- **Custom Objects**: Link agreements to custom CRM objects

## Data Quality Standards

### Completeness
- **Mandatory Fields**: All core identifiers, party info, dates must be populated
- **Conditional Fields**: Certain metadata required based on contract type
- **Acceptable Values**: Only valid values per data type
- **Documentation**: Metadata definitions documented and accessible

### Accuracy
- **Source Validation**: Verify party identifiers against master data
- **Date Validation**: Ensure logical date sequences (effective before expiration)
- **Financial Validation**: Contract value must match source documents
- **Regular Audits**: Periodic metadata quality audits

### Consistency
- **Standardized Format**: Consistent naming, formatting, conventions
- **Taxonomy Alignment**: All values from approved taxonomies
- **Cross-System Consistency**: Metadata matches integrated systems
- **Version Control**: Metadata changes tracked and timestamped

### Accessibility
- **Searchability**: Metadata enables contract discovery
- **Reporting**: Metadata supports standard reports
- **Analytics**: Metadata enables portfolio analysis
- **Export**: Metadata can be exported in standard formats

## Metadata Governance

### Ownership & Stewardship
- **Data Owner**: Department responsible for metadata accuracy
- **Custodian**: IT/System person who manages platform
- **Stakeholders**: Users who benefit from metadata
- **Governance Committee**: Meets quarterly to review standards

### Metadata Maintenance
- **Creation Standards**: Mandatory metadata populated at creation
- **Update Process**: Clear process for metadata changes
- **Validation Rules**: System-enforced metadata quality
- **Exception Handling**: Process for non-standard metadata
- **Review Cycle**: Annual review and update of standards

### Training & Documentation
- **Standard Documentation**: Clear definitions of each metadata element
- **User Training**: Training on metadata requirements and standards
- **Best Practices Guide**: Examples and guidance for proper metadata
- **FAQ Documentation**: Common questions about metadata

## Integration Mapping

### ERP Integration (SAP/Oracle)
- **Vendor Master**: Map party information to ERP vendor codes
- **Cost Center**: Sync cost center allocation for contracts
- **Purchase Order**: Link contracts to POs for spend tracking
- **GL Account**: Map financial data to accounting codes
- **Organizational Unit**: Sync business unit classification

### Procurement Integration (Coupa/Ariba)
- **Supplier Information**: Synchronize supplier classification
- **Category Management**: Align procurement categories
- **Sourcing Events**: Link to RFP and bidding data
- **Spend Analytics**: Enable spend categorization
- **Contract Visibility**: Expose contract data to procurement users

### CRM Integration (Salesforce)
- **Opportunity Mapping**: Link contracts to customer opportunities
- **Account Mapping**: Sync customer account information
- **Contact Information**: Update customer contact data
- **Opportunity Value**: Sync contract financial data
- **Account Health**: Derive from contract performance data

### eSignature Integration (DocuSign/Adobe)
- **Signer Information**: Map parties to signers
- **Signature Status**: Track signature workflow progress
- **Execution Evidence**: Store signature audit trail
- **Signed Document**: Link signed versions to contract records

## Sample Metadata Template

### Minimum Required Metadata
```
1. Contract Identification
   - Unique Identifier (required)
   - Contract Name (required)
   - Contract Type (required)
   - Status (required)

2. Party Information
   - Party Name (required)
   - Party Type (required)
   - Party Identifier (required)

3. Financial Terms
   - Contract Value (required for purchase contracts)
   - Currency (required)
   - Payment Terms (recommended)

4. Temporal
   - Effective Date (required)
   - Expiration Date (required)
   - Created Date (auto-populated)

5. Governance
   - Functional Owner (required)
   - Compliance Classification (required)
   - Approval Status (required)
```

## Metadata Standards Evolution

As organizations mature in CLM, metadata standards typically evolve through stages:

1. **Initial (Months 1-3)**: Core metadata only, basic classification
2. **Intermediate (Months 4-12)**: Extended metadata, enhanced classification
3. **Advanced (Year 2+)**: AI-extracted metadata, predictive attributes, real-time updates
4. **Intelligent (Year 3+)**: Machine learning recommendations, autonomous metadata management

## Conclusion

Comprehensive, well-governed metadata standards are foundational to CLM success, enabling effective contract discovery, analytics, compliance, and automation. Standards should be established upfront, enforced through system controls, and evolved as organizational needs mature.
