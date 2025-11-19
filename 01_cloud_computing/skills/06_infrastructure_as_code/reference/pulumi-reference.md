# Pulumi Reference

## Overview

Pulumi is a modern Infrastructure as Code platform that allows you to use familiar programming languages (TypeScript, Python, Go, C#, Java) to define and manage cloud infrastructure.

## Core Concepts

### Programs vs Declarative Config

Pulumi uses imperative programming languages but maintains declarative infrastructure semantics through its resource model.

**TypeScript Example**
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// Create a VPC
const vpc = new aws.ec2.Vpc("main", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    tags: {
        Name: "main-vpc",
    },
});

// Export VPC ID
export const vpcId = vpc.id;
```

**Python Example**
```python
import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("main",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    tags={
        "Name": "main-vpc",
    }
)

# Export VPC ID
pulumi.export("vpc_id", vpc.id)
```

### Resource Model

**Resource Declaration**
```typescript
const bucket = new aws.s3.Bucket("my-bucket", {
    bucket: "my-unique-bucket-name",
    acl: "private",
    versioning: {
        enabled: true,
    },
    tags: {
        Environment: "production",
    },
});
```

**Resource Options**
```typescript
const instance = new aws.ec2.Instance("web", {
    ami: "ami-12345678",
    instanceType: "t3.micro",
}, {
    dependsOn: [securityGroup],
    protect: true,
    deleteBeforeReplace: true,
    ignoreChanges: ["tags"],
    parent: parentResource,
    provider: awsProvider,
    customTimeouts: {
        create: "30m",
        update: "30m",
        delete: "30m",
    },
});
```

## Languages

### TypeScript

**Project Structure**
```
my-project/
├── index.ts
├── package.json
├── tsconfig.json
├── Pulumi.yaml
├── Pulumi.dev.yaml
└── Pulumi.prod.yaml
```

**index.ts**
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// Configuration
const config = new pulumi.Config();
const instanceType = config.get("instanceType") || "t3.micro";
const environment = pulumi.getStack();

// Component Resource
class WebServer extends pulumi.ComponentResource {
    public readonly instance: aws.ec2.Instance;
    public readonly publicIp: pulumi.Output<string>;

    constructor(name: string, args: WebServerArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:WebServer", name, {}, opts);

        // Security Group
        const securityGroup = new aws.ec2.SecurityGroup(`${name}-sg`, {
            description: "Allow HTTP and SSH",
            vpcId: args.vpcId,
            ingress: [
                { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] },
                { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
            ],
            egress: [
                { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
            ],
        }, { parent: this });

        // EC2 Instance
        this.instance = new aws.ec2.Instance(`${name}-instance`, {
            ami: args.ami,
            instanceType: args.instanceType,
            vpcSecurityGroupIds: [securityGroup.id],
            subnetId: args.subnetId,
            tags: {
                Name: `${name}-instance`,
                Environment: environment,
            },
        }, { parent: this });

        this.publicIp = this.instance.publicIp;

        this.registerOutputs({
            instance: this.instance,
            publicIp: this.publicIp,
        });
    }
}

interface WebServerArgs {
    vpcId: pulumi.Input<string>;
    subnetId: pulumi.Input<string>;
    ami: pulumi.Input<string>;
    instanceType: pulumi.Input<string>;
}

// Usage
const webServer = new WebServer("my-web-server", {
    vpcId: vpc.id,
    subnetId: subnet.id,
    ami: "ami-12345678",
    instanceType: instanceType,
});

export const webServerIp = webServer.publicIp;
```

### Python

**Project Structure**
```
my-project/
├── __main__.py
├── requirements.txt
├── Pulumi.yaml
├── Pulumi.dev.yaml
└── venv/
```

**__main__.py**
```python
import pulumi
import pulumi_aws as aws
from typing import Optional

# Configuration
config = pulumi.Config()
instance_type = config.get("instanceType") or "t3.micro"
environment = pulumi.get_stack()

# Component Resource
class WebServerArgs:
    def __init__(self,
                 vpc_id: pulumi.Input[str],
                 subnet_id: pulumi.Input[str],
                 ami: pulumi.Input[str],
                 instance_type: pulumi.Input[str]):
        self.vpc_id = vpc_id
        self.subnet_id = subnet_id
        self.ami = ami
        self.instance_type = instance_type

class WebServer(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 args: WebServerArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("custom:WebServer", name, {}, opts)

        # Security Group
        security_group = aws.ec2.SecurityGroup(
            f"{name}-sg",
            description="Allow HTTP and SSH",
            vpc_id=args.vpc_id,
            ingress=[
                {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
                {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
            ],
            egress=[
                {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )

        # EC2 Instance
        self.instance = aws.ec2.Instance(
            f"{name}-instance",
            ami=args.ami,
            instance_type=args.instance_type,
            vpc_security_group_ids=[security_group.id],
            subnet_id=args.subnet_id,
            tags={
                "Name": f"{name}-instance",
                "Environment": environment,
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.public_ip = self.instance.public_ip

        self.register_outputs({
            "instance": self.instance,
            "public_ip": self.public_ip,
        })

# Usage
web_server = WebServer("my-web-server", WebServerArgs(
    vpc_id=vpc.id,
    subnet_id=subnet.id,
    ami="ami-12345678",
    instance_type=instance_type,
))

pulumi.export("web_server_ip", web_server.public_ip)
```

