# OpenAPI Best Practices

## Overview

OpenAPI (formerly Swagger) is the industry-standard specification for describing RESTful APIs. This guide provides best practices for creating high-quality OpenAPI specifications.

**OpenAPI Version**: 3.1 (latest)
**Goal**: Machine-readable API specifications that generate excellent documentation and enable tooling

---

## Why OpenAPI?

**Benefits**:
- **Generate Documentation**: Redoc, Swagger UI, Stoplight
- **Generate SDKs**: Create client libraries in multiple languages
- **API Mocking**: Create mock servers for testing
- **Contract Testing**: Validate API responses match specification
- **Type Safety**: Generate TypeScript types, Python types from spec
- **IDE Integration**: Autocomplete and validation in editors

---

## OpenAPI 3.1 Structure

```yaml
openapi: 3.1.0  # OpenAPI version
info:           # API metadata
paths:          # API endpoints
components:     # Reusable schemas, responses, parameters
security:       # Security schemes
servers:        # API servers (production, sandbox)
tags:           # Endpoint grouping
```

---

## Best Practices

### 1. Provide Comprehensive Metadata

```yaml
openapi: 3.1.0
info:
  title: Payments API
  version: 1.0.0
  description: |
    The Payments API allows you to process payments, manage subscriptions,
    and handle refunds.

    ## Authentication
    All requests require an API key in the Authorization header:
    ```
    Authorization: Bearer YOUR_API_KEY
    ```

    ## Rate Limits
    - Standard: 100 requests/second
    - Premium: 1000 requests/second

    ## Support
    - Email: api-support@example.com
    - Docs: https://docs.example.com
    - Status: https://status.example.com

  contact:
    name: API Support
    email: api-support@example.com
    url: https://example.com/support

  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

  termsOfService: https://example.com/terms

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://sandbox.example.com/v1
    description: Sandbox (test mode)
```

**Why this matters**:
- Documentation tools display this information prominently
- Developers get context before reading endpoints
- Contact information helps when issues arise

---

### 2. Use Descriptive Operation IDs

```yaml
paths:
  /users/{userId}:
    get:
      operationId: getUser  # ✅ Good - clear, concise
      # operationId: get_users_userId  # ❌ Bad - auto-generated
```

**Benefits**:
- SDK code generation uses operation IDs for method names
- Better generated code: `client.getUser()` vs `client.get_users_userId()`

---

### 3. Provide Rich Descriptions

```yaml
paths:
  /payments:
    post:
      summary: Create a payment
      description: |
        Creates a new payment intent for collecting payment from a customer.

        ## Use cases
        - One-time payments
        - Saving payment method for future use
        - Collecting payment immediately

        ## Important notes
        - Amount must be in smallest currency unit (cents for USD)
        - Minimum amount is 50 (e.g., $0.50 USD)
        - Payments expire after 24 hours if not confirmed

        ## Related endpoints
        - [Confirm payment](#/operations/confirmPayment)
        - [Cancel payment](#/operations/cancelPayment)

      tags:
        - Payments
```

**Why descriptions matter**:
- Summary appears in navigation/search
- Description provides context and guidance
- Links to related endpoints improve discoverability

---

### 4. Define Comprehensive Schemas

**Use reusable schemas**:

```yaml
components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
      properties:
        id:
          type: string
          description: Unique user identifier
          example: usr_1234567890
          pattern: ^usr_[a-zA-Z0-9]+$

        email:
          type: string
          format: email
          description: User's email address
          example: alice@example.com
          maxLength: 255

        name:
          type: string
          description: User's full name
          example: Alice Johnson
          minLength: 1
          maxLength: 100

        role:
          type: string
          enum:
            - admin
            - member
            - guest
          default: member
          description: User's role in the organization

        created_at:
          type: string
          format: date-time
          description: ISO 8601 timestamp of account creation
          example: "2025-11-19T10:30:00Z"
          readOnly: true  # Not accepted in requests

        metadata:
          type: object
          description: Key-value pairs for storing additional information
          additionalProperties:
            type: string
          example:
            department: Engineering
            employee_id: "12345"
```

