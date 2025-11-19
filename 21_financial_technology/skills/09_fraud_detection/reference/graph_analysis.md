# Graph Analysis Reference

## Overview
Graph analysis detects fraud rings and collusive fraudsters by analyzing network relationships between entities (customers, cards, devices, etc.).

## Graph Components

### Entities (Nodes)
```
Customer IDs
Card Numbers
Device IDs
IP Addresses
Email Addresses
Phone Numbers
Shipping Addresses
Billing Addresses
Merchant IDs
```

### Relationships (Edges)
```
Customer used Card
Card processed Transaction
Device accessed Account
IP used by Device
Email linked to Account
Phone linked to Account
Address used for Shipping
Address used for Billing
Customer purchased from Merchant
```

### Edge Attributes
```
Weight: Transaction frequency or amount
Timestamp: When relationship established
Risk score: Confidence in relationship
Direction: One-way (card to transaction) vs two-way (customer to customer)
Type: Transaction, account link, shared attribute, etc.
```

## Graph Database Structure

### Example Graph
```
Customer A (risk: 0.3)
├── Card 1234 (used 50 times)
│   ├── Device X (used 30 times)
│   │   └── IP 192.1.1.1 (50 transactions)
│   └── Device Y (used 20 times)
│       └── IP 192.1.1.2 (20 transactions)
├── Card 5678 (used 30 times)
└── Email user@example.com
    └── Phone +1234567890
        └── Customer B (risk: 0.8)
            ├── Card 9999 (used 100 times)
            └── Device Z (used 100 times)
```

## Graph Algorithms

### Community Detection

**Modularity-Based (Louvain Algorithm)**
```
Objective: Partition graph into communities
Method: Maximize modularity (internal density - external sparsity)

Result: Identify potential fraud rings
Example:
- Community 1: 5 customers sharing 3 devices and 2 cards
- Community 2: 8 customers sharing 4 devices and 4 cards
```

**Overlapping Communities**
```
Customers can be in multiple communities
Identifies bridge entities connecting fraud rings

Example:
- Community A: 5 fraudsters
- Community B: 7 fraudsters
- Bridge: Customer C in both (higher risk)
```

### Shortest Path & Distance

**Shortest Path Analysis**
```
Find minimum connections between entities

Query: Distance from Customer A to Customer B?
Path: A --card--> Card1 --device--> Device1 --IP--> IP1 --device--> Device2 --card--> CardB --customer--> B
Distance: 6 hops

Interpretation:
- Close distance (1-2): Direct relationship
- Medium distance (3-4): Connected through intermediaries
- Distant (5+): Potentially unrelated
```

**Degree Centrality**
```
How many connections does an entity have?

Degree = number of edges connected

High degree = hub entity
Example:
- Device used by 50 customers = high degree (suspicious)
- Normal device: used by 1-3 customers

Risk assessment:
- High degree + many accounts = fraud ring hub
```

### Clustering Coefficient

**Local Clustering**
```
Measures how connected neighbors are

Formula: (# of edges between neighbors) / (max possible edges)

High coefficient (close to 1):
- Neighbors are well-connected
- Indicates tight-knit fraud ring

Low coefficient (close to 0):
- Neighbors not connected
- Indicates loose network
```

**Network Density**
```
Proportion of edges relative to possible edges

Dense network (high clustering):
- Many internal connections
- Likely fraud ring
- Strong collaboration

Sparse network (low clustering):
- Few connections
- Loose network
- Less organized fraud
```

### PageRank & Influence

**PageRank Algorithm**
```
Measures importance based on incoming edges

Idea: Important nodes have edges from important nodes

High PageRank = Central to network
Example:
- Device used by 5 fraudsters with confirmed fraud = high rank
- Customer connected to high-rank device = elevated rank

Application: Rank customers by fraud importance
```

## Fraud Ring Detection Patterns

### Ring Characteristics
```
Shared Resources:
- Multiple customers use same device
- Multiple customers use same card
- Multiple customers from same IP

Characteristics:
- Rapid enrollment after ring member activity
- Correlated transaction timing
- Similar merchant preferences
- Similar transaction amounts

Risk Pattern:
- Customer A (new) linked to device D
- Device D also linked to confirmed fraudster B
- Therefore, Customer A = high risk
```

### Ring Detection Signals

**Resource Sharing Patterns**
```
Suspicious: 50 customers share 1 device
  Risk: 99% probability fraud ring

Suspicious: 10 customers share 5 cards
  Risk: 95% probability coordinated fraud

Suspicious: 5 customers share address
  Risk: 80% probability organized fraud

Legitimate: 2-3 devices per customer (personal devices)
Legitimate: 1-2 cards per customer (personal + backup)
Legitimate: Family members at same address
```

**Temporal Patterns**
```
Suspicious:
- Customer B created 1 hour after Customer A
- Both use same device
- Both place orders to same address
- Suggests coordinated account creation

Suspicious:
- Customer A places order at 3 AM
- 10 minutes later, Customer B places order
- Same device, different billing address
- Rapid sequential activity

Legitimate:
- Transactions spread across week
- Different times of day
- Natural temporal variation
```

### Ring Severity Assessment

**Confirmed Fraud Ring**
```
Risk: CRITICAL
Indicators:
- 3+ confirmed fraudsters in network
- Shared devices/resources
- Coordinated activity timing
- Multiple fraud methods

Actions:
- Block all ring members
- Investigate all linked accounts
- Contact payment processor
- File fraud report
- Monitor for reconstitution
```

