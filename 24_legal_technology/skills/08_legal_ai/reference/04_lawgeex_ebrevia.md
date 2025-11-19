# LawGeex and eBrevia Platforms

## Overview
This reference covers two prominent contract AI platforms: LawGeex (contract review automation) and eBrevia (contract analytics). Both leverage AI to streamline contract workflows but with different focuses and approaches.

---

# LawGeex

## Overview
LawGeex is an AI-powered contract review platform that automates pre-signature contract analysis for legal departments. Founded in 2014, LawGeex specializes in comparing contracts against company policies and playbooks to accelerate review cycles.

## Core Technology

### AI Engine
- **Deep Learning**: Neural networks trained on millions of contracts
- **NLP**: Advanced natural language processing for legal text
- **Policy Matching**: Automated comparison against company standards
- **Risk Scoring**: Quantified risk assessment for each provision
- **Continuous Learning**: Improves from lawyer feedback

### Platform Architecture
```
┌─────────────────────────────────────────────────┐
│        LawGeex Platform                          │
├─────────────────────────────────────────────────┤
│  Contract Intake                                │
│  - Email Integration                            │
│  - CLM Integration                              │
│  - Manual Upload                                │
├─────────────────────────────────────────────────┤
│  AI Review Engine                               │
│  - Policy Comparison                            │
│  - Clause Detection                             │
│  - Risk Assessment                              │
│  - Redline Generation                           │
├─────────────────────────────────────────────────┤
│  Approval Workflow                              │
│  - Auto-approve (low risk)                      │
│  - Route for review (medium risk)               │
│  - Escalate (high risk)                         │
├─────────────────────────────────────────────────┤
│  Integration Layer                              │
│  - DocuSign, AdobeSign                          │
│  - Salesforce, SAP                              │
│  - CLM Systems                                  │
└─────────────────────────────────────────────────┘
```

## Key Features

### 1. Automated Contract Review
```python
# LawGeex Review Process
contract_review = {
    "input": "Vendor NDA received via email",
    "process": [
        "1. AI extracts and analyzes all clauses",
        "2. Compares against company NDA playbook",
        "3. Identifies 12 deviations from policy",
        "4. Scores risk: 8 low, 3 medium, 1 high",
        "5. Generates redline with suggested changes",
        "6. Routes based on risk level"
    ],
    "routing": {
        "low_risk": "Auto-approve and route to DocuSign",
        "medium_risk": "Send to in-house counsel for 5-min review",
        "high_risk": "Escalate to General Counsel"
    },
    "time": "2 minutes (vs. 60 minutes manual)"
}
```

### 2. Playbook Management
Define company positions on contract terms:

```python
nda_playbook = {
    "confidentiality_period": {
        "preferred": "3 years",
        "acceptable": "3-5 years",
        "unacceptable": "> 5 years",
        "action": "Counter-propose 3 years"
    },
    "exclusions": {
        "required": [
            "Publicly available information",
            "Independently developed",
            "Rightfully received from third party",
            "Already known"
        ],
        "missing_exclusion": "Flag for negotiation"
    },
    "return_of_information": {
        "preferred": "Upon request or termination",
        "action_if_missing": "Add provision"
    },
    "governing_law": {
        "required": "Delaware or New York",
        "unacceptable": "Foreign jurisdiction",
        "action": "Reject and request change"
    }
}
```

### 3. Pre-built AI Models
LawGeex offers pre-trained models for common agreement types:

**Contract Types**:
- Non-Disclosure Agreements (NDAs)
- Master Service Agreements (MSAs)
- Software as a Service (SaaS) Agreements
- Vendor Agreements
- Data Processing Agreements (DPAs)
- Purchase Orders
- Employment Offer Letters
- Consulting Agreements

