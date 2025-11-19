# C4 Model - Complete Reference Guide

## Overview

The C4 model is a hierarchical set of diagrams that help document software architecture. It was created by Simon Brown as a way to describe and communicate software architecture clearly, at different levels of abstraction.

### Why C4?

- **Simple and effective**: Bridges the gap between high-level business concept and low-level code
- **Scalable**: Works for teams of all sizes
- **Clear abstraction levels**: Each level removes unnecessary detail
- **Communication tool**: Facilitates discussion between technical and non-technical stakeholders
- **Reduces documentation burden**: One model approach for all levels

---

## The Four Levels

### Level 1: System Context Diagram

Shows the software system in scope and how it interacts with users and other systems.

**Purpose:**
- Define system boundaries
- Identify external systems and actors
- Show high-level data flows

**What to include:**
- Your system (as a single box)
- Users and actors (represented as stick figures)
- External systems (other software systems)
- Data flows between them

**Example:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│  │   User   │───▶│  E-Commerce      │◀───│  Payment         │ │
│  │          │    │  System          │    │  Gateway         │ │
│  └──────────┘    └──────────────────┘    └──────────────────┘ │
│                           │                                     │
│                           │                                     │
│                  ┌────────▼──────────┐                          │
│                  │  Email Service    │                          │
│                  └───────────────────┘                          │
│                                                                 │
│                     System Context                              │
└─────────────────────────────────────────────────────────────────┘
```

**Best practices:**
- Keep it simple - maximum 7-10 elements
- Use rectangular boxes for external systems
- Use stick figures or actor symbols for users
- Label all interactions clearly
- Include system name and context boundary

---

### Level 2: Container Diagram

Shows the high-level technology choices and how responsibilities are distributed across containers.

**Purpose:**
- Show architecture at a technical level
- Identify major technology choices
- Clarify responsibility separation
- Communicate deployment structure

**What is a Container?**
A container is a deployable unit of executable code (application, microservice, database, etc.)

**Example Elements:**
- Web application (React, Angular, etc.)
- Mobile app (iOS, Android)
- Server-side application (Java, Python, Node.js)
- Database (PostgreSQL, MongoDB)
- File storage (S3, Google Cloud Storage)
- Message queue (RabbitMQ, Kafka)

**Example:**

```
┌─────────────────────────────────────────────────────────┐
│                 E-Commerce System                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │  Web Browser     │    │  Mobile App              │  │
│  │  (React, SPA)    │    │  (React Native)          │  │
│  └────────┬─────────┘    └──────────┬───────────────┘  │
│           │                         │                   │
│           │         ┌───────────────┘                   │
│           │         │                                   │
│           ▼         ▼                                   │
│  ┌──────────────────────────────┐                      │
│  │  API Server                  │                      │
│  │  (Node.js/Express)           │                      │
│  └────────┬─────────┬────────────┘                      │
│           │         │                                   │
│    ┌──────▼──┐  ┌───▼─────────┐                        │
│    │ Database │  │ Cache       │                        │
│    │PostgreSQL│  │ (Redis)     │                        │
│    └──────────┘  └─────────────┘                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key information to include:**
- Container name
- Technology stack
- Primary responsibility
- Data stores (clearly marked)
- External system interactions

---

### Level 3: Component Diagram

Decompose each container into components and show how they interact.

**Purpose:**
- Show internal structure of a container
- Clarify how a container implements its functionality
- Identify major components and interfaces

**What is a Component?**
A component is a grouping of related functionality encapsulated behind an interface.

**Example:**

```
┌─────────────────────────────────────────────────────┐
│           API Server Container                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────┐                           │
│  │  HTTP API Controller │                           │
│  │  (Express Routes)    │                           │
│  └──────────┬───────────┘                           │
│             │                                        │
│  ┌──────────▼────────────────────────────────────┐ │
│  │  Business Logic Components                    │ │
│  │  ┌──────────────┐  ┌──────────────┐           │ │
│  │  │ Auth Service │  │ Order Service│           │ │
│  │  └──────────────┘  └──────────────┘           │ │
│  │  ┌──────────────┐  ┌──────────────┐           │ │
│  │  │User Service  │  │Payment Service           │ │
│  │  └──────────────┘  └──────────────┘           │ │
│  └────┬────────────────────────────────────┬─────┘ │
│       │                                    │        │
│  ┌────▼──────────────┐   ┌────────────────▼──┐    │
│  │ Database Accessor │   │ External Service  │    │
│  │ Component         │   │ Adapter           │    │
│  └───────────────────┘   └───────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Content to show:**
- Component name and responsibility
- Technology/library used
- Dependencies between components
- Interfaces and APIs
- Data flows

---

### Level 4: Code Diagram

The lowest level of detail - showing how components are implemented in code.

**Purpose:**
- Show code structure (classes, interfaces, etc.)
- Help developers understand specific implementations
- Useful for code review and development

**When to use:**
- For complex components that need clarification
- During onboarding of new developers
- When explaining design patterns

**Example Elements:**
- Classes and interfaces
- Methods and properties
- Inheritance and implementation relationships

**Example:**

```java
// Code Level Detail (illustrative)

