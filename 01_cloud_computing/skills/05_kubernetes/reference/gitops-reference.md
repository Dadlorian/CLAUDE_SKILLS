# GitOps Reference

## GitOps Principles

### Core Tenets
1. **Declarative**: System state described declaratively
2. **Versioned and Immutable**: State stored in version control (Git)
3. **Pulled Automatically**: Software agents pull desired state from Git
4. **Continuously Reconciled**: Agents ensure actual state matches desired state

### Benefits
- Single source of truth in Git
- Audit trail and rollback capability
- Disaster recovery (cluster recreation from Git)
- Improved security (no cluster credentials in CI)
- Collaboration through pull requests
- Automated deployments

## ArgoCD

### Architecture

**Components**:
- **API Server**: REST/gRPC API, web UI
- **Repository Server**: Clones Git repos, generates manifests
- **Application Controller**: Watches applications, compares desired vs actual state
- **Redis**: Caching
- **Dex** (optional): SSO integration

### Installation

**Helm**:
```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd -n argocd --create-namespace
```

**Manifests**:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Access UI**:
```bash
# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Application CRD

**Basic Application**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp
    targetRevision: HEAD
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

**Helm Application**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-helm
spec:
  source:
    repoURL: https://github.com/myorg/charts
    targetRevision: HEAD
    path: myapp
    helm:
      releaseName: myapp
      parameters:
      - name: image.tag
        value: v1.2.3
      valueFiles:
      - values-production.yaml
```

**Kustomize Application**:
```yaml
spec:
  source:
    repoURL: https://github.com/myorg/myapp
    path: k8s/overlays/production
    kustomize:
      version: v4.5.7
      namePrefix: prod-
      commonLabels:
        environment: production
      images:
      - name: myapp
        newTag: v1.2.3
```

**Multiple Sources** (ArgoCD 2.6+):
```yaml
spec:
  sources:
  - repoURL: https://github.com/myorg/myapp
    path: k8s
  - repoURL: https://github.com/myorg/configs
    path: production
    targetRevision: main
```

### AppProject

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production applications
  sourceRepos:
  - 'https://github.com/myorg/*'
  destinations:
  - namespace: 'production-*'
    server: https://kubernetes.default.svc
  - namespace: argocd
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: ''
    kind: Namespace
  namespaceResourceWhitelist:
  - group: 'apps'
    kind: Deployment
  - group: ''
    kind: Service
  - group: 'networking.k8s.io'
    kind: Ingress
  orphanedResources:
    warn: true
```

### Sync Waves and Hooks

**Sync Waves** (order resources):
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"  # -5 to 5, lower first
```

**Resource Hooks**:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
```

**Hook Types**:
- `PreSync`: Before sync
- `Sync`: During sync (rare)
- `PostSync`: After sync
- `SyncFail`: On sync failure
- `Skip`: Don't sync this resource

### Sync Options

```yaml
syncPolicy:
  syncOptions:
  - CreateNamespace=true
  - PrunePropagationPolicy=foreground
  - PruneLast=true
  - RespectIgnoreDifferences=true
  - ApplyOutOfSyncOnly=true
  - ServerSideApply=true
```

### Health Assessment

**Custom Health Check**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations: |
    networking.k8s.io/Ingress:
      health.lua: |
        hs = {}
        hs.status = "Healthy"
        if obj.status ~= nil then
          if obj.status.loadBalancer ~= nil and obj.status.loadBalancer.ingress ~= nil then
            hs.status = "Healthy"
            hs.message = "Ingress has LoadBalancer"
          else
            hs.status = "Progressing"
            hs.message = "Waiting for LoadBalancer"
          end
        end
        return hs
```

### Multi-Cluster Management

**Add Cluster**:
```bash
# Using kubeconfig context
argocd cluster add my-cluster-context

# Using service account
kubectl create sa argocd-manager -n kube-system
kubectl create clusterrolebinding argocd-manager --clusterrole=cluster-admin --serviceaccount=kube-system:argocd-manager
```

**Cluster Secret**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster-my-cluster
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: my-cluster
  server: https://my-cluster-api:6443
  config: |
    {
      "bearerToken": "<token>",
      "tlsClientConfig": {
        "insecure": false,
        "caData": "<base64-ca-cert>"
      }
    }
```

### ApplicationSet

**Git Generator**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: guestbook
spec:
  generators:
  - git:
      repoURL: https://github.com/myorg/myapp
      revision: HEAD
      directories:
      - path: environments/*
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/myapp
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
```

**Cluster Generator**:
```yaml
generators:
- clusters:
    selector:
      matchLabels:
        environment: production
template:
  metadata:
    name: '{{name}}-myapp'
  spec:
    source:
      repoURL: https://github.com/myorg/myapp
      path: k8s
    destination:
      server: '{{server}}'
      namespace: myapp
```

**List Generator**:
```yaml
generators:
- list:
    elements:
    - cluster: prod-us-east
      url: https://prod-us-east.k8s.local
    - cluster: prod-eu-west
      url: https://prod-eu-west.k8s.local
```

## Flux CD

### Architecture

**Components**:
- **Source Controller**: Handles Git/Helm repos, OCI artifacts
- **Kustomize Controller**: Reconciles Kustomize resources
- **Helm Controller**: Reconciles Helm releases
- **Notification Controller**: Event handling and notifications
- **Image Reflector/Automation**: Image updates

