# Privilege Review Workflows and Best Practices

## Overview

Privilege review is one of the most critical and expensive aspects of e-discovery. Inadvertent disclosure can waive privilege, while over-designation wastes resources. This guide provides comprehensive workflows for efficient, defensible privilege review.

## Privilege Fundamentals

### Types of Privilege

**Attorney-Client Privilege**: Communications between attorney and client for legal advice
**Work Product Doctrine**: Materials prepared in anticipation of litigation
**Other Privileges**: Physician-patient, spousal, clergy-penitent (context-dependent)

### Privilege Requirements

**Attorney-Client** (must have all):
1. Communication between attorney and client
2. Made in confidence
3. For purpose of obtaining/providing legal advice
4. Not waived

**Work Product**:
1. Prepared by/for attorney
2. In anticipation of litigation
3. Contains mental impressions, conclusions, opinions (higher protection)

### Waiver Considerations

**Intentional Waiver**: Voluntary disclosure
**Inadvertent Waiver**: Accidental production
**Subject Matter Waiver**: Waiving privilege on topic may waive for all related communications
**Fed. R. Evid. 502**: Protections against inadvertent waiver

## Privilege Review Workflow

### Phase 1: Preparation

**Identify Attorney Names and Domains**:
- In-house legal department attorneys
- External law firms
- Email domains (@lawfirm.com)
- Common attorney email patterns

**Create Privilege Term Lists**:
- "Attorney-client privilege"
- "Privileged and confidential"
- "Legal advice"
- "Work product"
- Attorney names
- Law firm names

**Set Up Review Platform**:
- Privilege coding fields
- Privilege log fields
- Segregated privilege workspace (optional)
- Privilege-specific batching

### Phase 2: Initial Screening (Automated)

**Email Domain Filtering**:
```
Create saved search:
Email From: *@lawfirm.com OR Email To: *@lawfirm.com
Flag for privilege review
```

**Attorney Name Filtering**:
```
Search: (Author:("Jane Smith" OR "John Attorney") OR
         Email From/To contains attorney names)
```

**Privilege Term Search**:
```
Text search: "attorney client privilege" OR 
             "privileged and confidential" OR
             "work product" OR "legal advice"
```

**TAR for Privilege** (Advanced):
- Train separate privilege model
- Prioritize likely privileged documents
- Saves 30-50% privilege review time

**Result**: "Potentially Privileged" batch of documents

### Phase 3: First-Pass Privilege Review

**Reviewer Qualifications**:
- Experienced attorneys (not contract attorneys typically)
- Trained on privilege principles
- Understand case context

**Review Process**:
1. Review each "Potentially Privileged" document
2. Apply privilege codes:
   - **Privileged**: Clearly privileged, withhold
   - **Not Privileged**: No privilege, continue to responsiveness review
   - **Potentially Privileged**: Unclear, escalate
3. For privileged documents, complete privilege log fields
4. Provide brief reasoning for privilege assertion

**Privilege Coding Fields**:
- **Privilege Type**: Attorney-Client / Work Product / Both
- **Privilege Holder**: Client name or entity
- **Author**: Document author
- **Recipients**: Document recipients
- **Date**: Document date
- **Description**: Brief description for log
- **Basis**: Reason for privilege assertion

**Efficiency Tips**:
- Review email families together
- Use bulk coding for obvious privilege (law firm letterhead)
- Create privilege "families" (email thread is all privileged)

### Phase 4: Quality Control

**QC Sampling**:
- 10-20% random sample of privilege assertions
- Review by senior attorney
- Check for false positives (over-designation)
- Check for false negatives (missed privilege)

**Common False Positives**:
- Business advice from attorneys
- Attorneys acting in business role
- CC'd attorney on non-legal business matters
- Legal department in FYI capacity

**Common False Negatives**:
- Client seeking legal advice without using "legal" keywords
- In-house counsel email from personal account
- Implicit requests for legal advice
- Draft agreements prepared by attorneys

**Overturn Process**:
- Document QC overturns
- Provide feedback to reviewers
- Re-train if systematic errors
- Adjust automated screening if needed

### Phase 5: Privilege Log Preparation

**Standard Privilege Log Fields** (per Fed. R. Civ. P. 26(b)(5)):
- Document ID / Bates range
- Date
- Author(s)
- Recipient(s)
- CC'd parties
- Document type (email, memo, letter)
- Brief description
- Privilege basis (attorney-client, work product, both)

