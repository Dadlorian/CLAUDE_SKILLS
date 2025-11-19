# GitOps - Elite Professional Practices

**Git as single source of truth for declarative infrastructure and applications**

---

## Overview

GitOps is a way of implementing Continuous Deployment for cloud-native applications, using Git as the single source of truth for declarative infrastructure and applications. Pioneered by Weaveworks, adopted by CNCF.

## Core Principles

1. **Declarative**: System described declaratively
2. **Versioned and Immutable**: Stored in Git, never modified directly
3. **Pulled Automatically**: Software agents auto-pull from Git
4. **Continuously Reconciled**: Agents ensure actual state matches desired state

## GitOps Workflow

1. Developer commits code to application repo
2. CI pipeline builds and tests, pushes image to registry
3. CI updates image tag in GitOps repo
4. GitOps operator detects change in Git
5. Operator pulls new manifests and applies to cluster
6. Operator continuously reconciles state

## Technology Stack

**ArgoCD** - Kubernetes-native GitOps
**Flux** - GitOps operator (CNCF)
**Rancher Fleet** - Multi-cluster GitOps
**Jenkins X** - Cloud-native CI/CD with GitOps

## Best Practices

- Separate repos for application code and manifests
- Use branches or directories for environments
- Implement drift detection and alerts
- Require PR reviews for all infrastructure changes
- Automate testing in CI before merge

---

**Version**: 1.0
**Last Updated**: 2025-11-19
