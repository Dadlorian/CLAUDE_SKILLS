# Six Sigma DMAIC Project Guide

## Overview

This guide provides a practical walkthrough of executing Six Sigma projects using the DMAIC methodology (Define-Measure-Analyze-Improve-Control).

---

## Project Selection Framework

### High-Impact Project Criteria

```
Scoring Matrix (1-5 scale, higher is better):

Project Name: Wire Harness Assembly Defects

1. Financial Impact (Score: 5/5)
   Current cost: $2.3M annually (8% returns)
   Potential savings: >$1.8M annually
   ROI if successful: >400%
   → HIGH PRIORITY

2. Problem Severity (Score: 5/5)
   Customer complaints: Multiple major OEMs
   Safety implications: Electrical short risk
   Repeat problem: 6+ months of issues
   → HIGH PRIORITY

3. Data Availability (Score: 4/5)
   Historical quality data: Available
   Production data: Complete
   Customer return data: Available
   → GOOD (sufficient data to work with)

4. Feasibility (Score: 4/5)
   Resource availability: 2 engineers available
   Timeline: 6 months realistic
   Technical complexity: Moderate
   → ACHIEVABLE

5. Organizational Support (Score: 5/5)
   Executive sponsorship: CEO committed
   Management backing: VP Production supportive
   Budget approval: $150k authorized
   → STRONG SUPPORT

Overall Score: 4.6/5 → Select this project
Expected timeline: 6 months
Expected team: 4-6 people
Expected savings: $1.8M annually
```

### Project Charter Template

```
PROJECT CHARTER: Reduce Wire Harness Assembly Defects

Date: January 15, 2024
Project Sponsor: VP Manufacturing
Project Lead: Process Engineer (John Smith)

BUSINESS CASE
Problem Statement:
Wire harness assembly produces 45,000 DPMO (4.5 sigma level)
with 8% customer returns, representing $2.3M annual cost.
Root causes are: crimper wear, material variation, temperature
control, and operator training gaps.

Project Goal:
Reduce DPMO from 45,000 to <3,400 (6 sigma level)
Achieve <0.3% customer returns
Save $1.8M annually

SCOPE
In Scope:
✓ All wire harness assembly operations (3 production lines)
✓ Crimp quality, wire striping, connector insertion
✓ Material and supplier quality

Out of Scope:
✗ Connector design (separate project)
✗ Raw wire manufacturing
✗ Packaging and logistics

TIMELINE
Phase 1 (Define): Jan 15 - Feb 15 (1 month)
Phase 2 (Measure): Feb 15 - Mar 31 (1.5 months)
Phase 3 (Analyze): Apr 1 - May 15 (1.5 months)
Phase 4 (Improve): May 15 - Jul 1 (1.5 months)
Phase 5 (Control): Jul 1 - Aug 31 (2 months)
Total: 8 months

TEAM
Project Lead: Process Engineer (John Smith)
Quality Lead: Quality Manager (Maria Garcia)
Operator Representative: Assembly Supervisor (Tom Wilson)
Data Analyst: Quality Analyst (Sarah Johnson)
Part-time: Maintenance Technician (Bob Davis)

BUDGET
Personnel: $80,000 (800 hours @ $100/hour)
Equipment/tools: $20,000
Consulting/training: $25,000
Travel: $5,000
Total: $130,000

SUCCESS METRICS
Financial: Save $1.8M annually
Quality: Reduce returns 8% → <0.3%
Process: Achieve 6 sigma (Cpk >1.67)
Customer: Achieve 99%+ satisfaction
Time: Complete within 8 months and $130k budget

Approvals:
Executive Sponsor: [Signature] _____________
Project Lead: [Signature] _________________
Finance Manager: [Signature] _______________
Date: January 15, 2024
```

---

## Phase 1: Define (Weeks 1-4)

### Define 1.1: Customer Requirements (VOC)

**Voice of Customer (VOC) Analysis:**

