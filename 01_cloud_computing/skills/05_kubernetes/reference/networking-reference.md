# Kubernetes Networking Reference

## Networking Fundamentals

### Kubernetes Network Model

**Requirements**:
1. All pods can communicate with each other without NAT
2. All nodes can communicate with all pods without NAT
3. The IP a pod sees itself as is the same IP others see it as

**Implementation**:
- Provided by CNI (Container Network Interface) plugins
- Cluster CIDR: Range for pod IPs
- Service CIDR: Range for service IPs
- No overlap between pod and service CIDRs

### IP Address Management

**Pod IPs**:
- Assigned from cluster CIDR
- Unique across cluster
- Ephemeral (change on pod restart)
- Assigned by CNI plugin

**Service IPs**:
- Assigned from service CIDR
- Virtual IPs (not assigned to any interface)
- Stable (don't change)
- Managed by kube-controller-manager

**Node IPs**:
- Assigned to node network interfaces
- Used for node-to-node communication
- Managed outside Kubernetes

## Services

### Service Types

**ClusterIP** (default):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

- Internal cluster IP
- Only accessible within cluster
- Default service type
- Use for internal microservices

**NodePort**:
```yaml
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080  # Optional, auto-assigned if not specified
```

- Exposes service on each node's IP at static port (30000-32767)
- Accessible via `<NodeIP>:<NodePort>`
- Builds on ClusterIP
- Use for simple external access or development

**LoadBalancer**:
```yaml
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

- Provisions external load balancer (cloud-specific)
- Assigns external IP
- Builds on NodePort
- Use for production external access (single service)

**ExternalName**:
```yaml
spec:
  type: ExternalName
  externalName: api.external-service.com
```

- Maps service to DNS name
- Returns CNAME record
- No proxying
- Use for external service abstraction

**Headless Service** (ClusterIP: None):
```yaml
spec:
  clusterIP: None
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
```

- No cluster IP allocated
- DNS returns pod IPs directly
- Use for StatefulSets or custom load balancing

### Service Discovery

**Environment Variables**:
```
MYSERVICE_SERVICE_HOST=10.96.0.1
MYSERVICE_SERVICE_PORT=80
```

**DNS** (recommended):
```
# Service: my-service in namespace default
my-service.default.svc.cluster.local

# Headless service pod DNS
pod-name.my-service.default.svc.cluster.local
```

**DNS Record Types**:
- **A Record**: `service-name.namespace.svc.cluster.local` → IP
- **SRV Record**: Includes port information
- **CNAME**: For ExternalName services

### Service Endpoints

**Endpoints Object**:
- Automatically created for services with selectors
- Lists pod IPs matching selector
- Updated as pods are created/destroyed

**EndpointSlice**:
- Newer, more scalable alternative to Endpoints
- Splits endpoints across multiple objects
- Better performance for large-scale services

### Session Affinity
```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

- **None** (default): Random load balancing
- **ClientIP**: Route client to same pod

### Traffic Policies

**External Traffic Policy**:
```yaml
spec:
  externalTrafficPolicy: Local  # or Cluster (default)
```

- **Cluster**: Traffic distributed across all pods
- **Local**: Traffic only to pods on receiving node
  - Preserves source IP
  - Avoids extra hop
  - Potential uneven load distribution

**Internal Traffic Policy** (Kubernetes 1.22+):
```yaml
spec:
  internalTrafficPolicy: Local  # or Cluster (default)
```

## Ingress

### Purpose
HTTP(S) routing to services based on hostnames and paths. Layer 7 load balancing.

### Ingress Example
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
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
              number: 80
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 8080
  tls:
  - hosts:
    - example.com
    secretName: example-tls
```

### Path Types
- **Exact**: Exact match
- **Prefix**: Prefix match (most common)
- **ImplementationSpecific**: Controller-specific

### Ingress Controllers

**NGINX Ingress Controller**:
- Most popular
- Feature-rich
- Good performance
- Extensive annotations

**Traefik**:
- Modern dynamic configuration
- Built-in Let's Encrypt support
- Good for service mesh
- Dashboard UI

**HAProxy Ingress**:
- High performance
- Advanced load balancing
- Good for large-scale

**Contour** (Envoy-based):
- Uses Envoy proxy
- HTTPProxy CRD
- Good integration with service mesh

**Ambassador** (Envoy-based):
- API Gateway features
- Developer-focused
- Rate limiting, auth built-in

**AWS ALB Ingress Controller**:
- Provisions AWS Application Load Balancer
- Native AWS integration
- Target groups for services

### TLS/SSL Configuration

**Certificate Secret**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: example-tls
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

**Automatic Certificate Management**:
- cert-manager: Automatic Let's Encrypt certificates
- External DNS: Automatic DNS record creation

### Ingress Annotations

**NGINX Examples**:
```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2
  nginx.ingress.kubernetes.io/ssl-redirect: "true"
  nginx.ingress.kubernetes.io/rate-limit: "100"
  nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8"
  nginx.ingress.kubernetes.io/cors-allow-origin: "*"
  nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
```

## Network Policies

### Purpose
Firewall rules for pod-to-pod and pod-to-external communication.

### Default Behavior
- Without NetworkPolicies: All traffic allowed
- With NetworkPolicies: Default deny for selected pods

### Network Policy Example
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-from-frontend
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          name: production
    - ipBlock:
        cidr: 10.0.0.0/8
        except:
        - 10.0.1.0/24
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

### Policy Types
- **Ingress**: Incoming traffic rules
- **Egress**: Outgoing traffic rules

### Selectors
- **podSelector**: Pods in same namespace
- **namespaceSelector**: Pods in matching namespaces
- **ipBlock**: CIDR ranges
- **Combination**: AND operation within item, OR across items

### Common Patterns

**Default Deny All**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**Allow from Same Namespace**:
```yaml
spec:
  ingress:
  - from:
    - podSelector: {}
```

**Allow DNS**:
```yaml
spec:
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### CNI Support
- Calico: Full support, advanced features
- Cilium: Full support, L7 policies
- Weave Net: Full support
- Flannel: No support (use Calico for policies)
- AWS VPC CNI: Via Calico integration

## DNS

### CoreDNS Architecture
- Deployed as Deployment
- ConfigMap for configuration (Corefile)
- Service for cluster DNS
- Default in Kubernetes 1.13+

### DNS Names

**Service DNS**:
```
<service>.<namespace>.svc.cluster.local
```

**Pod DNS** (when hostname/subdomain set):
```
<hostname>.<subdomain>.<namespace>.svc.cluster.local
```

**Pod DNS (default)**:
```
<pod-ip-with-dashes>.<namespace>.pod.cluster.local
```

### Corefile Configuration
```
.:53 {
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
    forward . /etc/resolv.conf
    cache 30
    loop
    reload
    loadbalance
}
```

### Custom DNS Configuration

**Pod DNS Config**:
```yaml
spec:
  dnsPolicy: "None"
  dnsConfig:
    nameservers:
    - 1.1.1.1
    searches:
    - my.dns.search.suffix
    options:
    - name: ndots
      value: "2"
```

**DNS Policies**:
- **Default**: Inherit from node
- **ClusterFirst**: Use cluster DNS (default for most pods)
- **ClusterFirstWithHostNet**: For pods with hostNetwork
- **None**: Use dnsConfig only

### External DNS
- Syncs Kubernetes services/ingresses to external DNS providers
- Supports: AWS Route53, Google Cloud DNS, Azure DNS, Cloudflare, etc.
- Automatic DNS record creation/deletion

## CNI Plugins

### Calico

**Features**:
- L3 networking with BGP
- Network policies (L3/L4 and L7 with Envoy)
- Both overlay (VXLAN, IPIP) and non-overlay
- eBPF dataplane option
- Enterprise: Egress gateway, WireGuard encryption

**Best For**:
- Large-scale deployments
- Advanced network policies
- Performance-critical workloads

### Cilium

**Features**:
- eBPF-based networking and security
- L7 network policies
- Identity-based security
- Hubble observability
- Service mesh features
- Cluster mesh for multi-cluster

**Best For**:
- Modern kernel environments
- Advanced security requirements
- Multi-cluster networking
- L7 visibility

### Flannel

**Features**:
- Simple overlay network
- Multiple backend options (VXLAN, host-gw, UDP)
- Easy to deploy
- No network policy support (use with Calico)

**Best For**:
- Simple environments
- Getting started
- Non-production workloads

### Weave Net

**Features**:
- Automatic mesh network
- Encryption support
- Network policies
- Multicast support

**Best For**:
- Easy setup
- Encryption requirements

### AWS VPC CNI

**Features**:
- Native VPC networking
- Each pod gets VPC IP
- Security group support for pods
- Prefix delegation for IP efficiency

**Best For**:
- EKS clusters
- AWS-native networking
- Security group requirements

### Azure CNI

**Features**:
- Native Azure VNet networking
- Pods get VNet IPs
- Integration with Azure network policies

**Best For**:
- AKS clusters
- Azure-native environments

### GKE Network Plugin

**Features**:
- Native VPC networking
- Alias IP ranges
- IP masquerading
- Network policy support

**Best For**:
- GKE clusters
- GCP-native environments

## Service Mesh

### Istio

**Components**:
- Istiod: Control plane
- Envoy: Data plane (sidecar proxy)
- Ingress/Egress gateways

**Features**:
- Traffic management (routing, retries, timeouts)
- Security (mTLS, authorization policies)
- Observability (metrics, logs, traces)
- Multi-cluster support

### Linkerd

**Components**:
- Control plane (controller, web, prometheus)
- Data plane (linkerd2-proxy sidecar)

**Features**:
- Automatic mTLS
- Service profiles for traffic splitting
- Lightweight and fast
- Simple to operate

### Consul Connect

**Features**:
- Service mesh with service discovery
- Intentions-based security
- Multi-datacenter support
- Consul catalog integration

## Load Balancing

### Internal Load Balancing
- kube-proxy: iptables/IPVS
- Service mesh: Envoy, Linkerd proxy
- Client-side: Application-level

### External Load Balancing
- Cloud provider load balancers
- Ingress controllers
- Service mesh gateways
- MetalLB (bare metal)

### Load Balancing Algorithms

**kube-proxy iptables**: Random selection
**kube-proxy IPVS**:
- Round Robin (default)
- Least Connection
- Destination Hashing
- Source Hashing
- Shortest Expected Delay
- Never Queue

## References

- [Kubernetes Networking Model](https://kubernetes.io/docs/concepts/cluster-administration/networking/)
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
