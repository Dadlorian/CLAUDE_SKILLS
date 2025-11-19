# Backstage Reference Guide

## Overview

Backstage is Spotify's open-source platform for building developer portals. It provides a unified frontend for all your infrastructure tooling, services, and documentation.

## Core Concepts

### Software Catalog

The catalog is the heart of Backstage, containing metadata about all software in your ecosystem.

#### Entity Types

1. **Component**
   - Services, websites, libraries
   - Has ownership and lifecycle
   - Can have dependencies

2. **API**
   - REST, GraphQL, gRPC, etc.
   - Describes interfaces between components
   - Versioned and documented

3. **Resource**
   - Databases, S3 buckets, CDN
   - Infrastructure dependencies
   - Managed by components

4. **System**
   - Collection of components and resources
   - Represents a product or platform
   - Organizational unit

5. **Domain**
   - Collection of systems
   - Business area or capability
   - Top-level organizational unit

6. **Group**
   - Teams and organizational units
   - Ownership mapping
   - Access control

7. **User**
   - Individual developers
   - Group membership
   - Identity mapping

### Software Templates

Scaffolder templates enable self-service creation of new software projects.

#### Template Structure

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: react-app-template
  title: React Application
  description: Create a new React application
spec:
  owner: platform-team
  type: service

  parameters:
    - title: Fill in some steps
      required:
        - name
      properties:
        name:
          title: Name
          type: string
          description: Unique name of the component
        description:
          title: Description
          type: string
          description: Help others understand what this service does

  steps:
    - id: fetch-base
      name: Fetch Base
      action: fetch:template
      input:
        url: ./template
        values:
          name: ${{ parameters.name }}

    - id: publish
      name: Publish
      action: publish:github
      input:
        allowedHosts: ['github.com']
        description: ${{ parameters.description }}
        repoUrl: ${{ parameters.repoUrl }}

    - id: register
      name: Register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: '/catalog-info.yaml'

  output:
    links:
      - title: Repository
        url: ${{ steps.publish.output.remoteUrl }}
      - title: Open in catalog
        icon: catalog
        entityRef: ${{ steps.register.output.entityRef }}
```

### TechDocs

TechDocs is Spotify's approach to documentation: "docs like code."

#### Features

- Markdown-based documentation
- Stored with code
- Automated builds
- Version control
- Search integration

## Architecture

### Core Components

#### Frontend

```
backstage-app/
├── packages/
│   ├── app/           # Main frontend application
│   ├── backend/       # Backend service
│   └── plugins/       # Custom plugins
├── plugins/           # Plugin workspace
└── package.json
```

#### Backend

The backend provides APIs and integrations:

- **Catalog Backend**: Manages entity data
- **Scaffolder Backend**: Template execution
- **TechDocs Backend**: Documentation generation
- **Search Backend**: Search indexing
- **Auth Backend**: Authentication/authorization
- **Proxy Backend**: API proxying

### Plugin System

#### Plugin Types

1. **Frontend Plugins**
   - UI components
   - Pages and routes
   - Integrations

2. **Backend Plugins**
   - API endpoints
   - Data processing
   - External integrations

3. **Common Packages**
   - Shared types
   - Utilities
   - Libraries

#### Creating a Plugin

```bash
# Create frontend plugin
yarn backstage-cli create-plugin --scope internal

# Create backend plugin
yarn backstage-cli create-plugin --backend --scope internal
```

## Popular Plugins

### Core Plugins

1. **Catalog**
   - Software catalog browser
   - Entity pages
   - Relations graph

2. **Scaffolder**
   - Template browser
   - Form generation
   - Task execution

3. **TechDocs**
   - Documentation viewer
   - Search integration
   - Build pipeline

4. **Search**
   - Unified search
   - Multiple backends
   - Custom indexers

### Integration Plugins

#### Source Control

1. **GitHub**
   ```yaml
   # catalog-info.yaml
   metadata:
     annotations:
       github.com/project-slug: org/repo
   ```

2. **GitLab**
   ```yaml
   metadata:
     annotations:
       gitlab.com/project-slug: org/repo
   ```

3. **Bitbucket**
   ```yaml
   metadata:
     annotations:
       bitbucket.org/project-key: PROJ
       bitbucket.org/repo-slug: repo
   ```

#### CI/CD

1. **Jenkins**
   - Build status
   - Job execution
   - Pipeline visualization

2. **CircleCI**
   - Workflow status
   - Build history
   - Re-run workflows

3. **GitHub Actions**
   - Workflow runs
   - Job logs
   - Deployment status

4. **ArgoCD**
   - Application status
   - Sync status
   - Deployment history

#### Cloud Providers

1. **AWS**
   - Resource discovery
   - Cost tracking
   - Service status

2. **Google Cloud**
   - Project integration
   - Resource management
   - IAM integration

3. **Azure**
   - Resource groups
   - Service integration
   - DevOps connection

#### Observability

1. **Datadog**
   - Dashboards
   - Alerts
   - Service metrics

2. **New Relic**
   - APM data
   - Error tracking
   - Performance metrics

3. **PagerDuty**
   - On-call schedules
   - Incident management
   - Service dependencies

4. **Sentry**
   - Error tracking
   - Release tracking
   - Issue management

#### Security

1. **Snyk**
   - Vulnerability scanning
   - Dependency analysis
   - Fix recommendations

2. **SonarQube**
   - Code quality
   - Security hotspots
   - Technical debt

3. **Dependabot**
   - Dependency updates
   - Security alerts
   - PR automation

## Configuration

### App Configuration

```yaml
# app-config.yaml
app:
  title: Developer Portal
  baseUrl: https://backstage.company.com

