# AMM (Automated Market Maker) Concepts Reference

## What is an AMM?

Automated Market Maker is a protocol where trades execute against liquidity pools, not order books. Prices determined algorithmically based on pool reserves.

### Traditional Order Book vs AMM
```
Order Book:
- Buyers and sellers place orders
- Orders matched at agreed price
- Requires market-making capital
- Examples: Binance, Deribit

AMM:
- Liquidity in pools
- Prices set by algorithm
- Capital from liquidity providers
- Examples: Uniswap, Curve, SushiSwap
```

## Core Formula: Constant Product (x*y=k)

### The Formula
```
x * y = k

Where:
x = reserve of token A (e.g., ETH)
y = reserve of token B (e.g., USDC)
k = constant product (invariant)
```

### How It Works
```
Initial: 100 ETH, 200,000 USDC
k = 100 * 200,000 = 20,000,000

User buys 10 ETH:
New x = 100 + 10 = 110 ETH
New k must equal old k
110 * y = 20,000,000
y = 181,818.18 USDC

User receives: 200,000 - 181,818 = 18,181.82 USDC

Price paid: 18,181.82 USDC / 10 ETH = $1,818.18/ETH
```

### Price Impact Formula
```
Price executed = output / input
Price impact = (expected_output - actual_output) / expected_output

As pool size increases: impact decreases
As trade size increases: impact increases
```

## Liquidity Providers (LPs)

### LP Tokens
```
Deposit 1 ETH + 2000 USDC
Receive LP token (e.g., UNI-V2)
Share of pool: 1 LP token / total LP tokens
When withdrawing: Get proportional share of both
```

### LP Returns

#### Swap Fees
```
Each trade: 0.3% fee (or 0.01%/0.05% depending on tier)
Example:
- Pool: 100 ETH / 200,000 USDC
- Trade: Buy 10 ETH
- Fee taken: 0.3% of input = 0.03 ETH ≈ $54.50
- Fee goes to LPs (reinvested in pool)
```

#### Earn by Transaction Volume
```
APY = (Fee * 365) / TVL

Example:
- Daily volume: $1,000,000
- Fee per tx: 0.3% = $3,000/day
- TVL: $10,000,000
- APY: ($3,000 * 365) / $10,000,000 = 10.95%
```

#### Additional Incentives
```
Governance tokens: Earn UNI, SUSHI, etc.
Boosters: Extra rewards based on gauge voting
```

## Impermanent Loss (IL)

### What is Impermanent Loss?
```
Loss relative to holding tokens independently
Occurs when token prices diverge significantly
```

### IL Calculation
```
IL = (2 * sqrt(price_ratio)) / (1 + price_ratio) - 1

Where price_ratio = new_price / old_price

Examples:
1.25x price change: -0.6% IL
1.5x price change: -2.0% IL
2.0x price change: -5.7% IL
3.0x price change: -13.4% IL
10.0x price change: -84.2% IL
```

### IL vs Fee Income
```
Scenario: 2x price increase
IL loss: -5.7%
Fee APY: 10% (if volume sufficient)

Net return: 10% - 5.7% = +4.3%

If volume insufficient:
Net: 5.7% loss

Break-even: Need sufficient fees to offset IL
```

### When IL Matters
```
High volatility: IL becomes significant
Stablecoin pairs: IL essentially zero
Major token pairs: IL depends on volume
Low volume: IL not offset by fees
```

## Concentrated Liquidity (Uniswap V3)

### Traditional Liquidity
```
Capital spread across all prices: 0 to ∞
Only earns fees in narrow ranges
Capital inefficient
```

### Concentrated Liquidity
```
Capital in specific price range (e.g., $1800-2200)
Earn more fees on same capital
Higher capital efficiency
Risk: Price moves outside range

Example:
V2: 1 ETH + 2000 USDC in pool
V3: Same capital earning 3-4x more fees (in range)
```

### Range Selection
```
Tight range (e.g., $1900-2100):
+ More fees on capital
- Higher chance of moving out of range
- Impermanent loss if it does

Wide range (e.g., $1000-3000):
+ Less likely to move out
- Fewer fees on capital
- Less capital efficient
```

## Multiple Token Pairs

### Standard Pairs (Uniswap V2)
```
Each pair is separate pool
ETH/USDC pair
ETH/DAI pair
DAI/USDC pair

Cross-pair routing: ETH → USDC → DAI (1% fee per hop)
```

### AMM with Multiple Tokens (Balancer)
```
Single pool with multiple tokens
ETH + USDC + DAI + USDT in one pool
Variable weights (not necessarily 50/50)
Example: 50% ETH, 30% USDC, 20% DAI
```

### Benefits of Multi-Token
```
- Single source of liquidity
- Fewer individual pools
- Shared trading fees
- Rebalancing through trading
```

## Types of AMMs