```
Customer Interview Summary:

Customer: Major Automotive OEM
Quality Manager: Discussed wire harness defects

Key Requirements:
1. "Defect rate < 1 per 1,000 parts (0.1%)"
   → Target DPMO: <1,000 (6.4 sigma)

2. "Consistent quality lot-to-lot"
   → Target Cpk: >1.67

3. "Fast response to any issues"
   → Response time: <4 hours for problems

4. "Complete traceability of all parts"
   → Documentation: Serial number + heat lot

5. "Reasonable price increases"
   → Cost target: No more than 3% price increase

6. "Delivery reliability >98%"
   → On-time delivery: 98%+

Data from Customer Returns Analysis:
- Quantity per month: 200-300 defective harnesses
- Defect types: Crimp failures (44%), wire issues (24%), solder (8%), other (24%)
- Return cost: $2,300 per incident (investigation + rework)
- Warranty claims: $1.5M annually

Translated to CTQ (Critical to Quality):
1. Crimp height: 3.5 ±0.3 mm (Currently: 3.6 ±0.4 mm)
2. Wire strip length: 6.0 ±0.5 mm (Currently: 6.1 ±0.6 mm)
3. Connector seating: Fully inserted (Currently: 5% not fully seated)
4. Solder joint quality: No cold joints (Currently: 0.8% cold joints)
5. Wire tensile: >45 N break force (Currently: 94% compliance)
```

### Define 1.2: Process Mapping

**Current State Process Flow:**

```
WIRE HARNESS ASSEMBLY PROCESS (Current State)

1. Material Prep (Wire Striping)
   ├─ Wire from supplier (Supplier A or B)
   │  └─ Supplier A: Higher strip failure rate (2.3%)
   │  └─ Supplier B: Lower strip failure rate (0.4%)
   ├─ Automatic wire stripper
   │  └─ Strip length: 6.0-6.5 mm (targeting 6.0 ±0.5)
   │  └─ Defect rate: 1.2% (stripped too long/short)
   └─ Output: Stripped wires ready for crimping

2. Crimping Station
   ├─ Crimper tool (Manual crimper)
   │  └─ Crimper A & B: Newer (wear < 5,000 cycles)
   │  └─ Crimper C & D: Older (wear > 15,000 cycles) → Higher failures
   │  └─ Defect rate from old crimpers: 4.5% vs. new: 1.8%
   ├─ Wire + Terminal + Connector
   │  └─ Target crimp height: 3.5 ±0.3 mm
   │  └─ Actual: 3.6 ±0.4 mm (off-center)
   └─ Output: Crimped wire-terminal assembly

3. Connector Assembly
   ├─ Insert crimped terminals into connector housing
   │  └─ Connector seating: Manual press (operator feel)
   │  └─ Defect: 0.6% not fully seated (not detected)
   ├─ Assembly verification: None (no confirmation)
   │  └─ Depends on operator visual inspection only
   └─ Output: Completed connector assembly

4. Final Inspection
   ├─ Visual inspection (50% sample)
   │  └─ Inspector samples 1 of 2 harnesses
   │  └─ Only visible defects detected (crimps OK, solder OK)
   │  └─ Inspector relies on experience (inconsistent)
   ├─ Functionality test: None (100% escape risk)
   └─ Output: Shipped harnesses

5. Packaging & Shipping
   └─ Boxes of 100 harnesses shipped to customer

6. Customer Use
   ├─ Installation in vehicle assembly
   └─ Failures detected: Cold solder, weak crimps
       └─ Root cause: Not detected in our inspection
```

**Issues Identified:**

```
1. Supplier Quality Variation
   Root Cause: Supplier A higher defect rate
   Impact: 2.3% - 0.4% = 1.9% of failures attributable
   Action: Shift to Supplier B

2. Crimper Wear
   Root Cause: Crimpers C & D not changed on schedule
   Impact: 4.5% - 1.8% = 2.7% extra defects from worn crimpers
   Action: Preventive crimper replacement every 8,000 cycles

3. Process Centering
   Root Cause: Crimp height average 3.6 mm (target 3.5)
   Impact: Offset reduces capability (Cpk from 1.33 → 1.05)
   Action: Calibrate crimpers; adjust stroke

4. Lack of In-Process Verification
   Root Cause: No confirmation of connector seating
   Impact: 0.6% of crimps not fully seated; not detected
   Action: Add visual or mechanical verification step

5. Inadequate Final Inspection
   Root Cause: Only 50% inspection; no functional test
   Impact: 5% of defects escape to customer
   Action: 100% inspection; add functional test
```

