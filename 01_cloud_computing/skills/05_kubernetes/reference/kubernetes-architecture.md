# Kubernetes Architecture Reference

## Overview

Kubernetes is a distributed system for managing containerized applications. Its architecture follows a master-worker pattern with a declarative API and eventual consistency model.

## Control Plane Components

### API Server (kube-apiserver)
**Purpose**: Frontend to the Kubernetes control plane, exposes the Kubernetes API

**Key Responsibilities**:
- Validates and processes REST API requests
- Updates etcd with cluster state
- Serves as the only component that directly interacts with etcd
- Implements authentication, authorization, and admission control
- Provides the API for all cluster components

**Configuration Considerations**:
- Enable audit logging for compliance
- Configure authentication providers (OIDC, webhook, certificates)
- Set appropriate authorization modes (RBAC, ABAC, webhook)
- Enable admission controllers (ValidatingAdmissionWebhook, MutatingAdmissionWebhook, PodSecurityPolicy/Standards)
- Configure API rate limiting and request prioritization

**High Availability**:
- Run multiple API server instances (typically 3 or 5)
- Load balance across instances
- Each instance is stateless and independent

### etcd
**Purpose**: Consistent and highly-available key-value store for all cluster data

**Key Responsibilities**:
- Stores entire cluster state
- Provides distributed consensus (Raft algorithm)
- Watches for changes to propagate updates
- Ensures strong consistency

**Configuration Considerations**:
- Enable encryption at rest for sensitive data
- Configure regular backups (snapshots)
- Use dedicated disks (SSDs recommended)
- Set appropriate snapshot policies
- Monitor etcd performance metrics

**High Availability**:
- Deploy odd number of instances (3, 5, or 7)
- Requires majority quorum for writes
- Can tolerate (n-1)/2 failures
- Use stacked or external etcd topology

**Performance Best Practices**:
- Keep etcd datastore size under 8GB
- Use fast disks (low latency critical)
- Monitor fsync duration
- Compact etcd regularly
- Defragment when needed

### Scheduler (kube-scheduler)
**Purpose**: Assigns pods to nodes based on resource requirements and constraints

**Key Responsibilities**:
- Watches for newly created pods with no assigned node
- Runs filtering (predicate) and scoring (priority) functions
- Selects best node for pod placement
- Communicates decision to API server

**Scheduling Phases**:
1. **Filtering**: Eliminates unsuitable nodes
   - Resource requirements (CPU, memory, storage)
   - Node selectors and affinity rules
   - Taints and tolerations
   - Volume zone constraints

2. **Scoring**: Ranks remaining nodes
   - Resource balance
   - Spreading across zones/nodes
   - Pod affinity preferences
   - Custom scoring plugins

**Advanced Features**:
- Pod priority and preemption
- Topology spread constraints
- Custom scheduler extenders
- Multiple schedulers
- Scheduling profiles

### Controller Manager (kube-controller-manager)
**Purpose**: Runs core control loops that regulate cluster state

**Key Controllers**:

1. **Node Controller**
   - Monitors node health
   - Marks nodes as unreachable
   - Evicts pods from failed nodes

2. **Replication Controller**
   - Maintains correct number of pod replicas
   - Creates/deletes pods to match desired state

3. **Endpoints Controller**
   - Populates Endpoints objects (joins Services and Pods)

4. **Service Account & Token Controllers**
   - Creates default service accounts for namespaces
   - Manages API access tokens

5. **Namespace Controller**
   - Deletes all resources when namespace is deleted

6. **Persistent Volume Controllers**
   - PV/PVC binding
   - Dynamic provisioning
   - Volume lifecycle management

**Controller Pattern**:
```
while true:
  desired_state = read_from_api_server()
  current_state = observe_reality()
  if desired_state != current_state:
    make_changes_to_achieve_desired_state()
  sleep()
```

**Configuration**:
- Adjust reconciliation periods
- Set concurrent sync workers
- Configure leader election
- Enable/disable specific controllers

### Cloud Controller Manager
**Purpose**: Integrates with cloud provider APIs

**Cloud-Specific Controllers**:

1. **Node Controller**
   - Checks cloud provider to determine if node has been deleted
   - Updates node with cloud provider specific labels/metadata

2. **Route Controller**
   - Sets up routes in cloud infrastructure for pod networking

3. **Service Controller**
   - Creates/updates/deletes cloud load balancers for LoadBalancer services

