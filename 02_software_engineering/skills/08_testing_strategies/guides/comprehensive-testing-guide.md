# Comprehensive Testing Guide for Modern Applications

A complete guide to implementing robust testing strategies across all layers of your application.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [E2E Testing](#e2e-testing)
5. [Advanced Testing Patterns](#advanced-testing-patterns)
6. [Test Infrastructure](#test-infrastructure)
7. [Best Practices](#best-practices)

## Testing Philosophy

### The Testing Pyramid

```
           /\
          /  \
         / E2E \       ~10% - Slow, expensive, brittle
        /      \       Test critical user journeys
       /--------\
      /          \
     / Integration\   ~20% - Medium speed
    /    Tests     \  Test component interaction
   /----------------\
  /                  \
 /    Unit Tests      \ ~70% - Fast, isolated
/      (Foundation)    \ Test business logic
------------------------
```

### The Testing Trophy (Modern View)

```
           /\
          /  \
         / E2E \       ~10% - Critical flows
        /------\
       /        \
      /  Integ.  \     ~50% - Most testing effort
     /   Tests    \
    /--------------\
   /                \
  /  Static Analysis\ ~20% - Types, linting
 /--------------------\
/    Unit Tests        \ ~20% - Business logic
-------------------------
```

### When to Use Each Type

**Unit Tests**:
- Business logic
- Utility functions
- Algorithm implementations
- Edge case handling

**Integration Tests**:
- API endpoints
- Database operations
- Service interactions
- External API mocking

**E2E Tests**:
- Critical user flows (signup, checkout)
- Auth flows
- Payment processing
- Data consistency across system

## Unit Testing

### Setting Up Jest/Vitest

**vitest.config.ts**:
```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### Testing Pure Functions

```typescript
// utils/string.ts
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// utils/string.test.ts
import { describe, it, expect } from 'vitest';
import { capitalize, slugify } from './string';

describe('capitalize', () => {
  it('should capitalize first letter', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('should handle all uppercase', () => {
    expect(capitalize('HELLO')).toBe('Hello');
  });

  it('should handle mixed case', () => {
    expect(capitalize('hElLo')).toBe('Hello');
  });

  it('should return empty string for empty input', () => {
    expect(capitalize('')).toBe('');
  });

  it('should handle single character', () => {
    expect(capitalize('a')).toBe('A');
  });
});

describe('slugify', () => {
  it('should convert spaces to hyphens', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('should remove special characters', () => {
    expect(slugify('Hello @#$ World!')).toBe('hello-world');
  });

  it('should handle multiple spaces', () => {
    expect(slugify('Hello    World')).toBe('hello-world');
  });

  it('should trim leading/trailing hyphens', () => {
    expect(slugify('  Hello World  ')).toBe('hello-world');
  });

  it('should handle already slugified strings', () => {
    expect(slugify('hello-world')).toBe('hello-world');
  });
});
```

### Testing Classes with Dependencies

```typescript
// services/payment.service.ts
export interface PaymentGateway {
  charge(amount: number, token: string): Promise<{ transactionId: string }>;
  refund(transactionId: string): Promise<void>;
}

export interface NotificationService {
  send(userId: string, message: string): Promise<void>;
}

export class PaymentService {
  constructor(
    private gateway: PaymentGateway,
    private notifications: NotificationService
  ) {}

  async processPayment(
    userId: string,
    amount: number,
    token: string
  ): Promise<string> {
    if (amount <= 0) {
      throw new Error('Amount must be positive');
    }

    const { transactionId } = await this.gateway.charge(amount, token);

    await this.notifications.send(
      userId,
      `Payment of $${amount} processed successfully`
    );

    return transactionId;
  }

  async refundPayment(userId: string, transactionId: string): Promise<void> {
    await this.gateway.refund(transactionId);

    await this.notifications.send(
      userId,
      'Your payment has been refunded'
    );
  }
}

// services/payment.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PaymentService, PaymentGateway, NotificationService } from './payment.service';

describe('PaymentService', () => {
  let paymentService: PaymentService;
  let mockGateway: PaymentGateway;
  let mockNotifications: NotificationService;

  beforeEach(() => {
    mockGateway = {
      charge: vi.fn(),
      refund: vi.fn(),
    };

    mockNotifications = {
      send: vi.fn(),
    };

    paymentService = new PaymentService(mockGateway, mockNotifications);
  });

  describe('processPayment', () => {
    it('should process payment successfully', async () => {
      // Arrange
      const userId = 'user-123';
      const amount = 100;
      const token = 'tok_123';
      const transactionId = 'txn_123';

      vi.mocked(mockGateway.charge).mockResolvedValue({ transactionId });
      vi.mocked(mockNotifications.send).mockResolvedValue(undefined);

      // Act
      const result = await paymentService.processPayment(userId, amount, token);

      // Assert
      expect(result).toBe(transactionId);
      expect(mockGateway.charge).toHaveBeenCalledWith(amount, token);
      expect(mockNotifications.send).toHaveBeenCalledWith(
        userId,
        'Payment of $100 processed successfully'
      );
    });

    it('should throw error for negative amount', async () => {
      await expect(
        paymentService.processPayment('user-123', -10, 'tok_123')
      ).rejects.toThrow('Amount must be positive');

      expect(mockGateway.charge).not.toHaveBeenCalled();
      expect(mockNotifications.send).not.toHaveBeenCalled();
    });

    it('should throw error for zero amount', async () => {
      await expect(
        paymentService.processPayment('user-123', 0, 'tok_123')
      ).rejects.toThrow('Amount must be positive');
    });

    it('should propagate gateway errors', async () => {
      vi.mocked(mockGateway.charge).mockRejectedValue(
        new Error('Payment declined')
      );

      await expect(
        paymentService.processPayment('user-123', 100, 'tok_123')
      ).rejects.toThrow('Payment declined');

      expect(mockNotifications.send).not.toHaveBeenCalled();
    });
  });

  describe('refundPayment', () => {
    it('should refund payment successfully', async () => {
      const userId = 'user-123';
      const transactionId = 'txn_123';

      vi.mocked(mockGateway.refund).mockResolvedValue(undefined);
      vi.mocked(mockNotifications.send).mockResolvedValue(undefined);

      await paymentService.refundPayment(userId, transactionId);

      expect(mockGateway.refund).toHaveBeenCalledWith(transactionId);
      expect(mockNotifications.send).toHaveBeenCalledWith(
        userId,
        'Your payment has been refunded'
      );
    });

    it('should still send notification even if refund fails', async () => {
      vi.mocked(mockGateway.refund).mockRejectedValue(
        new Error('Refund failed')
      );

      await expect(
        paymentService.refundPayment('user-123', 'txn_123')
      ).rejects.toThrow('Refund failed');

      expect(mockNotifications.send).not.toHaveBeenCalled();
    });
  });
});
```

### Testing React Components

```typescript
// components/LoginForm.tsx
import { useState } from 'react';

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  onForgotPassword?: () => void;
}

export function LoginForm({ onSubmit, onForgotPassword }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Email and password are required');
      return;
    }

    setLoading(true);
    try {
      await onSubmit(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} data-testid="login-form">
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={loading}
          data-testid="email-input"
        />
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
          data-testid="password-input"
        />
      </div>

      {error && (
        <div role="alert" data-testid="error-message">
          {error}
        </div>
      )}

      <button type="submit" disabled={loading} data-testid="submit-button">
        {loading ? 'Logging in...' : 'Login'}
      </button>

      {onForgotPassword && (
        <button
          type="button"
          onClick={onForgotPassword}
          data-testid="forgot-password-button"
        >
          Forgot Password?
        </button>
      )}
    </form>
  );
}

// components/LoginForm.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('should render form fields', () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('should call onSubmit with credentials', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.click(screen.getByTestId('submit-button'));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('should show error for empty fields', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<LoginForm onSubmit={onSubmit} />);

    await user.click(screen.getByTestId('submit-button'));

    expect(await screen.findByTestId('error-message')).toHaveTextContent(
      'Email and password are required'
    );
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('should show error when login fails', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockRejectedValue(new Error('Invalid credentials'));

    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'wrongpassword');
    await user.click(screen.getByTestId('submit-button'));

    expect(await screen.findByTestId('error-message')).toHaveTextContent(
      'Invalid credentials'
    );
  });

  it('should disable form during submission', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');

    const submitButton = screen.getByTestId('submit-button');
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(screen.getByTestId('email-input')).toBeDisabled();
    expect(screen.getByTestId('password-input')).toBeDisabled();
    expect(submitButton).toHaveTextContent('Logging in...');

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('should render forgot password button when provided', () => {
    const onSubmit = vi.fn();
    const onForgotPassword = vi.fn();

    render(<LoginForm onSubmit={onSubmit} onForgotPassword={onForgotPassword} />);

    expect(screen.getByTestId('forgot-password-button')).toBeInTheDocument();
  });

  it('should call onForgotPassword when clicked', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onForgotPassword = vi.fn();

    render(<LoginForm onSubmit={onSubmit} onForgotPassword={onForgotPassword} />);

    await user.click(screen.getByTestId('forgot-password-button'));

    expect(onForgotPassword).toHaveBeenCalled();
  });
});
```

## Integration Testing

### API Integration Tests with Supertest

```typescript
// test/integration/users.test.ts
import request from 'supertest';
import { app } from '../../src/app';
import { prisma } from '../../src/lib/prisma';

