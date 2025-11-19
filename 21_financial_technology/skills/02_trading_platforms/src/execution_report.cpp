// Execution report parser and handler
#include <cstring>
#include <vector>

struct ExecutionReport {
    char client_order_id[64];
    char exchange_order_id[64];
    char status;  // 0=New, 1=PartFilled, 2=Filled, 8=Rejected
    uint32_t cum_qty;
    uint32_t last_qty;
    uint32_t last_price;
    uint32_t leaves_qty;
    char text[256];
};

class ExecutionReportProcessor {
public:
    bool parse_exec_report(const uint8_t* msg, uint16_t len,
                          ExecutionReport& report) {
        // Simple FIX parser for execution reports
        const char* msg_str = (const char*)msg;

        // Extract ClOrdID
        extract_field(msg_str, "11=", report.client_order_id);

        // Extract OrderID
        extract_field(msg_str, "37=", report.exchange_order_id);

        // Extract OrdStatus
        char status_str[2];
        extract_field(msg_str, "39=", status_str);
        report.status = status_str[0];

        // Extract CumQty
        char qty_str[10];
        extract_field(msg_str, "14=", qty_str);
        report.cum_qty = atoi(qty_str);

        // Extract LastQty
        extract_field(msg_str, "32=", qty_str);
        report.last_qty = atoi(qty_str);

        // Extract LeavesQty
        extract_field(msg_str, "151=", qty_str);
        report.leaves_qty = atoi(qty_str);

        return true;
    }

    void handle_partial_fill(const ExecutionReport& report) {
        // Update order status in OMS
        // Record fill in trade record
        printf("Partial fill: %u shares at oid %s\n",
               report.last_qty, report.exchange_order_id);
    }

    void handle_full_fill(const ExecutionReport& report) {
        // Mark order as filled
        // Record complete fill
        printf("Full fill: %u total shares\n", report.cum_qty);
    }

    void handle_rejection(const ExecutionReport& report) {
        // Cancel order in OMS
        // Log rejection reason
        printf("Rejection: %s\n", report.text);
    }

private:
    void extract_field(const char* msg, const char* tag,
                      char* output) {
        const char* pos = strstr(msg, tag);
        if (!pos) return;

        pos += strlen(tag);
        int i = 0;
        while (pos[i] != '\x01' && i < 255) {
            output[i] = pos[i];
            i++;
        }
        output[i] = '\0';
    }
};
