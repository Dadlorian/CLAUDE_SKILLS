# ArgoCD Reference Guide

## Overview

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It follows the GitOps pattern of using Git repositories as the source of truth for defining the desired application state.

## Core Concepts

### Application

The Application CRD is the core resource in ArgoCD. It defines:
- Source repository (Git repo containing manifests)
- Destination cluster and namespace
- Sync policies and behaviors

### AppProject

Projects provide logical grouping of applications with:
- Source repository restrictions
- Destination cluster/namespace restrictions
- Resource whitelists/blacklists
- Role-based access control

### Repository

Git repositories or Helm repositories that ArgoCD monitors for application manifests.

## Installation

### Core Installation

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Install ArgoCD HA (High Availability)
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/ha/install.yaml
```

### Access ArgoCD UI

```bash
# Port forward (development)
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Production Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  ingressClassName: nginx
  rules:
  - host: argocd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              name: https
  tls:
  - hosts:
    - argocd.example.com
    secretName: argocd-server-tls
```

## Application Manifest Structure

### Basic Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/myapp.git
    targetRevision: HEAD
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### Application with Helm

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-helm
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/example/myapp.git
    targetRevision: v1.2.3
    path: charts/myapp
    helm:
      releaseName: myapp
      valueFiles:
      - values.yaml
      - values-production.yaml
      parameters:
      - name: image.tag
        value: "1.2.3"
      - name: replicas
        value: "3"
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Application with Kustomize

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-kustomize
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/myapp.git
    targetRevision: main
    path: k8s/overlays/staging
    kustomize:
      namePrefix: staging-
      nameSuffix: -v2
      commonLabels:
        environment: staging
        version: v2
      images:
      - myapp:v1.2.3
      replicas:
      - name: myapp-deployment
        count: 2
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp-staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Sync Policies

### Automated Sync

```yaml
syncPolicy:
  automated:
    # Automatically sync when repo changes
    prune: true        # Delete resources not in Git
    selfHeal: true     # Force sync when cluster state diverges
    allowEmpty: false  # Don't sync if source produces no manifests
  syncOptions:
  - CreateNamespace=true       # Create namespace if missing
  - PrunePropagationPolicy=foreground  # Wait for cascade deletion
  - PruneLast=true            # Prune resources after new resources are healthy
  - ApplyOutOfSyncOnly=true   # Only sync out-of-sync resources
  - RespectIgnoreDifferences=true  # Respect ignoreDifferences
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

### Manual Sync

```yaml
syncPolicy:
  syncOptions:
  - CreateNamespace=true
  - ApplyOutOfSyncOnly=true
  retry:
    limit: 3
    backoff:
      duration: 5s
      maxDuration: 1m
```

### Sync Waves

Use annotations to control sync order:

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "0"  # Lower numbers sync first
```

Example sync wave ordering:
- Wave -5: Namespaces
- Wave -4: CustomResourceDefinitions
- Wave -3: ServiceAccounts, Roles, RoleBindings
- Wave -2: ConfigMaps, Secrets
- Wave -1: PersistentVolumeClaims
- Wave 0: Deployments, Services (default)
- Wave 1: Ingress
- Wave 2: Jobs (data migration)

### Sync Hooks

```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync  # Run before sync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded  # Delete after success
```

Hook types:
- `PreSync`: Before the sync operation
- `Sync`: During the sync operation
- `PostSync`: After the sync operation
- `SyncFail`: If the sync operation fails
- `Skip`: Skip resource during sync

Delete policies:
- `HookSucceeded`: Delete after successful execution
- `HookFailed`: Delete after failed execution
- `BeforeHookCreation`: Delete before new hook is created

## AppProject Configuration

### Basic AppProject

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production applications

  # Source repositories
  sourceRepos:
  - 'https://github.com/example/*'
  - 'https://charts.example.com'

  # Destination clusters and namespaces
  destinations:
  - namespace: '*'
    server: https://kubernetes.default.svc
  - namespace: 'prod-*'
    server: https://prod-cluster.example.com

  # Cluster-scoped resources
  clusterResourceWhitelist:
  - group: ''
    kind: Namespace
  - group: 'rbac.authorization.k8s.io'
    kind: ClusterRole
  - group: 'rbac.authorization.k8s.io'
    kind: ClusterRoleBinding

  # Namespace-scoped resources
  namespaceResourceWhitelist:
  - group: '*'
    kind: '*'

  # Denied resources
  namespaceResourceBlacklist:
  - group: ''
    kind: ResourceQuota
  - group: ''
    kind: LimitRange
```

