# CKA, CKAD, and CKS Certification Topics

## Overview

This document covers topics for the three main Kubernetes certifications offered by the Linux Foundation and CNCF.

## Exam Information

| Certification | Duration | Passing Score | Exam Format | Cost |
|---------------|----------|---------------|-------------|------|
| CKA (Certified Kubernetes Administrator) | 2 hours | 66% | Performance-based | $395 |
| CKAD (Certified Kubernetes Application Developer) | 2 hours | 66% | Performance-based | $395 |
| CKS (Certified Kubernetes Security Specialist) | 2 hours | 67% | Performance-based | $395 |

**Prerequisites**:
- CKA: None
- CKAD: None
- CKS: Must have valid CKA certification

**Environment**:
- Remote proctored
- Single terminal with kubectl, helm, and other tools
- Kubernetes documentation allowed
- No other external resources

## CKA (Certified Kubernetes Administrator)

### Domains and Weights

1. **Storage** (10%)
2. **Troubleshooting** (30%)
3. **Workloads & Scheduling** (15%)
4. **Cluster Architecture, Installation & Configuration** (25%)
5. **Services & Networking** (20%)

### 1. Storage (10%)

**Topics**:
- Understand storage classes, persistent volumes
- Understand volume mode, access modes and reclaim policies for volumes
- Understand persistent volume claims primitive
- Know how to configure applications with persistent storage

**Key Skills**:
```bash
# Create PV
kubectl apply -f pv.yaml

# Create PVC
kubectl apply -f pvc.yaml

# Use PVC in pod
kubectl apply -f pod-with-pvc.yaml

# Create StorageClass
kubectl apply -f storageclass.yaml

# Expand PVC
kubectl edit pvc my-pvc  # Change size in spec.resources.requests.storage
```

### 2. Troubleshooting (30%)

**Topics**:
- Evaluate cluster and node logging
- Understand how to monitor applications
- Manage container stdout & stderr logs
- Troubleshoot application failure
- Troubleshoot cluster component failure
- Troubleshoot networking

**Key Skills**:
```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Check pod logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c <container-name>
kubectl logs <pod-name> --previous

# Check events
kubectl get events --sort-by='.lastTimestamp'
kubectl get events -n kube-system

# Cluster component logs
sudo journalctl -u kubelet
sudo journalctl -u docker

# Network troubleshooting
kubectl run test --image=busybox -it --rm -- sh
kubectl exec -it <pod> -- nslookup kubernetes.default

# Component health
kubectl get componentstatuses
kubectl get --raw /healthz?verbose
```

### 3. Workloads & Scheduling (15%)

**Topics**:
- Understand deployments and how to perform rolling update and rollbacks
- Use ConfigMaps and Secrets to configure applications
- Know how to scale applications
- Understand the primitives used to create robust, self-healing, application deployments
- Understand how resource limits can affect Pod scheduling
- Awareness of manifest management and common templating tools

**Key Skills**:
```bash
# Create deployment
kubectl create deployment nginx --image=nginx:1.21

# Scale deployment
kubectl scale deployment nginx --replicas=5

# Update image
kubectl set image deployment/nginx nginx=nginx:1.22

# Rollout status
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx

# ConfigMap/Secret
kubectl create configmap app-config --from-literal=key=value
kubectl create secret generic app-secret --from-literal=password=secret

# Resource limits
kubectl set resources deployment nginx --limits=cpu=200m,memory=512Mi --requests=cpu=100m,memory=256Mi
```

### 4. Cluster Architecture, Installation & Configuration (25%)

**Topics**:
- Manage role based access control (RBAC)
- Use Kubeadm to install a basic cluster
- Manage a highly-available Kubernetes cluster
- Provision underlying infrastructure to deploy a Kubernetes cluster
- Perform a version upgrade on a Kubernetes cluster using Kubeadm
- Implement etcd backup and restore

