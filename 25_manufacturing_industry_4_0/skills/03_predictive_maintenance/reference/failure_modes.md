# Common Equipment Failure Modes Reference

## Overview

This reference provides characteristic signatures and failure progression timelines for common equipment failure modes. Understanding these patterns is essential for accurate anomaly detection and RUL prediction.

---

## 1. Rolling Element Bearing Failures

### 1.1 Normal Bearing Life Cycle

**Stage 1: Run-In Phase (0-100 hours)**
```
Characteristics:
- Ferrous particle count: 20-50 mg/100ml (initial settling)
- Vibration: Elevated, then stabilizing
- Temperature: Rises 15-25°C above ambient
- Acoustic: Slight noise diminishing

Cause: Micro-asperities wearing off, oil film establishment
Action: Monitor for stabilization; oil change not recommended until settled
Typical duration: 50-150 hours depending on equipment type
```

**Stage 2: Normal Operation (100 hours - end of life)**
```
Characteristics:
- Ferrous particle count: 5-15 mg/100ml (steady low level)
- Vibration RMS: Stable, <ISO Zone A threshold
- Crest Factor: 2.5-3.5 (Gaussian-like)
- Temperature: Stable ±2°C
- Acoustic: Steady whirring sound

Bearing Fault Frequencies:
- Present but at low amplitude
- BPFO and harmonics barely above noise floor
- No envelope acceleration peaks

This phase represents ~95% of bearing service life in well-maintained equipment
```

### 1.2 Bearing Outer Race Defect

**Failure Progression Timeline:**

```
STAGE 1: INCIPIENT FAULT (Week 0-1, 0-2% spall area)
├─ Indicators:
│  ├─ Crest Factor: 3.5-4.5 (rising)
│  ├─ Kurtosis: 3-5 (emerging impulsivity)
│  ├─ BPFO and harmonics: Low amplitude, visible in envelope spectrum
│  ├─ Temperature: +2-5°C above baseline
│  ├─ Oil ferrous: 15-25 mg/100ml
│  └─ Acoustic: Occasional clicking at running speed
│
├─ ML Model Indicators:
│  ├─ Anomaly score: 0.4-0.5 (isolated forest)
│  ├─ Reconstruction error: Slightly elevated
│  └─ RUL estimate: 4-6 weeks
│
└─ Recommended Actions:
   ├─ Increase vibration monitoring to weekly
   ├─ Thermal monitoring: Daily
   ├─ Oil analysis: Confirm particle count trend
   └─ Prepare spare bearing and maintenance plan

STAGE 2: EARLY PROPAGATION (Week 1-3, 2-5% spall area)
├─ Indicators:
│  ├─ Crest Factor: 5-8 (distinctly elevated)
│  ├─ Kurtosis: 6-10 (clear impulsivity)
│  ├─ BPFO amplitude: 2-5 × baseline noise
│  ├─ BPFO sideband spacing: Running speed ×N harmonics
│  ├─ Temperature: +8-15°C above baseline
│  ├─ Oil ferrous: 30-60 mg/100ml
│  ├─ Vibration RMS: Rising 10-20% per day
│  └─ Audible: Rhythmic clicking synchronized with shaft
│
├─ ML Model Indicators:
│  ├─ Anomaly score: 0.65-0.75
│  ├─ Reconstruction error: 2-3× baseline
│  ├─ RUL estimate: 2-4 weeks
│  └─ Confidence: High (98%+)
│
└─ Recommended Actions:
   ├─ Schedule maintenance within 1-2 weeks
   ├─ Reduce equipment load to minimum
   ├─ Increase monitoring to daily
   ├─ Prepare for extended downtime
   └─ Brief production schedule

STAGE 3: RAPID PROGRESSION (Week 3-6, 5-20% spall area)
├─ Indicators:
│  ├─ Crest Factor: 8-15 (very high)
│  ├─ Kurtosis: 10-20+ (severe impulsivity)
│  ├─ BPFO harmonics: Clearly visible up to 10× BPFO
│  ├─ Subharmonics: Chaotic components emerging
│  ├─ Temperature: +20-40°C above baseline
│  ├─ Oil ferrous: 80-150 mg/100ml (rapid rise)
│  ├─ Vibration RMS: Rising 20-50% per day
│  ├─ ISO code: 21/19/16+ (contaminated)
│  └─ Audible: Loud, irregular grinding
│
├─ ML Model Indicators:
│  ├─ Anomaly score: 0.80-0.90
│  ├─ RUL estimate: 1-3 weeks
│  ├─ Failure probability: 95%+
│  └─ Confidence: Critical risk zone
│
└─ Recommended Actions:
   ├─ IMMEDIATE MAINTENANCE SCHEDULING REQUIRED
   ├─ Stop unnecessary operation
   ├─ Continuous vibration monitoring
   ├─ Prepare for emergency maintenance if accelerates
   └─ Notify all stakeholders

STAGE 4: CRITICAL (Week 6+, 20%+ spall area)
├─ Indicators:
│  ├─ Vibration RMS: >200% increase from baseline
│  ├─ Temperature: +40-60°C (approaching material limits)
│  ├─ Oil ferrous: 150-300+ mg/100ml
│  ├─ Visible damage: Outer race visible spalling under inspection
│  ├─ Bearing play: Excessive axial movement
│  ├─ Cage condition: Damaged by wild motion
│  └─ Acoustic: Severe grinding, potential structural resonance
│
├─ Failure Risk:
│  ├─ Imminent bearing seizure: Hours to days
│  ├─ Potential for catastrophic failure: High
│  ├─ Secondary damage risk: Very high
│  └─ Safety hazard: Critical
│
└─ Actions:
   ├─ STOP EQUIPMENT IMMEDIATELY if not already scheduled
   ├─ Emergency maintenance (no delay)
   ├─ Full bearing replacement
   ├─ Inspection of adjacent components for damage
   └─ Root cause analysis (load, alignment, lubrication)
```

