# RTOS API Integration Guide

**Comprehensive guide for integrating and using RTOS APIs across FreeRTOS, Zephyr, and ThreadX**

---

## Overview

This guide provides standardized patterns for working with Real-Time Operating System APIs, focusing on task management, inter-task communication, synchronization, and timing services.

---

## FreeRTOS API Integration

### Task Creation & Management

```c
#include "FreeRTOS.h"
#include "task.h"

/* Task handle (opaque pointer to task control block) */
static TaskHandle_t sensor_task_handle = NULL;

/* Task function prototype */
void sensor_task(void *parameters);

/* Create task */
BaseType_t create_sensor_task(void) {
    BaseType_t result;

    result = xTaskCreate(
        sensor_task,              // Task function
        "SensorTask",             // Task name (for debugging)
        256,                      // Stack depth (words, not bytes)
        NULL,                     // Parameters passed to task
        tskIDLE_PRIORITY + 2,     // Priority
        &sensor_task_handle       // Task handle (optional)
    );

    if (pdPASS != result) {
        /* Task creation failed */
        return pdFAIL;
    }

    return pdPASS;
}

/* Task implementation */
void sensor_task(void *parameters) {
    (void)parameters;  // Unused

    /* Task initialization */
    sensor_init();

    /* Infinite task loop */
    for (;;) {
        /* Task work */
        int16_t temperature = sensor_read();
        process_temperature(temperature);

        /* Delay for 1000ms (1 second) */
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    /* Tasks must not return - delete if needed */
    vTaskDelete(NULL);
}
```

### Queue Communication

```c
#include "queue.h"

#define QUEUE_LENGTH    (10)
#define QUEUE_ITEM_SIZE sizeof(sensor_data_t)

typedef struct {
    uint16_t sensor_id;
    int16_t temperature;
    uint32_t timestamp;
} sensor_data_t;

static QueueHandle_t sensor_queue = NULL;

/* Create queue */
void create_sensor_queue(void) {
    sensor_queue = xQueueCreate(QUEUE_LENGTH, QUEUE_ITEM_SIZE);

    if (NULL == sensor_queue) {
        /* Queue creation failed */
        error_handler();
    }
}

/* Producer task: Send to queue */
void sensor_task(void *parameters) {
    sensor_data_t data;

    for (;;) {
        /* Read sensor */
        data.sensor_id = 1;
        data.temperature = sensor_read();
        data.timestamp = xTaskGetTickCount();

        /* Send to queue (block for 100ms if full) */
        if (pdPASS != xQueueSend(sensor_queue, &data, pdMS_TO_TICKS(100))) {
            /* Queue full - data lost */
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

/* Consumer task: Receive from queue */
void processing_task(void *parameters) {
    sensor_data_t received_data;

    for (;;) {
        /* Wait indefinitely for queue data */
        if (pdPASS == xQueueReceive(sensor_queue, &received_data, portMAX_DELAY)) {
            /* Process received data */
            process_sensor_data(&received_data);
        }
    }
}
```

### Semaphores

```c
#include "semphr.h"

/* Binary semaphore for synchronization */
static SemaphoreHandle_t data_ready_sem = NULL;

/* Mutex for resource protection */
static SemaphoreHandle_t i2c_mutex = NULL;

/* Create semaphores */
void create_synchronization_objects(void) {
    /* Binary semaphore (signals events) */
    data_ready_sem = xSemaphoreCreateBinary();

    /* Mutex (protects shared resources) */
    i2c_mutex = xSemaphoreCreateMutex();

    if ((NULL == data_ready_sem) || (NULL == i2c_mutex)) {
        error_handler();
    }
}

/* ISR gives semaphore */
void UART_RX_IRQHandler(void) {
    BaseType_t higher_priority_task_woken = pdFALSE;

    /* Signal that data is ready */
    xSemaphoreGiveFromISR(data_ready_sem, &higher_priority_task_woken);

    /* Request context switch if needed */
    portYIELD_FROM_ISR(higher_priority_task_woken);
}

/* Task waits for semaphore */
void uart_processing_task(void *parameters) {
    for (;;) {
        /* Wait for data ready signal */
        if (pdPASS == xSemaphoreTake(data_ready_sem, pdMS_TO_TICKS(5000))) {
            /* Data available, process it */
            process_uart_data();
        } else {
            /* Timeout - no data received */
        }
    }
}

/* Mutex for I2C bus access */
status_t i2c_write_protected(uint8_t addr, const uint8_t *data, size_t len) {
    status_t result = STATUS_ERROR;

    /* Take mutex (wait up to 100ms) */
    if (pdPASS == xSemaphoreTake(i2c_mutex, pdMS_TO_TICKS(100))) {
        /* Critical section: exclusive I2C access */
        result = i2c_write(addr, data, len);

        /* Release mutex */
        xSemaphoreGive(i2c_mutex);
    } else {
        /* Mutex timeout */
        result = STATUS_TIMEOUT;
    }

    return result;
}
```

