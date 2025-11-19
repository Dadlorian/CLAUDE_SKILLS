# Robot Types Reference Guide

## Comprehensive Classification and Specifications

---

## 1. Articulated/6-Axis Robots

### Overview
The most versatile industrial robot type with six rotational joints providing complete workspace flexibility and high maneuverability.

### Architecture
- **Joint 1 (Base):** ±180° (full rotation)
- **Joint 2 (Shoulder):** ±180° (lift arm up/down)
- **Joint 3 (Elbow):** ±180° (bend arm forward/backward)
- **Joint 4 (Wrist 1):** ±400° (rotate wrist)
- **Joint 5 (Wrist 2):** ±180° (bend wrist)
- **Joint 6 (Wrist 3):** ±400° (rotate tool)

### Specifications by Manufacturer

#### ABB IRB Series

**IRB 6700 (Heavy-Duty)**
- **Payload:** 85-300 kg
- **Reach:** 2.85-3.2 m
- **Speed:** ±180°/s maximum joint velocity
- **Repeatability:** ±0.05 mm
- **Applications:** Heavy material handling, machine tending
- **IP Rating:** IP54 standard, IP67 option
- **Mounting:** Floor, wall, ceiling, overhead

**IRB 1200 (Compact)**
- **Payload:** 3-7 kg
- **Reach:** 900 mm
- **Speed:** 550°/s wrist rotation
- **Repeatability:** ±0.03 mm
- **Applications:** Assembly, welding, inspection
- **Advantages:** Space-saving, high speed-to-size ratio

**IRB 14000 (High-Speed Assembly)**
- **Payload:** 20-60 kg
- **Reach:** 1.45-1.6 m
- **Speed:** ±400°/s joint velocity
- **Repeatability:** ±0.03 mm
- **Applications:** High-speed assembly, machine tending

#### FANUC M-Series

**M-900i/260 (Large Payload)**
- **Payload:** 100-260 kg
- **Reach:** 2.794 m
- **Max Speed:** ±200°/s
- **Repeatability:** ±0.15 mm
- **Applications:** Heavy machine tending, forging
- **Special Features:** Hollow wrist for cable routing

**M-10iD/10 (Sealed for Cleanroom)**
- **Payload:** 10 kg
- **Reach:** 1.44 m
- **Speed:** ±200°/s
- **Repeatability:** ±0.03 mm
- **Applications:** Semiconductor, pharmaceutical, cleanroom
- **IP Rating:** IP67, fully sealed construction

**M-430iA/4L (Stainless Steel)**
- **Payload:** 3-4 kg
- **Reach:** 1.38 m
- **Speed:** ±400°/s wrist
- **Repeatability:** ±0.03 mm
- **Applications:** Food, beverage, washdown environments
- **Material:** Stainless steel construction

#### KUKA KR Series

**KR QUANTEC (Heavy Payload)**
- **Payload:** 120-210 kg
- **Reach:** 2.1-2.7 m
- **Max Speed:** ±200°/s
- **Repeatability:** ±0.15 mm
- **Applications:** Forging, foundry, material handling
- **Robustness:** Heavy-duty sealed design

**KR AGILUS (High-Speed)**
- **Payload:** 3-16 kg
- **Reach:** 0.695-1.7 m
- **Speed:** ±450°/s wrist
- **Repeatability:** ±0.03 mm
- **Applications:** Assembly, welding, machine tending
- **Accessibility:** Excellent visibility, easy teaching

**KR iontec (Cleanroom Capable)**
- **Payload:** 3-5 kg
- **Reach:** 0.9-1.45 m
- **IP Rating:** IP66, fully sealed
- **Applications:** Semiconductor, medical, cleanroom
- **Material:** Stainless steel available

#### Yaskawa Motoman Series

**HC10DTP (Dual Arm)**
- **Payload:** 10 kg per arm
- **Reach:** 1.4 m per arm
- **Repeatability:** ±0.05 mm
- **Applications:** Dual-arm assembly, bimanual tasks
- **Synchronized Motion:** Coordinated arm control

