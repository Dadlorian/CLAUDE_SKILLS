# IAM (Identity and Access Management) Reference

## IAM Overview

Google Cloud IAM provides unified access control across all GCP services through a policy-based model with fine-grained permissions and resource hierarchies.

## Core Concepts

### IAM Policy
Binds members to roles at a specific resource level.

**Policy Structure**:
```json
{
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": [
        "user:alice@example.com",
        "serviceAccount:my-sa@project.iam.gserviceaccount.com"
      ],
      "condition": {
        "title": "Expires in 2025",
        "expression": "request.time < timestamp('2025-12-31T23:59:59Z')"
      }
    }
  ],
  "etag": "BwXYZ123456=",
  "version": 3
}
```

### Members
Identities that can be granted access.

**Member Types**:
- `user:email@example.com` - Google Account
- `serviceAccount:sa@project.iam.gserviceaccount.com` - Service Account
- `group:group@example.com` - Google Group
- `domain:example.com` - G Suite/Cloud Identity domain
- `allUsers` - Anyone on the internet
- `allAuthenticatedUsers` - Any authenticated Google Account

### Roles
Collections of permissions.

**Role Types**:
1. **Primitive (Basic) Roles**: Broad, legacy
   - `roles/owner` - Full control
   - `roles/editor` - Modify resources
   - `roles/viewer` - Read-only access

2. **Predefined Roles**: Service-specific, curated by Google
   - `roles/compute.admin` - Compute Engine admin
   - `roles/storage.objectViewer` - Storage read-only
   - `roles/bigquery.dataEditor` - BigQuery data editor

3. **Custom Roles**: User-defined permissions
   - Created at organization or project level
   - Combine specific permissions

### Permissions
Granular actions on resources (e.g., `compute.instances.create`).

**Permission Format**: `service.resource.verb`

Examples:
- `storage.buckets.create`
- `compute.instances.delete`
- `bigquery.datasets.get`
- `iam.serviceAccounts.actAs`

## Resource Hierarchy

```
Organization
└── Folders
    └── Projects
        └── Resources (Compute, Storage, etc.)
```

**Policy Inheritance**:
- Policies set at higher levels are inherited by children
- Cannot remove inherited permissions (only add)
- Effective policy = union of all policies in hierarchy

## Service Accounts

### Service Account Types

1. **User-Managed**: Created by users
2. **Default Service Accounts**:
   - Compute Engine: `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
   - App Engine: `PROJECT_ID@appspot.gserviceaccount.com`
3. **Google-Managed**: Google creates and manages

### Create Service Account

```bash
gcloud iam service-accounts create my-service-account \
    --description="My application service account" \
    --display-name="My Service Account"
```

### Service Account Keys

**Create Key** (Not Recommended for production):
```bash
gcloud iam service-accounts keys create key.json \
    --iam-account=my-sa@project.iam.gserviceaccount.com
```

**Better Alternatives**:
1. **Workload Identity** (GKE)
2. **Workload Identity Federation** (external workloads)
3. **Service Account Impersonation**

### Service Account Impersonation

Allow users/SAs to act as another SA.

```bash
gcloud iam service-accounts add-iam-policy-binding \
    target-sa@project.iam.gserviceaccount.com \
    --member=user:admin@example.com \
    --role=roles/iam.serviceAccountTokenCreator
```

**Use Impersonation**:
```bash
gcloud compute instances list \
    --impersonate-service-account=target-sa@project.iam.gserviceaccount.com
```

### Service Account Best Practices

1. **Use specific service accounts** per application
2. **Avoid service account keys** when possible
3. **Rotate keys** regularly (< 90 days)
4. **Use Workload Identity** for GKE
5. **Limit permissions** to minimum required
6. **Monitor usage** with Cloud Logging
7. **Delete unused** service accounts
8. **Use service account impersonation** instead of keys

## IAM Roles

### Primitive Roles (Legacy)

```bash
# Owner (full access + billing)
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:owner@example.com \
    --role=roles/owner

# Editor (modify resources)
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:editor@example.com \
    --role=roles/editor

# Viewer (read-only)
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:viewer@example.com \
    --role=roles/viewer
