# AWS CloudFormation Reference

## Overview

AWS CloudFormation is Amazon's native Infrastructure as Code service that allows you to model and provision AWS resources using templates written in JSON or YAML.

## Template Anatomy

### Basic Structure
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: String describing the template

Metadata:
  # Template metadata

Parameters:
  # Input parameters

Mappings:
  # Static variables/lookups

Conditions:
  # Conditional resource creation

Transform:
  # Macros (e.g., AWS::Serverless)

Resources:
  # AWS resources (REQUIRED)

Outputs:
  # Output values
```

### Complete Example
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: VPC with public and private subnets

Parameters:
  EnvironmentName:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Environment name

  VpcCIDR:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: ^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$
    Description: VPC CIDR block

Mappings:
  EnvironmentMap:
    dev:
      InstanceType: t3.micro
      MinSize: 1
      MaxSize: 2
    prod:
      InstanceType: t3.large
      MinSize: 2
      MaxSize: 10

Conditions:
  IsProduction: !Equals [!Ref EnvironmentName, prod]
  CreateNATGateway: !Or
    - !Equals [!Ref EnvironmentName, staging]
    - !Equals [!Ref EnvironmentName, prod]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCIDR
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc
        - Key: Environment
          Value: !Ref EnvironmentName

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-igw

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Cidr [!Ref VpcCIDR, 6, 8]]
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-public-subnet-1

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VPC-ID

  PublicSubnet1Id:
    Description: Public Subnet 1 ID
    Value: !Ref PublicSubnet1
    Export:
      Name: !Sub ${EnvironmentName}-PublicSubnet1-ID
```

## Parameters

### Parameter Types
```yaml
Parameters:
  # String
  EnvironmentName:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    MinLength: 1
    MaxLength: 255
    ConstraintDescription: Must be a valid environment name

  # Number
  InstanceCount:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 10

  # List of numbers
  Ports:
    Type: List<Number>
    Default: "80,443,8080"

  # CommaDelimitedList
  SubnetIds:
    Type: CommaDelimitedList
    Default: "subnet-12345,subnet-67890"

  # AWS-Specific parameter types
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair

  SubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: Subnet ID

  SecurityGroupIds:
    Type: List<AWS::EC2::SecurityGroup::Id>
    Description: Security Group IDs

  ImageId:
    Type: AWS::EC2::Image::Id
    Default: ami-0c55b159cbfafe1f0

  # SSM Parameter
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

  # Secret
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    MaxLength: 41
    AllowedPattern: ^[a-zA-Z0-9]*$
```

## Intrinsic Functions

### Ref
```yaml
# Reference parameter or resource
VpcId: !Ref VPC
InstanceType: !Ref InstanceTypeParameter
```

### GetAtt
```yaml
# Get resource attribute
InstancePrivateIp: !GetAtt EC2Instance.PrivateIp
BucketArn: !GetAtt S3Bucket.Arn
LoadBalancerDNS: !GetAtt LoadBalancer.DNSName
```

### Sub
```yaml
# String substitution
Name: !Sub ${EnvironmentName}-vpc
ComplexString: !Sub
  - 'arn:aws:s3:::${BucketName}/*'
  - BucketName: !Ref MyBucket
MultiLine: !Sub |
  #!/bin/bash
  echo "Environment: ${EnvironmentName}"
  echo "Region: ${AWS::Region}"
```

### Join
```yaml
# Join strings with delimiter
SecurityGroupDescription: !Join
  - ' '
  - - 'Security group for'
    - !Ref EnvironmentName
    - 'environment'

# Result: "Security group for prod environment"
```

### Split
```yaml
# Split string into list
SubnetList: !Split [',', !Ref SubnetString]
```

### Select
```yaml
# Select item from list
FirstAZ: !Select [0, !GetAZs '']
SecondSubnet: !Select [1, !Ref SubnetIds]
```

### GetAZs
```yaml
# Get availability zones
AllAZs: !GetAZs ''
RegionAZs: !GetAZs us-east-1
```

### Cidr
```yaml
# Generate CIDR blocks
# !Cidr [ipBlock, count, cidrBits]
Subnets: !Cidr [!Ref VpcCIDR, 6, 8]
# Generates 6 subnets with /24 mask from /16 VPC
```

### FindInMap
```yaml
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    us-west-2:
      AMI: ami-0d1cd67c26f5fca19

Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]
```

### Condition Functions
```yaml
Conditions:
  IsProduction: !Equals [!Ref EnvironmentName, prod]
  IsNotProduction: !Not [!Condition IsProduction]
  IsUSRegion: !Or
    - !Equals [!Ref 'AWS::Region', us-east-1]
    - !Equals [!Ref 'AWS::Region', us-west-2]
  CreateResource: !And
    - !Condition IsProduction
    - !Condition IsUSRegion

Resources:
  ConditionalResource:
    Type: AWS::EC2::Instance
    Condition: CreateResource
    Properties:
      ImageId: ami-12345678
      InstanceType: !If [IsProduction, t3.large, t3.micro]
```

