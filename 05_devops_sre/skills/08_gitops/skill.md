# GitOps - Elite Professional Practices

**Git as single source of truth for declarative infrastructure and applications**

---

## Overview

GitOps is a way of implementing Continuous Deployment for cloud-native applications, using Git as the single source of truth for declarative infrastructure and applications. All infrastructure and application configuration is version-controlled in Git, with automated sync from Git to production.

You are an expert in GitOps practices that enable organizations to manage infrastructure safely, auditably, and automatically using standard Git workflows and tools.

## Core Principles

### 1. Declarative Description

Describe desired state, not how to achieve it.

```yaml
# Declarative (GitOps)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web
        image: myapp:v1.2.3  # Desired state

# Actual state: 3 replicas running myapp:v1.2.3
# Kubernetes ensures this, even if pods crash
```

### 2. Git as Source of Truth

All configuration stored in Git, with complete history and audit trail.

```
Git repository:
├── applications/
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── api/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── kustomization.yaml
├── infrastructure/
│   ├── namespaces.yaml
│   ├── rbac.yaml
│   └── network-policies.yaml
└── environments/
    ├── dev/
    ├── staging/
    └── production/

Everything in Git:
- Infrastructure definitions
- Application manifests
- Configuration
- Secrets (encrypted)
- Policy definitions

Benefits:
- Complete audit trail (who changed what, when, why)
- Easy rollback (revert Git commit)
- PR review process for all changes
- No manual changes (prevent drift)
```

### 3. Automated Sync

GitOps operator continuously reconciles actual state with desired state from Git.

```
Workflow:
1. Dev commits changes to Git
   git commit -am "Scale API to 5 replicas"
   git push

2. GitOps operator detects change
   ArgoCD/Flux polls Git every 3 minutes
   Or: Webhook notifies operator immediately

3. Operator applies changes to cluster
   kubectl apply -f manifests/

4. Continuous reconciliation
   Every 3 minutes: Compare Git state to actual state
   If drift detected: Auto-sync back to Git (can be configured)
   If failure: Alert and retry
```

## GitOps Workflow

```
Application development:
1. Dev writes application code
   Commits to application Git repo

2. CI/CD pipeline triggers
   - Build and test code
   - Build Docker image
   - Push image to registry: myapp:abc123def

3. Update image reference in GitOps repo
   - Automatically: Update manifests/deployment.yaml image: myapp:abc123def
   - Commit to GitOps repo: "Deploy myapp:abc123def"

4. GitOps operator detects GitOps repo change
   - Pulls latest manifests from Git
   - Compares to Kubernetes cluster state

5. Auto-sync (if enabled)
   - Applies manifests to cluster
   - New image deployed automatically

6. Continuous reconciliation
   - Every 3 minutes: Verify desired state matches actual state
   - If drift: Auto-correct or alert

Result: Application updated in production from Git commit
```

## Technology Stack

### ArgoCD

**Kubernetes-native GitOps continuous delivery**

```yaml
# ArgoCD Application resource
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/company/gitops-repo.git
    targetRevision: main
    path: applications/myapp
  destination:
    server: https://kubernetes.default.svc  # This cluster
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Delete resources removed from Git
      selfHeal: true   # Auto-sync if cluster drifts
    syncOptions:
    - CreateNamespace=true
```

**Features**:
- Web UI for visualization
- CLI support
- Multi-cluster management
- Diff before sync
- Rollback capability
- Progressive sync strategies

### Flux

**CNCF GitOps operator**

```yaml
# Flux Kustomization resource
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m          # Poll Git every 10 minutes
  sourceRef:
    kind: GitRepository
    name: gitops-repo
  path: ./applications/myapp
  prune: true            # Remove resources not in Git
  wait: true
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: myapp
    namespace: production
```

**Advantages**:
- Lightweight and fast
- Good for multi-cluster (Fleet)
- Strong community
- GitOps Foundation standard

### Rancher Fleet

**Multi-cluster GitOps**

```yaml
# Deploy to multiple clusters with Fleet
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: myapp
  namespace: fleet-default
spec:
  repo: https://github.com/company/gitops-repo.git
  branch: main
  paths:
  - applications/myapp

# Automatically deployed to:
# - All clusters
# - Specific clusters (via labels)
# - Specific namespaces
```

