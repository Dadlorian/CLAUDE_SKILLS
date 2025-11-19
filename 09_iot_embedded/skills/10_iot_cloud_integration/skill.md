# IoT Cloud Integration & Device Management - Subskill

**Expert in AWS IoT, Azure IoT, device provisioning, telemetry, and fleet management**

---

## Expertise Overview

Specialist in cloud IoT platforms:
- AWS IoT Core (MQTT, device shadows, rules engine)
- Azure IoT Hub (device twins, direct methods, DPS)
- Google Cloud IoT Core
- Device provisioning and lifecycle management
- Fleet-wide OTA updates and remote diagnostics
- Telemetry ingestion and time-series data

---

## Core Skills

### 1. AWS IoT Core

**MQTT Connection with X.509 Certificates**:
```c
#include "aws_iot_mqtt_client.h"
#include "aws_iot_config.h"

#define AWS_IOT_ENDPOINT     "xxxxx.iot.us-east-1.amazonaws.com"
#define AWS_IOT_ROOT_CA      "root-CA.crt"
#define AWS_IOT_CERT         "device.crt"
#define AWS_IOT_PRIVATE_KEY  "device.key"
#define THING_NAME           "my-device-001"

static AWS_IoT_Client mqtt_client;

void aws_iot_connect(void) {
    IoT_Client_Init_Params init_params = iotClientInitParamsDefault;
    IoT_Client_Connect_Params connect_params = iotClientConnectParamsDefault;

    init_params.enableAutoReconnect = true;
    init_params.pHostURL = AWS_IOT_ENDPOINT;
    init_params.port = 8883;
    init_params.pRootCALocation = AWS_IOT_ROOT_CA;
    init_params.pDeviceCertLocation = AWS_IOT_CERT;
    init_params.pDevicePrivateKeyLocation = AWS_IOT_PRIVATE_KEY;
    init_params.mqttCommandTimeout_ms = 20000;
    init_params.tlsHandshakeTimeout_ms = 5000;
    init_params.disconnectHandler = disconnect_callback;

    aws_iot_mqtt_init(&mqtt_client, &init_params);

    connect_params.keepAliveIntervalInSec = 60;
    connect_params.isCleanSession = true;
    connect_params.MQTTVersion = MQTT_3_1_1;
    connect_params.pClientID = THING_NAME;
    connect_params.clientIDLen = strlen(THING_NAME);

    IoT_Error_t rc = aws_iot_mqtt_connect(&mqtt_client, &connect_params);

    if (SUCCESS != rc) {
        ESP_LOGE("AWS", "Failed to connect: %d", rc);
    }
}

/* Publish telemetry */
void aws_iot_publish_telemetry(float temperature, float humidity) {
    char payload[128];
    IoT_Publish_Message_Params params;

    snprintf(payload, sizeof(payload),
             "{\"temperature\":%.2f,\"humidity\":%.2f,\"timestamp\":%lu}",
             temperature, humidity, time(NULL));

    params.qos = QOS1;
    params.payload = payload;
    params.payloadLen = strlen(payload);
    params.isRetained = 0;

    char topic[64];
    snprintf(topic, sizeof(topic), "devices/%s/telemetry", THING_NAME);

    aws_iot_mqtt_publish(&mqtt_client, topic, strlen(topic), &params);
}

/* Subscribe to commands */
void command_callback(AWS_IoT_Client *pClient, char *topicName,
                       uint16_t topicNameLen, IoT_Publish_Message_Params *params,
                       void *pData) {
    char *payload = (char *)params->payload;
    printf("Command received: %.*s\n", params->payloadLen, payload);

    /* Parse and execute command */
    handle_cloud_command(payload, params->payloadLen);
}

void aws_iot_subscribe_commands(void) {
    char topic[64];
    snprintf(topic, sizeof(topic), "devices/%s/commands", THING_NAME);

    aws_iot_mqtt_subscribe(&mqtt_client, topic, strlen(topic),
                            QOS1, command_callback, NULL);
}
```

