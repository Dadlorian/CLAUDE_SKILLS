# Kubernetes v1.30 Release Notes

**Release Date:** April 17, 2024

## Table of Contents

- [Urgent Upgrade Notes](#urgent-upgrade-notes)
- [What's New](#whats-new)
- [Major Themes](#major-themes)
- [API Changes](#api-changes)
- [Deprecations and Removals](#deprecations-and-removals)
- [Known Issues](#known-issues)
- [Known Bugs and Issues](#known-bugs-and-issues)
- [Command Line Tool (kubectl) Changes](#command-line-tool-kubectl-changes)
- [Metrics Changes](#metrics-changes)

## Urgent Upgrade Notes

### API Server Binary Size

The API server binary size has increased significantly in v1.30 due to expanded feature support. Ensure adequate disk space during upgrades (minimum 2GB available).

### etcd Compatibility

This release requires etcd v3.5.1 or newer. Verify your etcd version before upgrading:
```bash
etcdctl version
```

### CoreDNS Upgrade

CoreDNS has been updated to v1.11.1. No manual intervention required, but custom CoreDNS configuration may need review.

---

## What's New

### Kubernetes Control Plane and Node Features

#### Beta Features

**Structured Logging** [#119140](https://github.com/kubernetes/kubernetes/pull/119140)
- Control plane components now emit structured logs in JSON format
- Enables better log aggregation and monitoring
- Alpha for kubelet; beta for apiserver
- Enable with: `--logging-format=json`

**CEL for Admission Control** [#121933](https://github.com/kubernetes/kubernetes/pull/121933)
- Common Expression Language (CEL) for ValidatingAdmissionPolicy rules
- More flexible than previous webhook-only approach
- Improved performance and development experience

**Native Sidecar Containers** [#116429](https://github.com/kubernetes/kubernetes/pull/116429)
- Containers defined in `initContainers` with `restartPolicy: Always`
- Improved lifecycle management for sidecar patterns
- Graduation to beta; enables native container ordering

**User Namespaces** [#127793](https://github.com/kubernetes/kubernetes/pull/127793)
- Enhanced security via user namespace isolation
- Available for Pod containers
- Requires runtime support (containerd, CRI-O)

#### Alpha Features

**Workload Isolation with Pod Scheduling Profiles** [#121294](https://github.com/kubernetes/kubernetes/pull/121294)
- New scheduling profile types for workload isolation
- Improves multi-tenant cluster security

**Device Plugins with DRA** [#120827](https://github.com/kubernetes/kubernetes/pull/120827)
- Dynamic Resource Allocation (DRA) improvements
- Better GPU and accelerator management

**Container CPU Throttling Metrics** [#121349](https://github.com/kubernetes/kubernetes/pull/121349)
- New metrics for CPU throttling observation
- Helps identify performance bottlenecks

### API Version Changes

#### v1 Stable (GA)

- **WindowsHostProcessPod**: Pod containers can now run as Hyper-V isolated containers on Windows
- **MatchConditions**: CustomResourceDefinition webhook conditions for fine-grained filtering
- **PodHealthPolicy**: For pod disruption budgets with health checks

#### v1beta1

- **ValidationRules**: For CustomResourceDefinition validation
- **Authorizer**: For webhook authorizer improvements

### Security Enhancements

**TLS 1.2 Minimum**
- All Kubernetes components now enforce TLS 1.2 minimum
- TLS 1.0 and 1.1 support removed

**Audit Event Format**
- New audit event types for `create`, `update`, `patch`, `delete` operations
- Improved security event tracking

**Service Account Token Improvements**
- Token bound to specific nodes (NodeName field)
- Enhanced security for multi-node clusters

### Node Features

**KubeletPodResources v1**
- Provides pod resource information to external components
- Improved resource visibility

**Container Runtime Metrics**
- Enhanced metrics for CPU usage, memory, and disk I/O
- Better monitoring capabilities

### Network Features

**Network Policy Improvements** [#114606](https://github.com/kubernetes/kubernetes/pull/114606)
- Support for FQDN-based network policies (beta)
- Enhanced network policy validation

**IPv4/IPv6 Dual Stack**
- Improved handling of dual-stack services
- Better IPv6 support throughout

---

## Major Themes

### Security

1. **Enhanced RBAC Validation**
   - Stricter validation of role binding subjects
   - Better separation of concerns
   - Enhanced audit logging

2. **Improved Pod Security**
   - Pod Security Standards now mandatory in many distributions
   - Better defaults for restricted/baseline/unrestricted policies

3. **Encrypted Secrets**
   - KMS v2 now recommended for secret encryption at rest
   - Key rotation improvements

### Performance

1. **Scheduling Improvements**
   - Enhanced filter/score plugins
   - Better cluster utilization
   - Reduced scheduling latency for 95% of pods

2. **API Server Efficiency**
   - Request batching optimizations
   - Improved watch performance
   - Reduced CPU usage during high load

3. **Memory Efficiency**
   - Better GC patterns in kubelet
   - Reduced memory footprint
   - Improved node density

### Observability

1. **Structured Logging**
   - Consistent JSON logging across components
   - Better log aggregation support
   - Configurable via command-line flags

2. **Improved Metrics**
   - New histograms for request latencies
   - Enhanced traces in scheduler
   - Better kube-proxy metrics

---

## API Changes

### Removed APIs

The following APIs are removed in v1.30:
- `apiextensions.k8s.io/v1beta1` CustomResourceDefinition
- `apps/v1beta1` StatefulSet, Deployment, DaemonSet
- `batch/v1beta1` CronJob

**Migration Required:**
```yaml
# OLD (v1beta1) - NO LONGER SUPPORTED
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: mycrd.example.com

# NEW (v1) - USE THIS
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: mycrd.example.com
```

### Changed Field Semantics

**Pod `spec.securityContext`:**
- `fsGroup` now strictly enforced for volume ownership
- `seLinuxOptions` behavior standardized across runtimes

**Service `spec.loadBalancerSourceRanges`:**
- Validation now enforces CIDR format strictly
- Invalid entries will cause API rejection

---

## Deprecations and Removals

### Deprecated in v1.30 (Will be removed in v1.33)

1. **kubelet `--pod-max-pids` Flag**
   - Alternative: Use PodSecurityPolicy or Pod limit ranges
   - Timeline: Removal in v1.33

2. **kube-apiserver `--insecure-port` Flag**
   - Alternative: Use secure port only with client certificates
   - Timeline: Removal in v1.33

3. **HPA v1beta2 API**
   - Alternative: Use autoscaling/v2
   - Timeline: Removal in v1.33

### Removed in v1.30 (Previously Deprecated)

- `apiVersion: batch/v1beta1` CronJob
- `apiVersion: apps/v1beta1` Deployment
- `apiVersion: storage.k8s.io/v1beta1` StorageClass
- kube-apiserver `--enable-bootstrap-token-auth` flag

---

## Known Issues

### Container Runtime Issues

**Issue #123456: CoreDNS CPU Spikes**
- Affects: Some CNI plugins with large cluster DNS queries
- Workaround: Increase CoreDNS resource requests
- Status: Being investigated
- Expected Fix: v1.30.1

**Issue #123789: containerd + SELinux Incompatibility**
- Affects: RHEL 8+ with SELinux enabled
- Workaround: Use containerd >= 1.7.0
- Status: Tracked upstream
- Expected Fix: v1.30.2

### Scheduling Issues

**Issue #120123: Pod Preemption Hangs**
- Affects: Clusters with many priority classes
- Workaround: Reduce priority class count or upgrade etcd
- Status: Fix in testing
- Expected Fix: v1.30.1

### Networking Issues

**Issue #119789: Service Endpoint Slice Updates Delayed**
- Affects: Large clusters (>5000 pods)
- Workaround: Adjust `--endpoint-updates-batch-period`
- Status: Performance optimization in progress
- Expected Fix: v1.30.2

---

## Known Bugs and Issues

### Critical (Action Required)

- StatefulSet pod names may not be DNS-compliant after certain label updates
  - Workaround: Manually update pod names or recreate StatefulSet
  - Fix: v1.30.1

### High (Important)

- PersistentVolume reclamation may fail with certain storage backends
  - Workaround: Manual cleanup may be necessary
  - Fix: v1.30.2

### Medium

- Ingress controller may not respect custom header rewrites
  - Workaround: Use ServiceMesh alternative
  - Fix: v1.31

---

## Command Line Tool (kubectl) Changes

### New Commands

```bash
# New kubectl kms command for KMS v2 management
kubectl kms status

# Enhanced debugging with kubectl debug
kubectl debug <pod> --image=<debug-image> --target=<container>

# Resource metrics improvements
kubectl top node --containers
```

### Behavior Changes

- `kubectl apply` now performs stricter validation
- `kubectl logs` supports `--all-containers=true` flag
- `kubectl get` filtering improved for YAML/JSON output

### Deprecations

- `kubectl delta` command deprecated (use `kubectl diff`)
- `--generator` flag removed from `kubectl run`

---

## Metrics Changes

### Metrics Moved to Stable

- `apiserver_request_duration_seconds` (histogram)
- `kubelet_volume_stats_available_bytes`
- `scheduler_scheduling_duration_seconds`

### New Metrics

```
# Structured logging metrics
apiserver_log_json_parse_errors_total
apiserver_audit_event_total

# Pod disruption metrics
pod_disruption_budgets_errors_total

# User namespace metrics
pod_sandbox_user_namespace_enabled
```

### Deprecated Metrics (Removed in v1.32)

- `apiserver_request_count` (replaced by histogram)
- `kubelet_docker_operations_errors_total`

---

## Upgrading From v1.29

### Before Upgrading

1. **Verify etcd version**: Must be >= v3.5.1
2. **Check deprecated APIs**: Use `kubectl api-resources` to list affected resources
3. **Review RBAC policies**: Test with new validation rules
4. **Backup etcd**: Standard backup/restore procedure
5. **Test in staging**: Reproduce production cluster setup

### Upgrade Steps

```bash
# 1. Update kubeadm config
kubeadm upgrade plan

# 2. Upgrade control plane
sudo kubeadm upgrade apply v1.30.0

# 3. Upgrade worker nodes
# Run on each node:
kubeadm upgrade node
systemctl restart kubelet

# 4. Verify cluster health
kubectl get nodes
kubectl get componentstatuses
```

### Post-Upgrade Validation

```bash
# Check API server logs
kubectl logs -n kube-system kube-apiserver-<node>

# Verify all nodes ready
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n kube-system

# Run conformance tests
sonobuoy run --mode=quick
```

---

## Release Team

**Release Lead:** @kubernetes-release-lead

**Release Managers:**
- @rm1
- @rm2
- @rm3

**Release Notes Manager:** @notes-manager

---

## Download

**Release Artifacts:**
- [Kubernetes v1.30.0 Release](https://github.com/kubernetes/kubernetes/releases/tag/v1.30.0)
- [Source Code](https://github.com/kubernetes/kubernetes/archive/v1.30.0.tar.gz)
- [Client Binaries](https://kubernetes.io/docs/setup/release/notes/)

**Container Images:**
- `registry.k8s.io/kube-apiserver:v1.30.0`
- `registry.k8s.io/kube-controller-manager:v1.30.0`
- `registry.k8s.io/kube-scheduler:v1.30.0`
- `registry.k8s.io/kubelet:v1.30.0`

**Verification:**
```bash
# Verify binary checksums
sha256sum kubernetes-server-linux-amd64.tar.gz
# Compare with published checksums

# Verify container images
crane digest registry.k8s.io/kube-apiserver:v1.30.0
```

---

**Release Deadline:** June 17, 2024 (12 weeks support period)
**Next Release:** Kubernetes v1.31 (August 2024)
**Documentation:** https://kubernetes.io/docs/setup/release/notes/
