# PLC Project Setup Guide - From Concept to Deployment

## Phase 1: Project Planning & Requirements Analysis

### 1.1 Project Specification Document

**Essential Elements:**

```
PROJECT: Production Line Temperature Control System
VERSION: 1.0
DATE: 2024-01-15

1. EXECUTIVE SUMMARY
   Control temperature of drying oven ±2°C across 6 zones.
   Integrate with MES for recipe management.
   Achieve 99.5% uptime for pharmaceutical compliance.

2. SCOPE
   ✓ PLC controller (Siemens S7-1200)
   ✓ 6 temperature sensors (RTD Pt100)
   ✓ 6 heating elements (2kW each)
   ✓ 6 cooling circuits (proportional solenoid valves)
   ✓ Local 7" HMI panel
   ✓ Remote SCADA connectivity
   ✓ Integration with batch MES system

   ✗ Mechanical design (out of scope)
   ✗ Instrument procurement
   ✗ Building electrical modifications

3. REQUIREMENTS

   Functional Requirements:
   FR-1: Maintain temperature within ±2°C of setpoint
   FR-2: Support up to 10 recipes (different profile curves)
   FR-3: Ramp rate configurable (1-10°C/minute)
   FR-4: Alarm for temperature deviation > 5°C
   FR-5: Log all setpoint changes with timestamp/operator ID

   Non-Functional Requirements:
   NFR-1: Response time < 100ms to operator commands
   NFR-2: Scan cycle time ≤ 50ms
   NFR-3: System uptime ≥ 99.5% (per year)
   NFR-4: Support redundant sensors (voting logic)
   NFR-5: FDA 21 CFR Part 11 compliant logging

   Safety Requirements:
   SR-1: Temperature alarm triggers at ±5°C deviation
   SR-2: Heater interlock with cooling (prevent simultaneous ON)
   SR-3: Manual temperature limit: 0-100°C absolute
   SR-4: Emergency shutdown kills all heating/cooling
   SR-5: Watchdog timer monitors PLC health (1 second timeout)

4. CONSTRAINTS
   Budget: $150,000 (hardware + integration)
   Timeline: 3-month project (planning, build, test)
   Environment: Pharmaceutical facility (GMP)
   Regulatory: FDA, EMA validation required
   Ambient: Up to 45°C, 85% RH

5. ACCEPTANCE CRITERIA
   ✓ Factory acceptance test (FAT) passes all functional tests
   ✓ Site acceptance test (SAT) passes in actual environment
   ✓ All 50+ test cases pass
   ✓ Zero critical/major findings in audit
   ✓ Documentation complete and reviewed
   ✓ Training delivered to 20+ operators

6. TECHNICAL ENVIRONMENT
   PLC: Siemens S7-1200 (1215C CPU)
   Programming: TIA Portal v16
   Language: Structured Text (IEC 61131-3)
   SCADA: Siemens WinCC Advanced
   Database: Microsoft SQL Server 2019
   Network: Siemens PROFINET

7. RISKS & MITIGATION
   Risk: Sensor failure undetected
   Mitigation: Implement redundant sensors with voting logic

   Risk: Scope creep (MES integration delays)
   Mitigation: Clearly define MES interface in Phase 2

   Risk: Software bugs in production
   Mitigation: Independent code review, comprehensive testing
```

### 1.2 Hardware List & Specifications

**Bill of Materials (BOM):**

