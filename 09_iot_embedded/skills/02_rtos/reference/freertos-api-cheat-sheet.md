# FreeRTOS API Cheat Sheet

## Task Management

### Create Task
```c
BaseType_t xTaskCreate(
    TaskFunction_t pvTaskCode,      // Task function
    const char *pcName,             // Task name (debug)
    uint16_t usStackDepth,          // Stack size (words)
    void *pvParameters,             // Parameters
    UBaseType_t uxPriority,         // Priority
    TaskHandle_t *pxCreatedTask     // Handle (optional)
);

// Example
xTaskCreate(task_func, "MyTask", 256, NULL, 2, &task_handle);
```

### Delete Task
```c
void vTaskDelete(TaskHandle_t xTask);

// Delete self
vTaskDelete(NULL);
```

### Delay
```c
// Relative delay (from now)
void vTaskDelay(const TickType_t xTicksToDelay);

// Absolute delay (periodic)
void vTaskDelayUntil(TickType_t *pxPreviousWakeTime,
                     const TickType_t xTimeIncrement);

// Example: 100ms delay
vTaskDelay(pdMS_TO_TICKS(100));
```

### Priority
```c
// Get priority
UBaseType_t uxTaskPriorityGet(TaskHandle_t xTask);

// Set priority
void vTaskPrioritySet(TaskHandle_t xTask, UBaseType_t uxNewPriority);
```

### Suspend/Resume
```c
void vTaskSuspend(TaskHandle_t xTaskToSuspend);
void vTaskResume(TaskHandle_t xTaskToResume);
```

## Queue

### Create
```c
QueueHandle_t xQueueCreate(UBaseType_t uxQueueLength,
                           UBaseType_t uxItemSize);

// Example
QueueHandle_t queue = xQueueCreate(10, sizeof(uint32_t));
```

### Send
```c
// Send to back
BaseType_t xQueueSend(QueueHandle_t xQueue,
                      const void *pvItemToQueue,
                      TickType_t xTicksToWait);

// Send to front
BaseType_t xQueueSendToFront(QueueHandle_t xQueue,
                             const void *pvItemToQueue,
                             TickType_t xTicksToWait);

// From ISR
BaseType_t xQueueSendFromISR(QueueHandle_t xQueue,
                             const void *pvItemToQueue,
                             BaseType_t *pxHigherPriorityTaskWoken);
```

### Receive
```c
BaseType_t xQueueReceive(QueueHandle_t xQueue,
                         void *pvBuffer,
                         TickType_t xTicksToWait);

// From ISR
BaseType_t xQueueReceiveFromISR(QueueHandle_t xQueue,
                                void *pvBuffer,
                                BaseType_t *pxHigherPriorityTaskWoken);
```

## Semaphore

### Binary Semaphore
```c
SemaphoreHandle_t xSemaphoreCreateBinary(void);

// Give
BaseType_t xSemaphoreGive(SemaphoreHandle_t xSemaphore);

// Take
BaseType_t xSemaphoreTake(SemaphoreHandle_t xSemaphore,
                          TickType_t xTicksToWait);

// From ISR
BaseType_t xSemaphoreGiveFromISR(SemaphoreHandle_t xSemaphore,
                                 BaseType_t *pxHigherPriorityTaskWoken);
```

### Mutex
```c
SemaphoreHandle_t xSemaphoreCreateMutex(void);

// Take mutex (with priority inheritance)
xSemaphoreTake(mutex, portMAX_DELAY);

// Critical section
do_protected_operation();

// Give mutex
xSemaphoreGive(mutex);
```

### Counting Semaphore
```c
SemaphoreHandle_t xSemaphoreCreateCounting(
    UBaseType_t uxMaxCount,
    UBaseType_t uxInitialCount);
```

## Event Groups

### Create
```c
EventGroupHandle_t xEventGroupCreate(void);
```

### Set Bits
```c
EventBits_t xEventGroupSetBits(EventGroupHandle_t xEventGroup,
                               const EventBits_t uxBitsToSet);

// From ISR
BaseType_t xEventGroupSetBitsFromISR(EventGroupHandle_t xEventGroup,
                                     const EventBits_t uxBitsToSet,
                                     BaseType_t *pxHigherPriorityTaskWoken);
```

### Wait Bits
```c
EventBits_t xEventGroupWaitBits(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToWaitFor,
    const BaseType_t xClearOnExit,
    const BaseType_t xWaitForAllBits,
    TickType_t xTicksToWait);

// Example: Wait for bit 0 and bit 1
EventBits_t bits = xEventGroupWaitBits(
    event_group,
    BIT0 | BIT1,
    pdTRUE,     // Clear on exit
    pdTRUE,     // Wait for all bits
    portMAX_DELAY
);
```

