# Systems Architecture Expert Skill

## Overview

This skill provides elite-level expertise in designing, implementing, and evolving complex distributed systems using:

- **Microservices Architecture**: Service decomposition, communication patterns, data management
- **Event-Driven Architecture**: Messaging, event sourcing, CQRS, eventual consistency
- **Domain-Driven Design (DDD)**: Strategic and tactical patterns, bounded contexts, ubiquitous language

## When to Use This Skill

Invoke this skill when you need help with:

### Architecture Design
- Designing a new microservices system from scratch
- Breaking down a monolith into microservices
- Defining bounded contexts and service boundaries
- Creating system architecture diagrams and documentation

### Event-Driven Systems
- Implementing event sourcing and CQRS
- Choosing message brokers (Kafka, RabbitMQ, SQS, etc.)
- Designing event schemas and versioning strategies
- Implementing sagas for distributed transactions

### Domain Modeling
- Conducting Event Storming workshops
- Identifying aggregates, entities, and value objects
- Applying DDD tactical patterns
- Defining ubiquitous language

### Resilience & Reliability
- Implementing circuit breakers, retries, timeouts
- Designing for high availability and fault tolerance
- Setting up observability (logging, metrics, tracing)
- Defining SLOs and error budgets

### Migration & Evolution
- Planning monolith-to-microservices migration
- Implementing the Strangler Fig pattern
- Managing technical debt and incremental refactoring
- Versioning APIs and handling breaking changes

### Architecture Review
- Reviewing existing architecture for anti-patterns
- Identifying bottlenecks and scaling issues
- Recommending improvements and modernization paths
- Conducting architecture health checks

## How to Invoke

In Claude Code, reference this skill in your prompts:

```
Using the systems-architecture skill, help me [your specific request]
```

Or when creating a new Claude Code skill or slash command, reference:
```
/home/user/CLAUDE_SKILLS/cloud/systems-architecture/skill.md
```

## Example Usage

### Example 1: Designing a New E-commerce System

**User:**
> Using the systems-architecture skill, help me design a scalable e-commerce platform. We expect 10K orders/day initially, growing to 100K within a year. Need to support multiple payment methods, real-time inventory, and international shipping.

**Skill Response:**
The skill will:
1. Ask clarifying questions about business domain, team structure, tech stack
2. Propose bounded contexts (Order Management, Inventory, Shipping, Payment)
3. Design service decomposition with clear boundaries
4. Recommend communication patterns (sync vs. async)
5. Propose data management strategies
6. Define observability and testing approaches
7. Document decisions using ADRs

### Example 2: Implementing Event Sourcing

**User:**
> Using the systems-architecture skill, I want to implement event sourcing for our order management service. What are the best practices and what pitfalls should I avoid?

**Skill Response:**
The skill will:
1. Explain event sourcing concepts and when it's appropriate
2. Show implementation patterns for event store
3. Demonstrate projection strategies for read models
4. Address event schema evolution and versioning
5. Provide code examples in your preferred language
6. Discuss trade-offs and operational considerations
7. Reference industry examples (e.g., Netflix, Uber)

### Example 3: Migrating Monolith to Microservices

**User:**
> Using the systems-architecture skill, we have a 10-year-old monolithic Rails app. How do we safely migrate to microservices without disrupting our business?

**Skill Response:**
The skill will:
1. Assess readiness (team, CI/CD, monitoring)
2. Propose Strangler Fig pattern with phases
3. Identify first service to extract (low-risk, high-value)
4. Design anti-corruption layer
5. Plan data migration strategies
6. Define success metrics and rollback plans
7. Provide step-by-step migration roadmap

### Example 4: Event Storming Workshop

**User:**
> Using the systems-architecture skill, help me run an Event Storming workshop for our new healthcare appointment scheduling system.

**Skill Response:**
The skill will:
1. Provide workshop facilitation guide
2. Explain each phase of Event Storming
3. Suggest domain events to explore
4. Guide bounded context identification
5. Help define context maps and integration patterns
6. Output actionable architecture recommendations

### Example 5: Architecture Review

**User:**
> Using the systems-architecture skill, review our architecture. We have 15 services, shared MongoDB, synchronous REST calls everywhere, and we're seeing timeout issues under load.

