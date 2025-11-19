# Creating an OpenAPI Specification - Step-by-Step Guide

## Overview

This guide walks you through creating a production-ready OpenAPI 3.1 specification for your API.

**Time**: 30-45 minutes
**Level**: Intermediate
**Prerequisites**: Basic understanding of REST APIs

---

## Step 1: Set Up the Basic Structure

Create a file named `openapi.yaml`:

```yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0
  description: API description goes here
servers:
  - url: https://api.example.com/v1
    description: Production
paths: {}
components: {}
```

**What this does**:
- `openapi`: Declares spec version
- `info`: API metadata
- `servers`: API base URLs
- `paths`: Endpoints (we'll add these next)
- `components`: Reusable definitions

---

## Step 2: Add API Metadata

Enhance the `info` section:

```yaml
info:
  title: Payment Processing API
  version: 1.0.0
  description: |
    Process payments, manage subscriptions, and handle refunds.

    ## Authentication
    All requests require an API key:
    ```
    Authorization: Bearer YOUR_API_KEY
    ```

    ## Rate Limits
    - Standard: 100 requests/second
    - Premium: 1000 requests/second

  contact:
    name: API Support
    email: api-support@example.com
    url: https://example.com/support

  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
```

**Why this matters**: This information appears prominently in generated documentation.

---

## Step 3: Define Reusable Schemas

Add schemas in `components`:

```yaml
components:
  schemas:
    Payment:
      type: object
      required:
        - id
        - amount
        - currency
        - status
      properties:
        id:
          type: string
          description: Unique payment identifier
          example: pmt_1234567890
          pattern: ^pmt_[a-zA-Z0-9]+$

        amount:
          type: integer
          description: Amount in smallest currency unit (cents)
          minimum: 50
          example: 1000

        currency:
          type: string
          description: Three-letter ISO currency code
          pattern: ^[a-z]{3}$
          example: usd

        status:
          type: string
          enum:
            - pending
            - processing
            - succeeded
            - failed
            - canceled
          description: Payment status
          example: succeeded

        created_at:
          type: string
          format: date-time
          description: ISO 8601 timestamp
          example: "2025-11-19T10:30:00Z"
          readOnly: true

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: validation_error
            message:
              type: string
              example: Invalid request parameters
```

**Best practices**:
- Mark required fields
- Provide examples
- Use `format` for common types
- Set constraints (min/max, pattern)
- Use `readOnly` for non-writable fields

---

## Step 4: Add Your First Endpoint

Add a GET endpoint:

```yaml
paths:
  /payments/{id}:
    get:
      summary: Get a payment
      description: Retrieves the details of a payment
      operationId: getPayment
      tags:
        - Payments
      parameters:
        - name: id
          in: path
          required: true
          description: Payment identifier
          schema:
            type: string
          example: pmt_1234567890

      responses:
        '200':
          description: Payment retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Payment'
              example:
                id: pmt_1234567890
                amount: 1000
                currency: usd
                status: succeeded
                created_at: "2025-11-19T10:30:00Z"

        '404':
          description: Payment not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

**Key elements**:
- `operationId`: Used for SDK generation
- `tags`: Group related endpoints
- `parameters`: Path/query/header parameters
- `responses`: All possible responses

---

## Step 5: Add a POST Endpoint

```yaml
paths:
  /payments:
    post:
      summary: Create a payment
      description: Creates a new payment intent
      operationId: createPayment
      tags:
        - Payments

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
                  minimum: 50
                  example: 1000

                currency:
                  type: string
                  pattern: ^[a-z]{3}$
                  example: usd

                description:
                  type: string
                  maxLength: 500
                  example: Order #12345

            examples:
              basic:
                summary: Basic payment
                value:
                  amount: 1000
                  currency: usd

              with_description:
                summary: Payment with description
                value:
                  amount: 2500
                  currency: usd
                  description: Premium subscription

      responses:
        '201':
          description: Payment created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Payment'

        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

**requestBody tips**:
- Always mark if required
- Provide multiple examples
- Show simple and complex cases

---

## Step 6: Add Authentication

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: API Key
      description: |
        Use your API key from the dashboard.
        ```
        Authorization: Bearer YOUR_API_KEY
        ```

security:
  - bearerAuth: []  # Apply to all endpoints
```

**Per-endpoint security override**:

```yaml
paths:
  /health:
    get:
      security: []  # Public endpoint
```

---

## Step 7: Add Common Responses

Define reusable responses:

```yaml
components:
  responses:
    Unauthorized:
      description: Unauthorized - Invalid or missing API key
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error:
              code: unauthorized
              message: Invalid API key

    RateLimitExceeded:
      description: Too many requests
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds to wait before retrying
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

**Use in endpoints**:

```yaml
responses:
  '401':
    $ref: '#/components/responses/Unauthorized'
  '429':
    $ref: '#/components/responses/RateLimitExceeded'
```

---

## Step 8: Validate Your Spec

### Using Swagger CLI

```bash
# Install
npm install -g @apidevtools/swagger-cli

# Validate
swagger-cli validate openapi.yaml
```

### Using Spectral

```bash
# Install
npm install -g @stoplight/spectral-cli

# Lint
spectral lint openapi.yaml
```

### Online Validators

- Swagger Editor: https://editor.swagger.io
- Redocly: https://redocly.com/docs/cli/

---

## Step 9: Generate Documentation

### Using Redoc

```bash
npm install -g redoc-cli
redoc-cli bundle openapi.yaml -o docs.html
```

### Using Swagger UI

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: 'openapi.yaml',
      dom_id: '#swagger-ui'
    });
  </script>
