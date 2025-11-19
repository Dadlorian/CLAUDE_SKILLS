# Liquidity Pools Reference

## What are Liquidity Pools?

Smart contract-based repositories of assets enabling automated trading. Users deposit token pairs, earn fees from trades, and take on impermanent loss risk.

## Pool Architecture

### Basic Pool Structure
```
Pool: ETH/USDC
Reserve X: 100 ETH
Reserve Y: 200,000 USDC
Total LP Value: 300,000 USDC (assuming $1500/ETH)
LP Tokens: 1,000,000 issued
Exchange Rate: 0.003 ETH per USDC
```

### LP Token Mechanics
```
Initial deposit: 1 ETH + 2000 USDC
Pool total: 100 ETH + 200,000 USDC
User share: 1 ETH / 100 ETH = 1%
User LP tokens: 1% of 1,000,000 = 10,000 tokens
```

### Withdrawal
```
User holds: 10,000 LP tokens (out of 1,000,000)
Pool now: 150 ETH + 300,000 USDC (grew from fees)
User receives: (10,000 / 1,000,000) of each = 1.5 ETH + 3,000 USDC
Profit: 0.5 ETH + 1,000 USDC from trading fees
```

## Types of Pools

### Spot Pools (Standard)
```
Uniswap V2, V3
SushiSwap
Curve

Characteristics:
- Two or more tokens
- Prices determined by reserves
- Immediate settlement
- Trading fees: 0.01% to 1%
```

### Perpetual Futures Pools
```
Synthetic perpetual contracts
Traders bet on price movements (no expiry)
Funding rates: Mechanism to keep price near spot
Example: dYdX, Aevo

Characteristics:
- Leverage trading
- Mark price vs index price
- Funding rate payments
- More complex mechanism
```

### Options Pools
```
Sell or buy options
Strike prices and expirations
Pools manage liquidity
Example: Ribbon Finance, Dopex

Characteristics:
- Defined expiry
- Strike-dependent returns
- Volatility-dependent pricing
- Hedging tools
```

## Pool Design Patterns

### Uniswap V2 Style (Equal Distribution)
```
Reserve X: 100 ETH
Reserve Y: 200,000 USDC
Product: 100 * 200,000 = 20,000,000 (constant)
Weight: 50% ETH, 50% USDC
Fee: 0.3%

Any trade must maintain: x * y = k
```

### Balancer Pools (Variable Weights)
```
Reserve ETH: 40% weight
Reserve USDC: 30% weight
Reserve DAI: 20% weight
Reserve USDT: 10% weight

Multi-token pool
Weighted AMM formula
```

### Curve Pools (Stablecoins)
```
Designed for stablecoins (low volatility)
Concentrated liquidity around peg
Lower slippage within narrow price range
Formula: Optimized for stable pairs

Example:
USDC + USDT + DAI pool
All worth ~$1
Slippage: Minimal until major peg break
```

### Concentrated Liquidity (Uniswap V3)
```
User selects price range
Example: $1800-$2200
All capital within range
Fees concentrated in range
Outside range: No earnings

Trade-offs:
+ More fees in range
- Impermanent loss if price exits
- Management required
```

## Liquidity Mining

### Incentive Structure
```
Base rewards: Trading fees earned naturally
Governance rewards: Protocol issues tokens
Total APY: Fees + governance rewards

Example:
USDC/USDT in Curve
Trading fees: 3% APY
CRV rewards: 20% APY
Total: 23% APY
```

### Token Distribution
```
Early pools: Higher rewards (bootstrap)
Later pools: Lower rewards
Total emission: Decreases over time

Phase 1 (0-26 weeks): Max rewards
Phase 2 (26-52 weeks): 75% rewards
Phase 3 (52+ weeks): 50% rewards
```

## Fee Structures

### Trading Fees
```
Uniswap V2: 0.30% on all pairs
Uniswap V3: 0.01%, 0.05%, 0.30%, 1.00%
Curve: 0.04% - 0.40%
SushiSwap: 0.25% - 0.30%

Distributed to: LP holders (pro-rata)
```

### Protocol Fees
```
Some protocols: Take percentage of fees
Uniswap: Option to enable 0.05% fee (not active)
Curve: Collects small % for DAO
SushiSwap: 0.05% to dev fund

Used for: Development, incentives, buyback
```

### Governance Fees
```
Some tokens: Earn portion of protocol fees
MKR: Receives stability fees
UNI: Not yet (fee switch off)
SUSHI: Receives XSushi rewards
```

## Pool Health Metrics

### TVL (Total Value Locked)
```
Sum of all assets in pool
Example: $1M TVL = $500k ETH + $500k USDC

Indicator: Liquidity depth
Higher TVL: Lower slippage
Lower TVL: Higher slippage, less sustainable
```

### Volume
```
Daily or monthly trading volume
Indicates usage level
More volume: More fees for LPs

Volume / TVL ratio:
High: Efficient capital use
Low: Capital-inefficient
```

