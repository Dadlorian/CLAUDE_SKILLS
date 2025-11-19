# Smart Contract Testing Strategies

Comprehensive guide to testing blockchain applications with Foundry and Hardhat.

## Testing Philosophy

**Goal**: Achieve >95% coverage while testing real-world scenarios, edge cases, and attack vectors.

**Test Pyramid**:
1. **Unit Tests** (70%): Test individual functions in isolation
2. **Integration Tests** (20%): Test contract interactions
3. **Fork Tests** (5%): Test against real mainnet state
4. **Invariant/Fuzz Tests** (5%): Test properties and random inputs

## Foundry Testing Framework

### Basic Test Structure

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.23;

import "forge-std/Test.sol";
import "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;

    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    address owner = address(this);

    function setUp() public {
        myContract = new MyContract();

        // Fund test accounts
        vm.deal(alice, 100 ether);
        vm.deal(bob, 100 ether);
    }

    function test_BasicFunctionality() public {
        // Test implementation
    }
}
```

### Foundry Cheatcodes

```solidity
// Time manipulation
vm.warp(block.timestamp + 1 days);  // Set block.timestamp
vm.roll(block.number + 100);         // Set block.number

// Pranking (impersonation)
vm.prank(alice);                      // Next call from alice
myContract.deposit();

vm.startPrank(alice);                 // All calls from alice
myContract.deposit();
myContract.withdraw();
vm.stopPrank();

// Expectations
vm.expectRevert();                                    // Expect next call to revert
vm.expectRevert("Error message");                    // Specific error
vm.expectRevert(MyContract.CustomError.selector);    // Custom error

vm.expectEmit(true, true, false, true);              // Check event
emit Transfer(alice, bob, 100);
myContract.transfer(bob, 100);

// Balance manipulation
vm.deal(alice, 100 ether);            // Set ETH balance
deal(address(token), alice, 1000e18); // Set ERC20 balance

// Storage manipulation
vm.store(address(myContract), bytes32(uint256(0)), bytes32(uint256(123)));
bytes32 value = vm.load(address(myContract), bytes32(uint256(0)));

// Mock calls
vm.mockCall(
    address(oracle),
    abi.encodeWithSelector(oracle.getPrice.selector),
    abi.encode(100e18)
);
```

## Unit Testing Patterns

### 1. Test Happy Path

```solidity
function test_Deposit() public {
    uint256 amount = 1 ether;

    vm.prank(alice);
    myContract.deposit{value: amount}();

    assertEq(myContract.balances(alice), amount);
    assertEq(address(myContract).balance, amount);
}
```

### 2. Test Reverts

```solidity
function test_RevertWhen_DepositZero() public {
    vm.prank(alice);
    vm.expectRevert(MyContract.ZeroAmount.selector);
    myContract.deposit{value: 0}();
}

function test_RevertWhen_Unauthorized() public {
    vm.prank(alice);
    vm.expectRevert();
    myContract.adminFunction();
}
```

### 3. Test Events

```solidity
function test_EmitsDepositEvent() public {
    uint256 amount = 1 ether;

    vm.expectEmit(true, false, false, true);
    emit Deposit(alice, amount);

    vm.prank(alice);
    myContract.deposit{value: amount}();
}
```

### 4. Test State Changes

```solidity
function test_TransferUpdatesBalances() public {
    deal(address(token), alice, 1000e18);

    uint256 aliceBalanceBefore = token.balanceOf(alice);
    uint256 bobBalanceBefore = token.balanceOf(bob);

    vm.prank(alice);
    token.transfer(bob, 100e18);

    assertEq(token.balanceOf(alice), aliceBalanceBefore - 100e18);
    assertEq(token.balanceOf(bob), bobBalanceBefore + 100e18);
}
```

## Fuzz Testing

### Basic Fuzzing

```solidity
function testFuzz_Deposit(uint96 amount) public {
    vm.assume(amount > 0 && amount < 100 ether);

    vm.deal(alice, amount);
    vm.prank(alice);
    myContract.deposit{value: amount}();

    assertEq(myContract.balances(alice), amount);
}

function testFuzz_Transfer(address to, uint256 amount) public {
    vm.assume(to != address(0));
    vm.assume(amount > 0 && amount <= 1000e18);

    deal(address(token), alice, amount);

    vm.prank(alice);
    token.transfer(to, amount);

    assertEq(token.balanceOf(to), amount);
}
```

### Structured Fuzzing

```solidity
struct FuzzInput {
    address user;
    uint256 amount;
    uint256 timestamp;
}

