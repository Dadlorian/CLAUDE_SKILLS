# Property Data Model Reference

## Overview
Complete reference for the property management data model, including all entities, relationships, and key attributes used in modern PMS platforms.

## Core Entities

### Property
The physical real estate asset.

**Key Attributes:**
```
property_id (UUID, PK)
property_name (VARCHAR)
property_type (ENUM: multifamily, commercial, mixed_use, industrial)
street_address (VARCHAR)
city (VARCHAR)
state (CHAR(2))
postal_code (VARCHAR)
country (CHAR(2), default: 'US')
latitude (DECIMAL)
longitude (DECIMAL)
year_built (INT)
total_units (INT)
total_square_feet (DECIMAL)
lot_size_acres (DECIMAL)
parking_spaces (INT)
tax_id_number (VARCHAR)
legal_description (TEXT)
acquisition_date (DATE)
acquisition_price (DECIMAL)
current_value (DECIMAL)
status (ENUM: active, inactive, under_construction, sold)
portfolio_id (UUID, FK)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Relationships:**
- Has many: Units, Buildings, Amenities, Documents
- Belongs to: Portfolio, Owner(s)
- Has many through: Leases, Tenants, Work Orders

### Unit
Individual rentable space within a property.

**Key Attributes:**
```
unit_id (UUID, PK)
property_id (UUID, FK)
building_id (UUID, FK, nullable)
unit_number (VARCHAR)
unit_type (ENUM: studio, 1br, 2br, 3br, 4br, penthouse, commercial)
floor_number (INT)
square_feet (DECIMAL)
bedrooms (DECIMAL) -- can be 0.5 for studio
bathrooms (DECIMAL) -- can be 1.5, 2.5, etc.
market_rent (DECIMAL)
current_rent (DECIMAL)
security_deposit_amount (DECIMAL)
pet_deposit_amount (DECIMAL)
unit_status (ENUM: occupied, vacant, notice_given, maintenance, offline)
lease_status (ENUM: leased, vacant, pending, notice)
availability_date (DATE)
last_renovation_date (DATE)
features (JSONB) -- balcony, fireplace, etc.
amenities (JSONB) -- in-unit washer/dryer, dishwasher
accessibility (BOOLEAN)
smoking_allowed (BOOLEAN)
pets_allowed (BOOLEAN)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Common Queries:**
```sql
-- Available units for lease
SELECT * FROM units
WHERE unit_status = 'vacant'
  AND availability_date <= CURRENT_DATE
ORDER BY availability_date;

-- Units with rent loss-to-lease
SELECT unit_number, market_rent, current_rent,
       (market_rent - current_rent) AS loss_to_lease,
       ROUND(((market_rent - current_rent) / market_rent) * 100, 2) AS loss_percentage
FROM units
WHERE unit_status = 'occupied'
ORDER BY loss_to_lease DESC;
```

### Lease
Legal agreement for unit rental.

**Key Attributes:**
```
lease_id (UUID, PK)
unit_id (UUID, FK)
property_id (UUID, FK)
lease_number (VARCHAR, unique)
lease_type (ENUM: fixed, month_to_month, commercial, percentage)
lease_status (ENUM: draft, pending, active, expired, terminated, renewed)
start_date (DATE)
end_date (DATE)
notice_date (DATE, nullable)
move_in_date (DATE)
move_out_date (DATE, nullable)
base_rent (DECIMAL)
market_rent_at_signing (DECIMAL)
security_deposit (DECIMAL)
pet_deposit (DECIMAL)
pet_rent (DECIMAL)
parking_rent (DECIMAL)
storage_rent (DECIMAL)
total_monthly_rent (DECIMAL)
rent_due_day (INT, 1-31)
late_fee_amount (DECIMAL)
late_fee_grace_days (INT)
lease_term_months (INT)
renewal_count (INT, default: 0)
previous_lease_id (UUID, FK, nullable)
payment_method (ENUM: ach, credit_card, check, money_order, cash)
autopay_enabled (BOOLEAN)
lease_document_url (VARCHAR)
signed_date (DATE)
renewal_offered (BOOLEAN)
renewal_offer_date (DATE, nullable)
special_terms (TEXT)
created_by_user_id (UUID, FK)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Business Rules:**
- End date must be after start date
- Notice date must be before end date
- Total monthly rent = base_rent + pet_rent + parking_rent + storage_rent
- Security deposit typically 1-2x monthly rent
- Grace period typically 3-5 days

### Tenant
Individual or entity renting property.

**Key Attributes:**
```
tenant_id (UUID, PK)
tenant_type (ENUM: individual, corporate, guarantor)
first_name (VARCHAR)
last_name (VARCHAR)
company_name (VARCHAR, nullable)
email (VARCHAR, unique)
phone_primary (VARCHAR)
phone_secondary (VARCHAR, nullable)
date_of_birth (DATE)
ssn_last_4 (CHAR(4))
drivers_license_number (VARCHAR)
drivers_license_state (CHAR(2))
emergency_contact_name (VARCHAR)
emergency_contact_phone (VARCHAR)
employer_name (VARCHAR)
employer_phone (VARCHAR)
annual_income (DECIMAL)
credit_score (INT)
background_check_status (ENUM: pending, approved, denied)
background_check_date (DATE)
tenant_status (ENUM: applicant, approved, current, former, evicted)
move_in_date (DATE, nullable)
move_out_date (DATE, nullable)
portal_access_enabled (BOOLEAN)
communication_preferences (JSONB)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**Privacy Considerations:**
- Never store full SSN, only last 4 digits
- Encrypt sensitive PII (date of birth, drivers license)
- Implement field-level access control
- Audit all access to tenant records

