# Maintenance Strategies and Frameworks Reference

## Overview

This reference document covers Reliability-Centered Maintenance (RCM), Total Productive Maintenance (TPM), and Predictive Maintenance (PDM) as strategic approaches to equipment management. These frameworks complement ISO 55000 asset management principles and enable optimization of maintenance decisions.

---

## 1. Reliability-Centered Maintenance (RCM)

### 1.1 RCM Definition and Principles

**RCM** is a structured process to determine the optimum maintenance strategy for each equipment/asset by analyzing failure modes and their consequences.

**Core Philosophy:**
- Focus on reliability (preventing failures), not just fixing failures
- Allocate resources based on consequences of failure
- Use data-driven decision-making
- Tailor maintenance strategy to equipment criticality

**Key RCM Questions:**
1. What is the equipment supposed to do? (Functional requirements)
2. How can it fail? (Failure modes)
3. Why does it fail? (Root causes)
4. What are the consequences of failure? (Impact analysis)
5. How can we prevent/mitigate these failures? (Preventive strategy)
6. What do we do if we can't prevent failure? (Reactive strategy)

### 1.2 RCM Process Steps

```
STEP 1: SYSTEM DEFINITION
├─ Equipment scope and boundaries
├─ Functional block diagram
├─ Operating context and environment
├─ Design parameters and limits
└─ Historical failure data review

STEP 2: FUNCTIONAL ANALYSIS
├─ Primary functions (production output)
├─ Secondary functions (safety, environmental, economic)
├─ Required performance levels
├─ Operating modes (normal, startup, shutdown, emergency)
└─ Interactions with other equipment

STEP 3: FAILURE MODES AND EFFECTS ANALYSIS (FMEA)
├─ Identify all credible failure modes
├─ For each failure mode:
│  ├─ Probable causes
│  ├─ Effects on equipment and system
│  ├─ Detectability of failure mode
│  ├─ Severity of consequence
│  └─ Frequency of occurrence
├─ Prioritize by risk (Severity × Frequency)
└─ Identify critical failure modes

STEP 4: CONSEQUENCE EVALUATION
├─ Safety consequences: Risk to personnel
├─ Environmental consequences: Regulatory/legal liability
├─ Operational consequences: Production loss, downtime
├─ Economic consequences: Repair cost, lost revenue
└─ Hidden failures: Failures not immediately obvious to operators

STEP 5: MAINTENANCE TASK SELECTION
├─ For each failure mode, evaluate tactics:
│  ├─ Condition monitoring (detect early degradation)
│  ├─ Preventive overhaul (planned replacement before failure)
│  ├─ Preventive replacement (periodic, before wear-out)
│  ├─ Design modification (eliminate root cause)
│  └─ Run-to-failure (accept failure and repair reactively)
├─ Select best tactic considering:
│  ├─ Cost-benefit analysis
│  ├─ Failure consequences
│  ├─ Failure unpredictability
│  ├─ Maintenance resource availability
│  └─ Risk tolerance
└─ Document decision rationale

STEP 6: IMPLEMENTATION AND OPTIMIZATION
├─ Develop maintenance plan
├─ Set inspection intervals based on RCM analysis
├─ Train maintenance personnel
├─ Establish performance metrics
├─ Monitor and adjust based on results
└─ Continuous improvement
```

### 1.3 RCM Maintenance Task Matrix

**Decision Matrix for Maintenance Strategy Selection:**

| Consequence Severity | High Failure Frequency | Low Failure Frequency |
|---|---|---|
| **Catastrophic (Safety)** | Condition monitoring + redundancy | Condition monitoring + backup |
| **Critical (Major Downtime)** | Condition monitoring + preventive | Condition monitoring |
| **Moderate (Minor Downtime)** | Preventive replacement | Run-to-failure |
| **Minor (In-service repair)** | Run-to-failure | Run-to-failure |

**Key RCM Insight:**

