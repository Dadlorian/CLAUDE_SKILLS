// High-throughput tick data processor
#include <vector>
#include <atomic>
#include <deque>

struct Tick {
    uint64_t timestamp;
    uint32_t price;
    uint32_t volume;
    uint16_t sequence;
};

class TickProcessor {
private:
    static constexpr int MAX_WINDOW = 1000000;
    std::deque<Tick> tick_buffer;
    std::atomic<uint64_t> ticks_processed{0};
    std::atomic<uint64_t> volume_total{0};

public:
    void process_tick(const Tick& tick) {
        // Add to buffer
        tick_buffer.push_back(tick);

        // Keep buffer size limited
        if (tick_buffer.size() > MAX_WINDOW) {
            tick_buffer.pop_front();
        }

        ticks_processed.fetch_add(1);
        volume_total.fetch_add(tick.volume);
    }

    double calculate_vwap() {
        if (tick_buffer.empty()) return 0;

        uint64_t sum_pv = 0;
        uint64_t sum_v = 0;

        for (const auto& tick : tick_buffer) {
            sum_pv += (uint64_t)tick.price * tick.volume;
            sum_v += tick.volume;
        }

        return sum_v > 0 ? (double)sum_pv / sum_v : 0;
    }

    double calculate_twap() {
        if (tick_buffer.empty()) return 0;

        uint64_t sum_price = 0;
        for (const auto& tick : tick_buffer) {
            sum_price += tick.price;
        }

        return (double)sum_price / tick_buffer.size();
    }

    double calculate_volatility() {
        if (tick_buffer.size() < 2) return 0;

        double twap = calculate_twap();
        double sum_sq_dev = 0;

        for (const auto& tick : tick_buffer) {
            double dev = tick.price - twap;
            sum_sq_dev += dev * dev;
        }

        return sqrt(sum_sq_dev / tick_buffer.size());
    }

    uint64_t get_stats() {
        return ticks_processed.load();
    }
};
