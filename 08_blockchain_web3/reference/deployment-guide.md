# Smart Contract Deployment Guide

## Overview

Deploying smart contracts to production is a critical operation that requires careful planning, testing, and execution. This guide covers best practices for deploying contracts across multiple blockchain networks, managing upgrade cycles, and ensuring production stability.

A single deployment mistake can lead to security vulnerabilities, financial loss, or protocol failure. This guide emphasizes systematic verification, multi-stage testing, and careful transaction execution.

## Pre-Deployment Checklist

### Code Review & Security

Before any deployment, ensure:
- [ ] **Security Audit**: External audit completed and critical issues resolved
- [ ] **Code Review**: Peer review of all changes
- [ ] **Test Coverage**: >95% code coverage
- [ ] **Gas Optimization**: Optimized for target network
- [ ] **Access Control**: Admin functions properly protected
- [ ] **Emergency Procedures**: Pause mechanisms and circuit breakers in place
- [ ] **Documentation**: Comprehensive NatSpec comments

### Testing Requirements

- [ ] **Unit Tests**: All functions tested
- [ ] **Integration Tests**: Cross-contract interactions verified
- [ ] **Fork Tests**: Tested against actual blockchain state
- [ ] **Testnet Deployment**: Full deployment flow practiced
- [ ] **Invariant Tests**: Protocol invariants hold
- [ ] **Fuzz Tests**: Edge cases and boundary conditions checked
- [ ] **Simulation**: Tenderly or Hardhat simulations successful

### Verification Preparation

- [ ] Constructor arguments documented and verified
- [ ] Upgrade proxy configuration reviewed (if using proxies)
- [ ] Initialization parameters prepared
- [ ] Admin keys and multisig addresses confirmed
- [ ] Ownership transfer recipients identified

## Blockchain Network Profiles

### Ethereum Mainnet

**Characteristics**:
- Gas Prices: 20-200 gwei (highly variable)
- Block Time: ~12 seconds
- Finality: ~15 minutes (25 blocks)
- Transaction Cost: $50-500+ per deployment

**RPC Providers**:
- Infura: `https://mainnet.infura.io/v3/{projectId}`
- Alchemy: `https://eth-mainnet.alchemy.com/v2/{apiKey}`
- Quicknode: `https://mainnet.quicknode.pro/`

**Deployment Strategy**:
```javascript
// Estimate gas and wait for reasonable gas prices
const gasPrice = await ethers.provider.getGasPrice();
if (gasPrice.gt(ethers.utils.parseUnits('100', 'gwei'))) {
    console.warn('Gas price high, consider waiting');
}

// Deploy with explicit gas settings
const contract = await MyContract.deploy(...args, {
    gasLimit: 5000000,
    gasPrice: ethers.utils.parseUnits('50', 'gwei'),
});

// Wait for multiple confirmations
await contract.deployTransaction.wait(10);
```

**Cost Optimization**:
- Deploy during low-traffic periods (weekends, UTC morning)
- Use EIP-1559 with max priority fee instead of fixed price
- Monitor gas tracker (gwei.tools)
- Consider testnet pre-flights

### Polygon (Layer 2 Alternative-L1)

**Characteristics**:
- Gas Prices: 30-100 GWEI (much lower than Ethereum)
- Block Time: ~2 seconds
- Finality: ~5 minutes (256 blocks)
- Chain ID: 137
- Transaction Cost: $1-10 per deployment

**RPC Providers**:
- Public: `https://polygon-rpc.com/`
- Alchemy: `https://polygon-mainnet.alchemy.com/v2/{apiKey}`
- Quicknode: `https://polygon-mainnet.quicknode.pro/`

**Bridge Information**:
- Official Polygon Bridge: https://wallet.polygon.technology/bridge/
- Fee: 0-2% depending on asset
- Withdrawal Time: ~7-45 minutes

**Deployment Strategy**:
```javascript
const polygonProvider = new ethers.providers.JsonRpcProvider(
    'https://polygon-rpc.com'
);

const deployer = new ethers.Wallet(process.env.PRIVATE_KEY, polygonProvider);

const contract = await MyContract.connect(deployer).deploy(...args, {
    gasLimit: 3000000,
    gasPrice: ethers.utils.parseUnits('50', 'gwei'),
});

console.log('Deployed to:', contract.address);
```