organization:
  name: Company Name

backend:
  baseUrl: https://backstage.company.com
  listen:
    port: 7007
  csp:
    connect-src: ["'self'", 'http:', 'https:']
  cors:
    origin: https://backstage.company.com
    methods: [GET, POST, PUT, DELETE]
    credentials: true
  database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      port: ${POSTGRES_PORT}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}

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

    # GitHub org discovery
    - type: url
      target: https://github.com/org/repo/blob/main/all.yaml
      rules:
        - allow: [User, Group]

    # URL location
    - type: url
      target: https://github.com/org/repo/blob/main/catalog-info.yaml

  processors:
    githubOrg:
      providers:
        - target: https://github.com
          apiBaseUrl: https://api.github.com
          token: ${GITHUB_TOKEN}

auth:
  environment: production
  providers:
    github:
      production:
        clientId: ${AUTH_GITHUB_CLIENT_ID}
        clientSecret: ${AUTH_GITHUB_CLIENT_SECRET}

    google:
      production:
        clientId: ${AUTH_GOOGLE_CLIENT_ID}
        clientSecret: ${AUTH_GOOGLE_CLIENT_SECRET}

    okta:
      production:
        clientId: ${AUTH_OKTA_CLIENT_ID}
        clientSecret: ${AUTH_OKTA_CLIENT_SECRET}
        audience: ${AUTH_OKTA_AUDIENCE}

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

kubernetes:
  serviceLocatorMethod:
    type: 'multiTenant'
  clusterLocatorMethods:
    - type: 'config'
      clusters:
        - url: https://kubernetes.default.svc
          name: production
          authProvider: 'serviceAccount'
          serviceAccountToken: ${K8S_TOKEN}
```

### Plugin Configuration

```typescript
// packages/app/src/App.tsx
import { createApp } from '@backstage/app-defaults';
import { AppRouter, FlatRoutes } from '@backstage/core-app-api';
import { CatalogEntityPage, CatalogIndexPage } from '@backstage/plugin-catalog';
import { ScaffolderPage } from '@backstage/plugin-scaffolder';
import { TechDocsPage } from '@backstage/plugin-techdocs';
import { UserSettingsPage } from '@backstage/plugin-user-settings';

const app = createApp({
  apis,
  bindRoutes({ bind }) {
    bind(catalogPlugin.externalRoutes, {
      createComponent: scaffolderPlugin.routes.root,
    });
  },
});

const AppProvider = app.getProvider();
const AppRouter = app.getRouter();

const routes = (
  <FlatRoutes>
    <Route path="/" element={<Navigate to="catalog" />} />
    <Route path="/catalog" element={<CatalogIndexPage />} />
    <Route
      path="/catalog/:namespace/:kind/:name"
      element={<CatalogEntityPage />}
    />
    <Route path="/create" element={<ScaffolderPage />} />
    <Route path="/docs" element={<TechDocsPage />} />
    <Route path="/settings" element={<UserSettingsPage />} />
  </FlatRoutes>
);
```

## Authentication & Authorization

### Authentication Providers

#### GitHub OAuth

```yaml
auth:
  providers:
    github:
      production:
        clientId: ${GITHUB_CLIENT_ID}
        clientSecret: ${GITHUB_CLIENT_SECRET}
        signIn:
          resolvers:
            - resolver: usernameMatchingUserEntityName
```

#### SAML

```yaml
auth:
  providers:
    saml:
      production:
        entryPoint: https://idp.example.com/sso
        issuer: backstage-entity-id
        cert: ${SAML_CERT}
```

#### OIDC

```yaml
auth:
  providers:
    oidc:
      production:
        metadataUrl: https://idp.example.com/.well-known/openid-configuration
        clientId: ${OIDC_CLIENT_ID}
        clientSecret: ${OIDC_CLIENT_SECRET}
```

### Authorization

#### Permission Framework

```typescript
// packages/backend/src/plugins/permission.ts
import { createRouter } from '@backstage/plugin-permission-backend';
import { PermissionPolicy } from '@backstage/plugin-permission-node';

class MyPermissionPolicy implements PermissionPolicy {
  async handle(request, user) {
    if (request.permission.name === 'catalog.entity.delete') {
      return user?.identity.ownershipEntityRefs.includes(
        request.resourceRef
      )
        ? { result: AuthorizeResult.ALLOW }
        : { result: AuthorizeResult.DENY };
    }
    return { result: AuthorizeResult.ALLOW };
  }
}

