# Workload Resources Reference

## Overview

Workload resources in Kubernetes manage the deployment and lifecycle of pods. Each resource type serves specific use cases and provides different guarantees around pod lifecycle, ordering, and state management.

## Pod

### Definition
The smallest deployable unit in Kubernetes. A pod encapsulates one or more containers with shared storage, network, and specification for how to run the containers.

### Pod Lifecycle Phases
- **Pending**: Pod accepted but containers not yet created
- **Running**: Pod bound to node, all containers created, at least one running
- **Succeeded**: All containers terminated successfully
- **Failed**: All containers terminated, at least one failed
- **Unknown**: Pod state cannot be determined

### Pod Conditions
- **PodScheduled**: Pod has been scheduled to a node
- **ContainersReady**: All containers in pod are ready
- **Initialized**: All init containers have completed successfully
- **Ready**: Pod is ready to serve requests

### Container Types

**Init Containers**:
- Run before app containers
- Must complete successfully before app containers start
- Run sequentially in order defined
- Use cases: Setup scripts, wait for dependencies, security/compliance checks

**App Containers**:
- Main application containers
- Run concurrently
- Should remain running

**Ephemeral Containers**:
- Added to running pod for debugging
- Cannot be used in pod spec
- No resource guarantees
- Useful for distroless image debugging

### Pod Patterns

**Sidecar Pattern**:
```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0
  - name: log-shipper
    image: fluentd:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
```

**Ambassador Pattern**:
- Sidecar proxy for external services
- Abstract connection details from main container

**Adapter Pattern**:
- Standardize output from heterogeneous containers
- Transform logs, metrics to common format

### Resource Management

**Requests**: Minimum resources guaranteed
**Limits**: Maximum resources container can use

**QoS Classes**:
1. **Guaranteed**: requests = limits for all containers
2. **Burstable**: At least one container has request < limit
3. **BestEffort**: No requests or limits set

### Pod Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop:
    - ALL
    add:
    - NET_BIND_SERVICE
```

## ReplicaSet

### Purpose
Maintains a stable set of replica pods running at any given time. Typically used through Deployments rather than directly.

### Use Cases
- Ensure specified number of pod replicas
- Self-healing: recreate pods if they fail
- Scaling: adjust number of replicas

### Selector Types
- **matchLabels**: Equality-based (key: value)
- **matchExpressions**: Set-based (In, NotIn, Exists, DoesNotExist)

### Best Practices
- Use Deployments instead of ReplicaSets directly
- Set appropriate replica count based on load
- Use pod disruption budgets for critical workloads
- Label pods consistently

## Deployment

### Purpose
Declarative updates for pods and ReplicaSets. Provides rolling updates, rollback capabilities, and version history.

### Deployment Strategies

**RollingUpdate** (default):
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%        # Max pods above desired count
    maxUnavailable: 25%  # Max pods unavailable during update
```

**Recreate**:
```yaml
strategy:
  type: Recreate  # Terminate all pods before creating new ones
```

### Deployment Operations

**Create Deployment**:
```bash
kubectl create deployment nginx --image=nginx:1.21
```

**Update Image**:
```bash
kubectl set image deployment/nginx nginx=nginx:1.22
```

**Scale**:
```bash
kubectl scale deployment/nginx --replicas=5
```

**Rollout Status**:
```bash
kubectl rollout status deployment/nginx
```

**Rollback**:
```bash
kubectl rollout undo deployment/nginx
kubectl rollout undo deployment/nginx --to-revision=2
```

**Pause/Resume**:
```bash
kubectl rollout pause deployment/nginx
kubectl rollout resume deployment/nginx
```

### Advanced Deployment Patterns

**Blue-Green Deployment**:
- Deploy new version alongside old
- Switch service to new version
- Keep old version for quick rollback

**Canary Deployment**:
- Route small percentage to new version
- Gradually increase traffic
- Monitor metrics before full rollout

**Progressive Delivery**:
- Combine canary with automated analysis
- Tools: Flagger, Argo Rollouts

### Deployment Best Practices
- Always set resource requests and limits
- Define readiness and liveness probes
- Use rolling updates with appropriate maxSurge/maxUnavailable
- Keep revision history (revisionHistoryLimit)
- Use pod disruption budgets
- Set appropriate replicas for HA

## StatefulSet

### Purpose
Manages stateful applications requiring stable network identities, persistent storage, and ordered deployment/scaling.

### Guarantees
- **Stable Network Identity**: Predictable pod names (name-0, name-1, ...)
- **Stable Storage**: PersistentVolumeClaims persist across rescheduling
- **Ordered Deployment**: Pods created sequentially (0 to n-1)
- **Ordered Termination**: Pods deleted in reverse order (n-1 to 0)
- **Ordered Rolling Updates**: Updates proceed in order