**Outer Race Defect Signature:**

```
Vibration Signature:
- Bearing Fault Frequency (BPFO) = (n/2)×fr×(1 + Bd/Pd×cos(φ))
- Example: 3-4 kHz for typical motor bearing at 1500 RPM
- Amplitude modulation: Occurring once per shaft revolution
  (outer race is stationary but load zone rotates)

Envelope Analysis:
- Bandpass filter: 5-20 kHz
- Look for BPFO and harmonics (2×BPFO, 3×BPFO, ...)
- BPFO sidebands at running speed intervals indicate load zone modulation

Why outer race fault creates periodic impacts:
1. Shaft rotates with load zone
2. As load zone passes over defect, rolling element impacts spall
3. One impact per shaft revolution
4. Creates 1X modulation of BPFO
```

### 1.3 Bearing Inner Race Defect

**Key Differences from Outer Race:**

```
Frequency Components:
- BPFI = (n/2)×fr×(1 - Bd/Pd×cos(φ)) ≈ 5.43×fr (for typical bearing)
- BPFI > BPFO for same bearing (different geometry)

Modulation Pattern:
- Inner race rotates with shaft
- All rolling elements periodically pass over defect
- Results in BPFI harmonics ± (shaft harmonics)
- Sideband spacing = running speed (different from outer race)

Progression:
- Typically faster than outer race (higher stress)
- Spall often originates from subsurface fatigue
- Inner race failures can be more sudden

Detection:
- BPFI peaks often have 2X running speed sidebands
- More chaotic, less regular than outer race
- May appear in both velocity and acceleration

Critical difference:
- Outer race: Can operate at reduced speed longer
- Inner race: Often leads to rapid cage failure
```

### 1.4 Rolling Element (Ball/Roller) Defect

**Failure Pattern:**

```
Frequency: Ball Spin Frequency (BSF) ≈ 0.40×fr
Example: 200 Hz for 1500 RPM bearing

Signature:
- Impacts when defective ball contacts outer race
- Impacts occur at BPFO rate (number of balls)
- But modulated by BSF as ball spins

Detection Challenge:
- Lower amplitude than inner/outer race faults
- Often masked by outer race defects
- Requires high-frequency analysis (envelope acceleration)

Progression:
- Slow initial development
- Accelerates rapidly once cavity reaches critical size
- Can lead to outer race failure from secondary damage

Detection requires:
- Envelope analysis (high-frequency demodulation)
- 10-20 kHz minimum analysis bandwidth
- Long monitoring periods to establish baseline
```