### 4. Risk-Based Routing
```python
# Automated routing logic
routing_rules = {
    "auto_approve": {
        "criteria": "All clauses match playbook exactly",
        "action": "Route to e-signature automatically",
        "percentage_of_contracts": "20-30%"
    },
    "legal_review": {
        "criteria": "1-3 medium deviations",
        "action": "Route to legal with AI-suggested edits",
        "review_time": "5-10 minutes",
        "percentage_of_contracts": "50-60%"
    },
    "escalation": {
        "criteria": "High-risk deviation or novel clause",
        "action": "Route to senior counsel",
        "review_time": "30-60 minutes",
        "percentage_of_contracts": "10-20%"
    }
}
```

## Use Cases

### 1. NDA Automation
**Challenge**: Process 500+ NDAs per month

**LawGeex Solution**:
```
Before LawGeex:
- Every NDA reviewed by attorney
- Average time: 60 minutes
- Monthly hours: 500 hours
- Annual cost: $900,000

After LawGeex:
- 30% auto-approved (no review)
- 50% quick review (10 min)
- 20% standard review (30 min)
- Monthly hours: 100 hours
- Annual cost: $180,000
- Savings: $720,000 (80% reduction)
```

### 2. Vendor Agreement Standardization
**Challenge**: Inconsistent vendor terms across procurement

**LawGeex Solution**:
- AI ensures all vendor agreements comply with company policy
- Automatic flagging of non-standard terms
- Consistent risk assessment across all agreements
- Faster vendor onboarding (5 days → 1 day)

### 3. Sales Acceleration
**Challenge**: Legal bottleneck slowing sales cycles

**LawGeex Solution**:
- Sales team uploads customer paper
- AI review in 2 minutes
- Low-risk: Auto-approved, faster close
- Medium-risk: Legal review in hours, not days
- Result: 50% reduction in contract turnaround time

## Performance Metrics

### Accuracy Benchmark
In 2018, LawGeex commissioned a study comparing AI vs. lawyers:

```
Task: Review 5 NDAs for 30 legal issues

Results:
- LawGeex AI: 94% accuracy
- 20 experienced lawyers: 85% average accuracy
- Top lawyer: 94% accuracy
- AI Time: 26 seconds
- Lawyer Average Time: 92 minutes

Conclusion: AI matched top lawyer accuracy in 1/200th the time
```

### Business Impact
```python
typical_roi = {
    "time_savings": "60-80% reduction in contract review time",
    "cost_savings": "$50K-$500K annually (depending on volume)",
    "cycle_time": "3-5 days → 1 day for standard contracts",
    "legal_capacity": "Free up 10-20 hours/week per attorney",
    "consistency": "100% compliance with company policy",
    "risk_reduction": "Fewer missed issues in routine contracts"
}
```

## Pricing Model
- **Subscription-based**: Annual or multi-year contracts
- **Per-Contract**: Pay per contract reviewed
- **Tiered**: Based on contract volume and complexity
- **Enterprise**: Unlimited reviews for large legal departments

**Typical Range**: $30K-$150K annually for mid-size legal departments

## Integration Capabilities
```python
# Integration examples
integrations = {
    "email": "Intake contracts from legal@company.com",
    "clm": ["Ironclad", "Icertis", "ContractWorks", "Agiloft"],
    "crm": ["Salesforce", "HubSpot"],
    "erp": ["SAP", "Oracle"],
    "e_signature": ["DocuSign", "AdobeSign", "HelloSign"],
    "document_management": ["SharePoint", "Box", "Dropbox"]
}
```

---

# eBrevia

## Overview
eBrevia (acquired by DFIN in 2018) is an AI-powered platform for contract analytics and data extraction. It specializes in extracting key provisions from large volumes of contracts for due diligence, portfolio analysis, and compliance reviews.

## Core Technology

### Machine Learning Approach
- **Deep Learning**: Convolutional and recurrent neural networks
- **Pre-trained Models**: 100+ clause types out-of-the-box
- **Custom Training**: Build models for specific provisions
- **Multi-language**: Support for English, French, German, Spanish, others
- **Continuous Improvement**: Active learning from user feedback

