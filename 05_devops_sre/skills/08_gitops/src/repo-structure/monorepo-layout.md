# GitOps Monorepo Layout

This example demonstrates a monorepo structure where all environments and applications are managed in a single repository.

## Directory Structure

```
gitops-monorepo/
├── README.md
├── .gitignore
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   │   ├── gotk-components.yaml
│   │   │   ├── gotk-sync.yaml
│   │   │   └── kustomization.yaml
│   │   ├── infrastructure.yaml
│   │   ├── apps.yaml
│   │   └── config/
│   │       ├── cluster-config.yaml
│   │       └── cluster-secrets.enc.yaml
│   ├── staging/
│   │   ├── flux-system/
│   │   ├── infrastructure.yaml
│   │   ├── apps.yaml
│   │   └── config/
│   └── development/
│       ├── flux-system/
│       ├── infrastructure.yaml
│       ├── apps.yaml
│       └── config/
├── infrastructure/
│   ├── base/
│   │   ├── cert-manager/
│   │   │   ├── namespace.yaml
│   │   │   ├── release.yaml
│   │   │   ├── cluster-issuer.yaml
│   │   │   └── kustomization.yaml
│   │   ├── ingress-nginx/
│   │   │   ├── namespace.yaml
│   │   │   ├── release.yaml
│   │   │   ├── values.yaml
│   │   │   └── kustomization.yaml
│   │   ├── sealed-secrets/
│   │   │   ├── namespace.yaml
│   │   │   ├── release.yaml
│   │   │   └── kustomization.yaml
│   │   ├── external-dns/
│   │   │   ├── namespace.yaml
│   │   │   ├── deployment.yaml
│   │   │   ├── rbac.yaml
│   │   │   └── kustomization.yaml
│   │   ├── metrics-server/
│   │   │   ├── release.yaml
│   │   │   └── kustomization.yaml
│   │   └── monitoring/
│   │       ├── prometheus/
│   │       │   ├── namespace.yaml
│   │       │   ├── release.yaml
│   │       │   ├── values.yaml
│   │       │   └── kustomization.yaml
│   │       ├── grafana/
│   │       │   ├── release.yaml
│   │       │   ├── values.yaml
│   │       │   ├── dashboards/
│   │       │   └── kustomization.yaml
│   │       └── loki/
│   │           ├── release.yaml
│   │           ├── values.yaml
│   │           └── kustomization.yaml
│   ├── overlays/
│   │   ├── production/
│   │   │   ├── cert-manager/
│   │   │   │   ├── cluster-issuer-prod.yaml
│   │   │   │   └── kustomization.yaml
│   │   │   ├── ingress-nginx/
│   │   │   │   ├── values-prod.yaml
│   │   │   │   └── kustomization.yaml
│   │   │   ├── monitoring/
│   │   │   │   └── prometheus/
│   │   │   │       ├── values-prod.yaml
│   │   │   │       └── kustomization.yaml
│   │   │   └── kustomization.yaml
│   │   ├── staging/
│   │   │   ├── cert-manager/
│   │   │   ├── ingress-nginx/
│   │   │   └── kustomization.yaml
│   │   └── development/
│   │       ├── cert-manager/
│   │       ├── ingress-nginx/
│   │       └── kustomization.yaml
│   └── sources/
│       ├── helm-repositories.yaml
│       └── git-repositories.yaml
├── apps/
│   ├── base/
│   │   ├── webapp/
│   │   │   ├── namespace.yaml
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── sealed-secret.yaml
│   │   │   ├── servicemonitor.yaml
│   │   │   └── kustomization.yaml
│   │   ├── api/
│   │   │   ├── namespace.yaml
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── hpa.yaml
│   │   │   ├── pdb.yaml
│   │   │   └── kustomization.yaml
│   │   ├── worker/
│   │   │   ├── namespace.yaml
│   │   │   ├── deployment.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── kustomization.yaml
│   │   └── database/
│   │       ├── namespace.yaml
│   │       ├── statefulset.yaml
│   │       ├── service.yaml
│   │       ├── pvc.yaml
│   │       └── kustomization.yaml
│   ├── overlays/
│   │   ├── production/
│   │   │   ├── webapp/
│   │   │   │   ├── deployment-patch.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── kustomization.yaml
│   │   │   ├── api/
│   │   │   │   ├── deployment-patch.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   └── kustomization.yaml
│   │   │   ├── worker/
│   │   │   │   ├── deployment-patch.yaml
│   │   │   │   └── kustomization.yaml
│   │   │   └── kustomization.yaml
│   │   ├── staging/
│   │   │   ├── webapp/
│   │   │   ├── api/
│   │   │   ├── worker/
│   │   │   └── kustomization.yaml
│   │   └── development/
│   │       ├── webapp/
│   │       ├── api/
│   │       ├── worker/
│   │       └── kustomization.yaml
│   └── charts/
│       ├── webapp/
│       │   ├── Chart.yaml
│       │   ├── values.yaml
│       │   ├── values-production.yaml
│       │   ├── values-staging.yaml
│       │   └── templates/
│       └── api/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
├── policies/
│   ├── network-policies/
│   │   ├── default-deny-all.yaml
│   │   ├── allow-dns.yaml
│   │   ├── allow-monitoring.yaml
│   │   └── kustomization.yaml
│   ├── pod-security-policies/
│   │   ├── restricted.yaml
│   │   ├── baseline.yaml
│   │   └── kustomization.yaml
│   ├── resource-quotas/
│   │   ├── production-quota.yaml
│   │   ├── staging-quota.yaml
│   │   └── kustomization.yaml
│   └── limit-ranges/
│       ├── production-limits.yaml
│       ├── staging-limits.yaml
│       └── kustomization.yaml
├── scripts/
│   ├── bootstrap.sh
│   ├── encrypt-secret.sh
│   ├── decrypt-secret.sh
│   └── validate-manifests.sh
└── docs/
    ├── architecture.md
    ├── deployment-workflow.md
    ├── troubleshooting.md
    └── runbooks/
        ├── cert-renewal.md
        ├── disaster-recovery.md
        └── scaling.md
```

