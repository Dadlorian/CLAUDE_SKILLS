# MES Functions Reference - ISA-95 Standard Functions

This reference document details the eleven core MES functions defined in ISA-95 standard (ANSI/ISA-95.00.01-2010).

## Overview

MES functions represent the standard set of operations that a Manufacturing Execution System must support. These functions bridge enterprise planning systems (ERP) with shop floor automation and control systems (PLCs, SCADA, DCS).

The eleven MES functions are:
1. Production Scheduling
2. Production Dispatching
3. Production Execution
4. Genealogy Tracking
5. Exceptions/Alarms Management
6. Quality Management
7. Performance Analysis
8. Resource Management
9. Product Tracking and Genealogy
10. Operations Management
11. Production Unit Allocation

## Function 1: Production Scheduling

### Purpose
Create and optimize production schedules based on demand, resource constraints, and production capabilities.

### Input Data
- Master demand schedule from ERP
- Production order specifications
- Resource availability and capacity
- Equipment changeover times
- Lead times and dependencies
- Quality and compliance constraints

### Key Activities

**Demand Planning**
```
ERP Sends Demand
    ↓
Validate against Capacity
    ↓
Create Production Orders
    ↓
Sequence Orders
    ↓
Allocate Resources
    ↓
Publish Schedule to Shop Floor
```

**Constraint Handling**:
- Equipment capacity and availability
- Operator skills and availability
- Material availability
- Quality hold periods
- Maintenance windows
- Changeover and setup times
- Batch minimum/maximum sizes
- Storage space constraints

**Scheduling Algorithms**:
- First Come, First Served (FCFS)
- Shortest Job First (SJF)
- Critical Path Method (CPM) for job shop
- Constraint-based optimization
- Genetic algorithms for complex scenarios

### Output Data
- Production schedule with start/end times
- Equipment allocation
- Operator assignment
- Material requirements
- Expected inventory levels
- Schedule confidence metrics

### KPIs
- Schedule attainment (%)
- On-time delivery (%)
- Schedule variance (units)
- Capacity utilization (%)
- Resource utilization (%)
- Schedule stability (changes per week)

### System Requirements
- Real-time capacity visibility
- Bi-directional communication with ERP
- Constraint solver capability
- Historical performance data
- What-if analysis capability

### Integration Points
- **Input**: ERP (master schedule, demand)
- **Output**: Production Control, Resource Mgmt
- **Real-time Data**: Equipment availability, WIP

## Function 2: Production Dispatching

### Purpose
Translate scheduled production orders into work assignments for equipment, operators, and systems.

### Input Data
- Production schedule
- Detailed work order definitions
- Equipment capabilities
- Resource availability
- Material location and status
- Quality requirements
- Regulatory constraints

### Key Activities

**Work Order Creation**
```
Production Order (from Scheduling)
    ↓
Explode into Tasks
    ├─ Setup Task
    ├─ Execution Task
    ├─ Quality Task
    └─ Cleanup Task
    ↓
Assign to Resources
    ├─ Equipment Assignment
    ├─ Operator Assignment
    ├─ Material Reservation
    └─ Tool Reservation
    ↓
Create Dispatch List
    ↓
Send to Production Control Systems
```

**Dispatch List Elements**:
- Work order number and priority
- Product specification details
- Quantity to produce
- Start time and deadline
- Equipment and operator assignments
- Material lot numbers
- Quality checkpoints
- Safety and compliance notes

**Material Staging**:
- Identify required materials
- Check availability and location
- Reserve quantities
- Create pick list for warehouse
- Verify received materials match specification

**Setup Planning**:
- Define changeover procedures
- List tools and fixtures needed
- Environmental conditions to set
- Estimated setup time
- Validation points before execution

### Output Data
- Work orders ready for execution
- Equipment-specific instructions
- Material availability confirmation
- Resource assignment details
- Quality control checkpoints

### KPIs
- Dispatch accuracy (%)
- Work order creation time (minutes)
- Material availability (%)
- Setup efficiency (planned vs. actual)
- Dispatch system reliability (%)

### System Requirements
- Real-time inventory visibility
- Equipment status integration
- Work order template management
- Dispatch queue prioritization
- Exception handling for unavailable resources

## Function 3: Production Execution

### Purpose
Execute work orders on the production floor, collecting real-time data and managing execution.

### Input Data
- Dispatched work orders
- Equipment status and parameters
- Operator actions and inputs
- Sensor readings and equipment data
- Quality test results
- Material consumption data

### Key Activities

