# Patient Portal Reference

## Overview

Patient portals are secure web-based or mobile applications that provide patients with 24/7 access to their health information, communication with providers, and self-service healthcare management tools. This reference covers portal features, implementation requirements, and best practices.

## Core Portal Features

### 1. Health Information Access

**Patient Demographics**:
```
Viewable Information:
├── Name and contact information
├── Date of birth
├── Address and phone numbers
├── Emergency contacts
├── Insurance information
└── Preferred language

Update Capabilities:
├── Contact information updates
├── Insurance information updates
├── Emergency contact updates
└── Communication preferences
```

**Medical Record Access**:
```
Clinical Information Available:
├── Problem List
│   ├── Current diagnoses
│   ├── Chronic conditions
│   └── Historical diagnoses
├── Medication List
│   ├── Current medications
│   ├── Dosage and frequency
│   ├── Prescribing provider
│   └── Discontinued medications
├── Allergy List
│   ├── Drug allergies
│   ├── Food allergies
│   ├── Environmental allergies
│   └── Reactions experienced
├── Immunization History
│   ├── Vaccine name and date
│   ├── Administering provider
│   ├── Lot number
│   └── Next due date
├── Lab Results
│   ├── Test name
│   ├── Result value
│   ├── Reference range
│   ├── Abnormal flag
│   ├── Result date
│   └── Ordering provider
├── Imaging Results
│   ├── Study type
│   ├── Body part
│   ├── Report narrative
│   ├── Images (if available)
│   └── Radiologist interpretation
├── Visit Summaries
│   ├── Office visit notes
│   ├── Procedure notes
│   ├── Hospital discharge summaries
│   └── Specialist consult notes
├── Vital Signs
│   ├── Blood pressure
│   ├── Heart rate
│   ├── Temperature
│   ├── Weight
│   ├── Height
│   └── BMI
└── Care Plans
    ├── Treatment goals
    ├── Care team members
    ├── Self-management instructions
    └── Follow-up recommendations
```

### 2. Appointment Management

**Appointment Scheduling**:
```
Scheduling Features:
├── View available appointments
│   ├── Filter by provider
│   ├── Filter by location
│   ├── Filter by appointment type
│   └── Filter by date range
├── Schedule new appointment
│   ├── Select provider
│   ├── Select location
│   ├── Select date/time
│   ├── Specify reason for visit
│   └── Add notes for provider
├── Reschedule existing appointment
│   └── Select new date/time
├── Cancel appointment
│   └── Provide cancellation reason
├── View upcoming appointments
│   ├── Date and time
│   ├── Provider name
│   ├── Location and directions
│   ├── Pre-visit instructions
│   └── Add to calendar
└── View past appointments
    └── Visit history
```

**Appointment Reminders**:
```
Reminder Types:
├── Email reminders
│   ├── 7 days before
│   ├── 24 hours before
│   └── Custom timing
├── SMS/text reminders
│   └── Same timing options
├── Push notifications (mobile app)
│   └── Same timing options
└── Phone call reminders
    └── Automated or live

Reminder Content:
├── Appointment date/time
├── Provider name
├── Location and directions
├── Pre-visit instructions
├── Confirm/cancel options
└── Contact information
```

**Pre-Visit Activities**:
```
Pre-Visit Workflows:
├── Check-in online
│   ├── Confirm demographics
│   ├── Update insurance
│   ├── Complete registration
│   └── Sign consent forms
├── Complete intake forms
│   ├── Medical history questionnaire
│   ├── Review of systems
│   ├── Symptom checker
│   └── COVID-19 screening
├── Upload documents
│   ├── Insurance cards
│   ├── ID verification
│   ├── Referral documents
│   └── Prior medical records
└── Make payment
    ├── Co-pay
    ├── Outstanding balance
    └── Save payment method
```

### 3. Secure Messaging

