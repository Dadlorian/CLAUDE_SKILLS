# Logistics API Design Standards

## Overview

This document establishes API design standards for transportation and logistics systems, based on industry best practices from leading logistics technology companies (Flexport, project44, Uber Freight, Amazon Logistics) and standard API design principles (REST, GraphQL, gRPC).

## Core Principles

### 1. **Domain-Driven Design**
APIs should reflect real-world logistics domain concepts:
- **Shipments**, **Orders**, **Carriers**, **Vehicles**, **Drivers**, **Routes**, **Warehouses**
- Use ubiquitous language that logistics professionals understand
- Avoid technical jargon that obscures business meaning

### 2. **Idempotency**
All mutating operations (POST, PUT, PATCH, DELETE) must be idempotent:
```http
POST /api/v1/shipments
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "order_id": "ORD-12345",
  "carrier": "FEDEX",
  "service_type": "GROUND"
}
```

### 3. **Webhook-First for Async Operations**
Long-running operations (route optimization, shipment tracking updates) use webhooks:
```json
{
  "webhook_url": "https://customer.com/webhooks/shipments",
  "events": [
    "shipment.created",
    "shipment.in_transit",
    "shipment.delivered",
    "shipment.exception"
  ]
}
```

## Resource Design

### Shipment Resource

**Properties**:
```typescript
interface Shipment {
  id: string;                          // Unique identifier
  tracking_number: string;              // Customer-facing tracking number
  order_id: string;                     // Associated order
  carrier: CarrierCode;                 // FEDEX, UPS, USPS, etc.
  service_type: ServiceType;            // GROUND, EXPRESS, OVERNIGHT
  origin: Address;
  destination: Address;
  status: ShipmentStatus;
  milestones: Milestone[];              // Event history
  estimated_delivery: ISO8601DateTime;
  actual_delivery: ISO8601DateTime | null;
  packages: Package[];
  metadata: Record<string, any>;        // Custom fields
  created_at: ISO8601DateTime;
  updated_at: ISO8601DateTime;
}

enum ShipmentStatus {
  CREATED = "created",
  TENDERED = "tendered",
  PICKED_UP = "picked_up",
  IN_TRANSIT = "in_transit",
  OUT_FOR_DELIVERY = "out_for_delivery",
  DELIVERED = "delivered",
  EXCEPTION = "exception",
  CANCELLED = "cancelled"
}
```

**Endpoints**:
```
POST   /api/v1/shipments                 # Create shipment
GET    /api/v1/shipments/{id}            # Get shipment details
GET    /api/v1/shipments                 # List shipments (paginated)
PATCH  /api/v1/shipments/{id}            # Update shipment
DELETE /api/v1/shipments/{id}            # Cancel shipment
GET    /api/v1/shipments/{id}/track      # Get tracking details
POST   /api/v1/shipments/{id}/milestones # Add milestone event
GET    /api/v1/shipments/{id}/documents  # Get shipping documents (BOL, POD)
```

### Route Resource

**Properties**:
```typescript
interface Route {
  id: string;
  vehicle_id: string;
  driver_id: string;
  status: RouteStatus;
  stops: Stop[];
  total_distance_meters: number;
  total_duration_seconds: number;
  optimization_parameters: OptimizationParams;
  polyline: string;                    // Encoded polyline (Google format)
  scheduled_start: ISO8601DateTime;
  actual_start: ISO8601DateTime | null;
  scheduled_end: ISO8601DateTime;
  actual_end: ISO8601DateTime | null;
  created_at: ISO8601DateTime;
  updated_at: ISO8601DateTime;
}

interface Stop {
  sequence: number;                    // Order in route
  type: "pickup" | "delivery" | "depot";
  location: GeoCoordinates;
  address: Address;
  time_window_start: ISO8601DateTime;
  time_window_end: ISO8601DateTime;
  estimated_arrival: ISO8601DateTime;
  actual_arrival: ISO8601DateTime | null;
  service_duration_seconds: number;
  orders: string[];                    // Order IDs for this stop
  status: StopStatus;
  proof_of_delivery: ProofOfDelivery | null;
}
```