interface OrderService {
    +createOrder(userId, items)
    +updateOrder(orderId, items)
    +cancelOrder(orderId)
}

class OrderServiceImpl implements OrderService {
    -database: DatabaseAccessor
    -paymentService: PaymentService
    -notificationService: NotificationService

    +createOrder(userId, items)
    +updateOrder(orderId, items)
    +cancelOrder(orderId)
    -validateOrder()
    -persistOrder()
}
```

---

## Creating Effective C4 Diagrams

### General Principles

1. **Abstraction is key**: Each level should hide unnecessary complexity
2. **Consistency**: Use consistent shapes, colors, and notation across diagrams
3. **Single responsibility**: Each diagram should have one purpose
4. **Clarity over completeness**: Show what's important, hide what's not
5. **Technology agnostic**: Focus on architecture, not specific tools

### Notation Guidelines

**Standard Shapes:**
- **Rectangle**: Container or Component
- **Stick figure**: Person/User/Actor
- **Database symbol**: Data store
- **Cloud**: External system
- **Arrows**: Interactions with labels

**Color Coding:**
- Use different colors to distinguish:
  - Your system vs. external systems
  - Different technology stacks
  - Different deployment tiers
  - Different teams or concerns

### Common Mistakes to Avoid

1. **Too much detail too soon**: Don't put everything in Level 1
2. **Mixing levels**: Keep each diagram at its appropriate abstraction
3. **Poor labeling**: Every arrow and box should be clearly labeled
4. **Inconsistent notation**: Stick to your chosen notation system
5. **Ignoring data flows**: Always show how data moves
6. **Too many elements**: If you have >7-10 boxes, reconsider grouping
7. **Technology-first thinking**: Focus on architecture first, technology second

---

## Documenting C4 Diagrams

For each diagram, document:

### Title
Clearly state the level and purpose.

### Context/Scope
Brief explanation of what system or boundary this shows.

### Key Elements
List major components and their roles.

### Technology Stack
What technologies are used and why.

### Data Flows
How information moves through the system.

### Assumptions
What assumptions does this architecture make?

### Future Considerations
Known limitations or planned changes.

---

## C4 Model Example: Complete E-Commerce System

### Level 1: System Context
```
User → E-Commerce Platform → Payment Gateway
User → E-Commerce Platform → Email Service
E-Commerce Platform → Inventory System (External)
```

### Level 2: Containers
- Web Application (React)
- Mobile Application (React Native)
- API Server (Node.js)
- Database (PostgreSQL)
- Cache (Redis)
- Search Index (Elasticsearch)

### Level 3: Components (API Server)
- Auth Component
- Product Service
- Order Service
- User Service
- Payment Adapter
- External Service Adapters

### Level 4: Code
- Classes implementing each service
- Database models
- API endpoints

---

## Tools for Creating C4 Diagrams

- **C4-PlantUML**: PlantUML-based, open source
- **Structurizr**: Official C4 model tool by Simon Brown
- **ArchiMate**: Enterprise architecture notation
- **Draw.io**: Visual diagramming tool
- **Mermaid**: Markdown-based diagramming
- **Lucidchart**: Professional diagramming
- **Excalidraw**: Whiteboard-style diagrams

---

## When to Update C4 Diagrams

- Major architectural changes
- New containers or components added/removed
- Technology stack changes
- Significant data flow modifications
- Quarterly architecture reviews
- Before and after major refactoring

---

## Benefits of C4 Model

✓ Clear communication with all stakeholders
✓ Reduces ambiguity in architecture discussions
✓ Provides consistent structure for documentation
✓ Facilitates onboarding of new team members
✓ Identifies architectural issues early
✓ Helps in making informed technology choices
✓ Enables effective code reviews
✓ Creates living documentation

---

## References

- Simon Brown's C4 Model: https://c4model.com
- C4 Model Notation Guide
- Architecture as Code approaches
- System thinking principles