### 1.5 Cage (Retainer) Failure

**Causes:**

```
Primary: Inner race defect leading to cage damage
Secondary: Misalignment, inadequate lubrication
Rare: Fatigue from high-speed operation

Failure Progression:
1. Cage clearance increases (5-10% size increase)
2. Uncontrolled ball motion
3. Cage components fracture
4. Loose cage parts create random impacts
5. Bearing lockup imminent

Signature:
- Erratic, non-periodic vibration
- Subharmonic components (< 0.5×running speed)
- Very high kurtosis (>20)
- Chaotic time-domain appearance
- No clear frequency peaks (random impacts)

ML Detection:
- Isolation Forest detects high-anomaly scores
- Autocorrelation breaks down (non-periodic)
- Entropy increases significantly

Timeline:
- From cage damage to lockup: Hours to days
- Requires immediate bearing replacement
```

---

## 2. Rolling Machinery - Imbalance

### 2.1 Imbalance Characteristics

**Condition Definition:**

```
Rotating component has unequal mass distribution around rotation axis
Centrifugal force = m × r × ω²
Creates vibration at shaft running speed (1X)

Severity Levels (ISO 20816):
- Soft-bearing rotor: <3.5 mm/s
- Rigid-bearing rotor: <7.1 mm/s

Equipment-specific thresholds:
- Small motors: 2-3 mm/s
- Medium machines: 4-7 mm/s
- Large machines: 7-11 mm/s
```

**Vibration Signature:**

```
Frequency Domain:
- Dominant component: 1X (running speed)
- Amplitude proportional to imbalance mass × radius
- Minimal higher harmonics (clean, single-frequency)
- No sidebands or modulation

Time Domain:
- Smooth, sinusoidal appearance
- Peak-to-peak relatively constant
- Crest Factor ≈ 1.41 (perfect sine wave)

Directional Analysis:
- Radial (horizontal/vertical): Highest
- Axial: Minimal
- Usually uniform in both radial directions (though can be directional if uneven)

Thermal:
- Uniform temperature rise all around bearing
- Localized hot spots only at bearing supports
```

### 2.2 Imbalance Progression

**Timeline: Months to Years (Slow Degradation)**

```
STAGE 1: INITIAL IMBALANCE (Baseline condition)
├─ Characteristics:
│  ├─ 1X amplitude: Normal for equipment
│  ├─ Few months operation without change
│  └─ Stable temperature
│
└─ Action: Routine maintenance, no special attention

STAGE 2: PROGRESSIVE IMBALANCE (Months)
├─ Causes:
│  ├─ Corrosion eating material asymmetrically
│  ├─ Deposits on blade surface (pump, fan)
│  ├─ Material loss from erosion (cavitation, wear)
│  ├─ Bearing wear increasing radial play
│  └─ Coupling misalignment developing
│
├─ Indicators:
│  ├─ 1X amplitude increasing 5-10% per month
│  ├─ Temperature gradually rising
│  ├─ Phase angle changing (indicator: trending 1X vector)
│  └─ Crest Factor still ~1.41 (not impulsive)
│
└─ Action: Plan balancing within 2-3 months

STAGE 3: ADVANCED IMBALANCE
├─ Indicators:
│  ├─ 1X amplitude: 50-100% above baseline
│  ├─ Temperature: +15-25°C above normal
│  ├─ Bearing play: Visibly increased
│  └─ Mechanical looseness components: Minor (2X at 20% of 1X)
│
└─ Action: Schedule balancing within 2-4 weeks

STAGE 4: CRITICAL IMBALANCE
├─ Risk factors:
│  ├─ 1X vibration: >200% of baseline
│  ├─ Structural resonance excitation
│  ├─ Bearing wear approaching failure
│  └─ Looseness: Now significant (2X, 3X visible)
│
└─ Action: Immediate balancing required
          or equipment stop if balancing not immediately available
```

**Why imbalance often coexists with other faults:**

```
High imbalance → Elevated bearing loads
               → Accelerated bearing wear
               → Increased fatigue on cracked shafts
               → Looseness from wear

Imbalance + fault detection challenge:
- High 1X can mask other frequency peaks
- Use zoom FFT or order tracking around fault frequencies
- Filter out 1X component, analyze residual
```