describe('User API Integration Tests', () => {
  beforeAll(async () => {
    // Setup test database
    await prisma.$connect();
  });

  afterAll(async () => {
    // Cleanup
    await prisma.user.deleteMany();
    await prisma.$disconnect();
  });

  beforeEach(async () => {
    // Clean data before each test
    await prisma.user.deleteMany();
  });

  describe('POST /api/users', () => {
    it('should create a new user', async () => {
      const userData = {
        email: 'john@example.com',
        name: 'John Doe',
        password: 'SecurePass123!',
      };

      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect('Content-Type', /json/)
        .expect(201);

      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: userData.email,
        name: userData.name,
      });

      expect(response.body.password).toBeUndefined();

      // Verify in database
      const user = await prisma.user.findUnique({
        where: { id: response.body.id },
      });

      expect(user).toBeTruthy();
      expect(user!.email).toBe(userData.email);
    });

    it('should validate email format', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'invalid-email',
          name: 'John Doe',
          password: 'SecurePass123!',
        })
        .expect(400);

      expect(response.body).toHaveProperty('error');
      expect(response.body.error).toContain('email');
    });

    it('should enforce unique email constraint', async () => {
      const userData = {
        email: 'duplicate@example.com',
        name: 'John Doe',
        password: 'SecurePass123!',
      };

      // Create first user
      await request(app).post('/api/users').send(userData).expect(201);

      // Try to create duplicate
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(409);

      expect(response.body.error).toContain('already exists');
    });

    it('should hash passwords', async () => {
      const userData = {
        email: 'john@example.com',
        name: 'John Doe',
        password: 'SecurePass123!',
      };

      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(201);

      const user = await prisma.user.findUnique({
        where: { id: response.body.id },
      });

      expect(user!.passwordHash).not.toBe(userData.password);
      expect(user!.passwordHash).toMatch(/^\$2[aby]\$/); // bcrypt hash
    });
  });

  describe('GET /api/users/:id', () => {
    it('should return user by id', async () => {
      const user = await prisma.user.create({
        data: {
          email: 'john@example.com',
          name: 'John Doe',
          passwordHash: 'hashed',
        },
      });

      const response = await request(app)
        .get(`/api/users/${user.id}`)
        .expect(200);

      expect(response.body).toMatchObject({
        id: user.id,
        email: user.email,
        name: user.name,
      });

      expect(response.body.passwordHash).toBeUndefined();
    });

    it('should return 404 for non-existent user', async () => {
      await request(app)
        .get('/api/users/nonexistent-id')
        .expect(404);
    });
  });

  describe('PATCH /api/users/:id', () => {
    it('should update user name', async () => {
      const user = await prisma.user.create({
        data: {
          email: 'john@example.com',
          name: 'John Doe',
          passwordHash: 'hashed',
        },
      });

      const response = await request(app)
        .patch(`/api/users/${user.id}`)
        .send({ name: 'Jane Doe' })
        .expect(200);

      expect(response.body.name).toBe('Jane Doe');

      const updated = await prisma.user.findUnique({
        where: { id: user.id },
      });

      expect(updated!.name).toBe('Jane Doe');
    });

    it('should not allow email updates', async () => {
      const user = await prisma.user.create({
        data: {
          email: 'john@example.com',
          name: 'John Doe',
          passwordHash: 'hashed',
        },
      });

      await request(app)
        .patch(`/api/users/${user.id}`)
        .send({ email: 'newemail@example.com' })
        .expect(400);
    });
  });

  describe('DELETE /api/users/:id', () => {
    it('should delete user', async () => {
      const user = await prisma.user.create({
        data: {
          email: 'john@example.com',
          name: 'John Doe',
          passwordHash: 'hashed',
        },
      });

      await request(app)
        .delete(`/api/users/${user.id}`)
        .expect(204);

      const deleted = await prisma.user.findUnique({
        where: { id: user.id },
      });

      expect(deleted).toBeNull();
    });
  });
});
```

### Database Testing with Test Containers

```typescript
// test/integration/database.test.ts
import { GenericContainer, StartedTestContainer } from 'testcontainers';
import { PrismaClient } from '@prisma/client';
import { execSync } from 'child_process';

