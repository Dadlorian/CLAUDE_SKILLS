# Robot Programming Languages Reference

## Comprehensive Guide to Industrial Robot Programming Languages

---

## 1. ABB RAPID Programming Language

### Overview
RAPID is ABB's proprietary, structured programming language designed for ABB industrial robots. It offers powerful features for motion control, I/O management, and system integration.

### Language Structure

#### Program Organization

**Modules (.mod files):**
```rapid
MODULE MainModule

  ! Module declarations and variables
  VAR num test_variable;

  ! Procedures
  PROC main()
    ! Main program logic
  ENDPROC

  ! Functions
  FUNC num Calculate()
    ! Return calculation result
  ENDFUNC

ENDMODULE
```

#### Data Types and Variables

**Built-in Data Types:**

```rapid
num     - 32-bit floating point (-1.7e38 to 1.7e38)
int     - 32-bit integer
bool    - Boolean (TRUE/FALSE)
string  - Text strings (max 256 characters)
dnum    - Double precision float (64-bit)

! Structured types
dframe  - Position and orientation (6 values)
pose    - Homogeneous transformation matrix
robotarr - Robot configuration (6 values for joint angles)
```

**Variable Declaration:**

```rapid
VAR num speed := 100.0;           ! Local variable with initialization
CONST num MAX_SPEED := 500.0;     ! Constant
PERS num power_on_time;           ! Persistent (survives power cycle)
TASK PERS num shared_data;        ! Task-level persistent
```

#### Procedures and Functions

**Procedure (No Return Value):**

```rapid
PROC move_to_home()
  MoveJ home_pos, v100, z50, tool0;
  WaitDI signal_in, 1;
ENDPROC
```

**Function (Returns Value):**

```rapid
FUNC num calculate_distance(pos1, pos2)
  VAR num distance;
  distance := Distance(pos1, pos2);
  RETURN distance;
ENDFUNC
```

**Calling Procedures/Functions:**

```rapid
move_to_home;                    ! Call procedure
num dist := calculate_distance(p1, p2);  ! Call function with return
```

### Motion Instructions

#### Joint Motion (MoveJ)

```rapid
! Move using joint interpolation (fastest point-to-point)
MoveJ [[J1, J2, J3, J4, J5, J6], [0, 0, 0, 0]],
      v100,      ! Velocity (% of max)
      z50,       ! Zone (0 = exact point, 50 = blending zone)
      tool0;     ! Tool frame
```

**Speed Modifiers:**
- **v10 - v500:** Percentage of robot's maximum speed
- **v9999:** Default speed from SafeMove configuration
- **v_100, v_200, v_300:** Predefined speeds

**Zone Parameters:**
- **z0:** Stop exactly at waypoint
- **z1, z5, z10, z20, z50, z100, z200:** Progressive blending
- **Fine:** Synonym for z0
- **Fly:** Synonym for z100

#### Linear Motion (MoveL)

```rapid
! Move in straight line in Cartesian space
MoveL current_position, v100, z50, tool0;

! Move to absolute Cartesian position
MoveL [[100, 200, 300], [0, 0, 1, 0]], v100, z50, tool0;

! With specified configuration
MoveL [[100, 200, 300], [0, 0, 1, 0], [0, 0, 0, 0]],
      v100, z50, tool0;
```

#### Circular Motion (MoveC)

```rapid
! Circular motion with intermediate point and end point
MoveC mid_point,     ! Intermediate point
      end_point,     ! End point
      v100,          ! Velocity
      z50,           ! Zone
      tool0;         ! Tool
```

**Use Cases:**
- Arc welding along curves
- Circular assembly patterns
- Smooth curved paths

#### Configuration and Tool Definitions

**Tool Frame Definition:**

```rapid
PERS tooldata tool0 := [
  TRUE,                    ! Tool mounted (TRUE/FALSE)
  [[x, y, z], [q1, q2, q3, q4]],  ! TCP (Tool Center Point)
  [mass, [cog_x, cog_y, cog_z]],  ! Load
  [0, 0, 0, 0, 0, 0]       ! Inertia matrix (mostly 0)
];
```

**Work Object Definition:**

```rapid
PERS wobjdata work0 := [
  FALSE,                   ! Moving object (TRUE/FALSE)
  FALSE,                   ! Coordinate frame
  [[x, y, z], [q1, q2, q3, q4]],  ! Frame orientation
  [[0, 0, 0], [1, 0, 0, 0]]       ! Object frame
];
```

