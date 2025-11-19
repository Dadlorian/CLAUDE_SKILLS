# PMS API Integration Guide

## Overview
Complete guide for integrating with property management system APIs, including authentication, common workflows, error handling, and best practices.

## Authentication

### OAuth 2.0 Setup

#### 1. Register Your Application

Navigate to Developer Portal at `https://api.yourpms.com/developers`

**Application Registration**:
```
Application Name: My Integration App
Application Type: Web Application
Redirect URI: https://your-app.com/oauth/callback
Scopes: properties:read properties:write leases:read leases:write
  payments:read tenants:read workorders:read workorders:write
```

**Response**:
```json
{
  "client_id": "cli_1234567890abcdef",
  "client_secret": "sec_abcdefghijklmnopqrstuvwxyz1234567890",
  "created_at": "2024-11-19T10:00:00Z"
}
```

**⚠️ Important**: Store `client_secret` securely. Never commit to version control.

#### 2. Implement OAuth Flow

**Step 1: Authorization URL**
```javascript
const authUrl = `https://api.yourpms.com/oauth/authorize?` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
  `response_type=code&` +
  `scope=properties:read properties:write leases:read leases:write&` +
  `state=${generateRandomState()}`;

// Redirect user to authUrl
res.redirect(authUrl);
```

**Step 2: Handle Callback**
```javascript
app.get('/oauth/callback', async (req, res) => {
  const { code, state } = req.query;

  // Verify state to prevent CSRF
  if (state !== req.session.oauthState) {
    return res.status(400).send('Invalid state parameter');
  }

  try {
    // Exchange code for access token
    const tokenResponse = await axios.post(
      'https://api.yourpms.com/oauth/token',
      {
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: REDIRECT_URI,
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET
      }
    );

    const { access_token, refresh_token, expires_in } = tokenResponse.data;

    // Store tokens securely (encrypted in database)
    await storeTokens({
      access_token,
      refresh_token,
      expires_at: Date.now() + (expires_in * 1000)
    });

    res.redirect('/dashboard');
  } catch (error) {
    console.error('OAuth error:', error);
    res.status(500).send('Authentication failed');
  }
});
```

**Step 3: Refresh Token**
```javascript
async function refreshAccessToken(refreshToken) {
  const response = await axios.post(
    'https://api.yourpms.com/oauth/token',
    {
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET
    }
  );

  const { access_token, refresh_token, expires_in } = response.data;

  await updateStoredTokens({
    access_token,
    refresh_token,
    expires_at: Date.now() + (expires_in * 1000)
  });

  return access_token;
}
```

### API Key Authentication (Server-to-Server)

For server-to-server integrations, use API keys:

```javascript
const axios = require('axios');

const pmsAPI = axios.create({
  baseURL: 'https://api.yourpms.com/v1',
  headers: {
    'Authorization': `Bearer ${process.env.PMS_API_KEY}`,
    'Content-Type': 'application/json',
    'X-API-Version': '2024-11-01'
  },
  timeout: 30000
});

// Example request
const properties = await pmsAPI.get('/properties');
```

## Common Integration Workflows

### Workflow 1: Sync Properties

**Objective**: Keep external system in sync with PMS properties

**Implementation**:
```javascript
const cron = require('node-cron');