### Software Timers

```c
#include "timers.h"

static TimerHandle_t led_blink_timer = NULL;

/* Timer callback (runs in timer service task context) */
void led_blink_callback(TimerHandle_t timer) {
    (void)timer;
    gpio_toggle_led();
}

/* Create and start timer */
void create_led_timer(void) {
    /* Create timer: 500ms period, auto-reload */
    led_blink_timer = xTimerCreate(
        "LEDTimer",               // Timer name
        pdMS_TO_TICKS(500),       // Period (500ms)
        pdTRUE,                   // Auto-reload
        NULL,                     // Timer ID
        led_blink_callback        // Callback function
    );

    if (NULL == led_blink_timer) {
        error_handler();
    }

    /* Start timer */
    if (pdPASS != xTimerStart(led_blink_timer, 0)) {
        error_handler();
    }
}
```

---

## Zephyr RTOS API Integration

### Thread Creation

```c
#include <zephyr/kernel.h>

#define SENSOR_THREAD_STACK_SIZE 1024
#define SENSOR_THREAD_PRIORITY   5

/* Define thread stack */
K_THREAD_STACK_DEFINE(sensor_thread_stack, SENSOR_THREAD_STACK_SIZE);

/* Thread control block */
static struct k_thread sensor_thread_data;
static k_tid_t sensor_thread_id;

/* Thread function */
void sensor_thread_entry(void *p1, void *p2, void *p3) {
    ARG_UNUSED(p1);
    ARG_UNUSED(p2);
    ARG_UNUSED(p3);

    /* Thread initialization */
    sensor_init();

    while (1) {
        /* Thread work */
        int16_t temp = sensor_read();
        process_temperature(temp);

        /* Sleep for 1 second */
        k_sleep(K_MSEC(1000));
    }
}

/* Create and start thread */
void create_sensor_thread(void) {
    sensor_thread_id = k_thread_create(
        &sensor_thread_data,          // Thread control block
        sensor_thread_stack,          // Stack area
        SENSOR_THREAD_STACK_SIZE,     // Stack size
        sensor_thread_entry,          // Entry function
        NULL, NULL, NULL,             // Parameters
        SENSOR_THREAD_PRIORITY,       // Priority
        0,                            // Options
        K_NO_WAIT                     // Start delay
    );

    k_thread_name_set(sensor_thread_id, "sensor");
}
```

### Message Queues

```c
#include <zephyr/kernel.h>

typedef struct {
    uint16_t sensor_id;
    int16_t temperature;
} sensor_msg_t;

/* Define message queue */
K_MSGQ_DEFINE(sensor_msgq, sizeof(sensor_msg_t), 10, 4);

/* Producer: Send to message queue */
void sensor_thread(void *p1, void *p2, void *p3) {
    sensor_msg_t msg;

    while (1) {
        msg.sensor_id = 1;
        msg.temperature = sensor_read();

        /* Send message (block if full) */
        if (k_msgq_put(&sensor_msgq, &msg, K_FOREVER) != 0) {
            /* Should not happen with K_FOREVER */
        }

        k_sleep(K_MSEC(1000));
    }
}

/* Consumer: Receive from message queue */
void processing_thread(void *p1, void *p2, void *p3) {
    sensor_msg_t msg;

    while (1) {
        /* Receive message (block until available) */
        if (k_msgq_get(&sensor_msgq, &msg, K_FOREVER) == 0) {
            /* Process message */
            process_sensor_data(&msg);
        }
    }
}
```

