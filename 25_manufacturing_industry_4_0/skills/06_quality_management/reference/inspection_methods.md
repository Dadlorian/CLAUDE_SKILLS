# Inspection Methods Reference

## Overview

This reference covers advanced manufacturing inspection technologies: Coordinate Measuring Machines (CMM), Automated Optical Inspection (AOI), and Computer Vision systems.

---

## Coordinate Measuring Machine (CMM)

### CMM Types and Characteristics

#### Bridge CMM (Most Common)

**Design**: Portal structure with moving gantry over stationary table

**Advantages**:
- High rigidity and stability
- Excellent for large, heavy parts
- Best accuracy and repeatability
- Multiple probing heads and sensor options

**Disadvantages**:
- Large footprint (requires dedicated space)
- Longest setup time

**Typical Specifications**:
- Measuring range: 2-3 meters
- Accuracy: ±2-5 micrometers
- Point repeatability: ±0.5-1 micrometer
- Capacity: 500-5000 kg parts

**Best For**: Production high-volume inspection, complex parts, critical tolerances

#### Cantilever CMM

**Design**: Overhanging probe arm from fixed support structure

**Advantages**:
- Better access to part underside
- Three-sided access
- Compact footprint

**Disadvantages**:
- Less rigid than bridge
- Lower accuracy for large parts
- Typically smaller measurement range

**Typical Specifications**:
- Measuring range: 1.5-2.5 meters
- Accuracy: ±3-5 micrometers
- Capacity: 100-500 kg

**Best For**: Medium-sized parts, aerospace components, inspecting complex features

#### Horizontal Arm CMM

**Design**: Horizontal rotating probe arm with vertical Z-axis

**Advantages**:
- Ease of part loading
- Excellent for large parts
- Good for measuring deep cavities

**Disadvantages**:
- Slower point collection
- More manual operation required

**Best For**: Large castings, fabrications, one-off prototype parts

### CMM Measurement Process

#### 1. Part Setup

**Datum Establishment:**
```
Datum A (Primary): Usually largest, most stable surface
- Plane surface or reference pad
- Supports 3 points of contact
- Prevents rotation/rocking

Datum B (Secondary): Perpendicular to Datum A
- Supports 2 additional points
- Locks rotation about Datum A

Datum C (Tertiary): Perpendicular to both
- Supports 1 final point
- Completely constrains part in 6 degrees of freedom

Example - Engine Block Datum Setup:
Datum A: Top flat surface (cylinder deck) - 3 points
Datum B: Side reference surface - 2 points
Datum C: Back reference surface - 1 point
```

**Part Positioning:**
- Clean part (blow off loose dust, soft cloth)
- Position on machine table/fixture
- Confirm stable and secure
- Ensure probe accessibility to all features
- Place on repeatable locator pads

#### 2. Probe Calibration

```
1. Load master sphere (ceramic ball, certified diameter)
   - Typical size: ∅25 mm
   - Calibration uncertainty: ±0.1 micrometer
   - Sphere sits on calibration pad

2. Probe offset measurement
   - Approach sphere with each probe tip
   - Touch sphere at multiple points (8-12 points)
   - Machine calculates probe tip offset from readhead
   - Typical offset: 45-80 mm (varies by probe extension)

3. Verification
   - Probe repeatability: Re-touch sphere and confirm match
   - Repeat for each probe configuration
   - Document offset values in machine
```

#### 3. Feature Measurement

**Point Collection Methods:**

```
Manual Point Collection:
- Operator moves probe to feature
- Presses trigger to record point
- Used for: Simple parts, few points
- Time: 30-120 seconds per point

Automatic Scanning:
- CNC program controls probe movement
- Continuous surface following
- Records dense point cloud
- Used for: Complex surfaces, high point density
- Speed: 10-50 points per second

Tactile vs. Non-Contact:
- Tactile: Physical probe tip contacts surface
  * Higher accuracy
  * Works on all materials
  * Slower speed
- Non-contact: Laser or vision sensors
  * Faster measurement
  * No marking on surface
  * Limited to reflective or specific colors
```

**Feature Definition Example - Hole:**

```
Hole Measurement Points:
- Top circular pattern: 8 points around hole top
- Middle circular pattern: 8 points around hole middle
- Bottom circular pattern: 8 points around hole bottom

Total: 24 points in 3D space

Analysis:
- Diameter calculation: Best-fit circle
- Position: XY coordinates of circle center
- Depth: Z-axis position
- Perpendicularity: Angle vs. Datum A
- Confidence interval: ±0.02 mm typical
```

