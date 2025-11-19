import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

// Configuration
const config = new pulumi.Config();
const environment = pulumi.getStack();
const projectName = pulumi.getProject();

// Create VPC
const vpc = new awsx.ec2.Vpc(`${projectName}-${environment}-vpc`, {
    cidrBlock: "10.0.0.0/16",
    numberOfAvailabilityZones: 3,
    subnetSpecs: [
        {
            type: awsx.ec2.SubnetType.Public,
            cidrMask: 24,
        },
        {
            type: awsx.ec2.SubnetType.Private,
            cidrMask: 24,
        },
    ],
    natGateways: {
        strategy: awsx.ec2.NatGatewayStrategy.OnePerAz,
    },
    tags: {
        Name: `${projectName}-${environment}-vpc`,
        Environment: environment,
        ManagedBy: "Pulumi",
    },
});

// Security Group for ALB
const albSecurityGroup = new aws.ec2.SecurityGroup(`${projectName}-${environment}-alb-sg`, {
    vpcId: vpc.vpcId,
    description: "Security group for Application Load Balancer",
    ingress: [
        {
            fromPort: 80,
            toPort: 80,
            protocol: "tcp",
            cidrBlocks: ["0.0.0.0/0"],
            description: "HTTP from internet",
        },
        {
            fromPort: 443,
            toPort: 443,
            protocol: "tcp",
            cidrBlocks: ["0.0.0.0/0"],
            description: "HTTPS from internet",
        },
    ],
    egress: [
        {
            fromPort: 0,
            toPort: 0,
            protocol: "-1",
            cidrBlocks: ["0.0.0.0/0"],
            description: "Allow all outbound",
        },
    ],
    tags: {
        Name: `${projectName}-${environment}-alb-sg`,
    },
});

// Security Group for EC2
const ec2SecurityGroup = new aws.ec2.SecurityGroup(`${projectName}-${environment}-ec2-sg`, {
    vpcId: vpc.vpcId,
    description: "Security group for EC2 instances",
    ingress: [
        {
            fromPort: 80,
            toPort: 80,
            protocol: "tcp",
            securityGroups: [albSecurityGroup.id],
            description: "HTTP from ALB",
        },
    ],
    egress: [
        {
            fromPort: 0,
            toPort: 0,
            protocol: "-1",
            cidrBlocks: ["0.0.0.0/0"],
            description: "Allow all outbound",
        },
    ],
    tags: {
        Name: `${projectName}-${environment}-ec2-sg`,
    },
});

// Get latest Amazon Linux 2 AMI
const ami = aws.ec2.getAmi({
    mostRecent: true,
    owners: ["amazon"],
    filters: [
        {
            name: "name",
            values: ["amzn2-ami-hvm-*-x86_64-gp2"],
        },
    ],
});

// IAM Role for EC2
const ec2Role = new aws.iam.Role(`${projectName}-${environment}-ec2-role`, {
    assumeRolePolicy: aws.iam.assumeRolePolicyForPrincipal({
        Service: "ec2.amazonaws.com",
    }),
    tags: {
        Name: `${projectName}-${environment}-ec2-role`,
    },
});

// Attach SSM policy
new aws.iam.RolePolicyAttachment(`${projectName}-${environment}-ec2-ssm`, {
    role: ec2Role.name,
    policyArn: "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
});

// IAM Instance Profile
const instanceProfile = new aws.iam.InstanceProfile(`${projectName}-${environment}-instance-profile`, {
    role: ec2Role.name,
});

// User data script
const userData = `#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from Pulumi - Instance $(ec2-metadata --instance-id | cut -d ' ' -f 2)</h1>" > /var/www/html/index.html
`;

// Launch Template
const launchTemplate = new aws.ec2.LaunchTemplate(`${projectName}-${environment}-lt`, {
    imageId: ami.then(ami => ami.id),
    instanceType: "t3.micro",
    iamInstanceProfile: {
        name: instanceProfile.name,
    },
    vpcSecurityGroupIds: [ec2SecurityGroup.id],
    userData: Buffer.from(userData).toString("base64"),
    blockDeviceMappings: [
        {
            deviceName: "/dev/xvda",
            ebs: {
                volumeSize: 30,
                volumeType: "gp3",
                encrypted: true,
                deleteOnTermination: true,
            },
        },
    ],
    metadataOptions: {
        httpEndpoint: "enabled",
        httpTokens: "required",
        httpPutResponseHopLimit: 1,
    },
    monitoring: {
        enabled: true,
    },
    tagSpecifications: [
        {
            resourceType: "instance",
            tags: {
                Name: `${projectName}-${environment}-web`,
                Environment: environment,
                ManagedBy: "Pulumi",
            },
        },
    ],
});

// Application Load Balancer
const alb = new aws.lb.LoadBalancer(`${projectName}-${environment}-alb`, {
    internal: false,
    loadBalancerType: "application",
    securityGroups: [albSecurityGroup.id],
    subnets: vpc.publicSubnetIds,
    enableDeletionProtection: environment === "prod",
    tags: {
        Name: `${projectName}-${environment}-alb`,
        Environment: environment,
    },
});

