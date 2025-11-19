# Smart Contract Security Auditing

## Overview
Conduct comprehensive security audits of smart contracts, identify vulnerabilities, and implement security best practices. Master common attack vectors, auditing methodologies, and security tools.

## Common Vulnerabilities

### 1. Reentrancy Attacks
```solidity
// VULNERABLE CODE
contract Vulnerable {
    mapping(address => uint256) public balances;

    function withdraw() external {
        uint256 balance = balances[msg.sender];
        // WRONG: External call before state update
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success);
        balances[msg.sender] = 0; // Too late!
    }
}

// SECURE CODE
contract Secure {
    mapping(address => uint256) public balances;

    function withdraw() external nonReentrant {
        uint256 balance = balances[msg.sender];
        // RIGHT: Update state first (Checks-Effects-Interactions)
        balances[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success);
    }
}
```

### 2. Integer Overflow/Underflow
```solidity
// VULNERABLE CODE (Solidity < 0.8.0)
contract Vulnerable {
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b; // Can overflow
    }
}

// SECURE CODE
contract Secure {
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "Overflow");
        return c;
    }
}

// Or use Solidity >= 0.8.0 (built-in checks)
// Or use SafeMath library
```

### 3. Access Control Issues
```solidity
// VULNERABLE CODE
contract Vulnerable {
    address public owner;

    function withdraw() external {
        // Missing access control!
        payable(msg.sender).transfer(address(this).balance);
    }
}

// SECURE CODE
contract Secure {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
```

### 4. Front-Running
```solidity
// VULNERABLE CODE
contract Vulnerable {
    mapping(address => uint256) public bids;

    function bid() external payable {
        require(msg.value > bids[address(0)], "Bid too low");
        bids[msg.sender] = msg.value;
    }
}

// MITIGATION: Commit-Reveal Scheme
contract Secure {
    mapping(address => bytes32) public commits;
    mapping(address => uint256) public bids;

    function commitBid(bytes32 hash) external {
        commits[msg.sender] = hash;
    }

    function revealBid(uint256 amount, bytes32 salt) external payable {
        require(
            commits[msg.sender] == keccak256(abi.encodePacked(amount, salt)),
            "Invalid reveal"
        );
        require(msg.value == amount, "Wrong amount");

        bids[msg.sender] = amount;
        delete commits[msg.sender];
    }
}
```

### 5. Denial of Service
```solidity
// VULNERABLE CODE
contract Vulnerable {
    address[] public users;

    function distribute() external {
        // Unbounded loop - can run out of gas
        for (uint256 i = 0; i < users.length; i++) {
            payable(users[i]).transfer(1 ether);
        }
    }
}

// SECURE CODE: Pull over Push
contract Secure {
    mapping(address => uint256) public balances;

    function addReward(address user, uint256 amount) external {
        balances[user] += amount;
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}
```

### 6. Unchecked Return Values
```solidity
// VULNERABLE CODE
contract Vulnerable {
    function transferTokens(address token, address to, uint256 amount) external {
        // Return value not checked!
        IERC20(token).transfer(to, amount);
    }
}

// SECURE CODE
contract Secure {
    function transferTokens(address token, address to, uint256 amount) external {
        require(IERC20(token).transfer(to, amount), "Transfer failed");
        // Or use SafeERC20
    }
}
```

### 7. Delegate Call Injection
```solidity
// VULNERABLE CODE
contract Vulnerable {
    address public implementation;

    function execute(bytes memory data) external {
        // User can call any function in implementation
        (bool success, ) = implementation.delegatecall(data);
        require(success);
    }
}

// SECURE CODE
contract Secure {
    address public immutable implementation;
    mapping(bytes4 => bool) public allowedFunctions;

    function execute(bytes memory data) external {
        bytes4 sig = bytes4(data);
        require(allowedFunctions[sig], "Function not allowed");

        (bool success, ) = implementation.delegatecall(data);
        require(success);
    }
}
```

### 8. Oracle Manipulation
```solidity
// VULNERABLE CODE
contract Vulnerable {
    IUniswapV2Pair public pair;

    function getPrice() public view returns (uint256) {
        (uint256 reserve0, uint256 reserve1, ) = pair.getReserves();
        // WRONG: Spot price can be manipulated via flash loans
        return (reserve1 * 1e18) / reserve0;
    }
}

// SECURE CODE: Use TWAP
contract Secure {
    IUniswapV2Pair public pair;
    uint256 public price0CumulativeLast;
    uint256 public blockTimestampLast;
    uint256 public priceAverage;

    function update() external {
        (
            uint256 price0Cumulative,
            ,
            uint256 blockTimestamp
        ) = currentCumulativePrices(address(pair));

        uint256 timeElapsed = blockTimestamp - blockTimestampLast;
        require(timeElapsed >= 3600, "Too soon");

        priceAverage = (price0Cumulative - price0CumulativeLast) / timeElapsed;
        price0CumulativeLast = price0Cumulative;
        blockTimestampLast = blockTimestamp;
    }
}
```

