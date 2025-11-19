# Power Consumption Measurements

## STM32L4 (Ultra-Low-Power)

| Mode | Current @ 3.3V | Notes |
|------|---------------|--------|
| Run (80 MHz) | 100 µA/MHz = 8 mA | Active processing |
| Sleep | 1.2 mA | CPU stopped, peripherals running |
| Stop 2 | 1.28 µA | RAM retained, RTC running |
| Standby | 0.4 µA | No RAM retention |
| Shutdown | 0.03 µA | Lowest power |

## ESP32

| Mode | Current @ 3.3V | Notes |
|------|---------------|--------|
| Active (TX @ 20dBm) | 170 mA | Wi-Fi transmitting |
| Active (RX) | 95 mA | Wi-Fi receiving |
| Modem sleep | 15-20 mA | Wi-Fi connected, CPU active |
| Light sleep | 0.8 mA | Wi-Fi/BT off, RTC on |
| Deep sleep | 10 µA | ULP co-processor |
| Hibernation | 5 µA | RTC off |

## Nordic nRF52840 (BLE)

| Mode | Current @ 3.3V | Notes |
|------|---------------|--------|
| TX (0 dBm) | 5.3 mA | BLE transmit |
| RX | 5.4 mA | BLE receive |
| System ON idle | 1.5 µA | RAM retained |
| System OFF | 0.4 µA | No RAM retention |

## Battery Life Calculation

**Example**: Sensor with daily wake-up

```
- Deep sleep: 23h 59m @ 10 µA = 239.83 µAh
- Active: 1m @ 50 mA = 0.83 mAh = 830 µAh
- Total per day: 1.07 mAh
- Battery: CR2032 (220 mAh)
- Life: 220 / 1.07 ≈ 205 days
```
