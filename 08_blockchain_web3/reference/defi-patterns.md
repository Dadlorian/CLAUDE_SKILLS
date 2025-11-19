# DeFi Protocol Patterns & Mechanisms

## Overview

DeFi protocols are built on proven, reusable patterns. This guide covers the most common and successful mechanisms used by leading protocols like Uniswap, Aave, Yearn, and Curve. Understanding these patterns is essential for building new protocols and auditing existing ones.

## 1. Automated Market Makers (AMM)

### Constant Product Formula (Uniswap V2)

**Core Formula**:
```
x * y = k (constant product invariant)
```

Where:
- `x` = reserve of token 0
- `y` = reserve of token 1
- `k` = product (must always be ≥ k)

**Price Calculation**:
```solidity
// Spot price of Token1 in terms of Token0
spotPrice = reserveToken0 / reserveToken1

// Market price after swap
function getAmountOut(uint amountIn, uint reserveIn, uint reserveOut)
    internal
    pure
    returns (uint amountOut)
{
    uint amountInWithFee = amountIn * 997; // 0.3% fee
    uint numerator = amountInWithFee * reserveOut;
    uint denominator = (reserveIn * 1000) + amountInWithFee;
    amountOut = numerator / denominator;
}
```

**Gas Costs**: ~100,000 gas per swap

**Advantages**:
- Simple, deterministic pricing
- Liquidity always available
- Fair pricing based on supply/demand

**Disadvantages**:
- High slippage on large trades
- Impermanent loss for liquidity providers
- Inefficient capital utilization

**Real World Example (Uniswap V2)**:
```solidity
contract UniswapV2Router {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts) {
        require(block.timestamp <= deadline, "Expired");

        amounts = new uint[](path.length);
        amounts[0] = amountIn;

        for (uint i; i < path.length - 1; i++) {
            (uint reserve0, uint reserve1) = getReserves(path[i], path[i + 1]);
            amounts[i + 1] = getAmountOut(amounts[i], reserve0, reserve1);
        }

        require(amounts[amounts.length - 1] >= amountOutMin, "Slippage");

        // Transfer and execute swaps
        IERC20(path[0]).transferFrom(msg.sender, pairs[0], amounts[0]);

        for (uint i; i < path.length - 1; i++) {
            _swap(amounts, path[i], path[i + 1], to);
        }

        return amounts;
    }
}
```

### Concentrated Liquidity (Uniswap V3)

**Concept**: Allow LPs to concentrate liquidity in specific price ranges

```solidity
// LP provides liquidity only between priceMin and priceMax
// Higher capital efficiency (~4000x for tight ranges)

function mint(
    address token0,
    address token1,
    uint24 fee,
    int24 tickLower,
    int24 tickUpper,
    uint256 amount0Desired,
    uint256 amount1Desired
) external returns (uint256 liquidity) {
    // Calculate optimal amounts based on current price
    // Mint LP NFT with concentrated position
    // Earn proportional fees within the range

    // When price moves outside range:
    // - LPs no longer earn fees
    // - Position becomes single-sided
    // - Withdrawal available
}
```

**Capital Efficiency**:
- V2: 1x (full range)
- V3 (1% range): 100x
- V3 (0.01% range): 10,000x

**Tradeoffs**:
- Higher capital efficiency
- More fee income when price stays in range
- Impermanent loss when price moves outside range
- Requires active management

## 2. Lending Protocol Patterns

### Supply-Borrow Model (Aave/Compound)

**Core Mechanics**:

```solidity
contract Lending {
    // User deposits assets
    function deposit(address asset, uint amount) external {
        IERC20(asset).transferFrom(msg.sender, address(this), amount);

        uint shares = (amount * totalShares) / totalAssets;
        balances[msg.sender][asset] += shares;

        totalDeposits[asset] += amount;
    }

    // User borrows against collateral
    function borrow(address asset, uint amount) external {
        require(getCollateralValue(msg.sender) >= amount * 1.5, "Insufficient collateral");

        debts[msg.sender][asset] += amount;
        IERC20(asset).transfer(msg.sender, amount);
    }

    // Interest accrues over time
    function getInterest() internal {
        uint utilizationRate = totalBorrows / totalSupply;
        uint borrowRate = getInterestRate(utilizationRate); // Depends on utilization
        uint supplyRate = borrowRate * utilizationRate * (1 - reserveFactor);

        // Accrue interest on every transaction
        totalBorrows += totalBorrows * borrowRate * timeElapsed;
        totalSupply += totalSupply * supplyRate * timeElapsed;
    }

    // Liquidate positions with health factor < 1.0
    function liquidate(address borrower, address asset) external {
        uint healthFactor = getHealthFactor(borrower);
        require(healthFactor < 1e18, "Not liquidatable");

        uint debtToCover = debts[borrower][asset];
        uint closureFee = debtToCover / 20; // 5% bonus for liquidator

        IERC20(asset).transferFrom(msg.sender, address(this), debtToCover);
        debts[borrower][asset] = 0;

        // Seize collateral with bonus
        uint collateralToSeize = (debtToCover + closureFee) * IERC20(collateral).price();
        balances[borrower][collateral] -= collateralToSeize;
        balances[msg.sender][collateral] += collateralToSeize;
    }
}
```

