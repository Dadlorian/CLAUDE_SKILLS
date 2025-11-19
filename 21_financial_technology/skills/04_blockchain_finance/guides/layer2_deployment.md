# Layer 2 Deployment Guide

## Deployment Comparison

### Optimism (Optimistic Rollup)
```javascript
// hardhat.config.js
module.exports = {
  networks: {
    optimism: {
      url: "https://mainnet.optimism.io",
      accounts: [process.env.PRIVATE_KEY],
      gasPrice: 1000000000, // 1 Gwei typical
    },
    optimismSepolia: {
      url: "https://sepolia.optimism.io",
      accounts: [process.env.PRIVATE_KEY],
    },
  },
};

// Deployment script
async function main() {
  const Token = await ethers.getContractFactory("MyToken");
  const token = await Token.deploy();
  await token.deployed();

  console.log("Deployed to Optimism:", token.address);

  // Verify on Etherscan for Optimism
  await hre.run("verify:verify", {
    address: token.address,
    constructorArguments: [],
  });
}
```

### Arbitrum (Optimistic Rollup)
```javascript
module.exports = {
  networks: {
    arbitrum: {
      url: "https://arb1.arbitrum.io/rpc",
      accounts: [process.env.PRIVATE_KEY],
    },
    arbitrumSepolia: {
      url: "https://sepolia-rpc.arbitrum.io/rpc",
      accounts: [process.env.PRIVATE_KEY],
    },
  },
};

// Gas is denominated differently on Arbitrum
// L1 component + L2 component
```

### zkSync
```javascript
module.exports = {
  networks: {
    zkSync: {
      url: "https://mainnet.era.zksync.io",
      accounts: [process.env.PRIVATE_KEY],
    },
    zkSyncTestnet: {
      url: "https://testnet.era.zksync.dev",
      accounts: [process.env.PRIVATE_KEY],
    },
  },
};

// zkSync has different gas model
// EVM equivalent compilation differences
```

### Polygon
```javascript
module.exports = {
  networks: {
    polygon: {
      url: "https://polygon-rpc.com",
      accounts: [process.env.PRIVATE_KEY],
      gasPrice: 30000000000, // Varies
    },
  },
};

// Polygon is faster Ethereum chain
// More centralized than rollups
```

## Bridge Integration

### Deposit from Mainnet to L2
```javascript
async function depositToOptimism() {
  const provider = ethers.provider;

  // Get L1StandardBridge
  const l1Bridge = new ethers.Contract(
    "0x99C9fc46f92E8a1c0DeC1b1747d010903E884bE1", // Optimism L1 Bridge
    L1_BRIDGE_ABI,
    signer
  );

  // Approve token
  const token = new ethers.Contract(TOKEN_ADDRESS, ERC20_ABI, signer);
  await token.approve(l1Bridge.address, ethers.parseEther("100"));

  // Deposit
  const tx = await l1Bridge.depositERC20(
    tokenAddress,
    l2TokenAddress,
    ethers.parseEther("100"),
    200000, // L2 gas
    ethers.toUtf8Bytes("")
  );

  await tx.wait();
  console.log("Deposit initiated");
}
```

### Withdraw from L2 to Mainnet
```javascript
async function withdrawFromOptimism() {
  // Get L2StandardBridge on L2
  const l2Bridge = new ethers.Contract(
    "0x4200000000000000000000000000000000000010",
    L2_BRIDGE_ABI,
    l2Signer
  );

  // Approve token on L2
  const token = new ethers.Contract(l2TokenAddress, ERC20_ABI, l2Signer);
  await token.approve(l2Bridge.address, amount);

  // Initiate withdrawal
  const tx = await l2Bridge.withdraw(
    l2TokenAddress,
    amount,
    0,
    ethers.toUtf8Bytes("")
  );

  await tx.wait();

  // Wait for withdrawal to be finalized (7 days on Optimism)
  console.log("Withdrawal pending...");
}
```

## Multi-Chain Deployment

### Deploy to Multiple Networks
```javascript
const networks = ["mainnet", "optimism", "arbitrum", "polygon"];

async function deployToAll() {
  for (const network of networks) {
    console.log(`Deploying to ${network}...`);

    // Switch to network
    await hre.changeNetwork(network);

    // Deploy
    const Token = await ethers.getContractFactory("MyToken");
    const token = await Token.deploy();
    await token.deployed();

    console.log(`Deployed to ${network}: ${token.address}`);

    // Save addresses
    deployments[network] = token.address;
  }

  // Save deployment info
  fs.writeFileSync(
    "deployments.json",
    JSON.stringify(deployments, null, 2)
  );
}
```

## Monitoring L2 Transactions

### Track L2 Deposits
```javascript
async function trackDeposit(depositTxHash) {
  const provider = new ethers.providers.JsonRpcProvider(OPTIMISM_RPC);

  // Check L1 confirmation
  const receipt = await ethers.provider.getTransactionReceipt(depositTxHash);
  console.log("L1 block:", receipt.blockNumber);

  // Wait for message to be relayed
  const messenger = new ethers.OptimismSDK.CrossChainMessenger({
    l1ChainId: 1,
    l2ChainId: 10,
    l1SignerOrProvider: ethersProvider,
    l2SignerOrProvider: l2Provider,
  });

  // Check L2 status
  const status = await messenger.getMessageStatus(depositTxHash);
  console.log("L2 status:", status);
}
```

### Monitor Transaction Costs
```javascript
async function compareGas(contractCall, network) {
  const tx = await contractCall();
  const receipt = await tx.wait();

  const gasUsed = receipt.gasUsed;
  const gasPrice = receipt.gasPrice;
  const totalCost = gasUsed * gasPrice;

  console.log(`${network} cost:`, ethers.formatEther(totalCost), "ETH");
}

// Compare across networks
await compareGas(() => mainnetContract.someFunction(), "Mainnet");
await compareGas(() => optimismContract.someFunction(), "Optimism");
```

## Testing on Testnet

### Sepolia → Optimism Sepolia
```javascript
const networks = {
  sepoliaMainnet: {
    url: "https://sepolia.infura.io/v3/" + process.env.INFURA_KEY,
    chainId: 11155111,
  },
  optimismSepolia: {
    url: "https://sepolia.optimism.io",
    chainId: 11155420,
  },
};

// Deploy on testnet first
npx hardhat run scripts/deploy.js --network sepoliaMainnet
npx hardhat run scripts/deploy.js --network optimismSepolia
```

## Production Checklist

- [ ] Testnet deployment successful
- [ ] Contract verified on explorer
- [ ] Bridge mechanisms tested
- [ ] Gas costs profiled
- [ ] Multi-network deployments ready
- [ ] Monitoring setup configured
- [ ] Emergency procedures documented
- [ ] Insurance/guarantees in place
- [ ] Community informed
- [ ] Mainnet deployment authorized

---

**Key Takeaways**:
- Multiple L2 options with different trade-offs
- Optimize for target network characteristics
- Bridge integration enables asset movement
- Test thoroughly on testnets
- Monitor gas costs across networks
- Plan multi-chain strategy