</body>
</html>
```

---

## Step 10: Keep It Up to Date

### Automation

```yaml
# .github/workflows/validate-openapi.yml
name: Validate OpenAPI

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate OpenAPI spec
        run: |
          npm install -g @apidevtools/swagger-cli
          swagger-cli validate openapi.yaml

      - name: Lint with Spectral
        run: |
          npm install -g @stoplight/spectral-cli
          spectral lint openapi.yaml
```

### Documentation from Code

Some frameworks can generate OpenAPI from code:

**FastAPI (Python)**:
```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/payments/{id}")
def get_payment(id: str):
    """Get a payment by ID"""
    return {"id": id}

# Automatic OpenAPI at /docs
```

**NestJS (TypeScript)**:
```typescript
import { ApiProperty } from '@nestjs/swagger';

export class CreatePaymentDto {
  @ApiProperty({ example: 1000, minimum: 50 })
  amount: number;

  @ApiProperty({ example: 'usd' })
  currency: string;
}
```

---

## Best Practices Checklist

- [ ] Include comprehensive `info` section
- [ ] Define all schemas in `components`
- [ ] Use `$ref` to reuse schemas
- [ ] Document all parameters
- [ ] Provide examples for all schemas
- [ ] Document all possible responses
- [ ] Include error responses
- [ ] Add security schemes
- [ ] Use meaningful `operationId`s
- [ ] Group endpoints with `tags`
- [ ] Validate spec regularly
- [ ] Auto-generate docs from spec
- [ ] Keep spec in version control
- [ ] Update spec with code changes

---

## Troubleshooting

### Common Errors

**"Schema not found"**:
- Check `$ref` path (should be `#/components/schemas/SchemaName`)
- Ensure schema is defined in `components.schemas`

**"Invalid reference"**:
- YAML indentation issue
- Missing `:` after property names

**"Validation failed"**:
- Run `swagger-cli validate` for details
- Check required fields are marked
- Verify enum values match examples

---

## Next Steps

- [Add pagination](./adding-pagination.md)
- [Document webhooks](./documenting-webhooks.md)
- [Generate SDKs](./generating-sdks.md)
- [API contract testing](./contract-testing.md)

---

**Complete Example**: See `src/openapi-complete-example.yaml` in this directory.
