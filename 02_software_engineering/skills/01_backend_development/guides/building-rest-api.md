# Building a Production REST API - Complete Guide

This guide walks you through building a production-grade REST API from scratch using Node.js, Express, TypeScript, and PostgreSQL.

## Project Setup

```bash
mkdir my-api && cd my-api
npm init -y
npm install express cors helmet compression
npm install -D typescript @types/node @types/express ts-node nodemon
npm install pg dotenv zod winston
npm install -D @types/pg

npx tsc --init
```

## Project Structure

```
src/
├── config/
│   ├── database.ts
│   └── env.ts
├── middleware/
│   ├── auth.ts
│   ├── errorHandler.ts
│   └── validation.ts
├── modules/
│   └── users/
│       ├── user.controller.ts
│       ├── user.service.ts
│       ├── user.repository.ts
│       ├── user.model.ts
│       └── user.routes.ts
├── utils/
│   ├── logger.ts
│   └── errors.ts
├── app.ts
└── server.ts
```

## Step 1: Database Configuration

```typescript
// src/config/database.ts
import { Pool } from 'pg';

export const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  console.error('Unexpected database error', err);
  process.exit(-1);
});

export const query = (text: string, params?: any[]) => pool.query(text, params);
```

## Step 2: Models and Validation

```typescript
// src/modules/users/user.model.ts
import { z } from 'zod';

export const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  password: z.string().min(8),
});

export const UpdateUserSchema = z.object({
  email: z.string().email().optional(),
  name: z.string().min(1).max(100).optional(),
});

export type CreateUserDto = z.infer<typeof CreateUserSchema>;
export type UpdateUserDto = z.infer<typeof UpdateUserSchema>;

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: Date;
  updated_at: Date;
}
```

## Step 3: Repository Layer

```typescript
// src/modules/users/user.repository.ts
import { query } from '../../config/database';
import { User, CreateUserDto } from './user.model';

export class UserRepository {
  async findAll(): Promise<User[]> {
    const result = await query('SELECT id, email, name, created_at, updated_at FROM users ORDER BY created_at DESC');
    return result.rows;
  }

  async findById(id: string): Promise<User | null> {
    const result = await query(
      'SELECT id, email, name, created_at, updated_at FROM users WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const result = await query(
      'SELECT id, email, name, created_at, updated_at FROM users WHERE email = $1',
      [email]
    );
    return result.rows[0] || null;
  }

  async create(data: CreateUserDto & { passwordHash: string }): Promise<User> {
    const result = await query(
      'INSERT INTO users (email, name, password_hash) VALUES ($1, $2, $3) RETURNING id, email, name, created_at, updated_at',
      [data.email, data.name, data.passwordHash]
    );
    return result.rows[0];
  }

  async update(id: string, data: Partial<User>): Promise<User> {
    const fields = [];
    const values = [];
    let paramCount = 1;

    if (data.email) {
      fields.push(`email = $${paramCount++}`);
      values.push(data.email);
    }
    if (data.name) {
      fields.push(`name = $${paramCount++}`);
      values.push(data.name);
    }

    fields.push(`updated_at = NOW()`);
    values.push(id);

    const result = await query(
      `UPDATE users SET ${fields.join(', ')} WHERE id = $${paramCount} RETURNING id, email, name, created_at, updated_at`,
      values
    );
    return result.rows[0];
  }

  async delete(id: string): Promise<void> {
    await query('DELETE FROM users WHERE id = $1', [id]);
  }
}
```

## Step 4: Service Layer

```typescript
// src/modules/users/user.service.ts
import bcrypt from 'bcrypt';
import { UserRepository } from './user.repository';
import { CreateUserDto, UpdateUserDto } from './user.model';
import { ConflictError, NotFoundError } from '../../utils/errors';

export class UserService {
  constructor(private userRepository: UserRepository) {}

  async getAllUsers() {
    return this.userRepository.findAll();
  }

  async getUserById(id: string) {
    const user = await this.userRepository.findById(id);
    if (!user) {
      throw new NotFoundError('User not found');
    }
    return user;
  }

  async createUser(data: CreateUserDto) {
    const existing = await this.userRepository.findByEmail(data.email);
    if (existing) {
      throw new ConflictError('Email already exists');
    }

    const passwordHash = await bcrypt.hash(data.password, 12);
    return this.userRepository.create({ ...data, passwordHash });
  }

  async updateUser(id: string, data: UpdateUserDto) {
    await this.getUserById(id); // Check exists

    if (data.email) {
      const existing = await this.userRepository.findByEmail(data.email);
      if (existing && existing.id !== id) {
        throw new ConflictError('Email already exists');
      }
    }

    return this.userRepository.update(id, data);
  }

  async deleteUser(id: string) {
    await this.getUserById(id); // Check exists
    await this.userRepository.delete(id);
  }
}
```

## Step 5: Controller Layer

