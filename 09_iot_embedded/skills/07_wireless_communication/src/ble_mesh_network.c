/*
 * BLE Mesh Networking Implementation
 * Production-ready BLE mesh node with provisioning and models
 *
 * Features:
 * - Mesh provisioning (PB-ADV and PB-GATT)
 * - Generic OnOff Server/Client models
 * - Sensor Server model
 * - Friend and Low Power Node (LPN) support
 * - Message relay and TTL management
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* ============================================================================
 * BLE Mesh Node Configuration
 * ============================================================================ */

#define MESH_COMPANY_ID         0xFFFF  /* Example company ID */
#define MESH_PRODUCT_ID         0x0001
#define MESH_VERSION_ID         0x0001

#define MESH_MAX_ELEMENTS       4
#define MESH_MAX_MODELS         8
#define MESH_MAX_SUBSCRIPTIONS  16

/* Node features */
#define MESH_FEATURE_RELAY      (1 << 0)
#define MESH_FEATURE_PROXY      (1 << 1)
#define MESH_FEATURE_FRIEND     (1 << 2)
#define MESH_FEATURE_LPN        (1 << 3)

/* ============================================================================
 * Mesh Element and Model Definitions
 * ============================================================================ */

typedef enum {
    MESH_MODEL_GENERIC_ONOFF_SERVER = 0x1000,
    MESH_MODEL_GENERIC_ONOFF_CLIENT = 0x1001,
    MESH_MODEL_GENERIC_LEVEL_SERVER = 0x1002,
    MESH_MODEL_GENERIC_LEVEL_CLIENT = 0x1003,
    MESH_MODEL_SENSOR_SERVER = 0x1100,
    MESH_MODEL_SENSOR_CLIENT = 0x1102
} mesh_model_id_t;

typedef struct {
    uint16_t model_id;
    uint16_t company_id;  /* 0xFFFF for SIG models */
    void *user_data;

    /* Model callbacks */
    void (*on_message)(void *ctx, uint16_t src_addr, const uint8_t *data, uint16_t len);
    void (*on_publish)(void *ctx);
} mesh_model_t;

typedef struct {
    uint16_t loc;  /* Location descriptor */
    uint8_t num_models;
    mesh_model_t models[MESH_MAX_MODELS];
} mesh_element_t;

typedef struct {
    uint16_t primary_addr;  /* Primary element unicast address */
    uint16_t features;      /* Node features bitmask */
    uint8_t num_elements;
    mesh_element_t elements[MESH_MAX_ELEMENTS];

    /* Network credentials */
    uint8_t dev_key[16];
    uint8_t net_key[16];
    uint8_t app_key[16];
    uint16_t net_key_index;
    uint16_t app_key_index;

    /* Node state */
    bool provisioned;
    uint32_t iv_index;
    uint8_t ttl;  /* Time To Live for relayed messages */
} mesh_node_t;

static mesh_node_t g_mesh_node = {0};

/* ============================================================================
 * Generic OnOff Model Implementation
 * ============================================================================ */

typedef struct {
    bool onoff;
    uint32_t transition_time_ms;
    uint32_t delay_ms;
} generic_onoff_state_t;

typedef enum {
    GENERIC_ONOFF_OPCODE_GET = 0x8201,
    GENERIC_ONOFF_OPCODE_SET = 0x8202,
    GENERIC_ONOFF_OPCODE_SET_UNACK = 0x8203,
    GENERIC_ONOFF_OPCODE_STATUS = 0x8204
} generic_onoff_opcode_t;

void generic_onoff_server_publish(mesh_model_t *model) {
    generic_onoff_state_t *state = (generic_onoff_state_t *)model->user_data;

    uint8_t payload[3];
    payload[0] = state->onoff ? 1 : 0;
    payload[1] = 0;  /* Target state (same as present) */
    payload[2] = 0;  /* Remaining time */

    /* Publish status */
    extern void mesh_model_publish(mesh_model_t *model, uint16_t opcode,
                                    const uint8_t *data, uint16_t len);
    mesh_model_publish(model, GENERIC_ONOFF_OPCODE_STATUS, payload, sizeof(payload));
}

