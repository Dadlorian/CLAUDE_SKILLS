# PLC Programming Quick Reference

## IEC 61131-3 Structured Text (ST) Syntax

### Variable Declarations

```
VAR
    counter : INT := 0;              (* Declaration with initialization *)
    temperature : REAL;
    motor_running : BOOL := FALSE;
    device_name : STRING := 'Pump1';
    device_list : ARRAY [1..10] OF INT;
    timestamp : DATE_AND_TIME;
    on_off_time : TIME := T#500ms;   (* 500 milliseconds *)
END_VAR

VAR_INPUT
    sensor_value : REAL;             (* Read-only input *)
    enable : BOOL;
END_VAR

VAR_OUTPUT
    output_signal : REAL;            (* Write-only output *)
    alarm : BOOL;
END_VAR

VAR_IN_OUT
    shared_data : INT;               (* Can read and modify *)
END_VAR
```

### Data Types

```
(* Elementary Types *)
BOOL        - Boolean (TRUE/FALSE)
SINT        - Signed Byte (-128..127)
INT         - Signed 16-bit (-32768..32767)
DINT        - Signed 32-bit (-2147483648..2147483647)
LINT        - Signed 64-bit
USINT       - Unsigned Byte (0..255)
UINT        - Unsigned 16-bit (0..65535)
UDINT       - Unsigned 32-bit (0..4294967295)
ULINT       - Unsigned 64-bit
REAL        - 32-bit floating point
LREAL       - 64-bit floating point
TIME        - Duration (millisecond precision)
DATE        - Date (days since 1900-01-01)
TIME_OF_DAY - Time within a day (TOD)
DATE_AND_TIME - Combined date and time (DT)
BYTE        - 8-bit (0..255)
WORD        - 16-bit (0..65535)
DWORD       - 32-bit (0..4294967295)
LWORD       - 64-bit
STRING      - Variable-length string

(* Complex Types *)
ARRAY       - Multiple elements of same type
STRUCT      - Multiple elements of different types
ENUM        - Enumerated values
```

### String Operations

```
(* String assignment *)
text : STRING := 'Hello World';

(* String length *)
length := LEN(text);           (* 11 *)

(* Extract substring *)
substring := MID(text, 7, 5);  (* 'World' *)

(* Find substring *)
position := FIND(text, 'World');  (* 7 *)

(* Concatenate strings *)
combined := CONCAT('Status: ', 'RUNNING');

(* String to number conversion *)
value : INT;
value := STRING_TO_INT('123');  (* 123 *)

(* Number to string conversion *)
output : STRING;
output := INT_TO_STRING(counter);
```

### Arithmetic & Logical Operations

```
(* Arithmetic *)
sum := value1 + value2;
difference := value1 - value2;
product := value1 * value2;
quotient := value1 / value2;
remainder := value1 MOD value2;        (* Modulo *)
exponent := value1 ** value2;          (* Power *)

(* Logical *)
AND_result := condition1 AND condition2;
OR_result := condition1 OR condition2;
NOT_result := NOT condition;
XOR_result := condition1 XOR condition2;

(* Comparison *)
is_greater := value1 > value2;
is_less := value1 < value2;
is_equal := value1 = value2;
is_not_equal := value1 <> value2;
is_greater_equal := value1 >= value2;
is_less_equal := value1 <= value2;

(* Bit operations *)
left_shift := value << 2;              (* Shift left *)
right_shift := value >> 2;             (* Shift right *)
bit_and := value1 & value2;
bit_or := value1 | value2;
bit_not := ~value;
```

### Control Structures

```
(* IF-ELSIF-ELSE *)
IF process_state = 'RUNNING' THEN
    output := setpoint * gain;
ELSIF process_state = 'SHUTDOWN' THEN
    output := 0;
ELSE
    output := safe_value;
END_IF;

(* CASE statement *)
CASE device_mode OF
    0:  (* Manual *)
        output := manual_setpoint;
    1:  (* Automatic *)
        output := pid_controller.output;
    2:  (* Standby *)
        output := 0;
    ELSE
        output := ERROR_VALUE;
END_CASE;

(* FOR loop *)
FOR counter := 1 TO 100 DO
    sum := sum + array_data[counter];
END_FOR;

(* FOR loop with step *)
FOR index := 1 TO 50 BY 2 DO
    (* Processes indices: 1, 3, 5, ..., 49 *)
    process_value[index] := 0;
END_FOR;

(* WHILE loop *)
WHILE counter < max_count AND enable DO
    counter := counter + 1;
    accumulate := accumulate + values[counter];
END_WHILE;

(* REPEAT-UNTIL loop *)
REPEAT
    counter := counter + 1;
UNTIL counter >= 100 OR error_detected
END_REPEAT;

(* EXIT statement *)
FOR i := 1 TO 1000 DO
    IF error_condition THEN
        EXIT;
    END_IF;
    process_data[i] := calculate(i);
END_FOR;
```

