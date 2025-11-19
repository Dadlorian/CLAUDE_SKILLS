# Diagram Types in Architecture Documentation - When to Use Each

## Overview

Different diagram types serve different purposes in architecture documentation. This guide helps you choose the right diagram for your communication goal.

---

## 1. Sequence Diagrams

### Purpose
Show the interaction between actors and systems over time, emphasizing the order and flow of interactions.

### When to Use
- Explaining user workflows and interactions
- Documenting API call sequences
- Showing request-response cycles
- Explaining complex business processes
- Debugging interaction issues
- Documenting integration points

### Key Elements
- Actors/Participants (vertical lifelines)
- Messages (arrows showing interaction)
- Time progression (top to bottom)
- Activation boxes (showing when actors are active)

### Example: E-Commerce Order Placement

```
Customer    Browser      API Server    Database    Payment Service
   |           |             |            |              |
   |-- Place Order ---------->|            |              |
   |           |             |            |              |
   |           |         Validate Order   |              |
   |           |             |--Store--->|              |
   |           |             |<--OK------|              |
   |           |             |            |              |
   |           |        Process Payment --|------------>|
   |           |             |            |         Auth & Charge
   |           |             |            |<-----------|
   |           |        Store in DB       |              |
   |           |             |--Store--->|              |
   |           |             |<--Confirm-|              |
   |           |<--Success---|            |              |
   |<--Order Confirmed------|            |              |
   |           |             |            |              |
```

### Best Practices
- Keep sequences simple (5-7 interactions maximum)
- Use meaningful message labels
- Include time-dependent conditions (async operations, timeouts)
- Show error scenarios separately
- Add notes explaining complex interactions
- Group related interactions in reference frames

### Avoid
- Too many participants (more than 6-7)
- Overly detailed implementation steps
- Non-sequenced interactions (use state diagrams instead)
- Mixing multiple scenarios in one diagram

### Tools
- Draw.io (Sequence template)
- Mermaid (sequenceDiagram)
- PlantUML (@startuml ... @enduml)
- LucidChart
- Enterprise Architect

---

## 2. Flow Diagrams (Flowcharts)

### Purpose
Show decision points, branching logic, and process flows with alternative paths.

### When to Use
- Documenting algorithms and decision logic
- Showing error handling paths
- Explaining conditional workflows
- Process automation flows
- User journey with decision points
- Approval and review workflows

### Key Elements
- Start/End (oval/rounded rectangle)
- Process (rectangle)
- Decision (diamond)
- Data (parallelogram)
- Flow arrows showing direction

### Example: Order Processing Flow

```
        ┌─────────┐
        │  START  │
        └────┬────┘
             │
        ┌────▼────────────┐
        │ Receive Order   │
        └────┬────────────┘
             │
        ┌────▼─────────────────┐
        │ Validate Stock       │◄─────────┐
        └────┬────────────────┬┘          │
             │              NO│           │
            YES              │           │
             │               │        Notify
             │          ┌────▼──────┐  Customer
             │          │ Out Stock?│
             │          └────┬──────┘
             │              YES
        ┌────▼──────────────┐│
        │Check Inventory    ││
        │Update             ││
        └────┬──────────────┘│
             │               │
        ┌────▼──────────────┐│
        │ Process Payment   ││
        └────┬──────────────┤│
             │              │└─────┐
        ┌────▼──────────────┐      │
        │ Ship Order       │      │
        └────┬──────────────┘      │
             │                     │
        ┌────▼──────────────┐      │
        │ Send Confirmation│      │
        └────┬──────────────┘      │
             │                     │
        ┌────▼──────────────┐      │
        │ Log Event         │      │
        └────┬──────────────┘      │
             │                     │
             │              ┌──────▼─────┐
             │              │ Inform User│
             │              │ Try Later  │
             │              └────┬───────┘
             │                   │
        ┌────▼─────┐        ┌────▼──┐
        │   END    │        │ RETRY │
        └──────────┘        └───────┘
```

### Best Practices
- Use standard symbols consistently
- Keep decision logic simple (2-3 branches)
- Label all decision outcomes
- Show all possible paths
- Group related steps
- Use color to highlight different types of steps

