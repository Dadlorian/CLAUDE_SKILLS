# Market Data Processing Guide

## Architecture Overview

Market data pipeline processes 1M+ ticks/second with <500µs latency:

```
NIC → FIX Parser → Normalization → Order Book Update →
Analytics → Distribution → Consumer Applications
```

## Step 1: High-Speed NIC Configuration

```bash
#!/bin/bash
# Configure NIC for maximum throughput

IFACE="eth0"

# 1. Enable hardware offloads
ethtool -K $IFACE gro on gso on tso on  # Generic segmentation offload
ethtool -K $IFACE ntuple on              # N-tuple filtering

# 2. Enable timestamping
ethtool -T $IFACE hwtstamp rx on tx on

# 3. Set ring buffers
ethtool -G $IFACE rx 4096 tx 4096

# 4. Enable RSS (Receive Side Scaling) for parallelism
ethtool -L $IFACE combined 8

# 5. Set MTU (typical 1500 for Ethernet, 9000 for jumbo)
ip link set dev $IFACE mtu 1500

# Verify settings
ethtool -i $IFACE
```

## Step 2: FIX Protocol Parser

```cpp
class FIXMarketDataParser {
    static constexpr size_t BUFFER_SIZE = 65536;
    uint8_t buffer[BUFFER_SIZE];
    size_t buffer_pos = 0;

public:
    void on_data_received(const uint8_t* data, size_t len) {
        // Copy to buffer
        memcpy(buffer + buffer_pos, data, len);
        buffer_pos += len;

        // Parse complete messages
        while (buffer_pos > 0) {
            size_t msg_len = find_message_length();
            if (msg_len == 0) break;  // Incomplete message

            parse_fix_message(buffer, msg_len);

            // Slide buffer
            memmove(buffer, buffer + msg_len, buffer_pos - msg_len);
            buffer_pos -= msg_len;
        }
    }

private:
    size_t find_message_length() {
        // FIX format: BeginString(8)=FIX.4.4 | BodyLength(9)=<length>
        // Skip to field 9
        size_t pos = 0;
        int field_count = 0;

        while (pos < buffer_pos && field_count < 2) {
            if (buffer[pos] == SOH) {
                field_count++;
                if (field_count == 2) {
                    // Extract body length from field 9
                    pos++;
                    size_t len = 0;
                    while (pos < buffer_pos && buffer[pos] != SOH) {
                        len = len * 10 + (buffer[pos++] - '0');
                    }
                    if (pos < buffer_pos) {
                        return len + pos + 1 + 7;  // header + trailer
                    }
                }
            }
            pos++;
        }
        return 0;  // Incomplete
    }

    void parse_fix_message(const uint8_t* msg, size_t len) {
        // Extract fields using state machine
        uint32_t field_tag = 0;
        uint32_t field_value = 0;
        bool reading_tag = true;

        for (size_t i = 0; i < len; i++) {
            if (msg[i] == SOH) {
                // End of field
                process_field(field_tag, field_value);
                field_tag = 0;
                field_value = 0;
                reading_tag = true;
            } else if (msg[i] == '=') {
                reading_tag = false;
            } else if (reading_tag) {
                field_tag = field_tag * 10 + (msg[i] - '0');
            } else {
                field_value = field_value * 10 + (msg[i] - '0');
            }
        }
    }

    void process_field(uint32_t tag, uint32_t value) {
        // Handle specific FIX fields
        switch (tag) {
            case 35: quote.msg_type = (MsgType)value; break;
            case 49: quote.sender_id = value; break;
            case 55: quote.symbol_id = value; break;
            case 44: quote.bid_price = value; break;
            case 45: quote.ask_price = value; break;
            // ... more fields
        }
    }
};

static const uint8_t SOH = 0x01;  // Start of Header delimiter
```

## Step 3: Multi-Feed Aggregation

