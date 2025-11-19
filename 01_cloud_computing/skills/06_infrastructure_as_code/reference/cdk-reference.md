# AWS CDK Reference

## Overview

AWS Cloud Development Kit (CDK) is an open-source software development framework for defining cloud infrastructure using familiar programming languages and synthesizing it to AWS CloudFormation templates.

## Core Concepts

### Constructs

Constructs are the basic building blocks of CDK applications. They represent cloud components and encapsulate everything AWS CloudFormation needs to create the component.

**Construct Levels**

**L1 Constructs (CFN Resources)**
```typescript
// Low-level, direct mapping to CloudFormation
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucket = new s3.CfnBucket(this, 'MyBucket', {
  bucketName: 'my-bucket-name',
  versioningConfiguration: {
    status: 'Enabled',
  },
});
```

**L2 Constructs (AWS Constructs)**
```typescript
// Intent-based API with sensible defaults
const bucket = new s3.Bucket(this, 'MyBucket', {
  bucketName: 'my-bucket-name',
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
  removalPolicy: cdk.RemovalPolicy.RETAIN,
});
```

**L3 Constructs (Patterns)**
```typescript
// High-level abstractions for common architectures
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';

const loadBalancedService = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'Service', {
  cluster: cluster,
  taskImageOptions: {
    image: ecs.ContainerImage.fromRegistry('amazon/amazon-ecs-sample'),
  },
});
```

### App Structure

```typescript
#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { MyStack } from '../lib/my-stack';

const app = new cdk.App();

new MyStack(app, 'DevStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-east-1',
  },
  tags: {
    Environment: 'dev',
  },
});

new MyStack(app, 'ProdStack', {
  env: {
    account: '123456789012',
    region: 'us-west-2',
  },
  tags: {
    Environment: 'prod',
  },
});
```

### Stack

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';

export interface MyStackProps extends cdk.StackProps {
  vpcCidr?: string;
  databaseName?: string;
}

export class MyStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  public readonly database: rds.DatabaseInstance;

  constructor(scope: Construct, id: string, props?: MyStackProps) {
    super(scope, id, props);

    // VPC
    this.vpc = new ec2.Vpc(this, 'VPC', {
      ipAddresses: ec2.IpAddresses.cidr(props?.vpcCidr || '10.0.0.0/16'),
      maxAzs: 3,
      natGateways: 1,
    });

    // Database
    this.database = new rds.DatabaseInstance(this, 'Database', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15_3,
      }),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      vpc: this.vpc,
      databaseName: props?.databaseName || 'mydb',
    });

    // Outputs
    new cdk.CfnOutput(this, 'VpcId', {
      value: this.vpc.vpcId,
      exportName: 'VPC-ID',
    });

    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: this.database.dbInstanceEndpointAddress,
    });
  }
}
```

## Common Patterns

### VPC with Subnets
```typescript
const vpc = new ec2.Vpc(this, 'VPC', {
  ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
  maxAzs: 3,
  natGateways: 1,
  subnetConfiguration: [
    {
      cidrMask: 24,
      name: 'Public',
      subnetType: ec2.SubnetType.PUBLIC,
    },
    {
      cidrMask: 24,
      name: 'Private',
      subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
    },
    {
      cidrMask: 28,
      name: 'Isolated',
      subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
    },
  ],
});
```

### Lambda Function
```typescript
import * as lambda from 'aws-cdk-lib/aws-lambda';

const fn = new lambda.Function(this, 'MyFunction', {
  runtime: lambda.Runtime.NODEJS_18_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
  environment: {
    TABLE_NAME: table.tableName,
  },
  timeout: cdk.Duration.seconds(30),
  memorySize: 512,
});

// Grant permissions
table.grantReadWriteData(fn);
bucket.grantRead(fn);
```

### API Gateway + Lambda
```typescript
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

const api = new apigateway.RestApi(this, 'Api', {
  restApiName: 'My API',
  description: 'My API Gateway',
});

const items = api.root.addResource('items');
items.addMethod('GET', new apigateway.LambdaIntegration(getItemsFn));
items.addMethod('POST', new apigateway.LambdaIntegration(createItemFn));

const item = items.addResource('{id}');
item.addMethod('GET', new apigateway.LambdaIntegration(getItemFn));
item.addMethod('PUT', new apigateway.LambdaIntegration(updateItemFn));
item.addMethod('DELETE', new apigateway.LambdaIntegration(deleteItemFn));
```

### ECS Fargate Service
```typescript
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';

const cluster = new ecs.Cluster(this, 'Cluster', {
  vpc: vpc,
  containerInsights: true,
});

const service = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'Service', {
  cluster: cluster,
  cpu: 512,
  memoryLimitMiB: 1024,
  desiredCount: 2,
  taskImageOptions: {
    image: ecs.ContainerImage.fromRegistry('nginx:latest'),
    containerPort: 80,
    environment: {
      ENV: 'production',
    },
  },
  publicLoadBalancer: true,
});

// Auto scaling
const scaling = service.service.autoScaleTaskCount({
  minCapacity: 2,
  maxCapacity: 10,
});

