# API Versioning & Evolution

## Table of Contents
- [Introduction](#introduction)
- [Versioning Strategies](#versioning-strategies)
- [Backward Compatibility](#backward-compatibility)
- [Breaking Changes Management](#breaking-changes-management)
- [Deprecation Strategies](#deprecation-strategies)
- [API Lifecycle Management](#api-lifecycle-management)
- [Migration Patterns](#migration-patterns)
- [Real-World Examples](#real-world-examples)
- [Documentation & Communication](#documentation--communication)
- [Best Practices](#best-practices)

## Introduction

API versioning is critical for evolving APIs while maintaining compatibility with existing clients. Poor versioning strategies lead to broken integrations, unhappy users, and technical debt. This guide covers proven patterns for API evolution.

### Why Versioning Matters

- **Client Stability**: Existing clients continue to work as APIs evolve
- **Gradual Migration**: Clients upgrade at their own pace
- **Innovation**: Add new features without breaking existing functionality
- **Risk Management**: Test changes without impacting production users
- **Clear Communication**: Version numbers convey compatibility expectations

## Versioning Strategies

### 1. URI Path Versioning

Most common and explicit approach - version in URL path.

```python
from flask import Flask, jsonify
from typing import Dict, Any

app = Flask(__name__)

# Version 1 API
@app.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user_v1(user_id: str) -> Dict[str, Any]:
    """
    V1: Returns basic user information
    Response: {
        "id": "123",
        "name": "John Doe",
        "email": "john@example.com"
    }
    """
    user = get_user_from_db(user_id)

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

# Version 2 API - Enhanced with additional fields
@app.route('/api/v2/users/<user_id>', methods=['GET'])
def get_user_v2(user_id: str) -> Dict[str, Any]:
    """
    V2: Returns enhanced user information with metadata
    Response: {
        "id": "123",
        "profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "avatar": "https://..."
        },
        "metadata": {
            "createdAt": "2024-01-01T00:00:00Z",
            "lastLogin": "2024-01-15T12:30:00Z"
        }
    }
    """
    user = get_user_from_db(user_id)

    return jsonify({
        'id': user.id,
        'profile': {
            'name': user.name,
            'email': user.email,
            'avatar': user.avatar_url
        },
        'metadata': {
            'createdAt': user.created_at.isoformat(),
            'lastLogin': user.last_login.isoformat() if user.last_login else None
        }
    })

# Version 3 API - Breaking change in data structure
@app.route('/api/v3/users/<user_id>', methods=['GET'])
def get_user_v3(user_id: str) -> Dict[str, Any]:
    """
    V3: Complete restructure with HATEOAS links
    Response: {
        "data": {
            "type": "user",
            "id": "123",
            "attributes": {...},
            "relationships": {...}
        },
        "links": {...}
    }
    """
    user = get_user_from_db(user_id)

    return jsonify({
        'data': {
            'type': 'user',
            'id': user.id,
            'attributes': {
                'name': user.name,
                'email': user.email,
                'avatar': user.avatar_url
            },
            'relationships': {
                'posts': {
                    'links': {
                        'related': f'/api/v3/users/{user.id}/posts'
                    }
                }
            }
        },
        'links': {
            'self': f'/api/v3/users/{user.id}'
        }
    })

# AWS Lambda implementation
def lambda_handler(event, context):
    """Route to correct version based on path"""
    path = event['path']

    if path.startswith('/api/v1/'):
        return handle_v1_request(event, context)
    elif path.startswith('/api/v2/'):
        return handle_v2_request(event, context)
    elif path.startswith('/api/v3/'):
        return handle_v3_request(event, context)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'API version not found'})
        }
```

**Pros:**
- Clear and explicit
- Easy to route and cache
- Visible in logs and monitoring

**Cons:**
- Clutters URIs
- Can't version individual endpoints
- May duplicate code

### 2. Header Versioning

Version specified in HTTP header.

```python
from functools import wraps
from typing import Callable

def version_header(supported_versions: list[str] = None):
    """Decorator for header-based versioning"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event, context):
            # Get version from header
            headers = event.get('headers', {})
            api_version = headers.get('API-Version') or headers.get('api-version')

            if not api_version:
                # Default to latest version
                api_version = 'v3'

            # Validate version
            if supported_versions and api_version not in supported_versions:
                return {
                    'statusCode': 400,
                    'headers': {
                        'X-Supported-Versions': ', '.join(supported_versions)
                    },
                    'body': json.dumps({
                        'error': f'Unsupported API version: {api_version}',
                        'supportedVersions': supported_versions
                    })
                }

            # Add version to event
            event['apiVersion'] = api_version

            return func(event, context)

        return wrapper
    return decorator

@version_header(supported_versions=['v1', 'v2', 'v3'])
def get_user_handler(event, context):
    """Handler supporting multiple versions via headers"""
    user_id = event['pathParameters']['id']
    version = event['apiVersion']

    user = get_user_from_db(user_id)

    # Return different response based on version
    if version == 'v1':
        return {
            'statusCode': 200,
            'headers': {'API-Version': 'v1'},
            'body': json.dumps({
                'id': user.id,
                'name': user.name,
                'email': user.email
            })
        }

    elif version == 'v2':
        return {
            'statusCode': 200,
            'headers': {'API-Version': 'v2'},
            'body': json.dumps({
                'id': user.id,
                'profile': {
                    'name': user.name,
                    'email': user.email
                },
                'metadata': {
                    'createdAt': user.created_at.isoformat()
                }
            })
        }

    elif version == 'v3':
        return {
            'statusCode': 200,
            'headers': {'API-Version': 'v3'},
            'body': json.dumps({
                'data': {
                    'type': 'user',
                    'id': user.id,
                    'attributes': {
                        'name': user.name,
                        'email': user.email
                    }
                }
            })
        }
```

**Pros:**
- Clean URIs
- Can version individual endpoints
- Flexible

**Cons:**
- Less visible
- Harder to cache
- Can be forgotten by clients

### 3. Content Negotiation

Version specified via Accept header (RESTful approach).

```python
def content_negotiation_handler(event, context):
    """Version based on Accept header"""
    headers = event.get('headers', {})
    accept = headers.get('Accept', 'application/json')

    user_id = event['pathParameters']['id']
    user = get_user_from_db(user_id)

    # Parse Accept header
    if 'application/vnd.myapi.v1+json' in accept:
        response_body = {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
        content_type = 'application/vnd.myapi.v1+json'

    elif 'application/vnd.myapi.v2+json' in accept:
        response_body = {
            'id': user.id,
            'profile': {
                'name': user.name,
                'email': user.email
            }
        }
        content_type = 'application/vnd.myapi.v2+json'

    elif 'application/vnd.myapi.v3+json' in accept:
        response_body = {
            'data': {
                'type': 'user',
                'id': user.id,
                'attributes': {
                    'name': user.name,
                    'email': user.email
                }
            }
        }
        content_type = 'application/vnd.myapi.v3+json'

    else:
        # Default to latest version
        response_body = {
            'data': {
                'type': 'user',
                'id': user.id,
                'attributes': {
                    'name': user.name,
                    'email': user.email
                }
            }
        }
        content_type = 'application/vnd.myapi.v3+json'

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': content_type,
            'Vary': 'Accept'
        },
        'body': json.dumps(response_body)
    }
```

**Pros:**
- RESTful and standards-compliant
- Clean URIs
- Supports multiple representation formats

**Cons:**
- Complex for clients
- Harder to test in browser
- Requires careful header parsing

### 4. Semantic Versioning

Use semantic versioning (MAJOR.MINOR.PATCH) for clarity.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class APIVersion:
    """Semantic version representation"""
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> 'APIVersion':
        """Parse version string like 'v2.1.3' or '2.1.3'"""
        version_str = version_str.lstrip('v')
        parts = version_str.split('.')

        return cls(
            major=int(parts[0]),
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, other: 'APIVersion') -> bool:
        """Check if versions are compatible (same major version)"""
        return self.major == other.major

    def is_newer_than(self, other: 'APIVersion') -> bool:
        """Check if this version is newer"""
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch

class SemanticVersioning:
    """API versioning using semantic versioning"""

    def __init__(self):
        self.current_version = APIVersion(3, 1, 0)
        self.minimum_supported = APIVersion(2, 0, 0)

    def validate_version(self, requested_version: str) -> Optional[APIVersion]:
        """Validate requested version"""
        try:
            version = APIVersion.from_string(requested_version)

            # Check if version is supported
            if version.is_newer_than(self.current_version):
                raise ValueError(f"Version {version} not yet available")

            if self.minimum_supported.is_newer_than(version):
                raise ValueError(f"Version {version} no longer supported")

            return version

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {requested_version}")

    def get_sunset_date(self, version: APIVersion) -> Optional[str]:
        """Get sunset date for a version"""
        sunset_dates = {
            '1.0.0': '2023-12-31',
            '1.1.0': '2023-12-31',
            '2.0.0': '2024-12-31'
        }

        return sunset_dates.get(str(version))
```

## Backward Compatibility

### Additive Changes (Non-Breaking)

```python
class BackwardCompatibility:
    """Ensure backward compatibility when evolving APIs"""

    @staticmethod
    def add_optional_field(data: dict, field_name: str, value: Any) -> dict:
        """
        Safe: Adding optional fields is backward compatible
        Existing clients will ignore new fields
        """
        return {**data, field_name: value}

    @staticmethod
    def add_new_endpoint(router):
        """
        Safe: Adding new endpoints doesn't break existing clients
        """
        @router.get('/api/v1/users/{id}/preferences')
        def get_user_preferences(id: str):
            # New endpoint - doesn't affect existing clients
            pass

    @staticmethod
    def add_optional_query_param(handler):
        """
        Safe: Adding optional query parameters
        """
        def wrapper(event, context):
            # New optional parameter with default
            include_metadata = event.get('queryStringParameters', {}).get(
                'include_metadata', 'false'
            ) == 'true'

            result = handler(event, context)

            if include_metadata:
                # Add metadata if requested
                result['metadata'] = {...}

            return result

        return wrapper

    @staticmethod
    def extend_enum_values():
        """
        Safe: Adding new enum values (if clients handle unknown values)
        """
        class UserStatus(str, Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"
            SUSPENDED = "suspended"
            # New value added
            PENDING_VERIFICATION = "pending_verification"

# Example: Evolving response while maintaining compatibility
def get_user_compatible(user_id: str, api_version: str) -> dict:
    """Return user data compatible with requested version"""
    user = get_user_from_db(user_id)

    # Base response (v1 compatible)
    response = {
        'id': user.id,
        'name': user.name,
        'email': user.email
    }

    # Additive changes for v2+
    if api_version >= 'v2':
        response['createdAt'] = user.created_at.isoformat()
        response['lastLogin'] = user.last_login.isoformat() if user.last_login else None

    # Additive changes for v3+
    if api_version >= 'v3':
        response['avatar'] = user.avatar_url
        response['preferences'] = {
            'theme': user.theme,
            'notifications': user.notifications_enabled
        }

    return response
```

### Breaking Changes (Avoid or Manage Carefully)

```python
class BreakingChanges:
    """Identify and manage breaking changes"""

    BREAKING_CHANGES = [
        "Removing fields from response",
        "Renaming fields",
        "Changing field types",
        "Adding required request fields",
        "Changing endpoint URLs",
        "Removing endpoints",
        "Changing error response format",
        "Changing authentication method"
    ]

    @staticmethod
    def rename_field_with_alias(old_name: str, new_name: str):
        """
        Breaking: Renaming a field
        Mitigation: Support both names during transition
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                # Support both old and new field names
                if new_name in result and old_name not in result:
                    result[old_name] = result[new_name]  # Alias

                return result

            return wrapper
        return decorator

    @staticmethod
    def change_field_type_with_conversion():
        """
        Breaking: Changing field type
        Mitigation: Provide both formats during transition
        """
        def convert_response(response: dict, api_version: str) -> dict:
            # V1: amount is string
            # V2: amount is integer (cents)

            if api_version == 'v1':
                # Convert integer to string for v1 clients
                if 'amount' in response and isinstance(response['amount'], int):
                    response['amount'] = f"${response['amount'] / 100:.2f}"

            return response

        return convert_response

    @staticmethod
    def remove_field_with_deprecation(field_name: str, deprecation_notice: str):
        """
        Breaking: Removing a field
        Mitigation: Mark as deprecated, return null/empty, remove in next major version
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                # Include deprecated field with warning
                result[field_name] = None
                result['_deprecations'] = result.get('_deprecations', [])
                result['_deprecations'].append({
                    'field': field_name,
                    'message': deprecation_notice,
                    'removedIn': 'v4.0.0'
                })

                return result

            return wrapper
        return decorator
```

## Deprecation Strategies

### Graceful Deprecation Process

```python
from datetime import datetime, timedelta
from typing import Optional
import warnings

class DeprecationManager:
    """Manage API deprecations"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.deprecations_table = self.dynamodb.Table('APIDeprecations')

    def deprecate_endpoint(self, endpoint: str, version: str,
                          sunset_date: str, replacement: str):
        """Mark endpoint as deprecated"""
        self.deprecations_table.put_item(Item={
            'endpoint': endpoint,
            'version': version,
            'sunsetDate': sunset_date,
            'replacement': replacement,
            'deprecatedAt': datetime.utcnow().isoformat()
        })

    def get_deprecation_info(self, endpoint: str, version: str) -> Optional[dict]:
        """Get deprecation information for endpoint"""
        response = self.deprecations_table.get_item(
            Key={
                'endpoint': endpoint,
                'version': version
            }
        )

        return response.get('Item')

    def add_deprecation_headers(self, endpoint: str, version: str,
                               response_headers: dict) -> dict:
        """Add deprecation headers to response"""
        deprecation = self.get_deprecation_info(endpoint, version)

        if deprecation:
            response_headers.update({
                'Deprecation': f'version="{version}"',
                'Sunset': deprecation['sunsetDate'],
                'Link': f'<{deprecation["replacement"]}>; rel="alternate"',
                'Warning': f'299 - "This endpoint is deprecated and will be removed on {deprecation["sunsetDate"]}"'
            })

        return response_headers

def deprecated_endpoint(sunset_date: str, replacement: str):
    """Decorator to mark endpoint as deprecated"""

    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            # Execute function
            result = func(event, context)

            # Add deprecation headers
            headers = result.get('headers', {})
            headers.update({
                'Deprecation': 'true',
                'Sunset': sunset_date,
                'Link': f'<{replacement}>; rel="alternate"',
                'X-API-Warn': f'This endpoint is deprecated. Please migrate to {replacement} before {sunset_date}'
            })

            result['headers'] = headers

            # Log deprecation usage
            log_deprecation_usage(event['path'], event.get('user', {}).get('id'))

            return result

        return wrapper
    return decorator

# Usage
@deprecated_endpoint(
    sunset_date='2024-12-31',
    replacement='/api/v3/users'
)
def get_users_v1(event, context):
    """V1 endpoint - deprecated"""
    users = list_users()

    return {
        'statusCode': 200,
        'body': json.dumps({'users': users})
    }

def log_deprecation_usage(endpoint: str, user_id: Optional[str]):
    """Log usage of deprecated endpoints for monitoring"""
    cloudwatch = boto3.client('cloudwatch')

    cloudwatch.put_metric_data(
        Namespace='API/Deprecations',
        MetricData=[{
            'MetricName': 'DeprecatedEndpointUsage',
            'Value': 1,
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'Endpoint', 'Value': endpoint},
                {'Name': 'UserId', 'Value': user_id or 'anonymous'}
            ]
        }]
    )
```

### Communication Strategy

```python
class DeprecationCommunication:
    """Communicate deprecations to API consumers"""

    def __init__(self):
        self.ses = boto3.client('ses')
        self.sns = boto3.client('sns')

    def notify_deprecation_30_days(self, endpoint: str, affected_users: list[str]):
        """Notify users 30 days before sunset"""
        subject = f"Action Required: API Endpoint {endpoint} Deprecation"
        message = f"""
        Dear API User,

        This is a notice that the API endpoint {endpoint} will be deprecated
        and removed in 30 days.

        Deprecation Date: {datetime.utcnow().date()}
        Sunset Date: {(datetime.utcnow() + timedelta(days=30)).date()}

        Action Required:
        - Update your applications to use the new endpoint
        - Review the migration guide: https://docs.api.example.com/migration
        - Test your integration before the sunset date

        Questions? Contact api-support@example.com

        Best regards,
        API Team
        """

        for user_email in affected_users:
            self.ses.send_email(
                Source='api-noreply@example.com',
                Destination={'ToAddresses': [user_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': message}}
                }
            )

    def notify_deprecation_7_days(self, endpoint: str, affected_users: list[str]):
        """Final warning 7 days before sunset"""
        # Similar to above with urgent messaging
        pass

    def identify_affected_users(self, endpoint: str, version: str) -> list[str]:
        """Identify users still calling deprecated endpoint"""
        # Query CloudWatch Logs or access logs
        logs = boto3.client('logs')

        query = f"""
        fields @timestamp, userContext.user_id
        | filter path = "{endpoint}" and apiVersion = "{version}"
        | stats count() by userContext.user_id
        """

        # Execute log query and return user IDs
        # ...
        return []
```

## API Lifecycle Management

### Comprehensive Lifecycle

```python
from enum import Enum

class APILifecycleStage(str, Enum):
    """API lifecycle stages"""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    ALPHA = "alpha"
    BETA = "beta"
    GA = "general_availability"  # Production
    DEPRECATED = "deprecated"
    SUNSET = "sunset"

class APILifecycleManager:
    """Manage complete API lifecycle"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.versions_table = self.dynamodb.Table('APIVersions')

    def create_version(self, version: str, stage: APILifecycleStage):
        """Create new API version"""
        self.versions_table.put_item(Item={
            'version': version,
            'stage': stage,
            'createdAt': datetime.utcnow().isoformat(),
            'features': [],
            'breakingChanges': [],
            'releaseNotes': ''
        })

    def transition_stage(self, version: str, new_stage: APILifecycleStage):
        """Transition version to new lifecycle stage"""
        allowed_transitions = {
            APILifecycleStage.PLANNING: [APILifecycleStage.DEVELOPMENT],
            APILifecycleStage.DEVELOPMENT: [APILifecycleStage.ALPHA],
            APILifecycleStage.ALPHA: [APILifecycleStage.BETA],
            APILifecycleStage.BETA: [APILifecycleStage.GA],
            APILifecycleStage.GA: [APILifecycleStage.DEPRECATED],
            APILifecycleStage.DEPRECATED: [APILifecycleStage.SUNSET]
        }

        # Get current stage
        response = self.versions_table.get_item(Key={'version': version})
        current_stage = APILifecycleStage(response['Item']['stage'])

        # Validate transition
        if new_stage not in allowed_transitions.get(current_stage, []):
            raise ValueError(
                f"Invalid transition from {current_stage} to {new_stage}"
            )

        # Update stage
        self.versions_table.update_item(
            Key={'version': version},
            UpdateExpression='SET stage = :stage, updatedAt = :updated',
            ExpressionAttributeValues={
                ':stage': new_stage,
                ':updated': datetime.utcnow().isoformat()
            }
        )

        # Trigger stage-specific actions
        self._handle_stage_transition(version, current_stage, new_stage)

    def _handle_stage_transition(self, version: str,
                                 from_stage: APILifecycleStage,
                                 to_stage: APILifecycleStage):
        """Handle stage transition actions"""
        if to_stage == APILifecycleStage.BETA:
            # Enable for beta users
            self._enable_for_beta_users(version)

        elif to_stage == APILifecycleStage.GA:
            # Full release
            self._publish_release_notes(version)
            self._notify_ga_release(version)

        elif to_stage == APILifecycleStage.DEPRECATED:
            # Start deprecation process
            deprecation_date = datetime.utcnow()
            sunset_date = deprecation_date + timedelta(days=180)  # 6 months

            self._schedule_deprecation_notices(version, sunset_date)

        elif to_stage == APILifecycleStage.SUNSET:
            # Remove version
            self._disable_version(version)

    def get_supported_versions(self) -> list[dict]:
        """Get list of supported API versions"""
        response = self.versions_table.scan(
            FilterExpression='stage IN (:alpha, :beta, :ga)',
            ExpressionAttributeValues={
                ':alpha': APILifecycleStage.ALPHA,
                ':beta': APILifecycleStage.BETA,
                ':ga': APILifecycleStage.GA
            }
        )

        return response['Items']
```

## Migration Patterns

### Gradual Migration

```python
class GradualMigration:
    """Implement gradual migration from v1 to v2"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.migration_table = self.dynamodb.Table('MigrationProgress')

    def enable_dark_launch(self, user_id: str, percentage: int = 10):
        """
        Dark launch: Call both v1 and v2, compare results,
        return v1 to user but log differences
        """
        def decorator(func):
            @wraps(func)
            def wrapper(event, context):
                import random

                # Call v1
                v1_result = call_v1_endpoint(event)

                # For X% of requests, also call v2
                if random.randint(1, 100) <= percentage:
                    try:
                        v2_result = call_v2_endpoint(event)

                        # Compare results
                        differences = self._compare_results(v1_result, v2_result)

                        if differences:
                            # Log differences for analysis
                            self._log_migration_difference(
                                user_id, v1_result, v2_result, differences
                            )

                    except Exception as e:
                        # Log v2 errors but don't affect users
                        self._log_migration_error(user_id, str(e))

                # Return v1 result (safe)
                return v1_result

            return wrapper
        return decorator

    def canary_release(self, user_id: str) -> bool:
        """
        Canary release: Route small percentage of users to v2
        """
        # Check if user is in canary group
        migration_status = self.get_migration_status(user_id)

        return migration_status.get('canaryEnabled', False)

    def set_user_migration_preference(self, user_id: str, use_v2: bool):
        """Allow users to opt-in to v2"""
        self.migration_table.put_item(Item={
            'userId': user_id,
            'useV2': use_v2,
            'updatedAt': datetime.utcnow().isoformat()
        })

    def get_migration_status(self, user_id: str) -> dict:
        """Get user's migration status"""
        response = self.migration_table.get_item(Key={'userId': user_id})
        return response.get('Item', {})

    def _compare_results(self, v1_result: dict, v2_result: dict) -> list[dict]:
        """Compare v1 and v2 results"""
        differences = []

        # Deep comparison logic
        # ...

        return differences

# Feature flag based migration
class FeatureFlagMigration:
    """Use feature flags to control migration"""

    def __init__(self):
        self.appconfig = boto3.client('appconfig')

    def get_feature_flag(self, user_id: str, flag_name: str) -> bool:
        """Get feature flag value for user"""
        # Use AWS AppConfig or LaunchDarkly
        response = self.appconfig.get_configuration(
            Application='api-migrations',
            Environment='production',
            Configuration=flag_name,
            ClientId=user_id
        )

        config = json.loads(response['Content'].read())
        return config.get('enabled', False)

    def route_based_on_flag(self, event, context):
        """Route to v1 or v2 based on feature flag"""
        user_id = event['user']['id']

        use_v2 = self.get_feature_flag(user_id, 'use-v2-api')

        if use_v2:
            return call_v2_endpoint(event)
        else:
            return call_v1_endpoint(event)
```

### Adapter Pattern for Migration

```python
class V1ToV2Adapter:
    """Adapt V1 requests/responses to V2 format"""

    @staticmethod
    def adapt_request(v1_request: dict) -> dict:
        """Transform V1 request to V2 format"""
        # V1 format: {"name": "...", "email": "..."}
        # V2 format: {"profile": {"name": "...", "email": "..."}}

        return {
            'profile': {
                'name': v1_request.get('name'),
                'email': v1_request.get('email')
            }
        }

    @staticmethod
    def adapt_response(v2_response: dict) -> dict:
        """Transform V2 response to V1 format"""
        # V2 format: {"data": {"type": "user", "attributes": {...}}}
        # V1 format: {"id": "...", "name": "...", "email": "..."}

        if 'data' in v2_response:
            data = v2_response['data']
            attrs = data.get('attributes', {})

            return {
                'id': data.get('id'),
                'name': attrs.get('name'),
                'email': attrs.get('email')
            }

        return v2_response

# Use adapter to maintain V1 API while migrating backend to V2
def v1_endpoint_using_v2_backend(event, context):
    """V1 API endpoint using V2 backend"""
    # Parse V1 request
    v1_request = json.loads(event['body'])

    # Adapt to V2
    v2_request = V1ToV2Adapter.adapt_request(v1_request)

    # Call V2 backend
    v2_response = call_v2_backend(v2_request)

    # Adapt back to V1
    v1_response = V1ToV2Adapter.adapt_response(v2_response)

    return {
        'statusCode': 200,
        'body': json.dumps(v1_response)
    }
```

## Real-World Examples

### Stripe: API Versioning Excellence

```python
class StripeVersioning:
    """
    Stripe's versioning approach:
    - Date-based versions (2024-01-15)
    - Per-account version pinning
    - Request-level version override
    - Backward compatibility maintained
    """

    def __init__(self):
        self.default_version = '2024-01-15'
        self.dynamodb = boto3.resource('dynamodb')
        self.accounts_table = self.dynamodb.Table('StripeAccounts')

    def get_account_version(self, account_id: str) -> str:
        """Get account's pinned API version"""
        response = self.accounts_table.get_item(Key={'accountId': account_id})

        if 'Item' in response:
            return response['Item'].get('apiVersion', self.default_version)

        return self.default_version

    def handle_request(self, event, context):
        """
        Stripe's version resolution order:
        1. Stripe-Version header (request-level override)
        2. Account's pinned version
        3. Latest stable version
        """
        # 1. Check header
        header_version = event['headers'].get('Stripe-Version')

        if header_version:
            api_version = header_version
        else:
            # 2. Check account version
            account_id = event['user']['accountId']
            api_version = self.get_account_version(account_id)

        # Route to appropriate handler
        return self.route_by_version(api_version, event)

    def route_by_version(self, version: str, event: dict):
        """Route request based on version"""
        handlers = {
            '2024-01-15': self.handle_2024_01_15,
            '2023-10-16': self.handle_2023_10_16,
            '2023-08-16': self.handle_2023_08_16
        }

        handler = handlers.get(version, self.handle_latest)
        return handler(event)

    def handle_2024_01_15(self, event: dict):
        """Handler for 2024-01-15 version"""
        # Latest version logic
        pass

    def upgrade_account_version(self, account_id: str, new_version: str):
        """Allow accounts to upgrade their API version"""
        # Validate version exists
        if not self.is_valid_version(new_version):
            raise ValueError(f"Invalid API version: {new_version}")

        # Update account version
        self.accounts_table.update_item(
            Key={'accountId': account_id},
            UpdateExpression='SET apiVersion = :version, updatedAt = :updated',
            ExpressionAttributeValues={
                ':version': new_version,
                ':updated': datetime.utcnow().isoformat()
            }
        )

        # Log upgrade
        self._log_version_upgrade(account_id, new_version)
```

### Twitter API: v1.1 to v2 Migration

```python
class TwitterAPIMigration:
    """
    Twitter's v1.1 to v2 migration:
    - Ran both versions in parallel for years
    - Provided migration tools and guides
    - Gradual feature parity in v2
    - Clear communication about v1.1 sunset
    """

    def __init__(self):
        self.migration_tracker = MigrationTracker()

    def parallel_endpoint_support(self, event, context):
        """Support both v1.1 and v2 endpoints"""
        path = event['path']

        if path.startswith('/1.1/'):
            return self.handle_v1_1(event)
        elif path.startswith('/2/'):
            return self.handle_v2(event)
        else:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Not found'})}

    def provide_migration_mapping(self, v1_endpoint: str) -> dict:
        """Provide V2 equivalent for V1 endpoints"""
        mappings = {
            '/1.1/statuses/user_timeline': {
                'v2_endpoint': '/2/users/:id/tweets',
                'migration_guide': 'https://developer.twitter.com/en/docs/twitter-api/migrate',
                'differences': [
                    'Different response format (data-centric)',
                    'New field names',
                    'Pagination uses tokens instead of cursors'
                ]
            },
            '/1.1/search/tweets': {
                'v2_endpoint': '/2/tweets/search/recent',
                'migration_guide': 'https://developer.twitter.com/en/docs/twitter-api/migrate',
                'differences': [
                    'Query syntax changes',
                    'New expansion parameters',
                    'Different rate limits'
                ]
            }
        }

        return mappings.get(v1_endpoint, {})
```

### GitHub API: Version 3 (REST) to Version 4 (GraphQL)

```python
class GitHubAPIMigration:
    """
    GitHub's REST to GraphQL migration:
    - Maintained both APIs indefinitely
    - GraphQL offers more flexibility
    - REST API continues to receive updates
    - Clients choose based on use case
    """

    def handle_request(self, event, context):
        """Route to REST or GraphQL endpoint"""
        accept_header = event['headers'].get('Accept', '')

        if 'application/vnd.github.v3+json' in accept_header:
            # REST API (v3)
            return self.handle_rest_v3(event)

        elif event['path'].startswith('/graphql'):
            # GraphQL API (v4)
            return self.handle_graphql_v4(event)

        else:
            # Default to latest REST
            return self.handle_rest_v3(event)

    def handle_rest_v3(self, event: dict):
        """REST API v3 handler"""
        # Traditional REST endpoints
        # GET /users/:username
        # GET /repos/:owner/:repo
        pass

    def handle_graphql_v4(self, event: dict):
        """GraphQL API v4 handler"""
        # GraphQL query execution
        # Single endpoint: POST /graphql
        # Client specifies exactly what data needed
        pass
```

## Documentation & Communication

### Changelog Management

```python
class ChangelogManager:
    """Maintain comprehensive API changelog"""

    def __init__(self):
        self.s3 = boto3.client('s3')
        self.changelog_bucket = 'api-documentation'

    def publish_changelog(self, version: str, changes: dict):
        """Publish changelog for version"""
        changelog_entry = {
            'version': version,
            'releaseDate': datetime.utcnow().isoformat(),
            'changes': {
                'breaking': changes.get('breaking', []),
                'deprecated': changes.get('deprecated', []),
                'added': changes.get('added', []),
                'changed': changes.get('changed', []),
                'fixed': changes.get('fixed', []),
                'security': changes.get('security', [])
            }
        }

        # Upload to S3
        self.s3.put_object(
            Bucket=self.changelog_bucket,
            Key=f'changelogs/{version}.json',
            Body=json.dumps(changelog_entry, indent=2),
            ContentType='application/json'
        )

        # Update consolidated changelog
        self._update_master_changelog(changelog_entry)

    def generate_migration_guide(self, from_version: str, to_version: str) -> str:
        """Generate migration guide between versions"""
        # Get all changes between versions
        changes = self._get_changes_between_versions(from_version, to_version)

        # Generate markdown guide
        guide = f"""
# Migration Guide: {from_version} → {to_version}

## Overview
This guide helps you migrate from API version {from_version} to {to_version}.

## Breaking Changes
"""

        for change in changes['breaking']:
            guide += f"\n### {change['title']}\n"
            guide += f"{change['description']}\n\n"
            guide += f"**Before:**\n```json\n{change['before']}\n```\n\n"
            guide += f"**After:**\n```json\n{change['after']}\n```\n\n"

        return guide
```

## Best Practices

### 1. Version Selection Hierarchy

```python
def determine_api_version(event: dict, account_id: str) -> str:
    """
    Version resolution priority:
    1. Request header (explicit override)
    2. Query parameter (for testing)
    3. Account default version
    4. Global default version
    """

    # 1. Header
    header_version = event['headers'].get('API-Version')
    if header_version:
        return validate_version(header_version)

    # 2. Query parameter
    query_version = event.get('queryStringParameters', {}).get('api_version')
    if query_version:
        return validate_version(query_version)

    # 3. Account default
    account_version = get_account_version(account_id)
    if account_version:
        return account_version

    # 4. Global default
    return get_default_version()
```

### 2. Comprehensive Testing

```python
class VersionCompatibilityTesting:
    """Test API compatibility across versions"""

    def test_backward_compatibility(self, old_version: str, new_version: str):
        """Ensure new version is backward compatible with old"""
        test_cases = self._load_test_cases(old_version)

        for test_case in test_cases:
            # Run test against old version
            old_result = self._call_api(old_version, test_case['request'])

            # Run same test against new version
            new_result = self._call_api(new_version, test_case['request'])

            # Verify compatibility
            self._assert_compatible(old_result, new_result)

    def test_contract_compliance(self, version: str):
        """Test API matches OpenAPI specification"""
        spec = self._load_openapi_spec(version)

        # Validate all endpoints match spec
        for path, methods in spec['paths'].items():
            for method, definition in methods.items():
                self._test_endpoint_contract(path, method, definition)
```

### 3. Monitoring & Analytics

```python
class VersionAnalytics:
    """Track API version usage"""

    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')

    def track_version_usage(self, version: str, endpoint: str, user_id: str):
        """Track which versions are being used"""
        self.cloudwatch.put_metric_data(
            Namespace='API/Versions',
            MetricData=[{
                'MetricName': 'APICall',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Version', 'Value': version},
                    {'Name': 'Endpoint', 'Value': endpoint}
                ]
            }]
        )

    def get_version_adoption_metrics(self) -> dict:
        """Get version adoption statistics"""
        response = self.cloudwatch.get_metric_statistics(
            Namespace='API/Versions',
            MetricName='APICall',
            Dimensions=[{'Name': 'Version', 'Value': '*'}],
            StartTime=datetime.utcnow() - timedelta(days=30),
            EndTime=datetime.utcnow(),
            Period=86400,
            Statistics=['Sum']
        )

        return self._format_adoption_metrics(response)

    def alert_on_deprecated_usage(self, version: str, threshold: int):
        """Alert when deprecated version usage exceeds threshold"""
        # Create CloudWatch alarm for deprecated version usage
        self.cloudwatch.put_metric_alarm(
            AlarmName=f'DeprecatedAPI-{version}-Usage',
            MetricName='APICall',
            Namespace='API/Versions',
            Statistic='Sum',
            Period=3600,
            EvaluationPeriods=1,
            Threshold=threshold,
            ComparisonOperator='GreaterThanThreshold',
            Dimensions=[{'Name': 'Version', 'Value': version}],
            AlarmActions=['arn:aws:sns:region:account:api-alerts']
        )
```

## Conclusion

Effective API versioning enables innovation while maintaining stability. Key principles:

1. **Plan for evolution**: Design APIs with versioning from day one
2. **Communicate clearly**: Document all changes, especially breaking ones
3. **Deprecate gracefully**: Give users ample time to migrate
4. **Maintain compatibility**: Keep old versions working during transition
5. **Monitor adoption**: Track version usage to inform sunset decisions
6. **Test thoroughly**: Ensure compatibility across versions
7. **Document everything**: Changelogs, migration guides, and examples

Remember: Your API is a contract with users. Version changes carefully and communicate transparently.
