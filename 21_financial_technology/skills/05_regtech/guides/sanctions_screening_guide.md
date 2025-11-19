# Sanctions Screening Implementation Guide

## Quick Start

**Objective**: Implement real-time sanctions and PEP screening for AML compliance.

**Key Deliverables**:
- Automated screening system for new accounts
- Transaction screening for money transfers
- PEP identification and monitoring
- False positive management procedures

## Implementation Checklist

### Pre-Implementation (Week 1-2)

```
☐ Select screening vendor (Refinitiv, ComplyAdvantage, etc.)
☐ Negotiate SLA and pricing
☐ Establish API integration requirements
☐ Create testing environment
☐ Document current customer/transaction data
☐ Identify legacy screening gaps
☐ Staff training preparation
☐ Define escalation procedures
```

### Integration (Week 3-6)

```
☐ API authentication setup
☐ Staging environment testing
☐ Customer data migration
☐ Screening rule configuration
☐ Match investigation procedures
☐ False positive whitelisting
☐ Case management system setup
☐ Reporting procedures
```

### Testing (Week 7-8)

```
☐ Known match testing (OFAC list)
☐ False negative testing
☐ Performance/load testing
☐ System failure/fallback testing
☐ Integration testing with front-end systems
☐ Reporting accuracy verification
☐ Escalation procedure testing
☐ Documentation of results
```

### Deployment (Week 9-10)

```
☐ Production deployment
☐ Customer notification
☐ Staff training completion
☐ Monitoring and alerts setup
☐ First week performance review
☐ Issue resolution
☐ Optimization recommendations
```

## Screening Process Design

```
ACCOUNT OPENING SCREENING:

Customer Provides Information
        │
        ▼
Extract Key Data:
├── Full name
├── Alternative names/nicknames
├── Country of residence
├── Country of business
├── DOB
├── Nationality
├── Document number (passport, ID)
└── Entity type (if business)
        │
        ▼
Execute Screening:
├── Against OFAC SDN List (8000+ entries)
├── Against EU Consolidated List
├── Against UN Security Council list
├── Against custom sanctions lists
├── Against PEP databases
└── Against adverse media sources
        │
        ▼
Evaluate Results:
├── No Match → Proceed
├── Potential Match (70-95%) → Manual Review
├── Strong Match (>95%) → Escalate
└── Confirmed Match → Block/Decline
        │
        ▼
Document Decision
```

## Matching Techniques

### Exact Matching
```python
# Direct name comparison
if customer_name == sdnlist_name and \
   customer_dob == sdnlist_dob:
    alert_type = "EXACT_MATCH"
    severity = "CRITICAL"
```

### Fuzzy Matching
```python
# Levenshtein distance (spelling variations)
from difflib import SequenceMatcher

similarity = SequenceMatcher(None, customer_name, sdnlist_name)
confidence = similarity.ratio()  # 0-1 scale

if confidence > 0.95:
    alert_type = "HIGH_CONFIDENCE_FUZZY"
elif 0.85 < confidence <= 0.95:
    alert_type = "MANUAL_REVIEW_REQUIRED"
```

### Boolean Search
```python
# Multiple criteria matching
if match_name(customer_name, sdnlist_name) and \
   match_country(customer_country, sdnlist_country) and \
   (match_dob(customer_dob, sdnlist_dob) or \
    match_passport(customer_passport, sdnlist_passport)):
    alert_type = "MULTI_FACTOR_MATCH"
    severity = "HIGH"
```

## False Positive Management

### Whitelist Configuration
```
WHITELIST RULES:

Rule 1: Known Safe Customers
├── Customers with > 5 years history
├── No previous sanctions concerns
├── Multiple transactions without issues
└── Manual override not needed

Rule 2: Common Name Matching
├── Names like "John Smith"
├── Country helps distinguish
├── Additional criteria needed (DOB, etc.)
└── Require 3+ matching factors

Rule 3: Entity Designation
├── If beneficial owner passes screening
├── And entity screening passed
├── Then entity approved
└── No recurring alert needed

Rule 4: Professional Exemptions
├── Law firms conducting screening
├── Banks for correspondent banking
├── Government entities
└── Documented exemptions
```

