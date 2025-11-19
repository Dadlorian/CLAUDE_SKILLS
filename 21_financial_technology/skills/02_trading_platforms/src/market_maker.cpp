// Market making engine with dynamic spread calculation
#include <atomic>
#include <cmath>

class MarketMaker {
private:
    std::atomic<uint32_t> bid_price{0};
    std::atomic<uint32_t> ask_price{0};
    std::atomic<int32_t> position{0};
    std::atomic<uint64_t> pnl{0};

    static constexpr int MAX_POSITION = 10000;
    static constexpr double BASE_SPREAD = 0.01;  // 1 cent

public:
    void update_quotes(uint32_t mid_price, double volatility,
                      int current_position) {
        // Calculate spread based on volatility
        double vol_multiplier = volatility / 0.02;  // Normal vol = 2%
        double adjusted_spread = BASE_SPREAD * vol_multiplier;

        // Adjust for position (wider spread if overloaded)
        double position_adjustment = 1.0 + (double)current_position /
                                    MAX_POSITION * 0.005;

        double final_spread = adjusted_spread * position_adjustment;
        uint32_t half_spread = (uint32_t)(final_spread * 5000);

        bid_price.store(mid_price - half_spread);
        ask_price.store(mid_price + half_spread);
    }

    void record_trade(bool is_buy, int qty, uint32_t execution_price) {
        // Update position
        int qty_signed = is_buy ? qty : -qty;
        position.fetch_add(qty_signed);

        // Calculate PnL
        // Simplified: assume mid-price at execution
        // Real implementation would track detailed entry/exit
    }

    uint32_t get_bid() const { return bid_price.load(); }
    uint32_t get_ask() const { return ask_price.load(); }
    int32_t get_position() const { return position.load(); }
    uint64_t get_pnl() const { return pnl.load(); }
};
