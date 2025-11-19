/*
 * Advanced Power Management System
 * Production-grade power management for battery-powered IoT devices
 *
 * Features:
 * - Multi-level sleep modes
 * - Dynamic voltage and frequency scaling
 * - Battery monitoring and fuel gauge
 * - Power state machine
 * - Wake-up source management
 */

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* ============================================================================
 * Power State Machine
 * ============================================================================ */

typedef enum {
    POWER_STATE_ACTIVE,          /* Full performance */
    POWER_STATE_IDLE,            /* Reduced clock */
    POWER_STATE_LIGHT_SLEEP,     /* CPU stopped, peripherals active */
    POWER_STATE_DEEP_SLEEP,      /* Most peripherals off, RAM retained */
    POWER_STATE_STANDBY,         /* Everything off, minimal RAM */
    POWER_STATE_SHUTDOWN         /* Complete power-off */
} power_state_t;

typedef struct {
    power_state_t current_state;
    power_state_t requested_state;
    uint32_t state_entry_time;
    uint32_t time_in_state_ms;
    uint32_t transition_count;
} power_fsm_t;

static power_fsm_t g_power_fsm = {
    .current_state = POWER_STATE_ACTIVE,
    .requested_state = POWER_STATE_ACTIVE,
    .state_entry_time = 0,
    .time_in_state_ms = 0,
    .transition_count = 0
};

/* ============================================================================
 * Power Profile Configuration
 * ============================================================================ */

typedef struct {
    uint32_t cpu_freq_hz;
    float voltage_v;
    uint32_t max_current_ma;
    uint32_t idle_timeout_ms;
} power_profile_t;

static const power_profile_t g_power_profiles[] = {
    /* ACTIVE: Maximum performance */
    {
        .cpu_freq_hz = 80000000,      /* 80 MHz */
        .voltage_v = 1.2f,
        .max_current_ma = 50,
        .idle_timeout_ms = 5000
    },
    /* IDLE: Reduced performance */
    {
        .cpu_freq_hz = 16000000,      /* 16 MHz */
        .voltage_v = 1.0f,
        .max_current_ma = 10,
        .idle_timeout_ms = 2000
    },
    /* LIGHT_SLEEP: Minimal active */
    {
        .cpu_freq_hz = 0,             /* CPU stopped */
        .voltage_v = 1.0f,
        .max_current_ma = 1,
        .idle_timeout_ms = 10000
    }
};

/* ============================================================================
 * Battery Management
 * ============================================================================ */

#define BATTERY_CAPACITY_MAH        2000
#define BATTERY_FULL_VOLTAGE_MV     4200
#define BATTERY_EMPTY_VOLTAGE_MV    3000
#define BATTERY_CRITICAL_VOLTAGE_MV 3200

typedef enum {
    BATTERY_STATE_FULL,
    BATTERY_STATE_GOOD,
    BATTERY_STATE_LOW,
    BATTERY_STATE_CRITICAL,
    BATTERY_STATE_UNKNOWN
} battery_state_t;

typedef struct {
    uint16_t voltage_mv;
    uint8_t percentage;
    battery_state_t state;
    float capacity_remaining_mah;
    float current_consumption_ma;
    uint32_t estimated_runtime_sec;
} battery_info_t;

static battery_info_t g_battery = {
    .voltage_mv = 0,
    .percentage = 0,
    .state = BATTERY_STATE_UNKNOWN,
    .capacity_remaining_mah = 0,
    .current_consumption_ma = 0,
    .estimated_runtime_sec = 0
};

/* Read battery voltage from ADC */
uint16_t battery_read_voltage_mv(void) {
    /* Platform-specific ADC read */
    extern uint16_t adc_read_battery(void);
    return adc_read_battery();
}

