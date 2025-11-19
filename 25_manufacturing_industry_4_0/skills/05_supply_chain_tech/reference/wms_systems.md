# WMS Systems Reference Guide

## 1. WMS Platform Comparison

### 1.1 Manhattan Associates WMS

**Overview**
Manhattan Associates is the leading cloud-native WMS platform, designed for modern omnichannel operations. It's particularly strong in e-commerce, retail, and complex distribution operations.

**Key Features**
- Cloud-native architecture with high scalability
- Real-time inventory visibility across channels
- Advanced picking optimization (zone, batch, cluster)
- Integration with Manhattan Order Management System (OMS)
- AI-powered demand sensing and inventory optimization
- Mobile workforce management
- Labor management system (LMS) integrated
- Returns and reverse logistics

**Architecture**
```
Manhattan Warehouse Execution Platform
├─ Warehouse Execution Services
│  ├─ Inventory Management
│  ├─ Order Fulfillment
│  ├─ Labor Optimization
│  └─ Operations Monitoring
├─ Inventory Visibility Platform
│  ├─ Real-time Inventory
│  ├─ Allocation Engine
│  └─ Demand Sensing
├─ Warehouse Analytics
│  ├─ KPI Dashboard
│  ├─ Predictive Analytics
│  └─ Optimization
└─ Integration Hub (MULE)
   ├─ API Integration
   ├─ EDI
   └─ File-based Integration
```

**Deployment Options**
- Cloud (SaaS) - Primary offering
- Dedicated cloud instances
- Region-specific deployments

**Typical Implementation Timeline**
- Discovery and planning: 4-6 weeks
- Configuration: 8-12 weeks
- Testing and UAT: 6-8 weeks
- Go-live: 2-4 weeks
- Total: 6-9 months for standard implementation

**Best For**
- E-commerce and omnichannel retailers
- High-volume, fast-moving operations
- Organizations requiring cloud scalability
- Complex distribution networks

**Integration Ecosystem**
- ERP: SAP, Oracle, NetSuite, Infor
- OMS: Manhattan OMS, Shopify, WooCommerce
- TMS: JDA, Blue Yonder, SAP TM
- Analytics: Tableau, Qlik, Power BI
- IoT: MuleSoft for custom integrations

**Pricing Model**
- SaaS license based on SKU, transaction volume, and users
- Implementation and consulting fees
- Annual support and maintenance
- Typical cost: $500K-$5M+ depending on complexity

---

### 1.2 SAP Extended Warehouse Management (EWM)

**Overview**
SAP EWM is an enterprise-grade WMS tightly integrated with SAP ERP and S/4HANA. It's designed for large, complex organizations with sophisticated supply chain requirements.

**Key Features**
- Tight integration with SAP S/4HANA
- Advanced warehouse robotics integration
- Cross-docking and value-added services
- Wave management and optimization
- Labor management and task interleaving
- Quality management integration
- Global warehouse network management
- Advanced picking optimization with RF terminals

**Architecture**
```
SAP Extended Warehouse Management
├─ Warehouse Operations
│  ├─ Goods Receipt
│  ├─ Putaway
│  ├─ Inventory Management
│  ├─ Order Picking
│  └─ Goods Issue
├─ Warehouse Execution
│  ├─ Wave Planning
│  ├─ Task Management
│  ├─ Labor Management
│  └─ Task Interleaving
├─ Warehouse Analytics
│  ├─ Real-time Dashboards
│  ├─ Performance Reports
│  └─ Predictive Analytics
├─ Integration
│  ├─ ERP Integration (S/4HANA)
│  ├─ WCS Integration
│  └─ Robotics Integration
└─ Mobile & Reporting
   ├─ RF Terminal Management
   ├─ Mobile Apps
   └─ Analytics
```

**Deployment Options**
- On-Premise S/4HANA
- SAP Cloud Platform (SCP)
- SAP S/4HANA Cloud
- Hybrid deployments