### Define 1.3: Critical to Quality (CTQ) Flowdown

```
Customer Requirement → CTQ → Measurement → Spec

1. Low defect rate
   └─ DPMO <1,000
       └─ Crimp height accuracy
           └─ Crimp height: 3.5 ±0.3 mm
               └─ Measure: Micrometer on sample

2. Consistent quality
   └─ Cpk >1.67
       └─ Process variation
           └─ Wire strip length: 6.0 ±0.5 mm
               └─ Measure: Caliper or gage

3. Fast response
   └─ Problem detection <4 hours
       └─ Early defect detection
           └─ SPC monitoring every 30 min
               └─ First piece inspection after setup

4. Complete traceability
   └─ Serial number on each harness
       └─ Material batch tracking
           └─ Wire lot + Connector lot documented
               └─ Data recording in production system

CTQ Summary (What We Must Control):
1. Wire striping length (Supplier & equipment)
2. Crimp height (Crimper calibration & wear)
3. Connector seating (Assembly verification)
4. Solder joint quality (Wave solder temperature control)
5. Wire break resistance (Material property)
```

---

## Phase 2: Measure (Weeks 5-8)

### Measure 2.1: Data Collection Plan

**Baseline Defect Data:**

```
Baseline Defect Rate Analysis (Current Month)

Total Units Produced: 50,000
Total Defects Found: 3,135

Defect Summary by Type:
1. Crimp height failures: 1,378 (44.0%)
   - Height <3.2 mm: 456 parts
   - Height >3.8 mm: 922 parts
   - Conclusion: Process off-center (too high)

2. Wire strip failures: 750 (23.9%)
   - Stripped too short: 180 parts
   - Stripped too long: 570 parts
   - Conclusion: Supplier and equipment issues

3. Solder defects: 268 (8.5%)
   - Cold joints: 201 parts
   - Bridges: 67 parts
   - Conclusion: Solder temperature control needed

4. Connector defects: 189 (6.0%)
   - Not fully seated: 165 parts
   - Cracked housings: 24 parts
   - Conclusion: Assembly verification missing

5. Wire break/other: 550 (17.5%)
   - Wire breaks during test: 312 parts
   - Missing component: 238 parts
   - Conclusion: Material quality + assembly verification

DPMO Calculation:
Total Defects: 3,135
Total Opportunities: 50,000 parts × 5 critical characteristics = 250,000
DPMO = (3,135 / 250,000) × 1,000,000 = 12,540 DPMO
Sigma level: 4.87 sigma (vs. 6 sigma target)

Cost Impact:
- Rework cost: $2.3M annually (8% of annual cost)
- Loss of business risk: Potential customer loss
- Warranty claims: $1.5M annually
- Total: $3.8M+ annually
```

### Measure 2.2: Measurement System Validation

```
Gage R&R Study Results:

Characteristic: Crimp Height

Study Design:
- 10 harnesses representing range of heights
- 3 operators (Exp A, B, C)
- 3 measurements each
- Tool: Calibrated micrometer (±0.01 mm)

Results:
Repeatability (Same operator, multiple measurements):
- Operator A: ±0.01 mm
- Operator B: ±0.02 mm
- Operator C: ±0.01 mm
Average repeatability: ±0.013 mm

Reproducibility (Different operators):
- Range of average measurements: ±0.05 mm
- Operator A tends to read 0.02 mm lower
- Operator B tends to read 0.03 mm higher
- Conclusion: Technique variation exists

Total GR&R:
GR&R = √(Repeatability² + Reproducibility²)
     = √(0.013² + 0.05²)
     = √(0.000169 + 0.0025)
     = √0.002669
     = 0.0517 mm

GR&R as % of Tolerance:
Tolerance: ±0.3 mm (0.6 mm range)
GR&R % = (0.0517 / 0.6) × 100 = 8.6%

Status: ACCEPTABLE (<10%)

Actions to Improve Measurement:
1. Standardized measurement technique training
2. Ensure micrometer spindle zero'd before use
3. Apply consistent pressure (not too tight)
4. Use calibrated test blocks weekly
5. Document technique in work instruction
```

### Measure 2.3: Current Process Capability

