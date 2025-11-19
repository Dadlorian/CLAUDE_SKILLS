# Test Case Design Guide

**Master guide for designing effective, comprehensive test cases**

---

## Table of Contents

1. [Test Case Fundamentals](#test-case-fundamentals)
2. [Test Design Techniques](#test-design-techniques)
3. [Black Box Testing Techniques](#black-box-testing-techniques)
4. [White Box Testing Techniques](#white-box-testing-techniques)
5. [Test Case Templates](#test-case-templates)
6. [Test Data Design](#test-data-design)
7. [Test Coverage Strategies](#test-coverage-strategies)
8. [Test Case Examples by Domain](#test-case-examples-by-domain)

---

## Test Case Fundamentals

### What Makes a Good Test Case?

**Characteristics of Effective Test Cases**:
- **Clear**: Unambiguous steps and expected results
- **Concise**: Short, focused on one scenario
- **Repeatable**: Same results every time
- **Independent**: Not dependent on other tests
- **Traceable**: Linked to requirements
- **Maintainable**: Easy to update
- **Valuable**: Tests important functionality

### Test Case Anatomy

```markdown
**Test Case ID**: TC-001
**Module**: User Authentication
**Feature**: Login
**Priority**: High
**Type**: Functional

**Objective**: Verify that users can login with valid credentials

**Preconditions**:
- User account exists with email: test@example.com
- User password is: ValidPass123!
- User is on login page

**Test Steps**:
1. Enter "test@example.com" in email field
2. Enter "ValidPass123!" in password field
3. Click "Login" button

**Expected Result**:
- User is redirected to dashboard
- Welcome message displays "Welcome back, Test User"
- Navigation menu is visible

**Actual Result**: [To be filled during execution]

**Status**: [Pass/Fail/Blocked/Skipped]

**Test Data**:
- Email: test@example.com
- Password: ValidPass123!

**Postconditions**:
- User session is active
- User can logout successfully
```

---

## Test Design Techniques

### 1. Equivalence Partitioning

**Concept**: Divide input data into partitions where all values should behave the same

**Example: Age Validation**
```
Rule: Age must be between 18-65

Partitions:
1. Invalid (< 18):     [-∞, 17]      → Test: 10, 0, -5
2. Valid (18-65):      [18, 65]      → Test: 18, 40, 65
3. Invalid (> 65):     [66, ∞]       → Test: 66, 100, 200

Test Cases:
TC-001: Enter age = 10    → Expected: Error "Minimum age is 18"
TC-002: Enter age = 18    → Expected: Valid
TC-003: Enter age = 40    → Expected: Valid
TC-004: Enter age = 65    → Expected: Valid
TC-005: Enter age = 70    → Expected: Error "Maximum age is 65"
```

**Example: Email Validation**
```
Partitions:
1. Valid format:       user@domain.com
2. No @:              userdomain.com
3. No domain:         user@
4. No local part:     @domain.com
5. Multiple @:        user@@domain.com
6. Invalid chars:     user name@domain.com

Test Cases:
TC-001: email = "test@example.com"     → Valid
TC-002: email = "testexample.com"      → Error "Invalid email"
TC-003: email = "test@"                → Error "Invalid email"
TC-004: email = "@example.com"         → Error "Invalid email"
TC-005: email = "test@@example.com"    → Error "Invalid email"
TC-006: email = "test user@example.com"→ Error "Invalid email"
```

### 2. Boundary Value Analysis

**Concept**: Test at the boundaries of equivalence partitions

**Rule**: For range [A, B], test: A-1, A, A+1, B-1, B, B+1

**Example: Discount Percentage (0-100%)**
```
Boundaries: 0 and 100

Test Cases:
TC-001: discount = -1    → Error "Minimum 0%"
TC-002: discount = 0     → Valid (boundary)
TC-003: discount = 1     → Valid (just inside)
TC-004: discount = 50    → Valid (middle)
TC-005: discount = 99    → Valid (just inside)
TC-006: discount = 100   → Valid (boundary)
TC-007: discount = 101   → Error "Maximum 100%"
```

**Example: String Length (3-20 characters)**
```
Boundaries: 3 and 20

Test Cases:
TC-001: length = 2    (AB)          → Error "Minimum 3 characters"
TC-002: length = 3    (ABC)         → Valid
TC-003: length = 4    (ABCD)        → Valid
TC-004: length = 10   (ABCDEFGHIJ) → Valid
TC-005: length = 19   (19 chars)    → Valid
TC-006: length = 20   (20 chars)    → Valid
TC-007: length = 21   (21 chars)    → Error "Maximum 20 characters"
```

### 3. Decision Table Testing

**Concept**: Test all combinations of conditions and actions

**Example: Loan Approval System**

| Condition | Rule 1 | Rule 2 | Rule 3 | Rule 4 | Rule 5 | Rule 6 | Rule 7 | Rule 8 |
|-----------|--------|--------|--------|--------|--------|--------|--------|--------|
| Age >= 18 | Y | Y | Y | Y | N | N | N | N |
| Income >= $30k | Y | Y | N | N | Y | Y | N | N |
| Good Credit | Y | N | Y | N | Y | N | Y | N |
| **Approve Loan** | **Y** | **N** | **N** | **N** | **N** | **N** | **N** | **N** |
| **Reject Loan** | **N** | **Y** | **Y** | **Y** | **Y** | **Y** | **Y** | **Y** |

```
TC-001: age=25, income=$50k, credit=good   → Approve
TC-002: age=25, income=$50k, credit=bad    → Reject (bad credit)
TC-003: age=25, income=$20k, credit=good   → Reject (low income)
TC-004: age=25, income=$20k, credit=bad    → Reject (low income + bad credit)
TC-005: age=17, income=$50k, credit=good   → Reject (underage)
TC-006: age=17, income=$50k, credit=bad    → Reject (underage + bad credit)
TC-007: age=17, income=$20k, credit=good   → Reject (underage + low income)
TC-008: age=17, income=$20k, credit=bad    → Reject (all conditions fail)
```

**Optimized Decision Table** (Reduced redundancy):

| Condition | Rule 1 | Rule 2 | Rule 3 | Rule 4 |
|-----------|--------|--------|--------|--------|
| Age >= 18 | Y | Y | Y | N |
| Income >= $30k | Y | Y/N | N | - |
| Good Credit | Y | N | - | - |
| **Approve Loan** | **Y** | **N** | **N** | **N** |

### 4. State Transition Testing

**Concept**: Test system behavior through different states

**Example: Order Status State Machine**

```
States: Pending → Processing → Shipped → Delivered → Completed
                        ↓          ↓
                    Cancelled  Cancelled

Valid Transitions:
Pending → Processing
Pending → Cancelled
Processing → Shipped
Processing → Cancelled
Shipped → Delivered
Shipped → Cancelled (within 24h)
Delivered → Completed
```

**Test Cases**:
```
TC-001: Pending → Processing → Shipped → Delivered → Completed
  Steps:
  1. Create order (Pending)
  2. Process order (Processing)
  3. Ship order (Shipped)
  4. Deliver order (Delivered)
  5. Complete order (Completed)
  Expected: All transitions successful

TC-002: Pending → Cancelled
  Steps:
  1. Create order (Pending)
  2. Cancel order (Cancelled)
  Expected: Order cancelled successfully

TC-003: Processing → Cancelled
  Steps:
  1. Create order (Pending)
  2. Process order (Processing)
  3. Cancel order (Cancelled)
  Expected: Order cancelled, payment refunded

TC-004: Invalid transition: Pending → Shipped (skip Processing)
  Steps:
  1. Create order (Pending)
  2. Try to ship order directly
  Expected: Error "Order must be processed first"

TC-005: Invalid transition: Delivered → Processing
  Steps:
  1. Create and deliver order
  2. Try to change to Processing
  Expected: Error "Cannot change delivered order to processing"

TC-006: State validation: Cannot cancel after 24h of shipping
  Steps:
  1. Create and ship order
  2. Wait 24 hours
  3. Try to cancel
  Expected: Error "Cannot cancel after 24 hours"
```

### 5. Pairwise Testing (All-Pairs)

**Concept**: Test all possible pairs of parameters

**Example: Browser Compatibility**

```
Parameters:
- Browser: Chrome, Firefox, Safari, Edge (4 values)
- OS: Windows, macOS, Linux (3 values)
- Screen: Desktop, Tablet, Mobile (3 values)

Full combination: 4 × 3 × 3 = 36 test cases

Pairwise reduced: ~12 test cases (covers all pairs)

Test Cases:
TC-001: Chrome + Windows + Desktop
TC-002: Chrome + macOS + Tablet
TC-003: Chrome + Linux + Mobile
TC-004: Firefox + Windows + Tablet
TC-005: Firefox + macOS + Mobile
TC-006: Firefox + Linux + Desktop
TC-007: Safari + Windows + Mobile
TC-008: Safari + macOS + Desktop
TC-009: Safari + Linux + Tablet
TC-010: Edge + Windows + Mobile
TC-011: Edge + macOS + Desktop
TC-012: Edge + Linux + Tablet
```

**Tool**: Use pairwise testing tools like PICT (Microsoft):
```bash
# input.txt
Browser: Chrome, Firefox, Safari, Edge
OS: Windows, macOS, Linux
Screen: Desktop, Tablet, Mobile

# Generate pairs
pict input.txt
```

### 6. Error Guessing

**Concept**: Use experience to guess likely errors

**Common Error-Prone Areas**:

**1. Null/Empty Values**
```
TC-001: Submit form with empty required field
TC-002: Search with empty query
TC-003: Upload with no file selected
TC-004: API call with null parameter
```

**2. Special Characters**
```
TC-001: Name with apostrophe: O'Brien
TC-002: Name with hyphen: Mary-Jane
TC-003: SQL injection: '; DROP TABLE users; --
TC-004: XSS: <script>alert('XSS')</script>
TC-005: Unicode: 你好世界
TC-006: Emoji: Hello 👋 World
```

**3. Large Numbers**
```
TC-001: Max integer: 2,147,483,647
TC-002: Max integer + 1: 2,147,483,648
TC-003: Negative max: -2,147,483,648
TC-004: Very large number: 999,999,999,999,999
```

**4. Date/Time Edge Cases**
```
TC-001: Leap year: Feb 29, 2024
TC-002: Non-leap year: Feb 29, 2023 (invalid)
TC-003: Year 2038 problem: Jan 19, 2038 03:14:07
TC-004: Daylight saving time change
TC-005: Midnight: 00:00:00
TC-006: End of day: 23:59:59
```

**5. Concurrency Issues**
```
TC-001: Two users update same record simultaneously
TC-002: User submits form twice (double-click)
TC-003: Multiple tabs with same session
TC-004: Race condition in payment processing
```

### 7. Use Case Testing

**Concept**: Test complete user journeys

**Example: E-commerce User Journey**

```
Use Case: Complete Purchase Flow

Primary Actor: Customer

Preconditions:
- User has account
- Product is in stock
- Payment method configured

Main Flow:
1. User logs in
2. User searches for product
3. User views product details
4. User adds product to cart
5. User proceeds to checkout
6. User confirms shipping address
7. User selects payment method
8. User completes purchase
9. User receives order confirmation

Alternative Flows:
A1. Product out of stock (at step 3)
A2. Cart expires (at step 5)
A3. Payment fails (at step 8)
A4. Discount code applied (at step 6)
A5. Guest checkout (skip step 1)

Test Cases:
TC-001: Main flow (happy path)
TC-002: Alt A1 - Product becomes out of stock
TC-003: Alt A2 - Cart items expire
TC-004: Alt A3 - Payment declined
TC-005: Alt A4 - Apply valid discount code
TC-006: Alt A5 - Guest checkout flow
TC-007: Error - Invalid shipping address
TC-008: Error - Payment method expired
TC-009: Edge - Multiple items in cart
TC-010: Edge - Large quantity purchase
```

---

## Black Box Testing Techniques

### Input Domain Testing

**Example: User Registration**

```
Input Fields:
- Email: string, required, format validation
- Password: string, required, 8-20 chars, complexity rules
- Age: number, optional, 18-120
- Phone: string, optional, format validation

Test Cases (Input Validation):

Email:
TC-001: Valid email "test@example.com"
TC-002: Invalid - no @: "testexample.com"
TC-003: Invalid - no domain: "test@"
TC-004: Invalid - spaces: "test user@example.com"
TC-005: Edge - long email: "[64 chars]@[255 chars].com"
TC-006: Edge - international: "测试@例子.中国"

Password:
TC-007: Valid - 8 chars: "Test123!"
TC-008: Valid - 20 chars: "Test1234567890123!"
TC-009: Invalid - too short: "Test1!"
TC-010: Invalid - too long: "Test12345678901234567890!"
TC-011: Invalid - no uppercase: "test123!"
TC-012: Invalid - no number: "TestTest!"
TC-013: Invalid - no special: "Test1234"

Age:
TC-014: Valid - minimum: 18
TC-015: Valid - maximum: 120
TC-016: Valid - omitted (optional)
TC-017: Invalid - below min: 17
TC-018: Invalid - above max: 121
TC-019: Invalid - negative: -5
TC-020: Invalid - decimal: 25.5

Phone:
TC-021: Valid - US format: "+1-555-123-4567"
TC-022: Valid - international: "+44-20-1234-5678"
TC-023: Valid - omitted (optional)
TC-024: Invalid - letters: "555-CALL-NOW"
TC-025: Invalid - too short: "123"
```

### Output Domain Testing

**Example: Search Function**

```
Test Cases (Output Validation):

TC-001: Search returns results
  Input: "laptop"
  Expected: List of laptop products, sorted by relevance

TC-002: Search returns no results
  Input: "xyzabc123notexist"
  Expected: Empty list + message "No results found"

TC-003: Search returns paginated results
  Input: "phone" (500 results)
  Expected: First page (20 items) + pagination controls

TC-004: Search with filters
  Input: "laptop" + price filter "$500-$1000"
  Expected: Only laptops in price range

TC-005: Search result formatting
  Expected output structure:
  {
    results: [
      {
        id: string,
        name: string,
        price: number,
        imageUrl: string,
        rating: number (0-5)
      }
    ],
    total: number,
    page: number,
    perPage: number
  }
```

---

## White Box Testing Techniques

### 1. Statement Coverage

**Goal**: Execute every statement at least once

```typescript
function calculateDiscount(price: number, membershipType: string): number {
  let discount = 0;

  if (price > 100) {           // Line 1
    discount = 10;             // Line 2
  }

  if (membershipType === 'gold') {  // Line 3
    discount += 5;                  // Line 4
  }

  return discount;             // Line 5
}

Test Cases for 100% Statement Coverage:
TC-001: price=150, type='gold'   → Executes all lines (1,2,3,4,5)
TC-002: price=50, type='silver'  → Executes lines (1,3,5) - missed line 2,4

Need both tests for 100% coverage.
```

### 2. Branch Coverage

**Goal**: Execute all branches (true/false) of conditionals

```typescript
function validateUser(age: number, hasLicense: boolean): boolean {
  if (age >= 18) {              // Branch A
    if (hasLicense) {           // Branch B
      return true;
    }
    return false;
  }
  return false;
}

Test Cases for 100% Branch Coverage:
TC-001: age=20, hasLicense=true   → A=true, B=true
TC-002: age=20, hasLicense=false  → A=true, B=false
TC-003: age=16, hasLicense=true   → A=false, B=not reached
TC-004: age=16, hasLicense=false  → A=false, B=not reached

Need tests for: A(true,false) × B(true,false) = 4 combinations
But optimized: TC-001, TC-002, TC-003 cover all branches
```

### 3. Condition Coverage

**Goal**: Test each condition independently

```typescript
function canRent(age: number, income: number, credit: number): boolean {
  if (age >= 18 && income >= 30000 && credit >= 650) {
    return true;
  }
  return false;
}

Test Cases for Condition Coverage:
TC-001: age=20,  income=40000, credit=700  → T && T && T = true
TC-002: age=16,  income=40000, credit=700  → F && T && T = false
TC-003: age=20,  income=20000, credit=700  → T && F && T = false
TC-004: age=20,  income=40000, credit=600  → T && T && F = false

Each condition tested as both true and false.
```

### 4. Path Coverage

**Goal**: Execute all possible paths through code

```typescript
function processOrder(vip: boolean, total: number): number {
  let discount = 0;

  if (vip) {                // Decision 1
    discount = 20;
  } else {
    discount = 10;
  }

  if (total > 100) {        // Decision 2
    discount += 5;
  }

  return discount;
}

Paths:
Path 1: D1=true,  D2=true   → vip=true,  total=150 → discount=25
Path 2: D1=true,  D2=false  → vip=true,  total=50  → discount=20
Path 3: D1=false, D2=true   → vip=false, total=150 → discount=15
Path 4: D1=false, D2=false  → vip=false, total=50  → discount=10

Test Cases:
TC-001: vip=true,  total=150  → Path 1 → Result: 25
TC-002: vip=true,  total=50   → Path 2 → Result: 20
TC-003: vip=false, total=150  → Path 3 → Result: 15
TC-004: vip=false, total=50   → Path 4 → Result: 10
```

---

## Test Case Templates

### Functional Test Case Template

```markdown
**Test Case ID**: TC-[Module]-[Number]
**Module**: [Module Name]
**Feature**: [Feature Name]
**User Story**: [US-XXX]
**Priority**: [Critical/High/Medium/Low]
**Type**: [Functional/Integration/Regression]
**Automated**: [Yes/No]

**Test Objective**:
[What are we testing and why?]

**Preconditions**:
- [Condition 1]
- [Condition 2]

**Test Data**:
| Field | Value |
|-------|-------|
| Email | test@example.com |
| Password | ValidPass123! |

**Test Steps**:
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to login page | Login page displays |
| 2 | Enter email | Email field populated |
| 3 | Enter password | Password masked |
| 4 | Click Login button | User redirected to dashboard |

**Expected Results**:
- User successfully authenticated
- Dashboard loads within 2 seconds
- Welcome message displays user name

**Actual Results**:
[To be filled during execution]

**Status**: [Pass/Fail/Blocked/Skipped]
**Executed By**: [Tester Name]
**Execution Date**: [Date]
**Environment**: [Dev/Staging/Prod]
**Browser**: [Chrome 120]
**OS**: [Windows 11]

**Defects**: [BUG-XXX if failed]

**Notes**:
[Any additional observations]
```

### API Test Case Template

```markdown
**Test Case ID**: API-[Endpoint]-[Number]
**Endpoint**: POST /api/users
**Priority**: High
**Type**: API Integration Test

**Test Objective**:
Verify user creation with valid data

**Request**:
```json
POST /api/users
Headers:
  Content-Type: application/json
  Authorization: Bearer {token}

Body:
{
  "email": "test@example.com",
  "name": "Test User",
  "age": 25
}
```

**Expected Response**:
```json
Status Code: 201 Created
Headers:
  Content-Type: application/json
  Location: /api/users/123

Body:
{
  "id": "123",
  "email": "test@example.com",
  "name": "Test User",
  "age": 25,
  "createdAt": "2025-11-19T10:30:00Z"
}
```

**Validations**:
- [ ] Status code is 201
- [ ] Response time < 500ms
- [ ] ID is generated (UUID format)
- [ ] Email matches request
- [ ] Password not in response
- [ ] createdAt is valid ISO8601
- [ ] Location header present
- [ ] User exists in database

**Actual Response**:
[To be filled]

**Status**: [Pass/Fail]
```

### Performance Test Case Template

```markdown
**Test Case ID**: PERF-[Feature]-[Number]
**Feature**: User Login
**Type**: Performance - Load Test
**Priority**: High

**Test Objective**:
Verify login endpoint handles 1000 concurrent users

**Performance Requirements**:
| Metric | Target |
|--------|--------|
| Response Time (p95) | < 500ms |
| Response Time (p99) | < 1000ms |
| Throughput | > 100 RPS |
| Error Rate | < 1% |
| CPU Usage | < 70% |
| Memory Usage | < 80% |

**Load Profile**:
- Ramp up: 0 to 1000 users in 2 minutes
- Sustain: 1000 users for 10 minutes
- Ramp down: 2 minutes

**Test Scenario**:
1. User sends login request
2. System authenticates
3. System returns token
4. Think time: 2-5 seconds

**Metrics Collected**:
- Response time percentiles
- Requests per second
- Error count and types
- Resource utilization

**Results**:
[Performance metrics table]

**Status**: [Pass/Fail based on targets]
```

---

## Test Data Design

### Test Data Categories

**1. Valid Data**
```
Purpose: Happy path testing
Examples:
- email: "user@example.com"
- age: 25
- phone: "+1-555-123-4567"
```

**2. Invalid Data**
```
Purpose: Negative testing
Examples:
- email: "invalid-email"
- age: -5
- phone: "abc"
```

**3. Boundary Data**
```
Purpose: Boundary testing
Examples:
- age: 18 (min), 65 (max)
- password: 8 chars (min), 20 chars (max)
- quantity: 0, 1, 999, 1000
```

**4. Edge Cases**
```
Purpose: Unusual but valid scenarios
Examples:
- name: "X" (single char)
- name: "Mary-Ann O'Brien-Smith" (special chars)
- email: "user+tag@sub.domain.co.uk" (complex but valid)
```

**5. Special Characters**
```
Purpose: Security and encoding testing
Examples:
- SQL injection: "'; DROP TABLE users; --"
- XSS: "<script>alert('XSS')</script>"
- Path traversal: "../../etc/passwd"
- Unicode: "你好世界"
- Emoji: "Hello 👋"
```

### Test Data Generation Strategies

**1. Realistic Data (using Faker)**
```typescript
import { faker } from '@faker-js/faker';

const testUser = {
  firstName: faker.person.firstName(),      // "John"
  lastName: faker.person.lastName(),        // "Doe"
  email: faker.internet.email(),            // "john.doe@example.com"
  phone: faker.phone.number(),              // "+1-555-123-4567"
  address: {
    street: faker.location.streetAddress(), // "123 Main St"
    city: faker.location.city(),            // "San Francisco"
    zipCode: faker.location.zipCode()       // "94102"
  },
  dateOfBirth: faker.date.birthdate(),      // Date object
  company: faker.company.name()             // "Acme Corp"
};
```

**2. Parametrized Data**
```typescript
const testCases = [
  { age: -1,  expected: 'error' },
  { age: 0,   expected: 'error' },
  { age: 17,  expected: 'error' },
  { age: 18,  expected: 'valid' },
  { age: 50,  expected: 'valid' },
  { age: 65,  expected: 'valid' },
  { age: 66,  expected: 'error' },
  { age: 200, expected: 'error' }
];

testCases.forEach(({ age, expected }) => {
  test(`age ${age} should be ${expected}`, () => {
    const result = validateAge(age);
    if (expected === 'valid') {
      expect(result.isValid).toBe(true);
    } else {
      expect(result.isValid).toBe(false);
    }
  });
});
```

**3. Data Builders**
```typescript
class UserBuilder {
  private user = {
    email: 'test@example.com',
    password: 'ValidPass123!',
    age: 25,
    role: 'user'
  };

  withEmail(email: string) {
    this.user.email = email;
    return this;
  }

  withAge(age: number) {
    this.user.age = age;
    return this;
  }

  asAdmin() {
    this.user.role = 'admin';
    return this;
  }

  build() {
    return { ...this.user };
  }
}

// Usage
const normalUser = new UserBuilder().build();
const adminUser = new UserBuilder().asAdmin().build();
const youngUser = new UserBuilder().withAge(18).build();
const invalidUser = new UserBuilder().withEmail('invalid').build();
```

---

## Test Coverage Strategies

### Coverage Metrics

**1. Requirements Coverage**
```
Total Requirements: 100
Requirements with Tests: 85
Coverage: 85%

Gap Analysis:
- REQ-042: No test cases
- REQ-057: Partial coverage
- REQ-063: No automated tests
```

**2. Code Coverage**
```
Statement Coverage: 85%
Branch Coverage: 78%
Function Coverage: 92%
Line Coverage: 83%
```

**3. Risk-Based Coverage**
```
High Risk Areas (95%+ coverage):
- Payment processing
- User authentication
- Data encryption
- Financial calculations

Medium Risk (80%+ coverage):
- User profile management
- Search functionality
- Notifications

Low Risk (60%+ coverage):
- UI styling
- Help text
- Footer links
```

### Coverage Matrix

| Requirement | Unit | Integration | E2E | Manual | Status |
|-------------|------|-------------|-----|--------|--------|
| REQ-001: User Login | ✅ | ✅ | ✅ | ✅ | Complete |
| REQ-002: Password Reset | ✅ | ✅ | ⚠️ | ✅ | Partial |
| REQ-003: Profile Update | ✅ | ❌ | ❌ | ✅ | Gaps |
| REQ-004: Payment | ✅ | ✅ | ✅ | ✅ | Complete |

---

## Test Case Examples by Domain

### E-commerce Test Cases

```markdown
**Add to Cart**

TC-001: Add single item to empty cart
TC-002: Add multiple quantities of same item
TC-003: Add different items to cart
TC-004: Add item when cart has max items (limit)
TC-005: Add out-of-stock item (should fail)
TC-006: Add item with invalid quantity (0, negative)
TC-007: Add item as guest user
TC-008: Add item as logged-in user
TC-009: Cart persists across sessions
TC-010: Cart expires after timeout

**Checkout Process**

TC-011: Checkout with single item
TC-012: Checkout with multiple items
TC-013: Apply valid discount code
TC-014: Apply invalid/expired discount code
TC-015: Select shipping address from saved addresses
TC-016: Enter new shipping address
TC-017: Select payment method (credit card)
TC-018: Select payment method (PayPal)
TC-019: Complete purchase successfully
TC-020: Payment declined
TC-021: Checkout as guest
TC-022: Save order for later
```

### Banking Application Test Cases

```markdown
**Fund Transfer**

TC-001: Transfer valid amount within limit
TC-002: Transfer amount equal to balance
TC-003: Transfer amount exceeding balance (should fail)
TC-004: Transfer to valid beneficiary
TC-005: Transfer to invalid account number
TC-006: Transfer with insufficient balance
TC-007: Transfer exceeding daily limit
TC-008: Multiple transfers in sequence
TC-009: Concurrent transfers from same account
TC-010: Transfer with special instructions

**Security**

TC-011: Lock account after 3 failed login attempts
TC-012: Session timeout after inactivity
TC-013: Require 2FA for large transactions
TC-014: Prevent XSS in transaction remarks
TC-015: Prevent SQL injection in search
TC-016: Encrypt sensitive data in transit
TC-017: Mask account numbers in UI
TC-018: Audit log all transactions
```

---

## Best Practices

### Test Case Design Principles

✅ **DO**:
- Write clear, unambiguous test cases
- Include specific expected results
- Use test data that's realistic
- Cover positive and negative scenarios
- Test boundary conditions
- Make tests independent
- Link to requirements
- Include preconditions and postconditions
- Version control test cases
- Review test cases before execution

❌ **DON'T**:
- Assume prerequisites without stating them
- Write vague expected results like "works correctly"
- Skip negative testing
- Create test dependencies
- Hardcode test data in steps
- Write overly complex test cases
- Forget to update tests when requirements change
- Test multiple things in one test case
- Ignore edge cases
- Write tests that can't be reproduced

---

**Guide Version**: 1.0
**Last Updated**: 2025-11-19
**References**: ISTQB Foundation, IEEE 829, ISO/IEC/IEEE 29119
