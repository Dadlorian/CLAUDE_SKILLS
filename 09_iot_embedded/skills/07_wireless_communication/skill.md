# Wireless Communication - Subskill

**Expert in BLE, Wi-Fi, LoRa, Zigbee, and cellular IoT communication technologies**

---

## Expertise Overview

Specialist in wireless protocols:
- Bluetooth Low Energy (BLE 5.x, GATT/GAP, mesh)
- Wi-Fi (802.11n/ac, lwIP, provisioning, power save)
- LoRa & LoRaWAN (modulation, spreading factors, network architecture)
- Zigbee & Thread (IEEE 802.15.4, mesh networking)
- Cellular IoT (NB-IoT, LTE-M, AT commands)

---

## Core Skills

### 1. Bluetooth Low Energy

**Nordic nRF5 SDK BLE Peripheral**:
```c
#include "ble.h"
#include "ble_advdata.h"
#include "ble_srv_common.h"

#define DEVICE_NAME              "MyDevice"
#define APP_ADV_INTERVAL         300  /* 187.5ms */
#define APP_ADV_DURATION         18000 /* 180 seconds */

static uint16_t m_conn_handle = BLE_CONN_HANDLE_INVALID;

/* Advertisement data */
static void advertising_init(void) {
    ble_advdata_t advdata;
    ble_advdata_t srdata;

    memset(&advdata, 0, sizeof(advdata));
    advdata.name_type = BLE_ADVDATA_FULL_NAME;
    advdata.include_appearance = true;
    advdata.flags = BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE;

    /* Service UUID */
    ble_uuid_t adv_uuids[] = {{BLE_UUID_HEART_RATE_SERVICE, BLE_UUID_TYPE_BLE}};
    memset(&srdata, 0, sizeof(srdata));
    srdata.uuids_complete.uuid_cnt = sizeof(adv_uuids) / sizeof(adv_uuids[0]);
    srdata.uuids_complete.p_uuids = adv_uuids;

    /* Set advertising data */
    ble_advertising_advdata_update(&advdata, &srdata);
}

/* GATT Service Example: Custom Service */
#define CUSTOM_SERVICE_UUID      0x1800
#define CUSTOM_CHAR_UUID         0x2A00

static ble_uuid_t m_service_uuid;
static uint16_t m_service_handle;
static ble_gatts_char_handles_t m_char_handles;

static void custom_service_init(void) {
    ble_uuid128_t base_uuid = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                                0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};

    /* Add custom base UUID */
    sd_ble_uuid_vs_add(&base_uuid, &m_service_uuid.type);
    m_service_uuid.uuid = CUSTOM_SERVICE_UUID;

    /* Add service */
    sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY,
                              &m_service_uuid,
                              &m_service_handle);

    /* Add characteristic */
    ble_gatts_char_md_t char_md;
    memset(&char_md, 0, sizeof(char_md));
    char_md.char_props.read = 1;
    char_md.char_props.write = 1;
    char_md.char_props.notify = 1;

    ble_uuid_t char_uuid;
    char_uuid.type = m_service_uuid.type;
    char_uuid.uuid = CUSTOM_CHAR_UUID;

    ble_gatts_attr_md_t attr_md;
    memset(&attr_md, 0, sizeof(attr_md));
    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&attr_md.read_perm);
    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&attr_md.write_perm);

    ble_gatts_attr_t attr_char_value;
    memset(&attr_char_value, 0, sizeof(attr_char_value));
    attr_char_value.p_uuid = &char_uuid;
    attr_char_value.p_attr_md = &attr_md;
    attr_char_value.max_len = 20;

    sd_ble_gatts_characteristic_add(m_service_handle,
                                      &char_md,
                                      &attr_char_value,
                                      &m_char_handles);
}

/* Send notification */
static void send_notification(const uint8_t *data, uint16_t len) {
    if (m_conn_handle != BLE_CONN_HANDLE_INVALID) {
        ble_gatts_hvx_params_t hvx_params;
        memset(&hvx_params, 0, sizeof(hvx_params));

        hvx_params.handle = m_char_handles.value_handle;
        hvx_params.type = BLE_GATT_HVX_NOTIFICATION;
        hvx_params.offset = 0;
        hvx_params.p_len = &len;
        hvx_params.p_data = data;

        sd_ble_gatts_hvx(m_conn_handle, &hvx_params);
    }
}
```

### 2. Wi-Fi (ESP32)

