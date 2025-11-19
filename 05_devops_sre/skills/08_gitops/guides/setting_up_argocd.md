# Complete ArgoCD Setup Guide

## Introduction

This guide walks through setting up ArgoCD in a production Kubernetes cluster, from installation to deploying your first application.

## Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured to access your cluster
- Basic understanding of Kubernetes
- Git repository for your application manifests
- (Optional) Domain name for ArgoCD UI

## Installation Options

### Option 1: Standard Installation (Recommended for Getting Started)

This installs ArgoCD with default settings suitable for development and small deployments.

#### Step 1: Create Namespace

```bash
kubectl create namespace argocd
```

#### Step 2: Install ArgoCD

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Step 3: Verify Installation

```bash
# Check all pods are running
kubectl get pods -n argocd

# Expected output (all pods should be Running):
# NAME                                  READY   STATUS    RESTARTS   AGE
# argocd-application-controller-0       1/1     Running   0          2m
# argocd-dex-server-xxx                 1/1     Running   0          2m
# argocd-redis-xxx                      1/1     Running   0          2m
# argocd-repo-server-xxx                1/1     Running   0          2m
# argocd-server-xxx                     1/1     Running   0          2m
```

### Option 2: High Availability Installation (Production)

For production environments requiring high availability.

#### Install ArgoCD HA

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/ha/install.yaml
```

This installs:
- 3 application-controller replicas
- 3 repo-server replicas
- Redis HA with sentinel
- 2 server replicas

### Option 3: Helm Installation

For customized deployments using Helm.

#### Add Helm Repository

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

#### Create Values File

```yaml
# argocd-values.yaml
global:
  image:
    tag: v2.9.3

server:
  replicas: 2
  service:
    type: LoadBalancer
  ingress:
    enabled: true
    hosts:
      - argocd.example.com
    tls:
      - secretName: argocd-server-tls
        hosts:
          - argocd.example.com
  config:
    url: https://argocd.example.com
    dex.config: |
      connectors:
        - type: github
          id: github
          name: GitHub
          config:
            clientID: $dex.github.clientId
            clientSecret: $dex.github.clientSecret
            orgs:
            - name: your-org

repoServer:
  replicas: 2

controller:
  replicas: 1

redis-ha:
  enabled: true

configs:
  secret:
    createSecret: true
    githubSecret: ""
    gitlabSecret: ""
```

#### Install with Helm

```bash
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --values argocd-values.yaml
```

## Accessing ArgoCD

### Method 1: Port Forward (Development)

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Access at: https://localhost:8080

### Method 2: LoadBalancer Service

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

# Get LoadBalancer IP
kubectl get svc argocd-server -n argocd
```

### Method 3: Ingress (Production)

#### Install Ingress Controller (if needed)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

#### Install Cert-Manager (for TLS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

#### Create ClusterIssuer

```yaml
# letsencrypt-prod.yaml
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

```bash
kubectl apply -f letsencrypt-prod.yaml
```

#### Create Ingress for ArgoCD

```yaml
# argocd-ingress.yaml
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

```bash
kubectl apply -f argocd-ingress.yaml
```

## Initial Login

### Get Initial Password

```bash
# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Login via UI

1. Navigate to https://argocd.example.com (or localhost:8080)
2. Username: `admin`
3. Password: (from previous command)

### Login via CLI

#### Install ArgoCD CLI

```bash
# Linux
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd

# macOS
brew install argocd

# Windows
choco install argocd-cli
```

#### Login

```bash
# If using port-forward
argocd login localhost:8080 --insecure

# If using Ingress
argocd login argocd.example.com --grpc-web

# Enter admin credentials when prompted
```

### Change Admin Password

```bash
argocd account update-password
```

Or delete the initial secret after setting a new password:

```bash
kubectl -n argocd delete secret argocd-initial-admin-secret
```

## Configure Git Repository

### Public Repository

```bash
argocd repo add https://github.com/example/myapp.git
```

### Private Repository with SSH

#### Generate SSH Key

```bash
ssh-keygen -t ed25519 -f ~/.ssh/argocd -N ""
```

#### Add Public Key to Git Provider

Add `~/.ssh/argocd.pub` as a deploy key in your Git repository.

#### Add Repository to ArgoCD

```bash
argocd repo add git@github.com:example/myapp.git \
  --ssh-private-key-path ~/.ssh/argocd