**Schema best practices**:
- ✅ Mark required fields
- ✅ Provide examples for all properties
- ✅ Set appropriate constraints (min/max, pattern)
- ✅ Use `format` for common types (email, date-time, uri)
- ✅ Use `readOnly` for fields not accepted in requests
- ✅ Use `writeOnly` for sensitive fields (passwords)
- ✅ Document enums with descriptions

---

### 5. Document Request Bodies Thoroughly

```yaml
paths:
  /payments:
    post:
      requestBody:
        required: true
        description: Payment details
        content:
          application/json:
            schema:
              type: object
              required:
                - amount
                - currency
              properties:
                amount:
                  type: integer
                  description: |
                    Amount in smallest currency unit.
                    For example, to charge $10.00 USD, use 1000.
                  minimum: 50
                  example: 1000

                currency:
                  type: string
                  description: Three-letter ISO currency code
                  pattern: ^[a-z]{3}$
                  example: usd

                description:
                  type: string
                  description: Payment description (appears on statement)
                  maxLength: 500
                  example: Order #12345

                metadata:
                  type: object
                  description: Additional structured data
                  additionalProperties:
                    type: string

            examples:
              basic:
                summary: Basic payment
                value:
                  amount: 1000
                  currency: usd

              with_metadata:
                summary: Payment with metadata
                value:
                  amount: 2500
                  currency: usd
                  description: Premium subscription
                  metadata:
                    customer_id: cus_123
                    order_id: ord_456
```

**Why multiple examples help**:
- Shows simple and complex use cases
- Generated documentation displays all examples
- Developers can copy-paste working examples

---

### 6. Document All Response Scenarios

```yaml
paths:
  /payments:
    post:
      responses:
        '201':
          description: Payment created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Payment'
              example:
                id: pmt_1234567890
                amount: 1000
                currency: usd
                status: pending
                created_at: "2025-11-19T10:30:00Z"

        '400':
          description: Invalid request parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                amount_too_small:
                  summary: Amount below minimum
                  value:
                    error:
                      code: amount_too_small
                      message: Amount must be at least 50

                invalid_currency:
                  summary: Invalid currency code
                  value:
                    error:
                      code: invalid_currency
                      message: Currency must be a 3-letter ISO code

        '401':
          $ref: '#/components/responses/Unauthorized'

        '429':
          $ref: '#/components/responses/RateLimitExceeded'
```

**Response best practices**:
- ✅ Document all HTTP status codes endpoint can return
- ✅ Provide example response for each status
- ✅ Show different error scenarios
- ✅ Reuse common responses (401, 429, 500) via `$ref`

---

### 7. Use Tags for Organization

```yaml
tags:
  - name: Payments
    description: |
      Create and manage payments.

      Payment lifecycle: create → confirm → succeeded/failed

  - name: Users
    description: User account management

  - name: Webhooks
    description: Configure webhook endpoints to receive events

paths:
  /payments:
    post:
      tags:
        - Payments
      # ...

  /users:
    get:
      tags:
        - Users
      # ...
```

**Benefits**:
- Documentation is organized into logical sections
- Easier navigation in Swagger UI/Redoc
- Helps developers find related endpoints

---

### 8. Define Security Schemes

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: |
        Use your API key from the dashboard.
        Include it in the Authorization header:
        ```
        Authorization: Bearer YOUR_API_KEY
        ```

    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/oauth/authorize
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            read:payments: Read payment data
            write:payments: Create and modify payments
            read:users: Read user data

security:
  - bearerAuth: []  # Apply to all endpoints by default

paths:
  /public/health:
    get:
      security: []  # Override for public endpoint

  /admin/users:
    get:
      security:
        - oauth2: [read:users, admin]  # Requires specific OAuth scopes
```

---

### 9. Document Parameters Comprehensively

```yaml
paths:
  /payments:
    get:
      summary: List payments
      parameters:
        - name: limit
          in: query
          description: Number of results to return (1-100)
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
          example: 20

        - name: starting_after
          in: query
          description: |
            Cursor for pagination. Use the `id` of the last item from
            the previous page.
          required: false
          schema:
            type: string
          example: pmt_1234567890

        - name: status
          in: query
          description: Filter by payment status
          required: false
          schema:
            type: string
            enum:
              - pending
              - processing
              - succeeded
              - failed
              - canceled
          example: succeeded

        - name: created_after
          in: query
          description: Return only payments created after this timestamp
          required: false
          schema:
            type: string
            format: date-time
          example: "2025-01-01T00:00:00Z"