### Go

**main.go**
```go
package main

import (
    "github.com/pulumi/pulumi-aws/sdk/v6/go/aws/ec2"
    "github.com/pulumi/pulumi/sdk/v3/go/pulumi"
    "github.com/pulumi/pulumi/sdk/v3/go/pulumi/config"
)

func main() {
    pulumi.Run(func(ctx *pulumi.Context) error {
        // Configuration
        cfg := config.New(ctx, "")
        instanceType := "t3.micro"
        if param := cfg.Get("instanceType"); param != "" {
            instanceType = param
        }

        // Create VPC
        vpc, err := ec2.NewVpc(ctx, "main", &ec2.VpcArgs{
            CidrBlock:          pulumi.String("10.0.0.0/16"),
            EnableDnsHostnames: pulumi.Bool(true),
            Tags: pulumi.StringMap{
                "Name": pulumi.String("main-vpc"),
            },
        })
        if err != nil {
            return err
        }

        // Create Subnet
        subnet, err := ec2.NewSubnet(ctx, "public", &ec2.SubnetArgs{
            VpcId:     vpc.ID(),
            CidrBlock: pulumi.String("10.0.1.0/24"),
            Tags: pulumi.StringMap{
                "Name": pulumi.String("public-subnet"),
            },
        })
        if err != nil {
            return err
        }

        // Create Security Group
        sg, err := ec2.NewSecurityGroup(ctx, "web-sg", &ec2.SecurityGroupArgs{
            VpcId: vpc.ID(),
            Ingress: ec2.SecurityGroupIngressArray{
                &ec2.SecurityGroupIngressArgs{
                    Protocol:   pulumi.String("tcp"),
                    FromPort:   pulumi.Int(80),
                    ToPort:     pulumi.Int(80),
                    CidrBlocks: pulumi.StringArray{pulumi.String("0.0.0.0/0")},
                },
            },
        })
        if err != nil {
            return err
        }

        // Create Instance
        instance, err := ec2.NewInstance(ctx, "web", &ec2.InstanceArgs{
            Ami:                  pulumi.String("ami-12345678"),
            InstanceType:         pulumi.String(instanceType),
            SubnetId:             subnet.ID(),
            VpcSecurityGroupIds:  pulumi.StringArray{sg.ID()},
        })
        if err != nil {
            return err
        }

        // Export outputs
        ctx.Export("vpcId", vpc.ID())
        ctx.Export("instanceIp", instance.PublicIp)

        return nil
    })
}
```

## Configuration & Secrets

### Configuration
```typescript
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();

// Get configuration values
const instanceType = config.get("instanceType") || "t3.micro";
const requiredValue = config.require("apiKey");
const numericValue = config.getNumber("maxInstances") || 10;
const boolValue = config.getBoolean("enableMonitoring") || false;
const objectValue = config.getObject<DatabaseConfig>("database");

// Secrets
const dbPassword = config.requireSecret("dbPassword");
```

**Configuration Files**
```yaml
# Pulumi.yaml (project config)
name: my-infrastructure
runtime: nodejs
description: My infrastructure project

# Pulumi.dev.yaml (stack config)
config:
  aws:region: us-east-1
  my-infrastructure:instanceType: t3.micro
  my-infrastructure:maxInstances: "10"
  my-infrastructure:enableMonitoring: "true"

# Pulumi.prod.yaml
config:
  aws:region: us-west-2
  my-infrastructure:instanceType: t3.large
  my-infrastructure:maxInstances: "50"
  my-infrastructure:dbPassword:
    secure: AAABAKLSKJDLKJASDLKJASDasdfasdf...
```

### Secrets Management
```bash
# Set secret
pulumi config set --secret dbPassword mySecurePassword123

# Set from file
cat password.txt | pulumi config set --secret dbPassword

# Use secrets in code
```

```typescript
const dbPassword = config.requireSecret("dbPassword");

const db = new aws.rds.Instance("database", {
    engine: "postgres",
    instanceClass: "db.t3.micro",
    password: dbPassword,  // Automatically encrypted in state
});
```

## Outputs and Inputs

