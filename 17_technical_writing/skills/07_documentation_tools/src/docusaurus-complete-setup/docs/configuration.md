---
sidebar_position: 3
title: Configuration
description: Configure Project for your needs
---

# Configuration

Configure Project with your environment and preferences.

## Environment Variables

```bash
PROJECT_API_KEY=your_api_key_here
PROJECT_API_URL=https://api.example.com
PROJECT_ENVIRONMENT=production
PROJECT_LOG_LEVEL=info
```

## Configuration File

Create `project.config.js`:

```javascript
module.exports = {
  apiKey: process.env.PROJECT_API_KEY,
  apiUrl: process.env.PROJECT_API_URL,
  environment: process.env.PROJECT_ENVIRONMENT,
  logging: {
    level: 'info',
    format: 'json',
  },
  retry: {
    maxAttempts: 3,
    backoff: 'exponential',
  },
  timeout: 30000,
};
```

## Python Configuration

```python
import project_sdk

config = project_sdk.Config(
    api_key="your_api_key_here",
    api_url="https://api.example.com",
    environment="production",
    logging_level="info"
)

client = project_sdk.Client(config)
```

## Advanced Options

### Retry Policy
```javascript
{
  retry: {
    maxAttempts: 5,
    backoff: 'exponential',
    initialDelay: 100,
    maxDelay: 30000,
  }
}
```

### Logging
```javascript
{
  logging: {
    level: 'debug',
    format: 'json',
    destination: 'file',
    filePath: './logs/project.log',
  }
}
```

## See Also

- [Quick Start](./quick-start.md)
- [API Reference](./api/overview.md)
