# Infrastructure as Code (IaC) - Elite Professional Practices

**Declarative, version-controlled infrastructure management**

---

## Overview

Infrastructure as Code (IaC) is the practice of managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This subskill covers elite practices from HashiCorp, AWS, Google Cloud, and other tier-1 organizations.

## Core Principles

1. **Declarative over Imperative**: Define desired state, let tools converge
2. **Idempotency**: Running the same code produces the same result
3. **Version Control**: All infrastructure in Git
4. **Immutability**: Replace infrastructure rather than modify
5. **Modularity**: Reusable, composable infrastructure components

## Technology Stack

**Terraform** (HashiCorp) - Multi-cloud infrastructure provisioning
**Pulumi** - Infrastructure as code using general-purpose languages
**CloudFormation** - AWS-native infrastructure templates
**ARM/Bicep** - Azure infrastructure automation
**Crossplane** - Kubernetes-native infrastructure management
**Ansible** - Configuration management and automation

## Best Practices

- Use remote state with locking
- Implement CI/CD for infrastructure changes
- Use modules for reusability
- Separate environments with workspaces
- Implement policy as code (OPA, Sentinel)
- Tag all resources for governance

---

**Version**: 1.0
**Last Updated**: 2025-11-19
