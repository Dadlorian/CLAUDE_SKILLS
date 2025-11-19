# Business Associate Agreement (BAA) Requirements Reference

## Overview

A Business Associate Agreement (BAA) is a written contract between a covered entity and a business associate that specifies how protected health information (PHI) will be used, disclosed, and safeguarded.

**Legal Requirement:** 45 CFR §164.308(b)(1), §164.314(a), §164.502(e), §164.504(e)

## Who Needs a BAA?

### Business Associate Definition (§160.103)

A person or entity that:
1. Performs functions or activities on behalf of, or provides services to, a covered entity
2. Those functions/services involve the use or disclosure of PHI
3. Is not part of the covered entity's workforce

### Common Business Associates

**Healthcare Services:**
- Medical billing companies
- Claims processing services
- Practice management companies
- Pharmacy benefit managers
- Medical transcription services
- Patient safety organizations
- Health information exchanges (HIEs)

**Professional Services:**
- Law firms (handling PHI)
- Accounting firms (handling PHI)
- Consultants (accessing PHI)
- Benefits administrators
- Actuaries

**Technology Services:**
- Cloud storage providers (hosting ePHI)
- SaaS vendors (processing ePHI)
- IT support companies (accessing systems with ePHI)
- Data analytics companies
- Electronic health record vendors
- Email encryption services
- Backup and disaster recovery services

**Administrative Services:**
- Medical record shredding companies
- Document storage companies
- Courier services (transporting PHI)
- Collection agencies

**Subcontractors:**
- Any entity that creates, receives, maintains, or transmits PHI on behalf of a business associate

### Who Does NOT Need a BAA?

**Conduit Exception:**
- Telecommunications providers (providing only transmission services)
- US Postal Service
- Internet service providers (ISP) providing only data transmission
- **Key:** No access to PHI other than transient basis

**Other Exceptions:**
- Covered entity-to-covered entity disclosures for TPO (unless one acts as BA)
- Workforce members (employees covered by workforce policies)
- Organized healthcare arrangements among members

## Required BAA Provisions

### 1. Permitted and Required Uses and Disclosures (§164.504(e)(2)(i))

**Permitted Uses:**
- Only as permitted by the contract
- As required by law

**Permitted Disclosures:**
- Only as permitted by the contract
- As required by law

**Prohibited:**
- Use or disclosure not permitted by contract or required by law

**Template Language:**
```
Business Associate shall not use or disclose Protected Health Information other
than as permitted or required by this Agreement or as Required by Law.

Business Associate may use Protected Health Information for the proper
management and administration of Business Associate or to carry out its legal
responsibilities.

Business Associate may disclose Protected Health Information for the proper
management and administration of Business Associate or to carry out its legal
responsibilities, provided that:
(a) The disclosure is Required by Law; or
(b) Business Associate obtains reasonable assurances from the person to whom
the information is disclosed that it will be held confidentially and used or
further disclosed only as Required by Law or for the purpose for which it was
disclosed to the person, and the person notifies Business Associate of any
instances of which it is aware in which the confidentiality of the information
has been breached.
```

### 2. Safeguards (§164.504(e)(2)(ii)(B))

**Requirement:**
Implement appropriate safeguards to prevent unauthorized use or disclosure of PHI.

**Specifics:**
- Administrative safeguards
- Physical safeguards
- Technical safeguards (for ePHI)
- Comply with Security Rule requirements (§164.308, §164.310, §164.312)

**Template Language:**
```
Business Associate shall implement appropriate safeguards to prevent use or
disclosure of Protected Health Information other than as provided for by this
Agreement, including implementing administrative, physical, and technical
safeguards that reasonably and appropriately protect the confidentiality,
integrity, and availability of electronic Protected Health Information that it
creates, receives, maintains, or transmits on behalf of Covered Entity, as
required by 45 CFR Part 164, Subpart C.
```

### 3. Breach Reporting (§164.504(e)(2)(ii)(C))

**Requirement:**
Report any security incident or breach to covered entity.

**Timeline:**
- Without unreasonable delay
- No later than 60 days from discovery
- **Best Practice:** Much sooner (within days or immediately for serious breaches)

