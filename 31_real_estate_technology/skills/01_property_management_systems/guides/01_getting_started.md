# Getting Started with Property Management Systems

## Overview
This guide walks through setting up a property management system from scratch, covering initial configuration, data import, and go-live preparation.

## Prerequisites

### Technical Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Stable internet connection (10+ Mbps recommended)
- Email account for notifications
- Mobile device for mobile app (iOS 13+ or Android 8+)

### Data Requirements
- Property information (addresses, units, amenities)
- Existing tenant data (if migrating from another system)
- Lease agreements and terms
- Financial data (chart of accounts, GL codes)
- Vendor contact information

### Access Requirements
- Admin credentials from PMS provider
- Banking information for ACH setup
- API keys for integrations (payment processing, accounting)
- Domain access for custom portal URLs

## Step 1: System Configuration

### 1.1 Company Setup

**Navigate to**: Settings → Company Information

**Required Information**:
```
Company Legal Name: Premier Property Management LLC
DBA (Doing Business As): Premier Properties
Tax ID (EIN): 12-3456789
Business Address: 123 Main Street, Suite 100, Austin, TX 78701
Primary Phone: +1-555-123-4567
Primary Email: info@premierproperties.com
Website: https://www.premierproperties.com
```

**Financial Settings**:
```
Fiscal Year Start: January 1
Default Currency: USD
Tax Reporting Method: Accrual
Late Fee Policy: $75 flat or 5% of rent, whichever is greater
Grace Period: 5 days
NSF Fee: $50
```

### 1.2 User Management

**Create User Roles**:

1. **Portfolio Manager** (Full Access)
   - All properties
   - Financial reports
   - User management
   - System configuration

2. **Property Manager** (Property-Level)
   - Assigned properties only
   - Lease management
   - Tenant communication
   - Work orders

3. **Leasing Agent** (Limited)
   - Lead management
   - Showings and tours
   - Applications
   - Read-only financial access

4. **Maintenance Technician** (Work Orders Only)
   - View and update work orders
   - No financial access
   - Limited tenant information

**Add Users**:
```
Name: Jane Smith
Email: jane.smith@premierproperties.com
Role: Property Manager
Properties: Sunset Apartments, River View Towers
Mobile: +1-555-234-5678
```

### 1.3 Chart of Accounts Setup

**Income Accounts**:
```
4000 - Rental Income
  4100 - Base Rent
  4110 - Pet Rent
  4120 - Parking Income
  4130 - Storage Income
  4140 - Late Fees
  4150 - NSF Fees
  4160 - Utility Reimbursements
  4170 - Other Income
```

**Expense Accounts**:
```
5000 - Operating Expenses
  5100 - Payroll
    5110 - Salaries
    5120 - Benefits
    5130 - Payroll Taxes
  5200 - Maintenance & Repairs
    5210 - Plumbing
    5220 - Electrical
    5230 - HVAC
    5240 - Appliances
    5250 - General Repairs
  5300 - Utilities
    5310 - Water/Sewer
    5320 - Electricity
    5330 - Gas
    5340 - Trash
  5400 - Property Taxes
  5500 - Insurance
  5600 - Marketing & Advertising
  5700 - Professional Fees
  5800 - Administrative
```

### 1.4 Document Templates

**Configure Lease Template**:
- Upload your standard lease agreement
- Map merge fields (tenant name, unit, rent amount, dates)
- Set signing order (tenant → co-signer → landlord)
- Configure e-signature settings

**Other Document Templates**:
- Move-in checklist
- Move-out checklist
- Notice to vacate form
- Lease renewal offer
- Violation notice
- Rent increase notice

## Step 2: Property Setup

### 2.1 Add Your First Property

**Navigate to**: Properties → Add New Property

**Basic Information**:
```
Property Name: Sunset Apartments
Property Type: Multifamily
Address: 456 Sunset Boulevard
City: Austin
State: TX
ZIP: 78701
Country: USA
```

**Property Details**:
```
Year Built: 2015
Total Units: 150
Total Square Feet: 120,000
Lot Size: 3.5 acres
Parking Spaces: 200
Number of Buildings: 3
Number of Floors per Building: 5
```