```
┌──────────────────────────────────────────────────────┐
│ CONTROL SYSTEM COMPONENTS                            │
├──────────────────────────────────────────────────────┤

PLC:
├─ Siemens S7-1200 1215C CPU (Qty: 1)
│  ├─ Processor: 1.4 GHz, 8 MB work memory
│  ├─ I/O: 40 digital I/O, 16 analog inputs/outputs
│  ├─ Real-time clock: Yes
│  └─ Data storage: 200 MB SD card
├─ PROFINET communication module (Qty: 1)
├─ Analog input module (4x 4-20mA, 12-bit) (Qty: 2)
└─ Analog output module (4x 0-10V, 12-bit) (Qty: 2)

Sensors (Temperature):
├─ RTD Pt100 (3-wire) (Qty: 6)
│  ├─ Range: -20 to 200°C
│  ├─ Accuracy: ±0.5°C
│  ├─ Response time: 2-3 seconds
│  └─ Transmitter: 4-20mA output, field-mounted
├─ RTD Head assembly with connector (Qty: 6)
└─ Thermowell (stainless steel 1/2" NPT) (Qty: 6)

Actuators (Heating):
├─ Electric heater element (2kW) (Qty: 6)
│  ├─ Voltage: 208-240V 3-phase
│  ├─ Control: Proportional heating element controller
│  └─ Response: Proportional control 0-100%
├─ Proportional control module (Qty: 6)
│  ├─ Input: 0-10V modulation signal
│  ├─ Rated: 20A per circuit
│  └─ Soft-start capable
└─ Contactor (2NO/2NC) (Qty: 6)

Actuators (Cooling):
├─ Proportional solenoid valve (24VDC) (Qty: 6)
│  ├─ Nominal flow: 10 L/min
│  ├─ Response time: < 50ms
│  ├─ Spools: 2 positions (proportional)
│  └─ Spool position feedback: 0-10V linear
├─ Proportional driver (24VDC) (Qty: 6)
│  ├─ Input: 4-20mA or 0-10V
│  ├─ Output: 24VDC proportional current
│  └─ Integrated solenoid driver
└─ Water circulation pump (1.5 kW, 1450 RPM) (Qty: 1)

Safety Equipment:
├─ Emergency stop button (40mm red mushroom) (Qty: 1)
│  ├─ Contact: 2NO/2NC
│  ├─ Rating: Category 3 (ISO 13849-1)
│  └─ Mounted on control cabinet
├─ Temperature limit switch (electromechanical) (Qty: 2)
│  ├─ Setpoint: 95°C (high limit)
│  ├─ Hysteresis: 5°C
│  └─ Function: Disconnect main heater power
├─ Watchdog timer module (24VDC) (Qty: 1)
│  ├─ Timeout: 1 second
│  ├─ Output: Relay 2NO/2NC
│  └─ Testing: Manual test pushbutton
└─ Protective relays (overcurrent, overtemp) (Qty: 2)

Power Distribution:
├─ Main disconnect switch (630A, 3-phase) (Qty: 1)
├─ Main breaker (400A, 3-phase) (Qty: 1)
├─ Control power supply (24VDC, 40A redundant) (Qty: 2)
├─ Heating circuit breaker (30A per phase) (Qty: 3)
├─ Motor circuit breaker (16A) (Qty: 1)
├─ UPS (24V, 20 Ah battery) (Qty: 1)
│  └─ Supports PLC + HMI for 30 minutes
└─ Surge protection (SPD, Type 2) (Qty: 3)

Control Cabinet:
├─ Stainless steel enclosure (800mm × 1000mm × 300mm)
│  ├─ IP65 rating
│  ├─ Thermostat-controlled cooling
│  ├─ Two-door design (power/control separation)
│  └─ Front stainless steel door
├─ DIN rail (35mm, aluminum) (Qty: 4)
├─ Cable management (tray, conduit, grommets)
└─ Interior labeling (terminal blocks, breakers, modules)

HMI Panel (Local):
├─ 7" color touchscreen
│  ├─ Resolution: 800×480
│  ├─ Brightness: 500 nits (high visibility)
│  ├─ IP65 front bezel
│  └─ Multi-touch capable
├─ Software: Siemens KTP700 Mobile Panel
├─ Mounting: Articulated swing arm (eye level)
└─ Security: Password-protected settings screen

Network:
├─ Managed switch (16-port Gigabit)
│  ├─ PROFINET capable
│  ├─ Redundancy support (ring topology)
│  └─ -20 to 60°C industrial
├─ Network cables (Cat6A, shielded M12)
│  ├─ Cabinet to field devices: 100m
│  ├─ All connectors: M12 X-coded
│  └─ Strain relief: M12 angled connectors
├─ SCADA gateway (industrial PC)
│  ├─ Processor: Intel i7 8-core
│  ├─ RAM: 32GB
│  ├─ Storage: 256GB SSD + 1TB HDD
│  ├─ OS: Windows Server 2019 Enterprise
│  ├─ Dual redundant network cards
│  └─ Watchdog timer module
└─ WiFi access point (industrial, 5GHz)
    ├─ Coverage: Manufacturing floor
    ├─ Encryption: WPA3 Enterprise
    └─ Bandwidth: 100 Mbps minimum

Spare Parts (First Year):
├─ Temperature sensors (spare Pt100 heads) (Qty: 2)
├─ Solenoid valves (complete assemblies) (Qty: 1)
├─ Control modules (analog I/O) (Qty: 1)
├─ Network cables (spare shielded pairs) (Qty: 5)
├─ Fuses (assorted electrical ratings) (Qty: 20)
└─ Replacement heater elements (Qty: 2)

TOTAL HARDWARE COST: ~$95,000
```