### I/O Operations

#### Digital I/O

```rapid
! Set digital output
SetDO signal_out, 1;        ! Set output HIGH
SetDO gripper_open, 0;      ! Set output LOW

! Read digital input
WaitDI emergency_stop, 1;   ! Wait for input to be HIGH
IF (DInput(sensor_1) = 1) THEN
  ! Perform action
ENDIF
```

#### Analog I/O

```rapid
! Set analog output
SetAO pressure_valve, 50.5;  ! Set to 50.5V or mA

! Read analog input
num sensor_value := AInput(analog_1);
IF sensor_value > 100 THEN
  ! High pressure detected
ENDIF
```

#### Communication

**Socket-Based Communication:**

```rapid
! TCP/IP socket for external communication
VAR socketdev server_socket;

PROC connect_server()
  SocketCreate server_socket;
  SocketConnect server_socket, "192.168.1.100", 5000;
  SocketSend server_socket, "READY";
ENDPROC
```

### Control Flow Structures

#### If-Then-Else

```rapid
IF (condition1) THEN
  ! Execute if TRUE
ELSEIF (condition2) THEN
  ! Execute if condition2 TRUE
ELSE
  ! Execute if all FALSE
ENDIF
```

#### While Loop

```rapid
WHILE (counter < 10) DO
  MoveJ pos\#counter, v100, z50, tool0;
  counter := counter + 1;
ENDWHILE
```

#### For Loop

```rapid
FOR i FROM 1 TO array_size DO
  MoveJ waypoints\#i, v100, z50, tool0;
  ProcessPart;
ENDFOR
```

#### Test Instruction

```rapid
TEST condition
  CASE TRUE:
    ! Execute if TRUE
  CASE FALSE:
    ! Execute if FALSE
ENDTEST
```

### Error Handling

**Error Recovery:**

```rapid
PROC move_with_error_recovery()
  VAR errnum error_code;

  ON ERROR
    ! Error occurred
    error_code := ERRNO;
    IF error_code = ERR_ROBLIMIT THEN
      ! Handle limit violation
      MoveJ safe_position, v100, z50, tool0;
    ELSEIF error_code = ERR_COLLFAULT THEN
      ! Handle collision
      Stop;
    ENDIF
  UNDO

  MoveL target, v100, z50, tool0;

ENDPROC
```

### Advanced Features

**Interrupt Handling:**

```rapid
INTERRUPT handler_name
  SetDO emergency_light, 1;
  MoveJ safe_position, v100, z50, tool0;
  Stop;
ENDINTERRUPT

! Attach interrupt to event
CONNECT interrupt_signal TO handler_name;
WaitEventAT interrupt_signal;
```

**Multitasking (Multiple Programs):**

```rapid
! main_program:
StartTask bg_task;      ! Start background task
MoveJ pos1, v100, z50, tool0;
MoveJ pos2, v100, z50, tool0;

! background_program:
WHILE TRUE DO
  IF DInput(sensor_1) = 1 THEN
    SetDO indicator_light, 1;
  ELSE
    SetDO indicator_light, 0;
  ENDIF
  Wait 0.1;
ENDWHILE
```

---

## 2. FANUC KAREL Programming Language

### Overview
KAREL is FANUC's C-like structured programming language. It offers powerful programming constructs with deep integration to FANUC's teach pendant and motion system.

### Language Structure

#### Program Template

```karel
PROGRAM Program_Name
  ! Variable declarations go here
  VAR
    INTEGER counter;
    REAL position[6];
    BOOLEAN flag;
  END_VAR

  ! Main program body
BEGIN
  counter := 0;
  ! Program logic here
END Program_Name
```

#### Data Types

**Scalar Types:**

```karel
INTEGER   - 32-bit signed integer (-2147483648 to 2147483647)
REAL      - 32-bit floating point (-1.7e38 to 1.7e38)
BOOLEAN   - TRUE or FALSE
CHAR      - Single character
STRING    - Character array (max 256 chars)
```

**Array Types:**

```karel
INTEGER counter_array[10];        ! 1D array
REAL matrix[3][3];                ! 2D array
STRING name_list[100];            ! String array
BOOLEAN flags[50];                ! Boolean array
```

**Record/Structured Types:**