**Device Shadow**:
```c
#include "aws_iot_shadow_interface.h"

static char shadow_rx_buffer[200];
static char shadow_tx_buffer[200];

/* Shadow update callback */
void shadow_update_callback(const char *pThingName, ShadowActions_t action,
                             Shadow_Ack_Status_t status, const char *pReceivedJsonDocument,
                             void *pContextData) {
    if (status == SHADOW_ACK_TIMEOUT) {
        ESP_LOGW("Shadow", "Update timeout");
    } else if (status == SHADOW_ACK_REJECTED) {
        ESP_LOGE("Shadow", "Update rejected");
    } else if (status == SHADOW_ACK_ACCEPTED) {
        ESP_LOGI("Shadow", "Update accepted");
    }
}

/* Update device shadow */
void aws_iot_update_shadow(int battery_level, bool connected) {
    char json_document[200];

    snprintf(json_document, sizeof(json_document),
             "{\"state\":{\"reported\":{\"battery\":%d,\"connected\":%s}}}",
             battery_level, connected ? "true" : "false");

    IoT_Error_t rc = aws_iot_shadow_update(&mqtt_client, THING_NAME,
                                             json_document, shadow_update_callback,
                                             NULL, 4, true);

    if (SUCCESS != rc) {
        ESP_LOGE("Shadow", "Update failed: %d", rc);
    }
}

/* Delta callback (desired vs reported state) */
void shadow_delta_callback(const char *pJsonString, uint32_t JsonStringDataLen,
                            jsonStruct_t *pContext) {
    ESP_LOGI("Shadow", "Delta: %.*s", JsonStringDataLen, pJsonString);

    /* Parse desired state and apply */
    /* Example: {"state":{"led":true}} */
    if (strstr(pJsonString, "\"led\":true")) {
        gpio_set_led(true);
        /* Update reported state */
        aws_iot_update_shadow(battery_level, true);
    }
}

void aws_iot_register_delta(void) {
    jsonStruct_t delta_handler;
    delta_handler.cb = shadow_delta_callback;
    delta_handler.pKey = "state";

    aws_iot_shadow_register_delta(&mqtt_client, &delta_handler);
}
```

### 2. Azure IoT Hub

**Device Provisioning Service (DPS)**:
```c
#include "azure_iot_hub_client.h"
#include "azure_iot_dps_client.h"

#define DPS_SCOPE_ID      "0ne0012ABCD"
#define DPS_REGISTRATION_ID "my-device-001"
#define DPS_SYMMETRIC_KEY   "xxx...xxx"

static IOTHUB_DEVICE_CLIENT_HANDLE device_handle = NULL;

/* DPS registration callback */
static void dps_register_callback(PROV_DEVICE_RESULT register_result,
                                    const char* iothub_uri,
                                    const char* device_id,
                                    void* user_context) {
    if (register_result == PROV_DEVICE_RESULT_OK) {
        printf("Assigned to IoT Hub: %s\n", iothub_uri);
        printf("Device ID: %s\n", device_id);

        /* Connect to assigned IoT Hub */
        device_handle = IoTHubDeviceClient_CreateFromConnectionString(
            connection_string, MQTT_Protocol);
    }
}

void azure_dps_provision(void) {
    PROV_DEVICE_HANDLE prov_handle;
    PROV_DEVICE_LL_HANDLE prov_ll_handle;

    /* Initialize DPS */
    prov_ll_handle = Prov_Device_LL_Create(DPS_SCOPE_ID,
                                             DPS_REGISTRATION_ID,
                                             Prov_Device_MQTT_Protocol);

    /* Set symmetric key */
    Prov_Device_LL_SetOption(prov_ll_handle, PROV_OPTION_SYMMETRIC_KEY,
                               DPS_SYMMETRIC_KEY);

    /* Register device */
    Prov_Device_LL_Register_Device(prov_ll_handle, dps_register_callback,
                                     NULL, NULL, NULL);

    /* Wait for registration */
    do {
        Prov_Device_LL_DoWork(prov_ll_handle);
        delay_ms(100);
    } while (!device_handle);

    Prov_Device_LL_Destroy(prov_ll_handle);
}
```

