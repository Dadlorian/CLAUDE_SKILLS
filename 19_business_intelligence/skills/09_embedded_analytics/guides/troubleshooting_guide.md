# Troubleshooting Guide

## Common Issues

### 1. "Invalid Token" Error

**Symptoms**: Dashboard fails to load with authentication error

**Causes**:
- Token expired
- Secret key mismatch
- Invalid signature
- Clock skew

**Solutions**:

```javascript
// Check token expiration
const decoded = jwt.decode(token);
console.log('Token expires:', new Date(decoded.exp * 1000));
console.log('Current time:', new Date());

// Verify secret
try {
  jwt.verify(token, process.env.JWT_SECRET);
  console.log('Token valid');
} catch (error) {
  console.error('Token invalid:', error.message);
}

// Add clock tolerance
jwt.verify(token, secret, {
  clockTolerance: 60 // 60 seconds
});
```

### 2. CORS Errors

**Symptoms**: Browser blocks embed requests

**Causes**:
- Missing CORS headers
- Domain not whitelisted
- Credentials flag mismatch

**Solutions**:

```javascript
// Backend: Enable CORS
app.use(cors({
  origin: 'https://yourapp.example.com',
  credentials: true
}));

// Frontend: Include credentials
fetch('/api/embed-token', {
  credentials: 'include'
});

// BI Platform: Add domain to whitelist
// Tableau: Connected Apps > Domain Whitelist
// Power BI: Azure AD > Redirect URIs
```

### 3. RLS Not Working

**Symptoms**: Users see data from other tenants

**Causes**:
- RLS policy not applied
- Tenant context not set
- Filters not configured

**Debugging**:

```javascript
// Verify tenant context
async function debugRLS(user, query) {
  console.log('User tenant:', user.tenantId);

  const result = await db.query(query);

  // Check for data leakage
  const otherTenantData = result.rows.filter(
    row => row.tenant_id !== user.tenantId
  );

  if (otherTenantData.length > 0) {
    console.error('RLS VIOLATION:', otherTenantData);
    throw new Error('RLS not working!');
  }

  return result.rows;
}
```

**Fix**:

```sql
-- Verify RLS enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE tablename = 'sales';

-- Check policies
SELECT * FROM pg_policies
WHERE tablename = 'sales';

-- Test policy
SET app.current_tenant = '1';
SELECT * FROM sales; -- Should only show tenant 1
```

### 4. Slow Dashboard Load

**Symptoms**: Dashboard takes > 5 seconds to load

**Diagnosis**:

```javascript
// Measure load time
performance.mark('embed-start');

const viz = new tableau.Viz(container, url, {
  onFirstInteractive: () => {
    performance.mark('embed-end');
    performance.measure('embed-time', 'embed-start', 'embed-end');

    const measure = performance.getEntriesByName('embed-time')[0];
    console.log('Load time:', measure.duration, 'ms');
  }
});
```

**Solutions**:

```javascript
// 1. Enable caching
const cache = new QueryCache();

// 2. Optimize queries
EXPLAIN ANALYZE SELECT ...;

// 3. Add indexes
CREATE INDEX idx_sales_tenant ON sales(tenant_id, date);

// 4. Use materialized views
CREATE MATERIALIZED VIEW sales_summary AS ...;

// 5. Lazy load
const AnalyticsDashboard = React.lazy(() => import('./Dashboard'));
```

### 5. Dashboard Not Visible

**Symptoms**: Empty iframe or blank screen

**Debugging**:

```javascript
// Check iframe loaded
const iframe = document.querySelector('iframe');
console.log('Iframe src:', iframe.src);
console.log('Iframe loaded:', iframe.contentWindow != null);

// Check for errors
iframe.addEventListener('error', (e) => {
  console.error('Iframe error:', e);
});

// Check CSP
console.log('CSP:', document.querySelector('meta[http-equiv="Content-Security-Policy"]'));
```

**Solutions**:

```html
<!-- Add CSP headers -->
<meta http-equiv="Content-Security-Policy"
  content="frame-src https://tableau.example.com https://app.powerbi.com">

<!-- Or in HTTP headers -->
Content-Security-Policy: frame-src https://tableau.example.com
```

### 6. Memory Leaks

**Symptoms**: Browser slows down over time

**Detection**:

```javascript
// Monitor memory
setInterval(() => {
  if (performance.memory) {
    console.log('Heap used:', 
      (performance.memory.usedJSHeapSize / 1048576).toFixed(2), 'MB'
    );
  }
}, 10000);
```

**Fix**:

```javascript
// Cleanup on unmount
useEffect(() => {
  const viz = new tableau.Viz(container, url);

  return () => {
    viz.dispose(); // Important!
  };
}, []);
```

### 7. Token Refresh Issues

**Symptoms**: Dashboard stops working after 30 minutes

**Solution**:

```javascript
class TokenManager {
  constructor() {
    this.token = null;
    this.refreshTimer = null;
  }

  async getToken(forceRefresh = false) {
    if (!forceRefresh && this.token && !this.isExpiringSoon()) {
      return this.token;
    }

    const response = await fetch('/api/embed-token', {
      method: 'POST'
    });

    const { token, expiresIn } = await response.json();
    this.token = token;

    // Schedule refresh before expiration
    this.scheduleRefresh(expiresIn);

    return token;
  }

  scheduleRefresh(expiresIn) {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    // Refresh 1 minute before expiration
    const refreshIn = (expiresIn - 60) * 1000;

    this.refreshTimer = setTimeout(async () => {
      await this.getToken(true);
    }, refreshIn);
  }
}
```

## Debugging Tools

```javascript
// Enable verbose logging
localStorage.setItem('analytics_debug', 'true');

// Log all analytics events
window.addEventListener('message', (event) => {
  if (event.origin.includes('tableau')) {
    console.log('Tableau event:', event.data);
  }
});

// Monitor network requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('Fetch:', args[0]);
  return originalFetch.apply(this, arguments);
};
```

## Support Checklist

When asking for help, provide:
- [ ] Error message (exact text)
- [ ] Browser console logs
- [ ] Network tab (requests/responses)
- [ ] Token (first/last 10 chars only)
- [ ] Platform (Tableau/Power BI/etc.)
- [ ] Browser and version
- [ ] Steps to reproduce
- [ ] Expected vs actual behavior
