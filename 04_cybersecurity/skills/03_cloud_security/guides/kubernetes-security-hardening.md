# Kubernetes Security Hardening Guide

## Pod Security Standards

```yaml
# Restricted Pod Security Standard
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: myapp:1.0
    
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
          - ALL
        add:
          - NET_BIND_SERVICE
    
    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
      requests:
        memory: "128Mi"
        cpu: "250m"
    
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

## RBAC Configuration

```yaml
# Least privilege ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production

---
# Role with minimal permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["app-secret"]
  verbs: ["get"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind:RoleBinding
metadata:
  name: app-rolebinding
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: app-role
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
```

## Network Policies

```yaml
# Default deny all ingress/egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# Allow specific ingress
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
# Allow specific egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

## Secrets Management

```yaml
# Encrypted Secret
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
  namespace: production
type: Opaque
data:
  api-key: <base64-encoded-value>
immutable: true

---
# Use External Secrets Operator
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
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-external-secret
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: app-secret
  data:
  - secretKey: api-key
    remoteRef:
      key: prod/app/api-key
```

## Image Security

```yaml
# Pod with signed images and scanning
apiVersion: v1
kind: Pod
metadata:
  name: signed-pod
spec:
  containers:
  - name: app
    image: myregistry.io/myapp@sha256:abc123...
    imagePullPolicy: Always
  
  imagePullSecrets:
  - name: regcred

---
# Image Policy (using Kyverno)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-image-signature
spec:
  validationFailureAction: enforce
  rules:
  - name: verify-signature
    match:
      resources:
        kinds:
        - Pod
    verifyImages:
    - imageReferences:
      - "myregistry.io/*"
      attestors:
      - entries:
        - keys:
            publicKeys: |-
              -----BEGIN PUBLIC KEY-----
              ...
              -----END PUBLIC KEY-----

---
# Deny unsigned images
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: enforce
  rules:
  - name: require-image-tag
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Using 'latest' tag is not allowed"
      pattern:
        spec:
          containers:
          - image: "!*:latest"
```

## Admission Controllers

```yaml
# OPA Gatekeeper ConstraintTemplate
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8sblockdefault
spec:
  crd:
    spec:
      names:
        kind: K8sBlockDefault
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sblockdefault
        
        violation[{"msg": msg}] {
          input.review.object.kind == "Pod"
          not input.review.object.spec.securityContext.runAsNonRoot
          msg := "Pods must run as non-root"
        }

---
# Constraint
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sBlockDefault
metadata:
  name: block-default-user
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

## Runtime Security (Falco)

```yaml
# Falco rules
- rule: Detect shell in container
  desc: Detect shell spawned in container
  condition: >
    spawned_process and
    container and
    shell_procs and
    proc.pname exists
  output: >
    Shell spawned in container
    (user=%user.name container_id=%container.id
    container_name=%container.name shell=%proc.name)
  priority: WARNING

- rule: Detect sensitive file access
  desc: Detect access to sensitive files
  condition: >
    open_read and
    container and
    (fd.name startswith /etc/shadow or
     fd.name startswith /etc/passwd)
  output: >
    Sensitive file access
    (user=%user.name file=%fd.name
    container=%container.name)
  priority: CRITICAL
```

## Security Checklist

- [ ] RBAC enabled and configured
- [ ] Pod Security Standards enforced
- [ ] Network policies implemented
- [ ] Secrets encrypted at rest (encryption provider)
- [ ] Audit logging enabled
- [ ] API server authentication/authorization
- [ ] kubelet authentication enabled
- [ ] etcd encrypted and access-controlled
- [ ] Image scanning in CI/CD
- [ ] Runtime security (Falco/Sysdig)
- [ ] Admission controllers configured
- [ ] Resource quotas and limits
- [ ] No privileged containers
- [ ] Service mesh for mTLS (optional)
