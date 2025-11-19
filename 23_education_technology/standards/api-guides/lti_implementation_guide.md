# LTI 1.3 / LTI Advantage Implementation Guide

## Overview

Learning Tools Interoperability (LTI) is the IMS Global standard for integrating external tools into Learning Management Systems (LMS). LTI 1.3 (also called LTI Advantage) uses OAuth 2.0 and OpenID Connect (OIDC) for secure authentication and authorization.

## Key Concepts

### LTI Roles

**Platform**: The LMS (Canvas, Moodle, Blackboard) hosting the learning experience
**Tool**: The external application being integrated (quiz tool, video platform, simulation)
**User**: The learner, instructor, or administrator launching the tool from the platform

### LTI Advantage Services

1. **Core**: Basic launch with user/context information
2. **Deep Linking (LTI-DL)**: Content selection and embedding
3. **Assignment and Grade Services (AGS)**: Gradebook integration
4. **Names and Role Provisioning Service (NRPS)**: Roster access

## Implementation Steps

### 1. Registration & Configuration

**Platform Configuration** (what the platform needs about your tool):
```json
{
  "title": "Interactive Physics Simulator",
  "description": "3D physics simulations for STEM courses",
  "target_link_uri": "https://physics-sim.example.com/lti/launch",
  "oidc_initiation_url": "https://physics-sim.example.com/lti/oidc/login",
  "public_jwk_url": "https://physics-sim.example.com/.well-known/jwks.json",
  "redirect_uris": [
    "https://physics-sim.example.com/lti/callback"
  ],
  "scopes": [
    "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
    "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
    "https://purl.imsglobal.org/spec/lti-ags/scope/score",
    "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
  ],
  "custom_parameters": {
    "course_id": "$CourseOffering.sourcedId",
    "user_role": "$Canvas.membership.roles"
  }
}
```

**Tool Configuration** (what your tool needs about the platform):
```json
{
  "platform": {
    "issuer": "https://canvas.instructure.com",
    "client_id": "10000000000001",
    "auth_login_url": "https://canvas.instructure.com/api/lti/authorize_redirect",
    "auth_token_url": "https://canvas.instructure.com/login/oauth2/token",
    "key_set_url": "https://canvas.instructure.com/api/lti/security/jwks",
    "deployment_ids": ["1:abcd1234"]
  }
}
```

### 2. LTI Launch Flow (OIDC-based)

**Step 1: OIDC Login Initiation** (Platform → Tool)
```http
GET /lti/oidc/login?
  iss=https://canvas.instructure.com&
  login_hint=user-12345&
  target_link_uri=https://physics-sim.example.com/lti/launch&
  lti_message_hint=eyJ0eXAiOiJKV1QiLCJhbGc...&
  client_id=10000000000001
```

**Step 2: Authentication Request** (Tool → Platform)
```http
GET https://canvas.instructure.com/api/lti/authorize_redirect?
  response_type=id_token&
  scope=openid&
  client_id=10000000000001&
  redirect_uri=https://physics-sim.example.com/lti/callback&
  login_hint=user-12345&
  nonce=abc123def456&
  state=xyz789&
  response_mode=form_post&
  prompt=none
```

**Step 3: Authentication Response** (Platform → Tool)
```http
POST /lti/callback
Content-Type: application/x-www-form-urlencoded

id_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImNhbnZhcy1rZXkifQ...&
state=xyz789
```

**Step 4: Validate ID Token & Extract Claims**

The `id_token` is a signed JWT containing:
```json
{
  "iss": "https://canvas.instructure.com",
  "aud": "10000000000001",
  "sub": "user-12345",
  "exp": 1700000000,
  "iat": 1699999000,
  "nonce": "abc123def456",

  "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
  "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
  "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "1:abcd1234",

  "https://purl.imsglobal.org/spec/lti/claim/target_link_uri": "https://physics-sim.example.com/lti/launch",

  "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
    "id": "resource-link-12345",
    "title": "Newton's Laws Simulation"
  },

  "https://purl.imsglobal.org/spec/lti/claim/roles": [
    "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"
  ],

  "https://purl.imsglobal.org/spec/lti/claim/context": {
    "id": "course-101",
    "label": "PHYS 101",
    "title": "Introduction to Physics",
    "type": ["http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering"]
  },

  "name": "Dr. Jane Smith",
  "email": "jane.smith@university.edu",
  "given_name": "Jane",
  "family_name": "Smith",

  "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
    "scope": [
      "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
      "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
      "https://purl.imsglobal.org/spec/lti-ags/scope/score"
    ],
    "lineitems": "https://canvas.instructure.com/api/lti/courses/101/line_items",
    "lineitem": "https://canvas.instructure.com/api/lti/courses/101/line_items/456"
  },

  "https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice": {
    "context_memberships_url": "https://canvas.instructure.com/api/lti/courses/101/names_and_roles",
    "service_versions": ["2.0"]
  }
}
```

