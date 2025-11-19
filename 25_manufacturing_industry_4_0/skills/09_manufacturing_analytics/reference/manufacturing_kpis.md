# Manufacturing KPIs: Comprehensive Reference Guide

## Table of Contents
1. [Overall Equipment Effectiveness (OEE)](#overall-equipment-effectiveness-oee)
2. [Mean Time Between Failures (MTBF)](#mean-time-between-failures-mtbf)
3. [Mean Time To Repair (MTTR)](#mean-time-to-repair-mttr)
4. [Yield and Quality Metrics](#yield-and-quality-metrics)
5. [Efficiency and Utilization Metrics](#efficiency-and-utilization-metrics)
6. [Cost Metrics](#cost-metrics)
7. [Time-Based Metrics](#time-based-metrics)
8. [Supply Chain Metrics](#supply-chain-metrics)
9. [Safety and Environmental Metrics](#safety-and-environmental-metrics)
10. [Industry Benchmarks](#industry-benchmarks)

## Overall Equipment Effectiveness (OEE)

### Definition
OEE is a key metric that measures how effectively an asset is utilized. It accounts for three key components:

**Formula**:
```
OEE = Availability × Performance × Quality
```

### Components

#### 1. Availability
**Definition**: The percentage of time equipment is available to operate

**Formula**:
```
Availability = (Total Operating Time - Downtime) / Total Operating Time × 100%

Where:
- Total Operating Time = Scheduled Production Time - Planned Downtime
- Downtime = Unplanned maintenance + Changeovers + Setup failures
```

**Calculation Example**:
```
Scheduled Time: 480 minutes (8 hours shift)
Planned Downtime: 30 minutes (scheduled lunch)
Available Time: 450 minutes

Actual Downtime: 60 minutes
Operating Time: 390 minutes

Availability = 390 / 450 × 100% = 86.67%
```

**Typical Values**:
- World Class: > 90%
- Excellent: 75-90%
- Good: 65-75%
- Fair: 50-65%
- Poor: < 50%

**Improvement Strategies**:
- Preventive maintenance programs
- Root cause analysis of failures
- Quick changeover techniques (SMED)
- Redundant equipment for critical processes
- Real-time monitoring and early alerts

#### 2. Performance (Speed/Efficiency)
**Definition**: The rate at which equipment operates relative to its theoretical maximum

**Formula**:
```
Performance = (Ideal Cycle Time × Units Produced) / Actual Run Time × 100%

Or alternative:
Performance = Actual Output / Theoretical Maximum Output × 100%
```

**Calculation Example**:
```
Theoretical Cycle Time: 30 seconds per unit
Units Produced: 35 units
Actual Run Time: 20 minutes (1200 seconds)

Theoretical Time Needed: 35 × 30 = 1050 seconds
Performance = 1050 / 1200 × 100% = 87.5%
```

**Loss Categories**:
- Idling and minor stops (typically 5-10%)
- Reduced speed operations (10-15%)
- Power loss and brownouts (2-5%)

**Typical Values**:
- World Class: > 95%
- Excellent: 85-95%
- Good: 75-85%
- Fair: 60-75%
- Poor: < 60%

**Improvement Strategies**:
- Equipment tuning and optimization
- Operator training and skill development
- Material supply optimization
- Predictive maintenance to prevent slowdowns
- Process optimization studies

#### 3. Quality
**Definition**: The percentage of good units produced on the first pass

**Formula**:
```
Quality = Good Units Produced / Total Units Produced × 100%

Good Units = Total Units - Scrap - Rework
```

**Calculation Example**:
```
Total Units Produced: 100
Scrap: 3 units
Rework: 2 units
Good Units: 95

Quality = 95 / 100 × 100% = 95%
```

**Related Metrics**:
- First Pass Yield (FPY): Units passing all tests on first attempt
- Defects Per Million Opportunities (DPMO)
- Cost of Poor Quality (COPQ)

**Typical Values**:
- World Class: > 99%
- Excellent: 95-99%
- Good: 90-95%
- Fair: 85-90%
- Poor: < 85%

**Improvement Strategies**:
- Statistical process control
- Design of experiments
- Mistake-proofing (poka-yoke)
- Training on quality standards
- Real-time quality monitoring

### Overall OEE Calculation

**Combined Metric**:
```
OEE = Availability × Performance × Quality
```

**Example**:
```
Availability: 86.67%
Performance: 87.5%
Quality: 95%

OEE = 0.8667 × 0.875 × 0.95 = 0.722 = 72.2%
```

**OEE Levels and Industry Benchmarks**:
- World Class: > 85%
- Excellent: 75-85%
- Good: 65-75%
- Fair: 50-65%
- Poor: < 50%

## Mean Time Between Failures (MTBF)

### Definition
MTBF is the average time elapsed between one failure and the next failure of a non-repairable component or equipment.

### Calculation

**Formula**:
```
MTBF = Total Operating Time / Number of Failures

Or for multiple units:
MTBF = (Sum of All Operating Times) / (Total Number of Failures)
```

**Calculation Example**:
```
Equipment operates for 8,000 hours
Number of failures: 4

MTBF = 8,000 / 4 = 2,000 hours
```

### Units and Conversion

**Common Units**:
- Hours: For continuous operations
- Days: For equipment operating 8-16 hours/day
- Production Cycles: For batch or cyclical operations

**Conversion**:
```
MTBF (days) = MTBF (hours) / Operating hours per day

Example:
MTBF = 2,000 hours
Equipment operates 16 hours/day
MTBF = 2,000 / 16 = 125 days
```

### Failure Rate

**Inverse Relationship**:
```
Failure Rate (λ) = 1 / MTBF

MTBF = 1 / λ
```

**Example**:
```
If MTBF = 2,000 hours
Then λ = 1/2,000 = 0.0005 failures/hour
Or 0.5 failures per 1,000 hours
```

### Bathtub Curve

Equipment failure rate typically follows a bathtub curve:

```
Failure Rate
    ▲
    │     ╱╲
    │    ╱  ╲
    │   ╱    ╲___
    │  ╱      Wear-out Zone
    │ ╱ Infant Mortality
    │╱_____Useful Life Zone
    └─────────────────────► Time

Zones:
1. Infant Mortality: High initial failure rate (defective units)
2. Useful Life: Constant, low failure rate (random failures)
3. Wear-out: Increasing failure rate (age-related failures)
```

### Industry Benchmarks by Equipment Type

**Process Equipment**:
- Pumps: 10,000-50,000 hours
- Motors: 20,000-100,000 hours
- Compressors: 15,000-60,000 hours
- Conveyor Systems: 5,000-30,000 hours

**Mechanical Equipment**:
- Bearing: 5,000-25,000 hours
- Gearbox: 15,000-50,000 hours
- Valve: 20,000-100,000 hours
- Shaft: 50,000+ hours

**Semiconductor Equipment**:
- Etchers: 2,000-5,000 hours
- Lithography: 1,000-3,000 hours
- Chemical mechanical polishing: 3,000-8,000 hours

### Tracking and Analysis

**Data Collection**:
- Failure date and time
- Equipment identification
- Failure mode and description
- Repair actions taken
- Total operating time since last failure

**Analysis Methods**:
- Weibull analysis for failure distribution
- Pareto analysis of failure modes
- Trend analysis for degradation
- Predictive models for RUL (Remaining Useful Life)

## Mean Time To Repair (MTTR)

### Definition
MTTR is the average time required to restore a piece of equipment to working condition after a failure.

### Calculation

**Formula**:
```
MTTR = Total Downtime / Number of Repairs

Where:
Downtime = Detection Time + Diagnosis Time + Repair Time + Testing Time
```

**Calculation Example**:
```
Equipment had 4 failures with downtimes:
- Failure 1: 4 hours
- Failure 2: 3.5 hours
- Failure 3: 5 hours
- Failure 4: 2.5 hours

Total Downtime: 15 hours
MTTR = 15 / 4 = 3.75 hours
```

### Components of MTTR

**1. Detection Time**:
- Time to recognize that failure occurred
- Can be zero for self-announcing failures
- Minutes to hours for gradually degrading equipment

**2. Diagnosis Time**:
- Time to identify root cause
- Depends on failure complexity
- Critical for quick repairs

**3. Repair Time**:
- Actual time to fix the equipment
- Includes parts acquisition if not on hand
- Longest component for major repairs

**4. Testing and Verification**:
- Time to verify repair was successful
- Safety verification if applicable
- Performance verification

### Typical Values by Industry

**Discrete Manufacturing**:
- Simple equipment: 0.5-2 hours
- Complex equipment: 2-8 hours
- Highly complex systems: 8-24+ hours

**Process Manufacturing**:
- Simple processes: 1-3 hours
- Complex processes: 3-12 hours
- Integrated plants: 12-48+ hours

**Target Benchmarks**:
- World Class: < 2 hours
- Excellent: 2-4 hours
- Good: 4-8 hours
- Fair: 8-16 hours
- Poor: > 16 hours

### Improvement Strategies

**1. Reduce Detection Time**:
- Real-time monitoring systems
- Automated alarms and alerts
- Predictive monitoring (detect before failure)
- Sensor-based fault detection

**2. Reduce Diagnosis Time**:
- Technician training and skill
- Diagnostic equipment and tools
- Standard troubleshooting procedures
- Historical failure documentation
- AI-assisted diagnostics

**3. Reduce Repair Time**:
- Spare parts availability
- Standardized replacement procedures
- Quick-disconnect designs
- Modular equipment components
- Preventive maintenance

**4. Improve Testing**:
- Quick verification procedures
- Automated testing systems
- Clear acceptance criteria
- Performance monitoring integration

## Yield and Quality Metrics

### First Pass Yield (FPY)

**Definition**: Percentage of units that pass all tests on first attempt without rework

**Formula**:
```
FPY = (Total Units - Rework Units - Scrap Units) / Total Units × 100%

Or equivalently:
FPY = Good Units / Total Units × 100%
```

**Example**:
```
Total units produced: 1,000
Rework units: 50
Scrap units: 20
Good units: 930

FPY = 930 / 1,000 × 100% = 93%
```

**Benchmarks**:
- Automotive: 98%+
- Electronics: 95%+
- General Manufacturing: 90-95%
- Food and Beverage: 92-97%

### Rolled Throughput Yield (RTY)

**Definition**: Probability that a product passes all process steps without any rework

**Formula**:
```
RTY = FPY(Step 1) × FPY(Step 2) × ... × FPY(Step n)

Where FPY for each step is the first pass yield at that step
```

**Example**:
```
Step 1 FPY: 95%
Step 2 FPY: 97%
Step 3 FPY: 96%
Step 4 FPY: 98%

RTY = 0.95 × 0.97 × 0.96 × 0.98 = 0.882 = 88.2%
```

**Analysis**:
- RTY is always less than individual step FPY
- Multiple steps compound yield loss
- Improvement priority: Lowest FPY steps

### Defect Rate and DPMO

**Defect Rate**:
```
Defect Rate = (Number of Defects / Total Opportunities) × 100%

DPMO = (Number of Defects / Total Opportunities) × 1,000,000
```

**Example**:
```
Total units: 10,000
Defects found: 50
Total opportunities: 50,000 (5 critical dimensions per unit)

Defect Rate = 50 / 50,000 × 100% = 0.1%
DPMO = 50 / 50,000 × 1,000,000 = 1,000 DPMO
```

**Six Sigma Levels**:
- 1 Sigma: 308,537 DPMO (69%)
- 2 Sigma: 66,807 DPMO (95%)
- 3 Sigma: 2,700 DPMO (99.7%)
- 4 Sigma: 63 DPMO (99.99%)
- 5 Sigma: 0.57 DPMO (99.9999%)
- 6 Sigma: 0.002 DPMO (99.99997%)

### Cost of Quality (CoQ)

**Components**:
1. **Prevention Costs**: Training, process design, controls
2. **Appraisal Costs**: Inspection, testing, quality assurance
3. **Internal Failure Costs**: Scrap, rework, downtime
4. **External Failure Costs**: Returns, warranty, recalls

**Formula**:
```
CoQ = Prevention + Appraisal + Internal Failures + External Failures

CoQ as % of Revenue = (Total CoQ / Revenue) × 100%
```

**Example**:
```
Prevention: $100,000
Appraisal: $150,000
Internal Failures: $200,000
External Failures: $50,000
Total CoQ: $500,000

Annual Revenue: $10,000,000
CoQ % = 500,000 / 10,000,000 × 100% = 5%
```

**Industry Benchmarks**:
- World Class: < 2% of revenue
- Excellent: 2-5% of revenue
- Average: 5-15% of revenue
- Poor: > 15% of revenue

## Efficiency and Utilization Metrics

### Equipment Utilization

**Definition**: Percentage of available time equipment is actively producing

**Formula**:
```
Equipment Utilization = (Actual Operating Time / Available Time) × 100%

Where:
Available Time = Total Time - Planned Downtime
```

**Example**:
```
Total time in month: 730 hours
Planned maintenance: 20 hours
Changeovers: 10 hours
Available time: 700 hours

Actual operating time: 560 hours
Utilization = 560 / 700 × 100% = 80%
```

**Benchmarks**:
- Excellent: > 80%
- Good: 70-80%
- Fair: 50-70%
- Poor: < 50%

### Labor Efficiency

**Definition**: Measure of productive output relative to labor input

**Formula**:
```
Labor Efficiency = Standard Hours / Actual Hours × 100%

Standard Hours = Planned hours to complete work
Actual Hours = Time actually spent
```

**Example**:
```
Task should take 8 hours (standard)
Technician takes 6 hours (actual)

Labor Efficiency = 8 / 6 × 100% = 133%
```

**Productivity Metrics**:
```
Output per Labor Hour = Units Produced / Total Labor Hours

Revenue per Labor Hour = Revenue / Total Labor Hours
```

## Cost Metrics

### Cost Per Unit

**Definition**: Total production cost divided by number of units produced

**Formula**:
```
Cost Per Unit = (Fixed Costs + Variable Costs) / Units Produced

Or by component:
Cost Per Unit = Direct Materials + Direct Labor + Manufacturing Overhead
```

**Analysis**:
- Fixed costs decrease with volume
- Variable costs may increase with complexity
- Target: Minimize while maintaining quality

### Cost of Downtime

**Definition**: Revenue or profit lost due to equipment downtime

**Formula**:
```
Cost of Downtime = Production Rate × Selling Price × Downtime Hours

Or profit-based:
Cost of Downtime = Units Lost × Gross Margin per Unit
```

**Example**:
```
Production rate: 100 units/hour
Selling price: $50/unit
Downtime: 8 hours

Cost = 100 × 50 × 8 = $40,000

Or with 40% gross margin:
Cost = 100 × 20 × 8 = $16,000
```

### Manufacturing Cost Breakdown

**Typical Cost Structure**:
- Direct Materials: 40-60%
- Direct Labor: 10-20%
- Manufacturing Overhead: 15-30%
- Administrative/Sales: 10-15%

**Kaizen Costing**:
- Target costing approach
- Achieve cost reduction targets
- Focus on process improvement
- Cross-functional team approach

## Time-Based Metrics

### Cycle Time

**Definition**: Time required to complete one full production cycle from start to finish

**Formula**:
```
Cycle Time = Total Production Time / Number of Units

Or for batch production:
Cycle Time = Setup Time + (Batch Size × Run Time Per Unit)
```

**Components**:
- Setup time (non-value-added)
- Processing time (value-added)
- Transport time (non-value-added)
- Waiting/Queue time (non-value-added)
- Inspection time (non-value-added)

### Lead Time

**Definition**: Time from order receipt to delivery of finished product

**Formula**:
```
Lead Time = Cycle Time + Queue Time + Wait Time

Or simplified:
Lead Time = Design Time + Procurement Time + Manufacturing Time + Delivery Time
```

**Example**:
```
Design and Engineering: 5 days
Procurement: 10 days
Manufacturing: 15 days
Final testing: 2 days
Delivery: 3 days

Total Lead Time: 35 days
```

### Takt Time

**Definition**: Pace of production based on customer demand (German: "takt" = rhythm)

**Formula**:
```
Takt Time = Available Production Time / Customer Demand

Or inverted (rate):
Takt Rate = Customer Demand / Available Production Time
```

**Example**:
```
Available time per shift: 8 hours = 480 minutes
Customer demand: 100 units per day

Takt Time = 480 / 100 = 4.8 minutes per unit
```

**Application**:
- Balance production with demand
- Identify bottlenecks (cycle time > takt time)
- Set production pace
- Optimize workforce scheduling

### Manufacturing Cycle Efficiency (MCE)

**Definition**: Ratio of value-added time to total cycle time

**Formula**:
```
MCE = Value-Added Time / Total Cycle Time × 100%

Where:
Value-Added Time = Processing time only
Total Cycle Time = Setup + Processing + Transport + Wait + Inspection
```

**Example**:
```
Processing time (value-added): 10 minutes
Setup time: 2 minutes
Transport time: 1 minute
Wait time: 5 minutes
Inspection time: 2 minutes

Total Cycle Time: 20 minutes
MCE = 10 / 20 × 100% = 50%
```

**Target Benchmarks**:
- World Class: > 50%
- Excellent: 30-50%
- Good: 15-30%
- Poor: < 15%

**Improvement Opportunities**:
- Reduce setup time (SMED techniques)
- Minimize queue and wait times
- Streamline material handling
- Optimize batch sizes
- Integrate inspection into process

## Supply Chain Metrics

### On-Time Delivery

**Definition**: Percentage of orders delivered by promised date

**Formula**:
```
On-Time Delivery = (Orders Delivered On-Time / Total Orders) × 100%
```

**Example**:
```
Total orders in month: 500
Orders delivered on-time: 475

On-Time Delivery = 475 / 500 × 100% = 95%
```

**Benchmarks**:
- World Class: > 98%
- Excellent: 95-98%
- Good: 90-95%
- Fair: 85-90%
- Poor: < 85%

### Order Fulfillment Cycle Time

**Definition**: Time from order placement to delivery

**Formula**:
```
Fulfillment Time = Order Received Date → Order Shipped Date → Delivery Date
```

**Components**:
- Order processing: 1-2 days
- Production/picking: 3-10 days
- QC/packaging: 1-2 days
- Shipping: 2-7 days

### Inventory Metrics

**Inventory Turnover**:
```
Inventory Turnover = Cost of Goods Sold / Average Inventory Value

Days Inventory Outstanding (DIO) = 365 / Inventory Turnover
```

**Example**:
```
Annual COGS: $5,000,000
Average Inventory: $1,000,000

Turnover = 5,000,000 / 1,000,000 = 5 times/year
DIO = 365 / 5 = 73 days
```

**Stock-Out Rate**:
```
Stock-Out Rate = (Demands Not Met / Total Demands) × 100%
```

## Safety and Environmental Metrics

### Lost Time Injury Frequency (LTIF)

**Definition**: Number of lost-time injuries per 1,000,000 hours worked

**Formula**:
```
LTIF = (Total Lost-Time Injuries / Total Hours Worked) × 1,000,000
```

**Example**:
```
Lost-time injuries: 2
Total hours worked: 200,000

LTIF = (2 / 200,000) × 1,000,000 = 10 per million hours
```

**Benchmarks**:
- World Class: < 1
- Excellent: 1-3
- Good: 3-5
- Fair: 5-10
- Poor: > 10

### Total Recordable Incident Rate (TRIR)

**Definition**: All injuries including lost-time and non-lost-time per 1,000,000 hours

**Formula**:
```
TRIR = (Total Recordable Incidents / Total Hours Worked) × 1,000,000
```

### Energy Efficiency

**Energy Per Unit**:
```
Energy Per Unit = Total Energy Consumed / Units Produced

kWh per unit or BTU per unit
```

**Energy Cost as % of COGS**:
```
Energy Cost % = Energy Costs / Cost of Goods Sold × 100%
```

**Carbon Footprint**:
```
Emissions = Energy Consumed × Emission Factor + Direct Emissions

Tons CO2e per unit or per revenue
```

## Industry Benchmarks

### Automotive Manufacturing

| Metric | Target | World Class |
|--------|--------|------------|
| OEE | > 80% | > 85% |
| MTBF | > 400 hours | > 1000 hours |
| MTTR | < 1 hour | < 0.5 hours |
| FPY | > 98% | > 99% |
| On-time delivery | > 98% | > 99% |
| LTIF | < 5 | < 1 |

### Electronics Manufacturing

| Metric | Target | World Class |
|--------|--------|------------|
| OEE | > 75% | > 85% |
| MTBF | > 300 hours | > 800 hours |
| MTTR | < 2 hours | < 1 hour |
| FPY | > 95% | > 98% |
| CoQ | < 5% | < 2% |
| DPMO | < 500 | < 100 |

### Food and Beverage

| Metric | Target | World Class |
|--------|--------|------------|
| OEE | > 70% | > 80% |
| MTBF | > 200 hours | > 500 hours |
| MTTR | < 3 hours | < 1.5 hours |
| FPY | > 92% | > 97% |
| Equipment Uptime | > 90% | > 95% |

### Pharmaceutical Manufacturing

| Metric | Target | World Class |
|--------|--------|------------|
| OEE | > 75% | > 85% |
| MTBF | > 500 hours | > 1500 hours |
| MTTR | < 1 hour | < 0.5 hours |
| FPY | > 98% | > 99%+ |
| CoQ | < 3% | < 1% |
| Compliance Rate | 100% | 100% |

