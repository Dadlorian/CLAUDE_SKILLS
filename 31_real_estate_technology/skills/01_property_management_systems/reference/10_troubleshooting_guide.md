# PMS Troubleshooting Guide

## Payment Processing Issues

### Problem: Payment Declined
**Symptoms**: Credit card or ACH payment rejected

**Common Causes**:
- Insufficient funds
- Expired card
- Incorrect billing information
- Daily limit exceeded
- Fraud alert triggered

**Troubleshooting Steps**:
1. Check error code from payment processor
2. Verify card expiration date
3. Confirm billing address matches card
4. Ask tenant to contact bank
5. Try alternative payment method
6. Update payment information in system

**Prevention**:
- Enable saved payment methods
- Send expiration reminders 30 days before
- Offer multiple payment options
- Use automated retry logic for ACH

### Problem: Payment Not Posted to Ledger
**Symptoms**: Payment successful but not reflected in tenant account

**Troubleshooting Steps**:
1. Check webhook delivery logs
2. Verify transaction ID in payment gateway
3. Review application error logs
4. Check database transaction logs
5. Manually reconcile and post if needed

**Code Check**:
```javascript
// Verify webhook processing
app.post('/webhooks/payment', async (req, res) => {
  try {
    const event = req.body;

    // Log webhook received
    logger.info('Webhook received', { event_id: event.id });

    // Process payment
    await processPayment(event.data);

    // Send 200 BEFORE processing completes (best practice)
    res.status(200).json({ received: true });
  } catch (error) {
    logger.error('Webhook processing failed', { error });
    // Still return 200 to prevent retries for app errors
    res.status(200).json({ received: true, error: error.message });
  }
});
```

**Prevention**:
- Implement idempotency keys
- Use database transactions
- Set up webhook retry monitoring
- Create reconciliation reports

### Problem: Duplicate Payments Posted
**Symptoms**: Same payment recorded multiple times

**Troubleshooting Steps**:
1. Check for duplicate webhook deliveries
2. Review transaction timestamps
3. Verify idempotency key implementation
4. Reverse duplicate transactions
5. Refund if money was charged twice

**Fix**:
```javascript
// Implement idempotency check
async function processPayment(paymentData) {
  const existingTransaction = await Ledger.findOne({
    where: {
      external_transaction_id: paymentData.id
    }
  });

  if (existingTransaction) {
    logger.warn('Duplicate payment attempt', {
      payment_id: paymentData.id
    });
    return existingTransaction;
  }

  // Process new payment
  return await Ledger.create({
    external_transaction_id: paymentData.id,
    amount: -paymentData.amount,
    // ... other fields
  });
}
```

## Data Synchronization Issues

### Problem: Property Data Out of Sync
**Symptoms**: Different values in PMS vs. accounting system

**Troubleshooting Steps**:
1. Identify which system is source of truth
2. Check sync logs for errors
3. Review last successful sync timestamp
4. Manually compare records
5. Force full re-sync if needed

**Diagnostic Query**:
```sql
-- Find properties with sync issues
SELECT
  p.id,
  p.name,
  p.total_units,
  p.last_sync_at,
  p.sync_status,
  p.sync_error_message
FROM properties p
WHERE p.sync_status = 'error'
   OR p.last_sync_at < NOW() - INTERVAL '24 hours'
ORDER BY p.last_sync_at;
```

**Prevention**:
- Implement change data capture (CDC)
- Schedule regular reconciliation jobs
- Set up sync failure alerts
- Maintain audit logs

### Problem: Slow Database Queries
**Symptoms**: Reports timing out, slow page loads

**Troubleshooting Steps**:
1. Enable query logging
2. Identify slow queries (>1 second)
3. Analyze execution plans
4. Check for missing indexes
5. Review table statistics
6. Consider query optimization

**Diagnostic**:
```sql
-- Find slow queries (PostgreSQL)
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
WHERE mean_time > 1000 -- 1 second
ORDER BY total_time DESC
LIMIT 20;

-- Find missing indexes
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE 'pg_%'
ORDER BY tablename;
```

**Common Fixes**:
```sql
-- Add index on frequently queried columns
CREATE INDEX idx_units_property_status
ON units(property_id, unit_status);

CREATE INDEX idx_leases_dates
ON leases(start_date, end_date)
WHERE lease_status = 'active';

CREATE INDEX idx_ledger_lease_date
ON ledger(lease_id, transaction_date DESC);

-- Update table statistics
ANALYZE properties;
ANALYZE units;
ANALYZE leases;
ANALYZE ledger;
```

## Integration Failures

### Problem: API Connection Timeout
**Symptoms**: Integration requests failing with timeout errors

**Troubleshooting Steps**:
1. Check external service status page
2. Verify network connectivity
3. Review timeout configuration
4. Check rate limits
5. Implement exponential backoff
6. Use circuit breaker pattern