**Provider Communication**:
```
Messaging Features:
├── Compose new message
│   ├── Select recipient (provider/staff)
│   ├── Select message category
│   │   ├── Medication refills
│   │   ├── Test results
│   │   ├── Appointment requests
│   │   ├── General questions
│   │   └── Billing inquiries
│   ├── Enter subject and message
│   ├── Attach documents/images
│   └── Set priority level
├── View message thread
│   ├── Chronological conversation
│   ├── Provider responses
│   └── Read receipts
├── Message notifications
│   ├── Email notification of new message
│   ├── SMS notification
│   └── Push notification
└── Response expectations
    ├── Typical response time (e.g., 1-2 business days)
    ├── After-hours notification
    └── Emergency disclaimer

Message Categories:
├── Non-urgent clinical questions
├── Medication refill requests
├── Test result questions
├── Appointment scheduling
├── Billing questions
├── Referral requests
├── Medical records requests
└── General administrative

Urgent Care Disclaimer:
"This messaging system is not for urgent medical needs.
If you need immediate assistance, call 911 or go to the
nearest emergency room. For urgent but non-emergency
issues, call our office during business hours."
```

### 4. Prescription Management

**Medication Refills**:
```
Refill Request Process:
1. View current medications
2. Select medication for refill
3. Confirm pharmacy
4. Add notes (if needed)
5. Submit request
6. Provider approval
7. Pharmacy notification
8. Patient notification (ready for pickup)

Refill Information Displayed:
├── Medication name
├── Current dose
├── Last fill date
├── Refills remaining
├── Prescribing provider
├── Pharmacy location
└── Refill eligibility
```

**Pharmacy Management**:
```
Pharmacy Features:
├── View preferred pharmacy
├── Update pharmacy
│   ├── Search by name
│   ├── Search by ZIP code
│   ├── Search by address
│   └── Recent pharmacies
├── Multiple pharmacy options
│   ├── Retail pharmacy
│   ├── Mail-order pharmacy
│   └── Specialty pharmacy
└── View pharmacy details
    ├── Name and location
    ├── Phone number
    ├── Hours of operation
    └── NCPDP ID
```

### 5. Lab and Test Results

**Results Viewing**:
```
Lab Results Display:
├── Result overview
│   ├── Test date
│   ├── Ordering provider
│   ├── Status (final, preliminary, corrected)
│   └── Overall status indicator
├── Individual test results
│   ├── Test name (patient-friendly)
│   ├── Result value
│   ├── Units
│   ├── Reference range
│   ├── Abnormal flag (H, L, critical)
│   ├── Trend graph (if multiple results)
│   └── Provider comments
├── Result interpretation
│   ├── What does this mean? (patient education)
│   ├── Why was this test ordered?
│   └── Next steps
└── Download/print options
    ├── PDF download
    ├── Print-friendly format
    └── Include in health summary

Result Release Timing:
├── Normal results: Immediately upon finalization
├── Abnormal results: May be held for provider review
├── Critical results: Provider notification before release
└── Configurable by organization policy
```

**Result Notifications**:
```
Notification Options:
├── New results available
├── Abnormal result alert
├── Provider comment added
└── Follow-up action required

Notification Methods:
├── Email with link to portal
├── SMS alert
├── Push notification
└── In-portal notification
```

### 6. Bill Pay and Financial Management

**Billing Features**:
```
Account Balance:
├── Current balance
├── Itemized statements
│   ├── Date of service
│   ├── Provider/facility
│   ├── Service description
│   ├── Charges
│   ├── Insurance payments
│   ├── Adjustments
│   └── Patient responsibility
├── Payment history
│   ├── Payment date
│   ├── Payment amount
│   ├── Payment method
│   └── Applied to which service
└── Outstanding balances
    ├── Due immediately
    ├── Payment plan active
    └── Past due amounts

Payment Options:
├── One-time payment
│   ├── Full balance
│   └── Partial payment
├── Payment plans
│   ├── Set up monthly payments
│   ├── Auto-pay enrollment
│   └── Payment reminders
├── Payment methods
│   ├── Credit/debit card
│   ├── Bank account (ACH)
│   ├── Apple Pay/Google Pay
│   └── HSA/FSA card
└── Save payment methods
    ├── Tokenized storage
    ├── Default payment method
    └── Multiple payment methods

Financial Assistance:
├── View eligibility
├── Apply for assistance
├── Upload documentation
└── Track application status
```

