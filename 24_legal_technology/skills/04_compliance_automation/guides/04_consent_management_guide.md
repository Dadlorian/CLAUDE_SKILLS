# Consent Management Implementation Guide

## Building Automated Consent and Preference Management

### GDPR Consent Requirements
- **Freely given:** No coercion, genuine choice
- **Specific:** Purpose-specific consent
- **Informed:** Clear information about processing
- **Unambiguous:** Clear affirmative action
- **Easy to withdraw:** As easy as giving consent
- **Granular:** Separate consents for different purposes
- **Documented:** Proof of consent required

### Implementation Architecture

#### 1. Cookie Consent (Website)
**Deploy Cookie Banner:**
- Scan website for cookies and trackers
- Categorize: Strictly Necessary, Functional, Analytics, Marketing
- Display consent banner on first visit
- Block non-essential cookies until consent
- Remember consent choice
- Provide easy withdrawal mechanism

**Platforms:** OneTrust Cookie Compliance, Cookiebot, Osano, TrustArc

**Configuration:**
```javascript
// Example OneTrust cookie consent
OneTrust.OnConsentChanged(function(e) {
  if(OneTrust.IsAlertBoxClosed()) {
    // User made choice
    var analytics_consent = OneTrust.IsAlertBoxClosedAndValid() && 
                           OnetrustActiveGroups.includes('C0002'); // Analytics category
    
    if(analytics_consent) {
      // Load Google Analytics
      enableAnalytics();
    }
  }
});
```

#### 2. Preference Center
**Build Self-Service Portal:**
- User authentication
- Display current consent status
- Granular opt-in/opt-out by:
  - Purpose (marketing, analytics, personalization)
  - Channel (email, SMS, phone, mail)
  - Product/service category
- Consent history view
- One-click withdrawal
- Save preferences

**Example Preference Structure:**
```json
{
  "user_id": "12345",
  "consents": {
    "marketing_email": {
      "status": "opt-in",
      "timestamp": "2024-01-15T10:30:00Z",
      "version": "2.1",
      "source": "preference_center"
    },
    "marketing_sms": {
      "status": "opt-out",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "analytics": {
      "status": "opt-in",
      "timestamp": "2024-01-10T14:20:00Z",
      "source": "cookie_banner"
    }
  }
}
```

#### 3. Consent Database
**Centralized Consent Repository:**
- Store all consent records
- Who, what, when, how consent obtained
- Consent version control
- Withdrawal tracking
- Audit trail
- API access for systems to check consent status

**Database Schema:**
```sql
CREATE TABLE consents (
    consent_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL, -- opt-in, opt-out
    consent_method VARCHAR(50), -- web_form, cookie_banner, email_link
    consent_text_version VARCHAR(10),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP NOT NULL,
    expiration_date DATE,
    withdrawn_at TIMESTAMP,
    INDEX idx_user_purpose (user_id, purpose)
);
```

#### 4. System Integrations
**Sync Consents to Operational Systems:**

**CRM Integration (Salesforce):**
```python
def sync_consent_to_salesforce(user_id, consents):
    # Get Salesforce contact
    contact = sf_client.query(f"SELECT Id FROM Contact WHERE Email = '{user_id}'")
    
    # Update consent fields
    sf_client.Contact.update(contact['Id'], {
        'Marketing_Email_Opt_In__c': consents['marketing_email'] == 'opt-in',
        'Marketing_SMS_Opt_In__c': consents['marketing_sms'] == 'opt-in',
        'Last_Consent_Update__c': datetime.now()
    })
```

**Email Service Provider (Mailchimp, SendGrid):**
- Real-time consent status sync
- Suppress sending to opted-out users
- Segment lists based on consent status

**Marketing Automation:**
- Prevent campaigns to non-consented users
- Auto-exclude opt-outs from workflows
- Track consent in lead scoring

#### 5. Consent Capture Points
**Where to Collect Consent:**
- Website cookie banner
- Account registration
- Newsletter signup
- Checkout process
- Mobile app first launch
- In-store signup (tablet, POS)
- Phone (verbal consent with recording)
- Third-party data acquisition

