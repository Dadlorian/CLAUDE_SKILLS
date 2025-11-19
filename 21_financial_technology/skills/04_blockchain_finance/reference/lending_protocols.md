# Lending Protocols Reference

## Overview of Lending Protocols

Decentralized lending protocols enable users to:
- Deposit assets and earn interest
- Borrow assets using collateral
- Supply capital to platform, earn returns
- Eliminate intermediaries (banks)

### Market Size
```
Aave: ~$10B+ TVL
Compound: ~$3B+ TVL
MakerDAO: ~$5B+ TVL
Others: ~$5B+ combined
```

## Core Mechanisms

### Supply Side
```
User deposits: 100 USDC
Receives: cUSDC (compound token) or aUSDC (Aave)
These tokens earn interest
Interest accrues continuously
```

### Interest Calculation
```
Annual interest = Principal * Rate * Time
Compounding: Happens each block

Example:
Deposit: 1000 USDC
APY: 5%
After 1 year: 1000 * (1 + 0.05)^1 = 1050 USDC
```

### Borrow Side
```
User borrows: 100 USDC
Pays interest: Variable or stable rate
Requires collateral: e.g., 200 ETH
Borrow limit: Depends on LTV
```

## Risk Parameters

### Loan-to-Value (LTV)
```
LTV = borrowed amount / collateral value

Example:
Collateral: 200 ETH @ $1500/ETH = $300,000
Can borrow: Up to 75% LTV = $225,000 maximum
Borrows: $100,000 USDC
Current LTV: $100,000 / $300,000 = 33%
Safe: Yes (33% < 75% limit)
```

### Liquidation Threshold (LT)
```
LT = Minimum collateral ratio to avoid liquidation
Typically: 10-20% higher than LTV

Example:
LTV: 75% (can borrow up to)
LT: 80% (liquidation at this level)
Safe range: Between LTV and LT

If LT reached: Liquidation triggered
```

### Liquidation Process
```
1. User's collateral ratio > LT
2. Liquidators bid to repay debt
3. Win: Get collateral at discount
4. User: Loses collateral, debt reduced
5. Liquidator: Profit from discount (5-13% typical)

Example:
Debt: $100,000 USDC
Liquidation: Collateral worth $125,000 auctioned
Liquidator: Buys at $112,500 (10% discount)
Profit: $12,500
User loses: $12,500 collateral value
```

### Health Factor
```
Health Factor = (Collateral Value * LT) / Total Debt

Example:
Collateral: $300,000
LT: 80%
Debt: $100,000
HF = ($300,000 * 0.80) / $100,000 = 2.4

HF > 1: Safe
HF = 1: At liquidation threshold
HF < 1: Liquidated

Higher HF: Safer position
Lower HF: Higher liquidation risk
```

## Interest Rate Models

### Utilization-Based (Most Common)
```
interest_rate = base_rate + (utilization_rate * slope)

utilization = total_borrowed / total_supplied

Example:
Base: 2%
Slope: 5%
Utilization: 60%
Rate: 2% + (60% * 5%) = 5%

Higher usage: Higher rates (incentivize supply)
Lower usage: Lower rates (incentivize borrowing)
```

### Kinked Rates (Aave V3)
```
If utilization < kink (e.g., 80%):
  rate = base + (utilization * slope1)

If utilization >= kink:
  rate = base + (kink * slope1) + ((utilization - kink) * slope2)

slope2 > slope1

Below kink: Gradual increase
Above kink: Steep increase (prevents over-utilization)
```

### Example (Aave USDC)
```
Base: 0%
Slope1: 4% (up to 80% utilization)
Slope2: 75% (above 80%)
Kink: 80%

At 50% utilization: 0% + (50% * 4%) = 2%
At 80% utilization: 0% + (80% * 4%) = 3.2%
At 90% utilization: 0% + (80% * 4%) + (10% * 75%) = 10.7%
```

## Stable vs Variable Rates

### Variable Rate Borrow
```
Rate changes with protocol utilization
Lower initial rate (usually)
Rate risk: Could increase significantly
Use case: Short-term borrowing, expect rates to fall
```

### Stable Rate Borrow
```
Fixed rate for duration of loan
Protected from rate increases
Higher than variable (reflects risk premium)
Use case: Long-term planning, rate certainty
Aave: Only available if debt small relative to supply
```

## Isolation and Risk Isolation

### Traditional Model
```
All assets pooled together
Single oracle failure affects all
Single asset bad debt spreads
Risk concentration
```

### Isolation Mode (Aave V3)
```
New collateral: Enters isolation
Can only borrow stablecoins
Maximum debt limit: Per collateral type
Benefit: Prevents bad debt contagion
Example: New ERC20 token
```

### E-Mode (Efficiency Mode)
```
Groups of correlated assets
Higher LTV within group
Lower LTV across groups
Example: USDC, USDT, DAI in same e-mode group
- USDC/USDT: 97% LTV
- USDC/ETH: 80% LTV
```

## Major Lending Protocols

### Aave
```
Features:
- Multiple collateral types
- Flash loans
- Governance via AAVE token
- v3: Isolation, E-mode
- v2: Stable/variable rates

TVL: ~$10B+
Assets: 30+

Governance: AAVE token voting
Safety: Insurance fund + over-collateralization
```