---

## Phase 2: Development Environment Setup

### 2.1 TIA Portal Installation & Configuration

**Software Stack:**

```
1. Operating System
   ├─ Windows Server 2019 Standard
   ├─ CPU: Intel Xeon 8-core minimum
   ├─ RAM: 32GB recommended (16GB minimum)
   ├─ Storage: 500GB SSD (TIA + projects)
   └─ Patches: Latest Windows update

2. TIA Portal v16 (Totally Integrated Automation)
   ├─ Base package: ~2GB download
   ├─ STEP 7 (PLC programming): Included
   ├─ WinCC (HMI/SCADA): Included
   ├─ Portal Simulation Runtime: Included
   ├─ TIAcloud for cloud integration: Optional
   └─ Licenses: Floating license server (3-seat)

3. Database Layer
   ├─ SQL Server 2019 Express (development)
   └─ SQL Server 2019 Enterprise (production)

4. Additional Tools
   ├─ STEP 7 Simulation (plcsim)
   ├─ Wireshark (network analysis)
   ├─ Git/Version control (Gitea on-premises)
   ├─ Document editor (Office 365 or LibreOffice)
   └─ Code comparison tool (WinMerge)

Installation Steps:
1. Download TIA Portal ISO (30-40GB)
2. Install to dedicated SSD partition
3. Register floating license with activation server
4. Install SQL Server locally for testing
5. Install WinCC Advanced add-on
6. Configure backup to network share
7. Test PLC simulation first project
```

### 2.2 Project Structure & Version Control

**Git Repository Organization:**

