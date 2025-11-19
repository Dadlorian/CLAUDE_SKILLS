# DeFi Math Formulas

## AMM (Uniswap V2)
```
Constant Product: x * y = k

Price: price = reserveY / reserveX

Swap Output: amountOut = (amountIn * 997 * reserveOut) / ((reserveIn * 1000) + (amountIn * 997))

Add Liquidity: shares = min(amountX * totalShares / reserveX, amountY * totalShares / reserveY)

Remove Liquidity:
  amountX = shares * reserveX / totalShares
  amountY = shares * reserveY / totalShares
```

## Lending (Compound/Aave)
```
Utilization Rate: U = totalBorrows / totalSupply

Borrow Rate (linear): r_b = baseRate + slope * U

Supply Rate: r_s = r_b * U * (1 - reserveFactor)

Health Factor: HF = (collateral * liquidationThreshold) / debt
  HF < 1.0 = liquidatable

Collateral Ratio: CR = collateralValue / debtValue
```

## Staking Rewards
```
Reward Per Token: rewardRate * timeElapsed / totalStaked

User Reward: userStake * rewardPerToken

APY: ((1 + rewardRate / periods)^periods - 1) * 100
```

## Price Impact
```
Price Impact = |newPrice - oldPrice| / oldPrice * 100

Slippage: (expectedAmount - actualAmount) / expectedAmount * 100
```