function testFuzz_ComplexScenario(FuzzInput memory input) public {
    vm.assume(input.user != address(0));
    vm.assume(input.amount > 0 && input.amount < 1000e18);
    vm.assume(input.timestamp > block.timestamp);

    vm.deal(input.user, input.amount);
    vm.warp(input.timestamp);

    vm.prank(input.user);
    myContract.deposit{value: input.amount}();

    assertGe(myContract.balances(input.user), input.amount);
}
```

## Invariant Testing

### Property-Based Testing

```solidity
contract InvariantTest is Test {
    MyContract public myContract;
    Handler public handler;

    function setUp() public {
        myContract = new MyContract();
        handler = new Handler(myContract);

        // Target handler for invariant tests
        targetContract(address(handler));
    }

    // Invariant: Total balance should equal sum of user balances
    function invariant_TotalBalanceEqualsSum() public {
        assertEq(
            address(myContract).balance,
            handler.ghost_totalDeposited() - handler.ghost_totalWithdrawn()
        );
    }

    // Invariant: No user can have negative balance
    function invariant_NoNegativeBalances() public {
        address[] memory users = handler.getUsers();
        for (uint i = 0; i < users.length; i++) {
            assertGe(myContract.balances(users[i]), 0);
        }
    }
}

// Handler contract for invariant tests
contract Handler is Test {
    MyContract public myContract;

    uint256 public ghost_totalDeposited;
    uint256 public ghost_totalWithdrawn;
    address[] public users;

    constructor(MyContract _myContract) {
        myContract = _myContract;
    }

    function deposit(uint256 amount) public {
        amount = bound(amount, 1, 100 ether);
        vm.deal(msg.sender, amount);

        myContract.deposit{value: amount}();

        ghost_totalDeposited += amount;
        users.push(msg.sender);
    }

    function withdraw(uint256 amount) public {
        amount = bound(amount, 1, myContract.balances(msg.sender));

        myContract.withdraw(amount);

        ghost_totalWithdrawn += amount;
    }

    function getUsers() external view returns (address[] memory) {
        return users;
    }
}
```

## Fork Testing

### Test Against Mainnet State

```solidity
contract ForkTest is Test {
    uint256 mainnetFork;

    address constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant UNISWAP_ROUTER = 0xE592427A0AEce92De3Edee1F18E0157C05861564;

    function setUp() public {
        mainnetFork = vm.createFork(vm.envString("MAINNET_RPC_URL"));
        vm.selectFork(mainnetFork);

        // Now we have mainnet state at current block
    }

    function test_SwapOnUniswap() public {
        // Get a whale address from mainnet
        address whale = 0x...; // Known USDC holder

        uint256 balanceBefore = IERC20(USDC).balanceOf(whale);

        // Impersonate whale
        vm.startPrank(whale);

        IERC20(USDC).approve(UNISWAP_ROUTER, 1000e6);

        // Execute swap on real Uniswap
        ISwapRouter(UNISWAP_ROUTER).exactInputSingle(
            ISwapRouter.ExactInputSingleParams({
                tokenIn: USDC,
                tokenOut: WETH,
                fee: 3000,
                recipient: whale,
                deadline: block.timestamp,
                amountIn: 1000e6,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            })
        );

        vm.stopPrank();

        assertLt(IERC20(USDC).balanceOf(whale), balanceBefore);
    }

    function test_FlashLoanAttack() public {
        // Deploy attacker contract
        Attacker attacker = new Attacker();

        // Execute attack against real protocol
        vm.expectRevert(); // Should revert if protected
        attacker.attack();
    }
}
```

### Multi-Fork Testing

```solidity
function test_CrossChain() public {
    uint256 mainnetFork = vm.createFork(vm.envString("MAINNET_RPC_URL"));
    uint256 polygonFork = vm.createFork(vm.envString("POLYGON_RPC_URL"));

    // Test on Ethereum
    vm.selectFork(mainnetFork);
    uint256 ethPrice = oracle.getPrice();

    // Test on Polygon
    vm.selectFork(polygonFork);
    uint256 polyPrice = oracle.getPrice();

    // Compare prices across chains
    assertApproxEqRel(ethPrice, polyPrice, 0.01e18); // Within 1%
}
```

## Integration Testing

### Test Contract Interactions

```solidity
contract IntegrationTest is Test {
    Token public token;
    Staking public staking;
    Rewards public rewards;

    function setUp() public {
        token = new Token();
        rewards = new Rewards(address(token));
        staking = new Staking(address(token), address(rewards));

        // Setup initial state
        token.mint(alice, 1000e18);
        rewards.setStakingContract(address(staking));
    }

    function test_StakeAndEarnRewards() public {
        // Alice stakes tokens
        vm.startPrank(alice);
        token.approve(address(staking), 100e18);
        staking.stake(100e18);
        vm.stopPrank();

        // Time passes
        vm.warp(block.timestamp + 30 days);

        // Alice claims rewards
        vm.prank(alice);
        uint256 reward = staking.claimRewards();

        assertGt(reward, 0);
        assertEq(token.balanceOf(alice), 900e18 + reward);
    }
}
```

## Attack Scenario Testing

### Reentrancy Attack Test

```solidity
contract ReentrancyAttacker {
    Vulnerable public target;
    uint256 public attackCount;

    constructor(address _target) {
        target = Vulnerable(_target);
    }

    function attack() external payable {
        target.deposit{value: 1 ether}();
        target.withdraw(1 ether);
    }

    receive() external payable {
        if (attackCount < 5) {
            attackCount++;
            target.withdraw(1 ether);
        }
    }
}