```
The goal is NOT to prevent all failures, but to:
1. Prevent catastrophic failures (safety, major economic impact)
2. Use condition monitoring for critical equipment
3. Allow less critical equipment to run-to-failure
4. Allocate resources to highest-risk items

Traditional maintenance: Same strategy for all equipment
RCM maintenance: Tailored strategy by failure consequence
Result: Lower overall cost + better reliability
```

### 1.4 RCM Implementation Example

**Case: Centrifugal Pump in Process Line**

```
FUNCTIONS:
- Primary: Transfer fluid at 100 GPM, 50 psi
- Secondary: Maintain <5 ppm vibration (equipment health)

FAILURE MODES (Top 5 by criticality):
1. Impeller wear → Reduced flow
   - Consequence: Critical (production shortfall)
   - Frequency: Medium (every 2-3 years)
   - Detectability: Good (performance monitoring)
   - RCM Decision: CONDITION MONITORING (monthly performance curve)

2. Bearing outer race spall → Catastrophic bearing failure
   - Consequence: Catastrophic (unplanned downtime, risk of seal failure)
   - Frequency: Low (if maintained, 5-10 year interval)
   - Detectability: Excellent (vibration, temperature)
   - RCM Decision: CONDITION MONITORING (weekly vibration/temperature)

3. Mechanical seal failure → Leakage, environmental hazard
   - Consequence: Critical (environmental, safety)
   - Frequency: Medium (every 2-4 years)
   - Detectability: Good (visual leakage)
   - RCM Decision: PREVENTIVE REPLACEMENT (planned overhaul 3-year interval)

4. Pipe vibration looseness → Reduced performance, noise
   - Consequence: Minor (in-service correction)
   - Frequency: High (develops gradually)
   - Detectability: Fair (noise, visual inspection)
   - RCM Decision: RUN-TO-FAILURE (re-tighten when discovered)

5. Cavitation → Impeller erosion
   - Consequence: Critical (accelerated impeller wear)
   - Frequency: Medium (depends on NPSH margin)
   - Detectability: Good (acoustic, vibration signature)
   - RCM Decision: DESIGN MODIFICATION (improve inlet conditions)

MAINTENANCE PLAN SUMMARY:
├─ Weekly: Vibration monitoring (bearing health)
├─ Weekly: Discharge pressure trending (impeller wear, cavitation)
├─ Monthly: Temperature check (bearing health confirmation)
├─ Quarterly: Visual inspection for leakage (seal condition)
├─ 3-Year Interval: Mechanical seal replacement (preventive)
├─ 5-Year Interval: Bearing inspection (decide re-use vs. replacement)
└─ As-needed: Cavitation mitigation if detected

RISK REDUCTION:
- Bearing failure rate reduced 80% (condition monitoring prevents surprises)
- Seal degradation managed (no environmental incidents)
- Impeller wear tracked (plan replacement during scheduled downtime)
```

### 1.5 Hidden Failures in RCM

**Definition:** Failures whose effects are not immediately apparent to operators

**Examples:**

```
Backup/Redundancy failures:
- Standby pump fails; primary still running
- Operator unaware until primary fails and backup won't start
- Consequence: Extended downtime requiring emergency repair

Alarm system failures:
- Level sensor stuck (shows OK, tank actually overflowing)
- Pressure gauge broken (shows normal, actual pressure critical)
- Condition: Masked failure; operator unaware

Indicator light failures:
- Equipment temperature OK light fails
- Bearing actually degrading but no warning

RCM Action for hidden failures:
├─ Increase inspection frequency (don't rely on automatic detection)
├─ Implement redundant monitoring (two independent sensors)
├─ Schedule proof-test intervals (test backup systems periodically)
└─ Condition monitoring can reveal developing failure before catastrophic event
```

---

## 2. Total Productive Maintenance (TPM)

### 2.1 TPM Definition and Goals