### Compound
```
Features:
- cToken model
- Algorithmic rates
- Governance via COMP token

TVL: ~$3B+
Assets: 15+

Governance: COMP token voting
Safety: Guardian (slow pause mechanism)
```

### MakerDAO
```
Features:
- Over-collateralized stablecoin (DAI)
- Multi-collateral support
- Governance via MKR token

TVL: ~$5B+
Focus: Collateral types
Borrowable: Only DAI
Governance: MKR voting
Safety: Liquidation mechanisms
```

## Advanced Features

### Flash Loans
```
Borrow large amount in single block
Repay within same transaction
Include 0.09% fee (Aave)

Requirements:
onFlashLoan() callback function must be called
Must repay by end of transaction

Use cases:
- Arbitrage: Borrow, swap, repay, keep profit
- Liquidations: Borrow to liquidate, repay
- Collateral swaps: Swap without capital
- Refinancing: Switch loans
```

### Flashloan Example
```solidity
1. Call flashLoan(token, amount, callback)
2. Protocol transfers amount to caller
3. Caller executes arbitrary logic
4. Caller must repay amount + fee
5. onFlashLoan() callback validates repayment
6. If not repaid: Transaction reverts
```

### Incentives and Governance
```
Governance tokens: AAVE, COMP, MKR
Voting: Protocol parameters
Propose changes: Amount required
Delegate: Vote through others
Quorum: Minimum participation

Emission rates: Reward early LPs/borrowers
Governance APY: Extra incentive for voting
```

## Risk Management

### Smart Contract Risk
```
Audits: Professional security reviews
Time-tested: Longer deployment = proven
TVL: Higher TVL = more scrutiny
Governance: Response to issues

Mitigations:
- Use established protocols
- Monitor TVL and usage
- Follow security announcements
```

### Liquidation Risk
```
Price volatility: Prices drop, liquidation risk increases
Over-leverage: High borrowing relative to collateral
Flash crashes: Sudden price movements

Prevention:
- Keep health factor > 1.5
- Diversify collateral
- Monitor positions
```

### Oracle Risk
```
Price feed manipulation: Bad data
Flash loan attacks: Artificially move price
Single oracle: Depends on one source

Mitigations:
- Multiple oracles
- Time-weighted averages
- Price circuit breakers
```

### Bad Debt and Undercollateralization
```
If liquidation insufficient to cover debt
Protocol absorbs loss
Socialized loss: All lenders take haircut
Insurance fund: Covers some bad debt

Prevention:
- Over-collateralization requirements
- Liquidation incentives
- Risk management
```

## Strategies

### Leveraged Borrowing
```
1. Deposit 10 ETH collateral
2. Borrow 50 USDC (5x leverage)
3. Buy 0.025 ETH with USDC (if ETH = $2000)
4. Deposit ETH, repeat
5. Result: 5x exposure to ETH

Risk: If ETH price drops, liquidation
Upside: 5x gains if ETH rises

NOT recommended for beginners
```

### Yield Farming
```
1. Deposit token A
2. Borrow token B
3. Use B to LP on AMM
4. Earn:
   - LP fees from AMM
   - Governance token rewards
   - Minus interest on borrowed B

Target: Total rewards > cost of borrowed B
APY: 20-50%+ possible (with risk)
```

### Stablecoin Arbitrage
```
1. Deposit USDC, earn interest
2. Borrow DAI at same/lower rate
3. Swap DAI to USDC
4. Earn spread
Net: Interest income - borrowing cost

APY: 0.5-2% (low risk)
```

## Comparison: Major Protocols

| Feature | Aave | Compound | Maker |
|---------|------|----------|-------|
| Model | Lending pool | Lending pool | Debt position |
| Borrow Asset | Multiple | Multiple | DAI only |
| Collateral | 30+ types | 15+ types | Multiple |
| Max LTV | 80%+ | 75%+ | 66% |
| Flash Loans | Yes | Yes | No |
| Governance | AAVE | COMP | MKR |
| TVL | $10B+ | $3B+ | $5B+ |
| Stability | Proven | Proven | Proven |

## Emerging Risks

### Liquidation Cascades
```
Large liquidation in one protocol
Affects other protocols' collateral values
Can trigger liquidations elsewhere
Systemic risk across protocols
```

### Composability Risks
```
Cross-protocol positions
One failure affects others
Example: Collateral in protocol A, borrow from B
Protocol A fails: B liquidates

Mitigation: Diversify, understand dependencies
```

## Best Practices

### For Lenders
```
1. Diversify across protocols
2. Focus on stable assets
3. Monitor changes
4. Understand rates
5. Check insurance availability
```

### For Borrowers
```
1. Keep health factor > 1.5
2. Avoid maximum LTV
3. Use stablecoins for stability
4. Monitor collateral prices
5. Have exit plan
```

### For Yield Farmers
```
1. Understand all risks
2. Calculate true APY (including risks)
3. Start small
4. Monitor positions
5. Have stop-loss
```

---

**Key Takeaways**:
- Lending protocols enable decentralized finance
- Risk parameters protect against liquidation
- Interest rates adjust with utilization
- Flash loans enable complex DeFi interactions
- Liquidations maintain solvency
- Multiple protocols with different features available
- Risk management is essential
