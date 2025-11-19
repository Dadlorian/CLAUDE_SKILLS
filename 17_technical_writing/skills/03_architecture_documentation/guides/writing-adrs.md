# Writing Architecture Decision Records (ADRs): Complete Guide

## What Are ADRs?

Architecture Decision Records (ADRs) are documents that capture important architectural decisions made during a project's lifetime, along with the context, rationale, and consequences.

**Key Definition**: An ADR is a short text file that documents one significant architectural decision and its justification.

### Why ADRs Matter

**Problem They Solve**:
- Why was this technology chosen?
- Why is this pattern used?
- Why did we reject that approach?
- What were the tradeoffs?

**Benefits**:
- Institutional memory preserved
- Onboarding new team members accelerated
- Future decisions informed by past reasoning
- Accountability established
- Alternatives considered and documented
- Consequences tracked over time

## ADR Formats

### Standard ADR Template (Lightweight)

Most popular format, endorsed by Thoughtworks:

```markdown
# ADR-XXX: Brief Title

## Status
Accepted | Pending | Rejected | Deprecated | Superseded By ADR-XXX

## Context
[What is the issue?]

## Decision
[What decision did we make?]

## Consequences
[What are the positive and negative outcomes?]

## Alternatives Considered
[What other options did we evaluate?]
```

### Extended ADR Template (Comprehensive)

For more complex decisions:

```markdown
# ADR-XXX: Decision Title

## Status
Accepted

## Context
[Describe the situation requiring decision]

## Decision
[Clearly state the decision]

## Rationale
[Why this decision was made]

## Consequences
### Positive Impacts
- Impact 1
- Impact 2

### Negative Impacts
- Impact 1
- Impact 2

## Alternatives Considered
### Alternative 1: Option A
Pros: ...
Cons: ...
Cost: ...

### Alternative 2: Option B
Pros: ...
Cons: ...
Cost: ...

## Related Decisions
- ADR-XXX: Related decision
- ADR-YYY: Another related decision

## Implementation Plan
[How will this be implemented?]

## Review Date
[When should this be reviewed?]

## Author
[Who proposed this decision?]
```

### Executive Summary Format

For high-level architectural decisions:

```markdown
# ADR-XXX: [Title]

## Overview
[1-2 sentence summary]

## Business Context
[Why this decision matters to the business]

## Technical Context
[Technical constraints and requirements]

## Decision
[What we're doing]

## Impact
[Business and technical impacts]

## Timeline
[Implementation schedule]

## Stakeholders
[Who needs to know/approve]

## Approval Status
[Sign-offs needed]
```

## ADR Lifecycle

### Phase 1: Create ADR (Proposed)

**When to create ADR**:
- Before making major architectural decisions
- When selecting technology that affects system
- When establishing architectural patterns
- When making cross-cutting decisions
- When creating new standards or conventions

**Process**:
1. Create ADR file: `adr-NNNN-short-title.md`
2. Fill out template with initial information
3. Share for team discussion
4. Mark status as "Proposed"

### Phase 2: Review and Discussion

**Review Process**:
1. Share ADR in pull request
2. Get team/stakeholder feedback
3. Discuss alternatives
4. Document additional considerations
5. Identify implementation approach

**Discussion Points**:
- Is the context clear?
- Is the decision justified?
- Have alternatives been fairly evaluated?
- Will this decision impact other teams?
- What are long-term maintenance implications?

### Phase 3: Decision (Accepted/Rejected)

**For Accepted Decisions**:
1. Update status to "Accepted"
2. Record decision date
3. Identify implementation owner
4. Plan implementation timeline
5. Merge ADR into main branch

**For Rejected Decisions**:
1. Update status to "Rejected"
2. Document why rejected
3. Keep in repository for historical reference
4. Merge for future reference

### Phase 4: Implementation

**Tracking Implementation**:
- Create tickets for implementation work
- Link tickets to ADR
- Document any deviations from decision
- Track timeline and blockers

**Communication**:
- Notify affected teams
- Schedule implementation meetings
- Provide resources and guidance
- Address questions and concerns

### Phase 5: Review and Update

**Regular Review Cycle**:
- Schedule quarterly reviews
- Assess if decision still valid
- Check if consequences materialized as expected
- Identify lessons learned

**Status Updates**:
- **Superseded**: Another ADR replaced this decision
- **Deprecated**: Still valid but no longer recommended
- **Accepted**: Still current and valid

## Writing Effective ADRs

### Guideline 1: One Decision Per ADR

**Good Practice**:
- ADR-001: Use PostgreSQL for primary database
- ADR-002: Implement caching with Redis
- ADR-003: Use microservices architecture

**Avoid**:
- ADR-001: Database and caching strategy (too broad)

### Guideline 2: Use Clear, Specific Language

