# Yield Farming Reference

## What is Yield Farming?

Strategy to maximize returns on cryptocurrency holdings by participating in DeFi protocols. Earn returns through:
- Trading fees (swap commissions)
- Protocol rewards (governance tokens)
- Interest rates (lending)
- Liquidity mining bonuses
- Combination of above

## Basic Yield Farming

### LP Fee Farming
```
Action: Deposit tokens to AMM liquidity pool
Earn: Trading fees from swaps
APY: 0-50%+ depending on volume

Example:
Pool: ETH/USDC
Deposit: 1 ETH + 2000 USDC
Daily volume: 1M
Fee: 0.3%
Daily fees: 3000 USDC * 0.3% = 9 USDC/day
Annual: 9 * 365 = 3,285 USDC ≈ 1.6% APY
```

### Liquidity Mining
```
Protocol: Issues governance tokens to LPs
Beyond trading fees: Extra rewards
APY: Often 50-200%+

Example:
Pool: NEW/USDC
Protocol rewards: 1000 NEW tokens/day
NEW price: $1
TVL in pool: $500,000
Extra APY: (1000 * 365) / 500,000 = 73% APY
```

### Lending Interest
```
Action: Deposit token to lending protocol
Earn: Interest on deposits
APY: 2-10% typical (depends on utilization)

Example:
Deposit: 1000 USDC to Aave
Rate: 5% APY
Annual: 1000 * 0.05 = 50 USDC
```

## Leveraged Yield Farming

### Process
```
1. Deposit initial collateral: 10 ETH
2. Borrow against collateral: 50 ETH
3. Deposit all 60 ETH to lending pool
4. Earn interest on 60 ETH
5. Pay interest on 50 ETH borrowed
6. Keep the spread

Leverage: 6x
Risk: If price drops, liquidation
Upside: 6x gains
Downside: Losses amplified
```

### Calculation
```
Supplied: 60 ETH
Supplied rate: 3% APY
Supply income: 60 * 0.03 = 1.8 ETH/year

Borrowed: 50 ETH
Borrow rate: 5% APY
Borrow cost: 50 * 0.05 = 2.5 ETH/year

Net: 1.8 - 2.5 = -0.7 ETH/year (LOSS!)

Don't use if supply rate < borrow rate
Need asset appreciation or extra rewards
```

## Yield Farming Strategies

### Single Token Farming
```
Deposit: 1000 USDC
Earn: 5% interest
APY: 5%

Best for: Low risk, stable returns
Suitable for: Risk-averse investors
```

### LP Token Farming (AMM Fees)
```
Deposit: 1 ETH + 2000 USDC (LP token)
Earn:
  - Trading fees: 1.5% APY
  - Rewards: 50 USDC/day (governance)
APY: 50+ USDC/day bonus (impermanent loss offset)

Best for: Active management, monitoring
Risk: Impermanent loss
```

### Leveraged Yield Farming
```
Deposit: 10 ETH
Borrow: 50 USDC
Use 60 ETH to earn
APY: 20%+ possible (with risk)

Best for: Experienced farmers
Risk: High (liquidation risk)
Upside: Amplified returns
```

### Delta-Neutral Farming
```
Same asset on both sides:
1. Supply 100 ETH to Aave (earn interest)
2. Borrow 100 ETH from Aave (pay interest)
3. LP both on Uniswap (earn fees)
4. Net: 0 market exposure, earn fees + spread

Profit from: Fee income - spread
APY: 5-15%
Risk: Minimal (no market exposure)
```

### Cross-Chain Farming
```
1. Wrap ETH from Ethereum to Polygon
2. Farm on Polygon (higher APY)
3. Earn rewards in Polygon tokens
4. Wrap back to Ethereum

Considerations:
- Bridge risk
- Wrapping fees
- Price impact converting back
- Tax implications
```

## Yield Farming Pools

### Popular Pools by Type

#### Stablecoin Pools (High APY)
```
Curve: USDC/USDT/DAI
- Very low IL (prices track $1)
- Fees on high volume
- Boosted via CRV rewards

Convex: Boosts Curve yield
- Leverage CRV yield
- Lock CVX for boost
- 10-30% APY typical
```

#### Major Pair Pools (Moderate APY)
```
Uniswap: ETH/USDC, ETH/DAI, etc.
- Trading fees: 0.05% to 1%
- Volume dependent
- 3-10% APY typical

Curve: Asset-type pairs
- Similar pairs
- Higher fee tier
```

#### Volatile Pair Pools (Variable APY)
```
New token pairs: Often highest APY
- New token rewards
- High risk
- 100%+ APY possible initially
- APY drops as rewards end
```

## Governance Token Rewards

### Token Emission Schedule
```
Protocol launches with high emission
Example: Uniswap V3
- High rewards initially
- Incentivize early LPs
- Emission reduces over time
```

### APY Calculation with Token Rewards
```
Base APY: Trading fees = 2%
Token rewards: 100 UNI/day = $2000/day
TVL: $1M
Token APY: ($2000 * 365) / $1M = 73%
Total APY: 2% + 73% = 75%
```

