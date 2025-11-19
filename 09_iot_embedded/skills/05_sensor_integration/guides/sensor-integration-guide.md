# Sensor Integration Getting Started Guide

## Overview

This guide walks you through integrating sensors into your embedded system, from hardware connection to software implementation and calibration.

## Step 1: Hardware Setup

### I2C Bus Configuration

**Pull-up Resistors:**
- Required on SDA and SCL lines
- Typical values: 2.2kΩ - 4.7kΩ
- Formula: R_min = (V_DD - 0.4V) / 3mA

**Multiple Sensors on Same Bus:**
```
MCU                 Sensor 1 (0x76)
 |                       |
SDA ----[4.7kΩ]----+-----+
                   |
                   +-----+
                   |     |
SCL ----[4.7kΩ]----+  Sensor 2 (0x68)
                   |     |
GND ----------------+-----+
```

**Address Conflicts:**
- Check each sensor's I2C address
- Many sensors have an address select pin (AD0, SA0)
- Use I2C multiplexer (TCA9548A) if conflicts occur

### Power Supply

**Decoupling Capacitors:**
```
       VDD
        |
    [100nF]  <- Close to sensor
        |
      Sensor
        |
       GND
```

**Power Sequencing:**
1. Apply VDD
2. Wait for stabilization (typically 10-100ms)
3. Release reset pin (if present)
4. Initialize sensor via I2C/SPI

## Step 2: Software Initialization

### Basic I2C Sensor Init Pattern

```c
#include "i2c_hal.h"

typedef enum {
    SENSOR_OK,
    SENSOR_ERROR,
    SENSOR_NOT_FOUND
} sensor_status_t;

sensor_status_t sensor_init(uint8_t i2c_addr) {
    uint8_t chip_id;

    /* Read chip ID register */
    if (i2c_read_reg(i2c_addr, REG_CHIP_ID, &chip_id) != I2C_OK) {
        return SENSOR_ERROR;
    }

    /* Verify chip ID */
    if (chip_id != EXPECTED_CHIP_ID) {
        return SENSOR_NOT_FOUND;
    }

    /* Configure sensor */
    i2c_write_reg(i2c_addr, REG_CONFIG, CONFIG_VALUE);
    i2c_write_reg(i2c_addr, REG_CTRL, CTRL_VALUE);

    /* Wait for sensor to be ready */
    delay_ms(10);

    return SENSOR_OK;
}
```

### Error Handling

```c
sensor_status_t sensor_read_with_retry(uint8_t addr, float *value) {
    const int MAX_RETRIES = 3;
    int retries = 0;

    while (retries < MAX_RETRIES) {
        sensor_status_t status = sensor_read(addr, value);

        if (status == SENSOR_OK) {
            return SENSOR_OK;
        }

        /* Delay before retry */
        delay_ms(10);
        retries++;
    }

    /* All retries failed */
    log_error("Sensor read failed after %d retries", MAX_RETRIES);
    return SENSOR_ERROR;
}
```

## Step 3: Data Acquisition

### Polling vs Interrupt-Driven

**Polling (Simple):**
```c
void sensor_task_polling(void) {
    for (;;) {
        float value = sensor_read();
        process_data(value);
        delay_ms(100);  /* 10 Hz sampling */
    }
}
```

**Interrupt-Driven (Efficient):**
```c
static volatile bool data_ready = false;

/* GPIO interrupt handler */
void sensor_data_ready_irq(void) {
    data_ready = true;
}

void sensor_task_interrupt(void) {
    /* Configure sensor interrupt pin */
    configure_gpio_interrupt(SENSOR_INT_PIN, sensor_data_ready_irq);

    /* Enable sensor data ready interrupt */
    sensor_enable_interrupt();

    for (;;) {
        /* Wait for interrupt */
        while (!data_ready) {
            __WFI();  /* Sleep until interrupt */
        }

        data_ready = false;

        /* Read sensor */
        float value = sensor_read();
        process_data(value);
    }
}
```

### DMA-Based Acquisition (Advanced)

```c
#define NUM_SAMPLES  1000
static uint16_t adc_buffer[NUM_SAMPLES];

void setup_adc_dma(void) {
    /* Configure ADC */
    adc_init();
    adc_set_sample_rate(10000);  /* 10 kHz */

    /* Configure DMA: ADC -> Memory */
    dma_config_t dma_cfg = {
        .source = (uint32_t)&ADC_DATA_REG,
        .destination = (uint32_t)adc_buffer,
        .count = NUM_SAMPLES,
        .mode = DMA_CIRCULAR
    };

    dma_init(&dma_cfg);

    /* Start acquisition */
    dma_start();
    adc_start();
}

void dma_transfer_complete_callback(void) {
    /* Process buffer */
    fft_process(adc_buffer, NUM_SAMPLES);
}
```

## Step 4: Filtering & Signal Processing

### Choosing the Right Filter