4. **Volume Controller**
   - Creates/attaches/mounts cloud volumes

**Cloud Providers**:
- AWS (EKS)
- Azure (AKS)
- GCP (GKE)
- OpenStack
- vSphere

## Node Components

### Kubelet
**Purpose**: Agent running on each node, ensures containers are running in pods

**Key Responsibilities**:
- Registers node with API server
- Watches for pod assignments to its node
- Starts containers via container runtime (CRI)
- Monitors pod and container health
- Reports node and pod status to API server
- Executes liveness and readiness probes
- Manages volumes and secrets

**Container Runtime Interface (CRI)**:
- Abstraction layer for container runtimes
- Supports: containerd, CRI-O, Docker Engine (via cri-dockerd)

**Kubelet Configuration**:
- Resource reservation (system-reserved, kube-reserved)
- Eviction policies (memory, disk pressure)
- Image garbage collection
- Pod lifecycle event generator (PLEG)
- Authentication/authorization (webhook, certificate)

**Health Checks**:
- Node heartbeat (NodeStatus)
- Lease object updates (more efficient)

### Kube-Proxy
**Purpose**: Network proxy maintaining network rules for pod communication

**Proxy Modes**:

1. **iptables** (default in most distributions)
   - Uses iptables rules for traffic routing
   - Lower latency than userspace mode
   - Randomly selects backend pod
   - Can handle thousands of services

2. **IPVS** (recommended for large clusters)
   - Uses Linux IPVS (IP Virtual Server)
   - More efficient load balancing algorithms
   - Better performance at scale
   - Requires kernel IPVS modules

3. **userspace** (legacy, deprecated)
   - Runs proxy in userspace
   - Higher latency
   - Not recommended for production

4. **kernelspace** (Windows)
   - Windows HNS-based proxy

**Responsibilities**:
- Implements Service abstraction
- Load balances traffic to pod backends
- Handles NodePort, ClusterIP, LoadBalancer traffic
- Manages network rules for service discovery

### Container Runtime
**Purpose**: Software responsible for running containers

**Supported Runtimes**:

1. **containerd**
   - CNCF graduated project
   - Industry standard
   - Default in Kubernetes 1.24+
   - Lightweight and efficient

2. **CRI-O**
   - Kubernetes-specific runtime
   - OCI compliant
   - Minimal runtime focused on K8s

3. **Docker Engine** (via cri-dockerd)
   - Requires shim after Dockershim removal
   - More overhead than containerd
   - Still widely used

**Runtime Responsibilities**:
- Pull container images
- Unpack images
- Run containers
- Monitor container lifecycle
- Resource isolation (cgroups, namespaces)

## Add-Ons and Extensions

### CoreDNS
**Purpose**: Cluster DNS server for service discovery

**Features**:
- DNS-based service discovery
- Configurable via Corefile
- Plugin architecture
- Supports DNS forwarding
- Kubernetes-aware DNS resolution

**DNS Records**:
- Services: `<service>.<namespace>.svc.cluster.local`
- Pods: `<pod-ip-with-dashes>.<namespace>.pod.cluster.local`
- Headless services: Direct pod DNS names

### CNI Plugins
**Purpose**: Configure pod networking

**Popular CNI Plugins**:

1. **Calico**
   - L3 networking with BGP
   - Network policies
   - eBPF dataplane option
   - Enterprise support available

2. **Cilium**
   - eBPF-based networking
   - Advanced network policies (L7)
   - Service mesh features
   - Hubble observability

3. **Flannel**
   - Simple overlay network
   - Easy to deploy
   - Limited features
   - Good for getting started

4. **Weave Net**
   - Automatic network discovery
   - Encryption support
   - Network policies

5. **AWS VPC CNI**
   - Native AWS networking
   - Each pod gets VPC IP
   - Integrates with AWS security groups

### Metrics Server
**Purpose**: Cluster-wide aggregator of resource usage data

**Capabilities**:
- Collects CPU and memory metrics from kubelet
- Used by kubectl top
- Required for Horizontal Pod Autoscaler
- Short-term metrics storage (in-memory)

### Dashboard
**Purpose**: Web-based UI for Kubernetes clusters

**Features**:
- Deploy and manage applications
- Troubleshoot applications
- View cluster resources
- Create/modify Kubernetes resources via forms

## Architecture Patterns

### High Availability Control Plane

