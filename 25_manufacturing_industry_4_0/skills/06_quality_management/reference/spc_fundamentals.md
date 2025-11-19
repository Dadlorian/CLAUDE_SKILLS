# SPC Fundamentals Reference

## Overview

Statistical Process Control (SPC) is a scientific method for controlling manufacturing processes through statistical analysis and real-time monitoring using control charts.

---

## Key Concepts

### Variation in Manufacturing

All manufacturing processes produce variation. SPC distinguishes between two types:

#### 1. Common Cause Variation
- **Definition**: Inherent, random variation due to normal process factors
- **Characteristics**: Predictable, stable over time, cannot be eliminated
- **Examples**: Normal material property range, environmental fluctuation, machine tolerance
- **Action**: Not adjusted; process is in statistical control

#### 2. Special Cause Variation
- **Definition**: Non-random variation due to assignable causes
- **Characteristics**: Unpredictable, identifies specific problem
- **Examples**: Worn tool, incorrect setup, damaged equipment, operator error
- **Action**: Immediately investigate and correct

### Statistical Process Control Philosophy

**Key Principle**: Statistical signals when special cause variation exists

```
Process Output Distribution:

Common Cause Variation (In Control):
     ┌─────────────────┐
     │       Normal    │
     │    Distribution │
     │    (Predictable)│
     │       ↓         │
LSL  ├─────────────────┤  USL
     └─────────────────┘

     Decision: Process OK, monitor only

Special Cause Variation (Out of Control):
     ┌─────────────────┐     ┌─────────┐
     │      Shifted    │     │  Outlier│
     │   Distribution  │     │  Points │
     │                 │     │    ↓    │
LSL  ├─────────────────┤     └─────────┘  USL
     └─────────────────┘

     Decision: STOP, find and fix cause
```

---

## Control Chart Types Reference

### Variables Data Charts (Continuous Measurements)

#### X-bar and R Chart

**When to Use**: Monitoring process mean and variation simultaneously

**Data Requirements**:
- Rational subgroups: 4-5 measurements per sample
- Sample frequency: Regular intervals
- Continuous data (measurements, not counts)

**Formulas**:

```
X-bar-bar = Σ(Sample means) / Number of samples
R-bar = Σ(Sample ranges) / Number of samples

UCL_X = X-bar-bar + A2 × R-bar
CL_X = X-bar-bar
LCL_X = X-bar-bar - A2 × R-bar

UCL_R = D4 × R-bar
CL_R = R-bar
LCL_R = D3 × R-bar
```

**Control Chart Constants** (varies by sample size n):

```
n    A2      D3      D4      d2
2   1.880    0      3.267   1.128
3   1.023    0      2.575   1.693
4   0.729    0      2.282   2.059
5   0.577    0      2.114   2.326
6   0.483    0      2.004   2.534
7   0.419   0.076   1.924   2.704
8   0.373   0.136   1.864   2.847
```

**Interpretation Guidelines**:

- **R Chart First**: If R chart shows control, X-bar chart is valid
- **X-bar Chart Second**: Then evaluate mean centering
- **Joint Evaluation**: Together show if process is capable and centered

#### X-bar and S Chart

**When to Use**: For larger sample sizes (n > 10) or variable sample sizes

**Advantages over X-bar/R**:
- S (standard deviation) more stable than R for large samples
- Better for when samples have varying sizes

**Formulas**:

```
X-bar-bar = Average of all measurements
S-bar = Average of sample standard deviations

UCL_X = X-bar-bar + A3 × S-bar
CL_X = X-bar-bar
LCL_X = X-bar-bar - A3 × S-bar

UCL_S = B4 × S-bar
CL_S = S-bar
LCL_S = B3 × S-bar
```

#### Individual and Moving Range Chart (I-MR)

**When to Use**: When only one measurement per sample (cannot group data)

**Examples**:
- Batch characteristics (entire batch one value)
- Destructive testing (consume part to measure)
- Unique or expensive items
- Slow processes (one measurement per hour)

**Formulas**:

```
Individual values: X1, X2, X3, ..., Xn
Moving Range: MR_i = |X_i - X_(i-1)|

X-bar = Σ(Individual values) / n
MR-bar = Σ(Moving ranges) / (n-1)

UCL_X = X-bar + 2.66 × MR-bar
CL_X = X-bar
LCL_X = X-bar - 2.66 × MR-bar

UCL_MR = 3.267 × MR-bar
CL_MR = MR-bar
LCL_MR = 0
```

---

### Attribute Data Charts (Counts and Proportions)

#### P Chart (Proportion Defective)

**When to Use**: Tracking percentage of defective items

**Examples**:
- Percent of assemblies with at least one defect
- Percent non-conforming
- Pass/fail results