**Fix**:
```javascript
const axios = require('axios');

// Configure timeouts
const api = axios.create({
  baseURL: 'https://api.external-service.com',
  timeout: 30000, // 30 seconds
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  }
});

// Retry logic
async function callAPIWithRetry(endpoint, data, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await api.post(endpoint, data);
    } catch (error) {
      if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
        if (i === retries - 1) throw error;
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      throw error;
    }
  }
}
```

### Problem: Webhook Not Received
**Symptoms**: Expected event notification never arrives

**Troubleshooting Steps**:
1. Check webhook configuration in external service
2. Verify endpoint URL is correct and accessible
3. Review firewall/security group rules
4. Check SSL certificate validity
5. Review webhook delivery logs
6. Test endpoint manually

**Testing**:
```bash
# Test webhook endpoint
curl -X POST https://your-domain.com/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"test": true, "timestamp": "2024-11-19T10:00:00Z"}'

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

**Debugging Webhook Handler**:
```javascript
app.post('/webhooks/stripe', async (req, res) => {
  // Log raw request for debugging
  logger.debug('Webhook received', {
    headers: req.headers,
    body: req.body,
    timestamp: new Date()
  });

  try {
    // Validate signature
    const sig = req.headers['stripe-signature'];
    const event = stripe.webhooks.constructEvent(
      req.rawBody,
      sig,
      WEBHOOK_SECRET
    );

    logger.info('Webhook validated', { type: event.type });

    // Process event
    await handleEvent(event);

    res.json({ received: true });
  } catch (error) {
    logger.error('Webhook failed', { error: error.message });
    res.status(400).send(`Webhook Error: ${error.message}`);
  }
});
```

## User Access Issues

### Problem: User Cannot Login
**Symptoms**: Invalid credentials error despite correct password

**Troubleshooting Steps**:
1. Verify account exists and is active
2. Check password expiration policy
3. Review account lockout status
4. Test password reset flow
5. Check for case sensitivity issues
6. Review authentication logs

**Diagnostic**:
```sql
-- Check user account status
SELECT
  id,
  email,
  account_status,
  last_login_at,
  failed_login_attempts,
  locked_until,
  password_expires_at
FROM users
WHERE email = 'user@example.com';

-- Reset lockout
UPDATE users
SET failed_login_attempts = 0,
    locked_until = NULL
WHERE email = 'user@example.com';
```

### Problem: Permission Denied Error
**Symptoms**: User sees "Access Denied" on certain features

**Troubleshooting Steps**:
1. Verify user's role and permissions
2. Check resource ownership
3. Review role-based access control (RBAC) configuration
4. Check for recent permission changes
5. Review application logs for authorization failures

**Diagnostic**:
```sql
-- Check user roles and permissions
SELECT
  u.email,
  r.role_name,
  p.permission_name,
  p.resource_type
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE u.email = 'user@example.com';
```

## Report Generation Issues

### Problem: Report Takes Too Long to Generate
**Symptoms**: Timeout errors, slow performance

**Troubleshooting Steps**:
1. Check date range (limit to 1 year max)
2. Review query execution plan
3. Add appropriate indexes
4. Implement pagination
5. Use materialized views for complex reports
6. Consider async report generation

**Optimization**:
```javascript
// Async report generation
async function generateReport(reportType, params) {
  // Create job record
  const job = await ReportJob.create({
    type: reportType,
    params: params,
    status: 'pending',
    user_id: params.userId
  });

  // Queue background job
  await reportQueue.add('generate', {
    jobId: job.id,
    type: reportType,
    params: params
  });

  return {
    jobId: job.id,
    status: 'processing',
    checkUrl: `/api/reports/${job.id}/status`
  };
}

// Background worker
reportQueue.process('generate', async (job) => {
  const { jobId, type, params } = job.data;

  try {
    const reportData = await runReportQuery(type, params);
    const pdfBuffer = await generatePDF(reportData);

    // Upload to S3
    const url = await uploadToS3(pdfBuffer, `reports/${jobId}.pdf`);

    // Update job
    await ReportJob.update({
      status: 'completed',
      file_url: url,
      completed_at: new Date()
    }, {
      where: { id: jobId }
    });

    // Notify user
    await sendEmail(params.userEmail, {
      subject: 'Report Ready',
      downloadUrl: url
    });
  } catch (error) {
    await ReportJob.update({
      status: 'failed',
      error_message: error.message
    }, {
      where: { id: jobId }
    });
  }
});
```

### Problem: Incorrect Report Data
**Symptoms**: Numbers don't match, missing data

**Troubleshooting Steps**:
1. Verify report filters and date ranges
2. Check for timezone issues
3. Review data source queries
4. Validate calculation logic
5. Compare with raw data in database
6. Check for rounding errors

**Common Timezone Fix**:
```javascript
// Always use UTC for date queries
const startDate = moment.tz(params.startDate, userTimezone)
  .startOf('day')
  .utc()
  .format();

const endDate = moment.tz(params.endDate, userTimezone)
  .endOf('day')
  .utc()
  .format();