**Good Writing**:
```
We will use PostgreSQL as our primary relational database
because it offers ACID compliance, strong JSON support,
and excellent scalability for our data volumes.
```

**Avoid**:
```
We need a good database. We think PostgreSQL is cool.
```

### Guideline 3: Show Your Work

**Include**:
- Context: What problem does this solve?
- Constraints: What limitations exist?
- Options: What alternatives did you consider?
- Reasoning: Why is this best choice?
- Tradeoffs: What are you giving up?

**Don't Assume**:
- Readers don't know the problem context
- Everyone agrees on what's important
- Future readers will remember why

### Guideline 4: Be Honest About Tradeoffs

Every decision involves tradeoffs. Be explicit:

```
## Consequences

### Positive
+ Better performance than ORM-based approach
+ Type-safe queries
+ Reduced runtime errors
+ Easier to optimize for large datasets

### Negative
- Steeper learning curve
- More verbose code initially
- Requires schema management
- Team skill investment needed
```

### Guideline 5: Evaluate Alternatives Fairly

**Good Alternative Analysis**:
```
## Alternatives Considered

### Option A: PostgreSQL
Pros: ACID, scalability, JSON support, cost-effective
Cons: Less flexibility for unstructured data
Risk: Potential scaling at 100M+ rows

### Option B: MongoDB
Pros: Flexible schema, good for unstructured data
Cons: Eventual consistency, higher operational complexity
Risk: Cost escalation with data growth

### Option C: DynamoDB
Pros: Managed, auto-scaling, high availability
Cons: Limited query patterns, higher costs
Risk: Vendor lock-in with AWS
```

**Bad Alternative Analysis**:
```
We considered MongoDB but it's not as good.
```

## Common ADR Scenarios

### Scenario 1: Technology Selection

```markdown
# ADR-001: Use React for Frontend Framework

## Status
Accepted

## Context
The team needs to build a modern web application with:
- Dynamic user interface
- Real-time data updates
- Support for mobile-responsive design
- Integration with REST API
- Multiple development team members

Current situation: No frontend framework standardized
Decision required by: Project kickoff (2024-01-15)

## Decision
We will use React as our primary frontend framework.

## Rationale
React provides:
- Large ecosystem and community support
- Strong tooling and dev experience (Create React App, Vite)
- Component-based architecture for maintainability
- Excellent documentation and learning resources
- Team familiarity (all members have React experience)
- Strong performance characteristics
- Active job market for React developers

## Consequences

### Positive
+ Large developer pool for hiring
+ Mature ecosystem (React Router, Redux, Axios, etc.)
+ Strong community support and documentation
+ Fast rendering with Virtual DOM
+ Works well with REST APIs
+ Good TypeScript support

### Negative
- JavaScript bundle size can be large if not optimized
- Requires build step (webpack, Vite, etc.)
- Learning curve for new team members
- State management complexity for large apps

## Alternatives Considered

### Vue.js
Pros: Lighter, gentler learning curve, excellent documentation
Cons: Smaller ecosystem, fewer job opportunities, smaller community

### Angular
Pros: Complete framework, strong typing, large enterprise adoption
Cons: Steep learning curve, verbose code, heavy bundle size

### Svelte
Pros: Simplest syntax, smallest bundle, best performance
Cons: Smaller community, newer, fewer libraries available

## Related Decisions
- ADR-002: Use Redux for state management
- ADR-003: Use TypeScript with React

## Implementation Plan
1. Set up Create React App project (Week 1)
2. Define component structure and standards (Week 2)
3. Set up development environment and CI/CD (Week 3)
4. Begin core feature development (Week 4+)

## Review Date
2024-07-15 (6 months after implementation)
```

### Scenario 2: Architectural Pattern Decision

