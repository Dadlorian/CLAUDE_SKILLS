# Layer 7 Load Balancing Guide

## Overview
Layer 7 (Application Layer) load balancing makes routing decisions based on HTTP/HTTPS headers, content, and application-level data, enabling intelligent traffic distribution.

## When to Use L7 Load Balancing

### Ideal Use Cases
- **HTTP/HTTPS Applications**: Web servers, APIs, web apps
- **Multi-service Architecture**: Different services on different paths
- **Microservices**: Route by service name or path
- **Content-Based Routing**: Route by hostname, path, header
- **API Versioning**: Different versions on different backends
- **Mobile + Web**: Different backends for different clients
- **Canary Deployments**: Route percentage to new version

### Not Suitable For
- Non-HTTP protocols (MySQL, Redis, etc.) → Use L4
- Extreme performance critical (gaming, trading) → Use L4
- UDP protocols → Use L4
- Stream-based protocols → Use L4

## L7 Routing Strategies

### Path-Based Routing
**Concept**: Route based on URL path

**Example Configuration**:
```
/api/* → API backend pool
/admin/* → Admin backend pool
/static/* → Static content server
/uploads/* → File server
/ → Main web application

Request: /api/users/123
  ↓ Matches /api/*
  ↓ Routes to api_backend pool
```

**Use Cases**:
- Microservices with distinct paths
- Admin panel on same domain
- Separating static and dynamic
- Different service backends

**Implementation Example** (NGINX):
```nginx
location /api/ {
    proxy_pass http://api_backend;
}

location /admin/ {
    proxy_pass http://admin_backend;
}

location /static/ {
    proxy_pass http://static_backend;
}

location / {
    proxy_pass http://main_backend;
}
```

### Host-Based Routing
**Concept**: Route based on Host header

**Example Configuration**:
```
example.com → main_backend
api.example.com → api_backend
admin.example.com → admin_backend
cdn.example.com → cdn_backend

Request Host: api.example.com
  ↓ Routes to api_backend
```

**Use Cases**:
- Separate subdomains for services
- Multi-tenant applications
- Legacy system + modern separation
- Brand separation

**Implementation Example** (NGINX):
```nginx
server {
    server_name example.com;
    proxy_pass http://main_backend;
}

server {
    server_name api.example.com;
    proxy_pass http://api_backend;
}

server {
    server_name cdn.example.com;
    proxy_pass http://cdn_backend;
}
```

### Header-Based Routing
**Concept**: Route based on HTTP headers

**Example Configuration**:
```
User-Agent: Mobile → mobile_backend
User-Agent: Desktop → desktop_backend

X-API-Version: v2 → v2_backend
X-API-Version: v1 → v1_backend (default)

Accept: application/xml → xml_backend
Accept: application/json → json_backend (default)
```

**Use Cases**:
- Mobile app vs web browser
- API version selection
- Format negotiation
- Custom header routing

**Implementation Example** (F5 iRule):
```tcl
when HTTP_REQUEST {
    if { [HTTP::header exists "X-API-Version"] } {
        set version [HTTP::header "X-API-Version"]
        if { $version eq "v2" } {
            pool pool_api_v2
        } else {
            pool pool_api_v1
        }
    }
}
```

### Cookie-Based Routing
**Concept**: Route based on cookie values

**Example Configuration**:
```
Cookie "api_version=v2" → v2_backend
Cookie "api_version=v1" → v1_backend (default)

Cookie "user_tier=premium" → premium_backend
Cookie "user_tier=free" → free_backend (default)
```

**Use Cases**:
- A/B testing
- Feature flags
- User tier-based routing
- Client groups

### Query Parameter Routing
**Concept**: Route based on URL query parameters

**Example Configuration**:
```
?version=v2 → v2_backend
?version=v1 → v1_backend (default)

?format=xml → xml_backend
?format=json → json_backend (default)
```

**Implementation Example** (NGINX):
```nginx
location / {
    if ($arg_version = "v2") {
        proxy_pass http://api_v2_backend;
    }

    proxy_pass http://api_v1_backend;
}
```

## Content-Based Routing Patterns

### Microservices Architecture
```
example.com/auth/*          → auth_service
example.com/users/*         → user_service
example.com/products/*      → product_service
example.com/orders/*        → order_service
example.com/payments/*      → payment_service

Single entry point, multiple backends
Service isolation
Service scaling
```

**Configuration Example**:
```yaml
virtual_server: example.com:443
rules:
  - path: /auth/*
    backend: auth_service_pool
  - path: /users/*
    backend: user_service_pool
  - path: /products/*
    backend: product_service_pool
  - path: /orders/*
    backend: order_service_pool
  - default:
    backend: main_app_pool
```

### Multi-Tenant SaaS
```
tenant-a.example.com → tenant_a_backend
tenant-b.example.com → tenant_b_backend
tenant-c.example.com → tenant_c_backend

Host header determines tenant
Data isolation
Per-tenant scaling
```

### CDN + Web Server
```
example.com/cdn/* → CDN backend (high cache hit)
example.com/api/* → API backend (dynamic)
example.com/* → Web app backend (HTML)
```

## Advanced Routing Rules