## Implementation Patterns

### Repository Structure

```
# Monorepo approach (one repo for everything)
gitops-repo/
├── applications/
│   ├── frontend/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── production/
│   └── api/
│       ├── base/
│       └── overlays/
├── infrastructure/
│   ├── base/
│   │   ├── namespaces.yaml
│   │   ├── rbac.yaml
│   │   └── network-policies.yaml
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
└── README.md

# Multi-repo approach (separate repos)
app-repo/ (contains application code)
├── src/
├── tests/
├── Dockerfile
└── .github/workflows/ci.yml  # Updates image in GitOps repo

gitops-repo/ (contains infrastructure only)
├── manifests/
│   ├── production/
│   ├── staging/
│   └── dev/
└── README.md
```

### Secrets Management in GitOps

```yaml
# NEVER commit unencrypted secrets to Git

# Option 1: Sealed Secrets
# Encrypt secrets with cluster public key
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-password
  namespace: production
spec:
  encryptedData:
    password: AgBvK3X4F2kZ...  # Encrypted
  template:
    metadata:
      name: db-password
      namespace: production
    type: Opaque

# Option 2: External Secrets Operator
# Reference secrets from external vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-password
  namespace: production
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: db-password
  data:
  - secretKey: password
    remoteRef:
      key: prod/database/password

# Option 3: Kustomize + sensitive data
kustomization.yaml:
  secretGenerator:
  - name: db-password
    envs:
    - secrets.env  # .gitignored locally, but committed with values

# Only for secrets that can be different per environment
```

### Drift Detection and Remediation

```yaml
# ArgoCD continuous reconciliation
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
spec:
  syncPolicy:
    automated:
      prune: true      # Remove extra resources
      selfHeal: true   # Auto-sync drift
    syncOptions:
    - Validate=true
  # Manual sync
  # selfHeal: false
  # Alerts on drift but doesn't auto-fix

# Alerts when drift detected
status:
  operationState:
    phase: Error
    message: "Cluster has drifted from Git"
```

## Best Practices

### 1. Separate Repos

```
Application repo:
- Source code
- Tests
- CI/CD pipelines
- Build artifacts (Docker images)

GitOps repo:
- Kubernetes manifests
- Infrastructure definitions
- Configuration
- Deployment definitions
- Secrets (encrypted)

Reasoning:
- Application team controls app repo
- Platform team controls infra repo
- Independent workflows and access control
- Clear separation of concerns
```

### 2. Code Review for Infrastructure Changes

```
Every infrastructure change requires:
1. Feature branch created
2. Changes made to manifests
3. Pull request opened
4. Code review (platform team)
5. Tests/validation in PR
6. Approval
7. Merge to main
8. Automatic deployment from main

Benefits:
- Prevents human errors
- Audit trail (PR history)
- Knowledge sharing (reviews)
- Automated testing
- Rollback via Git revert
```

### 3. Testing in GitOps

```bash
# Validate manifests before merge
kubeval manifests/
# Checks YAML syntax and Kubernetes API compliance

# Policy testing (Kyverno, Kube-mgmt)
kyverno apply --resource pod.yaml --policies security.rego

# Schema validation
helm template myapp --validate

# Integration testing
kustomize build overlays/dev | kubectl apply --dry-run=client -f -
```

### 4. Progressive Sync

```yaml
# Deploy to dev first, then staging, then production
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-dev
spec:
  source:
    path: overlays/dev
  destination:
    server: https://dev-cluster.com
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

---

apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-staging
spec:
  source:
    path: overlays/staging
  destination:
    server: https://staging-cluster.com
  syncPolicy:
    automated:
      prune: true
      selfHeal: false  # Manual approval for staging

---

apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-production
spec:
  source:
    path: overlays/production
  destination:
    server: https://production-cluster.com
  syncPolicy:
    # Require manual sync for production
    syncOptions:
    - CreateNamespace=true
```

### 5. Monitoring and Alerting

```
Monitor:
- Sync status (in sync or out of sync)
- Sync success/failure
- Drift detection
- Application health

Alerts:
- Application out of sync (drift detected)
- Sync failed (error in Git or cluster)
- Health check failed
- Image pull failures
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Expertise Level**: Elite Professional
**Based on**: Weaveworks, ArgoCD, Flux, CNCF GitOps principles
