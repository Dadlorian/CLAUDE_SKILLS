# Embedded C Coding Standard

**Professional coding standard for embedded C development based on MISRA C:2012, AUTOSAR, and industry best practices**

---

## Overview

This coding standard ensures safe, reliable, and maintainable embedded C code suitable for resource-constrained systems, real-time applications, and safety-critical environments.

## Core Principles

1. **Predictability**: Code behavior must be deterministic and predictable
2. **Reliability**: Minimize undefined behavior and runtime errors
3. **Maintainability**: Code must be readable and self-documenting
4. **Efficiency**: Optimize for memory and CPU usage without sacrificing clarity
5. **Safety**: Follow MISRA C guidelines for safety-critical applications

---

## File Organization

### Header Files (.h)

```c
/**
 * @file    sensor_driver.h
 * @brief   Temperature sensor driver interface
 * @author  Engineering Team
 * @date    2025-11-19
 * @version 1.0.0
 */

#ifndef SENSOR_DRIVER_H
#define SENSOR_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes */
#include <stdint.h>
#include <stdbool.h>

/* Defines and Macros */
#define SENSOR_MAX_SAMPLES      (100U)
#define SENSOR_TIMEOUT_MS       (5000U)

/* Type Definitions */
typedef enum {
    SENSOR_OK = 0,
    SENSOR_ERROR,
    SENSOR_TIMEOUT,
    SENSOR_INVALID_PARAM
} sensor_status_t;

/* Function Prototypes */
sensor_status_t sensor_init(void);
sensor_status_t sensor_read_temperature(int16_t *temp);
void sensor_deinit(void);

#ifdef __cplusplus
}
#endif

#endif /* SENSOR_DRIVER_H */
```

### Source Files (.c)

```c
/**
 * @file    sensor_driver.c
 * @brief   Temperature sensor driver implementation
 */

/* Includes */
#include "sensor_driver.h"
#include "i2c_hal.h"
#include <string.h>

/* Private Defines */
#define SENSOR_I2C_ADDR         (0x48U)
#define SENSOR_REG_TEMP         (0x00U)

/* Private Types */
typedef struct {
    bool initialized;
    uint32_t last_read_timestamp;
} sensor_context_t;

/* Private Variables */
static sensor_context_t s_sensor_ctx = {0};

/* Private Function Prototypes */
static bool is_initialized(void);
static sensor_status_t read_register(uint8_t reg, uint8_t *data, size_t len);

/* Public Function Implementations */
sensor_status_t sensor_init(void) {
    /* Implementation */
}

/* Private Function Implementations */
static bool is_initialized(void) {
    return s_sensor_ctx.initialized;
}
```

---

## Naming Conventions

### Variables

| Type | Convention | Example |
|------|------------|---------|
| Local variables | snake_case | `int sample_count;` |
| Global variables | `g_` prefix + snake_case | `uint32_t g_system_tick;` |
| Static variables | `s_` prefix + snake_case | `static bool s_is_initialized;` |
| Constants | UPPER_SNAKE_CASE | `#define MAX_BUFFER_SIZE (256U)` |
| Pointers | prefix 'p' | `uint8_t *p_buffer;` |

### Functions

```c
/* Module prefix + action + object */
sensor_status_t sensor_read_temperature(int16_t *temp);
i2c_status_t i2c_write_bytes(uint8_t addr, const uint8_t *data, size_t len);
void gpio_set_pin_high(uint8_t pin);
```

### Types

```c
/* Suffix with _t */
typedef enum {
    STATE_IDLE,
    STATE_RUNNING,
    STATE_ERROR
} system_state_t;

typedef struct {
    uint16_t voltage_mv;
    int16_t temperature_c;
} sensor_data_t;
```

---

## Data Types

### Integer Types (stdint.h)

**Always use fixed-width types for portability:**

```c
#include <stdint.h>

uint8_t  byte_value;        // 0 to 255
int8_t   signed_byte;       // -128 to 127
uint16_t word_value;        // 0 to 65535
int16_t  signed_word;       // -32768 to 32767
uint32_t dword_value;       // 0 to 4,294,967,295
int32_t  signed_dword;      // -2,147,483,648 to 2,147,483,647
```

**MISRA Rule**: Never use `int`, `short`, `long` - use fixed-width types

### Boolean Type

```c
#include <stdbool.h>

bool is_ready;              // true or false
bool sensor_active = false;
```

### Size and Pointer Types

```c
#include <stddef.h>

size_t buffer_length;       // For sizes and counts
ptrdiff_t pointer_diff;     // For pointer arithmetic
uintptr_t addr;             // For storing addresses as integers
```

---

## Constants and Macros

### Constants