### Time Operations

```
(* Time literals *)
time_duration : TIME := T#2s500ms;     (* 2.5 seconds *)
time_duration := T#1h30m;              (* 1.5 hours *)
time_duration := T#5d;                 (* 5 days *)

(* Date literals *)
date_value : DATE := D#2024-01-15;     (* January 15, 2024 *)

(* Time of day *)
tod_value : TIME_OF_DAY := TOD#14:30:45;  (* 2:30:45 PM *)

(* Date and time *)
timestamp : DATE_AND_TIME := DT#2024-01-15-14:30:45;

(* Type conversions *)
seconds : INT := TIME_TO_INT(time_duration) / 1000;
milliseconds : UDINT := TIME_TO_DINT(time_duration);
time_from_int : TIME := INT_TO_TIME(5000);  (* 5 seconds *)

(* Get current time *)
now : DATE_AND_TIME := CURRENT_DATE_AND_TIME();
current_seconds : ULINT := GET_TICKS();
```

### Math Functions

```
ABS(value)          - Absolute value
SQRT(value)         - Square root
SIN(angle)          - Sine (radians)
COS(angle)          - Cosine (radians)
TAN(angle)          - Tangent (radians)
ASIN(value)         - Arc sine
ACOS(value)         - Arc cosine
ATAN(value)         - Arc tangent
ATAN2(y, x)         - Two-argument arc tangent
LOG(value)          - Natural logarithm
LN(value)           - Natural logarithm
LOG10(value)        - Base-10 logarithm
EXP(value)          - e raised to power
EXPT(base, power)   - Base raised to power
MIN(value1, value2) - Minimum
MAX(value1, value2) - Maximum
MOD(dividend, divisor) - Modulo
CEIL(value)         - Round up to integer
FLOOR(value)        - Round down to integer
ROUND(value)        - Round to nearest integer
TRUNC(value)        - Truncate to integer

(* Example: Temperature sensor scaling *)
raw_voltage : REAL := 2.5;        (* 0-5V sensor output *)
temperature : REAL;
temperature := (raw_voltage - 0.5) / 0.01;  (* 0.5V = 0°C, 10mV per °C *)
temperature := MAX(-50.0, MIN(temperature, 100.0));  (* Clamp -50 to 100 *)
```

### Array Operations

```
(* Array declaration *)
sensor_readings : ARRAY [1..100] OF REAL;
multi_dimensional : ARRAY [1..10, 1..20] OF INT;
dynamic_array : ARRAY [*] OF REAL;    (* Dynamic size *)

(* Array access *)
sensor_readings[1] := 25.5;
value := sensor_readings[50];
sum := sum + sensor_readings[index];

(* Array iteration *)
FOR i := 1 TO 100 DO
    sensor_readings[i] := 0;
END_FOR;

(* Multi-dimensional arrays *)
matrix[1, 1] := 10;
matrix[i, j] := matrix[i, j] * factor;

(* String array *)
device_names : ARRAY [1..5] OF STRING;
device_names[1] := 'Motor_1';
device_names[2] := 'Pump_2';

(* Find index of value *)
FOR i := 1 TO 100 DO
    IF sensor_readings[i] > 50.0 THEN
        high_index := i;
        EXIT;
    END_IF;
END_FOR;
```

### Structure Definitions

```
TYPE MotorStatus : STRUCT
    running : BOOL;
    current_speed : INT;              (* RPM *)
    power_consumption : REAL;          (* Watts *)
    temperature : REAL;               (* °C *)
    error_code : INT;
    last_maintenance : DATE;
END_STRUCT;

TYPE ProcessState : (IDLE, RUNNING, PAUSED, FAULT, SHUTDOWN);

(* Usage *)
VAR
    motor1 : MotorStatus;
    current_mode : ProcessState := IDLE;
END_VAR;

motor1.running := TRUE;
motor1.current_speed := 1500;
motor1.temperature := 45.5;

IF motor1.temperature > 80.0 THEN
    current_mode := FAULT;
END_IF;
```

---

## Ladder Logic Elements (ASCII Representation)

### Basic Contacts & Coils

```
Normally Open Contact (NO):
─| |─
Pass current when TRUE

Normally Closed Contact (NC):
─|/|─
Pass current when FALSE

Positive Edge Detection (Rising):
─|P|─
TRUE for one scan when transition 0→1

Negative Edge Detection (Falling):
─|N|─
TRUE for one scan when transition 1→0

Output Coil:
─( )─
Energizes when powered

Negated Output Coil:
─(/)─
Opposite of normal coil
```