## Software Timers

### Create
```c
TimerHandle_t xTimerCreate(
    const char *pcTimerName,
    const TickType_t xTimerPeriod,
    const UBaseType_t uxAutoReload,
    void *pvTimerID,
    TimerCallbackFunction_t pxCallbackFunction);

// Example: 500ms auto-reload timer
TimerHandle_t timer = xTimerCreate(
    "MyTimer",
    pdMS_TO_TICKS(500),
    pdTRUE,  // Auto-reload
    NULL,
    timer_callback);
```

### Control
```c
// Start
BaseType_t xTimerStart(TimerHandle_t xTimer, TickType_t xTicksToWait);

// Stop
BaseType_t xTimerStop(TimerHandle_t xTimer, TickType_t xTicksToWait);

// Reset
BaseType_t xTimerReset(TimerHandle_t xTimer, TickType_t xTicksToWait);

// Change period
BaseType_t xTimerChangePeriod(TimerHandle_t xTimer,
                              TickType_t xNewPeriod,
                              TickType_t xTicksToWait);
```

## Time Conversion

```c
// Milliseconds to ticks
pdMS_TO_TICKS(milliseconds)

// Seconds to ticks
pdMS_TO_TICKS(seconds * 1000)

// Get current tick count
TickType_t xTaskGetTickCount(void);

// From ISR
TickType_t xTaskGetTickCountFromISR(void);
```

## Memory Management

```c
// Allocate
void *pvPortMalloc(size_t xWantedSize);

// Free
void vPortFree(void *pv);

// Get free heap size
size_t xPortGetFreeHeapSize(void);

// Get minimum ever free heap size
size_t xPortGetMinimumEverFreeHeapSize(void);
```

## Critical Sections

```c
// Enter critical (disable interrupts)
taskENTER_CRITICAL();

// Protected code
critical_operation();

// Exit critical
taskEXIT_CRITICAL();

// ISR-safe version
UBaseType_t uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();
// Critical code
taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);
```

## Scheduler Control

```c
// Start scheduler (never returns)
vTaskStartScheduler();

// Suspend all tasks
vTaskSuspendAll();

// Resume all tasks
xTaskResumeAll();
```

## Stack Monitoring

```c
// Get stack high water mark (minimum free stack)
UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t xTask);

// Check for stack overflow in FreeRTOSConfig.h
#define configCHECK_FOR_STACK_OVERFLOW  2
```

## Common Patterns

### Producer-Consumer
```c
QueueHandle_t queue;

void producer_task(void *param) {
    for (;;) {
        uint32_t data = get_data();
        xQueueSend(queue, &data, portMAX_DELAY);
    }
}

void consumer_task(void *param) {
    uint32_t data;
    for (;;) {
        xQueueReceive(queue, &data, portMAX_DELAY);
        process(data);
    }
}
```

### Event Synchronization
```c
SemaphoreHandle_t sem;

void ISR_Handler(void) {
    BaseType_t higher_woken = pdFALSE;
    xSemaphoreGiveFromISR(sem, &higher_woken);
    portYIELD_FROM_ISR(higher_woken);
}

void task(void *param) {
    for (;;) {
        xSemaphoreTake(sem, portMAX_DELAY);
        handle_event();
    }
}
```

### Periodic Task
```c
void periodic_task(void *param) {
    TickType_t last_wake = xTaskGetTickCount();
    const TickType_t period = pdMS_TO_TICKS(100);

    for (;;) {
        do_work();
        vTaskDelayUntil(&last_wake, period);
    }
}
```

## FreeRTOSConfig.h Essentials

```c
#define configUSE_PREEMPTION                1
#define configUSE_IDLE_HOOK                 0
#define configUSE_TICK_HOOK                 0
#define configCPU_CLOCK_HZ                  80000000
#define configTICK_RATE_HZ                  1000
#define configMAX_PRIORITIES                7
#define configMINIMAL_STACK_SIZE            128
#define configTOTAL_HEAP_SIZE               20480
#define configMAX_TASK_NAME_LEN             16
#define configUSE_16_BIT_TICKS              0
#define configIDLE_SHOULD_YIELD             1
#define configUSE_MUTEXES                   1
#define configUSE_COUNTING_SEMAPHORES       1
#define configUSE_TIMERS                    1
#define configTIMER_TASK_PRIORITY           3
#define configTIMER_QUEUE_LENGTH            10
#define configTIMER_TASK_STACK_DEPTH        256
```