```

**Avoid in Production**: Too broad, use predefined/custom roles

### Predefined Roles

**Compute Engine**:
```bash
# Compute Admin
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:admin@example.com \
    --role=roles/compute.admin

# Compute Viewer
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:viewer@example.com \
    --role=roles/compute.viewer

# Instance Admin (v1)
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:instance-admin@example.com \
    --role=roles/compute.instanceAdmin.v1
```

**Cloud Storage**:
```bash
# Storage Admin
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:admin@example.com \
    --role=roles/storage.admin

# Storage Object Viewer
gsutil iam ch user:viewer@example.com:objectViewer gs://my-bucket

# Storage Object Creator
gsutil iam ch serviceAccount:sa@project.iam.gserviceaccount.com:objectCreator gs://my-bucket
```

**BigQuery**:
```bash
# BigQuery Admin
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:admin@example.com \
    --role=roles/bigquery.admin

# BigQuery Data Editor
bq add-iam-policy-binding \
    --member=user:editor@example.com \
    --role=roles/bigquery.dataEditor \
    mydataset

# BigQuery Job User
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:analyst@example.com \
    --role=roles/bigquery.jobUser
```

### Custom Roles

**Create Custom Role**:
```bash
gcloud iam roles create myCustomRole \
    --project=PROJECT_ID \
    --title="My Custom Role" \
    --description="Custom role for specific permissions" \
    --permissions=compute.instances.get,compute.instances.list,compute.instances.start,compute.instances.stop \
    --stage=GA
```

**From YAML**:
```yaml
# custom-role.yaml
title: "Instance Operator"
description: "Start and stop instances only"
stage: "GA"
includedPermissions:
- compute.instances.get
- compute.instances.list
- compute.instances.start
- compute.instances.stop
- compute.zones.list
```

```bash
gcloud iam roles create instanceOperator \
    --project=PROJECT_ID \
    --file=custom-role.yaml
```

**Update Custom Role**:
```bash
gcloud iam roles update myCustomRole \
    --project=PROJECT_ID \
    --add-permissions=compute.instances.reset
```

**List Permissions**:
```bash
gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/PROJECT_ID
```

## IAM Policy Management

### Project-Level IAM

**View Policy**:
```bash
gcloud projects get-iam-policy PROJECT_ID \
    --format=json > policy.json
```

**Set Policy**:
```bash
gcloud projects set-iam-policy PROJECT_ID policy.json
```

**Add Binding**:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:alice@example.com \
    --role=roles/compute.viewer
```

**Remove Binding**:
```bash
gcloud projects remove-iam-policy-binding PROJECT_ID \
    --member=user:alice@example.com \
    --role=roles/compute.viewer
```

### Resource-Level IAM

**Storage Bucket**:
```bash
gsutil iam get gs://my-bucket
gsutil iam ch user:alice@example.com:objectViewer gs://my-bucket
gsutil iam ch -d user:alice@example.com:objectViewer gs://my-bucket
```

**BigQuery Dataset**:
```bash
bq show --format=prettyjson mydataset | jq '.access'
bq update --source access.json mydataset
```

**Pub/Sub Topic**:
```bash
gcloud pubsub topics get-iam-policy my-topic
gcloud pubsub topics add-iam-policy-binding my-topic \
    --member=serviceAccount:sa@project.iam.gserviceaccount.com \
    --role=roles/pubsub.publisher
```

## IAM Conditions

### Conditional Access
Grant access based on conditions (time, resource attributes, etc.).

**Time-Based Access**:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:contractor@example.com \
    --role=roles/compute.viewer \
    --condition='expression=request.time < timestamp("2025-12-31T23:59:59Z"),title=Expires end of 2025,description=Temporary access'
```

**Resource-Based Access**:
```bash
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
    --member=user:analyst@example.com \
    --role=roles/storage.objectViewer \
    --condition='expression=resource.name.startsWith("projects/_/buckets/my-bucket/objects/public/"),title=Public folder only'
```

**IP-Based Access**:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=user:remote@example.com \
    --role=roles/compute.viewer \
    --condition='expression=origin.ip == "203.0.113.0/24",title=Office IP only'
```

### CEL Expression Examples

**Time-based**:
```
request.time < timestamp("2025-12-31T23:59:59Z")
request.time.getHours("America/New_York") >= 9 && request.time.getHours("America/New_York") <= 17
```