**Key Metrics**:

```
Utilization Rate = Total Borrows / Total Supply
- Low (<50%): Cheap borrowing, low yields
- Optimal (80-90%): Balanced
- High (>95%): Expensive borrowing, high yield

Health Factor = (Collateral Value × Liquidation Threshold) / Total Debt
- > 1.0: Safe
- < 1.0: Can be liquidated
- < 1.05: Liquidation zone (unsafe)
```

### Interest Rate Models

**Linear Model**:
```solidity
function getBorrowRate(uint utilization) pure returns (uint) {
    if (utilization < kink) {
        return baseRate + (utilization * slope1) / 1e18;
    } else {
        return baseRate + (kink * slope1) / 1e18 + ((utilization - kink) * slope2) / 1e18;
    }
}

// Example parameters (Compound):
// baseRate = 0% (2%)
// slope1 = 4% (low utilization rate)
// kink = 80% (optimal utilization)
// slope2 = 109% (high utilization rate - steep)
```

**Advantages**:
- Simple and predictable
- Users understand rates
- Encourages utilization near optimal

### Liquidations

**Two-Phase Liquidation**:
1. **Price Check**: Monitor health factor
2. **Liquidation**: When < 1.0, liquidator repays debt and receives collateral + bonus

```solidity
// Liquidation bonus structure (Aave)
baseBonus = 5%;           // Base liquidation bonus
additionalBonus = 0.5%;   // For each 1% health factor below 1.0

// Example: Health factor = 0.8 (20% below liquidation)
// Liquidation bonus = 5% + (0.2 * 0.5%) = 5.1%
```

**Flash Loan Liquidations**:
- Use flash loan to pay off debt
- Seize collateral
- Repay flash loan + premium in same transaction
- Pocket the profit

## 3. Yield Aggregator Pattern (Yearn/Aura)

### Vault Architecture (ERC-4626)

```solidity
contract YieldVault is ERC4626 {
    // Share price appreciates as strategy earns yield

    function deposit(uint assets, address receiver)
        public
        override
        returns (uint shares)
    {
        // Calculate shares based on current exchange rate
        uint currentShares = previewDeposit(assets);

        // User transfers assets
        IERC20(asset()).transferFrom(msg.sender, address(this), assets);

        // Mint shares to user
        _mint(receiver, currentShares);

        return currentShares;
    }

    function withdraw(uint assets, address receiver, address owner)
        public
        override
        returns (uint shares)
    {
        // Calculate shares needed to withdraw assets
        uint sharesToBurn = previewWithdraw(assets);

        _burn(owner, sharesToBurn);
        IERC20(asset()).transfer(receiver, assets);

        return sharesToBurn;
    }

    // Strategy harvesting
    function harvest() external {
        // 1. Earn yield from strategy (e.g., Aave)
        uint earned = strategy.getBalance() - totalAssets;

        // 2. Take protocol fee (10-20% of earnings)
        uint fee = earned * feePercent / 100;

        // 3. Distribute to share holders
        // Share price automatically increases as totalAssets grows
    }
}
```

**Key Formula**:
```
SharePrice = TotalAssets / TotalShares

When user deposits:
- Shares received = Assets × TotalShares / TotalAssets

When user withdraws:
- Assets received = Shares × TotalAssets / TotalShares

Share price only increases when:
- Strategy generates yield
- Vault receives protocol fees
```

**Multi-Strategy Approach**:
```solidity
contract StrategyAllocator {
    // Allocate assets across multiple strategies
    mapping(address => uint256) public allocation; // Strategy -> % allocation

    function rebalance() external {
        uint totalAssets = getTotalAssets();

        for (uint i; i < strategies.length; i++) {
            uint targetAmount = (totalAssets * allocation[strategies[i]]) / 100;
            strategies[i].adjustPosition(targetAmount);
        }
    }

    // Example allocations:
    // - 50% Aave (stable yield)
    // - 30% Uniswap (liquidity mining)
    // - 20% Curve (CRV incentives)
}
```