### Installation

```bash
# Install CLI
curl -s https://fluxcd.io/install.sh | bash

# Pre-check
flux check --pre

# Bootstrap
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --path=clusters/production \
  --personal
```

### GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/myorg/myapp
  ref:
    branch: main
  secretRef:
    name: git-credentials
  ignore: |
    .git/
    .github/
    **/*.md
```

### Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  retryInterval: 1m
  timeout: 5m
  sourceRef:
    kind: GitRepository
    name: myapp
  path: ./k8s/production
  prune: true
  wait: true
  validation: client
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: myapp
    namespace: production
  dependsOn:
  - name: infrastructure
```

### HelmRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: bitnami
  namespace: flux-system
spec:
  interval: 1h
  url: https://charts.bitnami.com/bitnami
```

### HelmRelease

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: nginx
  namespace: default
spec:
  interval: 10m
  chart:
    spec:
      chart: nginx
      version: '13.x'
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  values:
    replicaCount: 3
    service:
      type: LoadBalancer
  valuesFrom:
  - kind: ConfigMap
    name: nginx-values
  install:
    remediation:
      retries: 3
  upgrade:
    remediation:
      retries: 3
      remediateLastFailure: true
  rollback:
    recreate: true
```

### Image Automation

**ImageRepository**:
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  image: ghcr.io/myorg/myapp
  interval: 1m
```

**ImagePolicy**:
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
      range: '>=1.0.0 <2.0.0'
```

**ImageUpdateAutomation**:
```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
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
      messageTemplate: 'Update image to {{range .Updated.Images}}{{println .}}{{end}}'
    push:
      branch: main
  update:
    path: ./k8s
    strategy: Setters
```

**Image Policy Marker**:
```yaml
spec:
  containers:
  - name: myapp
    image: ghcr.io/myorg/myapp:1.0.0 # {"$imagepolicy": "flux-system:myapp"}
```

### Notifications

**Provider**:
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: deployments
  secretRef:
    name: slack-webhook
```

**Alert**:
```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: deployment-alerts
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
  - kind: Kustomization
    name: '*'
  - kind: HelmRelease
    name: '*'
```

## Progressive Delivery

### Argo Rollouts

**Rollout Resource**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 1m}
      - setWeight: 40
      - pause: {duration: 1m}
      - setWeight: 60
      - pause: {duration: 1m}
      - setWeight: 80
      - pause: {duration: 1m}
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v2
        ports:
        - containerPort: 8080
```

**Blue-Green Strategy**:
```yaml
spec:
  strategy:
    blueGreen:
      activeService: myapp
      previewService: myapp-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
```

**Analysis**:
```yaml
spec:
  strategy:
    canary:
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 2
        args:
        - name: service-name
          value: myapp
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result >= 0.95
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(
            http_requests_total{service="{{args.service-name}}",status!~"5.*"}[1m]
          )) /
          sum(rate(
            http_requests_total{service="{{args.service-name}}"}[1m]
          ))
```

### Flagger

**Canary**:
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
    port: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        type: cmd
        cmd: "hey -z 1m -q 10 -c 2 http://myapp-canary:8080/"
```

## Best Practices

### Repository Structure

**Monorepo**:
```
fleet-infra/
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   └── applications/
│   └── staging/
│       ├── flux-system/
│       └── applications/
├── infrastructure/
│   ├── base/
│   └── overlays/
└── applications/
    ├── base/
    └── overlays/
```

**Multi-Repo**:
```
app-repo/               # Application code
├── src/
└── k8s/                # K8s manifests

config-repo/            # GitOps config
├── apps/
│   └── myapp/
└── infrastructure/
```

### Security
- Store secrets externally (Sealed Secrets, External Secrets)
- Use SSH keys or deploy keys for Git access
- Implement RBAC for ArgoCD/Flux
- Sign commits
- Enable branch protection
- Audit Git access logs

### Operations
- Use ApplicationSets/Kustomizations for multi-environment
- Implement progressive delivery for critical apps
- Monitor sync status
- Set up alerting for sync failures
- Regular backup of ArgoCD/Flux state
- Document promotion workflows

### Automation
- Automate image updates (with approval)
- Use webhooks for faster sync
- Implement automated testing in PR
- Use semantic versioning
- Tag releases in Git

## Comparison: ArgoCD vs Flux

| Feature | ArgoCD | Flux |
|---------|--------|------|
| UI | Built-in web UI | No (use Weave GitOps) |
| Architecture | Monolithic | Modular (GitOps Toolkit) |
| CRDs | Application, AppProject | Multiple controllers |
| Multi-tenancy | AppProjects | Namespaces + RBAC |
| Helm Support | Native | HelmRelease controller |
| Image Automation | External (ArgoCD Image Updater) | Built-in |
| Notifications | Built-in | Built-in |
| Progressive Delivery | Argo Rollouts (separate) | Flagger |
| CLI | argocd CLI | flux CLI |
| Complexity | Medium | Low |

## References

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Flux Documentation](https://fluxcd.io/docs/)
- [Argo Rollouts](https://argoproj.github.io/argo-rollouts/)
- [Flagger](https://flagger.app/)
- [GitOps Principles](https://opengitops.dev/)