```karel
TYPE / MY_STRUCT
  REAL x;
  REAL y;
  INTEGER status;
END / MY_STRUCT;

VAR
  MY_STRUCT data_point;
END_VAR

! Access fields
data_point.x := 100.5;
```

### User-Defined Functions and Procedures

#### Function (Returns Value)

```karel
PROGRAM Calculate_Distance
  -- Calculate distance between two points
  REAL FUNCTION distance(x1, x2, y1, y2)
    REAL d;
  BEGIN
    d := SQRT((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
    RETURN d;
  END distance

BEGIN
  -- Main program
  REAL d;
  d := distance(0, 3, 0, 4);  -- d = 5
END Calculate_Distance
```

#### Procedure (No Return)

```karel
VOID PROCEDURE move_robot(x, y, z, speed)
  VAR
    REAL target[6];
  END_VAR
BEGIN
  target[1] := x;
  target[2] := y;
  target[3] := z;
  target[4] := 0;
  target[5] := 0;
  target[6] := 0;

  -- Call TP (teach pendant) instruction
  MOVE_TO_POSITION(target, speed);
END move_robot
```

### File I/O Operations

#### File Operations

```karel
PROGRAM File_Operations
  VAR
    FILE f_input, f_output;
    STRING file_line;
    INTEGER char_read;
  END_VAR

BEGIN
  -- Open file for reading
  OPEN_FILE(f_input, '/memotx/my_file.txt', 'RO');

  -- Read lines
  REPEAT
    READ(f_input, file_line);
    -- Process line
  UNTIL (STATUS = FILE_EOF)

  -- Close input file
  CLOSE_FILE(f_input);

  -- Open file for writing
  OPEN_FILE(f_output, '/memotx/output.txt', 'W');

  -- Write data
  WRITE(f_output, 'Robot Status: OK');
  WRITE(f_output, 'Cycle Time: 45.2 seconds');

  -- Close output file
  CLOSE_FILE(f_output);

END File_Operations
```

### Control Flow

#### If-Then-Else

```karel
IF (counter > 10) THEN
  -- Execute if true
  DO_SOMETHING;
ELSE
  -- Execute if false
  DO_SOMETHING_ELSE;
END_IF
```

#### While Loop

```karel
WHILE (counter < 100) DO
  -- Increment counter
  counter := counter + 1;
  -- Some processing
  PROCESS_DATA(counter);
END_WHILE
```

#### For Loop

```karel
FOR i := 1 TO 50 DO
  -- Loop body executes 50 times
  MOVE_TO_POSITION(positions[i], 100);
END_FOR
```

#### Select/Case Statement

```karel
SELECT (part_type) OF
  CASE (1):
    -- Part type 1
    PROCESS_PART_TYPE_1;
  CASE (2):
    -- Part type 2
    PROCESS_PART_TYPE_2;
  CASE (3):
    -- Part type 3
    PROCESS_PART_TYPE_3;
  DEFAULT:
    -- Unknown part
    ERROR('Unknown part type');
END_SELECT
```

### System Variables and Integration

#### Accessing Robot State

```karel
PROGRAM Robot_Status
  VAR
    REAL current_joints[6];
    REAL current_position[6];
    INTEGER robot_status;
  END_VAR

BEGIN
  -- Read current joint angles
  CURRENT_JOINT_ANGLES(current_joints);

  -- Read current Cartesian position
  CURRENT_POSITION(current_position);

  -- Get robot status (0 = moving, 1 = idle)
  robot_status := GET_ROBOT_STATUS();

  -- Log to file
  LOG_MESSAGE('Joints: ' + REAL_TO_STRING(current_joints[1]));

END Robot_Status
```

#### I/O Control

```karel
PROGRAM IO_Control
BEGIN
  -- Set digital output
  SET_DIGITAL_OUT('output_1', TRUE);

  -- Wait for digital input
  WAIT_DIGITAL_INPUT('sensor_1', TRUE, 5.0);  -- 5 second timeout

  -- Read analog input
  REAL pressure := READ_ANALOG_IN('pressure_sensor');

  -- Set analog output
  SET_ANALOG_OUT('valve_control', 50.5);

END IO_Control
```

### Error Handling

**ERROR/FAULT Handling:**

