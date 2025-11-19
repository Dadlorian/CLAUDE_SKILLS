# Sensor Integration Quick Reference

## Common I2C Sensors

### BME280 - Environmental Sensor
```
I2C Address: 0x76 or 0x77
Measures: Temperature, Humidity, Pressure
Interface: I2C/SPI
Power: 1.7-3.6V, ~3.6µA @ 1Hz sampling
```

**Quick Init:**
```c
bme280_t sensor;
bme280_init(&sensor, 0x76);
bme280_data_t data;
bme280_read(&sensor, &data);
// data.temperature in °C * 100
// data.pressure in Pa
// data.humidity in %RH * 1024
```

### MPU6050 - 6-Axis IMU
```
I2C Address: 0x68 or 0x69
Measures: 3-axis accelerometer, 3-axis gyroscope, temperature
Interface: I2C
Power: 2.375-3.46V, ~3.8mA active
```

**Accelerometer Ranges:**
- ±2g (16384 LSB/g)
- ±4g (8192 LSB/g)
- ±8g (4096 LSB/g)
- ±16g (2048 LSB/g)

**Gyroscope Ranges:**
- ±250°/s (131 LSB/°/s)
- ±500°/s (65.5 LSB/°/s)
- ±1000°/s (32.8 LSB/°/s)
- ±2000°/s (16.4 LSB/°/s)

### VL53L0X - ToF Distance Sensor
```
I2C Address: 0x29 (changeable)
Range: 30mm - 2000mm
Accuracy: ±3% @ 2m
Power: 2.6-3.5V, ~19mA continuous
```

**Quick Measurement:**
```c
vl53l0x_t sensor;
vl53l0x_init(&sensor, 0x29);
vl53l0x_start_ranging(&sensor, VL53L0X_MODE_CONTINUOUS);
vl53l0x_measurement_t meas;
vl53l0x_read_distance(&sensor, &meas);
// meas.distance_mm contains distance
```

## SPI Sensors

### LSM6DSL - 6-Axis IMU (SPI/I2C)
```
SPI Mode: Mode 0 or Mode 3
Max Clock: 10 MHz
CS: Active low
```

**SPI Read:**
- Set MSB of register address to 1 for read
- For multi-byte read, set bit 1 to 1

**SPI Write:**
- Clear MSB of register address
- Single byte writes only

## Analog Sensors (ADC)

### NTC Thermistor
**Steinhart-Hart Equation:**
```
1/T = A + B*ln(R) + C*ln(R)³
```
Where:
- T = temperature in Kelvin
- R = resistance in Ohms
- A, B, C = calibration coefficients

**Typical 10kΩ NTC Coefficients:**
- A = 0.001129148
- B = 0.000234125
- C = 0.0000000876741

### Photoresistor (LDR)
**Resistance vs Lux:**
```
R = R_10lux * (Lux / 10)^-γ
```
- γ ≈ 0.7 for typical LDRs
- R_10lux ≈ 10kΩ

## Digital Filters

### Moving Average Filter
```c
float moving_average(float new_sample, float *buffer, int size) {
    static int index = 0;
    buffer[index] = new_sample;
    index = (index + 1) % size;

    float sum = 0;
    for (int i = 0; i < size; i++) {
        sum += buffer[i];
    }
    return sum / size;
}
```

### Exponential Moving Average (EMA)
```c
float ema_filter(float new_sample, float prev_avg, float alpha) {
    return alpha * new_sample + (1 - alpha) * prev_avg;
}
// alpha = 0.1 for slow response (heavy filtering)
// alpha = 0.9 for fast response (light filtering)
```

### Low-Pass Filter (1st order)
```c
float low_pass_filter(float input, float prev_output, float dt, float tau) {
    float alpha = dt / (tau + dt);
    return alpha * input + (1 - alpha) * prev_output;
}
// tau = time constant (seconds)
// Lower tau = faster response
```

## Kalman Filter (1D)

**State Equations:**
```
Prediction:
  x_pred = x
  P_pred = P + Q

Update:
  K = P_pred / (P_pred + R)
  x = x_pred + K * (measurement - x_pred)
  P = (1 - K) * P_pred
```

Where:
- x = state estimate
- P = estimation error covariance
- Q = process noise covariance
- R = measurement noise covariance
- K = Kalman gain