## Key Files

### clusters/production/infrastructure.yaml
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
    substituteFrom:
    - kind: ConfigMap
      name: cluster-config
```

### clusters/production/apps.yaml
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: apps
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: flux-system
  path: ./apps/overlays/production
  prune: true
  dependsOn:
  - name: infrastructure
```

### clusters/production/config/cluster-config.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-config
  namespace: flux-system
data:
  cluster_name: prod-us-east-1
  environment: production
  region: us-east-1
  domain: example.com
```

## Advantages

1. **Single Source of Truth**: Everything in one place
2. **Easy to Navigate**: Clear directory structure
3. **Atomic Changes**: Changes across environments can be atomic
4. **Simplified RBAC**: Single repository to protect
5. **Easy to See Changes**: All changes visible in one repo

## Disadvantages

1. **Large Repository**: Can become unwieldy
2. **Slower Operations**: Git operations slow with size
3. **All or Nothing Access**: Everyone can see everything
4. **Merge Conflicts**: Higher chance with multiple teams

## Best Practices

1. Use `.gitignore` for local files:
   ```
   # .gitignore
   .DS_Store
   *.swp
   *.tmp
   .idea/
   .vscode/
   secrets-decrypted/
   ```

2. Document structure in README.md
3. Use consistent naming conventions
4. Implement pre-commit hooks for validation
5. Keep encrypted secrets in Git, never plaintext
6. Use sync waves to control deployment order
7. Leverage dependencies between Kustomizations

## Workflow

1. **Development**:
   - Create feature branch
   - Make changes to development overlay
   - Test in dev cluster
   - Open PR

2. **Staging**:
   - After dev approval, update staging overlay
   - Automated deployment to staging
   - Run integration tests

3. **Production**:
   - After staging validation, update production overlay
   - Require approval for production PR
   - Automated deployment after merge

## Bootstrapping

```bash
# Bootstrap production cluster
flux bootstrap github \
  --owner=myorg \
  --repository=gitops-monorepo \
  --branch=main \
  --path=clusters/production \
  --personal

# Bootstrap staging cluster
flux bootstrap github \
  --owner=myorg \
  --repository=gitops-monorepo \
  --branch=main \
  --path=clusters/staging \
  --personal

# Bootstrap development cluster
flux bootstrap github \
  --owner=myorg \
  --repository=gitops-monorepo \
  --branch=main \
  --path=clusters/development \
  --personal
```

## Recommended Team Size

- **Small to Medium** (1-5 teams, <50 applications)
- Centralized ops team managing infrastructure
- Teams have good collaboration practices
