# Case Law Databases: Comprehensive Reference Guide

## Overview

Case law databases are the foundation of legal research, providing access to judicial opinions from federal and state courts. This reference covers major commercial databases, free alternatives, and specialized repositories.

## Database Ecosystem

### Tier 1: Premium Comprehensive Databases

#### Westlaw Edge (Thomson Reuters)
**Coverage**:
- Federal Courts: Supreme Court (1790+), Courts of Appeals (1891+), District Courts (1789+)
- State Courts: All 50 states, appellate and trial courts (varying start dates)
- Specialized Courts: Tax Court, Bankruptcy Courts, Military Courts, Tribal Courts
- Administrative: Agency decisions (FCC, SEC, NLRB, etc.)

**Unique Features**:
- West Key Number System: Hierarchical topic classification (over 100,000 key numbers)
- Headnotes: Editorial summaries of legal points
- Star Pagination: Citations to original reporter pagination
- Unpublished Opinions: Comprehensive collection of unreported decisions

**Database Identifiers**:
```
ALLCASES - All federal and state cases
SCT - U.S. Supreme Court
CTA - Federal Courts of Appeals (all circuits)
DCT - Federal District Courts
ALLSTATES - All state cases
CA-CS - California state cases
NY-CS - New York state cases
TX-CS - Texas state cases
```

**Coverage Timeline**:
| Court | Start Year | Comprehensiveness |
|-------|------------|-------------------|
| U.S. Supreme Court | 1790 | 100% |
| Federal Appellate | 1891 | 99%+ |
| Federal District | 1789 | 80%+ (pre-1950), 99%+ (post-1950) |
| State Appellate | Varies | 95%+ (varies by state) |
| State Trial | Varies | Limited (increasing) |

#### LexisNexis
**Coverage**:
- Federal: Supreme Court, Circuit Courts, District Courts, specialized courts
- State: All jurisdictions, varying historical depth
- Administrative: Federal and state agency decisions
- International: Select foreign jurisdictions

**Unique Features**:
- Shepard's Editorial Treatment: Legal analysis of citation treatment
- Headnotes: LexisNexis editorial summaries
- Unpublished Decisions: Extensive collection
- Segment Searching: Search specific document segments (JUDGE, COUNSEL, DISSENT)

**Source Identifiers**:
```
Federal Cases, Combined - All federal
U.S. Supreme Court Cases - SCOTUS only
U.S. Courts of Appeals Cases - Circuit courts
U.S. District Courts Cases - District courts
State Cases, Combined - All states
California Cases, Combined - CA state
New York Cases, Combined - NY state
```

**Coverage Quality**:
- Supreme Court: Complete from 1790
- Federal Appellate: Near-complete from creation
- State Courts: Varies (most complete post-1945)
- Unpublished: Industry-leading collection

### Tier 2: Cost-Effective Premium Databases

#### Bloomberg Law
**Coverage**:
- Federal: Supreme Court, Courts of Appeals, District Courts
- State: All 50 states (appellate courts)
- Specialized: Tax Court, bankruptcy, administrative
- Dockets: PACER integration, state court dockets (select jurisdictions)

**Unique Features**:
- BLAW Points of Law: AI-extracted legal principles
- Litigation Analytics: Judge and attorney analytics tied to dockets
- Docket Search: Integrated docket and opinion research
- Company Litigation Profiles: Entity-centric litigation research

**Database Scope**:
- Federal cases: 1789-present
- State cases: Varies by jurisdiction (generally 1950s+)
- Dockets: Real-time PACER feeds
- International: Limited compared to Westlaw/Lexis

**Strengths**:
- Litigation analytics integration
- Docket-to-opinion linking
- Business intelligence integration
- Competitive pricing

#### Casetext
**Coverage**:
- Federal: All federal courts
- State: All 50 states (appellate opinions)
- Administrative: Select agency decisions

**Unique Features**:
- CARA A.I.: AI-powered research assistant (upload brief, find similar cases)
- SmartCite: Citation analysis with treatment indicators
- Parallel Search: Find similar cases based on legal issues (not just keywords)
- Collaborative Annotations: User-contributed notes (with limitations)