**ESP-IDF Wi-Fi Station Mode**:
```c
#include "esp_wifi.h"
#include "esp_event.h"

#define WIFI_SSID      "MyNetwork"
#define WIFI_PASSWORD  "MyPassword"
#define WIFI_RETRY_MAX 5

static int s_retry_num = 0;

static void event_handler(void* arg, esp_event_base_t event_base,
                          int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_num < WIFI_RETRY_MAX) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGI("WiFi", "Retry connection (%d/%d)", s_retry_num, WIFI_RETRY_MAX);
        } else {
            ESP_LOGE("WiFi", "Failed to connect");
        }
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI("WiFi", "Got IP:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
    }
}

void wifi_init_sta(void) {
    /* Initialize TCP/IP stack */
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    /* Initialize Wi-Fi */
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    /* Register event handlers */
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                          ESP_EVENT_ANY_ID,
                                                          &event_handler,
                                                          NULL,
                                                          NULL));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                          IP_EVENT_STA_GOT_IP,
                                                          &event_handler,
                                                          NULL,
                                                          NULL));

    /* Configure Wi-Fi */
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASSWORD,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg = {
                .capable = true,
                .required = false
            },
        },
    };

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
}

/* Wi-Fi Power Save */
void enable_wifi_power_save(void) {
    /* Modem sleep (default) */
    esp_wifi_set_ps(WIFI_PS_MIN_MODEM);

    /* Light sleep (more power saving) */
    esp_wifi_set_ps(WIFI_PS_MAX_MODEM);
}
```

### 3. LoRa (Semtech SX1276)

**LoRa Point-to-Point**:
```c
#include "sx1276.h"

#define LORA_FREQUENCY       868000000  /* 868 MHz */
#define LORA_TX_POWER        14          /* 14 dBm */
#define LORA_BANDWIDTH       0           /* 125 kHz */
#define LORA_SPREADING_FACTOR 7
#define LORA_CODING_RATE     1           /* 4/5 */

sx1276_t lora;

void lora_init(void) {
    sx1276_create(&lora);

    sx1276_set_frequency(&lora, LORA_FREQUENCY);
    sx1276_set_tx_power(&lora, LORA_TX_POWER);
    sx1276_set_bandwidth(&lora, LORA_BANDWIDTH);
    sx1276_set_spreading_factor(&lora, LORA_SPREADING_FACTOR);
    sx1276_set_coding_rate(&lora, LORA_CODING_RATE);

    /* Set to RX mode */
    sx1276_set_opmode(&lora, SX1276_MODE_RX_CONTINUOUS);
}

void lora_send(const uint8_t *data, uint8_t len) {
    /* Switch to standby */
    sx1276_set_opmode(&lora, SX1276_MODE_STANDBY);

    /* Write payload */
    sx1276_write_buffer(&lora, 0, data, len);
    sx1276_write_reg(&lora, REG_PAYLOAD_LENGTH, len);

    /* Transmit */
    sx1276_set_opmode(&lora, SX1276_MODE_TX);

    /* Wait for TX done (interrupt-driven in production) */
    while (!(sx1276_read_reg(&lora, REG_IRQ_FLAGS) & IRQ_TX_DONE));

    /* Clear IRQ */
    sx1276_write_reg(&lora, REG_IRQ_FLAGS, IRQ_TX_DONE);

    /* Back to RX */
    sx1276_set_opmode(&lora, SX1276_MODE_RX_CONTINUOUS);
}

void lora_receive(uint8_t *data, uint8_t *len) {
    /* Check for RX done */
    uint8_t irq_flags = sx1276_read_reg(&lora, REG_IRQ_FLAGS);

    if (irq_flags & IRQ_RX_DONE) {
        /* Read payload length */
        *len = sx1276_read_reg(&lora, REG_RX_NB_BYTES);

        /* Read FIFO */
        uint8_t fifo_addr = sx1276_read_reg(&lora, REG_FIFO_RX_CURRENT_ADDR);
        sx1276_read_buffer(&lora, fifo_addr, data, *len);

        /* Clear IRQ */
        sx1276_write_reg(&lora, REG_IRQ_FLAGS, IRQ_RX_DONE);
    }
}
```

### 4. Zigbee (Z-Stack)

