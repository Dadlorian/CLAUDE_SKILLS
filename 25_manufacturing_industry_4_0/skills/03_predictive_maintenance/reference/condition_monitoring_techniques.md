# Condition Monitoring Techniques Reference

## Overview

Condition monitoring encompasses multiple complementary techniques for assessing equipment health. This reference guide provides detailed technical information on the three primary monitoring approaches: vibration analysis, thermal imaging, and oil analysis (tribology).

---

## 1. Vibration Analysis

### 1.1 Fundamentals

**Definition**: Measurement and interpretation of mechanical vibrations to diagnose equipment condition and predict failures.

**Physical Basis**: All rotating machinery exhibits vibration that varies with:
- Speed of rotation
- Load applied
- Bearing/seal condition
- Alignment accuracy
- Balance condition
- Structural resonances

### 1.2 Vibration Parameters

#### 1.2.1 Time-Domain Parameters

**Peak-to-Peak (Pp)**
```
Pp = Maximum value - Minimum value

Application: Overall amplitude measurement
Unit: mm/s, inches/second, acceleration (g)
Interpretation: Larger values indicate more severe vibration
Limitation: Doesn't indicate where in frequency spectrum energy lies
```

**Peak (P) or Amplitude**
```
P = Maximum absolute value from centerline

Application: Shock/impact measurement
Unit: g for acceleration
Interpretation: Single transient events (bearing spall impacts)
Limitation: Can miss periodic lower-amplitude signals
```

**RMS (Root Mean Square)**
```
RMS = sqrt((1/n) * Σ(x_i - mean)²)

Application: Overall vibration energy
Unit: mm/s, g for acceleration
Interpretation: Energy content; better for overall health assessment
Standard: ISO 20816 severity zones based on RMS
Advantage: More statistically robust than peak
```

**Mean (Average)**
```
Mean = (1/n) * Σx_i

Application: DC offset in accelerometers
Interpretation: Should be ~0 for AC-coupled measurements
Issue: DC component removed by instrumentation
```

**Variance (σ²) and Standard Deviation (σ)**
```
σ² = (1/n) * Σ(x_i - mean)²
σ = sqrt(σ²)

Application: Signal spread and consistency
Unit: Same as signal units
Interpretation: Increasing σ suggests developing fault
Useful: Trend analysis over time
```

#### 1.2.2 Advanced Time-Domain Parameters

**Crest Factor (Peak-to-RMS Ratio)**
```
CF = Peak / RMS

Interpretation:
- CF ≈ 3.0: Gaussian random noise (healthy equipment)
- CF = 3-4: Early fault development
- CF = 4-6: Developing bearing/gear fault
- CF > 6-8: Severe spalling, tooth damage

Application: Impulsive fault detection without frequency analysis
Sensitivity: More sensitive to transient impacts than RMS alone
Early Detection: Can increase 2-3 weeks before RMS shows degradation
```

**Kurtosis (4th Moment / Normalized 4th Moment)**
```
Kurtosis = E[(x - μ)⁴] / σ⁴

Interpretation:
- Kurtosis ≈ 3: Gaussian distribution (healthy)
- Kurtosis > 3: Presence of impulsive events (developing fault)
- Kurtosis > 5-8: Clear evidence of bearing/gear faults
- Kurtosis >> 8: Severe, imminent failure

Application: Early detection of bearing wear and gear damage
Advantage: More sensitive than Crest Factor for some fault types
Limitation: Very sensitive to outliers; data quality critical
```

**Skewness**
```
Skewness = E[(x - μ)³] / σ³

Interpretation:
- Skewness ≈ 0: Symmetric distribution
- Skewness > 0.5: Asymmetry indicating one-sided damage
- Skewness > 1.0: Pronounced asymmetry typical of bearing spalls

Application: Distinguishing fault types
```

**Impulse Factor**
```
IF = Peak / Average(|x|)

Application: Impact detection
Higher values suggest discrete impacts from bearing defects
```

