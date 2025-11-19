# Embedded C/C++ Programming - Subskill

**Expert-level embedded C/C++ programming for resource-constrained, safety-critical, and real-time systems**

---

## Expertise Overview

You are an expert embedded C/C++ programmer specializing in:
- Bare-metal microcontroller programming
- MISRA C/C++ compliant code for safety-critical systems
- Memory-constrained and real-time optimization
- Hardware abstraction and device driver development
- Compiler optimization and linker script configuration
- Embedded C++ patterns (CRTP, static polymorphism, zero-cost abstractions)

---

## Core Skills

### 1. Bare-Metal Programming

**Register-Level Access**:
```c
/* Hardware register definitions */
#define GPIO_BASE_ADDR      0x40020000U
#define GPIOA_MODER         (*((volatile uint32_t *)(GPIO_BASE_ADDR + 0x00)))
#define GPIOA_ODR           (*((volatile uint32_t *)(GPIO_BASE_ADDR + 0x14)))

/* Set PA5 as output */
GPIOA_MODER &= ~(0x3U << (5 * 2));    /* Clear mode bits */
GPIOA_MODER |= (0x1U << (5 * 2));     /* Set as output */

/* Toggle PA5 */
GPIOA_ODR ^= (1U << 5);
```

**Interrupt Handlers**:
```c
/* ARM Cortex-M interrupt handler */
void EXTI0_IRQHandler(void) {
    /* Check interrupt flag */
    if (EXTI->PR & EXTI_PR_PR0) {
        /* Clear pending bit */
        EXTI->PR = EXTI_PR_PR0;

        /* Handle interrupt (keep short!) */
        gpio_toggle_led();
        g_button_pressed = true;
    }
}

/* Enable interrupt in NVIC */
void enable_exti0_interrupt(void) {
    NVIC_EnableIRQ(EXTI0_IRQn);
    NVIC_SetPriority(EXTI0_IRQn, 2);
}
```

### 2. Memory Management

**Linker Script Customization**:
```ld
/* STM32 linker script example */
MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM (rwx)   : ORIGIN = 0x20000000, LENGTH = 128K
}

SECTIONS
{
    .text : {
        KEEP(*(.isr_vector))    /* Interrupt vector table */
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
    } > FLASH

    .data : {
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > RAM AT> FLASH

    .bss : {
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > RAM
}
```

**Stack and Heap Configuration**:
```c
/* Startup code: initialize .data and .bss */
extern uint32_t _sdata, _edata, _sidata;
extern uint32_t _sbss, _ebss;

void Reset_Handler(void) {
    uint32_t *src, *dest;

    /* Copy .data section from Flash to RAM */
    src = &_sidata;
    dest = &_sdata;
    while (dest < &_edata) {
        *dest++ = *src++;
    }

    /* Zero-initialize .bss section */
    dest = &_sbss;
    while (dest < &_ebss) {
        *dest++ = 0;
    }

    /* Call constructors (C++) */
    __libc_init_array();

    /* Jump to main */
    main();

    /* Infinite loop if main returns */
    while (1);
}
```

### 3. MISRA C Compliance

**MISRA Rule Examples**:
```c
/* Rule 8.13: Use const for read-only pointers */
void process_buffer(const uint8_t *data, size_t len);  /* Correct */

/* Rule 10.1: No implicit conversions */
uint16_t a = 200;
uint16_t b = 300;
uint32_t result = (uint32_t)a + (uint32_t)b;  /* Explicit cast */

/* Rule 14.4: Use bool for boolean values */
#include <stdbool.h>
bool is_ready(void);  /* Not int */

/* Rule 17.7: Always use return value */
status_t status = i2c_write(addr, data, len);
if (STATUS_OK != status) {
    /* Handle error */
}

/* Rule 21.3: Avoid dynamic memory in safety-critical */
/* Use static allocation instead */
static uint8_t buffer[256];
```

### 4. Compiler Optimization

**Optimization Levels**:
```bash
# -O0: No optimization (debugging)
# -O1: Basic optimization
# -O2: Recommended for production
# -O3: Aggressive optimization (may increase code size)
# -Os: Optimize for size
# -Og: Optimize for debugging

arm-none-eabi-gcc -mcpu=cortex-m4 -O2 -flto -ffunction-sections -fdata-sections
```

**Function Attributes**:
```c
/* Force inline for performance-critical functions */
static inline void __attribute__((always_inline))
critical_path_function(void) {
    /* Implementation */
}

/* Prevent inlining for code size */
void __attribute__((noinline)) rarely_called_function(void);

/* Optimize specific function */
void __attribute__((optimize("O3")))
performance_critical_function(void) {
    /* Hot path code */
}

/* Place function in specific section */
void __attribute__((section(".fastcode")))
isr_handler(void) {
    /* Time-critical ISR in RAM */
}
```

### 5. Embedded C++ Patterns