**Endpoints**:
```
POST   /api/v1/routes/optimize           # Optimize routes (async)
GET    /api/v1/routes/{id}               # Get route details
GET    /api/v1/routes                    # List routes
PATCH  /api/v1/routes/{id}               # Update route
POST   /api/v1/routes/{id}/start         # Mark route started
POST   /api/v1/routes/{id}/complete      # Mark route completed
PATCH  /api/v1/routes/{id}/stops/{seq}   # Update stop status
```

### Vehicle Resource

**Properties**:
```typescript
interface Vehicle {
  id: string;
  license_plate: string;
  vin: string;
  type: VehicleType;                   // VAN, TRUCK, SEMI, etc.
  capacity_kg: number;
  capacity_cubic_meters: number;
  status: VehicleStatus;
  current_location: GeoCoordinates | null;
  assigned_driver_id: string | null;
  telematics_device_id: string | null;
  fuel_type: FuelType;
  metadata: Record<string, any>;
  created_at: ISO8601DateTime;
  updated_at: ISO8601DateTime;
}
```

**Endpoints**:
```
POST   /api/v1/vehicles                  # Add vehicle to fleet
GET    /api/v1/vehicles/{id}             # Get vehicle details
GET    /api/v1/vehicles                  # List vehicles
PATCH  /api/v1/vehicles/{id}             # Update vehicle
DELETE /api/v1/vehicles/{id}             # Remove vehicle
GET    /api/v1/vehicles/{id}/location    # Get real-time location
GET    /api/v1/vehicles/{id}/diagnostics # Get telematics data
```

## Common Patterns

### 1. Pagination

**Cursor-based pagination** (recommended for large datasets):
```http
GET /api/v1/shipments?limit=100&cursor=eyJpZCI6MTIzNDU2fQ

Response:
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNTU2fQ",
    "has_more": true
  }
}
```

### 2. Filtering

Use query parameters for filtering:
```http
GET /api/v1/shipments?status=in_transit&carrier=FEDEX&created_after=2025-01-01
```

### 3. Sorting

```http
GET /api/v1/shipments?sort=-created_at,status  # - prefix for descending
```

### 4. Field Selection

Allow clients to request specific fields:
```http
GET /api/v1/shipments/{id}?fields=id,tracking_number,status,estimated_delivery
```

### 5. Batch Operations

```http
POST /api/v1/shipments/batch

{
  "shipments": [
    { "order_id": "ORD-1", "carrier": "FEDEX" },
    { "order_id": "ORD-2", "carrier": "UPS" }
  ]
}

Response:
{
  "results": [
    { "index": 0, "id": "SHP-1001", "status": "created" },
    { "index": 1, "error": "Invalid carrier", "status": "failed" }
  ]
}
```

## Webhook Design

### Event Payload Structure

```json
{
  "id": "evt_1a2b3c4d5e6f",
  "type": "shipment.in_transit",
  "created_at": "2025-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "SHP-12345",
      "tracking_number": "1Z999AA10123456784",
      "status": "in_transit",
      "current_location": {
        "lat": 37.7749,
        "lon": -122.4194,
        "city": "San Francisco",
        "state": "CA"
      },
      "estimated_delivery": "2025-01-16T17:00:00Z"
    },
    "previous_attributes": {
      "status": "picked_up"
    }
  }
}
```

### Webhook Security

**Signature Verification**:
```http
POST /webhooks/shipments
X-Signature: t=1642258200,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
Content-Type: application/json

{...}
```

Verify signature:
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    timestamp, signature = parse_signature_header(signature_header)
    signed_payload = f"{timestamp}.{payload.decode()}"
    expected_signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

## Rate Limiting

**HTTP Headers**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1642258200
Retry-After: 60
```

**Response**:
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Rate limit of 1000 requests per hour exceeded",
    "retry_after": 60
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid shipment parameters",
    "errors": [
      {
        "field": "destination.postal_code",
        "code": "invalid_format",
        "message": "Postal code must be 5 digits"
      },
      {
        "field": "packages[0].weight_kg",
        "code": "out_of_range",
        "message": "Weight must be between 0.1 and 100 kg"
      }
    ],
    "request_id": "req_1a2b3c4d5e6f"
  }
}
```

