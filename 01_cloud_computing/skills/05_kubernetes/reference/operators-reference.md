# Kubernetes Operators Reference

## Operator Pattern Overview

### Definition
An operator is a Kubernetes extension that uses custom resources (CRDs) and custom controllers to manage complex applications and their components.

### Core Concepts
- **Custom Resource Definition (CRD)**: Extends Kubernetes API with custom resource types
- **Custom Controller**: Watches custom resources and reconciles desired vs actual state
- **Reconciliation Loop**: Continuous process to achieve desired state
- **Domain Knowledge**: Encodes operational knowledge about managing specific applications

### Operator Pattern Benefits
- Automates complex operational tasks
- Codifies domain-specific knowledge
- Enables self-healing and auto-scaling
- Simplifies application lifecycle management
- Provides consistent management across environments

## Custom Resource Definitions (CRDs)

### CRD Structure

**Basic CRD**:
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.example.com
spec:
  group: example.com
  names:
    kind: Database
    listKind: DatabaseList
    plural: databases
    singular: database
    shortNames:
    - db
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              size:
                type: string
                enum: ["small", "medium", "large"]
              version:
                type: string
                pattern: '^[0-9]+\.[0-9]+$'
              replicas:
                type: integer
                minimum: 1
                maximum: 5
            required:
            - size
            - version
          status:
            type: object
            properties:
              phase:
                type: string
              conditions:
                type: array
                items:
                  type: object
                  properties:
                    type:
                      type: string
                    status:
                      type: string
                    lastTransitionTime:
                      type: string
                      format: date-time
```

### Advanced CRD Features

**Validation**:
```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          replicas:
            type: integer
            minimum: 1
            maximum: 10
          region:
            type: string
            enum: ["us-east", "us-west", "eu-west"]
          config:
            type: object
            x-kubernetes-preserve-unknown-fields: true
```

**Default Values**:
```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          replicas:
            type: integer
            default: 3
          retention:
            type: string
            default: "30d"
```

**Subresources**:
```yaml
versions:
- name: v1
  subresources:
    status: {}  # Enable status subresource
    scale:      # Enable scale subresource
      specReplicasPath: .spec.replicas
      statusReplicasPath: .status.replicas
      labelSelectorPath: .status.labelSelector
```

**Additional Printer Columns**:
```yaml
versions:
- name: v1
  additionalPrinterColumns:
  - name: Size
    type: string
    jsonPath: .spec.size
  - name: Version
    type: string
    jsonPath: .spec.version
  - name: Replicas
    type: integer
    jsonPath: .spec.replicas
  - name: Status
    type: string
    jsonPath: .status.phase
  - name: Age
    type: date
    jsonPath: .metadata.creationTimestamp
```

**Multiple Versions**:
```yaml
versions:
- name: v1
  served: true
  storage: true
  schema:
    # v1 schema
- name: v1beta1
  served: true
  storage: false
  schema:
    # v1beta1 schema
  conversion:
    strategy: Webhook
    webhook:
      conversionReviewVersions: ["v1", "v1beta1"]
      clientConfig:
        service:
          namespace: default
          name: converter
          path: /convert
```

## Controller Pattern

### Reconciliation Loop

**Basic Pattern**:
```
1. Watch for changes to custom resources
2. Get current state of the resource
3. Get actual state of managed resources
4. Compare desired vs actual state
5. Take action to reconcile differences
6. Update status of custom resource
7. Requeue if needed
```

**Reconciliation Logic**:
```go
func (r *DatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. Fetch the custom resource
    var db examplev1.Database
    if err := r.Get(ctx, req.NamespacedName, &db); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. Check for deletion
    if !db.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, &db)
    }

    // 3. Ensure finalizer
    if !containsString(db.Finalizers, finalizerName) {
        db.Finalizers = append(db.Finalizers, finalizerName)
        if err := r.Update(ctx, &db); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 4. Get desired state
    desiredStatefulSet := r.constructStatefulSet(&db)

    // 5. Get actual state
    var actualStatefulSet appsv1.StatefulSet
    err := r.Get(ctx, types.NamespacedName{
        Name:      db.Name,
        Namespace: db.Namespace,
    }, &actualStatefulSet)

    // 6. Reconcile
    if err != nil && errors.IsNotFound(err) {
        // Create
        if err := r.Create(ctx, desiredStatefulSet); err != nil {
            return ctrl.Result{}, err
        }
    } else if err != nil {
        return ctrl.Result{}, err
    } else {
        // Update if needed
        if !reflect.DeepEqual(actualStatefulSet.Spec, desiredStatefulSet.Spec) {
            actualStatefulSet.Spec = desiredStatefulSet.Spec
            if err := r.Update(ctx, &actualStatefulSet); err != nil {
                return ctrl.Result{}, err
            }
        }
    }

    // 7. Update status
    db.Status.Phase = "Running"
    if err := r.Status().Update(ctx, &db); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}
