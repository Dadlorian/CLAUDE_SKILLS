# IaC Testing Reference

## Testing Pyramid for IaC

```
        /\
       /  \
      /E2E \          End-to-End Tests
     /------\         (Slow, Expensive, Few)
    /        \
   /Integration\      Integration Tests
  /------------\      (Medium Speed, Medium Cost, Some)
 /              \
/  Unit Tests    \    Unit Tests
------------------    (Fast, Cheap, Many)
```

## Static Testing

### Terraform Validate
```bash
# Syntax validation
terraform validate

# Format check
terraform fmt -check -recursive

# Format and write
terraform fmt -recursive
```

### Linting

**TFLint**
```bash
# Install
brew install tflint
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Configuration (.tflint.hcl)
config {
  module = true
}

plugin "aws" {
  enabled = true
  version = "0.27.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

# Run linting
tflint --init
tflint
tflint --recursive
tflint --module

# CI integration
tflint --format=checkstyle > tflint-report.xml
```

### Security Scanning

**Checkov**
```bash
# Full scan
checkov -d .

# Specific file
checkov -f main.tf

# Terraform plan
terraform plan -out tfplan
checkov -f tfplan

# With baseline
checkov -d . --baseline baseline.json

# Output formats
checkov -d . --output json --output-file results.json
checkov -d . --output junitxml --output-file results.xml
```

**tfsec**
```bash
# Install
brew install tfsec

# Scan directory
tfsec .

# With custom checks
tfsec . --custom-check-dir ./custom-checks

# Exclude checks
tfsec . --exclude AWS002,AWS017

# Output formats
tfsec . --format json
tfsec . --format junit
tfsec . --format sarif

# Minimum severity
tfsec . --minimum-severity HIGH
```

## Unit Testing

### Terraform Mock Testing

**Using Mock Provider**
```hcl
# test/main.tf
terraform {
  required_providers {
    testing = {
      source = "apparentlymart/testing"
    }
  }
}

provider "testing" {
  # Mock provider for testing
}

module "vpc" {
  source = "../modules/vpc"

  name               = "test-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
}

# Assertions
resource "testing_assertion" "vpc_cidr_valid" {
  component = "vpc"
  equal {
    statement = "VPC CIDR is correct"
    got       = module.vpc.vpc_cidr_block
    want      = "10.0.0.0/16"
  }
}

resource "testing_assertion" "subnet_count" {
  component = "vpc"
  equal {
    statement = "Correct number of subnets"
    got       = length(module.vpc.public_subnet_ids)
    want      = 2
  }
}
```

### Terratest (Go)

**Basic Test**
```go
// test/vpc_test.go
package test

import (
    "testing"

    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
    t.Parallel()

    opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/complete",

        Vars: map[string]interface{}{
            "name":               "test-vpc",
            "cidr_block":         "10.0.0.0/16",
            "availability_zones": []string{"us-east-1a", "us-east-1b"},
            "public_subnet_cidrs": []string{"10.0.1.0/24", "10.0.2.0/24"},
        },

        EnvVars: map[string]string{
            "AWS_DEFAULT_REGION": "us-east-1",
        },
    })

    defer terraform.Destroy(t, opts)

    terraform.InitAndApply(t, opts)

    // Test outputs
    vpcID := terraform.Output(t, opts, "vpc_id")
    assert.NotEmpty(t, vpcID)
    assert.Regexp(t, "^vpc-[a-z0-9]+$", vpcID)

    vpcCIDR := terraform.Output(t, opts, "vpc_cidr_block")
    assert.Equal(t, "10.0.0.0/16", vpcCIDR)

    subnetIDs := terraform.OutputList(t, opts, "public_subnet_ids")
    assert.Equal(t, 2, len(subnetIDs))
}
```