**Typical Implementation Timeline**
- Discovery and requirements: 4-8 weeks
- Design and configuration: 12-16 weeks
- Development and customization: 8-16 weeks
- Testing and UAT: 8-12 weeks
- Go-live: 2-4 weeks
- Total: 9-15 months for enterprise implementation

**Best For**
- Large enterprises with SAP infrastructure
- Complex manufacturing and distribution
- Organizations with multiple warehouses
- High-volume operations with robotics

**Integration Ecosystem**
- ERP: SAP S/4HANA (native), SAP ERP
- Planning: SAP Supply Chain Planning
- TMS: SAP Transportation Management
- Robotics: Swisslog, Dematic, Vanderlande
- Analytics: SAP Analytics Cloud, BusinessObjects
- MES: SAP Manufacturing Execution

**Pricing Model**
- License fees based on concurrent users and system size
- Significant implementation costs (typically $2M-$10M+)
- Professional services: High cost for customization
- Annual maintenance and support

---

### 1.3 Blue Yonder WMS

**Overview**
Blue Yonder (formerly JDA Software) offers a comprehensive WMS designed for retailers and distributors with strong TMS and supply chain planning integration.

**Key Features**
- Omnichannel fulfillment optimization
- Integrated TMS and OMS
- AI-powered demand and inventory optimization
- Supply chain visibility
- Cross-location inventory management
- Labor optimization
- Quality management
- Mobile operations

**Key Differentiators**
- Superior omnichannel capabilities
- Integrated TMS for end-to-end visibility
- Supply chain planning integration
- AI-driven optimization
- Strong in fashion and retail sectors

**Deployment Options**
- Cloud SaaS
- Hybrid cloud
- Private cloud

**Typical Implementation Timeline**
- Planning and discovery: 4-6 weeks
- Configuration: 8-12 weeks
- Testing: 6-8 weeks
- Go-live: 2-4 weeks
- Total: 5-8 months

**Best For**
- Retailers and distributors
- Omnichannel operations
- Fashion and apparel
- Organizations needing integrated TMS

---

### 1.4 Aptean WMS

**Overview**
Aptean (formerly Logility) provides WMS solutions for mid-market to enterprise organizations, with strong supply chain planning capabilities.

**Key Features**
- Flexible, configurable platform
- Strong supply chain planning integration
- Multi-location management
- Advanced picking and putaway
- Labor management
- Quality management
- Reporting and analytics
- Mobile workforce management

**Deployment Options**
- Cloud (SaaS)
- On-Premise
- Hybrid

**Typical Implementation Timeline**
- Discovery: 2-4 weeks
- Configuration: 6-10 weeks
- Testing: 4-6 weeks
- Go-live: 1-2 weeks
- Total: 4-6 months for standard implementation

**Best For**
- Mid-market organizations
- Manufacturing and distribution
- Organizations with integrated planning needs
- Flexible, customizable requirements

---

### 1.5 HighJump WMS

**Overview**
HighJump (now Flexport) focuses on logistics service providers and mid-market distributors with emphasis on ease of implementation and rapid ROI.

**Key Features**
- Fast implementation
- User-friendly interface
- Strong 3PL capabilities
- Order management
- Billing and chargeback
- Quality management
- Advanced analytics
- Flexible architecture

**Best For**
- 3PLs and logistics providers
- Mid-market distributors
- Fast-growth organizations
- Rapid implementation requirements

---

## 2. WMS Key Modules Deep Dive

### 2.1 Inventory Management Module

**Core Functions**
- SKU master data management
- Inventory levels across locations and bins
- Cycle counting and physical counts
- Inventory movements and adjustments
- Aging analysis and obsolescence management
- Lot and serial number tracking

**Key Configuration Items**
- Location types and structures
- Inventory status (available, reserved, damaged, etc.)
- Holding units and handling units
- Lot traceability rules
- ABC classification scheme

**Integration Points**
- ERP for master data synchronization
- WCS for automated movement
- Barcode/RFID for validation
- Demand planning for visibility

### 2.2 Order Management Module

