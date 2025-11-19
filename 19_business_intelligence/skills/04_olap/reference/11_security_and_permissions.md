# OLAP Security and Permissions

## Overview

Comprehensive security implementation for OLAP cubes, covering authentication, authorization, data security, and cell-level permissions.

## Security Layers

### 1. Server-Level Security
Access to the Analysis Services instance:

```
Windows Authentication (Recommended):
- Integrated with Active Directory
- Single Sign-On
- Centralized management

```xml
<Server>
  <ServerProperties>
    <Security>
      <RequireClientAuthentication>true</RequireClientAuthentication>
    </Security>
  </ServerProperties>
</Server>
```

### 2. Database-Level Security
Access to specific databases:

```xml
<Database>
  <ID>SalesCube</ID>
  <Roles>
    <Role>
      <ID>DatabaseAdmin</ID>
      <Name>Database Administrators</Name>
      <Members>
        <Member>
          <Name>DOMAIN\BI_Admins</Name>
        </Member>
      </Members>
    </Role>
  </Roles>
</Database>
```

### 3. Cube-Level Security
Access to cubes and measures:

```xml
<Cube>
  <ID>Sales</ID>
  <CubeDimension>
    <ID>Product</ID>
    <AttributePermissions>
      <AttributePermission>
        <AttributeID>ProductCost</AttributeID>
        <AllowedSet>{}</AllowedSet> <!-- Deny access -->
      </AttributePermission>
    </AttributePermissions>
  </CubeDimension>
</Cube>
```

### 4. Dimension Security
Row-level security on dimensions:

```xml
<Role>
  <ID>SalesRep</ID>
  <DimensionPermissions>
    <DimensionPermission>
      <CubeDimensionID>Customer</CubeDimensionID>
      <Read>Allowed</Read>
      <AttributePermissions>
        <AttributePermission>
          <AttributeID>Customer</AttributeID>
          <AllowedSet>
            <![CDATA[
              {[Customer].[Customer].&[CustomerID]}
            ]]>
          </AllowedSet>
        </AttributePermission>
      </AttributePermissions>
    </DimensionPermission>
  </DimensionPermissions>
</Role>
```

### 5. Cell-Level Security
Value-level permissions:

```xml
<CellPermission>
  <Access>Read</Access>
  <Expression>
    <![CDATA[
      [Measures].[Sales Amount] < 10000
    ]]>
  </Expression>
</CellPermission>
```

## Role-Based Access Control (RBAC)

### Database Roles

#### Full Administrator
```xml
<Role>
  <ID>Admin</ID>
  <Name>Full Administrators</Name>
  <Members>
    <Member>
      <Name>DOMAIN\BI_Admins</Name>
    </Member>
  </Members>
  <Permissions>
    <DatabasePermission>
      <DatabaseID>SalesCube</DatabaseID>
      <Read>Allowed</Read>
      <Process>Allowed</Process>
      <Administer>Allowed</Administer>
    </DatabasePermission>
  </Permissions>
</Role>
```

Permissions:
- Read: View data
- Process: Refresh cubes
- Administer: Full control

#### Read-Only User
```xml
<Role>
  <ID>Viewer</ID>
  <Name>Report Viewers</Name>
  <Members>
    <Member>
      <Name>DOMAIN\All_Employees</Name>
    </Member>
  </Members>
  <Permissions>
    <DatabasePermission>
      <DatabaseID>SalesCube</DatabaseID>
      <Read>Allowed</Read>
    </DatabasePermission>
  </Permissions>
</Role>
```

#### Power User (Process Only)
```xml
<Role>
  <ID>DataRefresh</ID>
  <Name>Data Refresh Users</Name>
  <Members>
    <Member>
      <Name>DOMAIN\ETL_Service</Name>
    </Member>
  </Members>
  <Permissions>
    <DatabasePermission>
      <DatabaseID>SalesCube</DatabaseID>
      <Read>Allowed</Read>
      <Process>Allowed</Process>
    </DatabasePermission>
  </Permissions>