### Token Value Risk
```
Earning tokens worth $X today
Future value uncertain
If token price drops: APY drops
If token price rises: APY looks better in hindsight
```

## Gas Optimization

### Compounding Frequency
```
Frequent compounds: Better returns but more fees
Rare compounds: Fewer fees but lower returns

Example:
Earn: 10 USDC/day
Gas: 50 USDC per transaction
Daily compound: Lose 50 USDC in gas
Better: Compound weekly (save 300 USDC in gas)

Rule of thumb:
Compound when earned > 5x gas cost
```

### Batch Transactions
```
Multiple actions in single transaction:
- Claim rewards
- Swap rewards
- Reinvest
Single gas cost: Save 3x
Less frequent manual intervention
```

### Layer 2 Farming
```
Costs: 100x lower than Ethereum
Compounds economical: Do daily
Downside: Smaller pools, less liquidity
Strategy: Farm on L2, use bridges
```

## Risk Factors

### Impermanent Loss (IL)
```
Affects: LP token farming
Caused by: Price divergence of pair
Mitigation:
- Use stablecoin pairs (no IL)
- Tight concentration (V3)
- Monitor and rebalance
- Choose high-volume pools
```

### Smart Contract Risk
```
Affects: All farming
Unaudited protocols: Highest risk
New protocols: Higher risk
Established: Lower risk

Examples of failures:
- Curve: Smart contract bugs (recovered)
- Yearn: Strategist exploit
- Flash loan attacks on new pools
```

### Liquidation Risk (Leverage)
```
Affects: Leveraged farming
Trigger: Price drops below liquidation threshold
Mitigation:
- Keep health factor > 1.5
- Monitor price changes
- Reduce leverage when volatile
- Set alerts
```

### Token Value Risk
```
Affects: All reward farming
Issue: Governance token may drop in value
Solutions:
- Harvest and sell rewards regularly
- Use stablecoin pairs where possible
- Diversify protocols
- Exit before rewards end
```

### Impermanent Loss from Leverage
```
Leverage amplifies IL
2x leverage: 2x IL loss
Example:
2x leverage farming
1.5x price increase
IL: -2%
IL * 2 = -4% with leverage
```

## DeFi Aggregators

### Functions
```
1. Find best APY across protocols
2. Execute multiple transactions
3. Rebalance automatically
4. Minimize gas costs
```

### Examples
```
Yearn Finance: Automated vaults
- Strategies manage deployment
- Rebalance automatically
- Fee: 2% management + 20% performance

Convex: Boosts Curve yield
- Lock CVX for rewards
- Delegate to Convex
- Earn boosted APY

Beefy: Multi-chain vaults
- Auto-compounds
- Supports 20+ blockchains
```

## Advanced Strategies

### Triangular Arbitrage
```
1. Farm on AMM A, earn token X
2. Swap X to Y on AMM B
3. Swap Y to Z on AMM C
4. Swap Z back to X on AMM D
5. Collect spread

Requires: Price inefficiencies
Tools: Arbitrage bots
APY: Varies wildly
```

### MEV Optimization
```
Transaction ordering: Affects slippage
Sandwich attacks: Steal MEV from you
Solutions:
- Private pools (MEV burn)
- Flashbots (MEV share)
- Decentralized sequencers

Can improve APY: 1-5%
```

### Governance Farming
```
Earn governance tokens
Vote for rewards
Use vote-escrow mechanism
Lock tokens: Higher voting power
APY: From delegation + governance

Example:
Curve: Lock CRV to veCRV
Vote: Direct 2.5x fee boost to choice
Earn: 50%+ APY on boost
```

## Exit Strategies

### When to Farm
```
APY > risk cost: Farm
APY < risk cost: Don't farm

Costs:
- Smart contract risk
- IL risk
- Liquidation risk
- Gas costs
- Tax implications
```

### When to Exit
```
Red flags:
- Protocol hack/exploit
- Governance attack
- Token devaluation
- APY collapse (rewards end)
- Better opportunities elsewhere
```

### Tax Implications
```
Farming = Creating taxable events:
- Claiming rewards: Taxable
- Swapping tokens: Capital gain/loss
- Impermanent loss: May be deductible (depends on jurisdiction)
- Interest income: Ordinary income

Advice: Consult tax professional
Keep records: All transactions
```

## Monitoring and Tools

### Metrics to Monitor
```
APY: Current and projected
TVL: Total locked, indicates sustainability
Rewards: Amount and vesting schedule
IL: Current position IL
Gas costs: Factor in compounding frequency
Liquidation price: For leveraged positions
```

### Platforms
```
Apy.vision: Compare APYs
Defi Llama: TVL and analytics
Yearn: Vault strategies
Zapper: Track positions
Etherscan: Verify contracts
```

---

**Key Takeaways**:
- Yield farming combines multiple income sources
- Returns come with proportional risks
- Leverage amplifies both gains and losses
- Gas costs critical on mainnet, less so on L2
- Smart contract risk is real and underpriced
- Exit plan is as important as entry
- Diversification across protocols reduces risk
