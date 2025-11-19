# Policy as Code Reference

## Overview

Policy as Code allows you to define, version, and automate infrastructure compliance policies using code. This enables automated validation of infrastructure before deployment and continuous compliance monitoring.

## Open Policy Agent (OPA)

### Rego Language Basics

**Structure**
```rego
package terraform.analysis

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Deny rule - blocks deployment if violated
deny[msg] {
    # Logic here
    msg := "Error message"
}

# Warn rule - shows warning but doesn't block
warn[msg] {
    # Logic here
    msg := "Warning message"
}

# Allow rule - explicitly allows (optional)
allow {
    # Logic here
}
```

**Basic Syntax**
```rego
package example

# Simple rule
rule_name {
    condition1
    condition2
}

# Rule with assignment
rule_name := value {
    # Logic
    value := "result"
}

# Rule that generates multiple results
rule_name[x] {
    # Logic that iterates
    some i
    x := array[i]
}

# Comprehensions
new_array := [x | some i; x := array[i]; x > 10]
new_object := {k: v | some k; v := object[k]; v != ""}
new_set := {x | some i; x := array[i]}

# Conditions
rule {
    x == y          # Equality
    x != y          # Inequality
    x > y           # Greater than
    x >= y          # Greater than or equal
    x < y           # Less than
    x <= y          # Less than or equal
}

# Functions
function(arg1, arg2) := result {
    result := arg1 + arg2
}
```

### Terraform Policy Examples

**Require S3 Bucket Encryption**
```rego
package terraform.s3

import future.keywords.if

# Deny unencrypted S3 buckets
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_encryption(resource)

    msg := sprintf(
        "S3 bucket '%s' must have encryption enabled",
        [resource.address]
    )
}

has_encryption(resource) {
    resource.change.after.server_side_encryption_configuration
}
```

**Enforce Tagging Standards**
```rego
package terraform.tagging

required_tags := ["Environment", "Owner", "CostCenter"]

deny[msg] {
    resource := input.resource_changes[_]
    is_taggable(resource.type)

    missing_tags := get_missing_tags(resource)
    count(missing_tags) > 0

    msg := sprintf(
        "Resource '%s' is missing required tags: %v",
        [resource.address, missing_tags]
    )
}

is_taggable(type) {
    taggable_types := {
        "aws_instance",
        "aws_vpc",
        "aws_subnet",
        "aws_security_group",
        "aws_s3_bucket",
        "aws_rds_instance"
    }
    taggable_types[type]
}

get_missing_tags(resource) := missing {
    existing_tags := object.keys(resource.change.after.tags)
    missing := [tag | tag := required_tags[_]; not tag in existing_tags]
}
```

**Prevent Public Access**
```rego
package terraform.security

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group"

    ingress := resource.change.after.ingress[_]
    is_public(ingress)
    is_dangerous_port(ingress.from_port)

    msg := sprintf(
        "Security group '%s' allows public access on dangerous port %d",
        [resource.address, ingress.from_port]
    )
}

is_public(ingress) {
    "0.0.0.0/0" in ingress.cidr_blocks
}

is_dangerous_port(port) {
    dangerous_ports := {22, 3389, 3306, 5432, 1433}
    dangerous_ports[port]
}
```

**Enforce Resource Naming Convention**
```rego
package terraform.naming

import future.keywords.if

deny[msg] {
    resource := input.resource_changes[_]
    resource.mode == "managed"

    name := get_resource_name(resource)
    not matches_naming_convention(name, resource.type)

    msg := sprintf(
        "Resource '%s' name '%s' doesn't match naming convention",
        [resource.address, name]
    )
}

get_resource_name(resource) := name {
    name := resource.change.after.name
} else := name {
    name := resource.change.after.tags.Name
}

matches_naming_convention(name, type) {
    # Format: {environment}-{service}-{resource}
    regex.match(`^(dev|staging|prod)-[a-z0-9-]+-[a-z0-9-]+$`, name)
}
```

**Cost Control**
```rego
package terraform.cost

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"

    instance_type := resource.change.after.instance_type
    is_expensive(instance_type)

    msg := sprintf(
        "Instance '%s' uses expensive instance type '%s'",
        [resource.address, instance_type]
    )
}

is_expensive(instance_type) {
    # Block instance types larger than xlarge
    regex.match(`\.(2xlarge|4xlarge|8xlarge|.*metal)$`, instance_type)
}

warn[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_rds_instance"

    storage := resource.change.after.allocated_storage
    storage > 1000

    msg := sprintf(
        "RDS instance '%s' allocates %d GB, which may be costly",
        [resource.address, storage]
    )
}
```