```

### Controller Best Practices

**Idempotency**:
- Reconcile should be idempotent
- Same inputs should produce same outputs
- Handle multiple calls gracefully

**Finalizers**:
```yaml
metadata:
  finalizers:
  - database.example.com/cleanup
```

**Status Conditions**:
```yaml
status:
  conditions:
  - type: Ready
    status: "True"
    lastTransitionTime: "2024-01-01T00:00:00Z"
    reason: DatabaseReady
    message: "Database is ready"
  - type: Progressing
    status: "False"
    lastTransitionTime: "2024-01-01T00:00:00Z"
```

**Error Handling**:
- Transient errors: Requeue with backoff
- Permanent errors: Update status, don't requeue
- Use exponential backoff for retries

**Resource Ownership**:
```go
// Set owner reference
ctrl.SetControllerReference(&db, statefulSet, r.Scheme)
```

## Operator Development Frameworks

### Kubebuilder

**Project Initialization**:
```bash
# Initialize project
kubebuilder init --domain example.com --repo github.com/myorg/myoperator

# Create API
kubebuilder create api --group apps --version v1 --kind Database
```

**Project Structure**:
```
├── api/
│   └── v1/
│       ├── database_types.go
│       └── zz_generated.deepcopy.go
├── config/
│   ├── crd/
│   ├── rbac/
│   ├── manager/
│   └── samples/
├── controllers/
│   └── database_controller.go
├── main.go
└── Dockerfile
```

**Marker Comments** (code generation):
```go
// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:subresource:scale:specpath=.spec.replicas,statuspath=.status.replicas
// +kubebuilder:printcolumn:name="Size",type=string,JSONPath=`.spec.size`
// +kubebuilder:validation:Enum=small;medium;large
type Database struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   DatabaseSpec   `json:"spec,omitempty"`
    Status DatabaseStatus `json:"status,omitempty"`
}
```

**RBAC Markers**:
```go
// +kubebuilder:rbac:groups=apps.example.com,resources=databases,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=apps.example.com,resources=databases/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=apps,resources=statefulsets,verbs=get;list;watch;create;update;patch;delete
```

### Operator SDK

**Project Types**:
1. **Go**: Full-featured Go-based operators
2. **Ansible**: Ansible-based operators
3. **Helm**: Helm-based operators

**Go Operator**:
```bash
# Initialize
operator-sdk init --domain example.com --repo github.com/myorg/myoperator

# Create API
operator-sdk create api --group apps --version v1 --kind Database
```

**Ansible Operator**:
```bash
# Initialize
operator-sdk init --plugins=ansible --domain example.com

# Create API
operator-sdk create api --group apps --version v1 --kind Database
```

**Helm Operator**:
```bash
# Initialize from existing Helm chart
operator-sdk init --plugins=helm --domain example.com
operator-sdk create api --group apps --version v1 --kind Database --helm-chart=./mychart
```

### Controller-Runtime

**Manager**:
```go
mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
    Scheme:                 scheme,
    MetricsBindAddress:     metricsAddr,
    Port:                   9443,
    HealthProbeBindAddress: probeAddr,
    LeaderElection:         enableLeaderElection,
    LeaderElectionID:       "abc123.example.com",
})
```

**Client**:
```go
// Get
var db examplev1.Database
err := r.Get(ctx, req.NamespacedName, &db)

// Create
err := r.Create(ctx, &deployment)