describe('Database Integration Tests', () => {
  let container: StartedTestContainer;
  let prisma: PrismaClient;

  beforeAll(async () => {
    // Start PostgreSQL container
    container = await new GenericContainer('postgres:16')
      .withEnvironment({
        POSTGRES_USER: 'test',
        POSTGRES_PASSWORD: 'test',
        POSTGRES_DB: 'testdb',
      })
      .withExposedPorts(5432)
      .start();

    const port = container.getMappedPort(5432);
    const databaseUrl = `postgresql://test:test@localhost:${port}/testdb`;

    // Set environment variable for Prisma
    process.env.DATABASE_URL = databaseUrl;

    // Initialize Prisma client
    prisma = new PrismaClient();
    await prisma.$connect();

    // Run migrations
    execSync('npx prisma migrate deploy', {
      env: { ...process.env, DATABASE_URL: databaseUrl },
    });
  }, 60000);

  afterAll(async () => {
    await prisma.$disconnect();
    await container.stop();
  });

  beforeEach(async () => {
    // Clean database before each test
    await prisma.user.deleteMany();
    await prisma.post.deleteMany();
  });

  it('should create and retrieve user', async () => {
    const user = await prisma.user.create({
      data: {
        email: 'test@example.com',
        name: 'Test User',
        passwordHash: 'hashed',
      },
    });

    const retrieved = await prisma.user.findUnique({
      where: { id: user.id },
    });

    expect(retrieved).toMatchObject({
      email: 'test@example.com',
      name: 'Test User',
    });
  });

  it('should handle unique constraint violations', async () => {
    await prisma.user.create({
      data: {
        email: 'duplicate@example.com',
        name: 'User 1',
        passwordHash: 'hashed',
      },
    });

    await expect(
      prisma.user.create({
        data: {
          email: 'duplicate@example.com',
          name: 'User 2',
          passwordHash: 'hashed',
        },
      })
    ).rejects.toThrow();
  });

  it('should handle relations correctly', async () => {
    const user = await prisma.user.create({
      data: {
        email: 'author@example.com',
        name: 'Author',
        passwordHash: 'hashed',
        posts: {
          create: [
            { title: 'Post 1', content: 'Content 1' },
            { title: 'Post 2', content: 'Content 2' },
          ],
        },
      },
      include: {
        posts: true,
      },
    });

    expect(user.posts).toHaveLength(2);
    expect(user.posts[0].authorId).toBe(user.id);
  });

  it('should handle transactions', async () => {
    await expect(
      prisma.$transaction(async (tx) => {
        await tx.user.create({
          data: {
            email: 'user1@example.com',
            name: 'User 1',
            passwordHash: 'hashed',
          },
        });

        // This will fail due to duplicate email
        await tx.user.create({
          data: {
            email: 'user1@example.com',
            name: 'User 2',
            passwordHash: 'hashed',
          },
        });
      })
    ).rejects.toThrow();

    // Verify rollback - no users should exist
    const count = await prisma.user.count();
    expect(count).toBe(0);
  });
});
```

## E2E Testing

### Complete Playwright Setup

**playwright.config.ts**:
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI
    ? [['github'], ['html']]
    : [['list'], ['html']],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },

    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },

    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Authentication Setup

**e2e/auth.setup.ts**:
```typescript
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');

  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.waitForURL('/dashboard');

  // Save authenticated state
  await page.context().storageState({ path: authFile });
});
```

### Complete E2E Test Suite

**e2e/checkout.spec.ts**:
```typescript
import { test, expect } from '@playwright/test';