**Work Order Execution State Machine**
```
Not Started
    ↓
Ready to Execute (materials staged, equipment ready)
    ↓
Executing
    ├─ Setup Phase
    │   └─ Configure equipment, validate setup
    ├─ Run Phase
    │   └─ Execute production, collect data
    ├─ Quality Phase
    │   └─ Perform in-process quality checks
    └─ Cleanup Phase
        └─ Clean equipment, record final state
    ↓
Completed Successfully (or Failed/Aborted)
    ↓
Closed
```

**Data Collection**:
- Equipment sensor data (temperature, pressure, speed)
- Operator inputs (material consumed, counts, observations)
- Quality measurements (pass/fail, numerical values)
- Equipment events (start, stop, error, changeover)
- Timestamps for sequence reconstruction
- Environment conditions (temperature, humidity)

**Exception Management**:
- Equipment failure → stop execution, alert supervisor
- Quality out-of-spec → hold product, investigate
- Material shortage → request additional material or stop
- Operator error → log discrepancy, plan recovery
- Schedule deviation → adjust remaining schedule

### Output Data
- Execution status updates
- Real-time production data
- Quality results
- Exception events
- Consumed material quantities
- Resource utilization data
- Cycle time data

### KPIs
- First pass yield (%)
- Equipment uptime (%)
- Cycle time (minutes)
- Production variance (vs. plan)
- Exception rate and resolution time
- Data collection completeness (%)

### System Requirements
- Real-time status updates from equipment
- Operator interface for data entry
- Quality result integration
- Exception detection and alerting
- Equipment parameter tracking

## Function 4: Genealogy Tracking

### Purpose
Maintain forward and backward traceability of products through production.

### Input Data
- Work order execution records
- Material lot numbers consumed
- Equipment used during production
- Operator IDs and timestamps
- Quality test results
- Finished product batch/serial numbers
- Process parameters

### Key Activities

**Forward Traceability (Material → Finished Product)**
```
Raw Material Lot A (100 kg)
    ↓
Production Batch 2024-1234
    ├─ Start Time: 2024-11-19 08:00
    ├─ Equipment: Line1-Machine1
    ├─ Operator: jsmith
    ├─ Temperature Profile: 70-75°C
    ├─ Process Time: 120 minutes
    ├─ Quality Results: Pass
    └─ Output: Finished Product Batch FP-2024-5678 (95 kg)
                Lost in process: 5 kg (5% yield loss)
```

**Backward Traceability (Finished Product → Materials)**
```
Finished Product Serial #ABC-123456
    ↓
Used in Production Batch 2024-1234
    ↓
Contains Material Lot A (component)
    Contains Material Lot B (component)
    Contains Material Lot C (component)
    ↓
Source: Supplier ABC, Received 2024-11-01
        Supplier DEF, Received 2024-11-02
```

**Multi-Level Genealogy** (Sub-assemblies):
```
Finished Product XYZ-001
    ├─ Sub-assembly ABC-001
    │   ├─ Component 1 (Lot#12345)
    │   ├─ Component 2 (Lot#67890)
    │   └─ Production Batch PAB-2024-0001
    ├─ Sub-assembly DEF-001
    │   ├─ Component 3 (Lot#11111)
    │   └─ Production Batch PDE-2024-0002
    └─ Final Assembly Batch PFP-2024-0003
```

**Impact Analysis**:
```
Defect Detected: Material Lot A has contamination
    ↓
Query: Forward traceability for Lot A
    ↓
Returns: All finished products containing Lot A
    ├─ Batch 2024-1234 (100 units)
    ├─ Batch 2024-1235 (50 units)
    └─ Batch 2024-1236 (75 units)
    ↓
Action: Quarantine 225 units, Customer notification, Recall if shipped
```

### Data Captured
- Material lot/batch numbers
- Quantities consumed (kg, liters, counts)
- Consumption timestamps
- Equipment identification
- Equipment serial numbers
- Equipment parameters during production
- Operator IDs
- Quality test IDs and results
- Environmental conditions
- Storage conditions

### Regulatory Requirements

**FDA 21 CFR Part 11**:
- Batch records must include materials used
- Timestamps must be recorded
- Operator identification required
- Audit trail of all changes

**GAMP 5**:
- Traceability data secured and backed up
- Data integrity verification
- Access controls on sensitive batches

**ISO 9001**:
- Complete chain of custody
- Periodic verification

**IFS/FSSC 22000** (Food):
- Supplier information required
- Distribution data for product recall
- Communication procedures with suppliers/customers

### Output Data
- Genealogy reports (forward/backward)
- Impact analysis for defects
- Compliance audit trails
- Supplier/customer communication data
- Historical genealogy for archived batches