**Multi-AZ Requirement**
```rego
package terraform.availability

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_rds_instance"

    environment := resource.change.after.tags.Environment
    environment == "prod"

    not resource.change.after.multi_az

    msg := sprintf(
        "Production RDS instance '%s' must have multi_az enabled",
        [resource.address]
    )
}

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_elasticsearch_domain"

    environment := resource.change.after.tags.Environment
    environment == "prod"

    zone_awareness := resource.change.after.cluster_config[_].zone_awareness_enabled
    not zone_awareness

    msg := sprintf(
        "Production Elasticsearch domain '%s' must have zone awareness enabled",
        [resource.address]
    )
}
```

### Running OPA Policies

**CLI Usage**
```bash
# Install OPA
brew install opa  # macOS
# or download from: openpolicyagent.org/downloads

# Generate Terraform plan JSON
terraform plan -out=tfplan
terraform show -json tfplan > tfplan.json

# Test policy
opa eval -i tfplan.json -d policy.rego "data.terraform.deny"

# Test with formatted output
opa eval -i tfplan.json -d policy.rego \
  --format pretty \
  "data.terraform.deny"

# Run all policies
opa exec --decision terraform/deny \
  --bundle policy/ \
  tfplan.json
```

**Policy Testing**
```rego
package terraform.s3_test

import future.keywords.if

test_s3_encryption_required {
    result := data.terraform.s3.deny with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.test",
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }]
    }
    count(result) > 0
}

test_s3_encrypted_allowed {
    result := data.terraform.s3.deny with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.test",
            "change": {
                "after": {
                    "bucket": "test-bucket",
                    "server_side_encryption_configuration": [{
                        "rule": [{
                            "apply_server_side_encryption_by_default": [{
                                "sse_algorithm": "AES256"
                            }]
                        }]
                    }]
                }
            }
        }]
    }
    count(result) == 0
}
```

```bash
# Run tests
opa test policy/*.rego -v
```

## Terraform Sentinel

### Policy Language

**Basic Policy**
```sentinel
import "tfplan/v2" as tfplan

# Require all EC2 instances to have specific tags
required_tags = ["Environment", "Owner"]

# Main rule
main = rule {
    all tfplan.resource_changes as _, rc {
        rc.type is "aws_instance" implies
            all required_tags as tag {
                rc.change.after.tags contains tag
            }
    }
}
```

**Policy Structure**
```sentinel
# Imports
import "tfplan/v2" as tfplan
import "tfrun"
import "strings"

# Parameters (can be overridden)
param max_instance_type default "t3.large"

# Functions
is_production = func() {
    return tfrun.workspace.name is "production"
}

# Helper functions
filter_resources = func(type) {
    return filter tfplan.resource_changes as address, rc {
        rc.type is type and
        rc.mode is "managed" and
        (rc.change.actions contains "create" or rc.change.actions contains "update")
    }
}

# Rules
instance_type_allowed = rule {
    all filter_resources("aws_instance") as address, rc {
        strings.has_prefix(rc.change.after.instance_type, "t3.")
    }
}

# Main rule (combines all rules)
main = rule {
    instance_type_allowed
}
```

**Advanced Examples**

**Limit Instance Types by Environment**
```sentinel
import "tfplan/v2" as tfplan
import "tfrun"

allowed_instance_types = {
    "dev": ["t3.micro", "t3.small"],
    "staging": ["t3.small", "t3.medium"],
    "prod": ["t3.medium", "t3.large", "t3.xlarge"]
}

workspace_to_env = {
    "dev-vpc": "dev",
    "staging-vpc": "staging",
    "prod-vpc": "prod"
}

get_environment = func() {
    return workspace_to_env[tfrun.workspace.name] else "dev"
}

main = rule {
    all tfplan.resource_changes as _, rc {
        rc.type is "aws_instance" implies
            rc.change.after.instance_type in allowed_instance_types[get_environment()]
    }
}
```

