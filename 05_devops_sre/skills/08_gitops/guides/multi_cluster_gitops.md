# Managing Multiple Kubernetes Clusters with GitOps

## Introduction

This guide covers strategies and implementations for managing multiple Kubernetes clusters using GitOps. You'll learn different multi-cluster patterns, from simple environment separation to complex multi-region, multi-cloud deployments.

## Multi-Cluster Architecture Patterns

### Pattern 1: Independent Clusters

Each cluster has its own GitOps operator instance.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Prod Cluster   │     │ Staging Cluster │     │  Dev Cluster    │
│  ┌───────────┐  │     │  ┌───────────┐  │     │  ┌───────────┐  │
│  │   Flux    │  │     │  │   Flux    │  │     │  │   Flux    │  │
│  └─────┬─────┘  │     │  └─────┬─────┘  │     │  └─────┬─────┘  │
└────────┼────────┘     └────────┼────────┘     └────────┼────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                         ┌───────▼────────┐
                         │   Git Repo     │
                         │ clusters/prod  │
                         │ clusters/stage │
                         │ clusters/dev   │
                         └────────────────┘
```

**Pros:**
- Complete isolation
- Independent failure domains
- Different versions possible
- Simple to understand

**Cons:**
- More resource overhead
- Harder to manage centrally
- Need to bootstrap each cluster

### Pattern 2: Hub and Spoke

Central management cluster controls spoke clusters.

```
┌──────────────────────────┐
│    Hub Cluster           │
│  ┌────────────────────┐  │
│  │  ArgoCD/Flux       │  │
│  │  (Management)      │  │
│  └──────┬─────────────┘  │
└─────────┼────────────────┘
          │
    ┌─────┴─────┬──────────────┬──────────────┐
    │           │              │              │
┌───▼───┐  ┌───▼───┐   ┌─────▼────┐  ┌─────▼────┐
│Prod-1 │  │Prod-2 │   │ Staging  │  │   Dev    │
│Spoke  │  │Spoke  │   │  Spoke   │  │  Spoke   │
└───────┘  └───────┘   └──────────┘  └──────────┘
```

**Pros:**
- Centralized management
- Single pane of glass
- Easier RBAC management
- Lower operational overhead

**Cons:**
- Hub is single point of failure
- Requires network connectivity
- More complex setup

### Pattern 3: Federated

Multiple management clusters with shared configuration.

```
┌────────────────┐         ┌────────────────┐
│   US Region    │         │   EU Region    │
│ ┌────────────┐ │         │ ┌────────────┐ │
│ │  Mgmt Hub  │ │         │ │  Mgmt Hub  │ │
│ └──────┬─────┘ │         │ └──────┬─────┘ │
│        │       │         │        │       │
│   ┌────┴───┐  │         │   ┌────┴───┐  │
│   │Cluster1│  │         │   │Cluster3│  │
│   │Cluster2│  │         │   │Cluster4│  │
└────────────────┘         └────────────────┘
         │                          │
         └──────────┬───────────────┘
                    │
            ┌───────▼────────┐
            │  Shared Config │
            │   Repository   │
            └────────────────┘
```

**Pros:**
- Regional isolation
- Better performance
- Disaster recovery
- Compliance boundaries

**Cons:**
- Most complex
- Configuration sync challenges
- Higher operational cost

## Implementation with Flux

### Repository Structure for Multi-Cluster

```
fleet-infra/
├── README.md
├── clusters/
│   ├── production/
│   │   ├── us-east-1/
│   │   │   ├── flux-system/
│   │   │   ├── infrastructure.yaml
│   │   │   └── apps.yaml
│   │   ├── us-west-2/
│   │   │   ├── flux-system/
│   │   │   ├── infrastructure.yaml
│   │   │   └── apps.yaml
│   │   └── eu-west-1/
│   │       ├── flux-system/
│   │       ├── infrastructure.yaml
│   │       └── apps.yaml
│   ├── staging/
│   │   └── us-east-1/
│   └── development/
│       └── us-east-1/
├── infrastructure/
│   ├── base/
│   │   ├── cert-manager/
│   │   ├── ingress-nginx/
│   │   └── monitoring/
│   ├── overlays/
│   │   ├── production/
│   │   ├── staging/
│   │   └── development/
│   └── regions/
│       ├── us-east-1/
│       ├── us-west-2/
│       └── eu-west-1/
└── apps/
    ├── base/
    └── overlays/
        ├── production/
        ├── staging/
        └── development/
