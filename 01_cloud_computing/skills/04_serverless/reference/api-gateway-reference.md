# API Gateway & Serverless APIs Reference

## Overview

API Gateways provide managed HTTP endpoints for serverless functions, handling routing, authentication, rate limiting, caching, and more.

## AWS API Gateway

### API Types

#### REST API
```yaml
Protocol: HTTP/HTTPS
Features: Full REST API features, request/response transformations
Pricing: $3.50 per million requests + data transfer
Use Cases: Complex APIs, request transformation, caching
Authorization: IAM, Cognito, Lambda authorizers, API keys
```

**Features**:
- Request/response transformation
- Request validation
- API caching
- Usage plans and API keys
- Custom domain names
- WAF integration
- Client SDKs generation

#### HTTP API
```yaml
Protocol: HTTP/HTTPS (HTTP/2, HTTP/1.1)
Features: Lightweight, lower latency, lower cost
Pricing: $1.00 per million requests + data transfer
Use Cases: Microservices, webhooks, proxy to Lambda
Authorization: IAM, JWT (Cognito, external), Lambda authorizers
```

**Advantages over REST API**:
- 70% cheaper
- Lower latency (~50ms faster)
- Automatic deployments
- CORS built-in
- JWT authorizers native

**Limitations** (vs REST):
- No request transformation (use Lambda)
- No usage plans/API keys
- No caching
- No request validators
- No API Gateway-level throttling per client

#### WebSocket API
```yaml
Protocol: WebSocket (bidirectional)
Pricing: $1.00 per million messages + connection minutes
Use Cases: Chat applications, real-time dashboards, multiplayer games
Features: Persistent connections, server-to-client push
```

### REST API Deep Dive

#### Integration Types

**Lambda Proxy Integration** (Recommended):
```json
// API Gateway passes everything to Lambda
{
  "resource": "/users/{id}",
  "httpMethod": "GET",
  "headers": {...},
  "queryStringParameters": {...},
  "pathParameters": {"id": "123"},
  "body": null
}

// Lambda must return specific format
{
  "statusCode": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"user\": \"data\"}"
}
```

**Lambda Custom Integration**:
```yaml
Use: When you need request/response transformation
Mapping Templates: VTL (Velocity Template Language)
```

**HTTP Integration**:
```yaml
Use: Proxy to HTTP endpoints
Types: Proxy or custom
```

**AWS Service Integration**:
```yaml
Use: Direct integration with AWS services (no Lambda)
Examples: DynamoDB, S3, SNS, SQS, Step Functions
```

**Mock Integration**:
```yaml
Use: Return static responses
Examples: CORS preflight, placeholder APIs
```

#### Request Validation
```json
{
  "type": "object",
  "required": ["name", "email"],
  "properties": {
    "name": {"type": "string", "minLength": 1},
    "email": {"type": "string", "format": "email"},
    "age": {"type": "integer", "minimum": 0}
  }
}
```

**Benefits**:
- Reject invalid requests before Lambda invocation
- Reduce Lambda costs
- Consistent validation

#### Mapping Templates (VTL)
**Request Template**:
```vtl
{
  "userId": "$input.params('id')",
  "body": $input.json('$'),
  "timestamp": "$context.requestTimeEpoch"
}
```

**Response Template**:
```vtl
#set($inputRoot = $input.path('$'))
{
  "data": $inputRoot,
  "metadata": {
    "requestId": "$context.requestId"
  }
}
```

#### Caching
```yaml
Cache Sizes: 0.5 GB - 237 GB
TTL: 0 - 3600 seconds
Pricing: $0.020/hour for 0.5 GB
Encryption: Optional
Per-key Invalidation: Yes
```

**Caching Strategy**:
```python
# Lambda can control caching
def handler(event, context):
    response = get_data()

    return {
        'statusCode': 200,
        'headers': {
            'Cache-Control': 'max-age=300'  # 5 minutes
        },
        'body': json.dumps(response)
    }
```

#### Throttling
```yaml
Account Limit: 10,000 requests/second (soft limit)
Burst: 5,000 requests
Method-Level: Custom limits per endpoint
Stage-Level: Overall stage throttle
Usage Plans: Per-client throttling
```

**Example: Usage Plan**:
```bash
aws apigateway create-usage-plan \
  --name "Gold Plan" \
  --throttle burstLimit=100,rateLimit=50 \
  --quota limit=10000,period=MONTH
```

#### Custom Domains
```bash
# Create custom domain
aws apigateway create-domain-name \
  --domain-name api.example.com \
  --certificate-arn arn:aws:acm:...

# Create base path mapping
aws apigateway create-base-path-mapping \
  --domain-name api.example.com \
  --rest-api-id abc123 \
  --stage prod \
  --base-path v1
```