**Advanced Test with AWS SDK**
```go
package test

import (
    "testing"

    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/ec2"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestVPCConfiguration(t *testing.T) {
    t.Parallel()

    opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/complete",
    })

    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)

    vpcID := terraform.Output(t, opts, "vpc_id")

    // Verify VPC settings using AWS API
    sess := session.Must(session.NewSession(&aws.Config{
        Region: aws.String("us-east-1"),
    }))

    ec2Client := ec2.New(sess)

    // Describe VPC
    vpcOutput, err := ec2Client.DescribeVpcs(&ec2.DescribeVpcsInput{
        VpcIds: []*string{aws.String(vpcID)},
    })
    require.NoError(t, err)
    require.Equal(t, 1, len(vpcOutput.Vpcs))

    vpc := vpcOutput.Vpcs[0]

    // Assertions
    assert.Equal(t, "10.0.0.0/16", *vpc.CidrBlock)
    assert.True(t, *vpc.EnableDnsSupport)
    assert.True(t, *vpc.EnableDnsHostnames)

    // Verify tags
    tags := make(map[string]string)
    for _, tag := range vpc.Tags {
        tags[*tag.Key] = *tag.Value
    }
    assert.Equal(t, "test-vpc", tags["Name"])
    assert.NotEmpty(t, tags["Environment"])
}

func TestSubnetConfiguration(t *testing.T) {
    t.Parallel()

    opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../examples/complete",
    })

    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)

    subnetIDs := terraform.OutputList(t, opts, "public_subnet_ids")

    sess := session.Must(session.NewSession(&aws.Config{
        Region: aws.String("us-east-1"),
    }))

    ec2Client := ec2.New(sess)

    // Verify each subnet
    for _, subnetID := range subnetIDs {
        subnetOutput, err := ec2Client.DescribeSubnets(&ec2.DescribeSubnetsInput{
            SubnetIds: []*string{aws.String(subnetID)},
        })
        require.NoError(t, err)
        require.Equal(t, 1, len(subnetOutput.Subnets))

        subnet := subnetOutput.Subnets[0]

        // Public subnets should auto-assign public IPs
        assert.True(t, *subnet.MapPublicIpOnLaunch)
    }
}
```

**Table-Driven Tests**
```go
func TestVPCWithDifferentConfigurations(t *testing.T) {
    t.Parallel()

    testCases := []struct {
        name           string
        cidr           string
        azCount        int
        expectError    bool
    }{
        {"Small VPC", "10.0.0.0/24", 2, false},
        {"Medium VPC", "10.0.0.0/20", 3, false},
        {"Large VPC", "10.0.0.0/16", 3, false},
        {"Invalid CIDR", "invalid", 2, true},
    }

    for _, tc := range testCases {
        tc := tc // Capture range variable
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()

            opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
                TerraformDir: "../examples/complete",
                Vars: map[string]interface{}{
                    "cidr_block": tc.cidr,
                    "az_count":   tc.azCount,
                },
            })

            defer terraform.Destroy(t, opts)

            _, err := terraform.InitAndApplyE(t, opts)

            if tc.expectError {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### Kitchen-Terraform (Ruby)

**kitchen.yml**
```yaml
---
driver:
  name: terraform
  root_module_directory: test/fixtures/default

provisioner:
  name: terraform

platforms:
  - name: aws

verifier:
  name: terraform
  systems:
    - name: default
      backend: aws
      controls:
        - vpc_configuration
        - subnet_configuration

suites:
  - name: default
    driver:
      variables:
        name: test-vpc
        cidr_block: 10.0.0.0/16
```

**test/integration/default/controls/vpc_spec.rb**
```ruby
# frozen_string_literal: true

control 'vpc_configuration' do
  impact 1.0
  title 'VPC Configuration'
  desc 'Verify VPC is configured correctly'

  describe aws_vpc(vpc_id: input(:vpc_id)) do
    it { should exist }
    its('cidr_block') { should eq '10.0.0.0/16' }
    its('state') { should eq 'available' }
    it { should have_dns_enabled }
    it { should have_dns_hostnames_enabled }
  end

  describe aws_vpc(vpc_id: input(:vpc_id)).tags do
    its('Name') { should eq 'test-vpc' }
    its('ManagedBy') { should eq 'Terraform' }
  end
end

control 'subnet_configuration' do
  impact 1.0
  title 'Subnet Configuration'
  desc 'Verify subnets are configured correctly'

  input(:public_subnet_ids).each do |subnet_id|
    describe aws_subnet(subnet_id: subnet_id) do
      it { should exist }
      it { should be_mapping_public_ip_on_launch }
      it { should be_available }
    end
  end

  input(:private_subnet_ids).each do |subnet_id|
    describe aws_subnet(subnet_id: subnet_id) do
      it { should exist }
      it { should_not be_mapping_public_ip_on_launch }
      it { should be_available }
    end
  end