### ImportValue
```yaml
# Import exported value from another stack
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      SubnetId: !ImportValue prod-PublicSubnet1-ID
      SecurityGroupIds:
        - !ImportValue prod-WebSecurityGroup-ID
```

### Base64
```yaml
# Encode to Base64 (useful for UserData)
UserData: !Base64
  !Sub |
    #!/bin/bash
    yum update -y
    echo "Environment: ${EnvironmentName}" > /etc/environment
```

## Pseudo Parameters

```yaml
# AWS::AccountId - Account ID
!Ref AWS::AccountId

# AWS::Region - Region
!Ref AWS::Region

# AWS::StackId - Stack ID
!Ref AWS::StackId

# AWS::StackName - Stack name
!Ref AWS::StackName

# AWS::NotificationARNs - Notification ARNs
!Ref AWS::NotificationARNs

# AWS::NoValue - Remove property
!If [Condition, Value, !Ref 'AWS::NoValue']

# AWS::Partition - Partition (aws, aws-cn, aws-us-gov)
!Sub 'arn:${AWS::Partition}:s3:::bucket-name'

# AWS::URLSuffix - Domain suffix (amazonaws.com)
!Sub 'https://s3.${AWS::Region}.${AWS::URLSuffix}/bucket'
```

## Nested Stacks

### Parent Stack
```yaml
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/network-stack.yaml
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VpcCIDR: !Ref VpcCIDR
      Tags:
        - Key: Name
          Value: NetworkStack

  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/application-stack.yaml
      Parameters:
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
        SubnetIds: !GetAtt NetworkStack.Outputs.SubnetIds

Outputs:
  NetworkVPCId:
    Value: !GetAtt NetworkStack.Outputs.VPCId
  AppLoadBalancerDNS:
    Value: !GetAtt ApplicationStack.Outputs.LoadBalancerDNS
```

## StackSets

### StackSet Template
```yaml
# No special syntax required in template
# Same as regular CloudFormation template
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  SecurityAuditRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: sts:AssumeRole
```

### CLI Commands
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://template.yaml \
  --parameters ParameterKey=Environment,ParameterValue=prod \
  --capabilities CAPABILITY_NAMED_IAM

# Add stack instances
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 123456789012 234567890123 \
  --regions us-east-1 us-west-2

# Update StackSet
aws cloudformation update-stack-set \
  --stack-set-name security-baseline \
  --template-body file://template-v2.yaml

# Delete StackSet
aws cloudformation delete-stack-instances \
  --stack-set-name security-baseline \
  --accounts 123456789012 \
  --regions us-east-1 \
  --no-retain-stacks

aws cloudformation delete-stack-set \
  --stack-set-name security-baseline
```

## Change Sets

```bash
# Create change set
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name my-changes \
  --template-body file://template.yaml \
  --parameters ParameterKey=InstanceType,ParameterValue=t3.large

# Describe change set
aws cloudformation describe-change-set \
  --stack-name my-stack \
  --change-set-name my-changes

# Execute change set
aws cloudformation execute-change-set \
  --stack-name my-stack \
  --change-set-name my-changes

# Delete change set
aws cloudformation delete-change-set \
  --stack-name my-stack \
  --change-set-name my-changes
```

## Custom Resources

### Lambda-backed Custom Resource
```yaml
Resources:
  CustomResourceLambda:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.11
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Code:
        ZipFile: |
          import json
          import cfnresponse
          import boto3

          def handler(event, context):
              try:
                  if event['RequestType'] == 'Create':
                      # Create logic
                      responseData = {'Key': 'Value'}
                      cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)

                  elif event['RequestType'] == 'Update':
                      # Update logic
                      responseData = {'Key': 'UpdatedValue'}
                      cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)

                  elif event['RequestType'] == 'Delete':
                      # Delete logic
                      cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

              except Exception as e:
                  print(e)
                  cfnresponse.send(event, context, cfnresponse.FAILED, {})

  CustomResource:
    Type: Custom::MyCustomResource
    Properties:
      ServiceToken: !GetAtt CustomResourceLambda.Arn
      Property1: Value1
      Property2: Value2

Outputs:
  CustomResourceOutput:
    Value: !GetAtt CustomResource.Key
```

## Macros and Transforms

### AWS::Serverless Transform
```yaml
Transform: AWS::Serverless-2016-10-31

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: index.handler
      CodeUri: ./src
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get

  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Auth:
        DefaultAuthorizer: MyCognitoAuthorizer
        Authorizers:
          MyCognitoAuthorizer:
            UserPoolArn: !GetAtt CognitoUserPool.Arn
