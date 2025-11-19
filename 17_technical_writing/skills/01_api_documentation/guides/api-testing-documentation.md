# API Testing Documentation - Postman Collections & Contract Testing

## Overview

This comprehensive guide covers documenting API tests, creating Postman collections, implementing contract testing, and establishing testing best practices for APIs.

**Time**: 40-50 minutes
**Level**: Advanced
**Prerequisites**: Understanding of APIs, REST principles, testing concepts

---

## What Is API Testing Documentation?

API testing documentation includes:
- Test case specifications
- Postman collection examples
- API contract definitions
- Contract testing implementations
- CI/CD integration guides
- Test data management

**Benefits**:
- Executable documentation
- Automated testing reduces bugs
- Clear API contract definitions
- Early compatibility detection
- Regression prevention

---

## Step 1: Plan Your Testing Strategy

Define your testing approach before creating documentation:

### Testing Pyramid

```
        /\
       /  \  End-to-End Tests (UI, flows)
      /----\
     /      \  Integration Tests (multiple services)
    /--------\
   /          \  Unit Tests (individual functions)
  /____________\

API Testing Levels:
1. Unit Tests: Validate individual functions
2. Integration Tests: Test API with dependencies
3. Contract Tests: Verify API contracts
4. End-to-End Tests: Full user flows
5. Performance Tests: Load and stress testing
```

### Test Categories

```yaml
Functional Testing:
  - Happy path: Valid requests work correctly
  - Edge cases: Boundary conditions
  - Negative cases: Invalid inputs rejected
  - Error handling: Proper error responses

Non-Functional Testing:
  - Performance: Response times acceptable
  - Load testing: Handle concurrent requests
  - Security testing: Authentication/authorization
  - Reliability: Retry logic, fault tolerance

Data Validation:
  - Request validation
  - Response validation
  - Schema validation
  - Data type checking
```

---

## Step 2: Create Postman Collections

### Installation & Setup

Install Postman:
```bash
# macOS
brew install --cask postman

# Or download from https://www.postman.com/downloads/
```

### Basic Collection Structure

**Collection JSON** (`payment-api.postman_collection.json`):