test.use({ storageState: '.auth/user.json' });

test.describe('Checkout Flow', () => {
  test('should complete full checkout process', async ({ page }) => {
    // Add item to cart
    await page.goto('/products');
    await page.click('[data-testid="product-1"]');
    await page.click('[data-testid="add-to-cart"]');

    await expect(page.locator('[data-testid="cart-count"]')).toHaveText('1');

    // Go to cart
    await page.click('[data-testid="cart-button"]');
    await expect(page).toHaveURL('/cart');

    // Verify cart contents
    const cartItem = page.locator('[data-testid="cart-item"]');
    await expect(cartItem).toBeVisible();
    await expect(cartItem.locator('[data-testid="item-name"]')).toHaveText(
      'Product 1'
    );

    // Proceed to checkout
    await page.click('[data-testid="checkout-button"]');
    await expect(page).toHaveURL('/checkout');

    // Fill shipping information
    await page.fill('[name="address"]', '123 Main St');
    await page.fill('[name="city"]', 'New York');
    await page.fill('[name="zipCode"]', '10001');
    await page.click('button[type="submit"]');

    // Fill payment information
    await page.fill('[name="cardNumber"]', '4242424242424242');
    await page.fill('[name="expiry"]', '12/25');
    await page.fill('[name="cvc"]', '123');

    // Submit order
    await page.click('[data-testid="place-order"]');

    // Verify order confirmation
    await expect(page).toHaveURL(/\/order\/[a-z0-9-]+/);
    await expect(page.locator('h1')).toContainText('Order Confirmed');
    await expect(page.locator('[data-testid="order-number"]')).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/checkout');

    await page.click('button[type="submit"]');

    await expect(page.locator('[data-testid="error-address"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-city"]')).toBeVisible();
  });

  test('should handle payment failure', async ({ page }) => {
    await page.goto('/checkout');

    // Fill valid shipping
    await page.fill('[name="address"]', '123 Main St');
    await page.fill('[name="city"]', 'New York');
    await page.fill('[name="zipCode"]', '10001');
    await page.click('button[type="submit"]');

    // Use card that will be declined
    await page.fill('[name="cardNumber"]', '4000000000000002');
    await page.fill('[name="expiry"]', '12/25');
    await page.fill('[name="cvc"]', '123');

    await page.click('[data-testid="place-order"]');

    await expect(page.locator('[role="alert"]')).toContainText(
      'Payment declined'
    );
  });
});
```

## Advanced Testing Patterns

### Testing with MSW (Mock Service Worker)

```typescript
// test/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: '1', name: 'John Doe', email: 'john@example.com' },
        { id: '2', name: 'Jane Doe', email: 'jane@example.com' },
      ])
    );
  }),

  rest.post('/api/users', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({
        id: '3',
        ...body,
      })
    );
  }),

  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;

    if (id === '404') {
      return res(ctx.status(404), ctx.json({ error: 'Not found' }));
    }

    return res(
      ctx.json({
        id,
        name: 'John Doe',
        email: 'john@example.com',
      })
    );
  }),
];

