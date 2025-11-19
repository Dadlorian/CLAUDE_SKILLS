# Full-Stack TypeScript Project Template
## Production-Ready Project Structure

---

## 🎯 Overview

This template provides a **battle-tested project structure** for full-stack TypeScript applications, based on best practices from successful production systems.

**Tech Stack**:
- **Frontend**: React + TypeScript + Next.js
- **Backend**: Node.js + Express + TypeScript
- **Database**: PostgreSQL with Prisma ORM
- **Testing**: Vitest + Playwright
- **DevOps**: Docker + GitHub Actions

---

## 📁 Project Structure

```
my-app/
├── .github/                          # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml                   # Continuous Integration
│   │   ├── deploy-staging.yml       # Staging deployment
│   │   └── deploy-production.yml    # Production deployment
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── apps/                             # Applications (monorepo)
│   ├── web/                         # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/                # App router (Next.js 13+)
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx
│   │   │   │   └── api/           # API routes
│   │   │   ├── components/        # React components
│   │   │   │   ├── ui/           # Reusable UI components
│   │   │   │   ├── features/     # Feature-specific components
│   │   │   │   └── layouts/      # Layout components
│   │   │   ├── hooks/            # Custom React hooks
│   │   │   ├── lib/              # Utilities and helpers
│   │   │   ├── styles/           # Global styles
│   │   │   └── types/            # TypeScript types
│   │   ├── public/               # Static assets
│   │   ├── tests/
│   │   │   ├── unit/            # Unit tests
│   │   │   ├── integration/     # Integration tests
│   │   │   └── e2e/             # E2E tests (Playwright)
│   │   ├── .env.example
│   │   ├── next.config.js
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vitest.config.ts
│   │
│   └── api/                         # Express backend
│       ├── src/
│       │   ├── controllers/        # Route controllers
│       │   │   ├── user.controller.ts
│       │   │   └── auth.controller.ts
│       │   ├── middleware/         # Express middleware
│       │   │   ├── auth.middleware.ts
│       │   │   ├── error.middleware.ts
│       │   │   └── validation.middleware.ts
│       │   ├── routes/             # Route definitions
│       │   │   ├── user.routes.ts
│       │   │   └── auth.routes.ts
│       │   ├── services/           # Business logic
│       │   │   ├── user.service.ts
│       │   │   └── auth.service.ts
│       │   ├── repositories/       # Data access layer
│       │   │   └── user.repository.ts
│       │   ├── models/             # Data models
│       │   │   └── user.model.ts
│       │   ├── utils/              # Utility functions
│       │   │   ├── logger.ts
│       │   │   ├── errors.ts
│       │   │   └── validators.ts
│       │   ├── config/             # Configuration
│       │   │   ├── database.ts
│       │   │   └── env.ts
│       │   ├── types/              # TypeScript types
│       │   │   └── express.d.ts
│       │   ├── app.ts              # Express app setup
│       │   └── server.ts           # Server entry point
│       ├── tests/
│       │   ├── unit/              # Unit tests
│       │   ├── integration/       # Integration tests
│       │   └── fixtures/          # Test data
│       ├── prisma/
│       │   ├── schema.prisma      # Database schema
│       │   ├── migrations/        # DB migrations
│       │   └── seed.ts            # Database seed
│       ├── .env.example
│       ├── package.json
│       ├── tsconfig.json
│       └── vitest.config.ts
│
├── packages/                         # Shared packages
│   ├── shared/                      # Shared code
│   │   ├── src/
│   │   │   ├── types/             # Shared TypeScript types
│   │   │   ├── utils/             # Shared utilities
│   │   │   └── constants/         # Shared constants
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── config/                      # Shared configurations
│   │   ├── eslint-config/         # Shared ESLint config
│   │   ├── typescript-config/     # Shared TS config
│   │   └── vitest-config/         # Shared test config
│   │
│   └── ui/                          # Shared UI components
│       ├── src/
│       │   └── components/
│       ├── package.json
│       └── tsconfig.json
│
├── docker/                           # Docker configuration
│   ├── api/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── web/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── docker-compose.yml
│
├── docs/                             # Documentation
│   ├── architecture/
│   │   ├── decisions/             # ADRs
│   │   └── diagrams/              # Architecture diagrams
│   ├── api/                       # API documentation
│   ├── deployment/                # Deployment guides
│   └── development/               # Development guides
│
├── scripts/                          # Utility scripts
│   ├── setup.sh                   # Initial project setup
│   ├── db-migrate.sh              # Database migration
│   ├── seed-db.sh                 # Seed database
│   └── deploy.sh                  # Deployment script
│
├── .gitignore
├── .nvmrc                           # Node version
├── package.json                     # Root package.json (monorepo)
├── turbo.json                       # Turborepo config (if using)
├── README.md
└── LICENSE

```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Required
Node.js >= 20.0.0
PostgreSQL >= 14
Docker (optional, for containerization)

