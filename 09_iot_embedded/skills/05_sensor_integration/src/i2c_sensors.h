/*
 * I2C Sensor Interface Library
 * Common sensor drivers for popular I2C sensors
 *
 * Supported sensors:
 * - BME280: Temperature, humidity, pressure
 * - MPU6050: 6-DOF IMU (accelerometer + gyroscope)
 * - LSM9DS1: 9-DOF IMU (accel + gyro + mag)
 * - BH1750: Ambient light sensor
 * - VL53L0X: Time-of-Flight distance sensor
 */

#ifndef I2C_SENSORS_H
#define I2C_SENSORS_H

#include <stdint.h>
#include <stdbool.h>

/* ============================================================================
 * Common I2C Interface
 * ============================================================================ */

typedef enum {
    SENSOR_OK = 0,
    SENSOR_ERROR,
    SENSOR_TIMEOUT,
    SENSOR_NOT_FOUND
} sensor_status_t;

/* Platform-specific I2C functions (implement these for your platform) */
extern sensor_status_t i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t value);
extern sensor_status_t i2c_read_reg(uint8_t addr, uint8_t reg, uint8_t *value);
extern sensor_status_t i2c_read_burst(uint8_t addr, uint8_t reg, uint8_t *buffer, uint16_t len);

/* ============================================================================
 * BME280 - Temperature, Humidity, Pressure Sensor
 * ============================================================================ */

#define BME280_I2C_ADDR_PRIMARY    0x76
#define BME280_I2C_ADDR_SECONDARY  0x77
#define BME280_CHIP_ID             0x60

typedef struct {
    int32_t temperature;  /* °C * 100 */
    uint32_t pressure;    /* Pa */
    uint32_t humidity;    /* %RH * 1024 */
} bme280_data_t;

typedef struct {
    uint8_t i2c_addr;
    /* Calibration data */
    uint16_t dig_T1;
    int16_t dig_T2, dig_T3;
    uint16_t dig_P1;
    int16_t dig_P2, dig_P3, dig_P4, dig_P5, dig_P6, dig_P7, dig_P8, dig_P9;
    uint8_t dig_H1, dig_H3;
    int16_t dig_H2, dig_H4, dig_H5;
    int8_t dig_H6;
    int32_t t_fine;  /* Temperature compensation value */
} bme280_t;

sensor_status_t bme280_init(bme280_t *sensor, uint8_t i2c_addr);
sensor_status_t bme280_read(bme280_t *sensor, bme280_data_t *data);
sensor_status_t bme280_set_mode(bme280_t *sensor, uint8_t mode);

/* ============================================================================
 * MPU6050 - 6-Axis IMU (Accelerometer + Gyroscope)
 * ============================================================================ */

#define MPU6050_I2C_ADDR           0x68
#define MPU6050_I2C_ADDR_ALT       0x69
#define MPU6050_WHO_AM_I           0x68

typedef enum {
    MPU6050_ACCEL_RANGE_2G  = 0,
    MPU6050_ACCEL_RANGE_4G  = 1,
    MPU6050_ACCEL_RANGE_8G  = 2,
    MPU6050_ACCEL_RANGE_16G = 3
} mpu6050_accel_range_t;

typedef enum {
    MPU6050_GYRO_RANGE_250DPS  = 0,
    MPU6050_GYRO_RANGE_500DPS  = 1,
    MPU6050_GYRO_RANGE_1000DPS = 2,
    MPU6050_GYRO_RANGE_2000DPS = 3
} mpu6050_gyro_range_t;

typedef struct {
    int16_t accel_x, accel_y, accel_z;  /* Raw accelerometer */
    int16_t gyro_x, gyro_y, gyro_z;     /* Raw gyroscope */
    int16_t temperature;                 /* Raw temperature */
} mpu6050_raw_data_t;

typedef struct {
    float accel_x, accel_y, accel_z;  /* m/s^2 */
    float gyro_x, gyro_y, gyro_z;     /* deg/s */
    float temperature;                 /* °C */
} mpu6050_data_t;

typedef struct {
    uint8_t i2c_addr;
    mpu6050_accel_range_t accel_range;
    mpu6050_gyro_range_t gyro_range;
    float accel_scale;
    float gyro_scale;
} mpu6050_t;