**Shape Factor**
```
SF = RMS / Average(|x|)

Healthy equipment: SF ≈ 1.11 (Gaussian)
Degrading equipment: SF > 1.4
Critical: SF > 1.6
```

#### 1.2.3 Energy and Entropy Metrics

**Spectral Entropy**
```
Shannon Entropy: SE = -Σ(p_i * log(p_i))

Where p_i = power at frequency i / total power

Interpretation:
- High entropy: Broadband noise (healthy)
- Low entropy: Concentrated energy at specific frequencies (fault signatures)
- Decreasing entropy: Developing fault becoming more tonal

Application: Detecting transition from healthy to degraded state
Advantage: Single scalar metric tracking degradation progression
```

**Energy Distribution**
```
Frequency band energy: E_band = Σ|FFT(band)|²

Typical bands for bearing diagnosis:
- 0-500 Hz: Imbalance, looseness
- 500-5 kHz: Bearing faults, misalignment
- 5-20 kHz: Bearing spalling, early cracks
- 20+ kHz: Ultrasonic friction, cavitation

Application: Identifying which frequency range contains fault signature
```

### 1.3 Frequency-Domain Analysis

#### 1.3.1 FFT (Fast Fourier Transform)

**Basic FFT Interpretation:**

```
FFT decomposes vibration signal into constituent frequencies

Peaks in FFT spectrum indicate:
- 1X (running speed): Imbalance
- 2X, 3X (harmonics): Misalignment, looseness
- Subsynchronous (< 1X): Rubs, blade passing
- Non-synchronous: Random noise, environmental

Amplitude interpretation:
- Normal: <50% of alarm threshold
- Alert: 70-100% of alarm threshold
- Alarm: > 100% of alarm threshold
```

**Bearing Fault Frequencies:**

```
Assuming:
- fr = shaft/fundamental frequency (Hz)
- Bd = roller/ball diameter (mm)
- Pd = pitch diameter (mm)
- n = number of rolling elements
- φ = contact angle (typically 0° for deep-groove bearings)

Ball Pass Frequency Outer race (BPFO):
BPFO = (n/2) * fr * (1 + Bd/Pd * cos(φ))
≈ 3.57 * fr (typical ball bearing)

Ball Pass Frequency Inner race (BPFI):
BPFI = (n/2) * fr * (1 - Bd/Pd * cos(φ))
≈ 5.43 * fr

Ball Spin Frequency (BSF):
BSF = (Pd/2Bd) * fr * (1 - (Bd/Pd * cos(φ))²)
≈ 0.40 * fr

Fundamental Train Frequency (FTF):
FTF = (1/2) * (1 - Bd/Pd * cos(φ)) * fr
≈ 0.35 * fr

Bearing fault presence: Look for BPFO, BPFI, BSF, FTF and harmonics
```

#### 1.3.2 Envelope Analysis (High-Frequency Demodulation)

**Purpose**: Extract bearing and gear fault signatures hidden in broadband noise

**Process:**

```
1. Acquisition: High-frequency acceleration (10-50 kHz)
2. Bandpass filtering: 5-40 kHz range
3. Demodulation/Rectification: Absolute value of analytic signal
4. Low-pass filtering: Remove high-frequency content
5. Analysis: Look for fault frequencies in filtered signal
```

**Mathematical Formulation:**

```
x(t) = input signal
X_hp(t) = high-pass filtered (> 5 kHz)
X_env(t) = |envelope(X_hp(t))| = bearing fault signature in envelope
FFT(X_env) = look for bearing fault frequencies
```

**Sensitivity**: 1000-10,000x more sensitive to bearing faults than time-domain RMS

**When to apply**: Early detection of bearing wear (weeks before failure)

#### 1.3.3 Zoom FFT and Order Tracking

**Zoom FFT:**
- Higher resolution around fault frequencies
- Useful when equipment speed varies
- Can achieve 3200 lines resolution around 1-10X running speed

