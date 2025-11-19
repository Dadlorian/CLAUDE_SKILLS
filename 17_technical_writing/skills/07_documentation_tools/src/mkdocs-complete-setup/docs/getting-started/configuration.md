# Configuration

Configure Project for your specific needs and environment.

## Environment Variables

```bash
PROJECT_API_KEY=your_api_key_here
PROJECT_API_URL=https://api.example.com
PROJECT_ENVIRONMENT=production
PROJECT_LOG_LEVEL=info
PROJECT_TIMEOUT=30000
```

## JavaScript Configuration

```javascript
const Project = require('@project/sdk');

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
  timeout: parseInt(process.env.PROJECT_TIMEOUT),
});
```

## Python Configuration

```python
import project_sdk

config = project_sdk.Config(
    api_key="your_api_key_here",
    api_url="https://api.example.com",
    environment="production",
    logging_level="info",
    timeout=30000
)

client = project_sdk.Client(config)
```

## Advanced Options

### Retry Policy

```javascript
retry: {
  maxAttempts: 5,
  backoff: 'exponential',
  initialDelay: 100,
  maxDelay: 30000,
}
```

### Logging Configuration

```javascript
logging: {
  level: 'debug',
  format: 'json',
  destination: 'file',
  filePath: './logs/project.log',
  rotateSize: '10M',
  retainFiles: 5
}
```

## See Also

- [Quick Start](quick-start.md)
- [API Reference](../api/overview.md)
- [Troubleshooting](../reference/faq.md)