## Auditing Methodology

### 1. Manual Review Process
```
1. Understand Project Scope
   - Read documentation
   - Understand business logic
   - Identify critical functions
   - Map contract interactions

2. Static Analysis
   - Review code line-by-line
   - Check for common patterns
   - Verify access controls
   - Review state changes

3. Dynamic Analysis
   - Test edge cases
   - Fuzzing tests
   - Integration tests
   - Mainnet fork tests

4. Report Writing
   - Document findings
   - Severity classification
   - Reproduction steps
   - Mitigation recommendations
```

### 2. Audit Checklist
```markdown
## Access Control
- [ ] Owner privileges properly restricted
- [ ] Role-based access implemented correctly
- [ ] No privilege escalation vectors
- [ ] Admin functions time-locked

## Reentrancy
- [ ] External calls follow CEI pattern
- [ ] ReentrancyGuard used where needed
- [ ] No cross-function reentrancy
- [ ] No read-only reentrancy

## Integer Safety
- [ ] Using Solidity >= 0.8.0 or SafeMath
- [ ] No unchecked blocks without validation
- [ ] Type casting checked
- [ ] Division by zero prevented

## Input Validation
- [ ] All external inputs validated
- [ ] Array lengths checked
- [ ] Address != address(0) verified
- [ ] Value ranges enforced

## Oracle Security
- [ ] Price feeds validated
- [ ] TWAP used for DEX prices
- [ ] Multiple oracle sources
- [ ] Stale data checks

## Gas Optimization
- [ ] No unbounded loops
- [ ] Storage packed efficiently
- [ ] Events used appropriately
- [ ] Batch operations possible

## Upgradeability
- [ ] Storage layout preserved
- [ ] Initialization secured
- [ ] Upgrade authorization proper
- [ ] Timelock implemented

## Token Handling
- [ ] ERC20 return values checked
- [ ] SafeERC20 used or equivalent
- [ ] Approval race condition handled
- [ ] Token decimals considered

## Testing
- [ ] >95% code coverage
- [ ] Edge cases tested
- [ ] Fuzzing implemented
- [ ] Integration tests comprehensive
```

## Security Tools

### 1. Slither (Static Analysis)
```bash
# Install Slither
pip3 install slither-analyzer

# Run analysis
slither .

# Specific detectors
slither . --detect reentrancy-eth,unprotected-upgrade

# Generate report
slither . --json slither-report.json
```

### 2. Mythril (Symbolic Execution)
```bash
# Install Mythril
pip3 install mythril

# Analyze contract
myth analyze contracts/MyContract.sol

# Specify strategy
myth analyze contracts/MyContract.sol --strategy bfs --max-depth 10
```

### 3. Echidna (Fuzzing)
```solidity
// echidna_test.sol
contract EchidnaTest is MyContract {
    // Invariant: balance never exceeds max supply
    function echidna_balance_bounded() public view returns (bool) {
        return totalSupply() <= MAX_SUPPLY;
    }

    // Property: transfer preserves total supply
    function echidna_transfer_preserves_supply() public returns (bool) {
        uint256 supplyBefore = totalSupply();
        // Perform transfer
        uint256 supplyAfter = totalSupply();
        return supplyBefore == supplyAfter;
    }
}
```

```bash
# Run Echidna
echidna-test contracts/echidna_test.sol --contract EchidnaTest
```

### 4. Foundry Fuzzing
```solidity
contract MyContractTest is Test {
    function testFuzz_Transfer(address to, uint256 amount) public {
        vm.assume(to != address(0));
        vm.assume(amount > 0 && amount <= token.balanceOf(address(this)));

        uint256 balanceBefore = token.balanceOf(address(this));
        token.transfer(to, amount);

        assertEq(token.balanceOf(to), amount);
        assertEq(token.balanceOf(address(this)), balanceBefore - amount);
    }
}
```

### 5. Manticore (Symbolic Execution)
```python
from manticore.ethereum import ManticoreEVM

m = ManticoreEVM()

# Create account with balance
user = m.create_account(balance=1000)

# Deploy contract
contract = m.solidity_create_contract('MyContract.sol', owner=user)

# Execute function
contract.vulnerableFunction(symbolic_value)

# Analyze results
for state in m.ready_states:
    print(f"State: {state}")
```

## Formal Verification

### 1. Certora Specs
```
methods {
    balanceOf(address) returns (uint256) envfree
    totalSupply() returns (uint256) envfree
}

// Invariant: sum of balances equals total supply
invariant sumBalancesEqualsTotalSupply()
    forall address a. balanceOf(a) <= totalSupply()

// Rule: transfer preserves total supply
rule transferPreservesTotalSupply(address from, address to, uint256 amount) {
    uint256 supplyBefore = totalSupply();

    env e;
    transfer(e, to, amount);

    uint256 supplyAfter = totalSupply();

    assert supplyBefore == supplyAfter;
}
```

