# Monorepo Setup Guide with Turborepo

Complete guide to setting up and managing a monorepo for full-stack applications using Turborepo.

## Why Monorepos?

**Benefits**:
- Share code easily between apps
- Consistent tooling and dependencies
- Atomic commits across projects
- Easier refactoring
- Better code reuse

**When to use**:
- Multiple related applications (web, mobile, admin)
- Shared component libraries
- Microservices architecture
- Teams working on interconnected projects

## Initial Setup

### Create Monorepo

```bash
# Using Turborepo starter
npx create-turbo@latest my-monorepo

# Or start from scratch
mkdir my-monorepo && cd my-monorepo
npm init -y
npm install turbo --save-dev
```

### Directory Structure

```
my-monorepo/
├── apps/
│   ├── web/                 # Next.js app
│   ├── mobile/              # React Native app
│   ├── admin/               # Admin dashboard
│   └── api/                 # Backend API
├── packages/
│   ├── ui/                  # Shared UI components
│   ├── database/            # Prisma client
│   ├── auth/                # Authentication logic
│   ├── utils/               # Shared utilities
│   ├── typescript-config/   # Shared TS configs
│   └── eslint-config/       # Shared ESLint configs
├── turbo.json              # Turborepo configuration
├── package.json            # Root package.json
└── .gitignore
```

## Configure Turborepo

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "lint": {
      "outputs": []
    },
    "type-check": {
      "dependsOn": ["^type-check"],
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "db:generate": {
      "cache": false
    },
    "db:push": {
      "cache": false
    }
  }
}
```

### Root package.json

```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules",
    "format": "prettier --write \"**/*.{ts,tsx,md}\""
  },
  "devDependencies": {
    "turbo": "latest",
    "prettier": "^3.1.0",
    "typescript": "^5.3.0"
  }
}
```

## Shared Packages

### UI Component Library

**packages/ui/package.json**:
```json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.tsx",
  "types": "./src/index.tsx",
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "type-check": "tsc --noEmit"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@repo/typescript-config": "*",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0"
  }
}
```

**packages/ui/src/Button.tsx**:
```typescript
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = 'rounded font-medium transition-colors';

  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

**packages/ui/src/index.tsx**:
```typescript
export { Button } from './Button';
export { Card } from './Card';
export { Input } from './Input';
export { Modal } from './Modal';
```

### Database Package

**packages/database/package.json**:
```json
{
  "name": "@repo/database",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "db:generate": "prisma generate",
    "db:push": "prisma db push --skip-generate",
    "db:migrate": "prisma migrate dev",
    "db:studio": "prisma studio",
    "db:seed": "tsx prisma/seed.ts"
  },
  "dependencies": {
    "@prisma/client": "^5.7.0"
  },
  "devDependencies": {
    "prisma": "^5.7.0",
    "tsx": "^4.7.0"
  }
}
```

**packages/database/src/index.ts**:
```typescript
import { PrismaClient } from '@prisma/client';

declare global {
  var __prisma: PrismaClient | undefined;
}

export const prisma = global.__prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development'
    ? ['query', 'error', 'warn']
    : ['error'],
});

if (process.env.NODE_ENV !== 'production') {
  global.__prisma = prisma;
}

export * from '@prisma/client';
```

### Auth Package

**packages/auth/package.json**:
```json
{
  "name": "@repo/auth",
  "version": "0.0.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "dependencies": {
    "bcrypt": "^5.1.1",
    "jsonwebtoken": "^9.0.2"
  },
  "devDependencies": {
    "@types/bcrypt": "^5.0.2",
    "@types/jsonwebtoken": "^9.0.5"
  }
}
```

**packages/auth/src/index.ts**:
```typescript
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const SALT_ROUNDS = 10;

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

export function generateToken(payload: object, expiresIn = '7d'): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn });
}

export function verifyToken<T = any>(token: string): T {
  return jwt.verify(token, JWT_SECRET) as T;
}

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}
```

### TypeScript Config Package

**packages/typescript-config/base.json**:
```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "display": "Base",
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "commonjs",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "allowJs": true,
    "checkJs": false,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "incremental": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "skipLibCheck": true
  },
  "exclude": ["node_modules"]
}
```

**packages/typescript-config/nextjs.json**:
```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "display": "Next.js",
  "extends": "./base.json",
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "plugins": [{ "name": "next" }],
    "isolatedModules": true,
    "noEmit": true,
    "allowImportingTsExtensions": true
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### ESLint Config Package

**packages/eslint-config/package.json**:
```json
{
  "name": "@repo/eslint-config",
  "version": "0.0.0",
  "private": true,
  "main": "./index.js",
  "dependencies": {
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-import": "^2.28.0",
    "eslint-plugin-jsx-a11y": "^6.7.0",
    "eslint-plugin-react": "^7.33.0",
    "eslint-plugin-react-hooks": "^4.6.0"
  }
}
```

**packages/eslint-config/index.js**:
```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react', 'react-hooks', 'jsx-a11y', 'import'],
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'import/order': [
      'error',
      {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
        'newlines-between': 'always',
        alphabetize: { order: 'asc' },
      },
    ],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

