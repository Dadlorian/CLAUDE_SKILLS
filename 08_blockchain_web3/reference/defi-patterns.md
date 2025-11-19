# DeFi Protocol Patterns

Core patterns and mechanisms used in DeFi protocols.

## 1. Automated Market Maker (AMM)

### Constant Product Formula (Uniswap V2)
```
x * y = k
```
Where x and y are reserve amounts, k is constant.

**Price Calculation:**
```solidity
price = reserveY / reserveX
```

**Swap Output:**
```solidity
amountOut = (amountIn * 997 * reserveOut) / ((reserveIn * 1000) + (amountIn * 997))
// 0.3% fee built in
```

### Concentrated Liquidity (Uniswap V3)
Liquidity provided in price ranges for capital efficiency.

## 2. Lending Protocol Patterns

### Supply-Borrow Model (Aave/Compound)
```
utilizationRate = totalBorrows / totalSupply
borrowRate = f(utilizationRate)
supplyRate = borrowRate * utilizationRate * (1 - reserveFactor)
```

### Interest Rate Models
- **Linear**: `rate = baseRate + utilizationRate * slope`
- **Kinked**: Low slope until kink, then steep

### Health Factor
```
healthFactor = (collateral * liquidationThreshold) / debt
```
- healthFactor < 1.0 = liquidatable

## 3. Yield Aggregator (Yearn)

**Vault Pattern (ERC-4626):**
```solidity
sharePrice = totalAssets / totalShares
shares = deposit * totalShares / totalAssets
withdrawal = shares * totalAssets / totalShares
```

## 4. Stablecoin Mechanisms

### Algorithmic (no collateral)
- Seigniorage shares
- Rebase mechanisms

### Collateralized (MakerDAO)
```
collateralRatio = collateralValue / debtValue
minCollateralRatio = 150% (for liquidation)
```

### Hybrid (Frax)
- Partially algorithmic, partially collateralized
