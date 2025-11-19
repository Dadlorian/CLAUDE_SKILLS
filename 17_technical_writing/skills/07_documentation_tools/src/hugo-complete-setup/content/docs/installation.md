---
title: "Installation"
description: "Install Project SDK"
weight: 10
---

# Installation

Get Project installed and ready to use.

## System Requirements

- Node.js 18+ or Python 3.9+
- npm or pip package manager
- 2GB RAM minimum
- 500MB disk space

## NPM Installation

```bash
npm install @project/sdk
```

## Python Installation

```bash
pip install project-sdk
```

## Docker Installation

```bash
docker run -it project/sdk:latest
```

## Verification

### JavaScript
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

- [Configure]({{< ref "configuration" >}}) your environment
- Follow the [Quick Start]({{< ref "quick-start" >}}) guide
- Check [API Reference]({{< ref "/api" >}})
