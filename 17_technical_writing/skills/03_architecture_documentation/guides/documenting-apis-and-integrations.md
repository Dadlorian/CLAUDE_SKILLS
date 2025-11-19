# Documenting APIs and Integrations Guide

## Table of Contents

1. [Overview](#overview)
2. [REST API Documentation](#rest-api-documentation)
3. [gRPC Service Documentation](#grpc-service-documentation)
4. [Webhook Integration Documentation](#webhook-integration-documentation)
5. [Third-Party Integration Guides](#third-party-integration-guides)
6. [Error Handling Documentation](#error-handling-documentation)
7. [Authentication and Security](#authentication-and-security)
8. [Rate Limiting and Quotas](#rate-limiting-and-quotas)
9. [Client Libraries](#client-libraries)
10. [API Versioning Strategy](#api-versioning-strategy)
11. [Migration Guides](#migration-guides)
12. [Best Practices](#best-practices)

## Overview

APIs and integrations are the primary means through which distributed systems communicate. Comprehensive documentation enables developers to understand contracts, implement integrations correctly, and troubleshoot issues effectively.

This guide provides patterns for documenting various API types and integration scenarios commonly encountered in microservices architectures.

## REST API Documentation

### OpenAPI/Swagger Specification

```yaml
openapi: 3.0.0
info:
  title: Order Management API
  version: 2.1.0
  description: |
    REST API for managing customer orders in the e-commerce platform.

    ## Changelog
    - v2.1.0 (2025-11-19): Add async order processing endpoint
    - v2.0.0 (2025-10-15): Breaking change - migrate to v2 endpoints
    - v1.0.0 (2025-01-01): Initial release

  contact:
    name: Order Service Team
    email: orders-team@example.com
    url: https://example.com/support

  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html

servers:
  - url: https://api.example.com/orders
    description: Production
    variables:
      basePath:
        default: /v2
  - url: https://staging-api.example.com/orders
    description: Staging
    variables:
      basePath:
        default: /v2

tags:
  - name: Orders
    description: Order creation, retrieval, and management
  - name: Order Items
    description: Individual items within orders
  - name: Order Status
    description: Order lifecycle and status tracking

paths:
  /api/v2/orders:
    post:
      tags:
        - Orders
      summary: Create a new order
      operationId: createOrder
      description: |
        Creates a new order for a customer. The order is created in DRAFT status
        and must be confirmed before proceeding to payment.

        ## Request Processing
        1. Validate order items exist in inventory
        2. Reserve inventory (async)
        3. Create order aggregate
        4. Publish OrderCreated event
        5. Return order details with confirmation URL

        ## Async Operations
        Inventory reservation happens asynchronously. Check order status
        endpoint to determine if inventory was reserved successfully.

      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
            examples:
              simple_order:
                summary: Single item order
                value:
                  customer_id: "550e8400-e29b-41d4-a716-446655440000"
                  items:
                    - sku: "PROD-12345"
                      quantity: 1
              bulk_order:
                summary: Multiple items order
                value:
                  customer_id: "550e8400-e29b-41d4-a716-446655440000"
                  items:
                    - sku: "PROD-12345"
                      quantity: 2
                    - sku: "PROD-67890"
                      quantity: 1

      parameters:
        - name: X-Idempotency-Key
          in: header
          required: true
          schema:
            type: string
            format: uuid
          description: |
            Unique idempotency key for this request. If the same key is sent
            multiple times, the API returns the same response without creating
            duplicate orders. Helps prevent duplicate orders from network retries.

            Format: UUID v4
            Example: 550e8400-e29b-41d4-a716-446655440000

        - name: X-Request-ID
          in: header
          required: false
          schema:
            type: string
            format: uuid
          description: |
            Optional request tracking ID. Used for distributed tracing and
            debugging. If not provided, the server generates one.

      responses:
        '201':
          description: Order created successfully
          headers:
            Location:
              schema:
                type: string
                format: uri
              description: |
                URI to access the created order resource.
                Example: https://api.example.com/orders/api/v2/orders/ORD-20251119-001
            X-Request-ID:
              schema:
                type: string
                format: uuid
              description: Request tracking ID for debugging
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
              example:
                order_id: "ORD-20251119-001"
                status: "DRAFT"
                customer_id: "550e8400-e29b-41d4-a716-446655440000"
                items:
                  - sku: "PROD-12345"
                    quantity: 1
                    unit_price_cents: 9999
                order_total_cents: 10799
                currency: "USD"
                created_at: "2025-11-19T14:32:00Z"

        '400':
          description: Bad request - validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              examples:
                missing_items:
                  summary: Order has no items
                  value:
                    error_code: "INVALID_ORDER"
                    message: "Order must contain at least one item"
                    details:
                      field: "items"
                      constraint: "min_length"
                      constraint_value: 1
                invalid_sku:
                  summary: Invalid product SKU
                  value:
                    error_code: "INVALID_SKU"
                    message: "Product SKU 'INVALID-SKU' does not exist"
                    details:
                      sku: "INVALID-SKU"

        '401':
          description: Unauthorized - authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                error_code: "UNAUTHORIZED"
                message: "Missing or invalid authentication token"

        '429':
          description: Too many requests - rate limit exceeded
          headers:
            X-RateLimit-Limit:
              schema:
                type: integer
              description: Maximum requests allowed per minute
            X-RateLimit-Remaining:
              schema:
                type: integer
              description: Remaining requests in current window
            X-RateLimit-Reset:
              schema:
                type: integer
                format: unix-time
              description: Unix timestamp when rate limit resets
            Retry-After:
              schema:
                type: integer
              description: Seconds to wait before retrying
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                error_code: "RATE_LIMIT_EXCEEDED"
                message: "Too many requests (100/min limit)"

        '500':
          description: Server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
              example:
                error_code: "INTERNAL_SERVER_ERROR"
                message: "An unexpected error occurred"
                request_id: "550e8400-e29b-41d4-a716-446655440000"

      security:
        - BearerAuth: []
        - ApiKeyAuth: []

    get:
      tags:
        - Orders
      summary: List orders
      operationId: listOrders
      description: |
        Retrieve paginated list of orders for authenticated customer.

        ## Filtering
        Results can be filtered by status, date range, and other criteria.

        ## Pagination
        Uses cursor-based pagination for efficient large result sets.
        For the next page, use the `next_cursor` value from the response.

      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [DRAFT, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED]
          description: Filter by order status
          example: CONFIRMED

        - name: created_after
          in: query
          schema:
            type: string
            format: date-time
          description: Filter orders created after this date (ISO 8601)
          example: "2025-11-01T00:00:00Z"

        - name: created_before
          in: query
          schema:
            type: string
            format: date-time
          description: Filter orders created before this date (ISO 8601)

        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
          description: Maximum number of orders to return

        - name: cursor
          in: query
          schema:
            type: string
          description: |
            Pagination cursor from previous response.
            Use the `next_cursor` value to get the next page.

      responses:
        '200':
          description: List of orders
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderListResponse'

  /api/v2/orders/{order_id}:
    get:
      tags:
        - Orders
      summary: Get order details
      operationId: getOrder
      parameters:
        - name: order_id
          in: path
          required: true
          schema:
            type: string
            pattern: '^ORD-\d{8}-\d{6}$'
          description: Order ID (format: ORD-YYYYMMDD-XXXXXX)
          example: "ORD-20251119-001"

      responses:
        '200':
          description: Order details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'

        '404':
          description: Order not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    CreateOrderRequest:
      type: object
      required: [customer_id, items]
      properties:
        customer_id:
          type: string
          format: uuid
          description: Customer unique identifier
        items:
          type: array
          minItems: 1
          maxItems: 100
          items:
            $ref: '#/components/schemas/OrderItemRequest'

    OrderItemRequest:
      type: object
      required: [sku, quantity]
      properties:
        sku:
          type: string
          pattern: '^[A-Z0-9\-]{5,20}$'
          description: Product SKU
        quantity:
          type: integer
          minimum: 1
          maximum: 1000

    OrderResponse:
      type: object
      properties:
        order_id:
          type: string
          description: Unique order identifier
        status:
          type: string
          enum: [DRAFT, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED]
        customer_id:
          type: string
          format: uuid
        items:
          type: array
          items:
            $ref: '#/components/schemas/OrderItem'
        order_total_cents:
          type: integer
          minimum: 0
        currency:
          type: string
          pattern: '^[A-Z]{3}$'
        created_at:
          type: string
          format: date-time
        confirmed_at:
          type: string
          format: date-time
          nullable: true

    OrderItem:
      type: object
      properties:
        sku:
          type: string
        product_name:
          type: string
        quantity:
          type: integer
        unit_price_cents:
          type: integer

    OrderListResponse:
      type: object
      properties:
        orders:
          type: array
          items:
            $ref: '#/components/schemas/OrderResponse'
        next_cursor:
          type: string
          nullable: true
          description: Cursor for fetching next page. Null if no more results.
        total_count:
          type: integer

    ErrorResponse:
      type: object
      required: [error_code, message]
      properties:
        error_code:
          type: string
          enum: [INVALID_ORDER, INVALID_SKU, UNAUTHORIZED, RATE_LIMIT_EXCEEDED, INTERNAL_SERVER_ERROR]
        message:
          type: string
        request_id:
          type: string
          format: uuid
        details:
          type: object
          additionalProperties: true

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JSON Web Token (JWT) authentication.

        Format: `Authorization: Bearer <token>`

        Token lifetime: 1 hour
        Refresh endpoint: POST /auth/refresh

    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key authentication for server-to-server communication.

        Format: `X-API-Key: <api-key>`

        Keys: Available in developer dashboard
        Rotation: Recommended every 90 days
```

### README for REST API

```markdown
## Order Management API

### Quick Start

#### 1. Authentication
```bash
# Get authentication token
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secret"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "Bearer",
#   "expires_in": 3600
# }
```

#### 2. Create an Order
```bash
curl -X POST https://api.example.com/orders/api/v2/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "items": [
      {
        "sku": "PROD-12345",
        "quantity": 1
      }
    ]
  }'
```

#### 3. Check Order Status
```bash
curl -X GET https://api.example.com/orders/api/v2/orders/ORD-20251119-001 \
  -H "Authorization: Bearer <token>"
```

### Key Concepts

#### Order Lifecycle
```
DRAFT → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
           ↓
         CANCELLED
```

#### Async Operations
Order creation is fast (< 100ms), but inventory reservation and payment
processing happen asynchronously. Poll the order status endpoint to
check when these operations complete.

#### Idempotency
The `X-Idempotency-Key` header ensures requests are idempotent.
If the same key is sent multiple times within 24 hours, the API
returns the same response without side effects.

#### Error Handling
```javascript
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.json();
    switch(error.error_code) {
      case 'INVALID_SKU':
        console.error('Product not found:', error.details.sku);
        break;
      case 'RATE_LIMIT_EXCEEDED':
        console.error('Rate limited, retry after:', response.headers.get('Retry-After'));
        break;
      default:
        console.error('API error:', error.message);
    }
  }
} catch (err) {
  console.error('Network error:', err);
}
```

### Pagination

The API uses cursor-based pagination:

```bash
# Get first page
curl https://api.example.com/orders/api/v2/orders \
  -H "Authorization: Bearer <token>"

# Response:
# {
#   "orders": [...20 orders...],
#   "next_cursor": "eyJvZmZzZXQiOiAyMH0="
# }

# Get next page
curl https://api.example.com/orders/api/v2/orders?cursor=eyJvZmZzZXQiOiAyMH0= \
  -H "Authorization: Bearer <token>"
```

### Rate Limiting

The API allows 100 requests per minute per API key/token.

When you hit the limit, the response includes:
- `X-RateLimit-Limit: 100`
- `X-RateLimit-Remaining: 0`
- `X-RateLimit-Reset: 1700402400`
- `Retry-After: 37`

Wait the number of seconds in `Retry-After` before retrying.

### Webhook Integration

Webhooks notify your application of order status changes in real-time.

#### Setup Webhook
```bash
curl -X POST https://api.example.com/webhooks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.example.com/webhooks/orders",
    "events": ["order.confirmed", "order.shipped", "order.delivered"],
    "secret": "your-secret-key"
  }'
```

#### Webhook Events
- `order.confirmed`: Order payment processed
- `order.shipped`: Order picked and sent to carrier
- `order.delivered`: Order delivered to customer
- `order.cancelled`: Order cancelled

#### Webhook Payload
```json
{
  "event_id": "evt-20251119-xyz789",
  "event_type": "order.shipped",
  "timestamp": "2025-11-19T14:32:00Z",
  "order_id": "ORD-20251119-001",
  "webhook_signature": "sha256=abcd1234..."
}
```

#### Verifying Webhooks
```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const hash = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return signature === `sha256=${hash}`;
}
```
```

## gRPC Service Documentation

### Protocol Buffers Definition

```protobuf
syntax = "proto3";

package order.v2;

option go_package = "github.com/example/order-service/api/v2";
option java_package = "com.example.order.api.v2";

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

service OrderService {
  option (google.api.default_host) = "order-service.default.svc.cluster.local:50051";

  // Create a new order
  // Request must include customer_id and at least one item
  // Returns Order with status DRAFT
  // Publishes OrderCreated event asynchronously
  rpc CreateOrder(CreateOrderRequest) returns (Order) {
    option (google.api.http) = {
      post: "/v2/orders"
      body: "*"
    };
  }

  // Get order details
  // Returns NOT_FOUND if order doesn't exist
  // Includes full order history in response
  rpc GetOrder(GetOrderRequest) returns (Order) {
    option (google.api.http) = {
      get: "/v2/orders/{order_id}"
    };
  }

  // List customer orders with pagination
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse) {
    option (google.api.http) = {
      get: "/v2/customers/{customer_id}/orders"
    };
  }

  // Confirm order (authorize payment)
  // Transitions order from DRAFT to CONFIRMED
  // Publishes OrderConfirmed event
  // Fails with FAILED_PRECONDITION if order already confirmed
  rpc ConfirmOrder(ConfirmOrderRequest) returns (Order) {
    option (google.api.http) = {
      post: "/v2/orders/{order_id}/confirm"
      body: "*"
    };
  }

  // Cancel order
  // Can only cancel DRAFT or CONFIRMED orders
  // Returns FAILED_PRECONDITION for PROCESSING or later states
  rpc CancelOrder(CancelOrderRequest) returns (Order) {
    option (google.api.http) = {
      post: "/v2/orders/{order_id}/cancel"
      body: "*"
    };
  }
}

message CreateOrderRequest {
  // Customer unique identifier (UUID v4)
  // Required field
  string customer_id = 1 [(google.api.field_behavior) = REQUIRED];

  // Order line items
  // Must contain at least 1 and at most 100 items
  repeated OrderItem items = 2 [(google.api.field_behavior) = REQUIRED];

  // Idempotency key for duplicate detection
  // UUID v4 format, required for production use
  string idempotency_key = 3;

  // Optional metadata
  map<string, string> metadata = 4;
}

message OrderItem {
  // Product SKU (stock keeping unit)
  // Pattern: [A-Z0-9\-]{5,20}
  string sku = 1 [(google.api.field_behavior) = REQUIRED];

  // Quantity to order
  // Range: 1 to 1000
  int32 quantity = 2 [(google.api.field_behavior) = REQUIRED];

  // Requested unit price in cents (optional)
  // If not provided, current catalog price is used
  // Allows price-checking before order creation
  int64 unit_price_cents = 3;
}

message Order {
  // Unique order identifier
  string order_id = 1;

  // Customer who placed order
  string customer_id = 2;

  // Current order status
  OrderStatus status = 3;

  // Order line items
  repeated OrderItem items = 4;

  // Total order amount in cents
  // Includes tax and shipping
  int64 order_total_cents = 5;

  // ISO 4217 currency code
  string currency = 6;

  // When order was created
  google.protobuf.Timestamp created_at = 7;

  // When order was confirmed (null if not confirmed)
  google.protobuf.Timestamp confirmed_at = 8;

  // Version number for optimistic locking
  // Increment on each update
  int32 version = 9;
}

enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;
  DRAFT = 1;           // Created but not confirmed
  CONFIRMED = 2;       // Payment authorized
  PROCESSING = 3;      // Being prepared for shipment
  SHIPPED = 4;         // Handed to carrier
  DELIVERED = 5;       // Received by customer
  CANCELLED = 6;       // Order cancelled
}

message GetOrderRequest {
  // Order identifier
  // Format: ORD-YYYYMMDD-XXXXXX
  string order_id = 1 [(google.api.field_behavior) = REQUIRED];

  // Include order events/history
  // If true, response includes list of all state changes
  bool include_history = 2;
}

message ListOrdersRequest {
  // Customer identifier
  string customer_id = 1 [(google.api.field_behavior) = REQUIRED];

  // Filter by status
  OrderStatus status_filter = 2;

  // Pagination: maximum results per page
  // Range: 1 to 100, default: 20
  int32 page_size = 3;

  // Pagination: opaque cursor from previous response
  string page_token = 4;

  // Sort order
  enum SortOrder {
    SORT_ORDER_UNSPECIFIED = 0;
    CREATED_DESC = 1;  // Newest first (default)
    CREATED_ASC = 2;   // Oldest first
  }
  SortOrder sort_order = 5;
}

message ListOrdersResponse {
  // List of orders
  repeated Order orders = 1;

  // Opaque cursor for fetching next page
  // Empty string if no more results
  string next_page_token = 2;

  // Total count of matching orders
  int32 total_count = 3;
}

message ConfirmOrderRequest {
  // Order to confirm
  string order_id = 1 [(google.api.field_behavior) = REQUIRED];

  // Payment authorization token
  // Obtained from payment service
  string payment_token = 2 [(google.api.field_behavior) = REQUIRED];

  // Expected version for optimistic locking
  // If provided, confirmation fails if order version differs
  int32 expected_version = 3;
}

message CancelOrderRequest {
  // Order to cancel
  string order_id = 1 [(google.api.field_behavior) = REQUIRED];

  // Cancellation reason
  string reason = 2;

  // Expected version for optimistic locking
  int32 expected_version = 3;
}
```

### Go Client Implementation

```markdown
## Using Order Service gRPC Client

### Installation
```bash
go get github.com/example/order-service/client
```

### Example Usage
```go
package main

import (
  "context"
  "log"
  "time"

  orderv2 "github.com/example/order-service/api/v2"
  "google.golang.org/grpc"
  "google.golang.org/grpc/credentials/insecure"
)

func main() {
  // Connect to order service
  ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
  defer cancel()

  conn, err := grpc.DialContext(ctx,
    "order-service.default.svc.cluster.local:50051",
    grpc.WithTransportCredentials(insecure.NewCredentials()),
  )
  if err != nil {
    log.Fatalf("Failed to connect: %v", err)
  }
  defer conn.Close()

  // Create client
  client := orderv2.NewOrderServiceClient(conn)

  // Call CreateOrder
  ctx, cancel = context.WithTimeout(context.Background(), 10*time.Second)
  defer cancel()

  order, err := client.CreateOrder(ctx, &orderv2.CreateOrderRequest{
    CustomerId: "550e8400-e29b-41d4-a716-446655440000",
    Items: []*orderv2.OrderItem{
      {
        Sku:      "PROD-12345",
        Quantity: 1,
      },
    },
    IdempotencyKey: "550e8400-e29b-41d4-a716-446655440100",
  })
  if err != nil {
    log.Fatalf("CreateOrder failed: %v", err)
  }

  log.Printf("Order created: %s (status: %s)", order.OrderId, order.Status)

  // Call GetOrder
  order, err = client.GetOrder(ctx, &orderv2.GetOrderRequest{
    OrderId:        order.OrderId,
    IncludeHistory: true,
  })
  if err != nil {
    log.Fatalf("GetOrder failed: %v", err)
  }

  log.Printf("Order details: %v", order)
}
```

### Error Handling
```go
// gRPC uses status codes for errors
import "google.golang.org/grpc/status"
import "google.golang.org/grpc/codes"

_, err := client.CreateOrder(ctx, req)
if err != nil {
  st := status.Convert(err)

  switch st.Code() {
  case codes.InvalidArgument:
    log.Printf("Invalid request: %s", st.Message())
  case codes.NotFound:
    log.Printf("Order not found: %s", st.Message())
  case codes.FailedPrecondition:
    log.Printf("Invalid state transition: %s", st.Message())
  case codes.ResourceExhausted:
    log.Printf("Rate limit exceeded: %s", st.Message())
  case codes.Unavailable:
    log.Printf("Service temporarily unavailable: %s", st.Message())
  default:
    log.Printf("Error: %v", err)
  }
}
```
```

## Webhook Integration Documentation

### Webhook Configuration

```markdown
## Setting Up Webhooks

### 1. Register Webhook Endpoint
Your application must have an HTTPS endpoint that:
- Accepts POST requests
- Validates webhook signatures
- Responds with 200 status within 30 seconds
- Handles duplicate events idempotently

### 2. Create Webhook
```bash
curl -X POST https://api.example.com/webhooks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.example.com/webhooks/orders",
    "events": ["order.confirmed", "order.shipped"],
    "secret": "your-secret-key",
    "active": true
  }'

# Response:
# {
#   "webhook_id": "wh_20251119_xyz",
#   "url": "https://your-app.example.com/webhooks/orders",
#   "events": ["order.confirmed", "order.shipped"],
#   "secret": "your-secret-key",
#   "active": true,
#   "created_at": "2025-11-19T14:32:00Z"
# }
```

### 3. Handle Webhook Events
```javascript
const express = require('express');
const crypto = require('crypto');

app.post('/webhooks/orders', (req, res) => {
  // 1. Verify webhook signature
  const signature = req.headers['x-webhook-signature'];
  const timestamp = req.headers['x-webhook-timestamp'];

  const payload = JSON.stringify(req.body);
  const hash = crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(`${timestamp}.${payload}`)
    .digest('hex');

  if (hash !== signature) {
    return res.status(401).send('Invalid signature');
  }

  // 2. Check timestamp (prevent replay attacks)
  const now = Date.now() / 1000;
  if (Math.abs(now - parseInt(timestamp)) > 300) { // 5 minutes
    return res.status(401).send('Webhook too old');
  }

  // 3. Process webhook event
  const { event_id, event_type, order_id, timestamp: event_timestamp } = req.body;

  // Store event_id to detect duplicates
  if (await hasProcessedEvent(event_id)) {
    return res.status(200).send('OK'); // Idempotent response
  }

  // Handle event
  switch (event_type) {
    case 'order.confirmed':
      await handleOrderConfirmed(order_id);
      break;
    case 'order.shipped':
      await handleOrderShipped(order_id);
      break;
    default:
      console.warn(`Unknown event type: ${event_type}`);
  }

  // 4. Mark event as processed
  await markEventProcessed(event_id);

  // 5. Return 200 to acknowledge
  res.status(200).send('OK');
});
```

### 4. Webhook Retry Logic
If your endpoint returns a non-200 status:
- Retry 1: After 5 seconds
- Retry 2: After 30 seconds
- Retry 3: After 2 minutes
- Retry 4: After 15 minutes
- Retry 5: After 1 hour
- Retry 6: After 4 hours

Total retry window: ~6 hours

### 5. Testing Webhooks
Use the test webhook feature:
```bash
curl -X POST https://api.example.com/webhooks/test \
  -H "Authorization: Bearer <token>" \
  -d '{
    "webhook_id": "wh_20251119_xyz",
    "event_type": "order.confirmed"
  }'
```

This sends a test webhook to your endpoint without creating a real event.

### 6. Webhook Events Reference

| Event Type | Trigger | Example Payload |
|---|---|---|
| order.created | Order created in DRAFT state | See below |
| order.confirmed | Order payment authorized | See below |
| order.shipped | Order handed to carrier | See below |
| order.delivered | Order delivered to customer | See below |
| order.cancelled | Order cancelled | See below |

#### order.confirmed Event
```json
{
  "event_id": "evt-20251119-abc123",
  "event_type": "order.confirmed",
  "timestamp": "2025-11-19T14:33:45Z",
  "order_id": "ORD-20251119-001",
  "customer_id": "CUST-54321",
  "order_details": {
    "status": "CONFIRMED",
    "total_cents": 10799,
    "currency": "USD",
    "items_count": 1
  }
}
```
```

## Third-Party Integration Guides

### Stripe Payment Integration

```markdown
## Integrating with Stripe

### Overview
Payment processing via Stripe for collecting customer payments.

### Setup Steps

1. **Get API Keys**
   - Login to Stripe dashboard
   - Navigate to Developers > API Keys
   - Copy Secret Key (starts with sk_) and Publishable Key (starts with pk_)

2. **Store Keys Securely**
   ```
   STRIPE_SECRET_KEY=sk_live_xyz...
   STRIPE_PUBLISHABLE_KEY=pk_live_abc...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

3. **Authorize Payment**
   ```python
   import stripe

   stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

   payment_intent = stripe.PaymentIntent.create(
     amount=order.total_cents,  # in cents
     currency="usd",
     customer=customer_stripe_id,
     description=f"Order {order.id}",
     metadata={
       "order_id": order.id,
       "customer_id": order.customer_id
     }
   )

   # Return client secret to frontend for checkout form
   return {
     "client_secret": payment_intent.client_secret
   }
   ```

4. **Handle Webhooks**
   ```python
   @app.route('/webhooks/stripe', methods=['POST'])
   def stripe_webhook():
     sig_header = request.headers.get('Stripe-Signature')

     try:
       event = stripe.Webhook.construct_event(
         request.data,
         sig_header,
         os.getenv("STRIPE_WEBHOOK_SECRET")
       )
     except ValueError:
       return "Invalid payload", 400
     except stripe.error.SignatureVerificationError:
       return "Invalid signature", 401

     if event['type'] == 'payment_intent.succeeded':
       payment_intent = event['data']['object']
       order_id = payment_intent['metadata']['order_id']
       # Update order status to CONFIRMED
       confirm_order(order_id)

     return "", 200
   ```

### Error Handling
```python
try:
  payment_intent = stripe.PaymentIntent.create(...)
except stripe.error.CardError as e:
  # Card was declined
  logging.error(f"Card declined: {e.user_message}")
  return {"error": e.user_message}, 400
except stripe.error.RateLimitError:
  # Too many requests to Stripe
  logging.error("Rate limited by Stripe")
  return {"error": "Service temporarily unavailable"}, 503
except stripe.error.InvalidRequestError as e:
  # Invalid parameters
  logging.error(f"Invalid request: {e.message}")
  return {"error": "Invalid payment details"}, 400
except stripe.error.AuthenticationError:
  # API key invalid
  logging.error("Invalid Stripe API key")
  return {"error": "Internal server error"}, 500
```

### Testing

Use Stripe test keys and test card numbers:

| Card Number | Description |
|---|---|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 0002 | Card declined |
| 4000 0025 0000 3155 | Requires 3D Secure |

### Monitoring
Monitor these Stripe events:
- `payment_intent.created`: Payment process initiated
- `payment_intent.amount_capturable_updated`: Amount ready for capture
- `payment_intent.succeeded`: Payment successful
- `payment_intent.payment_failed`: Payment declined/failed
- `charge.refunded`: Refund processed
```

## Error Handling Documentation

### Standard Error Codes

```markdown
## API Error Codes and Responses

### 400 - Bad Request
**Cause**: Request validation failed (malformed JSON, missing required fields, invalid values)

**Examples**:
- Missing required field: `{ "error_code": "MISSING_FIELD", "field": "customer_id" }`
- Invalid format: `{ "error_code": "INVALID_FORMAT", "field": "email", "expected": "email format" }`
- Out of range: `{ "error_code": "OUT_OF_RANGE", "field": "quantity", "min": 1, "max": 1000 }`

**Action**: Fix request and retry immediately (no backoff needed)

### 401 - Unauthorized
**Cause**: Authentication failed (missing/invalid token, expired credentials)

**Examples**:
- Missing token: `{ "error_code": "MISSING_AUTH", "message": "Authorization header required" }`
- Invalid token: `{ "error_code": "INVALID_TOKEN", "message": "Token expired" }`
- Insufficient permissions: `{ "error_code": "INSUFFICIENT_PERMISSIONS" }`

**Action**: Refresh authentication and retry

### 403 - Forbidden
**Cause**: Authenticated but not authorized for this resource

**Example**: `{ "error_code": "FORBIDDEN", "message": "Cannot access other customer's orders" }`

**Action**: Check permissions, do not retry

### 404 - Not Found
**Cause**: Resource doesn't exist

**Example**: `{ "error_code": "NOT_FOUND", "message": "Order ORD-xyz not found" }`

**Action**: Verify resource ID, do not retry if ID is correct

### 409 - Conflict
**Cause**: Request conflicts with current state

**Examples**:
- Duplicate: `{ "error_code": "DUPLICATE", "message": "Order already exists" }`
- Version mismatch: `{ "error_code": "CONFLICT", "message": "Order version mismatch", "current_version": 2, "expected_version": 1 }`

**Action**: Reload resource state and retry if appropriate

### 429 - Too Many Requests
**Cause**: Rate limit exceeded

**Response headers**:
- `Retry-After: 37` (seconds to wait)
- `X-RateLimit-Remaining: 0`
- `X-RateLimit-Reset: 1700402400` (unix timestamp)

**Action**: Wait `Retry-After` seconds, then retry

### 500 - Internal Server Error
**Cause**: Unexpected server error

**Example**: `{ "error_code": "INTERNAL_ERROR", "request_id": "req-xyz", "message": "An unexpected error occurred" }`

**Action**: Retry with exponential backoff (max 5 attempts)

### 503 - Service Unavailable
**Cause**: Server temporarily unavailable (maintenance, overload)

**Example**: `{ "error_code": "SERVICE_UNAVAILABLE", "retry_after": 300 }`

**Action**: Retry with exponential backoff after `retry_after` seconds

## Retry Strategy
```javascript
async function callWithRetry(fn, maxAttempts = 5) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      // Don't retry client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }

      // Don't retry last attempt
      if (attempt === maxAttempts) {
        throw error;
      }

      // Calculate backoff: 2^(attempt-1) * 100ms, with jitter
      const baseDelay = Math.pow(2, attempt - 1) * 100;
      const jitter = Math.random() * 0.1 * baseDelay;
      const delay = baseDelay + jitter;

      // Check Retry-After header
      if (error.headers?.['retry-after']) {
        const retryAfter = parseInt(error.headers['retry-after']) * 1000;
        await sleep(retryAfter);
      } else {
        await sleep(delay);
      }
    }
  }
}
```
```

## Authentication and Security

### OAuth 2.0 Implementation

```markdown
## OAuth 2.0 Authentication Flow

### Authorization Code Flow (Web Applications)

```
┌─────────┐                                      ┌─────────┐
│         │                                      │         │
│  Client │                                      │ Auth    │
│  App    │                                      │ Server  │
│         │                                      │         │
└────┬────┘                                      └────┬────┘
     │                                                │
     │ 1. Redirect to /authorize                     │
     ├───────────────────────────────────────────────>
     │                                                │
     │                        2. User logs in & grants permission
     │                                                │
     │                   3. Redirect with auth code  │
     <─────────────────────────────────────────────────
     │
     │ 4. Exchange code for token (backend)
     ├───────────────────────────────────────────────>
     │                                                │
     │                   5. Return access token      │
     <─────────────────────────────────────────────────
     │
     │ 6. Use token to call API
     ├───────────────────────────────────────────────>
     │                                                │
     │                   7. Return protected resource
     <─────────────────────────────────────────────────
```

### Implementation Steps

1. **Register Application**
   - Client ID: `client_id_xyz`
   - Client Secret: `client_secret_xyz` (keep secret!)
   - Redirect URIs: `https://your-app.example.com/auth/callback`

2. **Request Authorization Code**
   ```
   GET /oauth/authorize?
     client_id=client_id_xyz&
     redirect_uri=https://your-app.example.com/auth/callback&
     response_type=code&
     scope=orders:read orders:write&
     state=random_string_xyz
   ```

3. **Exchange Code for Token**
   ```bash
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&
   code=auth_code_from_step_2&
   client_id=client_id_xyz&
   client_secret=client_secret_xyz&
   redirect_uri=https://your-app.example.com/auth/callback
   ```

4. **Response**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "refresh_token_xyz"
   }
   ```

### Token Refresh
```bash
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
refresh_token=refresh_token_xyz&
client_id=client_id_xyz&
client_secret=client_secret_xyz
```

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "iss": "https://auth.example.com",
    "sub": "user_123",
    "aud": "api.example.com",
    "exp": 1700402400,
    "iat": 1700398800,
    "scopes": ["orders:read", "orders:write"]
  },
  "signature": "hash(header.payload, secret)"
}
```

### JWT Validation
```javascript
const jwt = require('jsonwebtoken');

function verifyToken(token, secret) {
  try {
    const decoded = jwt.verify(token, secret, {
      algorithms: ['HS256'],
      issuer: 'https://auth.example.com',
      audience: 'api.example.com'
    });

    // Check scopes
    const requiredScopes = ['orders:read'];
    const hasScopes = requiredScopes.every(scope =>
      decoded.scopes.includes(scope)
    );

    if (!hasScopes) {
      throw new Error('Insufficient scopes');
    }

    return decoded;
  } catch (error) {
    throw new Error(`Token validation failed: ${error.message}`);
  }
}
```

### Scopes
- `orders:read` - Read orders
- `orders:write` - Create/modify orders
- `customers:read` - Read customer information
- `customers:write` - Modify customer information
- `admin` - Administrative access
```

### API Key Authentication

```markdown
## Server-to-Server Authentication with API Keys

### Generate API Key
1. Login to developer dashboard
2. Navigate to API Keys
3. Create new key with desired scopes
4. Copy key (displayed once)
5. Store securely (never commit to version control)

### Using API Key
```bash
curl -H "X-API-Key: sk_live_abc123def456" \
  https://api.example.com/orders/api/v2/orders
```

### Key Rotation
- Rotate keys every 90 days
- Keep previous key valid for 7 days during transition
- Delete old key after transition complete
- Revoke compromised keys immediately
```

## Rate Limiting and Quotas

### Rate Limiting Strategy

```markdown
## Request Rate Limits

### Limits by Plan
| Plan | Requests/Min | Burst Size | Concurrency |
|---|---|---|---|
| Free | 100 | 10 | 5 |
| Pro | 1,000 | 100 | 20 |
| Enterprise | Custom | Custom | Custom |

### Rate Limit Headers
Every response includes rate limit information:
```
X-RateLimit-Limit: 1000         # Maximum requests per minute
X-RateLimit-Remaining: 950      # Requests remaining in current window
X-RateLimit-Reset: 1700402400   # Unix timestamp of window reset
```

### Retry-After on 429
```
HTTP/1.1 429 Too Many Requests
Retry-After: 37

{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "limits": {
    "requests_per_minute": 1000,
    "requests_made": 1000,
    "retry_after_seconds": 37
  }
}
```

### Handling Rate Limits

**Client-side strategy**:
1. Implement exponential backoff
2. Use Retry-After header value
3. Monitor X-RateLimit-Remaining
4. Batch requests when possible
5. Request higher limits if needed
```

## Client Libraries

### JavaScript/TypeScript Client

```markdown
## JavaScript SDK Usage

### Installation
```bash
npm install @example/order-api-client
```

### Basic Usage
```javascript
import { OrderClient } from '@example/order-api-client';

const client = new OrderClient({
  apiKey: 'sk_live_xyz',
  baseURL: 'https://api.example.com'
});

// Create order
const order = await client.orders.create({
  customer_id: 'CUST-123',
  items: [
    { sku: 'PROD-456', quantity: 1 }
  ]
});

// Get order
const order = await client.orders.get('ORD-20251119-001');

// List orders
const { orders, nextCursor } = await client.orders.list({
  customerId: 'CUST-123',
  status: 'CONFIRMED',
  limit: 20
});
```

### Error Handling
```javascript
try {
  const order = await client.orders.create({ /* ... */ });
} catch (error) {
  if (error.code === 'INVALID_ORDER') {
    console.error('Validation failed:', error.details);
  } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
    console.error('Rate limited, retry after:', error.retryAfter);
  } else {
    console.error('Unexpected error:', error.message);
  }
}
```

### Automatic Retries
```javascript
const client = new OrderClient({
  apiKey: 'sk_live_xyz',
  retryConfig: {
    maxAttempts: 3,
    initialDelayMs: 100,
    backoffMultiplier: 2,
    maxDelayMs: 5000
  }
});
```
```

## API Versioning Strategy

### Version Management

```markdown
## REST API Versioning

### Versioning Approach
- **URL-based versioning**: `/api/v1/`, `/api/v2/`
- **All endpoints include major version**
- **Minor versions are backward compatible**

### Version Lifecycle

```
v1.0 (2025-01-01)  ─────── GA ──────────────────────→ Deprecated
                                                    (2026-01-01)
                                                         │
                                                      EOL after
                                                      6 months
                                                     (2026-06-01)
         │
         └─────────────────────────────────────────────
v2.0 (2025-06-01)  ─────── GA ──────→ Current
         │
         └─────────────────────────────────────────────
v2.1 (2025-09-01)  ─────── GA ──────→ Current
         │
         └─────────────────────────────────────────────
v3.0 (2026-01-01)  ──→ Beta ──→ GA (expected 2026-03-01)
```

### Version Support Policy
- **Latest major version**: Full support
- **Previous major version**: 12 months support
- **Older versions**: No support, security fixes only for 6 months

### Breaking Changes Process
1. Announce in changelog 3 months before release
2. Release in new major version
3. Keep old version available for 12 months
4. Document migration guide (required reading)
5. Offer transition period with support

### Migration Example
```markdown
## Upgrading from v1 to v2

### Changed Endpoints

| v1 Endpoint | v2 Endpoint | Change |
|---|---|---|
| POST /api/v1/orders | POST /api/v2/orders | Request schema updated |
| GET /api/v1/orders/{id} | GET /api/v2/orders/{id} | Response includes new fields |

### Changed Fields

**OrderResponse.status** (v1 → v2):
- v1: String enum ("PENDING", "APPROVED", "SHIPPED")
- v2: String enum ("DRAFT", "CONFIRMED", "PROCESSING", "SHIPPED", "DELIVERED")

**Migration table**:
```
v1 Status  →  v2 Status
PENDING    →  DRAFT
APPROVED   →  CONFIRMED
SHIPPED    →  SHIPPED
```

### Client Migration Checklist
- [ ] Update import to `@example/order-api-client@^2.0.0`
- [ ] Update v1 endpoints to v2 endpoints
- [ ] Update response parsing for new status values
- [ ] Test with both v1 and v2 during transition
- [ ] Remove v1 code references after deadline
```
```

## Migration Guides

### Server-to-Client Migration

```markdown
## Migrating from REST to gRPC

### Why Migrate?
- Lower latency (10-100x faster)
- Smaller payload size (binary vs JSON)
- Bidirectional streaming
- Better tooling support

### Migration Strategy

#### Phase 1: Parallel Running (1 month)
- Deploy gRPC service alongside REST
- gRPC service reuses same business logic
- Both services write to same database
- Route new clients to gRPC, keep existing on REST

#### Phase 2: Gradual Cutover (2 months)
- Migrate 25% of traffic to gRPC (Week 1)
- Monitor error rates and performance
- Migrate 50% of traffic to gRPC (Week 2)
- Migrate 75% of traffic to gRPC (Week 3)
- Migrate remaining 25% (Week 4)

#### Phase 3: REST Deprecation (6 months)
- Announce REST deprecation date
- Provide migration guide
- Support both for 6 months
- Sunset REST API after transition period

### Validation Checklist
- [ ] gRPC service passes all integration tests
- [ ] Load test both services at 2x peak traffic
- [ ] Error rates within acceptable bounds (< 0.1%)
- [ ] Latency improvement measured and documented
- [ ] Team trained on gRPC debugging tools
- [ ] Monitoring alerts configured for gRPC service
```

## Best Practices

### Documentation Checklist

```markdown
## API Documentation Standards

### Every API Should Document

**Overview**:
- [ ] Purpose and use case
- [ ] Primary consumers/integrators
- [ ] High-level architecture diagram
- [ ] Key concepts and terminology

**Authentication**:
- [ ] Supported authentication methods
- [ ] How to obtain credentials
- [ ] Token lifetime and refresh
- [ ] Scope/permission model
- [ ] Security considerations

**Endpoints**:
- [ ] Purpose and semantics
- [ ] Request/response schemas
- [ ] Error codes and handling
- [ ] Rate limiting details
- [ ] Example requests and responses
- [ ] Curl and code examples

**Integrations**:
- [ ] External dependencies
- [ ] Callback/webhook contracts
- [ ] Async patterns if applicable

**Errors**:
- [ ] All possible error codes
- [ ] Cause and resolution for each
- [ ] Retry strategy guidance

**Versioning**:
- [ ] Current and supported versions
- [ ] Deprecation timeline
- [ ] Breaking change history

**Operations**:
- [ ] Healthcheck endpoints
- [ ] Metrics and monitoring
- [ ] Common issues and debugging
- [ ] Runbooks for on-call

### Code Examples

```javascript
// ✅ Good: Includes error handling, retry logic, validation
const response = await fetch('https://api.example.com/orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.API_KEY,
    'X-Idempotency-Key': crypto.randomUUID()
  },
  body: JSON.stringify({
    customer_id: customerId,
    items: items.map(item => ({
      sku: item.sku,
      quantity: item.quantity
    }))
  })
});

if (!response.ok) {
  const error = await response.json();
  switch (response.status) {
    case 400:
      throw new ValidationError(error.message);
    case 429:
      throw new RateLimitError(response.headers.get('Retry-After'));
    default:
      throw new APIError(error.message);
  }
}

const order = await response.json();
console.log(`Order created: ${order.order_id}`);

// ❌ Bad: No error handling, unclear purpose
fetch('https://api.example.com/orders', {
  method: 'POST',
  body: JSON.stringify({ customer_id, items })
})
  .then(r => r.json())
  .then(data => console.log(data));
```

### Documentation Tools

- **OpenAPI/Swagger**: REST API specification and interactive docs
- **Protocol Buffers**: gRPC service definitions and code generation
- **AsyncAPI**: Event/message-based API specification
- **Postman**: API testing and documentation
- **MkDocs/Confluence**: Long-form documentation
- **TypeDoc/JSDoc**: Code-generated API docs
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Author**: Platform Engineering Team
**Review Frequency**: Quarterly
**Glossary**: See Architecture Documentation Standards
