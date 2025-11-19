# Documate Platform Reference

## Overview

Documate is a no-code/low-code document automation platform designed for legal professionals who want to create automated workflows without extensive programming knowledge. It emphasizes ease of use, client-facing portals, and modern web-based interfaces.

## Platform Components

### Documate Builder
- Drag-and-drop interface builder
- Visual logic editor
- Template upload and management
- Preview and testing tools
- Version control

### Client Portal
- Branded client-facing interface
- Secure document generation
- Payment processing integration
- E-signature capabilities
- Mobile-responsive design

### Admin Dashboard
- User management
- Analytics and reporting
- Template organization
- Client management
- Billing and subscription management

## Template Creation

### Document Upload
```
Supported Formats:
- Microsoft Word (.docx)
- PDF forms (.pdf)
- Rich Text Format (.rtf)
- Google Docs (via import)
```

### Variable Mapping

#### Text Variables
```
Simple text input: {{client_name}}
Multi-line text: {{case_description}}
Email: {{client_email}}
Phone: {{client_phone}}
Address: {{client_address}}
```

#### Choice Variables
```
Dropdown: {{state}}
  - California
  - New York
  - Texas

Radio buttons: {{entity_type}}
  ○ Corporation
  ○ LLC
  ○ Partnership

Checkboxes: {{services_requested}}
  ☐ Estate Planning
  ☐ Business Formation
  ☐ Contract Review
```

#### Date Variables
```
Date picker: {{birth_date}}
Date range: {{employment_start}} to {{employment_end}}
Auto-fill today's date: {{current_date}}
```

#### Number Variables
```
Currency: {{contract_value}}
Percentage: {{ownership_percentage}}
Integer: {{number_of_shares}}
Decimal: {{interest_rate}}
```

### Conditional Logic

#### Show/Hide Sections
```yaml
Condition: Show "Spouse Information" section
  IF marital_status = "Married"
  THEN show spouse_name, spouse_dob, spouse_ssn
  ELSE hide section

Condition: Include arbitration clause
  IF include_arbitration = true
  THEN show arbitration_text
```

#### Nested Conditions
```yaml
Condition: Entity-specific provisions
  IF entity_type = "Corporation"
    THEN show corporate_provisions
    IF state_of_incorporation = "Delaware"
      THEN show delaware_specific_provisions
  ELSE IF entity_type = "LLC"
    THEN show llc_provisions
```

#### Multiple Condition Logic
```yaml
Condition: Executive compensation disclosure
  IF (employment_type = "Executive") AND (salary > 200000)
  THEN show compensation_disclosure

Condition: Complex eligibility
  IF (age >= 18) AND (state IN ["CA", "NY", "TX"]) AND (income > 50000)
  THEN eligible = true
```

### Calculated Fields

#### Mathematical Calculations
```yaml
Field: total_compensation
  Formula: base_salary + bonus + stock_value

Field: ownership_percentage
  Formula: (shares_owned / total_shares) * 100

Field: monthly_payment
  Formula: principal * (interest_rate / 12) / (1 - (1 + interest_rate / 12)^(-months))
```

#### Date Calculations
```yaml
Field: contract_end_date
  Formula: contract_start_date + (term_years * 365) days

Field: age
  Formula: YEARS_BETWEEN(birth_date, TODAY())

Field: notice_deadline
  Formula: termination_date - 30 days
```

#### Text Concatenation
```yaml
Field: full_name
  Formula: first_name + " " + middle_initial + " " + last_name

Field: full_address
  Formula: street_address + ", " + city + ", " + state + " " + zip_code

Field: formatted_phone
  Formula: "(" + area_code + ") " + phone_prefix + "-" + phone_line
```

### Repeating Sections

#### Simple List
```yaml
Repeating Section: "Children"
  Minimum: 0
  Maximum: 10
  Add button text: "Add Child"
  Remove button text: "Remove"

  Fields:
    - child_name (text)
    - child_dob (date)
    - child_ssn (text, optional)
```

#### Table Format
```yaml
Repeating Section: "Payment Schedule"
  Display as: Table

  Columns:
    - payment_date (date)
    - payment_amount (currency)
    - payment_description (text)

  Auto-calculate:
    - total_payments = SUM(payment_amount)
```

#### Nested Repeating Sections
```yaml
Repeating Section: "Shareholders"
  Fields:
    - shareholder_name
    - shareholder_address
    - total_shares_owned

  Nested Repeating Section: "Share Classes"
    Fields:
      - class_name
      - shares_in_class
      - price_per_share
```

