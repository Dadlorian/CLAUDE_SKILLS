/*
 * Modbus RTU Master Implementation
 * Production-grade industrial protocol implementation
 *
 * Features:
 * - Full Modbus RTU master functionality
 * - Multiple function codes support
 * - Exception handling
 * - Timeout and retry logic
 * - Multi-slave communication
 * - Thread-safe operations
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* ============================================================================
 * Modbus Function Codes
 * ============================================================================ */

#define MODBUS_FC_READ_COILS                0x01
#define MODBUS_FC_READ_DISCRETE_INPUTS      0x02
#define MODBUS_FC_READ_HOLDING_REGISTERS    0x03
#define MODBUS_FC_READ_INPUT_REGISTERS      0x04
#define MODBUS_FC_WRITE_SINGLE_COIL         0x05
#define MODBUS_FC_WRITE_SINGLE_REGISTER     0x06
#define MODBUS_FC_WRITE_MULTIPLE_COILS      0x0F
#define MODBUS_FC_WRITE_MULTIPLE_REGISTERS  0x10

/* Modbus Exception Codes */
#define MODBUS_EXCEPTION_ILLEGAL_FUNCTION       0x01
#define MODBUS_EXCEPTION_ILLEGAL_DATA_ADDRESS   0x02
#define MODBUS_EXCEPTION_ILLEGAL_DATA_VALUE     0x03
#define MODBUS_EXCEPTION_SLAVE_DEVICE_FAILURE   0x04
#define MODBUS_EXCEPTION_ACKNOWLEDGE            0x05
#define MODBUS_EXCEPTION_SLAVE_DEVICE_BUSY      0x06
#define MODBUS_EXCEPTION_MEMORY_PARITY_ERROR    0x08

/* ============================================================================
 * Modbus RTU Configuration
 * ============================================================================ */

#define MODBUS_RTU_MAX_PDU_SIZE  253
#define MODBUS_RTU_TIMEOUT_MS    1000
#define MODBUS_RTU_MAX_RETRIES   3

typedef enum {
    MODBUS_STATUS_OK = 0,
    MODBUS_STATUS_TIMEOUT,
    MODBUS_STATUS_CRC_ERROR,
    MODBUS_STATUS_EXCEPTION,
    MODBUS_STATUS_INVALID_LENGTH,
    MODBUS_STATUS_UART_ERROR
} modbus_status_t;

typedef struct {
    uint8_t slave_addr;
    uint32_t baudrate;
    uint8_t data_bits;
    uint8_t stop_bits;
    char parity;  /* 'N', 'E', 'O' */
    uint32_t timeout_ms;
    uint8_t max_retries;

    /* Internal state */
    uint8_t rx_buffer[MODBUS_RTU_MAX_PDU_SIZE + 5];  /* +5 for addr+crc */
    uint16_t rx_length;
    void *uart_handle;
    void *mutex;  /* For thread safety */
} modbus_master_t;

/* ============================================================================
 * CRC-16 Calculation (Modbus)
 * ============================================================================ */

static const uint16_t crc16_table[256] = {
    0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
    0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
    0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
    0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
    0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
    0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
    0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
    0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
    0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
    0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
    0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
    0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
    0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
    0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
    0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
    0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
    0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
    0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
    0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
    0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
    0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
    0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
    0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
    0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
    0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
    0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
    0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
    0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
    0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
    0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
    0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
    0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
};

uint16_t modbus_crc16(const uint8_t *data, uint16_t length) {
    uint16_t crc = 0xFFFF;

    for (uint16_t i = 0; i < length; i++) {
        uint8_t index = (uint8_t)(crc ^ data[i]);
        crc = (crc >> 8) ^ crc16_table[index];
    }

    return crc;
}

/* ============================================================================
 * UART Communication (Platform-specific)
 * ============================================================================ */

