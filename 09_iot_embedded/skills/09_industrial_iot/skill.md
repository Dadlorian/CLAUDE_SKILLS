# Industrial IoT (IIoT) & OT Security - Subskill

**Expert in SCADA, Modbus, OPC UA, predictive maintenance, and operational technology security**

---

## Expertise Overview

Specialist in industrial IoT:
- Industrial protocols (Modbus RTU/TCP, OPC UA, PROFINET, EtherCAT)
- CAN/CANopen for industrial automation
- SCADA integration and HMI connectivity
- Predictive maintenance and condition monitoring
- Functional safety (IEC 61508, SIL ratings)
- OT security and network segmentation

---

## Core Skills

### 1. Modbus Protocol

**Modbus RTU (Serial)**:
```c
#include <stdint.h>

#define MODBUS_SLAVE_ADDR    1
#define MODBUS_READ_HOLDING  0x03
#define MODBUS_WRITE_SINGLE  0x06

/* CRC-16 calculation (Modbus) */
uint16_t modbus_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;

    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];

        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc >>= 1;
                crc ^= 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }

    return crc;
}

/* Read holding registers */
status_t modbus_read_holding_registers(uint8_t slave_addr,
                                         uint16_t start_addr,
                                         uint16_t num_regs,
                                         uint16_t *values) {
    uint8_t request[8];
    uint8_t response[256];

    /* Build request */
    request[0] = slave_addr;
    request[1] = MODBUS_READ_HOLDING;
    request[2] = (start_addr >> 8) & 0xFF;
    request[3] = start_addr & 0xFF;
    request[4] = (num_regs >> 8) & 0xFF;
    request[5] = num_regs & 0xFF;

    uint16_t crc = modbus_crc16(request, 6);
    request[6] = crc & 0xFF;
    request[7] = (crc >> 8) & 0xFF;

    /* Send request */
    uart_send(request, 8);

    /* Receive response */
    size_t rx_len = uart_receive(response, sizeof(response), 1000);

    /* Verify CRC */
    uint16_t rx_crc = response[rx_len - 2] | (response[rx_len - 1] << 8);
    uint16_t calc_crc = modbus_crc16(response, rx_len - 2);

    if (rx_crc != calc_crc) {
        return STATUS_ERROR;
    }

    /* Parse registers */
    for (uint16_t i = 0; i < num_regs; i++) {
        values[i] = (response[3 + i * 2] << 8) | response[4 + i * 2];
    }

    return STATUS_OK;
}

/* Write single register */
status_t modbus_write_single_register(uint8_t slave_addr,
                                        uint16_t reg_addr,
                                        uint16_t value) {
    uint8_t request[8];

    request[0] = slave_addr;
    request[1] = MODBUS_WRITE_SINGLE;
    request[2] = (reg_addr >> 8) & 0xFF;
    request[3] = reg_addr & 0xFF;
    request[4] = (value >> 8) & 0xFF;
    request[5] = value & 0xFF;

    uint16_t crc = modbus_crc16(request, 6);
    request[6] = crc & 0xFF;
    request[7] = (crc >> 8) & 0xFF;

    uart_send(request, 8);

    /* Wait for echo response */
    uint8_t response[8];
    uart_receive(response, 8, 1000);

    /* Verify response matches request */
    return (memcmp(request, response, 8) == 0) ? STATUS_OK : STATUS_ERROR;
}
```

**Modbus TCP**:
```c
#include "lwip/sockets.h"

#define MODBUS_TCP_PORT  502

typedef struct {
    uint16_t transaction_id;
    uint16_t protocol_id;     /* Always 0 */
    uint16_t length;
    uint8_t unit_id;
} modbus_tcp_header_t;

status_t modbus_tcp_read_registers(int sockfd, uint8_t unit_id,
                                     uint16_t start_addr, uint16_t num_regs,
                                     uint16_t *values) {
    uint8_t request[12];
    uint8_t response[256];
    static uint16_t transaction_id = 0;

    /* Build MBAP header */
    request[0] = (transaction_id >> 8) & 0xFF;
    request[1] = transaction_id & 0xFF;
    request[2] = 0;  /* Protocol ID */
    request[3] = 0;
    request[4] = 0;  /* Length (6 bytes) */
    request[5] = 6;
    request[6] = unit_id;

    /* Modbus PDU */
    request[7] = MODBUS_READ_HOLDING;
    request[8] = (start_addr >> 8) & 0xFF;
    request[9] = start_addr & 0xFF;
    request[10] = (num_regs >> 8) & 0xFF;
    request[11] = num_regs & 0xFF;

    /* Send request */
    send(sockfd, request, 12, 0);

    /* Receive response */
    int rx_len = recv(sockfd, response, sizeof(response), 0);

    if (rx_len < 9) {
        return STATUS_ERROR;
    }

    /* Verify transaction ID */
    uint16_t rx_transaction_id = (response[0] << 8) | response[1];
    if (rx_transaction_id != transaction_id) {
        return STATUS_ERROR;
    }

    /* Parse registers */
    for (uint16_t i = 0; i < num_regs; i++) {
        values[i] = (response[9 + i * 2] << 8) | response[10 + i * 2];
    }

    transaction_id++;
    return STATUS_OK;
}
```

