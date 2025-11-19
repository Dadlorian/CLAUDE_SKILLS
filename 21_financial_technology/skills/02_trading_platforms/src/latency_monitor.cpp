// Real-time latency monitoring and measurement
#include <algorithm>
#include <cmath>
#include <atomic>

class LatencyHistogram {
private:
    static constexpr int BUCKET_COUNT = 1000;
    static constexpr int BUCKET_SIZE_NS = 100;

    std::atomic<uint64_t> buckets[BUCKET_COUNT]{};
    std::atomic<uint64_t> total_samples{0};
    std::atomic<uint64_t> min_latency{UINT64_MAX};
    std::atomic<uint64_t> max_latency{0};

public:
    void record_latency_ns(uint64_t latency) {
        int bucket_idx = std::min(
            (int)(latency / BUCKET_SIZE_NS),
            BUCKET_COUNT - 1);

        buckets[bucket_idx].fetch_add(1, std::memory_order_relaxed);
        total_samples.fetch_add(1, std::memory_order_relaxed);

        // Track min/max
        uint64_t old_min = min_latency.load();
        while (latency < old_min &&
               !min_latency.compare_exchange_weak(
                   old_min, latency,
                   std::memory_order_release)) {
            old_min = min_latency.load();
        }

        uint64_t old_max = max_latency.load();
        while (latency > old_max &&
               !max_latency.compare_exchange_weak(
                   old_max, latency,
                   std::memory_order_release)) {
            old_max = max_latency.load();
        }
    }

    uint64_t percentile(double p) {
        uint64_t total = total_samples.load();
        uint64_t target = (uint64_t)(total * p / 100);
        uint64_t count = 0;

        for (int i = 0; i < BUCKET_COUNT; i++) {
            count += buckets[i].load(std::memory_order_acquire);
            if (count >= target) {
                return (uint64_t)i * BUCKET_SIZE_NS;
            }
        }
        return 0;
    }

    void print_stats() {
        printf("Latency statistics:\n");
        printf("  Min:    %lu ns\n", min_latency.load());
        printf("  P50:    %lu ns\n", percentile(50));
        printf("  P95:    %lu ns\n", percentile(95));
        printf("  P99:    %lu ns\n", percentile(99));
        printf("  P99.9:  %lu ns\n", percentile(99.9));
        printf("  Max:    %lu ns\n", max_latency.load());
        printf("  Samples: %lu\n", total_samples.load());
    }
};