/* Update battery information */
void battery_update_info(battery_info_t *battery) {
    battery->voltage_mv = battery_read_voltage_mv();

    /* Calculate percentage (Li-Ion discharge curve approximation) */
    if (battery->voltage_mv >= BATTERY_FULL_VOLTAGE_MV) {
        battery->percentage = 100;
    } else if (battery->voltage_mv <= BATTERY_EMPTY_VOLTAGE_MV) {
        battery->percentage = 0;
    } else {
        /* Non-linear Li-Ion curve (simplified) */
        float normalized = (float)(battery->voltage_mv - BATTERY_EMPTY_VOLTAGE_MV) /
                          (BATTERY_FULL_VOLTAGE_MV - BATTERY_EMPTY_VOLTAGE_MV);
        battery->percentage = (uint8_t)(normalized * 100.0f);
    }

    /* Determine state */
    if (battery->voltage_mv >= 4000) {
        battery->state = BATTERY_STATE_FULL;
    } else if (battery->voltage_mv >= 3700) {
        battery->state = BATTERY_STATE_GOOD;
    } else if (battery->voltage_mv >= BATTERY_CRITICAL_VOLTAGE_MV) {
        battery->state = BATTERY_STATE_LOW;
    } else {
        battery->state = BATTERY_STATE_CRITICAL;
    }

    /* Calculate remaining capacity */
    battery->capacity_remaining_mah = (battery->percentage / 100.0f) * BATTERY_CAPACITY_MAH;

    /* Estimate runtime */
    if (battery->current_consumption_ma > 0.1f) {
        battery->estimated_runtime_sec =
            (uint32_t)((battery->capacity_remaining_mah / battery->current_consumption_ma) * 3600.0f);
    } else {
        battery->estimated_runtime_sec = 0xFFFFFFFF;  /* Infinite */
    }
}

/* Coulomb counting for more accurate state-of-charge */
typedef struct {
    float accumulated_mah;
    uint32_t last_update_ms;
    float current_ma;
} coulomb_counter_t;

static coulomb_counter_t g_coulomb_counter = {
    .accumulated_mah = 0,
    .last_update_ms = 0,
    .current_ma = 0
};

void coulomb_counter_update(coulomb_counter_t *counter, float current_ma) {
    extern uint32_t get_system_time_ms(void);
    uint32_t now_ms = get_system_time_ms();

    if (counter->last_update_ms != 0) {
        uint32_t dt_ms = now_ms - counter->last_update_ms;
        float dt_hours = dt_ms / 3600000.0f;

        /* Integrate current over time */
        counter->accumulated_mah += current_ma * dt_hours;
    }

    counter->current_ma = current_ma;
    counter->last_update_ms = now_ms;
}

uint8_t coulomb_counter_get_soc(coulomb_counter_t *counter) {
    float remaining = BATTERY_CAPACITY_MAH - counter->accumulated_mah;
    if (remaining < 0) remaining = 0;
    if (remaining > BATTERY_CAPACITY_MAH) remaining = BATTERY_CAPACITY_MAH;

    return (uint8_t)((remaining / BATTERY_CAPACITY_MAH) * 100.0f);
}

/* ============================================================================
 * Power State Transitions
 * ============================================================================ */

/* Platform-specific functions (implement these for your hardware) */
extern void platform_enter_light_sleep(uint32_t duration_ms);
extern void platform_enter_deep_sleep(uint32_t duration_ms);
extern void platform_enter_standby(void);
extern void platform_set_cpu_freq(uint32_t freq_hz);
extern void platform_set_voltage(float voltage_v);
extern void platform_disable_peripherals(void);
extern void platform_enable_peripherals(void);

void power_enter_state(power_state_t state) {
    extern uint32_t get_system_time_ms(void);

    /* Record transition */
    g_power_fsm.time_in_state_ms = get_system_time_ms() - g_power_fsm.state_entry_time;
    g_power_fsm.current_state = state;
    g_power_fsm.state_entry_time = get_system_time_ms();
    g_power_fsm.transition_count++;

    switch (state) {
        case POWER_STATE_ACTIVE:
            platform_enable_peripherals();
            platform_set_voltage(1.2f);
            platform_set_cpu_freq(80000000);
            break;

        case POWER_STATE_IDLE:
            platform_set_voltage(1.0f);
            platform_set_cpu_freq(16000000);
            break;

        case POWER_STATE_LIGHT_SLEEP:
            platform_enter_light_sleep(g_power_profiles[POWER_STATE_IDLE].idle_timeout_ms);
            break;

        case POWER_STATE_DEEP_SLEEP:
            platform_disable_peripherals();
            platform_enter_deep_sleep(60000);  /* Wake after 1 minute */
            break;

        case POWER_STATE_STANDBY:
            platform_disable_peripherals();
            platform_enter_standby();
            break;

        case POWER_STATE_SHUTDOWN:
            /* Save critical data before shutdown */
            /* ... */
            platform_enter_standby();
            break;
    }
}