# Check versions
node --version
npm --version
psql --version
```

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/org/my-app.git
cd my-app

# 2. Install dependencies
npm install

# 3. Copy environment variables
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env

# 4. Configure environment variables
# Edit apps/api/.env and apps/web/.env

# 5. Setup database
npm run db:migrate
npm run db:seed

# 6. Run development servers
npm run dev
```

### Environment Variables

**apps/api/.env**:
```bash
# Application
NODE_ENV=development
PORT=3001
API_URL=http://localhost:3001

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/myapp"

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_EXPIRES_IN=7d
REFRESH_TOKEN_SECRET=your-refresh-token-secret

# External Services
STRIPE_SECRET_KEY=sk_test_...
SENDGRID_API_KEY=SG...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_S3_BUCKET=my-app-uploads

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=debug
```

**apps/web/.env.local**:
```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:3001

# Analytics
NEXT_PUBLIC_GA_ID=G-...

# Feature Flags
NEXT_PUBLIC_ENABLE_BETA_FEATURES=true

# External Services
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## 🏗️ Architecture

### Backend Architecture (Layered)

```
┌─────────────────────────────────────────┐
│  Routes (HTTP endpoints)                │
│  - Define API endpoints                 │
│  - Input validation                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Controllers (Request/Response)         │
│  - Handle HTTP requests                 │
│  - Call services                        │
│  - Return responses                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Services (Business Logic)              │
│  - Core business logic                  │
│  - Orchestrate operations               │
│  - Call repositories                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Repositories (Data Access)             │
│  - Database queries                     │
│  - Data mapping                         │
│  - Prisma ORM                           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Database (PostgreSQL)                  │
└─────────────────────────────────────────┘
```

### Frontend Architecture (Feature-Based)

```
app/
├── (auth)/              # Auth-related routes
│   ├── login/
│   └── register/
├── dashboard/           # Dashboard routes
│   ├── page.tsx
│   └── layout.tsx
└── api/                # API routes

components/
├── ui/                 # Base UI components
│   ├── Button/
│   ├── Input/
│   └── Modal/
├── features/           # Feature-specific
│   ├── auth/
│   ├── dashboard/
│   └── profile/
└── layouts/            # Layouts
    ├── MainLayout/
    └── AuthLayout/
```

---

## 📝 Code Examples

### Backend Controller

```typescript
// apps/api/src/controllers/user.controller.ts
import { Request, Response, NextFunction } from 'express';
import { userService } from '../services/user.service';
import { AppError } from '../utils/errors';

export const userController = {
  async getUser(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const user = await userService.getUserById(id);

      if (!user) {
        throw new AppError('User not found', 404);
      }

      res.json({ data: user });
    } catch (error) {
      next(error);
    }
  },

  async updateUser(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const updateData = req.body;

      const user = await userService.updateUser(id, updateData);

      res.json({ data: user });
    } catch (error) {
      next(error);
    }
  },
};
```

### Backend Service

```typescript
// apps/api/src/services/user.service.ts
import { userRepository } from '../repositories/user.repository';
import { AppError } from '../utils/errors';
import type { User, UpdateUserDto } from '../types/user.types';

