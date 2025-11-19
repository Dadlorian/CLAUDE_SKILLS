# Pulumi Reference Guide

## Table of Contents
- [Introduction](#introduction)
- [Core Concepts](#core-concepts)
- [Supported Languages](#supported-languages)
- [Project Structure](#project-structure)
- [Resources](#resources)
- [Outputs](#outputs)
- [Configuration](#configuration)
- [Stacks](#stacks)
- [State Management](#state-management)
- [Pulumi vs Terraform](#pulumi-vs-terraform)
- [Best Practices](#best-practices)

## Introduction

### What is Pulumi?
Pulumi is a modern Infrastructure as Code platform that allows you to use familiar programming languages (TypeScript, Python, Go, C#, Java) to define cloud infrastructure. Unlike declarative tools like Terraform, Pulumi is imperative and leverages the full power of programming languages.

### Key Features
- Use real programming languages
- Type safety and IDE support
- Full access to language features (loops, conditionals, functions)
- Component model for reusable infrastructure
- Cross-cloud support (AWS, Azure, GCP, Kubernetes, etc.)
- State management with Pulumi Service or self-hosted backends

### Installation
```bash
# macOS
brew install pulumi/tap/pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows
choco install pulumi

# Verify installation
pulumi version
```

## Core Concepts

### Resources
The fundamental unit in Pulumi. Represents cloud infrastructure objects.

```typescript
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("my-bucket", {
    website: {
        indexDocument: "index.html",
    },
});
```

### Inputs and Outputs
- **Inputs**: Values passed to resources (can be concrete values or Outputs)
- **Outputs**: Values produced by resources (resolved asynchronously)

```typescript
// Input (concrete value)
const bucket = new aws.s3.Bucket("my-bucket", {
    bucket: "my-unique-bucket-name",
});

// Output
export const bucketName = bucket.id; // Output<string>

// Using an Output as an Input
const bucketObject = new aws.s3.BucketObject("index", {
    bucket: bucket.id,  // Output<string> used as Input
    content: "Hello, world!",
});
```

### Components
Reusable infrastructure abstractions that encapsulate multiple resources.

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export class StaticWebsite extends pulumi.ComponentResource {
    public readonly bucket: aws.s3.Bucket;
    public readonly bucketPolicy: aws.s3.BucketPolicy;
    public readonly url: pulumi.Output<string>;

    constructor(name: string, args: StaticWebsiteArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:StaticWebsite", name, {}, opts);

        this.bucket = new aws.s3.Bucket(`${name}-bucket`, {
            website: {
                indexDocument: args.indexDocument || "index.html",
            },
        }, { parent: this });

        this.bucketPolicy = new aws.s3.BucketPolicy(`${name}-policy`, {
            bucket: this.bucket.id,
            policy: this.bucket.arn.apply(arn => JSON.stringify({
                Version: "2012-10-17",
                Statement: [{
                    Effect: "Allow",
                    Principal: "*",
                    Action: "s3:GetObject",
                    Resource: `${arn}/*`,
                }],
            })),
        }, { parent: this });

        this.url = this.bucket.websiteEndpoint;

        this.registerOutputs({
            bucket: this.bucket,
            url: this.url,
        });
    }
}

interface StaticWebsiteArgs {
    indexDocument?: string;
}
```

### Stack
An isolated, independently configurable instance of a Pulumi program.

```bash
# Create a new stack
pulumi stack init dev

# Switch stacks
pulumi stack select prod

# List stacks
pulumi stack ls
```

## Supported Languages

### TypeScript
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("my-bucket");

export const bucketName = bucket.id;
```

### Python
```python
import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket("my-bucket")

pulumi.export("bucket_name", bucket.id)
```

### Go
```go
package main

import (
    "github.com/pulumi/pulumi-aws/sdk/v6/go/aws/s3"
    "github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
    pulumi.Run(func(ctx *pulumi.Context) error {
        bucket, err := s3.NewBucket(ctx, "my-bucket", nil)
        if err != nil {
            return err
        }

        ctx.Export("bucketName", bucket.ID())
        return nil
    })
}
```

### C#
```csharp
using Pulumi;
using Pulumi.Aws.S3;

class Program
{
    static Task<int> Main() => Deployment.RunAsync(() =>
    {
        var bucket = new Bucket("my-bucket");

        return new Dictionary<string, object?>
        {
            ["bucketName"] = bucket.Id
        };
    });
}
```

### Java
```java
package myproject;

import com.pulumi.Pulumi;
import com.pulumi.aws.s3.Bucket;

public class App {
    public static void main(String[] args) {
        Pulumi.run(ctx -> {
            var bucket = new Bucket("my-bucket");

            ctx.export("bucketName", bucket.id());
        });
    }
}
```

## Project Structure

### TypeScript Project
```
my-pulumi-project/
├── Pulumi.yaml           # Project configuration
├── Pulumi.dev.yaml       # Stack configuration (dev)
├── Pulumi.prod.yaml      # Stack configuration (prod)
├── package.json          # NPM dependencies
├── tsconfig.json         # TypeScript configuration
├── index.ts              # Main program
└── components/           # Custom components
    └── staticWebsite.ts
```

### Pulumi.yaml
```yaml
name: my-pulumi-project
runtime: nodejs
description: A Pulumi project for managing infrastructure
```

### package.json
```json
{
    "name": "my-pulumi-project",
    "version": "1.0.0",
    "dependencies": {
        "@pulumi/pulumi": "^3.0.0",
        "@pulumi/aws": "^6.0.0",
        "@pulumi/awsx": "^2.0.0"
    },
    "devDependencies": {
        "@types/node": "^20.0.0",
        "typescript": "^5.0.0"
    }
}
```

## Resources

### Creating Resources
```typescript
import * as aws from "@pulumi/aws";

// S3 Bucket
const bucket = new aws.s3.Bucket("my-bucket", {
    bucket: "my-unique-bucket-name",
    acl: "private",
    versioning: {
        enabled: true,
    },
    serverSideEncryptionConfiguration: {
        rule: {
            applyServerSideEncryptionByDefault: {
                sseAlgorithm: "AES256",
            },
        },
    },
    tags: {
        Environment: "dev",
        ManagedBy: "Pulumi",
    },
});

// EC2 Instance
const ami = aws.ec2.getAmi({
    mostRecent: true,
    owners: ["amazon"],
    filters: [{
        name: "name",
        values: ["amzn2-ami-hvm-*-x86_64-gp2"],
    }],
});

const instance = new aws.ec2.Instance("web-server", {
    ami: ami.then(ami => ami.id),
    instanceType: "t3.micro",
    tags: {
        Name: "web-server",
    },
});
```

### Resource Options
```typescript
// Explicit dependencies
const bucket = new aws.s3.Bucket("my-bucket");

const bucketObject = new aws.s3.BucketObject("index", {
    bucket: bucket.id,
    content: "Hello",
}, {
    dependsOn: [bucket],
});

// Parent-child relationships
class MyComponent extends pulumi.ComponentResource {
    constructor(name: string, opts?: pulumi.ComponentResourceOptions) {
        super("custom:MyComponent", name, {}, opts);

        const bucket = new aws.s3.Bucket(`${name}-bucket`, {}, {
            parent: this,  // Sets parent-child relationship
        });
    }
}

// Protect from deletion
const database = new aws.rds.Instance("db", {
    // ...
}, {
    protect: true,
});

// Ignore changes
const instance = new aws.ec2.Instance("web", {
    // ...
}, {
    ignoreChanges: ["tags", "userData"],
});

// Custom timeouts
const instance = new aws.ec2.Instance("web", {
    // ...
}, {
    customTimeouts: {
        create: "30m",
        update: "30m",
        delete: "30m",
    },
});

// Replace on changes
const instance = new aws.ec2.Instance("web", {
    // ...
}, {
    replaceOnChanges: ["instanceType"],
});

// Provider
const awsProvider = new aws.Provider("custom-aws", {
    region: "us-east-1",
});

const bucket = new aws.s3.Bucket("my-bucket", {}, {
    provider: awsProvider,
});
```

### Dynamic Providers
```typescript
import * as pulumi from "@pulumi/pulumi";

interface MyResourceInputs {
    data: pulumi.Input<string>;
}

interface MyResourceOutputs {
    id: string;
    data: string;
}

class MyResourceProvider implements pulumi.dynamic.ResourceProvider {
    async create(inputs: MyResourceInputs): Promise<pulumi.dynamic.CreateResult> {
        // Custom creation logic
        const id = "unique-id";
        return {
            id,
            outs: { id, data: inputs.data },
        };
    }

    async update(id: string, oldOutputs: MyResourceOutputs, newInputs: MyResourceInputs): Promise<pulumi.dynamic.UpdateResult> {
        // Custom update logic
        return {
            outs: { id, data: newInputs.data },
        };
    }

    async delete(id: string, props: MyResourceOutputs): Promise<void> {
        // Custom deletion logic
    }
}

class MyResource extends pulumi.dynamic.Resource {
    public readonly data!: pulumi.Output<string>;

    constructor(name: string, args: MyResourceInputs, opts?: pulumi.CustomResourceOptions) {
        super(new MyResourceProvider(), name, { data: args.data }, opts);
    }
}

// Usage
const resource = new MyResource("my-resource", {
    data: "Hello, World!",
});
```

## Outputs

### Working with Outputs
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("my-bucket");

// Export an Output directly
export const bucketName = bucket.id;

// Apply a transformation to an Output
export const bucketArn = bucket.arn.apply(arn => `ARN: ${arn}`);

// Combine multiple Outputs
const instance = new aws.ec2.Instance("web", {
    // ...
});

export const instanceInfo = pulumi.all([instance.id, instance.publicIp])
    .apply(([id, ip]) => `Instance ${id} is available at ${ip}`);

// Using Output in conditionals
const enableBackup = pulumi.output(true);
const backupBucket = enableBackup.apply(enabled =>
    enabled ? new aws.s3.Bucket("backup") : undefined
);

// Async operations with Outputs
const ami = pulumi.output(aws.ec2.getAmi({
    mostRecent: true,
    owners: ["amazon"],
    filters: [{
        name: "name",
        values: ["amzn2-ami-hvm-*"],
    }],
}));

const instance2 = new aws.ec2.Instance("web2", {
    ami: ami.id,
    instanceType: "t3.micro",
});

// Lifting operations
const bucket2 = new aws.s3.Bucket("my-bucket-2");
const upperCaseName = bucket2.id.apply(name => name.toUpperCase());

// JSON serialization
const config = pulumi.all([bucket.id, instance.publicIp]).apply(([bucketId, ip]) =>
    JSON.stringify({
        bucket: bucketId,
        instanceIp: ip,
    })
);
```

### Stack References
```typescript
import * as pulumi from "@pulumi/pulumi";

// Reference another stack's outputs
const stackRef = new pulumi.StackReference("organization/project/stack");

const vpcId = stackRef.getOutput("vpcId");
const subnetIds = stackRef.getOutput("subnetIds");

// Use in resources
const instance = new aws.ec2.Instance("web", {
    subnetId: subnetIds.apply(ids => ids[0]),
    // ...
});
```

## Configuration

### Setting Configuration
```bash
# Set config value
pulumi config set aws:region us-west-2

# Set secret (encrypted)
pulumi config set --secret dbPassword mySecretPassword123

# Set structured config
pulumi config set instanceConfig '{"type":"t3.micro","count":3}' --path

# Set config from file
pulumi config set-all --path config.json
```

### Pulumi.dev.yaml
```yaml
config:
  aws:region: us-west-2
  myproject:instanceType: t3.micro
  myproject:environment: dev
  myproject:dbPassword:
    secure: AAABADgXd8...  # Encrypted value
```

### Reading Configuration
```typescript
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();

// Get required config
const instanceType = config.require("instanceType");

// Get optional config with default
const region = config.get("region") || "us-west-2";

// Get secret
const dbPassword = config.requireSecret("dbPassword");

// Get numeric config
const instanceCount = config.requireNumber("instanceCount");

// Get boolean config
const enableBackup = config.getBoolean("enableBackup") || false;

// Get object config
interface InstanceConfig {
    type: string;
    count: number;
}
const instanceConfig = config.requireObject<InstanceConfig>("instanceConfig");

// AWS provider config
const awsConfig = new pulumi.Config("aws");
const awsRegion = awsConfig.require("region");
```

## Stacks

### Stack Management
```bash
# Create new stack
pulumi stack init staging

# List stacks
pulumi stack ls

# Select stack
pulumi stack select dev

# Get current stack info
pulumi stack

# View stack outputs
pulumi stack output

# View specific output
pulumi stack output vpcId

# Export stack state
pulumi stack export > stack-state.json

# Import stack state
pulumi stack import < stack-state.json

# Delete stack
pulumi stack rm dev
```

### Stack in Code
```typescript
import * as pulumi from "@pulumi/pulumi";

const stack = pulumi.getStack();  // "dev", "staging", "prod"
const project = pulumi.getProject();  // "my-project"

// Stack-specific configuration
const instanceType = stack === "prod" ? "t3.large" : "t3.micro";

const instance = new aws.ec2.Instance(`${stack}-web`, {
    instanceType: instanceType,
    tags: {
        Stack: stack,
        Project: project,
    },
});

// Stack tags
const stackTags = {
    "pulumi:stack": stack,
    "pulumi:project": project,
};
```

## State Management

### Pulumi Service (Default)
```bash
# Login to Pulumi Service
pulumi login

# View state
pulumi stack export

# Refresh state from actual infrastructure
pulumi refresh
```

### Self-Hosted Backend

#### Local Filesystem
```bash
# Login to local backend
pulumi login file://~/.pulumi/local

# Or set via environment
export PULUMI_BACKEND_URL=file://~/.pulumi/local
```

#### S3 Backend
```bash
# Login to S3 backend
pulumi login s3://my-pulumi-state-bucket

# With AWS profile
AWS_PROFILE=production pulumi login s3://my-pulumi-state-bucket
```

#### Azure Blob Storage
```bash
pulumi login azblob://my-pulumi-container
```

#### Google Cloud Storage
```bash
pulumi login gs://my-pulumi-bucket
```

### State Operations
```bash
# Refresh state from actual resources
pulumi refresh

# Import existing resource
pulumi import aws:s3/bucket:Bucket my-bucket my-existing-bucket

# Delete resource from state (without destroying)
pulumi state delete 'urn:pulumi:dev::myproject::aws:s3/bucket:Bucket::my-bucket'

# Unprotect resource
pulumi state unprotect 'urn:pulumi:dev::myproject::aws:rds/instance:Instance::db'

# Rename resource
pulumi state rename 'urn:pulumi:dev::myproject::aws:s3/bucket:Bucket::old' 'new'
```

## Pulumi vs Terraform

### Comparison

| Feature | Pulumi | Terraform |
|---------|--------|-----------|
| Language | TypeScript, Python, Go, C#, Java | HCL |
| Type Safety | Yes (with TypeScript, C#, Java, Go) | Limited |
| IDE Support | Full (IntelliSense, autocomplete) | Basic |
| Testing | Standard testing frameworks | Terratest, custom tools |
| State | Pulumi Service or self-hosted | Local or remote backends |
| Loops/Conditionals | Native language features | HCL constructs |
| Functions | Native language functions | Built-in functions only |
| Modules/Components | Language packages | HCL modules |
| Secrets | Built-in encryption | Requires external tools |

### Code Comparison

#### Terraform
```hcl
variable "instance_count" {
  type    = number
  default = 3
}

resource "aws_instance" "web" {
  count         = var.instance_count
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "web-${count.index}"
  }
}

output "instance_ids" {
  value = aws_instance.web[*].id
}
```

#### Pulumi (TypeScript)
```typescript
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const instanceCount = config.getNumber("instanceCount") || 3;

const instances: aws.ec2.Instance[] = [];
for (let i = 0; i < instanceCount; i++) {
    instances.push(new aws.ec2.Instance(`web-${i}`, {
        ami: "ami-12345678",
        instanceType: "t3.micro",
        tags: {
            Name: `web-${i}`,
        },
    }));
}

export const instanceIds = instances.map(i => i.id);
```

## Best Practices

### 1. Use Strong Typing
```typescript
// Define interfaces for configuration
interface WebServerConfig {
    instanceType: aws.ec2.InstanceType;
    minSize: number;
    maxSize: number;
}

// Type-safe configuration
const config = new pulumi.Config();
const webServerConfig = config.requireObject<WebServerConfig>("webServer");

// Type-safe resource creation
const instance = new aws.ec2.Instance("web", {
    instanceType: webServerConfig.instanceType,
    // TypeScript ensures you can't pass invalid values
});
```

### 2. Create Reusable Components
```typescript
export class WebApplication extends pulumi.ComponentResource {
    public readonly loadBalancer: aws.lb.LoadBalancer;
    public readonly targetGroup: aws.lb.TargetGroup;
    public readonly instances: aws.ec2.Instance[];
    public readonly url: pulumi.Output<string>;

    constructor(name: string, args: WebApplicationArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:WebApplication", name, {}, opts);

        // Create VPC
        const vpc = new aws.ec2.Vpc(`${name}-vpc`, {
            cidrBlock: args.vpcCidr,
        }, { parent: this });

        // Create subnets
        // Create security groups
        // Create load balancer
        // Create instances
        // ...

        this.registerOutputs({
            url: this.url,
        });
    }
}
```

### 3. Use Stack References for Multi-Stack Architectures
```typescript
// In networking stack
export const vpcId = vpc.id;
export const privateSubnetIds = privateSubnets.map(s => s.id);

// In application stack
const networkingStack = new pulumi.StackReference("organization/networking/prod");

const vpcId = networkingStack.requireOutput("vpcId");
const subnetIds = networkingStack.requireOutput("privateSubnetIds");
```

### 4. Proper Secret Management
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

const config = new pulumi.Config();

// Store secrets in Pulumi config
const dbPassword = config.requireSecret("dbPassword");

// Use secrets in resources
const db = new aws.rds.Instance("database", {
    password: dbPassword,  // Pulumi marks this as secret automatically
    // ...
});

// Create additional secrets
const apiKey = pulumi.secret("my-secret-api-key");

// Export secrets (they remain encrypted in state)
export const dbEndpoint = db.endpoint;  // Not secret
export const dbPasswordOutput = dbPassword;  // Remains secret
```

### 5. Implement Proper Tagging
```typescript
const defaultTags = {
    Project: pulumi.getProject(),
    Stack: pulumi.getStack(),
    ManagedBy: "Pulumi",
    CostCenter: config.require("costCenter"),
};

function createTaggedBucket(name: string, additionalTags: Record<string, string> = {}) {
    return new aws.s3.Bucket(name, {
        tags: {
            ...defaultTags,
            ...additionalTags,
        },
    });
}
```

### 6. Use Automation API for Advanced Workflows
```typescript
import * as pulumi from "@pulumi/pulumi/automation";

async function createStack(stackName: string, region: string) {
    const stack = await pulumi.LocalWorkspace.createOrSelectStack({
        stackName,
        projectName: "my-project",
        program: async () => {
            const bucket = new aws.s3.Bucket("my-bucket");
            return {
                bucketName: bucket.id,
            };
        },
    });

    await stack.setConfig("aws:region", { value: region });

    const upResult = await stack.up();
    console.log(`Stack ${stackName} created. Bucket: ${upResult.outputs.bucketName.value}`);
}
```

### 7. Testing Infrastructure Code
```typescript
import * as pulumi from "@pulumi/pulumi";
import "mocha";

pulumi.runtime.setMocks({
    newResource: function(args: pulumi.runtime.MockResourceArgs): {id: string, state: any} {
        return {
            id: args.inputs.name + "_id",
            state: args.inputs,
        };
    },
    call: function(args: pulumi.runtime.MockCallArgs) {
        return args.inputs;
    },
});

describe("Infrastructure", () => {
    let bucketName: pulumi.Output<string>;

    before(async () => {
        const infra = await import("./index");
        bucketName = infra.bucketName;
    });

    it("bucket name should be defined", (done) => {
        pulumi.all([bucketName]).apply(([name]) => {
            if (name) {
                done();
            } else {
                done(new Error("bucket name is undefined"));
            }
        });
    });
});
```

### 8. CI/CD Integration
```yaml
# GitHub Actions example
name: Pulumi
on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Pulumi preview
        uses: pulumi/actions@v4
        with:
          command: preview
          stack-name: dev
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Pulumi up
        uses: pulumi/actions@v4
        with:
          command: up
          stack-name: dev
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### 9. Resource Naming Conventions
```typescript
const prefix = `${pulumi.getProject()}-${pulumi.getStack()}`;

const bucket = new aws.s3.Bucket(`${prefix}-data`, {
    bucket: `${prefix}-data-${aws.getCallerIdentity().then(id => id.accountId)}`,
});

const instance = new aws.ec2.Instance(`${prefix}-web-${index}`, {
    tags: {
        Name: `${prefix}-web-${index}`,
    },
});
```

### 10. Error Handling
```typescript
try {
    const bucket = new aws.s3.Bucket("my-bucket", {
        bucket: "my-globally-unique-bucket-name",
    });

    export const bucketName = bucket.id;
} catch (error) {
    pulumi.log.error(`Failed to create bucket: ${error}`);
    throw error;
}

// Validation
const instanceType = config.require("instanceType");
const validTypes = ["t3.micro", "t3.small", "t3.medium"];

if (!validTypes.includes(instanceType)) {
    throw new Error(`Invalid instance type: ${instanceType}. Must be one of: ${validTypes.join(", ")}`);
}
```