### 7. Health Tracking and Personal Health Records

**Self-Reported Data**:
```
Trackable Metrics:
├── Vital Signs
│   ├── Blood pressure
│   ├── Blood glucose
│   ├── Weight
│   ├── Temperature
│   └── Oxygen saturation
├── Symptoms
│   ├── Pain level
│   ├── Symptom description
│   ├── Frequency
│   └── Triggers
├── Medications
│   ├── Adherence tracking
│   ├── Side effects
│   └── Effectiveness rating
├── Activities
│   ├── Exercise
│   ├── Sleep
│   └── Diet/nutrition
└── Mental Health
    ├── Mood tracking
    ├── Stress level
    └── PHQ-9 depression screening

Data Visualization:
├── Graphs and charts
├── Trend analysis
├── Goal tracking
└── Share with provider
```

**Device Integration**:
```
Connected Devices:
├── Fitness trackers (Fitbit, Apple Watch)
├── Blood pressure monitors
├── Glucose meters
├── Weight scales
├── Pulse oximeters
└── Continuous glucose monitors (CGM)

Integration Methods:
├── Apple Health integration
├── Google Fit integration
├── Direct device APIs
└── Manual data entry
```

### 8. Family and Proxy Access

**Proxy Account Features**:
```
Proxy Access Types:
├── Parent/Guardian access (minors)
│   ├── Full access until age of majority
│   ├── Automatic transition at 18
│   └── Sensitive information filtering
├── Caregiver access (adults)
│   ├── Patient-authorized access
│   ├── Limited or full access
│   ├── Revocable by patient
│   └── Audit trail of proxy actions
└── Legal representative access
    ├── Healthcare power of attorney
    ├── Court-appointed guardian
    └── Documentation required

Proxy Permissions:
├── View health information
├── Send/receive messages
├── Schedule appointments
├── Request prescription refills
├── View bills and make payments
└── Access medical records

Age-Based Rules:
├── 0-11: Full parent access
├── 12-17: Sensitive topics may be restricted
│   ├── Sexual health
│   ├── Mental health
│   ├── Substance abuse
│   └── Configurable by state law
└── 18+: Explicit patient authorization required
```

## Patient Portal Architecture

### Technical Stack

**Frontend**:
```
Web Portal:
├── Responsive design (mobile-friendly)
├── Accessibility (WCAG 2.1 AA compliance)
├── Browser compatibility
│   ├── Chrome, Firefox, Safari, Edge
│   └── Mobile browsers (iOS Safari, Chrome Mobile)
├── Progressive Web App (PWA) support
└── Technology choices:
    ├── React, Angular, or Vue.js
    ├── Bootstrap or Material-UI
    └── HTTPS only

Mobile Apps:
├── Native iOS app (Swift/SwiftUI)
├── Native Android app (Kotlin)
├── React Native (cross-platform option)
└── Features:
    ├── Biometric authentication
    ├── Push notifications
    ├── Offline access (limited)
    └── App store compliance
```

**Backend**:
```
API Layer:
├── RESTful APIs
├── FHIR R4 APIs (required)
├── OAuth 2.0 authentication
├── Rate limiting
└── Request/response logging

Database:
├── Patient portal data
├── Audit logs
├── Session management
└── Encrypted sensitive data

Integration Layer:
├── EHR integration
│   ├── HL7 interfaces
│   ├── FHIR APIs
│   └── Proprietary APIs
├── Third-party integrations
│   ├── Payment processors
│   ├── Identity verification
│   └── Telehealth platforms
└── HIE connectivity
    ├── Direct messaging
    └── Query-based exchange
```