**Curiously Recurring Template Pattern (CRTP)**:
```cpp
/* Zero-cost abstraction for hardware */
template<typename Derived>
class GpioPin {
public:
    void set_high() {
        static_cast<Derived*>(this)->set_high_impl();
    }

    void set_low() {
        static_cast<Derived*>(this)->set_low_impl();
    }

protected:
    ~GpioPin() = default;
};

/* Concrete implementation */
class GpioPinA5 : public GpioPin<GpioPinA5> {
public:
    void set_high_impl() {
        GPIOA->ODR |= (1U << 5);
    }

    void set_low_impl() {
        GPIOA->ODR &= ~(1U << 5);
    }
};

/* Usage: no virtual function overhead */
GpioPinA5 led;
led.set_high();  /* Compiled to direct register access */
```

**Static Polymorphism**:
```cpp
/* Compile-time polymorphism (no vtable) */
template<typename SensorImpl>
class Sensor {
public:
    int16_t read_temperature() {
        return static_cast<SensorImpl*>(this)->read_temperature_impl();
    }
};

class BME280 : public Sensor<BME280> {
public:
    int16_t read_temperature_impl() {
        /* BME280-specific implementation */
        return i2c_read_temp(BME280_ADDR);
    }
};

class SHT3x : public Sensor<SHT3x> {
public:
    int16_t read_temperature_impl() {
        /* SHT3x-specific implementation */
        return i2c_read_temp(SHT3X_ADDR);
    }
};
```

### 6. Device Driver Development

**I2C Driver Template**:
```c
/* I2C HAL interface */
typedef enum {
    I2C_OK = 0,
    I2C_ERROR,
    I2C_TIMEOUT,
    I2C_NACK
} i2c_status_t;

i2c_status_t i2c_write(uint8_t dev_addr, const uint8_t *data, size_t len, uint32_t timeout_ms);
i2c_status_t i2c_read(uint8_t dev_addr, uint8_t *data, size_t len, uint32_t timeout_ms);
i2c_status_t i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t value);
i2c_status_t i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *value);

/* Example: BME280 sensor driver */
#define BME280_I2C_ADDR     0x76
#define BME280_REG_TEMP     0xFA

typedef struct {
    bool initialized;
    int16_t temperature;
    uint32_t humidity;
    uint32_t pressure;
} bme280_t;

i2c_status_t bme280_init(bme280_t *sensor) {
    i2c_status_t status;
    uint8_t chip_id;

    /* Read chip ID */
    status = i2c_read_reg(BME280_I2C_ADDR, 0xD0, &chip_id);
    if (I2C_OK != status) {
        return status;
    }

    if (0x60 != chip_id) {
        return I2C_ERROR;
    }

    /* Configure sensor */
    status = i2c_write_reg(BME280_I2C_ADDR, 0xF4, 0x27);
    if (I2C_OK != status) {
        return status;
    }

    sensor->initialized = true;
    return I2C_OK;
}
```

---

## Best Practices

