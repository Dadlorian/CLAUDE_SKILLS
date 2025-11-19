# PropTech Naming Conventions

**Version:** 2.0
**Last Updated:** 2025-01-15
**Status:** Active Standard
**References:** Google Style Guide, Airbnb JavaScript Style Guide, Stripe API Design Patterns

## Table of Contents

1. [Overview](#overview)
2. [Database Naming Conventions](#database-naming-conventions)
3. [API Naming Conventions](#api-naming-conventions)
4. [Code Naming Conventions](#code-naming-conventions)
5. [UI Naming Conventions](#ui-naming-conventions)
6. [File Naming Conventions](#file-naming-conventions)
7. [Industry-Specific Terminology](#industry-specific-terminology)
8. [Compliance and Legal Considerations](#compliance-and-legal-considerations)

## Overview

This document establishes comprehensive naming conventions for PropTech applications, drawing from industry leaders like Yardi, RealPage, Zillow, and Redfin, combined with best practices from Google, Airbnb, and Stripe.

### Core Principles

1. **Clarity over Brevity**: `monthly_rent_amount` is better than `mnt_rnt`
2. **Consistency**: Use the same term across all layers (database, API, UI, code)
3. **Domain Alignment**: Follow real estate industry terminology (MRI, Yardi, RESO standards)
4. **Future-Proofing**: Names should accommodate business growth and internationalization

### Terminology Standards

- **Property** vs **Unit**: Property is the building/complex, Unit is the rentable space
- **Tenant** vs **Resident**: Use Tenant for legal/billing, Resident for marketing/communication
- **Lease** vs **Agreement**: Lease for residential, Agreement for commercial flexibility
- **Owner** vs **Landlord**: Owner for property ownership, Landlord for legal entity

## Database Naming Conventions

### Table Naming

**Standard:** `snake_case`, plural nouns, prefixed by domain

```sql
-- Property Management Domain
properties                  -- Master property (building/complex)
property_units              -- Individual rentable units
property_amenities          -- Swimming pool, gym, parking
property_documents          -- Deeds, insurance, permits
property_images             -- Marketing photos, floorplans
property_valuations         -- AVM results, appraisals

-- Tenant/Lease Domain
tenants                     -- Tenant master records
tenant_applications         -- Rental applications
tenant_screenings           -- Background/credit checks
tenant_documents            -- ID, employment verification
leases                      -- Lease agreements
lease_terms                 -- Rent, deposits, dates
lease_amendments            -- Lease modifications
lease_renewals              -- Renewal tracking
lease_violations            -- Rule violations, notices

-- Financial Domain
rent_charges                -- Recurring rent charges
one_time_charges            -- Pet fees, parking fees
late_fees                   -- Automated late fee calculations
payments                    -- Payment transactions
payment_methods             -- ACH, credit card details (PCI-compliant)
security_deposits           -- Deposit tracking and interest
refunds                     -- Security deposit refunds
gl_accounts                 -- General ledger mapping
financial_periods           -- Accounting period management

-- Maintenance Domain
work_orders                 -- Maintenance requests
work_order_tasks            -- Sub-tasks within work orders
maintenance_schedules       -- Preventive maintenance
vendors                     -- Service providers
vendor_invoices             -- Vendor billing
inspections                 -- Unit inspections
inspection_items            -- Individual inspection points

-- Owner/Investor Domain
owners                      -- Property owners
owner_entities              -- LLCs, partnerships, trusts
ownership_shares            -- Percentage ownership
owner_distributions         -- Profit distributions
investor_reports            -- Financial reporting

-- Smart Building/IoT Domain
iot_devices                 -- Sensors, controllers
device_readings             -- Time-series sensor data
device_commands             -- Control commands sent to devices
energy_consumption          -- Utility usage tracking
access_events               -- Door lock activity
access_credentials          -- Digital keys, access codes
```

### Column Naming

**Standard:** `snake_case`, descriptive, typed suffixes where helpful

```sql
-- ID Columns (always BIGINT/UUID)
id                          -- Primary key (prefer UUID for multi-region)
property_id                 -- Foreign key reference
external_property_id        -- Third-party system reference (Yardi, MRI)
mls_listing_id              -- MLS number

-- Monetary Columns (always DECIMAL(19,4), stored in cents for precision)
monthly_rent_amount         -- Base rent
market_rent_amount          -- Current market rate
security_deposit_amount     -- Deposit amount
late_fee_amount             -- Late fee calculation
total_amount_cents          -- Total in cents (Stripe pattern)

-- Percentage Columns (DECIMAL(5,2) for 0.00-100.00)
late_fee_percentage         -- e.g., 5.00 for 5%
ownership_percentage        -- Owner's share
occupancy_rate_percentage   -- Portfolio occupancy
commission_rate_percentage  -- Agent commission

-- Date/Time Columns
created_at                  -- Record creation (UTC timestamp)
updated_at                  -- Last modification (UTC timestamp)
deleted_at                  -- Soft delete (UTC timestamp, nullable)
lease_start_date            -- Lease commencement (DATE)
lease_end_date              -- Lease expiration (DATE)
rent_due_date               -- Monthly due date (DATE)
move_in_date                -- Actual move-in (DATE)
move_out_date               -- Actual move-out (DATE)
notice_given_at             -- Notice to vacate timestamp
inspected_at                -- Inspection timestamp

-- Boolean Columns (use is_, has_, can_ prefixes)
is_active                   -- Active status
is_deleted                  -- Soft delete flag
is_occupied                 -- Unit occupancy status
has_washer_dryer            -- Appliance flag
has_parking                 -- Parking availability
can_have_pets               -- Pet policy
requires_renters_insurance  -- Insurance requirement
is_rent_controlled          -- Rent control status
is_affordable_housing       -- Affordable housing program

-- Status Columns (use ENUM or VARCHAR with CHECK constraint)
application_status          -- draft, submitted, under_review, approved, denied
lease_status                -- draft, active, expired, terminated, renewed
work_order_status           -- open, assigned, in_progress, completed, closed
payment_status              -- pending, processing, completed, failed, refunded

-- Address Columns (follow USPS standards)
street_address_line_1       -- Primary address
street_address_line_2       -- Apt/Unit (optional)
city                        -- City name
state_province_code         -- Two-letter state code (e.g., CA, NY)
postal_code                 -- ZIP code (5 or 9 digit)
country_code                -- ISO 3166-1 alpha-2 (US, CA, MX)
latitude                    -- DECIMAL(10,8)
longitude                   -- DECIMAL(11,8)
geohash                     -- Geospatial indexing

-- Contact Columns
primary_email               -- Main email
secondary_email             -- Alternate email
mobile_phone                -- Mobile number (E.164 format: +14155551234)
home_phone                  -- Home number
work_phone                  -- Work number
emergency_contact_name      -- Emergency contact
emergency_contact_phone     -- Emergency phone

-- Metadata Columns (JSONB for PostgreSQL, JSON for MySQL)
metadata                    -- Flexible key-value storage
custom_fields               -- Tenant-specific customizations
integrations_data           -- Third-party integration data
audit_trail                 -- Change history tracking
```

### Indexes and Constraints

```sql
-- Index Naming: idx_{table}_{columns}_{type}
idx_properties_city_state           -- Multi-column index
idx_leases_tenant_id                -- Foreign key index
idx_leases_start_date_end_date      -- Date range index
idx_properties_location_gist        -- Geospatial index (PostGIS)
idx_device_readings_timestamp_btree -- Time-series index

-- Unique Constraint: uk_{table}_{columns}
uk_properties_external_id           -- Unique external ID
uk_tenants_email_active             -- Unique email for active tenants
uk_leases_unit_date_range           -- Prevent overlapping leases

-- Foreign Key: fk_{table}_{referenced_table}_{column}
fk_leases_properties_property_id
fk_leases_tenants_tenant_id
fk_payments_leases_lease_id

-- Check Constraint: chk_{table}_{constraint_description}
chk_leases_end_after_start          -- CHECK (lease_end_date > lease_start_date)
chk_rent_amount_positive            -- CHECK (monthly_rent_amount > 0)
chk_occupancy_valid_range           -- CHECK (occupancy_rate BETWEEN 0 AND 100)
```

### View Naming

```sql
-- Views: v_{descriptive_name}
v_active_leases                     -- Current active leases
v_vacant_units                      -- Available units
v_delinquent_tenants                -- Tenants with overdue rent
v_property_portfolio_summary        -- Aggregated portfolio metrics
v_rent_roll                         -- Rent roll report
v_lease_expiration_report           -- Upcoming expirations
v_maintenance_backlog               -- Open work orders

-- Materialized Views: mv_{descriptive_name}
mv_monthly_revenue_by_property      -- Pre-aggregated revenue
mv_occupancy_trends                 -- Historical occupancy
mv_energy_consumption_daily         -- Daily energy rollup
```

### Stored Procedures and Functions

```sql
-- Functions: fn_{action}_{entity}
fn_calculate_late_fee(lease_id, days_late)
fn_get_market_rent(unit_id, effective_date)
fn_check_lease_overlap(unit_id, start_date, end_date)
fn_generate_rent_roll(property_id, as_of_date)

-- Stored Procedures: sp_{action}_{entity}
sp_process_monthly_rent_charges()
sp_generate_late_fees()
sp_post_owner_distributions()
sp_sync_mls_listings()
sp_archive_expired_leases()
```

## API Naming Conventions

### RESTful Endpoint Structure

**Standard:** Follow REST principles, use kebab-case for URLs, plural resource names

```
Base URL: https://api.proptech.com/v1

-- Property Management
GET    /properties                          # List properties (paginated)
GET    /properties/{id}                     # Get property details
POST   /properties                          # Create property
PATCH  /properties/{id}                     # Update property
DELETE /properties/{id}                     # Soft delete property

GET    /properties/{id}/units               # List units in property
GET    /properties/{id}/financial-summary   # Financial overview
GET    /properties/{id}/occupancy-history   # Occupancy trends

-- Units
GET    /units                               # List all units (with filters)
GET    /units/{id}                          # Get unit details
GET    /units/{id}/lease-history            # Historical leases
GET    /units/{id}/maintenance-history      # Work order history
POST   /units/{id}/schedule-showing         # Schedule unit showing

-- Tenants
GET    /tenants                             # List tenants
GET    /tenants/{id}                        # Get tenant details
POST   /tenants                             # Create tenant
PATCH  /tenants/{id}                        # Update tenant
GET    /tenants/{id}/payment-history        # Payment history
GET    /tenants/{id}/lease-documents        # Lease documents
POST   /tenants/{id}/send-notice            # Send notice to tenant

-- Leases
GET    /leases                              # List leases (filters: status, property, tenant)
GET    /leases/{id}                         # Get lease details
POST   /leases                              # Create lease
PATCH  /leases/{id}                         # Update lease
POST   /leases/{id}/activate                # Activate lease (state transition)
POST   /leases/{id}/terminate               # Terminate lease early
POST   /leases/{id}/renew                   # Generate renewal lease
POST   /leases/{id}/amendments              # Add amendment
GET    /leases/{id}/payment-schedule        # Payment schedule

-- Payments
GET    /payments                            # List payments
GET    /payments/{id}                       # Get payment details
POST   /payments                            # Create payment
POST   /payments/{id}/refund                # Process refund
POST   /payments/bulk-process               # Batch payment processing

-- Work Orders
GET    /work-orders                         # List work orders
POST   /work-orders                         # Create work order
PATCH  /work-orders/{id}                    # Update work order
POST   /work-orders/{id}/assign             # Assign to vendor
POST   /work-orders/{id}/complete           # Mark complete
POST   /work-orders/{id}/attachments        # Upload photos

-- Smart Building/IoT
GET    /devices                             # List devices
GET    /devices/{id}/readings               # Get sensor readings (time-series)
POST   /devices/{id}/commands               # Send control command
GET    /properties/{id}/energy-analytics    # Energy consumption analytics
POST   /access-credentials                  # Grant access to unit

-- MLS Integration
GET    /mls/listings                        # Search MLS listings
GET    /mls/listings/{id}                   # Get listing details
POST   /mls/listings/sync                   # Sync MLS data
GET    /mls/listings/{id}/media             # Get listing photos/videos

-- Reporting
GET    /reports/rent-roll                   # Rent roll report
GET    /reports/occupancy-summary           # Occupancy report
GET    /reports/delinquency                 # Delinquency report
GET    /reports/financial-statement         # P&L, balance sheet
POST   /reports/generate-custom             # Generate custom report
```

### Query Parameter Naming

```
# Pagination (follow Stripe pattern)
?limit=50                                   # Page size (default: 20, max: 100)
?starting_after=obj_123                     # Cursor-based pagination
?ending_before=obj_456                      # Reverse pagination

# Filtering
?status=active                              # Enum filter
?status[in]=active,pending                  # Multiple values
?monthly_rent_amount[gte]=2000              # Range filter (gte, lte, gt, lt)
?monthly_rent_amount[between]=1500,3000     # Between range
?city=San Francisco                         # Exact match
?city[like]=San%                            # Pattern match
?has_parking=true                           # Boolean filter
?lease_start_date[gte]=2025-01-01           # Date filter

# Sorting
?sort=monthly_rent_amount                   # Ascending (default)
?sort=-monthly_rent_amount                  # Descending (- prefix)
?sort=city,-monthly_rent_amount             # Multiple fields

# Field Selection (sparse fieldsets)
?fields=id,street_address,monthly_rent      # Return specific fields only
?include=property,tenant                    # Include related resources

# Search
?search=luxury apartment downtown           # Full-text search
?search_fields=street_address,city,state    # Specify search fields

# Geospatial
?near=-122.419,37.775&radius=5mi            # Within radius
?bbox=-122.5,37.7,-122.3,37.8               # Bounding box
```

### Request/Response Field Naming

**Standard:** `snake_case` for JSON fields, match database naming

```json
{
  "id": "prop_2zXj9mK8vN",
  "object": "property",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "property_name": "Sunset Towers",
  "property_type": "multifamily",
  "year_built": 2015,
  "total_units": 120,
  "occupancy_rate_percentage": 95.5,
  "street_address_line_1": "123 Main Street",
  "street_address_line_2": null,
  "city": "San Francisco",
  "state_province_code": "CA",
  "postal_code": "94102",
  "country_code": "US",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "amenities": [
    {
      "id": "amenity_abc123",
      "amenity_type": "swimming_pool",
      "is_available": true,
      "additional_fee_amount": 0
    }
  ],
  "financial_summary": {
    "total_monthly_rent": 360000,
    "total_annual_revenue": 4320000,
    "average_rent_per_unit": 3000,
    "collection_rate_percentage": 98.5
  },
  "metadata": {
    "yardi_property_code": "SUNST001",
    "portfolio_segment": "premium"
  }
}
```

### Error Response Naming

**Standard:** Follow RFC 7807 Problem Details, use snake_case

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_lease_dates",
    "message": "Lease end date must be after start date",
    "param": "lease_end_date",
    "request_id": "req_abc123xyz",
    "details": [
      {
        "field": "lease_end_date",
        "message": "Must be after lease_start_date (2025-01-01)",
        "code": "date_range_invalid"
      }
    ]
  }
}
```

## Code Naming Conventions

### JavaScript/TypeScript

**Standard:** camelCase for variables/functions, PascalCase for classes, SCREAMING_SNAKE_CASE for constants

```typescript
// Constants
const MAX_LEASE_TERM_MONTHS = 24;
const DEFAULT_LATE_FEE_PERCENTAGE = 5.0;
const RENT_DUE_DAY_OF_MONTH = 1;
const PET_DEPOSIT_MULTIPLIER = 2.0;

// Enums (PascalCase)
enum LeaseStatus {
  Draft = 'draft',
  Active = 'active',
  Expired = 'expired',
  Terminated = 'terminated',
  Renewed = 'renewed'
}

enum PropertyType {
  Multifamily = 'multifamily',
  SingleFamily = 'single_family',
  Commercial = 'commercial',
  MixedUse = 'mixed_use',
  StudentHousing = 'student_housing'
}

// Interfaces (PascalCase, use 'I' prefix only if needed for disambiguation)
interface Property {
  id: string;
  propertyName: string;
  propertyType: PropertyType;
  totalUnits: number;
  occupancyRatePercentage: number;
  streetAddressLine1: string;
  city: string;
  stateProvinceCode: string;
  postalCode: string;
  latitude: number;
  longitude: number;
}

interface Lease {
  id: string;
  propertyId: string;
  unitId: string;
  tenantId: string;
  leaseStatus: LeaseStatus;
  leaseStartDate: Date;
  leaseEndDate: Date;
  monthlyRentAmount: number;
  securityDepositAmount: number;
  isRentControlled: boolean;
}

// Classes (PascalCase)
class PropertyManagementService {
  private readonly propertyRepository: PropertyRepository;
  private readonly cacheService: CacheService;

  constructor(propertyRepository: PropertyRepository, cacheService: CacheService) {
    this.propertyRepository = propertyRepository;
    this.cacheService = cacheService;
  }

  // Methods (camelCase, verb-noun pattern)
  async findPropertiesByCity(city: string): Promise<Property[]> {
    const cacheKey = `properties:city:${city}`;
    const cached = await this.cacheService.get(cacheKey);
    if (cached) return cached;

    const properties = await this.propertyRepository.findByCity(city);
    await this.cacheService.set(cacheKey, properties, 300); // 5 min TTL
    return properties;
  }

  async calculateMonthlyRevenue(propertyId: string, month: Date): Promise<number> {
    const leases = await this.getActiveLeases(propertyId, month);
    return leases.reduce((sum, lease) => sum + lease.monthlyRentAmount, 0);
  }

  async processLateFees(asOfDate: Date): Promise<void> {
    const delinquentLeases = await this.findDelinquentLeases(asOfDate);

    for (const lease of delinquentLeases) {
      const lateFee = this.calculateLateFee(lease, asOfDate);
      await this.createCharge(lease.id, lateFee);
    }
  }

  private calculateLateFee(lease: Lease, asOfDate: Date): number {
    const daysLate = this.calculateDaysLate(lease, asOfDate);
    return lease.monthlyRentAmount * (DEFAULT_LATE_FEE_PERCENTAGE / 100);
  }

  private calculateDaysLate(lease: Lease, asOfDate: Date): number {
    // Implementation
    return 0;
  }

  private async getActiveLeases(propertyId: string, month: Date): Promise<Lease[]> {
    return this.propertyRepository.findActiveLeases(propertyId, month);
  }

  private async findDelinquentLeases(asOfDate: Date): Promise<Lease[]> {
    // Implementation
    return [];
  }

  private async createCharge(leaseId: string, amount: number): Promise<void> {
    // Implementation
  }
}

// Variables (camelCase, descriptive)
const activeLeaseCount = 150;
const averageRentPerSquareFoot = 3.25;
const totalMonthlyRevenue = 480000;
const occupancyRateThreshold = 95.0;

// Boolean variables (use is/has/can prefixes)
const isUnitOccupied = true;
const hasParking = false;
const canHavePets = true;
const requiresRentersInsurance = true;

// Arrays (plural nouns)
const properties: Property[] = [];
const activeLeases: Lease[] = [];
const vacantUnits: Unit[] = [];

// Functions (camelCase, verb-first)
function calculateProrationAmount(
  monthlyRent: number,
  moveInDate: Date,
  daysInMonth: number
): number {
  const daysOccupied = daysInMonth - moveInDate.getDate() + 1;
  return (monthlyRent / daysInMonth) * daysOccupied;
}

function isLeaseExpiringSoon(lease: Lease, daysThreshold: number = 90): boolean {
  const daysUntilExpiration = differenceInDays(lease.leaseEndDate, new Date());
  return daysUntilExpiration <= daysThreshold && daysUntilExpiration > 0;
}

async function sendLeaseRenewalNotice(lease: Lease): Promise<void> {
  const tenant = await getTenantById(lease.tenantId);
  const emailTemplate = 'lease_renewal_reminder';
  await sendEmail(tenant.primaryEmail, emailTemplate, { lease });
}
```

### Python

**Standard:** snake_case for functions/variables, PascalCase for classes, SCREAMING_SNAKE_CASE for constants

```python
# Constants
MAX_LEASE_TERM_MONTHS = 24
DEFAULT_LATE_FEE_PERCENTAGE = 5.0
RENT_DUE_DAY_OF_MONTH = 1
PET_DEPOSIT_MULTIPLIER = 2.0

# Enums
from enum import Enum

class LeaseStatus(Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    EXPIRED = 'expired'
    TERMINATED = 'terminated'
    RENEWED = 'renewed'

class PropertyType(Enum):
    MULTIFAMILY = 'multifamily'
    SINGLE_FAMILY = 'single_family'
    COMMERCIAL = 'commercial'
    MIXED_USE = 'mixed_use'
    STUDENT_HOUSING = 'student_housing'

# Data Classes
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class Property:
    id: str
    property_name: str
    property_type: PropertyType
    total_units: int
    occupancy_rate_percentage: Decimal
    street_address_line_1: str
    city: str
    state_province_code: str
    postal_code: str
    latitude: Decimal
    longitude: Decimal

@dataclass
class Lease:
    id: str
    property_id: str
    unit_id: str
    tenant_id: str
    lease_status: LeaseStatus
    lease_start_date: date
    lease_end_date: date
    monthly_rent_amount: Decimal
    security_deposit_amount: Decimal
    is_rent_controlled: bool

# Classes
class PropertyManagementService:
    def __init__(self, property_repository, cache_service):
        self._property_repository = property_repository
        self._cache_service = cache_service

    async def find_properties_by_city(self, city: str) -> list[Property]:
        cache_key = f"properties:city:{city}"
        cached = await self._cache_service.get(cache_key)
        if cached:
            return cached

        properties = await self._property_repository.find_by_city(city)
        await self._cache_service.set(cache_key, properties, ttl=300)
        return properties

    async def calculate_monthly_revenue(self, property_id: str, month: date) -> Decimal:
        leases = await self._get_active_leases(property_id, month)
        return sum(lease.monthly_rent_amount for lease in leases)

    async def process_late_fees(self, as_of_date: date) -> None:
        delinquent_leases = await self._find_delinquent_leases(as_of_date)

        for lease in delinquent_leases:
            late_fee = self._calculate_late_fee(lease, as_of_date)
            await self._create_charge(lease.id, late_fee)

    def _calculate_late_fee(self, lease: Lease, as_of_date: date) -> Decimal:
        days_late = self._calculate_days_late(lease, as_of_date)
        return lease.monthly_rent_amount * (Decimal(DEFAULT_LATE_FEE_PERCENTAGE) / 100)
```

## UI Naming Conventions

### Component Naming

```typescript
// React Components (PascalCase)
PropertyListView
PropertyDetailView
UnitCard
LeaseForm
TenantApplicationWizard
PaymentHistoryTable
MaintenanceRequestModal
LeaseRenewalDialog
OccupancyDashboard
RentRollReport

// Component Props Interfaces
interface PropertyListViewProps {
  properties: Property[];
  onPropertySelect: (propertyId: string) => void;
  isLoading: boolean;
  emptyStateMessage?: string;
}

// Event Handlers (handle prefix)
const handlePropertySelect = (propertyId: string) => { };
const handleLeaseSubmit = (leaseData: LeaseFormData) => { };
const handlePaymentProcess = async () => { };
```

### Form Field IDs and Names

```html
<!-- Property Form -->
<input id="property-name" name="property_name" />
<input id="property-type" name="property_type" />
<input id="total-units" name="total_units" />
<input id="year-built" name="year_built" />

<!-- Lease Form -->
<input id="lease-start-date" name="lease_start_date" type="date" />
<input id="lease-end-date" name="lease_end_date" type="date" />
<input id="monthly-rent-amount" name="monthly_rent_amount" type="number" />
<input id="security-deposit-amount" name="security_deposit_amount" type="number" />

<!-- Tenant Application -->
<input id="tenant-first-name" name="tenant_first_name" />
<input id="tenant-last-name" name="tenant_last_name" />
<input id="tenant-email" name="tenant_email" type="email" />
<input id="tenant-phone" name="tenant_phone" type="tel" />
```

### Button Labels and Actions

```
Primary Actions:
- Save Property
- Create Lease
- Submit Application
- Process Payment
- Generate Report

Secondary Actions:
- Cancel
- Go Back
- Reset Form
- Clear Filters

Destructive Actions:
- Terminate Lease
- Delete Property
- Remove Tenant
- Cancel Payment

State Transitions:
- Activate Lease
- Mark Complete
- Approve Application
- Reject Application
```

## File Naming Conventions

### Document Types

```
# Lease Documents
lease_{lease_id}_{lease_start_date}.pdf
lease_amendment_{lease_id}_{amendment_number}_{date}.pdf
lease_renewal_{lease_id}_{renewal_date}.pdf
move_in_checklist_{lease_id}_{unit_id}.pdf
move_out_checklist_{lease_id}_{unit_id}.pdf

# Property Documents
deed_{property_id}_{recorded_date}.pdf
insurance_policy_{property_id}_{policy_number}_{effective_date}.pdf
inspection_report_{property_id}_{inspection_date}.pdf
certificate_of_occupancy_{property_id}_{issue_date}.pdf
property_survey_{property_id}_{survey_date}.pdf

# Financial Documents
rent_roll_{property_id}_{year}_{month}.xlsx
income_statement_{property_id}_{year}_{quarter}.pdf
balance_sheet_{property_id}_{year}_{month}.pdf
owner_distribution_{owner_id}_{year}_{month}.pdf
1099_form_{vendor_id}_{tax_year}.pdf

# Tenant Documents
tenant_application_{tenant_id}_{application_date}.pdf
credit_report_{tenant_id}_{report_date}.pdf
background_check_{tenant_id}_{check_date}.pdf
employment_verification_{tenant_id}_{employer}_{date}.pdf
rental_history_{tenant_id}_{previous_landlord}_{date}.pdf

# Work Order Documents
work_order_{work_order_id}_{created_date}.pdf
work_order_photo_{work_order_id}_{photo_number}_{timestamp}.jpg
vendor_invoice_{vendor_id}_{invoice_number}_{date}.pdf
```

### Image Naming

```
# Property Marketing Photos
{property_id}_exterior_front_001.jpg
{property_id}_exterior_aerial_001.jpg
{property_id}_lobby_001.jpg
{property_id}_amenity_pool_001.jpg
{property_id}_amenity_gym_001.jpg

# Unit Photos
{unit_id}_floorplan.pdf
{unit_id}_living_room_001.jpg
{unit_id}_kitchen_001.jpg
{unit_id}_bedroom_001.jpg
{unit_id}_bathroom_001.jpg

# Inspection Photos
inspection_{inspection_id}_damage_wall_001.jpg
inspection_{inspection_id}_damage_floor_002.jpg

# Work Order Photos
workorder_{work_order_id}_before_001.jpg
workorder_{work_order_id}_after_001.jpg
```

### Code Files

```
# React Components
PropertyListView.tsx
PropertyDetailView.tsx
UnitCard.tsx
LeaseForm.tsx
TenantApplicationWizard.tsx

# Services
PropertyManagementService.ts
LeaseService.ts
PaymentProcessingService.ts
MaintenanceService.ts

# Repositories
PropertyRepository.ts
LeaseRepository.ts
TenantRepository.ts

# Utilities
dateHelpers.ts
currencyFormatters.ts
addressValidation.ts
rentCalculations.ts

# Tests
PropertyManagementService.test.ts
LeaseService.test.ts
PropertyRepository.test.ts
```

## Industry-Specific Terminology

### RESO Standard Data Dictionary

Follow the Real Estate Standards Organization (RESO) naming where applicable:

```
StandardStatus (Active, Pending, Closed)
ListPrice (not asking_price or price)
ListingKey (unique MLS identifier)
OriginalListPrice
ClosePrice
DaysOnMarket
PropertyType (Residential, Commercial, Land)
PropertySubType (SingleFamily, Condominium, Townhouse)
BathroomsFull, BathroomsHalf
BedroomsTotal
LivingArea (in square feet)
LotSizeSquareFeet
YearBuilt
Appliances (array of appliance types)
```

### Yardi Voyager Alignment

For systems integrating with Yardi:

```
PropertyCode (alphanumeric property identifier)
UnitCode (unit number within property)
ChargeCode (rent, fees, utilities)
GLAccountNumber (general ledger account)
TenantCode (tenant identifier)
VendorCode (vendor identifier)
```

## Compliance and Legal Considerations

### Fair Housing Compliance

**Never use discriminatory field names or categorizations:**

❌ **Prohibited:**
- `race`, `ethnicity`, `national_origin`
- `religion`, `religious_affiliation`
- `family_status`, `has_children`, `number_of_children`
- `disability_status`, `has_disability`
- `age` (except for senior housing verification)
- `sexual_orientation`, `gender_identity`

✅ **Permitted:**
- `number_of_occupants` (for occupancy standards)
- `is_senior_housing_qualified` (for 55+ communities with proper verification)
- `service_animal_present` (with medical documentation)

### PCI DSS Compliance

**Never store sensitive payment data in plain text:**

❌ **Prohibited Field Names:**
- `credit_card_number`
- `cvv`, `security_code`
- `full_card_details`

✅ **Use Tokenization:**
- `payment_method_token` (Stripe: `pm_abc123`)
- `customer_token` (Stripe: `cus_abc123`)
- `bank_account_token` (for ACH)
- `last_four_digits` (masked card: `****1234`)
- `card_brand` (`visa`, `mastercard`, `amex`)

### GDPR/CCPA Privacy

```
# Personal Data Fields (must support deletion/export)
tenant_first_name
tenant_last_name
tenant_email
tenant_phone
tenant_ssn_encrypted  # Encrypted, never plain text
tenant_date_of_birth

# Consent Tracking
marketing_consent_given_at
data_processing_consent_given_at
consent_withdrawn_at

# Data Subject Rights
data_deletion_requested_at
data_export_completed_at
```

---

## References and Further Reading

1. **Google JSON Style Guide**: https://google.github.io/styleguide/jsoncstyleguide.xml
2. **Airbnb JavaScript Style Guide**: https://github.com/airbnb/javascript
3. **Stripe API Design**: https://stripe.com/docs/api
4. **RESO Data Dictionary**: https://www.reso.org/data-dictionary/
5. **Yardi Developer Resources**: https://www.yardi.com/products/voyager/
6. **Fair Housing Act**: https://www.hud.gov/program_offices/fair_housing_equal_opp
7. **PCI DSS Standards**: https://www.pcisecuritystandards.org/

## Version History

- **2.0** (2025-01-15): Added IoT/smart building conventions, RESO alignment
- **1.5** (2024-09-01): Enhanced API naming patterns, added payment gateway conventions
- **1.0** (2024-01-01): Initial release

---

*This document is maintained by the PropTech Standards Committee. For questions or updates, contact standards@proptech.com.*