### Output Type
```typescript
// Outputs represent eventual values
const bucket = new aws.s3.Bucket("my-bucket");
const bucketName: pulumi.Output<string> = bucket.id;

// Apply transformation to output
const bucketUrl = bucket.id.apply(id => `https://${id}.s3.amazonaws.com`);

// Combine multiple outputs
const combined = pulumi.all([bucket1.id, bucket2.id]).apply(([id1, id2]) => {
    return `${id1}-${id2}`;
});

// Export outputs
export const bucketEndpoint = bucketUrl;
```

### Input Type
```typescript
// Inputs accept both concrete values and Outputs
function createInstance(name: pulumi.Input<string>,
                       subnetId: pulumi.Input<string>) {
    return new aws.ec2.Instance(name, {
        ami: "ami-12345678",
        instanceType: "t3.micro",
        subnetId: subnetId,  // Can be string or Output<string>
    });
}

// Works with concrete value
createInstance("web1", "subnet-12345");

// Works with Output
createInstance("web2", subnet.id);
```

## Stack References

```typescript
import * as pulumi from "@pulumi/pulumi";

// Reference another stack
const stackRef = new pulumi.StackReference("organization/project/stack");

// Get outputs from referenced stack
const vpcId = stackRef.getOutput("vpcId");
const subnetIds = stackRef.requireOutput("subnetIds");

// Use in current stack
const instance = new aws.ec2.Instance("web", {
    ami: "ami-12345678",
    instanceType: "t3.micro",
    subnetId: subnetIds.apply(ids => ids[0]),
});
```

## Dynamic Providers

```typescript
import * as pulumi from "@pulumi/pulumi";

interface MyResourceInputs {
    name: pulumi.Input<string>;
    value: pulumi.Input<string>;
}

interface MyResourceOutputs {
    id: string;
    name: string;
    value: string;
}

class MyResourceProvider implements pulumi.dynamic.ResourceProvider {
    async create(inputs: MyResourceInputs): Promise<pulumi.dynamic.CreateResult> {
        // Implement resource creation logic
        const id = `my-resource-${Date.now()}`;

        // Call external API, run commands, etc.
        console.log(`Creating resource: ${inputs.name}`);

        return {
            id: id,
            outs: {
                id: id,
                name: inputs.name,
                value: inputs.value,
            },
        };
    }

    async update(id: string, olds: MyResourceOutputs, news: MyResourceInputs): Promise<pulumi.dynamic.UpdateResult> {
        console.log(`Updating resource: ${id}`);
        return {
            outs: {
                id: id,
                name: news.name,
                value: news.value,
            },
        };
    }

    async delete(id: string, props: MyResourceOutputs): Promise<void> {
        console.log(`Deleting resource: ${id}`);
    }

    async read(id: string, props: MyResourceOutputs): Promise<pulumi.dynamic.ReadResult> {
        return {
            id: id,
            props: props,
        };
    }
}

class MyResource extends pulumi.dynamic.Resource {
    public readonly name!: pulumi.Output<string>;
    public readonly value!: pulumi.Output<string>;

    constructor(name: string, args: MyResourceInputs, opts?: pulumi.CustomResourceOptions) {
        super(new MyResourceProvider(), name, args, opts);
    }
}

// Usage
const resource = new MyResource("my-custom-resource", {
    name: "test",
    value: "custom value",
});
```

## Automation API

```typescript
import * as pulumi from "@pulumi/pulumi/automation";

async function deployStack() {
    // Define inline Pulumi program
    const program = async () => {
        const bucket = new aws.s3.Bucket("my-bucket");
        return {
            bucketName: bucket.id,
        };
    };

    // Create or select stack
    const stack = await pulumi.LocalWorkspace.createOrSelectStack({
        stackName: "dev",
        projectName: "my-project",
        program: program,
    });

    // Set configuration
    await stack.setConfig("aws:region", { value: "us-east-1" });

    // Preview changes
    const previewResult = await stack.preview();
    console.log(`Preview summary: ${JSON.stringify(previewResult.changeSummary)}`);

    // Deploy
    const upResult = await stack.up();
    console.log(`Update summary: ${JSON.stringify(upResult.summary)}`);
    console.log(`Outputs: ${JSON.stringify(upResult.outputs)}`);
}

deployStack();
```

## Testing

### Unit Tests (TypeScript)
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import "mocha";
import { expect } from "chai";

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

describe("Infrastructure", function() {
    let resources: any;

    before(async function() {
        resources = await import("./index");
    });

    it("should create a bucket with versioning enabled", function(done) {
        pulumi.all([resources.bucket.urn, resources.bucket.versioning]).apply(([urn, versioning]) => {
            expect(urn).to.contain("aws:s3/bucket:Bucket");
            expect(versioning.enabled).to.equal(true);
            done();
        });
    });

    it("should have correct tags", function(done) {
        resources.bucket.tags.apply((tags: any) => {
            expect(tags).to.have.property("Environment");
            expect(tags.Environment).to.equal("production");
            done();
        });
    });
});
```

