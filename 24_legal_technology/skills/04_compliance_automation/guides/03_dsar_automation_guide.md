# Data Subject Access Request (DSAR) Automation Guide

## Automating GDPR/CCPA Data Subject Rights Requests

### Overview
Automate the end-to-end DSAR process from intake to fulfillment within regulatory deadlines (30 days GDPR, 45 days CCPA).

### DSAR Types
- **Access/Right to Know:** Provide copy of personal data
- **Deletion/Erasure:** Delete personal data
- **Rectification/Correction:** Correct inaccurate data  
- **Portability:** Export data in machine-readable format
- **Restriction:** Restrict processing
- **Objection:** Stop certain processing
- **Opt-Out:** Stop sale/sharing (CCPA)

### Implementation Steps

#### 1. Self-Service Portal
**Build Public-Facing Request Portal:**
- Web form for request submission
- Request type selection
- Requester information (name, email, account ID)
- Optional: Upload proof of identity
- CAPTCHA for bot protection
- Confirmation email with ticket number

**Platforms:** OneTrust DSAR, TrustArc Rights Management, Custom (ServiceNow, Zendesk)

#### 2. Identity Verification
**Verification Methods:**
- **Low Risk:** Email verification link
- **Medium Risk:** Knowledge-based authentication (KBA) - account details, last transaction
- **High Risk:** Government ID upload + selfie verification
- **Employee Requests:** SSO/corporate authentication

**Automated Decisioning:**
- Risk-based verification (deletion = higher verification)
- Automated verification for customers with active accounts
- Manual review for uncertain cases

#### 3. Data Discovery and Collection
**Automated Data Retrieval:**
```python
# Pseudocode for data discovery
def process_access_request(email):
    data_package = {}
    
    # CRM Data
    data_package['crm'] = salesforce_api.get_customer_data(email)
    
    # Marketing Data
    data_package['marketing'] = hubspot_api.get_contact_data(email)
    
    # Support Tickets
    data_package['support'] = zendesk_api.get_tickets(email)
    
    # Application Database
    data_package['app_db'] = database.query(f"SELECT * FROM users WHERE email = '{email}'")
    
    # File Storage
    data_package['files'] = s3.search_files_by_metadata(email)
    
    return compile_data_package(data_package)
```

**System Integrations:**
- CRM (Salesforce, HubSpot)
- Support (Zendesk, ServiceNow)
- Marketing automation (Marketo, Eloqua)
- E-commerce platforms
- HR systems (Workday, SAP)
- Custom applications via APIs
- File storage (SharePoint, Box, S3)
- Databases (PostgreSQL, MongoDB)

#### 4. Automated Workflow
```
Request Submitted
    ↓
[Automated] Create Ticket & Log
    ↓
[Automated] Identity Verification
    ↓ Pass                    ↓ Fail
Proceed                   Request Additional Info
    ↓
[Automated] Data Discovery Across Systems
    ↓
[Automated] Compile Data Package
    ↓
[Manual] Privacy Team Review (if needed)
    ↓
[Manual] Legal Review (if exceptions apply)
    ↓
[Automated] Generate Response Package
    ↓
[Automated] Deliver to Requester (Secure Portal/Email)
    ↓
[Automated] Deadline Tracking (Day 1-30)
    ↓
[Automated] Close Request & Archive
```

#### 5. Deletion Automation
**Deletion Process:**
- Identify all instances of personal data across systems
- Check for deletion exceptions (legal obligations, ongoing contracts)
- Execute deletion via APIs or scripts
- Verify deletion completion
- Generate certificates of deletion
- Maintain deletion audit trail

**Deletion Exceptions Check:**
```python
def check_deletion_exceptions(user_id):
    exceptions = []
    
    # Active contracts
    if has_active_contract(user_id):
        exceptions.append("Active contract in place")
    
    # Legal hold
    if legal_hold_exists(user_id):
        exceptions.append("Legal hold - litigation")
    
    # Regulatory retention
    if regulatory_retention_applies(user_id):
        exceptions.append("Regulatory retention requirement")
    
    return exceptions
```

#### 6. Response Delivery
**Secure Delivery Methods:**
- **Secure Portal:** Upload data package, send access link with authentication
- **Encrypted Email:** PGP or password-protected ZIP
- **API:** For portability requests, direct system-to-system transfer

**Data Package Format:**
- JSON for structured data
- CSV for tabular data
- PDF for documents
- ZIP archive for multiple files

### Deadline Management
**Automated Tracking:**
- GDPR: 30 days (extendable to 90 days)
- CCPA: 45 days (extendable to 90 days)
- Automated countdown from submission date
- Reminders at Day 7, Day 14, Day 21, Day 28
- Escalation for approaching/overdue requests
- Dashboard showing all requests by status and days remaining

### Metrics and KPIs
- Average response time
- % requests completed within SLA (30/45 days)
- Request volume trends
- Automation rate (% fully automated vs. manual)
- Verification success rate
- Request types distribution
- Top data sources for requests

### Technology Stack Example
**Portal:** Custom web app or OneTrust/TrustArc
**Workflow:** ServiceNow, Jira Service Management
**Data Discovery:** Custom Python/Node.js scripts, BigID, OneTrust
**Storage:** Secure cloud storage (AWS S3, Azure Blob)
**Delivery:** Secure file transfer, encrypted email
**Monitoring:** Compliance dashboard (Power BI, Tableau)

### Best Practices
1. **Automate Verification:** Reduce manual verification where safe
2. **Pre-Build Integrations:** Connect all major data sources upfront
3. **Test Thoroughly:** Run test requests through all workflows
4. **Monitor Deadlines:** Proactive alerts prevent missed SLAs
5. **Document Everything:** Maintain complete audit trail
6. **Train Teams:** Ensure staff can handle exceptions
7. **Continuous Improvement:** Analyze bottlenecks and optimize

### Common Challenges
- **Data Silos:** Personal data scattered across many systems
- **Unstructured Data:** Difficult to search emails, documents
- **Legacy Systems:** No APIs, manual extraction required
- **Verification Fraud:** Attackers requesting others' data
- **Volume Spikes:** Sudden influx of requests
- **Deletion Complexity:** Cascading deletes across systems

### Success Criteria
- 95%+ requests completed within deadline
- 80%+ automation rate (minimal manual effort)
- < 2% verification failures
- < 1% data accuracy complaints
- Complete audit trail for all requests

---
*Practical guide for automating data subject access requests*