### 3. Validating the ID Token (Critical Security Step)

```python
from jwcrypto import jwk, jwt
import requests
import time

def validate_lti_launch(id_token, platform_config):
    """
    Validates LTI 1.3 launch ID token.

    Security checks:
    1. Signature verification using platform's public key
    2. Issuer matches registered platform
    3. Audience matches our client_id
    4. Not expired
    5. Nonce hasn't been used before (replay attack prevention)
    6. Required LTI claims present
    """

    # Fetch platform's public keys (JWK Set)
    jwks_response = requests.get(platform_config['key_set_url'])
    jwks = jwk.JWKSet.from_json(jwks_response.text)

    # Decode and verify token
    try:
        token = jwt.JWT(key=jwks, jwt=id_token)
        claims = json.loads(token.claims)
    except Exception as e:
        raise ValueError(f"Token validation failed: {str(e)}")

    # Verify issuer
    if claims.get('iss') != platform_config['issuer']:
        raise ValueError("Invalid issuer")

    # Verify audience (client_id)
    aud = claims.get('aud')
    if isinstance(aud, list):
        if platform_config['client_id'] not in aud:
            raise ValueError("Invalid audience")
    elif aud != platform_config['client_id']:
        raise ValueError("Invalid audience")

    # Verify expiration
    if claims.get('exp', 0) < time.time():
        raise ValueError("Token expired")

    # Verify nonce (check against cache to prevent replay)
    nonce = claims.get('nonce')
    if not nonce or is_nonce_used(nonce):
        raise ValueError("Invalid or reused nonce")
    mark_nonce_as_used(nonce, expires_at=claims['exp'])

    # Verify required LTI claims
    required_claims = [
        'https://purl.imsglobal.org/spec/lti/claim/message_type',
        'https://purl.imsglobal.org/spec/lti/claim/version',
        'https://purl.imsglobal.org/spec/lti/claim/deployment_id'
    ]
    for claim in required_claims:
        if claim not in claims:
            raise ValueError(f"Missing required claim: {claim}")

    return claims

def is_nonce_used(nonce):
    """Check if nonce has been used (Redis, DB, or in-memory cache)"""
    # Implementation depends on your caching strategy
    return redis_client.exists(f"lti:nonce:{nonce}")

def mark_nonce_as_used(nonce, expires_at):
    """Mark nonce as used with expiration"""
    ttl = expires_at - int(time.time())
    redis_client.setex(f"lti:nonce:{nonce}", ttl, "1")
```

### 4. Provisioning User & Context

After validating the launch, provision or update the user and course in your system:

```python
def provision_lti_session(claims):
    """
    Create or update user and course based on LTI claims.
    Returns: (user, course, resource_link)
    """

    # Extract user information
    platform_user_id = claims['sub']
    email = claims.get('email')
    name = claims.get('name')
    roles = claims.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])

    # Determine role (simplified)
    is_instructor = any('Instructor' in role for role in roles)
    is_student = any('Learner' in role or 'Student' in role for role in roles)

    # Get or create user
    user = User.get_or_create(
        lti_platform=claims['iss'],
        lti_user_id=platform_user_id,
        defaults={'email': email, 'name': name}
    )

    # Update user info if changed
    if user.email != email or user.name != name:
        user.email = email
        user.name = name
        user.save()

    # Extract course/context information
    context = claims.get('https://purl.imsglobal.org/spec/lti/claim/context', {})
    course_id = context.get('id')
    course_title = context.get('title')

    if course_id:
        course = Course.get_or_create(
            lti_platform=claims['iss'],
            lti_context_id=course_id,
            defaults={'title': course_title}
        )

        # Enroll user in course with appropriate role
        enrollment = Enrollment.get_or_create(
            user=user,
            course=course,
            defaults={'role': 'instructor' if is_instructor else 'student'}
        )

    # Extract resource link (specific assignment/activity)
    resource_link_claim = claims.get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {})
    resource_link_id = resource_link_claim.get('id')
    resource_link_title = resource_link_claim.get('title')

    resource_link = ResourceLink.get_or_create(
        lti_platform=claims['iss'],
        lti_resource_link_id=resource_link_id,
        course=course,
        defaults={'title': resource_link_title}
    )

    return user, course, resource_link
```

