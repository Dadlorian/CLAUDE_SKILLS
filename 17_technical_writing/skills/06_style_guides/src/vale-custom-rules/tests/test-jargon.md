# Test: Jargon Detection

This file is used to test the TechWriter.Jargon rule. It ensures technical terms are explained for readers who may not be familiar with specialized vocabulary, improving documentation accessibility and comprehension.

## Rule Purpose

### Why Detect Jargon
Technical jargon creates barriers for:
- New developers and junior team members
- Cross-functional stakeholders (product, marketing, support)
- International audiences and non-native English speakers
- Future team members unfamiliar with legacy systems
- Customers evaluating or implementing the product

### Detection Criteria
- Industry-specific terminology used without context
- Technical concepts assumed to be universally understood
- Domain-specific language not explained on first use
- Complex terms that could be simplified

## Bad Examples - Unexplained Jargon (Should Flag)

### Emerging Technologies
- The blockchain technology enables transactions. (JARGON - should flag)
- Implement machine learning for predictions. (JARGON - should flag)
- Use containerization for deployment. (JARGON - should flag)
- Enable serverless functions. (JARGON - should flag)
- Leverage microservices architecture. (JARGON - should flag)

### Security and Cryptography
- Cryptography protects your data. (JARGON - should flag)
- Enable end-to-end encryption. (JARGON - should flag)
- Implement zero-trust security. (JARGON - should flag)
- Use public key infrastructure. (JARGON - should flag)
- Configure mutual TLS authentication. (JARGON - should flag)

### Development Practices
- Use test-driven development. (JARGON - should flag)
- Implement continuous integration. (JARGON - should flag)
- Follow domain-driven design. (JARGON - should flag)
- Apply behavior-driven development. (JARGON - should flag)
- Use pair programming techniques. (JARGON - should flag)

### Architecture Patterns
- The OAuth mechanism authenticates users. (JARGON - should flag)
- Implement event sourcing. (JARGON - should flag)
- Use CQRS pattern. (JARGON - should flag)
- Apply hexagonal architecture. (JARGON - should flag)
- Implement saga pattern. (JARGON - should flag)

### Integration and APIs
- Use the API to integrate. (JARGON - should flag)
- Implement webhooks for notifications. (JARGON - should flag)
- Use GraphQL for queries. (JARGON - should flag)
- Enable service mesh. (JARGON - should flag)
- Implement API gateway. (JARGON - should flag)

### Data and Processing
- Use MapReduce for processing. (JARGON - should flag)
- Implement sharding strategy. (JARGON - should flag)
- Enable data replication. (JARGON - should flag)
- Use normalization techniques. (JARGON - should flag)
- Implement caching layer. (JARGON - should flag)

## Good Examples - Explained Jargon (Should NOT Flag)

### Appositive Style (Comma-Separated Explanation)
- Blockchain, a distributed ledger technology, enables transactions.
- Cryptography, which is the practice of secure communication, protects your data.
- Containerization, which packages applications with their dependencies, simplifies deployment.
- Serverless, a cloud computing model where providers manage infrastructure, reduces operational overhead.
- Microservices, an architectural approach that structures applications as independent services, improves scalability.

### Parenthetical Definition Style
- An API (Application Programming Interface) provides a way to integrate.
- OAuth (an authentication protocol) authenticates users.
- TDD (Test-Driven Development) writes tests before code.
- CI (Continuous Integration) automatically tests code changes.
- DDD (Domain-Driven Design) models software around business concepts.

### Inline Explanation Style
- Use machine learning, a form of artificial intelligence that learns from data, for predictions.
- Implement end-to-end encryption, where data is encrypted throughout transmission, to protect privacy.
- Enable zero-trust security, which verifies every access request regardless of source, for better protection.
- Use public key infrastructure, a system for managing digital certificates and encryption keys, for authentication.
- Configure mutual TLS, where both client and server authenticate each other, for enhanced security.

### Introductory Sentence Pattern
Webhooks are HTTP callbacks that notify your application of events. Implement webhooks for real-time notifications.