```karel
PROGRAM With_Error_Handling
  VAR
    INTEGER error_num;
  END_VAR

BEGIN
  ERROR error_handler
  -- Protected code
  DO_CRITICAL_OPERATION();

  FAULT fault_handler
  -- Fault occurred
  MOVE_TO_SAFE_POSITION();

END With_Error_Handling

-- Error handler
ROUTINE error_handler
BEGIN
  PRINT_MESSAGE('Error occurred: ' + REAL_TO_STRING(error_num));
  -- Recovery logic
END error_handler

-- Fault handler
ROUTINE fault_handler
BEGIN
  -- Emergency handling
  ABORT;
END fault_handler
```

---

## 3. KUKA KRL Programming Language

### Overview
KRL (KUKA Robot Language) is KUKA's intuitive programming environment with excellent support for force feedback and collaborative operation.

### Program Structure

#### Basic Program

```kuka
DEF program_name()
  ! Variable declarations
  DECL INT counter
  DECL REAL speed
  DECL AXIS home_pos

  ! Initialize variables
  counter = 0
  speed = 100.0

  ! Program logic
  PTP(home_pos)

  ! Subprogram calls
  SubProgram()

END program_name
```

#### Variable Declaration

```kuka
! Axis position (joint angles)
DECL AXIS pos1 = {0, 45, 90, 0, 45, 0}

! Cartesian frame with position and orientation
DECL FRAME pos2 = {
  X 100, Y 200, Z 300,      ! Position in mm
  A 0, B 0, C 45            ! Orientation in degrees
}

! Real number (float)
DECL REAL speed = 50.0

! Integer
DECL INT counter = 0

! Boolean
DECL BOOL run_cycle = TRUE

! Persistent variable (survives power cycle)
DECL GLOBAL REAL saved_value
```

### Motion Instructions

#### Point-to-Point Motion (PTP)

```kuka
! Move via joint interpolation (fastest)
PTP(target_frame)

! With velocity and acceleration
PTP(target_frame, {VEL 100, ACC 50})

! Predefined speeds
PTP(home_pos)              ! Uses default speed
PTP(target, {VEL 80})      ! 80% of max speed
PTP(target, {VEL 0.2 m/s}) ! 0.2 m/s absolute
```

#### Linear Motion (LIN)

```kuka
! Straight line in Cartesian space
LIN(target_position)

! Maintaining orientation
LIN(target_position)
LIN(home_position, {VEL 100, ACC 75})

! Relative motion
LIN({X 10, Y 0, Z 20})  ! Move 10mm X, 20mm Z
```

#### Circular Motion (CIRC)

```kuka
! Arc motion via intermediate point
CIRC(mid_point, end_point)

! With parameters
CIRC(mid_point, end_point, {VEL 50, ACC 80})

! Example: Quarter circle
CIRC({X 100, Y 100, Z 100}, {X 100, Y 200, Z 100})
```

#### Spline Motion (SPLINE)

```kuka
! Smooth curve through multiple points
SPLINE(waypoint1, waypoint2, waypoint3, waypoint4)

SPLINE(
  {X 100, Y 100, Z 100},
  {X 150, Y 150, Z 100},
  {X 200, Y 200, Z 100},
  {X 250, Y 250, Z 100}
)
```

### Control Flow

#### If-Then-Else

```kuka
IF (counter > 10)
  ! Execute if TRUE
  LIN(high_position)
ELSEIF (counter < 5)
  ! Execute if another condition TRUE
  LIN(low_position)
ELSE
  ! Default case
  LIN(medium_position)
ENDIF
```

#### While Loop

```kuka
WHILE (counter < 100)
  counter = counter + 1
  LIN(waypoints[counter])
ENDWHILE
```

#### For Loop

```kuka
FOR i = 1 TO 50
  LIN(target_position)
  counter = counter + 1
ENDFOR
```

### I/O Operations

#### Digital I/O

```kuka
! Set output
SetIO("gripper_open", TRUE)
SetIO("lamp_red", FALSE)

! Wait for input (with timeout)
Wait(10.0, "sensor_detect")  ! 10 second timeout

! Check input state
IF (GetIO("emergency_stop") == TRUE)
  ! Handle emergency
ENDIF
```

#### Analog I/O

```kuka
! Read analog input
REAL pressure = GetAnalogInput("pressure_sensor")

! Set analog output
SetAnalogOutput("pressure_valve", 50.5)

! Conditional on analog reading
IF (pressure > 80.0)
  SetIO("warning_light", TRUE)
ENDIF
```

### Force/Torque Control

#### Force Control Mode