---

## 3. Misalignment

### 3.1 Angular Misalignment

**Definition:** Shaft centerlines not parallel but form an angle at coupling

```
Severity: Function of angle and coupling type
Typical alignment tolerance: < 0.05° (0.87 mrad)
Severe misalignment: > 0.2° (3.5 mrad)

Vibration Signature:
- Dominant: 2X (coupling rotational frequency × 2)
- Also present: 3X, 4X, 5X harmonics
- Phase: 180° between top and bottom of bearing
- Pattern: High 2X relative to 1X (often 2X > 1X)

Why 2X appears:
- Misaligned coupling has two peaks per revolution
- One impact on each side of flexible element
- Creates 2× running speed vibration

Thermal:
- Localized hot bearing (typically on one side)
- Can be 5-10°C hotter than opposite bearing
- Sometimes creeping motion in coupling
```

### 3.2 Parallel (Offset) Misalignment

**Definition:** Shaft centerlines parallel but offset

```
Vibration Signature:
- Dominant: High 1X (like imbalance)
- But accompanied by high 2X (unlike pure imbalance)
- Ratio: 1X and 2X comparable in amplitude
- Distinguishing from imbalance: Phase measurement between points
  - Imbalance: In-phase across bearing
  - Offset: Out-of-phase across bearing

Thermal:
- Axial bearing heat rise (thrust bearing becomes hot)
- Can indicate axial load from misalignment

Mechanical effect:
- Creates bending moment at coupling
- Higher stress on coupling bolts
- Can cause coupling fracture (sudden failure)
```

### 3.3 Misalignment Progression

```
SLOW PROGRESSION (months to years):
├─ Mechanical wear:
│  ├─ Coupling element degradation
│  ├─ Bearing wear from side loads
│  └─ Eventual bearing failure
│
├─ Vibration trend:
│  ├─ 2X (or combined 1X+2X) increases gradually
│  ├─ Rate: 5-15% per month (slower than bearing wear)
│  └─ Linear or slightly exponential

└─ Timescale: 3-12 months to bearing failure

RAPID FAILURE (sudden):
├─ Triggers:
│  ├─ Coupling bolt looseness develops
│  ├─ Coupling element suddenly fails
│  └─ Shaft fracture from fatigue
│
├─ Signature:
│  ├─ Sudden large vibration increase
│  ├─ Appearance of 3X, 4X, 5X harmonics
│  ├─ Looseness indicators (broad spectrum)
│  └─ Can appear in minutes

└─ Action: Emergency shutdown may be necessary
```

---

## 4. Shaft Looseness (Mechanical Looseness)

### 4.1 Types of Looseness

**Bearing to Housing Looseness:**
```
Bearing inner race rotates in loose outer race
- Symptoms: 1X, 2X, 3X, 4X, ... all prominent
- Signature: Multiple harmonics 50% or more of 1X
- Often called: "Rattle" signature
```

**Foundation/Foot Looseness:**
```
Equipment not bolted firmly to foundation
- Symptoms: 1X, 2X prominent; sometimes subharmonic
- Low-frequency modulation (minutes timescale)
- Audible clanking when equipment starts/stops
```

**Bearing Clearance Looseness:**
```
Wear increases bearing radial play
- Gradual process from bearing degradation
- Indicates imminent bearing failure
- Combined with other bearing fault indicators
```

### 4.2 Looseness Signature

**Frequency Characteristics:**

```
Time Domain:
- Non-sinusoidal appearance
- Sharp peaks, flat between peaks
- Crest Factor > 4 (impulsive)
- Kurtosis > 4 (non-Gaussian)

Frequency Domain:
- Multiple harmonics: 1X, 2X, 3X, 4X, 5X+
- High-amplitude low harmonics (not just fine structure)
- Subharmonics at 0.5X, 0.33X, 0.25X (modulation pattern)
- Continuous noise floor between peaks

Envelope Analysis:
- Low frequency modulation (< 1X) sometimes present
- Can indicate secondary frequency interaction
```

**Diagnostic Challenge:**

