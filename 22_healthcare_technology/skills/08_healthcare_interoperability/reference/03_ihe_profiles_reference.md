# IHE (Integrating the Healthcare Enterprise) Profiles Reference

## Overview

IHE coordinates healthcare organizations to integrate their systems. It defines profiles specifying how standards should be used together for specific healthcare processes.

## Core Concept: Actors and Transactions

### Actor Roles
- **Document Source** - Creates documents
- **Document Registry** - Maintains document metadata
- **Document Repository** - Stores documents
- **Document Consumer** - Retrieves documents
- **Imaging Manager** - Manages imaging data
- **Patient Demographics Supplier** - Provides patient info

### Transaction Types
- **Registry Stored Query (ITI-18)** - Query for document metadata
- **Retrieve Document Set (ITI-43)** - Fetch documents
- **Provide and Register Document Set (ITI-41)** - Submit documents
- **Patient Identity Feed (ITI-8)** - Patient registration
- **Patient Demographics Query (ITI-21)** - Search for patients

## Major IHE Profiles

### 1. Cross-Enterprise Document Sharing (XDS)

**Purpose:** Enables secure exchange of clinical documents across healthcare enterprises

**Key Components:**
- Document Registry - Stores metadata
- Document Repository - Stores documents
- Document Source - Submits documents
- Document Consumer - Retrieves documents

**Transactions:**
- ITI-41: Provide and Register Document Set
- ITI-42: Register Document Set (metadata only)
- ITI-43: Retrieve Document Set
- ITI-18: Registry Stored Query

**Supported Document Types:**
- Clinical reports
- Lab results
- Imaging reports
- Discharge summaries
- Progress notes

### 2. Cross-Community Access (XCA)

**Purpose:** Extended XDS for cross-community queries

**Key Transactions:**
- ITI-38: Cross-Community Query
- ITI-39: Cross-Community Retrieve

**Features:**
- Multi-community document discovery
- Community gateway integration
- Direct retrieval across communities

### 3. Mobile Health Documents (MHD)

**Purpose:** FHIR-based version of XDS for mobile devices

**Key Resources:**
- DocumentReference
- Bundle
- List
- Binary

**Transactions:**
- Simple Document Upload: POST Bundle
- Document Query: GET with search parameters
- Document Retrieve: GET Binary

**Advantages:**
- Native FHIR/REST support
- Better mobile integration
- JSON/XML flexibility

### 4. Patient Identifier Cross-Reference (PIX)

**Purpose:** Maintain patient identity across systems

**Actors:**
- PIX Manager - Maintains master patient index
- PIX Consumer - Queries for identifiers

**Transactions:**
- ITI-8: Patient Identity Feed (HL7 v2)
- ITI-9: PIX Query (HL7 v2)
- ITI-10: PIX Update Notification (HL7 v2)

**Use Cases:**
- Emergency department lookups
- Multi-system patient consolidation
- Insurance eligibility verification

### 5. Patient Identifier Cross-Reference for Mobile (PIXm)

**Purpose:** FHIR-based version of PIX

**Key Resources:**
- Patient
- Patient/$ihe-pix operation

**Transaction:**
- ITI-83: Mobile Patient Identifier Cross-reference Query

### 6. Patient Demographics Query (PDQ)

**Purpose:** Query for patient demographics information

**Actors:**
- PDQ Supplier - Maintains demographic data
- PDQ Consumer - Queries demographics

**Transactions:**
- ITI-21: Patient Demographics Query (HL7 v2)
- ITI-22: Patient Demographics and Visit Query Response (HL7 v2)

**Search Fields:**
- Last name, first name
- Date of birth
- Gender
- Identifier (MRN, SSN, etc.)
- Phone number
- Address

### 7. Patient Demographics Query for Mobile (PDQm)

**Purpose:** FHIR-based demographics query

**Key Resources:**
- Patient
- Search parameters