```kuka
! Activate force control on specific axes
ActivateForceControl(
  {X, Y, Z},           ! Axes to control force
  {100, 100, 100}      ! Target forces in N
)

! Move with force feedback
LIN(target_position)

! Deactivate force control
DeactivateForceControl()
```

#### Impedance Control

```kuka
! Set impedance parameters
SetImpedance({
  K_pos 5000,      ! Position stiffness N/mm
  K_vel 500,       ! Damping
  D_max 100        ! Max force before stop
})

! Motion with compliance
LIN(contact_surface)
```

### Subprograms and Functions

#### Subprogram Definition

```kuka
DEF subprogram_name()
  ! Subprogram code
  PTP(position)
  SetIO("output_1", TRUE)
  Wait(1.0)
  SetIO("output_1", FALSE)
END subprogram_name

! Main program calling subprogram
DEF main_program()
  subprogram_name()  ! Call subprogram
  PTP(home_position)
END main_program
```

---

## 4. Universal Robots URScript Programming

### Overview
URScript is a Python-like scripting language for Universal Robots collaborative manipulators. It combines intuitive syntax with powerful robot control capabilities.

### Program Structure

```python
def program():
  # Variable declarations
  speed = 0.5           # m/s
  acceleration = 0.5    # m/s²

  # Robot motion
  movej(q=[0, -1.57, 1.57, -1.57, -1.57, 0], a=acc, v=speed)
  movel(p=pose_trans(get_actual_tcp_pose(), [0, 0, 0.1, 0, 0, 0]), a=acc, v=speed)

  # I/O operations
  set_digital_out(0, True)
  wait(1.0)
  set_digital_out(0, False)

end  # End of program
```

### Data Types and Variables

#### Basic Types

```python
# Floating point
speed = 1.5           # m/s
acceleration = 0.5   # m/s²

# Boolean
gripper_open = True
run_cycle = False

# String
part_type = "Assembly_A"
log_message = "Robot ready"

# List/Array
joint_angles = [0, -1.57, 1.57, -1.57, -1.57, 0]
position = [100, 200, 300]  # mm
```

#### Pose and Transformation

```python
# Get current pose
current_pose = get_actual_tcp_pose()  # [x, y, z, rx, ry, rz]

# Define pose
target_pose = [0.5, 0.2, 0.3, 0, 0, 0]

# Pose transformation (relative motion)
new_pose = pose_trans(
  current_pose,
  [0.1, 0, 0, 0, 0, 0]  # 100mm in X
)

# Inverse kinematics (get joint angles for pose)
q = inverse(target_pose)
```

### Motion Commands

#### Joint Motion (movej)

```python
# Move to joint configuration
movej(q=[0, -1.57, 1.57, -1.57, -1.57, 0], a=0.5, v=0.3)

# q: Joint angles [J1, J2, J3, J4, J5, J6] in radians
# a: Acceleration (m/s² or rad/s²)
# v: Velocity (m/s or rad/s)
# t: Time (optional, overrides a and v)

# With defined speed (safer)
movej(q=home_configuration, a=acc, v=speed)
```

#### Linear Motion (movel)

```python
# Move linearly in Cartesian space
movel(p=[0.5, 0.2, 0.3, 0, 0, 0], a=0.5, v=0.3)

# p: Target pose [x, y, z, rx, ry, rz] in m and rad
# Maintains tool orientation

# Relative linear motion
movel(pose_trans(get_actual_tcp_pose(), [0.1, 0, 0, 0, 0, 0]))
```

#### Circular Motion (movec)

```python
# Arc motion via intermediate and final point
movec(
  pc=[0.4, 0.3, 0.2, 0, 0, 0],  ! Intermediate point
  p=[0.3, 0.4, 0.2, 0, 0, 0],   ! End point
  a=0.5, v=0.2
)
```

#### Motion with Blending

```python
# Smooth path with blending between waypoints
def smooth_path():
  waypoints = [
    [0.3, 0.2, 0.4, 0, 0, 0],
    [0.4, 0.3, 0.4, 0, 0, 0],
    [0.5, 0.2, 0.4, 0, 0, 0]
  ]

  for waypoint in waypoints:
    movel(p=waypoint, a=0.5, v=0.3, r=0.01)  # r=radius for blending
end
```

### I/O Operations

#### Digital I/O