### Security Architecture

**Authentication**:
```
Multi-Factor Authentication (MFA):
├── Username and password
├── Plus one of:
│   ├── SMS code
│   ├── Email code
│   ├── Authenticator app
│   ├── Biometric (mobile)
│   └── Security questions (legacy)

Identity Verification:
├── Initial registration
│   ├── Knowledge-based authentication (KBA)
│   ├── Email verification
│   ├── Phone verification
│   ├── In-person verification
│   └── Document upload (ID)
├── Password requirements
│   ├── Minimum 8 characters
│   ├── Uppercase, lowercase, number, symbol
│   ├── No common passwords
│   ├── Password history (no reuse)
│   └── Expiration policy (optional)
└── Account lockout
    ├── After 5 failed attempts
    ├── 30-minute lockout
    └── Account unlock process
```

**Authorization**:
```
Access Controls:
├── Role-based access
│   ├── Patient
│   ├── Proxy/caregiver
│   └── Minor with limited access
├── Resource-level permissions
├── Break-the-glass (emergency access)
└── Time-based restrictions
    └── Session timeout (15-30 minutes idle)
```

**Data Protection**:
```
Encryption:
├── Data in transit
│   ├── TLS 1.2+ required
│   ├── Certificate pinning (mobile)
│   └── HTTPS only
├── Data at rest
│   ├── Database encryption
│   ├── File encryption
│   └── Backup encryption

Privacy Controls:
├── HIPAA compliance
├── Data segmentation (sensitive data)
├── Minimum necessary access
├── De-identification options
└── Patient consent management
```

**Audit Logging**:
```
Logged Events:
├── User authentication
│   ├── Login success/failure
│   ├── Logout
│   └── Session timeout
├── Data access
│   ├── View health information
│   ├── Download records
│   ├── Share with third party
│   └── Proxy access
├── Data modifications
│   ├── Update demographics
│   ├── Add self-reported data
│   └── Message send/receive
└── Administrative actions
    ├── Account creation
    ├── Password reset
    └── Proxy access granted/revoked

Audit Log Details:
├── User ID
├── Action performed
├── Date and time
├── IP address
├── Resource accessed
└── Success/failure status
```

## Portal Adoption and Engagement

### Enrollment Strategies

**Patient Enrollment**:
```
Enrollment Methods:
├── In-person registration
│   ├── Front desk sign-up
│   ├── Kiosk registration
│   └── Provider-assisted enrollment
├── Online self-registration
│   ├── From practice website
│   ├── After office visit
│   └── Email invitation
├── Bulk enrollment
│   ├── Opt-out model
│   ├── Auto-enrollment after visit
│   └── Welcome email with instructions
└── Mobile app download
    └── App store registration

Enrollment Incentives:
├── Convenience messaging
├── Reduced wait times
├── 24/7 access to information
├── Paperless billing
└── Enhanced communication
```

### User Experience Optimization

**Usability Features**:
```
Navigation:
├── Intuitive menu structure
├── Search functionality
├── Breadcrumbs
├── Help/FAQ easily accessible
└── Recently viewed items

Accessibility:
├── Screen reader compatible
├── Keyboard navigation
├── High contrast mode
├── Adjustable font size
├── Alt text for images
└── WCAG 2.1 AA compliance

Personalization:
├── Dashboard customization
├── Preferred communication method
├── Language preference
├── Notification preferences
└── Saved searches/filters
```

**Patient Education**:
```
Educational Content:
├── Diagnosis explanations
├── Medication information
├── Test result interpretation
├── Pre/post-procedure instructions
├── Preventive health reminders
└── Disease management resources

Delivery Methods:
├── Inline contextual help
├── Video tutorials
├── PDF downloads
├── External links to trusted sources
└── Chatbot assistance
```