```

---

### 10. Include Webhooks (OpenAPI 3.1+)

```yaml
webhooks:
  payment.succeeded:
    post:
      summary: Payment succeeded
      description: Triggered when a payment is successfully completed
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                event:
                  type: string
                  example: payment.succeeded
                data:
                  $ref: '#/components/schemas/Payment'
                created_at:
                  type: string
                  format: date-time

      responses:
        '200':
          description: Webhook received successfully
```

---

## Common Patterns

### Error Response Schema

```yaml
components:
  schemas:
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Machine-readable error code
              example: validation_error

            message:
              type: string
              description: Human-readable error message
              example: Invalid email format

            details:
              type: object
              description: Additional error context
              additionalProperties: true
              example:
                field: email
                value: not-an-email

            request_id:
              type: string
              description: Request ID for support
              example: req_1234567890
```

### Pagination

```yaml
components:
  schemas:
    PaginatedResponse:
      type: object
      properties:
        data:
          type: array
          items:
            type: object
        has_more:
          type: boolean
          description: Whether more results exist
        total_count:
          type: integer
          description: Total number of results

    parameters:
      Limit:
        name: limit
        in: query
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 10

      StartingAfter:
        name: starting_after
        in: query
        description: Cursor for pagination
        schema:
          type: string
```

---

## Validation and Testing

### Validate Your Spec

**Tools**:
```bash
# Swagger CLI
swagger-cli validate openapi.yaml

# Spectral (advanced linting)
spectral lint openapi.yaml

# Redocly CLI
redocly lint openapi.yaml
```

### Generate Documentation

```bash
# Redoc
redoc-cli bundle openapi.yaml -o docs.html

# Swagger UI
# Use online editor: https://editor.swagger.io
```

### Contract Testing

```bash
# Dredd - test API matches OpenAPI spec
dredd openapi.yaml https://api.example.com

# Prism - mock server from OpenAPI
prism mock openapi.yaml
```

---

## Tools and Ecosystem

### Editors

- **Stoplight Studio** - Visual OpenAPI editor
- **Swagger Editor** - Online/self-hosted editor
- **VS Code** - OpenAPI extensions (OpenAPI Editor, Swagger Viewer)

### Documentation Generators

- **Redoc** - Beautiful, responsive docs
- **Swagger UI** - Interactive, try-it-now interface
- **Stoplight Elements** - Embeddable API docs
- **RapiDoc** - Fast, customizable docs

### Code Generators

- **OpenAPI Generator** - Client/server code in 50+ languages
- **Swagger Codegen** - Legacy code generation
- **openapi-typescript** - TypeScript types from OpenAPI

### Testing

- **Dredd** - HTTP API testing based on OpenAPI
- **Prism** - Mock server and proxy
- **Spectral** - OpenAPI linting and style guide enforcement

---

## Complete Example

```yaml
openapi: 3.1.0

info:
  title: Example API
  version: 1.0.0
  description: Comprehensive example API
  contact:
    email: support@example.com

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://sandbox.example.com/v1
    description: Sandbox

security:
  - bearerAuth: []

tags:
  - name: Users
    description: User management

paths:
  /users:
    get:
      operationId: listUsers
      summary: List users
      tags: [Users]
      parameters:
        - $ref: '#/components/parameters/Limit'
        - $ref: '#/components/parameters/Offset'
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  total:
                    type: integer
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      operationId: createUser
      summary: Create a user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, name]
              properties:
                email:
                  type: string
                  format: email
                name:
                  type: string
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer

  parameters:
    Limit:
      name: limit
      in: query
      schema:
        type: integer
        default: 10
        minimum: 1
        maximum: 100

    Offset:
      name: offset
      in: query
      schema:
        type: integer
        default: 0
        minimum: 0

  schemas:
    User:
      type: object
      required: [id, email, name]
      properties:
        id:
          type: string
          example: usr_123
        email:
          type: string
          format: email
          example: alice@example.com
        name:
          type: string
          example: Alice Johnson
        created_at:
          type: string
          format: date-time
          readOnly: true

  responses:
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    BadRequest:
      description: Bad request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**OpenAPI Version**: 3.1
**Tools**: Stoplight, Redoc, Swagger UI, OpenAPI Generator