**Skill Response:**
The skill will:
1. Identify anti-patterns (shared database, synchronous coupling)
2. Analyze through resilience lens
3. Propose architectural improvements
4. Prioritize changes by value and risk
5. Provide migration path with minimal disruption
6. Recommend observability enhancements

## Key Capabilities

### 1. Multi-Lens Analysis
The skill analyzes architecture through systematic lenses:
- Domain Modeling (DDD)
- Service Decomposition
- Communication Patterns
- Data Management
- Resilience & Reliability
- Observability
- Security
- Testing

### 2. Pattern Expertise
Deep knowledge of proven patterns:
- Microservices patterns (decomposition, data, communication)
- Event-driven patterns (event sourcing, CQRS, sagas)
- DDD tactical patterns (aggregates, entities, value objects, domain events)
- Resilience patterns (circuit breaker, retry, bulkhead, timeout)

### 3. Technology Selection
Guidance on choosing the right technologies:
- Message brokers (Kafka, RabbitMQ, SQS, Pub/Sub)
- Service meshes (Istio, Linkerd, Consul)
- API gateways (Kong, AWS API Gateway, Traefik)
- Observability tools (Prometheus, Jaeger, ELK)

### 4. Best Practices from Industry Leaders
References practices from:
- Netflix (Chaos Engineering, resilience)
- Uber (Domain-oriented microservices)
- Amazon (Two-pizza teams, SOA)
- Spotify (Organizational patterns)
- Google (SRE, observability)

### 5. Hands-On Implementation
Provides concrete implementation guidance:
- Code examples in multiple languages
- Configuration templates
- Architecture Decision Records (ADRs)
- Step-by-step migration guides
- Testing strategies

## Templates Included

The skill includes templates for common scenarios:

### 1. Architecture Decision Record (ADR)
Document key architectural decisions with context, alternatives, and consequences.

### 2. Service Specification Template
Define service boundaries, APIs, data ownership, and SLOs.

### 3. Event Storming Canvas
Facilitate domain discovery workshops.

### 4. Context Map Template
Document relationships between bounded contexts.

### 5. Migration Plan Template
Plan incremental migrations with risk mitigation.

## Prerequisites

To get the most value from this skill:

### Knowledge Prerequisites
- Basic understanding of distributed systems concepts
- Familiarity with REST APIs and HTTP
- Experience with at least one programming language
- Understanding of databases (SQL and/or NoSQL)

### Technical Prerequisites
- Access to cloud platform (AWS, Azure, GCP) or local development environment
- CI/CD pipeline or willingness to set one up
- Monitoring and logging infrastructure (or plan to implement)

### Organizational Prerequisites
- Team buy-in for architectural changes
- DevOps culture or willingness to adopt
- Product/business stakeholder engagement for domain modeling

## Output Formats

The skill can provide outputs in various formats:

### Architecture Diagrams
Text-based diagrams using:
- ASCII art for simple diagrams
- Mermaid syntax for complex flows
- C4 model notation for system context, containers, components

### Documentation
- Architecture Decision Records (ADRs)
- Service specifications
- API documentation
- Runbooks and operational guides

### Code Examples
Production-ready code in:
- Java/Spring Boot
- Node.js/TypeScript
- Python/FastAPI
- Go
- C#/.NET

### Implementation Plans
- Migration roadmaps with phases
- Testing strategies
- Rollback procedures
- Success metrics

## Common Scenarios

### Scenario: Choosing Between Sync and Async Communication

**When to use Synchronous (REST/gRPC):**
- User-facing requests requiring immediate response
- Simple CRUD operations
- Low-latency requirements (<100ms)
- Strong consistency needed

**When to use Asynchronous (Events):**
- Decoupling services for resilience
- Broadcasting changes to multiple consumers
- Eventual consistency acceptable
- High-throughput, non-urgent operations

**The skill will help you:** Analyze your specific use case and recommend the appropriate pattern with trade-offs.

### Scenario: Database Per Service vs. Shared Database

**Database Per Service:**
- ✅ Service autonomy
- ✅ Technology diversity (polyglot persistence)
- ✅ Independent scaling
- ❌ Complex cross-service queries
- ❌ Data duplication

**Shared Database:**
- ✅ Simple queries across data
- ✅ ACID transactions
- ❌ Tight coupling
- ❌ Cannot evolve independently

**The skill will help you:** Design transition strategies using patterns like database-per-service with API composition or CQRS.

### Scenario: Event Sourcing - Should I Use It?

