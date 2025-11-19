# Event Storming Workshop Canvas: [Domain Name]

**Date**: YYYY-MM-DD
**Facilitator**: [Name]
**Participants**: [List names and roles]
**Duration**: [Actual duration]
**Objective**: [What we're trying to discover/design]

---

## Workshop Overview

### Goals
1. [Goal 1: e.g., Discover domain events and boundaries]
2. [Goal 2: e.g., Identify service boundaries for microservices]
3. [Goal 3: e.g., Create shared understanding across teams]

### Scope
**In Scope**: [What business processes we're exploring]
**Out of Scope**: [What we're explicitly NOT covering]

---

## Event Storming Legend

```
🟧 Domain Event     - Something that happened (past tense)
🟦 Command          - Action that triggers an event
🟨 Aggregate        - Entity that handles commands
👤 Actor            - Who/what initiates commands
🟪 Policy           - Automation rule (When event X, then command Y)
🟥 Hotspot          - Problem, question, or conflict
🟩 Read Model       - Information needed to make decisions
⏰ Timer            - Time-based trigger
📄 External System  - Third-party system or legacy integration
```

---

## Phase 1: Domain Events Timeline

[Capture all domain events discovered, organized chronologically from left to right]

### Early Events (Start of Process)
```
🟧 [EventName1] → 🟧 [EventName2] → 🟧 [EventName3]

Example:
🟧 CustomerRegistered → 🟧 EmailVerificationSent → 🟧 EmailVerified
```

### Middle Events (Core Process)
```
🟧 [EventName4] → 🟧 [EventName5] → 🟧 [EventName6]

Example:
🟧 OrderPlaced → 🟧 PaymentProcessed → 🟧 InventoryReserved
```

### Late Events (Process Completion)
```
🟧 [EventName7] → 🟧 [EventName8] → 🟧 [EventName9]

Example:
🟧 OrderShipped → 🟧 OrderDelivered → 🟧 FeedbackRequested
```

### Exceptional Events (Error/Cancellation Paths)
```
🟧 [ErrorEvent1] → 🟧 [CompensationEvent]

Example:
🟧 PaymentFailed → 🟧 OrderCancelled → 🟧 InventoryReleased
```

---

## Phase 2: Commands & Actors

[For each event, identify what command triggered it and who/what initiated it]

### Command → Event Mappings

#### [Business Process 1]
```
👤 [Actor] → 🟦 [Command] → 🟨 [Aggregate] → 🟧 [Event]

Example:
👤 Customer → 🟦 PlaceOrder → 🟨 Order → 🟧 OrderPlaced
```

#### [Business Process 2]
```
👤 [Actor] → 🟦 [Command] → 🟨 [Aggregate] → 🟧 [Event]

Example:
👤 PaymentService → 🟦 ProcessPayment → 🟨 Payment → 🟧 PaymentProcessed
```

#### [Business Process 3]
```
👤 [Actor] → 🟦 [Command] → 🟨 [Aggregate] → 🟧 [Event]

Example:
⏰ Timer → 🟦 SendReminder → 🟨 Notification → 🟧 ReminderSent
```

---

## Phase 3: Aggregates & Invariants

[Identify aggregates that handle commands and enforce business rules]

### Aggregate: [AggregateName1]

**Responsibilities**: [What this aggregate manages]

**Commands Handled**:
- 🟦 [Command1]
- 🟦 [Command2]
- 🟦 [Command3]

**Events Raised**:
- 🟧 [Event1]
- 🟧 [Event2]
- 🟧 [Event3]

**Invariants** (Business Rules):
- ✓ [Rule 1: e.g., Order total must equal sum of line items]
- ✓ [Rule 2: e.g., Cannot modify order after it's shipped]
- ✓ [Rule 3: e.g., Quantity must be positive]

**Data Owned**:
- [Field1]: [Type]
- [Field2]: [Type]
- [Field3]: [Type]

---

### Aggregate: [AggregateName2]

**Responsibilities**: [What this aggregate manages]

**Commands Handled**:
- 🟦 [Command1]
- 🟦 [Command2]

**Events Raised**:
- 🟧 [Event1]
- 🟧 [Event2]

**Invariants** (Business Rules):
- ✓ [Rule 1]
- ✓ [Rule 2]

**Data Owned**:
- [Field1]: [Type]
- [Field2]: [Type]

---

## Phase 4: Policies (Automation Rules)

[Document "when event X happens, then trigger command Y" automation rules]

### Policy: [PolicyName1]
```
When: 🟧 [Event]
Then: 🟦 [Command]
Why: [Business reason for this automation]

Example:
When: 🟧 PaymentProcessed
Then: 🟦 ReserveInventory
Why: Ensure items are available before shipping
```

### Policy: [PolicyName2]
```
When: 🟧 [Event]
Then: 🟦 [Command]
Why: [Business reason]
```

### Policy: [PolicyName3]
```
When: 🟧 [Event1] AND 🟧 [Event2]
Then: 🟦 [Command]
Why: [Business reason for this complex rule]

Example:
When: 🟧 OrderPacked AND 🟧 LabelPrinted
Then: 🟦 MarkReadyForPickup
Why: Only notify shipping when fully prepared
```

---

## Phase 5: Read Models

[Identify what information users need to see or to make decisions]

### Read Model: [ViewName1]

**Purpose**: [What user needs to see or decide]

**Data Required**:
- [Field1] from [Aggregate/Event]
- [Field2] from [Aggregate/Event]
- [Field3] from [Aggregate/Event]

**Updated By Events**:
- 🟧 [Event1] → Updates [field]
- 🟧 [Event2] → Updates [field]

**Used By**:
- 👤 [Actor] when executing 🟦 [Command]

---

### Read Model: [ViewName2]

**Purpose**: [What user needs to see or decide]

**Data Required**:
- [Field1] from [Aggregate/Event]
- [Field2] from [Aggregate/Event]

**Updated By Events**:
- 🟧 [Event1]
- 🟧 [Event2]

**Used By**:
- 👤 [Actor] when executing 🟦 [Command]

---

## Phase 6: Bounded Contexts

[Group related aggregates, events, and processes into bounded contexts]

### Bounded Context: [ContextName1]

**Purpose**: [Core responsibility of this context]

**Ubiquitous Language**:
- **[Term1]**: [Definition in this context]
- **[Term2]**: [Definition in this context]
- **[Term3]**: [Definition in this context]

**Aggregates**:
- 🟨 [Aggregate1]
- 🟨 [Aggregate2]

**Key Events**:
- 🟧 [Event1]
- 🟧 [Event2]
- 🟧 [Event3]

**Team Ownership**: [Team name]

**Subdomain Type**: [Core | Supporting | Generic]

---

### Bounded Context: [ContextName2]

**Purpose**: [Core responsibility]

**Ubiquitous Language**:
- **[Term1]**: [Definition - may differ from other contexts!]
- **[Term2]**: [Definition]

**Aggregates**:
- 🟨 [Aggregate1]
- 🟨 [Aggregate2]

**Key Events**:
- 🟧 [Event1]
- 🟧 [Event2]

**Team Ownership**: [Team name]

**Subdomain Type**: [Core | Supporting | Generic]

---

## Phase 7: Context Relationships

[Define how bounded contexts interact]

### [Context1] → [Context2]

**Relationship Type**: [Partnership | Shared Kernel | Customer-Supplier | Conformist | Anti-Corruption Layer]

**Integration Pattern**:
```
[Context1] publishes: 🟧 [Event]
[Context2] consumes: 🟧 [Event] → triggers 🟦 [Command]

Example:
OrderContext publishes: 🟧 OrderPlaced
PaymentContext consumes: 🟧 OrderPlaced → triggers 🟦 ProcessPayment
```

**Translation Needed?**: [Yes/No - if yes, describe Anti-Corruption Layer]

**Data Shared**: [What data flows between contexts]

---

### [Context2] → [Context3]

**Relationship Type**: [Type]

**Integration Pattern**:
```
[Context2] publishes: 🟧 [Event]
[Context3] consumes: 🟧 [Event] → triggers 🟦 [Command]
```

**Translation Needed?**: [Yes/No]

**Data Shared**: [What data flows]

---

## Hotspots (Issues & Questions)

[Capture problems, conflicts, or unanswered questions discovered during the workshop]

### 🟥 Hotspot 1: [Issue Title]

**Description**: [What's the problem or uncertainty?]

**Impact**: [Why does this matter?]

**Options**:
1. [Option A]
2. [Option B]
3. [Option C]

**Decision Needed By**: [Date or milestone]

**Owner**: [Who will resolve this]

---

### 🟥 Hotspot 2: [Issue Title]

**Description**: [What's the problem?]

**Impact**: [Why it matters]

**Options**:
1. [Option A]
2. [Option B]

**Decision Needed By**: [Date]

**Owner**: [Who resolves]

---

## External Systems

[Document integration points with third-party or legacy systems]

### 📄 External System: [SystemName1]

**Purpose**: [Why we integrate with this]

**Integration Type**: [API call | Event notification | Batch import | etc.]

**Trigger**:
- 🟧 [Event] → Calls [System] → Returns [Data]

**Reliability**: [Known issues, SLA, failover strategy]

**Owner**: [External team/vendor]

---

### 📄 External System: [SystemName2]

**Purpose**: [Why we integrate]

**Integration Type**: [Type]

**Trigger**:
- 🟦 [Command] → Calls [System] → 🟧 [Event based on response]

**Reliability**: [Notes]

**Owner**: [Team/vendor]

---

## Complete Process Flow Example

[Document one complete end-to-end flow to validate understanding]

### Flow: [ProcessName, e.g., "Place Order to Delivery"]

```
1. 👤 Customer → 🟦 PlaceOrder → 🟨 Order → 🟧 OrderPlaced

2. 🟪 Policy: When OrderPlaced → 🟦 ProcessPayment
   👤 PaymentService → 🟦 ProcessPayment → 🟨 Payment → 🟧 PaymentProcessed

3. 🟪 Policy: When PaymentProcessed → 🟦 ReserveInventory
   👤 InventoryService → 🟦 ReserveInventory → 🟨 Inventory → 🟧 InventoryReserved

4. 🟪 Policy: When InventoryReserved → 🟦 CreateShipment
   👤 ShippingService → 🟦 CreateShipment → 🟨 Shipment → 🟧 ShipmentCreated

5. 👤 Warehouse → 🟦 PackOrder → 🟨 Shipment → 🟧 OrderPacked

6. 👤 Warehouse → 🟦 PrintLabel → 🟨 Shipment → 🟧 LabelPrinted

7. 🟪 Policy: When OrderPacked AND LabelPrinted → 🟦 MarkReadyForPickup
   🟨 Shipment → 🟧 ReadyForPickup

8. 👤 Carrier → 🟦 PickupOrder → 🟨 Shipment → 🟧 OrderPickedUp

9. ⏰ Daily Batch → 🟦 UpdateTrackingInfo → 🟨 Shipment → 🟧 TrackingUpdated

10. 👤 Carrier → 🟦 DeliverOrder → 🟨 Shipment → 🟧 OrderDelivered

11. 🟪 Policy: When OrderDelivered → 🟦 SendFeedbackRequest
    👤 NotificationService → 🟦 SendFeedbackRequest → 🟨 Notification → 🟧 FeedbackRequestSent
```

---

## Key Insights & Decisions

### Insights Gained
1. [Key insight 1 from the workshop]
2. [Key insight 2]
3. [Key insight 3]

### Decisions Made
1. [Decision 1: e.g., We will use event-driven architecture for X]
2. [Decision 2: e.g., Three bounded contexts identified: X, Y, Z]
3. [Decision 3: e.g., Payment context will be extracted first]

### Assumptions Validated
- ✓ [Assumption 1 that was confirmed]
- ✓ [Assumption 2 that was confirmed]

### Assumptions Invalidated
- ✗ [Assumption 1 that was proven wrong]
- ✗ [Assumption 2 that needs rethinking]

---

## Next Steps

### Immediate Actions (This Week)
1. [ ] [Action 1: e.g., Document ubiquitous language]
2. [ ] [Action 2: e.g., Create ADR for identified bounded contexts]
3. [ ] [Action 3: e.g., Resolve hotspot #1]

**Owner**: [Name]
**Due Date**: [Date]

---

### Short-Term Actions (This Month)
1. [ ] [Action 1: e.g., Design service boundaries based on contexts]
2. [ ] [Action 2: e.g., Define event schemas]
3. [ ] [Action 3: e.g., Create service specifications]

**Owner**: [Name]
**Due Date**: [Date]

---

### Long-Term Actions (This Quarter)
1. [ ] [Action 1: e.g., Implement first microservice]
2. [ ] [Action 2: e.g., Set up event streaming infrastructure]
3. [ ] [Action 3: e.g., Run follow-up workshop for context Y]

**Owner**: [Name]
**Due Date**: [Date]

---

## Appendix: Raw Notes

[Include photos of physical sticky notes, whiteboard diagrams, or raw unstructured notes from the session]

### Photo 1: [Description]
[Link or attach image]

### Photo 2: [Description]
[Link or attach image]

### Parking Lot (Out of Scope Items)
[Items raised but out of scope for this workshop]
- [Item 1]
- [Item 2]

---

## Participants Feedback

**What Went Well**:
- [Positive feedback 1]
- [Positive feedback 2]

**What Could Be Improved**:
- [Improvement 1]
- [Improvement 2]

**Suggestions for Next Workshop**:
- [Suggestion 1]
- [Suggestion 2]

---

**Workshop Facilitator Notes**: [Any additional observations or facilitation notes]
