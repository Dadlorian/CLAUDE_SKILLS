# Architectural Patterns

## Overview

This document covers proven architectural patterns used in production systems at scale, based on practices from FAANG companies and distributed systems research.

---

## Microservices Architecture

### When to Use
- **Large teams** (50+ engineers) working on complex domains
- **Independent deployment** requirements
- **Technology diversity** needs
- **Scale different components** independently

### When NOT to Use
- **Small teams** or startups (< 10 engineers)
- **Simple applications** with limited scope
- **Tight coupling** between business domains
- **Limited DevOps maturity**

### Pattern Structure

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│ API Gateway │────▶│  Service    │
└─────────────┘     └─────────────┘     │  Discovery  │
                                        └──────┬──────┘
                                               │
              ┌────────────────────────────────┼────────────────┐
              │                                │                │
         ┌────▼────┐                     ┌────▼────┐      ┌────▼────┐
         │  User   │                     │ Product │      │  Order  │
         │ Service │                     │ Service │      │ Service │
         └────┬────┘                     └────┬────┘      └────┬────┘
              │                               │                │
         ┌────▼────┐                     ┌────▼────┐      ┌────▼────┐
         │  User   │                     │ Product │      │  Order  │
         │   DB    │                     │   DB    │      │   DB    │
         └─────────┘                     └─────────┘      └─────────┘
```

### Implementation Example

```typescript
// User Service
@Controller('/api/users')
export class UserController {
  constructor(
    private userService: UserService,
    private eventBus: EventBus
  ) {}

  @Post()
  async createUser(@Body() dto: CreateUserDto) {
    const user = await this.userService.create(dto);

    // Publish event for other services
    await this.eventBus.publish('user.created', {
      userId: user.id,
      email: user.email
    });

    return user;
  }
}

// Order Service (listening to user events)
@Injectable()
export class UserEventHandler {
  @EventHandler('user.created')
  async handleUserCreated(event: UserCreatedEvent) {
    // Create customer profile in order service
    await this.customerService.createFromUser(event);
  }
}
```

### Best Practices
- **Database per service**: Each service owns its data
- **API Gateway**: Single entry point for clients
- **Service Discovery**: Dynamic service registration (Consul, Eureka)
- **Circuit Breakers**: Prevent cascading failures
- **Distributed Tracing**: OpenTelemetry, Jaeger
- **Async Communication**: Event-driven with message queues

---

## Event-Driven Architecture (EDA)

### When to Use
- **Real-time data processing** requirements
- **Loose coupling** between components
- **Audit trails** and event sourcing needs
- **Scalable data pipelines**

### Pattern Structure

```
┌──────────────┐
│   Producer   │
│  (Service A) │
└──────┬───────┘
       │
       │ publish events
       ▼
┌──────────────────┐
│   Event Bus      │
│ (Kafka/RabbitMQ) │
└──────┬───────────┘
       │
       │ subscribe
       ├───────────┬───────────┬──────────┐
       ▼           ▼           ▼          ▼
   ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
   │Service│  │Service│  │Service│  │Service│
   │   B   │  │   C   │  │   D   │  │   E   │
   └───────┘  └───────┘  └───────┘  └───────┘
```

### Implementation Example

```typescript
// Event definition
interface OrderPlacedEvent {
  eventId: string;
  eventType: 'order.placed';
  timestamp: Date;
  data: {
    orderId: string;
    userId: string;
    totalAmount: number;
    items: OrderItem[];
  };
}

// Producer
class OrderService {
  async placeOrder(order: CreateOrderDto) {
    const savedOrder = await this.orderRepository.save(order);

    // Publish event
    await this.eventBus.publish<OrderPlacedEvent>({
      eventId: uuid(),
      eventType: 'order.placed',
      timestamp: new Date(),
      data: {
        orderId: savedOrder.id,
        userId: savedOrder.userId,
        totalAmount: savedOrder.total,
        items: savedOrder.items
      }
    });

    return savedOrder;
  }
}

// Consumers
class InventoryService {
  @Subscribe('order.placed')
  async handleOrderPlaced(event: OrderPlacedEvent) {
    await this.reserveInventory(event.data.items);
  }
}

class NotificationService {
  @Subscribe('order.placed')
  async handleOrderPlaced(event: OrderPlacedEvent) {
    await this.sendOrderConfirmation(event.data.userId, event.data.orderId);
  }
}