**Resource-based**:
```
resource.name.startsWith("projects/_/buckets/bucket/objects/folder/")
resource.type == "storage.googleapis.com/Bucket"
```

**Multiple conditions**:
```
request.time.getDayOfWeek("America/New_York") >= 1 &&
request.time.getDayOfWeek("America/New_York") <= 5 &&
request.time.getHours("America/New_York") >= 9 &&
request.time.getHours("America/New_York") <= 17
```

## Organization Policies

### Constraint Types

**List Constraints**: Allow/deny specific values
**Boolean Constraints**: Enable/disable features

### Common Organization Policies

**Restrict VM external IPs**:
```bash
gcloud resource-manager org-policies set-policy policy.yaml \
    --project=PROJECT_ID
```

**policy.yaml**:
```yaml
constraint: compute.vmExternalIpAccess
listPolicy:
  deniedValues:
  - "*"
```

**Require Shared VPC**:
```yaml
constraint: compute.restrictSharedVpcSubnetworks
listPolicy:
  allowedValues:
  - "under:organizations/ORG_ID/folders/FOLDER_ID"
```

**Disable Service Account Key Creation**:
```yaml
constraint: iam.disableServiceAccountKeyCreation
booleanPolicy:
  enforced: true
```

**Allowed External IPs**:
```yaml
constraint: compute.vmExternalIpAccess
listPolicy:
  allowedValues:
  - projects/PROJECT_ID/regions/us-central1/addresses/allowed-ip-1
  - projects/PROJECT_ID/regions/us-central1/addresses/allowed-ip-2
```

## Workload Identity

### GKE Workload Identity
Secure way for GKE pods to access Google Cloud services.

**Enable on Cluster**:
```bash
gcloud container clusters create my-cluster \
    --workload-pool=PROJECT_ID.svc.id.goog
```

**Setup**:
```bash
# Create Kubernetes service account
kubectl create serviceaccount my-ksa -n my-namespace

# Create Google service account
gcloud iam service-accounts create my-gsa

# Bind accounts
gcloud iam service-accounts add-iam-policy-binding \
    my-gsa@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:PROJECT_ID.svc.id.goog[my-namespace/my-ksa]"

# Annotate Kubernetes SA
kubectl annotate serviceaccount my-ksa \
    iam.gke.io/gcp-service-account=my-gsa@PROJECT_ID.iam.gserviceaccount.com \
    -n my-namespace
```

**Use in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  namespace: my-namespace
spec:
  serviceAccountName: my-ksa
  containers:
  - name: app
    image: gcr.io/PROJECT_ID/my-app
```

## Workload Identity Federation

### External Identity Providers
Allow workloads outside GCP to access resources without service account keys.

**Supported Providers**:
- AWS
- Azure
- OIDC (GitHub Actions, GitLab, etc.)
- SAML

### AWS Example

**Create Workload Identity Pool**:
```bash
gcloud iam workload-identity-pools create aws-pool \
    --location=global \
    --description="AWS workload pool"
```

**Create Provider**:
```bash
gcloud iam workload-identity-pools providers create-aws aws-provider \
    --workload-identity-pool=aws-pool \
    --account-id=AWS_ACCOUNT_ID \
    --location=global
```

**Grant Access**:
```bash
gcloud iam service-accounts add-iam-policy-binding my-sa@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/aws-pool/attribute.aws_role/arn:aws:sts::AWS_ACCOUNT_ID:assumed-role/ROLE_NAME"
```

**Get Credentials (from AWS)**:
```bash
gcloud iam workload-identity-pools create-cred-config \
    projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/aws-pool/providers/aws-provider \
    --service-account=my-sa@PROJECT_ID.iam.gserviceaccount.com \
    --aws \
    --output-file=credentials.json

export GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```

### GitHub Actions Example

**Create OIDC Pool**:
```bash
gcloud iam workload-identity-pools create github-pool \
    --location=global \
    --description="GitHub Actions pool"
```

**Create Provider**:
```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
    --workload-identity-pool=github-pool \
    --issuer-uri=https://token.actions.githubusercontent.com \
    --attribute-mapping=google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository \
    --location=global