**Log Generation**:
```
Export privilege-coded documents to Excel:
- Filter: Privilege = "Privileged"
- Fields: All privilege log fields
- Group by email thread (optional)
- Format for production
```

**Description Guidelines**:
- Generic enough to not waive privilege
- Specific enough to allow challenge evaluation
- Typical: "Email from Client X to Attorney Y regarding legal advice on [topic]"
- Avoid: Detailed substance of communication

**Sample Privilege Log Entry**:
```
Bates    Date        Author       Recipients       Type    Description                              Privilege Basis
----------------------------------------------------------------------------------------------------------------------
ACME001  01/15/2024  J. Smith     A. Attorney      Email   Email from J. Smith to outside counsel  Attorney-Client
                     (Client)     (Law Firm LLP)           seeking legal advice regarding 
                                                            Widget contract dispute
```

### Phase 6: Privilege Disputes

**Challenging Party Process**:
1. Identify log entries to challenge
2. File motion to compel
3. Court may require in camera review

**Producing Party Process**:
1. Respond to challenges
2. Provide additional information if needed
3. Produce privilege log supplement
4. Defend privilege assertions

**In Camera Review**:
- Court reviews disputed documents privately
- Determines if privilege applies
- Ruling on disclosure

## Advanced Privilege Techniques

### Privilege Screening with TAR

**Methodology**:
1. Create privilege training set (500-1,000 documents)
2. Senior attorney codes for privilege
3. Algorithm learns privilege indicators
4. Rank documents by privilege likelihood
5. Prioritize review of high-scoring documents

**Benefits**:
- 40-60% reduction in privilege review scope
- Focus attorney time on likely privileged documents
- Defensible methodology

**Implementation** (Relativity Active Learning):
```
1. Create "Privilege" field (Yes/No)
2. Set up Active Learning project for privilege (separate from responsiveness)
3. Review algorithm-prioritized documents
4. Stop when diminishing returns (few privileged docs in recent batches)
5. Sample validate low-scoring documents
```

### Email Thread Privilege Analysis

**Approach**:
- If any email in thread is privileged, mark entire thread
- More conservative but efficient
- Maintains context and conversation flow

**Alternative**:
- Review each email individually
- More time-consuming but precise
- Necessary if thread has mixed participants

### Clawback Procedures

**Fed. R. Evid. 502(b)** - Inadvertent Disclosure Protection:

**Requirements** (all must be met):
1. Disclosure was inadvertent
2. Privilege holder took reasonable steps to prevent disclosure
3. Holder promptly took reasonable steps to rectify error

**Clawback Agreement** (negotiate pre-production):
```
The parties agree that inadvertent production of privileged materials
does not constitute waiver. Receiving party shall:
1. Promptly notify producing party upon discovery
2. Return, sequester, or destroy material and copies
3. Not use or disclose material pending resolution
4. Delete from any databases or systems

Producing party shall:
1. Confirm privilege claim in writing within 10 business days
2. Provide privilege log entry for withheld document
3. Bear costs of retrieval and deletion
```

**Fed. R. Evid. 502(d) Order** - Court Order Protection:
- Seek court order that inadvertent disclosures don't waive privilege
- Order protects against waiver in all jurisdictions
- Strongest protection
- Include in case management order or protective order

### Quick Peek Agreements

**Concept**: Receiving party reviews documents without formal production

**Benefits**:
- Producing party retains control
- Receiving party identifies relevant documents early
- Privilege review deferred until relevance determined
- Reduces privilege review of non-relevant documents

**Process**:
1. Producing party provides access to documents (without privilege review)
2. Receiving party identifies relevant documents
3. Producing party performs privilege review only on relevant set
4. Formal production of non-privileged relevant documents

**Agreement Terms**:
- Access does not constitute production
- No waiver for viewing documents
- Receiving party may not use or cite documents until formal production
- Producing party performs privilege review after relevance determination

## Privilege Review Cost Management

### Cost Analysis

**Traditional Privilege Review**:
```
Documents to review: 500,000
Potentially privileged (10%): 50,000
Attorney rate: $150/hour
Review rate: 25 docs/hour
Hours: 2,000
Cost: $300,000
```

**Optimized Privilege Review**:
```
Automated screening (60% reduction): 20,000 potentially privileged
TAR prioritization (40% further reduction): 12,000 priority review
Attorney rate: $150/hour
Review rate: 30 docs/hour (prioritized, similar documents)
Hours: 400
Cost: $60,000
Savings: $240,000 (80%)
```

