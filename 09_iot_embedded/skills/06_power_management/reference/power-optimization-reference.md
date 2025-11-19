# Power Optimization Quick Reference

## MCU Power Consumption Comparison

| MCU | Active (MHz) | Light Sleep | Deep Sleep | Standby |
|-----|--------------|-------------|------------|---------|
| STM32L4 | 100µA/MHz | 7µA | 1µA | 0.03µA |
| ESP32 | 240µA/MHz | 0.8mA | 10µA | 5µA |
| nRF52840 | 65µA/MHz | 60µA | 1.5µA | 0.5µA |
| ATmega328P | 200µA/MHz | 25µA | 4µA | 0.1µA |

## Sleep Mode Comparison

### STM32L4 Sleep Modes
```
RUN mode: Full operation, all peripherals available
SLEEP: CPU stopped, peripherals running
STOP 0: Most clocks stopped, SRAM retained, wake ~5µs
STOP 1: Lower power than STOP 0, wake ~5µs
STOP 2: Lowest with SRAM retention, wake ~20µs
STANDBY: Everything off, wake ~50ms
SHUTDOWN: All off except backup domain, <27nA
```

### ESP32 Sleep Modes
```c
// Light Sleep: CPU paused, peripherals may run
esp_light_sleep_start();  // ~0.8mA

// Deep Sleep: Most systems off, wake from RTC/GPIO
esp_deep_sleep_start();   // ~10µA

// Hibernation: Ultra-low power
esp_sleep_pd_config(ESP_PD_DOMAIN_MAX, ESP_PD_OPTION_OFF);
esp_deep_sleep_start();   // ~5µA
```

### Nordic nRF52 Sleep Modes
```c
// System ON: All peripherals available (2mA)
// System OFF: Ultra-low power, wake from GPIO (0.5µA)
sd_power_system_off();
```

## Battery Life Calculation

### Formula
```
Battery Life (hours) = Battery Capacity (mAh) / Average Current (mA)
```

### Duty Cycle Calculation
```
Average Current = (I_active * T_active + I_sleep * T_sleep) / (T_active + T_sleep)
```

### Example
```
Battery: 2000mAh Li-Ion
Active: 50mA for 100ms every 10 seconds
Sleep: 10µA (0.01mA) for 9900ms

Average = (50 * 100 + 0.01 * 9900) / 10000
        = (5000 + 99) / 10000
        = 5099 / 10000
        = 0.51 mA

Life = 2000 / 0.51 = 3922 hours = 163 days
```

## Voltage Regulator Efficiency

| Regulator Type | Efficiency | Quiescent Current | Best Use |
|----------------|-----------|-------------------|----------|
| Linear (LDO) | 60-90% | 1-50µA | Low dropout, low current |
| Buck (switching) | 85-95% | 10-100µA | High current, efficiency |
| Boost | 80-90% | 10-50µA | Step-up voltage |
| Buck-Boost | 80-90% | 20-100µA | Wide input range |

## Dynamic Voltage Scaling

### STM32L4 Voltage Ranges
```c
// Range 1: 1.2V, max 80 MHz
HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1);

// Range 2: 1.0V, max 26 MHz (lower power)
HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE2);
```

### Power vs Frequency
```
Power ∝ Frequency * Voltage²

Example:
80 MHz @ 1.2V: P = 80 * 1.2² = 115 (relative)
40 MHz @ 1.0V: P = 40 * 1.0² = 40  (relative)

Savings: 65% power reduction
```

## Clock Gating Example

```c
/* STM32: Disable unused peripherals */
void minimize_power(void) {
    // Disable unused GPIO ports
    __HAL_RCC_GPIOB_CLK_DISABLE();
    __HAL_RCC_GPIOC_CLK_DISABLE();
    __HAL_RCC_GPIOD_CLK_DISABLE();

    // Disable unused peripherals
    __HAL_RCC_SPI2_CLK_DISABLE();
    __HAL_RCC_USART2_CLK_DISABLE();
    __HAL_RCC_TIM3_CLK_DISABLE();
    __HAL_RCC_ADC1_CLK_DISABLE();
}

/* ESP32: Disable power domains */
void esp32_power_down(void) {
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_SLOW_MEM, ESP_PD_OPTION_OFF);
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_FAST_MEM, ESP_PD_OPTION_OFF);
}
```

## Wake-Up Sources

### STM32L4
```c
// RTC Alarm
HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, 10, RTC_WAKEUPCLOCK_CK_SPRE_16BITS);

// External Interrupt (GPIO)
HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);

// LPUART
__HAL_RCC_LPUART1_CLK_ENABLE();
```

### ESP32
```c
// Timer wakeup
esp_sleep_enable_timer_wakeup(10 * 1000000); // 10 sec

// GPIO wakeup
esp_sleep_enable_ext0_wakeup(GPIO_NUM_33, 0); // LOW level

// Touchpad wakeup
esp_sleep_enable_touchpad_wakeup();

// ULP wakeup
esp_sleep_enable_ulp_wakeup();
```