extern bool uart_init(void **handle, uint32_t baudrate, uint8_t data_bits,
                      uint8_t stop_bits, char parity);
extern void uart_deinit(void *handle);
extern bool uart_send(void *handle, const uint8_t *data, uint16_t length);
extern uint16_t uart_receive(void *handle, uint8_t *buffer, uint16_t max_length,
                              uint32_t timeout_ms);
extern void uart_flush_rx(void *handle);

/* ============================================================================
 * Modbus Master Initialization
 * ============================================================================ */

bool modbus_master_init(modbus_master_t *master,
                        uint8_t slave_addr,
                        uint32_t baudrate,
                        uint8_t data_bits,
                        uint8_t stop_bits,
                        char parity) {
    master->slave_addr = slave_addr;
    master->baudrate = baudrate;
    master->data_bits = data_bits;
    master->stop_bits = stop_bits;
    master->parity = parity;
    master->timeout_ms = MODBUS_RTU_TIMEOUT_MS;
    master->max_retries = MODBUS_RTU_MAX_RETRIES;

    /* Initialize UART */
    if (!uart_init(&master->uart_handle, baudrate, data_bits, stop_bits, parity)) {
        return false;
    }

    /* Create mutex for thread safety */
    extern bool mutex_create(void **mutex);
    mutex_create(&master->mutex);

    return true;
}

void modbus_master_deinit(modbus_master_t *master) {
    uart_deinit(master->uart_handle);

    extern void mutex_destroy(void *mutex);
    mutex_destroy(master->mutex);
}

/* ============================================================================
 * Low-Level Modbus Transaction
 * ============================================================================ */

static modbus_status_t modbus_transaction(modbus_master_t *master,
                                           const uint8_t *request,
                                           uint16_t request_length,
                                           uint8_t *response,
                                           uint16_t *response_length) {
    extern bool mutex_lock(void *mutex, uint32_t timeout_ms);
    extern void mutex_unlock(void *mutex);

    /* Lock for thread safety */
    if (!mutex_lock(master->mutex, 1000)) {
        return MODBUS_STATUS_TIMEOUT;
    }

    /* Flush RX buffer */
    uart_flush_rx(master->uart_handle);

    /* Send request */
    if (!uart_send(master->uart_handle, request, request_length)) {
        mutex_unlock(master->mutex);
        return MODBUS_STATUS_UART_ERROR;
    }

    /* Calculate expected response length (minimum) */
    uint16_t min_response_len = 5;  /* Slave + FC + CRC (2 bytes) */

    /* Wait for response */
    uint16_t rx_len = uart_receive(master->uart_handle,
                                     master->rx_buffer,
                                     sizeof(master->rx_buffer),
                                     master->timeout_ms);

    mutex_unlock(master->mutex);

    if (rx_len < min_response_len) {
        return MODBUS_STATUS_TIMEOUT;
    }

    /* Verify CRC */
    uint16_t rx_crc = (master->rx_buffer[rx_len - 1] << 8) |
                       master->rx_buffer[rx_len - 2];
    uint16_t calc_crc = modbus_crc16(master->rx_buffer, rx_len - 2);

    if (rx_crc != calc_crc) {
        return MODBUS_STATUS_CRC_ERROR;
    }

    /* Check for exception response */
    if (master->rx_buffer[1] & 0x80) {
        return MODBUS_STATUS_EXCEPTION;
    }

    /* Copy response (without CRC) */
    *response_length = rx_len - 2;
    memcpy(response, master->rx_buffer, *response_length);

    return MODBUS_STATUS_OK;
}

/* ============================================================================
 * Modbus Function: Read Holding Registers (0x03)
 * ============================================================================ */