```

### Custom Macro
```yaml
# Macro template
Transform: MyCustomMacro

Resources:
  # Macro will transform this
  SimplifiedResource:
    Type: Custom::MyType
    Properties:
      Name: MyResource
```

## Drift Detection

```bash
# Detect drift on entire stack
aws cloudformation detect-stack-drift \
  --stack-name my-stack

# Get drift detection status
aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id drift-id

# Describe stack resource drifts
aws cloudformation describe-stack-resource-drifts \
  --stack-name my-stack \
  --stack-resource-drift-status-filters IN_SYNC MODIFIED DELETED

# Detect drift on specific resource
aws cloudformation detect-stack-resource-drift \
  --stack-name my-stack \
  --logical-resource-id MyBucket
```

## Stack Policies

```json
{
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "Update:*",
      "Resource": "LogicalResourceId/ProductionDatabase",
      "Condition": {
        "StringEquals": {
          "ResourceType": ["AWS::RDS::DBInstance"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "Update:*",
      "Resource": "*"
    }
  ]
}
```

```bash
# Set stack policy
aws cloudformation set-stack-policy \
  --stack-name my-stack \
  --stack-policy-body file://policy.json

# Get stack policy
aws cloudformation get-stack-policy \
  --stack-name my-stack
```

## Termination Protection

```bash
# Enable termination protection
aws cloudformation update-termination-protection \
  --enable-termination-protection \
  --stack-name my-stack

# Disable termination protection
aws cloudformation update-termination-protection \
  --no-enable-termination-protection \
  --stack-name my-stack
```

## CLI Commands

```bash
# Create stack
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=my-key \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags Key=Environment,Value=prod

# Update stack
aws cloudformation update-stack \
  --stack-name my-stack \
  --template-body file://template-v2.yaml \
  --parameters ParameterKey=KeyName,UsePreviousValue=true

# Delete stack
aws cloudformation delete-stack \
  --stack-name my-stack

# Describe stack
aws cloudformation describe-stacks \
  --stack-name my-stack

# List stacks
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# List resources
aws cloudformation list-stack-resources \
  --stack-name my-stack

# Get template
aws cloudformation get-template \
  --stack-name my-stack

# Validate template
aws cloudformation validate-template \
  --template-body file://template.yaml

# Wait for stack complete
aws cloudformation wait stack-create-complete \
  --stack-name my-stack

aws cloudformation wait stack-update-complete \
  --stack-name my-stack

# Describe events
aws cloudformation describe-stack-events \
  --stack-name my-stack

# Cancel update
aws cloudformation cancel-update-stack \
  --stack-name my-stack

# Continue update rollback
aws cloudformation continue-update-rollback \
  --stack-name my-stack
```

## Best Practices

### Parameterization
```yaml
# Good: Parameterized and reusable
Parameters:
  EnvironmentName:
    Type: String
  InstanceType:
    Type: String
    Default: t3.micro

# Avoid: Hardcoded values
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro  # Don't hardcode
```

### Cross-Stack References
```yaml
# Exporting stack (network.yaml)
Outputs:
  VPCId:
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VPC-ID

# Importing stack (application.yaml)
Parameters:
  EnvironmentName:
    Type: String

Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      SubnetId: !ImportValue
        Fn::Sub: ${EnvironmentName}-PublicSubnet-ID
```

### DeletionPolicy and UpdateReplacePolicy
```yaml
Resources:
  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      # ...

  Bucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      # ...
```

### Template Organization
```
cloudformation/
├── templates/
│   ├── network.yaml
│   ├── compute.yaml
│   ├── database.yaml
│   └── master.yaml
├── parameters/
│   ├── dev.json
│   ├── staging.json
│   └── prod.json
└── policies/
    └── stack-policy.json
```

## Error Handling

### Rollback Configuration
```yaml
# Stack-level rollback monitoring
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --rollback-configuration \
    RollbackTriggers='[{Arn=arn:aws:cloudwatch:us-east-1:123456789012:alarm:my-alarm,Type=AWS::CloudWatch::Alarm}]' \
    MonitoringTimeInMinutes=5
```

### CreationPolicy
```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    CreationPolicy:
      ResourceSignal:
        Count: 3
        Timeout: PT15M
    Properties:
      # ...
```

### WaitCondition
```yaml
Resources:
  WaitHandle:
    Type: AWS::CloudFormation::WaitConditionHandle

  WaitCondition:
    Type: AWS::CloudFormation::WaitCondition
    Properties:
      Handle: !Ref WaitHandle
      Timeout: 300
      Count: 1

  Instance:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          # Install and configure
          /opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} \
            --resource WaitCondition --region ${AWS::Region}
```

## Resources

- User Guide: docs.aws.amazon.com/cloudformation
- Template Reference: docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html
- Sample Templates: github.com/awslabs/aws-cloudformation-templates
- Best Practices: docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html