## Battery Monitoring

### ADC Voltage Divider
```
VDD (4.2V max)
    |
   [R1]  e.g., 100kΩ
    |
    +----> ADC input (3.3V max)
    |
   [R2]  e.g., 100kΩ
    |
   GND

Voltage = ADC_reading * (VDD_ref / ADC_max) * (R1 + R2) / R2
```

### Li-Ion State of Charge
```
Voltage-based (approximate):
4.2V = 100%
4.0V = 80%
3.8V = 60%
3.6V = 40%
3.4V = 20%
3.0V = 0%

More accurate: Use fuel gauge IC (e.g., MAX17048, BQ27441)
```

### Coulomb Counting
```c
// Track battery discharge
float mAh_consumed = 0;

void update_battery(float current_mA, float dt_hours) {
    mAh_consumed += current_mA * dt_hours;

    float remaining = BATTERY_CAPACITY_MAH - mAh_consumed;
    uint8_t soc = (remaining / BATTERY_CAPACITY_MAH) * 100;
}
```

## Peripheral Power Optimization

### UART
```c
// Use low-power UART (LPUART) if available
// Reduce baud rate: lower = less power
// Use DMA to avoid CPU wake-ups
// Disable TX when not transmitting
```

### I2C
```c
// Reduce I2C clock speed (100 kHz vs 400 kHz)
// Use internal pull-ups if available (weaker = less current)
// Put sensors to sleep when idle
// Use DMA for transfers
```

### SPI
```c
// Disable SPI when not in use
// Use hardware CS (chip select) to save transitions
// Reduce SPI clock speed
// Use DMA for large transfers
```

### ADC
```c
// Use lower resolution (8-bit vs 12-bit)
// Reduce sampling frequency
// Use DMA + circular buffer
// Power down between conversions
```

## Wireless Power Optimization

### BLE
```
Connection Interval: Longer = less power
  - 7.5ms: ~1mA average
  - 100ms: ~0.1mA average
  - 1000ms: ~0.01mA average

TX Power:
  - 0 dBm: 10mA
  - -12 dBm: 5mA
  - -20 dBm: 3mA

Advertising:
  - Fast (20ms): ~200µA
  - Slow (1s): ~10µA
```

### Wi-Fi (ESP32)
```c
// Modem sleep: 15-30mA
esp_wifi_set_ps(WIFI_PS_MIN_MODEM);

// Light sleep: 0.8mA
esp_wifi_set_ps(WIFI_PS_MAX_MODEM);

// Deep sleep between transmissions: 10µA
// Turn off Wi-Fi completely when not needed
esp_wifi_stop();
```

### LoRa
```
TX Current: 20-120mA (depends on TX power)
RX Current: 10-15mA
Sleep: <1µA

Duty Cycle Strategy:
  - TX for 100ms every 60 seconds
  - Average: ~0.2mA
```

## Power Profiling Tools

### Hardware Tools
- Nordic Power Profiler Kit II ($100)
- Joulescope JS220 ($900)
- Otii Arc ($500)
- μCurrent Gold ($65)

### Software Tools
```c
// STM32CubeMonitor-Power (free)
// Segger SystemView (free for evaluation)
// Energy Profiler (Simplicity Studio for EFM32)
```

### DIY Power Measurement
```
[Battery] ---[Shunt Resistor 0.1Ω]--- [Device]
                      |
                  Measure voltage
                  I = V / R
```

## Common Power Bugs

| Issue | Symptom | Fix |
|-------|---------|-----|
| Floating GPIO | High current | Enable pull-up/down |
| Peripheral not disabled | Can't sleep | Disable clocks |
| Debug enabled | 5-10mA extra | Disable SWD/JTAG |
| LED on | mA wasted | Turn off or PWM dim |
| Pull-ups too strong | mA wasted | Use 10kΩ instead of 1kΩ |
| Voltage regulator inefficient | Battery drains fast | Use buck converter |

## Best Practices Checklist

- [ ] Disable unused peripherals
- [ ] Use lowest clock speed possible
- [ ] Implement sleep modes
- [ ] Duty cycle operations
- [ ] Disable debug interface in production
- [ ] Use DMA to avoid CPU wake-ups
- [ ] Configure GPIO to minimize leakage
- [ ] Use hardware timers for wake-up
- [ ] Batch wireless transmissions
- [ ] Profile actual power consumption
- [ ] Test at temperature extremes
- [ ] Document power budget

## Quick Power Estimates

### Example: Weather Station
```
Components:
- MCU (STM32L4): Active 10s/hour @ 10mA = 0.028mAh/hour
- MCU Deep Sleep: 3590s/hour @ 1µA = 0.001mAh/hour
- Sensors: 10s/hour @ 5mA = 0.014mAh/hour
- LoRa TX: 5s/hour @ 100mA = 0.139mAh/hour
- LoRa Sleep: 3595s/hour @ 1µA = 0.001mAh/hour

Total: ~0.183 mAh/hour

2000mAh battery: 2000 / 0.183 = 10929 hours = 455 days
```