### Integration Tests (Python)
```python
import unittest
import pulumi

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + '_id', args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

pulumi.runtime.set_mocks(MyMocks())

# Import your infrastructure module
import infra

class TestInfrastructure(unittest.TestCase):
    @pulumi.runtime.test
    def test_vpc_cidr(self):
        def check_cidr(args):
            cidr_block = args[0]
            self.assertEqual(cidr_block, "10.0.0.0/16")

        return infra.vpc.cidr_block.apply(check_cidr)

    @pulumi.runtime.test
    def test_instance_type(self):
        def check_type(args):
            instance_type = args[0]
            self.assertIn(instance_type, ["t3.micro", "t3.small", "t3.medium"])

        return infra.instance.instance_type.apply(check_type)
```

## CLI Commands

```bash
# New project
pulumi new aws-typescript
pulumi new aws-python
pulumi new kubernetes-go

# Stack management
pulumi stack init dev
pulumi stack select prod
pulumi stack ls
pulumi stack rm dev
pulumi stack export > stack.json
pulumi stack import < stack.json

# Configuration
pulumi config set aws:region us-east-1
pulumi config set --secret dbPassword myPassword
pulumi config get instanceType
pulumi config

# Preview and deploy
pulumi preview
pulumi up
pulumi up --yes
pulumi up --target urn
pulumi up --refresh

# Destroy
pulumi destroy
pulumi destroy --yes
pulumi destroy --target urn

# State management
pulumi refresh
pulumi state delete urn
pulumi state unprotect urn

# Outputs
pulumi stack output
pulumi stack output vpcId
pulumi stack output --json

# Import resources
pulumi import aws:s3/bucket:Bucket my-bucket my-bucket-name

# Policy
pulumi policy new aws-typescript
pulumi policy publish
pulumi policy enable

# Logs
pulumi logs
pulumi logs --follow

# Plugin management
pulumi plugin ls
pulumi plugin install resource aws 5.0.0
pulumi plugin rm resource aws 4.0.0

# Cancel update
pulumi cancel
```

## Best Practices

### Component Resources
```typescript
export class VpcStack extends pulumi.ComponentResource {
    public readonly vpc: aws.ec2.Vpc;
    public readonly publicSubnets: aws.ec2.Subnet[];
    public readonly privateSubnets: aws.ec2.Subnet[];

    constructor(name: string, args: VpcStackArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:VpcStack", name, {}, opts);

        // Create VPC
        this.vpc = new aws.ec2.Vpc(`${name}-vpc`, {
            cidrBlock: args.cidrBlock,
            enableDnsHostnames: true,
            enableDnsSupport: true,
        }, { parent: this });

        // Create subnets
        this.publicSubnets = args.availabilityZones.map((az, i) => {
            return new aws.ec2.Subnet(`${name}-public-${az}`, {
                vpcId: this.vpc.id,
                cidrBlock: args.publicSubnetCidrs[i],
                availabilityZone: az,
                mapPublicIpOnLaunch: true,
            }, { parent: this });
        });

        this.privateSubnets = args.availabilityZones.map((az, i) => {
            return new aws.ec2.Subnet(`${name}-private-${az}`, {
                vpcId: this.vpc.id,
                cidrBlock: args.privateSubnetCidrs[i],
                availabilityZone: az,
            }, { parent: this });
        });

        this.registerOutputs({
            vpcId: this.vpc.id,
            publicSubnetIds: this.publicSubnets.map(s => s.id),
            privateSubnetIds: this.privateSubnets.map(s => s.id),
        });
    }
}
```

### Strong Typing
```typescript
interface DatabaseConfig {
    engine: "postgres" | "mysql";
    instanceClass: string;
    allocatedStorage: number;
}

const dbConfig = config.requireObject<DatabaseConfig>("database");

// Type-safe usage
const db = new aws.rds.Instance("database", {
    engine: dbConfig.engine,
    instanceClass: dbConfig.instanceClass,
    allocatedStorage: dbConfig.allocatedStorage,
});
```

### Error Handling
```typescript
try {
    const instance = new aws.ec2.Instance("web", {
        ami: pulumi.output(getAmi()).apply(ami => {
            if (!ami) {
                throw new Error("AMI not found");
            }
            return ami;
        }),
        instanceType: "t3.micro",
    });
} catch (error) {
    pulumi.log.error(`Failed to create instance: ${error}`);
    throw error;
}
```

## Resources

- Official Documentation: pulumi.com/docs
- Registry: pulumi.com/registry
- Examples: github.com/pulumi/examples
- Community: pulumi.com/community
- Blog: pulumi.com/blog