### Arbitrum (Optimistic Rollup)

**Characteristics**:
- Gas Prices: Low (10-50 gwei base layer + L2 fees)
- Finality: ~1-2 minutes (on L2)
- L1-L2 Bridge: 10-15 minutes to L1
- Withdrawal (L2→L1): ~7 days
- Chain ID: 42161

**RPC Providers**:
- Offical: `https://arb1.arbitrum.io/rpc`
- Alchemy: `https://arb-mainnet.alchemy.com/v2/{apiKey}`
- Quicknode: `https://arbitrum-mainnet.quicknode.pro/`

**Key Differences**:
- Compute-intensive operations cost more (gas * 16-20)
- Storage operations are cheaper
- Call data is compressed with brotli
- L2-to-L1 communication uses async messaging

**Deployment Strategy**:
```javascript
const arbitrumProvider = new ethers.providers.JsonRpcProvider(
    'https://arb1.arbitrum.io/rpc'
);

// Calculate expected L1 costs
const estimatedGas = await contract.estimateGas.deploy(...args);
const baseFee = await arbitrumProvider.getGasPrice();
const l2Fee = baseFee.mul(estimatedGas);

console.log('Estimated L2 fee:', ethers.utils.formatEther(l2Fee));
```

**Bridging Assets**:
```typescript
// Use Arbitrum SDK for bridge operations
import { EthBridge, AdminErc20Bridge } from '@arbitrum/sdk';

const l1ToL2Message = await ethBridge.getL1ToL2Message(txHash);
const status = await l1ToL2Message.status();
```

### Optimism (Optimistic Rollup)

**Characteristics**:
- Gas Prices: Low (10-30 gwei equivalent)
- Finality: ~1 minute
- L1-L2 Bridge: Immediate (~3 minutes)
- Withdrawal (L2→L1): 7 days challenge period
- Chain ID: 10
- EVM Equivalent (exact EVM compatibility)

**RPC Providers**:
- Official: `https://mainnet.optimism.io`
- Alchemy: `https://opt-mainnet.alchemy.com/v2/{apiKey}`
- Quicknode: `https://optimism-mainnet.quicknode.pro/`

**Deployment Strategy**:
```javascript
const optimismProvider = new ethers.providers.JsonRpcProvider(
    'https://mainnet.optimism.io'
);

// Optimism transactions include scalar for fee calculation
const gasPrice = await optimismProvider.getGasPrice(); // includes L1 component
const estimatedTx = await MyContract.getDeployTransaction(...args);
const estimatedGas = await optimismProvider.estimateGas(estimatedTx);

console.log('Total fee:', ethers.utils.formatEther(
    gasPrice.mul(estimatedGas)
));
```

**Unique Features**:
- `block.number` returns next block number (off by 1)
- Beacon root available on L1 for cross-chain verification
- Efficient for storage-heavy contracts

### Base (Coinbase's L2)

**Characteristics**:
- Gas Prices: Very low (similar to Optimism)
- Based on Optimism stack
- Chain ID: 8453
- Finality: ~1 minute
- Transaction Cost: $0.1-2 per deployment

**RPC Providers**:
- Official: `https://mainnet.base.org`
- Alchemy: `https://base-mainnet.alchemy.com/v2/{apiKey}`
- Quicknode: `https://base-mainnet.quicknode.pro/`

**Deployment is identical to Optimism** (same codebase)

### Other EVM Chains

**Avalanche C-Chain**:
- Gas: 20-50 nanoAVAX (~$0.01-0.05)
- Finality: ~1-2 seconds
- RPC: `https://api.avax.mainnet.avalabs.io/ext/bc/C/rpc`

**BNB Smart Chain**:
- Gas: 1-3 gwei
- Finality: ~3 seconds
- RPC: `https://bsc-dataseed.binance.org/`

**Gnosis Chain**:
- Gas: 1-2 gwei
- Finality: ~5 seconds
- RPC: `https://rpc.gnosischain.com/`

## Deployment Process