### 2. OPC UA (Open Platform Communications)

**open62541 OPC UA Client**:
```c
#include "open62541.h"

UA_Client* opcua_client_connect(const char *endpoint_url) {
    UA_Client *client = UA_Client_new();
    UA_ClientConfig_setDefault(UA_Client_getConfig(client));

    /* Connect to server */
    UA_StatusCode status = UA_Client_connect(client, endpoint_url);

    if (status != UA_STATUSCODE_GOOD) {
        UA_Client_delete(client);
        return NULL;
    }

    return client;
}

/* Read node value */
status_t opcua_read_variable(UA_Client *client, UA_NodeId node_id, UA_Variant *value) {
    UA_StatusCode status = UA_Client_readValueAttribute(client, node_id, value);
    return (status == UA_STATUSCODE_GOOD) ? STATUS_OK : STATUS_ERROR;
}

/* Write node value */
status_t opcua_write_variable(UA_Client *client, UA_NodeId node_id, UA_Variant *value) {
    UA_StatusCode status = UA_Client_writeValueAttribute(client, node_id, value);
    return (status == UA_STATUSCODE_GOOD) ? STATUS_OK : STATUS_ERROR;
}

/* Subscribe to data changes */
void opcua_subscribe_callback(UA_Client *client, UA_UInt32 subId, void *subContext,
                               UA_UInt32 monId, void *monContext, UA_DataValue *value) {
    if (UA_Variant_hasScalarType(&value->value, &UA_TYPES[UA_TYPES_DOUBLE])) {
        double *data = (double *)value->value.data;
        printf("Received value: %.2f\n", *data);

        /* Trigger alert if threshold exceeded */
        if (*data > ALARM_THRESHOLD) {
            trigger_alarm();
        }
    }
}

status_t opcua_create_subscription(UA_Client *client, UA_NodeId node_id) {
    /* Create subscription */
    UA_CreateSubscriptionRequest request = UA_CreateSubscriptionRequest_default();
    UA_CreateSubscriptionResponse response = UA_Client_Subscriptions_create(client, request,
                                                                              NULL, NULL, NULL);

    if (response.responseHeader.serviceResult != UA_STATUSCODE_GOOD) {
        return STATUS_ERROR;
    }

    /* Create monitored item */
    UA_MonitoredItemCreateRequest monRequest =
        UA_MonitoredItemCreateRequest_default(node_id);

    UA_MonitoredItemCreateResult monResponse =
        UA_Client_MonitoredItems_createDataChange(client, response.subscriptionId,
                                                    UA_TIMESTAMPSTORETURN_BOTH,
                                                    monRequest, NULL,
                                                    opcua_subscribe_callback, NULL);

    return (monResponse.statusCode == UA_STATUSCODE_GOOD) ? STATUS_OK : STATUS_ERROR;
}
```

### 3. CAN Bus (Controller Area Network)

**CAN Frame Transmission**:
```c
#include "can_hal.h"

#define CAN_ID_SENSOR_DATA  0x100
#define CAN_ID_ACTUATOR_CMD 0x200

typedef struct {
    uint32_t id;
    uint8_t dlc;      /* Data length code (0-8) */
    uint8_t data[8];
    bool extended;    /* Extended ID (29-bit) */
    bool rtr;         /* Remote transmission request */
} can_message_t;

status_t can_send_message(const can_message_t *msg) {
    can_tx_msg_t tx_msg;

    tx_msg.StdId = msg->id;
    tx_msg.ExtId = msg->id;
    tx_msg.IDE = msg->extended ? CAN_ID_EXT : CAN_ID_STD;
    tx_msg.RTR = msg->rtr ? CAN_RTR_REMOTE : CAN_RTR_DATA;
    tx_msg.DLC = msg->dlc;

    memcpy(tx_msg.Data, msg->data, msg->dlc);

    /* Transmit */
    return can_transmit(&tx_msg, 100);  /* 100ms timeout */
}

status_t can_receive_message(can_message_t *msg, uint32_t timeout_ms) {
    can_rx_msg_t rx_msg;

    if (can_receive(&rx_msg, timeout_ms) != STATUS_OK) {
        return STATUS_TIMEOUT;
    }

    msg->id = (rx_msg.IDE == CAN_ID_EXT) ? rx_msg.ExtId : rx_msg.StdId;
    msg->dlc = rx_msg.DLC;
    msg->extended = (rx_msg.IDE == CAN_ID_EXT);
    msg->rtr = (rx_msg.RTR == CAN_RTR_REMOTE);

    memcpy(msg->data, rx_msg.Data, rx_msg.DLC);

    return STATUS_OK;
}

/* CANopen NMT (Network Management) */
void canopen_send_nmt_command(uint8_t node_id, uint8_t command) {
    can_message_t msg;

    msg.id = 0x000;  /* NMT COB-ID */
    msg.dlc = 2;
    msg.data[0] = command;  /* 0x01=Start, 0x02=Stop, 0x80=Pre-operational, 0x81=Reset */
    msg.data[1] = node_id;
    msg.extended = false;
    msg.rtr = false;

    can_send_message(&msg);
}
```

