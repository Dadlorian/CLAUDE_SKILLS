---
sidebar_position: 4
title: Quick Start
description: Get started with Project in 5 minutes
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

## 4. Verify Success

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

- Read [Core Concepts](./concepts/architecture.md)
- Explore [API Reference](./api/overview.md)
- Follow a [Tutorial](./guides/tutorial-setup.md)
- Check [Examples](https://github.com/organization/project-examples)