class AnalyticsService {
  @Subscribe('order.placed')
  async handleOrderPlaced(event: OrderPlacedEvent) {
    await this.trackOrderMetrics(event.data);
  }
}
```

### Best Practices
- **Event Schema Versioning**: Use schema registry (Confluent Schema Registry)
- **Idempotent Consumers**: Handle duplicate events gracefully
- **Dead Letter Queues**: Handle failed event processing
- **Event Ordering**: Use partition keys for ordered events
- **Event Replay**: Support for debugging and recovery

---

## CQRS (Command Query Responsibility Segregation)

### When to Use
- **Complex business logic** with different read/write patterns
- **High read load** vs write load mismatch
- **Event sourcing** implementation
- **Multiple read models** for same data

### Pattern Structure

```
              ┌─────────────┐
              │   Client    │
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    Commands      Queries         │
        │            │            │
        ▼            ▼            │
   ┌─────────┐  ┌─────────┐      │
   │ Command │  │  Query  │      │
   │ Handler │  │ Handler │      │
   └────┬────┘  └────┬────┘      │
        │            │            │
        │            │            │
        ▼            ▼            │
   ┌─────────┐  ┌─────────┐      │
   │  Write  │  │  Read   │      │
   │  Model  │  │  Model  │      │
   └────┬────┘  └─────────┘      │
        │                        │
        │    Event Bus           │
        └────────────────────────┘
```

### Implementation Example

```typescript
// Commands
class CreateUserCommand {
  constructor(
    public readonly email: string,
    public readonly name: string
  ) {}
}

class UpdateUserProfileCommand {
  constructor(
    public readonly userId: string,
    public readonly profileData: ProfileData
  ) {}
}

// Command Handler
@CommandHandler(CreateUserCommand)
class CreateUserHandler {
  async execute(command: CreateUserCommand) {
    const user = await this.userRepository.create({
      email: command.email,
      name: command.name
    });

    // Publish domain event
    await this.eventBus.publish(new UserCreatedEvent(user.id));

    return user.id;
  }
}

// Queries
class GetUserByIdQuery {
  constructor(public readonly userId: string) {}
}

class GetUserListQuery {
  constructor(
    public readonly filters: UserFilters,
    public readonly pagination: Pagination
  ) {}
}

// Query Handler (reads from optimized read model)
@QueryHandler(GetUserByIdQuery)
class GetUserByIdHandler {
  async execute(query: GetUserByIdQuery) {
    // Read from denormalized, optimized read model
    return this.userReadModel.findById(query.userId);
  }
}

// Read model updater (listens to domain events)
@EventHandler(UserCreatedEvent)
class UpdateUserReadModel {
  async handle(event: UserCreatedEvent) {
    // Update denormalized read model
    await this.userReadModel.create({
      id: event.userId,
      // ... optimized structure for reads
    });
  }
}
```

### Best Practices
- **Separate databases** for read and write models (optional)
- **Eventual consistency** between models
- **Event-driven synchronization**
- **Optimized read models** for specific queries
- **Clear command/query separation**

---

## Domain-Driven Design (DDD)

### Core Concepts

**Bounded Contexts**:
```
┌─────────────────────────────────────────────────┐
│         E-Commerce System                       │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   Catalog    │  │   Ordering   │           │
│  │   Context    │  │   Context    │           │
│  │              │  │              │           │
│  │  - Product   │  │  - Order     │           │
│  │  - Category  │  │  - OrderItem │           │
│  │  - Price     │  │  - Payment   │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Inventory   │  │   Shipping   │           │
│  │   Context    │  │   Context    │           │
│  │              │  │              │           │
│  │  - Stock     │  │  - Shipment  │           │
│  │  - Warehouse │  │  - Tracking  │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

### Implementation Example

```typescript
// Value Object
class Money {
  constructor(
    private readonly amount: number,
    private readonly currency: string
  ) {
    if (amount < 0) {
      throw new Error('Amount cannot be negative');
    }
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Cannot add money with different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }
}

// Entity
class Order {
  private readonly items: OrderItem[] = [];
  private status: OrderStatus;

  constructor(
    private readonly id: OrderId,
    private readonly customerId: CustomerId
  ) {
    this.status = OrderStatus.PENDING;
  }

  addItem(product: Product, quantity: number): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Cannot add items to non-pending order');
    }
    this.items.push(new OrderItem(product, quantity));
  }

  calculateTotal(): Money {
    return this.items.reduce(
      (total, item) => total.add(item.getSubtotal()),
      new Money(0, 'USD')
    );
  }

  confirm(): void {
    if (this.items.length === 0) {
      throw new Error('Cannot confirm order with no items');
    }
    this.status = OrderStatus.CONFIRMED;
  }
}

// Aggregate Root
class Customer {
  private readonly orders: Order[] = [];

  constructor(
    private readonly id: CustomerId,
    private email: Email,
    private readonly preferences: CustomerPreferences
  ) {}

  placeOrder(order: Order): void {
    // Business invariants enforced at aggregate level
    if (this.hasUnpaidOrders()) {
      throw new Error('Cannot place new order with unpaid orders');
    }
    this.orders.push(order);
  }

  private hasUnpaidOrders(): boolean {
    return this.orders.some(order => !order.isPaid());
  }
}

// Repository
interface CustomerRepository {
  findById(id: CustomerId): Promise<Customer | null>;
  save(customer: Customer): Promise<void>;
}

// Domain Service
class PricingService {
  calculateDiscount(
    customer: Customer,
    order: Order
  ): Money {
    if (customer.isVIP()) {
      return order.calculateTotal().multiply(0.1);
    }
    return new Money(0, 'USD');
  }
}
```