**Transaction:**
- ITI-78: Patient Demographics Query for Mobile

### 8. Retrieve Information for Display (RID)

**Purpose:** Retrieve document information for display in portals

**Transactions:**
- ITI-29: Get Documents
- ITI-30: Get Document and Retrieve Multiple
- ITI-31: One-time Document Retrieve

### 9. Consistent Time (CT)

**Purpose:** Ensure time synchronization across systems

**Requirements:**
- Network Time Protocol (NTP)
- Time validation and logging
- Clock offset monitoring

### 10. Audit Trail and Node Authentication (ATNA)

**Purpose:** Secure communication and audit logging

**Features:**
- TLS encryption
- Node authentication
- Digital signatures
- Audit event logging
- Non-repudiation

**IHE Audit Events:**
- User Authentication
- Document Creation/Access
- Query Execution
- Security Policy Changes

## Typical IHE Implementation Flow

```
1. Patient Admission (ITI-8: Patient Identity Feed)
   ↓
2. Patient Registration (ITI-8)
   ↓
3. Document Creation in EHR
   ↓
4. Document Submission (ITI-41: Provide and Register)
   ↓
5. Document Stored in Repository/Registry
   ↓
6. Patient Demographics Query (ITI-21: PDQ)
   ↓
7. Document Retrieval by Provider (ITI-43: Retrieve)
```

## Integration Scenarios

### Scenario 1: Single Community (XDS)
- Single document registry and repository
- All providers submit to and retrieve from same registry
- Simpler deployment
- Used within hospital systems

### Scenario 2: Multi-Community (XCA)
- Multiple independent communities
- Community gateways coordinate searches
- Each community maintains independence
- Used for regional health information exchanges

### Scenario 3: Mobile Access (MHD/PIXm/PDQm)
- FHIR-based mobile friendly APIs
- Suitable for patient-facing applications
- REST/JSON native
- Used in patient portals and apps

## Compliance Considerations

### Security Requirements (ATNA)
- TLS 1.2+ for all transactions
- Certificate-based mutual authentication
- Digital signatures on documents
- Audit logging of all access

### Metadata Requirements
- Document creation time
- Patient identifier
- Author information
- Document type/specialty
- Confidentiality classification
- Unique ID for each document

### Error Handling
- Invalid patient identifier
- Insufficient permissions
- Repository unavailable
- Registry query failures
- Metadata validation errors

## Performance Tuning

### Query Optimization
- Index frequently searched fields
- Cache patient identifiers
- Implement pagination for results
- Use specific search criteria

### Document Storage
- Compress documents for storage
- Implement tiered storage
- Archive old documents
- Monitor repository size

## Common Implementation Challenges

1. **Patient Matching** - Dealing with duplicate/similar patient records
2. **Namespace Management** - Managing multiple identifier systems
3. **Time Synchronization** - Ensuring accurate timestamps across systems
4. **Metadata Consistency** - Maintaining accurate document metadata
5. **Cross-Community Coordination** - Gateway setup and configuration
6. **Legacy System Integration** - Bridging old and new systems

## Tools and Libraries

- **OpenEHR** - Clinical data models
- **HAPI FHIR** - FHIR server with IHE support
- **Firely Server** - FHIR implementation
- **OpenMRS** - Medical records system with IHE support
- **Gazelle** - IHE testing and validation

## Certification and Testing

- **IHE Connectathon** - Annual testing event
- **Gazelle Test Tools** - Automated testing platform
- **Pre-connectathon Testing** - Before live events
- **Production Conformance** - Ongoing monitoring

## Roadmap and Evolution

### Recent Changes
- Increased focus on mobile (MHD, PIXm, PDQm)
- Shift towards FHIR-based profiles
- Enhanced security requirements
- Real-time data exchange emphasis

### Future Directions
- Extended authentication mechanisms
- Advanced privacy controls
- Blockchain for audit trails
- AI/ML for data quality