### KPIs
- Genealogy completeness (%)
- Traceability speed (minutes to retrieve)
- Root cause identification rate (%)
- Recall scope accuracy (false positives/negatives)
- Audit readiness (%)

### System Requirements
- Genealogy data storage (relational or graph database)
- Bidirectional relationship mapping
- Query capability for impact analysis
- Historical data archival
- Audit trail for genealogy changes

## Function 5: Exceptions/Alarms Management

### Purpose
Detect, track, and manage production exceptions and alarms.

### Exception Types

**Equipment Exceptions**:
- Machine failure or malfunction
- Sensor reading out of range
- Equipment not responding
- Maintenance alert
- Cycle time exceeding limits

**Quality Exceptions**:
- Test result out of specification
- Sample not available for testing
- Equipment calibration due
- Multiple consecutive failures
- SPC out-of-control signal

**Material Exceptions**:
- Material not available
- Material quantity incorrect
- Material expired or expired pending
- Material specification mismatch
- Storage conditions violated

**Scheduling Exceptions**:
- Resource unavailable
- Cannot meet schedule
- Multiple conflicting orders
- Setup time exceeded
- Changeover not possible

**Compliance Exceptions**:
- Required procedure not followed
- Authorization missing
- Audit trail gap
- Regulatory deadline approaching
- Document expiration

### Alarm Management Workflow

```
Exception Detected
    ↓
Alarm Generated and Categorized
    ├─ Severity: Critical / High / Medium / Low
    ├─ Type: Equipment / Quality / Material / Schedule / Compliance
    └─ Auto-escalation Path Defined
    ↓
Alert Sent to Responsible Party
    ├─ Operator (if on floor)
    ├─ Supervisor (if escalation)
    └─ Manager (if critical/compliance)
    ↓
Response Actions Available
    ├─ Acknowledge (operator aware)
    ├─ Investigate (supervisor inspecting)
    ├─ Take Action (fix implemented)
    ├─ Request Help (escalate)
    └─ Document (log for analysis)
    ↓
Root Cause Analysis (if critical)
    ├─ What happened?
    ├─ Why did it happen?
    ├─ When did it start?
    ├─ Impact assessment?
    └─ Corrective actions?
    ↓
Closure and Learning
    ├─ Alarm closed
    ├─ Root cause documented
    ├─ Preventive actions identified
    └─ Lessons learned shared
```

### Alarm Configuration

**Critical Alarm Example**:
```yaml
AlarmID: EQ001-HIGH-TEMP
Description: "Equipment temperature exceeds critical limit"
Severity: Critical
Equipment: Line1-Machine1
Condition: Temperature > 85°C for > 5 minutes
Action:
  - Immediate: Stop production, alert operator
  - 5 min: Alert supervisor
  - 15 min: Alert plant manager
  - 30 min: Notify maintenance
  - Email: operations@company.com
  - SMS: To on-call supervisor
Response Options:
  - Investigate and fix
  - Reduce temperature setpoint
  - Accept risk (with authorization)
  - Redirect to backup equipment
Documentation: Link to troubleshooting guide
```

### Output Data
- Real-time alarm notifications
- Alarm history and trends
- Root cause analysis reports
- Effectiveness of corrective actions
- Frequency and recurrence analysis

### KPIs
- Mean time to alarm resolution (minutes)
- Repeat alarm rate (%)
- Alarm false positive rate (%)
- Alarm response rate (% acknowledged)
- Prevention of recurrence (%)

## Function 6: Quality Management

### Purpose
Execute quality controls, record results, manage deviations.

### Quality Planning

**Quality Plan Definition**:
- Test specifications (what to measure)
- Acceptance criteria (pass/fail limits)
- Sampling strategy (frequency, location)
- Test methods and equipment
- Responsibility assignments
- Response actions for failures

**Quality Points in Production**:
- In-process quality (during production)
- End-of-line quality (after production)
- Lab quality (advanced testing)
- Customer feedback quality (post-sale)

### Quality Execution

**Test Recording**:
- Operator or automated system records result
- Measurement equipment and calibration status
- Environmental conditions if relevant
- Timestamp
- Operator/system identification
- Comments or observations

**Pass/Fail Decision**:
- Automatic comparison to limits
- Result status displayed to operator
- Hold triggered for failures
- Escalation to supervisor for investigation

**Non-Conformance Management**:
```
Quality Test Fails
    ↓
Product Held (cannot proceed)
    ↓
Investigation Initiated
    ├─ Document the problem
    ├─ Determine root cause
    ├─ Assess product impact
    └─ Assess process impact
    ↓
Corrective Action Plan
    ├─ Immediate action (contain problem)
    ├─ Temporary action (allow limited production)
    └─ Permanent action (prevent recurrence)
    ↓
Verification
    ├─ Effectiveness verified
    ├─ Similar issues checked
    └─ Process updated
    ↓
Closure and Learning
    ├─ Documentation complete
    ├─ Data analyzed for trends
    └─ Preventive actions identified
```

