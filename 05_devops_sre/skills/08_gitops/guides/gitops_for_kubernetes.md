# Managing Kubernetes Clusters with GitOps

## Introduction

This comprehensive guide covers managing Kubernetes clusters using GitOps principles. You'll learn how to declaratively manage infrastructure, applications, and configurations using Git as the single source of truth.

## GitOps Principles for Kubernetes

### 1. Declarative Configuration

All Kubernetes resources are defined declaratively in Git:
- Deployments
- Services
- ConfigMaps
- Secrets (encrypted)
- Custom Resources
- Cluster configuration

### 2. Version Control Everything

Git provides:
- Complete audit trail
- Easy rollbacks
- Change review process
- Collaborative workflows

### 3. Automated Synchronization

GitOps operators continuously:
- Monitor Git repositories
- Detect configuration drift
- Reconcile cluster state
- Apply changes automatically

### 4. Observability

Monitor and observe:
- Sync status
- Deployment health
- Resource metrics
- Application logs

## Repository Structure for Kubernetes

### Recommended Structure

```
k8s-gitops/
├── README.md
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   ├── infrastructure/
│   │   └── apps/
│   ├── staging/
│   │   ├── flux-system/
│   │   ├── infrastructure/
│   │   └── apps/
│   └── development/
│       ├── flux-system/
│       ├── infrastructure/
│       └── apps/
├── infrastructure/
│   ├── base/
│   │   ├── namespaces/
│   │   ├── cert-manager/
│   │   ├── ingress-nginx/
│   │   ├── sealed-secrets/
│   │   ├── metrics-server/
│   │   ├── prometheus/
│   │   └── grafana/
│   └── overlays/
│       ├── production/
│       ├── staging/
│       └── development/
├── apps/
│   ├── base/
│   │   ├── webapp/
│   │   ├── api/
│   │   ├── worker/
│   │   └── database/
│   └── overlays/
│       ├── production/
│       ├── staging/
│       └── development/
└── policies/
    ├── network-policies/
    ├── pod-security-policies/
    ├── resource-quotas/
    └── limit-ranges/
```

## Infrastructure Management

### Managing Core Infrastructure

#### Namespaces

**infrastructure/base/namespaces/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- production.yaml
- staging.yaml
- monitoring.yaml
- logging.yaml
```

**infrastructure/base/namespaces/production.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
    managed-by: gitops
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    persistentvolumeclaims: "10"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: production-limits
  namespace: production
spec:
  limits:
  - max:
      cpu: "4"
      memory: 8Gi
    min:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
```

#### Ingress Controller

**infrastructure/base/ingress-nginx/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: ingress-nginx
resources:
- namespace.yaml
- https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
patches:
- path: patches/service.yaml
```

**infrastructure/overlays/production/ingress-nginx/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../../base/ingress-nginx
patches:
- path: replicas.yaml
configMapGenerator:
- name: ingress-nginx-controller
  namespace: ingress-nginx
  behavior: merge
  literals:
  - use-forwarded-headers="true"
  - compute-full-forwarded-for="true"
  - use-proxy-protocol="false"
```

#### Cert Manager

**infrastructure/base/cert-manager/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: cert-manager
resources:
- namespace.yaml
- https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
- cluster-issuer.yaml
```

**infrastructure/base/cert-manager/cluster-issuer.yaml:**
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Managing Monitoring Stack

#### Prometheus

**infrastructure/base/prometheus/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: monitoring
resources:
- namespace.yaml
- https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
- servicemonitor.yaml
- prometheus.yaml
```

**infrastructure/base/prometheus/prometheus.yaml:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources:
  - nodes
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources:
  - configmaps
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
---
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 2
  serviceAccountName: prometheus
  serviceMonitorSelector:
    matchLabels:
      team: platform
  resources:
    requests:
      memory: 400Mi
      cpu: 500m
    limits:
      memory: 2Gi
      cpu: 2000m
  retention: 30d
  storage:
    volumeClaimTemplate:
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 50Gi
```

#### Grafana

**infrastructure/base/grafana/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: monitoring
resources:
- deployment.yaml
- service.yaml
- ingress.yaml
configMapGenerator:
- name: grafana-datasources
  files:
  - datasources.yaml
secretGenerator:
- name: grafana-admin
  literals:
  - admin-user=admin
  - admin-password=changeme
```

## Application Deployment Patterns

### Pattern 1: Kustomize-Based Deployment

#### Base Configuration

**apps/base/webapp/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    app: webapp
spec:
  replicas: 2
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
        image: myapp:latest
        ports:
        - containerPort: 8080
        env:
        - name: LOG_LEVEL
          value: info
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

**apps/base/webapp/service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp
  labels:
    app: webapp
spec:
  selector:
    app: webapp
  ports:
  - name: http
    port: 80
    targetPort: 8080
  type: ClusterIP
```

**apps/base/webapp/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
- configmap.yaml
commonLabels:
  app: webapp
  managed-by: gitops
```

#### Production Overlay

**apps/overlays/production/webapp/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
resources:
- ../../../base/webapp
- ingress.yaml
- hpa.yaml
- pdb.yaml