```json
{
  "info": {
    "_postman_id": "12345678-1234-1234-1234-123456789012",
    "name": "Payment API",
    "description": "Complete Payment API test collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Payments",
      "description": "Payment operations",
      "item": [
        {
          "name": "Create Payment",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 201', function() {",
                  "  pm.response.to.have.status(201);",
                  "});",
                  "",
                  "pm.test('Response has payment ID', function() {",
                  "  var jsonData = pm.response.json();",
                  "  pm.expect(jsonData.id).to.be.a('string');",
                  "  pm.expect(jsonData.id).to.match(/^pmt_/);",
                  "});",
                  "",
                  "// Save payment ID for next request",
                  "var jsonData = pm.response.json();",
                  "pm.collectionVariables.set('paymentId', jsonData.id);"
                ]
              }
            }
          ],
          "request": {
            "auth": {
              "type": "bearer",
              "bearer": [
                {
                  "key": "token",
                  "value": "{{apiKey}}",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"amount\": 1000,\n  \"currency\": \"usd\",\n  \"description\": \"Test payment\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/payments",
              "host": ["{{baseUrl}}"],
              "path": ["payments"]
            },
            "description": "Create a new payment with amount and currency"
          },
          "response": [
            {
              "name": "201 Created",
              "originalRequest": {
                "method": "POST",
                "header": [],
                "body": {
                  "mode": "raw",
                  "raw": "{\n  \"amount\": 1000,\n  \"currency\": \"usd\"\n}"
                },
                "url": {
                  "raw": "https://api.example.com/v1/payments",
                  "protocol": "https",
                  "host": ["api", "example", "com"],
                  "path": ["v1", "payments"]
                }
              },
              "status": "Created",
              "code": 201,
              "header": [
                {
                  "key": "Content-Type",
                  "value": "application/json"
                }
              ],
              "body": "{\n  \"id\": \"pmt_1234567890\",\n  \"amount\": 1000,\n  \"currency\": \"usd\",\n  \"status\": \"succeeded\",\n  \"created_at\": \"2025-11-19T10:30:00Z\"\n}"
            }
          ]
        },
        {
          "name": "Get Payment",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', function() {",
                  "  pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Response contains expected fields', function() {",
                  "  var jsonData = pm.response.json();",
                  "  pm.expect(jsonData).to.have.property('id');",
                  "  pm.expect(jsonData).to.have.property('amount');",
                  "  pm.expect(jsonData).to.have.property('currency');",
                  "  pm.expect(jsonData).to.have.property('status');",
                  "});",
                  "",
                  "pm.test('Amount is a positive integer', function() {",
                  "  var jsonData = pm.response.json();",
                  "  pm.expect(jsonData.amount).to.be.above(0);",
                  "  pm.expect(Number.isInteger(jsonData.amount)).to.be.true;",
                  "});",
                  "",
                  "pm.test('Status is valid', function() {",
                  "  var jsonData = pm.response.json();",
                  "  var validStatuses = ['pending', 'processing', 'succeeded', 'failed'];",
                  "  pm.expect(validStatuses).to.include(jsonData.status);",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "auth": {
              "type": "bearer",
              "bearer": [
                {
                  "key": "token",
                  "value": "{{apiKey}}",
                  "type": "string"
                }
              ]
            },
            "method": "GET",
            "url": {
              "raw": "{{baseUrl}}/payments/{{paymentId}}",
              "host": ["{{baseUrl}}"],
              "path": ["payments", "{{paymentId}}"]
            },
            "description": "Retrieve a specific payment by ID"
          },
          "response": [
            {
              "name": "200 OK",
              "status": "OK",
              "code": 200,
              "body": "{\n  \"id\": \"pmt_1234567890\",\n  \"amount\": 1000,\n  \"currency\": \"usd\",\n  \"status\": \"succeeded\",\n  \"created_at\": \"2025-11-19T10:30:00Z\"\n}"
            }
          ]
        }
      ]
    }
  ],
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{apiKey}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://api.example.com/v1",
      "type": "string"
    },
    {
      "key": "apiKey",
      "value": "sk_live_",
      "type": "string"
    },
    {
      "key": "paymentId",
      "value": "",
      "type": "string"
    }
  ]
}
```

### Pre-request Scripts

Add setup before each request:

```javascript
// Pre-request Script: Generate unique payment description

// Generate timestamp
const timestamp = new Date().toISOString();

// Create unique ID for this test run
const testId = pm.environment.get('testId') || Date.now().toString();

// Set variables
pm.environment.set('testId', testId);
pm.environment.set('timestamp', timestamp);
pm.environment.set('paymentDescription', `Test payment ${testId}`);

// Log for debugging
console.log(`Test ID: ${testId}`);
console.log(`Timestamp: ${timestamp}`);
```

### Test Scripts

Add assertions after each request:

```javascript
// Test Script: Comprehensive response validation

// 1. Status code tests
pm.test('Status code is 201 Created', function () {
    pm.response.to.have.status(201);
});

// 2. Response time test
pm.test('Response time is less than 1000ms', function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

// 3. Headers test
pm.test('Content-Type header is application/json', function () {
    pm.response.to.have.header('Content-Type');
    pm.expect(pm.response.headers.get('Content-Type')).to.include('application/json');
});

// 4. Body parsing test
pm.test('Response body is valid JSON', function () {
    pm.response.to.be.json;
});

// 5. Schema validation
pm.test('Response schema is valid', function () {
    var jsonData = pm.response.json();

    // Check required fields
    pm.expect(jsonData).to.have.all.keys('id', 'amount', 'currency', 'status', 'created_at');

    // Check field types
    pm.expect(jsonData.id).to.be.a('string');
    pm.expect(jsonData.amount).to.be.a('number');
    pm.expect(jsonData.currency).to.be.a('string');
    pm.expect(jsonData.status).to.be.a('string');
    pm.expect(jsonData.created_at).to.be.a('string');
});

// 6. Business logic tests
pm.test('Payment amount matches request', function () {
    var requestBody = pm.request.body.raw;
    var responseData = pm.response.json();

    var requestAmount = JSON.parse(requestBody).amount;
    pm.expect(responseData.amount).to.equal(requestAmount);
});

// 7. Boundary value tests
pm.test('Payment amount is within valid range', function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.amount).to.be.above(49); // Minimum $0.50
    pm.expect(jsonData.amount).to.be.below(999999999); // Maximum
});

// 8. Error handling tests
if (pm.response.code === 400) {
    pm.test('Error response has proper structure', function () {
        var jsonData = pm.response.json();
        pm.expect(jsonData).to.have.property('error');
        pm.expect(jsonData.error).to.have.all.keys('code', 'message');
    });
}

// 9. Save data for next request
if (pm.response.code === 201) {
    var jsonData = pm.response.json();
    pm.environment.set('paymentId', jsonData.id);
    pm.environment.set('paymentStatus', jsonData.status);
}

// 10. Custom assertions
pm.test('Payment ID follows naming convention', function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.id).to.match(/^pmt_[a-zA-Z0-9]+$/);
});
```