export const userService = {
  async getUserById(id: string): Promise<User | null> {
    return userRepository.findById(id);
  },

  async updateUser(id: string, data: UpdateUserDto): Promise<User> {
    // Validate data
    if (data.email) {
      const existingUser = await userRepository.findByEmail(data.email);
      if (existingUser && existingUser.id !== id) {
        throw new AppError('Email already in use', 400);
      }
    }

    // Update user
    const user = await userRepository.update(id, data);

    if (!user) {
      throw new AppError('User not found', 404);
    }

    return user;
  },
};
```

### Frontend Component

```typescript
// apps/web/src/components/features/profile/ProfileForm.tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useUser } from '@/hooks/useUser';

export function ProfileForm() {
  const { user, updateUser, isLoading } = useUser();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateUser(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />

      <Input
        label="Email"
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
      />

      <Button type="submit" loading={isLoading}>
        Save Changes
      </Button>
    </form>
  );
}
```

---

## 🧪 Testing

### Unit Test Example

```typescript
// apps/api/tests/unit/services/user.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { userService } from '../../../src/services/user.service';
import { userRepository } from '../../../src/repositories/user.repository';

vi.mock('../../../src/repositories/user.repository');

describe('UserService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getUserById', () => {
    it('should return user when found', async () => {
      const mockUser = { id: '1', email: 'test@example.com', name: 'Test' };
      vi.mocked(userRepository.findById).mockResolvedValue(mockUser);

      const user = await userService.getUserById('1');

      expect(user).toEqual(mockUser);
      expect(userRepository.findById).toHaveBeenCalledWith('1');
    });

    it('should return null when user not found', async () => {
      vi.mocked(userRepository.findById).mockResolvedValue(null);

      const user = await userService.getUserById('999');

      expect(user).toBeNull();
    });
  });
});
```

### E2E Test Example

```typescript
// apps/web/tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should allow user to login', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[name="email"]', 'wrong@example.com');
    await page.fill('[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error')).toContainText('Invalid credentials');
  });
});
```

---

## 🐳 Docker

### Docker Compose

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build:
      context: ..
      dockerfile: docker/api/Dockerfile
    ports:
      - "3001:3001"
    environment:
      DATABASE_URL: postgresql://myapp:password@postgres:5432/myapp
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  web:
    build:
      context: ..
      dockerfile: docker/web/Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:3001
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## 📊 Package Scripts

```json
{
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "test:e2e": "turbo run test:e2e",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "db:migrate": "cd apps/api && npx prisma migrate dev",
    "db:seed": "cd apps/api && npx prisma db seed",
    "db:studio": "cd apps/api && npx prisma studio",
    "docker:up": "docker-compose -f docker/docker-compose.yml up",
    "docker:down": "docker-compose -f docker/docker-compose.yml down",
    "clean": "turbo run clean && rm -rf node_modules"
  }
}
```

---

## 🎓 Best Practices

### Code Organization

1. **Feature-based structure** for frontend
2. **Layered architecture** for backend
3. **Shared code** in packages
4. **Separation of concerns** (controllers, services, repositories)

### Type Safety

1. **Shared types** between frontend and backend
2. **Strict TypeScript** configuration
3. **Zod** for runtime validation
4. **Prisma** for type-safe database access

### Testing

1. **Unit tests** for services and utilities
2. **Integration tests** for API endpoints
3. **E2E tests** for critical user flows
4. **80%+ code coverage**

### Security

1. **Environment variables** for secrets
2. **Input validation** on all endpoints
3. **Authentication middleware**
4. **HTTPS only** in production
5. **Security headers** (helmet)

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**License**: MIT