end
```

### Pulumi Testing

**TypeScript Unit Tests**
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import { expect } from "chai";
import "mocha";

// Mock Pulumi runtime
pulumi.runtime.setMocks({
    newResource: function(args: pulumi.runtime.MockResourceArgs): {id: string, state: any} {
        return {
            id: args.name + "_id",
            state: args.inputs,
        };
    },
    call: function(args: pulumi.runtime.MockCallArgs) {
        return args.inputs;
    },
});

describe("VPC Infrastructure", function() {
    let infra: typeof import("../index");

    before(async function() {
        infra = await import("../index");
    });

    describe("VPC", function() {
        it("should have correct CIDR block", function(done) {
            pulumi.all([infra.vpc.cidrBlock]).apply(([cidrBlock]) => {
                expect(cidrBlock).to.equal("10.0.0.0/16");
                done();
            });
        });

        it("should have DNS support enabled", function(done) {
            pulumi.all([infra.vpc.enableDnsSupport]).apply(([dnsSupport]) => {
                expect(dnsSupport).to.be.true;
                done();
            });
        });

        it("should have required tags", function(done) {
            pulumi.all([infra.vpc.tags]).apply(([tags]) => {
                expect(tags).to.have.property("Environment");
                expect(tags).to.have.property("ManagedBy");
                done();
            });
        });
    });

    describe("Subnets", function() {
        it("should create correct number of public subnets", function(done) {
            pulumi.all([infra.publicSubnets]).apply(([subnets]) => {
                expect(subnets).to.have.lengthOf(3);
                done();
            });
        });

        it("should enable public IP for public subnets", function(done) {
            pulumi.all([infra.publicSubnets[0].mapPublicIpOnLaunch]).apply(([mapPublicIp]) => {
                expect(mapPublicIp).to.be.true;
                done();
            });
        });
    });
});
```

**Python Unit Tests**
```python
import unittest
import pulumi

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + '_id', args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

pulumi.runtime.set_mocks(MyMocks())

# Import infrastructure module
import infra

class InfrastructureTest(unittest.TestCase):

    @pulumi.runtime.test
    def test_vpc_cidr(self):
        def check_cidr(args):
            cidr_block = args[0]
            self.assertEqual(cidr_block, "10.0.0.0/16")

        return infra.vpc.cidr_block.apply(check_cidr)

    @pulumi.runtime.test
    def test_vpc_tags(self):
        def check_tags(args):
            tags = args[0]
            self.assertIn("Environment", tags)
            self.assertIn("ManagedBy", tags)
            self.assertEqual(tags["ManagedBy"], "Pulumi")

        return infra.vpc.tags.apply(check_tags)

    @pulumi.runtime.test
    def test_subnet_count(self):
        def check_count(args):
            subnets = args[0]
            self.assertEqual(len(subnets), 3)

        return pulumi.Output.all(infra.public_subnets).apply(check_count)

if __name__ == '__main__':
    unittest.main()
```

## Integration Testing

### Multi-Stage Testing

```go
func TestCompleteInfrastructure(t *testing.T) {
    t.Parallel()

    // Stage 1: Network
    networkOpts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/network",
    })

    defer terraform.Destroy(t, networkOpts)
    terraform.InitAndApply(t, networkOpts)

    vpcID := terraform.Output(t, networkOpts, "vpc_id")
    subnetIDs := terraform.OutputList(t, networkOpts, "private_subnet_ids")

    // Stage 2: Database (depends on network)
    databaseOpts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/database",
        Vars: map[string]interface{}{
            "vpc_id":     vpcID,
            "subnet_ids": subnetIDs,
        },
    })

    defer terraform.Destroy(t, databaseOpts)
    terraform.InitAndApply(t, databaseOpts)

    dbEndpoint := terraform.Output(t, databaseOpts, "endpoint")

    // Stage 3: Application (depends on database)
    appOpts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/application",
        Vars: map[string]interface{}{
            "vpc_id":      vpcID,
            "subnet_ids":  subnetIDs,
            "db_endpoint": dbEndpoint,
        },
    })

    defer terraform.Destroy(t, appOpts)
    terraform.InitAndApply(t, appOpts)

    // Verify application
    appURL := terraform.Output(t, appOpts, "application_url")
    http_helper.HttpGetWithRetry(
        t,
        fmt.Sprintf("http://%s", appURL),
        nil,
        200,
        "Hello, World!",
        30,
        10*time.Second,
    )
}
```

### InSpec Testing

**inspec.yml**
```yaml
name: terraform-vpc
title: VPC Infrastructure Tests
version: 1.0.0
supports:
  - platform: aws

inputs:
  - name: vpc_id
    type: string
    required: true

  - name: subnet_ids
    type: array
    required: true
```

**controls/vpc_spec.rb**
```ruby
control 'vpc-1.0' do
  impact 1.0
  title 'VPC Configuration'

  describe aws_vpc(input('vpc_id')) do
    it { should exist }
    its('cidr_block') { should eq '10.0.0.0/16' }
    its('state') { should eq 'available' }
    its('instance_tenancy') { should eq 'default' }
  end

  describe aws_security_groups.where(vpc_id: input('vpc_id')) do
    its('group_ids.count') { should be > 0 }
  end
end

control 'subnet-1.0' do
  impact 1.0
  title 'Subnet Configuration'

  input('subnet_ids').each do |subnet_id|
    describe aws_subnet(subnet_id) do
      it { should exist }
      it { should be_available }
      its('vpc_id') { should eq input('vpc_id') }
    end
  end
end
```