**Order Tracking:**
```
Equipment running speed varies (e.g., motor acceleration)
Orders = multiples of running speed (1X, 2X, 3X, ...)

Order tracking normalizes spectrum to running speed:
- Imbalance always at 1X (regardless of actual frequency)
- Synchronous faults at integer orders
- Asynchronous faults show up as variations
```

**Application**: Variable-speed equipment, transmission shifting, startup/shutdown diagnosis

### 1.4 Sensor Selection and Placement

#### 1.4.1 Accelerometer Types

| Type | Range | Frequency | Application | Cost |
|------|-------|-----------|-------------|------|
| **MEMS** | ±2-50g | 0-10 kHz | Portable, temporary | Low |
| **Piezoelectric** | ±5-500g | 0.5-10 kHz | Standard condition monitoring | Medium |
| **Shear Mode Accelerometer** | ±100-500g | High frequency envelope | Bearing fault diagnosis | High |
| **IEPE** | Variable | 0.1-20 kHz | ICP, integrated electronics | Medium-High |
| **Wireless** | Limited | Variable | Mobile platforms | High |

**Typical specifications for bearing fault diagnosis:**
- Frequency range: 0.5 Hz to 20 kHz minimum (40 kHz preferred)
- Sensitivity: 100 mV/g (IEPE)
- Operating temperature: -40°C to +121°C
- Mounting: Permanent threaded or magnetic stud
- Weatherproofing: IP67+ for harsh environments

#### 1.4.2 Sensor Placement

**Optimal mounting locations:**

```
Rotating machinery:
- Bearings: Radial (horizontal, vertical) and axial directions
- Motor feet: Horizontal and vertical (detect looseness)
- Pump inlet/outlet: Structural mounting (fluid pulsation)
- Gearbox housing: Near bearing locations

Sensitivity ranking for bearing defects:
1. Bearing radial direction (highest sensitivity)
2. Structure-borne path to distant location
3. Axial direction (lower sensitivity for radial bearing faults)
4. Opposite side of bearing (much lower sensitivity)

Practical rule: Mount within 30mm of bearing for best sensitivity
```

**Multi-axis mounting:**

```
For comprehensive diagnostics, use 3-axis accelerometer or 3 single-axis:
- Horizontal (X): Detects imbalance, misalignment, looseness
- Vertical (Y): Detects bearing faults, resonance
- Axial/Thrust (Z): Detects thrust bearing wear, alignment

Or simplified 2-axis for cost reduction (eliminate axial)
```

### 1.5 Data Acquisition Parameters

**Sampling Rate and Duration:**

```
Nyquist frequency: f_s/2 must exceed highest frequency of interest
- For 10 kHz data: Minimum 20 kHz sampling rate
- For envelope analysis: 40-80 kHz recommended

Typical settings:
- Sampling rate: 51.2 kHz (10.24 kHz bandwidth), 102.4 kHz (20.48 kHz)
- Record duration: 10-60 seconds per measurement
- Measurement interval: Continuous (online) or periodic (offline)

Trade-off:
- Longer records: Better frequency resolution, more storage
- Shorter records: Lower latency, real-time capable
```

**Synchronization:**

```
Keyphasor (shaft speed reference):
- Enables order tracking and amplitude demodulation
- Shaft encoder or magnetic pickup on 1x per revolution marker

1 pulse per revolution enables:
- Running speed calculation
- Order-based analysis
- Speed-adaptive alarm thresholds
```

---

## 2. Thermal Analysis

### 2.1 Temperature Measurement Methods

#### 2.1.1 Contact Thermometry

**Thermocouples (TC):**
```
Temperature range: -200°C to +1200°C
Types:
- Type K (Nickel-Chromium): -50°C to +1250°C (most common)
- Type J (Iron-Constantan): -40°C to +750°C
- Type T (Copper-Constantan): -200°C to +350°C
- Type E (Nickel-Chromium): -200°C to +900°C

Characteristics:
- Response time: 0.5-5 seconds
- Accuracy: ±1-2% of temperature
- Non-intrusive if mounted on surface
- Direct contact required with measurement point

Application: Bearing, motor winding, gearbox sump temperature monitoring
```