**Require Encryption**
```sentinel
import "tfplan/v2" as tfplan

# All RDS instances must be encrypted
rds_encrypted = rule {
    all tfplan.resource_changes as _, rc {
        rc.type is "aws_db_instance" implies
            rc.change.after.storage_encrypted is true
    }
}

# All EBS volumes must be encrypted
ebs_encrypted = rule {
    all tfplan.resource_changes as _, rc {
        rc.type is "aws_ebs_volume" implies
            rc.change.after.encrypted is true
    }
}

main = rule {
    rds_encrypted and ebs_encrypted
}
```

**Cost Estimation**
```sentinel
import "tfrun"
import "decimal"

# Limit monthly cost increase
max_monthly_delta = decimal.new(1000)

cost_check = rule {
    decimal.new(tfrun.cost_estimate.delta_monthly_cost) less_than max_monthly_delta
}

main = rule {
    cost_check
}
```

### Policy Sets

**sentinel.hcl**
```hcl
policy "require-tags" {
    source = "./require-tags.sentinel"
    enforcement_level = "hard-mandatory"
}

policy "limit-instance-types" {
    source = "./limit-instance-types.sentinel"
    enforcement_level = "soft-mandatory"
}

policy "cost-control" {
    source = "./cost-control.sentinel"
    enforcement_level = "advisory"
}

# Modules can be imported
module "tfplan-functions" {
    source = "./common-functions/tfplan-functions.sentinel"
}
```

**Enforcement Levels:**
- `hard-mandatory`: Must pass, no overrides
- `soft-mandatory`: Must pass, can be overridden
- `advisory`: Warning only, doesn't block

## Checkov

### Built-in Policies

```bash
# Install Checkov
pip install checkov

# Scan Terraform directory
checkov -d /path/to/terraform

# Scan specific file
checkov -f main.tf

# Output formats
checkov -d . --output json
checkov -d . --output junitxml
checkov -d . --output github_failed_only

# Skip specific checks
checkov -d . --skip-check CKV_AWS_20,CKV_AWS_52

# Check specific frameworks
checkov -d . --framework terraform

# Scan Terraform plan
terraform plan -out tfplan
checkov -f tfplan

# Set baseline
checkov -d . --create-baseline
checkov -d . --baseline baseline.json
```

### Custom Policies

**Python Check**
```python
# my_custom_check.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class RequireSpecificTags(BaseResourceCheck):
    def __init__(self):
        name = "Ensure resources have required tags"
        id = "CKV_CUSTOM_1"
        supported_resources = [
            'aws_instance',
            'aws_vpc',
            'aws_subnet'
        ]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources
        )

    def scan_resource_conf(self, conf):
        """
        Looks for required tags in resource configuration
        """
        required_tags = ['Environment', 'Owner', 'CostCenter']

        if 'tags' in conf:
            tags = conf['tags'][0] if isinstance(conf['tags'], list) else conf['tags']

            for required_tag in required_tags:
                if required_tag not in tags:
                    self.details = f"Missing required tag: {required_tag}"
                    return CheckResult.FAILED

            return CheckResult.PASSED

        self.details = "No tags defined"
        return CheckResult.FAILED

check = RequireSpecificTags()
```

**YAML Check**
```yaml
# custom_checks.yaml
---
metadata:
  name: "Ensure S3 buckets have versioning enabled"
  id: "CUSTOM_AWS_S3_1"
  category: "BACKUP_AND_RECOVERY"

definition:
  cond_type: "attribute"
  resource_types:
    - "aws_s3_bucket"
  attribute: "versioning.enabled"
  operator: "equals"
  value: true
```

```bash
# Run with custom checks
checkov -d . --external-checks-dir ./custom_checks
```

### Suppression

**Inline Suppression**
```hcl
# Suppress single check
resource "aws_s3_bucket" "example" {
  # checkov:skip=CKV_AWS_20:Reason for skipping
  bucket = "example-bucket"
}

# Suppress multiple checks
resource "aws_instance" "example" {
  # checkov:skip=CKV_AWS_8:Public IP required for bastion
  # checkov:skip=CKV_AWS_135:EBS optimization not needed
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}
```

**Config File**
```yaml
# .checkov.yml
framework:
  - terraform
  - terraform_plan

skip-check:
  - CKV_AWS_20  # S3 bucket logging
  - CKV_AWS_52  # S3 bucket MFA delete

soft-fail: true

output: json

quiet: false
```

## TFLint

### Configuration