// Sync every hour
cron.schedule('0 * * * *', async () => {
  try {
    // Fetch properties from PMS
    const response = await pmsAPI.get('/properties', {
      params: {
        updated_since: await getLastSyncTime(),
        limit: 100
      }
    });

    const properties = response.data.data;

    for (const property of properties) {
      // Upsert to your database
      await db.properties.upsert({
        where: { pms_id: property.id },
        update: {
          name: property.name,
          address: property.address,
          total_units: property.total_units,
          occupancy_rate: property.occupancy_rate,
          updated_at: new Date()
        },
        create: {
          pms_id: property.id,
          name: property.name,
          address: property.address,
          total_units: property.total_units,
          occupancy_rate: property.occupancy_rate
        }
      });
    }

    // Update last sync time
    await setLastSyncTime(new Date());

    console.log(`✓ Synced ${properties.length} properties`);
  } catch (error) {
    console.error('Property sync failed:', error);
    // Alert admin
    await sendAlert('Property sync failed', error.message);
  }
});
```

### Workflow 2: Handle Payments

**Objective**: Process payment and update ledger

**Implementation**:
```javascript
async function processRentPayment(tenantId, amount, paymentMethod) {
  try {
    // 1. Create payment in PMS
    const payment = await pmsAPI.post('/payments', {
      tenant_id: tenantId,
      amount: amount,
      payment_method: paymentMethod,
      payment_date: new Date().toISOString().split('T')[0],
      notes: 'Rent payment via integration'
    });

    console.log('✓ Payment created:', payment.data.id);

    // 2. Verify payment was posted to ledger
    const ledger = await pmsAPI.get(`/tenants/${tenantId}/ledger`, {
      params: {
        start_date: new Date().toISOString().split('T')[0]
      }
    });

    const paymentEntry = ledger.data.transactions.find(
      t => t.id === payment.data.id
    );

    if (!paymentEntry) {
      throw new Error('Payment not found in ledger');
    }

    // 3. Get updated balance
    const currentBalance = ledger.data.current_balance;

    return {
      success: true,
      payment_id: payment.data.id,
      new_balance: currentBalance
    };
  } catch (error) {
    console.error('Payment processing error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Usage
const result = await processRentPayment('tenant_123', 2000.00, 'ach');
if (result.success) {
  console.log(`Payment processed. New balance: $${result.new_balance}`);
}
```

### Workflow 3: Create Lease from Application

**Objective**: Convert approved application to active lease

**Implementation**:
```javascript
async function createLeaseFromApplication(applicationId) {
  try {
    // 1. Get application details
    const app = await pmsAPI.get(`/applications/${applicationId}`);
    const application = app.data;

    if (application.status !== 'approved') {
      throw new Error('Application must be approved first');
    }

    // 2. Check unit availability
    const unit = await pmsAPI.get(`/units/${application.unit_id}`);
    if (unit.data.status !== 'vacant') {
      throw new Error('Unit is not available');
    }

    // 3. Create lease
    const lease = await pmsAPI.post('/leases', {
      unit_id: application.unit_id,
      tenant_ids: application.applicants.map(a => a.id),
      type: 'fixed',
      start_date: application.desired_move_in_date,
      end_date: calculateEndDate(
        application.desired_move_in_date,
        application.lease_term_months
      ),
      move_in_date: application.desired_move_in_date,
      base_rent: application.approved_rent,
      security_deposit: application.approved_rent,
      lease_term_months: application.lease_term_months,
      pet_rent: application.pets.length * 50,
      pets_allowed: application.pets.length > 0
    });

    console.log('✓ Lease created:', lease.data.id);

    // 4. Generate lease document
    const document = await pmsAPI.post(
      `/leases/${lease.data.id}/generate-document`,
      {
        template_id: 'standard_lease_12month',
        send_for_signature: true
      }
    );

    console.log('✓ Lease document sent for signature');

    // 5. Update unit status
    await pmsAPI.patch(`/units/${application.unit_id}`, {
      status: 'leased',
      availability_date: null
    });

    // 6. Update application status
    await pmsAPI.patch(`/applications/${applicationId}`, {
      status: 'leased',
      lease_id: lease.data.id
    });

    return {
      success: true,
      lease_id: lease.data.id,
      document_url: document.data.url
    };
  } catch (error) {
    console.error('Lease creation error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

function calculateEndDate(startDate, months) {
  const date = new Date(startDate);
  date.setMonth(date.getMonth() + months);
  date.setDate(date.getDate() - 1); // End day before start date
  return date.toISOString().split('T')[0];
}
```

### Workflow 4: Webhook Integration

**Objective**: Receive real-time notifications from PMS

**Setup**:
```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();

// Use raw body for signature verification
app.use('/webhooks', express.raw({ type: 'application/json' }));

app.post('/webhooks/pms', (req, res) => {
  const signature = req.headers['x-pms-signature'];
  const timestamp = req.headers['x-pms-timestamp'];

  // Verify webhook signature
  if (!verifyWebhookSignature(req.body, signature, timestamp)) {
    console.error('Invalid webhook signature');
    return res.status(401).send('Unauthorized');
  }

  // Acknowledge receipt immediately
  res.status(200).json({ received: true });

  // Process webhook async
  const event = JSON.parse(req.body.toString());
  processWebhook(event).catch(error => {
    console.error('Webhook processing error:', error);
  });
});

function verifyWebhookSignature(payload, signature, timestamp) {
  // Prevent replay attacks (reject if > 5 minutes old)
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - timestamp) > 300) {
    return false;
  }

  // Verify signature
  const expectedSig = crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(`${timestamp}.${payload}`)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`v1=${expectedSig}`)
  );
}

async function processWebhook(event) {
  console.log('Processing webhook:', event.type);

  switch (event.type) {
    case 'payment.received':
      await handlePaymentReceived(event.data);
      break;

    case 'lease.created':
      await handleLeaseCreated(event.data);
      break;

    case 'lease.expiring_soon':
      await handleLeaseExpiring(event.data);
      break;

    case 'workorder.created':
      await handleWorkOrderCreated(event.data);
      break;

    case 'tenant.moved_in':
      await handleTenantMovedIn(event.data);
      break;

    case 'tenant.moved_out':
      await handleTenantMovedOut(event.data);
      break;

    default:
      console.log('Unhandled event type:', event.type);
  }
}

async function handlePaymentReceived(data) {
  // Send confirmation email
  await sendEmail(data.tenant_email, {
    subject: 'Payment Received',
    template: 'payment_confirmation',
    data: {
      amount: data.amount,
      date: data.payment_date,
      new_balance: data.new_balance
    }
  });

  // Update analytics
  await updatePaymentMetrics(data);
}

async function handleLeaseExpiring(data) {
  // Trigger renewal offer workflow
  if (data.days_until_expiration === 90) {
    await sendRenewalOffer(data.lease_id);
  }

  // Alert property manager
  if (data.days_until_expiration === 30 && !data.renewal_offered) {
    await notifyManager(
      `Lease expiring in 30 days: Unit ${data.unit_number}`
    );
  }
}
```

## Pagination

**Handling Paginated Results**:
```javascript
async function fetchAllProperties() {
  const allProperties = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await pmsAPI.get('/properties', {
      params: {
        page: page,
        limit: 100
      }
    });

    allProperties.push(...response.data.data);

    // Check if there are more pages
    hasMore = response.data.pagination.current_page <
              response.data.pagination.total_pages;
    page++;
  }

  return allProperties;
}

// Alternative: Cursor-based pagination
async function fetchAllPropertiesCursor() {
  const allProperties = [];
  let cursor = null;

  do {
    const response = await pmsAPI.get('/properties', {
      params: {
        limit: 100,
        cursor: cursor
      }
    });

    allProperties.push(...response.data.data);
    cursor = response.data.pagination.next_cursor;
  } while (cursor);

  return allProperties;
}
```

## Error Handling

### Retry Logic with Exponential Backoff

```javascript
async function apiCallWithRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const isLastAttempt = attempt === maxRetries;
      const isRetryable = error.response?.status >= 500 ||
                         error.code === 'ECONNABORTED';

      if (isLastAttempt || !isRetryable) {
        throw error;
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, attempt - 1) * 1000;
      console.log(`Retry attempt ${attempt} after ${delay}ms`);
      await sleep(delay);
    }
  }
}

