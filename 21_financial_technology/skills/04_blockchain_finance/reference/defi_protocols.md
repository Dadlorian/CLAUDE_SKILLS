# DeFi Protocols Reference

## DeFi Overview

Decentralized Finance (DeFi) refers to financial services built on blockchain networks, operating without traditional intermediaries like banks. DeFi protocols enable lending, borrowing, trading, and yield generation through smart contracts.

### Core Principles
1. **Non-Custodial**: Users maintain control of assets
2. **Permissionless**: Open access without KYC/approval
3. **Transparent**: All transactions and code visible
4. **Composable**: Protocols interact seamlessly
5. **Decentralized**: No single point of control

## Decentralized Exchanges (DEXs)

### Automated Market Makers (AMMs)

#### Constant Product Formula (Uniswap V2)
```
x * y = k

Where:
x = reserve of token A
y = reserve of token B
k = constant product

When trading A for B:
newX = x + amountIn
newY = k / newX
amountOut = y - newY
```

#### Price Impact
```
Price impact = amountOut / expectedOut

As pool depth increases: impact decreases
As swap size increases: impact increases
```

#### Slippage Protection
```
Minimum output = expectedOutput * (1 - slippageTolerance)
Require(amountOut >= minimumOutput)
```

### Order Book DEXs
- Traditional limit order books
- Matching engines
- Better capital efficiency than AMMs
- Examples: dYdX (V4), 0x Protocol

### Liquidity Pools

#### Adding Liquidity
```
If pool has: 100 TokenA, 10 TokenB
New provider adds: 10 TokenA, 1 TokenB

Share = contributed / existing
LP tokens = share * totalLPTokens
```

#### Removing Liquidity
```
User burns LP tokens
Receives proportional share of both tokens
Earns fees accumulated since entry
```

#### Impermanent Loss (IL)
```
IL occurs when token prices diverge significantly

IL % = (2 * sqrt(price_ratio)) / (1 + price_ratio) - 1

Example:
Initial: 100 ETH + 100k DAI
Price change: ETH 2x
IL loss: -5.7% vs holding

Offset by trading fees if volume sufficient
```

## Lending & Borrowing Protocols

### Protocol Mechanics

#### Supply Side
```solidity
User deposits: USDC
Receives: cUSDC (compound token)
Earns interest: Continuously accrues

Interest = principal * rate * time
```

#### Borrow Side
```solidity
User borrows: USDC (up to LTV)
Collateral required: ETH
Borrow limit: ETH value * LTV

Liquidation threshold = collateral value * LT
If debt > threshold: Liquidatable
```

### Risk Parameters

#### Loan-to-Value (LTV)
```
LTV = borrowed amount / collateral value
LTV limit set per asset
Lower LTV = safer for protocol
Higher LTV = better for borrower

Typical: 50-80% for major assets
```

#### Liquidation Ratio (LR)
```
LR = collateral value * liquidation threshold
If debt > LR: Asset liquidated

Liquidation incentive: 5-15%
Liquidators profit from discounted collateral
```

### Interest Rate Models

#### Utilization-Based Model
```
interest_rate = baseRate + (utilizationRate * slope1)

If utilization > kink:
interest_rate = baseRate + (kink * slope1) + ((utilization - kink) * slope2)

Utilization = total_borrowed / total_supplied
```

### Examples
- **Aave**: Multi-collateral, variable/stable rates
- **Compound**: cToken model, algorithmic rates
- **MakerDAO**: Over-collateralized debt positions

## Yield Farming

### Mechanisms

#### Single Asset Farming
```
Stake token
Earn: Governance tokens + protocol fees
APY varies with TVL and emission schedule
```

#### LP Token Farming
```
Deposit: LP tokens (from pool)
Earn:
  - Swap fees from trades
  - Farming incentives (governance tokens)
  - Sometimes bonus rewards
```

#### Yield Optimization
```
Rebalance frequently to maximize returns
Compound rewards
Minimize slippage and gas costs
```

### Risk Factors
- Smart contract risk
- Impermanent loss (for LP farming)
- Governance token volatility
- Liquidity risk
- Oracle manipulation

## Stablecoins