sensor_status_t mpu6050_init(mpu6050_t *sensor, uint8_t i2c_addr);
sensor_status_t mpu6050_read_raw(mpu6050_t *sensor, mpu6050_raw_data_t *data);
sensor_status_t mpu6050_read(mpu6050_t *sensor, mpu6050_data_t *data);
sensor_status_t mpu6050_set_accel_range(mpu6050_t *sensor, mpu6050_accel_range_t range);
sensor_status_t mpu6050_set_gyro_range(mpu6050_t *sensor, mpu6050_gyro_range_t range);
sensor_status_t mpu6050_calibrate(mpu6050_t *sensor, uint16_t samples);

/* ============================================================================
 * BH1750 - Ambient Light Sensor
 * ============================================================================ */

#define BH1750_I2C_ADDR            0x23
#define BH1750_I2C_ADDR_ALT        0x5C

typedef enum {
    BH1750_MODE_CONTINUOUS_HIGH_RES   = 0x10,
    BH1750_MODE_CONTINUOUS_HIGH_RES2  = 0x11,
    BH1750_MODE_CONTINUOUS_LOW_RES    = 0x13,
    BH1750_MODE_ONE_TIME_HIGH_RES     = 0x20,
    BH1750_MODE_ONE_TIME_HIGH_RES2    = 0x21,
    BH1750_MODE_ONE_TIME_LOW_RES      = 0x23
} bh1750_mode_t;

typedef struct {
    uint8_t i2c_addr;
    bh1750_mode_t mode;
} bh1750_t;

sensor_status_t bh1750_init(bh1750_t *sensor, uint8_t i2c_addr, bh1750_mode_t mode);
sensor_status_t bh1750_read_lux(bh1750_t *sensor, float *lux);

/* ============================================================================
 * VL53L0X - Time-of-Flight Distance Sensor
 * ============================================================================ */

#define VL53L0X_I2C_ADDR           0x29

typedef enum {
    VL53L0X_MODE_SINGLE,
    VL53L0X_MODE_CONTINUOUS
} vl53l0x_mode_t;

typedef struct {
    uint8_t i2c_addr;
    vl53l0x_mode_t mode;
    uint32_t measurement_timing_budget_us;
} vl53l0x_t;

typedef struct {
    uint16_t distance_mm;
    uint16_t signal_rate;
    uint16_t ambient_rate;
    bool range_status;  /* true = valid measurement */
} vl53l0x_measurement_t;

sensor_status_t vl53l0x_init(vl53l0x_t *sensor, uint8_t i2c_addr);
sensor_status_t vl53l0x_start_ranging(vl53l0x_t *sensor, vl53l0x_mode_t mode);
sensor_status_t vl53l0x_read_distance(vl53l0x_t *sensor, vl53l0x_measurement_t *measurement);
sensor_status_t vl53l0x_stop_ranging(vl53l0x_t *sensor);

/* ============================================================================
 * LSM9DS1 - 9-DOF IMU (Accelerometer + Gyroscope + Magnetometer)
 * ============================================================================ */

#define LSM9DS1_ACCEL_GYRO_ADDR    0x6B
#define LSM9DS1_MAG_ADDR           0x1E

typedef struct {
    int16_t accel_x, accel_y, accel_z;
    int16_t gyro_x, gyro_y, gyro_z;
    int16_t mag_x, mag_y, mag_z;
    int16_t temperature;
} lsm9ds1_raw_data_t;

typedef struct {
    float accel_x, accel_y, accel_z;  /* g */
    float gyro_x, gyro_y, gyro_z;     /* deg/s */
    float mag_x, mag_y, mag_z;        /* gauss */
    float temperature;                 /* °C */
} lsm9ds1_data_t;

typedef struct {
    uint8_t accel_gyro_addr;
    uint8_t mag_addr;
    float accel_scale;
    float gyro_scale;
    float mag_scale;
} lsm9ds1_t;

sensor_status_t lsm9ds1_init(lsm9ds1_t *sensor);
sensor_status_t lsm9ds1_read_accel_gyro(lsm9ds1_t *sensor, lsm9ds1_data_t *data);
sensor_status_t lsm9ds1_read_mag(lsm9ds1_t *sensor, lsm9ds1_data_t *data);
sensor_status_t lsm9ds1_read_all(lsm9ds1_t *sensor, lsm9ds1_data_t *data);

/* ============================================================================
 * Sensor Calibration Utilities
 * ============================================================================ */

typedef struct {
    float offset_x, offset_y, offset_z;
    float scale_x, scale_y, scale_z;
} sensor_calibration_t;

void sensor_apply_calibration(float *x, float *y, float *z, const sensor_calibration_t *cal);
sensor_status_t sensor_auto_calibrate(float *samples_x, float *samples_y, float *samples_z,
                                       uint16_t num_samples, sensor_calibration_t *cal);

#endif /* I2C_SENSORS_H */
