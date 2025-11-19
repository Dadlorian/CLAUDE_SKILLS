# Stablecoins Reference

## What are Stablecoins?

Cryptocurrencies designed to maintain stable value, typically $1 USD. Enable predictable transactions in volatile crypto market.

### Market Size
```
USDT: ~$120B market cap
USDC: ~$35B market cap
DAI: ~$5B market cap
BUSD, FRAX, USDD, others: ~$15B combined
```

## Types of Stablecoins

### 1. Fiat-Collateralized (Centralized)

#### USDC (USD Coin)
```
Issuer: Circle
Backing: 100% reserve of USD held in banks
Collateral: 1:1 with USD in US bank accounts
Redemption: Direct from Circle
Regulation: Fully compliant, regulated by US authorities
```

#### USDT (Tether)
```
Issuer: Tether Limited
Backing: Claims 1:1 USD + other assets
Collateral: Controversial - regularly questioned
Redemption: Tether can redeem or deposit
Market: Largest stablecoin by volume
```

#### BUSD (Binance USD)
```
Issuer: Paxos
Backing: 100% USD reserves
Collateral: Fully backed
Redemption: Via Paxos
Note: Phase-out announced in 2023
```

### Advantages
```
- Simplest to understand
- Lowest volatility
- Direct USD redemption
- Regulatory approval
```

### Disadvantages
```
- Centralization (depends on issuer)
- Custody risk (are funds actually there?)
- Requires trust in fiat system
- Regulatory risk (government action)
```

### 2. Crypto-Collateralized (Decentralized)

#### DAI (MakerDAO)
```
Collateral: ETH, USDC, other cryptos
LTV: ~66% (150% collateral ratio)
Mechanism: Users lock collateral, mint DAI
Stability: Peg maintained through incentives

Decentralized governance via MKR token
Over-collateralized for security
Can be undercollateralized in edge cases
```

#### sUSD (Synthetix)
```
Collateral: SNX tokens
LTV: Variable based on debt ceiling
Mechanism: Mint/burn against SNX collateral
Stability: Incentives + collateral
Use case: Synth tracking USD price
```

#### Algorithm
```
1. If sUSD price > $1:
   - Incentive to mint sUSD (profit opportunity)
   - Minting increases supply
   - Price falls back to $1

2. If sUSD price < $1:
   - Incentive to burn sUSD (profit opportunity)
   - Burning decreases supply
   - Price rises back to $1
```

### Advantages
```
- Fully decentralized
- Transparent collateral
- No custodian risk
- No government risk
- Programmatic stability
```

### Disadvantages
```
- Capital inefficient (over-collateralized)
- Collateral volatility risk
- Complex mechanisms
- Potential undercollateralization
```

### 3. Algorithmic (Pure Incentive)

#### Terra Luna (FAILED EXAMPLE)
```
Collateral: None (only Luna token incentives)
Mechanism: Terra-Luna loop for peg maintenance
UST: No collateral, pure algorithm
Luna: Incentive to absorb UST volatility

Failed: Death spiral in May 2022
Caused: Exit event broke incentive loop
Loss: ~$40B
```

#### Why Algorithmic Failed
```
Assumptions:
1. Users keep wanting Luna (not guaranteed)
2. Luna price stays high (not guaranteed)
3. Death spiral won't occur (it can)

Reality:
1. Luna perceived as worthless
2. Luna price collapsed
3. Incentives inverted
4. Cascade failure
```

### Advantages (Theoretically)
```
- Capital efficient
- Fully decentralized
- Scalable
```

### Disadvantages
```
- Unproven mechanism
- Vulnerable to death spirals
- Requires constant demand
- Highly risky
```

## Hybrid Approaches

### Partially Collateralized

#### FRAX (Fractional-Algorithmic)
```
Collateral: USDC (80% initially)
Algorithm: Seignorage shares (FXS)
Ratio: Adjusts based on market
Over time: Reduce collateral, increase algorithm

Design: Start safe, become more scalable
Current: ~75% collateralized
Target: Decrease over time
```

#### USDD (Tron DAO)
```
Collateral: TRX + other assets
Algorithm: Incentive mechanisms
Governance: Tron DAO voting
Stability: Maintained through incentives + collateral
```

## Collateral Management

### Safe Collateralization

#### MakerDAO Structure
```solidity
{
  Vault (CDP):
    - Collateral: 200 ETH
    - Collateral Value: $300,000
    - DAI Debt: $100,000
    - Collateral Ratio: 300%
    - Minimum Ratio: 150%
    - Safe: Yes (300% > 150%)
}
```

#### Liquidation Process
```
1. Price drops: ETH now $800 (was $1500)
2. New collateral value: $160,000
3. Debt: $100,000
4. Ratio: 160% (above 150% minimum)
5. Status: Still safe

If price drops to $600:
1. New value: $120,000
2. Ratio: 120% (below 150%)
3. Status: Undercollateralized
4. Liquidation triggered
5. Collateral auctioned, debt repaid
```

### Risk Parameters

#### Liquidation Ratio (LR)
```
LR = collateral price * liquidation threshold
If debt > LR: Liquidation occurs

Liquidation incentive: 5-13% (liquidator gets discount)
Stability fee: Annual fee to maintain DAI
```

