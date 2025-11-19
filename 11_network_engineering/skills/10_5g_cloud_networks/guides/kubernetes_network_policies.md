# Kubernetes Network Policies Guide

## Network Policy Fundamentals

### Default Deny Approach

**Principle:** Deny all traffic by default, then explicitly allow required flows.

```yaml
# Default deny all ingress
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
# Default deny all egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
```

## Step 1: Frontend Service Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: frontend
      tier: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
      podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
  - from:
    - podSelector:
        matchLabels:
          app: prometheus
          namespace: monitoring
    ports:
    - protocol: TCP
      port: 9090
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: frontend
      tier: web
  policyTypes:
  - Egress
  egress:
  # Allow to API backend
  - to:
    - podSelector:
        matchLabels:
          app: api
          tier: backend
    ports:
    - protocol: TCP
      port: 8080
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # Allow external HTTP/HTTPS
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32  # Block metadata service
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
```

## Step 2: Backend Service Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
      tier: backend
  policyTypes:
  - Ingress
  ingress:
  # From frontend
  - from:
    - podSelector:
        matchLabels:
          app: frontend
          tier: web
    ports:
    - protocol: TCP
      port: 8080
  # From service mesh
  - from:
    - namespaceSelector:
        matchLabels:
          name: istio-system
    - podSelector:
        matchLabels:
          app: istio-proxy
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8443
  # Liveness/readiness probes
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8090
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
      tier: backend
  policyTypes:
  - Egress
  egress:
  # To database
  - to:
    - podSelector:
        matchLabels:
          app: postgres
          tier: database
    ports:
    - protocol: TCP
      port: 5432
  # To cache
  - to:
    - podSelector:
        matchLabels:
          app: redis
          tier: cache
    ports:
    - protocol: TCP
      port: 6379
  # DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # External services
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 169.254.169.254/32
    ports:
    - protocol: TCP
      port: 443
```

## Step 3: Database Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-database-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
      tier: database
  policyTypes:
  - Ingress
  ingress:
  # From backend only
  - from:
    - podSelector:
        matchLabels:
          app: api
          tier: backend
    ports:
    - protocol: TCP
      port: 5432
  # From backup/restore job
  - from:
    - podSelector:
        matchLabels:
          job-type: db-backup
    - namespaceSelector:
        matchLabels:
          name: backup-system
    ports:
    - protocol: TCP
      port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-database-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
      tier: database
  policyTypes:
  - Egress
  egress:
  # DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
  # Allow internal traffic for replication
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

## Step 4: Cross-Namespace Communication

```yaml
# Allow monitoring namespace to scrape metrics
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-prometheus-scrape
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090
```

## Step 5: Deny External Egress Except Whitelist

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-external-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  # Allow specific external IPs (API servers, etc.)
  - to:
    - ipBlock:
        cidr: 203.0.113.0/24
    ports:
    - protocol: TCP
      port: 443
  # Allow kube-system for upgrades/patches
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 443
```

## Step 6: Egress Firewall / Cluster Egress

```yaml
# Calico NetworkPolicy for cluster-wide egress control
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: restrict-external-ips
spec:
  selector: all()
  types:
  - Egress
  egress:
  - action: Allow
    destination:
      nets:
      - 10.0.0.0/8  # Internal networks
      - 172.16.0.0/12
      - 192.168.0.0/16
  - action: Allow
    destination:
      selector: "k8s-app == kube-dns"
    protocol: UDP
    ports:
    - 53
  - action: Allow
    destination:
      nets:
      - 0.0.0.0/0
    ports:
    - 443
      protocol: TCP
  - action: Deny
    destination:
      nets:
      - 0.0.0.0/0
```

## Step 7: Testing Network Policies

### Verification Commands

```bash
# List all network policies
kubectl get networkpolicies -n production

# Describe specific policy
kubectl describe np allow-backend-ingress -n production

# Check policy details
kubectl get np allow-backend-ingress -n production -o yaml

# Test connectivity within pod
kubectl exec -it api-pod-1 -- curl http://postgres:5432

# Debug with network diagnostic pod
kubectl run -it --rm netshoot \
  --image=nicolaka/netshoot:latest \
  --overrides='{"spec":{"serviceAccount":"debug-sa"}}' \
  -- bash
```

### Test Scenarios

```bash
# Test frontend to backend (should work)
kubectl exec -it frontend-pod-1 -n production -- \
  curl http://api.production.svc.cluster.local:8080

# Test frontend to database (should fail)
kubectl exec -it frontend-pod-1 -n production -- \
  curl postgres.production.svc.cluster.local:5432

# Test external DNS resolution
kubectl exec -it api-pod-1 -n production -- \
  nslookup google.com

# Test external HTTPS access
kubectl exec -it api-pod-1 -n production -- \
  curl https://api.github.com
```

## Step 8: Policy Audit & Logging

### Enable Policy Audit Logging (Calico)

```yaml
apiVersion: projectcalico.org/v3
kind: FelixConfiguration
metadata:
  name: default
spec:
  logFilePath: /var/log/calico/policy.log
  loggingLevel: Debug
  policyAuditLogging: Enabled
```

### Analyze Policy Violations

```bash
# View policy logs from node
kubectl node-shell <node-name>
tail -f /var/log/calico/policy.log

# Parse denied connections
grep "DENIED" /var/log/calico/policy.log | \
  jq -R 'split("|")[0,1,2,3,4,5]'
```

## Step 9: Application Service Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-communication
  namespace: production
spec:
  podSelector:
    matchLabels:
      component: app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow from load balancer
  - from:
    - podSelector:
        matchLabels:
          component: load-balancer
    ports:
    - protocol: TCP
      port: 8080
  # Allow health checks
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8090
  egress:
  # Service-to-service discovery
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  # Allow internal pod-to-pod
  - to:
    - podSelector:
        matchLabels:
          network-zone: internal
  # Allow external APIs
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 443
```

## Best Practices

1. **Start Restrictive** - Begin with default-deny, then add allows
2. **Use Labels** - Consistent labeling for policy selection
3. **Document Flows** - Maintain diagram of allowed traffic
4. **Test Thoroughly** - Verify policies before production
5. **Monitor Violations** - Enable and review audit logs
6. **Version Control** - Track policy changes in Git
7. **Regular Review** - Quarterly policy audits
8. **Separate Concerns** - One policy per service
9. **Use Namespaces** - Isolate workloads by namespace
10. **Multi-tool Approach** - Consider service mesh for advanced features

---

**Last Updated:** 2025-11-19