/* Determine optimal power state based on conditions */
power_state_t power_determine_next_state(void) {
    extern bool system_is_busy(void);
    extern uint32_t get_idle_time_ms(void);

    /* Critical battery: enter low-power mode */
    if (g_battery.state == BATTERY_STATE_CRITICAL) {
        return POWER_STATE_DEEP_SLEEP;
    }

    /* System busy: stay active */
    if (system_is_busy()) {
        return POWER_STATE_ACTIVE;
    }

    /* Check idle time */
    uint32_t idle_ms = get_idle_time_ms();

    if (idle_ms < 1000) {
        return POWER_STATE_ACTIVE;
    } else if (idle_ms < 5000) {
        return POWER_STATE_IDLE;
    } else if (idle_ms < 30000) {
        return POWER_STATE_LIGHT_SLEEP;
    } else {
        return POWER_STATE_DEEP_SLEEP;
    }
}

/* Main power management task */
void power_manager_task(void) {
    const uint32_t UPDATE_INTERVAL_MS = 1000;

    for (;;) {
        /* Update battery status */
        battery_update_info(&g_battery);

        /* Determine optimal power state */
        power_state_t next_state = power_determine_next_state();

        /* Transition if needed */
        if (next_state != g_power_fsm.current_state) {
            power_enter_state(next_state);
        }

        /* Wait before next update */
        extern void delay_ms(uint32_t ms);
        delay_ms(UPDATE_INTERVAL_MS);
    }
}

/* ============================================================================
 * Wake-Up Source Management
 * ============================================================================ */

typedef enum {
    WAKEUP_SOURCE_NONE      = 0x00,
    WAKEUP_SOURCE_RTC       = 0x01,
    WAKEUP_SOURCE_GPIO      = 0x02,
    WAKEUP_SOURCE_UART      = 0x04,
    WAKEUP_SOURCE_I2C       = 0x08,
    WAKEUP_SOURCE_TIMER     = 0x10
} wakeup_source_t;

typedef struct {
    uint32_t enabled_sources;
    uint32_t active_source;
    uint32_t wakeup_count[8];  /* Per-source counters */
} wakeup_manager_t;

static wakeup_manager_t g_wakeup_manager = {0};

void wakeup_enable_source(wakeup_source_t source) {
    g_wakeup_manager.enabled_sources |= source;

    /* Platform-specific configuration */
    if (source & WAKEUP_SOURCE_RTC) {
        extern void configure_rtc_wakeup(void);
        configure_rtc_wakeup();
    }

    if (source & WAKEUP_SOURCE_GPIO) {
        extern void configure_gpio_wakeup(void);
        configure_gpio_wakeup();
    }
}

void wakeup_disable_source(wakeup_source_t source) {
    g_wakeup_manager.enabled_sources &= ~source;
}

void wakeup_process_event(wakeup_source_t source) {
    g_wakeup_manager.active_source = source;

    /* Update statistics */
    for (int i = 0; i < 8; i++) {
        if (source & (1 << i)) {
            g_wakeup_manager.wakeup_count[i]++;
        }
    }

    /* Return to active state */
    power_enter_state(POWER_STATE_ACTIVE);
}

/* ============================================================================
 * Dynamic Voltage and Frequency Scaling (DVFS)
 * ============================================================================ */

typedef struct {
    uint32_t frequency_hz;
    float voltage_v;
    uint32_t power_mw;
} dvfs_point_t;

static const dvfs_point_t g_dvfs_table[] = {
    {  8000000, 0.90f,  5 },   /*  8 MHz @ 0.9V */
    { 16000000, 0.95f, 10 },   /* 16 MHz @ 0.95V */
    { 32000000, 1.05f, 25 },   /* 32 MHz @ 1.05V */
    { 48000000, 1.10f, 40 },   /* 48 MHz @ 1.1V */
    { 80000000, 1.20f, 80 }    /* 80 MHz @ 1.2V */
};

