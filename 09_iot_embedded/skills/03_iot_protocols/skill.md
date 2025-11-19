# IoT Protocols & Communication - Subskill

**Expert-level knowledge of MQTT, CoAP, LoRaWAN, and IoT application-layer protocols**

---

## Expertise Overview

Specialist in IoT communication protocols:
- MQTT (v3.1.1, v5.0) with QoS levels, retained messages, last will
- CoAP (Constrained Application Protocol) for resource-constrained devices
- LoRaWAN (classes A/B/C, ADR, regional parameters)
- AMQP, DDS, LwM2M for device management
- Protocol selection based on bandwidth, latency, power, and reliability constraints

---

## Core Skills

### 1. MQTT Implementation

**MQTT Client (Paho Embedded C)**:
```c
#include "MQTTClient.h"

#define BROKER_ADDRESS    "tcp://mqtt.example.com:1883"
#define CLIENT_ID         "device_001"
#define TOPIC_TELEMETRY   "devices/device_001/telemetry"
#define QOS               1

static MQTTClient client;

typedef struct {
    uint16_t temperature;
    uint16_t humidity;
    uint32_t timestamp;
} telemetry_t;

status_t mqtt_connect(void) {
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    conn_opts.keepAliveInterval = 60;
    conn_opts.cleansession = 1;
    conn_opts.username = "device_001";
    conn_opts.password = "secret_key";

    /* Last Will Testament */
    MQTTClient_willOptions will_opts = MQTTClient_willOptions_initializer;
    will_opts.topicName = "devices/device_001/status";
    will_opts.message = "offline";
    will_opts.qos = 1;
    will_opts.retained = 1;
    conn_opts.will = &will_opts;

    int rc = MQTTClient_connect(client, &conn_opts);
    return (MQTTCLIENT_SUCCESS == rc) ? STATUS_OK : STATUS_ERROR;
}

status_t mqtt_publish_telemetry(const telemetry_t *data) {
    char payload[128];
    snprintf(payload, sizeof(payload),
             "{\"temp\":%u,\"humidity\":%u,\"ts\":%lu}",
             data->temperature, data->humidity, data->timestamp);

    MQTTClient_message msg = MQTTClient_message_initializer;
    msg.payload = payload;
    msg.payloadlen = strlen(payload);
    msg.qos = QOS;
    msg.retained = 0;

    MQTTClient_deliveryToken token;
    int rc = MQTTClient_publishMessage(client, TOPIC_TELEMETRY, &msg, &token);

    if (MQTTCLIENT_SUCCESS != rc) {
        return STATUS_ERROR;
    }

    /* Wait for delivery (QoS 1) */
    rc = MQTTClient_waitForCompletion(client, token, 1000);
    return (MQTTCLIENT_SUCCESS == rc) ? STATUS_OK : STATUS_TIMEOUT;
}

/* Message arrived callback */
int message_arrived(void *context, char *topic, int topic_len,
                    MQTTClient_message *message) {
    printf("Message arrived on topic %s: %.*s\n",
           topic, message->payloadlen, (char*)message->payload);

    MQTTClient_freeMessage(&message);
    MQTTClient_free(topic);
    return 1;
}
```

### 2. CoAP Implementation

**libcoap Example**:
```c
#include "coap3/coap.h"

#define COAP_SERVER_URI "coap://[::1]:5683/temperature"

/* CoAP GET request */
status_t coap_get_temperature(int16_t *temperature) {
    coap_context_t *ctx = NULL;
    coap_session_t *session = NULL;
    coap_pdu_t *pdu = NULL;
    coap_address_t dst;
    status_t result = STATUS_ERROR;

    /* Initialize CoAP context */
    ctx = coap_new_context(NULL);
    if (!ctx) {
        return STATUS_ERROR;
    }

    /* Parse server address */
    coap_address_init(&dst);
    dst.addr.sin6.sin6_family = AF_INET6;
    dst.addr.sin6.sin6_port = htons(5683);

    /* Create session */
    session = coap_new_client_session(ctx, NULL, &dst, COAP_PROTO_UDP);
    if (!session) {
        goto cleanup;
    }

    /* Build GET request */
    pdu = coap_new_pdu(COAP_MESSAGE_CON, COAP_REQUEST_GET, session);
    if (!pdu) {
        goto cleanup;
    }

    /* Add options */
    coap_add_option(pdu, COAP_OPTION_URI_PATH,
                    11, (const uint8_t *)"temperature");

    /* Register response handler */
    coap_register_response_handler(ctx, response_handler);

    /* Send request */
    coap_send(session, pdu);

    /* Wait for response */
    coap_io_process(ctx, 5000);  /* 5 second timeout */

    result = STATUS_OK;

cleanup:
    coap_session_release(session);
    coap_free_context(ctx);
    return result;
}

/* CoAP response handler */
static void response_handler(coap_session_t *session,
                             const coap_pdu_t *sent,
                             const coap_pdu_t *received,
                             const coap_mid_t mid) {
    size_t len;
    const uint8_t *data;

    if (coap_get_data(received, &len, &data)) {
        printf("Received: %.*s\n", (int)len, data);
        /* Parse temperature from payload */
    }
}

/* CoAP POST with confirmable message */
status_t coap_post_sensor_data(uint16_t sensor_id, int16_t value) {
    coap_pdu_t *pdu = coap_new_pdu(COAP_MESSAGE_CON, COAP_REQUEST_POST, session);

    /* Add URI path */
    coap_add_option(pdu, COAP_OPTION_URI_PATH, 6, (const uint8_t *)"sensor");

    /* Add content format (application/json) */
    uint8_t content_format = COAP_MEDIATYPE_APPLICATION_JSON;
    coap_add_option(pdu, COAP_OPTION_CONTENT_FORMAT, 1, &content_format);

    /* Add payload */
    char payload[64];
    int len = snprintf(payload, sizeof(payload),
                       "{\"id\":%u,\"value\":%d}", sensor_id, value);
    coap_add_data(pdu, len, (const uint8_t *)payload);

    /* Send */
    return coap_send(session, pdu) != COAP_INVALID_MID ?
           STATUS_OK : STATUS_ERROR;
}
```

### 3. LoRaWAN Implementation

**LoRaMac-node Stack**:
```c
#include "LoRaMac.h"
#include "Commissioning.h"

/* LoRaWAN parameters */
static uint8_t DevEui[] = LORAWAN_DEVICE_EUI;
static uint8_t AppEui[] = LORAWAN_APPLICATION_EUI;
static uint8_t AppKey[] = LORAWAN_APPLICATION_KEY;

static LoRaMacPrimitives_t LoRaMacPrimitives;
static LoRaMacCallback_t LoRaMacCallbacks;

void lorawan_init(void) {
    /* Initialize MAC primitives */
    LoRaMacPrimitives.MacMcpsConfirm = McpsConfirm;
    LoRaMacPrimitives.MacMcpsIndication = McpsIndication;
    LoRaMacPrimitives.MacMlmeConfirm = MlmeConfirm;
    LoRaMacPrimitives.MacMlmeIndication = MlmeIndication;

    /* Initialize LoRaMac */
    LoRaMacStatus_t status = LoRaMacInitialization(
        &LoRaMacPrimitives,
        &LoRaMacCallbacks,
        LORAMAC_REGION_EU868
    );

    if (LORAMAC_STATUS_OK != status) {
        /* Handle error */
        return;
    }

    /* Set device parameters */
    MibRequestConfirm_t mibReq;

    mibReq.Type = MIB_DEV_EUI;
    mibReq.Param.DevEui = DevEui;
    LoRaMacMibSetRequestConfirm(&mibReq);

    mibReq.Type = MIB_APP_EUI;
    mibReq.Param.AppEui = AppEui;
    LoRaMacMibSetRequestConfirm(&mibReq);

    mibReq.Type = MIB_APP_KEY;
    mibReq.Param.AppKey = AppKey;
    LoRaMacMibSetRequestConfirm(&mibReq);

    /* Enable Adaptive Data Rate */
    mibReq.Type = MIB_ADR;
    mibReq.Param.AdrEnable = true;
    LoRaMacMibSetRequestConfirm(&mibReq);
}

/* OTAA Join */
void lorawan_join(void) {
    MlmeReq_t mlmeReq;
    mlmeReq.Type = MLME_JOIN;
    mlmeReq.Req.Join.DevEui = DevEui;
    mlmeReq.Req.Join.AppEui = AppEui;
    mlmeReq.Req.Join.AppKey = AppKey;
    mlmeReq.Req.Join.NbTrials = 3;

    LoRaMacMlmeRequest(&mlmeReq);
}

/* Send unconfirmed uplink */
status_t lorawan_send(uint8_t port, const uint8_t *data, uint8_t len) {
    McpsReq_t mcpsReq;
    LoRaMacTxInfo_t txInfo;

    /* Check payload size */
    if (LoRaMacQueryTxPossible(len, &txInfo) != LORAMAC_STATUS_OK) {
        return STATUS_ERROR;
    }

    /* Prepare uplink */
    mcpsReq.Type = MCPS_UNCONFIRMED;
    mcpsReq.Req.Unconfirmed.fPort = port;
    mcpsReq.Req.Unconfirmed.fBuffer = (uint8_t *)data;
    mcpsReq.Req.Unconfirmed.fBufferSize = len;
    mcpsReq.Req.Unconfirmed.Datarate = DR_0;  /* Or use ADR */

    LoRaMacStatus_t status = LoRaMacMcpsRequest(&mcpsReq);
    return (LORAMAC_STATUS_OK == status) ? STATUS_OK : STATUS_ERROR;
}

/* Callbacks */
static void McpsConfirm(McpsConfirm_t *mcpsConfirm) {
    if (mcpsConfirm->Status == LORAMAC_EVENT_INFO_STATUS_OK) {
        /* Transmission successful */
        switch (mcpsConfirm->McpsRequest) {
            case MCPS_UNCONFIRMED:
                /* Unconfirmed frame sent */
                break;

            case MCPS_CONFIRMED:
                /* Confirmed frame sent, ACK received */
                break;

            default:
                break;
        }
    }
}

static void McpsIndication(McpsIndication_t *mcpsIndication) {
    if (mcpsIndication->Status == LORAMAC_EVENT_INFO_STATUS_OK) {
        /* Downlink received */
        printf("Received on port %d: ", mcpsIndication->Port);
        for (uint8_t i = 0; i < mcpsIndication->BufferSize; i++) {
            printf("%02X ", mcpsIndication->Buffer[i]);
        }
        printf("\n");
    }
}
```

---

## Protocol Selection Guide

| Protocol | Bandwidth | Range | Power | Latency | Use Case |
|----------|-----------|-------|-------|---------|----------|
| MQTT     | High      | LAN/WAN | Medium | Low  | Cloud IoT, telemetry |
| CoAP     | Low-Med   | LAN/WAN | Low    | Low  | Constrained devices |
| LoRaWAN  | Very Low  | 2-15km | Very Low | High | Sensors, meters |
| BLE      | Medium    | 10-100m | Very Low | Low | Wearables, beacons |
| NB-IoT   | Low       | Cellular| Low    | Medium | Asset tracking |

---

## Best Practices

**MQTT**:
- Use QoS 1 for reliable delivery
- Implement reconnection with exponential backoff
- Set appropriate keep-alive interval (60s typical)
- Use Last Will Testament for device status

**CoAP**:
- Use confirmable messages for critical data
- Implement observe pattern for continuous updates
- Use block-wise transfer for large payloads
- Leverage DTLS for security

**LoRaWAN**:
- Enable ADR for optimal data rate
- Use Class A for battery-powered sensors
- Limit uplink frequency (duty cycle regulations)
- Implement downlink processing for configuration

---

## References

- OASIS MQTT v5.0 Specification
- IETF RFC 7252 (CoAP)
- LoRa Alliance LoRaWAN Specification v1.0.4
- Eclipse Paho MQTT libraries

---

---

## Protocol Comparison & Selection Criteria

### MQTT vs CoAP vs LoRaWAN Detailed

**MQTT (Message Queuing Telemetry Transport)**:
- Architecture: Publish/Subscribe with broker
- QoS Levels: 0 (at-most-once), 1 (at-least-once), 2 (exactly-once)
- Use Case: Cloud connectivity, frequent updates, reliable networks
- Bandwidth: ~2-3 bytes overhead per message
- Latency: 10-100ms typical
- Security: TLS/SSL support, username/password, client certificates

**CoAP (Constrained Application Protocol)**:
- Architecture: Request/Response with optional proxy
- Message Types: Confirmable (CON), Non-confirmable (NON)
- Use Case: IoT devices, resource-constrained environments
- Bandwidth: <20 bytes overhead
- Latency: <100ms with retries
- Security: DTLS (UDP-based TLS)

**LoRaWAN**:
- Architecture: Gateway-based, server-managed
- Classes: A (battery), B (scheduled), C (always-on)
- Use Case: Long-range sensors, meters, asset tracking
- Bandwidth: 50-5600 bps depending on SF
- Range: 2-15km line-of-sight
- Security: AES-128 at application and network layers

---

## Advanced Implementation Patterns

### MQTT Topic Hierarchies
```c
/* Recommended topic structure */
#define TELEMETRY_TOPIC      "devices/%s/telemetry"
#define COMMAND_TOPIC        "devices/%s/commands"
#define STATUS_TOPIC         "devices/%s/status"
#define FIRMWARE_TOPIC       "devices/%s/firmware"

/* Structured device identification */
typedef struct {
    char device_id[32];
    char organization[32];
    char site[32];
    char asset_type[32];
} device_identifier_t;

void build_topic(char *buffer, size_t len,
                 const char *topic_fmt,
                 const device_identifier_t *dev) {
    snprintf(buffer, len, topic_fmt, dev->device_id);
}
```

### CoAP Observe Pattern (Server Push)
```c
/* CoAP Observe request header */
#define COAP_OBSERVE_DEREGISTER   1
#define COAP_OBSERVE_REGISTER     0

status_t coap_observe_sensor(coap_session_t *session,
                              const char *resource_path) {
    coap_pdu_t *pdu = coap_new_pdu(COAP_MESSAGE_CON,
                                    COAP_REQUEST_GET, session);

    /* Add Observe option to register for updates */
    coap_add_option(pdu, COAP_OPTION_OBSERVE,
                    1, (const uint8_t *)&COAP_OBSERVE_REGISTER);

    coap_add_option(pdu, COAP_OPTION_URI_PATH,
                    strlen(resource_path),
                    (const uint8_t *)resource_path);

    return coap_send(session, pdu) != COAP_INVALID_MID ?
           STATUS_OK : STATUS_ERROR;
}
```

### Connection Management & Retries
```c
typedef struct {
    uint32_t retry_count;
    uint32_t backoff_ms;
    uint32_t max_backoff_ms;
    uint32_t max_retries;
} retry_config_t;

status_t connect_with_exponential_backoff(mqtt_client_t *client,
                                          const retry_config_t *config) {
    uint32_t backoff = config->backoff_ms;

    for (uint32_t attempt = 0; attempt < config->max_retries; attempt++) {
        if (mqtt_connect(client) == STATUS_OK) {
            return STATUS_OK;
        }

        /* Exponential backoff with jitter */
        uint32_t jitter = rand() % (backoff / 2);
        uint32_t wait_ms = backoff + jitter;

        sleep_ms(wait_ms);

        /* Increase backoff for next attempt */
        backoff = (backoff * 2 > config->max_backoff_ms) ?
                  config->max_backoff_ms : backoff * 2;
    }

    return STATUS_ERROR;
}
```

---

## Protocol Security Deep Dive

### MQTT over TLS/SSL
```c
/* TLS certificate handling in embedded systems */
typedef struct {
    const char *ca_cert;      /* Root CA certificate */
    const char *client_cert;  /* Device certificate */
    const char *client_key;   /* Device private key */
    int key_len;              /* Key length in bytes */
    int cert_len;             /* Certificate length */
} mqtt_tls_config_t;

/* Minimal certificate embedded */
const char mqtt_ca_cert[] = "-----BEGIN CERTIFICATE-----\n"
    "MIICljCCAX4CCQDp2..." /* Truncated for brevity */
    "-----END CERTIFICATE-----\n";

status_t mqtt_setup_tls(mqtt_client_t *client,
                        const mqtt_tls_config_t *tls_cfg) {
    /* Set CA certificate for server verification */
    if (mqtt_set_ca_cert(client, tls_cfg->ca_cert) != STATUS_OK) {
        return STATUS_ERROR;
    }

    /* Set client certificate and key */
    if (mqtt_set_client_cert(client, tls_cfg->client_cert,
                             tls_cfg->cert_len) != STATUS_OK) {
        return STATUS_ERROR;
    }

    if (mqtt_set_client_key(client, tls_cfg->client_key,
                            tls_cfg->key_len) != STATUS_OK) {
        return STATUS_ERROR;
    }

    return STATUS_OK;
}
```

### LoRaWAN Security Details
```c
/* LoRaWAN uses two keys: NwkSKey and AppSKey */
typedef struct {
    uint8_t nwk_skey[16];  /* Network session key */
    uint8_t app_skey[16];  /* Application session key */
    uint32_t fcnt_up;      /* Uplink frame counter */
    uint32_t fcnt_down;    /* Downlink frame counter */
} lorawan_session_keys_t;

/* OTAA: Over-The-Air Activation flow */
void lorawan_perform_otaa(const uint8_t *app_key,
                          const uint8_t *app_eui,
                          const uint8_t *dev_eui) {
    /* Step 1: Send Join Request (unencrypted) */
    lorawan_send_join_request(dev_eui, app_eui);

    /* Step 2: Receive Join Accept (encrypted with AppKey) */
    /* Step 3: Derive session keys from AppKey + Accept */
    lorawan_derive_session_keys(app_key);

    /* Step 4: Use session keys for encrypted uplink/downlink */
}
```

---

## Troubleshooting Protocol Issues

### Connection Problems
```c
/* Diagnostic checks */
void diagnose_mqtt_connectivity(mqtt_client_t *client) {
    /* Check network connectivity */
    if (!network_is_online()) {
        printf("Network offline\n");
        return;
    }

    /* Check broker DNS resolution */
    uint32_t broker_ip = dns_resolve(MQTT_BROKER);
    if (broker_ip == 0) {
        printf("DNS resolution failed\n");
        return;
    }

    /* Check TLS/SSL handshake */
    if (mqtt_test_tls_handshake(client) != STATUS_OK) {
        printf("TLS handshake failed - check certificates\n");
        return;
    }

    /* Check MQTT protocol negotiation */
    if (mqtt_test_connect(client) != STATUS_OK) {
        printf("MQTT CONNECT failed - check credentials\n");
        return;
    }

    printf("All connectivity checks passed\n");
}
```

### Message Loss & QoS Issues
```c
typedef struct {
    uint16_t message_id;
    uint32_t timestamp_ms;
    enum { PENDING, ACKED, FAILED } status;
} message_tracking_t;

#define MAX_PENDING_MESSAGES 10
static message_tracking_t pending_messages[MAX_PENDING_MESSAGES];

/* Track messages for retry handling */
void track_published_message(uint16_t msg_id) {
    for (int i = 0; i < MAX_PENDING_MESSAGES; i++) {
        if (pending_messages[i].status == FAILED) {
            pending_messages[i].message_id = msg_id;
            pending_messages[i].timestamp_ms = get_time_ms();
            pending_messages[i].status = PENDING;
            return;
        }
    }
}

/* Periodically check for unacknowledged messages */
void check_message_timeouts(void) {
    uint32_t now_ms = get_time_ms();

    for (int i = 0; i < MAX_PENDING_MESSAGES; i++) {
        if (pending_messages[i].status == PENDING) {
            uint32_t elapsed = now_ms - pending_messages[i].timestamp_ms;

            if (elapsed > PUBLISH_TIMEOUT_MS) {
                printf("Message %d timed out - retransmitting\n",
                       pending_messages[i].message_id);
                pending_messages[i].status = FAILED;
                /* Trigger retry mechanism */
            }
        }
    }
}
```

---

**Implement production-ready IoT protocol stacks with appropriate QoS, reliability, and power optimization.**