scaling.scaleOnCpuUtilization('CpuScaling', {
  targetUtilizationPercent: 70,
});
```

### S3 + CloudFront
```typescript
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';

const bucket = new s3.Bucket(this, 'WebsiteBucket', {
  encryption: s3.BucketEncryption.S3_MANAGED,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
  autoDeleteObjects: true,
});

const distribution = new cloudfront.Distribution(this, 'Distribution', {
  defaultBehavior: {
    origin: new origins.S3Origin(bucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
  },
  defaultRootObject: 'index.html',
  errorResponses: [
    {
      httpStatus: 404,
      responseHttpStatus: 200,
      responsePagePath: '/index.html',
    },
  ],
});

new s3deploy.BucketDeployment(this, 'DeployWebsite', {
  sources: [s3deploy.Source.asset('./website')],
  destinationBucket: bucket,
  distribution: distribution,
  distributionPaths: ['/*'],
});
```

## Context and Configuration

### cdk.json
```json
{
  "app": "npx ts-node --prefer-ts-exts bin/app.ts",
  "context": {
    "@aws-cdk/aws-apigateway:usagePlanKeyOrderInsensitiveId": true,
    "@aws-cdk/core:stackRelativeExports": true,
    "@aws-cdk/aws-rds:lowercaseDbIdentifier": true,
    "@aws-cdk/aws-lambda:recognizeVersionProps": true,
    "availability-zones:account=123456789012:region=us-east-1": [
      "us-east-1a",
      "us-east-1b",
      "us-east-1c"
    ]
  }
}
```

### Environment Variables
```typescript
const config = {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
};
```

### Context Values
```typescript
const app = new cdk.App();

// From command line: cdk deploy --context key=value
const value = app.node.tryGetContext('key');

// In stack
const stackValue = this.node.tryGetContext('stackKey');
```

## Aspects

```typescript
import { IAspect, IConstruct } from 'constructs';
import * as cdk from 'aws-cdk-lib';

class TagAspect implements IAspect {
  constructor(private key: string, private value: string) {}

  visit(node: IConstruct): void {
    if (cdk.TagManager.isTaggable(node)) {
      node.tags.setTag(this.key, this.value);
    }
  }
}

// Apply aspect
cdk.Aspects.of(app).add(new TagAspect('Environment', 'production'));
```

### Security Aspect
```typescript
class SecurityAspect implements IAspect {
  visit(node: IConstruct): void {
    // Ensure S3 buckets are encrypted
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        cdk.Annotations.of(node).addError('S3 bucket must be encrypted');
      }
    }

    // Ensure RDS instances are encrypted
    if (node instanceof rds.CfnDBInstance) {
      if (!node.storageEncrypted) {
        cdk.Annotations.of(node).addError('RDS instance must be encrypted');
      }
    }
  }
}
```

## Custom Constructs

```typescript
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as autoscaling from 'aws-cdk-lib/aws-autoscaling';

export interface WebServerFleetProps {
  vpc: ec2.IVpc;
  instanceType?: ec2.InstanceType;
  minCapacity?: number;
  maxCapacity?: number;
}

export class WebServerFleet extends Construct {
  public readonly loadBalancer: elbv2.ApplicationLoadBalancer;
  public readonly autoScalingGroup: autoscaling.AutoScalingGroup;

  constructor(scope: Construct, id: string, props: WebServerFleetProps) {
    super(scope, id);

    // Security Group
    const securityGroup = new ec2.SecurityGroup(this, 'SecurityGroup', {
      vpc: props.vpc,
      description: 'Security group for web server fleet',
      allowAllOutbound: true,
    });

    securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      'Allow HTTP traffic'
    );

    // Auto Scaling Group
    this.autoScalingGroup = new autoscaling.AutoScalingGroup(this, 'ASG', {
      vpc: props.vpc,
      instanceType: props.instanceType || ec2.InstanceType.of(
        ec2.InstanceClass.T3,
        ec2.InstanceSize.MICRO
      ),
      machineImage: new ec2.AmazonLinuxImage({
        generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
      }),
      minCapacity: props.minCapacity || 2,
      maxCapacity: props.maxCapacity || 10,
      securityGroup: securityGroup,
    });

    // User data
    this.autoScalingGroup.addUserData(
      '#!/bin/bash',
      'yum update -y',
      'yum install -y httpd',
      'systemctl start httpd',
      'systemctl enable httpd',
      'echo "<h1>Hello from CDK!</h1>" > /var/www/html/index.html'
    );

    // Load Balancer
    this.loadBalancer = new elbv2.ApplicationLoadBalancer(this, 'ALB', {
      vpc: props.vpc,
      internetFacing: true,
    });

    const listener = this.loadBalancer.addListener('Listener', {
      port: 80,
    });

    listener.addTargets('Target', {
      port: 80,
      targets: [this.autoScalingGroup],
      healthCheck: {
        path: '/',
        interval: cdk.Duration.seconds(30),
      },
    });

    // Outputs
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: this.loadBalancer.loadBalancerDnsName,
    });
  }
}

