# Cloud-Native Networking Reference

## Cloud-Native Architecture Principles

Cloud-native networking supports containerized, microservices-based applications with dynamic scaling, self-healing, and rapid deployment capabilities.

## Container Networking Fundamentals

### Container Runtime Integration

#### Docker Networking
- **Bridge mode** - Default, isolated network
- **Host mode** - Direct host network access
- **Overlay mode** - Multi-host networking
- **None mode** - No networking

**Use Cases**
- Development environments
- Small deployments
- Non-production workloads

#### Container Network Interface (CNI)
- **Plugin architecture** - Flexible network plugins
- **Standard specification** - Kubernetes standard
- **Third-party plugins** - Calico, Cilium, etc.
- **Custom implementations** - Organization-specific

### Network Abstractions

#### Container-to-Container
- **Pod network** - Shared network namespace
- **Port mapping** - Container port exposure
- **DNS resolution** - Service discovery
- **Network policies** - Traffic control

#### Container-to-Host
- **Host networking** - Direct host access
- **Port forwarding** - External access
- **Host firewall** - Host-level rules
- **Resource isolation** - Network bandwidth limiting

## Overlay vs Underlay Networks

### Overlay Networks
- **Encapsulation** - VXLAN, Geneve, etc.
- **Performance overhead** - 5-20% latency
- **Flexibility** - Works on any infrastructure
- **Multi-cloud friendly** - Cloud-agnostic

**Technologies**
- VXLAN (Virtual Extensible LAN)
- Geneve (Generic Network Virtualization Encapsulation)
- Weave tunneling
- Flannel backend

### Underlay Networks
- **Direct routing** - No encapsulation
- **Optimal performance** - Minimal overhead
- **Infrastructure dependent** - Hardware requirements
- **Simpler troubleshooting** - Direct packet inspection

**Implementation**
- BGP routing (Calico)
- Route distribution
- Physical network integration
- Layer 3 fabric

### Hybrid Approach
- Same-rack: Direct routing
- Cross-rack: Encapsulation
- Performance optimization
- Dynamic selection

## Service Discovery

### DNS-Based Discovery

**Kubernetes DNS**
- **Service FQDN** - service.namespace.svc.cluster.local
- **Headless services** - Direct pod DNS
- **StatefulSet DNS** - Predictable pod DNS
- **External DNS** - External system integration

**Implementation**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: MyApp
  type: ClusterIP
  clusterIP: None  # Headless service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9376
```

### API-Based Discovery
- **Kubernetes API** - Service and endpoint queries
- **Custom endpoints** - External service registration
- **Reconciliation** - Continuous sync
- **Event-driven** - Updates on changes

## Load Balancing

### Layer 4 Load Balancing
- **Connection level** - TCP/UDP
- **Network Load Balancer** - AWS NLB
- **Ultra-high throughput** - Millions of connections
- **Latency-sensitive** - Optimal for gaming, streaming

### Layer 7 Load Balancing
- **Application level** - HTTP, gRPC
- **Application Load Balancer** - AWS ALB
- **Content-based routing** - Path, hostname
- **Request enrichment** - Header modification

### Client-Side Load Balancing
- **Application responsibility** - Logic in client
- **gRPC load balancing** - Round-robin, pick-first
- **Service mesh** - Proxy-based LB
- **Kubernetes services** - kube-proxy iptables

## Container Networking Patterns

### Sidecar Pattern
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-logging
spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080
  - name: logging-sidecar
    image: logging:1.0
    volumeMounts:
    - name: shared-logs
      mountPath: /logs
  volumes:
  - name: shared-logs
    emptyDir: {}
```

**Use Cases**
- Log collection
- Metric collection
- Service mesh proxies
- Traffic encryption

### Ambassador Pattern
- Dedicated proxy container
- Protocol translation
- Request enrichment
- External resource access

### Adapter Pattern
- Data normalization
- Format conversion
- Legacy system integration
- Monitoring adaptation

## Network Policies Deep Dive

### Policy Enforcement Levels

**Pod-to-Pod**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pod-isolation
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector: {}
      namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
```

**Namespace-Level Policies**
- Cross-namespace rules
- Namespace isolation
- External network access
- Egress filtering

## DNS and Service Discovery

### CoreDNS Configuration

**Plugin Architecture**
```
. {
    errors
    health {
      lameduck 5s
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
      pods insecure
      fallthrough in-addr.arpa ip6.arpa
      ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf {
      max_concurrent 1000
    }
    cache 30
    loop
    reload
    loadbalance
}
```

**Custom DNS**
- Private zones
- Split-brain DNS
- External DNS integration
- Conditional forwarding

### Service Discovery Patterns

**Internal Services**
- Kubernetes service discovery
- DNS round-robin
- Service mesh discovery
- Endpoint reconciliation

**External Services**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: db.example.com
  ports:
  - port: 5432
```

## Multi-Cluster Networking

### Service Exposure
- Federation of services
- Cross-cluster communication
- Geographic distribution
- Automatic failover

### Network Topology
- Hub-and-spoke
- Full mesh
- Hierarchical
- Optimized paths

### Traffic Routing
- Global load balancing
- Latency-based routing
- Geo-location routing
- Active-active failover

## Egress and Ingress

### Ingress Patterns

**Single Ingress Controller**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-service
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1
            port:
              number: 8080
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2
            port:
              number: 8080
```

**Multi-Controller Setup**
- Shared Ingress resources
- Controller-specific classes
- Different entry points
- Advanced routing

### Egress Control

**Internet Egress**
- NAT gateway
- Proxy servers
- Cloud NAT
- Firewall rules

**Database Egress**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-db
spec:
  podSelector:
    matchLabels:
      tier: app
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 10.1.0.0/16
    ports:
    - protocol: TCP
      port: 5432
```

## Performance Optimization

### Reducing Latency
- Minimize encapsulation (underlay networks)
- Optimize path selection
- Connection pooling
- Keep-alive configuration

### Throughput Optimization
- Jumbo frames (MTU 9000)
- NUMA awareness
- CPU pinning
- SR-IOV for bypass

### Resource Efficiency
- Stateless connections
- Graceful degradation
- Horizontal scaling
- Auto-scaling policies

## Observability in Cloud-Native Networking

### Metrics Collection
- Packet drop rates
- Latency percentiles
- Bandwidth utilization
- Connection states

### Distributed Tracing
- Request flow tracking
- Latency breakdown
- Service dependencies
- Error attribution

### Network Logging
- Flow logs
- Connection logs
- Policy violation logs
- Audit trails

## Troubleshooting Tools

**Kubernetes Native**
```bash
kubectl describe service/pod
kubectl get networkpolicies
kubectl logs pod-name -c container-name
kubectl exec -it pod-name -- bash
```

**Network Tools**
```bash
tcpdump, wireshark - Packet capture
netstat/ss - Connection statistics
ping, traceroute - Connectivity verification
iptables, nftables - Firewall rules
```

**Service Mesh Tools**
```bash
istioctl analyze
linkerd diagnose
linkerd tap
linkerd stat
```

## Best Practices Summary

1. **Network Policy First** - Implement security early
2. **Observability** - Monitor all traffic
3. **Performance Testing** - Baseline and optimize
4. **Scalability** - Plan for growth
5. **Documentation** - Maintain architecture docs
6. **Automation** - IaC and GitOps
7. **Security** - Least privilege access

---

**Reference:** Kubernetes Networking Documentation, Cloud Native Computing Foundation
**Last Updated:** 2025-11-19