```

### Private Repository with HTTPS Token

#### GitHub Personal Access Token

```bash
argocd repo add https://github.com/example/myapp.git \
  --username git \
  --password ghp_yourpersonalaccesstoken
```

#### GitLab Deploy Token

```bash
argocd repo add https://gitlab.com/example/myapp.git \
  --username gitlab-ci-token \
  --password your-deploy-token
```

### Add Repository via Manifest

```yaml
# repository.yaml
apiVersion: v1
kind: Secret
metadata:
  name: private-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: https://github.com/example/myapp.git
  password: my-password
  username: my-username
```

```bash
kubectl apply -f repository.yaml
```

## Create Your First Application

### Example Application Structure

```
myapp/
├── deployment.yaml
├── service.yaml
└── kustomization.yaml
```

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 2
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
        image: nginx:1.25
        ports:
        - containerPort: 80
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

**kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
```

### Deploy Application via CLI

```bash
argocd app create myapp \
  --repo https://github.com/example/myapp.git \
  --path k8s \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace myapp \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

### Deploy Application via Manifest

```yaml
# myapp-application.yaml
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
    path: k8s
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

```bash
kubectl apply -f myapp-application.yaml
```

### Verify Deployment

```bash
# Check application status
argocd app get myapp

# Check application in cluster
kubectl get all -n myapp
```

## Create AppProject for Multi-Tenancy

### Define AppProject

```yaml
# team-alpha-project.yaml
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
    server: https://kubernetes.default.svc

  clusterResourceWhitelist:
  - group: ''
    kind: Namespace

  namespaceResourceWhitelist:
  - group: 'apps'
    kind: '*'
  - group: ''
    kind: '*'
  - group: 'networking.k8s.io'
    kind: '*'

  roles:
  - name: developer
    description: Developer role
    policies:
    - p, proj:team-alpha:developer, applications, get, team-alpha/*, allow
    - p, proj:team-alpha:developer, applications, sync, team-alpha/*, allow
    groups:
    - team-alpha-devs

  - name: admin
    description: Admin role
    policies:
    - p, proj:team-alpha:admin, applications, *, team-alpha/*, allow
    groups:
    - team-alpha-admins
```

```bash
kubectl apply -f team-alpha-project.yaml
```

### Create Application in Project

```bash
argocd app create team-alpha-app \
  --project team-alpha \
  --repo https://github.com/team-alpha/app.git \
  --path k8s \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace team-alpha-prod
```

## Configure SSO Authentication

### GitHub SSO

#### Create GitHub OAuth App

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create new OAuth App:
   - Application name: ArgoCD
   - Homepage URL: https://argocd.example.com
   - Callback URL: https://argocd.example.com/api/dex/callback

#### Configure ArgoCD

```yaml
# argocd-cm-patch.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  url: https://argocd.example.com
  dex.config: |
    connectors:
    - type: github
      id: github
      name: GitHub
      config:
        clientID: your-github-oauth-client-id
        clientSecret: $dex.github.clientSecret
        orgs:
        - name: your-organization
```

#### Store GitHub Client Secret

```bash
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {"dex.github.clientSecret": "your-github-oauth-client-secret"}}'
```

```bash
kubectl apply -f argocd-cm-patch.yaml
```

### Google SSO

```yaml
data:
  dex.config: |
    connectors:
    - type: oidc
      id: google
      name: Google
      config:
        issuer: https://accounts.google.com
        clientID: your-client-id.apps.googleusercontent.com
        clientSecret: $dex.google.clientSecret
        redirectURI: https://argocd.example.com/api/dex/callback
        hostedDomains:
        - example.com
```

## Configure RBAC

### ArgoCD RBAC Policy

```yaml
# argocd-rbac-cm.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly
  policy.csv: |
    # Administrator role
    p, role:admin, applications, *, */*, allow
    p, role:admin, clusters, *, *, allow
    p, role:admin, repositories, *, *, allow
    p, role:admin, projects, *, *, allow

    # Developer role
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, */*, allow
    p, role:developer, applications, override, */*, allow
    p, role:developer, repositories, get, *, allow

    # ReadOnly role
    p, role:readonly, applications, get, */*, allow
    p, role:readonly, repositories, get, *, allow
    p, role:readonly, projects, get, *, allow

    # Group bindings
    g, org-admins, role:admin
    g, org-developers, role:developer
    g, org-viewers, role:readonly
```

```bash
kubectl apply -f argocd-rbac-cm.yaml
```

## Configure Notifications

### Slack Notifications

#### Create Slack Webhook

