# Deployment Overview

Deploy Project to production with confidence.

## Deployment Options

- **Docker** - Containerized deployment
- **Kubernetes** - Orchestrated deployment
- **Cloud Providers** - AWS, GCP, Azure
- **On-Premise** - Self-hosted infrastructure

## Quick Start

### Docker

```bash
docker run -p 3000:3000 project/sdk:latest
```

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f deployment.yaml
```

## Environment Setup

Configure production environment:

```bash
PROJECT_ENV=production
PROJECT_API_KEY=your_key
PROJECT_LOG_LEVEL=info
```

## Monitoring

Set up monitoring and alerts:

- Health checks
- Metrics collection
- Log aggregation
- Alert rules

## See Also

- [Docker Deployment](/deployment/docker)
- [Kubernetes Deployment](/deployment/kubernetes)
- [Cloud Providers](/deployment/cloud-providers)
- [Monitoring Guide](/deployment/monitoring)