// Usage
const webFleet = new WebServerFleet(this, 'WebFleet', {
  vpc: vpc,
  minCapacity: 2,
  maxCapacity: 10,
});
```

## Testing

### Unit Tests
```typescript
import { Template, Match } from 'aws-cdk-lib/assertions';
import * as cdk from 'aws-cdk-lib';
import { MyStack } from '../lib/my-stack';

test('VPC Created', () => {
  const app = new cdk.App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::EC2::VPC', {
    CidrBlock: '10.0.0.0/16',
    EnableDnsHostnames: true,
  });
});

test('S3 Bucket Encrypted', () => {
  const app = new cdk.App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::S3::Bucket', {
    BucketEncryption: {
      ServerSideEncryptionConfiguration: [
        {
          ServerSideEncryptionByDefault: {
            SSEAlgorithm: 'AES256',
          },
        },
      ],
    },
  });
});

test('Lambda Has Correct Environment Variables', () => {
  const app = new cdk.App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::Lambda::Function', {
    Environment: {
      Variables: Match.objectLike({
        TABLE_NAME: Match.anyValue(),
      }),
    },
  });
});

test('Snapshot Test', () => {
  const app = new cdk.App();
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  expect(template.toJSON()).toMatchSnapshot();
});
```

### Integration Tests
```typescript
import { IntegTest } from '@aws-cdk/integ-tests-alpha';
import * as cdk from 'aws-cdk-lib';
import { MyStack } from '../lib/my-stack';

const app = new cdk.App();
const stack = new MyStack(app, 'IntegTestStack');

new IntegTest(app, 'MyIntegTest', {
  testCases: [stack],
  diffAssets: true,
});
```

## CLI Commands

```bash
# Initialize new project
cdk init app --language typescript
cdk init app --language python
cdk init app --language java
cdk init app --language csharp

# Install dependencies
npm install @aws-cdk/aws-s3
pip install aws-cdk.aws-s3

# List stacks
cdk list
cdk ls

# Synthesize CloudFormation
cdk synth
cdk synth StackName

# Compare changes
cdk diff
cdk diff StackName

# Deploy
cdk deploy
cdk deploy StackName
cdk deploy --all
cdk deploy --require-approval never

# Destroy
cdk destroy
cdk destroy StackName
cdk destroy --all

# Bootstrap
cdk bootstrap
cdk bootstrap aws://123456789012/us-east-1

# Watch mode (hot reload)
cdk watch
cdk watch StackName

# Context
cdk context
cdk context --clear

# Doctor (troubleshooting)
cdk doctor

# Metadata
cdk metadata
```

## Best Practices

### Use L2/L3 Constructs
```typescript
// Good: L2 construct with sensible defaults
const bucket = new s3.Bucket(this, 'MyBucket', {
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
});

// Avoid: L1 construct requiring all properties
const cfnBucket = new s3.CfnBucket(this, 'MyBucket', {
  versioningConfiguration: { status: 'Enabled' },
  bucketEncryption: {
    serverSideEncryptionConfiguration: [{
      serverSideEncryptionByDefault: {
        sseAlgorithm: 'AES256',
      },
    }],
  },
});
```

### Separation of Concerns
```typescript
// Good: Separate stacks
export class NetworkStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  // Network resources only
}

export class ComputeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, networkStack: NetworkStack) {
    super(scope, id);
    // Use networkStack.vpc
  }
}

// Usage
const networkStack = new NetworkStack(app, 'Network');
const computeStack = new ComputeStack(app, 'Compute', networkStack);
```

### Environment Agnostic
```typescript
// Good: Use tokens
const bucket = new s3.Bucket(this, 'MyBucket', {
  bucketName: `my-app-${cdk.Stack.of(this).account}-${cdk.Stack.of(this).region}`,
});

// Avoid: Hardcoding
const bucket = new s3.Bucket(this, 'MyBucket', {
  bucketName: 'my-app-123456789012-us-east-1',
});
```

### Tagging Strategy
```typescript
cdk.Tags.of(app).add('Project', 'MyProject');
cdk.Tags.of(app).add('ManagedBy', 'CDK');

// Stack-specific
cdk.Tags.of(stack).add('Environment', 'production');
```

## Troubleshooting

### Debug
```bash
# Verbose output
cdk deploy --verbose

# Debug logs
cdk synth --debug

# CloudFormation console logs
aws cloudformation describe-stack-events --stack-name StackName
```

### Common Issues

**Bootstrap Issues**
```bash
# Re-bootstrap
cdk bootstrap --force
```

**Asset Issues**
```bash
# Clear asset cache
rm -rf cdk.out
cdk synth
```

**Context Issues**
```bash
# Clear context
cdk context --clear
```

## Resources

- CDK Developer Guide: docs.aws.amazon.com/cdk
- API Reference: docs.aws.amazon.com/cdk/api/latest
- Construct Hub: constructs.dev
- CDK Patterns: cdkpatterns.com
- Examples: github.com/aws-samples/aws-cdk-examples
- Workshop: cdkworkshop.com
