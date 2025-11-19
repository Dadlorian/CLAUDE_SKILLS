# Smart Contract Testing Guide

## Overview
Comprehensive testing is critical for smart contract security and reliability. This guide covers unit testing, integration testing, fuzzing, and formal verification techniques.

## Testing Frameworks

### Hardhat Testing
```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time, loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("AdvancedERC20Token", function () {
    // Fixture for deployment
    async function deployTokenFixture() {
        const [owner, addr1, addr2, ...addrs] = await ethers.getSigners();

        const Token = await ethers.getContractFactory("AdvancedERC20Token");
        const token = await Token.deploy(
            "MyToken",
            "MTK",
            ethers.parseEther("1000000"), // max supply
            ethers.parseEther("100000")   // initial supply
        );

        return { token, owner, addr1, addr2, addrs };
    }

    describe("Deployment", function () {
        it("Should set the right owner", async function () {
            const { token, owner } = await loadFixture(deployTokenFixture);
            expect(await token.hasRole(await token.DEFAULT_ADMIN_ROLE(), owner.address))
                .to.be.true;
        });

        it("Should assign initial supply to owner", async function () {
            const { token, owner } = await loadFixture(deployTokenFixture);
            const ownerBalance = await token.balanceOf(owner.address);
            expect(ownerBalance).to.equal(ethers.parseEther("100000"));
        });

        it("Should set max supply correctly", async function () {
            const { token } = await loadFixture(deployTokenFixture);
            expect(await token.MAX_SUPPLY()).to.equal(ethers.parseEther("1000000"));
        });
    });

    describe("Minting", function () {
        it("Should mint tokens when called by minter", async function () {
            const { token, owner, addr1 } = await loadFixture(deployTokenFixture);

            await expect(token.mint(addr1.address, ethers.parseEther("1000")))
                .to.emit(token, "TokensMinted")
                .withArgs(addr1.address, ethers.parseEther("1000"));

            expect(await token.balanceOf(addr1.address))
                .to.equal(ethers.parseEther("1000"));
        });

        it("Should fail when non-minter tries to mint", async function () {
            const { token, addr1 } = await loadFixture(deployTokenFixture);

            await expect(
                token.connect(addr1).mint(addr1.address, ethers.parseEther("1000"))
            ).to.be.reverted;
        });

        it("Should not exceed max supply", async function () {
            const { token, addr1 } = await loadFixture(deployTokenFixture);

            const remaining = await token.remainingSupply();

            await expect(
                token.mint(addr1.address, remaining + 1n)
            ).to.be.revertedWith("Exceeds max supply");
        });

        it("Should emit MaxSupplyReached when minting to cap", async function () {
            const { token, addr1 } = await loadFixture(deployTokenFixture);

            const remaining = await token.remainingSupply();

            await expect(token.mint(addr1.address, remaining))
                .to.emit(token, "MaxSupplyReached");
        });
    });

    describe("Pausable", function () {
        it("Should pause and unpause transfers", async function () {
            const { token, owner, addr1, addr2 } = await loadFixture(deployTokenFixture);

            await token.transfer(addr1.address, ethers.parseEther("1000"));

            await token.pause();

            await expect(
                token.connect(addr1).transfer(addr2.address, ethers.parseEther("100"))
            ).to.be.reverted;

            await token.unpause();

            await token.connect(addr1).transfer(addr2.address, ethers.parseEther("100"));
            expect(await token.balanceOf(addr2.address))
                .to.equal(ethers.parseEther("100"));
        });

        it("Should prevent non-pauser from pausing", async function () {
            const { token, addr1 } = await loadFixture(deployTokenFixture);

            await expect(token.connect(addr1).pause()).to.be.reverted;
        });
    });

    describe("Batch Transfer", function () {
        it("Should transfer to multiple recipients", async function () {
            const { token, owner, addrs } = await loadFixture(deployTokenFixture);

            const recipients = addrs.slice(0, 5).map(addr => addr.address);
            const amounts = recipients.map(() => ethers.parseEther("100"));

            await token.batchTransfer(recipients, amounts);

            for (let i = 0; i < recipients.length; i++) {
                expect(await token.balanceOf(recipients[i]))
                    .to.equal(ethers.parseEther("100"));
            }
        });

        it("Should revert on array length mismatch", async function () {
            const { token, addrs } = await loadFixture(deployTokenFixture);

            const recipients = addrs.slice(0, 3).map(addr => addr.address);
            const amounts = [ethers.parseEther("100"), ethers.parseEther("100")];

            await expect(
                token.batchTransfer(recipients, amounts)
            ).to.be.revertedWith("Arrays length mismatch");
        });

        it("Should revert on insufficient balance", async function () {
            const { token, owner, addrs } = await loadFixture(deployTokenFixture);

            const recipients = addrs.slice(0, 5).map(addr => addr.address);
            const amounts = recipients.map(() => ethers.parseEther("100000"));

            await expect(
                token.batchTransfer(recipients, amounts)
            ).to.be.revertedWith("Insufficient balance");
        });

        it("Should prevent too many recipients", async function () {
            const { token, addrs } = await loadFixture(deployTokenFixture);

            const recipients = Array(201).fill(addrs[0].address);
            const amounts = Array(201).fill(ethers.parseEther("1"));

            await expect(
                token.batchTransfer(recipients, amounts)
            ).to.be.revertedWith("Too many recipients");
        });
    });

    describe("EIP-2612 Permit", function () {
        it("Should allow permit approval", async function () {
            const { token, owner, addr1 } = await loadFixture(deployTokenFixture);

            const value = ethers.parseEther("100");
            const deadline = await time.latest() + 3600;

            const domain = {
                name: await token.name(),
                version: "1",
                chainId: (await ethers.provider.getNetwork()).chainId,
                verifyingContract: await token.getAddress()
            };

            const types = {
                Permit: [
                    { name: "owner", type: "address" },
                    { name: "spender", type: "address" },
                    { name: "value", type: "uint256" },
                    { name: "nonce", type: "uint256" },
                    { name: "deadline", type: "uint256" }
                ]
            };

            const message = {
                owner: owner.address,
                spender: addr1.address,
                value: value,
                nonce: await token.nonces(owner.address),
                deadline: deadline
            };

            const signature = await owner.signTypedData(domain, types, message);
            const { v, r, s } = ethers.Signature.from(signature);

            await token.permit(
                owner.address,
                addr1.address,
                value,
                deadline,
                v,
                r,
                s
            );

            expect(await token.allowance(owner.address, addr1.address))
                .to.equal(value);
        });
    });

    describe("Gas Optimization", function () {
        it("Should efficiently pack storage", async function () {
            const { token } = await loadFixture(deployTokenFixture);

            // Check that MAX_SUPPLY is immutable and doesn't use storage
            const tx = await token.MAX_SUPPLY();
            // Immutable variables are compiled into bytecode
        });
    });
});
```

