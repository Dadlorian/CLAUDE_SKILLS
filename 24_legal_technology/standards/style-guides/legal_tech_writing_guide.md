# Legal Technology Writing Guide

## Executive Summary

This comprehensive style guide establishes standards for all written technical documentation, code comments, user-facing content, and specifications within legal technology systems. It integrates American Bar Association (ABA) technical standards with legal writing best practices and ethics compliance requirements under Model Rules of Professional Conduct.

**Audience**: Software engineers, technical writers, legal technologists, compliance officers, and quality assurance teams working on legal tech platforms.

**Version**: 1.0.0
**Last Updated**: November 2025
**Status**: Production-Grade Standards

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Writing Standards](#writing-standards)
3. [Technical Documentation](#technical-documentation)
4. [Legal Language Integration](#legal-language-integration)
5. [Ethics Compliance Standards](#ethics-compliance-standards)
6. [Code Documentation](#code-documentation)
7. [User-Facing Content](#user-facing-content)
8. [Terminology Reference](#terminology-reference)
9. [Review and Approval Process](#review-and-approval-process)
10. [Examples and Templates](#examples-and-templates)

---

## Core Principles

### 1. Clarity and Precision

**Requirement**: All writing must prioritize absolute clarity while maintaining technical precision required by legal professionals.

- Use short, declarative sentences (average 15-20 words)
- Avoid nested clauses that obscure meaning
- Define technical terms before first use
- Use active voice in 90% of sentences
- Minimize use of legalese in technical documentation

**Example - INCORRECT**:
```
The system's capability to facilitate the aggregation and subsequent processing
of documents through the utilization of machine learning algorithms, which are
designed to maximize accuracy whilst maintaining compliance with applicable
regulatory frameworks, is contingent upon proper configuration.
```

**Example - CORRECT**:
```
The system requires proper configuration to aggregate and process documents
using machine learning algorithms. This approach maximizes accuracy while
maintaining regulatory compliance.
```

### 2. Compliance and Accuracy

**Requirement**: All technical claims must be verifiable, accurate, and compliant with relevant legal and ethical standards.

- Every feature claim must be testable and documented
- Accuracy takes precedence over marketing language
- Include disclaimers where technical limitations exist
- Reference ABA standards and applicable legal frameworks
- Maintain audit trails for all significant documentation changes

### 3. Accessibility and Inclusivity

**Requirement**: Content must be accessible to users with varying technical expertise and accessibility needs.

- Avoid assuming prior knowledge of specialized systems
- Provide context for all acronyms (define on first use)
- Use simple language without sacrificing accuracy
- Ensure compliance with WCAG 2.1 AA standards for all digital content
- Use gender-neutral language and inclusive terminology

### 4. Consistency and Standardization

**Requirement**: Terminology, formatting, and structure must remain consistent across all documentation.

- Use controlled vocabulary from the Legal Tech Glossary
- Apply standardized formatting consistently across all documents
- Maintain consistent voice and tone throughout
- Use the same terms for the same concepts (no synonyms)
- Document all intentional variations and explain deviations

---

## Writing Standards

### Tone and Voice

**Professional Legal Context**: Maintain a professional, authoritative tone appropriate for legal professionals and technical specialists.

- **Confidence**: Assert facts directly without hedging
- **Respect**: Acknowledge the expertise of the audience
- **Clarity**: Prioritize understanding over brevity
- **Neutrality**: Present information objectively without marketing bias

**Prohibited Styles**:
- Casual slang or colloquialisms
- Overly technical jargon without explanation
- Marketing hyperbole or unsubstantiated claims
- Condescending or patronizing tone
- Legal boilerplate in technical sections

### Sentence Structure

**Word Count Per Sentence**: Maximum 25 words for technical documentation, maximum 30 words for legal explanations.

**Sentence Components**:
1. Begin with the main subject
2. Use active voice (preferred: 90%+)
3. Place conditions and qualifications at the beginning
4. End with the key action or result

**Example Structure**:
```
[Condition], [subject] [action] [object], [result].

When processing confidential documents, the system applies encryption protocols
immediately upon ingestion, ensuring all data meets HIPAA compliance standards.
```

### Paragraph Structure

**Optimal Paragraph Length**: 40-80 words (approximately 3-5 sentences)

**Paragraph Requirements**:
- One central idea per paragraph
- Topic sentence at the beginning
- Supporting sentences with specific details
- Concluding statement linking to next paragraph
- Clear transition between paragraphs

**Example Paragraph**:
```
Document encryption represents the foundational security layer in legal tech
systems. The system encrypts all incoming documents using AES-256 encryption
standards at the moment of ingestion. This approach aligns with ABA
cybersecurity recommendations and meets NIST cryptographic standards. No
unencrypted documents exist in system storage, ensuring consistent protection
of client confidential information throughout the document lifecycle.
```

### Headings and Structure

**Heading Hierarchy**:
- H1: Document title (one per document)
- H2: Major sections (equivalent to chapters)
- H3: Subsections (major topics within sections)
- H4: Detailed topics (specific implementation details)
- H5: Technical specifications or examples
- H6: Minor clarifications or notes

**Heading Guidelines**:
- Use descriptive nouns, not questions
- Avoid excessive nesting (maximum 4 levels)
- Use parallel structure for same-level headings
- Ensure each heading is preceded by introductory text

### Lists and Enumeration

**List Types**:

**Numbered Lists** - Use when order matters or for sequential steps:
```
Compliance review process:
1. Conduct initial document classification
2. Apply appropriate access controls
3. Generate audit log entries
4. Escalate to compliance officer if needed
```

**Bulleted Lists** - Use for non-sequential items or equal-weight options:
```
Required security certifications:
- ISO 27001 (Information Security Management)
- SOC 2 Type II (Service Organization Control)
- HIPAA BAA (if handling protected health information)
- State bar ethical compliance standards
```

**Requirements**:
- Use parallel grammatical structure
- Begin with action verbs for procedural lists
- Maintain consistent punctuation
- Avoid lists longer than 7 items (break into multiple lists)

### Formatting Standards

**Emphasis**:
- **Bold**: Key terminology, critical warnings, important concepts on first mention
- *Italics*: Citation references, variable names, foreign language terms
- `Code Font`: System components, commands, configuration parameters
- > Blockquotes: Regulatory quotations, important legal standards

**Punctuation Standards**:
- Use Oxford commas in all lists (item1, item2, and item3)
- Use em-dashes (—) for clarifications, not commas
- Avoid semicolons in technical documentation
- Use contractions sparingly in formal legal documentation

**Example with Formatting**:
```
The system implements three core **security mechanisms**: encryption at rest,
encryption in transit, and role-based access control. These mechanisms
collectively provide defense-in-depth protection—recommended by NIST
cybersecurity standards—ensuring confidential documents remain protected
throughout their lifecycle.
```

---

## Technical Documentation

### Requirements Documents

**Purpose**: Specify system functionality, constraints, and compliance obligations

**Required Sections**:
1. Overview (what the system does)
2. Functional Requirements (what it must do)
3. Non-Functional Requirements (performance, security, compliance)
4. Constraints and Limitations (what it cannot do)
5. Compliance Requirements (applicable standards)
6. Data Requirements (what data it processes)
7. Integration Requirements (systems it connects to)
8. Acceptance Criteria (how to verify completion)

**Writing Guidelines**:
- Use "must," "shall," and "will" for mandatory requirements
- Use "should" only for recommendations, not requirements
- Avoid "may" (ambiguous)
- Each requirement must be testable
- Reference specific standards by name and date

**Example Requirement**:
```
REQ-SEC-001: Data Encryption in Transit
The system SHALL encrypt all data in transit using TLS 1.3 (RFC 8446) or
higher. This requirement applies to all connections between client
applications and system servers. The system MUST reject connections from
clients unable to negotiate TLS 1.3 or higher encryption. This requirement
ensures compliance with ABA Cybersecurity and Data Protection Standards
and satisfies NIST SP 800-52 Rev. 2 recommendations.
```

### Architecture Documentation

**Purpose**: Explain system design, component relationships, and technical decisions

**Required Elements**:
1. System Context Diagram (what the system interacts with)
2. Component Diagram (major system components)
3. Data Flow Diagram (how information moves)
4. Deployment Diagram (where components run)
5. Decision Records (why design choices were made)

**Writing Style**:
- Explain the "why" before the "what"
- Use both text and diagrams
- Include security and compliance considerations
- Document constraints and trade-offs
- Explain recovery mechanisms and fail-safes

### API Documentation

**Required Sections Per Endpoint**:
1. Endpoint purpose and legal context
2. Request parameters with type and constraints
3. Response format with examples
4. Error codes and handling procedures
5. Compliance considerations (data protection, audit logging)
6. Rate limiting and usage policies
7. Authentication requirements
8. Example requests and responses

**Example Endpoint Documentation**:
```
## GET /api/documents/{documentId}

### Purpose
Retrieve a single document by its unique identifier. Requires proper
authorization based on user role and document access controls. All accesses
are logged for audit compliance.

### Request Parameters
- `documentId` (string, required): Document unique identifier
- `includeMetadata` (boolean, optional, default: true): Include document
  metadata in response

### Response Format (200 OK)
{
  "id": "doc-uuid",
  "title": "Contract Review",
  "contentHash": "sha256hash",
  "createdAt": "2025-11-19T10:30:00Z",
  "encryptionStatus": "encrypted",
  "accessLevel": "confidential"
}

### Error Responses
- 401 Unauthorized: User authentication failed
- 403 Forbidden: User lacks necessary access permissions
- 404 Not Found: Document does not exist
```

---

## Legal Language Integration

### Legal Terminology

**When Using Legal Terms**:
- Define on first use with non-legal explanation
- Maintain consistency with specific definitions
- Note when terms have technical meanings different from legal meanings
- Provide context for terms that may vary by jurisdiction

**Example**:
```
**Confidential Information** (as used in this documentation): Information
designated as confidential by the document owner, including but not limited
to client names, case details, financial information, and legal strategies.
In the system, this classification determines encryption levels, access
restrictions, and audit logging requirements.

Technical Note: In some systems, "confidential" may refer only to security
classifications. This guide uses "confidential" to include both legal and
security classifications.
```

### Compliance References

**Standard Reference Format**:
```
[Standard Acronym] - [Full Name] ([Year or Edition])
Example: ABA - Cybersecurity and Data Protection Standards (2024)
```

**When Referencing Standards**:
- Include the specific rule or section number
- Provide publication date or edition number
- Explain the specific application to the system
- Update references annually

**Example**:
```
This system implements role-based access controls as required by the ABA
Cybersecurity and Data Protection Standards (2024), Section 5.2.1, which
mandates "implementation of access control policies limiting system access
to authorized users with legitimate business needs."
```

### Regulatory Framework Integration

**Applicable Standards to Reference**:
- American Bar Association (ABA) Standards
- State Bar Association Rules and Opinions
- Model Rules of Professional Conduct
- NIST Cybersecurity Framework
- HIPAA (if applicable)
- GDPR (if applicable to EU users)
- State-specific data protection laws

**Documentation Requirements**:
- Map features to specific compliance obligations
- Document how design choices address standards
- Include disclaimers about jurisdictional variations
- Update documentation when standards change

---

## Ethics Compliance Standards

### Rule of Professional Conduct Integration

**Model Rule 1.1 - Competence**
Documentation must enable lawyers to understand and competently use the system.

Requirements:
- Explain system capabilities and limitations clearly
- Identify situations where lawyer judgment is required
- Document when system capabilities do not replace professional judgment
- Include warnings for common misuses

**Example Warning**:
```
WARNING: Automated Document Classification
The system uses machine learning to classify documents. Classifications must
be verified by qualified legal personnel before relying on them for case
decisions or client communications. System classifications are tools to
assist attorney judgment, not substitutes for attorney analysis. The attorney
remains fully responsible for document classification accuracy and its legal
consequences.
```

### Rule 1.6 - Confidentiality

All documentation must address confidentiality obligations.

Requirements:
- Explain how the system protects client information
- Document data retention and deletion procedures
- Explain audit logging and who can access logs
- Address data breach notification procedures
- Explain backup and disaster recovery protection

### Rule 8.4 - Misconduct

Documentation must not facilitate unethical conduct.

Requirements:
- Clearly document proper use cases only
- Include explicit warnings against improper uses
- Document audit trail capabilities for compliance verification
- Explain monitoring and detection of policy violations
- Reference applicable ethics rules

**Example Documentation**:
```
## Audit Logging (Model Rule 8.4 Compliance)

The system maintains immutable audit logs of all access to confidential
client information. These logs are protected separately from primary data
and cannot be modified or deleted. Logs include:
- Who accessed the information (user identifier)
- When the access occurred (timestamp)
- What information was accessed (document identification)
- How the information was accessed (API endpoint or user interface)

Misuse of this system to access information without legitimate case purposes
constitutes both technical policy violation and potential ethics violation
under Model Rule 8.4 (Misconduct). Regular audit log review is required to
detect and prevent such misuse.
```

### Data Protection and Privacy

**Documentation Must Address**:
- Explicit consent mechanisms for data collection
- Data minimization (collecting only necessary information)
- Purpose limitation (using data only for stated purposes)
- Data retention policies and deletion procedures
- User rights regarding personal data
- Data breach notification procedures
- Compliance with applicable privacy regulations

---

## Code Documentation

### Code Comments Standards

**Comment Purpose**:
- Explain the "why," not the "what"
- Provide context for non-obvious decisions
- Reference compliance requirements
- Explain edge cases and error handling
- Document known limitations

**Examples**:

**Incorrect Comment** (describes what code does, not why):
```javascript
// Loop through documents and check encryption
for (let i = 0; i < documents.length; i++) {
  if (documents[i].encrypted !== true) {
    errors.push("Not encrypted");
  }
}
```

**Correct Comment** (explains why and context):
```javascript
// Verify all documents are encrypted before returning to user.
// This satisfies ABA Cybersecurity Standards Section 5.1.2 requiring
// encryption of all data at rest. The verification is logged for audit
// compliance (Model Rule 1.6). If any document lacks encryption, we fail
// the entire request rather than returning mixed encryption states, which
// could cause attorney misunderstanding of protection level.
for (let i = 0; i < documents.length; i++) {
  if (documents[i].encrypted !== true) {
    logger.warning(`Unencrypted document detected: ${documents[i].id}`);
    errors.push({
      documentId: documents[i].id,
      reason: "encryption_required",
      complianceRule: "ABA-SEC-5.1.2"
    });
  }
}
```

### Function Documentation

**Required Elements**:
1. Clear purpose statement
2. Parameter descriptions with types
3. Return value description
4. Exceptions or error conditions
5. Compliance implications
6. Example usage if non-obvious

**JSDoc Example**:
```javascript
/**
 * Classify a legal document using machine learning.
 *
 * This function applies a trained ML model to automatically classify
 * documents by type (contract, complaint, discovery, etc.). Classifications
 * are provided as suggestions only and MUST be verified by qualified legal
 * personnel before use in legal decisions or client communications.
 *
 * Complies with: ABA Rule 1.1 (competence), Model Rule 8.4 (misconduct prevention)
 *
 * @param {Document} document - The document to classify
 * @param {Object} options - Classification options
 * @param {number} options.confidenceThreshold - Minimum confidence (0-1) to
 *   return classification. Below threshold, classification is suppressed.
 * @param {boolean} options.logClassification - Whether to log this
 *   classification for model improvement (requires explicit consent).
 *
 * @returns {Promise<Classification>} Classification with type and confidence
 *
 * @throws {ValidationError} If document is malformed
 * @throws {AuthorizationError} If user lacks permission to classify this type
 *
 * @example
 * const classification = await classifyDocument(myDocument, {
 *   confidenceThreshold: 0.85,
 *   logClassification: false
 * });
 *
 * if (classification.confidence < 0.95) {
 *   console.warn('Manual review recommended');
 * }
 */
function classifyDocument(document, options = {}) {
  // implementation
}
```

### Inline Documentation

**Use Inline Documentation For**:
- Complex algorithms or logic
- Non-obvious performance optimizations
- Edge cases and error handling paths
- Compliance-critical code
- Security-sensitive operations

**Format**:
```javascript
// [WHY] This explanation of purpose and context
// [HOW] This explanation of the approach
// [COMPLIANCE] Reference to applicable standards
```

---

## User-Facing Content

### Help Documentation

**Structure**:
1. Overview (what the feature does)
2. When to use this feature
3. Step-by-step instructions
4. Example scenarios
5. Common issues and troubleshooting
6. Compliance or legal implications
7. When to escalate to attorney

**Example Help Section**:
```
## Setting Document Access Controls

### What This Does
Access controls determine which team members can view or modify specific
documents. These controls are critical to confidentiality protection and
compliance with your professional responsibility obligations.

### When to Use
Set access controls whenever you create a document containing confidential
client information. Review access controls periodically (recommended
quarterly) to ensure only necessary team members retain access.

### Steps
1. Open the document
2. Click "Share & Permissions"
3. Add team members by email
4. Select permission level for each person:
   - View Only: Can read document only
   - Edit: Can view and modify document
   - Admin: Can view, modify, and change permissions
5. Click "Save Changes"

### Example
For a client contract, you might grant:
- Attorney assigned to case: Admin
- Paralegal supporting case: Edit
- Billing department: View Only
- All others: No access

### Compliance Note
Access control documentation is reviewed during audits and in ethics matters.
Ensure access levels match legitimate business needs and are updated when
roles change. Document your access control decisions, particularly for
sensitive matters.

### Need Help?
If team members frequently need access level changes, consider using
template-based access profiles that match standard roles.
```

### Error Messages

**Error Message Requirements**:
- Use clear, plain language
- Explain what went wrong
- Suggest corrective action when possible
- Avoid technical jargon
- Include reference codes for support escalation

**Example Error Messages**:

**Incorrect Error**:
```
ERROR 403: Access denied to resource
```

**Correct Error**:
```
ERROR SEC-403: You do not have permission to access this document.

Reason: Your role (Paralegal) does not include this case assignment.

Actions:
1. Verify you are assigned to this matter
2. Contact your case supervisor if access is required
3. Contact Support with code SEC-403 if you believe this is incorrect
```

### Consent and Disclosure Language

**Consent Form Requirements**:
- Clear explanation of what user is consenting to
- Specific statement of what data is collected
- Specific statement of how data is used
- Easy opt-out mechanisms
- Option to revoke consent

**Example Consent Language**:
```
## System Usage and Data Consent

By using this system, you consent to the following:

### Data Collection
The system automatically collects:
- Which documents you view and when
- Searches you perform
- System features you use
- Your location and device information

### Data Use
Your data is used to:
- Protect system security and prevent misuse
- Generate audit logs for compliance verification
- Improve system performance and features
- Detect and investigate policy violations

### Your Rights
- You may opt out of non-essential data collection
- You may request access to your personal data collected
- You may request deletion of non-essential data
- You may revoke this consent at any time

To manage your consent choices, see Privacy Settings.
```

---

## Terminology Reference

### Controlled Vocabulary List

**System Terms**:
- **Document**: Any file or text managed by the system (contract, email, memo)
- **Encryption**: Mathematical transformation of data unreadable without correct key
- **Access Control**: Rules determining who may view or modify specific information
- **Audit Log**: Immutable record of system usage for compliance verification
- **Encryption Key**: Digital code required to decrypt encrypted data
- **User Role**: Classification determining access permissions and capabilities
- **Confidential Information**: Information designated as requiring restricted access

**Legal Terms** (as used in this system):
- **Attorney-Client Privilege**: Legal protection preventing disclosure of communications between attorney and client
- **Work Product Doctrine**: Legal protection preventing disclosure of attorney thought processes and strategies
- **Confidential Client Information**: Client data requiring protection from unauthorized disclosure
- **Reasonable Care**: Standard of care required by Model Rules of Professional Conduct

**Do Not Use Synonyms**:
- Always use "access control," never "permissions"
- Always use "encryption," never "scrambling" or "security encoding"
- Always use "audit log," never "activity log" or "system log"
- Always use "Confidential Information," never "sensitive data"

---

## Review and Approval Process

### Internal Review Process

**Required Reviews**:
1. **Technical Review** (Engineering Lead)
   - Accuracy of technical descriptions
   - Alignment with implementation
   - Completeness of specifications

2. **Legal Review** (Compliance Officer or External Counsel)
   - Accuracy of legal references
   - Compliance with applicable standards
   - Appropriateness of disclaimers

3. **User Experience Review** (Product Manager)
   - Clarity for intended audience
   - Completeness of user guidance
   - Appropriateness of tone

4. **Quality Assurance Review** (QA Lead)
   - Testability of requirements
   - Completeness of acceptance criteria
   - Alignment with test plans

### Review Checklist

- [ ] All technical claims are accurate and verifiable
- [ ] All legal references are current and properly cited
- [ ] Compliance requirements are correctly stated
- [ ] Terminology is consistent with controlled vocabulary
- [ ] Accessibility standards are met (WCAG 2.1 AA)
- [ ] All acronyms are defined on first use
- [ ] Tone is appropriate and professional
- [ ] No marketing claims appear in technical documentation
- [ ] All disclaimers are clearly stated
- [ ] Examples are accurate and current
- [ ] Links and references are functional
- [ ] Content is reviewed annually and updated as needed

### Approval Authority

- **Technical Documentation**: Engineering Lead + Compliance Officer
- **User-Facing Content**: Product Manager + Compliance Officer
- **API Documentation**: Engineering Lead + API Designer
- **Compliance-Critical Content**: External Counsel (when significant changes occur)

---

## Examples and Templates

### Documentation Template Structure

**For Features**:
```
## Feature Name

### Overview
[Clear, concise description of what the feature does]

### Why This Matters
[Legal, compliance, or operational importance]

### How to Use
[Step-by-step instructions]

### Examples
[Real-world usage scenarios]

### Compliance Implications
[Relevant standards and rules]

### Limitations and Edge Cases
[What the feature does not do]

### Related Features
[Links to related documentation]
```

### Specification Template

```
# Specification: [Feature Name]

## Overview
[What is being specified and why]

## Requirements
[Mandatory requirements with "shall" or "must"]

## Constraints
[Limitations and edge cases]

## Compliance References
[Applicable standards and rules]

## Acceptance Criteria
[How to verify the specification is met]

## Implementation Notes
[Technical guidance for developers]
```

---

## Version History and Maintenance

**Document Updates Required When**:
- New compliance standards are adopted
- Applicable laws or rules change
- Significant system features are added
- Ethics opinions are issued affecting functionality
- User feedback indicates confusion or misuse

**Update Process**:
1. Identify needed changes
2. Draft updated content
3. Route through review process
4. Update version number
5. Document changes in version history
6. Notify affected teams
7. Archive previous version

**Annual Review Schedule**:
- Q1: Review compliance references and standards
- Q2: Review technical content accuracy
- Q3: Review user-facing documentation
- Q4: Comprehensive review of all documentation

---

## Enforcement and Training

### Compliance Expectations

- All documentation created by engineers and technical writers must follow this guide
- All documentation must pass review before publication
- Documentation quality is part of code review requirements
- Documentation deficiencies are tracked and addressed

### Training Requirements

- All technical staff receive training on this guide annually
- New hires receive training within first two weeks
- Technical writers complete advanced certification annually
- Compliance officers audit documentation quarterly

### Non-Compliance Consequences

- Technical review rejection until standards are met
- Delay in feature release until documentation is approved
- Performance impact if repeated violations occur
- Potential compliance violation if ethics standards are violated

---

## Contact and Support

**Documentation Questions**:
- Contact: [Documentation Lead]
- Email: [documentation@example.com]
- Slack: #documentation-standards

**Compliance Questions**:
- Contact: [Compliance Officer]
- Email: [compliance@example.com]

**Updates and Changes**:
- Subscribe to: [Documentation Updates mailing list]
- Review: [Quarterly compliance update meetings]

---

**END OF DOCUMENT**

*This guide is a living document subject to periodic updates. Last comprehensive review: November 2025. Next scheduled review: November 2026.*