```

**Grant Access**:
```bash
gcloud iam service-accounts add-iam-policy-binding my-sa@PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/my-org/my-repo"
```

**GitHub Actions Workflow**:
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
    - uses: google-github-actions/auth@v1
      with:
        workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
        service_account: 'my-sa@PROJECT_ID.iam.gserviceaccount.com'
    - run: gcloud compute instances list
```

## IAM Recommender

### IAM Insights and Recommendations

**List Recommendations**:
```bash
gcloud recommender recommendations list \
    --project=PROJECT_ID \
    --location=global \
    --recommender=google.iam.policy.Recommender
```

**Review Unused Service Accounts**:
```bash
gcloud recommender insights list \
    --project=PROJECT_ID \
    --location=global \
    --insight-type=google.iam.serviceAccount.Insight
```

**Apply Recommendation**:
```bash
gcloud recommender recommendations mark-claimed RECOMMENDATION_ID \
    --project=PROJECT_ID \
    --location=global \
    --recommender=google.iam.policy.Recommender \
    --etag=ETAG
```

## Access Context Manager

### Access Levels
Define security perimeters based on attributes.

**Create Access Level**:
```bash
gcloud access-context-manager levels create high_security \
    --policy=POLICY_ID \
    --title="High Security" \
    --basic-level-spec=conditions.yaml
```

**conditions.yaml**:
```yaml
- ipSubnetworks:
  - "203.0.113.0/24"
  devicePolicy:
    requireScreenlock: true
    requireCorpOwned: true
  regions:
  - US
```

### Service Perimeters (VPC Service Controls)

**Create Perimeter**:
```bash
gcloud access-context-manager perimeters create my_perimeter \
    --policy=POLICY_ID \
    --title="Production Perimeter" \
    --resources=projects/123456789 \
    --restricted-services=storage.googleapis.com,bigquery.googleapis.com
```

## IAM Audit Logging

### Admin Activity Logs
Always enabled, no configuration needed.

### Data Access Logs
Must be explicitly enabled.

**Enable Data Access Logging**:
```bash
gcloud projects get-iam-policy PROJECT_ID \
    --format=json > policy.json

# Edit policy.json to add auditConfigs:
```

```json
{
  "auditConfigs": [
    {
      "service": "storage.googleapis.com",
      "auditLogConfigs": [
        {
          "logType": "ADMIN_READ"
        },
        {
          "logType": "DATA_READ"
        },
        {
          "logType": "DATA_WRITE"
        }
      ]
    }
  ]
}
```

```bash
gcloud projects set-iam-policy PROJECT_ID policy.json
```

**Query Audit Logs**:
```bash
gcloud logging read "protoPayload.serviceName=storage.googleapis.com" \
    --limit=10 \
    --format=json
```

## Best Practices

1. **Principle of Least Privilege**: Grant minimum required permissions
2. **Use Predefined Roles**: Instead of primitive roles
3. **Custom Roles**: For specific use cases not covered by predefined
4. **Avoid Service Account Keys**: Use Workload Identity or federation
5. **Regular Audits**: Use IAM Recommender for unused permissions
6. **Enable Audit Logging**: Track all access and changes
7. **Use Groups**: Manage permissions via groups, not individual users
8. **Service Account Per Application**: Isolate permissions
9. **Rotate Keys**: If keys necessary, rotate < 90 days
10. **Use Conditions**: Time-bound or resource-scoped access
11. **Org Policies**: Enforce security guardrails
12. **Monitor IAM Changes**: Alert on policy modifications
13. **Document Roles**: Maintain clear role assignments
14. **Test Permissions**: Use Policy Troubleshooter
15. **Separate Environments**: Different SAs for dev/staging/prod

## Troubleshooting

### Policy Troubleshooter
Check why a member has or doesn't have access.

```bash
gcloud policy-troubleshoot iam policies \
    //cloudresourcemanager.googleapis.com/projects/PROJECT_ID \
    --principal-email=user@example.com \
    --permission=compute.instances.list
```

### Common Issues

1. **Access Denied**: Check role has required permission
2. **Policy Propagation**: Can take up to 7 minutes
3. **Quota Exceeded**: Project has limits on bindings
4. **Inherited Deny**: Organization policy blocking access
5. **Condition Not Met**: Check IAM condition expressions
