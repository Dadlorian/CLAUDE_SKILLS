# Low-Power Embedded System Design Guide

## Introduction

This guide provides a systematic approach to designing ultra-low-power embedded systems that can run for months or years on battery power.

## Target: 1-Year Battery Life Example

**Requirements:**
- Battery: 2000mAh Li-Ion
- Measurement: Every 60 seconds
- Wireless transmission: Every 10 minutes

**Power Budget:**
```
2000mAh / (365 * 24) = 0.228 mAh/hour = 228 µAh/hour

This means average current must be < 228µA
```

## Step-by-Step Power Optimization

### 1. Select Low-Power MCU

**Comparison:**
- STM32L4: Best for battery (1µA deep sleep)
- ESP32: Good for Wi-Fi but higher power (10µA deep sleep)
- nRF52: Excellent for BLE (0.5µA system-off)
- ATmega: Very low but limited features (0.1µA standby)

**Selection Criteria:**
1. Deep sleep current
2. Wake-up time
3. Peripheral power consumption
4. Available sleep modes

### 2. Design Power States

```c
typedef enum {
    STATE_MEASURE,      // 100ms, 10mA
    STATE_TRANSMIT,     // 1s, 50mA
    STATE_DEEP_SLEEP    // 59s, 1µA
} system_state_t;

// Power calculation:
// Measure: (100ms / 60000ms) * 10mA = 0.017mA
// Transmit: (1000ms / 600000ms) * 50mA = 0.083mA
// Sleep: (59000ms / 60000ms) * 0.001mA = 0.001mA
// Total: 0.101mA = 101µA

// Battery life: 2000mAh / 0.101mA = 19802 hours = 825 days!
```

### 3. Implement Sleep Modes

**STM32 Example:**
```c
void enter_deep_sleep_with_rtc(uint32_t seconds) {
    // Configure RTC wake-up
    HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, seconds,
                                RTC_WAKEUPCLOCK_CK_SPRE_16BITS);

    // Suspend SysTick
    HAL_SuspendTick();

    // Enter STOP2 mode
    HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);

    // After wake-up: reconfigure system clock
    SystemClock_Config();

    // Resume SysTick
    HAL_ResumeTick();
}
```

**ESP32 Example:**
```c
void enter_deep_sleep_esp32(uint64_t time_us) {
    // Configure wake sources
    esp_sleep_enable_timer_wakeup(time_us);

    // Power down unnecessary domains
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_SLOW_MEM, ESP_PD_OPTION_OFF);
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_FAST_MEM, ESP_PD_OPTION_OFF);

    // Enter deep sleep
    esp_deep_sleep_start();
}
```

### 4. Peripheral Management

**Pattern: Enable-Use-Disable**
```c
void read_sensor_optimized(void) {
    // Enable peripheral power
    __HAL_RCC_I2C1_CLK_ENABLE();

    // Enable sensor power via GPIO
    HAL_GPIO_WritePin(SENSOR_PWR_GPIO_Port, SENSOR_PWR_Pin, GPIO_PIN_SET);
    HAL_Delay(10);  // Sensor power-on time

    // Read sensor
    bme280_read(&sensor, &data);

    // Disable sensor power
    HAL_GPIO_WritePin(SENSOR_PWR_GPIO_Port, SENSOR_PWR_Pin, GPIO_PIN_RESET);

    // Disable peripheral clock
    __HAL_RCC_I2C1_CLK_DISABLE();
}
```

### 5. Wireless Optimization

**LoRa Power Profile:**
```c
void lora_transmit_optimized(const uint8_t *data, uint8_t len) {
    // Wake LoRa module
    lora_wakeup();
    HAL_Delay(5);  // Wake-up time

    // Set to lowest TX power that still works (-2 dBm)
    lora_set_tx_power(-2);

    // Transmit
    lora_send(data, len);

    // Wait for TX complete
    while (!lora_tx_done());

    // Put to sleep immediately
    lora_sleep();
}

// Power savings:
// TX at +20dBm: 120mA
// TX at -2dBm: 25mA
// Savings: 95mA (79% reduction)
```

**BLE Connection Parameters:**
```c
// Optimize for low power
ble_gap_conn_params_t conn_params = {
    .min_conn_interval = MSEC_TO_UNITS(1000, UNIT_1_25_MS),  // 1 second
    .max_conn_interval = MSEC_TO_UNITS(1000, UNIT_1_25_MS),
    .slave_latency = 4,  // Skip 4 connection events
    .conn_sup_timeout = MSEC_TO_UNITS(4000, UNIT_10_MS)
};

// Effective interval: 5 seconds
// Average current: ~20µA (from ~1mA at 100ms interval)
```

### 6. Sensor Duty Cycling

```c
typedef struct {
    uint32_t active_time_ms;
    uint32_t sleep_time_ms;
    float active_current_ma;
    float sleep_current_ma;
} duty_cycle_config_t;

float calculate_average_current(duty_cycle_config_t *config) {
    uint32_t total_time = config->active_time_ms + config->sleep_time_ms;

    float avg = (config->active_current_ma * config->active_time_ms +
                 config->sleep_current_ma * config->sleep_time_ms) / total_time;

    return avg;
}

// Example: Environmental sensor
// Active 100ms every 60s: 5mA active, 0.001mA sleep
// Average: (5*100 + 0.001*59900) / 60000 = 0.084mA
```