#### 4. Data Analysis and Reporting

**Dimensional Analysis:**
```
Measurement Result vs. Specification:
- Actual dimension: 25.043 mm
- Nominal: 25.000 mm
- Tolerance: ±0.050 mm (25.000 ± 0.050)
- Upper spec limit (USL): 25.050 mm
- Lower spec limit (LSL): 24.950 mm

Evaluation:
- Is 25.043 within tolerance? YES
- Position relative to nominal? +0.043 mm (high side)
- Margin to USL: 25.050 - 25.043 = 0.007 mm
- Margin to LSL: 25.043 - 24.950 = 0.093 mm

Status: PASS (Acceptable)
```

**Geometric Tolerance Evaluation:**

```
Example: Perpendicularity of hole to datum plane

Specification: Perpendicularity to Datum A: ≤0.05 mm

CMM Measurement:
1. Establish Datum A (plane best-fit to surface points)
2. Establish hole axis (best-fit to measured points)
3. Calculate angle between hole axis and Datum A plane
4. Convert angle to linear deviation at hole diameter

Result:
- Angle deviation: 0.015°
- Linear deviation (perpendicularity): 0.026 mm
- Tolerance: 0.050 mm
- Status: PASS (0.026 < 0.050)
```

### CMM Measurement Uncertainty

**Total Uncertainty Contributors:**

```
Measurement Uncertainty = √(Probe²+Environmental²+Technique²+Gage²)

1. Probe Uncertainty (±0.5-1.5 μm)
   - Probe stylus roundness
   - Offset calibration repeatability

2. Environmental (±0.5-2 μm)
   - Room temperature variation (±1°C changes length)
   - Air turbulence
   - Humidity effects

3. Technique (±1-5 μm)
   - Point location on surface
   - Pressure applied to surface
   - Operator consistency

4. Gage Uncertainty (±0.5-1 μm)
   - Positional repeatability
   - Scale calibration

Total Typical Uncertainty: ±2-5 μm

Example:
- Part dimension: 50.000 mm
- CMM reading: 50.012 mm
- Uncertainty: ±0.003 mm (±3 μm)
- Confidence: 50.009-50.015 mm range at 95% confidence
```

### CMM Applications

| Application | Typical Points | Tolerance | Time |
|-------------|--------|-----------|------|
| First piece inspection | 20-50 | ±0.05-0.10 mm | 15-30 min |
| 100% critical features | 5-20 | ±0.02-0.05 mm | 5-15 min |
| Sampling inspection | 10-30 | ±0.05-0.10 mm | 10-20 min |
| Complex assemblies | 100-500 | ±0.10-0.50 mm | 30-120 min |
| Reverse engineering | 500-5000 | Digital model | 2-8 hours |

---

## Automated Optical Inspection (AOI)

### AOI System Architecture

```
Production Line Integration:

Production Equipment
        ↓
    Conveyor
        ↓
    ┌─────────────────────────────────┐
    │   AOI System                    │
    ├─────────────────────────────────┤
    │  • Lighting System (LED arrays)  │
    │  • Camera (2K-8K resolution)     │
    │  • Optics (lens, focus motor)    │
    │  • Image Processing (GPU)        │
    │  • Software (templates, rules)   │
    └─────────────────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │   Decision Logic                │
    ├─────────────────────────────────┤
    │  • PASS → Continue to next station
    │  • FAIL-HIGH CONF → Reject
    │  • FAIL-LOW CONF → Manual review
    └─────────────────────────────────┘
        ↓
    ┌─────────────────────────────────┐
    │   Sorting Mechanism             │
    ├─────────────────────────────────┤
    │  • Pneumatic diverter arm       │
    │  • Conveyor sorter gate         │
    │  • Robot pick-and-place         │
    │  • Chute sorting                │
    └─────────────────────────────────┘
        ↓
    Good parts: Packaging
    Failed parts: Rework/Scrap bin
```

### Lighting Systems

**LED Lighting Characteristics:**

```
Wavelength Selection:
- UV (365 nm): Fluorescence, hidden defects
- Blue (450 nm): High contrast for dark surfaces
- Green (530 nm): Balanced visibility
- Red (625 nm): Subtle color variations
- IR (850 nm): Visible through packaging

Ring Lighting (Most Common):
- 52-100 mm diameter ring
- Uniform illumination around part
- Minimal shadows
- Brightness: Adjustable 0-100%

Coaxial Lighting:
- Light through optics to subject
- Reflection back through optics
- Best for flat, reflective surfaces
- Excellent depth visibility

Backlighting:
- Light from opposite side of camera
- Excellent for edge detection
- Silhouette inspection
- Good for checking completeness
```