## 4. Stablecoin Mechanisms

### Collateralized Stablecoins (MakerDAO)

```solidity
contract MakerDAOStablecoin {
    // MakerDAO = Over-collateralized debt issuer

    function openVault(uint collateralAmount) external returns (uint vaultId) {
        // User deposits ETH as collateral
        IERC20(collateral).transferFrom(msg.sender, address(this), collateralAmount);

        vaults[vaultId] = Vault({
            owner: msg.sender,
            collateral: collateralAmount,
            debt: 0
        });

        return vaultId;
    }

    function drawDebt(uint vaultId, uint daiAmount) external {
        Vault storage vault = vaults[vaultId];

        // Ensure collateral ratio > 150%
        uint maxDebt = (vault.collateral * collateralPrice) / 150;
        require(vault.debt + daiAmount <= maxDebt, "Exceeds max debt");

        vault.debt += daiAmount;

        // Mint DAI to user
        dai.mint(msg.sender, daiAmount);

        emit DebtDrawn(vaultId, daiAmount);
    }

    function repayDebt(uint vaultId, uint daiAmount) external {
        Vault storage vault = vaults[vaultId];

        // User repays DAI (plus interest)
        dai.transferFrom(msg.sender, address(this), daiAmount);
        dai.burn(daiAmount);

        vault.debt -= daiAmount;

        emit DebtRepaid(vaultId, daiAmount);
    }

    function liquidateVault(uint vaultId) external {
        Vault storage vault = vaults[vaultId];
        uint collateralRatio = (vault.collateral * collateralPrice) / vault.debt;

        // Can be liquidated if ratio < 150% (actually < 120% with discount)
        require(collateralRatio < liquidationThreshold, "Not liquidatable");

        // Liquidator repays debt and receives collateral at discount
        uint liquidationDiscount = 13%; // Liquidator gets 13% profit
        uint collateralToReceive = vault.debt * (100 + liquidationDiscount) / collateralPrice;

        IERC20(collateral).transfer(msg.sender, collateralToReceive);

        vault.debt = 0;
        vault.collateral -= collateralToReceive;
    }
}
```

**Mechanism Safeguards**:
- Peg stability module (PSM) for direct exchanges
- Surplus buffer accumulation
- Multi-collateral support
- Governance-controlled stability fee

### Algorithmic Stablecoins (Challenges)

**Problem**: No collateral backing, stability relies on:
1. Incentives (seigniorage shares)
2. Arbitrage (market forces)
3. Confidence (network effects)

**Result**: Most fail during market stress (Luna/UST collapse)

**Why they fail**:
- Positive feedback loops in a crisis
- Requires continuous growth for stability
- Difficult to maintain peg without external capital
- Bank-run dynamics

### Hybrid Approach (Frax)

```solidity
contract FractionalStablecoin {
    // Partially backed by collateral, partially algorithmic

    uint public collateralRatio = 80; // Start at 80% collateral

    function mint(uint usdAmount, uint collateralAmount) external {
        // User provides:
        // - 80% USDC (collateral)
        // - 20% FXS (algorithmic)

        uint requiredCollateral = (usdAmount * collateralRatio) / 100;
        uint requiredFXS = usdAmount - requiredCollateral;

        IERC20(usdc).transferFrom(msg.sender, address(this), requiredCollateral);
        IERC20(fxs).transferFrom(msg.sender, address(this), requiredFXS);

        frax.mint(msg.sender, usdAmount);
    }

    // Adjust ratio based on market conditions
    // If FRAX > $1.00: Increase ratio → More collateral needed
    // If FRAX < $1.00: Decrease ratio → Less collateral needed
}
```

## DeFi Pattern Comparison Matrix

| Pattern | TVL | Complexity | Risk | Returns |
|---------|-----|------------|------|---------|
| **AMM** | High | Low | Medium | Low |
| **Lending** | Very High | High | Medium-High | Medium |
| **Yield Vault** | High | Medium | Low-Medium | Medium |
| **Stablecoin** | High | Very High | High | None |

## Best Practices for DeFi Implementations

1. **Slippage Protection**: Always implement minAmountOut
2. **Reentrancy Guards**: Check-Effects-Interactions pattern
3. **Oracle Safety**: Multiple sources, staleness checks
4. **Liquidation Incentives**: Proper bonuses prevent orphaned positions
5. **Gas Optimization**: Storage packing, batch operations
6. **Upgrade Path**: Proxy patterns for future improvements

---

**Remember**: DeFi is high-risk, high-reward. Every pattern has trade-offs. Understand them deeply before building.
