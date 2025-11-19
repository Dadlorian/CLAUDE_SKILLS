# Embedded Analytics Implementation Guide

## Implementation Phases

### Phase 1: Planning (Week 1-2)
- Define use cases and requirements
- Choose embedding approach (iframe vs SDK)
- Design authentication flow
- Plan RLS strategy
- Estimate effort and timeline

### Phase 2: POC (Week 3-4)
- Set up development environment
- Implement basic embedding
- Test authentication
- Validate RLS
- Get stakeholder approval

### Phase 3: Development (Week 5-8)
- Build production authentication
- Implement all dashboards
- Add error handling
- Create monitoring
- Performance testing

### Phase 4: Deployment (Week 9-10)
- Deploy to staging
- User acceptance testing
- Security review
- Go-live planning
- Production deployment

## Architecture Patterns

### Single-Tenant (Simple)
```
Customer A Application
└─ Embeds → Dashboard (filtered to Customer A)

Customer B Application
└─ Embeds → Dashboard (filtered to Customer B)

Best for: < 10 customers, simple needs
```

### Multi-Tenant (Scalable)
```
SaaS Application
├─ Customer A → Embedded Dashboard (RLS: tenant_id='A')
├─ Customer B → Embedded Dashboard (RLS: tenant_id='B')
└─ Customer C → Embedded Dashboard (RLS: tenant_id='C')

Best for: Many customers, standardized dashboards
```

### White-Label (Custom)
```
Customer A Portal (Brand A)
└─ Embedded Analytics (Customer A colors/logo)

Customer B Portal (Brand B)  
└─ Embedded Analytics (Customer B colors/logo)

Best for: Premium customers, brand requirements
```

## Security Checklist

- [ ] JWT/Token authentication implemented
- [ ] Tokens expire (< 60 minutes)
- [ ] Row-level security configured
- [ ] Sensitive data masked
- [ ] HTTPS only
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Audit logging active

## Testing Strategy

### Functional Testing
1. Authentication works
2. Content loads correctly  
3. Filters apply properly
4. Drill-downs function
5. Export works (if enabled)

### Security Testing
1. Cannot access other tenant data
2. Token expiration enforced
3. Invalid tokens rejected
4. SQL injection prevented
5. XSS protection working

### Performance Testing
1. Load time < 3 seconds
2. Handles concurrent users
3. No memory leaks
4. Caching working

## Common Pitfalls

❌ Hardcoded credentials in client code
✓ Server-side token generation

❌ No token expiration
✓ Short-lived tokens (15-60 min)

❌ Client-side RLS filtering
✓ Server-enforced RLS

❌ Exposing all data
✓ Minimal data access

## Monitoring

```javascript
// Track embedding events
track('EmbedLoad', {
  customer_id: customerId,
  dashboard_id: dashboardId,
  load_time_ms: loadTime,
  success: true
});

// Alert on errors
if (error) {
  alert('EmbedError', {
    customer_id: customerId,
    error_type: error.type,
    error_message: error.message
  });
}
```

## Resources
- Tableau Embedding: https://help.tableau.com/current/api/embedding_api/
- Power BI Embedded: https://docs.microsoft.com/power-bi/developer/embedded/
- Looker Embed SDK: https://github.com/looker-open-source/embed-sdk
