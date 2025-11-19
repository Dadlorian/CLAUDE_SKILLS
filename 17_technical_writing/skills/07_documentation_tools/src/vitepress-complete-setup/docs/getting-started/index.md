# Getting Started

Welcome! Let's get you started with Project in minutes.

## Installation

Install Project using your preferred package manager:

```bash npm2yarn
npm install @project/sdk
```

## Configuration

Set up your API credentials:

```bash
export PROJECT_API_KEY=your_api_key_here
export PROJECT_API_URL=https://api.example.com
```

## Quick Start

Make your first request:

```javascript
import Project from '@project/sdk'

const client = new Project.Client({
  apiKey: process.env.PROJECT_API_KEY,
})

async function main() {
  const user = await client.users.create({
    name: 'John Doe',
    email: 'john@example.com',
  })
  console.log('User created:', user)
}

main()
```

## Next Steps

- [Explore API Reference](/api/overview)
- [Read Guides](/guides/rest-integration)
- [Check Deployment Options](/deployment/overview)

:::info
Need help? Join our [Discord community](https://discord.gg/example)
:::