---

## Step 3: Test Data & Environments

### Environment Setup

**Development Environment** (`development.postman_environment.json`):

```json
{
  "id": "env-dev-123",
  "name": "Development",
  "values": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "sk_test_dev123",
      "enabled": true
    },
    {
      "key": "timeout",
      "value": "5000",
      "enabled": true
    }
  ]
}
```

**Testing Environment** (`testing.postman_environment.json`):

```json
{
  "id": "env-test-123",
  "name": "Testing",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.staging.example.com",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "sk_test_staging456",
      "enabled": true
    },
    {
      "key": "timeout",
      "value": "10000",
      "enabled": true
    }
  ]
}
```

**Production Environment** (`production.postman_environment.json`):

```json
{
  "id": "env-prod-123",
  "name": "Production",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.example.com/v1",
      "enabled": true
    },
    {
      "key": "apiKey",
      "value": "{{PROD_API_KEY}}",
      "enabled": true
    },
    {
      "key": "timeout",
      "value": "30000",
      "enabled": true
    },
    {
      "key": "dryRun",
      "value": "true",
      "enabled": true
    }
  ]
}
```

### Test Data Sets

**Valid Test Cases** (`test-data-valid.json`):

```json
{
  "validPayments": [
    {
      "name": "Minimum amount",
      "amount": 50,
      "currency": "usd",
      "description": "Minimum valid payment"
    },
    {
      "name": "Standard amount",
      "amount": 1000,
      "currency": "usd",
      "description": "Standard $10 payment"
    },
    {
      "name": "Large amount",
      "amount": 999999999,
      "currency": "usd",
      "description": "Maximum valid payment"
    },
    {
      "name": "Different currency",
      "amount": 5000,
      "currency": "eur",
      "description": "Payment in EUR"
    },
    {
      "name": "With special characters",
      "amount": 2500,
      "currency": "usd",
      "description": "Order #123 - Special chars: !@#$%"
    }
  ]
}
```

**Invalid Test Cases** (`test-data-invalid.json`):

```json
{
  "invalidPayments": [
    {
      "name": "Missing amount",
      "data": {
        "currency": "usd"
      },
      "expectedError": "validation_error"
    },
    {
      "name": "Missing currency",
      "data": {
        "amount": 1000
      },
      "expectedError": "validation_error"
    },
    {
      "name": "Negative amount",
      "data": {
        "amount": -1000,
        "currency": "usd"
      },
      "expectedError": "validation_error"
    },
    {
      "name": "Zero amount",
      "data": {
        "amount": 0,
        "currency": "usd"
      },
      "expectedError": "validation_error"
    },
    {
      "name": "Invalid currency",
      "data": {
        "amount": 1000,
        "currency": "invalid"
      },
      "expectedError": "validation_error"
    },
    {
      "name": "Non-numeric amount",
      "data": {
        "amount": "abc",
        "currency": "usd"
      },
      "expectedError": "validation_error"
    }
  ]
}
```

---

## Step 4: Contract Testing

### What Is Contract Testing?