### StatefulSet Example
```yaml
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
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

### Pod Identity
- **Ordinal Index**: 0 to n-1
- **Pod Name**: $(statefulset name)-$(ordinal)
- **DNS**: $(podname).$(service name).$(namespace).svc.cluster.local

### Update Strategies

**RollingUpdate**:
- Default strategy
- Updates pods in reverse ordinal order
- Waits for each pod to be Ready before continuing

**OnDelete**:
- Manual updates
- Pods updated only when manually deleted

**Partitions**:
```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 2  # Only update pods >= ordinal 2
```

### Use Cases
- Databases (MySQL, PostgreSQL, MongoDB)
- Distributed systems (Kafka, ZooKeeper, Elasticsearch)
- Stateful applications requiring stable identity

### Best Practices
- Always use headless service (clusterIP: None)
- Define appropriate PVC template
- Set pod management policy (OrderedReady vs Parallel)
- Use init containers for initialization
- Implement proper backup/restore procedures
- Consider using operators for complex stateful apps

## DaemonSet

### Purpose
Ensures a copy of a pod runs on all (or selected) nodes. Pods are added/removed as nodes join/leave cluster.

### Use Cases
- Node monitoring (Prometheus Node Exporter)
- Log collection (Fluentd, Filebeat)
- Storage daemons (Ceph, GlusterFS)
- Network plugins (CNI components)
- Security agents (Falco)

### DaemonSet Example
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluentd:latest
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

### Node Selection
- **nodeSelector**: Simple node filtering
- **Node Affinity**: More expressive node selection
- **Taints and Tolerations**: Control which nodes daemon runs on

### Update Strategy
**RollingUpdate**:
```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1  # Max unavailable during update
```

**OnDelete**:
- Manual updates by deleting pods

### Best Practices
- Set appropriate resource limits
- Use tolerations to run on all nodes if needed
- Be careful with host filesystem access
- Use read-only mounts when possible
- Implement graceful shutdown

## Job

### Purpose
Creates one or more pods and ensures a specified number complete successfully. Used for batch processing.

### Job Patterns

**Single Job**:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4
```

**Parallel Jobs - Fixed Completion Count**:
```yaml
spec:
  completions: 8
  parallelism: 2
  template:
    # Pod template
```

**Parallel Jobs - Work Queue**:
```yaml
spec:
  parallelism: 2
  template:
    # Pods coordinate via queue
```

### Job Parameters
- **completions**: Number of successful completions required
- **parallelism**: Maximum number of pods running concurrently
- **backoffLimit**: Number of retries before marking job as failed
- **activeDeadlineSeconds**: Maximum time job can run
- **ttlSecondsAfterFinished**: Cleanup completed jobs

### Restart Policy
- **Never**: Create new pod on failure
- **OnFailure**: Restart container in same pod

### Best Practices
- Set appropriate backoffLimit
- Use activeDeadlineSeconds for long-running jobs
- Clean up completed jobs (ttlSecondsAfterFinished or CronJob)
- Monitor job completion
- Use indexed jobs for parallelism (Kubernetes 1.21+)

## CronJob

### Purpose
Creates jobs on a repeating schedule (cron format).

### CronJob Example
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup:latest
            command: ["/backup.sh"]
          restartPolicy: OnFailure
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Forbid
```

### Cron Schedule Format
```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
# │ │ │ │ │
# * * * * *
```

**Examples**:
- `*/5 * * * *` - Every 5 minutes
- `0 */2 * * *` - Every 2 hours
- `0 9 * * 1-5` - 9 AM Monday-Friday
- `0 0 1 * *` - First day of month

### Concurrency Policy
- **Allow**: Allow concurrent jobs (default)
- **Forbid**: Skip new job if previous still running
- **Replace**: Cancel running job and start new one

### Parameters
- **successfulJobsHistoryLimit**: Number of successful jobs to keep
- **failedJobsHistoryLimit**: Number of failed jobs to keep
- **startingDeadlineSeconds**: Deadline for starting job if missed
- **suspend**: Suspend subsequent executions

### Best Practices
- Use Forbid or Replace for jobs that shouldn't overlap
- Set appropriate history limits
- Monitor job failures
- Consider timezone (CronJob uses controller manager timezone)
- Use startingDeadlineSeconds for critical jobs
- Test schedule with online cron validators

## Horizontal Pod Autoscaler (HPA)

### Purpose
Automatically scales pods based on observed metrics (CPU, memory, custom metrics).

### HPA Example
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx
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
        type: AverageValue
        averageValue: 500Mi
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Metric Types
- **Resource**: CPU, memory (requires Metrics Server)
- **Pods**: Custom metrics from pods
- **Object**: Metrics from other objects (Ingress QPS)
- **External**: Metrics from external systems

### Algorithm
```
desiredReplicas = ceil[currentReplicas * (currentMetric / targetMetric)]
```

### Best Practices
- Set resource requests (required for CPU/memory-based HPA)
- Define appropriate min/max replicas
- Use stabilization window to prevent flapping
- Monitor HPA events
- Combine multiple metrics carefully
- Use behavior configuration for fine control

## Vertical Pod Autoscaler (VPA)

### Purpose
Automatically adjusts CPU and memory requests/limits based on usage.

### VPA Modes
- **Off**: Only provide recommendations
- **Initial**: Set resources on pod creation only
- **Recreate**: Update running pods (requires pod restart)
- **Auto**: Automatic mode

### Use Cases
- Right-sizing pods
- Adapting to changing workload patterns
- Reducing manual tuning

### Limitations
- Cannot use with HPA on same metrics
- Requires pod restart for updates (in Recreate mode)
- No support for JVM-based apps without tuning

## Pod Disruption Budget (PDB)

### Purpose
Limits disruptions during voluntary disruptions (node drains, upgrades).

### PDB Example
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nginx-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: nginx
```

### Configuration Options
- **minAvailable**: Minimum pods that must remain available
- **maxUnavailable**: Maximum pods that can be unavailable

### Use Cases
- Protect during cluster upgrades
- Ensure availability during node maintenance
- Prevent cascading failures

## References

- [Kubernetes Workload Resources](https://kubernetes.io/docs/concepts/workloads/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
