# Collaborative Robot Deployment Guide

## Implementation Strategy for Safe Human-Robot Collaboration

---

## Table of Contents

1. [Cobot Fundamentals](#cobot-fundamentals)
2. [Assessment and Planning](#assessment-and-planning)
3. [Safety Implementation](#safety-implementation)
4. [Programming for Collaboration](#programming-for-collaboration)
5. [Workspace Configuration](#workspace-configuration)
6. [Training and Operations](#training-and-operations)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Cobot Fundamentals

### What Makes a Cobot Different

**Key Distinguishing Features:**

1. **Built-in Safety:**
   - Integrated force/torque sensors in joints
   - Software-based speed/force limiting
   - Cannot exceed safe thresholds
   - Automatic compliance mode

2. **Ease of Use:**
   - Intuitive teach pendant or tablet
   - Drag-and-drop programming
   - Minimal training required (hours vs. days)
   - Visual feedback and diagnostics

3. **Flexibility:**
   - Mobile (on wheeled base option)
   - Quick setup for new tasks
   - No permanent installation needed
   - Easy tool exchange

4. **Cost Structure:**
   - Lower upfront cost ($35-120k)
   - Faster payback period (12-36 months)
   - Reduced integration complexity
   - Lower ongoing support costs

### Cobot Safety Certification

**ISO/TS 15066 Compliance:**

All collaborative robots must meet force and pressure limits:

**Transient Force Limits (collision):**
```
Fingertip:    220 N
Hand:         300 N
Wrist:        220 N
Forearm:      480 N
Upper Arm:    400 N
Shoulder:     400 N
```

**Quasi-Static Force Limits (sustained contact):**
```
Fingertip:    140 N
Hand:         190 N
Wrist:        140 N
Forearm:      210 N
Upper Arm:    200 N
Shoulder:     200 N
```

**Built-in Mechanisms:**

- **Joint Torque Limiting:** Each joint monitors its own torque
- **Software Speed Caps:** Maximum 1-1.3 m/s in collaborative mode
- **Force Feedback:** Real-time monitoring during operation
- **Safe Stop:** Automatic shutdown on collision detection

---

## Assessment and Planning

### Application Evaluation

#### Suitability Scorecard

```
Scoring: 1 (Poor) to 5 (Excellent)

Application Aspect                              Score  Weight  Result
────────────────────────────────────────────────────────────────
1. Task Clarity                                 _      15%     ___
   (Well-defined repeatable task)

2. Cycle Time Flexibility                       _      10%     ___
   (Can accept slower speeds?)

3. Part Presentation                            _      15%     ___
   (Consistent orientation/location)

4. Payload Suitability                          _      15%     ___
   (Part weight < max cobot capacity)

5. Work Space Availability                      _      10%     ___
   (Adequate space for cobot and human)

6. Environmental Conditions                     _      10%     ___
   (Temperature, dust, moisture controlled)

7. Cost Justification                           _      15%     ___
   (ROI analysis supports investment)

────────────────────────────────────────────────────────────────
TOTAL SCORE (weighted sum) ≥ 3.5 = Suitable
```

#### Task Types Ideal for Cobots

**Excellent Fit:**
- Assembly with human verification
- Machine tending with changeover flexibility
- Small-batch manufacturing
- Quality inspection and testing
- Light packaging and palletizing
- Collaborative pick-and-place

**Acceptable Fit:**
- Standalone pick-and-place (with guarding)
- Finishing operations (deburring, polishing)
- Material handling (≤ 20 kg)
- Testing and diagnostics

**Poor Fit:**
- High-volume 24/7 operation (cost ineffective)
- Heavy lifting (> 20 kg regularly)
- Harsh environment (dust, heat, moisture)
- Extremely fast cycle times (< 0.5 seconds)
- Tasks requiring absolute precision (< ±0.1mm)

### Planning Methodology

**4-Phase Implementation:**

**Phase 1: Discovery (Week 1)**
- Document current process
- Identify bottlenecks
- Estimate labor hours saved
- Rough cost estimation
- Task observation and video

**Phase 2: Feasibility (Week 2-3)**
- Detailed time study
- Safety assessment
- Cycle time simulation
- ROI calculation
- Stakeholder interviews

**Phase 3: Pilot (Week 4-8)**
- Obtain cobot rental or purchase
- Temporary setup without major integration
- Program basic task
- Test with real parts
- Gather feedback

**Phase 4: Deployment (Month 2-3)**
- Finalize design
- Permanent installation
- Full integration and testing
- Staff training
- Production launch

---

## Safety Implementation

### Collaborative Workspace Design

#### The Three Modes

**Mode 1: Manual/Teaching**
- Operator physically guides robot
- Speed limit: 0.25 m/s (safety standard)
- Force limit: 150 N maximum
- Button must be held continuously
- Full teaching access available

**Mode 2: Collaborative Execution**
- Robot operates independently
- Speed limit: 1 m/s (ISO/TS 15066)
- Force limiting active on all joints
- Human can work in shared space
- No interlocks required
- Immediate stop if excess force detected

**Mode 3: Autonomous (High-Speed)**
- Traditional industrial mode
- Full speed (up to 2 m/s)
- Standard industrial guarding required
- No human presence allowed
- Faster throughput possible
- Safety fence/interlocks essential

**Mode Selection Logic:**

```
Safety Requirements Assessment
        ↓
Is human continuously present in workspace?
├─ Yes → Collaborative Mode (1 m/s limit)
│        └─ Continue with Mode 2
└─ No → Autonomous Mode Available
         ├─ Do we want highest speed? (Faster throughput)
         │  ├─ Yes → Use Autonomous Mode with guarding
         │  └─ No → Keep Collaborative Mode (more flexible)
         └─ Are frequent changeovers needed?
            ├─ Yes → Collaborative (easier to reprogram)
            └─ No → Can use either
```

### Shared Workspace Configuration

#### Zone Definition

**Typical Cobot Collaborative Cell:**

```
                Operator Area
                    ↓
    ┌──────────────────────────────┐
    │                              │
    │  Cobot Collaborative Zone    │  Force-limited
    │  (1 m/s max, F-limited)      │  Safe for human contact
    │  ┌──────────────────┐        │
    │  │ Operating Area   │        │
    │  │ (cobot + tool)   │        │
    │  └──────────────────┘        │
    │                              │
    │  ↕ Engagement Zone           │
    │  (Where human can guide)     │
    │                              │
    └──────────────────────────────┘
    (Safety Monitored Area)
```

**Zone Types:**

1. **Power Limited Zone (PLZ):**
   - Force and speed limited
   - No additional guarding required
   - Human can work safely
   - Transient forces monitored

2. **Speed Limited Zone (SLZ):**
   - Speed mechanically limited
   - Still requires force monitoring
   - Human contact possible
   - Safeguarded pathway

3. **Monitored Zone (MON):**
   - Monitored by sensors
   - Can have multiple safety zones
   - Transition between modes

#### Spatial Design Examples

**Assembly Station (Human + Cobot):**

```
Worker Position
     ↓
   ┌─────────────────┐
   │     WORKER      │  ← Human can reach in
   │                 │
   │  ┌───────────┐  │
   │  │ COBOT     │  │  ← Force limited
   │  │  (UR5)    │  │
   │  └───────────┘  │
   │                 │
   │  Assembly Table │
   └─────────────────┘

No physical barrier needed!
Force and speed limits sufficient
```

**Machine Tending (Flexible Approach):**

```
Optional Partial Guard
  (depends on analysis)
        ↓
   ┌────┐
   │    │  ← Access point
   │    │
   ├────┤
   │    │
   │ CNC│  ← Cobot loads/unloads
   │    │
   │    │
   ├────┤
   │    │  ← Access point
   │    │
   └────┘

Cobot collaborative for safety
Machine provides containment
```

### Risk Assessment Process

**Collaboration Risk Factors:**

| Risk Factor | Assessment |
|-------------|-----------|
| Task Repeatability | Highly repetitive? → Lower risk |
| Part Consistency | Uniform parts? → Lower risk |
| Force Required | Light task? → Lower risk |
| Contact Duration | Momentary contact? → Lower risk |
| Visibility | Clear line of sight? → Lower risk |
| Environmental | Clean, controlled? → Lower risk |

**Risk Scoring:**

```
Risk Level = Severity × Probability × Frequency

Low Risk:    ≤ 25  → Collaborative OK
Medium Risk: 26-75 → Limited collaboration or guards
High Risk:   > 75  → Guards required or mode change
```

---

## Programming for Collaboration

### Universal Robots Example (Most Common Cobot)

#### Program Structure

**UR Script Template:**

```python
# Program: Collaborative Assembly
# Task: Load part from feeder, place in fixture
# Collaborative Mode: YES (speed limited to 1 m/s)

def collaborative_task():
  # Variables
  speed = 0.5              # m/s (safe collaborative speed)
  acceleration = 0.2      # m/s²

  # Configuration
  set_tool_voltage(24)
  set_tcp([0, 0, 0.05, 0, 0, 0])  # Gripper 50mm below wrist

  while True:
    # Wait for signal (feeder ready)
    wait_digital_in(0, True, 5.0)  # 5 second timeout

    # Move to approach position
    movej(q=[-1.57, -1.57, 1.57, -1.57, -1.57, 0],
          a=acceleration,
          v=speed)

    # Move to grasp position (linear, controlled speed)
    movel(p=pose_trans(get_actual_tcp_pose(), [0, 0, -0.15, 0, 0, 0]),
          a=acceleration,
          v=speed)

    # Grasp part
    set_digital_out(0, True)      # Gripper close
    wait(0.5)                      # Wait for grasp

    # Retract with force monitoring
    movel(p=pose_trans(get_actual_tcp_pose(), [0, 0, 0.15, 0, 0, 0]),
          a=acceleration,
          v=speed)

    # Move to assembly position
    movej(q=[-0.78, -1.57, 1.57, -1.57, -1.57, 0],
          a=acceleration,
          v=speed)

    # Place part (slow, careful approach)
    movel(p=assembly_pose,
          a=acceleration,
          v=0.3)                  # Even slower for assembly

    # Release and retract
    set_digital_out(0, False)     # Gripper open
    wait(0.3)

    movej(q=[-1.57, -1.57, 1.57, -1.57, -1.57, 0],
          a=acceleration,
          v=speed)

  end
end

# Run the program
collaborative_task()
```

#### Force Control for Collaborative Tasks

**Hand Guiding Mode:**

```python
def hand_guide_mode():
  # Enable force control for manual guidance
  force_mode(
    task_frame=get_tcp_offset(),
    selection_vector=[1, 1, 1, 0, 0, 0],  # Force on X, Y, Z
    wrench=[0, 0, 0, 0, 0, 0],            # No target force (passive)
    type=2,                               # Type 2 = admittance
    limits=[10, 10, 10, 0.5, 0.5, 0.5]   # Force limits (N, Nm)
  )

  # Robot follows hand guidance
  while True:
    # Monitor for withdrawal
    if get_tcp_force()[2] < -5:  # Operator pulling back
      break
    end
    sleep(0.01)
  end

  # Return to normal control
  end_force_mode()
end
```

### ABB Cobot (GoFa) Example

**RAPID Program for Collaborative Work:**

```rapid
MODULE CoboticAssembly

  PROC main()
    ! Define collaborative motion parameters
    VAR speeddata coll_speed := [0.5, 45, 9, 45];
    VAR zonedata coll_zone := z10;

    ! Main collaborative loop
    WHILE TRUE DO
      ! Wait for part ready signal
      WaitDI signal_part_ready, 1;

      ! Move to approach position (safe speed)
      MoveJ approach_pos, coll_speed, coll_zone, tool0;

      ! Linear approach to grasp (even more careful)
      VAR speeddata slow_speed := [0.3, 45, 9, 45];
      MoveL grasp_pos, slow_speed, z5, tool0;

      ! Activate gripper
      SetDO gripper, 1;
      WaitTime 0.5;

      ! Retract with force feedback
      MoveL retract_pos, slow_speed, z5, tool0;

      ! Move to assembly (safe speed)
      MoveJ assembly_pos, coll_speed, coll_zone, tool0;

      ! Slow approach for assembly
      MoveL place_pos, slow_speed, z5, tool0;

      ! Release and retract
      SetDO gripper, 0;
      WaitTime 0.3;
      MoveJ home_pos, coll_speed, coll_zone, tool0;

    ENDWHILE
  ENDPROC

ENDMODULE
```

### KUKA Cobot (LBR) Example

**KRL Program with Force Feedback:**

```kuka
DEF collaborative_assembly()
  DECL FRAME assembly_pose, grasp_pose
  DECL REAL force_limit = 100.0  ! N

  ! Configure collaborative operation
  SetIO("CollaborativeMode", TRUE)

  WHILE TRUE
    ! Wait for signal
    Wait("PartReady")

    ! Move to grasp with normal speed
    PTP(grasp_approach)

    ! Slow approach to part
    LIN(grasp_pose, {VEL 0.3})

    ! Grasp with force feedback
    SetIO("GripperClose", TRUE)
    Wait(0.5)

    ! Retract carefully
    LIN(grasp_approach, {VEL 0.3})

    ! Move to assembly station
    PTP(assembly_approach)

    ! Precise placement
    LIN(assembly_pose, {VEL 0.2})

    ! Release
    SetIO("GripperClose", FALSE)
    Wait(0.3)

    ! Return home
    PTP(home_position)

    ! Increment counter
    counter = counter + 1

  ENDWHILE
END collaborative_assembly
```

---

## Workspace Configuration

### Cobot Reach and Payload Planning

#### Model Selection Table

| Model | Payload | Reach | Max Speed | Collaborative Force |
|-------|---------|-------|-----------|-------------------|
| UR3 | 3 kg | 500 mm | 1 m/s | 150 N |
| UR5 | 5 kg | 850 mm | 1 m/s | 200 N |
| UR5e | 5 kg | 850 mm | 1 m/s | 200 N |
| UR10 | 10 kg | 1300 mm | 1 m/s | 300 N |
| UR10e | 10 kg | 1300 mm | 1 m/s | 300 N |
| UR20 | 20 kg | 1750 mm | 1.3 m/s | 400 N |
| ABB GoFa 3 | 3 kg | 790 mm | 1 m/s | 150 N |
| ABB GoFa 5 | 5 kg | 1300 mm | 1 m/s | 220 N |
| ABB GoFa 10 | 10 kg | 1300 mm | 1 m/s | 300 N |
| KUKA LBR 7 | 7 kg | 800 mm | 1 m/s | 200 N |
| KUKA LBR 14 | 14 kg | 820 mm | 1 m/s | 300 N |

#### Payload Verification

**Calculation:**

```
Available Robot Capacity: 5 kg
- Gripper Weight: 1.2 kg
- Tool Weight: 0.3 kg
- Part Weight: 3.0 kg
──────────────────────
Total Load: 4.5 kg ✓ (Within 5 kg limit)

Safety Factor Verification:
Load / Capacity = 4.5 / 5 = 0.9 (90% utilization)
Recommended: ≤ 80%
Status: ✓ Acceptable
```

### Tool and End-Effector Integration

#### Tool Frame Definition (UR Example)

```python
# Define tool frame for gripper
# Measurements taken from gripper center to TCP point
set_tcp([0.0, 0.0, 0.15, 0, 0, 0])
# X offset: 0 mm (centered)
# Y offset: 0 mm (centered)
# Z offset: 150 mm (down from tool mount to grasp point)
# Rotation: None (vertical orientation)

# Set tool weight for dynamics compensation
set_payload(mass=1.2, cog=[0, 0, 0.075])
# Mass: 1.2 kg
# Center of Gravity: 75 mm below mount point
```

#### Common End-Effector Options

**Parallel Jaw Gripper:**

```
Weight:     0.8-1.5 kg
Payload:    0.5-5 kg
Grip Force: 50-200 N
Cost:       $1,000-3,000
```

**Vacuum Gripper:**

```
Weight:     0.3-0.8 kg
Payload:    0.2-3 kg
Actuation:  Pneumatic (6-8 bar)
Cost:       $500-2,000
```

**Suction Cup with Adapter:**

```
Weight:     0.2-0.5 kg
Payload:    0.5-10 kg (depending on cup size)
Material:   TPE (best for porous surfaces)
Cost:       $100-500
```

### Safety Zone Configuration

#### Teach Pendant Safety Setup

**UR SafeMove Configuration:**

```
1. Define Collaborative Zone:
   - Zone boundaries (XYZ limits)
   - Speed limitation: 1 m/s
   - Force limits: 150N (fingers), 220N (hands)

2. Define Approach Zone:
   - External 0.3-0.5m buffer
   - Monitored by sensor if available
   - Optional speed reduction (1.5 m/s)

3. Define Monitored Stop Zone:
   - Optical safety scanner monitoring
   - Monitored stop rather than full stop
   - Time to stop: 100-200 ms

4. Define Safe Standby Position:
   - Away from human work area
   - Retracted and secure
   - Easy to reach in emergency
```

**Diagram:**

```
         Safety Scanner
         (optional)
              ↓
    ┌─────────────────┐
    │ Monitored Area  │  ← 0.5m buffer
    │ ┌─────────────┐ │
    │ │ Collab Zone │ │  ← Force/speed limited
    │ │  (1 m/s)    │ │     Human can work here
    │ │ ┌─────────┐ │ │
    │ │ │ Operating│ │ │  ← Cobot actual work envelope
    │ │ │  Area    │ │ │
    │ │ └─────────┘ │ │
    │ └─────────────┘ │
    └─────────────────┘
```

---

## Training and Operations

### Operator Training Program

**Training Duration:** 4-8 hours per operator

**Curriculum:**

**Module 1: Safety Fundamentals (30 minutes)**
- ISO/TS 15066 overview
- Collaborative robot limitations
- Force and pressure thresholds
- Emergency stop procedures
- When collaborative mode is safe

**Module 2: Teach Pendant Operation (1 hour)**
- Moving robot with teach pendant
- Speed adjustment
- Workspace awareness
- Using hand-guiding feature
- Reading status displays

**Module 3: Program Execution (30 minutes)**
- Starting automated program
- Program selection
- Monitoring operation
- Responding to errors
- Using pause/resume functions

**Module 4: Basic Troubleshooting (1 hour)**
- Common error codes
- Power cycling procedure
- Gripper troubleshooting
- Vision system calibration (if applicable)
- When to call for support

**Module 5: Maintenance Awareness (30 minutes)**
- Daily inspection checklist
- Lubrication requirements
- Cable management
- Reporting equipment issues
- Preventive maintenance awareness

**Module 6: Hands-On Practice (2 hours)**
- Supervised operation with trainer
- Multiple cycle execution
- Error recovery practice
- Emergency procedures
- Confidence building

### Daily Operating Checklist

**Pre-Operation (5 minutes):**

```
☐ Visual robot inspection (no visible damage)
☐ Check power is ON (lights/indicators active)
☐ Verify no emergency stop is active
☐ Test E-stop button (should stop immediately)
☐ Confirm gripper operates (open/close test)
☐ Check workspace is clear
☐ Confirm vision system green (if applicable)
☐ Start automated program
```

**During Operation:**

```
☐ Monitor first cycle completely
☐ Observe part quality
☐ Check cycle time reasonable
☐ Listen for unusual sounds
☐ Watch for any hesitation in motion
☐ Verify proper part placement
☐ No obstruction in workspace
```

**Post-Operation:**

```
☐ Move robot to safe position
☐ Close gripper (ready for next user)
☐ Note any issues encountered
☐ Log shift production count
☐ Clean workspace
☐ Secure cords and tools
```

### Maintenance Schedule

**Daily Maintenance (5 minutes):**
- Visual inspection for damage
- Test E-stop and safety features
- Verify cycle operation

**Weekly Maintenance (15 minutes):**
- Clean gripper and tool
- Inspect cables for damage
- Check joint movement smoothness
- Calibrate vision system (if applicable)

**Monthly Maintenance (30 minutes):**
- Detailed mechanical inspection
- Lubrication (if required by manufacturer)
- Electrical connections inspection
- Workspace clearance verification

**Annual Maintenance (2-4 hours):**
- Full system diagnostics
- Replace wear items (if needed)
- Complete recalibration
- Update firmware (if available)
- Safety system re-certification

---

## Troubleshooting Common Issues

### Issue: Reduced Speed in Collaborative Mode

**Possible Causes:**
1. Collaborative mode still active (should be 1 m/s limit)
2. Robot detecting force (touching something)
3. Speed limited in program
4. Joint reaching limit

**Diagnosis:**
```
Step 1: Check mode indicator
- If showing "Collaborative" = Expected behavior
- Reduce speed expectation or switch to autonomous mode

Step 2: Check for obstacles
- Move robot manually (hand-guide)
- Feel for resistance
- Remove any obstruction

Step 3: Review program
- Check movel/movej speed parameters
- Increase speed value if appropriate
- Verify zone parameters
```

**Solution:**
```python
# If needing faster motion, ensure proper mode
# Before running high-speed program:

# 1. Verify collaborative mode is OFF
# 2. Ensure guarding is in place
# 3. Clear workspace completely
# 4. Update program speed:

movej(q=target, a=0.5, v=1.5)  # 1.5 m/s (requires guarding)
# vs.
movej(q=target, a=0.5, v=0.5)  # 0.5 m/s (collaborative safe)
```

### Issue: Gripper Not Responding

**Possible Causes:**
1. Gripper solenoid not powered
2. Pneumatic supply disconnected
3. Digital output misconfigured
4. Gripper mechanical jam

**Diagnosis:**
```
Test 1: Check electrical connection
- Verify 24VDC power at gripper
- Continuity test on cable
- Listen for solenoid click

Test 2: Check pneumatic (if applicable)
- Verify air pressure at inlet
- Check for blockage
- Inspect hose connections

Test 3: Manual test
- Try manual gripper operation
- Feel for mechanical resistance
- Inspect for obvious damage
```

**Solution:**

```python
# Troubleshooting program
def test_gripper():
  # Test gripper with diagnostic feedback

  print("Testing gripper close...")
  set_digital_out(0, True)
  wait(1.0)

  pressure = get_analog_in(0)  # If pressure sensor exists
  if pressure < 20:
    print("WARNING: Low gripper pressure")
    # Try again or skip this cycle
  end

  print("Testing gripper open...")
  set_digital_out(0, False)
  wait(1.0)

  print("Gripper test complete")
end
```

### Issue: Vision System Not Detecting Parts

**Possible Causes:**
1. Lighting changed
2. Part orientation changed
3. Camera calibration drifted
4. Camera lens dirty
5. Part out of focus

**Diagnosis:**
```
Visual Check:
☐ Camera lens clean?
☐ Lighting level adequate?
☐ Part clearly visible in live view?
☐ Part within expected location?

Diagnostic Steps:
1. View live image from camera
2. Verify contrast sufficient
3. Check focus manually
4. Test with known-good part
5. Inspect lighting intensity
```

**Solution:**

```python
def vision_troubleshooting():
  # Capture and verify vision data

  # Get live image
  image = capture_image(camera)

  # Calculate brightness
  brightness = calculate_image_brightness(image)

  if brightness < 50:  # Too dark
    print("Image too dark - check lighting")
    adjust_lighting_intensity(+10)
  elif brightness > 200:  # Too bright
    print("Image too bright - reduce lighting")
    adjust_lighting_intensity(-10)
  end

  # Detect parts
  parts = detect_parts(image)

  if len(parts) == 0:
    print("No parts detected")
    print("1. Check camera focus")
    print("2. Verify part position")
    print("3. Recalibrate camera")
  else
    print("Parts detected: ", len(parts))
  end
end
```

### Issue: Erratic Motion

**Possible Causes:**
1. Calibration lost (software)
2. Joint encoder issue
3. Control loop instability
4. Excessive payload on wrist

**Diagnosis:**
```
Initial Check:
☐ Power cycle robot (full shutdown 10 seconds)
☐ Move manually with teach pendant
☐ Feel for smooth motion
☐ Check for grinding sounds

If problem persists:
☐ Run robot diagnostics program
☐ Check joint torques
☐ Verify payload weight
☐ Inspect for mechanical damage
☐ Contact support for full calibration
```

### Issue: Safety Fault Persistent

**Possible Causes:**
1. Safety sensor blocked
2. Wiring fault
3. Safety module failure
4. Software issue

**Diagnosis:**
```
Immediate Actions:
1. Power cycle (full reset)
2. Check all safety sensor indicators
3. Verify no gate/door open
4. Confirm no emergency stop active

If fault returns:
1. Document exact error code
2. Check manufacturer troubleshooting guide
3. Verify all connections are secure
4. Contact technical support
```

---

## Success Metrics

### Key Performance Indicators

**Track and Optimize:**

```
Metric                          Target      Actual
─────────────────────────────────────────────────
Cycle Time                      ±5%         ___
Uptime                          >95%        ___
Product Defect Rate             <2%         ___
Operator Efficiency (%)         >90%        ___
Payback Period (months)         <36         ___
Employee Satisfaction           >4/5        ___
```

### Continuous Improvement

**Monthly Review Process:**

1. **Analyze Data:**
   - Cycle times and trends
   - Error frequency
   - Downtime causes
   - Operator feedback

2. **Identify Issues:**
   - Longest delays
   - Most frequent errors
   - Safety incidents
   - Part quality issues

3. **Implement Improvements:**
   - Program optimization
   - Safety enhancements
   - Gripper changes
   - Lighting adjustments

4. **Verify Results:**
   - Re-measure metrics
   - Compare to baseline
   - Document improvements
   - Plan next phase

---

## Quick Reference Card

```
COLLABORATIVE ROBOT QUICK START

Speed Limits (ISO/TS 15066):
- Teach Mode: 0.25 m/s (always)
- Collaborative: 1.0 m/s (force-limited)
- Autonomous: 2.0+ m/s (guarded)

Force Limits (Contact):
- Transient (collision): 220N (fingertip) to 480N (forearm)
- Quasi-static (sustained): 140N (fingertip) to 210N (forearm)

Emergency:
- Press E-STOP button (all corners)
- Robot stops within 0.5 seconds
- Restart requires manual reset

Safety Check (Daily):
☐ Visual inspection
☐ E-stop test
☐ First cycle observation
☐ Workspace clearance
☐ Gripper operation

Contact Support If:
- Safety fault appears
- Unusual sounds/vibration
- Exceeds cycle time by >10%
- Part quality issues develop
- Any safety concern
```