```
manufacturing-oven-control/
│
├── .gitignore
│   ├─ TIA Portal temporary files (*.tmp, *.lock)
│   ├─ Binary project files (export only)
│   └─ Sensitive data (passwords, IP addresses)
│
├── README.md
│   └─ Project overview, team contacts, quick start
│
├── STRUCTURE.md
│   └─ This directory layout explained
│
├── docs/
│   ├── Requirements/
│   │   ├── Functional_Requirements.md
│   │   ├── Safety_Requirements.pdf
│   │   ├── Regulatory_Compliance.md
│   │   └── Network_Architecture.pdf
│   │
│   ├── Design/
│   │   ├── Control_Strategy.md
│   │   ├── State_Machine_Diagram.txt
│   │   ├── Sensor_Calibration.xlsx
│   │   └── Loop_Tuning_Parameters.md
│   │
│   ├── Hardware/
│   │   ├── Bill_of_Materials.xlsx
│   │   ├── Wiring_Diagram.pdf
│   │   ├── Terminal_Block_List.xlsx
│   │   └── Electrical_Schematic.dwg
│   │
│   └── Testing/
│       ├── Test_Plan.md
│       ├── Test_Cases.xlsx
│       └── FAT_Report_Template.docx
│
├── src/
│   ├── TIA_Portal_Projects/
│   │   ├── Oven_Control_v1.0/
│   │   │   ├── ProjectData.xml (version info)
│   │   │   │
│   │   │   ├── PLC_Code/
│   │   │   │   ├── Main_Program.st
│   │   │   │   ├── Temperature_Controller.st
│   │   │   │   ├── Safety_Monitor.st
│   │   │   │   ├── Communications.st
│   │   │   │   ├── Alarms_Events.st
│   │   │   │   └── Diagnostics.st
│   │   │   │
│   │   │   ├── Data_Types/
│   │   │   │   ├── SystemStatus.st
│   │   │   │   ├── TemperatureData.st
│   │   │   │   ├── RecipeData.st
│   │   │   │   └── AlarmStructure.st
│   │   │   │
│   │   │   ├── Function_Blocks/
│   │   │   │   ├── PID_Controller.st
│   │   │   │   ├── Sensor_Redundancy.st
│   │   │   │   ├── Temperature_Ramp.st
│   │   │   │   ├── Zone_Controller.st
│   │   │   │   └── Error_Handler.st
│   │   │   │
│   │   │   ├── Global_Variables/
│   │   │   │   ├── Inputs.gvl
│   │   │   │   ├── Outputs.gvl
│   │   │   │   ├── Process_Data.gvl
│   │   │   │   ├── Alarms.gvl
│   │   │   │   └── Configuration.gvl
│   │   │   │
│   │   │   ├── Device_Configuration/
│   │   │   │   ├── Siemens_S7_1200.xml
│   │   │   │   ├── PROFINET_Topology.xml
│   │   │   │   ├── Analog_Modules.xml
│   │   │   │   └── Network_Parameters.xml
│   │   │   │
│   │   │   ├── HMI_Screens/
│   │   │   │   ├── Main_Dashboard.xml
│   │   │   │   ├── Zone_Details.xml
│   │   │   │   ├── Alarms_View.xml
│   │   │   │   ├── Historical_Trends.xml
│   │   │   │   ├── Recipe_Management.xml
│   │   │   │   ├── Settings_Screen.xml
│   │   │   │   └── Diagnostics_Screen.xml
│   │   │   │
│   │   │   └── Alarms_Events/
│   │   │       ├── Critical_Alarms.xml
│   │   │       ├── Process_Alarms.xml
│   │   │       ├── Warning_Messages.xml
│   │   │       └── Informational_Events.xml
│   │   │
│   │   └── Export_History/
│   │       ├── Oven_Control_v1.0_2024-01-15.zip
│   │       ├── Oven_Control_v0.9_2024-01-08.zip
│   │       └── Oven_Control_v0.8_2024-01-01.zip
│   │
│   ├── Python_Scripts/
│   │   ├── requirements.txt
│   │   ├── generate_documentation.py
│   │   ├── parse_tia_xml.py
│   │   ├── modbus_simulator.py
│   │   └── historian_backup.py
│   │
│   └── SQL_Scripts/
│       ├── 01_Create_Historian_DB.sql
│       ├── 02_Create_Alarms_Table.sql
│       ├── 03_Create_User_Accounts.sql
│       ├── 04_Create_Stored_Procedures.sql
│       └── 05_Create_Indexes.sql
│
├── tests/
│   ├── unit_tests/
│   │   ├── test_pid_controller.st
│   │   ├── test_sensor_redundancy.st
│   │   ├── test_alarm_logic.st
│   │   └── test_state_machine.st
│   │
│   ├── integration_tests/
│   │   ├── test_temperature_ramp.md
│   │   ├── test_sensor_failure.md
│   │   ├── test_network_loss.md
│   │   └── test_safety_interlocks.md
│   │
│   └── test_results/
│       ├── FAT_Results_2024-01-20.xlsx
│       ├── SAT_Results_2024-02-10.xlsx
│       └── UAT_Results_2024-03-01.xlsx
│
├── config/
│   ├── production.yml
│   │   ├─ IP addresses
│   │   ├─ Control parameters
│   │   ├─ Alarm thresholds
│   │   └─ Recipe library
│   │
│   └── development.yml
│       ├─ Simulation parameters
│       ├─ Test data
│       └─ Mock addresses
│
├── deployment/
│   ├── Installation_Guide.md
│   ├── Commissioning_Checklist.pdf
│   ├── Startup_Procedure.md
│   ├── Backup_Recovery_Plan.pdf
│   └── Maintenance_Schedule.xlsx
│
└── CHANGELOG.md
    ├─ Version history
    ├─ Feature changes
    ├─ Bug fixes
    └─ Known issues
```

---

## Phase 3: PLC Programming

### 3.1 Program Structure (Siemens S7-1200 Pattern)

**Main Program Execution:**

