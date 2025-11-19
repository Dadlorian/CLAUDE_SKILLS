# PropTech Technical Writing Style Guide

## Purpose

This guide establishes writing standards for all PropTech documentation, including API documentation, user guides, system architecture documents, and technical specifications. It ensures clarity, consistency, and professionalism across all real estate technology communications.

## Target Audiences

### Primary Audiences
1. **Property Managers**: Operations-focused, need clear workflows and procedures
2. **Real Estate Developers**: Integration-focused, need API docs and technical specs
3. **Building Engineers**: IoT/systems-focused, need configuration and troubleshooting guides
4. **System Administrators**: Infrastructure-focused, need deployment and security docs
5. **End Users (Tenants/Owners)**: Feature-focused, need simple how-to guides

### Secondary Audiences
- Executive stakeholders (for business impact documentation)
- Compliance officers (for regulatory documentation)
- Support teams (for troubleshooting guides)
- Training teams (for educational materials)

---

## Core Principles

### 1. Accuracy First
Real estate transactions involve significant financial stakes. **Accuracy is paramount.**

**Do**:
- Verify all property data, financial calculations, and regulatory requirements
- Include specific citations for compliance requirements (e.g., "Fair Housing Act §3604")
- Test all code examples and procedures before publication
- Use precise real estate terminology
- Double-check all numerical examples (rent calculations, prorations, late fees)

**Don't**:
- Round numbers unless explicitly noted
- Make assumptions about market conditions
- Oversimplify legal or regulatory requirements
- Use vague terms like "approximately" for financial calculations

**Example**:
```markdown
❌ Bad: "The tenant owes about $1,850 in prorated rent."
✅ Good: "The tenant owes $1,838.71 in prorated rent (calculated as $1,800 monthly rent × 31 days in the month × 31.5 days occupied)."
```

### 2. Clarity & Simplicity
PropTech serves diverse users with varying technical backgrounds.

**Do**:
- Use short sentences (15-20 words average)
- Define acronyms on first use: "Multiple Listing Service (MLS)"
- Provide context before technical details
- Use active voice: "The system calculates late fees" not "Late fees are calculated by the system"
- Include visual aids (screenshots, diagrams) for complex workflows

**Don't**:
- Assume domain knowledge
- Use jargon without explanation
- Write walls of text without structure
- Mix multiple concepts in one sentence

### 3. Consistency
Use standard terminology and formats across all documentation.

**Do**:
- Follow the terminology guide (below)
- Use consistent capitalization (see naming conventions)
- Apply uniform formatting for UI elements, code, and paths
- Maintain consistent structure across similar documents

**Don't**:
- Alternate between synonyms ("property" vs "unit" vs "asset" vs "listing")
- Change formatting conventions mid-document
- Use British vs American English inconsistently

### 4. Actionability
Users should know exactly what to do after reading documentation.

**Do**:
- Start procedures with clear outcomes: "To configure automated rent collection..."
- Use numbered steps for procedures
- Include expected results: "You should see a confirmation message"
- Provide troubleshooting for common issues
- Include "Next Steps" sections

**Don't**:
- Describe features without explaining how to use them
- Omit prerequisites or required permissions
- Leave users uncertain about success/failure
- Forget error handling and edge cases

---

## PropTech Terminology Guide

### Preferred Terms

| Use This | Not This | Context |
|----------|----------|---------|
| Property | Asset, Listing, Building (except when specific) | General reference to real estate |
| Unit | Apartment, Space (except when specific) | Individual rentable space |
| Tenant | Resident, Renter, Lessee | Person occupying a property |
| Owner | Landlord, Lessor | Property owner |
| Property Manager | Manager, PM | Professional managing properties |
| Lease | Rental Agreement | Legal occupancy contract |
| Rent Roll | Rent Report | List of tenants and rent |
| Common Area Maintenance (CAM) | CAM | Shared expense in commercial properties |
| Net Operating Income (NOI) | NOI | Property income after operating expenses |
| Security Deposit | Deposit | Tenant deposit held during lease |
| Automated Valuation Model (AVM) | Valuation Model, Estimate | ML-based property valuation |
| Building Automation System (BAS) | BMS, Building Management System | Smart building control system |
| Multiple Listing Service (MLS) | Listing Service | Real estate data cooperative |
| Property Management System (PMS) | Management Software | Software for property operations |

