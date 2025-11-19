# Smart Contract Testing Guide

## Test Structure with Hardhat

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MyContract", function () {
  let contract;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    const MyContract = await ethers.getContractFactory("MyContract");
    contract = await MyContract.deploy();
  });

  describe("Initialization", function () {
    it("Should set owner correctly", async function () {
      expect(await contract.owner()).to.equal(owner.address);
    });

    it("Should initialize with correct values", async function () {
      expect(await contract.totalSupply()).to.equal(0);
    });
  });

  describe("Functions", function () {
    it("Should execute function successfully", async function () {
      const result = await contract.someFunction(param);
      expect(result).to.equal(expectedValue);
    });

    it("Should emit event correctly", async function () {
      await expect(contract.functionThatEmits(param))
        .to.emit(contract, "EventName")
        .withArgs(param);
    });

    it("Should revert with correct error", async function () {
      await expect(contract.invalidFunction())
        .to.be.revertedWith("Error message");
    });

    it("Should revert with custom error (Solidity 0.8.4+)", async function () {
      await expect(contract.invalidFunction())
        .to.be.revertedWithCustomError(contract, "CustomError");
    });
  });

  describe("Edge Cases", function () {
    it("Should handle zero input", async function () {
      const result = await contract.function(0);
      expect(result).to.equal(0);
    });

    it("Should handle max uint256", async function () {
      const maxUint = ethers.MaxUint256;
      const result = await contract.function(maxUint);
      expect(result).to.be.ok;
    });

    it("Should handle multiple calls", async function () {
      await contract.function(10);
      await contract.function(20);
      const state = await contract.getState();
      expect(state).to.equal(30);
    });
  });

  describe("Access Control", function () {
    it("Should only allow owner", async function () {
      await expect(
        contract.connect(user1).restrictedFunction()
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should allow owner", async function () {
      await expect(contract.connect(owner).restrictedFunction())
        .not.to.be.reverted;
    });
  });

  describe("State Changes", function () {
    it("Should update state correctly", async function () {
      const before = await contract.balance(user1.address);
      await contract.transfer(user1.address, 100);
      const after = await contract.balance(user1.address);

      expect(after).to.equal(before.add(100));
    });

    it("Should preserve invariants", async function () {
      await contract.transfer(user1.address, 100);
      await contract.transfer(user2.address, 50);

      const total = (await contract.balance(user1.address))
        .add(await contract.balance(user2.address));

      expect(total).to.equal(150);
    });
  });

  describe("Gas Efficiency", function () {
    it("Should use reasonable gas", async function () {
      const tx = await contract.expensiveFunction();
      const receipt = await tx.wait();

      expect(receipt.gasUsed).to.be.lt(ethers.parseEther("0.01"));
    });
  });
});
```

## Fixtures for Reusable Setup

```javascript
async function deployContractFixture() {
  const [owner, addr1, addr2] = await ethers.getSigners();

  const MyContract = await ethers.getContractFactory("MyContract");
  const contract = await MyContract.deploy();

  // Setup initial state
  await contract.initialize();
  await contract.addWhitelist(addr1.address);

  return { contract, owner, addr1, addr2 };
}

describe("Using Fixtures", function () {
  it("Should use fixture", async function () {
    const { contract, owner } = await loadFixture(deployContractFixture);

    const isWhitelisted = await contract.isWhitelisted(owner.address);
    expect(isWhitelisted).to.be.true;
  });
});
```

## Mocking and Stubbing

```javascript
const { ethers } = require("hardhat");

describe("Mocking Contracts", function () {
  it("Should mock external contract", async function () {
    // Create mock
    const MockToken = await ethers.getContractFactory("MockERC20");
    const mockToken = await MockToken.deploy("Mock", "MCK");

    // Setup behavior
    await mockToken.setBalance(user.address, ethers.parseEther("1000"));

    // Use in main contract
    const contract = await MyContract.deploy(mockToken.address);

    // Verify interaction
    const balance = await contract.getBalance(user.address);
    expect(balance).to.equal(ethers.parseEther("1000"));
  });
});
```

## Snapshot Testing

```javascript
describe("Snapshots", function () {
  it("Should match snapshot", async function () {
    const state = await contract.getFullState();

    expect(state).to.deep.equal({
      owner: expectedOwner,
      balance: expectedBalance,
      // ...
    });
  });

  it("Should restore from snapshot", async function () {
    const snapshot = await ethers.provider.send("evm_snapshot", []);

    // Make changes
    await contract.someFunction();

    // Restore
    await ethers.provider.send("evm_revert", [snapshot]);

    // State should be as before
    const state = await contract.getState();
    expect(state).to.equal(originalState);
  });
});
```

## Fuzzing with Echidna

```solidity
// Fuzzing test contract
contract TestMyContract {
    MyContract myContract;

    constructor() {
        myContract = new MyContract();
    }

    // Invariant: balance never negative
    function invariant_balance_never_negative() public {
        for (uint i = 0; i < users.length; i++) {
            assert(myContract.balanceOf(users[i]) >= 0);
        }
    }

    // Property: transfer maintains sum
    function property_transfer_maintains_sum(address from, address to, uint256 amount) public {
        uint256 balanceBefore = myContract.balanceOf(from) + myContract.balanceOf(to);

        myContract.transfer(from, to, amount);

        uint256 balanceAfter = myContract.balanceOf(from) + myContract.balanceOf(to);
        assert(balanceBefore == balanceAfter);
    }
}
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
      - uses: actions/checkout@v2

      - uses: actions/setup-node@v2
        with:
          node-version: "18"

      - run: npm install

      - run: npm run test

      - run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Coverage

```bash
# Generate coverage report
npx hardhat coverage

# Output shows which lines are tested
# Target: 90%+ coverage for financial contracts
```

## Best Practices

- [ ] Test all public functions
- [ ] Test all error conditions
- [ ] Test edge cases (0, max values)
- [ ] Test state transitions
- [ ] Test access controls
- [ ] Test events
- [ ] Test gas efficiency
- [ ] Use fixtures for setup
- [ ] Test with multiple signers
- [ ] Verify invariants

---

**Key Takeaways**:
- Comprehensive testing essential for financial contracts
- Test edge cases thoroughly
- Verify all error conditions revert correctly
- Monitor gas usage
- Use fixtures for reusable setup
- Target 95%+ code coverage
