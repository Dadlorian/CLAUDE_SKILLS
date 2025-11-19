// Ultra-low latency order book implementation
// Compiled: g++ -O3 -march=native order_book.cpp

#include <map>
#include <vector>
#include <atomic>
#include <cstring>
#include <stdint.h>

struct Level {
    uint32_t price;
    uint32_t volume;
    uint32_t order_count;
};

class OrderBook {
private:
    // Pre-allocated levels for performance
    static constexpr int MAX_LEVELS = 100;
    Level bid_levels[MAX_LEVELS];
    Level ask_levels[MAX_LEVELS];
    int bid_depth = 0;
    int ask_depth = 0;

    uint64_t sequence_number = 0;
    uint64_t last_update_ns = 0;

    // Atomic flags for lock-free updates
    std::atomic<uint32_t> best_bid{0};
    std::atomic<uint32_t> best_ask{0};

public:
    inline uint64_t rdtsc() {
        unsigned int lo, hi;
        asm volatile("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64_t)hi << 32) | lo;
    }

    void add_level(bool is_bid, uint32_t price, uint32_t volume) {
        Level* levels = is_bid ? bid_levels : ask_levels;
        int& depth = is_bid ? bid_depth : ask_depth;

        if (depth >= MAX_LEVELS) return;

        // Insert in sorted order (O(depth) but depth typically <20)
        int insert_pos = 0;
        if (is_bid) {
            // Bids in descending order
            for (int i = 0; i < depth; i++) {
                if (levels[i].price > price) {
                    insert_pos = i + 1;
                } else {
                    break;
                }
            }
        } else {
            // Asks in ascending order
            for (int i = 0; i < depth; i++) {
                if (levels[i].price < price) {
                    insert_pos = i + 1;
                } else {
                    break;
                }
            }
        }

        // Shift and insert
        for (int i = depth; i > insert_pos; i--) {
            levels[i] = levels[i - 1];
        }

        levels[insert_pos].price = price;
        levels[insert_pos].volume = volume;
        levels[insert_pos].order_count = 1;
        depth++;

        // Update best bid/ask atomically
        if (insert_pos == 0) {
            if (is_bid) {
                best_bid.store(price, std::memory_order_release);
            } else {
                best_ask.store(price, std::memory_order_release);
            }
        }

        sequence_number++;
        last_update_ns = rdtsc();
    }

    void modify_level(bool is_bid, uint32_t price, uint32_t new_volume) {
        Level* levels = is_bid ? bid_levels : ask_levels;
        int depth = is_bid ? bid_depth : ask_depth;

        for (int i = 0; i < depth; i++) {
            if (levels[i].price == price) {
                levels[i].volume = new_volume;
                sequence_number++;
                last_update_ns = rdtsc();
                return;
            }
        }
    }

    void remove_level(bool is_bid, uint32_t price) {
        Level* levels = is_bid ? bid_levels : ask_levels;
        int& depth = is_bid ? bid_depth : ask_depth;

        for (int i = 0; i < depth; i++) {
            if (levels[i].price == price) {
                // Shift levels down
                for (int j = i; j < depth - 1; j++) {
                    levels[j] = levels[j + 1];
                }
                depth--;
                sequence_number++;
                last_update_ns = rdtsc();

                // Update best bid/ask if front level removed
                if (i == 0) {
                    if (is_bid && depth > 0) {
                        best_bid.store(levels[0].price,
                                     std::memory_order_release);
                    } else if (!is_bid && depth > 0) {
                        best_ask.store(levels[0].price,
                                     std::memory_order_release);
                    }
                }
                return;
            }
        }
    }

    struct PriceLevel {
        uint32_t price;
        uint32_t volume;
    };

    double get_spread() {
        uint32_t bid = best_bid.load(std::memory_order_acquire);
        uint32_t ask = best_ask.load(std::memory_order_acquire);
        if (bid == 0 || ask == 0) return 0;
        return (double)(ask - bid) / 10000.0;
    }

    double get_mid_price() {
        uint32_t bid = best_bid.load(std::memory_order_acquire);
        uint32_t ask = best_ask.load(std::memory_order_acquire);
        if (bid == 0 || ask == 0) return 0;
        return (double)(bid + ask) / 20000.0;
    }

    const Level* get_bid_levels(int& out_depth) {
        out_depth = bid_depth;
        return bid_levels;
    }

    const Level* get_ask_levels(int& out_depth) {
        out_depth = ask_depth;
        return ask_levels;
    }

    uint64_t get_sequence() const { return sequence_number; }
    uint64_t get_last_update_ns() const { return last_update_ns; }
};

// Example usage
int main() {
    OrderBook book;

    // Build initial book
    book.add_level(true, 150000, 1000);  // Bid at $150.00
    book.add_level(true, 149950, 2000);  // Bid at $149.95
    book.add_level(false, 150050, 1500); // Ask at $150.05
    book.add_level(false, 150100, 2500); // Ask at $150.10

    // Process updates
    for (int i = 0; i < 1000000; i++) {
        book.modify_level(true, 150000, 1000 + i);
        book.modify_level(false, 150050, 1500 - i % 100);
    }

    // Query
    printf("Spread: %.2f cents\n", book.get_spread() * 100);
    printf("Mid: $%.4f\n", book.get_mid_price());
    printf("Sequence: %lu\n", book.get_sequence());

    return 0;
}