GraphQL is a query language for APIs that allows clients to request specific data. Use GraphQL for flexible queries.

A service mesh is a dedicated infrastructure layer for service-to-service communication. Enable service mesh for observability.

An API gateway is a server that acts as an entry point for APIs. Implement API gateway to manage traffic.

### Definition-First Pattern
- Event sourcing stores all changes as a sequence of events. Implement event sourcing for audit trails.
- CQRS (Command Query Responsibility Segregation) separates read and write operations. Use CQRS for scalability.
- Hexagonal architecture isolates business logic from external concerns. Apply hexagonal architecture for testability.
- The saga pattern manages distributed transactions across services. Implement saga pattern for data consistency.

### Comparative Explanation
- MapReduce, similar to divide-and-conquer algorithms, processes large datasets in parallel. Use MapReduce for big data.
- Sharding, like partitioning a database horizontally, distributes data across multiple servers. Implement sharding for performance.
- Data replication, which creates copies of data across systems like backup drives do, improves availability. Enable data replication for reliability.

## Edge Cases and Special Scenarios

### Previously Explained Terms
First paragraph: Containerization, which packages applications with dependencies, simplifies deployment.
Second paragraph: Use containerization for all production workloads.

**Status:** Should NOT flag second usage - term already explained
**Rule:** Track definitions per document or section

### Common Technical Terms in Technical Documentation
- Use the database to store records.
- Configure the server to handle requests.
- The network connects the systems.

**Status:** May NOT flag - basic terms in technical context
**Configuration:** Depends on target audience and documentation type

### Product-Specific Terminology
- Deploy using our FastScale technology.
- Enable AutoSync for automatic updates.
- Configure SmartCache for optimization.

**Status:** Should have explanation in product documentation
**Best Practice:** Define proprietary terms even if widely used internally

### Jargon in Code Comments
```javascript
// Implement debouncing to limit function calls
function debounce(func, delay) {
  // Implementation details
}
```

**Status:** Code context may be exempt
**Guideline:** Explain complex concepts even in code comments

### Academic or Research Terms
- Apply Bayesian inference for probability estimation.
- Use gradient descent optimization algorithm.
- Implement backpropagation for training.

**Status:** Should flag and explain for general audiences
**Exception:** May be acceptable in academic or research documentation

## Context-Specific Guidelines

### Developer Documentation
**Require Explanation:**
- Business domain concepts
- Emerging technologies
- Advanced patterns and practices
- Organization-specific terminology

**Often Acceptable:**
- Common programming terms (variables, functions, loops)
- Standard data structures (arrays, objects, maps)
- Basic web concepts (HTTP, URL, HTML)

### User-Facing Documentation
**Require Explanation:**
- ALL technical terms
- Industry-specific concepts
- Product-specific features
- Technical workflows

**Guideline:** Assume no technical knowledge

### API Documentation
**Require Explanation:**
- Authentication methods
- Data formats and protocols
- Rate limiting concepts
- Webhook mechanisms

**Often Acceptable:**
- HTTP methods (GET, POST, etc.)
- JSON/XML terminology
- Basic REST concepts (if API documentation)

### Architecture Documentation
**Require Explanation:**
- Specific architecture patterns
- Design decisions and trade-offs
- Technology choices and rationale
- Integration approaches

**Often Acceptable:**
- Standard architecture terms for technical audiences
- Common design patterns (Singleton, Factory, etc.)

## Testing Strategy

### Positive Tests (Should Trigger Warning)
1. First use of jargon without any explanation
2. Jargon in heading without body explanation
3. Jargon in list without context
4. Domain-specific terms without definition

### Negative Tests (Should NOT Trigger)
1. Jargon with appositive explanation
2. Jargon with parenthetical definition
3. Jargon with inline explanation
4. Previously explained jargon reused
5. Common terms in appropriate context

### Configuration Tests
1. Terms in exception list should not flag
2. Audience-specific thresholds respected
3. Document-type rules applied correctly
4. Custom organization terminology handled