### Series & Parallel Connections

```
Series (AND):
Input1 ──| |──┬─────── Output
            Input2 ──| |──┘

Equivalent: Output = Input1 AND Input2


Parallel (OR):
      ┌── Input1 ──| |──┐
Input │                 ├─── Output
      └── Input2 ──| |──┘

Equivalent: Output = Input1 OR Input2


Combination:
      ┌── Cond1 ──| |──┬──────┐
      │                │      │
Input │      ┌─ Cond2 ─| |─┘  ├─ Output
      │      │
      └─────┤ Cond3 ──| |─────┘

Equivalent: Output = Cond1 OR (Cond2 AND Cond3)
```

### Self-Latching Circuit

```
      ┌─────────────── Latch Output ──────────┐
      │                                        │
Start ┤                                        ├─( Latch_Status )─
      │                                        │
      └──── NOT Stop ────┘                     │

Logic:
- Latch_Status = (Start OR Latch_Status) AND NOT Stop
- Once Start activated, Latch_Status remains TRUE
- Reset only when Stop activated
```

### Timer Circuits

```
On-Delay Timer (TON):
Trigger ──| |─┬────────────────┐
           Timer Output (T)     Delay Time
           ├──( Pulse )─        (e.g., 5 seconds)

Behavior:
- Output stays LOW while input is LOW
- When input goes HIGH, output goes HIGH after delay
- Used for: Startup sequences, stabilization


Off-Delay Timer (TOF):
Trigger ──| |─┬────────────────┐
           Timer Output (T)     Delay Time
           ├──( Pulse )─        (e.g., 2 seconds)

Behavior:
- Output HIGH when input is HIGH
- When input goes LOW, output stays HIGH for delay
- Used for: Graceful shutdowns, cooldown periods


Pulse Timer (TP):
Trigger ──| |─┬────────────────┐
           Timer Output (T)     Pulse Width
           ├──( Pulse )─        (e.g., 500ms)

Behavior:
- Output generates single pulse of specified duration
- Pulse duration independent of input duration
- Used for: Momentary actions, pulse generation
```

### Counter Circuits

```
Up Counter:
Pulse ──| |──┐
      Counter ├──────────────┐
        Value ──────────────┐│
             Setpoint       ││
     ┌───────────────────────┘│
     │                         ├─( Count_Reached )─
     └─────────────┬───────────┘
              Reset

Behavior:
- Increments by 1 on each rising edge of Pulse
- Output TRUE when Counter Value reaches Setpoint
- Resets to 0 when Reset activated


Down Counter:
Pulse ──| |──┐
      Counter ├──────────────┐
     Setpoint ──────────────┐│
             Value          ││
     ┌───────────────────────┘│
     │                         ├─( Count_Complete )─
     └─────────────┬───────────┘
              Load

Behavior:
- Decrements by 1 on each rising edge of Pulse
- Output TRUE when Counter reaches 0
- Loads with Setpoint value when Load activated
```

---

## Function Block Examples (ST Syntax)

### On-Delay Timer (TON)

```
FUNCTION_BLOCK TON_Timer
VAR_INPUT
    IN : BOOL;
    PT : TIME;                    (* Preset time *)
END_VAR

VAR_OUTPUT
    Q : BOOL;                     (* Output *)
    ET : TIME;                    (* Elapsed time *)
END_VAR

VAR
    start_time : TIME;
    timer_running : BOOL := FALSE;
END_VAR

    IF IN THEN
        IF NOT timer_running THEN
            start_time := CURRENT_TIME();
            timer_running := TRUE;
        END_IF;

        ET := CURRENT_TIME() - start_time;

        IF ET >= PT THEN
            Q := TRUE;
        END_IF;
    ELSE
        Q := FALSE;
        ET := T#0ms;
        timer_running := FALSE;
    END_IF;

END_FUNCTION_BLOCK
```

### Rising Edge Detector

```
FUNCTION EdgeDetector
VAR_INPUT
    input_signal : BOOL;
END_VAR

VAR_OUTPUT
    rising_edge : BOOL;
    falling_edge : BOOL;
END_VAR

VAR
    previous_state : BOOL := FALSE;
END_VAR

    rising_edge := input_signal AND NOT previous_state;
    falling_edge := NOT input_signal AND previous_state;

    previous_state := input_signal;

END_FUNCTION
```

### Proportional Controller