```
PROGRAM Main
VAR
    (* System states *)
    system_mode : (IDLE, RUNNING, ERROR, MAINTENANCE);

    (* Function block instances *)
    zone_controller_1 : TemperatureController;
    zone_controller_2 : TemperatureController;
    (* ... zones 3-6 ... *)

    safety_monitor : SafetyMonitor;
    alarm_handler : AlarmManager;
    communications : CommunicationsGateway;

    (* Counters *)
    cycle_counter : UDINT := 0;
    heartbeat : INT := 0;
END_VAR

(*  MAIN EXECUTION CYCLE
    Scan time: 50ms (20 Hz)

    0ms  - Input scan (read all sensors)
    5ms  - Process logic (FB calls)
    40ms - Output scan (write all actuators)
    45ms - Communication (PROFINET, Modbus)
    50ms - End of cycle, repeat
*)

BEGIN

    (* SECTION 1: SAFETY MONITORING (first, every cycle) *)
    safety_monitor(
        temperature_inputs := temperature_array,
        e_stop_pressed := IN_E_Stop_Button,
        watchdog_active := IN_Watchdog_Feedback
    );

    (* If safety fault, skip everything else *)
    IF safety_monitor.fault_detected THEN
        disable_all_outputs();
        RETURN;
    END_IF;

    (* SECTION 2: INPUT PROCESSING *)
    (* Read sensor values, apply filtering *)
    FOR zone := 1 TO 6 DO
        temperature_array[zone] := read_temperature_sensor(zone);
        (* Apply low-pass filter to sensor noise *)
        filtered_temp[zone] := apply_filter(temperature_array[zone]);
    END_FOR;

    (* SECTION 3: CONTROLLER ALGORITHMS *)
    (* Call zone controllers *)
    zone_controller_1(
        process_value := filtered_temp[1],
        setpoint := recipe.zone_setpoint[1],
        enable := (system_mode = RUNNING),
        Kp := pid_params.Kp,
        Ki := pid_params.Ki,
        Kd := pid_params.Kd
    );

    (* Repeat for zones 2-6 *)
    zone_controller_2(...);
    (* ... *)

    (* SECTION 4: ALARM & EVENT MANAGEMENT *)
    alarm_handler(
        temperatures := filtered_temp,
        alarm_thresholds := alarm_config,
        operator_acknowledgement := HMI_Alarm_ACK
    );

    (* SECTION 5: OUTPUT GENERATION *)
    (* Write control signals *)
    FOR zone := 1 TO 6 DO
        AO_Heater_Output[zone] := zone_controller[zone].output;
        DO_Heater_Enable[zone] := zone_controller[zone].heater_on;
        AO_Cooler_Output[zone] := zone_controller[zone].cooler_output;
        DO_Cooler_Enable[zone] := zone_controller[zone].cooler_on;
    END_FOR;

    (* SECTION 6: DIAGNOSTICS & LOGGING *)
    (* Log critical events *)
    IF (cycle_counter MOD 10) = 0 THEN  (* Every 500ms *)
        log_process_state(
            timestamp := CURRENT_DATE_AND_TIME(),
            mode := system_mode,
            temperatures := filtered_temp,
            alarms := alarm_handler.active_alarms
        );
    END_IF;

    (* SECTION 7: COMMUNICATIONS *)
    (* PROFINET updates occur automatically via hardware *)
    communications(
        data_to_send := system_state,
        data_received := mbs_received_data
    );

    (* SECTION 8: HOUSEKEEPING *)
    (* Update diagnostics *)
    heartbeat := (heartbeat + 1) MOD 100;
    DO_Heartbeat_LED := (heartbeat < 50);  (* Blink every 5 seconds *)

    cycle_counter := cycle_counter + 1;

END;
```

### 3.2 Temperature Controller Function Block

```
FUNCTION_BLOCK TemperatureController
VAR_INPUT
    process_value : REAL;           (* Current temperature *)
    setpoint : REAL;                (* Target temperature *)
    enable : BOOL;
    Kp : REAL := 2.0;              (* Proportional gain *)
    Ki : REAL := 0.5;              (* Integral gain *)
    Kd : REAL := 0.05;             (* Derivative gain *)
    output_max : REAL := 100.0;
    output_min : REAL := -100.0;
END_VAR

VAR_OUTPUT
    output : REAL;                 (* Control output -100 to +100 *)
    heater_on : BOOL;
    cooler_on : BOOL;
    error : REAL;
END_VAR

VAR
    error_prev : REAL := 0.0;
    error_integral : REAL := 0.0;
    derivative : REAL := 0.0;
    p_term : REAL;
    i_term : REAL;
    d_term : REAL;
    dt : TIME := T#50ms;           (* Scan cycle time *)
    dt_seconds : REAL;
    integral_limit : REAL := 500.0; (* Anti-windup *)
END_VAR

BEGIN

    IF enable THEN
        (* Calculate error *)
        error := setpoint - process_value;

        (* Proportional term *)
        p_term := Kp * error;

        (* Integral term with anti-windup *)
        error_integral := error_integral + error * TIME_TO_REAL(dt) / 1000.0;
        error_integral := MAX(-integral_limit, MIN(error_integral, integral_limit));
        i_term := Ki * error_integral;

        (* Derivative term *)
        dt_seconds := TIME_TO_REAL(dt) / 1000.0;
        IF dt_seconds > 0 THEN
            derivative := (error - error_prev) / dt_seconds;
        ELSE
            derivative := 0;
        END_IF;
        d_term := Kd * derivative;

        (* Combine terms *)
        output := p_term + i_term + d_term;

        (* Limit output *)
        output := MAX(output_min, MIN(output, output_max));

        (* Determine heating/cooling *)
        IF output > 5.0 THEN
            heater_on := TRUE;
            cooler_on := FALSE;
        ELSIF output < -5.0 THEN
            heater_on := FALSE;
            cooler_on := TRUE;
        ELSE
            heater_on := FALSE;
            cooler_on := FALSE;
        END_IF;

        error_prev := error;

    ELSE
        (* Disabled *)
        output := 0.0;
        heater_on := FALSE;
        cooler_on := FALSE;
        error := 0.0;
        error_integral := 0.0;
    END_IF;

END_FUNCTION_BLOCK
```

