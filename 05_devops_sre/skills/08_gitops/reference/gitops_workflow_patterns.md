# GitOps Workflow Patterns Reference

## Overview

GitOps is a paradigm that uses Git as the single source of truth for declarative infrastructure and applications. This reference covers common repository structures, branching strategies, and workflow patterns.

## Core GitOps Principles

### 1. Declarative

The entire system is described declaratively in Git.

### 2. Versioned and Immutable

Git provides version control and immutable history.

### 3. Pulled Automatically

Software agents automatically pull desired state from Git.

### 4. Continuously Reconciled

Actual state is continuously reconciled with desired state.

## Repository Structure Patterns

### Pattern 1: Monorepo Structure

Single repository containing all environments and applications.

```
gitops-monorepo/
├── README.md
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   │   ├── gotk-components.yaml
│   │   │   ├── gotk-sync.yaml
│   │   │   └── kustomization.yaml
│   │   ├── infrastructure.yaml
│   │   └── apps.yaml
│   ├── staging/
│   │   ├── flux-system/
│   │   ├── infrastructure.yaml
│   │   └── apps.yaml
│   └── development/
│       ├── flux-system/
│       ├── infrastructure.yaml
│       └── apps.yaml
├── infrastructure/
│   ├── base/
│   │   ├── cert-manager/
│   │   ├── ingress-nginx/
│   │   ├── prometheus/
│   │   └── sealed-secrets/
│   └── overlays/
│       ├── production/
│       ├── staging/
│       └── development/
├── apps/
│   ├── base/
│   │   ├── app1/
│   │   ├── app2/
│   │   └── app3/
│   └── overlays/
│       ├── production/
│       ├── staging/
│       └── development/
└── policies/
    ├── network-policies/
    ├── pod-security-policies/
    └── resource-quotas/
```

**Pros:**
- Single source of truth
- Easy to see entire system
- Simpler RBAC
- Atomic changes across environments

**Cons:**
- Can become large
- Slower clone times
- All teams have visibility to all configs

**Best for:** Small to medium organizations with centralized ops teams

### Pattern 2: Repository per Environment

Separate repositories for each environment.

```
gitops-production/
├── README.md
├── flux-system/
├── infrastructure/
│   ├── cert-manager/
│   ├── ingress-nginx/
│   └── prometheus/
└── apps/
    ├── app1/
    ├── app2/
    └── app3/

gitops-staging/
├── README.md
├── flux-system/
├── infrastructure/
└── apps/

gitops-development/
├── README.md
├── flux-system/
├── infrastructure/
└── apps/
```

**Pros:**
- Strong environment isolation
- Different RBAC per environment
- Independent change cadence
- Production can be private

**Cons:**
- Configuration drift between environments
- Harder to promote changes
- Multiple repositories to maintain

**Best for:** Organizations requiring strong production isolation

### Pattern 3: Repository per Team

Team-owned repositories with environment overlays.

```
team-alpha-gitops/
├── README.md
├── base/
│   ├── app1/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── app2/
│       ├── deployment.yaml
│       └── kustomization.yaml
└── environments/
    ├── production/
    │   ├── app1/
    │   │   └── kustomization.yaml
    │   └── kustomization.yaml
    ├── staging/
    │   ├── app1/
    │   │   └── kustomization.yaml
    │   └── kustomization.yaml
    └── development/
        └── kustomization.yaml

platform-gitops/
├── README.md
├── clusters/
│   ├── production/
│   ├── staging/
│   └── development/
└── infrastructure/
    ├── base/
    └── overlays/
```

**Pros:**
- Team autonomy
- Clear ownership boundaries
- Faster team iteration
- Scoped RBAC per team

**Cons:**
- Requires orchestration layer
- More complex to set up
- Cross-team coordination needed

**Best for:** Large organizations with multiple autonomous teams

### Pattern 4: Hybrid - Fleet Repository + App Repositories

Central fleet repo references team app repositories.

```
fleet-infra/
├── README.md
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   ├── infrastructure/
│   │   │   ├── sources.yaml
│   │   │   └── releases.yaml
│   │   └── teams/
│   │       ├── team-alpha.yaml
│   │       ├── team-beta.yaml
│   │       └── team-gamma.yaml
│   └── staging/
│       └── ...
└── infrastructure/
    ├── sources/
    │   ├── repositories.yaml
    │   └── helm-repos.yaml
    └── configs/
        └── cluster-config.yaml

team-alpha-apps/
├── README.md
├── app1/
│   ├── base/
│   └── overlays/
└── app2/
    ├── base/
    └── overlays/
```

Fleet repo references:
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: team-alpha
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: team-alpha-apps
  path: ./production
  prune: true