1. Go to https://api.slack.com/apps
2. Create new app
3. Enable Incoming Webhooks
4. Create webhook URL

#### Configure ArgoCD Notifications

```yaml
# argocd-notifications-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: argocd-notifications-secret
  namespace: argocd
stringData:
  slack-token: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

```bash
kubectl apply -f argocd-notifications-secret.yaml
```

#### Configure Notification Templates

```yaml
# argocd-notifications-cm.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.slack: |
    token: $slack-token

  template.app-deployed: |
    message: |
      Application {{.app.metadata.name}} is now running version {{.app.status.sync.revision}}.
    slack:
      attachments: |
        [{
          "title": "{{ .app.metadata.name}}",
          "title_link": "{{.context.argocdUrl}}/applications/{{.app.metadata.name}}",
          "color": "#18be52",
          "fields": [{
            "title": "Sync Status",
            "value": "{{.app.status.sync.status}}",
            "short": true
          }, {
            "title": "Repository",
            "value": "{{.app.spec.source.repoURL}}",
            "short": true
          }]
        }]

  trigger.on-deployed: |
    - when: app.status.operationState.phase in ['Succeeded']
      oncePer: app.status.sync.revision
      send: [app-deployed]

  subscriptions: |
    - recipients:
      - slack:general
      triggers:
      - on-deployed
```

```bash
kubectl apply -f argocd-notifications-cm.yaml
```

#### Subscribe Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-deployed.slack: general
```

## Monitoring ArgoCD

### Expose Metrics

ArgoCD components expose Prometheus metrics by default.

#### Create ServiceMonitor

```yaml
# argocd-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: argocd-metrics
  namespace: argocd
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: argocd-server
  endpoints:
  - port: metrics
```

```bash
kubectl apply -f argocd-servicemonitor.yaml
```

### Import Grafana Dashboards

Import official ArgoCD Grafana dashboards:
- Dashboard ID: 14584 (ArgoCD Operational Overview)
- Dashboard ID: 19993 (ArgoCD Application Overview)

## Backup and Disaster Recovery

### Backup ArgoCD Configuration

```bash
# Backup all applications
kubectl get applications -n argocd -o yaml > applications-backup.yaml

# Backup all projects
kubectl get appprojects -n argocd -o yaml > projects-backup.yaml

# Backup repositories
kubectl get secrets -n argocd -l argocd.argoproj.io/secret-type=repository -o yaml > repos-backup.yaml

# Backup RBAC config
kubectl get configmap argocd-rbac-cm -n argocd -o yaml > rbac-backup.yaml
```

### Restore ArgoCD Configuration

```bash
kubectl apply -f applications-backup.yaml
kubectl apply -f projects-backup.yaml
kubectl apply -f repos-backup.yaml
kubectl apply -f rbac-backup.yaml
```

### Automated Backup with CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: argocd-backup
  namespace: argocd
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: argocd-backup
          containers:
          - name: backup
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              kubectl get applications -n argocd -o yaml > /backup/applications.yaml
              kubectl get appprojects -n argocd -o yaml > /backup/projects.yaml
              # Upload to S3/GCS
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            emptyDir: {}
          restartPolicy: OnFailure
```

## Troubleshooting

### Application Not Syncing

```bash
# Check application status
argocd app get myapp

# Check sync errors
kubectl describe application myapp -n argocd

# Force refresh
argocd app get myapp --refresh --hard-refresh
```

### Repository Connection Issues

```bash
# Test repository connection
argocd repo list

# View repository details
argocd repo get https://github.com/example/myapp.git
```

### Performance Issues

```bash
# Check resource usage
kubectl top pods -n argocd

# Scale repo server
kubectl scale deployment argocd-repo-server -n argocd --replicas=3

# Scale application controller
kubectl scale statefulset argocd-application-controller -n argocd --replicas=2
```

### View Logs

```bash
# Application controller logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller

# Repo server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-repo-server

# Server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server
```

## Next Steps

1. Set up multiple environments (dev, staging, production)
2. Implement AppProjects for multi-tenancy
3. Configure automated image updates
4. Set up progressive delivery with Argo Rollouts
5. Implement application health checks
6. Configure automated backups
7. Set up monitoring and alerting
8. Document GitOps workflows for your team

## Additional Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [ArgoCD Operator Manual](https://argo-cd.readthedocs.io/en/stable/operator-manual/)
- [ArgoCD Examples](https://github.com/argoproj/argocd-example-apps)