**Resistance Temperature Detectors (RTD/Pt100):**
```
Temperature range: -50°C to +200°C (Pt100 standard)
Response time: 1-10 seconds
Accuracy: ±0.5°C typical
Advantages:
- More stable than thermocouple
- Better long-term accuracy
- Common in industrial installations

Application: Embedded in motor stator, bearing housing
```

**Thermistors (NTC/PTC):**
```
Temperature range: -50°C to +200°C
Response time: < 0.5 seconds (fastest)
Cost: Very low
Disadvantages:
- Non-linear response
- Requires calibration
- Limited accuracy (±1-2°C)

Application: Low-cost equipment monitoring
```

#### 2.1.2 Non-Contact Thermography

**Infrared Thermometer (Pyrometer):**
```
Temperature range: -20°C to +1500°C
Response time: < 1 second
Measurement principle: Stefan-Boltzmann law
P = ε * σ * T⁴

Where:
- ε = emissivity (0-1, material dependent)
- σ = Stefan-Boltzmann constant
- T = absolute temperature

Advantages:
- Non-contact, safe for moving/hot equipment
- Fast response
- No mounting needed

Disadvantages:
- Emissivity dependent (shiny surfaces challenging)
- Spot measurement only
- Environmental radiation interference

Common emissivities:
- Painted steel: 0.92-0.97
- Oxidized steel: 0.82-0.88
- Polished steel: 0.08-0.15
- Motor paint (black): 0.95
- Aluminum (oxidized): 0.03-0.30

Correction: If emissivity unknown, compare change in readings (ratio)
```

**Thermal Imaging Camera:**
```
Resolution: 320x256 to 1024x768 pixels
Temperature range: -20°C to +1500°C (depends on model)
Accuracy: ±2% or ±2°C
Measurement speed: Real-time video

Advantages:
- Visual assessment of temperature distribution
- Detects thermal patterns and hotspots
- Large area coverage

Disadvantages:
- Equipment cost ($5K-$50K+)
- Training required for interpretation
- Environmental factors (reflections, emissivity)
- Post-processing needed for quantitative analysis

Typical inspection: Periodic (monthly, quarterly) survey
Mounting: Portable handheld for inspections
```

### 2.2 Thermal Analysis for Equipment Diagnosis

#### 2.2.1 Bearing Temperature Diagnosis

**Normal operating ranges:**

```
Equipment type          Normal range    Alert level    Danger level
Roller bearings        40-80°C         85-90°C        >100°C
Ball bearings          50-70°C         80-95°C        >110°C
Lightly loaded         40-60°C         70-80°C        >90°C
Heavily loaded         60-90°C         100-110°C      >120°C
High-speed            60-100°C         110-120°C      >130°C

Degradation timeline:
- Healthy: Stable temperature ±5°C
- Early wear: Temperature increase +10-15°C
- Progressive fault: Temperature increase +20-30°C
- Imminent failure: Temperature increase +40-50°C or sudden jump
```

**Temperature vs. Vibration Correlation:**

```
Typical progression:
Day 1:     Vibration increases (Crest Factor > 3)
Day 7-14:  Temperature begins rising visibly
Day 21-30: Vibration RMS and temperature both elevated
Day 30-60: Temperature becomes critical (>100°C for ball bearing)
Day 60+:   Failure imminent

Implication:
- Vibration detects fault 1-3 weeks BEFORE temperature rise
- Temperature provides backup confirmation
- Fusion improves reliability of both methods
```

#### 2.2.2 Motor Winding Temperature Diagnosis

**Hot-spot temperature estimation:**
```
Measured: Winding temperature sensor (RTD in coil)
Estimated: Actual hot-spot temperature

Relationship (IEC 60085):
T_hot_spot = T_measured + K * (I/I_rated)²

Where:
- K = temperature rise coefficient (10-30°C typical)
- I/I_rated = load factor

Example: Measured 75°C, rated temperature 180°C
Margin = 180 - 75 = 105°C
Safe operating current: I = I_rated * sqrt(105/20) ≈ 2.3 × I_rated (practical limit 1.5×)
```