**Information to Include:**
- Identification of affected individuals
- Date of breach
- Date of discovery
- Nature and extent of breach
- Types of PHI involved
- Any mitigation already undertaken

**Template Language:**
```
Business Associate shall report to Covered Entity any use or disclosure of
Protected Health Information not provided for by this Agreement, including
breaches of unsecured Protected Health Information as required by 45 CFR
§164.410, and any Security Incident of which it becomes aware.

Such reports shall be made without unreasonable delay and in no case later than
sixty (60) calendar days after discovery. Business Associate shall provide
sufficient information to allow Covered Entity to meet its obligations under
45 CFR §164.404, §164.406, and §164.408.
```

### 4. Subcontractor Agreements (§164.504(e)(2)(ii)(D))

**Requirement:**
Ensure subcontractors agree to same restrictions and conditions as BA.

**Subcontractor:**
Any person or entity to whom BA discloses PHI received from, or created/received on behalf of, covered entity.

**Obligation:**
Written agreement with same protections as CE-BA agreement.

**Template Language:**
```
Business Associate shall ensure that any subcontractors that create, receive,
maintain, or transmit Protected Health Information on behalf of Business
Associate agree to the same restrictions and conditions that apply to Business
Associate with respect to such information, including implementing reasonable
and appropriate safeguards to protect it.

Business Associate shall enter into a written agreement with each subcontractor
that meets the requirements of 45 CFR §164.504(e) and §164.314(a).
```

### 5. Individual Access (§164.504(e)(2)(ii)(E))

**Requirement:**
Provide access to PHI to covered entity or individual as needed for CE to meet access obligations.

**Timeline:**
- Within 30 days of request
- Extension of up to 30 days permissible

**Format:**
- Form and format requested (if readily producible)
- Electronic if maintained electronically

**Template Language:**
```
Business Associate shall, to the extent Business Associate maintains Protected
Health Information in a Designated Record Set, make available such information
to Covered Entity (or, as directed by Covered Entity, to an Individual) within
thirty (30) days for Covered Entity to fulfill its obligations under 45 CFR
§164.524.

Business Associate shall provide such information in the time, manner, and
format designated by Covered Entity, if readily producible in such form and
format, or otherwise in a readable hard copy or electronic format as agreed to
by Covered Entity and Business Associate.
```

### 6. Amendment Rights (§164.504(e)(2)(ii)(F))

**Requirement:**
Allow amendment of PHI as needed for CE to meet amendment obligations.

**Process:**
- Accept amendments from CE
- Incorporate into records maintained
- Provide to others who received PHI if directed

**Template Language:**
```
Business Associate shall, to the extent Business Associate maintains Protected
Health Information in a Designated Record Set, make any amendment(s) to
Protected Health Information that Covered Entity directs or agrees to pursuant
to 45 CFR §164.526 within thirty (30) days of receipt of such direction or
agreement.

Business Associate shall provide information to Covered Entity to allow Covered
Entity to fulfill its obligations under 45 CFR §164.526, including providing
information to enable Covered Entity to respond to a request for amendment.
```

### 7. Accounting of Disclosures (§164.504(e)(2)(ii)(G))

**Requirement:**
Document and provide information on disclosures to enable CE to provide accounting.

**Information Needed:**
- Date of disclosure
- Name of recipient
- Brief description of PHI
- Purpose of disclosure

**Retention:**
- Minimum 6 years

**Template Language:**
```
Business Associate shall maintain and make available to Covered Entity
information required to provide an accounting of disclosures as necessary for
Covered Entity to fulfill its obligations under 45 CFR §164.528.

Such information shall include:
(a) The date of the disclosure;
(b) The name of the entity or person who received the Protected Health
Information, and, if known, the address;
(c) A brief description of the Protected Health Information disclosed; and
(d) A brief statement of the purpose of the disclosure.

Business Associate shall provide such information within thirty (30) days of a
request by Covered Entity.
```

### 8. Internal Practices, Books, and Records (§164.504(e)(2)(ii)(H))

**Requirement:**
Make internal practices, books, and records available to HHS for compliance determination.

