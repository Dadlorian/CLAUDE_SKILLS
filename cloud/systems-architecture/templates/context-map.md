# Context Map: [System/Domain Name]

**Date**: YYYY-MM-DD
**Author**: [Name]
**Version**: 1.0
**Status**: [Draft | Active | Deprecated]

---

## Purpose

This context map documents the relationships between bounded contexts in our system, defining how they integrate and communicate. It serves as a strategic design tool for understanding dependencies, team boundaries, and integration patterns.

---

## Bounded Contexts Overview

### Summary Table

| Context Name | Team Owner | Type | Primary Responsibility | Status |
|--------------|------------|------|------------------------|--------|
| [Context1] | [Team A] | Core | [Primary capability] | Production |
| [Context2] | [Team B] | Supporting | [Primary capability] | Production |
| [Context3] | [Team C] | Generic | [Primary capability] | Planning |

---

## Bounded Context Details

### Context: [ContextName1]

**Team**: [Team Name]
**Subdomain Type**: [Core | Supporting | Generic]
**Business Purpose**: [Why this context exists from business perspective]

#### Ubiquitous Language
Key terms and their definitions within this context:
- **[Term1]**: [Definition]
- **[Term2]**: [Definition]
- **[Term3]**: [Definition]

#### Key Aggregates
- [Aggregate1]
- [Aggregate2]
- [Aggregate3]

#### Key Services (Microservices)
- [Service1]: [Purpose]
- [Service2]: [Purpose]

#### Data Stores
- [Database1]: [Type, purpose]
- [Cache/Queue]: [Type, purpose]

#### Team Structure
- Product Owner: [Name]
- Tech Lead: [Name]
- Team Size: [Number] engineers
- Location: [Location/Timezone]

---

### Context: [ContextName2]

**Team**: [Team Name]
**Subdomain Type**: [Core | Supporting | Generic]
**Business Purpose**: [Why this context exists]

#### Ubiquitous Language
- **[Term1]**: [Definition - may differ from Context1!]
- **[Term2]**: [Definition]

#### Key Aggregates
- [Aggregate1]
- [Aggregate2]

#### Key Services
- [Service1]: [Purpose]

#### Data Stores
- [Database1]: [Type, purpose]

#### Team Structure
- Product Owner: [Name]
- Tech Lead: [Name]
- Team Size: [Number] engineers

---

## Context Relationships

[For each relationship between contexts, document the pattern and integration details]

---

### Relationship: [Context1] ↔️ [Context2]

#### Relationship Type: **Partnership**

**Description**: Both teams collaborate on shared model and integration. Equal mutual dependency.

**Collaboration Model**:
- Joint planning sessions: [Frequency]
- Shared repository: [Yes/No, link if yes]
- Coordinated releases: [Yes/No]

**Shared Components**:
- [Component1]: [Purpose, ownership]
- [Component2]: [Purpose, ownership]

**Integration Points**:
```
API: [Context1] exposes /api/v1/[resource]
     [Context2] consumes this API

Events: [Context2] publishes [EventName]
        [Context1] subscribes to [EventName]
```

**Communication**:
- Primary: [Slack channel, email list]
- Meetings: [Frequency and format]

**Challenges**:
- [Challenge1]: [Description and mitigation]
- [Challenge2]: [Description and mitigation]

---

### Relationship: [Context1] → [Context2]

#### Relationship Type: **Shared Kernel**

**Description**: Limited shared subset of the domain model. Carefully managed shared code/database.

**Shared Scope**:
```
Shared Library: [library-name]
  Contains:
    - [SharedModel1]: [Purpose]
    - [SharedModel2]: [Purpose]
    - [Utility1]: [Purpose]

  Versioning: [Semantic versioning strategy]
  Ownership: [Joint ownership rules]
  Change Process: [How changes are approved]
```

**Integration Points**:
- Both contexts depend on: `shared-library v2.x`
- Database: [Shared tables if any]

**Governance**:
- Changes require approval from: [Both teams]
- Breaking changes: [Process for handling]
- Testing: [Joint integration test suite]