// Usage
const properties = await apiCallWithRetry(() =>
  pmsAPI.get('/properties')
);
```

### Error Response Handling

```javascript
async function handleAPIErrors(apiCall) {
  try {
    return await apiCall();
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;

      switch (status) {
        case 400:
          console.error('Bad Request:', data.error.message);
          // Handle validation errors
          if (data.error.details) {
            data.error.details.forEach(detail => {
              console.error(`  ${detail.field}: ${detail.message}`);
            });
          }
          break;

        case 401:
          console.error('Unauthorized - refreshing token');
          await refreshAccessToken();
          // Retry original request
          return await apiCall();

        case 403:
          console.error('Forbidden - insufficient permissions');
          break;

        case 404:
          console.error('Resource not found');
          break;

        case 409:
          console.error('Conflict:', data.error.message);
          break;

        case 429:
          console.error('Rate limit exceeded');
          const retryAfter = error.response.headers['retry-after'];
          await sleep(retryAfter * 1000);
          return await apiCall();

        case 500:
        case 502:
        case 503:
          console.error('Server error - will retry');
          throw error; // Let retry logic handle

        default:
          console.error(`HTTP ${status}:`, data);
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server');
      console.error('Possible network error or timeout');
    } else {
      // Error setting up request
      console.error('Request setup error:', error.message);
    }

    throw error;
  }
}
```

## Rate Limiting

**Respect API Rate Limits**:
```javascript
const Bottleneck = require('bottleneck');

// Create limiter (100 requests per minute)
const limiter = new Bottleneck({
  maxConcurrent: 10, // Max 10 simultaneous requests
  minTime: 600        // Min 600ms between requests (100/min)
});