// Query with UTC dates
const data = await Ledger.findAll({
  where: {
    transaction_date: {
      [Op.gte]: startDate,
      [Op.lte]: endDate
    }
  }
});
```

## Email/SMS Delivery Issues

### Problem: Emails Not Sending
**Symptoms**: No emails received by tenants

**Troubleshooting Steps**:
1. Check email service status (SendGrid, SES)
2. Verify API credentials
3. Review sending limits/quotas
4. Check spam folder
5. Validate email addresses
6. Review bounce and complaint rates

**Diagnostic**:
```javascript
// Test email sending
const sgMail = require('@sendgrid/mail');

async function testEmail() {
  try {
    await sgMail.send({
      to: 'test@example.com',
      from: 'noreply@yourproperty.com',
      subject: 'Test Email',
      text: 'If you receive this, email is working.'
    });
    console.log('✓ Email sent successfully');
  } catch (error) {
    console.error('✗ Email failed:', error.response.body);
  }
}
```

**Common Issues**:
- SPF/DKIM not configured: Set up email authentication
- High bounce rate: Clean email list, validate addresses
- Spam complaints: Review email content, add unsubscribe link

### Problem: SMS Not Delivering
**Symptoms**: Text messages not received

**Troubleshooting Steps**:
1. Verify phone number format (+1XXXXXXXXXX)
2. Check Twilio account status and balance
3. Review SMS sending logs
4. Check for carrier blocks
5. Validate phone numbers are mobile (not landline)
6. Review opt-out list

**Fix**:
```javascript
// Validate and format phone number
const phoneUtil = require('google-libphonenumber').PhoneNumberUtil.getInstance();

function validatePhone(phone, countryCode = 'US') {
  try {
    const number = phoneUtil.parse(phone, countryCode);
    if (!phoneUtil.isValidNumber(number)) {
      throw new Error('Invalid phone number');
    }
    return phoneUtil.format(number, PNF.E164); // +1XXXXXXXXXX
  } catch (error) {
    throw new Error(`Phone validation failed: ${error.message}`);
  }
}
```

## Performance Degradation

### Problem: Application Running Slow
**Symptoms**: Page loads taking >3 seconds

**Troubleshooting Steps**:
1. Check server CPU and memory usage
2. Review database connection pool
3. Analyze slow API endpoints
4. Check for memory leaks
5. Review caching effectiveness
6. Analyze front-end bundle size

**Monitoring**:
```javascript
// APM instrumentation
const apm = require('elastic-apm-node');

// Measure endpoint performance
app.get('/api/properties', async (req, res) => {
  const span = apm.startSpan('database.query');

  try {
    const properties = await Property.findAll({
      include: [{ model: Unit }]
    });

    res.json(properties);
  } finally {
    if (span) span.end();
  }
});

// Memory leak detection
setInterval(() => {
  const usage = process.memoryUsage();
  logger.info('Memory usage', {
    rss: `${Math.round(usage.rss / 1024 / 1024)}MB`,
    heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)}MB`,
    heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)}MB`
  });
}, 60000); // Every minute
```

**Common Fixes**:
- Add Redis caching for frequently accessed data
- Implement database query optimization
- Enable CDN for static assets
- Add pagination to large lists
- Optimize images and bundle size

## Data Validation Errors

### Problem: Invalid Data in Database
**Symptoms**: Application errors, data integrity issues

**Troubleshooting Steps**:
1. Run data validation queries
2. Identify source of bad data
3. Implement input validation
4. Add database constraints
5. Create data cleanup script

**Validation Queries**:
```sql
-- Find invalid email addresses
SELECT id, email FROM tenants
WHERE email NOT LIKE '%@%.%';

-- Find overlapping leases
SELECT u.unit_number, l1.id, l1.start_date, l1.end_date
FROM leases l1
JOIN leases l2 ON l1.unit_id = l2.unit_id
  AND l1.id != l2.id
  AND l1.lease_status = 'active'
  AND l2.lease_status = 'active'
  AND l1.start_date <= l2.end_date
  AND l1.end_date >= l2.start_date
JOIN units u ON l1.unit_id = u.id;

-- Find negative balances that shouldn't exist
SELECT tenant_id, SUM(amount) as balance
FROM ledger
GROUP BY tenant_id
HAVING SUM(amount) < -100; -- More than $100 credit
```

**Prevention**:
```javascript
// Input validation
const { body, validationResult } = require('express-validator');

app.post('/api/leases',
  body('start_date').isISO8601().toDate(),
  body('end_date').isISO8601().toDate()
    .custom((end_date, { req }) => {
      if (end_date <= req.body.start_date) {
        throw new Error('End date must be after start date');
      }
      return true;
    }),
  body('base_rent').isFloat({ min: 0 }),
  body('unit_id').isUUID(),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Process valid data
    const lease = await Lease.create(req.body);
    res.status(201).json(lease);
  }
);
```

This troubleshooting guide addresses the most common issues in property management systems.