| Filter Type | Use Case | Pros | Cons |
|-------------|----------|------|------|
| Moving Average | Slow-changing signals | Simple, stable | Lag, memory usage |
| EMA | Real-time updates | Low memory | Tuning required |
| Median | Spike rejection | Removes outliers | CPU intensive |
| Kalman | Noisy measurements | Optimal (math) | Complex setup |
| Low-Pass | High-freq noise | Smooth output | Phase delay |

### Implementation Example

```c
#include <math.h>

/* Combined filtering pipeline */
typedef struct {
    /* Stage 1: Median filter (reject spikes) */
    float median_buffer[5];
    int median_index;

    /* Stage 2: Kalman filter (optimal estimate) */
    float kalman_x;
    float kalman_P;

    /* Stage 3: Validation */
    float last_valid_value;
    uint32_t invalid_count;
} sensor_filter_pipeline_t;

void filter_pipeline_init(sensor_filter_pipeline_t *filter) {
    memset(filter->median_buffer, 0, sizeof(filter->median_buffer));
    filter->median_index = 0;
    filter->kalman_x = 0;
    filter->kalman_P = 1.0f;
    filter->last_valid_value = 0;
    filter->invalid_count = 0;
}

float filter_pipeline_process(sensor_filter_pipeline_t *filter, float raw_value) {
    /* Stage 1: Median filter */
    filter->median_buffer[filter->median_index] = raw_value;
    filter->median_index = (filter->median_index + 1) % 5;

    float sorted[5];
    memcpy(sorted, filter->median_buffer, sizeof(sorted));

    /* Simple bubble sort */
    for (int i = 0; i < 4; i++) {
        for (int j = i + 1; j < 5; j++) {
            if (sorted[j] < sorted[i]) {
                float temp = sorted[i];
                sorted[i] = sorted[j];
                sorted[j] = temp;
            }
        }
    }

    float median = sorted[2];

    /* Stage 2: Kalman filter */
    const float Q = 0.01f;  /* Process noise */
    const float R = 1.0f;   /* Measurement noise */

    filter->kalman_P += Q;
    float K = filter->kalman_P / (filter->kalman_P + R);
    filter->kalman_x += K * (median - filter->kalman_x);
    filter->kalman_P *= (1.0f - K);

    float filtered = filter->kalman_x;

    /* Stage 3: Validation (rate-of-change check) */
    float max_change = 10.0f;  /* Maximum expected change per sample */
    if (fabsf(filtered - filter->last_valid_value) > max_change) {
        filter->invalid_count++;
        if (filter->invalid_count < 5) {
            /* Use last valid value */
            return filter->last_valid_value;
        }
        /* Too many invalid samples - accept anyway */
    } else {
        filter->invalid_count = 0;
    }

    filter->last_valid_value = filtered;
    return filtered;
}
```

## Step 5: Calibration

### When to Calibrate

- **At manufacturing:** Factory calibration
- **At startup:** Zero-point offset
- **Periodically:** Drift compensation
- **On user request:** Manual recalibration

### Multi-Point Calibration Procedure

```c
#define CALIBRATION_POINTS  5

typedef struct {
    float reference[CALIBRATION_POINTS];
    float measured[CALIBRATION_POINTS];
    float slope;
    float intercept;
} calibration_data_t;

sensor_status_t perform_calibration(calibration_data_t *cal) {
    printf("Starting calibration...\n");

    for (int i = 0; i < CALIBRATION_POINTS; i++) {
        printf("Place sensor at reference value: %.2f\n", cal->reference[i]);
        printf("Press any key when ready...\n");
        wait_for_key();

        /* Take multiple samples and average */
        float sum = 0;
        for (int j = 0; j < 100; j++) {
            sum += sensor_read_raw();
            delay_ms(10);
        }
        cal->measured[i] = sum / 100;

        printf("Measured: %.2f\n", cal->measured[i]);
    }

    /* Linear regression: y = mx + b */
    float sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;
    int n = CALIBRATION_POINTS;

    for (int i = 0; i < n; i++) {
        float x = cal->measured[i];
        float y = cal->reference[i];
        sum_x += x;
        sum_y += y;
        sum_xy += x * y;
        sum_x2 += x * x;
    }

    cal->slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);
    cal->intercept = (sum_y - cal->slope * sum_x) / n;

    printf("Calibration complete: y = %.4f * x + %.4f\n",
           cal->slope, cal->intercept);

    /* Save to non-volatile memory */
    save_calibration_to_flash(cal);

    return SENSOR_OK;
}

float apply_calibration(float raw, calibration_data_t *cal) {
    return raw * cal->slope + cal->intercept;
}
```

## Step 6: Sensor Fusion

### IMU Sensor Fusion Example