**Zigbee Coordinator**:
```c
#include "zstack.h"

#define DEVICE_IEEE_ADDR  0x0123456789ABCDEF

void zigbee_init_coordinator(void) {
    /* Set device type */
    zstack_setDeviceType(DEVICE_COORDINATOR);

    /* Set IEEE address */
    zstack_setIeeeAddr(DEVICE_IEEE_ADDR);

    /* Set network parameters */
    zstack_setPanId(0x1234);
    zstack_setChannel(15);

    /* Form network */
    zstack_formNetwork();

    /* Enable permit join */
    zstack_permitJoin(60);  /* 60 seconds */
}

/* Receive data */
void zigbee_data_indication(uint16_t src_addr, uint8_t *data, uint8_t len) {
    printf("Received from 0x%04X: ", src_addr);
    for (uint8_t i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

/* Send data */
void zigbee_send_data(uint16_t dst_addr, const uint8_t *data, uint8_t len) {
    zstack_afDataReq_t req;
    req.dstAddr = dst_addr;
    req.endpoint = 1;
    req.clusterId = 0x0001;
    req.dataLen = len;
    req.data = (uint8_t *)data;

    zstack_afDataRequest(&req);
}
```

### 5. Cellular IoT (NB-IoT)

**AT Command Interface**:
```c
#include "uart.h"
#include <string.h>

#define NBIOT_UART      UART1
#define APN             "iot.provider.com"

typedef enum {
    NBIOT_OK,
    NBIOT_ERROR,
    NBIOT_TIMEOUT
} nbiot_status_t;

nbiot_status_t nbiot_send_at_command(const char *cmd, char *response,
                                      uint32_t timeout_ms) {
    /* Send AT command */
    uart_send_string(NBIOT_UART, cmd);
    uart_send_string(NBIOT_UART, "\r\n");

    /* Wait for response */
    uint32_t start_time = get_tick_ms();
    size_t rx_idx = 0;

    while ((get_tick_ms() - start_time) < timeout_ms) {
        if (uart_available(NBIOT_UART)) {
            response[rx_idx++] = uart_read_byte(NBIOT_UART);

            /* Check for OK or ERROR */
            if (strstr(response, "OK")) {
                return NBIOT_OK;
            } else if (strstr(response, "ERROR")) {
                return NBIOT_ERROR;
            }
        }
    }

    return NBIOT_TIMEOUT;
}

nbiot_status_t nbiot_connect(void) {
    char response[128];

    /* Check module */
    if (nbiot_send_at_command("AT", response, 1000) != NBIOT_OK) {
        return NBIOT_ERROR;
    }

    /* Set APN */
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "AT+CGDCONT=1,\"IP\",\"%s\"", APN);
    if (nbiot_send_at_command(cmd, response, 5000) != NBIOT_OK) {
        return NBIOT_ERROR;
    }

    /* Attach to network */
    nbiot_send_at_command("AT+CGATT=1", response, 30000);

    /* Activate PDP context */
    nbiot_send_at_command("AT+CGACT=1,1", response, 10000);

    return NBIOT_OK;
}

nbiot_status_t nbiot_udp_send(const char *host, uint16_t port,
                               const uint8_t *data, size_t len) {
    char cmd[256];
    char response[128];

    /* Create socket */
    nbiot_send_at_command("AT+NSOCR=DGRAM,17,0,1", response, 5000);

    /* Send data */
    snprintf(cmd, sizeof(cmd), "AT+NSOST=0,%s,%u,%zu,", host, port, len);
    uart_send_string(NBIOT_UART, cmd);

    /* Send hex-encoded data */
    for (size_t i = 0; i < len; i++) {
        char hex[3];
        snprintf(hex, sizeof(hex), "%02X", data[i]);
        uart_send_string(NBIOT_UART, hex);
    }
    uart_send_string(NBIOT_UART, "\r\n");

    /* Wait for response */
    return nbiot_send_at_command("", response, 10000);
}
```

---

## Protocol Selection Matrix

| Protocol | Range | Data Rate | Power | Mobility | Use Case |
|----------|-------|-----------|-------|----------|----------|
| BLE      | 100m  | 1 Mbps    | Very Low | Limited | Wearables, beacons |
| Wi-Fi    | 100m  | 50+ Mbps  | Medium | Full | Home automation |
| LoRa     | 15km  | 50 kbps   | Very Low | Limited | Sensors, meters |
| Zigbee   | 100m  | 250 kbps  | Low | Mesh | Smart home |
| NB-IoT   | Wide  | 250 kbps  | Low | Full | Asset tracking |

---

## Best Practices

1. **Power Management**: Use sleep modes between transmissions
2. **Error Handling**: Implement retries with exponential backoff
3. **Security**: Enable encryption (BLE bonding, Wi-Fi WPA3, LoRaWAN encryption)
4. **Antenna Design**: Follow RF layout guidelines
5. **Certification**: Plan for FCC/CE compliance testing

---

## References

- Bluetooth SIG specifications
- ESP-IDF documentation
- Semtech LoRa design guide
- Zigbee Alliance specifications
- 3GPP NB-IoT standards

---

**Implement robust, power-efficient wireless communication with appropriate protocol selection and production-grade reliability.**
