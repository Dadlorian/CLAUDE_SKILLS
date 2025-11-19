// High-performance matching engine
#include <map>
#include <vector>
#include <atomic>

struct Order {
    uint64_t order_id;
    uint32_t price;
    uint32_t quantity;
    uint32_t remaining;
    uint8_t side;  // 0=Buy, 1=Sell
};

struct Trade {
    uint64_t buyer_order_id;
    uint64_t seller_order_id;
    uint32_t price;
    uint32_t quantity;
};

class MatchingEngine {
private:
    std::map<uint32_t, std::vector<Order>> buy_book;   // Descending price
    std::map<uint32_t, std::vector<Order>> sell_book;  // Ascending price
    std::vector<Trade> trades;
    std::atomic<uint64_t> trade_count{0};

public:
    std::vector<Trade> match_order(const Order& incoming) {
        std::vector<Trade> new_trades;

        if (incoming.side == 0) {  // Buy order
            match_against_sells(incoming, new_trades);
        } else {  // Sell order
            match_against_buys(incoming, new_trades);
        }

        // Add remaining to book
        if (incoming.remaining > 0) {
            add_to_book(incoming);
        }

        return new_trades;
    }

private:
    void match_against_sells(const Order& buy_order,
                            std::vector<Trade>& new_trades) {
        Order remaining = buy_order;

        // Match from lowest asks upward
        for (auto& [price, orders] : sell_book) {
            if (price > buy_order.price) break;  // No match

            for (auto& sell_order : orders) {
                if (remaining.remaining == 0) break;

                uint32_t match_qty = std::min(remaining.remaining,
                                            sell_order.remaining);

                Trade trade{
                    remaining.order_id,
                    sell_order.order_id,
                    price,
                    match_qty
                };

                new_trades.push_back(trade);
                remaining.remaining -= match_qty;
                sell_order.remaining -= match_qty;
            }

            // Remove filled orders
            orders.erase(
                std::remove_if(orders.begin(), orders.end(),
                            [](const Order& o) { return o.remaining == 0; }),
                orders.end()
            );
        }
    }

    void match_against_buys(const Order& sell_order,
                           std::vector<Trade>& new_trades) {
        // Similar logic but matching against buy book
    }

    void add_to_book(const Order& order) {
        if (order.side == 0) {
            buy_book[order.price].push_back(order);
        } else {
            sell_book[order.price].push_back(order);
        }
    }
};
