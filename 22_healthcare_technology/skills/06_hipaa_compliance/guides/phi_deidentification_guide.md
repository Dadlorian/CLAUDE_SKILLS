# PHI De-identification Guide

## De-identification Methods

### Safe Harbor Method (§164.514(b)(2))

Remove all 18 identifiers:
1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year) 
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers/serial numbers
13. Device identifiers/serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photographs
18. Any other unique identifying number/characteristic/code

**PLUS:** No actual knowledge information could identify individual

### Expert Determination Method (§164.514(b)(1))

Qualified statistical/scientific expert determines risk of identification is very small.

**Requirements:**
- Expert has appropriate knowledge and experience
- Applies statistical/scientific principles
- Documents methods and results
- Determines risk very small
- Risk individual could be identified very small
- Risk could be identified when combined with other available information very small

## Limited Data Set (§164.514(e))

Partially de-identified information for research, public health, or healthcare operations.

**May Retain:**
- City, state, ZIP code
- Dates (including DOB)
- Ages (including >89)

**Must Remove All Other Identifiers**

**Requires:** Data Use Agreement

## De-identification Process

**Step 1: Identify Identifiers**
- Scan data for all 18 identifiers
- Document what is present

**Step 2: Choose Method**
- Safe Harbor (simpler)
- Expert Determination (retains more data utility)
- Limited Data Set (if appropriate)

**Step 3: Remove/Redact Identifiers**
- Automated tools for large datasets
- Manual review for accuracy
- Replace with generic values or remove entirely

**Step 4: Validate**
- Review sample records
- Verify all identifiers removed
- Check for indirect identifiers

**Step 5: Document**
- Method used
- Person performing
- Date completed
- Validation results
- Expert determination (if used)

## Common De-identification Techniques

**Suppression:**
- Remove data element entirely
- Example: Remove all names

**Generalization:**
- Replace specific value with broader category
- Example: Age 47 → Age range 40-49
- Example: ZIP 90210 → ZIP 902**

**Pseudonymization:**
- Replace identifier with code
- Maintain lookup table separately
- Example: Patient → ID 12345

**Date Shifting:**
- Offset dates by random amount
- Maintain relative relationships
- Example: All dates shifted +/- 90 days

**Aggregation:**
- Combine data into groups
- Report statistics only
- No individual-level data

## Tools and Software

**Commercial:**
- Privacy Analytics
- Privitar
- ARX Data Anonymization Tool
- Oracle Data Masking

**Open Source:**
- ARX (free)
- μ-ARGUS
- sdcMicro (R package)

**Manual:**
- Find/Replace in documents
- SQL UPDATE statements
- Spreadsheet formulas

## Use Cases

**Research:**
- Limited Data Set with DUA
- De-identified for unrestricted use
- Institutional Review Board oversight

**Public Health:**
- Reportable diseases (identifiable)
- Epidemiological studies (de-identified)
- Population health analytics

**Quality Improvement:**
- Internal QI (identifiable allowed)
- External benchmarking (de-identify)
- Publication (fully de-identify)

**Business Analytics:**
- Vendor analytics (BAA required unless de-identified)
- Marketing analysis (de-identify)
- Operational metrics (aggregate)

## Re-identification Risk

**Assess Risk:**
- Uniqueness of remaining attributes
- Availability of external data sources
- Motivation for re-identification
- Legal protections

**Mitigation:**
- Additional generalization
- Data access controls
- Data use agreements
- Security safeguards

## Regulatory Citations
- 45 CFR §164.514(a) - De-identification standard
- 45 CFR §164.514(b) - Implementation specifications
- 45 CFR §164.514(e) - Limited data set

## Best Practices
1. Use Safe Harbor when possible (clear standard)
2. Document de-identification process
3. Validate sample after de-identification
4. Retain mapping (if pseudonymization) securely
5. Apply appropriate method for use case
6. Consider re-identification risk
7. Update as data changes
8. Train staff on de-identification
9. Have policies and procedures
10. Periodic expert review

