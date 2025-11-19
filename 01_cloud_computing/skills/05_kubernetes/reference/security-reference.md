# Kubernetes Security Reference

## Security Principles

### Defense in Depth
Kubernetes security requires multiple layers of protection:
1. **Cluster Access**: Authentication and authorization
2. **Pod Security**: Pod Security Standards, security contexts
3. **Network Security**: Network policies, service mesh
4. **Runtime Security**: Container runtime, security monitoring
5. **Supply Chain**: Image security, admission control

### Least Privilege
- Minimal permissions for service accounts
- RBAC with specific permissions
- No privileged containers unless absolutely necessary
- Read-only root filesystems where possible

## Authentication

### Authentication Methods

**X509 Client Certificates**:
```bash
# Generate client certificate
openssl genrsa -out user.key 2048
openssl req -new -key user.key -out user.csr -subj "/CN=user/O=group"
# Sign CSR with cluster CA
```

**Static Token File** (deprecated):
```csv
token,user,uid,"group1,group2"
```

**Bootstrap Tokens**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: bootstrap-token-abc123
  namespace: kube-system
type: bootstrap.kubernetes.io/token
stringData:
  token-id: abc123
  token-secret: 0123456789abcdef
  usage-bootstrap-authentication: "true"
```

**Service Account Tokens**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp
  namespace: default
```

**OpenID Connect (OIDC)**:
```yaml
apiVersion: v1
kind: Config
users:
- name: user
  user:
    auth-provider:
      name: oidc
      config:
        client-id: kubernetes
        client-secret: secret
        id-token: eyJhbGc...
        idp-issuer-url: https://accounts.google.com
```

**Webhook Token Authentication**:
- External service validates tokens
- Flexible integration with identity providers

**Authentication Proxy**:
- Reverse proxy handles authentication
- Passes user info in headers

### Service Accounts

**Creating Service Account**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
automountServiceAccountToken: false  # Disable if not needed
```

**Using in Pod**:
```yaml
spec:
  serviceAccountName: myapp-sa
  automountServiceAccountToken: true
```

**Token Projection** (recommended):
```yaml
spec:
  serviceAccountName: myapp-sa
  volumes:
  - name: token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600
          audience: api
```

## Authorization

### RBAC (Role-Based Access Control)

**Role** (namespace-scoped):
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
```

**ClusterRole** (cluster-wide):
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "watch", "list"]
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["specific-secret"]  # Restrict to specific resources
  verbs: ["get"]
```

**RoleBinding**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: myapp-sa
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**ClusterRoleBinding**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-secrets-global
subjects:
- kind: Group
  name: managers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### RBAC Resources

**API Groups**:
- `""` (core): pods, services, configmaps, secrets
- `apps`: deployments, statefulsets, daemonsets
- `batch`: jobs, cronjobs
- `networking.k8s.io`: networkpolicies, ingresses
- `rbac.authorization.k8s.io`: roles, rolebindings

**Verbs**:
- `get`, `list`, `watch`: Read operations
- `create`, `update`, `patch`, `delete`: Write operations
- `deletecollection`: Delete multiple resources
- `*`: All verbs (avoid in production)

**Common Patterns**:
```yaml
# Read-only access to all resources in namespace
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]

# Full access to deployments
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["*"]

# Execute into pods
rules:
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
```

### Pre-defined ClusterRoles
- `cluster-admin`: Full cluster access
- `admin`: Full namespace access
- `edit`: Read/write namespace access
- `view`: Read-only namespace access

### RBAC Best Practices
- Principle of least privilege
- Use RoleBindings instead of ClusterRoleBindings when possible
- Avoid wildcards in production
- Regularly audit RBAC policies
- Use resourceNames to restrict access to specific resources
- Separate service accounts per application

## Pod Security

### Pod Security Standards

**Privileged** (unrestricted):
- No restrictions
- For trusted workloads only

**Baseline** (minimally restrictive):
- Prevents known privilege escalations
- Default for most workloads

**Restricted** (heavily restricted):
- Follows pod hardening best practices
- Recommended for security-critical workloads

### Pod Security Admission

**Namespace Labels**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

**Modes**:
- `enforce`: Rejects pods violating policy
- `audit`: Logs violations in audit log
- `warn`: Returns warning to user

### Security Context

**Pod Security Context**:
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    fsGroupChangePolicy: "OnRootMismatch"
    seccompProfile:
      type: RuntimeDefault
    seLinuxOptions:
      level: "s0:c123,c456"
    supplementalGroups: [4000]
    sysctls:
    - name: net.ipv4.ip_local_port_range
      value: "1024 65535"
```

**Container Security Context**:
```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
      seccompProfile:
        type: RuntimeDefault
```

### Capabilities

**Common Capabilities**:
- `CHOWN`: Change file ownership
- `DAC_OVERRIDE`: Bypass file permissions
- `FSETID`: Set file capabilities
- `KILL`: Send signals
- `NET_BIND_SERVICE`: Bind to ports < 1024
- `SETFCAP`: Set file capabilities
- `SETGID`: Set group ID
- `SETUID`: Set user ID
- `SYS_CHROOT`: Use chroot

**Best Practice**:
```yaml
securityContext:
  capabilities:
    drop:
    - ALL  # Drop all capabilities
    add:
    - NET_BIND_SERVICE  # Add only what's needed
```

### AppArmor

**Profile Selection**:
```yaml
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-apparmor-example
```

**Profile Types**:
- `runtime/default`: Default container runtime profile
- `localhost/<profile>`: Custom profile on node
- `unconfined`: No AppArmor profile