**Suspected Fraud Ring**
```
Risk: HIGH
Indicators:
- New account linked to fraudster device
- Multiple unconfirmed accounts
- Some fraud signals
- Shared resources

Actions:
- Enhanced verification required
- Velocity checks
- Behavioral monitoring
- Investigation priority
```

**Low-Risk Network**
```
Risk: LOW
Indicators:
- Few connections
- Legitimate relationship (family)
- Low fraud history
- Natural activity patterns

Actions:
- Standard monitoring
- Normal verification
- Allow transactions
```

## Real-World Ring Detection Examples

### Example 1: Card Sharing Ring
```
Discovery:
- Card 1234 linked to Customer A (confirmed fraud)
- Card 1234 also linked to Customers B, C, D, E
- Each customer in different country
- All created in last 2 weeks

Analysis:
- 4 new customers share 1 card
- Same issuer card = stolen card
- Coordinated use across countries
- Ring severity: CRITICAL

Action:
- Block all 5 customers
- Flag card as compromised
- Contact card issuer
```

### Example 2: Device Sharing Ring
```
Discovery:
- Device X linked to Customer P (flagged chargeback)
- Device X also linked to Customers Q, R, S
- Transactions to different addresses
- Similar transaction patterns

Analysis:
- 4 customers use same device
- Different billing/shipping addresses
- Device suggests coordination
- Estimated ring size: 3-4 people

Action:
- Flag Device X
- Enhanced verification for all customers
- Coordinate investigation
- Monitor for new account enrollment
```

### Example 3: Email/Phone Ring
```
Discovery:
- Email user@test.com linked to Customers X, Y, Z
- Phone +1234567890 also linked to same customers
- Different physical addresses
- All accounts created same day

Analysis:
- Shared contact info = likely coordinated
- Burner email/phone = common fraud pattern
- Mass account creation
- Ring severity: HIGH

Action:
- Block all accounts
- Flag contact info
- Monitor for new enrollments with similar pattern
```

## Graph-Based Risk Scoring

### Network Risk Propagation
```
Base Score:
- Confirmed fraudster A: Score 0.95

Direct neighbors (distance 1):
- Share resource with A: +0.30 to score
- Example: Customer B uses same device as A
- B's score: 0.30

Indirect neighbors (distance 2):
- Connected through intermediary: +0.15 to score
- Example: Customer C uses device of Customer D
- D uses card of confirmed fraudster A
- C's score: 0.15

Calculation:
- Multiple connections sum: C scores 0.3 from device + 0.15 from card = 0.45
```

### Ring Cohesion Scoring
```
Measure how tightly connected fraud ring is

Cohesion = (Actual edges / Possible edges)

Low cohesion (0.1):
- Loose network
- Random association
- Risk: 40%

Medium cohesion (0.5):
- Organized network
- Multiple connections
- Risk: 75%

High cohesion (0.9):
- Tight ring
- Heavy resource sharing
- Risk: 95%
```

## Graph Query Examples

### Find Fraud Rings
```
MATCH (c:Customer {fraud_flag: true})
-[:USES_DEVICE]->(d:Device)
-[:USES_DEVICE]->(c2:Customer)
RETURN d, count(c) as customer_count
HAVING customer_count > 3
```

### Find Account Takeover Patterns
```
MATCH (c:Customer)
-[:USES_DEVICE]->(d:Device)
-[:USES_DEVICE]->(c2:Customer {fraud_flag: true})
WHERE c.created_date > d.first_use_date - 1 day
AND c.created_date < d.first_use_date + 1 day
RETURN c, d, c2
```

### Find Bridge Entities
```
MATCH (c1:Customer)-[*1..2]-(c2:Customer)
WHERE c1.fraud_flag = true AND c2.fraud_flag = true
RETURN c1, c2, length(paths) as distance
ORDER BY distance
LIMIT 10
```

## Implementation Considerations

### Scalability
```
Graph size: Millions of nodes, billions of edges
Query latency: <1 second for real-time scoring

Solutions:
- Graph database (Neo4j, ArangoDB)
- Distributed graph processing (Spark GraphX)
- Approximate algorithms for large-scale
- Caching of frequently accessed subgraphs
```

### Performance
```
Real-time scoring: Pre-compute neighborhood subgraphs
Batch analysis: Nightly fraud ring detection
Stream processing: Update graph as new data arrives

Optimization:
- Index on frequently queried attributes
- Partition graph by entity type
- Cache high-degree nodes
- Approximate centrality measures
```

### Privacy & Compliance
```
PII considerations:
- Anonymize personal identifiers
- Pseudonyms for customers (e.g., C12345)
- Restrict graph access
- Audit trail of queries

Retention:
- Keep active fraud ring data indefinitely
- Archive resolved rings after 1-2 years
- Retain edges for risk scoring 18+ months
```

## Graph Analysis Limitations

### False Positives
- Legitimate shared devices (family members)
- Shared addresses (roommates, cohabitation)
- Natural network overlap (workplace)

### False Negatives
- Solo fraudsters (no ring)
- Organized fraud with good compartmentalization
- Fraud without resource sharing

### Recommendations
- Combine with other detection methods
- Use graph as risk factor, not sole decision
- Human investigation required for suspected rings
- Regular pattern validation