**Access:**
- HHS has right to access
- BA must cooperate with investigations/audits
- Provide documentation when requested

**Template Language:**
```
Business Associate shall make its internal practices, books, and records
relating to the use and disclosure of Protected Health Information available to
the Secretary of the U.S. Department of Health and Human Services for purposes
of determining Covered Entity's compliance with the HIPAA Privacy and Security
Rules.
```

### 9. Return or Destruction of PHI (§164.504(e)(2)(ii)(I))

**Requirement:**
At termination of contract, return or destroy all PHI received from or created/received on behalf of CE.

**Options:**
1. **Return:** All PHI in all forms
2. **Destroy:** If agreed upon and feasible
3. **Retain:** If required by law (with protections)

**Timeframe:**
- Promptly after termination
- Reasonable period specified in agreement

**Template Language:**
```
Upon termination of this Agreement, Business Associate shall:

(a) Return to Covered Entity or, if agreed to by Covered Entity, destroy all
Protected Health Information received from Covered Entity, or created,
maintained, or received by Business Associate on behalf of Covered Entity, that
Business Associate still maintains in any form, and retain no copies; OR

(b) If return or destruction is not feasible, extend the protections of this
Agreement to the information and limit further uses and disclosures to those
purposes that make the return or destruction of the information infeasible.

Business Associate shall complete such return or destruction as promptly as
feasible, but in no event later than thirty (30) days after the effective date
of termination.
```

### 10. Termination for Breach (§164.504(e)(2)(iii))

**Requirement:**
Authorize CE to terminate contract if BA breaches material provision.

**Process:**
- CE provides written notice of breach
- Opportunity for BA to cure (if feasible)
- Termination if not cured or cure not feasible
- Report to HHS if termination not feasible

**Template Language:**
```
Covered Entity may terminate this Agreement immediately if Covered Entity
determines that Business Associate has violated a material term of this
Agreement.

If Covered Entity learns of a pattern of activity or practice of Business
Associate that constitutes a material breach or violation of this Agreement,
Covered Entity shall either:

(a) Take reasonable steps to cure the breach or end the violation, and if such
steps are unsuccessful, terminate this Agreement; OR

(b) If termination is not feasible, report the problem to the Secretary of the
U.S. Department of Health and Human Services.
```

## Additional Recommended Provisions

### 1. Security Incident Definition

Define what constitutes a reportable security incident vs. routine security events.

### 2. Data Ownership

Clarify that CE retains ownership of all PHI.

### 3. Minimum Necessary

BA will request and use only minimum necessary PHI.

### 4. Training Requirements

BA will train workforce on HIPAA requirements.

### 5. Indemnification

Protection for CE from BA's violations (subject to negotiation).

### 6. Insurance Requirements

Cyber liability and other insurance coverage requirements.

### 7. Audit Rights

CE's right to audit BA's HIPAA compliance.

### 8. Security Standards

Specific technical requirements (encryption, access controls, etc.).

### 9. Business Continuity

BA's obligations for disaster recovery and business continuity.

### 10. Notice of Legal Processes

BA will notify CE of subpoenas, warrants, or other legal demands for PHI.

## BAA Workflow

### 1. Identification
- Identify all business associates
- Document relationship and PHI use
- Maintain BA inventory

### 2. Assessment
- Assess BA's HIPAA compliance capabilities
- Review BA's security practices
- Evaluate risk level
- Conduct due diligence

### 3. Negotiation
- Use template as starting point
- Include all required provisions
- Add additional protections as needed
- Legal review of contract

### 4. Execution
- Both parties sign agreement
- Obtain fully executed copy
- Store securely
- Add to BA tracking system

### 5. Ongoing Management
- Monitor BA performance
- Conduct periodic assessments
- Review and update agreements
- Address issues promptly
- Maintain documentation

### 6. Termination
- Follow termination procedures
- Ensure PHI return/destruction
- Obtain certification of destruction
- Remove access to systems
- Update BA inventory

## BAA Template Structure