```c
/* Use const for compile-time constants */
static const uint32_t UART_BAUDRATE = 115200U;
static const float PI = 3.14159265f;

/* Use enum for related constants */
typedef enum {
    LED_RED    = 0,
    LED_GREEN  = 1,
    LED_BLUE   = 2,
    LED_COUNT
} led_id_t;
```

### Macros

```c
/* Always use parentheses around parameters and entire expression */
#define MIN(a, b)  (((a) < (b)) ? (a) : (b))
#define MAX(a, b)  (((a) > (b)) ? (a) : (b))

/* Use 'U' suffix for unsigned literals */
#define BUFFER_SIZE     (256U)
#define TIMEOUT_MS      (1000U)

/* Bit manipulation macros */
#define BIT(n)          (1U << (n))
#define SET_BIT(reg, bit)    ((reg) |= (bit))
#define CLEAR_BIT(reg, bit)  ((reg) &= ~(bit))
#define TOGGLE_BIT(reg, bit) ((reg) ^= (bit))
#define READ_BIT(reg, bit)   (((reg) & (bit)) != 0U)
```

---

## Memory Management

### Static Allocation (Preferred)

```c
/* Use static allocation for embedded systems */
static uint8_t tx_buffer[256];
static sensor_data_t sensor_samples[100];

/* Avoid VLAs (Variable Length Arrays) - MISRA violation */
void bad_function(size_t n) {
    uint8_t buffer[n];  // BAD: VLA, non-deterministic stack usage
}

/* Use fixed-size or heap allocation instead */
#define MAX_BUFFER_SIZE (256U)
void good_function(size_t n) {
    static uint8_t buffer[MAX_BUFFER_SIZE];
    if (n > MAX_BUFFER_SIZE) {
        /* Error handling */
    }
}
```

### Dynamic Allocation (Use with Caution)

```c
#include <stdlib.h>

void* allocate_buffer(size_t size) {
    void *ptr = malloc(size);
    if (NULL == ptr) {
        /* Handle allocation failure */
        return NULL;
    }
    memset(ptr, 0, size);  // Always initialize
    return ptr;
}

/* Always free allocated memory */
void cleanup(void *ptr) {
    if (NULL != ptr) {
        free(ptr);
    }
}
```

**MISRA Guidance**: Avoid dynamic allocation in safety-critical code due to fragmentation and non-determinism

---

## Volatile Keyword

### When to Use Volatile

```c
/* Hardware registers */
volatile uint32_t *const REG_GPIO_DATA = (volatile uint32_t *)0x40020014;

/* Variables modified by interrupts */
static volatile bool g_data_ready = false;

/* Shared variables in multi-threaded systems */
static volatile uint32_t g_shared_counter = 0;

/* Correct usage */
void ISR_UART_RX(void) {
    g_data_ready = true;  // ISR modifies variable
}

void main_task(void) {
    while (!g_data_ready) {  // Volatile prevents optimization
        /* Wait */
    }
}
```

---

## Error Handling

### Return Status Pattern

```c
typedef enum {
    STATUS_OK = 0,
    STATUS_ERROR,
    STATUS_TIMEOUT,
    STATUS_INVALID_PARAM,
    STATUS_BUSY
} status_t;

/* Always check return values */
status_t sensor_init(void) {
    status_t status;

    status = i2c_init(I2C_SPEED_100KHZ);
    if (STATUS_OK != status) {
        return STATUS_ERROR;
    }

    status = sensor_configure();
    if (STATUS_OK != status) {
        i2c_deinit();  // Cleanup on error
        return status;
    }

    return STATUS_OK;
}

/* Caller must check status */
void application_code(void) {
    status_t status = sensor_init();
    if (STATUS_OK != status) {
        /* Handle error */
    }
}
```

### Assertions

```c
#include <assert.h>

/* Use for catching programming errors during development */
void buffer_write(uint8_t *buffer, size_t index, uint8_t value) {
    assert(NULL != buffer);
    assert(index < BUFFER_SIZE);

    buffer[index] = value;
}

/* For production, replace with runtime checks */
#ifdef PRODUCTION_BUILD
    #define ASSERT(expr) \
        do { \
            if (!(expr)) { \
                error_handler(__FILE__, __LINE__); \
            } \
        } while(0)
#else
    #define ASSERT(expr) assert(expr)
#endif
```

---

## Function Design

### Input Validation

```c
status_t buffer_copy(uint8_t *dest, const uint8_t *src, size_t len) {
    /* Validate all inputs */
    if ((NULL == dest) || (NULL == src)) {
        return STATUS_INVALID_PARAM;
    }

    if (0U == len) {
        return STATUS_INVALID_PARAM;
    }

    if (len > MAX_BUFFER_SIZE) {
        return STATUS_INVALID_PARAM;
    }

    /* Perform operation */
    memcpy(dest, src, len);

    return STATUS_OK;
}
```

### Function Length