**Database Details**:
- Coverage: Generally 1950+, Supreme Court complete
- Unpublished Opinions: Good collection (expanding)
- Updates: Daily
- Historical Depth: Less than Westlaw/Lexis for very old cases

**Technology Advantages**:
- Modern interface
- AI-first design
- Superior relevance ranking (by some measures)
- API access (premium feature)

#### Fastcase
**Coverage**:
- Federal: Supreme Court, Courts of Appeals, District Courts
- State: All 50 states
- Administrative: Select agencies

**Unique Features**:
- Bad Law Bot: AI identifies negative treatment
- Authority Check: Citation validation
- Interactive Timeline: Visualize case precedent over time
- Forecite: Citation network visualization

**Access Models**:
- Bar Association Memberships: Free for many state bars
- Direct Subscription: $995/year (individual)
- Law Firm Subscriptions: Negotiated pricing
- Public Library Access: Free in some jurisdictions

**Coverage Depth**:
- Supreme Court: 1 U.S. (1754) to present
- State Courts: Varies (often less historical depth than Westlaw/Lexis)
- Updates: Daily
- Unpublished: Limited compared to premium platforms

### Tier 3: Free & Open Access Databases

#### Google Scholar (Case Law)
**URL**: scholar.google.com
**Coverage**:
- Federal: Supreme Court, Courts of Appeals, District Courts (select), specialized courts
- State: All 50 states (appellate courts)
- Time Range: Varies by court (generally 1950s+)

**Features**:
- Free access (no subscription)
- Cited by linking
- Boolean search
- Court-specific filtering
- Citation export