export default async function createPlugin(
  env: PluginEnvironment,
): Promise<Router> {
  return await createRouter({
    config: env.config,
    logger: env.logger,
    discovery: env.discovery,
    policy: new MyPermissionPolicy(),
  });
}
```

## Catalog Discovery

### GitHub Discovery

```yaml
catalog:
  providers:
    github:
      providerId:
        organization: 'my-org'
        catalogPath: '/catalog-info.yaml'
        filters:
          branch: 'main'
          repository: '.*'
        schedule:
          frequency: { minutes: 30 }
          timeout: { minutes: 3 }
```

### GitLab Discovery

```yaml
catalog:
  providers:
    gitlab:
      myGitlab:
        host: gitlab.com
        group: my-group
        entityFilename: catalog-info.yaml
        schedule:
          frequency: { minutes: 30 }
          timeout: { minutes: 3 }
```

### AWS S3 Discovery

```yaml
catalog:
  providers:
    awsS3:
      myBucket:
        bucketName: my-catalog-bucket
        region: us-east-1
        schedule:
          frequency: { hours: 1 }
          timeout: { minutes: 5 }
```

## Best Practices

### Entity Modeling

1. **Use Descriptive Names**
   - Clear, meaningful entity names
   - Follow naming conventions
   - Include context

2. **Define Ownership**
   - Every entity has an owner
   - Map to teams/groups
   - Clear responsibility

3. **Document Thoroughly**
   - Complete descriptions
   - Links to documentation
   - Usage examples

4. **Model Dependencies**
   - Explicit component dependencies
   - API relationships
   - Resource connections

### Template Design

1. **Start Simple**
   - Minimal required inputs
   - Smart defaults
   - Clear instructions

2. **Validate Early**
   - Input validation
   - Availability checks
   - Naming rules

3. **Provide Feedback**
   - Progress indicators
   - Clear error messages
   - Success confirmation

4. **Enable Discovery**
   - Auto-register in catalog
   - Link to resources
   - Setup documentation

### Plugin Development

1. **Follow Conventions**
   - Use plugin CLI
   - Standard structure
   - TypeScript best practices

2. **Handle Errors**
   - Graceful degradation
   - User-friendly messages
   - Logging

3. **Test Thoroughly**
   - Unit tests
   - Integration tests
   - E2E tests

4. **Document Well**
   - Setup instructions
   - Configuration options
   - Examples

## Monitoring & Observability

### Metrics

```typescript
// Custom metrics
import { MetricsHandler } from '@backstage/backend-common';

const metrics = MetricsHandler.create();

metrics.counter('catalog.entity.created').inc();
metrics.histogram('scaffolder.task.duration').observe(durationMs);
metrics.gauge('catalog.entity.total').set(entityCount);
```

### Logging

```typescript
// Structured logging
logger.info('Processing entity', {
  entityRef: stringifyEntityRef(entity),
  kind: entity.kind,
});

logger.error('Failed to process entity', {
  error: error.message,
  stack: error.stack,
});
```

### Health Checks

```typescript
// packages/backend/src/plugins/app.ts
router.get('/health', (_, response) => {
  response.json({ status: 'ok' });
});

router.get('/healthcheck', async (_, response) => {
  const checks = {
    database: await checkDatabase(),
    catalog: await checkCatalog(),
  };

  const allHealthy = Object.values(checks).every(c => c.status === 'ok');

  response.status(allHealthy ? 200 : 503).json(checks);
});
```

## Performance Optimization

### Caching

```typescript
// Cache entity data
import { CacheClient } from '@backstage/backend-common';

const cache = CacheClient.create({
  client: cacheManager.store,
  defaultTtl: 300000, // 5 minutes
});

await cache.set('entity-key', entityData);
const cached = await cache.get('entity-key');
```

### Database Optimization

```yaml
backend:
  database:
    connection:
      pool:
        min: 2
        max: 10
      acquireTimeoutMillis: 60000
```

### Build Optimization

```json
// package.json
{
  "scripts": {
    "build": "backstage-cli package build",
    "build:all": "backstage-cli repo build --all",
    "build:backend": "yarn workspace backend build"
  }
}
```

## Troubleshooting

### Common Issues

1. **Plugin Not Loading**
   - Check plugin installation
   - Verify app configuration
   - Check browser console

2. **Entity Not Appearing**
   - Verify catalog location
   - Check entity validation
   - Review processor logs

3. **Authentication Failing**
   - Verify provider config
   - Check callback URLs
   - Review auth logs

4. **Template Execution Failing**
   - Check template syntax
   - Verify action configuration
   - Review scaffolder logs

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
yarn dev
```

## Resources

- Official Documentation: https://backstage.io/docs
- Plugin Marketplace: https://backstage.io/plugins
- Community: https://discord.gg/backstage-687207715902193673
- GitHub: https://github.com/backstage/backstage