**Result**: `https://api.example.com/v1/users`

#### CORS
```json
{
  "headers": {
    "Access-Control-Allow-Origin": "'*'",
    "Access-Control-Allow-Headers": "'Content-Type,Authorization'",
    "Access-Control-Allow-Methods": "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}
```

**Automatic CORS (HTTP API)**:
```bash
aws apigatewayv2 create-api \
  --name my-api \
  --protocol-type HTTP \
  --cors-configuration AllowOrigins="https://example.com",AllowMethods="GET,POST"
```

### HTTP API Details

**Pros**:
- 70% cheaper than REST API
- Lower latency
- Automatic deployments
- Native JWT validation
- Built-in CORS

**Example (Terraform)**:
```hcl
resource "aws_apigatewayv2_api" "api" {
  name          = "my-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["https://example.com"]
    allow_methods = ["GET", "POST", "PUT", "DELETE"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.function.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /users/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}
```

### WebSocket API

**Connection Management**:
```python
import boto3

apigateway_management = boto3.client(
    'apigatewaymanagementapi',
    endpoint_url=f'https://{connection_id}.execute-api.{region}.amazonaws.com/{stage}'
)

# Send message to client
apigateway_management.post_to_connection(
    ConnectionId=connection_id,
    Data=json.dumps({'message': 'Hello from server'})
)

# Disconnect client
apigateway_management.delete_connection(ConnectionId=connection_id)
```

**Routes**:
```yaml
$connect: Client connects (can authorize)
$disconnect: Client disconnects
$default: Default route for unmatched messages
custom: Custom route actions
```

**Example**:
```json
// Client sends
{"action": "sendMessage", "message": "Hello"}

// Lambda receives
{
  "requestContext": {
    "routeKey": "sendMessage",
    "connectionId": "abc123"
  },
  "body": "{\"message\": \"Hello\"}"
}
```

### Authorization

#### IAM Authorization
```python
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Sign request with AWS credentials
request = AWSRequest(
    method='GET',
    url='https://abc123.execute-api.us-east-1.amazonaws.com/prod/users',
    headers={'Host': 'abc123.execute-api.us-east-1.amazonaws.com'}
)

SigV4Auth(session.get_credentials(), 'execute-api', 'us-east-1').add_auth(request)
```

#### Cognito User Pools
```yaml
Authorization: Bearer <JWT token from Cognito>
Validation: Automatic by API Gateway
Claims: Available in $context.authorizer.claims
```

#### Lambda Authorizers (Custom)
```python
def handler(event, context):
    token = event['authorizationToken']  # "Bearer <token>"

    # Validate token (call OAuth server, check database, etc.)
    if validate_token(token):
        return {
            "principalId": "user123",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event['methodArn']
                }]
            },
            "context": {
                "userId": "user123",
                "role": "admin"
            }
        }
    else:
        raise Exception("Unauthorized")
```

**Types**:
- **TOKEN**: Authorization header
- **REQUEST**: Headers, query params, stage variables

**Caching**: Cache authorization decisions (TTL: 0-3600s)

## Azure API Management

### Overview
Enterprise-grade API Gateway with additional features like developer portal, monetization, and analytics.

**Tiers**:
```yaml
Consumption: Pay-per-execution, autoscales
Developer: Fixed cost, 1 unit, no SLA
Basic: Fixed cost, 2 units, 99.95% SLA
Standard: Fixed cost, 4 units, 99.95% SLA
Premium: Fixed cost, multi-region, 99.99% SLA
```

### Features

#### Policies
```xml
<policies>
  <inbound>
    <rate-limit calls="100" renewal-period="60" />
    <cors>
      <allowed-origins>
        <origin>https://example.com</origin>
      </allowed-origins>
    </cors>
    <set-header name="X-Forwarded-For" exists-action="override">
      <value>@(context.Request.IpAddress)</value>
    </set-header>
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <set-body>
      @{
        var response = context.Response.Body.As<JObject>();
        response["metadata"] = new JObject(
          new JProperty("timestamp", DateTime.UtcNow)
        );
        return response.ToString();
      }
    </set-body>
  </outbound>
  <on-error>
    <set-status code="500" reason="Internal Server Error" />
  </on-error>
</policies>
```

#### Response Caching
```xml
<cache-lookup vary-by-developer="false" vary-by-developer-groups="false">
  <vary-by-query-parameter>category</vary-by-query-parameter>
</cache-lookup>
<cache-store duration="3600" />
```

#### Authentication
- OAuth 2.0
- Azure AD
- Client certificates
- Subscriptionkeys

### Consumption Tier (Serverless)
```yaml
Pricing: $0.0035 per 10,000 calls
Auto-scaling: Yes
Throughput: 10,000 requests/second per region
Features: All except VNet, multi-region, caching
```

