# Sensor Integration & Signal Processing - Subskill

**Expert in sensor interfacing, ADC/DAC, I2C/SPI communication, digital filtering, and sensor fusion**

---

## Expertise Overview

Specialist in sensor systems:
- Interface protocols (I2C, SPI, UART, 1-Wire, analog ADC)
- Digital signal processing (FIR/IIR filters, FFT, Kalman filtering)
- Sensor calibration and compensation
- Sensor fusion (IMU, multi-sensor data aggregation)
- Environmental, motion, optical, and industrial sensors

---

## Core Skills

### 1. I2C Sensor Communication

**BME280 Temperature/Humidity/Pressure Sensor**:
```c
#include "i2c_hal.h"

#define BME280_I2C_ADDR         0x76
#define BME280_REG_CHIP_ID      0xD0
#define BME280_REG_CTRL_MEAS    0xF4
#define BME280_REG_CONFIG       0xF5
#define BME280_REG_PRESS_MSB    0xF7

typedef struct {
    int32_t temperature;  /* °C * 100 */
    uint32_t pressure;    /* Pa */
    uint32_t humidity;    /* %RH * 1024 */
} bme280_data_t;

status_t bme280_init(void) {
    uint8_t chip_id;

    /* Read and verify chip ID */
    if (i2c_read_reg(BME280_I2C_ADDR, BME280_REG_CHIP_ID, &chip_id) != STATUS_OK) {
        return STATUS_ERROR;
    }

    if (chip_id != 0x60) {
        return STATUS_ERROR;  /* Wrong chip */
    }

    /* Configure sensor: normal mode, oversampling x16 */
    uint8_t ctrl_meas = (0x05 << 5) | (0x05 << 2) | 0x03;  /* osrs_t, osrs_p, mode */
    if (i2c_write_reg(BME280_I2C_ADDR, BME280_REG_CTRL_MEAS, ctrl_meas) != STATUS_OK) {
        return STATUS_ERROR;
    }

    /* Config: standby 1000ms, filter coefficient 16 */
    uint8_t config = (0x05 << 5) | (0x04 << 2);
    if (i2c_write_reg(BME280_I2C_ADDR, BME280_REG_CONFIG, config) != STATUS_OK) {
        return STATUS_ERROR;
    }

    return STATUS_OK;
}

status_t bme280_read(bme280_data_t *data) {
    uint8_t raw_data[8];

    /* Read burst: pressure + temperature */
    if (i2c_read_burst(BME280_I2C_ADDR, BME280_REG_PRESS_MSB, raw_data, 8) != STATUS_OK) {
        return STATUS_ERROR;
    }

    /* Parse raw values */
    int32_t adc_P = (raw_data[0] << 12) | (raw_data[1] << 4) | (raw_data[2] >> 4);
    int32_t adc_T = (raw_data[3] << 12) | (raw_data[4] << 4) | (raw_data[5] >> 4);
    int32_t adc_H = (raw_data[6] << 8) | raw_data[7];

    /* Compensate using calibration data (simplified) */
    data->temperature = compensate_temperature(adc_T);
    data->pressure = compensate_pressure(adc_P);
    data->humidity = compensate_humidity(adc_H);

    return STATUS_OK;
}
```

### 2. SPI Sensor Communication