**Risks & Mitigations**:
- Risk: Tight coupling reduces autonomy
- Mitigation: Keep shared kernel minimal, consider splitting if grows

---

### Relationship: [Context1] → [Context2]

#### Relationship Type: **Customer-Supplier**

**Description**: [Context2] (Downstream/Customer) depends on [Context1] (Upstream/Supplier). Downstream defines needs, upstream delivers.

**Upstream Context**: [Context1] (Supplier)
**Downstream Context**: [Context2] (Customer)

**Contract Definition**:
```
API Contract: OpenAPI 3.0 specification
  Location: [URL or repo path]
  Version: v2.1
  Breaking change policy: 6 months deprecation notice

Events Contract: AsyncAPI specification
  Events provided:
    - [EventName1]: [Schema version, purpose]
    - [EventName2]: [Schema version, purpose]
```

**Service Level Agreement**:
- Availability: 99.9%
- Latency P95: < 200ms
- Support: [Response time for issues]

**Change Management**:
1. Downstream requests features via: [Process, e.g., Jira tickets]
2. Upstream prioritizes based on: [Criteria]
3. Upstream notifies of changes: [How and when]
4. Backward compatibility: [Policy]

**Integration Pattern**:
```
Synchronous:
  - [Context2] calls REST API of [Context1]
  - Circuit breaker configured
  - Timeout: 5 seconds
  - Retry: 3 attempts with exponential backoff

Asynchronous:
  - [Context1] publishes to topic: [topic-name]
  - [Context2] subscribes and processes events
```

**Responsibilities**:
- **Upstream ([Context1])**:
  - Maintain API stability
  - Provide documentation
  - Notify of breaking changes 6 months in advance

- **Downstream ([Context2])**:
  - Define requirements clearly
  - Adapt to API changes within grace period
  - Provide feedback on API usability

---

### Relationship: [Context1] → [Context2]

#### Relationship Type: **Conformist**

**Description**: [Context2] (Downstream) conforms to model of [Context1] (Upstream). Upstream has no motivation to support downstream.

**Upstream Context**: [Context1]
**Downstream Context**: [Context2]

**Why Conformist**:
[Explain why this pattern was chosen, e.g.:]
- Upstream is third-party service we cannot influence
- Cost of translation layer outweighs benefit
- Upstream model is good enough for our needs

**Conformance Details**:
```
[Context2] uses upstream's data model directly:
  - [UpstreamModel1]: Used as-is in downstream
  - [UpstreamModel2]: Mapped to [DownstreamConcept]
```

**Integration**:
- API: [Context1] provides [API endpoint]
- [Context2] calls directly without abstraction
- No anti-corruption layer

**Risks**:
- Upstream changes can break downstream
- Downstream accepts upstream's terminology even if suboptimal
- Limited ability to evolve independently

**Mitigation**:
- Version pinning: [Strategy]
- Monitor upstream changes: [How]
- Consider ACL if conformance becomes painful

---

### Relationship: [Context1] → [ACL] → [Context2]

#### Relationship Type: **Anti-Corruption Layer (ACL)**

**Description**: [Context2] protects its domain model from [Context1] by translating between models.

**Upstream Context**: [Context1] (potentially problematic model)
**Downstream Context**: [Context2] (protected by ACL)

**Why ACL Needed**:
[Explain the motivation, e.g.:]
- Upstream uses terminology that conflicts with our ubiquitous language
- Upstream model is complex/legacy and we want simpler model
- Upstream is third-party with frequent breaking changes
- We plan to replace upstream in future (ACL localizes changes)

**ACL Implementation**:
```
Location: [Service name or module]
Technology: [e.g., Adapter pattern, Facade, Translator service]

Translation Logic:
  Upstream Model       →  Translation  →  Downstream Model
  [UpstreamEntity1]    →  [Transform]  →  [DownstreamEntity1]
  [UpstreamEntity2]    →  [Transform]  →  [DownstreamEntity2]

Example:
  Upstream: LegacyOrder { customer_id, items[], total_amt }
  Translation: Map to domain model
  Downstream: Order { customerId, lineItems[], totalAmount }
```