```
BUSINESS ASSOCIATE AGREEMENT

This Business Associate Agreement ("Agreement") is entered into as of
[DATE] ("Effective Date") by and between [COVERED ENTITY NAME] ("Covered
Entity") and [BUSINESS ASSOCIATE NAME] ("Business Associate").

RECITALS

WHEREAS, Covered Entity is a [type of covered entity];

WHEREAS, Business Associate provides [description of services] to Covered
Entity;

WHEREAS, such services may involve the use or disclosure of Protected Health
Information;

WHEREAS, the parties intend to comply with the requirements of the Health
Insurance Portability and Accountability Act of 1996, as amended;

NOW, THEREFORE, in consideration of the mutual covenants contained herein
and other good and valuable consideration, the parties agree as follows:

1. DEFINITIONS
[Define terms used in agreement]

2. OBLIGATIONS OF BUSINESS ASSOCIATE
2.1 Permitted Uses and Disclosures
2.2 Safeguards
2.3 Breach Reporting
2.4 Subcontractors
2.5 Access to PHI
2.6 Amendment of PHI
2.7 Accounting of Disclosures
2.8 Governmental Access
2.9 Minimum Necessary
2.10 HIPAA Compliance

3. OBLIGATIONS OF COVERED ENTITY
3.1 Notices and Authorizations
3.2 Permissible Requests
3.3 Notice of Privacy Practices Changes

4. TERM AND TERMINATION
4.1 Term
4.2 Termination for Cause
4.3 Effect of Termination
4.4 Survival

5. MISCELLANEOUS
5.1 Regulatory References
5.2 Amendment
5.3 Interpretation
5.4 Indemnification
5.5 No Third-Party Beneficiaries
5.6 Notice
5.7 Severability
5.8 Entire Agreement

SIGNATURES
```

## Common BAA Mistakes to Avoid

### 1. Missing BAAs
- Not identifying all BAs
- Assuming vendor is not a BA
- Overlooking subcontractors

### 2. Inadequate Provisions
- Missing required elements
- Vague language
- No breach notification timeline
- No termination rights

### 3. Outdated Agreements
- Pre-HITECH provisions
- No breach notification
- No subcontractor requirements
- Missing Security Rule references

### 4. No Monitoring
- Signing and forgetting
- Not assessing BA compliance
- Not reviewing periodically
- Ignoring red flags

### 5. Poor Documentation
- No signed copy retained
- No BA inventory
- No assessment documentation
- No monitoring records

## Due Diligence Questions for BAs

### Technical Security
1. Do you encrypt PHI at rest and in transit?
2. What encryption standards do you use?
3. Do you conduct regular vulnerability scans and penetration testing?
4. Do you have audit logging and monitoring?
5. Do you have intrusion detection/prevention systems?

### Administrative
6. Do you conduct annual security risk assessments?
7. Do you have HIPAA policies and procedures?
8. Do you provide HIPAA training to your workforce?
9. Do you have a designated security official?
10. Do you have an incident response plan?

### Physical
11. Where is data stored physically?
12. What physical security controls are in place?
13. How do you dispose of hardware and media?
14. Do you have facility access controls?

### Business Continuity
15. Do you have a disaster recovery plan?
16. How often do you test backups?
17. What are your RTOs and RPOs?
18. Do you have redundant systems?

### Compliance
19. Have you had any HIPAA violations or breaches?
20. Have you been audited by OCR?
21. Do you have cyber liability insurance?
22. Can you provide evidence of HIPAA compliance (certifications, audits)?

### Subcontractors
23. Do you use subcontractors?
24. Do you have BAAs with all subcontractors?
25. How do you monitor subcontractor compliance?

## Regulatory Citations

- 45 CFR §160.103 - Definitions
- 45 CFR §164.308(b) - Business associate contracts and other arrangements
- 45 CFR §164.314(a) - Business associate contracts (Security Rule)
- 45 CFR §164.502(e) - Standard: Disclosures to business associates
- 45 CFR §164.504(e) - Implementation specifications: Business associate contracts

## Additional Resources

- HHS Sample Business Associate Agreement Provisions
- OCR Business Associate Guidance
- Business Associate Checklist
- Subcontractor Agreement Templates
