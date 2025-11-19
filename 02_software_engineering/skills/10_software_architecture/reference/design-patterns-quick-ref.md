# Design Patterns Quick Reference

## Creational Patterns

### Singleton
**Use when**: Need exactly one instance (database connection, configuration)

```typescript
class Database {
  private static instance: Database;
  private constructor() {}
  static getInstance(): Database {
    if (!Database.instance) {
      Database.instance = new Database();
    }
    return Database.instance;
  }
}
```

### Factory
**Use when**: Creating objects without specifying exact class

```typescript
interface Payment { process(amount: number): void; }

class PaymentFactory {
  create(type: string): Payment {
    if (type === 'stripe') return new StripePayment();
    if (type === 'paypal') return new PayPalPayment();
    throw new Error('Unknown payment type');
  }
}
```

### Builder
**Use when**: Complex object construction with many optional parameters

```typescript
class UserBuilder {
  private user: Partial<User> = {};

  setEmail(email: string) {
    this.user.email = email;
    return this;
  }

  setName(name: string) {
    this.user.name = name;
    return this;
  }

  build(): User {
    return this.user as User;
  }
}

const user = new UserBuilder()
  .setEmail('john@example.com')
  .setName('John')
  .build();
```

## Structural Patterns

### Adapter
**Use when**: Making incompatible interfaces work together

```typescript
// Old interface
class LegacyPayment {
  makePayment(amount: number) { }
}

// New interface
interface ModernPayment {
  process(amount: number): void;
}

// Adapter
class PaymentAdapter implements ModernPayment {
  constructor(private legacy: LegacyPayment) {}

  process(amount: number) {
    this.legacy.makePayment(amount);
  }
}
```

### Decorator
**Use when**: Adding functionality to objects dynamically

```typescript
interface Coffee {
  cost(): number;
  description(): string;
}

class SimpleCoffee implements Coffee {
  cost() { return 5; }
  description() { return 'Simple coffee'; }
}

class MilkDecorator implements Coffee {
  constructor(private coffee: Coffee) {}

  cost() {
    return this.coffee.cost() + 2;
  }

  description() {
    return this.coffee.description() + ', milk';
  }
}

let coffee = new SimpleCoffee();
coffee = new MilkDecorator(coffee);
console.log(coffee.cost()); // 7
```

### Proxy
**Use when**: Controlling access to an object (lazy loading, caching)

```typescript
interface Image {
  display(): void;
}

class RealImage implements Image {
  constructor(private filename: string) {
    this.loadFromDisk();
  }

  private loadFromDisk() {
    console.log('Loading ' + this.filename);
  }

  display() {
    console.log('Displaying ' + this.filename);
  }
}

class ProxyImage implements Image {
  private realImage?: RealImage;

  constructor(private filename: string) {}

  display() {
    if (!this.realImage) {
      this.realImage = new RealImage(this.filename);
    }
    this.realImage.display();
  }
}
```

## Behavioral Patterns

### Strategy
**Use when**: Different algorithms for same task

```typescript
interface SortStrategy {
  sort(data: number[]): number[];
}

class QuickSort implements SortStrategy {
  sort(data: number[]) { /* implementation */ return data; }
}

class MergeSort implements SortStrategy {
  sort(data: number[]) { /* implementation */ return data; }
}

class Sorter {
  constructor(private strategy: SortStrategy) {}

  setStrategy(strategy: SortStrategy) {
    this.strategy = strategy;
  }

  sort(data: number[]) {
    return this.strategy.sort(data);
  }
}
```

### Observer
**Use when**: One-to-many dependency between objects

```typescript
interface Observer {
  update(data: any): void;
}

class Subject {
  private observers: Observer[] = [];

  attach(observer: Observer) {
    this.observers.push(observer);
  }

  notify(data: any) {
    this.observers.forEach(o => o.update(data));
  }
}

class EmailObserver implements Observer {
  update(data: any) {
    console.log('Sending email:', data);
  }
}
```

### Command
**Use when**: Encapsulating requests as objects

```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class CreateUserCommand implements Command {
  constructor(private user: User) {}

  execute() {
    database.save(this.user);
  }

  undo() {
    database.delete(this.user.id);
  }
}

class CommandInvoker {
  private history: Command[] = [];

  execute(command: Command) {
    command.execute();
    this.history.push(command);
  }

  undo() {
    const command = this.history.pop();
    command?.undo();
  }
}
```

### Chain of Responsibility
**Use when**: Multiple handlers for a request

```typescript
abstract class Handler {
  protected next?: Handler;

  setNext(handler: Handler): Handler {
    this.next = handler;
    return handler;
  }

  handle(request: any): any {
    if (this.next) {
      return this.next.handle(request);
    }
    return null;
  }
}

class AuthHandler extends Handler {
  handle(request: any) {
    if (!request.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    return super.handle(request);
  }
}

class ValidationHandler extends Handler {
  handle(request: any) {
    if (!request.isValid) {
      throw new Error('Invalid request');
    }
    return super.handle(request);
  }
}

// Usage
const chain = new AuthHandler();
chain.setNext(new ValidationHandler());
chain.handle(request);
```

## Repository Pattern

**Use when**: Abstracting data access

```typescript
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: string): Promise<void>;
}

class UserRepository implements Repository<User> {
  async findById(id: string) {
    return db.users.findUnique({ where: { id } });
  }

  async findAll() {
    return db.users.findMany();
  }

  async save(user: User) {
    return db.users.upsert({
      where: { id: user.id },
      create: user,
      update: user,
    });
  }

  async delete(id: string) {
    await db.users.delete({ where: { id } });
  }
}
```

## Unit of Work

**Use when**: Grouping database operations

```typescript
class UnitOfWork {
  private operations: (() => Promise<void>)[] = [];

  register(operation: () => Promise<void>) {
    this.operations.push(operation);
  }

  async commit() {
    await db.$transaction(async (tx) => {
      for (const op of this.operations) {
        await op();
      }
    });
    this.operations = [];
  }

  rollback() {
    this.operations = [];
  }
}
```

## Dependency Injection

**Use when**: Managing dependencies

```typescript
// Without DI (tightly coupled)
class UserService {
  private repo = new UserRepository();
}

// With DI (loosely coupled)
class UserService {
  constructor(private repo: UserRepository) {}
}

// Container
class Container {
  private services = new Map();

  register<T>(key: string, factory: () => T) {
    this.services.set(key, factory);
  }

  resolve<T>(key: string): T {
    const factory = this.services.get(key);
    return factory();
  }
}

// Usage
const container = new Container();
container.register('UserRepository', () => new UserRepository());
container.register('UserService', () =>
  new UserService(container.resolve('UserRepository'))
);
```

## When to Use Which Pattern

| Pattern | Use Case |
|---------|----------|
| Singleton | Database connection, config |
| Factory | Creating objects based on type |
| Builder | Complex object construction |
| Adapter | Integrating legacy code |
| Decorator | Adding features dynamically |
| Proxy | Lazy loading, caching |
| Strategy | Swappable algorithms |
| Observer | Event systems |
| Command | Undo/redo functionality |
| Repository | Data access abstraction |
| Dependency Injection | Testability, loose coupling |