// Update
err := r.Update(ctx, &db)

// Patch
patch := client.MergeFrom(db.DeepCopy())
db.Status.Phase = "Running"
err := r.Status().Patch(ctx, &db, patch)

// Delete
err := r.Delete(ctx, &db)

// List
var dbList examplev1.DatabaseList
err := r.List(ctx, &dbList, client.InNamespace("default"))
```

**Watches**:
```go
// Watch primary resource
err = c.Watch(&source.Kind{Type: &appsv1.Database{}}, &handler.EnqueueRequestForObject{})

// Watch owned resources
err = c.Watch(&source.Kind{Type: &appsv1.StatefulSet{}}, &handler.EnqueueRequestForOwner{
    OwnerType:    &appsv1.Database{},
    IsController: true,
})

// Watch with predicate
err = c.Watch(&source.Kind{Type: &appsv1.Database{}}, &handler.EnqueueRequestForObject{},
    predicate.Funcs{
        UpdateFunc: func(e event.UpdateEvent) bool {
            return e.ObjectOld.GetGeneration() != e.ObjectNew.GetGeneration()
        },
    },
)
```

## Popular Operators

### Prometheus Operator

**ServiceMonitor**:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: example-app
spec:
  selector:
    matchLabels:
      app: example-app
  endpoints:
  - port: metrics
    interval: 30s
```

**PrometheusRule**:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: example-rules
spec:
  groups:
  - name: example
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status="500"}[5m]) > 0.05
      for: 10m
      labels:
        severity: warning
```

### Cert-Manager

**Certificate**:
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com
spec:
  secretName: example-com-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - example.com
  - www.example.com
```

**ClusterIssuer**:
```yaml
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

### Strimzi Kafka Operator

**Kafka Cluster**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
spec:
  kafka:
    version: 3.3.1
    replicas: 3
    listeners:
    - name: plain
      port: 9092
      type: internal
      tls: false
    - name: tls
      port: 9093
      type: internal
      tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
    storage:
      type: persistent-claim
      size: 100Gi
      deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

### KEDA (Kubernetes Event-Driven Autoscaling)

**ScaledObject**:
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-scaledobject
spec:
  scaleTargetRef:
    name: kafka-consumer
  minReplicaCount: 1
  maxReplicaCount: 10
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka:9092
      consumerGroup: my-group
      topic: orders
      lagThreshold: "50"
```

### ArgoCD

**Application**:
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
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Operator Lifecycle Manager (OLM)

### ClusterServiceVersion (CSV)

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: ClusterServiceVersion
metadata:
  name: database-operator.v1.0.0
spec:
  displayName: Database Operator
  version: 1.0.0
  replaces: database-operator.v0.9.0
  install:
    strategy: deployment
    spec:
      deployments:
      - name: database-operator
        spec:
          replicas: 1
          selector:
            matchLabels:
              name: database-operator
          template:
            metadata:
              labels:
                name: database-operator
            spec:
              containers:
              - name: operator
                image: example.com/database-operator:v1.0.0
```

### Subscription

```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: database-operator
  namespace: operators
spec:
  channel: stable
  name: database-operator
  source: operatorhub
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
```

## Operator Best Practices

### Design
- Follow Kubernetes conventions
- Use status conditions
- Implement proper RBAC
- Support multiple versions
- Provide clear documentation
- Handle upgrades gracefully

### Implementation
- Idempotent reconciliation
- Use finalizers for cleanup
- Implement proper error handling
- Use exponential backoff
- Set owner references
- Update status subresource

### Operations
- Enable leader election
- Implement health checks
- Expose metrics
- Provide detailed logging
- Support multiple namespaces
- Plan for disaster recovery

### Testing
- Unit tests for business logic
- Integration tests with envtest
- E2E tests in real cluster
- Upgrade/downgrade tests
- Failure scenario tests
- Performance tests

## References

- [Operator Pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [Kubebuilder Book](https://book.kubebuilder.io/)
- [Operator SDK](https://sdk.operatorframework.io/)
- [Controller Runtime](https://pkg.go.dev/sigs.k8s.io/controller-runtime)
- [OperatorHub.io](https://operatorhub.io/)