---

## Phase 4: Testing Strategy

### 4.1 Unit Testing (Code Review)

**Checklist:**

```
✓ PLC Code Review (Peer review of all programs)
  □ Static analysis passed (no warnings)
  □ Variable naming conventions followed
  □ No hardcoded values (use symbolic constants)
  □ Proper error handling (bounds checking)
  □ Comments document non-obvious logic
  □ Safety interlocks correct
  □ No circular dependencies

✓ Data Type Validation
  □ All array accesses within bounds
  □ No type conversion issues
  □ String lengths validated
  □ Enum values legal

✓ Function Block Testing (Standalone)
  □ PID controller output within limits
  □ Sensor redundancy voting works
  □ State machine transitions valid
  □ Alarm generation correct
  □ Edge cases handled (zero divide, overflow)
```

### 4.2 System Testing (Integration)

**Test Environment:**

```
Hardware:
├─ PLC simulator (TIAcloud simulation)
├─ Modbus simulator software
├─ Virtual SCADA server
└─ Test harness (Arduino-based sensor simulator)

Test Sequence:
1. Power-up test
   └─ All sensors read, no errors
   └─ Default values loaded
   └─ Heartbeat active

2. Setpoint change test
   └─ Adjust temperature setpoint
   └─ Verify heating/cooling response
   └─ Check alarm generation
   └─ Validate trend logging

3. Sensor failure test
   └─ Disconnect sensor #1
   └─ Verify redundancy switching
   └─ Alarm generated within 10 seconds
   └─ Control continues on remaining sensors

4. Network communication test
   └─ Modbus TCP read/write tests
   └─ Verify historian data flow
   └─ Test PROFINET redundancy
   └─ Recovery from network loss

5. Alarm test
   └─ Temperature overshoot test
   └─ High alarm triggers at setpoint + 5°C
   └─ Low alarm triggers at setpoint - 5°C
   └─ Alarm acknowledge resets flag
   └─ Audio/visual indicators work

6. Safety interlock test
   └─ Heater and cooler cannot run simultaneously
   └─ Emergency stop cuts power to heater
   └─ Temperature limit (95°C) stops heater
   └─ Watchdog timeout cuts all outputs

7. Performance test
   └─ Scan cycle time < 50ms (measure 100 cycles)
   └─ No memory leaks (run 24 hours simulation)
   └─ CPU utilization < 60%
   └─ Proper prioritization of critical functions
```

### 4.3 Factory Acceptance Test (FAT)

**Purpose:** Verify system meets requirements before shipment

```
FAT Checklist:

HARDWARE VERIFICATION:
□ All equipment present and matches BOM
□ Serial numbers recorded
□ Continuity testing on power circuits
□ Insulation resistance testing (all circuits)
□ Control power supply output voltage ±10%
□ Network communication tests (all nodes reachable)

FUNCTIONAL TESTING:
□ PLC boots successfully
□ All 6 temperature sensors read correctly
  └─ Within ±0.5°C of calibration values
□ Heater control outputs working (0-100%)
□ Cooler control outputs working (0-100%)
□ Emergency stop circuit cuts heater power
□ Watchdog timer generates fault if disabled
□ HMI panel communicates with PLC
□ SCADA server receives data

PERFORMANCE TESTING:
□ Scan cycle time: 45-55ms (target 50ms)
□ Temperature stability: ±1.5°C within 30 minutes
□ Response to setpoint change: < 5 minutes to reach ±2°C
□ Alarm response time: < 10 seconds from fault detection
□ Data logging rate: 1 sample/second sustained

SAFETY TESTING:
□ Temperature limit switch (95°C) disables heater
□ Interlock: Heater and cooler never simultaneous
□ Watchdog timer: 1-second timeout detected
□ Emergency stop: Verified dual-channel
□ Interlocks: All 5 safety functions working

FAT RESULT: PASS / FAIL
Issued by: [Lead Engineer]
Date: [Date]
Signed: [Authorized]
```