Contract testing verifies that consumer and provider services conform to an agreed contract (API specification).

### Pact Testing Setup

Install Pact:

```bash
# Python
pip install pact

# JavaScript
npm install --save-dev @pact-foundation/pact

# Java
// In pom.xml
<dependency>
  <groupId>au.com.dius</groupId>
  <artifactId>pact-jvm-consumer-junit</artifactId>
  <version>4.3.0</version>
</dependency>
```

### Python Contract Test

**test_payment_contract.py**:

```python
"""
Contract tests for Payment API consumer
Verifies that the consumer expectations match the provider API
"""

import json
from pact import Consumer, Provider

pact = Consumer("PaymentSDK").has_state(
    "a payment exists",
    upon_receiving="a request for payment details"
).with_request(
    "GET",
    "/payments/pmt_123"
).will_respond_with(200, body={
    "id": "pmt_123",
    "amount": 1000,
    "currency": "usd",
    "status": "succeeded",
    "created_at": "2025-11-19T10:30:00Z"
})

provider = Provider("PaymentAPI")

def test_get_payment():
    """Test that we can retrieve a payment"""
    with pact.get_url() as url:
        # Make request to pact mock server
        import requests

        response = requests.get(f"{url}/payments/pmt_123")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == "pmt_123"
        assert data["amount"] == 1000
        assert data["currency"] == "usd"
        assert data["status"] == "succeeded"

        # Verify contract is satisfied
        assert pact.verify() is not None


def test_create_payment():
    """Test that we can create a payment"""
    pact = Consumer("PaymentSDK").has_state(
        "no payments exist"
    ).upon_receiving(
        "a request to create a payment"
    ).with_request(
        "POST",
        "/payments",
        body={
            "amount": 1000,
            "currency": "usd",
            "description": "Test payment"
        }
    ).will_respond_with(201, body={
        "id": "pmt_123",
        "amount": 1000,
        "currency": "usd",
        "status": "pending",
        "created_at": "2025-11-19T10:30:00Z"
    })

    with pact.get_url() as url:
        import requests

        response = requests.post(
            f"{url}/payments",
            json={
                "amount": 1000,
                "currency": "usd",
                "description": "Test payment"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["id"] == "pmt_123"
        assert data["status"] == "pending"
```

### JavaScript Contract Test

**test-payment-contract.js**:

