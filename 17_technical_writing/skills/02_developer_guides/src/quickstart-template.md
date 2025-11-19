# API Quickstart Template

> Time: 5-10 minutes | Level: Beginner | Prerequisites: cURL or Postman installed

## What You'll Build

A complete example calling the payment API and receiving a response. This quickstart uses the simplest possible setup.

## What You'll Learn

- How to authenticate with API keys
- Make your first API request
- Handle success responses
- Understand error responses

## Step 1: Get Your API Key

1. Sign up at [example.com/signup](https://example.com/signup)
2. Go to [Settings → API Keys](https://example.com/settings/api-keys)
3. Click "Create New Key"
4. Copy the key (starts with `sk_live_`)

## Step 2: Make Your First Request

### Using cURL

```bash
curl -X POST https://api.example.com/v1/charges \
  -H "Authorization: Bearer sk_live_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2000,
    "currency": "usd",
    "description": "Test charge"
  }'
```

### Using Postman

1. Create new POST request
2. URL: `https://api.example.com/v1/charges`
3. In Headers:
   - Key: `Authorization`
   - Value: `Bearer sk_live_YOUR_API_KEY`
4. In Body (JSON):
```json
{
  "amount": 2000,
  "currency": "usd",
  "description": "Test charge"
}
```
5. Click Send

## Step 3: Check Your Response

You should see:

```json
{
  "id": "ch_1234567890",
  "status": "succeeded",
  "amount": 2000,
  "currency": "usd",
  "description": "Test charge"
}
```

Success! You've made your first API call.

## Next Steps

- Read the [full API documentation](/docs/api-reference)
- Learn about [authentication](/docs/authentication)
- Explore [error handling](/docs/errors)
- See [code samples](/docs/code-samples) in your language

## Troubleshooting

**Error: "Unauthorized"**
- Check that your API key starts with `sk_live_`
- Verify you copied the entire key
- Don't include the Bearer prefix in the key itself

**Error: "Invalid request"**
- Ensure amount is in cents (2000 = $20.00)
- Currency must be lowercase (usd, eur, gbp)
- Check JSON formatting

**Error: "Rate limited"**
- You've exceeded 100 requests/second
- Wait 1 minute before retrying
- See [rate limits](/docs/rate-limits) for upgrade options

## Complete Working Examples

See `/examples/quickstart-complete.js` and `/examples/quickstart-complete.py` for production-ready implementations.