```
Differentiation from imbalance:
Imbalance:        1X dominant, minimal 2X, smooth sine
Looseness:        1X, 2X, 3X equally significant, jagged

Differentiation from misalignment:
Misalignment:     2X elevated but harmonics regular
Looseness:        Multiple harmonics with non-periodic modulation

Combination fault:
Looseness often coexists with imbalance or misalignment
- High 1X (imbalance) + high 2X (misalignment) + random noise (looseness)
- Requires comprehensive analysis
- Usually indicates multiple problems requiring repair
```

### 4.3 Looseness Progression

**Timeline: Weeks to Months (Rapid once starts)**

```
STAGE 1: INCIPIENT LOOSENESS
├─ Cause: Bearing wear just creating slight play
├─ Amplitude: 0.5X level of main vibration
├─ Harmonics: 2X, 3X visible at 30-50% of 1X
├─ Time to critical: 4-12 weeks
└─ Action: Root cause investigation (bearing worn, fasteners loose?)

STAGE 2: MODERATE LOOSENESS
├─ 2X, 3X, 4X each 50-80% of 1X amplitude
├─ Non-periodic components emerging
├─ Audible rattling/clanking
├─ Bearing temperature rising (if bearing wear related)
├─ Time to critical: 1-4 weeks
└─ Action: Schedule maintenance (identify and tighten/replace parts)

STAGE 3: SEVERE LOOSENESS
├─ Harmonics extend to 6X+
├─ Broadband noise elevation (20+ dB above normal)
├─ Impulses visible in time waveform
├─ Foundation may visibly vibrate
├─ Time to catastrophic: Days to hours
└─ Action: Reduce load, plan emergency maintenance

STAGE 4: CATASTROPHIC
├─ Equipment in danger of rupture
├─ Bearing failure, shaft fracture, or coupling breakage imminent
└─ Action: STOP EQUIPMENT IMMEDIATELY
```

---

## 5. Pump-Specific Failures

### 5.1 Cavitation

**Definition:** Vapor bubbles form when pressure drops below vapor pressure, collapse causing damage

**Characteristics:**

```
Vibration Signature:
- Broadband noise increase (20-100 kHz)
- Fine granular appearance in time waveform
- No distinct frequency peaks
- Amplitude increases with cavitation severity

Acoustic:
- Distinctive grinding/sand-like sound
- Pulsating noise corresponding to pump speed
- Intensity increases at lower inlet pressure

Oil Analysis:
- No significant ferrous particles initially
- May see oxidation products later
- Water content can increase (corrosion products)

Temperature:
- Pump discharge temperature rises
- Inlet area may show localized heating

Vibration Features:
- Crest Factor: 4-8 (impulsive)
- Kurtosis: >4 (non-Gaussian)
- Energy in high frequencies (>5 kHz)
```

**Progression:**

```
EARLY CAVITATION:
- Brief cavitation during peak flow
- Intermittent grinding noise
- Detectable mainly in high-frequency bands
- Can be intermittent (load-dependent)

DEVELOPED CAVITATION:
- Continuous cavitation (poor inlet conditions)
- Visible surface erosion on impeller
- Vibration noticeably elevated
- Performance degradation (pressure, flow)

SEVERE CAVITATION:
- Rapid erosion rate
- Impeller thickness loss visible
- Mechanical imbalance develops (from erosion asymmetry)
- Imminent bearing failure (from imbalance effects)
- Sudden performance loss

Timeline: Weeks to months depending on severity
```

**Root Causes:**

```
- Inlet strainer clogged (pressure drop at inlet)
- Inlet line too small (excessive velocity)
- Seal leakage (air ingestion)
- NPSH (Net Positive Suction Head) insufficient
- Liquid temperature near saturation point
- Excessive viscosity (oil pump cavitation)
```

### 5.2 Impeller Wear

**Progression:**