images:
- name: myapp
  newName: myregistry.io/myapp
  newTag: v1.2.3

patches:
- path: replicas.yaml
- path: resources.yaml

configMapGenerator:
- name: webapp-config
  behavior: merge
  literals:
  - LOG_LEVEL=warn
  - ENVIRONMENT=production
```

**apps/overlays/production/webapp/replicas.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 5
```

**apps/overlays/production/webapp/hpa.yaml:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: webapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: webapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**apps/overlays/production/webapp/pdb.yaml:**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: webapp
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: webapp
```

**apps/overlays/production/webapp/ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.example.com
    secretName: webapp-tls
  rules:
  - host: app.example.com
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

### Pattern 2: Helm-Based Deployment

**apps/base/api/helmrelease.yaml:**
```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta2
kind: HelmRelease
metadata:
  name: api
  namespace: flux-system
spec:
  interval: 10m
  chart:
    spec:
      chart: ./charts/api
      sourceRef:
        kind: GitRepository
        name: apps
        namespace: flux-system
  releaseName: api
  targetNamespace: production
  install:
    createNamespace: true
    remediation:
      retries: 3
  upgrade:
    remediation:
      retries: 3
  values:
    replicaCount: 3
    image:
      repository: myregistry.io/api
      tag: v2.1.0
    service:
      type: ClusterIP
      port: 80
    ingress:
      enabled: true
      className: nginx
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt-prod
      hosts:
      - host: api.example.com
        paths:
        - path: /
          pathType: Prefix
      tls:
      - secretName: api-tls
        hosts:
        - api.example.com
    resources:
      limits:
        cpu: 1000m
        memory: 1Gi
      requests:
        cpu: 250m
        memory: 256Mi
    autoscaling:
      enabled: true
      minReplicas: 3
      maxReplicas: 10
      targetCPUUtilizationPercentage: 70
```

## Secret Management

### Option 1: Sealed Secrets

#### Install Sealed Secrets Controller

**infrastructure/base/sealed-secrets/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: kube-system
resources:
- https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

#### Create and Seal Secret

```bash
# Install kubeseal CLI
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-linux-amd64 -O kubeseal
chmod +x kubeseal
sudo mv kubeseal /usr/local/bin/

# Create secret
kubectl create secret generic db-credentials \
  --from-literal=username=myuser \
  --from-literal=password=mypassword \
  --dry-run=client -o yaml > secret.yaml

# Seal the secret
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# Commit sealed secret to Git
git add sealed-secret.yaml
git commit -m "Add sealed database credentials"
```

**apps/base/api/sealed-secret.yaml:**
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  encryptedData:
    username: AgBj8P7QK4...
    password: AgCm9L3NK1...
  template:
    metadata:
      name: db-credentials
      namespace: production
    type: Opaque
```

### Option 2: SOPS with Age

#### Install SOPS

```bash
# Install SOPS
wget https://github.com/mozilla/sops/releases/download/v3.8.1/sops-v3.8.1.linux.amd64 -O sops
chmod +x sops
sudo mv sops /usr/local/bin/

# Install age
wget https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz
tar xzf age-v1.1.1-linux-amd64.tar.gz
sudo mv age/age /usr/local/bin/
sudo mv age/age-keygen /usr/local/bin/
```

#### Generate Age Key

```bash
# Generate key
age-keygen -o age.agekey

# Public key: age1...
# Store private key securely
```

#### Encrypt Secret

**apps/base/api/secret.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: production
stringData:
  database_url: postgresql://user:pass@db:5432/mydb
  api_key: super-secret-api-key
```

```bash
# Encrypt with SOPS
sops --age age1... --encrypt secret.yaml > secret.enc.yaml

# Commit encrypted file
git add secret.enc.yaml
```

#### Configure Flux to Decrypt

**clusters/production/flux-system/kustomization.yaml:**
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  path: ./apps/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```

Create age key secret:
```bash
kubectl create secret generic sops-age \
  --namespace=flux-system \
  --from-file=age.agekey=./age.agekey
```

### Option 3: External Secrets Operator

#### Install External Secrets Operator

**infrastructure/base/external-secrets/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- https://raw.githubusercontent.com/external-secrets/external-secrets/main/deploy/crds/bundle.yaml
- https://raw.githubusercontent.com/external-secrets/external-secrets/main/deploy/external-secrets.yaml
```

#### Configure SecretStore

**infrastructure/overlays/production/external-secrets/secret-store.yaml:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-secrets-sa
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/external-secrets-role
```

#### Create ExternalSecret

**apps/overlays/production/api/external-secret.yaml:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: api-secrets
    creationPolicy: Owner
  data:
  - secretKey: database_url
    remoteRef:
      key: prod/api/database_url
  - secretKey: api_key
    remoteRef:
      key: prod/api/api_key
```

## Configuration Management

### ConfigMaps with Kustomize

**apps/base/webapp/configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  app.conf: |
    server {
      listen 8080;
      location / {
        proxy_pass http://backend;
      }
    }
  features.json: |
    {
      "feature_flags": {
        "new_ui": false,
        "beta_feature": false
      }
    }
```