**Stacked etcd Topology**:
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   API Server    │  │   API Server    │  │   API Server    │
│   Scheduler     │  │   Scheduler     │  │   Scheduler     │
│   Controller    │  │   Controller    │  │   Controller    │
│      Mgr        │  │      Mgr        │  │      Mgr        │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│      etcd       │  │      etcd       │  │      etcd       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Pros**: Simpler to deploy, fewer servers
**Cons**: Coupled failure domains, etcd failure affects control plane

**External etcd Topology**:
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   API Server    │  │   API Server    │  │   API Server    │
│   Scheduler     │  │   Scheduler     │  │   Scheduler     │
│   Controller    │  │   Controller    │  │   Controller    │
│      Mgr        │  │      Mgr        │  │      Mgr        │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
         ┌────────────────────┴─────────────────────┐
         │                                           │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│      etcd       │  │      etcd       │  │      etcd       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Pros**: Decoupled failure domains, can scale independently
**Cons**: More servers required, slightly more complex

### Multi-Zone Deployment
- Spread control plane across availability zones
- Spread worker nodes across zones
- Use pod topology spread constraints
- Configure pod disruption budgets
- Use regional persistent volumes

### Multi-Cluster Architectures

**Patterns**:
1. **Regional Isolation**: Cluster per region for latency/compliance
2. **Environment Isolation**: Separate dev/staging/prod clusters
3. **Tenant Isolation**: Cluster per major tenant
4. **Workload Isolation**: Separate clusters for different workload types

**Management Approaches**:
- Cluster API for declarative cluster management
- GitOps for multi-cluster deployments
- Service mesh for cross-cluster communication
- Federated services for global load balancing

## Communication Patterns

### API Server Communication
- All components communicate through API server
- API server is the only component that talks to etcd
- Components watch for changes (long-polling)
- Optimistic concurrency with resource versions

### Pod-to-Pod Communication
- Each pod gets its own IP address
- Pods can communicate without NAT
- Implemented by CNI plugin
- Network policies control traffic

### Pod-to-Service Communication
- Services provide stable IP/DNS
- kube-proxy handles load balancing
- Multiple service types (ClusterIP, NodePort, LoadBalancer)

### External-to-Service Communication
- NodePort: Exposes service on each node's IP
- LoadBalancer: Provisions cloud load balancer
- Ingress: L7 load balancing and routing

## Security Architecture

### Defense in Depth Layers

1. **Cluster Access**
   - API server authentication
   - RBAC authorization
   - Admission control

2. **Pod Security**
   - Pod Security Standards
   - Security contexts
   - Service account permissions

3. **Network Security**
   - Network policies
   - Service mesh (mTLS)
   - Firewall rules

4. **Runtime Security**
   - AppArmor/SELinux
   - seccomp profiles
   - Runtime monitoring (Falco)

5. **Supply Chain Security**
   - Image scanning
   - Image signing
   - Admission controllers

## Performance Considerations

### API Server Optimization
- Enable API priority and fairness
- Configure request timeouts
- Use watch bookmarks
- Enable API server caching
- Distribute load across instances

### etcd Optimization
- Use fast SSDs
- Monitor fsync duration
- Regular compaction and defragmentation
- Keep datastore size manageable
- Tune snapshot policies

### Scheduler Optimization
- Adjust scoring weights
- Use scheduling profiles
- Enable feature gates selectively
- Monitor scheduling latency

### Network Optimization
- Choose appropriate CNI plugin
- Use IPVS mode for large clusters
- Enable eBPF dataplane if available
- Optimize network policies

## Observability

### Metrics
- Control plane metrics (API server, scheduler, controller manager)
- etcd metrics (latency, leader changes, DB size)
- Node metrics (kubelet, container runtime)
- Application metrics (exposed by pods)

### Logging
- Control plane logs (API server audit, controller logs)
- Node logs (kubelet, container logs)
- Application logs
- Centralized logging (EFK, Loki)

### Tracing
- API request tracing
- Distributed tracing in applications
- OpenTelemetry integration

### Health Checks
- Component health endpoints
- Leader election status
- etcd cluster health
- Node conditions

## References

- [Kubernetes Documentation - Cluster Architecture](https://kubernetes.io/docs/concepts/architecture/)
- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)
- [etcd Documentation](https://etcd.io/docs/)
- [CRI Specification](https://github.com/kubernetes/cri-api)
- [CNI Specification](https://github.com/containernetworking/cni)
