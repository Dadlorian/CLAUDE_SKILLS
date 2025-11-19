# Hardware Design Guidelines for Embedded IoT

## Power Supply Design

### Linear Regulators (LDO)
- **Use**: Low noise, simple, < 500mA
- **Efficiency**: (Vout/Vin) * 100%
- **Dropout**: Min 200mV headroom
- **Example**: ADP150 (3.3V, 200mA, 0.9µA quiescent)

### Switching Regulators
- **Use**: High efficiency, > 100mA
- **Efficiency**: 85-95% typical
- **Components**: Input/output caps, inductor
- **Example**: TPS62840 (750mA, 60nA quiescent)

## Decoupling Capacitors

**Rules**:
- 100nF ceramic per IC power pin
- 10µF bulk near each IC
- Place < 5mm from power pins
- Use X7R or X5R dielectric (not Y5V)

## Crystal Oscillator Layout

- Keep traces < 10mm
- Guard with ground
- No vias under crystal
- Add loading capacitors (15-20pF typical)

## PCB Stack-up (4-layer recommended)

```
Layer 1: Signal (top)
Layer 2: Ground plane
Layer 3: Power plane (3.3V, 1.8V)
Layer 4: Signal (bottom)
```

## Antenna Design

### PCB Antenna
- Clearance: 3-5mm all sides
- Ground plane: Remove under antenna
- Match impedance: 50Ω
- Test with VNA

### U.FL Connector
- Use for external antenna
- 50Ω trace to connector
- Ground vias around connector

## EMC/EMI Mitigation

1. **Ground plane**: Continuous, no slots
2. **Trace routing**: Avoid right angles
3. **Decoupling**: Close to IC pins
4. **Ferrite beads**: On power lines
5. **Shielding**: RF sections