**MH24 (Heavy Payload)**
- **Payload:** 24 kg
- **Reach:** 1.8 m
- **Speed:** ±200°/s
- **Repeatability:** ±0.05 mm
- **Applications:** Machine tending, material handling

### Performance Characteristics

| Metric | Small | Medium | Large |
|--------|-------|--------|-------|
| Payload | 3-10 kg | 15-60 kg | 100-300 kg |
| Reach | 900-1400 mm | 1.4-2 m | 2.5-3.2 m |
| Speed | 200-400°/s | 150-250°/s | 100-200°/s |
| Accuracy | ±0.03mm | ±0.05mm | ±0.1-0.15mm |
| Footprint | Compact | Medium | Large |
| Cost | ~$100-150k | ~$150-300k | ~$300-600k+ |

### Advantages
- Versatile for multiple applications
- Excellent workspace coverage
- Well-established technology
- Extensive programming support
- Wide range of sizes and capabilities
- Good speed-to-accuracy ratio

### Disadvantages
- Complex kinematics and inverse kinematics
- Subject to singularities
- Requires skilled programmers
- More vibration than Cartesian
- Higher maintenance complexity
- Longer programming time

---

## 2. SCARA (Selective Compliance Assembly Robot Arm)

### Overview
Four-degree-of-freedom robot optimized for high-speed, lateral movement with vertical Z-axis simplicity.

### Architecture
- **Joint 1 (Base):** Rotational, full 360° or 270°
- **Joint 2 (Shoulder):** Rotational, ±180°
- **Joint 3 (Elbow):** Rotational, ±180°
- **Z-Axis:** Linear vertical motion
- **Wrist:** Optional additional rotation for tool orientation

### Specifications by Manufacturer

#### Stäubli TX2-HE Series

**TX2-90HE (Compact)**
- **Payload:** 2 kg
- **Reach:** 900 mm
- **Cycle Time:** 0.4-0.5 seconds (pick-and-place)
- **Repeatability:** ±0.02 mm
- **Speed:** 3 m/s horizontal velocity
- **Vertical Range:** 400 mm Z-motion
- **Applications:** PCB assembly, microelectronics, small parts

**TX2-160HE (Medium)**
- **Payload:** 10 kg
- **Reach:** 1600 mm
- **Cycle Time:** 0.8-1.0 seconds
- **Repeatability:** ±0.03 mm
- **Speed:** 4 m/s horizontal
- **Applications:** Electronics assembly, insert molding

#### EPSON T3 Series

**T3 (Compact Desktop)**
- **Payload:** 0.5-1 kg
- **Reach:** 300 mm
- **Cycle Time:** 0.35 seconds
- **Repeatability:** ±0.01 mm
- **Desktop mounted**
- **Perfect for:** Precision small parts
- **Cost:** Entry-level, ~$50-80k

**T6 (Larger Reach)**
- **Payload:** 2-3 kg
- **Reach:** 600 mm
- **Cycle Time:** 0.45 seconds
- **Repeatability:** ±0.02 mm
- **Applications:** Mid-range assembly

#### Omron VIPER Series

**VIPER S400**
- **Payload:** 0.5 kg
- **Reach:** 400 mm
- **Cycle Time:** 0.4 seconds
- **Repeatability:** ±0.02 mm
- **Compact footprint**
- **Ideal for:** High-mix assembly lines

**VIPER S650**
- **Payload:** 2 kg
- **Reach:** 650 mm
- **Cycle Time:** 0.5 seconds
- **Repeatability:** ±0.02 mm
- **Medium-sized applications**

### Performance Characteristics

| Metric | Small | Large |
|--------|-------|-------|
| Payload | 0.5-2 kg | 5-10 kg |
| Reach | 300-600 mm | 900-1600 mm |
| Cycle Time | 0.3-0.5 sec | 0.5-1.0 sec |
| Repeatability | ±0.01-0.02mm | ±0.02-0.03mm |
| Mounting | Desktop/Table | Floor mount |
| Cost | ~$60-120k | ~$150-250k |