## Apps Configuration

### Next.js App

**apps/web/package.json**:
```json
{
  "name": "web",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@repo/ui": "*",
    "@repo/database": "*",
    "@repo/auth": "*"
  },
  "devDependencies": {
    "@repo/typescript-config": "*",
    "@repo/eslint-config": "*",
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "eslint": "^8.0.0"
  }
}
```

**apps/web/tsconfig.json**:
```json
{
  "extends": "@repo/typescript-config/nextjs.json",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Express API App

**apps/api/package.json**:
```json
{
  "name": "api",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "lint": "eslint . --max-warnings 0",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "morgan": "^1.10.0",
    "zod": "^3.22.0",
    "@repo/database": "*",
    "@repo/auth": "*"
  },
  "devDependencies": {
    "@repo/typescript-config": "*",
    "@repo/eslint-config": "*",
    "@types/express": "^4.17.0",
    "@types/cors": "^2.8.0",
    "@types/morgan": "^1.9.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.0"
  }
}
```

## Development Workflow

### Running Apps in Development

```bash
# Run all apps
npm run dev

# Run specific app
npm run dev --filter=web

# Run multiple specific apps
npm run dev --filter=web --filter=api
```

### Building

```bash
# Build all apps
npm run build

# Build specific app
npm run build --filter=web

# Build with dependencies
npm run build --filter=web...
```

### Testing

```bash
# Run all tests
npm run test

# Run tests for changed code only
npm run test -- --affected

# Run tests for specific package
npm run test --filter=@repo/ui
```

## Advanced Features

### Remote Caching

**Enable Vercel Remote Caching**:
```bash
# Login to Vercel
npx turbo login

# Link repository
npx turbo link
```

**turbo.json** with remote caching:
```json
{
  "remoteCache": {
    "signature": true
  }
}
```

### Task Dependencies

```json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "deploy": {
      "dependsOn": ["build", "test"],
      "outputs": []
    }
  }
}
```

### Environment Variables

**apps/web/.env.local**:
```bash
DATABASE_URL="postgresql://..."
NEXT_PUBLIC_API_URL="http://localhost:3001"
```

**apps/api/.env.local**:
```bash
DATABASE_URL="postgresql://..."
JWT_SECRET="your-secret-key"
PORT=3001
```

### Code Generation

**packages/database/package.json**:
```json
{
  "scripts": {
    "postinstall": "prisma generate"
  }
}
```

## CI/CD Integration

### GitHub Actions

**.github/workflows/ci.yml**:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run test

  build:
    runs-on: ubuntu-latest
    needs: [lint, type-check, test]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - name: Cache turbo build
        uses: actions/cache@v3
        with:
          path: .turbo
          key: ${{ runner.os }}-turbo-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-turbo-
```

## Best Practices

### Package Naming

- Use scoped packages: `@repo/ui`, `@mycompany/shared`
- Keep names short and descriptive
- Use consistent naming conventions

### Version Management

- Keep all packages at version `0.0.0`
- Mark all as `"private": true`
- Update root dependencies regularly

### Dependencies

- Put shared dependencies in root `package.json`
- Use workspace protocol: `"@repo/ui": "*"`
- Avoid duplicate dependencies

### Code Sharing

1. **Extract common code** early
2. **Create focused packages** (single responsibility)
3. **Document public APIs**
4. **Version internal packages** if needed

### Performance

1. **Use caching** aggressively
2. **Minimize task dependencies**
3. **Enable remote caching** for teams
4. **Parallelize independent tasks**

### Organization

1. **Group related apps** in folders
2. **Separate concerns** (ui, logic, data)
3. **Use consistent structure** across packages
4. **Document architecture** decisions

## Troubleshooting

### Common Issues

**Dependency issues**:
```bash
# Clear all node_modules
npm run clean
npm install
```

**Type errors**:
```bash
# Regenerate types
npm run db:generate
npm run type-check
```

**Cache issues**:
```bash
# Clear turbo cache
rm -rf .turbo
npm run build
```

## Conclusion

Monorepos with Turborepo provide:
- Faster builds with caching
- Better code sharing
- Consistent tooling
- Simplified dependency management
- Improved developer experience

Start small and grow your monorepo as needed. Don't prematurely optimize - add packages when you have actual code to share.