```
STAGE 1: NORMAL WEAR (0-30% life)
├─ Wear particle size: 5-10 micrometers
├─ Wear rate: <1 mg/100ml per 1000 hours
└─ No performance change

STAGE 2: PROGRESSIVE WEAR (30-70% life)
├─ Wear rate: 1-3 mg/100ml per 1000 hours
├─ Pump discharge pressure: Slightly decreasing
├─ Vibration: Slight imbalance development (erosion asymmetric)
├─ Performance curves: Shifting toward lower efficiency
└─ Timeline: Months to years

STAGE 3: ACCELERATED WEAR (70-90% life)
├─ Wear rate: >5 mg/100ml per 1000 hours
├─ Mechanical imbalance visible
├─ Vibration RMS increasing
├─ Pressure: 5-10% loss visible
├─ Efficiency: Noticeably decreased
├─ Timeline: Weeks to months

STAGE 4: CRITICAL (>90% life)
├─ Performance loss: >20%
├─ Vibration excessive
├─ Bearing damage imminent
└─ Action: Impeller replacement required
```

**Wear Patterns:**

```
Abrasive wear (particulate in fluid):
- Uniform erosion around impeller
- Mainly visible on impeller back plate
- Particle size correlates to wear rate

Cavitation erosion:
- Pitting on suction side of impeller
- Non-uniform pattern
- Often concentrated on leading edge
- Rough, cratered surface

Corrosion wear:
- Uniform thin layer loss
- Occurs with incompatible fluids
- Surface becomes rough/dull
```

---

## 6. Gearbox Failures

### 6.1 Gear Tooth Pitting

**Definition:** Surface fatigue causing small material spalls/pits

**Progression:**

```
STAGE 1: EARLY PITTING (0-5% tooth face contact area)
├─ Initiation: Subsurface fatigue stress concentration
├─ Size: Pits 0.5-2 mm diameter, 0.1-0.5 mm depth
├─ Vibration signature:
│  ├─ Gear Mesh Frequency (GMF) amplitude rising
│  ├─ GMF sidebands appearing at shaft speed intervals
│  ├─ Envelope spectrum shows GMF + harmonics
│  └─ Broadband noise floor slightly rising
├─ Oil analysis:
│  ├─ Ferrous particles: 20-40 mg/100ml
│  ├─ Particle size: 5-20 micrometers (small)
│  └─ Particles relatively smooth (fatigue, not spall)
├─ Temperature: +2-5°C above baseline
└─ Duration: 2-8 months typical

STAGE 2: PROPAGATION (5-20% tooth face contact area)
├─ Pit sizes: 2-5 mm diameter, 0.5-1.5 mm depth
├─ Growth rate: Accelerating (exponential)
├─ Vibration:
│  ├─ GMF amplitude: 30-80% of normal
│  ├─ Sideband amplitude: More pronounced
│  ├─ Impulses visible in time waveform
│  └─ Envelope analysis: GMF clearly dominant
├─ Oil analysis:
│  ├─ Ferrous particles: 50-150 mg/100ml
│  ├─ Particle size distribution widening
│  └─ Some larger particles (>50 micrometers) appearing
├─ Temperature: +8-15°C above baseline
├─ Acoustic: Grinding noise at GMF becoming audible
└─ Duration: 1-3 months

STAGE 3: ADVANCED PITTING (20-50% tooth contact area)
├─ Tooth structural integrity compromised
├─ Pit depth: 1.5-3 mm (approaching dangerous territory)
├─ Vibration:
│  ├─ GMF and harmonics very prominent
│  ├─ Impulsive character increasing (high crest factor)
│  ├─ Overall RMS elevated 50-150%
│  └─ Multiple sideband families
├─ Oil analysis:
│  ├─ Ferrous particles: 150-300+ mg/100ml
│  ├─ Large particles: Some >100 micrometers
│  ├─ Particle morphology: Mix of spalls and fine wear
│  └─ Viscosity: May show slight decrease (heat)
├─ Temperature: +20-35°C elevation
├─ Acoustic: Loud grinding, metal-on-metal sound
└─ Duration: 2-8 weeks

STAGE 4: CRITICAL SPALLING (>50% tooth contact area)
├─ Tooth failure imminent
├─ Vibration: Extreme
├─ Potential for sudden tooth fracture
├─ Secondary failure: Spall fragments damage other teeth
└─ Action: IMMEDIATE REPLACEMENT REQUIRED
           Risk of catastrophic failure and extended downtime
```

**Gear Mesh Frequency (GMF):**

