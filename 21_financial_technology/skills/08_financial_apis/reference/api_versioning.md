# API Versioning Strategies

## Versioning Overview

API versioning allows systems to evolve while maintaining backward compatibility.

## Versioning Strategies

### 1. URL Path Versioning
**Format**: `https://api.example.com/v1/accounts`

**Advantages**:
- Clear and explicit
- Easy to route
- Simple client implementation
- Works with CDNs/caching

**Disadvantages**:
- Different URLs for same resource
- Duplicated code for multiple versions
- Multiple deployments required

**Implementation**:
```python
from flask import Flask, Blueprint

app = Flask(__name__)

# Version 1 endpoints
v1_bp = Blueprint('v1', __name__, url_prefix='/v1')

@v1_bp.route('/accounts', methods=['GET'])
def get_accounts_v1():
    """V1 endpoint - basic account info"""
    return {
        "accounts": [
            {
                "id": "acc-1",
                "iban": "DE89...",
                "currency": "EUR"
            }
        ]
    }

# Version 2 endpoints
v2_bp = Blueprint('v2', __name__, url_prefix='/v2')

@v2_bp.route('/accounts', methods=['GET'])
def get_accounts_v2():
    """V2 endpoint - enhanced with extra fields"""
    return {
        "accounts": [
            {
                "id": "acc-1",
                "iban": "DE89...",
                "currency": "EUR",
                "displayName": "My Account",
                "status": "ENABLED",
                "accountType": "CACC"
            }
        ]
    }

app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)
```

### 2. Header-Based Versioning
**Format**: `Accept-Version: 1.3`

**Advantages**:
- Single URL
- Client can switch versions without code change
- RESTful approach

**Disadvantages**:
- Less visible in browser
- Requires header parsing
- More complex routing

**Implementation**:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_api_version(headers):
    """Extract API version from headers"""
    version = headers.get('Accept-Version', '1.0')
    # Parse version
    return version

@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Handle account retrieval for any version"""
    version = get_api_version(request.headers)

    if version.startswith('1.'):
        return get_accounts_v1()
    elif version.startswith('2.'):
        return get_accounts_v2()
    else:
        return jsonify({"error": "Unsupported version"}), 400

def get_accounts_v1():
    """V1 response format"""
    return {"accounts": [...]}

def get_accounts_v2():
    """V2 response format"""
    return {"accounts": [...]}
```

### 3. Content Negotiation Versioning
**Format**: `Accept: application/vnd.api.v2+json`

**Advantages**:
- True REST approach
- Single URL
- Industry standard

**Disadvantages**:
- Complex implementation
- Less intuitive for clients
- More processing required

**Implementation**:
```python
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def parse_accept_header():
    """Parse custom Accept header for version"""
    accept = request.headers.get('Accept', 'application/json')

    # Match pattern: application/vnd.api.v2+json
    match = re.search(r'application/vnd\.api\.v(\d+)\+json', accept)

    if match:
        return int(match.group(1))

    return 1  # Default to version 1

@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Handle account retrieval"""
    version = parse_accept_header()

    if version == 1:
        response = get_accounts_v1()
    elif version == 2:
        response = get_accounts_v2()
    else:
        return jsonify({"error": "Unsupported version"}), 406

    return response
```

## Semantic Versioning

**Format**: `MAJOR.MINOR.PATCH`

```
1.2.3
├─ 1: Major version (breaking changes)
├─ 2: Minor version (backward-compatible features)
└─ 3: Patch version (bug fixes)
```

**Rules**:
- MAJOR: Increment for breaking changes (v1 → v2)
- MINOR: Increment for new features (v1.0 → v1.1)
- PATCH: Increment for bug fixes (v1.1.0 → v1.1.1)

**Examples**:
```
1.0.0 → Initial release
1.1.0 → Add new fields (backward compatible)
1.1.1 → Fix bug
1.2.0 → Add new endpoints
2.0.0 → Remove deprecated endpoints (breaking change)
```

## Migration Strategies

### Sunset Timeline
```
Timeline for API Deprecation:

v1 Released: Jan 2023
v2 Released: Jan 2024
├─ v1 Deprecated: May 2024
├─ v1 Rate Limited: Sep 2024 (slower service)
└─ v1 Removed: Jan 2025

Client Actions:
May 2024: Update to v2 (grace period)
Sep 2024: Move to v2 (degraded performance)
Jan 2025: v1 inaccessible, move to v2 required
```

### Backward Compatibility Layers
```python
class VersionAdapter:
    """Adapt v1 requests to v2 implementation"""

    def handle_v1_request(self, endpoint, params):
        """
        Convert v1 request to v2 format
        """
        # Map v1 parameters to v2
        v2_params = self.adapt_params(params)

        # Call v2 implementation
        v2_result = self.handle_v2_request(endpoint, v2_params)

        # Convert v2 response back to v1 format
        v1_response = self.adapt_response(v2_result)

        return v1_response

    def adapt_params(self, v1_params):
        """Convert v1 parameters to v2 format"""
        return {
            "limit": v1_params.get("pageSize", 20),
            "offset": (v1_params.get("page", 1) - 1) * v1_params.get("pageSize", 20)
        }

    def adapt_response(self, v2_response):
        """Convert v2 response to v1 format"""
        return {
            "accounts": v2_response["accounts"],
            "page": 1,
            "pageSize": len(v2_response["accounts"]),
            "total": 100
        }