- Keep functions short and focused (< 50 lines ideally)
- Single responsibility principle
- Extract complex logic into helper functions

### Const Correctness

```c
/* Use const for read-only parameters */
void process_data(const uint8_t *data, size_t len);

/* Use const for read-only pointers */
const char *get_version_string(void);

/* Const pointer to const data */
void display_message(const char *const message);
```

---

## Interrupt Service Routines (ISRs)

### ISR Guidelines

```c
/* Keep ISRs short and fast */
volatile bool g_uart_rx_complete = false;
static uint8_t s_rx_buffer[256];
static volatile size_t s_rx_index = 0;

void UART1_IRQHandler(void) {
    /* Read hardware register (volatile access) */
    uint8_t data = UART1->DATA;

    /* Minimal processing */
    if (s_rx_index < sizeof(s_rx_buffer)) {
        s_rx_buffer[s_rx_index++] = data;
    }

    /* Set flag for main task */
    g_uart_rx_complete = true;

    /* Clear interrupt flag */
    UART1->STATUS = UART_STATUS_CLEAR;
}

/* Main task processes data */
void main_task(void) {
    if (g_uart_rx_complete) {
        g_uart_rx_complete = false;
        process_uart_data(s_rx_buffer, s_rx_index);
        s_rx_index = 0;
    }
}
```

### Atomic Operations

```c
#include <stdatomic.h>  // C11

/* For simple flags, use atomic types */
atomic_bool g_data_ready = ATOMIC_VAR_INIT(false);

/* Or disable interrupts for critical sections */
void critical_update(void) {
    uint32_t primask = __get_PRIMASK();
    __disable_irq();

    /* Critical section */
    g_shared_variable++;

    __set_PRIMASK(primask);  // Restore interrupt state
}
```

---

## MISRA C Compliance

### Key MISRA Rules

1. **Rule 1.3**: No undefined behavior
2. **Rule 2.1**: No unreachable code
3. **Rule 8.13**: Use `const` for read-only pointers
4. **Rule 10.1**: No implicit conversions that may lose information
5. **Rule 14.4**: Use `bool` type for boolean values
6. **Rule 17.7**: Must use return value of non-void functions
7. **Rule 21.3**: Avoid `malloc` and `free` in safety-critical code

### MISRA Deviations

```c
/* Document deviations with justification */
/* MISRA Deviation: Rule 11.4 - Cast from pointer to integer
 * Justification: Required for hardware register access
 */
volatile uint32_t *gpio_base = (volatile uint32_t *)0x40020000;
```

---

## Code Comments

### Header Comments

```c
/**
 * @brief   Initialize the UART peripheral
 * @param   baudrate  Desired baud rate (e.g., 115200)
 * @param   config    Pointer to UART configuration structure
 * @return  STATUS_OK on success, error code otherwise
 * @note    Must be called before any UART operations
 * @warning Baudrate must be supported by hardware
 */
status_t uart_init(uint32_t baudrate, const uart_config_t *config);
```

### Inline Comments

```c
/* Use comments to explain WHY, not WHAT */

/* Good: Explains rationale */
// Wait 10ms for sensor stabilization after power-on
delay_ms(10);

/* Bad: States the obvious */
// Set i to 0
i = 0;

/* Good: Complex algorithm explanation */
// Apply exponential moving average to reduce noise
// alpha = 0.1, y[n] = alpha * x[n] + (1-alpha) * y[n-1]
filtered_value = (alpha * current_value) + ((1.0f - alpha) * filtered_value);
```

---

## Best Practices

### Integer Promotions

```c
/* Beware of implicit promotions */
uint8_t a = 200;
uint8_t b = 200;
uint8_t result = a + b;  // BAD: Overflow, promoted to int then truncated

/* Correct: Explicit cast */
uint16_t result = (uint16_t)a + (uint16_t)b;
```

### Bit Manipulation

```c
/* Use unsigned types for bit operations */
uint32_t flags = 0;
flags |= BIT(5);   // Set bit 5
flags &= ~BIT(3);  // Clear bit 3
bool is_set = (flags & BIT(5)) != 0U;
```

### Magic Numbers

```c
/* Bad: Magic numbers */
if (status == 3) {
    delay(500);
}

/* Good: Named constants */
#define STATUS_TIMEOUT  (3U)
#define RETRY_DELAY_MS  (500U)

if (status == STATUS_TIMEOUT) {
    delay_ms(RETRY_DELAY_MS);
}
```

---

## References

- MISRA C:2012 Guidelines for the Use of the C Language in Critical Systems
- BARR-C:2018 Embedded C Coding Standard
- SEI CERT C Coding Standard
- NASA C Style Guide
- Linux Kernel Coding Style (for embedded Linux)

---

**This standard ensures embedded C code is safe, portable, maintainable, and suitable for production deployment in resource-constrained and safety-critical systems.**
