# FreeRTOS Task Scheduling Guide

## Scheduling Fundamentals

### Preemptive Priority-Based Scheduling

FreeRTOS uses **preemptive priority-based scheduling**:
- Higher priority tasks always run before lower priority tasks
- Equal priority tasks share CPU time (round-robin if enabled)
- Tasks can be preempted at any time

### Priority Levels

```c
// FreeRTOSConfig.h
#define configMAX_PRIORITIES  7  // 0 (lowest) to 6 (highest)

// tskIDLE_PRIORITY is always 0

// Typical priority assignment
#define PRIORITY_IDLE      (tskIDLE_PRIORITY + 0)  // 0
#define PRIORITY_LOW       (tskIDLE_PRIORITY + 1)  // 1
#define PRIORITY_NORMAL    (tskIDLE_PRIORITY + 2)  // 2
#define PRIORITY_HIGH      (tskIDLE_PRIORITY + 3)  // 3
#define PRIORITY_REALTIME  (tskIDLE_PRIORITY + 4)  // 4
```

## Rate Monotonic Scheduling (RMS)

### Theory

**Liu & Layland (1973)**: For periodic tasks, assign priorities inversely proportional to period:
- Shortest period = Highest priority
- Longest period = Lowest priority

### Schedulability Test

```
n
Σ (Ci / Ti) ≤ n * (2^(1/n) - 1)
i=1

Where:
- Ci = Worst-case execution time of task i
- Ti = Period of task i
- n  = Number of tasks
```

For n=3: Utilization ≤ 0.7798 (77.98%)

### Example

```c
typedef struct {
    const char *name;
    uint32_t period_ms;     // Ti
    uint32_t wcet_ms;       // Ci
    UBaseType_t priority;
} task_spec_t;

// Task specifications
static const task_spec_t tasks[] = {
    {"Fast",    10,  2, 4},  // Highest priority (shortest period)
    {"Medium",  50,  8, 3},
    {"Slow",   100, 15, 2},  // Lowest priority (longest period)
};

// Schedulability check
void check_schedulability(void) {
    float utilization = 0.0f;
    const size_t n = sizeof(tasks) / sizeof(tasks[0]);

    for (size_t i = 0; i < n; i++) {
        float u = (float)tasks[i].wcet_ms / (float)tasks[i].period_ms;
        utilization += u;
        printf("%s: U=%.4f\n", tasks[i].name, u);
    }

    float bound = (float)n * (powf(2.0f, 1.0f/(float)n) - 1.0f);

    printf("Total utilization: %.4f\n", utilization);
    printf("RMS bound: %.4f\n", bound);
    printf("Schedulable: %s\n", (utilization <= bound) ? "YES" : "NO");
}

// Output:
// Fast: U=0.2000
// Medium: U=0.1600
// Slow: U=0.1500
// Total utilization: 0.5100
// RMS bound: 0.7798
// Schedulable: YES
```

## Periodic Task Pattern

### Using vTaskDelayUntil()

```c
void periodic_task(void *parameters) {
    TickType_t last_wake_time = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(100);  // 100ms

    for (;;) {
        // Task work (execution time < period!)
        uint32_t start = xTaskGetTickCount();

        perform_task_work();

        uint32_t elapsed = xTaskGetTickCount() - start;

        // Check for deadline miss
        if (elapsed > period) {
            printf("WARNING: Task exceeded period!\n");
        }

        // Wait for next period (absolute timing)
        vTaskDelayUntil(&last_wake_time, period);
    }
}
```

### vTaskDelay() vs vTaskDelayUntil()

| Function | Timing | Use Case |
|----------|--------|----------|
| vTaskDelay() | Relative (from now) | Non-critical delays |
| vTaskDelayUntil() | Absolute (precise period) | Periodic tasks (RMS) |

```c
// BAD: Drift over time
void bad_periodic_task(void *param) {
    for (;;) {
        do_work();  // Takes varying time
        vTaskDelay(pdMS_TO_TICKS(100));  // Period drifts!
    }
}

// GOOD: No drift
void good_periodic_task(void *param) {
    TickType_t last_wake = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(100);

    for (;;) {
        do_work();  // Execution time varies
        vTaskDelayUntil(&last_wake, period);  // Precise 100ms period
    }
}
```

## Priority Inversion

### Problem

```
High priority task (H): Waits for mutex held by Low (L)
Medium priority task (M): Preempts Low (L)
Result: High (H) waits for Medium (M) indirectly!
```

### Solution 1: Priority Inheritance (FreeRTOS Default)

```c
// Mutex automatically implements priority inheritance
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

// When H blocks on mutex held by L:
// - L inherits H's priority temporarily
// - M cannot preempt L
// - L finishes, releases mutex
// - H gets mutex, L returns to original priority
```

### Solution 2: Priority Ceiling

```c
void high_priority_task(void *param) {
    UBaseType_t original_priority = uxTaskPriorityGet(NULL);

    // Raise priority to ceiling
    vTaskPrioritySet(NULL, CEILING_PRIORITY);

    // Critical section (no task with priority < CEILING can preempt)
    access_shared_resource();

    // Restore priority
    vTaskPrioritySet(NULL, original_priority);
}
```

## Task State Diagram