**Formulas**:

```
p = Total defects / Total items inspected
σ_p = √[p(1-p)/n]

UCL = p + 3 × √[p(1-p)/n]
CL = p
LCL = p - 3 × √[p(1-p)/n]

If LCL < 0, set LCL = 0
```

**Variable Sample Size Handling**:

When n varies between samples:

```
UCL_i = p + 3 × √[p(1-p)/n_i]
LCL_i = p - 3 × √[p(1-p)/n_i]

(Recalculate limits for each sample)
```

#### NP Chart (Number Defective)

**When to Use**: Counting number of defective items (constant sample size)

**Advantage over P Chart**: No need to calculate proportions; use counts directly

**Formulas**:

```
n = constant sample size
np = Total defectives / Number of samples

UCL = np + 3 × √[np(1-np/n)]
CL = np
LCL = np - 3 × √[np(1-np/n)]
```

#### C Chart (Count of Defects)

**When to Use**: Counting total number of defects per inspection unit

**Examples**:
- Number of surface defects per sheet
- Number of solder joints per PCB
- Number of scratches per unit area

**Formulas**:

```
c = Total defects / Number of samples

UCL = c + 3√c
CL = c
LCL = c - 3√c (if negative, set to 0)
```

#### U Chart (Defects per Unit)

**When to Use**: Counting defects with variable inspection area

**Examples**:
- Defects per meter of fabric
- Defects per 100 feet of wire
- Defects per 1000 parts

**Formulas**:

```
u = Total defects / Total units inspected

UCL = u + 3 × √(u/n)
CL = u
LCL = u - 3 × √(u/n) (if negative, set to 0)
```

---

## Control Limits and Statistical Basis

### Three-Sigma Limits

Most control charts use **±3 sigma** limits:

```
Probability Distribution (Normal):
- Within ±1σ: 68.27% of data
- Within ±2σ: 95.45% of data
- Within ±3σ: 99.73% of data

Three-sigma limits select probability: 0.27% chance point falls outside
(Approximately 1 in 370 chance of false alarm from random variation)
```

### Western Electric Rules

Additional patterns indicating special cause variation:

**Rule 1**: One point beyond 3-sigma limits
- Immediate stop and investigate

**Rule 2**: 9 points in a row on same side of center
- Probable mean shift, investigate

**Rule 3**: 6 points in a row steadily increasing or decreasing
- Trend detected, investigate drift

**Rule 4**: 14 points alternating up and down
- Unusual variation pattern, investigate oscillation

**Rule 5**: 2 of 3 points beyond 2-sigma (same side)
- Possible mean shift, increase monitoring

**Rule 6**: 4 of 5 points beyond 1-sigma (same side)
- Definite mean shift, adjust process

**Rule 7**: 15 points in a row within ±1 sigma
- Artificially reduced variation, check measurement system

**Rule 8**: 8 points in a row beyond ±1 sigma (both sides)
- Mixed variation, investigate source

---

## Rational Subgrouping

**Definition**: Strategic selection of measurements to detect special causes effectively

### Subgrouping Strategies

#### Strategy 1: Consecutive Units
```
Sample every nth unit:
├─ Unit 1 ─ Unit 2 ─ Unit 3 ─ Unit 4 ─ Unit 5 ├─ (5-unit sample)
├─ Unit 6 ─ Unit 7 ─ Unit 8 ─ Unit 9 ─ Unit 10 ├─ (next sample)

Detects:
- Within-subgroup variation (natural process spread)
- Between-subgroup shifts (special causes)

Example: Machine cavity drift over production run
```

#### Strategy 2: Stratified Sampling
```
By production time or location:
├─ Early shift: Units 1-25 (5-unit sample)
├─ Mid shift: Units 26-50 (5-unit sample)
├─ Late shift: Units 51-75 (5-unit sample)

Detects:
- Shift-to-shift differences
- Time-dependent special causes (temperature changes, fatigue)

Example: Thermal cycling effects on dimensional stability
```

#### Strategy 3: By Source
```
By production line or machine:
├─ Machine A: 5 units per 2-hour period
├─ Machine B: 5 units per 2-hour period
├─ Machine C: 5 units per 2-hour period

Detects:
- Machine-to-machine differences
- Equipment-specific problems (calibration, wear)

Example: Cavity imbalance on multi-cavity mold
```

---

## Process Stability Assessment

### Statistical Tests for Stability

#### Test 1: Runs Test

**Hypothesis**: Data points randomly distributed around center line?

**Method**: Count runs (consecutive points on same side of center)

```
Expected runs for n points ≈ n/2

If runs << expected: Non-random pattern (special cause)
If runs >> expected: Alternating pattern (artificial control)

Example: 20 data points with only 4 runs
Expected: ~10 runs
Conclusion: Too few runs → NOT random → Special cause present
```

