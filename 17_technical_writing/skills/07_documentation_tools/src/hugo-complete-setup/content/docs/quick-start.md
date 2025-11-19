---
title: "Quick Start"
description: "Get started in 5 minutes"
weight: 30
---

# Quick Start

Get started with Project in just a few minutes.

## 1. Install

```bash npm2yarn
npm install @project/sdk
```

## 2. Initialize

```javascript
const Project = require('@project/sdk');

const client = new Project.Client({
  apiKey: 'your_api_key_here',
});
```

## 3. Make Your First Request

```javascript
async function main() {
  try {
    const user = await client.users.create({
      name: 'John Doe',
      email: 'john@example.com',
    });
    console.log('User created:', user);
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```

## 4. Success

You should see output like:

```json
{
  "id": "user_123abc",
  "name": "John Doe",
  "email": "john@example.com",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

## Next Steps

- Read [Core Concepts]({{< ref "architecture" >}})
- Explore [API Reference]({{< ref "/api" >}})
- Check [Guides]({{< ref "/guides" >}})