```python
# Set digital output
set_digital_out(0, True)     # Output 0 = HIGH
set_digital_out(1, False)    # Output 1 = LOW

# Read digital input
input_state = get_digital_in(0)

# Wait for digital input
wait_digital_in(0, True, 5.0)  # Wait 5 seconds for input 0 = HIGH

# Conditional I/O
if get_digital_in(0) == True:
  set_digital_out(1, True)
else:
  set_digital_out(1, False)
end
```

#### Analog I/O

```python
# Set analog output
set_analog_out(0, 2.5)  # Output 0 = 2.5V

# Read analog input
pressure = get_analog_in(0)

# Conditional on analog value
if pressure > 80.0:
  set_digital_out("warning", True)
end
```

#### I/O Configuration

```python
# Check input/output state
is_configured = is_io_module_available()

# Set I/O voltage (if supported)
set_io_voltage(24)  ! 24V for outputs
```

### Force/Torque Control

#### Force Mode Control

```python
# Enable force control in specified directions
force_mode(
  task_frame=get_tcp_offset(),              ! Reference frame
  selection_vector=[1, 0, 0, 0, 0, 0],     ! Control X-axis force
  wrench=[50, 0, 0, 0, 0, 0],              ! Target force [Fx, Fy, Fz, Tx, Ty, Tz]
  type=2,                                  ! 2 = impedance control
  limits=[2, 2, 2, 0.5, 0.5, 0.5]         ! Force/torque limits
)

# Move while in force control
movel(p=contact_surface_pose, a=0.1, v=0.05)

# Disable force control
set_standard_analog_input_domain(0)
end_force_mode()
```

#### Tool Force-Torque Sensor Integration

```python
# Get F/T sensor reading (if tool has sensor)
tcp_force = get_tcp_force()  # [Fx, Fy, Fz, Tx, Ty, Tz]

# Monitor force during motion
def force_limited_move():
  max_force = 100  # N

  movel(p=target_pose, a=0.2, v=0.1)

  while is_moving():
    force = get_tcp_force()
    if force[2] > max_force:  ! Force in Z-axis
      stopl(acc=0.5)
      break
    end
    sleep(0.01)
  end
end
```

### Control Structures

#### Conditionals

```python
# If-then-else
if counter > 10:
  set_digital_out(0, True)
elif counter > 5:
  set_digital_out(0, False)
else:
  set_digital_out(1, True)
end

# Multiple conditions
if (part_type == "TypeA") and (counter < 5):
  process_part_A()
end
```

#### Loops

```python
# While loop
counter = 0
while counter < 100:
  movej(q=get_actual_q(), a=0.5, v=0.3)
  counter = counter + 1
  sleep(0.5)
end

# For loop
for i in range(0, 10):
  movel(p=waypoints[i], a=0.5, v=0.3)
end
```

### Program Flow Control

#### Thread Sleep

```python
sleep(2.0)  ! Sleep 2 seconds
```

#### Stop Instructions

```python
# Soft stop (decelerate)
stopl(acc=0.5)

# Hard stop (emergency)
stopj(acc=2.0)

# Program halt
halt()
```

#### Program End

```python
end  ! End of program

# Or with explicit return
exit()
```

### Comments and Documentation

```python
# Single line comment

#
# Multi-line comment
# describing function behavior
#

def documented_function():
  # Variable descriptions
  speed = 0.5        # m/s - end-effector speed
  acceleration = 0.5 # m/s² - acceleration limit

  # Motion description
  movej(q=home_configuration, a=acceleration, v=speed)

  # I/O description
  set_digital_out(0, True)  ! Activate gripper
  wait(1.0)

end
```

---

## Comparison Table

| Feature | RAPID | KAREL | KRL | URScript |
|---------|-------|-------|-----|----------|
| **Manufacturer** | ABB | FANUC | KUKA | UR |
| **Type** | Procedural | Procedural | Imperative | Python-like |
| **Syntax** | Custom | C-like | Custom | Python-like |
| **Functions** | Yes | Yes | Subprograms | Yes |
| **Error Handling** | Yes | Yes | Limited | Exception-based |
| **Force Control** | Limited | Limited | Excellent | Good |
| **Learning Curve** | Medium | High | Low | Low |
| **Integration** | Excellent | Good | Good | Excellent |
| **Simulation** | RobotStudio | RoboGuide | KUKA Sim | Polyscope |
| **Offline Programming** | Yes | Yes | Yes | Yes |