```

**Pros:**
- Central control with team autonomy
- Clear separation of concerns
- Scalable for large orgs
- Platform team controls infrastructure

**Cons:**
- More complex setup
- Multiple repositories
- Requires coordination

**Best for:** Enterprise organizations with platform teams

## Branching Strategies

### Strategy 1: Environment Branches

Different branches represent different environments.

```
main (production)
├── staging
│   └── development
└── feature/new-app
```

**Workflow:**
1. Develop on feature branches
2. Merge to `development` branch → deploys to dev
3. Merge to `staging` branch → deploys to staging
4. Merge to `main` branch → deploys to production

**Pros:**
- Simple mental model
- Clear environment state
- Easy rollbacks (revert commit)

**Cons:**
- Merge conflicts between environments
- Drift between environments
- Hard to see what's different

**Configuration:**
```yaml
# ArgoCD for development
spec:
  source:
    targetRevision: development

# ArgoCD for production
spec:
  source:
    targetRevision: main
```

### Strategy 2: Directory-Based Environments

Single branch, directories per environment.

```
main
└── environments/
    ├── production/
    ├── staging/
    └── development/
```

**Workflow:**
1. All changes on `main` or feature branches
2. Kustomize overlays define environment differences
3. Different paths for different environments

**Pros:**
- Single branch to manage
- Clear visibility of all environments
- Kustomize provides structured differences
- No merge conflicts between environments

**Cons:**
- All environments updated together
- Requires discipline in directory structure

**Configuration:**
```yaml
# Production
spec:
  path: ./environments/production

# Staging
spec:
  path: ./environments/staging
```

### Strategy 3: GitOps with Pull Requests

Feature branches with PR-based promotion.

```
main
├── feature/app-v2
├── feature/new-config
└── hotfix/security-patch
```

**Workflow:**
1. Create feature branch
2. Make changes
3. Open PR for review
4. Merge to main → automated deployment
5. Tag releases for production

**Pros:**
- Code review for all changes
- Audit trail via PRs
- CI/CD validation before merge
- Safe rollback via Git

**Cons:**
- Manual PR process
- Potential for human error in approvals

**Configuration:**
```yaml
# Auto-deploy from main
spec:
  source:
    targetRevision: main
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Strategy 4: Trunk-Based with Tags

Main branch with tags for releases.

```
main
├── v1.0.0 (tag)
├── v1.1.0 (tag)
└── v2.0.0 (tag)
```

**Workflow:**
1. All development on `main`
2. Tag releases: `v1.0.0`, `v1.1.0`
3. Different environments track different tags
4. Promote by updating tag reference

**Pros:**
- Simplified branching
- Clear versioning
- Easy to see what's deployed
- Fast rollbacks (change tag)

**Cons:**
- Requires tag management
- Need process for tagging

**Configuration:**
```yaml
# Production tracks stable tags
spec:
  source:
    targetRevision: v1.1.0

# Staging tracks release candidates
spec:
  source:
    targetRevision: v1.2.0-rc1

# Development tracks main
spec:
  source:
    targetRevision: main
```

## Promotion Patterns

### Pattern 1: Manual Promotion via PR

```
┌─────────────┐      PR       ┌─────────────┐      PR       ┌─────────────┐
│ Development │ ────────────> │   Staging   │ ────────────> │ Production  │
└─────────────┘               └─────────────┘               └─────────────┘
```

**Process:**
1. Deploy to development automatically
2. Create PR to promote to staging
3. Review and merge
4. Create PR to promote to production
5. Review and merge

**Implementation:**
```yaml
# development/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
patches:
- path: development-patches.yaml

# To promote: copy to staging/, review, merge
```

### Pattern 2: Automated Promotion with Approval Gates

```
┌─────────────┐    Auto     ┌─────────────┐   Approval   ┌─────────────┐
│ Development │ ──────────> │   Staging   │ ───────────> │ Production  │
└─────────────┘             └─────────────┘              └─────────────┘
```

**Process:**
1. Merge to main → auto-deploy to dev
2. Tests pass → auto-promote to staging
3. Manual approval required for production
4. Approved → auto-deploy to production

**Implementation with GitHub Actions:**
```yaml
name: Promote to Production
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to promote'
        required: true

jobs:
  promote:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Update production
      run: |
        cd environments/production
        kustomize edit set image app:${{ inputs.version }}
        git add .
        git commit -m "Promote ${{ inputs.version }} to production"
        git push
```

### Pattern 3: Image Update Automation

```
┌──────────────┐   New Image   ┌──────────────┐
│   Registry   │ ────────────> │ Image Update │
└──────────────┘               │  Automation  │
                               └──────┬───────┘
                                      │
                                      v
                               ┌──────────────┐
                               │  Git Update  │
                               └──────────────┘
```