**Key Skills**:
```bash
# RBAC
kubectl create role pod-reader --verb=get,list,watch --resource=pods
kubectl create rolebinding read-pods --role=pod-reader --user=jane
kubectl create clusterrole secret-reader --verb=get,list --resource=secrets
kubectl create clusterrolebinding read-secrets --clusterrole=secret-reader --user=dave

# Cluster upgrade
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.28.0
sudo apt-get update && sudo apt-get install -y kubelet=1.28.0-00 kubectl=1.28.0-00
sudo systemctl daemon-reload && sudo systemctl restart kubelet

# etcd backup
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# etcd restore
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db \
  --data-dir=/var/lib/etcd-restore
```

### 5. Services & Networking (20%)

**Topics**:
- Understand host networking configuration on the cluster nodes
- Understand connectivity between Pods
- Understand ClusterIP, NodePort, LoadBalancer service types and endpoints
- Know how to use Ingress controllers and Ingress resources
- Know how to configure and use CoreDNS
- Choose an appropriate container network interface plugin

**Key Skills**:
```bash
# Create service
kubectl expose deployment nginx --port=80 --target-port=8080
kubectl create service clusterip my-svc --tcp=80:8080
kubectl create service nodeport my-svc --tcp=80:8080 --node-port=30080

# Ingress
kubectl create ingress my-ingress --rule="host.com/path*=svc:port"

# DNS troubleshooting
kubectl run busybox --image=busybox:1.28 --rm -it -- nslookup kubernetes.default
kubectl exec -it busybox -- cat /etc/resolv.conf

# Network policy
kubectl apply -f networkpolicy.yaml
kubectl get networkpolicy
```

## CKAD (Certified Kubernetes Application Developer)

### Domains and Weights

1. **Application Design and Build** (20%)
2. **Application Deployment** (20%)
3. **Application Observability and Maintenance** (15%)
4. **Application Environment, Configuration and Security** (25%)
5. **Services and Networking** (20%)

### 1. Application Design and Build (20%)

**Topics**:
- Define, build and modify container images
- Understand Jobs and CronJobs
- Understand multi-container Pod design patterns (e.g. sidecar, init containers)
- Utilize persistent and ephemeral volumes

**Key Skills**:
```bash
# Create Dockerfile
cat > Dockerfile <<EOF
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "app.js"]
EOF

# Build and push
docker build -t myapp:v1 .
docker push myapp:v1

# Job
kubectl create job pi --image=perl:5.34 -- perl -Mbignum=bpi -wle 'print bpi(2000)'

# CronJob
kubectl create cronjob backup --image=backup:latest --schedule="0 2 * * *" -- /backup.sh

# Init containers
# Multi-container pod with sidecar
```

### 2. Application Deployment (20%)

**Topics**:
- Use Kubernetes primitives to implement common deployment strategies
- Understand Deployments and how to perform rolling updates
- Use the Helm package manager to deploy existing packages

**Key Skills**:
```bash
# Deployment strategies
kubectl apply -f deployment.yaml
kubectl set image deployment/myapp myapp=myapp:v2
kubectl rollout status deployment/myapp
kubectl rollout undo deployment/myapp

# Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-release bitnami/nginx
helm upgrade my-release bitnami/nginx
helm rollback my-release 1
helm uninstall my-release
```

### 3. Application Observability and Maintenance (15%)

**Topics**:
- Understand API deprecations
- Implement probes and health checks
- Use provided tools to monitor Kubernetes applications
- Utilize container logs
- Debugging in Kubernetes

**Key Skills**:
```bash
# Probes
kubectl set probe deployment/myapp --readiness --get-url=http://:8080/health
kubectl set probe deployment/myapp --liveness --get-url=http://:8080/health --initial-delay-seconds=30

# Logs
kubectl logs myapp-pod
kubectl logs myapp-pod -f
kubectl logs myapp-pod --previous
kubectl logs myapp-pod -c sidecar

# Debug
kubectl describe pod myapp-pod
kubectl get events
kubectl exec -it myapp-pod -- sh
kubectl debug myapp-pod -it --image=busybox
```

### 4. Application Environment, Configuration and Security (25%)

**Topics**:
- Discover and use resources that extend Kubernetes (CRD)
- Understand authentication, authorization and admission control
- Understanding and defining resource requirements, limits and quotas
- Understand ConfigMaps
- Create & consume Secrets
- Understand ServiceAccounts
- Understand SecurityContexts