```
                 ┌─────────────┐
        ┌────────┤   READY     │◄────────┐
        │        └──────┬──────┘         │
        │               │                │
        │         Highest priority       │
        │         task selected          │
        │               │                │
        │               ▼                │
        │        ┌─────────────┐         │
        │        │   RUNNING   │         │
        │        └──────┬──────┘         │
        │               │                │
        │      ┌────────┼────────┐       │
        │      │        │        │       │
        │   Delay/  Blocked  Preempted  │
        │   Suspend   on I/O             │
        │      │        │        │       │
        │      ▼        ▼        └───────┘
        │  ┌────────┐ ┌────────┐
        └──┤BLOCKED │ │SUSPENDED│
           └────────┘ └────────┘
```

## Context Switch Overhead

### Measurement

```c
volatile uint32_t context_switch_count = 0;

void vApplicationTickHook(void) {
    static TaskHandle_t prev_task = NULL;
    TaskHandle_t current_task = xTaskGetCurrentTaskHandle();

    if (current_task != prev_task) {
        context_switch_count++;
        prev_task = current_task;
    }
}

void monitor_context_switches(void) {
    static uint32_t last_count = 0;
    uint32_t current_count = context_switch_count;
    uint32_t switches_per_second = (current_count - last_count);

    printf("Context switches/sec: %lu\n", switches_per_second);

    last_count = current_count;
}
```

### Minimizing Context Switches

1. **Use appropriate priorities** (don't over-prioritize)
2. **Batch work** in tasks (reduce wake-ups)
3. **Increase tick period** (if possible)
4. **Use direct-to-task notifications** (faster than queues)

## Deadline Monitoring

```c
typedef struct {
    TickType_t period;
    TickType_t deadline;
    uint32_t missed_deadlines;
    uint32_t total_invocations;
} task_stats_t;

void deadline_monitored_task(void *param) {
    task_stats_t *stats = (task_stats_t *)param;
    TickType_t last_wake = xTaskGetTickCount();

    for (;;) {
        TickType_t start = xTaskGetTickCount();

        // Task work
        perform_work();

        TickType_t end = xTaskGetTickCount();
        TickType_t execution_time = end - start;

        stats->total_invocations++;

        // Check deadline
        if (execution_time > stats->deadline) {
            stats->missed_deadlines++;

            printf("DEADLINE MISS: %lu ms (deadline: %lu ms)\n",
                   execution_time, stats->deadline);
        }

        vTaskDelayUntil(&last_wake, stats->period);
    }
}

void print_task_stats(task_stats_t *stats) {
    float miss_rate = 100.0f * stats->missed_deadlines / stats->total_invocations;

    printf("Deadline misses: %lu / %lu (%.2f%%)\n",
           stats->missed_deadlines,
           stats->total_invocations,
           miss_rate);
}
```

## CPU Utilization Monitoring

```c
#include "FreeRTOS.h"
#include "task.h"

void print_cpu_stats(void) {
    TaskStatus_t *pxTaskStatusArray;
    UBaseType_t uxArraySize, x;
    uint32_t ulTotalRunTime;

    // Get number of tasks
    uxArraySize = uxTaskGetNumberOfTasks();

    // Allocate array
    pxTaskStatusArray = pvPortMalloc(uxArraySize * sizeof(TaskStatus_t));

    if (pxTaskStatusArray != NULL) {
        // Get task stats
        uxArraySize = uxTaskGetSystemState(pxTaskStatusArray,
                                             uxArraySize,
                                             &ulTotalRunTime);

        printf("Task          \tAbs Time\tPercentage\n");
        printf("****************************************\n");

        for (x = 0; x < uxArraySize; x++) {
            uint32_t runtime = pxTaskStatusArray[x].ulRunTimeCounter;
            float percentage = (100.0f * runtime) / ulTotalRunTime;

            printf("%-16s\t%lu\t\t%.2f%%\n",
                   pxTaskStatusArray[x].pcTaskName,
                   runtime,
                   percentage);
        }

        vPortFree(pxTaskStatusArray);
    }
}

// FreeRTOSConfig.h requirements:
// #define configGENERATE_RUN_TIME_STATS        1
// #define configUSE_TRACE_FACILITY             1
// #define configUSE_STATS_FORMATTING_FUNCTIONS 1
```

## Best Practices

1. **Use RMS for periodic tasks** (assign priorities by period)
2. **Keep high-priority tasks short** (minimize blocking time)
3. **Use vTaskDelayUntil() for periodic tasks** (precise timing)
4. **Monitor deadline misses** (detect overloads early)
5. **Check schedulability** (verify utilization < RMS bound)
6. **Minimize priority levels** (3-5 priorities often sufficient)
7. **Use mutexes for shared resources** (priority inheritance)
8. **Profile execution times** (know your WCET)

## Common Pitfalls

### ❌ Priority Inversion
```c
// BAD: Binary semaphore doesn't prevent priority inversion
SemaphoreHandle_t sem = xSemaphoreCreateBinary();

// GOOD: Mutex implements priority inheritance
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();
```

### ❌ Busy Waiting
```c
// BAD: Wastes CPU
while (!flag) {
    // Busy wait
}

// GOOD: Block on semaphore
xSemaphoreTake(sem, portMAX_DELAY);
```

### ❌ Unbounded Execution Time
```c
// BAD: Unbounded loop
while (condition) {
    process_item();  // Could run forever
}

// GOOD: Bounded execution
for (int i = 0; i < MAX_ITEMS; i++) {
    if (!condition) break;
    process_item();
}
```

## References

- "Real-Time Systems" by Jane Liu
- FreeRTOS Documentation: www.freertos.org
- "Rate Monotonic Analysis" by Liu & Layland (1973)