**Process:**
1. New image pushed to registry
2. Image automation detects new version
3. Updates Git repository automatically
4. GitOps applies changes

**Implementation (Flux):**
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: myapp
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: myapp
  git:
    commit:
      author:
        email: fluxbot@example.com
        name: fluxbot
  update:
    path: ./environments/development
    strategy: Setters
```

## Application Deployment Patterns

### Pattern 1: Kustomize Base + Overlays

```
app/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── production/
    │   ├── kustomization.yaml
    │   ├── replica-count.yaml
    │   └── resource-limits.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── development/
        └── kustomization.yaml
```

**base/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
commonLabels:
  app: myapp
```

**overlays/production/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../base
namePrefix: prod-
commonLabels:
  environment: production
patches:
- path: replica-count.yaml
- path: resource-limits.yaml
```

### Pattern 2: Helm with Value Files

```
app/
├── Chart.yaml
├── values.yaml
├── values-production.yaml
├── values-staging.yaml
├── values-development.yaml
└── templates/
    ├── deployment.yaml
    └── service.yaml
```

**HelmRelease:**
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: myapp
spec:
  chart:
    spec:
      chart: ./app
      sourceRef:
        kind: GitRepository
        name: myapp
  values:
    replicaCount: 3
  valuesFrom:
  - kind: ConfigMap
    name: myapp-values
```

### Pattern 3: Application Sets (ArgoCD)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: myapp
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: production
        url: https://kubernetes.default.svc
        revision: v1.2.3
        replicas: 3
      - cluster: staging
        url: https://staging.k8s.example.com
        revision: v1.3.0
        replicas: 2
  template:
    metadata:
      name: 'myapp-{{cluster}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/example/myapp
        targetRevision: '{{revision}}'
        path: k8s
        helm:
          parameters:
          - name: replicaCount
            value: '{{replicas}}'
      destination:
        server: '{{url}}'
        namespace: myapp
```

## Secret Management Patterns

### Pattern 1: Sealed Secrets

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: mysecret
  namespace: production
spec:
  encryptedData:
    password: AgBj8P7QK4...encrypted...
  template:
    metadata:
      name: mysecret
    type: Opaque
```

**Workflow:**
1. Create secret normally
2. Encrypt with kubeseal
3. Commit encrypted secret to Git
4. Controller decrypts in cluster

### Pattern 2: SOPS with Age/GPG

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
stringData:
  password: ENC[AES256_GCM,data:encrypted,type:str]
sops:
  kms: []
  gcp_kms: []
  azure_kv: []
  age:
  - recipient: age1...
  lastmodified: "2024-01-15T10:30:00Z"
```

**Workflow:**
1. Create secret file
2. Encrypt with SOPS: `sops -e secret.yaml > secret.enc.yaml`
3. Commit encrypted file to Git
4. GitOps tool decrypts during apply

### Pattern 3: External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mysecret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: mysecret
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: prod/myapp/password
```

**Workflow:**
1. Store secrets in external system (Vault, AWS Secrets Manager)
2. Reference secrets via ExternalSecret CRD
3. Operator syncs from external system to Kubernetes

## Multi-Cluster Patterns

### Pattern 1: Cluster per Environment

```
fleet-repo/
├── clusters/
│   ├── production-us-east/
│   │   └── flux-system/
│   ├── production-eu-west/
│   │   └── flux-system/
│   ├── staging/
│   │   └── flux-system/
│   └── development/
│       └── flux-system/
└── apps/
    └── base/
```

Each cluster bootstrapped independently:
```bash
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-repo \
  --path=clusters/production-us-east
```

### Pattern 2: Hub and Spoke

```
hub-cluster (ArgoCD/Flux)
├── manages ──> spoke-cluster-1
├── manages ──> spoke-cluster-2
└── manages ──> spoke-cluster-3
```

**Hub cluster ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-apps
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          environment: production
  template:
    metadata:
      name: '{{name}}-apps'
    spec:
      destination:
        server: '{{server}}'
        namespace: apps
      source:
        repoURL: https://github.com/example/apps
        path: production
```

### Pattern 3: Federation

Multiple fleet repositories, one per region:

```
fleet-us/
├── clusters/
│   ├── us-east-1/
│   ├── us-east-2/
│   └── us-west-1/