modbus_status_t modbus_read_holding_registers(modbus_master_t *master,
                                                uint8_t slave_addr,
                                                uint16_t start_addr,
                                                uint16_t num_registers,
                                                uint16_t *values) {
    uint8_t request[8];
    uint8_t response[MODBUS_RTU_MAX_PDU_SIZE];
    uint16_t response_len;
    modbus_status_t status;

    /* Build request */
    request[0] = slave_addr;
    request[1] = MODBUS_FC_READ_HOLDING_REGISTERS;
    request[2] = (start_addr >> 8) & 0xFF;
    request[3] = start_addr & 0xFF;
    request[4] = (num_registers >> 8) & 0xFF;
    request[5] = num_registers & 0xFF;

    /* Calculate CRC */
    uint16_t crc = modbus_crc16(request, 6);
    request[6] = crc & 0xFF;
    request[7] = (crc >> 8) & 0xFF;

    /* Send request with retries */
    for (uint8_t retry = 0; retry < master->max_retries; retry++) {
        status = modbus_transaction(master, request, 8, response, &response_len);

        if (status == MODBUS_STATUS_OK) {
            /* Parse response */
            uint8_t byte_count = response[2];

            if (byte_count != num_registers * 2) {
                return MODBUS_STATUS_INVALID_LENGTH;
            }

            /* Extract register values */
            for (uint16_t i = 0; i < num_registers; i++) {
                values[i] = (response[3 + i * 2] << 8) |
                             response[4 + i * 2];
            }

            return MODBUS_STATUS_OK;
        } else if (status != MODBUS_STATUS_TIMEOUT && status != MODBUS_STATUS_CRC_ERROR) {
            /* Non-recoverable error */
            return status;
        }

        /* Delay before retry */
        extern void delay_ms(uint32_t ms);
        delay_ms(50);
    }

    return status;
}

/* ============================================================================
 * Modbus Function: Write Single Register (0x06)
 * ============================================================================ */

modbus_status_t modbus_write_single_register(modbus_master_t *master,
                                               uint8_t slave_addr,
                                               uint16_t reg_addr,
                                               uint16_t value) {
    uint8_t request[8];
    uint8_t response[MODBUS_RTU_MAX_PDU_SIZE];
    uint16_t response_len;
    modbus_status_t status;

    /* Build request */
    request[0] = slave_addr;
    request[1] = MODBUS_FC_WRITE_SINGLE_REGISTER;
    request[2] = (reg_addr >> 8) & 0xFF;
    request[3] = reg_addr & 0xFF;
    request[4] = (value >> 8) & 0xFF;
    request[5] = value & 0xFF;

    /* Calculate CRC */
    uint16_t crc = modbus_crc16(request, 6);
    request[6] = crc & 0xFF;
    request[7] = (crc >> 8) & 0xFF;

    /* Send request with retries */
    for (uint8_t retry = 0; retry < master->max_retries; retry++) {
        status = modbus_transaction(master, request, 8, response, &response_len);

        if (status == MODBUS_STATUS_OK) {
            /* Verify echo response */
            if (memcmp(request, response, 6) != 0) {
                return MODBUS_STATUS_INVALID_LENGTH;
            }

            return MODBUS_STATUS_OK;
        } else if (status != MODBUS_STATUS_TIMEOUT && status != MODBUS_STATUS_CRC_ERROR) {
            return status;
        }

        delay_ms(50);
    }

    return status;
}

/* ============================================================================
 * Modbus Function: Write Multiple Registers (0x10)
 * ============================================================================ */