```
Capability Study (100 samples across 3 production lines)

Crimp Height Data:
X-bar (average): 3.62 mm
σ (standard deviation): 0.38 mm
Specification: 3.5 ±0.3 mm (LSL=3.2, USL=3.8)

Capability Indices:

Cp = (USL - LSL) / (6σ)
   = (3.8 - 3.2) / (6 × 0.38)
   = 0.6 / 2.28
   = 0.263 → INCAPABLE

Cpk = Min[(USL - X-bar)/(3σ), (X-bar - LSL)/(3σ)]
    = Min[(3.8 - 3.62)/(3×0.38), (3.62 - 3.2)/(3×0.38)]
    = Min[0.158, 0.368]
    = 0.158 → SEVERELY INCAPABLE

Interpretation:
- Process is 3.5 sigma level (not meeting minimum)
- Major off-centering: Mean 3.62 vs target 3.5
- Very high variation (0.38 mm vs ideal 0.10 mm)
- Current reject rate: 44% (due to crimp issues alone)

Comparison: Defect vs. Specification

        LSL=3.2        Target=3.5        USL=3.8
         |              |                 |
    [====X====]=========●═════════════=[====X====]
      Defects <3.2     Process Mean    Defects >3.8
      (10%)            (3.62 mm)       (34%)
                       PROBLEM: Off-center + too wide!

Target for Success:
- Cpk >1.67 (6 sigma)
- σ < 0.10 mm (tight control)
- Mean = 3.50 mm (perfectly centered)
- Reject rate: < 0.3%

Required Improvement:
- Reduce standard deviation: 0.38 → 0.10 (74% reduction)
- Shift mean: 3.62 → 3.50 mm (offset correction)
```

---

## Phase 3: Analyze (Weeks 9-13)

### Analyze 3.1: Root Cause Analysis

**Fishbone Diagram (Cause & Effect):**

```
                            CRIMP HEIGHT FAILURES

        Man                 Methods              Materials
        ├─ Inconsistent      ├─ No calibration    ├─ Wire variability
        │  technique          │  schedule          │  (Supplier A vs B)
        │                     ├─ Incorrect stroke  └─ Terminal size variation
        ├─ Training gaps      │  setting
        │ (new operators)     └─ Setup procedure   Machines
        │                        missing           ├─ Crimper A & B: New
        └─ Fatigue/attention                       │  (Cpk = 1.8)
           issues                                  ├─ Crimper C & D: Worn
                                                  │  (Cpk = 0.8)
                      Process Mean: 3.62 mm        ├─ Excessive wear
                      (Target: 3.5 mm)             │  at 10,000 cycles
                      Variation: σ = 0.38 mm       └─ No preventive
                                                      replacement schedule

        Environment
        ├─ Temperature fluctuation (70-78°F)
        │  affecting die expansion
        └─ No coolant or lubrication
           causing friction/wear

Major Causes (Pareto):
1. Crimper Wear (40% of variation)
   - Old crimpers (C, D) not changed on schedule
   - Wear causes stroke shortening, crimp height reduction

2. Tool Offset (25% of variation)
   - Crimper dies not calibrated correctly
   - Offset setting drifts during shift

3. Supplier Wire Variation (20% of variation)
   - Supplier A delivers higher wire diameter variability
   - This affects how wire compresses in crimp

4. Operator Technique (10% of variation)
   - New operators not trained properly
   - Inconsistent pressure application

5. Other (5%)
   - Temperature effects, material storage
```

### Analyze 3.2: Statistical Confirmation

**Hypothesis Testing:**

