# Token Deployment Guide

## Planning Your Token

### Token Type Decision
```
ERC20 (Fungible):
  - Standard tokens (payments, governance)
  - Dividends, rewards
  - Staking rewards
  Best for: Most use cases

ERC721 (NFT):
  - Unique collectibles
  - Memberships
  - Gaming assets
  Best for: Unique items

ERC1155 (Multi-Token):
  - Mix of fungible and NFTs
  - Gaming items
  - Batched operations
  Best for: Complex scenarios
```

### Token Parameters
```
Name: Long form name
Symbol: 3-4 letter abbreviation
Decimals: Usually 18 (like ETH)
Initial Supply: Total tokens to create
Minting: Allow creating more later?
Burning: Allow destroying tokens?
Tax: Any fees on transfers?
```

## ERC20 Token Implementation

### Simple Token
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("My Token", "MTK") {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }
}
```

### Token with Minting
```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor(uint256 initialSupply)
        ERC20("My Token", "MTK")
    {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}
```

### Token with Burn
```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

contract MyToken is ERC20, ERC20Burnable {
    constructor(uint256 initialSupply)
        ERC20("My Token", "MTK")
    {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }
}
```

### Token with Capped Supply
```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Capped.sol";

contract MyToken is ERC20, ERC20Capped {
    constructor(uint256 initialSupply, uint256 maxSupply)
        ERC20("My Token", "MTK")
        ERC20Capped(maxSupply * 10 ** decimals())
    {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }

    function _mint(address to, uint256 amount)
        internal
        override(ERC20, ERC20Capped)
    {
        super._mint(to, amount);
    }
}
```

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and audited
- [ ] Tests pass (100% coverage)
- [ ] Testnet deployment successful
- [ ] Contract verified on block explorer
- [ ] Security considerations addressed
- [ ] Documentation complete
- [ ] Tax/fee mechanism (if any) tested
- [ ] Emergency pause mechanism ready
- [ ] Token distribution plan finalized
- [ ] Marketing ready

### Deployment Process

#### Step 1: Prepare Deployment
```bash
# Compile contract
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to testnet first
npx hardhat run scripts/deploy.js --network sepolia
```

#### Step 2: Verify Deployment
```bash
# Check deployment succeeded
npx hardhat run scripts/verify.js --network sepolia

# Verify balances
npx hardhat run scripts/check-balance.js --network sepolia
```

#### Step 3: Verify on Block Explorer
```bash
# Verify contract source code on Etherscan
# Visit: https://sepolia.etherscan.io/
# Paste contract address
# Verify source code matches deployment
```

#### Step 4: Test on Testnet
```bash
# Transfer tokens
# Test approve/transferFrom
# Verify events are logged
# Check gas costs
```

#### Step 5: Mainnet Deployment
```bash
npx hardhat run scripts/deploy.js --network mainnet
```

## Deployment Script

### Basic Deployment
```javascript
// scripts/deploy.js
const hre = require("hardhat");

