// FIX Protocol message parsing and generation
// Ultra-low latency implementation

#include <cstring>
#include <cstdint>

struct FIXMessage {
    uint8_t buffer[1024];
    uint16_t length;
    uint16_t position;
};

class FIXEngine {
private:
    static const uint8_t SOH = 0x01;

public:
    bool parse_message(const uint8_t* data, uint16_t len,
                      FIXMessage& msg) {
        msg.position = 0;
        msg.length = len;
        memcpy(msg.buffer, data, len);
        return true;
    }

    uint32_t extract_field(const FIXMessage& msg, uint16_t tag) {
        // Fast field extraction using tag lookup
        uint16_t pos = 0;
        uint32_t current_tag = 0;
        uint32_t current_value = 0;
        bool reading_tag = true;

        while (pos < msg.length) {
            uint8_t c = msg.buffer[pos++];

            if (c == SOH) {
                if (current_tag == tag) {
                    return current_value;
                }
                current_tag = 0;
                current_value = 0;
                reading_tag = true;
            } else if (c == '=') {
                reading_tag = false;
            } else if (reading_tag) {
                current_tag = current_tag * 10 + (c - '0');
            } else {
                current_value = current_value * 10 + (c - '0');
            }
        }

        return (current_tag == tag) ? current_value : 0;
    }

    void build_new_order_single(FIXMessage& msg,
                               const char* client_order_id,
                               uint32_t quantity,
                               uint32_t price) {
        uint16_t pos = 0;
        
        // Build message in buffer
        pos += sprintf((char*)msg.buffer + pos, "8=FIX.4.4%c", SOH);
        pos += sprintf((char*)msg.buffer + pos, "9=100%c", SOH);  // Body length
        pos += sprintf((char*)msg.buffer + pos, "35=D%c", SOH);   // MsgType
        pos += sprintf((char*)msg.buffer + pos, "49=CLIENT%c", SOH);
        pos += sprintf((char*)msg.buffer + pos, "56=EXCH%c", SOH);
        pos += sprintf((char*)msg.buffer + pos, "34=1%c", SOH);   // SeqNum
        pos += sprintf((char*)msg.buffer + pos, "52=20250101-10:00:00%c", SOH);
        pos += sprintf((char*)msg.buffer + pos, "11=%s%c", client_order_id, SOH);
        pos += sprintf((char*)msg.buffer + pos, "55=AAPL%c", SOH);
        pos += sprintf((char*)msg.buffer + pos, "54=1%c", SOH);   // Buy
        pos += sprintf((char*)msg.buffer + pos, "38=%u%c", quantity, SOH);
        pos += sprintf((char*)msg.buffer + pos, "40=2%c", SOH);   // Limit
        pos += sprintf((char*)msg.buffer + pos, "44=%u%c", price, SOH);
        pos += sprintf((char*)msg.buffer + pos, "10=000%c", SOH); // Checksum

        msg.length = pos;
    }
};

int main() {
    FIXEngine engine;
    FIXMessage msg;

    // Parse example message
    const char* raw = "8=FIX.4.4\x0135=D\x0155=AAPL\x0138=1000\x01";
    engine.parse_message((const uint8_t*)raw, strlen(raw), msg);

    // Extract fields
    uint32_t qty = engine.extract_field(msg, 38);  // OrderQty
    printf("Order quantity: %u\n", qty);

    // Build new order
    FIXMessage new_order;
    engine.build_new_order_single(new_order, "ORD001", 1000, 15000);
    printf("Built message length: %u\n", new_order.length);

    return 0;
}
