# Complete Getting Started Guide

**Target Audience:** Beginner developers
**Time to Complete:** 45 minutes
**Final Outcome:** Production-ready integration

## Prerequisites

- Node.js 14+ (or Python 3.8+)
- npm or pip installed
- A code editor (VS Code recommended)
- Basic JavaScript/Python knowledge
- Free account on example.com

## What You'll Build

A complete backend service that:
1. Authenticates with your API key
2. Processes payments
3. Handles errors gracefully
4. Logs transactions
5. Deploys to production

## Part 1: Setup Your Environment (10 min)

### Step 1: Create Project Directory

```bash
mkdir my-payment-app
cd my-payment-app
npm init -y
```

### Step 2: Install Dependencies

```bash
npm install axios express dotenv
npm install --save-dev nodemon
```

### Step 3: Create Environment File

Create `.env` file:

```bash
API_KEY=sk_live_YOUR_API_KEY_HERE
PORT=3000
NODE_ENV=development
```

⚠️ Never commit `.env` to version control. Add to `.gitignore`:

```
.env
node_modules/
```

### Step 4: Verify Installation

```bash
node -v  # Should be v14+
npm -v   # Should be v6+
```

## Part 2: Create Your API Client (15 min)

### Step 1: Create `src/api-client.js`

```javascript
// src/api-client.js
const axios = require('axios');

/**
 * Initialize API client
 * Uses API key from environment variables
 */
const client = axios.create({
  baseURL: 'https://api.example.com/v1',
  headers: {
    'Authorization': `Bearer ${process.env.API_KEY}`,
    'Content-Type': 'application/json'
  },
  timeout: 10000  // 10 second timeout
});

/**
 * Response interceptor for error handling
 */
client.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      console.error('Authentication failed. Check your API key.');
    } else if (error.response?.status === 429) {
      console.error('Rate limited. Wait before retrying.');
    }
    return Promise.reject(error);
  }
);

module.exports = client;
```

### Step 2: Create `src/payment-service.js`

```javascript
// src/payment-service.js
const client = require('./api-client');

class PaymentService {
  /**
   * Create a payment
   * @param {Object} params - Payment parameters
   * @returns {Promise<Object>} Payment result
   */
  static async createPayment(params) {
    const response = await client.post('/charges', {
      amount: params.amount,
      currency: params.currency || 'usd',
      description: params.description,
      metadata: params.metadata || {}
    });
    return response.data;
  }

  /**
   * Get payment details
   * @param {string} paymentId - Payment ID
   * @returns {Promise<Object>} Payment details
   */
  static async getPayment(paymentId) {
    const response = await client.get(`/charges/${paymentId}`);
    return response.data;
  }

  /**
   * List payments
   * @param {Object} options - Query options
   * @returns {Promise<Array>} List of payments
   */
  static async listPayments(options = {}) {
    const response = await client.get('/charges', { params: options });
    return response.data;
  }
}

module.exports = PaymentService;
```

## Part 3: Create Your API Server (15 min)

### Step 1: Create `src/server.js`

```javascript
// src/server.js
require('dotenv').config();
const express = require('express');
const PaymentService = require('./payment-service');

const app = express();
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * POST /api/payments
 * Create a new payment
 */
app.post('/api/payments', async (req, res) => {
  try {
    const { amount, currency, description } = req.body;

    // Validate input
    if (!amount || amount < 50) {
      return res.status(400).json({
        error: 'Amount must be at least $0.50 (50 cents)'
      });
    }

    // Create payment
    const payment = await PaymentService.createPayment({
      amount,
      currency,
      description
    });

    res.json({
      success: true,
      payment: payment
    });

  } catch (error) {
    console.error('Payment creation error:', error);

    res.status(error.response?.status || 500).json({
      error: error.response?.data?.error?.message || 'Payment failed',
      code: error.response?.data?.error?.code
    });
  }
});

/**
 * GET /api/payments/:id
 * Get payment details
 */
app.get('/api/payments/:id', async (req, res) => {
  try {
    const payment = await PaymentService.getPayment(req.params.id);
    res.json(payment);
  } catch (error) {
    res.status(404).json({ error: 'Payment not found' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV}`);
});
```

### Step 2: Update `package.json` Scripts

```json
{
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js",
    "test": "npm run test:payments"
  }
}
```

## Part 4: Test Your Integration (5 min)

### Option A: Using cURL

```bash
# Start the server
npm run dev

# In another terminal, create a payment
curl -X POST http://localhost:3000/api/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2000,
    "currency": "usd",
    "description": "Test payment"
  }'
```

### Option B: Using HTTP Client

Create `requests.rest`:

```http
### Create Payment
POST http://localhost:3000/api/payments
Content-Type: application/json

{
  "amount": 2000,
  "currency": "usd",
  "description": "Test payment"
}

### Check Health
GET http://localhost:3000/health

### Get Payment
GET http://localhost:3000/api/payments/ch_1234567890
```

Install "REST Client" extension in VS Code, then click "Send Request".

## Part 5: Production Deployment (5 min)

### Option A: Deploy to Heroku

```bash
# Create Heroku app
heroku create my-payment-app

# Set environment variables
heroku config:set API_KEY=sk_live_YOUR_API_KEY

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Option B: Deploy to Vercel

```bash
npm install -g vercel
vercel
```

## Next Steps

- Add database to store payments: [PostgreSQL Tutorial](/docs/postgresql)
- Implement webhooks: [Webhook Documentation](/docs/webhooks)
- Add authentication: [Auth Guide](/docs/authentication)
- Learn error handling: [Error Handling](/docs/errors)
- Explore advanced features: [Advanced Guide](/docs/advanced)

## Troubleshooting

**"Cannot find module 'axios'"**
```bash
npm install axios
```

**"API key not working"**
- Verify it starts with `sk_live_`
- Check it's in `.env` file
- Ensure `.env` is loaded: `require('dotenv').config()`

**"Port 3000 already in use"**
```bash
# Use different port
PORT=3001 npm run dev
```

## Complete Code Repository

Full working example: [github.com/example/getting-started](https://github.com/example/getting-started)

Clone it:
```bash
git clone https://github.com/example/getting-started
cd getting-started
npm install
cp .env.example .env
# Edit .env with your API key
npm run dev
```