**Financial Information**:
```
Acquisition Date: 2020-01-15
Acquisition Price: $25,000,000
Current Value: $32,000,000
Property Tax Account: 12345678
Annual Property Tax: $280,000
```

**Amenities**:
- ☑ Swimming Pool
- ☑ Fitness Center
- ☑ Business Center
- ☑ Dog Park
- ☑ Package Lockers
- ☑ Controlled Access
- ☑ On-Site Laundry
- ☐ Valet Trash

### 2.2 Configure Buildings (if applicable)

**Building 1**:
```
Building Name: Building A
Floors: 5
Units per Floor: 10
Total Units: 50
```

### 2.3 Add Units

**Manual Entry Example**:
```
Unit Number: A-101
Building: Building A
Floor: 1
Unit Type: 2 Bedroom / 2 Bathroom
Square Feet: 950
Market Rent: $2,200
Security Deposit: $2,200
Status: Vacant
Availability Date: 2024-12-01
```

**Features**:
- Balcony: Yes
- Washer/Dryer Hookup: Yes
- Walk-in Closet: Yes
- Fireplace: No
- Pets Allowed: Yes (2 max, 50 lbs each)

**Bulk Import via CSV**:
```csv
unit_number,building,floor,unit_type,sq_ft,bedrooms,bathrooms,market_rent
A-101,Building A,1,2BR/2BA,950,2,2.0,2200
A-102,Building A,1,1BR/1BA,750,1,1.0,1800
A-103,Building A,1,2BR/2BA,950,2,2.0,2200
```

Upload: Properties → Sunset Apartments → Units → Bulk Import

### 2.4 Unit Photos

**Best Practices**:
- Professional photography recommended
- Minimum 10 photos per unit type
- Include: living room, kitchen, bedrooms, bathrooms, balcony
- 1920x1080 resolution minimum
- Good lighting, staged if possible

**Upload Process**:
1. Select unit or unit type
2. Click "Upload Photos"
3. Drag and drop images
4. Add captions and reorder
5. Set featured image

## Step 3: Tenant and Lease Migration

### 3.1 Prepare Migration Data

**Create CSV Template**:
```csv
unit_number,tenant_first_name,tenant_last_name,tenant_email,tenant_phone,lease_start,lease_end,monthly_rent,security_deposit,move_in_date
A-101,John,Doe,john@example.com,555-123-4567,2024-01-01,2024-12-31,2200,2200,2024-01-01
A-102,Jane,Smith,jane@example.com,555-234-5678,2023-06-01,2024-05-31,1800,1800,2023-06-01
```

### 3.2 Import Data

**Navigate to**: Data Import → Tenants & Leases

**Import Steps**:
1. Download CSV template
2. Fill in your data
3. Upload CSV file
4. Map columns to fields
5. Validate data
6. Review preview
7. Confirm import

**Validation Checks**:
- All required fields present
- Dates in correct format (YYYY-MM-DD)
- No overlapping leases on same unit
- Email addresses valid
- Phone numbers formatted correctly

### 3.3 Historical Ledger Import

**Ledger CSV Template**:
```csv
unit_number,tenant_email,transaction_date,transaction_type,charge_code,amount,description
A-101,john@example.com,2024-11-01,charge,RENT,2200,November Rent
A-101,john@example.com,2024-11-03,payment,ACH,-2200,November Rent Payment
A-102,jane@example.com,2024-11-01,charge,RENT,1800,November Rent
```

**Import Options**:
- Full history (recommended for audit trail)
- Current balances only (faster, loses history)
- Since specific date (hybrid approach)

## Step 4: Payment Processing Setup

### 4.1 Connect Stripe

**Navigate to**: Settings → Integrations → Payment Processing

**Steps**:
1. Click "Connect Stripe Account"
2. Sign in to Stripe (or create account)
3. Authorize access
4. Configure payment methods:
   - ☑ ACH/Bank Transfer (free for tenants)
   - ☑ Credit Card (2.9% + 30¢ fee)
   - ☑ Debit Card (2.9% + 30¢ fee)

