# Setting Up Backstage: Complete Deployment Guide

## Overview

This guide walks through deploying Spotify Backstage in production, from initial setup to full production deployment with authentication, plugins, and integrations.

## Prerequisites

### Required Tools

```bash
# Node.js 18 or later
node --version  # v18.x or later

# Yarn package manager
yarn --version  # 1.22.x or later

# Docker for local development
docker --version

# Git
git --version

# kubectl for Kubernetes deployment
kubectl version --client
```

### Infrastructure Requirements

```yaml
Development:
  compute: 2 CPU, 4GB RAM
  database: PostgreSQL 12+

Production:
  compute:
    frontend: 2-4 instances, 2 CPU, 4GB RAM each
    backend: 3-6 instances, 4 CPU, 8GB RAM each
  database:
    postgres: RDS/CloudSQL, Multi-AZ, 8GB+ RAM
  storage:
    techdocs: S3/GCS bucket
    artifacts: Container registry
  networking:
    load_balancer: ALB/Cloud Load Balancer
    cdn: CloudFront/Cloud CDN (optional)
```

## Quick Start (Local Development)

### Step 1: Create Backstage App

```bash
# Create a new Backstage app
npx @backstage/create-app@latest

# Follow the prompts:
# ? Enter a name for the app [required] my-backstage-app
# ? Select database for the backend [required] PostgreSQL

cd my-backstage-app
```

### Step 2: Start Local Development

```bash
# Install dependencies
yarn install

# Start PostgreSQL (using Docker)
docker run --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=backstage \
  -p 5432:5432 \
  -d postgres:15

# Start Backstage
yarn dev
```

Backstage will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:7007

## Configuration

### Step 1: Basic Configuration

```yaml
# app-config.yaml
app:
  title: Company Developer Portal
  baseUrl: http://localhost:3000

organization:
  name: Company Name

backend:
  baseUrl: http://localhost:7007
  listen:
    port: 7007
    host: 0.0.0.0

  csp:
    connect-src: ["'self'", 'http:', 'https:']
    upgrade-insecure-requests: false

  cors:
    origin: http://localhost:3000
    methods: [GET, HEAD, PATCH, POST, PUT, DELETE]
    credentials: true

  database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      port: ${POSTGRES_PORT}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}
      ssl:
        rejectUnauthorized: false

  cache:
    store: memory
```

### Step 2: Authentication Setup

#### GitHub OAuth

```bash
# 1. Create GitHub OAuth App at:
# https://github.com/settings/applications/new

# Settings:
# Homepage URL: http://localhost:3000
# Authorization callback URL: http://localhost:7007/api/auth/github/handler/frame
```

```yaml
# app-config.yaml
auth:
  environment: development
  providers:
    github:
      development:
        clientId: ${AUTH_GITHUB_CLIENT_ID}
        clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}
        signIn:
          resolvers:
            # Match GitHub username to Backstage user entity
            - resolver: usernameMatchingUserEntityName
```

```typescript
// packages/app/src/App.tsx
import { githubAuthApiRef } from '@backstage/core-plugin-api';
import { SignInPage } from '@backstage/core-components';

const app = createApp({
  components: {
    SignInPage: props => (
      <SignInPage
        {...props}
        auto
        provider={{
          id: 'github-auth-provider',
          title: 'GitHub',
          message: 'Sign in using GitHub',
          apiRef: githubAuthApiRef,
        }}
      />
    ),
  },
});
```

#### Google OAuth

```yaml
# app-config.yaml
auth:
  providers:
    google:
      development:
        clientId: ${AUTH_GOOGLE_CLIENT_ID}
        clientSecret: ${AUTH_GOOGLE_CLIENT_SECRET}
        signIn:
          resolvers:
            - resolver: emailMatchingUserEntityProfileEmail
```

#### Okta SAML

```yaml
# app-config.yaml
auth:
  providers:
    okta:
      development:
        clientId: ${AUTH_OKTA_CLIENT_ID}
        clientSecret: ${AUTH_OKTA_CLIENT_SECRET}
        audience: ${AUTH_OKTA_AUDIENCE}
```

### Step 3: Catalog Configuration

#### Static Location

```yaml
# app-config.yaml
catalog:
  import:
    entityFilename: catalog-info.yaml
    pullRequestBranchName: backstage-integration

  rules:
    - allow: [Component, System, API, Resource, Location, Group, User, Domain]

  locations:
    # Local example data
    - type: file
      target: ../../examples/entities.yaml

    # Organization data
    - type: url
      target: https://github.com/company/platform/blob/main/catalog/all.yaml
      rules:
        - allow: [User, Group, System, Domain]
```