```
GMF = Number of teeth × shaft speed
    = N_teeth × RPM/60

Example: 40-tooth gear at 1500 RPM:
  GMF = 40 × 1500/60 = 1000 Hz

Sideband structure:
  GMF ± 1×RPM (gear error excitation)
  GMF ± 2×RPM (load modulation)
  GMF harmonics: 2×GMF, 3×GMF, ...

Detection method:
1. Calculate GMF for all gears in mesh
2. Look for peaks at GMF ± shaft harmonics
3. Use envelope analysis (5-30 kHz typical for industrial gears)
4. Monitor amplitude trend over weeks/months
```

### 6.2 Gear Tooth Fracture

**Brittle Failure vs. Fatigue:**

```
FATIGUE FRACTURE (progressive crack):
- Weeks of visible pitting first
- Crack initiates from pit
- Propagates slowly through tooth
- Warning: Vibration increasing consistently
- Timeline: Days to weeks from first crack to tooth separation

BRITTLE FRACTURE (sudden):
- Can occur in previously healthy teeth
- Often triggered by:
  * Sudden shock load
  * Thermal shock (cold fluid on hot gear)
  * Material defect or inclusion
  * Overload beyond design limit
- Timeline: No warning, instantaneous failure risk

Signature upon fracture:
├─ Sudden large vibration increase (100%+)
├─ Broadband energy increase across spectrum
├─ Multiple new frequency peaks (fragments bouncing)
├─ Temperature spike
├─ Oil analysis: Suddenly very high ferrous count (>500 mg/100ml)
└─ Sound: Sudden loud bang/crash at moment of fracture
```

### 6.3 Bearing Failure in Gearbox

**External load path:**

```
Gear mesh forces → Bearings support forces
Typically higher stress than standalone bearing
Gear mesh efficiency drives bearing load

Progression:
- Often follows gear wear (increased load)
- Can be simultaneous as root cause
- Outer race failure most common (stationary outer race)

Signature:
- BPFO (bearing fault frequency) + GMF interaction
- Complex sideband structure (BPFO ± GMF)
- Oil analysis confirms both ferrous particles and timing
```

---

## 7. Electric Motor Failures

### 7.1 Stator Winding Insulation Failure

**Failure Mechanisms:**

```
THERMAL DEGRADATION:
- Insulation rated temperature: 130°C (Class B), 155°C (Class F), 180°C (Class H)
- Operating at rated load should not exceed rated temperature
- Every 10°C above rating halves insulation life (rule of thumb)
- Degradation: Embrittlement, reduced mechanical strength

ELECTRICAL BREAKDOWN:
- Partial discharge (PD) initiates in voids/defects
- PD erodes insulation locally
- Creates carbonized paths (conducting)
- Eventually complete phase-to-phase or phase-to-ground short

MECHANICAL FAILURE:
- Vibration causing insulation abrasion against frame
- Thermal cycling causes expansion/contraction
- Loss of mechanical integrity of insulation

ENVIRONMENTAL:
- Moisture ingress causing hydrolysis
- Contamination (conductive particles, salt)
- Chemical attack (oil fumes, coolants)
```

**Progression:**

```
STAGE 1: INCIPIENT DEGRADATION (Months to years)
├─ Indicator: Temperature trending up +5-10°C
├─ Electrical: Minor partial discharge activity (fM or PD <1 pC)
├─ Mechanical: Insulation integrity still good
├─ Detection method: Temperature, Partial Discharge analysis
└─ Action: Maintain optimal operating temperature, increase monitoring

STAGE 2: PARTIAL DISCHARGE ACTIVITY (Weeks to months)
├─ PD level: 10-100 pC (partial discharge units)
├─ Visible damage: Pitting in insulation visible under magnification
├─ Current: Still normal (no short circuit yet)
├─ Temperature: Elevated
├─ Insulation resistance: Decreasing trend
├─ Detection: PD measurement, megohm test trending
└─ Action: Schedule motor replacement within 1-3 months

STAGE 3: ADVANCED DETERIORATION (Days to weeks)
├─ PD level: >100 pC, continuous discharge
├─ Insulation resistance: < 1 megohm
├─ Audible: Crackling/buzzing sound during operation
├─ Temperature: Significantly elevated (+20-30°C)
├─ Current: May show slight rise, harmonics increase
├─ Risk: Phase-to-phase short circuit possible (catastrophic)
└─ Action: Plan for imminent failure, have replacement ready

STAGE 4: FAILURE (Hours)
├─ Phase-to-phase or phase-to-ground short
├─ Excessive current (overcurrent), breaker trips
├─ Insulation charred, visible burn marks
├─ Magnetic field collapse
└─ Action: Emergency replacement, repair, or replacement as necessary
```

