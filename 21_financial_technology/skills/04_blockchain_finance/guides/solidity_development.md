# Solidity Development Guide

## Environment Setup

### Prerequisites
```bash
Node.js: v16+ (npm/yarn)
Git: For version control
Code Editor: VSCode recommended
```

### Installation

#### 1. Hardhat Setup
```bash
mkdir my-blockchain-project
cd my-blockchain-project
npm init -y
npm install --save-dev hardhat
npx hardhat

# Select: Create a basic sample project
# Select: Use default settings
```

#### 2. Project Structure
```
my-project/
├── contracts/          # Solidity files
├── test/              # Test files
├── scripts/           # Deployment scripts
├── hardhat.config.js  # Configuration
└── package.json       # Dependencies
```

#### 3. Install Dependencies
```bash
npm install --save-dev @openzeppelin/contracts
npm install --save-dev @nomicfoundation/hardhat-toolbox
npm install --save-dev dotenv
```

## First Smart Contract

### Create ERC20 Token
```bash
touch contracts/MyToken.sol
```

### Write Contract
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor() ERC20("My Token", "MTK") {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }

    function burn(uint256 amount) public {
        _burn(msg.sender, amount);
    }
}
```

## Compilation

### Compile Contract
```bash
npx hardhat compile

# Output:
# Compiling 1 file with 0.8.9
# Compilation successful
```

### Verify Compilation
```bash
ls artifacts/contracts/
# Should see: MyToken.sol/MyToken.json
```

### Contract Artifacts
```json
{
  "abi": [...],          // Application Binary Interface
  "bytecode": "0x...",   // Compiled binary
  "deployedBytecode": "0x..."
}
```

## Testing

### Create Test File
```bash
touch test/MyToken.test.js
```

### Write Tests
```javascript
const { expect } = require("chai");

describe("MyToken", function () {
  let myToken;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const MyToken = await ethers.getContractFactory("MyToken");
    myToken = await MyToken.deploy();
  });

  it("Should deploy with initial supply", async function () {
    const balance = await myToken.balanceOf(owner.address);
    const expectedSupply = ethers.parseEther("1000000");
    expect(balance).to.equal(expectedSupply);
  });

  it("Should transfer tokens", async function () {
    const transferAmount = ethers.parseEther("100");
    await myToken.transfer(addr1.address, transferAmount);

    const balance = await myToken.balanceOf(addr1.address);
    expect(balance).to.equal(transferAmount);
  });

  it("Owner can mint tokens", async function () {
    const mintAmount = ethers.parseEther("1000");
    await myToken.mint(addr1.address, mintAmount);

    const balance = await myToken.balanceOf(addr1.address);
    expect(balance).to.equal(mintAmount);
  });

  it("Non-owner cannot mint", async function () {
    await expect(
      myToken.connect(addr1).mint(addr1.address, ethers.parseEther("100"))
    ).to.be.revertedWith("Ownable: caller is not the owner");
  });
});
```

### Run Tests
```bash
npx hardhat test

# Output:
# MyToken
#   ✓ Should deploy with initial supply
#   ✓ Should transfer tokens
#   ✓ Owner can mint tokens
#   ✓ Non-owner cannot mint
#
# 4 passing
```

## Deployment

### Create Deployment Script
```bash
touch scripts/deploy.js
```

### Write Deployment Script
```javascript
const hre = require("hardhat");

