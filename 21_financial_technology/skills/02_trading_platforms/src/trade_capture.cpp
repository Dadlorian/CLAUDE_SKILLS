// Trade capture and settlement system
#include <vector>
#include <map>

struct Settlement {
    char security_isin[20];
    uint32_t quantity;
    uint32_t price;
    char counterparty[32];
    char settlement_date[10];
    char currency[4];
};

class TradeCapture {
private:
    std::vector<Settlement> settlements;
    std::map<std::string, uint32_t> pending_reconciliation;

public:
    void capture_trade(const char* exec_report) {
        // Parse execution report
        Settlement settle;

        // Extract settlement details
        extract_settlement_details(exec_report, settle);

        // Validate settlement
        if (validate_settlement(settle)) {
            settlements.push_back(settle);
            generate_settlement_instruction(settle);
        }
    }

    void generate_settlement_instruction(const Settlement& settle) {
        // Create DTC instruction
        printf("Settlement instruction:\n");
        printf("  ISIN: %s\n", settle.security_isin);
        printf("  Qty: %u\n", settle.quantity);
        printf("  Counterparty: %s\n", settle.counterparty);
        printf("  Settlement date: %s\n", settle.settlement_date);
    }

    void reconcile_settlement(const char* confirmation) {
        // Match execution report with settlement confirmation
        // Mark as reconciled
    }

private:
    void extract_settlement_details(const char* exec_report,
                                   Settlement& settle) {
        // Extract from FIX message
    }

    bool validate_settlement(const Settlement& settle) {
        // Check settlement is valid
        // Validate counterparty
        // Check settlement date is valid
        return true;
    }
};
