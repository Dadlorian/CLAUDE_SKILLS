# Wireless Protocols Comparison Reference

## Protocol Specifications

### Bluetooth Low Energy (BLE)

| Parameter | BLE 4.x | BLE 5.x |
|-----------|---------|---------|
| Data Rate | 1 Mbps | 2 Mbps (optional) |
| Range | ~100m | ~400m (with Coded PHY) |
| Power | Very Low | Very Low |
| Topology | Star, Mesh | Star, Mesh |
| Packet Size | 27 bytes | 251 bytes |
| Channels | 40 (3 advertising) | 40 |

**BLE Power Consumption:**
```
Advertising: 0.1-1mA (depends on interval)
Connected idle: 0.01-0.1mA
Active transmission: 10-20mA for 1-2ms
```

**Connection Parameters:**
```c
// Fast connection (high power)
conn_interval = 7.5ms
slave_latency = 0
timeout = 4s
Average current: ~1mA

// Balanced
conn_interval = 100ms
slave_latency = 4
timeout = 4s
Average current: ~0.1mA

// Ultra-low power
conn_interval = 1000ms
slave_latency = 10
timeout = 10s
Average current: ~0.01mA
```

### Wi-Fi (802.11)

| Parameter | 802.11b/g/n | 802.11ac | 802.11ax (Wi-Fi 6) |
|-----------|-------------|----------|-------------------|
| Max Data Rate | 54 Mbps | 866 Mbps | 1.2 Gbps |
| Frequency | 2.4 GHz | 5 GHz | 2.4/5 GHz |
| Range | ~100m | ~50m | ~100m |
| Power | High | High | Medium |

**Wi-Fi Power Modes (ESP32):**
```
Active: 80-160mA
Modem sleep: 15-30mA
Light sleep: 0.8mA
Deep sleep: 10µA
```

**When to use Wi-Fi:**
- High data rates needed (video, audio)
- Existing Wi-Fi infrastructure
- Internet connectivity required
- AC power available

### LoRa/LoRaWAN

| Parameter | Value |
|-----------|-------|
| Frequency | 433/868/915 MHz (regional) |
| Data Rate | 0.3 - 50 kbps |
| Range | 2-15 km (urban/rural) |
| Power | Very Low |
| Topology | Star-of-Stars |

**Spreading Factors:**
```
SF7:  5.5 kbps, shortest range
SF8:  3.1 kbps
SF9:  1.8 kbps
SF10: 980 bps
SF11: 440 bps
SF12: 250 bps, longest range

Higher SF = Longer range but slower speed
```

**LoRa Power Consumption:**
```
TX at +20dBm: 120mA for ~1s
TX at +14dBm: 40mA
RX: 10-12mA
Sleep: <1µA

Typical duty cycle (Class A):
- TX 1s every 600s
- Average: ~0.2mA
```

**LoRaWAN Classes:**
```
Class A: Lowest power, bi-directional
  - TX then RX for short windows
  - Best for battery devices

Class B: Scheduled receive windows
  - Synchronized with gateway
  - Moderate power

Class C: Continuous receive
  - Lowest latency
  - Highest power (AC powered)
```

### Zigbee (802.15.4)

| Parameter | Value |
|-----------|-------|
| Frequency | 2.4 GHz |
| Data Rate | 250 kbps |
| Range | 10-100m |
| Power | Low |
| Topology | Mesh |

**Device Types:**
```
Coordinator: Forms network, always on
Router: Forwards packets, always on
End Device: Sleeps between transmissions

Power consumption:
Coordinator/Router: 30-50mA continuous
End Device: 0.5mA average (with sleep)
```

### Cellular IoT

#### NB-IoT (Narrowband IoT)
```
Frequency: Licensed bands
Data Rate: ~200 kbps
Range: Wide area (cellular coverage)
Power: Low-Medium
Latency: 1-10 seconds

Power consumption:
TX: 200-300mA for 1-3s
RX: 50-100mA
PSM (Power Save Mode): <10µA
eDRX (Extended DRX): 1-10mA
```

#### LTE-M (LTE Cat-M1)
```
Data Rate: ~1 Mbps
Power: Medium
Mobility: Full (handover support)

Advantages over NB-IoT:
- Higher data rates
- VoLTE support
- Better latency (<100ms)
```

## Protocol Selection Matrix

| Use Case | Best Protocol | Alternative |
|----------|---------------|-------------|
| Wearables | BLE | Zigbee |
| Home Automation | Zigbee, BLE Mesh | Wi-Fi |
| Industrial Sensors | Zigbee, LoRa | Wi-Fi |
| Asset Tracking | Cellular, LoRa | BLE (short range) |
| Smart Meters | LoRaWAN, NB-IoT | Zigbee |
| Security Cameras | Wi-Fi | Cellular |
| Agricultural Sensors | LoRa | NB-IoT |

## Range vs Data Rate

```
|
|                Wi-Fi (802.11ax)
|               /
|              /
Data     Zigbee
Rate          \
|              \   NB-IoT/LTE-M
|               \  /
|             BLE/
|                \
|                 LoRa
|__________________________
           Range
```

## Coexistence Issues