### SELinux

**SELinux Options**:
```yaml
securityContext:
  seLinuxOptions:
    user: system_u
    role: system_r
    type: container_t
    level: s0:c100,c200
```

### Seccomp

**Seccomp Profiles**:
```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault  # Default runtime profile (recommended)
```

```yaml
securityContext:
  seccompProfile:
    type: Localhost
    localhostProfile: profiles/audit.json
```

**Profile Types**:
- `RuntimeDefault`: Default container runtime profile
- `Unconfined`: No seccomp profile
- `Localhost`: Custom profile from node

## Network Security

### Network Policies

**Default Deny All**:
```yaml
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
```

**Allow Specific Ingress**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          name: production
    ports:
    - protocol: TCP
      port: 8080
```

**Allow DNS**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
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

### Service Mesh Security

**Istio mTLS**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

**Istio Authorization Policy**:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

## Secrets Management

### Kubernetes Secrets

**Creating Secrets**:
```bash
# From literal
kubectl create secret generic db-pass --from-literal=password=secretpass

# From file
kubectl create secret generic ssh-key --from-file=ssh-privatekey=~/.ssh/id_rsa

# TLS secret
kubectl create secret tls tls-secret --cert=path/to/tls.cert --key=path/to/tls.key
```

**Secret Types**:
- `Opaque`: Arbitrary user-defined data (default)
- `kubernetes.io/service-account-token`: Service account token
- `kubernetes.io/dockercfg`: Docker config
- `kubernetes.io/dockerconfigjson`: Docker config JSON
- `kubernetes.io/basic-auth`: Basic authentication
- `kubernetes.io/ssh-auth`: SSH authentication
- `kubernetes.io/tls`: TLS certificate

**Using Secrets**:
```yaml
# As environment variables
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-pass
      key: password

# As volume
volumes:
- name: secret-volume
  secret:
    secretName: db-pass
    items:
    - key: password
      path: db-password
```

### External Secrets

**External Secrets Operator**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: vault-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: db-credentials
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/db
      property: password
```

**Sealed Secrets**:
```bash
# Encrypt secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml
```

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: mysecret
spec:
  encryptedData:
    password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...
```

### HashiCorp Vault Integration

**Vault Agent Injector**:
```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "myapp"
  vault.hashicorp.com/agent-inject-secret-database: "secret/data/database"
  vault.hashicorp.com/agent-inject-template-database: |
    {{- with secret "secret/data/database" -}}
    postgresql://{{ .Data.data.username }}:{{ .Data.data.password }}@postgres:5432/mydb
    {{- end -}}
```

## Image Security

### Image Scanning

**Admission Controllers**:
- ImagePolicyWebhook: External image verification
- ValidatingAdmissionWebhook: Custom validation

**Image Scanners**:
- Trivy
- Clair
- Anchore
- Snyk
- Aqua Security

### Image Signing

**Cosign** (Sigstore):
```bash
# Sign image
cosign sign $IMAGE

# Verify signature
cosign verify $IMAGE
```

**Policy Enforcement**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    cosigned.sigstore.dev/imageSignature: |
      {"critical":{"image":{"docker-manifest-digest":"sha256:..."}}}
```

### Admission Controllers

**Pod Security Admission**:
- Enforces Pod Security Standards

**ImagePolicyWebhook**:
- External service validates images

**ValidatingAdmissionWebhook**:
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-validator
webhooks:
- name: validate.images.io
  clientConfig:
    service:
      name: image-validator
      namespace: kube-system
      path: /validate
  rules:
  - operations: ["CREATE", "UPDATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
```

### Image Best Practices

- Use minimal base images (distroless, Alpine)
- Scan images for vulnerabilities
- Sign and verify images
- Use private registries
- Implement image pull secrets
- Use specific image tags (not `latest`)
- Regular image updates for security patches

## Runtime Security

### Falco

**Falco Rules**:
```yaml
- rule: Terminal shell in container
  desc: A shell was spawned in a container
  condition: >
    spawned_process and container and
    proc.name in (shell_binaries)
  output: >
    Shell spawned in container
    (user=%user.name container_id=%container.id
    container_name=%container.name shell=%proc.name
    parent=%proc.pname cmdline=%proc.cmdline)
  priority: WARNING
```

### Runtime Monitoring

**Tools**:
- Falco: Runtime threat detection
- Sysdig: System monitoring
- Aqua Security: Runtime protection
- Tetragon: eBPF-based security observability

## Audit Logging

### Audit Policy

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  verbs: ["create", "update", "patch", "delete"]
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: Metadata
  verbs: ["get", "list", "watch"]
- level: None
  resources:
  - group: ""
    resources: ["events"]
```

**Audit Levels**:
- `None`: Don't log
- `Metadata`: Log metadata only
- `Request`: Log metadata and request body
- `RequestResponse`: Log metadata, request, and response

### API Server Configuration

```bash
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
--audit-log-path=/var/log/kubernetes/audit.log
--audit-log-maxage=30
--audit-log-maxbackup=10
--audit-log-maxsize=100
```

## Compliance & Hardening

### CIS Kubernetes Benchmark

**Tools**:
- kube-bench: CIS benchmark validation
- kubescape: Security posture management

**Key Areas**:
- Control plane configuration
- etcd configuration
- Control plane security
- Worker node configuration
- Pod security policies

### Security Scanning

```bash
# Run kube-bench
kube-bench run --targets master,node

# Run kubescape
kubescape scan framework nsa
```

## References

- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