```markdown
# ADR-003: Adopt Microservices Architecture

## Status
Accepted

## Context
Current monolithic application:
- Single codebase of 500K lines of code
- Deployment cycle: 2 weeks (very slow)
- Different services have different scaling requirements
- Teams are siloed and stepping on each other's toes
- Database is becoming a bottleneck
- Technology stack is locked (Java 8, old libraries)

Requirements:
- Faster deployment cycles (weekly or daily)
- Independent scaling per service
- Technology flexibility per team
- Better separation of concerns
- Improved development velocity

## Decision
We will decompose our monolithic application into microservices,
with the following initial services:
- User Service (authentication, profiles)
- Order Service (order processing, management)
- Product Service (catalog, search)
- Payment Service (payment processing)
- Notification Service (email, SMS, push)
- Inventory Service (stock management)

## Rationale
Microservices architecture enables:
- Independent deployment cycles
- Technology flexibility (each team can choose)
- Isolated scaling (only scale what's needed)
- Smaller codebases (easier to understand)
- Team autonomy and faster development
- Clear separation of business domains

## Consequences

### Positive
+ Faster deployment cycles (weekly to daily)
+ Independent scaling reduces costs
+ Technology flexibility enables optimization
+ Smaller teams, better focus
+ Easier testing of individual services
+ Better failure isolation

### Negative
- Operational complexity increases significantly
- Network latency between services
- Data consistency challenges (distributed transactions)
- Debugging across services more difficult
- DevOps expertise required
- Initial development slower during transition
- Monitoring and logging complexity increases
- Significant infrastructure investment needed

## Alternatives Considered

### Modular Monolith
Pros: Simpler operational model, still deployable as units
Cons: Doesn't solve deployment frequency problem, scaling issues remain

### Serverless Functions
Pros: No infrastructure management, auto-scaling
Cons: Vendor lock-in, cold start issues, cost unpredictability

## Implementation Plan

### Phase 1: Infrastructure Setup (Months 1-2)
- Set up Kubernetes cluster
- Implement container orchestration
- Set up monitoring and logging
- Create service templates

### Phase 2: Initial Migration (Months 3-6)
- Extract User Service
- Extract Order Service
- Set up inter-service communication

### Phase 3: Full Migration (Months 7-12)
- Extract remaining services
- Decommission monolith gradually
- Optimize communication patterns

### Phase 4: Optimization (Ongoing)
- Performance tuning
- Cost optimization
- Developer experience improvements

## Related Decisions
- ADR-004: Use Docker containers for deployment
- ADR-005: Implement API Gateway pattern
- ADR-006: Use event-driven communication for async operations

## Training Required
- Kubernetes and container orchestration
- Distributed systems concepts
- Event-driven architecture patterns
- Service mesh (Istio/Linkerd)

## Review Date
2025-01-15 (12 months after decision)
```

### Scenario 3: Technical Implementation Decision

```markdown
# ADR-005: Use Typed GraphQL for API Communication

## Status
Accepted

## Context
Current REST API approach shows limitations:
- Over-fetching: Clients receive excess data
- Under-fetching: Multiple requests needed for related data
- Version management: Maintaining multiple API versions difficult
- Type safety: JavaScript frontend lacks type information
- Documentation: Constantly out of sync with implementation

Team capabilities:
- Strong TypeScript experience
- GraphQL knowledge present in 3/8 developers
- No GraphQL infrastructure currently

## Decision
We will use GraphQL as our primary API mechanism, with:
- Apollo Server for backend
- Apollo Client for frontend
- Generated TypeScript types for both client and server

## Rationale
GraphQL benefits:
- Clients request exactly what they need (no over-fetching)
- Reduced network traffic and latency
- Type-safe client and server
- Self-documenting through schema
- Real-time capabilities with subscriptions
- Better developer experience with tooling

## Consequences

### Positive
+ Reduced bandwidth (exact data requested)
+ Single endpoint instead of REST resource mapping
+ Strong typing across full stack
+ Better developer tools (GraphQL Playground)
+ Easier API evolution
+ Reduced client-side logic for data normalization

### Negative
- Learning curve (all developers need GraphQL knowledge)
- More complex caching strategies
- Query complexity management required
- Larger bundle size (Apollo Client ~34KB gzip)
- Monitoring and debugging more complex

## Alternatives Considered

### Stay with REST
Pros: Well-known, simpler
Cons: Doesn't solve over/under-fetching, versioning issues remain

### Use gRPC
Pros: High performance, strong typing
Cons: Not suitable for browser clients, steeper learning curve

## Implementation Plan
1. GraphQL Workshop (Week 1)
2. Set up Apollo Server (Week 2)
3. Implement initial schema (Weeks 3-4)
4. Migrate frontend to Apollo Client (Weeks 5-6)

## Training
- GraphQL fundamentals workshop
- Apollo Server best practices
- Apollo Client patterns and hooks
```

## ADR File Organization

### Directory Structure

```
project-root/
├── docs/
│   ├── adr/
│   │   ├── adr-0001-record-architecture-decisions.md
│   │   ├── adr-0002-use-postgres-for-database.md
│   │   ├── adr-0003-adopt-microservices.md
│   │   ├── adr-0004-use-docker-containers.md
│   │   └── adr-INDEX.md
│   └── README.md
```

### Naming Convention

`adr-NNNN-decision-title-slug.md`

- `NNNN`: 4-digit number (0001, 0002, etc.)
- `decision-title-slug`: Lowercase with hyphens
- Example: `adr-0008-use-postgresql-jsonb-for-configuration.md`

### Index File

Maintain an `adr-INDEX.md` listing all ADRs:

