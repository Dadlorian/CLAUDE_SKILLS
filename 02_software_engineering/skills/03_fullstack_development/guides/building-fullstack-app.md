# Building a Full-Stack Application: Complete Guide

This guide walks through building a production-ready full-stack application from scratch using modern tools and best practices.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Database Design](#database-design)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Authentication](#authentication)
6. [Deployment](#deployment)

## Project Setup

### Initialize Monorepo with Turborepo

```bash
# Create new project
npx create-turbo@latest my-fullstack-app
cd my-fullstack-app

# Install dependencies
npm install

# Project structure
my-fullstack-app/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # Express.js backend
├── packages/
│   ├── ui/               # Shared UI components
│   ├── database/         # Prisma client
│   ├── typescript-config/
│   └── eslint-config/
├── turbo.json
└── package.json
```

### Configure TypeScript

**packages/typescript-config/base.json**:
```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "display": "Default",
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "esModuleInterop": true,
    "incremental": false,
    "isolatedModules": true,
    "lib": ["es2022"],
    "module": "commonjs",
    "moduleResolution": "node",
    "noUncheckedIndexedAccess": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "strict": true,
    "target": "es2022"
  },
  "exclude": ["node_modules"]
}
```

## Database Design

### Design Schema with Prisma

**packages/database/prisma/schema.prisma**:
```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  name          String?
  passwordHash  String
  role          Role      @default(USER)
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
  posts         Post[]
  comments      Comment[]
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?
  user              User    @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Post {
  id        String    @id @default(cuid())
  title     String
  slug      String    @unique
  content   String
  excerpt   String?
  published Boolean   @default(false)
  author    User      @relation(fields: [authorId], references: [id])
  authorId  String
  comments  Comment[]
  tags      Tag[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt

  @@index([authorId])
  @@index([published])
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  post      Post     @relation(fields: [postId], references: [id], onDelete: Cascade)
  postId    String
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([postId])
  @@index([authorId])
}

model Tag {
  id    String @id @default(cuid())
  name  String @unique
  posts Post[]
}

enum Role {
  USER
  ADMIN
  EDITOR
}
```

### Setup Database Package

**packages/database/src/index.ts**:
```typescript
import { PrismaClient } from '@prisma/client';

declare global {
  var prisma: PrismaClient | undefined;
}

export const prisma = global.prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma;
}

export * from '@prisma/client';
```

**packages/database/package.json**:
```json
{
  "name": "@repo/database",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "db:generate": "prisma generate",
    "db:push": "prisma db push",
    "db:migrate": "prisma migrate dev",
    "db:studio": "prisma studio"
  },
  "dependencies": {
    "@prisma/client": "^5.7.0"
  },
  "devDependencies": {
    "prisma": "^5.7.0"
  }
}
```

## Backend Development

### Setup Express API

**apps/api/src/index.ts**:
```typescript
import express, { type Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { prisma } from '@repo/database';
import authRoutes from './routes/auth';
import postRoutes from './routes/posts';
import userRoutes from './routes/users';
import { errorHandler } from './middleware/errorHandler';
import { authenticate } from './middleware/auth';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/posts', authenticate, postRoutes);
app.use('/api/users', authenticate, userRoutes);

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  await prisma.$disconnect();
  process.exit(0);
});
```

### Error Handling Middleware

**apps/api/src/middleware/errorHandler.ts**:
```typescript
import { Request, Response, NextFunction } from 'express';
import { Prisma } from '@prisma/client';

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: 'error',
      message: err.message,
    });
  }

  if (err instanceof Prisma.PrismaClientKnownRequestError) {
    if (err.code === 'P2002') {
      return res.status(409).json({
        status: 'error',
        message: 'A record with this value already exists',
      });
    }
    if (err.code === 'P2025') {
      return res.status(404).json({
        status: 'error',
        message: 'Record not found',
      });
    }
  }

  console.error('Unhandled error:', err);

  return res.status(500).json({
    status: 'error',
    message: 'Internal server error',
  });
};
```

### Authentication Middleware

**apps/api/src/middleware/auth.ts**:
```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { prisma } from '@repo/database';
import { AppError } from './errorHandler';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader?.startsWith('Bearer ')) {
      throw new AppError(401, 'No token provided');
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, JWT_SECRET) as { userId: string };

    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
      select: { id: true, email: true, role: true },
    });

    if (!user) {
      throw new AppError(401, 'Invalid token');
    }

    req.user = user;
    next();
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      return next(new AppError(401, 'Invalid token'));
    }
    next(error);
  }
};

export const authorize = (...roles: string[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return next(new AppError(401, 'Not authenticated'));
    }

    if (!roles.includes(req.user.role)) {
      return next(new AppError(403, 'Insufficient permissions'));
    }

    next();
  };
};
```

### Post Routes

**apps/api/src/routes/posts.ts**:
```typescript
import { Router } from 'express';
import { z } from 'zod';
import { prisma } from '@repo/database';
import { AppError } from '../middleware/errorHandler';
import { authorize, type AuthRequest } from '../middleware/auth';

const router = Router();

// Validation schemas
const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  excerpt: z.string().max(300).optional(),
  published: z.boolean().default(false),
  tags: z.array(z.string()).optional(),
});

const updatePostSchema = createPostSchema.partial();

// Get all posts
router.get('/', async (req: AuthRequest, res, next) => {
  try {
    const { published, authorId, tag, page = 1, limit = 10 } = req.query;

    const where: any = {};
    if (published) where.published = published === 'true';
    if (authorId) where.authorId = authorId;
    if (tag) where.tags = { some: { name: tag as string } };

    const skip = (Number(page) - 1) * Number(limit);

    const [posts, total] = await Promise.all([
      prisma.post.findMany({
        where,
        include: {
          author: { select: { id: true, name: true, email: true } },
          tags: true,
          _count: { select: { comments: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: Number(limit),
      }),
      prisma.post.count({ where }),
    ]);

    res.json({
      data: posts,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        pages: Math.ceil(total / Number(limit)),
      },
    });
  } catch (error) {
    next(error);
  }
});

// Get single post
router.get('/:id', async (req, res, next) => {
  try {
    const post = await prisma.post.findUnique({
      where: { id: req.params.id },
      include: {
        author: { select: { id: true, name: true, email: true } },
        tags: true,
        comments: {
          include: {
            author: { select: { id: true, name: true } },
          },
          orderBy: { createdAt: 'desc' },
        },
      },
    });

    if (!post) {
      throw new AppError(404, 'Post not found');
    }

    res.json(post);
  } catch (error) {
    next(error);
  }
});

// Create post
router.post('/', async (req: AuthRequest, res, next) => {
  try {
    const data = createPostSchema.parse(req.body);
    const userId = req.user!.id;

    const slug = data.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');

    const post = await prisma.post.create({
      data: {
        ...data,
        slug,
        author: { connect: { id: userId } },
        tags: data.tags ? {
          connectOrCreate: data.tags.map(name => ({
            where: { name },
            create: { name },
          })),
        } : undefined,
      },
      include: {
        author: { select: { id: true, name: true, email: true } },
        tags: true,
      },
    });

    res.status(201).json(post);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    next(error);
  }
});

// Update post
router.patch('/:id', async (req: AuthRequest, res, next) => {
  try {
    const data = updatePostSchema.parse(req.body);
    const userId = req.user!.id;
    const postId = req.params.id;

    // Check ownership
    const existingPost = await prisma.post.findUnique({
      where: { id: postId },
      select: { authorId: true },
    });

    if (!existingPost) {
      throw new AppError(404, 'Post not found');
    }

    if (existingPost.authorId !== userId && req.user!.role !== 'ADMIN') {
      throw new AppError(403, 'Not authorized to update this post');
    }

    const post = await prisma.post.update({
      where: { id: postId },
      data: {
        ...data,
        tags: data.tags ? {
          set: [],
          connectOrCreate: data.tags.map(name => ({
            where: { name },
            create: { name },
          })),
        } : undefined,
      },
      include: {
        author: { select: { id: true, name: true, email: true } },
        tags: true,
      },
    });

    res.json(post);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    next(error);
  }
});

// Delete post
router.delete('/:id', authorize('ADMIN', 'EDITOR'), async (req: AuthRequest, res, next) => {
  try {
    const userId = req.user!.id;
    const postId = req.params.id;

    const existingPost = await prisma.post.findUnique({
      where: { id: postId },
      select: { authorId: true },
    });

    if (!existingPost) {
      throw new AppError(404, 'Post not found');
    }

    if (existingPost.authorId !== userId && req.user!.role !== 'ADMIN') {
      throw new AppError(403, 'Not authorized to delete this post');
    }

    await prisma.post.delete({
      where: { id: postId },
    });

    res.status(204).send();
  } catch (error) {
    next(error);
  }
});

export default router;
```

## Frontend Development

### Setup Next.js App

**apps/web/app/layout.tsx**:
```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Navigation } from '@/components/Navigation';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'My Full-Stack App',
  description: 'Built with Next.js, Express, and Prisma',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <Navigation />
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
```

### API Client with React Query

**apps/web/lib/api.ts**:
```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const postsApi = {
  getAll: (params?: { published?: boolean; page?: number; limit?: number }) =>
    api.get('/posts', { params }),

  getById: (id: string) =>
    api.get(`/posts/${id}`),

  create: (data: { title: string; content: string; published?: boolean }) =>
    api.post('/posts', data),

  update: (id: string, data: Partial<{ title: string; content: string }>) =>
    api.patch(`/posts/${id}`, data),

  delete: (id: string) =>
    api.delete(`/posts/${id}`),
};

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: { email: string; password: string; name?: string }) =>
    api.post('/auth/register', data),

  me: () =>
    api.get('/auth/me'),
};
```

### React Query Setup

**apps/web/app/providers.tsx**:
```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Post List Component

**apps/web/components/PostList.tsx**:
```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { postsApi } from '@/lib/api';
import { PostCard } from './PostCard';
import { Pagination } from './Pagination';
import { useState } from 'react';

export function PostList() {
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data, isLoading, error } = useQuery({
    queryKey: ['posts', { page, limit, published: true }],
    queryFn: () => postsApi.getAll({ page, limit, published: true }),
  });

  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-48 bg-gray-200 rounded-lg" />
            <div className="h-4 bg-gray-200 rounded mt-4" />
            <div className="h-4 bg-gray-200 rounded mt-2 w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load posts</p>
      </div>
    );
  }

  const posts = data?.data.data || [];
  const pagination = data?.data.pagination;

  return (
    <div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {pagination && pagination.pages > 1 && (
        <Pagination
          currentPage={pagination.page}
          totalPages={pagination.pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
```

## Authentication

### JWT Implementation

**apps/api/src/routes/auth.ts**:
```typescript
import { Router } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { prisma } from '@repo/database';
import { AppError } from '../middleware/errorHandler';

const router = Router();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(2).optional(),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

// Register
router.post('/register', async (req, res, next) => {
  try {
    const { email, password, name } = registerSchema.parse(req.body);

    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      throw new AppError(409, 'User already exists');
    }

    const passwordHash = await bcrypt.hash(password, 10);

    const user = await prisma.user.create({
      data: {
        email,
        passwordHash,
        name,
      },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
      },
    });

    const token = jwt.sign({ userId: user.id }, JWT_SECRET, {
      expiresIn: '7d',
    });

    res.status(201).json({
      user,
      token,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    next(error);
  }
});

// Login
router.post('/login', async (req, res, next) => {
  try {
    const { email, password } = loginSchema.parse(req.body);

    const user = await prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      throw new AppError(401, 'Invalid credentials');
    }

    const isValidPassword = await bcrypt.compare(password, user.passwordHash);

    if (!isValidPassword) {
      throw new AppError(401, 'Invalid credentials');
    }

    const token = jwt.sign({ userId: user.id }, JWT_SECRET, {
      expiresIn: '7d',
    });

    res.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      token,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    next(error);
  }
});

export default router;
```

## Deployment

### Docker Compose for Development

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: myapp
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Production Dockerfile

**apps/web/Dockerfile**:
```dockerfile
FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### CI/CD with GitHub Actions

**.github/workflows/deploy.yml**:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
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
      - run: npm run lint

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

## Best Practices

### Error Handling

1. **Always use try-catch** in async route handlers
2. **Create custom error classes** for different error types
3. **Centralized error handler** middleware
4. **Log errors** for debugging
5. **Never expose internal errors** to clients

### Security

1. **Validate all inputs** with Zod or similar
2. **Use parameterized queries** (Prisma handles this)
3. **Implement rate limiting** with express-rate-limit
4. **Use CORS properly** - don't allow all origins in production
5. **Hash passwords** with bcrypt (10+ rounds)
6. **Use HTTPS** in production
7. **Set security headers** with Helmet

### Performance

1. **Database indexes** on frequently queried fields
2. **Pagination** for large datasets
3. **Caching** with Redis for frequently accessed data
4. **Connection pooling** for database
5. **Code splitting** in frontend
6. **Image optimization** with next/image
7. **API response caching** with proper headers

### Testing

1. **Unit tests** for business logic
2. **Integration tests** for API endpoints
3. **E2E tests** with Playwright or Cypress
4. **Database mocking** with Prisma mock
5. **Test coverage** >80%

## Conclusion

This guide provides a solid foundation for building production-ready full-stack applications. Remember to:

- Keep your dependencies updated
- Monitor application performance
- Implement proper logging
- Set up error tracking (e.g., Sentry)
- Use environment variables for configuration
- Document your API with OpenAPI/Swagger
- Write comprehensive tests

Happy building!
