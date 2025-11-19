# Sensor HAL API Design Guide

## Generic Sensor Interface

```c
typedef enum {
    SENSOR_OK = 0,
    SENSOR_ERROR,
    SENSOR_TIMEOUT,
    SENSOR_NOT_FOUND,
    SENSOR_CALIBRATION_ERROR
} sensor_status_t;

typedef struct {
    sensor_status_t (*init)(void);
    sensor_status_t (*read)(float *value);
    sensor_status_t (*calibrate)(void);
    sensor_status_t (*sleep)(void);
    sensor_status_t (*wake)(void);
} sensor_ops_t;

typedef struct {
    const char *name;
    uint8_t i2c_address;
    const sensor_ops_t *ops;
    void *private_data;
} sensor_t;
```

## Implementation Example: BME280

```c
static sensor_status_t bme280_init(void);
static sensor_status_t bme280_read_temperature(float *temp);
static sensor_status_t bme280_sleep(void);

static const sensor_ops_t bme280_ops = {
    .init = bme280_init,
    .read = bme280_read_temperature,
    .sleep = bme280_sleep,
    .wake = NULL,
    .calibrate = NULL
};

sensor_t bme280 = {
    .name = "BME280",
    .i2c_address = 0x76,
    .ops = &bme280_ops,
    .private_data = NULL
};
```

## Usage

```c
void application_code(void) {
    sensor_t *sensor = &bme280;
    float temperature;

    if (sensor->ops->init() == SENSOR_OK) {
        if (sensor->ops->read(&temperature) == SENSOR_OK) {
            printf("Temperature: %.2f°C\n", temperature);
        }
    }
}
```

## Benefits

1. **Abstraction**: Application code independent of sensor
2. **Testability**: Mock sensor for unit tests
3. **Flexibility**: Swap sensors without changing app code
4. **Maintainability**: Clear interface boundaries