```markdown
# Architecture Decision Records

## Active Decisions

- [ADR-0001: Record Architecture Decisions](adr-0001-record-architecture-decisions.md) - Accepted
- [ADR-0002: Use PostgreSQL for Database](adr-0002-use-postgres-for-database.md) - Accepted
- [ADR-0003: Adopt Microservices Architecture](adr-0003-adopt-microservices.md) - Accepted
- [ADR-0004: Use Docker Containers](adr-0004-use-docker-containers.md) - Accepted

## Superseded Decisions

- [ADR-0005: Use MySQL Database](adr-0005-use-mysql-database.md) - Superseded by ADR-0002

## Rejected Decisions

- [ADR-0006: Implement CQRS Pattern](adr-0006-cqrs-pattern.md) - Rejected
```

## Best Practices

### Practice 1: Create ADR for First ADR

Your first ADR should be about recording architectural decisions:

```markdown
# ADR-0001: Record Architecture Decisions

## Status
Accepted

## Context
We need to record architectural decisions made on this project.

## Decision
We will use Architecture Decision Records, as described by Michael Nygard.

## Consequences
See Michael Nygard's article, linked below.

## References
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
```

### Practice 2: Link Related ADRs

Show connections between decisions:

```markdown
## Related Decisions
- Extends: ADR-0002 (Technology Platform)
- Contradicts: ADR-0004 (Frontend Framework)
- Superseded by: ADR-0008 (Updated Technology Standards)
```

### Practice 3: Record Decisions Early

Don't wait until implementation is complete. Record decisions:
- During design phase
- Before implementation starts
- As soon as decision is made

### Practice 4: Include Timestamps

```markdown
## Dates
- **Proposed**: 2024-01-15
- **Accepted**: 2024-01-22
- **Implementation Started**: 2024-02-01
- **Implementation Complete**: 2024-06-30
- **Next Review**: 2025-01-15
```

### Practice 5: Capture Decision Context

Future you won't remember why. Include:
- Problem statement
- Business constraints
- Technical constraints
- Stakeholders involved
- Timeline and urgency

## ADR Checklist

- [ ] Title is clear and specific
- [ ] ADR number is assigned sequentially
- [ ] Status is clearly indicated
- [ ] Context section explains the problem
- [ ] Decision is stated clearly and concisely
- [ ] Rationale explains the "why"
- [ ] Consequences section includes both positive and negative impacts
- [ ] All viable alternatives are listed
- [ ] Pros and cons are fair for all alternatives
- [ ] Related ADRs are referenced
- [ ] Implementation plan is described (if applicable)
- [ ] Timeline is specified
- [ ] Author/proposer is identified
- [ ] Review/decision date is included
- [ ] Stored in version control
- [ ] Added to ADR index
- [ ] Team has reviewed and approved

## Common Mistakes to Avoid

### Mistake 1: Vague Context
**Bad**: "We need to choose a database"
**Good**: "We're building a real-time inventory system that needs to handle 10K requests/sec with sub-100ms query times"

### Mistake 2: Unfair Alternative Comparison
**Bad**: "MongoDB is too slow and inefficient"
**Good**: "PostgreSQL: ACID guarantees, complex queries. MongoDB: Flexible schema, but eventual consistency"

### Mistake 3: Missing Consequences
**Bad**: "We'll use Kubernetes. It's great."
**Good**: "Consequences: +Better scaling, +Industry standard. -Operational complexity, -Learning curve"

### Mistake 4: Stale ADRs
**Bad**: ADR never updated or reviewed
**Good**: Regular review cycle, status updates, superseding decisions documented

### Mistake 5: Too Much Detail
**Bad**: 3000-word essay
**Good**: Concise, scannable, one page maximum

## Tools for ADR Management

### Simple Approach
- Markdown files in git
- Pull requests for review
- GitHub issues for discussion

### Dedicated Tools
- **adr-tools**: Command-line tool to manage ADRs
- **ADR Server**: Web interface for ADRs
- **Structurizr**: Integrates decisions with diagrams

### Implementation
```bash
# Using adr-tools
adr new "Use PostgreSQL for primary database"
adr list
adr status adr-0002
adr supersede adr-0002 adr-0010
```

## ADR Template Checklist

Before publishing:

- [ ] Clear, specific title
- [ ] Appropriate status assigned
- [ ] Context explains problem thoroughly
- [ ] Decision is stated clearly
- [ ] Rationale justifies the decision
- [ ] Consequences include positives and negatives
- [ ] Alternatives fairly evaluated
- [ ] Related ADRs linked
- [ ] Implementation plan described
- [ ] Timeline realistic
- [ ] Review date set
- [ ] Proper numbering
- [ ] Stored in correct directory
- [ ] Referenced in index
- [ ] Team has reviewed

---

**Resources**:
- Original ADR Concept: Michael Nygard
- adr-tools: https://github.com/npryce/adr-tools
- Thoughtworks Technology Radar
- Azure Architecture Decision Records