```cpp
class MarketDataAggregator {
    struct FeedState {
        uint32_t feed_id;
        uint64_t last_sequence;
        OrderBook book;
        Timestamp last_update;
    };

    std::map<uint32_t, FeedState> feeds;  // One per feed
    OrderBook aggregated_book;

public:
    void process_quote_update(uint32_t feed_id, const Quote& quote) {
        // 1. Validate sequence
        FeedState& state = feeds[feed_id];
        if (quote.sequence != state.last_sequence + 1) {
            LOG_WARNING("Gap in feed " << feed_id
                << ": expected " << state.last_sequence + 1
                << " got " << quote.sequence);
            request_retransmit(feed_id, state.last_sequence);
        }
        state.last_sequence = quote.sequence;

        // 2. Update feed-specific book
        state.book.update(quote);

        // 3. Recalculate aggregate best bid/ask
        uint32_t best_bid = 0;
        uint32_t best_ask = UINT32_MAX;

        for (auto& [fid, feed_state] : feeds) {
            best_bid = std::max(best_bid, feed_state.book.get_best_bid());
            best_ask = std::min(best_ask, feed_state.book.get_best_ask());
        }

        // 4. Publish if changed
        if (best_bid != aggregated_book.best_bid ||
            best_ask != aggregated_book.best_ask) {
            aggregated_book.best_bid = best_bid;
            aggregated_book.best_ask = best_ask;
            aggregated_book.timestamp = get_exchange_timestamp();
            publish_aggregated_quote();
        }
    }

    OrderBook get_best_book() const {
        return aggregated_book;
    }
};
```

## Step 4: Order Book Management

```cpp
struct OrderBookLevel {
    uint32_t price;
    uint32_t volume;
    uint16_t order_count;  // Number of orders at this level
};

class OrderBook {
    // Use skip list for fast search/insert/delete
    std::map<uint32_t, OrderBookLevel> bids;
    std::map<uint32_t, OrderBookLevel> asks;
    uint64_t sequence_number = 0;
    uint64_t timestamp = 0;

public:
    void add_level(Side side, uint32_t price, uint32_t volume) {
        auto& book = (side == BUY) ? bids : asks;
        book[price].price = price;
        book[price].volume = volume;
        book[price].order_count++;
        sequence_number++;
        timestamp = rdtsc();
    }

    void remove_level(Side side, uint32_t price) {
        auto& book = (side == BUY) ? bids : asks;
        auto it = book.find(price);
        if (it != book.end()) {
            book.erase(it);
            sequence_number++;
            timestamp = rdtsc();
        }
    }

    void modify_level(Side side, uint32_t price, uint32_t new_volume) {
        auto& book = (side == BUY) ? bids : asks;
        auto it = book.find(price);
        if (it != book.end()) {
            it->second.volume = new_volume;
            sequence_number++;
            timestamp = rdtsc();
        }
    }

    uint32_t get_best_bid() const {
        return bids.empty() ? 0 : bids.rbegin()->first;
    }

    uint32_t get_best_ask() const {
        return asks.empty() ? 0 : asks.begin()->first;
    }

    double get_spread() const {
        uint32_t bid = get_best_bid();
        uint32_t ask = get_best_ask();
        if (bid == 0 || ask == 0) return 0;
        return (ask - bid) / 10000.0;  // Convert to price
    }

    const std::map<uint32_t, OrderBookLevel>& get_depth() const {
        return bids;  // Or asks
    }
};
```

## Step 5: Real-Time VWAP Calculation

```cpp
class VWAPCalculator {
    uint64_t sum_pq = 0;      // Sum of price × quantity
    uint64_t sum_q = 0;       // Sum of quantity
    uint64_t window_start = 0; // Timestamp of window start
    static constexpr uint64_t WINDOW_NS = 3600 * 1e9;  // 1 hour

public:
    void process_trade(uint64_t timestamp, uint32_t price, uint32_t quantity) {
        // Initialize window if first trade
        if (window_start == 0) {
            window_start = timestamp;
        }

        // Check if window expired
        if (timestamp - window_start > WINDOW_NS) {
            // Reset for new window
            sum_pq = 0;
            sum_q = 0;
            window_start = timestamp;
        }

        // Add trade to VWAP
        sum_pq += (uint64_t)price * quantity;
        sum_q += quantity;
    }

    double get_vwap() const {
        if (sum_q == 0) return 0;
        return (double)sum_pq / sum_q / 10000.0;  // Convert to price
    }

    uint64_t get_volume() const {
        return sum_q;
    }
};
```

