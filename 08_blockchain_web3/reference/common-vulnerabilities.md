# Common Smart Contract Vulnerabilities

Quick reference guide to the most common vulnerabilities and their mitigations.

## 1. Reentrancy

**Risk**: CRITICAL | **Frequency**: HIGH

### Description
Attacker calls back into the contract before the first invocation completes, potentially draining funds.

### Vulnerable Code
```solidity
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount);
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
    balances[msg.sender] -= amount; // ❌ TOO LATE!
}
```

### Attack
```solidity
contract Attacker {
    Vulnerable target;

    function attack() external payable {
        target.deposit{value: 1 ether}();
        target.withdraw(1 ether);
    }

    receive() external payable {
        if (address(target).balance >= 1 ether) {
            target.withdraw(1 ether); // Reenter!
        }
    }
}
```

### Mitigation
```solidity
// ✅ Solution 1: Checks-Effects-Interactions
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount; // Update state FIRST
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}

// ✅ Solution 2: ReentrancyGuard
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Safe is ReentrancyGuard {
    function withdraw(uint amount) public nonReentrant {
        require(balances[msg.sender] >= amount);
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] -= amount;
    }
}
```

---

## 2. Integer Overflow/Underflow

**Risk**: HIGH | **Frequency**: MEDIUM (Solidity <0.8)

### Description
Arithmetic operations exceed type limits, wrapping around.

### Vulnerable Code (Solidity <0.8)
```solidity
function transfer(address to, uint256 amount) public {
    balances[msg.sender] -= amount; // ❌ Can underflow
    balances[to] += amount;          // ❌ Can overflow
}
```

### Attack
```solidity
// If balance = 100
transfer(attacker, 101); // Underflows to type(uint256).max
```

### Mitigation
```solidity
// ✅ Solution 1: Use Solidity 0.8+ (built-in overflow checks)
pragma solidity 0.8.23;

function transfer(address to, uint256 amount) public {
    balances[msg.sender] -= amount; // Auto reverts on underflow
    balances[to] += amount;          // Auto reverts on overflow
}

// ✅ Solution 2: SafeMath (Solidity <0.8)
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

using SafeMath for uint256;

function transfer(address to, uint256 amount) public {
    balances[msg.sender] = balances[msg.sender].sub(amount);
    balances[to] = balances[to].add(amount);
}
```

---

## 3. Access Control

**Risk**: CRITICAL | **Frequency**: HIGH

### Description
Unauthorized users can call privileged functions.

### Vulnerable Code
```solidity
function withdraw() public {
    payable(owner).transfer(address(this).balance); // ❌ No access control
}
```

### Mitigation
```solidity
// ✅ Solution 1: Ownable
import "@openzeppelin/contracts/access/Ownable.sol";

contract Safe is Ownable {
    function withdraw() public onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}

// ✅ Solution 2: Role-Based Access Control
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Safe is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function withdraw() public onlyRole(ADMIN_ROLE) {
        payable(msg.sender).transfer(address(this).balance);
    }
}
```

---

## 4. Front-Running

**Risk**: MEDIUM | **Frequency**: HIGH (DeFi)

### Description
Attacker sees pending transaction and submits their own with higher gas to execute first.

### Vulnerable Code
```solidity
function buy(uint256 amount) public payable {
    uint256 price = getPrice(); // ❌ Price can be manipulated before this tx
    require(msg.value >= price * amount);
    // Buy tokens
}
```

### Mitigation
```solidity
// ✅ Solution 1: Slippage Protection
function buy(uint256 amount, uint256 maxPrice) public payable {
    uint256 price = getPrice();
    require(price <= maxPrice, "Price too high");
    require(msg.value >= price * amount);
    // Buy tokens
}

// ✅ Solution 2: Commit-Reveal
mapping(bytes32 => Commit) public commits;

struct Commit {
    bytes32 commitment;
    uint256 timestamp;
}

function commit(bytes32 hash) public {
    commits[msg.sender] = Commit(hash, block.timestamp);
}

function reveal(uint256 amount, bytes32 secret) public {
    require(block.timestamp > commits[msg.sender].timestamp + 1 minutes);
    require(keccak256(abi.encodePacked(amount, secret)) == commits[msg.sender].commitment);
    // Execute order
}
```

---

## 5. Oracle Manipulation

**Risk**: CRITICAL | **Frequency**: MEDIUM (DeFi)