**Key Skills**:
```bash
# ConfigMap
kubectl create configmap app-config --from-file=config.yaml
kubectl create configmap app-config --from-literal=DB_HOST=mysql

# Secrets
kubectl create secret generic db-secret --from-literal=password=secret
kubectl create secret tls tls-secret --cert=cert.pem --key=key.pem

# ServiceAccount
kubectl create serviceaccount myapp-sa

# ResourceQuota
kubectl create quota dev-quota --hard=pods=10,requests.cpu=4,requests.memory=8Gi

# SecurityContext
# Applied in pod spec
```

### 5. Services and Networking (20%)

**Topics**:
- Demonstrate basic understanding of NetworkPolicies
- Provide and troubleshoot access to applications via services
- Use Ingress rules to expose applications

**Key Skills**:
```bash
# Services
kubectl expose deployment myapp --port=80 --target-port=8080 --type=ClusterIP
kubectl create service nodeport myapp --tcp=80:8080

# Ingress
kubectl create ingress myapp --rule="myapp.com/=myapp:80"
kubectl create ingress myapp --class=nginx --rule="myapp.com/api=myapp:80"

# NetworkPolicy
kubectl apply -f networkpolicy.yaml
kubectl label namespace default app=myapp  # For namespace selector
```

## CKS (Certified Kubernetes Security Specialist)

### Domains and Weights

1. **Cluster Setup** (10%)
2. **Cluster Hardening** (15%)
3. **System Hardening** (15%)
4. **Minimize Microservice Vulnerabilities** (20%)
5. **Supply Chain Security** (20%)
6. **Monitoring, Logging and Runtime Security** (20%)

### 1. Cluster Setup (10%)

**Topics**:
- Use Network security policies to restrict cluster level access
- Use CIS benchmark to review the security configuration of Kubernetes components (etcd, kubelet, kubedns, kubeapi)
- Properly set up Ingress objects with security control
- Protect node metadata and endpoints
- Minimize use of, and access to, GUI elements
- Verify platform binaries before deploying

**Key Skills**:
```bash
# CIS benchmark
kube-bench run --targets master,node

# Network policies
kubectl apply -f deny-all-network-policy.yaml

# Verify binaries
sha512sum kubectl
```

### 2. Cluster Hardening (15%)

**Topics**:
- Restrict access to Kubernetes API
- Use Role Based Access Controls to minimize exposure
- Exercise caution in using service accounts (e.g. disable defaults, minimize permissions on newly created ones)
- Update Kubernetes frequently

**Key Skills**:
```bash
# RBAC
kubectl create role pod-reader --verb=get,list --resource=pods
kubectl create rolebinding read-pods --role=pod-reader --serviceaccount=default:myapp

# Disable default service account automount
kubectl patch serviceaccount default -p '{"automountServiceAccountToken":false}'

# Upgrade cluster
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v1.28.0
```

### 3. System Hardening (15%)

**Topics**:
- Minimize host OS footprint (reduce attack surface)
- Minimize IAM roles
- Minimize external access to the network
- Appropriately use kernel hardening tools such as AppArmor, seccomp

**Key Skills**:
```bash
# AppArmor
sudo apparmor_parser -r /etc/apparmor.d/docker

# In pod spec:
# annotations:
#   container.apparmor.security.beta.kubernetes.io/app: localhost/k8s-apparmor

# Seccomp
# securityContext:
#   seccompProfile:
#     type: RuntimeDefault

# System hardening
sudo systemctl list-units --type=service --state=running
sudo systemctl disable <unnecessary-service>
```

### 4. Minimize Microservice Vulnerabilities (20%)

**Topics**:
- Setup appropriate OS level security domains
- Manage Kubernetes secrets
- Use container runtime sandboxes in multi-tenant environments (e.g. gvisor, kata containers)
- Implement pod to pod encryption by use of mTLS

