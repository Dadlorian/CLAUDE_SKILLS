# DeFi Integration Guide

## Overview
Complete guide to integrating decentralized finance protocols into applications. Covers lending, swaps, liquidity, and yield protocols.

## Prerequisites
```
- JavaScript/TypeScript knowledge
- Web3.js or ethers.js familiarity
- Understanding of DeFi concepts
- Access to blockchain RPC endpoints
- Testnet ETH for testing
```

## Environment Setup

### Install Dependencies
```bash
npm install ethers dotenv axios
npm install @aave/contract-helpers
npm install @uniswap/sdk @uniswap/v3-sdk
npm install @openzeppelin/contracts
```

### Environment Configuration
```env
INFURA_KEY=your_infura_key
ALCHEMY_KEY=your_alchemy_key
PRIVATE_KEY=your_private_key
CONTRACT_ADDRESS=deployed_contract_address
```

## Connecting to RPC

### Using ethers.js
```javascript
const ethers = require('ethers');

// Infura
const provider = new ethers.providers.InfuraProvider(
  'sepolia',
  process.env.INFURA_KEY
);

// Alchemy
const provider = new ethers.providers.AlchemyProvider(
  'sepolia',
  process.env.ALCHEMY_KEY
);

// Local node
const provider = new ethers.providers.JsonRpcProvider(
  'http://localhost:8545'
);

// Get network info
const network = await provider.getNetwork();
console.log('Network:', network.name);
```

## DEX Integration (Uniswap Example)

### Swap Tokens
```javascript
const { ethers } = require('ethers');
const { AlphaRouter } = require('@uniswap/smart-order-router');

const provider = new ethers.providers.AlchemyProvider(
  'mainnet',
  process.env.ALCHEMY_KEY
);

const router = new AlphaRouter({ chainId: 1, provider });

// Swap 1 USDC for ETH
const route = await router.route(
  fromAmount,    // 1000000 (1 USDC with 6 decimals)
  fromTokenInfo, // USDC token info
  toTokenInfo,   // ETH token info
  TradeType.EXACT_INPUT
);

console.log('Route found');
console.log('Quote:', route.quote);
console.log('Path:', route.route[0].tokenPath);
```

### Check Price
```javascript
const Fetcher = require('@uniswap/sdk').Fetcher;
const Route = require('@uniswap/sdk').Route;

// Fetch pair data
const pair = await Fetcher.fetchPairData(
  USDC,
  WETH,
  provider
);

// Create route
const route = new Route([pair], USDC, WETH);

// Get mid price
const midPrice = route.midPrice;
console.log('Price USDC/WETH:', midPrice.toSignificant(6));
console.log('Price WETH/USDC:', midPrice.invert().toSignificant(6));
```

## Lending Protocol Integration (Aave Example)

### Check User Balance
```javascript
const { LendingPool } = require('@aave/contract-helpers');

const lendingPool = new LendingPool({
  provider,
  lendingPoolAddress: AAVE_LENDING_POOL_ADDRESS
});

const balances = await lendingPool.getUserAccountData(userAddress);

console.log('Total Collateral (ETH):', balances.totalCollateralETH);
console.log('Total Borrow (ETH):', balances.totalBorrowsETH);
console.log('Available Borrow (ETH):', balances.availableBorrowsETH);
console.log('Health Factor:', balances.healthFactor);
```

### Deposit to Aave
```javascript
const { LendingPool } = require('@aave/contract-helpers');

// Get contract
const lendingPoolContract = new ethers.Contract(
  AAVE_LENDING_POOL,
  LENDING_POOL_ABI,
  signer
);

// Approve token (if not ETH)
const tokenContract = new ethers.Contract(
  USDC_ADDRESS,
  ERC20_ABI,
  signer
);

await tokenContract.approve(AAVE_LENDING_POOL, amount);

// Deposit
const tx = await lendingPoolContract.deposit(
  USDC_ADDRESS,
  amount,
  userAddress,
  0  // referral code
);

await tx.wait();
console.log('Deposit confirmed:', tx.hash);
```

### Borrow from Aave
```javascript
const lendingPoolContract = new ethers.Contract(
  AAVE_LENDING_POOL,
  LENDING_POOL_ABI,
  signer
);

// Borrow USDC
const tx = await lendingPoolContract.borrow(
  USDC_ADDRESS,
  amount,
  interestRateMode,  // 1 = stable, 2 = variable
  0,  // referral code
  userAddress
);

await tx.wait();
console.log('Borrow confirmed:', tx.hash);
```

## Liquidity Provider Integration

### Add Liquidity (Uniswap V3 Example)
```javascript
const {
  Trade,
  TokenAmount,
  Fetcher
} = require('@uniswap/sdk');
const { Position, Pool } = require('@uniswap/v3-sdk');

// Create position
const position = Position.fromAmount0({
  pool,
  tickLower,
  tickUpper,
  amount0: ethers.parseEther('1'),  // 1 ETH
  useFullPrecision: true,
});

const { amount0: amount0Desired, amount1: amount1Desired } = position.amounts;

// Create mint transaction
const tx = await nonfungiblePositionManager.mint({
  token0,
  token1,
  fee,
  tickLower,
  tickUpper,
  amount0Desired,
  amount1Desired,
  amount0Min: 0,
  amount1Min: 0,
  recipient: userAddress,
  deadline: Math.floor(Date.now() / 1000) + 60 * 20,
});

await tx.wait();
```