## Regulatory Compliance

### ONC Certification Requirements

**21st Century Cures Act**:
```
API Requirements:
├── FHIR R4 API (patient access)
├── OAuth 2.0 authentication
├── SMART on FHIR support
├── No blocking of patient access
├── USCDI data classes supported
└── Published API documentation

Data Access Timeline:
├── No delay in providing access
├── Lab results: Immediate release policy
├── Clinical notes: Upon finalization
├── No "gag clauses" in vendor contracts
```

### HIPAA Compliance

**Privacy Requirements**:
```
Patient Rights:
├── Right to access (within 30 days)
├── Right to amendment
├── Right to accounting of disclosures
├── Right to request restrictions
└── Right to confidential communications

Portal Compliance:
├── Notice of Privacy Practices acceptance
├── Authorization for disclosures
├── Minimum necessary access
├── Business Associate Agreements (vendors)
└── Breach notification procedures
```

### Meaningful Use / Promoting Interoperability

**Patient Engagement Measures**:
```
VDT (View, Download, Transmit):
├── >5% of patients must VDT
├── Within 4 days of availability
├── Download in computable format (C-CDA)
├── Transmit to third party
└── Track and report compliance

Patient-Generated Health Data:
├── Capture patient-entered data
├── Incorporate into EHR
├── Display to providers
└── Include in clinical workflow
```

## Analytics and Reporting

### Portal Usage Metrics

**Key Performance Indicators**:
```
Enrollment Metrics:
├── Total registered patients
├── % of eligible patients enrolled
├── New enrollments per month
├── Activation rate (registered → logged in)
└── Demographics of enrolled patients

Engagement Metrics:
├── Active users (monthly)
├── Login frequency
├── Session duration
├── Feature usage rates
│   ├── View lab results
│   ├── Send secure messages
│   ├── Request refills
│   ├── Schedule appointments
│   └── Make payments
├── Mobile vs. web usage
└── Patient satisfaction scores

Clinical Impact:
├── Reduction in phone calls
├── Reduction in no-shows
├── Medication adherence improvement
├── Patient-reported outcomes
└── Preventive care measure completion
```

### Reporting Dashboards

```
Administrative Dashboard:
├── Real-time portal usage
├── Peak usage times
├── Feature adoption rates
├── Error rates
├── Support ticket volume
└── Financial metrics (payments)

Clinical Dashboard:
├── Unread secure messages
├── Pending refill requests
├── Abnormal results requiring follow-up
├── Patient-generated health data
└── Missed appointment alerts
```

## Best Practices

### 1. User Onboarding
- Provide clear enrollment instructions
- Send welcome email with tutorial
- Offer in-person or phone assistance
- Create video walkthroughs
- Implement progressive disclosure for features

### 2. Communication
- Set clear response time expectations
- Use plain language, avoid medical jargon
- Provide multilingual support
- Implement read receipts
- Auto-response for after-hours messages

### 3. Mobile Optimization
- Responsive design for all screen sizes
- Native mobile apps for iOS and Android
- Biometric authentication support
- Push notifications for important updates
- Offline access to recent information

### 4. Continuous Improvement
- Collect user feedback regularly
- Monitor analytics and usage patterns
- Conduct usability testing
- A/B test new features
- Iterate based on patient needs

### 5. Support
- Comprehensive FAQ section
- Live chat or chatbot support
- Help desk phone number
- Video tutorials and guides
- Community forums (optional)

## References

- **ONC Patient Engagement Playbook**: https://www.healthit.gov/playbook/
- **HIPAA Patient Rights**: https://www.hhs.gov/hipaa/for-individuals/
- **21st Century Cures Act**: https://www.healthit.gov/curesrule/
- **WCAG Accessibility Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/

---

**Document Version**: 1.0
**Last Updated**: November 2024
**Author**: Healthcare Technology Team
**Classification**: Public - Educational Use