### AOI Defect Detection Algorithms

#### Template Matching

```
Algorithm: Normalized Cross-Correlation (NCC)

Process:
1. Capture image of known-good reference part
2. Define region of interest (ROI)
3. For each new part image:
   - Cross-correlate reference template with image
   - Calculate correlation coefficient (0-1 scale)
   - If correlation > threshold (e.g., 0.95): PASS
   - If correlation < threshold: Defect detected

Advantage: Simple, fast, reliable for consistent parts
Disadvantage: Fails with part rotation or scale changes
```

#### Edge Detection

```
Algorithm: Canny Edge Detection or Sobel Filter

Process:
1. Convert image to grayscale
2. Calculate image gradient (changes in brightness)
3. Apply non-maxima suppression (thin edges)
4. Apply hysteresis thresholding (connect edges)
5. Compare detected edges to expected edges

Example: PCB Trace Width Inspection
- Expected trace width: 0.3 mm ± 0.05 mm
- Detected left edge: X1 pixels
- Detected right edge: X2 pixels
- Width = (X2-X1) × calibration factor
- Status: PASS if within tolerance

Advantage: Works with variations in lighting
Disadvantage: Sensitive to noise
```

#### Color Detection

```
Algorithm: Hue-Saturation-Value (HSV) thresholding

Process:
1. Convert RGB image to HSV color space
2. Define acceptable color range in HSV
3. Create binary mask (color in range = white, outside = black)
4. Count pixels or evaluate region

Example: LED Color Inspection
- Expected red LED: Hue 0-10° or 350-360°
- Saturation: 50-100% (true color)
- Value: >50% (bright enough)
- Detection: >500 pixels with correct color
- Status: PASS if color detected

Advantage: Robust to lighting variations
Disadvantage: Requires careful color calibration
```

#### Pattern Recognition (Machine Learning)

```
Algorithm: Convolutional Neural Network (CNN) or Deep Learning

Process:
1. Train on 1000s of images (good and defective examples)
2. Network learns to recognize defect patterns
3. For each new image:
   - Forward pass through network
   - Output: Defect class and confidence score
   - If confidence > threshold: Report defect
   - Collect feedback for model improvement

Example: Solder Joint Quality
- Good joint: Shiny, smooth, appropriate height → 98% confidence
- Cold joint: Dull, grainy appearance → 92% confidence
- Bridge: Two joints connected → 99% confidence
- Insufficient solder: Rough, incomplete → 95% confidence

Advantages: Handles complex, variable defects
Disadvantages: Requires training data, slower processing
```

### AOI Defect Examples

#### PCB Assembly (Wave Solder Exit)

**Defect Types Detected:**

```
1. Solder Bridges
   Definition: Unwanted solder connection between traces
   Severity: Critical (short circuit)
   Detection: Edge detection finds continuous path between
              pads that shouldn't connect
   Rate: 0.3-0.8% typical

2. Cold Solder Joint
   Definition: Dull, grainy solder without proper wetting
   Severity: High (intermittent connection)
   Detection: Texture analysis - grainy appearance differs
              from shiny appearance
   Rate: 0.2-0.5% typical

3. Missing Component
   Definition: Footprint empty (component not placed)
   Severity: Critical (circuit won't function)
   Detection: Template matching - component image missing
              from expected location
   Rate: 0.1-0.3% typical

4. Insufficient Solder
   Definition: Solder fillet too small
   Severity: Medium (weak connection, risk of failure)
   Detection: Edge detection measures fillet size
              against threshold
   Rate: 0.2-0.4% typical

5. Component Tombstoning
   Definition: Component stands on edge instead of flat
   Severity: High (bad connection)
   Detection: Pattern recognition - component outline
              different orientation
   Rate: 0.1-0.2% typical

Overall Statistics:
- False positive rate (good parts rejected): <2%
- Detection rate (actual defects found): >98%
- Throughput: 100-150 parts/minute
- Reject rate: 0.8-2.0% typical
```

#### Injection Molding

**Visual Defects Detected:**

