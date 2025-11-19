# Power Management & Energy Optimization - Subskill

**Expert in low-power embedded design, sleep modes, energy harvesting, and battery management**

---

## Expertise Overview

Specialist in power optimization:
- MCU sleep modes (light sleep, deep sleep, hibernation)
- Dynamic voltage and frequency scaling (DVFS)
- Peripheral power management and clock gating
- Battery management systems (Li-Ion, LiPo, NiMH)
- Energy harvesting (solar, piezo, RF, thermal)
- Power profiling and current measurement

---

## Core Skills

### 1. MCU Sleep Modes

**STM32 Low-Power Modes**:
```c
#include "stm32l4xx_hal.h"

/* Enter Stop 2 mode (lowest power with RAM retention) */
void enter_stop2_mode(void) {
    /* Disable SysTick to prevent wake-up */
    HAL_SuspendTick();

    /* Configure wake-up source (e.g., RTC alarm) */
    /* ... */

    /* Enter Stop 2 mode */
    HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);

    /* After wake-up: reconfigure clocks */
    SystemClock_Config();

    /* Resume SysTick */
    HAL_ResumeTick();
}

/* Standby mode (all RAM lost, lowest power) */
void enter_standby_mode(void) {
    /* Enable wake-up pin */
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);

    /* Clear wake-up flag */
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);

    /* Enter Standby */
    HAL_PWR_EnterSTANDBYMode();
}
```

**ESP32 Deep Sleep**:
```c
#include "esp_sleep.h"
#include "driver/rtc_io.h"

void configure_deep_sleep(uint64_t sleep_time_us) {
    /* Wake-up source: Timer */
    esp_sleep_enable_timer_wakeup(sleep_time_us);

    /* Wake-up source: GPIO (e.g., button) */
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_33, 0);  /* Wake on LOW */

    /* Disable power to peripherals */
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);

    /* Enter deep sleep */
    esp_deep_sleep_start();
}

/* Example: Sleep for 10 seconds */
void power_save_mode(void) {
    printf("Entering deep sleep\n");
    configure_deep_sleep(10 * 1000000ULL);  /* 10 seconds */
}
```

### 2. Dynamic Power Management

**Peripheral Clock Gating**:
```c
/* STM32: Disable unused peripheral clocks */
void disable_unused_peripherals(void) {
    /* Disable unused GPIO ports */
    __HAL_RCC_GPIOB_CLK_DISABLE();
    __HAL_RCC_GPIOC_CLK_DISABLE();

    /* Disable unused peripherals */
    __HAL_RCC_SPI2_CLK_DISABLE();
    __HAL_RCC_USART2_CLK_DISABLE();
    __HAL_RCC_TIM3_CLK_DISABLE();
}

/* Enable peripherals only when needed */
void use_peripheral_on_demand(void) {
    /* Enable I2C clock */
    __HAL_RCC_I2C1_CLK_ENABLE();

    /* Use I2C */
    i2c_transaction();

    /* Disable I2C clock */
    __HAL_RCC_I2C1_CLK_DISABLE();
}
```

**Dynamic Voltage and Frequency Scaling**:
```c
typedef enum {
    PERF_MODE_HIGH,    /* 80 MHz, 1.2V */
    PERF_MODE_MEDIUM,  /* 40 MHz, 1.0V */
    PERF_MODE_LOW      /* 16 MHz, 0.9V */
} performance_mode_t;

void set_performance_mode(performance_mode_t mode) {
    switch (mode) {
        case PERF_MODE_HIGH:
            /* Set voltage regulator to Range 1 */
            HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1);

            /* Set system clock to 80 MHz */
            SystemClock_80MHz();
            break;

        case PERF_MODE_LOW:
            /* Set voltage regulator to Range 2 */
            HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE2);

            /* Set system clock to 16 MHz */
            SystemClock_16MHz();
            break;

        default:
            break;
    }
}
```

### 3. Event-Driven Architecture