</Role>
```

## Dimension Security (Row-Level)

### Basic Dimension Security

#### Allow Specific Members
```xml
<DimensionPermission>
  <CubeDimensionID>Region</CubeDimensionID>
  <AttributePermissions>
    <AttributePermission>
      <AttributeID>Region</AttributeID>
      <AllowedSet>
        <![CDATA[
          {
            [Region].[Region].&[West],
            [Region].[Region].&[Southwest]
          }
        ]]>
      </AllowedSet>
    </AttributePermission>
  </AttributePermissions>
</DimensionPermission>
```

Result: User sees only West and Southwest regions

#### Deny Specific Members
```xml
<AttributePermission>
  <AttributeID>Product</AttributeID>
  <DeniedSet>
    <![CDATA[
      {[Product].[Product].&[Confidential_Product]}
    ]]>
  </DeniedSet>
</AttributePermission>
```

### Dynamic Security

#### User-Based Security with CUSTOMDATA
```mdx
-- Use CustomData connection string property
CREATE ROLE [DynamicSecurity]
AS MEMBER [Measures].[UserRegion] AS
    CUSTOMDATA();

WITH MEMBER [Measures].[Allowed Regions] AS
    FILTER(
        [Region].[Region].MEMBERS,
        [Region].[Region].CURRENTMEMBER.Name = [Measures].[UserRegion]
    )

-- Then in dimension security:
<AllowedSet>
  <![CDATA[
    FILTER(
      [Region].[Region].MEMBERS,
      [Region].[Region].CURRENTMEMBER.Name = CUSTOMDATA()
    )
  ]]>
</AllowedSet>
```

#### Security Table Approach
```sql
-- Security table
CREATE TABLE UserSecurity (
    UserName VARCHAR(100),
    RegionID INT,
    ProductCategory VARCHAR(50)
);

-- Populate with user permissions
INSERT INTO UserSecurity VALUES
('DOMAIN\John.Smith', 1, 'Electronics'),
('DOMAIN\John.Smith', 2, 'Electronics'),
('DOMAIN\Jane.Doe', 1, 'All'),
('DOMAIN\Jane.Doe', 2, 'All');
```

```mdx
-- MDX for allowed set
<AllowedSet>
  <![CDATA[
    STRTOMEMBER(
      "[Region].[Region].[" +
      LOOKUPSTRING(
        USERNAME(),
        $RegionSecurity,
        'UserName',
        'RegionName'
      ) +
      "]"
    )
  ]]>
</AllowedSet>
```

### DAX Dynamic Security (Tabular/Power BI)

#### Basic Row-Level Security
```dax
// In Security Role
[Email] = USERPRINCIPALNAME()

// Or
[Region] = USERNAME()
```

#### Manager Hierarchy Security
```dax
// Allow users to see their own data and subordinates
VAR CurrentUser = USERPRINCIPALNAME()
VAR CurrentUserEmployeeID =
    LOOKUPVALUE(
        Employee[EmployeeID],
        Employee[Email],
        CurrentUser
    )
RETURN
    PATHCONTAINS(
        Employee[ManagerPath],
        CurrentUserEmployeeID
    )
```

#### Multi-Value Security
```dax
// User can see multiple regions
VAR CurrentUser = USERPRINCIPALNAME()
VAR UserRegions =
    CALCULATETABLE(
        VALUES(UserSecurity[Region]),
        UserSecurity[Email] = CurrentUser
    )
RETURN
    [Region] IN UserRegions
```

#### Dynamic Email-Based Security
```dax
// Customer sees only their data
VAR CurrentUser = USERPRINCIPALNAME()
VAR CustomerEmail = SUBSTITUTE(CurrentUser, "@company.com", "@customer.com")
RETURN
    Customer[Email] = CustomerEmail