// test/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// test/setup.ts
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Best Practices

### 1. Test Naming

```typescript
// Good
describe('UserService.createUser', () => {
  it('should create user when email is unique', () => {});
  it('should throw error when email already exists', () => {});
  it('should hash password before saving', () => {});
});

// Bad
describe('createUser', () => {
  it('works', () => {});
  it('test 2', () => {});
});
```

### 2. Test Organization

```
test/
├── unit/
│   ├── services/
│   ├── utils/
│   └── models/
├── integration/
│   ├── api/
│   └── database/
├── e2e/
│   ├── auth/
│   ├── checkout/
│   └── admin/
├── mocks/
│   ├── handlers.ts
│   └── server.ts
└── setup.ts
```

### 3. Test Data Builders

```typescript
// test/builders/user.builder.ts
export class UserBuilder {
  private data = {
    email: 'test@example.com',
    name: 'Test User',
    password: 'password123',
  };

  withEmail(email: string) {
    this.data.email = email;
    return this;
  }

  withName(name: string) {
    this.data.name = name;
    return this;
  }

  build() {
    return this.data;
  }
}

// Usage
const user = new UserBuilder()
  .withEmail('john@example.com')
  .withName('John Doe')
  .build();
```

### 4. Shared Test Utilities

```typescript
// test/utils/api.ts
export async function createTestUser(data?: Partial<User>) {
  return await prisma.user.create({
    data: {
      email: 'test@example.com',
      name: 'Test User',
      passwordHash: await hash('password123'),
      ...data,
    },
  });
}

export async function createAuthenticatedRequest(user: User) {
  const token = generateToken(user.id);
  return request(app).set('Authorization', `Bearer ${token}`);
}
```

## Conclusion

A comprehensive testing strategy:
- Catches bugs early in development
- Enables confident refactoring
- Documents expected behavior
- Improves code quality
- Reduces production incidents

Start with the most critical paths and expand coverage over time. Aim for 80%+ coverage but prioritize quality over quantity.