**TPM** is a proactive maintenance philosophy that empowers all personnel (operators, technicians, engineers) to participate in equipment maintenance and continuous improvement.

**TPM Pillars:**
1. **Autonomous Maintenance**: Operators maintain their own equipment
2. **Planned Maintenance**: Scheduled preventive and predictive maintenance
3. **Maintenance Prevention**: Design reliability into equipment at acquisition
4. **Quality Maintenance**: Prevent quality defects from equipment
5. **Occupational Health and Safety**: Prevent accidents through equipment condition
6. **Focused Improvement**: Eliminate losses (downtime, defects, accidents)
7. **Training and Development**: Build maintenance skills across organization

### 2.2 Eight Losses in Manufacturing (TPM Focus Areas)

```
EQUIPMENT LOSSES:
├─ 1. Equipment Failures (Unplanned downtime)
│   └─ Goal: Reduce to near-zero through predictive maintenance
├─ 2. Setup/Adjustments (Time between production runs)
│   └─ Goal: Reduce changeover time; improve availability
├─ 3. Startup/Slow Cycles (Equipment ramp to full speed)
│   └─ Goal: Ensure full performance from first unit

PERFORMANCE LOSSES:
├─ 4. Idling/Minor Stops (Brief stops, brief running)
│   └─ Goal: Improve reliability; reduce intermittent issues
├─ 5. Speed/Reduced Running (Running slower than capacity)
│   └─ Goal: Ensure equipment runs at rated speed

QUALITY LOSSES:
├─ 6. Defects (Quality issues from equipment variation)
│   └─ Goal: Maintain tight tolerances through predictive maintenance
└─ 7. Rework/Rejects (Product requiring correction)
    └─ Goal: Prevent quality loss through condition control

MANAGEMENT LOSSES:
└─ 8. Yield (Initial units until stable production)
    └─ Goal: Quick startup, stable production immediately
```

**Overall Equipment Effectiveness (OEE):**

```
OEE = Availability × Performance × Quality

Availability = (Scheduled Time - Downtime) / Scheduled Time
Performance = Actual Output / Theoretical Output
Quality = (Output - Defects) / Output

Example:
Availability: 95% (45 min downtime in 16-hour shift)
Performance: 90% (equipment running slower than capacity)
Quality: 98% (2% defect rate)
OEE = 0.95 × 0.90 × 0.98 = 0.839 = 83.9%

TPM Target: OEE > 85% (world class)
Typical manufacturing: OEE 50-70%
```

### 2.3 TPM Implementation Framework

**Operator Autonomous Maintenance (Jisutsu):**

```
LEVEL 1: INITIAL TRAINING
└─ Learn basic equipment operation and safety

LEVEL 2: CLEANING & INSPECTION
├─ Daily cleaning of equipment
├─ Visual inspection for abnormalities
├─ Learn normal vibration, sound, appearance, temperature
├─ Establish baseline "healthy equipment" understanding
└─ Early detection of problems (loose bolts, leakage, corrosion)

LEVEL 3: BASIC SERVICING
├─ Daily oil/coolant level checks
├─ Filter changes and fluid top-ups
├─ Lubrication as per checklist
├─ Greasing of accessible bearings
├─ Tightening of loose fasteners
└─ Record all activities

LEVEL 4: PROBLEM SOLVING
├─ Analyze equipment condition
├─ Identify and report abnormalities
├─ Investigate root causes of failures
├─ Participate in maintenance decisions
├─ Contribute to equipment improvements
└─ Training in root cause analysis (5-Why, Fishbone)

LEVEL 5: CONTINUOUS IMPROVEMENT
├─ Suggest equipment modifications
├─ Optimize maintenance routines
├─ Implement small-scale improvements
├─ Participate in preventive maintenance planning
└─ Share knowledge with other operators
```

**Planned Maintenance Integration:**