```

## Cell-Level Security

### Basic Cell Security
```xml
<CellPermission>
  <Access>Read</Access>
  <Expression>
    <![CDATA[
      (
        [Measures].[Sales Amount],
        [Product].[Category].CURRENTMEMBER
      ) < 1000000
    ]]>
  </Expression>
  <Description>Hide sales > $1M</Description>
</CellPermission>
```

### Conditional Access
```xml
<CellPermission>
  <Access>Read</Access>
  <Expression>
    <![CDATA[
      IIF(
        [Date].[Year].CURRENTMEMBER.Name = "2024",
        1,  -- Allow access
        0   -- Deny access
      )
    ]]>
  </Expression>
</CellPermission>
```

### Measure-Specific Security
```xml
<!-- Deny access to cost measures -->
<CellPermission>
  <Access>None</Access>
  <Expression>
    <![CDATA[
      [Measures].CURRENTMEMBER IN
      {
        [Measures].[Product Cost],
        [Measures].[Gross Margin]
      }
    ]]>
  </Expression>
</CellPermission>
```

## Visual Level Security (Power BI)

### Object-Level Security
```
Power BI Service:
- Workspace roles (Admin, Member, Contributor, Viewer)
- App permissions
- Report/Dashboard sharing
- Row-level security roles

Power BI Desktop:
- Model roles with DAX filters
```

### Report-Level Permissions
```
Workspace Viewer:
- View reports and dashboards
- Cannot edit
- Cannot share

Workspace Contributor:
- Create and edit content
- Cannot manage roles

Workspace Member:
- Full editing rights
- Can publish
- Can manage some settings

Workspace Admin:
- Full control
- Manage permissions
- Delete workspace
```

## Advanced Security Patterns

### Multi-Role Assignment
User belongs to multiple roles - UNION of permissions:

```
User: John Smith
Roles:
  - SalesWest: Allowed Set = {[Region].&[West]}
  - Electronics: Allowed Set = {[Product Category].&[Electronics]}

Result:
  - Sees ALL regions (no region restriction from Electronics role)
  - Sees ALL categories (no category restriction from SalesWest role)

Solution: Create combined role
  - SalesWest_Electronics:
    - Region: [West]
    - Product Category: [Electronics]
```

### Hierarchical Security
```mdx
-- Allow access to member and all descendants
<AllowedSet>
  <![CDATA[
    {
      [Geography].[Country].[USA],
      DESCENDANTS([Geography].[Country].[USA])
    }
  ]]>
</AllowedSet>

-- Deny specific descendants
<DeniedSet>
  <![CDATA[
    {[Geography].[State].[Confidential State]}
  ]]>
</DeniedSet>
```

### Time-Based Security
```mdx
-- Only allow current year data
<AllowedSet>
  <![CDATA[
    FILTER(
      [Date].[Calendar Year].MEMBERS,
      [Date].[Calendar Year].CURRENTMEMBER.Name =
        FORMAT(NOW(), "yyyy")
    )
  ]]>
</AllowedSet>
```

### Sensitive Data Masking
```dax
// Mask sensitive values
Masked Customer Name =
IF(
    USERPRINCIPALNAME() IN {"admin@company.com"},
    Customer[CustomerName],
    "***CONFIDENTIAL***"
)

Masked Email =
VAR Email = Customer[Email]
VAR AtPosition = FIND("@", Email)
RETURN
    IF(
        HASONEVALUE(Customer[Email]),
        LEFT(Email, 2) & "***" & MID(Email, AtPosition, 100),
        Email
    )
```

## Security Testing

### Test User Impersonation (SSMS)
```mdx
-- Test with specific role
EXECUTE AS LOGIN = 'DOMAIN\TestUser'

SELECT
    [Measures].[Sales Amount] ON 0,
    [Product].[Category].MEMBERS ON 1
FROM [Sales]

REVERT

-- Test with role name
EXECUTE AS ROLE = 'SalesRep'

-- Your test query here

