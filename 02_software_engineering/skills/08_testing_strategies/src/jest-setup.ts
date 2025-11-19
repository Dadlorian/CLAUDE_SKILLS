// Jest configuration and setup
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  transform: { '^.+\\.ts$': 'ts-jest' },
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

// Example test
import { UserService } from './user.service';

describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepo = {
      findById: jest.fn(),
      create: jest.fn(),
    } as any;
    service = new UserService(mockRepo);
  });

  it('creates user successfully', async () => {
    const userData = { email: 'test@example.com', name: 'Test' };
    mockRepo.create.mockResolvedValue({ id: '1', ...userData });

    const result = await service.createUser(userData);

    expect(result.id).toBe('1');
    expect(mockRepo.create).toHaveBeenCalledWith(userData);
  });
});
