# PEP Screening Implementation Guide

## Overview

PEP (Politically Exposed Person) screening identifies individuals holding or having held prominent public positions and determines enhanced due diligence requirements.

## PEP Categories

**Tier 1: Direct PEPs**
- Current heads of state/government
- Government ministers
- Central bank governors
- Constitutional court judges
- Military commanders (senior)
- Senior parliamentary members (>1/3)

**Tier 2: Senior Officials**
- Senior government officials
- State-owned enterprise managers
- High-ranking military/police
- Supreme court judges
- Senior international organization officials

**Tier 3: Family of PEPs**
- Spouse/domestic partner
- Children and their spouses
- Parents and grandparents
- Siblings
- Close associates

## Implementation Steps

1. **PEP Database Selection**
   - Commercial providers (Refinitiv, Lexis Nexis)
   - Government PEP lists
   - International databases
   - Regular updates (daily/weekly)

2. **Screening Procedures**
   - Real-time screening on account opening
   - Periodic rescreening (annual minimum)
   - Beneficial owner screening
   - Transaction party screening

3. **Enhanced Due Diligence Procedures**
   - Increased documentation requirements
   - Senior management approval
   - Enhanced ongoing monitoring
   - Source of wealth verification
   - Transaction purpose clarification

4. **Decision Making**
   - Approved (with monitoring)
   - Manual review required
   - Require enhanced documentation
   - Decline relationship
   - Report to authorities (if applicable)

## Screening Accuracy

- Match confidence thresholds: > 95% for automatic match
- Manual review: 85-95% confidence
- Name variations and transliterations
- DOB verification
- Jurisdiction confirmation

## Performance Metrics

- Coverage: 100% of customers
- Screening latency: < 500ms
- Accuracy: > 99% precision
- False positive rate: < 5%
- Processing cost: < $1/screening

## Best Practices

1. **Fuzzy Matching** - Account for name variations
2. **Multi-Factor Verification** - Use DOB, country, position
3. **Regular Updates** - Daily PEP list updates
4. **Ongoing Monitoring** - Check for PEP status changes
5. **Documentation** - Document all PEP matches and decisions
6. **Training** - Staff awareness of PEP risks
7. **Escalation** - Clear procedures for confirmed matches

## Regulatory Requirements

- FATF Recommendation 12: PEP identification
- Enhanced due diligence mandatory for PEPs
- Family member and associate screening
- Transaction monitoring
- Ongoing review procedures
- Documentation and reporting requirements
