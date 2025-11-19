# Smart Contract Security Guide

## Security Fundamentals

### Defense in Depth
```
Multiple layers of protection:
1. Code review
2. Automated testing
3. Static analysis
4. Dynamic testing
5. Formal verification
6. Audit
7. Monitoring
8. Insurance
```

### Threat Model
```
Identify:
1. Assets: What's at risk?
2. Attackers: Who might attack?
3. Attacks: What could they do?
4. Mitigations: How to prevent?
```

## Common Vulnerabilities

### 1. Reentrancy

#### Vulnerability
```solidity
// Vulnerable
function withdraw(uint256 amount) public {
  uint256 balance = balances[msg.sender];
  require(balance >= amount);

  // VULNERABLE: External call before state update
  (bool success, ) = msg.sender.call{value: amount}("");
  require(success);

  balances[msg.sender] -= amount;  // Too late!
}

// Attack:
// 1. Attacker withdraws 1 ETH
// 2. Fallback function calls withdraw again
// 3. Still has balance from first call
// 4. Withdrawal succeeds again
// 5. Repeat: Empty contract
```

#### Fix: Checks-Effects-Interactions
```solidity
// Safe
function withdraw(uint256 amount) public {
  uint256 balance = balances[msg.sender];
  require(balance >= amount);

  // 1. Checks (done above)

  // 2. Effects (state change FIRST)
  balances[msg.sender] -= amount;

  // 3. Interactions (external call LAST)
  (bool success, ) = msg.sender.call{value: amount}("");
  require(success);
}
```

#### Prevention Tools
```solidity
// Use ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

function withdraw() public nonReentrant {
  // Protected
}

// Or use Checks-Effects-Interactions pattern
// Always: State changes before external calls
```

### 2. Integer Overflow/Underflow

#### Vulnerability (Pre Solidity 0.8)
```solidity
// Vulnerable in Solidity < 0.8
uint8 public counter = 255;
function increment() public {
  counter++;  // Wraps to 0! (255 + 1 = 0)
}

uint256 public balance = 100;
function withdraw(uint256 amount) public {
  balance -= amount;  // Can underflow to huge number!
}
```

#### Fix: Solidity 0.8+
```solidity
// Solidity 0.8+ has automatic checks
pragma solidity ^0.8.0;

uint8 public counter = 255;
function increment() public {
  counter++;  // Reverts: overflow detected
}
```

#### Legacy: SafeMath
```solidity
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

uint256 public balance = 100;
function withdraw(uint256 amount) public {
  balance = balance.sub(amount);  // Safe subtraction
}
```

### 3. Unchecked External Calls

#### Vulnerability
```solidity
// Vulnerable
function transfer(address recipient, uint256 amount) public {
  // No return value check
  (bool success, ) = recipient.call{value: amount}("");
  // Assume success!
}

// Attacker: Send to contract that rejects, but your code continues
```

#### Fix: Check Return Values
```solidity
// Safe
function transfer(address recipient, uint256 amount) public {
  (bool success, ) = recipient.call{value: amount}("");
  require(success, "Transfer failed");
}

// Or use safe transfer library
SafeTransferLib.safeTransferETH(recipient, amount);
```

### 4. Timestamp Dependence

#### Vulnerability
```solidity
// Vulnerable
function lottery() public {
  if (block.timestamp % 2 == 0) {
    // You won!
    payWinner();
  }
}

// Miner can adjust timestamp within ~15 seconds
// Miner can choose: win or lose
```

#### Fix: Use Block Numbers
```solidity
// Better
uint256 private lastAction;

function delayedAction() public {
  require(block.number >= lastAction + 256, "Too soon");
  // ...
}

// Or use external randomness (oracle)
```

### 5. Authorization Errors

#### Vulnerability
```solidity
// Vulnerable
function transferFrom(address from, address to, uint256 amount) public {
  balances[from] -= amount;
  balances[to] += amount;
  // No check who's calling!
}

// Any user can steal from anyone
```

#### Fix: Check Caller
```solidity
// Safe
function transferFrom(address from, address to, uint256 amount) public {
  require(msg.sender == from || allowance[from][msg.sender] >= amount);
  require(balances[from] >= amount);

  balances[from] -= amount;
  balances[to] += amount;
  if (msg.sender != from) {
    allowance[from][msg.sender] -= amount;
  }
}
```

#### Best Practice: Access Control
```solidity
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyContract is Ownable {
  function adminFunction() public onlyOwner {
    // Only owner can call
  }
}

// Or RBAC
import "@openzeppelin/contracts/access/AccessControl.sol";

contract MyContract is AccessControl {
  bytes32 public constant ADMIN_ROLE = keccak256("ADMIN");

  modifier onlyAdmin() {
    require(hasRole(ADMIN_ROLE, msg.sender));
    _;
  }

  function adminFunction() public onlyAdmin {
    // Only ADMIN role
  }
}
```

### 6. Flash Loan Attacks

#### Vulnerability
```solidity
// Vulnerable
function liquidate(address borrower) public {
  uint256 price = getPriceFromAMM();  // Can be manipulated!
  uint256 debt = getDebt(borrower);

  if (price < threshold) {
    liquidate(borrower);
  }
}

// Attacker:
// 1. Flash borrow 1000 ETH
// 2. Dump on AMM pool
// 3. Price crashes
// 4. Liquidate innocent user
// 5. Repay flash loan + profit
```

#### Fix: Use Robust Oracles
```solidity
// Safe: Time-weighted average price
uint256 price = oracle.getTwap();  // 30-min average

// Or use multiple oracles
uint256 price1 = oracle1.getPrice();
uint256 price2 = oracle2.getPrice();
uint256 price3 = oracle3.getPrice();

// Take median or weighted average
```

### 7. Front-Running

#### Vulnerability
```
Transaction pool (mempool) visible:
1. Attacker sees your pending transaction
2. Attacker sends similar transaction
3. Attacker's tx included first
4. Price moves against you
5. Your tx executed at worse price
```

#### Fix: Private Transactions
```solidity
// Options:
1. Flashbots Protect: Private pools
2. Slippage limits: Reject bad outcomes
3. MEV burn: Mechanism to offset MEV
4. Batch auctions: Hide transaction order
```

```javascript
// Set slippage protection
const slippageTolerance = 0.01;  // 1%
const minimumOutput = expectedOutput * (1 - slippageTolerance);
await contract.swap({
  inputAmount,
  minimumOutput,  // Revert if output worse
});
```

## Testing Strategies

### Unit Testing
```javascript
describe("Contract", function () {
  it("Should handle edge cases", async function () {
    // Test boundary conditions
    await contract.function(0);      // Minimum
    await contract.function(MAX);    // Maximum
    await contract.function(1);      // Edge
  });

  it("Should revert on invalid input", async function () {
    await expect(
      contract.badFunction(invalidInput)
    ).to.be.revertedWith("Expected error");
  });
});
```

### Fuzzing
```javascript
// Use Echidna for property-based testing
// Property: After any transfer, sum of balances unchanged
// Echidna: Try random transfers, check property holds
```

### Static Analysis
```bash
# Slither: Finds common vulnerabilities
slither contract.sol

# Mythril: Bytecode analysis
mythril analyze contract.sol

# Semgrep: Pattern matching
semgrep --config=p/security-audit contract.sol
```

## Security Audit Checklist

### Code Review
- [ ] Access control properly implemented
- [ ] No reentrancy vulnerabilities
- [ ] Return values checked
- [ ] State changes before external calls
- [ ] No timestamp/block number manipulation
- [ ] Proper error handling
- [ ] Events logged for important changes

### Testing
- [ ] Unit tests cover all functions
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] Fuzzing performed
- [ ] Integration tests pass
- [ ] Gas costs reasonable
- [ ] No unexpected behavior

### Deployment
- [ ] Deployed on testnet first
- [ ] Contract verified on block explorer
- [ ] Admin keys secured
- [ ] Monitoring in place
- [ ] Emergency procedures documented
- [ ] Insurance considered
- [ ] Upgrade plan clear

## Security Best Practices

### General Principles
```
1. Assume data is malicious
2. Validate all inputs
3. Fail safely (deny by default)
4. Principle of least privilege
5. Defense in depth
6. Code simplicity
7. Extensive testing
```

### Code Standards
```solidity
// ✓ Good: Clear intent
function transfer(address to, uint256 amount) public returns (bool) {
  require(balances[msg.sender] >= amount);
  require(to != address(0));

  balances[msg.sender] -= amount;
  balances[to] += amount;

  emit Transfer(msg.sender, to, amount);
  return true;
}

// ✗ Bad: Unclear, potential issues
function xfer(address to, uint256 amt) public {
  balances[msg.sender] -= amt;
  balances[to] += amt;
}
```

### Event Logging
```solidity
// Always log important state changes
event Transfer(address indexed from, address indexed to, uint256 amount);
event Withdrawal(address indexed user, uint256 amount);
event ParameterChange(string indexed parameter, uint256 newValue);

function transfer(address to, uint256 amount) public {
  balances[msg.sender] -= amount;
  balances[to] += amount;
  emit Transfer(msg.sender, to, amount);  // Don't forget!
}
```

## Tools and Resources

### Static Analysis Tools
- **Slither**: Find vulnerabilities automatically
- **Mythril**: Bytecode analysis engine
- **Semgrep**: Pattern matching tool
- **Certora**: Formal verification

### Audit Services
- **OpenZeppelin**: Trusted audit firm
- **Consensys Diligence**: Auditing and security
- **Trail of Bits**: Security research
- **Spearbit**: Decentralized audit network

### Learning Resources
- [Smart Contract Audit Checklist](https://blog.openzeppelin.com/smart-contract-audit-checklist)
- [OWASP Smart Contract Top 10](https://owasp.org/www-project-smart-contract-top-10/)
- [ConsenSys Best Practices](https://consensys.github.io/smart-contract-best-practices/)

## Common Mistakes to Avoid

1. **Trusting user input**: Always validate
2. **Complex logic**: Keep it simple
3. **Skipping tests**: Test everything
4. **No error handling**: Handle all cases
5. **Hardcoded values**: Use parameters
6. **Lack of monitoring**: Watch deployed contracts
7. **Upgrading carelessly**: Thoroughly test upgrades
8. **Ignoring warnings**: Pay attention to linters

## Emergency Procedures

### Circuit Breaker Pattern
```solidity
bool public emergencyStop = false;

modifier stopInEmergency() {
  require(!emergencyStop, "Emergency: paused");
  _;
}

function triggerEmergency() public onlyOwner {
  emergencyStop = true;
}

function criticalFunction() public stopInEmergency {
  // Can be stopped in emergency
}
```

### Time Locks
```solidity
uint256 constant TIMELOCK = 2 days;
mapping(bytes32 => uint256) pendingChanges;

function initiateParameterChange(uint256 newValue) public onlyOwner {
  bytes32 key = keccak256("parameter");
  pendingChanges[key] = block.timestamp + TIMELOCK;
}

function executeParameterChange(uint256 newValue) public onlyOwner {
  bytes32 key = keccak256("parameter");
  require(block.timestamp >= pendingChanges[key]);
  // Execute change
}
```

---

**Key Takeaways**:
- Reentrancy: Use checks-effects-interactions pattern
- Integer overflow: Use Solidity 0.8+ or SafeMath
- Authorization: Implement access control
- Oracles: Use robust, time-weighted prices
- Testing: Comprehensive coverage essential
- Audits: Professional security review before mainnet
- Monitoring: Watch deployed contracts
