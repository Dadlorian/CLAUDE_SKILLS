# Real-Time Operating Systems (RTOS) - Subskill

**Expert-level RTOS design, implementation, and optimization for deterministic embedded systems**

---

## Expertise Overview

You are an expert in real-time operating systems specializing in:
- RTOS selection and configuration (FreeRTOS, Zephyr, ThreadX, VxWorks, QNX)
- Task scheduling algorithms (priority-based, rate-monotonic, EDF)
- Inter-task communication (queues, semaphores, mutexes, event flags)
- Timing analysis (WCET, response time, deadline scheduling)
- Priority inversion avoidance and resolution
- Real-time performance optimization and debugging

---

## Core Skills

### 1. RTOS Task Design

**FreeRTOS Task Creation**:
```c
#include "FreeRTOS.h"
#include "task.h"

#define SENSOR_TASK_PRIORITY        (tskIDLE_PRIORITY + 2)
#define SENSOR_TASK_STACK_SIZE      (256)  /* Words, not bytes */

static TaskHandle_t sensor_task_handle = NULL;

void sensor_task(void *parameters) {
    (void)parameters;

    /* Task initialization */
    sensor_init();

    /* Periodic task pattern */
    TickType_t last_wake_time = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(100);  /* 100ms period */

    for (;;) {
        /* Read sensor (assume 5ms execution time) */
        int16_t temperature = sensor_read_temperature();

        /* Process data */
        process_sensor_data(temperature);

        /* Wait for next period (precise timing) */
        vTaskDelayUntil(&last_wake_time, period);
    }
}

void create_sensor_task(void) {
    BaseType_t result = xTaskCreate(
        sensor_task,
        "SensorTask",
        SENSOR_TASK_STACK_SIZE,
        NULL,
        SENSOR_TASK_PRIORITY,
        &sensor_task_handle
    );

    configASSERT(pdPASS == result);
}
```

### 2. Priority Assignment (Rate Monotonic Scheduling)

**Liu & Layland Theorem**:
For n periodic tasks with fixed priorities, the system is schedulable if:
```
U = Σ(Ci/Ti) ≤ n * (2^(1/n) - 1)

Where:
- Ci = Worst-case execution time of task i
- Ti = Period of task i
- U = CPU utilization
```

**Example Priority Assignment**:
```c
/* Task characteristics */
typedef struct {
    const char *name;
    uint32_t period_ms;
    uint32_t wcet_ms;
    UBaseType_t priority;
} task_spec_t;

/* Rate Monotonic: Shortest period = Highest priority */
static const task_spec_t tasks[] = {
    {"FastTask",    10,  2, tskIDLE_PRIORITY + 4},  /* Highest */
    {"MediumTask",  50,  8, tskIDLE_PRIORITY + 3},
    {"SlowTask",   100, 15, tskIDLE_PRIORITY + 2},
    {"BgTask",    1000, 50, tskIDLE_PRIORITY + 1}   /* Lowest */
};

/* Schedulability check */
bool check_schedulability(void) {
    float utilization = 0.0f;
    size_t n = sizeof(tasks) / sizeof(tasks[0]);

    for (size_t i = 0; i < n; i++) {
        utilization += (float)tasks[i].wcet_ms / (float)tasks[i].period_ms;
    }

    float bound = (float)n * (powf(2.0f, 1.0f/(float)n) - 1.0f);

    return (utilization <= bound);
}
```

### 3. Inter-Task Communication

**Queue Pattern (Producer-Consumer)**:
```c
#include "queue.h"

#define QUEUE_LENGTH    10

typedef struct {
    uint16_t sensor_id;
    int16_t value;
    uint32_t timestamp;
} sensor_message_t;

static QueueHandle_t sensor_queue = NULL;

void queue_init(void) {
    sensor_queue = xQueueCreate(QUEUE_LENGTH, sizeof(sensor_message_t));
    configASSERT(NULL != sensor_queue);
}

/* Producer task */
void sensor_task(void *param) {
    sensor_message_t msg;

    for (;;) {
        msg.sensor_id = 1;
        msg.value = read_sensor();
        msg.timestamp = xTaskGetTickCount();

        /* Send to queue (block up to 100ms if full) */
        if (pdPASS != xQueueSend(sensor_queue, &msg, pdMS_TO_TICKS(100))) {
            /* Queue full - handle overflow */
            error_log("Queue full");
        }

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

/* Consumer task */
void processing_task(void *param) {
    sensor_message_t msg;

    for (;;) {
        /* Block until message available */
        if (pdPASS == xQueueReceive(sensor_queue, &msg, portMAX_DELAY)) {
            /* Process message */
            process_sensor_reading(msg.sensor_id, msg.value);
        }
    }
}
```