**Good fit when:**
- Audit trail is critical (financial, healthcare)
- Temporal queries needed ("state at time T")
- Complex business logic with many state transitions
- Event-driven architecture already in place

**Poor fit when:**
- Simple CRUD applications
- No audit requirements
- Team unfamiliar with pattern
- Read-heavy workloads without writes

**The skill will help you:** Assess fit, design implementation, handle schema evolution, and optimize performance.

## Best Practices

### Start Small
- Don't extract all services at once
- Begin with bounded, low-risk capability
- Validate patterns before scaling

### Embrace Conway's Law
- Align service boundaries with team boundaries
- Organize teams around business capabilities
- Enable team autonomy with clear ownership

### Prioritize Observability
- Implement logging, metrics, tracing from day one
- Define SLOs before launch
- Build dashboards for business and technical metrics

### Design for Failure
- Every external call will fail eventually
- Implement circuit breakers, retries, timeouts
- Practice chaos engineering

### Evolve Incrementally
- Architecture is never "done"
- Refactor continuously based on learnings
- Document decisions with ADRs

### Balance Consistency and Autonomy
- Not everything needs strong consistency
- Use eventual consistency where appropriate
- Reserve distributed transactions for critical paths

## Troubleshooting

### "My services are tightly coupled"
**Solution:** Introduce asynchronous events, implement anti-corruption layers, use API composition or CQRS for queries.

### "I have distributed transactions everywhere"
**Solution:** Apply Saga pattern (choreography or orchestration), design aggregates to minimize cross-service transactions.

### "Performance is poor with many service calls"
**Solution:** Implement caching, use event-carried state transfer, consider CQRS with materialized views, batch operations.

### "My domain model is anemic"
**Solution:** Apply DDD tactical patterns, move logic into entities and value objects, use domain services for cross-aggregate operations.

### "I can't trace requests across services"
**Solution:** Implement distributed tracing (OpenTelemetry, Jaeger), use correlation IDs, centralize logging.

## Advanced Topics

The skill can also help with:

- **Multi-tenancy patterns** in microservices
- **Multi-region, active-active architectures**
- **Zero-downtime deployments** (blue-green, canary)
- **API versioning strategies**
- **GraphQL federation** for microservices
- **Service mesh configuration** (Istio, Linkerd)
- **Chaos engineering experiments**
- **Cost optimization** in cloud-native architectures

## Learning Path

If you're new to these concepts, the skill can guide you through:

1. **Fundamentals**: Microservices basics, REST APIs, messaging
2. **Intermediate**: DDD, event sourcing, CQRS, resilience patterns
3. **Advanced**: Complex sagas, multi-region systems, performance optimization
4. **Expert**: Chaos engineering, capacity planning, organizational patterns

## References & Further Reading

The skill references authoritative sources:

### Books
- "Building Microservices" by Sam Newman
- "Domain-Driven Design" by Eric Evans
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Microservices Patterns" by Chris Richardson

### Industry Blogs
- Netflix Tech Blog
- Uber Engineering Blog
- AWS Architecture Blog
- Martin Fowler's blog

### Conferences
- QCon
- GOTO
- Microservices Practitioner Summit
- Domain-Driven Design Europe

## Support

This skill is part of the elite CLAUDE_SKILLS repository. For:

- **Bug reports**: Open an issue
- **Enhancements**: Submit a pull request
- **Questions**: Use the skill and ask directly
- **Examples**: Check the templates directory

## Version History

- **v1.0** (2025-11-19): Initial release
  - Comprehensive microservices architecture coverage
  - Event-driven architecture patterns
  - Domain-Driven Design (strategic & tactical)
  - Resilience and observability
  - Migration strategies
  - Technology selection guidance

## Contributing

To improve this skill:

1. Add new patterns based on emerging industry practices
2. Include more code examples in different languages
3. Add real-world case studies
4. Update technology recommendations as tools evolve
5. Expand testing and operational guidance

---

## Quick Start

Ready to use this skill? Try these starter prompts:

```
Using the systems-architecture skill, help me design [your system]

Using the systems-architecture skill, review my architecture: [describe current state]

Using the systems-architecture skill, how do I implement [specific pattern]?

Using the systems-architecture skill, what's the best way to [specific challenge]?
```

The skill will engage you with clarifying questions, then provide comprehensive, actionable guidance tailored to your context.

**Let's build better systems together!**