**MPU6050 IMU (Accelerometer + Gyroscope)**:
```c
#include "spi_hal.h"

#define MPU6050_SPI_CS_PIN      GPIO_PIN_4
#define MPU6050_REG_WHO_AM_I    0x75
#define MPU6050_REG_ACCEL_XOUT  0x3B

typedef struct {
    int16_t accel_x, accel_y, accel_z;  /* m/s^2 * 16384 */
    int16_t gyro_x, gyro_y, gyro_z;     /* °/s * 131 */
    int16_t temperature;                 /* °C * 340 + offset */
} mpu6050_data_t;

uint8_t mpu6050_read_reg(uint8_t reg) {
    uint8_t tx_data[2] = {reg | 0x80, 0x00};  /* Read bit set */
    uint8_t rx_data[2];

    gpio_write(MPU6050_SPI_CS_PIN, 0);  /* CS low */
    spi_transfer(tx_data, rx_data, 2);
    gpio_write(MPU6050_SPI_CS_PIN, 1);  /* CS high */

    return rx_data[1];
}

void mpu6050_write_reg(uint8_t reg, uint8_t value) {
    uint8_t tx_data[2] = {reg & 0x7F, value};  /* Write bit clear */

    gpio_write(MPU6050_SPI_CS_PIN, 0);
    spi_transfer(tx_data, NULL, 2);
    gpio_write(MPU6050_SPI_CS_PIN, 1);
}

status_t mpu6050_read(mpu6050_data_t *data) {
    uint8_t raw_data[14];
    uint8_t tx_data[15];

    tx_data[0] = MPU6050_REG_ACCEL_XOUT | 0x80;  /* Burst read */
    memset(&tx_data[1], 0, 14);

    gpio_write(MPU6050_SPI_CS_PIN, 0);
    spi_transfer(tx_data, raw_data, 15);
    gpio_write(MPU6050_SPI_CS_PIN, 1);

    /* Parse (big-endian) */
    data->accel_x = (int16_t)((raw_data[1] << 8) | raw_data[2]);
    data->accel_y = (int16_t)((raw_data[3] << 8) | raw_data[4]);
    data->accel_z = (int16_t)((raw_data[5] << 8) | raw_data[6]);
    data->temperature = (int16_t)((raw_data[7] << 8) | raw_data[8]);
    data->gyro_x = (int16_t)((raw_data[9] << 8) | raw_data[10]);
    data->gyro_y = (int16_t)((raw_data[11] << 8) | raw_data[12]);
    data->gyro_z = (int16_t)((raw_data[13] << 8) | raw_data[14]);

    return STATUS_OK;
}
```

### 3. ADC and Analog Sensors

**Temperature Sensor (NTC Thermistor)**:
```c
#include <math.h>

#define ADC_RESOLUTION  4096    /* 12-bit ADC */
#define VDD             3.3f    /* Supply voltage */
#define R_SERIES        10000   /* Series resistor (10kΩ) */

/* Steinhart-Hart coefficients for NTC thermistor */
#define A   0.001129148f
#define B   0.000234125f
#define C   0.0000000876741f

float read_temperature_ntc(uint16_t adc_value) {
    /* Calculate NTC resistance */
    float voltage = (float)adc_value * VDD / (float)ADC_RESOLUTION;
    float r_ntc = R_SERIES * voltage / (VDD - voltage);

    /* Steinhart-Hart equation */
    float ln_r = logf(r_ntc);
    float temp_kelvin = 1.0f / (A + B * ln_r + C * ln_r * ln_r * ln_r);
    float temp_celsius = temp_kelvin - 273.15f;

    return temp_celsius;
}

/* Multi-point ADC averaging */
float read_temperature_averaged(uint8_t samples) {
    uint32_t sum = 0;

    for (uint8_t i = 0; i < samples; i++) {
        sum += adc_read_channel(ADC_CHANNEL_TEMP);
        delay_ms(10);
    }

    uint16_t avg_adc = sum / samples;
    return read_temperature_ntc(avg_adc);
}
```

### 4. Digital Signal Processing

**Low-Pass FIR Filter**:
```c
#define FILTER_ORDER    8

/* FIR filter coefficients (low-pass, fc=10Hz @ fs=100Hz) */
static const float fir_coeffs[FILTER_ORDER] = {
    0.036, 0.072, 0.129, 0.167, 0.167, 0.129, 0.072, 0.036
};

static float fir_buffer[FILTER_ORDER] = {0};
static size_t fir_index = 0;

float fir_filter_process(float input) {
    /* Add new sample to circular buffer */
    fir_buffer[fir_index] = input;
    fir_index = (fir_index + 1) % FILTER_ORDER;

    /* Convolution */
    float output = 0.0f;
    for (size_t i = 0; i < FILTER_ORDER; i++) {
        size_t buf_idx = (fir_index + i) % FILTER_ORDER;
        output += fir_coeffs[i] * fir_buffer[buf_idx];
    }

    return output;
}
```

