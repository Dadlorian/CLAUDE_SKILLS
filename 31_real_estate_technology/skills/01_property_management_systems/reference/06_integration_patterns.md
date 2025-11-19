# PMS Integration Patterns Reference

## Overview
Common integration patterns, protocols, and best practices for connecting property management systems with external services.

## Integration Architecture Patterns

### 1. API-First Integration (Recommended)
**Pattern**: RESTful or GraphQL APIs with OAuth 2.0

**Advantages**:
- Real-time data synchronization
- Bidirectional communication
- Event-driven updates
- Scalable and maintainable

**Use Cases**:
- Payment processing
- Tenant screening
- Maintenance dispatch
- Accounting systems

**Example Flow**:
```
PMS → API Call → External Service → Response → PMS Update
```

### 2. Webhook-Based Integration
**Pattern**: Event-driven push notifications

**Advantages**:
- Near real-time updates
- Reduces polling overhead
- Efficient for event-based workflows

**Use Cases**:
- Payment confirmations
- Screening results
- Work order completions

**Example**:
```javascript
// Webhook endpoint receives event
POST /webhooks/payment-received
{
  "event": "payment.succeeded",
  "payment_id": "pmt_123",
  "amount": 2000.00,
  "lease_id": "lease_456"
}
```

### 3. File-Based Integration (Legacy)
**Pattern**: CSV/XML file exchange via SFTP/FTP

**Advantages**:
- Simple implementation
- Widely supported
- Good for batch processing

**Disadvantages**:
- Not real-time
- Error-prone
- Manual intervention often required

**Use Cases**:
- Accounting system exports
- Bank reconciliation files
- Bulk data imports

### 4. Database Replication
**Pattern**: Direct database sync or CDC (Change Data Capture)

**Advantages**:
- Near real-time sync
- No API development needed

**Disadvantages**:
- Tight coupling
- Security concerns
- Schema dependencies

**Use Cases**:
- Data warehousing
- Reporting systems
- Business intelligence

### 5. Message Queue Integration
**Pattern**: Async messaging via RabbitMQ, Kafka, SQS

**Advantages**:
- Decoupled systems
- Fault tolerant
- Scalable

**Use Cases**:
- High-volume data processing
- Async workflows
- Microservices architecture

## Common Integrations

### Payment Processing

#### Stripe Integration
**Type**: API + Webhooks

**Setup**:
```javascript
// Initialize Stripe
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

// Create payment intent
const paymentIntent = await stripe.paymentIntents.create({
  amount: 200000, // $2,000.00 in cents
  currency: 'usd',
  customer: tenant.stripe_customer_id,
  metadata: {
    lease_id: 'lease_456',
    tenant_id: 'tenant_789',
    charge_type: 'rent',
    period: '2024-11'
  }
});

// Webhook handler
app.post('/webhooks/stripe', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(
    req.body, sig, process.env.STRIPE_WEBHOOK_SECRET
  );

  if (event.type === 'payment_intent.succeeded') {
    await recordPayment(event.data.object);
  }
  res.json({received: true});
});
```

#### ACH Direct Integration
**Pattern**: NACHA file generation + bank portal upload

**File Format**: ACH (Fixed-width text file)

**Process**:
1. Generate ACH file with payment records
2. Upload to bank's secure portal
3. Bank processes on next business day
4. Receive settlement file with confirmations/rejections

### Accounting Systems

#### QuickBooks Online Integration
**Type**: OAuth 2.0 API

**Endpoints**:
```
POST /v3/company/{realmId}/invoice
POST /v3/company/{realmId}/payment
GET /v3/company/{realmId}/account
POST /v3/company/{realmId}/journalentry
```

**Data Sync**:
- Properties → Customers
- Units → Sub-customers
- Leases → Invoices
- Payments → Payments
- Expenses → Bills
- Chart of Accounts → GL Accounts

**Sync Frequency**: Daily or real-time

#### Sage Intacct Integration
**Type**: SOAP/XML API

**Key Objects**:
- CUSTOMER (Property/Tenant)
- ARINVOICE (Rent charges)
- ARPAYMENT (Rent payments)
- GLBATCH (Journal entries)

