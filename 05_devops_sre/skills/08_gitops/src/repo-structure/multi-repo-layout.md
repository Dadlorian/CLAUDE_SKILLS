# GitOps Multi-Repository Layout

This example demonstrates a multi-repository structure where each environment, team, or concern has its own repository.

## Repository Overview

### 1. Fleet Infrastructure Repository
Central repository managing cluster bootstrapping and cross-cutting concerns.

```
fleet-infra/
├── README.md
├── clusters/
│   ├── production/
│   │   ├── us-east-1/
│   │   │   ├── flux-system/
│   │   │   ├── infrastructure.yaml
│   │   │   ├── teams.yaml
│   │   │   └── config.yaml
│   │   ├── us-west-2/
│   │   │   ├── flux-system/
│   │   │   ├── infrastructure.yaml
│   │   │   ├── teams.yaml
│   │   │   └── config.yaml
│   │   └── eu-west-1/
│   │       ├── flux-system/
│   │       ├── infrastructure.yaml
│   │       ├── teams.yaml
│   │       └── config.yaml
│   ├── staging/
│   │   └── us-east-1/
│   └── development/
│       └── us-east-1/
├── infrastructure/
│   ├── sources/
│   │   ├── infrastructure-repo.yaml
│   │   ├── team-alpha-repo.yaml
│   │   ├── team-beta-repo.yaml
│   │   └── helm-repositories.yaml
│   └── configs/
│       ├── cluster-config.yaml
│       └── rbac-config.yaml
└── teams/
    ├── team-alpha.yaml
    ├── team-beta.yaml
    └── team-gamma.yaml
```

### 2. Infrastructure Repository
Platform infrastructure and shared services.

```
infrastructure/
├── README.md
├── base/
│   ├── namespaces/
│   │   ├── cert-manager.yaml
│   │   ├── ingress-nginx.yaml
│   │   ├── monitoring.yaml
│   │   ├── logging.yaml
│   │   └── kustomization.yaml
│   ├── cert-manager/
│   │   ├── namespace.yaml
│   │   ├── release.yaml
│   │   ├── cluster-issuer-staging.yaml
│   │   ├── cluster-issuer-prod.yaml
│   │   └── kustomization.yaml
│   ├── ingress-nginx/
│   │   ├── namespace.yaml
│   │   ├── release.yaml
│   │   ├── values.yaml
│   │   └── kustomization.yaml
│   ├── sealed-secrets/
│   │   ├── release.yaml
│   │   └── kustomization.yaml
│   ├── external-dns/
│   │   ├── deployment.yaml
│   │   ├── rbac.yaml
│   │   └── kustomization.yaml
│   ├── monitoring/
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   ├── alertmanager/
│   │   └── kustomization.yaml
│   └── logging/
│       ├── loki/
│       ├── promtail/
│       └── kustomization.yaml
├── overlays/
│   ├── production/
│   │   ├── cert-manager/
│   │   ├── ingress-nginx/
│   │   ├── monitoring/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── development/
│       └── kustomization.yaml
├── regions/
│   ├── us-east-1/
│   │   ├── ingress-annotations.yaml
│   │   └── kustomization.yaml
│   ├── us-west-2/
│   │   └── kustomization.yaml
│   └── eu-west-1/
│       └── kustomization.yaml
└── policies/
    ├── network-policies/
    ├── pod-security-policies/
    └── resource-quotas/
```

### 3. Team Application Repositories
Each team manages their own applications.

```
team-alpha-apps/
├── README.md
├── .github/
│   └── workflows/
│       ├── validate.yaml
│       └── image-update.yaml
├── apps/
│   ├── app1/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── production/
│   │       │   ├── deployment-patch.yaml
│   │       │   ├── ingress.yaml
│   │       │   ├── hpa.yaml
│   │       │   └── kustomization.yaml
│   │       ├── staging/
│   │       │   └── kustomization.yaml
│   │       └── development/
│   │           └── kustomization.yaml
│   ├── app2/
│   │   ├── base/
│   │   └── overlays/
│   └── shared/
│       ├── namespace.yaml
│       └── rbac.yaml
├── charts/
│   ├── app1/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-production.yaml
│   │   └── templates/
│   └── app2/
└── environments/
    ├── production/
    │   ├── kustomization.yaml
    │   └── image-policies.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── development/
        └── kustomization.yaml
```

## Key Configuration Files

### fleet-infra/clusters/production/us-east-1/infrastructure.yaml
```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 10m
  url: https://github.com/myorg/infrastructure
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: infrastructure
  path: ./overlays/production
  prune: true
  wait: true
  timeout: 10m
  postBuild:
    substitute:
      cluster_name: prod-us-east-1
      region: us-east-1
```