**apps/overlays/production/webapp/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../../base/webapp

configMapGenerator:
- name: webapp-config
  behavior: merge
  literals:
  - LOG_LEVEL=warn
  - ENVIRONMENT=production
  - CACHE_TTL=3600
  files:
  - features.production.json
```

### Environment-Specific Configuration

Use Kustomize variable substitution:

**apps/base/webapp/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  template:
    spec:
      containers:
      - name: webapp
        env:
        - name: ENVIRONMENT
          value: $(ENVIRONMENT)
        - name: API_ENDPOINT
          value: $(API_ENDPOINT)
```

**apps/overlays/production/webapp/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- ../../../base/webapp

replacements:
- source:
    kind: ConfigMap
    name: cluster-config
    fieldPath: data.environment
  targets:
  - select:
      kind: Deployment
    fieldPaths:
    - spec.template.spec.containers.[name=webapp].env.[name=ENVIRONMENT].value
```

## Progressive Delivery

### Canary Deployments with Flagger

#### Install Flagger

**infrastructure/base/flagger/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: flagger-system
resources:
- namespace.yaml
- https://raw.githubusercontent.com/fluxcd/flagger/main/artifacts/flagger/deployment.yaml
```

#### Create Canary Resource

**apps/overlays/production/webapp/canary.yaml:**
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: webapp
  namespace: production
spec:
  provider: nginx
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: webapp
  progressDeadlineSeconds: 600
  service:
    port: 80
    targetPort: 8080
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
      url: http://loadtester.test/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://webapp-canary.production/"
```

## Cluster Bootstrapping

### Flux Bootstrap Process

#### 1. Bootstrap Flux

```bash
flux bootstrap github \
  --owner=myorg \
  --repository=k8s-gitops \
  --branch=main \
  --path=clusters/production \
  --personal \
  --components-extra=image-reflector-controller,image-automation-controller
```

#### 2. Infrastructure Kustomization

**clusters/production/infrastructure.yaml:**
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
```

#### 3. Apps Kustomization

**clusters/production/apps.yaml:**
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: flux-system
  path: ./apps/overlays/production
  prune: true
  dependsOn:
  - name: infrastructure
```

## Monitoring and Observability

### GitOps Metrics

**infrastructure/base/monitoring/gitops-dashboard.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gitops-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  gitops.json: |
    {
      "dashboard": {
        "title": "GitOps Dashboard",
        "panels": [
          {
            "title": "Kustomization Sync Status",
            "targets": [{
              "expr": "gotk_reconcile_condition{type=\"Ready\"}"
            }]
          },
          {
            "title": "Reconciliation Duration",
            "targets": [{
              "expr": "gotk_reconcile_duration_seconds_bucket"
            }]
          }
        ]
      }
    }
```

### Alerting Rules

**infrastructure/base/monitoring/gitops-alerts.yaml:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: gitops-alerts
  namespace: monitoring
spec:
  groups:
  - name: gitops
    interval: 30s
    rules:
    - alert: KustomizationFailing
      expr: gotk_reconcile_condition{type="Ready",status="False"} == 1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Kustomization {{ $labels.name }} failing"
        description: "Kustomization {{ $labels.name }} in namespace {{ $labels.namespace }} has been failing for 5 minutes"

    - alert: HelmReleaseFailing
      expr: gotk_reconcile_condition{kind="HelmRelease",type="Ready",status="False"} == 1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "HelmRelease {{ $labels.name }} failing"
        description: "HelmRelease {{ $labels.name }} has been failing for 5 minutes"
```

## Best Practices

### 1. Repository Organization
- Separate infrastructure from applications
- Use consistent directory structure
- Keep environments clearly separated
- Document repository layout

### 2. Change Management
- All changes via pull requests
- Require code review for production
- Run automated validation tests
- Use branch protection rules

### 3. Security
- Encrypt all secrets before committing
- Use RBAC for repository access
- Implement least-privilege principles
- Regular security audits

### 4. Testing
- Validate manifests in CI
- Test in lower environments first
- Use preview environments for PRs
- Automated smoke tests after deployment

### 5. Observability
- Monitor sync status
- Alert on failures
- Track deployment metrics
- Maintain audit logs

## Troubleshooting Guide

### Kustomization Not Syncing

```bash
# Check Kustomization status
flux get kustomizations

# View events
kubectl describe kustomization -n flux-system myapp

# Check controller logs
flux logs --kind=kustomization-controller
```

### HelmRelease Failures

```bash
# Check HelmRelease status
flux get helmreleases

# View release history
helm history myapp -n production

# Check helm controller logs
flux logs --kind=helm-controller
```

### Source Sync Issues

```bash
# Check GitRepository status
flux get sources git

# Force reconciliation
flux reconcile source git flux-system --with-source

# Check source controller logs
flux logs --kind=source-controller
```

## Additional Resources

- [Flux Documentation](https://fluxcd.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitOps Principles](https://opengitops.dev/)