### 2. K Framework
```k
rule transfer-success:
    <k> transfer(TO, AMOUNT) => . ... </k>
    <caller> FROM </caller>
    <balances>
        ... FROM |-> (BAL_FROM => BAL_FROM - AMOUNT) ...
        ... TO |-> (BAL_TO => BAL_TO + AMOUNT) ...
    </balances>
    requires BAL_FROM >= AMOUNT
```

## Incident Response

### 1. Emergency Pause
```solidity
contract EmergencyPausable is Pausable {
    address public guardian;

    event EmergencyPause(address indexed guardian);
    event EmergencyUnpause(address indexed guardian);

    modifier onlyGuardian() {
        require(msg.sender == guardian, "Not guardian");
        _;
    }

    function emergencyPause() external onlyGuardian {
        _pause();
        emit EmergencyPause(msg.sender);
    }

    function emergencyUnpause() external onlyGuardian {
        _unpause();
        emit EmergencyUnpause(msg.sender);
    }
}
```

### 2. Circuit Breakers
```solidity
contract CircuitBreaker {
    uint256 public constant MAX_DAILY_WITHDRAWAL = 100 ether;
    uint256 public dailyWithdrawn;
    uint256 public lastResetDay;

    function withdraw(uint256 amount) external {
        uint256 currentDay = block.timestamp / 1 days;

        if (currentDay > lastResetDay) {
            dailyWithdrawn = 0;
            lastResetDay = currentDay;
        }

        require(
            dailyWithdrawn + amount <= MAX_DAILY_WITHDRAWAL,
            "Daily limit exceeded"
        );

        dailyWithdrawn += amount;
        // Execute withdrawal
    }
}
```

### 3. Upgrade Mechanisms
```solidity
contract Upgradeable {
    address public implementation;
    address public admin;
    uint256 public upgradeTimeLock = 2 days;

    mapping(address => uint256) public pendingImplementations;

    function proposeUpgrade(address newImplementation) external {
        require(msg.sender == admin, "Not admin");
        pendingImplementations[newImplementation] = block.timestamp;
    }

    function executeUpgrade(address newImplementation) external {
        require(msg.sender == admin, "Not admin");
        require(
            pendingImplementations[newImplementation] > 0,
            "Not proposed"
        );
        require(
            block.timestamp >= pendingImplementations[newImplementation] + upgradeTimeLock,
            "Timelock not passed"
        );

        implementation = newImplementation;
        delete pendingImplementations[newImplementation];
    }
}
```

## Best Practices

### 1. Development Practices
- Use latest Solidity version
- Follow Checks-Effects-Interactions pattern
- Minimize external calls
- Use ReentrancyGuard
- Implement proper access control
- Emit events for state changes
- Document code thoroughly

### 2. Testing Practices
- Achieve >95% code coverage
- Test edge cases
- Implement fuzzing tests
- Use mainnet forks
- Test upgrade paths
- Conduct integration tests

### 3. Deployment Practices
- Use multi-sig for ownership
- Implement timelock for critical functions
- Deploy to testnet first
- Conduct external audits
- Set up monitoring
- Prepare incident response plan

## Audit Report Template

```markdown
# Security Audit Report

## Project: [Name]
## Date: [Date]
## Auditor: [Name]

### Executive Summary
- Total Issues: X
- Critical: X
- High: X
- Medium: X
- Low: X
- Informational: X

### Scope
- Contracts audited: [List]
- Commit hash: [Hash]
- Lines of code: X

### Findings

#### [CRITICAL] [Finding Title]
**Severity:** Critical
**Status:** Open/Resolved
**File:** contracts/File.sol
**Lines:** XX-XX

**Description:**
[Detailed description]

**Impact:**
[Potential impact]

**Recommendation:**
[How to fix]

**Code:**
```solidity
// Vulnerable code
```

**Fixed Code:**
```solidity
// Secure code
```

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

### Conclusion
[Overall assessment]
```

## Resources

### Learning
- Ethernaut
- Damn Vulnerable DeFi
- Security Pitfalls & Best Practices
- SWC Registry
- Consensys Best Practices

### Tools
- Slither
- Mythril
- Echidna
- Manticore
- Certora

### Communities
- Secureum
- OpenZeppelin Forum
- Immunefi
- Code4rena
- Sherlock Protocol

## Conclusion

Smart contract security is paramount in blockchain development. Comprehensive auditing, proper testing, and following best practices are essential for building secure protocols. Stay updated with the latest vulnerabilities and security patterns to protect user funds and protocol integrity.
