# Flux GitOps Toolkit Reference Guide

## Overview

Flux is a set of continuous and progressive delivery solutions for Kubernetes that are open and extensible. Flux v2 (GitOps Toolkit) is built as a collection of specialized tools and controllers.

## Core Components

### Source Controller

Manages sources of truth for GitOps:
- **GitRepository**: Git repositories
- **HelmRepository**: Helm chart repositories
- **HelmChart**: Helm charts from repositories
- **Bucket**: Cloud storage buckets (S3, GCS, Azure Blob)

### Kustomize Controller

Reconciles cluster state from Kustomize overlays:
- **Kustomization**: Applies Kustomize builds to the cluster

### Helm Controller

Manages Helm releases:
- **HelmRelease**: Declarative Helm releases

### Notification Controller

Handles events and notifications:
- **Alert**: Notification routing
- **Provider**: Notification providers (Slack, Discord, etc.)
- **Receiver**: Webhook receivers

### Image Automation Controllers

Automates image updates:
- **ImageRepository**: Scans container registries
- **ImagePolicy**: Defines image selection rules
- **ImageUpdateAutomation**: Updates Git with new images

## Installation

### Prerequisites

```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Verify installation
flux --version
```

### Bootstrap Flux

#### GitHub Bootstrap

```bash
# Export GitHub token
export GITHUB_TOKEN=<your-token>

# Bootstrap Flux
flux bootstrap github \
  --owner=my-github-username \
  --repository=my-repository \
  --branch=main \
  --path=clusters/production \
  --personal \
  --private=false
```

#### GitLab Bootstrap

```bash
# Export GitLab token
export GITLAB_TOKEN=<your-token>

# Bootstrap Flux
flux bootstrap gitlab \
  --owner=my-gitlab-group \
  --repository=my-repository \
  --branch=main \
  --path=clusters/production \
  --token-auth
```

#### Generic Git Bootstrap

```bash
flux bootstrap git \
  --url=ssh://git@github.com/example/repo \
  --branch=main \
  --path=clusters/production \
  --private-key-file=/path/to/ssh/key
```

### Install Flux Components Manually

```bash
# Create namespace
kubectl create namespace flux-system

# Install Flux components
flux install \
  --namespace=flux-system \
  --network-policy=true \
  --components=source-controller,kustomize-controller,helm-controller,notification-controller
```

## GitRepository Source

### Basic GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 5m
  url: https://github.com/example/myapp
  ref:
    branch: main
  secretRef:
    name: git-credentials
```

### GitRepository with SSH

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp-ssh
  namespace: flux-system
spec:
  interval: 5m
  url: ssh://git@github.com/example/myapp.git
  ref:
    branch: main
  secretRef:
    name: ssh-credentials
---
apiVersion: v1
kind: Secret
metadata:
  name: ssh-credentials
  namespace: flux-system
type: Opaque
data:
  identity: <base64-encoded-private-key>
  known_hosts: <base64-encoded-known-hosts>
```

### GitRepository with Specific Tag/Commit

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp-versioned
  namespace: flux-system