async function main() {
  console.log("Deploying MyToken...");

  const MyToken = await hre.ethers.getContractFactory("MyToken");
  const myToken = await MyToken.deploy();
  await myToken.deployed();

  console.log("MyToken deployed to:", myToken.address);

  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    address: myToken.address,
    network: hre.network.name,
    blockNumber: await hre.ethers.provider.getBlockNumber(),
  };
  fs.writeFileSync(
    "deployment.json",
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

### Deploy to Local Network
```bash
# Terminal 1: Start local node
npx hardhat node

# Terminal 2: Run deployment
npx hardhat run scripts/deploy.js --network localhost
```

## Development Best Practices

### Code Organization
```solidity
// SPDX-License-Identifier identifier
pragma solidity version;

// Imports
import "./Interface.sol";

// Contract definition
contract MyContract {
  // Type declarations

  // State variables

  // Events

  // Modifiers

  // Constructor

  // External functions

  // Public functions

  // Internal functions

  // Private functions

  // Fallback functions
}
```

### Naming Conventions
```solidity
contract MyContract { }      // PascalCase
function myFunction() { }    // camelCase
uint256 private myVariable;  // camelCase, private prefix
bytes32 constant MY_CONSTANT = ...;  // UPPER_CASE
event MyEvent(uint256 indexed id);   // PascalCase
```

### Gas Optimization
```solidity
// Bad: Multiple SSTORE operations
function transfer(address[] calldata recipients, uint256[] calldata amounts) public {
  for (uint256 i = 0; i < recipients.length; i++) {
    balances[recipients[i]] += amounts[i];  // SSTORE each iteration
  }
}

// Good: Cache in memory
function transfer(address[] calldata recipients, uint256[] calldata amounts) public {
  uint256 length = recipients.length;
  for (uint256 i = 0; i < length; i++) {
    balances[recipients[i]] += amounts[i];
  }
}
```

### Error Handling
```solidity
// Before Solidity 0.8.4
require(amount > 0, "Amount must be positive");
require(balance >= amount, "Insufficient balance");

// After Solidity 0.8.4 (gas efficient)
error InvalidAmount();
error InsufficientBalance();

if (amount == 0) revert InvalidAmount();
if (balance < amount) revert InsufficientBalance();
```

## Interacting with Deployed Contracts

### Via Script
```javascript
const { ethers } = require("hardhat");

async function interact() {
  // Get contract
  const MyToken = await ethers.getContractFactory("MyToken");
  const myToken = MyToken.attach("0x...");  // Deployed address

  // Call functions
  const balance = await myToken.balanceOf(ethers.provider.defaultAccount);
  console.log("Balance:", balance);

  // Send transactions
  const tx = await myToken.transfer(recipientAddress, amount);
  await tx.wait();  // Wait for confirmation
}
```

### Via Hardhat Console
```bash
npx hardhat console --network localhost

# In console:
> const MyToken = await ethers.getContractFactory("MyToken");
> const myToken = MyToken.attach("0x...");
> const balance = await myToken.balanceOf("0x...");
> console.log(balance.toString());
```

## Debugging

### Log Statements
```solidity
import "hardhat/console.sol";

contract MyContract {
  function test() public {
    console.log("Value:", 123);
    console.log("Address:", msg.sender);
  }
}
```

### Hardhat Debugging
```bash
# Run test with debug output
HARDHAT_LOG=true npx hardhat test
```

### Transaction Trace
```bash
# Get detailed transaction info
npx hardhat console --network localhost

> await ethers.provider.send("hardhat_setLoggingEnabled", [true]);
> // Run transaction
```

## Upgrade Patterns

### Proxy Pattern
```solidity
// Implementation contract
contract MyTokenV1 {
  uint256 public value;

  function setValue(uint256 _value) public {
    value = _value;
  }
}

// Proxy contract
contract Proxy {
  address public implementation;

  fallback() external {
    _delegatecall(implementation);
  }

  function upgrade(address newImpl) public {
    implementation = newImpl;
  }
}
```

### Using OpenZeppelin Upgrades
```bash
npm install --save-dev @openzeppelin/hardhat-upgrades
npm install @openzeppelin/contracts-upgradeable
```

```javascript
const { upgrades } = require("hardhat");

// Deploy upgradeable
const MyToken = await ethers.getContractFactory("MyTokenV1");
const myToken = await upgrades.deployProxy(MyToken);

// Upgrade
const MyTokenV2 = await ethers.getContractFactory("MyTokenV2");
await upgrades.upgradeProxy(myToken.address, MyTokenV2);
```

## Security Checklist

- [ ] Code reviewed for vulnerabilities
- [ ] Tests cover all major functions
- [ ] No hardcoded addresses
- [ ] Access control properly implemented
- [ ] No reentrancy issues
- [ ] No overflow/underflow (Solidity 0.8+)
- [ ] Proper error handling
- [ ] Event logging for important changes
- [ ] Gas optimization reviewed
- [ ] Deployed on testnet first

## Common Patterns

### Ownable
```solidity
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyContract is Ownable {
  function onlyOwnerFunction() public onlyOwner {
    // Only owner can call
  }
}
```

### Pausable
```solidity
import "@openzeppelin/contracts/security/Pausable.sol";

contract MyContract is Pausable {
  function pause() public onlyOwner {
    _pause();
  }

  function unpause() public onlyOwner {
    _unpause();
  }

  function criticalFunction() public whenNotPaused {
    // Can be paused
  }
}
```

### ReentrancyGuard
```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract MyContract is ReentrancyGuard {
  function withdraw() public nonReentrant {
    // Protected from reentrancy
  }
}
```

## Resources

- [Solidity Documentation](https://docs.soliditylang.org)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Ethereum Development Documentation](https://ethereum.org/en/developers/docs)

---

**Next Steps**:
1. Deploy on testnet (Sepolia, Goerli)
2. Get testnet ETH from faucet
3. Verify contract on block explorer
4. Integrate with frontend
5. Move to mainnet