```
Test 1: Supplier Effect on Crimp Quality

Hypothesis:
H0: Supplier A and B produce equal crimp quality
H1: Suppliers differ (Supplier A worse)

Data Collection:
- Sample 50 harnesses made with Supplier A wire
- Sample 50 harnesses made with Supplier B wire
- Measure crimp height, calculate defect rate

Results:
Supplier A: 2,340 mm average, 12.5% defect rate
Supplier B: 2,320 mm average, 5.2% defect rate
Difference: 7.3% reduction in defect rate

Statistical Test (t-test):
t-statistic: 3.24
p-value: 0.002 (< 0.05)
Conclusion: REJECT H0 → Suppliers significantly different
            Supplier B is statistically better

Action: Qualify Supplier B as primary source


Test 2: Crimper Wear Effect

Hypothesis:
H0: Crimper age (wear) does not affect quality
H1: Worn crimpers produce more defects

Data Collection:
- Track defect rate by crimper:
  Crimper A (new, 1,000 cycles): 1.8% defect
  Crimper B (new, 2,500 cycles): 2.1% defect
  Crimper C (worn, 12,000 cycles): 5.3% defect
  Crimper D (worn, 15,000 cycles): 6.2% defect

Analysis:
Defect rate increases 3x from new to worn crimpers
Correlation between cycles and defect: r = 0.94 (strong)

Conclusion: Worn crimpers MAJOR contributor to defects
Action: Replace crimpers at 8,000-cycle mark


Test 3: Temperature Effect on Process

Hypothesis:
H0: Temperature does not affect crimp quality
H1: Temperature changes affect height

Data Collection:
- Track temperature and crimp height hourly
- Morning (70°F): Mean 3.54 mm
- Afternoon (75°F): Mean 3.58 mm
- Evening (72°F): Mean 3.56 mm

Analysis:
Linear regression: For every 1°F, height changes 0.02 mm
Temperature swing (70-78°F) = 0.16 mm height change
This accounts for 5-10% of total variation

Action: Install climate control (22±2°C target)
```

---

## Phase 4: Improve (Weeks 14-20)

### Improve 4.1: Solution Development

**Improvement Ideas Matrix:**

```
Improvement #1: Supplier Quality Switch
Current: 70% Supplier A, 30% Supplier B
Target: 100% Supplier B (if cost acceptable)
Benefit: Reduce wire-related defects 1.9%
Cost: +$0.02/harness ($1,000/month increase)
ROI: Pays back in 2 months from defect reduction
Timeline: 2 weeks to qualify and switch
Risk: Low (already qualified, better performer)
Decision: PROCEED ✓

Improvement #2: Crimper Maintenance Schedule
Current: No schedule (crimpers changed randomly at 10,000+ cycles)
Target: Mandatory change at 8,000 cycles
Action Plan:
  a) Install cycle counter on all crimpers
  b) Create replacement schedule
  c) Keep spare crimpers in stock
  d) Document each replacement in log
Benefit: Reduce wear-related defects 2.7%
Cost: $3,000 for spare crimpers, 2 hours/month labor
ROI: Pays back in 1 month
Timeline: 1 week to implement
Risk: Low (simple procedural change)
Decision: PROCEED ✓

Improvement #3: Crimper Calibration
Current: Occasional, no schedule
Target: Daily zero check; weekly full calibration
Action Plan:
  a) Create calibration procedure (micrometer standard)
  b) Train all operators on calibration
  c) Schedule: First thing each shift
  d) Record in production log
Benefit: Reduce offset drift; improve centering by 50%
Cost: 15 min/day labor = $100/month
ROI: Pays back in <1 month
Timeline: 1 week
Risk: Low (process improvement)
Decision: PROCEED ✓

Improvement #4: Operator Training
Current: 4-hour orientation for new operators
Target: 16-hour structured training + certification
Content:
  - Crimper operation and maintenance (4 hours)
  - Quality standards and inspection (4 hours)
  - Hands-on practice (6 hours)
  - Competency assessment (2 hours)
Benefit: Reduce operator error variation 60%
Cost: $80 per operator × 4 new hires/year = $320
ROI: Immediate (prevents errors)
Timeline: 2 weeks to develop training
Risk: Low (improves skills)
Decision: PROCEED ✓

Improvement #5: 100% Connector Seating Inspection
Current: 50% inspection; no connector seating verification
Target: 100% inspection with mechanical confirmation
Action Plan:
  a) Add go-nogo connector depth gage
  b) Operator inserts each connector
  c) Gage confirms full seating
  d) Any non-compliant → reject, rework
Benefit: Eliminate 0.6% connector seating defects
Cost: $2,000 for gage, 10 sec/harness labor
ROI: Pays back in 3 weeks
Timeline: 1 week setup
Risk: Low (simple mechanical check)
Decision: PROCEED ✓

Improvement #6: Temperature Control
Current: Ambient (70-78°F variation)
Target: Climate control (22±2°C)
Action Plan:
  a) Zone cooling/heating in assembly area
  b) Temperature monitor with alarm
  c) Maintenance: Filter change monthly
Benefit: Reduce thermal variation 5%
Cost: $8,000 HVAC equipment + $100/month maintenance
ROI: Pays back in 13 months
Timeline: 1 month installation
Risk: Medium (capital investment)
Decision: PROCEED ✓ (longer ROI acceptable for stability)
```