### Key Differentiators
- **Intelligent Search**: Beyond keyword matching
- **Timeline View**: Chronological view of contract portfolio
- **Amendment Tracking**: Links amendments to base agreements
- **Obligation Calendar**: Tracks deadlines and renewals
- **Integration with DFIN**: Enhanced due diligence capabilities

## Key Features

### 1. Pre-built Provision Library
```python
ebrevia_provisions = {
    "general_terms": [
        "Parties",
        "Effective Date",
        "Term",
        "Termination",
        "Governing Law",
        "Amendment",
        "Assignment"
    ],
    "financial": [
        "Payment Terms",
        "Price",
        "Fees",
        "Penalties",
        "Most Favored Nation",
        "Audit Rights"
    ],
    "risk": [
        "Indemnification",
        "Limitation of Liability",
        "Insurance",
        "Warranties",
        "Representations"
    ],
    "compliance": [
        "Confidentiality",
        "Data Privacy",
        "Anti-Corruption",
        "Export Controls",
        "Force Majeure"
    ],
    "ip": [
        "Ownership",
        "License Grants",
        "Restrictions",
        "Patent Rights"
    ]
}
```

### 2. Intelligent Search
```python
# eBrevia search capabilities
search_examples = {
    "conceptual": {
        "query": "limitation of liability provisions",
        "finds": [
            "cap on damages",
            "exclusion of consequential damages",
            "liability limitations",
            "damage disclaimers"
        ]
    },
    "proximity": {
        "query": "indemnification NEAR supplier",
        "finds": "indemnification obligations of supplier"
    },
    "boolean": {
        "query": "(termination OR cancellation) AND (cause OR convenience)",
        "finds": "termination provisions with cause/convenience distinctions"
    }
}
```

### 3. Amendment Analysis
Unique capability to link amendments to original agreements:

```python
amendment_tracking = {
    "base_agreement": "MSA_2020_Supplier_A.pdf",
    "amendments": [
        "Amendment_1_2021_pricing.pdf",
        "Amendment_2_2022_scope.pdf",
        "Amendment_3_2023_term_extension.pdf"
    ],
    "consolidated_view": "Single view showing current terms after all amendments",
    "change_tracking": "Highlights what changed in each amendment",
    "timeline": "Chronological evolution of agreement"
}
```

### 4. Timeline and Calendar
```python
# Contract timeline features
timeline_view = {
    "contract_lifecycle": {
        "negotiation_start": "2020-01-15",
        "execution_date": "2020-03-01",
        "effective_date": "2020-04-01",
        "first_renewal": "2021-04-01",
        "second_renewal": "2022-04-01",
        "termination_notice_deadline": "2023-01-01",
        "current_term_end": "2023-04-01"
    },
    "obligations": [
        {"type": "Annual Report", "due": "2023-12-31"},
        {"type": "Insurance Certificate", "due": "2023-06-01"},
        {"type": "Audit Rights Window", "dates": "2023-01-01 to 2023-12-31"}
    ],
    "alerts": "Email notifications 30/60/90 days before deadlines"
}
```

## Use Cases

### 1. M&A Due Diligence
**Challenge**: Analyze 8,000 contracts for acquisition

**eBrevia Solution**:
```
Process:
1. Upload all contracts to eBrevia
2. Run 75 standard provision extractions
3. Add 5 custom provisions for deal-specific issues
4. Generate comprehensive diligence report
5. Flag 200 high-risk provisions for detailed review
6. Export data to Excel for analysis

Results:
- 300 hours → 80 hours (73% time savings)
- More comprehensive than manual review
- Consistent analysis across all contracts
- Structured data for post-close integration
```

### 2. Lease Portfolio Analysis
**Challenge**: Understand 2,000 commercial leases