**Implementation:**
```c
typedef struct {
    float x, P, Q, R;
} kalman_1d_t;

void kalman_init(kalman_1d_t *kf, float q, float r) {
    kf->x = 0;
    kf->P = 1;
    kf->Q = q;  // process noise (0.001 - 0.1)
    kf->R = r;  // measurement noise (0.1 - 10.0)
}

float kalman_update(kalman_1d_t *kf, float measurement) {
    // Prediction
    kf->P += kf->Q;

    // Update
    float K = kf->P / (kf->P + kf->R);
    kf->x += K * (measurement - kf->x);
    kf->P *= (1 - K);

    return kf->x;
}
```

## Sensor Fusion - Complementary Filter

**For IMU (Accel + Gyro):**
```c
void complementary_filter(float *roll, float *pitch,
                          float accel_roll, float accel_pitch,
                          float gyro_x, float gyro_y,
                          float dt, float alpha) {
    // Integrate gyro
    *roll += gyro_x * dt;
    *pitch += gyro_y * dt;

    // Blend with accelerometer
    *roll = alpha * (*roll) + (1 - alpha) * accel_roll;
    *pitch = alpha * (*pitch) + (1 - alpha) * accel_pitch;
}
// alpha = 0.98 (typical)
// Higher alpha = trust gyro more
```

## Sensor Calibration

### Offset Calibration (Zero-Point)
```c
void calibrate_offset(float *samples, int count, float *offset) {
    float sum = 0;
    for (int i = 0; i < count; i++) {
        sum += samples[i];
    }
    *offset = sum / count;
}
```

### Gain Calibration (Scale)
```c
void calibrate_gain(float measured, float reference, float *gain) {
    *gain = reference / measured;
}
```

### Two-Point Calibration
```c
void calibrate_two_point(float measured_low, float reference_low,
                         float measured_high, float reference_high,
                         float *gain, float *offset) {
    *gain = (reference_high - reference_low) /
            (measured_high - measured_low);
    *offset = reference_low - (*gain) * measured_low;
}

float apply_calibration(float raw, float gain, float offset) {
    return raw * gain + offset;
}
```

## Power Management

### Sensor Sleep Modes
```c
// BME280: Force mode (single measurement then sleep)
i2c_write_reg(BME280_ADDR, BME280_REG_CTRL_MEAS, 0x01);

// MPU6050: Sleep mode
i2c_write_reg(MPU6050_ADDR, MPU6050_REG_PWR_MGMT_1, 0x40);

// MPU6050: Wake up
i2c_write_reg(MPU6050_ADDR, MPU6050_REG_PWR_MGMT_1, 0x00);
```

### Duty Cycling
```c
void sensor_duty_cycle(void) {
    // Wake sensor
    sensor_wake();
    delay_ms(10);  // Stabilization time

    // Read measurement
    float value = sensor_read();

    // Put to sleep
    sensor_sleep();

    // Long sleep (e.g., 10 seconds)
    deep_sleep_ms(10000);
}
```

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Noisy readings | Electrical noise | Add capacitor near sensor VDD |
| I2C timeouts | Pull-up resistors | Use 4.7kΩ pull-ups on SDA/SCL |
| Drift over time | Temperature sensitivity | Implement temp compensation |
| Spikes in data | EMI | Use shielded cables, twisted pairs |
| Incorrect values | Wrong scaling | Verify datasheet LSB values |
| Sensor not detected | Address conflict | Check if ADO/SA0 pin is correct |

## Typical Sampling Rates

| Sensor Type | Typical Rate | Notes |
|-------------|--------------|-------|
| Temperature | 0.1 - 1 Hz | Slow thermal response |
| Humidity | 0.1 - 1 Hz | Slow response time |
| Pressure | 1 - 10 Hz | Weather monitoring |
| Accelerometer | 50 - 1000 Hz | Motion detection |
| Gyroscope | 100 - 1000 Hz | Angular velocity |
| Magnetometer | 10 - 100 Hz | Compass heading |
| Distance (ToF) | 10 - 50 Hz | Object detection |
| Light | 1 - 10 Hz | Ambient lighting |

## Best Practices

1. **Always check return values** from sensor functions
2. **Implement timeouts** for I2C/SPI transactions
3. **Calibrate sensors** at startup and periodically
4. **Filter noisy data** before use
5. **Add sensor health monitoring** (stuck values, outliers)
6. **Use watchdog timers** to recover from sensor hangs
7. **Log sensor failures** for diagnostics
8. **Test at temperature extremes** if needed
9. **Validate measurements** against physical limits
10. **Document sensor orientation** and mounting
