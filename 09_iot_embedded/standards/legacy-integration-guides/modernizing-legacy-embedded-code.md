# Modernizing Legacy Embedded Code

## Migration Strategy

### Phase 1: Assessment
1. **Code Audit**: Static analysis (Cppcheck, Coverity)
2. **Dependency Map**: Identify external dependencies
3. **Test Coverage**: Measure existing coverage
4. **Risk Analysis**: Identify critical/safety paths

### Phase 2: Incremental Refactoring

**Rule**: Never break working code all at once

```c
// Legacy: Global variables, no structure
int sensor_value;
int threshold = 100;

void check_sensor() {
    if (sensor_value > threshold) {
        turn_on_alarm();
    }
}

// Step 1: Encapsulate in struct
typedef struct {
    int value;
    int threshold;
} sensor_t;

static sensor_t g_sensor = {0, 100};

void check_sensor() {
    if (g_sensor.value > g_sensor.threshold) {
        turn_on_alarm();
    }
}

// Step 2: Add error handling
typedef enum { SENSOR_OK, SENSOR_ERROR } sensor_status_t;

sensor_status_t check_sensor() {
    if (g_sensor.value > g_sensor.threshold) {
        return turn_on_alarm() ? SENSOR_OK : SENSOR_ERROR;
    }
    return SENSOR_OK;
}
```

### Phase 3: MISRA Compliance

```c
// Legacy: Implicit conversions
unsigned char a = 200;
unsigned char b = 200;
unsigned char result = a + b;  // Overflow!

// MISRA-compliant
uint8_t a = 200U;
uint8_t b = 200U;
uint16_t result = (uint16_t)a + (uint16_t)b;  // Explicit cast
```

### Phase 4: RTOS Migration

**Bare-metal → RTOS**:
1. Identify tasks (main loop sections)
2. Create RTOS tasks
3. Replace delays with vTaskDelay()
4. Add mutexes for shared resources
5. Test incrementally

## Tools

- **Refactoring**: Understand (commercial), Doxygen
- **Static Analysis**: PC-lint, Coverity, Cppcheck
- **Migration**: Code Composer Studio, IAR Workbench