### fleet-infra/clusters/production/us-east-1/teams.yaml
```yaml
---
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: team-alpha
  namespace: flux-system
spec:
  interval: 5m
  url: https://github.com/team-alpha/apps
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: team-alpha
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: team-alpha
  path: ./environments/production
  prune: true
  targetNamespace: team-alpha
  serviceAccountName: team-alpha
  dependsOn:
  - name: infrastructure
---
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: team-alpha
  namespace: flux-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: team-alpha
  namespace: team-alpha
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- kind: ServiceAccount
  name: team-alpha
  namespace: flux-system
```

### team-alpha-apps/environments/production/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: team-alpha
resources:
- ../../apps/app1/overlays/production
- ../../apps/app2/overlays/production
- ../../apps/shared
```

## Repository Permissions

### fleet-infra
- **Read**: All engineers
- **Write**: Platform team only
- **Admin**: Platform leads

### infrastructure
- **Read**: All engineers
- **Write**: Platform team, SRE team
- **Admin**: Platform leads

### team-alpha-apps
- **Read**: All engineers
- **Write**: Team Alpha members
- **Admin**: Team Alpha leads

## Advantages

1. **Strong Isolation**: Each repository can have different access controls
2. **Team Autonomy**: Teams control their own repositories
3. **Independent Velocity**: Teams can work at their own pace
4. **Clear Ownership**: Repository = ownership boundary
5. **Smaller Repos**: Faster clone and operations

## Disadvantages

1. **More Complex**: Multiple repositories to manage
2. **Cross-Repo Changes**: Harder to make atomic changes
3. **Coordination**: Requires more coordination between teams
4. **More Bootstrapping**: Each repo needs to be configured

## Workflow

### Platform Team Workflow
1. Make infrastructure changes in `infrastructure` repo
2. Update `fleet-infra` if needed (e.g., new team)
3. Changes automatically deployed to all clusters

### Application Team Workflow
1. Make changes in team repository
2. Changes automatically deployed to dev/staging
3. Create PR for production changes
4. After approval, changes deployed to production

## Bootstrapping

```bash
# Bootstrap fleet-infra
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production/us-east-1

# The fleet-infra repository will then:
# 1. Deploy infrastructure from infrastructure repo
# 2. Configure team repositories
# 3. Teams' apps are automatically deployed
```

## Repository Relationship

```
┌─────────────────────────────────────────────────────────────┐
│                        fleet-infra                          │
│  - Cluster bootstrapping                                    │
│  - Team configurations                                      │
│  - Cross-cutting concerns                                   │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
    ┌────────────────┐              ┌────────────────┐
    │ infrastructure │              │  team repos    │
    │  - Ingress     │              │  - Apps        │
    │  - Cert Mgr    │              │  - Services    │
    │  - Monitoring  │              │  - Configs     │
    └────────────────┘              └────────────────┘
```

## Migration Path

### From Monorepo to Multi-Repo

1. Create new infrastructure repository
2. Move infrastructure files
3. Update fleet-infra to reference new repo
4. Test in development
5. Gradually move teams to separate repos
6. Retire monorepo

### From Multi-Repo to Monorepo

1. Create new monorepo
2. Copy files from all repos maintaining structure
3. Update cluster configurations
4. Test in development
5. Switch production
6. Archive old repos

## Recommended Team Size

- **Medium to Large** (5+ teams, 50+ applications)
- Multiple autonomous teams
- Clear team boundaries
- Need for different security/compliance per team
- Platform team exists to manage infrastructure

## Best Practices

1. **Naming Convention**: Use consistent repository naming
   - `team-{team-name}-apps`
   - `platform-{component}`

2. **Documentation**: Each repo should have comprehensive README

3. **Templates**: Provide repository templates for teams

4. **CI/CD**: Standardized CI/CD across repos
   ```yaml
   # .github/workflows/validate.yaml
   name: Validate
   on: [pull_request]
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       - name: Validate manifests
         run: |
           kubectl apply --dry-run=server -f .
   ```

5. **CODEOWNERS**: Use CODEOWNERS for required reviews
   ```
   # team-alpha-apps/.github/CODEOWNERS
   * @team-alpha/developers
   /environments/production/ @team-alpha/leads
   ```

6. **Branch Protection**: Protect main/production branches

7. **Shared Libraries**: Consider a shared repository for common configs
   ```
   shared-configs/
   ├── bases/
   │   ├── deployment/
   │   ├── service/
   │   └── ingress/
   └── policies/
   ```

8. **Regular Syncs**: Regular sync meetings between teams
