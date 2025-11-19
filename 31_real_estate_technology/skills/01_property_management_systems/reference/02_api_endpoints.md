# Property Management System API Reference

## Overview
Comprehensive API endpoint reference for property management system operations. Following REST conventions with standard HTTP methods and JSON payloads.

## Base URL
```
Production: https://api.pmsplatform.com/v1
Staging: https://api-staging.pmsplatform.com/v1
Sandbox: https://api-sandbox.pmsplatform.com/v1
```

## Authentication

### OAuth 2.0 Flow
```http
POST /oauth/token
Content-Type: application/json

{
  "grant_type": "client_credentials",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "scope": "properties:read properties:write leases:read leases:write"
}

Response:
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "properties:read properties:write"
}
```

### Using Access Token
```http
GET /properties
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

## Properties

### List Properties
```http
GET /properties
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `status` (string): Filter by status (active, inactive, sold)
- `property_type` (string): Filter by type (multifamily, commercial, mixed_use)
- `city` (string): Filter by city
- `state` (string): Filter by state code
- `sort` (string): Sort field (name, created_at, total_units)
- `order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "data": [
    {
      "id": "prop_1234567890",
      "name": "Sunset Apartments",
      "type": "multifamily",
      "address": {
        "street": "123 Main Street",
        "city": "Austin",
        "state": "TX",
        "postal_code": "78701",
        "country": "US"
      },
      "total_units": 150,
      "occupied_units": 142,
      "occupancy_rate": 94.67,
      "total_square_feet": 120000,
      "year_built": 2015,
      "status": "active",
      "created_at": "2020-01-15T10:30:00Z",
      "updated_at": "2024-11-18T14:22:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 98,
    "items_per_page": 20
  }
}
```

### Get Property Details
```http
GET /properties/{property_id}
```

**Response:**
```json
{
  "id": "prop_1234567890",
  "name": "Sunset Apartments",
  "type": "multifamily",
  "address": {
    "street": "123 Main Street",
    "city": "Austin",
    "state": "TX",
    "postal_code": "78701",
    "country": "US",
    "latitude": 30.2672,
    "longitude": -97.7431
  },
  "details": {
    "total_units": 150,
    "occupied_units": 142,
    "occupancy_rate": 94.67,
    "total_square_feet": 120000,
    "lot_size_acres": 3.5,
    "parking_spaces": 200,
    "year_built": 2015,
    "last_renovation": 2022
  },
  "financial": {
    "acquisition_date": "2020-01-15",
    "acquisition_price": 25000000,
    "current_value": 32000000,
    "monthly_revenue": 180000,
    "monthly_expenses": 72000,
    "noi": 108000
  },
  "amenities": [
    "pool", "fitness_center", "dog_park", "business_center", "package_lockers"
  ],
  "management": {
    "property_manager": "Jane Smith",
    "management_company": "Premier Property Management",
    "phone": "+1-555-123-4567",
    "email": "manager@sunset-apts.com"
  },
  "status": "active",
  "created_at": "2020-01-15T10:30:00Z",
  "updated_at": "2024-11-18T14:22:00Z"
}
```

### Create Property
```http
POST /properties
Content-Type: application/json

{
  "name": "Riverside Towers",
  "type": "multifamily",
  "address": {
    "street": "456 River Road",
    "city": "Portland",
    "state": "OR",
    "postal_code": "97201",
    "country": "US"
  },
  "total_units": 200,
  "total_square_feet": 180000,
  "year_built": 2018,
  "parking_spaces": 250,
  "amenities": ["pool", "rooftop_deck", "bike_storage"]
}

Response: 201 Created
{
  "id": "prop_9876543210",
  "name": "Riverside Towers",
  ...
}
```

### Update Property
```http
PUT /properties/{property_id}
PATCH /properties/{property_id}  # Partial update
```

### Delete Property
```http
DELETE /properties/{property_id}

Response: 204 No Content
```

## Units

### List Units
```http
GET /properties/{property_id}/units
GET /units  # All units across all properties
```

**Query Parameters:**
- `status` (string): Filter by status (occupied, vacant, maintenance)
- `unit_type` (string): Filter by type (studio, 1br, 2br, 3br)
- `available_by` (date): Units available by date
- `min_rent` (number): Minimum rent amount
- `max_rent` (number): Maximum rent amount

**Response:**
```json
{
  "data": [
    {
      "id": "unit_abc123",
      "property_id": "prop_1234567890",
      "unit_number": "A101",
      "unit_type": "2br",
      "floor": 1,
      "square_feet": 950,
      "bedrooms": 2,
      "bathrooms": 2.0,
      "market_rent": 2200,
      "current_rent": 2100,
      "status": "occupied",
      "lease_status": "leased",
      "availability_date": null,
      "current_lease": {
        "id": "lease_xyz789",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "tenant_name": "John Doe"
      },
      "features": ["balcony", "washer_dryer_hookup", "walk_in_closet"],
      "pets_allowed": true,
      "created_at": "2020-01-15T10:30:00Z",
      "updated_at": "2024-11-18T14:22:00Z"
    }
  ],
  "pagination": {...}
}
```

