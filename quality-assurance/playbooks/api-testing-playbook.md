# API Testing Playbook

**Comprehensive guide for testing REST, GraphQL, and gRPC APIs**

---

## Table of Contents

1. [API Testing Strategy](#api-testing-strategy)
2. [REST API Testing](#rest-api-testing)
3. [GraphQL API Testing](#graphql-api-testing)
4. [gRPC API Testing](#grpc-api-testing)
5. [API Test Automation](#api-test-automation)
6. [API Performance Testing](#api-performance-testing)
7. [API Security Testing](#api-security-testing)
8. [Contract Testing](#contract-testing)
9. [API Mocking & Stubbing](#api-mocking--stubbing)
10. [API Monitoring](#api-monitoring)

---

## API Testing Strategy

### Why API Testing?

**Benefits**:
- **Fast**: No UI rendering, pure business logic testing
- **Stable**: Less brittle than UI tests
- **Early**: Test backend before UI is ready
- **Comprehensive**: Test all scenarios including edge cases
- **Efficient**: More coverage with fewer tests

**Testing Pyramid for APIs**:
```
     /\
    /E2E\         ← 5% - Full system integration
   /------\
  /  API   \      ← 70% - API integration & contract tests
 /----------\
/ UNIT TESTS \    ← 25% - Service logic, handlers
---------------
```

### API Test Levels

**1. Unit Tests** - Individual functions/handlers
```typescript
// Example: Testing a user service function
describe('UserService', () => {
  test('createUser validates email format', async () => {
    const userService = new UserService(mockDb);

    await expect(
      userService.createUser({ email: 'invalid-email', name: 'Test' })
    ).rejects.toThrow('Invalid email format');
  });

  test('createUser hashes password', async () => {
    const userService = new UserService(mockDb);
    const user = await userService.createUser({
      email: 'test@example.com',
      password: 'plaintext123'
    });

    expect(user.password).not.toBe('plaintext123');
    expect(user.password).toMatch(/^\$2[aby]\$/); // bcrypt hash
  });
});
```

**2. Integration Tests** - API endpoints with dependencies
```typescript
// Example: Testing API endpoint with database
describe('POST /api/users', () => {
  beforeEach(async () => {
    await db.clean(['users']);
  });

  test('creates user successfully', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'test@example.com',
        name: 'Test User',
        password: 'SecurePass123!'
      })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'test@example.com',
      name: 'Test User'
    });
    expect(response.body.password).toBeUndefined(); // Never return password

    // Verify in database
    const user = await db.users.findOne({ email: 'test@example.com' });
    expect(user).toBeDefined();
  });
});
```

**3. Contract Tests** - API consumer/provider contracts
```typescript
// Example: Pact contract test
import { PactV3, MatchersV3 } from '@pact-foundation/pact';

describe('User API Contract', () => {
  const provider = new PactV3({
    consumer: 'frontend-app',
    provider: 'user-service'
  });

  test('get user by ID', async () => {
    provider
      .given('user with ID 123 exists')
      .uponReceiving('a request for user 123')
      .withRequest({
        method: 'GET',
        path: '/api/users/123',
        headers: {
          'Authorization': MatchersV3.regex(/^Bearer .+/, 'Bearer token')
        }
      })
      .willRespondWith({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: MatchersV3.integer(123),
          email: MatchersV3.email(),
          name: MatchersV3.string(),
          createdAt: MatchersV3.iso8601DateTime()
        }
      });

    await provider.executeTest(async (mockService) => {
      const client = new UserClient(mockService.url);
      const user = await client.getUser(123);
      expect(user.id).toBe(123);
    });
  });
});
```

**4. End-to-End Tests** - Full user flows across services
```typescript
// Example: E2E user registration and order flow
describe('User Registration and Order Flow', () => {
  test('complete user journey', async () => {
    // 1. Register user
    const registerRes = await request(app)
      .post('/api/auth/register')
      .send({ email: 'user@example.com', password: 'Pass123!' })
      .expect(201);

    const { token } = registerRes.body;

    // 2. Create product (as admin)
    const productRes = await request(app)
      .post('/api/products')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ name: 'Widget', price: 29.99 })
      .expect(201);

    // 3. Add to cart
    await request(app)
      .post('/api/cart')
      .set('Authorization', `Bearer ${token}`)
      .send({ productId: productRes.body.id, quantity: 2 })
      .expect(200);

    // 4. Checkout
    const orderRes = await request(app)
      .post('/api/orders')
      .set('Authorization', `Bearer ${token}`)
      .send({ paymentMethod: 'card' })
      .expect(201);

    expect(orderRes.body).toMatchObject({
      id: expect.any(String),
      totalAmount: 59.98,
      status: 'pending'
    });
  });
});
```

---

## REST API Testing

### Complete REST API Test Suite

**Testing Checklist for Each Endpoint**:

#### HTTP Methods
- [ ] **GET** - Retrieve resources
- [ ] **POST** - Create resources
- [ ] **PUT** - Update entire resource
- [ ] **PATCH** - Partial update
- [ ] **DELETE** - Remove resource
- [ ] **HEAD** - Get headers only
- [ ] **OPTIONS** - Get allowed methods

#### Status Codes
- [ ] **200 OK** - Successful GET, PUT, PATCH
- [ ] **201 Created** - Successful POST
- [ ] **204 No Content** - Successful DELETE
- [ ] **400 Bad Request** - Invalid input
- [ ] **401 Unauthorized** - No/invalid auth
- [ ] **403 Forbidden** - Insufficient permissions
- [ ] **404 Not Found** - Resource doesn't exist
- [ ] **409 Conflict** - Resource conflict
- [ ] **422 Unprocessable Entity** - Validation error
- [ ] **429 Too Many Requests** - Rate limit
- [ ] **500 Internal Server Error** - Server error
- [ ] **503 Service Unavailable** - Service down

#### Headers
- [ ] **Content-Type** - application/json, multipart/form-data
- [ ] **Authorization** - Bearer token, Basic, API key
- [ ] **Accept** - Content negotiation
- [ ] **Cache-Control** - Caching directives
- [ ] **ETag** - Resource versioning
- [ ] **Rate-Limit-*** - Rate limiting info
- [ ] **CORS** - Cross-origin headers

### Complete Test Implementation

```typescript
// Complete REST API test suite for User endpoints
import request from 'supertest';
import { app } from '../src/app';
import { db } from '../src/database';
import { generateToken } from '../src/auth';

describe('User API - /api/users', () => {
  let authToken: string;
  let testUserId: string;

  beforeAll(async () => {
    // Setup: Create admin user for authenticated requests
    const admin = await db.users.create({
      email: 'admin@example.com',
      role: 'admin'
    });
    authToken = generateToken(admin);
  });

  afterAll(async () => {
    await db.close();
  });

  beforeEach(async () => {
    await db.clean(['users']);
  });

  // ==================== CREATE (POST) ====================

  describe('POST /api/users', () => {
    const validUserData = {
      email: 'test@example.com',
      name: 'Test User',
      password: 'SecurePass123!',
      age: 25
    };

    // ===== Success Cases =====

    test('creates user with valid data', async () => {
      const response = await request(app)
        .post('/api/users')
        .send(validUserData)
        .expect('Content-Type', /json/)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: validUserData.email,
        name: validUserData.name,
        age: validUserData.age,
        createdAt: expect.any(String),
        updatedAt: expect.any(String)
      });

      // Password should never be returned
      expect(response.body.password).toBeUndefined();

      // Verify Location header
      expect(response.headers.location).toBe(`/api/users/${response.body.id}`);

      testUserId = response.body.id;
    });

    test('creates user with optional fields omitted', async () => {
      const minimalData = {
        email: 'minimal@example.com',
        password: 'Pass123!'
      };

      const response = await request(app)
        .post('/api/users')
        .send(minimalData)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: minimalData.email,
        name: null,
        age: null
      });
    });

    // ===== Validation Errors (400) =====

    test('returns 400 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ ...validUserData, email: 'invalid-email' })
        .expect(400);

      expect(response.body).toMatchObject({
        error: 'Validation Error',
        details: expect.arrayContaining([
          expect.objectContaining({
            field: 'email',
            message: expect.stringContaining('valid email')
          })
        ])
      });
    });

    test('returns 400 for weak password', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ ...validUserData, password: '123' })
        .expect(400);

      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'password',
            message: expect.stringMatching(/at least 8 characters/i)
          })
        ])
      );
    });

    test('returns 400 for missing required fields', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ name: 'Test' }) // Missing email and password
        .expect(400);

      expect(response.body.details).toHaveLength(2);
      expect(response.body.details.map(d => d.field)).toEqual(
        expect.arrayContaining(['email', 'password'])
      );
    });

    test('returns 400 for invalid age (negative)', async () => {
      await request(app)
        .post('/api/users')
        .send({ ...validUserData, age: -5 })
        .expect(400);
    });

    test('returns 400 for invalid age (too high)', async () => {
      await request(app)
        .post('/api/users')
        .send({ ...validUserData, age: 200 })
        .expect(400);
    });

    test('returns 400 for invalid data types', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ ...validUserData, age: 'twenty-five' })
        .expect(400);

      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'age',
            message: expect.stringMatching(/must be a number/i)
          })
        ])
      );
    });

    // ===== Conflict Errors (409) =====

    test('returns 409 for duplicate email', async () => {
      // Create first user
      await request(app)
        .post('/api/users')
        .send(validUserData)
        .expect(201);

      // Try to create duplicate
      const response = await request(app)
        .post('/api/users')
        .send(validUserData)
        .expect(409);

      expect(response.body).toMatchObject({
        error: 'Conflict',
        message: expect.stringMatching(/email already exists/i)
      });
    });

    // ===== Authentication Tests =====

    test('creates user without authentication (public endpoint)', async () => {
      // No Authorization header
      await request(app)
        .post('/api/users')
        .send(validUserData)
        .expect(201);
    });

    // ===== Content Type Tests =====

    test('accepts application/json', async () => {
      await request(app)
        .post('/api/users')
        .set('Content-Type', 'application/json')
        .send(validUserData)
        .expect(201);
    });

    test('rejects invalid content type', async () => {
      await request(app)
        .post('/api/users')
        .set('Content-Type', 'text/plain')
        .send(JSON.stringify(validUserData))
        .expect(415); // Unsupported Media Type
    });

    // ===== SQL Injection Tests =====

    test('prevents SQL injection in email field', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          ...validUserData,
          email: "admin'--@example.com"
        })
        .expect(400);

      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'email',
            message: expect.stringMatching(/valid email/i)
          })
        ])
      );
    });

    test('prevents SQL injection in name field', async () => {
      // Should be sanitized/escaped, not cause error
      const response = await request(app)
        .post('/api/users')
        .send({
          ...validUserData,
          name: "'; DROP TABLE users; --"
        })
        .expect(201);

      // Name should be escaped/sanitized
      expect(response.body.name).toBe("'; DROP TABLE users; --");

      // Verify users table still exists
      const users = await db.users.findAll();
      expect(users).toBeDefined();
    });

    // ===== XSS Prevention Tests =====

    test('sanitizes HTML in name field', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          ...validUserData,
          name: '<script>alert("XSS")</script>'
        })
        .expect(201);

      // Should be escaped or stripped
      expect(response.body.name).not.toContain('<script>');
    });

    // ===== Rate Limiting Tests =====

    test('enforces rate limiting', async () => {
      // Make multiple requests rapidly
      const requests = Array(100).fill(null).map((_, i) =>
        request(app)
          .post('/api/users')
          .send({ ...validUserData, email: `user${i}@example.com` })
      );

      const responses = await Promise.all(requests);

      // Some should be rate limited
      const rateLimited = responses.filter(r => r.status === 429);
      expect(rateLimited.length).toBeGreaterThan(0);

      // Check rate limit headers
      const rateLimitedResponse = rateLimited[0];
      expect(rateLimitedResponse.headers).toMatchObject({
        'x-ratelimit-limit': expect.any(String),
        'x-ratelimit-remaining': '0',
        'x-ratelimit-reset': expect.any(String)
      });
    });
  });

  // ==================== READ (GET) ====================

  describe('GET /api/users', () => {
    beforeEach(async () => {
      // Create test users
      await db.users.bulkCreate([
        { email: 'user1@example.com', name: 'User 1', age: 25 },
        { email: 'user2@example.com', name: 'User 2', age: 30 },
        { email: 'user3@example.com', name: 'User 3', age: 35 }
      ]);
    });

    // ===== Success Cases =====

    test('returns all users', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveLength(3);
      expect(response.body[0]).toMatchObject({
        id: expect.any(String),
        email: expect.any(String),
        name: expect.any(String)
      });
    });

    test('returns empty array when no users', async () => {
      await db.clean(['users']);

      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toEqual([]);
    });

    // ===== Pagination =====

    test('supports pagination with limit and offset', async () => {
      const response = await request(app)
        .get('/api/users?limit=2&offset=1')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.data).toHaveLength(2);
      expect(response.body.pagination).toMatchObject({
        limit: 2,
        offset: 1,
        total: 3
      });
    });

    test('supports page-based pagination', async () => {
      const response = await request(app)
        .get('/api/users?page=2&perPage=2')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.data).toHaveLength(1);
      expect(response.body.pagination).toMatchObject({
        page: 2,
        perPage: 2,
        totalPages: 2,
        total: 3
      });
    });

    // ===== Filtering =====

    test('filters by age range', async () => {
      const response = await request(app)
        .get('/api/users?minAge=28&maxAge=32')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveLength(1);
      expect(response.body[0].age).toBe(30);
    });

    test('filters by email pattern', async () => {
      const response = await request(app)
        .get('/api/users?email=user1')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveLength(1);
      expect(response.body[0].email).toBe('user1@example.com');
    });

    // ===== Sorting =====

    test('sorts by age ascending', async () => {
      const response = await request(app)
        .get('/api/users?sortBy=age&order=asc')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      const ages = response.body.map(u => u.age);
      expect(ages).toEqual([25, 30, 35]);
    });

    test('sorts by age descending', async () => {
      const response = await request(app)
        .get('/api/users?sortBy=age&order=desc')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      const ages = response.body.map(u => u.age);
      expect(ages).toEqual([35, 30, 25]);
    });

    // ===== Field Selection =====

    test('supports field selection', async () => {
      const response = await request(app)
        .get('/api/users?fields=id,email')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body[0]).toHaveProperty('id');
      expect(response.body[0]).toHaveProperty('email');
      expect(response.body[0]).not.toHaveProperty('name');
      expect(response.body[0]).not.toHaveProperty('age');
    });

    // ===== Authentication Tests =====

    test('requires authentication', async () => {
      await request(app)
        .get('/api/users')
        .expect(401);
    });

    test('rejects invalid token', async () => {
      await request(app)
        .get('/api/users')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
    });

    // ===== Caching Tests =====

    test('returns ETag header', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.headers.etag).toBeDefined();
    });

    test('returns 304 Not Modified with matching ETag', async () => {
      const firstResponse = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      const etag = firstResponse.headers.etag;

      const secondResponse = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .set('If-None-Match', etag)
        .expect(304);

      expect(secondResponse.body).toEqual({});
    });

    // ===== Performance Tests =====

    test('responds within acceptable time', async () => {
      const start = Date.now();

      await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      const duration = Date.now() - start;
      expect(duration).toBeLessThan(100); // < 100ms
    });
  });

  // ==================== READ SINGLE (GET by ID) ====================

  describe('GET /api/users/:id', () => {
    let userId: string;

    beforeEach(async () => {
      const user = await db.users.create({
        email: 'test@example.com',
        name: 'Test User',
        age: 25
      });
      userId = user.id;
    });

    // ===== Success Cases =====

    test('returns user by ID', async () => {
      const response = await request(app)
        .get(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toMatchObject({
        id: userId,
        email: 'test@example.com',
        name: 'Test User',
        age: 25
      });
    });

    // ===== Not Found (404) =====

    test('returns 404 for non-existent user', async () => {
      const response = await request(app)
        .get('/api/users/99999999-9999-9999-9999-999999999999')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);

      expect(response.body).toMatchObject({
        error: 'Not Found',
        message: expect.stringMatching(/user not found/i)
      });
    });

    test('returns 404 for deleted user', async () => {
      await db.users.delete(userId);

      await request(app)
        .get(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });

    // ===== Validation Errors (400) =====

    test('returns 400 for invalid ID format', async () => {
      await request(app)
        .get('/api/users/invalid-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(400);
    });

    // ===== Authorization Tests =====

    test('allows users to get their own profile', async () => {
      const userToken = generateToken({ id: userId, role: 'user' });

      await request(app)
        .get(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(200);
    });

    test('prevents users from accessing other profiles', async () => {
      const otherUser = await db.users.create({
        email: 'other@example.com'
      });
      const userToken = generateToken({ id: userId, role: 'user' });

      await request(app)
        .get(`/api/users/${otherUser.id}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });
  });

  // ==================== UPDATE (PUT) ====================

  describe('PUT /api/users/:id', () => {
    let userId: string;

    beforeEach(async () => {
      const user = await db.users.create({
        email: 'test@example.com',
        name: 'Test User',
        age: 25
      });
      userId = user.id;
    });

    // ===== Success Cases =====

    test('updates user completely', async () => {
      const updatedData = {
        email: 'updated@example.com',
        name: 'Updated User',
        age: 30
      };

      const response = await request(app)
        .put(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(updatedData)
        .expect(200);

      expect(response.body).toMatchObject({
        id: userId,
        ...updatedData,
        updatedAt: expect.any(String)
      });

      // Verify in database
      const user = await db.users.findById(userId);
      expect(user).toMatchObject(updatedData);
    });

    // ===== Validation Errors =====

    test('returns 400 for invalid email', async () => {
      await request(app)
        .put(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ email: 'invalid', name: 'Test', age: 25 })
        .expect(400);
    });

    // ===== Not Found (404) =====

    test('returns 404 for non-existent user', async () => {
      await request(app)
        .put('/api/users/99999999-9999-9999-9999-999999999999')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ email: 'test@example.com', name: 'Test', age: 25 })
        .expect(404);
    });

    // ===== Idempotency Test =====

    test('is idempotent (multiple requests produce same result)', async () => {
      const updateData = {
        email: 'updated@example.com',
        name: 'Updated',
        age: 30
      };

      // First update
      const response1 = await request(app)
        .put(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(updateData)
        .expect(200);

      // Second identical update
      const response2 = await request(app)
        .put(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(updateData)
        .expect(200);

      // Both should return same data (except updatedAt might differ)
      expect(response1.body.email).toBe(response2.body.email);
      expect(response1.body.name).toBe(response2.body.name);
      expect(response1.body.age).toBe(response2.body.age);
    });
  });

  // ==================== PARTIAL UPDATE (PATCH) ====================

  describe('PATCH /api/users/:id', () => {
    let userId: string;

    beforeEach(async () => {
      const user = await db.users.create({
        email: 'test@example.com',
        name: 'Test User',
        age: 25
      });
      userId = user.id;
    });

    // ===== Success Cases =====

    test('updates only specified fields', async () => {
      const response = await request(app)
        .patch(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Updated Name' })
        .expect(200);

      expect(response.body).toMatchObject({
        id: userId,
        email: 'test@example.com', // Unchanged
        name: 'Updated Name',       // Changed
        age: 25                      // Unchanged
      });
    });

    test('updates multiple fields', async () => {
      const response = await request(app)
        .patch(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'New Name', age: 30 })
        .expect(200);

      expect(response.body).toMatchObject({
        name: 'New Name',
        age: 30
      });
    });

    test('allows empty patch (no changes)', async () => {
      const response = await request(app)
        .patch(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({})
        .expect(200);

      expect(response.body).toMatchObject({
        id: userId,
        email: 'test@example.com',
        name: 'Test User',
        age: 25
      });
    });

    // ===== Validation Errors =====

    test('returns 400 for invalid partial update', async () => {
      await request(app)
        .patch(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ age: -10 })
        .expect(400);
    });

    // ===== Optimistic Locking =====

    test('supports optimistic locking with version', async () => {
      const user = await db.users.findById(userId);
      const currentVersion = user.version;

      // Update with correct version
      await request(app)
        .patch(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Updated', version: currentVersion })
        .expect(200);

      // Try to update with old version
      await request(app)
        .patch(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Conflict', version: currentVersion })
        .expect(409); // Conflict - version mismatch
    });
  });

  // ==================== DELETE ====================

  describe('DELETE /api/users/:id', () => {
    let userId: string;

    beforeEach(async () => {
      const user = await db.users.create({
        email: 'test@example.com',
        name: 'Test User'
      });
      userId = user.id;
    });

    // ===== Success Cases =====

    test('deletes user successfully', async () => {
      await request(app)
        .delete(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(204);

      // Verify user is deleted
      const user = await db.users.findById(userId);
      expect(user).toBeNull();
    });

    test('performs soft delete (marks as deleted)', async () => {
      await request(app)
        .delete(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(204);

      // Verify user is soft deleted
      const user = await db.users.findByIdIncludingDeleted(userId);
      expect(user.deletedAt).toBeDefined();
      expect(user.deletedAt).toBeInstanceOf(Date);
    });

    // ===== Not Found (404) =====

    test('returns 404 for non-existent user', async () => {
      await request(app)
        .delete('/api/users/99999999-9999-9999-9999-999999999999')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });

    // ===== Idempotency Test =====

    test('is idempotent (deleting twice returns 404 second time)', async () => {
      // First delete
      await request(app)
        .delete(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(204);

      // Second delete
      await request(app)
        .delete(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });

    // ===== Cascade Delete Test =====

    test('cascades delete to related entities', async () => {
      // Create related data
      await db.orders.create({ userId, amount: 100 });
      await db.posts.create({ userId, title: 'Test Post' });

      // Delete user
      await request(app)
        .delete(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(204);

      // Verify related data is also deleted
      const orders = await db.orders.findByUserId(userId);
      const posts = await db.posts.findByUserId(userId);

      expect(orders).toHaveLength(0);
      expect(posts).toHaveLength(0);
    });

    // ===== Authorization Tests =====

    test('allows user to delete their own account', async () => {
      const userToken = generateToken({ id: userId, role: 'user' });

      await request(app)
        .delete(`/api/users/${userId}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(204);
    });

    test('prevents users from deleting other accounts', async () => {
      const otherUser = await db.users.create({ email: 'other@example.com' });
      const userToken = generateToken({ id: userId, role: 'user' });

      await request(app)
        .delete(`/api/users/${otherUser.id}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(403);
    });
  });

  // ==================== ERROR HANDLING ====================

  describe('Error Handling', () => {
    test('handles database connection errors', async () => {
      // Simulate database error
      jest.spyOn(db.users, 'findAll').mockRejectedValueOnce(
        new Error('Database connection failed')
      );

      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(500);

      expect(response.body).toMatchObject({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred'
      });

      // Error should be logged but details not exposed
      expect(response.body.message).not.toContain('Database connection');
    });

    test('handles malformed JSON', async () => {
      const response = await request(app)
        .post('/api/users')
        .set('Content-Type', 'application/json')
        .send('{ invalid json }')
        .expect(400);

      expect(response.body).toMatchObject({
        error: 'Bad Request',
        message: expect.stringMatching(/invalid json/i)
      });
    });

    test('handles unexpected errors gracefully', async () => {
      // Simulate unexpected error in handler
      jest.spyOn(db.users, 'create').mockImplementationOnce(() => {
        throw new Error('Unexpected error');
      });

      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'test@example.com',
          password: 'Pass123!'
        })
        .expect(500);

      expect(response.body.error).toBe('Internal Server Error');
    });
  });

  // ==================== SECURITY TESTS ====================

  describe('Security', () => {
    test('prevents NoSQL injection', async () => {
      const response = await request(app)
        .get('/api/users')
        .query({ email: { $ne: null } }) // NoSQL injection attempt
        .set('Authorization', `Bearer ${authToken}`)
        .expect(400);

      expect(response.body.message).toMatch(/invalid query/i);
    });

    test('sanitizes output to prevent XSS', async () => {
      const xssPayload = '<script>alert("XSS")</script>';

      const createRes = await request(app)
        .post('/api/users')
        .send({
          email: 'test@example.com',
          name: xssPayload,
          password: 'Pass123!'
        })
        .expect(201);

      // Response should be escaped/sanitized
      expect(createRes.body.name).not.toContain('<script>');

      // Get request should also return sanitized data
      const getRes = await request(app)
        .get(`/api/users/${createRes.body.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(getRes.body.name).not.toContain('<script>');
    });

    test('enforces HTTPS in production', async () => {
      process.env.NODE_ENV = 'production';

      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .set('X-Forwarded-Proto', 'http'); // HTTP request

      // Should redirect to HTTPS or reject
      expect([301, 302, 403]).toContain(response.status);

      process.env.NODE_ENV = 'test';
    });

    test('sets security headers', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.headers).toMatchObject({
        'x-content-type-options': 'nosniff',
        'x-frame-options': 'DENY',
        'x-xss-protection': '1; mode=block',
        'strict-transport-security': expect.any(String)
      });
    });

    test('prevents timing attacks on authentication', async () => {
      const start1 = Date.now();
      await request(app)
        .post('/api/auth/login')
        .send({ email: 'exists@example.com', password: 'wrong' })
        .expect(401);
      const time1 = Date.now() - start1;

      const start2 = Date.now();
      await request(app)
        .post('/api/auth/login')
        .send({ email: 'nonexistent@example.com', password: 'wrong' })
        .expect(401);
      const time2 = Date.now() - start2;

      // Times should be similar (within 50ms) to prevent user enumeration
      expect(Math.abs(time1 - time2)).toBeLessThan(50);
    });
  });

  // ==================== PERFORMANCE TESTS ====================

  describe('Performance', () => {
    test('handles bulk operations efficiently', async () => {
      const users = Array(100).fill(null).map((_, i) => ({
        email: `user${i}@example.com`,
        password: 'Pass123!',
        name: `User ${i}`
      }));

      const start = Date.now();

      await request(app)
        .post('/api/users/bulk')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ users })
        .expect(201);

      const duration = Date.now() - start;

      // Should complete in reasonable time
      expect(duration).toBeLessThan(5000); // < 5 seconds for 100 users
    });

    test('supports efficient pagination for large datasets', async () => {
      // Create 1000 users
      await db.users.bulkCreate(
        Array(1000).fill(null).map((_, i) => ({
          email: `user${i}@example.com`,
          name: `User ${i}`
        }))
      );

      const start = Date.now();

      const response = await request(app)
        .get('/api/users?page=50&perPage=20')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      const duration = Date.now() - start;

      expect(response.body.data).toHaveLength(20);
      expect(duration).toBeLessThan(100); // < 100ms even with 1000 records
    });

    test('uses database indexes efficiently', async () => {
      // Create many users
      await db.users.bulkCreate(
        Array(1000).fill(null).map((_, i) => ({
          email: `user${i}@example.com`,
          name: `User ${i}`
        }))
      );

      const start = Date.now();

      // Query by indexed field (email)
      await request(app)
        .get('/api/users?email=user500@example.com')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      const duration = Date.now() - start;

      // Should be fast due to index
      expect(duration).toBeLessThan(50); // < 50ms
    });
  });
});
```

---

## GraphQL API Testing

### GraphQL Testing Fundamentals

```typescript
import { ApolloServer } from '@apollo/server';
import { createTestClient } from 'apollo-server-testing';

describe('GraphQL API', () => {
  let testClient;

  beforeAll(() => {
    const server = new ApolloServer({
      typeDefs,
      resolvers,
      context: () => ({ db, user: mockUser })
    });

    testClient = createTestClient(server);
  });

  describe('Queries', () => {
    test('user query returns user by ID', async () => {
      const GET_USER = gql`
        query GetUser($id: ID!) {
          user(id: $id) {
            id
            email
            name
            posts {
              id
              title
            }
          }
        }
      `;

      const { data, errors } = await testClient.query({
        query: GET_USER,
        variables: { id: '123' }
      });

      expect(errors).toBeUndefined();
      expect(data.user).toMatchObject({
        id: '123',
        email: expect.any(String),
        name: expect.any(String),
        posts: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            title: expect.any(String)
          })
        ])
      });
    });

    test('handles query with fragments', async () => {
      const GET_USERS = gql`
        fragment UserFields on User {
          id
          email
          name
        }

        query GetUsers {
          users {
            ...UserFields
            posts {
              id
              title
            }
          }
        }
      `;

      const { data } = await testClient.query({
        query: GET_USERS
      });

      expect(data.users).toBeInstanceOf(Array);
      expect(data.users[0]).toHaveProperty('id');
      expect(data.users[0]).toHaveProperty('email');
      expect(data.users[0]).toHaveProperty('posts');
    });

    test('handles nested queries efficiently (N+1 problem)', async () => {
      const GET_USERS_WITH_POSTS = gql`
        query GetUsersWithPosts {
          users {
            id
            posts {
              id
              comments {
                id
                author {
                  id
                }
              }
            }
          }
        }
      `;

      // Spy on database queries
      const dbSpy = jest.spyOn(db, 'query');

      await testClient.query({
        query: GET_USERS_WITH_POSTS
      });

      // With DataLoader, should use batching/caching
      // Should not be O(n) queries for nested data
      const queryCount = dbSpy.mock.calls.length;
      expect(queryCount).toBeLessThan(10); // Efficient batching

      dbSpy.mockRestore();
    });
  });

  describe('Mutations', () => {
    test('creates user successfully', async () => {
      const CREATE_USER = gql`
        mutation CreateUser($input: CreateUserInput!) {
          createUser(input: $input) {
            user {
              id
              email
              name
            }
            errors {
              field
              message
            }
          }
        }
      `;

      const { data } = await testClient.mutate({
        mutation: CREATE_USER,
        variables: {
          input: {
            email: 'test@example.com',
            name: 'Test User',
            password: 'SecurePass123!'
          }
        }
      });

      expect(data.createUser.user).toMatchObject({
        id: expect.any(String),
        email: 'test@example.com',
        name: 'Test User'
      });
      expect(data.createUser.errors).toHaveLength(0);
    });

    test('returns validation errors', async () => {
      const CREATE_USER = gql`
        mutation CreateUser($input: CreateUserInput!) {
          createUser(input: $input) {
            user {
              id
            }
            errors {
              field
              message
            }
          }
        }
      `;

      const { data } = await testClient.mutate({
        mutation: CREATE_USER,
        variables: {
          input: {
            email: 'invalid-email',
            password: '123'
          }
        }
      });

      expect(data.createUser.user).toBeNull();
      expect(data.createUser.errors).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'email',
            message: expect.stringMatching(/valid email/i)
          }),
          expect.objectContaining({
            field: 'password',
            message: expect.stringMatching(/at least 8 characters/i)
          })
        ])
      );
    });
  });

  describe('Subscriptions', () => {
    test('subscribes to user updates', async () => {
      const USER_UPDATED = gql`
        subscription OnUserUpdated($userId: ID!) {
          userUpdated(userId: $userId) {
            id
            name
            email
          }
        }
      `;

      const subscription = testClient.subscribe({
        query: USER_UPDATED,
        variables: { userId: '123' }
      });

      // Trigger update
      await updateUser('123', { name: 'Updated Name' });

      // Wait for subscription event
      const { data } = await subscription.next();

      expect(data.userUpdated).toMatchObject({
        id: '123',
        name: 'Updated Name'
      });
    });
  });

  describe('Error Handling', () => {
    test('handles GraphQL errors', async () => {
      const INVALID_QUERY = gql`
        query {
          nonExistentField
        }
      `;

      const { errors } = await testClient.query({
        query: INVALID_QUERY
      });

      expect(errors).toHaveLength(1);
      expect(errors[0].message).toMatch(/nonExistentField/i);
    });

    test('handles resolver errors', async () => {
      const GET_USER = gql`
        query GetUser($id: ID!) {
          user(id: $id) {
            id
          }
        }
      `;

      const { errors } = await testClient.query({
        query: GET_USER,
        variables: { id: 'non-existent' }
      });

      expect(errors).toHaveLength(1);
      expect(errors[0].extensions.code).toBe('NOT_FOUND');
    });
  });

  describe('Authorization', () => {
    test('requires authentication for protected fields', async () => {
      const serverWithoutAuth = new ApolloServer({
        typeDefs,
        resolvers,
        context: () => ({ db, user: null }) // No authenticated user
      });

      const unauthClient = createTestClient(serverWithoutAuth);

      const GET_USER_EMAIL = gql`
        query {
          me {
            email
          }
        }
      `;

      const { errors } = await unauthClient.query({
        query: GET_USER_EMAIL
      });

      expect(errors).toHaveLength(1);
      expect(errors[0].extensions.code).toBe('UNAUTHENTICATED');
    });
  });
});
```

---

## API Performance Testing

### Load Testing REST APIs with K6

```javascript
// load-test-api.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const authDuration = new Trend('auth_duration');
const createUserDuration = new Trend('create_user_duration');
const getUserDuration = new Trend('get_user_duration');

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{type:auth}': ['p(95)<200'],
    'http_req_duration{type:read}': ['p(95)<300'],
    'http_req_duration{type:write}': ['p(95)<500'],
    errors: ['rate<0.01'],
    checks: ['rate>0.95']
  }
};

const BASE_URL = __ENV.API_URL || 'https://api.example.com';

export function setup() {
  // Create admin token for test
  const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: 'admin@example.com',
    password: 'admin123'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });

  const { token } = JSON.parse(loginRes.body);
  return { adminToken: token };
}

export default function(data) {
  // 1. Authenticate user
  const authStart = Date.now();
  const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: `user-${__VU}-${__ITER}@example.com`,
    password: 'password123'
  }), {
    headers: { 'Content-Type': 'application/json' },
    tags: { type: 'auth' }
  });

  const authCheck = check(loginRes, {
    'login status is 200 or 201': (r) => [200, 201].includes(r.status),
    'login returns token': (r) => JSON.parse(r.body).token !== undefined
  });

  if (!authCheck) {
    errorRate.add(1);
    return;
  }

  authDuration.add(Date.now() - authStart);
  const { token } = JSON.parse(loginRes.body);

  sleep(1);

  // 2. Create resource
  const createStart = Date.now();
  const createRes = http.post(`${BASE_URL}/api/users`, JSON.stringify({
    email: `newuser-${__VU}-${__ITER}@example.com`,
    name: `User ${__VU}`,
    age: 25
  }), {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    tags: { type: 'write' }
  });

  check(createRes, {
    'create status is 201': (r) => r.status === 201,
    'create returns user': (r) => JSON.parse(r.body).id !== undefined
  }) || errorRate.add(1);

  createUserDuration.add(Date.now() - createStart);

  if (createRes.status !== 201) {
    return;
  }

  const { id: userId } = JSON.parse(createRes.body);

  sleep(1);

  // 3. Read resource
  const getStart = Date.now();
  const getRes = http.get(`${BASE_URL}/api/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` },
    tags: { type: 'read' }
  });

  check(getRes, {
    'get status is 200': (r) => r.status === 200,
    'get returns correct user': (r) => JSON.parse(r.body).id === userId
  }) || errorRate.add(1);

  getUserDuration.add(Date.now() - getStart);

  sleep(1);

  // 4. List resources with pagination
  const listRes = http.get(`${BASE_URL}/api/users?page=1&limit=20`, {
    headers: { 'Authorization': `Bearer ${token}` },
    tags: { type: 'read' }
  });

  check(listRes, {
    'list status is 200': (r) => r.status === 200,
    'list returns array': (r) => Array.isArray(JSON.parse(r.body).data)
  }) || errorRate.add(1);

  sleep(1);

  // 5. Update resource
  const updateRes = http.patch(`${BASE_URL}/api/users/${userId}`, JSON.stringify({
    name: `Updated User ${__VU}`
  }), {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    tags: { type: 'write' }
  });

  check(updateRes, {
    'update status is 200': (r) => r.status === 200,
    'update modifies name': (r) => JSON.parse(r.body).name.includes('Updated')
  }) || errorRate.add(1);

  sleep(1);

  // 6. Delete resource
  const deleteRes = http.del(`${BASE_URL}/api/users/${userId}`, null, {
    headers: { 'Authorization': `Bearer ${token}` },
    tags: { type: 'write' }
  });

  check(deleteRes, {
    'delete status is 204': (r) => r.status === 204
  }) || errorRate.add(1);

  sleep(Math.random() * 3 + 2); // Think time: 2-5 seconds
}

export function teardown(data) {
  // Cleanup if needed
  console.log('Test completed');
}
```

---

## API Security Testing

### OWASP API Security Top 10 Tests

```typescript
describe('API Security Tests', () => {
  // API1:2023 - Broken Object Level Authorization (BOLA)
  test('prevents accessing other users resources', async () => {
    const user1Token = await createUserAndGetToken('user1@example.com');
    const user2Token = await createUserAndGetToken('user2@example.com');

    // User 1 creates a resource
    const createRes = await request(app)
      .post('/api/orders')
      .set('Authorization', `Bearer ${user1Token}`)
      .send({ amount: 100 })
      .expect(201);

    const orderId = createRes.body.id;

    // User 2 tries to access User 1's resource
    await request(app)
      .get(`/api/orders/${orderId}`)
      .set('Authorization', `Bearer ${user2Token}`)
      .expect(403); // Should be forbidden

    // User 2 tries to modify User 1's resource
    await request(app)
      .patch(`/api/orders/${orderId}`)
      .set('Authorization', `Bearer ${user2Token}`)
      .send({ amount: 200 })
      .expect(403);

    // User 2 tries to delete User 1's resource
    await request(app)
      .delete(`/api/orders/${orderId}`)
      .set('Authorization', `Bearer ${user2Token}`)
      .expect(403);
  });

  // API2:2023 - Broken Authentication
  test('requires valid authentication', async () => {
    // No token
    await request(app)
      .get('/api/users/me')
      .expect(401);

    // Invalid token
    await request(app)
      .get('/api/users/me')
      .set('Authorization', 'Bearer invalid-token')
      .expect(401);

    // Expired token
    const expiredToken = generateToken({ id: '123' }, { expiresIn: '-1h' });
    await request(app)
      .get('/api/users/me')
      .set('Authorization', `Bearer ${expiredToken}`)
      .expect(401);
  });

  test('enforces password complexity', async () => {
    const weakPasswords = ['123', 'password', 'abc', 'test'];

    for (const weakPassword of weakPasswords) {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          email: `test${Math.random()}@example.com`,
          password: weakPassword
        })
        .expect(400);

      expect(response.body.details).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            field: 'password',
            message: expect.stringMatching(/weak|complexity|requirements/i)
          })
        ])
      );
    }
  });

  test('prevents brute force attacks with rate limiting', async () => {
    const attempts = Array(20).fill(null).map(() =>
      request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'wrong-password'
        })
    );

    const responses = await Promise.all(attempts);

    const rateLimited = responses.filter(r => r.status === 429);
    expect(rateLimited.length).toBeGreaterThan(0);
  });

  // API3:2023 - Broken Object Property Level Authorization
  test('filters sensitive fields based on user role', async () => {
    const userToken = await createUserAndGetToken('user@example.com');
    const adminToken = await createAdminAndGetToken('admin@example.com');

    // Regular user should not see sensitive fields
    const userRes = await request(app)
      .get('/api/users/123')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(200);

    expect(userRes.body).not.toHaveProperty('password');
    expect(userRes.body).not.toHaveProperty('passwordHash');
    expect(userRes.body).not.toHaveProperty('ssn');
    expect(userRes.body).not.toHaveProperty('creditCard');

    // Admin should see more fields but still not sensitive ones
    const adminRes = await request(app)
      .get('/api/users/123')
      .set('Authorization', `Bearer ${adminToken}`)
      .expect(200);

    expect(adminRes.body).toHaveProperty('email');
    expect(adminRes.body).toHaveProperty('lastLogin');
    expect(adminRes.body).not.toHaveProperty('password');
    expect(adminRes.body).not.toHaveProperty('ssn');
  });

  // API4:2023 - Unrestricted Resource Consumption
  test('limits request payload size', async () => {
    const largePayload = {
      data: 'x'.repeat(10 * 1024 * 1024) // 10MB
    };

    await request(app)
      .post('/api/data')
      .send(largePayload)
      .expect(413); // Payload Too Large
  });

  test('limits pagination size', async () => {
    const token = await createUserAndGetToken('user@example.com');

    const response = await request(app)
      .get('/api/users?limit=10000') // Trying to fetch too many
      .set('Authorization', `Bearer ${token}`)
      .expect(400);

    expect(response.body.message).toMatch(/limit.*maximum/i);
  });

  // API5:2023 - Broken Function Level Authorization
  test('prevents privilege escalation', async () => {
    const userToken = await createUserAndGetToken('user@example.com');

    // Regular user trying to access admin endpoint
    await request(app)
      .get('/api/admin/users')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(403);

    // Regular user trying to delete any user
    await request(app)
      .delete('/api/admin/users/123')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(403);

    // Regular user trying to modify system settings
    await request(app)
      .patch('/api/admin/settings')
      .set('Authorization', `Bearer ${userToken}`)
      .send({ maintenanceMode: true })
      .expect(403);
  });

  // API6:2023 - Unrestricted Access to Sensitive Business Flows
  test('prevents automated abuse of critical flows', async () => {
    const token = await createUserAndGetToken('user@example.com');

    // Try to create 100 orders rapidly (should be rate limited)
    const orderAttempts = Array(100).fill(null).map(() =>
      request(app)
        .post('/api/orders')
        .set('Authorization', `Bearer ${token}`)
        .send({ amount: 1 })
    );

    const responses = await Promise.all(orderAttempts);
    const rateLimited = responses.filter(r => r.status === 429);

    expect(rateLimited.length).toBeGreaterThan(0);
  });

  // API7:2023 - Server Side Request Forgery (SSRF)
  test('prevents SSRF attacks', async () => {
    const token = await createUserAndGetToken('user@example.com');

    const ssrfAttempts = [
      'http://localhost:8080/admin',
      'http://169.254.169.254/latest/meta-data/',
      'file:///etc/passwd'
    ];

    for (const url of ssrfAttempts) {
      await request(app)
        .post('/api/fetch-url')
        .set('Authorization', `Bearer ${token}`)
        .send({ url })
        .expect(400); // Should reject
    }
  });

  // API8:2023 - Security Misconfiguration
  test('hides sensitive error details in production', async () => {
    process.env.NODE_ENV = 'production';

    // Trigger database error
    jest.spyOn(db, 'users').mockImplementationOnce(() => {
      throw new Error('Database connection string: postgres://user:pass@localhost');
    });

    const response = await request(app)
      .get('/api/users')
      .set('Authorization', `Bearer ${await createUserAndGetToken('user@example.com')}`)
      .expect(500);

    // Should not expose internal details
    expect(response.body.message).not.toContain('postgres://');
    expect(response.body.message).not.toContain('user:pass');
    expect(response.body.message).toBe('An unexpected error occurred');

    process.env.NODE_ENV = 'test';
  });

  test('disables dangerous HTTP methods', async () => {
    await request(app)
      .trace('/api/users')
      .expect(405); // Method Not Allowed

    await request(app)
      .options('/api/users')
      .expect(200); // OPTIONS is safe (CORS preflight)
  });

  // API9:2023 - Improper Inventory Management
  test('does not expose API version in headers', async () => {
    const response = await request(app)
      .get('/api/users')
      .set('Authorization', `Bearer ${await createUserAndGetToken('user@example.com')}`);

    expect(response.headers['x-powered-by']).toBeUndefined();
    expect(response.headers['server']).not.toMatch(/express|node|version/i);
  });

  // API10:2023 - Unsafe Consumption of APIs
  test('validates external API responses', async () => {
    // Mock external API with malicious response
    nock('https://external-api.com')
      .get('/users/123')
      .reply(200, {
        id: '123',
        name: '<script>alert("XSS")</script>',
        bio: 'A'.repeat(10000000) // 10MB string
      });

    const token = await createUserAndGetToken('user@example.com');

    const response = await request(app)
      .get('/api/import-user/123')
      .set('Authorization', `Bearer ${token}`)
      .expect(400);

    expect(response.body.message).toMatch(/validation failed|invalid data/i);
  });
});
```

---

## Best Practices Summary

### API Testing Best Practices

1. **Test all HTTP methods** - GET, POST, PUT, PATCH, DELETE
2. **Test all status codes** - Success (2xx), Client Error (4xx), Server Error (5xx)
3. **Test authentication** - No auth, invalid auth, expired tokens
4. **Test authorization** - RBAC, resource ownership, privilege escalation
5. **Test validation** - Required fields, data types, constraints
6. **Test edge cases** - Empty data, null values, boundary values
7. **Test security** - SQL injection, XSS, SSRF, CSRF
8. **Test performance** - Response time, rate limiting, pagination
9. **Test idempotency** - PUT and DELETE should be idempotent
10. **Test error handling** - Graceful degradation, error messages

### API Testing Anti-Patterns

❌ **Don't test only happy path** - Test error cases too
❌ **Don't skip authentication tests** - Security is critical
❌ **Don't hardcode test data** - Use factories and fixtures
❌ **Don't ignore performance** - Load test your APIs
❌ **Don't test UI and API together** - Separate concerns
❌ **Don't commit secrets** - Use environment variables
❌ **Don't skip contract tests** - Prevent breaking changes
❌ **Don't ignore rate limits** - Test throttling behavior

---

**Playbook Version**: 1.0
**Last Updated**: 2025-11-19
**References**: REST API standards, GraphQL best practices, OWASP API Security Top 10