**Wake on Interrupt Pattern**:
```c
#include "FreeRTOS.h"
#include "task.h"

static volatile bool g_event_occurred = false;

/* GPIO interrupt handler */
void EXTI0_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_0)) {
        __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);
        g_event_occurred = true;
    }
}

/* Low-power task pattern */
void sensor_task(void *param) {
    for (;;) {
        /* Sleep until event */
        while (!g_event_occurred) {
            /* Enter low-power mode (FreeRTOS tickless idle) */
            vTaskDelay(portMAX_DELAY);
        }

        g_event_occurred = false;

        /* Handle event */
        process_sensor_data();
    }
}
```

**FreeRTOS Tickless Idle**:
```c
/* FreeRTOSConfig.h */
#define configUSE_TICKLESS_IDLE    1

/* Pre-sleep processing hook */
void vApplicationSleep(TickType_t xExpectedIdleTime) {
    /* Configure wake-up timer */
    configure_wakeup_timer(xExpectedIdleTime);

    /* Enter low-power mode */
    __WFI();  /* Wait for interrupt */
}
```

### 4. Battery Management

**ADC Battery Voltage Monitoring**:
```c
#define BATTERY_FULL_MV      4200   /* 4.2V */
#define BATTERY_EMPTY_MV     3000   /* 3.0V */
#define ADC_VREF_MV          3300

typedef enum {
    BATTERY_FULL,
    BATTERY_GOOD,
    BATTERY_LOW,
    BATTERY_CRITICAL
} battery_level_t;

uint16_t read_battery_voltage_mv(void) {
    /* Read ADC */
    uint16_t adc_value = adc_read_channel(ADC_CHANNEL_VBAT);

    /* Convert to millivolts (with voltage divider 1:2) */
    uint16_t voltage_mv = (adc_value * ADC_VREF_MV * 2) / 4096;

    return voltage_mv;
}

battery_level_t get_battery_level(void) {
    uint16_t voltage_mv = read_battery_voltage_mv();

    if (voltage_mv >= 4000) {
        return BATTERY_FULL;
    } else if (voltage_mv >= 3700) {
        return BATTERY_GOOD;
    } else if (voltage_mv >= 3400) {
        return BATTERY_LOW;
    } else {
        return BATTERY_CRITICAL;
    }
}

uint8_t get_battery_percentage(void) {
    uint16_t voltage_mv = read_battery_voltage_mv();

    if (voltage_mv >= BATTERY_FULL_MV) {
        return 100;
    } else if (voltage_mv <= BATTERY_EMPTY_MV) {
        return 0;
    }

    /* Linear approximation */
    return ((voltage_mv - BATTERY_EMPTY_MV) * 100) /
           (BATTERY_FULL_MV - BATTERY_EMPTY_MV);
}
```

**Li-Ion Charging (BQ24074)**:
```c
#define CHG_STAT1_PIN    GPIO_PIN_5
#define CHG_STAT2_PIN    GPIO_PIN_6

typedef enum {
    CHG_STATUS_CHARGING,
    CHG_STATUS_COMPLETE,
    CHG_STATUS_FAULT,
    CHG_STATUS_NONE
} charge_status_t;

charge_status_t read_charge_status(void) {
    bool stat1 = gpio_read(CHG_STAT1_PIN);
    bool stat2 = gpio_read(CHG_STAT2_PIN);

    if (!stat1 && !stat2) {
        return CHG_STATUS_FAULT;
    } else if (!stat1 && stat2) {
        return CHG_STATUS_CHARGING;
    } else if (stat1 && !stat2) {
        return CHG_STATUS_COMPLETE;
    } else {
        return CHG_STATUS_NONE;
    }
}
```

### 5. Energy Harvesting

**Solar Panel with MPPT**:
```c
/* BQ25570 Energy Harvesting IC */
#define SOLAR_ADC_CHANNEL    ADC_CHANNEL_1

typedef struct {
    uint16_t voc_mv;         /* Open-circuit voltage */
    uint16_t vmpp_mv;        /* Maximum power point voltage */
    uint16_t vbat_mv;        /* Battery voltage */
    bool harvesting_active;
} solar_harvester_t;

static solar_harvester_t g_solar = {0};

void solar_mppt_update(void) {
    /* Read solar panel voltage */
    uint16_t vsolar_mv = read_adc_voltage_mv(SOLAR_ADC_CHANNEL);

    /* Read battery voltage */
    g_solar.vbat_mv = read_battery_voltage_mv();

    /* MPPT algorithm: Perturb & Observe */
    static uint16_t prev_power = 0;
    static int16_t voltage_step = 50;  /* 50mV steps */

    /* Calculate current power */
    uint16_t current_power = vsolar_mv * get_solar_current_ma();

    if (current_power > prev_power) {
        /* Power increased, continue in same direction */
        g_solar.vmpp_mv += voltage_step;
    } else {
        /* Power decreased, reverse direction */
        voltage_step = -voltage_step;
        g_solar.vmpp_mv += voltage_step;
    }

    prev_power = current_power;

    /* Apply MPPT voltage */
    set_mppt_voltage(g_solar.vmpp_mv);
}
```

