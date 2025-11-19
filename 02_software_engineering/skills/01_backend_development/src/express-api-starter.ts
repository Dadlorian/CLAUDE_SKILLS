// Complete Express + TypeScript API Starter
// Run: npx ts-node express-api-starter.ts

import express, { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json());

// Error class
class AppError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
  }
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Example route with error handling
app.get('/api/users/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    // Simulate database query
    if (id === '404') {
      throw new AppError(404, 'User not found');
    }

    res.json({
      data: {
        id,
        name: 'John Doe',
        email: 'john@example.com',
      },
    });
  } catch (error) {
    next(error);
  }
});

// Error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: { message: err.message },
    });
  }

  console.error(err);
  res.status(500).json({
    error: { message: 'Internal server error' },
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