### Standard Error Types

| HTTP Status | Error Type | Description |
|-------------|------------|-------------|
| 400 | `validation_error` | Invalid request parameters |
| 401 | `authentication_error` | Invalid or missing API key |
| 403 | `authorization_error` | Insufficient permissions |
| 404 | `resource_not_found` | Resource does not exist |
| 409 | `conflict_error` | Resource conflict (e.g., duplicate) |
| 422 | `business_logic_error` | Valid format but violates business rules |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_error` | Server error |
| 503 | `service_unavailable` | Temporary outage |

## Versioning

### URL Versioning (Recommended)

```
/api/v1/shipments
/api/v2/shipments
```

### Header Versioning (Alternative)

```http
GET /api/shipments
Accept: application/vnd.logistics.v1+json
```

### Deprecation Process

1. Announce deprecation 6 months in advance
2. Add deprecation headers:
   ```http
   Deprecation: true
   Sunset: Sat, 01 Jul 2025 23:59:59 GMT
   Link: <https://docs.api.com/migration-v2>; rel="deprecation"
   ```
3. Maintain old version for 12 months minimum

## Authentication

### API Key (Simple)

```http
GET /api/v1/shipments
Authorization: Bearer sk_live_1a2b3c4d5e6f7g8h9i0j
```

### OAuth 2.0 (Enterprise)

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=abc123&
client_secret=xyz789&
scope=shipments:read shipments:write
```

## Testing

### Sandbox Environment

- Base URL: `https://api-sandbox.logistics.com`
- Test API keys: `sk_test_*`
- Simulated carrier responses
- No real shipments created

### Idempotency Testing

```bash
# Same request twice with same idempotency key
curl -X POST https://api.logistics.com/v1/shipments \
  -H "Idempotency-Key: test-123" \
  -d '{"order_id": "ORD-1"}'

# Should return same shipment ID both times
```

## Documentation Standards

### OpenAPI 3.0 Specification

```yaml
openapi: 3.0.0
info:
  title: Logistics API
  version: 1.0.0
  description: Comprehensive API for transportation and logistics operations

paths:
  /shipments:
    post:
      summary: Create a new shipment
      operationId: createShipment
      tags:
        - Shipments
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateShipmentRequest'
      responses:
        '201':
          description: Shipment created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Shipment'
        '400':
          $ref: '#/components/responses/ValidationError'
```

### Code Examples

Provide examples in multiple languages:

**Python**:
```python
import requests

response = requests.post(
    'https://api.logistics.com/v1/shipments',
    headers={'Authorization': 'Bearer sk_live_abc123'},
    json={
        'order_id': 'ORD-12345',
        'carrier': 'FEDEX',
        'origin': {...},
        'destination': {...}
    }
)
shipment = response.json()
```

**JavaScript**:
```javascript
const response = await fetch('https://api.logistics.com/v1/shipments', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer sk_live_abc123',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    order_id: 'ORD-12345',
    carrier: 'FEDEX',
    origin: {...},
    destination: {...}
  })
});
const shipment = await response.json();
```

## Performance Standards

- **Response Time**: p50 < 200ms, p99 < 1000ms
- **Availability**: 99.9% uptime SLA
- **Rate Limits**:
  - Standard tier: 1,000 requests/hour
  - Enterprise tier: 10,000 requests/hour
- **Payload Size**: Maximum 10MB per request

## References

- **Stripe API**: Gold standard for developer experience
- **Twilio API**: Excellent documentation and error messages
- **Google Cloud APIs**: Consistent resource naming and design
- **REST API Design Guidelines**: Microsoft, Google, Zalando
- **OpenAPI Specification**: https://swagger.io/specification/

---

**Version**: 1.0
**Last Updated**: 2025-01-19
**Maintainer**: Transportation & Logistics Domain Team