### 6. Power Profiling

**Current Measurement with INA219**:
```c
#define INA219_ADDR             0x40
#define INA219_REG_BUS_VOLTAGE  0x02
#define INA219_REG_CURRENT      0x04
#define INA219_REG_POWER        0x03

typedef struct {
    float voltage_v;
    float current_ma;
    float power_mw;
} power_measurement_t;

status_t ina219_read_power(power_measurement_t *meas) {
    uint8_t data[2];

    /* Read bus voltage */
    if (i2c_read_burst(INA219_ADDR, INA219_REG_BUS_VOLTAGE, data, 2) != STATUS_OK) {
        return STATUS_ERROR;
    }

    uint16_t bus_voltage_raw = (data[0] << 8) | data[1];
    meas->voltage_v = (bus_voltage_raw >> 3) * 0.004f;  /* 4mV per LSB */

    /* Read current */
    if (i2c_read_burst(INA219_ADDR, INA219_REG_CURRENT, data, 2) != STATUS_OK) {
        return STATUS_ERROR;
    }

    int16_t current_raw = (int16_t)((data[0] << 8) | data[1]);
    meas->current_ma = current_raw * 0.1f;  /* 0.1mA per LSB (calibrated) */

    /* Calculate power */
    meas->power_mw = meas->voltage_v * meas->current_ma;

    return STATUS_OK;
}
```

---

## Power Optimization Strategies

### 1. Duty Cycling

```c
void low_power_sensor_loop(void) {
    for (;;) {
        /* Wake up */
        enable_peripherals();

        /* Read sensor (5ms) */
        sensor_data_t data = read_sensor();

        /* Transmit (50ms) */
        transmit_data(&data);

        /* Disable peripherals */
        disable_peripherals();

        /* Sleep for 10 seconds */
        deep_sleep(10000);
    }
}

/* Power calculation:
 * Active: 55ms @ 50mA = 2.75 mAh/hour
 * Sleep: 9945ms @ 0.01mA = 0.10 mAh/hour
 * Total: ~2.85 mAh/hour
 * Battery life (2000mAh): ~700 hours (~29 days)
 */
```

### 2. Adaptive Sampling

```c
void adaptive_sampling_task(void) {
    uint32_t sample_interval_ms = 1000;  /* Default 1 second */

    for (;;) {
        float value = read_sensor();

        /* Adapt sampling rate based on change */
        float change_rate = fabsf(value - prev_value);

        if (change_rate > THRESHOLD_HIGH) {
            sample_interval_ms = 100;   /* Fast sampling */
        } else if (change_rate > THRESHOLD_LOW) {
            sample_interval_ms = 1000;  /* Normal sampling */
        } else {
            sample_interval_ms = 10000; /* Slow sampling */
        }

        vTaskDelay(pdMS_TO_TICKS(sample_interval_ms));
    }
}
```

---

## Best Practices

1. **Measure First**: Profile actual current consumption
2. **Sleep Often**: Use sleep modes whenever idle
3. **Event-Driven**: Wake on interrupt, not polling
4. **Peripheral Management**: Disable unused peripherals
5. **Optimize Transmission**: Batch data, reduce TX power
6. **Battery Monitoring**: Track voltage and capacity

---

## References

- STM32 Ultra-Low-Power Design Guide
- ESP32 Power Management Documentation
- TI Battery Management Solutions
- Nordic nRF52 Power Profiler

---

**Design ultra-low-power embedded systems with months to years of battery life through systematic power optimization.**