#### GitHub Discovery

```yaml
# app-config.yaml
catalog:
  providers:
    github:
      companyOrg:
        organization: 'company-org'
        catalogPath: '/catalog-info.yaml'
        filters:
          branch: 'main'
          repository: '.*'
        schedule:
          frequency: { minutes: 30 }
          timeout: { minutes: 3 }
          initialDelay: { seconds: 15 }

integrations:
  github:
    - host: github.com
      token: ${GITHUB_TOKEN}
```

```typescript
// packages/backend/src/plugins/catalog.ts
import { GithubDiscoveryProcessor } from '@backstage/plugin-catalog-backend-module-github';

export default async function createPlugin(
  env: PluginEnvironment,
): Promise<Router> {
  const builder = await CatalogBuilder.create(env);

  builder.addProcessor(
    GithubDiscoveryProcessor.fromConfig(env.config, {
      logger: env.logger,
    }),
  );

  const { processingEngine, router } = await builder.build();
  await processingEngine.start();

  return router;
}
```

#### Example Catalog Entities

```yaml
# catalog/all.yaml
---
apiVersion: backstage.io/v1alpha1
kind: Location
metadata:
  name: systems
  description: Systems in our organization
spec:
  targets:
    - ./systems/*.yaml

---
apiVersion: backstage.io/v1alpha1
kind: Location
metadata:
  name: components
  description: All components
spec:
  targets:
    - https://github.com/company-org/*/blob/main/catalog-info.yaml
```

```yaml
# catalog/systems/ecommerce.yaml
---
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: ecommerce
  description: E-commerce platform
spec:
  owner: ecommerce-team
  domain: retail

---
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: product-catalog-api
  description: Product catalog API service
  annotations:
    github.com/project-slug: company-org/product-catalog-api
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: ecommerce-team
  system: ecommerce
  providesApis:
    - product-api
  consumesApis:
    - inventory-api

---
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: product-api
  description: Product catalog REST API
spec:
  type: openapi
  lifecycle: production
  owner: ecommerce-team
  system: ecommerce
  definition:
    $text: https://github.com/company-org/product-catalog-api/blob/main/openapi.yaml
```

### Step 4: TechDocs Setup

#### S3 Publisher

```yaml
# app-config.yaml
techdocs:
  builder: 'external'
  generator:
    runIn: 'docker'
  publisher:
    type: 'awsS3'
    awsS3:
      bucketName: ${TECHDOCS_S3_BUCKET}
      region: ${AWS_REGION}
      credentials:
        accessKeyId: ${AWS_ACCESS_KEY_ID}
        secretAccessKey: ${AWS_SECRET_ACCESS_KEY}
```

#### CI/CD Integration

```yaml
# .gitlab-ci.yml
techdocs:
  stage: docs
  image: spotify/techdocs
  script:
    - npx @techdocs/cli generate --source-dir . --output-dir ./site
    - npx @techdocs/cli publish --publisher-type awsS3 --storage-name $TECHDOCS_S3_BUCKET --entity default/component/my-service
  only:
    - main
```

## Plugin Installation

### Installing Core Plugins

```bash
# Kubernetes plugin
yarn workspace app add @backstage/plugin-kubernetes
yarn workspace backend add @backstage/plugin-kubernetes-backend

# ArgoCD plugin
yarn workspace app add @roadiehq/backstage-plugin-argo-cd

# PagerDuty plugin
yarn workspace app add @pagerduty/backstage-plugin

# Datadog plugin
yarn workspace app add @roadiehq/backstage-plugin-datadog
```

### Kubernetes Plugin Setup

```yaml
# app-config.yaml
kubernetes:
  serviceLocatorMethod:
    type: 'multiTenant'
  clusterLocatorMethods:
    - type: 'config'
      clusters:
        - url: https://kubernetes.default.svc
          name: production
          authProvider: 'serviceAccount'
          skipTLSVerify: false
          skipMetricsLookup: false
          serviceAccountToken: ${K8S_TOKEN}
          dashboardUrl: https://k8s-dashboard.company.com
          dashboardApp: standard
```

