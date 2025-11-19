# Code Quality Standards

## Overview

This document outlines elite-level code quality standards based on industry best practices from FAANG companies, open-source communities, and established software engineering principles.

---

## SOLID Principles

### Single Responsibility Principle (SRP)
**Definition**: A class should have only one reason to change.

**Good Example**:
```typescript
// ❌ Bad: Multiple responsibilities
class UserManager {
  createUser(data: UserData) { }
  sendWelcomeEmail(user: User) { }
  logUserActivity(user: User) { }
  generateUserReport(user: User) { }
}

// ✅ Good: Single responsibilities
class UserService {
  createUser(data: UserData) { }
}

class EmailService {
  sendWelcomeEmail(user: User) { }
}

class ActivityLogger {
  logUserActivity(user: User) { }
}

class ReportGenerator {
  generateUserReport(user: User) { }
}
```

### Open/Closed Principle (OCP)
**Definition**: Software entities should be open for extension but closed for modification.

**Good Example**:
```typescript
// ✅ Good: Use strategy pattern
interface PaymentProcessor {
  processPayment(amount: number): Promise<PaymentResult>;
}

class StripePaymentProcessor implements PaymentProcessor {
  async processPayment(amount: number): Promise<PaymentResult> {
    // Stripe-specific implementation
  }
}

class PayPalPaymentProcessor implements PaymentProcessor {
  async processPayment(amount: number): Promise<PaymentResult> {
    // PayPal-specific implementation
  }
}

class PaymentService {
  constructor(private processor: PaymentProcessor) {}

  async pay(amount: number) {
    return this.processor.processPayment(amount);
  }
}
```

### Liskov Substitution Principle (LSP)
**Definition**: Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

### Interface Segregation Principle (ISP)
**Definition**: No client should be forced to depend on methods it does not use.

**Good Example**:
```typescript
// ❌ Bad: Fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

// ✅ Good: Segregated interfaces
interface Workable {
  work(): void;
}

interface Eatable {
  eat(): void;
}

interface Sleepable {
  sleep(): void;
}

class Human implements Workable, Eatable, Sleepable {
  work() { }
  eat() { }
  sleep() { }
}

class Robot implements Workable {
  work() { }
}
```

### Dependency Inversion Principle (DIP)
**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions.

---

## Clean Code Principles

### Meaningful Names

**Variables**:
```typescript
// ❌ Bad
const d = 86400; // elapsed time in days
const list = getUserList();

// ✅ Good
const SECONDS_PER_DAY = 86400;
const activeUsers = getActiveUserList();
```

**Functions**:
```typescript
// ❌ Bad
function getData() { }
function process() { }

// ✅ Good
function fetchUserProfile(userId: string) { }
function validateEmailAddress(email: string) { }
```

**Classes**:
```typescript
// ❌ Bad
class DataManager { }
class Handler { }

// ✅ Good
class UserRepository { }
class PaymentProcessor { }
```

### Function Best Practices

**Small Functions**:
```typescript
// ❌ Bad: Long function
function processOrder(order: Order) {
  // Validate order (15 lines)
  // Calculate total (10 lines)
  // Apply discounts (20 lines)
  // Process payment (25 lines)
  // Send confirmation (10 lines)
  // Update inventory (15 lines)
}

// ✅ Good: Small, focused functions
function processOrder(order: Order) {
  validateOrder(order);
  const total = calculateOrderTotal(order);
  const finalAmount = applyDiscounts(total, order);
  processPayment(finalAmount, order.paymentMethod);
  sendOrderConfirmation(order);
  updateInventory(order.items);
}
```

**Single Level of Abstraction**:
```typescript
// ❌ Bad: Mixed abstraction levels
function createUser(userData: UserData) {
  const user = new User();
  user.email = userData.email.toLowerCase().trim();
  user.name = userData.name;

  // Low-level database operations mixed with high-level logic
  const connection = mysql.createConnection(config);
  connection.query('INSERT INTO users...', user);
}

// ✅ Good: Consistent abstraction level
function createUser(userData: UserData) {
  const validatedData = validateUserData(userData);
  const user = buildUserEntity(validatedData);
  return userRepository.save(user);
}
```

