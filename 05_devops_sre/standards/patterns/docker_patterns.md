# Docker Patterns and Best Practices

## Overview

This guide covers Docker best practices, multi-stage builds, layer optimization, and container design patterns based on official Docker guidelines and Google Container Tools best practices.

## Table of Contents

1. [Multi-Stage Build Patterns](#multi-stage-build-patterns)
2. [Layer Optimization](#layer-optimization)
3. [Image Size Optimization](#image-size-optimization)
4. [Build Cache Optimization](#build-cache-optimization)
5. [Container Design Patterns](#container-design-patterns)
6. [Health Check Patterns](#health-check-patterns)
7. [Logging Patterns](#logging-patterns)
8. [Configuration Management](#configuration-management)

---

## Multi-Stage Build Patterns

### Why Multi-Stage Builds?

Multi-stage builds allow you to:
- Separate build-time and runtime dependencies
- Reduce final image size dramatically
- Improve security by excluding build tools
- Create more maintainable Dockerfiles

### Basic Multi-Stage Pattern

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /build
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

### Builder Pattern with Dependency Caching

```dockerfile
# Stage 1: Dependencies
FROM golang:1.21-alpine AS dependencies
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download

# Stage 2: Build
FROM dependencies AS builder
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server

# Stage 3: Runtime
FROM alpine:3.18
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/server /usr/local/bin/server
USER nobody
ENTRYPOINT ["server"]
```

### Testing Stage Pattern

```dockerfile
# Base dependencies
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Testing stage (not included in final image)
FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN pytest tests/ && \
    pylint src/ && \
    black --check src/

# Production stage
FROM base AS production
COPY src/ ./src/
USER nobody
CMD ["python", "-m", "src.main"]
```

---

## Layer Optimization

### Principles

1. **Order Matters**: Place less frequently changing commands first
2. **Combine Commands**: Use `&&` to reduce layers
3. **Clean Up**: Remove temporary files in the same layer
4. **Use .dockerignore**: Prevent unnecessary context uploads

### Good Layer Ordering

```dockerfile
FROM node:18-alpine

# 1. Install system dependencies (rarely changes)
RUN apk add --no-cache dumb-init

# 2. Set working directory
WORKDIR /app

# 3. Copy dependency files (changes less frequently)
COPY package*.json ./

# 4. Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# 5. Copy application code (changes most frequently)
COPY . .

# 6. Runtime configuration
USER node
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "index.js"]
```

### Bad Layer Ordering

```dockerfile
FROM node:18-alpine

# Anti-pattern: Copying everything first
COPY . .

# This invalidates cache even if only app code changes
RUN npm install

# Missing cleanup, leaving cache in layer
RUN npm cache clean --force

CMD ["node", "index.js"]
```

### Cleanup in Same Layer

```dockerfile
# Good: Clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Bad: Cleanup in separate layer (doesn't reduce size)
RUN apt-get update
RUN apt-get install -y curl ca-certificates
RUN rm -rf /var/lib/apt/lists/*  # Too late, already in previous layer
```

---

## Image Size Optimization

### Use Minimal Base Images

```dockerfile
# Option 1: Alpine (smallest, but may have compatibility issues)
FROM python:3.11-alpine  # ~50MB

# Option 2: Slim (good balance)
FROM python:3.11-slim    # ~120MB

# Option 3: Distroless (Google's minimal images)
FROM gcr.io/distroless/python3  # ~50MB, production-ready

# Avoid: Full images unless necessary
FROM python:3.11         # ~900MB
```

### Multi-Stage Size Reduction

```dockerfile
# Build stage with full toolchain
FROM rust:1.73 AS builder
WORKDIR /build
COPY . .
RUN cargo build --release

# Minimal runtime image
FROM gcr.io/distroless/cc-debian12
COPY --from=builder /build/target/release/myapp /app/myapp
ENTRYPOINT ["/app/myapp"]
```

### Remove Build Dependencies

```dockerfile
FROM debian:bookworm-slim

# Install build deps, build, then remove build deps in single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev && \
    pip install --no-cache-dir cryptography && \
    apt-get purge -y --auto-remove \
        build-essential \
        python3-dev && \
    rm -rf /var/lib/apt/lists/*
```

---

## Build Cache Optimization

### Leverage BuildKit Cache Mounts

```dockerfile
# syntax=docker/dockerfile:1.4

FROM golang:1.21-alpine

# Cache Go modules
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

# Cache build artifacts
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go build -o /app/server
```

### Cache npm/pip Dependencies

```dockerfile
# syntax=docker/dockerfile:1.4

FROM node:18-alpine

WORKDIR /app

# Use cache mount for npm
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    npm ci --prefer-offline

COPY . .
```

### Bind Mounts for Context Efficiency

```dockerfile
# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

# Only mount requirements for installation
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY src/ /app/src/
```

---

## Container Design Patterns

### Single Responsibility Principle

Each container should have one primary concern:

```yaml
# Good: Separate concerns
services:
  web:
    image: myapp:web
    # Only runs web server

  worker:
    image: myapp:worker
    # Only runs background jobs

  scheduler:
    image: myapp:scheduler
    # Only runs scheduled tasks

# Bad: Monolithic container
services:
  app:
    image: myapp:all
    # Runs web + worker + scheduler + cron
```

### Sidecar Pattern

```yaml
# Main application container
app:
  image: myapp:latest

# Sidecar for logging
log-forwarder:
  image: fluent-bit:latest
  volumes:
    - app-logs:/logs

# Sidecar for metrics
metrics-exporter:
  image: prometheus-exporter:latest
```

### Init Container Pattern

```dockerfile
# Stage 1: Database migration
FROM myapp:base AS migrator
COPY migrations/ /migrations/
ENTRYPOINT ["migrate", "-path", "/migrations", "-database", "$DB_URL", "up"]

# Stage 2: Application
FROM myapp:base AS app
COPY src/ /app/
ENTRYPOINT ["./app"]
```

### Ambassador Pattern

```yaml
# Application connects to localhost
app:
  image: myapp:latest
  environment:
    - DATABASE_HOST=localhost

# Ambassador handles external connection
db-proxy:
  image: cloud-sql-proxy:latest
  command: /cloud_sql_proxy -instances=project:region:instance=tcp:0.0.0.0:5432
  network_mode: service:app
```

---

## Health Check Patterns

### HTTP Health Check

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY . .

# Install curl for health checks
RUN apk add --no-cache curl

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

### TCP Health Check

```dockerfile
FROM python:3.11-slim

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 8000)); s.close()" || exit 1

CMD ["python", "app.py"]
```

### Script-Based Health Check

```dockerfile
FROM golang:1.21-alpine

COPY health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["/usr/local/bin/health-check.sh"]

CMD ["./app"]
```

### Multi-Dependency Health Check

```bash
#!/bin/sh
# health-check.sh

# Check application
curl -f http://localhost:8080/health || exit 1

# Check database connection
pg_isready -h db -p 5432 || exit 1

# Check Redis connection
redis-cli -h redis ping || exit 1

exit 0
```

---

## Logging Patterns

### Log to STDOUT/STDERR

```dockerfile
FROM node:18-alpine

# Ensure logs go to stdout/stderr (best practice)
RUN ln -sf /dev/stdout /var/log/app.log && \
    ln -sf /dev/stderr /var/log/app.error.log

# Application logs to stdout
CMD ["node", "server.js"]
```

### Structured Logging

```python
# app.py
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        })

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.handlers[0].setFormatter(JsonFormatter())
```

### Log Rotation for Local Development

```dockerfile
FROM node:18-alpine

# Only for development, not production
RUN apk add --no-cache logrotate

COPY logrotate.conf /etc/logrotate.d/app

CMD ["node", "server.js"]
```

---

## Configuration Management

### Environment Variables

```dockerfile
FROM python:3.11-slim

# Set default environment variables
ENV APP_ENV=production \
    LOG_LEVEL=info \
    PORT=8000

# Allow runtime override
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "${PORT}"]
```

### Build Arguments vs Environment Variables

```dockerfile
FROM node:18-alpine

# Build-time argument (not available at runtime)
ARG NODE_ENV=production

# Convert to environment variable if needed at runtime
ENV NODE_ENV=${NODE_ENV}

RUN if [ "$NODE_ENV" = "production" ]; then \
        npm ci --only=production; \
    else \
        npm install; \
    fi

COPY . .
```

### Configuration Files

```dockerfile
FROM nginx:alpine

# Copy default configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Allow runtime configuration override via volume mount
# docker run -v $(pwd)/custom-nginx.conf:/etc/nginx/nginx.conf nginx:custom

EXPOSE 80
```

### Secrets Management

```dockerfile
FROM python:3.11-slim

# NEVER: Hardcode secrets
# ENV DATABASE_PASSWORD=supersecret  # ❌ BAD

# GOOD: Expect secrets from environment or secret management
# docker run -e DATABASE_PASSWORD="$(cat /path/to/secret)" app:latest
# or
# docker run --secret db-password app:latest

# Mount secrets (BuildKit)
RUN --mount=type=secret,id=db-password \
    export DB_PASSWORD=$(cat /run/secrets/db-password) && \
    # Use password during build if needed
    echo "Connected to database"

CMD ["python", "app.py"]
```

---

## Performance Patterns

### Parallel Builds

```dockerfile
FROM golang:1.21-alpine AS base
WORKDIR /src

# Download dependencies (can be cached)
FROM base AS dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build service 1
FROM dependencies AS build-service1
COPY service1/ ./service1/
RUN go build -o /out/service1 ./service1

# Build service 2 (parallel with service1)
FROM dependencies AS build-service2
COPY service2/ ./service2/
RUN go build -o /out/service2 ./service2

# Final image with both services
FROM alpine:3.18
COPY --from=build-service1 /out/service1 /usr/local/bin/
COPY --from=build-service2 /out/service2 /usr/local/bin/
```

### Concurrent Dependency Installation

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy all package files
COPY package*.json lerna.json ./
COPY packages/*/package.json ./packages/

# Install all dependencies concurrently
RUN npm ci --workspaces --if-present

COPY . .
RUN npm run build --workspaces
```

---

## Production-Ready Patterns

### Complete Production Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.4

# Build stage
FROM node:18-alpine AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++

WORKDIR /build

# Cache dependencies
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# Build application
COPY . .
RUN npm run build && \
    npm prune --production

# Production stage
FROM node:18-alpine

# Install production runtime dependencies
RUN apk add --no-cache \
    dumb-init \
    curl \
    ca-certificates && \
    addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app

# Copy built application
COPY --from=builder --chown=appuser:appgroup /build/dist ./dist
COPY --from=builder --chown=appuser:appgroup /build/node_modules ./node_modules
COPY --chown=appuser:appgroup package.json ./

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Security
USER appuser
EXPOSE 3000

# Proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]

# Metadata
LABEL org.opencontainers.image.title="MyApp" \
      org.opencontainers.image.description="Production-ready Node.js application" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="MyCompany"
```

---

## Anti-Patterns to Avoid

### ❌ Running as Root

```dockerfile
# BAD
FROM node:18
COPY . .
CMD ["node", "app.js"]  # Runs as root!

# GOOD
FROM node:18
COPY . .
USER node
CMD ["node", "app.js"]
```

### ❌ Using Latest Tag

```dockerfile
# BAD
FROM node:latest  # Unpredictable, breaks reproducibility

# GOOD
FROM node:18.17.1-alpine3.18  # Specific, reproducible
```

### ❌ Installing Unnecessary Packages

```dockerfile
# BAD
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    vim \
    emacs \
    nano \
    curl \
    wget \
    git

# GOOD
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*
```

### ❌ Storing Secrets in Images

```dockerfile
# BAD
FROM python:3.11
ENV API_KEY=sk-1234567890abcdef  # ❌ Visible in image history!

# GOOD
FROM python:3.11
# Pass at runtime: docker run -e API_KEY=secret app
```

### ❌ Large Build Context

```bash
# BAD: No .dockerignore, uploads everything
docker build .  # Uploads node_modules, .git, etc.

# GOOD: Use .dockerignore
echo "node_modules
.git
*.log
.env" > .dockerignore
```

---

## References

- [Docker Official Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Google Container Best Practices](https://cloud.google.com/architecture/best-practices-for-building-containers)
- [Docker BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