```
FUNCTION_BLOCK ProportionalControl
VAR_INPUT
    error : REAL;                 (* Setpoint - Process value *)
    gain : REAL := 1.0;
    output_max : REAL := 100.0;
    output_min : REAL := 0.0;
END_VAR

VAR_OUTPUT
    output : REAL;
END_VAR

    output := error * gain;
    output := MAX(output_min, MIN(output, output_max));

END_FUNCTION_BLOCK
```

### Simple PID Controller

```
FUNCTION_BLOCK SimplePID
VAR_INPUT
    setpoint : REAL;
    process_value : REAL;
    Kp : REAL := 1.0;
    Ki : REAL := 0.1;
    Kd : REAL := 0.05;
    dt : TIME := T#10ms;
    enable : BOOL := TRUE;
END_VAR

VAR_OUTPUT
    output : REAL;
END_VAR

VAR
    error : REAL;
    error_prev : REAL := 0.0;
    integral : REAL := 0.0;
    dt_seconds : REAL;
END_VAR

    IF enable THEN
        error := setpoint - process_value;
        dt_seconds := TIME_TO_REAL(dt) / 1000.0;

        (* Proportional *)
        p_term := Kp * error;

        (* Integral *)
        integral := integral + (error * dt_seconds);
        i_term := Ki * integral;

        (* Derivative *)
        d_term := Kd * (error - error_prev) / dt_seconds;

        output := p_term + i_term + d_term;
        error_prev := error;
    END_IF;

END_FUNCTION_BLOCK
```

---

## Modbus Protocol Quick Reference

### Modbus Function Codes

| Code | Name | Purpose | Read/Write |
|------|------|---------|-----------|
| 01 | Read Coils | Read discrete outputs | Read |
| 02 | Read Discrete Inputs | Read digital inputs | Read |
| 03 | Read Holding Registers | Read internal registers | Read |
| 04 | Read Input Registers | Read analog inputs | Read |
| 05 | Write Single Coil | Control single output | Write |
| 06 | Write Single Register | Set single value | Write |
| 15 (0x0F) | Write Multiple Coils | Control multiple outputs | Write |
| 16 (0x10) | Write Multiple Registers | Set multiple values | Write |

### Register Mapping Standard

```
0000-9999   : Coils (Boolean outputs)
10000-19999 : Discrete Inputs (Boolean inputs)
30000-39999 : Input Registers (Read-only data)
40000-49999 : Holding Registers (Read/write data)
```

### Typical Industrial Application

```
Modbus Device Example - Temperature Controller:

Registers:
40001 - Temperature Setpoint (0.1°C per unit)
40002 - Proportional Gain (0.01 per unit)
40003 - Integral Gain (0.01 per unit)
40004 - Derivative Gain (0.01 per unit)
40005 - Alarm High Threshold (0.1°C per unit)

30001 - Current Process Temperature (0.1°C per unit)
30002 - Output Power Percentage (0-1000 = 0-100%)
30003 - Status Code

Coils:
00001 - Enable/Disable Control
00002 - Manual Mode
```

---

## OPC UA Quick Reference

### Common Data Types (OPC UA)

```
Boolean, SByte, Byte
Int16, UInt16, Int32, UInt32, Int64, UInt64
Float, Double
String, ByteString
DateTime, Guid, QualifiedName, LocalizedText
NodeId, ExpandedNodeId
```

### Common Node Classes

```
Object       - Represents real-world or abstract entity
ObjectType   - Template for objects
Variable     - Contains data value
VariableType - Template for variables
Method       - Callable function
Property     - Characteristic of object/variable
DataType     - Definition of data structure
ReferenceType - Link between nodes
View         - Custom organizational view
```

### Standard Reference Types

```
HasChild        - Hierarchical parent-child relationship
HasComponent    - Object composition relationship
HasProperty     - Object characteristics
HasDataType     - Variable data type definition
HasEventSource  - Event generation source
Organizes       - Non-hierarchical organization
```

---

## Safety Interlocking Patterns

### Dual-Channel Monitoring

```
Input Channel 1 ──┐
                  ├─ Comparison ─┬─ Output (if equal)
Input Channel 2 ──┘              │
                                 └─ Fault signal (if unequal)

Logic:
- Both channels must agree
- Any disagreement triggers safety shutdown
- Cross-monitoring prevents single-point failure
```

### Watchdog Timer Pattern

```
Heartbeat Signal ──┐
                   ├─ Watchdog Timer ──────┐
  Timeout Value ───┘                       │
                                           ├─( FAULT )
                                           │
No Heartbeat for longer than timeout ──────┘

Logic:
- Controller must send periodic heartbeat
- Absence of heartbeat indicates controller failure
- Automatic shutdown on timeout
```