**Mutex for Resource Protection**:
```c
#include "semphr.h"

static SemaphoreHandle_t i2c_mutex = NULL;

void mutex_init(void) {
    i2c_mutex = xSemaphoreCreateMutex();
    configASSERT(NULL != i2c_mutex);
}

/* Protected I2C access */
status_t i2c_write_protected(uint8_t addr, const uint8_t *data, size_t len) {
    status_t result = STATUS_ERROR;

    /* Take mutex (implements priority inheritance automatically) */
    if (pdTRUE == xSemaphoreTake(i2c_mutex, pdMS_TO_TICKS(100))) {
        /* Critical section: exclusive I2C bus access */
        result = i2c_write(addr, data, len);

        /* Always release mutex */
        xSemaphoreGive(i2c_mutex);
    } else {
        /* Timeout acquiring mutex */
        result = STATUS_TIMEOUT;
    }

    return result;
}
```

### 4. Priority Inversion Handling

**Problem Scenario**:
```
High-priority task (H) blocked by low-priority task (L) holding mutex
Medium-priority task (M) preempts L, delaying H indefinitely
```

**Solution 1: Priority Inheritance**:
```c
/* FreeRTOS automatically implements priority inheritance for mutexes */
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

/* When low-priority task holds mutex and high-priority task blocks:
 * - Low-priority task temporarily inherits high priority
 * - Medium-priority tasks cannot preempt
 * - Low-priority task completes critical section
 * - High-priority task unblocks
 */
```

**Solution 2: Priority Ceiling Protocol**:
```c
/* Set task priority to ceiling when entering critical section */
void protected_operation(void) {
    UBaseType_t original_priority = uxTaskPriorityGet(NULL);
    UBaseType_t ceiling_priority = HIGHEST_TASK_PRIORITY;

    /* Raise priority to ceiling */
    vTaskPrioritySet(NULL, ceiling_priority);

    /* Critical section */
    access_shared_resource();

    /* Restore original priority */
    vTaskPrioritySet(NULL, original_priority);
}
```

### 5. Timing Analysis

**Worst-Case Execution Time (WCET) Measurement**:
```c
#include "systick.h"

typedef struct {
    uint32_t min_cycles;
    uint32_t max_cycles;
    uint32_t avg_cycles;
    uint32_t samples;
} timing_stats_t;

static timing_stats_t g_task_timing = {0};

void measure_task_timing(void) {
    uint32_t start_cycles = DWT->CYCCNT;

    /* Task work */
    perform_task_work();

    uint32_t end_cycles = DWT->CYCCNT;
    uint32_t elapsed = end_cycles - start_cycles;

    /* Update statistics */
    if ((0 == g_task_timing.samples) || (elapsed < g_task_timing.min_cycles)) {
        g_task_timing.min_cycles = elapsed;
    }

    if (elapsed > g_task_timing.max_cycles) {
        g_task_timing.max_cycles = elapsed;
    }

    g_task_timing.avg_cycles =
        (g_task_timing.avg_cycles * g_task_timing.samples + elapsed) /
        (g_task_timing.samples + 1);

    g_task_timing.samples++;
}
```

**Deadline Monitoring**:
```c
typedef struct {
    TickType_t period;
    TickType_t deadline;  /* Relative to period start */
    uint32_t missed_deadlines;
} deadline_task_t;

void deadline_task(void *param) {
    deadline_task_t *task_info = (deadline_task_t *)param;
    TickType_t last_wake = xTaskGetTickCount();

    for (;;) {
        TickType_t start_time = xTaskGetTickCount();

        /* Task work */
        perform_work();

        TickType_t end_time = xTaskGetTickCount();
        TickType_t execution_time = end_time - start_time;

        /* Check deadline */
        if (execution_time > task_info->deadline) {
            task_info->missed_deadlines++;
            log_deadline_miss(execution_time, task_info->deadline);
        }

        /* Wait for next period */
        vTaskDelayUntil(&last_wake, task_info->period);
    }
}
```

### 6. Memory and Stack Management