**Phase current imbalance detection:**
```
Three-phase motor phases should have balanced currents
Imbalance causes uneven heating:

Current imbalance = (max_phase - min_phase) / average_phase × 100%

Imbalance > 5%: Investigate
- Voltage supply imbalance
- Load imbalance
- Motor winding problem

Temperature signature:
- Hotter phase: Side with higher current
- Temperature difference: 10-20°C between phases
- Action: Voltage correction or motor inspection required
```

#### 2.2.3 Gearbox Temperature Diagnosis

**Oil temperature relationship:**

```
Gearbox temperature = Ambient + Load heating + Friction heating

Normal ranges:
- Lightly loaded: 55-70°C
- Normally loaded: 60-80°C
- Heavily loaded: 75-95°C
- Over-temperature: > 95°C critical

Degradation indicators:
- Temperature rise without load increase: Bearing wear or gear wear
- Temperature surge: Internal friction increase (gear spall, bearing damage)
- Erratic temperature: Intermittent contact issues

Rate of temperature rise:
- Normal startup: 20-30°C in first 30 minutes
- Should stabilize within 1-2 hours
- Continued rise indicates problem
```

**Localized thermal imaging findings:**

```
Hot bearing (one bearing hotter than others): Lubrication problem or wear
Hot gear mesh area: Tooth damage, misalignment, incorrect lubricant
Thermal pattern asymmetry: Shaft misalignment, uneven load distribution
Consistent elevation of entire box: Oil degradation, inadequate cooling
```

---

## 3. Oil Analysis (Tribology)

### 3.1 Oil Sampling and Preparation

#### 3.1.1 Sampling Procedure

**Sample location:**
```
Optimal: Middle of sump (neither surface nor bottom)
Bearing/gear box: 50mm from circulation pump outlet
Avoid: Walls, filters, drain valves (may have accumulated particles)

Timing:
- Equipment warm (normal operating temperature)
- After adequate run-in (reduce new oil particles)
- Before oil change (captures current condition)
- Consistent day/time for baseline trending
```

**Sample handling:**

```
Container: Clean glass or plastic vial (100-125 ml)
Labeling: Date, time, equipment ID, operator, run hours
Storage: Room temperature, dark location
Shipping: Within 2 weeks of collection
Contamination avoidance:
- Use fresh container (never reuse)
- Avoid dust, water introduction
- Sealed immediately after collection
- No exposure to extreme temperatures
```

**Sampling frequency:**

```
Based on equipment criticality and oil life:

Equipment criticality: HIGH (production critical)
- Normal operation: Every 250-500 hours
- Known issues: Every 50-100 hours
- During break-in: Every 100 hours (first 1000 hours)

Equipment criticality: MEDIUM
- Normal operation: Every 500-1000 hours
- Based on oil change interval

Equipment criticality: LOW
- Every 1000-2000 hours or per manufacturer schedule

Alternative approach: Condition-based
- Sample when equipment temperature rises 10-15°C
- Sample when vibration increases 50%
- Sample per maintenance plan updates
```

### 3.2 Oil Analysis Parameters

#### 3.2.1 Wear Debris Analysis

**Ferrous Particle Count:**

```
Measurement unit: mg/100ml (milligrams per 100 milliliters of oil)
Also reported as: ppm (parts per million, approximately equal for oils)

Interpretation:
- 0-10 mg/100ml: Excellent (new oil, clean equipment)
- 10-20 mg/100ml: Good (normal wear)
- 20-50 mg/100ml: Acceptable (monitor trend)
- 50-100 mg/100ml: Caution (degradation visible)
- 100-150 mg/100ml: Alert (advanced wear)
- >150 mg/100ml: Critical (imminent failure)

Wear rate assessment:
- Stable or decreasing: Equipment running-in completing
- Slowly increasing (1-5 mg/month): Normal wear
- Rapidly increasing (>10 mg/month): Developing fault
- Sudden spike: Bearing spall or gear tooth fracture

Rate of change importance:
- Absolute level less important than trend
- Rate of change predicts time to critical condition
- Equipment-specific baselines critical (compare only same equipment type)
```

