# Session Persistence Guide

## When Session Persistence is Needed

### Stateful Applications
**Definition**: Applications that maintain state per client

**Examples**:
```
Web Applications:
  - Shopping cart contents
  - User session data
  - Form data in progress
  - User preferences

Real-time Applications:
  - Chat/messaging (connection state)
  - Gaming (player session)
  - Video streaming (buffer state)

Data Applications:
  - Editing tools (document lock state)
  - Spreadsheets (cell edit state)
  - Design tools (canvas state)
```

### Session State Storage Options
```
Option 1: In-Memory on Backend
  - Fast
  - Lost if server fails
  - Per-server persistence needed

Option 2: Distributed Cache (Redis)
  - Fast
  - Survives server failure
  - Requires separate service

Option 3: Shared Database
  - Slower than memory
  - Persistent
  - Requires database access

Option 4: Load Balancer Affinity
  - Always route to same server
  - No session migration
  - Loss if server fails
```

## Implementing Session Affinity

### Cookie-Based Affinity

**Method 1: Application Session Cookie**

**How It Works**:
```
1. Client first request (no cookie)
   ↓ LB selects Backend A
   ↓ Backend A creates session
   ↓ Backend A sets cookie: JSESSIONID=abc123
   ↓ Browser receives cookie

2. Client second request (with cookie)
   ↓ Browser sends: JSESSIONID=abc123
   ↓ LB reads cookie
   ↓ Routes to Backend A (same server)
   ↓ Session state maintained
```

**Configuration** (NGINX Plus):
```nginx
upstream backend {
    server backend1.example.com:80 route=a;
    server backend2.example.com:80 route=b;
    server backend3.example.com:80 route=c;

    sticky route $route_id expires=1h domain=.example.com path=/ secure;
}
```

**Configuration** (HAProxy):
```
backend web_backend
    balance roundrobin
    cookie JSESSIONID insert indirect nocache

    server web1 192.168.1.10:80 check cookie web1
    server web2 192.168.1.11:80 check cookie web2
    server web3 192.168.1.12:80 check cookie web3
```

**Advantages**:
- Application aware
- Works with any application
- Cookie managed by application
- No load balancer overhead (if using app cookie)

**Disadvantages**:
- Requires cookie support in browser
- Session lost if cookie deleted
- Doesn't work with non-HTTP

### Method 2: Load Balancer Inserted Cookie

**How It Works**:
```
1. Client first request (no affinity cookie)
   ↓ LB selects Backend B
   ↓ LB inserts cookie: LB_AFFINITY=backend_b_id
   ↓ Backend B processes request
   ↓ Response includes Set-Cookie

2. Client second request (with LB_AFFINITY)
   ↓ LB reads LB_AFFINITY cookie
   ↓ Decodes backend ID (B)
   ↓ Routes to Backend B
   ↓ Session continues
```

**Cookie Encoding**:
```
Plain: LB_AFFINITY=backend_2
Encoded: LB_AFFINITY=YmFja2VuZF8y
Encrypted: LB_AFFINITY=kHf9...encrypted...s2Jx

Encrypted is more secure
```

**Configuration** (F5 BIG-IP):
```
ltm persistence cookie
create web_persist {
    cookie name LB_AFFINITY
    cookie expiration 3600
    cookie method insert
    match-across-services disabled
    match-across-virtuals disabled
    mode http
}

ltm virtual web_vs
apply pool web_backend
persistence web_persist
```

**Configuration** (HAProxy):
```
backend web_backend
    balance roundrobin
    cookie LB_AFFINITY insert indirect nocache httponly secure

    server web1 192.168.1.10:80 check cookie web1
    server web2 192.168.1.11:80 check cookie web2
    server web3 192.168.1.12:80 check cookie web3
```

### Source IP/IP Hash Persistence

**How It Works**:
```
1. Client sends request (IP: 203.0.113.50)
   ↓ LB calculates hash of IP
   ↓ hash(203.0.113.50) % 3 = 1
   ↓ Always routes to Backend 2

2. Client second request (same IP)
   ↓ hash(203.0.113.50) % 3 = 1
   ↓ Routes to Backend 2 again
   ↓ Session continues
```

**Advantages**:
- No cookies needed
- No session state
- Works with all protocols
- Load balancer stateless

**Disadvantages**:
- Unfair if clients share IP (NAT/proxy)
- No persistence if client IP changes
- Hash collisions possible
- Doesn't scale to new servers well

**Configuration** (NGINX):
```nginx
upstream backend {
    ip_hash;

    server backend1.example.com:80;
    server backend2.example.com:80;
    server backend3.example.com:80;
}
```

**Configuration** (HAProxy):
```
backend db_backend
    balance source  # Source IP hash
    server db1 192.168.1.20:3306
    server db2 192.168.1.21:3306 backup
```

### Session Timeout Configuration

**Idle Timeout**:
```
Timeout: 30 minutes

Session expires if:
  No requests for 30 minutes
  Even if browser open

Configuration:
  If no activity for 30 min → Session cleared
  LB stops routing to that backend for client

Tradeoff:
  Shorter timeout = Less memory, security
  Longer timeout = Better UX, more memory
```