// Target Group
const targetGroup = new aws.lb.TargetGroup(`${projectName}-${environment}-tg`, {
    port: 80,
    protocol: "HTTP",
    vpcId: vpc.vpcId,
    targetType: "instance",
    healthCheck: {
        enabled: true,
        healthyThreshold: 2,
        unhealthyThreshold: 2,
        timeout: 5,
        interval: 30,
        path: "/",
        matcher: "200",
    },
    tags: {
        Name: `${projectName}-${environment}-tg`,
    },
});

// ALB Listener
const listener = new aws.lb.Listener(`${projectName}-${environment}-listener`, {
    loadBalancerArn: alb.arn,
    port: 80,
    protocol: "HTTP",
    defaultActions: [
        {
            type: "forward",
            targetGroupArn: targetGroup.arn,
        },
    ],
});

// Auto Scaling Group
const asg = new aws.autoscaling.Group(`${projectName}-${environment}-asg`, {
    vpcZoneIdentifiers: vpc.privateSubnetIds,
    minSize: 1,
    maxSize: 3,
    desiredCapacity: 2,
    healthCheckType: "ELB",
    healthCheckGracePeriod: 300,
    launchTemplate: {
        id: launchTemplate.id,
        version: "$Latest",
    },
    targetGroupArns: [targetGroup.arn],
    tags: [
        {
            key: "Name",
            value: `${projectName}-${environment}-web`,
            propagateAtLaunch: true,
        },
        {
            key: "Environment",
            value: environment,
            propagateAtLaunch: true,
        },
    ],
});

// Auto Scaling Policies
const scaleUpPolicy = new aws.autoscaling.Policy(`${projectName}-${environment}-scale-up`, {
    scalingAdjustment: 1,
    adjustmentType: "ChangeInCapacity",
    cooldown: 300,
    autoscalingGroupName: asg.name,
});

const scaleDownPolicy = new aws.autoscaling.Policy(`${projectName}-${environment}-scale-down`, {
    scalingAdjustment: -1,
    adjustmentType: "ChangeInCapacity",
    cooldown: 300,
    autoscalingGroupName: asg.name,
});

// CloudWatch Alarms
const cpuHighAlarm = new aws.cloudwatch.MetricAlarm(`${projectName}-${environment}-cpu-high`, {
    comparisonOperator: "GreaterThanThreshold",
    evaluationPeriods: 2,
    metricName: "CPUUtilization",
    namespace: "AWS/EC2",
    period: 300,
    statistic: "Average",
    threshold: 70,
    dimensions: {
        AutoScalingGroupName: asg.name,
    },
    alarmDescription: "This metric monitors EC2 CPU utilization",
    alarmActions: [scaleUpPolicy.arn],
});

const cpuLowAlarm = new aws.cloudwatch.MetricAlarm(`${projectName}-${environment}-cpu-low`, {
    comparisonOperator: "LessThanThreshold",
    evaluationPeriods: 2,
    metricName: "CPUUtilization",
    namespace: "AWS/EC2",
    period: 300,
    statistic: "Average",
    threshold: 20,
    dimensions: {
        AutoScalingGroupName: asg.name,
    },
    alarmDescription: "This metric monitors EC2 CPU utilization",
    alarmActions: [scaleDownPolicy.arn],
});

// S3 Bucket for application data
const bucket = new aws.s3.Bucket(`${projectName}-${environment}-data`, {
    bucket: `${projectName}-${environment}-data-${aws.getCallerIdentity().then(id => id.accountId)}`,
    tags: {
        Name: `${projectName}-${environment}-data`,
        Environment: environment,
    },
});

// Enable versioning
new aws.s3.BucketVersioningV2(`${projectName}-${environment}-bucket-versioning`, {
    bucket: bucket.id,
    versioningConfiguration: {
        status: "Enabled",
    },
});

// Enable encryption
new aws.s3.BucketServerSideEncryptionConfigurationV2(`${projectName}-${environment}-bucket-encryption`, {
    bucket: bucket.id,
    rules: [
        {
            applyServerSideEncryptionByDefault: {
                sseAlgorithm: "AES256",
            },
        },
    ],
});

// Block public access
new aws.s3.BucketPublicAccessBlock(`${projectName}-${environment}-bucket-public-access`, {
    bucket: bucket.id,
    blockPublicAcls: true,
    blockPublicPolicy: true,
    ignorePublicAcls: true,
    restrictPublicBuckets: true,
});

// Outputs
export const vpcId = vpc.vpcId;
export const publicSubnetIds = vpc.publicSubnetIds;
export const privateSubnetIds = vpc.privateSubnetIds;
export const albDnsName = alb.dnsName;
export const applicationUrl = pulumi.interpolate`http://${alb.dnsName}`;
export const bucketName = bucket.id;
export const asgName = asg.name;