## Real-World Examples

### Bad: Developer Guide
Set up the CI/CD pipeline to automate deployments. Configure the service mesh for observability. Implement the saga pattern for distributed transactions. Use CQRS for read/write optimization.

**Issues:** Multiple unexplained jargon terms, assumes expert knowledge
**Impact:** Excludes junior developers, increases onboarding time

### Good: Developer Guide
Set up the CI/CD (Continuous Integration/Continuous Deployment) pipeline, which automatically tests and deploys code changes. Configure the service mesh, a dedicated layer for service communication, for observability. Implement the saga pattern, which manages distributed transactions across services, for data consistency. Use CQRS (Command Query Responsibility Segregation), which separates read and write operations, for optimization.

**Improvements:** All terms explained, accessible to various skill levels
**Result:** Faster comprehension, broader audience reach

### Bad: Architecture Documentation
The system uses event sourcing with CQRS. Services communicate via a service mesh implementing mutual TLS. We apply hexagonal architecture with DDD principles. The saga orchestrator coordinates distributed transactions.

**Issues:** Dense jargon, no explanations, expert-only accessible
**Impact:** Limited team understanding, difficult onboarding

### Good: Architecture Documentation
The system uses event sourcing, which stores changes as a sequence of events, combined with CQRS (Command Query Responsibility Segregation), which separates read and write operations. Services communicate via a service mesh, a dedicated infrastructure layer, implementing mutual TLS, where both parties authenticate each other. We apply hexagonal architecture, which isolates business logic, with DDD (Domain-Driven Design) principles, which model software around business concepts. The saga orchestrator, which manages multi-service transactions, coordinates distributed operations.

**Improvements:** Each concept explained, clear architecture rationale
**Result:** Better team alignment, easier knowledge transfer

## Implementation Checklist

### For Technical Writers
- [ ] Identify jargon in your domain
- [ ] Create organization-specific jargon glossary
- [ ] Define explanation style for consistency
- [ ] Review with cross-functional team
- [ ] Test explanations with target audience
- [ ] Update exceptions list regularly
- [ ] Monitor feedback on clarity

### For Developers
- [ ] Configure Vale jargon detection rules
- [ ] Build custom jargon dictionary
- [ ] Set audience-appropriate thresholds
- [ ] Create explanation templates
- [ ] Integrate with documentation workflow
- [ ] Review flagged terms regularly
- [ ] Maintain glossary of approved terms

## Benefits of Explaining Jargon

**Accessibility:**
- Reduces knowledge barriers
- Speeds up onboarding
- Enables cross-functional collaboration
- Supports international teams

**Quality:**
- Improves documentation clarity
- Reduces ambiguity
- Ensures consistent terminology
- Maintains professional standards

**Efficiency:**
- Fewer clarification questions
- Reduced support burden
- Faster task completion
- Better knowledge retention

**Business Impact:**
- Broader product adoption
- Better customer experience
- Reduced training costs
- Improved team productivity

## Common Anti-Patterns

### Over-Correction
**Problem:** Explaining universally known terms
**Example:** "Click the button (a UI element you press)"
**Fix:** Define only genuinely unclear terms

### Inconsistent Application
**Problem:** Explaining some jargon but not others
**Example:** "Configure OAuth (authentication protocol)" then "Enable JWT"
**Fix:** Consistent explanation standards

### Circular Definitions
**Problem:** Using jargon to explain jargon
**Example:** "Implement CQRS (Command Query Responsibility Segregation)"
**Fix:** Explain what the concept does, not just the acronym expansion

### Over-Simplification
**Problem:** Losing technical accuracy in explanation
**Example:** "API (thing that connects stuff)"
**Fix:** Balance clarity with technical precision

### Missing Context
**Problem:** Defining without explaining why it matters
**Example:** "Blockchain is a distributed ledger"
**Fix:** "Blockchain, a distributed ledger that ensures transaction integrity, prevents data tampering"