**Stack Overflow Detection**:
```c
/* Enable stack overflow checking in FreeRTOSConfig.h */
#define configCHECK_FOR_STACK_OVERFLOW  2

/* Hook function called on stack overflow */
void vApplicationStackOverflowHook(TaskHandle_t task, char *task_name) {
    /* Log error and halt or reset */
    error_log("Stack overflow in task: %s", task_name);

    /* Disable interrupts */
    taskDISABLE_INTERRUPTS();

    /* Infinite loop or trigger watchdog reset */
    for (;;) {
        /* Optionally toggle LED */
    }
}

/* Check stack high water mark */
void monitor_stack_usage(void) {
    UBaseType_t high_water = uxTaskGetStackHighWaterMark(NULL);

    /* Log if less than 25% margin */
    if (high_water < (SENSOR_TASK_STACK_SIZE / 4)) {
        log_warning("Low stack margin: %u words", high_water);
    }
}
```

**Heap Management**:
```c
/* FreeRTOS heap schemes:
 * heap_1.c - Simple, no free()
 * heap_2.c - Allow free(), but fragmentation
 * heap_3.c - Wrapper around malloc/free
 * heap_4.c - Coalescing free blocks (recommended)
 * heap_5.c - Multiple non-contiguous heaps
 */

/* Monitor heap usage */
void monitor_heap(void) {
    size_t free_heap = xPortGetFreeHeapSize();
    size_t min_ever_free = xPortGetMinimumEverFreeHeapSize();

    if (min_ever_free < (configTOTAL_HEAP_SIZE / 10)) {
        log_warning("Low heap margin: %u bytes", min_ever_free);
    }
}
```

---

## Advanced Patterns

### Event-Driven Architecture

```c
/* Event group for multiple event flags */
#include "event_groups.h"

#define EVENT_BIT_SENSOR_READY   (1 << 0)
#define EVENT_BIT_NETWORK_UP     (1 << 1)
#define EVENT_BIT_DATA_READY     (1 << 2)

static EventGroupHandle_t system_events = NULL;

void events_init(void) {
    system_events = xEventGroupCreate();
}

/* Set event from ISR */
void SENSOR_IRQHandler(void) {
    BaseType_t higher_priority_woken = pdFALSE;

    xEventGroupSetBitsFromISR(
        system_events,
        EVENT_BIT_SENSOR_READY,
        &higher_priority_woken
    );

    portYIELD_FROM_ISR(higher_priority_woken);
}

/* Wait for multiple events */
void processing_task(void *param) {
    const EventBits_t required_events =
        EVENT_BIT_SENSOR_READY | EVENT_BIT_NETWORK_UP;

    for (;;) {
        /* Wait for both events */
        EventBits_t events = xEventGroupWaitBits(
            system_events,
            required_events,
            pdTRUE,         /* Clear on exit */
            pdTRUE,         /* Wait for all bits */
            portMAX_DELAY
        );

        if ((events & required_events) == required_events) {
            /* Both events occurred */
            process_and_transmit_data();
        }
    }
}
```

---

## RTOS Selection Guide

| RTOS      | Best For | Pros | Cons |
|-----------|----------|------|------|
| FreeRTOS  | General embedded | Open-source, widely supported, MIT license | No filesystem by default |
| Zephyr    | Modern IoT devices | Linux Foundation, modular, growing | Steeper learning curve |
| ThreadX   | Safety-critical | TUV certified, Azure integration | Commercial (now free) |
| VxWorks   | Aerospace, automotive | Proven, DO-178C certified | Expensive, proprietary |
| QNX       | Automotive, medical | Microkernel, POSIX, reliability | Commercial licensing |
| Mbed OS   | IoT prototyping | ARM ecosystem, rapid development | Less deterministic |

---

## Best Practices

1. **Design for Determinism**: Ensure bounded execution times
2. **Minimize Blocking**: Use timeouts on all blocking operations
3. **Avoid Dynamic Allocation**: Use static allocation in tasks
4. **Monitor Stack Usage**: Check high water marks regularly
5. **Handle Priority Inversion**: Use mutexes with priority inheritance
6. **Document Timing**: Measure and document WCET for critical tasks
7. **Test Under Load**: Verify timing under worst-case conditions

---

## Debugging Tools

- **FreeRTOS Trace**: SystemView, Tracealyzer
- **Stack Analysis**: uxTaskGetStackHighWaterMark()
- **Timing**: DWT cycle counter, profiling tools
- **Deadlock Detection**: Mutex timeout monitoring

---

## References

- "FreeRTOS Reference Manual" by Richard Barry
- "Real-Time Systems" by Jane Liu
- "Rate Monotonic Analysis" by Liu & Layland (1973)
- RTOS comparison benchmarks from EEMBC
- FreeRTOS.org kernel documentation

---

**Provide deterministic, schedulable, and robust RTOS-based solutions with comprehensive timing analysis and priority management.**