### Stage 1: Testnet Deployment

**Purpose**: Verify the full deployment flow before mainnet

**Steps**:
```bash
# 1. Compile contracts
hardhat compile

# 2. Deploy to testnet
hardhat run scripts/deploy.js --network sepolia

# 3. Verify contracts on block explorer
hardhat verify --network sepolia 0x... "Constructor Arg1" "Constructor Arg2"

# 4. Test against deployed contract
npx hardhat test --network sepolia

# 5. Verify functionality
# Manually test key functions using etherscan write function
```

**Testnet RPC Endpoints**:
- Sepolia (Ethereum): `https://sepolia.infura.io/v3/{projectId}`
- Polygon Mumbai: `https://rpc-mumbai.maticvigil.com`
- Arbitrum Sepolia: `https://sepolia-rollup.arbitrum.io:nitro`
- Optimism Sepolia: `https://sepolia.optimism.io`

### Stage 2: Pre-Mainnet Preparation

**Final Verification**:
```javascript
// Verify all parameters are correct
console.log({
    deployer: deployerAddress,
    constructorArgs: [arg1, arg2],
    gasPrice: ethers.utils.formatUnits(estimatedGasPrice, 'gwei'),
    estimatedCost: ethers.utils.formatEther(estimatedTotalCost),
});

// Get deployer balance
const balance = await ethers.provider.getBalance(deployerAddress);
console.log('Deployer balance:', ethers.utils.formatEther(balance));
```

**Environment Setup**:
```bash
# Create .env.production
MAINNET_RPC_URL=https://eth-mainnet.alchemy.com/v2/...
DEPLOYER_PRIVATE_KEY=... # Should be in hardware wallet for real deployment
ETHERSCAN_API_KEY=... # For verification
```

### Stage 3: Mainnet Deployment

**Safe Deployment Script**:
```javascript
// scripts/deploy-mainnet.js
async function main() {
    const [deployer] = await ethers.getSigners();

    console.log('Deploying with account:', deployer.address);
    console.log('Account balance:', await ethers.provider.getBalance(deployer.address));

    // Optional: Wait for confirmation before proceeding
    console.log('Press ENTER to proceed with deployment...');
    await new Promise(resolve => setTimeout(resolve, 5000)); // 5 second delay

    const Contract = await ethers.getContractFactory('MyContract');
    const contract = await Contract.deploy(constructorArg1, constructorArg2, {
        gasLimit: 5000000,
    });

    console.log('Contract deployment transaction hash:', contract.deployTransaction.hash);
    console.log('Waiting for deployment...');

    // Wait for confirmations
    const receipt = await contract.deployTransaction.wait(5);

    console.log('Contract deployed to:', contract.address);
    console.log('Deployment block:', receipt.blockNumber);

    return contract.address;
}

main()
    .then(address => {
        console.log('SUCCESS: Contract deployed to', address);
        process.exit(0);
    })
    .catch(error => {
        console.error('FAILED:', error);
        process.exit(1);
    });
```

**Deployment Command**:
```bash
# Dry run (estimate gas/cost)
HARDHAT_NETWORK=hardhat npx hardhat run scripts/deploy-mainnet.js

# Actual deployment
HARDHAT_NETWORK=mainnet npx hardhat run scripts/deploy-mainnet.js
```

### Stage 4: Post-Deployment Verification

**On-Chain Verification**:
```solidity
// Verify bytecode matches source
// 1. Get deployed bytecode from Etherscan
// 2. Compare with local compilation: hardhat compile → artifacts

// Verify initialization
// 1. Call view functions to verify state
// 2. Check events emitted during deployment
// 3. Verify ownership/permissions
```

**Block Explorer Verification**:
```bash
# Hardhat verification command
hardhat verify --network mainnet 0xDeployedAddress "Constructor Arg 1" "Constructor Arg 2"

# Manual verification via Etherscan
# Upload source code with matching compiler version
```

**Functional Testing**:
```javascript
// Connect to deployed contract and test key functions
const deployedContract = MyContract.attach(deploymentAddress);

// Test readonly functions
const result = await deployedContract.myViewFunction();
console.log('Function result:', result);

// DO NOT call state-changing functions on mainnet unless necessary
```