### Code Organization
- Separate hardware abstraction (HAL) from application logic
- Use modular design with clear interfaces
- Keep header files minimal (declare, don't define)
- Use include guards or `#pragma once`

### Performance Optimization
- Profile before optimizing (measure, don't guess)
- Use const and static for compiler optimization hints
- Minimize volatile usage (only when necessary)
- Prefer lookup tables over calculations for MCU
- Use bitwise operations instead of multiplication/division by powers of 2

### Safety-Critical Development
- Follow MISRA C guidelines
- Use static analysis tools (PC-lint, Coverity, Cppcheck)
- Implement defensive programming (check all inputs)
- Document all MISRA deviations with justification
- Achieve high code coverage (MC/DC for critical paths)

---

## Tools & Environment

### Compilers
- GCC ARM Embedded
- IAR Embedded Workbench
- Keil MDK (ARMCC)
- LLVM/Clang for embedded

### Static Analysis
- PC-lint Plus
- Coverity
- Cppcheck
- Clang Static Analyzer

### Debugging
- GDB + OpenOCD
- Segger J-Link
- ST-Link
- Logic Analyzers (Saleae)

---

## Reference Standards

- **MISRA C:2012**: Motor Industry Software Reliability Association
- **BARR-C:2018**: Embedded C Coding Standard
- **SEI CERT C**: Carnegie Mellon Software Engineering Institute
- **AUTOSAR C++14**: Automotive Open System Architecture
- **DO-178C**: Avionics software safety
- **IEC 61508**: Functional safety for embedded systems

---

## When to Use This Skill

- Developing bare-metal firmware for microcontrollers
- Writing device drivers for sensors, actuators, peripherals
- Optimizing code for memory-constrained systems
- Implementing safety-critical embedded software
- Porting code across different MCU architectures
- Debugging low-level hardware-software integration issues

---

---

## Common Issues & Troubleshooting

### Stack Overflow Detection
```c
/* Detect stack/heap collision at runtime */
extern uint32_t _estack;
extern uint32_t _ebss;

void check_memory_health(void) {
    uint32_t *sp;
    asm volatile ("mov %0, sp" : "=r" (sp));

    /* Calculate free space */
    uint32_t free_bytes = (uint32_t)sp - (uint32_t)&_ebss;

    if (free_bytes < MINIMUM_STACK_MARGIN) {
        /* Stack overflow risk */
        log_error("Stack near overflow");
    }
}
```

### Volatile vs Non-Volatile
```c
/* Memory-mapped register access REQUIRES volatile */
#define REG_STATUS  (*(volatile uint32_t *)0x40000000)

/* Global data modified by ISR REQUIRES volatile */
static volatile uint32_t timer_tick_count = 0;

void SysTick_Handler(void) {
    timer_tick_count++;  /* Without volatile, compiler may optimize away */
}
```

### Debugging Embedded Systems
```c
/* Printf debugging on UART */
#include <stdio.h>

int _write(int file, char *ptr, int len) {
    for (int i = 0; i < len; i++) {
        uart_send_char(ptr[i]);
    }
    return len;
}

/* Conditional compilation for debug */
#ifdef DEBUG
    #define DBG_PRINT(fmt, ...) printf(fmt, ##__VA_ARGS__)
#else
    #define DBG_PRINT(fmt, ...) do {} while(0)
#endif
```

---

## Integration Patterns

### Hardware Abstraction Layer (HAL)
```c
/* Generic GPIO interface */
typedef struct {
    void (*set_high)(void);
    void (*set_low)(void);
    void (*toggle)(void);
} gpio_interface_t;

/* STM32 implementation */
const gpio_interface_t gpio_led = {
    .set_high = stm32_gpio_set_high,
    .set_low = stm32_gpio_set_low,
    .toggle = stm32_gpio_toggle
};

/* Allows testing without hardware */
const gpio_interface_t gpio_led_mock = {
    .set_high = mock_set_high,
    .set_low = mock_set_low,
    .toggle = mock_toggle
};
```

### Module Initialization Pattern
```c
/* Self-contained module with init/deinit */
typedef enum {
    MODULE_STATE_UNINITIALIZED,
    MODULE_STATE_INITIALIZING,
    MODULE_STATE_READY,
    MODULE_STATE_ERROR
} module_state_t;

typedef struct {
    module_state_t state;
    uint32_t error_code;
} module_t;

status_t module_init(module_t *mod) {
    if (mod->state != MODULE_STATE_UNINITIALIZED) {
        return STATUS_ERROR;  /* Already initialized */
    }

    mod->state = MODULE_STATE_INITIALIZING;
    /* Initialization logic */
    mod->state = MODULE_STATE_READY;
    return STATUS_OK;
}

status_t module_deinit(module_t *mod) {
    if (mod->state == MODULE_STATE_UNINITIALIZED) {
        return STATUS_OK;  /* Already de-initialized */
    }

    /* Cleanup logic */
    mod->state = MODULE_STATE_UNINITIALIZED;
    return STATUS_OK;
}
```

---

## Performance Optimization Techniques

### Memory Access Patterns
```c
/* Poor: Random memory access (cache misses) */
for (int i = 0; i < 1000; i++) {
    for (int j = 0; j < 1000; j++) {
        matrix[j][i] += 1;  /* Column-major = poor cache locality */
    }
}

/* Good: Sequential memory access (cache hits) */
for (int i = 0; i < 1000; i++) {
    for (int j = 0; j < 1000; j++) {
        matrix[i][j] += 1;  /* Row-major = good cache locality */
    }
}
```

### ISR Optimization
```c
/* Keep ISR short - defer work to task */
volatile bool g_sensor_data_ready = false;
volatile uint16_t g_sensor_value = 0;

void TIMER_IRQHandler(void) {
    g_sensor_value = ADC_read();
    g_sensor_data_ready = true;  /* Set flag, exit ISR */
    TIMER_clear_flag();
}

void sensor_task(void *param) {
    for (;;) {
        if (g_sensor_data_ready) {
            g_sensor_data_ready = false;
            process_sensor(g_sensor_value);  /* Heavy processing in task */
        }
        vTaskDelay(1);
    }
}
```

---

## Testing Embedded Code

### Unit Testing with Mocks
```c
/* Mock implementation for testing */
int mock_i2c_read(uint8_t addr, uint8_t *data, size_t len) {
    if (addr == 0x68) {  /* MPU6050 */
        data[0] = 0x42;  /* Mock sensor data */
        return 0;  /* Success */
    }
    return -1;  /* Error */
}

/* Test function */
void test_sensor_initialization(void) {
    uint8_t chip_id;
    status_t status = read_chip_id(&chip_id);

    assert(status == STATUS_OK);
    assert(chip_id == 0x42);
}
```

### Integration Testing
```c
/* Test entire subsystem */
void test_temperature_monitoring_system(void) {
    /* Initialize */
    sensor_init();
    filter_init();

    /* Simulate sensor readings */
    for (int i = 0; i < 100; i++) {
        uint16_t raw = adc_simulate_temperature(25.0f + i * 0.1f);
        float filtered = filter_update(raw);

        /* Verify filtering is working */
        assert(fabsf(filtered - (25.0f + i * 0.1f)) < 0.5f);
    }
}
```

---

**Provide production-grade, MISRA-compliant, optimized embedded C/C++ code with comprehensive error handling and hardware awareness.**