**Avoid Side Effects**:
```typescript
// ❌ Bad: Unexpected side effects
function checkPassword(password: string): boolean {
  if (isValid(password)) {
    Session.initialize(); // Side effect!
    return true;
  }
  return false;
}

// ✅ Good: Pure function, separate side effects
function isPasswordValid(password: string): boolean {
  return password.length >= 8 && /[A-Z]/.test(password);
}

function login(username: string, password: string) {
  if (isPasswordValid(password)) {
    Session.initialize(); // Explicit side effect
  }
}
```

### Error Handling

**Use Exceptions, Not Error Codes**:
```typescript
// ❌ Bad: Error codes
function deleteUser(userId: string): number {
  if (!userId) return -1;
  if (!userExists(userId)) return -2;
  // ... delete logic
  return 0; // Success
}

// ✅ Good: Exceptions
function deleteUser(userId: string): void {
  if (!userId) {
    throw new ValidationError('User ID is required');
  }
  if (!userExists(userId)) {
    throw new NotFoundError(`User ${userId} not found`);
  }
  // ... delete logic
}
```

**Don't Return Null**:
```typescript
// ❌ Bad: Returning null
function getUser(id: string): User | null {
  // ...
  return null;
}

const user = getUser('123');
if (user !== null) { // Null check required everywhere
  // ...
}

// ✅ Good: Use Optional/Maybe pattern or throw exception
function getUser(id: string): User {
  const user = findUser(id);
  if (!user) {
    throw new NotFoundError(`User ${id} not found`);
  }
  return user;
}

// Or with Optional type
function findUser(id: string): Optional<User> {
  // ...
  return Optional.of(user);
}
```

### Comments

**Self-Documenting Code > Comments**:
```typescript
// ❌ Bad: Unnecessary comments
// Check if user is adult
if (user.age >= 18) {
  // ...
}

// ✅ Good: Self-documenting
if (user.isAdult()) {
  // ...
}
```

**Good Comments**:
```typescript
// ✅ Legal comments
/**
 * Copyright (C) 2025 Company Name
 * Licensed under MIT License
 */

// ✅ Explanation of intent
// We use a WeakMap here to prevent memory leaks when components unmount
const cache = new WeakMap();

// ✅ Warning of consequences
// Don't remove this timeout! It's required for the animation to complete
// before the DOM element is removed
setTimeout(() => removeElement(), 300);

// ✅ TODO comments
// TODO: Refactor this to use the new payment API (TICKET-123)

// ✅ Complex algorithm explanation
/**
 * Uses binary search to find the insertion point.
 * Time complexity: O(log n)
 * Space complexity: O(1)
 */
```

---

## Code Organization

### File Structure

**One Class Per File**:
```
// ❌ Bad: Multiple classes in one file
user-stuff.ts

// ✅ Good: Single responsibility per file
user.entity.ts
user.repository.ts
user.service.ts
user.controller.ts
```

**Logical Grouping**:
```
src/
├── modules/
│   ├── users/
│   │   ├── dto/
│   │   ├── entities/
│   │   ├── services/
│   │   ├── controllers/
│   │   └── repositories/
│   ├── products/
│   └── orders/
├── common/
│   ├── guards/
│   ├── interceptors/
│   └── pipes/
└── config/
```

### Dependency Management

**Dependency Injection**:
```typescript
// ✅ Good: Dependency injection
class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService,
    private logger: Logger
  ) {}

  async createUser(data: UserData) {
    const user = await this.userRepository.create(data);
    await this.emailService.sendWelcome(user.email);
    this.logger.info(`User created: ${user.id}`);
    return user;
  }
}
```

---