### Constant Product (Uniswap, SushiSwap)
```
Formula: x * y = k
Covers full price range
Simple, proven
High slippage on large trades
```

### Constant Sum (x + y = k)
```
No slippage
But: Price constant (no supply adjustment)
Inefficient for large swaps
Not used
```

### Constant Mean Price
```
(x^w * y^(1-w)) = k
w = weight (not necessarily 0.5)
Handles multiple assets
Used in Balancer
```

### Curve Invariant (Stablecoins)
```
Optimized for stablecoin pairs
Lower slippage within peg
Amplified around equilibrium
Used in Curve Finance
Formula: More complex (A parameter)
```

## Fee Structures

### Fee Tiers (Uniswap V3)
```
0.01%: Stablecoin pairs (USDC/USDT)
0.05%: Stablecoins (DAI/USDC)
0.30%: Standard (most pairs)
1.00%: Volatile pairs

Higher fee: More incentive for LPs
Lower fee: Better execution for traders
```

### Dynamic Fees
```
Some AMMs: Adjust fee based on volatility
Higher volatility: Higher fees
More stable pairs: Lower fees
Incentive alignment
```

## Flash Swaps and Flash Loans

### Flash Swaps (Uniswap V2)
```
Borrow tokens from pool to buy
Execute any actions
Repay with token of different type
Fee: 0.30% of borrowed amount

Use case:
1. Borrow 1000 ETH from pool
2. Sell to different venue
3. Repay with USDC
4. Keep profit
```

### Flash Loan Integration
```
Can be part of complex DeFi transactions
Arbitrage: Buy ETH cheap, sell high, arbitrage
Liquidations: Borrow to liquidate positions
Collateral swapping: No capital needed
```

## Slippage and Execution

### What is Slippage?
```
Difference between expected and actual execution price
Caused by: Price impact of your trade

Large trade: High slippage
Small trade: Low slippage
Thick pool: Low slippage
Thin pool: High slippage
```

### Slippage Protection
```
Set maximum slippage tolerance
If actual slippage > tolerance: Revert transaction

Example:
Expecting 10 ETH for $20,000
Tolerance: 1%
Minimum output: $19,800
If output < $19,800: Reject trade
```

### MEV and Slippage
```
Sandwich attacks: Attacker puts your transaction in middle
Pre-transaction: Buy tokens ahead of your buy
Post-transaction: Sell after your buy
Your cost: Higher slippage

Mitigation: Private pools (MEV protection)
```

## Arbitrage in AMMs

### Classic Arbitrage
```
Price difference between venues
Example:
AMM A: 1 ETH = $1800
AMM B: 1 ETH = $1810

Arbitrageur:
1. Buy 100 ETH on AMM A: $180,000
2. Sell on AMM B: $181,000
3. Profit: $1,000

This equalizes prices across venues
```

### JIT (Just-in-Time) Liquidity
```
Concentrated liquidity enables:
1. Add liquidity to specific range
2. Execute large trade
3. Remove liquidity after

Profit from: Trade fees on single transaction
Trade: Better execution
Enables: New arbitrage strategies
```

## Advanced Features

### Governance and Fee Switch
```
Some protocols: DAO can switch fee switch
Divert protocol fees to treasury
Used for: Development, incentives
Uniswap: Not activated yet
```

### Liquidity Mining
```
Protocols reward: LPs earn governance tokens
Incentive: Bootstrap liquidity
Bonus APY: On top of trading fees
Example: Incentivize new pool launches
```

## Capital Efficiency and Design Choices

### TVL vs Volume
```
Good AMM: Low TVL, High volume
Bad AMM: High TVL, Low volume

Efficiency = Volume / TVL

Uniswap: Most efficient (billions volume, billions TVL)
New AMM: Low efficiency (trying to attract volume)
```

### MEV Considerations
```
Public mempool: Sandwich attacks possible
Dark pools: Hide transactions until settlement
PBS (Proposer-Builder Separation): Reduce MEV
MEV burn: Mechanism to offset negative MEV
```

## Best Practices for Users

### Choosing Pools
```
1. Check trading volume
2. Check TVL and slippage
3. Check fee tier
4. Check pair liquidity
5. Verify contract (official or audit)
```

### Providing Liquidity
```
1. Understand IL risks
2. Start with stablecoin pairs
3. Use tight ranges if experienced
4. Monitor position regularly
5. Have exit plan
```

### Trading Execution
```
1. Use reputable AMM (Uniswap, Curve)
2. Set appropriate slippage (0.1-1%)
3. Consider trade size impact
4. Use limit orders if available
5. Check aggregators (1inch, 0x)
```

---

**Key Takeaways**:
- AMMs replace order books with math (x*y=k)
- LPs earn fees but face impermanent loss
- Concentrated liquidity increases capital efficiency
- Different AMM designs optimize for different use cases
- Slippage increases with trade size and decreases with pool depth
- Arbitrage keeps prices aligned across venues