**.tflint.hcl**
```hcl
config {
  module = true
  force = false
}

plugin "aws" {
  enabled = true
  version = "0.27.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "azurerm" {
  enabled = true
  version = "0.25.0"
  source  = "github.com/terraform-linters/tflint-ruleset-azurerm"
}

rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "aws_instance_invalid_type" {
  enabled = true
}

rule "aws_instance_previous_type" {
  enabled = true
}
```

### Custom Rules

**Rule Configuration**
```hcl
# .tflint.hcl
plugin "local" {
  enabled = true
  source  = "github.com/org/tflint-ruleset-local"
}

rule "local_require_tags" {
  enabled = true
  tags    = ["Environment", "Owner"]
}

rule "local_restrict_instance_types" {
  enabled = true
  allowed_types = ["t3.micro", "t3.small", "t3.medium"]
}
```

### Usage

```bash
# Install TFLint
brew install tflint

# Initialize plugins
tflint --init

# Lint current directory
tflint

# Recursive lint
tflint --recursive

# Specific module
tflint --module

# Output formats
tflint --format json
tflint --format checkstyle
tflint --format junit

# Enable/disable rules
tflint --enable-rule=aws_instance_invalid_type
tflint --disable-rule=terraform_unused_declarations

# CI integration
tflint --format compact --force
```

## Terrascan

### Usage

```bash
# Install
brew install terrascan

# Scan directory
terrascan scan -d /path/to/terraform

# Scan specific IaC type
terrascan scan -t terraform
terrascan scan -t k8s
terrascan scan -t helm

# Scan remote repository
terrascan scan -r git -u https://github.com/org/repo

# Output formats
terrascan scan -o json
terrascan scan -o yaml
terrascan scan -o xml
terrascan scan -o junit-xml

# Specify policies
terrascan scan -p AWS
terrascan scan -p AZURE
terrascan scan -p GCP

# Skip rules
terrascan scan --skip-rules AWS.S3Bucket.DS.High.1043

# Config file mode
terrascan scan -c terrascan-config.toml
```

### Configuration

**terrascan-config.toml**
```toml
[rules]
skip-rules = [
    "AWS.S3Bucket.DS.High.1043",
    "AWS.EC2.NetworkSecurity.Medium.0506"
]

[severity]
level = "MEDIUM"  # Skip LOW severity issues

[notifications]
webhook-url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Policy as Code CI/CD

### GitHub Actions

```yaml
name: Policy Validation

on:
  pull_request:
    paths:
      - '**.tf'
      - '**.tfvars'

jobs:
  policy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: |
          terraform plan -out=tfplan
          terraform show -json tfplan > tfplan.json

      - name: OPA Policy Check
        uses: open-policy-agent/opa-toolkit@v1
        with:
          policy-path: ./policies
          input: tfplan.json

      - name: Checkov Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          output_format: cli
          soft_fail: false

      - name: TFLint
        uses: terraform-linters/setup-tflint@v3
        with:
          tflint_version: latest

      - name: Run TFLint
        run: tflint --init && tflint -f compact

      - name: Terrascan
        uses: tenable/terrascan-action@main
        with:
          iac_type: 'terraform'
          iac_dir: '.'
          policy_type: 'aws'
          fail_on_violation: true
```

### GitLab CI

```yaml
stages:
  - validate
  - policy

policy-check:
  stage: policy
  image: hashicorp/terraform:latest
  before_script:
    - apk add --no-cache python3 py3-pip
    - pip3 install checkov
    - wget -q https://github.com/open-policy-agent/opa/releases/download/v0.57.0/opa_linux_amd64 -O /usr/local/bin/opa
    - chmod +x /usr/local/bin/opa
  script:
    # OPA
    - terraform plan -out=tfplan
    - terraform show -json tfplan > tfplan.json
    - opa exec --decision terraform/deny --bundle policies/ tfplan.json

    # Checkov
    - checkov -d . --output cli --output json --output-file-path .

    # TFLint
    - |
      curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
      tflint --init
      tflint
  artifacts:
    when: always
    paths:
      - results_checkov.json
    reports:
      junit: results_checkov.json
```

## Resources

- OPA Documentation: openpolicyagent.org/docs
- Sentinel Language: docs.hashicorp.com/sentinel
- Checkov: checkov.io
- TFLint: github.com/terraform-linters/tflint
- Terrascan: github.com/tenable/terrascan