```javascript
/**
 * Contract tests for Payment API consumer
 * Uses Pact to verify consumer-provider compatibility
 */

const { Pact } = require('@pact-foundation/pact');
const axios = require('axios');

describe('Payment API Contract', () => {
  const provider = new Pact({
    consumer: 'PaymentSDK',
    provider: 'PaymentAPI',
    port: 8000,
  });

  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  describe('GET /payments/:id', () => {
    it('should return payment details', async () => {
      // Set up contract expectation
      await provider.addInteraction({
        state: 'payment exists',
        uponReceiving: 'a request for payment details',
        withRequest: {
          method: 'GET',
          path: '/payments/pmt_123',
        },
        willRespondWith: {
          status: 200,
          body: {
            id: 'pmt_123',
            amount: 1000,
            currency: 'usd',
            status: 'succeeded',
            created_at: '2025-11-19T10:30:00Z',
          },
        },
      });

      // Make request to pact mock server
      const response = await axios.get(
        `${provider.mockService.baseUrl}/payments/pmt_123`
      );

      // Assertions
      expect(response.status).toBe(200);
      expect(response.data).toEqual({
        id: 'pmt_123',
        amount: 1000,
        currency: 'usd',
        status: 'succeeded',
        created_at: '2025-11-19T10:30:00Z',
      });
    });
  });

  describe('POST /payments', () => {
    it('should create a payment', async () => {
      // Set up contract expectation
      await provider.addInteraction({
        state: 'no payments exist',
        uponReceiving: 'a request to create a payment',
        withRequest: {
          method: 'POST',
          path: '/payments',
          body: {
            amount: 1000,
            currency: 'usd',
            description: 'Test payment',
          },
        },
        willRespondWith: {
          status: 201,
          body: {
            id: 'pmt_123',
            amount: 1000,
            currency: 'usd',
            status: 'pending',
            created_at: '2025-11-19T10:30:00Z',
          },
        },
      });

      // Make request
      const response = await axios.post(
        `${provider.mockService.baseUrl}/payments`,
        {
          amount: 1000,
          currency: 'usd',
          description: 'Test payment',
        }
      );

      // Assertions
      expect(response.status).toBe(201);
      expect(response.data.id).toBe('pmt_123');
      expect(response.data.status).toBe('pending');
    });
  });

  describe('Error Cases', () => {
    it('should return 404 for non-existent payment', async () => {
      // Set up contract expectation
      await provider.addInteraction({
        state: 'payment does not exist',
        uponReceiving: 'a request for non-existent payment',
        withRequest: {
          method: 'GET',
          path: '/payments/pmt_invalid',
        },
        willRespondWith: {
          status: 404,
          body: {
            error: {
              code: 'not_found',
              message: 'Payment not found',
            },
          },
        },
      });

      try {
        await axios.get(
          `${provider.mockService.baseUrl}/payments/pmt_invalid`
        );
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.error.code).toBe('not_found');
      }
    });

    it('should return 400 for invalid request', async () => {
      // Set up contract expectation
      await provider.addInteraction({
        state: 'no payments exist',
        uponReceiving: 'a request with missing amount',
        withRequest: {
          method: 'POST',
          path: '/payments',
          body: {
            currency: 'usd',
          },
        },
        willRespondWith: {
          status: 400,
          body: {
            error: {
              code: 'validation_error',
              message: 'Missing required field: amount',
            },
          },
        },
      });

      try {
        await axios.post(
          `${provider.mockService.baseUrl}/payments`,
          {
            currency: 'usd',
          }
        );
      } catch (error) {
        expect(error.response.status).toBe(400);
        expect(error.response.data.error.code).toBe('validation_error');
      }
    });
  });
});
```

---

## Step 5: API Schema Validation

### JSON Schema Validation

Validate responses against JSON schemas:

**Payment Schema** (`schemas/payment.schema.json`):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Payment",
  "description": "A payment object",
  "type": "object",
  "required": ["id", "amount", "currency", "status", "created_at"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^pmt_[a-zA-Z0-9]+$",
      "description": "Unique payment identifier"
    },
    "amount": {
      "type": "integer",
      "minimum": 50,
      "maximum": 999999999,
      "description": "Amount in cents"
    },
    "currency": {
      "type": "string",
      "pattern": "^[a-z]{3}$",
      "description": "ISO currency code"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "processing", "succeeded", "failed"],
      "description": "Payment status"
    },
    "description": {
      "type": ["string", "null"],
      "maxLength": 500,
      "description": "Payment description"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 creation timestamp"
    }
  },
  "additionalProperties": false
}
```

### Schema Validation Test

**test_payment_schema.py**:

```python
"""
Schema validation tests for Payment API responses
"""

import json
import jsonschema
from jsonschema import validate

def test_payment_schema_validation():
    """Validate response against schema"""

    # Load schema
    with open('schemas/payment.schema.json', 'r') as f:
        schema = json.load(f)

    # Test valid payment
    valid_payment = {
        "id": "pmt_123",
        "amount": 1000,
        "currency": "usd",
        "status": "succeeded",
        "created_at": "2025-11-19T10:30:00Z"
    }

    # Should not raise
    validate(instance=valid_payment, schema=schema)
    print("✓ Valid payment passed schema validation")

    # Test invalid payment (missing required field)
    invalid_payment = {
        "amount": 1000,
        "currency": "usd",
        "status": "succeeded"
    }

    try:
        validate(instance=invalid_payment, schema=schema)
        assert False, "Should have raised validation error"
    except jsonschema.ValidationError as e:
        print(f"✓ Invalid payment correctly rejected: {e.message}")

    # Test invalid payment (wrong status)
    invalid_status = {
        "id": "pmt_123",
        "amount": 1000,
        "currency": "usd",
        "status": "invalid_status",
        "created_at": "2025-11-19T10:30:00Z"
    }

    try:
        validate(instance=invalid_status, schema=schema)
        assert False, "Should have raised validation error"
    except jsonschema.ValidationError as e:
        print(f"✓ Invalid status correctly rejected: {e.message}")
