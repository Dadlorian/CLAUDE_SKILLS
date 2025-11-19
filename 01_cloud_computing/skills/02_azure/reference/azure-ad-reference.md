# Azure Active Directory (Azure AD) Reference

## Azure AD Editions

### Free
**Included with**: Azure and Microsoft 365 subscriptions
**Features**:
- User and group management
- On-premises directory synchronization
- Basic reports
- Self-service password change for cloud users
- SSO across Azure, Microsoft 365, SaaS apps
- Up to 500,000 objects

### Premium P1 (~$6/user/month)
**Additional Features**:
- Self-service group management
- Advanced security reports
- Dynamic groups
- Self-service password reset for on-premises users
- Microsoft Identity Manager (MIM)
- Password writeback
- Conditional Access (basic)
- No object limit

### Premium P2 (~$9/user/month)
**Additional Features**:
- Azure AD Identity Protection
- Privileged Identity Management (PIM)
- Access Reviews
- Entitlement Management
- Advanced Conditional Access

## Authentication Methods

### Password Hash Synchronization (PHS)
**How**: Sync password hashes from on-premises AD to Azure AD
**Pros**: Simple, high availability, no extra infrastructure
**Cons**: Password in cloud (hashed)
**Best For**: Most scenarios, recommended default

```powershell
# Enable PHS with Azure AD Connect
Set-ADSyncScheduler -SyncCycleEnabled $true
Start-ADSyncSyncCycle -PolicyType Delta
```

### Pass-Through Authentication (PTA)
**How**: Password validation happens on-premises via agent
**Pros**: Password never in cloud, real-time password policies
**Cons**: Requires agent deployment, dependency on on-premises
**Best For**: Security requirements preventing cloud password storage

### Active Directory Federation Services (ADFS)
**How**: Federation service validates credentials
**Pros**: Maximum control, custom authentication, smartcard support
**Cons**: Complex infrastructure, high maintenance
**Best For**: Complex authentication requirements, legacy

## Multi-Factor Authentication (MFA)

### Methods
1. Microsoft Authenticator app (push notification or code)
2. SMS text message
3. Voice call
4. OATH hardware tokens
5. OATH software tokens

### Enable MFA

**Per-User MFA** (Legacy):
```powershell
# Requires MSOnline module
Connect-MsolService
$mfa = New-Object -TypeName Microsoft.Online.Administration.StrongAuthenticationRequirement
$mfa.RelyingParty = "*"
$mfa.State = "Enabled"
Set-MsolUser -UserPrincipalName user@domain.com -StrongAuthenticationRequirements $mfa
```

**Security Defaults** (Simple):
```powershell
# Enable security defaults (enforces MFA for all users)
# Portal: Azure AD > Properties > Manage Security defaults
```

