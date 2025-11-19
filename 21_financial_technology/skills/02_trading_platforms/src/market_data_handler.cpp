// High-performance market data handler
// Process 1M+ quotes/second with <1ms latency

#include <queue>
#include <thread>
#include <atomic>
#include <cstring>

struct Quote {
    uint64_t timestamp;
    uint32_t security_id;
    uint32_t bid_price;
    uint32_t ask_price;
    uint32_t bid_vol;
    uint32_t ask_vol;
    uint16_t sequence;
};

class MarketDataHandler {
private:
    static constexpr int QUEUE_SIZE = 1000000;
    Quote quotes[QUEUE_SIZE];
    std::atomic<int> write_pos{0};
    std::atomic<int> read_pos{0};

    // Statistics
    std::atomic<uint64_t> total_quotes{0};
    std::atomic<uint64_t> total_latency_ns{0};

    uint64_t subscription_filter = ~0ULL;  // Subscribe to all by default

public:
    bool enqueue_quote(const Quote& quote) {
        int next_write = (write_pos.load() + 1) % QUEUE_SIZE;

        if (next_write == read_pos.load()) {
            // Queue full, drop quote
            return false;
        }

        quotes[write_pos.load()] = quote;
        write_pos.store(next_write, std::memory_order_release);
        return true;
    }

    bool dequeue_quote(Quote& out_quote) {
        if (read_pos.load() == write_pos.load(std::memory_order_acquire)) {
            return false;  // Queue empty
        }

        out_quote = quotes[read_pos.load()];
        read_pos.store((read_pos.load() + 1) % QUEUE_SIZE);
        return true;
    }

    void process_batch() {
        Quote quote;

        while (dequeue_quote(quote)) {
            // Filter based on subscription
            if ((subscription_filter & (1ULL << quote.security_id)) == 0) {
                continue;  // Not subscribed
            }

            // Process quote (update order book, calculate metrics, etc.)
            process_single_quote(quote);

            // Track statistics
            uint64_t now = rdtsc();
            uint64_t latency = now - quote.timestamp;

            total_quotes.fetch_add(1, std::memory_order_relaxed);
            total_latency_ns.fetch_add(latency, std::memory_order_relaxed);
        }
    }

    void subscribe_symbol(uint32_t security_id) {
        if (security_id < 64) {
            subscription_filter |= (1ULL << security_id);
        }
    }

    void print_stats() {
        uint64_t quotes = total_quotes.load();
        uint64_t total_latency = total_latency_ns.load();

        if (quotes > 0) {
            printf("Processed: %lu quotes\n", quotes);
            printf("Avg latency: %.1f µs\n",
                   (double)total_latency / quotes / 1000.0);
        }
    }

private:
    uint64_t rdtsc() {
        unsigned int lo, hi;
        asm volatile("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64_t)hi << 32) | lo;
    }

    void process_single_quote(const Quote& quote) {
        // In real system: update order book, calculate VWAP, etc.
        // Keep this minimal for high throughput
    }
};

// Example producer/consumer
int main() {
    MarketDataHandler handler;

    // Simulate quote producer
    std::thread producer([&handler]() {
        Quote quote;
        quote.timestamp = 0;

        for (int i = 0; i < 1000000; i++) {
            quote.security_id = i % 10;
            quote.bid_price = 15000 + (rand() % 100);
            quote.ask_price = 15010 + (rand() % 100);
            quote.bid_vol = 1000 + (rand() % 5000);
            quote.ask_vol = 1000 + (rand() % 5000);
            quote.sequence = i;

            while (!handler.enqueue_quote(quote)) {
                // Busy wait if queue full
            }
        }
    });

    // Process quotes
    std::thread consumer([&handler]() {
        for (int batch = 0; batch < 10000; batch++) {
            handler.process_batch();
        }
        handler.print_stats();
    });

    producer.join();
    consumer.join();

    return 0;
}