### Efficiency Strategies

1. **Automated Pre-Screening**: 50-70% reduction
2. **TAR for Privilege**: 30-50% additional reduction
3. **Tiered Review**: Junior attorneys first pass, senior review escalations
4. **Bulk Coding**: Law firm correspondence, clear privilege indicators
5. **Thread-Level Review**: Review conversations, not individual emails
6. **Sampling**: If low privilege rate (<1%), sample and extrapolate

## Common Privilege Issues

### Issue: Business vs. Legal Advice

**Test**: Primary purpose of communication

**Business Advice** (Not Privileged):
- Strategic business recommendations
- Operational guidance
- Commercial decisions
- Attorney in business role

**Legal Advice** (Privileged):
- Interpretation of law
- Legal risks and exposure
- Litigation strategy
- Regulatory compliance advice

**Mixed Communications**: Apply privilege if primary purpose is legal advice

### Issue: In-House Counsel Dual Roles

**Challenge**: In-house attorneys often wear business and legal hats

**Analysis**:
- Was attorney acting as legal advisor or business executive?
- Was communication seeking/providing legal advice?
- Context and subject matter

**Best Practice**: In-house counsel should clearly label legal advice communications

### Issue: Third Parties on Communications

**General Rule**: Presence of third parties can waive privilege

**Exceptions**:
- Third party necessary for legal representation (expert, translator)
- Third party is agent of client or attorney
- Common interest/joint defense agreements

**Example**:
- Client + Attorney + Outside Consultant: May waive privilege
- Client + Attorney + Client's Employee: Likely privileged (employee is agent)
- Client + Attorney + Co-Defendant + Their Attorney: Joint defense privilege

### Issue: Crime-Fraud Exception

**Rule**: No privilege for communications furthering crime or fraud

**Requirements**:
1. Client was engaged in or planning crime/fraud
2. Attorney's services were obtained in furtherance
3. Prima facie showing required

**Red Flags**:
- Discussions of illegal activity
- Concealment schemes
- Sham transactions
- Attorney knowledge of fraud

**Response**: Careful review, possible in camera submission

## Privilege Log Best Practices

### Categorical Logs

**When Appropriate**:
- Large numbers of similar documents
- Court permits categorical description
- Reduces burden while allowing challenges

**Example**:
```
Documents 1-250: Emails between Client and Outside Counsel (Law Firm LLP)
dated January 2020 - December 2023, regarding legal advice on Widget
contract dispute. All withheld on basis of attorney-client privilege.
```

### Privilege Log Deficiencies to Avoid

**Common Errors**:
- Insufficient description (too generic)
- Revealing privileged content (too specific)
- Missing required fields (author, recipient, date)
- Inconsistent privilege assertions
- Including non-privileged documents

**Court Sanctions for Deficient Logs**:
- Deemed waiver of privilege
- Order to produce log supplement
- Cost-shifting for re-review
- Adverse inference

### Log Supplements

**When Required**:
- Discovery of additional privileged documents
- Correction of errors in original log
- Response to challenges

**Process**:
1. Prepare supplement with new entries
2. Clearly mark as "Supplement"
3. Cross-reference to original log
4. Serve on all parties

## Technology Solutions

### Privilege Review Platforms

**Features**:
- Privilege coding fields
- Email threading for privilege families
- Automated attorney name detection
- Privilege log generation
- Quality control workflows

**Top Platforms**:
- Relativity (privilege workflow tools)
- Everlaw (automated privilege detection)
- Disco (AI-powered privilege screening)
- Brainspace (privilege analytics)

### Privilege Automation Tools

**Metadata Extraction**:
- Automatically identify attorney email domains
- Extract names from signature blocks
- Parse email headers for attorney names

**Pattern Recognition**:
- Detect privilege headers/footers
- Identify law firm letterhead
- Flag privilege keywords

**Machine Learning**:
- Train on known privileged documents
- Predict privilege for new documents
- Continuous learning

## Conclusion

Effective privilege review requires a combination of legal expertise, technology, and efficient workflows. By implementing automated screening, TAR prioritization, quality control, and clear procedures, organizations can reduce privilege review costs by 50-80% while maintaining defensibility. Key to success is early planning, appropriate use of technology, and rigorous quality control to avoid inadvertent waiver or over-designation.