### Tenant Screening

#### TransUnion Screening Integration
**Type**: REST API

**Workflow**:
```javascript
// Submit screening request
const screening = await transunion.createScreening({
  applicant: {
    first_name: 'John',
    last_name: 'Doe',
    ssn: '123-45-6789',
    dob: '1990-01-15',
    address: {...}
  },
  products: ['credit', 'criminal', 'eviction'],
  property_id: 'prop_123'
});

// Poll for results or receive webhook
const results = await transunion.getResults(screening.id);

// Parse and store in PMS
await processScreeningResults(results);
```

**Results Include**:
- Credit score and report
- Criminal background check
- Eviction history
- Identity verification

### Maintenance Management

#### ServiceChannel Integration (Commercial)
**Type**: REST API + Webhooks

**Flow**:
```
1. Tenant submits work order in PMS
2. PMS creates service call in ServiceChannel
3. ServiceChannel dispatches to vendor
4. Vendor updates status
5. Webhook notifies PMS
6. PMS updates tenant
```

**Benefits**:
- Centralized vendor management
- Automated dispatching
- Invoice reconciliation

### Communication Platforms

#### Twilio SMS Integration
**Type**: REST API

```javascript
const twilio = require('twilio')(accountSid, authToken);

// Send rent reminder
await twilio.messages.create({
  body: 'Reminder: Rent of $2,000 is due tomorrow. Pay at tenantportal.com',
  from: '+15555551234',
  to: tenant.phone
});

// Receive SMS (webhook)
app.post('/sms/incoming', (req, res) => {
  const message = req.body.Body;
  const from = req.body.From;

  // Process tenant inquiry
  handleTenantMessage(from, message);

  res.type('text/xml');
  res.send('<Response></Response>');
});
```

#### SendGrid Email Integration
**Type**: REST API

```javascript
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const msg = {
  to: tenant.email,
  from: 'noreply@property.com',
  templateId: 'd-12345abcde',
  dynamicTemplateData: {
    tenant_name: tenant.first_name,
    property_name: property.name,
    rent_amount: lease.total_monthly_rent,
    due_date: '2024-12-01'
  }
};

await sgMail.send(msg);
```

### Listing Syndication

#### Apartments.com Integration
**Type**: XML Feed

**Feed Generation**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
  <Property>
    <PropertyID>
      <Identification>PROP123</Identification>
    </PropertyID>
    <PropertyName>Sunset Apartments</PropertyName>
    <Address>
      <Address>123 Main St</Address>
      <City>Austin</City>
      <State>TX</State>
      <PostalCode>78701</PostalCode>
    </Address>
    <ILS_Identification>
      <ILS_IdentificationValue>12345</ILS_IdentificationValue>
    </ILS_Identification>
    <Floorplan>
      <FloorplanName>2 Bed 2 Bath</FloorplanName>
      <Room>
        <Count>2</Count>
        <Type>Bedroom</Type>
      </Room>
      <Room>
        <Count>2</Count>
        <Type>Bathroom</Type>
      </Room>
      <SquareFeet>950</SquareFeet>
      <Rent>2200</Rent>
      <AvailableDate>2024-12-01</AvailableDate>
    </Floorplan>
  </Property>
</PhysicalProperty>
```

**Delivery**: FTP upload or API POST

### Smart Home Integration

#### August Smart Lock Integration
**Type**: REST API

**Use Cases**:
- Generate access codes for showings
- Provide temporary codes for maintenance
- Issue permanent codes to new tenants
- Revoke access upon move-out

```javascript
// Create access code
const code = await augustAPI.createAccessCode({
  lock_id: unit.smart_lock_id,
  name: `Tenant - ${tenant.name}`,
  code: generateRandomCode(),
  starts_at: lease.start_date,
  ends_at: lease.end_date
});