#### Debt Ceiling (DC)
```
Maximum DAI that can be minted
Per collateral type: 1000 ETH DC = 666M DAI possible
Prevents over-reliance on single asset
Adjustable via governance
```

## Stablecoin Mechanisms

### Arbitrage Mechanics (DAI Example)
```
If DAI trades at $1.02:
1. Arbitrageur locks $1000 of collateral
2. Mints 1000 DAI (costs $1000 in fees)
3. Sells 1000 DAI at $1.02 = $1020
4. Profit: $20 (minus fees)
5. This increases DAI supply
6. DAI price falls back toward $1

Vice versa if DAI trades at $0.98
```

### Incentive Structures

#### Reward Rates
```
High DAI supply: Reduce mint reward, increase burn reward
Low DAI supply: Increase mint reward, reduce burn reward
Automatic stabilization through incentives
```

#### Fee Mechanisms
```
Stability Fee: Annual charge to maintain debt
Redemption Fee: Fee to redeem collateral
Flash Loan Fee: Charge for large temporary borrows
Revenue: Goes to DAO treasury
```

## Comparison: Stablecoins by Type

| Feature | Fiat | Crypto | Algorithmic | Hybrid |
|---------|------|--------|------------|--------|
| Collateral | USD | Crypto | Incentives | Mixed |
| Decentralization | Low | High | High | Medium |
| Volatility | Very Low | Low-Medium | High | Low |
| Capital Efficiency | High | Low | High | Medium |
| Risk | Custodian | Smart Contract | System | Mixed |
| Examples | USDC, USDT | DAI, sUSD | UST (failed) | FRAX |

## Use Cases

### Payments
```
USDC, USDT: Most used for on-chain payments
DAI: Decentralized option
Eliminating USD volatility in crypto
```

### Collateral
```
USDC: Primary collateral on many protocols
DAI: Decentralized collateral
Allows leverage/borrowing against stables
```

### Yield
```
Aave: 3-5% APY on USDC, DAI
Curve: Stable swaps generate fees
MakerDAO: Savings rate (DSR) on DAI
```

### Cross-Chain Transfers
```
Bridge USDC from Ethereum to Polygon
Quick, cheap cross-chain transfers
Better than wrapping/unwrapping
```

## Risks and Considerations

### Counterparty Risk (Fiat-Backed)
```
- Issuer insolvency
- Government seizure
- Banking collapse
- Regulatory action
Mitigation: Audit trails, guarantees
```

### Smart Contract Risk (Crypto-Backed)
```
- Bug in collateral management
- Oracle manipulation
- Flash loan attacks
- Upgrade failures
Mitigation: Audits, timelock, insurance
```

### Economic Risk (All Types)
```
- Demand collapse (people stop wanting it)
- Depegging events
- Volatility during stress
- Liquidity crunches
Mitigation: Diversification, reserves
```

### Regulatory Risk
```
- Classification as security
- Custody requirements
- Reserve mandates
- Stablecoin regulation (upcoming)
EU: MICA regulation (2024)
US: Multiple regulatory proposals
```

## Emerging Regulations

### MiCA (EU Markets in Crypto Assets Regulation)
```
Effective: 2024
Stablecoin requirements:
- Full reserve backing
- Capital requirements
- Redemption rights
- Operational requirements
- Regular audits
```

### US Stablecoin Legislation
```
Multiple proposals:
- Full reserve requirements
- Issuer insolvency protection
- Regular audits
- Banking charter requirements
Status: Still debated
```

## Future Trends

### Digital Central Bank Currencies (CBDCs)
```
Government-backed digital currencies
Similar to stablecoins but official
Implications: Potential competition
Timeline: 2024-2027 for major economies
```

### Multi-Chain Stablecoins
```
Same stablecoin across multiple chains
Examples: USDC on Ethereum, Polygon, Arbitrum
Benefits: Unified liquidity, easier movement
```

### Yield-Bearing Stablecoins
```
Earn yield on stablecoin holdings
Example: sDAI (DAI in Aave saving rate)
Rate: 3-5% annually
Use: Better value than holding pure stable
```

### Programmable Payments
```
Stablecoins with embedded conditions
Scheduled payments
Conditional transfers
Use case: Payroll, escrow
```

## Best Practices

### Selection Criteria
```
For trading:
- USDC (most reliable, regulated)
- USDT (most liquid)
- DAI (if want decentralized)

For holding:
- USDC (lowest risk, audited)
- USDT (high liquidity)

For yield:
- DAI (DSR, decentralized)
- USDC (Aave, high APY)
```

### Risk Management
```
- Diversify across stablecoin types
- Monitor collateral health (if crypto-backed)
- Check redemption mechanisms
- Understand regulatory status
- Avoid untested mechanisms
```

---

**Key Takeaways**:
- Multiple stablecoin models with different trade-offs
- Fiat-backed most stable, centralized
- Crypto-backed decentralized, requires over-collateralization
- Algorithmic mechanisms have not proven viable
- Hybrid approaches balance safety and efficiency
- Regulation is increasingly important
- Choose based on use case and risk tolerance
