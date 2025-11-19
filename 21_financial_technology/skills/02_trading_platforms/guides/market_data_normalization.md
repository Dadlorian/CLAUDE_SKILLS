# Market Data Normalization Guide

## Multi-Exchange Normalization

```cpp
struct NormalizedQuote {
    uint64_t timestamp;      // Unified timestamp (ns)
    uint32_t security_id;    // Internal security ID
    uint32_t best_bid;       // Fixed-point: multiply by 10000
    uint32_t best_ask;
    uint32_t bid_volume;
    uint32_t ask_volume;
    uint8_t exchange_id;     // 0=NYSE, 1=NASDAQ, etc.
};

class MarketDataNormalizer {
    std::map<std::string, uint32_t> symbol_to_id;  // Symbol -> ID
    std::map<uint32_t, std::string> id_to_symbol;  // ID -> Symbol

    NormalizedQuote normalize(const ExchangeQuote& quote) {
        NormalizedQuote normalized;
        normalized.timestamp = rdtsc();
        normalized.security_id = symbol_to_id[quote.symbol];
        normalized.best_bid = quote.bid_price * 10000;  // Convert to fixed-point
        normalized.best_ask = quote.ask_price * 10000;
        normalized.bid_volume = quote.bid_qty;
        normalized.ask_volume = quote.ask_qty;
        normalized.exchange_id = get_exchange_id(quote.exchange);
        return normalized;
    }

    void adjust_for_corporate_actions(const CorporateAction& action) {
        // Handle splits, dividends, etc.
        switch (action.type) {
            case STOCK_SPLIT:
                // Adjust all historical prices
                split_factor = action.new_ratio / action.old_ratio;
                adjust_prices(split_factor);
                break;
            case DIVIDEND:
                // Add dividend impact to prices
                dividend_adjustment = action.dividend_amount;
                break;
        }
    }
};
