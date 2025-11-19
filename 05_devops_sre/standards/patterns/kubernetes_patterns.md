# Kubernetes Deployment Patterns

## Table of Contents
- [Deployment Patterns](#deployment-patterns)
- [StatefulSet Patterns](#statefulset-patterns)
- [Scaling Patterns](#scaling-patterns)
- [Security Patterns](#security-patterns)
- [High Availability Patterns](#high-availability-patterns)
- [Configuration Management Patterns](#configuration-management-patterns)

---

## Deployment Patterns

### 1. Rolling Update Pattern

**Use Case**: Zero-downtime deployments for stateless applications

**Pattern**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Maximum additional pods during update
      maxUnavailable: 1  # Maximum pods unavailable during update
  template:
    spec:
      containers:
      - name: app
        image: app:v2
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Best Practices**:
- Always define `readinessProbe` to ensure traffic only routes to ready pods
- Set `maxUnavailable` to maintain minimum capacity (25% is common)
- Use `maxSurge` to control resource consumption during updates
- Monitor rollout: `kubectl rollout status deployment/app-deployment`

---

### 2. Blue-Green Deployment Pattern

**Use Case**: Instant rollback capability, testing in production

**Pattern**:
```yaml
# Blue Deployment (Current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
  labels:
    app: myapp
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: app:v1.0

---
# Green Deployment (New)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
  labels:
    app: myapp
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: app:v2.0

---
# Service (Switch by changing selector)
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue  # Change to 'green' to switch traffic
  ports:
  - port: 80
    targetPort: 8080
```

**Workflow**:
1. Deploy green environment alongside blue
2. Test green environment thoroughly
3. Switch service selector from `blue` to `green`
4. Monitor for issues
5. Keep blue running for quick rollback
6. Delete blue after successful validation

---

### 3. Canary Deployment Pattern

**Use Case**: Gradual rollout with risk mitigation

**Pattern**:
```yaml
# Stable Deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
  labels:
    app: myapp
    track: stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
    spec:
      containers:
      - name: app
        image: app:v1.0

---
# Canary Deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
  labels:
    app: myapp
    track: canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
    spec:
      containers:
      - name: app
        image: app:v2.0

---
# Service (Routes to both)
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp  # Matches both stable and canary
  ports:
  - port: 80
    targetPort: 8080
```

**Progressive Rollout**:
1. Deploy canary with 10% capacity (1 replica vs 9 stable)
2. Monitor metrics, errors, latency
3. Gradually increase canary replicas: 2, 3, 5, 7, 10
4. Decrease stable replicas proportionally
5. Once canary is 100%, delete stable deployment

---

### 4. A/B Testing Pattern

**Use Case**: Feature testing with specific user segments

**Pattern**:
```yaml
# Version A Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-version-a
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: a
  template:
    metadata:
      labels:
        app: myapp
        version: a
    spec:
      containers:
      - name: app
        image: app:v1-feature-a

---
# Version B Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-version-b
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: b
  template:
    metadata:
      labels:
        app: myapp
        version: b
    spec:
      containers:
      - name: app
        image: app:v1-feature-b

---
# Istio VirtualService for traffic splitting
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: app-ab-test
spec:
  hosts:
  - app-service
  http:
  - match:
    - headers:
        user-type:
          exact: "premium"
    route:
    - destination:
        host: app-service
        subset: version-b
  - route:
    - destination:
        host: app-service
        subset: version-a
```

**Implementation Notes**:
- Requires service mesh (Istio, Linkerd) or ingress controller with advanced routing
- Route based on headers, cookies, or user attributes
- Collect metrics for both versions
- Analyze results before full rollout

---

## StatefulSet Patterns

### 1. Master-Slave Database Pattern

**Use Case**: Databases requiring persistent identity and ordered deployment

**Pattern**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  ports:
  - port: 3306
    name: mysql
  clusterIP: None  # Headless service
  selector:
    app: mysql

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      initContainers:
      - name: init-mysql
        image: mysql:8.0
        command:
        - bash
        - "-c"
        - |
          set -ex
          # Generate server-id from pod ordinal
          [[ $(hostname) =~ -([0-9]+)$ ]] || exit 1
          ordinal=${BASH_REMATCH[1]}
          echo [mysqld] > /mnt/conf.d/server-id.cnf
          echo server-id=$((100 + $ordinal)) >> /mnt/conf.d/server-id.cnf
          # Copy appropriate conf.d files from config-map to emptyDir
          if [[ $ordinal -eq 0 ]]; then
            cp /mnt/config-map/master.cnf /mnt/conf.d/
          else
            cp /mnt/config-map/slave.cnf /mnt/conf.d/
          fi
        volumeMounts:
        - name: conf
          mountPath: /mnt/conf.d
        - name: config-map
          mountPath: /mnt/config-map
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: password
        ports:
        - containerPort: 3306
          name: mysql
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
        - name: conf
          mountPath: /etc/mysql/conf.d
        livenessProbe:
          exec:
            command: ["mysqladmin", "ping"]
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - bash
            - "-c"
            - "mysql -h 127.0.0.1 -e 'SELECT 1'"
          initialDelaySeconds: 5
          periodSeconds: 2
      volumes:
      - name: conf
        emptyDir: {}
      - name: config-map
        configMap:
          name: mysql-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
```

**Key Features**:
- Stable network identities: `mysql-0`, `mysql-1`, `mysql-2`
- Ordered deployment and scaling
- Persistent storage per pod
- Master pod always `mysql-0`

---

### 2. Distributed Cache Pattern (Redis Cluster)

**Use Case**: Stateful distributed caching with sharding

**Pattern**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-cluster
spec:
  clusterIP: None
  ports:
  - port: 6379
    targetPort: 6379
    name: client
  - port: 16379
    targetPort: 16379
    name: gossip
  selector:
    app: redis-cluster

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - "/conf/redis.conf"
        - "--protected-mode"
        - "no"
        - "--cluster-enabled"
        - "yes"
        - "--cluster-config-file"
        - "/data/nodes.conf"
        - "--cluster-node-timeout"
        - "5000"
        - "--appendonly"
        - "yes"
        ports:
        - containerPort: 6379
          name: client
        - containerPort: 16379
          name: gossip
        volumeMounts:
        - name: conf
          mountPath: /conf
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: conf
        configMap:
          name: redis-cluster-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 10Gi
```

---

## Scaling Patterns

### 1. Horizontal Pod Autoscaler (HPA) Pattern

**Use Case**: Automatic scaling based on CPU, memory, or custom metrics

**Pattern**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Scale down max 50% of current pods
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Can double pods
        periodSeconds: 15
      - type: Pods
        value: 4  # Max 4 pods at a time
        periodSeconds: 15
      selectPolicy: Max
```

**Best Practices**:
- Set appropriate `minReplicas` for baseline capacity
- Use `stabilizationWindowSeconds` to prevent flapping
- Combine multiple metrics for intelligent scaling
- Test scaling behavior under load
- Monitor HPA status: `kubectl get hpa -w`

---

### 2. Vertical Pod Autoscaler (VPA) Pattern

**Use Case**: Right-sizing pod resource requests/limits

**Pattern**:
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  updatePolicy:
    updateMode: "Auto"  # or "Recreate", "Initial", "Off"
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
      mode: Auto
```

**Modes**:
- `Auto`: VPA updates pods automatically
- `Recreate`: VPA recreates pods when updating
- `Initial`: VPA only sets resources on pod creation
- `Off`: VPA only provides recommendations

---

### 3. Cluster Autoscaler Pattern

**Use Case**: Automatic node scaling based on pending pods

**Configuration** (Cloud-specific):
```yaml
# For AWS EKS
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.0
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
        - --balance-similar-node-groups
        - --skip-nodes-with-system-pods=false
        env:
        - name: AWS_REGION
          value: us-west-2
```

**Best Practices**:
- Set appropriate Pod Disruption Budgets (PDB)
- Use node affinity for stateful workloads
- Configure pod resource requests properly
- Monitor scale-up/down events

---

## Security Patterns

### 1. Network Policy Pattern

**Use Case**: Microsegmentation and network isolation

**Pattern**:
```yaml
# Default Deny All Ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress

---
# Allow Frontend to Backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

---
# Allow Backend to Database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-database
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 5432

---
# Allow Egress to DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-access
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

---

### 2. Pod Security Standards Pattern

**Use Case**: Enforce security constraints on pods

**Pattern**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-apps
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted

---
# Secure Pod Configuration
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: restricted-apps
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: app:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/cache
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

---

### 3. RBAC Pattern

**Use Case**: Fine-grained access control

**Pattern**:
```yaml
# Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: production

---
# Role (Namespace-scoped)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

---
# ClusterRole (Cluster-wide)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list"]
- apiGroups: ["metrics.k8s.io"]
  resources: ["nodes"]
  verbs: ["get", "list"]

---
# ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-nodes-global
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: production
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

---

### 4. Secrets Management Pattern

**Use Case**: Secure secret storage and injection

**Pattern**:
```yaml
# External Secrets Operator Pattern
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: app-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-password
    remoteRef:
      key: prod/database/password
  - secretKey: api-key
    remoteRef:
      key: prod/external-api/key

---
# Pod using the secret
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: app:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-password
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: api-key
```

---

## High Availability Patterns

### 1. Pod Disruption Budget Pattern

**Use Case**: Maintain availability during voluntary disruptions

**Pattern**:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2  # or use maxUnavailable: 1
  selector:
    matchLabels:
      app: critical-service
```

---

### 2. Multi-Zone Deployment Pattern

**Use Case**: Availability zone distribution

**Pattern**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-zone-app
spec:
  replicas: 6
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - multi-zone-app
            topologyKey: topology.kubernetes.io/zone
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: multi-zone-app
      containers:
      - name: app
        image: app:latest
```

---

## Configuration Management Patterns

### 1. ConfigMap Immutability Pattern

**Use Case**: Prevent configuration drift, enable safe rollbacks

**Pattern**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-v1
immutable: true
data:
  app.properties: |
    server.port=8080
    feature.new=true
    cache.ttl=3600

---
# New version for changes
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-v2
immutable: true
data:
  app.properties: |
    server.port=8080
    feature.new=true
    cache.ttl=7200  # Changed value
```

---

### 2. Environment-Specific Configuration Pattern

**Use Case**: Manage configs across environments using Kustomize

**Directory Structure**:
```
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── config.yaml
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── config.yaml
│   └── prod/
│       ├── kustomization.yaml
│       ├── config.yaml
│       └── replicas.yaml
```

**Base kustomization.yaml**:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
```

**Production overlay**:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
- ../../base
replicas:
- name: app
  count: 10
configMapGenerator:
- name: app-config
  literals:
  - ENVIRONMENT=production
  - LOG_LEVEL=warn
  - CACHE_ENABLED=true
```

---

## Summary

These patterns represent production-proven approaches for deploying and managing applications in Kubernetes. Key principles:

1. **Deployment**: Use appropriate strategy (rolling, blue-green, canary) based on risk tolerance
2. **StatefulSets**: For stateful apps requiring stable identity and persistent storage
3. **Scaling**: Combine HPA, VPA, and Cluster Autoscaler for complete autoscaling
4. **Security**: Layer defense with NetworkPolicies, RBAC, Pod Security, and secrets management
5. **High Availability**: Use PDBs, multi-zone distribution, and proper resource requests
6. **Configuration**: Embrace immutability and environment-specific overlays

Always test patterns in non-production environments first and monitor metrics to validate effectiveness.