**Key Skills**:
```bash
# Pod Security Standards
kubectl label namespace default pod-security.kubernetes.io/enforce=restricted

# SecurityContext
# In pod spec:
# securityContext:
#   runAsNonRoot: true
#   runAsUser: 1000
#   capabilities:
#     drop: ["ALL"]
#   readOnlyRootFilesystem: true

# Secrets
kubectl create secret generic db-creds --from-literal=password=secret
# Mount as volume, not env var

# gVisor runtime class
kubectl apply -f runtimeclass-gvisor.yaml
# Use in pod: runtimeClassName: gvisor
```

### 5. Supply Chain Security (20%)

**Topics**:
- Minimize base image footprint
- Secure your supply chain: whitelist allowed registries, sign and validate images
- Use static analysis of user workloads (e.g. Kubernetes resources, Docker files)
- Scan images for known vulnerabilities

**Key Skills**:
```bash
# Image scanning
trivy image myapp:latest
trivy image --severity HIGH,CRITICAL myapp:latest

# Image signing (Cosign)
cosign sign --key cosign.key myapp:latest
cosign verify --key cosign.pub myapp:latest

# Admission controller
kubectl apply -f imagepolicywebhook.yaml

# Static analysis
kubesec scan pod.yaml
kubeval deployment.yaml
```

### 6. Monitoring, Logging and Runtime Security (20%)

**Topics**:
- Perform behavioral analytics of syscall process and file activities at the host and container level to detect malicious activities
- Detect threats within physical infrastructure, apps, networks, data, users and workloads
- Detect all phases of attack regardless where it occurs and how it spreads
- Perform deep analytical investigation and identification of bad actors within environment
- Ensure immutability of containers at runtime
- Use Audit Logs to monitor access

**Key Skills**:
```bash
# Falco
sudo systemctl start falco
sudo tail -f /var/log/falco/falco.log

# Audit logs
# API server flag:
# --audit-log-path=/var/log/kubernetes/audit.log
# --audit-policy-file=/etc/kubernetes/audit-policy.yaml

cat /var/log/kubernetes/audit.log | grep "verb\":\"delete"

# Read-only filesystem
# securityContext:
#   readOnlyRootFilesystem: true

# Immutable infrastructure
kubectl set image deployment/myapp myapp=myapp:v2  # Don't patch running containers
```

## Exam Tips

### General
- Practice with `kubectl` extensively
- Learn to use `kubectl explain`
- Master imperative commands for speed
- Use aliases: `alias k=kubectl`
- Bookmark important docs pages
- Practice time management (2 hours, ~15-20 questions)

### kubectl Tips
```bash
# Imperative commands
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
kubectl create deployment nginx --image=nginx --replicas=3 --dry-run=client -o yaml > deployment.yaml
kubectl expose deployment nginx --port=80 --target-port=8080 --dry-run=client -o yaml > service.yaml

# Useful commands
kubectl explain pod.spec.containers
kubectl api-resources
kubectl api-versions
kubectl get events --sort-by='.lastTimestamp'

# Quick edits
kubectl edit deployment nginx
kubectl patch deployment nginx -p '{"spec":{"replicas":5}}'
kubectl set image deployment/nginx nginx=nginx:1.22
```

### Time-Saving Aliases
```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kgd='kubectl get deployments'
alias kgs='kubectl get services'
alias kd='kubectl describe'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias ke='kubectl exec -it'
export do='--dry-run=client -o yaml'
export now='--force --grace-period=0'
```

### Documentation Bookmarks
- kubectl Cheat Sheet
- Pod Security Standards
- Network Policies
- RBAC
- Service types
- Persistent Volumes
- ConfigMaps and Secrets

## Practice Resources

- [Killer.sh](https://killer.sh) - Exam simulator (included with exam purchase)
- [KodeKloud](https://kodekloud.com) - Practice labs
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- Practice on your own cluster with kubeadm
- GitHub repos with practice questions

## References

- [CKA Exam Curriculum](https://github.com/cncf/curriculum/blob/master/CKA_Curriculum_v1.28.pdf)
- [CKAD Exam Curriculum](https://github.com/cncf/curriculum/blob/master/CKAD_Curriculum_v1.28.pdf)
- [CKS Exam Curriculum](https://github.com/cncf/curriculum/blob/master/CKS_Curriculum_v1.28.pdf)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
