# MISRA C:2012 Quick Reference

## Mandatory Rules (Must Follow)

### Rule 1.3: No undefined behavior
- No division by zero
- No array out of bounds
- No dereferencing null pointers
- No signed integer overflow

### Rule 2.1: No unreachable code
```c
// BAD
if (true) {
    return;
}
unreachable_code();  // Violation

// GOOD
if (condition) {
    return;
}
reachable_code();
```

### Rule 8.13: Use const for read-only pointers
```c
// GOOD
void process(const uint8_t *data, size_t len);

// BAD
void process(uint8_t *data, size_t len);  // If data not modified
```

### Rule 10.1: No implicit conversions
```c
// BAD
uint8_t a = 200;
uint8_t b = 200;
uint8_t result = a + b;  // Overflow

// GOOD
uint16_t result = (uint16_t)a + (uint16_t)b;
```

### Rule 14.4: Use bool for boolean
```c
#include <stdbool.h>

// GOOD
bool is_ready(void);

// BAD
int is_ready(void);  // Returns 0/1
```

### Rule 17.7: Use return values
```c
// BAD
i2c_write(addr, data, len);  // Ignoring return

// GOOD
status_t status = i2c_write(addr, data, len);
if (STATUS_OK != status) {
    handle_error();
}
```

### Rule 21.3: Avoid malloc/free
```c
// Preferred in embedded
static uint8_t buffer[256];

// Avoid (fragmentation, non-determinism)
uint8_t *buffer = malloc(256);
```

## Required Rules (Should Follow)

### Rule 2.2: No dead code
- Remove unused variables
- Remove unused functions
- Remove unreachable code

### Rule 5.1: External identifiers unique (31 chars)
```c
// GOOD
extern uint32_t system_config_parameter_1;
extern uint32_t system_config_parameter_2;

// BAD (if only first 31 chars matter)
extern uint32_t system_config_parameter_value_a;
extern uint32_t system_config_parameter_value_b;
```

### Rule 8.4: Declare all functions
```c
// header.h
void public_function(void);

// source.c
static void private_function(void);  // File scope only
```

### Rule 11.4: No pointer to integer casts
```c
// Exception: Hardware registers
volatile uint32_t *GPIO = (volatile uint32_t *)0x40020000;

/* MISRA Deviation: Rule 11.4
 * Justification: Required for memory-mapped I/O
 */
```

## Advisory Rules (Recommended)

### Rule 8.7: Functions/variables with internal linkage = static
```c
// GOOD
static void helper_function(void);
static uint32_t module_state = 0;
```

### Rule 15.5: Single point of exit
```c
// Preferred
status_t function(void) {
    status_t result = STATUS_ERROR;

    if (condition_a) {
        if (condition_b) {
            result = STATUS_OK;
        }
    }

    return result;  // Single exit
}
```

## Common Deviations

### Hardware Register Access
```c
/* MISRA Deviation: Rule 11.4
 * Justification: Memory-mapped peripheral access
 */
#define GPIOA_BASE  0x40020000U
#define GPIOA       ((GPIO_TypeDef *)GPIOA_BASE)
```

### Volatile for ISRs
```c
/* Shared with ISR - must be volatile */
static volatile bool g_data_ready = false;
```

## Type Safety

### Fixed-width integers
```c
#include <stdint.h>

uint8_t byte;     // 8-bit
uint16_t word;    // 16-bit
uint32_t dword;   // 32-bit
int16_t signed_word;
```

### Size types
```c
#include <stddef.h>

size_t length;
ptrdiff_t diff;
```

## Bit Operations

```c
#define BIT(n)  (1U << (n))

// Set bit
register |= BIT(5);

// Clear bit
register &= ~BIT(5);

// Toggle bit
register ^= BIT(5);

// Test bit
if ((register & BIT(5)) != 0U) {
    // Bit is set
}
```

## Naming Conventions

```c
#define MAX_SIZE        100U    // Macros: UPPER_CASE
typedef enum {              // Types: snake_case_t
    STATE_IDLE,
    STATE_ACTIVE
} state_t;

static uint32_t s_module_var;  // Static: s_ prefix
uint32_t g_global_var;          // Global: g_ prefix
void function_name(void);       // Functions: snake_case
```

## Static Analysis Tools

- **PC-lint Plus**: Commercial, comprehensive
- **Cppcheck**: Open-source, free
- **Coverity**: Enterprise-grade
- **Clang Static Analyzer**: LLVM-based

## Compliance Levels

- **Mandatory**: Must comply (safety-critical)
- **Required**: Should comply (document deviations)
- **Advisory**: Recommended (best practices)

## Quick Checklist

- [ ] All functions have prototypes
- [ ] No implicit type conversions
- [ ] All return values checked
- [ ] No magic numbers (use #define or const)
- [ ] All pointers checked for NULL
- [ ] Fixed-width types used (uint8_t, etc.)
- [ ] Bool type for boolean values
- [ ] Const used for read-only data
- [ ] Static used for file-scope items
- [ ] All deviations documented with justification
