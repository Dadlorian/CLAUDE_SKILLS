# RTOS Performance Benchmarks

## Context Switch Time

| RTOS | Platform | Clock | Context Switch (µs) |
|------|----------|-------|-------------------|
| FreeRTOS | Cortex-M4 | 84 MHz | 1.2 |
| FreeRTOS | Cortex-M7 | 216 MHz | 0.5 |
| Zephyr | Cortex-M4 | 84 MHz | 1.5 |
| ThreadX | Cortex-M4 | 84 MHz | 0.8 |
| No RTOS | Cortex-M4 | 84 MHz | 0 (baseline) |

## Interrupt Latency

| RTOS | Latency (µs) | Notes |
|------|-------------|--------|
| FreeRTOS | 2-4 | With task switch |
| Zephyr | 3-5 | With task switch |
| Bare-metal | < 1 | Direct ISR |

## Memory Footprint (FreeRTOS)

| Component | RAM (bytes) | Flash (bytes) |
|-----------|-------------|---------------|
| Kernel | 200 | 6,000 |
| Per task | 256-512 | - |
| Queue (10 items, 4 bytes) | 80 | - |
| Semaphore | 20 | - |
| Mutex | 24 | - |

Source: FreeRTOS v10.5, ARM GCC, -Os optimization
