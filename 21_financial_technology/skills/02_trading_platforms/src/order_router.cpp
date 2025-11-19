// Smart order routing engine
#include <vector>
#include <algorithm>
#include <atomic>

struct VenueScore {
    uint8_t venue_id;
    double spread;
    double liquidity;
    uint32_t latency_us;
    double total_cost;
};

class OrderRouter {
private:
    static constexpr int NUM_VENUES = 5;

    struct VenueMetrics {
        double avg_spread;
        uint32_t available_liquidity;
        uint32_t latency_us;
        double exchange_fee;
    };

    VenueMetrics venue_metrics[NUM_VENUES];
    std::atomic<uint64_t> routing_decisions{0};

public:
    uint8_t select_best_venue(uint32_t symbol_id,
                              int side,
                              uint32_t quantity) {
        std::vector<VenueScore> scores;

        for (int i = 0; i < NUM_VENUES; i++) {
            VenueScore score;
            score.venue_id = i;
            score.spread = venue_metrics[i].avg_spread;
            score.liquidity = venue_metrics[i].available_liquidity;
            score.latency_us = venue_metrics[i].latency_us;

            // Calculate total cost
            score.total_cost = score.spread +
                              venue_metrics[i].exchange_fee +
                              estimate_market_impact(i, quantity);

            scores.push_back(score);
        }

        // Select venue with lowest cost
        auto best = std::min_element(
            scores.begin(), scores.end(),
            [](const VenueScore& a, const VenueScore& b) {
                return a.total_cost < b.total_cost;
            }
        );

        routing_decisions.fetch_add(1);
        return best->venue_id;
    }

    void update_venue_metrics(uint8_t venue_id,
                             double avg_spread,
                             uint32_t liquidity) {
        venue_metrics[venue_id].avg_spread = avg_spread;
        venue_metrics[venue_id].available_liquidity = liquidity;
    }

private:
    double estimate_market_impact(uint8_t venue_id,
                                 uint32_t quantity) {
        uint32_t liquidity = venue_metrics[venue_id].available_liquidity;
        if (liquidity == 0) return 1.0;  // High cost if no liquidity

        // Market impact = (quantity / liquidity)^0.5
        double ratio = (double)quantity / liquidity;
        return 0.1 * sqrt(ratio);  // Simplified model
    }
};