```typescript
// src/modules/users/user.controller.ts
import { Request, Response, NextFunction } from 'express';
import { UserService } from './user.service';
import { CreateUserSchema, UpdateUserSchema } from './user.model';

export class UserController {
  constructor(private userService: UserService) {}

  getAll = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const users = await this.userService.getAllUsers();
      res.json({ data: users });
    } catch (error) {
      next(error);
    }
  };

  getById = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const user = await this.userService.getUserById(req.params.id);
      res.json({ data: user });
    } catch (error) {
      next(error);
    }
  };

  create = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = CreateUserSchema.parse(req.body);
      const user = await this.userService.createUser(data);
      res.status(201).json({ data: user });
    } catch (error) {
      next(error);
    }
  };

  update = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = UpdateUserSchema.parse(req.body);
      const user = await this.userService.updateUser(req.params.id, data);
      res.json({ data: user });
    } catch (error) {
      next(error);
    }
  };

  delete = async (req: Request, res: Response, next: NextFunction) => {
    try {
      await this.userService.deleteUser(req.params.id);
      res.status(204).send();
    } catch (error) {
      next(error);
    }
  };
}
```

## Step 6: Routes

```typescript
// src/modules/users/user.routes.ts
import { Router } from 'express';
import { UserController } from './user.controller';
import { UserService } from './user.service';
import { UserRepository } from './user.repository';

const router = Router();
const userRepository = new UserRepository();
const userService = new UserService(userRepository);
const userController = new UserController(userService);

router.get('/', userController.getAll);
router.get('/:id', userController.getById);
router.post('/', userController.create);
router.patch('/:id', userController.update);
router.delete('/:id', userController.delete);

export default router;
```

## Step 7: Error Handling

```typescript
// src/utils/errors.ts
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

export class NotFoundError extends AppError {
  constructor(message: string) {
    super(404, message);
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(409, message);
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(400, message);
  }
}

// src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';
import { AppError } from '../utils/errors';
import { ZodError } from 'zod';
import { logger } from '../utils/logger';

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: {
        message: err.message,
        code: err.statusCode,
      },
    });
  }

  if (err instanceof ZodError) {
    return res.status(400).json({
      error: {
        message: 'Validation failed',
        details: err.errors,
      },
    });
  }

  logger.error('Unexpected error:', err);

  res.status(500).json({
    error: {
      message: 'Internal server error',
    },
  });
}
```

## Step 8: Application Setup

```typescript
// src/app.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import userRoutes from './modules/users/user.routes';
import { errorHandler } from './middleware/errorHandler';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/users', userRoutes);

// Error handling
app.use(errorHandler);

export default app;
```

## Step 9: Server

```typescript
// src/server.ts
import app from './app';
import { pool } from './config/database';
import { logger } from './utils/logger';

const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    // Test database connection
    await pool.query('SELECT NOW()');
    logger.info('Database connected');

    app.listen(PORT, () => {
      logger.info(`Server running on port ${PORT}`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  await pool.end();
  process.exit(0);
});
```

## Database Migration

```sql
-- migrations/001_create_users_table.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

## Testing

```typescript
// src/modules/users/user.service.test.ts
import { UserService } from './user.service';
import { UserRepository } from './user.repository';

describe('UserService', () => {
  let service: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = {
      findAll: jest.fn(),
      findById: jest.fn(),
      findByEmail: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    } as any;

    service = new UserService(mockRepository);
  });

  describe('createUser', () => {
    it('should create user when email does not exist', async () => {
      mockRepository.findByEmail.mockResolvedValue(null);
      mockRepository.create.mockResolvedValue({
        id: '1',
        email: 'test@example.com',
        name: 'Test',
        created_at: new Date(),
        updated_at: new Date(),
      });

      const result = await service.createUser({
        email: 'test@example.com',
        name: 'Test',
        password: 'password123',
      });

      expect(result.email).toBe('test@example.com');
    });

    it('should throw error when email exists', async () => {
      mockRepository.findByEmail.mockResolvedValue({
        id: '1',
        email: 'test@example.com',
        name: 'Test',
        created_at: new Date(),
        updated_at: new Date(),
      });

      await expect(
        service.createUser({
          email: 'test@example.com',
          name: 'Test',
          password: 'password123',
        })
      ).rejects.toThrow('Email already exists');
    });
  });
});
```

## Running the Application

```bash
# Development
npm run dev

# Production
npm run build
npm start

# Testing
npm test
```

## Best Practices Implemented

✅ Layered architecture (Controller → Service → Repository)
✅ TypeScript for type safety
✅ Input validation with Zod
✅ Proper error handling
✅ Database connection pooling
✅ Security headers with Helmet
✅ CORS configuration
✅ Compression
✅ Structured logging
✅ Graceful shutdown
✅ Environment variables
✅ Unit testing

## Next Steps

1. Add authentication (JWT)
2. Add rate limiting
3. Add pagination
4. Add caching (Redis)
5. Add API documentation (Swagger)
6. Add monitoring (Prometheus)
7. Add CI/CD pipeline