### Typical Applications

1. **Electronics Assembly**
   - Component placement on PCBs
   - Connector insertion
   - Micro-soldering assistance

2. **Small Parts Fastening**
   - Screw driving
   - Nut running
   - Snap assembly

3. **Insert Molding**
   - Part placement in molds
   - Extraction after molding
   - High-speed cycling

4. **Inspection and Testing**
   - Product transfer between stations
   - Test fixture loading

### Advantages
- Extremely fast for lateral movements
- Simple linear vertical motion
- Very high repeatability
- Compact footprint
- Ideal for assembly
- Lower cost than 6-axis for specific applications
- Easy to program (XY motion intuitive)

### Disadvantages
- Cannot perform tool reorientation
- Limited vertical reach
- Cannot work overhead
- Limited to 2.5-3D tasks
- Cannot pick from variable heights
- Reduced workspace flexibility

---

## 3. Delta/Parallel Robots

### Overview
Ultra-high-speed robots with three parallel arms, ideal for rapid pick-and-place operations with minimal footprint.

### Architecture
- **Base Motor 1, 2, 3:** Three independent motors
- **Parallel Links:** Maintain end-effector orientation
- **Work Plane:** Limited vertical range, typically 300-500 mm
- **Speed:** Linear velocity up to 10 m/s

### Specifications by Manufacturer

#### ABB DELTA Series

**ABB IRB 360**
- **Payload:** 1-3 kg
- **Reach:** 800-1200 mm diameter workspace
- **Speed:** 200+ picks per minute for standard tasks
- **Cycle Time:** 0.3-0.4 seconds per pick
- **Repeatability:** ±1 mm
- **Vertical Range:** 250-400 mm
- **Applications:** Food sorting, pharmaceutical packaging, electronics

**ABB IRB 4600-45/2.05**
- **Payload:** 10 kg
- **Reach:** 2050 mm diameter
- **Speed:** 30+ picks per minute (heavier payload)
- **Repeatability:** ±2 mm
- **Applications:** Large item handling, larger package assembly

#### Stäubli DELTA

**Stäubli TX2-90 DELTA**
- **Payload:** 2 kg
- **Reach:** 900 mm diameter
- **Cycle Time:** 0.4 seconds
- **Repeatability:** ±1 mm
- **Speed:** 3 m/s arm velocity
- **Compact design:** 1.2 m floor footprint

#### FANUC M-3iA Delta

- **Payload:** 0.5-3 kg
- **Reach:** 400-800 mm diameter
- **Cycle Time:** 0.3-0.5 seconds
- **Speed:** 100-150 picks/minute
- **Repeatability:** ±1 mm
- **Perfect for:** Food, pharmaceutical, electronics

### Typical Applications

1. **Food Industry**
   - Candy picking and sorting
   - Bakery item handling
   - Produce sorting by grade
   - Packaging of berries, nuts

2. **Pharmaceutical**
   - Tablet handling
   - Capsule placement
   - Bottle filling assistance
   - Package assembly

3. **Electronics**
   - Component placement at high speed
   - Small circuit board assembly
   - Test item handling

4. **General High-Speed Pick & Place**
   - Any application requiring 50+ picks/minute
   - Space-constrained environments
   - Lightweight items (≤10 kg)

### Performance Benchmarks

| Task | Cycle Time | Picks/Minute |
|------|------------|--------------|
| Standard 100g item | 0.3-0.4 sec | 150-200 |
| 500g item | 0.5-0.7 sec | 85-120 |
| Sorted items | 0.4-0.5 sec | 120-150 |
| Precision placement | 0.6-0.8 sec | 75-100 |

### Advantages
- Fastest robots available for XY motion
- Lightweight design
- Minimal floor space
- Excellent for repetitive tasks
- High reliability
- Simple kinematics
- Lower cost than comparable articulated robots