**Kalman Filter (1D)**:
```c
typedef struct {
    float x;      /* Estimated state */
    float P;      /* Estimation error covariance */
    float Q;      /* Process noise covariance */
    float R;      /* Measurement noise covariance */
} kalman_filter_t;

void kalman_init(kalman_filter_t *kf, float initial_value,
                 float process_noise, float measurement_noise) {
    kf->x = initial_value;
    kf->P = 1.0f;
    kf->Q = process_noise;
    kf->R = measurement_noise;
}

float kalman_update(kalman_filter_t *kf, float measurement) {
    /* Prediction */
    kf->P = kf->P + kf->Q;

    /* Update */
    float K = kf->P / (kf->P + kf->R);  /* Kalman gain */
    kf->x = kf->x + K * (measurement - kf->x);
    kf->P = (1.0f - K) * kf->P;

    return kf->x;
}

/* Usage */
static kalman_filter_t temp_filter;

void sensor_task(void) {
    kalman_init(&temp_filter, 25.0f, 0.1f, 1.0f);

    for (;;) {
        float raw_temp = read_temperature_raw();
        float filtered_temp = kalman_update(&temp_filter, raw_temp);

        process_temperature(filtered_temp);
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

### 5. Sensor Fusion (Complementary Filter)

**IMU Attitude Estimation**:
```c
typedef struct {
    float roll;   /* degrees */
    float pitch;  /* degrees */
    float alpha;  /* Filter coefficient (0-1) */
} attitude_t;

void update_attitude(attitude_t *att, mpu6050_data_t *imu, float dt) {
    /* Accelerometer angles */
    float accel_roll = atan2f(imu->accel_y, imu->accel_z) * 57.2958f;
    float accel_pitch = atan2f(-imu->accel_x,
        sqrtf(imu->accel_y * imu->accel_y + imu->accel_z * imu->accel_z)) * 57.2958f;

    /* Gyroscope integration */
    float gyro_roll = att->roll + (imu->gyro_x / 131.0f) * dt;
    float gyro_pitch = att->pitch + (imu->gyro_y / 131.0f) * dt;

    /* Complementary filter */
    att->roll = att->alpha * gyro_roll + (1.0f - att->alpha) * accel_roll;
    att->pitch = att->alpha * gyro_pitch + (1.0f - att->alpha) * accel_pitch;
}
```

---

## Calibration Techniques

**Offset Calibration**:
```c
typedef struct {
    int16_t offset_x;
    int16_t offset_y;
    int16_t offset_z;
} sensor_calibration_t;

void calibrate_accelerometer(sensor_calibration_t *cal) {
    int32_t sum_x = 0, sum_y = 0, sum_z = 0;
    const uint16_t samples = 100;

    for (uint16_t i = 0; i < samples; i++) {
        mpu6050_data_t data;
        mpu6050_read(&data);

        sum_x += data.accel_x;
        sum_y += data.accel_y;
        sum_z += data.accel_z;

        delay_ms(10);
    }

    cal->offset_x = sum_x / samples;
    cal->offset_y = sum_y / samples;
    cal->offset_z = (sum_z / samples) - 16384;  /* Subtract 1g */
}
```

---

## Best Practices

1. **Filtering**: Apply appropriate filters to reduce noise
2. **Calibration**: Implement offset and gain calibration
3. **Error Handling**: Check I2C/SPI communication status
4. **Power Management**: Use sensor sleep modes
5. **Sample Rate**: Match to application requirements

---

## References

- Sensor datasheets (Bosch, STMicroelectronics, TI)
- "Digital Signal Processing" by Proakis & Manolakis
- ARM CMSIS-DSP library
- Kalman filtering theory

---

**Implement robust, calibrated, and noise-filtered sensor systems with professional-grade signal processing.**