### Manual Review Process
```
INVESTIGATION PROCEDURE:

Step 1: Alert Received
├── Review match details
├── Customer information on file
├── Transaction/account details
└── Historical context

Step 2: Research
├── Google search for individual
├── LinkedIn verification
├── Corporate database check
├── Regulatory database check
├── PEP database verification

Step 3: Assessment
├── Likelihood it's the same person
├── Risk factors present?
├── Legitimate explanation?
├── Similar names in jurisdiction?
└── Circumstantial evidence

Step 4: Decision
├── False positive (proceed)
├── True positive (escalate)
├── Inconclusive (manual override + monitoring)
└── Document reasoning

Step 5: Action
├── Approve (if false positive)
├── Block (if true positive)
├── Monitor (if inconclusive)
└── File documentation
```

## Performance Metrics

```
TARGET METRICS:

Coverage:
├── All new accounts screened: 100%
├── All transaction initiated: 100%
├── OFAC list current: Daily updates
└── Screening uptime: 99.99%

Accuracy:
├── True positive rate: > 99%
├── True negative rate: > 99%
├── False positive rate: < 5%
├── False negative rate: < 0.1%

Efficiency:
├── Screening latency: < 500ms
├── Manual review decision: < 1 hour
├── Investigation completion: 100%
└── Documentation: 100%

Quality:
├── Match confidence scoring: Documented
├── Manual review quality: > 95%
├── Appeal/override rate: < 5%
└── Regulatory violations: 0
```

## Best Practices

1. **Real-Time Screening** - Immediate screening on account open/transaction initiation
2. **List Currency** - Daily/weekly list updates (not monthly)
3. **Threshold Management** - Balance detection with false positives
4. **Documentation** - Document every match and disposition
5. **Regular Testing** - Monthly accuracy testing with known matches
6. **Staff Training** - Quarterly training on matching procedures
7. **Escalation** - Clear procedures for confirmed matches
8. **Regulatory Alignment** - Follow OFAC FAQ guidance
9. **Performance Monitoring** - Daily monitoring of screening performance
10. **Contingency Planning** - Backup vendor or manual procedures

## Common Issues and Solutions

```
Issue: High False Positive Rate (>10%)

Causes:
├── Threshold too sensitive
├── List contains duplicates
├── Common names in jurisdiction
└── Poor matching algorithm

Solutions:
├── Increase threshold (but not > 95%)
├── Add additional matching factors
├── Enhance whitelist
├── Switch algorithm (fuzzy → boolean)
└── Add country/DOB as requirement
```

```
Issue: Missed Matches (False Negatives)

Causes:
├── Name variations (spelling, transliteration)
├── Threshold too high
├── Incomplete customer data
└── Account holder vs. beneficial owner mismatch

Solutions:
├── Lower threshold slightly (but maintain accuracy)
├── Add phonetic matching
├── Collect complete customer information
├── Screen beneficial owners separately
└── Add alternate name screening
```

```
Issue: System Latency Issues

Causes:
├── Vendor API slow
├── Large transaction volume
├── Network issues
└── List updates taking time

Solutions:
├── Implement caching for known passes
├── Use batch screening for off-peak processing
├── Add connection pooling
├── Implement failover mechanism
└── Vendor optimization
```

## Regulatory References

- **OFAC Guidance**: OFAC Notice on Sanctions Screening
- **FinCEN Guidance**: Sanctions Compliance
- **FATF Recommendations**: Recommendations 6, 7, 8
- **MAS Notice**: AML/CFT Regulation, Notice 648
- **EU Regulation**: 5AMLD, Sanctions Regulations

## Integration Points

- Customer onboarding system
- Transaction processing system
- Payment processor
- Core banking platform
- CRM system
- Reporting system
- Audit trail/logging system
