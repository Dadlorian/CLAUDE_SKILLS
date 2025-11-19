# Automated Material Handling Systems Reference

## 1. Automated Guided Vehicles (AGVs) vs. Autonomous Mobile Robots (AMRs)

### 1.1 AGV Technology

**Definition**
Automated Guided Vehicles are unmanned vehicles that follow predetermined paths using guidance systems such as magnetic strips, inductive sensors, QR codes, or laser navigation.

**Key Characteristics**
- Navigation: Fixed path (magnetic strips, wires, or predefined routes)
- Speed: Typically 1-2 m/s (3-7 km/h)
- Capacity: 500 kg to 5+ tons depending on model
- Operating Environment: Controlled warehouses, manufacturing floors
- Load Types: Pallets, totes, customized fixtures
- Collision Avoidance: Basic sensors with hard stops
- Integration: Requires WCS (Warehouse Control System)

**Navigation Technologies**

| Technology | How It Works | Advantages | Disadvantages |
|-----------|-----------|-----------|-------------|
| Magnetic Strips | Embedded in floor | Reliable, proven | Expensive floor modification, inflexible |
| Inductive Wires | Buried under floor | Invisible, durable | Very expensive installation |
| QR/Barcode | Visual markers | Flexible, low cost | Affected by floor conditions |
| Laser (LiDAR) | 3D mapping | No infrastructure | Complex, more expensive |
| GPS | Satellite positioning | Global, flexible | Not suitable for indoors |
| RFID | Radio frequency | Fast, reliable | Line-of-sight issues |

**Leading AGV Manufacturers**
- Toyota Material Handling (Toyota AGVs)
- Crown Equipment
- Hyster-Yale
- Mitsubishi Heavy Industries
- KION/Linde

**Typical AGV Implementation Cost**
- Vehicle: $50,000-$250,000 per unit
- Infrastructure (magnetic strips): $10,000-$50,000+ per path mile
- WCS Software: $100,000-$500,000
- Installation and Training: $50,000-$200,000
- Total for 10-vehicle fleet: $1-3 million

---

### 1.2 Autonomous Mobile Robots (AMRs)

**Definition**
AMRs are self-navigating vehicles using advanced sensors, AI, and dynamic path planning. They don't require predetermined paths or infrastructure modifications.

**Key Characteristics**
- Navigation: Dynamic path planning with obstacle avoidance
- Speed: Typically 1-1.5 m/s (3.6-5.4 km/h) to start, improving
- Capacity: 75 kg to 500+ kg (lighter than AGVs typically)
- Operating Environment: Flexible, can navigate unstructured environments
- Load Types: Totes, lighter pallets, mobile shelves
- Collision Avoidance: Advanced AI with 360° sensing
- Integration: API-based, more software-flexible
- Adaptability: Can be redeployed quickly with software updates

**AMR Technology Stack**

```
AMR System Architecture
├─ Perception Layer
│  ├─ LiDAR Sensors (3D mapping)
│  ├─ Camera Systems (obstacle detection)
│  ├─ Bumper Sensors (safety)
│  └─ Encoder Wheels (odometry)
├─ Navigation Layer
│  ├─ SLAM (Simultaneous Localization and Mapping)
│  ├─ Path Planning Algorithm
│  ├─ Collision Avoidance
│  └─ Dynamic Obstacle Processing
├─ Execution Layer
│  ├─ Motor Control
│  ├─ Battery Management
│  ├─ Task Scheduling
│  └─ Safety Protocols
└─ Integration Layer
    ├─ WMS API Integration
    ├─ Fleet Management Software
    ├─ Mobile Client Interface
    └─ Analytics & Reporting
```

**Leading AMR Manufacturers**
- Mobile Industrial Robots (MiR) - 70% market share
- Fetch Robotics
- InVata Robotics
- OTTO Motors (Clearpath Robotics)
- Geek+
- Jaka Robotics

**Typical AMR Implementation Cost**
- Robot: $35,000-$150,000 per unit
- Infrastructure: Minimal (floor mapping only)
- Fleet Management Software: $50,000-$200,000
- Installation and Training: $20,000-$50,000
- Total for 10-robot fleet: $500,000-$2 million

---

### 1.3 AGV vs. AMR Comparison