### Deviation Management

**Deviation Example**:
```
Deviation ID: DEV-2024-1234
Product: Widget A
Batch: 2024-1456
Issue: Color slightly off-specification
Date Discovered: 2024-11-19
Impact: 500 units affected

Root Cause: Supplier paint pigment variation
            Received from alternate supplier

Corrective Actions:
1. Quarantine 500 units for customer evaluation
2. Contact alternate supplier regarding specification
3. Implement receiving inspection for paint lots
4. Revise supplier specification requirements
5. Qualify backup paint suppliers

Timeline:
- Discovered: 2024-11-19 10:00 AM
- Investigation: 2024-11-19 11:30 AM
- Root Cause: 2024-11-19 2:00 PM
- CA Plan: 2024-11-20 9:00 AM
- CA Implemented: 2024-11-21 5:00 PM
- Verified Effective: 2024-11-22 3:00 PM
- Closed: 2024-11-23 10:00 AM
```

## Function 7: Performance Analysis

### Purpose
Measure, analyze, and report on production performance.

### Overall Equipment Effectiveness (OEE)

**Three Components**:
```
OEE = Availability × Performance × Quality

Availability = Scheduled Time - Downtime / Scheduled Time
Performance = Theoretical Cycle Time × Count / Running Time
Quality = Good Pieces / Total Pieces
```

**Example Calculation**:
```
Production Window: 8 hours = 480 minutes
Planned Downtime: 30 minutes (shifts, breaks)
Scheduled Time = 450 minutes

Actual Downtime: 30 minutes (equipment jam)
Running Time: 420 minutes
Availability = (450 - 30) / 450 = 93.3%

Theoretical Cycle Time: 2 minutes/part
Parts Produced: 150
Theoretical Time: 150 × 2 = 300 minutes
Performance = 300 / 420 = 71.4%

Parts Produced: 150
Good Parts: 142
Quality = 142 / 150 = 94.7%

OEE = 0.933 × 0.714 × 0.947 = 63.0%
```

**OEE Benchmarks**:
- World Class: > 85%
- Good: 75-85%
- Average: 60-75%
- Poor: < 60%

### Cycle Time Analysis

**Components of Cycle Time**:
```
Total Cycle Time = Setup Time + Processing Time + Wait Time + Transit Time

Setup Time: 15 minutes (tooling change, configuration)
Processing Time: 120 minutes (actual production)
Wait Time: 30 minutes (waiting for operator, inspection)
Transit Time: 5 minutes (movement between stations)
Total: 170 minutes
```

### Resource Utilization

**Equipment Utilization**:
- Available hours: 80 (10 days × 8 hours/day)
- Scheduled hours: 70 (accounting for maintenance)
- Actual running hours: 50
- Equipment utilization: 50/70 = 71.4%

**Operator Utilization**:
- Scheduled hours: 70
- Productive hours: 45 (actual production time)
- Non-productive: 25 (training, meetings, miscellaneous)
- Operator utilization: 45/70 = 64.3%

### Production Efficiency Metrics

- Throughput: Units produced per unit time
- Lead time: Time from order to delivery
- On-time delivery: % of orders meeting due date
- Schedule variance: Actual vs. planned production
- Waste/scrap percentage
- Rework percentage
- Cost performance: Actual vs. budgeted costs

## Function 8: Resource Management

### Purpose
Manage equipment, tools, personnel, and materials.

### Resource Types and Tracking

**Equipment Management**:
- Asset ID and serial number
- Location and responsible owner
- Capability and capacity data
- Current status (running, idle, maintenance, down)
- Scheduled maintenance dates
- Utilization history
- Performance data
- Spare parts inventory

**Tool Management**:
- Tool identification
- Tool location and availability
- Usage tracking (total uses, hours)
- Wear limits and replacement criteria
- Calibration status and dates
- Tool life and depreciation
- Preventive replacement schedule

**Personnel Resource Management**:
- Operator qualifications and certifications
- Available hours per shift
- Training records
- Competency assessments
- Shift assignments
- Availability calendar

**Material Resource Management**:
- Current inventory location
- Stock levels (current, minimum, maximum)
- Expiration dates
- Lot traceability
- Reserved quantities
- Storage requirements
- Supply lead times

### Resource Allocation

