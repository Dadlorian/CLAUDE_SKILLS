# Cloud Authentication & Authorization

## Table of Contents
- [Introduction](#introduction)
- [Authentication Patterns](#authentication-patterns)
- [Authorization Strategies](#authorization-strategies)
- [OAuth 2.0 & OIDC](#oauth-20--oidc)
- [SAML Integration](#saml-integration)
- [API Key Management](#api-key-management)
- [Mutual TLS (mTLS)](#mutual-tls-mtls)
- [IAM Integration](#iam-integration)
- [Real-World Examples](#real-world-examples)
- [Security Best Practices](#security-best-practices)
- [Performance Optimization](#performance-optimization)

## Introduction

Authentication verifies identity ("who you are"), while authorization determines permissions ("what you can do"). Cloud APIs require robust, scalable auth systems to protect resources and ensure compliance.

### Key Principles

- **Defense in Depth**: Multiple layers of security
- **Least Privilege**: Grant minimum necessary permissions
- **Zero Trust**: Never trust, always verify
- **Audit Everything**: Log all auth events
- **Fail Securely**: Default to deny on errors

## Authentication Patterns

### 1. JWT (JSON Web Tokens)

```python
import jwt
import datetime
from typing import Optional, Dict, Any
import os
from functools import wraps

class JWTAuthService:
    """JWT-based authentication service"""

    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry = 3600  # 1 hour

    def generate_token(self, user_id: str, email: str,
                      roles: list[str], metadata: Dict[str, Any] = None) -> str:
        """Generate JWT token"""
        now = datetime.datetime.utcnow()

        payload = {
            'sub': user_id,
            'email': email,
            'roles': roles,
            'iat': now,
            'exp': now + datetime.timedelta(seconds=self.token_expiry),
            'nbf': now,
            'iss': 'api.example.com',
            'aud': 'api.example.com'
        }

        if metadata:
            payload['metadata'] = metadata

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience='api.example.com',
                issuer='api.example.com'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f'Invalid token: {str(e)}')

    def refresh_token(self, token: str) -> str:
        """Refresh an existing token"""
        try:
            # Decode without verification for refresh
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': False}
            )

            # Generate new token
            return self.generate_token(
                user_id=payload['sub'],
                email=payload['email'],
                roles=payload['roles'],
                metadata=payload.get('metadata')
            )

        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f'Cannot refresh token: {str(e)}')

class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass

# Decorator for route protection
def require_auth(roles: list[str] = None):
    """Decorator to require authentication and optional roles"""

    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            auth_service = JWTAuthService(os.environ['JWT_SECRET'])

            # Extract token from header
            auth_header = event.get('headers', {}).get('Authorization', '')

            if not auth_header.startswith('Bearer '):
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Missing or invalid authorization header'})
                }

            token = auth_header[7:]  # Remove 'Bearer '

            try:
                # Verify token
                payload = auth_service.verify_token(token)

                # Check roles if specified
                if roles:
                    user_roles = payload.get('roles', [])
                    if not any(role in user_roles for role in roles):
                        return {
                            'statusCode': 403,
                            'body': json.dumps({'error': 'Insufficient permissions'})
                        }

                # Add user context to event
                event['user'] = payload

                # Call the actual function
                return func(event, context)

            except AuthenticationError as e:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': str(e)})
                }

        return wrapper
    return decorator

# Usage example
@require_auth(roles=['admin', 'moderator'])
def admin_handler(event, context):
    """Handler that requires admin or moderator role"""
    user = event['user']

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Hello {user['email']}",
            'roles': user['roles']
        })
    }
```

### 2. AWS Cognito Integration

```python
import boto3
from botocore.exceptions import ClientError

class CognitoAuthService:
    """AWS Cognito authentication service"""

    def __init__(self, user_pool_id: str, client_id: str, client_secret: str = None):
        self.cognito = boto3.client('cognito-idp')
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.client_secret = client_secret

    def sign_up(self, username: str, password: str, email: str,
                attributes: Dict[str, str] = None) -> str:
        """Register new user"""
        user_attributes = [
            {'Name': 'email', 'Value': email}
        ]

        if attributes:
            for key, value in attributes.items():
                user_attributes.append({'Name': key, 'Value': value})

        try:
            response = self.cognito.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=user_attributes
            )

            return response['UserSub']

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'UsernameExistsException':
                raise AuthenticationError('Username already exists')
            elif error_code == 'InvalidPasswordException':
                raise AuthenticationError('Password does not meet requirements')
            else:
                raise AuthenticationError(f'Sign up failed: {error_code}')

    def confirm_sign_up(self, username: str, confirmation_code: str):
        """Confirm user registration"""
        try:
            self.cognito.confirm_sign_up(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=confirmation_code
            )

        except ClientError as e:
            raise AuthenticationError(f'Confirmation failed: {e.response["Error"]["Code"]}')

    def sign_in(self, username: str, password: str) -> Dict[str, str]:
        """Sign in user and get tokens"""
        import hmac
        import hashlib
        import base64

        # Calculate secret hash if client secret is provided
        secret_hash = None
        if self.client_secret:
            message = username + self.client_id
            dig = hmac.new(
                self.client_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            secret_hash = base64.b64encode(dig).decode()

        try:
            auth_params = {
                'USERNAME': username,
                'PASSWORD': password
            }

            if secret_hash:
                auth_params['SECRET_HASH'] = secret_hash

            response = self.cognito.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters=auth_params
            )

            return {
                'accessToken': response['AuthenticationResult']['AccessToken'],
                'idToken': response['AuthenticationResult']['IdToken'],
                'refreshToken': response['AuthenticationResult']['RefreshToken'],
                'expiresIn': response['AuthenticationResult']['ExpiresIn']
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'NotAuthorizedException':
                raise AuthenticationError('Invalid username or password')
            elif error_code == 'UserNotConfirmedException':
                raise AuthenticationError('User not confirmed')
            else:
                raise AuthenticationError(f'Sign in failed: {error_code}')

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Cognito JWT token"""
        import requests
        from jose import jwt

        # Get Cognito public keys
        region = self.user_pool_id.split('_')[0]
        keys_url = f'https://cognito-idp.{region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json'

        response = requests.get(keys_url)
        keys = response.json()['keys']

        # Decode token header to get kid
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']

        # Find the right key
        key = next((k for k in keys if k['kid'] == kid), None)

        if not key:
            raise AuthenticationError('Public key not found')

        # Verify token
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id
            )

            return payload

        except jwt.JWTError as e:
            raise AuthenticationError(f'Token verification failed: {str(e)}')

    def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get user details from access token"""
        try:
            response = self.cognito.get_user(AccessToken=access_token)

            user_attributes = {}
            for attr in response['UserAttributes']:
                user_attributes[attr['Name']] = attr['Value']

            return {
                'username': response['Username'],
                'attributes': user_attributes
            }

        except ClientError as e:
            raise AuthenticationError(f'Get user failed: {e.response["Error"]["Code"]}')

    def add_user_to_group(self, username: str, group_name: str):
        """Add user to a group (for role-based access)"""
        try:
            self.cognito.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=group_name
            )

        except ClientError as e:
            raise AuthenticationError(f'Add to group failed: {e.response["Error"]["Code"]}')
```

### 3. Azure AD B2C Integration

```python
from msal import ConfidentialClientApplication
import requests

class AzureADB2CAuthService:
    """Azure AD B2C authentication service"""

    def __init__(self, tenant_name: str, policy_name: str,
                 client_id: str, client_secret: str):
        self.tenant_name = tenant_name
        self.policy_name = policy_name
        self.client_id = client_id
        self.client_secret = client_secret

        self.authority = f"https://{tenant_name}.b2clogin.com/{tenant_name}.onmicrosoft.com/{policy_name}"
        self.scope = [f"https://{tenant_name}.onmicrosoft.com/{client_id}/.default"]

        self.app = ConfidentialClientApplication(
            client_id,
            authority=self.authority,
            client_credential=client_secret
        )

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get authorization URL for OAuth flow"""
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scope,
            redirect_uri=redirect_uri,
            state=state
        )

        return auth_url

    def acquire_token_by_auth_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        result = self.app.acquire_token_by_authorization_code(
            code,
            scopes=self.scope,
            redirect_uri=redirect_uri
        )

        if 'error' in result:
            raise AuthenticationError(f"Token acquisition failed: {result['error_description']}")

        return {
            'accessToken': result['access_token'],
            'idToken': result.get('id_token'),
            'refreshToken': result.get('refresh_token'),
            'expiresIn': result['expires_in']
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Azure AD B2C token"""
        import jwt

        # Get signing keys
        jwks_uri = f"{self.authority}/discovery/v2.0/keys"
        response = requests.get(jwks_uri)
        keys = response.json()['keys']

        # Decode and verify
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next((k for k in keys if k['kid'] == unverified_header['kid']), None)

        if not rsa_key:
            raise AuthenticationError('Unable to find signing key')

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=['RS256'],
            audience=self.client_id,
            issuer=f"{self.authority}/v2.0/"
        )

        return payload
```

## Authorization Strategies

### 1. Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import Set, List
from dataclasses import dataclass

class Permission(str, Enum):
    """System permissions"""
    READ_USERS = "users:read"
    WRITE_USERS = "users:write"
    DELETE_USERS = "users:delete"
    READ_ORDERS = "orders:read"
    WRITE_ORDERS = "orders:write"
    DELETE_ORDERS = "orders:delete"
    MANAGE_SYSTEM = "system:manage"

class Role(str, Enum):
    """System roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

@dataclass
class RolePermissions:
    """Mapping of roles to permissions"""
    role: Role
    permissions: Set[Permission]

class RBACService:
    """Role-Based Access Control service"""

    def __init__(self):
        # Define role permissions
        self.role_permissions = {
            Role.ADMIN: {
                Permission.READ_USERS,
                Permission.WRITE_USERS,
                Permission.DELETE_USERS,
                Permission.READ_ORDERS,
                Permission.WRITE_ORDERS,
                Permission.DELETE_ORDERS,
                Permission.MANAGE_SYSTEM
            },
            Role.MANAGER: {
                Permission.READ_USERS,
                Permission.WRITE_USERS,
                Permission.READ_ORDERS,
                Permission.WRITE_ORDERS
            },
            Role.USER: {
                Permission.READ_USERS,
                Permission.READ_ORDERS,
                Permission.WRITE_ORDERS
            },
            Role.GUEST: {
                Permission.READ_USERS,
                Permission.READ_ORDERS
            }
        }

    def get_user_permissions(self, roles: List[Role]) -> Set[Permission]:
        """Get all permissions for user's roles"""
        permissions = set()

        for role in roles:
            role_perms = self.role_permissions.get(role, set())
            permissions.update(role_perms)

        return permissions

    def check_permission(self, user_roles: List[Role], required_permission: Permission) -> bool:
        """Check if user has required permission"""
        user_permissions = self.get_user_permissions(user_roles)
        return required_permission in user_permissions

    def require_permission(self, permission: Permission):
        """Decorator to require specific permission"""

        def decorator(func):
            @wraps(func)
            def wrapper(event, context):
                user = event.get('user')

                if not user:
                    return {
                        'statusCode': 401,
                        'body': json.dumps({'error': 'Unauthorized'})
                    }

                user_roles = [Role(r) for r in user.get('roles', [])]

                if not self.check_permission(user_roles, permission):
                    return {
                        'statusCode': 403,
                        'body': json.dumps({
                            'error': 'Forbidden',
                            'message': f'Missing required permission: {permission}'
                        })
                    }

                return func(event, context)

            return wrapper
        return decorator

# Usage
rbac = RBACService()

@require_auth()
@rbac.require_permission(Permission.DELETE_USERS)
def delete_user_handler(event, context):
    """Handler requiring DELETE_USERS permission"""
    user_id = event['pathParameters']['id']

    # Delete user
    # ...

    return {'statusCode': 204}
```

### 2. Attribute-Based Access Control (ABAC)

```python
from typing import Any, Dict, Callable

class ABACPolicy:
    """Attribute-Based Access Control policy"""

    def __init__(self):
        self.policies = {}

    def define_policy(self, name: str, condition: Callable[[Dict[str, Any]], bool]):
        """Define ABAC policy with condition function"""
        self.policies[name] = condition

    def evaluate(self, policy_name: str, context: Dict[str, Any]) -> bool:
        """Evaluate policy against context"""
        policy = self.policies.get(policy_name)

        if not policy:
            return False

        return policy(context)

# Define ABAC policies
abac = ABACPolicy()

# Policy: User can only access their own resources
abac.define_policy(
    'own_resource_access',
    lambda ctx: ctx['user']['id'] == ctx['resource']['ownerId']
)

# Policy: Manager can access resources in their department
abac.define_policy(
    'department_access',
    lambda ctx: (
        'manager' in ctx['user']['roles'] and
        ctx['user']['department'] == ctx['resource']['department']
    )
)

# Policy: Access during business hours only
abac.define_policy(
    'business_hours_only',
    lambda ctx: (
        9 <= datetime.now().hour < 17 and
        datetime.now().weekday() < 5  # Monday-Friday
    )
)

# Policy: Geo-based access restriction
abac.define_policy(
    'allowed_regions',
    lambda ctx: ctx['request']['region'] in ctx['user']['allowedRegions']
)

# Complex policy combining multiple conditions
abac.define_policy(
    'sensitive_data_access',
    lambda ctx: (
        'admin' in ctx['user']['roles'] and
        ctx['user']['mfaEnabled'] and
        ctx['request']['protocol'] == 'https' and
        ctx['user']['lastPasswordChange'] > datetime.now() - timedelta(days=90)
    )
)

def enforce_abac_policy(policy_name: str):
    """Decorator to enforce ABAC policy"""

    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            user = event.get('user')

            if not user:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Unauthorized'})
                }

            # Get resource being accessed
            resource_id = event['pathParameters'].get('id')
            resource = get_resource(resource_id)  # Implement this

            # Build context for policy evaluation
            policy_context = {
                'user': user,
                'resource': resource,
                'request': {
                    'method': event['httpMethod'],
                    'path': event['path'],
                    'ip': event['requestContext']['identity']['sourceIp'],
                    'region': os.environ['AWS_REGION'],
                    'protocol': event['headers'].get('X-Forwarded-Proto', 'https')
                }
            }

            # Evaluate policy
            if not abac.evaluate(policy_name, policy_context):
                return {
                    'statusCode': 403,
                    'body': json.dumps({
                        'error': 'Access denied',
                        'message': f'Policy {policy_name} evaluation failed'
                    })
                }

            return func(event, context)

        return wrapper
    return decorator

# Usage
@require_auth()
@enforce_abac_policy('own_resource_access')
def get_user_profile(event, context):
    """User can only access their own profile"""
    user_id = event['pathParameters']['id']

    # Get and return profile
    # ...
```

## OAuth 2.0 & OIDC

### OAuth 2.0 Authorization Server

```python
import secrets
from typing import Optional
from datetime import datetime, timedelta

class OAuth2Server:
    """OAuth 2.0 authorization server implementation"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.clients_table = self.dynamodb.Table('OAuthClients')
        self.codes_table = self.dynamodb.Table('AuthorizationCodes')
        self.tokens_table = self.dynamodb.Table('AccessTokens')

    def register_client(self, client_name: str, redirect_uris: List[str],
                       grant_types: List[str]) -> Dict[str, str]:
        """Register OAuth 2.0 client"""
        client_id = secrets.token_urlsafe(32)
        client_secret = secrets.token_urlsafe(64)

        self.clients_table.put_item(Item={
            'clientId': client_id,
            'clientSecret': client_secret,
            'clientName': client_name,
            'redirectUris': redirect_uris,
            'grantTypes': grant_types,
            'createdAt': datetime.utcnow().isoformat()
        })

        return {
            'clientId': client_id,
            'clientSecret': client_secret
        }

    def authorize(self, client_id: str, redirect_uri: str, scope: str,
                 state: str, user_id: str) -> str:
        """Authorization endpoint - generate authorization code"""
        # Validate client
        client = self.clients_table.get_item(Key={'clientId': client_id})

        if 'Item' not in client:
            raise OAuth2Error('invalid_client', 'Client not found')

        if redirect_uri not in client['Item']['redirectUris']:
            raise OAuth2Error('invalid_request', 'Invalid redirect URI')

        # Generate authorization code
        code = secrets.token_urlsafe(32)

        # Store code
        self.codes_table.put_item(Item={
            'code': code,
            'clientId': client_id,
            'userId': user_id,
            'scope': scope,
            'redirectUri': redirect_uri,
            'expiresAt': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            'used': False
        })

        # Return authorization code to client
        return f"{redirect_uri}?code={code}&state={state}"

    def exchange_code_for_token(self, code: str, client_id: str,
                                client_secret: str, redirect_uri: str) -> Dict[str, Any]:
        """Token endpoint - exchange authorization code for access token"""
        # Verify client credentials
        client = self.clients_table.get_item(Key={'clientId': client_id})

        if 'Item' not in client or client['Item']['clientSecret'] != client_secret:
            raise OAuth2Error('invalid_client', 'Invalid client credentials')

        # Get authorization code
        code_item = self.codes_table.get_item(Key={'code': code})

        if 'Item' not in code_item:
            raise OAuth2Error('invalid_grant', 'Invalid authorization code')

        code_data = code_item['Item']

        # Validate code
        if code_data['used']:
            raise OAuth2Error('invalid_grant', 'Code already used')

        if code_data['clientId'] != client_id:
            raise OAuth2Error('invalid_grant', 'Code issued to different client')

        if code_data['redirectUri'] != redirect_uri:
            raise OAuth2Error('invalid_grant', 'Redirect URI mismatch')

        if datetime.fromisoformat(code_data['expiresAt']) < datetime.utcnow():
            raise OAuth2Error('invalid_grant', 'Code expired')

        # Mark code as used
        self.codes_table.update_item(
            Key={'code': code},
            UpdateExpression='SET used = :used',
            ExpressionAttributeValues={':used': True}
        )

        # Generate access token
        access_token = secrets.token_urlsafe(64)
        refresh_token = secrets.token_urlsafe(64)

        # Store tokens
        self.tokens_table.put_item(Item={
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'clientId': client_id,
            'userId': code_data['userId'],
            'scope': code_data['scope'],
            'expiresAt': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'createdAt': datetime.utcnow().isoformat()
        })

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'scope': code_data['scope']
        }

    def verify_access_token(self, access_token: str) -> Dict[str, Any]:
        """Verify access token and return token info"""
        token = self.tokens_table.get_item(Key={'accessToken': access_token})

        if 'Item' not in token:
            raise OAuth2Error('invalid_token', 'Token not found')

        token_data = token['Item']

        if datetime.fromisoformat(token_data['expiresAt']) < datetime.utcnow():
            raise OAuth2Error('invalid_token', 'Token expired')

        return {
            'userId': token_data['userId'],
            'clientId': token_data['clientId'],
            'scope': token_data['scope']
        }

    def refresh_access_token(self, refresh_token: str, client_id: str,
                            client_secret: str) -> Dict[str, Any]:
        """Refresh access token"""
        # Verify client
        client = self.clients_table.get_item(Key={'clientId': client_id})

        if 'Item' not in client or client['Item']['clientSecret'] != client_secret:
            raise OAuth2Error('invalid_client', 'Invalid client credentials')

        # Find token by refresh token
        response = self.tokens_table.scan(
            FilterExpression='refreshToken = :rt',
            ExpressionAttributeValues={':rt': refresh_token}
        )

        if not response['Items']:
            raise OAuth2Error('invalid_grant', 'Invalid refresh token')

        old_token = response['Items'][0]

        # Generate new access token
        new_access_token = secrets.token_urlsafe(64)

        # Update token
        self.tokens_table.update_item(
            Key={'accessToken': old_token['accessToken']},
            UpdateExpression='SET accessToken = :new_token, expiresAt = :expires',
            ExpressionAttributeValues={
                ':new_token': new_access_token,
                ':expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        )

        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token
        }

class OAuth2Error(Exception):
    """OAuth 2.0 error"""

    def __init__(self, error: str, description: str):
        self.error = error
        self.description = description
        super().__init__(f"{error}: {description}")
```

### OpenID Connect (OIDC) Provider

```python
class OIDCProvider(OAuth2Server):
    """OpenID Connect provider built on OAuth 2.0"""

    def __init__(self):
        super().__init__()
        self.users_table = self.dynamodb.Table('Users')

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return user ID"""
        import hashlib

        user = self.users_table.get_item(Key={'username': username})

        if 'Item' not in user:
            return None

        user_data = user['Item']

        # Verify password (in production, use bcrypt/argon2)
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if user_data['passwordHash'] != password_hash:
            return None

        return user_data['userId']

    def generate_id_token(self, user_id: str, client_id: str, nonce: str = None) -> str:
        """Generate OIDC ID token (JWT)"""
        # Get user details
        user = self.users_table.get_item(Key={'userId': user_id})
        user_data = user['Item']

        # Create ID token payload
        now = datetime.utcnow()
        payload = {
            'iss': 'https://auth.example.com',
            'sub': user_id,
            'aud': client_id,
            'exp': now + timedelta(hours=1),
            'iat': now,
            'auth_time': int(now.timestamp()),
            'email': user_data['email'],
            'email_verified': user_data.get('emailVerified', False),
            'name': user_data.get('name'),
            'picture': user_data.get('picture')
        }

        if nonce:
            payload['nonce'] = nonce

        # Sign with JWT
        jwt_service = JWTAuthService(os.environ['JWT_SECRET'])
        return jwt.encode(payload, os.environ['JWT_SECRET'], algorithm='HS256')

    def get_userinfo(self, access_token: str) -> Dict[str, Any]:
        """UserInfo endpoint - return user claims"""
        token_info = self.verify_access_token(access_token)
        user_id = token_info['userId']

        # Get user details
        user = self.users_table.get_item(Key={'userId': user_id})
        user_data = user['Item']

        return {
            'sub': user_id,
            'email': user_data['email'],
            'email_verified': user_data.get('emailVerified', False),
            'name': user_data.get('name'),
            'picture': user_data.get('picture'),
            'updated_at': user_data.get('updatedAt')
        }

    def get_discovery_document(self) -> Dict[str, Any]:
        """OIDC discovery document (.well-known/openid-configuration)"""
        base_url = 'https://auth.example.com'

        return {
            'issuer': base_url,
            'authorization_endpoint': f'{base_url}/authorize',
            'token_endpoint': f'{base_url}/token',
            'userinfo_endpoint': f'{base_url}/userinfo',
            'jwks_uri': f'{base_url}/.well-known/jwks.json',
            'response_types_supported': ['code', 'id_token', 'token id_token'],
            'subject_types_supported': ['public'],
            'id_token_signing_alg_values_supported': ['HS256', 'RS256'],
            'scopes_supported': ['openid', 'email', 'profile'],
            'token_endpoint_auth_methods_supported': ['client_secret_basic', 'client_secret_post'],
            'claims_supported': ['sub', 'email', 'email_verified', 'name', 'picture']
        }
```

## SAML Integration

```python
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

class SAMLService:
    """SAML 2.0 Service Provider"""

    def __init__(self, settings: Dict[str, Any]):
        """
        Initialize SAML SP with settings

        settings = {
            'sp': {
                'entityId': 'https://app.example.com/metadata',
                'assertionConsumerService': {
                    'url': 'https://app.example.com/saml/acs',
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
                },
                'singleLogoutService': {
                    'url': 'https://app.example.com/saml/sls',
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'x509cert': 'SP_CERT',
                'privateKey': 'SP_PRIVATE_KEY'
            },
            'idp': {
                'entityId': 'https://idp.example.com/metadata',
                'singleSignOnService': {
                    'url': 'https://idp.example.com/sso',
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'singleLogoutService': {
                    'url': 'https://idp.example.com/slo',
                    'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                },
                'x509cert': 'IDP_CERT'
            }
        }
        """
        self.settings = settings

    def initiate_sso(self, request_data: Dict[str, Any]) -> str:
        """Initiate SAML SSO flow"""
        auth = OneLogin_Saml2_Auth(request_data, self.settings)
        return auth.login()

    def process_response(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process SAML response from IdP"""
        auth = OneLogin_Saml2_Auth(request_data, self.settings)
        auth.process_response()

        errors = auth.get_errors()

        if errors:
            raise SAMLError(f"SAML authentication failed: {', '.join(errors)}")

        if not auth.is_authenticated():
            raise SAMLError("User not authenticated")

        # Get user attributes
        attributes = auth.get_attributes()
        nameid = auth.get_nameid()

        return {
            'nameId': nameid,
            'sessionIndex': auth.get_session_index(),
            'attributes': attributes,
            'email': attributes.get('email', [None])[0],
            'displayName': attributes.get('displayName', [None])[0],
            'groups': attributes.get('groups', [])
        }

    def initiate_slo(self, request_data: Dict[str, Any], name_id: str,
                    session_index: str) -> str:
        """Initiate SAML Single Logout"""
        auth = OneLogin_Saml2_Auth(request_data, self.settings)
        return auth.logout(name_id=name_id, session_index=session_index)

    def get_metadata(self) -> str:
        """Get SP metadata XML"""
        auth = OneLogin_Saml2_Auth({}, self.settings)
        settings = auth.get_settings()
        metadata = settings.get_sp_metadata()

        errors = settings.validate_metadata(metadata)

        if errors:
            raise SAMLError(f"Invalid metadata: {', '.join(errors)}")

        return metadata

class SAMLError(Exception):
    """SAML authentication error"""
    pass

# Lambda handler for SAML SSO
def saml_sso_handler(event, context):
    """Initiate SAML SSO"""
    saml_service = SAMLService(get_saml_settings())

    request_data = {
        'https': 'on',
        'http_host': event['headers']['Host'],
        'script_name': event['path'],
        'get_data': event.get('queryStringParameters', {}),
        'post_data': {}
    }

    sso_url = saml_service.initiate_sso(request_data)

    return {
        'statusCode': 302,
        'headers': {'Location': sso_url}
    }

# Lambda handler for SAML ACS
def saml_acs_handler(event, context):
    """Handle SAML assertion"""
    import base64

    saml_service = SAMLService(get_saml_settings())

    # Parse POST data
    body = base64.b64decode(event['body']).decode()
    post_data = {}
    for pair in body.split('&'):
        key, value = pair.split('=')
        post_data[key] = value

    request_data = {
        'https': 'on',
        'http_host': event['headers']['Host'],
        'script_name': event['path'],
        'get_data': {},
        'post_data': post_data
    }

    try:
        user_data = saml_service.process_response(request_data)

        # Create session
        jwt_service = JWTAuthService(os.environ['JWT_SECRET'])
        token = jwt_service.generate_token(
            user_id=user_data['nameId'],
            email=user_data['email'],
            roles=user_data['groups']
        )

        return {
            'statusCode': 302,
            'headers': {
                'Location': '/dashboard',
                'Set-Cookie': f'session={token}; HttpOnly; Secure; SameSite=Strict'
            }
        }

    except SAMLError as e:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': str(e)})
        }
```

## API Key Management

```python
import secrets
import hashlib
from typing import Optional

class APIKeyService:
    """API key management service"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.keys_table = self.dynamodb.Table('APIKeys')

    def create_api_key(self, user_id: str, name: str,
                       scopes: List[str], rate_limit: int = 1000) -> Dict[str, str]:
        """Create new API key"""
        # Generate API key
        api_key = f"sk_{secrets.token_urlsafe(32)}"

        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Store hashed key
        self.keys_table.put_item(Item={
            'keyHash': key_hash,
            'userId': user_id,
            'name': name,
            'scopes': scopes,
            'rateLimit': rate_limit,
            'createdAt': datetime.utcnow().isoformat(),
            'lastUsed': None,
            'enabled': True
        })

        # Return the actual key only once
        return {
            'apiKey': api_key,
            'keyHash': key_hash,
            'name': name
        }

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify API key and return key info"""
        # Hash provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Look up key
        response = self.keys_table.get_item(Key={'keyHash': key_hash})

        if 'Item' not in response:
            return None

        key_data = response['Item']

        if not key_data['enabled']:
            return None

        # Update last used timestamp
        self.keys_table.update_item(
            Key={'keyHash': key_hash},
            UpdateExpression='SET lastUsed = :now',
            ExpressionAttributeValues={':now': datetime.utcnow().isoformat()}
        )

        return key_data

    def revoke_api_key(self, key_hash: str):
        """Revoke API key"""
        self.keys_table.update_item(
            Key={'keyHash': key_hash},
            UpdateExpression='SET enabled = :enabled',
            ExpressionAttributeValues={':enabled': False}
        )

    def list_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """List all API keys for user"""
        response = self.keys_table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )

        return response['Items']

# API key authentication middleware
def require_api_key(scopes: List[str] = None):
    """Decorator to require API key authentication"""

    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            api_key_service = APIKeyService()

            # Extract API key from header
            api_key = event.get('headers', {}).get('X-API-Key')

            if not api_key:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Missing API key'})
                }

            # Verify key
            key_data = api_key_service.verify_api_key(api_key)

            if not key_data:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Invalid API key'})
                }

            # Check scopes if specified
            if scopes:
                key_scopes = key_data.get('scopes', [])
                if not any(scope in key_scopes for scope in scopes):
                    return {
                        'statusCode': 403,
                        'body': json.dumps({
                            'error': 'Insufficient scopes',
                            'required': scopes,
                            'available': key_scopes
                        })
                    }

            # Check rate limit
            if not check_rate_limit(key_data['keyHash'], key_data['rateLimit']):
                return {
                    'statusCode': 429,
                    'body': json.dumps({'error': 'Rate limit exceeded'})
                }

            # Add key data to event
            event['apiKey'] = key_data

            return func(event, context)

        return wrapper
    return decorator

# Usage
@require_api_key(scopes=['users:read'])
def list_users_handler(event, context):
    """Handler requiring API key with users:read scope"""
    key_data = event['apiKey']

    # List users
    # ...

    return {
        'statusCode': 200,
        'body': json.dumps({'users': []})
    }
```

## Mutual TLS (mTLS)

```python
class MTLSService:
    """Mutual TLS authentication service"""

    def __init__(self):
        self.acm = boto3.client('acm')
        self.api_gateway = boto3.client('apigatewayv2')

    def configure_mtls_domain(self, domain_name: str, certificate_arn: str,
                             truststore_uri: str) -> str:
        """Configure mTLS for API Gateway custom domain"""
        response = self.api_gateway.create_domain_name(
            DomainName=domain_name,
            DomainNameConfigurations=[{
                'EndpointType': 'REGIONAL',
                'CertificateArn': certificate_arn
            }],
            MutualTlsAuthentication={
                'TruststoreUri': truststore_uri,  # S3 URI to truststore
                'TruststoreVersion': '1.0'
            }
        )

        return response['DomainName']

    def verify_client_certificate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and verify client certificate from request"""
        request_context = event.get('requestContext', {})
        identity = request_context.get('identity', {})

        # Client certificate info from API Gateway
        client_cert = identity.get('clientCert', {})

        if not client_cert:
            raise AuthenticationError('No client certificate provided')

        # Extract certificate details
        cert_info = {
            'subjectDN': client_cert.get('subjectDN'),
            'issuerDN': client_cert.get('issuerDN'),
            'serialNumber': client_cert.get('serialNumber'),
            'validity': {
                'notBefore': client_cert.get('validity', {}).get('notBefore'),
                'notAfter': client_cert.get('validity', {}).get('notAfter')
            }
        }

        # Additional validation logic here
        # - Check certificate revocation
        # - Validate certificate attributes
        # - Map certificate to user/service

        return cert_info

# Lambda authorizer for mTLS
def mtls_authorizer(event, context):
    """Custom authorizer that validates client certificates"""
    mtls_service = MTLSService()

    try:
        cert_info = mtls_service.verify_client_certificate(event)

        # Map certificate to user/service
        user_id = extract_user_from_cert(cert_info)

        # Generate allow policy
        return generate_policy(user_id, 'Allow', event['methodArn'])

    except AuthenticationError as e:
        # Generate deny policy
        return generate_policy('unknown', 'Deny', event['methodArn'])
```

## Real-World Examples

### Stripe: API Key Authentication

```python
class StripeStyleAPIKey:
    """Stripe-style API key management"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.keys_table = self.dynamodb.Table('StripeAPIKeys')

    def create_api_key(self, account_id: str, key_type: str = 'secret') -> str:
        """
        Create Stripe-style API key

        Key types:
        - secret: sk_live_... or sk_test_...
        - publishable: pk_live_... or pk_test_...
        - restricted: rk_live_... or rk_test_...
        """
        env = os.environ.get('ENVIRONMENT', 'test')
        prefix = {
            'secret': 'sk',
            'publishable': 'pk',
            'restricted': 'rk'
        }[key_type]

        # Generate key
        api_key = f"{prefix}_{env}_{secrets.token_urlsafe(24)}"

        # Hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Store
        self.keys_table.put_item(Item={
            'keyHash': key_hash,
            'accountId': account_id,
            'keyType': key_type,
            'environment': env,
            'createdAt': datetime.utcnow().isoformat(),
            'permissions': self._get_default_permissions(key_type)
        })

        return api_key

    def _get_default_permissions(self, key_type: str) -> Dict[str, str]:
        """Get default permissions for key type"""
        if key_type == 'publishable':
            return {
                'charges': 'read',
                'customers': 'write',
                'tokens': 'write'
            }
        elif key_type == 'secret':
            return {
                'all': 'write'
            }
        else:  # restricted
            return {}
```

### Netflix: Zero Trust API Access

```python
class NetflixStyleZeroTrust:
    """Netflix-inspired zero trust authentication"""

    def __init__(self):
        self.device_trust_score_threshold = 0.7

    def authenticate_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-factor zero trust authentication:
        1. User identity (JWT)
        2. Device trustworthiness
        3. Network context
        4. Behavioral analysis
        """
        # 1. Verify user identity
        user = self.verify_user_token(event)

        # 2. Assess device trust
        device_score = self.assess_device_trust(event)

        if device_score < self.device_trust_score_threshold:
            raise AuthenticationError('Device trust score too low')

        # 3. Validate network context
        network_valid = self.validate_network_context(event)

        if not network_valid:
            raise AuthenticationError('Invalid network context')

        # 4. Behavioral analysis
        behavior_anomaly = self.detect_behavior_anomaly(user['userId'], event)

        if behavior_anomaly:
            # Require step-up authentication
            return {
                'authenticated': False,
                'stepUpRequired': True,
                'challengeType': 'mfa'
            }

        return {
            'authenticated': True,
            'user': user,
            'trustScore': device_score
        }

    def assess_device_trust(self, event: Dict[str, Any]) -> float:
        """Calculate device trust score"""
        score = 1.0

        # Check device fingerprint
        device_id = event.get('headers', {}).get('X-Device-ID')

        if not device_id or not self.is_known_device(device_id):
            score -= 0.3

        # Check for root/jailbreak
        if event.get('headers', {}).get('X-Device-Rooted') == 'true':
            score -= 0.5

        # Check OS version
        os_version = event.get('headers', {}).get('X-OS-Version')

        if not self.is_supported_os_version(os_version):
            score -= 0.2

        return max(score, 0.0)

    def validate_network_context(self, event: Dict[str, Any]) -> bool:
        """Validate network context"""
        ip = event['requestContext']['identity']['sourceIp']

        # Check if IP is in blacklist
        if self.is_blacklisted_ip(ip):
            return False

        # Check for VPN/proxy
        if self.is_vpn_or_proxy(ip):
            # May require additional verification
            pass

        # Check geolocation consistency
        expected_country = self.get_user_country(event['user']['userId'])
        actual_country = self.get_ip_country(ip)

        if expected_country != actual_country:
            # Unusual location - require additional verification
            return False

        return True
```

## Security Best Practices

### 1. Token Rotation

```python
class TokenRotationService:
    """Implement token rotation for enhanced security"""

    def __init__(self):
        self.access_token_lifetime = 900  # 15 minutes
        self.refresh_token_lifetime = 604800  # 7 days

    def issue_token_pair(self, user_id: str) -> Dict[str, str]:
        """Issue access and refresh token pair"""
        jwt_service = JWTAuthService(os.environ['JWT_SECRET'])

        access_token = jwt_service.generate_token(
            user_id=user_id,
            email=self.get_user_email(user_id),
            roles=self.get_user_roles(user_id)
        )

        refresh_token = secrets.token_urlsafe(64)

        # Store refresh token
        self.store_refresh_token(user_id, refresh_token)

        return {
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'expiresIn': self.access_token_lifetime
        }

    def rotate_tokens(self, refresh_token: str) -> Dict[str, str]:
        """Rotate tokens using refresh token"""
        user_id = self.validate_refresh_token(refresh_token)

        if not user_id:
            raise AuthenticationError('Invalid refresh token')

        # Revoke old refresh token
        self.revoke_refresh_token(refresh_token)

        # Issue new token pair
        return self.issue_token_pair(user_id)
```

### 2. Rate Limiting

```python
from datetime import datetime, timedelta

class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate: int, per: int):
        """
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('RateLimits')

    def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.per)

        try:
            # Update counter atomically
            response = self.table.update_item(
                Key={'key': key},
                UpdateExpression='ADD requestCount :inc SET lastRequest = :now, windowStart = if_not_exists(windowStart, :window)',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':now': now.isoformat(),
                    ':window': window_start.isoformat()
                },
                ReturnValues='ALL_NEW'
            )

            attrs = response['Attributes']

            # Reset if outside window
            if datetime.fromisoformat(attrs['windowStart']) < window_start:
                self.table.update_item(
                    Key={'key': key},
                    UpdateExpression='SET requestCount = :one, windowStart = :window',
                    ExpressionAttributeValues={
                        ':one': 1,
                        ':window': now.isoformat()
                    }
                )
                return True

            # Check if within limit
            return attrs['requestCount'] <= self.rate

        except:
            # Allow on error (fail open)
            return True
```

## Conclusion

Robust authentication and authorization are critical for cloud API security. Key takeaways:

1. **Use standard protocols**: OAuth 2.0, OIDC, SAML for interoperability
2. **Implement defense in depth**: Multiple layers of security
3. **Follow least privilege**: Grant minimum necessary permissions
4. **Rotate credentials**: Regular token and key rotation
5. **Monitor and audit**: Log all authentication events
6. **Rate limit**: Protect against brute force and DoS
7. **Use HTTPS/TLS**: Encrypt all communications
8. **Implement MFA**: Multi-factor authentication for sensitive operations

Security is not a feature—it's a fundamental requirement for cloud APIs.