#### Test 2: Trend Test

**Hypothesis**: No systematic increase or decrease?

**Method**: Count increasing/decreasing pairs

```
# Increasing pairs for trend:
Points: 2.1, 2.3, 2.5, 2.6, 2.4, 2.7...
Pairs:    ↑    ↑    ↑     ↓    ↑

Significant trend if > expected number of ordered pairs
Suggests: Drift, wear, temperature change, etc.
```

#### Test 3: Variance Homogeneity

**Hypothesis**: Constant variance over time?

**Method**: Levene's test on variance by subgroup

```
H0: σ1² = σ2² = σ3² (Equal variances)
H1: At least one variance different

Reject H0 if: F-statistic > critical value
Conclusion: Special cause affecting variability
Example: Tool wear increasing variation
```

---

## Capability vs. Stability

### Four Capability Scenarios

```
Scenario 1: In Control & Capable (Ideal)
- Stable process
- Cpk > 1.33
- Maintain with routine monitoring
- Action: SPC monitoring only

┌──────────┐
│          │  X-bar chart: Random variation
│          │  Cpk: 1.52 (Excellent)
│    •     │  Decision: Production-ready
│   •••    │
│  •••••   │
└──────────┘

Scenario 2: In Control but Not Capable
- Stable process
- Cpk < 1.33 (too wide or off-center)
- Requires process improvement (equipment, methods)
- Action: Kaizen, equipment upgrade, process redesign

┌──────────┐
│ • •      │  X-bar chart: Stable
│•••••••   │  Cpk: 0.89 (Not capable)
│ • •      │  Decision: Cannot proceed; improve process
└──────────┘
  LSL  USL

Scenario 3: Out of Control but Appears Capable
- Unstable process
- Recent Cpk > 1.33 (false impression)
- Immediate investigation required
- Action: Find and eliminate special causes

┌──────────┐
│  • •     │  X-bar chart: Out of control (trends)
│ • • •    │  Recent Cpk: 1.41 (but unstable)
│  • •     │  Decision: Stop, investigate cause
│•        │
└──────────┘

Scenario 4: Out of Control and Not Capable (Critical)
- Unstable process
- Cpk < 1.33 significantly exceeded
- Emergency response required
- Action: Stop production, full investigation, redesign

┌──────────┐
│ •        │  X-bar chart: Out of control
│  •    •  │  Cpk: 0.55 (Very poor)
│ •   •••• │  Decision: STOP; critical improvement needed
│  •  •   │
└──────────┘
  LSL  USL
```

---

## Control Charting Fundamentals Checklist

### Data Collection
- [ ] Appropriate chart type selected for data type
- [ ] Rational subgroup strategy established
- [ ] Sample size consistent (or adjusted in chart)
- [ ] Sampling frequency documented
- [ ] Measurement system validated (Gage R&R)
- [ ] Data recorded with date/time stamps

### Control Limits Calculation
- [ ] Preliminary limits calculated from 25+ samples
- [ ] Control chart constants (A2, D3, D4) from correct table
- [ ] Baseline period represents normal operation
- [ ] No special causes in baseline period
- [ ] Sufficient data to establish stable baseline

### Chart Interpretation
- [ ] All points inside control limits (for baseline confirmation)
- [ ] No patterns suggesting special causes
- [ ] Common cause variation only
- [ ] Process declared "in control" to begin monitoring

### Ongoing Monitoring
- [ ] Charts maintained daily/per production shift
- [ ] New data points plotted immediately
- [ ] Rules applied (Western Electric rules)
- [ ] Out-of-control points documented
- [ ] Root cause investigations performed
- [ ] Corrective actions taken and verified
- [ ] Process capability maintained >1.33

---

## Quick Reference: Selecting the Right Chart

| Data Type | Chart Type | When to Use |
|-----------|-----------|------------|
| Continuous, rational groups | X-bar/R | Standard process monitoring (n=3-5) |
| Continuous, rational groups | X-bar/S | Larger samples (n>10) or variable n |
| Continuous, single value | I-MR | Batch characteristics, destructive testing |
| Defective items | P | Percent defective, variable sample size |
| Defective items | NP | Count defective, constant sample size |
| Defect count | C | Count total defects, fixed area/unit |
| Defect count | U | Defects per unit, variable area/unit |

---

## References and Further Learning

- **Montgomery, D. C.** (2020). Introduction to Statistical Quality Control
- **AIAG** (Automotive Industry Action Group). Statistical Process Control (SPC)
- **Wheeler, D. J.** (2010). Understanding Variation: The Key to Managing Chaos
- **ASQ** (American Society for Quality). Quality resources and certifications