```typescript
// packages/app/src/components/catalog/EntityPage.tsx
import { EntityKubernetesContent } from '@backstage/plugin-kubernetes';

const serviceEntityPage = (
  <EntityLayout>
    <EntityLayout.Route path="/kubernetes" title="Kubernetes">
      <EntityKubernetesContent />
    </EntityLayout.Route>
  </EntityLayout>
);
```

### CI/CD Plugin Setup (GitHub Actions)

```typescript
// packages/app/src/components/catalog/EntityPage.tsx
import {
  EntityGithubActionsContent,
  isGithubActionsAvailable,
} from '@backstage/plugin-github-actions';

const cicdContent = (
  <EntitySwitch>
    <EntitySwitch.Case if={isGithubActionsAvailable}>
      <EntityGithubActionsContent />
    </EntitySwitch.Case>
  </EntitySwitch>
);
```

## Production Deployment

### Step 1: Build Production Artifacts

```bash
# Build frontend and backend
yarn build:all

# Build Docker images
yarn build-image --tag company/backstage:1.0.0
```

### Step 2: Docker Configuration

```dockerfile
# Dockerfile
FROM node:18-bullseye-slim AS build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 g++ build-essential && \
    yarn config set python /usr/bin/python3

USER node
WORKDIR /app

# Copy package files
COPY --chown=node:node yarn.lock package.json packages/backend/dist/skeleton.tar.gz ./
RUN tar xzf skeleton.tar.gz && rm skeleton.tar.gz

# Install production dependencies
RUN yarn install --frozen-lockfile --production --network-timeout 600000

# Copy built backend
COPY --chown=node:node packages/backend/dist/bundle.tar.gz ./
RUN tar xzf bundle.tar.gz && rm bundle.tar.gz

# Runtime image
FROM node:18-bullseye-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 && \
    rm -rf /var/lib/apt/lists/*

USER node
WORKDIR /app

COPY --from=build --chown=node:node /app /app

CMD ["node", "packages/backend", "--config", "app-config.yaml"]
```

### Step 3: Kubernetes Deployment

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: backstage
```

```yaml
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: backstage-secrets
  namespace: backstage
type: Opaque
stringData:
  POSTGRES_HOST: postgres.backstage.svc.cluster.local
  POSTGRES_PORT: "5432"
  POSTGRES_USER: backstage
  POSTGRES_PASSWORD: <password>
  GITHUB_TOKEN: <token>
  AUTH_GITHUB_CLIENT_ID: <client-id>
  AUTH_GITHUB_CLIENT_SECRET: <client-secret>
```

```yaml
# kubernetes/postgres.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: backstage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: backstage
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: backstage-secrets
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: backstage-secrets
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_DB
              value: backstage
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: backstage
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

```yaml
# kubernetes/backstage.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backstage
  namespace: backstage
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backstage
  template:
    metadata:
      labels:
        app: backstage
    spec:
      serviceAccountName: backstage
      containers:
        - name: backstage
          image: company/backstage:1.0.0
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 7007
          envFrom:
            - secretRef:
                name: backstage-secrets
          env:
            - name: APP_CONFIG_app_baseUrl
              value: https://backstage.company.com
            - name: APP_CONFIG_backend_baseUrl
              value: https://backstage.company.com
          livenessProbe:
            httpGet:
              path: /healthcheck
              port: 7007
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /healthcheck
              port: 7007
            initialDelaySeconds: 30
            periodSeconds: 10
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backstage
  namespace: backstage
spec:
  selector:
    app: backstage
  ports:
    - name: http
      port: 80
      targetPort: 7007
  type: ClusterIP
```

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backstage
  namespace: backstage
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - backstage.company.com
      secretName: backstage-tls
  rules:
    - host: backstage.company.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: backstage
                port:
                  number: 80
```

```yaml
# kubernetes/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backstage
  namespace: backstage
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: backstage-read
rules:
  - apiGroups:
      - '*'
    resources:
      - pods
      - deployments
      - replicasets
      - services
      - ingresses
    verbs:
      - get
      - list
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: backstage-read
subjects:
  - kind: ServiceAccount
    name: backstage
    namespace: backstage
roleRef:
  kind: ClusterRole
  name: backstage-read
  apiGroup: rbac.authorization.k8s.io