### Improve 4.2: Pilot Trial Implementation

```
IMPROVEMENT PILOT TRIAL (1 Week, Line 1 Only)

Timeline: May 15-22, 2024

Changes Implemented:
✓ Switch to 100% Supplier B wire
✓ Install crimper cycle counters
✓ Daily calibration checks (new procedure)
✓ Operator training (pre-trial 4-hour session)
✓ Add connector seating gage
✓ Temporary HVAC upgrade to assembly area

Baseline (Week of May 8):
- 1,000 harnesses produced
- Defects: 135 (13.5%)
- Cpk: 0.42

Pilot Results (Week of May 15):
- 1,050 harnesses produced
- Defects: 25 (2.4%) ← 82% reduction!
- Cpk: 1.08 ← Improved but not yet 6 sigma

Defect Analysis:
Crimp height failures: 1,378 → 80 (94% reduction) ✓
Wire strip failures: 750 → 12 (98% reduction) ✓
Connector seating: 189 → 2 (99% reduction) ✓
Solder defects: 268 → 5 (98% reduction) ✓
(Solder temp still needs work)

Issues Found:
1. Solder temperature still drifting
   Solution: Need better temperature controller
2. Some operators still not following procedure
   Solution: Additional supervisor oversight during implementation

Statistics:
- Cpk improved: 0.42 → 1.08 (157% improvement)
- Defect rate: 13.5% → 2.4% (82% improvement)
- Cost impact: $28,000 savings in pilot week
- Annualized: $1.4M+ in improvements
- Payback on improvements: 4 weeks

Decision: FULL IMPLEMENTATION
```

### Improve 4.3: Full Implementation Plan

```
FULL PRODUCTION IMPLEMENTATION (June 1 - June 30)

Week 1 (Jun 1-7): Supplier Transition
- Complete qualification of Supplier B
- Send notice to Supplier A (phase out)
- Build inventory of Supplier B wire
- Update material procedures

Week 2 (Jun 8-14): Equipment Upgrades
- Install cycle counters on all 4 crimpers
- Procure spare crimpers
- Set up daily calibration procedure
- Train all operators on new procedures

Week 3 (Jun 15-21): Operational Changes
- 100% transition to Supplier B wire
- Daily calibration active on all lines
- Connector seating gage in use
- Monitor SPC charts closely
- Capture any issues

Week 4 (Jun 22-30): Validation & Stabilization
- Collect 100+ samples for capability study
- Verify Cpk > 1.33 (target 1.67)
- Document all procedures
- Train second shift fully
- Prepare for night shift implementation

Staffing:
- Project lead: Full-time oversight
- Quality: Daily audits of procedures
- Maintenance: Support equipment changes
- Supervisors: Reinforce new procedures daily

Expected Results (End of June):
- DPMO: 45,000 → <5,000 (89% reduction)
- Cpk: 0.42 → 1.50+ (350% improvement)
- Defect rate: 13.5% → <0.5%
- Customer returns: 8% → <1%
- Annual cost savings: $1.8M+ (exceeds goal)
```

---

## Phase 5: Control (Weeks 21-26)

### Control 5.1: Sustaining Improvements