### Avoid
- Crossing flow lines (rearrange to prevent)
- Too many decision points (refactor into sub-processes)
- Mixing different abstraction levels
- Implicit flows

### Tools
- Draw.io (Flowchart template)
- Lucidchart
- OmniGraffle
- Visio
- Mermaid (flowchart syntax)

---

## 3. Entity-Relationship Diagrams (ER Diagrams)

### Purpose
Show data entities, their attributes, and relationships between them.

### When to Use
- Documenting database schema
- Explaining data model structure
- Showing entity relationships
- Data validation documentation
- Database migration planning
- Domain modeling

### Key Elements
- Entity (rectangle)
- Attribute (oval in Chen notation, column in crow's foot)
- Relationship (line with cardinality indicators)
- Cardinality (1:1, 1:N, M:N)

### Example: E-Commerce Data Model

```
┌─────────────────────┐         ┌──────────────────┐
│       USER          │ 1    N  │     ORDER        │
├─────────────────────┤◄────────┤──────────────────┤
│ user_id (PK)        │         │ order_id (PK)    │
│ email               │         │ user_id (FK)     │
│ name                │         │ order_date       │
│ created_at          │         │ total_amount     │
└─────────────────────┘         └────┬─────────────┘
                                     │
                               1     │      N
                          ┌──────────┘
                          │
                    ┌─────▼──────────────┐
                    │   ORDER_ITEM       │
                    ├────────────────────┤
                    │ order_item_id (PK) │
                    │ order_id (FK)      │
                    │ product_id (FK)    │
                    │ quantity           │
                    │ unit_price         │
                    └─────┬──────────────┘
                          │
                          │ N     1 ┌──────────────────┐
                          └────────►│    PRODUCT       │
                                    ├──────────────────┤
                                    │ product_id (PK)  │
                                    │ name             │
                                    │ description      │
                                    │ price            │
                                    │ stock_quantity   │
                                    └──────────────────┘

Legend:
─────► One-to-Many (1:N)
◄─────► One-to-One (1:1)
M◄────►N Many-to-Many (M:N)
```

### Relationship Types

**Crow's Foot Notation:**
```
─── One (and only one)
──O One or Zero
──<  Many
──< One or More
```

### Best Practices
- Show primary keys (PK) and foreign keys (FK)
- Include important attributes
- Clearly mark cardinality
- Group related entities
- Use meaningful entity names
- Use crow's foot notation for clarity
- Document constraints and business rules

### Avoid
- Including all attributes (focus on key ones)
- Crossing relationship lines unnecessarily
- Complex many-to-many relationships without explanation
- Missing cardinality indicators

### Tools
- Draw.io
- Lucidchart
- DbDesigner
- Vertabelo
- Mermaid (erDiagram)
- PlantUML

---

## 4. Deployment Diagrams

### Purpose
Show how software components are deployed across infrastructure and environments.

### When to Use
- Documenting infrastructure architecture
- Explaining cloud deployment strategy
- Showing scalability and redundancy
- Environment documentation (dev, staging, prod)
- Security and isolation documentation
- Container orchestration visualization

### Key Elements
- Nodes (computers, servers, containers)
- Components deployed on nodes
- Communication paths (networks)
- Artifact representations
- Environment grouping

### Example: Kubernetes Deployment

```
┌────────────────────────────────────────────────────────┐
│             AWS Cloud (prod-cluster)                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Kubernetes Cluster (3 worker nodes)             │ │
│  ├──────────────────────────────────────────────────┤ │
│  │                                                  │ │
│  │  ┌─────────────────┐  ┌──────────────────┐     │ │
│  │  │  Node 1         │  │   Node 2         │     │ │
│  │  ├─────────────────┤  ├──────────────────┤     │ │
│  │  │ ┌─────────────┐ │  │ ┌──────────────┐ │     │ │
│  │  │ │ API Pod x3  │ │  │ │Web Pod x2    │ │     │ │
│  │  │ │(Docker img) │ │  │ │(Docker img)  │ │     │ │
│  │  │ └─────────────┘ │  │ └──────────────┘ │     │ │
│  │  │ ┌─────────────┐ │  │ ┌──────────────┐ │     │ │
│  │  │ │ Cache Pod   │ │  │ │ Worker Pod   │ │     │ │
│  │  │ │(Redis)      │ │  │ │(Background)  │ │     │ │
│  │  │ └─────────────┘ │  │ └──────────────┘ │     │ │
│  │  └─────────────────┘  └──────────────────┘     │ │
│  │                                                  │ │
│  │  ┌─────────────────────────────────────────┐   │ │
│  │  │  Node 3 (Database)                       │   │ │
│  │  ├─────────────────────────────────────────┤   │ │
│  │  │ ┌──────────────────────────────────────┐│   │ │
│  │  │ │ PostgreSQL Pod (StatefulSet)        ││   │ │
│  │  │ │ PersistentVolume: 100GB             ││   │ │
│  │  │ └──────────────────────────────────────┘│   │ │
│  │  └─────────────────────────────────────────┘   │ │
│  │                                                  │ │
│  │                                                  │ │
│  │  Load Balancer: api.example.com                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Persistent Storage (EBS): prod-db-backup            │
│  Logging (CloudWatch): API & Application logs        │
│  Monitoring (Prometheus): Metrics                    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Best Practices
- Show realistic deployment topology
- Clearly separate environments
- Indicate replication and redundancy
- Show data persistence locations
- Include monitoring and logging
- Label all components with versions
- Show network segmentation
- Document resource requirements

### Avoid
- Overly simplistic (hide important details)
- Mixing multiple environments
- Unclear network topology
- Missing failover/redundancy considerations

### Tools
- Draw.io (Deployment template)
- Lucidchart
- C4-PlantUML (deployment variant)
- Mermaid (graph syntax)
- Excalidraw

---

## 5. State Diagrams

### Purpose
Show how a system or object transitions between different states based on events.

### When to Use
- Documenting state machines (orders, payments, workflows)
- User authentication states
- Document lifecycle
- Game state management
- Complex object state transitions
- Protcol state diagrams

### Key Elements
- States (circles/rectangles)
- Transitions (arrows)
- Events/Triggers (labels on arrows)
- Initial state (solid circle)
- Final state (circle with dot inside)
- Actions (optional, on transitions)

### Example: Order State Diagram

```
       ┌─────────┐
       │  START  │
       └────┬────┘
            │
       ┌────▼────────────┐
       │   PENDING       │◄─────────────┐
       │(waiting for     │              │
       │ confirmation)   │              │
       └────┬────────────┘              │
            │                           │
    User confirms order               Cancel
            │                           │
       ┌────▼────────────┐              │
       │   PROCESSING    │──────────────┘
       │ (Payment being  │
       │ processed)      │
       └────┬────────────┘
            │
       ┌────▼────────────┐
       │   CONFIRMED     │
       │ (Ready to ship) │
       └────┬────────────┘
            │
       ┌────▼────────────┐
       │   SHIPPED       │
       │ (In transit)    │
       └────┬────────────┘
            │
       ┌────▼────────────┐
       │   DELIVERED     │
       └────┬────────────┘
            │
       ┌────▼────────────┐
       │   COMPLETED     │
       └─────────────────┘


Error State:
┌──────────────────────────┐
│ FAILED                   │
│ (Payment failed/timeout) │
└──────────────────────────┘
  ▲
  │ (Any state can go to FAILED on error)
```

### Best Practices
- Clearly show all possible states
- Document state-entry and state-exit actions
- Show conditions for transitions
- Include error states
- Document timeout behaviors
- Use consistent naming conventions
- Show guard conditions if present

### Avoid
- Overlapping transitions
- Missing states in the flow
- Unexplained spontaneous transitions
- Mixing unrelated state machines

### Tools
- Draw.io
- Lucidchart
- PlantUML (@startuml state)
- Mermaid (stateDiagram-v2)

---

## 6. Use Case Diagrams

### Purpose
Show system functionality from user perspective, emphasizing who can do what.

### When to Use
- System requirements documentation
- User role and permission documentation
- Feature overview for stakeholders
- System scope definition
- User journey at high level
- Actor and system boundary documentation

### Key Elements
- Actor (stick figure)
- Use case (ellipse)
- System boundary (rectangle)
- Association (line between actor and use case)
- Include/Extend relationships (dashed lines)

### Example: E-Commerce System Use Cases

```
┌────────────────────────────────┐
│     E-Commerce System          │
├────────────────────────────────┤
│                                │
│  (View Products)               │
│         ▲                       │
│         │                       │
│         │  ┌──────────────────┐ │
│         ├──┤ Browse Products  │ │
│         │  └──────────────────┘ │
│         │                       │
│  (Search/Filter)   ┌──────────────────┐
│         │     ┌────┤ Search Products  │
│    ┌────┴──────────┤            │
│    │               └──────────────────┘
│    │
│  ┌─┴────────────────────┐
│  │    Customer          │
│  └─┬────────────────────┘
│    │
│    │  ┌──────────────────┐
│    └──┤ Add to Cart      │
│       └──────────────────┘
│
│       ┌──────────────────┐
│       │ Place Order      │◄────┐
│       └────┬─────────────┘     │
│            │                   │
│       (Validate Payment)       │
│            │                   │
│       ┌────▼─────────────┐     │
│       │Process Payment   │     │
│       └────┬─────────────┘ (Include)
│            │                   │
│    ┌──────────────────┐        │
│    │ Admin User       │        │
│    └─┬────────────────┘        │
│      │                         │
│      │  ┌──────────────────┐   │
│      └──┤ Manage Orders    │───┘
│         └──────────────────┘
│
└────────────────────────────────┘
```

### Best Practices
- Keep use cases focused and simple
- Group related use cases
- Clearly identify actors and their roles
- Use verb-object naming for use cases
- Show system boundaries clearly
- Document special requirements separately
- Use include/extend relationships carefully

### Avoid
- Too many use cases (more than 10-15)
- Overlapping or redundant use cases
- Implementation details
- Complex relationships

### Tools
- Draw.io
- Lucidchart
- Enterprise Architect
- Visual Paradigm
- PlantUML

---

## 7. Comparison Matrix: When to Use What

| Diagram Type | Purpose | Audience | When to Use |
|---|---|---|---|
| **C4 System Context** | System overview | All stakeholders | Project kickoff, high-level planning |
| **C4 Container** | Technology layer | Tech leads, architects | Architecture design, deployment planning |
| **C4 Component** | Internal structure | Developers, tech leads | Code organization, refactoring planning |
| **Sequence** | Interaction flows | Developers, QA | Feature documentation, API flows |
| **Flowchart** | Decision logic | Developers, BA | Algorithms, process documentation |
| **ER Diagram** | Data structure | DBAs, developers | Database design, schema documentation |
| **Deployment** | Infrastructure | DevOps, tech leads | Deployment planning, disaster recovery |
| **State** | Object lifecycle | Developers, architects | Feature design, protocol documentation |
| **Use Case** | System functions | All stakeholders | Requirements, scope definition |

---

## Diagram Creation Workflow

### For Each Diagram Type:

1. **Define Purpose**: What question does this answer?
2. **Identify Audience**: Who needs to understand this?
3. **Gather Content**: What information to include?
4. **Choose Tool**: Select based on output requirements
5. **Create Draft**: Iterate with team
6. **Add Details**: Labels, legends, annotations
7. **Review**: Ensure accuracy and clarity
8. **Maintain**: Update as system evolves

---

## Best Practices Across All Diagram Types

- Use consistent naming conventions
- Include a legend if symbols aren't standard
- Add dates and version numbers
- Make diagrams readable at 50% zoom
- Use whitespace effectively
- Limit text per element
- Color code for meaning (not just decoration)
- Test readability in black and white
- Keep related diagrams synchronized

---

## Common Mistakes Across Diagrams

1. **Mixing abstraction levels**: Keep one diagram one level
2. **Information overload**: Show only what's necessary
3. **Poor labeling**: Every element should be clear
4. **Inconsistent symbols**: Use standard notation
5. **Crossing lines**: Rearrange to minimize crossings
6. **Missing context**: Add title, legend, explanation
7. **Not updated**: Diagrams decay; maintain regularly
8. **Tool-induced complexity**: Simple tools often produce clearer diagrams