```
Operators provide data/observations
             ↓
Maintenance technicians review condition data
             ↓
Plan predictive & preventive maintenance
             ↓
Execute maintenance with operator participation
             ↓
Feedback loop for continuous improvement

Example workflow:
Day 1 - Operator: "Bearing temperature rising, now 75°C (was 65°C)"
  ↓
Day 1 - Technician: Order vibration analysis
  ↓
Day 2 - Analysis: Bearing outer race fault detected (BPFO present)
  ↓
Day 3 - Plan: Schedule bearing replacement in 2 weeks
  ↓
Week 2 - Execute: Replace bearing, dispose old bearing
  ↓
Week 2 - Feedback: Operator confirms temperature back to 65°C
  ↓
Documentation: Updated maintenance interval, failure root cause (corrosion initiated spall)
```

### 2.4 TPM Metrics

```
Primary TPM Metrics:
├─ Overall Equipment Effectiveness (OEE): % of target
├─ Mean Time Between Failures (MTBF): hours/cycles
├─ Mean Time to Repair (MTTR): hours
├─ Equipment Availability: % uptime
├─ Maintenance Cost/Revenue: Cost per unit produced
├─ Unplanned Downtime: % of scheduled time
├─ Maintenance Labor Utilization: % productive time
└─ Maintenance Budget Variance: Actual vs. planned

Secondary Metrics:
├─ Operator Participation Rate: % trained, improvement suggestions/month
├─ Maintenance Incidents: Number of safety events
├─ Quality Defects/Equipment: % related to equipment condition
├─ Cost per Maintenance Hour: Materials + labor cost
└─ Maintenance Backlog: Number of work orders pending
```

---

## 3. Predictive Maintenance (PDM) as Strategy

### 3.1 PDM Framework

**Definition:** Use monitoring data to predict failures and optimize maintenance timing

**Advantages over Fixed-Interval Maintenance:**

```
FIXED-INTERVAL MAINTENANCE:
├─ Service every N hours/months/units
├─ Over-maintenance: Some equipment serviced before needed
├─ Under-maintenance: Some equipment fails before scheduled service
├─ Cost: Unnecessary maintenance on good equipment
├─ Benefit: Predictable cost, simple planning
└─ Best for: Low-cost, high-reliability equipment where failure is rare

PREDICTIVE MAINTENANCE:
├─ Service when condition indicates need
├─ Optimal timing: Just before failure (maximum equipment life)
├─ No wasted service cycles
├─ Cost savings: 20-40% maintenance cost reduction
├─ Benefit: Extended equipment life, reduced downtime
└─ Best for: Critical equipment, expensive repair, high-failure-rate items

COMBINED APPROACH (RECOMMENDED):
├─ PDM for critical equipment (large motors, centrifugal compressors, pumps)
├─ Fixed-interval for non-critical, inexpensive equipment
├─ Fixed-interval for safety-critical systems (backup to PDM)
├─ Transition equipment from fixed to predictive as monitoring deployed
└─ Result: Optimized cost-benefit across asset portfolio
```

### 3.2 PDM Implementation Phases