### Description
Attacker manipulates price oracle to exploit protocol.

### Vulnerable Code
```solidity
function borrow() public {
    uint256 price = uniswapPair.price(); // ❌ Spot price easily manipulated
    uint256 collateralValue = userCollateral * price;
    // Allow borrow based on collateral value
}
```

### Attack
```solidity
// 1. Flash loan huge amount
// 2. Swap to manipulate Uniswap price
// 3. Borrow at inflated collateral value
// 4. Repay flash loan
// 5. Keep profit
```

### Mitigation
```solidity
// ✅ Solution 1: Chainlink Oracle
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

AggregatorV3Interface priceFeed;

function getPrice() public view returns (uint256) {
    (
        uint80 roundId,
        int256 price,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) = priceFeed.latestRoundData();

    require(price > 0, "Invalid price");
    require(updatedAt > block.timestamp - 3600, "Stale price");
    require(answeredInRound >= roundId, "Stale round");

    return uint256(price);
}

// ✅ Solution 2: TWAP (Time-Weighted Average Price)
function getTimeWeightedAveragePrice() public view returns (uint256) {
    uint256 timeElapsed = block.timestamp - lastUpdateTime;
    return priceAccumulator / timeElapsed;
}
```

---

## 6. Flash Loan Attacks

**Risk**: CRITICAL | **Frequency**: MEDIUM (DeFi)

### Description
Attacker borrows large amounts in single transaction to manipulate protocol state.

### Vulnerable Code
```solidity
function liquidate(address user) public {
    uint256 healthFactor = calculateHealthFactor(user);
    require(healthFactor < 1e18);
    // Liquidate user
}

function calculateHealthFactor(address user) internal view returns (uint256) {
    uint256 price = spotPrice(); // ❌ Can be manipulated via flash loan
    return (userCollateral[user] * price) / userDebt[user];
}
```

### Mitigation
```solidity
// ✅ Solution 1: TWAP Oracle
function calculateHealthFactor(address user) internal view returns (uint256) {
    uint256 price = getTWAPPrice(); // Use time-weighted price
    return (userCollateral[user] * price) / userDebt[user];
}

// ✅ Solution 2: Block-based Limits
mapping(address => uint256) public lastActionBlock;

function borrow() public {
    require(block.number > lastActionBlock[msg.sender], "One action per block");
    lastActionBlock[msg.sender] = block.number;
    // Borrow logic
}

// ✅ Solution 3: Invariant Checks
uint256 private constant K = 1e36; // Constant product

function swap() public {
    // Swap logic

    require(reserve0 * reserve1 >= K, "K invariant violated");
}
```

---

## 7. Denial of Service (DoS)

**Risk**: MEDIUM | **Frequency**: MEDIUM

### Description
Attacker prevents legitimate users from using the contract.

### Vulnerable Code
```solidity
address[] public users;

function distribute() public {
    for (uint i = 0; i < users.length; i++) {
        (bool success, ) = users[i].call{value: 1 ether}(""); // ❌ Gas griefing
        require(success);
    }
}
```

### Attack
```solidity
contract Griefer {
    receive() external payable {
        revert(); // Always revert, blocking distribution
    }
}
```

### Mitigation
```solidity
// ✅ Solution 1: Pull Over Push
mapping(address => uint256) public pendingWithdrawals;

function distribute() public {
    for (uint i = 0; i < users.length; i++) {
        pendingWithdrawals[users[i]] += 1 ether;
    }
}

function withdraw() public {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success);
}

// ✅ Solution 2: Bounded Loops
function distribute(uint256 start, uint256 end) public {
    require(end - start <= 100, "Batch too large");
    for (uint i = start; i < end; i++) {
        // Distribute
    }
}
```

---

## 8. Delegatecall to Untrusted Callee

**Risk**: CRITICAL | **Frequency**: LOW

### Description
Using delegatecall with untrusted addresses can overwrite storage.

### Vulnerable Code
```solidity
function execute(address target, bytes memory data) public {
    (bool success, ) = target.delegatecall(data); // ❌ Dangerous!
    require(success);
}
```

### Attack
```solidity
contract Attacker {
    function attack() public {
        // delegatecall executes in victim's context
        // Can overwrite owner storage slot
        assembly {
            sstore(0, caller()) // Overwrite owner
        }
    }
}
```