### Disadvantages
- Very limited payload (1-10 kg typical)
- Fixed work plane height
- Cannot reorient tools
- Difficult to integrate into non-planar workflows
- Limited workspace height
- Cannot perform overhead operations

---

## 4. Cartesian/Gantry Robots

### Overview
Linear motion systems providing orthogonal X, Y, Z movement with high rigidity and payload capacity.

### Architecture
- **X-Axis:** Horizontal lateral motion (typically 1-10 m travel)
- **Y-Axis:** Horizontal longitudinal motion (typically 1-5 m travel)
- **Z-Axis:** Vertical motion (typically 0.5-3 m travel)
- **Tool Plate:** Attached to Z-axis slider

### Configurations

#### Wall-Mounted Gantry
- Suitable for: Space-constrained areas
- Advantages: Minimizes floor footprint
- Disadvantages: Limited reach in certain directions

#### Floor-Standing Gantry
- Suitable for: Large workpiece handling
- Advantages: Maximum stability and reach
- Disadvantages: Requires significant space

#### Ceiling-Suspended Gantry
- Suitable for: Overhead operations
- Advantages: Clear working area below
- Disadvantages: Installation complexity

#### Cantilever (Bridge) Gantry
- Suitable for: Medium reach with floor clearance
- Advantages: Good flexibility
- Disadvantages: Medium cost

### Specifications by Manufacturer

#### Bosch Rexroth Automation

**Linear Motion Systems (Customizable)**
- **Stroke Range:** Up to 10 m per axis
- **Payload:** 10-1000 kg depending on configuration
- **Speed:** 0.5-3 m/s typical
- **Accuracy:** ±1-2 mm
- **Repeatability:** ±0.5 mm
- **Modular design:** Mix and match components

#### PARKER Automation

**Parker Linear Motion**
- **Configurations:** Inline, cartesian, multi-axis
- **Ball Screw:** Precision pre-loaded for accuracy
- **Pneumatic or Electric:** Drive options
- **Integrated Control:** Single motion controller

#### Siemens Linear Motion

**Siemens Kinematics**
- **IP65 Sealed:** Environmental protection
- **Integrated Electronics:** Built-in drives
- **Networking:** PROFIBUS/EtherCAT integration
- **Modularity:** Customizable axis configurations

### Typical Applications

1. **CNC Machine Tool Interaction**
   - Loading/unloading parts
   - Tool changing
   - Coolant application

2. **Waterjet/Laser Cutting**
   - Multi-directional cutting paths
   - Large part handling
   - Precision positioning

3. **Heavy Part Assembly**
   - Large sheet metal fabrication
   - Structural component assembly
   - Welding prep and positioning

4. **Overhead Material Handling**
   - Warehouse operations
   - Factory logistics
   - Heavy part movement

5. **Palletizing Large Items**
   - Building layer-by-layer stacks
   - Handling oversized pallets
   - Warehouse automation

### Performance Characteristics

| Metric | Compact | Medium | Large |
|--------|---------|--------|-------|
| Payload | 100-500 kg | 500-2000 kg | 2000-5000+ kg |
| Stroke (Total) | 5-15 m³ | 20-100 m³ | 100+ m³ |
| Speed | 1-2 m/s | 0.5-1.5 m/s | 0.3-1 m/s |
| Accuracy | ±1-2 mm | ±2-5 mm | ±5-10 mm |
| Repeatability | ±0.5 mm | ±1 mm | ±2-3 mm |
| Cost | ~$150-300k | ~$300-800k | ~$800k-2M+ |

### Advantages
- No complex kinematics (linear programming)
- High rigidity for heavy loads
- Predictable motion paths
- Easy to troubleshoot
- Simple safety implementation
- Suitable for harsh environments
- Easy integration with multiple tools

### Disadvantages
- Large footprint
- Cannot perform complex reorientation
- Limited speed compared to articulated
- Requires significant factory space
- Cable management complexity
- Higher initial cost for custom configurations

---

## 5. Collaborative Robots (Cobots)

