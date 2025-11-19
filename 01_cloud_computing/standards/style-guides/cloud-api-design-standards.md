# Cloud API Design Standards

## Overview

This guide establishes API design standards for cloud services, covering RESTful APIs, GraphQL, and gRPC. Based on best practices from Google Cloud API Design Guide, Microsoft REST API Guidelines, AWS API Standards, and FAANG API patterns.

## Table of Contents

1. [API Design Principles](#api-design-principles)
2. [RESTful API Standards](#restful-api-standards)
3. [GraphQL Guidelines](#graphql-guidelines)
4. [gRPC Conventions](#grpc-conventions)
5. [Authentication & Authorization](#authentication--authorization)
6. [Versioning Strategies](#versioning-strategies)
7. [Error Handling](#error-handling)
8. [Rate Limiting & Throttling](#rate-limiting--throttling)
9. [Documentation Standards](#documentation-standards)
10. [Anti-Patterns](#anti-patterns)
11. [References](#references)

## API Design Principles

### Core Tenets

1. **Developer Experience First**: APIs should be intuitive, consistent, and well-documented
2. **Backward Compatibility**: Never break existing clients without clear migration path
3. **Resource-Oriented Design**: Think in terms of resources and their relationships
4. **Consistent Naming**: Use predictable, standard naming conventions
5. **Security by Default**: Authentication, authorization, encryption, input validation
6. **Observable**: Comprehensive logging, metrics, tracing
7. **Idempotent Operations**: Safe to retry without unintended side effects

### API Maturity Model (Richardson Maturity Model)

- **Level 0**: Single endpoint, single HTTP method (RPC style)
- **Level 1**: Multiple resource-based URIs
- **Level 2**: HTTP verbs properly used
- **Level 3**: HATEOAS (Hypermedia controls) - optional for most cloud APIs

**Target**: Minimum Level 2, Level 3 for public APIs where discoverability is critical.

## RESTful API Standards

### Resource Naming

**Format**: `/api/v{version}/{resources}/{identifier}/{sub-resources}`

**Rules**:
1. Use plural nouns for collections: `/users`, `/orders`, `/products`
2. Use hierarchical paths for relationships: `/users/123/orders`
3. Use kebab-case for multi-word resources: `/product-categories`
4. No trailing slashes
5. No file extensions (.json, .xml)
6. Use query parameters for filtering, sorting, pagination

**Examples**:

```
✅ Good:
GET    /api/v1/users
GET    /api/v1/users/123
GET    /api/v1/users/123/orders
GET    /api/v1/orders?status=pending&sort=-createdAt&limit=20
POST   /api/v1/users
PUT    /api/v1/users/123
PATCH  /api/v1/users/123
DELETE /api/v1/users/123

❌ Bad:
GET    /api/v1/user              # Singular noun
GET    /api/v1/getAllUsers       # RPC-style
GET    /api/v1/users/123/        # Trailing slash
POST   /api/v1/createUser        # Verb in path
GET    /api/v1/users.json        # File extension
```

### HTTP Methods

| Method | Usage | Idempotent | Safe | Request Body | Response Body |
|--------|-------|------------|------|--------------|---------------|
| GET | Retrieve resource(s) | Yes | Yes | No | Yes |
| POST | Create resource | No | No | Yes | Yes |
| PUT | Replace resource | Yes | No | Yes | Yes |
| PATCH | Partial update | No* | No | Yes | Yes |
| DELETE | Remove resource | Yes | No | No | Minimal |
| HEAD | Get metadata only | Yes | Yes | No | No |
| OPTIONS | Get allowed methods | Yes | Yes | No | Yes |

*PATCH can be idempotent if designed properly (JSON Patch with test operations)

### Request/Response Examples

**GET Collection**:

```http
GET /api/v1/users?status=active&role=admin&page=2&limit=20&sort=-createdAt HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Accept: application/json
```

```json
{
  "data": [
    {
      "id": "usr_1234567890",
      "email": "alice@example.com",
      "name": "Alice Johnson",
      "role": "admin",
      "status": "active",
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-03-10T14:22:00Z",
      "links": {
        "self": "/api/v1/users/usr_1234567890",
        "orders": "/api/v1/users/usr_1234567890/orders"
      }
    }
  ],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrevious": true,
    "links": {
      "first": "/api/v1/users?status=active&role=admin&page=1&limit=20",
      "prev": "/api/v1/users?status=active&role=admin&page=1&limit=20",
      "self": "/api/v1/users?status=active&role=admin&page=2&limit=20",
      "next": "/api/v1/users?status=active&role=admin&page=3&limit=20",
      "last": "/api/v1/users?status=active&role=admin&page=8&limit=20"
    }
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-03-15T16:30:00Z"
  }
}
```

**POST Create**:

```http
POST /api/v1/users HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json
Idempotency-Key: 7d4e2f89-1a3b-4c5d-8e7f-9a0b1c2d3e4f
```

```json
{
  "email": "bob@example.com",
  "name": "Bob Smith",
  "role": "user",
  "metadata": {
    "department": "Engineering",
    "location": "US-WEST"
  }
}
```

**Response (201 Created)**:

```http
HTTP/1.1 201 Created
Location: /api/v1/users/usr_0987654321
Content-Type: application/json
```

```json
{
  "data": {
    "id": "usr_0987654321",
    "email": "bob@example.com",
    "name": "Bob Smith",
    "role": "user",
    "status": "active",
    "metadata": {
      "department": "Engineering",
      "location": "US-WEST"
    },
    "createdAt": "2024-03-15T16:35:00Z",
    "updatedAt": "2024-03-15T16:35:00Z",
    "links": {
      "self": "/api/v1/users/usr_0987654321"
    }
  },
  "meta": {
    "requestId": "req_xyz789",
    "timestamp": "2024-03-15T16:35:00Z"
  }
}
```

**PATCH Partial Update**:

```http
PATCH /api/v1/users/usr_0987654321 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json
If-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

```json
{
  "name": "Robert Smith",
  "metadata": {
    "location": "US-EAST"
  }
}
```

**PUT Full Replacement** (less common):

```http
PUT /api/v1/users/usr_0987654321 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json
```

```json
{
  "email": "bob@example.com",
  "name": "Robert Smith",
  "role": "user",
  "status": "active",
  "metadata": {
    "department": "Engineering",
    "location": "US-EAST"
  }
}
```

**DELETE**:

```http
DELETE /api/v1/users/usr_0987654321 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
```

**Response (204 No Content or 200 with body)**:

```http
HTTP/1.1 204 No Content
```

Or with confirmation:

```json
{
  "data": {
    "id": "usr_0987654321",
    "deleted": true,
    "deletedAt": "2024-03-15T16:40:00Z"
  }
}
```

### Query Parameters

**Filtering**:
```
GET /api/v1/orders?status=pending&customerId=usr_123&minTotal=100
```

**Sorting**:
```
# Single field
GET /api/v1/users?sort=createdAt        # Ascending
GET /api/v1/users?sort=-createdAt       # Descending (- prefix)

# Multiple fields
GET /api/v1/users?sort=-createdAt,name
```

**Pagination** (Offset-based):
```
GET /api/v1/users?page=2&limit=20
# or
GET /api/v1/users?offset=20&limit=20
```

**Pagination** (Cursor-based, preferred for large datasets):
```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20
```

**Field Selection** (Sparse fieldsets):
```
GET /api/v1/users?fields=id,name,email
GET /api/v1/users/123?fields=id,name,orders(id,total,status)
```

**Searching**:
```
GET /api/v1/products?q=laptop&category=electronics
GET /api/v1/users?search=alice
```

### HTTP Status Codes

**Success Codes**:
- `200 OK` - Successful GET, PUT, PATCH, or DELETE with response body
- `201 Created` - Successful POST creating a resource
- `202 Accepted` - Request accepted for async processing
- `204 No Content` - Successful request with no response body (DELETE)
- `206 Partial Content` - Partial GET (range request)

**Client Error Codes**:
- `400 Bad Request` - Invalid request format or parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Valid auth but insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `405 Method Not Allowed` - HTTP method not supported for resource
- `409 Conflict` - Resource conflict (duplicate, version mismatch)
- `410 Gone` - Resource permanently deleted
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded

**Server Error Codes**:
- `500 Internal Server Error` - Generic server error
- `502 Bad Gateway` - Invalid response from upstream
- `503 Service Unavailable` - Temporary unavailability
- `504 Gateway Timeout` - Upstream timeout

### Response Envelope

**Standard Envelope**:

```json
{
  "data": { /* Resource data or array */ },
  "error": { /* Error details if applicable */ },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-03-15T16:30:00Z",
    "version": "v1"
  },
  "pagination": { /* If applicable */ },
  "links": { /* HATEOAS links */ }
}
```

**Minimal Envelope** (for high-performance APIs):

```json
{
  "id": "usr_123",
  "name": "Alice",
  "email": "alice@example.com"
}
```

### Bulk Operations

**Batch Create**:

```http
POST /api/v1/users/batch HTTP/1.1
```

```json
{
  "items": [
    { "email": "user1@example.com", "name": "User One" },
    { "email": "user2@example.com", "name": "User Two" }
  ]
}
```

**Response**:

```json
{
  "data": {
    "successful": [
      { "id": "usr_001", "email": "user1@example.com", "index": 0 }
    ],
    "failed": [
      {
        "index": 1,
        "email": "user2@example.com",
        "error": {
          "code": "DUPLICATE_EMAIL",
          "message": "Email already exists"
        }
      }
    ]
  },
  "meta": {
    "total": 2,
    "successful": 1,
    "failed": 1
  }
}
```

## GraphQL Guidelines

### Schema Design

**Type Naming**:
- PascalCase for types: `User`, `Order`, `ProductCategory`
- camelCase for fields: `firstName`, `createdAt`, `orderItems`
- SCREAMING_SNAKE_CASE for enums: `PENDING`, `APPROVED`, `REJECTED`

**Example Schema**:

```graphql
"""
User account in the system
"""
type User {
  "Unique identifier"
  id: ID!

  "User's email address"
  email: String!

  "Full name"
  name: String!

  "Account role"
  role: Role!

  "Account status"
  status: UserStatus!

  "User's orders"
  orders(
    "Filter by order status"
    status: OrderStatus
    "Number of orders to return"
    first: Int = 20
    "Cursor for pagination"
    after: String
  ): OrderConnection!

  "ISO 8601 timestamp"
  createdAt: DateTime!

  "ISO 8601 timestamp"
  updatedAt: DateTime!
}

enum Role {
  ADMIN
  USER
  GUEST
}

enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

"""
Connection pattern for pagination
"""
type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type OrderEdge {
  node: Order!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  "Get user by ID"
  user(id: ID!): User

  "List users with filtering"
  users(
    status: UserStatus
    role: Role
    first: Int = 20
    after: String
  ): UserConnection!

  "Search users"
  searchUsers(
    query: String!
    first: Int = 20
  ): UserConnection!
}

type Mutation {
  "Create a new user"
  createUser(input: CreateUserInput!): CreateUserPayload!

  "Update existing user"
  updateUser(input: UpdateUserInput!): UpdateUserPayload!

  "Delete user"
  deleteUser(id: ID!): DeleteUserPayload!
}

input CreateUserInput {
  email: String!
  name: String!
  role: Role = USER
  metadata: JSON
}

type CreateUserPayload {
  user: User
  errors: [UserError!]
}

type UserError {
  field: String
  message: String!
  code: ErrorCode!
}

enum ErrorCode {
  VALIDATION_ERROR
  DUPLICATE_EMAIL
  UNAUTHORIZED
  NOT_FOUND
}
```

### Resolver Best Practices

```javascript
// resolvers/user.js
const resolvers = {
  Query: {
    user: async (parent, { id }, context) => {
      // Check authentication
      if (!context.user) {
        throw new Error('UNAUTHORIZED');
      }

      // Use DataLoader to batch and cache
      return context.loaders.userLoader.load(id);
    },

    users: async (parent, { status, role, first, after }, context) => {
      if (!context.user) {
        throw new Error('UNAUTHORIZED');
      }

      const filters = {
        ...(status && { status }),
        ...(role && { role }),
      };

      return context.dataSources.userAPI.getUsers({
        filters,
        first,
        after,
      });
    },
  },

  User: {
    // Resolver for orders field with N+1 prevention
    orders: async (user, { status, first, after }, context) => {
      return context.dataSources.orderAPI.getOrdersByUserId({
        userId: user.id,
        status,
        first,
        after,
      });
    },
  },

  Mutation: {
    createUser: async (parent, { input }, context) => {
      // Check permissions
      if (!context.user?.isAdmin) {
        return {
          user: null,
          errors: [{
            message: 'Insufficient permissions',
            code: 'UNAUTHORIZED',
          }],
        };
      }

      // Validate input
      const validationErrors = validateCreateUserInput(input);
      if (validationErrors.length > 0) {
        return { user: null, errors: validationErrors };
      }

      try {
        const user = await context.dataSources.userAPI.createUser(input);
        return { user, errors: [] };
      } catch (error) {
        return {
          user: null,
          errors: [{
            message: error.message,
            code: 'INTERNAL_ERROR',
          }],
        };
      }
    },
  },
};
```

### DataLoader Pattern (N+1 Prevention)

```javascript
// loaders/userLoader.js
import DataLoader from 'dataloader';

export const createUserLoader = (userAPI) => {
  return new DataLoader(async (userIds) => {
    const users = await userAPI.getUsersByIds(userIds);

    // Return users in same order as requested IDs
    const userMap = new Map(users.map(user => [user.id, user]));
    return userIds.map(id => userMap.get(id) || null);
  });
};
```

## gRPC Conventions

### Proto File Structure

```protobuf
// api/v1/user_service.proto
syntax = "proto3";

package api.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "google/api/annotations.proto";

option go_package = "github.com/company/api/v1;apiv1";

// User service for account management
service UserService {
  // Get user by ID
  rpc GetUser(GetUserRequest) returns (User) {
    option (google.api.http) = {
      get: "/v1/users/{user_id}"
    };
  }

  // List users with filtering
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {
    option (google.api.http) = {
      get: "/v1/users"
    };
  }

  // Create new user
  rpc CreateUser(CreateUserRequest) returns (User) {
    option (google.api.http) = {
      post: "/v1/users"
      body: "*"
    };
  }

  // Update user
  rpc UpdateUser(UpdateUserRequest) returns (User) {
    option (google.api.http) = {
      patch: "/v1/users/{user_id}"
      body: "*"
    };
  }

  // Delete user
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty) {
    option (google.api.http) = {
      delete: "/v1/users/{user_id}"
    };
  }

  // Stream user events (server streaming)
  rpc WatchUsers(WatchUsersRequest) returns (stream UserEvent);

  // Batch create users (client streaming)
  rpc BatchCreateUsers(stream CreateUserRequest) returns (BatchCreateUsersResponse);

  // Bidirectional streaming for real-time updates
  rpc SyncUsers(stream UserSyncRequest) returns (stream UserSyncResponse);
}

message User {
  string user_id = 1;
  string email = 2;
  string name = 3;
  Role role = 4;
  UserStatus status = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
}

enum Role {
  ROLE_UNSPECIFIED = 0;
  ROLE_ADMIN = 1;
  ROLE_USER = 2;
  ROLE_GUEST = 3;
}

enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_INACTIVE = 2;
  USER_STATUS_SUSPENDED = 3;
}

message GetUserRequest {
  string user_id = 1;
}

message ListUsersRequest {
  // Filtering
  UserStatus status = 1;
  Role role = 2;

  // Pagination
  int32 page_size = 3;
  string page_token = 4;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
  Role role = 3;
}

message UpdateUserRequest {
  string user_id = 1;
  string name = 2;
  UserStatus status = 3;
}

message DeleteUserRequest {
  string user_id = 1;
}
```

### gRPC Best Practices

1. **Versioning**: Include version in package name (`api.v1`)
2. **Field Numbers**: Never reuse, reserve deprecated numbers
3. **Enums**: Always start with `_UNSPECIFIED = 0`
4. **Timestamps**: Use `google.protobuf.Timestamp`
5. **Streaming**: Use appropriately (server/client/bidirectional)
6. **HTTP Mapping**: Use `google.api.http` annotations for gRPC-Gateway

## Authentication & Authorization

### OAuth 2.0 / JWT Pattern

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**JWT Claims**:

```json
{
  "sub": "usr_1234567890",
  "email": "alice@example.com",
  "role": "admin",
  "permissions": ["users:read", "users:write", "orders:read"],
  "iat": 1710518400,
  "exp": 1710522000,
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com"
}
```

### API Key Pattern

```http
X-API-Key: api_key_EXAMPLE_NOT_REAL_123456789abcdefghijklmnop
```

### Mutual TLS (mTLS)

For service-to-service authentication in zero-trust environments.

### Authorization Models

**RBAC (Role-Based Access Control)**:
```
User -> Role -> Permissions
admin -> [users:*, orders:*, products:*]
user -> [orders:read:own, profile:*]
```

**ABAC (Attribute-Based Access Control)**:
```json
{
  "subject": { "role": "manager", "department": "sales" },
  "resource": { "type": "order", "department": "sales" },
  "action": "approve",
  "context": { "time": "business_hours" }
}
```

## Versioning Strategies

### URI Versioning (Recommended for REST)

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Pros**: Clear, cacheable, easy to route
**Cons**: Multiple base URLs

### Header Versioning

```http
GET /users HTTP/1.1
Accept: application/vnd.example.v1+json
```

**Pros**: Clean URLs
**Cons**: Harder to test, less visible

### Query Parameter Versioning

```
https://api.example.com/users?version=1
```

**Pros**: Easy to implement
**Cons**: Pollutes query space

### Versioning Best Practices

1. **Semantic Versioning**: Major version in path (v1, v2), minor/patch transparent
2. **Deprecation Timeline**: Announce deprecation, grace period (6-12 months), sunset
3. **Migration Guide**: Document breaking changes, provide examples
4. **Multiple Version Support**: Support N and N-1 versions minimum

**Deprecation Header**:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Wed, 31 Dec 2024 23:59:59 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

## Error Handling

### RFC 7807 Problem Details

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "One or more fields failed validation",
  "instance": "/api/v1/users",
  "requestId": "req_abc123",
  "timestamp": "2024-03-15T16:30:00Z",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "INVALID_FORMAT"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters",
      "code": "TOO_SHORT"
    }
  ]
}
```

### Standard Error Codes

```typescript
enum ErrorCode {
  // Validation (4xx)
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_FORMAT = 'INVALID_FORMAT',
  REQUIRED_FIELD = 'REQUIRED_FIELD',
  DUPLICATE_RESOURCE = 'DUPLICATE_RESOURCE',

  // Authentication/Authorization (4xx)
  UNAUTHORIZED = 'UNAUTHORIZED',
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  EXPIRED_TOKEN = 'EXPIRED_TOKEN',
  INSUFFICIENT_PERMISSIONS = 'INSUFFICIENT_PERMISSIONS',

  // Resource (4xx)
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  GONE = 'GONE',

  // Rate Limiting (4xx)
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',

  // Server (5xx)
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  UPSTREAM_ERROR = 'UPSTREAM_ERROR',
}
```

## Rate Limiting & Throttling

### Rate Limit Headers (IETF Draft Standard)

```http
RateLimit-Limit: 100
RateLimit-Remaining: 47
RateLimit-Reset: 1710522000
Retry-After: 3600
```

### Response When Exceeded

```http
HTTP/1.1 429 Too Many Requests
RateLimit-Limit: 100
RateLimit-Remaining: 0
RateLimit-Reset: 1710522000
Retry-After: 60
Content-Type: application/json
```

```json
{
  "type": "https://api.example.com/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the rate limit of 100 requests per hour",
  "retryAfter": 60,
  "limit": 100,
  "window": "1h"
}
```

### Rate Limiting Strategies

1. **Fixed Window**: 100 requests per hour, resets at :00
2. **Sliding Window**: 100 requests per rolling hour
3. **Token Bucket**: Burst allowance with steady refill rate
4. **Leaky Bucket**: Smooth rate limiting

## Documentation Standards

### OpenAPI 3.0 Specification

```yaml
openapi: 3.0.3
info:
  title: Example API
  version: 1.0.0
  description: RESTful API for user management
  contact:
    name: API Support
    email: api-support@example.com
    url: https://example.com/support
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://api-staging.example.com/v1
    description: Staging

paths:
  /users:
    get:
      summary: List users
      description: Retrieve a paginated list of users with optional filtering
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive, suspended]
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
      properties:
        id:
          type: string
          example: usr_1234567890
        email:
          type: string
          format: email
          example: alice@example.com
        name:
          type: string
          example: Alice Johnson
        createdAt:
          type: string
          format: date-time
```

## Anti-Patterns

### Don't: Use Verbs in REST URLs

```
❌ /api/v1/getUsers
❌ /api/v1/createOrder
❌ /api/v1/deleteProduct/123

✅ GET /api/v1/users
✅ POST /api/v1/orders
✅ DELETE /api/v1/products/123
```

### Don't: Return Different Structures for Same Resource

```
❌ GET /users -> {id, name}
❌ POST /users -> {userId, fullName}

✅ Consistent schema across all operations
```

### Don't: Ignore HTTP Status Codes

```
❌ Always return 200 with error in body

✅ Use appropriate status codes
```

### Don't: Expose Internal Implementation

```
❌ /api/v1/database-users
❌ /api/v1/mongodb/collections/users

✅ /api/v1/users (abstract implementation)
```

## References

### Standards & Guidelines

- **Google Cloud API Design Guide**: https://cloud.google.com/apis/design
- **Microsoft REST API Guidelines**: https://github.com/microsoft/api-guidelines
- **AWS API Gateway Best Practices**: https://docs.aws.amazon.com/apigateway/
- **RFC 7807 Problem Details**: https://tools.ietf.org/html/rfc7807
- **OpenAPI Specification**: https://spec.openapis.org/oas/latest.html
- **GraphQL Best Practices**: https://graphql.org/learn/best-practices/
- **gRPC Style Guide**: https://grpc.io/docs/guides/

### Tools

- **Swagger/OpenAPI**: https://swagger.io/
- **Postman**: https://www.postman.com/
- **Apollo GraphQL**: https://www.apollographql.com/
- **Buf (Protocol Buffers)**: https://buf.build/
- **Stoplight**: https://stoplight.io/
- **API Blueprint**: https://apiblueprint.org/

### Books

- "REST API Design Rulebook" - Mark Masse
- "Designing Web APIs" - Brenda Jin, Saurabh Sahni, Amir Shevat
- "API Design Patterns" - JJ Geewax (Google)