### Lease_Tenant (Junction Table)
Links tenants to leases (many-to-many).

**Key Attributes:**
```
lease_tenant_id (UUID, PK)
lease_id (UUID, FK)
tenant_id (UUID, FK)
relationship_type (ENUM: primary, co_tenant, occupant, guarantor)
responsible_for_payment (BOOLEAN)
percentage_liability (DECIMAL, 0-100)
move_in_date (DATE)
move_out_date (DATE, nullable)
created_at (TIMESTAMP)
```

### Ledger
Financial transaction ledger for each lease.

**Key Attributes:**
```
ledger_id (UUID, PK)
lease_id (UUID, FK)
tenant_id (UUID, FK)
property_id (UUID, FK)
transaction_date (DATE)
post_date (DATE)
transaction_type (ENUM: charge, payment, credit, adjustment)
charge_code (VARCHAR) -- rent, late_fee, pet_rent, etc.
description (VARCHAR)
amount (DECIMAL)
balance (DECIMAL) -- running balance after this transaction
payment_method (ENUM: ach, credit_card, check, money_order, cash, waiver)
reference_number (VARCHAR) -- check number, transaction ID
gl_account (VARCHAR) -- general ledger account code
is_recurring (BOOLEAN)
parent_transaction_id (UUID, FK, nullable)
reversed (BOOLEAN)
reversal_transaction_id (UUID, FK, nullable)
notes (TEXT)
created_by_user_id (UUID, FK)
created_at (TIMESTAMP)
```

**Common Charge Codes:**
- RENT: Base monthly rent
- LATE: Late fee
- PET: Pet rent
- PARK: Parking fee
- UTIL: Utility charges
- NSF: Non-sufficient funds fee
- ADMIN: Administrative fee
- MAINT: Maintenance charge
- DEPOSIT: Security deposit

### Work_Order
Maintenance and repair requests.

**Key Attributes:**
```
work_order_id (UUID, PK)
property_id (UUID, FK)
unit_id (UUID, FK, nullable)
tenant_id (UUID, FK, nullable)
work_order_number (VARCHAR, unique)
category (ENUM: plumbing, electrical, hvac, appliance, structural, cosmetic, other)
priority (ENUM: emergency, urgent, normal, low)
status (ENUM: submitted, assigned, in_progress, completed, cancelled)
issue_description (TEXT)
location_notes (VARCHAR)
requested_by (VARCHAR)
requested_date (TIMESTAMP)
assigned_to_vendor_id (UUID, FK, nullable)
assigned_to_staff_id (UUID, FK, nullable)
scheduled_date (DATE, nullable)
completed_date (TIMESTAMP, nullable)
estimated_cost (DECIMAL)
actual_cost (DECIMAL)
billable_to_tenant (BOOLEAN)
entry_permission (ENUM: anytime, contact_first, specific_time)
entry_notes (TEXT)
resolution_notes (TEXT)
tenant_satisfaction_rating (INT, 1-5)
attachments (JSONB) -- photos, invoices
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

**SLA Targets:**
- Emergency: 24 hours
- Urgent: 72 hours
- Normal: 5-7 business days
- Low: 14 days

### Vendor
Service providers and contractors.

**Key Attributes:**
```
vendor_id (UUID, PK)
vendor_name (VARCHAR)
vendor_type (ENUM: plumber, electrician, hvac, landscaping, general_contractor, other)
contact_person (VARCHAR)
email (VARCHAR)
phone (VARCHAR)
address (TEXT)
license_number (VARCHAR)
insurance_expiration (DATE)
w9_on_file (BOOLEAN)
payment_terms (VARCHAR)
preferred_payment_method (ENUM: check, ach, credit_card)
average_rating (DECIMAL)
service_areas (JSONB) -- which properties they service
notes (TEXT)
active (BOOLEAN)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### Owner
Property owner(s) and investors.