**Detection Methods:**

```
THERMAL:
- Winding temperature monitoring (RTD embedded in motor)
- Bearing temperature secondary indicator
- IR imaging of motor frame/terminal box

ELECTRICAL:
- Insulation resistance (megohm meter, DC test)
  Healthy: >2-5 megohms
  Degraded: 0.5-2 megohms
  Failure imminent: <0.5 megohms

- Partial discharge measurement
  (specialized equipment needed)

- Power quality: Phase balance, harmonics (current signature analysis)

VIBRATION:
- Electrical unbalance creates 2X running speed component
- Saturation effects if severe

ACOUSTIC:
- Crackling/buzzing sound (partial discharge)
- Whining tone change
```

### 7.2 Bearing Failure in Motors

**Specific to motor design:**

```
Motor bearing loads:
- Radial: Rotor weight + electromagnetic forces
- Axial: Typically light (except for direct-drive fans)
- Speed: Often high (1500-3600 RPM for induction motors)

Failure progression:
- Typically follows pattern similar to standalone bearings
- Combined with electrical load (unbalanced currents) can accelerate
- Bearing wear creates imbalance → increased current → winding heating

Bearing current (electrical current through bearing):
- Causes pitting and spalling independent of mechanical load
- Occurs when rotor current path through bearing to ground
- Prevention: Grounding rings, insulated bearings (for large motors)
- Effect: Dramatically shortens bearing life (can be 10x faster)
```

---

## 8. Failure Mode Prediction Framework

### 8.1 Feature Engineering for Each Failure Mode

**Create equipment-specific feature sets:**

```python
features_by_failure_mode = {
    "bearing_fault": [
        "crest_factor",
        "kurtosis",
        "bearing_fault_frequency_amplitude",
        "envelope_spectrum_energy_5_20khz",
        "temperature_trend"
    ],
    "imbalance": [
        "1x_amplitude",
        "1x_phase",
        "1x_amplitude_trend",
        "bearing_temperature_uniform"
    ],
    "misalignment": [
        "2x_amplitude",
        "2x_1x_ratio",
        "shaft_phase_difference",
        "bearing_temperature_asymmetry"
    ],
    "looseness": [
        "harmonic_count",
        "harmonic_amplitude_rms",
        "harmonic_spacing_uniformity",
        "crest_factor_time_series"
    ],
    "gear_pitting": [
        "gear_mesh_frequency_amplitude",
        "gmf_sideband_amplitude",
        "envelope_spectrum_gmf_energy",
        "oil_ferrous_particle_count",
        "oil_particle_size_distribution"
    ]
}
```

### 8.2 Multi-Fault Detection

**Equipment can exhibit multiple simultaneous faults:**

```python
# Example: Bearing fault + imbalance
# Signature includes:
# - Elevated 1X (imbalance)
# - High BPFO and harmonics (bearing fault)
# - Both 2X and bearing fault present

diagnosis_logic = {
    "1x_dominant_2x_secondary": "Primary: Imbalance, Secondary: Misalignment",
    "bpfo_with_1x_rise": "Primary: Bearing fault with developing imbalance",
    "gmf_plus_harmonics": "Primary: Gear pitting",
    "multiple_equal_harmonics": "Primary: Looseness",
    "broadband_noise": "Cavitation or advanced bearing spall"
}
```

---

## References

- ISO 20816: Mechanical vibration assessment of machines
- ISO 13373: Condition monitoring and diagnostics
- Mobley, R.K., "Predictive Maintenance"
- Harris, T.A., "Rolling Bearing Analysis: Essential Concepts of Bearing Technology"
- McFadden, P.D., & Smith, J.D., "Model for the impulsive vibrations from rolling element bearings"