modbus_status_t modbus_write_multiple_registers(modbus_master_t *master,
                                                  uint8_t slave_addr,
                                                  uint16_t start_addr,
                                                  uint16_t num_registers,
                                                  const uint16_t *values) {
    uint8_t request[MODBUS_RTU_MAX_PDU_SIZE];
    uint8_t response[MODBUS_RTU_MAX_PDU_SIZE];
    uint16_t response_len;
    modbus_status_t status;

    /* Check limits */
    if (num_registers > 123) {  /* Modbus limit */
        return MODBUS_STATUS_INVALID_LENGTH;
    }

    uint8_t byte_count = num_registers * 2;

    /* Build request */
    request[0] = slave_addr;
    request[1] = MODBUS_FC_WRITE_MULTIPLE_REGISTERS;
    request[2] = (start_addr >> 8) & 0xFF;
    request[3] = start_addr & 0xFF;
    request[4] = (num_registers >> 8) & 0xFF;
    request[5] = num_registers & 0xFF;
    request[6] = byte_count;

    /* Add register values */
    for (uint16_t i = 0; i < num_registers; i++) {
        request[7 + i * 2] = (values[i] >> 8) & 0xFF;
        request[8 + i * 2] = values[i] & 0xFF;
    }

    /* Calculate CRC */
    uint16_t request_len = 7 + byte_count;
    uint16_t crc = modbus_crc16(request, request_len);
    request[request_len] = crc & 0xFF;
    request[request_len + 1] = (crc >> 8) & 0xFF;

    /* Send request with retries */
    for (uint8_t retry = 0; retry < master->max_retries; retry++) {
        status = modbus_transaction(master, request, request_len + 2,
                                      response, &response_len);

        if (status == MODBUS_STATUS_OK) {
            /* Verify response */
            if (response_len < 6) {
                return MODBUS_STATUS_INVALID_LENGTH;
            }

            return MODBUS_STATUS_OK;
        } else if (status != MODBUS_STATUS_TIMEOUT && status != MODBUS_STATUS_CRC_ERROR) {
            return status;
        }

        delay_ms(50);
    }

    return status;
}

/* ============================================================================
 * Multi-Slave Polling
 * ============================================================================ */

typedef struct {
    uint8_t slave_addr;
    uint16_t register_addr;
    uint16_t num_registers;
    uint16_t *data_buffer;
    bool online;
    uint32_t last_poll_ms;
    uint32_t error_count;
} modbus_slave_t;

#define MAX_MODBUS_SLAVES  16

typedef struct {
    modbus_master_t *master;
    modbus_slave_t slaves[MAX_MODBUS_SLAVES];
    uint8_t num_slaves;
    uint32_t poll_interval_ms;
} modbus_polling_t;

void modbus_polling_add_slave(modbus_polling_t *polling,
                               uint8_t slave_addr,
                               uint16_t register_addr,
                               uint16_t num_registers,
                               uint16_t *data_buffer) {
    if (polling->num_slaves >= MAX_MODBUS_SLAVES) {
        return;
    }

    modbus_slave_t *slave = &polling->slaves[polling->num_slaves++];
    slave->slave_addr = slave_addr;
    slave->register_addr = register_addr;
    slave->num_registers = num_registers;
    slave->data_buffer = data_buffer;
    slave->online = false;
    slave->last_poll_ms = 0;
    slave->error_count = 0;
}

void modbus_polling_task(modbus_polling_t *polling) {
    extern uint32_t get_system_time_ms(void);

    for (;;) {
        uint32_t now_ms = get_system_time_ms();

        /* Poll each slave */
        for (uint8_t i = 0; i < polling->num_slaves; i++) {
            modbus_slave_t *slave = &polling->slaves[i];

            /* Check if it's time to poll this slave */
            if ((now_ms - slave->last_poll_ms) < polling->poll_interval_ms) {
                continue;
            }

            /* Read registers */
            modbus_status_t status = modbus_read_holding_registers(
                polling->master,
                slave->slave_addr,
                slave->register_addr,
                slave->num_registers,
                slave->data_buffer
            );

            slave->last_poll_ms = now_ms;

            if (status == MODBUS_STATUS_OK) {
                slave->online = true;
                slave->error_count = 0;
            } else {
                slave->error_count++;

                if (slave->error_count > 3) {
                    slave->online = false;
                }
            }
        }

        /* Small delay to prevent CPU hogging */
        extern void delay_ms(uint32_t ms);
        delay_ms(10);
    }
}