### Advanced AppProject with RBAC

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-alpha
  namespace: argocd
spec:
  description: Team Alpha applications

  sourceRepos:
  - 'https://github.com/team-alpha/*'

  destinations:
  - namespace: 'team-alpha-*'
    server: '*'

  clusterResourceWhitelist:
  - group: ''
    kind: Namespace

  namespaceResourceWhitelist:
  - group: 'apps'
    kind: Deployment
  - group: 'apps'
    kind: StatefulSet
  - group: ''
    kind: Service
  - group: ''
    kind: ConfigMap
  - group: ''
    kind: Secret
  - group: 'networking.k8s.io'
    kind: Ingress

  # RBAC roles
  roles:
  - name: developer
    description: Developer access
    policies:
    - p, proj:team-alpha:developer, applications, get, team-alpha/*, allow
    - p, proj:team-alpha:developer, applications, sync, team-alpha/*, allow
    groups:
    - team-alpha-devs

  - name: admin
    description: Full admin access
    policies:
    - p, proj:team-alpha:admin, applications, *, team-alpha/*, allow
    groups:
    - team-alpha-admins

  # Sync windows
  syncWindows:
  - kind: allow
    schedule: '0 9-17 * * 1-5'  # Mon-Fri 9am-5pm
    duration: 8h
    applications:
    - '*'
  - kind: deny
    schedule: '0 0 * * 0'  # Sunday midnight
    duration: 4h
    applications:
    - '*'
```

## Health Assessment

### Custom Health Checks

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations: |
    custom.example.com/MyCustomResource:
      health.lua: |
        hs = {}
        if obj.status ~= nil then
          if obj.status.phase == "Running" then
            hs.status = "Healthy"
            hs.message = "Resource is running"
            return hs
          end
          if obj.status.phase == "Failed" then
            hs.status = "Degraded"
            hs.message = obj.status.message
            return hs
          end
        end
        hs.status = "Progressing"
        hs.message = "Waiting for resource"
        return hs
```

### Health Status Values

- `Healthy`: Resource is healthy
- `Progressing`: Resource is being created/updated
- `Degraded`: Resource is degraded
- `Suspended`: Resource is suspended
- `Missing`: Resource is missing
- `Unknown`: Health status is unknown

## Ignore Differences

```yaml
spec:
  ignoreDifferences:
  # Ignore generated fields
  - group: apps
    kind: Deployment
    jsonPointers:
    - /spec/replicas

  # Ignore HPA-managed replicas
  - group: apps
    kind: Deployment
    jqPathExpressions:
    - .spec.replicas

  # Ignore all differences in specific resources
  - group: apps
    kind: StatefulSet
    name: myapp
    namespace: production
```

## Application Finalizers

```yaml
metadata:
  finalizers:
  - resources-finalizer.argocd.argoproj.io  # Delete app resources when app is deleted
```

## CLI Commands Reference

### Application Management

```bash
# List applications
argocd app list

# Get application details
argocd app get myapp

# Create application
argocd app create myapp \
  --repo https://github.com/example/myapp.git \
  --path k8s \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace myapp

# Sync application
argocd app sync myapp

# Sync with prune
argocd app sync myapp --prune

# Force sync
argocd app sync myapp --force

# Rollback application
argocd app rollback myapp

# Delete application
argocd app delete myapp

# Delete with cascade (delete app resources)
argocd app delete myapp --cascade
```

### Application Status

```bash
# Wait for application to be healthy
argocd app wait myapp --health

# Wait for sync to complete
argocd app wait myapp --sync

# Get application manifests
argocd app manifests myapp

# Get application diff
argocd app diff myapp

# Get application history
argocd app history myapp
```

### Repository Management

```bash
# Add repository
argocd repo add https://github.com/example/myapp.git \
  --username myuser \
  --password mytoken

# Add SSH repository
argocd repo add git@github.com:example/myapp.git \
  --ssh-private-key-path ~/.ssh/id_rsa

# List repositories
argocd repo list

# Remove repository
argocd repo rm https://github.com/example/myapp.git
```

### Cluster Management

```bash
# Add cluster
argocd cluster add my-cluster-context

# List clusters
argocd cluster list

# Get cluster info
argocd cluster get https://kubernetes.default.svc

# Remove cluster
argocd cluster rm https://my-cluster.example.com
```

### Project Management

```bash
# Create project
argocd proj create myproject

# Add source repo to project
argocd proj add-source myproject https://github.com/example/*

# Add destination to project
argocd proj add-destination myproject https://kubernetes.default.svc namespace

# List projects
argocd proj list

# Get project details
argocd proj get myproject
```

## Notifications

### Email Notifications

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.email.gmail: |
    username: $email-username
    password: $email-password
    host: smtp.gmail.com
    port: 465
    from: $email-username

  template.app-deployed: |
    email:
      subject: Application {{.app.metadata.name}} deployed
    message: |
      Application {{.app.metadata.name}} is now running new version.
      Application details: {{.context.argocdUrl}}/applications/{{.app.metadata.name}}.

  trigger.on-deployed: |
    - when: app.status.operationState.phase in ['Succeeded']
      oncePer: app.status.sync.revision
      send: [app-deployed]
```

### Slack Notifications

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.slack: |
    token: $slack-token

  template.app-sync-succeeded: |
    message: |
      Application {{.app.metadata.name}} sync succeeded.
      Revision: {{.app.status.sync.revision}}
      {{if .app.status.operationState.syncResult}}
      Resources:
      {{- range .app.status.operationState.syncResult.resources}}
      - {{.kind}}/{{.name}}: {{.message}}
      {{- end}}
      {{end}}
    slack:
      attachments: |
        [{
          "title": "{{ .app.metadata.name}}",
          "title_link":"{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
          "color": "#18be52",
          "fields": [
          {
            "title": "Sync Status",
            "value": "{{.app.status.sync.status}}",
            "short": true
          },
          {
            "title": "Repository",
            "value": "{{.app.spec.source.repoURL}}",
            "short": true
          }
          ]
        }]
```

## Performance Optimization

### Application Controller Tuning

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  # Application reconciliation timeout
  timeout.reconciliation: 180s

  # Status processors
  statusProcessors: "20"

  # Operation processors
  operationProcessors: "10"

  # Application resync interval
  timeout.hard.reconciliation: 0s  # Disable hard reconciliation
```

### Repo Server Tuning

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-repo-server
  namespace: argocd
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: argocd-repo-server
        env:
        - name: ARGOCD_EXEC_TIMEOUT
          value: "180s"
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 2Gi
```

## Best Practices

### 1. Use AppProjects for Multi-Tenancy

Organize applications by team or environment using AppProjects.

### 2. Enable Automated Pruning Carefully

Only enable `prune: true` when you're confident resources should be managed exclusively by GitOps.

### 3. Use Sync Waves for Dependencies

Order resource creation using sync waves to handle dependencies.

### 4. Implement Health Checks

Define custom health checks for CRDs to ensure accurate status reporting.

### 5. Use Resource Hooks

Leverage PreSync and PostSync hooks for database migrations and validations.

### 6. Monitor Application Status

Set up notifications for sync failures and degraded applications.

### 7. Backup ArgoCD Configuration

Regularly backup AppProject and Application manifests.

### 8. Use Git Webhooks

Configure webhooks for faster sync detection instead of polling.

### 9. Implement RBAC

Use AppProject RBAC to control access per team or environment.

### 10. Version Control Everything

Store all ArgoCD configurations (Applications, AppProjects) in Git.

## Troubleshooting

### Application Not Syncing

```bash
# Check application status
argocd app get myapp

# Check application events
kubectl get events -n argocd --field-selector involvedObject.name=myapp

# Check repo server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-repo-server

# Force refresh
argocd app get myapp --refresh --hard-refresh
```

### Sync Fails

```bash
# Get detailed sync status
argocd app sync myapp --dry-run

# Check resource differences
argocd app diff myapp

# Review sync operation details
argocd app get myapp --show-operation
```

### Performance Issues

```bash
# Check application controller logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller

# Check resource usage
kubectl top pods -n argocd

# Review application metrics
kubectl get applications -A
```

## Security Considerations

### 1. RBAC Configuration

Always implement least-privilege RBAC policies.

### 2. Secret Management

Use sealed-secrets or external secret operators for sensitive data.

### 3. Repository Access

Use deploy keys or machine accounts with read-only access.

### 4. TLS Configuration

Always use TLS for ArgoCD UI and API access.

### 5. Audit Logging

Enable audit logging for compliance requirements.

### 6. Network Policies

Restrict network access to ArgoCD components.

## Additional Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD GitHub](https://github.com/argoproj/argo-cd)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [ArgoCD Operator Manual](https://argo-cd.readthedocs.io/en/stable/operator-manual/)