### 7. GPIO Configuration

```c
void configure_gpios_for_low_power(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // Enable all GPIO clocks
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    // Configure unused pins as analog (lowest power)
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;

    // All pins of GPIOB (if unused)
    GPIO_InitStruct.Pin = GPIO_PIN_All;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    // Configure used pins appropriately
    // Input with pull-up/down to prevent floating
    GPIO_InitStruct.Pin = BUTTON_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(BUTTON_GPIO_Port, &GPIO_InitStruct);
}
```

### 8. Voltage Regulator Selection

**Trade-offs:**

| Type | Efficiency | Iq (µA) | Cost | Use Case |
|------|-----------|---------|------|----------|
| LDO | 60-90% | 1-50 | Low | Vin-Vout <0.5V |
| Buck | 85-95% | 10-100 | Med | Step down, I>50mA |
| Boost | 80-90% | 10-50 | Med | Step up |

**Recommendation:**
- Use buck converter for main power (high efficiency)
- Use LDO for sensitive analog (low noise)

## Testing and Validation

### Power Measurement Setup

```
[Battery Holder] ---> [Current Meter] ---> [Device]
                           |
                    Log to computer
```

**Tools:**
- Nordic PPK2: Best for detailed profiling
- USB power meter: Quick checks
- Oscilloscope + shunt resistor: DIY

### Test Cases

1. **Idle Current:**
   - All peripherals off
   - Deep sleep mode
   - Should match datasheet (±50%)

2. **Active Current:**
   - CPU running at max frequency
   - All peripherals enabled
   - Verify against calculations

3. **Real-World Scenario:**
   - Run full application cycle
   - Measure over extended period (hours)
   - Calculate battery life

### Common Issues

**Problem: Higher than expected sleep current**

Solutions:
- Check for floating GPIO pins
- Verify all peripherals are disabled
- Disable debug interface (SWD/JTAG)
- Check for current leakage through pull-ups
- Verify sensors are in sleep mode

**Problem: Can't achieve deep sleep**

Solutions:
- Check interrupt flags are cleared
- Verify DMA transfers are complete
- Ensure UART transmissions finished
- Check for pending system events

## Real-World Examples

### Example 1: Weather Station
```
Requirements:
- Measure temp/humidity/pressure every 60s
- Transmit via LoRa every 10 minutes
- 2000mAh battery, 2-year life target

Solution:
- STM32L4 in STOP2 mode: 1µA
- BME280 forced mode: 3µA average
- RFM95W LoRa sleep: 0.2µA
- Active (1s every 60s): 10mA → 0.167mA avg
- TX (2s every 600s): 100mA → 0.333mA avg

Total average: ~0.5mA
Battery life: 2000/0.5 = 4000 hours = 166 days

To reach 2 years: need to reduce to 0.23mA
- Reduce TX power
- Increase measurement interval to 120s
- Increase TX interval to 20 minutes
```

### Example 2: Asset Tracker
```
Requirements:
- GPS fix every 5 minutes
- Transmit via cellular every 15 minutes
- 5000mAh battery, 1-month life target

Solution:
- nRF52840 system-off: 0.5µA
- GPS fix (30s): 50mA
- Cellular TX (10s): 200mA
- Sleep (290s): 0.001mA

Average per cycle (300s):
= (50*30 + 200*10 + 0.001*260) / 300
= (1500 + 2000 + 0.26) / 300
= 11.67mA

Battery life: 5000/11.67 = 428 hours = 17.8 days

To reach 30 days: need 6.94mA average
- Use GPS assist (faster fix)
- Reduce cellular connection time
- Implement motion detection (only TX when moving)
```

## Checklist for Production

- [ ] All unused GPIO configured (analog or pulled)
- [ ] Debug interface disabled in production firmware
- [ ] All peripheral clocks disabled when not in use
- [ ] Sensors put to sleep between measurements
- [ ] Wireless module in sleep mode when idle
- [ ] RTC used for wake-up timing
- [ ] Battery voltage monitoring implemented
- [ ] Low-battery shutdown implemented
- [ ] Power profiling completed
- [ ] Temperature testing completed (-20°C to +60°C)
- [ ] Long-term battery life test (1+ weeks)
- [ ] EMC testing passed (if required)

## Advanced Techniques

### 1. Energy Harvesting
```c
// Check if enough energy available before operation
if (battery_voltage_mv > ENERGY_THRESHOLD_MV) {
    perform_measurement();
    transmit_data();
} else {
    // Skip this cycle, save energy
    deep_sleep(EXTENDED_SLEEP_TIME);
}
```

### 2. Adaptive Sampling
```c
// Sample faster when value changing, slower when stable
if (abs(current_value - previous_value) > CHANGE_THRESHOLD) {
    sample_interval = FAST_INTERVAL;  // 10s
} else {
    sample_interval = SLOW_INTERVAL;  // 300s
}
```

### 3. Predictive Wake-up
```c
// Learn usage patterns, wake up just before user needs data
if (time_of_day >= 8*3600 && time_of_day <= 17*3600) {
    // Business hours: more frequent updates
    sleep_time = 60;  // seconds
} else {
    // After hours: less frequent
    sleep_time = 300;
}
```

## Resources

- Application notes from MCU manufacturers
- Power profiling tools documentation
- Battery chemistry datasheets
- Reference designs from dev boards