### Mutexes and Semaphores

```c
/* Define mutex */
K_MUTEX_DEFINE(i2c_mutex);

/* Define semaphore (initial count 0) */
K_SEM_DEFINE(data_ready_sem, 0, 1);

/* Take mutex for I2C access */
int i2c_write_protected(uint8_t addr, const uint8_t *data, size_t len) {
    int ret;

    /* Lock mutex (wait up to 100ms) */
    if (k_mutex_lock(&i2c_mutex, K_MSEC(100)) == 0) {
        /* Critical section */
        ret = i2c_write(addr, data, len);

        /* Unlock mutex */
        k_mutex_unlock(&i2c_mutex);
    } else {
        ret = -ETIMEDOUT;
    }

    return ret;
}

/* Give semaphore from ISR */
void uart_isr(const struct device *dev, void *user_data) {
    /* Signal data ready */
    k_sem_give(&data_ready_sem);
}

/* Wait for semaphore in thread */
void uart_thread(void *p1, void *p2, void *p3) {
    while (1) {
        /* Wait for semaphore (timeout 5s) */
        if (k_sem_take(&data_ready_sem, K_MSEC(5000)) == 0) {
            process_uart_data();
        }
    }
}
```

---

## ThreadX (Azure RTOS) API Integration

### Thread Creation

```c
#include "tx_api.h"

#define SENSOR_THREAD_STACK_SIZE 1024
#define SENSOR_THREAD_PRIORITY   5

static TX_THREAD sensor_thread;
static UCHAR sensor_thread_stack[SENSOR_THREAD_STACK_SIZE];

/* Thread entry function */
void sensor_thread_entry(ULONG thread_input) {
    (void)thread_input;

    sensor_init();

    while (1) {
        int16_t temp = sensor_read();
        process_temperature(temp);

        /* Sleep for 100 ticks */
        tx_thread_sleep(100);
    }
}

/* Create thread */
UINT create_sensor_thread(void) {
    UINT status;

    status = tx_thread_create(
        &sensor_thread,               // Thread control block
        "Sensor Thread",              // Thread name
        sensor_thread_entry,          // Entry function
        0,                            // Entry input
        sensor_thread_stack,          // Stack start
        SENSOR_THREAD_STACK_SIZE,     // Stack size
        SENSOR_THREAD_PRIORITY,       // Priority
        SENSOR_THREAD_PRIORITY,       // Preemption threshold
        TX_NO_TIME_SLICE,             // Time slice
        TX_AUTO_START                 // Auto-start
    );

    return status;
}
```

### Queues

```c
#include "tx_api.h"

typedef struct {
    UINT sensor_id;
    INT temperature;
} sensor_message_t;

#define QUEUE_SIZE 10
#define MESSAGE_SIZE (sizeof(sensor_message_t) / sizeof(ULONG))

static TX_QUEUE sensor_queue;
static ULONG sensor_queue_storage[QUEUE_SIZE * MESSAGE_SIZE];

/* Create queue */
UINT create_sensor_queue(void) {
    return tx_queue_create(
        &sensor_queue,
        "Sensor Queue",
        MESSAGE_SIZE,
        sensor_queue_storage,
        sizeof(sensor_queue_storage)
    );
}

/* Send to queue */
void sensor_thread_entry(ULONG input) {
    sensor_message_t msg;

    while (1) {
        msg.sensor_id = 1;
        msg.temperature = sensor_read();

        /* Send message (wait TX_WAIT_FOREVER if full) */
        tx_queue_send(&sensor_queue, &msg, TX_WAIT_FOREVER);

        tx_thread_sleep(100);
    }
}

/* Receive from queue */
void processing_thread_entry(ULONG input) {
    sensor_message_t msg;

    while (1) {
        /* Receive message */
        if (TX_SUCCESS == tx_queue_receive(&sensor_queue, &msg, TX_WAIT_FOREVER)) {
            process_sensor_data(&msg);
        }
    }
}
```