### 5. Deep Linking (Content Selection)

**Use Case**: Instructor clicks "Add External Tool" in LMS, selects content from your tool, and embeds it in their course.

**Deep Linking Launch** (Platform → Tool):
- Message type: `LtiDeepLinkingRequest`
- Contains `deep_linking_settings` claim with `accept_types`, `accept_presentation_document_targets`, `return_url`

**Deep Linking Response** (Tool → Platform):
```python
from jwcrypto import jwt, jwk
import json

def create_deep_linking_response(platform_config, deployment_id, selected_content):
    """
    Create a deep linking response JWT to send back to platform.

    selected_content: List of content items chosen by instructor
    """

    # Load your tool's private key
    with open('private_key.pem', 'rb') as key_file:
        private_key = jwk.JWK.from_pem(key_file.read())

    # Build content items
    content_items = []
    for item in selected_content:
        content_items.append({
            "type": "ltiResourceLink",
            "title": item['title'],
            "url": f"https://physics-sim.example.com/lti/launch?sim={item['id']}",
            "custom": {
                "simulation_id": item['id'],
                "difficulty": item['difficulty']
            }
        })

    # Create JWT
    jwt_claims = {
        "iss": platform_config['client_id'],  # Tool is now the issuer
        "aud": [platform_config['issuer']],   # Platform is the audience
        "exp": int(time.time()) + 600,  # 10 minute expiration
        "iat": int(time.time()),
        "nonce": generate_nonce(),

        "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiDeepLinkingResponse",
        "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
        "https://purl.imsglobal.org/spec/lti/claim/deployment_id": deployment_id,

        "https://purl.imsglobal.org/spec/lti-dl/claim/content_items": content_items
    }

    token = jwt.JWT(header={"alg": "RS256", "kid": private_key.key_id}, claims=json.dumps(jwt_claims))
    token.make_signed_token(private_key)

    return token.serialize()

# Return as form POST to platform's return_url
return f"""
<html>
<body>
<form id="deep-link-form" action="{return_url}" method="POST">
  <input type="hidden" name="JWT" value="{deep_link_jwt}">
</form>
<script>document.getElementById('deep-link-form').submit();</script>
</body>
</html>
"""
```

### 6. Assignment and Grade Services (AGS)

**Reading Lineitem** (assignment in gradebook):
```python
def get_lineitem(lineitem_url, access_token):
    """Fetch lineitem (assignment) details from platform."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.ims.lis.v2.lineitem+json'
    }
    response = requests.get(lineitem_url, headers=headers)
    return response.json()
```

**Submitting a Score**:
```python
def submit_score(lineitem_url, access_token, user_id, score, max_score=100):
    """
    Submit a score to the platform's gradebook.

    Args:
        lineitem_url: AGS lineitem URL from launch claims
        access_token: OAuth 2.0 access token for AGS scope
        user_id: LTI user ID (from 'sub' claim)
        score: Earned score
        max_score: Maximum possible score
    """

    score_url = f"{lineitem_url}/scores"

    score_data = {
        "userId": user_id,
        "scoreGiven": score,
        "scoreMaximum": max_score,
        "comment": "Auto-graded simulation performance",
        "activityProgress": "Completed",
        "gradingProgress": "FullyGraded",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/vnd.ims.lis.v1.score+json'
    }

    response = requests.post(score_url, json=score_data, headers=headers)

    if response.status_code == 200:
        return {"success": True}
    else:
        return {"success": False, "error": response.text}
```