REVERT
```

### Test DAX Security (Power BI)
```
In Power BI Desktop:
1. Modeling tab → Manage Roles
2. Select role → View as
3. Optionally add "Other user" for dynamic security
4. Test queries and visuals
```

### Validation Queries
```mdx
-- Verify allowed members
WITH MEMBER [Measures].[Allowed Count] AS
    COUNT([Product].[Product].ALLMEMBERS)

SELECT
    [Measures].[Allowed Count]
ON 0
FROM [Sales]

-- Check for denied access
SELECT
    [Measures].[Product Cost]  -- Should error if denied
ON 0
FROM [Sales]
```

## Performance Considerations

### Security Impact
```
Performance Cost:
- Dimension Security: Low-Medium (filters at query time)
- Cell Security: High (evaluates for each cell)
- Dynamic Security: Medium (function evaluation overhead)

Optimization:
- Use dimension security over cell security
- Minimize complex MDX in security expressions
- Pre-calculate security attributes
- Test with representative data volumes
```

### Caching with Security
```
Query Cache:
- Separate cache per role
- Memory requirements multiply by role count
- Consider role consolidation

Aggregations:
- Built per role if dimension security applied
- Can significantly increase storage
- Monitor disk usage
```

## Best Practices

### 1. Security Design
```
✓ Start with least privilege
✓ Use Active Directory groups, not individuals
✓ Document all security roles
✓ Regular security audits
✓ Test thoroughly before deployment
✓ Use dimension security over cell security
✓ Minimize role count (combine where possible)
```

### 2. Dynamic Security
```
✓ Store security rules in tables
✓ Use CUSTOMDATA or USERNAME() appropriately
✓ Cache security lookups where possible
✓ Document security logic clearly
✓ Provide admin override capability
```

### 3. Maintenance
```
✓ Regular access reviews
✓ Remove unused roles
✓ Update security tables with user changes
✓ Monitor security-related errors
✓ Document security model
✓ Version control security configurations
```

### 4. Compliance
```
✓ Log security changes
✓ Audit access patterns
✓ Comply with data regulations (GDPR, HIPAA, etc.)
✓ Implement data classification
✓ Encrypt sensitive data at rest
✓ Use SSL/TLS for connections
```

## Troubleshooting

### Common Issues

#### Users See No Data
```
Check:
1. Role membership correct?
2. Allowed set defined?
3. Typos in MDX/DAX expressions?
4. Test with View As functionality
5. Check error logs
```

#### Users See Too Much Data
```
Check:
1. Multiple role assignment (UNION)
2. Missing denied set
3. Incorrect AllowedSet MDX
4. Default member accessible
```

#### Performance Degradation
```
Solutions:
1. Simplify security expressions
2. Reduce role count
3. Use dimension vs cell security
4. Monitor cache usage
5. Optimize security tables
```

### Debugging Tools
```powershell
# Get effective permissions
$server = New-Object Microsoft.AnalysisServices.Server
$server.Connect("localhost")

$db = $server.Databases["SalesCube"]
$role = $db.Roles["SalesRep"]

# View role definition
$role.DimensionPermissions | ForEach-Object {
    Write-Host "Dimension: $($_.CubeDimensionID)"
    Write-Host "Allowed Set: $($_.AllowedSet)"
}

$server.Disconnect()
```

## Compliance and Auditing

### Audit Logging
```xml
<Server>
  <ServerProperties>
    <Log>
      <QueryLog>
        <QueryLogConnectionString>...</QueryLogConnectionString>
        <QueryLogSampling>10</QueryLogSampling>
      </QueryLog>
      <FlightRecorder>
        <Enabled>true</Enabled>
      </FlightRecorder>
    </Log>
  </ServerProperties>
</Server>
```

### Security Event Monitoring
```sql
-- Query log analysis
SELECT
    SPID,
    StartTime,
    NTUserName,
    NTDomainName,
    ApplicationName,
    Duration,
    TextData
FROM QueryLog
WHERE NTUserName = 'suspicious_user'
ORDER BY StartTime DESC;
```