```

---

## Step 6: CI/CD Integration

### GitHub Actions Workflow

**`.github/workflows/api-tests.yml`**:

```yaml
name: API Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  postman-tests:
    name: Postman Collection Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Newman (Postman CLI)
        run: npm install -g newman

      - name: Run API tests against staging
        run: |
          newman run payment-api.postman_collection.json \
            -e testing.postman_environment.json \
            --reporters cli,json \
            --reporter-json-export test-results.json

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: postman-results
          path: test-results.json

  contract-tests:
    name: Contract Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pact pytest requests

      - name: Run contract tests
        run: pytest test_payment_contract.py -v

      - name: Publish pacts
        if: success()
        run: |
          # Publish to Pact Broker
          curl -X PUT \
            https://broker.pactflow.io/pacts/provider/PaymentAPI/consumer/PaymentSDK/version/$(git rev-parse --short HEAD) \
            -H "Authorization: Bearer ${{ secrets.PACT_BROKER_TOKEN }}" \
            -d @pacts/payment-sdk-paymentapi.json

  schema-validation:
    name: Schema Validation Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install jsonschema pytest requests

      - name: Run schema validation tests
        run: pytest test_payment_schema.py -v

  api-performance:
    name: API Performance Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install k6
        run: |
          sudo apt-get update
          sudo apt-get install -y k6

      - name: Run performance tests
        env:
          API_KEY: ${{ secrets.STAGING_API_KEY }}
        run: |
          k6 run performance-test.js \
            --vus 10 \
            --duration 30s \
            --summary-export=summary.json

      - name: Check performance results
        run: |
          # Check if any failed requests
          if grep -q '"failed"' summary.json; then
            echo "Performance test failed"
            exit 1
          fi
```

---

## Step 7: Testing Best Practices Documentation

### Best Practices Guide

**TESTING_GUIDE.md**:

```markdown
# API Testing Best Practices

## 1. Test Independence

Each test should be independent and not rely on other tests.

```python
# BAD: Test depends on previous test
def test_1_create_payment():
    global payment_id
    response = api.create_payment(1000, 'usd')
    payment_id = response['id']

def test_2_get_payment():
    response = api.get_payment(payment_id)  # Depends on test_1

# GOOD: Tests are independent
def test_create_payment_creates_resource():
    response = api.create_payment(1000, 'usd')
    assert response['status_code'] == 201
    assert 'id' in response['data']

def test_get_payment_retrieves_resource():
    # Set up test data independently
    payment = create_test_payment(1000, 'usd')
    response = api.get_payment(payment['id'])
    assert response['status_code'] == 200
    assert response['data']['id'] == payment['id']
```

## 2. Comprehensive Test Coverage

Test happy paths, edge cases, and error conditions.

```python
def test_payment_creation_coverage():
    # Happy path
    test_create_payment_with_valid_data()

    # Edge cases
    test_create_payment_with_minimum_amount()
    test_create_payment_with_maximum_amount()
    test_create_payment_with_special_characters()

    # Error cases
    test_create_payment_with_missing_amount()
    test_create_payment_with_negative_amount()
    test_create_payment_with_invalid_currency()
    test_create_payment_with_unauthorized_key()
```

## 3. Meaningful Assertions

Use clear, descriptive assertions.

```python
# BAD: Unclear assertion
assert response['status'] == 201

# GOOD: Clear assertion with context
pm.test('Payment creation returns 201 Created status', function() {
    pm.response.to.have.status(201);
});

# GOOD: Multiple specific assertions
pm.test('Payment response contains all required fields', function() {
    var data = pm.response.json();
    pm.expect(data).to.have.property('id');
    pm.expect(data).to.have.property('amount');
    pm.expect(data).to.have.property('currency');
    pm.expect(data).to.have.property('status');
    pm.expect(data).to.have.property('created_at');
});
```

## 4. Test Data Management

Use realistic, isolated test data.