**Particle Morphology (ISO 4406 Particle Counting):**

```
ISO 4406 Code Format: a/b/c
Where:
- a = particles > 4 micrometers (µm)
- b = particles > 6 µm
- c = particles > 14 µm

Examples and interpretation:
- 14/12/08: Very clean (new fluid standard)
- 16/14/11: Clean (acceptable for most systems)
- 18/16/13: Moderate cleanliness
- 20/18/15: Excessive contamination
- 21/19/16+: Severe contamination (filter or seal failure)

Trend tracking:
- Compare current ISO code to baseline
- First position (>4 µm) rises fastest with wear
- Rapid code increase: Accelerated wear rate

Action thresholds:
- Code increase > 2 positions: Investigate
- Code increase > 4 positions: Schedule maintenance
- Code rise beyond 20/18/15: Immediate action required
```

**Particle Size Distribution:**

```
Particle analysis reveals:
- Dominant particle size indicates fault type
- < 5 µm: Normal wear particles, dust contamination
- 5-15 µm: Moderate bearing/gear wear
- 15-50 µm: Spalling or tooth damage
- 50-100 µm: Catastrophic bearing failure
- > 100 µm: Imminent failure or bearing outer race failure
```

#### 3.2.2 Oil Degradation Parameters

**Viscosity (Kinematic Viscosity):**

```
Unit: cSt (centistokes = mm²/s)
Measurement: At 40°C and 100°C
Common oil grades: ISO VG 32, 46, 68, 100, 150, 220, 320, 460

Baseline and acceptable range:
- Baseline: Initial oil analysis value
- Acceptable drift: ±5% to ±10% from baseline
- Caution: 10-15% change
- Alert: 15-20% change
- Critical: > 20% change

Viscosity change causes:
- Increasing viscosity:
  * Oxidation of base oil
  * Contamination with heavy residue
  * Water emulsion (thick, milky appearance)

- Decreasing viscosity:
  * Shearing of VI improvers (if synthetic oil)
  * Contamination with lighter hydrocarbon
  * Base oil thermal degradation (very high temperature)
```

**Total Acid Number (TAN):**

```
Unit: mg KOH/g oil
Represents: Quantity of organic acids in oil

Baseline and thresholds:
- Fresh oil: TAN < 0.1 mg KOH/g
- Mid-life: TAN = 0.5-1.5 mg KOH/g
- Oxidation concern: TAN > 1.5 mg KOH/g
- Oil change required: TAN > 2.0-2.5 mg KOH/g (equipment/oil specific)

TAN increase rate:
- Normal oxidation: 0.05-0.1 mg KOH/g per 1000 hours
- Accelerated: > 0.2 mg KOH/g per 1000 hours (high temperature or contamination)
- Severe: > 0.5 mg KOH/g per 1000 hours (imminent oil change required)

Remaining oil life estimation:
- Oil life = (TAN_limit - TAN_current) / (TAN_increase_rate)
- Example: (2.0 - 1.2) / (0.1 per 1000 hrs) = 8,000 hours remaining
```

**Total Base Number (TBN):**

```
Unit: mg KOH/g oil
Represents: Alkalinity reserve for acid neutralization

Interpretation:
- Fresh oil: TBN = 8-12 mg KOH/g (typical mineral oils)
- Operating oil: TBN decreases with use
- Oil change required: TBN < 2-3 mg KOH/g (equipment specific)

TBN consumption:
- Normal rate: 0.3-0.7 mg KOH/g per 1000 hours
- Accelerated: > 1.0 mg KOH/g per 1000 hours

Alkalinity depletion reasons:
- Neutralizing organic acids from oxidation
- Neutralizing sulfurous acids from fuel contamination
- Neutralizing water-formed acids from moisture

Monitoring importance:
- TBN < 30% of original: Alert
- TBN < 10% of original: Critical, schedule oil change
```