```
PHASE 1: BASELINE ESTABLISHMENT (Months 1-2)
├─ Data collection from healthy equipment
├─ Establish normal parameter ranges
├─ Document baseline vibration, temperature, pressure
├─ Perform initial oil analysis
├─ Create health indicator baseline
└─ Goal: Know "normal" state for each equipment type

PHASE 2: MONITORING DEPLOYMENT (Months 2-4)
├─ Install sensors on critical equipment
├─ Establish daily/weekly monitoring schedule
├─ Integrate with data collection system
├─ Build data quality checks
├─ Create trend charts and visualization
└─ Goal: Continuous condition visibility

PHASE 3: ALERT & THRESHOLD TUNING (Months 4-6)
├─ Set alert thresholds based on design limits and safety margins
├─ Initial thresholds conservative (higher false positive rate)
├─ Gradually refine based on operational experience
├─ Establish alert escalation procedures
├─ Integrate alerts with maintenance planning system
└─ Goal: Reliable, actionable alerts without alert fatigue

PHASE 4: MODEL DEVELOPMENT (Months 4-8)
├─ Collect failure data for model training
├─ Develop RUL prediction models
├─ Validate models on historical data
├─ Test on current equipment
├─ Integrate models into prediction system
└─ Goal: Accurate RUL predictions for maintenance planning

PHASE 5: OPTIMIZATION (Months 8-12)
├─ Analyze actual maintenance vs. predictions
├─ Refine alert thresholds and RUL models
├─ Reduce false positive rate
├─ Extend equipment life where possible
├─ Scale to additional equipment types
└─ Goal: Optimal maintenance timing across fleet

PHASE 6: CONTINUOUS IMPROVEMENT (Year 2+)
├─ Monthly model performance reviews
├─ Quarterly alert threshold adjustments
├─ Annual retraining with new failure data
├─ Integrate lessons learned
├─ Expand to additional assets
└─ Goal: Steady improvement in reliability and cost
```

### 3.3 PDM Success Factors

```
TECHNICAL:
├─ Adequate sensor coverage (don't miss developing failures)
├─ Data quality (noise-free, correct calibration)
├─ Appropriate analysis methods (domain-specific algorithms)
├─ Robust modeling (generalizes to new equipment, new conditions)
└─ Real-time capability (latency < 1 hour for alerts)

ORGANIZATIONAL:
├─ Clear maintenance decision authority
├─ Regular review and adjustment of thresholds
├─ Feedback loop from maintenance to engineering
├─ Training of maintenance and operations personnel
├─ Cultural shift from reactive to proactive mindset
└─ Executive support and funding commitment

OPERATIONAL:
├─ Maintenance workforce ready (has capacity to perform maintenance)
├─ Spare parts availability (beforehand for critical items)
├─ Production schedule flexibility (perform maintenance when predicted)
├─ Equipment access (can reach sensors and bearings)
└─ Documentation (maintenance procedures up-to-date, clear)

ECONOMIC:
├─ ROI justification (savings exceed implementation cost)
├─ Cost allocation (assign maintenance costs properly)
├─ Capital budget (initial sensor and infrastructure investment)
├─ Operational budget (ongoing monitoring and analysis)
└─ Payback timeline (typical 18-36 months for critical assets)
```

---

## 4. Strategy Comparison Matrix

| Factor | Fixed-Interval | Condition-Based | Predictive |
|--------|---|---|---|
| **Failure Prevention** | Moderate | Good | Excellent |
| **Equipment Life Optimization** | Fair | Good | Excellent |
| **Maintenance Cost** | High (over-maintenance) | Medium | Low-Medium |
| **Downtime Risk** | Medium | Low | Very Low |
| **Implementation Complexity** | Low | Medium | High |
| **Data/Monitoring Required** | None | Periodic | Continuous |
| **Planning Horizon** | Fixed (known in advance) | 1-4 weeks | 1-12 weeks |
| **Best For | Simple, inexpensive equipment | Medium-criticality equipment | Critical, expensive equipment |
| **Scalability** | Excellent | Good | Moderate-Good |

---

## 5. Hybrid Maintenance Strategy (Recommended)

### 5.1 Equipment Classification