## Testing Standards

### Test Structure (AAA Pattern)

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user and send welcome email', async () => {
      // Arrange
      const userData = { email: 'test@example.com', name: 'Test User' };
      const mockRepository = createMockRepository();
      const mockEmailService = createMockEmailService();
      const service = new UserService(mockRepository, mockEmailService);

      // Act
      const result = await service.createUser(userData);

      // Assert
      expect(result).toBeDefined();
      expect(result.email).toBe(userData.email);
      expect(mockEmailService.sendWelcome).toHaveBeenCalledWith(userData.email);
    });
  });
});
```

### Test Coverage Goals

- **Critical paths**: 100% coverage
- **Business logic**: 90%+ coverage
- **Overall**: 80%+ coverage
- **Integration tests**: Cover all API endpoints
- **E2E tests**: Cover critical user flows

---

## Performance Standards

### Big O Complexity Awareness

```typescript
// ❌ Bad: O(n²) complexity
function findDuplicates(arr: number[]): number[] {
  const duplicates: number[] = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

// ✅ Good: O(n) complexity
function findDuplicates(arr: number[]): number[] {
  const seen = new Set<number>();
  const duplicates = new Set<number>();

  for (const num of arr) {
    if (seen.has(num)) {
      duplicates.add(num);
    }
    seen.add(num);
  }

  return Array.from(duplicates);
}
```

### Avoid Premature Optimization

```typescript
// ✅ Start simple and readable
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Only optimize if profiling shows this is a bottleneck
```

---

## Security Standards

### Input Validation

```typescript
// ✅ Always validate and sanitize input
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(0).max(150),
  name: z.string().min(1).max(100)
});

function createUser(input: unknown) {
  const validatedData = userSchema.parse(input);
  // Safe to use validatedData
}
```

### Secure Data Handling

```typescript
// ❌ Bad: Exposing sensitive data
function getUser(id: string) {
  return db.users.findOne({ id }); // Returns password hash!
}

// ✅ Good: Exclude sensitive fields
function getUser(id: string) {
  return db.users.findOne(
    { id },
    { projection: { password: 0, salt: 0 } }
  );
}
```

---

## Code Review Checklist

### Before Submitting PR

- [ ] Code follows project style guide
- [ ] All tests pass
- [ ] New code has test coverage
- [ ] No console.log or debug statements
- [ ] No commented-out code
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] Performance implications considered
- [ ] Error handling is comprehensive
- [ ] No hardcoded secrets or credentials

### During Code Review

- [ ] Logic is correct
- [ ] Edge cases are handled
- [ ] Code is readable and maintainable
- [ ] No code duplication
- [ ] Appropriate design patterns used
- [ ] Security best practices followed
- [ ] Tests are meaningful and comprehensive
- [ ] API changes are backward compatible (if applicable)

---

## Documentation Standards

### Code Documentation

```typescript
/**
 * Creates a new user account with email verification.
 *
 * @param userData - The user data including email, name, and password
 * @returns Promise resolving to the created user (without password)
 * @throws {ValidationError} If user data is invalid
 * @throws {ConflictError} If email already exists
 *
 * @example
 * const user = await createUser({
 *   email: 'john@example.com',
 *   name: 'John Doe',
 *   password: 'SecurePass123!'
 * });
 */
async function createUser(userData: UserData): Promise<User> {
  // Implementation
}
```

### README Documentation

Every module/package should have:
- Purpose and scope
- Installation instructions
- Usage examples
- API documentation
- Contributing guidelines
- License information

---

## References

- **Google Style Guides**: https://google.github.io/styleguide/
- **Airbnb JavaScript Style Guide**: https://github.com/airbnb/javascript
- **Clean Code** by Robert C. Martin
- **Refactoring** by Martin Fowler
- **The Pragmatic Programmer** by Hunt & Thomas

---

## Version

**Version**: 1.0
**Last Updated**: 2025-11-19