```

## Breaking Changes Handling

### Field Additions (Non-Breaking)
```
v1 Response:
{
  "accountId": "acc-1",
  "iban": "DE89..."
}

v2 Response:
{
  "accountId": "acc-1",
  "iban": "DE89...",
  "displayName": "My Account",  // NEW FIELD
  "status": "ENABLED"           // NEW FIELD
}

✓ Backward compatible - v1 clients ignore new fields
```

### Field Removals (Breaking)
```
v1 Response:
{
  "accountId": "acc-1",
  "iban": "DE89...",
  "accountNumber": "123456"
}

v2 Response:
{
  "accountId": "acc-1",
  "iban": "DE89..."
  // accountNumber REMOVED
}

✗ Breaking change - v1 clients expect accountNumber
```

### Endpoint Changes (Breaking)
```
v1: GET /transactions/123
v2: GET /accounts/acc-1/transactions/123

✗ Breaking change - different URL structure
→ Need migration guide for clients
```

### Response Format Changes (Breaking)
```
v1 Response:
{
  "balance": 1000.00
}

v2 Response:
{
  "balanceAmount": {
    "amount": "1000.00",
    "currency": "EUR"
  }
}

✗ Breaking change - different structure
```

## Version Documentation

### OpenAPI Specification with Versions
```yaml
openapi: 3.0.0
info:
  title: Financial API
  version: 2.1.0

servers:
  - url: https://api.example.com/v2
    description: Current version
  - url: https://api.example.com/v1
    description: Deprecated (sunsets Jan 2025)

paths:
  /accounts:
    get:
      summary: List accounts
      deprecated: false  # v2
      operationId: listAccountsV2
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  accounts:
                    type: array
                    items:
                      $ref: '#/components/schemas/Account'

components:
  schemas:
    Account:
      type: object
      required:
        - accountId
        - iban
        - currency
      properties:
        accountId:
          type: string
          example: "acc-123"
        iban:
          type: string
          example: "DE89370400440532013000"
        currency:
          type: string
          example: "EUR"
        displayName:
          type: string
          example: "My Checking Account"
          description: New in v2.0
```

## Client Version Management

### User Agent Header
```
User-Agent: MyApp/1.2.3 (FinanceSDK/2.0.1)
```

### Version Pinning
```python
class VersionedAPIClient:
    def __init__(self, api_key, api_version="1.3"):
        self.api_key = api_key
        self.api_version = api_version
        self.session = requests.Session()

    def get_accounts(self):
        """Get accounts using pinned version"""
        response = self.session.get(
            f"https://api.example.com/v{self.api_version}/accounts",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "MyApp/1.0.0"
            }
        )

        return response.json()

    def upgrade_to_version(self, new_version):
        """Upgrade client to new API version"""
        self.api_version = new_version
        # Run any migration code needed
        self.validate_compatibility()

    def validate_compatibility(self):
        """Ensure client is compatible with new version"""
        # Check version features
        # Run compatibility tests
        pass
```

## Version Support Policy

```
Support Timeline:

Version 1.x
  └─ v1.0 - v1.5: Released Jan 2023
     ├─ Security fixes: Until Jan 2025
     ├─ Bug fixes: Until Jul 2024
     ├─ New features: Until Jan 2024
     └─ Rate limited: From Sep 2024

Version 2.x
  ├─ v2.0: Released Jan 2024
  │  └─ Full support
  │
  ├─ v2.1: Released Mar 2024
  │  └─ Full support
  │
  └─ v2.2: Released Jul 2024
     └─ Full support

Support Levels:
├─ Full Support: All types of updates
├─ Security & Bugs: Only critical fixes
└─ Deprecated: No updates, migration required
```

## Versioning Best Practices

1. **Plan for Versioning**: Design APIs with evolution in mind
2. **Communicate Changes**: Announce deprecations 6-12 months ahead
3. **Provide Migration Path**: Clear documentation and tools
4. **Support Multiple Versions**: Run 2+ versions concurrently
5. **Use Semantic Versioning**: Clear version numbering
6. **Document Breaking Changes**: Explicit changelog entries
7. **Maintain Backward Compatibility**: Add, don't remove
8. **Test Thoroughly**: Ensure both versions work correctly

## References

- Semantic Versioning: https://semver.org/
- API Versioning: https://restfulapi.net/versioning/
- OpenAPI Versioning: https://swagger.io/docs/specification/