async function main() {
  console.log("Deploying MyToken...");

  const initialSupply = ethers.parseEther("1000000");  // 1M tokens

  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const token = await MyToken.deploy(initialSupply);

  await token.deployed();

  console.log("MyToken deployed to:", token.address);

  // Save deployment info
  const deploymentInfo = {
    token: token.address,
    network: hre.network.name,
    blockNumber: await hre.ethers.provider.getBlockNumber(),
    timestamp: new Date().toISOString(),
  };

  const fs = require("fs");
  fs.writeFileSync(
    `deployment-${hre.network.name}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### Deployment with Verification
```javascript
async function main() {
  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const token = await MyToken.deploy(initialSupply);

  await token.deployed();

  console.log("Deploying to:", token.address);

  // Wait for block confirmations
  await token.deployTransaction.wait(6);

  console.log("Verifying contract...");

  // Verify on Etherscan
  try {
    await hre.run("verify:verify", {
      address: token.address,
      constructorArguments: [initialSupply],
    });
  } catch (error) {
    console.log("Verification error:", error);
  }
}
```

## Token Distribution

### Vesting Schedule
```solidity
contract TokenVesting {
    IERC20 public token;
    address public beneficiary;
    uint256 public releaseTime;

    constructor(IERC20 _token, address _beneficiary, uint256 _releaseTime) {
        token = _token;
        beneficiary = _beneficiary;
        releaseTime = _releaseTime;
    }

    function release() public {
        require(block.timestamp >= releaseTime, "Not yet released");

        uint256 amount = token.balanceOf(address(this));
        token.transfer(beneficiary, amount);
    }
}
```

### Linear Vesting
```solidity
contract LinearVesting {
    IERC20 public token;
    address public beneficiary;
    uint256 public startTime;
    uint256 public duration;
    uint256 public totalAmount;
    uint256 public released;

    constructor(
        IERC20 _token,
        address _beneficiary,
        uint256 _totalAmount,
        uint256 _duration
    ) {
        token = _token;
        beneficiary = _beneficiary;
        totalAmount = _totalAmount;
        duration = _duration;
        startTime = block.timestamp;
    }

    function releasableAmount() public view returns (uint256) {
        if (block.timestamp < startTime) return 0;

        uint256 elapsed = block.timestamp - startTime;
        if (elapsed >= duration) {
            return totalAmount - released;
        }

        return (totalAmount * elapsed / duration) - released;
    }

    function release() public {
        uint256 amount = releasableAmount();
        require(amount > 0, "No tokens to release");

        released += amount;
        token.transfer(beneficiary, amount);
    }
}
```

## Post-Deployment

### Monitor Token
```javascript
// Monitor token transfers
const filter = token.filters.Transfer();

token.on(filter, (from, to, value, event) => {
  console.log(`Transfer: ${from} → ${to} (${ethers.formatEther(value)} tokens)`);
});
```

### Update on Listing Platforms
```
1. Register on CoinGecko
2. Apply for Uniswap listing
3. Create Uniswap pair with ETH
4. Apply to major exchanges
5. Add to portfolio trackers
6. Create token documentation
```

### Community Building
```
1. Create social media
2. Announce on Twitter
3. Get listed on DeFi dashboards
4. Apply to yield farming
5. Partner with other protocols
6. Create governance proposal template
```

## Common Issues and Solutions

### Liquidity Issues
```
Problem: Token won't trade on AMM
Solution:
1. Create sufficient liquidity pool
2. Pair with stable token
3. Seed initial liquidity
4. Incentivize liquidity providers
```

### Price Discovery
```
Problem: Token price fluctuates wildly
Solution:
1. Provide deep liquidity
2. Create market-making incentives
3. Communicate tokenomics clearly
4. Demonstrate utility
```

### Acceptance
```
Problem: Nobody wants to use token
Solution:
1. Clear use case
2. Value proposition
3. Community engagement
4. Real utility (not just speculation)
5. Sustainable economics
```

## Upgrades and Changes

### Adding Minting
```javascript
// After deployment, if needed
const token = MyToken.attach(TOKEN_ADDRESS);

// Check if owner
const owner = await token.owner();
console.log("Owner:", owner);

// Mint new tokens
const tx = await token.mint(recipientAddress, amount);
await tx.wait();
```

### Transferring Ownership
```javascript
const currentOwner = await token.owner();
const newOwner = "0x...";

const tx = await token.transferOwnership(newOwner);
await tx.wait();

console.log("Ownership transferred to:", newOwner);
```

## Security Considerations

- [ ] Contract audited
- [ ] No hardcoded addresses
- [ ] Access control verified
- [ ] No reentrancy issues
- [ ] Owner keys secured
- [ ] Emergency pause mechanism
- [ ] Documentation complete
- [ ] Community informed
- [ ] Regular monitoring
- [ ] Incident response plan

---

**Key Takeaways**:
- Use OpenZeppelin contracts for safety
- Test thoroughly on testnet first
- Verify contract on block explorer
- Plan token distribution carefully
- Communicate clearly with community
- Monitor after deployment
- Be prepared for upgrades if needed