**Core Functions**
- Order receipt and validation
- Order allocation to warehouses/locations
- Backorder management
- Order consolidation
- Shipping order creation
- Billing integration

**Key Configuration Items**
- Order types and profiles
- Allocation rules (first-come-first-served, priority-based, etc.)
- Backorder policies
- Consolidation rules
- Order splitting rules

**Integration Points**
- OMS/ERP for order creation
- Inventory management for availability
- Picking module for fulfillment
- Shipping/TMS for execution

### 2.3 Picking Module

**Core Functions**
- Pick wave creation and planning
- Pick list generation
- Batch, cluster, and zone picking support
- Pick verification (dimension, weight, barcode)
- Put-to-line (PTL) and pick-to-light (PTL) support
- Voice-directed picking integration
- Mobile device support
- Exception handling

**Picking Strategies**

| Strategy | Description | Best For |
|----------|-----------|----------|
| Single Pick | One order at a time | Low volume, complex orders |
| Batch Picking | Combine orders by destination | High volume, simple items |
| Cluster Picking | Combine orders by location | Multiple location visits |
| Zone Picking | Dedicated team per zone | Large warehouses |
| Wave Picking | Time-based grouping | Retail distribution |

**Key Performance Optimization**
- Aisle optimization
- Distance minimization
- Item sequencing
- Batching algorithms
- Labor balancing

### 2.4 Putaway Module

**Core Functions**
- Inbound receipt creation
- Location assignment (directed putaway)
- Putaway task generation
- Cross-docking setup
- Receiving area management
- Exception handling

**Putaway Strategies**

| Strategy | Description | Criteria |
|----------|-----------|----------|
| Slotting-based | High-velocity items in pick zone | Velocity, weight, size |
| FIFO | First received, first shipped | Product expiration dates |
| ABC | A-items in best locations | Turnover rate |
| Closest Available | Nearest available location | Speed of putaway |

**Slotting Analysis**
- Velocity analysis (units/time period)
- Slot utilization
- Replenishment frequency
- Putaway time vs. storage cost

### 2.5 Labor Management Module

**Core Functions**
- Labor tracking and time capture
- Productivity measurement
- Task management and assignment
- Incentive management
- Safety monitoring
- Reporting and analytics

**Key Metrics**
- Lines picked per hour (LPH)
- Cases received per hour
- Cases shipped per hour
- Cost per line/case
- Safety incidents
- Absence rates

---

## 3. WMS Implementation Approach

### 3.1 Pre-Implementation Phase

**1. Current State Assessment**
- Document existing processes
- Identify pain points
- Analyze transaction volumes
- Evaluate data quality
- Define KPIs

**2. Future State Design**
- Map optimized processes
- Define system requirements
- Plan organizational structure
- Design training program
- Establish governance model

**3. Project Planning**
- Develop detailed timeline
- Resource planning
- Budget allocation
- Risk assessment
- Stakeholder management

### 3.2 Configuration Phase

**System Setup**
- Warehouse structure definition
- Location type setup
- Inventory status configuration
- User creation and role assignment
- Mobile device setup

**Master Data**
- Product master
- Location master
- Vendor master
- Customer master
- Carrier master

**Business Rules**
- Allocation rules
- Putaway strategies
- Picking strategies
- Cross-docking rules
- Exception handling rules

### 3.3 Testing Phase

**Unit Testing**
- Individual module testing
- Business rule validation
- Integration point testing
- Data quality verification

**System Testing**
- End-to-end process testing
- Volume testing
- Performance testing
- Security testing

**User Acceptance Testing (UAT)**
- Business user validation
- Process alignment verification
- Training during UAT
- Sign-off on requirements

### 3.4 Go-Live Approach

**Big-Bang Approach**
- Advantages: Clean cutover, single learning curve
- Disadvantages: High risk, potential disruption
- Best for: Small operations, simple processes

**Phased Approach**
- Phase by location/operation
- Advantages: Lower risk, staged rollout
- Disadvantages: Complex integration period, longer timeline
- Best for: Large, complex operations