**Limitations**:
- No citation validation (no KeyCite/Shepard's equivalent)
- Limited search sophistication
- No unpublished opinions
- Inconsistent coverage across jurisdictions
- No customer support

**Best Use Cases**:
- Quick case retrieval by citation
- Budget research
- Public access
- Preliminary research
- Citation checking (via "Cited by")

#### Justia
**URL**: law.justia.com
**Coverage**:
- Federal: Supreme Court, Courts of Appeals, District Courts
- State: All 50 states
- Free access

**Features**:
- Clean interface
- Annotations by legal professionals
- Case summaries
- Email alerts
- API access (for developers)

**Content Depth**:
- Supreme Court: 1789-present
- Federal Appellate: 1950s-present
- State Courts: Varies
- Updates: Daily from official sources

#### CourtListener (Free Law Project)
**URL**: courtlistener.com
**Coverage**:
- Federal: Comprehensive (PACER data)
- State: Expanding (varies by jurisdiction)
- Oral Arguments: Audio archives
- Dockets: PACER recap project

**Features**:
- Open-source platform
- API access (free)
- Citation network data
- Judicial database
- Alerts (free)

**Unique Aspects**:
- Non-profit mission (free law)
- Bulk data downloads
- Research-grade data
- Oral argument audio/transcripts
- Developer-friendly

**Technical Features**:
```python
# CourtListener API example
import requests

def search_courtlistener(query):
    url = "https://www.courtlistener.com/api/rest/v3/search/"
    params = {
        "q": query,
        "type": "o",  # opinions
        "order_by": "score desc"
    }
    headers = {
        "Authorization": "Token your_api_token"
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()
```

#### Public.Resource.Org
**Coverage**:
- Federal cases: Bulk collections
- Legal materials: Public domain legal resources
- Primary law: Statutes, regulations, cases

**Mission**:
- Public access to law
- Open data advocacy
- Bulk data repositories

### Specialized Case Law Databases

#### Versuslaw
**Coverage**: Federal and state cases (budget-friendly)
**Pricing**: $13.95/month (basic individual)
**Niche**: Solo practitioners, small firms, cost-conscious research

#### Loislaw (Wolters Kluwer)
**Coverage**: Federal and state cases
**Integration**: Part of Wolters Kluwer practice management ecosystem
**Niche**: Integrated with billing/practice management

#### VersusLaw
**Coverage**: Basic case law (all jurisdictions)
**Cost**: Low-cost alternative
**Limitations**: Less comprehensive than tier 1 platforms

#### Ravel Law (acquired by LexisNexis)
**Legacy**: Innovative citation visualization
**Status**: Integrated into LexisNexis
**Contribution**: Advanced citation network analysis (now in Lexis)

## Case Law Coverage Analysis

### Historical Coverage Comparison

| Platform | SCOTUS Start | Fed. App. Start | State Coverage |
|----------|--------------|-----------------|----------------|
| Westlaw | 1790 | 1891 | Excellent (1800s+) |
| LexisNexis | 1790 | 1891 | Excellent (1800s+) |
| Bloomberg | 1789 | 1891 | Good (1950s+) |
| Casetext | 1790 | 1891 | Good (1950s+) |
| Fastcase | 1754 | 1891 | Fair (varies) |
| Google Scholar | 1791 | 1923 | Fair (1950s+) |

### Unpublished Opinion Coverage

**Importance**: Unpublished opinions increasingly citable (Fed. R. App. P. 32.1)

**Platform Coverage**:
- **Westlaw**: Most comprehensive (proprietary collection efforts)
- **LexisNexis**: Excellent (industry leader historically)
- **Bloomberg**: Good (growing)
- **Casetext**: Fair (expanding)
- **Fastcase**: Limited
- **Free Databases**: Minimal to none

### Current Good Law Validation

| Platform | Citation Checker | Methodology | Accuracy |
|----------|------------------|-------------|----------|
| Westlaw | KeyCite | Editorial + algorithmic | 99%+ |
| LexisNexis | Shepard's | Editorial + algorithmic | 99%+ |
| Bloomberg | BCite | Algorithmic | 95%+ |
| Casetext | SmartCite | AI-powered | 90%+ |
| Fastcase | Bad Law Bot | AI-powered | 85%+ |
| Free platforms | None | Manual (via citations) | N/A |

## Database Selection Framework

### By Firm Size

**Large Law Firms (100+ attorneys)**:
- Primary: Westlaw Edge + LexisNexis (both platforms)
- Analytics: Bloomberg Law (litigation intelligence)
- AI Research: Casetext (supplemental)
- Training: Comprehensive programs on all platforms

**Mid-Size Firms (20-100 attorneys)**:
- Primary: Westlaw OR LexisNexis (choose one)
- Cost-effective: Casetext or Fastcase (secondary)
- Specialized: Practice area-specific databases
- Strategy: Deep platform on primary, breadth on secondary

**Small Firms (5-20 attorneys)**:
- Primary: Casetext or Bloomberg Law
- Bar Benefit: Fastcase (if free through bar)
- Free: Google Scholar (supplemental)
- Cost focus: Maximize value per dollar

**Solo Practitioners**:
- Primary: Fastcase (bar membership) or Casetext
- Free: Google Scholar, Justia, CourtListener
- Transactional: Westlaw/Lexis hourly for complex matters
- Strategy: Minimize fixed costs, optimize per-matter spend

### By Practice Area

**Litigation-Heavy**:
- **Essential**: Westlaw or LexisNexis (citation validation critical)
- **Supplemental**: Bloomberg Law (litigation analytics)
- **Reasoning**: Need comprehensive case law + citation validation

**Transactional**:
- **Essential**: Casetext or Bloomberg Law
- **Supplemental**: Free resources
- **Reasoning**: Less case law research, more cost sensitivity

**Appellate Practice**:
- **Essential**: Westlaw Edge (KeyCite Overruling Risk)
- **Supplemental**: LexisNexis (cross-validation)
- **Reasoning**: Citation validation absolutely critical

**Federal Practice**:
- **Optimal**: Any platform (all cover federal well)
- **Free Option**: Google Scholar + CourtListener (adequate for federal)

**State-Specific Practice**:
- **Critical**: Verify state coverage depth
- **Check**: Unpublished opinion coverage
- **Consideration**: State-specific databases (e.g., Texas-specific platforms)

## Technical Integration

### API Capabilities

#### Westlaw Edge API
```python
# Search federal cases
def westlaw_search(query, jurisdiction="federal"):
    endpoint = "https://api.westlaw.com/search/v1/query"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "query": query,
        "database": "ALLFEDS" if jurisdiction == "federal" else "ALLSTATES",
        "fields": ["citation", "court", "date", "snippet"],
        "limit": 50
    }
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()
```

#### LexisNexis API
```python
# Search with Shepard's integration
def lexis_search_with_shepards(query):
    endpoint = "https://api.lexisnexis.com/v1/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "query": query,
        "sources": ["Federal Cases, Combined"],
        "shepardize": True,
        "limit": 50
    }
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()
```

#### CourtListener API (Free)
```python
# Free API for case law
def courtlistener_search(query, court="scotus"):
    endpoint = "https://www.courtlistener.com/api/rest/v3/search/"
    params = {
        "q": query,
        "type": "o",  # opinions
        "court": court,
        "format": "json"
    }
    response = requests.get(endpoint, params=params)
    return response.json()
```

### Bulk Data Access

**Westlaw**: Bulk Data API (enterprise only, costly)
**LexisNexis**: Bulk licensing (negotiated)
**Bloomberg**: Limited bulk access
**Casetext**: API with rate limits
**CourtListener**: Free bulk downloads (research license)
**Ravel (via LexisNexis)**: Citation data (integrated)

### Data Formats

**Standard Outputs**:
- PDF (formatted opinions)
- HTML (web viewing)
- Plain text (parsing)
- XML (structured data)
- JSON (API responses)

**Citation Formats**:
- Bluebook
- ALWD
- MLA
- APA
- Custom

## Database Currency & Updates

### Update Frequency

| Platform | Update Schedule | Lag Time |
|----------|----------------|----------|
| Westlaw | Continuous | < 24 hours |
| LexisNexis | Continuous | < 24 hours |
| Bloomberg | Daily | 24-48 hours |
| Casetext | Daily | 24-48 hours |
| Fastcase | Daily | 24-48 hours |
| Google Scholar | Periodic | Weeks to months |
| CourtListener | Daily | 24-48 hours |

### Source of Cases

**Official Sources**:
- Court websites (official reporters)
- PACER (federal docket system)
- State court systems
- Government printing office

**Proprietary Collection**:
- Westlaw: Aggressive acquisition of unpublished opinions
- LexisNexis: Historical agreements with courts
- Others: Automated collection from court sites

## Best Practices

### Multi-Database Strategy
1. **Primary Platform**: Comprehensive research (Westlaw or LexisNexis)
2. **Cost-Effective Secondary**: Routine research (Casetext, Fastcase)
3. **Free Resources**: Quick checks, public-facing citations (Google Scholar)
4. **Specialized**: Practice-specific databases as needed

### Research Workflow
```
1. Initial Research: Free databases (Google Scholar) - scoping
2. Comprehensive Research: Primary platform (Westlaw/Lexis) - depth
3. Validation: Citation checking (KeyCite/Shepard's) - currency
4. Cost-Effective Updates: Secondary platform alerts - monitoring
5. Client-Facing: Free database verification - accessibility
```

### Quality Assurance
- Cross-platform validation for critical cases
- Verify unpublished opinions on multiple platforms
- Check update dates on free platforms
- Validate citations before relying solely on free sources

## Emerging Trends

### AI-Enhanced Case Law Research
- Semantic search replacing pure keyword search
- Predictive case outcome models
- Automated brief analysis and citation suggestions
- Natural language query processing

### Open Access Movement
- Increasing free access to case law
- Standardized citation formats
- Bulk data availability
- Reduced dependency on commercial platforms

### Technology Integration
- API-first design
- Practice management integration
- Document automation linking
- Real-time citation validation in word processors

---

*This reference provides comprehensive coverage of case law databases as of 2025. Platform features and pricing subject to change.*