### Overview
Robots designed and certified for safe human-robot collaboration with force/torque sensing and built-in safety.

### Key Differentiators
- **Force Limiting:** Built-in torque limits at each joint
- **Speed Restrictions:** Maximum operating speeds
- **Soft Exterior:** Rounded edges with impact-absorbing pads
- **Safety Certifications:** ISO/TS 15066 compliance
- **Ease of Use:** Intuitive teach pendants and drag-and-drop programming

### Major Manufacturers

#### Universal Robots (UR)

**UR3**
- **Payload:** 3 kg
- **Reach:** 500 mm
- **Speed:** 1 m/s maximum collaborative speed
- **Repeatability:** ±0.03 mm
- **Max Force:** 150 N impact protection
- **Applications:** Small part assembly, precision tasks
- **Programming:** Python-like URScript, graphical interfaces
- **Cost:** ~$35-50k

**UR5**
- **Payload:** 5 kg
- **Reach:** 850 mm
- **Speed:** 1 m/s collaborative speed
- **Repeatability:** ±0.03 mm
- **Max Force:** 200 N collaborative
- **Applications:** General assembly, machine tending
- **Payload/Reach:** Balanced for most applications
- **Cost:** ~$40-55k

**UR10e**
- **Payload:** 10 kg
- **Reach:** 1300 mm
- **Speed:** 1 m/s collaborative
- **Repeatability:** ±0.05 mm
- **Max Force:** 300 N collaborative
- **Applications:** Heavy assembly, material handling
- **Industrial Speed Mode:** 2 m/s when guarded
- **Cost:** ~$50-70k

**UR20 (New - Larger Payload)**
- **Payload:** 20 kg
- **Reach:** 1750 mm
- **Speed:** 1.3 m/s collaborative
- **Repeatability:** ±0.05 mm
- **Applications:** Palletizing, heavy assembly
- **Cost:** ~$70-90k

#### ABB GoFa Series

**ABB GoFa 3**
- **Payload:** 3-5 kg
- **Reach:** 790 mm
- **Collaborative Speed:** 1 m/s
- **Force Limit:** 150 N
- **Design:** Integrated safety, rounded surfaces
- **Cost:** ~$40-55k

**ABB GoFa 5**
- **Payload:** 5-10 kg
- **Reach:** 1300 mm
- **Collaborative Speed:** 1 m/s
- **Force Limit:** 220 N
- **Applications:** General assembly, packaging
- **Cost:** ~$50-70k

**ABB GoFa 10**
- **Payload:** 10 kg
- **Reach:** 1300 mm
- **Collaborative Speed:** 1 m/s
- **Force Limit:** 300 N
- **Cost:** ~$70-85k

#### FANUC CRX Series

**FANUC CRX-10iA**
- **Payload:** 10 kg
- **Reach:** 1700 mm
- **Speed:** 1 m/s safety-rated
- **Repeatability:** ±0.03 mm
- **Features:** Integrated vision capability
- **Cost:** ~$55-75k

#### KUKA LBR iWA Series

**KUKA LBR iiwa 7 R800**
- **Payload:** 7 kg
- **Reach:** 800 mm
- **Max Speed:** 1 m/s collaborative
- **Torque Sensing:** All 7 joints
- **Force Limit:** 200 N per joint
- **Applications:** Delicate assembly, research
- **Specialized Strength:** Force feedback capabilities
- **Cost:** ~$70-95k

**KUKA LBR iiwa 14 R820**
- **Payload:** 14 kg
- **Reach:** 820 mm
- **Max Speed:** 1 m/s collaborative
- **All-Joint Torque Sensing:** High sensitivity
- **Cost:** ~$90-120k

#### Techman Robot (TM)

**TM5-900 Series**
- **Payload:** 4-5 kg
- **Reach:** 900 mm
- **Speed:** 1 m/s collaborative
- **Vision-Integrated:** Built-in 2D camera
- **Cost:** ~$38-52k (most affordable option)