**Send Telemetry**:
```c
#include "iothub_client_options.h"
#include "iothub_message.h"

void azure_send_telemetry(float temperature, float humidity) {
    char msg_text[128];
    snprintf(msg_text, sizeof(msg_text),
             "{\"temperature\":%.2f,\"humidity\":%.2f}", temperature, humidity);

    IOTHUB_MESSAGE_HANDLE message_handle = IoTHubMessage_CreateFromString(msg_text);

    /* Add properties */
    IoTHubMessage_SetContentTypeSystemProperty(message_handle, "application/json");
    IoTHubMessage_SetContentEncodingSystemProperty(message_handle, "utf-8");

    /* Send message */
    IoTHubDeviceClient_SendEventAsync(device_handle, message_handle,
                                       send_confirm_callback, NULL);

    IoTHubMessage_Destroy(message_handle);
}

static void send_confirm_callback(IOTHUB_CLIENT_CONFIRMATION_RESULT result,
                                    void* userContextCallback) {
    if (result == IOTHUB_CLIENT_CONFIRMATION_OK) {
        ESP_LOGI("Azure", "Message confirmed");
    } else {
        ESP_LOGE("Azure", "Send failed: %d", result);
    }
}
```

**Device Twin**:
```c
/* Device twin desired properties callback */
static void device_twin_callback(DEVICE_TWIN_UPDATE_STATE update_state,
                                   const unsigned char* payload, size_t size,
                                   void* userContextCallback) {
    printf("Twin update: %.*s\n", (int)size, payload);

    /* Parse JSON and update device */
    /* Example: {"desired":{"telemetryInterval":10}} */
}

void azure_register_device_twin(void) {
    IoTHubDeviceClient_SetDeviceTwinCallback(device_handle,
                                               device_twin_callback, NULL);
}

/* Report device twin properties */
void azure_report_twin_properties(int battery_level) {
    char reported[64];
    snprintf(reported, sizeof(reported),
             "{\"batteryLevel\":%d}", battery_level);

    IoTHubDeviceClient_SendReportedState(device_handle,
                                          (unsigned char*)reported,
                                          strlen(reported),
                                          NULL, NULL);
}
```

**Direct Methods**:
```c
/* Direct method callback */
static int device_method_callback(const char* method_name,
                                   const unsigned char* payload, size_t size,
                                   unsigned char** response, size_t* response_size,
                                   void* userContextCallback) {
    printf("Method: %s, Payload: %.*s\n", method_name, (int)size, payload);

    int status = 200;
    const char *response_msg = "{\"status\":\"OK\"}";

    if (strcmp(method_name, "reboot") == 0) {
        /* Schedule reboot */
        schedule_system_reboot();
    } else if (strcmp(method_name, "setLed") == 0) {
        /* Parse payload and set LED */
        bool led_state = (strstr((char*)payload, "\"on\":true") != NULL);
        gpio_set_led(led_state);
    } else {
        status = 404;
        response_msg = "{\"error\":\"Method not found\"}";
    }

    *response_size = strlen(response_msg);
    *response = (unsigned char*)malloc(*response_size);
    memcpy(*response, response_msg, *response_size);

    return status;
}

void azure_register_direct_methods(void) {
    IoTHubDeviceClient_SetDeviceMethodCallback(device_handle,
                                                 device_method_callback, NULL);
}
```

### 3. OTA Firmware Updates