**Oil Oxidation Stability:**

```
Measurement methods:
- TOST (ASTM D943): Time to increase in acidity by 1.0 mg KOH/g
- Rotary Bomb Oxidation Test (RBOT, ASTM D2272): Oxidation life

Oxidation stability indicates:
- Rate at which oil will degrade
- Extended oxidation stability (synthetic): 5000+ hour TOST
- Standard mineral oil: 1000-2000 hour TOST
- Degraded oil showing accelerated oxidation: Oxidation reserve depleted

Acceleration factors:
- Temperature: +10°C approximately doubles oxidation rate
- Copper contamination: Catalyst for oxidation (5-10x faster)
- Water contamination: Promotes oxidation
- Particulates: More surface area for oxidation reactions
```

#### 3.2.3 Water and Contamination

**Water Content:**

```
Measurement: Karl Fischer titration (ASTM D6304)
Unit: ppm (parts per million) or % by volume

Thresholds:
- New oil: < 100 ppm
- Operating oil (acceptable): < 500 ppm
- Caution: 500-1000 ppm
- Alert: 1000-1500 ppm
- Critical: > 1500 ppm (milky appearance, emulsion)

Water sources:
- Humidity ingress through breather
- Condensation (temperature cycling)
- Cooling water system leaks (critical for heat exchangers)
- Washdown and seal leakage

Water contamination effects:
- Viscosity increase (emulsion)
- Acid formation (water + organic acids)
- Bearing/gear surface corrosion
- Lubrication film breakdown

Time to critical for high water:
- 1000 ppm: 1-2 weeks
- 1500+ ppm: Immediate corrective action required
```

**Particulate Contamination (ISO 4406):**

Already discussed under particle morphology above.

**Flash Point:**

```
Definition: Minimum temperature at which oil vapors ignite
Unit: °C
Measurement: ASTM D92

Interpretation:
- Baseline flash point: Equipment oil specification
- Decrease in flash point:
  * Contamination with lighter hydrocarbons
  * Loss of volatiles (heating)
  * Equipment failure imminent

- Significant decrease (>10°C): Action required
  * May indicate fuel contamination or oil mixing
  * Safety hazard if operating near flash point
```

### 3.3 Oil Analysis Trending and Decision Rules

#### 3.3.1 Single-Parameter Trending

**Approach:**

```
1. Establish baseline (equipment runs normally, first 100-200 hours)
2. Subsequent samples plotted against:
   - Time
   - Operating hours
   - Equipment cycles
3. Fit trend line:
   - Linear trend: Rate of change
   - Exponential trend: Accelerating degradation

4. Decision rule:
   Current_value + (rate × time_to_action_threshold) = Action_threshold

   If sum exceeds action threshold: Schedule maintenance
```

**Ferrous particle trending example:**

```
Sample history (every 250 hours):
Hour 250:   15 mg/100ml
Hour 500:   18 mg/100ml
Hour 750:   22 mg/100ml
Hour 1000:  28 mg/100ml

Linear fit: y = 0.052x + 12.25 (rate = 13 mg/100ml per 1000 hours)

Critical threshold: 100 mg/100ml
Time to critical: (100 - 28) / 0.052 = 1385 hours remaining
Maintenance recommendation: Schedule within 1000 hours (conservative margin)
```

#### 3.3.2 Multi-Parameter Assessment

**Composite Condition Index:**

```
CCI = w₁(TAN_trend) + w₂(water_level) + w₃(particle_count) + w₄(viscosity_change)

Where weights (w₁, w₂, ...) reflect importance and normalized to 0-1 scale

Example normalization:
- TAN: (current - baseline) / (critical - baseline)
- Water: current / critical_level
- Particle count: current_ISO / critical_ISO
- Viscosity: |current - baseline| / (10% baseline)

Decision thresholds:
- CCI < 0.3: Continue operation, routine monitoring
- 0.3 < CCI < 0.6: Increased monitoring, preliminary scheduling
- 0.6 < CCI < 0.8: Schedule maintenance (1-2 weeks)
- CCI > 0.8: Immediate scheduling required
```