## Questionnaire Design

### Page Structure
```yaml
Page 1: "Client Information"
  Description: "Please provide your basic information"
  Progress: 1 of 5

  Fields:
    - first_name (required)
    - last_name (required)
    - email (required, validated)
    - phone (required, formatted)

  Navigation:
    Next: "Matter Details"
    Skip: Not allowed
```

### Page Logic
```yaml
Page 2: "Entity Information"
  Condition: Show only if matter_type = "Business Formation"

  Fields:
    - entity_name
    - entity_type
    - state_of_formation

  Auto-skip: If matter_type != "Business Formation"
```

### Field Validation
```yaml
Field: email
  Validation: Email format
  Error message: "Please enter a valid email address"

Field: phone
  Validation: Phone format (###) ###-####
  Error message: "Please enter phone as (555) 555-5555"

Field: ssn
  Validation: Pattern ###-##-####
  Mask input: Yes
  Error message: "Please enter SSN as 123-45-6789"

Field: contract_value
  Validation: Minimum 1000, Maximum 10000000
  Error message: "Contract value must be between $1,000 and $10,000,000"
```

### Progress Indicators
```yaml
Progress Type: Step-by-step
Steps:
  1. Client Information (required)
  2. Matter Details (required)
  3. Additional Parties (conditional)
  4. Payment Information (required)
  5. Review and Submit (required)

Show percentage: Yes
Allow back navigation: Yes
Show page titles: Yes
```

## Client Portal Features

### Branding Customization
```yaml
Portal Settings:
  Logo: firm_logo.png
  Primary color: #1E3A8A
  Secondary color: #3B82F6
  Font: Inter, sans-serif

  Welcome message: "Welcome to [Firm Name]'s document portal"
  Footer text: "© 2025 [Firm Name]. All rights reserved."

  Custom domain: documents.lawfirm.com
  SSL certificate: Enabled
```

### Client Management
```yaml
Client Account:
  Email: client@example.com
  First login: Sends welcome email
  Password: Secure (8+ chars, complexity required)

  Access control:
    - View only assigned matters
    - Download generated documents
    - Complete questionnaires
    - Make payments

  Notifications:
    - Email on document ready
    - Email on payment due
    - Reminder emails for incomplete forms
```

### Document Delivery
```yaml
Delivery Options:
  1. Portal Download
     - Secure link
     - Expiration: 30 days
     - Download tracking

  2. Email Attachment
     - PDF attachment
     - Password protected
     - Encrypted email option

  3. Secure File Share
     - Box integration
     - Dropbox integration
     - Google Drive integration
```

## Payment Integration

### Stripe Integration
```javascript
// Payment configuration
{
  "provider": "Stripe",
  "public_key": "pk_live_...",
  "charge_timing": "before_document_generation",
  "amount_type": "fixed",
  "amount": 500.00,
  "currency": "USD",
  "description": "Estate Planning Package"
}

// Dynamic pricing
{
  "amount_type": "calculated",
  "formula": "base_fee + (hourly_rate * estimated_hours)",
  "variables": {
    "base_fee": 500,
    "hourly_rate": 350,
    "estimated_hours": 5
  }
}
```

### Payment Plans
```yaml
Payment Plan: "Installment Option"
  Initial payment: 25%
  Number of installments: 3
  Installment amount: 25% each
  Due dates:
    - Initial: Upon submission
    - Installment 1: 30 days
    - Installment 2: 60 days
    - Installment 3: 90 days

  Late fee: 5% per installment
  Access control: Release document after initial payment
```

### Invoice Generation
```yaml
Invoice Settings:
  Auto-generate: Yes
  Include items:
    - Service description
    - Line item breakdown
    - Subtotal
    - Tax (if applicable)
    - Total amount

  Payment terms: Net 30
  Late payment terms: 1.5% per month
  Accept payments:
    - Credit card (Stripe)
    - ACH transfer
    - Check (manual confirmation)
```

## Workflow Automation

### Email Notifications
```yaml
Trigger: Document completed
  Send to: client_email
  Subject: "Your {{document_name}} is ready"
  Body: |
    Dear {{client_name}},

    Your {{document_name}} has been prepared and is ready for download.

    Click here to access your document: {{document_link}}

    This link will expire in 30 days.

    Best regards,
    {{firm_name}}

  Attachments:
    - Generated document (PDF)
    - Instructions (optional)
```