**Fee Configuration**:
```
Pass fees to tenant: Yes
ACH Fee: $0 (absorbed by landlord)
Card Fee: 2.9% + $0.30 (passed to tenant)
```

### 4.2 Bank Account Setup

**For Receiving Payments**:
```
Bank Name: Chase Bank
Account Type: Business Checking
Routing Number: 021000021
Account Number: 123456789
Account Holder: Premier Property Management LLC
```

**For Disbursements (Owner Distributions)**:
- Can add multiple owner bank accounts
- Set up distribution schedules (monthly, quarterly)

### 4.3 Configure Rent Collection

**Autopay Settings**:
```
Enable Autopay: Yes
Autopay Day: 1st of month
Retry Failed Payments: Yes
Retry Schedule: Days 3, 5, 7 after failure
Maximum Retries: 3
```

**Payment Reminders**:
```
First Reminder: 3 days before due date
Second Reminder: On due date (if not paid)
Third Reminder: 1 day after grace period
Late Fee Notice: Day late fee is applied
```

## Step 5: Tenant Portal Configuration

### 5.1 Branding

**Portal URL**: `https://sunset-apartments.yourpms.com`

**Custom Domain** (Optional): `https://residents.sunsetapts.com`

**Branding**:
- Upload logo (300x100px recommended)
- Primary color: #1E40AF (blue)
- Accent color: #10B981 (green)
- Welcome message customization

### 5.2 Enable Portal Features

**Available Features**:
- ☑ Pay Rent
- ☑ Set up Autopay
- ☑ View Lease
- ☑ Submit Maintenance Requests
- ☑ View Payment History
- ☑ Download Tax Documents
- ☑ Update Contact Information
- ☑ Request Lease Renewal
- ☑ Give Notice to Vacate
- ☑ Community Announcements

### 5.3 Tenant Invitation

**Send Portal Invites**:
1. Navigate to Tenants → All Tenants
2. Select tenants
3. Click "Send Portal Invitations"
4. Customize invitation email
5. Send

**Email Template**:
```
Subject: Welcome to Your Sunset Apartments Resident Portal!

Hi [Tenant Name],

We're excited to introduce your new resident portal! You can now:
- Pay rent online (no checks or money orders needed!)
- Submit maintenance requests 24/7
- View your lease and payment history
- Set up automatic payments

Get started: [Portal URL]
Your temporary password: [Temporary Password]

Questions? Reply to this email or call us at (555) 123-4567.

Best regards,
Sunset Apartments Management
```

## Step 6: Integrations

### 6.1 Accounting Integration (QuickBooks)

**Navigate to**: Settings → Integrations → Accounting

**Steps**:
1. Click "Connect QuickBooks"
2. Sign in to QuickBooks
3. Authorize access
4. Map accounts:
   - Rental Income → QuickBooks Income Account
   - Security Deposits → QuickBooks Liability Account
   - Each property → QuickBooks Customer

**Sync Settings**:
```
Sync Frequency: Daily at 2:00 AM
Sync Items:
  - ☑ Invoices (rent charges)
  - ☑ Payments
  - ☑ Journal Entries (adjustments)
  - ☑ Vendors
Starting Date: 2024-01-01
```

### 6.2 Screening Integration (TransUnion)

**Navigate to**: Settings → Integrations → Tenant Screening

**Configuration**:
```
Provider: TransUnion SmartMove
API Key: [Your API Key]
Products:
  - ☑ Credit Report
  - ☑ Criminal Background
  - ☑ Eviction History
Cost: $35 per application (pass to applicant)
```

### 6.3 Listing Syndication

**Syndicate to**:
- ☑ Apartments.com
- ☑ Zillow
- ☑ Trulia
- ☑ Rent.com
- ☑ Craigslist (requires manual setup per city)
- ☑ Facebook Marketplace

**Automated Syndication**:
- Listings auto-update when availability changes
- Photos sync automatically
- Pricing updates propagate within 1 hour

## Step 7: Mobile App Setup

### 7.1 Download Apps

**For Property Managers**:
- iOS: Search "YourPMS Manager" in App Store
- Android: Search "YourPMS Manager" in Play Store