```
CONTROL PLAN for Wire Harness Assembly

1. Daily Process Control
   X-bar/R Chart:
   - Collect 5 consecutive harnesses every 2 hours
   - Measure crimp height (micrometer)
   - Plot on control chart
   - Target: All points between 3.2-3.8 mm
   - Out of control action: Stop, investigate, correct

   Visual Inspection:
   - 100% inspection of all connectors
   - Verify: Seating, no solder bridges, no cold joints
   - Go-nogo gage for connector seating
   - Reject any non-conforming units

   Documentation:
   - Production log: Shift, operator, wire lot, connector lot
   - Defect log: Any failures documented with cause
   - SPC chart: Posted at workstation, signed daily

2. Maintenance Schedule (Sustain Equipment)
   Daily:
   - Visual inspection of crimpers for damage
   - Clean out any wire debris
   - Check cycle counter readings

   Weekly:
   - Full crimper calibration (micrometer check)
   - Test cycle on all crimpers
   - Verify gage marks and calibration blocks

   Every 8,000 Cycles:
   - Mandatory crimper replacement
   - Install new dies/anvils
   - Document in equipment log
   - Validate performance on first harness

   Monthly:
   - Solder pot temperature calibration
   - Coolant concentration check
   - Equipment performance audit
   - Document on maintenance form

3. Operator Discipline (Sustain Training)
   Initial (One-time):
   - 16-hour structured training program
   - Competency certification
   - Sign-off on procedures

   Ongoing (Continuous):
   - Daily: Supervisor review of quality metrics
   - Weekly: Brief 15-minute refresher meeting
   - Monthly: Performance feedback (defects per operator)
   - Quarterly: Full gage R&R test to ensure skill level
   - Annually: Recertification training
   - Special: Retraining if defect rate increases

4. Supplier Quality Control
   Supplier B (primary):
   - Monthly: Review incoming inspection data
   - Quarterly: Joint quality meeting
   - Semi-annually: Supplier audit
   - Annually: Performance scorecard review

   Quality Agreement:
   - Wire diameter tolerance: ±0.02 mm
   - Defect rate < 0.2% (6 sigma)
   - Monthly certification of testing
   - Any issues: 4-hour response time

5. Data & Metrics Tracking
   Daily Report:
   - Units produced: ___ / 500 target
   - Defects found: ___ (%) / <0.5% target
   - Cpk: ___ / >1.33 target
   - Downtime: ___ min (reason: ___)
   - OEE: ___ % / >85% target

   Weekly Review:
   - Production meeting: Manager reviews daily data
   - Trends: Any issues emerging?
   - Performance vs. target
   - Corrective actions if needed

   Monthly Analysis:
   - Capability study: Verify Cpk maintained
   - Trend analysis: Is performance stable?
   - Improvement ideas: Any suggestions?
   - Cost tracking: Savings achievement

   Quarterly Business Review:
   - Executive summary: Performance vs. goals
   - Financial impact: Cost savings realized
   - Customer feedback: Any issues reported?
   - Opportunities: Next improvement initiatives
```

### Control 5.2: Error-Proofing (Poka-yoke)

```
Prevent Reoccurrence of Defects:

1. Supplier Lock-in (Prevent Wrong Wire)
   Current: Operators can mix suppliers
   New:
   - Separate storage bins labeled Supplier A and B
   - Remove Supplier A from production floor
   - Color-coded wire (Blue = Supplier B only)
   - One-way valve on supplier dispenser
   Prevention: 100% (Cannot accidentally use wrong supplier)

2. Crimper Cycle Counter Mandatory Stop
   Current: Operators may forget to change crimpers
   New:
   - Electronic cycle counter that halts crimper at 8,000
   - Cannot resume until replaced
   - Replacement documented with time/date
   Prevention: 100% (Crimper automatically stops at wear point)

3. Connector Seating Verification
   Current: Operator presses connector; relies on feel
   New:
   - Go-nogo depth gage (mechanical)
   - Connector must fit in "GO" opening
   - If too shallow → Gage blocks it → Cannot pass
   - Any improper seating detected immediately
   Prevention: 99% (Mechanical block prevents error)

4. Operator Certification Badge
   Current: Anyone can operate crimper
   New:
   - Each operator has ID badge with certification
   - Crimper locked to certified operators only
   - Badge expires annually (requires recertification)
   Prevention: Ensures only trained staff operate equipment

5. Wire Lot Traceability
   Current: Wire supplier may be mixed
   New:
   - Each harness gets label with:
     * Wire supplier lot number
     * Wire date code
     * Connector lot number
     * Operator ID
     * Timestamp
   Prevention: Complete traceability if issues occur
               Can identify and recall specific lots
```

### Control 5.3: Continuous Monitoring