### Multi-step Workflows
```yaml
Workflow: "Estate Planning Package"

  Step 1: Initial Questionnaire
    Form: client_intake
    Notification: "Please complete your intake form"

  Step 2: Document Review (conditional)
    Condition: review_required = true
    Assignee: attorney@lawfirm.com
    Due: 2 business days

  Step 3: Client Approval
    Notification: "Please review your documents"
    Actions:
      - Approve → Step 4
      - Request changes → Return to Step 2

  Step 4: Payment
    Amount: package_price
    Method: Stripe

  Step 5: Final Delivery
    Actions:
      - Generate final documents
      - Send to client
      - Archive in case management system
```

### Zapier Integration
```yaml
Trigger: New Document Generated
  → Action: Create row in Google Sheets
  Mapping:
    - client_name → Column A
    - document_type → Column B
    - generation_date → Column C
    - status → Column D

Trigger: Payment Received
  → Action: Create invoice in QuickBooks
  Mapping:
    - client_name → Customer
    - amount → Amount
    - service_description → Description

Trigger: Form Completed
  → Action: Create task in Asana
  Mapping:
    - "Review document for {{client_name}}"
    - Assignee: Document reviewer
    - Due date: 2 days from now
```

## API Access

### REST API Endpoints
```
GET    /api/v1/templates
GET    /api/v1/templates/{id}
POST   /api/v1/sessions
POST   /api/v1/sessions/{id}/answers
GET    /api/v1/sessions/{id}
POST   /api/v1/sessions/{id}/generate
GET    /api/v1/documents/{id}
```

### API Example
```javascript
// Create a new session
const session = await fetch('https://api.documate.org/api/v1/sessions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    template_id: 'template_abc123',
    client_email: 'client@example.com'
  })
});

const sessionData = await session.json();

// Submit answers
await fetch(`https://api.documate.org/api/v1/sessions/${sessionData.id}/answers`, {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    answers: {
      client_name: 'John Doe',
      client_email: 'john@example.com',
      matter_type: 'Estate Planning'
    }
  })
});

// Generate document
const doc = await fetch(`https://api.documate.org/api/v1/sessions/${sessionData.id}/generate`, {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + apiKey
  }
});

const documentUrl = await doc.json();
```

## Analytics & Reporting

### Usage Metrics
```yaml
Metrics Tracked:
  - Number of documents generated
  - Completion rate (started vs. completed)
  - Average completion time
  - Abandonment points
  - Most used templates
  - Revenue by template
  - Client satisfaction ratings

Reports Available:
  - Daily activity summary
  - Monthly revenue report
  - Template performance
  - Client engagement
  - Conversion funnel
```

### Custom Dashboards
```yaml
Dashboard: "Monthly Performance"
  Widgets:
    - Total documents generated (number)
    - Revenue generated (currency)
    - Completion rate (percentage)
    - Top 5 templates (table)
    - Documents by type (pie chart)
    - Daily activity (line graph)

  Filters:
    - Date range
    - Template category
    - Client type

  Export options:
    - PDF report
    - Excel spreadsheet
    - CSV data
```

## Best Practices

### Template Design
1. Keep questionnaires short and focused
2. Use progressive disclosure for complex forms
3. Provide clear field labels and help text
4. Set appropriate default values
5. Group related fields logically

### User Experience
1. Mobile-first design approach
2. Clear progress indicators
3. Save and resume functionality
4. Inline validation with helpful error messages
5. Preview before final generation

### Security
1. Enable two-factor authentication
2. Use strong password requirements
3. Encrypt documents at rest and in transit
4. Regular security audits
5. GDPR and privacy compliance

### Performance
1. Optimize document templates for fast generation
2. Use caching for frequently accessed templates
3. Minimize external API calls
4. Compress large PDF outputs
5. Monitor system performance metrics

## Pricing & Plans

### Plan Tiers
```
Starter: $99/month
  - 5 templates
  - 100 documents/month
  - Basic branding
  - Email support

Professional: $299/month
  - Unlimited templates
  - 500 documents/month
  - Full branding
  - Payment processing
  - Priority support

Enterprise: Custom pricing
  - Unlimited everything
  - API access
  - Custom integrations
  - Dedicated support
  - SLA guarantees
```

## Resources

- **Documentation**: https://help.documate.org
- **Video Tutorials**: Documate YouTube Channel
- **Community**: Documate User Community
- **Support**: support@documate.org
- **Status Page**: https://status.documate.org