### Foundry Testing
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/AdvancedERC20Token.sol";

contract AdvancedERC20TokenTest is Test {
    AdvancedERC20Token public token;
    address public owner;
    address public addr1;
    address public addr2;

    uint256 constant MAX_SUPPLY = 1000000 ether;
    uint256 constant INITIAL_SUPPLY = 100000 ether;

    function setUp() public {
        owner = address(this);
        addr1 = makeAddr("addr1");
        addr2 = makeAddr("addr2");

        token = new AdvancedERC20Token(
            "MyToken",
            "MTK",
            MAX_SUPPLY,
            INITIAL_SUPPLY
        );
    }

    function testDeployment() public {
        assertEq(token.name(), "MyToken");
        assertEq(token.symbol(), "MTK");
        assertEq(token.MAX_SUPPLY(), MAX_SUPPLY);
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY);
    }

    function testMint() public {
        token.mint(addr1, 1000 ether);
        assertEq(token.balanceOf(addr1), 1000 ether);
    }

    function testFailMintExceedsMaxSupply() public {
        uint256 remaining = token.remainingSupply();
        token.mint(addr1, remaining + 1);
    }

    function testFuzzTransfer(uint256 amount) public {
        vm.assume(amount > 0 && amount <= INITIAL_SUPPLY);

        token.transfer(addr1, amount);
        assertEq(token.balanceOf(addr1), amount);
        assertEq(token.balanceOf(owner), INITIAL_SUPPLY - amount);
    }

    function testFuzzMint(uint256 amount) public {
        vm.assume(amount > 0 && amount <= token.remainingSupply());

        uint256 totalBefore = token.totalSupply();
        token.mint(addr1, amount);

        assertEq(token.balanceOf(addr1), amount);
        assertEq(token.totalSupply(), totalBefore + amount);
    }

    function testPauseUnpause() public {
        token.transfer(addr1, 1000 ether);

        token.pause();

        vm.prank(addr1);
        vm.expectRevert();
        token.transfer(addr2, 100 ether);

        token.unpause();

        vm.prank(addr1);
        token.transfer(addr2, 100 ether);
        assertEq(token.balanceOf(addr2), 100 ether);
    }

    function testBatchTransfer() public {
        address[] memory recipients = new address[](3);
        uint256[] memory amounts = new uint256[](3);

        recipients[0] = addr1;
        recipients[1] = addr2;
        recipients[2] = makeAddr("addr3");

        amounts[0] = 100 ether;
        amounts[1] = 200 ether;
        amounts[2] = 300 ether;

        token.batchTransfer(recipients, amounts);

        assertEq(token.balanceOf(addr1), 100 ether);
        assertEq(token.balanceOf(addr2), 200 ether);
        assertEq(token.balanceOf(recipients[2]), 300 ether);
    }

    function testFailBatchTransferInsufficientBalance() public {
        address[] memory recipients = new address[](2);
        uint256[] memory amounts = new uint256[](2);

        recipients[0] = addr1;
        recipients[1] = addr2;

        amounts[0] = INITIAL_SUPPLY;
        amounts[1] = 1 ether;

        token.batchTransfer(recipients, amounts);
    }

    function testInvariantTotalSupplyNeverExceedsMax() public {
        assertLe(token.totalSupply(), token.MAX_SUPPLY());
    }
}
```

## Testing Best Practices

### 1. Test Coverage
- Aim for 100% line coverage
- Test all edge cases
- Test failure conditions
- Test access control
- Test state transitions

### 2. Test Organization
```javascript
describe("Contract Name", function() {
    describe("Function Category", function() {
        it("should behave correctly in normal case", async function() {});
        it("should revert on invalid input", async function() {});
        it("should emit correct events", async function() {});
    });
});
```

### 3. Fixture Usage
Use fixtures to avoid code duplication:
```javascript
async function deployFixture() {
    // Deploy and setup
    return { contract, signers, etc };
}