### 4. Predictive Maintenance

**Vibration Analysis (FFT)**:
```c
#include "arm_math.h"

#define FFT_SIZE  1024
#define SAMPLE_RATE 10000  /* 10 kHz */

static float32_t fft_input[FFT_SIZE * 2];   /* Real + Imaginary */
static float32_t fft_output[FFT_SIZE];
static arm_rfft_fast_instance_f32 fft_instance;

void vibration_analysis_init(void) {
    arm_rfft_fast_init_f32(&fft_instance, FFT_SIZE);
}

typedef struct {
    float rms_value;
    float peak_frequency;
    float peak_amplitude;
    bool fault_detected;
} vibration_analysis_t;

void analyze_vibration(float32_t *samples, vibration_analysis_t *result) {
    /* Apply windowing (Hanning) */
    for (uint16_t i = 0; i < FFT_SIZE; i++) {
        float window = 0.5f * (1.0f - arm_cos_f32(2.0f * PI * i / (FFT_SIZE - 1)));
        fft_input[i] = samples[i] * window;
    }

    /* Perform FFT */
    arm_rfft_fast_f32(&fft_instance, fft_input, fft_output, 0);

    /* Calculate magnitude spectrum */
    float max_amplitude = 0.0f;
    uint16_t max_bin = 0;

    for (uint16_t i = 0; i < FFT_SIZE / 2; i++) {
        float real = fft_output[i * 2];
        float imag = fft_output[i * 2 + 1];
        float magnitude = sqrtf(real * real + imag * imag);

        if (magnitude > max_amplitude) {
            max_amplitude = magnitude;
            max_bin = i;
        }
    }

    /* Calculate RMS */
    float sum_squares = 0.0f;
    for (uint16_t i = 0; i < FFT_SIZE; i++) {
        sum_squares += samples[i] * samples[i];
    }
    result->rms_value = sqrtf(sum_squares / FFT_SIZE);

    /* Peak frequency */
    result->peak_frequency = (float)max_bin * SAMPLE_RATE / FFT_SIZE;
    result->peak_amplitude = max_amplitude;

    /* Fault detection (thresholds) */
    result->fault_detected = (result->rms_value > RMS_THRESHOLD) ||
                              (result->peak_amplitude > PEAK_THRESHOLD);
}
```

### 5. Functional Safety (IEC 61508)

**Safety Function Example (SIL 2)**:
```c
/* Dual-channel safety architecture */
typedef struct {
    bool channel_a_ok;
    bool channel_b_ok;
    uint32_t discrepancy_count;
    uint32_t test_pulse_count;
} safety_monitor_t;

static safety_monitor_t safety = {0};

/* Safety-critical: Emergency stop */
void safety_emergency_stop(void) {
    /* De-energize all actuators */
    gpio_write(RELAY_MOTOR1, 0);
    gpio_write(RELAY_MOTOR2, 0);
    gpio_write(RELAY_VALVE, 0);

    /* Activate brake */
    gpio_write(BRAKE_ENGAGE, 1);

    /* Log event */
    log_safety_event("Emergency stop activated");
}

/* Dual-channel monitoring */
void safety_monitor_task(void) {
    bool sensor_a = gpio_read(SAFETY_INPUT_A);
    bool sensor_b = gpio_read(SAFETY_INPUT_B);

    if (sensor_a != sensor_b) {
        safety.discrepancy_count++;

        if (safety.discrepancy_count > MAX_DISCREPANCY) {
            /* Fail-safe: initiate emergency stop */
            safety_emergency_stop();
        }
    } else {
        safety.discrepancy_count = 0;
    }

    /* Periodic test pulse */
    if (++safety.test_pulse_count >= TEST_PULSE_INTERVAL) {
        perform_self_test();
        safety.test_pulse_count = 0;
    }
}
```

---

## OT Security (Purdue Model)

### Network Segmentation

**Level 0-1**: Field devices (sensors, actuators)
**Level 2**: Control systems (PLCs, DCS)
**Level 3**: Plant operations (SCADA, HMI)
**Level 4**: Business logistics
**Level 5**: Enterprise network

**Firewall Rules**:
- Deny all by default
- Allow only required protocols (Modbus, OPC UA)
- Implement industrial DMZ
- Use IDS/IPS for anomaly detection

---

## Best Practices

1. **Deterministic Communication**: Use time-synchronized protocols
2. **Redundancy**: Implement failover for critical paths
3. **Safety First**: Follow IEC 61508 for functional safety
4. **Security by Design**: Segment networks, authenticate devices
5. **Monitoring**: Log all critical operations and alarms

---

## References

- IEC 61508 (Functional Safety)
- IEC 62443 (Industrial Security)
- Modbus Organization specifications
- OPC Foundation documentation
- ISA/IEC 62443 standards

---

**Implement robust, safe, and secure industrial IoT systems with deterministic protocols and functional safety compliance.**