```

### Bootstrap Multiple Clusters

#### Production US-East-1

```bash
# Set context to production us-east-1 cluster
kubectl config use-context prod-us-east-1

# Bootstrap Flux
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production/us-east-1 \
  --components-extra=image-reflector-controller,image-automation-controller
```

#### Production US-West-2

```bash
# Set context to production us-west-2 cluster
kubectl config use-context prod-us-west-2

# Bootstrap Flux
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production/us-west-2
```

#### Production EU-West-1

```bash
# Set context to production eu-west-1 cluster
kubectl config use-context prod-eu-west-1

# Bootstrap Flux
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production/eu-west-1
```

### Cluster-Specific Configuration

#### Infrastructure Kustomization

**clusters/production/us-east-1/infrastructure.yaml:**
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: flux-system
  path: ./infrastructure/overlays/production
  prune: true
  wait: true
  timeout: 5m
  postBuild:
    substitute:
      cluster_name: prod-us-east-1
      cluster_region: us-east-1
      environment: production
      aws_region: us-east-1
      domain: us.example.com
    substituteFrom:
    - kind: ConfigMap
      name: cluster-config
```

**clusters/production/us-east-1/cluster-config.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: flux-system
data:
  cluster_name: prod-us-east-1
  cluster_region: us-east-1
  environment: production
  aws_region: us-east-1
  aws_account_id: "123456789012"
  vpc_cidr: "10.0.0.0/16"
  domain: us.example.com
  timezone: America/New_York
```

### Shared Infrastructure with Region-Specific Overrides

**infrastructure/base/ingress-nginx/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: ingress-nginx
resources:
- https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
patches:
- path: service-annotations.yaml
```

**infrastructure/regions/us-east-1/ingress-nginx/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../../base/ingress-nginx
patches:
- patch: |
    apiVersion: v1
    kind: Service
    metadata:
      name: ingress-nginx-controller
      namespace: ingress-nginx
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: nlb
        service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
        service.beta.kubernetes.io/aws-load-balancer-subnets: subnet-abc123,subnet-def456
```

**infrastructure/regions/eu-west-1/ingress-nginx/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../../base/ingress-nginx
patches:
- patch: |
    apiVersion: v1
    kind: Service
    metadata:
      name: ingress-nginx-controller
      namespace: ingress-nginx
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: nlb
        service.beta.kubernetes.io/aws-load-balancer-subnets: subnet-xyz789,subnet-uvw012
```

### Multi-Region Application Deployment

**apps/base/webapp/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: myapp:v1.0.0
        env:
        - name: CLUSTER_NAME
          value: ${cluster_name}
        - name: REGION
          value: ${cluster_region}
        - name: ENVIRONMENT
          value: ${environment}
```

**apps/overlays/production/webapp/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
resources:
- ../../../base/webapp
- ingress.yaml
- hpa.yaml
images:
- name: myapp
  newTag: v1.2.3
patches:
- target:
    kind: Deployment
    name: webapp
  patch: |
    - op: replace
      path: /spec/replicas
      value: 5
```

## Implementation with ArgoCD

### Hub-and-Spoke Architecture

#### Install ArgoCD in Hub Cluster

```bash
# Install ArgoCD in hub cluster
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Register Spoke Clusters

```bash
# Add production cluster 1
argocd cluster add prod-us-east-1-context \
  --name prod-us-east-1 \
  --labels environment=production,region=us-east-1

# Add production cluster 2
argocd cluster add prod-us-west-2-context \
  --name prod-us-west-2 \
  --labels environment=production,region=us-west-2

# Add staging cluster
argocd cluster add staging-us-east-1-context \
  --name staging-us-east-1 \
  --labels environment=staging,region=us-east-1