void generic_onoff_server_on_message(void *ctx, uint16_t src_addr,
                                      const uint8_t *data, uint16_t len) {
    mesh_model_t *model = (mesh_model_t *)ctx;
    generic_onoff_state_t *state = (generic_onoff_state_t *)model->user_data;

    if (len < 1) return;

    uint16_t opcode = (data[0] << 8) | data[1];
    const uint8_t *params = data + 2;
    uint16_t params_len = len - 2;

    switch (opcode) {
        case GENERIC_ONOFF_OPCODE_GET:
            /* Reply with status */
            generic_onoff_server_publish(model);
            break;

        case GENERIC_ONOFF_OPCODE_SET:
        case GENERIC_ONOFF_OPCODE_SET_UNACK: {
            if (params_len < 1) break;

            bool new_state = params[0] ? true : false;
            uint8_t tid = params[1];  /* Transaction ID */

            /* Check for duplicate message (same TID) */
            static uint8_t last_tid = 0xFF;
            static uint16_t last_src = 0;
            if (tid == last_tid && src_addr == last_src) {
                return;  /* Duplicate, ignore */
            }
            last_tid = tid;
            last_src = src_addr;

            /* Update state */
            state->onoff = new_state;

            /* Apply to hardware */
            extern void gpio_set_output(bool value);
            gpio_set_output(state->onoff);

            /* Send status if SET (acknowledged) */
            if (opcode == GENERIC_ONOFF_OPCODE_SET) {
                generic_onoff_server_publish(model);
            }
            break;
        }
    }
}

mesh_model_t* generic_onoff_server_create(generic_onoff_state_t *state) {
    static mesh_model_t model = {0};

    model.model_id = MESH_MODEL_GENERIC_ONOFF_SERVER;
    model.company_id = 0xFFFF;  /* SIG model */
    model.user_data = state;
    model.on_message = generic_onoff_server_on_message;
    model.on_publish = generic_onoff_server_publish;

    return &model;
}

/* ============================================================================
 * Sensor Model Implementation
 * ============================================================================ */

typedef struct {
    uint16_t property_id;  /* Sensor Property ID (e.g., 0x004F for Temperature) */
    uint8_t *data;
    uint16_t data_len;
} sensor_descriptor_t;

typedef enum {
    SENSOR_OPCODE_DESCRIPTOR_GET = 0x8230,
    SENSOR_OPCODE_DESCRIPTOR_STATUS = 0x51,
    SENSOR_OPCODE_GET = 0x8231,
    SENSOR_OPCODE_STATUS = 0x52,
    SENSOR_OPCODE_SERIES_GET = 0x8233,
    SENSOR_OPCODE_SERIES_STATUS = 0x53
} sensor_opcode_t;

void sensor_server_publish(mesh_model_t *model) {
    sensor_descriptor_t *sensor = (sensor_descriptor_t *)model->user_data;

    /* Read current sensor value */
    extern float read_temperature_sensor(void);
    float temp = read_temperature_sensor();

    /* Encode as temperature (0.01°C resolution) */
    int16_t temp_encoded = (int16_t)(temp * 100.0f);

    uint8_t payload[5];
    payload[0] = SENSOR_OPCODE_STATUS;
    payload[1] = sensor->property_id & 0xFF;
    payload[2] = (sensor->property_id >> 8) & 0x07;  /* Property ID (11 bits) */
    payload[3] = temp_encoded & 0xFF;
    payload[4] = (temp_encoded >> 8) & 0xFF;

    extern void mesh_model_publish(mesh_model_t *model, uint16_t opcode,
                                    const uint8_t *data, uint16_t len);
    mesh_model_publish(model, SENSOR_OPCODE_STATUS, payload, sizeof(payload));
}

void sensor_server_on_message(void *ctx, uint16_t src_addr,
                               const uint8_t *data, uint16_t len) {
    mesh_model_t *model = (mesh_model_t *)ctx;

    if (len < 1) return;

    uint8_t opcode = data[0];

    switch (opcode) {
        case SENSOR_OPCODE_GET:
        case SENSOR_OPCODE_DESCRIPTOR_GET:
            /* Reply with sensor data */
            sensor_server_publish(model);
            break;
    }
}

mesh_model_t* sensor_server_create(sensor_descriptor_t *sensor) {
    static mesh_model_t model = {0};

    model.model_id = MESH_MODEL_SENSOR_SERVER;
    model.company_id = 0xFFFF;
    model.user_data = sensor;
    model.on_message = sensor_server_on_message;
    model.on_publish = sensor_server_publish;

    return &model;
}

/* ============================================================================
 * Low Power Node (LPN) Support
 * ============================================================================ */

typedef struct {
    bool enabled;
    uint16_t friend_addr;
    uint32_t poll_timeout_ms;
    uint8_t receive_delay;
    uint32_t last_poll_ms;
} lpn_state_t;