```python
# Use fixtures for reusable test data
@pytest.fixture
def test_payment():
    return {
        'amount': 1000,
        'currency': 'usd',
        'description': f'Test payment {time.time()}'
    }

def test_create_payment(test_payment):
    response = api.create_payment(**test_payment)
    assert response['status'] == 201

# Clean up after tests
def test_create_and_delete_payment():
    payment = api.create_payment(1000, 'usd')
    try:
        assert payment['status'] == 'pending'
    finally:
        api.delete_payment(payment['id'])
```

## 5. Timeout Handling

Always use appropriate timeouts.

```python
# BAD: No timeout
response = requests.get(url)

# GOOD: With timeout
response = requests.get(url, timeout=5)

# GOOD: Custom timeouts per environment
TIMEOUTS = {
    'development': 5,
    'staging': 10,
    'production': 30
}
timeout = TIMEOUTS.get(os.getenv('ENV'), 10)
```

## 6. Error Message Clarity

Include helpful error messages.

```python
# BAD: Generic error message
assert response['status'] == 201

# GOOD: Specific error message
assert response['status'] == 201, (
    f"Expected status 201, got {response['status']}. "
    f"Response: {response['body']}"
)
```

## 7. Idempotency Testing

Verify endpoints are idempotent where expected.

```python
def test_create_payment_idempotency():
    request_data = {'amount': 1000, 'currency': 'usd', 'idempotency_key': 'unique_key'}

    # First request
    response1 = api.create_payment(**request_data)
    payment_id1 = response1['data']['id']

    # Second request with same key
    response2 = api.create_payment(**request_data)
    payment_id2 = response2['data']['id']

    # Should return same payment
    assert payment_id1 == payment_id2
```

## 8. Rate Limit Testing

Test API behavior under rate limits.

```javascript
pm.test('API respects rate limits', function() {
  // Make multiple rapid requests
  for (let i = 0; i < 101; i++) {
    pm.sendRequest({
      url: pm.environment.get('baseUrl') + '/payments',
      method: 'POST',
      body: { amount: 1000, currency: 'usd' }
    });
  }

  // 101st request should be rate limited
  pm.response.to.have.status(429);
  pm.expect(pm.response.headers.get('Retry-After')).to.exist;
});
```

## 9. Monitoring and Logging

Log test execution for debugging.

```python
import logging

logger = logging.getLogger(__name__)

def test_create_payment():
    logger.info(f"Creating payment with amount=1000")

    response = api.create_payment(1000, 'usd')

    logger.info(f"Payment created: id={response['data']['id']}, status={response['status']}")

    assert response['status'] == 201
```

## 10. Documentation

Document test purposes and setup.

