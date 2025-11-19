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

**Build scalable, secure IoT cloud integrations with automated provisioning, fleet management, and real-time telemetry.**
