---
sidebar_position: 2
title: Installation
description: Install Project and get started
---

# Installation

Get Project up and running on your system.

## System Requirements

- Node.js 18+ or Python 3.9+
- npm or pip package manager
- 2GB RAM minimum
- 500MB disk space

## NPM Installation

```bash npm2yarn
npm install @project/sdk
```

## Python Installation

```bash
pip install project-sdk
```

## Docker Installation

```dockerfile
FROM node:18-alpine
WORKDIR /app
RUN npm install @project/sdk
```

Run with Docker:

```bash
docker run -it project-sdk:latest
```

## Verification

Verify your installation:

### Node.js
```javascript
const Project = require('@project/sdk');
console.log(Project.version);
// Output: 1.0.0
```

### Python
```python
import project_sdk
print(project_sdk.__version__)
# Output: 1.0.0
```

## Next Steps

- [Configure](./configuration.md) your environment
- Follow the [Quick Start](./quick-start.md) guide
- Check [API Reference](./api/overview.md)