---

## Phase 5: Deployment & Commissioning

### 5.1 Pre-Startup Checklist

**48 Hours Before Power-Up:**

```
Safety Review:
□ All electrical connections inspected by certified electrician
□ Ground/bonding resistance < 10 Ohms (all frames)
□ Main disconnect switch clearly labeled
□ Emergency stop button tested (disconnect heater power)
□ Fire suppression system checked (if required)

Hardware Configuration:
□ Temperature sensors: Installed, calibrated, wired
□ Heating elements: Installed, wired to contactor
□ Cooling system: Filled with coolant, tested for leaks
□ Pressure relief: Set to 60 PSI (or per design spec)

Control System:
□ PLC firmware updated to latest version
□ All modules seated in proper slots
□ PROFINET network cards installed
□ IP addresses assigned (documented)
□ Database backups verified on secure location

Communications:
□ PROFINET cable tested (continuity, resistance)
□ Historian server online and responding
□ SCADA client installation verified
□ Modbus simulator reachable from PLC

Documentation:
□ As-built wiring diagram approved
□ Terminal block list verified
□ Software version number recorded
□ Backup copy of PLC program on USB

Power:
□ Main breaker tested (ON/OFF)
□ Control circuit breaker tested (24VDC is ON)
□ UPS battery tested (simulated load)
□ Ground-fault detection armed
```

### 5.2 Startup Procedure (Step-by-Step)