#define DVFS_TABLE_SIZE (sizeof(g_dvfs_table) / sizeof(dvfs_point_t))

void dvfs_set_performance_level(uint8_t level) {
    if (level >= DVFS_TABLE_SIZE) {
        level = DVFS_TABLE_SIZE - 1;
    }

    const dvfs_point_t *point = &g_dvfs_table[level];

    /* Voltage scaling (increase voltage before frequency) */
    if (point->voltage_v > platform_get_current_voltage()) {
        platform_set_voltage(point->voltage_v);
        extern void delay_us(uint32_t us);
        delay_us(100);  /* Voltage stabilization time */
    }

    /* Frequency scaling */
    platform_set_cpu_freq(point->frequency_hz);

    /* Voltage scaling (decrease voltage after frequency) */
    if (point->voltage_v < platform_get_current_voltage()) {
        platform_set_voltage(point->voltage_v);
    }
}

extern float platform_get_current_voltage(void);

/* Adaptive DVFS based on CPU load */
typedef struct {
    uint32_t active_cycles;
    uint32_t total_cycles;
    uint8_t current_level;
    uint32_t measurement_window_ms;
} dvfs_controller_t;

static dvfs_controller_t g_dvfs_ctrl = {
    .current_level = DVFS_TABLE_SIZE - 1,  /* Start at max performance */
    .measurement_window_ms = 1000
};

void dvfs_update_adaptive(dvfs_controller_t *ctrl) {
    /* Calculate CPU utilization */
    float utilization = (float)ctrl->active_cycles / ctrl->total_cycles;

    /* Determine appropriate performance level */
    uint8_t target_level;

    if (utilization > 0.8f) {
        target_level = DVFS_TABLE_SIZE - 1;  /* Max performance */
    } else if (utilization > 0.5f) {
        target_level = DVFS_TABLE_SIZE - 2;  /* High performance */
    } else if (utilization > 0.2f) {
        target_level = DVFS_TABLE_SIZE - 3;  /* Medium performance */
    } else {
        target_level = 0;  /* Low performance */
    }

    /* Apply hysteresis to prevent oscillation */
    if (target_level != ctrl->current_level) {
        if (abs((int)target_level - (int)ctrl->current_level) > 1 ||
            utilization > 0.9f || utilization < 0.1f) {
            dvfs_set_performance_level(target_level);
            ctrl->current_level = target_level;
        }
    }

    /* Reset counters for next measurement window */
    ctrl->active_cycles = 0;
    ctrl->total_cycles = 0;
}

/* ============================================================================
 * Power Budget Management
 * ============================================================================ */

typedef struct {
    uint32_t budget_mw;          /* Power budget in mW */
    uint32_t current_usage_mw;   /* Current power consumption */
    uint32_t peak_usage_mw;      /* Peak power consumption */
    bool budget_exceeded;
} power_budget_t;

static power_budget_t g_power_budget = {
    .budget_mw = 100,            /* 100mW budget */
    .current_usage_mw = 0,
    .peak_usage_mw = 0,
    .budget_exceeded = false
};

void power_budget_set(uint32_t budget_mw) {
    g_power_budget.budget_mw = budget_mw;
}

void power_budget_update(uint32_t usage_mw) {
    g_power_budget.current_usage_mw = usage_mw;

    if (usage_mw > g_power_budget.peak_usage_mw) {
        g_power_budget.peak_usage_mw = usage_mw;
    }

    if (usage_mw > g_power_budget.budget_mw) {
        g_power_budget.budget_exceeded = true;

        /* Take corrective action */
        extern void power_budget_enforce(void);
        power_budget_enforce();
    } else {
        g_power_budget.budget_exceeded = false;
    }
}

/* Enforce power budget by throttling */
void power_budget_enforce(void) {
    /* Reduce performance level */
    if (g_dvfs_ctrl.current_level > 0) {
        dvfs_set_performance_level(g_dvfs_ctrl.current_level - 1);
    }

    /* Disable non-essential peripherals */
    extern void disable_non_essential_peripherals(void);
    disable_non_essential_peripherals();
}