```

### Step 4: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create secrets
kubectl apply -f kubernetes/secrets.yaml

# Deploy PostgreSQL
kubectl apply -f kubernetes/postgres.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n backstage --timeout=300s

# Deploy Backstage
kubectl apply -f kubernetes/serviceaccount.yaml
kubectl apply -f kubernetes/backstage.yaml
kubectl apply -f kubernetes/ingress.yaml

# Check deployment status
kubectl get pods -n backstage
kubectl logs -f deployment/backstage -n backstage
```

### Step 5: Helm Chart (Alternative)

```yaml
# values.yaml
backstage:
  image:
    repository: company/backstage
    tag: 1.0.0

  replicas: 3

  resources:
    requests:
      memory: 2Gi
      cpu: 1000m
    limits:
      memory: 4Gi
      cpu: 2000m

  ingress:
    enabled: true
    host: backstage.company.com
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod

postgresql:
  enabled: true
  auth:
    username: backstage
    password: <password>
    database: backstage
  primary:
    persistence:
      size: 20Gi

config:
  app:
    baseUrl: https://backstage.company.com
  backend:
    baseUrl: https://backstage.company.com
```

```bash
# Install with Helm
helm repo add backstage https://backstage.github.io/charts
helm install backstage backstage/backstage -f values.yaml -n backstage
```

## High Availability Setup

### Multiple Regions

```yaml
# Multi-region deployment
regions:
  us-east-1:
    backstage:
      replicas: 3
    database:
      primary: true
      replicas: 2

  eu-west-1:
    backstage:
      replicas: 3
    database:
      read_replica: true
      replicas: 2

global_load_balancer:
  type: Route53
  health_checks: enabled
  failover: automatic
```

### Database HA

```yaml
# AWS RDS Multi-AZ
database:
  engine: postgres
  version: "15"
  instance_class: db.r6g.xlarge
  multi_az: true
  backup:
    retention_period: 7
    preferred_window: "03:00-04:00"
  monitoring:
    enhanced: true
    interval: 60
```

## Monitoring and Observability

### Prometheus Metrics

```yaml
# kubernetes/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backstage
  namespace: backstage
spec:
  selector:
    matchLabels:
      app: backstage
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Backstage Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"backstage\"}[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"backstage\",status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{job=\"backstage\"}[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### Common Issues

```bash
# Check pod status
kubectl get pods -n backstage
kubectl describe pod <pod-name> -n backstage

# View logs
kubectl logs -f deployment/backstage -n backstage

# Check database connection
kubectl exec -it deployment/backstage -n backstage -- \
  psql -h postgres -U backstage -d backstage -c "SELECT version();"

# Test backend health
kubectl exec -it deployment/backstage -n backstage -- \
  curl http://localhost:7007/healthcheck

# Check secrets
kubectl get secrets -n backstage
kubectl describe secret backstage-secrets -n backstage
```

### Performance Tuning

```yaml
# Increase worker processes
backend:
  listen:
    port: 7007
  database:
    connection:
      pool:
        min: 5
        max: 20

# Enable caching
backend:
  cache:
    store: redis
    connection: redis://redis:6379
    ttl: 600
```

## Maintenance

### Backup Strategy

```bash
# Database backup
kubectl exec deployment/postgres -n backstage -- \
  pg_dump -U backstage backstage > backup-$(date +%Y%m%d).sql

# Restore
kubectl exec -i deployment/postgres -n backstage -- \
  psql -U backstage backstage < backup-20240101.sql
```

### Upgrade Process

```bash
# 1. Backup database
# 2. Update image tag
kubectl set image deployment/backstage \
  backstage=company/backstage:1.1.0 \
  -n backstage

# 3. Monitor rollout
kubectl rollout status deployment/backstage -n backstage

# 4. Rollback if needed
kubectl rollout undo deployment/backstage -n backstage
```

## Security Hardening

### Network Policies

```yaml
# kubernetes/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backstage
  namespace: backstage
spec:
  podSelector:
    matchLabels:
      app: backstage
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 7007
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 443
```

### Pod Security Policy

```yaml
# kubernetes/podsecuritypolicy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: backstage
spec:
  privileged: false
  allowPrivilegeEscalation: false
  runAsUser:
    rule: MustRunAsNonRoot
  fsGroup:
    rule: RunAsAny
  volumes:
    - 'configMap'
    - 'secret'
    - 'persistentVolumeClaim'
```

## Resources

- Backstage Documentation: https://backstage.io/docs
- Kubernetes Guide: https://backstage.io/docs/deployment/k8s
- Docker Guide: https://backstage.io/docs/deployment/docker
- Helm Charts: https://github.com/backstage/charts