**Conditional Access** (Recommended for P1+):
```json
{
  "displayName": "Require MFA for all users",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

## Conditional Access

### Common Policies

**Block Legacy Authentication**:
```json
{
  "displayName": "Block legacy authentication",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    },
    "clientAppTypes": ["exchangeActiveSync", "other"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

**Require MFA for Azure Management**:
```json
{
  "displayName": "Require MFA for Azure Management",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeUsers": ["All"],
      "excludeGroups": ["EmergencyAccess"]
    },
    "applications": {
      "includeApplications": ["797f4846-ba00-4fd7-ba43-dac1f8f63013"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

**Require Compliant Device**:
```json
{
  "displayName": "Require compliant device for Office 365",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    },
    "applications": {
      "includeApplications": ["Office365"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["compliantDevice", "domainJoinedDevice"]
  }
}
```

**Risk-Based MFA** (Requires P2):
```json
{
  "displayName": "MFA for risky sign-ins",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    },
    "signInRiskLevels": ["medium", "high"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

### Conditional Access Templates
- Require MFA for administrators
- Require MFA for Azure management
- Block legacy authentication
- Require MFA for risky sign-ins
- Require compliant devices
- Require password change for high-risk users

## Privileged Identity Management (PIM)

**Use Case**: Just-in-time privileged access

### Enable PIM for Azure AD Roles

```powershell
# Requires P2 license and Privileged Role Administrator role
# Activate via Azure Portal: Azure AD > Privileged Identity Management

# Make user eligible for role
New-AzureADMSPrivilegedRoleAssignment `
  -ProviderId "aadRoles" `
  -ResourceId "tenant-id" `
  -RoleDefinitionId "role-id" `
  -SubjectId "user-id" `
  -AssignmentState "Eligible" `
  -Schedule "P180D"
```

### Configure Role Settings
- Activation maximum duration: 8 hours (default)
- Require MFA on activation: Yes
- Require justification: Yes
- Require approval: Optional
- Send notifications: On activation, on assignment

### User Activation Flow
1. User requests role activation
2. Provides justification
3. Completes MFA if required
4. Approval if configured
5. Role active for configured duration
6. Auto-deactivation after expiry

## Identity Protection (P2)

### Risk Detections
- Anonymous IP address usage
- Atypical travel
- Malware linked IP address
- Unfamiliar sign-in properties
- Leaked credentials
- Password spray
- Azure AD threat intelligence

### Risk-Based Policies

**User Risk Policy**:
```json
{
  "displayName": "Block high-risk users",
  "userRiskLevels": ["high"],
  "controls": {
    "block": true
  }
}
```

**Sign-In Risk Policy**:
```json
{
  "displayName": "Require MFA for medium/high risk",
  "signInRiskLevels": ["medium", "high"],
  "controls": {
    "mfa": true
  }
}
```

## Application Registration

### Register Application

```bash
# Create app registration
az ad app create \
  --display-name "MyApp" \
  --sign-in-audience "AzureADMyOrg" \
  --web-redirect-uris "https://myapp.com/auth/callback"

# Create service principal
az ad sp create --id <app-id>

# Add client secret
az ad app credential reset --id <app-id>
```

### API Permissions

**Microsoft Graph Permissions**:
- User.Read: Read signed-in user profile
- User.ReadWrite: Read and update user profile
- Mail.Send: Send mail as signed-in user
- Files.ReadWrite: Access user files
- Directory.Read.All: Read directory data

**Application vs Delegated**:
- **Delegated**: On behalf of signed-in user
- **Application**: App-only access (daemon/service)

```bash
# Add API permission
az ad app permission add \
  --id <app-id> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope

# Grant admin consent
az ad app permission admin-consent --id <app-id>
```

## Managed Identities

### System-Assigned Identity

```bash
# Enable on VM
az vm identity assign --name myVM --resource-group myRG

# Enable on App Service
az webapp identity assign --name myApp --resource-group myRG

# Enable on Azure Function
az functionapp identity assign --name myFunction --resource-group myRG
```

### User-Assigned Identity

```bash
# Create managed identity
az identity create --resource-group myRG --name myIdentity

# Assign to VM
az vm identity assign \
  --name myVM \
  --resource-group myRG \
  --identities /subscriptions/.../userAssignedIdentities/myIdentity

# Get identity
identityPrincipalId=$(az identity show \
  --resource-group myRG \
  --name myIdentity \
  --query principalId -o tsv)

# Grant permissions (e.g., Key Vault)
az keyvault set-policy \
  --name myKeyVault \
  --object-id $identityPrincipalId \
  --secret-permissions get list
```

### Use Managed Identity in Code

**C# Example**:
```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var client = new SecretClient(
    new Uri("https://myvault.vault.azure.net"),
    new DefaultAzureCredential());

var secret = await client.GetSecretAsync("MySecret");
Console.WriteLine(secret.Value.Value);
```

**Python Example**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net", credential=credential)

secret = client.get_secret("MySecret")
print(secret.value)
```

## B2B (Business-to-Business)

**Use Case**: Collaborate with external users

### Invite Guest User

```bash
az ad user create \
  --display-name "External User" \
  --user-principal-name externaluser@external.com \
  --mail-nickname externaluser \
  --user-type Guest
```

**Invitation Settings**:
- Admins and users in the guest inviter role can invite
- Members can invite
- Guests can invite
- Anyone in the organization can invite (default)

### External Identities Settings
- Guest user access restrictions
- External collaboration settings
- Cross-tenant access settings
- Identity providers (Google, Facebook, SAML/WS-Fed)

## B2C (Business-to-Consumer)

**Use Case**: Customer-facing applications

### Create B2C Tenant

```bash
az rest --method put \
  --url "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.AzureActiveDirectory/b2cDirectories/{tenantName}?api-version=2021-04-01" \
  --body '{"location": "United States", "sku": {"name": "PremiumP1", "tier": "A0"}}'
```

### User Flows
- Sign up and sign in
- Profile editing
- Password reset
- Phone sign-up and sign-in

### Identity Providers
- Local accounts (email, username)
- Microsoft Account
- Google
- Facebook
- Amazon
- LinkedIn
- Twitter
- Azure AD
- Custom SAML/OpenID Connect

### Custom Policies (Advanced)
- Complex user journeys
- Custom claims
- API connectors
- Multi-tenancy
- Legacy system integration

## Group Management

### Group Types

**Security Groups**:
```bash
# Create security group
az ad group create \
  --display-name "MySecurityGroup" \
  --mail-nickname "MySecurityGroup" \
  --description "Security group for access control"

# Add member
az ad group member add \
  --group "MySecurityGroup" \
  --member-id <user-object-id>
```

**Microsoft 365 Groups**:
```bash
az ad group create \
  --display-name "MyM365Group" \
  --mail-nickname "MyM365Group" \
  --mail-enabled true \
  --security-enabled false \
  --description "Microsoft 365 group"
```

### Dynamic Groups (P1+)

**Dynamic User Membership**:
```bash
az ad group create \
  --display-name "Marketing Department" \
  --mail-nickname "marketing" \
  --membership-rule "(user.department -eq \"Marketing\")" \
  --membership-rule-processing-type "Dynamic"
```

**Common Rules**:
```
# Department equals Marketing
user.department -eq "Marketing"

# Job title contains Manager
user.jobTitle -contains "Manager"

# User in specific country
user.country -eq "United States"

# Multiple conditions (AND)
(user.department -eq "IT") -and (user.country -eq "United States")

# Multiple conditions (OR)
(user.department -eq "IT") -or (user.department -eq "Engineering")
```

## Self-Service Password Reset (SSPR)

### Enable SSPR

**Requirements**:
- Azure AD Premium P1 or P2
- Registration required before use

**Authentication Methods** (require 2):
- Mobile app notification
- Mobile app code
- Email
- Mobile phone (SMS)
- Office phone
- Security questions (not recommended for production)

### Configure SSPR

1. Enable for users: None, Selected, All
2. Configure authentication methods
3. Set registration requirements
4. Configure notifications
5. Customize helpdesk link
6. Enable password writeback (hybrid)

## Azure AD Connect (Hybrid Identity)

### Installation Options

**Express Settings**:
- Password Hash Sync
- Single forest
- Default OU filtering

**Custom Settings**:
- Choose sync method (PHS, PTA, Federation)
- Multi-forest
- Custom OU filtering
- Attribute filtering
- Group filtering

### Sync Components

**Sync Service**:
- Import from AD
- Export to Azure AD
- Transformation rules
- Filtering

**Health Monitoring**:
```powershell
# Install Azure AD Connect Health agent
.\AzureADConnectHealthSyncSetup.exe
```

### Password Writeback

**Enable in Azure AD Connect**:
Optional Features > Password writeback

**Requirements**:
- Azure AD Premium P1
- Hybrid identity
- Appropriate permissions in on-premises AD

## Monitoring and Reporting

### Sign-In Logs

**Query with Azure CLI**:
```bash
az monitor activity-log list \
  --resource-group myRG \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z
```

**Key Metrics**:
- Total sign-ins
- Success rate
- Failed sign-ins
- Conditional Access policy impact
- MFA usage
- Legacy authentication attempts

### Audit Logs

**Common Events**:
- User created/updated/deleted
- Group created/updated/deleted
- Role assignment changes
- Application consent
- Password reset
- MFA changes

### Access Reviews (P2)

**Use Cases**:
- Review group memberships
- Review application access
- Review Azure AD role assignments
- Review Azure resource role assignments

```powershell
# Create access review
New-AzureADMSAccessReview `
  -DisplayName "Quarterly Group Review" `
  -StartDateTime (Get-Date) `
  -EndDateTime (Get-Date).AddDays(30) `
  -ReviewedEntity "Group" `
  -ReviewerId "user@domain.com"
```

## Best Practices

1. **Enable MFA**: For all users, especially admins
2. **Use Conditional Access**: Block legacy auth, require MFA for admin
3. **Implement PIM**: Just-in-time admin access
4. **Enable Identity Protection**: Risk-based policies
5. **Use Managed Identities**: Eliminate credentials in code
6. **Monitor Sign-Ins**: Watch for anomalies
7. **Regular Access Reviews**: Ensure least privilege
8. **Break Glass Account**: Emergency access account with excluded from CA
9. **Security Defaults**: Minimum baseline (Free tier)
10. **SSPR**: Reduce helpdesk tickets

## Emergency Access Accounts

```bash
# Create break-glass account
az ad user create \
  --display-name "Break Glass Admin" \
  --user-principal-name breakglass@domain.com \
  --password <strong-password> \
  --force-change-password-next-login false

# Assign Global Admin
az role assignment create \
  --assignee breakglass@domain.com \
  --role "Global Administrator" \
  --scope /

# Exclude from all Conditional Access policies!
# Store credentials in secure physical location
# Monitor for usage with alerts
```

## Common Scenarios

### Secure Azure Resources with Azure AD
1. Enable managed identity on resource
2. Grant RBAC permissions to managed identity
3. Use DefaultAzureCredential in code

### SSO for SaaS Applications
1. Add application from gallery
2. Configure SSO (SAML or OIDC)
3. Assign users or groups
4. Test SSO

### Hybrid Identity
1. Install Azure AD Connect
2. Configure sync method (PHS recommended)
3. Enable SSPR with writeback
4. Implement Conditional Access
5. Monitor sync health