## End-to-End Testing

### Complete Application Test

```go
func TestE2EApplication(t *testing.T) {
    t.Parallel()

    opts := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../",
        Vars: map[string]interface{}{
            "environment": "test",
        },
    })

    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)

    // Get application URL
    appURL := terraform.Output(t, opts, "application_url")

    // Test 1: Health check
    http_helper.HttpGetWithRetry(
        t,
        fmt.Sprintf("https://%s/health", appURL),
        nil,
        200,
        `{"status":"healthy"}`,
        30,
        10*time.Second,
    )

    // Test 2: API endpoint
    response, err := http_helper.HttpGetE(
        t,
        fmt.Sprintf("https://%s/api/users", appURL),
    )
    require.NoError(t, err)
    assert.Equal(t, 200, response.StatusCode)

    // Test 3: Database connectivity
    dbEndpoint := terraform.Output(t, opts, "db_endpoint")
    testDatabaseConnection(t, dbEndpoint)

    // Test 4: Storage functionality
    bucketName := terraform.Output(t, opts, "bucket_name")
    testS3Operations(t, bucketName)
}

func testDatabaseConnection(t *testing.T, endpoint string) {
    // Implement database connection test
    sess := session.Must(session.NewSession())
    rdsClient := rds.New(sess)

    // Verify RDS instance is available
    input := &rds.DescribeDBInstancesInput{
        DBInstanceIdentifier: aws.String(endpoint),
    }

    result, err := rdsClient.DescribeDBInstances(input)
    require.NoError(t, err)
    require.Equal(t, "available", *result.DBInstances[0].DBInstanceStatus)
}

func testS3Operations(t *testing.T, bucketName string) {
    sess := session.Must(session.NewSession())
    s3Client := s3.New(sess)

    // Test PUT
    _, err := s3Client.PutObject(&s3.PutObjectInput{
        Bucket: aws.String(bucketName),
        Key:    aws.String("test-file.txt"),
        Body:   strings.NewReader("test content"),
    })
    require.NoError(t, err)

    // Test GET
    result, err := s3Client.GetObject(&s3.GetObjectInput{
        Bucket: aws.String(bucketName),
        Key:    aws.String("test-file.txt"),
    })
    require.NoError(t, err)
    defer result.Body.Close()

    body, err := ioutil.ReadAll(result.Body)
    require.NoError(t, err)
    assert.Equal(t, "test content", string(body))

    // Test DELETE
    _, err = s3Client.DeleteObject(&s3.DeleteObjectInput{
        Bucket: aws.String(bucketName),
        Key:    aws.String("test-file.txt"),
    })
    require.NoError(t, err)
}
```

## Test Helpers and Utilities

### Retry Logic
```go
func WaitForResourceReady(t *testing.T, checkFunc func() bool, timeout time.Duration) {
    deadline := time.Now().Add(timeout)

    for time.Now().Before(deadline) {
        if checkFunc() {
            return
        }
        time.Sleep(10 * time.Second)
    }

    t.Fatal("Resource not ready within timeout")
}
```

### Test Fixtures
```go
func GetTestConfig(t *testing.T) map[string]interface{} {
    return map[string]interface{}{
        "name":        fmt.Sprintf("test-vpc-%d", time.Now().Unix()),
        "cidr_block":  "10.0.0.0/16",
        "environment": "test",
        "tags": map[string]string{
            "Testing":   "true",
            "CreatedBy": "terratest",
        },
    }
}
```

### Cleanup Utilities
```go
func CleanupResources(t *testing.T, resourceType string, namePrefix string) {
    sess := session.Must(session.NewSession())

    switch resourceType {
    case "vpc":
        ec2Client := ec2.New(sess)
        // Find and delete test VPCs
        // Implementation...
    case "s3":
        s3Client := s3.New(sess)
        // Find and delete test buckets
        // Implementation...
    }
}
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Infrastructure Tests

on:
  pull_request:
    paths:
      - '**.tf'
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2

      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Validate
        run: |
          terraform init -backend=false
          terraform validate

      - name: Security Scan
        run: |
          pip install checkov
          checkov -d .

      - name: Run Terratest
        run: |
          cd test
          go test -v -timeout 30m
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: us-east-1
```

## Resources

- Terratest: terratest.gruntwork.io
- Kitchen-Terraform: github.com/newcontext-oss/kitchen-terraform
- InSpec: inspec.io
- Pulumi Testing: pulumi.com/docs/using-pulumi/testing
- AWS Testing: github.com/awslabs/aws-terraform-dev-platform