## Step 6: Consumer Distribution

```cpp
class MarketDataPublisher {
    std::vector<MarketDataConsumer*> subscribers;
    RealtimeBuffer<Quote> quote_buffer;

public:
    void subscribe(MarketDataConsumer* consumer) {
        subscribers.push_back(consumer);
    }

    void publish_quote(const Quote& quote) {
        // Add to ring buffer
        quote_buffer.add(quote);

        // Notify all subscribers (lock-free)
        for (auto consumer : subscribers) {
            consumer->on_quote_update(quote);
        }
    }

    void publish_batch(const std::vector<Quote>& quotes) {
        // More efficient than per-quote publishing
        for (const auto& quote : quotes) {
            quote_buffer.add(quote);
        }

        // Single notification
        for (auto consumer : subscribers) {
            consumer->on_quotes_batch(quotes);
        }
    }
};
```

## Step 7: Tick Storage

```cpp
class TickDatabase {
    // Use memory-mapped file for efficiency
    std::fstream tick_file;
    struct TickRecord {
        uint64_t timestamp;
        uint32_t symbol_id;
        uint32_t price;
        uint32_t volume;
        uint8_t flags;
    };

    static constexpr size_t BUFFER_SIZE = 1000000;  // 1M ticks

public:
    void record_tick(const TickRecord& tick) {
        buffer[buffer_pos++] = tick;

        // Flush periodically
        if (buffer_pos >= BUFFER_SIZE) {
            flush_to_disk();
        }
    }

    void flush_to_disk() {
        tick_file.write((const char*)buffer,
                       buffer_pos * sizeof(TickRecord));
        tick_file.flush();
        buffer_pos = 0;
    }

    std::vector<TickRecord> query_range(uint64_t start_ts, uint64_t end_ts) {
        // Use binary search to find range
        std::vector<TickRecord> result;
        // Fetch and return records in time range
        return result;
    }
};
```

## Performance Targets

| Metric | Target | Typical | Optimized |
|--------|--------|---------|-----------|
| **Parse Latency** | <10µs | 5-20µs | 2-5µs |
| **Book Update** | <100ns | 500ns-1µs | 50-100ns |
| **VWAP Latency** | <1µs | 2-5µs | <1µs |
| **Publishing** | <1µs | 5-10µs | 1-2µs |
| **Throughput** | 1M/sec | 500K/sec | 5M/sec |

## Monitoring & Alerts

```cpp
class DataQualityMonitor {
    void check_feed_health() {
        auto now = get_current_time();

        for (auto& [feed_id, state] : feeds) {
            auto time_since_update = now - state.last_update;

            // Alert if no data for 1 second
            if (time_since_update > 1000000000) {
                ALERT("Feed " << feed_id << " stale");
            }

            // Alert if spread abnormally wide
            auto spread = state.book.get_spread();
            if (spread > normal_spread * 3) {
                ALERT("Unusual spread in feed " << feed_id);
            }

            // Alert if gap in sequence
            if (state.last_sequence != expected_sequence) {
                ALERT("Sequence gap in feed " << feed_id);
            }
        }
    }
};
```

## Production Deployment

- [ ] High-speed NIC configured and tested
- [ ] FIX parser handles all exchange formats
- [ ] Multi-feed aggregation tested
- [ ] Order book reconstruction verified
- [ ] VWAP calculation accuracy confirmed
- [ ] Latency histograms monitored
- [ ] Tick database tested under load
- [ ] Feed failure handling tested
- [ ] Monitoring and alerting in place
- [ ] Capacity planning for peak load
