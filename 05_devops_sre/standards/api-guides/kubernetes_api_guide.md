# Kubernetes API Guide

## Table of Contents
- [Kubernetes API Fundamentals](#kubernetes-api-fundamentals)
- [Working with the API](#working-with-the-api)
- [Custom Resource Definitions (CRDs)](#custom-resource-definitions-crds)
- [Kubernetes Operators](#kubernetes-operators)
- [API Extensions](#api-extensions)
- [Client Libraries](#client-libraries)
- [Best Practices](#best-practices)

---

## Kubernetes API Fundamentals

### API Structure

Kubernetes API follows a RESTful design organized by:
- **API Groups**: Logical grouping of resources (e.g., `apps`, `batch`, `networking.k8s.io`)
- **Versions**: API maturity levels (`v1`, `v1beta1`, `v1alpha1`)
- **Resources**: Objects managed by the API (pods, services, deployments)
- **Verbs**: Operations on resources (get, list, create, update, delete, watch)

### API URL Structure

```
/apis/{group}/{version}/namespaces/{namespace}/{resource}/{name}
```

**Examples**:
```bash
# Core API (no group)
/api/v1/namespaces/default/pods/nginx

# Apps API group
/apis/apps/v1/namespaces/default/deployments/web-app

# Custom resource
/apis/example.com/v1/namespaces/default/widgets/my-widget
```

### API Discovery

```bash
# List all API groups
kubectl api-resources

# Get API versions for a group
kubectl api-versions

# Explain resource schema
kubectl explain pod
kubectl explain deployment.spec.strategy

# Get OpenAPI spec
kubectl get --raw /openapi/v2 > swagger.json
```

---

## Working with the API

### 1. Using kubectl with Raw API

```bash
# GET request
kubectl get --raw /api/v1/namespaces/default/pods

# Create resource via API
kubectl create --raw /api/v1/namespaces/default/pods \
  -f pod.json \
  --output=json

# Proxy to access API locally
kubectl proxy --port=8080 &
curl http://localhost:8080/api/v1/namespaces/default/pods
```

### 2. Direct API Access with curl

```bash
# Get API server address
APISERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

# Get token
TOKEN=$(kubectl create token default -n default)

# Make request
curl -X GET $APISERVER/api/v1/namespaces/default/pods \
  --header "Authorization: Bearer $TOKEN" \
  --cacert /path/to/ca.crt
```

### 3. Using Service Account from Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-client
spec:
  serviceAccountName: api-reader
  containers:
  - name: client
    image: alpine:latest
    command:
    - sh
    - -c
    - |
      apk add --no-cache curl
      APISERVER=https://kubernetes.default.svc
      TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
      CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

      # List pods
      curl -X GET $APISERVER/api/v1/namespaces/default/pods \
        --header "Authorization: Bearer $TOKEN" \
        --cacert $CACERT
```

### 4. Watch API (Streaming)

**Concept**: Long-polling for resource changes

```bash
# Watch pods
kubectl get pods --watch

# Raw API watch
kubectl get --raw '/api/v1/namespaces/default/pods?watch=true'
```

**Response Format**:
```json
{
  "type": "ADDED",
  "object": {
    "kind": "Pod",
    "metadata": {...},
    "spec": {...}
  }
}
{
  "type": "MODIFIED",
  "object": {...}
}
{
  "type": "DELETED",
  "object": {...}
}
```

---

## Custom Resource Definitions (CRDs)

### 1. Creating a CRD

**Use Case**: Extend Kubernetes with custom resources

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
              engine:
                type: string
                enum: ["postgres", "mysql", "mongodb"]
              version:
                type: string
              size:
                type: string
                enum: ["small", "medium", "large"]
              replicas:
                type: integer
                minimum: 1
                maximum: 5
              backup:
                type: object
                properties:
                  enabled:
                    type: boolean
                  schedule:
                    type: string
                  retention:
                    type: integer
            required: ["engine", "version", "size"]
          status:
            type: object
            properties:
              phase:
                type: string
              message:
                type: string
              endpoint:
                type: string
              ready:
                type: boolean
    subresources:
      status: {}
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
    additionalPrinterColumns:
    - name: Engine
      type: string
      jsonPath: .spec.engine
    - name: Version
      type: string
      jsonPath: .spec.version
    - name: Status
      type: string
      jsonPath: .status.phase
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
```

### 2. Using the Custom Resource

```yaml
apiVersion: example.com/v1
kind: Database
metadata:
  name: my-postgres
  namespace: production
spec:
  engine: postgres
  version: "14.5"
  size: medium
  replicas: 3
  backup:
    enabled: true
    schedule: "0 2 * * *"
    retention: 30
```

```bash
# Create resource
kubectl apply -f database.yaml

# List databases
kubectl get databases
kubectl get db  # Using short name

# Describe
kubectl describe database my-postgres

# Watch changes
kubectl get databases --watch
```

### 3. Advanced CRD Features

**Validation Rules**:
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
          resources:
            type: object
            properties:
              cpu:
                type: string
                pattern: '^[0-9]+m?$'
              memory:
                type: string
                pattern: '^[0-9]+(Mi|Gi)$'
        x-kubernetes-validations:
        - rule: "self.replicas <= 5 || self.size == 'large'"
          message: "More than 5 replicas requires 'large' size"
```

**Default Values**:
```yaml
spec:
  properties:
    replicas:
      type: integer
      default: 1
    backup:
      type: object
      default:
        enabled: false
        retention: 7
```

**Versioning and Conversion**:
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.example.com
spec:
  group: example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema: {...}
  - name: v1beta1
    served: true
    storage: false
    deprecated: true
    deprecationWarning: "v1beta1 is deprecated, use v1"
    schema: {...}
  conversion:
    strategy: Webhook
    webhook:
      clientConfig:
        service:
          namespace: default
          name: database-webhook
          path: /convert
        caBundle: <base64-encoded-ca>
```

---

## Kubernetes Operators

### 1. Operator Pattern

**Components**:
- **CRD**: Defines the API
- **Controller**: Reconciliation loop watching CRDs
- **Webhooks**: Admission control, validation, mutation

### 2. Building an Operator with Kubebuilder

**Initialize project**:
```bash
kubebuilder init --domain example.com --repo github.com/myorg/database-operator

# Create API
kubebuilder create api --group example --version v1 --kind Database
```

**Controller Logic** (api/v1/database_types.go):
```go
package v1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// DatabaseSpec defines the desired state
type DatabaseSpec struct {
    Engine   string `json:"engine"`
    Version  string `json:"version"`
    Size     string `json:"size"`
    Replicas int32  `json:"replicas"`
}

// DatabaseStatus defines the observed state
type DatabaseStatus struct {
    Phase    string `json:"phase,omitempty"`
    Ready    bool   `json:"ready,omitempty"`
    Endpoint string `json:"endpoint,omitempty"`
    Message  string `json:"message,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:printcolumn:name="Engine",type=string,JSONPath=`.spec.engine`
//+kubebuilder:printcolumn:name="Status",type=string,JSONPath=`.status.phase`
//+kubebuilder:printcolumn:name="Age",type=date,JSONPath=`.metadata.creationTimestamp`

type Database struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   DatabaseSpec   `json:"spec,omitempty"`
    Status DatabaseStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

type DatabaseList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []Database `json:"items"`
}

func init() {
    SchemeBuilder.Register(&Database{}, &DatabaseList{})
}
```

**Reconciliation Loop** (controllers/database_controller.go):
```go
package controllers

import (
    "context"
    "time"

    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"

    examplev1 "github.com/myorg/database-operator/api/v1"
)

type DatabaseReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

//+kubebuilder:rbac:groups=example.example.com,resources=databases,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=example.example.com,resources=databases/status,verbs=get;update;patch
//+kubebuilder:rbac:groups=apps,resources=statefulsets,verbs=get;list;watch;create;update;patch;delete
//+kubebuilder:rbac:groups=core,resources=services,verbs=get;list;watch;create;update;patch;delete

func (r *DatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // Fetch the Database instance
    database := &examplev1.Database{}
    err := r.Get(ctx, req.NamespacedName, database)
    if err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Reconciliation logic
    log.Info("Reconciling Database", "name", database.Name)

    // 1. Create or update StatefulSet
    if err := r.reconcileStatefulSet(ctx, database); err != nil {
        return ctrl.Result{}, err
    }

    // 2. Create or update Service
    if err := r.reconcileService(ctx, database); err != nil {
        return ctrl.Result{}, err
    }

    // 3. Update status
    database.Status.Phase = "Running"
    database.Status.Ready = true
    database.Status.Endpoint = database.Name + "-svc." + database.Namespace + ".svc.cluster.local"

    if err := r.Status().Update(ctx, database); err != nil {
        return ctrl.Result{}, err
    }

    // Requeue after 30 seconds to check status
    return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}

func (r *DatabaseReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&examplev1.Database{}).
        Owns(&appsv1.StatefulSet{}).
        Owns(&corev1.Service{}).
        Complete(r)
}
```

### 3. Admission Webhooks

**Validating Webhook**:
```go
//+kubebuilder:webhook:path=/validate-example-example-com-v1-database,mutating=false,failurePolicy=fail,groups=example.example.com,resources=databases,verbs=create;update,versions=v1,name=vdatabase.kb.io

func (r *Database) ValidateCreate() error {
    if r.Spec.Replicas > 5 && r.Spec.Size != "large" {
        return fmt.Errorf("replicas > 5 requires size 'large'")
    }
    return nil
}

func (r *Database) ValidateUpdate(old runtime.Object) error {
    oldDB := old.(*Database)
    if oldDB.Spec.Engine != r.Spec.Engine {
        return fmt.Errorf("engine cannot be changed")
    }
    return nil
}
```

**Mutating Webhook**:
```go
//+kubebuilder:webhook:path=/mutate-example-example-com-v1-database,mutating=true,failurePolicy=fail,groups=example.example.com,resources=databases,verbs=create;update,versions=v1,name=mdatabase.kb.io

func (r *Database) Default() {
    if r.Spec.Replicas == 0 {
        r.Spec.Replicas = 1
    }
    if r.Labels == nil {
        r.Labels = make(map[string]string)
    }
    r.Labels["managed-by"] = "database-operator"
}
```

### 4. Operator Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-operator
  namespace: operators
spec:
  replicas: 1
  selector:
    matchLabels:
      control-plane: database-operator
  template:
    metadata:
      labels:
        control-plane: database-operator
    spec:
      serviceAccountName: database-operator
      containers:
      - name: manager
        image: database-operator:v1.0.0
        command:
        - /manager
        args:
        - --leader-elect
        resources:
          limits:
            cpu: 500m
            memory: 128Mi
          requests:
            cpu: 10m
            memory: 64Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8081
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8081
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: database-operator
  namespace: operators

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: database-operator-role
rules:
- apiGroups: ["example.com"]
  resources: ["databases"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["example.com"]
  resources: ["databases/status"]
  verbs: ["get", "update", "patch"]
- apiGroups: ["apps"]
  resources: ["statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["services"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: database-operator-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: database-operator-role
subjects:
- kind: ServiceAccount
  name: database-operator
  namespace: operators
```

---

## API Extensions

### 1. Aggregated API Servers

**Use Case**: Extend the Kubernetes API with custom implementations

```yaml
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  name: v1beta1.metrics.k8s.io
spec:
  service:
    name: metrics-server
    namespace: kube-system
    port: 443
  group: metrics.k8s.io
  version: v1beta1
  insecureSkipTLSVerify: false
  caBundle: <base64-ca-cert>
  groupPriorityMinimum: 100
  versionPriority: 100
```

### 2. API Priority and Fairness

**Use Case**: Protect API server from overload

```yaml
apiVersion: flowcontrol.apiserver.k8s.io/v1beta2
kind: FlowSchema
metadata:
  name: critical-workloads
spec:
  priorityLevelConfiguration:
    name: workload-high
  matchingPrecedence: 1000
  distinguisherMethod:
    type: ByUser
  rules:
  - subjects:
    - kind: ServiceAccount
      namespace: critical-apps
      name: "*"
    resourceRules:
    - verbs: ["*"]
      apiGroups: ["*"]
      resources: ["*"]
      namespaces: ["critical-apps"]

---
apiVersion: flowcontrol.apiserver.k8s.io/v1beta2
kind: PriorityLevelConfiguration
metadata:
  name: workload-high
spec:
  type: Limited
  limited:
    assuredConcurrencyShares: 100
    limitResponse:
      type: Queue
      queuing:
        queues: 128
        queueLengthLimit: 50
        handSize: 6
```

---

## Client Libraries

### 1. Python Client

**Installation**:
```bash
pip install kubernetes
```

**Usage**:
```python
from kubernetes import client, config, watch

# Load config
config.load_incluster_config()  # When running in cluster
# config.load_kube_config()  # When running locally

v1 = client.CoreV1Api()

# List pods
pods = v1.list_namespaced_pod(namespace="default")
for pod in pods.items:
    print(f"{pod.metadata.name} - {pod.status.phase}")

# Create pod
pod_manifest = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {"name": "my-pod"},
    "spec": {
        "containers": [
            {
                "name": "nginx",
                "image": "nginx:latest",
                "ports": [{"containerPort": 80}]
            }
        ]
    }
}
v1.create_namespaced_pod(namespace="default", body=pod_manifest)

# Watch pods
w = watch.Watch()
for event in w.stream(v1.list_namespaced_pod, namespace="default"):
    print(f"Event: {event['type']} {event['object'].metadata.name}")

# Custom resources
api = client.CustomObjectsApi()
databases = api.list_namespaced_custom_object(
    group="example.com",
    version="v1",
    namespace="default",
    plural="databases"
)
```

### 2. Go Client

**Installation**:
```bash
go get k8s.io/client-go@latest
```

**Usage**:
```go
package main

import (
    "context"
    "fmt"
    "path/filepath"

    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/util/homedir"
)

func main() {
    // Build config
    kubeconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
    config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        panic(err)
    }

    // Create client
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        panic(err)
    }

    // List pods
    pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{})
    if err != nil {
        panic(err)
    }

    for _, pod := range pods.Items {
        fmt.Printf("%s - %s\n", pod.Name, pod.Status.Phase)
    }

    // Watch pods
    watcher, err := clientset.CoreV1().Pods("default").Watch(context.TODO(), metav1.ListOptions{})
    if err != nil {
        panic(err)
    }

    for event := range watcher.ResultChan() {
        pod := event.Object.(*v1.Pod)
        fmt.Printf("Event: %s %s\n", event.Type, pod.Name)
    }
}
```

### 3. JavaScript/TypeScript Client

**Installation**:
```bash
npm install @kubernetes/client-node
```

**Usage**:
```typescript
import * as k8s from '@kubernetes/client-node';

const kc = new k8s.KubeConfig();
kc.loadFromDefault();

const k8sApi = kc.makeApiClient(k8s.CoreV1Api);

// List pods
k8sApi.listNamespacedPod('default').then((res) => {
    res.body.items.forEach((pod) => {
        console.log(`${pod.metadata.name} - ${pod.status.phase}`);
    });
});

// Watch pods
const watch = new k8s.Watch(kc);
watch.watch('/api/v1/namespaces/default/pods',
    {},
    (type, apiObj, watchObj) => {
        console.log(`Event: ${type} ${apiObj.metadata.name}`);
    },
    (err) => {
        console.error(err);
    }
);
```

---

## Best Practices

### 1. API Design

- **Use proper API versioning**: `v1alpha1` → `v1beta1` → `v1`
- **Make fields optional when possible**: Use default values
- **Design for immutability**: Separate spec and status
- **Use meaningful status conditions**: Help users understand state
- **Implement proper validation**: Fail fast with clear messages

### 2. Controller Development

- **Idempotent reconciliation**: Handle being called multiple times
- **Use owner references**: Enable garbage collection
- **Implement proper error handling**: Requeue on errors
- **Add finalizers for cleanup**: Ensure proper resource deletion
- **Use predicates to filter events**: Reduce reconciliation load

**Example with finalizers**:
```go
const finalizerName = "example.com/finalizer"

func (r *DatabaseReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    database := &examplev1.Database{}
    if err := r.Get(ctx, req.NamespacedName, database); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Check if being deleted
    if !database.DeletionTimestamp.IsZero() {
        if controllerutil.ContainsFinalizer(database, finalizerName) {
            // Cleanup external resources
            if err := r.cleanupExternalResources(ctx, database); err != nil {
                return ctrl.Result{}, err
            }

            // Remove finalizer
            controllerutil.RemoveFinalizer(database, finalizerName)
            if err := r.Update(ctx, database); err != nil {
                return ctrl.Result{}, err
            }
        }
        return ctrl.Result{}, nil
    }

    // Add finalizer if not present
    if !controllerutil.ContainsFinalizer(database, finalizerName) {
        controllerutil.AddFinalizer(database, finalizerName)
        if err := r.Update(ctx, database); err != nil {
            return ctrl.Result{}, err
        }
    }

    // Normal reconciliation logic
    return ctrl.Result{}, nil
}
```

### 3. Security

- **Use proper RBAC**: Least privilege principle
- **Validate all inputs**: Don't trust user data
- **Use admission webhooks**: Enforce policies
- **Audit API access**: Enable audit logging
- **Rotate credentials**: Use short-lived tokens

### 4. Performance

- **Use field selectors and label selectors**: Reduce data transfer
- **Implement pagination**: For large lists
- **Use watches efficiently**: Avoid polling
- **Cache frequently accessed data**: Use informers
- **Set appropriate resource limits**: On controllers

### 5. Testing

**Unit Tests**:
```go
func TestDatabaseReconciler(t *testing.T) {
    scheme := runtime.NewScheme()
    _ = examplev1.AddToScheme(scheme)

    db := &examplev1.Database{
        ObjectMeta: metav1.ObjectMeta{
            Name:      "test-db",
            Namespace: "default",
        },
        Spec: examplev1.DatabaseSpec{
            Engine: "postgres",
            Size:   "small",
        },
    }

    client := fake.NewClientBuilder().
        WithScheme(scheme).
        WithObjects(db).
        Build()

    reconciler := &DatabaseReconciler{
        Client: client,
        Scheme: scheme,
    }

    _, err := reconciler.Reconcile(context.TODO(), ctrl.Request{
        NamespacedName: types.NamespacedName{
            Name:      "test-db",
            Namespace: "default",
        },
    })

    assert.NoError(t, err)
}
```

---

## Summary

The Kubernetes API provides a powerful, extensible platform for managing containerized applications:

- **RESTful Design**: Consistent, discoverable API structure
- **CRDs**: Extend Kubernetes with custom resources
- **Operators**: Encode operational knowledge as code
- **Client Libraries**: Access API from any language
- **Webhooks**: Validate and mutate resources
- **API Extensions**: Add custom functionality

Master these concepts to build production-grade Kubernetes applications and operators.