### Get Unit Details
```http
GET /units/{unit_id}
```

### Create Unit
```http
POST /properties/{property_id}/units

{
  "unit_number": "A305",
  "unit_type": "1br",
  "floor": 3,
  "square_feet": 750,
  "bedrooms": 1,
  "bathrooms": 1.0,
  "market_rent": 1800,
  "security_deposit_amount": 1800,
  "features": ["balcony", "dishwasher"],
  "pets_allowed": true
}
```

## Leases

### List Leases
```http
GET /leases
```

**Query Parameters:**
- `property_id` (string): Filter by property
- `unit_id` (string): Filter by unit
- `tenant_id` (string): Filter by tenant
- `status` (string): Filter by status (active, expired, pending)
- `expiring_before` (date): Leases expiring before date
- `expiring_after` (date): Leases expiring after date

**Response:**
```json
{
  "data": [
    {
      "id": "lease_xyz789",
      "lease_number": "L-2024-001234",
      "property_id": "prop_1234567890",
      "unit_id": "unit_abc123",
      "unit_number": "A101",
      "status": "active",
      "type": "fixed",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "move_in_date": "2024-01-01",
      "base_rent": 2100,
      "pet_rent": 50,
      "parking_rent": 100,
      "total_monthly_rent": 2250,
      "security_deposit": 2100,
      "lease_term_months": 12,
      "tenants": [
        {
          "id": "tenant_def456",
          "name": "John Doe",
          "email": "john@example.com",
          "relationship": "primary"
        }
      ],
      "autopay_enabled": true,
      "signed_date": "2023-12-15",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2024-11-18T14:22:00Z"
    }
  ],
  "pagination": {...}
}
```

### Create Lease
```http
POST /leases

{
  "unit_id": "unit_abc123",
  "tenant_ids": ["tenant_def456"],
  "type": "fixed",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "move_in_date": "2025-01-01",
  "base_rent": 2200,
  "pet_rent": 50,
  "security_deposit": 2200,
  "lease_term_months": 12,
  "rent_due_day": 1,
  "late_fee_amount": 75,
  "late_fee_grace_days": 3
}

Response: 201 Created
```

### Renew Lease
```http
POST /leases/{lease_id}/renew

{
  "new_end_date": "2026-12-31",
  "new_rent": 2300,
  "lease_term_months": 12
}

Response: 200 OK
{
  "id": "lease_newid123",
  "previous_lease_id": "lease_xyz789",
  "renewal_count": 1,
  ...
}
```

### Terminate Lease
```http
POST /leases/{lease_id}/terminate

{
  "termination_date": "2024-11-30",
  "termination_reason": "tenant_request",
  "notice_date": "2024-10-15",
  "early_termination": false
}
```

## Tenants

### List Tenants
```http
GET /tenants
```

**Query Parameters:**
- `status` (string): Filter by status (current, former, applicant)
- `property_id` (string): Filter by property
- `search` (string): Search by name or email

### Get Tenant Details
```http
GET /tenants/{tenant_id}
```

**Response:**
```json
{
  "id": "tenant_def456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_primary": "+1-555-987-6543",
  "date_of_birth": "1990-05-15",
  "status": "current",
  "current_lease": {
    "id": "lease_xyz789",
    "unit_number": "A101",
    "property_name": "Sunset Apartments",
    "monthly_rent": 2250,
    "lease_end_date": "2024-12-31"
  },
  "balance": 0,
  "portal_access_enabled": true,
  "autopay_enabled": true,
  "emergency_contact": {
    "name": "Jane Doe",
    "phone": "+1-555-111-2222",
    "relationship": "spouse"
  },
  "move_in_date": "2024-01-01",
  "created_at": "2023-12-01T09:00:00Z",
  "updated_at": "2024-11-18T14:22:00Z"
}
```

### Create Tenant
```http
POST /tenants

{
  "first_name": "Sarah",
  "last_name": "Johnson",
  "email": "sarah@example.com",
  "phone_primary": "+1-555-222-3333",
  "date_of_birth": "1992-08-22",
  "emergency_contact_name": "Mike Johnson",
  "emergency_contact_phone": "+1-555-444-5555"
}
```

## Ledger & Payments

### Get Tenant Ledger
```http
GET /tenants/{tenant_id}/ledger
GET /leases/{lease_id}/ledger
```

**Query Parameters:**
- `start_date` (date): Filter transactions from date
- `end_date` (date): Filter transactions to date
- `transaction_type` (string): Filter by type (charge, payment, credit)