```

### ApplicationSet for Multi-Cluster

#### Cluster Generator

**applicationset/webapp-cluster-generator.yaml:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: webapp-production
  namespace: argocd
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          environment: production
      values:
        revision: v1.2.3
        replicas: "5"
  template:
    metadata:
      name: 'webapp-{{name}}'
    spec:
      project: production
      source:
        repoURL: https://github.com/myorg/apps
        targetRevision: '{{values.revision}}'
        path: webapp/overlays/production
        helm:
          parameters:
          - name: replicaCount
            value: '{{values.replicas}}'
          - name: cluster.name
            value: '{{name}}'
          - name: cluster.region
            value: '{{metadata.labels.region}}'
      destination:
        server: '{{server}}'
        namespace: production
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

#### List Generator for Specific Clusters

**applicationset/infrastructure-list.yaml:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: infrastructure
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      - cluster: prod-us-east-1
        url: https://prod-us-east-1.k8s.example.com
        region: us-east-1
        environment: production
        domain: us.example.com
      - cluster: prod-us-west-2
        url: https://prod-us-west-2.k8s.example.com
        region: us-west-2
        environment: production
        domain: west.example.com
      - cluster: prod-eu-west-1
        url: https://prod-eu-west-1.k8s.example.com
        region: eu-west-1
        environment: production
        domain: eu.example.com
  template:
    metadata:
      name: 'infrastructure-{{cluster}}'
    spec:
      project: platform
      source:
        repoURL: https://github.com/myorg/infrastructure
        targetRevision: main
        path: overlays/{{environment}}
        kustomize:
          commonAnnotations:
            cluster: '{{cluster}}'
          commonLabels:
            region: '{{region}}'
          patches:
          - target:
              kind: ConfigMap
              name: cluster-vars
            patch: |
              - op: replace
                path: /data/domain
                value: {{domain}}
      destination:
        server: '{{url}}'
        namespace: infrastructure
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

#### Git Directory Generator

**applicationset/apps-git-directory.yaml:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: apps
  namespace: argocd
spec:
  generators:
  - matrix:
      generators:
      - git:
          repoURL: https://github.com/myorg/apps
          revision: main
          directories:
          - path: apps/*
      - clusters:
          selector:
            matchLabels:
              environment: production
  template:
    metadata:
      name: '{{path.basename}}-{{name}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/myorg/apps
        targetRevision: main
        path: '{{path}}/overlays/production'
      destination:
        server: '{{server}}'
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

### AppProject for Multi-Cluster

**projects/production-project.yaml:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production applications across all clusters

  sourceRepos:
  - 'https://github.com/myorg/*'

  destinations:
  # Production US-East-1
  - namespace: '*'
    server: https://prod-us-east-1.k8s.example.com
  # Production US-West-2
  - namespace: '*'
    server: https://prod-us-west-2.k8s.example.com
  # Production EU-West-1
  - namespace: '*'
    server: https://prod-eu-west-1.k8s.example.com

  clusterResourceWhitelist:
  - group: ''
    kind: Namespace
  - group: 'rbac.authorization.k8s.io'
    kind: ClusterRole
  - group: 'rbac.authorization.k8s.io'
    kind: ClusterRoleBinding

  namespaceResourceWhitelist:
  - group: '*'
    kind: '*'

  roles:
  - name: deployer
    description: Deployment access
    policies:
    - p, proj:production:deployer, applications, sync, production/*, allow
    - p, proj:production:deployer, applications, get, production/*, allow
    groups:
    - production-deployers
```

## Multi-Region Considerations

### DNS and Traffic Routing

#### Global Load Balancer with External DNS

**infrastructure/base/external-dns/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: external-dns
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      serviceAccountName: external-dns
      containers:
      - name: external-dns
        image: k8s.gcr.io/external-dns/external-dns:v0.13.5
        args:
        - --source=service
        - --source=ingress
        - --domain-filter=example.com
        - --provider=aws
        - --policy=sync
        - --aws-zone-type=public
        - --registry=txt
        - --txt-owner-id=${cluster_name}
        - --log-level=info