## Contract Initialization

### Constructor vs Initializer Pattern

**Immutable Deployment** (No Upgrades):
```solidity
contract MyToken is ERC20 {
    address public owner;

    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        owner = msg.sender;
    }
}

// Deploy with: await MyToken.deploy("MyToken", "MTK");
```

**Upgradeable with Proxy**:
```solidity
contract MyTokenV1 is ERC20Upgradeable {
    address public owner;

    // Constructor must be empty!
    constructor() {
        _disableInitializers();
    }

    // Initialization function called after proxy creation
    function initialize(string memory name, string memory symbol) external initializer {
        __ERC20_init(name, symbol);
        owner = msg.sender;
    }
}

// Deploy: proxy = await upgrades.deployProxy(MyTokenV1, ["MyToken", "MTK"]);
```

### Multi-Step Initialization

```javascript
// Deploy proxy
const proxy = await upgrades.deployProxy(MyToken, []);

// Wait for confirmation
await proxy.deployed();

// Initialize in separate transaction
await proxy.initialize("Token Name", "SYMBOL");

// Verify initialization
const name = await proxy.name();
console.log('Token initialized:', name);
```

## Ownership & Access Control Transfer

**Critical**: Always transfer admin powers to multisig before considering deployment complete.

```javascript
// 1. Deploy contract with deployer as initial owner
const contract = await MyContract.deploy();

// 2. Transfer ownership to multisig
const multisigAddress = "0x..."; // Gnosis Safe or similar
await contract.transferOwnership(multisigAddress);

// 3. Verify ownership
const currentOwner = await contract.owner();
console.assert(currentOwner === multisigAddress, "Ownership not transferred!");
```

## Multi-Chain Deployment Configuration

### Hardhat Configuration

```javascript
// hardhat.config.js
module.exports = {
    networks: {
        mainnet: {
            url: process.env.MAINNET_RPC_URL || "",
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 1,
            verify: {
                etherscan: {
                    apiUrl: "https://api.etherscan.io",
                    apiKey: process.env.ETHERSCAN_API_KEY
                }
            }
        },
        polygon: {
            url: process.env.POLYGON_RPC_URL || "https://polygon-rpc.com",
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 137,
            verify: {
                etherscan: {
                    apiUrl: "https://api.polygonscan.com",
                    apiKey: process.env.POLYGONSCAN_API_KEY
                }
            }
        },
        arbitrum: {
            url: process.env.ARBITRUM_RPC_URL || "https://arb1.arbitrum.io/rpc",
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 42161,
        },
        optimism: {
            url: process.env.OPTIMISM_RPC_URL || "https://mainnet.optimism.io",
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 10,
        },
        base: {
            url: process.env.BASE_RPC_URL || "https://mainnet.base.org",
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 8453,
        },
        // Testnets
        sepolia: {
            url: process.env.SEPOLIA_RPC_URL || `https://sepolia.infura.io/v3/${process.env.INFURA_API_KEY}`,
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 11155111,
        },
        mumbai: {
            url: process.env.MUMBAI_RPC_URL || "https://rpc-mumbai.maticvigil.com",
            accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : [],
            chainId: 80001,
        },
    },
    etherscan: {
        apiKey: {
            mainnet: process.env.ETHERSCAN_API_KEY,
            polygon: process.env.POLYGONSCAN_API_KEY,
            arbitrumOne: process.env.ARBITRUMSCAN_API_KEY,
            optimisticEthereum: process.env.OPTIMISMSCAN_API_KEY,
            base: process.env.BASESCAN_API_KEY,
        }
    }
};
```

### Unified Deployment Script

```javascript
// scripts/deploy-all-chains.js
async function deployToChain(chainName) {
    console.log(`\n===== Deploying to ${chainName} =====`);

    const contract = await ethers.getContractFactory("MyContract");
    const instance = await contract.deploy(/* args */);

    await instance.deployed();

    console.log(`${chainName}: Deployed to ${instance.address}`);

    // Wait for block explorer indexing
    if (chainName !== "hardhat") {
        console.log(`Waiting for indexing...`);
        await new Promise(r => setTimeout(r, 30000));
    }

    // Verify on block explorer
    if (process.env.VERIFY === "true") {
        console.log(`Verifying on ${chainName}...`);
        try {
            await hre.run("verify:verify", {
                address: instance.address,
                constructorArguments: [/* args */],
            });
        } catch (e) {
            console.error("Verification failed:", e.message);
        }
    }

    return instance.address;
}