**Key Attributes:**
```
owner_id (UUID, PK)
owner_type (ENUM: individual, llc, corporation, partnership, reit)
name (VARCHAR)
tax_id (VARCHAR) -- EIN or SSN
email (VARCHAR)
phone (VARCHAR)
mailing_address (TEXT)
ownership_percentage (DECIMAL)
distribution_percentage (DECIMAL)
management_fee_percentage (DECIMAL)
portal_access (BOOLEAN)
receive_financial_reports (BOOLEAN)
report_frequency (ENUM: monthly, quarterly, annual)
bank_account_for_distributions (VARCHAR, encrypted)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

## Relationships Diagram

```
Portfolio (1) ──────┐
                    │
Property (N) ───────┼───── (N) Owner
    │               │
    ├─── (N) Unit  │
    │       │       │
    │       │       │
    │    Lease (N) ─┤
    │       │       │
    │       │       │
    └──── (N) ──────┴───── (N) Tenant
          │
          │
      Ledger (N)

Property (1) ────── (N) Work_Order ────── (1) Vendor
    │
    └────── (N) Building ────── (N) Unit
```

## Data Integrity Rules

### Constraints
1. **Unique unit numbers** within a property
2. **No overlapping leases** for the same unit
3. **Lease dates** must be logically consistent
4. **Security deposits** must match lease amount
5. **Tenant ledger** must always balance

### Cascading Deletes
- Deleting a property: CASCADE to units, leases (use soft delete instead)
- Deleting a lease: CASCADE to lease_tenants, ledger entries
- Deleting a tenant: SET NULL on leases (preserve history)

### Audit Requirements
- Track all changes to rent amounts
- Maintain complete payment history
- Log all lease modifications
- Record security deposit transactions

## Indexes for Performance

```sql
-- Property indexes
CREATE INDEX idx_property_status ON properties(status);
CREATE INDEX idx_property_type ON properties(property_type);
CREATE INDEX idx_property_location ON properties USING GIST(lat_lng_point);

-- Unit indexes
CREATE INDEX idx_unit_property ON units(property_id);
CREATE INDEX idx_unit_status ON units(unit_status, lease_status);
CREATE INDEX idx_unit_availability ON units(availability_date)
  WHERE unit_status = 'vacant';

-- Lease indexes
CREATE INDEX idx_lease_unit ON leases(unit_id);
CREATE INDEX idx_lease_dates ON leases(start_date, end_date);
CREATE INDEX idx_lease_status ON leases(lease_status);
CREATE INDEX idx_lease_expiring ON leases(end_date)
  WHERE lease_status = 'active';

-- Ledger indexes
CREATE INDEX idx_ledger_lease ON ledger(lease_id);
CREATE INDEX idx_ledger_date ON ledger(transaction_date DESC);
CREATE INDEX idx_ledger_type ON ledger(transaction_type, charge_code);

-- Work order indexes
CREATE INDEX idx_wo_property ON work_orders(property_id);
CREATE INDEX idx_wo_status ON work_orders(status, priority);
CREATE INDEX idx_wo_assigned ON work_orders(assigned_to_vendor_id);
```

## Common Calculations

### Occupancy Rate
```sql
SELECT
  property_id,
  COUNT(*) FILTER (WHERE unit_status = 'occupied') * 100.0 / COUNT(*) AS occupancy_rate
FROM units
GROUP BY property_id;
```

### Delinquency Amount
```sql
SELECT
  lease_id,
  tenant_id,
  SUM(CASE WHEN transaction_type = 'charge' THEN amount ELSE -amount END) AS balance
FROM ledger
GROUP BY lease_id, tenant_id
HAVING SUM(CASE WHEN transaction_type = 'charge' THEN amount ELSE -amount END) > 0;
```

### Average Rent by Unit Type
```sql
SELECT
  unit_type,
  AVG(current_rent) AS avg_rent,
  COUNT(*) AS unit_count
FROM units
WHERE unit_status = 'occupied'
GROUP BY unit_type
ORDER BY avg_rent DESC;
```

This data model forms the foundation of all property management operations and integrations.