contract ReentrancyTest is Test {
    Vulnerable public vulnerable;
    ReentrancyAttacker public attacker;

    function setUp() public {
        vulnerable = new Vulnerable();
        attacker = new ReentrancyAttacker(address(vulnerable));
    }

    function test_ReentrancyAttack() public {
        vm.deal(address(attacker), 1 ether);
        vm.deal(address(vulnerable), 10 ether);

        vm.expectRevert(); // Should revert if protected
        attacker.attack();
    }
}
```

### Flash Loan Attack Test

```solidity
function test_FlashLoanAttack() public {
    // Setup DEX with liquidity
    dex.addLiquidity{value: 100 ether}(100_000e18);

    // Deploy attacker
    FlashLoanAttacker attacker = new FlashLoanAttacker(address(dex));

    // Attempt price manipulation via flash loan
    vm.expectRevert("Flash loan protection");
    attacker.attack();
}
```

## Gas Testing

```solidity
function testGas_Deposit() public {
    uint256 gasBefore = gasleft();

    vm.prank(alice);
    myContract.deposit{value: 1 ether}();

    uint256 gasUsed = gasBefore - gasleft();
    console.log("Gas used:", gasUsed);

    // Assert gas usage is within acceptable range
    assertLt(gasUsed, 50000);
}
```

## Coverage Analysis

```bash
# Foundry coverage
forge coverage

# Detailed coverage report
forge coverage --report lcov
genhtml lcov.info -o coverage

# Coverage with specific tests
forge coverage --match-test test_Deposit
```

## Testing Checklist

Unit Tests:
- [ ] Happy path for all functions
- [ ] All revert conditions
- [ ] Event emissions
- [ ] State changes
- [ ] Access control
- [ ] Edge cases (zero values, max values)
- [ ] Boundary conditions

Fuzz Tests:
- [ ] Input validation
- [ ] Arithmetic operations
- [ ] State transitions
- [ ] Complex scenarios

Invariant Tests:
- [ ] Protocol invariants hold
- [ ] Total supply consistency
- [ ] Balance accounting
- [ ] No negative values

Integration Tests:
- [ ] Multi-contract interactions
- [ ] External protocol integrations
- [ ] Complex workflows

Fork Tests:
- [ ] Real protocol integrations
- [ ] Attack scenarios
- [ ] Mainnet state interactions

Attack Scenarios:
- [ ] Reentrancy attacks
- [ ] Flash loan attacks
- [ ] Oracle manipulation
- [ ] Front-running
- [ ] Integer overflow/underflow
- [ ] Access control bypass

Gas Tests:
- [ ] Gas usage within expected range
- [ ] Gas optimizations verified

---

## Hardhat Testing (TypeScript)

```typescript
import { expect } from "chai";
import { ethers } from "hardhat";
import { loadFixture } from "@nomicfoundation/hardhat-network-helpers";

describe("MyContract", function () {
  async function deployFixture() {
    const [owner, alice, bob] = await ethers.getSigners();
    const MyContract = await ethers.getContractFactory("MyContract");
    const myContract = await MyContract.deploy();
    return { myContract, owner, alice, bob };
  }

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { myContract, owner } = await loadFixture(deployFixture);
      expect(await myContract.owner()).to.equal(owner.address);
    });
  });

  describe("Deposits", function () {
    it("Should accept deposits", async function () {
      const { myContract, alice } = await loadFixture(deployFixture);

      await expect(
        myContract.connect(alice).deposit({ value: ethers.utils.parseEther("1") })
      ).to.emit(myContract, "Deposit")
        .withArgs(alice.address, ethers.utils.parseEther("1"));

      expect(await myContract.balances(alice.address))
        .to.equal(ethers.utils.parseEther("1"));
    });

    it("Should revert on zero deposit", async function () {
      const { myContract, alice } = await loadFixture(deployFixture);

      await expect(
        myContract.connect(alice).deposit({ value: 0 })
      ).to.be.revertedWith("Zero amount");
    });
  });
});
```

## Continuous Integration

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: foundry-rs/foundry-toolchain@v1

      - name: Run tests
        run: forge test -vvv

      - name: Check coverage
        run: |
          forge coverage --report lcov
          lcov --list lcov.info

      - name: Gas snapshot
        run: forge snapshot --check
```

**Remember**: Comprehensive testing is your best defense against bugs and exploits. Test early, test often, test thoroughly.