### Define on First Use
- **Cap Rate (Capitalization Rate)**: ROI metric for properties
- **Triple Net Lease (NNN)**: Tenant pays property expenses
- **Gross Lease**: Owner pays property expenses
- **BACnet**: Building automation and control networks protocol
- **RETS (Real Estate Transaction Standard)**: MLS data format
- **RESO (Real Estate Standards Organization)**: Industry data standards
- **LOI (Letter of Intent)**: Preliminary agreement to lease/purchase
- **PSF (Per Square Foot)**: Pricing metric ($X/sq ft)

### Real Estate Financial Terms - Always Define
- **NOI (Net Operating Income)**: Rental income minus operating expenses
- **DSC (Debt Service Coverage)**: Ratio of NOI to debt payments
- **IRR (Internal Rate of Return)**: Annualized return on investment
- **LTV (Loan to Value)**: Ratio of loan amount to property value
- **CoC (Cash on Cash Return)**: Annual return divided by initial investment

---

## Document Structure Standards

### API Documentation

#### Endpoint Documentation Template
```markdown
## [HTTP Method] [Endpoint Path]

**Description**: [One-sentence summary of what this endpoint does]

**Authentication**: [Required auth method: API key, OAuth 2.0, etc.]

**Rate Limit**: [Requests per minute/hour]

### Request

**Path Parameters**:
- `parameter_name` (type, required/optional): Description

**Query Parameters**:
- `parameter_name` (type, required/optional): Description. Default: value.

**Request Body**:
```json
{
  "field_name": "value_description"
}
```

**Field Descriptions**:
- `field_name` (type, required/optional): Description. Constraints.

### Response

**Success Response (200 OK)**:
```json
{
  "field_name": "value_description"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters. Returns `{"error": "description"}`
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Property not found
- `429 Too Many Requests`: Rate limit exceeded

### Examples

**Request**:
```bash
curl -X POST https://api.example.com/v1/properties \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "zip": "78701",
    "property_type": "multifamily",
    "units": 24
  }'
```

**Response**:
```json
{
  "property_id": "prop_1234567890",
  "address": "123 Main St",
  "created_at": "2025-01-15T10:30:00Z",
  "status": "active"
}
```

### Notes
- [Additional context, edge cases, related endpoints]
```

#### Example: Property Search Endpoint
```markdown
## GET /v1/properties/search

**Description**: Search properties with filters for price, location, type, and features.

**Authentication**: API key (header: `X-API-Key`)

**Rate Limit**: 100 requests per minute

### Request

**Query Parameters**:
- `city` (string, optional): City name. Example: "Austin"
- `state` (string, optional): Two-letter state code. Example: "TX"
- `min_price` (integer, optional): Minimum price in USD. Default: 0
- `max_price` (integer, optional): Maximum price in USD. Default: unlimited
- `bedrooms` (integer, optional): Minimum bedrooms. Range: 0-10
- `bathrooms` (number, optional): Minimum bathrooms. Range: 0-10. Supports half baths (e.g., 1.5)
- `property_type` (string, optional): One of: single_family, condo, townhouse, multifamily
- `page` (integer, optional): Page number. Default: 1
- `per_page` (integer, optional): Results per page. Range: 1-100. Default: 20

### Response

**Success Response (200 OK)**:
```json
{
  "properties": [
    {
      "property_id": "prop_1234",
      "address": "123 Main St",
      "city": "Austin",
      "state": "TX",
      "zip": "78701",
      "price": 450000,
      "bedrooms": 3,
      "bathrooms": 2.5,
      "sqft": 1850,
      "property_type": "single_family",
      "images": ["https://cdn.example.com/..."],
      "listed_date": "2025-01-10"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_results": 156,
    "total_pages": 8
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters (e.g., invalid state code, bedrooms > 10)
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Exceeded 100 requests/minute

### Examples

**Request**:
```bash
curl "https://api.example.com/v1/properties/search?city=Austin&state=TX&min_price=400000&bedrooms=3" \
  -H "X-API-Key: your_api_key_here"
```

### Notes
- Results are sorted by relevance (matching criteria + listing recency)
- For geospatial search (radius-based), use `/v1/properties/search/nearby` endpoint
- Property images are CDN URLs with 1-year cache expiration
```

### User Guide Structure

```markdown
# [Feature/Module Name]

## Overview
[2-3 sentence description of what this feature does and why it's useful]

## Prerequisites
- [Required permissions/roles]
- [Required configuration]
- [Related features that must be set up first]

## How It Works
[High-level explanation of the feature's logic and workflow]

## Step-by-Step Instructions

### Task 1: [Descriptive Task Name]

1. Navigate to [location in UI]
2. Click **[Button Name]**
3. Enter the following information:
   - **Field Name**: [What to enter and why]
   - **Another Field**: [Details]
4. Click **Save**
5. **Expected Result**: [What should happen]

**Screenshot**: [Insert annotated screenshot]

### Task 2: [Next Task]
[Continue pattern...]

## Common Issues & Troubleshooting

### Issue: [Common Problem]
**Symptoms**: [What the user sees]
**Cause**: [Why it happens]
**Solution**: [How to fix it]

## FAQs

**Q: [Common question]?**
A: [Clear answer]

## Related Features
- [Link to related documentation]
- [Link to API docs if applicable]

## Support
For additional help, contact [support method]
```

### Architecture Documentation

```markdown
# [System/Component Name] Architecture

## Executive Summary
[2-3 paragraphs for non-technical stakeholders explaining purpose and business value]

## System Overview

### Purpose
[What problem this system solves]

### Scope
[What's included and explicitly what's NOT included]

### Key Requirements
- [Functional requirement 1]
- [Non-functional requirement 1: performance, scalability, etc.]

## Architecture Diagram
[Include C4 model diagrams: Context, Container, Component, Code]

## Components

### Component 1: [Name]
**Responsibility**: [What this component does]
**Technology**: [Languages, frameworks, services]
**Key Interfaces**: [APIs, events, data stores]
**Scalability**: [How it scales]
**Dependencies**: [What it depends on]

## Data Model

### Entity: Property
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| property_id | UUID | Yes | Unique identifier |
| address | string(200) | Yes | Street address |
| city | string(100) | Yes | City name |
| state | char(2) | Yes | Two-letter state code |
| ... | ... | ... | ... |

**Relationships**:
- One-to-many with Units
- Many-to-one with Owners
- One-to-many with Leases

### Entity: [Next Entity]
[Continue...]

## API Contracts

### Internal APIs
[Document internal microservice APIs]

### External Integrations
- **MLS Integration**: RETS/RESO for property data
- **Payment Gateway**: Stripe for rent collection
- **Background Checks**: [Provider] for tenant screening

## Security

### Authentication & Authorization
[How users/systems authenticate and what permissions exist]

### Data Protection
- Encryption at rest: [Method]
- Encryption in transit: TLS 1.3
- PII handling: [Approach to personally identifiable information]

### Compliance
- **Fair Housing Act**: [How system ensures compliance]
- **PCI DSS**: [For payment processing]
- **GDPR/CCPA**: [Data privacy measures]

## Performance & Scalability

### Performance Targets
- API response time p95: < 300ms
- Property search: < 200ms
- Database query time p95: < 50ms
- Uptime: 99.9%

### Scalability Approach
- **Horizontal scaling**: [Which components]
- **Database sharding**: [Strategy, e.g., by geographic region]
- **Caching**: [Redis for session data, property listings]
- **CDN**: [For property images, videos]

## Monitoring & Alerting

### Metrics
- Request rate, error rate, latency (RED metrics)
- Database connection pool utilization
- Queue depth for async jobs
- [Domain-specific: properties indexed, searches/minute]

### Alerts
- Error rate > 1%: Page on-call engineer
- Latency p95 > 500ms: Slack notification
- [Critical alerts vs warnings]

## Disaster Recovery

### Backup Strategy
- Database backups: Every 6 hours, retained 30 days
- Document storage: Replicated across 3 regions
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour

### Failover
[Describe failover procedures for each critical component]

## Deployment

### Environments
- **Development**: Individual developer environments
- **Staging**: Production-like for QA
- **Production**: Multi-region deployment (US-East, US-West)

### Deployment Process
[CI/CD pipeline, rollback procedures]

## Future Considerations
- [Planned improvements]
- [Known technical debt]
- [Scalability limits and when to revisit architecture]

## References
- [Links to ADRs (Architecture Decision Records)]
- [Links to related documentation]
- [External references]
```

---

## Formatting Standards

### Text Formatting

#### UI Elements
- **Buttons**: Bold with exact capitalization: **Save Property**
- **Menu Items**: Bold: **Settings > Integrations**
- **Field Labels**: Bold: **Monthly Rent**
- **Tabs**: Bold: **Properties** tab

#### Code Elements
- **Inline Code**: Backticks: `property_id`
- **File Paths**: Backticks: `/var/log/proptech/app.log`
- **Environment Variables**: Backticks: `STRIPE_API_KEY`
- **API Endpoints**: Backticks: `GET /v1/properties/{id}`

#### Emphasis
- **Important Terms (First Use)**: Bold: **Net Operating Income (NOI)**
- **Warnings**: Use admonition blocks (see below)
- **User Input**: Italic: Enter *your API key*

### Code Blocks

#### Always Include Language Identifier
```python
# Calculate prorated rent
def calculate_prorated_rent(monthly_rent, move_in_date, days_in_month):
    """
    Calculate prorated rent for partial month occupancy.

    Args:
        monthly_rent (Decimal): Full month rent amount
        move_in_date (int): Day of month tenant moves in (1-31)
        days_in_month (int): Total days in the month (28-31)

    Returns:
        Decimal: Prorated rent amount, rounded to 2 decimals
    """
    days_occupied = days_in_month - move_in_date + 1
    daily_rate = monthly_rent / days_in_month
    return round(daily_rate * days_occupied, 2)
```

#### Include Comments for Complex Logic
```javascript
// Calculate late fees according to local regulations
function calculateLateFee(rentAmount, daysLate, stateCode) {
  // Most states limit late fees to 5-10% of monthly rent
  const maxLateFeePercent = STATE_LATE_FEE_LIMITS[stateCode] || 0.05;
  const maxLateFee = rentAmount * maxLateFeePercent;

  // Standard: $50 or 5% of rent, whichever is less
  const standardFee = 50;
  const lateFee = Math.min(standardFee, maxLateFee);

  // Some states allow additional daily charges after grace period
  if (daysLate > GRACE_PERIOD_DAYS && STATE_ALLOWS_DAILY_FEES[stateCode]) {
    const dailyFee = 5; // $5/day after grace period
    return lateFee + (dailyFee * (daysLate - GRACE_PERIOD_DAYS));
  }

  return lateFee;
}
```

### Lists

#### Unordered Lists
Use for non-sequential items:
```markdown
Features include:
- Automated rent collection
- Maintenance request tracking
- Financial reporting
- Tenant portal access
```

#### Ordered Lists
Use for sequential steps or rankings:
```markdown
To add a new property:
1. Click **Add Property**
2. Enter property details
3. Upload property images
4. Click **Save**
```

#### Nested Lists
Indent with 2 spaces:
```markdown
Property types supported:
- Residential
  - Single-family
  - Multifamily (2-4 units)
  - Multifamily (5+ units)
- Commercial
  - Office
  - Retail
  - Industrial
```

### Tables

#### Use for Structured Comparisons
```markdown
| Plan | Properties | Users | Price |
|------|-----------|-------|-------|
| Starter | Up to 10 | 3 | $49/month |
| Professional | Up to 100 | 10 | $199/month |
| Enterprise | Unlimited | Unlimited | Custom |
```

#### Use for Field Descriptions
```markdown
| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| monthly_rent | Decimal(10,2) | Yes | > 0, < 100000 |
| security_deposit | Decimal(10,2) | No | >= 0, <= monthly_rent * 3 |
| lease_start_date | Date | Yes | >= today |
```

### Admonitions (Callouts)

Use for important information that needs to stand out:

```markdown
> **Note**: Property images are cached for 24 hours. Changes may not appear immediately.

> **Warning**: Deleting a property will also delete all associated units, leases, and financial records. This action cannot be undone.

> **Tip**: Use the bulk import feature to add multiple properties from a CSV file.

> **Important**: Fair Housing regulations prohibit collecting certain applicant information. Ensure your application forms comply with local, state, and federal laws.
```

---

## Real Estate-Specific Writing Guidelines

### Financial Information

#### Always Specify Currency
```markdown
❌ Bad: "Monthly rent: 1,850"
✅ Good: "Monthly rent: $1,850.00 USD"
```

#### Show Calculations
```markdown
❌ Bad: "The prorated rent is $945.16"
✅ Good: "The prorated rent is $945.16, calculated as $1,800/month ÷ 31 days × 16 days occupied"
```

#### Round Consistently
- **Rents**: 2 decimal places ($1,234.56)
- **Percentages**: 2 decimal places (5.25% late fee)
- **Square footage**: Whole numbers (1,850 sq ft)
- **Acreage**: 2 decimal places (2.35 acres)

### Property Descriptions

#### Address Format
```markdown
Standard Format:
123 Main Street, Unit 4B
Austin, TX 78701

Database Storage (separate fields):
street_address: "123 Main Street"
unit_number: "4B"
city: "Austin"
state: "TX"
zip: "78701"
```

#### Property Types - Use Consistent Names
- **Single-Family**: Detached house, single unit
- **Condo**: Individual ownership within multi-unit building
- **Townhouse**: Multi-floor, shared walls, individual ownership
- **Multifamily (2-4 units)**: Duplex, triplex, fourplex
- **Multifamily (5+ units)**: Apartment complex
- **Commercial**: Office, retail, industrial, mixed-use

### Compliance & Legal

#### Fair Housing Language
```markdown
❌ Bad: "Perfect for families" (implies preference)
✅ Good: "3-bedroom, 2-bathroom home"

❌ Bad: "Great for young professionals" (age discrimination)
✅ Good: "Near downtown business district"

❌ Bad: "Walking distance to St. Mary's Church" (religious preference)
✅ Good: "Walkable neighborhood" or "Walk Score: 85"
```

#### Legal Disclaimers
Include when documenting features that touch on legal/financial advice:
```markdown
> **Legal Disclaimer**: This software provides tools for property management but does not constitute legal or financial advice. Consult with licensed professionals for legal, tax, and financial guidance. Landlord-tenant laws vary by jurisdiction; ensure compliance with local, state, and federal regulations.
```

### Accessibility

#### Alt Text for Images
```markdown
![Property search interface showing filters for location, price, bedrooms, and bathrooms](images/search-interface.png)

![Floor plan for 2-bedroom unit showing living room, kitchen, 2 bedrooms, and 1 bathroom](images/floorplan-2br.png)
```

#### Semantic HTML in Documentation
- Use proper heading hierarchy (H1 > H2 > H3)
- Use `<table>` for tabular data, not layout
- Use `<code>` for inline code, `<pre><code>` for blocks
- Use `<ul>/<ol>` for lists

---

## Review Checklist

Before publishing PropTech documentation, verify:

### Content
- [ ] All property data examples use realistic values
- [ ] Financial calculations are accurate and shown
- [ ] Fair housing compliance (no discriminatory language)
- [ ] Regulatory citations are current
- [ ] Code examples are tested
- [ ] All acronyms defined on first use

### Structure
- [ ] Clear heading hierarchy (H1 for title, H2 for sections, etc.)
- [ ] Logical flow (overview → details → examples → troubleshooting)
- [ ] Table of contents for docs > 3 pages
- [ ] Related docs linked

### Formatting
- [ ] Consistent terminology per guide
- [ ] UI elements bolded
- [ ] Code elements in backticks
- [ ] Proper code block language identifiers
- [ ] Tables properly formatted

### Accessibility
- [ ] Alt text for all images
- [ ] Proper heading structure
- [ ] Color not sole indicator of meaning
- [ ] Links have descriptive text (not "click here")

### Technical Accuracy
- [ ] API examples return valid responses
- [ ] Database schemas match implementation
- [ ] Architecture diagrams current
- [ ] Version-specific features noted

---

## Examples: Before & After

### Example 1: API Endpoint

**Before (Poor)**:
```markdown
## Get Property

GET /properties/{id}

Returns property data.

Response:
{
  "id": 123,
  "address": "123 Main St",
  ...
}
```

**After (Good)**:
```markdown
## GET /v1/properties/{property_id}

**Description**: Retrieve detailed information for a specific property by ID.

**Authentication**: Bearer token required

### Request

**Path Parameters**:
- `property_id` (string, required): Unique property identifier (format: `prop_` followed by 10-digit number)

### Response

**Success Response (200 OK)**:
```json
{
  "property_id": "prop_1234567890",
  "address": {
    "street": "123 Main Street",
    "unit": "4B",
    "city": "Austin",
    "state": "TX",
    "zip": "78701",
    "latitude": 30.2672,
    "longitude": -97.7431
  },
  "details": {
    "property_type": "multifamily",
    "year_built": 2015,
    "total_units": 24,
    "total_sqft": 28800,
    "parking_spaces": 36
  },
  "financial": {
    "purchase_price": 4800000,
    "current_value": 5200000,
    "annual_noi": 312000,
    "cap_rate": 6.0
  },
  "created_at": "2023-05-12T09:30:00Z",
  "updated_at": "2025-01-15T14:22:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing bearer token
- `404 Not Found`: Property with given ID does not exist
- `403 Forbidden`: User does not have access to this property

### Example

**Request**:
```bash
curl https://api.proptech.example.com/v1/properties/prop_1234567890 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Notes
- Property financial data is updated nightly
- For real-time property value estimates, use the `/v1/properties/{id}/valuation` endpoint
- Rate limit: 1000 requests per hour per API key
```

### Example 2: User Guide

**Before (Poor)**:
```markdown
## Adding a Lease

Go to the leases page and click add lease. Fill in the form and save.
```

**After (Good)**:
```markdown
## Creating a New Lease

### Overview
Create a new lease agreement to document tenant occupancy terms, rent amount, and lease duration. The system will automatically generate rent charges and track lease expiration.

### Prerequisites
- Property and unit must exist in the system
- Tenant application must be approved
- You must have **Property Manager** or **Owner** role

### Instructions

1. Navigate to **Properties > [Your Property] > Units > [Select Unit]**

2. In the **Leases** section, click **+ Create Lease**

3. **Tenant Information**:
   - Click **Select Tenant** and choose from approved applicants
   - Or click **+ Add New Tenant** to create a tenant record first

4. **Lease Terms**:
   - **Lease Start Date**: The date tenant takes possession (e.g., 2025-02-01)
   - **Lease End Date**: The date lease expires (e.g., 2026-01-31)
   - **Monthly Rent**: Enter base rent amount (e.g., $1,850.00)
   - **Security Deposit**: Typically 1-2 months rent (check local regulations)
   - **Lease Type**: Select one:
     - **Fixed Term**: Specific start and end dates
     - **Month-to-Month**: Automatically renews monthly

5. **Additional Charges** (Optional):
   - Click **+ Add Charge** to include:
     - Pet rent ($25-$75/month typical)
     - Parking fees
     - Storage fees
     - Utilities (if not included in rent)

6. **Move-In Charges**:
   - The system auto-calculates prorated rent if move-in date isn't the 1st
   - Review and adjust if needed
   - Example: Moving in Jan 15 with $1,800/month rent = $929.03 prorated ($1,800 ÷ 31 days × 17 days)

7. Click **Generate Lease Document** to create a PDF from your template

8. Review the lease document, then click **Send for Signature**

9. **Expected Result**: Tenant receives an email with DocuSign link. You'll get a notification when signed.

### After Lease Creation

Once the lease is signed:
- Rent charges will automatically post on the 1st of each month
- Late fees apply per your settings (typically 5 days after due date)
- Tenant receives access to the tenant portal
- Lease expiration reminders sent 90, 60, and 30 days before end date

### Common Issues

**Issue**: Can't find tenant in dropdown
**Solution**: Ensure tenant application is marked "Approved". Pending or Denied applicants won't appear.

**Issue**: Prorated rent seems wrong
**Solution**: System calculates as (monthly rent ÷ days in month × days occupied). Verify your move-in date is correct.

### Related Guides
- [Tenant Screening Process](#)
- [Setting Up Recurring Charges](#)
- [Lease Renewal Workflow](#)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-19 | Initial PropTech writing guide |

---

**Maintained By**: PropTech Documentation Team
**Questions**: docs@proptech.example.com
**Related**: See also [PropTech Naming Conventions](./proptech_naming_conventions.md) and [Documentation Standards](./proptech_documentation_standards.md)