```
MONTHLY SPC SUMMARY REPORT

Month: September 2024 (3 months after improvements)

PROJECT RESULTS:

Baseline (Before Improvements):
- DPMO: 45,000 (4.5 sigma)
- Cpk: 0.42 (incapable)
- Defect rate: 13.5%
- Customer returns: 8%
- Annual cost: $2.3M

Current (Month 3):
- DPMO: 1,850 (5.8 sigma)
- Cpk: 1.58 (acceptable, approaching 6 sigma)
- Defect rate: 0.37%
- Customer returns: 0.08% (98% improvement!)
- Annual cost: $0.5M

Performance vs. Goals:
Goal: DPMO <3,400 (6 sigma)
Actual: 1,850 → ✓ EXCEEDED (90% better than target)

Goal: Cpk >1.33
Actual: 1.58 → ✓ EXCEEDED

Goal: Reduce returns from 8% to <0.3%
Actual: 0.08% → ✓ EXCEEDED

Goal: Save $1.8M annually
Actual: Savings projected $1.8M+ → ✓ ON TARGET

Variation by Defect Type (Month 3):
- Crimp height: 1,378 → 28 (98% reduction)
- Wire striping: 750 → 8 (99% reduction)
- Connector seating: 189 → 1 (99% reduction)
- Solder defects: 268 → 12 (95% reduction)
- Wire strength: 550 → 136 (75% reduction - still needs work)

Process Stability:
- X-bar/R chart: All points in control (stable)
- No trends or patterns detected
- Cpk stable 1.55-1.62 over past 6 weeks
- Conclusion: Process STABLE and CAPABLE

Remaining Issues:
1. Wire strength: 5 breaks per 10,000 parts
   Root cause: Material specification at low end
   Action: Supplier discussion to improve material strength
   Target: Reduce to <2 breaks per 10,000 parts

2. Solder temperature: Still occasional drifts
   Root cause: Temperature controller aging
   Action: Replace controller with newer model ($3,500)
   Target: Reduce solder defects <0.2%

Costs and Savings:
Improvement Costs:
- Supplier B wire premium: $12,000
- Crimper replacements & spares: $8,000
- Gage and tooling: $5,000
- Training program: $2,500
- HVAC equipment: $8,000
- Total Investment: $35,500

Annualized Savings:
- Reduced scrap: $1,400,000
- Reduced rework: $280,000
- Reduced warranty: $130,000
- Reduced downtime: $20,000
- Total Savings: $1,830,000

ROI: $1,830,000 / $35,500 = 51.5x ROI (516% annually!)
Payback Period: <1 month

Lessons Learned:
1. Supplier quality has major impact (40% of improvement)
2. Equipment wear is critical; preventive maintenance essential
3. Operator training crucial; discipline required
4. Measurement system must be validated first
5. Quick wins (Supplier B switch) help maintain momentum
6. Data-driven decisions enable targeting root causes

Recommendations:
1. Apply lessons to other assembly processes
2. Document procedures for standardization
3. Expand SPC to secondary operations
4. Plan for next improvement initiative
5. Share success story with other plants

Next Phase: Maintain control; plan for expansion to other products
```

---

## DMAIC Quick Reference

| Phase | Key Activities | Duration | Deliverables |
|-------|---|---|---|
| **Define** | Charter, VOC, CTQ, process mapping | 4 weeks | Project charter, CTQ flowdown, process maps |
| **Measure** | Data plan, Gage R&R, baseline capability | 4 weeks | Gage R&R study, baseline Cpk, data collection plan |
| **Analyze** | Root cause analysis, hypothesis testing | 5 weeks | Fishbone diagrams, statistical tests, validated causes |
| **Improve** | Solution development, pilot trial, implementation | 7 weeks | Improvement solutions, pilot results, full rollout plan |
| **Control** | Control plans, error-proofing, sustain | 6 weeks | Control plans, SPC charts, training, monitoring system |
| **Total** | Complete DMAIC cycle | **26 weeks** | Documented process improvements & sustained results |

---

## References

- Pyzdek, T., & Keller, P. A. (2018). The Handbook of Six Sigma
- Pande, P. S., Neuman, R. P., & Cavanagh, R. R. (2000). The Six Sigma Way
- George, M. L. (2002). Lean Six Sigma: Combining Six Sigma Quality with Lean Speed
- AIAG. Six Sigma Methodology and Tools
