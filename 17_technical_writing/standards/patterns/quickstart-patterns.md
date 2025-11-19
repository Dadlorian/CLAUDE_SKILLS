# Quickstart Patterns

## Goal

Get developers to their first successful API call in **under 10 minutes**.

---

## Quickstart Structure

### 1. **Clear Time Estimate**

```markdown
# Quickstart: Send your first message

⏱️ **Time to complete**: 5 minutes
```

### 2. **Prerequisites**

```markdown
## Prerequisites

- Node.js 18 or later
- An Example account ([sign up free](https://example.com/signup))
```

### 3. **Step-by-Step Instructions**

```markdown
## Step 1: Get your API key

1. Sign in to your [dashboard](https://example.com/dashboard)
2. Navigate to **API Keys**
3. Click **Create API Key**
4. Copy your key (starts with `sk_live_`)

## Step 2: Install the SDK

```bash
npm install @example/sdk
```

## Step 3: Send a message

Create a file `send-message.js`:

```javascript
const { ExampleClient } = require('@example/sdk');

const client = new ExampleClient(process.env.API_KEY);

async function main() {
  const message = await client.messages.create({
    to: '+15555551234',
    body: 'Hello from Example API!'
  });

  console.log(`✓ Message sent! ID: ${message.id}`);
}

main();
```

## Step 4: Run the code

```bash
export API_KEY=your_api_key_here
node send-message.js
```

**Expected output**:
```
✓ Message sent! ID: msg_1234567890
```
```

### 4. **What's Next**

```markdown
## What's next?

- [Receive messages](./receive-messages.md)
- [Handle delivery status](./delivery-status.md)
- [View full API reference](./api-reference.md)
```

---

## Best Practices

✅ **Do**:
- Use the most common use case
- Provide complete, copy-paste code
- Show expected output
- Link to next steps

❌ **Don't**:
- Require complex setup
- Explain concepts (save for guides)
- Show multiple approaches
- Include optional parameters

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Industry Examples**: Stripe, Twilio, SendGrid, Plaid