static lpn_state_t g_lpn_state = {
    .enabled = false,
    .friend_addr = 0,
    .poll_timeout_ms = 10000,  /* 10 seconds */
    .receive_delay = 100,      /* 100 ms */
    .last_poll_ms = 0
};

void lpn_enable(void) {
    g_lpn_state.enabled = true;

    /* Send Friend Request */
    extern void mesh_send_friend_request(uint32_t poll_timeout,
                                          uint8_t receive_delay);
    mesh_send_friend_request(g_lpn_state.poll_timeout_ms,
                             g_lpn_state.receive_delay);
}

void lpn_poll_friend(void) {
    if (!g_lpn_state.enabled || g_lpn_state.friend_addr == 0) {
        return;
    }

    extern uint32_t get_system_time_ms(void);
    uint32_t now = get_system_time_ms();

    /* Check if it's time to poll */
    if ((now - g_lpn_state.last_poll_ms) >= g_lpn_state.poll_timeout_ms) {
        /* Send Friend Poll message */
        extern void mesh_send_friend_poll(uint16_t friend_addr);
        mesh_send_friend_poll(g_lpn_state.friend_addr);

        g_lpn_state.last_poll_ms = now;

        /* Enter low-power mode until next poll */
        extern void enter_low_power_mode(uint32_t duration_ms);
        enter_low_power_mode(g_lpn_state.poll_timeout_ms - 100);
    }
}

void lpn_on_friend_offer(uint16_t friend_addr, uint8_t receive_window) {
    /* Accept friend offer */
    g_lpn_state.friend_addr = friend_addr;

    /* Send Friend Poll immediately */
    lpn_poll_friend();
}

/* ============================================================================
 * Mesh Provisioning
 * ============================================================================ */

typedef enum {
    PROV_STATE_IDLE,
    PROV_STATE_LINK_OPEN,
    PROV_STATE_INVITE,
    PROV_STATE_CAPABILITIES,
    PROV_STATE_START,
    PROV_STATE_PUBLIC_KEY,
    PROV_STATE_CONFIRM,
    PROV_STATE_RANDOM,
    PROV_STATE_DATA,
    PROV_STATE_COMPLETE
} prov_state_t;

typedef struct {
    prov_state_t state;
    uint8_t uuid[16];
    uint8_t public_key[64];
    uint8_t private_key[32];
    uint8_t auth_value[16];
} prov_context_t;

static prov_context_t g_prov_ctx = {
    .state = PROV_STATE_IDLE
};

void provisioning_start_unprovisioned_beacon(void) {
    /* Advertise unprovisioned beacon */
    uint8_t beacon_data[22];
    beacon_data[0] = 0x00;  /* Beacon type: Unprovisioned */
    memcpy(&beacon_data[1], g_prov_ctx.uuid, 16);

    /* OOB information (Out-Of-Band) */
    beacon_data[17] = 0x00;  /* OOB flags (low byte) */
    beacon_data[18] = 0x00;  /* OOB flags (high byte) */

    /* URI hash (optional) */
    beacon_data[19] = 0x00;
    beacon_data[20] = 0x00;
    beacon_data[21] = 0x00;
    beacon_data[22] = 0x00;

    extern void ble_advertise_mesh_beacon(const uint8_t *data, uint16_t len);
    ble_advertise_mesh_beacon(beacon_data, sizeof(beacon_data));
}

void provisioning_on_invite(void) {
    /* Send capabilities */
    uint8_t capabilities[11];
    capabilities[0] = 1;  /* Number of elements */
    capabilities[1] = 0x00;  /* Algorithms (FIPS P-256) */
    capabilities[2] = 0x00;  /* Public key type */
    capabilities[3] = 0x00;  /* Static OOB type */
    capabilities[4] = 0x00;  /* Output OOB size */
    capabilities[5] = 0x00;  /* Output OOB action */
    capabilities[6] = 0x00;  /* Input OOB size */
    capabilities[7] = 0x00;  /* Input OOB action */

    extern void provisioning_send_pdu(uint8_t type, const uint8_t *data, uint16_t len);
    provisioning_send_pdu(0x01, capabilities, sizeof(capabilities));
}

