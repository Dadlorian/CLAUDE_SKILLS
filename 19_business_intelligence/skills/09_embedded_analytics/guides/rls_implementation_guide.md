# Row-Level Security Implementation Guide

## Database-Level RLS (PostgreSQL)

### Step 1: Enable RLS on Tables

```sql
-- Enable RLS
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY tenant_isolation_sales ON sales
  FOR ALL
  TO app_user
  USING (tenant_id = current_setting('app.current_tenant')::int);

CREATE POLICY tenant_isolation_customers ON customers
  FOR ALL
  TO app_user
  USING (tenant_id = current_setting('app.current_tenant')::int);
```

### Step 2: Set Tenant Context

```javascript
async function executeQuery(user, query, params) {
  const client = await pool.connect();

  try {
    // Set tenant context
    await client.query(
      'SET app.current_tenant = $1',
      [user.tenantId]
    );

    // Execute query - RLS automatically applied
    const result = await client.query(query, params);

    return result.rows;
  } finally {
    client.release();
  }
}
```

### Step 3: Testing

```javascript
describe('Row-Level Security', () => {
  it('should only return tenant-specific data', async () => {
    const tenant1User = { tenantId: 1 };
    const tenant2User = { tenantId: 2 };

    const data1 = await executeQuery(
      tenant1User,
      'SELECT * FROM sales'
    );

    const data2 = await executeQuery(
      tenant2User,
      'SELECT * FROM sales'
    );

    // Verify isolation
    expect(data1.every(row => row.tenant_id === 1)).toBe(true);
    expect(data2.every(row => row.tenant_id === 2)).toBe(true);

    // No overlap
    const ids1 = new Set(data1.map(r => r.id));
    const ids2 = new Set(data2.map(r => r.id));
    const intersection = [...ids1].filter(id => ids2.has(id));

    expect(intersection).toHaveLength(0);
  });
});
```

## BI Platform RLS

### Tableau: User Attributes + Calculated Fields

```javascript
// Backend: Include RLS in token
const token = jwt.sign({
  'https://tableau.com/oda': {
    tenant_id: user.tenantId,
    region: user.region
  }
}, secret);
```

```
// Tableau: Create calculated field
[Tenant Filter] = [tenant_id] = ATTR([Tenant ID User Attribute])

// Add to Filters > Add to Context
```

### Power BI: Dynamic RLS

```dax
-- Define role in Power BI Desktop
[tenant_id] = USERPRINCIPALNAME()

-- Or with lookup
[tenant_id] = LOOKUPVALUE(
    Users[tenant_id],
    Users[email],
    USERPRINCIPALNAME()
)
```

```javascript
// Backend: Apply role in embed token
const embedToken = await powerbi.generateEmbedToken({
  identities: [{
    username: user.email,
    roles: ['TenantUser'],
    datasets: [datasetId]
  }]
});
```

### Looker: Access Filters

```lookml
# user_attributes.lkml
access_grant: tenant_access {
  user_attribute: tenant_id
  allowed_values: ["*"]
}

# model.lkml
explore: sales {
  required_access_grants: [tenant_access]
  
  sql_always_where:
    ${tenant_id} = '{{ _user_attributes["tenant_id"] }}' ;;
}
```

## Testing Checklist

- [ ] Each tenant sees only their data
- [ ] SQL injection attempts blocked
- [ ] RLS applies to all query types
- [ ] Admin override works (if needed)
- [ ] Performance acceptable with RLS
- [ ] Cross-tenant queries blocked
- [ ] Audit logs capture violations
