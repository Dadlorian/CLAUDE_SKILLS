# Session Persistence Reference

## Overview
Session persistence (sticky sessions/affinity) ensures that client requests are consistently directed to the same backend server, maintaining application state and session continuity.

## Session Persistence Methods

### Cookie-Based Persistence (Application Cookie)
**Description**: Uses existing application session cookies to maintain affinity.

**How It Works**:
1. Load balancer reads application session cookie
2. Extracts session identifier
3. Consistently routes client to same backend
4. Application manages session state

**Configuration Example**:
```
Method: Cookie-Based
Cookie Name: JSESSIONID
Timeout: 1 hour
Path: /
Domain: example.com
```

**Request Flow**:
```
1. Client sends initial request (no cookie)
   → Load balancer selects Backend A
   → Application creates session cookie (JSESSIONID=abc123)
   → Response includes Set-Cookie header

2. Client sends second request (with JSESSIONID=abc123)
   → Load balancer reads JSESSIONID
   → Routes to same Backend A
   → Session state maintained
```

**Advantages**:
- Application-native solution
- No load balancer overhead
- Works across restarts (if cookie preserved)
- Can work across multiple load balancers

**Disadvantages**:
- Depends on application cookie generation
- Session loss if cookie deleted
- No automatic backup if server fails

### Cookie-Based Persistence (Load Balancer Cookie)
**Description**: Load balancer inserts its own cookie to track affinity.

**How It Works**:
1. Load balancer selects backend for client
2. Inserts proprietary cookie with backend identifier
3. On subsequent requests, reads own cookie
4. Routes to same backend based on cookie value

**Configuration Example**:
```
Method: Persistent Cookie
Cookie Name: LB_AFFINITY
Timeout: 30 minutes
Insert Mode: Rewrite
Encryption: yes
```

**Request Flow**:
```
1. Client sends initial request
   → Load balancer selects Backend B
   → Inserts Set-Cookie: LB_AFFINITY=backend_b_id
   → Response sent to client

2. Client sends follow-up request
   → Cookie sent: LB_AFFINITY=backend_b_id
   → Load balancer decodes and routes to Backend B
```

**Cookie Encoding Options**:
```
Plain: LB_AFFINITY=backend_2
Encoded: LB_AFFINITY=YmFja2VuZF8y
Encrypted: LB_AFFINITY=aBcD3fGhIjK1lMnOpQ==
```

**Advantages**:
- Load balancer controlled
- Works with any application
- Can survive backend failure (if cookie includes failover info)
- Fine-grained timeout control

**Disadvantages**:
- Extra cookie in all requests
- Session loss if cookie deleted
- Firewall/proxy might remove cookies

### Source IP Hash
**Description**: Routes based on client source IP address.

**How It Works**:
1. Load balancer calculates hash of client IP
2. Consistently maps to same backend
3. No cookie or session state required
4. Stateless on load balancer

**Configuration Example**:
```
Method: Source IP Hash
Hash Algorithm: CRC32 or MD5
Mask: For source IP ranges (if needed)
Fallback: Round Robin on server failure
```

**Calculation**:
```
backend_index = hash(client_ip) % number_of_backends
select backends[backend_index]
```

**Hash Function Example** (CRC32):
```
Client IP: 192.168.1.100
CRC32 Hash: 0x12345678
Modulo 3: 0x12345678 % 3 = 2
Select: Backend[2] (3rd backend)
```

**Advantages**:
- Stateless persistence
- No cookies required
- Works with all applications
- Low overhead

**Disadvantages**:
- Unfair distribution if client IPs vary
- Breaks with NAT/Proxy scenarios
- No persistence if client IP changes
- Difficult for load balancing across IP subnets