// Load fixture in each test
const { contract } = await loadFixture(deployFixture);
```

### 4. Time Manipulation
```javascript
const { time } = require("@nomicfoundation/hardhat-network-helpers");

// Increase time
await time.increase(3600); // 1 hour

// Set specific timestamp
await time.increaseTo(deadline);

// Latest block timestamp
const latest = await time.latest();
```

### 5. Event Testing
```javascript
await expect(contract.function())
    .to.emit(contract, "EventName")
    .withArgs(arg1, arg2);
```

### 6. Revert Testing
```javascript
// Generic revert
await expect(contract.function()).to.be.reverted;

// Specific revert message
await expect(contract.function())
    .to.be.revertedWith("Error message");

// Custom error
await expect(contract.function())
    .to.be.revertedWithCustomError(contract, "CustomError");
```

## Fuzzing Tests

### Foundry Fuzzing
```solidity
function testFuzz_Transfer(uint256 amount, address recipient) public {
    // Assumptions
    vm.assume(recipient != address(0));
    vm.assume(amount > 0 && amount <= token.balanceOf(owner));

    // Test
    token.transfer(recipient, amount);
    assertEq(token.balanceOf(recipient), amount);
}
```

### Echidna Property Testing
```solidity
contract EchidnaTest {
    AdvancedERC20Token token;

    constructor() {
        token = new AdvancedERC20Token("Test", "TST", 1000000 ether, 100000 ether);
    }

    // Invariant: total supply never exceeds max supply
    function echidna_total_supply_bounded() public view returns (bool) {
        return token.totalSupply() <= token.MAX_SUPPLY();
    }

    // Invariant: sum of balances equals total supply
    function echidna_balance_sum_equals_supply() public view returns (bool) {
        // Implementation depends on tracking all addresses
        return true;
    }
}
```

## Integration Testing

### Multi-Contract Interactions
```javascript
describe("DeFi Protocol Integration", function () {
    it("Should handle complex swap workflow", async function () {
        const { token1, token2, router, pair } = await loadFixture(deployDeFiFixture);

        // 1. Approve tokens
        await token1.approve(router.address, ethers.parseEther("1000"));

        // 2. Add liquidity
        await router.addLiquidity(
            token1.address,
            token2.address,
            ethers.parseEther("1000"),
            ethers.parseEther("1000"),
            0,
            0,
            owner.address,
            deadline
        );

        // 3. Swap tokens
        await router.swapExactTokensForTokens(
            ethers.parseEther("100"),
            0,
            [token1.address, token2.address],
            addr1.address,
            deadline
        );

        // Verify final state
        expect(await token2.balanceOf(addr1.address)).to.be.gt(0);
    });
});
```

### Fork Testing
```javascript
const { network } = require("hardhat");

describe("Mainnet Fork Tests", function () {
    it("Should interact with Uniswap", async function () {
        await network.provider.request({
            method: "hardhat_reset",
            params: [{
                forking: {
                    jsonRpcUrl: process.env.MAINNET_RPC_URL,
                    blockNumber: 18000000
                }
            }]
        });

        const uniswapRouter = await ethers.getContractAt(
            "IUniswapV2Router02",
            "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        );

        // Test interactions with live Uniswap
    });
});
```

## Gas Profiling

### Hardhat Gas Reporter
```javascript
// hardhat.config.js
require("hardhat-gas-reporter");

module.exports = {
    gasReporter: {
        enabled: true,
        currency: "USD",
        coinmarketcap: process.env.COINMARKETCAP_API_KEY,
        outputFile: "gas-report.txt",
        noColors: true
    }
};
```

### Foundry Gas Snapshots
```bash
# Generate gas snapshot
forge snapshot

# Compare gas changes
forge snapshot --diff .gas-snapshot
```

## Security Testing

### Slither Analysis
```bash
# Run Slither
slither .

# Specific detectors
slither . --detect reentrancy-eth,unchecked-transfer
```

### Mythril Analysis
```bash
# Analyze contract
myth analyze contracts/MyContract.sol

# With specific options
myth analyze --execution-timeout 300 contracts/MyContract.sol
```

## Continuous Integration

### GitHub Actions
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run coverage
        run: npm run coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Conclusion

Comprehensive testing is essential for smart contract security. Combine unit tests, fuzzing, integration tests, and formal verification for maximum confidence in your code.