**Fleet-Wide OTA (AWS IoT Jobs)**:
```c
#include "aws_iot_jobs_interface.h"

#define JOB_TOPIC_PREFIX  "$aws/things/"THING_NAME"/jobs"

void ota_job_callback(AWS_IoT_Client *pClient, char *topicName,
                       uint16_t topicNameLen, IoT_Publish_Message_Params *params,
                       void *pData) {
    /* Parse job document */
    /* Example: {"operation":"install","version":"1.2.3","url":"https://..."} */

    /* Download firmware */
    download_firmware_from_url(firmware_url);

    /* Verify signature */
    if (!verify_firmware_signature()) {
        report_job_status("FAILED", "Signature verification failed");
        return;
    }

    /* Install firmware */
    install_firmware();

    /* Report success */
    report_job_status("SUCCEEDED", "Firmware updated to v1.2.3");

    /* Reboot */
    NVIC_SystemReset();
}

void aws_iot_subscribe_jobs(void) {
    char job_notify_topic[128];
    snprintf(job_notify_topic, sizeof(job_notify_topic),
             "%s/notify-next", JOB_TOPIC_PREFIX);

    aws_iot_mqtt_subscribe(&mqtt_client, job_notify_topic,
                            strlen(job_notify_topic), QOS1,
                            ota_job_callback, NULL);
}
```

---

## Best Practices

1. **Certificate Management**: Rotate X.509 certificates regularly
2. **Retry Logic**: Implement exponential backoff for reconnects
3. **Batching**: Aggregate telemetry to reduce messages
4. **Compression**: Use GZIP for large payloads
5. **Monitoring**: Track connection uptime and message delivery
6. **Security**: Use TLS 1.2+, mutual authentication

---

## Cloud Platform Comparison

| Feature          | AWS IoT Core | Azure IoT Hub | Google Cloud IoT |
|------------------|--------------|---------------|------------------|
| Protocol         | MQTT, HTTPS  | MQTT, AMQP, HTTPS | MQTT, HTTPS |
| Device Registry  | Thing Registry | Device Registry | Device Registry |
| State Sync       | Device Shadow | Device Twin | Device State |
| OTA              | IoT Jobs | Device Update | Cloud IoT |
| Pricing Model    | Message-based | Message-based | Data volume |

---

## References

- AWS IoT Developer Guide
- Azure IoT Hub documentation
- Google Cloud IoT Core guides
- MQTT v5.0 specification

---

---

## Advanced Cloud Integration Patterns

### Device Lifecycle Management
```c
/* Complete device lifecycle: provisioning -> operation -> decommissioning */
typedef enum {
    DEVICE_STATE_UNPROVISIONED,
    DEVICE_STATE_PROVISIONING,
    DEVICE_STATE_ACTIVE,
    DEVICE_STATE_MAINTENANCE,
    DEVICE_STATE_RETIRED
} device_state_t;

typedef struct {
    char device_id[64];
    device_state_t state;
    uint32_t provisioned_timestamp;
    uint32_t last_heartbeat;
    uint32_t firmware_version;
} device_lifecycle_t;

status_t provision_device_to_cloud(device_lifecycle_t *device,
                                    const char *api_key,
                                    const char *provisioning_code) {
    device->state = DEVICE_STATE_PROVISIONING;

    /* Register device with cloud backend */
    status_t status = cloud_api_register_device(device->device_id,
                                                api_key,
                                                provisioning_code);

    if (status == STATUS_OK) {
        device->state = DEVICE_STATE_ACTIVE;
        device->provisioned_timestamp = get_time_s();
        return STATUS_OK;
    } else {
        device->state = DEVICE_STATE_UNPROVISIONED;
        return STATUS_ERROR;
    }
}

void send_device_heartbeat(device_lifecycle_t *device,
                           cloud_client_t *client) {
    char heartbeat[256];
    snprintf(heartbeat, sizeof(heartbeat),
             "{\"deviceId\":\"%s\",\"state\":%d,\"uptime\":%lu,\"fwVersion\":%u}",
             device->device_id, device->state,
             get_time_s() - device->provisioned_timestamp,
             device->firmware_version);

    cloud_send_message(client, "devices/heartbeat", heartbeat);
    device->last_heartbeat = get_time_s();
}
```