fleet-eu/
├── clusters/
│   ├── eu-west-1/
│   ├── eu-west-2/
│   └── eu-central-1/
```

## Change Management Workflows

### Workflow 1: Feature Development

```mermaid
Developer → Feature Branch → PR → Review → Merge → Deploy Dev → Test → Promote Staging → Promote Prod
```

**Steps:**
1. Create feature branch from main
2. Make infrastructure/app changes
3. Open PR with changes
4. Automated checks run (linting, validation)
5. Team reviews changes
6. Merge to main
7. Auto-deploy to development
8. Run integration tests
9. Manual promotion to staging (PR or workflow)
10. Manual promotion to production (PR or workflow)

### Workflow 2: Hotfix

```mermaid
Incident → Hotfix Branch → Quick Review → Merge → Fast-track Deploy
```

**Steps:**
1. Create hotfix branch from production tag
2. Make minimal fix
3. Expedited review
4. Merge and tag
5. Update production environment to new tag
6. Backport to main if needed

### Workflow 3: Scheduled Maintenance

```mermaid
Plan → Maintenance Branch → Review → Schedule → Maintenance Window → Deploy
```

**Steps:**
1. Create maintenance branch
2. Prepare all changes
3. Review and test in staging
4. Schedule maintenance window
5. Create PR to production
6. During window, merge and deploy
7. Monitor and validate

## Disaster Recovery Patterns

### Pattern 1: Git as Backup

```bash
# Restore entire cluster from Git
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --path=clusters/production

# GitOps reconciliation restores all resources
```

### Pattern 2: Periodic Snapshots

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gitops-snapshot
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: snapshot
            image: kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              kubectl get all -A -o yaml > snapshot.yaml
              # Upload to S3/GCS
```

### Pattern 3: Multi-Region GitOps

- Primary region: Active GitOps
- Secondary region: Standby GitOps pointing to same repo
- Failover: Redirect traffic, both regions in sync

## Testing Patterns

### Pattern 1: Pre-merge Validation

```yaml
# GitHub Actions
name: Validate
on: pull_request
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Validate Kubernetes manifests
      run: |
        kubeval **/*.yaml
    - name: Kustomize build
      run: |
        kustomize build environments/production
    - name: Policy check
      run: |
        conftest test -p policies/ environments/production
```

### Pattern 2: Staging Environment Testing

```yaml
# Flux Kustomization with tests
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp-staging
spec:
  interval: 10m
  path: ./staging
  sourceRef:
    kind: GitRepository
    name: myapp
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: myapp
  postBuild:
    substitute:
      test_enabled: "true"
```

### Pattern 3: Canary Testing

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
```

## Observability and Monitoring

### GitOps Metrics to Track

1. **Sync Status**
   - Number of applications out of sync
   - Sync failure rate
   - Time to sync

2. **Deployment Frequency**
   - Commits per day
   - Deployments per environment
   - Lead time from commit to deploy

3. **Change Failure Rate**
   - Failed deployments
   - Rollbacks initiated
   - Time to remediate

4. **Recovery Time**
   - Time to detect issues
   - Time to rollback
   - Time to full recovery

### Monitoring Implementation

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard
data:
  gitops.json: |
    {
      "dashboard": {
        "title": "GitOps Overview",
        "panels": [
          {
            "title": "Sync Status",
            "targets": [{
              "expr": "argocd_app_sync_total"
            }]
          },
          {
            "title": "Health Status",
            "targets": [{
              "expr": "argocd_app_health_status"
            }]
          }
        ]
      }
    }
```

## Best Practices Summary

### Repository Organization
1. Use clear, consistent directory structure
2. Separate infrastructure from applications
3. Use base + overlay pattern for environments
4. Keep secrets encrypted in Git

### Branching Strategy
5. Choose strategy that fits team workflow
6. Main/trunk branch as source of truth
7. Use tags for production releases
8. Feature branches for development

### Change Management
9. All changes via pull requests
10. Automated validation in CI
11. Required reviews for production
12. Audit trail through Git history

### Deployment
13. Automated deployments to dev/staging
14. Manual approval for production
15. Health checks for all applications
16. Automated rollback on failures

### Security
17. Encrypt all secrets before committing
18. Use RBAC for repository access
19. Separate credentials per environment
20. Regular security audits

### Operations
21. Monitor GitOps sync status
22. Alert on sync failures
23. Regular backup validation
24. Document runbooks in repository

## Anti-Patterns to Avoid

### 1. Manual Cluster Changes
Never make manual changes to clusters. Always commit to Git first.

### 2. Secrets in Plaintext
Never commit unencrypted secrets to Git repositories.

### 3. No Testing
Always validate changes in lower environments before production.

### 4. Unclear Ownership
Every repository and application should have clear ownership.

### 5. No Rollback Plan
Always have a tested rollback procedure for deployments.

### 6. Overly Complex Structure
Keep repository structure as simple as possible.

### 7. No Documentation
Document repository structure, promotion process, and runbooks.

### 8. Ignoring Drift
Address configuration drift immediately when detected.

## Additional Resources

- [GitOps Principles](https://opengitops.dev/)
- [CNCF GitOps Working Group](https://github.com/cncf/tag-app-delivery)
- [GitOps Patterns and Best Practices](https://www.weave.works/technologies/gitops/)