**Integration Pattern**:
```
[Context2] → [ACL Service/Module] → [Context1]

ACL Responsibilities:
  - Translate models between contexts
  - Handle upstream errors gracefully
  - Cache/buffer if needed
  - Insulate downstream from upstream changes
```

**Code Example**:
```java
// ACL Adapter
public class LegacyOrderAdapter {
  private final LegacyOrderClient upstream;

  public Order fetchOrder(OrderId id) {
    LegacyOrder legacyOrder = upstream.getOrder(id.value());
    return translateToOrder(legacyOrder);
  }

  private Order translateToOrder(LegacyOrder legacy) {
    return Order.builder()
      .orderId(OrderId.of(legacy.getId()))
      .customerId(CustomerId.of(legacy.getCustomer_id()))
      .lineItems(translateLineItems(legacy.getItems()))
      .totalAmount(Money.of(legacy.getTotal_amt(), "USD"))
      .build();
  }
}
```

**Maintenance**:
- Owner: [Downstream team]
- Update when: [Upstream changes OR downstream model evolves]
- Testing: [Integration tests ensuring correct translation]

---

### Relationship: [Context1] → [Context2, Context3, ...]

#### Relationship Type: **Open Host Service**

**Description**: [Context1] provides a well-defined protocol/API as a service for all consumers.

**Host Context**: [Context1]
**Consumer Contexts**: [Context2], [Context3], [Context4]

**Service Definition**:
```
API Type: REST + Events
Documentation: [OpenAPI spec URL]
Versioning: [Strategy, e.g., URL versioning /v1, /v2]

REST Endpoints:
  GET /api/v1/[resources]
  POST /api/v1/[resources]
  [... full API surface]

Events Published:
  - [EventName1]: [Schema, topic]
  - [EventName2]: [Schema, topic]
```

**Published Language**:
[Well-documented, standardized integration contract]
- Schema: [JSON Schema | Protobuf | Avro]
- Schema Registry: [URL]
- Backward compatibility: [Guaranteed for N versions]

**Service Level Objectives**:
- Availability: 99.95%
- Latency P95: < 150ms
- Throughput: [X] req/sec

**Consumer Onboarding**:
1. Read documentation: [Link]
2. Obtain API key: [Process]
3. Test in sandbox: [URL]
4. Production access: [Approval process]

**Support**:
- Documentation: [Link]
- Sample code: [Repo]
- Slack channel: #[channel-name]
- SLA for breaking issues: 4 hours response

**Consumers**:
| Consumer | Use Case | Integration Type | SLA Tier |
|----------|----------|------------------|----------|
| [Context2] | [Purpose] | REST + Events | Gold |
| [Context3] | [Purpose] | Events only | Silver |

---

### Relationship: [Context1] ↔️ [Context2]

#### Relationship Type: **Published Language**

**Description**: Shared, well-documented integration language used by multiple contexts.

**Published Language Definition**:
```
Format: [JSON | XML | Protobuf | Avro]
Schema Location: [Schema registry URL or Git repo]
Version: 2.0

Standard Models:
  - [CommonModel1]: [Purpose, schema link]
  - [CommonModel2]: [Purpose, schema link]
  - [CommonModel3]: [Purpose, schema link]
```

**Usage**:
- [Context1] publishes events using this language
- [Context2] consumes events using this language
- [Context3] also uses for integration

**Governance**:
- Schema changes: [RFC process or committee approval]
- Breaking changes: [Versioning strategy]
- Backward compatibility: [Policy]

**Documentation**:
- Schema docs: [Link]
- Examples: [Link to sample messages]
- Migration guides: [For version upgrades]

---

### Relationship: [Context1] | [Context2]

#### Relationship Type: **Separate Ways**

**Description**: No integration needed between these contexts. They operate independently.

**Contexts**: [Context1] and [Context2]

**Why Separate**:
- No business need for integration
- Different business domains with no overlap
- Different organizations/customers