### Offline Queue & Sync
```c
/* Queue messages when offline, sync when reconnected */
#define MAX_OFFLINE_MESSAGES 100

typedef struct {
    char topic[64];
    char payload[256];
    uint32_t timestamp;
    bool synced;
} queued_message_t;

typedef struct {
    queued_message_t messages[MAX_OFFLINE_MESSAGES];
    uint32_t queue_head;
    uint32_t queue_tail;
    uint32_t message_count;
    bool is_online;
} offline_queue_t;

status_t enqueue_message(offline_queue_t *queue, const char *topic,
                        const char *payload) {
    if (queue->message_count >= MAX_OFFLINE_MESSAGES) {
        return STATUS_ERROR;  /* Queue full */
    }

    queued_message_t *msg = &queue->messages[queue->queue_tail];
    strncpy(msg->topic, topic, sizeof(msg->topic) - 1);
    strncpy(msg->payload, payload, sizeof(msg->payload) - 1);
    msg->timestamp = get_time_s();
    msg->synced = false;

    queue->queue_tail = (queue->queue_tail + 1) % MAX_OFFLINE_MESSAGES;
    queue->message_count++;

    return STATUS_OK;
}

void sync_offline_messages(offline_queue_t *queue,
                          cloud_client_t *client) {
    uint32_t synced_count = 0;

    while (queue->message_count > 0 && synced_count < 10) {
        queued_message_t *msg = &queue->messages[queue->queue_head];

        /* Attempt to send */
        if (cloud_send_message(client, msg->topic, msg->payload) == STATUS_OK) {
            msg->synced = true;
            queue->queue_head = (queue->queue_head + 1) % MAX_OFFLINE_MESSAGES;
            queue->message_count--;
            synced_count++;
        } else {
            break;  /* Stop on first failure */
        }
    }

    if (synced_count > 0) {
        printf("Synced %u offline messages\n", synced_count);
    }
}
```

---

## Fleet Management & Analytics

### Device Group Management
```c
typedef enum {
    DEPLOYMENT_STABLE,
    DEPLOYMENT_BETA,
    DEPLOYMENT_CANARY
} deployment_track_t;

typedef struct {
    char group_id[32];
    deployment_track_t track;
    char firmware_version[16];
    uint32_t device_count;
    float error_rate;
} device_group_t;

/* Canary deployment: gradual rollout to detect issues */
status_t deploy_firmware_canary(const device_group_t *group,
                                const char *new_firmware_url,
                                uint8_t canary_percentage) {
    uint32_t canary_count = (group->device_count * canary_percentage) / 100;

    printf("Starting canary deployment: %u/%u devices (%.0f%%)\n",
           canary_count, group->device_count, (float)canary_percentage);

    /* Deploy to subset of devices */
    for (uint32_t i = 0; i < canary_count; i++) {
        char device_id[64];
        get_device_in_group(group->group_id, i, device_id);

        /* Create OTA job for this device */
        create_ota_job(device_id, new_firmware_url, "canary");
    }

    /* Monitor canary devices for errors */
    sleep_s(60);  /* Wait for deployment

*/
    float canary_error_rate = get_group_error_rate(group->group_id, "canary");

    if (canary_error_rate > 5.0f) {  /* >5% error rate */
        printf("Canary failed - aborting rollout\n");
        return STATUS_ERROR;
    }

    printf("Canary successful - proceeding with full rollout\n");
    return STATUS_OK;
}
```

### Telemetry Aggregation & Storage
```c
/* Efficient telemetry with compression */
typedef struct {
    uint16_t temperature;      /* Celsius * 100 */
    uint16_t humidity;         /* RH * 100 */
    uint32_t timestamp;        /* Unix timestamp */
    uint8_t flags;             /* Status flags */
} compact_telemetry_t;

/* Batch telemetry for efficiency */
typedef struct {
    compact_telemetry_t readings[60];  /* 1 hour @ 1 min intervals */
    uint32_t count;
    uint32_t batch_size;
} telemetry_batch_t;

void send_telemetry_batch(telemetry_batch_t *batch,
                         cloud_client_t *client) {
    /* Create compact JSON representation */
    char buffer[512];
    int pos = 0;

    pos += snprintf(&buffer[pos], sizeof(buffer) - pos, "{\"readings\":[");

    for (uint32_t i = 0; i < batch->count; i++) {
        compact_telemetry_t *r = &batch->readings[i];

        pos += snprintf(&buffer[pos], sizeof(buffer) - pos,
                       "{\"t\":%u,\"temp\":%.2f,\"hum\":%.2f}%s",
                       r->timestamp,
                       r->temperature / 100.0f,
                       r->humidity / 100.0f,
                       i < batch->count - 1 ? "," : "");
    }

    pos += snprintf(&buffer[pos], sizeof(buffer) - pos, "]}");

    cloud_send_message(client, "telemetry/batch", buffer);
    batch->count = 0;  /* Reset batch */
}
```