**Response:**
```json
{
  "tenant_id": "tenant_def456",
  "current_balance": -150.00,
  "transactions": [
    {
      "id": "txn_001",
      "date": "2024-11-01",
      "type": "charge",
      "charge_code": "RENT",
      "description": "November Rent",
      "amount": 2250.00,
      "balance": 2250.00
    },
    {
      "id": "txn_002",
      "date": "2024-11-03",
      "type": "payment",
      "payment_method": "ach",
      "description": "Payment - ACH",
      "amount": -2100.00,
      "balance": 150.00,
      "reference_number": "ACH123456"
    },
    {
      "id": "txn_003",
      "date": "2024-11-05",
      "type": "charge",
      "charge_code": "LATE",
      "description": "Late Fee",
      "amount": 75.00,
      "balance": 225.00
    }
  ]
}
```

### Record Payment
```http
POST /payments

{
  "lease_id": "lease_xyz789",
  "tenant_id": "tenant_def456",
  "amount": 2250.00,
  "payment_method": "ach",
  "payment_date": "2024-11-01",
  "reference_number": "ACH123456",
  "notes": "November rent payment"
}

Response: 201 Created
```

### Post Charge
```http
POST /charges

{
  "lease_id": "lease_xyz789",
  "charge_code": "LATE",
  "amount": 75.00,
  "charge_date": "2024-11-05",
  "description": "Late fee - Nov rent paid after grace period"
}
```

## Work Orders

### List Work Orders
```http
GET /work-orders
```

**Query Parameters:**
- `property_id` (string): Filter by property
- `unit_id` (string): Filter by unit
- `status` (string): Filter by status (submitted, in_progress, completed)
- `priority` (string): Filter by priority (emergency, urgent, normal)
- `assigned_to` (string): Filter by vendor or staff ID

**Response:**
```json
{
  "data": [
    {
      "id": "wo_123456",
      "work_order_number": "WO-2024-5678",
      "property_id": "prop_1234567890",
      "unit_id": "unit_abc123",
      "unit_number": "A101",
      "category": "plumbing",
      "priority": "urgent",
      "status": "in_progress",
      "description": "Leaking kitchen faucet",
      "requested_by": "John Doe (Tenant)",
      "requested_date": "2024-11-18T09:30:00Z",
      "assigned_to": {
        "vendor_id": "vendor_789",
        "vendor_name": "ABC Plumbing"
      },
      "scheduled_date": "2024-11-19",
      "estimated_cost": 150.00,
      "billable_to_tenant": false,
      "created_at": "2024-11-18T09:30:00Z",
      "updated_at": "2024-11-18T10:15:00Z"
    }
  ],
  "pagination": {...}
}
```

### Create Work Order
```http
POST /work-orders

{
  "property_id": "prop_1234567890",
  "unit_id": "unit_abc123",
  "category": "hvac",
  "priority": "normal",
  "description": "AC not cooling effectively",
  "requested_by": "Tenant",
  "entry_permission": "contact_first",
  "entry_notes": "Dog in apartment, please call before entering"
}
```

### Update Work Order
```http
PATCH /work-orders/{work_order_id}

{
  "status": "completed",
  "completed_date": "2024-11-19T14:30:00Z",
  "actual_cost": 175.00,
  "resolution_notes": "Replaced faulty faucet cartridge"
}
```

## Financial Reports

### Get Income Statement
```http
GET /reports/income-statement

Query Parameters:
- property_id (required)
- start_date (required)
- end_date (required)
- period (month, quarter, year)
```

### Get Rent Roll
```http
GET /reports/rent-roll

Query Parameters:
- property_id (required)
- as_of_date (default: today)
- include_vacant (boolean)
```

### Get Delinquency Report
```http
GET /reports/delinquency

Query Parameters:
- property_id (optional)
- min_balance (default: 0.01)
- include_payment_plans (boolean)
```

## Webhooks

### Available Events
- `property.created`, `property.updated`, `property.deleted`
- `unit.created`, `unit.updated`, `unit.status_changed`
- `lease.created`, `lease.renewed`, `lease.terminated`, `lease.expiring_soon`
- `tenant.created`, `tenant.moved_in`, `tenant.moved_out`
- `payment.received`, `payment.failed`, `payment.nsf`
- `charge.posted`
- `workorder.created`, `workorder.completed`, `workorder.assigned`

### Webhook Payload Example
```json
{
  "event": "payment.received",
  "timestamp": "2024-11-18T14:30:00Z",
  "data": {
    "payment_id": "pmt_123456",
    "lease_id": "lease_xyz789",
    "tenant_id": "tenant_def456",
    "amount": 2250.00,
    "payment_method": "ach"
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "start_date",
        "message": "Start date must be before end date"
      }
    ]
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., overlapping lease)
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1634567890
```

- Standard: 1000 requests per hour
- Enterprise: 5000 requests per hour
- Burst: 100 requests per minute