**Best Practice Consent Form:**
```html
<form id="consent-form">
  <p>We will use your personal data for the following purposes:</p>
  
  <label>
    <input type="checkbox" name="marketing_email">
    Send me promotional emails about products and services
  </label>
  
  <label>
    <input type="checkbox" name="marketing_sms">
    Send me promotional text messages
  </label>
  
  <label>
    <input type="checkbox" name="profiling">
    Analyze my behavior to personalize my experience
  </label>
  
  <p><small>You can withdraw consent anytime in your <a href="/preferences">Preference Center</a></small></p>
  
  <button type="submit">Save Preferences</button>
</form>
```

#### 6. Consent Lifecycle Management
**Automated Lifecycle:**
- **Capture:** Record consent with full context
- **Store:** Centralized consent database
- **Sync:** Real-time sync to operational systems
- **Enforce:** Block processing without valid consent
- **Renew:** Re-consent when policies change or consent expires
- **Withdraw:** Process withdrawals immediately
- **Audit:** Maintain complete consent history

**Consent Expiration:**
```python
def check_consent_expiration():
    # Find consents expiring in 30 days
    expiring_consents = db.query("""
        SELECT user_id, email, purpose 
        FROM consents 
        WHERE status = 'opt-in' 
        AND expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
    """)
    
    # Send re-consent requests
    for consent in expiring_consents:
        send_reconsent_email(consent['email'], consent['purpose'])
```

### Compliance Monitoring
**Automated Checks:**
- Consent coverage: % of users with documented consent
- Opt-in rates by channel and purpose
- Withdrawal rates and reasons
- Consent age (time since obtained)
- Invalid consents (expired, withdrawn)
- Processing without consent (compliance violations)

**Dashboards:**
- Real-time consent metrics
- Consent trends over time
- Channel performance (email vs. SMS opt-in rates)
- Compliance risk indicators

### Consent Proof Documentation
**Maintain Evidence:**
- Exact consent text shown to user
- Version of privacy policy/terms
- Timestamp of consent
- User IP address and device
- Method of consent (checkbox, button click, etc.)
- Screenshot or copy of consent interface
- User identifier

### CCPA Opt-Out Implementation
**"Do Not Sell or Share" Link:**
```html
<!-- Homepage footer -->
<a href="/do-not-sell" class="privacy-link">
  Do Not Sell or Share My Personal Information
</a>
```

**Opt-Out Form:**
- Collect user identification (email, name, account)
- Verify identity
- Process opt-out immediately
- Confirm to user
- Stop sales/sharing within required timeframe
- Document opt-out

**Global Privacy Control (GPC) Support:**
```javascript
// Detect GPC signal
if (navigator.globalPrivacyControl) {
  // User has GPC enabled
  processOptOut(user_id);
  suppressDataSalesAndSharing(user_id);
}
```

### Key Metrics
- Consent opt-in rate (% accepting)
- Opt-out rate
- Consent withdrawal rate
- Time to sync consent across systems
- % of marketing sends to consented users
- Invalid consent rate
- Re-consent campaign success rate

### Technology Stack
**Consent Management Platform:** OneTrust, TrustArc, Cookiebot
**Preference Center:** Custom build or CMP-provided
**Consent Storage:** PostgreSQL, MongoDB, CMP database
**Integrations:** RESTful APIs, webhooks
**Marketing Suppression:** Native integrations or custom sync

### Best Practices
1. **Granular Consents:** Separate consents for each purpose
2. **Clear Language:** Plain language, not legalese
3. **Prominent Placement:** Easy to find and access
4. **Pre-Ticked Boxes Forbidden:** Require affirmative action
5. **Audit Trail:** Document everything
6. **Real-Time Sync:** Update systems immediately
7. **Easy Withdrawal:** One-click preference center
8. **Periodic Re-Consent:** Refresh consents annually
9. **A/B Testing:** Optimize consent capture rates
10. **Privacy by Default:** Don't assume consent

---
*Guide for implementing automated consent and preference management*