| Aspect | AGV | AMR |
|--------|-----|-----|
| **Navigation** | Fixed paths | Dynamic/flexible |
| **Infrastructure** | Magnetic strips/wires required | Minimal infrastructure |
| **Deployment Time** | 6-12 months | 4-8 weeks |
| **Installation Cost** | High ($10K-50K per path mile) | Low (floor mapping) |
| **Vehicle Cost** | Higher ($100K-250K) | Lower ($35K-150K) |
| **Flexibility** | Low (dedicated paths) | High (any route) |
| **Scalability** | Linear with paths | Easy to add units |
| **Obstacle Avoidance** | Basic (hard stops) | Advanced (AI-based) |
| **Adoption Timeline** | Long learning curve | Quick deployment |
| **ROI Period** | 3-5 years | 1-3 years |
| **Load Capacity** | Heavier (1-5+ tons) | Lighter (75-500 kg) |
| **Operating Speed** | Consistent (1-2 m/s) | Variable (0.5-1.5 m/s) |
| **Human Interaction** | Minimal | High (shared spaces) |
| **Technology Risk** | Lower | Higher (emerging tech) |

---

### 1.4 Hybrid Approach: AGVs + AMRs

Many modern warehouses implement a hybrid approach:

**Strategy**
- AGVs for high-volume, repetitive routes (loading docks to storage)
- AMRs for flexible, variable routes (goods-to-person, small order picking)

**Benefits**
- Combines cost-efficiency of AGVs with flexibility of AMRs
- Leverages best technology for each use case
- Reduces risk by splitting deployment
- Easier workforce management

**Example Warehouse Configuration**
```
Loading Dock → AGV Fleet → Storage Area
                              ↓
                        AMR Fleet
                              ↓
                     Goods-to-Person Stations
                              ↓
                       Packing Stations
                              ↓
                      Shipping Dock
```

---

## 2. Automated Storage and Retrieval Systems (AS/RS)

### 2.1 Overview

AS/RS systems automatically store and retrieve items from high-density storage locations. They dramatically increase space utilization and improve productivity.

**Key Benefits**
- Space utilization: 5-10x increase vs. traditional racking
- Picking productivity: 2-5x improvement
- Accuracy: >99.9% due to automation
- Safety: Reduced workplace injuries
- Consistency: Uniform, predictable performance

---

### 2.2 Vertical Lift Modules (VLMs)

**Technology**
Vertical carousel systems with enclosed cabs that bring items to a fixed operator workstation.

**How It Works**
1. Operator enters item request
2. VLM carousel rotates to locate item
3. Item tray comes to operator at waist height
4. Operator picks/places item
5. Carousel stores tray and moves to next request

**Specifications**
- Height: 20-40 feet (6-12 meters)
- Footprint: 5' × 8' to 8' × 10' (1.5m × 2.5m to 2.5m × 3m)
- Capacity: 15,000-50,000 unit loads per module
- Cycle Time: 8-12 seconds for item retrieval
- Throughput: 300-500 picks per hour per operator

**Best For**
- High-SKU, low-velocity items
- Spare parts and aftermarket
- Healthcare and pharmaceuticals
- E-commerce (small orders)

**Leading Manufacturers**
- Kardex (Remstar and Megamat)
- Modula
- Schäfer Systems International
- Hanel
- Bastian Solutions

**Typical VLM Cost**
- Single module: $200,000-$500,000
- Installation: $50,000-$100,000 per module
- Software: $50,000-$100,000

---

### 2.3 Horizontal Carousels

**Technology**
Rotating shelves rotating around a central axis, bringing items to a fixed operator.

**How It Works**
1. Operator enters request
2. Carousel rotates to item location
3. Item presented at pick height
4. Operator picks/places item
5. Carousel moves to next request

**Specifications**
- Diameter: 12-20 feet (3.5-6 meters)
- Height: 6-20 feet (1.8-6 meters)
- Capacity: 5,000-50,000 unit loads
- Cycle Time: 3-6 seconds for rotation
- Throughput: 300-600 picks per hour per operator

**Advantages vs. VLMs**
- Lower cost
- Faster access times
- More flexible configuration
- Better for small to medium items

**Best For**
- General distribution
- Small parts logistics
- Retail operations
- Manufacturing support

**Leading Manufacturers**
- Kardex
- Schäfer Systems
- Modula
- Hanel

---

### 2.4 Robotic Shuttle Systems (RSS)