---

## Common RTOS Patterns

### Producer-Consumer with Queue

**Problem**: Multiple tasks generating data, single task processing

**Solution**: Use message queue for decoupling

```c
/* FreeRTOS example */
QueueHandle_t data_queue;

void producer_task(void *param) {
    data_t item;
    for (;;) {
        generate_data(&item);
        xQueueSend(data_queue, &item, portMAX_DELAY);
    }
}

void consumer_task(void *param) {
    data_t item;
    for (;;) {
        xQueueReceive(data_queue, &item, portMAX_DELAY);
        process_data(&item);
    }
}
```

### Resource Protection with Mutex

**Problem**: Multiple tasks accessing shared resource (I2C, SPI, UART)

**Solution**: Use mutex for mutual exclusion

```c
SemaphoreHandle_t resource_mutex;

status_t access_shared_resource(void) {
    status_t result;

    if (pdTRUE == xSemaphoreTake(resource_mutex, pdMS_TO_TICKS(100))) {
        result = use_resource();
        xSemaphoreGive(resource_mutex);
    } else {
        result = STATUS_TIMEOUT;
    }

    return result;
}
```

### Event Notification with Semaphore

**Problem**: ISR needs to wake up task

**Solution**: Use binary semaphore

```c
SemaphoreHandle_t event_sem;

void ISR_Handler(void) {
    BaseType_t higher_priority_woken = pdFALSE;
    xSemaphoreGiveFromISR(event_sem, &higher_priority_woken);
    portYIELD_FROM_ISR(higher_priority_woken);
}

void event_task(void *param) {
    for (;;) {
        if (pdTRUE == xSemaphoreTake(event_sem, portMAX_DELAY)) {
            handle_event();
        }
    }
}
```

---

## Best Practices

### Stack Sizing

- **FreeRTOS**: Stack in words (multiply by 4 for bytes on 32-bit)
- **Zephyr**: Stack in bytes
- **ThreadX**: Stack in bytes
- **Tool**: Use stack watermarking to measure actual usage

```c
/* FreeRTOS stack usage check */
UBaseType_t uxHighWaterMark = uxTaskGetStackHighWaterMark(task_handle);
```

### Priority Assignment

**Rate Monotonic Scheduling**: Assign priorities inversely proportional to period
- Shortest period = Highest priority
- Longest period = Lowest priority

```c
/* Example priority assignment */
#define FAST_TASK_PRIORITY   (tskIDLE_PRIORITY + 3)  // 10ms period
#define MEDIUM_TASK_PRIORITY (tskIDLE_PRIORITY + 2)  // 50ms period
#define SLOW_TASK_PRIORITY   (tskIDLE_PRIORITY + 1)  // 1000ms period
```

### Avoiding Priority Inversion

Use mutexes with priority inheritance:

```c
/* FreeRTOS: Mutex automatically implements priority inheritance */
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

/* Zephyr: Mutex with priority inheritance (default) */
K_MUTEX_DEFINE(mutex);

/* ThreadX: Enable priority inheritance */
tx_mutex_create(&mutex, "MyMutex", TX_INHERIT);
```

### Watchdog Integration

```c
/* FreeRTOS idle task hook */
void vApplicationIdleHook(void) {
    watchdog_feed();
}

/* Or per-task watchdog feeding */
void critical_task(void *param) {
    for (;;) {
        perform_work();
        watchdog_feed();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

---

## References

- [FreeRTOS Developer Documentation](https://www.freertos.org/Documentation/RTOS_book.html)
- [Zephyr RTOS API Documentation](https://docs.zephyrproject.org/latest/kernel/index.html)
- [ThreadX User Guide](https://learn.microsoft.com/en-us/azure/rtos/threadx/)
- "Patterns for Time-Triggered Embedded Systems" by Michael J. Pont

---

**Use this guide to ensure consistent, safe, and efficient RTOS API usage across embedded projects.**