spec:
  interval: 10m
  url: https://github.com/example/myapp
  ref:
    tag: v1.2.3
    # OR
    # commit: abc123def456
    # semver: ">=1.0.0 <2.0.0"
  ignore: |
    # exclude all
    /*
    # include charts directory
    !/charts/
```

## Kustomization

### Basic Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  path: ./k8s/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  targetNamespace: myapp
```

### Kustomization with Post-Build Variable Substitution

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp-with-vars
  namespace: flux-system
spec:
  interval: 10m
  path: ./k8s
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  postBuild:
    substitute:
      cluster_name: production
      domain: example.com
      replicas: "3"
    substituteFrom:
    - kind: ConfigMap
      name: cluster-vars
    - kind: Secret
      name: cluster-secrets
```

### Kustomization with Health Checks

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp-with-health
  namespace: flux-system
spec:
  interval: 10m
  path: ./k8s
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: myapp
    namespace: production
  - apiVersion: v1
    kind: Service
    name: myapp
    namespace: production
  timeout: 5m
  wait: true
```

### Kustomization with Dependencies

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  path: ./k8s/myapp
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  dependsOn:
  - name: infrastructure
  - name: database
```

### Kustomization with Patches

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp-patched
  namespace: flux-system
spec:
  interval: 10m
  path: ./k8s/base
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  patches:
  - patch: |
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: myapp
      spec:
        replicas: 3
    target:
      kind: Deployment
      name: myapp
  - patch: |
      - op: replace
        path: /spec/template/spec/containers/0/image
        value: myapp:v2.0.0
    target:
      kind: Deployment
      name: myapp
```

## HelmRepository Source

### Public Helm Repository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 30m
  url: https://charts.bitnami.com/bitnami
```

### Private Helm Repository with Basic Auth

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: private-charts
  namespace: flux-system
spec:
  interval: 30m
  url: https://charts.example.com
  secretRef:
    name: helm-credentials
---
apiVersion: v1
kind: Secret
metadata:
  name: helm-credentials
  namespace: flux-system
type: Opaque
stringData:
  username: myuser
  password: mypassword
```

### OCI Helm Repository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: oci-registry
  namespace: flux-system
spec:
  interval: 30m
  type: oci
  url: oci://ghcr.io/example/charts
  secretRef:
    name: oci-credentials
```

## HelmRelease

### Basic HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: nginx
  namespace: flux-system
spec:
  interval: 30m
  chart:
    spec:
      chart: nginx
      version: "15.x"
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  values:
    replicaCount: 2
    service:
      type: LoadBalancer
```

### HelmRelease with Values from ConfigMap/Secret

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 30m
  chart:
    spec:
      chart: myapp
      version: "1.2.3"
      sourceRef:
        kind: HelmRepository
        name: private-charts
  valuesFrom:
  - kind: ConfigMap
    name: myapp-values
    valuesKey: values.yaml
  - kind: Secret
    name: myapp-secrets
    valuesKey: secrets.yaml
  values:
    image:
      repository: myapp
      tag: v1.2.3
    replicas: 3
```

### HelmRelease from Git

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: myapp-git
  namespace: flux-system
spec:
  interval: 30m
  chart:
    spec:
      chart: ./charts/myapp
      sourceRef:
        kind: GitRepository
        name: myapp
        namespace: flux-system
      interval: 10m
  values:
    image:
      tag: v1.2.3
```

### HelmRelease with Rollback and Testing

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: myapp-safe
  namespace: flux-system
spec:
  interval: 30m
  chart:
    spec:
      chart: myapp
      version: ">=1.0.0 <2.0.0"
      sourceRef:
        kind: HelmRepository
        name: private-charts
  install:
    createNamespace: true
    remediation:
      retries: 3
  upgrade:
    remediation:
      retries: 3
      remediateLastFailure: true
    cleanupOnFail: true
  test:
    enable: true
  rollback:
    recreate: true
    force: true
    cleanupOnFail: true
  timeout: 10m
```

### HelmRelease with Post-Renderers

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: myapp-postrender
  namespace: flux-system
spec:
  interval: 30m
  chart:
    spec:
      chart: myapp
      sourceRef:
        kind: HelmRepository
        name: private-charts
  postRenderers:
  - kustomize:
      patches:
      - target:
          kind: Deployment
        patch: |
          - op: add
            path: /spec/template/spec/securityContext
            value:
              runAsNonRoot: true
              runAsUser: 1000
```

## Image Automation

### ImageRepository

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  image: ghcr.io/example/myapp
  interval: 5m
  secretRef:
    name: registry-credentials
```

### ImagePolicy

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: myapp
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: myapp
  policy:
    semver:
      range: ">=1.0.0 <2.0.0"
    # OR
    # numerical:
    #   order: asc
    # OR
    # alphabetical:
    #   order: asc
  filterTags:
    pattern: '^v[0-9]+\.[0-9]+\.[0-9]+$'
    extract: '$0'
```

### ImageUpdateAutomation

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 30m
  sourceRef:
    kind: GitRepository
    name: myapp
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxcdbot@users.noreply.github.com
        name: fluxcdbot
      messageTemplate: |
        Automated image update

        Automation name: {{ .AutomationObject }}

        Files:
        {{ range $filename, $_ := .Updated.Files -}}
        - {{ $filename }}
        {{ end -}}

        Objects:
        {{ range $resource, $_ := .Updated.Objects -}}
        - {{ $resource.Kind }} {{ $resource.Name }}
        {{ end -}}

        Images:
        {{ range .Updated.Images -}}
        - {{.}}
        {{ end -}}
    push:
      branch: main
  update:
    path: ./k8s/production
    strategy: Setters
```

### Image Update Markers

In your Kubernetes manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: ghcr.io/example/myapp:v1.0.0 # {"$imagepolicy": "flux-system:myapp"}
```

## Notifications

### Alert Provider - Slack

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: gitops-notifications
  secretRef:
    name: slack-url
---
apiVersion: v1
kind: Secret
metadata:
  name: slack-url
  namespace: flux-system
stringData:
  address: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Alert Provider - Microsoft Teams

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: teams
  namespace: flux-system
spec:
  type: msteams
  secretRef:
    name: teams-url
---
apiVersion: v1
kind: Secret
metadata:
  name: teams-url
  namespace: flux-system
stringData:
  address: https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK
```

### Alert Configuration

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Alert
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  summary: "Production cluster notifications"
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
  - kind: GitRepository
    name: '*'
  - kind: Kustomization
    name: '*'
  - kind: HelmRelease
    name: '*'
  exclusionList:
  - ".*upgrade.*has.*started"
  - ".*is.*not.*ready"
```

### Webhook Receiver

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1
kind: Receiver
metadata:
  name: github-receiver
  namespace: flux-system
spec:
  type: github
  events:
  - "ping"
  - "push"
  secretRef:
    name: webhook-token
  resources:
  - apiVersion: source.toolkit.fluxcd.io/v1
    kind: GitRepository
    name: myapp
    namespace: flux-system
---
apiVersion: v1
kind: Secret
metadata:
  name: webhook-token
  namespace: flux-system
type: Opaque
stringData:
  token: your-webhook-secret-token
```

## Multi-Tenancy

### Tenant Structure

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: team-alpha
  namespace: team-alpha
spec:
  interval: 5m
  url: https://github.com/example/team-alpha
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: team-alpha
  namespace: team-alpha
spec:
  interval: 10m
  path: ./k8s
  prune: true
  sourceRef:
    kind: GitRepository
    name: team-alpha
  serviceAccountName: team-alpha
  targetNamespace: team-alpha
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: team-alpha
  namespace: team-alpha
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-alpha
  namespace: team-alpha
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: team-alpha
  namespace: team-alpha
```

## CLI Commands Reference

### Bootstrap Commands

```bash
# Check prerequisites
flux check --pre

# Bootstrap GitHub
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production

# Uninstall Flux
flux uninstall --silent
```

### Source Commands

```bash
# Create GitRepository
flux create source git myapp \
  --url=https://github.com/example/myapp \
  --branch=main \
  --interval=5m

# Create HelmRepository
flux create source helm bitnami \
  --url=https://charts.bitnami.com/bitnami \
  --interval=30m

# List sources
flux get sources all

# Reconcile source
flux reconcile source git myapp

# Suspend/Resume source
flux suspend source git myapp
flux resume source git myapp
```

### Kustomization Commands

```bash
# Create Kustomization
flux create kustomization myapp \
  --source=GitRepository/myapp \
  --path=./k8s \
  --prune=true \
  --interval=10m

# List Kustomizations
flux get kustomizations

# Reconcile Kustomization
flux reconcile kustomization myapp

# Suspend/Resume Kustomization
flux suspend kustomization myapp
flux resume kustomization myapp
```

### HelmRelease Commands

```bash
# Create HelmRelease
flux create helmrelease nginx \
  --source=HelmRepository/bitnami \
  --chart=nginx \
  --chart-version="15.x" \
  --interval=30m

# List HelmReleases
flux get helmreleases

# Reconcile HelmRelease
flux reconcile helmrelease nginx

# Suspend/Resume HelmRelease
flux suspend helmrelease nginx
flux resume helmrelease nginx
```

### Image Automation Commands

```bash
# Create ImageRepository
flux create image repository myapp \
  --image=ghcr.io/example/myapp \
  --interval=5m

# Create ImagePolicy
flux create image policy myapp \
  --image-ref=myapp \
  --semver=">=1.0.0"

# Create ImageUpdateAutomation
flux create image update myapp \
  --git-repo-ref=myapp \
  --git-repo-path=./k8s \
  --checkout-branch=main \
  --push-branch=main \
  --author-name=fluxcdbot \
  --author-email=fluxcdbot@users.noreply.github.com \
  --commit-template="{{range .Updated.Images}}{{println .}}{{end}}"

# List image automation
flux get images all
```

### Export Commands

```bash
# Export GitRepository
flux export source git myapp

# Export Kustomization
flux export kustomization myapp

# Export HelmRelease
flux export helmrelease nginx

# Export all resources
flux export source git myapp > myapp-git.yaml
flux export kustomization myapp > myapp-ks.yaml
```

### Debugging Commands

```bash
# Check cluster status
flux check

# Get events
flux events

# Logs for controllers
flux logs --level=info --all-namespaces

# Trace Kustomization
flux trace myapp --kind=Kustomization --api-version=kustomize.toolkit.fluxcd.io/v1

# Build Kustomization locally
flux build kustomization myapp --path ./k8s

# Diff Kustomization
flux diff kustomization myapp --path ./k8s
```

## Best Practices

### 1. Repository Structure

Organize repositories by environment and team:
```
fleet-infra/
├── clusters/
│   ├── production/
│   └── staging/
├── infrastructure/
│   ├── sources/
│   └── configs/
└── teams/
    ├── team-alpha/
    └── team-beta/
```

### 2. Use Dependencies

Define dependencies between Kustomizations to ensure proper ordering.

### 3. Health Checks

Always define health checks for critical resources.

### 4. Progressive Delivery

Use Flagger with Flux for canary deployments and progressive delivery.

### 5. Secret Management

Integrate with SOPS, Sealed Secrets, or external secret operators.

### 6. Image Automation

Use image automation for development environments, manual approvals for production.

### 7. Notifications

Set up alerts for all critical resources and environments.

### 8. Resource Limits

Set appropriate resource limits on Flux controllers.

### 9. Backup Strategy

Regularly backup flux-system namespace and Git repositories.

### 10. Monitoring

Monitor Flux controllers with Prometheus and Grafana.

## Troubleshooting

### Reconciliation Failures

```bash
# Check Kustomization status
flux get kustomization myapp

# View detailed events
kubectl describe kustomization myapp -n flux-system

# Check controller logs
flux logs --kind=kustomization-controller --since=10m
```

### Source Sync Issues

```bash
# Check GitRepository status
flux get sources git

# Force reconciliation
flux reconcile source git myapp --with-source

# Check source controller logs
flux logs --kind=source-controller
```

### HelmRelease Issues

```bash
# Check HelmRelease status
flux get helmreleases

# View Helm release history
helm history myapp -n flux-system

# Check helm controller logs
flux logs --kind=helm-controller
```

## Security Considerations

### 1. RBAC

Implement least-privilege RBAC for Flux service accounts.

### 2. Network Policies

Restrict network access to Flux controllers.

### 3. Secret Encryption

Use SOPS or similar tools to encrypt secrets in Git.

### 4. Webhook Security

Always use webhook tokens and validate webhook payloads.

### 5. Image Scanning

Scan container images before deployment.

### 6. Git Authentication

Use SSH keys or deploy tokens with minimum required permissions.

## Integration with Other Tools

### SOPS (Secret Encryption)

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  path: ./k8s
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp
  decryption:
    provider: sops
    secretRef:
      name: sops-gpg
```

### Flagger (Progressive Delivery)

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
  namespace: production
spec:
  provider: istio
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  progressDeadlineSeconds: 600
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
```

## Additional Resources

- [Flux Documentation](https://fluxcd.io/docs/)
- [Flux GitHub](https://github.com/fluxcd/flux2)
- [Flux Best Practices](https://fluxcd.io/flux/guides/)
- [GitOps Toolkit Components](https://fluxcd.io/flux/components/)