```

#### Region-Specific Ingress

**apps/overlays/production/webapp/ingress-us-east-1.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    external-dns.alpha.kubernetes.io/hostname: us.app.example.com
    external-dns.alpha.kubernetes.io/ttl: "60"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - us.app.example.com
    secretName: webapp-tls
  rules:
  - host: us.app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp
            port:
              number: 80
```

**apps/overlays/production/webapp/ingress-eu-west-1.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    external-dns.alpha.kubernetes.io/hostname: eu.app.example.com
    external-dns.alpha.kubernetes.io/ttl: "60"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - eu.app.example.com
    secretName: webapp-tls
  rules:
  - host: eu.app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp
            port:
              number: 80
```

### Cross-Cluster Service Mesh

#### Istio Multi-Cluster Configuration

**infrastructure/base/istio/primary-cluster.yaml:**
```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: istio
  namespace: istio-system
spec:
  values:
    global:
      meshID: mesh1
      multiCluster:
        clusterName: prod-us-east-1
      network: network1
  meshConfig:
    accessLogFile: /dev/stdout
    defaultConfig:
      proxyMetadata:
        ISTIO_META_DNS_CAPTURE: "true"
```

**infrastructure/base/istio/remote-cluster.yaml:**
```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: istio
  namespace: istio-system
spec:
  values:
    global:
      meshID: mesh1
      multiCluster:
        clusterName: prod-us-west-2
      network: network2
      remotePilotAddress: istio-pilot.istio-system.svc.cluster.local
```

### Data Replication

#### Database Replication ConfigMap

**apps/base/database/replication-config.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-replication
data:
  primary_region: us-east-1
  replica_regions: us-west-2,eu-west-1
  replication_mode: async
  failover_priority: |
    1. us-east-1
    2. us-west-2
    3. eu-west-1
```

## Cluster Promotion Strategy

### Progressive Rollout Across Clusters

#### Stage 1: Canary Cluster

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: webapp-rollout
  namespace: argocd
spec:
  generators:
  - list:
      elements:
      # Stage 1: Canary cluster
      - cluster: prod-us-east-1-canary
        url: https://prod-us-east-1.k8s.example.com
        namespace: canary
        version: v1.3.0
        weight: "10"
  template:
    metadata:
      name: 'webapp-{{cluster}}'
    spec:
      project: production
      source:
        repoURL: https://github.com/myorg/apps
        targetRevision: main
        path: webapp
        helm:
          parameters:
          - name: image.tag
            value: '{{version}}'
          - name: trafficWeight
            value: '{{weight}}'
      destination:
        server: '{{url}}'
        namespace: '{{namespace}}'
      syncPolicy:
        automated:
          prune: true
```

#### Stage 2: Primary Region

After canary validation:

```yaml
- cluster: prod-us-east-1
  url: https://prod-us-east-1.k8s.example.com
  namespace: production
  version: v1.3.0
  weight: "100"
```

#### Stage 3: Secondary Regions

After primary region stabilizes:

```yaml
- cluster: prod-us-west-2
  url: https://prod-us-west-2.k8s.example.com
  namespace: production
  version: v1.3.0
  weight: "100"
- cluster: prod-eu-west-1
  url: https://prod-eu-west-1.k8s.example.com
  namespace: production
  version: v1.3.0
  weight: "100"
```

## Disaster Recovery

### Cluster Failover Strategy

#### Active-Active Configuration

**infrastructure/base/failover/global-config.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: failover-config
  namespace: infrastructure
data:
  mode: active-active
  health_check_interval: 30s
  failover_threshold: 3
  primary_regions: us-east-1,eu-west-1
  secondary_regions: us-west-2
```

#### Active-Passive Configuration

**infrastructure/base/failover/global-config.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: failover-config
  namespace: infrastructure
data:
  mode: active-passive
  primary_region: us-east-1
  secondary_region: us-west-2
  auto_failover: "true"
  failback: "false"