// Wrap API calls
const rateLimitedAPI = {
  get: limiter.wrap((url, config) => pmsAPI.get(url, config)),
  post: limiter.wrap((url, data, config) => pmsAPI.post(url, data, config)),
  put: limiter.wrap((url, data, config) => pmsAPI.put(url, data, config)),
  patch: limiter.wrap((url, data, config) => pmsAPI.patch(url, data, config)),
  delete: limiter.wrap((url, config) => pmsAPI.delete(url, config))
};

// Usage
const properties = await rateLimitedAPI.get('/properties');
```

## Testing

### Unit Tests

```javascript
const nock = require('nock');

describe('PMS API Integration', () => {
  beforeEach(() => {
    nock.cleanAll();
  });

  it('should fetch properties', async () => {
    nock('https://api.yourpms.com')
      .get('/v1/properties')
      .query({ page: 1, limit: 20 })
      .reply(200, {
        data: [
          {
            id: 'prop_123',
            name: 'Test Property',
            total_units: 100
          }
        ],
        pagination: {
          current_page: 1,
          total_pages: 1
        }
      });

    const response = await pmsAPI.get('/properties', {
      params: { page: 1, limit: 20 }
    });

    expect(response.data.data).toHaveLength(1);
    expect(response.data.data[0].name).toBe('Test Property');
  });

  it('should handle API errors', async () => {
    nock('https://api.yourpms.com')
      .get('/v1/properties/invalid')
      .reply(404, {
        error: {
          code: 'not_found',
          message: 'Property not found'
        }
      });

    await expect(pmsAPI.get('/properties/invalid'))
      .rejects
      .toThrow();
  });
});
```

### Integration Tests

```javascript
// Use sandbox environment for integration tests
const sandboxAPI = axios.create({
  baseURL: 'https://api-sandbox.yourpms.com/v1',
  headers: {
    'Authorization': `Bearer ${process.env.SANDBOX_API_KEY}`
  }
});

describe('E2E Integration Tests', () => {
  it('should create and retrieve a property', async () => {
    // Create property
    const createResponse = await sandboxAPI.post('/properties', {
      name: 'Test Property',
      type: 'multifamily',
      address: {
        street: '123 Test St',
        city: 'Austin',
        state: 'TX',
        postal_code: '78701'
      },
      total_units: 50
    });

    const propertyId = createResponse.data.id;
    expect(propertyId).toBeTruthy();

    // Retrieve property
    const getResponse = await sandboxAPI.get(`/properties/${propertyId}`);
    expect(getResponse.data.name).toBe('Test Property');

    // Cleanup
    await sandboxAPI.delete(`/properties/${propertyId}`);
  });
});
```

## Best Practices

### 1. Idempotency

Use idempotency keys for write operations:
```javascript
await pmsAPI.post('/payments', paymentData, {
  headers: {
    'Idempotency-Key': generateUUID()
  }
});
```

### 2. Logging

Log all API interactions:
```javascript
pmsAPI.interceptors.request.use(request => {
  logger.info('API Request', {
    method: request.method,
    url: request.url,
    params: request.params
  });
  return request;
});

pmsAPI.interceptors.response.use(
  response => {
    logger.info('API Response', {
      status: response.status,
      url: response.config.url
    });
    return response;
  },
  error => {
    logger.error('API Error', {
      status: error.response?.status,
      url: error.config?.url,
      error: error.message
    });
    throw error;
  }
);
```

### 3. Caching

Cache frequently accessed data:
```javascript
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 }); // 10 minute TTL

async function getProperty(propertyId) {
  const cacheKey = `property:${propertyId}`;
  const cached = cache.get(cacheKey);

  if (cached) {
    return cached;
  }

  const response = await pmsAPI.get(`/properties/${propertyId}`);
  cache.set(cacheKey, response.data);

  return response.data;
}
```

### 4. Monitoring

Set up monitoring and alerts:
```javascript
const { CloudWatch } = require('@aws-sdk/client-cloudwatch');
const cloudwatch = new CloudWatch();

async function trackAPIMetric(metricName, value) {
  await cloudwatch.putMetricData({
    Namespace: 'PMSIntegration',
    MetricData: [{
      MetricName: metricName,
      Value: value,
      Timestamp: new Date(),
      Unit: 'Count'
    }]
  });
}

// Track successful API calls
trackAPIMetric('APICallsSuccess', 1);

// Track errors
trackAPIMetric('APICallsError', 1);
```

This guide provides a solid foundation for integrating with property management system APIs effectively and reliably.