### Composite Routing Rules
**Combine multiple conditions**:
```
IF path BEGINS WITH /api
   AND method EQUALS POST
   AND header Content-Type IS application/json
   THEN route to api_v2_backend

IF header User-Agent CONTAINS "Mobile"
   AND path NOT BEGINS WITH /admin
   THEN route to mobile_optimized_backend

IF source IP IN (203.0.113.0/24)
   AND header X-Internal EQUALS true
   THEN route to internal_backend
```

**Implementation Example** (HAProxy):
```
acl is_api path_beg /api
acl is_post method POST
acl is_json_content hdr(Content-Type) -i application/json
use_backend api_v2 if is_api is_post is_json_content

acl is_mobile hdr_sub(User-Agent) -i mobile
acl not_admin path_beg !/admin
use_backend mobile_backend if is_mobile not_admin
```

### Request Manipulation + Routing
```
Read request headers
Determine backend
Modify headers for backend
Pass to selected backend

Example: Add tenant ID from header to request path
Original: GET /users/123 with X-Tenant: acme
Modified: GET /acme/users/123 for backend
```

## Session Affinity with L7

### Sticky Sessions with Cookies
**Challenge**: L7 makes content-based decisions, but may route same client to different backends

**Solution**: Insert persistence cookie
```
Request 1: GET /page1
  ↓ No cookie, select Backend A
  ↓ Insert cookie: LB_AFFINITY=backend_a
  ↓ Response with Set-Cookie

Request 2: GET /page2 (with LB_AFFINITY=backend_a)
  ↓ Read cookie
  ↓ Route to Backend A (same as before)
  ↓ Session maintained
```

**Configuration Example** (NGINX Plus):
```nginx
upstream backend {
    server backend1.example.com:80 route=a;
    server backend2.example.com:80 route=b;
    server backend3.example.com:80 route=c;

    sticky route $route_id expires=1h;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

## Performance Considerations

### L7 Processing Overhead
```
L4 decision: < 1 microsecond (network 5-tuple only)
L7 decision: 10-100 microseconds (header parsing, routing logic)

For 1 million requests/second:
  L4 LB: 1 core can handle 5+ million RPS
  L7 LB: 1 core can handle 50k-500k RPS (depends on complexity)
```

### Optimization Strategies

**1. Connection Reuse**
```
Keep-Alive: enabled
Connection pooling
Avoid TLS handshake per request
```

**2. Request Buffering**
```
Buffer complete request before routing decision
Allows full header inspection
Slight latency but better routing
```

**3. Intelligent Caching**
```
Cache routing decisions
Pre-compute for common paths
Reduce re-evaluation
```

**4. Parallel Processing**
```
Multiple cores/threads
Stateless routing logic
Scale horizontally
```

## Monitoring L7 Load Balancers

### Metrics to Track
```
1. Request Rate
   - Requests per second
   - Requests per second per pool
   - Requests per second per path

2. Response Time
   - Average response time
   - P95 response time
   - P99 response time

3. Backend Health
   - Pool member status
   - Response codes (2xx, 4xx, 5xx)
   - Error rate by pool

4. Routing Decisions
   - Requests routed to each backend
   - Path distribution
   - Header-based decisions
```

### Alerting

**Critical Alerts**:
```
- Any backend pool completely down
- Error rate > 5%
- Response time P95 > 1 second (for web apps)
- LB CPU > 80%
```

**Warning Alerts**:
```
- Single backend down (still have redundancy)
- Error rate > 1%
- Response time P95 > 500ms
- Any backend connection limit > 80%
```

## Common L7 Patterns

### Blue-Green Deployment
```
Existing (Blue): Stable production version
New (Green): New version, being tested

Route: 100% to Blue initially
Gradually shift percentage to Green as testing passes
Eventually: 100% to Green
Rollback: Shift back to Blue if issues

Configuration:
  Use weighted routing
  path /api/*
    100% → blue_backend
  Shift to: 50/50 blend
  Finally: 100% → green_backend
```

### Canary Deployment
```
Canary: Small percentage of users on new version
Stable: Majority still on proven version

Configuration:
  path /api/*
    95% → stable_v1_backend
    5% → canary_v2_backend

Monitor canary metrics
If healthy: Gradually increase percentage
If issues: Rollback immediately
```

### Rate Limiting and Throttling
```
Per-client rate limiting using L7 awareness
Example: API key in header

If header X-API-Key:
  Check rate limit for key
  If over limit: Return 429 Too Many Requests
  Otherwise: Route to backend

Configuration in load balancer or reverse proxy
```

## Best Practices

1. **Test Routing Rules Thoroughly**
   - All code paths tested
   - Edge cases considered
   - Failover behavior verified

2. **Monitor Routing Decisions**
   - Track which rules match most often
   - Identify hotspots
   - Optimize rules

3. **Keep Rules Simple**
   - Complex rules = slower routing
   - Hard to troubleshoot
   - Difficult to maintain

4. **Document Everything**
   - Why each rule exists
   - Dependencies between rules
   - Testing procedures

5. **Use Request Logging**
   - Log routing decision
   - Log selected backend
   - Help with troubleshooting

6. **Performance Testing**
   - Test with realistic headers
   - Measure routing latency
   - Identify bottlenecks

---

**Last Updated**: 2025-11-19
**Version**: 2.0