**eBrevia Solution**:
```python
lease_analysis = {
    "provisions_extracted": [
        "Base Rent",
        "Rent Escalations",
        "Lease Term",
        "Renewal Options",
        "CAM Charges",
        "Tenant Improvements",
        "Assignment Rights",
        "Sublease Restrictions"
    ],
    "deliverables": {
        "rent_roll": "Complete rent schedule with escalations",
        "expiration_schedule": "Lease end dates and renewal options",
        "cost_analysis": "Total occupancy costs by location",
        "risk_report": "Unfavorable terms requiring attention"
    }
}
```

### 3. Regulatory Compliance Review
**Challenge**: Ensure GDPR compliance across 3,000 vendor contracts

**eBrevia Solution**:
```python
compliance_review = {
    "provisions_checked": [
        "Data Processing Agreement",
        "Sub-processor Consent",
        "Data Subject Rights",
        "Breach Notification",
        "Data Retention",
        "International Transfers"
    ],
    "gap_analysis": {
        "compliant": 1200,
        "needs_amendment": 1500,
        "missing_dpa": 300
    },
    "remediation_plan": "Prioritized list of contracts to update"
}
```

### 4. Contract Renewal Management
**Challenge**: Track renewals and terminations across portfolio

**eBrevia Solution**:
- Extract all renewal and termination provisions
- Build obligation calendar with alerts
- Track notice periods and auto-renewal clauses
- Proactive notification 90 days before deadlines
- Prevent unwanted auto-renewals

## Performance Metrics

```python
accuracy_metrics = {
    "standard_provisions": "90-95% accuracy",
    "custom_provisions": "85-90% after training",
    "ocr_quality": "95%+ on modern documents",
    "processing_speed": "100-200 pages/minute",
    "training_time": "1-2 hours for custom models"
}

efficiency_gains = {
    "data_extraction": "10-15x faster than manual",
    "due_diligence": "60-75% time reduction",
    "portfolio_analysis": "80-90% time reduction",
    "typical_roi": "6-12 month payback period"
}
```

## Pricing Model
- **Per-Page**: Pay per page processed
- **Subscription**: Annual unlimited usage
- **Project-Based**: Fixed fee for specific engagements
- **Enterprise**: Custom pricing for large organizations

**Typical Range**: $20K-$100K+ annually depending on volume

## Integration with DFIN

After acquisition by DFIN (Donnelley Financial Solutions):
- Enhanced due diligence capabilities
- Integration with DFIN Venue (virtual data room)
- Combined with DFIN's regulatory expertise
- Offering to investment banks and M&A advisors

---

# Comparison: LawGeex vs. eBrevia

## Primary Focus
```python
comparison = {
    "lawgeex": {
        "primary_use": "Pre-signature contract review",
        "ideal_for": "High-volume, repetitive contracts",
        "key_feature": "Playbook-based automated approval",
        "typical_users": "Corporate legal departments"
    },
    "ebrevia": {
        "primary_use": "Post-signature contract analysis",
        "ideal_for": "Due diligence and portfolio analysis",
        "key_feature": "Comprehensive data extraction",
        "typical_users": "Law firms, M&A teams"
    }
}
```

## Use Case Fit
| Use Case | LawGeex | eBrevia |
|----------|---------|---------|
| NDA Review | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Vendor Agreement Review | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| M&A Due Diligence | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Portfolio Analysis | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Contract Redlining | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Data Extraction | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Real-time Review | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Historical Analysis | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Resources

### LawGeex
- **Website**: https://www.lawgeex.com
- **Documentation**: Customer portal with guides and videos
- **Support**: Email and phone support
- **Training**: Online training and webinars

### eBrevia
- **Website**: https://ebrevia.com
- **Parent Company**: DFIN (https://www.dfinsolutions.com)
- **Documentation**: User manual and video tutorials
- **Support**: Dedicated customer success team

---

*Both LawGeex and eBrevia represent specialized applications of AI to different contract workflows. LawGeex excels at pre-signature review automation, while eBrevia shines in post-signature analysis and data extraction. Many organizations use both for complementary purposes.*
