# Docker Deployment

Deploy Project using Docker containers.

## Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "start"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PROJECT_API_KEY=${PROJECT_API_KEY}
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## Build and Run

```bash
# Build
docker build -t project-app:latest .

# Run
docker run -p 3000:3000 project-app:latest

# With Compose
docker-compose up -d
```

## Production Checklist

- [ ] Set environment variables
- [ ] Configure logging
- [ ] Enable health checks
- [ ] Set resource limits
- [ ] Configure restart policy
- [ ] Set up monitoring
- [ ] Configure networking
- [ ] Set up backups