### Mitigation
```solidity
// ✅ Solution: Whitelist known addresses
mapping(address => bool) public trustedImplementations;

function execute(address target, bytes memory data) public {
    require(trustedImplementations[target], "Untrusted target");
    (bool success, ) = target.delegatecall(data);
    require(success);
}
```

---

## 9. Timestamp Dependence

**Risk**: LOW | **Frequency**: MEDIUM

### Description
Miners can manipulate block.timestamp within ~15 seconds.

### Vulnerable Code
```solidity
function mint() public {
    uint256 random = uint256(keccak256(abi.encodePacked(block.timestamp))); // ❌ Predictable
    if (random % 10 == 0) {
        // Mint rare NFT
    }
}
```

### Mitigation
```solidity
// ✅ Solution: Chainlink VRF for randomness
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract NFT is VRFConsumerBase {
    bytes32 internal keyHash;
    uint256 internal fee;

    function requestRandomness() public {
        requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override {
        // Use true randomness
    }
}

// ✅ For time-based logic: Accept ~15 second tolerance
function unlock() public {
    require(block.timestamp >= unlockTime, "Still locked");
    // 15-second manipulation is acceptable here
}
```

---

## 10. Unchecked External Calls

**Risk**: MEDIUM | **Frequency**: MEDIUM

### Description
Not checking return value of external calls.

### Vulnerable Code
```solidity
function transferTokens(address token, address to, uint256 amount) public {
    IERC20(token).transfer(to, amount); // ❌ Not checking return value
}
```

### Mitigation
```solidity
// ✅ Solution: SafeERC20
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

using SafeERC20 for IERC20;

function transferTokens(address token, address to, uint256 amount) public {
    IERC20(token).safeTransfer(to, amount); // Reverts on failure
}
```

---

## 11. Signature Replay

**Risk**: MEDIUM | **Frequency**: LOW

### Description
Reusing valid signatures for unauthorized actions.

### Vulnerable Code
```solidity
function executeWithSignature(bytes memory signature) public {
    bytes32 hash = keccak256(abi.encodePacked(msg.sender));
    address signer = recoverSigner(hash, signature);
    require(signer == owner);
    // Execute action ❌ Can be replayed
}
```

### Mitigation
```solidity
// ✅ Solution: Nonces
mapping(address => uint256) public nonces;

function executeWithSignature(uint256 nonce, bytes memory signature) public {
    require(nonce == nonces[msg.sender], "Invalid nonce");

    bytes32 hash = keccak256(abi.encodePacked(msg.sender, nonce));
    address signer = recoverSigner(hash, signature);
    require(signer == owner);

    nonces[msg.sender]++;
    // Execute action
}
```

---

## 12. Selfdestruct

**Risk**: MEDIUM | **Frequency**: LOW

### Description
Selfdestruct can forcibly send ETH, breaking contract assumptions.

### Vulnerable Code
```solidity
function claimPrize() public {
    require(address(this).balance == 10 ether, "Not enough deposits"); // ❌ Bypassable
    // Award prize
}
```

### Attack
```solidity
contract Attacker {
    function attack() public payable {
        selfdestruct(payable(target)); // Force send ETH
    }
}
```

### Mitigation
```solidity
// ✅ Solution: Track deposits internally
uint256 public totalDeposits;

function deposit() public payable {
    totalDeposits += msg.value;
}

function claimPrize() public {
    require(totalDeposits == 10 ether);
    // Award prize
}
```

---

## Severity Ratings

| Severity | Impact | Likelihood |
|----------|---------|------------|
| CRITICAL | Loss of funds, protocol insolvency | High |
| HIGH | Partial loss, manipulation | Medium |
| MEDIUM | Griefing, DoS | Medium |
| LOW | Edge cases, theoretical | Low |

## Prevention Checklist

- [ ] Use Solidity 0.8+ for overflow protection
- [ ] Follow Checks-Effects-Interactions pattern
- [ ] Use ReentrancyGuard on payable functions
- [ ] Implement proper access control
- [ ] Use Chainlink oracles for prices
- [ ] Protect against flash loan attacks
- [ ] Use SafeERC20 for token transfers
- [ ] Avoid delegatecall to untrusted addresses
- [ ] Use Chainlink VRF for randomness
- [ ] Implement nonces for signature replay protection
- [ ] Pull over push for payments
- [ ] Bound loops and gas usage

---

**Remember**: This is not exhaustive. Always get professional audits for production code.