### Best Practices
- **Ubiquitous Language**: Use domain terms in code
- **Aggregates**: Consistency boundaries
- **Value Objects**: Immutable domain concepts
- **Domain Events**: Capture important state changes
- **Anti-Corruption Layer**: Protect domain from external models

---

## Clean Architecture (Hexagonal Architecture)

### Pattern Structure

```
┌───────────────────────────────────────────────────┐
│              External Layer                       │
│  ┌─────────────┐  ┌─────────────┐               │
│  │   Web API   │  │  Database   │               │
│  │ (Framework) │  │   (Infra)   │               │
│  └──────┬──────┘  └──────┬──────┘               │
│         │                │                       │
├─────────┼────────────────┼───────────────────────┤
│         │  Adapters      │                       │
│  ┌──────▼──────┐  ┌──────▼──────┐               │
│  │ Controllers │  │Repositories │               │
│  └──────┬──────┘  └──────┬──────┘               │
│         │                │                       │
├─────────┼────────────────┼───────────────────────┤
│         │  Application   │                       │
│  ┌──────▼────────────────▼──────┐               │
│  │      Use Cases / Services     │               │
│  └──────┬────────────────┬──────┘               │
│         │                │                       │
├─────────┼────────────────┼───────────────────────┤
│         │    Domain      │                       │
│  ┌──────▼──────┐  ┌──────▼──────┐               │
│  │  Entities   │  │  Business   │               │
│  │             │  │    Logic    │               │
│  └─────────────┘  └─────────────┘               │
└───────────────────────────────────────────────────┘
```

### Implementation Example

```typescript
// Domain Layer (innermost, no dependencies)
interface User {
  id: string;
  email: string;
  name: string;
}

// Application Layer (use cases)
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

class CreateUserUseCase {
  constructor(private userRepository: UserRepository) {}

  async execute(email: string, name: string): Promise<User> {
    // Business logic
    const user: User = {
      id: generateId(),
      email: email.toLowerCase(),
      name: name
    };

    await this.userRepository.save(user);
    return user;
  }
}

// Infrastructure Layer (adapters)
class PostgresUserRepository implements UserRepository {
  constructor(private db: PostgresDatabase) {}

  async findById(id: string): Promise<User | null> {
    const row = await this.db.query('SELECT * FROM users WHERE id = $1', [id]);
    return row ? this.mapToUser(row) : null;
  }

  async save(user: User): Promise<void> {
    await this.db.query(
      'INSERT INTO users (id, email, name) VALUES ($1, $2, $3)',
      [user.id, user.email, user.name]
    );
  }
}

// Presentation Layer (controllers)
class UserController {
  constructor(private createUserUseCase: CreateUserUseCase) {}

  async create(req: Request, res: Response) {
    const { email, name } = req.body;
    const user = await this.createUserUseCase.execute(email, name);
    res.status(201).json(user);
  }
}
```

### Best Practices
- **Dependency inversion**: Core depends on abstractions
- **Independent of frameworks**: Business logic portable
- **Testable**: Easy to test in isolation
- **Independent of UI**: Can change UI without affecting business logic
- **Independent of database**: Can swap databases

---

## Monolith Architecture

### When to Use (Yes, still valid!)
- **Startups/MVPs**: Fast iteration, simple deployment
- **Small teams**: < 10 engineers
- **Simple domains**: Limited business complexity
- **Low scale requirements**: < 10k users initially

### Modular Monolith Structure

```
src/
├── modules/
│   ├── users/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── models/
│   ├── products/
│   └── orders/
├── shared/
│   ├── database/
│   ├── auth/
│   └── utils/
└── main.ts
```

### Best Practices
- **Modular structure**: Prepare for future extraction
- **Clear boundaries**: Module interfaces
- **Shared database**: But separate schemas per module
- **Easier to start**: Can extract to microservices later

---

## Service Mesh Architecture

### Pattern Structure

```
┌─────────────────────────────────────────────────┐
│              Service Mesh (Istio)               │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │           Control Plane                  │  │
│  │  - Traffic Management                    │  │
│  │  - Security (mTLS)                       │  │
│  │  - Observability                         │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                               │
│  ┌──────────────▼───────────────────────────┐  │
│  │           Data Plane (Envoy Proxies)     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │ Service │    │ Service │    │ Service │   │
│  │    A    │───▶│    B    │───▶│    C    │   │
│  └─────────┘    └─────────┘    └─────────┘   │
└─────────────────────────────────────────────────┘
```

### Benefits
- **Traffic management**: Load balancing, routing, retries
- **Security**: mTLS between services
- **Observability**: Automatic metrics, logs, traces
- **Resilience**: Circuit breakers, timeouts, retries

---

## References

- **"Building Microservices"** by Sam Newman
- **"Domain-Driven Design"** by Eric Evans
- **"Clean Architecture"** by Robert C. Martin
- **"Designing Data-Intensive Applications"** by Martin Kleppmann
- **Martin Fowler's Blog**: https://martinfowler.com/
- **Microservices.io**: https://microservices.io/

---

## Version

**Version**: 1.0
**Last Updated**: 2025-11-19
