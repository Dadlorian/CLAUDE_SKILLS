# OLAP Security Implementation Guide

## Database Roles

### Read-Only Role
```xml
<Role>
  <ID>Viewers</ID>
  <Name>Report Viewers</Name>
  <Members>
    <Member>
      <Name>DOMAIN\AllUsers</Name>
    </Member>
  </Members>
  <DatabasePermission>
    <Read>Allowed</Read>
  </DatabasePermission>
</Role>
```

### Processing Role
```xml
<Role>
  <ID>DataRefresh</ID>
  <Name>ETL Service</Name>
  <Members>
    <Member>
      <Name>DOMAIN\ETLService</Name>
    </Member>
  </Members>
  <DatabasePermission>
    <Read>Allowed</Read>
    <Process>Allowed</Process>
  </DatabasePermission>
</Role>
```

## Row-Level Security

### Basic Dimension Security
```xml
<DimensionPermission>
  <CubeDimensionID>Region</CubeDimensionID>
  <AttributePermissions>
    <AttributePermission>
      <AttributeID>Region</AttributeID>
      <AllowedSet>
        <![CDATA[
          {[Region].[West], [Region].[Southwest]}
        ]]>
      </AllowedSet>
    </AttributePermission>
  </AttributePermissions>
</DimensionPermission>
```

### Dynamic Security (MDX)
```mdx
-- User sees their assigned region
<AllowedSet>
  <![CDATA[
    STRTOMEMBER(
      "[Region].[" + USERNAME() + "]"
    )
  ]]>
</AllowedSet>
```

### Dynamic Security (DAX)
```dax
// Power BI RLS
[Region] = USERPRINCIPALNAME()

// Or with lookup table
VAR UserEmail = USERPRINCIPALNAME()
VAR UserRegions =
    CALCULATETABLE(
        VALUES(UserSecurity[Region]),
        UserSecurity[Email] = UserEmail
    )
RETURN
    [Region] IN UserRegions
```

## Testing Security

### Impersonate User
```mdx
EXECUTE AS LOGIN = 'DOMAIN\TestUser'

SELECT [Measures].[Sales] ON 0
FROM [Sales]

REVERT
```

### Power BI Testing
In Power BI Desktop:
1. Modeling → Manage Roles
2. View as Role
3. Optionally add "Other user"
4. Test visuals and measures