```

### Backup Strategy

**infrastructure/base/velero/schedule.yaml:**
```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"
  template:
    includedNamespaces:
    - production
    - staging
    excludedResources:
    - events
    - events.events.k8s.io
    storageLocation: default
    volumeSnapshotLocations:
    - default
    ttl: 720h0m0s
```

## Monitoring Multi-Cluster Deployments

### Centralized Prometheus

**infrastructure/base/monitoring/prometheus-federation.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 30s

    scrape_configs:
    # Federate from prod-us-east-1
    - job_name: 'federate-us-east-1'
      scrape_interval: 60s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
        - '{job="kubernetes-pods"}'
        - '{job="kubernetes-nodes"}'
      static_configs:
      - targets:
        - 'prometheus.prod-us-east-1.example.com'
        labels:
          cluster: 'prod-us-east-1'
          region: 'us-east-1'

    # Federate from prod-us-west-2
    - job_name: 'federate-us-west-2'
      scrape_interval: 60s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
        - '{job="kubernetes-pods"}'
        - '{job="kubernetes-nodes"}'
      static_configs:
      - targets:
        - 'prometheus.prod-us-west-2.example.com'
        labels:
          cluster: 'prod-us-west-2'
          region: 'us-west-2'
```

### Multi-Cluster Grafana Dashboard

**infrastructure/base/monitoring/grafana-multi-cluster-dashboard.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: multi-cluster-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  multi-cluster.json: |
    {
      "dashboard": {
        "title": "Multi-Cluster Overview",
        "panels": [
          {
            "title": "Cluster Health",
            "targets": [{
              "expr": "up{job=\"kubernetes-nodes\"}"
            }]
          },
          {
            "title": "Pod Count by Cluster",
            "targets": [{
              "expr": "sum(kube_pod_info) by (cluster)"
            }]
          },
          {
            "title": "GitOps Sync Status",
            "targets": [{
              "expr": "gotk_reconcile_condition{type=\"Ready\"}"
            }]
          }
        ],
        "templating": {
          "list": [
            {
              "name": "cluster",
              "type": "query",
              "query": "label_values(up, cluster)"
            }
          ]
        }
      }
    }
```

## Best Practices

### 1. Cluster Naming
- Use consistent naming: `{environment}-{region}-{number}`
- Examples: `prod-us-east-1`, `staging-eu-west-1`

### 2. Configuration Management
- Share common configuration
- Use overlays for cluster-specific settings
- Leverage variable substitution

### 3. Promotion Strategy
- Test in canary clusters first
- Gradual rollout across regions
- Automated validation gates

### 4. Disaster Recovery
- Regular backup testing
- Document failover procedures
- Automate recovery where possible

### 5. Monitoring
- Centralized metrics and logs
- Per-cluster and cross-cluster views
- Alert on sync failures

### 6. Security
- Separate credentials per cluster
- Use workload identity
- Implement network policies

### 7. Cost Optimization
- Right-size management overhead
- Share infrastructure where appropriate
- Monitor resource utilization

## Troubleshooting

### Cluster Registration Issues

```bash
# List registered clusters
argocd cluster list

# Test cluster connectivity
kubectl --context=prod-us-east-1 get nodes

# Re-add cluster
argocd cluster add prod-us-east-1 --name prod-us-east-1
```

### ApplicationSet Not Creating Applications

```bash
# Check ApplicationSet status
kubectl describe applicationset -n argocd webapp-production

# View generated applications
argocd app list --selector argocd.argoproj.io/application-set-name=webapp-production

# Check generator output
kubectl get applicationset webapp-production -n argocd -o yaml
```

### Cross-Cluster Communication Issues

```bash
# Test DNS resolution
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- nslookup service.namespace.svc.cluster.local

# Test service mesh connectivity
istioctl pc endpoint deployment/webapp -n production

# Check network policies
kubectl get networkpolicy -A
```

## Additional Resources

- [Flux Multi-Cluster](https://fluxcd.io/flux/guides/multi-tenancy/)
- [ArgoCD ApplicationSet](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/)
- [Istio Multi-Cluster](https://istio.io/latest/docs/setup/install/multicluster/)
- [Kubernetes Federation](https://github.com/kubernetes-sigs/kubefed)
