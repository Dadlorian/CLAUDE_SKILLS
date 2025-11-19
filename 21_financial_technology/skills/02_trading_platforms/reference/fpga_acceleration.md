# FPGA Acceleration Reference

## FPGA Fundamentals

**FPGA (Field-Programmable Gate Array)**: Reconfigurable hardware for custom logic implementation.

**Advantages in Trading**:
- Deterministic latency (<100ns)
- Parallel processing
- Direct hardware acceleration
- Power efficiency
- Reconfigurability

**Disadvantages**:
- High development cost ($1-5M)
- Expertise requirement (Verilog/VHDL)
- Limited debugging
- Board costs ($10-50K)
- Power consumption

## Hardware Platforms

### Xilinx Platforms
- **Virtex-7**: Previous generation, widely used
- **Kintex-7**: Mid-range, cost-effective
- **UltraScale+**: Latest generation, high performance
- **Alveo**: PCIe accelerator cards for data centers

### Altera (Intel) Platforms
- **Stratix V**: High-end FPGA
- **Cyclone**: Cost-effective option
- **Arria**: Mid-range performance
- **OPALcore**: Proprietary trading FPGA

## Trading-Specific Applications

### 1. Order Book Processing

**Traditional Software**:
```cpp
void process_quote_update(const Quote& quote) {
    // Software latency: 100-500µs

    // Parse message
    auto price = quote.price;
    auto qty = quote.quantity;

    // Update book
    order_book.update(price, qty);

    // Calculate metrics
    auto spread = calculate_spread();
    auto mid = calculate_midpoint();
}
```

**FPGA Implementation**:
```verilog
// Parallel processing
// Latency: 50-100ns

always @(posedge clk) begin
    // 1. Simultaneously parse and validate
    valid_price <= validate_price(data_in);
    price_reg <= extract_price(data_in);
    qty_reg <= extract_qty(data_in);

    // 2. Parallel order book updates
    bids[price_reg] <= qty_reg;  // Direct update (no lock needed)
    asks[price_reg] <= qty_reg;

    // 3. Parallel calculation of metrics
    spread_out <= asks[min_ask] - bids[max_bid];
    mid_out <= (asks[min_ask] + bids[max_bid]) / 2;

    // Output after pipe delay (3-5 cycles)
    out_valid <= valid_price;
    out_spread <= spread_calc;
    out_mid <= mid_calc;
end
```

**Performance Improvement**: 1000-5000x latency reduction

### 2. FIX Protocol Parsing

**Traditional Software**:
```cpp
// Parse FIX message
char* parse_fix_message(const char* msg) {
    // Scan for SOH delimiter
    // Extract fields manually
    // Convert types
    // Latency: 5-20µs (with optimizations)
}
```

**FPGA Pipeline**:
```verilog
// Parallel field extraction
// Hardware state machine
module fix_parser (
    input clk,
    input [7:0] data_in,  // 1 byte/cycle

    output [31:0] order_id,
    output [15:0] price,
    output [31:0] qty,
    output valid
);

// Parallel extraction:
// State 0: Scan for BeginString
// State 1: Extract message type
// State 2-5: Extract key fields in parallel
// Total: 8-12 cycles for complete parse

always @(posedge clk) begin
    if (data_in == SOH) begin  // Field delimiter detected
        // Capture previous field (3 bytes for 35=D pattern)
        case (state)
            0: order_id <= temp_val;
            1: msg_type <= temp_val;
            2: price <= temp_val;
            3: qty <= temp_val;
        endcase
        temp_val <= 0;
        state <= state + 1;
    end else begin
        temp_val <= temp_val * 10 + (data_in - '0');
    end
end
```

**Performance Improvement**: 100-500x faster parsing

### 3. Matching Engine

**Software Matching** (O(log n) per order):
```cpp
struct MatchingEngine {
    std::map<double, std::vector<Order>> bids;
    std::map<double, std::vector<Order>> asks;

    void match_order(Order& order) {
        auto& target_side = order.side == BUY ? asks : bids;

        while (order.remaining_qty > 0 && !target_side.empty()) {
            auto best_level = target_side.begin();

            for (auto& ctr_order : best_level->second) {
                auto match_qty = min(order.remaining_qty,
                                     ctr_order.remaining_qty);
                // Execute trade
                execute_trade(order, ctr_order, match_qty);
                // Latency: 10-50µs per order
            }

            if (best_level->second.empty()) {
                target_side.erase(best_level);
            }
        }
    }
};
```

**FPGA Matching** (Direct hardware):
```verilog
// Dual-ported RAM for order book
// Simultaneous bid/ask updates
// Direct comparison logic

module matching_engine (
    input clk,
    input [31:0] new_order,

    output [15:0] match_price,
    output [31:0] match_qty,
    output valid
);

// Parallel matching:
// 1. Extract new order details (Cycle 1)
// 2. Look up best opposing side (Cycle 2, direct RAM read)
// 3. Compare prices for match (Cycle 3)
// 4. Calculate trade qty (Cycle 4)
// 5. Update both sides (Cycle 5)
// Total: 5 cycles = 50ns @ 100MHz

always @(posedge clk) begin
    // Direct hardware matching
    // No software overhead
    // Latency: <100ns for complete match + update
end
```

**Performance**: 10,000+ matches/second, <100ns latency

### 4. Risk Checking