**Technology**
Motorized shuttles that move in 3D space on high-density racks, retrieving individual loads and bringing them to a picking station.

**How It Works**
1. WCS receives picking request
2. Shuttle retrieves load from assigned location
3. Shuttle delivers to picking station
4. Operator picks items or retrieves full load
5. Empty tray returned to storage via shuttle

**Specifications**
- Height: 30-50+ feet (9-15+ meters)
- Footprint: Flexible (modular racks)
- Density: 10x higher than traditional racking
- Cycle Time: 3-8 seconds per retrieval
- Throughput: 200-400 retrievals per hour

**System Components**
```
Robotic Shuttle System
├─ High-Density Racking (vertical)
├─ Motorized Shuttles (horizontal movement)
├─ Lift Systems (vertical movement)
├─ Picking Stations (G2P)
├─ WCS (Warehouse Control System)
└─ Sortation/Diverters (downstream)
```

**Best For**
- Large, complex warehouses
- High-volume operations
- Space-constrained locations
- End-to-end automation

**Leading Manufacturers**
- Swisslog (CarryPick, AutoStore via acquisition)
- Dematic (Kardex integration)
- Vanderlande
- Knapp
- Honeywell Intelligrated

**Typical RSS Cost**
- Full system (small): $2-5 million
- Full system (large): $5-20 million+
- Implementation: 12-18 months

---

### 2.5 Goods-to-Person (G2P) Systems

**Concept**
Goods are automatically brought to a fixed picking station, eliminating picker walking time.

**Technologies**
- Shuttle systems bringing totes/carts to workstation
- Conveyor bringing items to picker
- Mobile robots delivering goods
- Rotating carousels presenting items

**Benefits**
- Pick rates increase 2-5x
- Walking time reduced to zero
- Ergonomics improved (no bending, reaching)
- Accuracy improved (less movement errors)

**G2P Workflow**
```
Picking Request
       ↓
Automated Retrieval
       ↓
Transport to Station
       ↓
Operator Picks Item
       ↓
Item Conveyed to Packing
```

**Implementation Considerations**
- Significant capital investment
- Substantial throughput required for ROI
- Requires sophisticated WMS
- Needs change management for workforce

---

## 3. Conveyor and Sortation Systems

### 3.1 Conveyor Types

**Belt Conveyors**
- Continuous rubber/PVC belt over rollers
- Best for: General goods movement, inclines
- Speed: 60-400 feet per minute (0.3-2 m/s)
- Cost: $200-$500 per linear foot

**Roller Conveyors**
- Metal rollers in frame (powered or gravity)
- Best for: Pallets, totes, boxes
- Speed: 60-180 feet per minute
- Cost: $150-$400 per linear foot

**Sorter Conveyors**
- Specialized for routing items to different destinations
- Speed: 300-600 feet per minute
- Cost: $1,500-$5,000 per linear foot

### 3.2 Sortation Technologies

**Cross-Belt Sorters**
- Moving belts perpendicular to main flow
- Operates at high speed (600-1000 items per minute)
- Handles diverse items (shoes, books, clothing)
- Typical cost: $1-3 million per system
- Best for: E-commerce, parcels

**Tilt-Tray Sorters**
- Trays tilt to divert items
- Speed: 3,000-7,000 items per minute (highest)
- Gentle handling for fragile items
- Cost: $2-5 million for large systems
- Best for: High-volume e-commerce, parcels

**Swing-Shoe Sorters**
- Shoes swing out to deflect items
- Speed: 1,000-2,000 items per minute
- Robust for heavier items
- Cost: $1.5-3 million
- Best for: Groceries, distribution centers

**Comparison Table**

| Feature | Cross-Belt | Tilt-Tray | Swing-Shoe |
|---------|-----------|----------|-----------|
| **Speed** | 600-1000/min | 3000-7000/min | 1000-2000/min |
| **Capacity** | Medium | Very high | High |
| **Fragility** | Medium | High | Low-Medium |
| **Cost** | $1-3M | $2-5M | $1.5-3M |
| **Installation Time** | 6-9 months | 8-12 months | 6-10 months |

---

## 4. Palletizing and Depalletizing

### 4.1 Robotic Palletizers

**Technology**
Articulated robots or gantry systems automatically arrange items onto pallets.

**How It Works**
1. Items conveyed to palletizer
2. Robot picks item with specialized gripper
3. Places item in pattern on pallet
4. Builds pattern layer by layer
5. Wraps or stretches-wraps completed pallet