## Google Cloud Endpoints / API Gateway

### Cloud Endpoints
**OpenAPI-based** API management.

**Supported Backends**:
- Cloud Functions
- Cloud Run
- App Engine
- GKE

**Example (OpenAPI)**:
```yaml
swagger: "2.0"
info:
  title: "My API"
  version: "1.0.0"
host: "my-api-abc123-uc.a.run.app"
schemes:
  - "https"
paths:
  /users:
    get:
      summary: "Get users"
      operationId: "getUsers"
      x-google-backend:
        address: "https://users-service.a.run.app/users"
      responses:
        200:
          description: "Success"
```

**Deploy**:
```bash
gcloud endpoints services deploy openapi.yaml
```

### API Gateway (Managed)
**Features**:
- API management
- Authentication (API keys, Firebase Auth, Service Accounts)
- Rate limiting
- Monitoring

**Example (gcloud)**:
```bash
gcloud api-gateway apis create my-api

gcloud api-gateway api-configs create my-config \
  --api=my-api \
  --openapi-spec=openapi.yaml \
  --backend-auth-service-account=my-sa@project.iam.gserviceaccount.com

gcloud api-gateway gateways create my-gateway \
  --api=my-api \
  --api-config=my-config \
  --location=us-central1
```

## Serverless Framework Integration

### AWS (serverless.yml)
```yaml
service: my-api

provider:
  name: aws
  runtime: nodejs20.x
  stage: ${opt:stage, 'dev'}
  region: us-east-1

  httpApi:  # HTTP API
    cors: true
    authorizers:
      jwtAuthorizer:
        type: jwt
        identitySource: $request.header.Authorization
        issuerUrl: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_ABC123
        audience:
          - my-app-client-id

functions:
  getUser:
    handler: handler.getUser
    events:
      - httpApi:
          path: /users/{id}
          method: get
          authorizer:
            name: jwtAuthorizer

  createUser:
    handler: handler.createUser
    events:
      - httpApi:
          path: /users
          method: post
```

### Azure (serverless.yml)
```yaml
service: my-azure-api

provider:
  name: azure
  region: West US
  runtime: node18

functions:
  getUsers:
    handler: handlers/users.getUsers
    events:
      - http: true
        x-azure-settings:
          methods:
            - GET
          authLevel: function
          route: users
```

## Best Practices

### Performance
1. Use HTTP API over REST API when possible (AWS)
2. Enable caching for read-heavy endpoints
3. Implement CDN caching (CloudFront) for static responses
4. Use Lambda proxy integration (avoid mapping templates)
5. Enable compression

### Security
1. Always use HTTPS (TLS 1.2+)
2. Implement authentication (OAuth, JWT, API keys)
3. Use WAF for protection against common attacks
4. Rate limit APIs
5. Validate requests before Lambda invocation
6. Use custom domains (avoid exposing .execute-api.amazonaws.com)

### Cost Optimization
1. Use HTTP API instead of REST API (AWS - 70% savings)
2. Implement caching to reduce backend calls
3. Use request validation to reject invalid requests early
4. Monitor and alert on unexpected usage
5. Implement usage plans for different tiers

### Reliability
1. Implement retry logic in clients
2. Use circuit breakers for downstream dependencies
3. Set appropriate timeouts
4. Monitor error rates and latencies
5. Implement health check endpoints

### API Design
1. Follow RESTful conventions
2. Version APIs (path-based: /v1/users or header-based)
3. Use consistent error responses
4. Implement HATEOAS (links to related resources)
5. Document with OpenAPI/Swagger

## Monitoring & Logging

### AWS CloudWatch Metrics
```yaml
IntegrationLatency: Backend processing time
Latency: End-to-end latency
Count: Number of API calls
4XXError: Client errors
5XXError: Server errors
CacheHitCount: Cache hits
CacheMissCount: Cache misses
```

### AWS X-Ray
Enable tracing:
```bash
aws apigateway update-stage \
  --rest-api-id abc123 \
  --stage-name prod \
  --patch-operations op=replace,path=/tracingEnabled,value=true
```

### Custom Logging
```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info({
        "event": "api_request",
        "path": event['path'],
        "method": event['httpMethod'],
        "sourceIp": event['requestContext']['identity']['sourceIp'],
        "userAgent": event['requestContext']['identity']['userAgent'],
        "requestId": event['requestContext']['requestId']
    })
```

## Resources

- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Azure API Management Documentation](https://docs.microsoft.com/azure/api-management/)
- [Google Cloud Endpoints](https://cloud.google.com/endpoints/docs)
- [OpenAPI Specification](https://swagger.io/specification/)
