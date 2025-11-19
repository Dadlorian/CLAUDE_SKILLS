# Deployment Guide

## Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Secrets stored securely
- [ ] SSL certificates installed
- [ ] Database migrations run
- [ ] RLS policies tested
- [ ] Performance tested
- [ ] Security audit completed
- [ ] Backup strategy in place

## Environment Configuration

```bash
# .env.production
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@db.example.com/analytics
REDIS_URL=redis://redis.example.com:6379

# BI Platform
TABLEAU_CLIENT_ID=xxxxx
TABLEAU_SECRET=xxxxx
POWERBI_CLIENT_ID=xxxxx
POWERBI_CLIENT_SECRET=xxxxx

# JWT
JWT_SECRET=your-very-long-random-secret-minimum-32-chars

# CDN
CDN_URL=https://cdn.example.com
```

## Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analytics
  template:
    metadata:
      labels:
        app: analytics
    spec:
      containers:
      - name: app
        image: yourregistry/analytics:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: analytics-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Database Migration

```javascript
// migrations/001_enable_rls.js
exports.up = async function(db) {
  await db.query(`
    ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

    CREATE POLICY tenant_isolation ON sales
      USING (tenant_id = current_setting('app.current_tenant')::int);
  `);
};

exports.down = async function(db) {
  await db.query(`
    DROP POLICY tenant_isolation ON sales;
    ALTER TABLE sales DISABLE ROW LEVEL SECURITY;
  `);
};
```

## Monitoring Setup

```javascript
// healthcheck.js
app.get('/health', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    biPlatform: await checkBIPlatform()
  };

  const healthy = Object.values(checks).every(c => c.status === 'ok');

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'unhealthy',
    checks,
    timestamp: new Date().toISOString()
  });
});

async function checkDatabase() {
  try {
    await db.query('SELECT 1');
    return { status: 'ok' };
  } catch (error) {
    return { status: 'error', message: error.message };
  }
}
```

## Rollback Plan

```bash
# If deployment fails, rollback:
kubectl rollout undo deployment/analytics-app

# Or with Docker
docker-compose down
git checkout previous-version
docker-compose up -d
```
