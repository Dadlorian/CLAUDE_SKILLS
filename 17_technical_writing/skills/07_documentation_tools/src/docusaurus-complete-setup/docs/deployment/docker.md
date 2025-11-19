---
sidebar_position: 2
title: Docker Deployment
description: Deploy with Docker
---

# Docker Deployment

Deploy Project using Docker containers.

## Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build documentation
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD node healthcheck.js

# Start server
CMD ["npm", "run", "serve"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  docs:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - docs
```

## Build and Run

```bash
# Build image
docker build -t project-docs:latest .

# Run container
docker run -p 3000:3000 project-docs:latest

# With Docker Compose
docker-compose up -d
```

## Environment Variables

```bash
NODE_ENV=production
LOG_LEVEL=info
API_ENDPOINT=https://api.example.com
```