**Specifications**
- Pick speed: 1,200-2,400 picks per hour
- Accuracy: ±2-5mm
- Payload: 100-300 kg
- ROI: 2-4 years
- Payback: Reduction in labor cost

**Leading Manufacturers**
- KUKA (Robots + palletizing software)
- ABB (Industrial robots)
- Fanuc (High-speed robots)
- Yaskawa
- Stäubli

**Typical Cost**
- Robot system: $400,000-$800,000
- Gripper and tooling: $50,000-$200,000
- Controls and software: $100,000-$200,000
- Installation: $100,000-$200,000
- Total: $700,000-$1.4 million

---

### 4.2 Case Palletizing

**Standard Case Palletization**
- Cases of standard size (e.g., 12" × 10" × 8")
- Robot arranges cases in organized patterns
- High-speed, repetitive applications

**Mixed-Case Palletization**
- Different case sizes and weights
- Requires advanced vision and AI
- More complex programming
- Higher cost due to flexibility

**Pattern Optimization**
- Maximize pallet load (typically 40-48 cases per pallet)
- Consider weight distribution
- Account for stacking strength
- Minimize overhang for stability

---

## 5. Automation ROI Analysis

### 5.1 Cost-Benefit Analysis Framework

**Capital Costs**
```
Total CapEx = Equipment + Installation + Infrastructure + Software + Training

Equipment Cost: $500,000-$3,000,000 (varies by type)
Installation: 10-20% of equipment cost
Infrastructure: 5-10% of equipment cost
Software: 10-15% of equipment cost
Training: 2-5% of equipment cost
```

**Operational Costs**
```
Annual OpEx = Maintenance + Software License + Electricity + Labor

Maintenance: 5-10% of equipment cost annually
Software License: $50,000-$200,000 annually
Electricity: $30,000-$100,000 annually
Labor: Typically reduced 30-50% in automated areas
```

**Benefits**
```
Annual Benefits = Labor Savings + Productivity Gains + Error Reduction + ...

Labor Savings: $200,000-$500,000 annually (typical)
Productivity Gains: 20-50% throughput increase
Error Reduction: 2-5% cost savings from reduced damage/returns
Space Savings: 30-50% reduction in footprint
```

**ROI Calculation**
```
ROI = (Annual Benefits - Annual OpEx) / Total CapEx × 100%
Payback Period = Total CapEx / (Annual Benefits - Annual OpEx)

Typical: 3-5 year payback, 20-40% ROI
```

### 5.2 Factors Affecting ROI

**Positive ROI Factors**
- High volume operations (>100K units/day)
- Labor-intensive processes
- Tight labor market (high wage growth)
- Space constraints (expensive real estate)
- 24/7 operation requirements
- Quality/accuracy critical

**Negative ROI Factors**
- Low volume operations
- High product variety
- Unpredictable demand
- Frequent process changes
- High technology risk
- Vendor viability concerns

---

## 6. Implementation Considerations

### 6.1 Feasibility Assessment

**Throughput Analysis**
- Current and projected volume
- Seasonal variation
- Peak hour requirements
- Growth forecast

**Process Analysis**
- Item mix and sizes
- Handling complexity
- Quality requirements
- Customer demands

**Economic Analysis**
- Labor market conditions
- Land/real estate costs
- Equipment pricing trends
- Technology maturity

### 6.2 Phased Implementation

**Phase 1: Pilot (Months 1-6)**
- Single process or area
- Limited equipment (1-3 units)
- Learning and optimization
- ROI validation

**Phase 2: Expansion (Months 6-18)**
- Expand to adjacent processes
- Scale equipment deployment
- Refine operations
- Build expertise

**Phase 3: Integration (Months 12-24)**
- Full system optimization
- Advanced features (AI, ML)
- Integration across operations
- Continuous improvement

### 6.3 Risk Management

**Technical Risks**
- Equipment reliability
- Integration challenges
- Data quality issues
- Skills gaps

**Operational Risks**
- Workflow disruption
- Customer impact
- Employee resistance
- Vendor dependency

**Financial Risks**
- Cost overruns
- Delayed ROI
- Technology obsolescence
- Market changes

**Mitigation Strategies**
- Thorough due diligence
- Vendor evaluation
- Pilot programs
- Change management
- Performance monitoring