**Equipment Allocation**:
```
Production Order: Widget A × 1000 units
Required Processing Time: 120 minutes
Equipment Options:
  - Line1-Machine1: Available, 2 hour lead time
  - Line1-Machine2: Down until 3:00 PM
  - Line2-Machine1: Available, 4 hour lead time (longer)

Recommendation: Allocate to Line1-Machine1
Scheduled Start: 10:00 AM
Scheduled Completion: 12:00 PM
```

**Personnel Allocation**:
```
Work Order Tasks:
  - Setup: 0.5 hours (skill: Equipment Technician)
  - Operation: 2 hours (skill: Machine Operator)
  - Quality: 0.5 hours (skill: Quality Inspector)

Available Resources:
  - Operator John (qualified for all): 1.5 hours available
  - Operator Mary (qualified for all): 2.5 hours available
  - Technician Bob (setup only): 1 hour available

Allocation:
  - Bob for setup (0.5 hrs, 8:00-8:30 AM)
  - Mary for operation (2 hrs, 8:30-10:30 AM)
  - John for quality (0.5 hrs, 10:30-11:00 AM)
```

## Function 9: Operations Management

### Purpose
Real-time coordination of production execution.

### Shift Operations Workflow

```
Shift Start
    ↓
Briefing (previous shift summary, planned work)
    ↓
Equipment Startup (pre-production checks)
    ↓
Work Order Dispatch
    ↓
Throughout Shift:
    ├─ Monitor production status
    ├─ Address exceptions and alarms
    ├─ Adjust schedule if needed
    ├─ Collect quality data
    ├─ Record consumable usage
    └─ Maintain equipment
    ↓
Production Completion
    ↓
Shift End
    ├─ Equipment shutdown
    ├─ Quality release if OK
    ├─ Document exceptions
    └─ Handover to next shift
    ↓
Shift End Reporting
    ├─ Production totals
    ├─ Quality summary
    ├─ Equipment issues
    └─ Staffing notes
```

### Metrics Monitored During Operations

- **Current Production Rate**: Units/hour
- **Cumulative Production**: Units produced so far
- **Scheduled vs. Actual**: Comparing to plan
- **Equipment Status**: Running, idle, down
- **Quality Pass Rate**: Real-time yield
- **Scrap/Defect Count**: Number and types
- **Equipment Condition**: Temperature, pressure, vibration
- **Inventory Status**: Materials on hand vs. expected

## Function 10: Resource Optimization

### Purpose
Analyze and recommend resource utilization improvements.

### Bottleneck Analysis

```
Production Flow Analysis:
  Step 1: Paint Booth → 500 units/day capacity
  Step 2: Assembly    → 800 units/day capacity
  Step 3: Test        → 600 units/day capacity

Current Production:
  Step 1: 450 units/day (90% utilization)
  Step 2: 380 units/day (47% utilization) ← BOTTLENECK
  Step 3: 350 units/day (58% utilization)

Bottleneck Impact:
- Overall capacity limited to 350 units/day
- Assembly equipment running at low utilization
- Waiting time at previous steps

Solution Options:
1. Add assembly capacity (add equipment)
2. Improve assembly efficiency (faster process)
3. Cross-train for multi-skilled assembly work
4. Extend operating hours for assembly
```

## Function 11: Production Unit Allocation

### Purpose
Define and manage equipment groupings for production.

### Production Unit Hierarchy

```
Plant (Site-level grouping)
    ├─ Production Line
    │   ├─ Work Cell 1
    │   │   ├─ Equipment A
    │   │   ├─ Equipment B
    │   │   └─ Equipment C
    │   ├─ Work Cell 2
    │   └─ Work Cell N
    ├─ Production Line 2
    └─ Production Line N
```

### Production Unit Definition

**Master Data for Each Unit**:
- Unit identification and location
- Equipment list with serial numbers
- Operating capability (what products can be made)
- Capacity (units/time)
- Operating hours/shifts
- Planned maintenance windows
- Safety and environmental requirements
- Operator qualifications needed

## Summary: MES Functions Integration

All eleven functions work together in an integrated MES:

```
Production Scheduling (1)
    ↓
Production Dispatching (2)
    ↓
Production Execution (3)
    ├─ Collects data for
    │   ├─ Genealogy Tracking (4)
    │   ├─ Quality Management (6)
    │   ├─ Performance Analysis (7)
    │   └─ Exceptions Management (5)
    ↓
Resource Management (8)
    ↓
Operations Management (9)
    ↓
Resource Optimization (10) + Production Unit Allocation (11)
    ↓
Feedback to ERP System and Next Planning Cycle
```

This integrated approach ensures complete visibility, traceability, compliance, and continuous improvement.
