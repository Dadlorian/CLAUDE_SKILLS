# Configuration

Configure Project for your environment.

## Environment Variables

```bash
PROJECT_API_KEY=your_api_key_here
PROJECT_API_URL=https://api.example.com
PROJECT_ENVIRONMENT=production
PROJECT_LOG_LEVEL=info
```

## JavaScript Configuration

```javascript
import Project from '@project/sdk'

const client = new Project.Client({
  apiKey: process.env.PROJECT_API_KEY,
  apiUrl: process.env.PROJECT_API_URL,
  environment: process.env.PROJECT_ENVIRONMENT,
  logging: {
    level: process.env.PROJECT_LOG_LEVEL,
    format: 'json',
  },
  retry: {
    maxAttempts: 3,
    backoff: 'exponential',
  },
})
```

## Python Configuration

```python
import project_sdk

config = project_sdk.Config(
    api_key="your_api_key_here",
    api_url="https://api.example.com",
    environment="production",
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