### Collateralized Stablecoins

#### Over-Collateralized (MakerDAO)
```
Deposit: 150 ETH
Borrow: 100 DAI
Collateral Ratio: 150%

Benefits: Maintains peg through collateral
Risks: Requires liquidation mechanisms
```

#### Under-Collateralized (Algorithmic)
```
Rely on incentive mechanisms
No backing collateral
Pure stabilization through economics

Example: Terra Luna (failed)
```

### Algorithmic Stablecoins
```
Supply adjustments based on price
Mint when price > $1
Burn when price < $1

Challenges: Maintaining peg, death spirals
```

### Central Bank Digital Currency (CBDC) Stablecoins
- USDC, USDT: Fiat-backed
- 1:1 with underlying currency
- Redemption guarantees
- Most reliable, still centralized

## Flash Loans

### Mechanics
```
1. Borrow large amount without collateral
2. Must repay within same transaction
3. Can use borrowed amount for arbitrage
4. Includes 0.09% fee

[borrow] → [use funds] → [repay + fee]
All in one atomic transaction
```

### Use Cases
- Arbitrage
- Liquidations
- Refinancing
- Collateral swapping

### Risk: Flash Loan Attacks
```
Attack: Borrow large amount
Manipulate price via borrowed funds
Liquidate victim's position
Repay loan + profit difference

Mitigation: Oracle design, price checks
```

## Governance Tokens

### Rights and Functions
```
Voting: Proposals and parameter changes
Rewards: Earn protocol fees
Delegation: Vote through representatives
```

### Voting Mechanisms

#### Simple Majority
```
Quorum: Minimum participation
Vote: 50%+ wins
Time lock: Delay before execution
```

#### Quadratic Voting
```
Voting power = sqrt(token_amount)
Prevents whale dominance
More balanced participation
```

#### Conviction Voting
```
Longer lockup = more voting power
Aligned incentives
Prevents short-term attacks
```

## Derivatives and Synthetics

### Options and Futures
- Hedging tools
- Leverage exposure
- Price discovery
- Examples: dYdX, Aevo

### Synthetic Assets
```
Track price of underlying asset
Collateral backed or oracle-dependent
Enable exposure without actual ownership

Example: sUSD tracks USD price
```

## Cross-Chain Protocols

### Bridges
```
Lock asset on source chain
Mint wrapped version on destination
Unlock when returning

Risks: Smart contract bugs, validator sets
```

### Multi-Chain DEXs
```
Liquidity across chains
Cross-chain swaps
Atomic execution

Examples: Stargate, Across
```

## Risk Management

### Smart Contract Risk
```
Audit history
TVL and adoption
Code maturity
Bug bounties
Insurance
```

### Economic Risk
```
Collateral liquidation
Oracle manipulation
Governance attacks
Market volatility
```

### Operational Risk
```
Key management
Upgrade risks
Validator security
Network congestion
```

## Composability ("Money Legos")

### Flash Loan Arbitrage
```solidity
1. Flash borrow 1000 ETH from Aave
2. Swap on Uniswap V2 for better rate
3. Swap back on Uniswap V3
4. Repay Aave + fee, keep profit
```

### Leveraged Yield Farming
```
1. Deposit 10 ETH collateral to Aave
2. Borrow 50 DAI against ETH
3. Buy 50 DAI worth of ETH
4. Deposit ETH to Aave
5. Repeat to achieve 5x leverage
```

### Liquidation Arbitrage
```
1. Monitor liquidation prices
2. Buy collateral as it's liquidated
3. Sell on open market
4. Profit from discount
```

## Popular DeFi Protocols by Category

### DEXs: Uniswap, Curve, SushiSwap, Balancer
### Lending: Aave, Compound, Maker
### Yield: Yearn, Convex, Curve
### Derivatives: dYdX, Aevo, Perp Protocol
### Bridges: Across, Stargate, LayerZero

---

**Key Takeaways**:
- DeFi enables permissionless financial services
- AMMs revolutionized trading efficiency
- Lending protocols require careful risk management
- Composability creates powerful financial opportunities
- Security and oracle design are critical
- Different protocols optimize for different trade-offs
