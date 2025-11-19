# Kubernetes Networking Reference

## Kubernetes Networking Model

### Core Principles

**Pod Networking**
- **Every pod has IP** - Unique IP per pod
- **Containers share IP** - Containers in pod share network namespace
- **No NAT** - Pod-to-pod communication without translation
- **Accessible from all nodes** - Network namespace isolation

**Service Abstraction**
- **Stable endpoint** - Single IP for pod set
- **Load balancing** - Distribute traffic across pods
- **Service discovery** - DNS and environment variables
- **Port mapping** - Flexible port configuration

### Network Plugins (CNI)

#### Calico
- **BGP routing** - Dynamic routing protocol
- **Network policies** - Microsegmentation
- **eBPF dataplane** - High-performance option
- **VXLAN tunneling** - Overlay networking

**Use Cases**
- Enterprise networking
- High-performance requirements
- Complex network policies
- Multi-cloud deployments

#### Cilium
- **eBPF-based** - Linux kernel technology
- **Layer 3/4/7 visibility** - Deep packet inspection
- **Service mesh integration** - Sidecar-less mesh
- **Distributed security** - Kernel-level enforcement

**Benefits**
- Ultra-low latency
- High throughput
- API-aware filtering
- Kubernetes-native

#### Flannel
- **Lightweight** - Minimal resource usage
- **Simple setup** - Easy deployment
- **VXLAN/UDP** - Tunneling options
- **CNI-standard** - Compatible with most tools

**Use Cases**
- Development/testing
- Lightweight deployments
- Small clusters
- Learning environments

#### Weave
- **Mesh networking** - Full mesh topology
- **Fast datapath** - optimized performance
- **Network policies** - Policy enforcement
- **Integration** - Works with most tools

## Service Types

### ClusterIP
- **Internal only** - No external access
- **Default type** - Internal load balancing
- **DNS accessible** - service.namespace.svc.cluster.local
- **iptables rules** - Kernel-based routing

### NodePort
- **External access** - All nodes accept traffic
- **Port mapping** - Node port to service port
- **Range** - 30000-32767 by default
- **LoadBalancer prerequisite** - Often used with external LB

### LoadBalancer
- **External IP** - Cloud provider assigns EIP
- **Auto-configuration** - Cloud provider integration
- **NodePort creation** - Underlying NodePort
- **Health checks** - Cloud provider managed

### ExternalName
- **CNAME mapping** - DNS alias to external service
- **No endpoints** - Proxy-less
- **External service access** - Direct routing
- **Use case** - Legacy service integration

## Ingress

### Ingress Architecture

**Ingress Controller**
- **Entry point** - Traffic ingestion
- **Path/host routing** - Route-based forwarding
- **TLS termination** - HTTPS offloading
- **Reverse proxy** - Request routing

**Popular Controllers**
- **NGINX Ingress** - Feature-rich, widely used
- **HAProxy** - High performance
- **Traefik** - Modern, dynamic routing
- **AWS ALB Controller** - AWS integration

### Ingress Resource

**Basic Components**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

**Advanced Features**
- Path-based routing
- Host-based routing
- TLS/SSL termination
- Header-based routing
- Rate limiting

## Network Policies

### Network Policy Basics

**Ingress Policies**
- **Pod selector** - Target pods
- **Namespace selector** - Target namespaces
- **IP blocks** - CIDR ranges
- **Port specifications** - Protocol/port

**Egress Policies**
- **Destination pods** - Egress targets
- **Namespace selectors** - Target namespaces
- **IP blocks** - CIDR ranges
- **Port specifications** - Allowed ports

### Policy Types

#### Default Deny Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

#### Deny All
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

#### Allow Specific Traffic
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      role: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8080
```

## DNS in Kubernetes

### CoreDNS

**Service DNS**
- **Service.namespace.svc.cluster.local** - Full FQDN
- **Service.namespace** - Namespace-scoped
- **Service** - Cluster local
- **FQDN resolution** - Automatic

**Configuration**
```
- Pod DNS policy: ClusterFirst, None, Default
- DNS search paths: Namespace-based
- Custom DNS: /etc/resolv.conf
- DNS caching: Configurable TTL
```

### External DNS

**Integration**
- **Kubernetes resources** - Auto-register DNS
- **Supported providers** - AWS Route53, Azure DNS, GCP DNS
- **Ingress/Service annotation** - Configuration
- **Dynamic updates** - Real-time DNS sync

**Use Cases**
- Automatic DNS registration
- Multi-cloud deployments
- Hybrid cloud integration
- Service discovery automation

## Advanced Networking

### Network Policies for Microsegmentation

**Zero-Trust Architecture**
1. Deny all by default
2. Allow explicit flows
3. Regular policy audits
4. Threat modeling
5. Least privilege access

### Pod-to-Pod Communication

**Same Node**
- Direct veth pair connection
- No encapsulation required
- Maximum throughput
- Lowest latency

**Cross-Node**
- CNI encapsulation (VXLAN, Geneve, etc.)
- Underlay or overlay network
- Performance overhead
- Encapsulation choice matters

### Egress Control

**Common Patterns**
- Database access control
- External API restrictions
- Internet access control
- By-app restrictions

## Multi-Cluster Networking

### Service Export

**ServiceExport**
- Service availability across clusters
- Namespace-scoped
- Automatic load balancing
- Multi-cluster discovery

### Multi-Cluster Ingress

**MCS (Multi-Cluster Service)**
- Cross-cluster load balancing
- Automatic failover
- Geographic distribution
- Unified service discovery

## Performance Considerations

### CNI Performance

**Throughput**
- Direct routing (5-10% overhead)
- VXLAN overlay (10-20% overhead)
- Geneve encapsulation (5-15% overhead)
- eBPF optimization (< 5% overhead)

**Latency**
- Cross-node latency: 0.5-2ms
- CNI processing: < 1ms
- Encapsulation: Minimal impact
- Network hardware: Primary factor

### Optimization Strategies
- eBPF-based CNI (Cilium)
- Direct routing in same AZ
- Hardware acceleration (DPDK)
- Network policy optimization

## Debugging & Troubleshooting

### Common Tools

**kubectl commands**
```
kubectl get pods -o wide
kubectl get svc
kubectl get networkpolicies
kubectl get ingress
kubectl logs -f pod-name
kubectl exec -it pod-name -- bash
kubectl describe node node-name
```

**Network diagnostics**
```
kubectl run -it --rm debug --image=busybox -- sh
kubectl run -it --rm debug --image=nicolaka/netshoot -- bash
```

**Packet capture**
```
tcpdump -i eth0 -w capture.pcap
kubectl debug pod-name
```

## Best Practices

### Network Architecture
- Use network policies for security
- Implement service mesh for advanced features
- Plan IP CIDR ranges carefully
- Use namespaces for isolation

### Security
- Default deny network policies
- Regular policy audits
- Encryption in transit
- RBAC integration

### Performance
- Choose appropriate CNI
- Monitor network metrics
- Optimize policy rules
- Test scalability limits

### Monitoring
- Network policy logs
- Service mesh metrics
- CNI performance metrics
- Pod network statistics

---

**Reference:** Kubernetes Networking Documentation
**Last Updated:** 2025-11-19