**Software Risk Check**:
```cpp
bool check_risk_limits(const Order& order) {
    // Check exposure
    auto new_notional = current_notional + (order.qty * order.price);
    if (new_notional > risk_limit) return false;

    // Check position limit
    auto new_position = current_position + order.qty;
    if (abs(new_position) > position_limit) return false;

    // Check Greeks
    auto new_delta = current_delta + (order.qty * delta_per_share);
    if (abs(new_delta) > delta_limit) return false;

    // Latency: 2-5µs
    return true;
}
```

**FPGA Risk Check**:
```verilog
// Parallel limit checking
module risk_checker (
    input [63:0] order_info,
    input [63:0] current_state,

    output pass,
    output fail_reason
);

// Parallel checks:
// Check1: notional vs limit (Cycle 1)
// Check2: position vs limit (Cycle 1, parallel)
// Check3: delta vs limit (Cycle 1, parallel)
// All comparisons simultaneous
// Output valid: Cycle 2 (20ns @ 100MHz)
```

**Performance**: <100ns vs 2-5µs (25-50x faster)

## FPGA Development Flow

### 1. RTL Development
```verilog
module trading_accelerator (
    input clk,
    input [7:0] data_in,
    input valid_in,

    output [31:0] result_out,
    output valid_out
);

// Register all inputs
reg [7:0] data_reg;
reg valid_reg;

always @(posedge clk) begin
    data_reg <= data_in;
    valid_reg <= valid_in;
end

// Pipelined processing
always @(posedge clk) begin
    // Stage 1: Input parsing
    // Stage 2: Processing
    // Stage 3: Output formatting
end

endmodule
```

### 2. Simulation
- ModelSim, VCS, or Vivado Simulator
- Functional verification
- Timing simulation
- Throughput testing

### 3. Synthesis
- Convert RTL to gate-level netlist
- Timing analysis
- Resource utilization check
- Optimization passes

### 4. P&R (Place & Route)
- Map design to FPGA resources
- Route signals
- Timing closure
- Bit stream generation

### 5. Testing & Deployment
- Hardware testing
- Integration testing
- Production deployment
- Monitoring & updates

## Performance Characteristics

### Latency Comparison

| Component | Software | FPGA | Improvement |
|-----------|----------|------|-------------|
| **FIX Parse** | 5-20µs | 100-200ns | 25-200x |
| **Order Book Update** | 100-500ns | 50-100ns | 1-10x |
| **Risk Check** | 2-5µs | 100-200ns | 20-50x |
| **Match Order** | 10-50µs | 100-500ns | 20-100x |
| **Total Order Process** | 50-100µs | 500-1000ns | 50-200x |

### Throughput Comparison

| Metric | Software | FPGA |
|--------|----------|------|
| **Orders/sec** | 100K | 1M+ |
| **Quotes/sec** | 100K | 1M+ |
| **Matches/sec** | 10K | 100K+ |
| **Concurrent Orders** | 10K | 100K+ |

## Power Efficiency

### Hardware Utilization
```
Modern Trading FPGA:
- Clock: 100-200 MHz
- Logic cells: 100K-500K
- Memory: 10-50MB
- Power consumption: 50-200W
- Power per operation: 0.1-1µJ

Equivalent Software:
- CPU: 3-5 GHz
- Cores: 8-16
- Power consumption: 100-500W
- Power per operation: 1-10µJ

FPGA Advantage: 10-100x power efficiency
```

## Integration Challenges

### PCIe Bandwidth
```
PCIe Gen 3: 16 lanes = 16 GB/s
Throughput per quote: 50-100 bytes
Maximum quotes/sec: 160M-320M
Usually not bottleneck for trading
```

### Host Integration
```
Data Path:
1. Quote arrives (100ns)
2. Transmitted to FPGA via PCIe
3. FPGA processes (100-500ns)
4. Results transmitted back (100ns)
5. Software consumed

Total: 1-2µs (mostly PCIe)
```

## Cost Analysis

### Development Cost
- **Engineering**: $500K-$2M (team for 1-2 years)
- **Tools**: $50-100K (EDA software licenses)
- **Hardware**: $20-50K (development boards, test equipment)
- **Integration**: $100-500K (software integration, testing)
- **Total**: $1-5M

### Per-Unit Cost
- **FPGA Board**: $10-30K
- **Integration**: $5-10K
- **Software licensing**: $1-5K
- **Total**: $16-45K per system

### Payback Period
```
Benefit per system per year:
= Revenue increase + Cost savings
= (Better execution × Volume × Margin) + (Latency advantage value)

Example:
- 1M shares/day trading
- 0.5 bps execution improvement
- $50/share value
- Annual benefit = 1M × 250 × $0.0005 × $50 = $6.25M

ROI: $6.25M / $45K ≈ 140x (payback < 1 month)
```

## Production Deployment

### Reliability
- **Uptime**: 99.99% (proven in production)
- **Thermal**: Fan-cooled, standard data center
- **Failover**: Dual FPGA systems for critical paths
- **Recovery**: Fast bitstream reload

### Monitoring
- **Temperature**: Continuous monitoring
- **Performance**: Latency tracking
- **Errors**: Parity checking, ECC
- **Alerts**: Real-time notification

## Best Practices

1. **Profile First**: Identify actual bottlenecks
2. **Start Small**: Accelerate critical path only
3. **Prototype**: Use high-level synthesis initially
4. **Test Thoroughly**: Hardware is harder to fix
5. **Maintain**: Keep RTL documented and versioned
6. **Monitor**: Track real-world performance
7. **Plan for Evolution**: Design for future upgrades
