# API Versioning Best Practices

## Table of Contents

1. [Overview](#overview)
2. [URL Path Versioning](#url-path-versioning)
3. [Header-Based Versioning](#header-based-versioning)
4. [Content Negotiation Versioning](#content-negotiation-versioning)
5. [Query Parameter Versioning](#query-parameter-versioning)
6. [Versioning Strategy Comparison](#versioning-strategy-comparison)
7. [Deprecation Policies](#deprecation-policies)
8. [Implementation Patterns](#implementation-patterns)
9. [Production Examples](#production-examples)

---

## Overview

API versioning allows you to make breaking changes while maintaining backward compatibility with existing clients. Without proper versioning, updating your API can break applications that depend on it.

### Why API Versioning Matters

```
Without Versioning:
API v1 released
├─ Clients A, B, C integrate
├─ You need to add required field "email"
├─ New API enforces email
└─ ❌ Clients A, B, C break

With Versioning:
API v1 available at /v1
├─ Clients A, B, C integrate with /v1
├─ You release /v2 with required email
├─ New clients use /v2
├─ Old clients continue using /v1
└─ ✓ No breakage, smooth transition
```

### Versioning Principles

1. **Never break existing APIs** - Support old versions during transition
2. **Clear deprecation timeline** - Announce changes well in advance
3. **Documented migration path** - Help clients upgrade easily
4. **Version selection mechanism** - Clear way to specify version
5. **Consistent across endpoints** - Same strategy everywhere

---

## URL Path Versioning

Embedding version in the URL path is the most common and visible approach.

### Implementation

```
/v1/users          - Version 1 endpoint
/v2/users          - Version 2 endpoint
/v3/users          - Version 3 endpoint
```

### Flask/Python Implementation

```python
from flask import Flask, Blueprint, jsonify, request

app = Flask(__name__)

# Version 1 Blueprint
v1_api = Blueprint('v1', __name__, url_prefix='/api/v1')
v2_api = Blueprint('v2', __name__, url_prefix='/api/v2')

# V1 Endpoints
@v1_api.route('/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    """V1: Returns basic user info"""
    return jsonify({
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    })

@v1_api.route('/users', methods=['POST'])
def create_user_v1():
    """V1: Create user (email optional)"""
    data = request.json
    return jsonify({
        'id': 123,
        'name': data.get('name'),
        'email': data.get('email', '')
    }), 201

# V2 Endpoints - Breaking changes
@v2_api.route('/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    """V2: Returns enhanced user info with roles and metadata"""
    return jsonify({
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com',
        'roles': ['admin', 'user'],
        'metadata': {
            'created_at': '2024-01-15T10:30:00Z',
            'last_login': '2024-11-19T14:22:00Z',
            'account_status': 'active'
        }
    })

@v2_api.route('/users', methods=['POST'])
def create_user_v2():
    """V2: Create user (email required)"""
    data = request.json

    # Validate required field
    if not data.get('email'):
        return jsonify({'error': 'email is required'}), 400

    return jsonify({
        'id': 124,
        'name': data.get('name'),
        'email': data.get('email'),
        'roles': ['user'],
        'metadata': {
            'created_at': '2024-11-19T14:30:00Z',
            'last_login': None,
            'account_status': 'active'
        }
    }), 201

# Register blueprints
app.register_blueprint(v1_api)
app.register_blueprint(v2_api)

# Version information endpoint
@app.route('/api/versions')
def api_versions():
    """List all available API versions"""
    return jsonify({
        'versions': [
            {
                'version': 'v1',
                'status': 'deprecated',
                'deprecation_date': '2025-01-01',
                'sunset_date': '2025-06-01',
                'base_url': '/api/v1'
            },
            {
                'version': 'v2',
                'status': 'current',
                'deprecation_date': None,
                'sunset_date': None,
                'base_url': '/api/v2'
            }
        ]
    })
```

### Express.js/Node.js Implementation

```javascript
const express = require('express');
const app = express();

app.use(express.json());

// V1 Router
const v1Router = express.Router();

v1Router.get('/users/:id', (req, res) => {
  res.json({
    id: req.params.id,
    name: 'John Doe',
    email: 'john@example.com'
  });
});

v1Router.post('/users', (req, res) => {
  res.status(201).json({
    id: 123,
    name: req.body.name,
    email: req.body.email || ''
  });
});

// V2 Router
const v2Router = express.Router();

v2Router.get('/users/:id', (req, res) => {
  res.json({
    id: req.params.id,
    name: 'John Doe',
    email: 'john@example.com',
    roles: ['admin', 'user'],
    metadata: {
      created_at: new Date('2024-01-15'),
      last_login: new Date(),
      account_status: 'active'
    }
  });
});

v2Router.post('/users', (req, res) => {
  // Email is required in V2
  if (!req.body.email) {
    return res.status(400).json({ error: 'email is required' });
  }

  res.status(201).json({
    id: 124,
    name: req.body.name,
    email: req.body.email,
    roles: ['user'],
    metadata: {
      created_at: new Date(),
      last_login: null,
      account_status: 'active'
    }
  });
});

// Register routers
app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

// Version info endpoint
app.get('/api/versions', (req, res) => {
  res.json({
    versions: [
      {
        version: 'v1',
        status: 'deprecated',
        deprecation_date: '2025-01-01',
        sunset_date: '2025-06-01',
        base_url: '/api/v1'
      },
      {
        version: 'v2',
        status: 'current',
        deprecation_date: null,
        sunset_date: null,
        base_url: '/api/v2'
      }
    ]
  });
});

app.listen(3000);
```

### Advantages

- **Explicit and visible** - Version is clear in URL
- **Easy to test** - Different versions can run simultaneously
- **Easy to document** - Each version has separate documentation
- **Browser-friendly** - Can test in browser directly
- **Industry standard** - Most companies use this (AWS, GitHub, Stripe)

### Disadvantages

- **Code duplication** - Need to maintain multiple endpoint versions
- **URL pollution** - URLs become version-specific
- **Increased complexity** - More routes to manage
- **Not truly RESTful** - Version isn't a resource

---

## Header-Based Versioning

Version specified via HTTP header instead of URL.

### Implementation

```
GET /api/users/123
Accept: application/vnd.company.v2+json
```

### Flask Implementation

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

def get_api_version():
    """Extract API version from Accept header"""
    accept_header = request.headers.get('Accept', 'application/vnd.company.v1+json')

    # Parse custom media type: application/vnd.company.v2+json
    if 'vnd.company.v' in accept_header:
        version = accept_header.split('vnd.company.')[1].split('+')[0]
        return version
    return 'v1'  # Default version

def api_route(*args, **kwargs):
    """Decorator to handle version-specific logic"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            version = get_api_version()
            return f(version=version, *args, **kwargs)
        return wrapper
    return app.route(*args, **kwargs)(decorator)

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get user with version-specific response"""
    version = get_api_version()

    base_response = {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    }

    if version == 'v2':
        base_response.update({
            'roles': ['admin'],
            'metadata': {
                'created_at': '2024-01-15T10:30:00Z',
                'last_login': '2024-11-19T14:22:00Z'
            }
        })
    elif version == 'v3':
        base_response.update({
            'roles': ['admin'],
            'permissions': ['read', 'write', 'delete'],
            'metadata': {
                'created_at': '2024-01-15T10:30:00Z',
                'updated_at': '2024-11-19T14:22:00Z',
                'last_login': '2024-11-19T14:22:00Z',
                'profile_complete': True
            }
        })

    return jsonify(base_response)

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create user with version-specific validation"""
    version = get_api_version()
    data = request.json

    # V2 and later require email
    if version in ['v2', 'v3'] and not data.get('email'):
        return jsonify({'error': 'email is required'}), 400

    response = {
        'id': 124,
        'name': data.get('name'),
        'email': data.get('email')
    }

    if version in ['v2', 'v3']:
        response.update({
            'roles': ['user'],
            'metadata': {
                'created_at': '2024-11-19T14:30:00Z',
                'last_login': None
            }
        })

    return jsonify(response), 201
```

### Advantages

- **Clean URLs** - No version in URL path
- **Single endpoint** - Can serve all versions from one route
- **More RESTful** - Resources aren't duplicated
- **Flexible** - Easy to change versioning strategy

### Disadvantages

- **Less visible** - Version hidden in headers
- **Hard to test manually** - Can't visit in browser easily
- **Requires header awareness** - Clients must understand header format
- **Less common** - Not as widely used as URL versioning

---

## Content Negotiation Versioning

Version via Accept header with standard media types.

### MIME Type Strategy

```
GET /api/users/123
Accept: application/json;version=2

OR

Accept: application/vnd.api+json;version=2
```

### Implementation

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

def parse_version_from_accept():
    """Extract version from Accept header"""
    accept = request.headers.get('Accept', '')

    # Parse version parameter: application/json;version=2
    if 'version=' in accept:
        version_str = accept.split('version=')[1].split(',')[0].strip()
        return f"v{version_str}"

    return 'v1'  # Default

def versioned_response(v1_data=None, v2_data=None, v3_data=None):
    """Return appropriate response based on version"""
    version = parse_version_from_accept()

    response_map = {
        'v1': v1_data,
        'v2': v2_data or v1_data,
        'v3': v3_data or v2_data or v1_data
    }

    return jsonify(response_map.get(version, v1_data))

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get user with content negotiation versioning"""

    # V1 response
    v1_response = {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    }

    # V2 response (adds metadata)
    v2_response = {
        **v1_response,
        'roles': ['admin'],
        'metadata': {
            'created_at': '2024-01-15T10:30:00Z',
            'last_login': '2024-11-19T14:22:00Z'
        }
    }

    # V3 response (adds permissions)
    v3_response = {
        **v2_response,
        'permissions': ['read', 'write', 'delete'],
        'metadata': {
            **v2_response['metadata'],
            'updated_at': '2024-11-19T14:22:00Z',
            'profile_complete': True
        }
    }

    return versioned_response(v1_response, v2_response, v3_response)

@app.before_request
def validate_version():
    """Validate requested version is supported"""
    version = parse_version_from_accept()

    supported_versions = ['v1', 'v2', 'v3']
    if version not in supported_versions:
        return jsonify({
            'error': 'unsupported_version',
            'requested_version': version,
            'supported_versions': supported_versions
        }), 406  # Not Acceptable
```

### Advantages

- **Standards-compliant** - Uses HTTP content negotiation
- **Clean URLs** - No version in URL
- **Semantic** - Uses standard media type mechanism
- **Flexible** - Easy to support multiple versions

### Disadvantages

- **Complex** - Requires understanding of media types
- **Hard to debug** - Version hidden in headers
- **Not widely used** - Less familiar to developers
- **Manual header setting** - Requires client support

---

## Query Parameter Versioning

Version specified as query parameter.

### Implementation

```
GET /api/users/123?api_version=2
GET /api/users?v=2
```

### Example

```python
from flask import request, jsonify

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get user with query parameter versioning"""
    version = request.args.get('api_version', 'v1')

    base = {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    }

    if version == 'v2':
        base['roles'] = ['admin']
        base['metadata'] = {'created_at': '2024-01-15T10:30:00Z'}

    return jsonify(base)
```

### Advantages

- **Easy to test** - Can use in browser query string
- **Flexible** - Easy to add multiple parameters

### Disadvantages

- **Not RESTful** - Version should be in URL path, not query
- **Confusing** - Mixes versioning with filtering
- **Caching issues** - Query params affect cache keys
- **Not recommended** - Industry standard discourages this

---

## Versioning Strategy Comparison

### Decision Matrix

| Factor | URL Path | Header | Content Negotiation | Query Param |
|--------|----------|--------|---------------------|-------------|
| **Visibility** | Excellent | Poor | Moderate | Good |
| **Testing** | Excellent | Poor | Moderate | Excellent |
| **RESTfulness** | Fair | Good | Excellent | Poor |
| **Simplicity** | Good | Good | Moderate | Good |
| **Caching** | Good | Excellent | Good | Fair |
| **Documentation** | Excellent | Moderate | Moderate | Good |
| **Adoption** | Excellent | Moderate | Poor | Poor |

### When to Use Each

**Use URL Path Versioning if:**
- You want maximum clarity
- You have significant breaking changes
- You need to support multiple versions simultaneously
- Most of your users are developers (not just integrations)
- You want good SEO (search engines see separate URLs)

**Use Header-Based Versioning if:**
- You want cleaner URLs
- You have minor versioning needs
- Your clients are mostly server-to-server
- You're building internal APIs
- You want flexibility in changing versioning strategy

**Use Content Negotiation if:**
- You follow REST principles strictly
- You have sophisticated client libraries
- You want very flexible versioning
- Your audience is REST-aware developers

**Use Query Parameters if:**
- You need quick backwards compatibility
- Your API doesn't change often
- Simplicity is paramount

---

## Deprecation Policies

Clear deprecation communication prevents surprise breakage.

### Example Deprecation Timeline

```
Timeline for v1 Deprecation:
├─ Week 0: Announce v1 deprecated, v2 current
│   └─ Email all users with migration guide
│
├─ Week 1-12: Deprecation phase (3 months)
│   ├─ V1 still works normally
│   ├─ Responses include deprecation warning
│   ├─ Documentation points to migration
│   └─ Support team helps migrations
│
├─ Week 12-24: Sunset phase (additional 3 months)
│   ├─ V1 returns 410 Gone status
│   ├─ Error message provides migration link
│   ├─ Support escalates for migrations
│   └─ Only critical customers
│
└─ Week 24: Complete removal
    └─ V1 endpoints removed entirely
```

### Implementation

```python
from flask import request, jsonify, g
from datetime import datetime, timedelta

DEPRECATION_DATES = {
    'v1': {
        'deprecated_date': datetime(2024, 12, 1),
        'sunset_date': datetime(2025, 6, 1),
        'removal_date': datetime(2025, 9, 1)
    },
    'v2': {
        'deprecated_date': None,  # Not deprecated
        'sunset_date': None,
        'removal_date': None
    }
}

def check_deprecation(version):
    """Check if version is deprecated and add headers"""
    dates = DEPRECATION_DATES.get(version)

    if not dates or not dates['deprecated_date']:
        return True  # Version OK

    now = datetime.now()
    deprecated_date = dates['deprecated_date']
    sunset_date = dates['sunset_date']

    # Still accepting requests (deprecation phase)
    if now < sunset_date:
        g.deprecation_warning = True
        g.sunset_date = sunset_date
        return True

    # Sunset date passed
    return False

@app.before_request
def validate_version_status():
    """Reject requests to versions past sunset"""
    if request.path.startswith('/api/v'):
        version_str = request.path.split('/')[2]  # Extract v1, v2, etc

        if not check_deprecation(version_str):
            dates = DEPRECATION_DATES[version_str]
            return jsonify({
                'error': 'version_no_longer_supported',
                'version': version_str,
                'removal_date': dates['removal_date'].isoformat(),
                'migration_guide': 'https://docs.example.com/migration-guide'
            }), 410

@app.after_request
def add_deprecation_headers(response):
    """Add deprecation warnings to response headers"""
    if hasattr(g, 'deprecation_warning') and g.deprecation_warning:
        sunset_date = g.sunset_date.isoformat()
        response.headers['Deprecation'] = 'true'
        response.headers['Sunset'] = sunset_date
        response.headers['Warning'] = (
            f'299 - "API version deprecated, '
            f'will be removed on {sunset_date}"'
        )

    return response

@app.route('/api/deprecation-schedule')
def deprecation_schedule():
    """Public endpoint for version status"""
    schedule = {}

    for version, dates in DEPRECATION_DATES.items():
        if not dates['deprecated_date']:
            status = 'current'
        elif datetime.now() < dates['sunset_date']:
            status = 'deprecated'
        else:
            status = 'removed'

        schedule[version] = {
            'status': status,
            'deprecated_date': dates['deprecated_date'].isoformat() if dates['deprecated_date'] else None,
            'sunset_date': dates['sunset_date'].isoformat() if dates['sunset_date'] else None,
            'removal_date': dates['removal_date'].isoformat() if dates['removal_date'] else None,
            'migration_guide': 'https://docs.example.com/migration-guides'
        }

    return jsonify(schedule)
```

### Communication

```python
def send_deprecation_notification(users):
    """Notify users about deprecation"""
    for user in users:
        email_template = f"""
        Dear {user.name},

        We're deprecating API v1 on {DEPRECATION_DATES['v1']['sunset_date'].strftime('%B %d, %Y')}.

        Your account is currently using v1 endpoints.

        Migration Steps:
        1. Review the migration guide: https://docs.example.com/v1-to-v2-migration
        2. Update your API calls to use /api/v2 instead of /api/v1
        3. Test thoroughly in your development environment
        4. Deploy to production before {DEPRECATION_DATES['v1']['sunset_date']}

        Questions? Contact support@example.com

        Best regards,
        API Team
        """

        send_email(user.email, 'API v1 Deprecation Notice', email_template)
```

---

## Implementation Patterns

### Shared Logic Between Versions

```python
class UserService:
    """Shared business logic across versions"""

    @staticmethod
    def get_user(user_id):
        """Get user from database"""
        return {
            'id': user_id,
            'name': 'John Doe',
            'email': 'john@example.com'
        }

    @staticmethod
    def get_user_with_metadata(user_id):
        """Get user with additional metadata"""
        user = UserService.get_user(user_id)
        user['roles'] = ['admin']
        user['metadata'] = {
            'created_at': '2024-01-15T10:30:00Z',
            'last_login': '2024-11-19T14:22:00Z'
        }
        return user

# V1 Endpoint
@v1_api.route('/users/<int:user_id>')
def get_user_v1(user_id):
    return jsonify(UserService.get_user(user_id))

# V2 Endpoint
@v2_api.route('/users/<int:user_id>')
def get_user_v2(user_id):
    return jsonify(UserService.get_user_with_metadata(user_id))
```

### Response Transformers

```python
class ResponseTransformer:
    """Transform responses between versions"""

    @staticmethod
    def v1_to_v2(v1_response):
        """Upgrade v1 response to v2"""
        return {
            **v1_response,
            'roles': ['user'],
            'metadata': {
                'created_at': '2024-01-15T10:30:00Z'
            }
        }

    @staticmethod
    def v2_to_v1(v2_response):
        """Downgrade v2 response to v1"""
        v1_response = v2_response.copy()
        del v1_response['roles']
        del v1_response['metadata']
        return v1_response
```

---

## Production Examples

### Stripe API Versioning

Stripe uses URL path versioning with account-specific API versions:

```
Account-specific API version:
GET /v1/charges?api_version=2024-04-01

Always uses latest:
GET /v1/charges

URL patterns:
/v1/charges      - Charges resource
/v1/customers    - Customers resource
/v1/subscriptions - Subscriptions resource
```

### Twilio Versioning

Twilio uses URL path versioning:

```
/2010-04-01/Accounts/{AccountSid}/Messages.json
/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}
/2010-04-01/Addresses/{AddressSid}
```

The date format (2010-04-01) represents the API version released on that date.

### GitHub API Versioning

GitHub uses header-based versioning:

```
Accept: application/vnd.github.v3+json
Accept: application/vnd.github+json

Also supports preview headers for beta features:
Accept: application/vnd.github.symmetra-preview+json
```

### Slack API Versioning

Slack uses query parameter versioning in some cases:

```
POST https://slack.com/api/chat.postMessage?token=...

Uses Content-Type header for JSON format:
Content-Type: application/json

Web API is typically "v1" but not explicitly versioned
```

---

## Monitoring Version Usage

```python
from datetime import datetime, timedelta
import redis

class VersionUsageMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client

    def track_request(self, version, endpoint, status_code):
        """Track API request statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"api:usage:{version}:{endpoint}:{today}"

        # Track total requests
        self.redis.incr(f"{key}:total")

        # Track status codes
        self.redis.incr(f"{key}:status:{status_code}")

        # Track hourly usage
        hour_key = f"api:usage:hourly:{version}:{datetime.now().hour}"
        self.redis.incr(hour_key)

    def get_version_statistics(self, version, days=30):
        """Get usage statistics for a version"""
        stats = {
            'version': version,
            'total_requests': 0,
            'deprecated': False,
            'endpoints': {},
            'daily_usage': []
        }

        # Aggregate daily stats
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            # ... aggregate logic

        return stats

    def alert_on_version_spike(self, version, threshold=1000):
        """Alert if usage spikes unusually"""
        hour_key = f"api:usage:hourly:{version}:{datetime.now().hour}"
        usage = int(self.redis.get(hour_key) or 0)

        if usage > threshold:
            send_alert(f"Unusual spike for {version}: {usage} requests")

    def identify_deprecated_version_users(self, deprecated_version):
        """Find users still using deprecated versions"""
        # Query logs for requests to deprecated version
        # Generate list of affected users
        # Return for notification
        pass
```

---

## Checklist for API Versioning

- [ ] Choose versioning strategy and document it
- [ ] Implement version routing/selection mechanism
- [ ] Create deprecation policy and timeline
- [ ] Set up monitoring for version usage
- [ ] Document migration paths between versions
- [ ] Implement version-specific response transformers
- [ ] Add version information endpoints
- [ ] Include deprecation headers in responses
- [ ] Set up automated alerts for deprecated version usage
- [ ] Create clear migration guides for each upgrade
- [ ] Notify users before deprecation dates
- [ ] Test thoroughly with multiple API versions
- [ ] Monitor for unintended breaking changes
- [ ] Track adoption of new versions
- [ ] Plan graceful sunset of old versions

---

## References

- [Semantic Versioning](https://semver.org/)
- [REST API Versioning (Nordic APIs)](https://nordicapis.com/api-versioning-good-practices/)
- [Web API Design Best Practices (Microsoft)](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design)
- [API Versioning Strategy (InfoQ)](https://www.infoq.com/articles/api-versioning/)
- [Stripe API Versioning](https://stripe.com/docs/api/versioning)
- [GitHub API Versioning](https://docs.github.com/en/rest/overview/api-versions)