```
CLASS A (CRITICAL):
├─ High consequence of failure (safety, major production loss)
├─ High cost of failure (repair, downtime, lost revenue)
├─ Examples: Centrifugal compressors, large motors, critical pumps
├─ Strategy: PREDICTIVE + CONDITION MONITORING + PREVENTIVE BACKUP
├─ Monitoring: Continuous (online or high-frequency)
├─ Sensors: Multiple types (vibration, temperature, pressure, acoustic)
└─ Goal: Prevent unplanned failure; maximize equipment life

CLASS B (IMPORTANT):
├─ Moderate consequence (some production loss, equipment damage)
├─ Medium repair cost
├─ Examples: Secondary pumps, small motors, medium-load bearings
├─ Strategy: CONDITION MONITORING + PREVENTIVE at extended intervals
├─ Monitoring: Weekly/monthly manual or automatic
├─ Sensors: Single primary sensor (vibration or temperature)
└─ Goal: Balance uptime and cost

CLASS C (ROUTINE):
├─ Low consequence (in-service repair, minor downtime)
├─ Low repair cost
├─ Examples: Small fans, small motors, low-criticality bearings
├─ Strategy: FIXED-INTERVAL MAINTENANCE
├─ Monitoring: Visual inspection, operator observation
├─ Maintenance: Simple, quick replacement procedures
└─ Goal: Minimize administrative overhead
```

### 5.2 Portfolio Maintenance Budget Allocation

```
Typical Manufacturing Plant Maintenance Budget Distribution:

CLASS A (Critical): 30% of assets, 60% of budget
└─ PDM with continuous monitoring ($100K+ per asset)
   Cost per asset: High, but justified by high failure cost

CLASS B (Important): 40% of assets, 30% of budget
└─ Condition monitoring, quarterly inspections
   Cost per asset: Moderate

CLASS C (Routine): 30% of assets, 10% of budget
└─ Fixed-interval maintenance
   Cost per asset: Low

Total maintenance budget: Typically 3-8% of plant replacement value

ROI from PDM:
├─ Direct savings: 20-40% reduction in maintenance costs
├─ Indirect savings: 35-45% reduction in unplanned downtime
├─ Quality improvements: 10-15% reduction in equipment-related defects
├─ Safety improvements: 25-30% reduction in equipment-related incidents
└─ Payback period: 18-36 months for critical assets
```

---

## 6. Decision Support Tools

### 6.1 Failure Mode Decision Tree

```
Equipment shows early degradation signals
    ↓
Is failure catastrophic or unsafe?
├─ YES → CONDITION MONITORING (must prevent failure)
│        └─ Alert thresholds: Conservative (high sensitivity)
│
└─ NO → Continue below

Are failures frequent (multiple per year)?
├─ YES → CONDITION MONITORING or PREVENTIVE REPLACEMENT
│        └─ Increase monitoring or shorten interval
│
└─ NO → Continue below

Is equipment failure predictable (gradual degradation)?
├─ YES → CONDITION MONITORING (can predict failures)
│        └─ Vibration, temperature, pressure trending
│
└─ NO → Is failure cost high (>$10K repair + downtime)?
        ├─ YES → FIXED-INTERVAL MAINTENANCE (conservative)
        │        └─ Fixed overhaul interval based on MTBF
        │
        └─ NO → RUN-TO-FAILURE (economically optimal)
               └─ Repair only when broken
```

### 6.2 Monitoring Technology Selection

```
Decision matrix for sensor/monitoring type:

HIGH failure consequence + GRADUAL degradation
→ Vibration monitoring (early detection) + Thermal (backup)
  Examples: Critical pump bearings, large motor bearings

HIGH failure consequence + SUDDEN failures
→ Thermal monitoring + Pressure (backup) + Run-to-failure protocol
  Examples: Electrical motor winding failures, sudden seal failures

MEDIUM failure consequence
→ Simple temperature or vibration (choose based on failure mode)
  Examples: Secondary pump, small fan motor

LOW failure consequence
→ Operator observation or run-to-failure
  Examples: Small fan, low-criticality item
```

---

## References

- Rausand, M. & Høyland, A., "System Reliability Theory"
- Moubray, J., "Reliability-Centered Maintenance" (RCM classic)
- Nakajima, S., "Introduction to TPM"
- ISO 55000: Asset Management standards
- IEC 60300: Dependability management series
- SAE JA1012: RCM standard