---

## Performance Optimization Techniques

### Memory Usage Optimization

```
(* Before: Inefficient *)
data_array : ARRAY [1..10000] OF REAL;

(* After: Efficient *)
data_array : ARRAY [1..100] OF REAL;  (* Rolling buffer *)
array_index : INT := 0;

(* Use modulo for circular buffer *)
array_index := (array_index + 1) MOD 100;
data_array[array_index] := new_value;
```

### Scan Time Optimization

```
(* Before: Expensive floating-point *)
ratio := (sensor_value / MAX_RANGE) * 100.0;

(* After: Integer math *)
ratio : INT;
ratio := (sensor_value * 100) / MAX_RANGE;  (* Same result, faster *)
```

### Communication Efficiency

```
(* Before: Sending all values every scan *)
FOR i := 1 TO 100 DO
    send_to_network(register[i]);
END_FOR;

(* After: Send only changed values *)
FOR i := 1 TO 100 DO
    IF register[i] <> register_prev[i] THEN
        send_to_network(register[i]);
        register_prev[i] := register[i];
    END_IF;
END_FOR;
```

---

## Common Industrial Patterns

### State Machine Pattern

```
FUNCTION_BLOCK StateController
VAR
    current_state : (IDLE, RUNNING, PAUSED, FAULT);
    next_state : (IDLE, RUNNING, PAUSED, FAULT);
END_VAR

    (* State entry conditions *)
    CASE next_state OF
        IDLE:
            motor_enable := FALSE;
        RUNNING:
            motor_enable := TRUE;
        PAUSED:
            motor_enable := FALSE;
        FAULT:
            alarm := TRUE;
            motor_enable := FALSE;
    END_CASE;

    (* State transitions *)
    CASE current_state OF
        IDLE:
            IF start_command THEN
                next_state := RUNNING;
            END_IF;

        RUNNING:
            IF pause_command THEN
                next_state := PAUSED;
            ELSIF fault_detected THEN
                next_state := FAULT;
            ELSIF stop_command THEN
                next_state := IDLE;
            END_IF;

        PAUSED:
            IF start_command THEN
                next_state := RUNNING;
            ELSIF stop_command THEN
                next_state := IDLE;
            END_IF;

        FAULT:
            IF reset_command AND NOT fault_detected THEN
                next_state := IDLE;
            END_IF;
    END_CASE;

    current_state := next_state;

END_FUNCTION_BLOCK
```

### Hysteresis Filter

```
(* Prevent oscillation around setpoint *)
IF input_value > (setpoint + HYSTERESIS) THEN
    output := TRUE;
ELSIF input_value < (setpoint - HYSTERESIS) THEN
    output := FALSE;
END_IF;

(* Example: Hysteresis = 2°C *)
(* Turn on heater when T < 48°C *)
(* Turn off heater when T > 52°C *)
(* Prevents rapid switching near 50°C setpoint *)
```

### Debounce Filter

```
FUNCTION_BLOCK Debounce
VAR_INPUT
    noisy_input : BOOL;
    debounce_time : TIME := T#20ms;
END_VAR

VAR_OUTPUT
    clean_output : BOOL;
END_VAR

VAR
    last_stable_state : BOOL := FALSE;
    change_time : TIME;
    state_changed : BOOL := FALSE;
END_VAR

    IF noisy_input <> last_stable_state THEN
        IF NOT state_changed THEN
            change_time := CURRENT_TIME();
            state_changed := TRUE;
        END_IF;

        IF (CURRENT_TIME() - change_time) >= debounce_time THEN
            last_stable_state := noisy_input;
            state_changed := FALSE;
        END_IF;
    END_IF;

    clean_output := last_stable_state;

END_FUNCTION_BLOCK
```

---

## Debugging Tips

### Printf-style Debugging

```
(* Log variable state *)
log_message := CONCAT('Temperature: ', REAL_TO_STRING(temperature));
(* Send to historian or debug buffer *)
log_event(log_message);
```

### Range Checking

```
(* Verify inputs are within expected range *)
IF temperature < -50.0 OR temperature > 100.0 THEN
    sensor_error := TRUE;
    temperature := last_known_good;
END_IF;
```

### Heartbeat Monitoring

```
(* Add heartbeat counter to verify program is running *)
VAR
    heartbeat : INT := 0;
END_VAR;

heartbeat := (heartbeat + 1) MOD 100;  (* Counts 0-99, repeats *)
(* Monitor external tool can verify heartbeat changes *)
```

---

## Document Version: 2.0
**Last Updated:** January 2024
**Standard Reference:** IEC 61131-3:2013