**TM14 Series**
- **Payload:** 10-14 kg
- **Reach:** 1400 mm
- **Speed:** 1 m/s collaborative
- **Vision:** Integrated camera for pick-and-place
- **Cost:** ~$55-70k

### Collaborative Safety Features

| Feature | Purpose | Mechanism |
|---------|---------|-----------|
| Joint Torque Limiting | Prevent excessive force | Servo feedback control |
| Speed Limiting | Compliance with ISO/TS 15066 | Software speed caps |
| Force Sensing | Detect collision | F/T sensors on tool/joints |
| Soft Exterior | Reduce impact | Impact-absorbing rubber |
| Hand Guiding | Intuitive teach | Force feedback enables operator control |
| Safety Zones | Area restriction | Vision/laser enforcement |
| Collaborative Mode | Speed/force reduction | Automatic limiting below threshold |

### Advantages Over Industrial Robots
- **Safer:** Certified for human interaction
- **Easier to Program:** Intuitive teach methods
- **Flexible Deployment:** Quick setup and movement
- **Lower Cost:** Often more affordable
- **Training:** Requires less expertise
- **Footprint:** Compact and mobile
- **Payback:** Faster ROI in small-to-medium volume

### Limitations
- **Speed:** Generally slower than industrial equivalents
- **Payload:** Maximum 20 kg currently (market standard)
- **Environment:** Not suitable for harsh conditions
- **Precision:** Generally ±0.03-0.1 mm (adequate for most tasks)
- **Cost per Unit:** Higher cost in high-volume scenarios
- **Customization:** Less customizable than industrial

### Typical Collaborative Applications
1. Small parts assembly with human verification
2. Machine tending in small/medium shops
3. Packaging and palletizing
4. Quality inspection with human judgment
5. Light material handling
6. Finishing operations (polishing, deburring)
7. Research and education

---

## Comparison Matrix

| Metric | 6-Axis | SCARA | Delta | Cartesian | Cobot |
|--------|--------|-------|-------|-----------|-------|
| **Payload Range** | 3-300 kg | 1-10 kg | 1-10 kg | 10-5000+ kg | 3-20 kg |
| **Reach** | 0.9-3.2 m | 0.3-1.6 m | 0.4-2 m | Up to 10m+ | 0.5-1.8 m |
| **Speed** | 200-400°/s | 3-4 m/s | 5-10 m/s | 0.5-3 m/s | 1-2 m/s |
| **Repeatability** | ±0.03-0.15mm | ±0.01-0.03mm | ±1-2 mm | ±0.5-2 mm | ±0.03-0.1mm |
| **Programming** | Complex | Medium | Simple | Very Simple | Very Simple |
| **Footprint** | Medium | Small | Small | Very Large | Small |
| **Cost** | $100-600k | $60-250k | $150-300k | $150-2M+ | $35-120k |
| **Maintenance** | High | Medium | Medium | Medium | Low |
| **Flexibility** | Very High | Medium | Low | Low | High |
| **Human Safety** | Guarded | Guarded | Guarded | Guarded | Collaborative |

---

## Selection Guide

### Choose 6-Axis When:
- Multiple task types required
- Complex tool orientations needed
- Medium to heavy payloads
- Established technology preferred
- Workforce familiar with traditional robots

### Choose SCARA When:
- High-speed lateral movement essential
- Assembly operations dominant
- Space constraints exist
- Light payloads (< 10 kg)
- Very high cycle rates needed

### Choose Delta When:
- Ultra-high speed required (100+ picks/minute)
- Light payloads adequate
- Pick-and-place primary application
- Minimal footprint required
- Food/pharmaceutical industry focus

### Choose Cartesian When:
- Very heavy payloads required
- Large workspace needed
- Simple linear paths acceptable
- Precision in specific axes critical
- Heavy-duty environment
- Overhead operations required

### Choose Cobot When:
- Human collaboration needed
- Easy programming essential
- Quick deployment/redeployment
- Safety critical
- Training minimal required
- Flexible manufacturing environment
- Small-to-medium volume production