### Remove Liquidity
```javascript
const tx = await nonfungiblePositionManager.decreaseLiquidity({
  tokenId: positionId,
  liquidity,
  amount0Min: 0,
  amount1Min: 0,
  deadline: Math.floor(Date.now() / 1000) + 60 * 20,
});

await tx.wait();
```

## Oracle Integration (Chainlink Example)

### Get Price Feed
```javascript
const { ethers } = require('ethers');

const aggregatorV3ABI = require('@chainlink/contracts/abi/v0.8/AggregatorV3Interface.json');

const priceFeed = new ethers.Contract(
  CHAINLINK_ETH_USD_FEED,  // 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419
  aggregatorV3ABI,
  provider
);

const roundData = await priceFeed.latestRoundData();

const price = roundData.answer / 10 ** 8;  // 8 decimals
console.log('ETH Price (USD):', price);
```

### Verify Data Freshness
```javascript
const roundData = await priceFeed.latestRoundData();

const timestamp = roundData.updatedAt.toNumber();
const now = Math.floor(Date.now() / 1000);
const staleness = now - timestamp;

if (staleness > 3600) {
  console.warn('Price data is stale (> 1 hour)');
} else {
  console.log('Price data is fresh');
}
```

## Error Handling

### Transaction Reversion
```javascript
try {
  const tx = await contract.someFunction();
  await tx.wait();
} catch (error) {
  if (error.reason) {
    console.error('Revert reason:', error.reason);
  } else if (error.code === 'INSUFFICIENT_FUNDS') {
    console.error('Insufficient funds');
  } else {
    console.error('Error:', error.message);
  }
}
```

### Gas Estimation
```javascript
// Estimate gas before sending
const gasEstimate = await contract.estimateGas.someFunction(params);
const tx = await contract.someFunction(params, {
  gasLimit: gasEstimate.mul(120).div(100),  // 20% buffer
});
```

## Event Listening

### Monitor Transfers
```javascript
const tokenContract = new ethers.Contract(
  TOKEN_ADDRESS,
  ERC20_ABI,
  provider
);

// Listen to Transfer events
const filter = tokenContract.filters.Transfer(userAddress);

tokenContract.on(filter, (from, to, value, event) => {
  console.log('Transfer detected:');
  console.log('From:', from);
  console.log('To:', to);
  console.log('Value:', ethers.formatEther(value));
});

// Stop listening
// tokenContract.off(filter);
```

### Monitor Swaps
```javascript
const uniswapRouter = new ethers.Contract(
  UNISWAP_ROUTER,
  ROUTER_ABI,
  provider
);

const filter = uniswapRouter.filters.Swap();

uniswapRouter.on(filter, (sender, amount0In, amount1In, amount0Out, amount1Out, to, event) => {
  console.log('Swap detected:', event.transactionHash);
});
```

## Rate Limiting and Best Practices

### Batch Calls (Multicall)
```javascript
const multicall = new ethers.Contract(
  MULTICALL_ADDRESS,
  MULTICALL_ABI,
  provider
);

// Call multiple functions in single request
const calls = [
  tokenA.interface.encodeFunctionData('balanceOf', [userAddress]),
  tokenB.interface.encodeFunctionData('balanceOf', [userAddress]),
  tokenC.interface.encodeFunctionData('balanceOf', [userAddress]),
];

const results = await multicall.aggregate(calls);
```

### Rate Limiting
```javascript
async function rateLimited(fn, delayMs = 100) {
  await new Promise(resolve => setTimeout(resolve, delayMs));
  return fn();
}

// Usage
const price1 = await rateLimited(() => getPriceFromOracle1());
const price2 = await rateLimited(() => getPriceFromOracle2());
```

## Testing Integration

### Mock Contract Calls
```javascript
describe('DeFi Integration', () => {
  it('should handle swap correctly', async () => {
    const mockProvider = new ethers.providers.JsonRpcProvider(
      'http://localhost:8545'  // Local hardhat
    );

    // Get accounts
    const accounts = await mockProvider.listAccounts();
    const signer = mockProvider.getSigner(accounts[0]);

    // Test swap
    const tx = await router.swap(tokenA, tokenB, amount);
    await expect(tx).to.not.be.reverted;
  });
});
```

## Production Checklist

- [ ] Use testnet extensively
- [ ] Test with real RPC providers
- [ ] Implement error handling
- [ ] Monitor gas costs
- [ ] Add rate limiting
- [ ] Implement logging
- [ ] Handle timeouts
- [ ] Test edge cases
- [ ] Verify contract addresses
- [ ] Implement monitoring/alerting
- [ ] Secure private keys
- [ ] Document API keys setup

---

**Next Steps**:
1. Test on testnet (Sepolia)
2. Monitor transactions
3. Implement error recovery
4. Set up production monitoring
5. Plan upgrade strategy