**Use Cases**:
- P2P applications
- Download clients (same IP maintains connection)
- VPN users (IP doesn't change)
- Desktop applications

### SSL Session ID Persistence
**Description**: Routes based on SSL/TLS session identifier.

**How It Works**:
1. During SSL handshake, client receives session ID
2. On subsequent connections, client sends same session ID
3. Load balancer uses session ID for routing
4. Reduces SSL handshake overhead

**Configuration Example**:
```
Method: SSL Session ID
SSL Version: TLS 1.2, TLS 1.3
Session Timeout: 24 hours
Cache Size: 32MB
```

**SSL Session Resumption Flow**:
```
Connection 1 (New Session):
- Full TLS handshake (costly)
- Session ID created: sess_abc123
- Sent in ServerHello
- Client stores session ID

Connection 2 (Session Resume):
- Client sends session ID in ClientHello
- Server recognizes session ID
- Abbreviated handshake (fast)
- Routing based on session ID
```

**Advantages**:
- Reduces TLS handshake overhead
- Works with HTTPS automatically
- Transparent to application
- Session tied to certificate

**Disadvantages**:
- Requires TLS support
- Session memory requirements
- Complex with distributed load balancers

### Request Header Persistence
**Description**: Uses HTTP headers to identify and route clients.

**Common Headers**:
```
X-User-ID: user_123
X-Session-ID: session_abc
X-Client-ID: mobile_app_1
Authorization: Bearer token_xyz
```

**Configuration Example**:
```
Method: Header-Based
Header Name: X-Session-ID
Hash Function: MD5
Fallback: Random
```

**Use Cases**:
- API authentication tokens
- Mobile application tracking
- Microservices routing
- Custom application identifiers

### URL Parameter Persistence
**Description**: Uses URL query parameters for session identification.

**Example URLs**:
```
https://example.com/api/data?sessionid=abc123
https://app.example.com/page?user_id=456
https://service.example.com/resource?token=xyz789
```

**Limitations**:
- Parameters might be rewritten
- Not suitable for all URLs
- Security concerns (exposing session in URL)
- Browser history leakage

## Session Persistence Timeout

### Timeout Configuration
**Idle Timeout**: Session ends after no activity
```
Timeout: 30 minutes
After 30 minutes of inactivity, session cleared
```

**Absolute Timeout**: Maximum session duration
```
Timeout: 8 hours
Session ends after 8 hours regardless of activity
```

**Browser Session Timeout**: Session ends when browser closes
```
HTTP Only Cookie (without explicit expiration)
Session lost on browser close
```

### Timeout Behavior
```
15:00 - Client session starts
15:10 - Client makes request (activity) → timeout reset
15:25 - No activity → still valid (within 30-min idle)
15:35 - Still no activity → session expires (past 30-min)
15:40 - Client requests → new session created
```

## Session Persistence with Health Checks

### Graceful Drain on Server Failure
**Scenario**: Backend server becomes unhealthy while sessions are active

**Options**:
```
1. Immediate Failover: Redirect active sessions to healthy backend
   - Session loss (if not replicated)
   - Quick recovery
   - Requires backend selection logic

2. Connection Draining: Wait for sessions to complete
   - Sessions continue on failing server
   - New sessions routed to healthy server
   - Graceful degradation
   - Requires timeout

3. Session Replication: Use replicated session store
   - Sessions survive backend failure
   - Requires shared storage
   - More complex setup
```

**Configuration Example** (Connection Draining):
```
Health Check Status: Down
Drain Timeout: 5 minutes
Existing Connections: Allow to complete
New Connections: Route to healthy backend
```

## Session Persistence Failure Scenarios

### Scenario 1: Server Failure
**Situation**: Preferred backend goes down

**With Session Replication**:
```
Client → LB → Backend A (DOWN)
                ↓ (detect failure)
              Backend B (replica available)
              ✓ Session restored
```

**Without Session Replication**:
```
Client → LB → Backend A (DOWN)
                ↓ (backend unavailable)
              Backend B (fallback)
              ✗ Session lost (new session created)
```

### Scenario 2: Cookie Deletion
**Situation**: Client deletes session cookie

**Result**:
```
1. No persistence cookie sent
2. Load balancer selects new backend
3. Session lost
4. User must re-authenticate
```

### Scenario 3: Client IP Change
**Situation**: Client changes network (IP hash method)

**Result**:
```
Home: 192.168.1.100 → Backend A
Mobile: 4G network (different IP) → Backend B
↓ Session lost if using IP hash
↓ No persistence without other methods
```

## Session Persistence Best Practices

### 1. Choose Appropriate Method
```
Web Applications → Application Cookie
Legacy Systems → IP Hash
API Services → Token/Header-based
HTTPS-only → SSL Session ID
```

### 2. Implement Backup Strategy
```
Primary: Application cookie
Secondary: Load balancer cookie
Tertiary: Session store replication
```

### 3. Session State Management
```
Session Location:
- In-memory: Fast, lost on restart
- Database: Persistent, slower
- Distributed Cache: Fast and persistent (Redis)
```

### 4. Timeout Configuration
```
Idle Timeout: 30 minutes (typical)
Absolute Timeout: 8 hours (max session)
Warning: Account for timezone differences
```

### 5. Monitor Session Persistence
```
- Track session persistence rate
- Monitor session duration
- Alert on unusual patterns
- Log persistence failures
```

### 6. Security Considerations
```
- Use HTTPS for session cookies
- HttpOnly flag prevents JavaScript access
- Secure flag ensures HTTPS-only transmission
- SameSite attribute prevents CSRF
```

### 7. Multiple Load Balancer Scenario
```
With Cookies: Works across load balancers
With IP Hash: Doesn't work (different source IP per LB)
Solution: Use session store or shared cookie strategy
```

## Session Persistence Configuration Templates

### Web Application (Session Store)
```yaml
Persistence: Cookie (application)
Cookie Name: JSESSIONID
Timeout: 1 hour
Backup: Database session store
Failover: Reload session from database
SSL: Yes (HTTPS only)
```

### API Service (Token-based)
```yaml
Persistence: Header-based
Header Name: X-API-Token
Timeout: 24 hours
Validation: Token verification on backend
Failover: Token invalid on backup
```

### Database Connection (Sticky)
```yaml
Persistence: Source IP Hash
Timeout: Session duration + 5 min
Fallback: Weighted least connections
Failover: Connection error, reconnect to new backend
```

---

**Last Updated**: 2025-11-19
**Version**: 2.0
