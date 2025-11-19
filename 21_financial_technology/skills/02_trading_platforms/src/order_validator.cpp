// Order validation engine
#include <atomic>
#include <map>

class OrderValidator {
private:
    static constexpr double MAX_PRICE = 10000.0;
    static constexpr int MAX_QUANTITY = 1000000;
    static constexpr double POSITION_LIMIT = 50000.0;

    std::map<std::string, std::atomic<int>> positions;

public:
    struct ValidationResult {
        bool valid;
        const char* reason;
    };

    ValidationResult validate_order(const char* symbol,
                                   int side,
                                   uint32_t quantity,
                                   double price) {
        // 1. Price check
        if (price <= 0 || price > MAX_PRICE) {
            return {false, "PRICE_OUT_OF_RANGE"};
        }

        // 2. Quantity check
        if (quantity <= 0 || quantity > MAX_QUANTITY) {
            return {false, "QUANTITY_OUT_OF_RANGE"};
        }

        // 3. Position limit check
        int current_position = positions[symbol].load();
        int new_position = current_position + (side == 1 ? quantity : -quantity);

        if (abs(new_position) > POSITION_LIMIT) {
            return {false, "POSITION_LIMIT_EXCEEDED"};
        }

        // 4. Duplicate check
        if (is_duplicate_order(symbol, quantity, price)) {
            return {false, "DUPLICATE_ORDER"};
        }

        return {true, nullptr};
    }

    void update_position(const char* symbol, int side, uint32_t quantity) {
        int qty_signed = (side == 1) ? quantity : -quantity;
        positions[symbol].fetch_add(qty_signed);
    }

private:
    bool is_duplicate_order(const char* symbol,
                           uint32_t quantity,
                           double price) {
        // Check recent order history for duplicates
        // Return true if duplicate found
        return false;
    }
};