```
PHASE 1: INITIAL POWER-UP (15 minutes)
─────────────────────────────────────────

Step 1: Pre-startup safety briefing
└─ All personnel briefed on hazards
└─ Emergency stop location identified
└─ Observer positions established (safety zone)

Step 2: Main power switch
└─ Set main disconnect to OFF
└─ Wait 30 seconds
└─ Set main disconnect to ON
└─ Verify status lights (green LED on)
└─ Verify no fault signals
└─ Confirm control power is 24VDC ±5%

Step 3: PLC boot sequence
└─ Observe LED sequence (should flash 3 times)
└─ Wait 30 seconds for full boot
└─ Verify PLC status LED is steady green
└─ Check PROFINET LED (blinking = normal)

Step 4: HMI panel startup
└─ 7" touchscreen should power on
└─ Display logo screen first
└─ Navigate to Dashboard screen (5-10 seconds)
└─ Verify all tags visible and refreshing

Step 5: Network communication test
└─ Ping PLC IP address (192.168.1.100)
└─ Confirm SCADA server reaches PLC
└─ Verify historian is recording timestamps
└─ Check network traffic (should be ~50-100 packets/sec)

PHASE 2: CONTROLLED RAMP-UP (30 minutes)
─────────────────────────────────────────

Step 6: Manual mode testing
└─ Set system to MANUAL mode on HMI
└─ Set Zone 1 heater output to 10%
└─ Observe temperature feedback change (should rise slowly)
└─ Monitor PLC scan cycle time (watch for spikes)
└─ Stop heater, observe temperature stabilize

Step 7: Zone-by-zone testing
└─ Repeat Step 6 for all 6 zones
└─ Verify each heater/cooler responds independently
└─ Test cooler (should reduce temperature)
└─ Document actual temperature rise rate (°C per minute)

Step 8: Safety interlock test
└─ Try to turn on heater AND cooler simultaneously
└─ Verify only one activates (others blocked)
└─ Verify interlock prevents simultaneous operation
└─ Test emergency stop button (should cut heater power)

Step 9: Alarm thresholds test
└─ Deliberately heat Zone 1 to 55°C
└─ Wait for HIGH temperature alarm
└─ Verify alarm appears on HMI (red indicator)
└─ Verify audible alarm sounds (if configured)
└─ Test alarm acknowledge button
└─ Verify alarm clears when temperature normalizes

PHASE 3: AUTOMATIC CONTROL (45 minutes)
───────────────────────────────────────

Step 10: Automatic mode test
└─ Set system to AUTOMATIC mode
└─ Load default recipe (constant setpoint 40°C)
└─ Monitor temperature response
└─ Time how long to reach ±2°C of setpoint (should be < 15 min)
└─ Observe stability over 15 minutes
└─ Record PID parameters actually used

Step 11: Temperature ramp profile
└─ Load ramp recipe (e.g., 25°C → 60°C over 10 minutes)
└─ Set ramp rate to 3.5°C/minute
└─ Observe PLC control output ramping
└─ Verify target temperature reached on time
└─ Check for overshoot (should be < 2°C)

Step 12: Long-term stability
└─ Run for 2 hours at constant setpoint
└─ Record temperature data every 1 minute
└─ Calculate average and standard deviation
└─ Verify stability ±1°C over 2-hour period
└─ Monitor for any intermittent errors

PHASE 4: FAULT CONDITION TESTING (30 minutes)
──────────────────────────────────────────────

Step 13: Sensor simulation failures
└─ Disconnect temperature sensor #1
└─ Verify Zone 1 controller switches to backup sensor
└─ Alarm should trigger within 10 seconds (if backup unavailable)
└─ System should continue controlling other 5 zones

Step 14: Network fault simulation
└─ Unplug PROFINET cable (simulate network loss)
└─ Verify PLC continues local control (no SCADA updates)
└─ Verify error message on HMI
└─ Reconnect network
└─ Verify automatic resynchronization (< 30 seconds)

Step 15: Power loss and recovery
└─ Pull main breaker (simulating power loss)
└─ Wait 10 seconds
└─ Restore power
└─ Verify PLC boot completes
└─ Verify all parameters restored (check HMI setpoints)
└─ Verify resume operation (if enabled)

PHASE 5: DOCUMENTATION & HANDOVER (30 minutes)
───────────────────────────────────────────────

Step 16: Record final parameters
└─ Document actual PID parameters used
└─ Record network addresses and hostnames
└─ Print as-built labeling (cabinet terminals)
└─ Take photos of final installation (for reference)

Step 17: Operator training
└─ Show main dashboard features
└─ Explain alarm handling procedure
└─ Demonstrate manual override (if available)
└─ Review emergency shutdown procedure
└─ Practice setpoint changes

Step 18: Handover sign-off
└─ Obtain commissioning engineer sign-off
└─ Obtain manufacturing supervisor acceptance
└─ Provide operation manual (printed + USB copy)
└─ Provide emergency contact information
└─ Schedule follow-up visit (1 week post-startup)

TOTAL TIME: ~2 hours
REQUIRED PERSONNEL:
├─ Commissioning engineer (lead)
├─ PLC programmer (troubleshooting)
├─ Electrical technician
├─ Manufacturing operator (observer)
└─ Safety officer (observer)
```

---

## Phase 6: Post-Deployment Monitoring

### 6.1 First Month Verification

```
Week 1:
├─ Daily system health check
├─ Monitor scan cycle time (should be stable)
├─ Verify no unplanned alarms
├─ Collect temperature log data (verify consistency)
└─ Check historian database growth rate

Week 2:
├─ Temperature stability analysis
│  └─ Calculate average ±1σ over 7 days
│  └─ Verify ±1°C or better at setpoint
├─ Alarm audit
│  └─ Review all alarms logged in historian
│  └─ Verify no spurious alarms
│  └─ Confirm alarm response times
└─ Network performance
   └─ Monitor network latency (should be < 10ms)
   └─ Check for packet loss (should be 0%)

Week 3:
├─ Perform recalibration of temperature sensors
├─ Fine-tune PID parameters (if needed)
└─ Review maintenance logs

Week 4:
├─ Full system test
│  └─ Run complete test scenario (same as FAT)
│  └─ Compare results to baseline
│  └─ Document any drift or changes
├─ Database verification
│  └─ Test backup/restore functionality
│  └─ Verify data integrity
│  └─ Check retention policy (verify no data loss)
└─ Generate Month 1 Report
   ├─ Summary of operation
   ├─ Any anomalies noted
   ├─ Recommended improvements
   └─ Approval signature
```

---

## Document Version: 2.0
**Last Updated:** January 2024
**Reference Standards:** IEC 61508, ISA-95, FDA 21 CFR Part 11