**Future Considerations**:
- Monitor for: [Signals that integration might become needed]
- Re-evaluate: [When or under what conditions]

---

## Context Map Diagram

[Visual representation of all contexts and their relationships]

```
                    +------------------+
                    |   Context1       |
                    |   (Core Domain)  |
                    |   Team: Alpha    |
                    +------------------+
                            |
              Partnership   |   Customer-Supplier
                           |
        +------------------+------------------+
        |                                     |
        v                                     v
+------------------+                +------------------+
|   Context2       |    ACL         |   Context3       |
|   (Supporting)   |--------------->|   (Generic)      |
|   Team: Beta     |                |   Team: Gamma    |
+------------------+                +------------------+
        |
        | Open Host Service
        |
        v
+------------------+
|   Context4       |
|   (Supporting)   |
|   Team: Delta    |
+------------------+
```

---

## Strategic Design Insights

### Core Domain Investment
**Core Domains**: [List core contexts]
- Invest most engineering resources here
- Build in-house with best engineers
- Optimize for flexibility and evolution

**Supporting Domains**: [List supporting contexts]
- Invest moderate resources
- Build in-house but with less perfection
- Can outsource if needed

**Generic Domains**: [List generic contexts]
- Minimal investment
- Prefer COTS/SaaS solutions
- Build only if no suitable alternative

---

### Integration Complexity Hotspots

**High Complexity**:
- [Context1] ↔️ [Context2]: [Why complex, plan to simplify]
- [Context3] → [Context4]: [Why complex, plan to simplify]

**Medium Complexity**:
- [Context A] → [Context B]: [Description]

**Low Complexity**:
- [Context X] → [Context Y]: [Description]

---

### Team Dependencies

**High Dependency** (Frequent coordination needed):
- Team Alpha ↔️ Team Beta: [Mitigation: Weekly sync, shared Slack]

**Medium Dependency**:
- Team Beta → Team Gamma: [Customer-Supplier with quarterly planning]

**Low Dependency** (Async integration):
- Team Alpha → Team Delta: [Event-driven, minimal coordination]

---

### Evolution & Future State

#### Current Pain Points
1. [Pain point 1]: [Description and impact]
2. [Pain point 2]: [Description and impact]

#### Planned Changes (Next 6 Months)
1. **[Change 1]**: [e.g., Introduce ACL between Context1 and Context3]
   - Why: [Reduce coupling]
   - When: Q2 2025
   - Owner: Team Beta

2. **[Change 2]**: [e.g., Split Context2 into two bounded contexts]
   - Why: [Context grew too large, different business capabilities]
   - When: Q3 2025
   - Owner: Team Beta

#### Long-Term Vision (12+ Months)
- [Vision 1]: [e.g., Full event-driven architecture across all contexts]
- [Vision 2]: [e.g., Replace legacy Context4 with modern implementation]

---

## Governance & Ownership

### Context Map Maintenance
**Owner**: [Architecture team or specific person]
**Review Cadence**: [Quarterly or after major changes]
**Update Process**: [How to propose changes to context boundaries]

### Decision-Making
**Strategic Decisions** (new contexts, major refactoring):
- Escalation: Architecture review board
- Process: [RFC process or ADR]

**Tactical Decisions** (integration patterns, API changes):
- Owner: Respective teams
- Coordination: Via customer-supplier relationship

---

## References

- **Domain Vision Statement**: [Link]
- **Architecture Decision Records**: [Link to ADR repository]
- **Service Catalog**: [Link to all services]
- **API Documentation**: [Link to API docs]
- **Event Catalog**: [Link to event schemas]

---

## Change History

| Date | Change | Reason | Author |
|------|--------|--------|--------|
| YYYY-MM-DD | Initial context map | Project kickoff | [Name] |
| YYYY-MM-DD | Added Context4 | New feature launch | [Name] |
| YYYY-MM-DD | Changed Context1-Context2 from Conformist to ACL | Reduce coupling | [Name] |

---

**Last Review**: YYYY-MM-DD
**Next Review**: YYYY-MM-DD
**Status**: [Current | Outdated - needs update]