```
1. Surface Scratches
   - Detection: Edge detection finds thin line artifacts
   - Severity: Medium (cosmetic)
   - Threshold: Length >5mm, depth >0.1mm

2. Flash/Mold Seam
   - Detection: Boundary detection at mold parting line
   - Severity: Medium (cosmetic, functional impact)
   - Threshold: Width >0.5mm

3. Voids/Sink Marks
   - Detection: Shadow analysis and texture
   - Severity: Medium (structural weakness)
   - Threshold: Area >5mm²

4. Color Variations
   - Detection: HSV color analysis
   - Severity: Low (cosmetic)
   - Threshold: Hue deviation >15°

5. Incomplete Fill
   - Detection: Edge detection of part boundary
   - Severity: Critical (part non-functional)
   - Threshold: Missing >3% of expected area

Inspection Speed: 2-5 seconds per part
Part Capacity: 720-1800 parts per 8-hour shift
```

### AOI System Performance Metrics

```
Sensitivity (True Positive Rate):
= # Defects Found / Total Actual Defects
= Number detected correctly / Total that should be found
Target: >95%

Specificity (True Negative Rate):
= # Good Parts Accepted / Total Actual Good Parts
= Correctly accepted / Total that should pass
Target: >98%

False Positive Rate:
= # Good Parts Rejected / Total Good Parts
= Incorrectly rejected / Total good parts
Target: <2%

Positive Predictive Value (Precision):
= # Correct Rejects / Total Parts Rejected
= Actual defects / (Actual defects + False positives)
Target: >90%

Example System Performance:
- Sensitivity: 97% (catches 97% of actual defects)
- Specificity: 98.5% (accepts 98.5% of good parts)
- False positive rate: 1.5%
- Precision: 91% (91% of rejects are actually bad)
```

---

## Computer Vision Systems for Dimensional Inspection

### Vision-Based Measurement Principles

```
Measurement Chain:
1. Scene → 2. Optics → 3. Sensor → 4. Image → 5. Processing → 6. Result

1. Scene: Physical part with features to measure
2. Optics: Lens focuses image on sensor plane
3. Sensor: Camera converts light to digital data
4. Image: Grid of pixels (e.g., 1920×1080)
5. Processing: Software detects features, calculates dimensions
6. Result: Measurement report with dimensions and status
```

### Calibration and Scaling

**Pixel-to-Millimeter Conversion:**

```
Calibration Process:
1. Place precision calibration standard under camera
   - Optical scale (1 cm with 10 equal divisions)
   - Certified accuracy: ±0.01 mm
2. Capture image of standard
3. Detect edges of known-distance marks
4. Calculate pixels per millimeter:

   PPM = Distance_pixels / Distance_mm

   Example: Standard is 10.00 mm, spans 400 pixels
   PPM = 400 pixels / 10.00 mm = 40 pixels/mm

4. Apply to measurements:
   Dimension_mm = Dimension_pixels / PPM
   = 125 pixels / 40 pixels/mm
   = 3.125 mm
```

**Distortion Correction:**

```
Lens distortion effects:
- Barrel distortion: Image curved outward
- Pincushion distortion: Image curved inward
- Lateral chromatic aberration: Color fringing

Correction:
1. Calibrate with distortion pattern
2. Measure known dimensions at image center and edges
3. Calculate distortion coefficients
4. Apply polynomial correction to all measurements
```

### Feature Detection Algorithms

#### Hole/Circle Detection

```
Algorithm: Hough Circle Transform

Process:
1. Edge detection (Canny filter)
2. For each edge pixel, assume it's on a circle
3. Vote for center coordinates and radius
4. Accumulator array records votes
5. Find peaks (strong votes = actual circles)

Example:
Input: Image of hole in metal plate
Expected: Circle ∅4.50 ±0.20 mm

Detection Results:
- Circle 1: Center (152, 245), Radius 90 pixels
  Diameter = (90 px) × (0.025 mm/px) = 4.50 mm ✓ PASS

Output:
- Diameter: 4.50 ±0.05 mm (measurement uncertainty)
- Position: X=3.80mm, Y=4.70mm (vs. nominal 3.75, 4.75)
- Concentricity to datum: 0.07 mm
```

#### Edge Detection for Linear Features

```
Algorithm: Canny Edge Detection or Sobel

Process for measuring slot width:
1. Detect vertical edges on both sides of slot
2. Find left edge line: X = 45 pixels
3. Find right edge line: X = 85 pixels
4. Width = 85 - 45 = 40 pixels
5. Convert: 40 px × 0.025 mm/px = 1.00 mm

Specification: 1.00 ±0.10 mm
Result: 1.00 mm → PASS

Measurement Uncertainty:
- Edge detection: ±1-2 pixels
- Calibration: ±0.02 mm
- Total: ±0.05 mm
- Confidence: ±0.05 mm at 95%
```