**For Tenants**:
- iOS: Search "YourPMS Resident" in App Store
- Android: Search "YourPMS Resident" in Play Store

### 7.2 Manager App Configuration

**Sign In**:
- Email: your@email.com
- Password: your password
- Enable Face ID / Touch ID (recommended)

**Enable Notifications**:
- ☑ New Work Orders
- ☑ Maintenance Updates
- ☑ Payments Received
- ☑ New Applications
- ☑ Lease Expirations

**Offline Mode**:
- Download property data for offline access
- Sync when back online

## Step 8: Testing Before Go-Live

### 8.1 Test Rent Payment Flow

1. Create test tenant account
2. Submit rent payment with test card (4242 4242 4242 4242)
3. Verify payment posts to ledger
4. Check webhook delivery
5. Confirm accounting sync

### 8.2 Test Lease Workflow

1. Create test application
2. Run screening (use sandbox mode)
3. Approve application
4. Generate lease
5. E-sign lease
6. Verify move-in costs calculated correctly

### 8.3 Test Maintenance Workflow

1. Submit work order from tenant portal
2. Assign to vendor
3. Update status
4. Complete work order
5. Verify tenant notification

### 8.4 Test Reporting

1. Generate rent roll
2. Generate income statement
3. Generate delinquency report
4. Export reports to PDF/Excel
5. Verify data accuracy

## Step 9: Staff Training

### 9.1 Training Schedule

**Week 1: Property Managers**
- System overview
- Property and unit management
- Lease creation and management
- Financial reporting

**Week 2: Leasing Agents**
- Lead management
- Showing scheduling
- Application processing
- Lease signing

**Week 3: Maintenance Staff**
- Work order management
- Mobile app usage
- Vendor coordination

### 9.2 Training Resources

- Video tutorials (in-app)
- Live webinar sessions
- PDF user guides
- Sandbox environment for practice

## Step 10: Go-Live

### 10.1 Go-Live Checklist

**Pre-Launch** (1 week before):
- ☐ All properties added
- ☐ All units configured
- ☐ All tenants migrated
- ☐ Historical data imported
- ☐ Payment processing tested
- ☐ Integrations connected
- ☐ Staff trained
- ☐ Portal invitations ready

**Launch Day**:
- ☐ Send portal invitations to all tenants
- ☐ Activate automatic rent reminders
- ☐ Enable online payments
- ☐ Turn off old system (if replacing)
- ☐ Monitor for issues
- ☐ Support team on standby

**Post-Launch** (First Week):
- ☐ Monitor portal adoption rate
- ☐ Address tenant questions
- ☐ Fix any issues immediately
- ☐ Collect staff feedback
- ☐ Optimize workflows

### 10.2 Success Metrics (First 30 Days)

**Adoption Targets**:
- Portal registration: 70%+
- Online payment adoption: 60%+
- Work order submissions via portal: 50%+
- Staff satisfaction: 8/10+

**Support Volume**:
- Week 1: High (expected)
- Week 2: Moderate
- Week 3-4: Normalizing

## Ongoing Optimization

### Monthly Tasks
- Review financial reports
- Analyze occupancy trends
- Monitor collection rates
- Review work order metrics
- Check integration sync status

### Quarterly Tasks
- Staff refresher training
- Review and update processes
- Analyze tenant feedback
- Evaluate new features
- Update document templates

### Annual Tasks
- Comprehensive system audit
- Renewal of integrations/subscriptions
- Major process improvements
- Strategic planning

## Getting Help

### Support Resources
- **Knowledge Base**: help.yourpms.com
- **Support Email**: support@yourpms.com
- **Phone**: 1-800-PMS-HELP (24/7)
- **Live Chat**: Available in app (8am-8pm EST)
- **Community Forum**: community.yourpms.com

### Escalation Path
1. Knowledge Base / Help Articles
2. Live Chat / Email Support
3. Phone Support
4. Escalation to Tier 2/Engineering
5. Account Manager (enterprise clients)

Congratulations! Your property management system is now fully operational and ready to streamline your property operations.