// Revoke on move-out
await augustAPI.deleteAccessCode(code.id);
```

## Integration Security

### Authentication Methods

#### OAuth 2.0 (Recommended)
```
1. Authorization Code Flow (user-initiated)
2. Client Credentials Flow (server-to-server)
3. Refresh tokens for long-lived access
```

#### API Keys
- Simpler but less secure
- Rotate regularly (90 days)
- Environment variable storage
- Never commit to version control

#### mTLS (Mutual TLS)
- Certificate-based authentication
- High security for financial transactions
- Used in banking integrations

### Data Encryption

**In Transit**:
- TLS 1.2 or higher
- Strong cipher suites
- Certificate pinning for mobile apps

**At Rest**:
- AES-256 encryption
- Encrypted database fields for PII
- Key management service (KMS)

### Webhook Validation

```javascript
// Validate webhook signature
const crypto = require('crypto');

function validateWebhook(payload, signature, secret) {
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSig)
  );
}
```

## Error Handling

### Retry Logic
```javascript
async function apiCallWithRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      if (error.statusCode >= 500) {
        // Retry on server errors
        await sleep(Math.pow(2, i) * 1000); // Exponential backoff
        continue;
      }
      throw error; // Don't retry client errors
    }
  }
}
```

### Circuit Breaker Pattern
```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.failures = 0;
    this.threshold = threshold;
    this.timeout = timeout;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
  }

  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failures++;
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
    }
  }
}
```

### Dead Letter Queue
For failed webhook deliveries or async processing:
- Store failed messages
- Retry with exponential backoff
- Alert after max retries
- Manual review and reprocessing

## Monitoring and Observability

### Metrics to Track
- API request rate
- Response times (p50, p95, p99)
- Error rates by endpoint
- Integration uptime
- Data sync lag

### Logging
```javascript
logger.info('Payment processed', {
  integration: 'stripe',
  payment_id: 'pmt_123',
  amount: 2000.00,
  tenant_id: 'tenant_456',
  duration_ms: 342
});

logger.error('Payment failed', {
  integration: 'stripe',
  error_code: 'card_declined',
  tenant_id: 'tenant_456',
  retry_attempt: 2
});
```

### Alerting
- Failed payment processing
- Sync failures
- API rate limit warnings
- Integration downtime

## Rate Limiting

### Outbound (to external APIs)
```javascript
const Bottleneck = require('bottleneck');

const limiter = new Bottleneck({
  maxConcurrent: 10,
  minTime: 100 // Min 100ms between requests
});

const apiCall = limiter.wrap(async (params) => {
  return await externalAPI.call(params);
});
```

### Inbound (from external services)
```javascript
const rateLimit = require('express-rate-limit');

const webhookLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
  message: 'Too many requests'
});

app.post('/webhooks/payment', webhookLimiter, handlePaymentWebhook);
```

## Testing Integration

### Unit Tests
```javascript
describe('Stripe Integration', () => {
  it('should create payment intent', async () => {
    const mockStripe = {
      paymentIntents: {
        create: jest.fn().mockResolvedValue({id: 'pi_123'})
      }
    };

    const result = await createPayment(mockStripe, {amount: 2000});
    expect(result.id).toBe('pi_123');
  });
});
```

### Integration Tests
```javascript
describe('Payment Flow', () => {
  it('should record payment on successful webhook', async () => {
    const response = await request(app)
      .post('/webhooks/stripe')
      .send(mockWebhookPayload)
      .set('Stripe-Signature', validSignature);

    expect(response.status).toBe(200);

    const ledger = await Ledger.findOne({
      where: {lease_id: 'lease_456'}
    });
    expect(ledger.amount).toBe(-2000);
  });
});
```

### Sandbox Testing
- Use sandbox/test environments
- Test all scenarios (success, failure, partial)
- Validate webhook handling
- Test error conditions

## Best Practices

1. **Idempotency**: Use idempotency keys to prevent duplicate processing
2. **Versioning**: Version your APIs (v1, v2) for backward compatibility
3. **Documentation**: Maintain integration runbooks
4. **Failover**: Have backup processes for critical integrations
5. **Data Validation**: Validate all incoming data
6. **Audit Logging**: Log all integration activity
7. **Regular Testing**: Test integrations monthly
8. **Monitoring**: 24/7 monitoring of critical integrations
9. **Graceful Degradation**: Continue operations if integration fails
10. **Partner SLAs**: Establish uptime and response time SLAs

Integration architecture should prioritize reliability, security, and maintainability for long-term success.