---

## Edge-to-Cloud Synchronization

### Bi-Directional Configuration Sync
```c
/* Device config managed in cloud, synced to device */
typedef struct {
    uint32_t sample_interval_ms;
    uint32_t report_interval_s;
    bool enable_local_processing;
    float anomaly_threshold;
    uint32_t config_version;
} device_config_t;

/* Configuration change callback from cloud */
void on_config_change(const char *config_json,
                      device_config_t *config) {
    /* Parse new configuration */
    uint32_t sample_interval = json_get_int(config_json, "sampleInterval");
    uint32_t report_interval = json_get_int(config_json, "reportInterval");
    float threshold = json_get_float(config_json, "anomalyThreshold");

    /* Validate changes */
    if (sample_interval < 100 || sample_interval > 60000) {
        log_error("Invalid sample interval");
        return;
    }

    /* Apply configuration */
    config->sample_interval_ms = sample_interval;
    config->report_interval_s = report_interval;
    config->anomaly_threshold = threshold;
    config->config_version = json_get_int(config_json, "version");

    /* Persist to flash for recovery */
    save_config_to_flash(config);

    printf("Configuration updated to v%u\n", config->config_version);
}

void confirm_config_change(cloud_client_t *client,
                          const device_config_t *config) {
    char message[128];
    snprintf(message, sizeof(message),
             "{\"configVersion\":%u,\"status\":\"applied\"}",
             config->config_version);

    cloud_send_message(client, "device/config/ack", message);
}
```

### Two-Way Firmware Updates with Rollback
```c
typedef struct {
    char current_version[16];
    char previous_version[16];
    uint32_t update_timestamp;
    bool rollback_available;
} firmware_state_t;

status_t install_and_verify_firmware(const uint8_t *firmware_data,
                                     size_t fw_size,
                                     firmware_state_t *fw_state) {
    /* Backup current firmware */
    if (save_firmware_backup(fw_state->current_version) != STATUS_OK) {
        return STATUS_ERROR;
    }

    /* Install new firmware */
    if (flash_write_firmware(firmware_data, fw_size) != STATUS_OK) {
        restore_firmware_from_backup();
        return STATUS_ERROR;
    }

    /* Verify integrity (checksum/signature) */
    uint8_t expected_hash[32], actual_hash[32];
    calculate_firmware_hash(firmware_data, fw_size, actual_hash);
    extract_expected_hash(firmware_data, expected_hash);

    if (memcmp(expected_hash, actual_hash, 32) != 0) {
        log_error("Firmware verification failed");
        restore_firmware_from_backup();
        return STATUS_ERROR;
    }

    /* Firmware valid - update state */
    strcpy(fw_state->previous_version, fw_state->current_version);
    extract_version_from_firmware(firmware_data, fw_state->current_version);
    fw_state->update_timestamp = get_time_s();
    fw_state->rollback_available = true;

    return STATUS_OK;
}

status_t rollback_firmware(firmware_state_t *fw_state) {
    if (!fw_state->rollback_available) {
        return STATUS_ERROR;
    }

    if (restore_firmware_from_backup() != STATUS_OK) {
        return STATUS_ERROR;
    }

    strcpy(fw_state->current_version, fw_state->previous_version);
    fw_state->rollback_available = false;

    return STATUS_OK;
}
```

---

**Build scalable, secure IoT cloud integrations with automated provisioning, fleet management, and real-time telemetry.**