**Parallel Approach**
- Run old and new systems simultaneously
- Advantages: Highest safety, validation possible
- Disadvantages: Most expensive, longest duration
- Best for: Critical operations requiring high confidence

---

## 4. WMS Integration Patterns

### 4.1 ERP Integration

**Master Data Synchronization**
```
ERP              WMS
Product Master ←→ SKU Master
Inventory      ←→ Stock Levels
Customer       ←→ Ship-To Customer
Vendor         ←→ Vendor Master
```

**Transaction Flow**
```
Purchase Order (ERP) → Receipt (WMS) → Goods Receipt (ERP)
Sales Order (ERP) → Picking (WMS) → Shipment (ERP)
```

### 4.2 OMS Integration

**Order Flow**
```
Customer Order → OMS → WMS (Picking) → Shipping → OMS (Status) → Customer
```

**Real-Time Updates**
- Order status updates
- Inventory availability
- Shipment tracking
- Exception notifications

### 4.3 TMS Integration

**Shipment Information**
- Pick quantity and details
- Weight and dimensions
- Carrier instructions
- Destination information

**Execution Information**
- Shipment confirmation
- Tracking numbers
- Proof of delivery
- Exception handling

### 4.4 Automation Integration

**WMS to WCS (Warehouse Control System)**
```
WMS          WCS          Equipment
Picking Task → Routing → AGV/Conveyor
```

**Real-Time Feedback**
- Task completion
- Equipment status
- Exception notifications
- Performance metrics

---

## 5. WMS Deployment Checklist

### Pre-Go-Live
- [ ] All master data loaded and validated
- [ ] All integrations tested and working
- [ ] All users trained
- [ ] All business processes documented
- [ ] All reports created and validated
- [ ] Hardware (RF terminals, scanners, printers) installed
- [ ] Contingency/rollback plan documented
- [ ] Support team trained and available
- [ ] Vendor cutover support confirmed
- [ ] Data archival plan documented

### Go-Live
- [ ] Old system snapshot taken
- [ ] All users logged out of old system
- [ ] Final data sync executed
- [ ] System cutover executed
- [ ] Initial transactions processed successfully
- [ ] Key reports validated
- [ ] Stakeholder notifications sent
- [ ] Hypercare team monitoring

### Post-Go-Live
- [ ] First week performance monitored closely
- [ ] Issues logged and resolved
- [ ] User questions addressed
- [ ] Process refinements documented
- [ ] Optimization opportunities identified
- [ ] Two-week health check completed
- [ ] 30-day review conducted
- [ ] Handoff to operations team
- [ ] Benefits realization tracking initiated

---

## 6. WMS Selection Criteria

### Evaluation Factors

| Factor | Weight | Evaluation |
|--------|--------|------------|
| Functionality | 25% | Match to current/future requirements |
| Scalability | 20% | Support for growth, multi-location |
| Integration | 15% | ERP, OMS, TMS, automation compatibility |
| Ease of Use | 10% | User interface, mobile capabilities |
| Vendor Stability | 10% | Financial viability, market position |
| Cost | 10% | Licensing, implementation, support |
| Support | 5% | Local support, response time, expertise |
| References | 5% | Customer experiences, similar industry |

### Scoring Template

For each vendor:
1. Score 1-5 on each factor
2. Multiply by weight
3. Sum weighted scores
4. Higher score = better fit

Example:
- Vendor A: 4.2/5.0
- Vendor B: 3.8/5.0
- Vendor C: 4.0/5.0

---

## 7. WMS Troubleshooting Guide

### Common Issues and Solutions

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Inventory discrepancies | Data sync issues, manual adjustments | Validate cycle counts, audit adjustments |
| Pick accuracy problems | Poor location labeling, training gaps | Improve signage, reinforce training |
| System slowness | High transaction volume, database issues | Optimize queries, archive old data |
| Integration failures | Connection issues, data format mismatch | Check APIs, validate data mapping |
| User adoption resistance | Complex interface, insufficient training | Simplify workflows, provide refresher training |