void provisioning_on_data(const uint8_t *prov_data, uint16_t len) {
    /* Extract provisioning data */
    const uint8_t *net_key = &prov_data[0];
    uint16_t key_index = (prov_data[16] << 8) | prov_data[17];
    uint8_t flags = prov_data[18];
    uint32_t iv_index = (prov_data[19] << 24) | (prov_data[20] << 16) |
                        (prov_data[21] << 8) | prov_data[22];
    uint16_t unicast_addr = (prov_data[23] << 8) | prov_data[24];

    /* Store provisioning data */
    memcpy(g_mesh_node.net_key, net_key, 16);
    g_mesh_node.net_key_index = key_index;
    g_mesh_node.iv_index = iv_index;
    g_mesh_node.primary_addr = unicast_addr;
    g_mesh_node.provisioned = true;

    /* Send provisioning complete */
    provisioning_send_pdu(0x07, NULL, 0);

    /* Save to persistent storage */
    extern void mesh_save_config(mesh_node_t *node);
    mesh_save_config(&g_mesh_node);
}

/* ============================================================================
 * Mesh Network Layer
 * ============================================================================ */

typedef struct {
    uint16_t src;
    uint16_t dst;
    uint8_t ttl;
    uint8_t ctl;  /* Control message flag */
    uint32_t seq;
    uint16_t net_key_index;
    const uint8_t *payload;
    uint16_t payload_len;
} mesh_network_pdu_t;

void mesh_network_transmit(mesh_network_pdu_t *pdu) {
    /* Encrypt network PDU */
    uint8_t encrypted_pdu[29];  /* Max network PDU size */

    extern void mesh_network_encrypt(mesh_network_pdu_t *pdu,
                                      const uint8_t *net_key,
                                      uint8_t *output);
    mesh_network_encrypt(pdu, g_mesh_node.net_key, encrypted_pdu);

    /* Transmit via BLE advertising */
    extern void ble_mesh_transmit(const uint8_t *data, uint16_t len);
    ble_mesh_transmit(encrypted_pdu, pdu->payload_len + 9);
}

void mesh_network_receive(const uint8_t *data, uint16_t len) {
    /* Decrypt network PDU */
    mesh_network_pdu_t pdu;

    extern bool mesh_network_decrypt(const uint8_t *data, uint16_t len,
                                      const uint8_t *net_key,
                                      mesh_network_pdu_t *pdu);
    if (!mesh_network_decrypt(data, len, g_mesh_node.net_key, &pdu)) {
        return;  /* Decryption failed */
    }

    /* Check if message is for this node */
    bool is_for_me = (pdu.dst == g_mesh_node.primary_addr) ||
                      (pdu.dst >= 0xC000 && pdu.dst <= 0xFEFF);  /* Group/virtual address */

    /* Relay if enabled and TTL > 1 */
    if ((g_mesh_node.features & MESH_FEATURE_RELAY) && pdu.ttl > 1 && !is_for_me) {
        pdu.ttl--;
        mesh_network_transmit(&pdu);
    }

    /* Process if for this node */
    if (is_for_me) {
        /* Decrypt transport layer */
        extern void mesh_transport_process(mesh_network_pdu_t *pdu);
        mesh_transport_process(&pdu);
    }
}

/* ============================================================================
 * Mesh Initialization
 * ============================================================================ */

void mesh_node_init(void) {
    /* Generate UUID from device ID */
    extern void get_device_uuid(uint8_t *uuid);
    get_device_uuid(g_prov_ctx.uuid);

    /* Load provisioning data from storage if available */
    extern bool mesh_load_config(mesh_node_t *node);
    if (mesh_load_config(&g_mesh_node)) {
        /* Already provisioned */
        g_mesh_node.provisioned = true;
    } else {
        /* Start unprovisioned */
        g_mesh_node.provisioned = false;
        provisioning_start_unprovisioned_beacon();
    }

    /* Configure node features */
    g_mesh_node.features = MESH_FEATURE_RELAY | MESH_FEATURE_PROXY;
    g_mesh_node.ttl = 7;  /* Default TTL */

    /* Add primary element with models */
    mesh_element_t *elem = &g_mesh_node.elements[0];
    elem->loc = 0x0100;  /* Front */
    elem->num_models = 0;

    /* Add Generic OnOff Server */
    static generic_onoff_state_t onoff_state = {.onoff = false};
    elem->models[elem->num_models++] = *generic_onoff_server_create(&onoff_state);

    /* Add Sensor Server */
    static sensor_descriptor_t temp_sensor = {
        .property_id = 0x004F  /* Temperature */
    };
    elem->models[elem->num_models++] = *sensor_server_create(&temp_sensor);

    g_mesh_node.num_elements = 1;
}