### 24h Volume/TVL
```
Metrics of efficiency:
1.0 = Vol equals TVL in day (very healthy)
0.1 = Vol is 10% of TVL (moderately active)
0.01 = Vol is 1% of TVL (low activity)

Pools with ratio > 1: Highly efficient
Pools with ratio < 0.1: Difficult for LPs to profit
```

### Slippage
```
Slippage = (expected_output - actual_output) / expected_output

Deep pool: 1000 ETH
Buy 1 ETH: Slippage ~0.01%
Buy 10 ETH: Slippage ~0.1%
Buy 100 ETH: Slippage ~1%

Thin pool: 10 ETH
Buy 1 ETH: Slippage ~10%
Buy 10 ETH: Impossible (exceeds pool)
```

## Liquidity Pool Risks

### Smart Contract Risk
```
Code bugs in pool contract
Upgradeable pools: Admin risk
Newly deployed: Higher risk

Examples:
- Curve: Math issues (fixed)
- Uniswap: Very few bugs (trusted)
- New protocols: Higher risk

Mitigation: Audit, time in production, TVL
```

### Impermanent Loss
```
Loss from price divergence
More severe with:
- Higher divergence
- Lower transaction volume
- Concentrated liquidity

Mitigation:
- Stablecoin pairs (no IL)
- High volume pairs
- Fees offset IL
```

### Slippage/Sandwich Attacks
```
Attackers put your tx in middle
Pre-tx: Buy ahead of you (front-run)
Post-tx: Sell after you (back-run)
Your cost: Higher slippage

Defense:
- Set slippage limits
- Use MEV-protected pools
- Off-peak trading
```

### Oracle Manipulation
```
Flash loan attack on price:
1. Borrow large amount from lending protocol
2. Dump on AMM
3. Price crashes
4. Execute exploit using false price
5. Repay flash loan + profit

Defense:
- Time-weighted price oracles (TWAP)
- Multiple oracle sources
- Price circuit breakers
```

### Withdrawal Risk (Bridges)
```
Cross-chain pools: Bridge risk
Asset on sidechain: Depends on bridge security
If bridge fails: Assets stuck

Examples:
- Polygon bridge: Highly secure
- New L2 bridges: Higher risk
- Private bridges: Requires trust
```

## Pool Selection

### For LP Providers

#### Safe Pools
```
Characteristics:
- Established protocol (Uniswap, Curve)
- High TVL ($100M+)
- Stablecoin pairs
- Audited code
- Low leverage/complexity

APY: 2-5%
Risk: Very low

Examples: USDC/USDT on Curve
```

#### Moderate Risk
```
Characteristics:
- Established protocol
- Major token pairs (ETH, LINK)
- Moderate TVL ($10M-100M)
- Some fee incentives

APY: 5-20%
Risk: Low-moderate

Examples: ETH/USDC on Uniswap V3
```

#### Higher Risk
```
Characteristics:
- New protocols
- Alt token pairs
- High APY (50%+)
- Unproven mechanisms

APY: 50-200%+
Risk: High

Examples: New token launches, emerging DeFi
```

## Pool Strategies

### Balanced Position
```
Equal dollar amount in both tokens
Example: 1 ETH + 2000 USDC
50% pool in ETH, 50% in USDC
If price stable: Earn only fees
If price moves: IL applies
```

### Asymmetric Position
```
More of one asset to bet on direction
Example: 0.5 ETH + 4000 USDC
25% ETH, 75% USDC
Bet: USDC > ETH (expect ETH to fall or underperform)
Less IL if correct: More profit if right
```

### Range Farming (V3)
```
Concentrate liquidity in price range
Earn more fees on less capital
Higher capital efficiency
Management required
```

### Market Making
```
Provide liquidity actively
Adjust ranges based on price movement
Earn spreads
Professional strategy
```

## Pool Creation

### Deployment Steps
```
1. Select two tokens
2. Initial liquidity: Seed pool
3. Choose fee tier (if applicable)
4. Deploy to network
5. Market: Attract more LPs
```

### Considerations
```
Token selection: Demand for pair
Fee tier: Should match volatility
Initial capital: Need sufficient liquidity
Marketing: Get LPs to the pool
Rewards: Consider incentivizing LPs
```

## Advanced Pools

### Stable Swap Pools (Curve)
```
Specialized for correlated assets
Formula: Optimized for stable prices
Lower slippage: Within stable range
Better returns: On stablecoin pairs

Best for: Stablecoins, wrapped tokens
APY: 3-10% typical
```

### Concentrated Liquidity AMM
```
Uniswap V3 style: LPs choose ranges
Capital efficiency: 4000x in tight ranges
Management: Requires monitoring
Complexity: Medium-high
```

### Multi-Token Pools
```
Balancer, Curve: 3+ token pools
Single pool: Multiple assets
Rebalancing: Automatic via trading
Benefits: Shared liquidity, lower fees
```

---

**Key Takeaways**:
- Liquidity pools enable automated trading
- LPs earn fees but face impermanent loss
- Pool design affects capital efficiency and risk
- Multiple pool types for different use cases
- Deep pools have lower slippage
- Risk management is critical for LP success
- Stablecoin pools lowest risk, lowest reward