#### 3.3.3 Condition-Based Oil Change Intervals

**Traditional approach**: Fixed interval (2000 hours, 1 year)

**Advanced approach**: Condition-based intervals

```
CONDITION-BASED DECISION ALGORITHM:

While (equipment operating):
    Sample oil every 500 hours

    If TAN > 1.5 and TAN rate > 0.2 mg/100h:
        estimate_oil_life = (2.0 - TAN) / rate
        if estimate_oil_life < 1000 hours:
            schedule_oil_change()

    If water_level > 1000 ppm:
        schedule_oil_change()  # Immediate

    If ferrous_particle > 100 mg/100ml:
        investigate_equipment_failure()
        schedule_oil_change()

    If ISO_code increase > 4 positions:
        log_seal_failure_alert()
        schedule_inspection()

    If viscosity change > 20%:
        notify_engineering()
        evaluate_oil_compatibility()

Result: Oil change only when needed
- Extends oil life 20-40% (cost savings)
- Prevents over-extended intervals
- Maintains equipment reliability
```

---

## 4. Comparison and Integration

### 4.1 Technique Comparison Matrix

| Factor | Vibration | Thermal | Oil Analysis |
|--------|-----------|---------|--------------|
| **Fault detection time** | Earliest (1-4 weeks) | Early-to-mid (2-6 weeks) | Later (4-12 weeks) |
| **Bearing faults** | Excellent | Good | Fair |
| **Gear faults** | Excellent | Moderate | Good |
| **Lubrication issues** | Poor | Moderate | Excellent |
| **Misalignment** | Excellent | Poor | Poor |
| **Imbalance** | Excellent | Fair | Poor |
| **Looseness** | Good | Fair | Poor |
| **Temperature control** | Poor | Excellent | Moderate |
| **Implementation cost** | Moderate | Low-Moderate | Moderate |
| **Real-time capability** | Yes | Yes | No (lab analysis) |
| **Instrumentation invasive** | Slightly | Non-contact | Yes (sampling) |

### 4.2 Integrated Condition Monitoring

**Health Score Calculation:**

```
Normalized scores (0-1, 0=healthy, 1=failure):
- Vibration_score = (RMS - normal_RMS) / (alarm_RMS - normal_RMS)
- Thermal_score = (Temp - normal_Temp) / (alarm_Temp - normal_Temp)
- Oil_score = (ferrous - baseline) / (critical - baseline)

Composite Health Score:
H = 0.40×Vibration + 0.30×Thermal + 0.30×Oil

Interpretation:
- H < 0.3: Healthy, continue operation
- 0.3 < H < 0.5: Caution, increase monitoring
- 0.5 < H < 0.7: Alert, schedule maintenance within 2 weeks
- H > 0.7: Critical, schedule maintenance immediately
```

**Decision support example:**

```
Equipment: Centrifugal pump bearing
Vibration RMS: 12 mm/s (normal: 6, alarm: 25)
      Vibration_score = (12-6)/(25-6) = 0.316
Bearing temperature: 85°C (normal: 60, alarm: 100)
      Thermal_score = (85-60)/(100-60) = 0.625
Oil ferrous particles: 45 mg/100ml (baseline: 15, critical: 120)
      Oil_score = (45-15)/(120-15) = 0.286

Health Score = 0.40×0.316 + 0.30×0.625 + 0.30×0.286 = 0.409

Decision: CAUTION level
Action: Schedule oil sample (confirm trend), increase vibration monitoring
         from monthly to bi-weekly, plan maintenance within 3 weeks
```

---

## References

- ISO 20816 (formerly ISO 10816): Mechanical vibration assessment
- ISO 13373 series: Condition monitoring and diagnostics
- ISO 4406: Lubricant cleanliness codes
- ASTM D6595: Standard practice for oil condition monitoring
- Mobley, R. K., "Predictive Maintenance"
- DIN 51589: Guidelines for oil analysis