### 2.4 GHz Band (Crowded!)
```
BLE: Channels 0-39 (2402-2480 MHz)
Wi-Fi: Channels 1-13 (2412-2472 MHz)
Zigbee: Channels 11-26 (2405-2480 MHz)

Recommended Zigbee channels: 15, 20, 25
(Least overlap with Wi-Fi channels 1, 6, 11)
```

### Mitigation Strategies
```c
// BLE: Use adaptive frequency hopping
// Wi-Fi: Configure fixed channel
// Zigbee: Select non-overlapping channel

// ESP32: Enable BLE/Wi-Fi coexistence
esp_coex_preference_set(ESP_COEX_PREFER_BALANCE);
```

## Security Comparison

| Protocol | Encryption | Authentication | Key Length |
|----------|-----------|----------------|------------|
| BLE | AES-CCM | Pairing/Bonding | 128-bit |
| Wi-Fi | WPA2/WPA3 | PSK/Enterprise | 128/256-bit |
| Zigbee | AES-CCM | Network Key | 128-bit |
| LoRaWAN | AES-128 | Device/App Keys | 128-bit |
| NB-IoT | LTE Security | SIM-based | 128/256-bit |

## Antenna Considerations

### Antenna Types
```
Chip Antenna:
- Small footprint
- Moderate performance
- Cheaper

PCB Antenna:
- No extra cost
- Design-dependent performance
- Sensitive to layout

External Antenna:
- Best performance
- Larger size
- Higher cost
```

### Antenna Placement
```
DO:
✓ Keep away from large metal objects
✓ Place at edge of PCB
✓ Orient for best radiation pattern
✓ Use ground plane

DON'T:
✗ Place near DC-DC converter
✗ Route traces underneath
✗ Block with metal housing
```

## Practical Examples

### Example 1: Smart Thermostat
```
Requirements:
- Always-on connection
- Low latency control
- Firmware updates
- AC powered

Solution: Wi-Fi
- Fast response times
- OTA updates easy
- Connect to home network
- Power not a concern
```

### Example 2: Wireless Sensor Network
```
Requirements:
- 100+ sensors
- Battery powered (5+ years)
- Long range (1 km)
- Low data rate

Solution: LoRaWAN
- Excellent range
- Ultra-low power
- Scalable network
- Public/private networks available
```

### Example 3: BLE Beacon
```
Requirements:
- Broadcast only
- Proximity detection
- 1-year on coin cell
- Low cost

Solution: BLE Advertising
- Non-connectable mode
- 1s advertising interval
- CR2032 battery sufficient
- Wide ecosystem support
```

### Example 4: Industrial Control
```
Requirements:
- Deterministic latency
- Mesh networking
- Industrial environment
- Moderate range

Solution: WirelessHART or Zigbee
- Industrial-grade reliability
- Mesh for redundancy
- 2.4 GHz or sub-GHz
- Proven in harsh environments
```

## Testing and Certification

### FCC (USA)
```
Part 15.247: Intentional radiators (2.4 GHz, ISM)
Part 15.407: UWB devices

Tests:
- Conducted emissions
- Radiated emissions
- Bandwidth
- Power spectral density
```

### CE (Europe)
```
RED Directive 2014/53/EU
EN 300 328: Wideband transmission (2.4 GHz)
EN 301 489: EMC for radio equipment

Tests:
- RF spectrum
- Effective radiated power
- Spurious emissions
- EMC immunity/emissions
```

### Certification Shortcuts
```
1. Use pre-certified modules (no RF testing)
2. Design with reference designs
3. Use certified antennas
4. Follow layout guidelines strictly
```

## Practical Tips

### BLE
```c
// Reduce connection interval for power savings
ble_gap_conn_params_t params = {
    .min_conn_interval = MSEC_TO_UNITS(1000, UNIT_1_25_MS),
    .max_conn_interval = MSEC_TO_UNITS(1000, UNIT_1_25_MS),
    .slave_latency = 4,
    .conn_sup_timeout = MSEC_TO_UNITS(4000, UNIT_10_MS)
};
```

### LoRa
```c
// Adaptive Data Rate (ADR) for optimal settings
lora_set_adr(true);

// Use lowest SF that still works
lora_set_spreading_factor(7);  // Fastest

// Reduce TX power when close to gateway
lora_set_tx_power(2);  // +2 dBm instead of +14
```

### Wi-Fi
```c
// Power save mode
esp_wifi_set_ps(WIFI_PS_MAX_MODEM);

// Reduce TX power indoors
esp_wifi_set_max_tx_power(40);  // 10 dBm instead of 20

// Use static IP to avoid DHCP delays
tcpip_adapter_dhcpc_stop(TCPIP_ADAPTER_IF_STA);
tcpip_adapter_set_ip_info(TCPIP_ADAPTER_IF_STA, &ip_info);
```

## Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| Short range | Antenna mismatch | Use proper impedance matching |
| High power | Constant scanning | Duty cycle radio operations |
| Packet loss | Interference | Change channel/frequency |
| Can't pair BLE | Wrong security | Check pairing requirements |
| LoRa no downlink | Duty cycle violated | Respect 1% duty cycle limit |
| Wi-Fi drops | Weak signal | Use external antenna |