**Absolute Timeout**:
```
Timeout: 8 hours

Session expires after:
  8 hours total, regardless of activity

Configuration:
  Session created at 09:00
  Session expires at 17:00
  Even if actively used all day

Typical for:
  Security-sensitive applications
  Banking, healthcare
```

## Session Replication

### Distributed Session Store (Recommended)

**Architecture**:
```
Load Balancer
    ↓
┌───┬───┬───┐
│ BE1│ BE2│ BE3│ Backends
└─┬─┴─┬─┴─┬─┘
  │   │   │
  └───┼───┘
      ↓
  ┌─────────┐
  │ Redis   │ Session Store
  │ Cluster │
  └─────────┘
```

**How It Works**:
```
1. Client connects to Backend 1
   ↓ User creates session
   ↓ Session stored in Redis
   ↓ Cookie contains session ID

2. Client request 2 (LB routes to Backend 2)
   ↓ Backend 2 reads session ID from cookie
   ↓ Backend 2 fetches session from Redis
   ↓ Session restored
   ↓ User continues seamlessly

3. Backend 1 fails
   ↓ Client routes to Backend 3
   ↓ Session still available in Redis
   ↓ Zero disruption (if client doesn't get sticky routed)
```

**Configuration** (Java + Spring):
```xml
<bean id="redisConnectionFactory"
      class="org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory"/>

<bean id="sessionRepository"
      class="org.springframework.session.data.redis.config.annotation.web.http.EnableRedisHttpSession">
  <constructor-arg ref="redisConnectionFactory"/>
</bean>
```

**Configuration** (Node.js + Express):
```javascript
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

const redisClient = createClient();

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: 'secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24 // 24 hours
  }
}));
```

### In-Memory Session Replication

**Pros**:
- Fast (memory-based)
- No external dependency

**Cons**:
- Memory hungry
- Replication overhead
- Complexity

**Not Recommended For**:
- Most scenarios (use Redis instead)
- High session counts
- New deployments

## Handling Session Loss

### Graceful Degradation

**When Backend Fails**:
```
Scenario: Backend 1 fails (where client connected)

Without Session Replication:
  Client session lost
  User logged out
  User must re-login

With Session Replication:
  User continues seamlessly
  LB routes to Backend 2
  Backend 2 retrieves session from store
  User doesn't notice
```

### Session Affinity Failover

**With IP Hash (No Replication)**:
```
Setup:
  Persistence: IP Hash
  Session Location: Backend 1

Backend 1 Fails:
  hash(client_ip) % 3 = 1 (Backend 2)
  New requests route to Backend 2
  But session is gone!
  Solution: Re-login

Better Approach:
  Add session replication
  Or increase down threshold
  Or use cookie persistence
```

## Testing Session Persistence

### Verification Test
```bash
#!/bin/bash
# Test session persistence

URL="http://example.com/login"
SESSION_COOKIE=""

# Step 1: Login (create session)
echo "1. Creating session..."
RESPONSE=$(curl -i -X POST $URL \
  -d "username=test&password=pass" 2>/dev/null)

# Extract session cookie
SESSION_COOKIE=$(echo "$RESPONSE" | grep -i 'Set-Cookie' | \
  sed 's/.*\(JSESSIONID=[^;]*\).*/\1/')

echo "Session cookie: $SESSION_COOKIE"

# Step 2: Make multiple requests (verify same backend)
echo "2. Verifying session persistence..."
for i in {1..5}; do
  echo "Request $i:"
  curl -s "$URL/dashboard" \
    -H "Cookie: $SESSION_COOKIE" | \
    grep -i "Welcome\|Unauthorized"
  sleep 2
done

# Step 3: Delete cookie (test failure)
echo "3. Testing session loss..."
curl -s "$URL/dashboard" | grep -i "login"
```

### Load Test with Session Affinity
```bash
#!/bin/bash
# Load test to verify affinity

# Simulate 100 concurrent users
for i in {1..100}; do
  (
    # Each user: login → access protected resource 10 times
    SESSION=$(curl -s -X POST http://example.com/login \
      -d "user=user$i" | grep -i JSESSIONID)

    for j in {1..10}; do
      curl -s http://example.com/dashboard \
        -H "Cookie: $SESSION" > /dev/null
    done
  ) &
done

wait
echo "Load test complete"
```

## Session Persistence Best Practices

1. **Use Distributed Session Store**
   - Redis, Memcached, or database
   - Better than relying on affinity
   - Survives backend failure

2. **Set Appropriate Timeouts**
   - 30 minutes idle (typical)
   - 8 hours absolute (security)
   - Adjust based on application

3. **Secure Session Cookies**
   - HttpOnly flag (no JavaScript access)
   - Secure flag (HTTPS only)
   - SameSite attribute (CSRF protection)
   - Signed/encrypted if sensitive

4. **Monitor Session Metrics**
   - Active session count
   - Session creation rate
   - Session timeout rate
   - Memory usage

5. **Test Failover**
   - Verify session survives backend failure
   - Test timeout behavior
   - Verify correct backend selection

6. **Document Session Design**
   - Where sessions stored
   - How long persisted
   - Failover behavior
   - Monitoring approach

---

**Last Updated**: 2025-11-19
**Version**: 2.0