#### 3D Vision for Height/Depth

```
Methods:
1. Structured Light: Project patterns, triangulate
2. Time-of-Flight: Measure light travel time
3. Stereoscopic: Dual camera with triangulation
4. Laser Profiling: Scan with laser line

Example: Solder Joint Height Measurement
- Project laser line across PCB
- Camera captures profile
- Software detects raised surface (solder bump)
- Triangulation calculates height

Results:
- Solder height: 0.35 ±0.05 mm
- Specification: 0.30-0.50 mm
- Status: PASS

Measurement accuracy: ±0.05 mm typical
Speed: 0.5-2 seconds per part
```

### Vision System Application Examples

#### Automotive: Casting Dimension Verification

```
Part: Engine Block Casting
Critical Features:
1. Bore diameters (8 cylinders): ∅86.00 ±0.05 mm
2. Main bearing positions: ±0.20 mm location
3. Bearing bore perpendicularity: <0.10 mm

Vision Inspection Setup:
- High-resolution camera (5 megapixel)
- 50mm lens at 30cm working distance
- Calibration: 0.04 mm per pixel
- Structured light for 3D measurement

Inspection Sequence:
1. Place casting in v-block fixture
2. Automated image capture from 3 angles
3. Circle detection for all 8 bores
4. Calculate center positions and diameters
5. Check perpendicularity using bore depth
6. Generate pass/fail report

Detection Rate: 95% (5% human review for edge cases)
Cycle Time: 15 seconds per part
Cost per part: $0.35

Defects Found:
- Undersized bores: 2.3% of parts
- Location out of spec: 0.8% of parts
- Total defect rate: 3.1%
```

#### Electronics: PCB Assembly Verification

```
Part: Printed Circuit Board Assembly
Inspection Points:
1. Component placement accuracy: ±0.1 mm
2. Solder joint quality: Shine/shape analysis
3. Component presence: Required parts in place
4. Orientation verification: Polarized components correct

Vision System:
- 2K camera at 100-300 mm height
- Segmented illumination (ring + coaxial)
- Image processing at 10+ boards/minute
- Deep learning model trained on 5000+ examples

Results Statistics:
- True positive (defects found): 97.2%
- False positive (good called bad): 1.8%
- False negative (bad called good): 2.8%
- Net quality improvement: 3-5% reduction in escapes

ROI Calculation:
- System cost: $150,000
- Annual throughput: 500,000 boards
- Defect reduction: $200,000 value
- Payback: <1 year
```

### Vision System Limitations

```
Challenges:
1. Reflective surfaces: Specular reflection washes out detail
   Solution: Diffuse coating, polarizing filters

2. Transparency: Glass/clear plastic confuses algorithms
   Solution: Structured light, backlighting

3. Color sensitivity: Requires careful calibration
   Solution: Multi-spectral imaging, machine learning

4. Speed: Processing time limits throughput
   Solution: GPU acceleration, parallel processing

5. Occlusion: Part features hidden from view
   Solution: Multiple camera angles, structured light

6. Lighting variation: Environmental changes affect results
   Solution: Controlled LED lighting, exposure control

Typical Accuracy: ±0.1-0.5 mm
Best achievable: ±0.05 mm with optimized setup
Not suitable for: <0.05 mm tolerances (use CMM instead)
```

---

## Inspection Method Selection Guide

| Tolerance | Method | Speed | Cost | Suitability |
|-----------|--------|-------|------|------------|
| ±0.02 mm | CMM | 10-30 min/part | High | Critical, high-value |
| ±0.05 mm | CMM or Vision | 5-15 min/part | Medium-High | Precision parts |
| ±0.10 mm | Vision preferred | 2-5 sec/part | Medium | High-volume |
| ±0.20 mm | Vision or AOI | <2 sec/part | Low-Medium | Mass production |
| ±0.50 mm | AOI preferred | <1 sec/part | Low | Cosmetic/assembly |

## References

- Mitutoyo CMM User Guide
- National Instruments Vision Toolkit Documentation
- AOI System Manufacturers: Cyberscan, Cohu, Koh Young
- ASME B89.4.10 (CMM Performance Evaluation)
- ISO 15530 (CMM Measurement Uncertainty)