**Getting Access Token for AGS**:
```python
def get_ags_access_token(platform_config, scopes):
    """
    Get OAuth 2.0 access token for AGS service.

    Uses client_credentials grant with JWT assertion.
    """

    # Create JWT assertion
    with open('private_key.pem', 'rb') as key_file:
        private_key = jwk.JWK.from_pem(key_file.read())

    jwt_claims = {
        "iss": platform_config['client_id'],
        "sub": platform_config['client_id'],
        "aud": platform_config['auth_token_url'],
        "iat": int(time.time()),
        "exp": int(time.time()) + 60,
        "jti": generate_nonce()
    }

    token = jwt.JWT(header={"alg": "RS256"}, claims=json.dumps(jwt_claims))
    token.make_signed_token(private_key)
    client_assertion = token.serialize()

    # Request access token
    data = {
        'grant_type': 'client_credentials',
        'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'client_assertion': client_assertion,
        'scope': ' '.join(scopes)
    }

    response = requests.post(platform_config['auth_token_url'], data=data)
    return response.json()['access_token']
```

### 7. Names and Role Provisioning Service (NRPS)

**Fetching Course Roster**:
```python
def get_course_roster(nrps_url, access_token):
    """
    Fetch course membership (roster) from platform.

    Returns list of members with roles and basic information.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.ims.lti-nrps.v2.membershipcontainer+json'
    }

    response = requests.get(nrps_url, headers=headers)
    data = response.json()

    members = []
    for member in data.get('members', []):
        members.append({
            'user_id': member['user_id'],
            'name': member.get('name'),
            'email': member.get('email'),
            'roles': member.get('roles', []),
            'status': member.get('status', 'Active')
        })

    return members
```

## Security Best Practices

### 1. State Parameter
- Always use a cryptographically random `state` parameter
- Validate state on callback to prevent CSRF attacks
- Store state server-side tied to session

### 2. Nonce Management
- Generate cryptographically random nonces
- Store used nonces with expiration (Redis recommended)
- Reject any token with a reused nonce (replay attack prevention)

### 3. Token Validation
- **ALWAYS** validate ID token signature using platform's public keys
- Verify issuer, audience, expiration
- Check deployment_id matches your registration

### 4. HTTPS Only
- All LTI endpoints MUST use HTTPS
- Redirect HTTP requests to HTTPS

### 5. Key Management
- Store private keys securely (encrypted at rest, not in version control)
- Rotate keys periodically
- Support multiple active keys (key_id in JWT header)

### 6. Scoped Permissions
- Request only the LTI scopes you actually need
- Store access tokens securely (encrypted)
- Use short-lived access tokens (request new when needed)

## Testing Tools

**LTI Advantage Complete Test Suite**:
https://lti-ri.imsglobal.org/

**Canvas LTI 1.3 Developer Keys**:
Configure test instance at https://canvas.instructure.com/doc/api/file.lti_dev_key_config.html

**Python Library**:
```bash
pip install PyLTI1p3
```

**Example with PyLTI1p3**:
```python
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.message_launch import MessageLaunch
from pylti1p3.grade_passback import GradePassback

# Configuration
tool_conf = ToolConfJsonFile('config.json')

# Handle launch
@app.route('/lti/launch', methods=['POST'])
def lti_launch():
    launch = MessageLaunch(request, tool_conf)
    if not launch.validate():
        return "Invalid launch", 401

    # Use launch data
    user_id = launch.get_launch_data().get('sub')
    return render_template('tool_page.html', user_id=user_id)

# Submit grade
def submit_grade_example(launch, score):
    ags = launch.get_ags()
    score_data = {
        "scoreGiven": score,
        "scoreMaximum": 100,
        "activityProgress": "Completed",
        "gradingProgress": "FullyGraded"
    }
    ags.put_grade(score_data)
```

## Common Pitfalls

1. **Not validating nonces**: Allows replay attacks
2. **Skipping signature verification**: Allows token forgery
3. **Hardcoding platform URLs**: Different per deployment
4. **Not handling multiple deployments**: Same platform, different contexts
5. **Exposing private keys**: Store securely, never commit to git
6. **Long-lived access tokens**: Request fresh tokens for each AGS/NRPS call
7. **Not testing with real LMS**: Subtle differences between platforms

## References

- **IMS LTI 1.3 Core Specification**: https://www.imsglobal.org/spec/lti/v1p3/
- **LTI Advantage**: https://www.imsglobal.org/activity/learning-tools-interoperability
- **Canvas LTI 1.3 Docs**: https://canvas.instructure.com/doc/api/file.lti_dev_key_config.html
- **Moodle LTI Docs**: https://docs.moodle.org/en/LTI_and_Moodle
- **PyLTI1p3 Library**: https://github.com/dmitry-viskov/pylti1p3

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain
