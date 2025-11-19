# MQTT Protocol Quick Reference

## Connection

### Connect Packet
```c
typedef struct {
    char *client_id;        // Unique identifier
    char *username;         // Optional
    char *password;         // Optional
    uint16_t keep_alive;    // Seconds (60-300 typical)
    bool clean_session;     // true = discard previous session
} mqtt_connect_t;

// Keep-alive: Server disconnects if no message in keep_alive * 1.5
```

### Last Will and Testament (LWT)
```c
typedef struct {
    char *topic;
    char *message;
    uint8_t qos;            // 0, 1, or 2
    bool retained;
} mqtt_will_t;

// Sent by broker if client disconnects unexpectedly
```

## Quality of Service (QoS)

| QoS | Name | Guarantee | Use Case |
|-----|------|-----------|----------|
| 0 | At most once | Fire and forget | Non-critical telemetry |
| 1 | At least once | Acknowledged | Most telemetry |
| 2 | Exactly once | 4-way handshake | Critical commands |

### QoS 0 Flow
```
Client → PUBLISH → Broker
```

### QoS 1 Flow
```
Client → PUBLISH → Broker
Client ← PUBACK ← Broker
```

### QoS 2 Flow (Slow!)
```
Client → PUBLISH → Broker
Client ← PUBREC ← Broker
Client → PUBREL → Broker
Client ← PUBCOMP ← Broker
```

## Topics

### Topic Structure
```
sensors/building1/floor2/temperature
└─root─┘└─building──┘└floor┘└─metric──┘

devices/+/status        # + = single-level wildcard
sensors/#               # # = multi-level wildcard
```

### Topic Best Practices
```
✓ devices/{device_id}/telemetry
✓ commands/{device_id}/reboot
✓ alerts/temperature/high

✗ sensor1                    # Too generic
✗ /sensors/building          # Don't start with /
✗ sensors/building/floor/    # Don't end with /
```

### Reserved Topics
```
$SYS/broker/clients/connected
$SYS/broker/messages/sent
$SYS/broker/uptime
```

## Publish

```c
mqtt_publish(
    topic,          // "devices/sensor1/temp"
    payload,        // "{\"temp\":25.5}"
    payload_len,    // strlen(payload)
    qos,            // 0, 1, or 2
    retained        // true/false
);
```

### Retained Messages
- Broker stores last message with retained=true
- New subscribers immediately receive retained message
- Use for status (online/offline), configuration

```c
// Device comes online
mqtt_publish("devices/sensor1/status", "online", 6, 1, true);

// Last will (sent on disconnect)
mqtt_set_will("devices/sensor1/status", "offline", 7, 1, true);
```

## Subscribe

```c
mqtt_subscribe(
    topic,          // "commands/+/reboot"
    qos             // Max QoS (broker may downgrade)
);
```

### Wildcard Patterns
```c
// Single device
mqtt_subscribe("devices/sensor1/telemetry", 1);

// All devices
mqtt_subscribe("devices/+/telemetry", 1);

// All messages for a device
mqtt_subscribe("devices/sensor1/#", 1);

// All telemetry
mqtt_subscribe("+/+/telemetry", 1);
```

## Message Size Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Max packet size | 268,435,455 bytes | 256 MB (impractical) |
| Typical limit | 128 KB - 256 KB | Broker configuration |
| Recommended | < 1 KB | For IoT devices |
| ESP32 MQTT | 6 KB default | Can be increased |

## Keep-Alive

```c
// Send PINGREQ if no message sent in keep_alive period
keep_alive = 60;  // seconds

// Broker closes connection if no PINGREQ in keep_alive * 1.5
// = 90 seconds for keep_alive=60
```

## Persistent Session

### Clean Session = false
- Broker stores:
  - Subscriptions
  - QoS 1/2 messages for offline client
  - Pending QoS 2 messages
- Use for: Unreliable networks, critical messages

### Clean Session = true
- Fresh start on each connect
- No stored state
- Use for: Reliable networks, non-critical data

## MQTT v5.0 Features

### Request/Response
```c
mqtt_publish(
    topic,
    payload,
    qos,
    response_topic = "devices/sensor1/response",
    correlation_data = "request-123"
);
```

### Message Expiry
```c
mqtt_publish(
    topic,
    payload,
    qos,
    message_expiry_interval = 300  // 5 minutes
);
```

### User Properties
```c
mqtt_set_user_property("sensor-type", "DHT22");
mqtt_set_user_property("location", "warehouse");
```

### Topic Alias
```c
// First publish
mqtt_publish("very/long/topic/path/sensor/data", data, qos, topic_alias=1);

// Subsequent publishes
mqtt_publish(NULL, data, qos, topic_alias=1);  // Uses alias
```

## Security

### TLS/SSL (Port 8883)
```c
mqtt_config.transport = MQTT_TRANSPORT_OVER_SSL;
mqtt_config.cert_pem = ca_cert;
mqtt_config.client_cert_pem = client_cert;
mqtt_config.client_key_pem = client_key;
```

### Username/Password (Port 1883)
```c
mqtt_config.username = "device123";
mqtt_config.password = "secret_password";
```

### Recommendations
- Always use TLS in production
- Use username/password even with TLS
- Consider client certificates for device auth
- Rotate credentials periodically

## Common Patterns

### Device Telemetry
```c
// Publish every 60 seconds
mqtt_publish("devices/{id}/telemetry", json, strlen(json), 1, false);
```

### Remote Commands
```c
// Subscribe
mqtt_subscribe("commands/{id}/#", 1);

// Handle message
void on_message(char *topic, char *payload) {
    if (strcmp(topic, "commands/{id}/reboot") == 0) {
        schedule_reboot();
    }
}
```

### Status Reporting
```c
// On connect
mqtt_publish("devices/{id}/status", "online", 6, 1, true);

// Last will
mqtt_set_will("devices/{id}/status", "offline", 7, 1, true);
```

### Request-Response (MQTT v5)
```c
// Client request
mqtt_publish(
    "rpc/get_config",
    request_id,
    1,
    response_topic = "rpc/response/{client_id}"
);

// Server response
mqtt_publish(
    "rpc/response/{client_id}",
    config_json,
    1,
    correlation_data = request_id
);
```

## Broker Comparison

| Broker | Type | Max Connections | Clustering |
|--------|------|-----------------|------------|
| Mosquitto | Open | 100K+ | No |
| EMQ X | Open | 10M+ | Yes |
| HiveMQ | Commercial | Unlimited | Yes |
| AWS IoT Core | Cloud | Unlimited | N/A |
| Azure IoT Hub | Cloud | Unlimited | N/A |

## Error Codes (CONNACK)

| Code | Meaning |
|------|---------|
| 0 | Connection accepted |
| 1 | Unacceptable protocol version |
| 2 | Identifier rejected |
| 3 | Server unavailable |
| 4 | Bad username or password |
| 5 | Not authorized |

## Performance Tips

1. **Use QoS 0 for telemetry** (unless critical)
2. **Batch messages** when possible
3. **Use persistent sessions** for unreliable networks
4. **Keep payload small** (< 1 KB)
5. **Compress JSON** or use binary formats (Protobuf, CBOR)
6. **Adjust keep-alive** (60-300s typical)
7. **Use topic aliases** (MQTT v5) for frequent messages
8. **Limit subscriptions** (each adds overhead)

## Debugging

```bash
# Mosquitto clients
mosquitto_pub -h broker.example.com -t "test/topic" -m "Hello"
mosquitto_sub -h broker.example.com -t "test/#" -v

# With TLS
mosquitto_pub -h broker.example.com -p 8883 \
    --cafile ca.crt \
    --cert client.crt \
    --key client.key \
    -t "test/topic" -m "Hello"
```

## Resources

- OASIS MQTT v3.1.1: [docs.oasis-open.org](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html)
- MQTT v5.0: [docs.oasis-open.org](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
- Mosquitto: [mosquitto.org](https://mosquitto.org/)
- HiveMQ: [hivemq.com](https://www.hivemq.com/)