async function main() {
    const deployments = {};

    // Deploy to each configured network
    for (const chain of ["mainnet", "polygon", "arbitrum", "optimism", "base"]) {
        try {
            deployments[chain] = await deployToChain(chain);
        } catch (error) {
            console.error(`Failed to deploy to ${chain}:`, error);
        }
    }

    console.log("\n===== DEPLOYMENT SUMMARY =====");
    console.log(JSON.stringify(deployments, null, 2));

    // Save deployment addresses
    const fs = require("fs");
    fs.writeFileSync(
        "deployments.json",
        JSON.stringify(deployments, null, 2)
    );
}

main().catch(console.error);
```

## Gas Optimization by Chain

### Ethereum Mainnet
- **Storage costs**: Very high (~20,000 gas per write)
- **Strategy**: Minimize storage, use packing
- **Typical deployment cost**: $1,000-5,000

### Layer 2s (Arbitrum, Optimism, Base)
- **Storage costs**: Still ~20,000 gas equivalent (but cheaper)
- **Call data**: Compressed, so more efficient
- **Strategy**: Function consolidation okay, fewer calls better
- **Typical deployment cost**: $50-200

### Alternative L1s (Polygon, BSC, Avalanche)
- **Storage costs**: ~20,000 gas (but very cheap gwei)
- **Strategy**: Similar to L2
- **Typical deployment cost**: $10-100

## Post-Deployment Monitoring

### Event Logging

```javascript
// Monitor deployment-related events
contract.on("OwnershipTransferred", (previousOwner, newOwner) => {
    console.log(`Ownership transferred from ${previousOwner} to ${newOwner}`);
});

contract.on("Initialized", (version) => {
    console.log(`Contract initialized at version ${version}`);
});
```

### Health Checks

```javascript
// Regular verification contract is operational
async function verifyDeployment(contractAddress) {
    const contract = MyContract.attach(contractAddress);

    // Call view functions
    const name = await contract.name();
    const owner = await contract.owner();

    // Verify state
    console.assert(name === "Expected Name", "Name mismatch");
    console.assert(owner !== ethers.constants.AddressZero, "Owner not set");

    console.log("✓ Deployment verified");
}
```

## Emergency Procedures

### Pause/Unpause

```javascript
// If critical issue discovered post-deployment
if (issueDetected) {
    await contract.pause(); // Requires onlyOwner (multisig)
    console.log("Contract paused - emergency maintenance");

    // After fix deployed via upgrade
    await contract.unpause();
}
```

### Rollback Strategy

For upgradeable contracts:
```javascript
// Revert to previous implementation
const previousImpl = "0x...";
const proxyAdmin = "0x...";

await proxyAdmin.upgrade(proxyAddress, previousImpl);
console.log("Rolled back to previous implementation");
```

## Deployment Checklist

Pre-Deployment:
- [ ] Code audit completed
- [ ] All tests passing with >95% coverage
- [ ] Testnet deployment successful
- [ ] Block explorer verification working
- [ ] Constructor arguments triple-checked
- [ ] Deployer account funded with sufficient gas

Deployment:
- [ ] Deploy with explicit gas limits
- [ ] Wait for sufficient confirmations (5+ on mainnet)
- [ ] Record deployment transaction hash
- [ ] Save deployment address and ABI

Post-Deployment:
- [ ] Verify contract on block explorer
- [ ] Initialize contracts if using proxy pattern
- [ ] Test key functions via etherscan
- [ ] Transfer ownership to multisig
- [ ] Set up monitoring and alerting
- [ ] Announce deployment to community
- [ ] Document in deployment tracking

---

**Remember**: Blockchain transactions are immutable. Verify everything multiple times before deployment. When in doubt, deploy to testnet first.