```python
def test_payment_succeeds_with_valid_card():
    """
    Test that payment processing succeeds with valid card details.

    This test verifies the happy path for payment creation.
    It ensures that:
    1. A valid payment request is accepted
    2. Payment status is initially 'pending'
    3. The response contains all required fields

    Setup: Uses test card 4111111111111111
    Cleanup: Automatically deletes created payment
    """
    payment = api.create_payment(
        amount=1000,
        currency='usd',
        payment_method='card_4111111111111111'
    )

    assert payment['status'] == 'pending'
    assert 'id' in payment
```
```

---

## Step 8: Performance Testing

### Load Testing with k6

**performance-test.js**:

```javascript
/**
 * Performance test for Payment API
 * Run with: k6 run performance-test.js
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp-up to 100 VUs
    { duration: '5m', target: 100 },   // Stay at 100 VUs
    { duration: '2m', target: 0 },     // Ramp-down to 0 VUs
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
    http_req_failed: ['<0.1'],         // <0.1% failure rate
  },
};

const API_KEY = __ENV.API_KEY;
const BASE_URL = __ENV.BASE_URL || 'https://api.staging.example.com';

export default function () {
  group('Create Payment', () => {
    const createRes = http.post(
      `${BASE_URL}/payments`,
      JSON.stringify({
        amount: Math.floor(Math.random() * 10000) + 50,
        currency: 'usd',
        description: 'Load test payment'
      }),
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`
        }
      }
    );

    check(createRes, {
      'create payment status is 201': (r) => r.status === 201,
      'create payment has id': (r) => JSON.parse(r.body).id !== undefined,
      'create payment response time < 500ms': (r) => r.timings.duration < 500,
    });

    const paymentId = JSON.parse(createRes.body).id;

    sleep(1);

    group('Get Payment', () => {
      const getRes = http.get(
        `${BASE_URL}/payments/${paymentId}`,
        {
          headers: {
            'Authorization': `Bearer ${API_KEY}`
          }
        }
      );

      check(getRes, {
        'get payment status is 200': (r) => r.status === 200,
        'get payment returns same id': (r) => JSON.parse(r.body).id === paymentId,
        'get payment response time < 500ms': (r) => r.timings.duration < 500,
      });
    });

    sleep(1);
  });
}
```

---

## Step 9: Documentation Summary

### Testing Documentation Structure

Create comprehensive testing documentation:

```
api-testing-docs/
├── README.md                          # Overview
├── GETTING_STARTED.md                 # Quick start guide
├── POSTMAN_SETUP.md                   # Postman collection setup
├── CONTRACT_TESTING.md                # Pact/contract testing guide
├── TEST_DATA.md                       # Test data management
├── BEST_PRACTICES.md                  # Testing best practices
├── PERFORMANCE_TESTING.md             # k6 performance tests
├── CI_CD_INTEGRATION.md              # GitHub Actions setup
├── TROUBLESHOOTING.md                # Common issues and solutions
│
├── postman/
│   ├── payment-api.postman_collection.json
│   ├── development.postman_environment.json
│   ├── testing.postman_environment.json
│   └── production.postman_environment.json
│
├── test-data/
│   ├── valid-cases.json
│   ├── invalid-cases.json
│   └── edge-cases.json
│
├── contracts/
│   ├── payment-sdk-payment-api.json
│   └── payment-api-database.json
│
├── schemas/
│   ├── payment.schema.json
│   ├── error.schema.json
│   └── list-response.schema.json
│
├── tests/
│   ├── test_payment_contract.py
│   ├── test_payment_schema.py
│   ├── test_payment_api.js
│   └── payment-api-test.go
│
├── performance/
│   ├── performance-test.js
│   ├── load-test.js
│   └── stress-test.js
│
└── ci-cd/
    ├── api-tests.yml
    ├── contract-tests.yml
    └── performance-tests.yml
```

---

## Testing Checklist

- [ ] Postman collection created with all endpoints
- [ ] Pre-request scripts for test setup
- [ ] Test scripts with assertions for all responses
- [ ] Test data sets for valid/invalid cases
- [ ] Environments configured (dev/test/prod)
- [ ] Contract tests implemented
- [ ] Schema validation tests
- [ ] Error case tests documented
- [ ] Happy path tests documented
- [ ] Edge case tests documented
- [ ] Performance tests created
- [ ] Load testing configured
- [ ] CI/CD pipeline configured
- [ ] Test results reporting
- [ ] Documentation complete
- [ ] Examples provided for each test type

---

## Troubleshooting Tests

### Tests fail intermittently

**Causes**:
- Race conditions
- Timing dependencies
- Inconsistent test data

**Solutions**:
```javascript
// Add retry logic
pm.test('Payment created', function() {
  let success = false;
  for (let i = 0; i < 3; i++) {
    if (pm.response.code === 201) {
      success = true;
      break;
    }
    sleep(1000);
  }
  pm.expect(success).to.be.true;
});
```

### Contract tests not matching

**Verify**:
1. Consumer expectations match actual requests
2. Provider responses match contract
3. Data types are consistent
4. Required fields are present

### Performance tests timeout

**Check**:
1. API endpoint is responding
2. Timeout is appropriate for environment
3. Database has test data
4. No rate limiting blocking requests

---

## Next Steps

- [Webhook Documentation](./documenting-webhooks.md)
- [SDK Documentation](./creating-sdk-documentation.md)
- [OpenAPI Specifications](./creating-openapi-spec.md)

---

**Complete Examples**: See test examples in `src/test-examples/` directory for Postman, Pact, and k6 tests.