```c
#include "madgwick.h"

/* Global state */
static madgwick_filter_t imu_filter;
static euler_angles_t orientation;

void imu_fusion_init(void) {
    /* Initialize sensors */
    mpu6050_init();
    lsm303_init();  /* Magnetometer */

    /* Initialize filter */
    madgwick_init(&imu_filter, 100.0f, 0.1f);  /* 100 Hz, beta=0.1 */
}

void imu_fusion_update(void) {
    /* Read IMU data */
    mpu6050_data_t imu;
    mpu6050_read(&imu);

    lsm303_mag_data_t mag;
    lsm303_read_mag(&mag);

    /* Convert to appropriate units */
    vector3_t gyro = {
        .x = imu.gyro_x * DEG_TO_RAD,
        .y = imu.gyro_y * DEG_TO_RAD,
        .z = imu.gyro_z * DEG_TO_RAD
    };

    vector3_t accel = {
        .x = imu.accel_x / 9.81f,  /* Convert m/s^2 to g */
        .y = imu.accel_y / 9.81f,
        .z = imu.accel_z / 9.81f
    };

    vector3_t mag_vec = {
        .x = mag.x,
        .y = mag.y,
        .z = mag.z
    };

    /* Update fusion filter */
    madgwick_update(&imu_filter, gyro, accel, mag_vec);

    /* Get Euler angles */
    quaternion_to_euler(&imu_filter, &orientation);

    /* Use orientation */
    printf("Roll: %.1f°, Pitch: %.1f°, Yaw: %.1f°\n",
           orientation.roll, orientation.pitch, orientation.yaw);
}
```

## Step 7: Production Considerations

### Sensor Health Monitoring

```c
typedef struct {
    uint32_t read_count;
    uint32_t error_count;
    uint32_t last_read_time;
    bool is_alive;
} sensor_health_t;

void sensor_health_check(sensor_health_t *health) {
    uint32_t now = get_time_ms();

    /* Check if sensor is stuck */
    if ((now - health->last_read_time) > 5000) {
        health->is_alive = false;
        log_error("Sensor timeout - no data for 5 seconds");

        /* Attempt recovery */
        sensor_reset();
        sensor_init();
    }

    /* Check error rate */
    float error_rate = (float)health->error_count / health->read_count;
    if (error_rate > 0.1f) {  /* > 10% error rate */
        log_warning("High sensor error rate: %.1f%%", error_rate * 100);
    }
}
```

### Data Logging

```c
void sensor_data_logger(void) {
    FILE *log_file = fopen("sensor_log.csv", "a");

    fprintf(log_file, "timestamp,sensor_id,value,quality\n");

    for (;;) {
        uint32_t timestamp = get_time_ms();
        float value = sensor_read();
        int quality = sensor_get_quality();

        fprintf(log_file, "%u,%d,%.3f,%d\n",
                timestamp, SENSOR_ID, value, quality);

        fflush(log_file);  /* Ensure data is written */
        delay_ms(1000);
    }
}
```

## Troubleshooting Guide

### Issue: Sensor Not Detected

**Symptoms:** I2C read returns error, chip ID doesn't match

**Checklist:**
1. Verify VDD voltage (use multimeter)
2. Check I2C pull-up resistors (should be 2.2-4.7kΩ)
3. Verify I2C address (use I2C scanner)
4. Check SDA/SCL connections (swap if needed)
5. Ensure sensor is powered before I2C access
6. Try reducing I2C clock speed

### Issue: Noisy or Erratic Readings

**Solutions:**
1. Add 100nF capacitor close to sensor VDD pin
2. Use twisted pair or shielded cable for long connections
3. Implement digital filtering (moving average, Kalman)
4. Check for ground loops
5. Separate analog and digital grounds
6. Use ferrite beads on sensor power supply

### Issue: Values Drift Over Time

**Solutions:**
1. Implement temperature compensation
2. Recalibrate periodically
3. Use humidity compensation (for some sensors)
4. Check for mechanical stress on sensor
5. Ensure stable power supply

### Issue: I2C Bus Lockup

**Recovery Procedure:**
```c
void i2c_bus_recovery(void) {
    /* Disable I2C peripheral */
    i2c_deinit();

    /* Configure pins as GPIO */
    gpio_init(SDA_PIN, GPIO_OUTPUT);
    gpio_init(SCL_PIN, GPIO_OUTPUT);

    /* Send 9 clock pulses */
    for (int i = 0; i < 9; i++) {
        gpio_write(SCL_PIN, 0);
        delay_us(5);
        gpio_write(SCL_PIN, 1);
        delay_us(5);
    }

    /* Send STOP condition */
    gpio_write(SDA_PIN, 0);
    delay_us(5);
    gpio_write(SCL_PIN, 1);
    delay_us(5);
    gpio_write(SDA_PIN, 1);
    delay_us(5);

    /* Re-initialize I2C */
    i2c_init();
}
```

## Next Steps

1. **Performance Optimization:** Profile sensor read times, optimize sampling rates
2. **Power Optimization:** Implement sensor sleep modes, duty cycling
3. **Advanced Fusion:** Implement EKF or UKF for multi-sensor fusion
4. **Machine Learning:** Add anomaly detection, predictive maintenance
5. **Cloud Integration:** Send sensor data to cloud for analytics

## Additional Resources

- Sensor datasheets from manufacturers
- Application notes for specific sensors
- Reference designs from evaluation boards
- Community forums (ST Community, TI E2E, etc.)
